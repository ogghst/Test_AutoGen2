
"""
Configuration settings for the multi-agent project management system
Compatible with AutoGen 0.7.2+ and DeepSeek API
Provides centralized configuration management from a single JSON file.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from autogen_core.models import ModelInfo

# ============================================================================
# ENUMS
# ============================================================================

class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    OLLAMA = "ollama"
    ANTHROPIC = "anthropic"

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# ============================================================================
# CONFIGURATION DATACLASSES
# ============================================================================

@dataclass
class DeepSeekConfig:
    """Configuration for DeepSeek API"""
    api_key: str = "sk-9a4206f76b4a466095d6b85b859c6a85"
    model: str = "deepseek-chat"
    api_url: str = "https://api.deepseek.com/v1/chat/completions"
    model_info: ModelInfo = field(default_factory=lambda: {
                "family": "deepseek",
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True
            })
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["api_key"] = "***REDACTED***"  # Don't expose API key
        return data



@dataclass
class OllamaConfig:
    """Configuration for Ollama"""
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    model_info: ModelInfo = field(default_factory=lambda: {
                "family": "ollama",
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True
            })

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)



@dataclass
class LLMConfig:
    """Unified LLM configuration containing all provider configs"""
    deepseek: DeepSeekConfig
    ollama: OllamaConfig
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "deepseek": self.deepseek.to_dict(),
            "ollama": self.ollama.to_dict()
        }



@dataclass
class LoggingConfig:
    """Configuration for logging system"""
    log_level: str = "INFO"
    console_logging: bool = False
    max_bytes: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RuntimeConfig:
    """Configuration for runtime behavior"""
    max_concurrent_agents: int = 10
    session_timeout: int = 3600  # seconds
    enable_tracing: bool = True
    tracing_endpoint: str = "http://localhost:4317"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SystemConfig:
    """General system configuration"""
    
    # Paths
    knowledge_base_path: str = "../knowledge_base"
    documents_path: str = "../output_documents"
    logs_path: str = "../logs"
    temp_path: str = "../temp"
    config_path: str = "../config"
    data_model_file: str = "../data_model/json/data_model.json"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ServerConfig:
    """Configuration for the web server"""
    host: str = "0.0.0.0"
    port: int = 8000

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ============================================================================
# MAIN CONFIGURATION MANAGER
# ============================================================================

class ConfigManager:
    """Central configuration manager for the multi-agent system"""

    llm_provider: ModelProvider = ModelProvider.OLLAMA
    llm_config: LLMConfig = LLMConfig( deepseek=DeepSeekConfig(), ollama=OllamaConfig())
    system: SystemConfig = SystemConfig()
    logging: LoggingConfig = LoggingConfig()
    runtime: RuntimeConfig = RuntimeConfig()
    server: ServerConfig = ServerConfig()
    
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
        
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def reload_configuration(self):
        """Reload configuration from the JSON file"""
        try:
            self._config_cache = self._load_from_file()
        except (FileNotFoundError, json.JSONDecodeError):
            # Create default configuration if file doesn't exist or is invalid
            self._create_default_config()
            self._config_cache = self._load_from_file()

        # Set LLM provider
        provider_str = self._config_cache.get("llm_provider", "ollama").lower()
        try:
            self.llm_provider = ModelProvider(provider_str)
        except ValueError:
            self.llm_provider = ModelProvider.OLLAMA

        # Load all configurations
        self.llm_config = self._load_llm_config()
        self.system = self._load_system_config()
        self.logging = self._load_logging_config()
        self.runtime = self._load_runtime_config()
        self.server = self._load_server_config()

    def _create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "llm_provider": "ollama",
            "llm_config": {
                "deepseek": DeepSeekConfig(api_key="your-deepseek-api-key-here").to_dict(),
                "ollama": OllamaConfig().to_dict()
            },
            "system": SystemConfig().to_dict(),
            "logging": LoggingConfig().to_dict(),
            "runtime": RuntimeConfig().to_dict(),
            "server": ServerConfig().to_dict(),
        }
        
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)

    def _load_llm_config(self) -> LLMConfig:
        """Load unified LLM configuration containing all providers"""
        llm_config_data = self._config_cache.get("llm_config", {})
        
        # Load DeepSeek config
        deepseek_data = llm_config_data.get("deepseek", {})
        if "api_key" not in deepseek_data:
            deepseek_data["api_key"] = "your-deepseek-api-key-here"
        deepseek_config = DeepSeekConfig(**deepseek_data)
        
        # Load Ollama config
        ollama_data = llm_config_data.get("ollama", {})
        ollama_config = OllamaConfig(**ollama_data)
        
        return LLMConfig(deepseek=deepseek_config, ollama=ollama_config)

    def _load_system_config(self) -> SystemConfig:
        """Load system configuration from file"""
        config_data = self._config_cache.get("system", {})
        return SystemConfig(**config_data)

    def _load_logging_config(self) -> LoggingConfig:
        """Load logging configuration from file"""
        config_data = self._config_cache.get("logging", {})
        return LoggingConfig(**config_data)

    def _load_runtime_config(self) -> RuntimeConfig:
        """Load runtime configuration from file"""
        config_data = self._config_cache.get("runtime", {})
        return RuntimeConfig(**config_data)

    def _load_server_config(self) -> ServerConfig:
        """Load server configuration from file"""
        config_data = self._config_cache.get("server", {})
        return ServerConfig(**config_data)

    def save_to_file(self, config_file: Optional[str] = None):
        """Save current configuration to JSON file"""
        path = Path(config_file) if config_file else self.config_file
        
        config_data = {
            "llm_provider": self.llm_provider.value,
            "llm_config": self.llm_config.to_dict(),
            "system": self.system.to_dict(),
            "logging": self.logging.to_dict(),
            "runtime": self.runtime.to_dict(),
            "server": self.server.to_dict(),
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            "llm_provider": self.llm_provider.value,
            "llm_config": self.llm_config.to_dict(),
            "system": self.system.to_dict(),
            "logging": self.logging.to_dict(),
            "runtime": self.runtime.to_dict(),
            "server": self.server.to_dict(),
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

_config_manager_instance: Optional[ConfigManager] = None

def get_config_manager(config_file: str = "../config/config.json") -> ConfigManager:
    """Get a configured ConfigManager instance."""
    global _config_manager_instance
    if _config_manager_instance is None or _config_manager_instance.config_file != Path(config_file):
        _config_manager_instance = ConfigManager(config_file)
    
    return _config_manager_instance


def create_default_config(config_file: str = "../config/config.json"):
    """Create a default configuration file."""
    default_config = {
        "llm_provider": "ollama",
        "llm_config": {
            "deepseek": DeepSeekConfig(api_key="your-deepseek-api-key-here").to_dict(),
            "ollama": OllamaConfig().to_dict()
        },
        "system": SystemConfig().to_dict(),
        "logging": LoggingConfig().to_dict(),
        "runtime": RuntimeConfig().to_dict(),
        "server": ServerConfig().to_dict(),
    }
    
    path = Path(config_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    print(f"✅ Default configuration saved to {path}")


def validate_config_file(config_file: str) -> bool:
    """Validate a configuration file by attempting to load it."""
    try:
        ConfigManager(config_file)
        print(f"✅ Configuration file '{config_file}' is valid.")
        return True
    except Exception as e:
        print(f"❌ Configuration file validation failed: {e}")
        return False


if __name__ == "__main__":
    # Simple test: create and load configuration
    print("🔧 Testing Configuration System...")
    
    try:
        # Create default config
        create_default_config("test_config.json")
        print("✅ Default configuration created")
        
        # Load and validate
        config_manager = get_config_manager("test_config.json")
        print("✅ Configuration loaded successfully")
        print(f"  • LLM Provider: {config_manager.llm_provider.value}")
        print(f"  • DeepSeek Model: {config_manager.llm_config.deepseek.model}")
        print(f"  • Ollama Model: {config_manager.llm_config.ollama.model}")
        
        # Cleanup
        import os
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
            print("✅ Test file cleaned up")
        
        print("🎉 Configuration system working correctly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
