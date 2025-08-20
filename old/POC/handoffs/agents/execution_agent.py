"""
Execution Agent for the handoffs pattern.

This agent is responsible for task execution and project management.
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from ..base.AIAgent import AIAgent
from .tools import (
    EXECUTION_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    execute_project_task_tool,
    transfer_back_to_triage_tool,
)


class ExecutionAgent(AIAgent):
    """
    Project execution agent responsible for task execution and project management.
    
    This agent specializes in project execution activities including:
    - Executing project tasks
    - Managing project timelines and deliverables
    - Task prioritization and management
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the ExecutionAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard execution tools
        """
        system_message = SystemMessage(
            content="You are a project execution agent. Your role is to:\n"
            "1. Help users execute project tasks\n"
            "2. Manage project timelines and deliverables\n"
            "3. Use the execute_project_task tool when needed\n"
            "4. Transfer back to triage if the request is outside your scope\n\n"
            "Always be efficient and results-oriented. Focus on getting things done."
        )
        
        execution_tools = [execute_project_task_tool]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A project execution agent responsible for task execution and project management.",
            system_message=system_message,
            model_client=model_client,
            tools=execution_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=EXECUTION_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
