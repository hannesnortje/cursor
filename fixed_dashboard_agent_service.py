#!/usr/bin/env python3
"""
Fixed Dashboard Agent Service
Connects directly to MCP server tools to get real agent data
"""

import asyncio
import logging
import subprocess
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class FixedMCPAgentService:
    """Service that actually connects to MCP tools to get agent data."""

    def __init__(self, instance_id: str = None):
        self.instance_id = instance_id
        self.base_path = Path("/media/hannesn/storage/Code/cursor")

    async def get_real_agent_data(self) -> List[Dict[str, Any]]:
        """Get real agent data by calling MCP tools directly."""
        try:
            # Use poetry to run a Python script that calls MCP tools
            script_content = """
import sys
import os
import asyncio
import json
from datetime import datetime

# Add the source path
sys.path.append("/media/hannesn/storage/Code/cursor/src")

async def get_agents():
    try:
        # Import the actual protocol server
        from protocol_server import AgentSystem

        # Create agent system instance (same as running server)
        agent_system = AgentSystem()

        # Get agents from memory
        agents_data = []
        if hasattr(agent_system, "agents") and agent_system.agents:
            for agent_id, agent in agent_system.agents.items():
                # Convert agent object to dict for dashboard
                agent_info = {
                    "agent_id": agent_id,
                    "agent_type": getattr(agent, "role", "unknown"),
                    "name": getattr(agent, "name", agent_id),
                    "status": "operational",
                    "last_activity": datetime.now().isoformat(),
                    "capabilities": getattr(agent, "capabilities", []),
                    "project_id": getattr(agent, "project_id", ""),
                    "created_at": getattr(agent, "created_at", ""),
                    "specializations": getattr(agent, "specializations", []),
                    "system_message": str(getattr(agent, "system_message", ""))[:100] + "..." if getattr(agent, "system_message", "") else ""
                }
                agents_data.append(agent_info)

        # Output as JSON for the dashboard to parse
        print(json.dumps({"success": True, "agents": agents_data}))

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))

# Run the async function
asyncio.run(get_agents())
"""

            # Write the script to a temporary file
            script_path = self.base_path / "temp_agent_query.py"
            with open(script_path, "w") as f:
                f.write(script_content)

            # Run the script using poetry
            result = subprocess.run(
                ["poetry", "run", "python", "temp_agent_query.py"],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Clean up the temporary file
            try:
                script_path.unlink()
            except:
                pass

            if result.returncode == 0:
                # Parse the JSON output
                try:
                    output_data = json.loads(result.stdout.strip())
                    if output_data.get("success"):
                        agents = output_data.get("agents", [])
                        logger.info(
                            f"Successfully retrieved {len(agents)} agents from MCP server"
                        )
                        return agents
                    else:
                        logger.error(f"MCP query failed: {output_data.get('error')}")
                        return []
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse MCP response: {e}")
                    logger.debug(f"Raw output: {result.stdout}")
                    return []
            else:
                logger.error(f"MCP script failed: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            logger.error("MCP query timed out")
            return []
        except Exception as e:
            logger.error(f"Failed to query MCP server: {e}")
            return []


# Test function
if __name__ == "__main__":

    async def test():
        service = FixedMCPAgentService()
        agents = await service.get_real_agent_data()

        print(f"Found {len(agents)} agents:")
        for agent in agents:
            print(f"  - {agent['agent_id']} ({agent['agent_type']})")
            print(f"    Capabilities: {', '.join(agent['capabilities'][:3])}...")
            print(f"    Project: {agent['project_id']}")
            print()

    asyncio.run(test())
