"""Basic MCP tools (add_numbers, reverse_text, etc.)."""

from typing import Dict, Any, List


def get_basic_tools() -> List[Dict[str, Any]]:
    """Get basic MCP tools definitions."""
    return [
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
        }
    ]


def handle_basic_tool(tool_name: str, arguments: Dict[str, Any], request_id: str, send_response) -> bool:
    """Handle basic tool calls."""
    if tool_name == "add_numbers":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        result = a + b
        send_response(request_id, {
            "content": [{"type": "text", "text": f"The sum of {a} and {b} is {result}"}],
            "structuredContent": {"result": result}
        })
        return True
        
    elif tool_name == "reverse_text":
        text = arguments.get("text", "")
        result = text[::-1]
        send_response(request_id, {
            "content": [{"type": "text", "text": f"'{text}' reversed is '{result}'"}],
            "structuredContent": {"result": result}
        })
        return True
    
    return False
