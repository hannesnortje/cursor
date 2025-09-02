"""Agent registry system for managing agent lifecycle and coordination."""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

from .base.base_agent import BaseAgent, AgentType, AgentStatus


class RegistryStatus(Enum):
    """Registry status enumeration."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    SHUTTING_DOWN = "shutting_down"
    STOPPED = "stopped"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    agent_id: str
    agent_type: AgentType
    name: str
    description: str
    status: AgentStatus
    created_at: datetime
    last_activity: datetime
    capabilities: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRegistry:
    """Central registry for managing all agents in the system."""
    
    def __init__(self):
        """Initialize the agent registry."""
        self.logger = logging.getLogger("agent.registry")
        self.status = RegistryStatus.INITIALIZING
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_info: Dict[str, AgentInfo] = {}
        self.agent_types: Dict[AgentType, List[str]] = {agent_type: [] for agent_type in AgentType}
        
        # Registry metrics
        self.total_agents_registered = 0
        self.active_agents = 0
        self.registry_start_time = datetime.now()
        
        self.logger.info("Initializing agent registry")
    
    async def initialize(self) -> bool:
        """Initialize the agent registry."""
        try:
            self.logger.info("Starting agent registry initialization")
            
            # Set up periodic health checks
            asyncio.create_task(self._periodic_health_check())
            
            self.status = RegistryStatus.ACTIVE
            self.logger.info("Agent registry initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agent registry: {e}")
            self.status = RegistryStatus.STOPPED
            return False
    
    async def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent in the registry."""
        try:
            if agent.agent_id in self.agents:
                self.logger.warning(f"Agent {agent.agent_id} already registered")
                return False
            
            # Add agent to registry
            self.agents[agent.agent_id] = agent
            self.agent_types[agent.agent_type].append(agent.agent_id)
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent.agent_id,
                agent_type=agent.agent_type,
                name=agent.name,
                description=agent.description,
                status=agent.status,
                created_at=agent.created_at,
                last_activity=agent.last_activity,
                capabilities=[c.name for c in agent.capabilities if c.enabled],
                metadata={}
            )
            self.agent_info[agent.agent_id] = agent_info
            
            # Update metrics
            self.total_agents_registered += 1
            if agent.status == AgentStatus.ACTIVE:
                self.active_agents += 1
            
            self.logger.info(f"Registered agent: {agent.name} ({agent.agent_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.name}: {e}")
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry."""
        try:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found in registry")
                return False
            
            agent = self.agents[agent_id]
            
            # Remove from registry
            del self.agents[agent_id]
            del self.agent_info[agent_id]
            self.agent_types[agent.agent_type].remove(agent_id)
            
            # Update metrics
            if agent.status == AgentStatus.ACTIVE:
                self.active_agents -= 1
            
            self.logger.info(f"Unregistered agent: {agent.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    def get_agents_by_type(self, agent_type: AgentType) -> List[BaseAgent]:
        """Get all agents of a specific type."""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agents[agent_id] for agent_id in agent_ids if agent_id in self.agents]
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        """Get information about a specific agent."""
        return self.agent_info.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all registered agents."""
        return list(self.agent_info.values())
    
    def list_agents_by_type(self, agent_type: AgentType) -> List[AgentInfo]:
        """List agents of a specific type."""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agent_info[agent_id] for agent_id in agent_ids if agent_id in self.agent_info]
    
    async def broadcast_message(self, message_type: str, message_data: Dict[str, Any],
                              target_types: Optional[List[AgentType]] = None) -> Dict[str, Any]:
        """Broadcast a message to all agents or specific types."""
        try:
            results = {}
            target_agents = []
            
            if target_types:
                # Send to specific agent types
                for agent_type in target_types:
                    agents = self.get_agents_by_type(agent_type)
                    target_agents.extend(agents)
            else:
                # Send to all agents
                target_agents = list(self.agents.values())
            
            # Send message to each agent
            for agent in target_agents:
                try:
                    result = await agent.handle_message(message_type, message_data)
                    results[agent.agent_id] = result
                except Exception as e:
                    self.logger.error(f"Error sending message to {agent.name}: {e}")
                    results[agent.agent_id] = {"success": False, "error": str(e)}
            
            return {
                "success": True,
                "message": f"Broadcasted to {len(target_agents)} agents",
                "results": results
            }
            
        except Exception as e:
            self.logger.error(f"Broadcast message failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def assign_task_to_agent(self, task_data: Dict[str, Any], 
                                  preferred_agent_type: Optional[AgentType] = None) -> Dict[str, Any]:
        """Assign a task to an appropriate agent."""
        try:
            from .base.base_agent import AgentTask
            
            # Create task object
            task = AgentTask(
                id=task_data.get("id", f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                type=task_data.get("type", "general"),
                description=task_data.get("description", ""),
                priority=task_data.get("priority", 1),
                metadata=task_data.get("metadata", {})
            )
            
            # Find suitable agent
            target_agent = None
            
            if preferred_agent_type:
                # Try to find agent of preferred type
                agents = self.get_agents_by_type(preferred_agent_type)
                available_agents = [a for a in agents if a.status == AgentStatus.ACTIVE 
                                 and len(a.tasks) < a.max_concurrent_tasks]
                
                if available_agents:
                    target_agent = available_agents[0]  # Simple selection - could be enhanced
            
            if not target_agent:
                # Find any available agent
                for agent in self.agents.values():
                    if (agent.status == AgentStatus.ACTIVE and 
                        len(agent.tasks) < agent.max_concurrent_tasks):
                        target_agent = agent
                        break
            
            if not target_agent:
                return {
                    "success": False,
                    "error": "No available agents to handle task"
                }
            
            # Assign task
            success = await target_agent.assign_task(task)
            if success:
                return {
                    "success": True,
                    "task_id": task.id,
                    "assigned_to": target_agent.agent_id,
                    "agent_name": target_agent.name
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to assign task to {target_agent.name}"
                }
                
        except Exception as e:
            self.logger.error(f"Task assignment failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_registry_status(self) -> Dict[str, Any]:
        """Get registry status information."""
        return {
            "status": self.status.value,
            "total_agents": len(self.agents),
            "active_agents": self.active_agents,
            "agent_types": {
                agent_type.value: len(agent_ids)
                for agent_type, agent_ids in self.agent_types.items()
                if agent_ids
            },
            "registry_uptime": (datetime.now() - self.registry_start_time).total_seconds(),
            "total_registered": self.total_agents_registered
        }
    
    async def _periodic_health_check(self) -> None:
        """Periodic health check for all agents."""
        while self.status == RegistryStatus.ACTIVE:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                for agent_id, agent in self.agents.items():
                    try:
                        # Update agent info
                        if agent_id in self.agent_info:
                            self.agent_info[agent_id].status = agent.status
                            self.agent_info[agent_id].last_activity = agent.last_activity
                        
                        # Check for inactive agents
                        if (agent.status == AgentStatus.ACTIVE and 
                            (datetime.now() - agent.last_activity).total_seconds() > 300):
                            self.logger.warning(f"Agent {agent.name} appears inactive")
                            
                    except Exception as e:
                        self.logger.error(f"Health check failed for {agent_id}: {e}")
                
                # Update active agent count
                self.active_agents = sum(1 for a in self.agents.values() 
                                       if a.status == AgentStatus.ACTIVE)
                
            except Exception as e:
                self.logger.error(f"Periodic health check failed: {e}")
    
    async def shutdown(self) -> bool:
        """Shutdown the agent registry."""
        try:
            self.logger.info("Shutting down agent registry")
            self.status = RegistryStatus.SHUTTING_DOWN
            
            # Stop all agents
            for agent in self.agents.values():
                try:
                    await agent.stop()
                except Exception as e:
                    self.logger.error(f"Error stopping agent {agent.name}: {e}")
            
            # Clear registry
            self.agents.clear()
            self.agent_info.clear()
            for agent_type in self.agent_types:
                self.agent_types[agent_type].clear()
            
            self.status = RegistryStatus.STOPPED
            self.logger.info("Agent registry shutdown complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during registry shutdown: {e}")
            return False


# Global registry instance
_global_registry: Optional[AgentRegistry] = None


async def get_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = AgentRegistry()
        await _global_registry.initialize()
    return _global_registry


async def shutdown_registry() -> bool:
    """Shutdown the global agent registry."""
    global _global_registry
    if _global_registry:
        success = await _global_registry.shutdown()
        _global_registry = None
        return success
    return True
