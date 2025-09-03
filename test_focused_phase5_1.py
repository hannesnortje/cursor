#!/usr/bin/env python3
"""
Focused test for Phase 5.1 failing functions with real project/sprint IDs.
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

def create_test_project(process):
    """Create a test agile project."""
    print("🏗️  Creating test agile project...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "create_agile_project",
            "arguments": {
                "project_name": "Debug Test Project",
                "project_type": "scrum",
                "sprint_length": 14,
                "team_size": 3
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
                print(f"✅ Project created: {project_id}")
                return project_id
    
    print("❌ Failed to create project")
    return None

def create_test_sprint(process, project_id):
    """Create a test sprint."""
    print(f"🏃 Creating test sprint for project {project_id}...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_sprint",
            "arguments": {
                "project_id": project_id,
                "sprint_name": "Debug Sprint 1",
                "goal": "Test sprint burndown functionality"
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
                print(f"✅ Sprint created: {sprint_id}")
                return sprint_id
    
    print("❌ Failed to create sprint")
    return None

def test_sprint_burndown(process, sprint_id):
    """Test sprint burndown with real sprint ID."""
    print(f"📊 Testing sprint burndown for sprint {sprint_id}...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
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
                print("✅ Sprint burndown generated successfully!")
                print(f"   Data: {json.dumps(burndown_data, indent=2)}")
                return True
            else:
                print(f"❌ Burndown failed: {burndown_data.get('error')}")
                return False
        else:
            print("❌ No structured content in response")
            return False
    else:
        print("❌ No response from server")
        return False

def test_team_velocity(process, project_id):
    """Test team velocity with real project ID."""
    print(f"🚀 Testing team velocity for project {project_id}...")
    
    request = {
        "jsonrpc": "2.0",
        "id": 4,
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
                print("✅ Team velocity calculated successfully!")
                print(f"   Data: {json.dumps(velocity_data, indent=2)}")
                return True
            else:
                error_msg = velocity_data.get('error', '')
                if "No completed sprints found" in error_msg:
                    print("✅ Team velocity handled correctly (no completed sprints)")
                    return True
                else:
                    print(f"❌ Velocity calculation failed: {error_msg}")
                    return False
        else:
            print("❌ No structured content in response")
            return False
    else:
        print("❌ No response from server")
        return False

def main():
    print("🎯 Focused Phase 5.1 Test: Sprint Burndown & Team Velocity")
    print("=" * 65)
    
    # Start MCP server
    print("Starting MCP server...")
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
        # Step 1: Create project
        project_id = create_test_project(process)
        if not project_id:
            print("❌ Cannot continue without project ID")
            return
        
        # Step 2: Create sprint
        sprint_id = create_test_sprint(process, project_id)
        if not sprint_id:
            print("❌ Cannot continue without sprint ID")
            return
        
        # Step 3: Test sprint burndown
        print("\n" + "="*50)
        burndown_success = test_sprint_burndown(process, sprint_id)
        
        # Step 4: Test team velocity
        print("\n" + "="*50)
        velocity_success = test_team_velocity(process, project_id)
        
        # Results
        print("\n" + "="*50)
        print("📊 TEST RESULTS:")
        print(f"   Sprint Burndown: {'✅ PASS' if burndown_success else '❌ FAIL'}")
        print(f"   Team Velocity: {'✅ PASS' if velocity_success else '❌ FAIL'}")
        
        if burndown_success and velocity_success:
            print("🎉 All tests passed! Phase 5.1 is ready for completion.")
        else:
            print("⚠️  Some tests failed. Need to investigate further.")
            
    finally:
        # Cleanup
        process.terminate()
        process.wait()
        print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
