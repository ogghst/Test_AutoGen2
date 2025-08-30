"""
Agent Factory for the handoffs pattern.

This module provides factory functions for creating and registering all agent types
in the handoffs system.
"""

import asyncio

from autogen_core import SingleThreadedAgentRuntime, TypeSubscription
from autogen_core.models import ChatCompletionClient

from base.AIAgent import AIAgent
from .websocket_agent import WebSocketAgent
from .triage_agent import TriageAgent
from .planning_agent import PlanningAgent
from .execution_agent import ExecutionAgent
from .quality_agent import QualityAgent
from .human_agent import HumanAgent
from .project_management_agent import ProjectManagementAgent
from .user_stories_agent import UserStoriesAgent
from .user_profiler_agent import UserProfilerAgent
from .user_agent import UserAgent
from knowledge.knowledge_service import KnowledgeService
from .tools import (
    TRIAGE_AGENT_TOPIC_TYPE,
    PLANNING_AGENT_TOPIC_TYPE,
    EXECUTION_AGENT_TOPIC_TYPE,
    QUALITY_AGENT_TOPIC_TYPE,
    HUMAN_AGENT_TOPIC_TYPE,
    PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
    USER_STORIES_AGENT_TOPIC_TYPE,
    USER_PROFILER_AGENT_TOPIC_TYPE,
    USER_TOPIC_TYPE,
)
from .knowledge_tools import create_knowledge_tools


class AgentFactory:
    """
    Factory class for creating and registering agents in the handoffs system.
    
    This class centralizes the creation and registration of all agent types,
    making the system more maintainable and configurable.
    """
    
    def __init__(self, user_session):
        """
        Initialize the AgentFactory.
        
        Args:
            user_session: The user session object.
        """
        self.user_session = user_session
        self.runtime = user_session.runtime
        self.model_client = user_session.model_client
        self.knowledge_service = user_session.knowledge_service
        self.registered_agents = {}
        self.input_queue = user_session.input_queue
        self.response_queue = user_session.response_queue
    
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
        
        # Register the user profiler agent
        self.registered_agents[USER_PROFILER_AGENT_TOPIC_TYPE] = await self._register_user_profiler_agent()

        # Register the human agent
        self.registered_agents[HUMAN_AGENT_TOPIC_TYPE] = await self._register_human_agent()
        
        # Register the user agent
        #self.registered_agents[USER_TOPIC_TYPE] = await self._register_user_agent()
        
        self.registered_agents[USER_TOPIC_TYPE] = await self._register_websocket_agent()
        
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
            factory=lambda: TriageAgent(self.user_session),
        )
    
    #async def _register_planning_agent(self):
    #    """Register the planning agent."""
    #    return await AIAgent.register(
    #        self.runtime,
    #        type=PLANNING_AGENT_TOPIC_TYPE,
    #        factory=lambda: PlanningAgent(self.user_session),
    #    )
    
    async def _register_execution_agent(self):
        """Register the execution agent."""
        return await AIAgent.register(
            self.runtime,
            type=EXECUTION_AGENT_TOPIC_TYPE,
            factory=lambda: ExecutionAgent(self.user_session),
        )
    
    async def _register_quality_agent(self):
        """Register the quality agent."""
        return await AIAgent.register(
            self.runtime,
            type=QUALITY_AGENT_TOPIC_TYPE,
            factory=lambda: QualityAgent(self.user_session),
        )
    
    async def _register_project_management_agent(self):
        """Register the project management agent."""
        return await AIAgent.register(
            self.runtime,
            type=PROJECT_MANAGEMENT_AGENT_TOPIC_TYPE,
            factory=lambda: ProjectManagementAgent(
                user_session=self.user_session,
                tools=create_knowledge_tools(self.user_session),
            ),
        )
    
    async def _register_user_stories_agent(self):
        """Register the user stories agent."""
        return await AIAgent.register(
            self.runtime,
            type=USER_STORIES_AGENT_TOPIC_TYPE,
            factory=lambda: UserStoriesAgent(
                user_session=self.user_session,
                tools=create_knowledge_tools(self.user_session),
            ),
        )

    async def _register_user_profiler_agent(self):
        """Register the user profiler agent."""
        return await AIAgent.register(
            self.runtime,
            type=USER_PROFILER_AGENT_TOPIC_TYPE,
            factory=lambda: UserProfilerAgent(
                user_session=self.user_session,
                tools=create_knowledge_tools(self.user_session),
            ),
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

    async def _register_websocket_agent(self):
        # Create a websocket agent for this session
        return await WebSocketAgent.register(
            self.runtime,
            type=USER_TOPIC_TYPE,
            factory=lambda: WebSocketAgent(
                input_queue=self.input_queue,
                response_queue=self.response_queue,
                user_topic_type=USER_TOPIC_TYPE,
                agent_topic_type=TRIAGE_AGENT_TOPIC_TYPE,
            )
        )
        
        