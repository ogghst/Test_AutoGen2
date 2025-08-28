"""
Human Agent for the handoffs pattern.

This agent handles complex requests that require human intervention.
"""

from config.logging_config import get_logger
from autogen_core import MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import AssistantMessage

from base.messaging import UserTask, AgentResponse
from .tools import HUMAN_AGENT_TOPIC_TYPE, USER_TOPIC_TYPE


class HumanAgent(RoutedAgent):
    """
    Human agent for handling complex requests that require human intervention.
    
    This agent provides a bridge between the AI system and human operators
    for cases where automated processing is insufficient.
    """
    
    def __init__(self, agent_topic_type: str, user_topic_type: str) -> None:
        """
        Initialize the HumanAgent.
        
        Args:
            agent_topic_type: The topic type for agent communication
            user_topic_type: The topic type for user communication
        """
        super().__init__("A human agent for handling complex requests.")
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type

    @message_handler
    async def handle_user_task(self, message: UserTask, ctx: MessageContext) -> None:
        """
        Handle user tasks by requesting human intervention.
        
        Args:
            message: The user task message containing context
            ctx: The message context for routing
        """
        logger = get_logger(__name__)
        logger.info(f"{self.id.type}: Human intervention required")

        # Get human input
        human_input = input("Human Agent: ")
        #print(f"{'-'*80}\n{self.id.type}:\nHuman response: {human_input}", flush=True)
        
        logger.info(f"{self.id.type}: Human response received: {human_input}")

        logger.info(f"{self.id.type}: Publishing human response")
        message.context.append(AssistantMessage(content=human_input, source=self.id.type))
        await self.publish_message(
            AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
            topic_id=TopicId(self._user_topic_type, source=self.id.key),
        )
