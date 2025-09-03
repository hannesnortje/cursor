#!/usr/bin/env python3
"""
Cross-Chat Service for AI Agent System.
Integrates all communication components for seamless cross-chat functionality.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from .cross_chat_coordinator import CrossChatCoordinator
from .events import CrossChatEvent
from .websocket_server import WebSocketServer
from .message_router import MessageRouter
from .session_manager import SessionManager

logger = logging.getLogger(__name__)


class CrossChatService:
    """Main service for cross-chat communication functionality."""
    
    def __init__(self, host: str = "localhost", port: int = 4000):
        self.host = host
        self.port = port
        
        # Initialize components
        self.websocket_server = WebSocketServer(host=host, port=port)
        self.message_router = MessageRouter()
        self.session_manager = SessionManager()
        
        # Initialize cross-chat coordinator
        self.coordinator = CrossChatCoordinator(
            websocket_server=self.websocket_server,
            message_router=self.message_router,
            session_manager=self.session_manager
        )
        
        # Service state
        self.is_running = False
        self.start_time = None
        
        logger.info(f"Cross-chat service initialized on {host}:{port}")
    
    def start_service(self) -> Dict[str, Any]:
        """Start the cross-chat service."""
        try:
            if self.is_running:
                return {
                    "success": False,
                    "error": "Service is already running",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Start WebSocket server (this would be async in real implementation)
            # For now, we'll simulate the start
            self.is_running = True
            self.start_time = datetime.now()
            
            logger.info("Cross-chat service started successfully")
            
            return {
                "success": True,
                "message": "Cross-chat service started successfully",
                "websocket_port": self.port,
                "start_time": self.start_time.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to start cross-chat service: {e}")
            self.is_running = False
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def stop_service(self) -> Dict[str, Any]:
        """Stop the cross-chat service."""
        try:
            if not self.is_running:
                return {
                    "success": False,
                    "error": "Service is not running",
                    "timestamp": datetime.now().isoformat()
                }
            
            # Stop WebSocket server
            # self.websocket_server.stop()  # Would be async in real implementation
            
            self.is_running = False
            stop_time = datetime.now()
            
            uptime = (stop_time - self.start_time).total_seconds() if self.start_time else 0
            
            logger.info("Cross-chat service stopped")
            
            return {
                "success": True,
                "message": "Cross-chat service stopped successfully",
                "uptime_seconds": uptime,
                "stop_time": stop_time.isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to stop cross-chat service: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def create_chat_session(self, chat_id: str, chat_type: str, 
                           participants: List[str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new chat session for cross-chat communication."""
        try:
            success = self.coordinator.register_chat_session(chat_id, chat_type, participants, metadata)
            
            if success:
                return {
                    "success": True,
                    "message": f"Chat session {chat_id} created successfully",
                    "chat_id": chat_id,
                    "chat_type": chat_type,
                    "participants": participants,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to create chat session {chat_id}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error creating chat session {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def close_chat_session(self, chat_id: str) -> Dict[str, Any]:
        """Close a chat session."""
        try:
            success = self.coordinator.unregister_chat_session(chat_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Chat session {chat_id} closed successfully",
                    "chat_id": chat_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to close chat session {chat_id}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error closing chat session {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def subscribe_agent(self, agent_id: str, chat_id: str) -> Dict[str, Any]:
        """Subscribe an agent to a chat session."""
        try:
            success = self.coordinator.subscribe_agent_to_chat(agent_id, chat_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Agent {agent_id} subscribed to chat {chat_id}",
                    "agent_id": agent_id,
                    "chat_id": chat_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to subscribe agent {agent_id} to chat {chat_id}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error subscribing agent {agent_id} to chat {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def unsubscribe_agent(self, agent_id: str, chat_id: str) -> Dict[str, Any]:
        """Unsubscribe an agent from a chat session."""
        try:
            success = self.coordinator.unsubscribe_agent_from_chat(agent_id, chat_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"Agent {agent_id} unsubscribed from chat {chat_id}",
                    "agent_id": agent_id,
                    "chat_id": chat_id,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to unsubscribe agent {agent_id} from chat {chat_id}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error unsubscribing agent {agent_id} from chat {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def broadcast_message(self, source_chat: str, source_agent: str, 
                         content: Any, target_chats: List[str], 
                         message_type: str = "message", priority: int = 2) -> Dict[str, Any]:
        """Broadcast a message across multiple chat sessions."""
        try:
            event = CrossChatEvent(
                event_id=f"msg_{datetime.now().timestamp()}",
                event_type=message_type,
                source_chat=source_chat,
                source_agent=source_agent,
                content=content,
                target_chats=target_chats,
                priority=priority
            )
            
            result = await self.coordinator.broadcast_event(event)
            
            if result["success"]:
                return {
                    "success": True,
                    "message": "Message broadcast successfully",
                    "event_id": event.event_id,
                    "target_chats": result["target_chats"],
                    "routed_messages": result["routed_messages"],
                    "websocket_broadcasts": result["websocket_broadcasts"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Unknown broadcast error"),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get comprehensive service status."""
        try:
            cross_chat_status = self.coordinator.get_cross_chat_status()
            session_stats = self.session_manager.get_session_statistics()
            
            return {
                "success": True,
                "service_status": {
                    "is_running": self.is_running,
                    "start_time": self.start_time.isoformat() if self.start_time else None,
                    "uptime_seconds": (datetime.now() - self.start_time).total_seconds() if self.start_time and self.is_running else 0
                },
                "websocket_server": {
                    "host": self.host,
                    "port": self.port,
                    "status": "running" if self.is_running else "stopped"
                },
                "cross_chat": cross_chat_status,
                "sessions": session_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def search_messages(self, query: str, event_type: Optional[str] = None, 
                       limit: int = 50) -> Dict[str, Any]:
        """Search cross-chat messages."""
        try:
            events = self.coordinator.search_cross_chat_events(query, event_type, limit)
            
            return {
                "success": True,
                "query": query,
                "event_type": event_type,
                "results_count": len(events),
                "results": [
                    {
                        "event_id": event.event_id,
                        "type": event.event_type,
                        "source_chat": event.source_chat,
                        "source_agent": event.source_agent,
                        "content": event.content,
                        "timestamp": event.timestamp,
                        "priority": event.priority
                    }
                    for event in events
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_chat_summary(self, chat_id: str) -> Dict[str, Any]:
        """Get summary of a specific chat session."""
        try:
            summary = self.coordinator.get_chat_summary(chat_id)
            
            if summary:
                return {
                    "success": True,
                    "chat_summary": summary,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Chat session {chat_id} not found",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting chat summary for {chat_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
