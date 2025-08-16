from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json


class DocumentType(Enum):
    PROJECT_CHARTER = "project_charter"
    REQUIREMENTS = "requirements"
    TECHNICAL_SPEC = "technical_spec"
    PROJECT_PLAN = "project_plan"
    ARCHITECTURE = "architecture"


class ChangeType(Enum):
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"


class AgentRole(Enum):
    PROJECT_MANAGER = "project_manager"
    REQUIREMENTS_ANALYST = "requirements_analyst" 
    CHANGE_DETECTOR = "change_detector"
    TECHNICAL_WRITER = "technical_writer"
    HUMAN = "human"


@dataclass
class Document:
    id: str
    type: DocumentType
    title: str
    content: str
    version: int
    created_at: datetime
    modified_at: datetime
    hash: str
    dependencies: List[str]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat(),
            'type': self.type.value
        }


@dataclass
class ProjectContext:
    project_id: str
    project_name: str
    objectives: List[str]
    stakeholders: List[str]
    constraints: List[str]
    timeline: Optional[str]
    budget: Optional[str]
    domain: Optional[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AgentMessage:
    agent_id: str
    role: AgentRole
    content: str
    message_type: str
    timestamp: datetime
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat(),
            'role': self.role.value
        }
