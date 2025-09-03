"""Enhanced communication system with AutoGen and Qdrant integration."""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
import uuid

from src.llm import autogen_integration, llm_gateway
from src.database import vector_store

logger = logging.getLogger(__name__)


class EnhancedCommunicationSystem:
    """Enhanced communication system with AutoGen and Qdrant integration."""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.cross_chat_visibility: Dict[str, Set[str]] = {}
        self.agent_conversations: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize components
        self.autogen = autogen_integration
        self.llm_gateway = llm_gateway
        self.vector_store = vector_store
        
        logger.info("Enhanced communication system initialized")
    
    async def create_session(self, session_id: str, agent_ids: List[str], 
                           session_type: str = "general") -> Dict[str, Any]:
        """Create a new communication session."""
        try:
            session = {
                "id": session_id,
                "agent_ids": agent_ids,
                "session_type": session_type,
                "created_at": datetime.now(),
                "messages": [],
                "autogen_chat_id": None,
                "context": {}
            }
            
            # Create AutoGen group chat if available
            if self.autogen.enabled:
                try:
                    autogen_chat_id = await self.autogen.create_group_chat(
                        f"session_{session_id}", agent_ids
                    )
                    session["autogen_chat_id"] = autogen_chat_id
                    logger.info(f"Created AutoGen group chat: {autogen_chat_id}")
                except Exception as e:
                    logger.warning(f"Failed to create AutoGen group chat: {e}")
            
            self.active_sessions[session_id] = session
            
            # Initialize cross-chat visibility
            for agent_id in agent_ids:
                if agent_id not in self.cross_chat_visibility:
                    self.cross_chat_visibility[agent_id] = set()
                self.cross_chat_visibility[agent_id].add(session_id)
            
            logger.info(f"Created communication session: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def send_message(self, session_id: str, agent_id: str, 
                          message: str, message_type: str = "text",
                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a message in a session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            # Create message object
            message_obj = {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "agent_id": agent_id,
                "message": message,
                "message_type": message_type,
                "timestamp": datetime.now(),
                "context": context or {}
            }
            
            # Add to session messages
            session["messages"].append(message_obj)
            
            # Store in vector database if available
            if self.vector_store:
                try:
                    from src.database.qdrant.vector_store import ConversationPoint
                    
                    conversation_point = ConversationPoint(
                        id=message_obj["id"],
                        session_id=session_id,
                        agent_id=agent_id,
                        agent_type="agent",  # Could be enhanced
                        message=message,
                        context=str(context) if context else "",
                        timestamp=message_obj["timestamp"],
                        metadata={
                            "message_type": message_type,
                            "session_type": session["session_type"]
                        }
                    )
                    
                    await self.vector_store.store_conversation(conversation_point)
                    logger.debug(f"Stored conversation in vector database: {message_obj['id']}")
                    
                except Exception as e:
                    logger.warning(f"Failed to store in vector database: {e}")
            
            # Process with AutoGen if available
            if self.autogen.enabled and session["autogen_chat_id"]:
                try:
                    autogen_response = await self.autogen.add_group_message(
                        session["autogen_chat_id"], agent_id, message
                    )
                    message_obj["autogen_response"] = autogen_response
                    logger.debug(f"AutoGen processed message: {autogen_response}")
                    
                except Exception as e:
                    logger.warning(f"AutoGen processing failed: {e}")
            
            # Update agent conversations
            if agent_id not in self.agent_conversations:
                self.agent_conversations[agent_id] = []
            self.agent_conversations[agent_id].append(message_obj)
            
            logger.info(f"Message sent in session {session_id} by {agent_id}")
            return message_obj
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise
    
    async def get_session_messages(self, session_id: str, 
                                 limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages from a session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            messages = session["messages"][-limit:] if limit > 0 else session["messages"]
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get session messages: {e}")
            return []
    
    async def get_agent_conversations(self, agent_id: str, 
                                    limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for an agent."""
        try:
            if agent_id not in self.agent_conversations:
                return []
            
            conversations = self.agent_conversations[agent_id][-limit:] if limit > 0 else self.agent_conversations[agent_id]
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get agent conversations: {e}")
            return []
    
    async def search_conversations(self, query: str, session_id: Optional[str] = None,
                                 agent_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations using vector database."""
        try:
            if not self.vector_store:
                logger.warning("Vector store not available for search")
                return []
            
            # Search in vector database
            results = await self.vector_store.search_conversations(
                query, session_id, agent_id, limit
            )
            
            # Convert to our format
            search_results = []
            for result in results:
                search_results.append({
                    "id": result.id,
                    "session_id": result.session_id,
                    "agent_id": result.agent_id,
                    "agent_type": result.agent_type,
                    "message": result.message,
                    "context": result.context,
                    "timestamp": result.timestamp,
                    "metadata": result.metadata
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
    
    async def get_cross_chat_visibility(self, agent_id: str) -> List[str]:
        """Get sessions visible to an agent."""
        try:
            return list(self.cross_chat_visibility.get(agent_id, set()))
            
        except Exception as e:
            logger.error(f"Failed to get cross-chat visibility: {e}")
            return []
    
    async def add_agent_to_session(self, session_id: str, agent_id: str) -> bool:
        """Add an agent to an existing session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            if agent_id not in session["agent_ids"]:
                session["agent_ids"].append(agent_id)
                
                # Update cross-chat visibility
                if agent_id not in self.cross_chat_visibility:
                    self.cross_chat_visibility[agent_id] = set()
                self.cross_chat_visibility[agent_id].add(session_id)
                
                # Add to AutoGen group chat if available
                if self.autogen.enabled and session["autogen_chat_id"]:
                    try:
                        # Note: AutoGen doesn't support adding agents to existing chats
                        # We'd need to recreate the chat or handle this differently
                        logger.info(f"Agent {agent_id} added to session {session_id}")
                    except Exception as e:
                        logger.warning(f"Failed to add agent to AutoGen chat: {e}")
                
                logger.info(f"Agent {agent_id} added to session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to add agent to session: {e}")
            return False
    
    async def remove_agent_from_session(self, session_id: str, agent_id: str) -> bool:
        """Remove an agent from a session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            if agent_id in session["agent_ids"]:
                session["agent_ids"].remove(agent_id)
                
                # Update cross-chat visibility
                if agent_id in self.cross_chat_visibility:
                    self.cross_chat_visibility[agent_id].discard(session_id)
                
                logger.info(f"Agent {agent_id} removed from session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove agent from session: {e}")
            return False
    
    async def close_session(self, session_id: str) -> bool:
        """Close a communication session."""
        try:
            if session_id not in self.active_sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.active_sessions[session_id]
            
            # Remove from cross-chat visibility
            for agent_id in session["agent_ids"]:
                if agent_id in self.cross_chat_visibility:
                    self.cross_chat_visibility[agent_id].discard(session_id)
            
            # Clean up AutoGen chat if available
            if self.autogen.enabled and session["autogen_chat_id"]:
                try:
                    # Note: AutoGen doesn't have a direct close method
                    # We'd need to implement cleanup logic
                    logger.info(f"AutoGen chat {session['autogen_chat_id']} marked for cleanup")
                except Exception as e:
                    logger.warning(f"Failed to cleanup AutoGen chat: {e}")
            
            # Remove session
            del self.active_sessions[session_id]
            
            logger.info(f"Session {session_id} closed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close session: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and statistics."""
        try:
            status = {
                "active_sessions": len(self.active_sessions),
                "total_agents": len(self.cross_chat_visibility),
                "autogen_enabled": self.autogen.enabled,
                "vector_store_available": self.vector_store is not None,
                "llm_gateway_available": self.llm_gateway is not None
            }
            
            # Add AutoGen stats if available
            if self.autogen.enabled:
                status["autogen_agents"] = len(self.autogen.list_agents())
                status["autogen_group_chats"] = len(self.autogen.list_group_chats())
            
            # Add vector store stats if available
            if self.vector_store:
                try:
                    stats = asyncio.run(self.vector_store.get_collection_stats())
                    status["vector_store_stats"] = stats
                except Exception as e:
                    logger.warning(f"Failed to get vector store stats: {e}")
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}


# Global enhanced communication system instance
enhanced_communication = EnhancedCommunicationSystem()
