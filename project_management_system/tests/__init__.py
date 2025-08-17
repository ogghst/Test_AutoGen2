"""
Test package for the Multi-Agent Project Management System.

This package contains comprehensive test suites for all system components.

Test Architecture:
=================

1. Base Test Classes (base_test.py):
   - BaseTestCase: Common test functionality
   - AsyncBaseTestCase: For async tests
   - PerformanceTestCase: For performance testing
   - IntegrationTestCase: For integration tests
   - MockTestCase: For tests using mocks

2. Common Fixtures (conftest.py):
   - pytest fixtures for common test data
   - Test utilities and helpers
   - Performance testing utilities

3. Test Categories:
   - Unit tests: Fast, isolated tests
   - Integration tests: Component interaction tests
   - Performance tests: Performance and scalability tests

4. Test Markers:
   - @pytest.mark.unit: Unit tests
   - @pytest.mark.integration: Integration tests
   - @pytest.mark.performance: Performance tests
   - @pytest.mark.knowledge_base: Knowledge base tests
   - @pytest.mark.document_store: Document store tests
   - @pytest.mark.agents: Agent tests

5. Test Runner (run_tests.py):
   - Convenient test execution
   - Category-based test running
   - Coverage reporting
   - Multiple output formats

Usage Examples:
==============

# Run all tests
python tests/run_tests.py

# Run specific category
python tests/run_tests.py -c knowledge_base

# Run with coverage
python tests/run_tests.py --coverage

# Run only unit tests
python tests/run_tests.py -c unit

# Generate test report
python tests/run_tests.py --report

# Using pytest directly
python -m pytest tests/ -v
python -m pytest tests/ -m unit
python -m pytest tests/ -m performance

# Using unittest (fallback)
python -m unittest discover tests/ -v
"""

__version__ = "2.0.0"
__author__ = "Test Suite"
__description__ = "Comprehensive testing for the project management system"

# Import common test utilities for easy access
from .base_test import (
    BaseTestCase,
    AsyncBaseTestCase,
    PerformanceTestCase,
    IntegrationTestCase,
    MockTestCase,
    TestUtils,
    assert_performance,
    cleanup_test_files,
    assert_file_contents,
    assert_directory_structure
)

# Import common fixtures
from .conftest import (
    temp_dir,
    knowledge_base,
    knowledge_base_with_data,
    document_store,
    feature_rich_document_store,
    sample_project_context,
    sample_document,
    sample_entities,
    test_utils,
    performance_threshold
)

__all__ = [
    # Base test classes
    'BaseTestCase',
    'AsyncBaseTestCase', 
    'PerformanceTestCase',
    'IntegrationTestCase',
    'MockTestCase',
    
    # Test utilities
    'TestUtils',
    'assert_performance',
    'cleanup_test_files',
    'assert_file_contents',
    'assert_directory_structure',
    
    # Common fixtures
    'temp_dir',
    'knowledge_base',
    'knowledge_base_with_data',
    'document_store',
    'feature_rich_document_store',
    'sample_project_context',
    'sample_document',
    'sample_entities',
    'test_utils',
    'performance_threshold'
]
