"""Enhanced AutoGen Integration for Phase 9.2 - Sophisticated Conversation Engine."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

try:
    from autogen import AssistantAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("AutoGen not available. Install with: pip install pyautogen")

from .llm_gateway import LLMGateway, LLMModel, ModelType
from ..database.enhanced_vector_store import EnhancedVectorStore

logger = logging.getLogger(__name__)


@dataclass
class ConversationContext:
    """Context for AutoGen conversations."""
    conversation_id: str
    project_id: str
    participants: List[str]
    conversation_type: str  # "sprint_planning", "code_review", "general", etc.
    context_data: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class AgentRole:
    """Dynamic agent role configuration."""
    role_name: str
    capabilities: List[str]
    system_message: str
    preferred_models: List[str] = field(default_factory=list)
    max_tokens: int = 4096
    temperature: float = 0.7
    specializations: List[str] = field(default_factory=list)


class EnhancedAutoGenAgent:
    """Enhanced AutoGen agent with dynamic role assignment and project integration."""
    
    def __init__(self, agent_id: str, role: AgentRole, project_id: str = None):
        self.agent_id = agent_id
        self.role = role
        self.project_id = project_id
        self.autogen_agent = None
        self.conversation_history = []
        self.vector_store = None
        self.llm_gateway = LLMGateway()
        
        # Initialize vector store for project-specific memory
        if project_id:
            self.vector_store = EnhancedVectorStore(project_id=project_id)
        
        # Create AutoGen agent
        self._create_autogen_agent()
    
    def _create_autogen_agent(self):
        """Create AutoGen agent with dynamic configuration."""
        if not AUTOGEN_AVAILABLE:
            logger.warning(f"AutoGen not available, creating mock agent for {self.agent_id}")
            return
        
        try:
            # Get best model for this agent's role (handle event loop)
            try:
                model = asyncio.run(self._select_best_model_for_role())
            except RuntimeError:
                # If we're already in an event loop, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                model = loop.run_until_complete(self._select_best_model_for_role())
                loop.close()
            
            # Configure LLM for AutoGen
            llm_config = {
                "config_list": [
                    {
                        "model": model.name,
                        "api_base": model.api_base,
                        "api_key": model.api_key,
                        "temperature": self.role.temperature,
                        "max_tokens": self.role.max_tokens,
                    }
                ],
                "timeout": 60,
                "max_retries": 3
            }
            
            # Create AutoGen agent
            self.autogen_agent = AssistantAgent(
                name=self.agent_id,
                system_message=self.role.system_message,
                llm_config=llm_config,
                human_input_mode="NEVER",  # Fully autonomous
                max_consecutive_auto_reply=10
            )
            
            logger.info(f"Created enhanced AutoGen agent: {self.agent_id} with role: {self.role.role_name}")
            
        except Exception as e:
            logger.error(f"Failed to create AutoGen agent {self.agent_id}: {e}")
            self.autogen_agent = None
    
    async def _select_best_model_for_role(self) -> LLMModel:
        """Select the best LLM model for this agent's role."""
        try:
            # Determine task type based on role
            task_type = "general"
            if any(spec in self.role.specializations for spec in ["coding", "development", "programming"]):
                task_type = "coding"
            elif any(spec in self.role.specializations for spec in ["creative", "writing", "design"]):
                task_type = "creative"
            elif any(spec in self.role.specializations for spec in ["analysis", "reasoning", "research"]):
                task_type = "analysis"
            
            # Use preferred models if available
            if self.role.preferred_models:
                available_models = await self.llm_gateway.get_available_models()
                for preferred_model in self.role.preferred_models:
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if model.name == preferred_model and model.is_available:
                                    return model
            
            # Fallback to intelligent selection
            return await self.llm_gateway.select_best_model(task_type, self.role.role_name)
            
        except Exception as e:
            logger.error(f"Failed to select model for {self.agent_id}: {e}")
            # Return a basic fallback model
            return LLMModel(
                name="gpt-4",
                provider="cursor",
                model_type=ModelType.GENERAL,
                api_base="cursor://builtin",
                is_available=True
            )
    
    async def participate_in_conversation(self, group_chat: 'GroupChat', 
                                        message: str = None) -> str:
        """Participate in a group conversation."""
        if not self.autogen_agent:
            return f"[Mock Agent {self.agent_id}] I would respond to: {message or 'the conversation'}"
        
        try:
            # Store conversation context
            if self.vector_store:
                await self._store_conversation_context(message, group_chat)
            
            # Let AutoGen handle the conversation
            if message:
                response = self.autogen_agent.generate_reply(
                    messages=[{"role": "user", "content": message}],
                    sender=group_chat
                )
            else:
                # AutoGen will determine when to speak
                response = self.autogen_agent.generate_reply(
                    messages=group_chat.messages,
                    sender=group_chat
                )
            
            # Store the response
            self.conversation_history.append({
                "timestamp": datetime.now(),
                "message": message,
                "response": response,
                "agent_id": self.agent_id
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in conversation for {self.agent_id}: {e}")
            return f"[Error] {self.agent_id} encountered an error: {str(e)}"
    
    async def _store_conversation_context(self, message: str, group_chat: 'GroupChat'):
        """Store conversation context in vector database."""
        try:
            if not self.vector_store or not message:
                return
            
            # Create conversation point
            conversation_data = {
                "agent_id": self.agent_id,
                "role": self.role.role_name,
                "message": message,
                "conversation_type": "autogen_group_chat",
                "participants": [agent.name for agent in group_chat.agents],
                "project_id": self.project_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in vector database
            await self.vector_store.store_conversation(
                message=message,
                response="",  # Will be filled by the actual response
                agent_id=self.agent_id,
                context_data=conversation_data
            )
            
        except Exception as e:
            logger.error(f"Failed to store conversation context: {e}")


class EnhancedGroupChat:
    """Enhanced AutoGen group chat with project integration and workflow management."""
    
    def __init__(self, chat_id: str, project_id: str = None):
        self.chat_id = chat_id
        self.project_id = project_id
        self.agents: List[EnhancedAutoGenAgent] = []
        self.group_chat = None
        self.chat_manager = None
        self.conversation_context = None
        self.workflow_templates = {}
        
        # Initialize conversation context
        self.conversation_context = ConversationContext(
            conversation_id=chat_id,
            project_id=project_id or "default",
            participants=[],
            conversation_type="general"
        )
    
    def add_agent(self, agent: EnhancedAutoGenAgent):
        """Add an agent to the group chat."""
        self.agents.append(agent)
        self.conversation_context.participants.append(agent.agent_id)
        
        # Create AutoGen group chat if we have agents
        if len(self.agents) >= 2 and AUTOGEN_AVAILABLE:
            self._create_autogen_group_chat()
    
    def _create_autogen_group_chat(self):
        """Create AutoGen group chat with all agents."""
        if not AUTOGEN_AVAILABLE:
            return
        
        try:
            # Get AutoGen agents (filter out None values)
            autogen_agents = [agent.autogen_agent for agent in self.agents if agent.autogen_agent]
            
            if len(autogen_agents) < 2:
                logger.warning("Need at least 2 AutoGen agents for group chat")
                return
            
            # Create group chat
            self.group_chat = GroupChat(
                agents=autogen_agents,
                messages=[],
                max_round=20
            )
            
            # Create group chat manager
            self.chat_manager = GroupChatManager(
                groupchat=self.group_chat,
                llm_config=autogen_agents[0].llm_config if autogen_agents else None
            )
            
            logger.info(f"Created AutoGen group chat with {len(autogen_agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to create AutoGen group chat: {e}")
    
    async def start_conversation(self, initial_message: str, 
                               conversation_type: str = "general") -> Dict[str, Any]:
        """Start a group conversation."""
        self.conversation_context.conversation_type = conversation_type
        self.conversation_context.last_updated = datetime.now()
        
        if not self.group_chat or not self.chat_manager:
            # Fallback to individual agent responses
            responses = {}
            for agent in self.agents:
                response = await agent.participate_in_conversation(
                    group_chat=None, 
                    message=initial_message
                )
                responses[agent.agent_id] = response
            
            return {
                "success": True,
                "conversation_id": self.chat_id,
                "responses": responses,
                "type": "individual_responses"
            }
        
        try:
            # Use AutoGen group chat
            result = self.chat_manager.run(
                message=initial_message,
                max_turns=10
            )
            
            # Extract conversation history
            conversation_history = []
            for message in self.group_chat.messages:
                conversation_history.append({
                    "sender": message.get("name", "unknown"),
                    "content": message.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "conversation_id": self.chat_id,
                "result": result,
                "conversation_history": conversation_history,
                "type": "group_chat"
            }
            
        except Exception as e:
            logger.error(f"Error in group conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "conversation_id": self.chat_id
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if self.group_chat:
            return [
                {
                    "sender": msg.get("name", "unknown"),
                    "content": msg.get("content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                for msg in self.group_chat.messages
            ]
        else:
            # Combine individual agent histories
            all_history = []
            for agent in self.agents:
                all_history.extend(agent.conversation_history)
            return sorted(all_history, key=lambda x: x["timestamp"])


class EnhancedAutoGenIntegration:
    """Enhanced AutoGen integration with dynamic role assignment and workflow management."""
    
    def __init__(self):
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available - enhanced integration disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.agents: Dict[str, EnhancedAutoGenAgent] = {}
        self.group_chats: Dict[str, EnhancedGroupChat] = {}
        self.role_templates: Dict[str, AgentRole] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default role templates
        self._initialize_default_roles()
        
        # Initialize workflow templates
        self._initialize_workflow_templates()
    
    def _initialize_default_roles(self):
        """Initialize default agent role templates."""
        self.role_templates = {
            "coordinator": AgentRole(
                role_name="Coordinator",
                capabilities=["planning", "coordination", "delegation", "project_management"],
                system_message="You are a project coordinator specializing in PDCA methodology and Agile/Scrum processes. You orchestrate team activities, manage sprints, and ensure project success.",
                specializations=["project_management", "agile", "scrum", "coordination"],
                preferred_models=["gpt-4", "claude-sonnet-4"]
            ),
            "frontend_developer": AgentRole(
                role_name="Frontend Developer",
                capabilities=["react", "typescript", "ui_ux", "frontend_development"],
                system_message="You are a frontend development specialist with expertise in React, TypeScript, and modern UI/UX practices. You create responsive, accessible, and performant user interfaces.",
                specializations=["react", "typescript", "ui_ux", "frontend"],
                preferred_models=["gpt-4", "claude-sonnet-4"]
            ),
            "backend_developer": AgentRole(
                role_name="Backend Developer",
                capabilities=["api_development", "database_design", "security", "backend_development"],
                system_message="You are a backend development specialist with expertise in API design, database architecture, security, and scalable system design.",
                specializations=["api", "database", "security", "backend"],
                preferred_models=["gpt-4", "claude-sonnet-4"]
            ),
            "testing_specialist": AgentRole(
                role_name="Testing Specialist",
                capabilities=["test_automation", "quality_assurance", "testing_strategies"],
                system_message="You are a testing specialist with expertise in test automation, quality assurance, and comprehensive testing strategies.",
                specializations=["testing", "qa", "automation"],
                preferred_models=["gpt-4", "claude-sonnet-4"]
            ),
            "documentation_specialist": AgentRole(
                role_name="Documentation Specialist",
                capabilities=["technical_writing", "documentation", "knowledge_management"],
                system_message="You are a documentation specialist with expertise in technical writing, API documentation, and knowledge management.",
                specializations=["documentation", "writing", "knowledge"],
                preferred_models=["gpt-4", "claude-sonnet-4"]
            )
        }
    
    def _initialize_workflow_templates(self):
        """Initialize workflow templates for common scenarios."""
        self.workflow_templates = {
            "sprint_planning": {
                "name": "Sprint Planning",
                "description": "Plan and organize a development sprint",
                "required_roles": ["coordinator", "frontend_developer", "backend_developer", "testing_specialist"],
                "conversation_type": "sprint_planning",
                "max_rounds": 15
            },
            "code_review": {
                "name": "Code Review",
                "description": "Review and improve code quality",
                "required_roles": ["frontend_developer", "backend_developer", "testing_specialist"],
                "conversation_type": "code_review",
                "max_rounds": 10
            },
            "architecture_design": {
                "name": "Architecture Design",
                "description": "Design system architecture and technical decisions",
                "required_roles": ["coordinator", "frontend_developer", "backend_developer"],
                "conversation_type": "architecture_design",
                "max_rounds": 20
            },
            "bug_triage": {
                "name": "Bug Triage",
                "description": "Analyze and prioritize bug reports",
                "required_roles": ["coordinator", "frontend_developer", "backend_developer", "testing_specialist"],
                "conversation_type": "bug_triage",
                "max_rounds": 12
            }
        }
    
    async def create_agent(self, agent_id: str, role_name: str, 
                          project_id: str = None, custom_role: AgentRole = None) -> str:
        """Create an enhanced AutoGen agent with dynamic role assignment."""
        if not self.enabled:
            raise RuntimeError("Enhanced AutoGen integration not available")
        
        try:
            # Get role configuration
            if custom_role:
                role = custom_role
            elif role_name in self.role_templates:
                role = self.role_templates[role_name]
            else:
                # Create a generic role
                role = AgentRole(
                    role_name=role_name.title(),
                    capabilities=["general"],
                    system_message=f"You are a {role_name} specialist with expertise in your domain.",
                    specializations=[role_name.lower()]
                )
            
            # Create enhanced agent
            agent = EnhancedAutoGenAgent(agent_id, role, project_id)
            self.agents[agent_id] = agent
            
            logger.info(f"Created enhanced AutoGen agent: {agent_id} with role: {role.role_name}")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create enhanced AutoGen agent: {e}")
            raise
    
    async def create_group_chat(self, chat_id: str, agent_ids: List[str], 
                               project_id: str = None) -> str:
        """Create an enhanced group chat with specified agents."""
        if not self.enabled:
            raise RuntimeError("Enhanced AutoGen integration not available")
        
        try:
            # Create group chat
            group_chat = EnhancedGroupChat(chat_id, project_id)
            
            # Add agents to group chat
            for agent_id in agent_ids:
                if agent_id in self.agents:
                    group_chat.add_agent(self.agents[agent_id])
                else:
                    logger.warning(f"Agent {agent_id} not found, skipping")
            
            self.group_chats[chat_id] = group_chat
            
            logger.info(f"Created enhanced group chat: {chat_id} with {len(agent_ids)} agents")
            return chat_id
            
        except Exception as e:
            logger.error(f"Failed to create enhanced group chat: {e}")
            raise
    
    async def start_workflow(self, workflow_name: str, project_id: str = None, 
                           initial_message: str = None) -> Dict[str, Any]:
        """Start a predefined workflow with appropriate agents."""
        if workflow_name not in self.workflow_templates:
            raise ValueError(f"Unknown workflow: {workflow_name}")
        
        workflow = self.workflow_templates[workflow_name]
        
        try:
            # Create workflow-specific agents
            agent_ids = []
            for role_name in workflow["required_roles"]:
                agent_id = f"{workflow_name}_{role_name}_{uuid.uuid4().hex[:8]}"
                await self.create_agent(agent_id, role_name, project_id)
                agent_ids.append(agent_id)
            
            # Create group chat for workflow
            chat_id = f"{workflow_name}_{uuid.uuid4().hex[:8]}"
            await self.create_group_chat(chat_id, agent_ids, project_id)
            
            # Start conversation
            if not initial_message:
                initial_message = f"Let's start the {workflow['name']} workflow. Please introduce yourselves and begin the process."
            
            group_chat = self.group_chats[chat_id]
            result = await group_chat.start_conversation(
                initial_message, 
                workflow["conversation_type"]
            )
            
            return {
                "success": True,
                "workflow_name": workflow_name,
                "chat_id": chat_id,
                "agent_ids": agent_ids,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"Failed to start workflow {workflow_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "workflow_name": workflow_name
            }
    
    def get_available_roles(self) -> List[str]:
        """Get list of available role templates."""
        return list(self.role_templates.keys())
    
    def get_available_workflows(self) -> List[str]:
        """Get list of available workflow templates."""
        return list(self.workflow_templates.keys())
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent."""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "role": agent.role.role_name,
            "capabilities": agent.role.capabilities,
            "specializations": agent.role.specializations,
            "project_id": agent.project_id,
            "conversation_count": len(agent.conversation_history)
        }
    
    def get_group_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific group chat."""
        if chat_id not in self.group_chats:
            return None
        
        group_chat = self.group_chats[chat_id]
        return {
            "chat_id": chat_id,
            "project_id": group_chat.project_id,
            "participants": group_chat.conversation_context.participants,
            "conversation_type": group_chat.conversation_context.conversation_type,
            "message_count": len(group_chat.get_conversation_history())
        }


# Global instance for easy access
_enhanced_autogen = None

def get_enhanced_autogen() -> EnhancedAutoGenIntegration:
    """Get the global enhanced AutoGen integration instance."""
    global _enhanced_autogen
    if _enhanced_autogen is None:
        _enhanced_autogen = EnhancedAutoGenIntegration()
    return _enhanced_autogen
