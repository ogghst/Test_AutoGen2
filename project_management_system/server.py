import asyncio
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from autogen_core import SingleThreadedAgentRuntime, TopicId, MessageContext
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

app = FastAPI()

runtime: SingleThreadedAgentRuntime = None
model_client = None
logger = None

@app.on_event("startup")
async def startup_event():
    global runtime, model_client, logger
    # Load configuration - get_config_manager handles all fallback cases
    config_manager = get_config_manager("config.json")

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

    logger.info(json.dumps(Project.model_json_schema(), indent=2))

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

@app.on_event("shutdown")
async def shutdown_event():
    global runtime, model_client
    if runtime:
        await runtime.stop()
    if model_client:
        await model_client.close()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws/test_session");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Client connected: {session_id}")

    # Queue for receiving agent responses
    response_queue = asyncio.Queue()

    # Subscription to handle agent responses
    async def handle_response(message: AgentResponse, ctx: MessageContext):
        await response_queue.put(message)

    # Subscribe to the user topic for this session
    user_topic = TopicId(USER_TOPIC_TYPE, source=session_id)
    subscription_id = await runtime.subscribe(handle_response, topic_id=user_topic)

    # Start a new user session by sending a login message.
    await runtime.publish_message(
        UserLogin(),
        topic_id=user_topic
    )

    # Task to send agent responses to the client
    async def send_responses():
        while True:
            response = await response_queue.get()
            if response is None:
                break
            if response.context and len(response.context) > 0:
                agent_reply = response.context[-1].content
                await websocket.send_text(agent_reply)

    send_task = asyncio.create_task(send_responses())

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from {session_id}: {data}")

            triage_topic = TopicId(TRIAGE_AGENT_TOPIC_TYPE, source=session_id)
            await runtime.publish_message(
                UserTask(context=[UserMessage(content=data)]),
                topic_id=triage_topic
            )

    except WebSocketDisconnect:
        logger.info(f"Client disconnected: {session_id}")
    finally:
        logger.info(f"Closing connection for {session_id}")
        await response_queue.put(None)
        send_task.cancel()
        await runtime.unsubscribe(subscription_id)
