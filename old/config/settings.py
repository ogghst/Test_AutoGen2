
"""
Configuration settings for the multi-agent project management system
Compatible with AutoGen 0.7.2+ and DeepSeek API
Provides centralized configuration management from a single JSON file.
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

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
        data = asdict(self)
        data["api_key"] = "***REDACTED***"  # Don't expose API key
        return data
    
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
class OllamaConfig:
    """Configuration for Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
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
        return asdict(self)

    def get_api_url(self) -> str:
        """Get the full API URL for chat completions"""
        return f"{self.base_url.rstrip('/')}/api/chat"

    def get_payload_template(self) -> Dict[str, Any]:
        """Get template payload for Ollama API requests"""
        return {
            "model": self.model,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "top_p": self.top_p,
                "frequency_penalty": self.frequency_penalty,
                "presence_penalty": self.presence_penalty,
            },
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
        data = asdict(self)
        data["default_team_pattern"] = self.default_team_pattern.value
        return data


@dataclass
class SystemConfig:
    """General system configuration"""
    debug: bool = False
    log_level: LogLevel = LogLevel.INFO
    log_file: Optional[str] = None
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # Paths
    knowledge_base_path: str = "../knowledge_base"
    documents_path: str = "../output_documents"
    logs_path: str = "../logs"
    temp_path: str = "../temp"
    config_path: str = "../config"
    
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
        data = asdict(self)
        data["log_level"] = self.log_level.value
        return data


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
        data = asdict(self)
        data["model_provider"] = self.model_provider.value
        return data


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
        data = asdict(self)
        data["pattern"] = self.pattern.value
        return data


# ============================================================================
# MAIN CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Central configuration manager for the multi-agent system"""
    
    def __init__(self, config_file: str):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file (JSON)
        """
        self.config_file = Path(config_file)
        self._config_cache: Dict[str, Any] = {}
        self.reload_configuration()

    def _load_from_file(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not self.config_file.is_file():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from {self.config_file}: {e}")

    def reload_configuration(self):
        """Reload configuration from the JSON file"""
        logger = logging.getLogger(__name__)
        logger.info("Reloading configuration from %s...", self.config_file)
        
        self._config_cache = self._load_from_file()

        provider_str = self._config_cache.get("llm_provider", "deepseek").lower()
        try:
            self.llm_provider = ModelProvider(provider_str)
        except ValueError:
            raise ValueError(f"Invalid llm_provider: {provider_str}. Must be one of {[p.value for p in ModelProvider]}")

        self.llm_config = self._load_llm_config()
        self.autogen = self._load_autogen_config()
        self.system = self._load_system_config()
        self.agents = self._load_agents_config()
        self.teams = self._load_teams_config()
        
        self._validate_configuration()
        logger.info("Configuration reloaded successfully")

    def _load_llm_config(self) -> Union[DeepSeekConfig, OllamaConfig]:
        """Load configuration for the selected LLM provider."""
        config_data = self._config_cache.get(self.llm_provider.value)
        if not config_data:
            raise ValueError(f"Missing configuration for LLM provider '{self.llm_provider.value}' in config file.")
        
        if self.llm_provider == ModelProvider.DEEPSEEK:
            return DeepSeekConfig(**config_data)
        elif self.llm_provider == ModelProvider.OLLAMA:
            return OllamaConfig(**config_data)
        else:
            raise NotImplementedError(f"LLM provider '{self.llm_provider.value}' is not implemented.")

    def _load_autogen_config(self) -> AutoGenConfig:
        """Load AutoGen configuration from file"""
        config_data = self._config_cache.get("autogen")
        if not config_data:
            raise ValueError("Missing 'autogen' configuration in config file.")
        
        if 'default_team_pattern' in config_data:
            config_data['default_team_pattern'] = TeamPattern(config_data['default_team_pattern'])
        
        return AutoGenConfig(**config_data)

    def _load_system_config(self) -> SystemConfig:
        """Load system configuration from file"""
        config_data = self._config_cache.get("system")
        if not config_data:
            raise ValueError("Missing 'system' configuration in config file.")
        
        if 'log_level' in config_data:
            config_data['log_level'] = LogLevel(config_data['log_level'])
            
        return SystemConfig(**config_data)

    def _load_agents_config(self) -> Dict[str, AgentConfig]:
        """Load agents configuration from file"""
        agents_data = self._config_cache.get("agents", {})
        agents = {}
        for name, config in agents_data.items():
            if 'model_provider' in config:
                config['model_provider'] = ModelProvider(config['model_provider'])
            agents[name] = AgentConfig(**config)
        return agents

    def _load_teams_config(self) -> Dict[str, TeamConfig]:
        """Load teams configuration from file"""
        teams_data = self._config_cache.get("teams", {})
        teams = {}
        for name, config in teams_data.items():
            if 'pattern' in config:
                config['pattern'] = TeamPattern(config['pattern'])
            teams[name] = TeamConfig(**config)
        return teams

    def _validate_configuration(self):
        """Validate configuration settings"""
        errors = []
        warnings = []
        
        # Validate LLM configuration
        if self.llm_provider == ModelProvider.DEEPSEEK:
            if not self.llm_config.api_key or not self.llm_config.api_key.startswith("sk-"):
                errors.append("Invalid DeepSeek API key format (should start with 'sk-')")
            if self.llm_config.temperature < 0.0 or self.llm_config.temperature > 2.0:
                errors.append("DeepSeek temperature must be between 0.0 and 2.0")
            if self.llm_config.max_tokens < 1 or self.llm_config.max_tokens > 32000:
                warnings.append("DeepSeek max_tokens is recommended to be between 1 and 32000")
        
        elif self.llm_provider == ModelProvider.OLLAMA:
            if not self.llm_config.base_url.startswith("http"):
                errors.append("Ollama base_url must be a valid URL (e.g., http://localhost:11434)")
            if not self.llm_config.model:
                errors.append("Ollama model name cannot be empty")

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
    
    def save_to_file(self, config_file: Optional[str] = None):
        """Save current configuration to JSON file"""
        path = Path(config_file) if config_file else self.config_file
        
        config_data = {
            "llm_provider": self.llm_provider.value,
            self.llm_provider.value: self.llm_config.to_dict(),
            "autogen": self.autogen.to_dict(),
            "system": self.system.to_dict(),
            "agents": {name: config.to_dict() for name, config in self.agents.items()},
            "teams": {name: config.to_dict() for name, config in self.teams.items()}
        }
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise IOError(f"Failed to save configuration to {path}: {e}")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "llm_provider": self.llm_provider.value,
            "llm_config": self.llm_config.to_dict(),
            "autogen": self.autogen.to_dict(),
            "system": self.system.to_dict(),
            "agents_count": len(self.agents),
            "teams_count": len(self.teams),
            "autogen_available": AUTOGEN_AVAILABLE,
            "autogen_version": AUTOGEN_VERSION
        }

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_config_manager_instance: Optional[ConfigManager] = None

def get_config_manager(config_file: str = "../config/config.json") -> ConfigManager:
    """
    Get a configured ConfigManager instance.
    
    Args:
        config_file: Path to configuration file.
        
    Returns:
        A ConfigManager instance.
    """
    global _config_manager_instance
    if _config_manager_instance is None or _config_manager_instance.config_file != Path(config_file):
        _config_manager_instance = ConfigManager(config_file)
    return _config_manager_instance


def create_default_config(config_file: str = "../config/config.json"):
    """
    Create a default configuration file.
    
    Args:
        config_file: Path where to save the default configuration.
    """
    default_config = {
        "llm_provider": "deepseek",
        "deepseek": DeepSeekConfig(api_key="your_deepseek_api_key_here").to_dict(),
        "ollama": OllamaConfig().to_dict(),
        "autogen": AutoGenConfig().to_dict(),
        "system": SystemConfig().to_dict(),
        "agents": {
            "project_manager": AgentConfig(
                name="ProjectManager",
                role="project_manager",
                description="Coordinates project workflow, manages stakeholder communication, and ensures project objectives are met.",
                system_message="You are a Project Manager agent responsible for coordinating project activities, managing timelines, and ensuring successful project delivery. Use your knowledge of project management best practices to guide the team.",
                human_input_mode="TERMINATE"
            ).to_dict(),
            "requirements_analyst": AgentConfig(
                name="RequirementsAnalyst",
                role="requirements_analyst",
                description="Gathers, analyzes, and documents project requirements through stakeholder engagement.",
                system_message="You are a Requirements Analyst agent specialized in gathering, analyzing, and documenting project requirements. Focus on creating comprehensive and clear requirements documentation.",
                human_input_mode="ALWAYS"
            ).to_dict(),
            "technical_writer": AgentConfig(
                name="TechnicalWriter",
                role="technical_writer",
                description="Creates and maintains comprehensive technical documentation for projects.",
                system_message="You are a Technical Writer agent responsible for creating clear, comprehensive technical documentation. Focus on structure, clarity, and completeness."
            ).to_dict(),
            "change_detector": AgentConfig(
                name="ChangeDetector",
                role="change_detector",
                description="Monitors and analyzes changes to maintain documentation consistency.",
                system_message="You are a Change Detector agent that monitors project changes and ensures documentation remains up-to-date. Focus on identifying impacts and coordinating updates.",
                reflect_on_tool_use=False,
                max_tool_iterations=1
            ).to_dict()
        },
        "teams": {
            "default": TeamConfig(
                name="DefaultProjectTeam",
                agents=["project_manager", "requirements_analyst", "technical_writer", "change_detector"],
                termination_conditions=AutoGenConfig().termination_conditions
            ).to_dict()
        }
    }
    
    path = Path(config_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        print(f"✅ Default configuration saved to {path}")
    except IOError as e:
        print(f"❌ Failed to save default configuration to {path}: {e}")


def validate_config_file(config_file: str) -> bool:
    """
    Validate a configuration file by attempting to load it.
    
    Args:
        config_file: Path to the configuration file to validate.
        
    Returns:
        True if valid, False otherwise.
    """
    try:
        ConfigManager(config_file)
        print(f"✅ Configuration file '{config_file}' is valid.")
        return True
    except (FileNotFoundError, ValueError, IOError) as e:
        print(f"❌ Configuration file validation failed: {e}")
        return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import sys
    
    print("🔧 Multi-Agent Project Management System - Configuration Manager")
    print("=" * 70)
    
    default_config_path = "../config/config.json"
    
    # Create a default config file if it doesn't exist
    if not Path(default_config_path).exists():
        print(f"'{default_config_path}' not found. Creating a default config file...")
        create_default_config(default_config_path)
        print("\nPlease edit the default configuration file with your settings (e.g., API keys).")
        sys.exit(0)

    # Validate the existing config file
    if not validate_config_file(default_config_path):
        sys.exit(1)
        
    try:
        # Get the config manager instance
        config_manager = get_config_manager(default_config_path)
        
        # Display configuration summary
        summary = config_manager.get_config_summary()
        print("\n📋 Configuration Summary:")
        print(f"  • LLM Provider: {summary['llm_provider']}")
        print(f"  • LLM Config Loaded: {'✅ Yes' if summary['llm_config'] else '❌ No'}")
        print(f"  • AutoGen: {'✅ Available' if summary['autogen_available'] else '❌ Not available'} ({summary['autogen_version']}")
        print(f"  • Agents: {summary['agents_count']}")
        print(f"  • Teams: {summary['teams_count']}")
        
        print("\n✅ Configuration manager initialized successfully!")
        
    except Exception as e:
        print(f"\n❌ Error initializing configuration manager: {e}")
        sys.exit(1)
