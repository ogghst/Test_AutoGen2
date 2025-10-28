import asyncio
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from autogen_core import SingleThreadedAgentRuntime, TopicId, MessageContext, TypeSubscription
import json
from config.logging_config import setup_logging, get_logger
from base.utils import configure_oltp_tracing
from base.model_client import create_model_client
from agents.factory import AgentFactory
from tools.tools import USER_TOPIC_TYPE, TRIAGE_AGENT_TOPIC_TYPE
from base.messaging import UserLogin, UserTask, AgentResponse
from config.settings import get_config_manager
from models.data_models import Project
from knowledge.knowledge_service import KnowledgeService
from autogen_core.models import UserMessage, ChatCompletionClient
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
from session import UserSessionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_client, logger, user_session_manager
    # Load configuration - get_config_manager handles all fallback cases
    config_manager = get_config_manager("../config/config.json")

    # Setup logging with configuration
    setup_logging(
        log_level=config_manager.logging.log_level,
        console_logging=config_manager.logging.console_logging,
        max_bytes=config_manager.logging.max_bytes,
        backup_count=config_manager.logging.backup_count
    )

    # Get logger after setup
    logger = get_logger(__name__)
    logger.info("Starting handoffs pattern system")

    # Configure tracing based on configuration
    if config_manager.runtime.enable_tracing:
        tracing_endpoint = config_manager.runtime.tracing_endpoint
        tracer_provider = configure_oltp_tracing(endpoint=tracing_endpoint)
    else:
        tracer_provider = configure_oltp_tracing()

    # Create the model client with configuration
    logger.info(f"LLM Provider: {config_manager.llm_provider.value}")
    model_client = create_model_client(config_manager=config_manager)

    # Create the user session manager
    user_session_manager = UserSessionManager(model_client, tracer_provider)

    yield
    
    # Shutdown logic
    logger.info("Shutting down handoffs pattern system")
    
    # Close all active sessions gracefully
    if user_session_manager:
        try:
            # Get all session IDs to close
            session_ids = list(user_session_manager.sessions.keys())
            logger.info(f"Closing {len(session_ids)} active sessions")
            
            # Close each session
            for session_id in session_ids:
                try:
                    await user_session_manager.close_session(session_id)
                except Exception as e:
                    logger.error(f"Error closing session {session_id} during shutdown: {e}")
            
            logger.info("All sessions closed")
        except Exception as e:
            logger.error(f"Error during session cleanup: {e}")
    
    # Close the model client
    if model_client:
        try:
            await model_client.close()
            logger.info("Model client closed")
        except Exception as e:
            logger.error(f"Error closing model client: {e}")
    
    logger.info("Shutdown complete")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/session")
async def create_session():
    session_id = await user_session_manager.create_session()
    logger.info(f"Created new session: {session_id}")
    return {"session_id": session_id}


@app.get("/api/session/{session_id}/project")
async def get_project(session_id: str):
    session = await user_session_manager.get_session(session_id)
    if not session:
        return JSONResponse(status_code=404, content={"message": "Session not found"})

    project_json = session.knowledge_service.get_full_project_context(session.project_id)
    return JSONResponse(content=json.loads(project_json))


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Client connected: {session_id}")

    session = await user_session_manager.get_session(session_id)
    if not session:
        logger.error(f"Session not found: {session_id}")
        await websocket.close(code=1011, reason="Session not found")
        return

    logger.info(f"Runtime for session {session_id}: {session.runtime}")

    # Task to send agent responses to the client
    async def send_responses():
        try:
            while True:
                response = await session.response_queue.get()
                if response is None:
                    break
                if response.context and len(response.context) > 0:
                    import json
                    agent_reply = json.dumps(response.context[-1].model_dump())
                    logger.info(f"Sending agent reply to client: {agent_reply}")
                    await websocket.send_text(agent_reply)
        except Exception as e:
            logger.error(f"Error in send_responses for session {session_id}: {e}")
        finally:
            logger.info(f"Send responses task completed for session {session_id}")

    send_task = asyncio.create_task(send_responses())

    try:
        while True:
            data = await websocket.receive_text()
            await session.input_queue.put(data)
            logger.info(f"Received message from {session_id}: {data}")

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Error in websocket endpoint for session {session_id}: {e}")
    finally:
        logger.info(f"Closing connection for {session_id}")
        
        # Cancel the send task first
        if not send_task.done():
            send_task.cancel()
            try:
                await send_task
            except asyncio.CancelledError:
                pass
        
        # Signal the send task to stop
        try:
            await session.response_queue.put(None)
        except Exception as e:
            logger.warning(f"Could not put None in response queue for session {session_id}: {e}")
        
        # Close the session properly
        try:
            await user_session_manager.close_session(session_id)
        except Exception as e:
            logger.error(f"Error closing session {session_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    # Load configuration to get server settings
    config_manager = get_config_manager("../config/config.json")
    server_settings = config_manager.server
    
    uvicorn.run(
        app, 
        host=server_settings.host, 
        port=server_settings.port
    )