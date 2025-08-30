from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'pm',
     'default_range': 'string',
     'description': 'Comprehensive data model integrating PMI standards with Agile '
                    'practices, supporting hybrid methodologies and full lifecycle '
                    'documentation generation',
     'id': 'https://example.org/software_project_management',
     'imports': ['linkml:types'],
     'license': 'https://creativecommons.org/publicdomain/zero/1.0/',
     'name': 'software_project_management',
     'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'pm': {'prefix_prefix': 'pm',
                         'prefix_reference': 'https://example.org/software_project_management/'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'}},
     'source_file': 'data_model_linkml_enhanced.yaml',
     'title': 'Enhanced Agile Project Management Data Model',
     'types': {'date': {'base': 'str',
                        'description': 'Date in YYYY-MM-DD format',
                        'from_schema': 'https://example.org/software_project_management',
                        'name': 'date',
                        'pattern': '^\\d{4}-\\d{2}-\\d{2}$',
                        'uri': 'xsd:date'},
               'datetime': {'base': 'str',
                            'description': 'A date with time information',
                            'from_schema': 'https://example.org/software_project_management',
                            'name': 'datetime',
                            'pattern': '^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$',
                            'uri': 'xsd:dateTime'},
               'email': {'base': 'str',
                         'description': 'A valid email address',
                         'from_schema': 'https://example.org/software_project_management',
                         'name': 'email',
                         'pattern': '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
                         'uri': 'xsd:string'},
               'percentage': {'base': 'float',
                              'description': 'Percentage value between 0 and 100',
                              'from_schema': 'https://example.org/software_project_management',
                              'maximum_value': 100,
                              'minimum_value': 0,
                              'name': 'percentage',
                              'uri': 'xsd:float'},
               'uuid': {'base': 'str',
                        'description': 'UUIDv4 identifier',
                        'from_schema': 'https://example.org/software_project_management',
                        'name': 'uuid',
                        'pattern': '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$',
                        'uri': 'xsd:string'}}} )

class MethodologyEnum(str, Enum):
    """
    Software development methodologies and frameworks
    """
    Scrum = "Scrum"
    """
    Framework with fixed-length sprints and defined roles
    """
    Kanban = "Kanban"
    """
    Flow-based method with continuous delivery
    """
    XP = "XP"
    """
    Extreme Programming with technical excellence focus
    """
    Hybrid = "Hybrid"
    """
    Combination of predictive and adaptive approaches
    """
    Waterfall = "Waterfall"
    """
    Sequential phase-based approach
    """


class SDLCPhaseEnum(str, Enum):
    """
    Software Development Life Cycle phases
    """
    Concept = "Concept"
    Inception = "Inception"
    Iteration = "Iteration"
    Release = "Release"
    Maintenance = "Maintenance"
    Retirement = "Retirement"


class ProjectStatusEnum(str, Enum):
    """
    Project lifecycle status values
    """
    Initiation = "Initiation"
    Planning = "Planning"
    Execution = "Execution"
    Monitoring = "Monitoring"
    Closing = "Closing"


class PriorityEnum(str, Enum):
    """
    Priority levels for work items and tasks
    """
    Critical = "Critical"
    High = "High"
    Medium = "Medium"
    Low = "Low"


class EpicStatusEnum(str, Enum):
    """
    Status values for epic work items
    """
    Proposed = "Proposed"
    Approved = "Approved"
    In_Progress = "In Progress"
    Completed = "Completed"
    Deferred = "Deferred"


class UserStoryStatusEnum(str, Enum):
    """
    Status values for user stories
    """
    Backlog = "Backlog"
    To_Do = "To Do"
    In_Progress = "In Progress"
    Review = "Review"
    Done = "Done"


class IssueTypeEnum(str, Enum):
    """
    Types of issues that can be tracked
    """
    Bug = "Bug"
    Task = "Task"
    Improvement = "Improvement"
    Technical_Debt = "Technical Debt"
    Spike = "Spike"


class IssueStatusEnum(str, Enum):
    """
    Status values for issue tracking
    """
    Backlog = "Backlog"
    To_Do = "To Do"
    In_Progress = "In Progress"
    Review = "Review"
    Done = "Done"
    Blocked = "Blocked"


class SeverityEnum(str, Enum):
    """
    Severity levels for issues and risks
    """
    Critical = "Critical"
    High = "High"
    Medium = "Medium"
    Low = "Low"


class RoleEnum(str, Enum):
    """
    Team member roles in the project
    """
    Product_Owner = "Product Owner"
    Scrum_Master = "Scrum Master"
    Developer = "Developer"
    QA_Engineer = "QA Engineer"
    DevOps_Engineer = "DevOps Engineer"
    UX_Designer = "UX Designer"
    Project_Manager = "Project Manager"
    Business_Analyst = "Business Analyst"
    Sponsor = "Sponsor"


class InfluenceLevelEnum(str, Enum):
    """
    Levels of influence for stakeholders
    """
    High = "High"
    Medium = "Medium"
    Low = "Low"


class InterestLevelEnum(str, Enum):
    """
    Levels of interest for stakeholders
    """
    High = "High"
    Medium = "Medium"
    Low = "Low"


class RiskCategoryEnum(str, Enum):
    """
    Categories of project risks
    """
    Technical = "Technical"
    Management = "Management"
    Organizational = "Organizational"
    External = "External"
    Requirements = "Requirements"


class RiskStatusEnum(str, Enum):
    """
    Status values for risk management
    """
    Identified = "Identified"
    Analyzed = "Analyzed"
    Planned = "Planned"
    Monitored = "Monitored"
    Resolved = "Resolved"


class MilestoneStatusEnum(str, Enum):
    """
    Status values for project milestones
    """
    Planned = "Planned"
    At_Risk = "At Risk"
    Achieved = "Achieved"
    Missed = "Missed"


class DeliverableStatusEnum(str, Enum):
    """
    Status values for project deliverables
    """
    Not_Started = "Not Started"
    In_Progress = "In Progress"
    Completed = "Completed"
    Accepted = "Accepted"
    Rejected = "Rejected"


class ChangeTypeEnum(str, Enum):
    """
    Types of change requests
    """
    Corrective = "Corrective"
    Preventive = "Preventive"
    Defect = "Defect"
    Enhancement = "Enhancement"
    Emergency = "Emergency"


class ApprovalStatusEnum(str, Enum):
    """
    Status values for approval workflows
    """
    Proposed = "Proposed"
    Under_Review = "Under_Review"
    Approved = "Approved"
    Rejected = "Rejected"
    Deferred = "Deferred"


class TestTypeEnum(str, Enum):
    """
    Types of software testing
    """
    Unit = "Unit"
    Integration = "Integration"
    System = "System"
    Acceptance = "Acceptance"
    Regression = "Regression"
    Performance = "Performance"


class AgileArtifactStatusEnum(str, Enum):
    """
    Status values for Agile artifacts
    """
    Draft = "Draft"
    Review = "Review"
    Approved = "Approved"
    Archived = "Archived"


class DocumentationTypeEnum(str, Enum):
    """
    Types of project documentation
    """
    Charter = "Charter"
    Requirements = "Requirements"
    Design = "Design"
    Technical = "Technical"
    User = "User"
    Process = "Process"
    Report = "Report"


class RepositoryTypeEnum(str, Enum):
    """
    Types of project repositories
    """
    Code = "Code"
    Documentation = "Documentation"
    Design = "Design"
    Requirements = "Requirements"
    Test = "Test"


class StoryPointsEnum(str, Enum):
    """
    Fibonacci sequence values used for story point estimation in Agile methodologies.
    """
    number_1 = "1"
    number_2 = "2"
    number_3 = "3"
    number_5 = "5"
    number_8 = "8"
    number_13 = "13"
    number_21 = "21"



class Project(ConfiguredBaseModel):
    """
    Root entity representing the entire software project
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'methodology': {'name': 'methodology',
                                        'range': 'MethodologyEnum',
                                        'required': True},
                        'sdlc_phase': {'name': 'sdlc_phase',
                                       'range': 'SDLCPhaseEnum',
                                       'required': True},
                        'status': {'name': 'status', 'range': 'ProjectStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    vision: Optional[str] = Field(default=None, description="""Project vision statement""", le=500, json_schema_extra = { "linkml_meta": {'alias': 'vision', 'domain_of': ['Project']} })
    methodology: MethodologyEnum = Field(default=..., description="""Project methodology""", json_schema_extra = { "linkml_meta": {'alias': 'methodology', 'domain_of': ['Project']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    business_case: Optional[str] = Field(default=None, description="""Project business case""", json_schema_extra = { "linkml_meta": {'alias': 'business_case', 'domain_of': ['Project']} })
    sdlc_phase: SDLCPhaseEnum = Field(default=..., description="""Current SDLC phase""", json_schema_extra = { "linkml_meta": {'alias': 'sdlc_phase', 'domain_of': ['Project']} })
    release_plan: Optional[str] = Field(default=None, description="""High-level release plan""", le=1000, json_schema_extra = { "linkml_meta": {'alias': 'release_plan', 'domain_of': ['Project']} })
    team: Optional[str] = Field(default=None, description="""Assigned project team""", json_schema_extra = { "linkml_meta": {'alias': 'team', 'domain_of': ['Project', 'WorkStream']} })
    scope: Optional[Scope] = Field(default=None, description="""Project scope definition""", json_schema_extra = { "linkml_meta": {'alias': 'scope', 'domain_of': ['Project']} })
    stakeholders: Optional[list[str]] = Field(default=None, description="""Project stakeholders""", json_schema_extra = { "linkml_meta": {'alias': 'stakeholders', 'domain_of': ['Project']} })
    risks: Optional[list[str]] = Field(default=None, description="""Project risks""", json_schema_extra = { "linkml_meta": {'alias': 'risks', 'domain_of': ['Project']} })
    milestones: Optional[list[str]] = Field(default=None, description="""Project milestones""", json_schema_extra = { "linkml_meta": {'alias': 'milestones', 'domain_of': ['Project']} })
    phases: Optional[list[str]] = Field(default=None, description="""Project phases""", json_schema_extra = { "linkml_meta": {'alias': 'phases', 'domain_of': ['Project']} })
    status: Optional[ProjectStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    created_date: Optional[str] = Field(default=None, description="""Creation timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'created_date',
         'domain_of': ['Project', 'Requirement', 'Epic', 'Issue', 'Documentation']} })
    last_updated: Optional[str] = Field(default=None, description="""Last update timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'last_updated',
         'domain_of': ['Project', 'Requirement', 'Documentation']} })
    knowledge_transfer: Optional[str] = Field(default=None, description="""Knowledge transfer activities""", le=1000, json_schema_extra = { "linkml_meta": {'alias': 'knowledge_transfer', 'domain_of': ['Project']} })
    change_requests: Optional[list[str]] = Field(default=None, description="""Change requests""", json_schema_extra = { "linkml_meta": {'alias': 'change_requests', 'domain_of': ['Project']} })
    baselines: Optional[list[str]] = Field(default=None, description="""Project baselines""", json_schema_extra = { "linkml_meta": {'alias': 'baselines', 'domain_of': ['Project']} })
    repositories: Optional[list[str]] = Field(default=None, description="""Project repositories""", json_schema_extra = { "linkml_meta": {'alias': 'repositories', 'domain_of': ['Project']} })
    ai_work_products: Optional[list[str]] = Field(default=None, description="""AI-generated work products""", json_schema_extra = { "linkml_meta": {'alias': 'ai_work_products', 'domain_of': ['Project']} })


class BusinessCase(ConfiguredBaseModel):
    """
    Justification for the project including financial and strategic considerations
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    project_id: Optional[str] = Field(default=None, description="""Reference to the project this belongs to""", json_schema_extra = { "linkml_meta": {'alias': 'project_id', 'domain_of': ['BusinessCase']} })
    problem_statement: Optional[str] = Field(default=None, description="""Problem statement""", json_schema_extra = { "linkml_meta": {'alias': 'problem_statement', 'domain_of': ['BusinessCase']} })
    business_objectives: Optional[list[str]] = Field(default=None, description="""Business objectives""", json_schema_extra = { "linkml_meta": {'alias': 'business_objectives', 'domain_of': ['BusinessCase']} })
    benefits: Optional[list[str]] = Field(default=None, description="""Expected benefits""", json_schema_extra = { "linkml_meta": {'alias': 'benefits', 'domain_of': ['BusinessCase']} })
    costs: Optional[str] = Field(default=None, description="""Estimated costs""", json_schema_extra = { "linkml_meta": {'alias': 'costs', 'domain_of': ['BusinessCase']} })
    roi_analysis: Optional[str] = Field(default=None, description="""ROI analysis""", json_schema_extra = { "linkml_meta": {'alias': 'roi_analysis', 'domain_of': ['BusinessCase']} })
    alternatives_analysis: Optional[str] = Field(default=None, description="""Alternatives analysis""", json_schema_extra = { "linkml_meta": {'alias': 'alternatives_analysis', 'domain_of': ['BusinessCase']} })
    recommendation: Optional[str] = Field(default=None, description="""Recommendation""", json_schema_extra = { "linkml_meta": {'alias': 'recommendation', 'domain_of': ['BusinessCase']} })
    approval_status: Optional[ApprovalStatusEnum] = Field(default=None, description="""Approval status""", json_schema_extra = { "linkml_meta": {'alias': 'approval_status', 'domain_of': ['BusinessCase']} })
    approved_date: Optional[str] = Field(default=None, description="""Approval date""", json_schema_extra = { "linkml_meta": {'alias': 'approved_date', 'domain_of': ['BusinessCase', 'Baseline']} })


class Scope(ConfiguredBaseModel):
    """
    Project scope definition with inclusions, exclusions, and constraints
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    epics: Optional[list[str]] = Field(default=None, description="""Collection of epics""", json_schema_extra = { "linkml_meta": {'alias': 'epics', 'domain_of': ['Scope']} })
    inclusions: Optional[list[str]] = Field(default=None, description="""Included items in scope""", le=50, json_schema_extra = { "linkml_meta": {'alias': 'inclusions', 'domain_of': ['Scope']} })
    exclusions: Optional[list[str]] = Field(default=None, description="""Excluded items from scope""", le=50, json_schema_extra = { "linkml_meta": {'alias': 'exclusions', 'domain_of': ['Scope']} })
    assumptions: Optional[list[str]] = Field(default=None, description="""Scope assumptions""", json_schema_extra = { "linkml_meta": {'alias': 'assumptions', 'domain_of': ['Scope']} })
    constraints: Optional[list[str]] = Field(default=None, description="""Scope constraints""", json_schema_extra = { "linkml_meta": {'alias': 'constraints', 'domain_of': ['Scope']} })
    acceptance_criteria: Optional[list[str]] = Field(default=None, description="""Acceptance criteria""", json_schema_extra = { "linkml_meta": {'alias': 'acceptance_criteria',
         'domain_of': ['Scope', 'Requirement', 'UserStory', 'Milestone']} })
    requirements: Optional[list[str]] = Field(default=None, description="""Project requirements""", json_schema_extra = { "linkml_meta": {'alias': 'requirements', 'domain_of': ['Scope']} })


class Requirement(ConfiguredBaseModel):
    """
    Single discrete requirement with unique identifier and traceability
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    category: Optional[RiskCategoryEnum] = Field(default=None, description="""Risk category""", json_schema_extra = { "linkml_meta": {'alias': 'category', 'domain_of': ['Requirement', 'Risk']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    status: Optional[str] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    source: Optional[str] = Field(default=None, description="""Source of the requirement""", json_schema_extra = { "linkml_meta": {'alias': 'source', 'domain_of': ['Requirement']} })
    acceptance_criteria: Optional[list[str]] = Field(default=None, description="""Acceptance criteria""", json_schema_extra = { "linkml_meta": {'alias': 'acceptance_criteria',
         'domain_of': ['Scope', 'Requirement', 'UserStory', 'Milestone']} })
    created_date: Optional[str] = Field(default=None, description="""Creation timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'created_date',
         'domain_of': ['Project', 'Requirement', 'Epic', 'Issue', 'Documentation']} })
    last_updated: Optional[str] = Field(default=None, description="""Last update timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'last_updated',
         'domain_of': ['Project', 'Requirement', 'Documentation']} })


class Epic(ConfiguredBaseModel):
    """
    Large work body capturing major capability with traceability to business objectives
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'description': {'maximum_value': 500, 'name': 'description'},
                        'status': {'name': 'status', 'range': 'EpicStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", le=500, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    business_value: Optional[int] = Field(default=None, description="""Business value score (1-10)""", ge=1, le=10, json_schema_extra = { "linkml_meta": {'alias': 'business_value', 'domain_of': ['Epic', 'BacklogItem']} })
    user_stories: Optional[list[str]] = Field(default=None, description="""User stories""", json_schema_extra = { "linkml_meta": {'alias': 'user_stories', 'domain_of': ['Epic']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    status: Optional[EpicStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    created_date: Optional[str] = Field(default=None, description="""Creation timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'created_date',
         'domain_of': ['Project', 'Requirement', 'Epic', 'Issue', 'Documentation']} })
    target_release: Optional[str] = Field(default=None, description="""Target release version""", json_schema_extra = { "linkml_meta": {'alias': 'target_release', 'domain_of': ['Epic']} })


class UserStory(ConfiguredBaseModel):
    """
    End-user perspective feature description with acceptance criteria
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'acceptance_criteria': {'maximum_value': 10,
                                                'minimum_value': 1,
                                                'name': 'acceptance_criteria',
                                                'required': True},
                        'description': {'maximum_value': 1000, 'name': 'description'},
                        'status': {'name': 'status', 'range': 'UserStoryStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    title: str = Field(default=..., description="""Short descriptive title""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['UserStory', 'Issue', 'Documentation']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", le=1000, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    acceptance_criteria: list[str] = Field(default=..., description="""Acceptance criteria""", ge=1, le=10, json_schema_extra = { "linkml_meta": {'alias': 'acceptance_criteria',
         'domain_of': ['Scope', 'Requirement', 'UserStory', 'Milestone']} })
    definition_of_done: Optional[str] = Field(default=None, description="""Definition of done criteria""", le=1000, json_schema_extra = { "linkml_meta": {'alias': 'definition_of_done', 'domain_of': ['UserStory']} })
    story_points: StoryPointsEnum = Field(default=..., description="""Relative complexity estimate using Fibonacci sequence.""", json_schema_extra = { "linkml_meta": {'alias': 'story_points', 'domain_of': ['UserStory']} })
    issues: Optional[list[str]] = Field(default=None, description="""Associated issues""", json_schema_extra = { "linkml_meta": {'alias': 'issues', 'domain_of': ['UserStory']} })
    epic_id: Optional[str] = Field(default=None, description="""Parent epic reference""", json_schema_extra = { "linkml_meta": {'alias': 'epic_id', 'domain_of': ['UserStory']} })
    sprint_id: Optional[str] = Field(default=None, description="""Sprint assignment reference""", json_schema_extra = { "linkml_meta": {'alias': 'sprint_id', 'domain_of': ['UserStory']} })
    status: Optional[UserStoryStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    tests: Optional[list[str]] = Field(default=None, description="""Associated test cases""", json_schema_extra = { "linkml_meta": {'alias': 'tests', 'domain_of': ['UserStory']} })
    technical_notes: Optional[str] = Field(default=None, description="""Technical notes""", json_schema_extra = { "linkml_meta": {'alias': 'technical_notes', 'domain_of': ['UserStory']} })


class Backlog(ConfiguredBaseModel):
    """
    Ordered list of work items awaiting execution
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    items: Optional[list[str]] = Field(default=None, description="""Backlog items""", json_schema_extra = { "linkml_meta": {'alias': 'items', 'domain_of': ['Backlog']} })
    prioritization_method: Optional[str] = Field(default=None, description="""Prioritization method""", json_schema_extra = { "linkml_meta": {'alias': 'prioritization_method', 'domain_of': ['Backlog']} })
    last_prioritized_date: Optional[str] = Field(default=None, description="""Last prioritization date""", json_schema_extra = { "linkml_meta": {'alias': 'last_prioritized_date', 'domain_of': ['Backlog']} })


class BacklogItem(ConfiguredBaseModel):
    """
    Single item in a backlog with estimation and prioritization data
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    estimate: Optional[int] = Field(default=None, description="""Effort estimate""", json_schema_extra = { "linkml_meta": {'alias': 'estimate', 'domain_of': ['BacklogItem']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    risk_level: Optional[SeverityEnum] = Field(default=None, description="""Risk level""", json_schema_extra = { "linkml_meta": {'alias': 'risk_level', 'domain_of': ['BacklogItem']} })
    business_value: Optional[int] = Field(default=None, description="""Business value score (1-10)""", ge=1, le=10, json_schema_extra = { "linkml_meta": {'alias': 'business_value', 'domain_of': ['Epic', 'BacklogItem']} })
    dependencies: Optional[list[str]] = Field(default=None, description="""Dependencies""", json_schema_extra = { "linkml_meta": {'alias': 'dependencies', 'domain_of': ['BacklogItem', 'WorkStream']} })
    tags: Optional[list[str]] = Field(default=None, description="""Tags""", json_schema_extra = { "linkml_meta": {'alias': 'tags', 'domain_of': ['BacklogItem']} })


class Sprint(ConfiguredBaseModel):
    """
    Time-boxed iteration typically 1-4 weeks in duration
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'name': {'maximum_value': 50, 'name': 'name'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=50, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    goal: Optional[str] = Field(default=None, description="""Goal description""", le=200, json_schema_extra = { "linkml_meta": {'alias': 'goal', 'domain_of': ['Sprint']} })
    start_date: Optional[str] = Field(default=None, description="""Start date""", json_schema_extra = { "linkml_meta": {'alias': 'start_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    end_date: Optional[str] = Field(default=None, description="""End date""", json_schema_extra = { "linkml_meta": {'alias': 'end_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    velocity: Optional[float] = Field(default=None, description="""Team velocity""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'velocity', 'domain_of': ['Sprint', 'Team']} })
    retrospective_notes: Optional[str] = Field(default=None, description="""Retrospective notes""", json_schema_extra = { "linkml_meta": {'alias': 'retrospective_notes', 'domain_of': ['Sprint']} })
    daily_standup_notes: Optional[str] = Field(default=None, description="""Daily standup notes""", le=2000, json_schema_extra = { "linkml_meta": {'alias': 'daily_standup_notes', 'domain_of': ['Sprint']} })
    review_notes: Optional[str] = Field(default=None, description="""Review notes""", le=2000, json_schema_extra = { "linkml_meta": {'alias': 'review_notes', 'domain_of': ['Sprint']} })
    backlog_items: Optional[list[str]] = Field(default=None, description="""Items in the backlog""", json_schema_extra = { "linkml_meta": {'alias': 'backlog_items', 'domain_of': ['Sprint']} })
    committed_velocity: Optional[float] = Field(default=None, description="""Committed velocity""", json_schema_extra = { "linkml_meta": {'alias': 'committed_velocity', 'domain_of': ['Sprint']} })
    actual_velocity: Optional[float] = Field(default=None, description="""Actual velocity""", json_schema_extra = { "linkml_meta": {'alias': 'actual_velocity', 'domain_of': ['Sprint']} })


class Issue(ConfiguredBaseModel):
    """
    Technical task or problem resolution item
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'description': {'maximum_value': 500, 'name': 'description'},
                        'status': {'name': 'status', 'range': 'IssueStatusEnum'},
                        'type': {'name': 'type', 'range': 'IssueTypeEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    title: str = Field(default=..., description="""Short descriptive title""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['UserStory', 'Issue', 'Documentation']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", le=500, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    type: Optional[IssueTypeEnum] = Field(default=None, description="""Type classification""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Issue',
                       'ChangeRequest',
                       'TestCase',
                       'Documentation',
                       'Repository']} })
    status: Optional[IssueStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    severity: Optional[SeverityEnum] = Field(default=None, description="""Severity level""", json_schema_extra = { "linkml_meta": {'alias': 'severity', 'domain_of': ['Issue']} })
    assignee: Optional[str] = Field(default=None, description="""Assigned person""", json_schema_extra = { "linkml_meta": {'alias': 'assignee', 'domain_of': ['Issue']} })
    estimate_hours: Optional[float] = Field(default=None, description="""Time estimate in hours""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'estimate_hours', 'domain_of': ['Issue']} })
    actual_hours: Optional[float] = Field(default=None, description="""Actual time spent in hours""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'actual_hours', 'domain_of': ['Issue']} })
    due_date: Optional[str] = Field(default=None, description="""Target completion date""", json_schema_extra = { "linkml_meta": {'alias': 'due_date', 'domain_of': ['Issue']} })
    created_date: Optional[str] = Field(default=None, description="""Creation timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'created_date',
         'domain_of': ['Project', 'Requirement', 'Epic', 'Issue', 'Documentation']} })
    root_cause: Optional[str] = Field(default=None, description="""Root cause analysis""", json_schema_extra = { "linkml_meta": {'alias': 'root_cause', 'domain_of': ['Issue']} })
    resolution: Optional[str] = Field(default=None, description="""Resolution description""", json_schema_extra = { "linkml_meta": {'alias': 'resolution', 'domain_of': ['Issue']} })
    reproduction_steps: Optional[str] = Field(default=None, description="""Reproduction steps""", json_schema_extra = { "linkml_meta": {'alias': 'reproduction_steps', 'domain_of': ['Issue']} })
    detected_version: Optional[str] = Field(default=None, description="""Detected in version""", json_schema_extra = { "linkml_meta": {'alias': 'detected_version', 'domain_of': ['Issue']} })
    resolved_version: Optional[str] = Field(default=None, description="""Resolved in version""", json_schema_extra = { "linkml_meta": {'alias': 'resolved_version', 'domain_of': ['Issue']} })


class Team(ConfiguredBaseModel):
    """
    Cross-functional team responsible for project delivery
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    members: Optional[list[str]] = Field(default=None, description="""Team members""", json_schema_extra = { "linkml_meta": {'alias': 'members', 'domain_of': ['Team']} })
    velocity: Optional[float] = Field(default=None, description="""Team velocity""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'velocity', 'domain_of': ['Sprint', 'Team']} })
    capacity: Optional[float] = Field(default=None, description="""Weekly capacity in hours""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'capacity', 'domain_of': ['Team', 'TeamMember']} })
    focus_factor: Optional[float] = Field(default=None, description="""Team focus factor""", json_schema_extra = { "linkml_meta": {'alias': 'focus_factor', 'domain_of': ['Team']} })
    process_maturity: Optional[int] = Field(default=None, description="""Process maturity level (1-5)""", ge=1, le=5, json_schema_extra = { "linkml_meta": {'alias': 'process_maturity', 'domain_of': ['Team']} })
    collaboration_tools: Optional[list[str]] = Field(default=None, description="""Collaboration tools""", json_schema_extra = { "linkml_meta": {'alias': 'collaboration_tools', 'domain_of': ['Team']} })


class Risk(ConfiguredBaseModel):
    """
    Project risk following PMI risk management framework
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'description': {'maximum_value': 500,
                                        'minimum_value': 1,
                                        'name': 'description',
                                        'required': True},
                        'status': {'name': 'status', 'range': 'RiskStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    description: str = Field(default=..., description="""Detailed description""", ge=1, le=500, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    category: Optional[RiskCategoryEnum] = Field(default=None, description="""Risk category""", json_schema_extra = { "linkml_meta": {'alias': 'category', 'domain_of': ['Requirement', 'Risk']} })
    probability: Optional[InfluenceLevelEnum] = Field(default=None, description="""Probability of occurrence""", json_schema_extra = { "linkml_meta": {'alias': 'probability', 'domain_of': ['Risk']} })
    impact: Optional[InfluenceLevelEnum] = Field(default=None, description="""Impact level""", json_schema_extra = { "linkml_meta": {'alias': 'impact', 'domain_of': ['Risk']} })
    mitigation_strategy: Optional[str] = Field(default=None, description="""Mitigation strategy""", json_schema_extra = { "linkml_meta": {'alias': 'mitigation_strategy', 'domain_of': ['Risk']} })
    contingency_plan: Optional[str] = Field(default=None, description="""Contingency plan""", json_schema_extra = { "linkml_meta": {'alias': 'contingency_plan', 'domain_of': ['Risk']} })
    status: Optional[RiskStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    triggers: Optional[list[str]] = Field(default=None, description="""Risk triggers""", json_schema_extra = { "linkml_meta": {'alias': 'triggers', 'domain_of': ['Risk']} })
    owner: Optional[str] = Field(default=None, description="""Owner""", json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['Risk', 'Documentation', 'CommunicationPlan']} })


class Milestone(ConfiguredBaseModel):
    """
    Significant point in project timeline with deliverable tracking
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'description': {'maximum_value': 500, 'name': 'description'},
                        'status': {'name': 'status', 'range': 'MilestoneStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", le=500, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    target_date: Optional[str] = Field(default=None, description="""Planned completion date""", json_schema_extra = { "linkml_meta": {'alias': 'target_date', 'domain_of': ['Milestone']} })
    actual_date: Optional[str] = Field(default=None, description="""Actual completion date""", json_schema_extra = { "linkml_meta": {'alias': 'actual_date', 'domain_of': ['Milestone']} })
    deliverables: Optional[list[str]] = Field(default=None, description="""Associated deliverables""", json_schema_extra = { "linkml_meta": {'alias': 'deliverables', 'domain_of': ['Milestone', 'Phase', 'WorkStream']} })
    status: Optional[MilestoneStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    acceptance_criteria: Optional[list[str]] = Field(default=None, description="""Acceptance criteria""", json_schema_extra = { "linkml_meta": {'alias': 'acceptance_criteria',
         'domain_of': ['Scope', 'Requirement', 'UserStory', 'Milestone']} })


class Deliverable(ConfiguredBaseModel):
    """
    Tangible or intangible product produced as part of project completion
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'description': {'maximum_value': 500, 'name': 'description'},
                        'status': {'name': 'status', 'range': 'DeliverableStatusEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", le=500, json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    status: Optional[DeliverableStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    acceptance_date: Optional[str] = Field(default=None, description="""Acceptance date""", json_schema_extra = { "linkml_meta": {'alias': 'acceptance_date', 'domain_of': ['Deliverable']} })
    quality_metrics: Optional[str] = Field(default=None, description="""Quality metrics""", json_schema_extra = { "linkml_meta": {'alias': 'quality_metrics', 'domain_of': ['Deliverable']} })
    storage_location: Optional[str] = Field(default=None, description="""Storage location""", json_schema_extra = { "linkml_meta": {'alias': 'storage_location', 'domain_of': ['Deliverable']} })
    version: Optional[str] = Field(default=None, description="""Version""", json_schema_extra = { "linkml_meta": {'alias': 'version', 'domain_of': ['Deliverable', 'Baseline', 'Documentation']} })


class ChangeRequest(ConfiguredBaseModel):
    """
    Formal request to modify project baselines
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'status': {'name': 'status', 'range': 'ApprovalStatusEnum'},
                        'type': {'name': 'type', 'range': 'ChangeTypeEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    rationale: Optional[str] = Field(default=None, description="""Rationale""", json_schema_extra = { "linkml_meta": {'alias': 'rationale', 'domain_of': ['ChangeRequest']} })
    impact_analysis: Optional[str] = Field(default=None, description="""Impact analysis""", json_schema_extra = { "linkml_meta": {'alias': 'impact_analysis', 'domain_of': ['ChangeRequest']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    type: Optional[ChangeTypeEnum] = Field(default=None, description="""Type classification""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Issue',
                       'ChangeRequest',
                       'TestCase',
                       'Documentation',
                       'Repository']} })
    status: Optional[ApprovalStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    submitted_by: Optional[str] = Field(default=None, description="""Submitted by""", json_schema_extra = { "linkml_meta": {'alias': 'submitted_by', 'domain_of': ['ChangeRequest']} })
    submitted_date: Optional[str] = Field(default=None, description="""Submission date""", json_schema_extra = { "linkml_meta": {'alias': 'submitted_date', 'domain_of': ['ChangeRequest']} })
    decision: Optional[str] = Field(default=None, description="""Decision""", json_schema_extra = { "linkml_meta": {'alias': 'decision', 'domain_of': ['ChangeRequest']} })
    decision_date: Optional[str] = Field(default=None, description="""Decision date""", json_schema_extra = { "linkml_meta": {'alias': 'decision_date', 'domain_of': ['ChangeRequest']} })
    decision_maker: Optional[str] = Field(default=None, description="""Decision maker""", json_schema_extra = { "linkml_meta": {'alias': 'decision_maker', 'domain_of': ['ChangeRequest']} })


class Baseline(ConfiguredBaseModel):
    """
    Approved version of scope, schedule, or cost used for comparison
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    version: Optional[str] = Field(default=None, description="""Version""", json_schema_extra = { "linkml_meta": {'alias': 'version', 'domain_of': ['Deliverable', 'Baseline', 'Documentation']} })
    approved_date: Optional[str] = Field(default=None, description="""Approval date""", json_schema_extra = { "linkml_meta": {'alias': 'approved_date', 'domain_of': ['BusinessCase', 'Baseline']} })
    approved_by: Optional[str] = Field(default=None, description="""Person who approved the baseline""", json_schema_extra = { "linkml_meta": {'alias': 'approved_by', 'domain_of': ['Baseline']} })
    elements: Optional[list[str]] = Field(default=None, description="""Baseline elements""", json_schema_extra = { "linkml_meta": {'alias': 'elements', 'domain_of': ['Baseline']} })


class TestCase(ConfiguredBaseModel):
    """
    Verifiable condition for requirement validation
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'type': {'name': 'type', 'range': 'TestTypeEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    test_steps: Optional[list[str]] = Field(default=None, description="""Test steps""", json_schema_extra = { "linkml_meta": {'alias': 'test_steps', 'domain_of': ['TestCase']} })
    expected_result: Optional[str] = Field(default=None, description="""Expected result""", json_schema_extra = { "linkml_meta": {'alias': 'expected_result', 'domain_of': ['TestCase']} })
    actual_result: Optional[str] = Field(default=None, description="""Actual result""", json_schema_extra = { "linkml_meta": {'alias': 'actual_result', 'domain_of': ['TestCase']} })
    status: Optional[str] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    type: Optional[TestTypeEnum] = Field(default=None, description="""Type classification""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Issue',
                       'ChangeRequest',
                       'TestCase',
                       'Documentation',
                       'Repository']} })
    priority: Optional[PriorityEnum] = Field(default=None, description="""Priority level""", json_schema_extra = { "linkml_meta": {'alias': 'priority',
         'domain_of': ['Requirement',
                       'Epic',
                       'UserStory',
                       'BacklogItem',
                       'ChangeRequest',
                       'TestCase']} })
    associated_requirement: Optional[str] = Field(default=None, description="""Associated requirement""", json_schema_extra = { "linkml_meta": {'alias': 'associated_requirement', 'domain_of': ['TestCase', 'AIWorkProduct']} })
    automated: Optional[bool] = Field(default=None, description="""Automated test""", json_schema_extra = { "linkml_meta": {'alias': 'automated', 'domain_of': ['TestCase']} })
    last_tested: Optional[str] = Field(default=None, description="""Last tested date""", json_schema_extra = { "linkml_meta": {'alias': 'last_tested', 'domain_of': ['TestCase']} })


class Phase(ConfiguredBaseModel):
    """
    Distinct time period in predictive project lifecycles
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    start_date: Optional[str] = Field(default=None, description="""Start date""", json_schema_extra = { "linkml_meta": {'alias': 'start_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    end_date: Optional[str] = Field(default=None, description="""End date""", json_schema_extra = { "linkml_meta": {'alias': 'end_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    deliverables: Optional[list[str]] = Field(default=None, description="""Associated deliverables""", json_schema_extra = { "linkml_meta": {'alias': 'deliverables', 'domain_of': ['Milestone', 'Phase', 'WorkStream']} })
    entrance_criteria: Optional[str] = Field(default=None, description="""Entrance criteria""", json_schema_extra = { "linkml_meta": {'alias': 'entrance_criteria', 'domain_of': ['Phase']} })
    exit_criteria: Optional[str] = Field(default=None, description="""Exit criteria""", json_schema_extra = { "linkml_meta": {'alias': 'exit_criteria', 'domain_of': ['Phase']} })
    status: Optional[str] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })


class WorkStream(ConfiguredBaseModel):
    """
    Parallel work track focusing on specific project aspect
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    lead: Optional[str] = Field(default=None, description="""Work stream lead""", json_schema_extra = { "linkml_meta": {'alias': 'lead', 'domain_of': ['WorkStream']} })
    team: Optional[str] = Field(default=None, description="""Assigned project team""", json_schema_extra = { "linkml_meta": {'alias': 'team', 'domain_of': ['Project', 'WorkStream']} })
    deliverables: Optional[list[str]] = Field(default=None, description="""Associated deliverables""", json_schema_extra = { "linkml_meta": {'alias': 'deliverables', 'domain_of': ['Milestone', 'Phase', 'WorkStream']} })
    dependencies: Optional[list[str]] = Field(default=None, description="""Dependencies""", json_schema_extra = { "linkml_meta": {'alias': 'dependencies', 'domain_of': ['BacklogItem', 'WorkStream']} })


class Documentation(ConfiguredBaseModel):
    """
    Project artifact serving various stakeholder needs
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'status': {'name': 'status',
                                   'range': 'AgileArtifactStatusEnum'},
                        'type': {'name': 'type', 'range': 'DocumentationTypeEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    title: str = Field(default=..., description="""Short descriptive title""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'title', 'domain_of': ['UserStory', 'Issue', 'Documentation']} })
    content: Optional[str] = Field(default=None, description="""Content""", json_schema_extra = { "linkml_meta": {'alias': 'content', 'domain_of': ['Documentation']} })
    type: Optional[DocumentationTypeEnum] = Field(default=None, description="""Type classification""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Issue',
                       'ChangeRequest',
                       'TestCase',
                       'Documentation',
                       'Repository']} })
    status: Optional[AgileArtifactStatusEnum] = Field(default=None, description="""Current status""", json_schema_extra = { "linkml_meta": {'alias': 'status',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'TestCase',
                       'Phase',
                       'Documentation']} })
    owner: Optional[str] = Field(default=None, description="""Owner""", json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['Risk', 'Documentation', 'CommunicationPlan']} })
    created_date: Optional[str] = Field(default=None, description="""Creation timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'created_date',
         'domain_of': ['Project', 'Requirement', 'Epic', 'Issue', 'Documentation']} })
    last_updated: Optional[str] = Field(default=None, description="""Last update timestamp""", json_schema_extra = { "linkml_meta": {'alias': 'last_updated',
         'domain_of': ['Project', 'Requirement', 'Documentation']} })
    version: Optional[str] = Field(default=None, description="""Version""", json_schema_extra = { "linkml_meta": {'alias': 'version', 'domain_of': ['Deliverable', 'Baseline', 'Documentation']} })
    audience: Optional[str] = Field(default=None, description="""Target audience""", json_schema_extra = { "linkml_meta": {'alias': 'audience', 'domain_of': ['Documentation', 'CommunicationPlan']} })


class Repository(ConfiguredBaseModel):
    """
    Storage location for project artifacts and code
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'type': {'name': 'type', 'range': 'RepositoryTypeEnum'}}})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    type: Optional[RepositoryTypeEnum] = Field(default=None, description="""Type classification""", json_schema_extra = { "linkml_meta": {'alias': 'type',
         'domain_of': ['Issue',
                       'ChangeRequest',
                       'TestCase',
                       'Documentation',
                       'Repository']} })
    url: Optional[str] = Field(default=None, description="""URL""", json_schema_extra = { "linkml_meta": {'alias': 'url', 'domain_of': ['Repository']} })
    access_controls: Optional[str] = Field(default=None, description="""Access controls""", json_schema_extra = { "linkml_meta": {'alias': 'access_controls', 'domain_of': ['Repository']} })
    last_sync_date: Optional[str] = Field(default=None, description="""Last sync date""", json_schema_extra = { "linkml_meta": {'alias': 'last_sync_date', 'domain_of': ['Repository']} })


class Metric(ConfiguredBaseModel):
    """
    Quantitative measure of project performance or quality
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    value: Optional[float] = Field(default=None, description="""Metric value""", json_schema_extra = { "linkml_meta": {'alias': 'value', 'domain_of': ['Metric']} })
    target: Optional[float] = Field(default=None, description="""Target value""", json_schema_extra = { "linkml_meta": {'alias': 'target', 'domain_of': ['Metric']} })
    unit: Optional[str] = Field(default=None, description="""Measurement unit""", json_schema_extra = { "linkml_meta": {'alias': 'unit', 'domain_of': ['Metric']} })
    measurement_date: Optional[str] = Field(default=None, description="""Measurement date""", json_schema_extra = { "linkml_meta": {'alias': 'measurement_date', 'domain_of': ['Metric']} })
    trend: Optional[str] = Field(default=None, description="""Trend""", json_schema_extra = { "linkml_meta": {'alias': 'trend', 'domain_of': ['Metric']} })


class Person(ConfiguredBaseModel):
    """
    Human individual involved in the project environment
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'schema:Person',
         'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    person_name: str = Field(default=..., description="""Person's name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'person_name', 'domain_of': ['Person']} })
    email: Optional[str] = Field(default=None, description="""Contact email""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['Person']} })
    communication_preferences: Optional[str] = Field(default=None, description="""Communication preferences""", json_schema_extra = { "linkml_meta": {'alias': 'communication_preferences', 'domain_of': ['Stakeholder', 'Person']} })


class TeamMember(Person):
    """
    Individual team member with role responsibilities and capacity
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management',
         'slot_usage': {'role': {'name': 'role',
                                 'range': 'RoleEnum',
                                 'required': True}}})

    role: RoleEnum = Field(default=..., description="""Primary role""", json_schema_extra = { "linkml_meta": {'alias': 'role', 'domain_of': ['TeamMember', 'Stakeholder']} })
    capacity: Optional[float] = Field(default=None, description="""Weekly capacity in hours""", ge=0, json_schema_extra = { "linkml_meta": {'alias': 'capacity', 'domain_of': ['Team', 'TeamMember']} })
    is_active: Optional[bool] = Field(default=True, description="""Active status""", json_schema_extra = { "linkml_meta": {'alias': 'is_active', 'domain_of': ['TeamMember'], 'ifabsent': 'boolean(true)'} })
    skills: Optional[list[str]] = Field(default=None, description="""Skills""", json_schema_extra = { "linkml_meta": {'alias': 'skills', 'domain_of': ['TeamMember']} })
    start_date: Optional[str] = Field(default=None, description="""Start date""", json_schema_extra = { "linkml_meta": {'alias': 'start_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    end_date: Optional[str] = Field(default=None, description="""End date""", json_schema_extra = { "linkml_meta": {'alias': 'end_date', 'domain_of': ['Sprint', 'TeamMember', 'Phase']} })
    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    person_name: str = Field(default=..., description="""Person's name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'person_name', 'domain_of': ['Person']} })
    email: Optional[str] = Field(default=None, description="""Contact email""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['Person']} })
    communication_preferences: Optional[str] = Field(default=None, description="""Communication preferences""", json_schema_extra = { "linkml_meta": {'alias': 'communication_preferences', 'domain_of': ['Stakeholder', 'Person']} })


class Stakeholder(Person):
    """
    Project stakeholder with influence and interest assessment
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    role: Optional[RoleEnum] = Field(default=None, description="""Primary role""", json_schema_extra = { "linkml_meta": {'alias': 'role', 'domain_of': ['TeamMember', 'Stakeholder']} })
    influence: Optional[InfluenceLevelEnum] = Field(default=None, description="""Influence level""", json_schema_extra = { "linkml_meta": {'alias': 'influence', 'domain_of': ['Stakeholder']} })
    interest: Optional[InterestLevelEnum] = Field(default=None, description="""Interest level""", json_schema_extra = { "linkml_meta": {'alias': 'interest', 'domain_of': ['Stakeholder']} })
    communication_preferences: Optional[str] = Field(default=None, description="""Communication preferences""", json_schema_extra = { "linkml_meta": {'alias': 'communication_preferences', 'domain_of': ['Stakeholder', 'Person']} })
    engagement_plan: Optional[str] = Field(default=None, description="""Engagement plan""", json_schema_extra = { "linkml_meta": {'alias': 'engagement_plan', 'domain_of': ['Stakeholder']} })
    concerns: Optional[list[str]] = Field(default=None, description="""Concerns""", json_schema_extra = { "linkml_meta": {'alias': 'concerns', 'domain_of': ['Stakeholder']} })
    expectations: Optional[list[str]] = Field(default=None, description="""Expectations""", json_schema_extra = { "linkml_meta": {'alias': 'expectations', 'domain_of': ['Stakeholder']} })
    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    person_name: str = Field(default=..., description="""Person's name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'person_name', 'domain_of': ['Person']} })
    email: Optional[str] = Field(default=None, description="""Contact email""", json_schema_extra = { "linkml_meta": {'alias': 'email', 'domain_of': ['Person']} })


class CommunicationPlan(ConfiguredBaseModel):
    """
    Structured approach to project information distribution
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    purpose: Optional[str] = Field(default=None, description="""Purpose of the communication plan""", json_schema_extra = { "linkml_meta": {'alias': 'purpose', 'domain_of': ['CommunicationPlan']} })
    audience: Optional[str] = Field(default=None, description="""Target audience""", json_schema_extra = { "linkml_meta": {'alias': 'audience', 'domain_of': ['Documentation', 'CommunicationPlan']} })
    message: Optional[str] = Field(default=None, description="""Message content for communication""", json_schema_extra = { "linkml_meta": {'alias': 'message', 'domain_of': ['CommunicationPlan']} })
    frequency: Optional[str] = Field(default=None, description="""Frequency of communication""", json_schema_extra = { "linkml_meta": {'alias': 'frequency', 'domain_of': ['CommunicationPlan']} })
    channel: Optional[str] = Field(default=None, description="""Communication channel""", json_schema_extra = { "linkml_meta": {'alias': 'channel', 'domain_of': ['CommunicationPlan']} })
    owner: Optional[str] = Field(default=None, description="""Owner""", json_schema_extra = { "linkml_meta": {'alias': 'owner', 'domain_of': ['Risk', 'Documentation', 'CommunicationPlan']} })
    feedback_mechanism: Optional[str] = Field(default=None, description="""Feedback mechanism for communication""", json_schema_extra = { "linkml_meta": {'alias': 'feedback_mechanism', 'domain_of': ['CommunicationPlan']} })


class AIWorkProduct(ConfiguredBaseModel):
    """
    AI-generated artifacts and their provenance information
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/software_project_management'})

    id: str = Field(default=..., description="""Unique identifier""", json_schema_extra = { "linkml_meta": {'alias': 'id',
         'domain_of': ['Project',
                       'BusinessCase',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Sprint',
                       'Issue',
                       'Team',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Documentation',
                       'Repository',
                       'Metric',
                       'Person',
                       'CommunicationPlan',
                       'AIWorkProduct']} })
    name: str = Field(default=..., description="""Name""", ge=1, le=100, json_schema_extra = { "linkml_meta": {'alias': 'name',
         'domain_of': ['Project',
                       'Epic',
                       'Backlog',
                       'Sprint',
                       'Team',
                       'Milestone',
                       'Deliverable',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Repository',
                       'Metric',
                       'AIWorkProduct']} })
    description: Optional[str] = Field(default=None, description="""Detailed description""", json_schema_extra = { "linkml_meta": {'alias': 'description',
         'domain_of': ['Project',
                       'Requirement',
                       'Epic',
                       'UserStory',
                       'Backlog',
                       'BacklogItem',
                       'Issue',
                       'Risk',
                       'Milestone',
                       'Deliverable',
                       'ChangeRequest',
                       'Baseline',
                       'TestCase',
                       'Phase',
                       'WorkStream',
                       'Metric',
                       'AIWorkProduct']} })
    generated_by: Optional[str] = Field(default=None, description="""Generated by""", json_schema_extra = { "linkml_meta": {'alias': 'generated_by', 'domain_of': ['AIWorkProduct']} })
    generation_date: Optional[str] = Field(default=None, description="""Generation date""", json_schema_extra = { "linkml_meta": {'alias': 'generation_date', 'domain_of': ['AIWorkProduct']} })
    input_parameters: Optional[str] = Field(default=None, description="""Input parameters""", json_schema_extra = { "linkml_meta": {'alias': 'input_parameters', 'domain_of': ['AIWorkProduct']} })
    confidence_score: Optional[float] = Field(default=None, description="""Confidence score""", ge=0, le=1, json_schema_extra = { "linkml_meta": {'alias': 'confidence_score', 'domain_of': ['AIWorkProduct']} })
    validation_status: Optional[ApprovalStatusEnum] = Field(default=None, description="""Validation status""", json_schema_extra = { "linkml_meta": {'alias': 'validation_status', 'domain_of': ['AIWorkProduct']} })
    associated_requirement: Optional[str] = Field(default=None, description="""Associated requirement""", json_schema_extra = { "linkml_meta": {'alias': 'associated_requirement', 'domain_of': ['TestCase', 'AIWorkProduct']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Project.model_rebuild()
BusinessCase.model_rebuild()
Scope.model_rebuild()
Requirement.model_rebuild()
Epic.model_rebuild()
UserStory.model_rebuild()
Backlog.model_rebuild()
BacklogItem.model_rebuild()
Sprint.model_rebuild()
Issue.model_rebuild()
Team.model_rebuild()
Risk.model_rebuild()
Milestone.model_rebuild()
Deliverable.model_rebuild()
ChangeRequest.model_rebuild()
Baseline.model_rebuild()
TestCase.model_rebuild()
Phase.model_rebuild()
WorkStream.model_rebuild()
Documentation.model_rebuild()
Repository.model_rebuild()
Metric.model_rebuild()
Person.model_rebuild()
TeamMember.model_rebuild()
Stakeholder.model_rebuild()
CommunicationPlan.model_rebuild()
AIWorkProduct.model_rebuild()

