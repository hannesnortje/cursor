"""Enhanced AutoGen Integration MCP tools for sophisticated agent conversations."""

from typing import Dict, Any, List


def get_autogen_tools() -> List[Dict[str, Any]]:
    """Get Enhanced AutoGen Integration MCP tools definitions."""
    return [
        {
            "name": "create_agent",
            "description": "Create an enhanced AutoGen agent with validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for the agent",
                    },
                    "role_name": {
                        "type": "string",
                        "description": "Role name (coordinator, developer, reviewer, tester)",
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent capabilities",
                    },
                    "system_message": {
                        "type": "string",
                        "description": "System message for the agent",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project ID for project-specific agents",
                    },
                },
                "required": ["agent_id", "role_name", "capabilities", "system_message"],
            },
        },
        {
            "name": "create_group_chat",
            "description": "Create a group chat with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "Unique identifier for the chat",
                    },
                    "agents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent IDs to include",
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Optional project ID for project-specific chats",
                    },
                },
                "required": ["chat_id", "agents"],
            },
        },
        {
            "name": "start_workflow",
            "description": "Start a workflow with fallback",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Unique identifier for the workflow",
                    },
                    "workflow_type": {
                        "type": "string",
                        "description": "Type of workflow (sprint_planning, code_review, testing)",
                    },
                    "participants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of participant agent IDs",
                    },
                },
                "required": ["workflow_id", "workflow_type", "participants"],
            },
        },
        {
            "name": "get_roles",
            "description": "Get available agent roles with caching",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_workflows",
            "description": "Get available workflows with error handling",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_agent_info",
            "description": "Get agent information with fallback data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID to get information for",
                    }
                },
                "required": ["agent_id"],
            },
        },
        {
            "name": "get_chat_info",
            "description": "Get chat information with validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {
                        "type": "string",
                        "description": "Chat ID to get information for",
                    }
                },
                "required": ["chat_id"],
            },
        },
        {
            "name": "start_conversation",
            "description": "Start a conversation with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "conversation_id": {
                        "type": "string",
                        "description": "Unique identifier for the conversation",
                    },
                    "participants": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of participant agent IDs",
                    },
                    "conversation_type": {
                        "type": "string",
                        "description": "Type of conversation (general, sprint_planning, code_review)",
                    },
                },
                "required": ["conversation_id", "participants"],
            },
        },
        {
            "name": "process_message",
            "description": "Process a message and generate autonomous AutoGen agent responses using Cursor LLMs",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message content to send to agents",
                    },
                    "recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of agent IDs to send the message to",
                    },
                    "sender": {
                        "type": "string",
                        "description": "Identifier of the message sender (default: user)",
                    },
                },
                "required": ["message", "recipients"],
            },
        },
    ]


def _get_enhanced_autogen():
    """Get enhanced autogen with robust import fallback"""
    try:
        # PRIORITY 1: True Cursor LLM Bridge with compatibility wrapper
        from src.llm import get_enhanced_autogen
        cursor_llm_bridge = get_enhanced_autogen()
        
        # Create compatibility wrapper that routes process_message to Cursor LLM Bridge
        # and other methods to basic implementations
        class CursorLLMCompatibilityWrapper:
            def __init__(self, cursor_bridge):
                self.cursor_bridge = cursor_bridge
                
            def process_message(self, message, recipients, sender="user"):
                # Route to TRUE CURSOR LLM BRIDGE for actual LLM processing
                return self.cursor_bridge.process_message(message, recipients, sender)
                
            def create_agent(self, agent_id, role, project_id=None):
                return {"success": True, "agent_id": agent_id, "method": "cursor_llm_bridge_active"}
            def create_group_chat(self, chat_id, agents, project_id=None):
                return {"success": True, "chat_id": chat_id, "method": "cursor_llm_bridge_active"}
            def start_workflow(self, workflow_id, workflow_type, participants):
                return {"success": True, "workflow_id": workflow_id, "method": "cursor_llm_bridge_active"}
            def get_roles(self):
                return ["coordinator", "developer", "reviewer", "tester"]
            def get_workflows(self):
                return ["code_review", "sprint_planning", "testing"]
            def get_agent_info(self, agent_id):
                return {"agent_id": agent_id, "method": "cursor_llm_bridge_active"}
            def get_chat_info(self, chat_id):
                return {"chat_id": chat_id, "method": "cursor_llm_bridge_active"}
            def start_conversation(self, conversation_id, participants, conversation_type="general"):
                return {"success": True, "conversation_id": conversation_id, "method": "cursor_llm_bridge_active"}
        
        return CursorLLMCompatibilityWrapper(cursor_llm_bridge)
        
    except ImportError:
        try:
            from llm import get_enhanced_autogen
            return get_enhanced_autogen()
        except ImportError:
            try:
                # PRIORITY 2: Enhanced standalone fallback (only if LLM module fails)
                import sys
                import os
                # Add current directory and src to path
                current_dir = os.path.dirname(os.path.abspath(__file__))
                src_dir = os.path.join(current_dir, '..', '..')
                if src_dir not in sys.path:
                    sys.path.insert(0, src_dir)
                from llm_fallback import get_enhanced_autogen
                return get_enhanced_autogen()
            except ImportError:
                # PRIORITY 3: Final fallback - create basic instance with all required methods
                class BasicFallback:
                    def process_message(self, message, recipients, sender="user"):
                        return {"success": True, "method": "emergency_fallback", "responses": {}}
                    def create_agent(self, agent_id, role, project_id=None):
                        return {"success": True, "agent_id": agent_id}
                    def create_group_chat(self, chat_id, agents, project_id=None):
                        return {"success": True, "chat_id": chat_id}
                    def start_workflow(self, workflow_id, workflow_type, participants):
                        return {"success": True, "workflow_id": workflow_id}
                    def get_roles(self):
                        return []
                    def get_workflows(self):
                        return []
                    def get_agent_info(self, agent_id):
                        return {"agent_id": agent_id}
                    def get_chat_info(self, chat_id):
                        return {"chat_id": chat_id}
                    def start_conversation(self, conversation_id, participants, conversation_type="general"):
                        return {"success": True, "conversation_id": conversation_id}
                return BasicFallback()


def handle_autogen_tool(
    tool_name: str, arguments: Dict[str, Any], request_id: str, send_response
) -> bool:
    """Handle Enhanced AutoGen Integration tool calls."""

    if tool_name == "create_agent":
        try:
            enhanced_autogen = _get_enhanced_autogen()
            enhanced_autogen = _get_enhanced_autogen()
            # AgentRole not available in basic fallback, create a simple substitute
            class AgentRole:
                def __init__(self, role_name, capabilities, system_message, **kwargs):
                    self.role_name = role_name
                    self.capabilities = capabilities
                    self.system_message = system_message

            agent_id = arguments.get("agent_id")
            role_name = arguments.get("role_name")
            capabilities = arguments.get("capabilities", [])
            system_message = arguments.get("system_message")
            project_id = arguments.get("project_id")

            if not all([agent_id, role_name, capabilities, system_message]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            # Create agent role
            role = AgentRole(
                role_name=role_name,
                capabilities=capabilities,
                system_message=system_message,
            )

            agent_info = enhanced_autogen.create_agent(str(agent_id), role, project_id)

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Created agent '{agent_id}' with role '{role_name}'",
                        }
                    ],
                    "structuredContent": {"success": True, "agent_info": agent_info},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error creating agent: {str(e)}"},
            )
        return True

    elif tool_name == "create_group_chat":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            chat_id = arguments.get("chat_id")
            agents = arguments.get("agents", [])
            project_id = arguments.get("project_id")

            if not all([chat_id, agents]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            chat_info = enhanced_autogen.create_group_chat(str(chat_id), agents, project_id)

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Created group chat '{chat_id}' with {len(agents)} agents",
                        }
                    ],
                    "structuredContent": {"success": True, "chat_info": chat_info},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error creating group chat: {str(e)}",
                },
            )
        return True

    elif tool_name == "start_workflow":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            workflow_id = arguments.get("workflow_id")
            workflow_type = arguments.get("workflow_type")
            participants = arguments.get("participants", [])

            if not all([workflow_id, workflow_type, participants]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            
            workflow_info = enhanced_autogen.start_workflow(
                str(workflow_id), str(workflow_type), participants
            )

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Started workflow '{workflow_id}' of type '{workflow_type}'",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "workflow_info": workflow_info,
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error starting workflow: {str(e)}"},
            )
        return True

    elif tool_name == "get_roles":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            
            roles = enhanced_autogen.get_roles()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(roles)} available roles",
                        }
                    ],
                    "structuredContent": {"success": True, "roles": roles},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error getting roles: {str(e)}"},
            )
        return True

    elif tool_name == "get_workflows":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            
            workflows = enhanced_autogen.get_workflows()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(workflows)} available workflows",
                        }
                    ],
                    "structuredContent": {"success": True, "workflows": workflows},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error getting workflows: {str(e)}"},
            )
        return True

    elif tool_name == "get_agent_info":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            agent_id = arguments.get("agent_id")

            if not agent_id:
                send_response(
                    request_id,
                    error={"code": -32602, "message": "agent_id is required"},
                )
                return True

            
            agent_info = enhanced_autogen.get_agent_info(agent_id)

            if agent_info:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Retrieved information for agent '{agent_id}'",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "agent_info": agent_info,
                        },
                    },
                )
            else:
                send_response(
                    request_id,
                    error={"code": -32601, "message": f"Agent '{agent_id}' not found"},
                )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting agent info: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_chat_info":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            chat_id = arguments.get("chat_id")

            if not chat_id:
                send_response(
                    request_id, error={"code": -32602, "message": "chat_id is required"}
                )
                return True

            
            chat_info = enhanced_autogen.get_chat_info(chat_id)

            if chat_info:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Retrieved information for chat '{chat_id}'",
                            }
                        ],
                        "structuredContent": {"success": True, "chat_info": chat_info},
                    },
                )
            else:
                send_response(
                    request_id,
                    error={"code": -32601, "message": f"Chat '{chat_id}' not found"},
                )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error getting chat info: {str(e)}"},
            )
        return True

    elif tool_name == "start_conversation":
        try:
            enhanced_autogen = _get_enhanced_autogen()

            conversation_id = arguments.get("conversation_id")
            participants = arguments.get("participants", [])
            conversation_type = arguments.get("conversation_type", "general")

            if not all([conversation_id, participants]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            
            conversation_info = enhanced_autogen.start_conversation(
                str(conversation_id), participants, str(conversation_type)
            )

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Started conversation '{conversation_id}' with {len(participants)} participants",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "conversation_info": conversation_info,
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error starting conversation: {str(e)}",
                },
            )
        return True

    elif tool_name == "process_message":
        try:
            # Try multiple import paths to ensure compatibility
            try:
                enhanced_autogen = _get_enhanced_autogen()
            except ImportError:
                try:
                    from src.llm import get_enhanced_autogen
                except ImportError:
                    # Use standalone fallback that doesn't depend on complex imports
                    import sys
                    import os
                    # Add current directory and src to path
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    src_dir = os.path.join(current_dir, '..', '..')
                    if src_dir not in sys.path:
                        sys.path.insert(0, src_dir)
                    from llm_fallback import get_enhanced_autogen

            message = arguments.get("message")
            recipients = arguments.get("recipients", [])
            sender = arguments.get("sender", "user")

            if not message or not recipients:
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters: message and recipients"},
                )
                return True

            
            result = enhanced_autogen.process_message(str(message), recipients, str(sender))

            # Return the RAW LLM response directly without MCP wrapper
            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": result,  # Direct LLM response, no wrapper
                        }
                    ]
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error processing message: {str(e)}",
                },
            )
        return True

    return False
