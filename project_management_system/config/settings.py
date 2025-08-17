"""
Configuration settings for the multi-agent project management system
Compatible with AutoGen 0.7.2+ and DeepSeek API
Provides centralized configuration management with environment variable support
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from enum import Enum
import json

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

# AutoGen 0.7.2+ compatibility check
try:
    from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
    from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.messages import TextMessage, BaseChatMessage
    from autogen_core import CancellationToken
    from autogen_core.models import ChatCompletionClient
    from autogen_core.memory import Memory
    AUTOGEN_AVAILABLE = True
    AUTOGEN_VERSION = "0.7.2+"
except ImportError:
    AUTOGEN_AVAILABLE = False
    AUTOGEN_VERSION = "not_available"

# Load environment variables
if DOTENV_AVAILABLE:
    load_dotenv()


# ============================================================================
# ENUMS
# ============================================================================

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"


class TeamPattern(Enum):
    ROUND_ROBIN = "round_robin"
    SELECTOR = "selector"
    HIERARCHICAL = "hierarchical"
    SWARM = "swarm"


class TerminationCondition(Enum):
    MAX_MESSAGES = "max_messages"
    TEXT_MENTION = "text_mention"
    TIMEOUT = "timeout"
    CUSTOM = "custom"


# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API"""
    api_key: str
    model: str = "deepseek-chat"
    api_url: str = "https://api.deepseek.com/v1/chat/completions"
    timeout: float = 60.0
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 0.95
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    max_retries: int = 3
    retry_delay: float = 1.0
    enable_streaming: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_key": "***REDACTED***",  # Don't expose API key
            "model": self.model,
            "api_url": self.api_url,
            "timeout": self.timeout,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "enable_streaming": self.enable_streaming
        }
    
    def get_headers(self) -> Dict[str, str]:
        """Get API headers for requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AutoGen-ProjectManagement/1.0"
        }
    
    def get_payload_template(self) -> Dict[str, Any]:
        """Get template payload for API requests"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.enable_streaming
        }


@dataclass
class AutoGenConfig:
    """Configuration for AutoGen 0.7.2+ system"""
    default_team_pattern: TeamPattern = TeamPattern.ROUND_ROBIN
    max_turns: int = 20
    max_consecutive_auto_reply: int = 3
    enable_human_input_mode: bool = True
    human_input_timeout: float = 300.0  # 5 minutes
    enable_code_execution: bool = False
    code_execution_timeout: float = 60.0
    enable_function_calling: bool = True
    enable_memory: bool = True
    memory_max_tokens: int = 8000
    enable_logging: bool = True
    log_conversation: bool = True
    cache_seed: Optional[int] = 42
    
    # AutoGen 0.7.2+ specific settings
    enable_structured_output: bool = True
    enable_handoffs: bool = True
    enable_tool_calling: bool = True
    enable_workbench: bool = False
    model_client_stream: bool = False
    reflect_on_tool_use: bool = True
    max_tool_iterations: int = 3
    
    # Termination conditions
    termination_conditions: List[Dict[str, Any]] = field(default_factory=lambda: [
        {"type": "max_messages", "value": 20},
        {"type": "text_mention", "keywords": ["TERMINATE", "FINISHED", "COMPLETE"]},
        {"type": "timeout", "value": 1800}  # 30 minutes
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "default_team_pattern": self.default_team_pattern.value,
            "max_turns": self.max_turns,
            "max_consecutive_auto_reply": self.max_consecutive_auto_reply,
            "enable_human_input_mode": self.enable_human_input_mode,
            "human_input_timeout": self.human_input_timeout,
            "enable_code_execution": self.enable_code_execution,
            "code_execution_timeout": self.code_execution_timeout,
            "enable_function_calling": self.enable_function_calling,
            "enable_memory": self.enable_memory,
            "memory_max_tokens": self.memory_max_tokens,
            "enable_logging": self.enable_logging,
            "log_conversation": self.log_conversation,
            "cache_seed": self.cache_seed,
            "enable_structured_output": self.enable_structured_output,
            "enable_handoffs": self.enable_handoffs,
            "enable_tool_calling": self.enable_tool_calling,
            "enable_workbench": self.enable_workbench,
            "model_client_stream": self.model_client_stream,
            "reflect_on_tool_use": self.reflect_on_tool_use,
            "max_tool_iterations": self.max_tool_iterations,
            "termination_conditions": self.termination_conditions
        }


@dataclass
class SystemConfig:
    """General system configuration"""
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Paths
    knowledge_base_path: str = "knowledge_base.jsonld"
    documents_path: str = "output_documents"
    logs_path: str = "logs"
    temp_path: str = "temp"
    config_path: str = "config"
    
    # Performance
    max_concurrent_operations: int = 10
    request_timeout: float = 60.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Features
    enable_metrics: bool = True
    enable_backup: bool = True
    enable_search_index: bool = True
    enable_versioning: bool = True
    auto_cleanup: bool = True
    max_versions_per_document: int = 10
    
    # Security
    enable_api_key_validation: bool = True
    enable_rate_limiting: bool = False
    rate_limit_requests_per_minute: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "log_level": self.log_level.value,
            "log_file": self.log_file,
            "log_format": self.log_format,
            "log_date_format": self.log_date_format,
            "knowledge_base_path": self.knowledge_base_path,
            "documents_path": self.documents_path,
            "logs_path": self.logs_path,
            "temp_path": self.temp_path,
            "config_path": self.config_path,
            "max_concurrent_operations": self.max_concurrent_operations,
            "request_timeout": self.request_timeout,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "enable_metrics": self.enable_metrics,
            "enable_backup": self.enable_backup,
            "enable_search_index": self.enable_search_index,
            "enable_versioning": self.enable_versioning,
            "auto_cleanup": self.auto_cleanup,
            "max_versions_per_document": self.max_versions_per_document,
            "enable_api_key_validation": self.enable_api_key_validation,
            "enable_rate_limiting": self.enable_rate_limiting,
            "rate_limit_requests_per_minute": self.rate_limit_requests_per_minute
        }


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    name: str
    role: str
    description: str = ""
    system_message: Optional[str] = None
    model_provider: ModelProvider = ModelProvider.DEEPSEEK
    enable_tools: bool = True
    enable_handoffs: bool = True
    enable_memory: bool = True
    max_consecutive_auto_reply: int = 3
    human_input_mode: str = "NEVER"  # NEVER, TERMINATE, ALWAYS
    code_execution_config: Optional[Dict[str, Any]] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    # AutoGen 0.7.2+ specific
    produced_message_types: List[str] = field(default_factory=lambda: ["TextMessage"])
    model_client_stream: bool = False
    reflect_on_tool_use: bool = True
    max_tool_iterations: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "system_message": self.system_message,
            "model_provider": self.model_provider.value,
            "enable_tools": self.enable_tools,
            "enable_handoffs": self.enable_handoffs,
            "enable_memory": self.enable_memory,
            "max_consecutive_auto_reply": self.max_consecutive_auto_reply,
            "human_input_mode": self.human_input_mode,
            "code_execution_config": self.code_execution_config,
            "custom_config": self.custom_config,
            "produced_message_types": self.produced_message_types,
            "model_client_stream": self.model_client_stream,
            "reflect_on_tool_use": self.reflect_on_tool_use,
            "max_tool_iterations": self.max_tool_iterations
        }


@dataclass
class TeamConfig:
    """Configuration for AutoGen teams"""
    name: str
    pattern: TeamPattern = TeamPattern.ROUND_ROBIN
    agents: List[str] = field(default_factory=list)
    max_turns: int = 20
    termination_conditions: List[Dict[str, Any]] = field(default_factory=list)
    allow_repeat_speaker: bool = True
    enable_clear_history: bool = True
    custom_speaker_selection: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pattern": self.pattern.value,
            "agents": self.agents,
            "max_turns": self.max_turns,
            "termination_conditions": self.termination_conditions,
            "allow_repeat_speaker": self.allow_repeat_speaker,
            "enable_clear_history": self.enable_clear_history,
            "custom_speaker_selection": self.custom_speaker_selection
        }


# ============================================================================
# MAIN CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Central configuration manager for the multi-agent system"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (JSON)
        """
        self.config_file = config_file
        self._config_cache: Dict[str, Any] = {}
        
        # Initialize configurations
        self.deepseek = self._load_deepseek_config()
        self.autogen = self._load_autogen_config()
        self.system = self._load_system_config()
        
        # Agent and team configurations
        self.agents: Dict[str, AgentConfig] = {}
        self.teams: Dict[str, TeamConfig] = {}
        
        # Load from config file if provided
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
        
        # Load default agent configurations
        self._load_default_agents()
        
        # Validate configuration
        self._validate_configuration()
    
    def _load_deepseek_config(self) -> DeepSeekConfig:
        """Load DeepSeek configuration from environment"""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DEEPSEEK_API_KEY environment variable is required. "
                "Get your API key from https://platform.deepseek.com/"
            )
        
        return DeepSeekConfig(
            api_key=api_key,
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            api_url=os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions"),
            timeout=float(os.getenv("DEEPSEEK_TIMEOUT", "60.0")),
            max_tokens=int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000")),
            temperature=float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")),
            top_p=float(os.getenv("DEEPSEEK_TOP_P", "0.95")),
            frequency_penalty=float(os.getenv("DEEPSEEK_FREQUENCY_PENALTY", "0.1")),
            presence_penalty=float(os.getenv("DEEPSEEK_PRESENCE_PENALTY", "0.1")),
            max_retries=int(os.getenv("DEEPSEEK_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("DEEPSEEK_RETRY_DELAY", "1.0")),
            enable_streaming=os.getenv("DEEPSEEK_ENABLE_STREAMING", "false").lower() == "true"
        )
    
    def _load_autogen_config(self) -> AutoGenConfig:
        """Load AutoGen configuration from environment"""
        default_pattern = os.getenv("AUTOGEN_DEFAULT_PATTERN", "round_robin")
        try:
            team_pattern = TeamPattern(default_pattern)
        except ValueError:
            team_pattern = TeamPattern.ROUND_ROBIN
        
        termination_conditions = []
        
        # Max messages termination
        max_messages = int(os.getenv("AUTOGEN_MAX_MESSAGES", "20"))
        termination_conditions.append({"type": "max_messages", "value": max_messages})
        
        # Text mention termination
        termination_keywords = os.getenv("AUTOGEN_TERMINATION_KEYWORDS", "TERMINATE,FINISHED,COMPLETE").split(",")
        termination_conditions.append({"type": "text_mention", "keywords": termination_keywords})
        
        # Timeout termination
        timeout_seconds = int(os.getenv("AUTOGEN_TIMEOUT", "1800"))  # 30 minutes
        termination_conditions.append({"type": "timeout", "value": timeout_seconds})
        
        return AutoGenConfig(
            default_team_pattern=team_pattern,
            max_turns=int(os.getenv("AUTOGEN_MAX_TURNS", "20")),
            max_consecutive_auto_reply=int(os.getenv("AUTOGEN_MAX_CONSECUTIVE_REPLY", "3")),
            enable_human_input_mode=os.getenv("AUTOGEN_HUMAN_INPUT", "true").lower() == "true",
            human_input_timeout=float(os.getenv("AUTOGEN_HUMAN_TIMEOUT", "300.0")),
            enable_code_execution=os.getenv("AUTOGEN_CODE_EXECUTION", "false").lower() == "true",
            code_execution_timeout=float(os.getenv("AUTOGEN_CODE_TIMEOUT", "60.0")),
            enable_function_calling=os.getenv("AUTOGEN_FUNCTION_CALLING", "true").lower() == "true",
            enable_memory=os.getenv("AUTOGEN_MEMORY", "true").lower() == "true",
            memory_max_tokens=int(os.getenv("AUTOGEN_MEMORY_MAX_TOKENS", "8000")),
            enable_logging=os.getenv("AUTOGEN_LOGGING", "true").lower() == "true",
            log_conversation=os.getenv("AUTOGEN_LOG_CONVERSATION", "true").lower() == "true",
            cache_seed=int(os.getenv("AUTOGEN_CACHE_SEED", "42")) if os.getenv("AUTOGEN_CACHE_SEED") else None,
            enable_structured_output=os.getenv("AUTOGEN_STRUCTURED_OUTPUT", "true").lower() == "true",
            enable_handoffs=os.getenv("AUTOGEN_HANDOFFS", "true").lower() == "true",
            enable_tool_calling=os.getenv("AUTOGEN_TOOL_CALLING", "true").lower() == "true",
            enable_workbench=os.getenv("AUTOGEN_WORKBENCH", "false").lower() == "true",
            model_client_stream=os.getenv("AUTOGEN_MODEL_STREAM", "false").lower() == "true",
            reflect_on_tool_use=os.getenv("AUTOGEN_REFLECT_TOOL_USE", "true").lower() == "true",
            max_tool_iterations=int(os.getenv("AUTOGEN_MAX_TOOL_ITERATIONS", "3")),
            termination_conditions=termination_conditions
        )
    
    def _load_system_config(self) -> SystemConfig:
        """Load system configuration from environment"""
        log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            log_level = LogLevel(log_level_str)
        except ValueError:
            log_level = LogLevel.INFO
        
        return SystemConfig(
            debug=os.getenv("DEBUG", "false").lower() == "true",
            log_level=log_level,
            log_file=os.getenv("LOG_FILE"),
            log_format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
            log_date_format=os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S"),
            knowledge_base_path=os.getenv("KNOWLEDGE_BASE_PATH", "knowledge_base.jsonld"),
            documents_path=os.getenv("DOCUMENTS_PATH", "output_documents"),
            logs_path=os.getenv("LOGS_PATH", "logs"),
            temp_path=os.getenv("TEMP_PATH", "temp"),
            config_path=os.getenv("CONFIG_PATH", "config"),
            max_concurrent_operations=int(os.getenv("MAX_CONCURRENT_OPERATIONS", "10")),
            request_timeout=float(os.getenv("REQUEST_TIMEOUT", "60.0")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
            enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
            enable_backup=os.getenv("ENABLE_BACKUP", "true").lower() == "true",
            enable_search_index=os.getenv("ENABLE_SEARCH_INDEX", "true").lower() == "true",
            enable_versioning=os.getenv("ENABLE_VERSIONING", "true").lower() == "true",
            auto_cleanup=os.getenv("AUTO_CLEANUP", "true").lower() == "true",
            max_versions_per_document=int(os.getenv("MAX_VERSIONS_PER_DOCUMENT", "10")),
            enable_api_key_validation=os.getenv("ENABLE_API_KEY_VALIDATION", "true").lower() == "true",
            enable_rate_limiting=os.getenv("ENABLE_RATE_LIMITING", "false").lower() == "true",
            rate_limit_requests_per_minute=int(os.getenv("RATE_LIMIT_RPM", "100"))
        )
    
    def _load_default_agents(self):
        """Load default agent configurations"""
        self.agents = {
            "project_manager": AgentConfig(
                name="ProjectManager",
                role="project_manager",
                description="Coordinates project workflow, manages stakeholder communication, and ensures project objectives are met",
                system_message="You are a Project Manager agent responsible for coordinating project activities, managing timelines, and ensuring successful project delivery. Use your knowledge of project management best practices to guide the team.",
                enable_tools=True,
                enable_handoffs=True,
                human_input_mode="TERMINATE",
                reflect_on_tool_use=True,
                max_tool_iterations=3
            ),
            
            "requirements_analyst": AgentConfig(
                name="RequirementsAnalyst",
                role="requirements_analyst",
                description="Gathers, analyzes, and documents project requirements through stakeholder engagement",
                system_message="You are a Requirements Analyst agent specialized in gathering, analyzing, and documenting project requirements. Focus on creating comprehensive and clear requirements documentation.",
                enable_tools=True,
                enable_handoffs=True,
                human_input_mode="ALWAYS",
                reflect_on_tool_use=True,
                max_tool_iterations=2
            ),
            
            "technical_writer": AgentConfig(
                name="TechnicalWriter",
                role="technical_writer",
                description="Creates and maintains comprehensive technical documentation for projects",
                system_message="You are a Technical Writer agent responsible for creating clear, comprehensive technical documentation. Focus on structure, clarity, and completeness.",
                enable_tools=True,
                enable_handoffs=True,
                human_input_mode="NEVER",
                reflect_on_tool_use=True,
                max_tool_iterations=2
            ),
            
            "change_detector": AgentConfig(
                name="ChangeDetector",
                role="change_detector",
                description="Monitors and analyzes changes to maintain documentation consistency",
                system_message="You are a Change Detector agent that monitors project changes and ensures documentation remains up-to-date. Focus on identifying impacts and coordinating updates.",
                enable_tools=True,
                enable_handoffs=True,
                human_input_mode="NEVER",
                reflect_on_tool_use=False,
                max_tool_iterations=1
            )
        }
        
        # Default team configuration
        self.teams["default"] = TeamConfig(
            name="DefaultProjectTeam",
            pattern=TeamPattern.ROUND_ROBIN,
            agents=["project_manager", "requirements_analyst", "technical_writer", "change_detector"],
            max_turns=20,
            termination_conditions=self.autogen.termination_conditions,
            allow_repeat_speaker=True,
            enable_clear_history=True
        )
    
    def _load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update configurations from file
            if "deepseek" in config_data:
                for key, value in config_data["deepseek"].items():
                    if hasattr(self.deepseek, key):
                        setattr(self.deepseek, key, value)
            
            if "autogen" in config_data:
                for key, value in config_data["autogen"].items():
                    if hasattr(self.autogen, key):
                        if key == "default_team_pattern":
                            setattr(self.autogen, key, TeamPattern(value))
                        else:
                            setattr(self.autogen, key, value)
            
            if "system" in config_data:
                for key, value in config_data["system"].items():
                    if hasattr(self.system, key):
                        if key == "log_level":
                            setattr(self.system, key, LogLevel(value))
                        else:
                            setattr(self.system, key, value)
            
            # Load agents configuration
            if "agents" in config_data:
                for agent_name, agent_data in config_data["agents"].items():
                    self.agents[agent_name] = AgentConfig(**agent_data)
            
            # Load teams configuration
            if "teams" in config_data:
                for team_name, team_data in config_data["teams"].items():
                    if "pattern" in team_data:
                        team_data["pattern"] = TeamPattern(team_data["pattern"])
                    self.teams[team_name] = TeamConfig(**team_data)
            
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_file}: {e}")
    
    def _validate_configuration(self):
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Validate DeepSeek configuration
        if not self.deepseek.api_key or not self.deepseek.api_key.startswith("sk-"):
            errors.append("Invalid DeepSeek API key format (should start with 'sk-')")
        
        if self.deepseek.temperature < 0.0 or self.deepseek.temperature > 2.0:
            errors.append("DeepSeek temperature must be between 0.0 and 2.0")
        
        if self.deepseek.max_tokens < 1 or self.deepseek.max_tokens > 32000:
            warnings.append("DeepSeek max_tokens should be between 1 and 32000")
        
        # Validate AutoGen configuration
        if not AUTOGEN_AVAILABLE:
            warnings.append(f"AutoGen not available (required version: >=0.7.2)")
        
        if self.autogen.max_turns < 1:
            errors.append("AutoGen max_turns must be at least 1")
        
        if self.autogen.human_input_timeout < 10.0:
            warnings.append("Human input timeout is very short (<10 seconds)")
        
        # Validate system paths
        for path_attr in ["knowledge_base_path", "documents_path", "logs_path", "temp_path"]:
            path_value = getattr(self.system, path_attr)
            try:
                Path(path_value).parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                warnings.append(f"Cannot create directory for {path_attr}: {e}")
        
        # Validate agents
        for agent_name, agent_config in self.agents.items():
            if not agent_config.name or not agent_config.role:
                errors.append(f"Agent {agent_name} missing required name or role")
            
            if agent_config.human_input_mode not in ["NEVER", "TERMINATE", "ALWAYS"]:
                errors.append(f"Agent {agent_name} has invalid human_input_mode")
        
        # Validate teams
        for team_name, team_config in self.teams.items():
            if not team_config.agents:
                errors.append(f"Team {team_name} has no agents configured")
            
            for agent_name in team_config.agents:
                if agent_name not in self.agents:
                    errors.append(f"Team {team_name} references unknown agent: {agent_name}")
        
        # Report validation results
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
            raise ValueError(error_msg)
        
        if warnings:
            warning_msg = "Configuration warnings:\n" + "\n".join(f"  - {warning}" for warning in warnings)
            print(f"⚠️ {warning_msg}")
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent"""
        return self.agents.get(agent_name)
    
    def get_team_config(self, team_name: str) -> Optional[TeamConfig]:
        """Get configuration for a specific team"""
        return self.teams.get(team_name)
    
    def add_agent_config(self, agent_name: str, config: AgentConfig):
        """Add or update agent configuration"""
        self.agents[agent_name] = config
    
    def add_team_config(self, team_name: str, config: TeamConfig):
        """Add or update team configuration"""
        self.teams[team_name] = config
    
    def save_to_file(self, config_file: str):
        """Save current configuration to JSON file"""
        config_data = {
            "deepseek": self.deepseek.to_dict(),
            "autogen": self.autogen.to_dict(),
            "system": self.system.to_dict(),
            "agents": {name: config.to_dict() for name, config in self.agents.items()},
            "teams": {name: config.to_dict() for name, config in self.teams.items()}
        }
        
        try:
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_file}: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "deepseek": self.deepseek.to_dict(),
            "autogen": self.autogen.to_dict(),
            "system": self.system.to_dict(),
            "agents_count": len(self.agents),
            "teams_count": len(self.teams),
            "autogen_available": AUTOGEN_AVAILABLE,
            "autogen_version": AUTOGEN_VERSION
        }
    
    def reload_configuration(self):
        """Reload configuration from environment variables and config file"""
        logger = logging.getLogger(__name__)
        logger.info("Reloading configuration...")
        
        # Reload from environment
        self.deepseek = self._load_deepseek_config()
        self.autogen = self._load_autogen_config()
        self.system = self._load_system_config()
        
        # Reload from config file if it exists
        if self.config_file and Path(self.config_file).exists():
            self._load_from_file(self.config_file)
        
        # Revalidate
        self._validate_configuration()
        logger.info("Configuration reloaded successfully")
    
    def export_environment_template(self, output_file: str = "env_template.txt"):
        """Export environment variable template for configuration"""
        template = """# Environment Variables Template for Multi-Agent Project Management System
# Copy this file to .env and fill in your values

# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=60.0
DEEPSEEK_MAX_TOKENS=4000
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_TOP_P=0.95
DEEPSEEK_FREQUENCY_PENALTY=0.1
DEEPSEEK_PRESENCE_PENALTY=0.1
DEEPSEEK_MAX_RETRIES=3
DEEPSEEK_RETRY_DELAY=1.0
DEEPSEEK_ENABLE_STREAMING=false

# AutoGen Configuration
AUTOGEN_DEFAULT_PATTERN=round_robin
AUTOGEN_MAX_TURNS=20
AUTOGEN_MAX_CONSECUTIVE_REPLY=3
AUTOGEN_HUMAN_INPUT=true
AUTOGEN_HUMAN_TIMEOUT=300.0
AUTOGEN_CODE_EXECUTION=false
AUTOGEN_CODE_TIMEOUT=60.0
AUTOGEN_FUNCTION_CALLING=true
AUTOGEN_MEMORY=true
AUTOGEN_MEMORY_MAX_TOKENS=8000
AUTOGEN_LOGGING=true
AUTOGEN_LOG_CONVERSATION=true
AUTOGEN_CACHE_SEED=42
AUTOGEN_STRUCTURED_OUTPUT=true
AUTOGEN_HANDOFFS=true
AUTOGEN_TOOL_CALLING=true
AUTOGEN_WORKBENCH=false
AUTOGEN_MODEL_STREAM=false
AUTOGEN_REFLECT_TOOL_USE=true
AUTOGEN_MAX_TOOL_ITERATIONS=3
AUTOGEN_MAX_MESSAGES=20
AUTOGEN_TERMINATION_KEYWORDS=TERMINATE,FINISHED,COMPLETE
AUTOGEN_TIMEOUT=1800

# System Configuration
DEBUG=false
LOG_LEVEL=INFO
LOG_FILE=
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_DATE_FORMAT=%Y-%m-%d %H:%M:%S
KNOWLEDGE_BASE_PATH=knowledge_base.jsonld
DOCUMENTS_PATH=output_documents
LOGS_PATH=logs
TEMP_PATH=temp
CONFIG_PATH=config
MAX_CONCURRENT_OPERATIONS=10
REQUEST_TIMEOUT=60.0
MAX_RETRIES=3
RETRY_DELAY=1.0
ENABLE_METRICS=true
ENABLE_BACKUP=true
ENABLE_SEARCH_INDEX=true
ENABLE_VERSIONING=true
AUTO_CLEANUP=true
MAX_VERSIONS_PER_DOCUMENT=10
ENABLE_API_KEY_VALIDATION=true
ENABLE_RATE_LIMITING=false
RATE_LIMIT_RPM=100
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"✅ Environment template exported to {output_file}")
        except Exception as e:
            print(f"❌ Failed to export environment template: {e}")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_config_manager(config_file: Optional[str] = None) -> ConfigManager:
    """
    Get a configured ConfigManager instance
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Configured ConfigManager instance
    """
    return ConfigManager(config_file)


def create_default_config(config_file: str = "config/default_config.json"):
    """
    Create a default configuration file
    
    Args:
        config_file: Path where to save the default configuration
    """
    config_manager = ConfigManager()
    config_manager.save_to_file(config_file)
    print(f"✅ Default configuration saved to {config_file}")


def validate_config_file(config_file: str) -> bool:
    """
    Validate a configuration file
    
    Args:
        config_file: Path to configuration file to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        config_manager = ConfigManager(config_file)
        print("✅ Configuration file is valid")
        return True
    except Exception as e:
        print(f"❌ Configuration file validation failed: {e}")
        return False


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Example usage and testing
    try:
        print("🔧 Multi-Agent Project Management System - Configuration Manager")
        print("=" * 70)
        
        # Create default configuration
        config_manager = get_config_manager()
        
        # Display configuration summary
        summary = config_manager.get_config_summary()
        print("\n📋 Configuration Summary:")
        print(f"  • DeepSeek API: {'✅ Configured' if summary['deepseek']['api_key'] == '***REDACTED***' else '❌ Not configured'}")
        print(f"  • AutoGen: {'✅ Available' if summary['autogen_available'] else '❌ Not available'} ({summary['autogen_version']})")
        print(f"  • Agents: {summary['agents_count']}")
        print(f"  • Teams: {summary['teams_count']}")
        
        # Export environment template
        config_manager.export_environment_template()
        
        # Create default config file
        create_default_config()
        
        print("\n✅ Configuration manager initialized successfully!")
        
    except Exception as e:
        print(f"\n❌ Error initializing configuration manager: {e}")
        sys.exit(1) 