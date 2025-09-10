"""Consolidated MCP tools manager for protocol_server.py integration."""

from typing import Dict, Any, List
from .handlers import (
    basic_tools,
    system_tools,
    database_tools,
    autogen_tools,
    communication_tools,
    knowledge_tools,
)


def get_all_mcp_tools() -> List[Dict[str, Any]]:
    """Get all MCP tools definitions."""
    all_tools = []

    # Add basic tools
    all_tools.extend(basic_tools.get_basic_tools())

    # Add system tools (coordinator, project management, agile, etc.)
    all_tools.extend(system_tools.get_system_tools())

    # Add database management tools
    all_tools.extend(database_tools.get_database_tools())

    # Add enhanced AutoGen integration tools
    all_tools.extend(autogen_tools.get_autogen_tools())

    # Add advanced communication features tools
    all_tools.extend(communication_tools.get_communication_tools())

    # Add predetermined knowledge bases tools
    all_tools.extend(knowledge_tools.get_knowledge_tools())

    return all_tools


def handle_mcp_tool(
    tool_name: str, arguments: Dict[str, Any], request_id: str, send_response
) -> bool:
    """Handle MCP tool calls by delegating to appropriate handlers."""

    # Try basic tools first
    if basic_tools.handle_basic_tool(tool_name, arguments, request_id, send_response):
        return True

    # Try system tools (coordinator, project management, agile, etc.)
    if system_tools.handle_system_tool(tool_name, arguments, request_id, send_response):
        return True

    # Try database management tools
    if database_tools.handle_database_tool(
        tool_name, arguments, request_id, send_response
    ):
        return True

    # Try enhanced AutoGen integration tools
    if autogen_tools.handle_autogen_tool(
        tool_name, arguments, request_id, send_response
    ):
        return True

    # Try advanced communication features tools
    if communication_tools.handle_communication_tool(
        tool_name, arguments, request_id, send_response
    ):
        return True

    # Try predetermined knowledge bases tools
    if knowledge_tools.handle_knowledge_tool(
        tool_name, arguments, request_id, send_response
    ):
        return True

    # Tool not found
    return False
