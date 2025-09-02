"""Coordinator Agent for orchestrating the AI agent system."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..base.base_agent import BaseAgent, AgentType, AgentCapability, AgentTask
from ..registry import AgentRegistry
from .pdca_framework import PDCAFramework, PDCACycle, PDCAObjective


@dataclass
class ProjectPlan:
    """Represents a project plan managed by the coordinator."""
    id: str
    name: str
    description: str
    objectives: List[str]
    success_criteria: List[str]
    timeline: Dict[str, Any]
    resources: List[str]
    risks: List[str]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "planning"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "objectives": self.objectives,
            "success_criteria": self.success_criteria,
            "timeline": self.timeline,
            "resources": self.resources,
            "risks": self.risks,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }


class CoordinatorAgent(BaseAgent):
    """Coordinator Agent that orchestrates the entire AI agent system."""
    
    def __init__(self, agent_id: str = "coordinator_001", name: str = "System Coordinator"):
        """Initialize the coordinator agent."""
        capabilities = [
            AgentCapability(
                name="project_planning",
                description="Create and manage project plans",
                version="1.0.0"
            ),
            AgentCapability(
                name="agent_coordination",
                description="Coordinate and delegate tasks to other agents",
                version="1.0.0"
            ),
            AgentCapability(
                name="pdca_management",
                description="Manage PDCA cycles for continuous improvement",
                version="1.0.0"
            ),
            AgentCapability(
                name="resource_allocation",
                description="Allocate resources and manage dependencies",
                version="1.0.0"
            ),
            AgentCapability(
                name="performance_monitoring",
                description="Monitor system performance and agent metrics",
                version="1.0.0"
            )
        ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COORDINATOR,
            name=name,
            description="Central orchestrator for the AI agent system",
            capabilities=capabilities
        )
        
        # Initialize coordinator-specific components
        self.pdca_framework = PDCAFramework()
        self.project_plans: Dict[str, ProjectPlan] = {}
        self.agent_registry: Optional[AgentRegistry] = None
        self.active_projects: List[str] = []
        
        self.logger.info(f"Coordinator Agent {name} initialized")
    
    async def initialize(self) -> bool:
        """Initialize the coordinator agent."""
        try:
            # Initialize base agent
            base_initialized = await super().initialize()
            if not base_initialized:
                return False
            
            # Get agent registry
            from ..registry import get_registry
            self.agent_registry = await get_registry()
            
            # Register coordinator-specific message handlers
            self.register_message_handler("create_project", self._handle_create_project)
            self.register_message_handler("start_pdca_cycle", self._handle_start_pdca_cycle)
            self.register_message_handler("assign_task", self._handle_assign_task)
            self.register_message_handler("get_system_status", self._handle_get_system_status)
            self.register_message_handler("create_agent", self._handle_create_agent)
            
            self.logger.info("Coordinator Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Coordinator Agent initialization failed: {e}")
            return False
    
    async def create_project(self, name: str, description: str, 
                           objectives: List[str], success_criteria: List[str],
                           timeline: Dict[str, Any], resources: List[str],
                           risks: List[str]) -> ProjectPlan:
        """Create a new project plan."""
        try:
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            project = ProjectPlan(
                id=project_id,
                name=name,
                description=description,
                objectives=objectives,
                success_criteria=success_criteria,
                timeline=timeline,
                resources=resources,
                risks=risks
            )
            
            self.project_plans[project_id] = project
            self.active_projects.append(project_id)
            
            # Create corresponding PDCA cycle
            pdca_cycle = await self.pdca_framework.create_cycle(
                name=f"PDCA for {name}",
                description=f"PDCA cycle for project: {description}",
                objectives=objectives,
                success_criteria=success_criteria
            )
            
            project.metadata["pdca_cycle_id"] = pdca_cycle.id
            
            self.logger.info(f"Created project: {name} ({project_id})")
            return project
            
        except Exception as e:
            self.logger.error(f"Failed to create project {name}: {e}")
            raise
    
    async def start_project(self, project_id: str) -> bool:
        """Start a project and its associated PDCA cycle."""
        try:
            if project_id not in self.project_plans:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.project_plans[project_id]
            project.status = "active"
            
            # Start PDCA cycle
            pdca_cycle_id = project.metadata.get("pdca_cycle_id")
            if pdca_cycle_id:
                await self.pdca_framework.start_cycle(pdca_cycle_id)
            
            self.logger.info(f"Started project: {project.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start project {project_id}: {e}")
            return False
    
    async def create_agent(self, agent_type: str, name: str, 
                          description: str, capabilities: List[str]) -> Dict[str, Any]:
        """Create a new agent of the specified type."""
        try:
            # This would typically create specialized agents
            # For now, we'll return a mock response
            agent_id = f"agent_{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            agent_info = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "status": "created",
                "created_at": datetime.now().isoformat()
            }
            
            self.logger.info(f"Created agent: {name} ({agent_type})")
            return agent_info
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {name}: {e}")
            return {"error": str(e)}
    
    async def assign_task_to_agent(self, task_description: str, 
                                  preferred_agent_type: Optional[str] = None,
                                  priority: int = 1) -> Dict[str, Any]:
        """Assign a task to an appropriate agent."""
        try:
            if not self.agent_registry:
                return {"error": "Agent registry not available"}
            
            # Create task data
            task_data = {
                "description": task_description,
                "priority": priority,
                "type": "general"
            }
            
            # Assign task through registry
            result = await self.agent_registry.assign_task_to_agent(
                task_data, 
                preferred_agent_type=preferred_agent_type
            )
            
            if result.get("success"):
                self.logger.info(f"Task assigned: {task_description}")
            else:
                self.logger.warning(f"Task assignment failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to assign task: {e}")
            return {"error": str(e)}
    
    async def advance_project_phase(self, project_id: str) -> bool:
        """Advance the PDCA phase for a project."""
        try:
            if project_id not in self.project_plans:
                raise ValueError(f"Project {project_id} not found")
            
            project = self.project_plans[project_id]
            pdca_cycle_id = project.metadata.get("pdca_cycle_id")
            
            if not pdca_cycle_id:
                raise ValueError(f"No PDCA cycle found for project {project_id}")
            
            # Advance PDCA phase
            success = await self.pdca_framework.advance_phase(pdca_cycle_id)
            
            if success:
                # Update project status based on PDCA phase
                cycle = self.pdca_framework.cycles.get(pdca_cycle_id)
                if cycle:
                    project.metadata["current_pdca_phase"] = cycle.current_phase.value
                    
                    if cycle.status.value == "completed":
                        project.status = "completed"
                        self.active_projects.remove(project_id)
                
                self.logger.info(f"Advanced project {project.name} to phase: {project.metadata.get('current_pdca_phase')}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to advance project phase for {project_id}: {e}")
            return False
    
    async def get_project_status(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a specific project."""
        try:
            if project_id not in self.project_plans:
                return None
            
            project = self.project_plans[project_id]
            project_data = project.to_dict()
            
            # Add PDCA cycle information
            pdca_cycle_id = project.metadata.get("pdca_cycle_id")
            if pdca_cycle_id:
                pdca_status = await self.pdca_framework.get_cycle_status(pdca_cycle_id)
                project_data["pdca_status"] = pdca_status
            
            return project_data
            
        except Exception as e:
            self.logger.error(f"Failed to get project status for {project_id}: {e}")
            return None
    
    async def list_projects(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all projects with optional status filtering."""
        try:
            projects = []
            for project in self.project_plans.values():
                if status_filter is None or project.status == status_filter:
                    projects.append(project.to_dict())
            
            return projects
            
        except Exception as e:
            self.logger.error(f"Failed to list projects: {e}")
            return []
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        try:
            # Get base agent status
            base_status = await super().get_status()
            
            # Get PDCA framework status
            pdca_status = self.pdca_framework.get_framework_status()
            
            # Get agent registry status
            registry_status = {}
            if self.agent_registry:
                registry_status = await self.agent_registry.get_registry_status()
            
            # Get project status
            total_projects = len(self.project_plans)
            active_projects = len(self.active_projects)
            completed_projects = len([p for p in self.project_plans.values() if p.status == "completed"])
            
            return {
                **base_status,
                "pdca_framework": pdca_status,
                "agent_registry": registry_status,
                "projects": {
                    "total": total_projects,
                    "active": active_projects,
                    "completed": completed_projects
                },
                "coordinator_status": "active"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    # Message handlers
    async def _handle_create_project(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project creation requests."""
        try:
            project = await self.create_project(
                name=message_data["name"],
                description=message_data["description"],
                objectives=message_data.get("objectives", []),
                success_criteria=message_data.get("success_criteria", []),
                timeline=message_data.get("timeline", {}),
                resources=message_data.get("resources", []),
                risks=message_data.get("risks", [])
            )
            
            return {"success": True, "project": project.to_dict()}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_start_pdca_cycle(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PDCA cycle start requests."""
        try:
            cycle_id = message_data["cycle_id"]
            success = await self.pdca_framework.start_cycle(cycle_id)
            
            return {"success": success}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_assign_task(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task assignment requests."""
        try:
            result = await self.assign_task_to_agent(
                task_description=message_data["description"],
                preferred_agent_type=message_data.get("preferred_agent_type"),
                priority=message_data.get("priority", 1)
            )
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_get_system_status(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle system status requests."""
        try:
            status = await self.get_system_status()
            return {"success": True, "status": status}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _handle_create_agent(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle agent creation requests."""
        try:
            result = await self.create_agent(
                agent_type=message_data["agent_type"],
                name=message_data["name"],
                description=message_data["description"],
                capabilities=message_data.get("capabilities", [])
            )
            
            return {"success": True, "agent": result}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task assigned to the coordinator."""
        try:
            task_type = task.type
            
            if task_type == "create_project":
                # Extract project data from task metadata
                project_data = task.metadata
                project = await self.create_project(
                    name=project_data["name"],
                    description=project_data["description"],
                    objectives=project_data.get("objectives", []),
                    success_criteria=project_data.get("success_criteria", []),
                    timeline=project_data.get("timeline", {}),
                    resources=project_data.get("resources", []),
                    risks=project_data.get("risks", [])
                )
                
                return {"success": True, "project": project.to_dict()}
                
            elif task_type == "coordinate_agents":
                # Coordinate a group of agents
                agent_ids = task.metadata.get("agent_ids", [])
                coordination_task = task.metadata.get("task", "")
                
                results = {}
                for agent_id in agent_ids:
                    result = await self.assign_task_to_agent(coordination_task)
                    results[agent_id] = result
                
                return {"success": True, "coordination_results": results}
                
            elif task_type == "system_health_check":
                # Perform system health check
                status = await self.get_system_status()
                return {"success": True, "system_status": status}
                
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e)}
