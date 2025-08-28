"""
Common fixtures and utilities for the Multi-Agent Project Management System.

This file provides:
- Common test fixtures
- Test utilities and helpers
- Configuration for testing
- Shared test data

Note: This file is designed to work with both pytest and unittest.
"""

import tempfile
import shutil
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, Generator
from datetime import datetime

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Try to import pytest, but don't fail if it's not available
try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    # Create a mock pytest module for unittest compatibility
    class MockPytest:
        def mark(self, *args, **kwargs):
            return lambda func: func
    pytest = MockPytest()

from models.data_models import (
    Project, Team, TeamMember, Scope, Epic, UserStory, Issue, Stakeholder, Risk, Milestone, Deliverable,
    generate_uuid
)

# ============================================================================
# COMMON FIXTURES
# ============================================================================

def temp_dir():
    """Create a temporary directory for test files and clean it up afterwards."""
    temp_dir = tempfile.mkdtemp(prefix="test_pms_")
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


def temp_file_path(temp_dir: Path) -> Path:
    """Create a temporary file path within the temp directory."""
    return temp_dir / "test_file.json"




# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

def sample_project() -> Project:
    """Provide a sample Project for testing."""
    team_member = TeamMember(name="Dev 1", role="Developer", email="dev1@test.com", capacity=40)
    team = Team(name="Test Team", members=[team_member], velocity=10, capacity=40)
    issue = Issue(title="Test Issue", description="Test issue description", type="Task", status="To Do", assignee=team_member, estimate_hours=8, actual_hours=0, due_date=datetime.now().date())
    user_story = UserStory(title="Test User Story", description="As a user...", acceptance_criteria=["Criteria 1"], story_points=5, issues=[issue], status="Backlog", priority=1)
    epic = Epic(name="Test Epic", description="Test epic description", business_value=10, user_stories=[user_story], priority="High", status="Proposed")
    scope = Scope(epics=[epic], inclusions=["Feature A"], exclusions=["Feature B"], assumptions=["Assumption 1"], constraints=["Constraint 1"], acceptance_criteria=["Criteria 1"])
    stakeholder = Stakeholder(name="Test Stakeholder", role="Sponsor", influence="High", interest="High", communication_preferences="Email")
    risk = Risk(description="Test Risk", category="Technical", probability="Medium", impact="High", mitigation_strategy="Test", contingency_plan="Test", status="Identified")
    deliverable = Deliverable(name="Test Deliverable", description="Test deliverable", status="Not Started")
    milestone = Milestone(name="Test Milestone", description="Test milestone", target_date=datetime.now().date(), deliverables=[deliverable], status="Planned")

    return Project(
        name="Test Project",
        vision="A test project for unit testing",
        description="A test project for unit testing",
        team=team,
        scope=scope,
        stakeholders=[stakeholder],
        risks=[risk],
        milestones=[milestone],
        status="Planning"
    )


def sample_entities() -> Dict[str, Dict[str, Any]]:
    """Provide sample entities for testing."""
    return {
        "basic_entity": {
            "@id": "test:entity1",
            "type": "TestEntity",
            "name": "Test Entity 1",
            "description": "A test entity for unit testing",
            "properties": ["prop1", "prop2"],
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00"
        },
        "entity_with_relations": {
            "@id": "test:entity2",
            "type": "Entity",
            "name": "Entity with Relations",
            "hasChild": ["test:child1", "test:child2"],
            "belongsTo": "test:group1"
        },
        "child_entity": {
            "@id": "test:child1",
            "type": "ChildEntity",
            "name": "Child Entity 1",
            "hasParent": "test:entity2"
        }
    }


# ============================================================================
# TEST UTILITIES
# ============================================================================

class TestUtils:
    """Utility class providing common test helper methods."""
    
    @staticmethod
    def create_temp_file(content: str, temp_dir: Path, filename: str = "test.txt") -> Path:
        """Create a temporary file with specified content."""
        file_path = temp_dir / filename
        file_path.write_text(content)
        return file_path
    
    @staticmethod
    def assert_entity_structure(entity: Dict[str, Any], required_fields: list):
        """Assert that an entity has the required structure."""
        for field in required_fields:
            assert field in entity, f"Entity missing required field: {field}"
    
    @staticmethod
    def assert_entity_relationships(entity: Dict[str, Any], expected_relations: Dict[str, list]):
        """Assert that an entity has the expected relationships."""
        for relation, expected_values in expected_relations.items():
            if relation in entity:
                actual_values = entity[relation] if isinstance(entity[relation], list) else [entity[relation]]
                assert set(actual_values) == set(expected_values), \
                    f"Expected {relation} to be {expected_values}, got {actual_values}"
    
    @staticmethod
    def create_test_entities(count: int, base_type: str = "TestEntity") -> list:
        """Create a list of test entities."""
        entities = []
        for i in range(count):
            entity = {
                "@id": f"test:{base_type.lower()}{i}",
                "type": base_type,
                "name": f"Test {base_type} {i}",
                "description": f"Description for test {base_type} {i}",
                "index": i
            }
            entities.append(entity)
        return entities


def test_utils() -> TestUtils:
    """Provide TestUtils instance for tests."""
    return TestUtils()


# ============================================================================
# PERFORMANCE TESTING
# ============================================================================

def performance_threshold() -> float:
    """Provide performance threshold for tests (in seconds)."""
    return 1.0


def assert_performance(operation_time: float, threshold: float, operation_name: str = "Operation"):
    """Assert that an operation completes within the performance threshold."""
    assert operation_time < threshold, \
        f"{operation_name} took {operation_time:.3f}s, expected less than {threshold}s"


# ============================================================================
# CLEANUP UTILITIES
# ============================================================================

def cleanup_test_files(*file_paths: Path):
    """Clean up test files after tests."""
    for file_path in file_paths:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path, ignore_errors=True)


def auto_cleanup():
    """Automatically clean up after each test."""
    yield
    # This will run after each test
    # Additional cleanup can be added here if needed


# ============================================================================
# PYTEST INTEGRATION (if available)
# ============================================================================

if PYTEST_AVAILABLE:
    # Convert functions to pytest fixtures
    temp_dir = pytest.fixture(temp_dir)
    sample_project = pytest.fixture(sample_project)
    sample_entities = pytest.fixture(sample_entities)
    test_utils = pytest.fixture(test_utils)
    performance_threshold = pytest.fixture(performance_threshold)
    auto_cleanup = pytest.fixture(autouse=True)(auto_cleanup)
