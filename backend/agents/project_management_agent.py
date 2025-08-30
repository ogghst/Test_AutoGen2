"""
Project Management Agent for the handoffs pattern.

This agent is responsible for guiding users through PMI best practices and creating
comprehensive project management plans in markdown format.
"""

import json

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool
from typing import TYPE_CHECKING

from models.data_models import Project

from base.AIAgent import AIAgent
from .tools import (
    PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    retrieve_project_data_tool,
    save_project_data_tool,
    transfer_back_to_triage_tool,
    UUIDEncoder,
)

from .knowledge_tools import get_tools

# Add forward reference to avoid circular import
if TYPE_CHECKING:
    from session import UserSession

class ProjectManagementAgent(AIAgent):
    """
    Project management agent responsible for PMI best practices and comprehensive project planning.
    
    This agent specializes in project management activities including:
    - Guiding users through PMI best practices
    - Providing project management guidance and standards
    - Creating an initial project management plan
    """
    
    def __init__(self, user_session: "UserSession", tools: list[Tool] = None):  # Use string literal for forward reference
        """
        Initialize the ProjectManagementAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="You are a certified Project Management Professional (PMP) agent specializing in PMI best practices. Your role is to:\n\n"
            "1. Guide users through PMI project management standards and best practices\n"
            "2. Help create comprehensive, PMI-compliant project management plans\n"
            "3. Educate users on the PMBOK Guide framework and its application\n"
            "4. Provide expert advice on project management methodologies and processes\n"
            "5. Transfer back to triage if the request is outside your scope or when the user is satisfied with the project data\n\n"
            "## RULES\n"
            "1. Always follow PMI standards and best practices. Be thorough, professional, and educational. "
            "2. When creating project management plans, ensure they include all essential PMI components "
            "such as scope, schedule, cost, quality, risk, communication, and stakeholder management. "
            "3. Project data schema is defined as follows: '" + json.dumps(Project.model_json_schema(), cls=UUIDEncoder) + "'. "
            "3.0 Start by getting the actual project data using the get_actual_project_context tool. "
            "3.1 You shall manage only Project, Team, Person, Stakeholder, and Issue entities. "
            "3.2 You can suggest to the user to create a new entity if it is not in the schema. \n"
            "3.3 You can suggest to the user to create a new relationship if it is not in the schema. \n"
            "3.4 You can suggest to the user to modify other entities if the change you are describing has impact on other entities. \n"
            "4. Provide clear explanations of PMI concepts and how they apply to the user's project."
            "5. If the user asks for project data, use the get_full_project_context to retrieve the data."
            "6. If the user asks to save project data, use the create_entity or update_entity to save the data."
            "7. When the project data is complete, ask the user if they would like to save the data."
        )

        
        
        project_management_tools = [
            get_tools(user_session)
        ]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A certified PMP agent responsible for PMI best practices and comprehensive project management planning.",
            system_message=system_message,
            model_client=user_session.model_client,
            tools=project_management_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
            user_session=user_session,
            )
