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

            # 🚀 CHECK FOR AUTOGEN DELEGATION FIRST
            if await self._should_delegate_to_autogen(message):
                logger.info(f"🎯 DELEGATING to AutoGen: {message}")
                return await self._delegate_to_autogen_agents(message)

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

    async def _should_delegate_to_autogen(self, message: str) -> bool:
        """Check if the message should be delegated to AutoGen agents."""
        delegation_keywords = [
            "delegate to",
            "let the agent",
            "agent work autonomously",
            "frontend agent",
            "backend agent",
            "react typescript",
            "work independently",
            "autonomous",
            "delegate",
        ]
        message_lower = message.lower()
        logger.info(f"🔍 Checking delegation for message: '{message}'")
        logger.info(f"🔍 Message lower: '{message_lower}'")

        for keyword in delegation_keywords:
            if keyword in message_lower:
                logger.info(
                    f"🎯 DELEGATION MATCH: Found keyword '{keyword}' in message"
                )
                return True

        logger.info(f"❌ No delegation keywords found in message")
        return False

    async def _delegate_to_autogen_agents(self, message: str) -> Dict[str, Any]:
        """Delegate message to AutoGen agents for autonomous work."""
        try:
            logger.info(f"🚀 Delegating to AutoGen: {message}")

            # Import AutoGen system
            from ...llm.enhanced_autogen import get_enhanced_autogen

            enhanced = get_enhanced_autogen()

            # Extract agent information from the message
            if "frontend" in message.lower():
                target_agent = "cursor_frontend_agent"
                task_type = "frontend_development"
            else:
                target_agent = "cursor_frontend_agent"  # Default for now
                task_type = "general_development"

            # Check if target agent exists
            if target_agent not in enhanced.agents:
                logger.error(f"Target agent {target_agent} not found")
                return {
                    "success": False,
                    "error": f"Agent {target_agent} not available",
                    "response": f"I couldn't find the {target_agent}. Let me handle this task instead.",
                }

            # Get the agents
            coordinator_agent = enhanced.agents.get("coordinator_agent")
            target_agent_obj = enhanced.agents[target_agent]

            if not coordinator_agent or not target_agent_obj:
                logger.error("Required AutoGen agents not available")
                return {
                    "success": False,
                    "error": "AutoGen agents not available",
                    "response": "The autonomous agents are not ready. Let me handle this task manually.",
                }

            # Check if AutoGen agents are properly initialized
            if not (coordinator_agent.autogen_agent and target_agent_obj.autogen_agent):
                logger.error("AutoGen agents not properly initialized")
                return {
                    "success": False,
                    "error": "AutoGen agents not initialized",
                    "response": "The agents are not fully set up. Let me work on this task directly.",
                }

            # Create task-specific prompt
            task_prompt = f"""
User Request: {message}

You are a {task_type} agent working autonomously.
Please:
1. Analyze the request thoroughly
2. Create a detailed implementation plan
3. Provide complete, working code solutions
4. Include proper documentation and best practices

Provide a comprehensive response with all necessary code and explanations.
"""

            logger.info(f"Initiating AutoGen conversation: {target_agent}")

            # Start AutoGen conversation (using Ollama fallback to avoid timeouts)
            coordinator_agent.autogen_agent.initiate_chat(
                target_agent_obj.autogen_agent,
                message=task_prompt,
                max_turns=2,  # Limit conversation length
            )

            # Extract the last response from the conversation
            if target_agent_obj.autogen_agent.chat_messages:
                last_messages = target_agent_obj.autogen_agent.chat_messages.get(
                    coordinator_agent.autogen_agent, []
                )
                if last_messages:
                    agent_response = last_messages[-1].get(
                        "content", "Task completed autonomously."
                    )
                else:
                    agent_response = "The autonomous agent completed the task."
            else:
                agent_response = "Task delegated to autonomous agent for completion."

            return {
                "success": True,
                "response": agent_response,
                "integration_type": "autogen_delegation",
                "delegated_to": target_agent,
                "task_type": task_type,
                "autonomous": True,
                "timestamp": "2025-09-11T14:55:00.000000",
            }

        except Exception as e:
            logger.error(f"AutoGen delegation failed: {e}")
            import traceback

            traceback.print_exc()
            return {
                "success": False,
                "error": f"Delegation failed: {str(e)}",
                "response": "I couldn't delegate to the autonomous agent. Let me handle this task directly instead.",
            }


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
