import json
from typing import Annotated
from autogen_core.tools import FunctionTool
from autogen_core.models import SystemMessage
from autogen_core.tools import Tool

from session import UserSession

from models.data_models import Project

from base.AIAgent import AIAgent
from tools.tools import (
    USER_TOPIC_TYPE,
    KNOWLEDGE_GRAPH_AGENT_TOPIC_TYPE,
    transfer_back_to_triage_tool,
    UUIDEncoder,
)
from tools.knowledge_tools import create_knowledge_tools

class KnowledgeGraphAgent(AIAgent):
    """
    Knowledge graph agent responsible to create or modify a knowledge graph.
    """
    
    def __init__(self, user_session: UserSession, tools: list[Tool] = None):
        # Track which entity schemas have been retrieved to prevent loops
        self._retrieved_schemas = set()
        self.user_session = user_session
        # Initialize task list as instance variable
        
        """
        Initialize the KnowledgeGraphAgent.
        
        Args:
            user_session: The user session object.
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="You are a skilled knowledge graph manager agent. \n\n"
            "Your role is to:\n\n"
            "1. Analyze user request and identify entities and relationships to create or modify.\n"    
            "2. Make a plan breaking down the request into smaller tasks, one per each entities and relationships to create or update. Example: if user asks to create a project with two users A and B, then you shall create a project, create a user A, create another user B, create a relationship between the user A and the project, create a relationship between the user B and the project. Revise the accomplished tasks using 'get_task_list_tool' tool, and add tasks using 'add_task_tool' tool to add task to the plan.\n"
            "3. Call then all the appropriate tools to create or modify the knowledge graph in one call, call them in the order of the plan and call them only once for each task\n"
            "4. After creating entities, remember their id and make sure to create appropriate relationships between them.\n"
            "       Example: after creating a user, make sure it has the proper project role and create the relationship with label 'assigned_to' between the user and the project.\n"
            "5. When the tool returns a success message, update the plan with the success task using 'update_task_tool' tool, and move to the next task until the plan is completed.\n"  
            "Example of a successful user creation return message: {\"success\": true, \"message\": \"User successfully created\", \"task_completed\": true}\n"
            "6. Once all tasks in the plan are completed, terminate the conversation by transferring back to the triage agent.\n"
            "## CONTEXT AND KNOWLEDGE GRAPH DATA\n"
            "1. Session_id of this project is: '" + (user_session.session_id or "None") + "'. \n"
            "2. Active project id is: '" + (user_session.project_id or "None") + "'. \n"
            "3. Entities and relationships have an unique identifier called 'id' \n"
        )
        
        # Create tools as instance methods
        add_task_tool = FunctionTool(
            self.add_task,
            description="Add a task to the plan. Returns None."
        )
    
        
        get_task_list_tool = FunctionTool(
            self.get_task_list,
            description="Get the task list. Returns the task list."
        )
        
        update_task_tool = FunctionTool(
            self.update_task,
            description="Update a task in the plan. Returns None."
        )
        
        knowledge_graph_tools = [
            add_task_tool,
            get_task_list_tool,
            update_task_tool,
        ]
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            user_session=user_session,
            description="A skilled knowledge graph agent responsible for knowledge graph creation and modification.",
            system_message=system_message,
            tools=knowledge_graph_tools + (tools or []),
            delegate_tools=delegate_tools,
            agent_topic_type=KNOWLEDGE_GRAPH_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )

    async def add_task(self, task: Annotated[str, "The task to add"], is_accomplished: Annotated[bool, "Whether the task is accomplished"]) -> dict[str, bool]:
        """
        Add a task to the plan.
        
        Args:
            task: The task to add.
            is_accomplished: Whether the task is accomplished.
            
        Returns: 
            the task list
        """
        self.user_session.task_list[task] = is_accomplished
        return self.user_session.task_list
        
    async def update_task(self, task: Annotated[str, "The task to update"], is_accomplished: Annotated[bool, "Whether the task is accomplished"]) -> dict[str, bool]:
        """
        Update a task in the plan.
        
        Args:
            task: The task to update.
            is_accomplished: Whether the task is accomplished.

        Returns:
            the task list
        """
        if task in self.user_session.task_list:
            self.user_session.task_list[task] = is_accomplished
        return self.user_session.task_list
        
    async def get_task_list(self) -> dict[str, bool]:
        """
        Get the task list.
        
        Returns:
            the task list
        """
        return self.user_session.task_list
