"""
Agent Factory for the handoffs pattern.

This module provides factory functions for creating and registering all agent types
in the handoffs system.
"""

from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from autogen_core.models import ChatCompletionClient

from base.AIAgent import AIAgent
from .triage_agent import TriageAgent
from .planning_agent import PlanningAgent
from .execution_agent import ExecutionAgent
from .quality_agent import QualityAgent
from .human_agent import HumanAgent
from .project_management_agent import ProjectManagementAgent
from .user_stories_agent import UserStoriesAgent
from .user_agent import UserAgent
from .tools import (
    TRIAGE_AGENT_TOPIC_TYPE,
    PLANNING_AGENT_TOPIC_TYPE,
    EXECUTION_AGENT_TOPIC_TYPE,
    QUALITY_AGENT_TOPIC_TYPE,
    HUMAN_AGENT_TOPIC_TYPE,
    PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
    USER_STORIES_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
)


class AgentFactory:
    """
    Factory class for creating and registering agents in the handoffs system.
    
    This class centralizes the creation and registration of all agent types,
    making the system more maintainable and configurable.
    """
    
    def __init__(self, runtime: SingleThreadedAgentRuntime, model_client: ChatCompletionClient):
        """
        Initialize the AgentFactory.
        
        Args:
            runtime: The agent runtime for registration
            model_client: The LLM client for AI agents
        """
        self.runtime = runtime
        self.model_client = model_client
        self.registered_agents = {}
    
    async def register_all_agents(self):
        """
        Register all agent types in the system.
        
        Returns:
            dict: Dictionary mapping topic types to registered agent types
        """
        # Register the triage agent
        self.registered_agents[TRIAGE_AGENT_TOPIC_TYPE] = await self._register_triage_agent()
        
        # Register the planning agent
        #self.registered_agents[PLANNING_AGENT_TOPIC_TYPE] = await self._register_planning_agent()
        
        # Register the execution agent
        self.registered_agents[EXECUTION_AGENT_TOPIC_TYPE] = await self._register_execution_agent()
        
        # Register the quality agent
        self.registered_agents[QUALITY_AGENT_TOPIC_TYPE] = await self._register_quality_agent()
        
        # Register the project management agent
        self.registered_agents[PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE] = await self._register_project_management_agent()
        
        # Register the user stories agent
        self.registered_agents[USER_STORIES_AGENT_TOPIC_TYPE] = await self._register_user_stories_agent()
        
        # Register the human agent
        self.registered_agents[HUMAN_AGENT_TOPIC_TYPE] = await self._register_human_agent()
        
        # Register the user agent
        self.registered_agents[USER_TOPIC_TYPE] = await self._register_user_agent()
        
        return self.registered_agents
    
    async def add_all_subscriptions(self):
        """Add subscriptions for all registered agents."""
        for topic_type, agent_type in self.registered_agents.items():
            await self.runtime.add_subscription(
                TypeSubscription(topic_type=topic_type, agent_type=agent_type.type)
            )
    
    async def _register_triage_agent(self):
        """Register the triage agent."""
        return await AIAgent.register(
            self.runtime,
            type=TRIAGE_AGENT_TOPIC_TYPE,
            factory=lambda: TriageAgent(self.model_client),
        )
    
    #async def _register_planning_agent(self):
    #    """Register the planning agent."""
    #    return await AIAgent.register(
    #        self.runtime,
    #        type=PLANNING_AGENT_TOPIC_TYPE,
    #        factory=lambda: PlanningAgent(self.model_client),
    #    )
    
    async def _register_execution_agent(self):
        """Register the execution agent."""
        return await AIAgent.register(
            self.runtime,
            type=EXECUTION_AGENT_TOPIC_TYPE,
            factory=lambda: ExecutionAgent(self.model_client),
        )
    
    async def _register_quality_agent(self):
        """Register the quality agent."""
        return await AIAgent.register(
            self.runtime,
            type=QUALITY_AGENT_TOPIC_TYPE,
            factory=lambda: QualityAgent(self.model_client),
        )
    
    async def _register_project_management_agent(self):
        """Register the project management agent."""
        return await AIAgent.register(
            self.runtime,
            type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            factory=lambda: ProjectManagementAgent(self.model_client),
        )
    
    async def _register_user_stories_agent(self):
        """Register the user stories agent."""
        return await AIAgent.register(
            self.runtime,
            type=USER_STORIES_AGENT_TOPIC_TYPE,
            factory=lambda: UserStoriesAgent(self.model_client),
        )
    
    async def _register_human_agent(self):
        """Register the human agent."""
        return await HumanAgent.register(
            self.runtime,
            type=HUMAN_AGENT_TOPIC_TYPE,
            factory=lambda: HumanAgent(
                agent_topic_type=HUMAN_AGENT_TOPIC_TYPE,
                user_topic_type=USER_TOPIC_TYPE,
            ),
        )
    
    async def _register_user_agent(self):
        """Register the user agent."""
        return await UserAgent.register(
            self.runtime,
            type=USER_TOPIC_TYPE,
            factory=lambda: UserAgent(
                user_topic_type=USER_TOPIC_TYPE,
                agent_topic_type=TRIAGE_AGENT_TOPIC_TYPE,  # Start with the triage agent
            ),
        )
