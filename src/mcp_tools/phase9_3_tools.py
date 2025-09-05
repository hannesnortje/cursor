"""MCP tools for Phase 9.3: Advanced Communication Features."""

import logging
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from ..communication.phase9_3_advanced_communication import (
    get_phase9_3_communication, AdvancedMessage, MessageType, 
    MessagePriority, CompressionType
)

logger = logging.getLogger(__name__)


class Phase9_3MCPTools:
    """MCP tools for Phase 9.3 advanced communication features."""
    
    def __init__(self):
        self.advanced_comm = None
    
    def _ensure_initialized(self):
        """Ensure advanced communication system is initialized."""
        if not self.advanced_comm:
            self.advanced_comm = get_phase9_3_communication()
    
    async def start_advanced_communication(self) -> Dict[str, Any]:
        """Start the advanced communication system."""
        try:
            self._ensure_initialized()
            await self.advanced_comm.start()
            
            return {
                "success": True,
                "message": "Advanced communication system started successfully",
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Failed to start advanced communication: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start advanced communication system"
            }
    
    async def stop_advanced_communication(self) -> Dict[str, Any]:
        """Stop the advanced communication system."""
        try:
            self._ensure_initialized()
            await self.advanced_comm.stop()
            
            return {
                "success": True,
                "message": "Advanced communication system stopped successfully",
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop advanced communication: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to stop advanced communication system"
            }
    
    async def send_advanced_message(self, sender: str, recipient: str, 
                                  message_type: str, content: Any, 
                                  priority: str = "NORMAL", project_id: str = None,
                                  session_id: str = None, compression: str = "NONE") -> Dict[str, Any]:
        """Send a message through the advanced communication system."""
        try:
            self._ensure_initialized()
            
            # Convert string enums to actual enums
            msg_type = MessageType(message_type.lower())
            
            # Convert priority string to enum
            priority_map = {
                "LOW": MessagePriority.LOW,
                "NORMAL": MessagePriority.NORMAL,
                "HIGH": MessagePriority.HIGH,
                "URGENT": MessagePriority.URGENT,
                "CRITICAL": MessagePriority.CRITICAL
            }
            msg_priority = priority_map.get(priority.upper(), MessagePriority.NORMAL)
            
            comp_type = CompressionType(compression.lower())
            
            # Create advanced message
            message = AdvancedMessage(
                sender=sender,
                recipient=recipient,
                message_type=msg_type,
                priority=msg_priority,
                content=content,
                project_id=project_id,
                session_id=session_id,
                compression=comp_type
            )
            
            # Send message
            success = await self.advanced_comm.send_message(message)
            
            if success:
                return {
                    "success": True,
                    "message_id": message.id,
                    "message": f"Message sent successfully from {sender} to {recipient}",
                    "priority": priority,
                    "compression": compression
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to send message",
                    "message": "Message could not be sent"
                }
            
        except Exception as e:
            logger.error(f"Failed to send advanced message: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to send advanced message"
            }
    
    async def get_communication_analytics(self) -> Dict[str, Any]:
        """Get communication analytics and performance metrics."""
        try:
            self._ensure_initialized()
            analytics = await self.advanced_comm.get_analytics()
            
            return {
                "success": True,
                "analytics": analytics,
                "message": "Retrieved communication analytics successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get communication analytics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve communication analytics"
            }
    
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current message queue status."""
        try:
            self._ensure_initialized()
            queue_status = await self.advanced_comm.get_queue_status()
            
            return {
                "success": True,
                "queue_status": queue_status,
                "message": "Retrieved queue status successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get queue status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve queue status"
            }
    
    async def enable_cross_project_communication(self, project1: str, project2: str) -> Dict[str, Any]:
        """Enable cross-project communication between two projects."""
        try:
            self._ensure_initialized()
            await self.advanced_comm.enable_cross_project_communication(project1, project2)
            
            return {
                "success": True,
                "message": f"Enabled cross-project communication between {project1} and {project2}",
                "project1": project1,
                "project2": project2
            }
            
        except Exception as e:
            logger.error(f"Failed to enable cross-project communication: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to enable cross-project communication between {project1} and {project2}"
            }
    
    async def disable_cross_project_communication(self, project1: str, project2: str) -> Dict[str, Any]:
        """Disable cross-project communication between two projects."""
        try:
            self._ensure_initialized()
            await self.advanced_comm.disable_cross_project_communication(project1, project2)
            
            return {
                "success": True,
                "message": f"Disabled cross-project communication between {project1} and {project2}",
                "project1": project1,
                "project2": project2
            }
            
        except Exception as e:
            logger.error(f"Failed to disable cross-project communication: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to disable cross-project communication between {project1} and {project2}"
            }
    
    async def share_knowledge_between_projects(self, source_project: str, target_project: str, 
                                             knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Share knowledge between projects."""
        try:
            self._ensure_initialized()
            success = await self.advanced_comm.share_knowledge_between_projects(
                source_project, target_project, knowledge
            )
            
            if success:
                return {
                    "success": True,
                    "message": f"Knowledge shared successfully from {source_project} to {target_project}",
                    "source_project": source_project,
                    "target_project": target_project,
                    "knowledge_type": knowledge.get("type", "general")
                }
            else:
                return {
                    "success": False,
                    "error": "Knowledge sharing failed",
                    "message": f"Failed to share knowledge from {source_project} to {target_project}"
                }
            
        except Exception as e:
            logger.error(f"Failed to share knowledge between projects: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to share knowledge between {source_project} and {target_project}"
            }
    
    async def get_compression_stats(self) -> Dict[str, Any]:
        """Get message compression statistics."""
        try:
            self._ensure_initialized()
            compression_stats = self.advanced_comm.compressor.compression_stats
            
            # Calculate compression ratios
            ratios = {}
            for algorithm, stats in compression_stats.items():
                if stats["total_original"] > 0:
                    ratio = 1.0 - (stats["total_compressed"] / stats["total_original"])
                    ratios[algorithm] = ratio
                else:
                    ratios[algorithm] = 0.0
            
            return {
                "success": True,
                "compression_stats": compression_stats,
                "compression_ratios": ratios,
                "message": "Retrieved compression statistics successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get compression stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve compression statistics"
            }
    
    async def get_available_message_types(self) -> Dict[str, Any]:
        """Get available message types."""
        try:
            message_types = [msg_type.value for msg_type in MessageType]
            priorities = [priority.value for priority in MessagePriority]
            compression_types = [comp_type.value for comp_type in CompressionType]
            
            return {
                "success": True,
                "message_types": message_types,
                "priorities": priorities,
                "compression_types": compression_types,
                "message": "Retrieved available message types and options"
            }
            
        except Exception as e:
            logger.error(f"Failed to get available message types: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve available message types"
            }
    
    async def get_communication_health(self) -> Dict[str, Any]:
        """Get communication system health status."""
        try:
            self._ensure_initialized()
            analytics = await self.advanced_comm.get_analytics()
            queue_status = await self.advanced_comm.get_queue_status()
            
            health_score = analytics.get("health_score", 0)
            is_healthy = health_score > 70
            
            return {
                "success": True,
                "health_score": health_score,
                "is_healthy": is_healthy,
                "status": "healthy" if is_healthy else "degraded",
                "uptime": analytics.get("uptime", 0),
                "messages_processed": analytics.get("performance_metrics", {}).get("messages_processed", 0),
                "error_count": analytics.get("performance_metrics", {}).get("error_count", 0),
                "queue_status": queue_status,
                "message": f"Communication system is {'healthy' if is_healthy else 'degraded'} (score: {health_score:.1f})"
            }
            
        except Exception as e:
            logger.error(f"Failed to get communication health: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve communication health status"
            }


# Global instance for synchronous access
_phase9_3_tools = None

def get_phase9_3_tools():
    """Get the global Phase9_3MCPTools instance."""
    global _phase9_3_tools
    if _phase9_3_tools is None:
        _phase9_3_tools = Phase9_3MCPTools()
    return _phase9_3_tools


# Synchronous wrapper functions for MCP server
def start_advanced_communication() -> Dict[str, Any]:
    """Start the advanced communication system (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.start_advanced_communication())

def stop_advanced_communication() -> Dict[str, Any]:
    """Stop the advanced communication system (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.stop_advanced_communication())

def send_advanced_message(sender: str, recipient: str, message_type: str, content: Any, 
                         priority: str = "NORMAL", project_id: str = None, 
                         session_id: str = None, compression: str = "NONE") -> Dict[str, Any]:
    """Send a message through the advanced communication system (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.send_advanced_message(sender, recipient, message_type, content, 
                                                  priority, project_id, session_id, compression))

def get_communication_analytics() -> Dict[str, Any]:
    """Get communication analytics and performance metrics (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.get_communication_analytics())

def get_queue_status() -> Dict[str, Any]:
    """Get current message queue status (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.get_queue_status())

def enable_cross_project_communication(project1: str, project2: str) -> Dict[str, Any]:
    """Enable cross-project communication between two projects (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.enable_cross_project_communication(project1, project2))

def disable_cross_project_communication(project1: str, project2: str) -> Dict[str, Any]:
    """Disable cross-project communication between two projects (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.disable_cross_project_communication(project1, project2))

def share_knowledge_between_projects(source_project: str, target_project: str, 
                                   knowledge: Dict[str, Any]) -> Dict[str, Any]:
    """Share knowledge between projects (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.share_knowledge_between_projects(source_project, target_project, knowledge))

def get_compression_stats() -> Dict[str, Any]:
    """Get message compression statistics (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.get_compression_stats())

def get_available_message_types() -> Dict[str, Any]:
    """Get available message types (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.get_available_message_types())

def get_communication_health() -> Dict[str, Any]:
    """Get communication system health status (synchronous wrapper)."""
    tools = get_phase9_3_tools()
    return asyncio.run(tools.get_communication_health())
