# MCP Server Guide for Cursor

## What is MCP?

**MCP (Model Context Protocol)** is a protocol that allows AI assistants and tools to communicate with each other. In Cursor, MCP servers provide additional tools and capabilities that can be used alongside the built-in AI features.

## Prerequisites

- Python 3.8+ installed
- Cursor editor
- Basic understanding of Python and JSON

## Step 1: Set Up Your Project

### Create a new directory for your MCP server:
```bash
mkdir my-mcp-server
cd my-mcp-server
```

### Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install required packages:
```bash
pip install mcp
```

## Step 2: Create Your MCP Server

### Basic MCP Server Structure

Create a file called `server.py`:

```python
#!/usr/bin/env python3
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my-mcp-server")

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
    logger.info("Starting MCP server...")
    
    # Define your tools
    tools = [
        {
            "name": "example_tool",
            "description": "An example tool that does something useful.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "input_param": {"type": "string", "description": "Input parameter"}
                },
                "required": ["input_param"]
            }
        }
        # Add more tools here
    ]
    
    # Server initialization response
    init_response = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "tools": tools
            }
        },
        "serverInfo": {
            "name": "my-mcp-server",
            "version": "1.0.0"
        }
    }
    
    # Main message loop
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                # Handle initialization
                send_response(request_id, init_response)
                send_notification("initialized")
                
            elif method == "tools/list":
                # Return list of available tools
                tools_response = {"tools": tools}
                send_response(request_id, tools_response)
                
            elif method == "tools/call":
                # Handle tool execution
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                if tool_name == "example_tool":
                    # Your tool logic here
                    input_param = arguments.get("input_param", "")
                    result = f"Processed: {input_param}"
                    
                    send_response(request_id, {
                        "content": [{"type": "text", "text": result}],
                        "structuredContent": {"result": result}
                    })
                else:
                    send_response(request_id, error={
                        "code": -32601, 
                        "message": f"Unknown tool: {tool_name}"
                    })
                    
            else:
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error: {e}")

if __name__ == "__main__":
    main()
```

## Step 3: Configure Cursor

### Create MCP Configuration

Create or edit the file: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["/path/to/your/server.py"]
    }
  }
}
```

**Important**: Replace the paths with your actual paths:
- `command`: Full path to your virtual environment's Python interpreter
- `args`: Full path to your server script

### Example with absolute paths:
```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "/home/user/projects/my-mcp-server/venv/bin/python",
      "args": ["/home/user/projects/my-mcp-server/server.py"]
    }
  }
}
```

## Step 4: Test Your Server

### Test the server manually:
```bash
source venv/bin/activate
python server.py
```

### Test with a simple MCP message:
```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | python server.py
```

## Step 5: Restart Cursor

1. **Completely close Cursor**
2. **Wait 10 seconds**
3. **Restart Cursor**
4. **Go to Settings** → **Extensions** → **MCP**

## Step 6: Verify Connection

- **Green status** = Connection successful
- **Red dot** = Connection failed
- **Tools listed** = Server working properly

## Creating Custom Tools

### Tool Structure
Each tool needs:
- **name**: Unique identifier
- **description**: What the tool does
- **inputSchema**: JSON schema for input parameters

### Example Tool
```python
{
    "name": "calculate_area",
    "description": "Calculate the area of a rectangle.",
    "inputSchema": {
        "type": "object",
        "properties": {
            "width": {"type": "number", "description": "Width of rectangle"},
            "height": {"type": "number", "description": "Height of rectangle"}
        },
        "required": ["width", "height"]
    }
}
```

### Tool Implementation
```python
elif method == "tools/call":
    tool_name = data.get("params", {}).get("name")
    arguments = data.get("params", {}).get("arguments", {})
    
    if tool_name == "calculate_area":
        width = arguments.get("width", 0)
        height = arguments.get("height", 0)
        area = width * height
        
        send_response(request_id, {
            "content": [{"type": "text", "text": f"Area: {area}"}],
            "structuredContent": {"area": area}
        })
```

## Troubleshooting

### Red Dot (Connection Failed)
- Check file paths in `mcp.json`
- Ensure server script is executable
- Verify virtual environment has required packages
- Check server logs for errors

### No Tools Listed
- Verify server responds to `tools/list` requests
- Check tool schema format
- Ensure proper JSON-RPC responses

### Server Won't Start
- Check Python path in `mcp.json`
- Verify virtual environment activation
- Check for syntax errors in server code

## Advanced Features

### Adding More Capabilities
```python
init_response = {
    "protocolVersion": "2024-11-05",
    "capabilities": {
        "tools": {"tools": tools},
        "resources": {"resources": []},
        "prompts": {"prompts": []}
    },
    "serverInfo": {
        "name": "my-mcp-server",
        "version": "1.0.0"
    }
}
```

### Error Handling
```python
try:
    # Your tool logic
    result = process_tool_call(tool_name, arguments)
    send_response(request_id, result)
except Exception as e:
    send_response(request_id, error={
        "code": -32603,
        "message": f"Internal error: {str(e)}"
    })
```

### Logging
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Best Practices

1. **Use absolute paths** in `mcp.json`
2. **Test server manually** before configuring Cursor
3. **Handle all MCP methods** properly
4. **Provide meaningful error messages**
5. **Log important events** for debugging
6. **Use proper JSON-RPC format**
7. **Validate input parameters**
8. **Handle exceptions gracefully**

## Example Complete Server

See the `protocol_server.py` file in this project for a complete working example with:
- `add_numbers` tool
- `reverse_text` tool
- Proper MCP protocol implementation
- Error handling
- Logging

## Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Python Package](https://github.com/modelcontextprotocol/python-sdk)
- [Cursor Documentation](https://cursor.sh/docs)

---

**Happy MCP Server Building! 🚀**
