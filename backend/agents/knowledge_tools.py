from typing import Dict, List, Any, Optional
from autogen_core.tools import FunctionTool
from knowledge.knowledge_service import KnowledgeService

# Initialize the knowledge service
knowledge_service = KnowledgeService()

async def get_full_project_context(project_id: str) -> str:
    """
    Retrieve the full context of a project, including all related entities.

    Args:
        project_id (str): The unique identifier (UUID string) of the project to retrieve.

    Returns:
        str: A JSON-formatted string representing the project and all its related entities.
            The structure includes the project and nested or referenced related entities
            (such as epics, team, risks, milestones, etc.). If the project is not found,
            returns a JSON string with an "error" key and message.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "name": "Project Alpha",
            "epics": [...],
            "team": {...},
            ...
        }
    """
    return knowledge_service.get_full_project_context(project_id)

async def get_entity_by_id(entity_type: str, entity_id: str) -> str:
    """
    Retrieve a specific entity by its type and unique identifier, without loading relationships.

    Args:
        entity_type (str): The type of the entity (e.g., "Project", "Epic", "UserStory").
        entity_id (str): The unique identifier (UUID string) of the entity.

    Returns:
        str: A JSON-formatted string representing the entity's data, excluding related entities.
            If the entity is not found, returns a JSON string with an "error" key and message.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "name": "Sample Epic",
            ...
        }
    """
    return knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=False)

async def get_entity_with_relationships(entity_type: str, entity_id: str) -> str:
    """
    Retrieve a specific entity by its type and unique identifier, including all its relationships.

    Args:
        entity_type (str): The type of the entity (e.g., "Project", "Epic", "UserStory").
        entity_id (str): The unique identifier (UUID string) of the entity.

    Returns:
        str: A JSON-formatted string representing the entity and all its related entities.
            If the entity is not found, returns a JSON string with an "error" key and message.

    Example:
        {
            "id": "123e4567-e89b-12d3-a456-426614174001",
            "name": "Sample Epic",
            "user_stories": [...],
            ...
        }
    """
    return knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=True)

async def create_entity(entity_type: str, entity_data_json: str) -> str:
    """
    Create a new entity of the specified type using the provided JSON data.

    Args:
        entity_type (str): The type of the entity to create (e.g., "Project", "Epic").
        entity_data_json (str): A JSON-formatted string containing the entity's data.
            The ID should not be provided; it will be generated automatically.

    Returns:
        str: A JSON-formatted string containing the result of the creation operation,
            including the generated entity ID, entity type, and a success status.
            If creation fails, returns a JSON string with an "error" key and message.

    Example:
        {
            "success": true,
            "entity_id": "123e4567-e89b-12d3-a456-426614174002",
            "entity_type": "Epic",
            "message": "Epic created successfully"
        }
    """
    return knowledge_service.create_entity(entity_type, entity_data_json)

async def update_entity(entity_type: str, entity_id: str, updates_json: str) -> str:
    """
    Update an existing entity by its type and unique identifier with the provided updates.

    Args:
        entity_type (str): The type of the entity to update (e.g., "Project", "Epic").
        entity_id (str): The unique identifier (UUID string) of the entity to update.
        updates_json (str): A JSON-formatted string containing the fields to update.

    Returns:
        str: A JSON-formatted string indicating the success status of the update operation.
            If the update fails, returns a JSON string with an "error" key and message.

    Example:
        {
            "success": true,
            "message": "Epic updated successfully"
        }
    """
    return knowledge_service.update_entity(entity_type, entity_id, updates_json)

async def delete_entity(entity_type: str, entity_id: str) -> str:
    """
    Delete an entity by its type and unique identifier.

    Args:
        entity_type (str): The type of the entity to delete (e.g., "Project", "Epic").
        entity_id (str): The unique identifier (UUID string) of the entity to delete.

    Returns:
        str: A JSON-formatted string indicating the success status of the deletion operation.
            If the deletion fails, returns a JSON string with an "error" key and message.

    Example:
        {
            "success": true,
            "message": "Epic deleted successfully"
        }
    """
    return knowledge_service.delete_entity(entity_type, entity_id)

async def query_entities(entity_type: str, filters_json: str = "{}") -> str:
    """
    Query entities of a specific type using optional filter criteria.

    Args:
        entity_type (str): The type of entities to query (e.g., "UserStory", "Risk").
        filters_json (str, optional): A JSON-formatted string specifying filter criteria.
            Defaults to an empty JSON object (no filters).

    Returns:
        str: A JSON-formatted string representing a list of matching entities.
            If no entities match or an error occurs, returns a JSON string with an "error" key and message.

    Example:
        [
            {
                "id": "123e4567-e89b-12d3-a456-426614174003",
                "title": "User Story 1",
                ...
            },
            ...
        ]
    """
    return knowledge_service.query_entities(entity_type, filters_json)


# Additional utility: Get entity types
async def get_entity_types() -> str:
    """
    Get the list of entity types
    """
    return knowledge_service.get_entity_types()

# Tool instances
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