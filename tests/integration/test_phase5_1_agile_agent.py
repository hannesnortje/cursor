#!/usr/bin/env python3
"""
Test script for Phase 5.1: Agile Agent Implementation
Tests all Agile Agent functionality including project creation, user stories, sprints, and metrics.
"""

import json
import subprocess
import time
import sys
from typing import Dict, Any, Optional

# Test configuration
TEST_PROJECT_NAME = "Test Agile Project"
TEST_SPRINT_NAME = "Sprint 1"
TEST_STORY_TITLE = "User Authentication Feature"
TEST_STORY_DESCRIPTION = (
    "Implement secure user authentication system with login/logout functionality"
)
TEST_ACCEPTANCE_CRITERIA = [
    "User can register with email and password",
    "User can login with valid credentials",
    "User can logout and session is cleared",
    "Password requirements are enforced",
]


def log_test(message: str, level: str = "INFO"):
    """Log test message with timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def send_mcp_request(process, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Send an MCP request to the server process."""
    try:
        request_json = json.dumps(request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()

        response = process.stdout.readline()
        if response:
            return json.loads(response.strip())
        else:
            return None
    except Exception as e:
        log_test(f"Error sending MCP request: {e}", "ERROR")
        return None


def test_agile_project_creation(process) -> Optional[str]:
    """Test creating an agile project."""
    log_test("Testing agile project creation...")

    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_agile_project",
            "arguments": {
                "project_name": TEST_PROJECT_NAME,
                "project_type": "scrum",
                "sprint_length": 14,
                "team_size": 5,
            },
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            project_data = result["structuredContent"]
            if project_data.get("success"):
                project_id = project_data.get("project_id")
                log_test(f"✅ Agile project created successfully: {project_id}")
                return project_id
            else:
                log_test(
                    f"❌ Failed to create agile project: {project_data.get('error')}",
                    "FAIL",
                )
                return None
        else:
            log_test("❌ No structured content in response", "FAIL")
            return None
    else:
        log_test("❌ No response from server", "FAIL")
        return None


def test_user_story_creation(process, project_id: str) -> Optional[str]:
    """Test creating a user story."""
    log_test("Testing user story creation...")

    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_user_story",
            "arguments": {
                "project_id": project_id,
                "title": TEST_STORY_TITLE,
                "description": TEST_STORY_DESCRIPTION,
                "acceptance_criteria": TEST_ACCEPTANCE_CRITERIA,
                "priority": "high",
            },
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            story_data = result["structuredContent"]
            if story_data.get("success"):
                story_id = story_data.get("story_id")
                story_points = story_data.get("user_story", {}).get("story_points")
                log_test(
                    f"✅ User story created successfully: {story_id} ({story_points} points)"
                )
                return story_id
            else:
                log_test(
                    f"❌ Failed to create user story: {story_data.get('error')}", "FAIL"
                )
                return None
        else:
            log_test("❌ No structured content in response", "FAIL")
            return None
    else:
        log_test("❌ No response from server", "FAIL")
        return None


def test_sprint_creation(process, project_id: str) -> Optional[str]:
    """Test creating a sprint."""
    log_test("Testing sprint creation...")

    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "create_sprint",
            "arguments": {
                "project_id": project_id,
                "sprint_name": TEST_SPRINT_NAME,
                "goal": "Complete user authentication feature",
            },
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            sprint_data = result["structuredContent"]
            if sprint_data.get("success"):
                sprint_id = sprint_data.get("sprint_id")
                log_test(f"✅ Sprint created successfully: {sprint_id}")
                return sprint_id
            else:
                log_test(
                    f"❌ Failed to create sprint: {sprint_data.get('error')}", "FAIL"
                )
                return None
        else:
            log_test("❌ No structured content in response", "FAIL")
            return None
    else:
        log_test("❌ No response from server", "FAIL")
        return None


def test_sprint_planning(process, sprint_id: str, story_id: str):
    """Test planning a sprint with user stories."""
    log_test("Testing sprint planning...")

    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "plan_sprint",
            "arguments": {"sprint_id": sprint_id, "story_ids": [story_id]},
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            plan_data = result["structuredContent"]
            if plan_data.get("success"):
                planned_stories = plan_data.get("planned_stories")
                total_points = plan_data.get("total_points")
                log_test(
                    f"✅ Sprint planned successfully: {planned_stories} stories ({total_points} points)"
                )
                return True
            else:
                log_test(f"❌ Failed to plan sprint: {plan_data.get('error')}", "FAIL")
                return False
        else:
            log_test("❌ No structured content in response", "FAIL")
            return False
    else:
        log_test("❌ No response from server", "FAIL")
        return False


def test_project_status(process, project_id: str):
    """Test getting project status."""
    log_test("Testing project status retrieval...")

    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "get_project_status",
            "arguments": {"project_id": project_id},
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            status_data = result["structuredContent"]
            if status_data.get("success"):
                metrics = status_data.get("metrics", {})
                total_stories = metrics.get("total_stories")
                total_points = metrics.get("total_story_points")
                log_test(
                    f"✅ Project status retrieved: {total_stories} stories, {total_points} points"
                )
                return True
            else:
                log_test(
                    f"❌ Failed to get project status: {status_data.get('error')}",
                    "FAIL",
                )
                return False
        else:
            log_test("❌ No structured content in response", "FAIL")
            return False
    else:
        log_test("❌ No response from server", "FAIL")
        return False


def test_sprint_burndown(process, sprint_id: str):
    """Test generating sprint burndown data."""
    log_test("Testing sprint burndown generation...")

    request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "get_sprint_burndown",
            "arguments": {"sprint_id": sprint_id},
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            burndown_data = result["structuredContent"]
            if burndown_data.get("success"):
                total_points = burndown_data.get("total_points")
                completion_percentage = burndown_data.get("completion_percentage")
                log_test(
                    f"✅ Sprint burndown generated: {total_points} points, {completion_percentage}% complete"
                )
                return True
            else:
                log_test(
                    f"❌ Failed to generate burndown: {burndown_data.get('error')}",
                    "FAIL",
                )
                return False
        else:
            log_test("❌ No structured content in response", "FAIL")
            return False
    else:
        log_test("❌ No response from server", "FAIL")
        return False


def test_team_velocity(process, project_id: str):
    """Test team velocity calculation."""
    log_test("Testing team velocity calculation...")

    request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "calculate_team_velocity",
            "arguments": {"project_id": project_id},
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            velocity_data = result["structuredContent"]
            if velocity_data.get("success"):
                log_test(
                    "✅ Team velocity calculated (expected: no completed sprints yet)"
                )
                return True
            else:
                # This is expected for a new project with no completed sprints
                error_msg = velocity_data.get("error", "")
                if "No completed sprints found" in error_msg:
                    log_test(
                        "✅ Team velocity calculation handled correctly (no completed sprints)"
                    )
                    return True
                else:
                    log_test(
                        f"❌ Unexpected error in velocity calculation: {error_msg}",
                        "FAIL",
                    )
                    return False
        else:
            log_test("❌ No structured content in response", "FAIL")
            return False
    else:
        log_test("❌ No response from server", "FAIL")
        return False


def test_user_story_completion(process, story_id: str):
    """Test completing a user story."""
    log_test("Testing user story completion...")

    request = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "complete_user_story",
            "arguments": {"story_id": story_id, "actual_hours": 8.5},
        },
    }

    response = send_mcp_request(process, request)
    if response and "result" in response:
        result = response["result"]
        if "structuredContent" in result:
            completion_data = result["structuredContent"]
            if completion_data.get("success"):
                completed_points = completion_data.get("completed_points")
                log_test(
                    f"✅ User story completed successfully: {completed_points} points"
                )
                return True
            else:
                log_test(
                    f"❌ Failed to complete user story: {completion_data.get('error')}",
                    "FAIL",
                )
                return False
        else:
            log_test("❌ No structured content in response", "FAIL")
            return False
    else:
        log_test("❌ No response from server", "FAIL")
        return False


def run_agile_agent_tests():
    """Run all Agile Agent tests."""
    log_test("🚀 Starting Phase 5.1: Agile Agent Tests")
    log_test("=" * 60)

    # Start MCP server
    log_test("Starting MCP server...")
    try:
        process = subprocess.Popen(
            ["python3", "protocol_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Wait for server to start
        time.sleep(2)

        # Test results tracking
        test_results = []

        # Test 1: Project Creation
        project_id = test_agile_project_creation(process)
        test_results.append(("Project Creation", project_id is not None))

        if not project_id:
            log_test("❌ Cannot continue tests without project ID", "FAIL")
            process.terminate()
            return False

        # Test 2: User Story Creation
        story_id = test_user_story_creation(process, project_id)
        test_results.append(("User Story Creation", story_id is not None))

        if not story_id:
            log_test("❌ Cannot continue tests without story ID", "FAIL")
            process.terminate()
            return False

        # Test 3: Sprint Creation
        sprint_id = test_sprint_creation(process, project_id)
        test_results.append(("Sprint Creation", sprint_id is not None))

        if not sprint_id:
            log_test("❌ Cannot continue tests without sprint ID", "FAIL")
            process.terminate()
            return False

        # Test 4: Sprint Planning
        sprint_planned = test_sprint_planning(process, sprint_id, story_id)
        test_results.append(("Sprint Planning", sprint_planned))

        # Test 5: Project Status
        status_retrieved = test_project_status(process, project_id)
        test_results.append(("Project Status", status_retrieved))

        # Test 6: Sprint Burndown
        burndown_generated = test_sprint_burndown(process, sprint_id)
        test_results.append(("Sprint Burndown", burndown_generated))

        # Test 7: Team Velocity
        velocity_calculated = test_team_velocity(process, project_id)
        test_results.append(("Team Velocity", velocity_calculated))

        # Test 8: User Story Completion
        story_completed = test_user_story_completion(process, story_id)
        test_results.append(("User Story Completion", story_completed))

        # Final project status after completion
        log_test("Getting final project status...")
        final_status = test_project_status(process, project_id)
        test_results.append(("Final Project Status", final_status))

        # Test summary
        log_test("=" * 60)
        log_test("📊 PHASE 5.1 TEST RESULTS")
        log_test("=" * 60)

        passed_tests = 0
        total_tests = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            log_test(f"{test_name}: {status}")
            if result:
                passed_tests += 1

        success_rate = (passed_tests / total_tests) * 100
        log_test(
            f"Overall: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)"
        )

        if success_rate >= 80:
            log_test("🎉 Phase 5.1 Agile Agent tests completed successfully!")
        else:
            log_test("⚠️  Some tests failed. Review the output above.")

        # Cleanup
        process.terminate()
        return success_rate >= 80

    except Exception as e:
        log_test(f"❌ Test execution failed: {e}", "ERROR")
        return False


if __name__ == "__main__":
    success = run_agile_agent_tests()
    sys.exit(0 if success else 1)
