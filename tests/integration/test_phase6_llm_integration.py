#!/usr/bin/env python3
"""
Phase 6: LLM Integration & Model Orchestration Tests

This test file verifies the implementation of Phase 6 features:
- LLM Gateway integration
- Model selection and orchestration
- Text generation with fallback
- Performance monitoring
- Integration testing
"""

import sys
import os
import asyncio
import pytest
from unittest.mock import patch, MagicMock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.llm.llm_gateway import LLMGateway, LLMModel, LLMProvider, ModelType
from src.llm.enhanced_autogen import EnhancedAutoGen, AgentRole


class TestLLMGateway:
    """Test LLM Gateway functionality."""
    
    def test_llm_gateway_initialization(self):
        """Test LLM Gateway initialization."""
        gateway = LLMGateway()
        assert gateway is not None
        assert hasattr(gateway, 'cursor_llms')
        assert hasattr(gateway, 'docker_ollama')
        assert hasattr(gateway, 'model_performance')
        assert hasattr(gateway, 'fallback_strategy')
    
    @patch('src.llm.llm_gateway.CursorLLMProvider')
    @patch('src.llm.llm_gateway.DockerOllamaProvider')
    async def test_get_available_models(self, mock_ollama, mock_cursor):
        """Test getting available models from all providers."""
        # Mock cursor models
        mock_cursor_instance = MagicMock()
        mock_cursor_instance.get_available_models.return_value = [
            LLMModel(
                name="cursor-gpt-4",
                provider=LLMProvider.CURSOR,
                model_type=ModelType.GENERAL,
                max_tokens=4096,
                temperature=0.7,
                api_base="http://localhost:8000"
            )
        ]
        mock_cursor.return_value = mock_cursor_instance
        
        # Mock ollama models
        mock_ollama_instance = MagicMock()
        mock_ollama_instance.get_available_models.return_value = [
            LLMModel(
                name="llama2",
                provider=LLMProvider.DOCKER_OLLAMA,
                model_type=ModelType.CODING,
                max_tokens=4096,
                temperature=0.3,
                api_base="http://localhost:11434"
            )
        ]
        mock_ollama.return_value = mock_ollama_instance
        
        gateway = LLMGateway()
        result = await gateway.get_available_models()
        
        assert "cursor" in result
        assert "docker_ollama" in result
        assert result["total_count"] == 2
    
    async def test_select_best_model(self):
        """Test model selection logic."""
        gateway = LLMGateway()
        
        # Mock available models
        with patch.object(gateway, 'get_available_models') as mock_get_models:
            mock_get_models.return_value = {
                "cursor": [
                    LLMModel(
                        name="cursor-gpt-4",
                        provider=LLMProvider.CURSOR,
                        model_type=ModelType.CODING,
                        max_tokens=4096,
                        temperature=0.7,
                        api_base="http://localhost:8000",
                        success_rate=0.95,
                        response_time=1.2
                    )
                ],
                "docker_ollama": [
                    LLMModel(
                        name="llama2",
                        provider=LLMProvider.DOCKER_OLLAMA,
                        model_type=ModelType.CODING,
                        max_tokens=4096,
                        temperature=0.3,
                        api_base="http://localhost:11434",
                        success_rate=0.90,
                        response_time=2.1
                    )
                ]
            }
            
            # Test coding task selection
            selected_model = await gateway.select_best_model("coding", "Write Python code")
            assert selected_model.model_type == ModelType.CODING
            assert selected_model.name == "cursor-gpt-4"  # Higher success rate
    
    async def test_generate_with_fallback(self):
        """Test text generation with fallback mechanism."""
        gateway = LLMGateway()
        
        # Mock model selection
        with patch.object(gateway, 'select_best_model') as mock_select:
            mock_select.return_value = LLMModel(
                name="cursor-gpt-4",
                provider=LLMProvider.CURSOR,
                model_type=ModelType.GENERAL,
                max_tokens=4096,
                temperature=0.7,
                api_base="http://localhost:8000"
            )
            
            # Mock cursor generation
            with patch.object(gateway.cursor_llms, 'generate') as mock_generate:
                mock_generate.return_value = "Generated text response"
                
                result = await gateway.generate_with_fallback(
                    "Test prompt", "general"
                )
                
                assert result == "Generated text response"
                mock_generate.assert_called_once()
    
    def test_performance_tracking(self):
        """Test model performance tracking."""
        gateway = LLMGateway()
        
        # Update performance metrics
        gateway._update_model_performance("test-model", True)
        gateway._update_model_performance("test-model", False)
        gateway._update_model_performance("test-model", True)
        
        stats = gateway.get_performance_stats()
        assert "test-model" in stats
        assert stats["test-model"]["success_rate"] == 2/3
        assert stats["test-model"]["total_requests"] == 3


class TestAutoGenIntegration:
    """Test AutoGen integration functionality."""
    
    def test_autogen_config(self):
        """Test AutoGen configuration."""
        config = AutoGenConfig(
            model_name="gpt-4",
            api_base="http://localhost:8000",
            temperature=0.7,
            max_tokens=4096
        )
        
        assert config.model_name == "gpt-4"
        assert config.api_base == "http://localhost:8000"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
    
    def test_autogen_agent_wrapper(self):
        """Test AutoGen agent wrapper."""
        config = AutoGenConfig(
            model_name="gpt-4",
            api_base="http://localhost:8000"
        )
        
        wrapper = AutoGenAgentWrapper("test-agent", "assistant", config)
        assert wrapper.agent_id == "test-agent"
        assert wrapper.agent_type == "assistant"
        assert wrapper.config == config
    
    async def test_process_message(self):
        """Test message processing."""
        config = AutoGenConfig(
            model_name="gpt-4",
            api_base="http://localhost:8000"
        )
        
        wrapper = AutoGenAgentWrapper("test-agent", "assistant", config)
        
        # Test message processing
        response = await wrapper.process_message("Hello, test message")
        assert "AutoGen Agent test-agent" in response
        assert "Hello, test message" in response
        
        # Check conversation history
        assert len(wrapper.conversation_history) == 1
        assert wrapper.conversation_history[0]["message"] == "Hello, test message"


class TestLLMIntegrationEndToEnd:
    """Test end-to-end LLM integration."""
    
    @patch('src.llm.llm_gateway.httpx.AsyncClient')
    async def test_cursor_llm_integration(self, mock_client):
        """Test Cursor LLM integration."""
        # Mock HTTP client response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": ["cursor-gpt-4", "cursor-claude-3"],
            "response": "Test response from Cursor LLM"
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        from src.llm.llm_gateway import CursorLLMProvider
        
        provider = CursorLLMProvider()
        models = await provider.get_available_models()
        
        assert len(models) > 0
        assert any("cursor-gpt-4" in model.name for model in models)
    
    @patch('src.llm.llm_gateway.httpx.AsyncClient')
    async def test_docker_ollama_integration(self, mock_client):
        """Test Docker Ollama integration."""
        # Mock HTTP client response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": ["llama2", "codellama"],
            "response": "Test response from Ollama"
        }
        
        mock_client_instance = MagicMock()
        mock_client_instance.__aenter__.return_value = mock_client_instance
        mock_client_instance.__aexit__.return_value = None
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        from src.llm.llm_gateway import DockerOllamaProvider
        
        provider = DockerOllamaProvider()
        models = await provider.get_available_models()
        
        assert len(models) > 0
        assert any("llama2" in model.name for model in models)


class TestLLMOrchestration:
    """Test LLM model orchestration."""
    
    async def test_model_orchestration(self):
        """Test multiple model orchestration."""
        gateway = LLMGateway()
        
        # Mock available models with different capabilities
        with patch.object(gateway, 'get_available_models') as mock_get_models:
            mock_get_models.return_value = {
                "cursor": [
                    LLMModel(
                        name="cursor-gpt-4",
                        provider=LLMProvider.CURSOR,
                        model_type=ModelType.CODING,
                        max_tokens=4096,
                        temperature=0.7,
                        api_base="http://localhost:8000"
                    ),
                    LLMModel(
                        name="cursor-claude-3",
                        provider=LLMProvider.CURSOR,
                        model_type=ModelType.CREATIVE,
                        max_tokens=4096,
                        temperature=0.8,
                        api_base="http://localhost:8000"
                    )
                ],
                "docker_ollama": [
                    LLMModel(
                        name="llama2",
                        provider=LLMProvider.DOCKER_OLLAMA,
                        model_type=ModelType.ANALYSIS,
                        max_tokens=4096,
                        temperature=0.3,
                        api_base="http://localhost:11434"
                    )
                ]
            }
            
            # Test orchestration for complex task
            selected_models = await gateway.select_best_model("coding", "Write Python code")
            assert selected_models.model_type == ModelType.CODING
            
            # Test fallback to general models
            general_models = await gateway.select_best_model("general", "General task")
            assert general_models is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
