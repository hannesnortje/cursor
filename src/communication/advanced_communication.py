"""Advanced Communication Features for Phase 9.3 with fallback support."""

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
        return time.time() - self.timestamp > self.ttl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender,
            "recipients": self.recipients,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "compression": self.compression,
            "encryption": self.encryption,
            "metadata": self.metadata
        }


class MessageCompressor:
    """Message compression with performance monitoring."""
    
    def __init__(self):
        self.compression_stats = {
            "total_compressed": 0,
            "total_uncompressed": 0,
            "compression_ratio": 0.0,
            "compression_time": 0.0,
            "decompression_time": 0.0
        }
        logger.info("Message compressor initialized")
    
    def compress_message(self, content: str, level: int = 6) -> Dict[str, Any]:
        """Compress message content with performance monitoring."""
        try:
            start_time = time.time()
            
            # Convert to bytes if string
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            else:
                content_bytes = str(content).encode('utf-8')
            
            # Compress
            compressed = zlib.compress(content_bytes, level)
            
            compression_time = time.time() - start_time
            
            # Calculate compression ratio
            original_size = len(content_bytes)
            compressed_size = len(compressed)
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            
            # Update stats
            self.compression_stats["total_compressed"] += 1
            self.compression_stats["compression_ratio"] = compression_ratio
            self.compression_stats["compression_time"] += compression_time
            
            logger.info(f"Compressed message: {original_size} -> {compressed_size} bytes ({compression_ratio:.2%} ratio)")
            
            return {
                "compressed": True,
                "content": compressed,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "compression_time": compression_time
            }
            
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            # Fallback to uncompressed
            return {
                "compressed": False,
                "content": content,
                "original_size": len(str(content)),
                "compressed_size": len(str(content)),
                "compression_ratio": 1.0,
                "compression_time": 0.0,
                "error": str(e)
            }
    
    def decompress_message(self, compressed_content: bytes) -> Dict[str, Any]:
        """Decompress message content with performance monitoring."""
        try:
            start_time = time.time()
            
            # Decompress
            decompressed = zlib.decompress(compressed_content)
            content = decompressed.decode('utf-8')
            
            decompression_time = time.time() - start_time
            
            # Update stats
            self.compression_stats["total_uncompressed"] += 1
            self.compression_stats["decompression_time"] += decompression_time
            
            logger.info(f"Decompressed message: {len(compressed_content)} -> {len(content)} bytes")
            
            return {
                "decompressed": True,
                "content": content,
                "decompression_time": decompression_time
            }
            
        except Exception as e:
            logger.error(f"Decompression failed: {e}")
            return {
                "decompressed": False,
                "content": str(compressed_content),
                "decompression_time": 0.0,
                "error": str(e)
            }
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return self.compression_stats.copy()


class PriorityRouter:
    """Priority-based message routing with fallback."""
    
    def __init__(self):
        self.message_queues = {
            priority: deque() for priority in MessagePriority
        }
        self.routing_stats = {
            "total_routed": 0,
            "priority_counts": {priority.name: 0 for priority in MessagePriority},
            "routing_time": 0.0
        }
        logger.info("Priority router initialized")
    
    def route_message(self, message: AdvancedMessage) -> Dict[str, Any]:
        """Route message based on priority with performance monitoring."""
        try:
            start_time = time.time()
            
            # Add to appropriate priority queue
            self.message_queues[message.priority].append(message)
            
            # Update stats
            self.routing_stats["total_routed"] += 1
            self.routing_stats["priority_counts"][message.priority.name] += 1
            self.routing_stats["routing_time"] += time.time() - start_time
            
            logger.info(f"Routed message {message.id} with priority {message.priority.name}")
            
            return {
                "routed": True,
                "message_id": message.id,
                "priority": message.priority.name,
                "queue_size": len(self.message_queues[message.priority])
            }
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return {
                "routed": False,
                "message_id": message.id,
                "error": str(e)
            }
    
    def get_next_message(self, priority: Optional[MessagePriority] = None) -> Optional[AdvancedMessage]:
        """Get next message from queue, checking highest priority first."""
        try:
            if priority:
                # Get from specific priority queue
                if self.message_queues[priority]:
                    return self.message_queues[priority].popleft()
            else:
                # Get from highest priority queue first
                for p in [MessagePriority.CRITICAL, MessagePriority.URGENT, 
                         MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]:
                    if self.message_queues[p]:
                        return self.message_queues[p].popleft()
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get next message: {e}")
            return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status information."""
        return {
            "queue_sizes": {priority.name: len(queue) for priority, queue in self.message_queues.items()},
            "total_messages": sum(len(queue) for queue in self.message_queues.values()),
            "routing_stats": self.routing_stats.copy()
        }


class CommunicationAnalytics:
    """Communication pattern analysis and optimization."""
    
    def __init__(self):
        self.message_history = deque(maxlen=1000)  # Keep last 1000 messages
        self.analytics_data = {
            "message_counts": defaultdict(int),
            "sender_counts": defaultdict(int),
            "recipient_counts": defaultdict(int),
            "priority_distribution": defaultdict(int),
            "type_distribution": defaultdict(int),
            "response_times": [],
            "throughput": 0.0
        }
        self.analytics_enabled = True
        logger.info("Communication analytics initialized")
    
    def record_message(self, message: AdvancedMessage, response_time: float = 0.0):
        """Record message for analytics."""
        if not self.analytics_enabled:
            return
        
        try:
            # Add to history
            self.message_history.append(message)
            
            # Update analytics
            self.analytics_data["message_counts"][message.message_type.value] += 1
            self.analytics_data["sender_counts"][message.sender] += 1
            self.analytics_data["recipient_counts"][len(message.recipients)] += 1
            self.analytics_data["priority_distribution"][message.priority.name] += 1
            self.analytics_data["type_distribution"][message.message_type.value] += 1
            
            if response_time > 0:
                self.analytics_data["response_times"].append(response_time)
                # Keep only last 100 response times
                if len(self.analytics_data["response_times"]) > 100:
                    self.analytics_data["response_times"] = self.analytics_data["response_times"][-100:]
            
            # Calculate throughput (messages per second)
            if len(self.message_history) > 1:
                time_span = self.message_history[-1].timestamp - self.message_history[0].timestamp
                if time_span > 0:
                    self.analytics_data["throughput"] = len(self.message_history) / time_span
            
        except Exception as e:
            logger.error(f"Failed to record message for analytics: {e}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get communication analytics."""
        try:
            # Calculate average response time
            avg_response_time = 0.0
            if self.analytics_data["response_times"]:
                avg_response_time = sum(self.analytics_data["response_times"]) / len(self.analytics_data["response_times"])
            
            return {
                "enabled": self.analytics_enabled,
                "total_messages": len(self.message_history),
                "message_counts": dict(self.analytics_data["message_counts"]),
                "sender_counts": dict(self.analytics_data["sender_counts"]),
                "recipient_counts": dict(self.analytics_data["recipient_counts"]),
                "priority_distribution": dict(self.analytics_data["priority_distribution"]),
                "type_distribution": dict(self.analytics_data["type_distribution"]),
                "average_response_time": avg_response_time,
                "throughput": self.analytics_data["throughput"],
                "analytics_data": self.analytics_data.copy()
            }
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {e}")
            return {
                "enabled": self.analytics_enabled,
                "error": str(e)
            }
    
    def enable_analytics(self):
        """Enable analytics collection."""
        self.analytics_enabled = True
        logger.info("Analytics enabled")
    
    def disable_analytics(self):
        """Disable analytics collection."""
        self.analytics_enabled = False
        logger.info("Analytics disabled")


class AdvancedCommunication:
    """Advanced communication system with compression, routing, and analytics."""
    
    def __init__(self):
        self.compressor = MessageCompressor()
        self.router = PriorityRouter()
        self.analytics = CommunicationAnalytics()
        self.cross_project_enabled = False
        self.message_types = [msg_type.value for msg_type in MessageType]
        self.status = "active"
        logger.info("Advanced communication system initialized")
    
    def send_message(self, content: Any, sender: str, recipients: List[str], 
                    message_type: str = "agent", priority: str = "normal",
                    compression: bool = False, ttl: Optional[float] = None) -> Dict[str, Any]:
        """Send message with advanced features."""
        try:
            # Create message
            message = AdvancedMessage(
                id=hashlib.md5(f"{sender}{recipients}{time.time()}".encode()).hexdigest()[:8],
                content=content,
                sender=sender,
                recipients=recipients,
                message_type=MessageType(message_type),
                priority=MessagePriority[priority.upper()],
                timestamp=time.time(),
                ttl=ttl,
                compression=compression
            )
            
            # Compress if requested
            if compression:
                compression_result = self.compressor.compress_message(str(content))
                if compression_result["compressed"]:
                    message.content = compression_result["content"]
                    message.compression = True
                    message.metadata["compression_stats"] = compression_result
            
            # Route message
            routing_result = self.router.route_message(message)
            
            # Record for analytics
            self.analytics.record_message(message)
            
            logger.info(f"Sent message {message.id} from {sender} to {len(recipients)} recipients")
            
            return {
                "success": True,
                "message_id": message.id,
                "routing_result": routing_result,
                "compression_applied": message.compression,
                "timestamp": message.timestamp
            }
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get communication analytics."""
        return self.analytics.get_analytics()
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get message queue status."""
        return self.router.get_queue_status()
    
    def enable_cross_project(self) -> Dict[str, Any]:
        """Enable cross-project communication."""
        try:
            self.cross_project_enabled = True
            logger.info("Cross-project communication enabled")
            return {
                "success": True,
                "cross_project_enabled": True,
                "message": "Cross-project communication enabled"
            }
        except Exception as e:
            logger.error(f"Failed to enable cross-project communication: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def disable_cross_project(self) -> Dict[str, Any]:
        """Disable cross-project communication."""
        try:
            self.cross_project_enabled = False
            logger.info("Cross-project communication disabled")
            return {
                "success": True,
                "cross_project_enabled": False,
                "message": "Cross-project communication disabled"
            }
        except Exception as e:
            logger.error(f"Failed to disable cross-project communication: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def share_knowledge(self, knowledge: str, source_project: str, 
                       target_projects: List[str]) -> Dict[str, Any]:
        """Share knowledge between projects."""
        try:
            if not self.cross_project_enabled:
                return {
                    "success": False,
                    "error": "Cross-project communication is disabled"
                }
            
            # Create knowledge sharing message
            result = self.send_message(
                content=knowledge,
                sender=f"project_{source_project}",
                recipients=[f"project_{p}" for p in target_projects],
                message_type="system",
                priority="normal",
                compression=True
            )
            
            logger.info(f"Shared knowledge from {source_project} to {target_projects}")
            
            return {
                "success": True,
                "knowledge_shared": True,
                "source_project": source_project,
                "target_projects": target_projects,
                "message_result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to share knowledge: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_compression_stats(self) -> Dict[str, Any]:
        """Get compression statistics."""
        return self.compressor.get_compression_stats()
    
    def get_message_types(self) -> List[str]:
        """Get available message types."""
        return self.message_types.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "status": self.status,
            "cross_project_enabled": self.cross_project_enabled,
            "compression_stats": self.get_compression_stats(),
            "queue_status": self.get_queue_status(),
            "analytics_enabled": self.analytics.analytics_enabled
        }


# Global instance
_advanced_communication = None

def get_advanced_communication() -> AdvancedCommunication:
    """Get the global advanced communication instance."""
    global _advanced_communication
    if _advanced_communication is None:
        _advanced_communication = AdvancedCommunication()
    return _advanced_communication