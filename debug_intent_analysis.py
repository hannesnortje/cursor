#!/usr/bin/env python3
"""Debug intent analysis in the Memory Enhanced Coordinator."""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(".")

from src.agents.coordinator.memory_enhanced_coordinator import MemoryEnhancedCoordinator
from src.agents.coordinator.memory_enhanced_coordinator import MemoryContext


async def test_intent_analysis():
    """Test intent analysis with various messages."""
    print("🔍 Testing Intent Analysis System")
    print("=" * 50)

    coordinator = MemoryEnhancedCoordinator()

    test_messages = [
        "I want to start a new Vue 3 dashboard project with user authentication",
        "I want to create a new project for data visualization",
        "start project with Vue 3 and authentication",
        "create project using modern web technologies",
        "I need to build a new web application project",
        "develop project for dashboard creation",
    ]

    # Create empty memory context for testing
    memory_context = MemoryContext(
        similar_projects=[],
        relevant_knowledge=[],
        agent_experiences=[],
        success_patterns=[],
        lessons_learned=[],
        risk_patterns=[],
    )

    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Testing: '{message}'")

        try:
            intent_analysis = await coordinator._analyze_user_intent(
                message, memory_context
            )

            print(f"   Intent: {intent_analysis.get('intent', 'Unknown')}")
            print(f"   Confidence: {intent_analysis.get('confidence', 'N/A')}")

            if intent_analysis.get("project_type"):
                print(f"   Project Type: {intent_analysis.get('project_type')}")

            if intent_analysis.get("suggested_approach"):
                print(
                    f"   Suggested Approach: {intent_analysis.get('suggested_approach')}"
                )

        except Exception as e:
            print(f"   ❌ Error: {e}")

    print("\n" + "=" * 50)
    print("🧪 Testing LLM Tool Orchestration Trigger")

    # Test a message that should trigger create_project
    test_project_message = "create project with Vue 3 dashboard"
    print(f"\nTesting: '{test_project_message}'")

    try:
        response = await coordinator.start_intelligent_conversation(
            test_project_message
        )

        print(f"Phase: {response.get('phase')}")
        print(f"Response includes tool suggestions: {'suggested_tools' in response}")
        print(f"Response includes LLM reasoning: {'llm_reasoning' in response}")

        if response.get("suggested_tools"):
            print(f"Suggested tools: {response['suggested_tools']}")

    except Exception as e:
        print(f"❌ Error in full test: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_intent_analysis())
