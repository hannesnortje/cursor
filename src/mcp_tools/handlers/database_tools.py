"""Database Management MCP tools for project-specific Qdrant databases."""

from typing import Dict, Any, List


def get_database_tools() -> List[Dict[str, Any]]:
    """Get Database Management MCP tools definitions."""
    return [
        {
            "name": "start_container",
            "description": "Start Qdrant Docker container with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "create_database",
            "description": "Create a new project-specific database with validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_name": {"type": "string", "description": "Name of the project"},
                    "project_id": {"type": "string", "description": "Optional project ID (auto-generated if not provided)"}
                },
                "required": ["project_name"]
            }
        },
        {
            "name": "list_databases",
            "description": "List all project databases with fallback",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "switch_database",
            "description": "Switch to a specific project database with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID to switch to"}
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "archive_database",
            "description": "Archive a project database with confirmation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID to archive"}
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "restore_database",
            "description": "Restore an archived project database with validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID to restore"}
                },
                "required": ["project_id"]
            }
        },
        {
            "name": "delete_database",
            "description": "Delete a project database with safety checks",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID to delete"},
                    "confirm": {"type": "boolean", "description": "Confirmation flag for deletion"}
                },
                "required": ["project_id", "confirm"]
            }
        },
        {
            "name": "get_stats",
            "description": "Get database statistics with fallback data",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Optional project ID for specific stats"}
                },
                "required": []
            }
        }
    ]


def handle_database_tool(tool_name: str, arguments: Dict[str, Any], request_id: str, send_response) -> bool:
    """Handle Database Management tool calls."""
    
    if tool_name == "start_container":
        try:
            from src.database.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            success = docker_manager.start_qdrant_container()
            
            if success:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Qdrant container started successfully"}],
                    "structuredContent": {"success": True, "message": "Container started"}
                })
            else:
                send_response(request_id, {
                    "content": [{"type": "text", "text": "Failed to start Qdrant container"}],
                    "structuredContent": {"success": False, "message": "Container start failed"}
                })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error starting container: {str(e)}"})
        return True
    
    elif tool_name == "create_database":
        try:
            from src.database.project_manager import get_project_manager
            project_name = arguments.get("project_name")
            project_id = arguments.get("project_id")
            
            if not project_name:
                send_response(request_id, error={"code": -32602, "message": "project_name is required"})
                return True
            
            project_manager = get_project_manager()
            project = project_manager.create_project_database(project_name, project_id)
            
            send_response(request_id, {
                "content": [{"type": "text", "text": f"Created project database '{project_name}' with ID: {project.project_id}"}],
                "structuredContent": {
                    "success": True,
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "database_name": project.database_name,
                    "collections": list(project.collections.keys())
                }
            })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error creating database: {str(e)}"})
        return True
    
    elif tool_name == "list_databases":
        try:
            from src.database.project_manager import get_project_manager
            project_manager = get_project_manager()
            projects = project_manager.list_project_databases()
            
            project_list = []
            for project in projects:
                project_list.append({
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "database_name": project.database_name,
                    "status": project.status,
                    "created_at": project.created_at.isoformat()
                })
            
            send_response(request_id, {
                "content": [{"type": "text", "text": f"Found {len(project_list)} project databases"}],
                "structuredContent": {
                    "success": True,
                    "projects": project_list,
                    "count": len(project_list)
                }
            })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error listing databases: {str(e)}"})
        return True
    
    elif tool_name == "switch_database":
        try:
            from src.database.enhanced_vector_store import get_enhanced_vector_store
            project_id = arguments.get("project_id")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            vector_store = get_enhanced_vector_store()
            success = vector_store.set_current_project(project_id)
            
            if success:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Switched to project database: {project_id}"}],
                    "structuredContent": {"success": True, "project_id": project_id}
                })
            else:
                send_response(request_id, error={"code": -32603, "message": f"Failed to switch to project: {project_id}"})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error switching database: {str(e)}"})
        return True
    
    elif tool_name == "archive_database":
        try:
            from src.database.project_manager import get_project_manager
            project_id = arguments.get("project_id")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            project_manager = get_project_manager()
            success = project_manager.archive_project_database(project_id)
            
            if success:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Archived project database: {project_id}"}],
                    "structuredContent": {"success": True, "project_id": project_id, "action": "archived"}
                })
            else:
                send_response(request_id, error={"code": -32603, "message": f"Failed to archive project: {project_id}"})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error archiving database: {str(e)}"})
        return True
    
    elif tool_name == "restore_database":
        try:
            from src.database.project_manager import get_project_manager
            project_id = arguments.get("project_id")
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            project_manager = get_project_manager()
            # Note: restore functionality would need to be implemented in project_manager
            send_response(request_id, {
                "content": [{"type": "text", "text": f"Restore functionality for project {project_id} - not yet implemented"}],
                "structuredContent": {"success": False, "message": "Restore not implemented", "project_id": project_id}
            })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error restoring database: {str(e)}"})
        return True
    
    elif tool_name == "delete_database":
        try:
            from src.database.project_manager import get_project_manager
            project_id = arguments.get("project_id")
            confirm = arguments.get("confirm", False)
            
            if not project_id:
                send_response(request_id, error={"code": -32602, "message": "project_id is required"})
                return True
            
            if not confirm:
                send_response(request_id, error={"code": -32602, "message": "confirmation required for deletion"})
                return True
            
            project_manager = get_project_manager()
            success = project_manager.delete_project_database(project_id)
            
            if success:
                send_response(request_id, {
                    "content": [{"type": "text", "text": f"Deleted project database: {project_id}"}],
                    "structuredContent": {"success": True, "project_id": project_id, "action": "deleted"}
                })
            else:
                send_response(request_id, error={"code": -32603, "message": f"Failed to delete project: {project_id}"})
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error deleting database: {str(e)}"})
        return True
    
    elif tool_name == "get_stats":
        try:
            from src.database.project_manager import get_project_manager
            from src.database.enhanced_vector_store import get_enhanced_vector_store
            project_id = arguments.get("project_id")
            
            project_manager = get_project_manager()
            vector_store = get_enhanced_vector_store()
            
            # Get general database stats
            db_stats = project_manager.get_database_stats()
            
            # Get project-specific stats if project_id provided
            project_stats = None
            if project_id:
                project_stats = vector_store.get_project_stats(project_id)
            
            send_response(request_id, {
                "content": [{"type": "text", "text": f"Database statistics retrieved successfully"}],
                "structuredContent": {
                    "success": True,
                    "database_stats": db_stats,
                    "project_stats": project_stats
                }
            })
        except Exception as e:
            send_response(request_id, error={"code": -32603, "message": f"Error getting stats: {str(e)}"})
        return True
    
    return False
