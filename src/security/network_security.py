"""Network security implementation for AI Agent System."""

import socket
import ssl
import threading
import time
import logging
import psutil
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    """Network connection status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    SUSPICIOUS = "suspicious"


class SecurityLevel(Enum):
    """Security level classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NetworkConnection:
    """Represents a network connection."""

    def __init__(self, local_addr: str, remote_addr: str, status: str, pid: int = None):
        self.local_addr = local_addr
        self.remote_addr = remote_addr
        self.status = ConnectionStatus(status)
        self.pid = pid
        self.timestamp = datetime.now()
        self.security_level = SecurityLevel.LOW
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_count = 1


class SecurityEvent:
    """Represents a security event."""

    def __init__(
        self,
        event_type: str,
        description: str,
        severity: SecurityLevel,
        source_ip: str = None,
        target_port: int = None,
    ):
        self.event_type = event_type
        self.description = description
        self.severity = severity
        self.source_ip = source_ip
        self.target_port = target_port
        self.timestamp = datetime.now()
        self.event_id = f"{int(time.time())}_{hash(description) % 10000}"


class NetworkMonitor:
    """Network monitoring and security analysis."""

    def __init__(self):
        self.connections = {}
        self.security_events = []
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.RLock()

        # Configuration
        self.monitor_interval = 5  # seconds
        self.max_connections_per_ip = 10
        self.suspicious_ports = [22, 23, 135, 139, 445, 1433, 3389, 5432, 6379]

        logger.info("Network monitor initialized")

    def start_monitoring(self):
        """Start network monitoring."""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Network monitoring started")

    def stop_monitoring(self):
        """Stop network monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        logger.info("Network monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._scan_connections()
                self._analyze_security()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error in network monitoring loop: {e}")
                time.sleep(self.monitor_interval)

    def _scan_connections(self):
        """Scan current network connections."""
        try:
            connections = psutil.net_connections(kind="inet")

            with self.lock:
                # Clear old connections
                current_time = time.time()
                old_connections = [
                    key
                    for key, conn in self.connections.items()
                    if (current_time - conn.timestamp.timestamp()) > 300  # 5 minutes
                ]
                for key in old_connections:
                    del self.connections[key]

                # Process new connections
                for conn in connections:
                    if conn.status == "ESTABLISHED":
                        local_addr = (
                            f"{conn.laddr.ip}:{conn.laddr.port}"
                            if conn.laddr
                            else "unknown"
                        )
                        remote_addr = (
                            f"{conn.raddr.ip}:{conn.raddr.port}"
                            if conn.raddr
                            else "unknown"
                        )

                        key = f"{local_addr}-{remote_addr}"

                        if key in self.connections:
                            self.connections[key].connection_count += 1
                            self.connections[key].timestamp = datetime.now()
                        else:
                            self.connections[key] = NetworkConnection(
                                local_addr, remote_addr, "active", conn.pid
                            )

        except Exception as e:
            logger.error(f"Error scanning connections: {e}")

    def _analyze_security(self):
        """Analyze connections for security threats."""
        with self.lock:
            # Count connections per IP
            ip_counts = {}
            for conn in self.connections.values():
                if conn.remote_addr != "unknown":
                    ip = conn.remote_addr.split(":")[0]
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1

            # Check for suspicious activity
            for ip, count in ip_counts.items():
                if count > self.max_connections_per_ip:
                    self._create_security_event(
                        "high_connection_count",
                        f"IP {ip} has {count} active connections",
                        SecurityLevel.MEDIUM,
                        ip,
                    )

            # Check for suspicious ports
            for conn in self.connections.values():
                if conn.remote_addr != "unknown":
                    try:
                        port = int(conn.remote_addr.split(":")[1])
                        if port in self.suspicious_ports:
                            self._create_security_event(
                                "suspicious_port",
                                f"Connection to suspicious port {port} from {conn.remote_addr}",
                                SecurityLevel.HIGH,
                                conn.remote_addr.split(":")[0],
                                port,
                            )
                    except (ValueError, IndexError):
                        pass

    def _create_security_event(
        self,
        event_type: str,
        description: str,
        severity: SecurityLevel,
        source_ip: str = None,
        target_port: int = None,
    ):
        """Create a security event."""
        event = SecurityEvent(event_type, description, severity, source_ip, target_port)
        self.security_events.append(event)

        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        logger.warning(f"Security event: {event_type} - {description}")

    def get_network_statistics(self) -> Dict[str, Any]:
        """Get network statistics."""
        with self.lock:
            total_connections = len(self.connections)
            active_connections = sum(
                1
                for conn in self.connections.values()
                if conn.status == ConnectionStatus.ACTIVE
            )

            # Count by security level
            security_counts = {}
            for conn in self.connections.values():
                level = conn.security_level.value
                security_counts[level] = security_counts.get(level, 0) + 1

            # Recent security events
            recent_events = [
                {
                    "type": event.event_type,
                    "description": event.description,
                    "severity": event.severity.value,
                    "timestamp": event.timestamp.isoformat(),
                    "source_ip": event.source_ip,
                }
                for event in self.security_events[-10:]  # Last 10 events
            ]

            return {
                "total_connections": total_connections,
                "active_connections": active_connections,
                "security_levels": security_counts,
                "recent_events": recent_events,
                "monitoring_active": self.monitoring_active,
                "monitor_interval": self.monitor_interval,
            }

    def get_connections(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get current network connections."""
        with self.lock:
            connections = []
            for conn in self.connections.values():
                connections.append(
                    {
                        "local_addr": conn.local_addr,
                        "remote_addr": conn.remote_addr,
                        "status": conn.status.value,
                        "security_level": conn.security_level.value,
                        "pid": conn.pid,
                        "timestamp": conn.timestamp.isoformat(),
                        "connection_count": conn.connection_count,
                    }
                )

            # Sort by timestamp (newest first)
            connections.sort(key=lambda x: x["timestamp"], reverse=True)
            return connections[:limit]

    def get_security_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get security events."""
        with self.lock:
            events = []
            for event in self.security_events:
                events.append(
                    {
                        "event_id": event.event_id,
                        "type": event.event_type,
                        "description": event.description,
                        "severity": event.severity.value,
                        "source_ip": event.source_ip,
                        "target_port": event.target_port,
                        "timestamp": event.timestamp.isoformat(),
                    }
                )

            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x["timestamp"], reverse=True)
            return events[:limit]


class SSLConfig:
    """SSL/TLS configuration management."""

    def __init__(self):
        self.ssl_contexts = {}
        self.certificates = {}
        self.configuration = {
            "protocol": ssl.PROTOCOL_TLS,
            "verify_mode": ssl.CERT_REQUIRED,
            "check_hostname": True,
            "ciphers": "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS",
        }

        logger.info("SSL configuration initialized")

    def create_ssl_context(
        self,
        context_name: str,
        cert_file: str = None,
        key_file: str = None,
        ca_file: str = None,
    ) -> ssl.SSLContext:
        """Create an SSL context."""
        try:
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

            # Configure the context
            context.protocol = self.configuration["protocol"]
            context.verify_mode = self.configuration["verify_mode"]
            context.check_hostname = self.configuration["check_hostname"]
            context.set_ciphers(self.configuration["ciphers"])

            # Load certificates if provided
            if cert_file and key_file:
                context.load_cert_chain(cert_file, key_file)

            if ca_file:
                context.load_verify_locations(ca_file)

            self.ssl_contexts[context_name] = context
            logger.info(f"SSL context '{context_name}' created successfully")
            return context

        except Exception as e:
            logger.error(f"Error creating SSL context '{context_name}': {e}")
            raise

    def validate_ssl_config(self) -> Dict[str, Any]:
        """Validate SSL configuration."""
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": [],
            "contexts": len(self.ssl_contexts),
            "certificates": len(self.certificates),
        }

        # Check if we have any SSL contexts
        if not self.ssl_contexts:
            validation_result["recommendations"].append(
                "Consider creating SSL contexts for secure connections"
            )

        # Validate each context
        for name, context in self.ssl_contexts.items():
            try:
                # Check protocol version
                if hasattr(context, "protocol"):
                    validation_result["recommendations"].append(
                        f"Context '{name}' using protocol: {context.protocol}"
                    )

                # Check verification mode
                if context.verify_mode == ssl.CERT_NONE:
                    validation_result["issues"].append(
                        f"Context '{name}' has no certificate verification"
                    )
                    validation_result["valid"] = False

            except Exception as e:
                validation_result["issues"].append(
                    f"Error validating context '{name}': {e}"
                )
                validation_result["valid"] = False

        return validation_result

    def test_ssl_connection(
        self, host: str, port: int, context_name: str = None
    ) -> Dict[str, Any]:
        """Test SSL connection to a host."""
        try:
            context = self.ssl_contexts.get(context_name) if context_name else None

            with socket.create_connection((host, port), timeout=10) as sock:
                if context:
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        return {
                            "success": True,
                            "host": host,
                            "port": port,
                            "ssl_version": ssock.version(),
                            "cipher": ssock.cipher(),
                            "certificate": (
                                {
                                    "subject": dict(
                                        x[0] for x in cert.get("subject", [])
                                    ),
                                    "issuer": dict(
                                        x[0] for x in cert.get("issuer", [])
                                    ),
                                    "not_before": cert.get("notBefore"),
                                    "not_after": cert.get("notAfter"),
                                }
                                if cert
                                else None
                            ),
                        }
                else:
                    return {
                        "success": True,
                        "host": host,
                        "port": port,
                        "ssl_version": "None (plain connection)",
                        "cipher": None,
                        "certificate": None,
                    }

        except Exception as e:
            return {"success": False, "host": host, "port": port, "error": str(e)}


class FirewallManager:
    """Firewall and network access control."""

    def __init__(self):
        self.blocked_ips = set()
        self.allowed_ips = set()
        self.blocked_ports = set()
        self.allowed_ports = set()
        self.rules = []

        logger.info("Firewall manager initialized")

    def block_ip(self, ip: str, reason: str = "Manual block") -> bool:
        """Block an IP address."""
        try:
            self.blocked_ips.add(ip)
            self.rules.append(
                {
                    "type": "block_ip",
                    "target": ip,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Blocked IP: {ip} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error blocking IP {ip}: {e}")
            return False

    def allow_ip(self, ip: str, reason: str = "Manual allow") -> bool:
        """Allow an IP address."""
        try:
            self.allowed_ips.add(ip)
            self.blocked_ips.discard(ip)  # Remove from blocked if present
            self.rules.append(
                {
                    "type": "allow_ip",
                    "target": ip,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Allowed IP: {ip} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error allowing IP {ip}: {e}")
            return False

    def block_port(self, port: int, reason: str = "Manual block") -> bool:
        """Block a port."""
        try:
            self.blocked_ports.add(port)
            self.rules.append(
                {
                    "type": "block_port",
                    "target": port,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Blocked port: {port} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error blocking port {port}: {e}")
            return False

    def allow_port(self, port: int, reason: str = "Manual allow") -> bool:
        """Allow a port."""
        try:
            self.allowed_ports.add(port)
            self.blocked_ports.discard(port)  # Remove from blocked if present
            self.rules.append(
                {
                    "type": "allow_port",
                    "target": port,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            logger.info(f"Allowed port: {port} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error allowing port {port}: {e}")
            return False

    def is_ip_allowed(self, ip: str) -> bool:
        """Check if an IP is allowed."""
        if ip in self.blocked_ips:
            return False
        if ip in self.allowed_ips:
            return True
        return True  # Default to allowed if not explicitly blocked

    def is_port_allowed(self, port: int) -> bool:
        """Check if a port is allowed."""
        if port in self.blocked_ports:
            return False
        if port in self.allowed_ports:
            return True
        return True  # Default to allowed if not explicitly blocked

    def get_firewall_status(self) -> Dict[str, Any]:
        """Get firewall status and rules."""
        return {
            "blocked_ips": list(self.blocked_ips),
            "allowed_ips": list(self.allowed_ips),
            "blocked_ports": list(self.blocked_ports),
            "allowed_ports": list(self.allowed_ports),
            "total_rules": len(self.rules),
            "recent_rules": self.rules[-10:] if self.rules else [],
        }

    def test_network_connectivity(
        self, host: str, port: int, timeout: int = 5
    ) -> Dict[str, Any]:
        """Test network connectivity to a host and port."""
        start_time = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds

            return {
                "host": host,
                "port": port,
                "connected": result == 0,
                "response_time_ms": round(response_time, 2),
                "timeout": timeout,
                "error_code": result if result != 0 else None,
            }

        except socket.timeout:
            return {
                "host": host,
                "port": port,
                "connected": False,
                "error": "timeout",
                "timeout": timeout,
            }
        except Exception as e:
            return {
                "host": host,
                "port": port,
                "connected": False,
                "error": str(e),
                "timeout": timeout,
            }


# Global instances
network_monitor = NetworkMonitor()
ssl_config = SSLConfig()
firewall_manager = FirewallManager()
