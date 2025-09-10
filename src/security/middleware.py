"""Security middleware for AI Agent System."""

import json
import time
import hashlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from .headers import SecurityHeaders
from .rate_limiting import rate_limiter

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for request processing and validation."""

    def __init__(self):
        """Initialize security middleware."""
        self.security_headers = SecurityHeaders()
        self.request_count = 0
        self.blocked_requests = 0
        self.security_events = []

        logger.info("Security middleware initialized")

    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and validate a request through security middleware."""
        self.request_count += 1

        # Extract request information
        method = request_data.get("method", "UNKNOWN")
        path = request_data.get("path", "/")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")

        # Generate client ID from request
        client_id = self._generate_client_id(request_data)

        # Initialize result
        result = {
            "allowed": True,
            "client_id": client_id,
            "method": method,
            "path": path,
            "rate_limit": {},
            "security_validation": {"issues": []},
            "ddos_detected": False,
            "timestamp": time.time(),
        }

        # Rate limiting check
        endpoint_type = self._determine_endpoint_type(path)
        rate_limit_result = rate_limiter.is_allowed(client_id, endpoint_type)
        result["rate_limit"] = rate_limit_result

        if not rate_limit_result["allowed"]:
            result["allowed"] = False
            self.blocked_requests += 1
            self._log_security_event(
                "rate_limit_exceeded",
                client_id,
                method,
                path,
                rate_limit_result["reason"],
            )
            return result

        # Security validation
        security_issues = self._validate_request_security(method, path, headers, body)
        result["security_validation"]["issues"] = security_issues

        if security_issues:
            result["allowed"] = False
            self.blocked_requests += 1
            self._log_security_event(
                "security_validation_failed",
                client_id,
                method,
                path,
                security_issues[0],
            )
            return result

        # DDoS detection
        if self._detect_ddos(client_id):
            result["ddos_detected"] = True
            result["allowed"] = False
            self.blocked_requests += 1
            self._log_security_event(
                "ddos_detected", client_id, method, path, "Potential DDoS attack"
            )
            return result

        # Log successful request
        self._log_security_event(
            "request", client_id, method, path, "Request processed successfully"
        )

        return result

    def _generate_client_id(self, request_data: Dict[str, Any]) -> str:
        """Generate a client ID from request data."""
        # Use a combination of headers and IP-like information
        headers = request_data.get("headers", {})
        user_agent = headers.get("User-Agent", "unknown")
        method = request_data.get("method", "unknown")
        path = request_data.get("path", "/")

        # Create a hash for client identification
        client_string = f"{user_agent}:{method}:{path}"
        return hashlib.md5(client_string.encode()).hexdigest()[:16]

    def _determine_endpoint_type(self, path: str) -> str:
        """Determine endpoint type for rate limiting."""
        if "/mcp/" in path or "tools/" in path:
            return "mcp_tools"
        elif "/auth/" in path or "/login" in path:
            return "authentication"
        else:
            return "general"

    def _validate_request_security(
        self, method: str, path: str, headers: Dict[str, str], body: str
    ) -> List[str]:
        """Validate request for security issues."""
        issues = []

        # Check for XSS attempts
        if self._detect_xss(body):
            issues.append("Potential XSS attack detected")

        # Check for SQL injection attempts
        if self._detect_sql_injection(body):
            issues.append("Potential SQL injection attack detected")

        # Check for path traversal attempts
        if self._detect_path_traversal(path):
            issues.append("Path traversal attempt detected")

        # Check for large request body
        if len(body) > 10 * 1024 * 1024:  # 10MB limit
            issues.append("Request body too large")

        return issues

    def _detect_xss(self, content: str) -> bool:
        """Detect potential XSS attacks."""
        xss_patterns = [
            "<script",
            "javascript:",
            "onload=",
            "onerror=",
            "onclick=",
            "onmouseover=",
            "vbscript:",
            "data:text/html",
        ]

        content_lower = content.lower()
        return any(pattern in content_lower for pattern in xss_patterns)

    def _detect_sql_injection(self, content: str) -> bool:
        """Detect potential SQL injection attacks."""
        sql_patterns = [
            "union select",
            "drop table",
            "delete from",
            "insert into",
            "update set",
            "or 1=1",
            "and 1=1",
            "' or '",
            '" or "',
            "'; --",
            '"; --',
        ]

        content_lower = content.lower()
        return any(pattern in content_lower for pattern in sql_patterns)

    def _detect_path_traversal(self, path: str) -> bool:
        """Detect path traversal attempts."""
        traversal_patterns = [
            "../",
            "..\\",
            "/etc/passwd",
            "/etc/shadow",
            "windows/system32",
            "boot.ini",
        ]

        return any(pattern in path for pattern in traversal_patterns)

    def _detect_ddos(self, client_id: str) -> bool:
        """Detect potential DDoS attacks."""
        # Simple DDoS detection based on request frequency
        # In a real implementation, this would be more sophisticated

        # Check if client has made too many requests recently
        recent_requests = [
            event
            for event in self.security_events
            if event.get("client_id") == client_id
            and time.time() - event.get("timestamp", 0) < 60  # Last minute
        ]

        return len(recent_requests) > 100  # More than 100 requests per minute

    def _log_security_event(
        self, event_type: str, client_id: str, method: str, path: str, description: str
    ):
        """Log a security event."""
        event = {
            "type": event_type,
            "client_id": client_id,
            "method": method,
            "path": path,
            "description": description,
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
        }

        self.security_events.append(event)

        # Keep only last 1000 events
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]

        # Log based on event type
        if event_type in [
            "rate_limit_exceeded",
            "security_validation_failed",
            "ddos_detected",
        ]:
            logger.warning(f"Security event: {event}")
        else:
            logger.info(f"Security event: {event}")

    def get_security_statistics(self) -> Dict[str, Any]:
        """Get security middleware statistics."""
        return {
            "total_requests": self.request_count,
            "blocked_requests": self.blocked_requests,
            "success_rate": (self.request_count - self.blocked_requests)
            / max(self.request_count, 1)
            * 100,
            "security_events": len(self.security_events),
            "recent_events": self.security_events[-10:] if self.security_events else [],
            "headers_configured": len(self.security_headers.get_headers()),
        }

    def get_security_headers(self) -> Dict[str, str]:
        """Get security headers."""
        return self.security_headers.get_headers()


# Global security middleware instance
security_middleware = SecurityMiddleware()
