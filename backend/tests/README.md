# Test Architecture for Multi-Agent Project Management System

This document describes the comprehensive test architecture that has been implemented for the project management system.

## Overview

The test architecture provides a consistent, maintainable, and extensible testing framework that supports both pytest and unittest, with common utilities and fixtures that can be shared across all test suites.

## Architecture Components

### 1. Base Test Classes (`base_test.py`)

The foundation of the test architecture provides several base classes:

- **`BaseTestCase`**: Common test functionality with automatic setup/teardown
- **`AsyncBaseTestCase`**: For testing async code with proper event loop management
- **`PerformanceTestCase`**: For performance testing with configurable thresholds
- **`IntegrationTestCase`**: For integration tests with enhanced environment setup
- **`MockTestCase`**: For tests that require extensive mocking

#### Key Features:
- Automatic temporary directory creation and cleanup
- Common assertion methods for entities and relationships
- Performance measurement utilities
- File and directory testing helpers

### 2. Common Fixtures (`conftest.py`)

Provides shared test data and utilities that work with both pytest and unittest:

- **Test Data**: Sample entities, documents, and project contexts
- **Storage Fixtures**: Knowledge base and document store instances
- **Utility Classes**: TestUtils for common testing operations
- **Performance Tools**: Thresholds and performance assertions

### 3. Test Categories

Tests are organized by category and can be run selectively:

- **Unit Tests**: Fast, isolated tests for individual components
- **Integration Tests**: Tests for component interactions
- **Performance Tests**: Tests for performance and scalability
- **Component Tests**: Tests for specific system components

### 4. Test Markers

When using pytest, tests can be marked for selective execution:

```python
@pytest.mark.unit
@pytest.mark.knowledge_base
def test_something():
    pass
```

Available markers:
- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.knowledge_base` - Knowledge base tests
- `@pytest.mark.document_store` - Document store tests
- `@pytest.mark.agents` - Agent tests

## Usage Examples

### Running Tests

#### Using the Test Runner Script
```bash
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
```

#### Using pytest directly
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific category
python -m pytest tests/ -m unit

# Run performance tests
python -m pytest tests/ -m performance

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

#### Using unittest (fallback)
```bash
# Run all tests
python -m unittest discover tests/ -v

# Run specific test class
python -m unittest tests.test_knowledge_base.TestKnowledgeBase -v

# Run specific test method
python -m unittest tests.test_knowledge_base.TestKnowledgeBase.test_initialization -v
```

### Writing Tests

#### Basic Test Structure
```python
from .base_test import BaseTestCase

class TestMyComponent(BaseTestCase):
    def setup_test_environment(self):
        """Set up test environment."""
        self.my_component = MyComponent()
    
    def test_something(self):
        """Test something."""
        result = self.my_component.do_something()
        self.assertEqual(result, expected_value)
```

#### Async Test Structure
```python
from .base_test import AsyncBaseTestCase

class TestMyAsyncComponent(AsyncBaseTestCase):
    def setup_test_environment(self):
        """Set up test environment."""
        self.async_component = MyAsyncComponent()
    
    async def test_async_operation(self):
        """Test async operation."""
        result = await self.async_component.do_async_thing()
        self.assertEqual(result, expected_value)
```

#### Performance Test Structure
```python
from .base_test import PerformanceTestCase

class TestMyPerformance(PerformanceTestCase):
    def setup_test_environment(self):
        """Set up test environment."""
        self.set_performance_threshold(2.0)  # 2 seconds
    
    def test_performance(self):
        """Test performance."""
        execution_time = self.measure_performance(
            lambda: self.expensive_operation()
        )
        self.assert_performance(execution_time, self.performance_threshold, "Expensive operation")
```

### Using Common Fixtures

#### In Test Classes
```python
def test_with_sample_data(self):
    """Test using sample data."""
    sample_entity = sample_entities()["basic_entity"]
    result = self.kb.add_entity(sample_entity)
    self.assertIsNotNone(result)
```

#### In pytest Tests
```python
def test_with_fixtures(knowledge_base, sample_document):
    """Test using pytest fixtures."""
    result = knowledge_base.add_entity(sample_document)
    assert result is not None
```

## Test Organization

### Directory Structure
```
tests/
├── __init__.py              # Package initialization and exports
├── base_test.py             # Base test classes and utilities
├── conftest.py              # Common fixtures and utilities
├── run_tests.py             # Test runner script
├── requirements-test.txt     # Testing dependencies
├── pytest.ini              # pytest configuration
├── README.md                # This documentation
├── test_knowledge_base.py   # Knowledge base tests
├── test_document_store.py   # Document store tests
└── test_agents.py           # Agent tests (placeholder)
```

### Test File Naming Convention
- Test files: `test_<component>.py`
- Test classes: `Test<ComponentName>`
- Test methods: `test_<description>`

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use `setup_test_environment()` and `cleanup_test_environment()` for setup/teardown
- Avoid sharing state between tests

### 2. Test Data
- Use the provided sample data fixtures
- Create realistic test scenarios
- Avoid hardcoded test data in test methods

### 3. Assertions
- Use descriptive assertion messages
- Use the provided utility methods for common assertions
- Test both positive and negative cases

### 4. Performance Testing
- Set appropriate performance thresholds
- Use the performance measurement utilities
- Document performance requirements

### 5. Error Handling
- Test error conditions and edge cases
- Verify that appropriate exceptions are raised
- Test error recovery scenarios

## Dependencies

### Required for Basic Testing
- Python 3.8+
- unittest (built-in)

### Optional for Enhanced Testing
- pytest (for advanced features)
- pytest-asyncio (for async test support)
- pytest-cov (for coverage reporting)
- pytest-xdist (for parallel execution)

### Installation
```bash
# Install basic testing dependencies
pip install -r tests/requirements-test.txt

# Or install specific packages
pip install pytest pytest-asyncio pytest-cov
```

## Configuration

### pytest Configuration (`pytest.ini`)
- Test discovery settings
- Marker definitions
- Output formatting
- Coverage settings

### Test Runner Configuration
- Category-based test execution
- Output format options
- Coverage reporting
- Performance thresholds

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in the Python path
2. **Fixture Errors**: Check that fixtures are properly defined and imported
3. **Performance Failures**: Adjust performance thresholds based on your system
4. **Async Test Issues**: Ensure proper event loop management

### Debug Mode
```bash
# Run tests with verbose output
python -m pytest tests/ -v -s

# Run specific test with debug output
python -m pytest tests/test_knowledge_base.py::TestKnowledgeBase::test_initialization -v -s
```

## Contributing

When adding new tests:

1. Follow the existing naming conventions
2. Use appropriate base test classes
3. Add appropriate markers for categorization
4. Include comprehensive test coverage
5. Update this documentation if needed

## Future Enhancements

- Parallel test execution support
- Advanced coverage reporting
- Test result visualization
- Performance benchmarking
- Integration with CI/CD pipelines
