"""
Tools and topic types for the handoffs pattern.

This module contains all the tool functions and topic type constants used by
the various agents in the system.
"""

import os
import json
import re
import uuid
from datetime import datetime, date

from config.logging_config import get_logger
from autogen_core.tools import FunctionTool
from models.data_models import Project


# Custom JSON encoder to handle UUID and datetime serialization
class UUIDEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles UUID and datetime objects."""
    
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


# Topic type constants
TRIAGE_AGENT_TOPIC_TYPE = "triage_agent"
PLANNING_AGENT_TOPIC_TYPE = "planning_agent"
EXECUTION_AGENT_TOPIC_TYPE = "execution_agent"
QUALITY_AGENT_TOPIC_TYPE = "quality_agent"
HUMAN_AGENT_TOPIC_TYPE = "human_agent"
PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE = "project_management_agent"
USER_STORIES_AGENT_TOPIC_TYPE = "user_stories_agent"
USER_PROFILER_AGENT_TOPIC_TYPE = "user_profiler_agent"
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


async def transfer_to_user_stories_agent() -> str:
    """Transfer control to the user stories gathering agent."""
    return USER_STORIES_AGENT_TOPIC_TYPE


async def transfer_to_user_profiler_agent() -> str:
    """Transfer control to the user profiler agent."""
    return USER_PROFILER_AGENT_TOPIC_TYPE


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


async def retrieve_project_data(name: str) -> str:
    """Retrieve project data.
    Args:
        name (str): The name of the project to retrieve data for.

    Returns:
        str: The project data as a JSON string.
    """
    logger = get_logger(__name__)
    logger.info(f"Retrieving project data for {name}")
    # Retrieve the project info file generated as per save_project_data code
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_documents')
    # Find the first .json file in the output_documents directory
    try:
        safe_project_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', name)
        
        files = [f for f in os.listdir(output_dir) if f.startswith(safe_project_name)]
        if not files:
            raise FileNotFoundError("No project data files found in output_documents.")
        # For simplicity, retrieve the first file (could be improved to select by project name)
        project_file = os.path.join(output_dir, safe_project_name + ".json")
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Return the JSON data as a string to avoid UUID serialization issues
        return json.dumps(project_data, indent=2, cls=UUIDEncoder)
    except Exception as e:
        logger.error(f"Error retrieving project data: {e}")
        # Return an error message if retrieval fails
        return f"Error retrieving project data: {str(e)}"


async def save_project_data(
     project: Project # the project to save
) -> str:
    """Save project data."""
    logger = get_logger(__name__)
    logger.info(f"Saving project data for {project.name}")
    
    # save the project data to the database


    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_documents')
    os.makedirs(output_dir, exist_ok=True)
    # Transform the project name to a filesystem-compatible string

    safe_project_name = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', project.name)
    output_path = os.path.join(output_dir, f'{safe_project_name}.json')

    # Use Pydantic's .model_dump_json() for serialization if available, else fallback to .json()
    try:
        project_json = project.model_dump_json(indent=2)
    except AttributeError:
        project_json = project.json(indent=2)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(project_json)
    
    return f"Project data saved for {project.name}"


async def create_uuid() -> str:
    """Create a uuid.
    Args:
        None
    Returns:
        str: A uuid.
    """
    return str(uuid.uuid4())

async def create_pmi_project_management_plan(
    project: Project # the project to create a project management plan for
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
    logger.info(f"Creating PMI-compliant project management plan for {project.name}")
    
    # Create the markdown project management plan
    plan = f"""# Project Management Plan - {project.name}

## 1. Project Overview

### 1.1 Project Description
{project.description}

### 1.2 Project Objectives
{project.vision}

### 1.3 Project Epics
{chr(10).join([f"- **{epic.name}**: {epic.description}" for epic in project.scope.epics])}


## 2. Stakeholder Analysis

### 2.1 Stakeholder Requirements
Project: {project.name}
Description: {project.description}
Vision: {project.vision}

### 2.2 Stakeholder Register
{chr(10).join([f"- **{stakeholder.name}** ({stakeholder.role}): {stakeholder.influence} influence, {stakeholder.interest} interest" for stakeholder in project.stakeholders])}




## 3. Project Constraints and Assumptions

### 3.1 Constraints
{chr(10).join([f"- {constraint}" for constraint in project.scope.constraints]) if project.scope.constraints else "- No specific constraints identified"}

### 3.2 Assumptions
{chr(10).join([f"- {assumption}" for assumption in project.scope.assumptions]) if project.scope.assumptions else "- No specific assumptions identified"}


## 4. Project Management Approach

### 4.1 Methodology
This project follows the **{project.methodology}** methodology and will adhere to PMI best practices and the PMBOK Guide framework.

**Current Project Status**: {project.status}
**Last Updated**: {project.last_updated.strftime('%Y-%m-%d %H:%M:%S') if project.last_updated else 'Not specified'}

### 4.2 Project Life Cycle
- **Initiation Phase**: Project charter and stakeholder identification
- **Planning Phase**: Detailed project planning and risk assessment
- **Execution Phase**: Project implementation and team management
- **Monitoring & Control**: Progress tracking and change management
- **Closure Phase**: Project completion and lessons learned

## 5. Scope Management

### 5.1 Scope Statement
**Inclusions:**
{chr(10).join([f"- {item}" for item in project.scope.inclusions]) if project.scope.inclusions else "- No specific inclusions defined"}

**Exclusions:**
{chr(10).join([f"- {item}" for item in project.scope.exclusions]) if project.scope.exclusions else "- No specific exclusions defined"}

**Acceptance Criteria:**
{chr(10).join([f"- {criteria}" for criteria in project.scope.acceptance_criteria]) if project.scope.acceptance_criteria else "- No specific acceptance criteria defined"}

### 5.2 Work Breakdown Structure (WBS)
- **Level 1**: Project
- **Level 2**: Major deliverables
- **Level 3**: Work packages
- **Level 4**: Activities

## 6. Schedule Management

### 6.1 Project Schedule
- **Project Start Date**: {project.created_date.strftime('%Y-%m-%d') if project.created_date else 'To be determined'}
- **Project End Date**: [To be determined]
- **Key Milestones**: 
{chr(10).join([f"  - **{milestone.name}**: {milestone.description} (Target: {milestone.target_date}, Status: {milestone.status})" for milestone in project.milestones]) if project.milestones else "  - No milestones defined yet"}

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
**Team: {project.team.name}**
**Total Capacity**: {project.team.capacity} hours/week
**Velocity**: {project.team.velocity} story points per sprint

**Team Members:**
{chr(10).join([f"- **{member.name}** ({member.role}): {member.capacity} hours/week, Active: {'Yes' if member.is_active else 'No'}" for member in project.team.members]) if project.team.members else "- No team members assigned yet"}

**Roles and Responsibilities**: Defined according to PMI best practices
**Resource Allocation**: Managed through sprint planning and capacity management

### 9.2 Physical Resources
- Equipment and materials
- Facilities and infrastructure

## 10. Risk Management

### 10.1 Risk Identification
**Identified Risks:**
{chr(10).join([f"- **{risk.description}** ({risk.category}): {risk.probability} probability, {risk.impact} impact - Status: {risk.status}" for risk in project.risks]) if project.risks else "- No risks identified yet"}

**Risk Categories Covered:**
- Technical risks
- Schedule risks  
- Resource risks
- External risks
- Requirements risks

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

retrieve_project_data_tool = FunctionTool(
    retrieve_project_data,
    description="Only call this if explicitly asked to retrieve project data.",
)

save_project_data_tool = FunctionTool(
    save_project_data,
    description="Only call this if explicitly asked to save project data.",
)

create_uuid_tool = FunctionTool(
    create_uuid,
    description="Only call this if explicitly asked to create a uuid.",
)

# Tool instances for user story generation
transfer_to_user_stories_tool = FunctionTool(
    transfer_to_user_stories_agent,
    description="Only call this if explicitly asked to generate user stories or unpack requirements into detailed user stories with acceptance criteria.",
)

transfer_to_user_profiler_tool = FunctionTool(
    transfer_to_user_profiler_agent,
    description="Only call this if explicitly asked to create a user profile.",
)
