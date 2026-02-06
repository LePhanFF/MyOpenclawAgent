"""
Test VLLM Client functionality
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp

from src.core.llm_client import VLLMClient, ChatMessage


class TestVLLMClient:
    """Test VLLMClient class"""
    
    @pytest.mark.asyncio
    async def test_initialize(self, mock_config_manager):
        """Test VLLM client initialization"""
        client = VLLMClient(mock_config_manager)
        
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = AsyncMock()
            mock_session_class.return_value = mock_session
            
            await client.initialize()
            
            assert client.base_url == "http://localhost:8001/v1"
            assert client.model_name == "/model"
            assert client.api_key == "sk-dummy"
            assert client.max_tokens == 1000
            assert client.temperature == 0.7
            assert client.session is mock_session
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, mock_config_manager):
        """Test successful vLLM connection"""
        client = VLLMClient(mock_config_manager)
        client.session = AsyncMock()
        client.base_url = "http://localhost:8001/v1"
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "data": [{"id": "/model", "object": "model"}]
        }
        client.session.get.return_value.__aenter__.return_value = mock_response
        
        result = await client.test_connection()
        
        assert result is True
        client.session.get.assert_called_once_with("http://localhost:8001/v1/models")
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, mock_config_manager):
        """Test failed vLLM connection"""
        client = VLLMClient(mock_config_manager)
        client.session = AsyncMock()
        client.base_url = "http://localhost:8001/v1"
        
        # Mock failed response
        mock_response = AsyncMock()
        mock_response.status = 500
        client.session.get.return_value.__aenter__.return_value = mock_response
        
        result = await client.test_connection()
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_completion_success(self, mock_config_manager):
        """Test successful completion request"""
        client = VLLMClient(mock_config_manager)
        client.session = AsyncMock()
        client.base_url = "http://localhost:8001/v1"
        client.model_name = "/model"
        client.max_tokens = 1000
        client.temperature = 0.7
        client.api_key = "sk-dummy"
        
        messages = [ChatMessage(role="user", content="Hello")]
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello! How can I help you?"}}]
        }
        client.session.post.return_value.__aenter__.return_value = mock_response
        
        result = await client.get_completion(messages)
        
        assert result == "Hello! How can I help you?"
        
        # Verify request data
        call_args = client.session.post.call_args[1]
        json_data = call_args["json"]
        
        assert json_data["model"] == "/model"
        assert json_data["messages"][0]["role"] == "user"
        assert json_data["messages"][0]["content"] == "Hello"
        assert json_data["max_tokens"] == 1000
        assert json_data["temperature"] == 0.7
    
    @pytest.mark.asyncio
    async def test_chat_success(self, mock_config_manager):
        """Test chat interface"""
        client = VLLMClient(mock_config_manager)
        client.get_completion = AsyncMock(return_value="Chat response")
        
        result = await client.chat("Hello")
        
        assert result == "Chat response"
        client.get_completion.assert_called_once()
        
        # Verify messages
        call_args = client.get_completion.call_args[0][0]
        messages = call_args
        assert len(messages) == 2  # system + user
        assert messages[0].role == "system"
        assert messages[1].role == "user"
        assert messages[1].content == "Hello"
    
    @pytest.mark.asyncio
    async def test_get_available_models(self, mock_config_manager):
        """Test getting available models"""
        client = VLLMClient(mock_config_manager)
        client.session = AsyncMock()
        client.base_url = "http://localhost:8001/v1"
        
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "/model"},
                {"id": "gpt-3.5-turbo"},
                {"id": ""}
            ]
        }
        client.session.get.return_value.__aenter__.return_value = mock_response
        
        models = await client.get_available_models()
        
        assert len(models) == 2  # Should filter out empty string
        assert "/model" in models
        assert "gpt-3.5-turbo" in models
    
    @pytest.mark.asyncio
    async def test_health_check(self, mock_config_manager):
        """Test health check functionality"""
        client = VLLMClient(mock_config_manager)
        client.model_name = "/model"
        client.base_url = "http://localhost:8001/v1"
        
        # Mock dependencies
        client.get_available_models = AsyncMock(return_value=["/model"])
        client.chat = AsyncMock(return_value="OK")
        
        result = await client.health_check()
        
        assert result["status"] == "healthy"
        assert result["models_available"] == 1
        assert result["current_model"] == "/model"
        assert result["base_url"] == "http://localhost:8001/v1"
        assert result["test_response"] == "OK"
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, mock_config_manager):
        """Test health check when unhealthy"""
        client = VLLMClient(mock_config_manager)
        client.model_name = "/model"
        client.base_url = "http://localhost:8001/v1"
        
        # Mock failed test response
        client.get_available_models = AsyncMock(return_value=["/model"])
        client.chat = AsyncMock(return_value=None)
        
        result = await client.health_check()
        
        assert result["status"] == "unhealthy"
        assert result["test_response"] is None
    
    @pytest.mark.asyncio
    async def test_cleanup(self, mock_config_manager):
        """Test cleanup functionality"""
        client = VLLMClient(mock_config_manager)
        client.session = AsyncMock()
        
        await client.cleanup()
        
        client.session.close.assert_called_once()
    
    def test_chat_message_creation(self):
        """Test ChatMessage dataclass"""
        message = ChatMessage(role="user", content="Hello world")
        
        assert message.role == "user"
        assert message.content == "Hello world"