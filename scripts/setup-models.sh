#!/bin/bash

# Setup script for Ollama models
# This script downloads the models specified in the LLM Gateway

echo "🚀 Setting up Ollama models for MCP Server..."

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service to start..."
while ! curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "Waiting for Ollama..."
    sleep 5
done

echo "✅ Ollama service is ready!"

# Function to pull a model with error handling
pull_model() {
    local model=$1
    echo "📥 Pulling model: $model"

    if ollama pull "$model"; then
        echo "✅ Successfully pulled: $model"
    else
        echo "❌ Failed to pull: $model"
        return 1
    fi
}

# Pull the models defined in LLM Gateway
echo "📦 Downloading efficient models for coding and general tasks..."

# Small, efficient models that work well for most tasks
pull_model "llama3.2:3b"     # 3B parameter model - good balance of size/performance
pull_model "codellama:7b"    # 7B specialized for coding
pull_model "mistral:7b"      # 7B model good for analysis

# Optional: Larger models (uncomment if you have enough storage/memory)
# pull_model "llama3.1:8b"   # Larger general model
# pull_model "deepseek-coder:6.7b"  # Specialized coding model

echo "🎉 Model setup complete!"
echo "📊 Available models:"
ollama list

echo "🔧 Testing model functionality..."
echo "Testing llama3.2:3b..."
echo "Hello, can you help me with coding?" | ollama run llama3.2:3b --verbose

echo "✅ Setup complete! Your local LLM models are ready to use."
