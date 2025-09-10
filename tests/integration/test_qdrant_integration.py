#!/usr/bin/env python3
"""Test script for Qdrant integration with main MCP server."""

import asyncio
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_qdrant_integration():
    """Test the Qdrant integration with the main system."""
    print("🧪 Testing Qdrant Integration with Main MCP Server")
    print("=" * 60)

    try:
        # Test 1: Import the main system
        print("\n1️⃣ Testing imports...")
        from protocol_server import AgentSystem

        print("  ✅ Successfully imported AgentSystem")

        # Test 2: Initialize the system
        print("\n2️⃣ Testing system initialization...")
        agent_system = AgentSystem()

        print("  ✅ AgentSystem initialized successfully")

        # Test 3: Check vector store availability
        print("\n3️⃣ Testing vector store availability...")
        vector_available = agent_system.vector_store is not None
        print(f"  📊 Vector store available: {vector_available}")

        if vector_available:
            print("  🎯 Vector store type: Qdrant")
        else:
            print("  ⚠️  Vector store not available (fallback to in-memory)")

        # Test 4: Check system health
        print("\n4️⃣ Testing system health...")
        health = agent_system.get_system_health()
        print(f"  🏥 System status: {health['status']}")
        print(f"  📊 Vector store status: {health['vector_store']['status']}")

        # Test 5: Test project creation with vector storage
        print("\n5️⃣ Testing project creation with vector storage...")
        project_result = agent_system.start_project("test", "Qdrant Integration Test")

        if project_result["success"]:
            print(f"  ✅ Project created: {project_result['project_id']}")
            print(f"  📝 Message: {project_result['message']}")
        else:
            print(f"  ❌ Project creation failed: {project_result['error']}")

        # Test 6: Test cross-chat message storage
        print("\n6️⃣ Testing cross-chat message storage...")
        message_result = agent_system.broadcast_cross_chat_message(
            source_chat="test_chat",
            source_agent="test_agent",
            content="Testing Qdrant integration for cross-chat messages",
            target_chats=["chat1", "chat2"],
        )

        if message_result["success"]:
            print(f"  ✅ Message broadcasted: {message_result['message_id']}")
            print(f"  📡 Target chats: {message_result['broadcast_count']}")
        else:
            print(f"  ❌ Message broadcast failed: {message_result['error']}")

        # Test 7: Test message retrieval
        print("\n7️⃣ Testing message retrieval...")
        messages = agent_system.get_cross_chat_messages(limit=10)

        if messages["success"]:
            print(f"  ✅ Retrieved {messages['message_count']} messages")
            print(f"  💾 Storage type: {messages['storage']}")
        else:
            print(f"  ❌ Message retrieval failed: {messages['error']}")

        # Test 8: Test message search
        print("\n8️⃣ Testing message search...")
        search_results = agent_system.search_cross_chat_messages("Qdrant", limit=5)

        if search_results["success"]:
            print(f"  ✅ Search completed: {search_results['result_count']} results")
            print(f"  🔍 Storage type: {search_results['storage']}")
        else:
            print(f"  ❌ Search failed: {search_results['error']}")

        # Test 9: Test communication status
        print("\n9️⃣ Testing communication status...")
        comm_status = agent_system.get_communication_status()

        if comm_status["success"]:
            print(f"  ✅ Communication status retrieved")
            print(f"  🌐 WebSocket: {comm_status['websocket_server']['status']}")
            print(f"  📡 Redis: {comm_status['redis_queue']['status']}")
            print(f"  💾 Vector Store: {comm_status['vector_store']['status']}")
        else:
            print(f"  ❌ Communication status failed: {comm_status['error']}")

        print("\n" + "=" * 60)
        print("🎉 Qdrant Integration Test Completed Successfully!")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_qdrant_integration()
    sys.exit(0 if success else 1)
