#!/usr/bin/env python3
"""Communication event classes for cross-chat system."""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid


@dataclass
class CrossChatEvent:
    """Cross-chat event for broadcasting across chat sessions."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "message"
    source_chat: str = ""
    source_agent: str = ""
    content: Any = ""
    target_chats: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "source_chat": self.source_chat,
            "source_agent": self.source_agent,
            "content": self.content,
            "target_chats": self.target_chats,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "metadata": self.metadata
        }


@dataclass
class CrossChatMessage:
    """Cross-chat message for routing and delivery."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    sender_type: str = "agent"
    content: Any = ""
    message_type: str = "message"
    target_chats: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: int = 2
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "sender_type": self.sender_type,
            "content": self.content,
            "message_type": self.message_type,
            "target_chats": self.target_chats,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "metadata": self.metadata
        }


@dataclass
class WebSocketMessage:
    """WebSocket message for real-time communication."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: str = ""
    message_type: str = "message"
    content: Any = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    session_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message_id": self.message_id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
