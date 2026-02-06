"""
Test configuration and utilities for pytest
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Mock configuration for testing"""
    return {
        "application": {
            "name": "OpenClaw AI Agent",
            "version": "1.0.0",
            "debug": True,
            "log_level": "DEBUG"
        },
        "llm": {
            "base_url": "http://localhost:8001/v1",
            "model_name": "/model",
            "api_key": "sk-dummy",
            "max_tokens": 1000,
            "temperature": 0.7
        },
        "docker": {
            "host": "tcp://dind:2376",
            "tls_verify": True,
            "cert_path": "/certs/client",
            "default_registry": "docker.io",
            "build_timeout": 300
        },
        "discord": {
            "bot": {
                "token": "mock_discord_token",
                "command_prefix": "/",
                "status": "Testing"
            },
            "commands": {
                "enabled": ["ping", "status", "chat"]
            },
            "chat": {
                "enabled": True,
                "context_length": 10
            }
        },
        "github": {
            "api": {
                "token": "mock_github_token",
                "base_url": "https://api.github.com"
            }
        },
        "workspace": {
            "mount_path": "/workspace",
            "github_workspace": "/app/github-workspace",
            "build_cache": "/app/build-cache",
            "log_path": "/app/logs"
        }
    }


@pytest.fixture
def mock_config_manager(mock_config):
    """Mock ConfigManager instance"""
    from src.core.config_manager import ConfigManager
    
    config_manager = MagicMock(spec=ConfigManager)
    config_manager.config = mock_config
    config_manager.get.side_effect = lambda key, default=None: mock_config.get(key, default)
    config_manager.get_nested_value.side_effect = lambda key, default=None: mock_config.get(key, default)
    config_manager.get_discord_token.return_value = mock_config["discord"]["bot"]["token"]
    config_manager.get_github_token.return_value = mock_config["github"]["api"]["token"]
    config_manager.get_llm_config.return_value = mock_config["llm"]
    config_manager.get_docker_config.return_value = mock_config["docker"]
    config_manager.get_discord_config.return_value = mock_config["discord"]
    config_manager.get_github_config.return_value = mock_config["github"]
    config_manager.validate_config.return_value = True
    
    return config_manager


@pytest.fixture
def mock_llm_client():
    """Mock VLLMClient instance"""
    from src.core.llm_client import VLLMClient
    
    client = AsyncMock(spec=VLLMClient)
    client.initialize.return_value = None
    client.test_connection.return_value = True
    client.get_completion.return_value = "Mock AI response"
    client.chat.return_value = "Mock AI response"
    client.get_available_models.return_value = ["/model"]
    client.health_check.return_value = {
        "status": "healthy",
        "models_available": 1,
        "current_model": "/model",
        "base_url": "http://localhost:8001/v1",
        "test_response": "OK"
    }
    client.cleanup.return_value = None
    
    return client


@pytest.fixture
def mock_discord_bot():
    """Mock Discord bot instance"""
    bot = MagicMock()
    bot.user = MagicMock()
    bot.user.name = "TestBot"
    bot.latency = 0.1
    bot.guilds = []
    bot.sync_commands = AsyncMock()
    
    return bot


@pytest.fixture
def temp_dirs(tmp_path):
    """Create temporary directories for testing"""
    dirs = {
        "logs": tmp_path / "logs",
        "github_workspace": tmp_path / "github-workspace",
        "build_cache": tmp_path / "build-cache",
        "data": tmp_path / "data"
    }
    
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True)
    
    return dirs


# Async test decorator for pytest-asyncio compatibility
def async_test(func):
    """Decorator to mark async test functions"""
    return pytest.mark.asyncio(func)