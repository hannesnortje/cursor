"""Security middleware for AI Agent System."""

import time
import logging
from typing import Dict, Any, Optional, Callable
from .headers import SecurityHeaders
from .rate_limiting import rate_limiter

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Security middleware for HTTP requests and responses."""
    
    def __init__(self):
        """Initialize security middleware."""
        self.security_headers = SecurityHeaders()
        self.rate_limiter = rate_limiter
        self.request_count = 0
        self.start_time = time.time()
        
        # Security event logging
        self.security_events = []
        self.max_events = 1000  # Keep last 1000 security events
    
    def process_request(self, 
                       request_data: Dict[str, Any],
                       client_id: str = None) -> Dict[str, Any]:
        """
        Process incoming request for security checks.
        
        Args:
            request_data: Request data dictionary
            client_id: Client identifier for rate limiting
            
        Returns:
            Dict with security processing results
        """
        start_time = time.time()
        self.request_count += 1
        
        # Extract request information
        method = request_data.get("method", "GET")
        path = request_data.get("path", "/")
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        
        # Generate client ID if not provided
        if not client_id:
            client_id = self._generate_client_id(request_data)
        
        # Determine endpoint type for rate limiting
        endpoint_type = self._get_endpoint_type(path, method)
        
        # Rate limiting check
        rate_limit_result = self.rate_limiter.is_allowed(
            client_id=client_id,
            endpoint_type=endpoint_type
        )
        
        # Security validation
        security_validation = self._validate_request(request_data)
        
        # DDoS detection
        ddos_detected = self.rate_limiter.is_ddos_attack(client_id)
        
        # Log security event
        self._log_security_event({
            "type": "request",
            "client_id": client_id,
            "method": method,
            "path": path,
            "rate_limited": not rate_limit_result["allowed"],
            "ddos_detected": ddos_detected,
            "security_issues": security_validation["issues"],
            "timestamp": time.time()
        })
        
        processing_time = time.time() - start_time
        
        return {
            "allowed": rate_limit_result["allowed"] and not ddos_detected and security_validation["valid"],
            "client_id": client_id,
            "endpoint_type": endpoint_type,
            "rate_limit": rate_limit_result,
            "security_validation": security_validation,
            "ddos_detected": ddos_detected,
            "processing_time": processing_time,
            "request_number": self.request_count
        }
    
    def process_response(self, 
                        response_data: Dict[str, Any],
                        request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process outgoing response to add security headers.
        
        Args:
            response_data: Response data dictionary
            request_info: Request processing information
            
        Returns:
            Dict with enhanced response data
        """
        start_time = time.time()
        
        # Get security headers
        security_headers = self.security_headers.get_headers()
        
        # Add rate limit headers
        rate_limit_headers = self.rate_limiter.get_rate_limit_headers(
            client_id=request_info.get("client_id", "unknown"),
            endpoint_type=request_info.get("endpoint_type", "general")
        )
        
        # Add response time header
        response_time = time.time() - start_time
        security_headers["X-Response-Time"] = f"{response_time:.3f}s"
        
        # Combine all headers
        all_headers = {**security_headers, **rate_limit_headers}
        
        # Update response data
        response_data["headers"] = {**response_data.get("headers", {}), **all_headers}
        
        # Log response security event
        self._log_security_event({
            "type": "response",
            "client_id": request_info.get("client_id"),
            "status_code": response_data.get("status_code", 200),
            "response_time": response_time,
            "headers_added": len(all_headers),
            "timestamp": time.time()
        })
        
        return response_data
    
    def _generate_client_id(self, request_data: Dict[str, Any]) -> str:
        """Generate a client ID from request data."""
        headers = request_data.get("headers", {})
        
        # Try to get client IP from various headers
        client_ip = (
            headers.get("X-Forwarded-For", "").split(",")[0].strip() or
            headers.get("X-Real-IP", "") or
            headers.get("Remote-Addr", "") or
            "unknown"
        )
        
        # Add user agent for additional uniqueness
        user_agent = headers.get("User-Agent", "unknown")
        
        # Create a simple hash-based ID
        import hashlib
        client_string = f"{client_ip}:{user_agent}"
        client_id = hashlib.md5(client_string.encode()).hexdigest()[:16]
        
        return client_id
    
    def _get_endpoint_type(self, path: str, method: str) -> str:
        """Determine endpoint type for rate limiting."""
        path_lower = path.lower()
        
        if "/mcp/" in path_lower or "mcp" in path_lower:
            return "mcp_tools"
        elif "/auth" in path_lower or "/login" in path_lower:
            return "authentication"
        elif "/files" in path_lower or "/upload" in path_lower:
            return "file_operations"
        elif "/api/" in path_lower:
            return "api_endpoints"
        else:
            return "general"
    
    def _validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate request for security issues."""
        issues = []
        warnings = []
        
        headers = request_data.get("headers", {})
        body = request_data.get("body", "")
        path = request_data.get("path", "")
        
        # Check for suspicious headers
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Original-URL",
            "X-Rewrite-URL"
        ]
        
        for header in suspicious_headers:
            if header in headers:
                warnings.append(f"Suspicious header detected: {header}")
        
        # Check for path traversal attempts
        if ".." in path or "~" in path:
            issues.append("Path traversal attempt detected")
        
        # Check for SQL injection patterns in body
        sql_patterns = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        if any(pattern in str(body).lower() for pattern in sql_patterns):
            warnings.append("Potential SQL injection pattern detected")
        
        # Check for XSS patterns
        xss_patterns = ["<script", "javascript:", "onload=", "onerror="]
        if any(pattern in str(body).lower() for pattern in xss_patterns):
            issues.append("Potential XSS attack detected")
        
        # Check request size
        body_size = len(str(body))
        if body_size > 10 * 1024 * 1024:  # 10MB limit
            issues.append("Request body too large")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "body_size": body_size
        }
    
    def _log_security_event(self, event: Dict[str, Any]):
        """Log security event."""
        self.security_events.append(event)
        
        # Keep only recent events
        if len(self.security_events) > self.max_events:
            self.security_events = self.security_events[-self.max_events:]
        
        # Log to logger if it's a security issue
        if event.get("type") == "request" and (
            event.get("rate_limited") or 
            event.get("ddos_detected") or 
            event.get("security_issues")
        ):
            logger.warning(f"Security event: {event}")
    
    def get_security_statistics(self) -> Dict[str, Any]:
        """Get security middleware statistics."""
        uptime = time.time() - self.start_time
        
        # Count security events by type
        event_counts = {}
        for event in self.security_events:
            event_type = event.get("type", "unknown")
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Count security issues
        security_issues = sum(1 for event in self.security_events 
                            if event.get("rate_limited") or 
                               event.get("ddos_detected") or 
                               event.get("security_issues"))
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self.request_count,
            "requests_per_second": self.request_count / uptime if uptime > 0 else 0,
            "security_events": len(self.security_events),
            "security_issues": security_issues,
            "event_counts": event_counts,
            "rate_limiter_stats": self.rate_limiter.get_statistics(),
            "headers_validation": self.security_headers.validate_headers()
        }
    
    def cleanup(self):
        """Clean up middleware resources."""
        self.rate_limiter.cleanup_old_windows()
        
        # Clear old security events
        current_time = time.time()
        self.security_events = [
            event for event in self.security_events
            if current_time - event.get("timestamp", 0) < 3600  # Keep last hour
        ]


# Global security middleware instance
security_middleware = SecurityMiddleware()
