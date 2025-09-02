"""Tests for Phase 3 Coordinator Agent and PDCA Framework."""

import asyncio
import sys
from datetime import datetime


async def test_pdca_framework():
    """Test the PDCA framework."""
    print("🧪 Testing PDCA Framework...")
    print("=" * 40)
    
    try:
        from src.agents.coordinator.pdca_framework import (
            PDCAFramework, PDCAPhase, PDCAStatus
        )
        
        # Create PDCA framework
        framework = PDCAFramework()
        print("✅ PDCA Framework created")
        
        # Test cycle creation
        print("📋 Creating PDCA cycle...")
        cycle = await framework.create_cycle(
            name="Test Project",
            description="A test project for testing",
            objectives=["Complete testing", "Validate functionality"],
            success_criteria=["All tests pass", "System works correctly"]
        )
        print(f"✅ Cycle created: {cycle.name}")
        
        # Test cycle start
        print("🚀 Starting PDCA cycle...")
        started = await framework.start_cycle(cycle.id)
        if started:
            print("✅ Cycle started successfully")
        else:
            print("❌ Cycle start failed")
            return False
        
        # Test phase advancement
        print("⏭️  Advancing phases...")
        for phase_name in ["plan", "do", "check", "act"]:
            advanced = await framework.advance_phase(cycle.id)
            if advanced:
                print(f"✅ Advanced to {phase_name} phase")
            else:
                print(f"❌ Failed to advance to {phase_name} phase")
                return False
        
        # Test cycle completion
        print("🏁 Completing cycle...")
        completed = await framework.complete_cycle(cycle.id, success=True)
        if completed:
            print("✅ Cycle completed successfully")
        else:
            print("❌ Cycle completion failed")
            return False
        
        # Test framework status
        status = framework.get_framework_status()
        print(f"✅ Framework status: {status['total_cycles']} cycles")
        
        print("✅ PDCA Framework tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDCA Framework test failed: {e}")
        return False


async def test_coordinator_agent():
    """Test the Coordinator Agent."""
    print("🧪 Testing Coordinator Agent...")
    print("=" * 40)
    
    try:
        from src.agents.coordinator.coordinator_agent import CoordinatorAgent
        
        # Create coordinator agent
        print("🤖 Creating Coordinator Agent...")
        coordinator = CoordinatorAgent(
            agent_id="test_coordinator_001",
            name="Test Coordinator"
        )
        
        # Test initialization
        print("🚀 Initializing coordinator...")
        initialized = await coordinator.initialize()
        if initialized:
            print("✅ Coordinator initialized successfully")
        else:
            print("❌ Coordinator initialization failed")
            return False
        
        # Test project creation
        print("📋 Creating test project...")
        project = await coordinator.create_project(
            name="Test Project",
            description="A test project for coordinator testing",
            objectives=["Test coordinator functionality", "Validate PDCA integration"],
            success_criteria=["All tests pass", "Coordinator works correctly"],
            timeline={"start": "2025-09-02", "end": "2025-09-03"},
            resources=["Test agents", "Test database"],
            risks=["Test failures", "Integration issues"]
        )
        print(f"✅ Project created: {project.name}")
        
        # Test project start
        print("🚀 Starting project...")
        started = await coordinator.start_project(project.id)
        if started:
            print("✅ Project started successfully")
        else:
            print("❌ Project start failed")
            return False
        
        # Test project status
        print("📊 Getting project status...")
        status = await coordinator.get_project_status(project.id)
        if status:
            print(f"✅ Project status: {status['status']}")
        else:
            print("❌ Failed to get project status")
            return False
        
        # Test system status
        print("🔍 Getting system status...")
        system_status = await coordinator.get_system_status()
        if system_status:
            print(f"✅ System status: {system_status['coordinator_status']}")
        else:
            print("❌ Failed to get system status")
            return False
        
        # Test agent creation
        print("🤖 Creating test agent...")
        agent_info = await coordinator.create_agent(
            agent_type="test",
            name="Test Agent",
            description="A test agent for testing",
            capabilities=["testing", "validation"]
        )
        if "agent_id" in agent_info:
            print(f"✅ Agent created: {agent_info['name']}")
        else:
            print("❌ Agent creation failed")
            return False
        
        # Test coordinator stop
        print("⏹️  Stopping coordinator...")
        stopped = await coordinator.stop()
        if stopped:
            print("✅ Coordinator stopped successfully")
        else:
            print("❌ Coordinator stop failed")
            return False
        
        print("✅ Coordinator Agent tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Coordinator Agent test failed: {e}")
        return False


async def test_pdca_integration():
    """Test PDCA integration with Coordinator Agent."""
    print("🧪 Testing PDCA Integration...")
    print("=" * 40)
    
    try:
        from src.agents.coordinator.coordinator_agent import CoordinatorAgent
        
        # Create coordinator
        coordinator = CoordinatorAgent("test_integration_001", "Integration Test Coordinator")
        await coordinator.initialize()
        
        # Create project with PDCA
        print("📋 Creating integrated project...")
        project = await coordinator.create_project(
            name="PDCA Integration Test",
            description="Testing PDCA integration with coordinator",
            objectives=["Test PDCA workflow", "Validate integration"],
            success_criteria=["PDCA cycles work", "Integration successful"],
            timeline={"start": "2025-09-02", "end": "2025-09-03"},
            resources=["PDCA framework", "Coordinator agent"],
            risks=["Integration failures", "Workflow issues"]
        )
        
        # Start project (starts PDCA cycle)
        await coordinator.start_project(project.id)
        
        # Test PDCA phase advancement
        print("⏭️  Testing PDCA phase advancement...")
        for i in range(4):  # 4 phases: plan, do, check, act
            advanced = await coordinator.advance_project_phase(project.id)
            if advanced:
                print(f"✅ Advanced to phase {i+1}")
            else:
                print(f"❌ Failed to advance to phase {i+1}")
                return False
        
        # Verify project completion
        final_status = await coordinator.get_project_status(project.id)
        if final_status and final_status['status'] == 'completed':
            print("✅ Project completed successfully with PDCA")
        else:
            print("❌ Project completion failed")
            return False
        
        # Cleanup
        await coordinator.stop()
        
        print("✅ PDCA Integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ PDCA Integration test failed: {e}")
        return False


async def run_phase3_tests():
    """Run all Phase 3 tests."""
    print("🚀 Running Phase 3 Coordinator & PDCA Tests...")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(await test_pdca_framework())
    test_results.append(await test_coordinator_agent())
    test_results.append(await test_pdca_integration())
    
    # Summary
    print("=" * 60)
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    if passed_tests == total_tests:
        print(f"🎉 All {total_tests} Phase 3 tests passed!")
        print("✅ Phase 3 Coordinator Agent & PDCA Framework is ready!")
        print("\n💡 You can now:")
        print("   - Create and manage projects with PDCA cycles")
        print("   - Coordinate multiple agents through the system")
        print("   - Use the PDCA framework for continuous improvement")
        print("   - Monitor system performance and project status")
    else:
        print(f"❌ {total_tests - passed_tests} out of {total_tests} tests failed")
        print("🔧 Phase 3 components need attention")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = asyncio.run(run_phase3_tests())
    sys.exit(0 if success else 1)
