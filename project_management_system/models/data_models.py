"""
Data models per il sistema multi-agente di project management
Definisce strutture dati, enum e classi per gestire entità e relazioni
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Union
import json
import uuid
from pathlib import Path


# ============================================================================
# ENUMERATIONS
# ============================================================================

class DocumentType(Enum):
    """Tipi di documento supportati dal sistema"""
    PROJECT_CHARTER = "project_charter"
    REQUIREMENTS = "requirements"
    TECHNICAL_SPEC = "technical_spec"
    PROJECT_PLAN = "project_plan"
    ARCHITECTURE = "architecture"
    USER_STORIES = "user_stories"
    TEST_PLAN = "test_plan"
    DEPLOYMENT_GUIDE = "deployment_guide"
    API_DOCUMENTATION = "api_documentation"
    CHANGE_LOG = "change_log"


class ChangeType(Enum):
    """Tipi di cambiamento per change management"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"
    MOVED = "moved"


class AgentRole(Enum):
    """Ruoli degli agenti nel sistema"""
    PROJECT_MANAGER = "project_manager"
    REQUIREMENTS_ANALYST = "requirements_analyst" 
    CHANGE_DETECTOR = "change_detector"
    TECHNICAL_WRITER = "technical_writer"
    ARCHITECT = "architect"
    QA_SPECIALIST = "qa_specialist"
    HUMAN = "human"


class ProjectStatus(Enum):
    """Stati del progetto"""
    DRAFT = "draft"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Priority(Enum):
    """Livelli di priorità"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Methodology(Enum):
    """Metodologie di project management"""
    AGILE = "agile"
    WATERFALL = "waterfall"
    SCRUM = "scrum"
    KANBAN = "kanban"
    HYBRID = "hybrid"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_uuid() -> str:
    """Genera UUID unico per entità"""
    return str(uuid.uuid4())


def serialize_datetime(dt: datetime) -> str:
    """Serializza datetime in formato ISO"""
    return dt.isoformat() if dt else None


def deserialize_datetime(dt_str: str) -> Optional[datetime]:
    """Deserializza datetime da formato ISO"""
    try:
        return datetime.fromisoformat(dt_str) if dt_str else None
    except (ValueError, TypeError):
        return None


# ============================================================================
# CORE DATA MODELS
# ============================================================================

@dataclass
class Document:
    """Rappresenta un documento generato dal sistema"""
    id: str
    type: DocumentType
    title: str
    content: str
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    hash: str = ""
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    author: str = ""
    project_id: Optional[str] = None
    file_path: Optional[str] = None
    
    def __post_init__(self):
        """Post-init per validazione e setup"""
        if not self.id:
            self.id = generate_uuid()
        
        # Auto-set metadata se non presente
        if 'created_by' not in self.metadata and self.author:
            self.metadata['created_by'] = self.author
            
        if 'document_format' not in self.metadata:
            self.metadata['document_format'] = 'markdown'
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'created_at': serialize_datetime(self.created_at),
            'modified_at': serialize_datetime(self.modified_at),
            'type': self.type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Crea istanza da dizionario"""
        data = data.copy()  # Avoid modifying original
        data['created_at'] = deserialize_datetime(data.get('created_at'))
        data['modified_at'] = deserialize_datetime(data.get('modified_at'))
        data['type'] = DocumentType(data['type'])
        return cls(**data)
    
    def update_content(self, new_content: str, author: str = "system"):
        """Aggiorna contenuto e incrementa versione"""
        self.content = new_content
        self.modified_at = datetime.now()
        self.version += 1
        self.metadata['last_modified_by'] = author
        
    def add_dependency(self, doc_id: str):
        """Aggiunge dipendenza da altro documento"""
        if doc_id not in self.dependencies:
            self.dependencies.append(doc_id)
    
    def remove_dependency(self, doc_id: str):
        """Rimuove dipendenza"""
        if doc_id in self.dependencies:
            self.dependencies.remove(doc_id)


@dataclass 
class ChangeEvent:
    """Rappresenta un evento di cambiamento nel sistema"""
    id: str = field(default_factory=generate_uuid)
    document_id: str = ""
    change_type: ChangeType = ChangeType.MODIFIED
    old_hash: Optional[str] = None
    new_hash: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    author: str = "system"
    details: Dict[str, Any] = field(default_factory=dict)
    affected_documents: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'timestamp': serialize_datetime(self.timestamp),
            'change_type': self.change_type.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChangeEvent':
        """Crea istanza da dizionario"""
        data = data.copy()
        data['timestamp'] = deserialize_datetime(data.get('timestamp'))
        data['change_type'] = ChangeType(data['change_type'])
        return cls(**data)


@dataclass
class ProjectContext:
    """Contesto completo di un progetto"""
    project_id: str = field(default_factory=generate_uuid)
    project_name: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    timeline: Optional[str] = None
    budget: Optional[str] = None
    domain: Optional[str] = None
    methodology: Methodology = Methodology.AGILE
    status: ProjectStatus = ProjectStatus.DRAFT
    priority: Priority = Priority.MEDIUM
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Relazioni
    team_members: List[str] = field(default_factory=list)
    related_projects: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'created_at': serialize_datetime(self.created_at),
            'updated_at': serialize_datetime(self.updated_at),
            'methodology': self.methodology.value,
            'status': self.status.value,
            'priority': self.priority.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectContext':
        """Crea istanza da dizionario"""
        data = data.copy()
        data['created_at'] = deserialize_datetime(data.get('created_at'))
        data['updated_at'] = deserialize_datetime(data.get('updated_at'))
        data['methodology'] = Methodology(data.get('methodology', 'agile'))
        data['status'] = ProjectStatus(data.get('status', 'draft'))
        data['priority'] = Priority(data.get('priority', 'medium'))
        return cls(**data)
    
    def update_status(self, new_status: ProjectStatus):
        """Aggiorna status del progetto"""
        self.status = new_status
        self.updated_at = datetime.now()
        self.metadata['status_changed_at'] = serialize_datetime(datetime.now())
    
    def add_stakeholder(self, stakeholder: str):
        """Aggiunge stakeholder"""
        if stakeholder not in self.stakeholders:
            self.stakeholders.append(stakeholder)
            self.updated_at = datetime.now()
    
    def add_objective(self, objective: str):
        """Aggiunge obiettivo"""
        if objective not in self.objectives:
            self.objectives.append(objective)
            self.updated_at = datetime.now()


@dataclass
class AgentMessage:
    """Messaggio tra agenti nel sistema"""
    id: str = field(default_factory=generate_uuid)
    agent_id: str = ""
    role: AgentRole = AgentRole.HUMAN
    content: str = ""
    message_type: str = "text"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    thread_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'timestamp': serialize_datetime(self.timestamp),
            'role': self.role.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Crea istanza da dizionario"""
        data = data.copy()
        data['timestamp'] = deserialize_datetime(data.get('timestamp'))
        data['role'] = AgentRole(data['role'])
        return cls(**data)


@dataclass
class Requirement:
    """Rappresenta un singolo requisito"""
    id: str = field(default_factory=generate_uuid)
    title: str = ""
    description: str = ""
    type: str = "functional"  # functional, non_functional, constraint
    priority: Priority = Priority.MEDIUM
    status: str = "draft"  # draft, approved, implemented, tested
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    stakeholder: str = ""
    effort_estimate: Optional[int] = None  # in hours
    project_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'created_at': serialize_datetime(self.created_at),
            'updated_at': serialize_datetime(self.updated_at),
            'priority': self.priority.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Requirement':
        """Crea istanza da dizionario"""
        data = data.copy()
        data['created_at'] = deserialize_datetime(data.get('created_at'))
        data['updated_at'] = deserialize_datetime(data.get('updated_at'))
        data['priority'] = Priority(data.get('priority', 'medium'))
        return cls(**data)
    
    def update_status(self, new_status: str):
        """Aggiorna status del requisito"""
        self.status = new_status
        self.updated_at = datetime.now()
        self.metadata['status_history'] = self.metadata.get('status_history', [])
        self.metadata['status_history'].append({
            'status': new_status,
            'timestamp': serialize_datetime(datetime.now())
        })


@dataclass
class Task:
    """Rappresenta un task di progetto"""
    id: str = field(default_factory=generate_uuid)
    title: str = ""
    description: str = ""
    assignee: str = ""
    status: str = "todo"  # todo, in_progress, review, done
    priority: Priority = Priority.MEDIUM
    effort_estimate: Optional[int] = None  # in hours
    actual_effort: Optional[int] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    project_id: str = ""
    requirement_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario per serializzazione"""
        return {
            **asdict(self),
            'created_at': serialize_datetime(self.created_at),
            'updated_at': serialize_datetime(self.updated_at),
            'due_date': serialize_datetime(self.due_date),
            'completed_at': serialize_datetime(self.completed_at),
            'priority': self.priority.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Crea istanza da dizionario"""
        data = data.copy()
        data['created_at'] = deserialize_datetime(data.get('created_at'))
        data['updated_at'] = deserialize_datetime(data.get('updated_at'))
        data['due_date'] = deserialize_datetime(data.get('due_date'))
        data['completed_at'] = deserialize_datetime(data.get('completed_at'))
        data['priority'] = Priority(data.get('priority', 'medium'))
        return cls(**data)
    
    def mark_completed(self):
        """Marca task come completato"""
        self.status = "done"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()


# ============================================================================
# VALIDATION HELPERS
# ============================================================================

class ValidationError(Exception):
    """Eccezione per errori di validazione"""
    pass


def validate_project_context(project: ProjectContext) -> bool:
    """Valida ProjectContext"""
    if not project.project_name.strip():
        raise ValidationError("Project name cannot be empty")
    
    if not project.objectives:
        raise ValidationError("Project must have at least one objective")
    
    if project.budget and not project.budget.replace('$', '').replace(',', '').replace('.', '').isdigit():
        raise ValidationError("Invalid budget format")
    
    return True


def validate_document(document: Document) -> bool:
    """Valida Document"""
    if not document.title.strip():
        raise ValidationError("Document title cannot be empty")
    
    if not document.content.strip():
        raise ValidationError("Document content cannot be empty")
    
    if document.version < 1:
        raise ValidationError("Document version must be >= 1")
    
    return True


def validate_requirement(requirement: Requirement) -> bool:
    """Valida Requirement"""
    if not requirement.title.strip():
        raise ValidationError("Requirement title cannot be empty")
    
    if not requirement.description.strip():
        raise ValidationError("Requirement description cannot be empty")
    
    if requirement.type not in ["functional", "non_functional", "constraint"]:
        raise ValidationError("Invalid requirement type")
    
    return True


# ============================================================================
# EXPORT ALL
# ============================================================================

__all__ = [
    # Enums
    'DocumentType', 'ChangeType', 'AgentRole', 'ProjectStatus', 
    'Priority', 'Methodology',
    
    # Models
    'Document', 'ChangeEvent', 'ProjectContext', 'AgentMessage',
    'Requirement', 'Task',
    
    # Utilities
    'generate_uuid', 'serialize_datetime', 'deserialize_datetime',
    
    # Validation
    'ValidationError', 'validate_project_context', 'validate_document',
    'validate_requirement'
]