#!/usr/bin/env python3
"""
Browser Manager Service
Handles automatic browser opening for dashboard instances
"""

import logging
import subprocess
import sys
import platform
import time
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class BrowserType(str, Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    CHROMIUM = "chromium"
    SAFARI = "safari"
    EDGE = "edge"
    OPERA = "opera"


@dataclass
class BrowserInfo:
    """Information about a detected browser."""
    name: str
    command: str
    args: List[str]
    browser_type: BrowserType
    available: bool = True
    priority: int = 0  # Lower number = higher priority


class BrowserManager:
    """Manages browser detection and opening for dashboard instances."""
    
    def __init__(self):
        self.detected_browsers: List[BrowserInfo] = []
        self.preferred_browser: Optional[BrowserInfo] = None
        self.system = platform.system().lower()
        
        # Initialize browser detection
        self._detect_browsers()
    
    def _detect_browsers(self):
        """Detect available browsers on the system."""
        logger.info("Detecting available browsers...")
        
        # Define browser configurations for different systems
        browser_configs = self._get_browser_configs()
        
        for config in browser_configs:
            if self._is_browser_available(config):
                self.detected_browsers.append(config)
                logger.info(f"✅ Found browser: {config.name}")
            else:
                logger.debug(f"❌ Browser not available: {config.name}")
        
        # Sort by priority
        self.detected_browsers.sort(key=lambda x: x.priority)
        
        if self.detected_browsers:
            self.preferred_browser = self.detected_browsers[0]
            logger.info(f"🎯 Preferred browser: {self.preferred_browser.name}")
        else:
            logger.warning("⚠️ No browsers detected")
    
    def _get_browser_configs(self) -> List[BrowserInfo]:
        """Get browser configurations based on the operating system."""
        if self.system == "linux":
            return [
                BrowserInfo(
                    name="Google Chrome",
                    command="google-chrome",
                    args=["--new-window", "--disable-web-security", "--disable-features=VizDisplayCompositor"],
                    browser_type=BrowserType.CHROME,
                    priority=1
                ),
                BrowserInfo(
                    name="Chromium",
                    command="chromium-browser",
                    args=["--new-window", "--disable-web-security"],
                    browser_type=BrowserType.CHROMIUM,
                    priority=2
                ),
                BrowserInfo(
                    name="Firefox",
                    command="firefox",
                    args=["-new-window"],
                    browser_type=BrowserType.FIREFOX,
                    priority=3
                ),
                BrowserInfo(
                    name="Opera",
                    command="opera",
                    args=["--new-window"],
                    browser_type=BrowserType.OPERA,
                    priority=4
                )
            ]
        elif self.system == "darwin":  # macOS
            return [
                BrowserInfo(
                    name="Google Chrome",
                    command="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                    args=["--new-window", "--disable-web-security"],
                    browser_type=BrowserType.CHROME,
                    priority=1
                ),
                BrowserInfo(
                    name="Safari",
                    command="open",
                    args=["-a", "Safari"],
                    browser_type=BrowserType.SAFARI,
                    priority=2
                ),
                BrowserInfo(
                    name="Firefox",
                    command="/Applications/Firefox.app/Contents/MacOS/firefox",
                    args=["-new-window"],
                    browser_type=BrowserType.FIREFOX,
                    priority=3
                ),
                BrowserInfo(
                    name="Edge",
                    command="/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                    args=["--new-window"],
                    browser_type=BrowserType.EDGE,
                    priority=4
                )
            ]
        elif self.system == "windows":
            return [
                BrowserInfo(
                    name="Google Chrome",
                    command="chrome",
                    args=["--new-window", "--disable-web-security"],
                    browser_type=BrowserType.CHROME,
                    priority=1
                ),
                BrowserInfo(
                    name="Microsoft Edge",
                    command="msedge",
                    args=["--new-window"],
                    browser_type=BrowserType.EDGE,
                    priority=2
                ),
                BrowserInfo(
                    name="Firefox",
                    command="firefox",
                    args=["-new-window"],
                    browser_type=BrowserType.FIREFOX,
                    priority=3
                ),
                BrowserInfo(
                    name="Opera",
                    command="opera",
                    args=["--new-window"],
                    browser_type=BrowserType.OPERA,
                    priority=4
                )
            ]
        else:
            logger.warning(f"Unsupported operating system: {self.system}")
            return []
    
    def _is_browser_available(self, browser_info: BrowserInfo) -> bool:
        """Check if a browser is available on the system."""
        try:
            # For macOS Safari, use 'open' command
            if browser_info.browser_type == BrowserType.SAFARI and self.system == "darwin":
                result = subprocess.run(
                    ["which", "open"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.returncode == 0
            
            # For other browsers, check if command exists
            result = subprocess.run(
                ["which", browser_info.command] if self.system != "windows" else ["where", browser_info.command],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def open_dashboard(self, url: str, instance_id: str = None, browser_type: Optional[BrowserType] = None) -> bool:
        """
        Open a dashboard URL in a browser.
        
        Args:
            url: Dashboard URL to open
            instance_id: Optional instance ID for logging
            browser_type: Optional specific browser to use
            
        Returns:
            True if browser opened successfully
        """
        try:
            # Select browser
            browser = self._select_browser(browser_type)
            if not browser:
                logger.error("No browser available to open dashboard")
                return False
            
            # Prepare command
            command = [browser.command] + browser.args + [url]
            
            # Special handling for macOS Safari
            if browser.browser_type == BrowserType.SAFARI and self.system == "darwin":
                command = ["open", "-a", "Safari", url]
            
            # Open browser
            logger.info(f"Opening dashboard in {browser.name}: {url}")
            if instance_id:
                logger.info(f"Dashboard for instance {instance_id} opening in {browser.name}")
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent process
            )
            
            # Give browser time to start
            time.sleep(1)
            
            # Check if process started successfully
            if process.poll() is None:
                logger.info(f"✅ Dashboard opened successfully in {browser.name}")
                return True
            else:
                logger.error(f"❌ Failed to open dashboard in {browser.name}")
                return False
                
        except Exception as e:
            logger.error(f"Error opening dashboard: {e}")
            return False
    
    def _select_browser(self, browser_type: Optional[BrowserType] = None) -> Optional[BrowserInfo]:
        """Select browser to use."""
        if browser_type:
            # Find specific browser type
            for browser in self.detected_browsers:
                if browser.browser_type == browser_type and browser.available:
                    return browser
            logger.warning(f"Requested browser {browser_type} not available")
        
        # Return preferred browser
        return self.preferred_browser
    
    def get_available_browsers(self) -> List[Dict[str, Any]]:
        """Get list of available browsers."""
        return [
            {
                "name": browser.name,
                "type": browser.browser_type.value,
                "command": browser.command,
                "priority": browser.priority,
                "available": browser.available
            }
            for browser in self.detected_browsers
        ]
    
    def get_browser_status(self) -> Dict[str, Any]:
        """Get browser manager status."""
        return {
            "system": self.system,
            "total_browsers": len(self.detected_browsers),
            "preferred_browser": self.preferred_browser.name if self.preferred_browser else None,
            "available_browsers": self.get_available_browsers(),
            "timestamp": time.time()
        }
    
    def test_browser_opening(self, test_url: str = "https://www.google.com") -> Dict[str, Any]:
        """Test browser opening functionality."""
        results = {}
        
        for browser in self.detected_browsers:
            try:
                logger.info(f"Testing {browser.name}...")
                success = self.open_dashboard(test_url, browser_type=browser.browser_type)
                results[browser.name] = {
                    "success": success,
                    "browser_type": browser.browser_type.value
                }
                
                if success:
                    # Close the test tab after a short delay
                    time.sleep(2)
                    
            except Exception as e:
                results[browser.name] = {
                    "success": False,
                    "error": str(e),
                    "browser_type": browser.browser_type.value
                }
        
        return results


# Global browser manager instance
_browser_manager: Optional[BrowserManager] = None


def get_browser_manager() -> BrowserManager:
    """Get global browser manager instance."""
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager


def open_dashboard_in_browser(url: str, instance_id: str = None, browser_type: Optional[BrowserType] = None) -> bool:
    """Open dashboard in browser using global browser manager."""
    return get_browser_manager().open_dashboard(url, instance_id, browser_type)


def get_browser_status() -> Dict[str, Any]:
    """Get browser status using global browser manager."""
    return get_browser_manager().get_browser_status()
