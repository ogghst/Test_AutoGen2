from typing import Dict, List, Any, Optional
from autogen_core.tools import FunctionTool
from knowledge.knowledge_service import KnowledgeService
from session import UserSession

# Tool factory functions
def create_knowledge_tools(user_session: UserSession) -> List[FunctionTool]:
    """
    Factory function to create knowledge tools with a specific knowledge service instance.
    """
    
    async def get_current_session_id() -> str:
        return user_session.session_id
    
    async def get_session_project_context() -> str:
        return user_session.knowledge_service.get_full_project_context(user_session.project_id)

    async def get_full_project_context(project_id: str) -> str:
        return user_session.knowledge_service.get_full_project_context(project_id)

    async def get_entity_by_id(entity_type: str, entity_id: str) -> str:
        return user_session.knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=False)

    async def get_entity_with_relationships(entity_type: str, entity_id: str) -> str:
        return user_session.knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=True)

    async def create_entity(entity_type: str, entity_data_json: str) -> str:
        return user_session.knowledge_service.create_entity(entity_type, entity_data_json)

    async def update_entity(entity_type: str, entity_id: str, updates_json: str) -> str:
        return user_session.knowledge_service.update_entity(entity_type, entity_id, updates_json)

    async def delete_entity(entity_type: str, entity_id: str) -> str:
        return user_session.knowledge_service.delete_entity(entity_type, entity_id)

    async def query_entities(entity_type: str, filters_json: str = "{}") -> str:
        return user_session.knowledge_service.query_entities(entity_type, filters_json)

    async def get_entity_types() -> str:
        return user_session.knowledge_service.get_entity_types()

    # Tool instances
    get_current_session_id_tool = FunctionTool(
        get_current_session_id,
        description="Get the ID of the current session. Returns string."
    )
    
    get_session_project_context_tool = FunctionTool(
        get_session_project_context,
        description="Get the full context of the project for the current session. Returns JSON string."
    )
    
    get_full_project_context_tool = FunctionTool(
        get_full_project_context,
        description="Get the full context of a project including all related entities (epics, team, risks, milestones, etc.). Returns JSON string."
    )

    get_entity_by_id_tool = FunctionTool(
        get_entity_by_id,
        description="Get a specific entity by ID without loading relationships. Returns JSON string representation of the entity."
    )

    get_entity_with_relationships_tool = FunctionTool(
        get_entity_with_relationships,
        description="Get a specific entity by ID with all its relationships loaded. Returns JSON string representation with related entities."
    )

    create_entity_tool = FunctionTool(
        create_entity,
        description="Create a new entity without providing an ID. The system will generate a UUID. Returns JSON string with the generated ID."
    )

    update_entity_tool = FunctionTool(
        update_entity,
        description="Update an existing entity by ID. Returns JSON string with success status."
    )

    delete_entity_tool = FunctionTool(
        delete_entity,
        description="Delete an entity by ID. Returns JSON string with success status."
    )

    query_entities_tool = FunctionTool(
        query_entities,
        description="Query entities of a specific type with optional filters. Returns JSON string representation of matching entities."
    )

    get_entity_types_tool = FunctionTool(
        get_entity_types,
        description="Get the list of entity types. Returns JSON string representation of the entity types."
    )

    return [        
        get_current_session_id_tool,
        get_session_project_context_tool,
        get_full_project_context_tool,
        get_entity_by_id_tool,
        get_entity_with_relationships_tool,
        create_entity_tool,
        update_entity_tool,
        delete_entity_tool,
        query_entities_tool,
        get_entity_types_tool,
    ]