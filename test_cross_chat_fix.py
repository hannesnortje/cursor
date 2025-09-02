#!/usr/bin/env python3
"""
Test script to verify cross-chat message functionality is now working.
"""

import json
import subprocess
import sys

def send_mcp_message(message):
    """Send MCP message to the server."""
    try:
        # Start the server process
        process = subprocess.Popen(
            ["python3", "protocol_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send the message
        stdout, stderr = process.communicate(input=json.dumps(message) + "\n", timeout=10)
        
        # Parse response
        try:
            # The server might output multiple lines, get the last valid JSON
            lines = stdout.strip().split('\n')
            for line in reversed(lines):
                line = line.strip()
                if line and line.startswith('{'):
                    try:
                        response = json.loads(line)
                        return response, stderr
                    except json.JSONDecodeError:
                        continue
            
            return {"error": "No valid JSON response found", "raw": stdout}, stderr
        except Exception as e:
            return {"error": f"Response parsing error: {e}", "raw": stdout}, stderr
            
    except subprocess.TimeoutExpired:
        process.kill()
        return {"error": "Process timeout"}, ""
    except Exception as e:
        return {"error": f"Process error: {e}"}, ""


def test_cross_chat_functionality():
    """Test that cross-chat messages are now actually stored and retrieved."""
    print("🧪 Testing Cross-Chat Message Storage & Retrieval")
    print("=" * 60)
    
    # Test 1: Initialize server
    print("\n1️⃣ Testing server initialization...")
    init_message = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response, stderr = send_mcp_message(init_message)
    if "error" in response:
        print(f"❌ Server initialization failed: {response['error']}")
        if stderr:
            print(f"Stderr: {stderr}")
        return False
    else:
        print("✅ Server initialized successfully")
    
    # Test 2: Send first cross-chat message
    print("\n2️⃣ Testing first cross-chat message...")
    message1 = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "broadcast_cross_chat_message",
            "arguments": {
                "source_chat": "dev_team",
                "source_agent": "developer",
                "content": "🚀 Development sprint starting! Working on Phase 4.3!",
                "target_chats": ["all"]
            }
        }
    }
    
    response, stderr = send_mcp_message(message1)
    if "error" in response:
        print(f"❌ First message failed: {response['error']}")
        return False
    
    # Check if the response indicates success
    if "result" in response:
        result = response.get("result", {})
        if "structuredContent" in result:
            structured_content = result.get("structuredContent", {})
            if structured_content.get("success"):
                print("✅ First message sent successfully")
            else:
                print(f"❌ First message failed: {structured_content}")
                return False
        else:
            # Check if the content indicates success
            content = result.get("content", [])
            if content and "Message broadcast successfully" in content[0].get("text", ""):
                print("✅ First message sent successfully")
            else:
                print(f"❌ First message failed: {content}")
                return False
    else:
        print(f"❌ First message failed: {response}")
        return False
    
    # Test 3: Send second cross-chat message
    print("\n3️⃣ Testing second cross-chat message...")
    message2 = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "broadcast_cross_chat_message",
            "arguments": {
                "source_chat": "qa_team",
                "source_agent": "tester",
                "content": "🧪 QA testing Phase 4.3 cross-chat functionality!",
                "target_chats": ["all"]
            }
        }
    }
    
    response, stderr = send_mcp_message(message2)
    if "error" in response:
        print(f"❌ Second message failed: {response['error']}")
        return False
    
    # Check if the response indicates success
    if "result" in response:
        result = response.get("result", {})
        if "structuredContent" in result:
            structured_content = result.get("structuredContent", {})
            if structured_content.get("success"):
                print("✅ Second message sent successfully")
            else:
                print(f"❌ Second message failed: {structured_content}")
                return False
        else:
            # Check if the content indicates success
            content = result.get("content", [])
            if content and "Message broadcast successfully" in content[0].get("text", ""):
                print("✅ Second message sent successfully")
            else:
                print(f"❌ Second message failed: {content}")
                return False
    else:
        print(f"❌ Second message failed: {response}")
        return False
    
    # Test 4: Retrieve all messages
    print("\n4️⃣ Testing message retrieval...")
    get_messages = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_cross_chat_messages",
            "arguments": {
                "limit": 10
            }
        }
    }
    
    response, stderr = send_mcp_message(get_messages)
    if "error" in response:
        print(f"❌ Message retrieval failed: {response['error']}")
        return False
    
    result = response.get("result", {})
    structured_content = result.get("structuredContent", {})
    
    if structured_content.get("success"):
        messages = structured_content.get("messages", [])
        print(f"✅ Retrieved {len(messages)} messages")
        
        if len(messages) >= 2:
            print("✅ Both messages are now visible!")
            for i, msg in enumerate(messages, 1):
                print(f"   {i}. {msg['source_agent']} in {msg['source_chat']}: {msg['content'][:50]}...")
        else:
            print(f"❌ Expected 2+ messages, got {len(messages)}")
            return False
    else:
        print(f"❌ Message retrieval failed: {structured_content.get('error')}")
        return False
    
    # Test 5: Search for specific content
    print("\n5️⃣ Testing message search...")
    search_messages = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "search_cross_chat_messages",
            "arguments": {
                "query": "Phase 4.3",
                "limit": 5
            }
        }
    }
    
    response, stderr = send_mcp_message(search_messages)
    if "error" in response:
        print(f"❌ Message search failed: {response['error']}")
        return False
    
    result = response.get("result", {})
    structured_content = result.get("structuredContent", {})
    
    if structured_content.get("success"):
        results = structured_content.get("results", [])
        print(f"✅ Search found {len(results)} messages containing 'Phase 4.3'")
        
        if len(results) >= 1:
            print("✅ Search functionality working!")
        else:
            print("❌ Search should have found at least 1 message")
            return False
    else:
        print(f"❌ Message search failed: {structured_content.get('error')}")
        return False
    
    print("\n🎉 Cross-chat functionality is now working!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_cross_chat_functionality()
    sys.exit(0 if success else 1)
