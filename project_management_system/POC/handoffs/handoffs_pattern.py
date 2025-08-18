import json
import uuid
import os
import logging
from pathlib import Path
from typing import List, Tuple

from autogen_core import (
    FunctionCall,
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
)
from autogen_core.models import (
    AssistantMessage,
    ChatCompletionClient,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
    LLMMessage,
    SystemMessage,
    UserMessage,
)
from autogen_core.tools import FunctionTool, Tool
from autogen_ext.models.openai import OpenAIChatCompletionClient
from pydantic import BaseModel


def setup_logging():
    """Setup logging configuration for the handoffs pattern"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    log_file = script_dir / "handoff.log"
    
    # Remove existing log file to reset it at each run
    if log_file.exists():
        log_file.unlink()
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=' - - - %(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            #logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging initialized for handoffs pattern")
    return logger


# Message Protocol for agent communication
class UserLogin(BaseModel):
    pass


class UserTask(BaseModel):
    context: List[LLMMessage]


class AgentResponse(BaseModel):
    reply_to_topic_type: str
    context: List[LLMMessage]


# AI Agent base class for all AI agents
class AIAgent(RoutedAgent):
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
        logger = logging.getLogger(__name__)
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
            print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
        except Exception as e:
            logger.error(f"Error in {self.id.type}: {e}", exc_info=True)
            #print(f"Error in {self.id.type}: {e}", flush=True)
            
            # Send error response to user
            #response = AgentResponse(
            #    reply_to_topic_type=self._user_topic_type,
            #    context=message.context + [AssistantMessage(content=f"Error: {str(e)}", source=self.id.type)],
            #)
            #topic_id = TopicId(self._user_topic_type, source=ctx.topic_id.source)
            #await self.publish_message(response, topic_id=topic_id)
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
                    print(f"{'-'*80}\n{self.id.type}:\nDelegating to {topic_type}", flush=True)
                    logger.info(f"{self.id.type}: Publishing to topic: {topic_type}")
                    await self.publish_message(task, topic_id=topic_id)
                      
            if len(tool_call_results) > 0:
                print(f"{'-'*80}\n{self.id.type}:\n{tool_call_results}", flush=True)
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
                print(f"{'-'*80}\n{self.id.type}:\n{llm_result.content}", flush=True)
            else:
                logger.info(f"{self.id.type}: No more tool calls to process")
                break
        
        # Send the final response to the customer
        if not isinstance(llm_result.content, list):
            logger.info(f"{self.id.type}: Sending final response to user - {llm_result.content}")
            message.context.append(AssistantMessage(content=llm_result.content, source=self.id.type))
            await self.publish_message(
                AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
                topic_id=TopicId(self._user_topic_type, source=self.id.key),
            )
        else:
            logger.warning(f"{self.id.type}: Unexpected LLM response format: {type(llm_result.content)}")


# Human Agent for handling complex requests
class HumanAgent(RoutedAgent):
    def __init__(self, description: str, agent_topic_type: str, user_topic_type: str) -> None:
        super().__init__(description)
        self._agent_topic_type = agent_topic_type
        self._user_topic_type = user_topic_type

    @message_handler
    async def handle_user_task(self, message: UserTask, ctx: MessageContext) -> None:
        logger = logging.getLogger(__name__)
        logger.info(f"{self.id.type}: Human intervention required")

        # Get human input
        human_input = input("Human Agent: ")
        print(f"{'-'*80}\n{self.id.type}:\nHuman response: {human_input}", flush=True)
        
        logger.info(f"{self.id.type}: Human response received: {human_input}")

        logger.info(f"{self.id.type}: Publishing human response")
        message.context.append(AssistantMessage(content=human_input, source=self.id.type))
        await self.publish_message(
            AgentResponse(context=message.context, reply_to_topic_type=self._agent_topic_type),
            topic_id=TopicId(self._user_topic_type, source=self.id.key),
        )


# User Agent for managing user sessions
class UserAgent(RoutedAgent):
    def __init__(self, description: str, user_topic_type: str, agent_topic_type: str) -> None:
        super().__init__(description)
        self._user_topic_type = user_topic_type
        self._agent_topic_type = agent_topic_type

    @message_handler
    async def handle_user_login(self, message: UserLogin, ctx: MessageContext) -> None:
        logger = logging.getLogger(__name__)
        logger.info(f"User login, session ID: {self.id.key}")
        print(f"User login, session ID: {self.id.key}.", flush=True)
        # Get the user's initial input after login.
        user_input = input("User: ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        # Start the conversation with the triage agent
        topic_id = TopicId(self._agent_topic_type, source=self.id.key)
        logger.info(f"Starting conversation with {self._agent_topic_type}")
        await self.publish_message(UserTask(context=[UserMessage(content=user_input, source="User")]), topic_id=topic_id)

    @message_handler
    async def handle_task_result(self, message: AgentResponse, ctx: MessageContext) -> None:
        logger = logging.getLogger(__name__)
        logger.info(f"Handling task result from {message.reply_to_topic_type}")
        # Get the user's input after receiving a response from an agent.
        user_input = input("User (type 'exit' to close the session): ")
        print(f"{'-'*80}\n{self.id.type}:\n{user_input}", flush=True)
        if user_input.strip().lower() == "exit":
            logger.info(f"User session ended, session ID: {self.id.key}")
            print(f"{'-'*80}\nUser session ended, session ID: {self.id.key}.")
            return
        message.context.append(UserMessage(content=user_input, source="User"))
        logger.info(f"Publishing user input to {message.reply_to_topic_type}")

        await self.publish_message(
            UserTask(context=message.context), topic_id=TopicId(message.reply_to_topic_type, source=self.id.key)
        )
        
# Define topic types for the agents
triage_agent_topic_type = "triage_agent"
planning_agent_topic_type = "planning_agent"
execution_agent_topic_type = "execution_agent"
quality_agent_topic_type = "quality_agent"
human_agent_topic_type = "human_agent"
user_topic_type = "user"

# Tools for the AI agents
async def transfer_to_planning_agent() -> str:
    return planning_agent_topic_type


async def transfer_to_execution_agent() -> str:
    return execution_agent_topic_type


async def transfer_to_quality_agent() -> str:
    return quality_agent_topic_type


async def transfer_back_to_triage() -> str:
    return triage_agent_topic_type


async def escalate_to_human() -> str:
    return human_agent_topic_type


async def create_project_plan(
    project_name: str,  # Project name: str - The name of the project to be planned.
    requirements: str   # Requirements: str - The requirements or specifications for the project.
) -> str:
    """
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
    Args:
        task_name (str): The name of the task to be executed.
        priority (str): The priority level of the task.

    Returns:
        str: Confirmation message that the task has been executed.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Executing task '{task_name}' with priority '{priority}'")
    return f"Task '{task_name}' with priority '{priority}' has been executed."


# Create tool instances
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


async def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting handoffs pattern system")
    
    # Create the runtime
    runtime = SingleThreadedAgentRuntime()
    
    # Create the model client
    api_key = os.getenv("DEEPSEEK_API_KEY", "sk-9a4206f76b4a466095d6b85b859c6a85")
    logger.info(f"Creating model client with model: deepseek-chat")
    logger.debug(f"API key: {api_key[:10]}...")
    
    model_client = OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        model_info={
            "family": "deepseek",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output": True
        }
    )
        
    # Register the triage agent
    logger.info("Registering triage agent")
    triage_agent_type = await AIAgent.register(
        runtime,
        type=triage_agent_topic_type,
        factory=lambda: AIAgent(
            description="A triage agent responsible for understanding user requests and routing to appropriate agents.",
            system_message=SystemMessage(
                content="You are a project management triage agent. Your role is to:\n"
                "1. Understand the user's request\n"
                "2. Route them to the appropriate specialized agent\n"
                "3. Use the transfer tools to delegate tasks\n\n"
                "Always be helpful and professional. Route users to the most appropriate agent."
            ),
            model_client=model_client,
            tools=[],
            delegate_tools=[
                transfer_to_planning_tool,
                transfer_to_execution_tool,
                transfer_to_quality_tool,
                escalate_to_human_tool,
            ],
            agent_topic_type=triage_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    
    # Add subscriptions for the triage agent
    logger.info(f"Adding subscription for triage agent: {triage_agent_topic_type}")
    await runtime.add_subscription(
        TypeSubscription(topic_type=triage_agent_topic_type, agent_type=triage_agent_type.type)
    )
    
    # Register the planning agent
    logger.info("Registering planning agent")
    planning_agent_type = await AIAgent.register(
        runtime,
        type=planning_agent_topic_type,
        factory=lambda: AIAgent(
            description="A project planning agent responsible for creating project plans and gathering requirements.",
            system_message=SystemMessage(
                content="You are a project planning agent for ACME Inc. Your role is to:\n"
                "1. Help users create project plans\n"
                "2. Gather and document requirements\n"
                "3. Create project timelines and milestones\n"
                "4. Use the create_project_plan tool when needed\n"
                "5. Transfer back to triage if the request is outside your scope\n\n"
                "Always be thorough and professional. Ask clarifying questions when needed."
            ),
            model_client=model_client,
            tools=[create_project_plan_tool],
            delegate_tools=[transfer_back_to_triage_tool, transfer_to_execution_tool],
            agent_topic_type=planning_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    
    # Add subscriptions for the planning agent
    await runtime.add_subscription(
        TypeSubscription(topic_type=planning_agent_topic_type, agent_type=planning_agent_type.type)
    )
    
    # Register the execution agent
    logger.info("Registering execution agent")
    execution_agent_type = await AIAgent.register(
        runtime,
        type=execution_agent_topic_type,
        factory=lambda: AIAgent(
            description="A project execution agent responsible for task execution and project management.",
            system_message=SystemMessage(
                content="You are a project execution agent. Your role is to:\n"
                "1. Help users execute project tasks\n"
                "2. Manage project timelines and deliverables\n"
                "3. Use the execute_project_task tool when needed\n"
                "4. Transfer back to triage if the request is outside your scope\n\n"
                "Always be efficient and results-oriented. Focus on getting things done."
            ),
            model_client=model_client,
            tools=[execute_project_task_tool],
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=execution_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    
    # Add subscriptions for the execution agent
    await runtime.add_subscription(
        TypeSubscription(topic_type=execution_agent_topic_type, agent_type=execution_agent_type.type)
    )
    
    # Register the quality agent
    logger.info("Registering quality agent")
    quality_agent_type = await AIAgent.register(
        runtime,
        type=quality_agent_topic_type,
        factory=lambda: AIAgent(
            description="A project quality agent responsible for quality assurance and project reviews.",
            system_message=SystemMessage(
                content="You are a project quality agent for ACME Inc. Your role is to:\n"
                "1. Help users review project quality\n"
                "2. Conduct quality assessments\n"
                "3. Use the review_project_quality tool when needed\n"
                "4. Transfer back to triage if the request is outside your scope\n\n"
                "Always be thorough and quality-focused. Maintain high standards."
            ),
            model_client=model_client,
            tools=[review_project_quality_tool],
            delegate_tools=[transfer_back_to_triage_tool],
            agent_topic_type=quality_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    
    # Add subscriptions for the quality agent
    await runtime.add_subscription(
        TypeSubscription(topic_type=quality_agent_topic_type, agent_type=quality_agent_type.type)
    )
    
    # Register the human agent
    logger.info("Registering human agent")
    human_agent_type = await HumanAgent.register(
        runtime,
        type=human_agent_topic_type,
        factory=lambda: HumanAgent(
            description="A human agent for handling complex requests.",
            agent_topic_type=human_agent_topic_type,
            user_topic_type=user_topic_type,
        ),
    )
    
    # Add subscriptions for the human agent
    await runtime.add_subscription(
        TypeSubscription(topic_type=human_agent_topic_type, agent_type=human_agent_type.type)
    )
    
    # Register the user agent
    logger.info("Registering user agent")
    user_agent_type = await UserAgent.register(
        runtime,
        type=user_topic_type,
        factory=lambda: UserAgent(
            description="A user agent for managing user sessions.",
            user_topic_type=user_topic_type,
            agent_topic_type=triage_agent_topic_type,  # Start with the triage agent
        ),
    )
    
    # Add subscriptions for the user agent
    await runtime.add_subscription(
        TypeSubscription(topic_type=user_topic_type, agent_type=user_agent_type.type)
    )
    
    # Start the runtime
    logger.info("Starting runtime")
    runtime.start()
    
    # Create a new session for the user
    session_id = str(uuid.uuid4())
    logger.info(f"Creating user session: {session_id}")
    await runtime.publish_message(UserLogin(), topic_id=TopicId(user_topic_type, source=session_id))
    
    # Run until completion
    logger.info("Waiting for runtime to complete")
    await runtime.stop_when_idle()
    logger.info("Runtime completed, closing model client")
    await model_client.close()
    logger.info("Handoffs pattern system shutdown complete")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
