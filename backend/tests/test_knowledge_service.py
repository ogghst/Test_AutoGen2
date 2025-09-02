"""
Test suite for KnowledgeService.

This test suite performs comprehensive testing of the KnowledgeService class,
including all CRUD operations, entity management, and relationship handling.

The KnowledgeService is a wrapper around EntityService that provides the expected
interface for the knowledge tools and other parts of the system.

Test Coverage:
- Service initialization
- Entity type management
- CRUD operations (Create, Read, Update, Delete)
- Entity relationships and subgraphs
- Query operations with filters
- Entity persistence
- Error handling
- Performance testing

Usage:
    # Run all knowledge service tests
    python -m pytest tests/test_knowledge_service.py -v
    
    # Run only unit tests
    python -m pytest tests/test_knowledge_service.py -m unit -v
    
    # Run only performance tests
    python -m pytest tests/test_knowledge_service.py -m performance -v
    
    # Run with test runner
    python tests/run_tests.py -c knowledge_service
"""

import json
import tempfile
import shutil
import uuid
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any

import pytest

# Import the KnowledgeService and data models
from knowledge.knowledge_service import KnowledgeService
from models.data_models import (
    Project, Epic, UserStory, Issue, Risk, Milestone, Deliverable,
    Team, Person, Stakeholder, Requirement, Backlog, Sprint,
    ChangeRequest, Baseline, TestCase, Phase, WorkStream,
    Documentation, Repository, Metric, CommunicationPlan, AIWorkProduct,
    Scope, TeamMember, BusinessCase, BacklogItem,
    MethodologyEnum, SDLCPhaseEnum, ProjectStatusEnum, PriorityEnum,
    EpicStatusEnum, UserStoryStatusEnum, IssueTypeEnum, IssueStatusEnum,
    SeverityEnum, RoleEnum, InfluenceLevelEnum, InterestLevelEnum,
    RiskCategoryEnum, RiskStatusEnum, MilestoneStatusEnum, DeliverableStatusEnum,
    ChangeTypeEnum, ApprovalStatusEnum, TestTypeEnum, AgileArtifactStatusEnum,
    DocumentationTypeEnum, RepositoryTypeEnum, StoryPointsEnum
)


@pytest.mark.unit
@pytest.mark.knowledge_base
class TestKnowledgeService:
    """Test suite for KnowledgeService with comprehensive testing."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test storage
        self.temp_dir = tempfile.mkdtemp(prefix="test_knowledge_service_")
        self.storage_path = Path(self.temp_dir) / "knowledge_base"
        self.service = KnowledgeService(str(self.storage_path))
        
        # Test data containers
        self.test_entities = {}
        self.test_entity_ids = {}
        
        # Create test entities for use in tests
        self._create_test_entities()
    
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary directory
        if self.temp_dir and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_test_entities(self):
        """Create test entities for use in tests."""
        # Generate UUIDs for all entities
        project_id = str(uuid.uuid4())
        epic_id = str(uuid.uuid4())
        user_story_id = str(uuid.uuid4())
        issue_id = str(uuid.uuid4())
        test_case_id = str(uuid.uuid4())
        milestone_id = str(uuid.uuid4())
        deliverable_id = str(uuid.uuid4())
        risk_id = str(uuid.uuid4())
        requirement_id = str(uuid.uuid4())
        
        # Helper function to convert dates to strings for JSON serialization
        def convert_dates_to_strings(data):
            if isinstance(data, dict):
                return {k: convert_dates_to_strings(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [convert_dates_to_strings(item) for item in data]
            elif isinstance(data, datetime):
                return data.isoformat()
            elif isinstance(data, date):
                return data.isoformat()
            else:
                return data
        
        # Create a simple project
        project = Project(
            id=project_id,
            name="Test Project",
            vision="A test project for validation",
            methodology=MethodologyEnum.Hybrid,
            description="Test project description",
            business_case="Testing purposes",
            sdlc_phase=SDLCPhaseEnum.Inception,
            release_plan="Phase 1: Testing",
            team="test-team",
            scope=Scope(
                epics=[epic_id],
                inclusions=["Core functionality", "User management"],
                exclusions=["Third-party integrations"],
                assumptions=["Stable requirements", "Adequate resources"],
                constraints=["Budget limit", "Timeline constraint"],
                acceptance_criteria=["All features work", "Performance requirements met"],
                requirements=[requirement_id]
            ),
            stakeholders=[],
            risks=[risk_id],
            milestones=[milestone_id],
            phases=[],
            status=ProjectStatusEnum.Planning,
            knowledge_transfer="Documentation",
            change_requests=[],
            baselines=[],
            repositories=[],
            ai_work_products=[]
        )
        
        # Create an epic
        epic = Epic(
            id=epic_id,
            name="Test Epic",
            description="A test epic for validation",
            status=EpicStatusEnum.Proposed,
            priority=PriorityEnum.High,
            business_value=8,
            user_stories=[user_story_id],
            target_release="v1.0"
        )
        
        # Create a user story
        user_story = UserStory(
            id=user_story_id,
            title="Test User Story",
            description="A test user story for validation",
            acceptance_criteria=["Criterion 1", "Criterion 2"],
            story_points="5",
            priority=PriorityEnum.High,
            status="To Do",
            epic_id=epic_id,
            issues=[issue_id],
            definition_of_done="All acceptance criteria met",
            technical_notes="Test technical notes"
        )
        
        # Create an issue
        issue = Issue(
            id=issue_id,
            title="Test Issue",
            description="A test issue for validation",
            type=IssueTypeEnum.Bug,
            status="To Do",
            severity=SeverityEnum.Medium,
            assignee="test-user",
            estimate_hours=4.0,
            due_date=datetime.now().date(),
            root_cause="Test root cause",
            resolution="Test resolution"
        )
        
        # Create a risk
        risk = Risk(
            id=risk_id,
            description="A test risk for validation",
            category=RiskCategoryEnum.Technical,
            probability=InfluenceLevelEnum.Medium,
            impact=InfluenceLevelEnum.High,
            status=RiskStatusEnum.Identified,
            mitigation_strategy="Test mitigation",
            contingency_plan="Test contingency",
            owner="test-owner",
            triggers=["Resource shortage", "Technical complexity"]
        )
        
        # Create a milestone
        milestone = Milestone(
            id=milestone_id,
            name="Test Milestone",
            description="A test milestone for validation",
            target_date=datetime.now().date(),
            status=MilestoneStatusEnum.Planned,
            deliverables=[deliverable_id],
            acceptance_criteria=["Criterion 1"]
        )
        
        # Create a deliverable
        deliverable = Deliverable(
            id=deliverable_id,
            name="Test Deliverable",
            description="A test deliverable for validation",
            status="In Progress",
            acceptance_date=datetime.now().date(),
            quality_metrics="Test quality metrics",
            storage_location="Test storage location",
            version="1.0"
        )
        
        # Create a test case
        test_case = TestCase(
            id=test_case_id,
            name="Test Case",
            description="A test case for validation",
            test_steps=["Step 1", "Step 2"],
            expected_result="Expected result",
            actual_result="Not yet tested",
            status="Not Started",
            type=TestTypeEnum.Unit,
            priority=PriorityEnum.Medium,
            associated_requirement=requirement_id,
            automated=False,
            last_tested=datetime.now().date()
        )
        
        # Store all entities for testing (convert dates to strings for JSON serialization)
        # Remove IDs so new ones are generated for each test
        project_data = convert_dates_to_strings(project.model_dump())
        del project_data['id']
        
        epic_data = convert_dates_to_strings(epic.model_dump())
        del epic_data['id']
        
        user_story_data = convert_dates_to_strings(user_story.model_dump())
        del user_story_data['id']
        
        issue_data = convert_dates_to_strings(issue.model_dump())
        del issue_data['id']
        
        risk_data = convert_dates_to_strings(risk.model_dump())
        del risk_data['id']
        
        milestone_data = convert_dates_to_strings(milestone.model_dump())
        del milestone_data['id']
        
        deliverable_data = convert_dates_to_strings(deliverable.model_dump())
        del deliverable_data['id']
        
        test_case_data = convert_dates_to_strings(test_case.model_dump())
        del test_case_data['id']
        
        self.test_entities = {
            "project": project_data,
            "epic": epic_data,
            "user_story": user_story_data,
            "issue": issue_data,
            "risk": risk_data,
            "milestone": milestone_data,
            "deliverable": deliverable_data,
            "test_case": test_case_data
        }
        
        # Store entity IDs for reference
        self.test_entity_ids = {
            "project_id": project_id,
            "epic_id": epic_id,
            "user_story_id": user_story_id,
            "issue_id": issue_id,
            "test_case_id": test_case_id,
            "milestone_id": milestone_id,
            "deliverable_id": deliverable_id,
            "risk_id": risk_id,
            "requirement_id": requirement_id
        }
    
    def test_service_initialization(self):
        """Test that the service initializes correctly."""
        assert self.service is not None
        assert hasattr(self.service, 'entity_service')
        assert self.service.entity_service is not None
    
    def test_get_entity_types(self):
        """Test getting entity types from the service."""
        entity_types_json = self.service.get_entity_types()
        entity_types = json.loads(entity_types_json)
        
        assert isinstance(entity_types, list)
        assert len(entity_types) > 0
        
        # Check that we have the expected entity types
        expected_types = ["project", "epic", "userstory", "issue", "risk", "milestone", "deliverable"]
        for expected_type in expected_types:
            assert expected_type in entity_types
    
    def test_create_entity(self):
        """Test creating a new entity."""
        # Create test data
        project_data = self.test_entities["project"]
        
        # Test creating a project
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        create_data = json.loads(create_result)
        
        # Verify the entity was created
        assert "id" in create_data
        assert create_data["name"] == "Test Project"
        assert create_data["__type__"] == "Project"
        
        # Store the created ID for later tests
        self.test_entity_ids["created_project_id"] = create_data["id"]
    
    def test_get_entity_by_id(self):
        """Test retrieving an entity by ID."""
        # First create an entity
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Test retrieving the entity
        retrieve_result = self.service.get_entity_by_id("Project", project_id)
        retrieve_data = json.loads(retrieve_result)
        
        assert retrieve_data["id"] == project_id
        assert retrieve_data["name"] == "Test Project"
        assert retrieve_data["__type__"] == "Project"
    
    def test_get_entity_by_id_with_relationships(self):
        """Test retrieving an entity with relationships."""
        # First create an entity
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Test retrieving the entity with relationships
        retrieve_result = self.service.get_entity_by_id("Project", project_id, include_relationships=True)
        retrieve_data = json.loads(retrieve_result)
        
        # Should return a subgraph structure
        assert "central_entity_id" in retrieve_data
        assert "nodes" in retrieve_data
        assert "edges" in retrieve_data
        assert retrieve_data["central_entity_id"] == project_id
    
    def test_get_entity_by_id_not_found(self):
        """Test retrieving a non-existent entity."""
        non_existent_id = str(uuid.uuid4())
        retrieve_result = self.service.get_entity_by_id("Project", non_existent_id)
        retrieve_data = json.loads(retrieve_result)
        
        assert "error" in retrieve_data
        assert non_existent_id in retrieve_data["error"]
    
    def test_update_entity(self):
        """Test updating an existing entity."""
        # First create an entity
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Update the entity
        updates = {"name": "Updated Project Name", "description": "Updated description"}
        update_result = self.service.update_entity("Project", project_id, json.dumps(updates))
        update_data = json.loads(update_result)
        
        assert update_data["id"] == project_id
        assert update_data["name"] == "Updated Project Name"
        assert update_data["description"] == "Updated description"
    
    def test_update_entity_not_found(self):
        """Test updating a non-existent entity."""
        non_existent_id = str(uuid.uuid4())
        updates = {"name": "Updated Name"}
        update_result = self.service.update_entity("Project", non_existent_id, json.dumps(updates))
        update_data = json.loads(update_result)
        
        assert "error" in update_data
        assert non_existent_id in update_data["error"]
    
    def test_delete_entity(self):
        """Test deleting an entity."""
        # First create an entity
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Delete the entity
        delete_result = self.service.delete_entity("Project", project_id)
        delete_data = json.loads(delete_result)
        
        assert delete_data["success"] is True
        assert delete_data["entity_id"] == project_id
        
        # Verify the entity is deleted
        retrieve_result = self.service.get_entity_by_id("Project", project_id)
        retrieve_data = json.loads(retrieve_result)
        assert "error" in retrieve_data
    
    def test_delete_entity_not_found(self):
        """Test deleting a non-existent entity."""
        non_existent_id = str(uuid.uuid4())
        delete_result = self.service.delete_entity("Project", non_existent_id)
        delete_data = json.loads(delete_result)
        
        assert delete_data["success"] is False
        assert delete_data["entity_id"] == non_existent_id
    
    def test_query_entities_no_filters(self):
        """Test querying entities without filters."""
        # Create multiple entities
        for i in range(3):
            project_data = self.test_entities["project"].copy()
            project_data["name"] = f"Test Project {i+1}"
            self.service.create_entity("Project", json.dumps(project_data))
        
        # Query all projects
        results = self.service.query_entities("Project", "{}")
        results_data = json.loads(results)
        
        assert len(results_data) >= 3
        for result in results_data:
            assert result["__type__"] == "Project"
    
    def test_query_entities_with_filters(self):
        """Test querying entities with filters."""
        # Create multiple entities with different names
        for i in range(3):
            project_data = self.test_entities["project"].copy()
            project_data["name"] = f"Test Project {i+1}"
            project_data["status"] = "Planning" if i == 0 else "Execution"
            self.service.create_entity("Project", json.dumps(project_data))
        
        # Query for planning status projects
        filters = {"status": "Planning"}
        results = self.service.query_entities("Project", json.dumps(filters))
        results_data = json.loads(results)
        
        assert len(results_data) >= 1
        for result in results_data:
            assert result["status"] == "Planning"
    
    def test_get_full_project_context(self):
        """Test getting full project context."""
        # Create a project
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Get full project context
        context_result = self.service.get_full_project_context(project_id)
        context_data = json.loads(context_result)
        
        # Should return a subgraph structure
        assert "central_entity_id" in context_data
        assert "nodes" in context_data
        assert "edges" in context_data
        assert context_data["central_entity_id"] == project_id
    
    def test_get_full_project_context_not_found(self):
        """Test getting full project context for non-existent project."""
        non_existent_id = str(uuid.uuid4())
        context_result = self.service.get_full_project_context(non_existent_id)
        context_data = json.loads(context_result)
        
        assert "error" in context_data
        assert non_existent_id in context_data["error"]
    
    def test_get_entity_schema(self):
        """Test getting entity schema."""
        schema_result = self.service.get_entity_schema("Project")
        schema_data = json.loads(schema_result)
        
        assert "entity_type" in schema_data
        assert "model_name" in schema_data
        assert "properties" in schema_data
        assert "required_fields" in schema_data
        assert schema_data["entity_type"] == "Project"
        assert schema_data["model_name"] == "Project"
    
    def test_get_entity_schema_invalid_type(self):
        """Test getting schema for invalid entity type."""
        with pytest.raises(ValueError, match="Unknown entity type"):
            self.service.get_entity_schema("InvalidType")
    
    def test_create_entity_with_invalid_json(self):
        """Test creating entity with invalid JSON."""
        invalid_json = "{ invalid json }"
        result = self.service.create_entity("Project", invalid_json)
        result_data = json.loads(result)
        
        assert "error" in result_data
        assert "Invalid JSON format" in result_data["error"]
    
    def test_create_entity_with_invalid_type(self):
        """Test creating entity with invalid type."""
        project_data = self.test_entities["project"]
        
        with pytest.raises(ValueError, match="Unknown entity type"):
            self.service.create_entity("InvalidType", json.dumps(project_data))
    
    def test_entity_persistence(self):
        """Test that entities are properly persisted to storage."""
        # Create an entity
        project_data = self.test_entities["project"]
        create_result = self.service.create_entity("Project", json.dumps(project_data))
        project_id = json.loads(create_result)["id"]
        
        # Create a new service instance to test persistence
        new_service = KnowledgeService(str(self.storage_path))
        
        # Retrieve the entity
        retrieve_result = new_service.get_entity_by_id("Project", project_id)
        retrieve_data = json.loads(retrieve_result)
        
        assert retrieve_data["id"] == project_id
        assert retrieve_data["name"] == "Test Project"
    
    def test_multiple_entity_types(self):
        """Test creating and retrieving multiple entity types."""
        # Create different types of entities
        entity_types = ["Project", "Epic", "UserStory", "Issue", "Risk"]
        created_ids = {}
        
        for entity_type in entity_types:
            # Map entity type to test entity key
            entity_key = entity_type.lower().replace("_", "_")
            if entity_type == "UserStory":
                entity_key = "user_story"
            elif entity_type == "Project":
                entity_key = "project"
            elif entity_type == "Epic":
                entity_key = "epic"
            elif entity_type == "Issue":
                entity_key = "issue"
            elif entity_type == "Risk":
                entity_key = "risk"
            
            entity_data = self.test_entities[entity_key]
            create_result = self.service.create_entity(entity_type, json.dumps(entity_data))
            entity_id = json.loads(create_result)["id"]
            created_ids[entity_type] = entity_id
        
        # Verify all entities were created and can be retrieved
        for entity_type, entity_id in created_ids.items():
            retrieve_result = self.service.get_entity_by_id(entity_type, entity_id)
            retrieve_data = json.loads(retrieve_result)
            assert retrieve_data["id"] == entity_id
            assert retrieve_data["__type__"] == entity_type
    
    def test_entity_type_tracking(self):
        """Test that entity types are properly tracked."""
        # Create entities of different types
        project_data = self.test_entities["project"]
        epic_data = self.test_entities["epic"]
        
        self.service.create_entity("Project", json.dumps(project_data))
        self.service.create_entity("Epic", json.dumps(epic_data))
        
        # Query for each type
        projects = self.service.query_entities("Project", "{}")
        epics = self.service.query_entities("Epic", "{}")
        
        projects_data = json.loads(projects)
        epics_data = json.loads(epics)
        
        # Verify type filtering works
        for project in projects_data:
            assert project["__type__"] == "Project"
        
        for epic in epics_data:
            assert epic["__type__"] == "Epic"
    
    @pytest.mark.performance
    def test_performance_with_multiple_entities(self):
        """Test performance with multiple entities."""
        import time
        
        # Create many entities
        start_time = time.time()
        for i in range(100):
            project_data = self.test_entities["project"].copy()
            project_data["name"] = f"Performance Test Project {i}"
            self.service.create_entity("Project", json.dumps(project_data))
        
        creation_time = time.time() - start_time
        
        # Query all entities
        start_time = time.time()
        results = self.service.query_entities("Project", "{}")
        query_time = time.time() - start_time
        
        results_data = json.loads(results)
        
        # Verify performance is reasonable (less than 5 seconds for 100 entities)
        assert creation_time < 5.0, f"Creation took {creation_time:.2f}s, expected < 5.0s"
        assert query_time < 2.0, f"Query took {query_time:.2f}s, expected < 2.0s"
        assert len(results_data) >= 100


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
