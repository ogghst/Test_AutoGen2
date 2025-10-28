import json

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
        """
        Initialize the KnowledgeGraphAgent.
        
        Args:
            user_session: The user session object.
            tools: Additional tools beyond the standard project management tools
        """
        system_message = SystemMessage(
            content="""You are a skilled knowledge graph manager agent. 
            Your role is to:
            
            1. Analyze user request and identify entities and relationships to create or modify.
            2. Make a plan breaking down the request into smaller tasks, one per each entities and relationships to create or update.
               Example: if user asks to create a project with two users A and B, then you shall create a project, create a user A, create another user B, create a relationship between the user A and the project, create a relationship between the user B and the project.            
            2. Call all the appropriate tools to create or modify the knowledge graph, call them in the order of the plan and call them only once for each task.
            3. After creating entities, remember their id and make sure to create appropriate relationships between them.
               Example: after creating a user, make sure it has the proper project role and create the relationship with label 'assigned_to' between the user and the project.
            4. When the tool returns a success message, move to the next task until the plan is completed.
               Example of a successful user creation return message: {\"success\": true, \"message\": \"User successfully created\"}
            5. After each tool execution, update the plan with success tasks and failed tasks and check whether other tool calls are needed.
            6. terminate the conversation and transfer back to triage at each task completion.
           
            ## CONTEXT AND KNOWLEDGE GRAPH DATA
            1. Session_id of this project is: '{user_session.session_id}'. 
            2. Active project id is: '{user_session.project_id}'.
            3. Entities and relationships have an unique identifier called 'id'

            """
        )
                
        # Create a custom get_entity_schema tool that prevents loops
        from autogen_core.tools import FunctionTool
        from typing import Annotated
        

        
        knowledge_graph_tools = [
            
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
