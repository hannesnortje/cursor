#!/usr/bin/env python3
"""
Comprehensive Test Suite for Phase 9: Dynamic Agent Ecosystem
Tests all three phases: 9.1 (Qdrant), 9.2 (AutoGen), 9.3 (Advanced Communication)
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Import all Phase 9 tools
from src.mcp_tools.phase9_tools import (
    start_qdrant_container, stop_qdrant_container, get_qdrant_status,
    create_project_database, list_project_databases, switch_project_database,
    get_project_collection_stats, initialize_predetermined_knowledge,
    search_project_knowledge
)

from src.mcp_tools.phase9_2_tools import (
    create_autogen_agent, create_autogen_group_chat, start_autogen_workflow,
    get_autogen_roles, get_autogen_workflows, list_autogen_agents,
    start_autogen_conversation
)

from src.mcp_tools.phase9_3_tools import (
    start_advanced_communication, stop_advanced_communication, send_advanced_message,
    get_communication_analytics, get_queue_status, enable_cross_project_communication,
    share_knowledge_between_projects, get_compression_stats, get_communication_health
)


class Phase9TestSuite:
    """Comprehensive test suite for Phase 9 implementation."""
    
    def __init__(self):
        self.test_results = {
            "phase9_1": {"tests": [], "passed": 0, "failed": 0},
            "phase9_2": {"tests": [], "passed": 0, "failed": 0},
            "phase9_3": {"tests": [], "passed": 0, "failed": 0},
            "integration": {"tests": [], "passed": 0, "failed": 0}
        }
        self.start_time = datetime.now()
    
    def log_test(self, phase: str, test_name: str, success: bool, message: str, details: Dict = None):
        """Log a test result."""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.test_results[phase]["tests"].append(result)
        if success:
            self.test_results[phase]["passed"] += 1
            print(f"✅ {phase.upper()} - {test_name}: {message}")
        else:
            self.test_results[phase]["failed"] += 1
            print(f"❌ {phase.upper()} - {test_name}: {message}")
    
    def test_phase9_1_qdrant(self):
        """Test Phase 9.1: Project-Specific Qdrant Databases."""
        print("\n🔍 Testing Phase 9.1: Project-Specific Qdrant Databases")
        print("=" * 60)
        
        # Test 1: Qdrant Container Status
        try:
            result = get_qdrant_status()
            success = result.get("success", False)
            self.log_test("phase9_1", "Qdrant Status Check", success, 
                         f"Qdrant status: {result.get('status', {}).get('running', 'unknown')}")
        except Exception as e:
            self.log_test("phase9_1", "Qdrant Status Check", False, f"Error: {str(e)}")
        
        # Test 2: Create Project Database
        try:
            result = create_project_database("test-project-1", "Test Project 1")
            success = result.get("success", False)
            self.log_test("phase9_1", "Create Project Database", success, 
                         f"Created project: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_1", "Create Project Database", False, f"Error: {str(e)}")
        
        # Test 3: List Project Databases
        try:
            result = list_project_databases()
            success = result.get("success", False)
            count = result.get("count", 0)
            self.log_test("phase9_1", "List Project Databases", success, 
                         f"Found {count} project databases")
        except Exception as e:
            self.log_test("phase9_1", "List Project Databases", False, f"Error: {str(e)}")
        
        # Test 4: Switch Project Database
        try:
            result = switch_project_database("test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_1", "Switch Project Database", success, 
                         f"Switched to project: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_1", "Switch Project Database", False, f"Error: {str(e)}")
        
        # Test 5: Initialize Predetermined Knowledge
        try:
            result = initialize_predetermined_knowledge("test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_1", "Initialize Predetermined Knowledge", success, 
                         f"Initialized knowledge: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_1", "Initialize Predetermined Knowledge", False, f"Error: {str(e)}")
        
        # Test 6: Search Project Knowledge
        try:
            result = search_project_knowledge("test-project-1", "PDCA methodology")
            success = result.get("success", False)
            count = len(result.get("results", []))
            self.log_test("phase9_1", "Search Project Knowledge", success, 
                         f"Found {count} knowledge results")
        except Exception as e:
            self.log_test("phase9_1", "Search Project Knowledge", False, f"Error: {str(e)}")
        
        # Test 7: Get Collection Stats
        try:
            result = get_project_collection_stats("test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_1", "Get Collection Stats", success, 
                         f"Collection stats: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_1", "Get Collection Stats", False, f"Error: {str(e)}")
    
    def test_phase9_2_autogen(self):
        """Test Phase 9.2: Enhanced AutoGen Integration."""
        print("\n🤖 Testing Phase 9.2: Enhanced AutoGen Integration")
        print("=" * 60)
        
        # Test 1: Get Available Roles
        try:
            result = get_autogen_roles()
            success = result.get("success", False)
            roles = result.get("roles", [])
            self.log_test("phase9_2", "Get Available Roles", success, 
                         f"Found {len(roles)} roles: {', '.join(roles)}")
        except Exception as e:
            self.log_test("phase9_2", "Get Available Roles", False, f"Error: {str(e)}")
        
        # Test 2: Get Available Workflows
        try:
            result = get_autogen_workflows()
            success = result.get("success", False)
            workflows = result.get("workflows", {})
            self.log_test("phase9_2", "Get Available Workflows", success, 
                         f"Found {len(workflows)} workflows: {', '.join(workflows.keys())}")
        except Exception as e:
            self.log_test("phase9_2", "Get Available Workflows", False, f"Error: {str(e)}")
        
        # Test 3: Create AutoGen Agent
        try:
            result = create_autogen_agent("test-coordinator", "coordinator", "test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_2", "Create AutoGen Agent", success, 
                         f"Created agent: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_2", "Create AutoGen Agent", False, f"Error: {str(e)}")
        
        # Test 4: Create Another Agent
        try:
            result = create_autogen_agent("test-developer", "frontend_developer", "test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_2", "Create Second Agent", success, 
                         f"Created second agent: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_2", "Create Second Agent", False, f"Error: {str(e)}")
        
        # Test 5: List AutoGen Agents
        try:
            result = list_autogen_agents()
            success = result.get("success", False)
            agents = result.get("agents", {})
            self.log_test("phase9_2", "List AutoGen Agents", success, 
                         f"Found {len(agents)} agents")
        except Exception as e:
            self.log_test("phase9_2", "List AutoGen Agents", False, f"Error: {str(e)}")
        
        # Test 6: Create Group Chat
        try:
            result = create_autogen_group_chat("test-chat", ["test-coordinator", "test-developer"], "test-project-1")
            success = result.get("success", False)
            self.log_test("phase9_2", "Create Group Chat", success, 
                         f"Created group chat: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_2", "Create Group Chat", False, f"Error: {str(e)}")
        
        # Test 7: Start AutoGen Workflow
        try:
            result = start_autogen_workflow("sprint_planning", "test-project-1", "Let's plan our sprint!")
            success = result.get("success", False)
            self.log_test("phase9_2", "Start AutoGen Workflow", success, 
                         f"Started workflow: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_2", "Start AutoGen Workflow", False, f"Error: {str(e)}")
        
        # Test 8: Start Conversation
        try:
            result = start_autogen_conversation("test-chat", "Let's discuss the project requirements", "sprint_planning")
            success = result.get("success", False)
            self.log_test("phase9_2", "Start Conversation", success, 
                         f"Started conversation: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_2", "Start Conversation", False, f"Error: {str(e)}")
    
    def test_phase9_3_communication(self):
        """Test Phase 9.3: Advanced Communication Features."""
        print("\n📡 Testing Phase 9.3: Advanced Communication Features")
        print("=" * 60)
        
        # Test 1: Start Advanced Communication
        try:
            result = start_advanced_communication()
            success = result.get("success", False)
            self.log_test("phase9_3", "Start Advanced Communication", success, 
                         f"Started system: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_3", "Start Advanced Communication", False, f"Error: {str(e)}")
        
        # Test 2: Send Advanced Message
        try:
            result = send_advanced_message(
                "agent1", "agent2", "agent_communication", 
                "Hello from Phase 9.3 test!", "HIGH", "test-project-1", 
                "test-session", "gzip"
            )
            success = result.get("success", False)
            message_id = result.get("message_id", "unknown")
            self.log_test("phase9_3", "Send Advanced Message", success, 
                         f"Sent message {message_id} with compression")
        except Exception as e:
            self.log_test("phase9_3", "Send Advanced Message", False, f"Error: {str(e)}")
        
        # Test 3: Send Multiple Messages
        try:
            messages_sent = 0
            for i in range(3):
                result = send_advanced_message(
                    f"agent{i}", f"agent{(i+1)%3}", "workflow_coordination", 
                    f"Test message {i+1}", "NORMAL", "test-project-1", 
                    "test-session", "none"
                )
                if result.get("success", False):
                    messages_sent += 1
            
            self.log_test("phase9_3", "Send Multiple Messages", messages_sent > 0, 
                         f"Sent {messages_sent}/3 messages successfully")
        except Exception as e:
            self.log_test("phase9_3", "Send Multiple Messages", False, f"Error: {str(e)}")
        
        # Test 4: Get Communication Analytics
        try:
            result = get_communication_analytics()
            success = result.get("success", False)
            analytics = result.get("analytics", {})
            health_score = analytics.get("health_score", 0)
            self.log_test("phase9_3", "Get Communication Analytics", success, 
                         f"Health score: {health_score:.1f}, Analytics retrieved")
        except Exception as e:
            self.log_test("phase9_3", "Get Communication Analytics", False, f"Error: {str(e)}")
        
        # Test 5: Get Queue Status
        try:
            result = get_queue_status()
            success = result.get("success", False)
            queue_status = result.get("queue_status", {})
            total_queued = queue_status.get("total_queued", 0)
            self.log_test("phase9_3", "Get Queue Status", success, 
                         f"Queue status: {total_queued} messages queued")
        except Exception as e:
            self.log_test("phase9_3", "Get Queue Status", False, f"Error: {str(e)}")
        
        # Test 6: Enable Cross-Project Communication
        try:
            result = enable_cross_project_communication("test-project-1", "test-project-2")
            success = result.get("success", False)
            self.log_test("phase9_3", "Enable Cross-Project Communication", success, 
                         f"Enabled communication: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_3", "Enable Cross-Project Communication", False, f"Error: {str(e)}")
        
        # Test 7: Share Knowledge Between Projects
        try:
            knowledge = {
                "type": "best_practice",
                "content": "Use TypeScript for better type safety",
                "category": "frontend",
                "priority": "high"
            }
            result = share_knowledge_between_projects("test-project-1", "test-project-2", knowledge)
            success = result.get("success", False)
            self.log_test("phase9_3", "Share Knowledge Between Projects", success, 
                         f"Shared knowledge: {result.get('message', 'Unknown')}")
        except Exception as e:
            self.log_test("phase9_3", "Share Knowledge Between Projects", False, f"Error: {str(e)}")
        
        # Test 8: Get Compression Stats
        try:
            result = get_compression_stats()
            success = result.get("success", False)
            compression_stats = result.get("compression_stats", {})
            self.log_test("phase9_3", "Get Compression Stats", success, 
                         f"Compression stats retrieved: {len(compression_stats)} algorithms")
        except Exception as e:
            self.log_test("phase9_3", "Get Compression Stats", False, f"Error: {str(e)}")
        
        # Test 9: Get Communication Health
        try:
            result = get_communication_health()
            success = result.get("success", False)
            health_score = result.get("health_score", 0)
            is_healthy = result.get("is_healthy", False)
            self.log_test("phase9_3", "Get Communication Health", success, 
                         f"Health: {health_score:.1f} ({'Healthy' if is_healthy else 'Degraded'})")
        except Exception as e:
            self.log_test("phase9_3", "Get Communication Health", False, f"Error: {str(e)}")
    
    def test_integration(self):
        """Test integration between all Phase 9 components."""
        print("\n🔗 Testing Phase 9 Integration")
        print("=" * 60)
        
        # Test 1: Create Project with Knowledge
        try:
            # Create project
            create_result = create_project_database("integration-test", "Integration Test Project")
            if create_result.get("success", False):
                # Initialize knowledge
                knowledge_result = initialize_predetermined_knowledge("integration-test")
                if knowledge_result.get("success", False):
                    # Create AutoGen agents for this project
                    agent1_result = create_autogen_agent("integration-coordinator", "coordinator", "integration-test")
                    agent2_result = create_autogen_agent("integration-tester", "testing_specialist", "integration-test")
                    
                    if agent1_result.get("success", False) and agent2_result.get("success", False):
                        self.log_test("integration", "Project + Knowledge + Agents", True, 
                                     "Successfully integrated Qdrant, knowledge, and AutoGen agents")
                    else:
                        self.log_test("integration", "Project + Knowledge + Agents", False, 
                                     "Failed to create AutoGen agents")
                else:
                    self.log_test("integration", "Project + Knowledge + Agents", False, 
                                 "Failed to initialize knowledge")
            else:
                self.log_test("integration", "Project + Knowledge + Agents", False, 
                             "Failed to create project")
        except Exception as e:
            self.log_test("integration", "Project + Knowledge + Agents", False, f"Error: {str(e)}")
        
        # Test 2: Cross-Project Knowledge Sharing
        try:
            # Create second project
            create_result2 = create_project_database("integration-test-2", "Integration Test Project 2")
            if create_result2.get("success", False):
                # Enable cross-project communication
                comm_result = enable_cross_project_communication("integration-test", "integration-test-2")
                if comm_result.get("success", False):
                    # Share knowledge
                    knowledge = {
                        "type": "integration_test",
                        "content": "This is a test of cross-project knowledge sharing",
                        "source": "integration-test",
                        "timestamp": datetime.now().isoformat()
                    }
                    share_result = share_knowledge_between_projects("integration-test", "integration-test-2", knowledge)
                    if share_result.get("success", False):
                        self.log_test("integration", "Cross-Project Knowledge Sharing", True, 
                                     "Successfully shared knowledge between projects")
                    else:
                        self.log_test("integration", "Cross-Project Knowledge Sharing", False, 
                                     "Failed to share knowledge")
                else:
                    self.log_test("integration", "Cross-Project Knowledge Sharing", False, 
                                 "Failed to enable cross-project communication")
            else:
                self.log_test("integration", "Cross-Project Knowledge Sharing", False, 
                             "Failed to create second project")
        except Exception as e:
            self.log_test("integration", "Cross-Project Knowledge Sharing", False, f"Error: {str(e)}")
        
        # Test 3: End-to-End Workflow
        try:
            # Start advanced communication
            comm_start = start_advanced_communication()
            if comm_start.get("success", False):
                # Send workflow coordination message
                workflow_msg = send_advanced_message(
                    "integration-coordinator", "integration-tester", "workflow_coordination",
                    "Let's start our integration testing workflow", "HIGH", "integration-test",
                    "integration-session", "gzip"
                )
                if workflow_msg.get("success", False):
                    # Start AutoGen workflow
                    autogen_workflow = start_autogen_workflow("code_review", "integration-test", "Review the integration test code")
                    if autogen_workflow.get("success", False):
                        self.log_test("integration", "End-to-End Workflow", True, 
                                     "Successfully executed complete workflow with all components")
                    else:
                        self.log_test("integration", "End-to-End Workflow", False, 
                                     "Failed to start AutoGen workflow")
                else:
                    self.log_test("integration", "End-to-End Workflow", False, 
                                 "Failed to send workflow message")
            else:
                self.log_test("integration", "End-to-End Workflow", False, 
                             "Failed to start advanced communication")
        except Exception as e:
            self.log_test("integration", "End-to-End Workflow", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all Phase 9 tests."""
        print("🚀 Starting Comprehensive Phase 9 Test Suite")
        print("=" * 80)
        print(f"Test started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test phases
        self.test_phase9_1_qdrant()
        self.test_phase9_2_autogen()
        self.test_phase9_3_communication()
        self.test_integration()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary report."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 PHASE 9 COMPREHENSIVE TEST SUMMARY")
        print("=" * 80)
        
        total_passed = 0
        total_failed = 0
        
        for phase, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total = passed + failed
            
            total_passed += passed
            total_failed += failed
            
            success_rate = (passed / total * 100) if total > 0 else 0
            
            print(f"\n{phase.upper()}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        overall_total = total_passed + total_failed
        overall_success_rate = (total_passed / overall_total * 100) if overall_total > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📈 Overall Success Rate: {overall_success_rate:.1f}%")
        print(f"  ⏱️  Total Duration: {duration:.2f} seconds")
        
        # Status assessment
        if overall_success_rate >= 90:
            status = "🟢 EXCELLENT"
        elif overall_success_rate >= 80:
            status = "🟡 GOOD"
        elif overall_success_rate >= 70:
            status = "🟠 FAIR"
        else:
            status = "🔴 NEEDS IMPROVEMENT"
        
        print(f"\n🏆 PHASE 9 STATUS: {status}")
        
        # Save detailed results
        self.save_results()
    
    def save_results(self):
        """Save detailed test results to file."""
        results_file = f"phase9_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        detailed_results = {
            "test_suite": "Phase 9 Comprehensive Test",
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "results": self.test_results
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {results_file}")


def main():
    """Run the comprehensive Phase 9 test suite."""
    test_suite = Phase9TestSuite()
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
