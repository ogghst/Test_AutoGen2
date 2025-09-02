"""
Example usage of the EntityService for CRUD operations.
"""

import json
from service import EntityService


def main():
    """Demonstrate the EntityService functionality."""
    
    # Initialize the service
    service = EntityService(storage_path="data_model/test/storage")
    
    print("=== EntityService Demo ===\n")
    
    # 1. Create entities
    print("1. Creating entities...")
    
    # Create a project
    project_data = json.dumps({
        "name": "Test Project"
    })
    project_result = service.create_entity("project", project_data)
    project = json.loads(project_result)
    project_id = project["id"]
    print(f"Created project: {project['name']} (ID: {project_id})")
    
    # Create a user
    user_data = json.dumps({
        "name": "John Doe",
        "email": "john.doe@example.com"
    })
    user_result = service.create_entity("user", user_data)
    user = json.loads(user_result)
    user_id = user["id"]
    print(f"Created user: {user['name']} (ID: {user_id})")
    
    # Create an issue
    issue_data = json.dumps({
        "title": "Bug in authentication",
        "description": "Users cannot log in with special characters in password"
    })
    issue_result = service.create_entity("issue", issue_data)
    issue = json.loads(issue_result)
    issue_id = issue["id"]
    print(f"Created issue: {issue['title']} (ID: {issue_id})")
    
    print()
    
    # 2. Create relationships
    print("2. Creating relationships...")
    
    # User assigned to project
    assignment_edge = service.create_relationship(
        user_id, project_id, "assigned_to"
    )
    print(f"Created assignment relationship: User -> Project")
    
    # Issue belongs to project
    belongs_edge = service.create_relationship(
        issue_id, project_id, "belongs_to"
    )
    print(f"Created belongs relationship: Issue -> Project")
    
    # User created issue
    created_edge = service.create_relationship(
        user_id, issue_id, "created"
    )
    print(f"Created creation relationship: User -> Issue")
    
    print()
    
    # 3. Retrieve entities
    print("3. Retrieving entities...")
    
    retrieved_project = service.get_entity(project_id)
    if retrieved_project:
        project_data = json.loads(retrieved_project)
        print(f"Retrieved project: {project_data['name']}")
    
    retrieved_user = service.get_entity(user_id)
    if retrieved_user:
        user_data = json.loads(retrieved_user)
        print(f"Retrieved user: {user_data['name']} ({user_data['email']})")
    
    print()
    
    # 4. List all entities
    print("4. Listing all entities...")
    all_entities = service.list_entities()
    entities = json.loads(all_entities)
    print(f"Total entities: {len(entities)}")
    for entity in entities:
        entity_type = entity.get('__type__', 'unknown')
        name = entity.get('name', entity.get('title', entity.get('id', 'unnamed')))
        print(f"  - {entity_type}: {name}")
    
    print()
    
    # 5. Get relationships
    print("5. Getting relationships...")
    all_relationships = service.get_relationships()
    relationships = json.loads(all_relationships)
    print(f"Total relationships: {len(relationships)}")
    for rel in relationships:
        print(f"  - {rel['source']} --[{rel['label']}]--> {rel['target']}")
    
    print()
    
    # 6. Get schema
    print("6. Graph schema:")
    schema = service.get_schema()
    schema_data = json.loads(schema)
    print(json.dumps(schema_data, indent=2))
    
    print()
    
    # 6.1. Get entity schemas
    print("6.1. Entity schemas:")
    for entity_type in ['project', 'user', 'issue', 'edge']:
        print(f"\n{entity_type.upper()} schema:")
        entity_schema = service.get_entity_schema(entity_type)
        schema_data = json.loads(entity_schema)
        print(json.dumps(schema_data, indent=2))
    
    print()
    
    # 7. Get statistics
    print("7. Graph statistics:")
    stats = service.get_graph_statistics()
    stats_data = json.loads(stats)
    print(json.dumps(stats_data, indent=2))
    
    print()
    
    # 8. Export graph
    print("8. Exporting graph...")
    export_path = service.export_graph('json', 'demo_export.json')
    print(f"Graph exported to: {export_path}")
    
    print()
    
    # 9. Demonstrate new features
    print("9. Advanced Features Demo:")
    
    # 9.1. Search functionality
    print("9.1. Entity Search:")
    search_results = service.search_entity("user", "John")
    results = json.loads(search_results)
    print(f"Found {len(results)} users matching 'John'")
    for result in results:
        print(f"  - {result['entity_data']['name']} ({result['entity_data']['email']})")
    
    # 9.2. Graph-RAG subgraph
    print("\n9.2. Graph-RAG Subgraph:")
    if project_id:
        subgraph = service.get_relevant_subgraph(project_id, max_depth=1)
        subgraph_data = json.loads(subgraph)
        print(f"Subgraph around project has {subgraph_data['statistics']['total_nodes']} nodes and {subgraph_data['statistics']['total_edges']} edges")
    
    # 9.3. Transaction support
    print("\n9.3. Transaction Support:")
    try:
        with service.transaction():
            tx_project_data = json.dumps({"name": "Transaction Project"})
            tx_project = json.loads(service.create_entity("project", tx_project_data))
            tx_user_data = json.dumps({"name": "Transaction User", "email": "tx@example.com"})
            tx_user = json.loads(service.create_entity("user", tx_user_data))
            service.create_relationship(tx_user["id"], tx_project["id"], "assigned_to")
        print("  Transaction completed successfully")
    except Exception as e:
        print(f"  Transaction failed: {e}")
    
    # 9.4. Upsert functionality
    print("\n9.4. Upsert Functionality:")
    upsert_data = json.dumps({"name": "Upsert Project"})
    result1 = service.upsert_entity("project", upsert_data)
    project1 = json.loads(result1)
    print(f"  First upsert created project: {project1['name']} (ID: {project1['id']})")
    
    # Try to create same project again
    upsert_data2 = json.dumps({"name": "Upsert Project", "description": "Updated description"})
    result2 = service.upsert_entity("project", upsert_data2)
    project2 = json.loads(result2)
    print(f"  Second upsert updated project: {project2['name']} (ID: {project2['id']})")
    print(f"  Same ID: {project1['id'] == project2['id']}")
    
    print("\n=== Demo completed ===")


if __name__ == "__main__":
    main()
