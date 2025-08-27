import asyncio
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from autogen_core import SingleThreadedAgentRuntime, TopicId, MessageContext, TypeSubscription
import json
from config.logging_config import setup_logging, get_logger
from base.utils import configure_oltp_tracing
from base.model_client import create_model_client
from agents.factory import AgentFactory
from agents.tools import USER_TOPIC_TYPE, TRIAGE_AGENT_TOPIC_TYPE
from base.messaging import UserLogin, UserTask, AgentResponse
from config.settings import get_config_manager
from models.data_models import Project
from autogen_core.models import UserMessage
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    global runtime, model_client, logger, agent_factory
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

    #logger.info(json.dumps(Project.model_json_schema(), indent=2))

    # Configure tracing based on configuration
    if config_manager.runtime.enable_tracing:
        tracing_endpoint = config_manager.runtime.tracing_endpoint
        tracer_provider = configure_oltp_tracing(endpoint=tracing_endpoint)
    else:
        tracer_provider = configure_oltp_tracing()

    # Create the runtime
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer_provider)


    # Create the model client with configuration
    logger.info(f"LLM Provider: {config_manager.llm_provider.value}")

    # Pass configuration to model client creation
    model_client = create_model_client(config_manager=config_manager)

    # Create agent factory and register all agents
    logger.info("Creating agent factory and registering agents")
    agent_factory = AgentFactory(runtime, model_client)
    registered_agents = await agent_factory.register_all_agents()

    # Add subscriptions for all agents
    logger.info("Adding subscriptions for all agents")
    await agent_factory.add_all_subscriptions()

    # Start the runtime
    logger.info("Starting runtime")
    runtime.start()

    #await runtime.stop_when_idle()  
    yield
    
    # Shutdown logic
    if runtime:
        await runtime.stop()
    if model_client:
        await model_client.close()

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
    session_id = str(uuid.uuid4())
    logger.info(f"Created new session: {session_id}")
    
    # Start a new user session by sending a login message.
    await runtime.publish_message(
        UserLogin(), 
        topic_id=TopicId(USER_TOPIC_TYPE, source=session_id)
    ) 
    
    return {"session_id": session_id}

from agents.websocket_agent import WebSocketAgent

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Client connected: {session_id}")

    logger.info(f"Runtime: {runtime}")

    # Subscribe the agent to the user topic for this session
    subscription_id = await runtime.add_subscription(
        TypeSubscription(topic_type=USER_TOPIC_TYPE, agent_type=TRIAGE_AGENT_TOPIC_TYPE)
    )

    # Task to send agent responses to the client
    async def send_responses():
        while True:
            response = await agent_factory.response_queue.get()
            if response is None:
                break
            if response.context and len(response.context) > 0:
                agent_reply = response.context[-1].content
                await websocket.send_text(agent_reply)

    send_task = asyncio.create_task(send_responses())

    try:
        while True:
            data = await websocket.receive_text()
            await agent_factory.input_queue.put(data)
            logger.info(f"Received message from {session_id}: {data}")

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    finally:
        logger.info(f"Closing connection for {session_id}")
        await agent_factory.response_queue.put(None)
        send_task.cancel()
        await runtime.unsubscribe(subscription_id)


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