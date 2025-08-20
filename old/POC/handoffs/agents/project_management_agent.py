"""
Project Management Agent for the handoffs pattern.

This agent is responsible for guiding users through PMI best practices and creating
comprehensive project management plans in markdown format.
"""

from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from ..base.AIAgent import AIAgent
from .tools import (
    PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
    create_pmi_project_management_plan_tool,
    transfer_back_to_triage_tool,
)

class ProjectManagementAgent(AIAgent):
    """
    Project management agent responsible for PMI best practices and comprehensive project planning.
    
    This agent specializes in project management activities including:
    - Creating PMI-compliant project management plans
    - Guiding users through PMI best practices
    - Providing project management guidance and standards
    - Creating comprehensive markdown project documentation
    """
    
    def __init__(self, model_client, tools: list[Tool] = None):
        """
        Initialize the ProjectManagementAgent.
        
        Args:
            model_client: The LLM client for processing requests
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="You are a certified Project Management Professional (PMP) agent specializing in PMI best practices. Your role is to:\n\n"
            "1. Guide users through PMI project management standards and best practices\n"
            "2. Help create comprehensive, PMI-compliant project management plans\n"
            "3. Educate users on the PMBOK Guide framework and its application\n"
            "4. Use the create_pmi_project_management_plan tool to generate structured plans\n"
            "5. Provide expert advice on project management methodologies and processes\n"
            "6. Transfer back to triage if the request is outside your scope\n\n"
            "Always follow PMI standards and best practices. Be thorough, professional, and educational. "
            "When creating project management plans, ensure they include all essential PMI components "
            "such as scope, schedule, cost, quality, risk, communication, and stakeholder management. "
            "Provide clear explanations of PMI concepts and how they apply to the user's project."
        )
        
        project_management_tools = [create_pmi_project_management_plan_tool]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            description="A certified PMP agent responsible for PMI best practices and comprehensive project management planning.",
            system_message=system_message,
            model_client=model_client,
            tools=project_management_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
