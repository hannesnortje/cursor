#!/usr/bin/env python3
"""
Test the protocol server with LLM-based coordinator integration.

This simulates the exact MCP calls that Cursor would make.
"""

import sys
import os
sys.path.append('src')

import json
import logging
from protocol_server import AgentSystem

def test_protocol_server_llm():
    """Test the protocol server with LLM coordinator."""
    print("🔍 Testing Protocol Server with LLM Coordinator...")
    print("=" * 80)
    
    # Set up logging
    logging.basicConfig(level=logging.WARNING)
    
    # Initialize protocol server
    print("📦 Initializing Agent System...")
    server = AgentSystem()
    print("✅ Server initialized successfully")
    
    # Test 1: Phase 10.6 initial request
    print("\n" + "=" * 80)
    print("🧪 TEST 1: chat_with_coordinator - Initial Project Request")
    print("=" * 80)
    
    initial_message = """I need a project management system for my development team. We're a small team of 5 developers working on multiple client projects. We need a way to track tasks, manage sprints, and collaborate on code. The system should be web-based so we can access it from anywhere, and it needs to be fast and responsive. We also need user authentication and role-based access control. What would you recommend for the technology stack and architecture?"""
    
    print(f"📝 Input: {initial_message[:100]}...")
    response = server.chat_with_coordinator(initial_message)
    print(f"✅ Success: {response.get('success', False)}")
    print(f"📤 Response: {response.get('response', 'No response')[:200]}...")
    print(f"📋 Phase: {response.get('phase', 'unknown')}")
    print(f"🔄 Next Steps: {response.get('next_steps', 'unknown')}")
    print(f"🤖 LLM Enabled: {response.get('llm_enabled', False)}")
    
    # Test 2: Vue 3 follow-up
    print("\n" + "=" * 80)
    print("🧪 TEST 2: chat_with_coordinator - Vue 3 Technology Preference")
    print("=" * 80)
    
    vue_message = """Thanks! I'd specifically like to use Vue 3 with TypeScript for the frontend. My team has experience with React/Node.js/PostgreSQL/AWS but wants to transition to Vue 3. What complete technology stack would you recommend for this project management system?"""
    
    print(f"📝 Input: {vue_message[:100]}...")
    response = server.chat_with_coordinator(vue_message)
    print(f"✅ Success: {response.get('success', False)}")
    print(f"📤 Response: {response.get('response', 'No response')[:200]}...")
    print(f"📋 Phase: {response.get('phase', 'unknown')}")
    print(f"🔄 Next Steps: {response.get('next_steps', 'unknown')}")
    print(f"🤖 LLM Enabled: {response.get('llm_enabled', False)}")
    
    # Test 3: Agent creation
    print("\n" + "=" * 80)
    print("🧪 TEST 3: chat_with_coordinator - Agent Creation Request")
    print("=" * 80)
    
    agent_message = """Perfect! I love the Vue 3 + TypeScript stack recommendation. Now I'd like to create the specialized agents to help with this project. Can you set up the core development team agents: Agile Agent for sprint planning, Frontend Agent for Vue 3 development, Backend Agent for Node.js/API work, and Testing Agent for quality assurance?"""
    
    print(f"📝 Input: {agent_message[:100]}...")
    response = server.chat_with_coordinator(agent_message)
    print(f"✅ Success: {response.get('success', False)}")
    print(f"📤 Response: {response.get('response', 'No response')[:200]}...")
    print(f"📋 Phase: {response.get('phase', 'unknown')}")
    print(f"🔄 Next Steps: {response.get('next_steps', 'unknown')}")
    print(f"🤖 LLM Enabled: {response.get('llm_enabled', False)}")
    
    # Test 4: Test with JSON message (legacy support)
    print("\n" + "=" * 80)
    print("🧪 TEST 4: chat_with_coordinator - JSON Legacy Message")
    print("=" * 80)
    
    json_message = json.dumps({
        "type": "test",
        "action": "status_check",
        "message": "Testing legacy JSON support"
    })
    
    print(f"📝 Input: {json_message[:50]}...")
    response = server.chat_with_coordinator(json_message)
    print(f"✅ Success: {response.get('success', False)}")
    print(f"📤 Response: {response.get('response', 'No response')[:200]}...")
    
    print("\n" + "=" * 80)
    print("✅ Protocol Server LLM Integration Test Complete!")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    test_protocol_server_llm()
