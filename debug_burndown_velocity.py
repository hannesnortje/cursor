#!/usr/bin/env python3
"""
Debug script for sprint burndown and team velocity functions.
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

def main():
    print("🔍 Debug: Sprint Burndown and Team Velocity Functions")
    print("=" * 60)
    
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
    
    # Test 1: Sprint Burndown
    print("\n🧪 Test 1: Sprint Burndown Generation")
    print("-" * 40)
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "get_sprint_burndown",
            "arguments": {
                "sprint_id": "test_sprint_123"
            }
        }
    }
    
    print(f"Request: {json.dumps(request, indent=2)}")
    response = send_mcp_request(process, request)
    print(f"Response: {json.dumps(response, indent=2) if response else 'No response'}")
    
    # Test 2: Team Velocity
    print("\n🧪 Test 2: Team Velocity Calculation")
    print("-" * 40)
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "calculate_team_velocity",
            "arguments": {
                "project_id": "test_project_123"
            }
        }
    }
    
    print(f"Request: {json.dumps(request, indent=2)}")
    response = send_mcp_request(process, request)
    print(f"Response: {json.dumps(response, indent=2) if response else 'No response'}")
    
    # Cleanup
    process.terminate()
    process.wait()
    print("\n✅ Debug complete!")

if __name__ == "__main__":
    main()
