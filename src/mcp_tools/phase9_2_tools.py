"""MCP tools for Phase 9.2: Enhanced AutoGen Integration."""

import logging
from typing import Dict, Any, List
import asyncio

from ..llm.enhanced_autogen import get_enhanced_autogen

logger = logging.getLogger(__name__)


class Phase9_2MCPTools:
    """MCP tools for Phase 9.2 enhanced AutoGen integration."""
    
    def __init__(self):
        self.enhanced_autogen = None
    
    def _ensure_initialized(self):
        """Ensure enhanced AutoGen is initialized."""
        if not self.enhanced_autogen:
            self.enhanced_autogen = get_enhanced_autogen()
    
    async def create_autogen_agent(self, agent_id: str, role_name: str, 
                                  project_id: str = None) -> Dict[str, Any]:
        """Create an enhanced AutoGen agent with dynamic role assignment."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            agent_id = await self.enhanced_autogen.create_agent(
                agent_id=agent_id,
                role_name=role_name,
                project_id=project_id
            )
            
            agent_info = self.enhanced_autogen.get_agent_info(agent_id)
            
            return {
                "success": True,
                "agent_id": agent_id,
                "agent_info": agent_info,
                "message": f"Enhanced AutoGen agent '{agent_id}' created with role '{role_name}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to create AutoGen agent: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create AutoGen agent"
            }
    
    async def create_autogen_group_chat(self, chat_id: str, agent_ids: List[str], 
                                       project_id: str = None) -> Dict[str, Any]:
        """Create an enhanced AutoGen group chat."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            chat_id = await self.enhanced_autogen.create_group_chat(
                chat_id=chat_id,
                agent_ids=agent_ids,
                project_id=project_id
            )
            
            chat_info = self.enhanced_autogen.get_group_chat_info(chat_id)
            
            return {
                "success": True,
                "chat_id": chat_id,
                "chat_info": chat_info,
                "message": f"Enhanced AutoGen group chat '{chat_id}' created with {len(agent_ids)} agents"
            }
            
        except Exception as e:
            logger.error(f"Failed to create AutoGen group chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create AutoGen group chat"
            }
    
    async def start_autogen_workflow(self, workflow_name: str, project_id: str = None, 
                                   initial_message: str = None) -> Dict[str, Any]:
        """Start a predefined AutoGen workflow."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            result = await self.enhanced_autogen.start_workflow(
                workflow_name=workflow_name,
                project_id=project_id,
                initial_message=initial_message
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to start AutoGen workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start workflow '{workflow_name}'"
            }
    
    async def get_autogen_roles(self) -> Dict[str, Any]:
        """Get available AutoGen agent roles."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            roles = self.enhanced_autogen.get_available_roles()
            
            return {
                "success": True,
                "roles": roles,
                "count": len(roles),
                "message": f"Retrieved {len(roles)} available AutoGen roles"
            }
            
        except Exception as e:
            logger.error(f"Failed to get AutoGen roles: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get AutoGen roles"
            }
    
    async def get_autogen_workflows(self) -> Dict[str, Any]:
        """Get available AutoGen workflow templates."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            workflows = self.enhanced_autogen.get_available_workflows()
            workflow_details = {}
            
            for workflow_name in workflows:
                workflow = self.enhanced_autogen.workflow_templates[workflow_name]
                workflow_details[workflow_name] = {
                    "name": workflow["name"],
                    "description": workflow["description"],
                    "required_roles": workflow["required_roles"],
                    "conversation_type": workflow["conversation_type"]
                }
            
            return {
                "success": True,
                "workflows": workflow_details,
                "count": len(workflows),
                "message": f"Retrieved {len(workflows)} available AutoGen workflows"
            }
            
        except Exception as e:
            logger.error(f"Failed to get AutoGen workflows: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get AutoGen workflows"
            }
    
    async def get_autogen_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about a specific AutoGen agent."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            agent_info = self.enhanced_autogen.get_agent_info(agent_id)
            
            if not agent_info:
                return {
                    "success": False,
                    "error": "Agent not found",
                    "message": f"AutoGen agent '{agent_id}' not found"
                }
            
            return {
                "success": True,
                "agent_info": agent_info,
                "message": f"Retrieved information for AutoGen agent '{agent_id}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to get AutoGen agent info: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get info for agent '{agent_id}'"
            }
    
    async def get_autogen_group_chat_info(self, chat_id: str) -> Dict[str, Any]:
        """Get information about a specific AutoGen group chat."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            chat_info = self.enhanced_autogen.get_group_chat_info(chat_id)
            
            if not chat_info:
                return {
                    "success": False,
                    "error": "Group chat not found",
                    "message": f"AutoGen group chat '{chat_id}' not found"
                }
            
            return {
                "success": True,
                "chat_info": chat_info,
                "message": f"Retrieved information for AutoGen group chat '{chat_id}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to get AutoGen group chat info: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to get info for group chat '{chat_id}'"
            }
    
    async def list_autogen_agents(self) -> Dict[str, Any]:
        """List all AutoGen agents."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            agents = {}
            for agent_id in self.enhanced_autogen.agents:
                agent_info = self.enhanced_autogen.get_agent_info(agent_id)
                if agent_info:
                    agents[agent_id] = agent_info
            
            return {
                "success": True,
                "agents": agents,
                "count": len(agents),
                "message": f"Retrieved {len(agents)} AutoGen agents"
            }
            
        except Exception as e:
            logger.error(f"Failed to list AutoGen agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list AutoGen agents"
            }
    
    async def list_autogen_group_chats(self) -> Dict[str, Any]:
        """List all AutoGen group chats."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            group_chats = {}
            for chat_id in self.enhanced_autogen.group_chats:
                chat_info = self.enhanced_autogen.get_group_chat_info(chat_id)
                if chat_info:
                    group_chats[chat_id] = chat_info
            
            return {
                "success": True,
                "group_chats": group_chats,
                "count": len(group_chats),
                "message": f"Retrieved {len(group_chats)} AutoGen group chats"
            }
            
        except Exception as e:
            logger.error(f"Failed to list AutoGen group chats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list AutoGen group chats"
            }
    
    async def start_autogen_conversation(self, chat_id: str, message: str, 
                                       conversation_type: str = "general") -> Dict[str, Any]:
        """Start a conversation in an AutoGen group chat."""
        try:
            self._ensure_initialized()
            
            if not self.enhanced_autogen.enabled:
                return {
                    "success": False,
                    "error": "Enhanced AutoGen integration not available",
                    "message": "AutoGen is not installed or not available"
                }
            
            if chat_id not in self.enhanced_autogen.group_chats:
                return {
                    "success": False,
                    "error": "Group chat not found",
                    "message": f"AutoGen group chat '{chat_id}' not found"
                }
            
            group_chat = self.enhanced_autogen.group_chats[chat_id]
            result = await group_chat.start_conversation(message, conversation_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to start AutoGen conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start conversation in group chat '{chat_id}'"
            }


# Global instance for synchronous access
_phase9_2_tools = None

def get_phase9_2_tools():
    """Get the global Phase9_2MCPTools instance."""
    global _phase9_2_tools
    if _phase9_2_tools is None:
        _phase9_2_tools = Phase9_2MCPTools()
    return _phase9_2_tools


# Synchronous wrapper functions for MCP server
def create_autogen_agent(agent_id: str, role_name: str, project_id: str = None) -> Dict[str, Any]:
    """Create an enhanced AutoGen agent (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.create_autogen_agent(agent_id, role_name, project_id))

def create_autogen_group_chat(chat_id: str, agent_ids: List[str], project_id: str = None) -> Dict[str, Any]:
    """Create an enhanced AutoGen group chat (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.create_autogen_group_chat(chat_id, agent_ids, project_id))

def start_autogen_workflow(workflow_name: str, project_id: str = None, initial_message: str = None) -> Dict[str, Any]:
    """Start a predefined AutoGen workflow (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.start_autogen_workflow(workflow_name, project_id, initial_message))

def get_autogen_roles() -> Dict[str, Any]:
    """Get available AutoGen agent roles (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.get_autogen_roles())

def get_autogen_workflows() -> Dict[str, Any]:
    """Get available AutoGen workflow templates (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.get_autogen_workflows())

def get_autogen_agent_info(agent_id: str) -> Dict[str, Any]:
    """Get information about a specific AutoGen agent (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.get_autogen_agent_info(agent_id))

def get_autogen_group_chat_info(chat_id: str) -> Dict[str, Any]:
    """Get information about a specific AutoGen group chat (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.get_autogen_group_chat_info(chat_id))

def list_autogen_agents() -> Dict[str, Any]:
    """List all AutoGen agents (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.list_autogen_agents())

def list_autogen_group_chats() -> Dict[str, Any]:
    """List all AutoGen group chats (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.list_autogen_group_chats())

def start_autogen_conversation(chat_id: str, message: str, conversation_type: str = "general") -> Dict[str, Any]:
    """Start a conversation in an AutoGen group chat (synchronous wrapper)."""
    tools = get_phase9_2_tools()
    return asyncio.run(tools.start_autogen_conversation(chat_id, message, conversation_type))
