"""
Knowledge Base per il sistema multi-agente
Gestisce entità, relazioni e contesto in formato JSON-LD
Fornisce API per query, aggiornamenti e reasoning contestuale
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Sequence
from datetime import datetime
from dataclasses import asdict

from models.data_models import (
    ProjectContext, AgentRole, Methodology, DocumentType, Priority,
    serialize_datetime, ValidationError
)

# Import logging configuration
from config.logging_config import get_logger

# AutoGen compatibility imports
try:
    from autogen_agentchat.messages import BaseChatMessage
    AUTOGEN_AVAILABLE = True
except ImportError:
    BaseChatMessage = Any
    AUTOGEN_AVAILABLE = False


# ============================================================================
# LOGGER SETUP
# ============================================================================

logger = get_logger(__name__)


# ============================================================================
# KNOWLEDGE BASE EXCEPTIONS
# ============================================================================

class KnowledgeBaseError(Exception):
    """Eccezione base per errori della knowledge base"""
    pass


class EntityNotFoundError(KnowledgeBaseError):
    """Entità non trovata nella knowledge base"""
    pass


class InvalidEntityError(KnowledgeBaseError):
    """Entità non valida o malformata"""
    pass


class QueryError(KnowledgeBaseError):
    """Errore nell'esecuzione di query"""
    pass


# ============================================================================
# KNOWLEDGE BASE CORE
# ============================================================================

class KnowledgeBase:
    """
    Knowledge Base principale del sistema
    Gestisce entità, relazioni e contesto in formato JSON-LD
    """
    
    def __init__(self, kb_path: str = "knowledge_base.jsonld", auto_save: bool = True):
        """
        Inizializza la Knowledge Base
        
        Args:
            kb_path: Path del file JSON-LD
            auto_save: Se True, salva automaticamente le modifiche
        """
        self.kb_path = Path(kb_path)
        self.auto_save = auto_save
        self.context = {
            "@context": self._create_jsonld_context(),
            "@graph": [],
            "metadata": {
                "version": "1.0.0",
                "created_at": serialize_datetime(datetime.now()),
                "last_updated": serialize_datetime(datetime.now()),
                "entity_count": 0,
                "schema_version": "2024.1"
            }
        }
        
        # Cache per performance
        self._entity_cache: Dict[str, Dict[str, Any]] = {}
        self._relationship_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._dirty = False  # Flag per modifiche non salvate
        
        # Inizializza KB
        self._load_or_create_kb()
        
        logger.info(f"Knowledge Base inizializzata: {self.kb_path}")
    
    def _create_jsonld_context(self) -> Dict[str, Any]:
        """Crea il contesto JSON-LD con vocabulario del dominio"""
        return {
            "@vocab": "https://projectmanagement.org/vocab/",
            "name": "http://schema.org/name",
            "description": "http://schema.org/description",
            "type": "@type",
            "id": "@id",
            
            # Project Management vocabulary
            "hasObjective": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasStakeholder": {
                "@type": "@id", 
                "@container": "@set"
            },
            "hasConstraint": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasRequirement": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasTask": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasPhase": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasDeliverable": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasRisk": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasTemplate": {
                "@type": "@id",
                "@container": "@set"
            },
            "hasBestPractice": {
                "@type": "@id",
                "@container": "@set"
            },
            
            # Relations
            "dependsOn": {
                "@type": "@id",
                "@container": "@set"
            },
            "involves": {
                "@type": "@id",
                "@container": "@set"
            },
            "belongsToDomain": "@id",
            "usesMethodology": "@id",
            "hasRole": "@id",
            "assignedTo": "@id",
            "relatedTo": {
                "@type": "@id",
                "@container": "@set"
            },
            
            # Properties
            "priority": "http://schema.org/priority",
            "startDate": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
            },
            "endDate": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
            },
            "createdAt": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
            },
            "updatedAt": {
                "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
            },
            "status": "http://schema.org/status",
            "methodology": "@id",
            "domain": "@id",
            "effort": "http://schema.org/duration",
            "budget": "http://schema.org/MonetaryAmount"
        }
    
    def _load_or_create_kb(self):
        """Carica KB esistente o crea una nuova con entità di default"""
        if self.kb_path.exists():
            try:
                self._load_from_file()
                logger.info(f"Knowledge Base caricata: {len(self.context['@graph'])} entità")
            except Exception as e:
                logger.error(f"Errore caricamento KB: {e}")
                logger.info("Inizializzazione KB di default...")
                self._initialize_default_kb()
        else:
            self._initialize_default_kb()
            
        self._rebuild_cache()
    
    def _load_from_file(self):
        """Carica KB da file JSON-LD"""
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            loaded_context = json.load(f)
            
        # Validate structure
        if "@context" not in loaded_context or "@graph" not in loaded_context:
            raise KnowledgeBaseError("Invalid JSON-LD structure")
            
        self.context = loaded_context
        
        # Update metadata
        if "metadata" not in self.context:
            self.context["metadata"] = {}
        self.context["metadata"]["last_loaded"] = serialize_datetime(datetime.now())
        self.context["metadata"]["entity_count"] = len(self.context["@graph"])
    
    def _initialize_default_kb(self):
        """Inizializza KB con entità di default per project management"""
        default_entities = [
            # === DOMAINS ===
            {
                "@id": "domain:ProjectManagement",
                "type": "Domain",
                "name": "Project Management",
                "description": "Discipline of planning, executing, and controlling projects to achieve specific goals",
                "hasSubdomain": ["domain:SoftwareDevelopment", "domain:ITProjects", "domain:BusinessTransformation"]
            },
            {
                "@id": "domain:SoftwareDevelopment", 
                "type": "Domain",
                "name": "Software Development",
                "description": "Domain focused on creating software applications and systems",
                "belongsToDomain": "domain:ProjectManagement"
            },
            {
                "@id": "domain:ITProjects",
                "type": "Domain", 
                "name": "IT Projects",
                "description": "Information Technology project management and implementation",
                "belongsToDomain": "domain:ProjectManagement"
            },
            
            # === METHODOLOGIES ===
            {
                "@id": "methodology:Agile",
                "type": "Methodology",
                "name": "Agile",
                "description": "Iterative and incremental development methodology emphasizing collaboration and flexibility",
                "hasPhase": [
                    "phase:ProjectInitiation",
                    "phase:Sprint", 
                    "phase:Review",
                    "phase:Retrospective",
                    "phase:Release"
                ],
                "hasBestPractice": [
                    "practice:DailyStandups",
                    "practice:SprintPlanning", 
                    "practice:UserStories",
                    "practice:ContinuousIntegration"
                ],
                "hasRole": [
                    "role:ScrumMaster",
                    "role:ProductOwner", 
                    "role:DevelopmentTeam"
                ]
            },
            {
                "@id": "methodology:Waterfall",
                "type": "Methodology",
                "name": "Waterfall",
                "description": "Sequential development methodology with distinct phases",
                "hasPhase": [
                    "phase:Requirements",
                    "phase:Design", 
                    "phase:Implementation",
                    "phase:Testing",
                    "phase:Deployment",
                    "phase:Maintenance"
                ],
                "hasBestPractice": [
                    "practice:DetailedPlanning",
                    "practice:DocumentationFirst",
                    "practice:PhaseGateReviews"
                ]
            },
            {
                "@id": "methodology:Scrum",
                "type": "Methodology",
                "name": "Scrum", 
                "description": "Agile framework for managing product development with fixed-length sprints",
                "belongsToDomain": "methodology:Agile",
                "hasPhase": [
                    "phase:SprintPlanning",
                    "phase:Sprint",
                    "phase:SprintReview",
                    "phase:SprintRetrospective"
                ],
                "hasDeliverable": [
                    "deliverable:ProductBacklog",
                    "deliverable:SprintBacklog",
                    "deliverable:ProductIncrement"
                ]
            },
            
            # === DOCUMENT TEMPLATES ===
            {
                "@id": "template:ProjectCharter",
                "type": "DocumentTemplate",
                "name": "Project Charter", 
                "description": "Document that formally authorizes a project and defines its scope, objectives, and stakeholders",
                "hasSection": [
                    "section:ExecutiveSummary",
                    "section:ProjectObjectives",
                    "section:Scope",
                    "section:Stakeholders",
                    "section:Budget",
                    "section:Timeline",
                    "section:RiskAssessment",
                    "section:SuccessCriteria"
                ],
                "requiredFor": ["methodology:Waterfall", "methodology:Agile"],
                "priority": "critical"
            },
            {
                "@id": "template:RequirementsDocument",
                "type": "DocumentTemplate", 
                "name": "Requirements Document",
                "description": "Comprehensive specification of functional and non-functional requirements",
                "hasSection": [
                    "section:Introduction",
                    "section:FunctionalRequirements",
                    "section:NonFunctionalRequirements", 
                    "section:Constraints",
                    "section:Assumptions",
                    "section:AcceptanceCriteria"
                ],
                "dependsOn": ["template:ProjectCharter"]
            },
            {
                "@id": "template:TechnicalSpecification",
                "type": "DocumentTemplate",
                "name": "Technical Specification",
                "description": "Detailed technical design and architecture documentation",
                "hasSection": [
                    "section:Architecture",
                    "section:SystemDesign",
                    "section:DatabaseDesign",
                    "section:APISpecification",
                    "section:SecurityConsiderations",
                    "section:PerformanceRequirements"
                ],
                "dependsOn": ["template:RequirementsDocument"]
            },
            {
                "@id": "template:ProjectPlan",
                "type": "DocumentTemplate",
                "name": "Project Plan",
                "description": "Comprehensive plan outlining project phases, tasks, resources, and timeline",
                "hasSection": [
                    "section:WorkBreakdownStructure",
                    "section:Timeline",
                    "section:ResourceAllocation", 
                    "section:RiskManagement",
                    "section:CommunicationPlan",
                    "section:QualityAssurance"
                ]
            },
            
            # === BEST PRACTICES ===
            {
                "@id": "practice:RequirementsTraceability",
                "type": "BestPractice",
                "name": "Requirements Traceability",
                "description": "Maintain traceability between requirements, design, and implementation",
                "applicableFor": ["methodology:Waterfall", "methodology:Agile"],
                "benefit": "Ensures all requirements are addressed and enables impact analysis"
            },
            {
                "@id": "practice:VersionControl",
                "type": "BestPractice", 
                "name": "Version Control",
                "description": "Use version control systems for all project artifacts",
                "applicableFor": ["domain:SoftwareDevelopment"],
                "hasTemplate": ["template:ChangeLog"]
            },
            {
                "@id": "practice:ContinuousIntegration",
                "type": "BestPractice",
                "name": "Continuous Integration",
                "description": "Automatically integrate code changes and run tests frequently",
                "applicableFor": ["methodology:Agile", "methodology:Scrum"],
                "relatedTo": ["practice:AutomatedTesting"]
            },
            
            # === ROLES ===
            {
                "@id": "role:ProjectManager",
                "type": "Role",
                "name": "Project Manager", 
                "description": "Responsible for planning, executing, and closing projects",
                "hasResponsibility": [
                    "Project planning and scheduling",
                    "Resource allocation and management",
                    "Risk identification and mitigation", 
                    "Stakeholder communication",
                    "Project monitoring and control"
                ],
                "hasTemplate": ["template:ProjectCharter", "template:ProjectPlan"]
            },
            {
                "@id": "role:RequirementsAnalyst",
                "type": "Role",
                "name": "Requirements Analyst",
                "description": "Responsible for gathering, analyzing, and documenting requirements",
                "hasResponsibility": [
                    "Requirements elicitation",
                    "Requirements analysis and validation",
                    "Requirements documentation", 
                    "Change management",
                    "Stakeholder engagement"
                ],
                "hasTemplate": ["template:RequirementsDocument"]
            },
            {
                "@id": "role:TechnicalWriter",
                "type": "Role",
                "name": "Technical Writer",
                "description": "Creates and maintains technical documentation",
                "hasTemplate": [
                    "template:TechnicalSpecification",
                    "template:APIDocumentation",
                    "template:DeploymentGuide"
                ]
            },
            
            # === PHASES ===
            {
                "@id": "phase:ProjectInitiation",
                "type": "Phase",
                "name": "Project Initiation",
                "description": "Initial phase where project is defined and authorized",
                "hasDeliverable": ["template:ProjectCharter"],
                "typicalDuration": "1-2 weeks",
                "hasActivity": [
                    "Define project objectives",
                    "Identify stakeholders",
                    "Conduct feasibility analysis",
                    "Create project charter"
                ]
            },
            {
                "@id": "phase:Planning",
                "type": "Phase", 
                "name": "Planning",
                "description": "Detailed planning of project scope, timeline, and resources",
                "dependsOn": ["phase:ProjectInitiation"],
                "hasDeliverable": ["template:ProjectPlan", "template:RequirementsDocument"],
                "hasActivity": [
                    "Create work breakdown structure",
                    "Estimate effort and duration",
                    "Allocate resources",
                    "Identify and assess risks"
                ]
            },
            
            # === RISK PATTERNS ===
            {
                "@id": "risk:ScopeCreep",
                "type": "RiskPattern",
                "name": "Scope Creep",
                "description": "Uncontrolled expansion of project scope without adjusting time, cost, and resources",
                "likelihood": "high",
                "impact": "high",
                "mitigation": [
                    "Clear scope definition",
                    "Change control process",
                    "Regular stakeholder communication"
                ]
            },
            {
                "@id": "risk:ResourceConstraints",
                "type": "RiskPattern",
                "name": "Resource Constraints",
                "description": "Insufficient human or technical resources to complete project",
                "likelihood": "medium", 
                "impact": "high",
                "mitigation": [
                    "Early resource planning",
                    "Resource leveling",
                    "Cross-training team members"
                ]
            }
        ]
        
        self.context["@graph"] = default_entities
        self.context["metadata"]["entity_count"] = len(default_entities)
        self.context["metadata"]["initialized_at"] = serialize_datetime(datetime.now())
        
        if self.auto_save:
            self.save()
        
        logger.info(f"KB inizializzata con {len(default_entities)} entità di default")
    
    def _rebuild_cache(self):
        """Ricostruisce cache per performance"""
        self._entity_cache.clear()
        self._relationship_cache.clear()
        
        for entity in self.context["@graph"]:
            entity_id = entity.get("@id")
            if entity_id:
                self._entity_cache[entity_id] = entity
                
                # Cache relationships
                for key, value in entity.items():
                    if key.startswith(("has", "belongs", "uses", "depends", "involves", "related")):
                        if isinstance(value, list):
                            for related_id in value:
                                if isinstance(related_id, str):
                                    if related_id not in self._relationship_cache:
                                        self._relationship_cache[related_id] = []
                                    self._relationship_cache[related_id].append({
                                        "source": entity_id,
                                        "relation": key,
                                        "target": related_id
                                    })
                        elif isinstance(value, str):
                            if value not in self._relationship_cache:
                                self._relationship_cache[value] = []
                            self._relationship_cache[value].append({
                                "source": entity_id,
                                "relation": key,
                                "target": value
                            })
        
        logger.debug(f"Cache ricostruita: {len(self._entity_cache)} entità, {len(self._relationship_cache)} relazioni")
    
    def save(self) -> bool:
        """
        Salva la KB su file
        
        Returns:
            bool: True se salvato con successo
        """
        try:
            # Update metadata
            self.context["metadata"]["last_updated"] = serialize_datetime(datetime.now())
            self.context["metadata"]["entity_count"] = len(self.context["@graph"])
            
            # Ensure parent directory exists
            self.kb_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with pretty formatting
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2, ensure_ascii=False)
            
            self._dirty = False
            logger.info(f"KB salvata: {self.kb_path}")
            return True
            
        except Exception as e:
            logger.error(f"Errore salvataggio KB: {e}")
            return False
    
    def add_entity(self, entity: Dict[str, Any]) -> str:
        """
        Aggiunge una nuova entità alla KB
        
        Args:
            entity: Dizionario rappresentante l'entità
            
        Returns:
            str: ID dell'entità aggiunta
            
        Raises:
            InvalidEntityError: Se l'entità non è valida
        """
        # Validate entity
        if "@id" not in entity:
            raise InvalidEntityError("Entity must have @id field")
        
        if "type" not in entity:
            raise InvalidEntityError("Entity must have type field")
        
        entity_id = entity["@id"]
        
        # Remove existing entity with same ID
        self.context["@graph"] = [
            e for e in self.context["@graph"] 
            if e.get("@id") != entity_id
        ]
        
        # Add timestamps if not present
        if "createdAt" not in entity:
            entity["createdAt"] = serialize_datetime(datetime.now())
        entity["updatedAt"] = serialize_datetime(datetime.now())
        
        # Add entity
        self.context["@graph"].append(entity)
        
        # Update cache
        self._entity_cache[entity_id] = entity
        self._dirty = True
        
        if self.auto_save:
            self.save()
        
        logger.debug(f"Entità aggiunta: {entity_id} ({entity.get('type')})")
        return entity_id
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un'entità per ID
        
        Args:
            entity_id: ID dell'entità
            
        Returns:
            Optional[Dict]: Entità o None se non trovata
        """
        return self._entity_cache.get(entity_id)
    
    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> bool:
        """
        Aggiorna un'entità esistente
        
        Args:
            entity_id: ID dell'entità da aggiornare
            updates: Dizionario con i campi da aggiornare
            
        Returns:
            bool: True se aggiornata con successo
            
        Raises:
            EntityNotFoundError: Se l'entità non esiste
        """
        entity = self.get_entity(entity_id)
        if not entity:
            raise EntityNotFoundError(f"Entity not found: {entity_id}")
        
        # Apply updates
        for key, value in updates.items():
            entity[key] = value
        
        entity["updatedAt"] = serialize_datetime(datetime.now())
        
        self._dirty = True
        if self.auto_save:
            self.save()
        
        logger.debug(f"Entità aggiornata: {entity_id}")
        return True
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Elimina un'entità dalla KB
        
        Args:
            entity_id: ID dell'entità da eliminare
            
        Returns:
            bool: True se eliminata con successo
        """
        original_count = len(self.context["@graph"])
        
        # Remove from graph
        self.context["@graph"] = [
            e for e in self.context["@graph"] 
            if e.get("@id") != entity_id
        ]
        
        # Remove from cache
        self._entity_cache.pop(entity_id, None)
        self._relationship_cache.pop(entity_id, None)
        
        deleted = len(self.context["@graph"]) < original_count
        
        if deleted:
            self._dirty = True
            if self.auto_save:
                self.save()
            logger.debug(f"Entità eliminata: {entity_id}")
        
        return deleted
    
    def query_entities(
        self, 
        entity_type: Optional[str] = None, 
        **filters
    ) -> List[Dict[str, Any]]:
        """
        Query entità con filtri
        
        Args:
            entity_type: Tipo di entità da filtrare
            **filters: Filtri aggiuntivi
            
        Returns:
            List[Dict]: Lista di entità che corrispondono ai filtri
        """
        results = list(self.context["@graph"])
        
        # Filter by type
        if entity_type:
            results = [e for e in results if e.get("type") == entity_type]
        
        # Apply additional filters
        for key, value in filters.items():
            if isinstance(value, (list, set)):
                # Match any value in list
                results = [
                    e for e in results 
                    if any(v in str(e.get(key, "")).lower() for v in value)
                ]
            else:
                # Exact match or contains
                results = [
                    e for e in results 
                    if str(value).lower() in str(e.get(key, "")).lower()
                ]
        
        return results
    
    def get_related_entities(
        self, 
        entity_id: str, 
        relation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Recupera entità correlate
        
        Args:
            entity_id: ID dell'entità di partenza
            relation_type: Tipo di relazione da seguire (opzionale)
            
        Returns:
            List[Dict]: Lista di entità correlate
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return []
        
        related_entities = []
        
        for key, value in entity.items():
            # Skip non-relation fields
            if not key.startswith(("has", "belongs", "uses", "depends", "involves", "related")):
                continue
            
            # Filter by relation type if specified
            if relation_type and key != relation_type:
                continue
            
            # Handle single values and lists
            values = value if isinstance(value, list) else [value]
            
            for related_id in values:
                if isinstance(related_id, str):
                    related_entity = self.get_entity(related_id)
                    if related_entity:
                        related_entities.append(related_entity)
        
        return related_entities
    
    def get_methodologies(self) -> List[Dict[str, Any]]:
        """Recupera tutte le metodologie disponibili"""
        return self.query_entities(entity_type="Methodology")
    
    def get_document_templates(self) -> List[Dict[str, Any]]:
        """Recupera tutti i template di documenti"""
        return self.query_entities(entity_type="DocumentTemplate")
    
    def get_best_practices(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Recupera best practices, opzionalmente filtrate per dominio
        
        Args:
            domain: Dominio per filtrare le best practices
            
        Returns:
            List[Dict]: Best practices applicabili
        """
        practices = self.query_entities(entity_type="BestPractice")
        
        if domain:
            # Filter by applicable domain
            filtered_practices = []
            for practice in practices:
                applicable_for = practice.get("applicableFor", [])
                if isinstance(applicable_for, str):
                    applicable_for = [applicable_for]
                
                if any(domain.lower() in app.lower() for app in applicable_for):
                    filtered_practices.append(practice)
            
            return filtered_practices
        
        return practices
    
    def get_risk_patterns(self) -> List[Dict[str, Any]]:
        """Recupera pattern di rischio noti"""
        return self.query_entities(entity_type="RiskPattern")
    
    def add_project(self, project_context: ProjectContext) -> str:
        """
        Aggiunge un progetto alla KB
        
        Args:
            project_context: Contesto del progetto
            
        Returns:
            str: ID dell'entità progetto creata
        """
        project_entity = {
            "@id": f"project:{project_context.project_id}",
            "type": "Project",
            "name": project_context.project_name,
            "description": project_context.description,
            "status": project_context.status.value,
            "priority": project_context.priority.value,
            "methodology": f"methodology:{project_context.methodology.value.title()}",
            "hasObjective": project_context.objectives,
            "hasStakeholder": project_context.stakeholders,
            "hasConstraint": project_context.constraints,
            "assumptions": project_context.assumptions,
            "timeline": project_context.timeline,
            "budget": project_context.budget,
            "createdAt": serialize_datetime(project_context.created_at),
            "updatedAt": serialize_datetime(project_context.updated_at)
        }
        
        if project_context.domain:
            project_entity["belongsToDomain"] = f"domain:{project_context.domain}"
        
        if project_context.team_members:
            project_entity["hasTeamMember"] = project_context.team_members
        
        if project_context.related_projects:
            project_entity["relatedTo"] = [
                f"project:{pid}" for pid in project_context.related_projects
            ]
        
        return self.add_entity(project_entity)
    
    def get_context_for_agent(
        self, 
        agent_role: AgentRole, 
        project_id: Optional[str] = None,
        message_history: Optional[Sequence[BaseChatMessage]] = None
    ) -> str:
        """
        Genera contesto specializzato per un agente compatibile con AutoGen 0.7+
        
        Args:
            agent_role: Ruolo dell'agente
            project_id: ID del progetto (opzionale)
            message_history: Cronologia messaggi per contesto dinamico
            
        Returns:
            str: Contesto formattato per l'agente
        """
        context_parts = []
        
        # Analizza cronologia messaggi per contesto dinamico
        recent_topics = []
        if AUTOGEN_AVAILABLE and message_history:
            # Estrae topic recenti dai messaggi
            for msg in message_history[-5:]:  # Ultimi 5 messaggi
                if hasattr(msg, 'content') and isinstance(msg.content, str):
                    if len(msg.content) > 10:  # Skip messaggi troppo corti
                        # Simple keyword extraction
                        content_lower = msg.content.lower()
                        for keyword in ['requirements', 'architecture', 'planning', 'testing', 'deployment']:
                            if keyword in content_lower:
                                recent_topics.append(keyword)
        
        # Sezione contesto dinamico
        if recent_topics:
            context_parts.append("## Recent Discussion Context:")
            context_parts.append(f"Recent topics: {', '.join(set(recent_topics))}")
            context_parts.append("")
        
        # Sezione metodologie
        methodologies = self.get_methodologies()
        if methodologies:
            context_parts.append("## Available Methodologies:")
            for method in methodologies:
                description = method.get('description', '')
                phases = method.get('hasPhase', [])
                context_parts.append(f"**{method['name']}**: {description}")
                if phases:
                    context_parts.append(f"  - Phases: {', '.join(phases)}")
        
        # Sezione template documenti
        templates = self.get_document_templates()
        if templates:
            context_parts.append("\n## Document Templates:")
            for template in templates:
                description = template.get('description', '')
                sections = template.get('hasSection', [])
                context_parts.append(f"**{template['name']}**: {description}")
                if sections:
                    context_parts.append(f"  - Sections: {', '.join(sections)}")
        
        # Best practices per ruolo
        role_id = f"role:{agent_role.value.replace('_', '').title().replace('Manager', 'Manager')}"
        role_entity = self.get_entity(role_id)
        
        if role_entity:
            context_parts.append(f"\n## Your Role: {role_entity['name']}")
            context_parts.append(f"{role_entity.get('description', '')}")
            
            responsibilities = role_entity.get('hasResponsibility', [])
            if responsibilities:
                context_parts.append("**Key Responsibilities:**")
                for resp in responsibilities:
                    context_parts.append(f"  - {resp}")
            
            role_templates = role_entity.get('hasTemplate', [])
            if role_templates:
                context_parts.append("**Templates you typically work with:**")
                for template_id in role_templates:
                    template = self.get_entity(template_id)
                    if template:
                        context_parts.append(f"  - {template['name']}")
        
        # Best practices applicabili
        domain = None
        if project_id:
            project = self.get_entity(f"project:{project_id}")
            if project:
                domain = project.get('belongsToDomain', '').replace('domain:', '')
        
        best_practices = self.get_best_practices(domain)
        if best_practices:
            context_parts.append("\n## Applicable Best Practices:")
            for practice in best_practices[:5]:  # Limit to top 5
                context_parts.append(f"**{practice['name']}**: {practice.get('description', '')}")
                benefit = practice.get('benefit')
                if benefit:
                    context_parts.append(f"  - Benefit: {benefit}")
        
        # Contesto progetto specifico
        if project_id:
            project = self.get_entity(f"project:{project_id}")
            if project:
                context_parts.append(f"\n## Current Project: {project['name']}")
                context_parts.append(f"{project.get('description', '')}")
                
                if 'hasObjective' in project:
                    objectives = project['hasObjective']
                    if isinstance(objectives, list):
                        context_parts.append(f"**Objectives**: {', '.join(objectives)}")
                    else:
                        context_parts.append(f"**Objectives**: {objectives}")
                
                if 'methodology' in project:
                    methodology = self.get_entity(project['methodology'])
                    if methodology:
                        context_parts.append(f"**Methodology**: {methodology['name']}")
                
                if 'hasStakeholder' in project:
                    stakeholders = project['hasStakeholder']
                    if isinstance(stakeholders, list):
                        context_parts.append(f"**Stakeholders**: {', '.join(stakeholders)}")
                
                if 'hasConstraint' in project:
                    constraints = project['hasConstraint']
                    if isinstance(constraints, list):
                        context_parts.append(f"**Constraints**: {', '.join(constraints)}")
        
        # Risk patterns rilevanti
        risk_patterns = self.get_risk_patterns()
        if risk_patterns:
            context_parts.append("\n## Common Risk Patterns to Consider:")
            for risk in risk_patterns[:3]:  # Top 3 risks
                context_parts.append(f"**{risk['name']}**: {risk.get('description', '')}")
                mitigation = risk.get('mitigation', [])
                if mitigation:
                    if isinstance(mitigation, list):
                        context_parts.append(f"  - Mitigation: {', '.join(mitigation)}")
                    else:
                        context_parts.append(f"  - Mitigation: {mitigation}")
        
        return "\n".join(context_parts)
    
    def create_agent_system_message(
        self,
        agent_role: AgentRole,
        project_id: Optional[str] = None,
        custom_instructions: Optional[str] = None
    ) -> str:
        """
        Crea system message per agenti AutoGen compatibile con BaseChatAgent
        
        Args:
            agent_role: Ruolo dell'agente
            project_id: ID del progetto
            custom_instructions: Istruzioni personalizzate
            
        Returns:
            str: System message formattato per AutoGen
        """
        role_entity = self.get_entity(f"role:{agent_role.value.replace('_', '').title().replace('Manager', 'Manager')}")
        
        base_message = f"""You are a {agent_role.value.replace('_', ' ').title()} agent in an AutoGen multi-agent system.

Your core responsibilities:"""

        if role_entity and 'hasResponsibility' in role_entity:
            responsibilities = role_entity['hasResponsibility']
            if isinstance(responsibilities, list):
                for resp in responsibilities:
                    base_message += f"\n• {resp}"
            else:
                base_message += f"\n• {responsibilities}"
        
        base_message += f"""

Context and Knowledge:
{self.get_context_for_agent(agent_role, project_id)}

Communication Guidelines:
• Respond concisely and professionally
• Use structured formats (markdown, bullets) when appropriate
• Collaborate effectively with other agents in the team
• Ask clarifying questions when information is insufficient
• Focus on actionable insights and concrete deliverables"""

        if custom_instructions:
            base_message += f"\n\nSpecial Instructions:\n{custom_instructions}"
        
        return base_message
    
    def get_agent_tools_suggestions(self, agent_role: AgentRole) -> List[Dict[str, Any]]:
        """
        Suggerisce tools appropriati per un agente basato sul suo ruolo
        Compatible with AutoGen 0.7+ tools system
        
        Args:
            agent_role: Ruolo dell'agente
            
        Returns:
            List[Dict]: Lista di tool suggestions
        """
        role_id = f"role:{agent_role.value.replace('_', '').title().replace('Manager', 'Manager')}"
        role_entity = self.get_entity(role_id)
        
        tools_suggestions = []
        
        if agent_role == AgentRole.PROJECT_MANAGER:
            tools_suggestions = [
                {
                    "name": "create_project_charter",
                    "description": "Creates a comprehensive project charter document",
                    "parameters": {
                        "project_name": "str",
                        "objectives": "List[str]",
                        "stakeholders": "List[str]"
                    }
                },
                {
                    "name": "analyze_project_risks", 
                    "description": "Analyzes project risks and suggests mitigation strategies",
                    "parameters": {
                        "project_context": "str",
                        "methodology": "str"
                    }
                }
            ]
        
        elif agent_role == AgentRole.REQUIREMENTS_ANALYST:
            tools_suggestions = [
                {
                    "name": "gather_requirements",
                    "description": "Systematically gathers and analyzes requirements",
                    "parameters": {
                        "stakeholder": "str",
                        "domain": "str",
                        "priority": "str"
                    }
                },
                {
                    "name": "create_requirements_document",
                    "description": "Creates structured requirements documentation",
                    "parameters": {
                        "functional_requirements": "List[str]",
                        "non_functional_requirements": "List[str]"
                    }
                }
            ]
        
        elif agent_role == AgentRole.TECHNICAL_WRITER:
            tools_suggestions = [
                {
                    "name": "generate_technical_documentation",
                    "description": "Generates comprehensive technical documentation",
                    "parameters": {
                        "doc_type": "str", 
                        "technical_specs": "Dict[str, Any]",
                        "audience": "str"
                    }
                }
            ]
        
        elif agent_role == AgentRole.CHANGE_DETECTOR:
            tools_suggestions = [
                {
                    "name": "analyze_changes",
                    "description": "Analyzes changes and their impact on documentation",
                    "parameters": {
                        "change_description": "str",
                        "affected_documents": "List[str]"
                    }
                }
            ]
        
        return tools_suggestions
    
    def get_handoff_suggestions(self, agent_role: AgentRole) -> List[Dict[str, str]]:
        """
        Suggerisce handoff appropriati per un agente
        Compatible with AutoGen 0.7+ handoff system
        
        Args:
            agent_role: Ruolo dell'agente
            
        Returns:
            List[Dict]: Lista di handoff configurations
        """
        handoffs = []
        
        if agent_role == AgentRole.PROJECT_MANAGER:
            handoffs = [
                {"target": "RequirementsAnalyst", "condition": "when requirements gathering is needed"},
                {"target": "TechnicalWriter", "condition": "when documentation needs to be created"},
                {"target": "ChangeDetector", "condition": "when changes need to be analyzed"}
            ]
        
        elif agent_role == AgentRole.REQUIREMENTS_ANALYST:
            handoffs = [
                {"target": "ProjectManager", "condition": "when requirements are complete"},
                {"target": "TechnicalWriter", "condition": "when technical documentation is needed"}
            ]
        
        elif agent_role == AgentRole.TECHNICAL_WRITER:
            handoffs = [
                {"target": "ProjectManager", "condition": "when documentation is complete"},
                {"target": "RequirementsAnalyst", "condition": "when requirements clarification is needed"}
            ]
        
        elif agent_role == AgentRole.CHANGE_DETECTOR:
            handoffs = [
                {"target": "ProjectManager", "condition": "when change impact analysis is complete"},
                {"target": "TechnicalWriter", "condition": "when documentation updates are needed"}
            ]
        
        return handoffs
    
    def create_team_configuration(
        self, 
        agent_roles: List[AgentRole], 
        methodology: Methodology = Methodology.AGILE
    ) -> Dict[str, Any]:
        """
        Crea configurazione team per AutoGen compatible con Team API
        
        Args:
            agent_roles: Lista ruoli agenti nel team
            methodology: Metodologia di progetto
            
        Returns:
            Dict: Configurazione team per AutoGen
        """
        team_config = {
            "methodology": methodology.value,
            "agents": [],
            "workflow_patterns": [],
            "termination_conditions": []
        }
        
        # Configura agenti
        for role in agent_roles:
            agent_config = {
                "role": role.value,
                "name": f"{role.value.replace('_', '').title()}Agent",
                "description": self._get_agent_description(role),
                "system_message": self.create_agent_system_message(role),
                "tools": self.get_agent_tools_suggestions(role),
                "handoffs": self.get_handoff_suggestions(role)
            }
            team_config["agents"].append(agent_config)
        
        # Workflow patterns basati sulla metodologia
        methodology_entity = self.get_entity(f"methodology:{methodology.value.title()}")
        if methodology_entity and 'hasPhase' in methodology_entity:
            phases = methodology_entity['hasPhase']
            if isinstance(phases, list):
                team_config["workflow_patterns"] = [
                    {
                        "type": "sequential",
                        "phases": phases,
                        "description": f"{methodology.value.title()} workflow pattern"
                    }
                ]
        
        # Termination conditions
        team_config["termination_conditions"] = [
            {
                "type": "max_turns",
                "value": 20,
                "description": "Maximum conversation turns"
            },
            {
                "type": "keyword_mention", 
                "keywords": ["TERMINATE", "COMPLETE", "FINISHED"],
                "description": "Completion keywords"
            }
        ]
        
        return team_config
    
    def _get_agent_description(self, agent_role: AgentRole) -> str:
        """Helper per ottenere descrizione agente"""
        role_id = f"role:{agent_role.value.replace('_', '').title().replace('Manager', 'Manager')}"
        role_entity = self.get_entity(role_id)
        
        if role_entity and 'description' in role_entity:
            return role_entity['description']
        
        # Fallback descriptions
        descriptions = {
            AgentRole.PROJECT_MANAGER: "Coordinates project workflow, manages stakeholder communication, and ensures project objectives are met",
            AgentRole.REQUIREMENTS_ANALYST: "Gathers, analyzes, and documents project requirements through stakeholder engagement",
            AgentRole.TECHNICAL_WRITER: "Creates and maintains comprehensive technical documentation for projects",
            AgentRole.CHANGE_DETECTOR: "Monitors and analyzes changes to maintain documentation consistency"
        }
        
        return descriptions.get(agent_role, f"Specialized {agent_role.value.replace('_', ' ')} agent")
    
    def get_template_sections(self, template_id: str) -> List[str]:
        """
        Recupera sezioni di un template documento
        
        Args:
            template_id: ID del template
            
        Returns:
            List[str]: Lista delle sezioni
        """
        template = self.get_entity(template_id)
        if template:
            sections = template.get('hasSection', [])
            return sections if isinstance(sections, list) else [sections]
        return []
    
    def suggest_documents_for_methodology(self, methodology: Methodology) -> List[Dict[str, Any]]:
        """
        Suggerisce documenti per una metodologia specifica
        
        Args:
            methodology: Metodologia di progetto
            
        Returns:
            List[Dict]: Template documenti suggeriti
        """
        methodology_id = f"methodology:{methodology.value.title()}"
        templates = self.get_document_templates()
        
        suggested = []
        for template in templates:
            required_for = template.get('requiredFor', [])
            if isinstance(required_for, str):
                required_for = [required_for]
            
            if methodology_id in required_for or 'all' in [r.lower() for r in required_for]:
                suggested.append(template)
        
        # Sort by priority if available
        def priority_sort_key(template):
            priority = template.get('priority', 'medium')
            priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            return priority_order.get(priority, 2)
        
        suggested.sort(key=priority_sort_key)
        return suggested
    
    def find_dependencies(self, entity_id: str) -> Dict[str, List[str]]:
        """
        Trova tutte le dipendenze di un'entità
        
        Args:
            entity_id: ID dell'entità
            
        Returns:
            Dict: Dizionario con dipendenze incoming e outgoing
        """
        entity = self.get_entity(entity_id)
        if not entity:
            return {"incoming": [], "outgoing": []}
        
        # Outgoing dependencies (cosa dipende da questa entità)
        outgoing = []
        depends_on = entity.get('dependsOn', [])
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        outgoing.extend(depends_on)
        
        # Incoming dependencies (cosa dipende da questa entità)
        incoming = []
        for other_entity in self.context["@graph"]:
            other_id = other_entity.get("@id")
            if other_id == entity_id:
                continue
            
            other_deps = other_entity.get('dependsOn', [])
            if isinstance(other_deps, str):
                other_deps = [other_deps]
            
            if entity_id in other_deps:
                incoming.append(other_id)
        
        return {"incoming": incoming, "outgoing": outgoing}
    
    def get_autogen_compatible_entities(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Restituisce entità organizzate per compatibilità con AutoGen 0.7+
        
        Returns:
            Dict: Entità organizzate per tipo con metadati AutoGen
        """
        entities = {
            "agents": [],
            "teams": [], 
            "tools": [],
            "templates": [],
            "methodologies": [],
            "best_practices": []
        }
        
        for entity in self.context["@graph"]:
            entity_type = entity.get("type", "").lower()
            
            if entity_type == "role":
                # Convert to agent-compatible format
                agent_entity = {
                    **entity,
                    "agent_class": "BaseChatAgent",
                    "produced_message_types": ["TextMessage"],
                    "required_tools": entity.get("hasTemplate", [])
                }
                entities["agents"].append(agent_entity)
            
            elif entity_type == "methodology":
                # Add AutoGen team patterns
                methodology = {
                    **entity,
                    "team_patterns": ["RoundRobinGroupChat", "SelectorGroupChat"],
                    "termination_patterns": entity.get("hasPhase", [])
                }
                entities["methodologies"].append(methodology)
            
            elif entity_type == "documenttemplate":
                # Convert to tool-compatible format
                template = {
                    **entity,
                    "tool_type": "document_generator",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "sections": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
                entities["templates"].append(template)
            
            elif entity_type == "bestpractice":
                entities["best_practices"].append(entity)
        
        return entities
    
    def validate_autogen_compatibility(self) -> Dict[str, Any]:
        """
        Valida compatibilità con AutoGen 0.7+ e restituisce report
        
        Returns:
            Dict: Report di compatibilità
        """
        compatibility_report = {
            "is_compatible": True,
            "autogen_version_detected": AUTOGEN_AVAILABLE,
            "issues": [],
            "recommendations": [],
            "supported_features": []
        }
        
        if not AUTOGEN_AVAILABLE:
            compatibility_report["is_compatible"] = False
            compatibility_report["issues"].append("AutoGen not installed or importable")
            compatibility_report["recommendations"].append("Install autogen-agentchat>=0.4.0")
            return compatibility_report
        
        # Check agent roles compatibility
        agent_entities = self.query_entities(entity_type="Role")
        if len(agent_entities) < 2:
            compatibility_report["issues"].append("Insufficient agent roles defined (need at least 2 for team)")
            compatibility_report["recommendations"].append("Add more agent roles to enable team functionality")
        
        # Check methodology compatibility
        methodologies = self.get_methodologies()
        supported_methodologies = []
        for method in methodologies:
            if method.get('hasPhase'):
                supported_methodologies.append(method['name'])
                compatibility_report["supported_features"].append(f"Methodology: {method['name']}")
        
        if not supported_methodologies:
            compatibility_report["issues"].append("No structured methodologies with phases defined")
        
        # Check template compatibility
        templates = self.get_document_templates()
        for template in templates:
            if not template.get('hasSection'):
                compatibility_report["issues"].append(f"Template {template['name']} lacks structured sections")
            else:
                compatibility_report["supported_features"].append(f"Template: {template['name']}")
        
        # Overall compatibility assessment
        if len(compatibility_report["issues"]) > 2:
            compatibility_report["is_compatible"] = False
        
        compatibility_report["summary"] = {
            "total_agents": len(agent_entities),
            "total_methodologies": len(methodologies),
            "total_templates": len(templates),
            "issues_count": len(compatibility_report["issues"]),
            "features_count": len(compatibility_report["supported_features"])
        }
        
        return compatibility_report
        """
        Valida che tutti i riferimenti tra entità siano validi
        
        Returns:
            List[str]: Lista di errori di validazione
        """
        errors = []
        valid_ids = {entity.get("@id") for entity in self.context["@graph"]}
        
        for entity in self.context["@graph"]:
            entity_id = entity.get("@id")
            
            # Check all reference fields
            for key, value in entity.items():
                if key.startswith(("has", "belongs", "uses", "depends", "involves", "related")):
                    references = value if isinstance(value, list) else [value]
                    
                    for ref in references:
                        if isinstance(ref, str) and ref.startswith(("domain:", "methodology:", "template:", "role:", "phase:", "project:")):
                            if ref not in valid_ids:
                                errors.append(f"Entity {entity_id} references non-existent {ref} in field {key}")
        
        return errors
    
    def export_to_rdf(self, format_type: str = "turtle") -> str:
        """
        Esporta KB in formato RDF
        
        Args:
            format_type: Formato RDF (turtle, xml, n3)
            
        Returns:
            str: KB serializzata in RDF
        """
        try:
            from rdflib import Graph, Namespace, URIRef, Literal
            
            g = Graph()
            
            # Define namespaces
            PM = Namespace("https://projectmanagement.org/vocab/")
            g.bind("pm", PM)
            
            for entity in self.context["@graph"]:
                entity_id = entity.get("@id")
                if not entity_id:
                    continue
                
                subject = URIRef(entity_id.replace(":", "/"))
                
                for key, value in entity.items():
                    if key.startswith("@"):
                        continue
                    
                    predicate = PM[key]
                    
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, str) and item.startswith(("domain:", "methodology:", "template:", "role:")):
                                obj = URIRef(item.replace(":", "/"))
                            else:
                                obj = Literal(item)
                            g.add((subject, predicate, obj))
                    else:
                        if isinstance(value, str) and value.startswith(("domain:", "methodology:", "template:", "role:")):
                            obj = URIRef(value.replace(":", "/"))
                        else:
                            obj = Literal(value)
                        g.add((subject, predicate, obj))
            
            return g.serialize(format=format_type)
            
        except ImportError:
            logger.warning("rdflib not installed, cannot export to RDF")
            return json.dumps(self.context, indent=2)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Recupera statistiche sulla KB
        
        Returns:
            Dict: Statistiche della knowledge base
        """
        entities = self.context["@graph"]
        
        # Count by type
        type_counts = {}
        for entity in entities:
            entity_type = entity.get("type", "Unknown")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        # Count relationships
        relationship_count = 0
        for entity in entities:
            for key in entity.keys():
                if key.startswith(("has", "belongs", "uses", "depends", "involves", "related")):
                    value = entity[key]
                    if isinstance(value, list):
                        relationship_count += len(value)
                    else:
                        relationship_count += 1
        
        return {
            "total_entities": len(entities),
            "entities_by_type": type_counts,
            "total_relationships": relationship_count,
            "cache_size": len(self._entity_cache),
            "file_size_bytes": self.kb_path.stat().st_size if self.kb_path.exists() else 0,
            "last_updated": self.context["metadata"].get("last_updated"),
            "is_dirty": self._dirty
        }
    
    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Ricerca full-text nella KB
        
        Args:
            query: Query di ricerca
            limit: Numero massimo di risultati
            
        Returns:
            List[Dict]: Risultati di ricerca ordinati per rilevanza
        """
        query_lower = query.lower()
        results = []
        
        for entity in self.context["@graph"]:
            score = 0
            matched_fields = []
            
            # Search in name (higher weight)
            name = entity.get("name", "")
            if query_lower in name.lower():
                score += 10
                matched_fields.append("name")
            
            # Search in description (medium weight)
            description = entity.get("description", "")
            if query_lower in description.lower():
                score += 5
                matched_fields.append("description")
            
            # Search in other text fields (lower weight)
            for key, value in entity.items():
                if key in ["name", "description", "@id", "type"]:
                    continue
                
                if isinstance(value, str) and query_lower in value.lower():
                    score += 2
                    matched_fields.append(key)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str) and query_lower in item.lower():
                            score += 1
                            matched_fields.append(key)
                            break
            
            if score > 0:
                results.append({
                    "entity": entity,
                    "score": score,
                    "matched_fields": matched_fields
                })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return [r["entity"] for r in results[:limit]]
    
    def backup(self, backup_path: Optional[str] = None) -> str:
        """
        Crea backup della KB
        
        Args:
            backup_path: Path del backup (opzionale)
            
        Returns:
            str: Path del file di backup creato
        """
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.kb_path.stem}_backup_{timestamp}.jsonld"
        
        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create backup with metadata
        backup_data = {
            **self.context,
            "backup_metadata": {
                "original_path": str(self.kb_path),
                "backup_created_at": serialize_datetime(datetime.now()),
                "backup_version": "1.0"
            }
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Backup creato: {backup_path}")
        return str(backup_path)
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """
        Ripristina KB da backup
        
        Args:
            backup_path: Path del file di backup
            
        Returns:
            bool: True se ripristinato con successo
        """
        try:
            backup_path = Path(backup_path)
            if not backup_path.exists():
                raise KnowledgeBaseError(f"Backup file not found: {backup_path}")
            
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Validate backup structure
            if "@context" not in backup_data or "@graph" not in backup_data:
                raise KnowledgeBaseError("Invalid backup file structure")
            
            # Remove backup-specific metadata
            backup_data.pop("backup_metadata", None)
            
            # Restore context
            self.context = backup_data
            self._rebuild_cache()
            
            # Save restored KB
            self.save()
            
            logger.info(f"KB ripristinata da backup: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Errore ripristino backup: {e}")
            return False
    
    def __len__(self) -> int:
        """Numero di entità nella KB"""
        return len(self.context["@graph"])
    
    def __contains__(self, entity_id: str) -> bool:
        """Verifica se un'entità esiste nella KB"""
        return entity_id in self._entity_cache
    
    def __iter__(self):
        """Itera su tutte le entità"""
        return iter(self.context["@graph"])
    
    def __str__(self) -> str:
        """Rappresentazione string della KB"""
        stats = self.get_statistics()
        return f"KnowledgeBase({stats['total_entities']} entities, {stats['total_relationships']} relationships)"
    
    def __repr__(self) -> str:
        """Rappresentazione tecnica della KB"""
        return f"KnowledgeBase(path='{self.kb_path}', entities={len(self)}, dirty={self._dirty})"


# ============================================================================
# KNOWLEDGE BASE FACTORY
# ============================================================================

class KnowledgeBaseFactory:
    """Factory per creare istanze di Knowledge Base"""
    
    @staticmethod
    def create_default() -> KnowledgeBase:
        """Crea KB con configurazione di default"""
        return KnowledgeBase()
    
    @staticmethod
    def create_from_file(file_path: str) -> KnowledgeBase:
        """Crea KB da file esistente"""
        return KnowledgeBase(kb_path=file_path)
    
    @staticmethod
    def create_in_memory() -> KnowledgeBase:
        """Crea KB in memoria (senza persistenza automatica)"""
        kb = KnowledgeBase(auto_save=False)
        kb.kb_path = Path(":memory:")  # Symbolic path
        return kb
    
    @staticmethod
    def merge_knowledge_bases(kb1: KnowledgeBase, kb2: KnowledgeBase) -> KnowledgeBase:
        """
        Unisce due knowledge base
        
        Args:
            kb1: Prima knowledge base
            kb2: Seconda knowledge base
            
        Returns:
            KnowledgeBase: Nuova KB con entità unite
        """
        merged_kb = KnowledgeBase(auto_save=False)
        
        # Merge contexts
        merged_context = kb1.context.copy()
        
        # Add entities from kb2, avoiding duplicates
        existing_ids = {e.get("@id") for e in merged_context["@graph"]}
        
        for entity in kb2.context["@graph"]:
            entity_id = entity.get("@id")
            if entity_id not in existing_ids:
                merged_context["@graph"].append(entity)
        
        merged_kb.context = merged_context
        merged_kb._rebuild_cache()
        
        logger.info(f"Merged KBs: {len(kb1)} + {len(kb2)} = {len(merged_kb)} entities")
        return merged_kb


# ============================================================================
# EXPORTS - Updated for AutoGen 0.7+ compatibility
# ============================================================================

__all__ = [
    'KnowledgeBase',
    'KnowledgeBaseFactory', 
    'KnowledgeBaseError',
    'EntityNotFoundError',
    'InvalidEntityError',
    'QueryError',
    # AutoGen compatibility
    'AUTOGEN_AVAILABLE'
]