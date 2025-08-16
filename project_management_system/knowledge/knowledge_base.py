import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..models.data_models import ProjectContext, AgentRole


class KnowledgeBase:
    """Gestisce la knowledge base in formato JSON-LD"""
    
    def __init__(self, kb_path: str = "knowledge/knowledge_base.jsonld"):
        self.kb_path = Path(kb_path)
        self.context = {
            "@context": {
                "@vocab": "https://projectmanagement.org/vocab/",
                "name": "http://schema.org/name",
                "description": "http://schema.org/description",
                "type": "@type",
                "hasObjective": "hasObjective",
                "hasStakeholder": "hasStakeholder",
                "hasConstraint": "hasConstraint",
                "dependsOn": "dependsOn",
                "involves": "involves"
            },
            "@graph": []
        }
        self._load_or_create_kb()
    
    def _load_or_create_kb(self):
        """Carica la KB esistente o crea una nuova"""
        if self.kb_path.exists():
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                self.context = json.load(f)
        else:
            self._initialize_default_kb()
            self.save()
    
    def _initialize_default_kb(self):
        """Inizializza la KB con entità e relazioni di base"""
        default_entities = [
            {
                "@id": "pm:ProjectManagement",
                "type": "Domain",
                "name": "Project Management",
                "description": "Domain of project planning, execution and control"
            },
            {
                "@id": "pm:Agile",
                "type": "Methodology", 
                "name": "Agile",
                "description": "Iterative development methodology",
                "hasPhase": ["pm:Sprint", "pm:Retrospective", "pm:Planning"]
            },
            {
                "@id": "pm:Waterfall",
                "type": "Methodology",
                "name": "Waterfall", 
                "description": "Sequential development methodology",
                "hasPhase": ["pm:Requirements", "pm:Design", "pm:Implementation", "pm:Testing", "pm:Deployment"]
            },
            {
                "@id": "pm:ProjectCharter",
                "type": "DocumentTemplate",
                "name": "Project Charter",
                "description": "Document that formally authorizes a project",
                "hasSection": ["pm:ProjectObjective", "pm:Scope", "pm:Stakeholders", "pm:Budget", "pm:Timeline"]
            },
            {
                "@id": "pm:RequirementsDocument", 
                "type": "DocumentTemplate",
                "name": "Requirements Document",
                "description": "Detailed project requirements specification",
                "hasSection": ["pm:FunctionalRequirements", "pm:NonFunctionalRequirements", "pm:Constraints"]
            }
        ]
        
        self.context["@graph"] = default_entities
    
    def add_entity(self, entity: Dict[str, Any]):
        """Aggiunge una nuova entità alla KB"""
        if "@id" not in entity:
            raise ValueError("Entity must have @id field")
        
        # Rimuovi entità esistente con stesso ID
        self.context["@graph"] = [
            e for e in self.context["@graph"] 
            if e.get("@id") != entity["@id"]
        ]
        
        # Aggiungi nuova entità
        self.context["@graph"].append(entity)
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Recupera un'entità per ID"""
        for entity in self.context["@graph"]:
            if entity.get("@id") == entity_id:
                return entity
        return None
    
    def query_entities(self, entity_type: str = None, **filters) -> List[Dict[str, Any]]:
        """Query entità con filtri"""
        results = self.context["@graph"]
        
        if entity_type:
            results = [e for e in results if e.get("type") == entity_type]
        
        for key, value in filters.items():
            results = [e for e in results if e.get(key) == value]
        
        return results
    
    def get_methodologies(self) -> List[Dict[str, Any]]:
        """Recupera metodologie disponibili"""
        return self.query_entities(entity_type="Methodology")
    
    def get_document_templates(self) -> List[Dict[str, Any]]:
        """Recupera template documenti disponibili"""
        return self.query_entities(entity_type="DocumentTemplate")
    
    def add_project(self, project_context: ProjectContext):
        """Aggiunge un progetto alla KB"""
        project_entity = {
            "@id": f"project:{project_context.project_id}",
            "type": "Project",
            "name": project_context.project_name,
            "description": f"Project: {project_context.project_name}",
            "hasObjective": project_context.objectives,
            "hasStakeholder": project_context.stakeholders,
            "hasConstraint": project_context.constraints
        }
        
        if project_context.domain:
            project_entity["belongsToDomain"] = project_context.domain
        
        self.add_entity(project_entity)
    
    def save(self):
        """Salva la KB su file"""
        with open(self.kb_path, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, indent=2, ensure_ascii=False)
    
    def get_context_for_agent(self, agent_role: AgentRole, project_id: str = None) -> str:
        """Genera contesto specializzato per un agente"""
        context_parts = []
        
        # Contesto generale
        methodologies = self.get_methodologies()
        context_parts.append("Available Methodologies:")
        for method in methodologies:
            context_parts.append(f"- {method['name']}: {method.get('description', '')}")
        
        # Template documenti
        templates = self.get_document_templates()
        context_parts.append("\nDocument Templates:")
        for template in templates:
            context_parts.append(f"- {template['name']}: {template.get('description', '')}")
        
        # Contesto progetto specifico
        if project_id:
            project = self.get_entity(f"project:{project_id}")
            if project:
                context_parts.append(f"\nCurrent Project: {project['name']}")
                if "hasObjective" in project:
                    context_parts.append(f"Objectives: {', '.join(project['hasObjective'])}")
        
        return "\n".join(context_parts)
