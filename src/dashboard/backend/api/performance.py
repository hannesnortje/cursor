#!/usr/bin/env python3
"""
Performance API endpoints for the dashboard
"""

from fastapi import APIRouter, HTTPException

try:
    from ..services.mcp_integration import MCPIntegrationService
except ImportError:
    from services.mcp_integration import MCPIntegrationService

router = APIRouter()
mcp_service = MCPIntegrationService()


@router.get("/metrics")
async def get_performance_metrics():
    """Get performance metrics."""
    try:
        metrics = await mcp_service.get_performance_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache")
async def get_cache_metrics():
    """Get cache performance metrics."""
    try:
        metrics = await mcp_service.get_performance_metrics()
        return {
            "cache_hit_rate": metrics.get("cache_hit_rate", 0),
            "cache_efficiency": (
                "high" if metrics.get("cache_hit_rate", 0) > 80 else "medium"
            ),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/throughput")
async def get_throughput_metrics():
    """Get throughput metrics."""
    try:
        metrics = await mcp_service.get_performance_metrics()
        return {
            "current_throughput": metrics.get("throughput", 0),
            "response_time_avg": metrics.get("response_time_avg", 0),
            "active_agents": metrics.get("active_agents", 0),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
