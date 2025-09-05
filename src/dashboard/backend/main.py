#!/usr/bin/env python3
"""
Dashboard Backend - FastAPI Application
Provides real-time monitoring and visualization for the AI Agent System
"""

import logging
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import will be handled when running as module
try:
    from .api import agents, system, performance, websocket
    from .models.dashboard import DashboardStatus
    from .services.mcp_integration import MCPIntegrationService
    from .services.advanced_lit_manager import advanced_lit_manager
except ImportError:
    # For direct execution, import from current directory
    from api import agents, system, performance, websocket
    from models.dashboard import DashboardStatus
    from services.mcp_integration import MCPIntegrationService
    from services.advanced_lit_manager import advanced_lit_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Agent System Dashboard",
    description="Real-time monitoring and visualization dashboard for the AI Agent "
                "System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP integration service (will be set up in startup event)
mcp_service = None

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Mount current Lit 3 files
app.mount("/static/lib/lit", StaticFiles(directory="../frontend/lib/lit/current"), name="lit_current")

# Include API routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(websocket.router, prefix="/api/websocket", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup."""
    logger.info("🚀 Dashboard Backend starting up...")
    
    # Initialize Advanced Lit 3 manager
    try:
        logger.info("📦 Initializing Advanced Lit 3 manager...")
        success = await advanced_lit_manager.ensure_lit_available()
        if success:
            info = advanced_lit_manager.get_lit_info()
            logger.info(f"✅ Lit 3 ready: {info['size']} bytes, version: {info['version']}")
            
            # Start background tasks
            await advanced_lit_manager.start_background_tasks()
            logger.info("🚀 Started background tasks for automatic updates and health checks")
        else:
            logger.warning("⚠️ Lit 3 initialization failed, will use CDN fallback")
    except Exception as e:
        logger.warning(f"⚠️ Advanced Lit 3 manager initialization failed: {e}")
        logger.info("Dashboard will use CDN fallback for Lit 3")
    
    # Initialize MCP integration service
    global mcp_service
    try:
        # Get instance ID from environment
        instance_id = os.environ.get('MCP_INSTANCE_ID')
        if instance_id:
            mcp_service = MCPIntegrationService(instance_id)
            await mcp_service.initialize()
            logger.info(f"✅ MCP integration service initialized for instance {instance_id}")
        else:
            mcp_service = MCPIntegrationService()
            await mcp_service.initialize()
            logger.info("✅ MCP integration service initialized (no specific instance)")
    except Exception as e:
        logger.warning(f"⚠️ MCP integration service initialization failed: {e}")
        logger.info("Dashboard will run with limited functionality")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Dashboard Backend shutting down...")
    
    # Stop background tasks
    try:
        await advanced_lit_manager.stop_background_tasks()
        logger.info("✅ Advanced Lit 3 manager background tasks stopped")
    except Exception as e:
        logger.warning(f"⚠️ Failed to stop Lit manager background tasks: {e}")
    
    await mcp_service.cleanup()

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Serve the main dashboard page."""
    try:
        # Read the component-based HTML file
        with open("../frontend/index.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to simple HTML if file not found
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Agent System Dashboard</title>
        </head>
        <body>
            <h1>Dashboard Frontend Not Found</h1>
            <p>Please check the frontend files in src/dashboard/frontend/</p>
        </body>
        </html>
        """


@app.get("/test", response_class=HTMLResponse)
async def dashboard_test():
    """Serve the test dashboard page."""
    try:
        # Read the test HTML file
        with open("../frontend/test-simple.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Test Page Not Found</h1>
            <p>Test file not found</p>
        </body>
        </html>
        """

@app.get("/api/status")
async def get_dashboard_status() -> DashboardStatus:
    """Get overall dashboard status."""
    return DashboardStatus(
        status="operational",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        mcp_connected=mcp_service.is_connected(),
        services={
            "dashboard_backend": "operational",
            "mcp_integration": "operational" if mcp_service.is_connected() else "limited",
            "websocket": "operational",
            "api_endpoints": "operational"
        }
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "dashboard_backend",
        "port": 5000
    }

@app.get("/api/lit/info")
async def get_lit_info():
    """Get comprehensive Lit 3 library information."""
    try:
        info = advanced_lit_manager.get_lit_info()
        return {
            "status": "success",
            "lit_info": info,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get Lit info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Lit information")

@app.get("/api/lit/download")
async def download_lit():
    """Force download/update of Lit 3 library."""
    try:
        success = await advanced_lit_manager.force_update()
        if success:
            info = advanced_lit_manager.get_lit_info()
            return {
                "status": "success",
                "message": "Lit 3 library updated successfully",
                "lit_info": info,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to download Lit 3 library")
    except Exception as e:
        logger.error(f"Failed to download Lit: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download Lit: {str(e)}")

@app.get("/api/lit/versions")
async def get_available_versions():
    """Get list of available Lit 3 versions."""
    try:
        versions = advanced_lit_manager.get_available_versions()
        return {
            "status": "success",
            "versions": versions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get available versions")

@app.post("/api/lit/rollback/{version}")
async def rollback_to_version(version: str):
    """Rollback to a specific Lit 3 version."""
    try:
        success = await advanced_lit_manager.rollback_to_version(version)
        if success:
            info = advanced_lit_manager.get_lit_info()
            return {
                "status": "success",
                "message": f"Successfully rolled back to version {version}",
                "lit_info": info,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to rollback to version {version}")
    except Exception as e:
        logger.error(f"Failed to rollback to version {version}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rollback: {str(e)}")

@app.get("/api/lit/health")
async def get_lit_health():
    """Get Lit 3 system health and metrics."""
    try:
        info = advanced_lit_manager.get_lit_info()
        health_status = {
            "status": "healthy" if info["available"] else "unhealthy",
            "current_version": info.get("version", "unknown"),
            "uptime_seconds": info.get("uptime", 0),
            "cdn_sources_healthy": sum(1 for source in info.get("cdn_sources", []) if source["healthy"]),
            "total_cdn_sources": len(info.get("cdn_sources", [])),
            "metrics": info.get("metrics", {}),
            "recent_events": info.get("recent_events", []),
            "timestamp": datetime.now().isoformat()
        }
        return health_status
    except Exception as e:
        logger.error(f"Failed to get health status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get health status")

if __name__ == "__main__":
    import argparse
    import os
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Agent System Dashboard Backend")
    parser.add_argument("--port", type=int, default=5000, help="Port to run the dashboard on")
    parser.add_argument("--instance-id", type=str, help="MCP instance ID this dashboard belongs to")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    
    args = parser.parse_args()
    
    # Get port from environment or arguments
    port = int(os.environ.get('DASHBOARD_PORT', args.port))
    instance_id = os.environ.get('MCP_INSTANCE_ID', args.instance_id)
    
    logger.info(f"🚀 Starting Dashboard Backend for instance {instance_id} on port {port}...")
    
    # Update app title with instance info
    if instance_id:
        app.title = f"AI Agent System Dashboard - Instance {instance_id}"
    
    uvicorn.run(
        "main:app",
        host=args.host,
        port=port,
        reload=args.reload,
        log_level=args.log_level
    )
