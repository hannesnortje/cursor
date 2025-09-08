"""Rate limiting implementation for AI Agent System."""

import time
import threading
from typing import Dict, Any, Optional
from collections import defaultdict, deque
import os
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting implementation with multiple strategies."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.limits = self._load_rate_limits()
        self.windows = defaultdict(lambda: deque())
        self.lock = threading.RLock()
        
        # Load configuration from environment
        self.default_limit = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100"))
        self.burst_size = int(os.getenv("RATE_LIMIT_BURST_SIZE", "20"))
        self.window_size = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    def _load_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Load rate limits configuration."""
        return {
            "general": {
                "requests_per_minute": int(os.getenv("RATE_LIMIT_GENERAL", "100")),
                "burst_size": int(os.getenv("RATE_LIMIT_GENERAL_BURST", "20"))
            },
            "mcp_tools": {
                "requests_per_minute": int(os.getenv("RATE_LIMIT_MCP_TOOLS", "50")),
                "burst_size": int(os.getenv("RATE_LIMIT_MCP_TOOLS_BURST", "10"))
            },
            "authentication": {
                "requests_per_minute": int(os.getenv("RATE_LIMIT_AUTH", "10")),
                "burst_size": int(os.getenv("RATE_LIMIT_AUTH_BURST", "3"))
            },
            "file_operations": {
                "requests_per_minute": int(os.getenv("RATE_LIMIT_FILES", "20")),
                "burst_size": int(os.getenv("RATE_LIMIT_FILES_BURST", "5"))
            },
            "api_endpoints": {
                "requests_per_minute": int(os.getenv("RATE_LIMIT_API", "200")),
                "burst_size": int(os.getenv("RATE_LIMIT_API_BURST", "50"))
            }
        }
    
    def is_allowed(self, 
                   client_id: str, 
                   endpoint_type: str = "general",
                   custom_limit: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """
        Check if request is allowed based on rate limits.
        
        Args:
            client_id: Unique identifier for the client
            endpoint_type: Type of endpoint (general, mcp_tools, auth, etc.)
            custom_limit: Custom rate limit configuration
            
        Returns:
            Dict with allowed status and rate limit info
        """
        with self.lock:
            current_time = time.time()
            
            # Use custom limit if provided, otherwise use configured limit
            if custom_limit:
                limit_config = custom_limit
            else:
                limit_config = self.limits.get(endpoint_type, self.limits["general"])
            
            requests_per_minute = limit_config["requests_per_minute"]
            burst_size = limit_config["burst_size"]
            
            # Get or create window for this client and endpoint
            window_key = f"{client_id}:{endpoint_type}"
            window = self.windows[window_key]
            
            # Clean old requests outside the window
            cutoff_time = current_time - self.window_size
            while window and window[0] < cutoff_time:
                window.popleft()
            
            # Check if request is allowed
            current_requests = len(window)
            
            # Allow if under the limit
            if current_requests < requests_per_minute:
                # Add current request
                window.append(current_time)
                
                return {
                    "allowed": True,
                    "remaining": requests_per_minute - current_requests - 1,
                    "reset_time": current_time + self.window_size,
                    "limit": requests_per_minute,
                    "current": current_requests + 1
                }
            
            # Check burst allowance
            recent_requests = sum(1 for req_time in window if req_time > current_time - 10)  # Last 10 seconds
            if recent_requests < burst_size:
                window.append(current_time)
                
                return {
                    "allowed": True,
                    "remaining": 0,
                    "reset_time": current_time + self.window_size,
                    "limit": requests_per_minute,
                    "current": current_requests + 1,
                    "burst_used": True
                }
            
            # Request denied
            return {
                "allowed": False,
                "remaining": 0,
                "reset_time": window[0] + self.window_size if window else current_time + self.window_size,
                "limit": requests_per_minute,
                "current": current_requests,
                "reason": "rate_limit_exceeded"
            }
    
    def get_rate_limit_headers(self, 
                              client_id: str, 
                              endpoint_type: str = "general") -> Dict[str, str]:
        """Get rate limit headers for response."""
        result = self.is_allowed(client_id, endpoint_type)
        
        headers = {
            "X-RateLimit-Limit": str(result["limit"]),
            "X-RateLimit-Remaining": str(result["remaining"]),
            "X-RateLimit-Reset": str(int(result["reset_time"]))
        }
        
        if not result["allowed"]:
            headers["X-RateLimit-Retry-After"] = str(int(result["reset_time"] - time.time()))
        
        return headers
    
    def cleanup_old_windows(self):
        """Clean up old rate limit windows to prevent memory leaks."""
        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - (self.window_size * 2)  # Keep 2x window size
            
            # Remove old windows
            keys_to_remove = []
            for window_key, window in self.windows.items():
                if not window or window[-1] < cutoff_time:
                    keys_to_remove.append(window_key)
            
            for key in keys_to_remove:
                del self.windows[key]
            
            logger.debug(f"Cleaned up {len(keys_to_remove)} old rate limit windows")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        with self.lock:
            current_time = time.time()
            active_windows = 0
            total_requests = 0
            
            for window in self.windows.values():
                if window:
                    active_windows += 1
                    total_requests += len(window)
            
            return {
                "active_windows": active_windows,
                "total_requests": total_requests,
                "window_size_seconds": self.window_size,
                "configured_limits": self.limits,
                "cleanup_needed": len(self.windows) > 1000  # Flag for cleanup if too many windows
            }
    
    def reset_client(self, client_id: str, endpoint_type: str = None):
        """Reset rate limits for a specific client."""
        with self.lock:
            if endpoint_type:
                window_key = f"{client_id}:{endpoint_type}"
                if window_key in self.windows:
                    del self.windows[window_key]
            else:
                # Reset all windows for this client
                keys_to_remove = [key for key in self.windows.keys() if key.startswith(f"{client_id}:")]
                for key in keys_to_remove:
                    del self.windows[key]
    
    def update_limits(self, endpoint_type: str, new_limits: Dict[str, int]):
        """Update rate limits for a specific endpoint type."""
        with self.lock:
            self.limits[endpoint_type] = new_limits
            logger.info(f"Updated rate limits for {endpoint_type}: {new_limits}")
    
    def is_ddos_attack(self, client_id: str, threshold: int = 100) -> bool:
        """Detect potential DDoS attack from a client."""
        with self.lock:
            # Check total requests across all endpoint types for this client
            total_requests = 0
            for window_key, window in self.windows.items():
                if window_key.startswith(f"{client_id}:"):
                    total_requests += len(window)
            
            return total_requests > threshold


# Global rate limiter instance
rate_limiter = RateLimiter()
