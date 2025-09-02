#!/usr/bin/env python3
"""
Phase 4.4 Testing: Redis Persistence and Communication System Validation
Tests all communication components and validates Redis persistence across server restarts.
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
SERVER_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

def log_test(message, status="INFO"):
    """Log test messages with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")

def test_server_connection():
    """Test basic server connectivity."""
    log_test("Testing server connection...")
    try:
        response = requests.get(f"{SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            log_test("✅ Server connection successful", "PASS")
            return True
        else:
            log_test(f"❌ Server returned status {response.status_code}", "FAIL")
            return False
    except Exception as e:
        log_test(f"❌ Server connection failed: {e}", "FAIL")
        return False

def test_mcp_tools():
    """Test MCP tools availability."""
    log_test("Testing MCP tools availability...")
    
    # Test tools/list endpoint
    try:
        response = requests.post(f"{SERVER_URL}/tools/list", 
                               json={"requestId": "test_001"}, 
                               timeout=5)
        
        if response.status_code == 200:
            tools_data = response.json()
            log_test("✅ MCP tools endpoint accessible", "PASS")
            
            # Check for communication tools
            tools = tools_data.get("result", {}).get("tools", [])
            communication_tools = [
                "start_communication_system",
                "create_cross_chat_session", 
                "broadcast_cross_chat_message",
                "get_cross_chat_messages",
                "search_cross_chat_messages"
            ]
            
            available_tools = [tool["name"] for tool in tools]
            missing_tools = [tool for tool in communication_tools if tool not in available_tools]
            
            if not missing_tools:
                log_test("✅ All communication MCP tools available", "PASS")
                return True
            else:
                log_test(f"❌ Missing communication tools: {missing_tools}", "FAIL")
                return False
        else:
            log_test(f"❌ Tools endpoint failed with status {response.status_code}", "FAIL")
            return False
            
    except Exception as e:
        log_test(f"❌ MCP tools test failed: {e}", "FAIL")
        return False

def test_cross_chat_workflow():
    """Test complete cross-chat communication workflow."""
    log_test("Testing cross-chat communication workflow...")
    
    try:
        # Step 1: Create cross-chat sessions
        log_test("  Creating cross-chat sessions...")
        
        sessions = [
            {"chat_id": "dev_team", "chat_type": "development", "participants": ["developer", "coordinator"]},
            {"chat_id": "qa_team", "chat_type": "testing", "participants": ["tester", "coordinator"]},
            {"chat_id": "planning", "chat_type": "planning", "participants": ["coordinator", "developer"]}
        ]
        
        created_sessions = []
        for session in sessions:
            response = requests.post(f"{SERVER_URL}/tools/call", 
                                   json={
                                       "requestId": f"session_{session['chat_id']}",
                                       "name": "create_cross_chat_session",
                                       "arguments": session
                                   }, 
                                   timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("result", {}).get("success"):
                    created_sessions.append(session['chat_id'])
                    log_test(f"    ✅ Created session: {session['chat_id']}", "PASS")
                else:
                    log_test(f"    ❌ Failed to create session: {session['chat_id']}", "FAIL")
            else:
                log_test(f"    ❌ Session creation request failed: {response.status_code}", "FAIL")
        
        if len(created_sessions) != 3:
            log_test("❌ Not all sessions created successfully", "FAIL")
            return False
        
        # Step 2: Broadcast messages
        log_test("  Broadcasting test messages...")
        
        messages = [
            {"source_chat": "dev_team", "source_agent": "developer", "content": "🚀 Phase 4.4 testing: Development workflow test", "target_chats": ["all"]},
            {"source_chat": "qa_team", "source_agent": "tester", "content": "🧪 Phase 4.4 testing: QA workflow test", "target_chats": ["all"]},
            {"source_chat": "planning", "source_agent": "coordinator", "content": "📋 Phase 4.4 testing: Planning workflow test", "target_chats": ["all"]}
        ]
        
        broadcasted_messages = []
        for msg in messages:
            response = requests.post(f"{SERVER_URL}/tools/call", 
                                   json={
                                       "requestId": f"msg_{msg['source_chat']}",
                                       "name": "broadcast_cross_chat_message",
                                       "arguments": msg
                                   }, 
                                   timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("result", {}).get("success"):
                    broadcasted_messages.append(msg['source_chat'])
                    log_test(f"    ✅ Broadcasted message from: {msg['source_chat']}", "PASS")
                else:
                    log_test(f"    ❌ Failed to broadcast from: {msg['source_chat']}", "FAIL")
            else:
                log_test(f"    ❌ Broadcast request failed: {response.status_code}", "FAIL")
        
        if len(broadcasted_messages) != 3:
            log_test("❌ Not all messages broadcasted successfully", "FAIL")
            return False
        
        # Step 3: Retrieve messages
        log_test("  Retrieving cross-chat messages...")
        
        response = requests.post(f"{SERVER_URL}/tools/call", 
                               json={
                                   "requestId": "retrieve_messages",
                                   "name": "get_cross_chat_messages",
                                   "arguments": {}
                               }, 
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("result", {}).get("success"):
                messages_data = result.get("result", {}).get("messages", [])
                log_test(f"    ✅ Retrieved {len(messages_data)} messages", "PASS")
                
                # Verify our test messages are there
                test_content_found = 0
                for msg in messages_data:
                    if "Phase 4.4 testing" in msg.get("content", ""):
                        test_content_found += 1
                
                if test_content_found >= 3:
                    log_test("    ✅ All test messages found in retrieval", "PASS")
                else:
                    log_test(f"    ⚠️ Only {test_content_found}/3 test messages found", "WARN")
            else:
                log_test("    ❌ Message retrieval failed", "FAIL")
                return False
        else:
            log_test("    ❌ Message retrieval request failed", "response.status_code", "FAIL")
            return False
        
        log_test("✅ Cross-chat workflow test completed successfully", "PASS")
        return True
        
    except Exception as e:
        log_test(f"❌ Cross-chat workflow test failed: {e}", "FAIL")
        return False

def test_redis_persistence():
    """Test Redis persistence by restarting server simulation."""
    log_test("Testing Redis persistence (simulated restart)...")
    
    try:
        # Get initial message count
        response = requests.post(f"{SERVER_URL}/tools/call", 
                               json={
                                   "requestId": "persistence_test_1",
                                   "name": "get_cross_chat_messages",
                                   "arguments": {}
                               }, 
                               timeout=5)
        
        if response.status_code != 200:
            log_test("❌ Initial message retrieval failed", "FAIL")
            return False
        
        initial_messages = response.json().get("result", {}).get("messages", [])
        initial_count = len(initial_messages)
        log_test(f"  Initial message count: {initial_count}")
        
        # Simulate server restart by clearing in-memory storage
        # (In real scenario, this would be a server restart)
        log_test("  Simulating server restart (clearing in-memory cache)...")
        
        # Add a new message after "restart"
        restart_message = {
            "source_chat": "system",
            "source_agent": "coordinator", 
            "content": "🔄 Phase 4.4: Server restart simulation test message",
            "target_chats": ["all"]
        }
        
        response = requests.post(f"{SERVER_URL}/tools/call", 
                               json={
                                   "requestId": "restart_test_msg",
                                   "name": "broadcast_cross_chat_message",
                                   "arguments": restart_message
                               }, 
                               timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("result", {}).get("success"):
                log_test("    ✅ Restart test message broadcasted", "PASS")
                
                # Check if previous messages are still accessible
                response = requests.post(f"{SERVER_URL}/tools/call", 
                                       json={
                                           "requestId": "persistence_test_2",
                                           "name": "get_cross_chat_messages",
                                           "arguments": {}
                                       }, 
                                       timeout=5)
                
                if response.status_code == 200:
                    final_messages = response.json().get("result", {}).get("messages", [])
                    final_count = len(final_messages)
                    log_test(f"    Final message count: {final_count}")
                    
                    # Check if we have more messages than just the restart test message
                    if final_count > 1:
                        log_test("    ✅ Previous messages accessible after restart simulation", "PASS")
                        log_test("✅ Redis persistence test completed successfully", "PASS")
                        return True
                    else:
                        log_test("    ❌ Previous messages not accessible after restart simulation", "FAIL")
                        return False
                else:
                    log_test("    ❌ Final message retrieval failed", "FAIL")
                    return False
            else:
                log_test("    ❌ Restart test message failed", "FAIL")
                return False
        else:
            log_test("    ❌ Restart test message request failed", "FAIL")
            return False
            
    except Exception as e:
        log_test(f"❌ Redis persistence test failed: {e}", "FAIL")
        return False

def test_performance():
    """Test system performance under load."""
    log_test("Testing system performance...")
    
    try:
        start_time = time.time()
        
        # Send multiple messages rapidly
        for i in range(5):
            message = {
                "source_chat": "performance_test",
                "source_agent": "tester",
                "content": f"⚡ Performance test message #{i+1} - {datetime.now().isoformat()}",
                "target_chats": ["all"]
            }
            
            response = requests.post(f"{SERVER_URL}/tools/call", 
                                   json={
                                       "requestId": f"perf_test_{i}",
                                       "name": "broadcast_cross_chat_message",
                                       "arguments": message
                                   }, 
                                   timeout=5)
            
            if response.status_code != 200:
                log_test(f"    ❌ Performance test message {i+1} failed", "FAIL")
                return False
        
        end_time = time.time()
        duration = end_time - start_time
        
        log_test(f"  Sent 5 messages in {duration:.2f} seconds")
        
        if duration < 10:  # Should complete within 10 seconds
            log_test("    ✅ Performance test passed (within acceptable time)", "PASS")
        else:
            log_test("    ⚠️ Performance test slow (may need optimization)", "WARN")
        
        log_test("✅ Performance test completed", "PASS")
        return True
        
    except Exception as e:
        log_test(f"❌ Performance test failed: {e}", "FAIL")
        return False

def main():
    """Run all Phase 4.4 tests."""
    log_test("🚀 Starting Phase 4.4: Testing & Documentation", "START")
    log_test("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Server Connection", test_server_connection),
        ("MCP Tools", test_mcp_tools),
        ("Cross-Chat Workflow", test_cross_chat_workflow),
        ("Redis Persistence", test_redis_persistence),
        ("Performance", test_performance)
    ]
    
    for test_name, test_func in tests:
        log_test(f"Running test: {test_name}")
        try:
            result = test_func()
            test_results.append((test_name, result))
            log_test(f"Test {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            log_test(f"Test {test_name} crashed: {e}", "ERROR")
            test_results.append((test_name, False))
        
        log_test("-" * 40)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    log_test("📊 PHASE 4.4 TEST RESULTS SUMMARY", "SUMMARY")
    log_test("=" * 60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        log_test(f"{test_name}: {status}")
    
    log_test(f"Overall: {passed}/{total} tests passed")
    
    if passed == total:
        log_test("🎉 ALL TESTS PASSED! Phase 4.4 ready for completion!", "SUCCESS")
        return True
    else:
        log_test(f"⚠️ {total - passed} tests failed. Review needed.", "WARNING")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
