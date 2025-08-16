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
from datetime import datetime

from ..models.data_models import AgentRole
from ..knowledge.knowledge_base import KnowledgeBase
from ..storage.document_store import DocumentStore


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
