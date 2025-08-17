"""
Main entry point for the Multi-Agent Project Management System.

This script initializes and runs the interactive command-line interface (CLI)
for managing software projects using a team of autonomous agents.
"""

import asyncio
import os
import sys
import logging

# Add the project root directory to the Python path to ensure correct module imports.
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import core components of the system.
from agents.project_manager import ProjectManagerAgent
from knowledge.knowledge_base import KnowledgeBase
from storage.document_store import DocumentStoreFactory
from config.settings import ConfigManager

# Import AutoGen classes for agent orchestration.

from autogen_agentchat.agents import UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat as GroupChat
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination

# Import logging configuration
from config.logging_config import setup_logging, get_logger, log_system_info

# --- Global Configuration ---
try:
    config_manager = ConfigManager()
    settings = config_manager.system
    # Setup logging based on settings
    setup_logging(
        log_level=settings.log_level.value,
        log_file=settings.log_file or os.path.join(settings.logs_path, "system.log"),
        console_logging=False,  # Keep console clean for UI
        max_bytes=10 * 1024 * 1024,  # 10MB
        backup_count=5
    )
    logger = get_logger(__name__)
except ValueError as e:
    print(f"\n❌ Configuration Error: {e}")
    print("Please ensure your .env file or environment variables are set correctly.")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ An unexpected error occurred during initial setup: {e}")
    sys.exit(1)


async def main():
    """
    Asynchronous main function to initialize and run the agent system.
    """
    log_system_info()
    logger.info("Starting Multi-Agent Project Management System")

    logger.info("Initializing system components...")
    try:
        kb = KnowledgeBase(kb_path=settings.knowledge_base_path)
        ds = DocumentStoreFactory.create_production(
            storage_path=settings.documents_path
        )
        logger.info("KnowledgeBase and DocumentStore initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        print(f"\n❌ Error initializing system components: {e}")
        return

    # --- Agent Initialization ---
    logger.info("Initializing agents...")
    try:
        project_manager = ProjectManagerAgent(
            knowledge_base=kb,
            document_store=ds
        )

        user_proxy = UserProxyAgent(
            name="HumanUser",
            description="A human user who provides commands and information to the project management system.",
            # Reverted to input_func for compatibility
            input_func=input,
        )
        logger.info("Agents initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}", exc_info=True)
        print(f"\n❌ Error initializing agents: {e}")
        return

    # --- Group Chat Setup ---
    termination = TextMentionTermination("exit", sources=[user_proxy])
    groupchat = GroupChat(
        participants=[project_manager, user_proxy],
        max_turns=config_manager.autogen.max_turns,
    )
    
    # --- Start Interactive Demo ---
    print("\n" + "="*60)
    print("      🤖 Multi-Agent Project Management System 🤖")
    print("="*60)
    print("\nWelcome! You are interacting with the Project Manager agent.")
    print("You can start by initializing a project. For example:")
    print("\n  init_project Name: E-commerce Platform, Objectives: Increase online sales, Stakeholders: Sales Team, IT Team\n")
    print("Other available commands: 'status', 'requirements', 'plan project'")
    print("\nType 'exit' to end the session.")
    print("-"*60)

    initial_message = "Hello, I am the user. I am ready to begin managing a project."

    logger.info("Starting group chat session")
    await Console(groupchat.run_stream(task=initial_message))
    logger.info("Group chat session completed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
        logger.info("System shutdown completed successfully")
    except (KeyboardInterrupt, EOFError):
        print("\n\nSession terminated by user. Goodbye!")
        logger.info("Session terminated by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        print("Check the logs for more details.")
        logger.error(f"Unexpected error during system execution: {e}", exc_info=True)
