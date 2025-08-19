"""
Planning Agent for the handoffs pattern.

This agent is responsible for creating project plans and gathering requirements.
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from ..base.AIAgent import AIAgent
from .tools import (
    PLANNING_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    create_project_plan_tool,
    transfer_back_to_triage_tool,
)


class PlanningAgent(AIAgent):
    """
    Project planning agent responsible for creating project plans and gathering requirements.
    
    This agent specializes in project planning activities including:
    - Creating project plans
    - Gathering and documenting requirements
    - Creating project timelines and milestones
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the PlanningAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard planning tools
        """
        system_message = SystemMessage(
            content="You are a project planning agent for ACME Inc. Your role is to:\n"
            "1. Help users create project plans\n"
            "2. Gather and document requirements\n"
            "3. Create project timelines and milestones\n"
            "4. Use the create_project_plan tool when needed\n"
            "5. Transfer back to triage if the request is outside your scope\n\n"
            "Always be thorough and professional. Ask clarifying questions when needed."
        )
        
        planning_tools = [create_project_plan_tool]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A project planning agent responsible for creating project plans and gathering requirements.",
            system_message=system_message,
            model_client=model_client,
            tools=planning_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=PLANNING_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
