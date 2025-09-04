#!/usr/bin/env python3
"""
System API endpoints for the dashboard
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

try:
    from ..services.mcp_integration import MCPIntegrationService
except ImportError:
    from services.mcp_integration import MCPIntegrationService

router = APIRouter()
mcp_service = MCPIntegrationService()


@router.get("/health")
async def get_system_health():
    """Get system health information."""
    try:
        health = await mcp_service.get_system_health()
        return health
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status():
    """Get overall system status."""
    try:
        health = await mcp_service.get_system_health()
        mcp_status = mcp_service.get_mcp_status()
        
        return {
            "system_health": health,
            "mcp_status": mcp_status,
            "dashboard_status": "operational"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_system_info():
    """Get system information."""
    return {
        "system": "AI Agent System",
        "version": "1.0.0",
        "dashboard_port": 5000,
        "mcp_server_port": 5007,
        "websocket_port": 4000,
        "architecture": "Microservices with MCP integration"
    }
