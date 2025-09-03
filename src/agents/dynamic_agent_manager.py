#!/usr/bin/env python3
"""Dynamic Agent Management System for Phase 7.1."""

import asyncio
import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass
from enum import Enum

from src.agents.base.base_agent import BaseAgent
from src.agents.base.base_agent import AgentType

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent status enumeration."""
    LOADING = "loading"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    FAILED = "failed"

@dataclass
class AgentInfo:
    """Information about a managed agent."""
    name: str
    agent_type: AgentType
    status: AgentStatus
    instance: Optional[BaseAgent]
    module_path: str
    class_name: str
    load_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class DynamicAgentManager:
    """Dynamic agent management system with plugin capabilities."""
    
    def __init__(self):
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_plugins: Dict[str, Path] = {}
        self.discovery_paths: List[Path] = []
        self._load_lock = asyncio.Lock()
        
    async def add_discovery_path(self, path: str) -> bool:
        """Add a path for agent discovery."""
        try:
            discovery_path = Path(path)
            if discovery_path.exists() and discovery_path.is_dir():
                self.discovery_paths.append(discovery_path)
                logger.info(f"Added discovery path: {path}")
                return True
            else:
                logger.warning(f"Discovery path does not exist or is not a directory: {path}")
                return False
        except Exception as e:
            logger.error(f"Error adding discovery path {path}: {e}")
            return False
    
    async def discover_agents(self) -> List[str]:
        """Discover available agents in discovery paths."""
        discovered_agents = []
        
        for discovery_path in self.discovery_paths:
            try:
                # Look for Python files that might contain agents
                for py_file in discovery_path.rglob("*.py"):
                    if py_file.name.startswith("_") or py_file.name.startswith("test"):
                        continue
                    
                    # Try to import and inspect the module
                    module_name = self._path_to_module_name(py_file)
                    if module_name:
                        agent_classes = await self._inspect_module_for_agents(module_name)
                        for agent_class in agent_classes:
                            discovered_agents.append(agent_class)
                            
            except Exception as e:
                logger.error(f"Error discovering agents in {discovery_path}: {e}")
        
        logger.info(f"Discovered {len(discovered_agents)} potential agent classes")
        return discovered_agents
    
    def _path_to_module_name(self, file_path: Path) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            # Convert path to module name relative to src directory
            src_path = Path(__file__).parent.parent.parent
            relative_path = file_path.relative_to(src_path)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".").replace(".py", "")
            return f"src.{module_name}"
        except Exception:
            return None
    
    async def _inspect_module_for_agents(self, module_name: str) -> List[str]:
        """Inspect a module for agent classes."""
        agent_classes = []
        
        try:
            module = importlib.import_module(module_name)
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseAgent) and 
                    obj != BaseAgent):
                    agent_classes.append(f"{module_name}.{name}")
                    
        except Exception as e:
            logger.debug(f"Could not inspect module {module_name}: {e}")
        
        return agent_classes
    
    async def load_agent(self, agent_class_path: str, **kwargs) -> Optional[AgentInfo]:
        """Dynamically load an agent class."""
        async with self._load_lock:
            try:
                logger.info(f"Loading agent: {agent_class_path}")
                
                # Parse module and class name
                module_name, class_name = agent_class_path.rsplit(".", 1)
                
                # Import the module
                module = importlib.import_module(module_name)
                agent_class = getattr(module, class_name)
                
                # Validate it's a proper agent class
                if not issubclass(agent_class, BaseAgent):
                    raise ValueError(f"{class_name} is not a valid agent class")
                
                # Create agent instance
                agent_instance = agent_class(**kwargs)
                
                # Get agent information
                agent_info = AgentInfo(
                    name=agent_instance.name,
                    agent_type=agent_instance.agent_type,
                    status=AgentStatus.ACTIVE,
                    instance=agent_instance,
                    module_path=module_name,
                    class_name=class_name,
                    load_time=asyncio.get_event_loop().time(),
                    metadata=kwargs
                )
                
                # Store the agent
                self.agents[agent_instance.name] = agent_info
                
                logger.info(f"Successfully loaded agent: {agent_instance.name}")
                return agent_info
                
            except Exception as e:
                logger.error(f"Failed to load agent {agent_class_path}: {e}")
                
                # Create error info
                error_info = AgentInfo(
                    name=agent_class_path.split(".")[-1],
                    agent_type=AgentType.CUSTOM,
                    status=AgentStatus.ERROR,
                    instance=None,
                    module_path=agent_class_path,
                    class_name=agent_class_path.split(".")[-1],
                    load_time=asyncio.get_event_loop().time(),
                    error_message=str(e)
                )
                
                self.agents[error_info.name] = error_info
                return error_info
    
    async def unload_agent(self, agent_name: str) -> bool:
        """Unload an agent."""
        async with self._load_lock:
            if agent_name in self.agents:
                agent_info = self.agents[agent_name]
                
                try:
                    # Clean up agent instance if it has cleanup method
                    if (agent_info.instance and 
                        hasattr(agent_info.instance, 'cleanup') and 
                        callable(agent_info.instance.cleanup)):
                        await agent_info.instance.cleanup()
                    
                    # Remove from agents dict
                    del self.agents[agent_name]
                    
                    logger.info(f"Successfully unloaded agent: {agent_name}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error unloading agent {agent_name}: {e}")
                    return False
            else:
                logger.warning(f"Agent not found: {agent_name}")
                return False
    
    async def reload_agent(self, agent_name: str) -> Optional[AgentInfo]:
        """Reload an agent."""
        if agent_name in self.agents:
            agent_info = self.agents[agent_name]
            
            # Unload first
            await self.unload_agent(agent_name)
            
            # Reload with same parameters
            return await self.load_agent(f"{agent_info.module_path}.{agent_info.class_name}", 
                                       **(agent_info.metadata or {}))
        else:
            logger.warning(f"Agent not found for reload: {agent_name}")
            return None
    
    async def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent instance by name."""
        if agent_name in self.agents:
            agent_info = self.agents[agent_name]
            if agent_info.status == AgentStatus.ACTIVE:
                return agent_info.instance
            else:
                logger.warning(f"Agent {agent_name} is not active (status: {agent_info.status})")
                return None
        else:
            logger.warning(f"Agent not found: {agent_name}")
            return None
    
    async def get_agent_status(self, agent_name: str) -> Optional[AgentStatus]:
        """Get the status of an agent."""
        if agent_name in self.agents:
            return self.agents[agent_name].status
        return None
    
    async def list_agents(self) -> List[AgentInfo]:
        """List all managed agents."""
        return list(self.agents.values())
    
    async def get_agent_count(self) -> Dict[AgentStatus, int]:
        """Get count of agents by status."""
        status_counts = {status: 0 for status in AgentStatus}
        
        for agent_info in self.agents.values():
            status_counts[agent_info.status] += 1
        
        return status_counts
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all agents."""
        health_status = {
            "total_agents": len(self.agents),
            "status_counts": await self.get_agent_count(),
            "errors": [],
            "warnings": []
        }
        
        for agent_name, agent_info in self.agents.items():
            if agent_info.status == AgentStatus.ERROR:
                health_status["errors"].append({
                    "agent": agent_name,
                    "error": agent_info.error_message
                })
            elif agent_info.status == AgentStatus.FAILED:
                health_status["warnings"].append({
                    "agent": agent_name,
                    "status": "failed"
                })
        
        return health_status

# Global instance
dynamic_agent_manager = DynamicAgentManager()
