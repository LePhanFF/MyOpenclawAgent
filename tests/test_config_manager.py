"""
Test Configuration Manager functionality
"""

import pytest
import os
import tempfile
from pathlib import Path

from src.core.config_manager import ConfigManager


class TestConfigManager:
    """Test ConfigManager class"""
    
    def test_init_with_default_path(self):
        """Test initialization with default path"""
        with patch.dict(os.environ, {'CONFIG_PATH': '/test/config'}):
            config_manager = ConfigManager()
            assert config_manager.config_path == '/test/config'
    
    def test_init_with_custom_path(self):
        """Test initialization with custom path"""
        config_manager = ConfigManager('/custom/path')
        assert config_manager.config_path == '/custom/path'
    
    @pytest.mark.asyncio
    async def test_load_config_success(self, tmp_path):
        """Test successful config loading"""
        # Create test config file
        config_content = """
application:
  name: "Test App"
  version: "1.0.0"

llm:
  base_url: "http://localhost:8001/v1"
  model_name: "/model"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(config_content)
        
        config_manager = ConfigManager(str(tmp_path))
        await config_manager.load_config()
        
        assert config_manager.get("application.name") == "Test App"
        assert config_manager.get("application.version") == "1.0.0"
        assert config_manager.get("llm.base_url") == "http://localhost:8001/v1"
        assert config_manager.get("llm.model_name") == "/model"
    
    @pytest.mark.asyncio
    async def test_load_config_file_not_found(self):
        """Test config loading with missing file"""
        config_manager = ConfigManager("/nonexistent/path")
        
        with pytest.raises(FileNotFoundError):
            await config_manager.load_config()
    
    def test_get_nested_value(self, mock_config):
        """Test getting nested configuration values"""
        config_manager = ConfigManager()
        config_manager.config = mock_config
        
        assert config_manager.get_nested_value("application.name") == "OpenClaw AI Agent"
        assert config_manager.get_nested_value("llm.base_url") == "http://localhost:8001/v1"
        assert config_manager.get_nested_value("nonexistent.key") is None
        assert config_manager.get_nested_value("nonexistent.key", "default") == "default"
    
    def test_set_nested_value(self):
        """Test setting nested configuration values"""
        config_manager = ConfigManager()
        config_manager.config = {}
        
        config_manager.set_nested_value("app.name", "Test App")
        assert config_manager.get_nested_value("app.name") == "Test App"
        
        config_manager.set_nested_value("app.version", "1.0.0")
        assert config_manager.get_nested_value("app.version") == "1.0.0"
        
        # Test setting deeper nested value
        config_manager.set_nested_value("services.database.host", "localhost")
        assert config_manager.get_nested_value("services.database.host") == "localhost"
    
    def test_get_method(self, mock_config):
        """Test get method"""
        config_manager = ConfigManager()
        config_manager.config = mock_config
        
        assert config_manager.get("application.name") == "OpenClaw AI Agent"
        assert config_manager.get("nonexistent", "default") == "default"
    
    def test_override_with_env(self):
        """Test environment variable overrides"""
        config_manager = ConfigManager()
        config_manager.config = {
            "llm": {
                "base_url": "original_url",
                "api_key": "original_key"
            },
            "application": {
                "log_level": "INFO"
            }
        }
        
        with patch.dict(os.environ, {
            'OPENAI_BASE_URL': 'http://override:8001/v1',
            'MODEL_NAME': 'override_model'
        }):
            config_manager._override_with_env()
        
        assert config_manager.get("llm.base_url") == "http://override:8001/v1"
        assert config_manager.get("llm.api_key") == "original_key"  # Not overridden
        # The MODEL_NAME should be set during override
        assert config_manager.get("llm.model_name") == "override_model"
    
    def test_get_discord_token_from_env(self):
        """Test getting Discord token from environment"""
        config_manager = ConfigManager()
        config_manager.config = {"discord": {"bot": {"token": "config_token"}}}
        
        with patch.dict(os.environ, {'DISCORD_BOT_TOKEN': 'env_token'}):
            token = config_manager.get_discord_token()
            assert token == 'env_token'
    
    def test_get_discord_token_from_config(self):
        """Test getting Discord token from config"""
        config_manager = ConfigManager()
        config_manager.config = {"discord": {"bot": {"token": "config_token"}}}
        
        token = config_manager.get_discord_token()
        assert token == 'config_token'
    
    def test_get_github_token_from_env(self):
        """Test getting GitHub token from environment"""
        config_manager = ConfigManager()
        config_manager.config = {"github": {"api": {"token": "config_token"}}}
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'env_token'}):
            token = config_manager.get_github_token()
            assert token == 'env_token'
    
    def test_is_debug_enabled_true(self):
        """Test debug enabled from config"""
        config_manager = ConfigManager()
        config_manager.config = {"application": {"debug": True}}
        
        assert config_manager.is_debug_enabled() is True
    
    def test_is_debug_enabled_false(self):
        """Test debug disabled from config"""
        config_manager = ConfigManager()
        config_manager.config = {"application": {"debug": False}}
        
        assert config_manager.is_debug_enabled() is False
    
    def test_is_debug_enabled_from_env(self):
        """Test debug enabled from environment"""
        config_manager = ConfigManager()
        config_manager.config = {"application": {"debug": False}}
        
        with patch.dict(os.environ, {'DEBUG': 'true'}):
            assert config_manager.is_debug_enabled() is True
    
    def test_get_llm_config(self, mock_config):
        """Test getting LLM configuration"""
        config_manager = ConfigManager()
        config_manager.config = mock_config
        
        llm_config = config_manager.get_llm_config()
        assert llm_config == mock_config["llm"]
    
    def test_validate_config_success(self, mock_config):
        """Test successful configuration validation"""
        config_manager = ConfigManager()
        config_manager.config = mock_config
        
        assert config_manager.validate_config() is True
    
    def test_validate_config_missing_required(self):
        """Test configuration validation with missing required keys"""
        config_manager = ConfigManager()
        config_manager.config = {
            "application": {"name": "Test"},
            # Missing llm.base_url and llm.model_name
        }
        
        assert config_manager.validate_config() is False
    
    def test_validate_config_discord_token_missing(self):
        """Test validation when Discord token is missing"""
        config_manager = ConfigManager()
        config_manager.config = {
            "application": {"name": "Test"},
            "llm": {"base_url": "http://localhost:8001/v1", "model_name": "/model"},
            "discord": {"enabled": True}
        }
        
        # Mock get_discord_token to return None
        config_manager.get_discord_token = lambda: None
        
        assert config_manager.validate_config() is False