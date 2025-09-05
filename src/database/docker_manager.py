"""Docker integration for automatic Qdrant container management."""

import logging
import subprocess
import time
import asyncio
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import docker
import requests

logger = logging.getLogger(__name__)


@dataclass
class QdrantContainerConfig:
    """Qdrant container configuration."""
    image: str = "qdrant/qdrant:latest"
    container_name: str = "ai-agent-qdrant"
    port: int = 6333
    data_volume: str = "ai-agent-qdrant-data"
    config_file: Optional[str] = None
    environment: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {
                "QDRANT__SERVICE__HTTP_PORT": str(self.port),
                "QDRANT__SERVICE__GRPC_PORT": str(self.port + 1)
            }


class QdrantDockerManager:
    """Manages Qdrant Docker container for the AI agent system."""
    
    def __init__(self, config: QdrantContainerConfig = None):
        self.config = config or QdrantContainerConfig()
        self.docker_client = None
        self.container = None
        self.is_running = False
        
        # Initialize Docker client
        self._initialize_docker_client()
    
    def _initialize_docker_client(self):
        """Initialize Docker client."""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            self.docker_client = None
    
    async def start_qdrant(self, force_restart: bool = False) -> bool:
        """Start Qdrant container."""
        if not self.docker_client:
            logger.error("Docker client not available")
            return False
        
        try:
            # Check if container already exists
            try:
                self.container = self.docker_client.containers.get(self.config.container_name)
                if self.container.status == "running":
                    if force_restart:
                        logger.info("Restarting existing Qdrant container")
                        await self.stop_qdrant()
                    else:
                        logger.info("Qdrant container already running")
                        self.is_running = True
                        return True
            except docker.errors.NotFound:
                logger.info("Qdrant container not found, creating new one")
            
            # Create data volume if it doesn't exist
            try:
                self.docker_client.volumes.get(self.config.data_volume)
            except docker.errors.NotFound:
                self.docker_client.volumes.create(
                    name=self.config.data_volume,
                    driver="local"
                )
                logger.info(f"Created data volume: {self.config.data_volume}")
            
            # Prepare container configuration
            container_config = {
                "image": self.config.image,
                "name": self.config.container_name,
                "ports": {f"{self.config.port}/tcp": self.config.port},
                "volumes": {
                    self.config.data_volume: {"bind": "/qdrant/storage", "mode": "rw"}
                },
                "environment": self.config.environment,
                "detach": True,
                "restart_policy": {"Name": "unless-stopped"}
            }
            
            # Add config file if specified
            if self.config.config_file:
                container_config["volumes"][self.config.config_file] = {
                    "bind": "/qdrant/config/production.yaml",
                    "mode": "ro"
                }
            
            # Create and start container
            if self.container and self.container.status != "running":
                self.container.remove(force=True)
            
            self.container = self.docker_client.containers.run(**container_config)
            logger.info(f"Started Qdrant container: {self.config.container_name}")
            
            # Wait for Qdrant to be ready
            if await self._wait_for_qdrant_ready():
                self.is_running = True
                logger.info("Qdrant is ready and accepting connections")
                return True
            else:
                logger.error("Qdrant failed to start properly")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Qdrant container: {e}")
            return False
    
    async def stop_qdrant(self) -> bool:
        """Stop Qdrant container."""
        if not self.container:
            logger.info("No Qdrant container to stop")
            return True
        
        try:
            self.container.stop(timeout=10)
            logger.info("Stopped Qdrant container")
            self.is_running = False
            return True
        except Exception as e:
            logger.error(f"Failed to stop Qdrant container: {e}")
            return False
    
    async def restart_qdrant(self) -> bool:
        """Restart Qdrant container."""
        logger.info("Restarting Qdrant container")
        await self.stop_qdrant()
        await asyncio.sleep(2)  # Brief pause
        return await self.start_qdrant()
    
    async def remove_qdrant(self, remove_volume: bool = False) -> bool:
        """Remove Qdrant container and optionally data volume."""
        try:
            if self.container:
                self.container.remove(force=True)
                logger.info("Removed Qdrant container")
            
            if remove_volume:
                try:
                    volume = self.docker_client.volumes.get(self.config.data_volume)
                    volume.remove(force=True)
                    logger.info(f"Removed data volume: {self.config.data_volume}")
                except docker.errors.NotFound:
                    logger.info("Data volume not found")
            
            self.container = None
            self.is_running = False
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove Qdrant container: {e}")
            return False
    
    async def get_qdrant_status(self) -> Dict[str, Any]:
        """Get Qdrant container status."""
        if not self.container:
            return {
                "status": "not_found",
                "running": False,
                "message": "Container not found"
            }
        
        try:
            self.container.reload()
            return {
                "status": self.container.status,
                "running": self.container.status == "running",
                "created": self.container.attrs["Created"],
                "ports": self.container.attrs["NetworkSettings"]["Ports"],
                "image": self.container.image.tags[0] if self.container.image.tags else "unknown"
            }
        except Exception as e:
            return {
                "status": "error",
                "running": False,
                "message": str(e)
            }
    
    async def _wait_for_qdrant_ready(self, timeout: int = 30) -> bool:
        """Wait for Qdrant to be ready to accept connections."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{self.config.port}/collections", timeout=5)
                if response.status_code == 200:
                    logger.info("Qdrant is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            await asyncio.sleep(1)
        
        logger.error(f"Qdrant failed to start within {timeout} seconds")
        return False
    
    async def get_qdrant_logs(self, tail: int = 100) -> List[str]:
        """Get Qdrant container logs."""
        if not self.container:
            return []
        
        try:
            logs = self.container.logs(tail=tail, timestamps=True).decode("utf-8")
            return logs.split("\n")
        except Exception as e:
            logger.error(f"Failed to get Qdrant logs: {e}")
            return []
    
    async def backup_qdrant_data(self, backup_path: str) -> bool:
        """Backup Qdrant data."""
        if not self.container or not self.is_running:
            logger.error("Qdrant container not running")
            return False
        
        try:
            # Create backup using Docker exec
            backup_command = f"tar -czf /tmp/qdrant_backup.tar.gz -C /qdrant/storage ."
            result = self.container.exec_run(backup_command)
            
            if result.exit_code == 0:
                # Copy backup from container to host
                with open(backup_path, "wb") as f:
                    for chunk in self.container.get_archive("/tmp/qdrant_backup.tar.gz")[0]:
                        f.write(chunk)
                
                logger.info(f"Qdrant data backed up to: {backup_path}")
                return True
            else:
                logger.error(f"Backup command failed: {result.output.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to backup Qdrant data: {e}")
            return False
    
    async def restore_qdrant_data(self, backup_path: str) -> bool:
        """Restore Qdrant data from backup."""
        if not self.container or not self.is_running:
            logger.error("Qdrant container not running")
            return False
        
        try:
            # Stop Qdrant first
            await self.stop_qdrant()
            
            # Copy backup to container
            with open(backup_path, "rb") as f:
                self.container.put_archive("/tmp/", f.read())
            
            # Restore data
            restore_command = "tar -xzf /tmp/qdrant_backup.tar.gz -C /qdrant/storage"
            result = self.container.exec_run(restore_command)
            
            if result.exit_code == 0:
                # Restart Qdrant
                await self.start_qdrant()
                logger.info(f"Qdrant data restored from: {backup_path}")
                return True
            else:
                logger.error(f"Restore command failed: {result.output.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to restore Qdrant data: {e}")
            return False


# Global Docker manager instance
docker_manager = None

def get_docker_manager() -> QdrantDockerManager:
    """Get the global Docker manager."""
    global docker_manager
    if docker_manager is None:
        docker_manager = QdrantDockerManager()
    return docker_manager
