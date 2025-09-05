#!/usr/bin/env python3
"""
Instance Registry System
Manages MCP server instances and their associated dashboards
"""

import logging
import json
import threading
from typing import Dict, List, Optional, Set
from pathlib import Path
from datetime import datetime, timedelta

from .instance_info import InstanceInfo, InstanceStatus
from .port_manager import PortPool, get_port_pool

logger = logging.getLogger(__name__)


class InstanceRegistry:
    """Registry for managing MCP server instances."""
    
    def __init__(self, registry_file: Optional[Path] = None):
        """
        Initialize instance registry.
        
        Args:
            registry_file: Optional file to persist registry state
        """
        self.registry_file = registry_file or Path.home() / ".mcp_instance_registry.json"
        self.instances: Dict[str, InstanceInfo] = {}
        self.lock = threading.Lock()
        self.port_pool = get_port_pool()
        
        # Load existing registry
        self._load_registry()
        
        # Clean up stale instances
        self._cleanup_stale_instances()
    
    def _load_registry(self):
        """Load registry from file."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    
                for instance_data in data.get('instances', []):
                    instance = InstanceInfo.from_dict(instance_data)
                    self.instances[instance.instance_id] = instance
                    
                logger.info(f"Loaded {len(self.instances)} instances from registry")
        except Exception as e:
            logger.warning(f"Failed to load registry: {e}")
    
    def _save_registry(self):
        """Save registry to file."""
        try:
            # Don't acquire lock here - it's already held by caller
            data = {
                'instances': [instance.to_dict() for instance in self.instances.values()],
                'last_updated': datetime.now().isoformat(),
                'version': '1.0'
            }
            
            # Ensure directory exists
            self.registry_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                    
        except Exception as e:
            logger.warning(f"Failed to save registry: {e}")
    
    def _cleanup_stale_instances(self):
        """Clean up instances that are no longer running."""
        with self.lock:
            stale_instances = []
            
            for instance_id, instance in self.instances.items():
                # Check if process is still running
                if instance.process_id:
                    try:
                        import psutil
                        if not psutil.pid_exists(instance.process_id):
                            stale_instances.append(instance_id)
                    except ImportError:
                        # psutil not available, skip process checking
                        pass
                
                # Check for very old stopped instances (older than 1 hour)
                if (instance.status == InstanceStatus.STOPPED and 
                    instance.stopped_at and 
                    datetime.now() - instance.stopped_at > timedelta(hours=1)):
                    stale_instances.append(instance_id)
            
            # Remove stale instances
            for instance_id in stale_instances:
                self._remove_instance_internal(instance_id)
                logger.info(f"Cleaned up stale instance {instance_id}")
    
    def register_instance(self, 
                         instance_id: Optional[str] = None,
                         cursor_client_id: Optional[str] = None,
                         working_directory: Optional[str] = None) -> InstanceInfo:
        """
        Register a new MCP server instance.
        
        Args:
            instance_id: Optional specific instance ID
            cursor_client_id: Optional Cursor client identifier
            working_directory: Optional working directory path
            
        Returns:
            InstanceInfo object for the new instance
        """
        with self.lock:
            # Create new instance
            instance = InstanceInfo()
            if instance_id:
                instance.instance_id = instance_id
            instance.cursor_client_id = cursor_client_id
            instance.working_directory = working_directory
            
            # Allocate ports
            try:
                instance.dashboard_port = self.port_pool.allocate_port()
                instance.communication_port = self.port_pool.allocate_port()
            except Exception as e:
                logger.error(f"Failed to allocate ports for instance {instance.instance_id}: {e}")
                instance.error(f"Port allocation failed: {e}")
                return instance
            
            # Register instance
            self.instances[instance.instance_id] = instance
            self._save_registry()
            
            logger.info(f"Registered new instance {instance.instance_id} with ports {instance.dashboard_port}, {instance.communication_port}")
            return instance
    
    def get_instance(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get instance by ID."""
        return self.instances.get(instance_id)
    
    def get_instances_by_status(self, status: InstanceStatus) -> List[InstanceInfo]:
        """Get all instances with specific status."""
        return [instance for instance in self.instances.values() if instance.status == status]
    
    def get_running_instances(self) -> List[InstanceInfo]:
        """Get all running instances."""
        return self.get_instances_by_status(InstanceStatus.RUNNING)
    
    def get_instance_by_port(self, port: int) -> Optional[InstanceInfo]:
        """Get instance by dashboard port."""
        for instance in self.instances.values():
            if instance.dashboard_port == port:
                return instance
        return None
    
    def update_instance(self, instance_id: str, **kwargs) -> bool:
        """
        Update instance information.
        
        Args:
            instance_id: Instance ID to update
            **kwargs: Fields to update
            
        Returns:
            True if updated successfully
        """
        with self.lock:
            instance = self.instances.get(instance_id)
            if not instance:
                return False
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            self._save_registry()
            logger.info(f"Updated instance {instance_id}")
            return True
    
    def start_instance(self, instance_id: str, process_id: int) -> bool:
        """Mark instance as started with process ID."""
        return self.update_instance(instance_id, process_id=process_id, status=InstanceStatus.RUNNING)
    
    def stop_instance(self, instance_id: str) -> bool:
        """Mark instance as stopped."""
        return self.update_instance(instance_id, status=InstanceStatus.STOPPED)
    
    def error_instance(self, instance_id: str, error_message: str) -> bool:
        """Mark instance as error state."""
        return self.update_instance(instance_id, status=InstanceStatus.ERROR, config={'error_message': error_message})
    
    def remove_instance(self, instance_id: str) -> bool:
        """
        Remove instance from registry.
        
        Args:
            instance_id: Instance ID to remove
            
        Returns:
            True if removed successfully
        """
        with self.lock:
            return self._remove_instance_internal(instance_id)
    
    def _remove_instance_internal(self, instance_id: str) -> bool:
        """Internal method to remove instance."""
        instance = self.instances.get(instance_id)
        if not instance:
            return False
        
        # Release ports
        if instance.dashboard_port:
            self.port_pool.release_port(instance.dashboard_port)
        if instance.communication_port:
            self.port_pool.release_port(instance.communication_port)
        
        # Remove from registry
        del self.instances[instance_id]
        self._save_registry()
        
        logger.info(f"Removed instance {instance_id}")
        return True
    
    def get_all_instances(self) -> List[InstanceInfo]:
        """Get all instances."""
        return list(self.instances.values())
    
    def get_registry_status(self) -> dict:
        """Get registry status information."""
        status_counts = {}
        for status in InstanceStatus:
            status_counts[status.value] = len(self.get_instances_by_status(status))
        
        return {
            'total_instances': len(self.instances),
            'status_counts': status_counts,
            'running_instances': len(self.get_running_instances()),
            'port_pool_status': self.port_pool.get_status(),
            'registry_file': str(self.registry_file),
            'last_updated': datetime.now().isoformat()
        }
    
    def cleanup_old_instances(self, max_age_hours: int = 24):
        """Clean up instances older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        with self.lock:
            old_instances = []
            for instance_id, instance in self.instances.items():
                if instance.created_at < cutoff_time:
                    old_instances.append(instance_id)
            
            for instance_id in old_instances:
                self._remove_instance_internal(instance_id)
                logger.info(f"Cleaned up old instance {instance_id}")
    
    def find_available_dashboard_port(self) -> Optional[int]:
        """Find an available dashboard port."""
        try:
            return self.port_pool.allocate_port()
        except Exception:
            return None


# Global registry instance
_registry: Optional[InstanceRegistry] = None


def get_registry() -> InstanceRegistry:
    """Get global registry instance."""
    global _registry
    if _registry is None:
        _registry = InstanceRegistry()
    return _registry


def register_new_instance(**kwargs) -> InstanceInfo:
    """Register a new instance using global registry."""
    return get_registry().register_instance(**kwargs)


def get_instance(instance_id: str) -> Optional[InstanceInfo]:
    """Get instance using global registry."""
    return get_registry().get_instance(instance_id)


def get_running_instances() -> List[InstanceInfo]:
    """Get running instances using global registry."""
    return get_registry().get_running_instances()
