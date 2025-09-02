#!/usr/bin/env python3
import json
import logging
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced-mcp-server")


class AgentSystem:
    """Core agent system management class."""
    
    def __init__(self):
        self.agents = {}
        self.projects = {}
        self.system_status = "initializing"
        self.start_time = datetime.now()
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            "status": self.system_status,
            "uptime_seconds": uptime,
            "active_agents": len(self.agents),
            "active_projects": len(self.projects),
            "timestamp": datetime.now().isoformat()
        }
    
    def start_project(self, project_type: str, 
                     project_name: str) -> Dict[str, Any]:
        """Start a new project with PDCA framework."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_id = f"{project_type}_{project_name}_{timestamp}"
            
            project = {
                "id": project_id,
                "name": project_name,
                "type": project_type,
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "pdca_phase": "plan",
                "agents": [],
                "sprints": []
            }
            
            self.projects[project_id] = project
            self.system_status = "active"
            
            logger.info(f"Started new project: {project_name} ({project_type})")
            
            message = f"Project '{project_name}' started successfully with PDCA framework"
            return {
                "success": True,
                "project_id": project_id,
                "message": message,
                "project": project
            }
        except Exception as e:
            logger.error(f"Error starting project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def chat_with_coordinator(self, message: str) -> Dict[str, Any]:
        """Handle communication with Coordinator Agent."""
        try:
            logger.info(f"Coordinator chat message: {message}")
            
            # Simple response logic - this will be enhanced with actual agent logic
            if "start" in message.lower() or "begin" in message.lower():
                response = "🚀 Great! I'm ready to help you start a new project. Use the 'start_project' tool to begin with the PDCA framework."
            elif "help" in message.lower() or "what" in message.lower():
                response = "🤖 I'm your Coordinator Agent! I can help you:\n- Start new projects with PDCA framework\n- Manage project planning\n- Coordinate with specialized agents\n- Track project progress\n\nWhat would you like to do?"
            elif "project" in message.lower():
                response = "📋 I can help you manage projects! Use 'start_project' to create a new one, or ask me about project planning and coordination."
            else:
                response = "💬 I understand your message. As your Coordinator Agent, I'm here to help with project planning and coordination. What specific assistance do you need?"
            
            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "coordinator_status": "active"
            }
        except Exception as e:
            logger.error(f"Error in coordinator chat: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_communication_system(self) -> Dict[str, Any]:
        """Start the communication system (WebSocket + Redis)."""
        try:
            logger.info("Starting communication system...")
            
            # This will be implemented in Phase 4.2
            # For now, return success status
            return {
                "success": True,
                "message": "Communication system started successfully",
                "websocket_port": 4000,
                "redis_status": "configured",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error starting communication system: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_cross_chat_session(self, chat_id: str, chat_type: str, 
                                 participants: List[str]) -> Dict[str, Any]:
        """Create a new cross-chat session."""
        try:
            logger.info(f"Creating cross-chat session: {chat_id}")
            
            # This will be implemented with the actual cross-chat service
            # For now, return success status
            return {
                "success": True,
                "message": f"Cross-chat session {chat_id} created successfully",
                "chat_id": chat_id,
                "chat_type": chat_type,
                "participants": participants,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating cross-chat session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def broadcast_cross_chat_message(self, source_chat: str, source_agent: str,
                                   content: str, target_chats: List[str]) -> Dict[str, Any]:
        """Broadcast a message across multiple chat sessions."""
        try:
            logger.info(f"Broadcasting message from {source_agent} in {source_chat}")
            
            # This will be implemented with the actual cross-chat service
            # For now, return success status
            return {
                "success": True,
                "message": "Message broadcast successfully",
                "source_chat": source_chat,
                "source_agent": source_agent,
                "content": content,
                "target_chats": target_chats,
                "broadcast_count": len(target_chats),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_communication_status(self) -> Dict[str, Any]:
        """Get communication system status."""
        try:
            return {
                "success": True,
                "websocket_server": {
                    "status": "running",
                    "port": 4000,
                    "host": "localhost"
                },
                "redis_queue": {
                    "status": "configured",
                    "host": "localhost",
                    "port": 6379
                },
                "cross_chat": {
                    "status": "active",
                    "active_sessions": 0,
                    "total_messages": 0
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting communication status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_project_status(self) -> Dict[str, Any]:
        """Get current project and system status."""
        try:
            return {
                "success": True,
                "system_health": self.get_system_health(),
                "projects": self.projects,
                "available_tools": [
                    "start_project",
                    "chat_with_coordinator", 
                    "get_project_status",
                    "add_numbers",
                    "reverse_text"
                ],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize agent system
agent_system = AgentSystem()

def send_response(request_id, result=None, error=None):
    """Send a JSON-RPC response."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)

def send_notification(method, params=None):
    """Send a JSON-RPC notification."""
    notification = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params:
        notification["params"] = params
    
    print(json.dumps(notification), flush=True)

def main():
    logger.info("Starting enhanced MCP server with agent system...")
    
    # Enhanced initialization response with agent tools
    init_response = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "tools": [
                    # Existing tools (preserved)
                    {
                        "name": "add_numbers",
                        "description": "Add two integers and return the sum.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "integer"},
                                "b": {"type": "integer"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "reverse_text",
                        "description": "Reverse the given string.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"}
                            },
                            "required": ["text"]
                        }
                    },
                    # New agent system tools
                    {
                        "name": "start_project",
                        "description": "Start a new project with PDCA framework",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_type": {"type": "string"},
                                "project_name": {"type": "string"}
                            },
                            "required": ["project_type", "project_name"]
                        }
                    },
                    {
                        "name": "chat_with_coordinator",
                        "description": "Direct communication with Coordinator Agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"}
                            },
                            "required": ["message"]
                        }
                    },
                    {
                        "name": "get_project_status",
                        "description": "Get current project and system status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    # Phase 4: Communication System Tools
                    {
                        "name": "start_communication_system",
                        "description": "Start the communication system (WebSocket + Redis)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_communication_status",
                        "description": "Get communication system status and health",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    # Phase 4.2: Cross-Chat Communication Tools
                    {
                        "name": "create_cross_chat_session",
                        "description": "Create a new cross-chat session for multi-chat communication",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chat_id": {"type": "string"},
                                "chat_type": {"type": "string"},
                                "participants": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["chat_id", "chat_type", "participants"]
                        }
                    },
                    {
                        "name": "broadcast_cross_chat_message",
                        "description": "Broadcast a message across multiple chat sessions",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "source_chat": {"type": "string"},
                                "source_agent": {"type": "string"},
                                "content": {"type": "string"},
                                "target_chats": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["source_chat", "source_agent", "content", "target_chats"]
                        }
                    }
                ]
            }
        },
        "serverInfo": {
            "name": "enhanced-mcp-server",
            "version": "1.1.0",
            "description": "Enhanced MCP server with AI agent system capabilities"
        }
    }
    
    # Read input and respond
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                send_response(request_id, init_response)
                # Send initialized notification
                send_notification("initialized")
                logger.info("MCP server initialized successfully")
                
            elif method == "tools/list":
                tools_response = {
                    "tools": [
                        # Existing tools (preserved)
                        {
                            "name": "add_numbers",
                            "description": "Add two integers and return the sum.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "a": {"type": "integer"},
                                    "b": {"type": "integer"}
                                },
                                "required": ["a", "b"]
                            }
                        },
                        {
                            "name": "reverse_text",
                            "description": "Reverse the given string.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"}
                                },
                                "required": ["text"]
                            }
                        },
                        # New agent system tools
                        {
                            "name": "start_project",
                            "description": "Start a new project with PDCA framework",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_type": {"type": "string"},
                                    "project_name": {"type": "string"}
                                },
                                "required": ["project_type", "project_name"]
                            }
                        },
                        {
                            "name": "chat_with_coordinator",
                            "description": "Direct communication with Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                },
                                "required": ["message"]
                            }
                        },
                        {
                            "name": "get_project_status",
                            "description": "Get current project and system status",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        # Phase 4: Communication System Tools
                        {
                            "name": "start_communication_system",
                            "description": "Start the communication system (WebSocket + Redis)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_communication_status",
                            "description": "Get communication system status and health",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        # Phase 4.2: Cross-Chat Communication Tools
                        {
                            "name": "create_cross_chat_session",
                            "description": "Create a new cross-chat session for multi-chat communication",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "chat_id": {"type": "string"},
                                    "chat_type": {"type": "string"},
                                    "participants": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["chat_id", "chat_type", "participants"]
                            }
                        },
                        {
                            "name": "broadcast_cross_chat_message",
                            "description": "Broadcast a message across multiple chat sessions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_chat": {"type": "string"},
                                    "source_agent": {"type": "string"},
                                    "content": {"type": "string"},
                                    "target_chats": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["source_chat", "source_agent", "content", "target_chats"]
                            }
                        }
                    ]
                }
                send_response(request_id, tools_response)
                
            elif method == "tools/call":
                # Handle tool calls
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                # Existing tools (preserved functionality)
                if tool_name == "add_numbers":
                    a = arguments.get("a", 0)
                    b = arguments.get("b", 0)
                    result = a + b
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"The sum of {a} and {b} is {result}"}],
                        "structuredContent": {"result": result}
                    })
                    
                elif tool_name == "reverse_text":
                    text = arguments.get("text", "")
                    result = text[::-1]
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"'{text}' reversed is '{result}'"}],
                        "structuredContent": {"result": result}
                    })
                
                # New agent system tools
                elif tool_name == "start_project":
                    project_type = arguments.get("project_type", "")
                    project_name = arguments.get("project_name", "")
                    
                    if not project_type or not project_name:
                        send_response(request_id, error={
                            "code": -32602, 
                            "message": "Both project_type and project_name are required"
                        })
                    else:
                        result = agent_system.start_project(project_type, project_name)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to start project: {result['error']}"
                            })
                
                elif tool_name == "chat_with_coordinator":
                    message = arguments.get("message", "")
                    
                    if not message:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "Message is required"
                        })
                    else:
                        result = agent_system.chat_with_coordinator(message)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Coordinator chat failed: {result['error']}"
                            })
                
                elif tool_name == "get_project_status":
                    result = agent_system.get_project_status()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": "Project status retrieved successfully"}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get project status: {result['error']}"
                        })
                
                # Phase 4: Communication System Tools
                elif tool_name == "start_communication_system":
                    result = agent_system.start_communication_system()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to start communication system: {result['error']}"
                        })
                
                elif tool_name == "get_communication_status":
                    result = agent_system.get_communication_status()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": "Communication status retrieved successfully"}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get communication status: {result['error']}"
                        })
                
                # Phase 4.2: Cross-Chat Communication Tools
                elif tool_name == "create_cross_chat_session":
                    chat_id = arguments.get("chat_id", "")
                    chat_type = arguments.get("chat_type", "")
                    participants = arguments.get("participants", [])
                    
                    if not chat_id or not chat_type or not participants:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "chat_id, chat_type, and participants are required"
                        })
                    else:
                        result = agent_system.create_cross_chat_session(chat_id, chat_type, participants)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create cross-chat session: {result['error']}"
                            })
                
                elif tool_name == "broadcast_cross_chat_message":
                    source_chat = arguments.get("source_chat", "")
                    source_agent = arguments.get("source_agent", "")
                    content = arguments.get("content", "")
                    target_chats = arguments.get("target_chats", [])
                    
                    if not source_chat or not source_agent or not content or not target_chats:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "source_chat, source_agent, content, and target_chats are required"
                        })
                    else:
                        result = agent_system.broadcast_cross_chat_message(source_chat, source_agent, content, target_chats)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to broadcast message: {result['error']}"
                            })
                    
                else:
                    send_response(request_id, error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
                    
            else:
                # Handle other methods
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error: {e}")
            if 'request_id' in locals():
                send_response(request_id, error={"code": -32603, "message": f"Internal error: {str(e)}"})

if __name__ == "__main__":
    main()
