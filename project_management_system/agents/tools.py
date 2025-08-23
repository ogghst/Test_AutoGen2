"""
Tools and topic types for the handoffs pattern.

This module contains all the tool functions and topic type constants used by
the various agents in the system.
"""

from config.logging_config import get_logger
from autogen_core.tools import FunctionTool
from models.data_models import Project


# Topic type constants
TRIAGE_AGENT_TOPIC_TYPE = "triage_agent"
PLANNING_AGENT_TOPIC_TYPE = "planning_agent"
EXECUTION_AGENT_TOPIC_TYPE = "execution_agent"
QUALITY_AGENT_TOPIC_TYPE = "quality_agent"
HUMAN_AGENT_TOPIC_TYPE = "human_agent"
PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE = "project_management_agent"
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


async def transfer_to_project_management_agent() -> str:
    """Transfer control to the project management agent."""
    return PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE


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
    logger = get_logger(__name__)
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
    logger = get_logger(__name__)
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
    logger = get_logger(__name__)
    logger.info(f"Executing task '{task_name}' with priority '{priority}'")
    return f"Task '{task_name}' with priority '{priority}' has been executed."


async def create_pmi_project_management_plan(
    project: Project
) -> str:
    """
    Create a comprehensive PMI-compliant project management plan in markdown format.
    
    This tool follows PMI best practices and creates a structured project management plan
    that includes all essential components according to the PMBOK Guide.
    
    Args:
        project_name (str): The name of the project
        project_description (str): Brief description of the project
        project_objectives (str): Key objectives and success criteria
        project_scope (str): What is included and excluded from the project
        stakeholder_requirements (str): Key stakeholder needs and expectations
        constraints (str): Time, budget, resource, or technical constraints
        assumptions (str): Key assumptions about the project

    Returns:
        str: A comprehensive project management plan in markdown format following PMI standards
    """
    logger = get_logger(__name__)
    logger.info(f"Creating PMI-compliant project management plan for {project_name}")
    
    # Create the markdown project management plan
    plan = f"""# Project Management Plan - {project_name}

## 1. Project Overview

### 1.1 Project Description
{project_description}

### 1.2 Project Objectives
{project_objectives}

### 1.3 Project Scope
{project_scope}

## 2. Stakeholder Analysis

### 2.1 Stakeholder Requirements
{stakeholder_requirements}

### 2.2 Stakeholder Register
- **Project Sponsor**: [To be identified]
- **Project Manager**: [To be identified]
- **Project Team**: [To be identified]
- **End Users**: [To be identified]

## 3. Project Constraints and Assumptions

### 3.1 Constraints
{constraints}

### 3.2 Assumptions
{assumptions}

## 4. Project Management Approach

### 4.1 Methodology
This project will follow PMI best practices and the PMBOK Guide framework.

### 4.2 Project Life Cycle
- **Initiation Phase**: Project charter and stakeholder identification
- **Planning Phase**: Detailed project planning and risk assessment
- **Execution Phase**: Project implementation and team management
- **Monitoring & Control**: Progress tracking and change management
- **Closure Phase**: Project completion and lessons learned

## 5. Scope Management

### 5.1 Scope Statement
{project_scope}

### 5.2 Work Breakdown Structure (WBS)
- **Level 1**: Project
- **Level 2**: Major deliverables
- **Level 3**: Work packages
- **Level 4**: Activities

## 6. Schedule Management

### 6.1 Project Schedule
- **Project Start Date**: [To be determined]
- **Project End Date**: [To be determined]
- **Key Milestones**: [To be defined]

### 6.2 Critical Path
[To be developed during detailed planning]

## 7. Cost Management

### 7.1 Budget Estimate
- **Total Project Budget**: [To be determined]
- **Cost Categories**: [To be defined]

### 7.2 Cost Control
- Regular budget reviews
- Earned value management
- Change control procedures

## 8. Quality Management

### 8.1 Quality Standards
- PMI quality standards
- Industry best practices
- Customer requirements

### 8.2 Quality Assurance
- Quality audits
- Process improvements
- Continuous monitoring

## 9. Resource Management

### 9.1 Human Resources
- Project team structure
- Roles and responsibilities
- Resource allocation

### 9.2 Physical Resources
- Equipment and materials
- Facilities and infrastructure

## 10. Risk Management

### 10.1 Risk Identification
- Technical risks
- Schedule risks
- Resource risks
- External risks

### 10.2 Risk Response Strategies
- Avoid, transfer, mitigate, or accept
- Contingency planning
- Risk monitoring

## 11. Communication Management

### 11.1 Communication Plan
- Stakeholder communication matrix
- Reporting schedule
- Communication channels

### 11.2 Information Distribution
- Regular status reports
- Team meetings
- Stakeholder updates

## 12. Procurement Management

### 12.1 Procurement Strategy
- Make-or-buy decisions
- Vendor selection criteria
- Contract management

## 13. Integration Management

### 13.1 Change Control
- Change request process
- Impact assessment
- Approval procedures

### 13.2 Project Monitoring
- Performance measurement
- Progress reporting
- Issue management

## 14. Project Success Criteria

### 14.1 Success Metrics
- On-time delivery
- Within budget
- Meets quality standards
- Stakeholder satisfaction

## 15. Lessons Learned and Knowledge Management

### 15.1 Knowledge Capture
- Best practices documentation
- Lessons learned repository
- Process improvements

---

*This project management plan follows PMI best practices and the PMBOK Guide framework. It should be reviewed and updated regularly throughout the project lifecycle.*
"""
    
    return plan


# Tool instances for delegation
transfer_to_planning_tool = FunctionTool(
    transfer_to_planning_agent,
    description="Only call this if explicitly asked to create a project plan.",
)

transfer_to_execution_tool = FunctionTool(
    transfer_to_execution_agent,
    description="Only call this if explicitly asked to execute a project task.",
)

transfer_to_quality_tool = FunctionTool(
    transfer_to_quality_agent,
    description="Only call this if explicitly asked to review project quality.",
)

transfer_to_project_management_tool = FunctionTool(
    transfer_to_project_management_agent,
    description="Only call this if explicitly asked to create a PMI-compliant project management plan or follow PMI best practices.",
)

transfer_back_to_triage_tool = FunctionTool(
    transfer_back_to_triage,
    description="Call this if the user brings up a topic outside of your duties, including escalating to human.",
)

escalate_to_human_tool = FunctionTool(
    escalate_to_human,
    description="Only call this if explicitly asked to escalate to a human.",
)

# Tool instances for project management
create_project_plan_tool = FunctionTool(
    create_project_plan,
    description="Only call this if explicitly asked to create a project plan.",
)

execute_project_task_tool = FunctionTool(
    execute_project_task,
    description="Only call this if explicitly asked to execute a project task.",
)

review_project_quality_tool = FunctionTool(
    review_project_quality, 
    description="Only call this if explicitly asked to review project quality.",
)

create_pmi_project_management_plan_tool = FunctionTool(
    create_pmi_project_management_plan,
    description="Only call this if explicitly asked to create a PMI-compliant project management plan.",
)
