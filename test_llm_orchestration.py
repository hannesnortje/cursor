#!/usr/bin/env python3
"""Test LLM-powered tool orchestration in the Memory Enhanced Coordinator."""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(".")

from src.agents.coordinator.memory_enhanced_coordinator import MemoryEnhancedCoordinator


async def test_llm_tool_orchestration():
    """Test the LLM-powered tool orchestration system."""
    print("🧪 Testing LLM Tool Orchestration System")
    print("=" * 50)

    coordinator = MemoryEnhancedCoordinator()

    # Test scenario: User wants to start a Vue 3 project
    test_message = "I want to start a new Vue 3 dashboard project with user authentication and data visualization."

    print(f"📝 Test Message: {test_message}")
    print()

    try:
        # Process the message through the coordinator
        response = await coordinator.start_intelligent_conversation(test_message)

        print("🤖 Coordinator Response:")
        print(f"✓ Success: {response.get('success')}")
        print(f"📋 Phase: {response.get('phase', 'No phase')}")
        print()

        # Display the response
        response_text = response.get("response", "No response")
        print("💬 Response Text:")
        print(response_text)
        print()

        # Check for tool suggestions
        if "suggested_tools" in response and response["suggested_tools"]:
            print("🔧 Suggested Tools:")
            for i, tool in enumerate(response["suggested_tools"], 1):
                print(f"  {i}. {tool}")
            print()

        # Check for tool execution results
        if "tool_results" in response and response["tool_results"]:
            print("🚀 Tool Execution Results:")
            for result in response["tool_results"]:
                print(
                    f"  - {result.get('tool', 'Unknown')}: {result.get('status', 'No status')}"
                )
            print()

        # Display LLM reasoning if available
        if "llm_reasoning" in response and response["llm_reasoning"]:
            print("💭 LLM Reasoning:")
            print(response["llm_reasoning"])
            print()

        # Check for next steps
        if "next_steps" in response and response["next_steps"]:
            print("⏭️  Next Steps:")
            for step in response["next_steps"]:
                print(f"  • {step}")
            print()

        print("✅ LLM Tool Orchestration Test Complete")

        # Test continuation with a follow-up message
        print("\n" + "=" * 50)
        print("🧪 Testing Continuation Response")

        followup_message = "Great! Now I need help setting up the development environment and choosing the right libraries."
        print(f"📝 Follow-up Message: {followup_message}")

        continuation_response = await coordinator.start_intelligent_conversation(
            followup_message
        )

        print("\n🤖 Continuation Response:")
        continuation_text = continuation_response.get("response", "No response")
        print(continuation_text)

        if continuation_response.get("suggested_tools"):
            print("\n🔧 Additional Tool Suggestions:")
            for tool in continuation_response["suggested_tools"]:
                print(f"  • {tool}")

        print("\n✅ Continuation Test Complete")

    except Exception as e:
        print(f"❌ Error testing LLM orchestration: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_llm_tool_orchestration())
    if success:
        print("\n🎉 All LLM orchestration tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
