"""
Triage Agent for the handoffs pattern.

This agent is responsible for understanding user requests and routing them to
appropriate specialized agents.
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from base.AIAgent import AIAgent
from .tools import (
    TRIAGE_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    #transfer_to_planning_tool,
    transfer_to_execution_tool,
    transfer_to_quality_tool,
    transfer_to_project_management_tool,
    transfer_to_user_stories_tool,
    escalate_to_human_tool,
)


class TriageAgent(AIAgent):
    """
    Triage agent responsible for understanding user requests and routing to appropriate agents.
    
    This agent acts as the entry point for all user requests and determines which
    specialized agent should handle the request based on the content and context.
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the TriageAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard delegation tools
        """
        system_message = SystemMessage(
            content="You are a project management triage agent. Your role is to:\n"
            "1. Understand the user's request\n"
            "2. Route them to the appropriate specialized agent\n"
            "3. Use the transfer tools to delegate tasks\n\n"
            "Available specialized agents:\n"
            #"- Planning Agent: For basic project planning and requirements gathering\n"
            "- Project Management Agent: For PMI-compliant project management plans and best practices\n"
            "- Execution Agent: For task execution and project management\n"
            "- Quality Agent: For quality assurance and project reviews\n"
            "- User Stories Agent: For generating comprehensive user stories with EARS notation acceptance criteria\n"
            "- Human Agent: For complex requests requiring human intervention\n\n"
            "Always be helpful and professional. Route users to the most appropriate agent."
        )
        
        delegate_tools = [
        #    transfer_to_planning_tool,
            transfer_to_execution_tool,
            transfer_to_quality_tool,
            transfer_to_project_management_tool,
            transfer_to_user_stories_tool,
            escalate_to_human_tool,
        ]
        
        super().__init__(
            description="A triage agent responsible for understanding user requests and routing to appropriate agents.",
            system_message=system_message,
            model_client=model_client,
            tools=tools or [],
            delegate_tools=delegate_tools,
            agent_topic_type=TRIAGE_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
