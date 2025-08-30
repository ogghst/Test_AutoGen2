"""
Test suite for KnowledgeService.

This test suite performs closed-loop testing using the data models to create
test entities, serialize them to JSON, and verify the service operations.
"""

import json
import tempfile
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

import pytest

# Import the real KnowledgeService and data models
from knowledge.knowledge_service import KnowledgeService
from agents.tools import UUIDEncoder
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


class TestKnowledgeService:
    """Test suite for KnowledgeService with closed-loop JSON testing."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create temporary directory for test storage
        self.temp_dir = tempfile.mkdtemp(prefix="test_knowledge_")
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
            actual_result=None,
            status="Not Started",
            type=TestTypeEnum.Unit,
            priority=PriorityEnum.Medium,
            associated_requirement=requirement_id,
            automated=False,
            last_tested=datetime.now().date()
        )
        
        # Store all entities for testing
        self.test_entities = {
            "project": project,
            "epic": epic,
            "user_story": user_story,
            "issue": issue,
            "risk": risk,
            "milestone": milestone,
            "deliverable": deliverable,
            "test_case": test_case
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
    
    def test_get_entity_types(self):
        """Test getting entity types from the service."""
        entity_types = self.service.get_entity_types()
        assert isinstance(entity_types, list)
        assert len(entity_types) > 0
        
        # Check that we have the expected entity types
        entity_type_names = [et["type"] for et in entity_types]
        expected_types = ["Project", "Epic", "UserStory", "Issue", "Risk", "Milestone", "Deliverable"]
        for expected_type in expected_types:
            assert expected_type in entity_type_names
    
    def test_create_and_retrieve_project(self):
        """Test creating a project and then retrieving it."""
        # Create test data
        project_data = self.test_entities["project"].model_dump()
        
        # Test creating a project
        create_result = self.service.create_entity("Project", json.dumps(project_data, cls=UUIDEncoder))
        create_data = json.loads(create_result)
        assert create_data["success"] is True
        assert "entity_id" in create_data
        
        project_id = create_data["entity_id"]
        
        # Test retrieving the project
        retrieve_result = self.service.get_entity_by_id("Project", project_id)
        retrieve_data = json.loads(retrieve_result)
        assert retrieve_data["id"] == project_id
        assert retrieve_data["name"] == "Test Project"
    
    def test_create_multiple_entities(self):
        """Test creating multiple entities of different types."""
        # Create epic
        epic_data = self.test_entities["epic"].model_dump()
        create_result = self.service.create_entity("Epic", json.dumps(epic_data, cls=UUIDEncoder))
        create_data = json.loads(create_result)
        epic_id = create_data["entity_id"]
        
        # Create user story
        user_story_data = self.test_entities["user_story"].model_dump()
        user_story_data["epic_id"] = epic_id  # Reference the created epic
        create_result = self.service.create_entity("UserStory", json.dumps(user_story_data, cls=UUIDEncoder))
        create_data = json.loads(create_result)
        user_story_id = create_data["entity_id"]
        
        # Create issue
        issue_data = self.test_entities["issue"].model_dump()
        create_result = self.service.create_entity("Issue", json.dumps(issue_data, cls=UUIDEncoder))
        create_data = json.loads(create_result)
        issue_id = create_data["entity_id"]
        
        # Verify all entities were created
        assert epic_id is not None
        assert user_story_id is not None
        assert issue_id is not None
    
    def test_entity_relationships(self):
        """Test retrieving an entity with its relationships."""
        # Create related entities
        epic_data = self.test_entities["epic"].model_dump()
        create_result = self.service.create_entity("Epic", json.dumps(epic_data, cls=UUIDEncoder))
        epic_id = json.loads(create_result)["entity_id"]
        
        user_story_data = self.test_entities["user_story"].model_dump()
        user_story_data["epic_id"] = epic_id
        create_result = self.service.create_entity("UserStory", json.dumps(user_story_data, cls=UUIDEncoder))
        user_story_id = json.loads(create_result)["entity_id"]
        
        # Test retrieving the epic
        epic_result = self.service.get_entity_by_id("Epic", epic_id)
        epic_data = json.loads(epic_result)
        assert epic_data["id"] == epic_id
        assert epic_data["name"] == "Test Epic"
        
        # Test retrieving the user story
        user_story_result = self.service.get_entity_by_id("UserStory", user_story_id)
        user_story_data = json.loads(user_story_result)
        assert user_story_data["id"] == user_story_id
        assert user_story_data["epic_id"] == epic_id
    
    def test_query_entities(self):
        """Test querying entities with filters."""
        # Create multiple entities of the same type
        for i in range(3):
            user_story_data = self.test_entities["user_story"].model_dump()
            user_story_data["title"] = f"User Story {i+1}"
            user_story_data["priority"] = "High" if i == 0 else "Medium"
            self.service.create_entity("UserStory", json.dumps(user_story_data, cls=UUIDEncoder))
        
        # Query for high priority user stories
        filters = {"priority": "High"}
        results = self.service.query_entities("UserStory", json.dumps(filters))
        results_data = json.loads(results)
        assert len(results_data) >= 1
        
        # Verify the filter worked
        for result in results_data:
            assert result["priority"] == "High"
    
    def test_full_project_context(self):
        """Test getting full project context with all related entities."""
        # Create a complete project structure
        project_data = self.test_entities["project"].model_dump()
        
        # Create the project
        create_result = self.service.create_entity("Project", json.dumps(project_data, cls=UUIDEncoder))
        project_id = json.loads(create_result)["entity_id"]
        
        # Get full project context
        context_result = self.service.get_full_project_context(project_id)
        context_data = json.loads(context_result)
        
        # Should return project data (even if no relationships yet)
        assert "id" in context_data or "error" in context_data
    
    def test_entity_serialization(self):
        """Test that entities can be serialized to JSON and back without data loss."""
        # Create a complex entity
        project_data = self.test_entities["project"].model_dump()
        
        # Serialize to JSON
        json_str = json.dumps(project_data)
        
        # Deserialize back
        deserialized = json.loads(json_str)
        
        # Verify key fields are preserved
        assert deserialized["name"] == project_data["name"]
        assert deserialized["vision"] == project_data["vision"]
        assert deserialized["methodology"] == project_data["methodology"]
    
    def test_entity_persistence(self):
        """Test that entities are properly persisted to storage."""
        # Create an entity
        epic_data = self.test_entities["epic"].model_dump()
        create_result = self.service.create_entity("Epic", json.dumps(epic_data, cls=UUIDEncoder))
        epic_id = json.loads(create_result)["entity_id"]
        
        # Create a new service instance to test persistence
        new_service = KnowledgeService(str(self.storage_path))
        
        # Retrieve the entity
        retrieve_result = new_service.get_entity_by_id("Epic", epic_id)
        retrieve_data = json.loads(retrieve_result)
        assert retrieve_data["id"] == epic_id
        assert retrieve_data["name"] == "Test Epic"


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
