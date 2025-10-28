"""
Message Protocol and Base AI Agent classes for the handoffs pattern.

This module contains the core message classes and the base AIAgent class that all
specialized agents inherit from.
"""

from typing import List, Literal

from pydantic import BaseModel

from autogen_core.models import (
    LLMMessage,
)


class UserLogin(BaseModel):
    """Message class for user login events."""
    pass


class UserTask(BaseModel):
    """Message class for user task requests."""
    context: List[LLMMessage]
class AgentResponse(BaseModel):
    """Message class for agent responses."""
    reply_to_topic_type: str
    context: List[LLMMessage]
    

class DebugMessage(BaseModel):
    """Message class for debug messages."""
    content: str
    source: str
    type: Literal['debug'] = 'debug'    
class DebugResponse(BaseModel):
    """Message class for debug messages."""
    reply_to_topic_type: str
    context: List[DebugMessage]


