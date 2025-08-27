
import asyncio
from autogen_core import MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import UserMessage
from base.messaging import UserLogin, UserTask, AgentResponse
from .tools import USER_TOPIC_TYPE, TRIAGE_AGENT_TOPIC_TYPE
from config.logging_config import get_logger

class WebSocketAgent(RoutedAgent):
    def __init__(self, input_queue: asyncio.Queue, response_queue: asyncio.Queue, user_topic_type: str, agent_topic_type: str):
        super().__init__("A websocket agent for managing user sessions.")
        self._input_queue = input_queue
        self._response_queue = response_queue
        self._user_topic_type = user_topic_type
        self._agent_topic_type = agent_topic_type

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        logger = get_logger(__name__)
        logger.info(f"User login, session ID: {self.id.key}")
        
        user_input = await self._input_queue.get()
        
        topic_id = TopicId(self._agent_topic_type, source=self.id.key)
        logger.info(f"Starting conversation with {self._agent_topic_type}")
        await self.publish_message(
            UserTask(context=[UserMessage(content=user_input, source="User")]), 
            topic_id=topic_id
        )


    @message_handler
    async def handle_task_result(self, message: AgentResponse, ctx: MessageContext) -> None:
        logger = get_logger(__name__)
        logger.info(f"Handling task result from {message.reply_to_topic_type}: {message.context}")
        
        await self._response_queue.put(message)

        user_input = await self._input_queue.get()

        #if user_input.strip().lower() == "exit":
        #    logger.info(f"User session ended, session ID: {self.id.key}")
        #    return
            
        message.context.append(UserMessage(content=user_input, source="User"))
        logger.info(f"Publishing user input to {message.reply_to_topic_type}: {user_input}")

        await self.publish_message(
            UserTask(context=message.context), 
            topic_id=TopicId(message.reply_to_topic_type, source=self.id.key)
        )
