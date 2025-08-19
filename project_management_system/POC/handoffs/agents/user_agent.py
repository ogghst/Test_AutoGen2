"""
User Agent for the handoffs pattern.

This agent manages user sessions and handles user input/output.
"""

import logging
from autogen_core import MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import UserMessage

from ..base.messaging import UserLogin, UserTask, AgentResponse
from .tools import USER_TOPIC_TYPE, TRIAGE_AGENT_TOPIC_TYPE


class UserAgent(RoutedAgent):
    """
    User agent for managing user sessions and handling user input/output.
    
    This agent serves as the interface between users and the AI system,
    managing conversation flow and user session state.
    """
    
    def __init__(self, user_topic_type: str, agent_topic_type: str) -> None:
        """
        Initialize the UserAgent.
        
        Args:
            user_topic_type: The topic type for user communication
            agent_topic_type: The topic type for agent communication
        """
        super().__init__("A user agent for managing user sessions.")
        self._user_topic_type = user_topic_type
        self._agent_topic_type = agent_topic_type

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        """
        Handle user login and start the conversation.
        
        Args:
            message: The user login message
            ctx: The message context for routing
        """
        logger = logging.getLogger(__name__)
        logger.info(f"User login, session ID: {self.id.key}")
        print(f"User login, session ID: {self.id.key}.", flush=True)
        
        # Get the user's initial input after login.
        user_input = input("User: ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        
        # Start the conversation with the triage agent
        topic_id = TopicId(self._agent_topic_type, source=self.id.key)
        logger.info(f"Starting conversation with {self._agent_topic_type}")
        await self.publish_message(
            UserTask(context=[UserMessage(content=user_input, source="User")]), 
            topic_id=topic_id
        )

    @message_handler
    async def handle_task_result(self, message: AgentResponse, ctx: MessageContext) -> None:
        """
        Handle task results from agents and get user input for continuation.
        
        Args:
            message: The agent response message
            ctx: The message context for routing
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Handling task result from {message.reply_to_topic_type}")
        
        # Get the user's input after receiving a response from an agent.
        user_input = input("User (type 'exit' to close the session): ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        
        if user_input.strip().lower() == "exit":
            logger.info(f"User session ended, session ID: {self.id.key}")
            print(f"{'-'*80}\nUser session ended, session ID: {self.id.key}.")
            return
            
        message.context.append(UserMessage(content=user_input, source="User"))
        logger.info(f"Publishing user input to {message.reply_to_topic_type}")

        await self.publish_message(
            UserTask(context=message.context), 
            topic_id=TopicId(message.reply_to_topic_type, source=self.id.key)
        )
