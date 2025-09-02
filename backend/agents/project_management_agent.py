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
            "2. Help create comprehensive, PMI-compliant project description using available entity types and attributes defined in their schemas.\n"
            "3. Educate users on the PMBOK Guide framework and its application\n"
            "4. Educate users on project context and project data\n"
            "5. Transfer back to triage if the request is outside your scope, if you have obtained the project data or when the user is satisfied with the project data\n\n"
            #"## CONTEXT AND PROJECT DATA\n"
            #"1. Session_id of this project is: '" + user_session.session_id + "'. "
            #"2. Only create entities that are defined in the project data model, with proper schema.\n"
            #"## WORKFLOW AND TOOL USAGE\n"
            #"1. **First, get available entity types**: If not known, use get_entity_types_tool to see what entity types are available.\n"
            #"2. **Get schema only when needed**: Use get_entity_schema per entity type when you need to understand the structure.\n"
            #"3. **Create entities when ready**: Use create_entity_tool when you have all the required information to create a new entity.\n"
            #"4. **Update existing entities**: Use update_entity_tool to modify existing entities.\n"
            #"1. before calling create_entity_tool, use get_entity_schema_tool to get the schema of the entity type use its output to format the input of create_entity_tool accordingly. \n"
            #"   Example: to create a 'project' entity, call get_entity_schema_tool with 'project' entity type to get the schema and use its schema to format the input of create_entity_tool accordingly.\n"
            "## RULES\n"
            "1. Always follow PMI standards and best practices. Be thorough, professional, and educational.\n"
            "2. When creating project management plans, ensure they include all essential PMI components.\n"
            "3. Provide clear explanations of PMI concepts and how they apply to the user's project.\n"
            "4. When the project data is complete, ask the user if they would like to save the data.\n"
        )
                
        # Create a custom get_entity_schema tool that prevents loops
        from autogen_core.tools import FunctionTool
        from typing import Annotated
        
        async def get_entity_schema_safe(entity_type: Annotated[str, "The type of the entity to get the schema of."]) -> str:
            """
            Get the JSON schema of a specific entity type with loop prevention.
            """
            if entity_type.lower() in self._retrieved_schemas:
                return f"Schema for '{entity_type}' has already been retrieved. Please proceed with your task using the previously obtained schema information."
            
            # Mark this schema as retrieved
            self._retrieved_schemas.add(entity_type.lower())
            
            # Call the actual tool
            return user_session.knowledge_service.get_entity_schema(entity_type)
        
        get_entity_schema_safe_tool = FunctionTool(
            get_entity_schema_safe,
            description="Get entity schema formatted specifically for LLM consumption. Returns JSON string. WARNING: Only call this tool ONCE per entity type. Do not call repeatedly for the same entity type."
        )
        
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
