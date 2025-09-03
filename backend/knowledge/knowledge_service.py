"""
Service layer for generic CRUD operations on entities and relationships.
Uses Pydantic models for validation and NetworkX for graph operations.
"""

import json
import uuid
from typing import Dict, List, Optional, Type, Any, Union, Callable
from pathlib import Path
import networkx as nx
from pydantic import BaseModel, ValidationError
from contextlib import contextmanager

from config.logging_config import get_logger
from models.data_models import ConfiguredBaseModel, Edge

logger = get_logger(__name__)

class KnowledgeService:
    """Wrapper class that provides the expected interface for the knowledge service."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the KnowledgeService with an EntityService instance.
        
        Args:
            storage_path: Path to store graph data files
        """
        self.entity_service = EntityService(storage_path)
    
    def get_entity_types(self) -> str:
        """
        Get the list of entity types.
        
        Returns:
            JSON string representation of the list of entity types.
        """
        logger.info("Retrieving available entity types")
        entity_types = list(self.entity_service.entity_types.keys())
        logger.info(f"Found {len(entity_types)} entity types: {entity_types}")
        return json.dumps(entity_types)
    
    def create_entity(self, entity_type: str, json_data: str) -> str:
        """
        Create a new entity.
        
        Args:
            entity_type: Type of entity
            json_data: JSON string containing entity data
            
        Returns:
            JSON string of the created entity with generated ID
        """
        logger.info(f"Creating new entity of type: {entity_type}")
        logger.debug(f"Entity data: {json_data}")
        
        # Parse the JSON data
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format for entity creation: {e}")
            return json.dumps({"error": f"Invalid JSON format: {e}"})
        
        # Create the entity first (without __type__ field)
        result = self.entity_service.create_entity(entity_type, json.dumps(data))
        result_data = json.loads(result)
        
        # Add the entity type to the result data for tracking
        #result_data['__type__'] = entity_type
        
        # Convert any remaining date objects to strings
        #result_data = self.entity_service._convert_dates_to_strings(result_data)
        
        logger.info(f"Successfully created entity {result_data.get('id')} of type {entity_type}")
        return json.dumps(result_data)
    
    def create_relationship(self, source: str, target: str, label: str, json_data: str) -> str:
        """
        Create a new relationship.
        
        Args:
            source: The source entity ID
            target: The target entity ID
            label: The relationship label
            json_data: JSON string containing relationship attributes
        """
        return self.entity_service.create_relationship(source, target, label, json_data)
    
    def get_entity_by_id(self, entity_type: str, entity_id: str, include_relationships: bool = False) -> str:
        """
        Get a specific entity by ID.
        
        Args:
            entity_type: The type of the entity to get.
            entity_id: The ID of the entity to get.
            include_relationships: Whether to include relationship data
            
        Returns:
            JSON string representation of the entity.
        """
        logger.info(f"Retrieving entity {entity_id} of type {entity_type}, include_relationships={include_relationships}")
        
        if include_relationships:
            # Get the entity with its relationships using subgraph
            logger.debug(f"Getting entity with relationships using subgraph")
            return self.entity_service.get_relevant_subgraph(entity_id, max_depth=1, include_relationships=True)
        else:
            # Get just the entity without relationships
            result = self.entity_service.get_entity(entity_id)
            if result is None:
                logger.warning(f"Entity {entity_id} not found")
                return json.dumps({"error": f"Entity {entity_id} not found"})
            
            # Add the entity type to the result
            result_data = json.loads(result)
            result_data['__type__'] = entity_type
            logger.info(f"Successfully retrieved entity {entity_id}")
            return json.dumps(result_data)
    
    def update_entity(self, entity_type: str, entity_id: str, updates_json: str) -> str:
        """
        Update an existing entity by ID.
        
        Args:
            entity_type: The type of the entity to update.
            entity_id: The ID of the entity to update.
            updates_json: The JSON string representation of the updates to apply.
            
        Returns:
            JSON string representation of the updated entity.
        """
        logger.info(f"Updating entity {entity_id} of type {entity_type}")
        logger.debug(f"Update data: {updates_json}")
        
        result = self.entity_service.update_entity(entity_id, entity_type, updates_json)
        if result is None:
            logger.warning(f"Entity {entity_id} not found for update")
            return json.dumps({"error": f"Entity {entity_id} not found"})
        
        # Add the entity type to the result
        result_data = json.loads(result)
        result_data['__type__'] = entity_type
        
        # Convert any remaining date objects to strings
        result_data = self.entity_service._convert_dates_to_strings(result_data)
        
        logger.info(f"Successfully updated entity {entity_id}")
        return json.dumps(result_data)
    
    def delete_entity(self, entity_type: str, entity_id: str) -> str:
        """
        Delete an existing entity by ID.
        
        Args:
            entity_type: The type of the entity to delete.
            entity_id: The ID of the entity to delete.
            
        Returns:
            JSON string representation of the deletion result.
        """
        logger.info(f"Deleting entity {entity_id} of type {entity_type}")
        
        success = self.entity_service.delete_entity(entity_id)
        
        if success:
            logger.info(f"Successfully deleted entity {entity_id}")
        else:
            logger.warning(f"Failed to delete entity {entity_id} - entity not found")
        
        return json.dumps({"success": success, "entity_id": entity_id})
    
    def query_entities(self, entity_type: str, filters_json: str) -> str:
        """
        Query entities of a specific type with optional filters.
        
        Args:
            entity_type: The type of the entities to query.
            filters_json: The JSON string representation of the filters to apply.
            
        Returns:
            JSON string representation of the matching entities.
        """
        logger.info(f"Querying entities of type {entity_type}")
        logger.debug(f"Filters: {filters_json}")
        
        # Parse filters
        try:
            filters = json.loads(filters_json) if filters_json else {}
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid filters JSON format: {e}, using empty filters")
            filters = {}
        
        # Get all entities of the specified type
        all_entities = self.entity_service.list_entities(entity_type)
        entities = json.loads(all_entities)
        
        logger.debug(f"Found {len(entities)} total entities of type {entity_type}")
        
        # Apply simple filters (this is a basic implementation)
        filtered_entities = []
        for entity in entities:
            # Ensure entity has the correct type
            if entity.get('__type__') != entity_type:
                continue
                
            match = True
            for key, value in filters.items():
                if key not in entity or entity[key] != value:
                    match = False
                    break
            if match:
                filtered_entities.append(entity)
        
        logger.info(f"Query returned {len(filtered_entities)} matching entities")
        return json.dumps(filtered_entities)
    
    def get_full_project_context(self, project_id: str) -> str:
        """
        Get the full context of a project including all related entities.
        
        Args:
            project_id: The ID of the project to get the full context of.
            
        Returns:
            JSON string containing the full project context.
        """
        logger.info(f"Getting full project context for project {project_id}")
        
        # Get the project entity
        project_data = self.entity_service.get_entity(project_id)
        if project_data is None:
            logger.warning(f"Project {project_id} not found")
            return json.dumps({"error": f"Project {project_id} not found"})
        
        # Get the relevant subgraph around the project
        logger.debug(f"Retrieving subgraph with max_depth=2 and relationships")
        return self.entity_service.get_relevant_subgraph(project_id, max_depth=2, include_relationships=True)
    
    def get_entity_schema(self, entity_type: str) -> str:
        """
        Get the JSON schema of a specific entity type.

        Args:
            entity_type: The type of the entity to get the schema of.

        Returns:
            JSON string representation of the entity's model schema.
        """
        logger.info(f"Retrieving schema for entity type: {entity_type}")
        return self.entity_service.get_entity_schema(entity_type)


class EntityService:
    """Generic service for entity and relationship management."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the service with optional storage path.
        
        Args:
            storage_path: Path to store graph data files
        """
        logger.info("Initializing EntityService")
        logger.debug(f"Storage path: {storage_path}")
        
        self.storage_path = Path(storage_path) if storage_path else Path(".")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using storage path: {self.storage_path.absolute()}")
        
        # Initialize NetworkX graph
        self.graph = nx.DiGraph()
        logger.debug("Initialized NetworkX directed graph")
        
        # Entity type mapping
        # Dynamically retrieve all classes from models.data_models that inherit from ConfiguredBaseModel
        import inspect
        import models.data_models as data_models

        logger.debug("Discovering entity types from data models")
        self.entity_types = {
            name.lower(): cls
            for name, cls in inspect.getmembers(data_models, inspect.isclass)
            if issubclass(cls, ConfiguredBaseModel) and cls is not ConfiguredBaseModel
        }
        
        # Also include classes that inherit from ConfiguredBaseModel through intermediate classes
        # This ensures classes like TeamMember (which inherits from Person -> ConfiguredBaseModel) are included
        additional_entity_types = {
            name.lower(): cls
            for name, cls in inspect.getmembers(data_models, inspect.isclass)
            if (hasattr(cls, '__bases__') and 
                any(issubclass(base, ConfiguredBaseModel) for base in cls.__bases__) and
                cls is not ConfiguredBaseModel and
                name.lower() not in self.entity_types)  # Don't duplicate existing entries
        }
        self.entity_types.update(additional_entity_types)
        
        logger.info(f"Discovered {len(self.entity_types)} entity types: {list(self.entity_types.keys())}")
        
        # Load existing data if available
        logger.debug("Loading existing graph data")
        self._load_graph()
        
        # Transaction support
        self._transaction_stack = []
        self._in_transaction = False
        logger.info("EntityService initialization completed")
    
    def _get_entity_class(self, entity_type: str) -> Type[ConfiguredBaseModel]:
        """Get the Pydantic model class for the given entity type."""
        entity_type = entity_type.lower()
        if entity_type not in self.entity_types:
            logger.error(f"Unknown entity type: {entity_type}")
            logger.debug(f"Available entity types: {list(self.entity_types.keys())}")
            raise ValueError(f"Unknown entity type: {entity_type}. Available types: {list(self.entity_types.keys())}")
        
        logger.debug(f"Retrieved entity class for type: {entity_type}")
        return self.entity_types[entity_type]
    
    def _validate_json_input(self, json_data: str, entity_type: str, generate_id: bool = False) -> Dict[str, Any]:
        """Validate and parse JSON input."""
        logger.debug(f"Validating JSON input for entity type: {entity_type}")
        
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Generate ID if requested and not provided
        #if generate_id and ('id' not in data or not data['id']):
        data['id'] = self._generate_id()
        logger.debug(f"Generated ID: {data['id']}")
        
        # Remove __type__ field before validation as it's not part of the Pydantic model
        #data_for_validation = {k: v for k, v in data.items() if k != '__type__'}
        
        data_for_validation = data
        
        entity_class = self._get_entity_class(entity_type)
        try:
            # Validate using Pydantic
            validated_entity = entity_class(**data_for_validation)
            validated_data = validated_entity.model_dump()
            
            # Restore __type__ field if it was present
            #if '__type__' in data:
            #    validated_data['__type__'] = data['__type__']
            
            logger.debug(f"Successfully validated {entity_type} entity")
            return validated_data
        except ValidationError as e:
            logger.error(f"Validation error for {entity_type}: {e}")
            raise ValueError(f"Validation error for {entity_type}: {e}")
    
    def _generate_id(self) -> str:
        """Generate a UUIDv4 identifier."""
        return str(uuid.uuid4())
    
    def create_entity(self, entity_type: str, json_data: str) -> str:
        """
        Create a new entity.
        
        Args:
            entity_type: Type of entity ('project', 'user', 'issue', 'edge')
            json_data: JSON string containing entity data
            
        Returns:
            JSON string of the created entity with generated ID
        """
        
        logger.info(f"Creating entity: {entity_type} with data: {json_data}")   
        
        try:
            # Parse the JSON string to a dict before adding 'class_name'

            data = json.loads(json_data)
            data['class_name'] = entity_type
            json_data = json.dumps(data)
            validated_data = self._validate_json_input(json_data, entity_type, generate_id=True)
            
            # Add entity type to the data for tracking
            #validated_data['__type__'] = entity_type
            
            # Convert any date objects to strings for JSON serialization
            validated_data = self._convert_dates_to_strings(validated_data)
            
            # Add to NetworkX graph
            self.graph.add_node(validated_data['id'], **validated_data)
            logger.debug(f"Added node {validated_data['id']} to graph")
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
                logger.debug("Graph saved to file")
            
            logger.info(f"Successfully created entity {validated_data['id']} of type {entity_type}")
            return json.dumps(validated_data)
            
        except Exception as e:
            logger.error(f"Failed to create entity of type {entity_type}: {e}")
            raise
    
    def upsert_entity(self, entity_type: str, json_data: str, unique_fields: Optional[List[str]] = None) -> str:
        """
        Create or update an entity based on unique field matching (upsert operation).
        
        Args:
            entity_type: Type of entity ('project', 'user', 'issue', 'edge')
            json_data: JSON string containing entity data
            unique_fields: List of fields to use for uniqueness check (defaults to entity-specific fields)
            
        Returns:
            JSON string of the created or updated entity
        """
        logger.info(f"Upserting entity of type {entity_type}")
        logger.debug(f"Unique fields: {unique_fields}")
        
        try:
            validated_data = self._validate_json_input(json_data, entity_type, generate_id=True)
            
            # Default unique fields for each entity type
            default_unique_fields = {
                'project': ['name'],
                'user': ['email'],
                'issue': ['title'],
                'edge': ['source', 'target', 'label']
            }
            
            if unique_fields is None:
                unique_fields = default_unique_fields.get(entity_type, ['name'])
            
            logger.debug(f"Using unique fields: {unique_fields}")
            
            # Search for existing entity with matching unique fields
            existing_entity_id = self._find_entity_by_unique_fields(entity_type, validated_data, unique_fields)
            
            if existing_entity_id:
                # Update existing entity
                logger.info(f"Found existing entity {existing_entity_id}, updating")
                validated_data['id'] = existing_entity_id
                self.graph.nodes[existing_entity_id].update(validated_data)
                
                # Save to file (only if not in transaction)
                if not self._in_transaction:
                    self._save_graph()
                    logger.debug("Graph saved after update")
                
                logger.info(f"Successfully updated entity {existing_entity_id}")
                return json.dumps(validated_data)
            else:
                # Create new entity
                logger.info("No existing entity found, creating new one")
                return self.create_entity(entity_type, json_data)
                
        except Exception as e:
            logger.error(f"Failed to upsert entity of type {entity_type}: {e}")
            raise
    
    def _find_entity_by_unique_fields(self, entity_type: str, data: Dict[str, Any], unique_fields: List[str]) -> Optional[str]:
        """Find an existing entity that matches the unique fields."""
        for node_id, node_data in self.graph.nodes(data=True):
            if self._is_entity_of_type(node_data, entity_type):
                # Check if all unique fields match
                matches = True
                for field in unique_fields:
                    if field in data and field in node_data:
                        if data[field] != node_data[field]:
                            matches = False
                            break
                    elif field in data or field in node_data:
                        matches = False
                        break
                
                if matches:
                    return node_id
        
        return None
    
    def get_entity(self, entity_id: str) -> Optional[str]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            JSON string of the entity or None if not found
        """
        logger.debug(f"Retrieving entity {entity_id}")
        
        if not self.graph.has_node(entity_id):
            logger.debug(f"Entity {entity_id} not found in graph")
            return None
        
        entity_data = self.graph.nodes[entity_id].copy()
        # Ensure the ID is included in the returned data
        entity_data['id'] = entity_id
        logger.debug(f"Successfully retrieved entity {entity_id}")
        return json.dumps(entity_data)
    
    def update_entity(self, entity_id: str, entity_type: str, json_data: str) -> Optional[str]:
        """
        Update an existing entity.
        
        Args:
            entity_id: ID of the entity to update
            entity_type: Type of entity
            json_data: JSON string containing updated entity data
            
        Returns:
            JSON string of the updated entity or None if not found
        """
        logger.info(f"Updating entity {entity_id} of type {entity_type}")
        logger.debug(f"Update data: {json_data}")
        
        if not self.graph.has_node(entity_id):
            logger.warning(f"Entity {entity_id} not found for update")
            return None
        
        try:
            # Get existing entity data
            existing_data = self.graph.nodes[entity_id].copy()
            
            # Parse the update data
            try:
                update_data = json.loads(json_data)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON format for update: {e}")
                raise ValueError(f"Invalid JSON format: {e}")
            
            # Merge update data with existing data
            merged_data = existing_data.copy()
            merged_data.update(update_data)
            
            # Validate the merged data
            validated_data = self._validate_json_input(json.dumps(merged_data), entity_type)
            
            # Ensure ID matches
            validated_data['id'] = entity_id
            
            # Convert any date objects to strings for JSON serialization
            validated_data = self._convert_dates_to_strings(validated_data)
            
            # Update in NetworkX graph
            self.graph.nodes[entity_id].update(validated_data)
            logger.debug(f"Updated node {entity_id} in graph")
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
                logger.debug("Graph saved after update")
            
            logger.info(f"Successfully updated entity {entity_id}")
            return json.dumps(validated_data)
            
        except Exception as e:
            logger.error(f"Failed to update entity {entity_id}: {e}")
            raise
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity and all its relationships.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting entity {entity_id}")
        
        if not self.graph.has_node(entity_id):
            logger.warning(f"Entity {entity_id} not found for deletion")
            return False
        
        try:
            # Remove all edges connected to this node
            edges_to_remove = list(self.graph.edges(entity_id, data=True))
            edges_to_remove.extend(list(self.graph.in_edges(entity_id, data=True)))
            
            logger.debug(f"Removing {len(edges_to_remove)} edges connected to entity {entity_id}")
            
            for edge in edges_to_remove:
                self.graph.remove_edge(edge[0], edge[1])
            
            # Remove the node
            self.graph.remove_node(entity_id)
            logger.debug(f"Removed node {entity_id} from graph")
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
                logger.debug("Graph saved after deletion")
            
            logger.info(f"Successfully deleted entity {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete entity {entity_id}: {e}")
            raise
    
    def list_entities(self, entity_type: Optional[str] = None) -> str:
        """
        List all entities, optionally filtered by type.
        
        Args:
            entity_type: Optional entity type filter
            
        Returns:
            JSON string containing list of entities
        """
        logger.info(f"Listing entities, filter: {entity_type or 'all types'}")
        
        entities = []
        total_nodes = 0
        
        for node_id, data in self.graph.nodes(data=True):
            total_nodes += 1
            if entity_type is None or data.get('__type__') == entity_type:
                entities.append(data)
        
        logger.info(f"Found {len(entities)} entities of type {entity_type or 'all'} from {total_nodes} total nodes")
        return json.dumps(entities)
    
    def create_relationship(self, source_id: str, target_id: str, label: str, 
                          additional_data: Optional[str] = None) -> str:
        """
        Create a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            label: Label/type of the relationship
            additional_data: Optional JSON string with additional edge data
            
        Returns:
            JSON string of the created edge
        """
        logger.info(f"Creating relationship from {source_id} to {target_id} with label '{label}'")
        logger.debug(f"Additional data: {additional_data}")
        
        try:
            # Validate that both nodes exist
            if not self.graph.has_node(source_id):
                logger.error(f"Source entity {source_id} not found")
                raise ValueError(f"Source entity {source_id} not found")
            if not self.graph.has_node(target_id):
                logger.error(f"Target entity {target_id} not found")
                raise ValueError(f"Target entity {target_id} not found")
            
            # Create edge data
            edge_data = {
                'id': self._generate_id(),
                'source': source_id,
                'target': target_id,
                'label': label
            }
            
            # Add additional data if provided
            if additional_data:
                try:
                    extra_data = json.loads(additional_data)
                    edge_data.update(extra_data)
                    logger.debug(f"Added additional data to edge: {extra_data}")
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid additional data JSON: {e}")
                    raise ValueError(f"Invalid additional data JSON: {e}")
            
            # Validate using Edge model
            #try:
            #    validated_edge = Edge(**edge_data)
            #    edge_data = validated_edge.model_dump()
            #except ValidationError as e:
            #    logger.error(f"Edge validation error: {e}")
            #    raise ValueError(f"Edge validation error: {e}")
            
            # Add edge to graph
            self.graph.add_edge(source_id, target_id, **edge_data)
            logger.debug(f"Added edge {edge_data['id']} to graph")
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
                logger.debug("Graph saved after relationship creation")
            
            logger.info(f"Successfully created relationship {edge_data['id']}")
            return json.dumps(edge_data)
            
        except Exception as e:
            logger.error(f"Failed to create relationship from {source_id} to {target_id}: {e}")
            raise
    
    def get_relationships(self, entity_id: Optional[str] = None, 
                         direction: str = 'both') -> str:
        """
        Get relationships for an entity or all relationships.
        
        Args:
            entity_id: Optional entity ID to filter relationships
            direction: 'in', 'out', or 'both' for relationship direction
            
        Returns:
            JSON string containing list of relationships
        """
        logger.info(f"Getting relationships for entity {entity_id}, direction: {direction}")
        
        relationships = []
        
        if entity_id:
            if direction in ['out', 'both']:
                out_edges = list(self.graph.out_edges(entity_id, data=True))
                for source, target, data in out_edges:
                    relationships.append(data)
                logger.debug(f"Found {len(out_edges)} outgoing relationships")
            
            if direction in ['in', 'both']:
                in_edges = list(self.graph.in_edges(entity_id, data=True))
                for source, target, data in in_edges:
                    relationships.append(data)
                logger.debug(f"Found {len(in_edges)} incoming relationships")
        else:
            # Get all edges
            all_edges = list(self.graph.edges(data=True))
            for source, target, data in all_edges:
                relationships.append(data)
            logger.debug(f"Found {len(all_edges)} total relationships")
        
        logger.info(f"Retrieved {len(relationships)} relationships")
        return json.dumps(relationships)
    
    def search_entity(self, entity_type: str, query: str, search_fields: Optional[List[str]] = None) -> str:
        """
        Search for entities matching a query string.
        
        Args:
            entity_type: Type of entity to search ('project', 'user', 'issue', 'edge')
            query: Search query string
            search_fields: Optional list of fields to search in (defaults to common searchable fields)
            
        Returns:
            JSON string containing list of matching entities
        """
        logger.info(f"Searching for {entity_type} entities with query: '{query}'")
        logger.debug(f"Search fields: {search_fields}")
        
        if entity_type not in self.entity_types:
            logger.error(f"Unknown entity type: {entity_type}")
            raise ValueError(f"Unknown entity type: {entity_type}. Available types: {list(self.entity_types.keys())}")
        
        # Default searchable fields for each entity type
        default_search_fields = {
            'project': ['name'],
            'user': ['name', 'email'],
            'issue': ['title', 'description'],
            'edge': ['label']
        }
        
        if search_fields is None:
            search_fields = default_search_fields.get(entity_type, ['name'])
        
        logger.debug(f"Using search fields: {search_fields}")
        
        query_lower = query.lower()
        matching_entities = []
        total_entities_checked = 0
        
        for node_id, data in self.graph.nodes(data=True):
            # Check if this node matches the entity type
            if self._is_entity_of_type(data, entity_type):
                total_entities_checked += 1
                # Search in specified fields
                for field in search_fields:
                    if field in data and data[field]:
                        field_value = str(data[field]).lower()
                        if query_lower in field_value:
                            matching_entities.append({
                                'id': node_id,
                                'entity_type': entity_type,
                                'match_field': field,
                                'match_value': data[field],
                                'entity_data': data
                            })
                            logger.debug(f"Found match in {node_id} field '{field}': '{data[field]}'")
                            break  # Found a match, no need to check other fields
        
        logger.info(f"Search completed: {len(matching_entities)} matches found from {total_entities_checked} {entity_type} entities")
        return json.dumps(matching_entities)
    
    def get_relevant_subgraph(self, entity_id: str, max_depth: int = 2, include_relationships: bool = True) -> str:
        """
        Get a relevant subgraph around a specific entity (Graph-RAG functionality).
        
        Args:
            entity_id: ID of the central entity
            max_depth: Maximum depth of relationships to include
            include_relationships: Whether to include relationship data
            
        Returns:
            JSON string containing the relevant subgraph
        """
        logger.info(f"Getting relevant subgraph for entity {entity_id}, max_depth={max_depth}, include_relationships={include_relationships}")
        
        if not self.graph.has_node(entity_id):
            logger.error(f"Entity {entity_id} not found")
            raise ValueError(f"Entity {entity_id} not found")
        
        try:
            # Get the subgraph using NetworkX
            subgraph_nodes = set([entity_id])
            
            # Expand to include connected nodes up to max_depth
            current_level = [entity_id]
            for depth in range(max_depth):
                next_level = set()
                for node in current_level:
                    # Add neighbors (both in and out edges)
                    neighbors = list(self.graph.neighbors(node))
                    neighbors.extend(list(self.graph.predecessors(node)))
                    next_level.update(neighbors)
                
                subgraph_nodes.update(next_level)
                current_level = list(next_level)
                logger.debug(f"Depth {depth + 1}: found {len(next_level)} new nodes")
            
            # Create subgraph
            subgraph = self.graph.subgraph(subgraph_nodes)
            logger.debug(f"Created subgraph with {subgraph.number_of_nodes()} nodes and {subgraph.number_of_edges()} edges")
            
            # Build result
            result = {
                'central_entity_id': entity_id,
                'max_depth': max_depth,
                'nodes': [],
                'edges': [],
                'statistics': {
                    'total_nodes': subgraph.number_of_nodes(),
                    'total_edges': subgraph.number_of_edges(),
                    'depth_reached': max_depth
                }
            }
            
            # Add nodes
            for node_id, data in subgraph.nodes(data=True):
                node_info = {
                    'id': node_id,
                    'data': data,
                    'distance_from_center': self._calculate_distance(entity_id, node_id, subgraph)
                }
                result['nodes'].append(node_info)
            
            # Add edges if requested
            if include_relationships:
                for source, target, data in subgraph.edges(data=True):
                    edge_info = {
                        'source': source,
                        'target': target,
                        'data': data
                    }
                    result['edges'].append(edge_info)
            
            logger.info(f"Successfully generated subgraph with {len(result['nodes'])} nodes and {len(result['edges'])} edges")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to get relevant subgraph for entity {entity_id}: {e}")
            raise
    
    def _calculate_distance(self, source_id: str, target_id: str, graph: nx.Graph) -> int:
        """Calculate the shortest path distance between two nodes."""
        try:
            return nx.shortest_path_length(graph, source_id, target_id)
        except nx.NetworkXNoPath:
            return -1  # No path exists
    
    def _is_entity_of_type(self, data: Dict[str, Any], entity_type: str) -> bool:
        """Check if a node's data matches the specified entity type."""
        # For now, we'll use a simple heuristic based on field presence
        # In a more sophisticated system, you might store entity type as metadata
        type_indicators = {
            'project': ['name'],
            'user': ['email'],
            'issue': ['title'],
            'edge': ['source', 'target', 'label']
        }
        
        indicators = type_indicators.get(entity_type, [])
        return any(field in data for field in indicators)
    
    def delete_relationship(self, source_id: str, target_id: str) -> bool:
        """
        Delete a relationship between two entities.
        
        Args:
            source_id: ID of the source entity
            target_id: ID of the target entity
            
        Returns:
            True if deleted, False if not found
        """
        logger.info(f"Deleting relationship from {source_id} to {target_id}")
        
        if not self.graph.has_edge(source_id, target_id):
            logger.warning(f"Relationship from {source_id} to {target_id} not found")
            return False
        
        try:
            self.graph.remove_edge(source_id, target_id)
            logger.debug(f"Removed edge from {source_id} to {target_id}")
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
                logger.debug("Graph saved after relationship deletion")
            
            logger.info(f"Successfully deleted relationship from {source_id} to {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete relationship from {source_id} to {target_id}: {e}")
            raise
    
    def get_schema(self) -> str:
        """
        Generate and return the graph schema.
        
        Returns:
            JSON string containing the graph schema
        """
        schema = {
            'nodes': {
                'count': self.graph.number_of_nodes(),
                'types': {}
            },
            'edges': {
                'count': self.graph.number_of_edges(),
                'types': {}
            },
            'properties': {
                'is_directed': self.graph.is_directed(),
                'is_multigraph': self.graph.is_multigraph()
            }
        }
        
        # Count node types
        for node_id, data in self.graph.nodes(data=True):
            node_type = data.get('__type__', 'unknown')
            schema['nodes']['types'][node_type] = schema['nodes']['types'].get(node_type, 0) + 1
        
        # Count edge types
        for source, target, data in self.graph.edges(data=True):
            edge_label = data.get('label', 'unknown')
            schema['edges']['types'][edge_label] = schema['edges']['types'].get(edge_label, 0) + 1
        
        return json.dumps(schema, indent=2)
    
    def get_entity_schema(self, entity_type: str) -> str:
        """
        Get the schema definition for a specific entity type.
        
        Args:
            entity_type: Type of entity ('project', 'user', 'issue', 'edge')
            
        Returns:
            JSON string containing the entity schema definition
        """
        entity_class = self._get_entity_class(entity_type)
        
        # Get the Pydantic model schema
        model_schema = entity_class.model_json_schema()
        
        return json.dumps(model_schema)
        '''
        # Extract relevant information
        entity_schema = {
            'entity_type': entity_type,
            'model_name': entity_class.__name__,
            'description': model_schema.get('description', ''),
            'properties': {},
            'required_fields': model_schema.get('required', []),
            'field_types': {},
            'validation_rules': {}
        }
        
        # Process properties
        properties = model_schema.get('properties', {})
        for field_name, field_info in properties.items():
            entity_schema['properties'][field_name] = {
                'type': field_info.get('type', 'unknown'),
                'description': field_info.get('description', ''),
                'format': field_info.get('format', None),
                'pattern': field_info.get('pattern', None),
                'is_identifier': field_name == 'id'
            }
            
            # Store field types for easy access
            entity_schema['field_types'][field_name] = field_info.get('type', 'unknown')
            
            # Store validation rules
            if 'pattern' in field_info:
                entity_schema['validation_rules'][field_name] = {
                    'pattern': field_info['pattern'],
                    'description': f"Must match pattern: {field_info['pattern']}"
                }
        
        # Add entity-specific metadata
        entity_schema['metadata'] = {
            'total_fields': len(properties),
            'required_count': len(entity_schema['required_fields']),
            'optional_count': len(properties) - len(entity_schema['required_fields']),
            'has_identifier': 'id' in properties,
            'identifier_field': 'id' if 'id' in properties else None
        }
        
        return json.dumps(entity_schema, indent=2)
        '''
    
    def _save_graph(self) -> None:
        """Save the graph to files."""
        logger.debug("Saving graph to files")
        
        try:
            # Create a copy of the graph with complex objects filtered out for GraphML
            graph_copy = self.graph.copy()
            
            # Filter node data to only include simple types
            filtered_nodes = 0
            for node_id in graph_copy.nodes():
                node_data = graph_copy.nodes[node_id]
                filtered_data = {}
                for k, v in node_data.items():
                    if v is not None and self._is_simple_type(v):
                        filtered_data[k] = v
                graph_copy.nodes[node_id].clear()
                graph_copy.nodes[node_id].update(filtered_data)
                filtered_nodes += 1
            
            # Filter edge data to only include simple types
            filtered_edges = 0
            for edge in graph_copy.edges():
                edge_data = graph_copy.edges[edge]
                filtered_data = {}
                for k, v in edge_data.items():
                    if v is not None and self._is_simple_type(v):
                        filtered_data[k] = v
                graph_copy.edges[edge].clear()
                graph_copy.edges[edge].update(filtered_data)
                filtered_edges += 1
            
            logger.debug(f"Filtered {filtered_nodes} nodes and {filtered_edges} edges for GraphML")
            
            # Save as GraphML
            graphml_path = self.storage_path / "graph.graphml"
            nx.write_graphml(graph_copy, graphml_path)
            logger.debug(f"Saved GraphML to {graphml_path}")
            
            
            # Save as JSON (original graph with all data, converting dates to strings)
            json_path = self.storage_path / "graph.json"
            # Use edges="links" for backward compatibility with NetworkX
            graph_data = nx.node_link_data(self.graph, edges="links")
            # Convert dates to strings for JSON serialization
            graph_data = self._convert_dates_to_strings(graph_data)
            with open(json_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
            logger.debug(f"Saved JSON to {json_path}")
            
            logger.info(f"Successfully saved graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")
            raise
    
    def _is_simple_type(self, value) -> bool:
        """Check if a value is a simple type that can be stored in GraphML."""
        return isinstance(value, (str, int, float, bool)) or value is None
    
    def _convert_dates_to_strings(self, data):
        """Convert date and datetime objects to strings for JSON serialization."""
        from datetime import datetime, date
        
        if isinstance(data, dict):
            return {k: self._convert_dates_to_strings(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_dates_to_strings(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, date):
            return data.isoformat()
        else:
            return data
    
    def _load_graph(self) -> None:
        """Load the graph from files."""
        json_path = self.storage_path / "graph.json"
        
        if json_path.exists():
            logger.info(f"Loading existing graph from {json_path}")
            try:
                with open(json_path, 'r') as f:
                    graph_data = json.load(f)
                # Use edges="links" for backward compatibility with NetworkX
                self.graph = nx.node_link_graph(graph_data, edges="links")
                logger.info(f"Successfully loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            except Exception as e:
                logger.warning(f"Could not load existing graph: {e}")
                logger.info("Initializing empty graph")
                self.graph = nx.DiGraph()
        else:
            logger.info("No existing graph found, initializing empty graph")
            self.graph = nx.DiGraph()
    
    def export_graph(self, format: str = 'graphml', filename: Optional[str] = None) -> str:
        """
        Export the graph in various formats.
        
        Args:
            format: Export format ('graphml', 'json', 'gexf', 'gml')
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        logger.info(f"Exporting graph in {format} format")
        
        if filename is None:
            filename = f"export.{format}"
        
        export_path = self.storage_path / filename
        logger.debug(f"Export path: {export_path}")
        
        try:
            if format == 'graphml':
                nx.write_graphml(self.graph, export_path)
            elif format == 'json':
                graph_data = nx.node_link_data(self.graph, edges="links")
                with open(export_path, 'w') as f:
                    json.dump(graph_data, f, indent=2)
            elif format == 'gexf':
                nx.write_gexf(self.graph, export_path)
            elif format == 'gml':
                nx.write_gml(self.graph, export_path)
            else:
                logger.error(f"Unsupported export format: {format}")
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Successfully exported graph to {export_path}")
            return str(export_path)
            
        except Exception as e:
            logger.error(f"Failed to export graph in {format} format: {e}")
            raise
    
    def import_graph(self, file_path: str, format: str = 'auto') -> None:
        """
        Import a graph from a file.
        
        Args:
            file_path: Path to the file to import
            format: File format ('graphml', 'json', 'gexf', 'gml', 'auto')
        """
        logger.info(f"Importing graph from {file_path} in {format} format")
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"Import file not found: {file_path}")
            raise FileNotFoundError(f"Import file not found: {file_path}")
        
        if format == 'auto':
            format = file_path.suffix[1:]  # Remove the dot
            logger.debug(f"Auto-detected format: {format}")
        
        try:
            if format == 'graphml':
                self.graph = nx.read_graphml(file_path)
            elif format == 'json':
                with open(file_path, 'r') as f:
                    graph_data = json.load(f)
                self.graph = nx.node_link_graph(graph_data, edges="links")
            elif format == 'gexf':
                self.graph = nx.read_gexf(file_path)
            elif format == 'gml':
                self.graph = nx.read_gml(file_path)
            else:
                logger.error(f"Unsupported import format: {format}")
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Successfully imported graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            
            # Save the imported graph
            self._save_graph()
            
        except Exception as e:
            logger.error(f"Failed to import graph from {file_path}: {e}")
            raise
    
    def clear_graph(self) -> None:
        """Clear all entities and relationships."""
        logger.info("Clearing all entities and relationships from graph")
        nodes_count = self.graph.number_of_nodes()
        edges_count = self.graph.number_of_edges()
        
        self.graph.clear()
        logger.info(f"Cleared {nodes_count} nodes and {edges_count} edges")
        
        self._save_graph()
        logger.info("Graph cleared and saved")
    
    def get_graph_statistics(self) -> str:
        """
        Get detailed graph statistics.
        
        Returns:
            JSON string containing graph statistics
        """
        stats = {
            'basic': {
                'nodes': self.graph.number_of_nodes(),
                'edges': self.graph.number_of_edges(),
                'is_directed': self.graph.is_directed(),
                'is_multigraph': self.graph.is_multigraph()
            },
            'connectivity': {
                'is_connected': nx.is_weakly_connected(self.graph) if self.graph.is_directed() else nx.is_connected(self.graph),
                'number_of_components': nx.number_weakly_connected_components(self.graph) if self.graph.is_directed() else nx.number_connected_components(self.graph)
            },
            'centrality': {}
        }
        
        if self.graph.number_of_nodes() > 0:
            # Calculate centrality measures
            try:
                stats['centrality']['degree_centrality'] = dict(nx.degree_centrality(self.graph))
                if self.graph.is_directed():
                    stats['centrality']['in_degree_centrality'] = dict(nx.in_degree_centrality(self.graph))
                    stats['centrality']['out_degree_centrality'] = dict(nx.out_degree_centrality(self.graph))
            except Exception as e:
                stats['centrality']['error'] = str(e)
        
        return json.dumps(stats, indent=2)
    
    @contextmanager
    def transaction(self):
        """
        Context manager for transaction support.
        
        Usage:
            with service.transaction():
                service.create_entity("project", project_data)
                service.create_relationship(user_id, project_id, "assigned_to")
        """
        logger.info("Starting transaction")
        # Save current state
        original_graph = self.graph.copy()
        original_nodes = self.graph.number_of_nodes()
        original_edges = self.graph.number_of_edges()
        self._in_transaction = True
        
        try:
            logger.debug("Transaction active, yielding control")
            yield self
            # Transaction successful, save changes
            logger.info("Transaction completed successfully, saving changes")
            self._save_graph()
            logger.info(f"Transaction committed: {self.graph.number_of_nodes() - original_nodes} nodes and {self.graph.number_of_edges() - original_edges} edges added")
        except Exception as e:
            # Transaction failed, rollback
            logger.error(f"Transaction failed, rolling back: {e}")
            self.graph = original_graph
            logger.info("Transaction rolled back to original state")
            raise e
        finally:
            self._in_transaction = False
            logger.debug("Transaction ended")
    
    def execute_transaction(self, operations: List[Callable]) -> Dict[str, Any]:
        """
        Execute a list of operations as a single transaction.
        
        Args:
            operations: List of callable operations to execute
            
        Returns:
            Dictionary with results and status
        """
        logger.info(f"Executing transaction with {len(operations)} operations")
        results = []
        original_graph = self.graph.copy()
        original_nodes = self.graph.number_of_nodes()
        original_edges = self.graph.number_of_edges()
        
        try:
            for i, operation in enumerate(operations):
                logger.debug(f"Executing operation {i + 1}/{len(operations)}")
                result = operation()
                results.append({
                    'operation_index': i,
                    'result': result,
                    'status': 'success'
                })
                logger.debug(f"Operation {i + 1} completed successfully")
            
            # All operations successful, save changes
            logger.info("All operations completed successfully, saving changes")
            self._save_graph()
            
            final_nodes = self.graph.number_of_nodes()
            final_edges = self.graph.number_of_edges()
            logger.info(f"Transaction committed: {final_nodes - original_nodes} nodes and {final_edges - original_edges} edges added")
            
            return {
                'status': 'success',
                'operations_executed': len(operations),
                'results': results
            }
            
        except Exception as e:
            # Rollback on any failure
            logger.error(f"Transaction failed at operation {len(results) + 1}, rolling back: {e}")
            self.graph = original_graph
            logger.info("Transaction rolled back to original state")
            return {
                'status': 'failed',
                'error': str(e),
                'operations_executed': len(results),
                'results': results
            }
