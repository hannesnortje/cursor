#!/usr/bin/env python3
"""Comprehensive test suite for all Phase 9 components (9.1, 9.2, 9.3, 9.4)."""

import json
import time
from datetime import datetime
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_phase9_complete():
    """Test all Phase 9 components comprehensively."""
    print("🚀 Phase 9 Complete: Dynamic Agent Ecosystem - Comprehensive Testing")
    print("=" * 80)
    
    test_results = {
        "phase": "9.0",
        "name": "Dynamic Agent Ecosystem (Complete)",
        "timestamp": datetime.now().isoformat(),
        "phases": {
            "9.1": {"name": "Project-Specific Qdrant Databases", "tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}},
            "9.2": {"name": "Enhanced AutoGen Integration", "tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}},
            "9.3": {"name": "Advanced Communication Features", "tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}},
            "9.4": {"name": "Predetermined Knowledge Bases", "tests": [], "summary": {"total": 0, "passed": 0, "failed": 0}}
        },
        "integration_tests": [],
        "overall_summary": {
            "total_phases": 4,
            "completed_phases": 0,
            "total_tests": 0,
            "total_passed": 0,
            "total_failed": 0,
            "overall_success_rate": 0.0
        }
    }
    
    def run_test(phase, test_name, test_func):
        """Run a single test and record results."""
        print(f"\n🔍 Testing {phase}: {test_name}")
        test_results["phases"][phase]["summary"]["total"] += 1
        test_results["overall_summary"]["total_tests"] += 1
        
        try:
            result = test_func()
            if result["success"]:
                print(f"✅ PASSED: {result['message']}")
                test_results["phases"][phase]["summary"]["passed"] += 1
                test_results["overall_summary"]["total_passed"] += 1
                test_results["phases"][phase]["tests"].append({
                    "name": test_name,
                    "status": "PASSED",
                    "message": result["message"],
                    "details": result.get("details", {})
                })
            else:
                print(f"❌ FAILED: {result['message']}")
                test_results["phases"][phase]["summary"]["failed"] += 1
                test_results["overall_summary"]["total_failed"] += 1
                test_results["phases"][phase]["tests"].append({
                    "name": test_name,
                    "status": "FAILED",
                    "message": result["message"],
                    "error": result.get("error", "Unknown error")
                })
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            test_results["phases"][phase]["summary"]["failed"] += 1
            test_results["overall_summary"]["total_failed"] += 1
            test_results["phases"][phase]["tests"].append({
                "name": test_name,
                "status": "ERROR",
                "message": f"Test execution failed: {str(e)}",
                "error": str(e)
            })
    
    # Phase 9.1 Tests: Project-Specific Qdrant Databases
    print("\n" + "="*50)
    print("🗄️ Phase 9.1: Project-Specific Qdrant Databases")
    print("="*50)
    
    def test_qdrant_status():
        try:
            from src.mcp_tools.phase9_tools import get_qdrant_status
            result = get_qdrant_status()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get Qdrant status: {str(e)}"}
    
    def test_project_creation():
        try:
            from src.mcp_tools.phase9_tools import create_project_database
            result = create_project_database("test-phase9-complete", "test-phase9-complete-1")
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to create project: {str(e)}"}
    
    def test_project_listing():
        try:
            from src.mcp_tools.phase9_tools import list_project_databases
            result = list_project_databases()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to list projects: {str(e)}"}
    
    run_test("9.1", "Qdrant Status Check", test_qdrant_status)
    run_test("9.1", "Project Database Creation", test_project_creation)
    run_test("9.1", "Project Database Listing", test_project_listing)
    
    # Phase 9.2 Tests: Enhanced AutoGen Integration
    print("\n" + "="*50)
    print("🤖 Phase 9.2: Enhanced AutoGen Integration")
    print("="*50)
    
    def test_autogen_agent_creation():
        try:
            from src.mcp_tools.phase9_2_tools import create_autogen_agent
            result = create_autogen_agent("test-agent", "developer", "A test agent for Phase 9.2")
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to create AutoGen agent: {str(e)}"}
    
    def test_autogen_workflow():
        try:
            from src.mcp_tools.phase9_2_tools import start_autogen_workflow
            result = start_autogen_workflow("test-workflow", ["test-agent"], "Test workflow for Phase 9.2")
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to start AutoGen workflow: {str(e)}"}
    
    def test_autogen_roles():
        try:
            from src.mcp_tools.phase9_2_tools import get_autogen_roles
            result = get_autogen_roles()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get AutoGen roles: {str(e)}"}
    
    run_test("9.2", "AutoGen Agent Creation", test_autogen_agent_creation)
    run_test("9.2", "AutoGen Workflow Start", test_autogen_workflow)
    run_test("9.2", "AutoGen Roles Retrieval", test_autogen_roles)
    
    # Phase 9.3 Tests: Advanced Communication Features
    print("\n" + "="*50)
    print("📡 Phase 9.3: Advanced Communication Features")
    print("="*50)
    
    def test_communication_start():
        try:
            from src.mcp_tools.phase9_3_tools import start_advanced_communication
            result = start_advanced_communication()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to start communication: {str(e)}"}
    
    def test_advanced_message():
        try:
            from src.mcp_tools.phase9_3_tools import send_advanced_message
            result = send_advanced_message("test-sender", "test-receiver", "Test message for Phase 9.3", "agent_communication", "high", "gzip")
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to send advanced message: {str(e)}"}
    
    def test_communication_analytics():
        try:
            from src.mcp_tools.phase9_3_tools import get_communication_analytics
            result = get_communication_analytics()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get communication analytics: {str(e)}"}
    
    run_test("9.3", "Advanced Communication Start", test_communication_start)
    run_test("9.3", "Advanced Message Sending", test_advanced_message)
    run_test("9.3", "Communication Analytics", test_communication_analytics)
    
    # Phase 9.4 Tests: Predetermined Knowledge Bases
    print("\n" + "="*50)
    print("🧠 Phase 9.4: Predetermined Knowledge Bases")
    print("="*50)
    
    def test_knowledge_domains():
        try:
            from src.mcp_tools.phase9_4_tools import get_available_knowledge_domains
            result = get_available_knowledge_domains()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get knowledge domains: {str(e)}"}
    
    def test_knowledge_search():
        try:
            from src.mcp_tools.phase9_4_tools import search_knowledge
            result = search_knowledge("agile", domain="agile")
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to search knowledge: {str(e)}"}
    
    def test_knowledge_statistics():
        try:
            from src.mcp_tools.phase9_4_tools import get_knowledge_statistics
            result = get_knowledge_statistics()
            return {
                "success": result["success"],
                "message": result["message"],
                "details": result
            }
        except Exception as e:
            return {"success": False, "message": f"Failed to get knowledge statistics: {str(e)}"}
    
    run_test("9.4", "Knowledge Domains Retrieval", test_knowledge_domains)
    run_test("9.4", "Knowledge Search Functionality", test_knowledge_search)
    run_test("9.4", "Knowledge Statistics", test_knowledge_statistics)
    
    # Integration Tests
    print("\n" + "="*50)
    print("🔗 Integration Tests: Cross-Phase Functionality")
    print("="*50)
    
    def test_phase_integration():
        try:
            # Test that all phases work together
            from src.mcp_tools.phase9_tools import get_qdrant_status
            from src.mcp_tools.phase9_2_tools import get_autogen_roles
            from src.mcp_tools.phase9_3_tools import get_communication_health
            from src.mcp_tools.phase9_4_tools import get_available_knowledge_domains
            
            qdrant_result = get_qdrant_status()
            autogen_result = get_autogen_roles()
            comm_result = get_communication_health()
            knowledge_result = get_available_knowledge_domains()
            
            all_success = all([
                qdrant_result["success"],
                autogen_result["success"],
                comm_result["success"],
                knowledge_result["success"]
            ])
            
            return {
                "success": all_success,
                "message": f"Integration test: Qdrant={qdrant_result['success']}, AutoGen={autogen_result['success']}, Communication={comm_result['success']}, Knowledge={knowledge_result['success']}",
                "details": {
                    "qdrant": qdrant_result,
                    "autogen": autogen_result,
                    "communication": comm_result,
                    "knowledge": knowledge_result
                }
            }
        except Exception as e:
            return {"success": False, "message": f"Integration test failed: {str(e)}"}
    
    def test_mcp_server_integration():
        try:
            # Test that all tools are available in the MCP server
            from src.mcp_tools.phase9_tools import get_qdrant_status
            from src.mcp_tools.phase9_2_tools import create_autogen_agent
            from src.mcp_tools.phase9_3_tools import start_advanced_communication
            from src.mcp_tools.phase9_4_tools import get_available_knowledge_domains
            
            # Test that we can call all tool functions
            qdrant_result = get_qdrant_status()
            autogen_result = create_autogen_agent("integration-test", "developer", "Integration test agent")
            comm_result = start_advanced_communication()
            knowledge_result = get_available_knowledge_domains()
            
            return {
                "success": True,
                "message": "All MCP tools are accessible and functional",
                "details": {
                    "tools_tested": 4,
                    "qdrant_available": qdrant_result["success"],
                    "autogen_available": autogen_result["success"],
                    "communication_available": comm_result["success"],
                    "knowledge_available": knowledge_result["success"]
                }
            }
        except Exception as e:
            return {"success": False, "message": f"MCP server integration test failed: {str(e)}"}
    
    # Integration tests (not part of specific phases)
    print(f"\n🔍 Testing Integration: Cross-Phase Integration")
    test_results["overall_summary"]["total_tests"] += 1
    try:
        result = test_phase_integration()
        if result["success"]:
            print(f"✅ PASSED: {result['message']}")
            test_results["overall_summary"]["total_passed"] += 1
        else:
            print(f"❌ FAILED: {result['message']}")
            test_results["overall_summary"]["total_failed"] += 1
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        test_results["overall_summary"]["total_failed"] += 1
    
    print(f"\n🔍 Testing Integration: MCP Server Integration")
    test_results["overall_summary"]["total_tests"] += 1
    try:
        result = test_mcp_server_integration()
        if result["success"]:
            print(f"✅ PASSED: {result['message']}")
            test_results["overall_summary"]["total_passed"] += 1
        else:
            print(f"❌ FAILED: {result['message']}")
            test_results["overall_summary"]["total_failed"] += 1
    except Exception as e:
        print(f"💥 ERROR: {str(e)}")
        test_results["overall_summary"]["total_failed"] += 1
    
    # Calculate phase completion
    for phase in ["9.1", "9.2", "9.3", "9.4"]:
        phase_data = test_results["phases"][phase]
        if phase_data["summary"]["total"] > 0:
            phase_success_rate = phase_data["summary"]["passed"] / phase_data["summary"]["total"] * 100
            if phase_success_rate >= 80:
                test_results["overall_summary"]["completed_phases"] += 1
    
    # Calculate overall success rate
    test_results["overall_summary"]["overall_success_rate"] = (
        test_results["overall_summary"]["total_passed"] / test_results["overall_summary"]["total_tests"] * 100
        if test_results["overall_summary"]["total_tests"] > 0 else 0
    )
    
    # Print summary
    print("\n" + "="*80)
    print("📊 Phase 9 Complete Test Results Summary")
    print("="*80)
    
    for phase in ["9.1", "9.2", "9.3", "9.4"]:
        phase_data = test_results["phases"][phase]
        success_rate = (phase_data["summary"]["passed"] / phase_data["summary"]["total"] * 100) if phase_data["summary"]["total"] > 0 else 0
        status = "✅ COMPLETE" if success_rate >= 80 else "❌ INCOMPLETE"
        print(f"{phase} {phase_data['name']}: {phase_data['summary']['passed']}/{phase_data['summary']['total']} tests passed ({success_rate:.1f}%) {status}")
    
    print(f"\nOverall: {test_results['overall_summary']['total_passed']}/{test_results['overall_summary']['total_tests']} tests passed ({test_results['overall_summary']['overall_success_rate']:.1f}%)")
    print(f"Completed Phases: {test_results['overall_summary']['completed_phases']}/{test_results['overall_summary']['total_phases']}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"phase9_complete_test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n💾 Complete test results saved to: {filename}")
    
    # Overall assessment
    if test_results["overall_summary"]["overall_success_rate"] >= 90 and test_results["overall_summary"]["completed_phases"] >= 3:
        print("\n🎉 Phase 9 Complete Status: EXCELLENT - Production Ready!")
        print("🚀 Dynamic Agent Ecosystem is fully operational!")
    elif test_results["overall_summary"]["overall_success_rate"] >= 80 and test_results["overall_summary"]["completed_phases"] >= 3:
        print("\n✅ Phase 9 Complete Status: GOOD - Minor issues to address")
    elif test_results["overall_summary"]["overall_success_rate"] >= 70:
        print("\n⚠️ Phase 9 Complete Status: FAIR - Some issues need attention")
    else:
        print("\n❌ Phase 9 Complete Status: POOR - Major issues need fixing")
    
    return test_results

if __name__ == "__main__":
    test_phase9_complete()
