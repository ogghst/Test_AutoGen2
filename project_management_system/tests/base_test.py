"""
Base test class providing common functionality for all test suites.

This class provides:
- Common setup and teardown methods
- Utility methods for testing
- Performance testing helpers
- Common assertions
"""

import unittest
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class BaseTestCase(unittest.TestCase, ABC):
    """Base test case class with common functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.test_dir = Path(tempfile.mkdtemp(prefix="test_pms_"))
        self.setup_test_environment()
    
    def tearDown(self):
        """Clean up after each test method."""
        self.cleanup_test_environment()
        shutil.rmtree(self.test_dir, ignore_errors=True)
        super().tearDown()
    
    @abstractmethod
    def setup_test_environment(self):
        """Set up the test environment. Must be implemented by subclasses."""
        pass
    
    def cleanup_test_environment(self):
        """Clean up the test environment. Can be overridden by subclasses."""
        pass
    
    def get_temp_file_path(self, filename: str = "test_file.txt") -> Path:
        """Get a temporary file path within the test directory."""
        return Path(self.test_dir) / filename
    
    def create_temp_file(self, content: str, filename: str = "test_file.txt") -> Path:
        """Create a temporary file with specified content."""
        file_path = self.get_temp_file_path(filename)
        file_path.write_text(content)
        return file_path
    
    def assert_entity_structure(self, entity: Dict[str, Any], required_fields: List[str]):
        """Assert that an entity has the required structure."""
        for field in required_fields:
            self.assertIn(field, entity, f"Entity missing required field: {field}")
    
    def assert_entity_relationships(self, entity: Dict[str, Any], expected_relations: Dict[str, List[str]]):
        """Assert that an entity has the expected relationships."""
        for relation, expected_values in expected_relations.items():
            if relation in entity:
                actual_values = entity[relation] if isinstance(entity[relation], list) else [entity[relation]]
                self.assertEqual(set(actual_values), set(expected_values),
                               f"Expected {relation} to be {expected_values}, got {actual_values}")
    
    def assert_performance(self, operation_time: float, threshold: float, operation_name: str = "Operation"):
        """Assert that an operation completes within the performance threshold."""
        self.assertLess(operation_time, threshold,
                       f"{operation_name} took {operation_time:.3f}s, expected less than {threshold}s")
    
    def measure_performance(self, operation, *args, **kwargs) -> float:
        """Measure the execution time of an operation."""
        start_time = time.time()
        result = operation(*args, **kwargs)
        end_time = time.time()
        return end_time - start_time
    
    def create_test_entities(self, count: int, base_type: str = "TestEntity") -> List[Dict[str, Any]]:
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


class AsyncBaseTestCase(BaseTestCase):
    """Base test case class for async tests."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.loop = None
    
    def tearDown(self):
        """Clean up after each test method."""
        if self.loop and not self.loop.is_closed():
            self.loop.close()
        super().tearDown()
    
    def run_async(self, coro):
        """Run an async coroutine in a new event loop."""
        import asyncio
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            return self.loop.run_until_complete(coro)
        finally:
            self.loop.close()
            self.loop = None


class PerformanceTestCase(BaseTestCase):
    """Base test case class for performance tests."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.performance_threshold = 1.0  # Default 1 second threshold
    
    def set_performance_threshold(self, threshold: float):
        """Set the performance threshold for tests."""
        self.performance_threshold = threshold
    
    def assert_operation_performance(self, operation, *args, operation_name: str = "Operation", **kwargs):
        """Assert that an operation meets performance requirements."""
        execution_time = self.measure_performance(operation, *args, **kwargs)
        self.assert_performance(execution_time, self.performance_threshold, operation_name)
        return execution_time


class IntegrationTestCase(BaseTestCase):
    """Base test case class for integration tests."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.integration_mode = True
    
    def setup_test_environment(self):
        """Set up integration test environment."""
        # Create more complex test environment for integration tests
        self.test_data_dir = Path(self.test_dir) / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
        self.test_config_dir = Path(self.test_dir) / "config"
        self.test_config_dir.mkdir(exist_ok=True)
    
    def cleanup_test_environment(self):
        """Clean up integration test environment."""
        # Additional cleanup for integration tests
        pass


class MockTestCase(BaseTestCase):
    """Base test case class for tests using mocks."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        super().setUp()
        self.setup_mocks()
    
    def setup_mocks(self):
        """Set up mocks for testing. Can be overridden by subclasses."""
        pass
    
    def create_mock_entity(self, entity_type: str = "MockEntity", **kwargs) -> Dict[str, Any]:
        """Create a mock entity with default values."""
        default_entity = {
            "@id": f"mock:{entity_type.lower()}",
            "type": entity_type,
            "name": f"Mock {entity_type}",
            "description": f"Mock description for {entity_type}",
            "createdAt": "2024-01-01T00:00:00",
            "updatedAt": "2024-01-01T00:00:00"
        }
        default_entity.update(kwargs)
        return default_entity


# ============================================================================
# TEST UTILITY FUNCTIONS
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


def create_test_file_structure(base_dir: Path, structure: Dict[str, Any]):
    """Create a test file structure based on a dictionary specification."""
    for name, content in structure.items():
        path = base_dir / name
        if isinstance(content, dict):
            path.mkdir(exist_ok=True)
            create_test_file_structure(path, content)
        else:
            path.write_text(str(content))


def cleanup_test_files(*file_paths: Path):
    """Clean up test files after tests."""
    for file_path in file_paths:
        if file_path.exists():
            if file_path.is_file():
                file_path.unlink()
            elif file_path.is_dir():
                shutil.rmtree(file_path, ignore_errors=True)


def assert_file_contents(file_path: Path, expected_content: str):
    """Assert that a file contains the expected content."""
    assert file_path.exists(), f"File {file_path} does not exist"
    actual_content = file_path.read_text()
    assert actual_content == expected_content, \
        f"File content mismatch. Expected: {expected_content}, Got: {actual_content}"


def assert_directory_structure(dir_path: Path, expected_structure: List[str]):
    """Assert that a directory contains the expected files and subdirectories."""
    assert dir_path.exists(), f"Directory {dir_path} does not exist"
    actual_items = [item.name for item in dir_path.iterdir()]
    for expected_item in expected_structure:
        assert expected_item in actual_items, f"Expected item {expected_item} not found in {dir_path}"


def assert_performance(operation_time: float, threshold: float, operation_name: str = "Operation"):
    """Assert that an operation completes within the performance threshold."""
    assert operation_time < threshold, \
        f"{operation_name} took {operation_time:.3f}s, expected less than {threshold}s"
