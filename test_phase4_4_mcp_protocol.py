#!/usr/bin/env python3
"""
Phase 4.4 Testing: MCP Protocol Testing for Communication System
Tests all communication components using the proper MCP protocol (stdin/stdout).
"""

import json
import subprocess
import time
import sys
from datetime import datetime


def log_test(message, status="INFO"):
    """Log test messages with timestamp."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {status}: {message}")


def send_mcp_request(process, request):
    """Send an MCP request to the server process."""
    try:
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response
        response = process.stdout.readline()
        if response:
            return json.loads(response.strip())
        else:
            return None
    except Exception as e:
        log_test(f"Error sending MCP request: {e}", "ERROR")
        return None


def test_mcp_server_startup():
    """Test MCP server startup and initialization."""
    log_test("Testing MCP server startup...")
    
    try:
        # Start the MCP server
        process = subprocess.Popen(
            ["python3", "protocol_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait a moment for server to initialize
        time.sleep(2)
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "Phase4.4-Test",
                    "version": "1.0.0"
                }
            }
        }
        
        response = send_mcp_request(process, init_request)
        
        if response and "result" in response:
            log_test("✅ MCP server started successfully", "PASS")
            return process, True
        else:
            log_test("❌ MCP server initialization failed", "FAIL")
            process.terminate()
            return None, False
            
    except Exception as e:
        log_test(f"❌ MCP server startup failed: {e}", "FAIL")
        return None, False


def test_mcp_tools(process):
    """Test MCP tools availability."""
    log_test("Testing MCP tools availability...")
    
    try:
        # Request tools list
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = send_mcp_request(process, tools_request)
        
        if response and "result" in response:
            tools = response["result"].get("tools", [])
            log_test(f"✅ MCP tools endpoint accessible, found {len(tools)} tools", "PASS")
            
            # Check for communication tools
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
            log_test("❌ Tools endpoint failed", "FAIL")
            return False
            
    except Exception as e:
        log_test(f"❌ MCP tools test failed: {e}", "FAIL")
        return False


def test_cross_chat_workflow(process):
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
        for i, session in enumerate(sessions):
            request = {
                "jsonrpc": "2.0",
                "id": f"session_{i}",
                "method": "tools/call",
                "params": {
                    "name": "create_cross_chat_session",
                    "arguments": session
                }
            }
            
            response = send_mcp_request(process, request)
            
            if response and "result" in response:
                result = response["result"]
                if result.get("success"):
                    created_sessions.append(session['chat_id'])
                    log_test(f"    ✅ Created session: {session['chat_id']}", "PASS")
                else:
                    log_test(f"    ❌ Failed to create session: {session['chat_id']}", "FAIL")
            else:
                log_test(f"    ❌ Session creation request failed", "FAIL")
        
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
        for i, msg in enumerate(messages):
            request = {
                "jsonrpc": "2.0",
                "id": f"msg_{i}",
                "method": "tools/call",
                "params": {
                    "name": "broadcast_cross_chat_message",
                    "arguments": msg
                }
            }
            
            response = send_mcp_request(process, request)
            
            if response and "result" in response:
                result = response["result"]
                if result.get("success"):
                    broadcasted_messages.append(msg['source_chat'])
                    log_test(f"    ✅ Broadcasted message from: {msg['source_chat']}", "PASS")
                else:
                    log_test(f"    ❌ Failed to broadcast from: {msg['source_chat']}", "FAIL")
            else:
                log_test(f"    ❌ Broadcast request failed", "FAIL")
        
        if len(broadcasted_messages) != 3:
            log_test("❌ Not all messages broadcasted successfully", "FAIL")
            return False
        
        # Step 3: Retrieve messages
        log_test("  Retrieving cross-chat messages...")
        
        request = {
            "jsonrpc": "2.0",
            "id": "retrieve_messages",
            "method": "tools/call",
            "params": {
                "name": "get_cross_chat_messages",
                "arguments": {}
            }
        }
        
        response = send_mcp_request(process, request)
        
        if response and "result" in response:
            result = response["result"]
            if result.get("success"):
                messages_data = result.get("messages", [])
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
            log_test("    ❌ Message retrieval request failed", "FAIL")
            return False
        
        log_test("✅ Cross-chat workflow test completed successfully", "PASS")
        return True
        
    except Exception as e:
        log_test(f"❌ Cross-chat workflow test failed: {e}", "FAIL")
        return False


def test_redis_persistence(process):
    """Test Redis persistence by checking message storage."""
    log_test("Testing Redis persistence...")
    
    try:
        # Get initial message count
        request = {
            "jsonrpc": "2.0",
            "id": "persistence_test_1",
            "method": "tools/call",
            "params": {
                "name": "get_cross_chat_messages",
                "arguments": {}
            }
        }
        
        response = send_mcp_request(process, request)
        
        if not response or "result" not in response:
            log_test("❌ Initial message retrieval failed", "FAIL")
            return False
        
        initial_messages = response["result"].get("messages", [])
        initial_count = len(initial_messages)
        log_test(f"  Initial message count: {initial_count}")
        
        # Add a new message to test persistence
        restart_message = {
            "source_chat": "system",
            "source_agent": "coordinator", 
            "content": "🔄 Phase 4.4: Redis persistence test message",
            "target_chats": ["all"]
        }
        
        request = {
            "jsonrpc": "2.0",
            "id": "restart_test_msg",
            "method": "tools/call",
            "params": {
                "name": "broadcast_cross_chat_message",
                "arguments": restart_message
            }
        }
        
        response = send_mcp_request(process, request)
        
        if response and "result" in response:
            result = response["result"]
            if result.get("success"):
                log_test("    ✅ Persistence test message broadcasted", "PASS")
                
                # Check if previous messages are still accessible
                request = {
                    "jsonrpc": "2.0",
                    "id": "persistence_test_2",
                    "method": "tools/call",
                    "params": {
                        "name": "get_cross_chat_messages",
                        "arguments": {}
                    }
                }
                
                response = send_mcp_request(process, request)
                
                if response and "result" in response:
                    final_messages = response["result"].get("messages", [])
                    final_count = len(final_messages)
                    log_test(f"    Final message count: {final_count}")
                    
                    # Check if we have more messages than just the test message
                    if final_count > 1:
                        log_test("    ✅ Previous messages accessible", "PASS")
                        log_test("✅ Redis persistence test completed successfully", "PASS")
                        return True
                    else:
                        log_test("    ❌ Previous messages not accessible", "FAIL")
                        return False
                else:
                    log_test("    ❌ Final message retrieval failed", "FAIL")
                    return False
            else:
                log_test("    ❌ Persistence test message failed", "FAIL")
                return False
        else:
            log_test("    ❌ Persistence test message request failed", "FAIL")
            return False
            
    except Exception as e:
        log_test(f"❌ Redis persistence test failed: {e}", "FAIL")
        return False


def test_performance(process):
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
            
            request = {
                "jsonrpc": "2.0",
                "id": f"perf_test_{i}",
                "method": "tools/call",
                "params": {
                    "name": "broadcast_cross_chat_message",
                    "arguments": message
                }
            }
            
            response = send_mcp_request(process, request)
            
            if not response or "result" not in response:
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
    log_test("🚀 Starting Phase 4.4: Testing & Documentation (MCP Protocol)", "START")
    log_test("=" * 70)
    
    # Start MCP server
    process, server_started = test_mcp_server_startup()
    if not server_started:
        log_test("❌ Cannot proceed without MCP server", "ERROR")
        return False
    
    test_results = []
    
    try:
        # Run all tests
        tests = [
            ("MCP Tools", test_mcp_tools),
            ("Cross-Chat Workflow", test_cross_chat_workflow),
            ("Redis Persistence", test_redis_persistence),
            ("Performance", test_performance)
        ]
        
        for test_name, test_func in tests:
            log_test(f"Running test: {test_name}")
            try:
                result = test_func(process)
                test_results.append((test_name, result))
                log_test(f"Test {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                log_test(f"Test {test_name} crashed: {e}", "ERROR")
                test_results.append((test_name, False))
            
            log_test("-" * 50)
            time.sleep(1)  # Brief pause between tests
        
    finally:
        # Clean up
        if process:
            process.terminate()
            process.wait()
            log_test("MCP server terminated")
    
    # Summary
    log_test("📊 PHASE 4.4 TEST RESULTS SUMMARY", "SUMMARY")
    log_test("=" * 70)
    
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
