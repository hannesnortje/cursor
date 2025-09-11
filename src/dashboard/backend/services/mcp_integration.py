#!/usr/bin/env python3
"""
MCP Integration Service for Dashboard
Connects dashboard with the MCP server to get real-time data
"""

import asyncio
import logging
import subprocess
import sys
import psutil
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPIntegrationService:
    """Service for integrating dashboard with MCP server."""

    def __init__(self, instance_id: str = None):
        self.instance_id = instance_id
        self.mcp_server_path = Path(
            "/media/hannesn/storage/Code/cursor/protocol_server.py"
        )
        self.mcp_process = None
        self._is_connected = False
        self.connection_attempts = 0
        self.max_attempts = 3

        # Try to get instance info from registry
        try:
            from ...core.instance_registry import get_registry

            self.registry = get_registry()
            if instance_id:
                self.instance_info = self.registry.get_instance(instance_id)
            else:
                self.instance_info = None
        except ImportError:
            self.registry = None
            self.instance_info = None

    async def initialize(self):
        """Initialize MCP integration service."""
        try:
            # Check if MCP server file exists
            if not self.mcp_server_path.exists():
                logger.warning("MCP server file not found, integration disabled")
                return

            # Try to connect to existing MCP server
            await self._check_mcp_connection()

            if not self._is_connected:
                logger.info("Attempting to start MCP server...")
                await self._start_mcp_server()

        except Exception as e:
            logger.error(f"Failed to initialize MCP integration: {e}")
            self._is_connected = False

    async def _check_mcp_connection(self):
        """Check if MCP server is already running."""
        try:
            # Check if we have instance info from registry
            if self.registry and self.instance_id:
                instance_info = self.registry.get_instance(self.instance_id)
                if instance_info and instance_info.status == "running":
                    self._is_connected = True
                    logger.info(
                        f"MCP server connection verified for instance {self.instance_id}"
                    )
                    return

            # Check if MCP server process is running
            if self.mcp_process and self.mcp_process.poll() is None:
                self._is_connected = True
                logger.info("MCP server process is running")
                return

            # Try to find running MCP server process
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["cmdline"] and "protocol_server.py" in " ".join(
                        proc.info["cmdline"]
                    ):
                        # Create a dummy process object to track the found MCP server
                        self.mcp_process = type(
                            "Process",
                            (),
                            {"pid": proc.info["pid"], "poll": lambda self=None: None},
                        )()
                        self._is_connected = True
                        logger.info(
                            f"Found running MCP server process: {proc.info['pid']}"
                        )
                        return
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            self._is_connected = False
            logger.debug("No running MCP server found")
        except Exception as e:
            logger.debug(f"MCP server not accessible: {e}")
            self._is_connected = False

    async def _start_mcp_server(self):
        """Start MCP server if not running."""
        try:
            if self.mcp_process and self.mcp_process.poll() is None:
                logger.info("MCP server already running")
                return

            # Start MCP server in background
            self.mcp_process = subprocess.Popen(
                [sys.executable, str(self.mcp_server_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait a bit for server to start
            await asyncio.sleep(2)

            # Check if process is running
            if self.mcp_process.poll() is None:
                self._is_connected = True
                logger.info("MCP server started successfully")
            else:
                logger.error("Failed to start MCP server")
                self._is_connected = False

        except Exception as e:
            logger.error(f"Error starting MCP server: {e}")
            self._is_connected = False

    def get_mcp_status(self) -> Dict[str, Any]:
        """Get MCP server status."""
        if not self.mcp_process:
            return {"status": "not_started", "connected": False}

        if self.mcp_process.poll() is None:
            return {"status": "running", "connected": self._is_connected}
        else:
            return {"status": "stopped", "connected": False}

    async def get_agent_status(self) -> List[Dict[str, Any]]:
        """Get agent status from MCP server using unified vector store access."""
        try:
            # Try to access the actual agent system directly
            agents_data = []

            # Use the unified vector store to get agents (respects fallback)
            try:
                sys.path.append("/media/hannesn/storage/Code/cursor/src")
                # Add project root to Python path for imports
                project_root = str(Path(__file__).parents[3])
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                from src.database.enhanced_vector_store import get_enhanced_vector_store

                vector_store = get_enhanced_vector_store()

                # Get health status for monitoring
                health = vector_store.get_health_status()
                logger.info(
                    f"Vector store status: {health['mode']}, connected: {health['connected']}"
                )

                if health["mode"] == "fallback":
                    logger.warning(
                        f"Vector store in fallback mode for {health.get('fallback_duration', 0):.1f} seconds"
                    )

                # Get all agent collections using the vector store
                if vector_store.fallback_mode:
                    # Get from in-memory store
                    for (
                        collection_name,
                        points,
                    ) in vector_store.in_memory_store.collections.items():
                        if collection_name.endswith("_agents"):
                            for point in points:
                                payload = point.get("payload", {})
                                if payload.get("agent_id"):
                                    agents_data.append(
                                        {
                                            "agent_id": payload.get(
                                                "agent_id", "unknown"
                                            ),
                                            "agent_type": payload.get(
                                                "role", "unknown"
                                            ),
                                            "name": payload.get("agent_id", "unknown"),
                                            "status": payload.get(
                                                "status", "operational"
                                            ),
                                            "last_activity": payload.get(
                                                "updated_at", datetime.now().isoformat()
                                            ),
                                            "capabilities": payload.get(
                                                "capabilities", []
                                            ),
                                            "project_id": payload.get("project_id", ""),
                                            "created_at": payload.get("created_at", ""),
                                            "specializations": payload.get(
                                                "specializations", []
                                            ),
                                            "source": "memory_fallback",
                                        }
                                    )
                else:
                    # Get from Qdrant through the vector store
                    import requests

                    qdrant_url = "http://localhost:6333"

                    try:
                        # Get all collections that end with '_agents'
                        collections_response = requests.get(f"{qdrant_url}/collections")
                        if collections_response.status_code == 200:
                            collections = collections_response.json()["result"][
                                "collections"
                            ]

                            for collection in collections:
                                collection_name = collection["name"]
                                if collection_name.endswith("_agents"):
                                    # Get agents from this collection
                                    response = requests.post(
                                        f"{qdrant_url}/collections/{collection_name}/points/scroll",
                                        json={
                                            "limit": 100,
                                            "with_payload": True,
                                            "with_vector": False,
                                        },
                                    )

                                    if response.status_code == 200:
                                        data = response.json()
                                        agents = data["result"]["points"]

                                        for agent in agents:
                                            payload = agent["payload"]
                                            agents_data.append(
                                                {
                                                    "agent_id": payload.get(
                                                        "agent_id", "unknown"
                                                    ),
                                                    "agent_type": payload.get(
                                                        "role", "unknown"
                                                    ),
                                                    "name": payload.get(
                                                        "agent_id", "unknown"
                                                    ),
                                                    "status": payload.get(
                                                        "status", "operational"
                                                    ),
                                                    "last_activity": payload.get(
                                                        "updated_at",
                                                        datetime.now().isoformat(),
                                                    ),
                                                    "capabilities": payload.get(
                                                        "capabilities", []
                                                    ),
                                                    "project_id": payload.get(
                                                        "project_id", ""
                                                    ),
                                                    "created_at": payload.get(
                                                        "created_at", ""
                                                    ),
                                                    "specializations": payload.get(
                                                        "specializations", []
                                                    ),
                                                    "source": "qdrant",
                                                }
                                            )
                    except Exception as e:
                        logger.warning(f"Failed to get agents from Qdrant: {e}")
                        # Force recovery attempt
                        if vector_store.force_recovery_attempt():
                            logger.info("Successfully forced Qdrant recovery")

                if agents_data:
                    logger.info(
                        f"Found {len(agents_data)} agents via unified vector store"
                    )
                    return agents_data

            except Exception as e:
                logger.warning(f"Unified vector store access failed: {e}")

            # Original fallback approach - direct agent system access
            try:
                from protocol_server import AgentSystem

                # Create agent system instance (same as the running MCP server)
                agent_system = AgentSystem()

                # The agent system should have access to the agent database
                logger.info("Attempting to get real agent data from MCP system...")

                # Try to access the agent storage directly
                if hasattr(agent_system, "agents") and agent_system.agents:
                    for agent_id, agent_data in agent_system.agents.items():
                        # Only add if not already found
                        if not any(a["agent_id"] == agent_id for a in agents_data):
                            agents_data.append(
                                {
                                    "agent_id": agent_id,
                                    "agent_type": agent_data.get("role", "unknown"),
                                    "name": agent_data.get("name", agent_id),
                                    "status": "operational",
                                    "last_activity": datetime.now().isoformat(),
                                    "capabilities": agent_data.get("capabilities", []),
                                    "project_id": agent_data.get("project_id", ""),
                                    "created_at": agent_data.get("created_at", ""),
                                    "specializations": agent_data.get(
                                        "specializations", []
                                    ),
                                    "source": "memory",
                                }
                            )

                # If we found agents, return them
                if agents_data:
                    logger.info(f"Found {len(agents_data)} total agents")
                    return agents_data

            except Exception as e:
                logger.debug(f"Direct agent system access failed: {e}")

            # If we found agents from any source, return them
            if agents_data:
                logger.info(f"Returning {len(agents_data)} agents from various sources")
                return agents_data

            # Fallback: Show MCP server status if no agents found
            # Check if we have a running MCP server process
            mcp_server_found = False
            mcp_pid = None

            # Try to find running MCP server process
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["cmdline"] and "protocol_server.py" in " ".join(
                        proc.info["cmdline"]
                    ):
                        mcp_server_found = True
                        mcp_pid = proc.info["pid"]
                        break
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            if mcp_server_found:
                # Get process info
                try:
                    process = psutil.Process(mcp_pid)
                    create_time = process.create_time()
                    uptime_seconds = time.time() - create_time
                    uptime_hours = int(uptime_seconds // 3600)
                    uptime_minutes = int((uptime_seconds % 3600) // 60)
                    uptime_str = f"{uptime_hours}h {uptime_minutes}m"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    uptime_str = "Unknown"

                return [
                    {
                        "agent_id": f"mcp_server_{mcp_pid}",
                        "agent_type": "mcp_server",
                        "name": "MCP Server",
                        "status": "operational",
                        "last_activity": datetime.now().isoformat(),
                        "uptime": uptime_str,
                        "process_id": mcp_pid,
                        "memory_usage": (
                            round(process.memory_info().rss / 1024 / 1024, 1)
                            if "process" in locals()
                            else 0
                        ),
                        "cpu_usage": (
                            round(process.cpu_percent(), 1)
                            if "process" in locals()
                            else 0
                        ),
                    }
                ]

            # Try to get from registry if available
            if self.registry and self.instance_id:
                try:
                    instance_info = self.registry.get_instance(self.instance_id)
                    if instance_info and instance_info.status == "running":
                        return [
                            {
                                "agent_id": f"mcp_server_{self.instance_id}",
                                "agent_type": "mcp_server",
                                "name": "MCP Server",
                                "status": "operational",
                                "last_activity": instance_info.started_at or "Unknown",
                                "uptime": self._calculate_uptime(
                                    instance_info.started_at
                                ),
                                "dashboard_port": instance_info.dashboard_port,
                                "process_id": instance_info.process_id,
                            }
                        ]
                except Exception as e:
                    logger.debug(f"Registry lookup failed: {e}")

            return []
        except Exception as e:
            logger.error(f"Failed to get agent status: {e}")
            return []

    async def get_system_health(self) -> Dict[str, Any]:
        """Get system health from MCP server."""
        try:
            # Get real system health data
            current_time = datetime.now().isoformat()

            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage("/")

            # Calculate uptime
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_hours = int(uptime_seconds // 3600)
            uptime_minutes = int((uptime_seconds % 3600) // 60)
            uptime_str = f"{uptime_hours}h {uptime_minutes}m"

            # Check if MCP server is running
            mcp_server_running = False
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if proc.info["cmdline"] and "protocol_server.py" in " ".join(
                        proc.info["cmdline"]
                    ):
                        mcp_server_running = True
                        break
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue

            # Get MCP server status
            mcp_status = self.get_mcp_status()
            overall_status = "operational" if mcp_server_running else "degraded"

            # Count active connections (simplified)
            active_connections = 1 if mcp_server_running else 0

            return {
                "overall_status": overall_status,
                "timestamp": current_time,
                "uptime": uptime_str,
                "memory_usage": round(memory.percent, 1),
                "cpu_usage": round(cpu_percent, 1),
                "disk_usage": round(disk.percent, 1),
                "active_connections": active_connections,
                "errors_count": 0,
                "warnings_count": 0 if mcp_server_running else 1,
                "mcp_connected": mcp_server_running,
                "mcp_status": "running" if mcp_server_running else "not_started",
            }
        except Exception as e:
            logger.error(f"Failed to get system health: {e}")
            return {
                "overall_status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "mcp_connected": False,
            }

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics from MCP server."""
        try:
            # Get real performance metrics
            current_time = datetime.now().isoformat()

            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)

            # Get MCP server process info if available
            mcp_memory = 0
            mcp_cpu = 0
            if self.mcp_process and self.mcp_process.poll() is None:
                try:
                    process = psutil.Process(self.mcp_process.pid)
                    mcp_memory = process.memory_info().rss / 1024 / 1024  # MB
                    mcp_cpu = process.cpu_percent()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Get agent count
            agents = await self.get_agent_status()
            active_agents = len(agents)

            return {
                "timestamp": current_time,
                "cache_hit_rate": 95.0,  # Placeholder - would need MCP server metrics
                "response_time_avg": 50.0,  # Placeholder - would need MCP server metrics
                "throughput": active_agents * 10,  # Estimated based on agents
                "active_agents": active_agents,
                "memory_usage": round(memory.percent, 1),
                "cpu_usage": round(cpu_percent, 1),
                "mcp_memory_mb": round(mcp_memory, 1),
                "mcp_cpu_percent": round(mcp_cpu, 1),
                "queue_depth": 0,  # Placeholder
                "mcp_connected": self._is_connected,
            }
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e),
                "mcp_connected": False,
            }

    def get_vector_store_health(self) -> Dict[str, Any]:
        """Get vector store health status for monitoring."""
        try:
            # Add project root to Python path for imports
            project_root = str(Path(__file__).parents[3])
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.database.enhanced_vector_store import get_enhanced_vector_store

            vector_store = get_enhanced_vector_store()
            health = vector_store.get_health_status()

            # Add dashboard-specific context
            health.update(
                {
                    "dashboard_assessment": (
                        "healthy"
                        if not health.get("fallback_mode", True)
                        else "degraded"
                    ),
                    "recommendation": (
                        "All systems operational"
                        if not health.get("fallback_mode", True)
                        else f"Running in fallback mode for {health.get('fallback_duration', 0):.1f}s - check Qdrant connection"
                    ),
                }
            )

            return health

        except Exception as e:
            logger.error(f"Failed to get vector store health: {e}")
            return {
                "mode": "unknown",
                "connected": False,
                "error": str(e),
                "dashboard_assessment": "unhealthy",
                "recommendation": "Unable to assess vector store health",
            }

    def force_vector_store_recovery(self) -> Dict[str, Any]:
        """Force a vector store recovery attempt."""
        try:
            # Add project root to Python path for imports
            project_root = str(Path(__file__).parents[3])
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            from src.database.enhanced_vector_store import get_enhanced_vector_store

            vector_store = get_enhanced_vector_store()

            if not vector_store.fallback_mode:
                return {"status": "success", "message": "Already connected to Qdrant"}

            success = vector_store.force_recovery_attempt()

            if success:
                return {
                    "status": "success",
                    "message": "Successfully recovered Qdrant connection",
                    "health": vector_store.get_health_status(),
                }
            else:
                return {
                    "status": "failed",
                    "message": "Recovery attempt failed - Qdrant still unavailable",
                    "health": vector_store.get_health_status(),
                }

        except Exception as e:
            logger.error(f"Failed to force recovery: {e}")
            return {"status": "error", "message": f"Recovery attempt error: {e}"}

    async def cleanup(self):
        """Cleanup MCP integration service."""
        try:
            if self.mcp_process and self.mcp_process.poll() is None:
                self.mcp_process.terminate()
                await asyncio.sleep(1)

                if self.mcp_process.poll() is None:
                    self.mcp_process.kill()

            self._is_connected = False
            logger.info("MCP integration service cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def is_connected(self) -> bool:
        """Check if MCP server is connected."""
        return self._is_connected

    def _calculate_uptime(self, started_at: str) -> str:
        """Calculate uptime from start timestamp."""
        if not started_at:
            return "Unknown"

        try:
            start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
            now = datetime.now(start_time.tzinfo)
            uptime_seconds = (now - start_time).total_seconds()

            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            return f"{hours}h {minutes}m"
        except Exception:
            return "Unknown"
