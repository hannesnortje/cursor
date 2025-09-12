"""
AutoGen Cursor Client Wrapper

This module provides a wrapper that makes AutoGen use Cursor's internal LLM system
instead of external OpenAI API calls. It implements the OpenAI client interface
that AutoGen expects while redirecting all calls to our CursorLLMBridge.

This enables AutoGen agents to use Cursor's actual LLMs for dynamic content generation.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, AsyncGenerator
from dataclasses import dataclass
import json

from .cursor_llm_bridge import CursorLLMBridge

logger = logging.getLogger(__name__)


class MockOpenAIResponse:
    """Mock OpenAI response object that AutoGen expects."""
    
    def __init__(self, response_data: Dict[str, Any]):
        self.data = response_data
        self.choices = [MockChoice(choice) for choice in response_data.get("choices", [])]
        self.id = response_data.get("id", "")
        self.object = response_data.get("object", "chat.completion")
        self.created = response_data.get("created", 0)
        self.model = response_data.get("model", "")
        self.usage = MockUsage(response_data.get("usage", {}))
    
    def __getitem__(self, key):
        return self.data[key]
    
    def get(self, key, default=None):
        return self.data.get(key, default)


class MockChoice:
    """Mock choice object that AutoGen expects."""
    
    def __init__(self, choice_data: Dict[str, Any]):
        self.data = choice_data
        self.index = choice_data.get("index", 0)
        self.message = MockMessage(choice_data.get("message", {}))
        self.finish_reason = choice_data.get("finish_reason", "stop")
    
    def __getitem__(self, key):
        return self.data[key]
    
    def get(self, key, default=None):
        return self.data.get(key, default)


class MockMessage:
    """Mock message object that AutoGen expects."""
    
    def __init__(self, message_data: Dict[str, Any]):
        self.data = message_data
        self.role = message_data.get("role", "assistant")
        self.content = message_data.get("content", "")
    
    def __getitem__(self, key):
        return self.data[key]
    
    def get(self, key, default=None):
        return self.data.get(key, default)


class MockUsage:
    """Mock usage object that AutoGen expects."""
    
    def __init__(self, usage_data: Dict[str, Any]):
        self.data = usage_data
        self.prompt_tokens = usage_data.get("prompt_tokens", 0)
        self.completion_tokens = usage_data.get("completion_tokens", 0)
        self.total_tokens = usage_data.get("total_tokens", 0)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def get(self, key, default=None):
        return self.data.get(key, default)


class AutoGenCursorClient:
    """
    AutoGen-compatible client that uses Cursor's LLM system.
    
    This class implements the OpenAI client interface that AutoGen expects,
    but redirects all calls to Cursor's internal LLM system via CursorLLMBridge.
    
    AutoGen will treat this as a normal OpenAI client, but it will actually
    use Cursor's LLMs for generation.
    """
    
    def __init__(self, cursor_bridge: Optional[CursorLLMBridge] = None):
        self.cursor_bridge = cursor_bridge or CursorLLMBridge()
        self.chat = MockChatCompletion(self.cursor_bridge)
        
        # Mock attributes that AutoGen might expect
        self.api_key = "cursor-internal"
        self.api_base = "cursor://builtin"
        self.api_version = "cursor-v1"
        
        logger.info("AutoGenCursorClient initialized with Cursor LLM bridge")
    
    async def initialize(self):
        """Initialize the client and discover available models."""
        await self.cursor_bridge.discover_models()
        available_models = self.cursor_bridge.get_available_model_names()
        logger.info(f"AutoGenCursorClient ready with models: {available_models}")


class MockChatCompletion:
    """Mock chat completion interface that AutoGen expects."""
    
    def __init__(self, cursor_bridge: CursorLLMBridge):
        self.cursor_bridge = cursor_bridge
    
    async def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[MockOpenAIResponse, AsyncGenerator]:
        """
        Create a chat completion using Cursor's LLM system.
        
        This method intercepts AutoGen's OpenAI API calls and redirects them
        to Cursor's internal LLM system for actual generation.
        """
        try:
            logger.info(f"AutoGen requesting completion from model: {model}")
            logger.debug(f"Messages: {messages}")
            
            # Check if model is available in Cursor
            available_models = self.cursor_bridge.get_available_model_names()
            
            # Map common AutoGen model names to Cursor models
            cursor_model = self._map_model_name(model, available_models)
            
            if not cursor_model:
                # Fallback to preferred model
                cursor_model = self.cursor_bridge.get_preferred_model("general")
                if not cursor_model:
                    raise ValueError(f"No Cursor models available for AutoGen request")
                logger.warning(f"Model {model} not found, using {cursor_model}")
            
            # Generate response using Cursor LLM
            response_data = await self.cursor_bridge.generate_response(
                model_name=cursor_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Return response in format AutoGen expects
            if stream:
                return self._create_stream_response(response_data)
            else:
                response = MockOpenAIResponse(response_data)
                logger.info(f"Successfully generated response using Cursor model {cursor_model}")
                return response
                
        except Exception as e:
            logger.error(f"Error in AutoGen Cursor completion: {e}")
            # Return error response in format AutoGen expects
            return self._create_error_response(str(e))
    
    def _map_model_name(self, requested_model: str, available_models: List[str]) -> Optional[str]:
        """Map AutoGen model names to available Cursor models."""
        
        # Direct match
        if requested_model in available_models:
            return requested_model
        
        # Common mappings
        model_mappings = {
            "gpt-4": "gpt-4o",
            "gpt-3.5-turbo": "gpt-4o",
            "claude-3-sonnet": "claude-3-5-sonnet",
            "claude": "claude-3-5-sonnet",
        }
        
        if requested_model in model_mappings:
            mapped_model = model_mappings[requested_model]
            if mapped_model in available_models:
                return mapped_model
        
        # Partial matching for similar names
        for available_model in available_models:
            if requested_model.lower() in available_model.lower():
                return available_model
            if available_model.lower() in requested_model.lower():
                return available_model
        
        return None
    
    async def _create_stream_response(self, response_data: Dict[str, Any]) -> AsyncGenerator:
        """Create streaming response for AutoGen."""
        # For now, we'll convert the complete response to a stream format
        # A full implementation would handle true streaming from Cursor
        
        content = response_data["choices"][0]["message"]["content"]
        words = content.split()
        
        for i, word in enumerate(words):
            chunk_data = {
                "id": response_data["id"],
                "object": "chat.completion.chunk",
                "created": response_data["created"],
                "model": response_data["model"],
                "choices": [{
                    "index": 0,
                    "delta": {"content": word + " " if i < len(words) - 1 else word},
                    "finish_reason": None if i < len(words) - 1 else "stop"
                }]
            }
            yield MockOpenAIResponse(chunk_data)
            await asyncio.sleep(0.02)  # Simulate streaming delay
    
    def _create_error_response(self, error_message: str) -> MockOpenAIResponse:
        """Create error response in format AutoGen expects."""
        error_data = {
            "id": "error-response",
            "object": "chat.completion",
            "created": int(asyncio.get_event_loop().time()),
            "model": "cursor-error",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Error: {error_message}"
                },
                "finish_reason": "error"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
        return MockOpenAIResponse(error_data)


def create_autogen_cursor_config(
    models: Optional[List[str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> Dict[str, Any]:
    """
    Create AutoGen-compatible LLM config for Cursor models.
    
    This function creates the configuration that AutoGen expects,
    but configured to use our Cursor LLM bridge.
    
    Args:
        models: List of preferred models (will be mapped to available Cursor models)
        temperature: Default temperature for generation
        max_tokens: Default max tokens for generation
        
    Returns:
        AutoGen-compatible LLM configuration
    """
    
    # Default models if none specified
    if models is None:
        models = ["gpt-4o", "claude-3-5-sonnet", "gpt-4-turbo"]
    
    return {
        "config_list": [
            {
                "model": model,
                "api_key": "cursor-internal",
                "api_base": "cursor://builtin",
                "api_type": "cursor",
                "api_version": "cursor-v1"
            }
            for model in models
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timeout": 60,
        "cache_seed": None,  # Disable caching for real LLM responses
    }


async def test_autogen_cursor_client():
    """Test the AutoGen Cursor Client functionality."""
    
    # Create and initialize client
    client = AutoGenCursorClient()
    await client.initialize()
    
    # Test completion
    test_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    print("Testing AutoGen Cursor Client...")
    response = await client.chat.create(
        model="gpt-4o",
        messages=test_messages,
        temperature=0.7
    )
    
    print(f"Model: {response.model}")
    print(f"Response: {response.choices[0].message.content}")
    print(f"Usage: {response.usage.total_tokens} tokens")


if __name__ == "__main__":
    asyncio.run(test_autogen_cursor_client())
