"""Advanced Communication Features MCP tools for message compression and routing."""

from typing import Dict, Any, List


def get_communication_tools() -> List[Dict[str, Any]]:
    """Get Advanced Communication Features MCP tools definitions."""
    return [
        {
            "name": "send_message",
            "description": "Send message with compression and priority routing",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "Message content to send",
                    },
                    "sender": {"type": "string", "description": "Sender identifier"},
                    "recipients": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of recipient identifiers",
                    },
                    "message_type": {
                        "type": "string",
                        "description": "Type of message (system, agent, user, monitoring, error, debug)",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Message priority (low, normal, high, urgent, critical)",
                    },
                    "compression": {
                        "type": "boolean",
                        "description": "Whether to compress the message",
                    },
                    "ttl": {
                        "type": "number",
                        "description": "Time to live in seconds (optional)",
                    },
                },
                "required": ["content", "sender", "recipients"],
            },
        },
        {
            "name": "get_analytics",
            "description": "Get communication analytics with fallback data",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_queue_status",
            "description": "Get message queue status with error handling",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "enable_cross_project",
            "description": "Enable cross-project communication with validation",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "disable_cross_project",
            "description": "Disable cross-project communication with confirmation",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "share_knowledge",
            "description": "Share knowledge between projects with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "knowledge": {
                        "type": "string",
                        "description": "Knowledge content to share",
                    },
                    "source_project": {
                        "type": "string",
                        "description": "Source project identifier",
                    },
                    "target_projects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of target project identifiers",
                    },
                },
                "required": ["knowledge", "source_project", "target_projects"],
            },
        },
        {
            "name": "get_compression_stats",
            "description": "Get compression statistics with fallback",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_message_types",
            "description": "Get available message types with caching",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
    ]


def handle_communication_tool(
    tool_name: str, arguments: Dict[str, Any], request_id: str, send_response
) -> bool:
    """Handle Advanced Communication Features tool calls."""

    if tool_name == "send_message":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            content = arguments.get("content")
            sender = arguments.get("sender")
            recipients = arguments.get("recipients", [])
            message_type = arguments.get("message_type", "agent")
            priority = arguments.get("priority", "normal")
            compression = arguments.get("compression", False)
            ttl = arguments.get("ttl")

            if not all([content, sender, recipients]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            advanced_comm = get_advanced_communication()
            result = advanced_comm.send_message(
                content=content,
                sender=sender,
                recipients=recipients,
                message_type=message_type,
                priority=priority,
                compression=compression,
                ttl=ttl,
            )

            if result["success"]:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Message sent successfully with ID: {result['message_id']}",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "message_id": result["message_id"],
                            "routing_result": result["routing_result"],
                            "compression_applied": result["compression_applied"],
                        },
                    },
                )
            else:
                send_response(
                    request_id, error={"code": -32603, "message": result["error"]}
                )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error sending message: {str(e)}"},
            )
        return True

    elif tool_name == "get_analytics":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            analytics = advanced_comm.get_analytics()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved communication analytics: {analytics.get('total_messages', 0)} messages analyzed",
                        }
                    ],
                    "structuredContent": {"success": True, "analytics": analytics},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error getting analytics: {str(e)}"},
            )
        return True

    elif tool_name == "get_queue_status":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            queue_status = advanced_comm.get_queue_status()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved queue status: {queue_status.get('total_messages', 0)} messages in queues",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "queue_status": queue_status,
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting queue status: {str(e)}",
                },
            )
        return True

    elif tool_name == "enable_cross_project":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            result = advanced_comm.enable_cross_project()

            if result["success"]:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": "Cross-project communication enabled successfully",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "cross_project_enabled": result["cross_project_enabled"],
                        },
                    },
                )
            else:
                send_response(
                    request_id, error={"code": -32603, "message": result["error"]}
                )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error enabling cross-project communication: {str(e)}",
                },
            )
        return True

    elif tool_name == "disable_cross_project":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            result = advanced_comm.disable_cross_project()

            if result["success"]:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": "Cross-project communication disabled successfully",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "cross_project_enabled": result["cross_project_enabled"],
                        },
                    },
                )
            else:
                send_response(
                    request_id, error={"code": -32603, "message": result["error"]}
                )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error disabling cross-project communication: {str(e)}",
                },
            )
        return True

    elif tool_name == "share_knowledge":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            knowledge = arguments.get("knowledge")
            source_project = arguments.get("source_project")
            target_projects = arguments.get("target_projects", [])

            if not all([knowledge, source_project, target_projects]):
                send_response(
                    request_id,
                    error={"code": -32602, "message": "Missing required parameters"},
                )
                return True

            advanced_comm = get_advanced_communication()
            result = advanced_comm.share_knowledge(
                knowledge, source_project, target_projects
            )

            if result["success"]:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Knowledge shared from {source_project} to {len(target_projects)} projects",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "knowledge_shared": result["knowledge_shared"],
                            "source_project": result["source_project"],
                            "target_projects": result["target_projects"],
                        },
                    },
                )
            else:
                send_response(
                    request_id, error={"code": -32603, "message": result["error"]}
                )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error sharing knowledge: {str(e)}"},
            )
        return True

    elif tool_name == "get_compression_stats":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            stats = advanced_comm.get_compression_stats()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved compression stats: {stats.get('total_compressed', 0)} messages compressed",
                        }
                    ],
                    "structuredContent": {"success": True, "compression_stats": stats},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting compression stats: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_message_types":
        try:
            from src.communication.advanced_communication import (
                get_advanced_communication,
            )

            advanced_comm = get_advanced_communication()
            message_types = advanced_comm.get_message_types()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(message_types)} message types",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "message_types": message_types,
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting message types: {str(e)}",
                },
            )
        return True

    return False
