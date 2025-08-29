"""
User Profiler Agent.

This agent is responsible for gathering user's profile information to better tune other agents' tone and questions.
"""

import json

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool


from models.data_models import Project, TeamMember

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
    User profiler agent responsible for gathering user's profile information.

    This agent specializes in:
    - Analyzing the project requested from the context
    - Asking user about their role on the project, their experience on past similar projects, skills, and expectations
    - Adding the information to the team by using the same project storage tool used by project management agent
    """

    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the UserProfilerAgent.

        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="You are a User Profiler agent. Your role is to understand the user's capabilities and knowledge to better tune other agents' tone and questions based on their profile. Your role is to:\n\n"
            "1. Analyze the project requested from the context.\n"
            "2. Ask the user about their role on the project, their experience on past similar projects, skills, and expectations.\n"
            "3. Add the information to the team by using the same project storage tool used by project management agent.\n"
            "4. Use the retrieve_project_data_tool and save project data tool to initiate and revise project data\n"
            "5. Transfer back to triage if the request is outside your scope or when the user is satisfied with the project data\n\n"
            "## RULES\n"
            "1. Always be polite and professional.\n"
            "2. Ask clear and concise questions.\n"
            "3. If the user asks for project data, use the retrieve_project_data_tool to retrieve the data."
            "4. If the user asks to save project data, use the save_project_data_tool to save the data."
            "5. When the user profile is complete, ask the user if they would like to save the data."
            "6. If the user would like to save the data, use the save_project_data_tool to save the data."
            "7. If the user would not like to save the data, use the transfer_back_to_triage_tool to transfer back to the triage agent."
        )

        user_profiler_tools = [retrieve_project_data_tool, save_project_data_tool]
        delegate_tools = [transfer_back_to_triage_tool]

        super().__init__(
            description="A user profiler agent responsible for gathering user's profile information.",
            system_message=system_message,
            model_client=model_client,
            tools=user_profiler_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=USER_PROFILER_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
