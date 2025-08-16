from typing import Optional, List, Dict, Any
import re
from datetime import datetime

from .base_agent import BaseProjectAgent
from ..models.data_models import AgentRole, ProjectContext
from ..knowledge.knowledge_base import KnowledgeBase
from ..storage.document_store import DocumentStore
from autogen_agentchat.messages import BaseMessage


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
"""
