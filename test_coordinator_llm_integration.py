#!/usr/bin/env python3
"""
Test the LLM-based coordinator integration for Phase 10.6 Vue3 testing.

This simulates the exact workflow from PHASE_10_6_VUE3_PROMPT_SEQUENCE.md
"""

import sys
import os

sys.path.append("src")

from src.agents.coordinator.simple_coordinator_agent import SimpleCoordinatorAgent
import logging
import json


def test_phase_10_6_workflow():
    """Test the Phase 10.6 Vue 3 project management workflow."""
    print("🔍 Testing Phase 10.6 LLM Coordinator Integration...")
    print("=" * 80)

    # Set up logging
    logging.basicConfig(level=logging.WARNING)

    # Initialize coordinator
    print("📦 Initializing Simple Coordinator Agent...")
    coordinator = SimpleCoordinatorAgent()
    print("✅ Coordinator initialized successfully")

    # Test 1: Initial project request (from PHASE_10_6)
    print("\n" + "=" * 80)
    print("🧪 TEST 1: Phase 10.6 Initial Project Request")
    print("=" * 80)

    initial_message = """I need a project management system for my development team. We're a small team of 5 developers working on multiple client projects. We need a way to track tasks, manage sprints, and collaborate on code. The system should be web-based so we can access it from anywhere, and it needs to be fast and responsive. We also need user authentication and role-based access control. What would you recommend for the technology stack and architecture?"""

    print(f"📝 Input: {initial_message[:100]}...")
    response = coordinator.process_message(initial_message)
    print(f"📤 Response: {response['response'][:200]}...")
    print(f"📋 Phase: {response['phase']}")
    print(f"🔄 Next Steps: {response['next_steps']}")

    # Test 2: Follow-up with Vue 3 preference
    print("\n" + "=" * 80)
    print("🧪 TEST 2: Vue 3 Technology Preference")
    print("=" * 80)

    vue_message = """Thanks for the questions! Here are my answers:

1. Main purpose: A comprehensive project management system for our 5-developer team
2. Target users: Development team members, project managers, and clients  
3. Key features: Task tracking, sprint management, code collaboration, time tracking, client dashboards

4. Current state: We're using scattered tools (Trello, email, spreadsheets) - need centralization
5. Main challenges: Poor visibility into project status, difficulty tracking multiple client projects simultaneously

6. Success criteria: All projects visible in one dashboard, improved team collaboration, better client communication
7. Outcomes: 50% reduction in project coordination time, improved delivery predictability

8. Timeline: 3-4 months for MVP, then iterative improvements
9. Technical requirements: Vue 3 frontend (team preference), TypeScript, responsive design, real-time updates
10. Team: 5 developers with React/Node.js/PostgreSQL/AWS experience, transitioning to Vue 3

I'd specifically like to use Vue 3 with TypeScript for the frontend. What technology stack would you recommend?"""

    print(f"📝 Input: {vue_message[:150]}...")
    response = coordinator.process_message(vue_message)
    print(f"📤 Response: {response['response'][:300]}...")
    print(f"📋 Phase: {response['phase']}")
    print(f"🔄 Next Steps: {response['next_steps']}")

    # Test 3: Agent creation request
    print("\n" + "=" * 80)
    print("🧪 TEST 3: Agent Creation Request")
    print("=" * 80)

    agent_message = """Perfect! I love the Vue 3 + TypeScript stack recommendation. Now I'd like to create the specialized agents to help with this project. Can you set up the core development team agents: Agile Agent for sprint planning, Frontend Agent for Vue 3 development, Backend Agent for Node.js/API work, and Testing Agent for quality assurance?"""

    print(f"📝 Input: {agent_message[:100]}...")
    response = coordinator.process_message(agent_message)
    print(f"📤 Response: {response['response'][:300]}...")
    print(f"📋 Phase: {response['phase']}")
    print(f"🔄 Next Steps: {response['next_steps']}")

    if "agents_created" in response:
        print(f"🤖 Agents Created: {response['agents_created']}")

    print("\n" + "=" * 80)
    print("✅ Phase 10.6 Workflow Test Complete!")
    print("=" * 80)

    # Summary
    print(f"📊 Coordinator State:")
    print(
        f"  - Current Phase: {coordinator.decision_engine.get_conversation_state().current_phase.value}"
    )
    print(
        f"  - Technology Stack: {coordinator.decision_engine.get_conversation_state().technology_stack}"
    )
    print(
        f"  - Created Agents: {coordinator.decision_engine.get_conversation_state().created_agents}"
    )
    print(
        f"  - Conversation History: {len(coordinator.decision_engine.get_conversation_state().conversation_history)} messages"
    )

    return True


if __name__ == "__main__":
    test_phase_10_6_workflow()
