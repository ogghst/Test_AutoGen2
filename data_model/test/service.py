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

# Import the generated models
try:
    from .test import Project, User, Issue, Edge, ConfiguredBaseModel
except ImportError:
    from test import Project, User, Issue, Edge, ConfiguredBaseModel


class EntityService:
    """Generic service for entity and relationship management."""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the service with optional storage path.
        
        Args:
            storage_path: Path to store graph data files
        """
        self.storage_path = Path(storage_path) if storage_path else Path("data_model/test/storage")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize NetworkX graph
        self.graph = nx.DiGraph()
        
        # Entity type mapping
        self.entity_types = {
            'project': Project,
            'user': User,
            'issue': Issue,
            'edge': Edge
        }
        
        # Load existing data if available
        self._load_graph()
        
        # Transaction support
        self._transaction_stack = []
        self._in_transaction = False
    
    def _get_entity_class(self, entity_type: str) -> Type[ConfiguredBaseModel]:
        """Get the Pydantic model class for the given entity type."""
        entity_type = entity_type.lower()
        if entity_type not in self.entity_types:
            raise ValueError(f"Unknown entity type: {entity_type}. Available types: {list(self.entity_types.keys())}")
        return self.entity_types[entity_type]
    
    def _validate_json_input(self, json_data: str, entity_type: str, generate_id: bool = False) -> Dict[str, Any]:
        """Validate and parse JSON input."""
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        
        # Generate ID if requested and not provided
        if generate_id and ('id' not in data or not data['id']):
            data['id'] = self._generate_id()
        
        entity_class = self._get_entity_class(entity_type)
        try:
            # Validate using Pydantic
            validated_entity = entity_class(**data)
            return validated_entity.model_dump()
        except ValidationError as e:
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
        validated_data = self._validate_json_input(json_data, entity_type, generate_id=True)
        
        # Add to NetworkX graph
        self.graph.add_node(validated_data['id'], **validated_data)
        
        # Save to file (only if not in transaction)
        if not self._in_transaction:
            self._save_graph()
        
        return json.dumps(validated_data)
    
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
        
        # Search for existing entity with matching unique fields
        existing_entity_id = self._find_entity_by_unique_fields(entity_type, validated_data, unique_fields)
        
        if existing_entity_id:
            # Update existing entity
            validated_data['id'] = existing_entity_id
            self.graph.nodes[existing_entity_id].update(validated_data)
            
            # Save to file (only if not in transaction)
            if not self._in_transaction:
                self._save_graph()
            
            return json.dumps(validated_data)
        else:
            # Create new entity
            return self.create_entity(entity_type, json_data)
    
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
        if not self.graph.has_node(entity_id):
            return None
        
        entity_data = self.graph.nodes[entity_id]
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
        if not self.graph.has_node(entity_id):
            return None
        
        validated_data = self._validate_json_input(json_data, entity_type)
        
        # Ensure ID matches
        validated_data['id'] = entity_id
        
        # Update in NetworkX graph
        self.graph.nodes[entity_id].update(validated_data)
        
        # Save to file (only if not in transaction)
        if not self._in_transaction:
            self._save_graph()
        
        return json.dumps(validated_data)
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity and all its relationships.
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if deleted, False if not found
        """
        if not self.graph.has_node(entity_id):
            return False
        
        # Remove all edges connected to this node
        edges_to_remove = list(self.graph.edges(entity_id, data=True))
        edges_to_remove.extend(list(self.graph.in_edges(entity_id, data=True)))
        
        for edge in edges_to_remove:
            self.graph.remove_edge(edge[0], edge[1])
        
        # Remove the node
        self.graph.remove_node(entity_id)
        
        # Save to file (only if not in transaction)
        if not self._in_transaction:
            self._save_graph()
        
        return True
    
    def list_entities(self, entity_type: Optional[str] = None) -> str:
        """
        List all entities, optionally filtered by type.
        
        Args:
            entity_type: Optional entity type filter
            
        Returns:
            JSON string containing list of entities
        """
        entities = []
        
        for node_id, data in self.graph.nodes(data=True):
            if entity_type is None or data.get('__type__') == entity_type:
                entities.append(data)
        
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
        # Validate that both nodes exist
        if not self.graph.has_node(source_id):
            raise ValueError(f"Source entity {source_id} not found")
        if not self.graph.has_node(target_id):
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
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid additional data JSON: {e}")
        
        # Validate using Edge model
        try:
            validated_edge = Edge(**edge_data)
            edge_data = validated_edge.model_dump()
        except ValidationError as e:
            raise ValueError(f"Edge validation error: {e}")
        
        # Add edge to graph
        self.graph.add_edge(source_id, target_id, **edge_data)
        
        # Save to file (only if not in transaction)
        if not self._in_transaction:
            self._save_graph()
        
        return json.dumps(edge_data)
    
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
        relationships = []
        
        if entity_id:
            if direction in ['out', 'both']:
                for source, target, data in self.graph.out_edges(entity_id, data=True):
                    relationships.append(data)
            
            if direction in ['in', 'both']:
                for source, target, data in self.graph.in_edges(entity_id, data=True):
                    relationships.append(data)
        else:
            # Get all edges
            for source, target, data in self.graph.edges(data=True):
                relationships.append(data)
        
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
        if entity_type not in self.entity_types:
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
        
        query_lower = query.lower()
        matching_entities = []
        
        for node_id, data in self.graph.nodes(data=True):
            # Check if this node matches the entity type
            if self._is_entity_of_type(data, entity_type):
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
                            break  # Found a match, no need to check other fields
        
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
        if not self.graph.has_node(entity_id):
            raise ValueError(f"Entity {entity_id} not found")
        
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
        
        # Create subgraph
        subgraph = self.graph.subgraph(subgraph_nodes)
        
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
        
        return json.dumps(result, indent=2)
    
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
        if not self.graph.has_edge(source_id, target_id):
            return False
        
        self.graph.remove_edge(source_id, target_id)
        
        # Save to file (only if not in transaction)
        if not self._in_transaction:
            self._save_graph()
        return True
    
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
    
    def _save_graph(self) -> None:
        """Save the graph to files."""
        # Save as GraphML
        graphml_path = self.storage_path / "graph.graphml"
        nx.write_graphml(self.graph, graphml_path)
        
        # Save as JSON
        json_path = self.storage_path / "graph.json"
        graph_data = nx.node_link_data(self.graph)
        with open(json_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
    
    def _load_graph(self) -> None:
        """Load the graph from files."""
        json_path = self.storage_path / "graph.json"
        
        if json_path.exists():
            try:
                with open(json_path, 'r') as f:
                    graph_data = json.load(f)
                self.graph = nx.node_link_graph(graph_data)
            except Exception as e:
                print(f"Warning: Could not load existing graph: {e}")
                self.graph = nx.DiGraph()
        else:
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
        if filename is None:
            filename = f"export.{format}"
        
        export_path = self.storage_path / filename
        
        if format == 'graphml':
            nx.write_graphml(self.graph, export_path)
        elif format == 'json':
            graph_data = nx.node_link_data(self.graph)
            with open(export_path, 'w') as f:
                json.dump(graph_data, f, indent=2)
        elif format == 'gexf':
            nx.write_gexf(self.graph, export_path)
        elif format == 'gml':
            nx.write_gml(self.graph, export_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return str(export_path)
    
    def import_graph(self, file_path: str, format: str = 'auto') -> None:
        """
        Import a graph from a file.
        
        Args:
            file_path: Path to the file to import
            format: File format ('graphml', 'json', 'gexf', 'gml', 'auto')
        """
        file_path = Path(file_path)
        
        if format == 'auto':
            format = file_path.suffix[1:]  # Remove the dot
        
        if format == 'graphml':
            self.graph = nx.read_graphml(file_path)
        elif format == 'json':
            with open(file_path, 'r') as f:
                graph_data = json.load(f)
            self.graph = nx.node_link_graph(graph_data)
        elif format == 'gexf':
            self.graph = nx.read_gexf(file_path)
        elif format == 'gml':
            self.graph = nx.read_gml(file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Save the imported graph
        self._save_graph()
    
    def clear_graph(self) -> None:
        """Clear all entities and relationships."""
        self.graph.clear()
        self._save_graph()
    
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
        # Save current state
        original_graph = self.graph.copy()
        self._in_transaction = True
        
        try:
            yield self
            # Transaction successful, save changes
            self._save_graph()
        except Exception as e:
            # Transaction failed, rollback
            self.graph = original_graph
            raise e
        finally:
            self._in_transaction = False
    
    def execute_transaction(self, operations: List[Callable]) -> Dict[str, Any]:
        """
        Execute a list of operations as a single transaction.
        
        Args:
            operations: List of callable operations to execute
            
        Returns:
            Dictionary with results and status
        """
        results = []
        original_graph = self.graph.copy()
        
        try:
            for i, operation in enumerate(operations):
                result = operation()
                results.append({
                    'operation_index': i,
                    'result': result,
                    'status': 'success'
                })
            
            # All operations successful, save changes
            self._save_graph()
            
            return {
                'status': 'success',
                'operations_executed': len(operations),
                'results': results
            }
            
        except Exception as e:
            # Rollback on any failure
            self.graph = original_graph
            return {
                'status': 'failed',
                'error': str(e),
                'operations_executed': len(results),
                'results': results
            }
