"""
Project Management Agent for the handoffs pattern.

This agent is responsible for guiding users through PMI best practices and creating
comprehensive project management plans in markdown format.
"""

import json

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool


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

class ProjectManagementAgent(AIAgent):
    """
    Project management agent responsible for PMI best practices and comprehensive project planning.
    
    This agent specializes in project management activities including:
    - Guiding users through PMI best practices
    - Providing project management guidance and standards
    - Creating an initial project management plan
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
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
            "4. Use the retrieve_project_data_tool and save project data tool to initiate and revise project data\n"
            "5. Provide expert advice on project management methodologies and processes\n"
            "6. Transfer back to triage if the request is outside your scope or when the user is satisfied with the project data\n\n"
            "## RULES\n"
            "1. Always follow PMI standards and best practices. Be thorough, professional, and educational. "
            "2. When creating project management plans, ensure they include all essential PMI components "
            "such as scope, schedule, cost, quality, risk, communication, and stakeholder management. "
            "3. Project data schema is defined as follows: '" + json.dumps(Project.model_json_schema(), cls=UUIDEncoder) + "'. Don't create any entity below 'Scope' field like 'Epic', 'User Story', 'Task', etc. \n"
            "4. Provide clear explanations of PMI concepts and how they apply to the user's project."
            "5. If the user asks for project data, use the retrieve_project_data_tool to retrieve the data."
            "6. If the user asks to save project data, use the save_project_data_tool to save the data."
            "7. When the project data is complete, ask the user if they would like to save the data."
            "8. If the user would like to save the data, use the save_project_data_tool to save the data."
            "9. If the user would not like to save the data, use the transfer_back_to_triage_tool to transfer back to the triage agent."
            "## UUID Management \n\n"
            "When generating the JSON with entities and relationships:\n"
            "1. First identify all unique entities in the content.\n"
            "2. Create a consistent mapping of entity names to UUIDs before generating relationships.\n"
            "3. To generate UUIDs, use UUID4 format for all entities.\n" 
            "4. Generate a random UUID for each entity.\n" 
            "5. Make sure to use the same UUID for the same entity across the project.\n"
            "6. After assigning all UUIDs, create relationships using these exact UUID values.\n"
            "7. Before finalizing, verify that all relationship references match the assigned entity UUIDs.\n"
        )

        
        
        project_management_tools = [retrieve_project_data_tool, save_project_data_tool]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A certified PMP agent responsible for PMI best practices and comprehensive project management planning.",
            system_message=system_message,
            model_client=model_client,
            tools=project_management_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
