"""LLM integration MCP tools."""

from typing import Dict, Any, List


def get_llm_tools() -> List[Dict[str, Any]]:
    """Get LLM MCP tools definitions."""
    # TODO: Extract LLM tools from protocol_server.py
    return []


def handle_llm_tool(tool_name: str, arguments: Dict[str, Any], request_id: str, send_response) -> bool:
    """Handle LLM tool calls."""
    # TODO: Extract LLM tool handlers from protocol_server.py
    return False
