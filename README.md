# AI Agent System with Cursor Integration

A sophisticated AI Agent System built on the Model Context Protocol (MCP) that provides advanced tools for Cursor editor, including AutoGen integration, vector database storage, and specialized agents for project management.

## Features

- **🤖 AutoGen Integration**: Multi-agent conversations and coordination
- **🗄️ Vector Database**: Qdrant-based context and memory storage
- **🎭 Coordinator Agent**: Central orchestration and PDCA framework
- **📋 Agile/Scrum Agent**: Sprint planning and user story management
- **🏗️ Project Generation Agent**: Multi-language project scaffolding
- **🌐 Cross-Chat Communication**: Real-time communication across sessions
- **💾 Persistent Storage**: Redis-based message persistence
- **🔧 MCP Tools**: Comprehensive toolset for Cursor integration

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
├── src/                    # Source code and agent implementations
├── tests/                  # Comprehensive test suite
├── test_prompts/           # Testing prompts and guides
├── docs/                   # Complete documentation
├── pyproject.toml          # Poetry configuration
├── protocol_server.py      # Main MCP server
└── README.md               # This file
```

## Documentation

- [📚 docs/README.md](docs/README.md) - Documentation index and navigation
- [📊 docs/implementation/IMPLEMENTATION_PROGRESS.md](docs/implementation/IMPLEMENTATION_PROGRESS.md) - Current status
- [📋 docs/implementation/IMPLEMENTATION_PLAN.md](docs/implementation/IMPLEMENTATION_PLAN.md) - Roadmap
- [🔧 docs/guides/MCP_Server_Guide.md](docs/guides/MCP_Server_Guide.md) - Usage guide
- [🧪 tests/README.md](tests/README.md) - Testing framework
- [🗣️ test_prompts/README.md](test_prompts/README.md) - Testing prompts

## License

MIT License
