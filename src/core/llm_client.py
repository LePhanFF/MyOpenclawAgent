"""
vLLM Client for OpenClaw AI Agent

Handles communication with vLLM server for AI-powered responses.
"""

import asyncio
import logging
import aiohttp
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str
    content: str


class VLLMClient:
    """Client for interacting with vLLM server"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url: str = ""
        self.model_name: str = ""
        self.api_key: str = ""
        self.max_tokens: int = 4000
        self.temperature: float = 0.7
    
    async def initialize(self) -> None:
        """Initialize the vLLM client"""
        try:
            llm_config = self.config_manager.get_llm_config()
            
            self.base_url = llm_config.get("base_url", "http://host.docker.internal:8001/v1")
            self.model_name = llm_config.get("model_name", "/model")
            self.api_key = llm_config.get("api_key", "sk-dummy")
            self.max_tokens = llm_config.get("max_tokens", 4000)
            self.temperature = llm_config.get("temperature", 0.7)
            
            # Create HTTP session
            self.session = aiohttp.ClientSession(
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            self.logger.info(f"✅ vLLM client initialized: {self.base_url}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize vLLM client: {e}")
            raise
    
    async def test_connection(self) -> bool:
        """Test connection to vLLM server"""
        try:
            if not self.session:
                raise RuntimeError("Client not initialized")
            
            # Test models endpoint
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    models = await response.json()
                    self.logger.info(f"✅ vLLM server accessible. Available models: {len(models.get('data', []))}")
                    return True
                else:
                    self.logger.error(f"❌ vLLM server returned status {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ vLLM connection test failed: {e}")
            return False
    
    async def get_completion(self, messages: List[ChatMessage], **kwargs) -> Optional[str]:
        """Get completion from vLLM"""
        try:
            if not self.session:
                raise RuntimeError("Client not initialized")
            
            # Prepare request
            request_data = {
                "model": self.model_name,
                "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
            
            # Add optional parameters
            if "stream" in kwargs:
                request_data["stream"] = kwargs["stream"]
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=request_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    self.logger.debug(f"✅ Received completion ({len(content)} chars)")
                    return content
                else:
                    error_text = await response.text()
                    self.logger.error(f"❌ vLLM API error {response.status}: {error_text}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to get completion: {e}")
            return None
    
    async def chat(self, user_message: str, system_message: Optional[str] = None, **kwargs) -> Optional[str]:
        """Simple chat interface"""
        messages = []
        
        if system_message:
            messages.append(ChatMessage(role="system", content=system_message))
        else:
            messages.append(ChatMessage(
                role="system", 
                content="You are OpenClaw, an AI DevOps assistant. You help with Docker, GitHub, and development tasks using clear, actionable responses."
            ))
        
        messages.append(ChatMessage(role="user", content=user_message))
        
        return await self.get_completion(messages, **kwargs)
    
    async def get_available_models(self) -> List[str]:
        """Get list of available models from vLLM"""
        try:
            if not self.session:
                raise RuntimeError("Client not initialized")
            
            async with self.session.get(f"{self.base_url}/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [model.get("id", "") for model in data.get("data", [])]
                    return [model for model in models if model]  # Filter out empty strings
                else:
                    self.logger.error(f"❌ Failed to get models: {response.status}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"❌ Error getting models: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on vLLM service"""
        try:
            if not self.session:
                return {"status": "error", "message": "Client not initialized"}
            
            # Test basic connectivity
            models = await self.get_available_models()
            
            # Test actual completion
            test_response = await self.chat("Say 'OK' if you can hear me.", max_tokens=10)
            
            return {
                "status": "healthy" if test_response else "unhealthy",
                "models_available": len(models),
                "current_model": self.model_name,
                "base_url": self.base_url,
                "test_response": test_response
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            self.logger.info("✅ vLLM client cleaned up")