#!/usr/bin/env python3
"""
Agile/Scrum Agent for AI Agent System.
Provides sprint planning, user story management, and agile workflow capabilities.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from ..base.base_agent import BaseAgent, AgentType, AgentStatus, AgentCapability
from ...database.schemas import AgileProject, UserStory, Sprint, Task, TeamMember

logger = logging.getLogger(__name__)


@dataclass
class SprintMetrics:
    """Sprint performance metrics."""

    sprint_id: str
    planned_points: int
    completed_points: int
    velocity: float
    burndown_data: List[Dict[str, Any]]
    team_velocity: float
    sprint_health: str  # "healthy", "at_risk", "critical"


@dataclass
class UserStoryEstimate:
    """User story estimation data."""

    story_id: str
    story_points: int
    confidence_level: str  # "high", "medium", "low"
    complexity_factors: List[str]
    estimated_hours: float
    dependencies: List[str]


class AgileAgent(BaseAgent):
    """Agile/Scrum Agent for project management and sprint planning."""

    def __init__(self, agent_id: str = None, name: str = "Agile Agent"):
        super().__init__(
            agent_id=agent_id or f"agile_{uuid.uuid4().hex[:8]}",
            name=name,
            agent_type=AgentType.AGILE,
            capabilities=[
                AgentCapability(
                    name="project_management",
                    description="Manage agile projects and sprints",
                ),
                AgentCapability(
                    name="sprint_planning", description="Plan and manage sprints"
                ),
                AgentCapability(
                    name="user_story_management",
                    description="Create and manage user stories",
                ),
                AgentCapability(
                    name="team_coordination", description="Coordinate team activities"
                ),
                AgentCapability(
                    name="metrics_analysis",
                    description="Analyze project metrics and velocity",
                ),
            ],
        )

        # Agile-specific attributes
        self.agile_projects: Dict[str, AgileProject] = {}
        self.active_sprints: Dict[str, Sprint] = {}
        self.user_stories: Dict[str, UserStory] = {}
        self.team_members: Dict[str, TeamMember] = {}
        self.sprint_metrics: Dict[str, SprintMetrics] = {}

        # Configuration
        self.default_sprint_length = 14  # days
        self.default_story_point_scale = [1, 2, 3, 5, 8, 13, 21]  # Fibonacci
        self.velocity_calculation_sprints = (
            3  # Number of sprints for velocity calculation
        )

        logger.info(
            f"Agile Agent {self.agent_id} initialized with capabilities: {[cap.name for cap in self.capabilities]}"
        )

    async def _execute_task_impl(self, task) -> Dict[str, Any]:
        """Execute task implementation - required by BaseAgent."""
        try:
            logger.info(f"Executing task {task.id} in Agile Agent")

            # Handle different task types
            if task.type == "create_project":
                return await self._handle_create_project_task(task)
            elif task.type == "create_user_story":
                return await self._handle_create_user_story_task(task)
            elif task.type == "create_sprint":
                return await self._handle_create_sprint_task(task)
            elif task.type == "plan_sprint":
                return await self._handle_plan_sprint_task(task)
            else:
                return {"success": False, "error": f"Unknown task type: {task.type}"}

        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            return {"success": False, "error": str(e)}

    async def _handle_create_project_task(self, task) -> Dict[str, Any]:
        """Handle create project task."""
        project_name = task.metadata.get("project_name")
        project_type = task.metadata.get("project_type", "scrum")
        sprint_length = task.metadata.get("sprint_length")
        team_size = task.metadata.get("team_size", 5)

        return self.create_agile_project(
            project_name, project_type, sprint_length, team_size
        )

    async def _handle_create_user_story_task(self, task) -> Dict[str, Any]:
        """Handle create user story task."""
        project_id = task.metadata.get("project_id")
        title = task.metadata.get("title")
        description = task.metadata.get("description")
        acceptance_criteria = task.metadata.get("acceptance_criteria")
        story_points = task.metadata.get("story_points")
        priority = task.metadata.get("priority", "medium")
        epic = task.metadata.get("epic")

        return self.create_user_story(
            project_id,
            title,
            description,
            acceptance_criteria,
            story_points,
            priority,
            epic,
        )

    async def _handle_create_sprint_task(self, task) -> Dict[str, Any]:
        """Handle create sprint task."""
        project_id = task.metadata.get("project_id")
        sprint_name = task.metadata.get("sprint_name")
        start_date = task.metadata.get("start_date")
        end_date = task.metadata.get("end_date")
        goal = task.metadata.get("goal")

        return self.create_sprint(project_id, sprint_name, start_date, end_date, goal)

    async def _handle_plan_sprint_task(self, task) -> Dict[str, Any]:
        """Handle plan sprint task."""
        sprint_id = task.metadata.get("sprint_id")
        story_ids = task.metadata.get("story_ids")

        return self.plan_sprint(sprint_id, story_ids)

    def create_agile_project(
        self,
        project_name: str,
        project_type: str = "scrum",
        sprint_length: int = None,
        team_size: int = 5,
    ) -> Dict[str, Any]:
        """Create a new agile project."""
        try:
            project_id = f"agile_{project_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

            project = AgileProject(
                id=project_id,
                project_name=project_name,
                sprint_duration=sprint_length or self.default_sprint_length,
                status="planning",
                metadata={
                    "project_type": project_type,
                    "team_size": team_size,
                    "created_at": datetime.now().isoformat(),
                },
            )

            self.agile_projects[project_id] = project
            logger.info(f"Created agile project: {project_name} ({project_id})")

            return {
                "success": True,
                "project_id": project_id,
                "message": f"Agile project '{project_name}' created successfully",
                "project": {
                    "project_id": project.id,
                    "name": project.project_name,
                    "project_type": project_type,
                    "sprint_length": project.sprint_duration,
                    "team_size": team_size,
                    "created_at": project.metadata.get("created_at"),
                    "status": project.status,
                },
            }

        except Exception as e:
            logger.error(f"Error creating agile project: {e}")
            return {"success": False, "error": str(e)}

    def create_user_story(
        self,
        project_id: str,
        title: str,
        description: str,
        acceptance_criteria: List[str],
        story_points: int = None,
        priority: str = "medium",
        epic: str = None,
    ) -> Dict[str, Any]:
        """Create a new user story."""
        try:
            if project_id not in self.agile_projects:
                return {"success": False, "error": f"Project {project_id} not found"}

            story_id = f"story_{uuid.uuid4().hex[:8]}"

            # Auto-estimate story points if not provided
            if story_points is None:
                story_points = self._auto_estimate_story_points(
                    description, acceptance_criteria
                )

            user_story = UserStory(
                story_id=story_id,
                project_id=project_id,
                title=title,
                description=description,
                acceptance_criteria=acceptance_criteria,
                story_points=story_points,
                priority=priority,
                epic=epic,
                status="backlog",
                created_at=datetime.now().isoformat(),
                assigned_to=None,
                sprint_id=None,
                estimated_hours=None,
                actual_hours=None,
                completed_at=None,
            )

            self.user_stories[story_id] = user_story

            # Update project metrics
            project = self.agile_projects[project_id]
            project.total_story_points += story_points

            logger.info(
                f"Created user story: {title} ({story_id}) with {story_points} points"
            )

            return {
                "success": True,
                "story_id": story_id,
                "message": f"User story '{title}' created successfully",
                "user_story": asdict(user_story),
            }

        except Exception as e:
            logger.error(f"Error creating user story: {e}")
            return {"success": False, "error": str(e)}

    def _auto_estimate_story_points(
        self, description: str, acceptance_criteria: List[str]
    ) -> int:
        """Auto-estimate story points based on complexity."""
        # Simple heuristic-based estimation
        complexity_score = 0

        # Description length factor
        complexity_score += len(description.split()) * 0.1

        # Acceptance criteria count factor
        complexity_score += len(acceptance_criteria) * 0.5

        # Keyword complexity factors
        complex_keywords = [
            "integration",
            "api",
            "database",
            "security",
            "performance",
            "testing",
        ]
        for keyword in complex_keywords:
            if keyword.lower() in description.lower():
                complexity_score += 1

        # Map complexity score to story points
        if complexity_score <= 2:
            return 1
        elif complexity_score <= 4:
            return 2
        elif complexity_score <= 6:
            return 3
        elif complexity_score <= 8:
            return 5
        elif complexity_score <= 10:
            return 8
        else:
            return 13

    def create_sprint(
        self,
        project_id: str,
        sprint_name: str,
        start_date: str = None,
        end_date: str = None,
        goal: str = None,
    ) -> Dict[str, Any]:
        """Create a new sprint."""
        try:
            if project_id not in self.agile_projects:
                return {"success": False, "error": f"Project {project_id} not found"}

            project = self.agile_projects[project_id]
            sprint_id = f"sprint_{uuid.uuid4().hex[:8]}"

            # Calculate dates if not provided
            if not start_date:
                start_date = datetime.now().isoformat()

            if not end_date:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = start_dt + timedelta(days=project.sprint_duration)
                end_date = end_dt.isoformat()

            sprint = Sprint(
                sprint_id=sprint_id,
                project_id=project_id,
                name=sprint_name,
                start_date=start_date,
                end_date=end_date,
                goal=goal or f"Complete sprint {sprint_name} objectives",
                status="planning",
                planned_stories=[],
                completed_stories=[],
                total_story_points=0,
                completed_story_points=0,
                team_velocity=0.0,
            )

            self.active_sprints[sprint_id] = sprint
            project.current_sprint = sprint_id

            logger.info(
                f"Created sprint: {sprint_name} ({sprint_id}) for project {project_id}"
            )

            return {
                "success": True,
                "sprint_id": sprint_id,
                "message": f"Sprint '{sprint_name}' created successfully",
                "sprint": asdict(sprint),
            }

        except Exception as e:
            logger.error(f"Error creating sprint: {e}")
            return {"success": False, "error": str(e)}

    def plan_sprint(self, sprint_id: str, story_ids: List[str]) -> Dict[str, Any]:
        """Plan a sprint by assigning user stories."""
        try:
            if sprint_id not in self.active_sprints:
                return {"success": False, "error": f"Sprint {sprint_id} not found"}

            sprint = self.active_sprints[sprint_id]
            project = self.agile_projects[sprint.project_id]

            # Validate stories
            valid_stories = []
            total_points = 0

            for story_id in story_ids:
                if story_id in self.user_stories:
                    story = self.user_stories[story_id]
                    if (
                        story.status == "backlog"
                        and story.project_id == sprint.project_id
                    ):
                        valid_stories.append(story)
                        total_points += story.story_points
                        story.status = "planned"
                        story.sprint_id = sprint_id
                    else:
                        logger.warning(f"Story {story_id} cannot be added to sprint")
                else:
                    logger.warning(f"Story {story_id} not found")

            # Update sprint
            sprint.planned_stories = [story.story_id for story in valid_stories]
            sprint.total_story_points = total_points
            sprint.status = "active"

            # Update project
            project.status = "active"

            logger.info(
                f"Planned sprint {sprint_id} with {len(valid_stories)} stories ({total_points} points)"
            )

            return {
                "success": True,
                "message": f"Sprint planned with {len(valid_stories)} stories",
                "planned_stories": len(valid_stories),
                "total_points": total_points,
                "sprint_status": sprint.status,
            }

        except Exception as e:
            logger.error(f"Error planning sprint: {e}")
            return {"success": False, "error": str(e)}

    def complete_user_story(
        self, story_id: str, actual_hours: float = None
    ) -> Dict[str, Any]:
        """Mark a user story as completed."""
        try:
            if story_id not in self.user_stories:
                return {"success": False, "error": f"Story {story_id} not found"}

            story = self.user_stories[story_id]
            story.status = "completed"
            story.actual_hours = actual_hours
            story.completed_at = datetime.now().isoformat()

            # Update sprint metrics
            if story.sprint_id and story.sprint_id in self.active_sprints:
                sprint = self.active_sprints[story.sprint_id]
                sprint.completed_stories.append(story_id)
                sprint.completed_story_points += story.story_points

                # Move from planned to completed
                if story_id in sprint.planned_stories:
                    sprint.planned_stories.remove(story_id)

            # Update project metrics
            project = self.agile_projects[story.project_id]
            project.completed_story_points += story.story_points

            logger.info(f"Completed user story: {story.title} ({story_id})")

            return {
                "success": True,
                "message": f"User story '{story.title}' completed",
                "story_status": story.status,
                "completed_points": story.story_points,
            }

        except Exception as e:
            logger.error(f"Error completing user story: {e}")
            return {"success": False, "error": str(e)}

    def calculate_team_velocity(
        self, project_id: str, sprint_count: int = None
    ) -> Dict[str, Any]:
        """Calculate team velocity based on completed sprints."""
        try:
            if project_id not in self.agile_projects:
                return {"success": False, "error": f"Project {project_id} not found"}

            project = self.agile_projects[project_id]
            sprint_count = sprint_count or self.velocity_calculation_sprints

            # Get completed sprints for this project
            completed_sprints = [
                sprint
                for sprint in self.active_sprints.values()
                if sprint.project_id == project_id and sprint.status == "completed"
            ]

            if not completed_sprints:
                return {
                    "success": False,
                    "error": "No completed sprints found for velocity calculation",
                }

            # Sort by completion date and take the most recent ones
            completed_sprints.sort(key=lambda x: x.end_date, reverse=True)
            recent_sprints = completed_sprints[:sprint_count]

            # Calculate velocity
            total_points = sum(
                sprint.completed_story_points for sprint in recent_sprints
            )
            average_velocity = total_points / len(recent_sprints)

            # Calculate velocity trend
            if len(recent_sprints) >= 2:
                recent_velocity = recent_sprints[0].completed_story_points
                previous_velocity = recent_sprints[1].completed_story_points
                velocity_trend = (
                    "increasing"
                    if recent_velocity > previous_velocity
                    else (
                        "decreasing"
                        if recent_velocity < previous_velocity
                        else "stable"
                    )
                )
            else:
                velocity_trend = "insufficient_data"

            logger.info(
                f"Calculated team velocity for project {project_id}: {average_velocity:.1f} points/sprint"
            )

            return {
                "success": True,
                "message": f"Team velocity calculated successfully for project {project_id}: {average_velocity:.1f} points/sprint",
                "project_id": project_id,
                "average_velocity": round(average_velocity, 1),
                "velocity_trend": velocity_trend,
                "sprints_analyzed": len(recent_sprints),
                "total_points": total_points,
                "velocity_range": {
                    "min": min(
                        sprint.completed_story_points for sprint in recent_sprints
                    ),
                    "max": max(
                        sprint.completed_story_points for sprint in recent_sprints
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error calculating team velocity: {e}")
            return {"success": False, "error": str(e)}

    def get_sprint_burndown(self, sprint_id: str) -> Dict[str, Any]:
        """Generate burndown chart data for a sprint."""
        try:
            if sprint_id not in self.active_sprints:
                return {"success": False, "error": f"Sprint {sprint_id} not found"}

            sprint = self.active_sprints[sprint_id]

            # Calculate burndown data
            total_points = sprint.total_story_points
            remaining_points = total_points - sprint.completed_story_points

            # Generate daily burndown data
            start_date = datetime.fromisoformat(sprint.start_date)
            end_date = datetime.fromisoformat(sprint.end_date)
            sprint_days = (end_date - start_date).days

            burndown_data = []
            for day in range(sprint_days + 1):
                current_date = start_date + timedelta(days=day)
                ideal_points = total_points - (total_points / sprint_days) * day

                burndown_data.append(
                    {
                        "day": day,
                        "date": current_date.isoformat(),
                        "ideal_points": round(ideal_points, 1),
                        "actual_points": (
                            remaining_points if day == sprint_days else None
                        ),
                        "remaining_points": (
                            remaining_points if day == sprint_days else None
                        ),
                    }
                )

            logger.info(f"Generated burndown data for sprint {sprint_id}")

            return {
                "success": True,
                "message": f"Sprint burndown data generated successfully for sprint {sprint_id}",
                "sprint_id": sprint_id,
                "total_points": total_points,
                "completed_points": sprint.completed_story_points,
                "remaining_points": remaining_points,
                "sprint_days": sprint_days,
                "burndown_data": burndown_data,
                "completion_percentage": (
                    round((sprint.completed_story_points / total_points) * 100, 1)
                    if total_points > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error generating burndown data: {e}")
            return {"success": False, "error": str(e)}

    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status and metrics."""
        try:
            if project_id not in self.agile_projects:
                return {"success": False, "error": f"Project {project_id} not found"}

            project = self.agile_projects[project_id]

            # Get project stories
            project_stories = [
                story
                for story in self.user_stories.values()
                if story.project_id == project_id
            ]

            # Get project sprints
            project_sprints = [
                sprint
                for sprint in self.active_sprints.values()
                if sprint.project_id == project_id
            ]

            # Calculate metrics
            total_stories = len(project_stories)
            completed_stories = len(
                [s for s in project_stories if s.status == "completed"]
            )
            in_progress_stories = len(
                [s for s in project_stories if s.status == "in_progress"]
            )
            backlog_stories = len([s for s in project_stories if s.status == "backlog"])

            # Calculate velocity
            velocity_data = self.calculate_team_velocity(project_id)

            logger.info(f"Retrieved project status for {project_id}")

            return {
                "success": True,
                "message": f"Project status retrieved successfully for {project.project_name}",
                "project": project.to_dict(),
                "metrics": {
                    "total_stories": total_stories,
                    "completed_stories": completed_stories,
                    "in_progress_stories": in_progress_stories,
                    "backlog_stories": backlog_stories,
                    "completion_percentage": (
                        round((completed_stories / total_stories) * 100, 1)
                        if total_stories > 0
                        else 0
                    ),
                    "total_story_points": project.total_story_points,
                    "completed_story_points": project.completed_story_points,
                    "points_completion_percentage": (
                        round(
                            (
                                project.completed_story_points
                                / project.total_story_points
                            )
                            * 100,
                            1,
                        )
                        if project.total_story_points > 0
                        else 0
                    ),
                },
                "sprints": {
                    "total": len(project_sprints),
                    "active": len([s for s in project_sprints if s.status == "active"]),
                    "completed": len(
                        [s for s in project_sprints if s.status == "completed"]
                    ),
                    "planning": len(
                        [s for s in project_sprints if s.status == "planning"]
                    ),
                },
                "velocity": velocity_data if velocity_data["success"] else None,
            }

        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {"success": False, "error": str(e)}

    def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status and capabilities."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "agile_projects": len(self.agile_projects),
            "active_sprints": len(self.active_sprints),
            "user_stories": len(self.user_stories),
            "team_members": len(self.team_members),
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "last_activity": (
                self.last_activity.isoformat() if self.last_activity else None
            ),
        }
