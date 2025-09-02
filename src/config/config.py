"""Configuration management for the enhanced MCP server."""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MCPConfig:
    """MCP server configuration."""
    server_name: str = "enhanced-mcp-server"
    server_version: str = "1.1.0"
    protocol_version: str = "2024-11-05"
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class AgentConfig:
    """Agent system configuration."""
    max_concurrent_agents: int = 5
    agent_timeout: int = 30000
    enable_coordinator: bool = True
    enable_specialized_agents: bool = False
    agent_auto_start: bool = False


@dataclass
class DatabaseConfig:
    """Database configuration."""
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    enable_vector_db: bool = False


@dataclass
class LLMConfig:
    """LLM integration configuration."""
    enable_cursor_llm: bool = True
    enable_docker_ollama: bool = False
    ollama_url: str = "http://localhost:11434"
    default_model: str = "cursor-auto"


@dataclass
class AppConfig:
    """Main application configuration."""
    mcp: MCPConfig = field(default_factory=MCPConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # MCP Configuration
        if os.getenv("MCP_SERVER_NAME"):
            self.mcp.server_name = os.getenv("MCP_SERVER_NAME")
        if os.getenv("MCP_LOG_LEVEL"):
            self.mcp.log_level = os.getenv("MCP_LOG_LEVEL")
        
        # Agent Configuration
        if os.getenv("MAX_CONCURRENT_AGENTS"):
            self.agent.max_concurrent_agents = int(os.getenv("MAX_CONCURRENT_AGENTS"))
        if os.getenv("AGENT_TIMEOUT"):
            self.agent.agent_timeout = int(os.getenv("AGENT_TIMEOUT"))
        if os.getenv("ENABLE_COORDINATOR"):
            self.agent.enable_coordinator = os.getenv("ENABLE_COORDINATOR").lower() == "true"
        
        # Database Configuration
        if os.getenv("QDRANT_URL"):
            self.database.qdrant_url = os.getenv("QDRANT_URL")
        if os.getenv("QDRANT_API_KEY"):
            self.database.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        if os.getenv("ENABLE_VECTOR_DB"):
            self.database.enable_vector_db = os.getenv("ENABLE_VECTOR_DB").lower() == "true"
        
        # LLM Configuration
        if os.getenv("ENABLE_CURSOR_LLM"):
            self.llm.enable_cursor_llm = os.getenv("ENABLE_CURSOR_LLM").lower() == "true"
        if os.getenv("ENABLE_DOCKER_OLLAMA"):
            self.llm.enable_docker_ollama = os.getenv("ENABLE_DOCKER_OLLAMA").lower() == "true"
        if os.getenv("OLLAMA_URL"):
            self.llm.ollama_url = os.getenv("OLLAMA_URL")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "mcp": {
                "server_name": self.mcp.server_name,
                "server_version": self.mcp.server_version,
                "protocol_version": self.mcp.protocol_version,
                "log_level": self.mcp.log_level,
                "log_format": self.mcp.log_format
            },
            "agent": {
                "max_concurrent_agents": self.agent.max_concurrent_agents,
                "agent_timeout": self.agent.agent_timeout,
                "enable_coordinator": self.agent.enable_coordinator,
                "enable_specialized_agents": self.agent.enable_specialized_agents,
                "agent_auto_start": self.agent.agent_auto_start
            },
            "database": {
                "qdrant_url": self.database.qdrant_url,
                "qdrant_api_key": self.database.qdrant_api_key,
                "enable_vector_db": self.database.enable_vector_db
            },
            "llm": {
                "enable_cursor_llm": self.llm.enable_cursor_llm,
                "enable_docker_ollama": self.llm.enable_docker_ollama,
                "ollama_url": self.llm.ollama_url,
                "default_model": self.llm.default_model
            }
        }
    
    def validate(self) -> bool:
        """Validate configuration values."""
        try:
            # Validate agent configuration
            if self.agent.max_concurrent_agents <= 0:
                raise ValueError("max_concurrent_agents must be positive")
            if self.agent.agent_timeout <= 0:
                raise ValueError("agent_timeout must be positive")
            
            # Validate database configuration
            if self.database.enable_vector_db and not self.database.qdrant_url:
                raise ValueError("qdrant_url required when vector db is enabled")
            
            # Validate LLM configuration
            if not self.llm.enable_cursor_llm and not self.llm.enable_docker_ollama:
                raise ValueError("At least one LLM provider must be enabled")
            
            return True
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


def load_config() -> AppConfig:
    """Load and return application configuration."""
    config = AppConfig()
    
    if not config.validate():
        print("Warning: Configuration validation failed, using defaults")
    
    return config


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    if not hasattr(get_config, '_instance'):
        get_config._instance = load_config()
    return get_config._instance
