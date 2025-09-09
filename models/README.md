# Offline LLM Models Directory

This directory contains offline LLM models for the AI Agent System.

## Current Models

### Phi-2 Model
- **File**: `phi-2.Q4_K_M.gguf`
- **Size**: 1.7 GB
- **Type**: Quantized GGUF format
- **Source**: Microsoft Phi-2
- **Use Case**: General purpose language model

## Ollama Models

The system uses Ollama for local LLM inference. Ollama models are stored in the system directory and accessed via the Ollama API at `http://localhost:11434`.

### Available Ollama Models
- **llama3.1:8b** (4.9 GB) - Primary model for decision making
- **Model ID**: `46e0c10c039e`
- **Context Length**: 131,072 tokens
- **Parameters**: 8.0B
- **Quantization**: Q4_K_M

## Usage

The LLM decision engine automatically uses:
1. **Local Ollama** (llama3.1:8b) as primary
2. **Cursor LLM** as fallback for complex cases
3. **Rule-based logic** as final fallback

## Configuration

Models are configured in `src/llm/simple_decision_engine.py`:
```python
def __init__(self, local_llm_url: str = "http://localhost:11434", 
             model_name: str = "llama3.1:8b"):
```

## Adding New Models

To add new models:
1. Place GGUF files in this directory
2. Update the model configuration in the decision engine
3. Test with the provided test scripts

## Storage Locations

- **Project Models**: `/media/hannesn/storage/Code/cursor/models/`
- **Ollama Models**: System directory (managed by Ollama)
- **Total Storage**: ~6.6 GB (1.7 GB Phi-2 + 4.9 GB Llama 3.1)
