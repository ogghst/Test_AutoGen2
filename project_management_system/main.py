"""
Main entry point for the Multi-Agent Project Management System.

This script initializes and runs the interactive command-line interface (CLI)
for managing software projects using a team of autonomous agents.
"""

import asyncio
import logging
import os
import sys

# Add the project root directory to the Python path to ensure correct module imports.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    # Load environment variables from a .env file for configuration.
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: 'python-dotenv' is not installed. Please run 'pip install python-dotenv' or set environment variables manually.")

# Import core components of the system.
from agents.project_manager import ProjectManagerAgent
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStore

# Import AutoGen classes for agent orchestration.
from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat as GroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination


# --- Logger Configuration ---
# Configure logging to provide informative output during system operation.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# Reduce verbosity of AutoGen's internal logging.
logging.getLogger("autogen").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main():
    """
    Asynchronous main function to initialize and run the agent system.
    """
    # --- Configuration Check ---
    # Verify that the required DeepSeek API key is available.
    if not os.getenv("DEEPSEEK_API_KEY"):
        logger.error("DEEPSEEK_API_KEY environment variable not set.")
        print("\n❌ ERROR: DEEPSEEK_API_KEY not found.")
        print("Please get a free API key from https://platform.deepseek.com/")
        print("Then, create a file named '.env' in the 'project_management_system' directory and add the line:")
        print("DEEPSEEK_API_KEY='your_api_key_here'")
        return

    # --- System Initialization ---
    logger.info("Initializing system components...")
    try:
        kb = KnowledgeBase(kb_path="knowledge/knowledge_base.jsonld")
        ds = DocumentStore(storage_path="output_documents")
        logger.info("KnowledgeBase and DocumentStore initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        return

    # --- Agent Initialization ---
    logger.info("Initializing agents...")
    try:
        # The Project Manager agent orchestrates the project workflow.
        project_manager = ProjectManagerAgent(
            knowledge_base=kb,
            document_store=ds
        )

        def non_interactive_input(prompt: str) -> str:
            """A function to handle input in a non-interactive environment."""
            print(prompt)
            return "exit"

        # The User Proxy agent acts as the interface for the human user.
        user_proxy = UserProxyAgent(
            name="HumanUser",
            description="A human user who provides commands and information to the project management system.",
            input_func=non_interactive_input
        )
        logger.info("Agents initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}", exc_info=True)
        return

    # --- Group Chat Setup ---
    # Configure the group chat to manage the conversation between agents.
    termination = TextMentionTermination("exit", sources=["HumanUser"])
    groupchat = GroupChat(
        participants=[project_manager, user_proxy],
        termination_condition=termination
    )
    
    # --- Start Interactive Demo ---
    print("\n" + "="*60)
    print("      🤖 Multi-Agent Project Management System 🤖")
    print("="*60)
    print("\nWelcome! You are interacting with the Project Manager agent.")
    print("You can start by initializing a project. For example:")
    print("\n  init_project Name: E-commerce Platform, Objectives: Increase online sales, Stakeholders: Sales Team, IT Team\n")
    print("Other available commands: 'status', 'requirements', 'plan project'")
    print("\nType 'quit' or 'exit' to end the session.")
    print("-"*60)

    # This initial message kicks off the conversation. The user will then be
    # prompted for their first real command by the UserProxyAgent.
    initial_message = "Hello, I am the user. I am ready to begin managing a project."

    await Console(groupchat.run_stream(task=initial_message))

if __name__ == "__main__":
    try:
        # Run the asynchronous main function.
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        # Handle graceful shutdown on user interruption.
        print("\n\nSession terminated by user. Goodbye!")


