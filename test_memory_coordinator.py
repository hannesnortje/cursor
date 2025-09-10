"""Test the Memory-Enhanced Coordinator with Qdrant integration."""

import sys
import asyncio

sys.path.append(".")

from src.agents.coordinator.coordinator_integration import (
    initialize_memory_coordinator,
    process_user_message_with_memory,
    get_comprehensive_system_status,
)


async def test_memory_enhanced_coordinator():
    """Test the memory-enhanced coordinator functionality."""
    print("🧠 Testing Memory-Enhanced Coordinator with Qdrant Integration")
    print("=" * 60)

    # Initialize the coordinator
    print("🔧 Initializing Memory-Enhanced Coordinator...")
    success = await initialize_memory_coordinator()

    if not success:
        print("❌ Failed to initialize coordinator")
        return

    print("✅ Coordinator initialized successfully!")
    print()

    # Test system status
    print("📊 Getting System Status...")
    status = await get_comprehensive_system_status()

    if status.get("success"):
        print("✅ System Status:")
        integration_status = status.get("integration_status", {})
        vector_status = status.get("vector_store_status", {})
        memory_insights = status.get("memory_insights", {})

        print(
            f"   - Coordinator Ready: {integration_status.get('coordinator_ready', False)}"
        )
        print(f"   - Memory Enabled: {integration_status.get('memory_enabled', False)}")
        print(f"   - Qdrant Connected: {vector_status.get('qdrant_connected', False)}")
        print(
            f"   - Knowledge Domains: {len(memory_insights.get('knowledge_domains', []))}"
        )
        print()

    # Test intelligent conversation scenarios
    test_scenarios = [
        "I want to create a new Vue.js dashboard project for project management",
        "Please create the specialized agents for this project",
        "What are the best practices for agile development?",
        "How should we plan the sprint structure?",
    ]

    print("🤖 Testing Intelligent Conversations...")
    print("-" * 40)

    for i, message in enumerate(test_scenarios, 1):
        print(f"\n🗣️  Test {i}: {message}")
        print("📝 Coordinator Response:")

        response = await process_user_message_with_memory(message)

        if response.get("success"):
            print(f"✅ {response.get('response', 'No response')[:200]}...")

            # Show metadata
            integration = response.get("integration", {})
            print(
                f"📊 Memory: {integration.get('memory_enabled', False)}, "
                f"Qdrant: {integration.get('qdrant_connected', False)}, "
                f"Phase: {response.get('phase', 'unknown')}"
            )

            if response.get("memory_insights"):
                insights = response["memory_insights"]
                print(
                    f"🧠 Insights: {insights.get('similar_projects_count', 0)} similar projects, "
                    f"{insights.get('relevant_knowledge_count', 0)} knowledge items"
                )
        else:
            print(f"❌ Error: {response.get('error', 'Unknown error')}")

        print("-" * 40)

    print("\n🎉 Memory-Enhanced Coordinator test completed!")
    print("The coordinator is now ready for intelligent project management!")


if __name__ == "__main__":
    asyncio.run(test_memory_enhanced_coordinator())
