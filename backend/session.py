import asyncio
import uuid
import json
from autogen_core import SingleThreadedAgentRuntime, TopicId
from autogen_core.models import ChatCompletionClient
from base.messaging import UserLogin
from knowledge.knowledge_service import KnowledgeService
from tools.tools import USER_TOPIC_TYPE
import logging

logger = logging.getLogger(__name__)

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
        """Initialize the session with agents and runtime."""
        try:
            from agents.factory import AgentFactory
            
            # Set a timeout for initialization to prevent hanging
            async with asyncio.timeout(30):  # 30 second timeout
                self.agent_factory = AgentFactory(self)
                await self.agent_factory.register_all_agents()
                await self.agent_factory.add_all_subscriptions()
                
                # Start the runtime
                self.runtime.start()
                logger.info(f"Runtime started for session {self.session_id}")

                # Create a new project for the session
                project_data = json.dumps({
                    "name": "New Project",
                    "description": "A new project",
                    "methodology": "Hybrid",
                    "sdlc_phase": "Concept",
                    "status": "Initiation"
                })
                project_id_json = self.knowledge_service.create_entity('Project', project_data)
                project_id_data = json.loads(project_id_json)
                
                # Check if creation was successful
                if "error" in project_id_data:
                    raise RuntimeError(f"Failed to create project: {project_id_data['error']}")
                
                if "id" not in project_id_data:
                    raise RuntimeError(f"Invalid response from create_entity: {project_id_data}")
                
                self.project_id = project_id_data["id"]
                logger.info(f"Project created for session {self.session_id}: {self.project_id}")

                # Publish initial login message
                await self.runtime.publish_message(
                    UserLogin(),
                    topic_id=TopicId(USER_TOPIC_TYPE, source=self.session_id)
                )
                logger.info(f"Session {self.session_id} initialized successfully")
                
        except asyncio.TimeoutError:
            logger.error(f"Session {self.session_id} initialization timed out")
            await self.close()
            raise RuntimeError(f"Session initialization timed out for {self.session_id}")
        except Exception as e:
            logger.error(f"Error initializing session {self.session_id}: {e}")
            # Clean up on initialization failure
            await self.close()
            raise

    async def close(self):
        """Close the session and cleanup resources."""
        try:
            # Stop the runtime first to prevent new messages
            if self.runtime:
                await self.runtime.stop()
                logger.info(f"Runtime stopped for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error stopping runtime for session {self.session_id}: {e}")
        
        # Clear the queues to prevent memory leaks and task_done issues
        try:
            while not self.input_queue.empty():
                try:
                    self.input_queue.get_nowait()
                    self.input_queue.task_done()
                except asyncio.QueueEmpty:
                    break
        except Exception as e:
            logger.warning(f"Error clearing input queue for session {self.session_id}: {e}")
        
        try:
            while not self.response_queue.empty():
                try:
                    self.response_queue.get_nowait()
                    self.response_queue.task_done()
                except asyncio.QueueEmpty:
                    break
        except Exception as e:
            logger.warning(f"Error clearing response queue for session {self.session_id}: {e}")

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
        """Close a session and cleanup all resources."""
        async with self._lock:
            session = self.sessions.pop(session_id, None)
        
        if session:
            try:
                logger.info(f"Closing session {session_id}")
                await session.close()
                logger.info(f"Session {session_id} closed successfully")
            except Exception as e:
                logger.error(f"Error closing session {session_id}: {e}")
            finally:
                # Ensure session is removed even if close fails
                async with self._lock:
                    self.sessions.pop(session_id, None)
