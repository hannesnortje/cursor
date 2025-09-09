#!/usr/bin/env python3
"""
Model Management Script for AI Agent System

This script helps manage offline LLM models and provides information about available models.
"""

import os
import subprocess
import json
from pathlib import Path

def get_ollama_models():
    """Get list of available Ollama models."""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 3:
                        models.append({
                            'name': parts[0],
                            'id': parts[1],
                            'size': parts[2],
                            'modified': ' '.join(parts[3:]) if len(parts) > 3 else 'Unknown'
                        })
            return models
        else:
            print(f"Error getting Ollama models: {result.stderr}")
            return []
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return []

def get_local_models():
    """Get list of local GGUF models in the models directory."""
    models_dir = Path(__file__).parent
    models = []
    
    for file_path in models_dir.glob("*.gguf"):
        stat = file_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        models.append({
            'name': file_path.name,
            'path': str(file_path),
            'size_mb': round(size_mb, 2),
            'size_gb': round(size_mb / 1024, 2)
        })
    
    return models

def check_ollama_status():
    """Check if Ollama server is running."""
    try:
        result = subprocess.run(['curl', '-s', 'http://localhost:11434/api/tags'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return True, "Ollama server is running"
        else:
            return False, "Ollama server not responding"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, "Cannot connect to Ollama server"

def main():
    """Main function to display model information."""
    print("🤖 AI Agent System - Model Management")
    print("=" * 50)
    
    # Check Ollama status
    ollama_running, ollama_status = check_ollama_status()
    print(f"📡 Ollama Status: {ollama_status}")
    
    if ollama_running:
        print("\n🔧 Available Ollama Models:")
        ollama_models = get_ollama_models()
        if ollama_models:
            for model in ollama_models:
                print(f"  • {model['name']} ({model['size']}) - {model['modified']}")
        else:
            print("  No Ollama models found")
    
    print("\n📁 Local GGUF Models:")
    local_models = get_local_models()
    if local_models:
        for model in local_models:
            print(f"  • {model['name']} ({model['size_gb']} GB)")
    else:
        print("  No local GGUF models found")
    
    print(f"\n💾 Total Local Storage: {sum(m['size_gb'] for m in local_models):.1f} GB")
    
    print("\n🎯 Configuration:")
    print("  • Primary LLM: Ollama (llama3.1:8b)")
    print("  • Fallback: Cursor LLM")
    print("  • Final Fallback: Rule-based logic")
    
    print("\n📝 Usage:")
    print("  • Models are automatically used by the decision engine")
    print("  • No manual configuration needed")
    print("  • Check logs for LLM usage details")

if __name__ == "__main__":
    main()
