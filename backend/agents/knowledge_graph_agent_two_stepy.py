import json
from typing import Dict, Optional, List
from autogen_core.models import SystemMessage
from autogen_core.tools import Tool
from autogen_core import MessageContext

from session import UserSession
from models.data_models import Project
from base.AIAgent import AIAgent
from base.messaging import UserTask, AgentResponse
from tools.tools import (
    USER_TOPIC_TYPE,
    KNOWLEDGE_GRAPH_AGENT_TOPIC_TYPE,
    transfer_back_to_triage_tool,
    UUIDEncoder,
)
from tools.knowledge_tools import create_knowledge_tools

from autogen_core import TopicId
from autogen_core.models import AssistantMessage
from autogen_core import message_handler



class KnowledgeGraphAgent(AIAgent):
    """
    Knowledge graph agent responsible to create or modify a knowledge graph.
    This agent implements a two-phase planning and execution model.
    """
    
    def __init__(self, user_session: UserSession, tools: list[Tool] = None):
        # State management variables
        self._plan = None
        self._completed_steps = []
        self._plan_completed = False
        self._last_result = None
        
        # The system message is now dynamically generated in handle_task
        system_message = SystemMessage(content="You are a helpful assistant.")
        
        delegate_tools = [transfer_back_to_triage_tool]
        
        super().__init__(
            user_session=user_session,
            description="A skilled knowledge graph agent responsible for knowledge graph creation and modification.",
            system_message=system_message,
            tools=tools or [],
            delegate_tools=delegate_tools,
            agent_topic_type=KNOWLEDGE_GRAPH_AGENT_TOPIC_TYPE,
            user_topic_type=USER_TOPIC_TYPE,
        )
        
    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> None:
        # Phase 1: Planning (if no plan exists yet)
        if self._plan is None:
            planning_prompt = f"""
            You are a meticulous planner. Based on the user's request, create a JSON object representing the plan to execute.
            The user's request is: '{message.context[-1].content}'

            The plan must be a JSON object with a single key "steps", which is a list of dictionaries.
            Each dictionary in the list represents a single step and must have "tool_name" and "parameters" keys.
            - "tool_name": The name of the tool to call.
            - "parameters": A dictionary of parameters for the tool.

            Break the request into atomic steps. For dependencies, use the placeholder "<LAST_RESULT>" for parameter values that should be populated from the previous step's result.
            For example, to create a user and then assign them to a project, the 'user_id' in the second step would come from the result of the first step.

            Available tools: {list(self._tools.keys())}

            Generate *only* the JSON plan.
            """

            try:
                # Use the model client directly to generate the plan
                plan_response = await self._model_client.create(
                    messages=[SystemMessage(content=planning_prompt)],
                    cancellation_token=ctx.cancellation_token,
                )
                plan_json_str = plan_response.content[plan_response.content.find('{'):plan_response.content.rfind('}')+1]
                self._plan = json.loads(plan_json_str)
            except (json.JSONDecodeError, IndexError, Exception) as e:
                # Handle failure to generate a valid plan
                error_msg = f"Error creating a plan: {e}"
                ctx.append(AssistantMessage(content=error_msg, source=self.id.type))
                await self.publish_message(
                    AgentResponse(context=ctx, reply_to_topic_type=self._agent_topic_type), topic_id=TopicId(self._user_topic_type, source=self.id.key))
                return

        # Phase 2: Execution Loop
        while not self._plan_completed:
            next_step_index = -1
            for i in range(len(self._plan.get('steps', []))):
                if i not in self._completed_steps:
                    next_step_index = i
                    break

            if next_step_index == -1:
                self._plan_completed = True
                continue

            step = self._plan['steps'][next_step_index]
            tool_name = step['tool_name']
            parameters = step['parameters']

            # Handle placeholder for the previous step's result
            for key, value in parameters.items():
                if isinstance(value, str) and value == "<LAST_RESULT>":
                    # The result of a ToolResponse is in the 'data' field
                    if isinstance(self._last_result, dict) and 'data' in self._last_result:
                        parameters[key] = self._last_result['data']
                    else:
                        parameters[key] = self._last_result

            tool_to_run = self._tools.get(tool_name)
            if not tool_to_run:
                error_msg = f"Error: Tool '{tool_name}' not found."
                msg = AssistantMessage(content=error_msg, source=self.id.type)
                await self.publish_message(AgentResponse(context=ctx + msg, reply_to_topic_type=self._agent_topic_type), topic_id=ctx.reply_to)
                return

            try:
                result = await tool_to_run.run_json(parameters, ctx.cancellation_token)
                self._last_result = result
                self._completed_steps.append(next_step_index)
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {e}"
                msg = AssistantMessage(content=error_msg, source=self.id.type)
                await self.publish_message(AgentResponse(context=ctx + msg, reply_to_topic_type=self._agent_topic_type), topic_id=ctx.reply_to)
                return # Stop execution on error

        # If we reach here, the plan is complete
        final_message = "Plan executed successfully. All tasks are complete."
        # Use transfer_back_to_triage tool
        transfer_tool = self._delegate_tools.get("transfer_back_to_triage")
        if transfer_tool:
            await transfer_tool.run_json({}, ctx.cancellation_token)
        else:
            # Fallback if tool not found
            msg = AssistantMessage(content=error_msg, source=self.id.type)
            await self.publish_message(AgentResponse(context=ctx+msg, reply_to_topic_type=self._agent_topic_type), topic_id=ctx.reply_to)
