"""
Main application entry point for the handoffs pattern.

This module orchestrates the entire handoffs system by:
1. Setting up logging
2. Creating the runtime and model client
3. Registering all agents
4. Starting the system and managing the user session
"""

import asyncio
import uuid
from autogen_core import SingleThreadedAgentRuntime, TopicId

from .base.utils import setup_logging, configure_oltp_tracing
from .base.model_client import create_model_client
from .agents.factory import AgentFactory
from .agents.tools import USER_TOPIC_TYPE
from .base.messaging import UserLogin


async def main():
    """
    Main function that orchestrates the handoffs pattern system.
    
    This function sets up the entire system, registers all agents, and manages
    the user session lifecycle.
    """
    # Setup logging
    logger = setup_logging()
    logger.info("Starting handoffs pattern system")
    

    tracer_provider = configure_oltp_tracing()
    
    # Create the runtime
    runtime = SingleThreadedAgentRuntime(tracer_provider=tracer_provider)
    
    # Create the model client
    logger.info("Creating model client with model: deepseek-chat")
    model_client = create_model_client()
    #logger.debug(f"API key: {model_client.api_key[:10] if model_client.api_key else 'None'}...")
    
    # Create agent factory and register all agents
    logger.info("Creating agent factory and registering agents")
    agent_factory = AgentFactory(runtime, model_client)
    registered_agents = await agent_factory.register_all_agents()
    
    # Add subscriptions for all agents
    logger.info("Adding subscriptions for all agents")
    await agent_factory.add_all_subscriptions()
    
    # Start the runtime
    logger.info("Starting runtime")
    runtime.start()
    
    # Create a new session for the user
    session_id = str(uuid.uuid4())
    logger.info(f"Creating user session: {session_id}")
    await runtime.publish_message(
        UserLogin(), 
        topic_id=TopicId(USER_TOPIC_TYPE, source=session_id)
    )
    
    # Run until completion
    logger.info("Waiting for runtime to complete")
    await runtime.stop_when_idle()
    
    # Cleanup
    logger.info("Runtime completed, closing model client")
    await model_client.close()
    logger.info("Handoffs pattern system shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
