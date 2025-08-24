"""
User Stories Gathering Agent for generating comprehensive user stories with EARS notation.

This agent specializes in unpacking high-level requirements into detailed user stories
with comprehensive acceptance criteria using the Easy Approach to Requirements Syntax (EARS).
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from base.AIAgent import AIAgent
from .tools import (
    USER_STORIES_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,

    transfer_back_to_triage_tool,
)


class UserStoriesAgent(AIAgent):
    """
    User Stories Gathering Agent responsible for generating comprehensive user stories
    with EARS notation acceptance criteria.
    
    This agent specializes in:
    - Unpacking high-level requirements into detailed user stories
    - Generating EARS notation acceptance criteria
    - Covering edge cases and scenarios developers typically handle
    - Creating stories for complex systems like review systems
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the UserStoriesAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard user story generation tools
        """
        system_message = SystemMessage(
            content="You are a User Stories Gathering Agent specializing in creating comprehensive user stories "
            "with EARS (Easy Approach to Requirements Syntax) notation acceptance criteria.\n\n"
            "Your expertise includes:\n"
            "1. **Unpacking high-level requirements** into detailed, actionable user stories\n"
            "2. **Generating EARS notation** acceptance criteria covering:\n"
            "   - Ubiquitous requirements (always true)\n"
            "   - Event-driven requirements (when X happens)\n"
            "   - State-driven requirements (while X is true)\n"
            "   - Unwanted behavior requirements (never X)\n"
            "3. **Covering edge cases** that developers typically handle:\n"
            "   - Invalid inputs and validation\n"
            "   - Rate limiting and security\n"
            "   - Error handling and recovery\n"
            "   - Performance and scalability\n"
            "   - Accessibility and internationalization\n\n"
            "4. **Creating comprehensive story sets** for complex systems\n\n"
            "When generating user stories, always:\n"
            "   - Follow the 'As a... I want... So that...' format\n"
            "   - Include multiple acceptance criteria per story\n"
            "   - Consider different user roles and permissions\n"
            "   - Address both happy path and edge cases\n"
            "   - Use clear, testable acceptance criteria\n\n"
            "Available tools:\n"
            "- transfer_back_to_triage: Transfer back to triage if the request is outside your scope or when the user is satisfied with the user stories\n\n"
            "Always be thorough and consider the developer's perspective when creating acceptance criteria."
            "After generating the user stories, ask the user if the user story is complete."
            "If the user is satisfied with the user stories, use the transfer_back_to_triage_tool to transfer back to the triage agent."
        )
        
        # These are regular tools that return content, not delegate tools
        tools = [

        ]
        
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A specialized agent for generating comprehensive user stories with EARS notation acceptance criteria.",
            system_message=system_message,
            model_client=model_client,
            tools=tools or [],
            delegate_tools=delegate_tools,
            agent_topic_type=USER_STORIES_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
