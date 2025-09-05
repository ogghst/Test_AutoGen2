"""
Model Client Factory for the handoffs pattern.

This module provides factory functions for creating and configuring model clients
used by the AI agents in the system.
"""

import json
import os
from typing import Optional
from config.settings import ConfigManager, ModelProvider
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_core.models import ChatCompletionClient
from config.logging_config import get_logger

logger = get_logger(__name__)

def create_model_client(config_manager: ConfigManager) -> ChatCompletionClient:
    """
    Create and configure a model client for the handoffs system.
    
    Args:
        config_manager: Configuration manager instance from settings.py
    
    Returns:
        Configured model client
    """
    if config_manager.llm_provider == ModelProvider.DEEPSEEK:
        # Get DeepSeek configuration from unified LLM config
        deepseek_config = config_manager.llm_config.deepseek
        
        client = OpenAIChatCompletionClient(
            model=deepseek_config.model,
            api_key=deepseek_config.api_key,
            base_url=deepseek_config.api_url,
            model_info=deepseek_config.model_info,
            temperature=deepseek_config.temperature
        )
                
    elif config_manager.llm_provider == ModelProvider.OLLAMA:
        # Get Ollama configuration from unified LLM config
        ollama_config = config_manager.llm_config.ollama
        
        client = OllamaChatCompletionClient(
            model=ollama_config.model,
            host=ollama_config.base_url,
            model_info=ollama_config.model_info
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {config_manager.llm_provider.value}")
    
    logger.info(f"LLM Client created: {json.dumps(client._raw_config)}")
    
    return client
                
                