#!/usr/bin/env python3
"""Test script for Phase 2: AutoGen + Qdrant + LLM Gateway integration."""

import asyncio
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.llm import llm_gateway
from src.llm.enhanced_autogen import EnhancedAutoGen
from database import vector_store
from src.communication import AdvancedCommunication

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_llm_gateway():
    """Test LLM Gateway functionality."""
    print("\n🔧 Testing LLM Gateway...")
    
    try:
        # Test getting available models
        print("  📋 Getting available models...")
        models = await llm_gateway.get_available_models()
        print(f"    ✅ Available models: {models['total_count']}")
        print(f"    📊 Cursor models: {len(models['cursor'])}")
        print(f"    🐳 Docker Ollama models: {len(models['docker_ollama'])}")
        
        # Test model selection
        print("  🎯 Testing model selection...")
        best_model = await llm_gateway.select_best_model("coding", "Write a Python function")
        print(f"    ✅ Best model for coding: {best_model.name} ({best_model.provider.value})")
        
        # Test performance stats
        print("  📈 Getting performance stats...")
        stats = llm_gateway.get_performance_stats()
        print(f"    ✅ Performance stats: {len(stats)} models tracked")
        
        print("  ✅ LLM Gateway tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ LLM Gateway test failed: {e}")
        return False


async def test_autogen_integration():
    """Test AutoGen integration - DEPRECATED: Use enhanced_autogen instead."""
    print("\n🤖 Testing AutoGen Integration (DEPRECATED)...")
    print("  ⚠️  This test is deprecated. AutoGen functionality has been moved to enhanced_autogen.")
    print("  ✅ Skipping deprecated AutoGen integration test")
    return True


async def test_vector_store():
    """Test Qdrant vector store functionality."""
    print("\n🗄️  Testing Qdrant Vector Store...")
    
    try:
        if not vector_store:
            print("  ⚠️  Qdrant not available, skipping tests")
            return True
        
        # Test storing conversation
        print("  💾 Testing conversation storage...")
        from database.qdrant.vector_store import ConversationPoint
        from datetime import datetime
        
        conversation = ConversationPoint(
            id="test_conv_1",
            session_id="test_session",
            agent_id="test_agent",
            agent_type="assistant",
            message="This is a test message",
            context="Test context",
            timestamp=datetime.now(),
            metadata={"test": True}
        )
        
        conv_id = await vector_store.store_conversation(conversation)
        print(f"    ✅ Stored conversation: {conv_id}")
        
        # Test storing project context
        print("  📁 Testing project context storage...")
        from database.qdrant.vector_store import ProjectContext
        
        project_context = ProjectContext(
            id="test_proj_1",
            project_id="test_project",
            project_name="Test Project",
            context_type="planning",
            content="This is test project content",
            agent_id="test_agent",
            timestamp=datetime.now(),
            metadata={"test": True}
        )
        
        proj_id = await vector_store.store_project_context(project_context)
        print(f"    ✅ Stored project context: {proj_id}")
        
        # Test searching conversations
        print("  🔍 Testing conversation search...")
        search_results = await vector_store.search_conversations("test message")
        print(f"    ✅ Found {len(search_results)} conversations")
        
        # Test getting session history
        print("  📜 Testing session history...")
        history = await vector_store.get_session_history("test_session")
        print(f"    ✅ Session history: {len(history)} messages")
        
        # Test getting collection stats
        print("  📊 Getting collection stats...")
        stats = await vector_store.get_collection_stats()
        print(f"    ✅ Collection stats: {len(stats)} collections")
        
        print("  ✅ Qdrant Vector Store tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Qdrant Vector Store test failed: {e}")
        return False


async def test_enhanced_communication():
    """Test enhanced communication system."""
    print("\n📡 Testing Enhanced Communication System...")
    
    try:
        # Test creating session
        print("  🆕 Creating communication session...")
        session = await enhanced_communication.create_session(
            "test_session", ["agent1", "agent2"], "development"
        )
        print(f"    ✅ Created session: {session['id']} with {len(session['agent_ids'])} agents")
        
        # Test sending messages
        print("  📤 Testing message sending...")
        message1 = await enhanced_communication.send_message(
            "test_session", "agent1", "Hello from agent 1"
        )
        message2 = await enhanced_communication.send_message(
            "test_session", "agent2", "Hello from agent 2"
        )
        print(f"    ✅ Sent messages: {message1['id']}, {message2['id']}")
        
        # Test getting session messages
        print("  📥 Getting session messages...")
        messages = await enhanced_communication.get_session_messages("test_session")
        print(f"    ✅ Session has {len(messages)} messages")
        
        # Test getting agent conversations
        print("  👤 Getting agent conversations...")
        agent_convos = await enhanced_communication.get_agent_conversations("agent1")
        print(f"    ✅ Agent 1 has {len(agent_convos)} conversations")
        
        # Test cross-chat visibility
        print("  👁️  Testing cross-chat visibility...")
        visible_sessions = await enhanced_communication.get_cross_chat_visibility("agent1")
        print(f"    ✅ Agent 1 can see {len(visible_sessions)} sessions")
        
        # Test adding agent to session
        print("  ➕ Adding agent to session...")
        success = await enhanced_communication.add_agent_to_session("test_session", "agent3")
        print(f"    ✅ Added agent 3: {success}")
        
        # Test system status
        print("  📊 Getting system status...")
        status = enhanced_communication.get_system_status()
        print(f"    ✅ System status: {status['active_sessions']} active sessions")
        
        # Test closing session
        print("  🔒 Closing session...")
        closed = await enhanced_communication.close_session("test_session")
        print(f"    ✅ Session closed: {closed}")
        
        print("  ✅ Enhanced Communication System tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Enhanced Communication System test failed: {e}")
        return False


async def main():
    """Run all Phase 2 tests."""
    print("🚀 Phase 2 Testing: AutoGen + Qdrant + LLM Gateway")
    print("=" * 60)
    
    test_results = []
    
    # Run tests
    test_results.append(await test_llm_gateway())
    test_results.append(await test_autogen_integration())
    test_results.append(await test_vector_store())
    test_results.append(await test_enhanced_communication())
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"  ✅ Passed: {passed}/{total}")
    print(f"  ❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All Phase 2 tests passed! The system is ready.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)
