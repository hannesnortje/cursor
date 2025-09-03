#!/usr/bin/env python3
"""Advanced Communication Features for Phase 7.3."""

import asyncio
import json
import logging
import time
import zlib
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib

logger = logging.getLogger(__name__)

class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class MessageType(Enum):
    """Message types for routing."""
    SYSTEM = "system"
    AGENT = "agent"
    USER = "user"
    MONITORING = "monitoring"
    ERROR = "error"
    DEBUG = "debug"

@dataclass
class AdvancedMessage:
    """Advanced message with metadata and routing information."""
    id: str
    content: Any
    sender: str
    recipients: List[str]
    message_type: MessageType
    priority: MessagePriority
    timestamp: float
    ttl: Optional[float] = None
    compression: bool = False
    encryption: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.ttl is None:
            return False
        return time.time() > self.timestamp + self.ttl
    
    def get_size(self) -> int:
        """Get approximate message size."""
        content_str = json.dumps(self.content)
        return len(content_str.encode('utf-8'))

class MessageCompressor:
    """Message compression utilities."""
    
    @staticmethod
    def compress(data: bytes) -> bytes:
        """Compress data using zlib."""
        try:
            return zlib.compress(data, level=6)
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return data
    
    @staticmethod
    def decompress(data: bytes) -> bytes:
        """Decompress data using zlib."""
        try:
            return zlib.decompress(data)
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return data
    
    @staticmethod
    def should_compress(data: bytes, threshold: int = 1024) -> bool:
        """Determine if data should be compressed."""
        return len(data) > threshold

class PriorityQueue:
    """Priority-based message queue."""
    
    def __init__(self):
        self.queues: Dict[MessagePriority, deque] = {
            priority: deque() for priority in MessagePriority
        }
        self._lock = asyncio.Lock()
    
    async def put(self, message: AdvancedMessage):
        """Put message in appropriate priority queue."""
        async with self._lock:
            self.queues[message.priority].append(message)
    
    async def get(self) -> Optional[AdvancedMessage]:
        """Get highest priority message."""
        async with self._lock:
            # Check queues from highest to lowest priority
            for priority in sorted(MessagePriority, reverse=True):
                if self.queues[priority]:
                    return self.queues[priority].popleft()
        return None
    
    async def size(self) -> int:
        """Get total queue size."""
        async with self._lock:
            return sum(len(queue) for queue in self.queues.values())
    
    async def get_queue_sizes(self) -> Dict[MessagePriority, int]:
        """Get size of each priority queue."""
        async with self._lock:
            return {priority: len(queue) for priority, queue in self.queues.items()}

class MessageRouter:
    """Advanced message routing with filtering and analytics."""
    
    def __init__(self):
        self.routes: Dict[str, List[Callable]] = defaultdict(list)
        self.filters: Dict[str, List[Callable]] = defaultdict(list)
        self.analytics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = asyncio.Lock()
    
    def add_route(self, message_type: str, handler: Callable):
        """Add a route handler for a message type."""
        self.routes[message_type].append(handler)
    
    def add_filter(self, message_type: str, filter_func: Callable):
        """Add a filter for a message type."""
        self.filters[message_type].append(filter_func)
    
    async def route_message(self, message: AdvancedMessage) -> bool:
        """Route a message through filters and handlers."""
        message_type = message.message_type.value
        
        # Apply filters
        if message_type in self.filters:
            for filter_func in self.filters[message_type]:
                try:
                    if not await filter_func(message):
                        logger.debug(f"Message {message.id} filtered out by {filter_func.__name__}")
                        return False
                except Exception as e:
                    logger.error(f"Filter {filter_func.__name__} failed: {e}")
                    return False
        
        # Route to handlers
        if message_type in self.routes:
            for handler in self.routes[message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Handler {handler.__name__} failed: {e}")
        
        # Update analytics
        await self._update_analytics(message)
        return True
    
    async def _update_analytics(self, message: AdvancedMessage):
        """Update message analytics."""
        message_type = message.message_type.value
        
        async with self._lock:
            if message_type not in self.analytics:
                self.analytics[message_type] = {
                    "count": 0,
                    "total_size": 0,
                    "priority_distribution": {p.value: 0 for p in MessagePriority},
                    "sender_distribution": defaultdict(int),
                    "avg_processing_time": 0.0
                }
            
            analytics = self.analytics[message_type]
            analytics["count"] += 1
            analytics["total_size"] += message.get_size()
            analytics["priority_distribution"][message.priority.value] += 1
            analytics["sender_distribution"][message.sender] += 1
    
    def get_analytics(self, message_type: Optional[str] = None) -> Dict[str, Any]:
        """Get message analytics."""
        if message_type:
            return self.analytics.get(message_type, {})
        return dict(self.analytics)

class MessageFilter:
    """Built-in message filters."""
    
    @staticmethod
    async def rate_limit_filter(max_messages_per_second: int = 100):
        """Create a rate limiting filter."""
        message_counts = defaultdict(int)
        last_reset = time.time()
        
        async def filter_func(message: AdvancedMessage) -> bool:
            nonlocal last_reset
            current_time = time.time()
            
            # Reset counter every second
            if current_time - last_reset >= 1.0:
                message_counts.clear()
                last_reset = current_time
            
            sender = message.sender
            if message_counts[sender] >= max_messages_per_second:
                logger.warning(f"Rate limit exceeded for {sender}")
                return False
            
            message_counts[sender] += 1
            return True
        
        return filter_func
    
    @staticmethod
    async def size_filter(max_size: int = 1024 * 1024):  # 1MB
        """Create a size-based filter."""
        async def filter_func(message: AdvancedMessage) -> bool:
            if message.get_size() > max_size:
                logger.warning(f"Message {message.id} exceeds size limit")
                return False
            return True
        
        return filter_func
    
    @staticmethod
    async def content_filter(forbidden_patterns: List[str] = None):
        """Create a content-based filter."""
        if forbidden_patterns is None:
            forbidden_patterns = []
        
        async def filter_func(message: AdvancedMessage) -> bool:
            content_str = json.dumps(message.content).lower()
            for pattern in forbidden_patterns:
                if pattern.lower() in content_str:
                    logger.warning(f"Message {message.id} contains forbidden pattern: {pattern}")
                    return False
            return True
        
        return filter_func

class AdvancedCommunicationSystem:
    """Advanced communication system with all features."""
    
    def __init__(self):
        self.priority_queue = PriorityQueue()
        self.router = MessageRouter()
        self.compressor = MessageCompressor()
        self.message_history: deque = deque(maxlen=10000)
        self._processing_task: Optional[asyncio.Task] = None
        self._stats = {
            "messages_sent": 0,
            "messages_received": 0,
            "messages_filtered": 0,
            "compression_ratio": 0.0,
            "avg_processing_time": 0.0
        }
    
    async def start(self):
        """Start the advanced communication system."""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._process_messages())
            logger.info("Advanced communication system started")
    
    async def stop(self):
        """Stop the advanced communication system."""
        if self._processing_task:
            self._processing_task.cancel()
            self._processing_task = None
            logger.info("Advanced communication system stopped")
    
    async def send_message(self, message: AdvancedMessage) -> bool:
        """Send a message through the system."""
        try:
            # Compress if beneficial
            if message.compression and isinstance(message.content, str):
                content_bytes = message.content.encode('utf-8')
                if self.compressor.should_compress(content_bytes):
                    compressed = self.compressor.compress(content_bytes)
                    message.content = compressed
                    message.metadata["compressed"] = True
                    message.metadata["original_size"] = len(content_bytes)
                    message.metadata["compressed_size"] = len(compressed)
            
            # Add to priority queue
            await self.priority_queue.put(message)
            
            # Update stats
            self._stats["messages_sent"] += 1
            
            logger.debug(f"Message {message.id} queued with priority {message.priority.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message {message.id}: {e}")
            return False
    
    async def _process_messages(self):
        """Process messages from the priority queue."""
        while True:
            try:
                message = await self.priority_queue.get()
                if message is None:
                    await asyncio.sleep(0.01)
                    continue
                
                start_time = time.time()
                
                # Check if message has expired
                if message.is_expired():
                    logger.debug(f"Message {message.id} expired, skipping")
                    self._stats["messages_filtered"] += 1
                    continue
                
                # Route the message
                success = await self.router.route_message(message)
                
                # Update processing time
                processing_time = time.time() - start_time
                self._update_processing_time(processing_time)
                
                # Store in history
                self.message_history.append({
                    "id": message.id,
                    "timestamp": message.timestamp,
                    "processing_time": processing_time,
                    "success": success
                })
                
                # Update stats
                self._stats["messages_received"] += 1
                if not success:
                    self._stats["messages_filtered"] += 1
                
                # Update compression ratio
                if message.metadata.get("compressed"):
                    original_size = message.metadata.get("original_size", 0)
                    compressed_size = message.metadata.get("compressed_size", 0)
                    if original_size > 0:
                        ratio = 1 - (compressed_size / original_size)
                        self._update_compression_ratio(ratio)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await asyncio.sleep(0.1)
    
    def _update_processing_time(self, processing_time: float):
        """Update average processing time."""
        current_avg = self._stats["avg_processing_time"]
        count = self._stats["messages_received"]
        
        if count > 0:
            new_avg = ((current_avg * (count - 1)) + processing_time) / count
            self._stats["avg_processing_time"] = new_avg
        else:
            self._stats["avg_processing_time"] = processing_time
    
    def _update_compression_ratio(self, ratio: float):
        """Update average compression ratio."""
        current_avg = self._stats["compression_ratio"]
        count = self._stats["messages_sent"]
        
        if count > 0:
            new_avg = ((current_avg * (count - 1)) + ratio) / count
            self._stats["compression_ratio"] = new_avg
        else:
            self._stats["compression_ratio"] = ratio
    
    def get_stats(self) -> Dict[str, Any]:
        """Get communication system statistics."""
        return {
            **self._stats,
            "queue_size": asyncio.create_task(self.priority_queue.size()),
            "queue_distribution": asyncio.create_task(self.priority_queue.get_queue_sizes()),
            "router_analytics": self.router.get_analytics(),
            "message_history_size": len(self.message_history)
        }
    
    def add_route(self, message_type: str, handler: Callable):
        """Add a message route handler."""
        self.router.add_route(message_type, handler)
    
    def add_filter(self, message_type: str, filter_func: Callable):
        """Add a message filter."""
        self.router.add_filter(message_type, filter_func)

# Global instance
advanced_communication = AdvancedCommunicationSystem()
