# MCP Server for Cursor

A Model Context Protocol (MCP) server that provides tools for Cursor editor.

## Features

- **add_numbers**: Add two integers and return the sum
- **reverse_text**: Reverse any given text string
- Full MCP protocol implementation
- Easy to extend with new tools

## Installation

This project uses Poetry for dependency management.

### Prerequisites

- Python 3.10+
- Poetry

### Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

3. **Run the server:**
   ```bash
   poetry run python protocol_server.py
   ```

## Configuration

### Cursor MCP Configuration

Add this to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "mcp-server": {
      "command": "/path/to/your/poetry/env/bin/python",
      "args": ["/path/to/your/protocol_server.py"]
    }
  }
}
```

To find your Poetry environment path:
```bash
poetry env info --path
```

## Development

### Code Quality

- **Formatting**: `poetry run black .`
- **Linting**: `poetry run flake8 .`
- **Type checking**: `poetry run mypy .`
- **Testing**: `poetry run pytest`

### Adding New Tools

1. Add tool definition to the `tools` list in `protocol_server.py`
2. Implement tool logic in the `tools/call` handler
3. Test the tool manually
4. Restart Cursor to see the new tool

## Project Structure

```
.
├── pyproject.toml          # Poetry configuration
├── protocol_server.py      # Main MCP server
├── MCP_Server_Guide.md     # Comprehensive guide
└── README.md               # This file
```

## License

MIT License
