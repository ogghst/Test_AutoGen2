# Logging Configuration Guide

This document explains the logging setup for the Multi-Agent Project Management System.

## Overview

The system uses a centralized logging configuration that:
- Logs all messages to files in the `logs/` directory
- Supports log rotation to manage file sizes
- Provides different log levels for different components
- Integrates with the existing AutoGen and system components

## Logging Architecture

### 1. Centralized Configuration (`config/logging_config.py`)

The main logging configuration is centralized in `config/logging_config.py` and provides:

- **File-based logging**: All logs are written to `logs/backend.log`
- **Log rotation**: Automatic rotation when files exceed size limits
- **Component-specific loggers**: Different log levels for different system parts
- **System information logging**: Automatic logging of system details

### 2. Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about system operation
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for problems that occurred
- **CRITICAL**: Critical errors that may cause system failure

### 3. Log Format

Logs include:
- Timestamp (ISO format)
- Logger name (component identifier)
- Log level
- Function name and line number (for detailed format)
- Message content

Example:
```
2024-01-15 14:30:25 - agents.project_manager - INFO - ProjectManager agent initialized successfully
2024-01-15 14:30:26 - knowledge.knowledge_base - DEBUG - Retrieved context for agent ProjectManager (project: None)
```

## Configuration

### Basic Setup

```python
from config.logging_config import setup_logging, get_logger

# Set up logging (file only, no console output)
setup_logging(
    log_level="INFO",
    console_logging=False,
    max_bytes=10 * 1024 * 1024,  # 10MB
    backup_count=5
)

# Get a logger for your component
logger = get_logger(__name__)
```

### Environment Variables

You can configure logging using environment variables:

```bash
# Log level
export LOG_LEVEL=DEBUG

# Log file path
export LOG_FILE=custom_log.log

# Console logging (true/false)
export CONSOLE_LOGGING=false
```

### Component-Specific Logging

```python
# Set specific log level for a component
from config.logging_config import set_component_log_level

set_component_log_level("agents", "DEBUG")
set_component_log_level("knowledge", "INFO")
set_component_log_level("storage", "WARNING")
```

## Usage in Components

### 1. Agents

```python
from config.logging_config import get_logger

class MyAgent(BaseProjectAgent):
    def __init__(self, ...):
        self.logger = get_logger(__name__)
        self.logger.info("Agent initialized")
    
    async def process_message(self, message):
        self.logger.debug(f"Processing message: {message.content[:100]}...")
        # ... processing logic
        self.logger.info("Message processed successfully")
```

### 2. Knowledge Base

```python
from config.logging_config import get_logger

logger = get_logger(__name__)

def add_entity(self, entity):
    logger.info(f"Adding entity: {entity.get('@id', 'unknown')}")
    # ... logic
    logger.debug("Entity added successfully")
```

### 3. Document Store

```python
from config.logging_config import get_logger

class DocumentStore:
    def __init__(self, ...):
        self.logger = get_logger(__name__)
        self.logger.info(f"DocumentStore initialized: {storage_path}")
    
    def save_document(self, document):
        self.logger.info(f"Saving document: {document.title}")
        # ... logic
        self.logger.debug("Document saved successfully")
```

## Log Files

### Main Log File

- **Location**: `logs/backend.log`
- **Content**: All system logs
- **Rotation**: Automatically rotated when size exceeds limit

### Rotated Log Files

When the main log file exceeds the size limit, it's rotated:
- `backend.log.1` (most recent backup)
- `backend.log.2`
- `backend.log.3`
- etc.

### Log Directory Structure

```
logs/
├── backend.log      # Current log file
├── backend.log.1    # Most recent backup
├── backend.log.2    # Second backup
└── backend.log.3    # Third backup
```

## Testing

### Test Logging Setup

Run the test script to verify logging works:

```bash
cd backend
python test_logging.py
```

This will:
1. Set up logging configuration
2. Generate test log messages
3. Verify log file creation
4. Test log rotation
5. Display log contents

### Manual Testing

```python
# Test in Python console
from config.logging_config import setup_logging, get_logger

setup_logging(console_logging=True)  # Enable console for testing
logger = get_logger("test")
logger.info("Test message")
```

## Troubleshooting

### Common Issues

1. **Logs not appearing**
   - Check if `logs/` directory exists
   - Verify file permissions
   - Check log level configuration

2. **Log rotation not working**
   - Verify `max_bytes` and `backup_count` settings
   - Check available disk space
   - Ensure write permissions

3. **Performance issues**
   - Reduce log level for verbose components
   - Increase rotation frequency
   - Use async logging for high-volume operations

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
setup_logging(
    log_level="DEBUG",
    console_logging=True  # Enable console for immediate feedback
)
```

## Best Practices

1. **Use appropriate log levels**
   - DEBUG: Detailed debugging information
   - INFO: General operational information
   - WARNING: Potential issues
   - ERROR: Actual errors
   - CRITICAL: System-threatening errors

2. **Include context in log messages**
   ```python
   logger.info(f"Processing project {project_id} for user {user_id}")
   ```

3. **Log exceptions with context**
   ```python
   try:
       # ... operation
   except Exception as e:
       logger.error(f"Failed to process {item_id}: {e}", exc_info=True)
   ```

4. **Use structured logging for complex data**
   ```python
   logger.info("User action", extra={
       "user_id": user_id,
       "action": "project_create",
       "project_id": project_id
   })
   ```

## Integration with AutoGen

The logging system is designed to work with AutoGen 0.7.2+:

- AutoGen's internal logging is set to WARNING level to reduce noise
- Agent conversations are logged through the system's logging infrastructure
- Tool calls and responses are logged for debugging

## Monitoring and Maintenance

### Log Analysis

Use standard tools to analyze logs:

```bash
# View recent logs
tail -f logs/backend.log

# Search for errors
grep "ERROR" logs/backend.log

# Count log entries by level
grep -c "INFO" logs/backend.log
```

### Log Cleanup

The system automatically manages log rotation, but you may want to:

- Monitor disk space usage
- Archive old log files
- Set up log aggregation for production environments

### Performance Monitoring

- Monitor log file sizes
- Check rotation frequency
- Monitor logging performance impact
