"""
Unit tests for the EntityService.
"""

import json
import pytest
from service import EntityService


class TestEntityService:
    """Test cases for EntityService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = EntityService(storage_path="test_storage")
        self.service.clear_graph()  # Start with clean graph
    
    def teardown_method(self):
        """Clean up after tests."""
        self.service.clear_graph()
    
    def test_create_project(self):
        """Test creating a project entity."""
        project_data = json.dumps({"name": "Test Project"})
        result = self.service.create_entity("project", project_data)
        
        project = json.loads(result)
        assert project["name"] == "Test Project"
        assert "id" in project
        assert len(project["id"]) == 36  # UUID length
    
    def test_create_user(self):
        """Test creating a user entity."""
        user_data = json.dumps({
            "name": "Test User",
            "email": "test@example.com"
        })
        result = self.service.create_entity("user", user_data)
        
        user = json.loads(result)
        assert user["name"] == "Test User"
        assert user["email"] == "test@example.com"
        assert "id" in user
    
    def test_create_issue(self):
        """Test creating an issue entity."""
        issue_data = json.dumps({
            "title": "Test Issue",
            "description": "Test description"
        })
        result = self.service.create_entity("issue", issue_data)
        
        issue = json.loads(result)
        assert issue["title"] == "Test Issue"
        assert issue["description"] == "Test description"
        assert "id" in issue
    
    def test_get_entity(self):
        """Test retrieving an entity."""
        # Create an entity
        project_data = json.dumps({"name": "Test Project"})
        result = self.service.create_entity("project", project_data)
        project = json.loads(result)
        project_id = project["id"]
        
        # Retrieve it
        retrieved = self.service.get_entity(project_id)
        assert retrieved is not None
        
        retrieved_project = json.loads(retrieved)
        assert retrieved_project["name"] == "Test Project"
        assert retrieved_project["id"] == project_id
    
    def test_update_entity(self):
        """Test updating an entity."""
        # Create an entity
        project_data = json.dumps({"name": "Original Name"})
        result = self.service.create_entity("project", project_data)
        project = json.loads(result)
        project_id = project["id"]
        
        # Update it
        updated_data = json.dumps({"name": "Updated Name"})
        result = self.service.update_entity(project_id, "project", updated_data)
        
        updated_project = json.loads(result)
        assert updated_project["name"] == "Updated Name"
        assert updated_project["id"] == project_id
    
    def test_delete_entity(self):
        """Test deleting an entity."""
        # Create an entity
        project_data = json.dumps({"name": "Test Project"})
        result = self.service.create_entity("project", project_data)
        project = json.loads(result)
        project_id = project["id"]
        
        # Delete it
        success = self.service.delete_entity(project_id)
        assert success is True
        
        # Verify it's gone
        retrieved = self.service.get_entity(project_id)
        assert retrieved is None
    
    def test_create_relationship(self):
        """Test creating a relationship."""
        # Create two entities
        project_data = json.dumps({"name": "Test Project"})
        project_result = self.service.create_entity("project", project_data)
        project = json.loads(project_result)
        
        user_data = json.dumps({"name": "Test User", "email": "test@example.com"})
        user_result = self.service.create_entity("user", user_data)
        user = json.loads(user_result)
        
        # Create relationship
        edge_data = self.service.create_relationship(
            user["id"], project["id"], "assigned_to"
        )
        
        edge = json.loads(edge_data)
        assert edge["source"] == user["id"]
        assert edge["target"] == project["id"]
        assert edge["label"] == "assigned_to"
        assert "id" in edge
    
    def test_get_relationships(self):
        """Test getting relationships."""
        # Create entities and relationship
        project_data = json.dumps({"name": "Test Project"})
        project_result = self.service.create_entity("project", project_data)
        project = json.loads(project_result)
        
        user_data = json.dumps({"name": "Test User", "email": "test@example.com"})
        user_result = self.service.create_entity("user", user_data)
        user = json.loads(user_result)
        
        self.service.create_relationship(user["id"], project["id"], "assigned_to")
        
        # Get relationships
        relationships = self.service.get_relationships()
        rels = json.loads(relationships)
        
        assert len(rels) == 1
        assert rels[0]["source"] == user["id"]
        assert rels[0]["target"] == project["id"]
        assert rels[0]["label"] == "assigned_to"
    
    def test_list_entities(self):
        """Test listing entities."""
        # Create multiple entities
        project_data = json.dumps({"name": "Project 1"})
        self.service.create_entity("project", project_data)
        
        user_data = json.dumps({"name": "User 1", "email": "user1@example.com"})
        self.service.create_entity("user", user_data)
        
        # List all entities
        all_entities = self.service.list_entities()
        entities = json.loads(all_entities)
        
        assert len(entities) == 2
        
        # List specific type
        projects = self.service.list_entities("project")
        project_list = json.loads(projects)
        assert len(project_list) == 1
        assert project_list[0]["name"] == "Project 1"
    
    def test_get_schema(self):
        """Test getting graph schema."""
        # Create some entities and relationships
        project_data = json.dumps({"name": "Test Project"})
        project_result = self.service.create_entity("project", project_data)
        project = json.loads(project_result)
        
        user_data = json.dumps({"name": "Test User", "email": "test@example.com"})
        user_result = self.service.create_entity("user", user_data)
        user = json.loads(user_result)
        
        self.service.create_relationship(user["id"], project["id"], "assigned_to")
        
        # Get schema
        schema = self.service.get_schema()
        schema_data = json.loads(schema)
        
        assert schema_data["nodes"]["count"] == 2
        assert schema_data["edges"]["count"] == 1
        assert schema_data["properties"]["is_directed"] is True
    
    def test_get_entity_schema(self):
        """Test getting entity schema."""
        # Test project schema
        project_schema = self.service.get_entity_schema("project")
        schema_data = json.loads(project_schema)
        
        assert schema_data["entity_type"] == "project"
        assert schema_data["model_name"] == "Project"
        assert "id" in schema_data["properties"]
        assert "name" in schema_data["properties"]
        assert schema_data["properties"]["id"]["is_identifier"] is True
        assert "id" in schema_data["required_fields"]
        
        # Test user schema
        user_schema = self.service.get_entity_schema("user")
        user_schema_data = json.loads(user_schema)
        
        assert user_schema_data["entity_type"] == "user"
        assert user_schema_data["model_name"] == "User"
        assert "email" in user_schema_data["properties"]
        assert "email" in user_schema_data["validation_rules"]
        
        # Test issue schema
        issue_schema = self.service.get_entity_schema("issue")
        issue_schema_data = json.loads(issue_schema)
        
        assert issue_schema_data["entity_type"] == "issue"
        assert issue_schema_data["model_name"] == "Issue"
        assert "title" in issue_schema_data["properties"]
        assert "description" in issue_schema_data["properties"]
        
        # Test edge schema
        edge_schema = self.service.get_entity_schema("edge")
        edge_schema_data = json.loads(edge_schema)
        
        assert edge_schema_data["entity_type"] == "edge"
        assert edge_schema_data["model_name"] == "Edge"
        assert "source" in edge_schema_data["properties"]
        assert "target" in edge_schema_data["properties"]
        assert "label" in edge_schema_data["properties"]
    
    def test_validation_error(self):
        """Test validation error handling."""
        # Try to create user with invalid email
        invalid_user_data = json.dumps({
            "name": "Test User",
            "email": "invalid-email"  # Invalid email format
        })
        
        with pytest.raises(ValueError, match="Validation error"):
            self.service.create_entity("user", invalid_user_data)
    
    def test_invalid_entity_type(self):
        """Test handling of invalid entity type."""
        data = json.dumps({"name": "Test"})
        
        with pytest.raises(ValueError, match="Unknown entity type"):
            self.service.create_entity("invalid_type", data)
    
    def test_search_entity(self):
        """Test entity search functionality."""
        # Create test entities
        project_data = json.dumps({"name": "Test Project"})
        project_result = self.service.create_entity("project", project_data)
        project = json.loads(project_result)
        
        user_data = json.dumps({"name": "John Doe", "email": "john@example.com"})
        user_result = self.service.create_entity("user", user_data)
        user = json.loads(user_result)
        
        issue_data = json.dumps({"title": "Bug Report", "description": "Critical bug in login"})
        issue_result = self.service.create_entity("issue", issue_data)
        issue = json.loads(issue_result)
        
        # Search for project by name
        search_results = self.service.search_entity("project", "Test")
        results = json.loads(search_results)
        assert len(results) == 1
        assert results[0]["id"] == project["id"]
        assert results[0]["match_field"] == "name"
        
        # Search for user by email
        search_results = self.service.search_entity("user", "john@example.com")
        results = json.loads(search_results)
        assert len(results) == 1
        assert results[0]["id"] == user["id"]
        
        # Search for issue by title
        search_results = self.service.search_entity("issue", "Bug")
        results = json.loads(search_results)
        assert len(results) == 1
        assert results[0]["id"] == issue["id"]
    
    def test_get_relevant_subgraph(self):
        """Test Graph-RAG subgraph functionality."""
        # Create entities and relationships
        project_data = json.dumps({"name": "Test Project"})
        project_result = self.service.create_entity("project", project_data)
        project = json.loads(project_result)
        
        user_data = json.dumps({"name": "John Doe", "email": "john@example.com"})
        user_result = self.service.create_entity("user", user_data)
        user = json.loads(user_result)
        
        issue_data = json.dumps({"title": "Bug Report", "description": "Critical bug"})
        issue_result = self.service.create_entity("issue", issue_data)
        issue = json.loads(issue_result)
        
        # Create relationships
        self.service.create_relationship(user["id"], project["id"], "assigned_to")
        self.service.create_relationship(issue["id"], project["id"], "belongs_to")
        self.service.create_relationship(user["id"], issue["id"], "created")
        
        # Get subgraph around project
        subgraph = self.service.get_relevant_subgraph(project["id"], max_depth=1)
        subgraph_data = json.loads(subgraph)
        
        assert subgraph_data["central_entity_id"] == project["id"]
        assert subgraph_data["statistics"]["total_nodes"] >= 3  # At least project, user, issue
        assert subgraph_data["statistics"]["total_edges"] >= 2  # At least 2 relationships
        
        # Check that all connected entities are included
        node_ids = [node["id"] for node in subgraph_data["nodes"]]
        assert project["id"] in node_ids
        assert user["id"] in node_ids
        assert issue["id"] in node_ids
    
    def test_transaction_success(self):
        """Test successful transaction."""
        project_data = json.dumps({"name": "Transaction Project"})
        user_data = json.dumps({"name": "Transaction User", "email": "transaction@example.com"})
        
        # Use transaction context manager
        with self.service.transaction():
            project_result = self.service.create_entity("project", project_data)
            project = json.loads(project_result)
            
            user_result = self.service.create_entity("user", user_data)
            user = json.loads(user_result)
            
            self.service.create_relationship(user["id"], project["id"], "assigned_to")
        
        # Verify all operations were successful
        retrieved_project = self.service.get_entity(project["id"])
        retrieved_user = self.service.get_entity(user["id"])
        relationships = self.service.get_relationships()
        
        assert retrieved_project is not None
        assert retrieved_user is not None
        assert len(json.loads(relationships)) == 1
    
    def test_transaction_rollback(self):
        """Test transaction rollback on failure."""
        project_data = json.dumps({"name": "Rollback Project"})
        
        # Count entities before transaction
        entities_before = self.service.list_entities()
        count_before = len(json.loads(entities_before))
        
        try:
            with self.service.transaction():
                project_result = self.service.create_entity("project", project_data)
                project = json.loads(project_result)
                
                # Force an error
                raise ValueError("Simulated error")
        except ValueError:
            pass  # Expected error
        
        # Verify rollback occurred
        entities_after = self.service.list_entities()
        count_after = len(json.loads(entities_after))
        assert count_after == count_before  # No new entities should exist
    
    def test_upsert_entity_create(self):
        """Test upsert creating new entity."""
        project_data = json.dumps({"name": "Upsert Project"})
        
        # First upsert should create
        result = self.service.upsert_entity("project", project_data)
        project = json.loads(result)
        
        assert project["name"] == "Upsert Project"
        assert "id" in project
        
        # Verify entity exists
        retrieved = self.service.get_entity(project["id"])
        assert retrieved is not None
    
    def test_upsert_entity_update(self):
        """Test upsert updating existing entity."""
        project_data = json.dumps({"name": "Upsert Project"})
        
        # First upsert creates
        result1 = self.service.upsert_entity("project", project_data)
        project1 = json.loads(result1)
        
        # Second upsert with same name should update
        updated_data = json.dumps({"name": "Upsert Project", "description": "Updated description"})
        result2 = self.service.upsert_entity("project", updated_data)
        project2 = json.loads(result2)
        
        # Should have same ID but updated data
        assert project1["id"] == project2["id"]
        assert project2["name"] == "Upsert Project"
        
        # Verify only one entity exists
        all_projects = self.service.list_entities("project")
        projects = json.loads(all_projects)
        assert len(projects) == 1
    
    def test_upsert_user_by_email(self):
        """Test upsert for user by email uniqueness."""
        user_data1 = json.dumps({"name": "John Doe", "email": "john@example.com"})
        user_data2 = json.dumps({"name": "John Smith", "email": "john@example.com"})
        
        # First upsert creates
        result1 = self.service.upsert_entity("user", user_data1)
        user1 = json.loads(result1)
        
        # Second upsert with same email should update
        result2 = self.service.upsert_entity("user", user_data2)
        user2 = json.loads(result2)
        
        # Should have same ID but updated name
        assert user1["id"] == user2["id"]
        assert user2["name"] == "John Smith"
        assert user2["email"] == "john@example.com"
    
    def test_execute_transaction(self):
        """Test execute_transaction method."""
        project_data = json.dumps({"name": "Transaction Project"})
        user_data = json.dumps({"name": "Transaction User", "email": "transaction@example.com"})
        
        def create_project():
            return self.service.create_entity("project", project_data)
        
        def create_user():
            return self.service.create_entity("user", user_data)
        
        def create_relationship():
            project = json.loads(create_project())
            user = json.loads(create_user())
            return self.service.create_relationship(user["id"], project["id"], "assigned_to")
        
        # Execute transaction
        result = self.service.execute_transaction([create_project, create_user, create_relationship])
        
        assert result["status"] == "success"
        assert result["operations_executed"] == 3
        assert len(result["results"]) == 3


if __name__ == "__main__":
    pytest.main([__file__])
