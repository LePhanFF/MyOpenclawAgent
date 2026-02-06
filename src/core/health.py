"""
Health Check Service for OpenClaw AI Agent

Provides health check endpoints and monitoring for the application.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse


class HealthChecker:
    """Health checker service for OpenClaw"""
    
    def __init__(self, config_manager, llm_client=None):
        self.config_manager = config_manager
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.start_time = datetime.now()
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health"""
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "version": self.config_manager.get("application.version", "1.0.0"),
            "services": {}
        }
        
        # Check vLLM service
        if self.llm_client:
            llm_health = await self.llm_client.health_check()
            health["services"]["vllm"] = llm_health
            
            # Update overall status based on vLLM
            if llm_health.get("status") != "healthy":
                health["status"] = "unhealthy"
        
        # Check configuration
        try:
            config_valid = self.config_manager.validate_config()
            health["services"]["config"] = {
                "status": "healthy" if config_valid else "unhealthy",
                "valid": config_valid
            }
            
            if not config_valid:
                health["status"] = "unhealthy"
                
        except Exception as e:
            health["services"]["config"] = {
                "status": "error",
                "error": str(e)
            }
            health["status"] = "unhealthy"
        
        # Check file system access
        try:
            import os
            test_paths = [
                "/app/logs",
                "/app/github-workspace", 
                "/app/build-cache",
                "/app/data"
            ]
            
            fs_status = []
            for path in test_paths:
                accessible = os.path.exists(path) and os.access(path, os.W_OK)
                fs_status.append(accessible)
            
            health["services"]["filesystem"] = {
                "status": "healthy" if all(fs_status) else "unhealthy",
                "paths": {path: accessible for path, accessible in zip(test_paths, fs_status)}
            }
            
            if not all(fs_status):
                health["status"] = "unhealthy"
                
        except Exception as e:
            health["services"]["filesystem"] = {
                "status": "error",
                "error": str(e)
            }
            health["status"] = "unhealthy"
        
        return health
    
    async def get_simple_health(self) -> Dict[str, Any]:
        """Get simple health status for load balancers"""
        health = await self.get_system_health()
        return {
            "status": health["status"],
            "timestamp": health["timestamp"]
        }


def create_app(config_manager=None, llm_client=None) -> FastAPI:
    """Create FastAPI application for health checks"""
    app = FastAPI(
        title="OpenClaw Health API",
        description="Health check endpoints for OpenClaw AI Agent",
        version="1.0.0"
    )
    
    health_checker = HealthChecker(config_manager, llm_client)
    
    @app.get("/health")
    async def health_check():
        """Simple health check endpoint"""
        try:
            health = await health_checker.get_simple_health()
            status_code = 200 if health["status"] == "healthy" else 503
            return JSONResponse(content=health, status_code=status_code)
        except Exception as e:
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=500
            )
    
    @app.get("/health/detailed")
    async def detailed_health_check():
        """Detailed health check endpoint"""
        try:
            health = await health_checker.get_system_health()
            status_code = 200 if health["status"] == "healthy" else 503
            return JSONResponse(content=health, status_code=status_code)
        except Exception as e:
            return JSONResponse(
                content={"status": "error", "message": str(e)},
                status_code=500
            )
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "OpenClaw AI Agent",
            "status": "running",
            "health_check": "/health",
            "detailed_health": "/health/detailed"
        }
    
    return app