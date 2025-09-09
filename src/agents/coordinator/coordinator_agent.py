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
            self.register_message_handler("project_generation", self._handle_project_generation_request)
            
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
            # Create agent ID
            agent_id = f"agent_{agent_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Store agent info
            agent_info = {
                "agent_id": agent_id,
                "agent_type": agent_type,
                "name": name,
                "description": description,
                "capabilities": capabilities,
                "status": "active",
                "created_at": datetime.now().isoformat()
            }
            
            # Add to active agents list
            if not hasattr(self, 'active_agents'):
                self.active_agents = []
            self.active_agents.append(agent_info)
            
            self.logger.info(f"Created agent: {name} ({agent_type})")
            
            return {
                "success": True,
                "agent_info": agent_info,
                "message": f"✅ {name} created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create agent {name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"❌ Failed to create {name}"
            }
    
    def start_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Start PDCA planning conversation with the user."""
        try:
            # Analyze the message to understand the project request
            message_lower = message.lower()
            
            # Check if this is a new project request
            if any(word in message_lower for word in ["start", "create", "build", "develop", "new project"]):
                return {
                    "success": True,
                    "response": """🎯 Starting PDCA Framework for your project!

📋 PLAN Phase - Let me gather the essential information:

1. **Project Goals & Objectives:**
   - What is the main purpose of this project?
   - Who are the target users?
   - What key features do you want to include?

2. **Current State Analysis:**
   - What existing solutions or platforms are you building upon?
   - What are the main challenges you're trying to solve?

3. **Target State Definition:**
   - What does success look like for this project?
   - What specific outcomes do you want to achieve?

4. **Implementation Strategy:**
   - What is your preferred timeline?
   - Do you have any specific technical requirements?
   - What's your team size and expertise?

Please share your thoughts on these questions, and I'll guide you through the planning process.""",
                    "phase": "plan",
                    "next_steps": "awaiting_project_details",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "response": "I'd be happy to help you with your project! Could you tell me more about what you'd like to build or work on?",
                    "phase": "plan",
                    "next_steps": "awaiting_project_details",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error in start_pdca_planning: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while starting the PDCA planning. Let me try a different approach."
            }
    
    def continue_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Continue PDCA planning based on user input."""
        try:
            # Analyze the message to understand what information the user is providing
            message_lower = message.lower()
            
            # Check if user wants to create agents (prioritize this check)
            if any(phrase in message_lower for phrase in ["create agents", "let's create", "please create", "specialized agents", "agent team", "create the", "create an agile", "create a frontend", "create a backend", "create a testing"]):
                return self._handle_agent_creation_request(message)
            
            # Check if user is providing project details
            elif any(word in message_lower for word in ["purpose", "goal", "objective", "dashboard", "react", "typescript", "vue", "project management", "web application"]):
                return {
                    "success": True,
                    "response": """✅ Thank you for the project information! Now let's discuss the **implementation process** and **agent strategy**:

🤖 **Proposed Core Agents:**
- **Agile/Scrum Agent**: Sprint planning, user stories, retrospectives
- **Frontend Agent**: Vue.js/TypeScript components, UI/UX
- **Backend Agent**: Node.js/Express API development, database design
- **Testing Agent**: Test strategies, coverage, automation
- **Documentation Agent**: Project docs, API documentation

🔧 **Specialized Agents to Consider:**
- **Git Agent**: Branch management, commit strategies, conflict resolution
- **Logging Agent**: Application logging, monitoring, debugging
- **Security Agent**: Security reviews, vulnerability scanning
- **Performance Agent**: Performance optimization, monitoring
- **Deployment Agent**: CI/CD, deployment automation

💭 **Questions for You:**
1. Which specialized agents would be most valuable for your project?
2. Do you have any specific workflows or processes you'd like automated?
3. Any particular areas where you'd like extra support (logging, git management, etc.)?
4. How would you like the agents to collaborate and communicate?

Let's discuss this together and customize the agent team for your specific needs!""",
                    "phase": "plan",
                    "next_steps": "agent_strategy_discussion",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "response": "Thank you for that information! Could you provide more details about your project goals and requirements?",
                    "phase": "plan",
                    "next_steps": "awaiting_project_details",
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            self.logger.error(f"Error in continue_pdca_planning: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while continuing the PDCA planning. Let me try a different approach."
            }
    
    def _handle_agent_creation_request(self, message: str) -> Dict[str, Any]:
        """Handle requests to create specialized agents."""
        try:
            # Create the core agents for the project
            agents_created = []
            
            # Create Agile Agent
            agile_result = asyncio.run(self.create_agent(
                agent_type="agile",
                name="Agile/Scrum Agent",
                description="Sprint planning, user stories, retrospectives",
                capabilities=["sprint_planning", "user_stories", "retrospectives", "velocity_tracking"]
            ))
            if agile_result.get("success"):
                agents_created.append(agile_result["agent_info"])
            
            # Create Frontend Agent
            frontend_result = asyncio.run(self.create_agent(
                agent_type="frontend",
                name="Frontend Agent",
                description="Vue.js/TypeScript components, UI/UX development",
                capabilities=["vue_development", "typescript", "ui_ux", "component_design"]
            ))
            if frontend_result.get("success"):
                agents_created.append(frontend_result["agent_info"])
            
            # Create Backend Agent
            backend_result = asyncio.run(self.create_agent(
                agent_type="backend",
                name="Backend Agent",
                description="Node.js/Express API development, database design",
                capabilities=["nodejs", "express", "api_development", "database_design"]
            ))
            if backend_result.get("success"):
                agents_created.append(backend_result["agent_info"])
            
            # Create Testing Agent
            testing_result = asyncio.run(self.create_agent(
                agent_type="testing",
                name="Testing Agent",
                description="Test strategies, coverage, automation",
                capabilities=["test_planning", "test_automation", "coverage_analysis", "quality_assurance"]
            ))
            if testing_result.get("success"):
                agents_created.append(testing_result["agent_info"])
            
            return {
                "success": True,
                "response": f"""🎉 **Agent Team Created Successfully!**

✅ **Core Agents Created ({len(agents_created)} agents):**
- **Agile/Scrum Agent**: Ready for sprint planning and user story management
- **Frontend Agent**: Ready for Vue.js/TypeScript development
- **Backend Agent**: Ready for Node.js/Express API development  
- **Testing Agent**: Ready for test strategies and automation

📋 **Next Steps:**
1. **Sprint Planning**: Agile Agent will create the first sprint plan
2. **Architecture Design**: Backend Agent will design the API structure
3. **UI/UX Planning**: Frontend Agent will plan the component architecture
4. **Test Strategy**: Testing Agent will create the testing framework

🚀 **Ready to start development!** The agent team is now active and ready to collaborate on your project management system.

Would you like me to:
- Start sprint planning with the Agile Agent?
- Begin architecture design with the Backend Agent?
- Plan the UI/UX with the Frontend Agent?
- Set up the testing framework with the Testing Agent?""",
                "phase": "do",
                "next_steps": "agent_collaboration",
                "agents_created": len(agents_created),
                "agent_details": agents_created,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error creating agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while creating the agent team. Let me try a different approach."
            }
    
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
    
    # Project Generation Methods
    async def create_project_from_template(self, template_id: str, project_name: str, 
                                         target_path: str = ".", 
                                         customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a project using a template through the Project Generation Agent."""
        try:
            self.logger.info(f"Coordinator: Creating project '{project_name}' using template '{template_id}'")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate project generation to the agent
            result = project_gen_agent.generate_project(template_id, project_name, target_path, customizations)
            
            if result["success"]:
                self.logger.info(f"Coordinator: Project '{project_name}' created successfully")
                # Create a project plan for the generated project
                await self._create_project_plan_for_generated_project(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to create project from template: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_custom_project(self, project_name: str, language: str, 
                                   custom_structure: Dict[str, Any] = None,
                                   target_path: str = ".") -> Dict[str, Any]:
        """Create a custom project through the Project Generation Agent."""
        try:
            self.logger.info(f"Coordinator: Creating custom project '{project_name}' in {language}")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate custom project creation to the agent
            result = project_gen_agent.create_custom_project(project_name, language, custom_structure, target_path)
            
            if result["success"]:
                self.logger.info(f"Coordinator: Custom project '{project_name}' created successfully")
                # Create a project plan for the generated project
                await self._create_project_plan_for_generated_project(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to create custom project: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_project_templates(self, language: Optional[str] = None, 
                                   category: Optional[str] = None) -> Dict[str, Any]:
        """List available project templates through the Project Generation Agent."""
        try:
            self.logger.info(f"Coordinator: Listing project templates (language: {language}, category: {category})")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate template listing to the agent
            result = project_gen_agent.list_project_templates(language, category)
            
            self.logger.info(f"Coordinator: Retrieved {result.get('total_count', 0)} project templates")
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to list project templates: {e}")
            return {"success": False, "error": str(e)}
    
    async def customize_project_template(self, template_id: str, 
                                       customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Customize a project template through the Project Generation Agent."""
        try:
            self.logger.info(f"Coordinator: Customizing template '{template_id}'")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate template customization to the agent
            result = project_gen_agent.customize_project_template(template_id, customizations)
            
            if result["success"]:
                self.logger.info(f"Coordinator: Template '{template_id}' customized successfully")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to customize template: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_generated_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get status of a generated project through the Project Generation Agent."""
        try:
            self.logger.info(f"Coordinator: Getting status for generated project '{project_id}'")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate status retrieval to the agent
            result = project_gen_agent.get_project_status(project_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to get generated project status: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_generated_projects(self) -> Dict[str, Any]:
        """List all generated projects through the Project Generation Agent."""
        try:
            self.logger.info("Coordinator: Listing all generated projects")
            
            # Create or get Project Generation Agent
            project_gen_agent = await self._get_or_create_project_generation_agent()
            if not project_gen_agent:
                return {"success": False, "error": "Failed to create Project Generation Agent"}
            
            # Delegate project listing to the agent
            result = project_gen_agent.list_generated_projects()
            
            self.logger.info(f"Coordinator: Retrieved {result.get('total_count', 0)} generated projects")
            return result
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to list generated projects: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_or_create_project_generation_agent(self):
        """Get or create a Project Generation Agent."""
        try:
            if not self.agent_registry:
                return None
            
            # Check if Project Generation Agent already exists
            existing_agent = self.agent_registry.get_agent_by_type("project_generation")
            if existing_agent:
                return existing_agent
            
            # Create new Project Generation Agent
            self.logger.info("Coordinator: Creating new Project Generation Agent")
            agent_result = await self.create_agent(
                agent_type="project_generation",
                name="Project Generation Agent",
                description="Agent for generating projects from templates and custom structures"
            )
            
            if agent_result.get("success"):
                return agent_result.get("agent")
            else:
                self.logger.error(f"Coordinator: Failed to create Project Generation Agent: {agent_result.get('error')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Coordinator: Error getting/creating Project Generation Agent: {e}")
            return None
    
    async def _create_project_plan_for_generated_project(self, generation_result: Dict[str, Any]):
        """Create a project plan for a generated project."""
        try:
            project_name = generation_result.get("project_name", "Unknown Project")
            project_id = generation_result.get("project_id", "unknown")
            language = generation_result.get("language", "unknown")
            
            # Create a basic project plan
            project_plan = await self.create_project(
                name=f"Generated: {project_name}",
                description=f"Project generated using {language} template",
                objectives=[f"Develop {project_name} using {language}"],
                success_criteria=[f"Project structure created successfully", f"Build system configured"],
                timeline={"estimated_duration": "1 week"},
                resources=[f"{language} development environment"],
                risks=["Template may not fit exact requirements"]
            )
            
            if project_plan:
                self.logger.info(f"Coordinator: Created project plan for generated project '{project_name}'")
                # Link the generated project to the project plan
                generation_result["project_plan_id"] = project_plan.id
            
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to create project plan for generated project: {e}")
    
    async def _handle_project_generation_request(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle project generation requests."""
        try:
            request_type = message_data.get("type")
            
            if request_type == "create_from_template":
                return await self.create_project_from_template(
                    template_id=message_data["template_id"],
                    project_name=message_data["project_name"],
                    target_path=message_data.get("target_path", "."),
                    customizations=message_data.get("customizations", {})
                )
            elif request_type == "create_custom":
                return await self.create_custom_project(
                    project_name=message_data["project_name"],
                    language=message_data["language"],
                    custom_structure=message_data.get("custom_structure", {}),
                    target_path=message_data.get("target_path", ".")
                )
            elif request_type == "list_templates":
                return await self.list_project_templates(
                    language=message_data.get("language"),
                    category=message_data.get("category")
                )
            elif request_type == "customize_template":
                return await self.customize_project_template(
                    template_id=message_data["template_id"],
                    customizations=message_data["customizations"]
                )
            elif request_type == "get_status":
                return await self.get_generated_project_status(
                    project_id=message_data["project_id"]
                )
            elif request_type == "list_projects":
                return await self.list_generated_projects()
            else:
                return {"success": False, "error": f"Unknown project generation request type: {request_type}"}
                
        except Exception as e:
            self.logger.error(f"Coordinator: Failed to handle project generation request: {e}")
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
