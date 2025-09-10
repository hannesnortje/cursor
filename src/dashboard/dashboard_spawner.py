#!/usr/bin/env python3
"""
Dashboard Spawner Service
Automatically spawns dashboard instances for MCP server instances
"""

import asyncio
import logging
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

from ..core.instance_info import InstanceInfo, InstanceStatus
from ..core.instance_registry import get_registry
from .browser_manager import get_browser_manager, open_dashboard_in_browser
from .browser_config import get_browser_config, should_auto_open_browser

logger = logging.getLogger(__name__)


class DashboardSpawner:
    """Service for spawning dashboard instances for MCP server instances."""

    def __init__(self):
        self.active_dashboards: Dict[str, Dict[str, Any]] = {}
        self.registry = get_registry()
        self.dashboard_backend_path = Path(__file__).parent / "backend" / "main.py"
        self.lock = threading.Lock()
        self.browser_manager = get_browser_manager()
        self.browser_config = get_browser_config()
        self.auto_open_browser = True  # Enable automatic browser opening by default

    async def spawn_dashboard(
        self, instance_id: str, port: int, mcp_instance_info: InstanceInfo
    ) -> bool:
        """
        Spawn a dashboard instance for an MCP server instance.

        Args:
            instance_id: MCP instance ID
            port: Port for the dashboard
            mcp_instance_info: MCP instance information

        Returns:
            True if dashboard spawned successfully
        """
        try:
            with self.lock:
                # Check if dashboard already exists for this instance
                if instance_id in self.active_dashboards:
                    logger.info(f"Dashboard already exists for instance {instance_id}")
                    return True

                # Validate dashboard backend exists
                if not self.dashboard_backend_path.exists():
                    logger.error(
                        f"Dashboard backend not found at {self.dashboard_backend_path}"
                    )
                    return False

                # Create dashboard configuration
                dashboard_config = {
                    "instance_id": instance_id,
                    "port": port,
                    "mcp_instance_info": mcp_instance_info,
                    "process": None,
                    "started_at": datetime.now(),
                    "status": "starting",
                }

                # Start dashboard process
                success = await self._start_dashboard_process(dashboard_config)

                if success:
                    self.active_dashboards[instance_id] = dashboard_config
                    logger.info(
                        f"✅ Dashboard spawned for instance {instance_id} on port {port}"
                    )

                    # Update MCP instance with dashboard info
                    self.registry.update_instance(
                        instance_id,
                        dashboard_process=dashboard_config["process"],
                        config={"dashboard_spawned": True, "dashboard_port": port},
                    )

                    # Open browser automatically if enabled
                    if self.auto_open_browser and should_auto_open_browser(
                        len(self.active_dashboards)
                    ):
                        # Add delay before opening browser
                        time.sleep(self.browser_config.auto_open_delay)
                        self._open_dashboard_in_browser(instance_id, port)

                    return True
                else:
                    logger.error(
                        f"❌ Failed to spawn dashboard for instance {instance_id}"
                    )
                    return False

        except Exception as e:
            logger.error(f"Error spawning dashboard for instance {instance_id}: {e}")
            return False

    async def _start_dashboard_process(self, dashboard_config: Dict[str, Any]) -> bool:
        """Start the dashboard backend process."""
        try:
            instance_id = dashboard_config["instance_id"]
            port = dashboard_config["port"]

            # Prepare environment variables
            env = {
                "DASHBOARD_PORT": str(port),
                "MCP_INSTANCE_ID": instance_id,
                "PYTHONPATH": str(Path.cwd()),
                **dashboard_config["mcp_instance_info"].environment,
            }

            # Start dashboard backend process
            # Set working directory to the dashboard backend directory
            backend_dir = self.dashboard_backend_path.parent
            process = subprocess.Popen(
                [
                    sys.executable,
                    str(self.dashboard_backend_path),
                    "--port",
                    str(port),
                    "--instance-id",
                    instance_id,
                ],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=backend_dir,
            )

            dashboard_config["process"] = process

            # Wait for dashboard to start
            await self._wait_for_dashboard_startup(port, timeout=30)

            # Check if process is still running
            if process.poll() is None:
                dashboard_config["status"] = "running"
                logger.info(
                    f"Dashboard process started successfully for instance {instance_id}"
                )
                return True
            else:
                # Process exited, check for errors
                stdout, stderr = process.communicate()
                logger.error(
                    f"Dashboard process exited: stdout={stdout}, stderr={stderr}"
                )
                return False

        except Exception as e:
            logger.error(f"Error starting dashboard process: {e}")
            return False

    async def _wait_for_dashboard_startup(self, port: int, timeout: int = 30):
        """Wait for dashboard to be ready."""
        import socket
        import time

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(("localhost", port))
                    if result == 0:
                        logger.info(f"Dashboard on port {port} is ready")
                        return True
            except Exception:
                pass

            await asyncio.sleep(1)

        logger.warning(
            f"Dashboard on port {port} did not start within {timeout} seconds"
        )
        return False

    def _open_dashboard_in_browser(self, instance_id: str, port: int):
        """Open dashboard in browser."""
        try:
            url = f"http://localhost:{port}"
            success = open_dashboard_in_browser(url, instance_id)

            if success:
                logger.info(
                    f"🌐 Dashboard opened in browser for instance {instance_id}: {url}"
                )
            else:
                logger.warning(
                    f"⚠️ Failed to open dashboard in browser for instance {instance_id}"
                )

        except Exception as e:
            logger.error(
                f"Error opening dashboard in browser for instance {instance_id}: {e}"
            )

    def open_dashboard_browser(self, instance_id: str) -> bool:
        """
        Manually open dashboard in browser for an instance.

        Args:
            instance_id: Instance ID

        Returns:
            True if browser opened successfully
        """
        try:
            with self.lock:
                if instance_id not in self.active_dashboards:
                    logger.warning(f"No dashboard found for instance {instance_id}")
                    return False

                dashboard_config = self.active_dashboards[instance_id]
                port = dashboard_config["port"]

                return self._open_dashboard_in_browser(instance_id, port)

        except Exception as e:
            logger.error(
                f"Error opening dashboard browser for instance {instance_id}: {e}"
            )
            return False

    def stop_dashboard(self, instance_id: str) -> bool:
        """
        Stop a dashboard instance.

        Args:
            instance_id: MCP instance ID

        Returns:
            True if stopped successfully
        """
        try:
            with self.lock:
                if instance_id not in self.active_dashboards:
                    logger.warning(f"No dashboard found for instance {instance_id}")
                    return False

                dashboard_config = self.active_dashboards[instance_id]
                process = dashboard_config.get("process")

                if process and process.poll() is None:
                    # Gracefully terminate the process
                    process.terminate()

                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        # Force kill if graceful shutdown fails
                        process.kill()
                        process.wait()

                    logger.info(f"Dashboard stopped for instance {instance_id}")

                # Remove from active dashboards
                del self.active_dashboards[instance_id]

                # Update registry
                self.registry.update_instance(
                    instance_id,
                    dashboard_process=None,
                    config={"dashboard_spawned": False},
                )

                return True

        except Exception as e:
            logger.error(f"Error stopping dashboard for instance {instance_id}: {e}")
            return False

    def get_dashboard_status(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get dashboard status for an instance."""
        with self.lock:
            if instance_id not in self.active_dashboards:
                return None

            dashboard_config = self.active_dashboards[instance_id]
            process = dashboard_config.get("process")

            return {
                "instance_id": instance_id,
                "port": dashboard_config["port"],
                "status": dashboard_config["status"],
                "started_at": dashboard_config["started_at"].isoformat(),
                "process_running": process.poll() is None if process else False,
                "dashboard_url": f"http://localhost:{dashboard_config['port']}",
            }

    def get_all_dashboards_status(self) -> Dict[str, Any]:
        """Get status of all active dashboards."""
        with self.lock:
            dashboards = {}
            for instance_id, config in self.active_dashboards.items():
                dashboards[instance_id] = self.get_dashboard_status(instance_id)

            return {
                "total_dashboards": len(self.active_dashboards),
                "dashboards": dashboards,
                "timestamp": datetime.now().isoformat(),
            }

    def cleanup_stale_dashboards(self):
        """Clean up dashboards for instances that are no longer running."""
        with self.lock:
            stale_instances = []

            for instance_id, config in self.active_dashboards.items():
                process = config.get("process")
                if process and process.poll() is not None:
                    # Process has exited
                    stale_instances.append(instance_id)
                else:
                    # Check if MCP instance is still running
                    mcp_instance = self.registry.get_instance(instance_id)
                    if not mcp_instance or not mcp_instance.is_running:
                        stale_instances.append(instance_id)

            # Clean up stale instances
            for instance_id in stale_instances:
                logger.info(f"Cleaning up stale dashboard for instance {instance_id}")
                self.stop_dashboard(instance_id)

    async def auto_spawn_for_running_instances(self):
        """Automatically spawn dashboards for all running MCP instances."""
        try:
            running_instances = self.registry.get_running_instances()

            for instance in running_instances:
                if (
                    instance.dashboard_port
                    and instance_id not in self.active_dashboards
                ):
                    logger.info(
                        f"Auto-spawning dashboard for running instance {instance.instance_id}"
                    )
                    await self.spawn_dashboard(
                        instance.instance_id, instance.dashboard_port, instance
                    )

        except Exception as e:
            logger.error(f"Error in auto-spawn: {e}")


# Global dashboard spawner instance
_spawner: Optional[DashboardSpawner] = None


def get_dashboard_spawner() -> DashboardSpawner:
    """Get global dashboard spawner instance."""
    global _spawner
    if _spawner is None:
        _spawner = DashboardSpawner()
    return _spawner


async def spawn_dashboard_for_instance(
    instance_id: str, port: int, mcp_instance_info: InstanceInfo
) -> bool:
    """Spawn dashboard for an instance using global spawner."""
    return await get_dashboard_spawner().spawn_dashboard(
        instance_id, port, mcp_instance_info
    )


def stop_dashboard_for_instance(instance_id: str) -> bool:
    """Stop dashboard for an instance using global spawner."""
    return get_dashboard_spawner().stop_dashboard(instance_id)
