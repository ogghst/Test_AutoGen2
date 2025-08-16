# ============================================================================
# models/data_models.py
# ============================================================================

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


# ============================================================================
# knowledge/knowledge_base.py
# ============================================================================

import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class KnowledgeBase:
    """Gestisce la knowledge base in formato JSON-LD"""
    
    def __init__(self, kb_path: str = "knowledge_base.jsonld"):
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


# ============================================================================
# storage/document_store.py  
# ============================================================================

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class DocumentStore:
    """Store per documenti di output generati dagli agenti"""
    
    def __init__(self, storage_path: str = "documents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.index_file = self.storage_path / "document_index.json"
        self.documents: Dict[str, Document] = {}
        self._load_index()
    
    def _load_index(self):
        """Carica l'indice dei documenti"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                
            for doc_data in index_data:
                doc_data['created_at'] = datetime.fromisoformat(doc_data['created_at'])
                doc_data['modified_at'] = datetime.fromisoformat(doc_data['modified_at'])
                doc_data['type'] = DocumentType(doc_data['type'])
                
                doc = Document(**doc_data)
                self.documents[doc.id] = doc
    
    def _save_index(self):
        """Salva l'indice dei documenti"""
        index_data = [doc.to_dict() for doc in self.documents.values()]
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def save_document(self, document: Document) -> None:
        """Salva un documento e aggiorna l'indice"""
        # Calcola hash del contenuto
        document.hash = hashlib.md5(document.content.encode()).hexdigest()
        document.modified_at = datetime.now()
        
        # Salva contenuto su file
        doc_file = self.storage_path / f"{document.id}_v{document.version}.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(document.content)
        
        # Aggiorna indice
        self.documents[document.id] = document
        self._save_index()
        
        print(f"📄 Documento salvato: {document.title} (v{document.version})")
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Recupera un documento per ID"""
        return self.documents.get(doc_id)
    
    def get_documents_by_type(self, doc_type: DocumentType) -> List[Document]:
        """Recupera documenti per tipo"""
        return [doc for doc in self.documents.values() if doc.type == doc_type]
    
    def list_documents(self) -> List[Document]:
        """Lista tutti i documenti"""
        return list(self.documents.values())


# ============================================================================
# agents/base_agent.py
# ============================================================================

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from autogen_agentchat.agents import ConversableAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import BaseMessage, TextMessage
from autogen_core.base import CancellationToken
import httpx
import json
import asyncio
import os


class BaseProjectAgent(ConversableAgent, ABC):
    """Classe base per tutti gli agenti del sistema"""
    
    def __init__(
        self, 
        name: str,
        role: AgentRole,
        description: str,
        knowledge_base: KnowledgeBase,
        document_store: DocumentStore,
        deepseek_model: str = "deepseek-chat",
        deepseek_api_key: str = None
    ):
        super().__init__(name=name, description=description)
        self.role = role
        self.knowledge_base = knowledge_base
        self.document_store = document_store
        self.deepseek_model = deepseek_model
        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
        self.conversation_history: List[Dict[str, Any]] = []
        
        if not self.deepseek_api_key:
            raise ValueError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or pass it as parameter.")
        
    async def on_messages(self, messages: List[BaseMessage], cancellation_token: CancellationToken) -> Response:
        """Gestisce messaggi ricevuti - implementazione base"""
        try:
            # Aggiorna cronologia conversazione
            for msg in messages:
                if isinstance(msg, TextMessage):
                    self.conversation_history.append({
                        "role": "user" if msg.source != self.name else "assistant",
                        "content": msg.content,
                        "timestamp": datetime.now().isoformat()
                    })
            
            # Processa il messaggio
            response_content = await self._process_message(messages[-1])
            
            # Crea risposta
            if response_content:
                response_msg = TextMessage(content=response_content, source=self.name)
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": response_content,
                    "timestamp": datetime.now().isoformat()
                })
                return Response(chat_message=response_msg)
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            return Response(chat_message=TextMessage(content=error_msg, source=self.name))
        
        return Response(chat_message=TextMessage(content="Message processed", source=self.name))
    
    @abstractmethod
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa un messaggio specifico - da implementare in sottoclassi"""
        pass
    
    async def _call_deepseek(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Chiama DeepSeek API per generazione testo"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.deepseek_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4000,
            "top_p": 0.95,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stop": None
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.deepseek_url,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"].strip()
                elif response.status_code == 401:
                    return "❌ Error: Invalid DeepSeek API key. Please check your DEEPSEEK_API_KEY environment variable."
                elif response.status_code == 429:
                    return "⚠️ Rate limit exceeded. Please wait a moment and try again."
                else:
                    error_detail = response.text
                    return f"❌ Error calling DeepSeek API: {response.status_code} - {error_detail}"
                    
        except httpx.TimeoutException:
            return "⏰ Request timeout. DeepSeek API is taking too long to respond."
        except Exception as e:
            return f"❌ Error connecting to DeepSeek API: {str(e)}"
    
    def _get_agent_context(self, project_id: str = None) -> str:
        """Ottiene contesto specifico per l'agente dalla knowledge base"""
        return self.knowledge_base.get_context_for_agent(self.role, project_id)
    
    def _create_system_prompt(self, project_id: str = None) -> str:
        """Crea system prompt base per l'agente"""
        context = self._get_agent_context(project_id)
        
        base_prompt = f"""You are a {self.role.value.replace('_', ' ').title()} agent in a multi-agent project management system.

Your role: {self.description}

Knowledge Base Context:
{context}

Guidelines:
- Be professional and concise in your responses
- Use the knowledge base information to inform your decisions
- Collaborate effectively with other agents
- When generating documents, follow industry best practices
- Ask clarifying questions when information is insufficient
- Focus on actionable insights and concrete deliverables
- Use structured formats (markdown, bullet points) when appropriate

Current conversation history is available for context."""

        return base_prompt


# ============================================================================
# agents/project_manager.py
# ============================================================================

from typing import Optional, List, Dict, Any
import re
from datetime import datetime


class ProjectManagerAgent(BaseProjectAgent):
    """Agente Project Manager - Orchestratore principale"""
    
    def __init__(self, knowledge_base: KnowledgeBase, document_store: DocumentStore, **kwargs):
        super().__init__(
            name="ProjectManager",
            role=AgentRole.PROJECT_MANAGER,
            description="Coordinates project workflow, manages stakeholder communication, and ensures project objectives are met",
            knowledge_base=knowledge_base,
            document_store=document_store,
            **kwargs
        )
        self.current_project: Optional[ProjectContext] = None
        self.workflow_state = "idle"  # idle, initializing, requirements_gathering, planning, executing
        
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa messaggi e coordina il workflow"""
        content = message.content.lower()
        
        # Analizza tipo di messaggio
        if "init_project" in content or "start project" in content:
            return await self._handle_project_initialization(message.content)
        elif "status" in content or "update" in content:
            return await self._handle_status_request()
        elif "requirements" in content and self.workflow_state == "initializing":
            return await self._coordinate_requirements_gathering()
        elif "plan" in content and "project" in content:
            return await self._coordinate_project_planning()
        else:
            return await self._handle_general_coordination(message.content)
    
    async def _handle_project_initialization(self, content: str) -> str:
        """Gestisce inizializzazione nuovo progetto"""
        self.workflow_state = "initializing"
        
        # Estrae informazioni dal prompt usando DeepSeek
        extraction_prompt = f"""
        Extract project information from the following text and structure it as JSON:
        
        Text: {content}
        
        Extract and format as valid JSON:
