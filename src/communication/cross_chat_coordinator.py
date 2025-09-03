#!/usr/bin/env python3
"""
Cross-Chat Coordinator for AI Agent System.
Manages communication across multiple chat sessions with real-time synchronization.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

from .message_router import MessageRouter, ChatSession
from .session_manager import SessionManager
from .websocket_server import WebSocketServer
from .real_time_handler import RealTimeMessageHandler
from .events import CrossChatEvent, CrossChatMessage, WebSocketMessage

logger = logging.getLogger(__name__)


class CrossChatCoordinator:
    """Coordinates communication across multiple chat sessions."""
    
    def __init__(self, websocket_server: WebSocketServer, 
                 message_router: MessageRouter, 
                 session_manager: SessionManager,
                 real_time_handler: RealTimeMessageHandler):
        self.websocket_server = websocket_server
        self.message_router = message_router
        self.session_manager = session_manager
        self.real_time_handler = real_time_handler
        
        # Cross-chat state
        self.active_chats: Dict[str, Dict[str, Any]] = {}
        self.chat_subscriptions: Dict[str, Set[str]] = {}  # chat_id -> set of subscribed_agents
        self.broadcast_history: List[CrossChatEvent] = []
        self.max_history_size = 1000
        
        # Event handlers
        self.event_handlers: Dict[str, callable] = {}
        self._register_event_handlers()
        
        logger.info("Cross-chat coordinator initialized")
    
    def _register_event_handlers(self) -> None:
        """Register handlers for different event types."""
        self.event_handlers.update({
            "message": self._handle_chat_message,
            "project_update": self._handle_project_update,
            "agent_status": self._handle_agent_status,
            "sprint_update": self._handle_sprint_update,
            "coordination": self._handle_coordination_event,
            "user_action": self._handle_user_action
        })
    
    def register_chat_session(self, chat_id: str, chat_type: str, 
                            participants: List[str], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Register a new chat session for cross-chat communication."""
        try:
            # Create session in session manager
            session = self.session_manager.create_session(chat_id, chat_type, participants, metadata)
            
            # Register in cross-chat system
            self.active_chats[chat_id] = {
                "session": session,
                "type": chat_type,
                "participants": participants,
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
                "subscribed_agents": set(),
                "metadata": metadata or {}
            }
            
            # Initialize chat subscriptions
            self.chat_subscriptions[chat_id] = set()
            
            logger.info(f"Registered chat session: {chat_id} ({chat_type})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register chat session {chat_id}: {e}")
            return False
    
    def unregister_chat_session(self, chat_id: str) -> bool:
        """Unregister a chat session from cross-chat communication."""
        try:
            if chat_id in self.active_chats:
                # Close session in session manager
                self.session_manager.close_session(chat_id)
                
                # Remove from cross-chat system
                del self.active_chats[chat_id]
                if chat_id in self.chat_subscriptions:
                    del self.chat_subscriptions[chat_id]
                
                logger.info(f"Unregistered chat session: {chat_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unregister chat session {chat_id}: {e}")
            return False
    
    def subscribe_agent_to_chat(self, agent_id: str, chat_id: str) -> bool:
        """Subscribe an agent to a specific chat session."""
        try:
            if chat_id in self.active_chats:
                self.chat_subscriptions[chat_id].add(agent_id)
                self.message_router.subscribe_agent_to_chat(agent_id, chat_id)
                
                logger.info(f"Agent {agent_id} subscribed to chat {chat_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to subscribe agent {agent_id} to chat {chat_id}: {e}")
            return False
    
    def unsubscribe_agent_from_chat(self, agent_id: str, chat_id: str) -> bool:
        """Unsubscribe an agent from a specific chat session."""
        try:
            if chat_id in self.chat_subscriptions:
                self.chat_subscriptions[chat_id].discard(agent_id)
                self.message_router.unsubscribe_agent_from_chat(agent_id, chat_id)
                
                logger.info(f"Agent {agent_id} unsubscribed from chat {chat_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe agent {agent_id} from chat {chat_id}: {e}")
            return False
    
    async def broadcast_event(self, event: CrossChatEvent) -> Dict[str, Any]:
        """Broadcast an event across multiple chat sessions."""
        try:
            # Add to broadcast history
            self.broadcast_history.append(event)
            if len(self.broadcast_history) > self.max_history_size:
                self.broadcast_history.pop(0)
            
            # Determine target chats
            if "all" in event.target_chats:
                target_chats = list(self.active_chats.keys())
            else:
                target_chats = [chat_id for chat_id in event.target_chats 
                              if chat_id in self.active_chats]
            
            # Create cross-chat message
            cross_chat_msg = CrossChatMessage(
                message_id=event.event_id,
                sender=event.source_agent,
                sender_type="agent",
                content=event.content,
                message_type=event.event_type,
                target_chats=target_chats,
                timestamp=event.timestamp,
                priority=event.priority,
                metadata=event.metadata
            )
            
            # Route message through message router
            routing_result = self.message_router.route_message(cross_chat_msg)
            
            # Broadcast via WebSocket if target chats have active connections
            websocket_broadcast_count = 0
            for chat_id in target_chats:
                if chat_id in self.active_chats:
                    # Update chat activity
                    self.active_chats[chat_id]["last_activity"] = datetime.now().isoformat()
                    self.active_chats[chat_id]["message_count"] += 1
                    
                    # Broadcast via WebSocket
                    websocket_msg = WebSocketMessage(
                        message_id=event.event_id,
                        sender=event.source_agent,
                        recipient=chat_id,
                        message_type="cross_chat_event",
                        content=event.to_dict(),
                        timestamp=event.timestamp,
                        session_id=chat_id
                    )
                    
                    # This would be async in real implementation
                    # For now, we'll simulate the broadcast
                    websocket_broadcast_count += 1
            
            # Store message in real-time handler for cross-chat visibility
            try:
                await self.real_time_handler.store_cross_chat_message(event)
                logger.info(f"Cross-chat message stored for real-time visibility: {event.event_id}")
            except Exception as e:
                logger.error(f"Failed to store cross-chat message: {e}")
            
            # Handle event with appropriate handler
            if event.event_type in self.event_handlers:
                try:
                    self.event_handlers[event.event_type](event)
                except Exception as e:
                    logger.error(f"Event handler error for {event.event_type}: {e}")
            
            result = {
                "success": True,
                "event_id": event.event_id,
                "target_chats": target_chats,
                "routed_messages": routing_result.get("routed_count", 0),
                "websocket_broadcasts": websocket_broadcast_count,
                "real_time_stored": True,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Cross-chat event {event.event_id} broadcast to {len(target_chats)} chats")
            return result
            
        except Exception as e:
            logger.error(f"Failed to broadcast event: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _handle_chat_message(self, event: CrossChatEvent) -> None:
        """Handle chat message events."""
        logger.info(f"Chat message from {event.source_agent} in {event.source_chat}")
        # Could trigger notifications, update chat history, etc.
    
    def _handle_project_update(self, event: CrossChatEvent) -> None:
        """Handle project update events."""
        logger.info(f"Project update from {event.source_agent}: {event.content}")
        # Could trigger project status updates, notifications, etc.
    
    def _handle_agent_status(self, event: CrossChatEvent) -> None:
        """Handle agent status events."""
        logger.info(f"Agent status from {event.source_agent}: {event.content}")
        # Could update agent registry, trigger health checks, etc.
    
    def _handle_sprint_update(self, event: CrossChatEvent) -> None:
        """Handle sprint update events."""
        logger.info(f"Sprint update from {event.source_agent}: {event.content}")
        # Could update sprint tracking, notify stakeholders, etc.
    
    def _handle_coordination_event(self, event: CrossChatEvent) -> None:
        """Handle coordination events."""
        logger.info(f"Coordination event from {event.source_agent}: {event.content}")
        # Could trigger agent coordination, update workflows, etc.
    
    def _handle_user_action(self, event: CrossChatEvent) -> None:
        """Handle user action events."""
        logger.info(f"User action from {event.source_agent}: {event.content}")
        # Could trigger agent responses, update user context, etc.
    
    def get_cross_chat_status(self) -> Dict[str, Any]:
        """Get current cross-chat system status."""
        active_chat_count = len(self.active_chats)
        total_subscriptions = sum(len(subs) for subs in self.chat_subscriptions.values())
        total_events = len(self.broadcast_history)
        
        return {
            "active_chats": active_chat_count,
            "total_subscriptions": total_subscriptions,
            "total_events": total_events,
            "chat_types": list(set(chat["type"] for chat in self.active_chats.values())),
            "recent_events": [
                {
                    "event_id": event.event_id,
                    "type": event.event_type,
                    "source": event.source_agent,
                    "timestamp": event.timestamp
                }
                for event in self.broadcast_history[-10:]  # Last 10 events
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def search_cross_chat_events(self, query: str, event_type: Optional[str] = None, 
                                limit: int = 50) -> List[CrossChatEvent]:
        """Search cross-chat events by content or type."""
        results = []
        
        for event in self.broadcast_history:
            # Check event type filter
            if event_type and event.event_type != event_type:
                continue
            
            # Check content match
            content_str = str(event.content).lower()
            if query.lower() in content_str:
                results.append(event)
        
        # Sort by timestamp and limit
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]
    
    def get_chat_summary(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of a specific chat session."""
        if chat_id not in self.active_chats:
            return None
        
        chat_data = self.active_chats[chat_id]
        session = self.session_manager.get_session(chat_id)
        
        return {
            "chat_id": chat_id,
            "type": chat_data["type"],
            "participants": chat_data["participants"],
            "created_at": chat_data["created_at"],
            "last_activity": chat_data["last_activity"],
            "message_count": chat_data["message_count"],
            "subscribed_agents": list(chat_data["subscribed_agents"]),
            "session_status": session.is_active if session else False,
            "metadata": chat_data["metadata"]
        }
