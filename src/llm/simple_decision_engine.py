"""
Simple Decision Engine with LLM fallback.

This provides a working decision engine that can fall back to rule-based decisions
when LLM is not available or too slow.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# Try to import Cursor LLM tools
try:
    from mcp_tools.cursor_llm import generate_with_cursor_llm
    CURSOR_LLM_AVAILABLE = True
except ImportError:
    CURSOR_LLM_AVAILABLE = False
    logging.warning("Cursor LLM not available - will use rule-based fallback")


class ActionType(Enum):
    """Available protocol actions."""
    ASK_QUESTIONS = "ask_questions"
    PROVIDE_RECOMMENDATIONS = "provide_recommendations"
    CREATE_AGENTS = "create_agents"
    CONTINUE_PLANNING = "continue_planning"
    START_IMPLEMENTATION = "start_implementation"
    CLARIFY_REQUIREMENTS = "clarify_requirements"
    TECHNOLOGY_SELECTION = "technology_selection"


class PDCAPhase(Enum):
    """PDCA framework phases."""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


@dataclass
class ProtocolDecision:
    """Structured decision from the decision engine."""
    action_type: ActionType
    confidence: float  # 0.0 to 1.0
    reasoning: str
    next_phase: PDCAPhase
    parameters: Dict[str, Any]
    technology_preferences: Optional[List[str]] = None
    agent_types_needed: Optional[List[str]] = None


@dataclass
class ConversationState:
    """Tracks conversation state and context."""
    current_phase: PDCAPhase = PDCAPhase.PLAN
    project_details: Dict[str, Any] = None
    answered_questions: List[str] = None
    user_preferences: Dict[str, Any] = None
    technology_stack: Optional[List[str]] = None
    created_agents: List[str] = None
    conversation_history: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.project_details is None:
            self.project_details = {}
        if self.answered_questions is None:
            self.answered_questions = []
        if self.user_preferences is None:
            self.user_preferences = {}
        if self.created_agents is None:
            self.created_agents = []
        if self.conversation_history is None:
            self.conversation_history = []


class SimpleDecisionEngine:
    """Simple decision engine with LLM fallback and rule-based decisions."""
    
    def __init__(self, local_llm_url: str = "http://localhost:11434", 
                 model_name: str = "llama3.1:8b"):
        """Initialize the decision engine."""
        self.local_llm_url = local_llm_url
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.conversation_state = ConversationState()
        
        # Test local LLM availability
        self.local_llm_available = self._test_local_llm()
        
        self.logger.info(f"Simple Decision Engine initialized:")
        self.logger.info(f"  - Local LLM: {'✅ Available' if self.local_llm_available else '❌ Unavailable'}")
        self.logger.info(f"  - Cursor LLM: {'✅ Available' if CURSOR_LLM_AVAILABLE else '❌ Unavailable'}")
        self.logger.info(f"  - Rule-based fallback: ✅ Available")
    
    def _test_local_llm(self) -> bool:
        """Test if local LLM is available with a quick test."""
        try:
            response = requests.post(
                f"{self.local_llm_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": "Test",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 5
                    }
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"Local LLM test failed: {e}")
            return False
    
    def _rule_based_decision(self, message: str) -> Optional[ProtocolDecision]:
        """Make a rule-based decision as fallback."""
        message_lower = message.lower()
        
        # Check for agent creation requests
        if any(phrase in message_lower for phrase in [
            "create agents", "let's create", "please create", "specialized agents", 
            "agent team", "create the", "create an agile", "create a frontend", 
            "create a backend", "create a testing", "i'd like to create", 
            "create the core agents", "create core agents", "set up agents", 
            "create specialized", "create the agents"
        ]):
            return ProtocolDecision(
                action_type=ActionType.CREATE_AGENTS,
                confidence=0.9,
                reasoning="User explicitly requested agent creation",
                next_phase=PDCAPhase.DO,
                parameters={},
                agent_types_needed=["agile", "frontend", "backend", "testing"]
            )
        
        # Check for technology recommendations requests (but not initial project requests)
        if any(phrase in message_lower for phrase in [
            "technology stack", "architecture", "tech stack", "recommendations",
            "what would you recommend", "technology recommendations"
        ]) and not any(phrase in message_lower for phrase in [
            "start a new project", "business need", "not sure exactly what technology"
        ]):
            # Extract technology preferences
            tech_prefs = []
            if "vue" in message_lower:
                tech_prefs.append("Vue 3")
            if "react" in message_lower:
                tech_prefs.append("React")
            if "angular" in message_lower:
                tech_prefs.append("Angular")
            if "typescript" in message_lower:
                tech_prefs.append("TypeScript")
            
            return ProtocolDecision(
                action_type=ActionType.PROVIDE_RECOMMENDATIONS,
                confidence=0.8,
                reasoning="User requested technology recommendations",
                next_phase=PDCAPhase.PLAN,
                parameters={},
                technology_preferences=tech_prefs
            )
        
        # Check for comprehensive project details
        has_project_goals = any(phrase in message_lower for phrase in [
            "project goals", "main purpose", "project management system"
        ])
        has_objectives = any(phrase in message_lower for phrase in [
            "objectives", "target users", "development team"
        ])
        has_tech_requirements = any(phrase in message_lower for phrase in [
            "technical requirements", "team expertise", "authentication"
        ])
        
        if has_project_goals and has_objectives and has_tech_requirements:
            return ProtocolDecision(
                action_type=ActionType.PROVIDE_RECOMMENDATIONS,
                confidence=0.7,
                reasoning="User provided comprehensive project details",
                next_phase=PDCAPhase.PLAN,
                parameters={},
                technology_preferences=[]
            )
        
        # Check for initial project requests
        if any(phrase in message_lower for phrase in [
            "start a new project", "business need", "software solution",
            "not sure exactly what technology", "help me figure out"
        ]):
            return ProtocolDecision(
                action_type=ActionType.ASK_QUESTIONS,
                confidence=0.8,
                reasoning="User is starting a new project and needs guidance",
                next_phase=PDCAPhase.PLAN,
                parameters={}
            )
        
        # Default to asking questions
        return ProtocolDecision(
            action_type=ActionType.ASK_QUESTIONS,
            confidence=0.5,
            reasoning="Default fallback - asking for more information",
            next_phase=PDCAPhase.PLAN,
            parameters={}
        )
    
    def _call_local_llm(self, message: str) -> Optional[ProtocolDecision]:
        """Call the local LLM with a simple prompt."""
        try:
            # Simple prompt for faster response
            prompt = f"""Analyze this message and determine the action:

Message: {message}

Actions: ask_questions, provide_recommendations, create_agents, technology_selection

Respond with just the action name:"""
            
            response = requests.post(
                f"{self.local_llm_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 20
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                action_text = result.get("response", "").strip().lower()
                
                # Map to action type
                action_mapping = {
                    "ask_questions": ActionType.ASK_QUESTIONS,
                    "provide_recommendations": ActionType.PROVIDE_RECOMMENDATIONS,
                    "create_agents": ActionType.CREATE_AGENTS,
                    "technology_selection": ActionType.TECHNOLOGY_SELECTION
                }
                
                action_type = action_mapping.get(action_text, ActionType.ASK_QUESTIONS)
                
                return ProtocolDecision(
                    action_type=action_type,
                    confidence=0.7,
                    reasoning=f"LLM determined: {action_text}",
                    next_phase=PDCAPhase.PLAN,
                    parameters={}
                )
            else:
                self.logger.error(f"Local LLM error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Local LLM call failed: {e}")
            return None
    
    def make_decision(self, message: str) -> Optional[ProtocolDecision]:
        """Make a protocol decision based on user message."""
        # Try local LLM first if available
        if self.local_llm_available:
            self.logger.info("Attempting local LLM decision")
            decision = self._call_local_llm(message)
            if decision:
                return decision
        
        # Fallback to rule-based decision
        self.logger.info("Using rule-based fallback decision")
        return self._rule_based_decision(message)
    
    def update_conversation_state(self, message: str, decision: ProtocolDecision, 
                                response: str = None) -> None:
        """Update conversation state based on message and decision."""
        # Add to conversation history
        self.conversation_state.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user": message,
            "assistant": response or "",
            "action": decision.action_type.value
        })
        
        # Update current phase
        self.conversation_state.current_phase = decision.next_phase
        
        # Update project details if provided
        if decision.parameters.get("project_details"):
            self.conversation_state.project_details.update(decision.parameters["project_details"])
        
        # Update technology preferences
        if decision.technology_preferences:
            self.conversation_state.technology_stack = decision.technology_preferences
        
        # Update created agents
        if decision.agent_types_needed:
            self.conversation_state.created_agents.extend(decision.agent_types_needed)
        
        self.logger.info(f"Conversation state updated - Phase: {self.conversation_state.current_phase.value}")
    
    def get_conversation_state(self) -> ConversationState:
        """Get current conversation state."""
        return self.conversation_state
    
    def reset_conversation_state(self) -> None:
        """Reset conversation state for new project."""
        self.conversation_state = ConversationState()
        self.logger.info("Conversation state reset")


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create decision engine
    engine = SimpleDecisionEngine()
    
    # Test with sample message
    test_message = "I want to start a new project. I have a business need that requires a software solution, but I'm not sure exactly what technology stack or approach would be best. Can you help me figure out what we need to build and how to approach it? I'd like to use your PDCA framework to make sure we plan this properly before we start development. What information do you need from me to get started?"
    
    print("Testing Simple Decision Engine...")
    print(f"Message: {test_message[:100]}...")
    
    decision = engine.make_decision(test_message)
    
    if decision:
        print(f"\nDecision: {decision.action_type.value}")
        print(f"Confidence: {decision.confidence}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Next Phase: {decision.next_phase.value}")
        print(f"Parameters: {decision.parameters}")
    else:
        print("Failed to make decision")
