#!/usr/bin/env python3
"""
Test script for the Simple Coordinator Agent.

This script tests the complete workflow with the simple coordinator.
"""

import sys
import os
sys.path.append('src')

from src.agents.coordinator.simple_coordinator_agent import SimpleCoordinatorAgent
import logging

def test_simple_coordinator():
    """Test the Simple Coordinator Agent with various scenarios."""
    print("🔍 Testing Simple Coordinator Agent...")
    print("=" * 60)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize coordinator
        print("📦 Initializing Simple Coordinator Agent...")
        coordinator = SimpleCoordinatorAgent()
        print("✅ Simple Coordinator Agent initialized successfully")
        
        # Test scenarios
        test_scenarios = [
            {
                "name": "Initial Project Request",
                "message": "I want to start a new project. I have a business need that requires a software solution, but I'm not sure exactly what technology stack or approach would be best. Can you help me figure out what we need to build and how to approach it? I'd like to use your PDCA framework to make sure we plan this properly before we start development. What information do you need from me to get started?",
                "expected_phase": "plan"
            },
            {
                "name": "Vue 3 Project Details",
                "message": "I need to build a project management system for my development team. Here are the details: Project Goals: A comprehensive project management system for a 5-developer team. Target users: Development team members, project managers, and clients. Key features: Task tracking, sprint management, code collaboration, web-based access, user authentication, role-based access control. Current State: Starting from scratch. Main challenges: Need centralized project management, team collaboration, and multi-client tracking. Target State: A fast, responsive web-based system for efficient management of multiple client projects. Implementation Strategy: Team size 5 developers, technical requirements web-based fast and responsive user authentication role-based access control, technology preference Vue 3 with TypeScript. What would you recommend for the complete technology stack and architecture?",
                "expected_phase": "plan"
            },
            {
                "name": "Agent Creation Request",
                "message": "I'd like to create the core agents for this project. Please set up the specialized agents we need.",
                "expected_phase": "do"
            },
            {
                "name": "Technology Selection Help",
                "message": "I'm not sure which frontend framework to choose. I've heard about Vue 3, React, and Angular. What would you recommend?",
                "expected_phase": "plan"
            }
        ]
        
        # Run tests
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"🧪 TEST {i}: {scenario['name']}")
            print(f"{'='*60}")
            
            print(f"📝 Input: {scenario['message'][:100]}...")
            
            # Process message
            response = coordinator.process_message(scenario['message'])
            
            if response.get("success"):
                print(f"📤 Response: {response.get('response', 'No response')[:200]}...")
                print(f"📋 Phase: {response.get('phase', 'Unknown')}")
                print(f"🔄 Next Steps: {response.get('next_steps', 'None')}")
                
                if response.get('agents_created'):
                    print(f"🤖 Agents Created: {response.get('agents_created')}")
                
                if response.get('agent_details'):
                    print(f"📋 Agent Details: {len(response.get('agent_details', []))} agents")
                
                # Check if phase matches expected
                if response.get('phase') == scenario['expected_phase']:
                    print("✅ Phase matches expected")
                else:
                    print(f"⚠️ Phase doesn't match expected: {scenario['expected_phase']}")
            else:
                print(f"❌ Failed to process message: {response.get('error', 'Unknown error')}")
        
        print(f"\n{'='*60}")
        print("✅ All tests completed!")
        print(f"{'='*60}")
        
        # Test conversation state
        print(f"\n📊 Conversation State:")
        state = coordinator.decision_engine.get_conversation_state()
        print(f"  - Current Phase: {state.current_phase.value}")
        print(f"  - Technology Stack: {state.technology_stack}")
        print(f"  - Created Agents: {state.created_agents}")
        print(f"  - Conversation History: {len(state.conversation_history)} messages")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_coordinator()
