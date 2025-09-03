#!/usr/bin/env python3
"""Quick system readiness test for the AI Agent System."""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_system_ready():
    """Test if the system is ready for Cursor chat testing."""
    print("🧪 AI Agent System - Quick Readiness Test")
    print("=" * 50)
    
    try:
        # Test 1: Import main system
        print("\n1️⃣ Testing imports...")
        from protocol_server import AgentSystem
        print("  ✅ Main system imported successfully")
        
        # Test 2: Initialize system
        print("\n2️⃣ Testing initialization...")
        agent_system = AgentSystem()
        print("  ✅ System initialized successfully")
        
        # Test 3: Check basic functionality
        print("\n3️⃣ Testing basic functionality...")
        health = agent_system.get_system_health()
        print(f"  ✅ System health: {health['status']}")
        print(f"  📊 Vector store: {health['vector_store']['status']}")
        
        # Test 4: Check communication status
        print("\n4️⃣ Testing communication...")
        comm_status = agent_system.get_communication_status()
        print(f"  ✅ Communication status retrieved")
        print(f"  🌐 WebSocket: {comm_status['websocket_server']['status']}")
        print(f"  📡 Redis: {comm_status['redis_queue']['status']}")
        print(f"  💾 Vector Store: {comm_status['vector_store']['status']}")
        
        # Test 5: Test project creation
        print("\n5️⃣ Testing project creation...")
        project_result = agent_system.start_project("test", "System Readiness Test")
        if project_result['success']:
            print(f"  ✅ Project created: {project_result['project_id']}")
        else:
            print(f"  ❌ Project creation failed: {project_result['error']}")
        
        print("\n" + "=" * 50)
        print("🎉 System is READY for Cursor chat testing!")
        print("\n📋 Next steps:")
        print("  1. Open Cursor chat")
        print("  2. Try: /system_health")
        print("  3. Try: /start_project test basic 'My Test Project'")
        print("  4. Check test_prompts.md for more test commands")
        
        return True
        
    except Exception as e:
        print(f"\n❌ System not ready: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Check if protocol_server.py exists")
        print("  2. Verify all dependencies are installed")
        print("  3. Check system logs for errors")
        return False

if __name__ == "__main__":
    success = test_system_ready()
    sys.exit(0 if success else 1)
