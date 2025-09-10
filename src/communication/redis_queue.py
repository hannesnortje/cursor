#!/usr/bin/env python3
"""
Redis Message Queue for AI Agent System.
Provides reliable message delivery and offline message handling.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class QueuedMessage:
    """Message stored in Redis queue."""

    message_id: str
    sender: str
    recipient: str
    content: Any
    message_type: str
    priority: int
    created_at: str
    expires_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class RedisMessageQueue:
    """Redis-based message queue for reliable message delivery."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False
        self.retry_delay = 5  # seconds
        self.max_retries = 3

        # Queue names
        self.main_queue = "ai_agent_messages"
        self.priority_queue = "ai_agent_priority"
        self.dead_letter_queue = "ai_agent_dead_letter"
        self.offline_queue = "ai_agent_offline"

        logger.info(f"Redis message queue initialized for {host}:{port}")

    async def connect(self) -> bool:
        """Connect to Redis server."""
        if not REDIS_AVAILABLE:
            logger.error("Redis not available. Install redis package.")
            return False

        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )

            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("Connected to Redis server")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from Redis server."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("Disconnected from Redis server")

    async def enqueue_message(self, message: QueuedMessage) -> bool:
        """Add message to the appropriate queue."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return False

        try:
            message_data = json.dumps(message.to_dict())

            if message.priority >= 3:  # High priority messages
                await self.redis_client.lpush(self.priority_queue, message_data)
                logger.debug(f"High priority message enqueued: {message.message_id}")
            else:
                await self.redis_client.lpush(self.main_queue, message_data)
                logger.debug(f"Message enqueued: {message.message_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to enqueue message: {e}")
            return False

    async def dequeue_message(
        self, queue_name: Optional[str] = None
    ) -> Optional[QueuedMessage]:
        """Get next message from queue."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return None

        try:
            # Try priority queue first, then main queue
            if queue_name:
                queues = [queue_name]
            else:
                queues = [self.priority_queue, self.main_queue]

            for queue in queues:
                message_data = await self.redis_client.rpop(queue)
                if message_data:
                    message_dict = json.loads(message_data)
                    message = QueuedMessage(**message_dict)
                    logger.debug(f"Message dequeued from {queue}: {message.message_id}")
                    return message

            return None

        except Exception as e:
            logger.error(f"Failed to dequeue message: {e}")
            return None

    async def enqueue_offline_message(self, message: QueuedMessage) -> bool:
        """Store message for offline recipient."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return False

        try:
            # Set expiration for offline messages (24 hours)
            expires_at = datetime.now() + timedelta(hours=24)
            message.expires_at = expires_at.isoformat()

            message_data = json.dumps(message.to_dict())
            await self.redis_client.lpush(self.offline_queue, message_data)

            logger.info(
                f"Offline message stored: {message.message_id} for {message.recipient}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to store offline message: {e}")
            return False

    async def get_offline_messages(self, recipient: str) -> List[QueuedMessage]:
        """Get offline messages for a specific recipient."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return []

        try:
            messages = []
            current_time = datetime.now()

            # Get all offline messages
            offline_messages = await self.redis_client.lrange(self.offline_queue, 0, -1)

            for message_data in offline_messages:
                try:
                    message_dict = json.loads(message_data)
                    message = QueuedMessage(**message_dict)

                    # Check if message is for this recipient
                    if message.recipient == recipient:
                        # Check if message has expired
                        if message.expires_at:
                            expires_at = datetime.fromisoformat(message.expires_at)
                            if current_time > expires_at:
                                # Remove expired message
                                await self.redis_client.lrem(
                                    self.offline_queue, 1, message_data
                                )
                                continue

                        messages.append(message)

                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid offline message data: {e}")
                    continue

            logger.info(f"Retrieved {len(messages)} offline messages for {recipient}")
            return messages

        except Exception as e:
            logger.error(f"Failed to get offline messages: {e}")
            return []

    async def remove_offline_message(self, message_id: str) -> bool:
        """Remove a specific offline message."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return False

        try:
            offline_messages = await self.redis_client.lrange(self.offline_queue, 0, -1)

            for message_data in offline_messages:
                try:
                    message_dict = json.loads(message_data)
                    if message_dict.get("message_id") == message_id:
                        await self.redis_client.lrem(
                            self.offline_queue, 1, message_data
                        )
                        logger.info(f"Removed offline message: {message_id}")
                        return True
                except (json.JSONDecodeError, KeyError):
                    continue

            return False

        except Exception as e:
            logger.error(f"Failed to remove offline message: {e}")
            return False

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        if not self.is_connected:
            return {"error": "Not connected to Redis"}

        try:
            main_queue_size = await self.redis_client.llen(self.main_queue)
            priority_queue_size = await self.redis_client.llen(self.priority_queue)
            offline_queue_size = await self.redis_client.llen(self.offline_queue)
            dead_letter_size = await self.redis_client.llen(self.dead_letter_queue)

            return {
                "main_queue_size": main_queue_size,
                "priority_queue_size": priority_queue_size,
                "offline_queue_size": offline_queue_size,
                "dead_letter_size": dead_letter_size,
                "total_messages": main_queue_size
                + priority_queue_size
                + offline_queue_size,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {"error": str(e)}

    async def clear_expired_messages(self) -> int:
        """Clear expired messages from offline queue."""
        if not self.is_connected:
            logger.error("Not connected to Redis")
            return 0

        try:
            cleared_count = 0
            current_time = datetime.now()
            offline_messages = await self.redis_client.lrange(self.offline_queue, 0, -1)

            for message_data in offline_messages:
                try:
                    message_dict = json.loads(message_data)
                    if "expires_at" in message_dict:
                        expires_at = datetime.fromisoformat(message_dict["expires_at"])
                        if current_time > expires_at:
                            await self.redis_client.lrem(
                                self.offline_queue, 1, message_data
                            )
                            cleared_count += 1

                except (json.JSONDecodeError, KeyError):
                    continue

            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} expired messages")

            return cleared_count

        except Exception as e:
            logger.error(f"Failed to clear expired messages: {e}")
            return 0

    async def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        if not self.is_connected:
            return {"status": "disconnected", "error": "Not connected to Redis"}

        try:
            # Test ping
            await self.redis_client.ping()

            # Get basic info
            info = await self.redis_client.info()

            return {
                "status": "healthy",
                "redis_version": info.get("redis_version", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "unknown"),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
