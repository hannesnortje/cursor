"""
Simple LLM-Based Coordinator Agent for orchestrating the AI agent system.

This coordinator uses the simple decision engine with rule-based fallback,
providing intelligent, context-aware protocol decisions.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from ..base.base_agent import BaseAgent, AgentType, AgentCapability, AgentTask
from ..registry import AgentRegistry
from .pdca_framework import PDCAFramework, PDCACycle, PDCAObjective
from src.llm.simple_decision_engine import SimpleDecisionEngine, ActionType, PDCAPhase, ProtocolDecision


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
    technology_stack: List[str] = field(default_factory=list)
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
            "technology_stack": self.technology_stack,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }


class SimpleCoordinatorAgent(BaseAgent):
    """Simple LLM-Based Coordinator Agent that orchestrates the entire AI agent system."""
    
    def __init__(self, agent_id: str = "simple_coordinator_001", name: str = "Simple System Coordinator"):
        """Initialize the simple coordinator agent."""
        capabilities = [
            AgentCapability(
                name="intelligent_planning",
                description="Use LLM and rule-based decisions for intelligent project planning",
                version="2.0.0"
            ),
            AgentCapability(
                name="pdca_management",
                description="Manage PDCA cycles with intelligent decisions",
                version="2.0.0"
            ),
            AgentCapability(
                name="agent_coordination",
                description="Coordinate and delegate tasks to other agents intelligently",
                version="2.0.0"
            ),
            AgentCapability(
                name="technology_recommendations",
                description="Provide framework-agnostic technology recommendations",
                version="2.0.0"
            ),
            AgentCapability(
                name="conversation_management",
                description="Maintain context-aware conversations",
                version="2.0.0"
            )
        ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.COORDINATOR,
            name=name,
            description="Simple LLM-powered central orchestrator for the AI agent system",
            capabilities=capabilities
        )
        
        # Initialize simple decision engine
        self.decision_engine = SimpleDecisionEngine()
        
        # Initialize coordinator-specific components
        self.pdca_framework = PDCAFramework()
        self.project_plans: Dict[str, ProjectPlan] = {}
        self.agent_registry: Optional[AgentRegistry] = None
        self.active_projects: List[str] = []
        
        self.logger.info(f"Simple Coordinator Agent {name} initialized")
    
    async def initialize(self) -> bool:
        """Initialize the simple coordinator agent."""
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
            
            self.logger.info("Simple Coordinator Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Simple Coordinator Agent initialization failed: {e}")
            return False
    
    def process_message(self, message: str) -> Dict[str, Any]:
        """Process user message using simple decision engine."""
        try:
            self.logger.info(f"Processing message: {message[:100]}...")
            
            # Make decision using simple decision engine
            decision = self.decision_engine.make_decision(message)
            
            if not decision:
                return {
                    "success": False,
                    "error": "Failed to make decision",
                    "response": "I encountered an error while processing your request. Please try again."
                }
            
            # Route decision to appropriate handler
            response = self._route_decision(decision, message)
            
            # Update conversation state
            self.decision_engine.update_conversation_state(message, decision, response.get("response", ""))
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request. Please try again."
            }
    
    def _route_decision(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Route decision to appropriate handler."""
        try:
            action_type = decision.action_type
            
            if action_type == ActionType.ASK_QUESTIONS:
                return self._handle_ask_questions(decision, message)
            elif action_type == ActionType.PROVIDE_RECOMMENDATIONS:
                return self._handle_provide_recommendations(decision, message)
            elif action_type == ActionType.CREATE_AGENTS:
                return self._handle_create_agents(decision, message)
            elif action_type == ActionType.CONTINUE_PLANNING:
                return self._handle_continue_planning(decision, message)
            elif action_type == ActionType.START_IMPLEMENTATION:
                return self._handle_start_implementation(decision, message)
            elif action_type == ActionType.CLARIFY_REQUIREMENTS:
                return self._handle_clarify_requirements(decision, message)
            elif action_type == ActionType.TECHNOLOGY_SELECTION:
                return self._handle_technology_selection(decision, message)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action type: {action_type}",
                    "response": "I'm not sure how to handle that request. Could you please clarify?"
                }
                
        except Exception as e:
            self.logger.error(f"Error routing decision: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request. Please try again."
            }
    
    def _handle_ask_questions(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle asking questions for project details."""
        questions = [
            "What is the main purpose of this project?",
            "Who are the target users?",
            "What key features do you want to include?",
            "What technology preferences do you have?",
            "What is your team size and expertise?",
            "What is your preferred timeline?"
        ]
        
        response = f"""🎯 **Starting PDCA Framework for your project!**

📋 **PLAN Phase - Let me gather the essential information:**

{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}

Please share your thoughts on these questions, and I'll guide you through the planning process using the PDCA framework."""
        
        return {
            "success": True,
            "response": response,
            "phase": "plan",
            "next_steps": "awaiting_project_details",
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_provide_recommendations(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle providing technology recommendations."""
        technology_preferences = decision.technology_preferences or []
        
        # Generate framework-agnostic recommendations
        recommendations = self._generate_technology_recommendations(technology_preferences)
        
        response = f"""🎯 **Excellent! Based on your project details, here's my technology stack and architecture recommendation:**

{recommendations}

## **🚀 Next Steps - Agent Strategy**

Now let's discuss the **implementation process** and **agent strategy**:

🤖 **Proposed Core Agents:**
- **Agile/Scrum Agent**: Sprint planning, user stories, retrospectives
- **Frontend Agent**: {technology_preferences[0] if technology_preferences else 'Frontend'} development, UI/UX
- **Backend Agent**: Backend API development, database design
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
3. Any particular areas where you'd like extra support?
4. How would you like the agents to collaborate and communicate?

Let's discuss this together and customize the agent team for your specific needs!"""
        
        return {
            "success": True,
            "response": response,
            "phase": "plan",
            "next_steps": "agent_strategy_discussion",
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_create_agents(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle creating specialized agents."""
        agent_types = decision.agent_types_needed or ["agile", "frontend", "backend", "testing"]
        
        # Create agents
        agents_created = []
        for agent_type in agent_types:
            result = asyncio.run(self.create_agent(
                agent_type=agent_type,
                name=f"{agent_type.title()} Agent",
                description=f"Specialized {agent_type} agent for project development",
                capabilities=[f"{agent_type}_development", "project_management"]
            ))
            if result.get("success"):
                agents_created.append(result["agent_info"])
        
        response = f"""🎉 **Agent Team Created Successfully!**

✅ **Core Agents Created ({len(agents_created)} agents):**
{chr(10).join([f"- **{agent['name']}**: {agent['description']}" for agent in agents_created])}

📋 **Next Steps:**
1. **Sprint Planning**: Agile Agent will create the first sprint plan
2. **Architecture Design**: Backend Agent will design the API structure
3. **UI/UX Planning**: Frontend Agent will plan the component architecture
4. **Test Strategy**: Testing Agent will create the testing framework

🚀 **Ready to start development!** The agent team is now active and ready to collaborate on your project.

Would you like me to:
- Start sprint planning with the Agile Agent?
- Begin architecture design with the Backend Agent?
- Plan the UI/UX with the Frontend Agent?
- Set up the testing framework with the Testing Agent?"""
        
        return {
            "success": True,
            "response": response,
            "phase": "do",
            "next_steps": "agent_collaboration",
            "agents_created": len(agents_created),
            "agent_details": agents_created,
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_continue_planning(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle continuing PDCA planning."""
        return {
            "success": True,
            "response": "Thank you for that information! Let me continue with the planning process...",
            "phase": "plan",
            "next_steps": "continue_planning",
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_start_implementation(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle starting implementation phase."""
        return {
            "success": True,
            "response": "Great! Let's start the implementation phase. I'll coordinate with the specialized agents to begin development.",
            "phase": "do",
            "next_steps": "implementation",
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_clarify_requirements(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle clarifying requirements."""
        clarification_questions = [
            "Could you provide more details about that?",
            "What specific requirements do you have?",
            "How would you like this to work?"
        ]
        
        response = f"""I'd like to clarify a few things to better understand your needs:

{chr(10).join([f"- {q}" for q in clarification_questions])}

This will help me provide more accurate recommendations and create the right agent team for your project."""
        
        return {
            "success": True,
            "response": response,
            "phase": "plan",
            "next_steps": "clarification",
            "timestamp": datetime.now().isoformat()
        }
    
    def _handle_technology_selection(self, decision: ProtocolDecision, message: str) -> Dict[str, Any]:
        """Handle technology selection assistance."""
        technology_preferences = decision.technology_preferences or []
        
        response = f"""Let me help you with technology selection for your project.

Based on your requirements, I recommend considering these technologies:

{chr(10).join([f"- **{tech}**: [Brief description]" for tech in technology_preferences])}

Would you like me to:
1. Provide more detailed recommendations for any of these technologies?
2. Suggest additional technologies that might be suitable?
3. Help you compare different options?
4. Create specialized agents for your chosen technology stack?"""
        
        return {
            "success": True,
            "response": response,
            "phase": "plan",
            "next_steps": "technology_discussion",
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_technology_recommendations(self, preferences: List[str]) -> str:
        """Generate framework-agnostic technology recommendations."""
        if not preferences:
            return """## **🏗️ Recommended Technology Stack**

### **Frontend Stack**
- **Modern Framework**: Choose based on your team's expertise and project requirements
- **TypeScript**: For type safety and better development experience
- **Build Tool**: Vite or Webpack for fast development and building
- **UI Library**: Component library that matches your chosen framework
- **State Management**: Appropriate state management solution for your framework

### **Backend Stack**
- **Runtime**: Node.js, Python, or your preferred backend language
- **Framework**: Express.js, FastAPI, or equivalent for your language
- **Database**: PostgreSQL for relational data, MongoDB for document-based
- **Authentication**: JWT with secure password hashing
- **API**: RESTful or GraphQL based on your needs

### **Infrastructure**
- **Containerization**: Docker for consistent deployment
- **Cloud Platform**: AWS, Azure, or Google Cloud
- **CI/CD**: GitHub Actions, GitLab CI, or similar
- **Monitoring**: Application and infrastructure monitoring tools"""
        
        # Generate recommendations based on preferences
        frontend_recs = []
        backend_recs = []
        
        for pref in preferences:
            if any(fw in pref.lower() for fw in ['vue', 'react', 'angular', 'svelte']):
                frontend_recs.append(f"- **{pref}**: Modern frontend framework")
            elif any(tech in pref.lower() for tech in ['node', 'python', 'java', 'c#', 'go']):
                backend_recs.append(f"- **{pref}**: Backend runtime/framework")
            elif any(db in pref.lower() for db in ['postgres', 'mysql', 'mongodb', 'redis']):
                backend_recs.append(f"- **{pref}**: Database solution")
        
        recommendations = "## **🏗️ Recommended Technology Stack**\n\n"
        
        if frontend_recs:
            recommendations += "### **Frontend Stack**\n" + "\n".join(frontend_recs) + "\n\n"
        
        if backend_recs:
            recommendations += "### **Backend Stack**\n" + "\n".join(backend_recs) + "\n\n"
        
        recommendations += """### **Additional Recommendations**
- **TypeScript**: For type safety across the stack
- **Docker**: For containerization and deployment
- **Git**: For version control and collaboration
- **Testing**: Comprehensive testing strategy
- **CI/CD**: Automated deployment pipeline"""
        
        return recommendations
    
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
    
    def reset_conversation(self) -> None:
        """Reset conversation state for new project."""
        self.decision_engine.reset_conversation_state()
        self.logger.info("Conversation state reset for new project")
    
    async def _execute_task_impl(self, task: AgentTask) -> Dict[str, Any]:
        """Execute a task assigned to the coordinator."""
        try:
            task_type = task.type
            
            if task_type == "process_message":
                # Process a message using the decision engine
                message = task.metadata.get("message", "")
                result = self.process_message(message)
                return result
                
            elif task_type == "create_agent":
                # Create a new agent
                agent_type = task.metadata.get("agent_type", "general")
                name = task.metadata.get("name", f"{agent_type.title()} Agent")
                description = task.metadata.get("description", f"Specialized {agent_type} agent")
                capabilities = task.metadata.get("capabilities", [])
                
                result = await self.create_agent(agent_type, name, description, capabilities)
                return result
                
            elif task_type == "reset_conversation":
                # Reset conversation state
                self.reset_conversation()
                return {"success": True, "message": "Conversation state reset"}
                
            else:
                return {"success": False, "error": f"Unknown task type: {task_type}"}
                
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    # Additional methods from the original coordinator can be added here
    # For now, focusing on the core LLM-based functionality
