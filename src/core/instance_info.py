#!/usr/bin/env python3
"""
Instance Information Data Structure
Defines the data structure for MCP server instances
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import uuid


class InstanceStatus(str, Enum):
    """Instance status enumeration."""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class InstanceInfo:
    """Information about an MCP server instance."""

    # Core identification
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    process_id: Optional[int] = None

    # Port allocation
    dashboard_port: Optional[int] = None
    communication_port: Optional[int] = None

    # Status and timing
    status: InstanceStatus = InstanceStatus.STARTING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

    # Process information
    mcp_process: Optional[Any] = None
    dashboard_process: Optional[Any] = None

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    cursor_client_id: Optional[str] = None
    working_directory: Optional[str] = None
    environment: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Post-initialization setup."""
        if self.started_at is None and self.status == InstanceStatus.RUNNING:
            self.started_at = datetime.now()

    def start(self):
        """Mark instance as started."""
        self.status = InstanceStatus.RUNNING
        self.started_at = datetime.now()

    def stop(self):
        """Mark instance as stopped."""
        self.status = InstanceStatus.STOPPED
        self.stopped_at = datetime.now()

    def error(self, error_message: str):
        """Mark instance as error state."""
        self.status = InstanceStatus.ERROR
        self.config["error_message"] = error_message
        self.stopped_at = datetime.now()

    @property
    def uptime_seconds(self) -> Optional[float]:
        """Get uptime in seconds."""
        if self.started_at:
            end_time = self.stopped_at or datetime.now()
            return (end_time - self.started_at).total_seconds()
        return None

    @property
    def is_running(self) -> bool:
        """Check if instance is running."""
        return self.status == InstanceStatus.RUNNING

    @property
    def dashboard_url(self) -> Optional[str]:
        """Get dashboard URL if port is allocated."""
        if self.dashboard_port:
            return f"http://localhost:{self.dashboard_port}"
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "instance_id": self.instance_id,
            "process_id": self.process_id,
            "dashboard_port": self.dashboard_port,
            "communication_port": self.communication_port,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stopped_at": self.stopped_at.isoformat() if self.stopped_at else None,
            "config": self.config,
            "cursor_client_id": self.cursor_client_id,
            "working_directory": self.working_directory,
            "environment": self.environment,
            "uptime_seconds": self.uptime_seconds,
            "dashboard_url": self.dashboard_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InstanceInfo":
        """Create instance from dictionary."""
        instance = cls()
        instance.instance_id = data.get("instance_id", str(uuid.uuid4()))
        instance.process_id = data.get("process_id")
        instance.dashboard_port = data.get("dashboard_port")
        instance.communication_port = data.get("communication_port")
        instance.status = InstanceStatus(data.get("status", "starting"))

        # Parse datetime fields
        if data.get("created_at"):
            instance.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("started_at"):
            instance.started_at = datetime.fromisoformat(data["started_at"])
        if data.get("stopped_at"):
            instance.stopped_at = datetime.fromisoformat(data["stopped_at"])

        instance.config = data.get("config", {})
        instance.cursor_client_id = data.get("cursor_client_id")
        instance.working_directory = data.get("working_directory")
        instance.environment = data.get("environment", {})

        return instance
