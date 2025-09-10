#!/usr/bin/env python3
"""
Agents API endpoints for the dashboard
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

try:
    from ..services.mcp_integration import MCPIntegrationService
except ImportError:
    from services.mcp_integration import MCPIntegrationService

router = APIRouter()
mcp_service = MCPIntegrationService()


@router.get("/status", response_model=List[Dict[str, Any]])
async def get_agent_status():
    """Get status of all agents."""
    try:
        agents = await mcp_service.get_agent_status()
        return agents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/status", response_model=Dict[str, Any])
async def get_agent_status_by_id(agent_id: str):
    """Get status of a specific agent."""
    try:
        agents = await mcp_service.get_agent_status()
        for agent in agents:
            if agent["agent_id"] == agent_id:
                return agent

        raise HTTPException(status_code=404, detail="Agent not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=List[str])
async def get_agent_types():
    """Get list of available agent types."""
    try:
        agents = await mcp_service.get_agent_status()
        types = list(set(agent["agent_type"] for agent in agents))
        return types
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/count", response_model=Dict[str, Any])
async def get_agent_count():
    """Get count of agents by status."""
    try:
        agents = await mcp_service.get_agent_status()

        counts = {
            "total": len(agents),
            "operational": len([a for a in agents if a["status"] == "operational"]),
            "degraded": len([a for a in agents if a["status"] == "degraded"]),
            "down": len([a for a in agents if a["status"] == "down"]),
            "limited": len([a for a in agents if a["status"] == "limited"]),
        }

        return counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
