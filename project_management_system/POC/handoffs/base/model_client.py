"""
Model Client Factory for the handoffs pattern.

This module provides factory functions for creating and configuring model clients
used by the AI agents in the system.
"""

import os
from autogen_ext.models.openai import OpenAIChatCompletionClient


def create_model_client(api_key: str = None, base_url: str = None, model: str = None):
    """
    Create and configure a model client for the handoffs system.
    
    Args:
        api_key: API key for the model service (defaults to environment variable)
        base_url: Base URL for the model service (defaults to DeepSeek)
        model: Model name to use (defaults to deepseek-chat)
    
    Returns:
        OpenAIChatCompletionClient: Configured model client
    """
    # Use provided API key or fall back to environment variable
    api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "sk-9a4206f76b4a466095d6b85b859c6a85")
    
    # Use provided base URL or fall back to DeepSeek
    base_url = base_url or "https://api.deepseek.com"
    
    # Use provided model or fall back to deepseek-chat
    model = model or "deepseek-chat"
    
    return OpenAIChatCompletionClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
        model_info={
            "family": "deepseek",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True
        }
    )
