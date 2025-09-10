#!/usr/bin/env python3
"""
Message Router for AI Agent System.
Handles message routing, cross-chat communication, and message distribution.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChatSession:
    """Represents a chat session."""

    session_id: str
    chat_type: str  # 'coordinator', 'agent', 'user'
    participants: List[str]
    created_at: str
    last_activity: str
    is_active: bool = True


@dataclass
class CrossChatMessage:
    """Message that can be shared across multiple chats."""

    message_id: str
    sender: str
    sender_type: str  # 'agent', 'user', 'coordinator'
    content: Any
    message_type: str  # 'text', 'project_update', 'status', 'command'
    target_chats: List[str]  # List of chat session IDs to receive this message
    timestamp: str
    priority: int = 1  # 1=low, 2=normal, 3=high, 4=urgent
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class MessageRouter:
    """Routes messages across different chat sessions and agents."""

    def __init__(self):
        self.chat_sessions: Dict[str, ChatSession] = {}
        self.message_history: Dict[str, List[CrossChatMessage]] = {}
        self.agent_subscriptions: Dict[str, Set[str]] = (
            {}
        )  # agent_id -> set of chat_ids
        self.message_handlers: Dict[str, callable] = {}

        # Register default message handlers
        self._register_default_handlers()

        logger.info("Message router initialized")

    def _register_default_handlers(self) -> None:
        """Register default message handlers."""
        self.message_handlers.update(
            {
                "project_update": self._handle_project_update,
                "agent_status": self._handle_agent_status,
                "sprint_update": self._handle_sprint_update,
                "coordination": self._handle_coordination_message,
                "user_message": self._handle_user_message,
            }
        )

    def create_chat_session(
        self, session_id: str, chat_type: str, participants: List[str]
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            session_id=session_id,
            chat_type=chat_type,
            participants=participants,
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat(),
        )

        self.chat_sessions[session_id] = session
        self.message_history[session_id] = []

        logger.info(f"Created chat session: {session_id} ({chat_type})")
        return session

    def close_chat_session(self, session_id: str) -> bool:
        """Close a chat session."""
        if session_id in self.chat_sessions:
            self.chat_sessions[session_id].is_active = False
            self.chat_sessions[session_id].last_activity = datetime.now().isoformat()
            logger.info(f"Closed chat session: {session_id}")
            return True
        return False

    def subscribe_agent_to_chat(self, agent_id: str, chat_id: str) -> None:
        """Subscribe an agent to a specific chat session."""
        if agent_id not in self.agent_subscriptions:
            self.agent_subscriptions[agent_id] = set()

        self.agent_subscriptions[agent_id].add(chat_id)
        logger.info(f"Agent {agent_id} subscribed to chat {chat_id}")

    def unsubscribe_agent_from_chat(self, agent_id: str, chat_id: str) -> None:
        """Unsubscribe an agent from a specific chat session."""
        if agent_id in self.agent_subscriptions:
            self.agent_subscriptions[agent_id].discard(chat_id)
            logger.info(f"Agent {agent_id} unsubscribed from chat {chat_id}")

    def route_message(self, message: CrossChatMessage) -> Dict[str, Any]:
        """Route a message to appropriate chat sessions."""
        routed_count = 0
        errors = []

        # Route to target chats
        for chat_id in message.target_chats:
            if chat_id in self.chat_sessions:
                if self.chat_sessions[chat_id].is_active:
                    # Add message to chat history
                    self.message_history[chat_id].append(message)

                    # Update last activity
                    self.chat_sessions[chat_id].last_activity = (
                        datetime.now().isoformat()
                    )

                    routed_count += 1
                    logger.debug(f"Message routed to chat: {chat_id}")
                else:
                    errors.append(f"Chat session {chat_id} is inactive")
            else:
                errors.append(f"Chat session {chat_id} not found")

        # Handle message based on type
        if message.message_type in self.message_handlers:
            try:
                self.message_handlers[message.message_type](message)
            except Exception as e:
                errors.append(f"Handler error: {str(e)}")

        result = {
            "success": len(errors) == 0,
            "routed_count": routed_count,
            "target_chats": message.target_chats,
            "errors": errors,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"Message {message.message_id} routed to {routed_count} chats")
        return result

    def broadcast_to_all_chats(self, message: CrossChatMessage) -> Dict[str, Any]:
        """Broadcast message to all active chat sessions."""
        # Set target chats to all active sessions
        message.target_chats = [
            chat_id
            for chat_id, session in self.chat_sessions.items()
            if session.is_active
        ]

        return self.route_message(message)

    def get_chat_messages(
        self, chat_id: str, limit: int = 100
    ) -> List[CrossChatMessage]:
        """Get message history for a specific chat."""
        if chat_id in self.message_history:
            messages = self.message_history[chat_id]
            return messages[-limit:] if limit > 0 else messages
        return []

    def get_agent_messages(
        self, agent_id: str, limit: int = 100
    ) -> List[CrossChatMessage]:
        """Get messages relevant to a specific agent."""
        messages = []

        if agent_id in self.agent_subscriptions:
            for chat_id in self.agent_subscriptions[agent_id]:
                chat_messages = self.get_chat_messages(chat_id, limit)
                messages.extend(chat_messages)

        # Sort by timestamp and limit
        messages.sort(key=lambda x: x.timestamp)
        return messages[-limit:] if limit > 0 else messages

    def _handle_project_update(self, message: CrossChatMessage) -> None:
        """Handle project update messages."""
        logger.info(f"Project update from {message.sender}: {message.content}")
        # Could trigger notifications, update project status, etc.

    def _handle_agent_status(self, message: CrossChatMessage) -> None:
        """Handle agent status messages."""
        logger.info(f"Agent status from {message.sender}: {message.content}")
        # Could update agent registry, trigger health checks, etc.

    def _handle_sprint_update(self, message: CrossChatMessage) -> None:
        """Handle sprint update messages."""
        logger.info(f"Sprint update from {message.sender}: {message.content}")
        # Could update sprint tracking, notify stakeholders, etc.

    def _handle_coordination_message(self, message: CrossChatMessage) -> None:
        """Handle coordination messages."""
        logger.info(f"Coordination message from {message.sender}: {message.content}")
        # Could trigger agent coordination, update workflows, etc.

    def _handle_user_message(self, message: CrossChatMessage) -> None:
        """Handle user messages."""
        logger.info(f"User message from {message.sender}: {message.content}")
        # Could trigger agent responses, update user context, etc.

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        active_sessions = sum(1 for s in self.chat_sessions.values() if s.is_active)
        total_messages = sum(len(msgs) for msgs in self.message_history.values())

        return {
            "total_chat_sessions": len(self.chat_sessions),
            "active_chat_sessions": active_sessions,
            "total_messages": total_messages,
            "subscribed_agents": len(self.agent_subscriptions),
            "timestamp": datetime.now().isoformat(),
        }

    def search_messages(
        self, query: str, chat_id: Optional[str] = None, limit: int = 50
    ) -> List[CrossChatMessage]:
        """Search messages by content."""
        results = []

        if chat_id:
            # Search in specific chat
            if chat_id in self.message_history:
                messages = self.message_history[chat_id]
                for msg in messages:
                    if query.lower() in str(msg.content).lower():
                        results.append(msg)
        else:
            # Search in all chats
            for chat_messages in self.message_history.values():
                for msg in chat_messages:
                    if query.lower() in str(msg.content).lower():
                        results.append(msg)

        # Sort by timestamp and limit
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
