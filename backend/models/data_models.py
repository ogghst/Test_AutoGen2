"""
Pydantic data models for the project management system, generated from data_model.yaml.
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Literal, Annotated

from pydantic import BaseModel, Field, EmailStr

def generate_uuid() -> uuid.UUID:
    """Generates a new UUID."""
    return uuid.uuid4()

class TeamMember(BaseModel):
    """Individual team member definition with PMI role responsibilities"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique member identifier")]
    name: Annotated[str, Field(description="Member name", min_length=1, max_length=100)]
    role: Annotated[Literal["Product Owner", "Scrum Master", "Developer", "QA Engineer", "DevOps Engineer", "UX Designer", "Project Manager"], Field(description="Primary role")]
    email: Annotated[EmailStr, Field(description="Contact email")]
    capacity: Annotated[float, Field(description="Weekly availability in hours", ge=0, le=60)]
    is_active: Annotated[bool, Field(default=True, description="Whether the team member is currently active on the project")]

class Deliverable(BaseModel):
    """Tangible or intangible product produced as part of project completion"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique deliverable identifier")]
    name: Annotated[str, Field(description="Deliverable name", min_length=1, max_length=100)]
    description: Annotated[str, Field(description="Deliverable description and acceptance criteria", max_length=500)]
    status: Annotated[Literal["Not Started", "In Progress", "Completed", "Accepted", "Rejected"], Field(description="Deliverable status")]
    acceptance_date: Annotated[Optional[date], Field(default=None, description="Date when deliverable was accepted")]

class Stakeholder(BaseModel):
    """Project stakeholder following PMI stakeholder management"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique stakeholder identifier")]
    name: Annotated[str, Field(description="Stakeholder name", min_length=1, max_length=100)]
    role: Annotated[str, Field(description="Stakeholder role in relation to project")]
    influence: Annotated[Literal["High", "Medium", "Low"], Field(description="Level of influence on project")]
    interest: Annotated[Literal["High", "Medium", "Low"], Field(description="Level of interest in project")]
    communication_preferences: Annotated[str, Field(description="Preferred communication method")]

class Risk(BaseModel):
    """Project risk following PMI risk management framework"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique risk identifier")]
    description: Annotated[str, Field(description="Risk description", min_length=1, max_length=500)]
    category: Annotated[Literal["Technical", "Management", "Organizational", "External", "Requirements"], Field(description="Risk category")]
    probability: Annotated[Literal["High", "Medium", "Low"], Field(description="Probability of occurrence")]
    impact: Annotated[Literal["High", "Medium", "Low"], Field(description="Impact if risk occurs")]
    mitigation_strategy: Annotated[str, Field(description="Planned mitigation strategy")]
    contingency_plan: Annotated[str, Field(description="Contingency plan if risk occurs")]
    status: Annotated[Literal["Identified", "Analyzed", "Planned", "Monitored", "Resolved"], Field(description="Current risk status")]

class Issue(BaseModel):
    """Technical task or problem resolution item with PMI work breakdown structure alignment"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique issue identifier")]
    title: Annotated[str, Field(description="Short descriptive title", min_length=1, max_length=100)]
    description: Annotated[str, Field(description="Detailed technical description", max_length=500)]
    type: Annotated[Literal["Bug", "Task", "Improvement", "Technical Debt", "Spike"], Field(description="Issue type")]
    status: Annotated[Literal["Backlog", "To Do", "In Progress", "Review", "Done", "Blocked"], Field(description="Current status")]
    severity: Annotated[Optional[Literal["Critical", "High", "Medium", "Low"]], Field(default=None, description="Issue severity level")]
    assignee: TeamMember
    estimate_hours: Annotated[float, Field(description="Time estimate in hours", ge=0)]
    actual_hours: Annotated[float, Field(description="Actual time spent in hours", ge=0)]
    due_date: Annotated[date, Field(description="Target completion date")]
    created_date: Annotated[datetime, Field(default_factory=datetime.now, description="Issue creation timestamp")]

class UserStory(BaseModel):
    """End-user perspective feature description with acceptance criteria"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique story identifier")]
    title: Annotated[str, Field(description="Short descriptive title", min_length=1, max_length=100)]
    description: Annotated[str, Field(description="Detailed user story narrative following 'As a... I want... So that...' format", max_length=1000)]
    acceptance_criteria: Annotated[List[str], Field(description="Conditions to satisfy story", min_items=1, max_items=10)]
    definition_of_done: Annotated[Optional[str], Field(default=None, description="Definition of done for this user story", max_length=1000)]
    story_points: Annotated[Literal[1, 2, 3, 5, 8, 13, 21], Field(description="Relative complexity estimate using Fibonacci sequence")]
    issues: List[Issue]
    #epic_id: Annotated[uuid.UUID, Field(description="Parent epic reference")]
    #sprint_id: Annotated[Optional[uuid.UUID], Field(default=None, description="Sprint assignment reference")]
    status: Annotated[Literal["Backlog", "To Do", "In Progress", "Review", "Done"], Field(description="Current story status")]
    priority: Annotated[int, Field(description="Implementation priority (1 is highest)", ge=1, le=10)]

class Epic(BaseModel):
    """Large work body capturing major capability with traceability to business objectives"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique epic identifier")]
    name: Annotated[str, Field(description="Epic name", min_length=1, max_length=100)]
    description: Annotated[str, Field(description="Detailed epic description", max_length=500)]
    business_value: Annotated[int, Field(description="Business value score (1-10)", ge=1, le=10)]
    user_stories: List[UserStory]
    priority: Annotated[Literal["Critical", "High", "Medium", "Low"], Field(description="Business priority")]
    status: Annotated[Literal["Proposed", "Approved", "In Progress", "Completed", "Deferred"], Field(description="Current epic status")]
    created_date: Annotated[datetime, Field(default_factory=datetime.now, description="Epic creation timestamp")]

class Scope(BaseModel):
    """Defines project boundaries and deliverables following PMI scope management"""
    epics: List[Epic]
    inclusions: Annotated[List[str], Field(description="Explicitly included items in scope", max_items=50)]
    exclusions: Annotated[List[str], Field(description="Explicitly excluded items from scope", max_items=50)]
    assumptions: List[str]
    constraints: List[str]
    acceptance_criteria: List[str]

class Team(BaseModel):
    """Group responsible for project delivery with RACI matrix support"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Team identifier")]
    name: Annotated[str, Field(description="Team name", min_length=1, max_length=50)]
    members: List[TeamMember]
    velocity: Annotated[float, Field(description="Team velocity (average story points per sprint)", ge=0)]
    capacity: Annotated[float, Field(description="Total weekly capacity in hours", ge=0)]

class Milestone(BaseModel):
    """Project milestone with deliverable tracking following PMI time management"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique milestone identifier")]
    name: Annotated[str, Field(description="Milestone name", min_length=1, max_length=100)]
    description: Annotated[str, Field(description="Milestone description and significance", max_length=500)]
    target_date: Annotated[date, Field(description="Planned completion date")]
    actual_date: Annotated[Optional[date], Field(default=None, description="Actual completion date")]
    deliverables: List[Deliverable]
    status: Annotated[Literal["Planned", "At Risk", "Achieved", "Missed"], Field(description="Milestone status")]

class Sprint(BaseModel):
    """Time-boxed iteration in agile development"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique sprint identifier")]
    name: Annotated[str, Field(description="Sprint name/number", min_length=1, max_length=50)]
    goal: Annotated[str, Field(description="Sprint goal", max_length=200)]
    start_date: Annotated[date, Field(description="Sprint start date")]
    end_date: Annotated[date, Field(description="Sprint end date")]
    velocity: Annotated[float, Field(description="Actual velocity achieved in this sprint", ge=0)]
    retrospective_notes: Annotated[Optional[str], Field(default=None, description="Notes from sprint retrospective")]
    daily_standup_notes: Annotated[Optional[str], Field(default=None, description="Notes from daily stand-up meetings", max_length=2000)]
    review_notes: Annotated[Optional[str], Field(default=None, description="Notes from sprint review/demo", max_length=2000)]

class Project(BaseModel):
    """Root entity representing the entire software project with PMI governance"""
    id: Annotated[uuid.UUID, Field(default_factory=generate_uuid, description="Unique project identifier following PMI standards")]
    name: Annotated[str, Field(description="Project name", min_length=1, max_length=100)]
    vision: Annotated[str, Field(description="Project vision statement guiding agile execution", max_length=500)]
    methodology: Annotated[Literal["Agile", "Scrum", "Kanban", "XP", "Hybrid"], Field(default="Agile", description="Project methodology")]
    description: Annotated[str, Field(description="Project charter description", max_length=1000)]
    release_plan: Annotated[Optional[str], Field(default=None, description="High-level release plan and roadmap", max_length=1000)]
    team: Team
    scope: Scope
    stakeholders: List[Stakeholder]
    risks: List[Risk]
    milestones: List[Milestone]
    status: Annotated[Literal["Initiation", "Planning", "Execution", "Monitoring", "Closing"], Field(description="Current project status")]
    created_date: Annotated[datetime, Field(default_factory=datetime.now, description="Project creation timestamp")]
    last_updated: Annotated[datetime, Field(default_factory=datetime.now, description="Last project update timestamp")]
    knowledge_transfer: Annotated[Optional[str], Field(default=None, description="Knowledge transfer activities and documentation", max_length=1000)]