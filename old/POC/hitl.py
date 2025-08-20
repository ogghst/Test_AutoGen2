import asyncio
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

async def main():
    
    # Create the agents.
    model_client = OpenAIChatCompletionClient(
        model="deepseek-chat",
        api_key="sk-9a4206f76b4a466095d6b85b859c6a85",
        base_url="https://api.deepseek.com",
        model_info={
            "family": "deepseek",
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "structured_output":True
        }
    )
    
    pm_system_message = f"""You are a project management assistant. Analyze the user's message and determine their intent.

    Based on the agent's capabilities described in its description, classify the user's intent into one of these categories:

    1. PROJECT_INITIALIZATION - User wants to start/create a new project
    2. STATUS_REQUEST - User wants to know project status or updates
    3. REQUIREMENTS_GATHERING - User wants to gather project requirements
    4. PROJECT_PLANNING - User wants to create or view project plan
    5. SYSTEM_RESTART - User wants to restart or start over
    6. GENERAL_COORDINATION - General questions or unclear intent
    7. APPROVE - User wants to approve the project

    Consider the context and natural language variations. For example:
    - "I want to build an app" = PROJECT_INITIALIZATION
    - "How is the project going?" = STATUS_REQUEST
    - "Let's plan this out" = PROJECT_PLANNING
    - "Start over" = SYSTEM_RESTART

    IMPORTANT: Respond with ONLY the category name (e.g., PROJECT_INITIALIZATION). Do not include any other text, explanations, or formatting."""
        
    pm = AssistantAgent("assistant", model_client=model_client, system_message=pm_system_message)
    user_proxy = UserProxyAgent("user_proxy", input_func=input)  # Use input() to get user input from console.

    # Create the termination condition which will end the conversation when the user says "APPROVE".
    termination = TextMentionTermination("APPROVE")

    # Create the team.
    team = RoundRobinGroupChat([pm, user_proxy], termination_condition=termination)

    # Run the conversation and stream to the console.
    stream = team.run_stream()
    # Use asyncio.run(...) when running in a script.
    await Console(stream, output_stats=True)
    await model_client.close()
    
if __name__ == "__main__":
    asyncio.run(main())