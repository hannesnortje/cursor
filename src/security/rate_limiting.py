"""Rate limiting implementation for AI Agent System."""

import time
import threading
import os
import logging
from collections import defaultdict, deque
from typing import Dict, Any, List

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

        logger.info(
            f"Rate limiter initialized - default: {self.default_limit}/min, burst: {self.burst_size}"
        )

    def _load_rate_limits(self) -> Dict[str, Dict[str, int]]:
        """Load rate limits from environment configuration."""
        return {
            "general": {
                "requests_per_minute": int(
                    os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "100")
                ),
                "burst_size": int(os.getenv("RATE_LIMIT_BURST_SIZE", "20")),
            },
            "mcp_tools": {
                "requests_per_minute": int(
                    os.getenv("RATE_LIMIT_MCP_TOOLS_PER_MINUTE", "50")
                ),
                "burst_size": int(os.getenv("RATE_LIMIT_MCP_BURST_SIZE", "10")),
            },
            "authentication": {
                "requests_per_minute": int(
                    os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "10")
                ),
                "burst_size": int(os.getenv("RATE_LIMIT_AUTH_BURST_SIZE", "3")),
            },
        }

    def is_allowed(
        self, client_id: str, endpoint_type: str = "general"
    ) -> Dict[str, Any]:
        """Check if request is allowed for client and endpoint type."""
        with self.lock:
            now = time.time()
            window_key = f"{client_id}:{endpoint_type}"

            # Get limits for endpoint type
            limits = self.limits.get(endpoint_type, self.limits["general"])
            requests_per_minute = limits["requests_per_minute"]
            burst_size = limits["burst_size"]

            # Clean old requests (older than 1 minute)
            window = self.windows[window_key]
            cutoff_time = now - 60  # 1 minute ago

            while window and window[0] < cutoff_time:
                window.popleft()

            # Check if within limits
            current_count = len(window)

            if current_count >= requests_per_minute:
                return {
                    "allowed": False,
                    "reason": "rate_limit_exceeded",
                    "limit": requests_per_minute,
                    "current": current_count,
                    "remaining": 0,
                    "reset_time": window[0] + 60 if window else now + 60,
                }

            # Check burst protection
            if current_count >= burst_size:
                # Check if requests are coming too fast (within last 10 seconds)
                recent_requests = [
                    req_time for req_time in window if now - req_time < 10
                ]
                if len(recent_requests) >= burst_size:
                    return {
                        "allowed": False,
                        "reason": "burst_limit_exceeded",
                        "limit": burst_size,
                        "current": len(recent_requests),
                        "remaining": 0,
                        "reset_time": (
                            recent_requests[0] + 10 if recent_requests else now + 10
                        ),
                    }

            # Add current request
            window.append(now)

            return {
                "allowed": True,
                "reason": "allowed",
                "limit": requests_per_minute,
                "current": current_count + 1,
                "remaining": requests_per_minute - (current_count + 1),
                "reset_time": now + 60,
            }

    def get_statistics(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        with self.lock:
            now = time.time()
            active_windows = 0
            total_requests = 0

            for window in self.windows.values():
                # Count active requests (within last minute)
                cutoff_time = now - 60
                active_requests = sum(
                    1 for req_time in window if req_time > cutoff_time
                )
                if active_requests > 0:
                    active_windows += 1
                    total_requests += active_requests

            return {
                "active_windows": active_windows,
                "total_requests": total_requests,
                "limits": self.limits,
                "default_limit": self.default_limit,
                "burst_size": self.burst_size,
            }

    def reset_client(self, client_id: str, endpoint_type: str = "general") -> bool:
        """Reset rate limit for a specific client and endpoint."""
        with self.lock:
            window_key = f"{client_id}:{endpoint_type}"
            if window_key in self.windows:
                del self.windows[window_key]
                logger.info(
                    f"Rate limit reset for client {client_id} on {endpoint_type}"
                )
                return True
            return False

    def cleanup_old_windows(self) -> int:
        """Clean up old rate limit windows."""
        with self.lock:
            now = time.time()
            cutoff_time = now - 300  # 5 minutes ago
            windows_to_remove = []

            for window_key, window in self.windows.items():
                # Remove windows with no recent activity
                if not window or window[-1] < cutoff_time:
                    windows_to_remove.append(window_key)

            for window_key in windows_to_remove:
                del self.windows[window_key]

            if windows_to_remove:
                logger.info(
                    f"Cleaned up {len(windows_to_remove)} old rate limit windows"
                )

            return len(windows_to_remove)


# Global rate limiter instance
rate_limiter = RateLimiter()
