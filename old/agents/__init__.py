"""
Multi-Agent System for Project Management

This module provides a collection of specialized agents that collaborate to automate
project documentation creation and management.
"""

from .base_agent import BaseProjectAgent
from .project_manager import ProjectManagerAgent
from .requirements_analyst import RequirementsAnalystAgent
from .change_detector import ChangeDetectorAgent
from .technical_writer import TechnicalWriterAgent

__all__ = [
    "BaseProjectAgent",
    "ProjectManagerAgent", 
    "RequirementsAnalystAgent",
    "ChangeDetectorAgent",
    "TechnicalWriterAgent"
]

# Agent factory function for easy instantiation
def create_agent(agent_type: str, knowledge_base, document_store, **kwargs):
    """
    Factory function to create agent instances.
    
    Args:
        agent_type: Type of agent to create
        knowledge_base: Knowledge base instance
        document_store: Document store instance
        **kwargs: Additional arguments for agent initialization
        
    Returns:
        Agent instance of the specified type
        
    Raises:
        ValueError: If agent type is not supported
    """
    agent_map = {
        "project_manager": ProjectManagerAgent,
        "requirements_analyst": RequirementsAnalystAgent,
        "change_detector": ChangeDetectorAgent,
        "technical_writer": TechnicalWriterAgent
    }
    
    if agent_type not in agent_map:
        raise ValueError(f"Unsupported agent type: {agent_type}. Available types: {list(agent_map.keys())}")
    
    return agent_map[agent_type](knowledge_base, document_store, **kwargs)
