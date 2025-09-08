"""Consolidated MCP tools manager for protocol_server.py integration."""

from typing import Dict, Any, List
from .handlers import (
    basic_tools,
    communication_tools,
    agile_tools,
    project_generation_tools,
    backend_tools,
    llm_tools,
    dashboard_tools,
    phase9_1_tools,
    phase9_2_tools,
    phase9_3_tools
)


def get_all_mcp_tools() -> List[Dict[str, Any]]:
    """Get all MCP tools definitions."""
    all_tools = []
    
    # Add basic tools
    all_tools.extend(basic_tools.get_basic_tools())
    
    # Add communication tools
    all_tools.extend(communication_tools.get_communication_tools())
    
    # Add agile tools
    all_tools.extend(agile_tools.get_agile_tools())
    
    # Add project generation tools
    all_tools.extend(project_generation_tools.get_project_generation_tools())
    
    # Add backend tools
    all_tools.extend(backend_tools.get_backend_tools())
    
    # Add LLM tools
    all_tools.extend(llm_tools.get_llm_tools())
    
    # Add dashboard tools
    all_tools.extend(dashboard_tools.get_dashboard_tools())
    
    # Add Phase 9.1 tools
    all_tools.extend(phase9_1_tools.get_phase9_1_tools())
    
    # Add Phase 9.2 tools
    all_tools.extend(phase9_2_tools.get_phase9_2_tools())
    
    # Add Phase 9.3 tools
    all_tools.extend(phase9_3_tools.get_phase9_3_tools())
    
    return all_tools


def handle_mcp_tool(tool_name: str, arguments: Dict[str, Any], request_id: str, send_response) -> bool:
    """Handle MCP tool calls by delegating to appropriate handlers."""
    
    # Try basic tools first
    if basic_tools.handle_basic_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try communication tools
    if communication_tools.handle_communication_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try agile tools
    if agile_tools.handle_agile_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try project generation tools
    if project_generation_tools.handle_project_generation_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try backend tools
    if backend_tools.handle_backend_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try LLM tools
    if llm_tools.handle_llm_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try dashboard tools
    if dashboard_tools.handle_dashboard_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try Phase 9.1 tools
    if phase9_1_tools.handle_phase9_1_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try Phase 9.2 tools
    if phase9_2_tools.handle_phase9_2_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Try Phase 9.3 tools
    if phase9_3_tools.handle_phase9_3_tool(tool_name, arguments, request_id, send_response):
        return True
    
    # Tool not found
    return False
