from asyncio.log import logger
from typing import Dict, List, Any, Optional, Annotated, Literal
from autogen_core.tools import FunctionTool
from knowledge.knowledge_service import KnowledgeService
from session import UserSession
import json
from models.data_models import Project, Issue, Edge, User, UserCreate, IssueCreate, ProjectCreate

# Tool factory functions
def create_knowledge_tools(user_session: UserSession) -> List[FunctionTool]:
    """
    Factory function to create knowledge tools with a specific knowledge service instance.
    """
    
    async def get_current_session_id() -> str:
        """
        Get the ID of the current session.
        
        Args:
            None
            
        Returns:
            str: The ID of the current session.
        """
        return user_session.session_id
    
    async def get_current_project_id() -> str:
        """
        Get the ID of the current project.
        
        Args:
            None
            
        Returns:
            str: The ID of the current project.
        """
        return user_session.project_id
    
    async def set_current_project_id(project_id: Annotated[str, "The ID of the project to set as current."]) -> str:
        """
        Set the ID of the current project.
        
        Args:
            project_id: The ID of the project to set as current.
        """
        user_session.project_id = project_id
        return project_id
    
    async def get_session_project_context() -> str:
        """
        Get the full context of the project for the current session.
        
        Args:
            None
            
        Returns:
            str: The full context of the project for the current session.
        """
        return user_session.knowledge_service.get_full_project_context(user_session.project_id)

    async def get_full_project_context(project_id: Annotated[str, "The ID of the project to get the full context of."]) -> str:
        """
        Get the full context of a project including all related entities (epics, team, risks, milestones, etc.).
        
        Args:
            project_id: The ID of the project to get the full context of.
            
        Returns:
            str: The full context of the project including all related entities.
        """
        return user_session.knowledge_service.get_full_project_context(project_id)

    async def get_entity_by_id(entity_type: Annotated[str, "The type of the entity to get."], entity_id: Annotated[str, "The ID of the entity to get."]) -> str:
        """
        Get a specific entity by ID without loading relationships.
        
        Args:
            entity_type: The type of the entity to get.
            entity_id: The ID of the entity to get.
            
        Returns:
            str: The entity by ID without loading relationships.
        """
        return user_session.knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=False)

    async def get_entity_with_relationships(entity_type: Annotated[str, "The type of the entity to get."], entity_id: Annotated[str, "The ID of the entity to get."]) -> str:
        """ 
        Get a specific entity by ID with all its relationships loaded.
        
        Args:
            entity_type: The type of the entity to get.
            entity_id: The ID of the entity to get.
            
        Returns:
            str: The entity by ID with all its relationships loaded.
        """    
        return user_session.knowledge_service.get_entity_by_id(entity_type, entity_id, include_relationships=True)

    async def create_entity(
        entity_type: Annotated[str, "The type of the entity to create, must be one of the entity types available through get_all_entities_with_schemas_tool."],
        entity_data_json: Annotated[str, "The JSON string representation of the entity to create."]
    ) -> str:
        """
        Create a new entity without providing an ID. The system will generate a UUID. This is the standard way to create a new entity.
        
        Args:
            entity_type: The type of the entity to create.
            entity_data_json: The JSON string representation of the entity to create.
            
        Returns:
            str: The JSON string representation of the created entity.
        """     
        return user_session.knowledge_service.create_entity(entity_type, entity_data_json)

    async def create_project(project: Annotated[ProjectCreate, "The JSON string representation of the project to create."]) -> str:
        """
        Create a new Project entity.
        
        Args:
            project: The Project object to create.
            
        Returns:
            str: A message stating that the project was successfully created, with the content of the created project.
        """
        project_data = user_session.knowledge_service.create_entity("Project", project.model_dump_json())
        user_session.project_id = json.loads(project_data)['id']
        return "Project successfully created, with content: " + project_data

    async def create_issue(issue: Annotated[IssueCreate, "The JSON string representation of the issue to create."]) -> str:
        """
        Create a new Issue entity.
        
        Args:
            issue: The Issue object to create.
            
        Returns:
            str: A message stating that the issue was successfully created, with the content of the created issue.
        """
        return "Issue successfully created, with content: " + user_session.knowledge_service.create_entity("Issue", issue.model_dump_json())
    
    async def create_edge(edge: Annotated[Edge, "The JSON string representation of the edge to create."]) -> str:
        """
        Create a new Edge entity.
        
        Args:
            edge: The Edge object to create.
            
        Returns:
            str: A message stating that the edge was successfully created, with the content of the created edge.
        """
        #return user_session.knowledge_service.create_relationship(edge.source, edge.target, edge.label, edge.)
        return "Edge successfully created, with content: " + user_session.knowledge_service.create_entity("Edge", edge.model_dump_json())
    

    async def create_relationship(source: Annotated[str, "The source entity ID"], target: Annotated[str, "The target entity ID"], label: Annotated[str, "The relationship label, example: 'assigned_to'"], json_data: Annotated[str, "The JSON string representation of the relationassociated data."]) -> str:
        """
        Create a new relationship.
        
        Args:
            source: The source entity ID.
            target: The target entity ID.
            label: The relationship label.
            json_data: The JSON string representation of the relationship associated data.
            
        Returns:
            str: A message stating that the relationship was successfully created, with the content of the created relationship.
        """
        return "Relationship successfully created, with content: " + user_session.knowledge_service.create_relationship(source, target, label, json_data)
    
    async def create_user(user: Annotated[UserCreate, "The JSON string representation of the user to create."]) -> str:
        """
        Create a new User entity.
        
        Args:
            user: The User object to create.
            
        Returns:
            str: A message stating that the user was successfully created, with the content of the created user.
        """
        return "User successfully created, with content: " + user_session.knowledge_service.create_entity("User", user.model_dump_json())
    
    async def create_edge(edge: Annotated[Edge, "The JSON string representation of the edge to create."]) -> str:
        """
        Create a new Edge entity.
        
        Args:
            edge: The Edge object to create.
            
        Returns:
            str: A message stating that the edge was successfully created, with the content of the created edge.
        """
        return user_session.knowledge_service.create_entity("Edge", edge.model_dump_json())

    async def update_entity(entity_type: Annotated[str, "The type of the entity to update."], entity_id: Annotated[str, "The ID of the entity to update."], updates_json: Annotated[str, "The JSON string representation of the updates to apply."]) -> str:
        """
        Update an existing entity by ID.
        
        Args:
            entity_type: The type of the entity to update.
            entity_id: The ID of the entity to update.
            updates_json: The JSON string representation of the updates to apply.
            
        Returns:
            str: The JSON string representation of the updated entity.
        """
        return user_session.knowledge_service.update_entity(entity_type, entity_id, updates_json)

    async def delete_entity(entity_type: Annotated[str, "The type of the entity to delete."], entity_id: Annotated[str, "The ID of the entity to delete."]) -> str:
        """
        Delete an existing entity by ID.
        
        Args:
            entity_type: The type of the entity to delete.
            entity_id: The ID of the entity to delete.
            
        Returns:
            str: The JSON string representation of the deleted entity.
        """
        return user_session.knowledge_service.delete_entity(entity_type, entity_id)

    async def query_entities(entity_type: Annotated[str, "The type of the entities to query."], filters_json: Annotated[str, "The JSON string representation of the filters to apply."]) -> str:
        """
        Query entities of a specific type with optional filters.
        
        Args:
            entity_type: The type of the entities to query.
            filters_json: The JSON string representation of the filters to apply.
            
        Returns:
            str: The JSON string representation of the matching entities.
        """
        return user_session.knowledge_service.query_entities(entity_type, filters_json)

    async def get_entity_types() -> Annotated[str, "The JSON string representation of the list of entity types, without structure."]:
        """
        Get the list of entity types.
        
        Args:
            None
            
        Returns:
            str: The JSON string representation of the list of entity types.
        """
        return user_session.knowledge_service.get_entity_types()
    
    async def get_entity_schema(entity_type: Annotated[str, "The type of the entity to get the schema of."]) -> str:
        """
        Get the JSON schema of a specific entity type.

        Args:
            entity_type: The type of the entity to get the schema of.

        Returns:
            str: The JSON string representation of the entity's model schema.
        """
        return user_session.knowledge_service.get_entity_schema(entity_type)

    async def get_all_entities_with_schemas() -> str:
        """
        Get a list of all available entity types with their corresponding schemas.

        Args:
            None

        Returns:
            str: JSON string containing a list of entities with their schemas.
        """
        import json
        
        # Get all entity types
        entity_types_json = user_session.knowledge_service.get_entity_types()
        entity_types = json.loads(entity_types_json)
        
        # Create result structure
        entities_with_schemas = []
        
        for entity_type in entity_types:
            # Get schema for each entity type
            schema_json = user_session.knowledge_service.get_entity_schema(entity_type)
            schema = json.loads(schema_json)
            
            # Add to result
            entities_with_schemas.append(schema)
        
        logger.info(f"Entities with schemas: {json.dumps(entities_with_schemas, indent=2)}")
        
        return json.dumps(entities_with_schemas)
    
    

    async def export_project_data(project_id: Annotated[str, "The ID of the project to export data from."]) -> str:
        """
        Export all project data.

        Args:
            project_id: The ID of the project to export data from.

        Returns:
            str: Path to the exported file
        """
        return user_session.knowledge_service.entity_service.export_graph(filename=project_id+".json", format='json')

    async def import_project_data(project_id: Annotated[str, "The ID of the project to import data to."]) -> str:
        """
        Import project data from a file, replacing current data.
        
        Args:
            project_id: The ID of the project to import data to.
            
        Returns:
            str: json representation of the project data
        """
        user_session.project_id = project_id
        user_session.knowledge_service.entity_service.import_graph(filename=project_id+".json", format='json')
        return project_id

    async def clear_project_data() -> str:
        """
        Clear all project data (entities and relationships). Use with caution!
        
        Args:
            None
            
        Returns:
            str: Confirmation message
        """
        user_session.knowledge_service.entity_service.clear_graph()
        return "All project data has been cleared"

    async def get_project_statistics() -> str:
        """
        Get detailed statistics about the current project data.
        
        Args:
            None
            
        Returns:
            str: JSON string containing detailed graph statistics
        """
        return user_session.knowledge_service.entity_service.get_graph_statistics()

    async def get_project_schema() -> str:
        """
        Get the schema of the current project data structure.
        
        Args:
            None
            
        Returns:
            str: JSON string containing the graph schema
        """
        return user_session.knowledge_service.entity_service.get_schema()

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
        description="Get a specific entity by ID. Returns JSON string representation of the entity."
    )

    #get_entity_with_relationships_tool = FunctionTool(
    #    get_entity_with_relationships,
    #    description="Get a specific entity by ID with all its relationships loaded. Returns JSON string representation with related entities."
    #)

    create_entity_tool = FunctionTool(
        create_entity,
        description="Create a new entity without providing an ID. The system will generate a UUID."
    )
    

    update_entity_tool = FunctionTool(
        update_entity,
        description="Update an existing entity by ID. Returns JSON string with success status."
    )

    delete_entity_tool = FunctionTool(
        delete_entity,
        description="Delete an entity by ID. Returns JSON string with success status."
    )

    #query_entities_tool = FunctionTool(
    #    query_entities,
    #    description="Query entities of a specific type with optional filters. Returns JSON string representation of matching entities."
    #)

    get_entity_types_tool = FunctionTool(
        get_entity_types,
        description="Get the list of entity types that describes the project data structure. Returns JSON string representation of the entity types."
    )
    
    get_entity_schema_tool = FunctionTool(
        get_entity_schema,
        description="Get entity schema of the specified entity type. Returns JSON schema of the entity."
    )

    get_all_entities_with_schemas_tool = FunctionTool(
        get_all_entities_with_schemas,
        description="Get a list of all available entity types with their corresponding schemas. Returns JSON string containing entities and their schemas. Entity type is defined in 'title', eg. {\"title\": \"Project\" } means the entity type is 'Project'.\n"
    )

    export_project_data_tool = FunctionTool(
        export_project_data,
        description="Export all project data in json format. Returns file path."
    )

    import_project_data_tool = FunctionTool(
        import_project_data,
        description="Import project data. Returns json representation of the project data."
    )

    clear_project_data_tool = FunctionTool(
        clear_project_data,
        description="Clear all project data (entities and relationships). Use with caution! Returns confirmation message."
    )

    get_project_statistics_tool = FunctionTool(
        get_project_statistics,
        description="Get detailed statistics about the current project data including nodes, edges, connectivity, and centrality measures. Returns JSON string."
    )

    get_project_schema_tool = FunctionTool(
        get_project_schema,
        description="Get the schema of the current project data structure including node types, edge types, and properties. Returns JSON string."
    )
    
    create_issue_tool = FunctionTool(
        create_issue,
        description="Create a new Issue entity. Returns JSON representation of the generated issue data."
    )

    create_edge_tool = FunctionTool(
        create_edge,
        description="Create a new Edge entity. Returns JSON representation of the generated edge data."
    )
    
    create_user_tool = FunctionTool(
        create_user,
        description="Create a new User entity. Returns JSON representation of the generated user data."
    )
    
    create_relationship_tool = FunctionTool(
        create_relationship,
        description="Create a new relationship between two entities. Returns JSON representation of the generated relationship data."
    )
    
    set_current_project_id_tool = FunctionTool(
        set_current_project_id,
        description="Set the ID of the current project. Returns project ID."
    )
    
    get_current_project_id_tool = FunctionTool(
        get_current_project_id,
        description="Get the ID of the current project. Returns project ID."
    )
    
    
    
    
    
    
    
    
    create_project_tool = FunctionTool(
        create_project,
        description="Create a new Project entity. Returns JSON representation of the generated project data."
    )

    return [        
        #get_current_session_id_tool,
        #get_session_project_context_tool,
        #get_full_project_context_tool,
        #get_entity_by_id_tool,
        #get_entity_with_relationships_tool,
        #create_entity_tool,
        # Specific create_entity tools for each data model class
        create_project_tool,
        create_issue_tool,
        create_relationship_tool,
        create_user_tool,
        #create_business_case_tool,
        #create_scope_tool,
        #create_requirement_tool,
        #create_epic_tool,
        #create_user_story_tool,
        #create_backlog_tool,
        #create_backlog_item_tool,
        #create_sprint_tool,
        #create_issue_tool,
        #create_team_tool,
        #create_risk_tool,
        #create_milestone_tool,
        #create_deliverable_tool,
        #create_change_request_tool,
        #create_baseline_tool,
        #create_test_case_tool,
        #create_phase_tool,
        #create_work_stream_tool,
        #create_documentation_tool,
        #create_repository_tool,
        #create_metric_tool,
        #create_person_tool,
        #create_communication_plan_tool,
        #create_ai_work_product_tool,
        #create_release_plan_tool,
        #create_knowledge_transfer_tool,
        #create_edge_tool,
        #update_entity_tool,
        #delete_entity_tool,
        #query_entities_tool,
        #get_entity_types_tool,
        #get_entity_schema_tool,
        #get_all_entities_with_schemas_tool,
        export_project_data_tool,
        import_project_data_tool,
        #set_current_project_id_tool,
        get_current_project_id_tool,
        #clear_project_data_tool,
        #get_project_statistics_tool,
        #get_project_schema_tool,
    ]