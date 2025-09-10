"""Integration module for Fast and Memory-Enhanced Coordinators with MCP Server."""

import logging
import asyncio
from typing import Dict, Any, Optional

from .memory_enhanced_coordinator import (
    MemoryEnhancedCoordinator,
    get_memory_enhanced_coordinator,
)
from .fast_coordinator import FastCoordinator
from ...database.enhanced_vector_store import get_enhanced_vector_store
from ...llm.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


class CoordinatorIntegration:
    """Integration layer for Fast and Memory-Enhanced Coordinators with MCP Server."""

    def __init__(self, use_fast_coordinator: bool = True):
        """Initialize the integration.

        Args:
            use_fast_coordinator: Whether to use the fast rule-based coordinator (default: True)
        """
        self.use_fast_coordinator = use_fast_coordinator
        self.fast_coordinator: Optional[FastCoordinator] = None
        self.memory_coordinator: Optional[MemoryEnhancedCoordinator] = None
        self.initialized = False

    async def initialize(self) -> bool:
        """Initialize the coordinator integration."""
        try:
            if self.use_fast_coordinator:
                # Initialize fast coordinator
                vector_store = get_enhanced_vector_store()
                self.fast_coordinator = FastCoordinator(
                    vector_store=vector_store, llm_gateway=llm_gateway
                )
                logger.info("Fast Coordinator initialized successfully")
            else:
                # Initialize memory-enhanced coordinator (legacy)
                self.memory_coordinator = get_memory_enhanced_coordinator()
                success = await self.memory_coordinator.initialize()
                if not success:
                    logger.error("Failed to initialize memory-enhanced coordinator")
                    return False
                logger.info("Memory-Enhanced Coordinator initialized successfully")

            self.initialized = True
            return True

        except Exception as e:
            logger.error(f"Coordinator integration failed: {e}")
            return False

    async def process_user_message(self, message: str) -> Dict[str, Any]:
        """Process user message through the appropriate coordinator."""
        try:
            if not self.initialized:
                return {
                    "success": False,
                    "error": "Coordinator not initialized",
                    "response": "I'm not ready yet. Please try again in a moment.",
                }

            if self.use_fast_coordinator and self.fast_coordinator:
                # Use fast coordinator (< 2s response time)
                return await self.fast_coordinator.process_message_fast(message)
            elif self.memory_coordinator:
                # Use memory-enhanced coordinator (legacy, slower)
                response = await self.memory_coordinator.start_intelligent_conversation(
                    message
                )

                # Add integration metadata
                response["integration"] = {
                    "coordinator_type": "memory_enhanced",
                    "memory_enabled": True,
                    "qdrant_connected": not self.memory_coordinator.vector_store.fallback_mode,
                    "session_id": self.memory_coordinator.current_session_id,
                }

                return response
            else:
                return {
                    "success": False,
                    "error": "No coordinator available",
                    "response": "No coordinator is currently available.",
                }

        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your message. Let me try again.",
            }

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            if not self.initialized:
                return {"success": False, "error": "Coordinator not initialized"}

            if self.use_fast_coordinator:
                # Fast coordinator status
                vector_store = get_enhanced_vector_store()
                return {
                    "success": True,
                    "coordinator_type": "fast_rule_based",
                    "coordinator_status": {
                        "type": "fast",
                        "llm_polish_enabled": (
                            self.fast_coordinator.enable_llm_polish
                            if self.fast_coordinator
                            else False
                        ),
                        "performance_target": "<2s response time",
                    },
                    "vector_store": {
                        "qdrant_connected": not vector_store.fallback_mode,
                        "fallback_mode": vector_store.fallback_mode,
                        "current_project": vector_store.current_project_id,
                    },
                    "llm_gateway": {
                        "available": llm_gateway is not None,
                        "local_llm_enabled": True,
                    },
                }
            else:
                # Memory-enhanced coordinator status (legacy)
                coordinator_status = await self.memory_coordinator.get_system_status()
                memory_insights = await self.memory_coordinator.get_memory_insights()

                vector_store = get_enhanced_vector_store()
                vector_status = {
                    "qdrant_connected": not vector_store.fallback_mode,
                    "fallback_mode": vector_store.fallback_mode,
                    "current_project": vector_store.current_project_id,
                }

                return {
                    "success": True,
                    "coordinator_type": "memory_enhanced",
                    "coordinator_status": coordinator_status,
                    "memory_insights": memory_insights,
                    "vector_store": vector_status,
                }

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"success": False, "error": str(e)}


# Global instances for both coordinators
_fast_coordinator_integration = None
_memory_coordinator_integration = None


def get_coordinator_integration(use_fast: bool = True) -> CoordinatorIntegration:
    """Get the global coordinator integration instance."""
    global _fast_coordinator_integration, _memory_coordinator_integration

    if use_fast:
        if _fast_coordinator_integration is None:
            _fast_coordinator_integration = CoordinatorIntegration(
                use_fast_coordinator=True
            )
        return _fast_coordinator_integration
    else:
        if _memory_coordinator_integration is None:
            _memory_coordinator_integration = CoordinatorIntegration(
                use_fast_coordinator=False
            )
        return _memory_coordinator_integration


# Convenience functions for backward compatibility and easy access


async def process_user_message_with_memory(
    message: str, use_fast: bool = True
) -> Dict[str, Any]:
    """Process user message with the specified coordinator type.

    Args:
        message: User message to process
        use_fast: Whether to use fast coordinator (True) or memory-enhanced (False)
    """
    try:
        integration = get_coordinator_integration(use_fast=use_fast)

        if not integration.initialized:
            await integration.initialize()

        return await integration.process_user_message(message)

    except Exception as e:
        logger.error(f"Error in process_user_message_with_memory: {e}")
        return {
            "success": False,
            "error": str(e),
            "response": "I encountered an error while processing your request.",
        }


async def get_comprehensive_system_status(use_fast: bool = True) -> Dict[str, Any]:
    """Get comprehensive system status from the specified coordinator.

    Args:
        use_fast: Whether to use fast coordinator (True) or memory-enhanced (False)
    """
    try:
        integration = get_coordinator_integration(use_fast=use_fast)

        if not integration.initialized:
            await integration.initialize()

        return await integration.get_system_status()

    except Exception as e:
        logger.error(f"Error in get_comprehensive_system_status: {e}")
        return {"success": False, "error": str(e)}
