"""
Quality Agent for the handoffs pattern.

This agent is responsible for quality assurance and project reviews.
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from base.AIAgent import AIAgent
from .tools import (
    QUALITY_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    review_project_quality_tool,
    transfer_back_to_triage_tool,
)


class QualityAgent(AIAgent):
    """
    Project quality agent responsible for quality assurance and project reviews.
    
    This agent specializes in quality-related activities including:
    - Reviewing project quality
    - Conducting quality assessments
    - Quality assurance processes
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the QualityAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard quality tools
        """
        system_message = SystemMessage(
            content="You are a project quality agent for ACME Inc. Your role is to:\n"
            "1. Help users review project quality\n"
            "2. Conduct quality assessments\n"
            "3. Use the review_project_quality tool when needed\n"
            "4. Transfer back to triage if the request is outside your scope\n\n"
            "Always be thorough and quality-focused. Maintain high standards."
        )
        
        quality_tools = [review_project_quality_tool]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A project quality agent responsible for quality assurance and project reviews.",
            system_message=system_message,
            model_client=model_client,
            tools=quality_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=QUALITY_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
