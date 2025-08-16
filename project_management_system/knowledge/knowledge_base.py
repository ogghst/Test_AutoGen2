"""
Knowledge Base per il sistema multi-agente
Gestisce entità, relazioni e contesto in formato JSON-LD
Fornisce API per query, aggiornamenti e reasoning contestuale
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import asdict

from models.data_models import (
    ProjectContext, AgentRole, Methodology, DocumentType, Priority,
    serialize_datetime, ValidationError
)


# ============================================================================
# LOGGER SETUP
# ============================================================================

logger = logging.getLogger(__name__)


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
        
        logger.debug("Cache ricostruita")

    def save(self):
        """Salva la KB su file JSON-LD"""
        try:
            self.context["metadata"]["last_updated"] = serialize_datetime(datetime.now())
            self.context["metadata"]["entity_count"] = len(self.context["@graph"])
            
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(self.context, f, indent=2, ensure_ascii=False)
            
            self._dirty = False
            logger.info(f"Knowledge Base salvata in {self.kb_path}")
        except Exception as e:
            logger.error(f"Errore salvataggio KB: {e}")
            raise KnowledgeBaseError(f"Impossibile salvare KB: {e}")

    # ============================================================================
    # PUBLIC API - ENTITY MANAGEMENT
    # ============================================================================

    def add_entity(self, entity: Dict[str, Any]) -> str:
        """
        Aggiunge una nuova entità alla KB
        
        Args:
            entity: Dizionario rappresentante l'entità
            
        Returns:
            ID dell'entità aggiunta
            
        Raises:
            InvalidEntityError: Se l'entità è malformata o ID esiste già
        """
        if "@id" not in entity or "type" not in entity:
            raise InvalidEntityError("Entità deve avere '@id' e 'type'")
            
        entity_id = entity["@id"]
        if self.get_entity(entity_id):
            raise InvalidEntityError(f"Entità con ID '{entity_id}' già esistente")
            
        now = serialize_datetime(datetime.now())
        entity["createdAt"] = entity.get("createdAt", now)
        entity["updatedAt"] = now
        
        self.context["@graph"].append(entity)
        self._entity_cache[entity_id] = entity
        self._dirty = True
        
        # Aggiorna cache relazioni
        self._rebuild_cache()
        
        if self.auto_save:
            self.save()
            
        logger.info(f"Entità aggiunta: {entity_id}")
        return entity_id

    def update_entity(self, entity_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggiorna un'entità esistente
        
        Args:
            entity_id: ID dell'entità da aggiornare
            updates: Dizionario con i campi da aggiornare
            
        Returns:
            L'entità aggiornata
            
        Raises:
            EntityNotFoundError: Se l'entità non esiste
        """
        entity = self.get_entity(entity_id)
        if not entity:
            raise EntityNotFoundError(f"Entità non trovata: {entity_id}")
            
        # Rimuovi campi non aggiornabili
        updates.pop("@id", None)
        updates.pop("createdAt", None)
        
        entity.update(updates)
        entity["updatedAt"] = serialize_datetime(datetime.now())
        
        self._entity_cache[entity_id] = entity
        self._dirty = True
        
        # Aggiorna cache relazioni
        self._rebuild_cache()
        
        if self.auto_save:
            self.save()
            
        logger.info(f"Entità aggiornata: {entity_id}")
        return entity

    def remove_entity(self, entity_id: str) -> bool:
        """
        Rimuove un'entità dalla KB
        
        Args:
            entity_id: ID dell'entità da rimuovere
            
        Returns:
            True se rimossa, False altrimenti
        """
        entity_index = -1
        for i, entity in enumerate(self.context["@graph"]):
            if entity.get("@id") == entity_id:
                entity_index = i
                break
        
        if entity_index != -1:
            self.context["@graph"].pop(entity_index)
            self._entity_cache.pop(entity_id, None)
            self._dirty = True
            
            # Rimuovi da cache relazioni
            self._rebuild_cache()
            
            if self.auto_save:
                self.save()
                
            logger.info(f"Entità rimossa: {entity_id}")
            return True
            
        return False

    # ============================================================================
    # PUBLIC API - QUERY & SEARCH
    # ============================================================================

    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un'entità per ID
        
        Args:
            entity_id: ID dell'entità
            
        Returns:
            Dizionario dell'entità o None se non trovata
        """
        return self._entity_cache.get(entity_id)

    def find_entities_by_type(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Trova tutte le entità di un certo tipo
        
        Args:
            entity_type: Tipo di entità da cercare
            
        Returns:
            Lista di entità corrispondenti
        """
        return [
            entity for entity in self.context["@graph"]
            if entity.get("type") == entity_type
        ]

    def find_entities_by_property(self, prop_name: str, prop_value: Any) -> List[Dict[str, Any]]:
        """
        Trova entità che hanno una proprietà con un certo valore
        
        Args:
            prop_name: Nome della proprietà
            prop_value: Valore della proprietà
            
        Returns:
            Lista di entità corrispondenti
        """
        results = []
        for entity in self.context["@graph"]:
            if prop_name in entity:
                if isinstance(entity[prop_name], list):
                    if prop_value in entity[prop_name]:
                        results.append(entity)
                elif entity[prop_name] == prop_value:
                    results.append(entity)
        return results

    def search(self, query_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Esegue una query semplice sulla KB
        
        Args:
            query_dict: Dizionario con criteri di ricerca (es. {"type": "Methodology", "name": "Agile"})
            
        Returns:
            Lista di entità che soddisfano tutti i criteri
        """
        results = []
        for entity in self.context["@graph"]:
            match = True
            for key, value in query_dict.items():
                if key not in entity or entity[key] != value:
                    match = False
                    break
            if match:
                results.append(entity)
        return results

    def get_related_entities(self, entity_id: str, relation: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ottiene entità collegate a un'entità data
        
        Args:
            entity_id: ID dell'entità di partenza
            relation: (Opzionale) Filtra per tipo di relazione (es. "hasTask")
            
        Returns:
            Lista di entità collegate
            
        Raises:
            EntityNotFoundError: Se l'entità di partenza non esiste
        """
        entity = self.get_entity(entity_id)
        if not entity:
            raise EntityNotFoundError(f"Entità non trovata: {entity_id}")
            
        related_ids = []
        for key, value in entity.items():
            if relation and key != relation:
                continue
            
            if key.startswith(("has", "belongs", "uses", "depends", "involves", "related")):
                if isinstance(value, list):
                    related_ids.extend(v for v in value if isinstance(v, str))
                elif isinstance(value, str):
                    related_ids.append(value)
                    
        return [
            self.get_entity(rid) for rid in set(related_ids) if self.get_entity(rid)
        ]

    # ============================================================================
    # PUBLIC API - DOMAIN-SPECIFIC QUERIES
    # ============================================================================

    def get_methodology_details(self, methodology_name: str) -> Optional[Dict[str, Any]]:
        """
        Recupera dettagli di una metodologia, incluse fasi, ruoli e best practice
        
        Args:
            methodology_name: Nome della metodologia (es. "Agile")
            
        Returns:
            Dizionario con dettagli o None se non trovata
        """
        methodologies = self.find_entities_by_property("name", methodology_name)
        if not methodologies:
            return None
            
        methodology = methodologies[0]
        details = {
            "methodology": methodology,
            "phases": self.get_related_entities(methodology["@id"], "hasPhase"),
            "roles": self.get_related_entities(methodology["@id"], "hasRole"),
            "best_practices": self.get_related_entities(methodology["@id"], "hasBestPractice"),
            "templates": self.get_related_entities(methodology["@id"], "hasTemplate")
        }
        return details

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Recupera un template di documento per nome
        
        Args:
            template_name: Nome del template (es. "Project Charter")
            
        Returns:
            Dizionario del template o None se non trovato
        """
        templates = self.find_entities_by_property("name", template_name)
        return templates[0] if templates else None

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """Recupera tutti i template di documento"""
        return self.find_entities_by_type("DocumentTemplate")

    def get_all_methodologies(self) -> List[Dict[str, Any]]:
        """Recupera tutte le metodologie"""
        return self.find_entities_by_type("Methodology")

    # ============================================================================
    # CONTEXT MANAGEMENT
    # ============================================================================

    def set_project_context(self, project_context: ProjectContext):
        """
        Imposta il contesto del progetto corrente nella KB
        
        Args:
            project_context: Oggetto ProjectContext
        """
        context_entity = asdict(project_context)
        context_entity["@id"] = f"context:project_{project_context.project_id}"
        context_entity["type"] = "ProjectContext"
        
        if self.get_entity(context_entity["@id"]):
            self.update_entity(context_entity["@id"], context_entity)
        else:
            self.add_entity(context_entity)
            
        logger.info(f"Contesto progetto impostato: {project_context.project_id}")

    def get_project_context(self, project_id: str) -> Optional[ProjectContext]:
        """
        Recupera il contesto di un progetto
        
        Args:
            project_id: ID del progetto
            
        Returns:
            Oggetto ProjectContext o None
        """
        context_id = f"context:project_{project_id}"
        entity = self.get_entity(context_id)
        if not entity:
            return None
        
        try:
            # Rimuovi campi non attesi da ProjectContext
            entity.pop("@id", None)
            entity.pop("type", None)
            entity.pop("createdAt", None)
            entity.pop("updatedAt", None)
            return ProjectContext(**entity)
        except Exception as e:
            logger.error(f"Errore deserializzazione contesto progetto: {e}")
            return None