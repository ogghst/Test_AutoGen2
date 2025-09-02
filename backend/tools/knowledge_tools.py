from typing import Dict, List, Any, Optional, Annotated
from autogen_core.tools import FunctionTool
from knowledge.knowledge_service import KnowledgeService
from session import UserSession
from models.data_models import (
    Project, BusinessCase, Scope, Requirement, Epic, UserStory, Backlog, BacklogItem,
    Sprint, Issue, Team, Risk, Milestone, Deliverable, ChangeRequest, Baseline,
    TestCase, Phase, WorkStream, Documentation, Repository, Metric, Person,
    CommunicationPlan, AIWorkProduct, ReleasePlan, KnowledgeTransfer, Edge
)

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

    async def create_entity(entity_type: Annotated[str, "The type of the entity to create."], entity_data_json: Annotated[str, "The JSON string representation of the entity to create."]) -> str:
        """
        Create a new entity without providing an ID. The system will generate a UUID. This is the standard way to create a new entity.
        
        Args:
            entity_type: The type of the entity to create.
            entity_data_json: The JSON string representation of the entity to create.
            
        Returns:
            str: The JSON string representation of the created entity.
        """     
        return user_session.knowledge_service.create_entity(entity_type, entity_data_json)

    # Specific create_entity functions for each data model class
    async def create_project(project: Annotated[Project, "The Project object to create."]) -> str:
        """
        Create a new Project entity.
        
        Args:
            project: The Project object to create.
            
        Returns:
            str: The JSON string representation of the created Project entity.
        """
        return user_session.knowledge_service.create_entity("Project", project.model_dump_json())

    async def create_business_case(business_case: Annotated[BusinessCase, "The BusinessCase object to create."]) -> str:
        """
        Create a new BusinessCase entity.
        
        Args:
            business_case: The BusinessCase object to create.
            
        Returns:
            str: The JSON string representation of the created BusinessCase entity.
        """
        return user_session.knowledge_service.create_entity("BusinessCase", business_case.model_dump_json())

    async def create_scope(scope: Annotated[Scope, "The Scope object to create."]) -> str:
        """
        Create a new Scope entity.
        
        Args:
            scope: The Scope object to create.
            
        Returns:
            str: The JSON string representation of the created Scope entity.
        """
        return user_session.knowledge_service.create_entity("Scope", scope.model_dump_json())

    async def create_requirement(requirement: Annotated[Requirement, "The Requirement object to create."]) -> str:
        """
        Create a new Requirement entity.
        
        Args:
            requirement: The Requirement object to create.
            
        Returns:
            str: The JSON string representation of the created Requirement entity.
        """
        return user_session.knowledge_service.create_entity("Requirement", requirement.model_dump_json())

    async def create_epic(epic: Annotated[Epic, "The Epic object to create."]) -> str:
        """
        Create a new Epic entity.
        
        Args:
            epic: The Epic object to create.
            
        Returns:
            str: The JSON string representation of the created Epic entity.
        """
        return user_session.knowledge_service.create_entity("Epic", epic.model_dump_json())

    async def create_user_story(user_story: Annotated[UserStory, "The UserStory object to create."]) -> str:
        """
        Create a new UserStory entity.
        
        Args:
            user_story: The UserStory object to create.
            
        Returns:
            str: The JSON string representation of the created UserStory entity.
        """
        return user_session.knowledge_service.create_entity("UserStory", user_story.model_dump_json())

    async def create_backlog(backlog: Annotated[Backlog, "The Backlog object to create."]) -> str:
        """
        Create a new Backlog entity.
        
        Args:
            backlog: The Backlog object to create.
            
        Returns:
            str: The JSON string representation of the created Backlog entity.
        """
        return user_session.knowledge_service.create_entity("Backlog", backlog.model_dump_json())

    async def create_backlog_item(backlog_item: Annotated[BacklogItem, "The BacklogItem object to create."]) -> str:
        """
        Create a new BacklogItem entity.
        
        Args:
            backlog_item: The BacklogItem object to create.
            
        Returns:
            str: The JSON string representation of the created BacklogItem entity.
        """
        return user_session.knowledge_service.create_entity("BacklogItem", backlog_item.model_dump_json())

    async def create_sprint(sprint: Annotated[Sprint, "The Sprint object to create."]) -> str:
        """
        Create a new Sprint entity.
        
        Args:
            sprint: The Sprint object to create.
            
        Returns:
            str: The JSON string representation of the created Sprint entity.
        """
        return user_session.knowledge_service.create_entity("Sprint", sprint.model_dump_json())

    async def create_issue(issue: Annotated[Issue, "The Issue object to create."]) -> str:
        """
        Create a new Issue entity.
        
        Args:
            issue: The Issue object to create.
            
        Returns:
            str: The JSON string representation of the created Issue entity.
        """
        return user_session.knowledge_service.create_entity("Issue", issue.model_dump_json())

    async def create_team(team: Annotated[Team, "The Team object to create."]) -> str:
        """
        Create a new Team entity.
        
        Args:
            team: The Team object to create.
            
        Returns:
            str: The JSON string representation of the created Team entity.
        """
        return user_session.knowledge_service.create_entity("Team", team.model_dump_json())

    async def create_risk(risk: Annotated[Risk, "The Risk object to create."]) -> str:
        """
        Create a new Risk entity.
        
        Args:
            risk: The Risk object to create.
            
        Returns:
            str: The JSON string representation of the created Risk entity.
        """
        return user_session.knowledge_service.create_entity("Risk", risk.model_dump_json())

    async def create_milestone(milestone: Annotated[Milestone, "The Milestone object to create."]) -> str:
        """
        Create a new Milestone entity.
        
        Args:
            milestone: The Milestone object to create.
            
        Returns:
            str: The JSON string representation of the created Milestone entity.
        """
        return user_session.knowledge_service.create_entity("Milestone", milestone.model_dump_json())

    async def create_deliverable(deliverable: Annotated[Deliverable, "The Deliverable object to create."]) -> str:
        """
        Create a new Deliverable entity.
        
        Args:
            deliverable: The Deliverable object to create.
            
        Returns:
            str: The JSON string representation of the created Deliverable entity.
        """
        return user_session.knowledge_service.create_entity("Deliverable", deliverable.model_dump_json())

    async def create_change_request(change_request: Annotated[ChangeRequest, "The ChangeRequest object to create."]) -> str:
        """
        Create a new ChangeRequest entity.
        
        Args:
            change_request: The ChangeRequest object to create.
            
        Returns:
            str: The JSON string representation of the created ChangeRequest entity.
        """
        return user_session.knowledge_service.create_entity("ChangeRequest", change_request.model_dump_json())

    async def create_baseline(baseline: Annotated[Baseline, "The Baseline object to create."]) -> str:
        """
        Create a new Baseline entity.
        
        Args:
            baseline: The Baseline object to create.
            
        Returns:
            str: The JSON string representation of the created Baseline entity.
        """
        return user_session.knowledge_service.create_entity("Baseline", baseline.model_dump_json())

    async def create_test_case(test_case: Annotated[TestCase, "The TestCase object to create."]) -> str:
        """
        Create a new TestCase entity.
        
        Args:
            test_case: The TestCase object to create.
            
        Returns:
            str: The JSON string representation of the created TestCase entity.
        """
        return user_session.knowledge_service.create_entity("TestCase", test_case.model_dump_json())

    async def create_phase(phase: Annotated[Phase, "The Phase object to create."]) -> str:
        """
        Create a new Phase entity.
        
        Args:
            phase: The Phase object to create.
            
        Returns:
            str: The JSON string representation of the created Phase entity.
        """
        return user_session.knowledge_service.create_entity("Phase", phase.model_dump_json())

    async def create_work_stream(work_stream: Annotated[WorkStream, "The WorkStream object to create."]) -> str:
        """
        Create a new WorkStream entity.
        
        Args:
            work_stream: The WorkStream object to create.
            
        Returns:
            str: The JSON string representation of the created WorkStream entity.
        """
        return user_session.knowledge_service.create_entity("WorkStream", work_stream.model_dump_json())

    async def create_documentation(documentation: Annotated[Documentation, "The Documentation object to create."]) -> str:
        """
        Create a new Documentation entity.
        
        Args:
            documentation: The Documentation object to create.
            
        Returns:
            str: The JSON string representation of the created Documentation entity.
        """
        return user_session.knowledge_service.create_entity("Documentation", documentation.model_dump_json())

    async def create_repository(repository: Annotated[Repository, "The Repository object to create."]) -> str:
        """
        Create a new Repository entity.
        
        Args:
            repository: The Repository object to create.
            
        Returns:
            str: The JSON string representation of the created Repository entity.
        """
        return user_session.knowledge_service.create_entity("Repository", repository.model_dump_json())

    async def create_metric(metric: Annotated[Metric, "The Metric object to create."]) -> str:
        """
        Create a new Metric entity.
        
        Args:
            metric: The Metric object to create.
            
        Returns:
            str: The JSON string representation of the created Metric entity.
        """
        return user_session.knowledge_service.create_entity("Metric", metric.model_dump_json())

    async def create_person(person: Annotated[Person, "The Person object to create."]) -> str:
        """
        Create a new Person entity.
        
        Args:
            person: The Person object to create.
            
        Returns:
            str: The JSON string representation of the created Person entity.
        """
        return user_session.knowledge_service.create_entity("Person", person.model_dump_json())

    async def create_communication_plan(communication_plan: Annotated[CommunicationPlan, "The CommunicationPlan object to create."]) -> str:
        """
        Create a new CommunicationPlan entity.
        
        Args:
            communication_plan: The CommunicationPlan object to create.
            
        Returns:
            str: The JSON string representation of the created CommunicationPlan entity.
        """
        return user_session.knowledge_service.create_entity("CommunicationPlan", communication_plan.model_dump_json())

    async def create_ai_work_product(ai_work_product: Annotated[AIWorkProduct, "The AIWorkProduct object to create."]) -> str:
        """
        Create a new AIWorkProduct entity.
        
        Args:
            ai_work_product: The AIWorkProduct object to create.
            
        Returns:
            str: The JSON string representation of the created AIWorkProduct entity.
        """
        return user_session.knowledge_service.create_entity("AIWorkProduct", ai_work_product.model_dump_json())

    async def create_release_plan(release_plan: Annotated[ReleasePlan, "The ReleasePlan object to create."]) -> str:
        """
        Create a new ReleasePlan entity.
        
        Args:
            release_plan: The ReleasePlan object to create.
            
        Returns:
            str: The JSON string representation of the created ReleasePlan entity.
        """
        return user_session.knowledge_service.create_entity("ReleasePlan", release_plan.model_dump_json())

    async def create_knowledge_transfer(knowledge_transfer: Annotated[KnowledgeTransfer, "The KnowledgeTransfer object to create."]) -> str:
        """
        Create a new KnowledgeTransfer entity.
        
        Args:
            knowledge_transfer: The KnowledgeTransfer object to create.
            
        Returns:
            str: The JSON string representation of the created KnowledgeTransfer entity.
        """
        return user_session.knowledge_service.create_entity("KnowledgeTransfer", knowledge_transfer.model_dump_json())

    async def create_edge(edge: Annotated[Edge, "The Edge object to create."]) -> str:
        """
        Create a new Edge entity.
        
        Args:
            edge: The Edge object to create.
            
        Returns:
            str: The JSON string representation of the created Edge entity.
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

    async def export_project_data(format: Annotated[str, "Export format: 'graphml', 'json', 'gexf', or 'gml'."] ="json", filename: Annotated[str, "Optional custom filename for the export."] = "knowledge_base/project_data.json") -> str:
        """
        Export all project data in various formats for backup or external use.
        
        Args:
            format: Export format ('graphml', 'json', 'gexf', 'gml'). Default is 'json'.
            filename: Optional custom filename for the export. Default is 'knowledge_base/project_data.json'.
            
        Returns:
            str: Path to the exported file
        """
        return user_session.knowledge_service.entity_service.export_graph(format, filename)

    async def import_project_data(file_path: Annotated[str, "Path to the file to import."], format: Annotated[str, "File format: 'graphml', 'json', 'gexf', 'gml', or 'auto'."] = "knowledge_base/project_data.json") -> str:
        """
        Import project data from a file, replacing current data.
        
        Args:
            file_path: Path to the file to import. Default is 'knowledge_base/project_data.json'.
            format: File format ('graphml', 'json', 'gexf', 'gml', 'auto'). Default is 'json'.
            
        Returns:
            str: Success message with import details
        """
        user_session.knowledge_service.entity_service.import_graph(file_path, format)
        return f"Successfully imported project data from {file_path} in {format} format"

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

    #create_entity_tool = FunctionTool(
    #    create_entity,
    #    description="Create a new entity without providing an ID. The system will generate a UUID. Returns JSON string with the generated ID."
    #)
    #)

    # Specific create_entity tools for each data model class
    create_project_tool = FunctionTool(
        create_project,
        description="Create a new Project entity. Returns JSON string with the generated ID."
    )

    create_business_case_tool = FunctionTool(
        create_business_case,
        description="Create a new BusinessCase entity. Returns JSON string with the generated ID."
    )

    create_scope_tool = FunctionTool(
        create_scope,
        description="Create a new Scope entity. Returns JSON string with the generated ID."
    )

    create_requirement_tool = FunctionTool(
        create_requirement,
        description="Create a new Requirement entity. Returns JSON string with the generated ID."
    )

    create_epic_tool = FunctionTool(
        create_epic,
        description="Create a new Epic entity. Returns JSON string with the generated ID."
    )

    create_user_story_tool = FunctionTool(
        create_user_story,
        description="Create a new UserStory entity. Returns JSON string with the generated ID."
    )

    create_backlog_tool = FunctionTool(
        create_backlog,
        description="Create a new Backlog entity. Returns JSON string with the generated ID."
    )

    create_backlog_item_tool = FunctionTool(
        create_backlog_item,
        description="Create a new BacklogItem entity. Returns JSON string with the generated ID."
    )

    create_sprint_tool = FunctionTool(
        create_sprint,
        description="Create a new Sprint entity. Returns JSON string with the generated ID."
    )

    create_issue_tool = FunctionTool(
        create_issue,
        description="Create a new Issue entity. Returns JSON string with the generated ID."
    )

    create_team_tool = FunctionTool(
        create_team,
        description="Create a new Team entity. Returns JSON string with the generated ID."
    )

    create_risk_tool = FunctionTool(
        create_risk,
        description="Create a new Risk entity. Returns JSON string with the generated ID."
    )

    create_milestone_tool = FunctionTool(
        create_milestone,
        description="Create a new Milestone entity. Returns JSON string with the generated ID."
    )

    create_deliverable_tool = FunctionTool(
        create_deliverable,
        description="Create a new Deliverable entity. Returns JSON string with the generated ID."
    )

    create_change_request_tool = FunctionTool(
        create_change_request,
        description="Create a new ChangeRequest entity. Returns JSON string with the generated ID."
    )

    create_baseline_tool = FunctionTool(
        create_baseline,
        description="Create a new Baseline entity. Returns JSON string with the generated ID."
    )

    create_test_case_tool = FunctionTool(
        create_test_case,
        description="Create a new TestCase entity. Returns JSON string with the generated ID."
    )

    create_phase_tool = FunctionTool(
        create_phase,
        description="Create a new Phase entity. Returns JSON string with the generated ID."
    )

    create_work_stream_tool = FunctionTool(
        create_work_stream,
        description="Create a new WorkStream entity. Returns JSON string with the generated ID."
    )

    create_documentation_tool = FunctionTool(
        create_documentation,
        description="Create a new Documentation entity. Returns JSON string with the generated ID."
    )

    create_repository_tool = FunctionTool(
        create_repository,
        description="Create a new Repository entity. Returns JSON string with the generated ID."
    )

    create_metric_tool = FunctionTool(
        create_metric,
        description="Create a new Metric entity. Returns JSON string with the generated ID."
    )

    create_person_tool = FunctionTool(
        create_person,
        description="Create a new Person entity. Returns JSON string with the generated ID."
    )

    create_communication_plan_tool = FunctionTool(
        create_communication_plan,
        description="Create a new CommunicationPlan entity. Returns JSON string with the generated ID."
    )

    create_ai_work_product_tool = FunctionTool(
        create_ai_work_product,
        description="Create a new AIWorkProduct entity. Returns JSON string with the generated ID."
    )

    create_release_plan_tool = FunctionTool(
        create_release_plan,
        description="Create a new ReleasePlan entity. Returns JSON string with the generated ID."
    )

    create_knowledge_transfer_tool = FunctionTool(
        create_knowledge_transfer,
        description="Create a new KnowledgeTransfer entity. Returns JSON string with the generated ID."
    )

    create_edge_tool = FunctionTool(
        create_edge,
        description="Create a new Edge entity. Returns JSON string with the generated ID."
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

    export_project_data_tool = FunctionTool(
        export_project_data,
        description="Export all project data in various formats (graphml, json, gexf, gml) for backup or external use. Returns file path."
    )

    import_project_data_tool = FunctionTool(
        import_project_data,
        description="Import project data from a file, replacing current data. Supports multiple formats. Returns success message."
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

    return [        
        get_current_session_id_tool,
        get_session_project_context_tool,
        get_full_project_context_tool,
        get_entity_by_id_tool,
        #get_entity_with_relationships_tool,
        #create_entity_tool,
        # Specific create_entity tools for each data model class
        create_project_tool,
        create_business_case_tool,
        create_scope_tool,
        create_requirement_tool,
        create_epic_tool,
        create_user_story_tool,
        create_backlog_tool,
        create_backlog_item_tool,
        create_sprint_tool,
        create_issue_tool,
        create_team_tool,
        create_risk_tool,
        create_milestone_tool,
        create_deliverable_tool,
        create_change_request_tool,
        create_baseline_tool,
        create_test_case_tool,
        create_phase_tool,
        create_work_stream_tool,
        create_documentation_tool,
        create_repository_tool,
        create_metric_tool,
        create_person_tool,
        create_communication_plan_tool,
        create_ai_work_product_tool,
        create_release_plan_tool,
        create_knowledge_transfer_tool,
        create_edge_tool,
        update_entity_tool,
        delete_entity_tool,
        #query_entities_tool,
        get_entity_types_tool,
        get_entity_schema_tool,
        export_project_data_tool,
        import_project_data_tool,
        clear_project_data_tool,
        get_project_statistics_tool,
        get_project_schema_tool,
    ]