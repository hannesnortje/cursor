#!/bin/bash
# Setup script for local LLM environment

echo "🤖 AI Agent System - LLM Setup"
echo "================================"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama is installed at $(which ollama)"
fi

# Check if Ollama service is running
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama service is running"
else
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 5
fi

# Check if llama3.1:8b is available
if ollama list | grep -q "llama3.1:8b"; then
    echo "✅ llama3.1:8b model is available"
else
    echo "📥 Downloading llama3.1:8b model..."
    ollama pull llama3.1:8b
fi

# Test the model
echo "🧪 Testing LLM connection..."
if curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama3.1:8b",
        "prompt": "Hello",
        "stream": false
    }' > /dev/null; then
    echo "✅ LLM is responding correctly"
else
    echo "❌ LLM test failed"
fi

echo ""
echo "📊 Current setup:"
ollama list

echo ""
echo "🎯 Configuration:"
echo "  • LLM Server: http://localhost:11434"
echo "  • Primary Model: llama3.1:8b"
echo "  • Model Storage: System managed by Ollama"
echo "  • Your Code: /media/hannesn/storage/Code/cursor"
echo ""
echo "✅ Local LLM setup complete!"
