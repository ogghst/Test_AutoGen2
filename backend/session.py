import asyncio
import uuid
import json
from autogen_core import SingleThreadedAgentRuntime, TopicId
from autogen_core.models import ChatCompletionClient
from base.messaging import UserLogin
from knowledge.knowledge_service import KnowledgeService
from tools.tools import USER_TOPIC_TYPE

class UserSession:
    def __init__(self, session_id: str, model_client: ChatCompletionClient, tracer_provider):
        self.session_id = session_id
        self.runtime = SingleThreadedAgentRuntime(tracer_provider=tracer_provider)
        self.knowledge_service = KnowledgeService()
        self.model_client = model_client
        self.input_queue = asyncio.Queue()
        self.response_queue = asyncio.Queue()
        self.agent_factory = None
        self.project_id = None

    async def initialize(self):
        from agents.factory import AgentFactory
        self.agent_factory = AgentFactory(self)
        await self.agent_factory.register_all_agents()
        await self.agent_factory.add_all_subscriptions()
        self.runtime.start()

        # Create a new project for the session
        project_data = json.dumps({
            "name": "New Project",
            "description": "A new project",
            "methodology": "Hybrid",
            "sdlc_phase": "Concept"
        })
        project_id_json = self.knowledge_service.create_entity('Project', project_data)
        project_id_data = json.loads(project_id_json)
        self.project_id = project_id_data["entity_id"]

        await self.runtime.publish_message(
        UserLogin(),
        topic_id=TopicId(USER_TOPIC_TYPE, source=self.session_id)
    )

    async def close(self):
        await self.runtime.stop()

class UserSessionManager:
    def __init__(self, model_client: ChatCompletionClient, tracer_provider):
        self.sessions = {}
        self.model_client = model_client
        self.tracer_provider = tracer_provider
        self._lock = asyncio.Lock()

    async def create_session(self) -> str:
        async with self._lock:
            session_id = str(uuid.uuid4())
            session = UserSession(session_id, self.model_client, self.tracer_provider)
            await session.initialize()
            self.sessions[session_id] = session
            return session_id

    async def get_session(self, session_id: str) -> UserSession:
        async with self._lock:
            return self.sessions.get(session_id)

    async def close_session(self, session_id: str):
        async with self._lock:
            session = self.sessions.pop(session_id, None)
        if session:
            await session.close()
