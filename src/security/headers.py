"""Security headers implementation for AI Agent System."""

from typing import Dict, Any
import os


class SecurityHeaders:
    """Manages security headers for HTTP responses."""
    
    def __init__(self):
        """Initialize security headers configuration."""
        self.headers = self._get_default_headers()
        self._load_custom_config()
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default security headers."""
        return {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking attacks
            "X-Frame-Options": "DENY",
            
            # Enable XSS protection
            "X-XSS-Protection": "1; mode=block",
            
            # Force HTTPS (if enabled)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            
            # Content Security Policy
            "Content-Security-Policy": self._get_csp_policy(),
            
            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions policy
            "Permissions-Policy": self._get_permissions_policy(),
            
            # Cross-Origin policies
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
    
    def _get_csp_policy(self) -> str:
        """Get Content Security Policy."""
        # Allow self, localhost, and essential external resources
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Required for some MCP functionality
            "style-src 'self' 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' data:",
            "connect-src 'self' ws: wss: http: https:",
            "frame-ancestors 'none'",
            "base-uri 'self'",
            "form-action 'self'"
        ]
        
        # Add environment-specific policies
        if os.getenv("ENVIRONMENT") == "development":
            csp_directives.append("script-src 'self' 'unsafe-inline' 'unsafe-eval' localhost:*")
            csp_directives.append("connect-src 'self' ws: wss: http: https: localhost:*")
        
        return "; ".join(csp_directives)
    
    def _get_permissions_policy(self) -> str:
        """Get Permissions Policy."""
        # Restrict potentially dangerous features
        permissions = [
            "camera=()",
            "microphone=()",
            "geolocation=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "accelerometer=()",
            "gyroscope=()"
        ]
        
        # Allow clipboard for development
        if os.getenv("ENVIRONMENT") == "development":
            permissions.append("clipboard-read=()")
            permissions.append("clipboard-write=()")
        
        return ", ".join(permissions)
    
    def _load_custom_config(self):
        """Load custom security configuration from environment."""
        # Allow customization via environment variables
        custom_csp = os.getenv("CSP_POLICY")
        if custom_csp:
            self.headers["Content-Security-Policy"] = custom_csp
        
        custom_hsts = os.getenv("HSTS_MAX_AGE")
        if custom_hsts:
            self.headers["Strict-Transport-Security"] = f"max-age={custom_hsts}; includeSubDomains"
        
        # Disable HSTS in development
        if os.getenv("ENVIRONMENT") == "development":
            self.headers.pop("Strict-Transport-Security", None)
    
    def get_headers(self) -> Dict[str, str]:
        """Get all security headers."""
        return self.headers.copy()
    
    def get_header(self, name: str) -> str:
        """Get a specific security header."""
        return self.headers.get(name, "")
    
    def add_header(self, name: str, value: str):
        """Add or update a security header."""
        self.headers[name] = value
    
    def remove_header(self, name: str):
        """Remove a security header."""
        self.headers.pop(name, None)
    
    def update_headers(self, headers: Dict[str, str]):
        """Update multiple headers at once."""
        self.headers.update(headers)
    
    def get_cors_headers(self) -> Dict[str, str]:
        """Get CORS-specific headers."""
        return {
            "Access-Control-Allow-Origin": os.getenv("CORS_ORIGIN", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "86400"
        }
    
    def get_api_headers(self) -> Dict[str, str]:
        """Get API-specific security headers."""
        api_headers = self.get_headers()
        api_headers.update({
            "X-API-Version": "1.0",
            "X-Response-Time": "",  # Will be set by middleware
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        })
        return api_headers
    
    def validate_headers(self) -> Dict[str, Any]:
        """Validate security headers configuration."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check for missing critical headers
        critical_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy"
        ]
        
        for header in critical_headers:
            if header not in self.headers:
                validation_result["errors"].append(f"Missing critical header: {header}")
                validation_result["valid"] = False
        
        # Check CSP policy
        csp = self.headers.get("Content-Security-Policy", "")
        if "'unsafe-inline'" in csp and "'unsafe-eval'" in csp:
            validation_result["warnings"].append("CSP contains unsafe directives")
            validation_result["recommendations"].append("Consider removing 'unsafe-inline' and 'unsafe-eval' for production")
        
        # Check HSTS in development
        if os.getenv("ENVIRONMENT") == "development" and "Strict-Transport-Security" in self.headers:
            validation_result["warnings"].append("HSTS enabled in development environment")
        
        return validation_result
