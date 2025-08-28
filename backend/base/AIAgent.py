
from .messaging import AgentResponse, UserTask
from autogen_core import FunctionCall, MessageContext, RoutedAgent, TopicId, message_handler
from autogen_core.models import AssistantMessage, ChatCompletionClient, FunctionExecutionResult, FunctionExecutionResultMessage, SystemMessage
from autogen_core.tools import Tool

import json
from config.logging_config import get_logger
from typing import List, Tuple


class AIAgent(RoutedAgent):
    """
    Base AI Agent class for all AI agents in the handoffs pattern.

    This class provides the core functionality for:
    - Processing user tasks with LLM integration
    - Executing tools and delegating to other agents
    - Managing conversation flow and context
    """

    def __init__(
        self,
        description: str,
        system_message: SystemMessage,
        model_client: ChatCompletionClient,
        tools: List[Tool],
        delegate_tools: List[Tool],
        agent_topic_type: str,
        user_topic_type: str,
    ) -> None:
        super().__init__(description)
        self._system_message = system_message
        self._model_client = model_client
        self._tools = dict([(tool.name, tool) for tool in tools])
        self._tool_schema = [tool.schema for tool in tools]
        self._delegate_tools = dict([(tool.name, tool) for tool in delegate_tools])
        self._delegate_tool_schema = [tool.schema for tool in delegate_tools]
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type

    @message_handler
    async def handle_task(self, message: UserTask, ctx: MessageContext) -> None:
        """
        Handle incoming user tasks by processing them through the LLM and executing tools.

        Args:
            message: The user task message containing context
            ctx: The message context for cancellation and routing
        """
        logger = get_logger(__name__)
        try:
            logger.info(f"{self.id.type}: Processing task with {len(message.context)} messages")
            logger.debug(f"{self.id.type}: Context messages: {[msg.content for msg in message.context]}")

            # Send the task to the LLM
            logger.info(f"{self.id.type}: Sending request to LLM")
            llm_result = await self._model_client.create(
                messages=[self._system_message] + message.context,
                tools=self._tool_schema + self._delegate_tool_schema,
                cancellation_token=ctx.cancellation_token,
            )
            logger.info(f"{self.id.type}: LLM response received - content: {llm_result.content}")
            #print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
        except Exception as e:
            logger.error(f"Error in {self.id.type}: {e}", exc_info=True)
                        # Send error response to user instead of just returning
            error_message = f"I encountered an error while processing your request: {str(e)}. Please try again or contact support."
            message.context.append(AssistantMessage(content=error_message, source=self.id.type))
            await self.publish_message(
                AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
                topic_id=TopicId(self._user_topic_type, source=self.id.key),
            )
            return

        # Process the LLM result
        logger.info(f"{self.id.type}: Processing LLM result: {type(llm_result.content)}")

        while isinstance(llm_result.content, list) and all(isinstance(m, FunctionCall) for m in llm_result.content):
            logger.info(f"{self.id.type}: Processing function calls: {[call.name for call in llm_result.content]}")
            tool_call_results: List[FunctionExecutionResult] = []
            delegate_targets: List[Tuple[str, UserTask]] = []

            # Process each function call
            for call in llm_result.content:
                logger.info(f"{self.id.type}: Processing function call: {call.name}")
                arguments = json.loads(call.arguments)
                logger.debug(f"{self.id.type}: Function arguments: {arguments}")

                if call.name in self._tools:
                    # Execute the tool directly
                    logger.info(f"{self.id.type}: Executing tool: {call.name}")
                    result = await self._tools[call.name].run_json(arguments, ctx.cancellation_token)
                    result_as_str = self._tools[call.name].return_value_as_string(result)
                    logger.info(f"{self.id.type}: Tool {call.name} result: {result_as_str}")
                    tool_call_results.append(
                        FunctionExecutionResult(call_id=call.id, content=result_as_str, is_error=False, name=call.name)
                    )
                elif call.name in self._delegate_tools:
                    # Execute the tool to get the delegate agent's topic type
                    logger.info(f"{self.id.type}: Executing delegate tool: {call.name}")
                    result = await self._delegate_tools[call.name].run_json(arguments, ctx.cancellation_token)
                    topic_type = self._delegate_tools[call.name].return_value_as_string(result)
                    logger.info(f"{self.id.type}: Delegating to: {topic_type}")

                    # Create the context for the delegate agent, including the function call and the result
                    delegate_messages = list(message.context) + [
                        AssistantMessage(content=[call], source=self.id.type),
                        FunctionExecutionResultMessage(
                            content=[
                                FunctionExecutionResult(
                                    call_id=call.id,
                                    content=f"Transferred to {topic_type}. Adopt persona immediately.",
                                    is_error=False,
                                    name=call.name,
                                )
                            ]
                        ),
                    ]
                    delegate_targets.append((topic_type, UserTask(context=delegate_messages)))
                else:
                    logger.error(f"{self.id.type}: Unknown tool: {call.name}")
                    raise ValueError(f"Unknown tool: {call.name}")

            if len(delegate_targets) > 0:
                # Delegate the task to other agents by publishing messages to the corresponding topics
                logger.info(f"{self.id.type}: Delegating to {len(delegate_targets)} agents")
                for topic_type, task in delegate_targets:
                    topic_id = TopicId(topic_type, source=self.id.key)
                    #print(f"{'-'*80}\n{self.id.type}:\nDelegating to {topic_type}", flush=True)
                    logger.info(f"{self.id.type}: Publishing to topic: {topic_type}")
                    await self.publish_message(task, topic_id=topic_id)

            if len(tool_call_results) > 0:
                #print(f"{'-'*80}\n{self.id.type}:\n{tool_call_results}", flush=True)
                # Make another call to the model with the tool results
                logger.info(f"{self.id.type}: Making follow-up LLM call with tool results - {tool_call_results}")

                llm_result = await self._model_client.create(
                    messages=[self._system_message] + message.context + [
                        AssistantMessage(content=llm_result.content, source=self.id.type),
                        FunctionExecutionResultMessage(content=tool_call_results),
                    ],
                    tools=self._tool_schema + self._delegate_tool_schema,
                    cancellation_token=ctx.cancellation_token,
                )
                logger.info(f"{self.id.type}: Follow-up LLM response received - {llm_result.content}")
                #print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
            else:
                logger.info(f"{self.id.type}: No more tool calls to process")
                break

        # Send the final response to the customer
        if not isinstance(llm_result.content, list):
            logger.info(f"{self.id.type}: Sending final response to user - {llm_result.content}")
            message.context.append(AssistantMessage(content=llm_result.content, source=self.id.type))
            logger.info(f"{self.id.type}: Publishing AgentResponse to topic {self._user_topic_type} for user {self.id.key}")
            await self.publish_message(
                AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
                topic_id=TopicId(self._user_topic_type, source=self.id.key),
            )
        else:
            logger.warning(f"{self.id.type}: Unexpected LLM response format: {type(llm_result.content)}")