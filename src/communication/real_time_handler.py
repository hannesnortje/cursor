#!/usr/bin/env python3
"""
Real-Time Message Handler for AI Agent System.
Integrates with Redis to provide actual cross-chat message visibility.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

from .redis_queue import RedisMessageQueue, QueuedMessage
from .cross_chat_coordinator import CrossChatEvent

logger = logging.getLogger(__name__)


@dataclass
class RealTimeMessage:
    """Real-time message for cross-chat visibility."""
    message_id: str
    source_chat: str
    source_agent: str
    content: str
    message_type: str
    target_chats: List[str]
    priority: int
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class RealTimeMessageHandler:
    """Handles real-time message processing and storage."""
    
    def __init__(self, redis_queue: RedisMessageQueue):
        self.redis_queue = redis_queue
        self.active_chats: Set[str] = set()
        self.chat_messages: Dict[str, List[RealTimeMessage]] = {}
        self.message_history: List[RealTimeMessage] = []
        self.max_history_size = 1000
        
        logger.info("Real-time message handler initialized")
    
    async def connect(self) -> bool:
        """Connect to Redis."""
        return await self.redis_queue.connect()
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        await self.redis_queue.disconnect()
    
    async def store_cross_chat_message(self, event: CrossChatEvent) -> bool:
        """Store a cross-chat message in Redis."""
        try:
            # Create real-time message
            real_time_msg = RealTimeMessage(
                message_id=event.event_id,
                source_chat=event.source_chat,
                source_agent=event.source_agent,
                content=str(event.content),
                message_type=event.event_type,
                target_chats=event.target_chats,
                priority=event.priority,
                timestamp=event.timestamp,
                metadata=event.metadata
            )
            
            # Store in Redis
            queued_msg = QueuedMessage(
                message_id=event.event_id,
                sender=event.source_agent,
                recipient="cross_chat",
                content=real_time_msg.to_dict(),
                message_type="cross_chat",
                priority=event.priority,
                created_at=event.timestamp
            )
            
            success = await self.redis_queue.enqueue_message(queued_msg)
            
            if success:
                # Update local state
                self._update_local_state(real_time_msg)
                logger.info(f"Cross-chat message stored: {event.event_id}")
                return True
            else:
                logger.error(f"Failed to store cross-chat message: {event.event_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing cross-chat message: {e}")
            return False
    
    def _update_local_state(self, message: RealTimeMessage) -> None:
        """Update local message state."""
        # Add to message history
        self.message_history.append(message)
        if len(self.message_history) > self.max_history_size:
            self.message_history.pop(0)
        
        # Update chat messages
        for chat_id in message.target_chats:
            if chat_id not in self.chat_messages:
                self.chat_messages[chat_id] = []
            self.chat_messages[chat_id].append(message)
            
            # Keep only recent messages per chat
            if len(self.chat_messages[chat_id]) > 100:
                self.chat_messages[chat_id] = self.chat_messages[chat_id][-100:]
    
    async def get_chat_messages(self, chat_id: str, limit: int = 50) -> List[RealTimeMessage]:
        """Get messages for a specific chat."""
        try:
            # First try to get from Redis
            if await self.redis_queue.is_connected:
                # Get messages from Redis (this would be implemented with proper chat-specific keys)
                # For now, return from local state
                pass
            
            # Return from local state
            if chat_id in self.chat_messages:
                messages = self.chat_messages[chat_id][-limit:]
                return messages
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error getting chat messages for {chat_id}: {e}")
            return []
    
    async def get_all_cross_chat_messages(self, limit: int = 100) -> List[RealTimeMessage]:
        """Get all cross-chat messages."""
        try:
            # Return from local state (most recent first)
            messages = self.message_history[-limit:] if self.message_history else []
            return list(reversed(messages))  # Most recent first
            
        except Exception as e:
            logger.error(f"Error getting all cross-chat messages: {e}")
            return []
    
    async def search_messages(self, query: str, chat_id: Optional[str] = None, 
                            limit: int = 50) -> List[RealTimeMessage]:
        """Search messages by content."""
        try:
            results = []
            search_query = query.lower()
            
            # Determine which messages to search
            if chat_id and chat_id in self.chat_messages:
                messages_to_search = self.chat_messages[chat_id]
            else:
                messages_to_search = self.message_history
            
            for message in messages_to_search:
                if search_query in message.content.lower():
                    results.append(message)
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []
    
    async def get_chat_summary(self, chat_id: str) -> Dict[str, Any]:
        """Get summary of a specific chat."""
        try:
            if chat_id not in self.chat_messages:
                return {
                    "chat_id": chat_id,
                    "message_count": 0,
                    "last_message": None,
                    "active": False
                }
            
            messages = self.chat_messages[chat_id]
            last_message = messages[-1] if messages else None
            
            return {
                "chat_id": chat_id,
                "message_count": len(messages),
                "last_message": last_message.to_dict() if last_message else None,
                "active": True,
                "last_activity": last_message.timestamp if last_message else None
            }
            
        except Exception as e:
            logger.error(f"Error getting chat summary for {chat_id}: {e}")
            return {"error": str(e)}
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            redis_status = await self.redis_queue.health_check()
            queue_status = await self.redis_queue.get_queue_status()
            
            return {
                "redis": redis_status,
                "queue": queue_status,
                "active_chats": len(self.active_chats),
                "total_messages": len(self.message_history),
                "chat_messages": {chat_id: len(messages) for chat_id, messages in self.chat_messages.items()},
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def cleanup_old_messages(self, max_age_hours: int = 24) -> int:
        """Clean up old messages."""
        try:
            cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
            cleaned_count = 0
            
            # Clean up message history
            original_count = len(self.message_history)
            self.message_history = [
                msg for msg in self.message_history 
                if datetime.fromisoformat(msg.timestamp).timestamp() > cutoff_time
            ]
            cleaned_count += original_count - len(self.message_history)
            
            # Clean up chat messages
            for chat_id in list(self.chat_messages.keys()):
                original_count = len(self.chat_messages[chat_id])
                self.chat_messages[chat_id] = [
                    msg for msg in self.chat_messages[chat_id]
                    if datetime.fromisoformat(msg.timestamp).timestamp() > cutoff_time
                ]
                cleaned_count += original_count - len(self.chat_messages[chat_id])
                
                # Remove empty chat entries
                if not self.chat_messages[chat_id]:
                    del self.chat_messages[chat_id]
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old messages")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {e}")
            return 0
