#!/usr/bin/env python3
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("protocol-mcp-server")

def send_response(request_id, result=None, error=None):
    """Send a JSON-RPC response."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)

def send_notification(method, params=None):
    """Send a JSON-RPC notification."""
    notification = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params:
        notification["params"] = params
    
    print(json.dumps(notification), flush=True)

def main():
    logger.info("Starting protocol MCP server...")
    
    # Send initialization response
    init_response = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "tools": [
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
            }
        },
        "serverInfo": {
            "name": "protocol-mcp-server",
            "version": "1.0.0"
        }
    }
    
    # Read input and respond
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                send_response(request_id, init_response)
                # Send initialized notification
                send_notification("initialized")
                
            elif method == "tools/list":
                tools_response = {
                    "tools": [
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
                }
                send_response(request_id, tools_response)
                
            elif method == "tools/call":
                # Handle tool calls
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                if tool_name == "add_numbers":
                    a = arguments.get("a", 0)
                    b = arguments.get("b", 0)
                    result = a + b
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"The sum of {a} and {b} is {result}"}],
                        "structuredContent": {"result": result}
                    })
                    
                elif tool_name == "reverse_text":
                    text = arguments.get("text", "")
                    result = text[::-1]
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"'{text}' reversed is '{result}'"}],
                        "structuredContent": {"result": result}
                    })
                    
                else:
                    send_response(request_id, error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
                    
            else:
                # Handle other methods
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
