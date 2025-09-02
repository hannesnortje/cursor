"""PDCA (Plan-Do-Check-Act) Framework for the Coordinator Agent."""

import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class PDCAPhase(Enum):
    """PDCA cycle phases."""
    PLAN = "plan"
    DO = "do"
    CHECK = "check"
    ACT = "act"


class PDCAStatus(Enum):
    """PDCA cycle status."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class PDCACycle:
    """Represents a single PDCA cycle."""
    id: str
    name: str
    description: str
    current_phase: PDCAPhase = PDCAPhase.PLAN
    status: PDCAStatus = PDCAStatus.INITIATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[timedelta] = None
    objectives: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "current_phase": self.current_phase.value,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": str(self.duration) if self.duration else None,
            "objectives": self.objectives,
            "success_criteria": self.success_criteria,
            "metrics": self.metrics,
            "notes": self.notes,
            "metadata": self.metadata
        }


@dataclass
class PDCAObjective:
    """Represents a PDCA objective."""
    id: str
    description: str
    priority: int = 1
    status: str = "pending"
    assigned_agent: Optional[str] = None
    due_date: Optional[datetime] = None
    completion_percentage: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completion_percentage": self.completion_percentage,
            "dependencies": self.dependencies,
            "metrics": self.metrics
        }


class PDCAFramework:
    """PDCA Framework implementation for project management."""
    
    def __init__(self):
        """Initialize PDCA framework."""
        self.logger = logging.getLogger("coordinator.pdca")
        self.cycles: Dict[str, PDCACycle] = {}
        self.objectives: Dict[str, PDCAObjective] = {}
        self.phase_handlers: Dict[PDCAPhase, Callable] = {}
        self.metrics_collectors: List[Callable] = []
        
        # Register default phase handlers
        self._register_default_handlers()
        
        self.logger.info("PDCA Framework initialized")
    
    def _register_default_handlers(self) -> None:
        """Register default phase handlers."""
        self.register_phase_handler(PDCAPhase.PLAN, self._default_plan_handler)
        self.register_phase_handler(PDCAPhase.DO, self._default_do_handler)
        self.register_phase_handler(PDCAPhase.CHECK, self._default_check_handler)
        self.register_phase_handler(PDCAPhase.ACT, self._default_act_handler)
    
    def register_phase_handler(self, phase: PDCAPhase, handler: Callable) -> None:
        """Register a handler for a specific PDCA phase."""
        self.phase_handlers[phase] = handler
        self.logger.debug(f"Registered handler for phase: {phase.value}")
    
    def register_metrics_collector(self, collector: Callable) -> None:
        """Register a metrics collector function."""
        self.metrics_collectors.append(collector)
        self.logger.debug("Registered metrics collector")
    
    async def create_cycle(self, name: str, description: str, 
                          objectives: List[str], success_criteria: List[str]) -> PDCACycle:
        """Create a new PDCA cycle."""
        try:
            cycle_id = f"pdca_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            cycle = PDCACycle(
                id=cycle_id,
                name=name,
                description=description,
                objectives=objectives,
                success_criteria=success_criteria
            )
            
            self.cycles[cycle_id] = cycle
            self.logger.info(f"Created PDCA cycle: {name} ({cycle_id})")
            
            return cycle
            
        except Exception as e:
            self.logger.error(f"Failed to create PDCA cycle: {e}")
            raise
    
    async def start_cycle(self, cycle_id: str) -> bool:
        """Start a PDCA cycle."""
        try:
            if cycle_id not in self.cycles:
                raise ValueError(f"PDCA cycle {cycle_id} not found")
            
            cycle = self.cycles[cycle_id]
            cycle.status = PDCAStatus.IN_PROGRESS
            cycle.started_at = datetime.now()
            cycle.current_phase = PDCAPhase.PLAN
            
            self.logger.info(f"Started PDCA cycle: {cycle.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start PDCA cycle {cycle_id}: {e}")
            return False
    
    async def advance_phase(self, cycle_id: str) -> bool:
        """Advance to the next phase in a PDCA cycle."""
        try:
            if cycle_id not in self.cycles:
                raise ValueError(f"PDCA cycle {cycle_id} not found")
            
            cycle = self.cycles[cycle_id]
            
            # Execute current phase
            if cycle.current_phase in self.phase_handlers:
                handler = self.phase_handlers[cycle.current_phase]
                if asyncio.iscoroutinefunction(handler):
                    await handler(cycle)
                else:
                    handler(cycle)
            
            # Advance to next phase
            if cycle.current_phase == PDCAPhase.PLAN:
                cycle.current_phase = PDCAPhase.DO
            elif cycle.current_phase == PDCAPhase.DO:
                cycle.current_phase = PDCAPhase.CHECK
            elif cycle.current_phase == PDCAPhase.CHECK:
                cycle.current_phase = PDCAPhase.ACT
            elif cycle.current_phase == PDCAPhase.ACT:
                # Cycle completed
                cycle.status = PDCAStatus.COMPLETED
                cycle.completed_at = datetime.now()
                if cycle.started_at:
                    cycle.duration = cycle.completed_at - cycle.started_at
            
            self.logger.info(f"Advanced cycle {cycle.name} to phase: {cycle.current_phase.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to advance phase for cycle {cycle_id}: {e}")
            return False
    
    async def complete_cycle(self, cycle_id: str, success: bool = True) -> bool:
        """Complete a PDCA cycle."""
        try:
            if cycle_id not in self.cycles:
                raise ValueError(f"PDCA cycle {cycle_id} not found")
            
            cycle = self.cycles[cycle_id]
            cycle.status = PDCAStatus.COMPLETED if success else PDCAStatus.FAILED
            cycle.completed_at = datetime.now()
            
            if cycle.started_at:
                cycle.duration = cycle.completed_at - cycle.started_at
            
            # Collect final metrics
            await self._collect_cycle_metrics(cycle)
            
            self.logger.info(f"Completed PDCA cycle: {cycle.name} (success: {success})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete cycle {cycle_id}: {e}")
            return False
    
    async def add_objective(self, cycle_id: str, description: str, 
                           priority: int = 1, due_date: Optional[datetime] = None) -> PDCAObjective:
        """Add an objective to a PDCA cycle."""
        try:
            if cycle_id not in self.cycles:
                raise ValueError(f"PDCA cycle {cycle_id} not found")
            
            objective_id = f"obj_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            objective = PDCAObjective(
                id=objective_id,
                description=description,
                priority=priority,
                due_date=due_date
            )
            
            self.objectives[objective_id] = objective
            self.cycles[cycle_id].objectives.append(objective_id)
            
            self.logger.info(f"Added objective to cycle {cycle_id}: {description}")
            return objective
            
        except Exception as e:
            self.logger.error(f"Failed to add objective to cycle {cycle_id}: {e}")
            raise
    
    async def assign_objective(self, objective_id: str, agent_id: str) -> bool:
        """Assign an objective to an agent."""
        try:
            if objective_id not in self.objectives:
                raise ValueError(f"Objective {objective_id} not found")
            
            objective = self.objectives[objective_id]
            objective.assigned_agent = agent_id
            objective.status = "assigned"
            
            self.logger.info(f"Assigned objective {objective_id} to agent {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to assign objective {objective_id}: {e}")
            return False
    
    async def update_objective_progress(self, objective_id: str, 
                                      completion_percentage: float, 
                                      status: str = None) -> bool:
        """Update objective progress."""
        try:
            if objective_id not in self.objectives:
                raise ValueError(f"Objective {objective_id} not found")
            
            objective = self.objectives[objective_id]
            objective.completion_percentage = completion_percentage
            
            if status:
                objective.status = status
            
            if completion_percentage >= 100.0:
                objective.status = "completed"
            
            self.logger.debug(f"Updated objective {objective_id} progress: {completion_percentage}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update objective {objective_id}: {e}")
            return False
    
    async def get_cycle_status(self, cycle_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a PDCA cycle."""
        try:
            if cycle_id not in self.cycles:
                return None
            
            cycle = self.cycles[cycle_id]
            cycle_data = cycle.to_dict()
            
            # Add objectives data
            cycle_objectives = []
            for obj_id in cycle.objectives:
                if obj_id in self.objectives:
                    cycle_objectives.append(self.objectives[obj_id].to_dict())
            
            cycle_data["objectives"] = cycle_objectives
            return cycle_data
            
        except Exception as e:
            self.logger.error(f"Failed to get cycle status for {cycle_id}: {e}")
            return None
    
    async def list_cycles(self, status_filter: Optional[PDCAStatus] = None) -> List[Dict[str, Any]]:
        """List all PDCA cycles with optional status filtering."""
        try:
            cycles = []
            for cycle in self.cycles.values():
                if status_filter is None or cycle.status == status_filter:
                    cycles.append(cycle.to_dict())
            
            return cycles
            
        except Exception as e:
            self.logger.error(f"Failed to list cycles: {e}")
            return []
    
    async def _collect_cycle_metrics(self, cycle: PDCACycle) -> None:
        """Collect metrics for a completed cycle."""
        try:
            for collector in self.metrics_collectors:
                try:
                    if asyncio.iscoroutinefunction(collector):
                        metrics = await collector(cycle)
                    else:
                        metrics = collector(cycle)
                    
                    if metrics:
                        cycle.metrics.update(metrics)
                        
                except Exception as e:
                    self.logger.warning(f"Metrics collector failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to collect cycle metrics: {e}")
    
    # Default phase handlers
    async def _default_plan_handler(self, cycle: PDCACycle) -> None:
        """Default handler for Plan phase."""
        self.logger.info(f"Executing Plan phase for cycle: {cycle.name}")
        cycle.notes.append(f"Plan phase executed at {datetime.now().isoformat()}")
    
    async def _default_do_handler(self, cycle: PDCACycle) -> None:
        """Default handler for Do phase."""
        self.logger.info(f"Executing Do phase for cycle: {cycle.name}")
        cycle.notes.append(f"Do phase executed at {datetime.now().isoformat()}")
    
    async def _default_check_handler(self, cycle: PDCACycle) -> None:
        """Default handler for Check phase."""
        self.logger.info(f"Executing Check phase for cycle: {cycle.name}")
        cycle.notes.append(f"Check phase executed at {datetime.now().isoformat()}")
    
    async def _default_act_handler(self, cycle: PDCACycle) -> None:
        """Default handler for Act phase."""
        self.logger.info(f"Executing Act phase for cycle: {cycle.name}")
        cycle.notes.append(f"Act phase executed at {datetime.now().isoformat()}")
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get overall framework status."""
        total_cycles = len(self.cycles)
        active_cycles = len([c for c in self.cycles.values() if c.status == PDCAStatus.IN_PROGRESS])
        completed_cycles = len([c for c in self.cycles.values() if c.status == PDCAStatus.COMPLETED])
        
        return {
            "total_cycles": total_cycles,
            "active_cycles": active_cycles,
            "completed_cycles": completed_cycles,
            "total_objectives": len(self.objectives),
            "framework_status": "active"
        }
