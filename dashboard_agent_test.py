#!/usr/bin/env python3
"""
Test script to directly access agent data from Qdrant
"""

import json
import requests
from datetime import datetime


def get_real_agent_data():
    """Get real agent data from Qdrant database."""
    try:
        # Connect to Qdrant on localhost:6333
        qdrant_url = "http://localhost:6333"

        # Collection name for TaskFlow Pro agents
        collection_name = "project_web_application_TaskFlow Pro_20250911_074404_agents"

        # Get all points from the agents collection
        response = requests.post(
            f"{qdrant_url}/collections/{collection_name}/points/scroll",
            json={"limit": 100, "with_payload": True, "with_vector": False},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            agents = []

            if "result" in data and "points" in data["result"]:
                for point in data["result"]["points"]:
                    payload = point.get("payload", {})

                    # Extract agent information
                    agent_data = {
                        "agent_id": payload.get(
                            "agent_id", f"agent_{point.get('id', 'unknown')}"
                        ),
                        "agent_type": payload.get("role", "unknown"),
                        "name": payload.get("agent_id", "Unknown Agent"),
                        "status": "operational",
                        "last_activity": datetime.now().isoformat(),
                        "capabilities": payload.get("capabilities", []),
                        "project_id": payload.get("project_id", ""),
                        "created_at": payload.get("created_at", ""),
                        "specializations": payload.get("specializations", []),
                        "role": payload.get("role", ""),
                        "system_message": (
                            payload.get("system_message", "")[:100] + "..."
                            if payload.get("system_message", "")
                            else ""
                        ),
                    }
                    agents.append(agent_data)

                print(f"✅ Found {len(agents)} agents in Qdrant:")
                for agent in agents:
                    print(
                        f"  - {agent['agent_id']} ({agent['role']}) - {len(agent['capabilities'])} capabilities"
                    )

                return agents
            else:
                print("⚠️ No agents found in collection")
                return []
        else:
            print(
                f"❌ Failed to query Qdrant: {response.status_code} - {response.text}"
            )
            return []

    except Exception as e:
        print(f"❌ Error accessing Qdrant: {e}")
        return []


if __name__ == "__main__":
    print("🔍 Testing direct Qdrant access for agent data...")
    agents = get_real_agent_data()

    if agents:
        print(f"\n📊 Agent Summary:")
        print(f"Total agents: {len(agents)}")

        # Show first agent details
        if agents:
            first_agent = agents[0]
            print(f"\n📋 Sample Agent Details:")
            print(f"ID: {first_agent['agent_id']}")
            print(f"Role: {first_agent['role']}")
            print(f"Capabilities: {', '.join(first_agent['capabilities'][:3])}...")
            print(f"Project: {first_agent['project_id']}")
    else:
        print("❌ No agent data found")
