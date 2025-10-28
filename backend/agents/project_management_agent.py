import json

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from session import UserSession

from models.data_models import Project

from base.AIAgent import AIAgent
from tools.tools import (
    PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    transfer_back_to_triage_tool,
    UUIDEncoder,
)
from tools.knowledge_tools import create_knowledge_tools

class ProjectManagementAgent(AIAgent):
    """
    Project management agent responsible to create or modify a project.
    
    This agent specializes in project management activities including:
    - Guiding users through PMI best practices
    - Providing project management guidance and standards and project data
    - Creating or modifying a project
    """
    
    def __init__(self, user_session: UserSession, tools: list[Tool] = None):
        # Track which entity schemas have been retrieved to prevent loops
        self._retrieved_schemas = set()
        """
        Initialize the ProjectManagementAgent.
        
        Args:
            user_session: The user session object.
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="You are a certified Project Management Professional (PMP) agent specializing in PMI best practices. "  
            "Your role is to:\n\n"
            "1. Guide users through PMI project management standards and best practices\n"
            "2. Help create comprehensive, PMI-compliant project\n"
            "3. Educate users on the PMBOK Guide framework and its application\n"
            "4. Educate users on project context and project data\n"
            "5. Transfer back to triage if the request is outside your scope, if you have obtained the project data or when the user is satisfied with the project data\n\n"
            "## CONTEXT AND PROJECT DATA\n"
            #"1. Session_id of this project is: '" + user_session.session_id + "'. "
            #"1. Create and update entities, using **only** available entity types and attributes defined in get_all_entities_with_schemas_tool.\n"
            "1. Make a plan of which entities and relationships to create or update.\n"
            "    Example: if user asks to create a project with two users A and B, then you shall create a project, create a user A, create another user B, create a relationship between the user A and the project, create a relationship between the user B and the project.\n"
            "2. After creating entities, make sure to create appropriate relationships between them."
            "    Example: after creating a user, make sure it has the proper project role and create the relationship with label 'assigned_to' between the user and the project.\n"
            "3. When the tool returns a success message, move to the next task until the plan is completed."
            "    Example of a successful user creation return message: {\"status\": \"success\", \"message\": \"User successfully created\", \"task_completed\": true}\n"
            "4. provide a summary of the plan and the task completed and check whether other tool calls are needed."
            "5. stop calling tools when the plan is completed."
            #"4. **Update existing entities**: Use update_entity_tool to modify existing entities.\n"
            #"1. before calling create_entity_tool, use get_entity_schema_tool to get the schema of the entity type use its output to format the input of create_entity_tool accordingly. \n"
            #"   Example: to create a 'project' entity, call get_entity_schema_tool with 'project' entity type to get the schema and use its schema to format the input of create_entity_tool accordingly.\n"
            "## RULES\n"
            "1. Always follow PMI standards and best practices. Be thorough, professional, and educational.\n"
            "2. Provide clear explanations of PMI concepts and how they apply to the user's project.\n"
            "3. When the user task is completed, transfer back to triage.\n"
        )
                
        # Create a custom get_entity_schema tool that prevents loops
        from autogen_core.tools import FunctionTool
        from typing import Annotated
        

        
        project_management_tools = [
            
        ]
        delegate_tools = [transfer_back_to_triage_tool]
        
        
        
        super().__init__(
            user_session=user_session,
            description="A certified PMP agent responsible for PMI best practices and comprehensive project management.",
            system_message=system_message,
            tools=project_management_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
