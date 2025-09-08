"""System MCP tools (coordinator, project management, communication, etc.)."""

from typing import Dict, Any, List


def get_system_tools() -> List[Dict[str, Any]]:
    """Get system MCP tools definitions."""
    return [
        # Core System Tools
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
        
        # Communication System Tools
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
        },
        {
            "name": "get_cross_chat_messages",
            "description": "Get cross-chat messages for a specific chat or all chats",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "chat_id": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": []
            }
        },
        {
            "name": "search_cross_chat_messages",
            "description": "Search cross-chat messages by content",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "chat_id": {"type": "string"},
                    "limit": {"type": "integer"}
                },
                "required": ["query"]
            }
        },
        
        # Agile/Scrum Tools
        {
            "name": "create_agile_project",
            "description": "Create a new agile project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string"},
                    "project_type": {"type": "string", "default": "scrum"},
                    "sprint_length": {"type": "integer"},
                    "team_size": {"type": "integer", "default": 5}
                },
                "required": ["project_name"]
            }
        },
        {
            "name": "create_user_story",
            "description": "Create a new user story in an agile project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                    "story_points": {"type": "integer"},
                    "priority": {"type": "string", "default": "medium"},
                    "epic": {"type": "string"}
                },
                "required": ["project_id", "title", "description", "acceptance_criteria"]
            }
        },
        {
            "name": "create_sprint",
            "description": "Create a new sprint in an agile project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "sprint_name": {"type": "string"},
                    "start_date": {"type": "string"},
                    "end_date": {"type": "string"},
                    "goal": {"type": "string"}
                },
                "required": ["project_id", "sprint_name"]
            }
        },
        {
            "name": "plan_sprint",
            "description": "Plan a sprint by assigning user stories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "string"},
                    "story_ids": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["sprint_id", "story_ids"]
            }
        },
        {
            "name": "complete_user_story",
            "description": "Mark a user story as completed",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "story_id": {"type": "string"},
                    "actual_hours": {"type": "number"}
                },
                "required": ["story_id"]
            }
        },
        {
            "name": "get_project_status",
            "description": "Get comprehensive project status and metrics for an agile project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"}
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "get_sprint_burndown",
            "description": "Generate burndown chart data for a sprint",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sprint_id": {"type": "string"}
                },
                "required": ["sprint_id"]
            }
        },
        {
            "name": "calculate_team_velocity",
            "description": "Calculate team velocity based on completed sprints",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string"},
                    "sprint_count": {"type": "integer"}
                },
                "required": ["project_id"]
            }
        },
        
        # Project Generation Tools
        {
            "name": "list_project_templates",
            "description": "List available project templates with optional filtering by language and category",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "language": {"type": "string", "description": "Filter by programming language (python, cpp, java, go, rust, typescript, etc.)"},
                    "category": {"type": "string", "description": "Filter by project category (web, api, library, cli, data-science, etc.)"}
                },
                "required": []
            }
        },
        {
            "name": "generate_project",
            "description": "Generate a new project from a template",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "ID of the template to use"},
                    "project_name": {"type": "string", "description": "Name of the project to create"},
                    "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"},
                    "customizations": {"type": "object", "description": "Optional customizations for the project"}
                },
                "required": ["template_id", "project_name"]
            }
        },
        {
            "name": "customize_project_template",
            "description": "Customize an existing project template",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "ID of the template to customize"},
                    "customizations": {"type": "object", "description": "Customizations to apply to the template"}
                },
                "required": ["template_id", "customizations"]
            }
        },
        {
            "name": "get_generated_project_status",
            "description": "Get status of a generated project",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "ID of the generated project"}
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "list_generated_projects",
            "description": "List all generated projects",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        
        # Security Tools
        {
            "name": "get_security_status",
            "description": "Get security middleware status and statistics",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        },
        {
            "name": "get_rate_limit_status",
            "description": "Get rate limiting status and statistics",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "client_id": {"type": "string", "description": "Client ID to check (optional)"}
                }
            }
        },
        {
            "name": "validate_security_headers",
            "description": "Validate security headers configuration",
            "inputSchema": {
                "type": "object",
                "properties": {}
            }
        }
    ]


def handle_system_tool(tool_name: str, arguments: Dict[str, Any], request_id: str, send_response) -> bool:
    """Handle system tool calls."""
    
    # Import agent system for tool handling
    try:
        import protocol_server
        agent_system = protocol_server.agent_system
    except Exception as e:
        send_response(request_id, error={"code": -32603, "message": f"Failed to access agent system: {str(e)}"})
        return True
    
    # Core System Tools
    if tool_name == "start_project":
        try:
            project_type = arguments.get("project_type")
            project_name = arguments.get("project_name")
            
            if not project_type or not project_name:
                send_response(request_id, error={"code": -32602, "message": "project_type and project_name are required"})
                return True
            
            result = agent_system.start_project(project_type, project_name)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": result["message"]}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error starting project: {str(e)}"})
        return True
    
    elif tool_name == "chat_with_coordinator":
        try:
            message = arguments.get("message")
            
            if not message:
                send_response(request_id, error={"code": -32602, "message": "message is required"})
                return True
            
            result = agent_system.chat_with_coordinator(message)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": result["response"]}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error chatting with coordinator: {str(e)}"})
        return True
    
    # Communication System Tools
    elif tool_name == "start_communication_system":
        try:
            result = agent_system.start_communication_system()
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": result["message"]}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error starting communication system: {str(e)}"})
        return True
    
    elif tool_name == "get_communication_status":
        try:
            result = agent_system.get_communication_status()
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Communication system status retrieved"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting communication status: {str(e)}"})
        return True
    
    elif tool_name == "create_cross_chat_session":
        try:
            chat_id = arguments.get("chat_id")
            chat_type = arguments.get("chat_type")
            participants = arguments.get("participants", [])
            
            if not chat_id or not chat_type:
                send_response(request_id, error={"code": -32602, "message": "chat_id and chat_type are required"})
                return True
            
            result = agent_system.create_cross_chat_session(chat_id, chat_type, participants)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": result["message"]}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error creating cross-chat session: {str(e)}"})
        return True
    
    elif tool_name == "broadcast_cross_chat_message":
        try:
            source_chat = arguments.get("source_chat")
            source_agent = arguments.get("source_agent")
            content = arguments.get("content")
            target_chats = arguments.get("target_chats", [])
            
            if not all([source_chat, source_agent, content]):
                send_response(request_id, error={"code": -32602, "message": "source_chat, source_agent, and content are required"})
                return True
            
            result = agent_system.broadcast_cross_chat_message(source_chat, source_agent, content, target_chats)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": result["message"]}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error broadcasting message: {str(e)}"})
        return True
    
    elif tool_name == "get_cross_chat_messages":
        try:
            chat_id = arguments.get("chat_id")
            limit = arguments.get("limit", 50)
            
            result = agent_system.get_cross_chat_messages(chat_id, limit)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Retrieved {result['message_count']} messages"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting cross-chat messages: {str(e)}"})
        return True
    
    elif tool_name == "search_cross_chat_messages":
        try:
            query = arguments.get("query")
            chat_id = arguments.get("chat_id")
            limit = arguments.get("limit", 50)
            
            if not query:
                send_response(request_id, error={"code": -32602, "message": "query is required"})
                return True
            
            result = agent_system.search_cross_chat_messages(query, chat_id, limit)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Found {result['results_count']} results"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error searching cross-chat messages: {str(e)}"})
        return True
    
    # Agile/Scrum Tools
    elif tool_name == "create_agile_project":
        try:
            project_name = arguments.get("project_name")
            project_type = arguments.get("project_type", "scrum")
            sprint_length = arguments.get("sprint_length")
            team_size = arguments.get("team_size", 5)
            
            if not project_name:
                send_response(request_id, error={"code": -32602, "message": "project_name is required"})
                return True
            
            result = agent_system.create_agile_project(project_name, project_type, sprint_length, team_size)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Agile project '{project_name}' created successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error creating agile project: {str(e)}"})
        return True
    
    elif tool_name == "create_user_story":
        try:
            project_id = arguments.get("project_id")
            title = arguments.get("title")
            description = arguments.get("description")
            acceptance_criteria = arguments.get("acceptance_criteria", [])
            story_points = arguments.get("story_points")
            priority = arguments.get("priority", "medium")
            epic = arguments.get("epic")
            
            if not all([project_id, title, description]):
                send_response(request_id, error={"code": -32602, "message": "project_id, title, and description are required"})
                return True
            
            result = agent_system.create_user_story(project_id, title, description, acceptance_criteria, story_points, priority, epic)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"User story '{title}' created successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error creating user story: {str(e)}"})
        return True
    
    elif tool_name == "create_sprint":
        try:
            project_id = arguments.get("project_id")
            sprint_name = arguments.get("sprint_name")
            start_date = arguments.get("start_date")
            end_date = arguments.get("end_date")
            goal = arguments.get("goal")
            
            if not all([project_id, sprint_name]):
                send_response(request_id, error={"code": -32602, "message": "project_id and sprint_name are required"})
                return True
            
            result = agent_system.create_sprint(project_id, sprint_name, start_date, end_date, goal)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Sprint '{sprint_name}' created successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error creating sprint: {str(e)}"})
        return True
    
    elif tool_name == "plan_sprint":
        try:
            sprint_id = arguments.get("sprint_id")
            story_ids = arguments.get("story_ids", [])
            
            if not all([sprint_id, story_ids]):
                send_response(request_id, error={"code": -32602, "message": "sprint_id and story_ids are required"})
                return True
            
            result = agent_system.plan_sprint(sprint_id, story_ids)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Sprint {sprint_id} planned with {len(story_ids)} stories"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error planning sprint: {str(e)}"})
        return True
    
    elif tool_name == "complete_user_story":
        try:
            story_id = arguments.get("story_id")
            actual_hours = arguments.get("actual_hours")
            
            if not story_id:
                send_response(request_id, error={"code": -32602, "message": "story_id is required"})
                return True
            
            result = agent_system.complete_user_story(story_id, actual_hours)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"User story {story_id} completed successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error completing user story: {str(e)}"})
        return True
    
    elif tool_name == "get_project_status":
        try:
            project_id = arguments.get("project_id")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            result = agent_system.get_project_status(project_id)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Project status for {project_id} retrieved"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting project status: {str(e)}"})
        return True
    
    elif tool_name == "get_sprint_burndown":
        try:
            sprint_id = arguments.get("sprint_id")
            
            if not sprint_id:
                send_response(request_id, error={"code": -32602, "message": "sprint_id is required"})
                return True
            
            result = agent_system.get_sprint_burndown(sprint_id)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Burndown data for sprint {sprint_id} generated"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting sprint burndown: {str(e)}"})
        return True
    
    elif tool_name == "calculate_team_velocity":
        try:
            project_id = arguments.get("project_id")
            sprint_count = arguments.get("sprint_count")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            result = agent_system.calculate_team_velocity(project_id, sprint_count)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Team velocity for project {project_id} calculated"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error calculating team velocity: {str(e)}"})
        return True
    
    # Project Generation Tools
    elif tool_name == "list_project_templates":
        try:
            language = arguments.get("language")
            category = arguments.get("category")
            
            result = agent_system.list_project_templates(language, category)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Retrieved {result.get('total_count', 0)} project templates"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error listing project templates: {str(e)}"})
        return True
    
    elif tool_name == "generate_project":
        try:
            template_id = arguments.get("template_id")
            project_name = arguments.get("project_name")
            target_path = arguments.get("target_path", ".")
            customizations = arguments.get("customizations", {})
            
            if not all([template_id, project_name]):
                send_response(request_id, error={"code": -32602, "message": "template_id and project_name are required"})
                return True
            
            result = agent_system.generate_project(template_id, project_name, target_path, customizations)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Project '{project_name}' generated successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error generating project: {str(e)}"})
        return True
    
    elif tool_name == "customize_project_template":
        try:
            template_id = arguments.get("template_id")
            customizations = arguments.get("customizations", {})
            
            if not all([template_id, customizations]):
                send_response(request_id, error={"code": -32602, "message": "template_id and customizations are required"})
                return True
            
            result = agent_system.customize_project_template(template_id, customizations)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Template '{template_id}' customized successfully"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error customizing template: {str(e)}"})
        return True
    
    elif tool_name == "get_generated_project_status":
        try:
            project_id = arguments.get("project_id")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            result = agent_system.get_generated_project_status(project_id)
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Project status for {project_id} retrieved"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting generated project status: {str(e)}"})
        return True
    
    elif tool_name == "list_generated_projects":
        try:
            result = agent_system.list_generated_projects()
            
            if result["success"]:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Retrieved {result.get('total_count', 0)} generated projects"}],
                    "structuredContent": result
                })
            else:
                send_response(request_id, error={"code": -32603, "message": result["error"]})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error listing generated projects: {str(e)}"})
        return True
    
    # Security Tools
    elif tool_name == "get_security_status":
        try:
            # Import security middleware
            try:
                from src.security.middleware import security_middleware
                from src.security.headers import SecurityHeaders
                
                # Get security statistics
                security_stats = security_middleware.get_security_statistics()
                
                # Get headers validation
                headers = SecurityHeaders()
                headers_validation = headers.validate_headers()
                
                result = {
                    "security_middleware": security_stats,
                    "headers_validation": headers_validation,
                    "security_available": True
                }
                
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Security status retrieved successfully"}],
                    "structuredContent": result
                })
            except ImportError:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Security middleware not available"}],
                    "structuredContent": {"security_available": False}
                })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting security status: {str(e)}"})
        return True
    
    elif tool_name == "get_rate_limit_status":
        try:
            # Import rate limiter
            try:
                from src.security.rate_limiting import rate_limiter
                
                client_id = arguments.get("client_id", "default")
                
                # Get rate limit statistics
                stats = rate_limiter.get_statistics()
                
                # Test rate limit for client
                test_result = rate_limiter.is_allowed(client_id, "general")
                
                result = {
                    "statistics": stats,
                    "client_test": {
                        "client_id": client_id,
                        "allowed": test_result["allowed"],
                        "remaining": test_result["remaining"],
                        "limit": test_result["limit"]
                    },
                    "rate_limiting_available": True
                }
                
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Rate limit status for client '{client_id}' retrieved"}],
                    "structuredContent": result
                })
            except ImportError:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Rate limiting not available"}],
                    "structuredContent": {"rate_limiting_available": False}
                })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting rate limit status: {str(e)}"})
        return True
    
    elif tool_name == "validate_security_headers":
        try:
            # Import security headers
            try:
                from src.security.headers import SecurityHeaders
                
                headers = SecurityHeaders()
                validation_result = headers.validate_headers()
                headers_list = headers.get_headers()
                
                result = {
                    "validation": validation_result,
                    "headers": headers_list,
                    "headers_count": len(headers_list),
                    "security_headers_available": True
                }
                
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Security headers validation completed - {len(headers_list)} headers configured"}],
                    "structuredContent": result
                })
            except ImportError:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Security headers not available"}],
                    "structuredContent": {"security_headers_available": False}
                })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error validating security headers: {str(e)}"})
        return True
    
    return False
