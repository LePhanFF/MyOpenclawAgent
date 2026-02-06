"""
OpenClaw AI Agent - Main Application Entry Point

This is the main entry point for the OpenClaw AI Agent, which provides
Discord bot integration, GitHub automation, Docker-in-Docker capabilities,
and vLLM integration for AI-powered assistance.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config_manager import ConfigManager
from src.core.llm_client import VLLMClient
from src.core.health import HealthChecker
from src.discord.bot import OpenClawBot


class OpenClawAgent:
    """Main OpenClaw AI Agent application"""
    
    def __init__(self):
        self.config_manager: Optional[ConfigManager] = None
        self.llm_client: Optional[VLLMClient] = None
        self.health_checker: Optional[HealthChecker] = None
        self.discord_bot: Optional[OpenClawBot] = None
        self.logger = logging.getLogger(__name__)
    
    async def initialize(self) -> bool:
        """Initialize the OpenClaw agent and all its components"""
        try:
            self.logger.info("🚀 Initializing OpenClaw AI Agent...")
            
            # Load environment variables
            self._load_environment()
            
            # Load configuration
            self.config_manager = ConfigManager()
            await self.config_manager.load_config()
            
            # Initialize logging
            self._setup_logging()
            
            # Initialize vLLM client
            self.llm_client = VLLMClient(self.config_manager)
            await self.llm_client.initialize()
            
            # Test vLLM connectivity
            if await self.llm_client.test_connection():
                self.logger.info("✅ vLLM client initialized successfully")
            else:
                self.logger.warning("⚠️ vLLM client initialized but connection test failed")
            
            # Initialize health checker
            self.health_checker = HealthChecker(self.config_manager, self.llm_client)
            
            # Initialize Discord bot
            self.discord_bot = OpenClawBot(
                config_manager=self.config_manager,
                llm_client=self.llm_client
            )
            
            self.logger.info("✅ OpenClaw AI Agent initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize OpenClaw: {e}")
            return False
    
    def _load_environment(self):
        """Load environment variables from .env file"""
        env_path = Path(__file__).parent.parent.parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            self.logger.info("✅ Environment variables loaded")
        else:
            self.logger.info("ℹ️ No .env file found, using environment variables only")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config_manager.get("application.log_level", "INFO")
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/logs/openclaw.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger.info(f"✅ Logging initialized with level: {log_level}")
    
    async def run(self) -> None:
        """Run the OpenClaw agent"""
        if not await self.initialize():
            self.logger.error("❌ Failed to initialize, exiting...")
            return
        
        try:
            self.logger.info("🤖 Starting OpenClaw AI Agent...")
            
            # Start Discord bot
            if self.discord_bot:
                await self.discord_bot.start()
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"❌ Unexpected error during execution: {e}")
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        self.logger.info("🧹 Cleaning up resources...")
        
        if self.discord_bot:
            await self.discord_bot.cleanup()
        
        if self.llm_client:
            await self.llm_client.cleanup()
        
        self.logger.info("✅ Cleanup completed")


async def main():
    """Main entry point"""
    agent = OpenClawAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())