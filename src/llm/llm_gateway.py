"""LLM Gateway for intelligent model selection and dual LLM support."""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import httpx
import json

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM provider types."""
    CURSOR = "cursor"
    DOCKER_OLLAMA = "docker_ollama"
    LM_STUDIO = "lm_studio"


class ModelType(Enum):
    """Model type categories."""
    GENERAL = "general"
    CODING = "coding"
    CREATIVE = "creative"
    ANALYSIS = "analysis"


@dataclass
class LLMModel:
    """LLM model configuration."""
    name: str
    provider: LLMProvider
    model_type: ModelType
    max_tokens: int
    temperature: float
    api_base: str
    api_key: Optional[str] = None
    is_available: bool = True
    response_time: float = 0.0
    success_rate: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "provider": self.provider.value,
            "model_type": self.model_type.value,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_base": self.api_base,
            "is_available": self.is_available,
            "response_time": self.response_time,
            "success_rate": self.success_rate
        }
    
    def __json__(self):
        """JSON serialization support."""
        return self.to_dict()


class CursorLLMProvider:
    """Cursor LLM provider integration."""
    
    def __init__(self, api_base: str = "http://localhost:8000/cursor-llm"):
        self.api_base = api_base
        self.available_models = self._get_default_cursor_models()
    
    def _get_default_cursor_models(self) -> List[LLMModel]:
        """Get default Cursor LLM models."""
        return [
            LLMModel(
                name="cursor-gpt-4-turbo",
                provider=LLMProvider.CURSOR,
                model_type=ModelType.GENERAL,
                max_tokens=4096,
                temperature=0.7,
                api_base=self.api_base
            ),
            LLMModel(
                name="cursor-claude-3-sonnet",
                provider=LLMProvider.CURSOR,
                model_type=ModelType.CODING,
                max_tokens=4096,
                temperature=0.3,
                api_base=self.api_base
            ),
            LLMModel(
                name="cursor-gpt-4o",
                provider=LLMProvider.CURSOR,
                model_type=ModelType.CREATIVE,
                max_tokens=4096,
                temperature=0.8,
                api_base=self.api_base
            )
        ]
    
    async def get_available_models(self) -> List[LLMModel]:
        """Get available Cursor LLM models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/models")
                if response.status_code == 200:
                    models_data = response.json()
                    # Update available models based on response
                    for model in self.available_models:
                        model.is_available = model.name in models_data.get("models", [])
                else:
                    logger.warning(f"Failed to get Cursor models: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting Cursor models: {e}")
        
        return [model for model in self.available_models if model.is_available]
    
    async def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate text using Cursor LLM."""
        try:
            model = next((m for m in self.available_models if m.name == model_name), None)
            if not model:
                raise ValueError(f"Model {model_name} not found")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "max_tokens": kwargs.get("max_tokens", model.max_tokens),
                        "temperature": kwargs.get("temperature", model.temperature)
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("text", "")
                else:
                    raise Exception(f"Cursor LLM generation failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating with Cursor LLM: {e}")
            raise


class DockerOllamaProvider:
    """Docker Ollama LLM provider integration."""
    
    def __init__(self, api_base: str = "http://localhost:11434"):
        self.api_base = api_base
        self.available_models = self._get_default_ollama_models()
    
    def _get_default_ollama_models(self) -> List[LLMModel]:
        """Get default Docker Ollama models."""
        return [
            LLMModel(
                name="llama3.2:3b",
                provider=LLMProvider.DOCKER_OLLAMA,
                model_type=ModelType.GENERAL,
                max_tokens=2048,
                temperature=0.7,
                api_base=self.api_base
            ),
            LLMModel(
                name="codellama:7b",
                provider=LLMProvider.DOCKER_OLLAMA,
                model_type=ModelType.CODING,
                max_tokens=2048,
                temperature=0.3,
                api_base=self.api_base
            ),
            LLMModel(
                name="mistral:7b",
                provider=LLMProvider.DOCKER_OLLAMA,
                model_type=ModelType.ANALYSIS,
                max_tokens=2048,
                temperature=0.5,
                api_base=self.api_base
            )
        ]
    
    async def get_available_models(self) -> List[LLMModel]:
        """Get available Docker Ollama models."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.api_base}/api/tags")
                if response.status_code == 200:
                    models_data = response.json()
                    available_names = [model["name"] for model in models_data.get("models", [])]
                    
                    # Update available models based on response
                    for model in self.available_models:
                        model.is_available = model.name in available_names
                else:
                    logger.warning(f"Failed to get Ollama models: {response.status_code}")
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
        
        return [model for model in self.available_models if model.is_available]
    
    async def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """Generate text using Docker Ollama."""
        try:
            model = next((m for m in self.available_models if m.name == model_name), None)
            if not model:
                raise ValueError(f"Model {model_name} not found")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": kwargs.get("max_tokens", model.max_tokens),
                            "temperature": kwargs.get("temperature", model.temperature)
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama generation failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise


class LLMGateway:
    """Intelligent LLM Gateway for model selection and fallback."""
    
    def __init__(self):
        self.cursor_llms = CursorLLMProvider()
        self.docker_ollama = DockerOllamaProvider()
        self.model_performance = {}  # Track model performance
        self.fallback_strategy = "auto"  # auto, cursor_first, ollama_first
    
    async def get_available_models(self) -> Dict[str, List[LLMModel]]:
        """Get all available models from all providers."""
        try:
            cursor_models = await self.cursor_llms.get_available_models()
        except Exception as e:
            logger.warning(f"Failed to get Cursor models: {e}")
            cursor_models = []
        
        try:
            ollama_models = await self.docker_ollama.get_available_models()
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
            ollama_models = []
        
        return {
            "cursor": cursor_models,
            "docker_ollama": ollama_models,
            "total_count": len(cursor_models) + len(ollama_models)
        }
    
    async def select_best_model(self, task_type: str, context: str = "") -> LLMModel:
        """Select the best model for the given task."""
        available_models = await self.get_available_models()
        
        # Priority-based selection
        if task_type == "coding" or "code" in context.lower():
            # Prefer coding models
            coding_models = []
            for provider_models in available_models.values():
                if isinstance(provider_models, list):
                    for model in provider_models:
                        if model.model_type == ModelType.CODING and model.is_available:
                            coding_models.append(model)
            
            if coding_models:
                return self._select_by_performance(coding_models)
        
        elif task_type == "creative" or "creative" in context.lower():
            # Prefer creative models
            creative_models = []
            for provider_models in available_models.values():
                if isinstance(provider_models, list):
                    for model in provider_models:
                        if model.model_type == ModelType.CREATIVE and model.is_available:
                            creative_models.append(model)
            
            if creative_models:
                return self._select_by_performance(creative_models)
        
        # Default to best available model
        all_models = []
        for provider_models in available_models.values():
            if isinstance(provider_models, list):
                for model in provider_models:
                    if model.is_available:
                        all_models.append(model)
        
        if not all_models:
            raise Exception("No LLM models available")
        
        return self._select_by_performance(all_models)
    
    def _select_by_performance(self, models: List[LLMModel]) -> LLMModel:
        """Select model based on performance metrics."""
        if not models:
            raise Exception("No models available for selection")
        
        # Sort by success rate and response time
        sorted_models = sorted(
            models,
            key=lambda m: (m.success_rate, -m.response_time),
            reverse=True
        )
        
        return sorted_models[0]
    
    async def generate_with_fallback(self, prompt: str, task_type: str = "general", 
                                   preferred_model: Optional[str] = None, **kwargs) -> str:
        """Generate text with automatic fallback."""
        try:
            # Try preferred model first if specified
            if preferred_model:
                try:
                    if preferred_model.startswith("cursor-"):
                        return await self.cursor_llms.generate(preferred_model, prompt, **kwargs)
                    else:
                        return await self.docker_ollama.generate(preferred_model, prompt, **kwargs)
                except Exception as e:
                    logger.warning(f"Preferred model {preferred_model} failed: {e}")
            
            # Select best available model
            selected_model = await self.select_best_model(task_type, prompt)
            
            # Try generation with selected model
            try:
                if selected_model.provider == LLMProvider.CURSOR:
                    result = await self.cursor_llms.generate(selected_model.name, prompt, **kwargs)
                else:
                    result = await self.docker_ollama.generate(selected_model.name, prompt, **kwargs)
                
                # Update performance metrics
                self._update_model_performance(selected_model.name, success=True)
                return result
                
            except Exception as e:
                logger.error(f"Selected model {selected_model.name} failed: {e}")
                self._update_model_performance(selected_model.name, success=False)
                
                # Try fallback to other available models
                return await self._try_fallback_generation(prompt, selected_model, **kwargs)
                
        except Exception as e:
            logger.error(f"All LLM generation attempts failed: {e}")
            raise Exception(f"LLM generation failed: {e}")
    
    async def _try_fallback_generation(self, prompt: str, failed_model: LLMModel, **kwargs) -> str:
        """Try generation with fallback models."""
        available_models = await self.get_available_models()
        
        # Get all models except the failed one
        fallback_models = [
            model for provider_models in available_models.values() 
            for model in provider_models 
            if model.name != failed_model.name and model.is_available
        ]
        
        if not fallback_models:
            raise Exception("No fallback models available")
        
        # Try each fallback model
        for model in fallback_models:
            try:
                if model.provider == LLMProvider.CURSOR:
                    result = await self.cursor_llms.generate(model.name, prompt, **kwargs)
                else:
                    result = await self.docker_ollama.generate(model.name, prompt, **kwargs)
                
                self._update_model_performance(model.name, success=True)
                logger.info(f"Fallback generation successful with {model.name}")
                return result
                
            except Exception as e:
                logger.warning(f"Fallback model {model.name} failed: {e}")
                self._update_model_performance(model.name, success=False)
                continue
        
        raise Exception("All fallback models failed")
    
    def _update_model_performance(self, model_name: str, success: bool):
        """Update model performance metrics."""
        if model_name not in self.model_performance:
            self.model_performance[model_name] = {"successes": 0, "failures": 0, "total_time": 0.0}
        
        if success:
            self.model_performance[model_name]["successes"] += 1
        else:
            self.model_performance[model_name]["failures"] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all models."""
        stats = {}
        for model_name, metrics in self.model_performance.items():
            total = metrics["successes"] + metrics["failures"]
            if total > 0:
                stats[model_name] = {
                    "success_rate": metrics["successes"] / total,
                    "total_requests": total,
                    "successes": metrics["successes"],
                    "failures": metrics["failures"]
                }
        return stats


# Global LLM Gateway instance
llm_gateway = LLMGateway()
