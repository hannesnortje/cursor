#!/usr/bin/env python3
"""
Test script for the Simple Decision Engine.

This script tests the hybrid approach with rule-based fallback.
"""

import sys
import os

sys.path.append("src")

from src.llm.simple_decision_engine import SimpleDecisionEngine, ActionType, PDCAPhase
import logging


def test_simple_decision_engine():
    """Test the Simple Decision Engine with various scenarios."""
    print("🔍 Testing Simple Decision Engine...")
    print("=" * 60)

    # Set up logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize decision engine
        print("📦 Initializing Simple Decision Engine...")
        engine = SimpleDecisionEngine()
        print("✅ Simple Decision Engine initialized successfully")

        # Test scenarios
        test_scenarios = [
            {
                "name": "Initial Project Request",
                "message": "I want to start a new project. I have a business need that requires a software solution, but I'm not sure exactly what technology stack or approach would be best. Can you help me figure out what we need to build and how to approach it? I'd like to use your PDCA framework to make sure we plan this properly before we start development. What information do you need from me to get started?",
                "expected_action": ActionType.ASK_QUESTIONS,
            },
            {
                "name": "Vue 3 Project Details",
                "message": "I need to build a project management system for my development team. Here are the details: Project Goals: A comprehensive project management system for a 5-developer team. Target users: Development team members, project managers, and clients. Key features: Task tracking, sprint management, code collaboration, web-based access, user authentication, role-based access control. Current State: Starting from scratch. Main challenges: Need centralized project management, team collaboration, and multi-client tracking. Target State: A fast, responsive web-based system for efficient management of multiple client projects. Implementation Strategy: Team size 5 developers, technical requirements web-based fast and responsive user authentication role-based access control, technology preference Vue 3 with TypeScript. What would you recommend for the complete technology stack and architecture?",
                "expected_action": ActionType.PROVIDE_RECOMMENDATIONS,
            },
            {
                "name": "Agent Creation Request",
                "message": "I'd like to create the core agents for this project. Please set up the specialized agents we need.",
                "expected_action": ActionType.CREATE_AGENTS,
            },
            {
                "name": "Technology Selection Help",
                "message": "I'm not sure which frontend framework to choose. I've heard about Vue 3, React, and Angular. What would you recommend?",
                "expected_action": ActionType.PROVIDE_RECOMMENDATIONS,
            },
            {
                "name": "Simple Project Request",
                "message": "I need help building a web application for my business.",
                "expected_action": ActionType.ASK_QUESTIONS,
            },
        ]

        # Run tests
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{'='*60}")
            print(f"🧪 TEST {i}: {scenario['name']}")
            print(f"{'='*60}")

            print(f"📝 Input: {scenario['message'][:100]}...")

            # Make decision
            decision = engine.make_decision(scenario["message"])

            if decision:
                print(f"📤 Decision: {decision.action_type.value}")
                print(f"🎯 Confidence: {decision.confidence}")
                print(f"💭 Reasoning: {decision.reasoning}")
                print(f"📋 Next Phase: {decision.next_phase.value}")
                print(f"🔧 Parameters: {decision.parameters}")

                if decision.technology_preferences:
                    print(
                        f"🛠️ Technology Preferences: {decision.technology_preferences}"
                    )

                if decision.agent_types_needed:
                    print(f"🤖 Agent Types Needed: {decision.agent_types_needed}")

                # Check if decision matches expected
                if decision.action_type == scenario["expected_action"]:
                    print("✅ Decision matches expected action")
                else:
                    print(
                        f"⚠️ Decision doesn't match expected action: {scenario['expected_action'].value}"
                    )
            else:
                print("❌ Failed to make decision")

        print(f"\n{'='*60}")
        print("✅ All tests completed!")
        print(f"{'='*60}")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_simple_decision_engine()
