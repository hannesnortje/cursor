#!/usr/bin/env python3
"""
Dashboard Backend - FastAPI Application
Provides real-time monitoring and visualization for the AI Agent System
"""

import logging
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import will be handled when running as module
try:
    from .api import agents, system, performance, websocket
    from .models.dashboard import DashboardStatus
    from .services.mcp_integration import MCPIntegrationService
except ImportError:
    # For direct execution, import from current directory
    from api import agents, system, performance, websocket
    from models.dashboard import DashboardStatus
    from services.mcp_integration import MCPIntegrationService

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

# Initialize MCP integration service
mcp_service = MCPIntegrationService()

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="../frontend"), name="static")

# Include API routers
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(websocket.router, prefix="/api/websocket", tags=["websocket"])

@app.on_event("startup")
async def startup_event():
    """Initialize dashboard on startup."""
    logger.info("🚀 Dashboard Backend starting up...")
    try:
        await mcp_service.initialize()
        logger.info("✅ MCP integration service initialized successfully")
    except Exception as e:
        logger.warning(f"⚠️ MCP integration service initialization failed: {e}")
        logger.info("Dashboard will run with limited functionality")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("🛑 Dashboard Backend shutting down...")
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

if __name__ == "__main__":
    logger.info("🚀 Starting Dashboard Backend on port 5000...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
