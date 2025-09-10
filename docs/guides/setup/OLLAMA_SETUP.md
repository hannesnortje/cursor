# 🤖 Local LLM Setup with Docker Ollama

This directory contains everything needed to run local LLM models alongside your MCP server using Docker Ollama.

## 🚀 Quick Start

### 1. Start Ollama Service

**With GPU (Recommended):**
```bash
./scripts/manage-ollama.sh start-gpu
```

**CPU Only:**
```bash
./scripts/manage-ollama.sh start-cpu
```

### 2. Download Models
```bash
./scripts/manage-ollama.sh setup
```

This will download efficient models:
- **llama3.2:3b** - Fast general purpose (2GB)
- **codellama:7b** - Specialized for coding (4GB)
- **mistral:7b** - Good for analysis (4GB)

### 3. Test the Service
```bash
./scripts/manage-ollama.sh test
```

## 📊 Model Information

| Model | Size | Use Case | Memory |
|-------|------|----------|---------|
| llama3.2:3b | 2GB | General chat, quick responses | 4GB RAM |
| codellama:7b | 4GB | Code generation, debugging | 8GB RAM |
| mistral:7b | 4GB | Analysis, reasoning | 8GB RAM |

## 🔧 Management Commands

```bash
# Service Management
./scripts/manage-ollama.sh start-gpu     # Start with GPU
./scripts/manage-ollama.sh start-cpu     # Start CPU-only
./scripts/manage-ollama.sh stop          # Stop service
./scripts/manage-ollama.sh restart       # Restart service
./scripts/manage-ollama.sh status        # Check status

# Model Management
./scripts/manage-ollama.sh models        # List models
./scripts/manage-ollama.sh pull llama3.1:8b  # Pull specific model
./scripts/manage-ollama.sh setup         # Setup default models

# Monitoring
./scripts/manage-ollama.sh logs          # Show logs
./scripts/manage-ollama.sh test          # Test functionality

# Maintenance
./scripts/manage-ollama.sh clean         # Remove all data
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MCP Server    │ ── │   LLM Gateway   │ ── │  Docker Ollama  │
│ (Port 4000)     │    │                 │    │ (Port 11434)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────│  Cursor LLM     │              │
                        │   (Fallback)    │              │
                        └─────────────────┘              │
                                                          │
                                                ┌─────────────────┐
                                                │  Local Models   │
                                                │  (Persistent)   │
                                                └─────────────────┘
```

## 🔧 Configuration

### GPU Requirements
- NVIDIA GPU with 6GB+ VRAM (recommended)
- CUDA drivers installed
- nvidia-docker2 installed

### CPU Requirements
- 8GB+ RAM (16GB recommended)
- Modern multi-core CPU

### Storage Requirements
- 10GB+ free space for models
- SSD recommended for better performance

## 🚨 Troubleshooting

### Service won't start
```bash
# Check Docker
docker --version
docker compose version

# Check system resources
./scripts/manage-ollama.sh status
docker compose logs
```

### Models won't download
```bash
# Check internet connection
curl -I https://ollama.ai

# Check disk space
df -h

# Try manual download
./scripts/manage-ollama.sh pull llama3.2:3b
```

### Slow performance
```bash
# Check if GPU is being used
nvidia-smi  # Should show ollama process

# Check memory usage
docker stats

# Try smaller models
./scripts/manage-ollama.sh pull phi3:mini
```

## 🔗 Integration with MCP Server

The LLM Gateway automatically detects and uses local Ollama models:

1. **Primary**: Local Ollama models (fastest, private)
2. **Fallback**: Cursor built-in LLM (when local unavailable)

Test integration:
```bash
# Start MCP server (in another terminal)
poetry run python protocol_server.py

# Test with coordinator
poetry run python -c "
from src.agents.coordinator.coordinator_integration import process_user_message_with_memory
import asyncio
response = asyncio.run(process_user_message_with_memory('Hello, test local LLM'))
print(response)
"
```

## 📁 File Structure

```
cursor/
├── docker-compose.yml          # Docker services
├── .env.ollama                 # Configuration
├── scripts/
│   ├── manage-ollama.sh        # Management script
│   └── setup-models.sh         # Model setup
└── docs/
    └── OLLAMA_SETUP.md         # This file
```

## 🎯 Next Steps

1. **Start the service**: `./scripts/manage-ollama.sh start-gpu`
2. **Setup models**: `./scripts/manage-ollama.sh setup`
3. **Test integration**: `./scripts/manage-ollama.sh test`
4. **Start your MCP server**: `poetry run python protocol_server.py`
5. **Use with Cursor**: Chat with coordinator using local LLMs!

## 🔒 Privacy & Security

- **✅ Fully local**: No data sent to external services
- **✅ Persistent**: Models stay downloaded
- **✅ Isolated**: Runs in Docker containers
- **✅ Secure**: No external network access required

Your code and conversations stay completely private! 🔐
