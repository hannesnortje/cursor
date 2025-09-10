#!/usr/bin/env python3
"""
Browser Configuration
Configuration options for browser integration
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class BrowserAutoOpenMode(str, Enum):
    """Browser auto-open modes."""

    ALWAYS = "always"  # Always open browser
    FIRST_INSTANCE = "first_instance"  # Only open for first instance
    NEVER = "never"  # Never open browser automatically
    PROMPT = "prompt"  # Prompt user before opening


@dataclass
class BrowserConfig:
    """Browser configuration settings."""

    # Auto-open settings
    auto_open_mode: BrowserAutoOpenMode = BrowserAutoOpenMode.ALWAYS
    auto_open_delay: float = 2.0  # Delay before opening browser (seconds)

    # Browser preferences
    preferred_browser: Optional[str] = None  # Preferred browser name
    browser_args: Dict[str, Any] = None  # Additional browser arguments

    # Dashboard settings
    dashboard_title_prefix: str = "AI Agent Dashboard"
    show_instance_info: bool = True

    # Security settings
    disable_web_security: bool = True  # For development
    allow_insecure_content: bool = True  # For development

    def __post_init__(self):
        if self.browser_args is None:
            self.browser_args = {}


def load_browser_config() -> BrowserConfig:
    """Load browser configuration from environment variables."""
    config = BrowserConfig()

    # Auto-open mode
    auto_open_mode = os.environ.get("BROWSER_AUTO_OPEN_MODE", "always").lower()
    try:
        config.auto_open_mode = BrowserAutoOpenMode(auto_open_mode)
    except ValueError:
        config.auto_open_mode = BrowserAutoOpenMode.ALWAYS

    # Auto-open delay
    try:
        config.auto_open_delay = float(os.environ.get("BROWSER_AUTO_OPEN_DELAY", "2.0"))
    except ValueError:
        config.auto_open_delay = 2.0

    # Preferred browser
    config.preferred_browser = os.environ.get("PREFERRED_BROWSER")

    # Dashboard settings
    config.dashboard_title_prefix = os.environ.get(
        "DASHBOARD_TITLE_PREFIX", "AI Agent Dashboard"
    )
    config.show_instance_info = (
        os.environ.get("SHOW_INSTANCE_INFO", "true").lower() == "true"
    )

    # Security settings
    config.disable_web_security = (
        os.environ.get("DISABLE_WEB_SECURITY", "true").lower() == "true"
    )
    config.allow_insecure_content = (
        os.environ.get("ALLOW_INSECURE_CONTENT", "true").lower() == "true"
    )

    return config


# Global configuration instance
_browser_config: Optional[BrowserConfig] = None


def get_browser_config() -> BrowserConfig:
    """Get global browser configuration."""
    global _browser_config
    if _browser_config is None:
        _browser_config = load_browser_config()
    return _browser_config


def should_auto_open_browser(instance_count: int = 1) -> bool:
    """Determine if browser should be opened automatically."""
    config = get_browser_config()

    if config.auto_open_mode == BrowserAutoOpenMode.NEVER:
        return False
    elif config.auto_open_mode == BrowserAutoOpenMode.ALWAYS:
        return True
    elif config.auto_open_mode == BrowserAutoOpenMode.FIRST_INSTANCE:
        return instance_count == 1
    elif config.auto_open_mode == BrowserAutoOpenMode.PROMPT:
        # For now, default to True. In a full implementation, this would prompt the user
        return True

    return True
