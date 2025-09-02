"""Tests for Phase 2 infrastructure components."""

import asyncio
import sys
from datetime import datetime


async def test_database_manager():
    """Test the Qdrant database manager."""
    print("🧪 Testing Database Manager...")
    
    try:
        # Import the database manager
        from src.database.qdrant_manager import QdrantManager
        
        # Create database manager
        manager = QdrantManager(host="localhost", port=6333)
        
        # Test connection
        connected = await manager.connect()
        if connected:
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test health check
        health = await manager.health_check()
        if health.get("healthy"):
            print("✅ Database health check passed")
        else:
            print("❌ Database health check failed")
            return False
        
        # Test collection creation
        collection_created = await manager.create_collection("test_collection", 1536)
        if collection_created:
            print("✅ Collection creation successful")
        else:
            print("❌ Collection creation failed")
            return False
        
        # Test collection listing
        collections = await manager.list_collections()
        if collections:
            print(f"✅ Collection listing successful: {len(collections)} collections")
        else:
            print("❌ Collection listing failed")
            return False
        
        # Test disconnect
        disconnected = await manager.disconnect()
        if disconnected:
            print("✅ Database disconnection successful")
        else:
            print("❌ Database disconnection failed")
            return False
        
        print("✅ Database Manager tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database Manager test failed: {e}")
        return False


async def test_base_agent():
    """Test the base agent framework."""
    print("🧪 Testing Base Agent Framework...")
    
    try:
        from src.agents.base.base_agent import BaseAgent, AgentType, AgentStatus, AgentCapability
        
        # Create a mock agent class
        class MockAgent(BaseAgent):
            async def _execute_task_impl(self, task):
                return {"success": True, "result": f"Task {task.id} completed"}
        
        # Create agent capabilities
        capabilities = [
            AgentCapability(
                name="test_capability",
                description="Test capability for testing",
                version="1.0.0"
            )
        ]
        
        # Create mock agent
        agent = MockAgent(
            agent_id="test_agent_001",
            agent_type=AgentType.CUSTOM,
            name="Test Agent",
            description="A test agent for testing",
            capabilities=capabilities
        )
        
        # Test agent initialization
        initialized = await agent.initialize()
        if initialized:
            print("✅ Agent initialization successful")
        else:
            print("❌ Agent initialization failed")
            return False
        
        # Test agent status
        status = await agent.get_status()
        if status["status"] == "active":
            print("✅ Agent status retrieval successful")
        else:
            print("❌ Agent status retrieval failed")
            return False
        
        # Test agent capabilities
        agent_capabilities = await agent.get_capabilities()
        if agent_capabilities:
            print(f"✅ Agent capabilities retrieval successful: {len(agent_capabilities)} capabilities")
        else:
            print("❌ Agent capabilities retrieval failed")
            return False
        
        # Test message handling
        message_result = await agent.handle_message("ping", {})
        if message_result.get("success"):
            print("✅ Agent message handling successful")
        else:
            print("❌ Agent message handling failed")
            return False
        
        # Test agent stop
        stopped = await agent.stop()
        if stopped:
            print("✅ Agent stop successful")
        else:
            print("❌ Agent stop failed")
            return False
        
        print("✅ Base Agent Framework tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Base Agent Framework test failed: {e}")
        return False


async def test_agent_registry():
    """Test the agent registry system."""
    print("🧪 Testing Agent Registry...")
    
    try:
        from src.agents.registry import AgentRegistry
        from src.agents.base.base_agent import BaseAgent, AgentType, AgentStatus, AgentCapability
        
        # Create a mock agent class
        class MockRegistryAgent(BaseAgent):
            async def _execute_task_impl(self, task):
                return {"success": True, "result": f"Task {task.id} completed"}
        
        # Create registry
        registry = AgentRegistry()
        
        # Test registry initialization
        initialized = await registry.initialize()
        if initialized:
            print("✅ Registry initialization successful")
        else:
            print("❌ Registry initialization failed")
            return False
        
        # Create test agents
        agent1 = MockRegistryAgent(
            agent_id="test_agent_001",
            agent_type=AgentType.FRONTEND,
            name="Frontend Test Agent",
            description="A test frontend agent"
        )
        
        agent2 = MockRegistryAgent(
            agent_id="test_agent_002",
            agent_type=AgentType.BACKEND,
            name="Backend Test Agent",
            description="A test backend agent"
        )
        
        # Test agent registration
        registered1 = await registry.register_agent(agent1)
        registered2 = await registry.register_agent(agent2)
        
        if registered1 and registered2:
            print("✅ Agent registration successful")
        else:
            print("❌ Agent registration failed")
            return False
        
        # Test agent listing
        all_agents = registry.list_agents()
        if len(all_agents) == 2:
            print(f"✅ Agent listing successful: {len(all_agents)} agents")
        else:
            print("❌ Agent listing failed")
            return False
        
        # Test getting agents by type
        frontend_agents = registry.get_agents_by_type(AgentType.FRONTEND)
        backend_agents = registry.get_agents_by_type(AgentType.BACKEND)
        
        if len(frontend_agents) == 1 and len(backend_agents) == 1:
            print("✅ Agent type filtering successful")
        else:
            print("❌ Agent type filtering failed")
            return False
        
        # Test registry status
        registry_status = await registry.get_registry_status()
        if registry_status["total_agents"] == 2:
            print("✅ Registry status retrieval successful")
        else:
            print("❌ Registry status retrieval failed")
            return False
        
        # Test agent unregistration
        unregistered = await registry.unregister_agent("test_agent_001")
        if unregistered:
            print("✅ Agent unregistration successful")
        else:
            print("❌ Agent unregistration failed")
            return False
        
        # Test registry shutdown
        shutdown = await registry.shutdown()
        if shutdown:
            print("✅ Registry shutdown successful")
        else:
            print("❌ Registry shutdown failed")
            return False
        
        print("✅ Agent Registry tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent Registry test failed: {e}")
        return False


async def test_database_schemas():
    """Test the database schemas."""
    print("🧪 Testing Database Schemas...")
    
    try:
        from src.database.schemas import (
            CodeContext, Conversation, Documentation, ProjectState,
            GitOperation, CursorSession, AgentCollaboration,
            AgileProject, DocumentationArtifact, CodeLanguage,
            get_collection_config, get_all_collection_names
        )
        
        # Test CodeContext schema
        code_context = CodeContext(
            id="test_code_001",
            file_path="src/test.py",
            function_name="test_function",
            code_snippet="def test_function(): pass",
            language=CodeLanguage.PYTHON
        )
        
        code_dict = code_context.to_dict()
        if code_dict["id"] == "test_code_001":
            print("✅ CodeContext schema test passed")
        else:
            print("❌ CodeContext schema test failed")
            return False
        
        # Test Conversation schema
        conversation = Conversation(
            id="test_conv_001",
            agent_id="test_agent",
            user_id="test_user",
            message="Hello",
            response="Hi there!"
        )
        
        conv_dict = conversation.to_dict()
        if conv_dict["message"] == "Hello":
            print("✅ Conversation schema test passed")
        else:
            print("❌ Conversation schema test failed")
            return False
        
        # Test collection configuration
        collection_config = get_collection_config("code_context")
        if collection_config["vector_size"] == 1536:
            print("✅ Collection configuration test passed")
        else:
            print("❌ Collection configuration test failed")
            return False
        
        # Test collection names
        collection_names = get_all_collection_names()
        if "code_context" in collection_names:
            print("✅ Collection names test passed")
        else:
            print("❌ Collection names test failed")
            return False
        
        print("✅ Database Schemas tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Database Schemas test failed: {e}")
        return False


async def run_phase2_tests():
    """Run all Phase 2 infrastructure tests."""
    print("🚀 Running Phase 2 Infrastructure Tests...")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_database_manager())
    test_results.append(await test_base_agent())
    test_results.append(await test_agent_registry())
    test_results.append(await test_database_schemas())
    
    # Summary
    print("=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print(f"🎉 All {total_tests} Phase 2 tests passed!")
        print("✅ Phase 2 infrastructure is ready!")
        return True
    else:
        print(f"❌ {total_tests - passed_tests} out of {total_tests} tests failed")
        print("🔧 Phase 2 infrastructure needs attention")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_phase2_tests())
    sys.exit(0 if success else 1)
