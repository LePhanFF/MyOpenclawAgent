"""
Discord Bot for OpenClaw AI Agent

Provides Discord integration with slash commands and natural language interface.
"""

import asyncio
import logging
from typing import Optional

import discord
from discord.ext import commands

from src.core.config_manager import ConfigManager


class OpenClawBot:
    """OpenClaw Discord bot"""
    
    def __init__(self, config_manager: ConfigManager, llm_client=None):
        self.config_manager = config_manager
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.bot: Optional[discord.Bot] = None
        self._setup_complete = False
    
    async def initialize(self) -> bool:
        """Initialize Discord bot"""
        try:
            discord_config = self.config_manager.get_discord_config()
            bot_config = discord_config.get("bot", {})
            
            # Get bot token
            token = self.config_manager.get_discord_token()
            if not token:
                self.logger.error("❌ Discord bot token not found")
                return False
            
            # Configure intents (avoid privileged intents)
            intents = discord.Intents.default()
            # Note: message_content requires privileged intent - disabled for now
            # intents.message_content = True
            intents.guilds = True
            
            # Create bot instance
            self.bot = discord.Bot(
                command_prefix=bot_config.get("command_prefix", "/"),
                intents=intents,
                status=discord.Status.online,
                activity=discord.Activity(
                    type=discord.ActivityType.custom,
                    name=bot_config.get("status", "🤖 Building containers...")
                )
            )
            
            # Setup events and commands
            await self._setup_events()
            await self._setup_commands()
            
            self._setup_complete = True
            self.logger.info("✅ Discord bot initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Discord bot: {e}")
            return False
    
    async def _setup_events(self):
        """Setup bot events"""
        
        @self.bot.event
        async def on_ready():
            """Called when bot is ready"""
            self.logger.info(f"✅ Bot logged in as {self.bot.user}")
            self.logger.info(f"📊 Connected to {len(self.bot.guilds)} guilds")
            
            # Log registered commands before sync
            cmd_count = len(self.bot.application_commands)
            self.logger.info(f"📋 Commands registered: {cmd_count}")
            for cmd in self.bot.application_commands:
                self.logger.info(f"  - /{cmd.name}: {cmd.description}")
            
            # Sync commands
            try:
                await self.bot.sync_commands()
                self.logger.info("✅ Commands synced successfully")
                # Verify commands are accessible
                for guild in self.bot.guilds:
                    try:
                        cmds = await self.bot.fetch_commands(guild_id=guild.id)
                        self.logger.info(f"📋 Commands in {guild.name}: {len(cmds)}")
                        for cmd in cmds:
                            self.logger.info(f"  - /{cmd.name}")
                    except Exception as e:
                        self.logger.error(f"❌ Failed to fetch commands for {guild.name}: {e}")
            except Exception as e:
                self.logger.error(f"❌ Failed to sync commands: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        
        @self.bot.event
        async def on_guild_join(guild):
            """Called when bot joins a new guild"""
            self.logger.info(f"🎉 Joined new guild: {guild.name} (ID: {guild.id})")
        
        @self.bot.event
        async def on_error(event, *args, **kwargs):
            """Handle bot errors"""
            self.logger.error(f"❌ Bot error in event {event}: {args} {kwargs}")
    
    async def _setup_commands(self):
        """Setup slash commands"""

        @self.bot.slash_command(name="ping", description="Check bot latency")
        async def ping(ctx: discord.ApplicationContext):
            """Simple ping command"""
            latency = round(self.bot.latency * 1000)
            await ctx.respond(f"Pong! Latency: {latency}ms")

        @self.bot.slash_command(name="status", description="Check OpenClaw system status")
        async def status(ctx: discord.ApplicationContext):
            """Check system status"""
            try:
                embed = discord.Embed(
                    title="🤖 OpenClaw Status",
                    color=discord.Color.green()
                )

                # Check vLLM status
                if self.llm_client:
                    vllm_health = await self.llm_client.health_check()
                    vllm_status = "✅ Healthy" if vllm_health.get("status") == "healthy" else "❌ Unhealthy"
                    embed.add_field(
                        name="🧠 vLLM Service",
                        value=vllm_status,
                        inline=True
                    )

                    if vllm_health.get("models_available"):
                        embed.add_field(
                            name="📊 Available Models",
                            value=str(vllm_health["models_available"]),
                            inline=True
                        )

                embed.add_field(
                    name="🔧 Version",
                    value=self.config_manager.get("application.version", "1.0.0"),
                    inline=True
                )

                await ctx.respond(embed=embed)

            except Exception as e:
                self.logger.error(f"❌ Status command error: {e}")
                await ctx.respond("❌ Failed to get system status", ephemeral=True)

        @self.bot.slash_command(name="chat", description="Chat with OpenClaw AI")
        async def chat(
            ctx: discord.ApplicationContext,
            message: discord.Option(str, description="Your message to OpenClaw")
        ):
            """Chat with AI"""
            try:
                if not self.llm_client:
                    await ctx.respond("❌ LLM service not available", ephemeral=True)
                    return

                # Send typing indicator
                await ctx.defer()
                self.logger.info(f"💬 Chat command received: {message[:50]}...")

                # Get AI response with timeout
                import asyncio
                try:
                    response = await asyncio.wait_for(
                        self.llm_client.chat(message, max_tokens=500),
                        timeout=30.0
                    )
                    self.logger.info(f"✅ Got response: {response[:100] if response else 'None'}...")
                except asyncio.TimeoutError:
                    self.logger.error("❌ vLLM response timeout")
                    await ctx.respond("❌ Request timed out. The AI is taking too long to respond.", ephemeral=True)
                    return

                if response:
                    # Clean up response - remove thinking tags if present
                    clean_response = response
                    if '<think>' in clean_response:
                        # Extract content after thinking
                        parts = clean_response.split('</think>')
                        if len(parts) > 1:
                            clean_response = parts[-1].strip()
                        else:
                            # Remove think tags entirely
                            clean_response = clean_response.replace('<think>', '').strip()
                    
                    # Ensure response isn't empty after cleaning
                    if not clean_response or len(clean_response) < 10:
                        clean_response = response  # Use original if cleaning went wrong
                    
                    self.logger.info(f"📤 Sending response to Discord: {clean_response[:100]}...")
                    
                    # Create embed for response
                    embed = discord.Embed(
                        title="🤖 OpenClaw Response",
                        description=clean_response[:2000],  # Discord limit
                        color=discord.Color.blue()
                    )
                    embed.add_field(
                        name="💭 Your Message",
                        value=message[:1024],
                        inline=False
                    )

                    await ctx.respond(embed=embed)
                    self.logger.info("✅ Response sent to Discord successfully")
                else:
                    await ctx.respond("❌ Failed to get AI response", ephemeral=True)

            except Exception as e:
                self.logger.error(f"❌ Chat command error: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                await ctx.respond(f"❌ An error occurred: {str(e)[:100]}", ephemeral=True)

        self.logger.info("✅ Discord commands setup completed")
    
    async def start(self):
        """Start the Discord bot"""
        if not self._setup_complete:
            if not await self.initialize():
                raise RuntimeError("Failed to initialize Discord bot")
        
        token = self.config_manager.get_discord_token()
        if not token:
            raise ValueError("Discord bot token not available")
        
        self.logger.info("🚀 Starting Discord bot...")
        await self.bot.start(token)
    
    async def cleanup(self):
        """Cleanup Discord bot"""
        if self.bot:
            await self.bot.close()
            self.logger.info("✅ Discord bot cleaned up")
    
    def get_bot_instance(self) -> Optional[discord.Bot]:
        """Get the Discord bot instance"""
        return self.bot