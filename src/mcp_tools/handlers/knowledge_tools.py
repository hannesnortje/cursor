"""Predetermined Knowledge Bases MCP tools for project initialization."""

from typing import Dict, Any, List


def get_knowledge_tools() -> List[Dict[str, Any]]:
    """Get Predetermined Knowledge Bases MCP tools definitions."""
    return [
        {
            "name": "get_domains",
            "description": "Get available knowledge domains with fallback data",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_domain_knowledge",
            "description": "Get knowledge items for a specific domain with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Knowledge domain (pdca, agile, code_quality, security, testing, documentation)",
                    }
                },
                "required": ["domain"],
            },
        },
        {
            "name": "get_all",
            "description": "Get all knowledge items with pagination",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of items to return",
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of items to skip",
                    },
                },
                "required": [],
            },
        },
        {
            "name": "search",
            "description": "Search knowledge items by content with fallback",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "domain": {
                        "type": "string",
                        "description": "Optional domain to search within",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "get_statistics",
            "description": "Get knowledge base statistics with caching",
            "inputSchema": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "initialize_project",
            "description": "Initialize project with predetermined knowledge with validation",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project identifier",
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of knowledge domains to initialize",
                    },
                },
                "required": ["project_id"],
            },
        },
        {
            "name": "get_by_category",
            "description": "Get knowledge items by category with error handling",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Knowledge category (methodology, code_quality, security, testing, documentation)",
                    }
                },
                "required": ["category"],
            },
        },
        {
            "name": "get_by_priority",
            "description": "Get knowledge items by priority with fallback",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "priority": {
                        "type": "string",
                        "description": "Priority level (high, medium, low)",
                    }
                },
                "required": ["priority"],
            },
        },
    ]


def handle_knowledge_tool(
    tool_name: str, arguments: Dict[str, Any], request_id: str, send_response
) -> bool:
    """Handle Predetermined Knowledge Bases tool calls."""

    if tool_name == "get_domains":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            knowledge_base = get_predetermined_knowledge()
            domains = knowledge_base.get_available_domains()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(domains)} knowledge domains",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "domains": domains,
                        "total_domains": len(domains),
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={"code": -32603, "message": f"Error getting domains: {str(e)}"},
            )
        return True

    elif tool_name == "get_domain_knowledge":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            domain = arguments.get("domain")

            if not domain:
                send_response(
                    request_id, error={"code": -32602, "message": "domain is required"}
                )
                return True

            knowledge_base = get_predetermined_knowledge()
            knowledge_items = knowledge_base.get_knowledge_for_domain(domain)

            # Convert to dictionaries
            items_dict = [item.to_dict() for item in knowledge_items]

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(knowledge_items)} knowledge items for domain '{domain}'",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "domain": domain,
                        "knowledge_items": items_dict,
                        "total_items": len(knowledge_items),
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting domain knowledge: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_all":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            limit = arguments.get("limit", 100)
            offset = arguments.get("offset", 0)

            knowledge_base = get_predetermined_knowledge()
            all_knowledge = knowledge_base.get_all_knowledge()

            # Flatten all knowledge items
            all_items = []
            for domain, items in all_knowledge.items():
                for item in items:
                    item_dict = item.to_dict()
                    item_dict["domain"] = domain
                    all_items.append(item_dict)

            # Apply pagination
            total_items = len(all_items)
            paginated_items = all_items[offset : offset + limit]

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(paginated_items)} of {total_items} total knowledge items",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "knowledge_items": paginated_items,
                        "total_items": total_items,
                        "limit": limit,
                        "offset": offset,
                        "has_more": offset + limit < total_items,
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting all knowledge: {str(e)}",
                },
            )
        return True

    elif tool_name == "search":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            query = arguments.get("query")
            domain = arguments.get("domain")

            if not query:
                send_response(
                    request_id, error={"code": -32602, "message": "query is required"}
                )
                return True

            knowledge_base = get_predetermined_knowledge()
            search_results = knowledge_base.search_knowledge(query, domain)

            # Convert to dictionaries
            results_dict = [item.to_dict() for item in search_results]

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Found {len(search_results)} knowledge items matching '{query}'",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "query": query,
                        "domain": domain,
                        "results": results_dict,
                        "total_results": len(search_results),
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error searching knowledge: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_statistics":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            knowledge_base = get_predetermined_knowledge()
            stats = knowledge_base.get_statistics()

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Knowledge base statistics: {stats.get('total_items', 0)} items across {stats.get('total_domains', 0)} domains",
                        }
                    ],
                    "structuredContent": {"success": True, "statistics": stats},
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting statistics: {str(e)}",
                },
            )
        return True

    elif tool_name == "initialize_project":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            project_id = arguments.get("project_id")
            domains = arguments.get("domains")

            if not project_id:
                send_response(
                    request_id,
                    error={"code": -32602, "message": "project_id is required"},
                )
                return True

            knowledge_base = get_predetermined_knowledge()
            result = knowledge_base.initialize_project(project_id, domains)

            if result["success"]:
                send_response(
                    request_id,
                    {
                        "content": [
                            {
                                "type": "text",
                                "text": f"Initialized project '{project_id}' with {result['total_items']} knowledge items",
                            }
                        ],
                        "structuredContent": {
                            "success": True,
                            "project_id": result["project_id"],
                            "domains_initialized": result["domains_initialized"],
                            "total_items": result["total_items"],
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
                    "message": f"Error initializing project: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_by_category":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            category = arguments.get("category")

            if not category:
                send_response(
                    request_id,
                    error={"code": -32602, "message": "category is required"},
                )
                return True

            knowledge_base = get_predetermined_knowledge()
            category_items = knowledge_base.get_by_category(category)

            # Convert to dictionaries
            items_dict = [item.to_dict() for item in category_items]

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(category_items)} knowledge items for category '{category}'",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "category": category,
                        "knowledge_items": items_dict,
                        "total_items": len(category_items),
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting by category: {str(e)}",
                },
            )
        return True

    elif tool_name == "get_by_priority":
        try:
            from src.knowledge.predetermined_knowledge import (
                get_predetermined_knowledge,
            )

            priority = arguments.get("priority")

            if not priority:
                send_response(
                    request_id,
                    error={"code": -32602, "message": "priority is required"},
                )
                return True

            knowledge_base = get_predetermined_knowledge()
            priority_items = knowledge_base.get_by_priority(priority)

            # Convert to dictionaries
            items_dict = [item.to_dict() for item in priority_items]

            send_response(
                request_id,
                {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Retrieved {len(priority_items)} knowledge items with priority '{priority}'",
                        }
                    ],
                    "structuredContent": {
                        "success": True,
                        "priority": priority,
                        "knowledge_items": items_dict,
                        "total_items": len(priority_items),
                    },
                },
            )
        except Exception as e:
            send_response(
                request_id,
                error={
                    "code": -32603,
                    "message": f"Error getting by priority: {str(e)}",
                },
            )
        return True

    return False
