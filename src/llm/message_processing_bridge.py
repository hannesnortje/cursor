"""
Message Processing Bridge for AutoGen-Cursor Integration

This module provides sophisticated message processing capabilities for bridging
between AutoGen's message format and Cursor's LLM system, including context
management, conversation history, and advanced formatting.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"
    TOOL = "tool"


class ConversationRole(Enum):
    """Roles in AutoGen conversations."""
    COORDINATOR = "coordinator"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    USER = "user"


@dataclass
class ProcessedMessage:
    """A processed message ready for Cursor LLM."""
    content: str
    role: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime


@dataclass
class ConversationContext:
    """Context for the conversation."""
    session_id: str
    agent_role: ConversationRole
    task_type: str
    conversation_history: List[ProcessedMessage]
    project_context: Optional[Dict[str, Any]] = None
    code_context: Optional[Dict[str, Any]] = None


class MessageProcessingBridge:
    """
    Advanced message processing bridge for AutoGen-Cursor integration.
    
    This class handles:
    1. Converting AutoGen messages to Cursor-optimized format
    2. Managing conversation context and history
    3. Enhancing messages with relevant context
    4. Processing responses from Cursor LLMs
    5. Maintaining conversation state across interactions
    """
    
    def __init__(self):
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.message_enhancers = {
            "coding": self._enhance_coding_message,
            "review": self._enhance_review_message,
            "testing": self._enhance_testing_message,
            "general": self._enhance_general_message,
        }
        
    async def process_autogen_messages(
        self,
        messages: List[Dict[str, str]],
        agent_role: str = "developer",
        task_type: str = "general",
        session_id: Optional[str] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, ConversationContext]:
        """
        Process AutoGen messages for Cursor LLM consumption.
        
        Args:
            messages: AutoGen message list
            agent_role: Role of the agent processing messages
            task_type: Type of task (coding, review, testing, general)
            session_id: Optional session identifier
            project_context: Optional project context information
            
        Returns:
            Tuple of (processed_prompt, conversation_context)
        """
        
        # Create or retrieve conversation context
        if not session_id:
            session_id = self._generate_session_id()
        
        if session_id not in self.active_conversations:
            self.active_conversations[session_id] = ConversationContext(
                session_id=session_id,
                agent_role=ConversationRole(agent_role) if isinstance(agent_role, str) else agent_role,
                task_type=task_type,
                conversation_history=[],
                project_context=project_context
            )
        
        context = self.active_conversations[session_id]
        
        # Process each message
        processed_messages = []
        for msg in messages:
            processed_msg = await self._process_single_message(
                msg, context, task_type
            )
            processed_messages.append(processed_msg)
            context.conversation_history.append(processed_msg)
        
        # Generate final prompt for Cursor LLM
        cursor_prompt = await self._generate_cursor_prompt(
            processed_messages, context
        )
        
        logger.info(f"Processed {len(messages)} messages for Cursor LLM (session: {session_id})")
        return cursor_prompt, context
    
    async def _process_single_message(
        self,
        message: Dict[str, str],
        context: ConversationContext,
        task_type: str
    ) -> ProcessedMessage:
        """Process a single message with context enhancement."""
        
        role = message.get("role", "user")
        content = message.get("content", "")
        
        # Enhance message based on task type
        if task_type in self.message_enhancers:
            enhanced_content = await self.message_enhancers[task_type](
                content, context
            )
        else:
            enhanced_content = content
        
        # Add metadata
        metadata = {
            "original_role": role,
            "task_type": task_type,
            "agent_role": context.agent_role.value,
            "session_id": context.session_id,
            "message_length": len(content),
            "enhanced": enhanced_content != content
        }
        
        return ProcessedMessage(
            content=enhanced_content,
            role=role,
            context={"task_type": task_type, "agent_role": context.agent_role.value},
            metadata=metadata,
            timestamp=datetime.now()
        )
    
    async def _enhance_coding_message(
        self,
        content: str,
        context: ConversationContext
    ) -> str:
        """Enhance coding-related messages with additional context."""
        
        enhancements = []
        
        # Add agent role context
        if context.agent_role == ConversationRole.DEVELOPER:
            enhancements.append("As an expert developer assistant")
        elif context.agent_role == ConversationRole.REVIEWER:
            enhancements.append("As a thorough code reviewer")
        
        # Add project context if available
        if context.project_context:
            tech_stack = context.project_context.get("tech_stack", [])
            if tech_stack:
                enhancements.append(f"Working with: {', '.join(tech_stack)}")
        
        # Add conversation context
        recent_topics = self._extract_recent_topics(context.conversation_history)
        if recent_topics:
            enhancements.append(f"Context: {', '.join(recent_topics)}")
        
        if enhancements:
            enhancement_text = " | ".join(enhancements)
            return f"[{enhancement_text}]\n\n{content}"
        
        return content
    
    async def _enhance_review_message(
        self,
        content: str,
        context: ConversationContext
    ) -> str:
        """Enhance code review messages."""
        
        enhancements = []
        
        if context.agent_role == ConversationRole.REVIEWER:
            enhancements.append("Code Review Focus: security, performance, maintainability")
        
        # Check for code patterns in content
        if "def " in content or "function " in content or "class " in content:
            enhancements.append("Code analysis requested")
        
        if enhancements:
            enhancement_text = " | ".join(enhancements)
            return f"[{enhancement_text}]\n\n{content}"
        
        return content
    
    async def _enhance_testing_message(
        self,
        content: str,
        context: ConversationContext
    ) -> str:
        """Enhance testing-related messages."""
        
        enhancements = []
        
        if context.agent_role == ConversationRole.TESTER:
            enhancements.append("Testing focus: coverage, edge cases, integration")
        
        # Detect testing keywords
        testing_keywords = ["test", "spec", "assert", "expect", "mock"]
        if any(keyword in content.lower() for keyword in testing_keywords):
            enhancements.append("Test development context")
        
        if enhancements:
            enhancement_text = " | ".join(enhancements)
            return f"[{enhancement_text}]\n\n{content}"
        
        return content
    
    async def _enhance_general_message(
        self,
        content: str,
        context: ConversationContext
    ) -> str:
        """Enhance general messages."""
        
        # For general messages, just add basic agent context
        if context.agent_role != ConversationRole.USER:
            return f"[Agent: {context.agent_role.value}]\n\n{content}"
        
        return content
    
    def _extract_recent_topics(
        self,
        history: List[ProcessedMessage],
        window_size: int = 3
    ) -> List[str]:
        """Extract recent conversation topics."""
        
        if not history:
            return []
        
        recent_messages = history[-window_size:]
        topics = []
        
        for msg in recent_messages:
            # Simple keyword extraction
            content_lower = msg.content.lower()
            
            # Common programming topics
            if any(keyword in content_lower for keyword in ["function", "class", "method"]):
                topics.append("code structure")
            if any(keyword in content_lower for keyword in ["bug", "error", "exception"]):
                topics.append("debugging")
            if any(keyword in content_lower for keyword in ["test", "testing"]):
                topics.append("testing")
            if any(keyword in content_lower for keyword in ["api", "endpoint"]):
                topics.append("API development")
        
        return list(set(topics))  # Remove duplicates
    
    async def _generate_cursor_prompt(
        self,
        messages: List[ProcessedMessage],
        context: ConversationContext
    ) -> str:
        """Generate optimized prompt for Cursor LLM."""
        
        prompt_parts = []
        
        # Add system context
        system_context = self._build_system_context(context)
        if system_context:
            prompt_parts.append(f"System Context: {system_context}")
        
        # Add conversation messages
        for msg in messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
            else:
                prompt_parts.append(f"{msg.role.title()}: {msg.content}")
        
        # Add context-specific instructions
        context_instructions = self._get_context_instructions(context)
        if context_instructions:
            prompt_parts.append(f"\nInstructions: {context_instructions}")
        
        return "\n\n".join(prompt_parts)
    
    def _build_system_context(self, context: ConversationContext) -> str:
        """Build system context string."""
        
        context_parts = []
        
        # Agent role
        context_parts.append(f"Agent Role: {context.agent_role.value}")
        
        # Task type
        context_parts.append(f"Task: {context.task_type}")
        
        # Project context
        if context.project_context:
            tech_stack = context.project_context.get("tech_stack")
            if tech_stack:
                context_parts.append(f"Tech Stack: {', '.join(tech_stack)}")
        
        return " | ".join(context_parts)
    
    def _get_context_instructions(self, context: ConversationContext) -> str:
        """Get context-specific instructions for the LLM."""
        
        instructions = []
        
        # Role-specific instructions
        if context.agent_role == ConversationRole.DEVELOPER:
            instructions.append("Provide practical, implementable code solutions")
        elif context.agent_role == ConversationRole.REVIEWER:
            instructions.append("Focus on code quality, security, and best practices")
        elif context.agent_role == ConversationRole.TESTER:
            instructions.append("Emphasize comprehensive testing strategies")
        
        # Task-specific instructions
        if context.task_type == "coding":
            instructions.append("Include working code examples when relevant")
        elif context.task_type == "review":
            instructions.append("Provide specific, actionable feedback")
        
        return "; ".join(instructions)
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import uuid
        return f"session-{uuid.uuid4().hex[:8]}"
    
    async def process_cursor_response(
        self,
        response: str,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Process response from Cursor LLM back to AutoGen format.
        
        Args:
            response: Raw response from Cursor LLM
            context: Conversation context
            
        Returns:
            Processed response with metadata
        """
        
        # Clean up response
        cleaned_response = self._clean_cursor_response(response)
        
        # Extract any structured information
        extracted_info = self._extract_response_info(cleaned_response)
        
        # Add to conversation history
        response_message = ProcessedMessage(
            content=cleaned_response,
            role="assistant",
            context={"agent_role": context.agent_role.value},
            metadata={
                "response_length": len(cleaned_response),
                "extracted_info": extracted_info,
                "session_id": context.session_id
            },
            timestamp=datetime.now()
        )
        
        context.conversation_history.append(response_message)
        
        return {
            "content": cleaned_response,
            "metadata": response_message.metadata,
            "extracted_info": extracted_info,
            "session_id": context.session_id
        }
    
    def _clean_cursor_response(self, response: str) -> str:
        """Clean up Cursor LLM response."""
        
        # Remove any cursor-specific markers
        cleaned = response.replace("[CURSOR LLM]", "").replace("[REAL CURSOR LLM RESPONSE]", "")
        
        # Clean up extra whitespace
        cleaned = "\n".join(line.strip() for line in cleaned.split("\n") if line.strip())
        
        return cleaned.strip()
    
    def _extract_response_info(self, response: str) -> Dict[str, Any]:
        """Extract structured information from response."""
        
        info = {
            "contains_code": bool("```" in response or "def " in response or "function " in response),
            "contains_error": bool("error" in response.lower() or "exception" in response.lower()),
            "contains_question": bool("?" in response),
            "word_count": len(response.split()),
            "code_blocks": response.count("```") // 2
        }
        
        return info
    
    def get_conversation_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get summary of conversation."""
        
        if session_id not in self.active_conversations:
            return None
        
        context = self.active_conversations[session_id]
        
        return {
            "session_id": session_id,
            "agent_role": context.agent_role.value,
            "task_type": context.task_type,
            "message_count": len(context.conversation_history),
            "start_time": context.conversation_history[0].timestamp if context.conversation_history else None,
            "last_activity": context.conversation_history[-1].timestamp if context.conversation_history else None,
            "topics_discussed": self._extract_recent_topics(context.conversation_history, len(context.conversation_history))
        }


# Example usage
async def test_message_bridge():
    """Test the message processing bridge."""
    
    bridge = MessageProcessingBridge()
    
    # Test messages
    test_messages = [
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Help me write a Python function to calculate fibonacci numbers."},
    ]
    
    # Process messages
    print("Processing AutoGen messages...")
    prompt, context = await bridge.process_autogen_messages(
        messages=test_messages,
        agent_role="developer",
        task_type="coding",
        project_context={"tech_stack": ["python", "pytest"]}
    )
    
    print(f"Generated prompt:\n{prompt}")
    
    # Simulate Cursor response
    cursor_response = "Here's a Python function for fibonacci calculation:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```"
    
    # Process response
    processed_response = await bridge.process_cursor_response(cursor_response, context)
    print(f"\nProcessed response: {processed_response}")
    
    # Get conversation summary
    summary = bridge.get_conversation_summary(context.session_id)
    print(f"\nConversation summary: {summary}")


if __name__ == "__main__":
    asyncio.run(test_message_bridge())
