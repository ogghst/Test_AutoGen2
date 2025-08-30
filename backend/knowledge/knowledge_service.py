from typing import Dict, List, Optional, Any, Type, Union
from pathlib import Path
import json
import uuid
from datetime import datetime
from config.logging_config import get_logger

from models.data_models import (
    Project, Epic, UserStory, Issue, Risk, Milestone, Deliverable,
    Team, Person, Stakeholder, Requirement, Backlog, Sprint,
    ChangeRequest, Baseline, TestCase, Phase, WorkStream,
    Documentation, Repository, Metric, CommunicationPlan, AIWorkProduct,
    Scope
)

from agents.tools import UUIDEncoder

class KnowledgeService:
    """Knowledge management service for LLM agents to access project context"""
    
    def __init__(self, storage_path: str = "../knowledge_base"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.logger = get_logger(__name__)
        
        # Entity type registry mapping string names to actual classes
        self.entity_types = {
            'Project': Project,
            'Epic': Epic,
            'UserStory': UserStory,
            'Issue': Issue,
            'Risk': Risk,
            'Milestone': Milestone,
            'Deliverable': Deliverable,
            'Team': Team,
            'Person': Person,
            'Stakeholder': Stakeholder,
            'Requirement': Requirement,
            'Backlog': Backlog,
            'Sprint': Sprint,
            'ChangeRequest': ChangeRequest,
            'Baseline': Baseline,
            'TestCase': TestCase,
            'Phase': Phase,
            'WorkStream': WorkStream,
            'Documentation': Documentation,
            'Repository': Repository,
            'Metric': Metric,
            'CommunicationPlan': CommunicationPlan,
            'AIWorkProduct': AIWorkProduct,
            'Scope': Scope
        }
        
    def get_entity_types(self) -> List[str]:
        """
        Get the list of entity types
        """
        # Return a list of dicts with entity type and description from class docstring
        entity_info = []
        for entity_name, entity_cls in self.entity_types.items():
            description = (entity_cls.__doc__ or "").strip()
            entity_info.append({
                "type": entity_name,
                "description": description
            })
        return entity_info
    
    def get_full_project_context(self, project_id: str) -> str:
        """
        Feature 2: Return the full context (Project class and its relationships)
        Returns JSON string representation of project with all related entities
        """
        try:
            # Load project data
            project_data = self._load_entity_data("Project", project_id)
            if not project_data:
                return json.dumps({"error": f"Project {project_id} not found"})
            
            # Load all related entities
            full_context = self._build_full_project_context(project_data)
            
            return json.dumps(full_context, indent=2, cls=UUIDEncoder)
            
        except Exception as e:
            self.logger.error(f"Error getting full project context: {e}")
            return json.dumps({"error": f"Failed to get project context: {str(e)}"})
    
    def get_entity_by_id(self, entity_type: str, entity_id: str, include_relationships: bool = False) -> str:
        """
        Feature 3: Return a specific entity by ID, without relationships
        Feature 7: Return a specific entity by ID, with relationships
        """
        try:
            if entity_type not in self.entity_types:
                return json.dumps({"error": f"Unknown entity type: {entity_type}"})
            
            entity_data = self._load_entity_data(entity_type, entity_id)
            if not entity_data:
                return json.dumps({"error": f"{entity_type} {entity_id} not found"})
            
            if include_relationships:
                # Load related entities
                entity_data = self._load_entity_with_relationships(entity_type, entity_data)
            
            return json.dumps(entity_data, indent=2, cls=UUIDEncoder)
            
        except Exception as e:
            self.logger.error(f"Error getting entity {entity_type} {entity_id}: {e}")
            return json.dumps({"error": f"Failed to get entity: {str(e)}"})
    
    def create_entity(self, entity_type: str, entity_data_json: str) -> str:
        """
        Feature 4: Create a specific entity without ID, returning the generated ID
        """
        try:
            if entity_type not in self.entity_types:
                return json.dumps({"error": f"Unknown entity type: {entity_type}"})
            
            # Parse JSON input
            entity_data = json.loads(entity_data_json)
            
            # Generate UUID
            entity_id = str(uuid.uuid4())
            entity_data['id'] = entity_id
            
            # Validate and create entity instance
            entity_class = self.entity_types[entity_type]
            
            # Set timestamps only if the model supports them
            current_time = datetime.now().isoformat()
            
            # Check if the entity class has timestamp fields
            if hasattr(entity_class, 'model_fields'):
                if 'created_date' in entity_class.model_fields:
                    entity_data['created_date'] = current_time
                if 'last_updated' in entity_class.model_fields:
                    entity_data['last_updated'] = current_time
            entity_instance = entity_class(**entity_data)
            
            # Store entity
            self._store_entity(entity_type, entity_id, entity_instance)
            
            # Update relationships if this entity references others
            self._update_relationships(entity_instance)
            
            result = {
                "success": True,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "message": f"{entity_type} created successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error creating entity {entity_type}: {e}")
            return json.dumps({"error": f"Failed to create entity: {str(e)}"})
    
    def update_entity(self, entity_type: str, entity_id: str, updates_json: str) -> str:
        """
        Feature 5: Update a specific entity by ID
        """
        try:
            if entity_type not in self.entity_types:
                return json.dumps({"error": f"Unknown entity type: {entity_type}"})
            
            # Load existing entity
            entity_data = self._load_entity_data(entity_type, entity_id)
            if not entity_data:
                return json.dumps({"error": f"{entity_type} {entity_id} not found"})
            
            # Parse updates JSON
            updates = json.loads(updates_json)
            
            # Update entity data
            entity_data.update(updates)
            
            # Set last_updated only if the model supports it
            if hasattr(entity_class, 'model_fields') and 'last_updated' in entity_class.model_fields:
                entity_data['last_updated'] = datetime.now().isoformat()
            
            # Validate and create updated entity instance
            entity_class = self.entity_types[entity_type]
            updated_entity = entity_class(**entity_data)
            
            # Store updated entity
            self._store_entity(entity_type, entity_id, updated_entity)
            
            # Update relationships if needed
            self._update_relationships(updated_entity)
            
            result = {
                "success": True,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "message": f"{entity_type} updated successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error updating entity {entity_type} {entity_id}: {e}")
            return json.dumps({"error": f"Failed to update entity: {str(e)}"})
    
    def delete_entity(self, entity_type: str, entity_id: str) -> str:
        """
        Feature 6: Delete a specific entity
        """
        try:
            if entity_type not in self.entity_types:
                return json.dumps({"error": f"Unknown entity type: {entity_type}"})
            
            # Check if entity exists
            entity_data = self._load_entity_data(entity_type, entity_id)
            if not entity_data:
                return json.dumps({"error": f"{entity_type} {entity_id} not found"})
            
            # Remove from storage
            self._remove_entity(entity_type, entity_id)
            
            # Clean up relationships (remove references to this entity)
            self._cleanup_relationships(entity_type, entity_id)
            
            result = {
                "success": True,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "message": f"{entity_type} deleted successfully"
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error deleting entity {entity_type} {entity_id}: {e}")
            return json.dumps({"error": f"Failed to delete entity: {str(e)}"})
    
    def query_entities(self, entity_type: str, filters_json: str = "{}") -> str:
        """
        Additional utility: Query entities with filters
        """
        try:
            if entity_type not in self.entity_types:
                return json.dumps({"error": f"Unknown entity type: {entity_type}"})
            
            filters = json.loads(filters_json)
            entities_data = self._load_all_entities(entity_type)
            
            # Apply filters
            if filters:
                entities_data = self._apply_filters(entities_data, filters)
            
            return json.dumps(entities_data, indent=2, cls=UUIDEncoder)
            
        except Exception as e:
            self.logger.error(f"Error querying entities {entity_type}: {e}")
            return json.dumps({"error": f"Failed to query entities: {str(e)}"})
    
    # Private helper methods
    def _build_full_project_context(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build full project context with all related entities"""
        full_context = project_data.copy()
        
        # Load related entities
        if project_data.get("epics"):
            full_context["epics"] = self._load_entities_by_ids("Epic", project_data["epics"])
        
        if project_data.get("team"):
            full_context["team"] = self._load_entity_data("Team", project_data["team"])
        
        if project_data.get("risks"):
            full_context["risks"] = self._load_entities_by_ids("Risk", project_data["risks"])
        
        if project_data.get("milestones"):
            full_context["milestones"] = self._load_entities_by_ids("Milestone", project_data["milestones"])
        
        if project_data.get("stakeholders"):
            full_context["stakeholders"] = self._load_entities_by_ids("Stakeholder", project_data["stakeholders"])
        
        if project_data.get("scope"):
            full_context["scope"] = self._load_entity_data("Scope", project_data["scope"])
        
        return full_context
    
    def _load_entity_with_relationships(self, entity_type: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Load entity with its related entities"""
        entity_with_relations = entity_data.copy()
        
        # Load related entities based on entity type
        if entity_type == "Epic" and entity_data.get("user_stories"):
            entity_with_relations["user_stories"] = self._load_entities_by_ids("UserStory", entity_data["user_stories"])
        
        elif entity_type == "UserStory" and entity_data.get("epic_id"):
            entity_with_relations["epic"] = self._load_entity_data("Epic", entity_data["epic_id"])
        
        elif entity_type == "Team" and entity_data.get("members"):
            entity_with_relations["members"] = self._load_entities_by_ids("TeamMember", entity_data["members"])
        
        return entity_with_relations
    
    def _load_entities_by_ids(self, entity_type: str, entity_ids: List[str]) -> List[Dict[str, Any]]:
        """Load multiple entities by their IDs"""
        entities = []
        for entity_id in entity_ids:
            entity_data = self._load_entity_data(entity_type, entity_id)
            if entity_data:
                entities.append(entity_data)
        return entities
    
    def _apply_filters(self, entities: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to entities"""
        filtered_entities = []
        
        for entity in entities:
            matches = True
            for field, value in filters.items():
                if field not in entity or entity[field] != value:
                    matches = False
                    break
            
            if matches:
                filtered_entities.append(entity)
        
        return filtered_entities
    
    def _update_relationships(self, entity: Any):
        """Update relationships when entity is created/updated"""
        # Implementation for maintaining relationship integrity
        pass
    
    def _cleanup_relationships(self, entity_type: str, entity_id: str):
        """Clean up relationships when entity is deleted"""
        # Implementation for cleaning up references
        pass
    
    def _store_entity(self, entity_type: str, entity_id: str, entity: Any):
        """Store entity to persistent storage"""
        entity_file = self.storage_path / f"{entity_type.lower()}" / f"{entity_id}.json"
        entity_file.parent.mkdir(exist_ok=True)
        
        with open(entity_file, 'w', encoding='utf-8') as f:
            json.dump(entity.model_dump(), f, indent=2, cls=UUIDEncoder)
    
    def _load_entity_data(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Load entity data from storage"""
        entity_file = self.storage_path / f"{entity_type.lower()}" / f"{entity_id}.json"
        
        if not entity_file.exists():
            return None
        
        with open(entity_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_all_entities(self, entity_type: str) -> List[Dict[str, Any]]:
        """Load all entities of a specific type"""
        entity_dir = self.storage_path / f"{entity_type.lower()}"
        
        if not entity_dir.exists():
            return []
        
        entities = []
        for entity_file in entity_dir.glob("*.json"):
            try:
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entities.append(json.load(f))
            except Exception as e:
                self.logger.warning(f"Failed to load {entity_file}: {e}")
        
        return entities
    
    def _remove_entity(self, entity_type: str, entity_id: str):
        """Remove entity from storage"""
        entity_file = self.storage_path / f"{entity_type.lower()}" / f"{entity_id}.json"
        if entity_file.exists():
            entity_file.unlink()
