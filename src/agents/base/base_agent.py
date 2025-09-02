"""Base agent class for the AI agent system."""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum


class AgentStatus(Enum):
    """Agent status enumeration."""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    STOPPED = "stopped"


class AgentType(Enum):
    """Agent type enumeration."""
    COORDINATOR = "coordinator"
    FRONTEND = "frontend"
    BACKEND = "backend"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    AGILE = "agile"
    GIT = "git"
    LOGGING = "logging"
    SECURITY = "security"
    CUSTOM = "custom"


@dataclass
class AgentCapability:
    """Represents an agent capability."""
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Represents a task assigned to an agent."""
    id: str
    type: str
    description: str
    priority: int = 1
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the system."""
    
    def __init__(self, agent_id: str, agent_type: AgentType, name: str,
                 description: str = "", capabilities: Optional[List[AgentCapability]] = None):
        """Initialize base agent."""
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = capabilities or []
        self.status = AgentStatus.INITIALIZING
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.tasks: List[AgentTask] = []
        self.max_concurrent_tasks = 5
        self.logger = logging.getLogger(f"agent.{agent_type.value}.{name}")
        
        # Performance metrics
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.total_processing_time = 0.0
        
        # Communication handlers
        self.message_handlers: Dict[str, Callable] = {}
        self.event_handlers: Dict[str, Callable] = {}
        
        self.logger.info(f"Initializing {agent_type.value} agent: {name}")
    
    async def initialize(self) -> bool:
        """Initialize the agent."""
        try:
            self.logger.info(f"Starting initialization for {self.name}")
            
            # Initialize capabilities
            await self._initialize_capabilities()
            
            # Register default message handlers
            self._register_default_handlers()
            
            # Set status to active
            self.status = AgentStatus.ACTIVE
            self.last_activity = datetime.now()
            
            self.logger.info(f"Successfully initialized {self.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.name}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def _initialize_capabilities(self) -> None:
        """Initialize agent capabilities."""
        for capability in self.capabilities:
            if capability.enabled:
                try:
                    await self._initialize_capability(capability)
                    self.logger.debug(f"Initialized capability: {capability.name}")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize capability {capability.name}: {e}")
                    capability.enabled = False
    
    async def _initialize_capability(self, capability: AgentCapability) -> None:
        """Initialize a specific capability."""
        # Override in subclasses for specific capability initialization
        pass
    
    def _register_default_handlers(self) -> None:
        """Register default message and event handlers."""
        self.register_message_handler("ping", self._handle_ping)
        self.register_message_handler("status", self._handle_status_request)
        self.register_message_handler("capabilities", self._handle_capabilities_request)
        self.register_event_handler("task_assigned", self._handle_task_assigned)
        self.register_event_handler("task_completed", self._handle_task_completed)
    
    def register_message_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler."""
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered message handler for: {message_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register an event handler."""
        self.event_handlers[event_type] = handler
        self.logger.debug(f"Registered event handler for: {event_type}")
    
    async def handle_message(self, message_type: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming messages."""
        try:
            self.last_activity = datetime.now()
            
            if message_type in self.message_handlers:
                handler = self.message_handlers[message_type]
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(message_data)
                else:
                    result = handler(message_data)
                return {"success": True, "result": result}
            else:
                self.logger.warning(f"No handler registered for message type: {message_type}")
                return {"success": False, "error": f"Unknown message type: {message_type}"}
                
        except Exception as e:
            self.logger.error(f"Error handling message {message_type}: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """Handle incoming events."""
        try:
            if event_type in self.event_handlers:
                handler = self.event_handlers[event_type]
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            else:
                self.logger.debug(f"No handler registered for event type: {event_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling event {event_type}: {e}")
    
    async def assign_task(self, task: AgentTask) -> bool:
        """Assign a task to this agent."""
        try:
            if len(self.tasks) >= self.max_concurrent_tasks:
                self.logger.warning(f"Cannot assign task {task.id}: at capacity")
                return False
            
            task.assigned_at = datetime.now()
            task.status = "assigned"
            self.tasks.append(task)
            
            self.logger.info(f"Assigned task {task.id}: {task.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning task {task.id}: {e}")
            return False
    
    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a specific task."""
        try:
            task = self._find_task(task_id)
            if not task:
                return {"success": False, "error": f"Task {task_id} not found"}
            
            if task.status != "assigned":
                return {"success": False, "error": f"Task {task_id} is not in assigned status"}
            
            self.status = AgentStatus.BUSY
            task.status = "executing"
            start_time = datetime.now()
            
            self.logger.info(f"Executing task {task_id}: {task.description}")
            
            # Execute the task
            result = await self._execute_task_impl(task)
            
            # Update task status
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            
            # Update metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_processing_time += execution_time
            self.tasks_completed += 1
            
            self.status = AgentStatus.ACTIVE
            self.last_activity = datetime.now()
            
            self.logger.info(f"Completed task {task_id} in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing task {task_id}: {e}")
            if task:
                task.status = "failed"
                task.error = str(e)
                self.tasks_failed += 1
            
            self.status = AgentStatus.ACTIVE
            return {"success": False, "error": str(e)}
    
    @abstractmethod
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Execute task implementation - must be implemented by subclasses."""
        pass
    
    def _find_task(self, task_id: str) -> Optional[AgentTask]:
        """Find a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "active_tasks": len([t for t in self.tasks if t.status in ["assigned", "executing"]]),
            "total_tasks": len(self.tasks),
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "capabilities": [c.name for c in self.capabilities if c.enabled],
            "performance": {
                "total_processing_time": self.total_processing_time,
                "avg_task_time": (self.total_processing_time / self.tasks_completed 
                                if self.tasks_completed > 0 else 0)
            }
        }
    
    async def get_capabilities(self) -> List[Dict[str, Any]]:
        """Get agent capabilities information."""
        return [
            {
                "name": c.name,
                "description": c.description,
                "version": c.version,
                "enabled": c.enabled,
                "metadata": c.metadata
            }
            for c in self.capabilities
        ]
    
    async def stop(self) -> bool:
        """Stop the agent."""
        try:
            self.logger.info(f"Stopping agent {self.name}")
            
            # Complete any active tasks
            active_tasks = [t for t in self.tasks if t.status in ["assigned", "executing"]]
            for task in active_tasks:
                task.status = "cancelled"
                self.logger.info(f"Cancelled task {task.id}")
            
            self.status = AgentStatus.STOPPED
            self.logger.info(f"Successfully stopped agent {self.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping agent {self.name}: {e}")
            return False
    
    # Default message handlers
    async def _handle_ping(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ping messages."""
        return {"pong": True, "timestamp": datetime.now().isoformat()}
    
    async def _handle_status_request(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle status request messages."""
        return await self.get_status()
    
    async def _handle_capabilities_request(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle capabilities request messages."""
        return await self.get_capabilities()
    
    # Default event handlers
    async def _handle_task_assigned(self, event_data: Dict[str, Any]) -> None:
        """Handle task assigned events."""
        task_id = event_data.get("task_id")
        self.logger.info(f"Task {task_id} assigned to {self.name}")
    
    async def _handle_task_completed(self, event_data: Dict[str, Any]) -> None:
        """Handle task completed events."""
        task_id = event_data.get("task_id")
        self.logger.info(f"Task {task_id} completed by {self.name}")
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.agent_type.value.capitalize()}Agent({self.name})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the agent."""
        return (f"{self.__class__.__name__}(id={self.agent_id}, "
                f"type={self.agent_type.value}, name={self.name}, "
                f"status={self.status.value})")
