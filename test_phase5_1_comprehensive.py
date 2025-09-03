#!/usr/bin/env python3
"""
Comprehensive Phase 5.1 test that runs all Agile Agent functions in a single server session.
"""

import json
import subprocess
import time

def send_mcp_request(process, request):
    """Send MCP request and get response."""
    try:
        request_json = json.dumps(request)
        process.stdin.write(request_json + "\n")
        process.stdin.flush()
        
        # Wait for response
        time.sleep(1)
        
        # Try to read response
        if process.poll() is None:  # Process still running
            try:
                response = process.stdout.readline()
                if response:
                    return json.loads(response.strip())
            except (json.JSONDecodeError, AttributeError):
                pass
        
        return None
    except Exception as e:
        print(f"Error sending request: {e}")
        return None

def log_test(message, level="INFO"):
    """Log test message with timestamp."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def main():
    print("🎯 Comprehensive Phase 5.1: Agile Agent Test")
    print("=" * 60)
    print("Running all tests in a single server session...")
    
    # Start MCP server
    log_test("Starting MCP server...")
    process = subprocess.Popen(
        ["python3", "protocol_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    time.sleep(3)  # Wait for server to start
    
    try:
        test_results = []
        
        # Test 1: Create Agile Project
        log_test("🧪 Test 1: Creating Agile Project")
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "create_agile_project",
                "arguments": {
                    "project_name": "Comprehensive Test Project",
                    "project_type": "scrum",
                    "sprint_length": 14,
                    "team_size": 5
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                project_data = result["structuredContent"]
                if project_data.get("success"):
                    project_id = project_data.get("project_id")
                    log_test(f"✅ Project created: {project_id}")
                    test_results.append(("Project Creation", True))
                else:
                    log_test(f"❌ Project creation failed: {project_data.get('error')}")
                    test_results.append(("Project Creation", False))
                    return
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Project Creation", False))
                return
        else:
            log_test("❌ No response from server")
            test_results.append(("Project Creation", False))
            return
        
        # Test 2: Create User Story
        log_test("🧪 Test 2: Creating User Story")
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "create_user_story",
                "arguments": {
                    "project_id": project_id,
                    "title": "User Authentication Feature",
                    "description": "Implement secure user authentication system",
                    "acceptance_criteria": [
                        "User can register with email and password",
                        "User can login with valid credentials",
                        "User can logout and session is cleared"
                    ],
                    "priority": "high"
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                story_data = result["structuredContent"]
                if story_data.get("success"):
                    story_id = story_data.get("story_id")
                    log_test(f"✅ User story created: {story_id}")
                    test_results.append(("User Story Creation", True))
                else:
                    log_test(f"❌ User story creation failed: {story_data.get('error')}")
                    test_results.append(("User Story Creation", False))
                    return
            else:
                log_test("❌ No structured content in response")
                test_results.append(("User Story Creation", False))
                return
        else:
            log_test("❌ No response from server")
            test_results.append(("User Story Creation", False))
            return
        
        # Test 3: Create Sprint
        log_test("🧪 Test 3: Creating Sprint")
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_sprint",
                "arguments": {
                    "project_id": project_id,
                    "sprint_name": "Sprint 1",
                    "goal": "Complete user authentication feature"
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                sprint_data = result["structuredContent"]
                if sprint_data.get("success"):
                    sprint_id = sprint_data.get("sprint_id")
                    log_test(f"✅ Sprint created: {sprint_id}")
                    test_results.append(("Sprint Creation", True))
                else:
                    log_test(f"❌ Sprint creation failed: {sprint_data.get('error')}")
                    test_results.append(("Sprint Creation", False))
                    return
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Sprint Creation", False))
                return
        else:
            log_test("❌ No response from server")
            test_results.append(("Sprint Creation", False))
            return
        
        # Test 4: Plan Sprint
        log_test("🧪 Test 4: Planning Sprint")
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "plan_sprint",
                "arguments": {
                    "sprint_id": sprint_id,
                    "story_ids": [story_id]
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                plan_data = result["structuredContent"]
                if plan_data.get("success"):
                    log_test("✅ Sprint planned successfully")
                    test_results.append(("Sprint Planning", True))
                else:
                    log_test(f"❌ Sprint planning failed: {plan_data.get('error')}")
                    test_results.append(("Sprint Planning", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Sprint Planning", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("Sprint Planning", False))
        
        # Test 5: Get Project Status
        log_test("🧪 Test 5: Getting Project Status")
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_project_status",
                "arguments": {
                    "project_id": project_id
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                status_data = result["structuredContent"]
                if status_data.get("success"):
                    log_test("✅ Project status retrieved successfully")
                    test_results.append(("Project Status", True))
                else:
                    log_test(f"❌ Project status failed: {status_data.get('error')}")
                    test_results.append(("Project Status", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Project Status", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("Project Status", False))
        
        # Test 6: Get Sprint Burndown
        log_test("🧪 Test 6: Getting Sprint Burndown")
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "get_sprint_burndown",
                "arguments": {
                    "sprint_id": sprint_id
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                burndown_data = result["structuredContent"]
                if burndown_data.get("success"):
                    log_test("✅ Sprint burndown generated successfully")
                    test_results.append(("Sprint Burndown", True))
                else:
                    log_test(f"❌ Sprint burndown failed: {burndown_data.get('error')}")
                    test_results.append(("Sprint Burndown", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Sprint Burndown", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("Sprint Burndown", False))
        
        # Test 7: Calculate Team Velocity
        log_test("🧪 Test 7: Calculating Team Velocity")
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "calculate_team_velocity",
                "arguments": {
                    "project_id": project_id
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                velocity_data = result["structuredContent"]
                if velocity_data.get("success"):
                    log_test("✅ Team velocity calculated successfully")
                    test_results.append(("Team Velocity", True))
                else:
                    # This is expected for a new project with no completed sprints
                    error_msg = velocity_data.get('error', '')
                    if "No completed sprints found" in error_msg:
                        log_test("✅ Team velocity handled correctly (no completed sprints)")
                        test_results.append(("Team Velocity", True))
                    else:
                        log_test(f"❌ Team velocity failed: {error_msg}")
                        test_results.append(("Team Velocity", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Team Velocity", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("Team Velocity", False))
        
        # Test 8: Complete User Story
        log_test("🧪 Test 8: Completing User Story")
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "complete_user_story",
                "arguments": {
                    "story_id": story_id,
                    "actual_hours": 8.5
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                completion_data = result["structuredContent"]
                if completion_data.get("success"):
                    log_test("✅ User story completed successfully")
                    test_results.append(("User Story Completion", True))
                else:
                    log_test(f"❌ User story completion failed: {completion_data.get('error')}")
                    test_results.append(("User Story Completion", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("User Story Completion", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("User Story Completion", False))
        
        # Final Project Status
        log_test("🧪 Test 9: Getting Final Project Status")
        request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "get_project_status",
                "arguments": {
                    "project_id": project_id
                }
            }
        }
        
        response = send_mcp_request(process, request)
        if response and "result" in response:
            result = response["result"]
            if "structuredContent" in result:
                status_data = result["structuredContent"]
                if status_data.get("success"):
                    log_test("✅ Final project status retrieved successfully")
                    test_results.append(("Final Project Status", True))
                else:
                    log_test(f"❌ Final project status failed: {status_data.get('error')}")
                    test_results.append(("Final Project Status", False))
            else:
                log_test("❌ No structured content in response")
                test_results.append(("Final Project Status", False))
        else:
            log_test("❌ No response from server")
            test_results.append(("Final Project Status", False))
        
        # Test Summary
        log_test("=" * 60)
        log_test("📊 PHASE 5.1 COMPREHENSIVE TEST RESULTS")
        log_test("=" * 60)
        
        passed_tests = 0
        total_tests = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            log_test(f"{test_name}: {status}")
            if result:
                passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100
        log_test(f"Overall: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            log_test("🎉 Phase 5.1 Agile Agent tests completed successfully!")
        else:
            log_test("⚠️  Some tests failed. Review the output above.")
        
        return success_rate >= 80
        
    finally:
        # Cleanup
        process.terminate()
        process.wait()
        log_test("✅ Test complete!")

if __name__ == "__main__":
    main()
