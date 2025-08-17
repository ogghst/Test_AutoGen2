from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import Response
from autogen_agentchat.messages import BaseMessage, TextMessage
from autogen_core import CancellationToken
import httpx
import json
import asyncio
import os
from datetime import datetime

from models.data_models import AgentRole
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore
from config.logging_config import get_logger


from config.settings import DeepSeekConfig, OllamaConfig


class LLMConnectionError(Exception):
    """Custom exception for LLM connection errors."""
    pass


class BaseProjectAgent(BaseChatAgent, ABC):
    """Classe base per tutti gli agenti del sistema"""

    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str,
        knowledge_base: KnowledgeBase,
        document_store: DocumentStore,
        llm_config: Union[DeepSeekConfig, OllamaConfig],
    ):
        super().__init__(name=name, description=description)
        self.role = role
        self.knowledge_base = knowledge_base
        self.document_store = document_store
        self.llm_config = llm_config
        self.conversation_history: List[Dict[str, Any]] = []

        # Set up logger
        self.logger = get_logger(__name__)

        self.logger.info(f"Agent initialized: {name} ({role.value})")

    @property
    def produced_message_types(self) -> List[type]:
        """The types of messages that the agent produces."""
        return [TextMessage]

    async def on_reset(self, cancellation_token: CancellationToken) -> None:
        """Resets the agent to its initialization state."""
        self.conversation_history = []
        self.logger.debug(f"Agent {self.name} reset")
        
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
            
            self.logger.debug(f"Agent {self.name} received {len(messages)} messages")
            
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
                
                self.logger.debug(f"Agent {self.name} generated response: {len(response_content)} characters")
                return Response(chat_message=response_msg)
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.logger.error(f"Agent {self.name} error processing message: {e}", exc_info=True)
            return Response(chat_message=TextMessage(content=error_msg, source=self.name))
        
        return Response(chat_message=TextMessage(content="Message processed", source=self.name))
    
    @abstractmethod
    async def _process_message(self, message: BaseMessage) -> Optional[str]:
        """Processa un messaggio specifico - da implementare in sottoclassi"""
        pass
    
    async def _call_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Calls the configured LLM (DeepSeek or Ollama) for text generation."""
        if isinstance(self.llm_config, DeepSeekConfig):
            return await self._execute_deepseek_request(prompt, system_prompt)
        elif isinstance(self.llm_config, OllamaConfig):
            return await self._execute_ollama_request(prompt, system_prompt)
        else:
            unsupported_error = "Unsupported LLM configuration."
            self.logger.error(unsupported_error)
            return unsupported_error

    async def _execute_deepseek_request(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Executes a request to the DeepSeek API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = self.llm_config.get_headers()
        payload = self.llm_config.get_payload_template()
        payload["messages"] = messages
        
        self.logger.debug(f"Calling DeepSeek API with {len(messages)} messages")
        
        try:
            async with httpx.AsyncClient(timeout=self.llm_config.timeout) as client:
                response = await client.post(self.llm_config.api_url, headers=headers, json=payload)
                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"].strip()
                self.logger.debug(f"DeepSeek API call successful: {len(content)} characters")
                return content
        except httpx.HTTPStatusError as e:
            error_msg = f"Error calling DeepSeek API: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            raise LLMConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Error connecting to DeepSeek API: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise LLMConnectionError(error_msg) from e

    async def _execute_ollama_request(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Executes a request to the Ollama API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = self.llm_config.get_payload_template()
        payload["messages"] = messages

        self.logger.debug(f"Calling Ollama API at {self.llm_config.get_api_url()} with model {self.llm_config.model}")

        try:
            async with httpx.AsyncClient(timeout=self.llm_config.timeout) as client:
                response = await client.post(self.llm_config.get_api_url(), json=payload)
                response.raise_for_status()
                result = response.json()
                content = result["message"]["content"].strip()
                self.logger.debug(f"Ollama API call successful: {len(content)} characters")
                return content
        except httpx.HTTPStatusError as e:
            error_msg = f"Error calling Ollama API: {e.response.status_code} - {e.response.text}"
            self.logger.error(error_msg)
            raise LLMConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Error connecting to Ollama API: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise LLMConnectionError(error_msg) from e
    
    def _get_agent_context(self, project_id: str = None) -> str:
        """Ottiene contesto specifico per l'agente dalla knowledge base"""
        try:
            context = self.knowledge_base.get_context_for_agent(self.role, project_id)
            self.logger.debug(f"Retrieved context for agent {self.name} (project: {project_id})")
            return context
        except Exception as e:
            self.logger.warning(f"Failed to get context for agent {self.name}: {e}")
            return "No specific context available for this agent."
    
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

        self.logger.debug(f"Created system prompt for agent {self.name}: {len(base_prompt)} characters")
        return base_prompt
