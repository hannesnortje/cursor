# Enhanced MCP Server with AI Agent System

This is an enhanced version of the MCP server that adds AI agent system capabilities while preserving all existing functionality.

## 🚀 What's New

### New MCP Tools Added:
1. **`start_project`** - Start a new project with PDCA framework
2. **`chat_with_coordinator`** - Direct communication with Coordinator Agent
3. **`get_project_status`** - Get current project and system status

### Existing Tools Preserved:
1. **`add_numbers`** - Add two integers (original functionality)
2. **`reverse_text`** - Reverse a string (original functionality)

## 🛠️ Quick Start

### 1. Start the Enhanced Server
```bash
python protocol_server.py
```

### 2. Test Existing Tools (Still Work!)
In Cursor, you can still use:
- `add_numbers` with `a=5` and `b=3`
- `reverse_text` with `text="hello"`

### 3. Try New Agent Tools
In Cursor, you can now use:
- `start_project` with `project_type="typescript"` and `project_name="my-app"`
- `chat_with_coordinator` with `message="Can you help me start a project?"`
- `get_project_status` to see current system status

## 🔧 Configuration

The server can be configured using environment variables:

```bash
# Copy the example config
cp config.env.example .env

# Edit .env with your preferences
nano .env
```

### Key Configuration Options:
- **Agent System**: Enable/disable coordinator and specialized agents
- **Database**: Configure Qdrant vector database (optional)
- **LLM Integration**: Enable Cursor LLMs and Docker Ollama
- **Logging**: Set log level and format

## 🧪 Testing

### Run Basic Tests
```bash
python tests/test_enhanced_server.py
```

### Test in Cursor
1. Start the server: `python protocol_server.py`
2. In Cursor, try the new MCP tools
3. Verify existing tools still work

## 📁 Project Structure

```
ai-agent-system/
├── src/
│   ├── agents/           # Agent system modules
│   ├── database/         # Vector database integration
│   ├── communication/    # WebSocket and messaging
│   ├── llm/             # LLM integration
│   ├── utils/           # Utility functions
│   └── config/          # Configuration management
├── tests/               # Test suite
├── docs/                # Documentation
├── scripts/             # Utility scripts
├── protocol_server.py   # Enhanced MCP server
├── config.env.example   # Configuration template
└── README_ENHANCED.md   # This file
```

## 🔍 How It Works

### Agent System Integration
The enhanced server includes an `AgentSystem` class that manages:
- Project lifecycle with PDCA framework
- Coordinator Agent for project planning
- System health monitoring
- Project status tracking

### MCP Tool Enhancement
New tools are seamlessly integrated into the existing MCP protocol:
- Tools are registered during server initialization
- Tool calls are routed to appropriate handlers
- Responses maintain MCP protocol compliance

### Backward Compatibility
- All existing tools work exactly as before
- No changes to existing tool behavior
- Seamless upgrade from original server

## 🎯 Example Usage

### Starting a New Project
```json
{
  "name": "start_project",
  "arguments": {
    "project_type": "typescript",
    "project_name": "social-media-app"
  }
}
```

### Chatting with Coordinator
```json
{
  "name": "chat_with_coordinator",
  "arguments": {
    "message": "I want to build a React app with TypeScript"
  }
}
```

### Getting System Status
```json
{
  "name": "get_project_status",
  "arguments": {}
}
```

## 🚧 Development Status

- **Phase 1.1**: ✅ Project Structure Setup
- **Phase 1.2**: ✅ MCP Server Enhancement
- **Phase 1.3**: 🔄 Testing & Documentation
- **Phase 1.4**: ⏳ Git Setup & Initial Commit

## 🔮 Next Steps

This enhanced server is the foundation for the full AI agent system. Future phases will add:
- Vector database integration
- WebSocket communication
- Specialized agents (Frontend, Backend, Agile)
- LLM integration
- Visual dashboard

## 🐛 Troubleshooting

### Common Issues:
1. **Server won't start**: Check Python version (3.11+ required)
2. **Tools not recognized**: Restart Cursor after starting server
3. **Configuration errors**: Verify .env file format

### Debug Mode:
Set `DEBUG=true` in your .env file for detailed logging.

## 📚 Documentation

- **Implementation Plan**: `IMPLEMENTATION_PLAN.md`
- **Progress Tracker**: `IMPLEMENTATION_PROGRESS.md`
- **System Specs**: `AI_AGENT_SYSTEM_SPECS.md`

## 🤝 Contributing

This is part of a larger AI agent system implementation. See the implementation plan for the complete roadmap.

---

**Note**: This enhanced server maintains 100% backward compatibility while adding powerful new agent capabilities. Your existing MCP tools will continue to work exactly as before.
