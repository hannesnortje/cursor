"""Phase 9.3: Advanced Communication Features with AutoGen and Qdrant Integration."""

import asyncio
import json
import logging
import time
import zlib
import gzip
from typing import Dict, List, Optional, Any, Callable, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib
import statistics
from datetime import datetime, timedelta
import uuid

logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Message priority levels for intelligent routing."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


class MessageType(Enum):
    """Message types for advanced routing."""
    AGENT_COMMUNICATION = "agent_communication"
    WORKFLOW_COORDINATION = "workflow_coordination"
    PROJECT_SYNC = "project_sync"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    SYSTEM_NOTIFICATION = "system_notification"
    CROSS_PROJECT = "cross_project"
    AUTOGEN_CONVERSATION = "autogen_conversation"
    QDRANT_UPDATE = "qdrant_update"


class CompressionType(Enum):
    """Compression algorithms available."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"


@dataclass
class AdvancedMessage:
    """Enhanced message structure with advanced features."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: MessageType = MessageType.AGENT_COMMUNICATION
    priority: MessagePriority = MessagePriority.NORMAL
    content: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    project_id: Optional[str] = None
    session_id: Optional[str] = None
    compression: CompressionType = CompressionType.NONE
    ttl: Optional[int] = None  # Time to live in seconds
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "project_id": self.project_id,
            "session_id": self.session_id,
            "compression": self.compression.value,
            "ttl": self.ttl,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        }


class MessageCompressor:
    """Advanced message compression with multiple algorithms."""
    
    def __init__(self):
        self.compression_stats = {
            "gzip": {"count": 0, "total_original": 0, "total_compressed": 0},
            "zlib": {"count": 0, "total_original": 0, "total_compressed": 0}
        }
        self.min_compression_size = 1024  # Only compress if larger than 1KB
    
    def should_compress(self, content: bytes) -> bool:
        """Determine if content should be compressed."""
        return len(content) > self.min_compression_size
    
    def compress(self, content: bytes, algorithm: CompressionType = CompressionType.GZIP) -> bytes:
        """Compress content using specified algorithm."""
        if algorithm == CompressionType.GZIP:
            compressed = gzip.compress(content)
        elif algorithm == CompressionType.ZLIB:
            compressed = zlib.compress(content)
        else:
            return content
        
        # Update stats
        self.compression_stats[algorithm.value]["count"] += 1
        self.compression_stats[algorithm.value]["total_original"] += len(content)
        self.compression_stats[algorithm.value]["total_compressed"] += len(compressed)
        
        return compressed
    
    def decompress(self, content: bytes, algorithm: CompressionType) -> bytes:
        """Decompress content using specified algorithm."""
        if algorithm == CompressionType.GZIP:
            return gzip.decompress(content)
        elif algorithm == CompressionType.ZLIB:
            return zlib.decompress(content)
        else:
            return content
    
    def get_compression_ratio(self, algorithm: CompressionType) -> float:
        """Get compression ratio for an algorithm."""
        stats = self.compression_stats[algorithm.value]
        if stats["total_original"] == 0:
            return 0.0
        return 1.0 - (stats["total_compressed"] / stats["total_original"])


class PriorityQueue:
    """Advanced priority queue with multiple priority levels."""
    
    def __init__(self):
        self.queues = {priority: deque() for priority in MessagePriority}
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
    
    async def put(self, message: AdvancedMessage) -> None:
        """Add message to appropriate priority queue."""
        async with self._condition:
            self.queues[message.priority].append(message)
            self._condition.notify()
    
    async def get(self) -> AdvancedMessage:
        """Get highest priority message."""
        async with self._condition:
            while True:
                # Check queues in priority order (CRITICAL first)
                for priority in sorted(MessagePriority, key=lambda x: x.value, reverse=True):
                    if self.queues[priority]:
                        return self.queues[priority].popleft()
                
                # Wait for new messages
                await self._condition.wait()
    
    async def get_queue_sizes(self) -> Dict[MessagePriority, int]:
        """Get current queue sizes."""
        async with self._lock:
            return {priority: len(queue) for priority, queue in self.queues.items()}


class CommunicationAnalytics:
    """Advanced analytics for communication patterns."""
    
    def __init__(self):
        self.message_counts = defaultdict(int)
        self.message_latencies = defaultdict(list)
        self.throughput_history = deque(maxlen=1000)
        self.error_rates = defaultdict(int)
        self.project_activity = defaultdict(int)
        self.agent_activity = defaultdict(int)
        self.start_time = datetime.now()
    
    def record_message(self, message: AdvancedMessage, processing_time: float = 0.0):
        """Record message statistics."""
        self.message_counts[message.message_type.value] += 1
        self.message_latencies[message.message_type.value].append(processing_time)
        
        if message.project_id:
            self.project_activity[message.project_id] += 1
        
        if message.sender:
            self.agent_activity[message.sender] += 1
        
        # Record throughput (messages per minute)
        now = datetime.now()
        self.throughput_history.append(now)
    
    def record_error(self, message_type: str, error: str):
        """Record communication errors."""
        self.error_rates[f"{message_type}_{error}"] += 1
    
    def get_throughput(self, minutes: int = 1) -> float:
        """Get current throughput in messages per minute."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_messages = [t for t in self.throughput_history if t > cutoff]
        return len(recent_messages) / minutes
    
    def get_avg_latency(self, message_type: str) -> float:
        """Get average latency for a message type."""
        latencies = self.message_latencies[message_type]
        return statistics.mean(latencies) if latencies else 0.0
    
    def get_error_rate(self, message_type: str) -> float:
        """Get error rate for a message type."""
        total_messages = self.message_counts[message_type]
        if total_messages == 0:
            return 0.0
        
        errors = sum(count for key, count in self.error_rates.items() 
                   if key.startswith(message_type))
        return errors / total_messages
    
    def get_project_activity(self) -> Dict[str, int]:
        """Get project activity statistics."""
        return dict(self.project_activity)
    
    def get_agent_activity(self) -> Dict[str, int]:
        """Get agent activity statistics."""
        return dict(self.agent_activity)
    
    def get_health_score(self) -> float:
        """Calculate overall communication health score (0-100)."""
        # Factor in throughput, error rates, and latency
        throughput = self.get_throughput()
        avg_error_rate = statistics.mean([
            self.get_error_rate(msg_type) 
            for msg_type in self.message_counts.keys()
        ]) if self.message_counts else 0
        
        # Health score calculation (simplified)
        throughput_score = min(throughput * 10, 50)  # Max 50 points for throughput
        error_score = max(0, 30 - (avg_error_rate * 100))  # Max 30 points, reduced by errors
        latency_score = 20  # Base 20 points (could be improved with latency analysis)
        
        return min(100, throughput_score + error_score + latency_score)


class CrossProjectCommunicator:
    """Handle cross-project communication and knowledge sharing."""
    
    def __init__(self, vector_store_manager=None):
        self.vector_store_manager = vector_store_manager
        self.project_connections = defaultdict(set)  # project_id -> set of connected projects
        self.knowledge_sharing_enabled = True
        self.sharing_history = deque(maxlen=1000)
    
    async def enable_project_connection(self, project1: str, project2: str):
        """Enable knowledge sharing between two projects."""
        self.project_connections[project1].add(project2)
        self.project_connections[project2].add(project1)
        logger.info(f"Enabled cross-project communication between {project1} and {project2}")
    
    async def disable_project_connection(self, project1: str, project2: str):
        """Disable knowledge sharing between two projects."""
        self.project_connections[project1].discard(project2)
        self.project_connections[project2].discard(project1)
        logger.info(f"Disabled cross-project communication between {project1} and {project2}")
    
    async def share_knowledge(self, source_project: str, target_project: str, 
                            knowledge: Dict[str, Any]) -> bool:
        """Share knowledge between projects."""
        if not self.knowledge_sharing_enabled:
            return False
        
        if target_project not in self.project_connections[source_project]:
            logger.warning(f"Projects {source_project} and {target_project} not connected")
            return False
        
        try:
            # Create cross-project message
            message = AdvancedMessage(
                sender=f"project_{source_project}",
                recipient=f"project_{target_project}",
                message_type=MessageType.CROSS_PROJECT,
                priority=MessagePriority.NORMAL,
                content=knowledge,
                project_id=target_project,
                metadata={
                    "source_project": source_project,
                    "knowledge_type": knowledge.get("type", "general"),
                    "shared_at": datetime.now().isoformat()
                }
            )
            
            # Record sharing
            self.sharing_history.append({
                "source": source_project,
                "target": target_project,
                "timestamp": datetime.now(),
                "knowledge_type": knowledge.get("type", "general")
            })
            
            logger.info(f"Shared knowledge from {source_project} to {target_project}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to share knowledge: {e}")
            return False
    
    async def get_connected_projects(self, project_id: str) -> Set[str]:
        """Get projects connected to a given project."""
        return self.project_connections[project_id].copy()
    
    async def get_sharing_history(self, project_id: str = None) -> List[Dict[str, Any]]:
        """Get knowledge sharing history."""
        if project_id:
            return [
                entry for entry in self.sharing_history
                if entry["source"] == project_id or entry["target"] == project_id
            ]
        return list(self.sharing_history)


class Phase9_3AdvancedCommunication:
    """Phase 9.3: Advanced Communication Features with AutoGen and Qdrant Integration."""
    
    def __init__(self, vector_store_manager=None, autogen_integration=None):
        self.vector_store_manager = vector_store_manager
        self.autogen_integration = autogen_integration
        
        # Core components
        self.priority_queue = PriorityQueue()
        self.compressor = MessageCompressor()
        self.analytics = CommunicationAnalytics()
        self.cross_project_comm = CrossProjectCommunicator(vector_store_manager)
        
        # Message routing
        self.routes: Dict[str, List[Callable]] = defaultdict(list)
        self.filters: Dict[str, List[Callable]] = defaultdict(list)
        
        # Processing
        self._processing_task: Optional[asyncio.Task] = None
        self._is_running = False
        
        # Performance monitoring
        self.performance_metrics = {
            "messages_processed": 0,
            "avg_processing_time": 0.0,
            "compression_savings": 0.0,
            "error_count": 0
        }
        
        logger.info("Phase 9.3 Advanced Communication system initialized")
    
    async def start(self):
        """Start the advanced communication system."""
        if not self._is_running:
            self._processing_task = asyncio.create_task(self._process_messages())
            self._is_running = True
            logger.info("Phase 9.3 Advanced Communication system started")
    
    async def stop(self):
        """Stop the advanced communication system."""
        if self._processing_task:
            self._processing_task.cancel()
            self._processing_task = None
            self._is_running = False
            logger.info("Phase 9.3 Advanced Communication system stopped")
    
    async def send_message(self, message: AdvancedMessage) -> bool:
        """Send a message through the advanced communication system."""
        try:
            start_time = time.time()
            
            # Apply compression if beneficial
            if message.compression != CompressionType.NONE and isinstance(message.content, str):
                content_bytes = message.content.encode('utf-8')
                if self.compressor.should_compress(content_bytes):
                    compressed = self.compressor.compress(content_bytes, message.compression)
                    message.content = compressed
                    message.metadata["compressed"] = True
                    message.metadata["original_size"] = len(content_bytes)
                    message.metadata["compressed_size"] = len(compressed)
            
            # Add to priority queue
            await self.priority_queue.put(message)
            
            # Update performance metrics
            processing_time = time.time() - start_time
            self.performance_metrics["messages_processed"] += 1
            self.performance_metrics["avg_processing_time"] = (
                (self.performance_metrics["avg_processing_time"] * 
                 (self.performance_metrics["messages_processed"] - 1) + processing_time) /
                self.performance_metrics["messages_processed"]
            )
            
            logger.debug(f"Message {message.id} queued with priority {message.priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            self.performance_metrics["error_count"] += 1
            return False
    
    async def _process_messages(self):
        """Process messages from the priority queue."""
        while self._is_running:
            try:
                message = await self.priority_queue.get()
                await self._handle_message(message)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self.performance_metrics["error_count"] += 1
    
    async def _handle_message(self, message: AdvancedMessage):
        """Handle a single message."""
        try:
            start_time = time.time()
            
            # Check TTL
            if message.ttl and (datetime.now() - message.timestamp).seconds > message.ttl:
                logger.debug(f"Message {message.id} expired, dropping")
                return
            
            # Apply filters
            if not await self._apply_filters(message):
                logger.debug(f"Message {message.id} filtered out")
                return
            
            # Route message
            await self._route_message(message)
            
            # Record analytics
            processing_time = time.time() - start_time
            self.analytics.record_message(message, processing_time)
            
            logger.debug(f"Message {message.id} processed in {processing_time:.3f}s")
            
        except Exception as e:
            logger.error(f"Error handling message {message.id}: {e}")
            self.analytics.record_error(message.message_type.value, str(e))
    
    async def _apply_filters(self, message: AdvancedMessage) -> bool:
        """Apply message filters."""
        message_type = message.message_type.value
        
        if message_type in self.filters:
            for filter_func in self.filters[message_type]:
                try:
                    if not await filter_func(message):
                        return False
                except Exception as e:
                    logger.error(f"Filter {filter_func.__name__} failed: {e}")
                    return False
        
        return True
    
    async def _route_message(self, message: AdvancedMessage):
        """Route message to appropriate handlers."""
        message_type = message.message_type.value
        
        if message_type in self.routes:
            for handler in self.routes[message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Handler {handler.__name__} failed: {e}")
                    self.analytics.record_error(message_type, str(e))
    
    def add_route(self, message_type: MessageType, handler: Callable):
        """Add a message route handler."""
        self.routes[message_type.value].append(handler)
        logger.info(f"Added route handler for {message_type.value}")
    
    def add_filter(self, message_type: MessageType, filter_func: Callable):
        """Add a message filter."""
        self.filters[message_type.value].append(filter_func)
        logger.info(f"Added filter for {message_type.value}")
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Get communication analytics."""
        return {
            "message_counts": dict(self.analytics.message_counts),
            "throughput": self.analytics.get_throughput(),
            "health_score": self.analytics.get_health_score(),
            "project_activity": self.analytics.get_project_activity(),
            "agent_activity": self.analytics.get_agent_activity(),
            "compression_stats": self.compressor.compression_stats,
            "performance_metrics": self.performance_metrics,
            "uptime": (datetime.now() - self.analytics.start_time).total_seconds()
        }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        queue_sizes = await self.priority_queue.get_queue_sizes()
        return {
            "queue_sizes": {priority.name: size for priority, size in queue_sizes.items()},
            "total_queued": sum(queue_sizes.values()),
            "is_processing": self._is_running
        }
    
    async def enable_cross_project_communication(self, project1: str, project2: str):
        """Enable cross-project communication between two projects."""
        await self.cross_project_comm.enable_project_connection(project1, project2)
    
    async def disable_cross_project_communication(self, project1: str, project2: str):
        """Disable cross-project communication between two projects."""
        await self.cross_project_comm.disable_project_connection(project1, project2)
    
    async def share_knowledge_between_projects(self, source_project: str, target_project: str, 
                                             knowledge: Dict[str, Any]) -> bool:
        """Share knowledge between projects."""
        return await self.cross_project_comm.share_knowledge(
            source_project, target_project, knowledge
        )


# Global instance for easy access
_phase9_3_communication = None

def get_phase9_3_communication() -> Phase9_3AdvancedCommunication:
    """Get the global Phase 9.3 communication instance."""
    global _phase9_3_communication
    if _phase9_3_communication is None:
        _phase9_3_communication = Phase9_3AdvancedCommunication()
    return _phase9_3_communication
