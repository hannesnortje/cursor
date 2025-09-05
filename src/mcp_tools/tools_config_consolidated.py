#!/usr/bin/env python3
"""Consolidated MCP Tools Configuration - Optimized tool definitions for the MCP server."""

def get_tools_config():
    """Get the consolidated tools configuration for the MCP server."""
    return {
        "tools": [
            # Basic Tools
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
            
            # Core Agent System Tools
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

            # Consolidated System Status Tool
            {
                "name": "get_system_status",
                "description": "Get comprehensive system status including communication, dashboard, browser, registry, and instance information",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status_type": {"type": "string", "description": "Type of status to get (communication, dashboard, browser, registry, instance, all)"}
                    },
                    "required": []
                }
            },

            # Communication System Tools
            {
                "name": "manage_communication",
                "description": "Manage communication system (start, stop, get status, create sessions, broadcast messages)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (start, stop, status, create_session, broadcast, get_messages, search_messages)"},
                        "chat_id": {"type": "string", "description": "Chat ID for session operations"},
                        "chat_type": {"type": "string", "description": "Chat type for session creation"},
                        "participants": {"type": "array", "items": {"type": "string"}, "description": "Participants for session creation"},
                        "source_chat": {"type": "string", "description": "Source chat for broadcasting"},
                        "source_agent": {"type": "string", "description": "Source agent for broadcasting"},
                        "content": {"type": "string", "description": "Message content"},
                        "target_chats": {"type": "array", "items": {"type": "string"}, "description": "Target chats for broadcasting"},
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Limit for message retrieval"}
                    },
                    "required": ["action"]
                }
            },

            # Agile Agent Tools
            {
                "name": "manage_agile_project",
                "description": "Manage agile projects (create, create user stories, create sprints, plan sprints, complete stories, get status, get burndown, calculate velocity)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (create_project, create_story, create_sprint, plan_sprint, complete_story, get_status, get_burndown, calculate_velocity)"},
                        "project_name": {"type": "string", "description": "Project name for creation"},
                        "project_type": {"type": "string", "description": "Project type (scrum, kanban)"},
                        "sprint_length": {"type": "integer", "description": "Sprint length in days"},
                        "team_size": {"type": "integer", "description": "Team size"},
                        "project_id": {"type": "string", "description": "Project ID for operations"},
                        "title": {"type": "string", "description": "User story title"},
                        "description": {"type": "string", "description": "User story description"},
                        "acceptance_criteria": {"type": "array", "items": {"type": "string"}, "description": "Acceptance criteria"},
                        "story_points": {"type": "integer", "description": "Story points"},
                        "priority": {"type": "string", "description": "Priority level"},
                        "epic": {"type": "string", "description": "Epic name"},
                        "sprint_name": {"type": "string", "description": "Sprint name"},
                        "start_date": {"type": "string", "description": "Sprint start date"},
                        "end_date": {"type": "string", "description": "Sprint end date"},
                        "goal": {"type": "string", "description": "Sprint goal"},
                        "sprint_id": {"type": "string", "description": "Sprint ID for operations"},
                        "story_ids": {"type": "array", "items": {"type": "string"}, "description": "Story IDs for sprint planning"},
                        "story_id": {"type": "string", "description": "Story ID for completion"},
                        "actual_hours": {"type": "number", "description": "Actual hours worked"},
                        "sprint_count": {"type": "integer", "description": "Number of sprints for velocity calculation"}
                    },
                    "required": ["action"]
                }
            },

            # Project Generation Tools
            {
                "name": "manage_project_generation",
                "description": "Manage project generation (list templates, generate projects, customize templates, get status, list projects, create custom projects)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (list_templates, generate, customize, get_status, list_projects, create_custom)"},
                        "language": {"type": "string", "description": "Programming language filter"},
                        "category": {"type": "string", "description": "Project category filter"},
                        "template_id": {"type": "string", "description": "Template ID for generation/customization"},
                        "project_name": {"type": "string", "description": "Project name"},
                        "target_path": {"type": "string", "description": "Target path for project creation"},
                        "customizations": {"type": "object", "description": "Customizations for template"},
                        "project_id": {"type": "string", "description": "Project ID for status checking"},
                        "custom_structure": {"type": "object", "description": "Custom project structure"}
                    },
                    "required": ["action"]
                }
            },

            # Backend Agent Tools
            {
                "name": "manage_backend_development",
                "description": "Manage backend development (design APIs, create database schemas, implement security, design architecture, generate code, get specifications, get technologies)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (design_api, create_database, implement_security, design_architecture, generate_code, get_specifications, get_technologies)"},
                        "api_type": {"type": "string", "description": "API type (rest, graphql, grpc)"},
                        "name": {"type": "string", "description": "Name of the resource"},
                        "description": {"type": "string", "description": "Description of the resource"},
                        "endpoints": {"type": "array", "items": {"type": "object"}, "description": "API endpoints"},
                        "data_models": {"type": "array", "items": {"type": "object"}, "description": "Data models"},
                        "authentication": {"type": "object", "description": "Authentication configuration"},
                        "database_type": {"type": "string", "description": "Database type"},
                        "entities": {"type": "array", "items": {"type": "object"}, "description": "Database entities"},
                        "relationships": {"type": "array", "items": {"type": "object"}, "description": "Entity relationships"},
                        "constraints": {"type": "array", "items": {"type": "object"}, "description": "Database constraints"},
                        "indexes": {"type": "array", "items": {"type": "object"}, "description": "Database indexes"},
                        "security_type": {"type": "string", "description": "Security type"},
                        "method": {"type": "string", "description": "Security method"},
                        "configuration": {"type": "object", "description": "Security configuration"},
                        "architecture_type": {"type": "string", "description": "Architecture type"},
                        "components": {"type": "array", "items": {"type": "object"}, "description": "System components"},
                        "deployment": {"type": "string", "description": "Deployment type"},
                        "scaling": {"type": "object", "description": "Scaling configuration"},
                        "language": {"type": "string", "description": "Programming language"},
                        "framework": {"type": "string", "description": "Framework"},
                        "specification_id": {"type": "string", "description": "Specification ID"},
                        "type": {"type": "string", "description": "Specification type"},
                        "category": {"type": "string", "description": "Technology category"}
                    },
                    "required": ["action"]
                }
            },

            # LLM Integration Tools
            {
                "name": "manage_llm_models",
                "description": "Manage LLM models (get models, select best model, generate text, get performance stats, test integration, orchestrate models)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (get_models, select_best, generate, get_stats, test, orchestrate)"},
                        "provider": {"type": "string", "description": "LLM provider filter"},
                        "task_type": {"type": "string", "description": "Task type for model selection"},
                        "context": {"type": "string", "description": "Context for model selection"},
                        "prompt": {"type": "string", "description": "Text prompt for generation"},
                        "preferred_model": {"type": "string", "description": "Preferred model name"},
                        "temperature": {"type": "number", "description": "Generation temperature"},
                        "max_tokens": {"type": "integer", "description": "Maximum tokens to generate"},
                        "test_type": {"type": "string", "description": "Type of test to run"},
                        "task_description": {"type": "string", "description": "Task description for orchestration"},
                        "required_capabilities": {"type": "array", "items": {"type": "string"}, "description": "Required model capabilities"},
                        "coordination_strategy": {"type": "string", "description": "Coordination strategy"}
                    },
                    "required": ["action"]
                }
            },

            # Project Database Management Tools
            {
                "name": "manage_project_databases",
                "description": "Manage project-specific Qdrant databases (start/stop container, create/list/switch/archive/restore/delete databases, get stats, initialize knowledge, search knowledge, backup/restore data)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (start_container, stop_container, get_status, create_database, list_databases, switch_database, archive_database, restore_database, delete_database, get_stats, initialize_knowledge, search_knowledge, backup_data, restore_data)"},
                        "project_name": {"type": "string", "description": "Project name for database creation"},
                        "project_id": {"type": "string", "description": "Project ID for operations"},
                        "permanent": {"type": "boolean", "description": "Whether to permanently delete"},
                        "query": {"type": "string", "description": "Search query"},
                        "knowledge_type": {"type": "string", "description": "Knowledge type for search"},
                        "limit": {"type": "integer", "description": "Search result limit"},
                        "backup_path": {"type": "string", "description": "Backup file path"}
                    },
                    "required": ["action"]
                }
            },

            # AutoGen Integration Tools
            {
                "name": "manage_autogen_agents",
                "description": "Manage AutoGen agents and workflows (create agents, create group chats, start workflows, get roles/workflows, get agent/chat info, list agents/chats, start conversations)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (create_agent, create_group_chat, start_workflow, get_roles, get_workflows, get_agent_info, get_chat_info, list_agents, list_chats, start_conversation)"},
                        "agent_id": {"type": "string", "description": "Agent ID for operations"},
                        "role_name": {"type": "string", "description": "Agent role name"},
                        "project_id": {"type": "string", "description": "Project ID for context"},
                        "chat_id": {"type": "string", "description": "Group chat ID"},
                        "agent_ids": {"type": "array", "items": {"type": "string"}, "description": "List of agent IDs"},
                        "workflow_name": {"type": "string", "description": "Workflow name"},
                        "initial_message": {"type": "string", "description": "Initial conversation message"},
                        "message": {"type": "string", "description": "Conversation message"},
                        "conversation_type": {"type": "string", "description": "Conversation type"}
                    },
                    "required": ["action"]
                }
            },

            # Advanced Communication Tools
            {
                "name": "manage_advanced_communication",
                "description": "Manage advanced communication features (start/stop system, send messages, get analytics, get queue status, enable/disable cross-project communication, share knowledge, get compression stats, get message types, get health)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (start, stop, send_message, get_analytics, get_queue_status, enable_cross_project, disable_cross_project, share_knowledge, get_compression_stats, get_message_types, get_health)"},
                        "sender": {"type": "string", "description": "Message sender"},
                        "recipient": {"type": "string", "description": "Message recipient"},
                        "message_type": {"type": "string", "description": "Message type"},
                        "content": {"type": "string", "description": "Message content"},
                        "priority": {"type": "string", "description": "Message priority"},
                        "session_id": {"type": "string", "description": "Session ID"},
                        "compression": {"type": "string", "description": "Compression type"},
                        "project1": {"type": "string", "description": "First project ID"},
                        "project2": {"type": "string", "description": "Second project ID"},
                        "source_project": {"type": "string", "description": "Source project ID"},
                        "target_project": {"type": "string", "description": "Target project ID"},
                        "knowledge": {"type": "object", "description": "Knowledge data to share"}
                    },
                    "required": ["action"]
                }
            },

            # Knowledge Management Tools
            {
                "name": "manage_knowledge_bases",
                "description": "Manage predetermined knowledge bases (get domains, get domain knowledge, get all knowledge, search knowledge, get statistics, initialize project knowledge, get by category/priority)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action to perform (get_domains, get_domain_knowledge, get_all, search, get_statistics, initialize_project, get_by_category, get_by_priority)"},
                        "domain": {"type": "string", "description": "Knowledge domain"},
                        "query": {"type": "string", "description": "Search query"},
                        "category": {"type": "string", "description": "Knowledge category"},
                        "priority": {"type": "string", "description": "Knowledge priority"},
                        "project_id": {"type": "string", "description": "Project ID for initialization"},
                        "domains": {"type": "array", "items": {"type": "string"}, "description": "List of domains to initialize"}
                    },
                    "required": ["action"]
                }
            }
        ]
    }
