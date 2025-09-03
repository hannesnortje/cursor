#!/usr/bin/env python3
"""
Debug script for team velocity function only.
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
    print("🔍 Debug: Team Velocity Function Only")
    print("=" * 50)
    
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
    
    # Test team velocity with a real project ID from our previous test
    project_id = "agile_debug_test_project_20250903"
    print(f"🧪 Testing team velocity for project: {project_id}")
    print("-" * 50)
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "calculate_team_velocity",
            "arguments": {
                "project_id": project_id
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
