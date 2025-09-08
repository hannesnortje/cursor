"""Qdrant Docker container manager for Phase 9.1 with error handling."""

import logging
import subprocess
import time
import requests
from typing import Optional, Dict, Any
import os

# Try to import Docker with fallback
try:
    import docker
    DOCKER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Docker client available")
except ImportError:
    DOCKER_AVAILABLE = False
    docker = None
    logger = logging.getLogger(__name__)
    logger.warning("Docker client not available - using subprocess fallback")

logger = logging.getLogger(__name__)


class QdrantDockerManager:
    """Manager for Qdrant Docker containers with fallback support."""
    
    def __init__(self):
        self.container_name = "qdrant-mcp-server"
        self.port = 6333
        self.docker_client = None
        self.fallback_mode = False
        
        # Try to initialize Docker client
        if DOCKER_AVAILABLE:
            try:
                self.docker_client = docker.from_env()
                # Test connection
                self.docker_client.ping()
                logger.info("Connected to Docker daemon")
            except Exception as e:
                logger.warning(f"Failed to connect to Docker: {e}")
                logger.info("Using subprocess fallback for Docker operations")
                self.fallback_mode = True
                self.docker_client = None
        else:
            logger.info("Docker not available - using subprocess fallback")
            self.fallback_mode = True
    
    def is_qdrant_running(self) -> bool:
        """Check if Qdrant container is running."""
        if self.fallback_mode:
            return self._check_qdrant_with_subprocess()
        
        try:
            container = self.docker_client.containers.get(self.container_name)
            return container.status == "running"
        except Exception as e:
            logger.warning(f"Failed to check container status: {e}")
            return self._check_qdrant_with_subprocess()
    
    def _check_qdrant_with_subprocess(self) -> bool:
        """Check Qdrant status using subprocess."""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "Up" in result.stdout
        except Exception as e:
            logger.warning(f"Failed to check container with subprocess: {e}")
            return False
    
    def start_qdrant_container(self) -> bool:
        """Start Qdrant container."""
        if self.is_qdrant_running():
            logger.info("Qdrant container is already running")
            return True
        
        logger.info(f"Starting Qdrant container: {self.container_name}")
        
        if self.fallback_mode:
            return self._start_qdrant_with_subprocess()
        
        try:
            # Try to start existing container
            try:
                container = self.docker_client.containers.get(self.container_name)
                container.start()
                logger.info("Started existing Qdrant container")
                return True
            except Exception:
                # Container doesn't exist, create new one
                pass
            
            # Create new container
            container = self.docker_client.containers.run(
                "qdrant/qdrant:latest",
                name=self.container_name,
                ports={6333: self.port, 6334: 6334},
                detach=True,
                restart_policy={"Name": "unless-stopped"}
            )
            logger.info(f"Created and started new Qdrant container: {container.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start Qdrant container with Docker client: {e}")
            logger.info("Falling back to subprocess method")
            return self._start_qdrant_with_subprocess()
    
    def _start_qdrant_with_subprocess(self) -> bool:
        """Start Qdrant container using subprocess."""
        try:
            # Check if container exists
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if self.container_name in result.stdout:
                # Container exists, start it
                subprocess.run(
                    ["docker", "start", self.container_name],
                    check=True,
                    timeout=30
                )
                logger.info("Started existing Qdrant container with subprocess")
            else:
                # Create new container
                subprocess.run([
                    "docker", "run", "-d",
                    "--name", self.container_name,
                    "-p", f"{self.port}:6333",
                    "-p", "6334:6334",
                    "--restart", "unless-stopped",
                    "qdrant/qdrant:latest"
                ], check=True, timeout=60)
                logger.info("Created and started new Qdrant container with subprocess")
            
            # Wait for Qdrant to be ready
            return self._wait_for_qdrant_ready()
            
        except Exception as e:
            logger.error(f"Failed to start Qdrant container with subprocess: {e}")
            return False
    
    def stop_qdrant_container(self) -> bool:
        """Stop Qdrant container."""
        logger.info(f"Stopping Qdrant container: {self.container_name}")
        
        if self.fallback_mode:
            return self._stop_qdrant_with_subprocess()
        
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.stop()
            logger.info("Stopped Qdrant container")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Qdrant container with Docker client: {e}")
            return self._stop_qdrant_with_subprocess()
    
    def _stop_qdrant_with_subprocess(self) -> bool:
        """Stop Qdrant container using subprocess."""
        try:
            subprocess.run(
                ["docker", "stop", self.container_name],
                check=True,
                timeout=30
            )
            logger.info("Stopped Qdrant container with subprocess")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Qdrant container with subprocess: {e}")
            return False
    
    def remove_qdrant_container(self) -> bool:
        """Remove Qdrant container."""
        logger.info(f"Removing Qdrant container: {self.container_name}")
        
        if self.fallback_mode:
            return self._remove_qdrant_with_subprocess()
        
        try:
            container = self.docker_client.containers.get(self.container_name)
            container.remove(force=True)
            logger.info("Removed Qdrant container")
            return True
        except Exception as e:
            logger.error(f"Failed to remove Qdrant container with Docker client: {e}")
            return self._remove_qdrant_with_subprocess()
    
    def _remove_qdrant_with_subprocess(self) -> bool:
        """Remove Qdrant container using subprocess."""
        try:
            subprocess.run(
                ["docker", "rm", "-f", self.container_name],
                check=True,
                timeout=30
            )
            logger.info("Removed Qdrant container with subprocess")
            return True
        except Exception as e:
            logger.error(f"Failed to remove Qdrant container with subprocess: {e}")
            return False
    
    def _wait_for_qdrant_ready(self, timeout: int = 30) -> bool:
        """Wait for Qdrant to be ready."""
        logger.info("Waiting for Qdrant to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.port}/collections", timeout=5)
                if response.status_code == 200:
                    logger.info("Qdrant is ready!")
                    return True
            except Exception:
                pass
            
            time.sleep(1)
        
        logger.error(f"Qdrant failed to become ready within {timeout} seconds")
        return False
    
    def get_container_status(self) -> Dict[str, Any]:
        """Get container status information."""
        if self.fallback_mode:
            return self._get_status_with_subprocess()
        
        try:
            container = self.docker_client.containers.get(self.container_name)
            return {
                "name": self.container_name,
                "status": container.status,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "ports": container.ports,
                "created": container.attrs["Created"],
                "docker_available": True
            }
        except Exception as e:
            logger.warning(f"Failed to get container status with Docker client: {e}")
            return self._get_status_with_subprocess()
    
    def _get_status_with_subprocess(self) -> Dict[str, Any]:
        """Get container status using subprocess."""
        try:
            result = subprocess.run(
                ["docker", "inspect", self.container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)[0]
                return {
                    "name": self.container_name,
                    "status": data["State"]["Status"],
                    "image": data["Config"]["Image"],
                    "ports": data["NetworkSettings"]["Ports"],
                    "created": data["Created"],
                    "docker_available": True
                }
            else:
                return {
                    "name": self.container_name,
                    "status": "not_found",
                    "docker_available": True
                }
        except Exception as e:
            logger.error(f"Failed to get container status with subprocess: {e}")
            return {
                "name": self.container_name,
                "status": "error",
                "error": str(e),
                "docker_available": False
            }


# Global instance
_docker_manager = None

def get_docker_manager() -> QdrantDockerManager:
    """Get the global Docker manager instance."""
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = QdrantDockerManager()
    return _docker_manager
