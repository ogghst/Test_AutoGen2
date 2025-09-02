# Entity Service Layer

A comprehensive service layer for CRUD operations on entities and relationships using Pydantic models and NetworkX for graph operations. Designed for LLM-powered multi-agent systems with advanced features for entity resolution, Graph-RAG, transactions, and idempotency.

## Features

### Core Functionality
- **Generic CRUD Operations**: Create, read, update, and delete entities without writing specific functions for each entity type
- **Relationship Management**: Create and manage relationships between entities
- **Pydantic Validation**: All inputs are validated using the generated Pydantic models with UUID4 validation
- **NetworkX Integration**: Uses NetworkX for graph operations and analysis
- **File Storage**: Automatic persistence to GraphML and JSON formats

### Advanced Features
- **Entity Search**: Search for entities by natural language queries (solves LLM entity resolution)
- **Graph-RAG**: Extract relevant subgraphs for scalable context management
- **Transaction Support**: Atomic operations with automatic rollback for data consistency
- **Upsert Operations**: Create or update entities to prevent duplicates (idempotency)
- **Schema Generation**: Generate detailed graph schemas and entity schemas
- **Export/Import**: Support for multiple graph formats (GraphML, JSON, GEXF, GML)
- **Graph Statistics**: Comprehensive graph analysis and centrality measures

## Entity Types

The service supports the following entity types with UUID4 identifiers:
- `project`: Project entities (unique by name)
- `user`: User entities (unique by email)
- `issue`: Issue/ticket entities (unique by title)
- `edge`: Relationship entities (unique by source, target, label combination)

### Entity Schema Information
Each entity type has a defined schema with:
- **Required Fields**: Fields that must be provided
- **Optional Fields**: Fields that can be omitted
- **Validation Rules**: UUID4 format for IDs, email format validation, regex patterns
- **Unique Constraints**: Fields used for duplicate detection in upsert operations

## Usage

### Basic Setup

```python
from service import EntityService

# Initialize the service
service = EntityService(storage_path="path/to/storage")
```

### Entity Operations

#### Create Entity
```python
import json

# Create a project
project_data = json.dumps({
    "name": "My Project"
})
result = service.create_entity("project", project_data)
project = json.loads(result)
print(f"Created project with ID: {project['id']}")
```

#### Get Entity
```python
# Retrieve an entity by ID
entity_json = service.get_entity("entity-id-here")
if entity_json:
    entity = json.loads(entity_json)
    print(f"Entity: {entity}")
```

#### Update Entity
```python
# Update an entity
updated_data = json.dumps({
    "name": "Updated Project Name"
})
result = service.update_entity("entity-id", "project", updated_data)
```

#### Delete Entity
```python
# Delete an entity (and all its relationships)
success = service.delete_entity("entity-id")
```

#### List Entities
```python
# List all entities
all_entities = service.list_entities()
entities = json.loads(all_entities)

# List entities of specific type
projects = service.list_entities("project")
```

### Relationship Operations

#### Create Relationship
```python
# Create a relationship between two entities
edge_data = service.create_relationship(
    source_id="user-id",
    target_id="project-id", 
    label="assigned_to"
)
```

#### Get Relationships
```python
# Get all relationships for an entity
relationships = service.get_relationships("entity-id")

# Get all relationships in the graph
all_relationships = service.get_relationships()
```

#### Delete Relationship
```python
# Delete a specific relationship
success = service.delete_relationship("source-id", "target-id")
```

### Graph Analysis

#### Get Schema
```python
# Get graph schema information
schema = service.get_schema()
schema_data = json.loads(schema)
print(json.dumps(schema_data, indent=2))

# Get schema for a specific entity type
entity_schema = service.get_entity_schema("project")
schema_data = json.loads(entity_schema)
print(json.dumps(schema_data, indent=2))
```

#### Get Statistics
```python
# Get detailed graph statistics
stats = service.get_graph_statistics()
stats_data = json.loads(stats)
print(json.dumps(stats_data, indent=2))
```

### Advanced Features

#### Entity Search
```python
# Search for entities by name, email, title, etc.
search_results = service.search_entity("user", "john")
results = json.loads(search_results)
print(f"Found {len(results)} users matching 'john'")

# Search with custom fields
search_results = service.search_entity("issue", "bug", ["title", "description"])
```

#### Graph-RAG (Relevant Subgraph)
```python
# Get relevant subgraph around an entity
subgraph = service.get_relevant_subgraph("entity-id", max_depth=2)
subgraph_data = json.loads(subgraph)
print(f"Subgraph has {subgraph_data['statistics']['total_nodes']} nodes")
```

#### Upsert Operations (Prevent Duplicates)
```python
# Create or update entity based on unique fields
project_data = json.dumps({"name": "My Project"})
result = service.upsert_entity("project", project_data)

# Second call with same name will update existing entity
updated_data = json.dumps({"name": "My Project", "description": "Updated"})
result = service.upsert_entity("project", updated_data)
```

#### Transaction Support
```python
# Use context manager for atomic operations
with service.transaction():
    project = service.create_entity("project", project_data)
    user = service.create_entity("user", user_data)
    service.create_relationship(user_id, project_id, "assigned_to")

# Or execute multiple operations as transaction
def create_project():
    return service.create_entity("project", project_data)

def create_user():
    return service.create_entity("user", user_data)

result = service.execute_transaction([create_project, create_user])
```

### File Operations

#### Export Graph
```python
# Export in different formats
json_path = service.export_graph('json', 'my_graph.json')
graphml_path = service.export_graph('graphml', 'my_graph.graphml')
gexf_path = service.export_graph('gexf', 'my_graph.gexf')
```

#### Import Graph
```python
# Import from file
service.import_graph('path/to/graph.json', 'json')
```

#### Clear Graph
```python
# Clear all data
service.clear_graph()
```

## Data Validation

All entity data is validated using Pydantic models generated from the LinkML schema:

- **UUID Validation**: IDs must be valid UUIDv4 format
- **Email Validation**: Email addresses must be valid format
- **Required Fields**: All required fields are enforced
- **Type Validation**: Data types are validated according to the schema

## Storage

The service automatically saves data in two formats:
- **GraphML**: For compatibility with graph analysis tools
- **JSON**: For easy integration with other systems

Files are stored in the specified storage directory and automatically loaded on service initialization.

## Solved Issues

This service layer addresses four critical issues in LLM-powered graph management systems:

### 1. Entity Resolution & Ambiguity
**Problem**: LLMs don't know entity UUIDs when processing natural language commands.
**Solution**: `search_entity()` method allows finding entities by name, email, title, etc.

### 2. State Management & Context Window
**Problem**: Large graphs don't fit in LLM context windows.
**Solution**: `get_relevant_subgraph()` provides Graph-RAG functionality for scalable context.

### 3. Transactionality and Multi-Step Failures
**Problem**: Multi-step operations can fail partially, leaving inconsistent state.
**Solution**: `transaction()` context manager and `execute_transaction()` ensure atomicity.

### 4. Idempotency
**Problem**: Repeated commands create duplicate entities.
**Solution**: `upsert_entity()` prevents duplicates using unique field matching.

## Use Cases

### LLM Agent Integration
```python
# Agent receives: "Assign the login bug to Alice"
# Step 1: Find entities
bug = service.search_entity("issue", "login bug")[0]
alice = service.search_entity("user", "alice")[0]

# Step 2: Create relationship
service.create_relationship(alice["id"], bug["id"], "assigned_to")
```

### Multi-Agent Workflows
```python
# Atomic project creation with team assignment
with service.transaction():
    project = service.create_entity("project", project_data)
    for member in team_members:
        user = service.upsert_entity("user", member_data)
        service.create_relationship(user["id"], project["id"], "assigned_to")
```

### Graph Analysis and Reporting
```python
# Get context for analysis
subgraph = service.get_relevant_subgraph(project_id, max_depth=2)
stats = service.get_graph_statistics()
schema = service.get_entity_schema("project")
```

## Example

See `example_usage.py` for a complete demonstration of all service features.

## Error Handling

The service provides comprehensive error handling:

### Validation Errors
```python
try:
    service.create_entity("user", json.dumps({"email": "invalid-email"}))
except ValueError as e:
    print(f"Validation error: {e}")
```

### Entity Not Found
```python
entity = service.get_entity("non-existent-id")
if entity is None:
    print("Entity not found")
```

### Transaction Failures
```python
try:
    with service.transaction():
        service.create_entity("project", project_data)
        raise ValueError("Simulated error")
except ValueError:
    print("Transaction rolled back automatically")
```

## Best Practices

### 1. Use Transactions for Multi-Step Operations
```python
# Good: Atomic operation
with service.transaction():
    project = service.create_entity("project", project_data)
    service.create_relationship(user_id, project["id"], "assigned_to")

# Bad: Non-atomic operation
project = service.create_entity("project", project_data)
service.create_relationship(user_id, project["id"], "assigned_to")  # Could fail
```

### 2. Use Upsert for Idempotent Operations
```python
# Good: Safe to run multiple times
service.upsert_entity("project", json.dumps({"name": "My Project"}))

# Bad: Creates duplicates
service.create_entity("project", json.dumps({"name": "My Project"}))
```

### 3. Search Before Creating Relationships
```python
# Good: Find entities first
users = service.search_entity("user", "alice")
if users:
    service.create_relationship(users[0]["id"], project_id, "assigned_to")

# Bad: Assume entity exists
service.create_relationship("alice-id", project_id, "assigned_to")  # Could fail
```

### 4. Use Graph-RAG for Large Contexts
```python
# Good: Get relevant context
subgraph = service.get_relevant_subgraph(entity_id, max_depth=2)

# Bad: Load entire graph
all_entities = service.list_entities()  # Could be huge
```

## Requirements

- Python 3.8+
- NetworkX >= 3.0
- Pydantic >= 2.0

Install requirements:
```bash
pip install -r requirements.txt
```

## Complete API Reference

### Entity Operations

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `create_entity(entity_type, json_data)` | Create a new entity with UUID4 ID | `entity_type`: str, `json_data`: str | JSON string of created entity |
| `get_entity(entity_id)` | Retrieve entity by UUID4 ID | `entity_id`: str | JSON string or None |
| `update_entity(entity_id, entity_type, json_data)` | Update existing entity | `entity_id`: str, `entity_type`: str, `json_data`: str | JSON string or None |
| `delete_entity(entity_id)` | Delete entity and all relationships | `entity_id`: str | bool (success) |
| `list_entities(entity_type=None)` | List all entities or by type | `entity_type`: str (optional) | JSON string of entity list |
| `upsert_entity(entity_type, json_data, unique_fields=None)` | Create or update entity | `entity_type`: str, `json_data`: str, `unique_fields`: List[str] (optional) | JSON string of entity |

### Relationship Operations

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `create_relationship(source_id, target_id, label, additional_data=None)` | Create relationship between entities | `source_id`: str, `target_id`: str, `label`: str, `additional_data`: str (optional) | JSON string of edge |
| `get_relationships(entity_id=None, direction='both')` | Get relationships for entity or all | `entity_id`: str (optional), `direction`: str ('in', 'out', 'both') | JSON string of relationships |
| `delete_relationship(source_id, target_id)` | Delete specific relationship | `source_id`: str, `target_id`: str | bool (success) |

### Search and Discovery

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `search_entity(entity_type, query, search_fields=None)` | Search entities by query | `entity_type`: str, `query`: str, `search_fields`: List[str] (optional) | JSON string of matches |
| `get_relevant_subgraph(entity_id, max_depth=2, include_relationships=True)` | Get Graph-RAG subgraph | `entity_id`: str, `max_depth`: int, `include_relationships`: bool | JSON string of subgraph |

### Schema and Analysis

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `get_schema()` | Get overall graph schema | None | JSON string of schema |
| `get_entity_schema(entity_type)` | Get entity type schema | `entity_type`: str | JSON string of entity schema |
| `get_graph_statistics()` | Get detailed graph statistics | None | JSON string of statistics |

### Transaction Management

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `transaction()` | Context manager for atomic operations | None | Context manager |
| `execute_transaction(operations)` | Execute operations as transaction | `operations`: List[Callable] | Dict with results |

### File Operations

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `export_graph(format='graphml', filename=None)` | Export graph to file | `format`: str, `filename`: str (optional) | Path to exported file |
| `import_graph(file_path, format='auto')` | Import graph from file | `file_path`: str, `format`: str | None |
| `clear_graph()` | Clear all data | None | None |

## Data Validation

All entity data is validated using Pydantic models generated from the LinkML schema:

- **UUID4 Validation**: All IDs must be valid UUID4 format (`^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`)
- **Email Validation**: Email addresses must match RFC format
- **Required Fields**: All required fields are enforced
- **Type Validation**: Data types are validated according to the schema
- **Pattern Validation**: Custom regex patterns for field validation

## Storage

The service automatically saves data in two formats:
- **GraphML**: For compatibility with graph analysis tools (Cytoscape, Gephi, etc.)
- **JSON**: For easy integration with other systems and APIs

Files are stored in the specified storage directory and automatically loaded on service initialization.

## Generated Models

The service uses Pydantic models generated from the LinkML schema in `test.yaml`. To regenerate the models:

```bash
gen-pydantic test.yaml > test.py
```
