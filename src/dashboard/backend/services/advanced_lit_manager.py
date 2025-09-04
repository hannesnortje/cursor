"""
Advanced Lit Manager Service
Enhanced version with automatic updates, version management, and monitoring
"""

import asyncio
import aiohttp
import json
import time
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class UpdateStatus(Enum):
    """Update status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class VersionInfo:
    """Version information data class"""
    version: str
    etag: str
    size: int
    download_time: datetime
    checksum: str
    source_url: str
    is_active: bool = False
    performance_score: float = 0.0
    error_count: int = 0

@dataclass
class UpdateEvent:
    """Update event data class"""
    timestamp: datetime
    event_type: str
    version: str
    status: UpdateStatus
    message: str
    details: Dict[str, Any] = None

class AdvancedLitManager:
    """Advanced Lit Manager with automatic updates and monitoring"""
    
    def __init__(self, base_path: str = None):
        if base_path is None:
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent.parent
            base_path = project_root / "dashboard" / "frontend" / "lib"
        
        self.base_path = Path(base_path)
        self.lib_path = self.base_path / "lit"
        self.versions_path = self.lib_path / "versions"
        self.current_path = self.lib_path / "current"
        self.metrics_file = self.lib_path / "metrics.json"
        self.events_file = self.lib_path / "events.json"
        
        # CDN sources with priority and health status
        self.cdn_sources = [
            {
                "url": "https://cdn.jsdelivr.net/gh/lit/dist@3/core/lit-core.min.js",
                "priority": 1,
                "healthy": True,
                "last_check": None,
                "response_time": 0.0,
                "error_count": 0
            },
            {
                "url": "https://unpkg.com/lit@3/index.js",
                "priority": 2,
                "healthy": True,
                "last_check": None,
                "response_time": 0.0,
                "error_count": 0
            },
            {
                "url": "https://cdn.skypack.dev/lit@3",
                "priority": 3,
                "healthy": True,
                "last_check": None,
                "response_time": 0.0,
                "error_count": 0
            }
        ]
        
        # Configuration
        self.update_check_interval = 24 * 60 * 60  # 24 hours
        self.health_check_interval = 60 * 60  # 1 hour
        self.max_versions = 5  # Keep last 5 versions
        self.circuit_breaker_threshold = 5  # Mark source unhealthy after 5 errors
        self.circuit_breaker_timeout = 30 * 60  # 30 minutes
        
        # State
        self.current_version: Optional[VersionInfo] = None
        self.update_task: Optional[asyncio.Task] = None
        self.health_check_task: Optional[asyncio.Task] = None
        self.last_update_check = None
        self.update_in_progress = False
        
        # Metrics
        self.metrics = {
            "total_downloads": 0,
            "successful_downloads": 0,
            "failed_downloads": 0,
            "total_updates": 0,
            "successful_updates": 0,
            "failed_updates": 0,
            "rollbacks": 0,
            "average_download_time": 0.0,
            "last_update": None,
            "uptime_start": datetime.now()
        }
        
        # Events log
        self.events: List[UpdateEvent] = []
        
        # Ensure directories exist
        self.lib_path.mkdir(parents=True, exist_ok=True)
        self.versions_path.mkdir(parents=True, exist_ok=True)
        self.current_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._load_metrics()
        self._load_events()
        self._load_current_version()
    
    def _load_metrics(self):
        """Load metrics from file"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                    # Convert timestamp strings back to datetime
                    if data.get('last_update'):
                        data['last_update'] = datetime.fromisoformat(data['last_update'])
                    if data.get('uptime_start'):
                        data['uptime_start'] = datetime.fromisoformat(data['uptime_start'])
                    self.metrics.update(data)
            except Exception as e:
                logger.warning(f"Failed to load metrics: {e}")
    
    def _save_metrics(self):
        """Save metrics to file"""
        try:
            data = self.metrics.copy()
            # Convert datetime objects to strings
            if data.get('last_update'):
                data['last_update'] = data['last_update'].isoformat()
            if data.get('uptime_start'):
                data['uptime_start'] = data['uptime_start'].isoformat()
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def _load_events(self):
        """Load events from file"""
        if self.events_file.exists():
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                    self.events = [
                        UpdateEvent(
                            timestamp=datetime.fromisoformat(event['timestamp']),
                            event_type=event['event_type'],
                            version=event['version'],
                            status=UpdateStatus(event['status']),
                            message=event['message'],
                            details=event.get('details', {})
                        )
                        for event in data
                    ]
            except Exception as e:
                logger.warning(f"Failed to load events: {e}")
    
    def _save_events(self):
        """Save events to file"""
        try:
            data = [
                {
                    'timestamp': event.timestamp.isoformat(),
                    'event_type': event.event_type,
                    'version': event.version,
                    'status': event.status.value,
                    'message': event.message,
                    'details': event.details or {}
                }
                for event in self.events[-100:]  # Keep last 100 events
            ]
            
            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save events: {e}")
    
    def _add_event(self, event_type: str, version: str, status: UpdateStatus, message: str, details: Dict[str, Any] = None):
        """Add an event to the log"""
        event = UpdateEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            version=version,
            status=status,
            message=message,
            details=details or {}
        )
        self.events.append(event)
        self._save_events()
        logger.info(f"Event: {event_type} - {message}")
    
    def _load_current_version(self):
        """Load current version information"""
        current_file = self.current_path / "version.json"
        if current_file.exists():
            try:
                with open(current_file, 'r') as f:
                    data = json.load(f)
                    self.current_version = VersionInfo(
                        version=data['version'],
                        etag=data['etag'],
                        size=data['size'],
                        download_time=datetime.fromisoformat(data['download_time']),
                        checksum=data['checksum'],
                        source_url=data['source_url'],
                        is_active=data.get('is_active', True),
                        performance_score=data.get('performance_score', 0.0),
                        error_count=data.get('error_count', 0)
                    )
            except Exception as e:
                logger.warning(f"Failed to load current version: {e}")
    
    def _save_current_version(self):
        """Save current version information"""
        if not self.current_version:
            return
        
        try:
            current_file = self.current_path / "version.json"
            data = {
                'version': self.current_version.version,
                'etag': self.current_version.etag,
                'size': self.current_version.size,
                'download_time': self.current_version.download_time.isoformat(),
                'checksum': self.current_version.checksum,
                'source_url': self.current_version.source_url,
                'is_active': self.current_version.is_active,
                'performance_score': self.current_version.performance_score,
                'error_count': self.current_version.error_count
            }
            
            with open(current_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save current version: {e}")
    
    async def _check_cdn_health(self, source: Dict[str, Any]) -> bool:
        """Check health of a CDN source"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.head(source['url'], timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_time = time.time() - start_time
                    source['response_time'] = response_time
                    source['last_check'] = datetime.now()
                    
                    if response.status == 200:
                        source['healthy'] = True
                        source['error_count'] = 0
                        return True
                    else:
                        source['healthy'] = False
                        source['error_count'] += 1
                        return False
        except Exception as e:
            source['healthy'] = False
            source['error_count'] += 1
            source['last_check'] = datetime.now()
            logger.warning(f"Health check failed for {source['url']}: {e}")
            return False
    
    async def _get_healthy_sources(self) -> List[Dict[str, Any]]:
        """Get list of healthy CDN sources sorted by priority"""
        healthy_sources = []
        
        for source in self.cdn_sources:
            # Check if source is in circuit breaker timeout
            if source['error_count'] >= self.circuit_breaker_threshold:
                if source['last_check']:
                    time_since_error = datetime.now() - source['last_check']
                    if time_since_error.total_seconds() < self.circuit_breaker_timeout:
                        continue  # Still in circuit breaker timeout
            
            # Perform health check if needed
            if (not source['last_check'] or 
                (datetime.now() - source['last_check']).total_seconds() > self.health_check_interval):
                await self._check_cdn_health(source)
            
            if source['healthy']:
                healthy_sources.append(source)
        
        # Sort by priority (lower number = higher priority)
        return sorted(healthy_sources, key=lambda x: x['priority'])
    
    async def _download_from_source(self, source: Dict[str, Any]) -> Tuple[bool, Optional[VersionInfo]]:
        """Download Lit 3 from a specific source"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(source['url'], timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    
                    content = await response.read()
                    download_time = time.time() - start_time
                    
                    # Calculate checksum
                    checksum = hashlib.sha256(content).hexdigest()
                    
                    # Get ETag from headers
                    etag = response.headers.get('ETag', f'"{checksum[:16]}"')
                    
                    # Create version info
                    version_info = VersionInfo(
                        version=etag,
                        etag=etag,
                        size=len(content),
                        download_time=datetime.now(),
                        checksum=checksum,
                        source_url=source['url'],
                        is_active=False,
                        performance_score=1.0 / (download_time + 0.1)  # Higher score for faster downloads
                    )
                    
                    # Save to versions directory (sanitize version for filesystem)
                    safe_version = version_info.version.replace('"', '').replace('/', '_').replace('\\', '_')
                    version_dir = self.versions_path / safe_version
                    version_dir.mkdir(exist_ok=True)
                    
                    with open(version_dir / "lit-core.min.js", 'wb') as f:
                        f.write(content)
                    
                    with open(version_dir / "version.json", 'w') as f:
                        json.dump(asdict(version_info), f, indent=2, default=str)
                    
                    # Update metrics
                    self.metrics['total_downloads'] += 1
                    self.metrics['successful_downloads'] += 1
                    self.metrics['average_download_time'] = (
                        (self.metrics['average_download_time'] * (self.metrics['successful_downloads'] - 1) + download_time) /
                        self.metrics['successful_downloads']
                    )
                    
                    self._add_event(
                        "download_success",
                        version_info.version,
                        UpdateStatus.COMPLETED,
                        f"Successfully downloaded from {source['url']}",
                        {"download_time": download_time, "size": version_info.size}
                    )
                    
                    return True, version_info
                    
        except Exception as e:
            self.metrics['total_downloads'] += 1
            self.metrics['failed_downloads'] += 1
            
            self._add_event(
                "download_failed",
                "unknown",
                UpdateStatus.FAILED,
                f"Failed to download from {source['url']}: {str(e)}"
            )
            
            logger.error(f"Download failed from {source['url']}: {e}")
            return False, None
    
    async def _check_for_updates(self) -> bool:
        """Check if updates are available"""
        try:
            healthy_sources = await self._get_healthy_sources()
            if not healthy_sources:
                logger.warning("No healthy CDN sources available")
                return False
            
            # Try to get latest version info from highest priority source
            source = healthy_sources[0]
            async with aiohttp.ClientSession() as session:
                async with session.head(source['url'], timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        latest_etag = response.headers.get('ETag', '')
                        if latest_etag and latest_etag != self.current_version.version:
                            logger.info(f"Update available: {self.current_version.version} -> {latest_etag}")
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Update check failed: {e}")
            return False
    
    async def _perform_update(self) -> bool:
        """Perform automatic update"""
        if self.update_in_progress:
            logger.info("Update already in progress")
            return False
        
        self.update_in_progress = True
        self.metrics['total_updates'] += 1
        
        try:
            self._add_event(
                "update_started",
                "unknown",
                UpdateStatus.IN_PROGRESS,
                "Starting automatic update"
            )
            
            healthy_sources = await self._get_healthy_sources()
            if not healthy_sources:
                raise Exception("No healthy CDN sources available")
            
            # Try each source in order of priority
            for source in healthy_sources:
                success, version_info = await self._download_from_source(source)
                if success and version_info:
                    # Activate new version
                    await self._activate_version(version_info)
                    
                    self.metrics['successful_updates'] += 1
                    self.metrics['last_update'] = datetime.now()
                    
                    self._add_event(
                        "update_completed",
                        version_info.version,
                        UpdateStatus.COMPLETED,
                        f"Successfully updated to version {version_info.version}"
                    )
                    
                    return True
            
            raise Exception("All download sources failed")
            
        except Exception as e:
            self.metrics['failed_updates'] += 1
            
            self._add_event(
                "update_failed",
                "unknown",
                UpdateStatus.FAILED,
                f"Automatic update failed: {str(e)}"
            )
            
            logger.error(f"Automatic update failed: {e}")
            return False
            
        finally:
            self.update_in_progress = False
    
    async def _activate_version(self, version_info: VersionInfo):
        """Activate a specific version"""
        try:
            # Deactivate current version
            if self.current_version:
                self.current_version.is_active = False
                self._save_current_version()
            
            # Copy new version to current directory (sanitize version for filesystem)
            safe_version = version_info.version.replace('"', '').replace('/', '_').replace('\\', '_')
            version_dir = self.versions_path / safe_version
            current_js = self.current_path / "lit-core.min.js"
            current_json = self.current_path / "version.json"
            
            # Copy files
            import shutil
            shutil.copy2(version_dir / "lit-core.min.js", current_js)
            shutil.copy2(version_dir / "version.json", current_json)
            
            # Update current version
            version_info.is_active = True
            self.current_version = version_info
            self._save_current_version()
            
            # Clean up old versions
            await self._cleanup_old_versions()
            
            logger.info(f"Activated version {version_info.version}")
            
        except Exception as e:
            logger.error(f"Failed to activate version {version_info.version}: {e}")
            raise
    
    async def _cleanup_old_versions(self):
        """Clean up old versions, keeping only the most recent ones"""
        try:
            version_dirs = [d for d in self.versions_path.iterdir() if d.is_dir()]
            
            # Sort by modification time (newest first)
            version_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old versions beyond max_versions
            for old_dir in version_dirs[self.max_versions:]:
                import shutil
                shutil.rmtree(old_dir)
                logger.info(f"Cleaned up old version: {old_dir.name}")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old versions: {e}")
    
    async def start_background_tasks(self):
        """Start background tasks for automatic updates and health checks"""
        if self.update_task is None:
            self.update_task = asyncio.create_task(self._update_loop())
            logger.info("Started update background task")
        
        if self.health_check_task is None:
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            logger.info("Started health check background task")
    
    async def stop_background_tasks(self):
        """Stop background tasks"""
        if self.update_task:
            self.update_task.cancel()
            try:
                await self.update_task
            except asyncio.CancelledError:
                pass
            self.update_task = None
            logger.info("Stopped update background task")
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
            self.health_check_task = None
            logger.info("Stopped health check background task")
    
    async def _update_loop(self):
        """Background loop for automatic updates"""
        while True:
            try:
                await asyncio.sleep(self.update_check_interval)
                
                if not self.current_version:
                    continue
                
                # Check if update is needed
                if await self._check_for_updates():
                    await self._perform_update()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Update loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _health_check_loop(self):
        """Background loop for health checks"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._get_healthy_sources()  # This performs health checks
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def ensure_lit_available(self) -> bool:
        """Ensure Lit 3 is available (enhanced version)"""
        try:
            # If no current version, download one
            if not self.current_version:
                healthy_sources = await self._get_healthy_sources()
                if not healthy_sources:
                    logger.error("No healthy CDN sources available")
                    return False
                
                success, version_info = await self._download_from_source(healthy_sources[0])
                if success and version_info:
                    await self._activate_version(version_info)
                    return True
                else:
                    return False
            
            # Check if current version file exists
            current_js = self.current_path / "lit-core.min.js"
            if not current_js.exists():
                logger.warning("Current version file missing, re-downloading")
                return await self.ensure_lit_available()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure Lit availability: {e}")
            return False
    
    def get_lit_info(self) -> Dict[str, Any]:
        """Get comprehensive Lit 3 information"""
        info = {
            "available": False,
            "version": "unknown",
            "path": str(self.current_path / "lit-core.min.js"),
            "size": 0,
            "download_time": None,
            "source_url": "unknown",
            "performance_score": 0.0,
            "error_count": 0,
            "uptime": 0,
            "metrics": self.metrics.copy(),
            "cdn_sources": [
                {
                    "url": source["url"],
                    "priority": source["priority"],
                    "healthy": source["healthy"],
                    "response_time": source["response_time"],
                    "error_count": source["error_count"],
                    "last_check": source["last_check"].isoformat() if source["last_check"] else None
                }
                for source in self.cdn_sources
            ],
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "version": event.version,
                    "status": event.status.value,
                    "message": event.message
                }
                for event in self.events[-10:]  # Last 10 events
            ]
        }
        
        if self.current_version:
            info.update({
                "available": True,
                "version": self.current_version.version,
                "size": self.current_version.size,
                "download_time": self.current_version.download_time.isoformat(),
                "source_url": self.current_version.source_url,
                "performance_score": self.current_version.performance_score,
                "error_count": self.current_version.error_count
            })
            
            # Calculate uptime
            uptime = datetime.now() - self.metrics['uptime_start']
            info["uptime"] = uptime.total_seconds()
        
        return info
    
    async def force_update(self) -> bool:
        """Force an immediate update"""
        return await self._perform_update()
    
    async def rollback_to_version(self, version: str) -> bool:
        """Rollback to a specific version"""
        try:
            # Sanitize version for filesystem
            safe_version = version.replace('"', '').replace('/', '_').replace('\\', '_')
            version_dir = self.versions_path / safe_version
            if not version_dir.exists():
                logger.error(f"Version {version} not found")
                return False
            
            # Load version info
            with open(version_dir / "version.json", 'r') as f:
                data = json.load(f)
                version_info = VersionInfo(
                    version=data['version'],
                    etag=data['etag'],
                    size=data['size'],
                    download_time=datetime.fromisoformat(data['download_time']),
                    checksum=data['checksum'],
                    source_url=data['source_url'],
                    is_active=False,
                    performance_score=data.get('performance_score', 0.0),
                    error_count=data.get('error_count', 0)
                )
            
            await self._activate_version(version_info)
            
            self.metrics['rollbacks'] += 1
            
            self._add_event(
                "rollback",
                version,
                UpdateStatus.ROLLED_BACK,
                f"Rolled back to version {version}"
            )
            
            logger.info(f"Rolled back to version {version}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_available_versions(self) -> List[Dict[str, Any]]:
        """Get list of available versions"""
        versions = []
        
        for version_dir in self.versions_path.iterdir():
            if version_dir.is_dir():
                version_file = version_dir / "version.json"
                if version_file.exists():
                    try:
                        with open(version_file, 'r') as f:
                            data = json.load(f)
                            versions.append({
                                "version": data['version'],
                                "size": data['size'],
                                "download_time": data['download_time'],
                                "source_url": data['source_url'],
                                "performance_score": data.get('performance_score', 0.0),
                                "is_active": data.get('is_active', False)
                            })
                    except Exception as e:
                        logger.warning(f"Failed to read version info for {version_dir.name}: {e}")
        
        # Sort by download time (newest first)
        versions.sort(key=lambda x: x['download_time'], reverse=True)
        return versions

# Global instance
advanced_lit_manager = AdvancedLitManager()
