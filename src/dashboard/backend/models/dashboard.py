#!/usr/bin/env python3
"""
Dashboard data models for the AI Agent System
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any
from enum import Enum


class ServiceStatus(str, Enum):
    """Service status enumeration."""

    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"
    LIMITED = "limited"


@dataclass
class DashboardStatus:
    """Overall dashboard status."""

    status: str
    timestamp: str
    version: str
    mcp_connected: bool
    services: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemHealth:
    """System health information."""

    overall_status: ServiceStatus
    timestamp: str
    uptime: str
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int
    errors_count: int = 0
    warnings_count: int = 0


@dataclass
class AgentStatus:
    """Individual agent status."""

    agent_id: str
    agent_type: str
    name: str
    status: ServiceStatus
    last_activity: str
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    uptime: str = ""


@dataclass
class PerformanceMetrics:
    """Performance metrics data."""

    timestamp: str
    cache_hit_rate: float
    response_time_avg: float
    throughput: float
    active_agents: int
    memory_usage: float
    cpu_usage: float
    queue_depth: int = 0


@dataclass
class CommunicationStats:
    """Communication statistics."""

    timestamp: str
    total_messages: int
    messages_per_second: float
    active_chats: int
    websocket_connections: int
    redis_queue_size: int
    error_rate: float = 0.0


@dataclass
class DashboardConfig:
    """Dashboard configuration."""

    refresh_interval: int = 5000  # milliseconds
    max_data_points: int = 100
    enable_real_time: bool = True
    chart_colors: List[str] = field(
        default_factory=lambda: ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
    )
    theme: str = "dark"
