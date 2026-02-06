"""
Configuration Manager for OpenClaw AI Agent

Handles loading and managing configuration from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import logging


class ConfigManager:
    """Configuration manager for OpenClaw AI Agent"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.getenv("CONFIG_PATH", "/app/config")
        self.config: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
    
    async def load_config(self) -> None:
        """Load configuration from YAML files"""
        try:
            config_file = Path(self.config_path) / "config.yaml"
            
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")
            
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            
            # Override with environment variables
            self._override_with_env()
            
            self.logger.info(f"✅ Configuration loaded from {config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    def _override_with_env(self) -> None:
        """Override configuration with environment variables"""
        env_mappings = {
            "OPENAI_BASE_URL": "llm.base_url",
            "OPENAI_API_KEY": "llm.api_key",
            "MODEL_NAME": "llm.model_name",
            "DISCORD_BOT_TOKEN": "discord.bot.token",
            "GITHUB_TOKEN": "github.api.token",
            "DOCKER_HOST": "docker.host",
            "LOG_LEVEL": "application.log_level",
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                self.set_nested_value(config_key, env_value)
                self.logger.debug(f"✅ Overrode {config_key} with {env_var}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        return self.get_nested_value(key, default)
    
    def set_nested_value(self, key: str, value: Any) -> None:
        """Set nested configuration value using dot notation"""
        keys = key.split('.')
        current = self.config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def get_nested_value(self, key: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation"""
        keys = key.split('.')
        current = self.config
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default
    
    def get_discord_token(self) -> Optional[str]:
        """Get Discord bot token from environment or config"""
        return os.getenv("DISCORD_BOT_TOKEN") or self.get("discord.bot.token")
    
    def get_github_token(self) -> Optional[str]:
        """Get GitHub token from environment or config"""
        return os.getenv("GITHUB_TOKEN") or self.get("github.api.token")
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.get("application.debug", False) or os.getenv("DEBUG", "false").lower() == "true"
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return self.get("llm", {})
    
    def get_docker_config(self) -> Dict[str, Any]:
        """Get Docker configuration"""
        return self.get("docker", {})
    
    def get_discord_config(self) -> Dict[str, Any]:
        """Get Discord configuration"""
        return self.get("discord", {})
    
    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub configuration"""
        return self.get("github", {})
    
    def validate_config(self) -> bool:
        """Validate essential configuration"""
        required_keys = [
            "application.name",
            "llm.base_url",
            "llm.model_name",
        ]
        
        for key in required_keys:
            if not self.get(key):
                self.logger.error(f"❌ Required configuration missing: {key}")
                return False
        
        # Validate Discord token if Discord integration is enabled
        discord_enabled = self.get("discord.enabled", True)
        if discord_enabled and not self.get_discord_token():
            self.logger.error("❌ Discord token required when Discord integration is enabled")
            return False
        
        self.logger.info("✅ Configuration validation passed")
        return True