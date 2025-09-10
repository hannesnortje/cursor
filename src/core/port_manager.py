#!/usr/bin/env python3
"""
Port Management System
Handles dynamic port allocation for MCP server instances
"""

import logging
import socket
from typing import Set, Optional, List
from dataclasses import dataclass
from pathlib import Path
import json
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class NoPortsAvailableError(Exception):
    """Exception raised when no ports are available."""

    pass


@dataclass
class PortRange:
    """Port range configuration."""

    start: int
    end: int

    def __post_init__(self):
        if self.start > self.end:
            raise ValueError("Start port must be less than or equal to end port")
        if self.start < 1024:
            raise ValueError("Start port must be >= 1024 (system ports)")
        if self.end > 65535:
            raise ValueError("End port must be <= 65535")


class PortPool:
    """Manages a pool of available ports."""

    def __init__(
        self, port_ranges: List[PortRange] = None, state_file: Optional[Path] = None
    ):
        """
        Initialize port pool.

        Args:
            port_ranges: List of port ranges to manage
            state_file: Optional file to persist port state
        """
        if port_ranges is None:
            # Default port ranges for dashboard instances
            port_ranges = [
                PortRange(5000, 5100),  # Dashboard instances
                PortRange(5101, 5200),  # Communication ports
            ]

        self.port_ranges = port_ranges
        self.state_file = state_file or Path.home() / ".mcp_port_state.json"
        self.lock = threading.Lock()

        # Initialize port sets
        self._initialize_ports()

        # Load persisted state
        self._load_state()

    def _initialize_ports(self):
        """Initialize available and used port sets."""
        self.available_ports: Set[int] = set()
        self.used_ports: Set[int] = set()

        for port_range in self.port_ranges:
            for port in range(port_range.start, port_range.end + 1):
                self.available_ports.add(port)

    def _load_state(self):
        """Load port state from file."""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    data = json.load(f)
                    used_ports = set(data.get("used_ports", []))

                    # Validate that used ports are still in our ranges
                    for port in used_ports.copy():
                        if not self._is_port_in_ranges(port):
                            used_ports.discard(port)

                    self.used_ports = used_ports
                    self.available_ports -= used_ports

                logger.info(
                    f"Loaded port state: {len(self.used_ports)} used, {len(self.available_ports)} available"
                )
        except Exception as e:
            logger.warning(f"Failed to load port state: {e}")

    def _save_state(self):
        """Save port state to file."""
        try:
            # Don't acquire lock here - it's already held by caller
            data = {
                "used_ports": list(self.used_ports),
                "timestamp": datetime.now().isoformat(),
            }

            # Ensure directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.warning(f"Failed to save port state: {e}")

    def _is_port_in_ranges(self, port: int) -> bool:
        """Check if port is within configured ranges."""
        for port_range in self.port_ranges:
            if port_range.start <= port <= port_range.end:
                return True
        return False

    def _is_port_available(self, port: int) -> bool:
        """Check if port is actually available on the system."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)  # Much faster timeout
                result = sock.connect_ex(("localhost", port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False

    def allocate_port(self, preferred_port: Optional[int] = None) -> int:
        """
        Allocate an available port.

        Args:
            preferred_port: Preferred port number (if available)

        Returns:
            Allocated port number

        Raises:
            NoPortsAvailableError: If no ports are available
        """
        with self.lock:
            logger.info(
                f"Allocating port, available: {len(self.available_ports)}, used: {len(self.used_ports)}"
            )

            # Try preferred port first
            if preferred_port and self._try_allocate_port(preferred_port):
                logger.info(f"Allocated preferred port {preferred_port}")
                return preferred_port

            # Find first available port
            logger.info("Searching for available port in pool...")
            for i, port in enumerate(sorted(self.available_ports)):
                if i % 50 == 0:  # Log every 50 ports
                    logger.info(f"Checked {i} ports, current: {port}")
                if self._try_allocate_port(port):
                    logger.info(f"Allocated port {port} from pool")
                    return port

            # If no ports in pool, try to find any available port in ranges
            logger.info("No ports in pool, searching ranges...")
            for port_range in self.port_ranges:
                for port in range(port_range.start, port_range.end + 1):
                    if port not in self.used_ports and self._is_port_available(port):
                        self._allocate_port_internal(port)
                        logger.info(f"Allocated port {port} from range")
                        return port

            raise NoPortsAvailableError("No ports available in configured ranges")

    def _try_allocate_port(self, port: int) -> bool:
        """Try to allocate a specific port."""
        if port in self.available_ports:
            # Skip the actual port availability check for now to avoid hanging
            # Just check if it's in our available pool
            self._allocate_port_internal(port)
            return True
        return False

    def _allocate_port_internal(self, port: int):
        """Internal method to allocate a port."""
        self.available_ports.discard(port)
        self.used_ports.add(port)
        self._save_state()
        logger.info(f"Allocated port {port}")

    def release_port(self, port: int):
        """
        Release a port back to the pool.

        Args:
            port: Port number to release
        """
        with self.lock:
            if port in self.used_ports:
                self.used_ports.discard(port)
                if self._is_port_in_ranges(port):
                    self.available_ports.add(port)
                self._save_state()
                logger.info(f"Released port {port}")
            else:
                logger.warning(f"Attempted to release unallocated port {port}")

    def get_available_count(self) -> int:
        """Get count of available ports."""
        return len(self.available_ports)

    def get_used_count(self) -> int:
        """Get count of used ports."""
        return len(self.used_ports)

    def get_used_ports(self) -> Set[int]:
        """Get set of used ports."""
        return self.used_ports.copy()

    def cleanup_stale_ports(self):
        """Clean up ports that are no longer in use."""
        with self.lock:
            stale_ports = set()
            for port in self.used_ports:
                if self._is_port_available(port):
                    stale_ports.add(port)

            for port in stale_ports:
                self.release_port(port)
                logger.info(f"Cleaned up stale port {port}")

    def get_status(self) -> dict:
        """Get port pool status."""
        return {
            "available_count": self.get_available_count(),
            "used_count": self.get_used_count(),
            "total_ports": len(self.available_ports) + len(self.used_ports),
            "used_ports": list(self.used_ports),
            "port_ranges": [
                {"start": pr.start, "end": pr.end} for pr in self.port_ranges
            ],
        }


# Global port pool instance
_port_pool: Optional[PortPool] = None


def get_port_pool() -> PortPool:
    """Get global port pool instance."""
    global _port_pool
    if _port_pool is None:
        _port_pool = PortPool()
    return _port_pool


def allocate_dashboard_port() -> int:
    """Allocate a port for dashboard instance."""
    return get_port_pool().allocate_port()


def allocate_communication_port() -> int:
    """Allocate a port for communication."""
    return get_port_pool().allocate_port()


def release_port(port: int):
    """Release a port."""
    get_port_pool().release_port(port)
