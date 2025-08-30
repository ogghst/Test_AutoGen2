"""
User Profiler Agent for the handoffs pattern.

This agent is responsible for understanding the user's capabilities and knowledge
to better tune other agents' tone and questions based on its profile.
"""

import json

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool


from models.data_models import UserProfiler

from base.AIAgent import AIAgent
from .tools import (
    USER_PROFILER_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    retrieve_project_data_tool,
    save_project_data_tool,
    transfer_back_to_triage_tool,
    UUIDEncoder,
)

class UserProfilerAgent(AIAgent):
    """
    User profiler agent responsible for understanding the user's capabilities and knowledge.

    This agent specializes in user profiling activities including:
    - Asking the user about their role, experience, skills, and expectations
    - Saving the user profile to the project's storage
    """

    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the UserProfilerAgent.

        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard user profiler tools
        """
        system_message = SystemMessage(
            content="You are a User Profiler agent. Your role is to:\n\n"
            "1. Understand the user's capabilities and knowledge to better tune other agents' tone and questions based on its profile.\n"
            "2. Ask the user about their role on the project, their experience on past similar projects, skills, and expectations.\n"
            "3. Use the save_project_data_tool to save the user profile to the project's storage.\n"
            "4. Transfer back to triage when the user profile is complete.\n\n"
            "## RULES\n"
            "1. Be friendly and conversational.\n"
            "2. Ask one question at a time.\n"
            "3. Start by asking the user about their role in the project.\n"
            "4. Then, ask about their experience with similar projects.\n"
            "5. Then, ask about their skills.\n"
            "6. Finally, ask about their expectations.\n"
            "7. When the user profile is complete, ask the user if they would like to save the profile.\n"
            "8. If the user would like to save the profile, use the save_project_data_tool to save the data.\n"
            "9. If the user would not like to save the profile, use the transfer_back_to_triage_tool to transfer back to the triage agent.\n"
            "10. User profile data schema is defined as follows: '" + json.dumps(UserProfiler.model_json_schema(), cls=UUIDEncoder) + "'. "
        )



        user_profiler_tools = [retrieve_project_data_tool, save_project_data_tool]
        delegate_tools = [transfer_back_to_triage_tool]

        super().__init__(
            description="A user profiler agent responsible for understanding the user's capabilities and knowledge.",
            system_message=system_message,
            model_client=model_client,
            tools=user_profiler_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=USER_PROFILER_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
