"""Security headers implementation for AI Agent System."""

import os
from typing import Dict, Any, List


class SecurityHeaders:
    """Security headers management for HTTP responses."""

    def __init__(self):
        """Initialize security headers."""
        self.headers = self._load_security_headers()

    def _load_security_headers(self) -> Dict[str, str]:
        """Load security headers from environment configuration."""
        return {
            # Content Security Policy
            "Content-Security-Policy": os.getenv(
                "CSP_HEADER",
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self'",
            ),
            # XSS Protection
            "X-XSS-Protection": os.getenv("XSS_PROTECTION_HEADER", "1; mode=block"),
            # Content Type Options
            "X-Content-Type-Options": os.getenv(
                "CONTENT_TYPE_OPTIONS_HEADER", "nosniff"
            ),
            # Frame Options
            "X-Frame-Options": os.getenv("FRAME_OPTIONS_HEADER", "DENY"),
            # Strict Transport Security
            "Strict-Transport-Security": os.getenv(
                "HSTS_HEADER", "max-age=31536000; includeSubDomains; preload"
            ),
            # Referrer Policy
            "Referrer-Policy": os.getenv(
                "REFERRER_POLICY_HEADER", "strict-origin-when-cross-origin"
            ),
            # Cross-Origin Policies
            "Cross-Origin-Embedder-Policy": os.getenv("COEP_HEADER", "require-corp"),
            "Cross-Origin-Opener-Policy": os.getenv("COOP_HEADER", "same-origin"),
            "Cross-Origin-Resource-Policy": os.getenv("CORP_HEADER", "same-origin"),
            # Permissions Policy
            "Permissions-Policy": os.getenv(
                "PERMISSIONS_POLICY_HEADER",
                "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), speaker=()",
            ),
        }

    def get_headers(self) -> Dict[str, str]:
        """Get all security headers."""
        return self.headers.copy()

    def get_header(self, name: str) -> str:
        """Get a specific security header."""
        return self.headers.get(name, "")

    def validate_headers(self) -> Dict[str, Any]:
        """Validate security headers configuration."""
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": [],
            "header_count": len(self.headers),
        }

        # Check for required headers
        required_headers = [
            "X-XSS-Protection",
            "X-Content-Type-Options",
            "X-Frame-Options",
        ]

        for header in required_headers:
            if header not in self.headers or not self.headers[header]:
                validation_result["issues"].append(f"Missing required header: {header}")
                validation_result["valid"] = False

        # Check CSP header
        if "Content-Security-Policy" not in self.headers:
            validation_result["recommendations"].append(
                "Consider adding Content-Security-Policy header"
            )

        # Check HSTS header
        if "Strict-Transport-Security" not in self.headers:
            validation_result["recommendations"].append(
                "Consider adding Strict-Transport-Security header for HTTPS"
            )

        return validation_result

    def add_header(self, name: str, value: str):
        """Add or update a security header."""
        self.headers[name] = value

    def remove_header(self, name: str):
        """Remove a security header."""
        if name in self.headers:
            del self.headers[name]
