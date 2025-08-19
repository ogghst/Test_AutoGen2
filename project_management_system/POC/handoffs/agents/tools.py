"""
Tools and topic types for the handoffs pattern.

This module contains all the tool functions and topic type constants used by
the various agents in the system.
"""

import logging
from autogen_core.tools import FunctionTool


# Topic type constants
TRIAGE_AGENT_TOPIC_TYPE = "triage_agent"
PLANNING_AGENT_TOPIC_TYPE = "planning_agent"
EXECUTION_AGENT_TOPIC_TYPE = "execution_agent"
QUALITY_AGENT_TOPIC_TYPE = "quality_agent"
HUMAN_AGENT_TOPIC_TYPE = "human_agent"
USER_TOPIC_TYPE = "user"


# Tool functions for agent delegation
async def transfer_to_planning_agent() -> str:
    """Transfer control to the planning agent."""
    return PLANNING_AGENT_TOPIC_TYPE


async def transfer_to_execution_agent() -> str:
    """Transfer control to the execution agent."""
    return EXECUTION_AGENT_TOPIC_TYPE


async def transfer_to_quality_agent() -> str:
    """Transfer control to the quality agent."""
    return QUALITY_AGENT_TOPIC_TYPE


async def transfer_back_to_triage() -> str:
    """Transfer control back to the triage agent."""
    return TRIAGE_AGENT_TOPIC_TYPE


async def escalate_to_human() -> str:
    """Escalate the request to a human agent."""
    return HUMAN_AGENT_TOPIC_TYPE


# Tool functions for project management tasks
async def create_project_plan(
    project_name: str,  # Project name: str - The name of the project to be planned.
    requirements: str   # Requirements: str - The requirements or specifications for the project.
) -> str:
    """
    Create a project plan with the given name and requirements.
    
    Args:
        project_name (str): The name of the project to be planned.
        requirements (str): The requirements or specifications for the project.

    Returns:
        str: Confirmation message that the project plan has been created.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Creating project plan for {project_name} with requirements: {requirements}")
    return f"Project plan created for {project_name} with requirements: {requirements}"


async def review_project_quality(
    project_id: str  # project_id: str - The unique identifier of the project to be reviewed.
) -> str:
    """
    Review the quality of a project.
    
    Args:
        project_id (str): The unique identifier of the project to be reviewed.

    Returns:
        str: Confirmation message that the quality review has been completed for the specified project.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Reviewing quality for project {project_id}")
    return f"Quality review completed for project {project_id}"


async def execute_project_task(
    task_name: str,  # task_name: str - The name of the task to be executed.
    priority: str   # priority: str - The priority level of the task.
) -> str:
    """
    Execute a project task with the given name and priority.
    
    Args:
        task_name (str): The name of the task to be executed.
        priority (str): The priority level of the task.

    Returns:
        str: Confirmation message that the task has been executed.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Executing task '{task_name}' with priority '{priority}'")
    return f"Task '{task_name}' with priority '{priority}' has been executed."


# Tool instances for delegation
transfer_to_planning_tool = FunctionTool(
    transfer_to_planning_agent,
    description="Use for anything planning or requirements related.",
)

transfer_to_execution_tool = FunctionTool(
    transfer_to_execution_agent,
    description="Use for anything execution or task related.",
)

transfer_to_quality_tool = FunctionTool(
    transfer_to_quality_agent,
    description="Use for anything quality or review related.",
)

transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your purview, including escalating to human.",
)

escalate_to_human_tool = FunctionTool(
    escalate_to_human,
    description="Only call this if explicitly asked to.",
)

# Tool instances for project management
create_project_plan_tool = FunctionTool(
    create_project_plan,
    description="Use for anything related to creating a project plan.",
)

execute_project_task_tool = FunctionTool(
    execute_project_task,
    description="Use for anything related to executing a project task.",
)

review_project_quality_tool = FunctionTool(
    review_project_quality, 
    description="Use for anything related to reviewing project quality.",
)
