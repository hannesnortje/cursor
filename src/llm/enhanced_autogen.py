"""Enhanced AutoGen Integration for Phase 9.2 with fallback support."""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Try to import AutoGen with fallback
try:
    from autogen import AssistantAgent, GroupChat, GroupChatManager

    AUTOGEN_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("AutoGen available for enhanced integration")
except ImportError:
    AUTOGEN_AVAILABLE = False
    AssistantAgent = None
    GroupChat = None
    GroupChatManager = None
    logger = logging.getLogger(__name__)
    logger.warning("AutoGen not available - using fallback conversation system")

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


class FallbackConversationSystem:
    """Fallback conversation system when AutoGen is not available."""

    def __init__(self):
        self.conversations: Dict[str, ConversationContext] = {}
        self.agents: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized fallback conversation system")

    def create_agent(
        self, agent_id: str, role: AgentRole, project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a fallback agent with Qdrant persistence."""
        agent = {
            "agent_id": agent_id,
            "role": role.role_name,
            "project_id": project_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "capabilities": role.capabilities,
            "specializations": role.specializations,
            "system_message": role.system_message,
            "preferred_models": role.preferred_models,
            "max_tokens": role.max_tokens,
            "temperature": role.temperature,
        }

        # Store in memory
        self.agents[agent_id] = agent

        # Persist to Qdrant for dashboard access
        try:
            logger.info(f"Attempting to persist agent {agent['agent_id']} to Qdrant...")
            self._persist_agent_to_qdrant(agent)
            logger.info(
                f"Created and persisted agent: {agent_id} with role: {role.role_name}"
            )
        except Exception as e:
            logger.error(f"Failed to persist agent {agent_id} to Qdrant: {e}")
            # Continue anyway - agent exists in memory

        return agent

    def _persist_agent_to_qdrant(self, agent: Dict[str, Any]) -> None:
        """Persist agent data to Qdrant for dashboard access."""
        try:
            # Import vector store
            from src.database.enhanced_vector_store import get_enhanced_vector_store

            vector_store = get_enhanced_vector_store()
            if not vector_store:
                logger.warning(
                    "Vector store not available - skipping agent persistence"
                )
                return

            # Create collection name for agents
            project_id = agent.get("project_id", "general")
            collection_name = f"project_{project_id}_agents"

            # Check if collection exists, create only if needed
            try:
                collection_info = vector_store.get_collection_info(collection_name)
                logger.info(f"Collection {collection_name} already exists")
            except:
                # Collection doesn't exist, create it with correct vector size (384 for simple embeddings)
                vector_store.create_collection(collection_name, vector_size=384)
                logger.info(f"Created new collection {collection_name}")

            # Create a simple embedding for the agent description
            agent_description = f"Agent {agent['agent_id']} with role {agent['role']} and capabilities: {', '.join(agent['capabilities'])}"
            embedding = vector_store._get_simple_embedding(agent_description)

            # Generate UUID for Qdrant point ID
            import uuid

            point_id = str(uuid.uuid4())

            # Prepare agent data for storage in Qdrant format
            point_data = {
                "id": point_id,
                "vector": embedding,
                "payload": {
                    "agent_id": agent["agent_id"],
                    "role": agent["role"],
                    "project_id": agent["project_id"],
                    "status": agent["status"],
                    "created_at": agent["created_at"],
                    "capabilities": agent["capabilities"],
                    "specializations": agent["specializations"],
                    "system_message": agent["system_message"],
                    "preferred_models": agent.get("preferred_models", []),
                    "max_tokens": agent.get("max_tokens", 4096),
                    "temperature": agent.get("temperature", 0.7),
                    "type": "agent_info",
                    "last_updated": datetime.now().isoformat(),
                    "content": agent_description,
                },
            }

            # Store in Qdrant
            success = vector_store.upsert_points(collection_name, [point_data])

            # Store in Qdrant
            success = vector_store.upsert_points(collection_name, [point_data])

            if success:
                logger.info(
                    f"Successfully persisted agent {agent['agent_id']} to Qdrant collection {collection_name}"
                )
            else:
                logger.warning(f"Failed to persist agent {agent['agent_id']} to Qdrant")

        except Exception as e:
            logger.error(f"Failed to persist agent to Qdrant: {e}")
            raise

    def create_group_chat(
        self, chat_id: str, agents: List[str], project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a fallback group chat."""
        chat = {
            "chat_id": chat_id,
            "agents": agents,
            "project_id": project_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "messages": [],
        }
        logger.info(f"Created fallback group chat: {chat_id} with {len(agents)} agents")
        return chat

    def start_workflow(
        self, workflow_id: str, workflow_type: str, participants: List[str]
    ) -> Dict[str, Any]:
        """Start a fallback workflow."""
        workflow = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "participants": participants,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "steps": [],
        }
        logger.info(
            f"Started fallback workflow: {workflow_id} of type: {workflow_type}"
        )
        return workflow

    def get_roles(self) -> List[Dict[str, Any]]:
        """Get available roles."""
        return [
            {
                "role_name": "coordinator",
                "capabilities": ["planning", "coordination", "delegation"],
                "description": "Coordinates tasks and manages workflow",
            },
            {
                "role_name": "developer",
                "capabilities": ["coding", "debugging", "testing"],
                "description": "Handles development tasks",
            },
            {
                "role_name": "reviewer",
                "capabilities": ["code_review", "quality_assurance"],
                "description": "Reviews code and ensures quality",
            },
            {
                "role_name": "tester",
                "capabilities": ["testing", "qa", "validation"],
                "description": "Handles testing and validation",
            },
        ]

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get available workflows."""
        return [
            {
                "workflow_id": "sprint_planning",
                "name": "Sprint Planning",
                "description": "Plan and organize sprint activities",
                "participants": ["coordinator", "developer", "tester"],
            },
            {
                "workflow_id": "code_review",
                "name": "Code Review",
                "description": "Review and improve code quality",
                "participants": ["developer", "reviewer"],
            },
            {
                "workflow_id": "testing",
                "name": "Testing Workflow",
                "description": "Execute testing procedures",
                "participants": ["tester", "developer"],
            },
        ]

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information."""
        return self.agents.get(agent_id)

    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information."""
        # In a real implementation, this would return chat info
        return {"chat_id": chat_id, "status": "active", "message_count": 0}

    def start_conversation(
        self,
        conversation_id: str,
        participants: List[str],
        conversation_type: str = "general",
    ) -> Dict[str, Any]:
        """Start a conversation."""
        context = ConversationContext(
            conversation_id=conversation_id,
            project_id=None,
            participants=participants,
            conversation_type=conversation_type,
        )
        self.conversations[conversation_id] = context

        return {
            "conversation_id": conversation_id,
            "participants": participants,
            "conversation_type": conversation_type,
            "status": "active",
            "created_at": context.created_at.isoformat(),
        }


class EnhancedAutoGenAgent:
    """Enhanced AutoGen agent with dynamic role assignment and project integration."""

    def __init__(
        self, agent_id: str, role: AgentRole, project_id: Optional[str] = None
    ):
        self.agent_id = agent_id
        self.role = role
        self.project_id = project_id
        self.status = "active"
        self.created_at = datetime.now()

        if AUTOGEN_AVAILABLE:
            try:
                # Create AutoGen agent with Cursor LLM + Ollama fallback configuration
                llm_config = self._create_llm_config(role)
                self.autogen_agent = AssistantAgent(
                    name=agent_id,
                    system_message=role.system_message,
                    llm_config=llm_config,
                )
                logger.info(f"Created AutoGen agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to create AutoGen agent: {e}")
                self.autogen_agent = None
        else:
            self.autogen_agent = None
            logger.info(f"Created fallback agent: {agent_id}")

    def _create_llm_config(self, role: AgentRole) -> Dict[str, Any]:
        """Create LLM configuration for AutoGen with Cursor LLM + Ollama fallback."""
        # Check if local Ollama is available
        ollama_available = self._check_ollama_availability()

        config_list = []

        # PRIMARY: Cursor LLMs (via OpenAI-compatible API)
        cursor_models = [
            "gpt-4o",  # Most capable
            "claude-3.5-sonnet-20240620",  # Claude Sonnet
            "gpt-4-turbo",  # GPT-4 Turbo
            "gpt-4",  # Standard GPT-4
        ]

        for model in cursor_models:
            config_list.append(
                {
                    "model": model,
                    "api_key": "cursor-api-key",  # Cursor handles authentication
                    "base_url": None,  # Use default OpenAI endpoint (Cursor will route)
                }
            )

        # FALLBACK: Local Ollama models (if available)
        if ollama_available:
            ollama_models = [
                "llama3.1:8b",  # Available model - primary local model
                # "codellama:7b",  # Code-specific model (if available)
                # "llama3.2:3b",  # Lightweight fallback (not available)
            ]
            for model in ollama_models:
                config_list.append(
                    {
                        "model": model,
                        "base_url": "http://localhost:11434/v1",
                        "api_key": "ollama-local",  # Placeholder for local Ollama
                    }
                )

        return {
            "config_list": config_list,
            "temperature": role.temperature,
            "max_tokens": role.max_tokens,
            "timeout": 60,
            "cache_seed": None,  # Disable caching for dynamic responses
        }

    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running and available."""
        try:
            import urllib.request
            import urllib.error

            # Use urllib instead of requests for minimal dependencies
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                return response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            return False

    def get_info(self) -> Dict[str, Any]:
        """Get agent information."""
        return {
            "agent_id": self.agent_id,
            "role": self.role.role_name,
            "capabilities": self.role.capabilities,
            "specializations": self.role.specializations,
            "project_id": self.project_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "autogen_available": self.autogen_agent is not None,
        }


class EnhancedAutoGen:
    """Enhanced AutoGen integration with fallback support."""

    def __init__(self):
        self.agents: Dict[str, EnhancedAutoGenAgent] = {}
        self.group_chats: Dict[str, Any] = {}
        self.workflows: Dict[str, Any] = {}
        self.fallback_system = FallbackConversationSystem()
        self.fallback_mode = not AUTOGEN_AVAILABLE

        if self.fallback_mode:
            logger.info("Using fallback conversation system")
        else:
            logger.info("Using AutoGen integration")

    def create_agent(
        self, agent_id: str, role: AgentRole, project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create an enhanced agent."""
        if self.fallback_mode:
            logger.info(f"Using fallback system to create agent {agent_id}")
            return self.fallback_system.create_agent(agent_id, role, project_id)

        try:
            agent = EnhancedAutoGenAgent(agent_id, role, project_id)
            # Check if AutoGen creation was successful
            if agent.autogen_agent is None:
                logger.info(
                    "AutoGen agent creation failed, falling back to fallback system"
                )
                self.fallback_mode = True
                return self.fallback_system.create_agent(agent_id, role, project_id)

            self.agents[agent_id] = agent
            logger.info(f"Successfully created AutoGen agent {agent_id}")
            return agent.get_info()
        except Exception as e:
            logger.error(f"Failed to create agent with AutoGen: {e}")
            logger.info("Falling back to fallback system")
            self.fallback_mode = True
            logger.info(
                f"Creating agent {agent_id} using fallback system with persistence"
            )
            return self.fallback_system.create_agent(agent_id, role, project_id)

    def create_group_chat(
        self, chat_id: str, agents: List[str], project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a group chat."""
        if self.fallback_mode:
            return self.fallback_system.create_group_chat(chat_id, agents, project_id)

        try:
            # Get AutoGen agents
            if not AUTOGEN_AVAILABLE:
                logger.warning("AutoGen not available, cannot create group chat")
                return {"error": "AutoGen not available", "status": "fallback"}

            autogen_agents = []
            for agent_id in agents:
                if agent_id in self.agents:
                    agent_wrapper = self.agents[agent_id]
                    if agent_wrapper and agent_wrapper.autogen_agent:
                        autogen_agents.append(agent_wrapper.autogen_agent)

            if not autogen_agents:
                logger.warning("No valid AutoGen agents found for group chat")
                return {"error": "No valid agents", "status": "fallback"}

            # Create group chat with proper AutoGen imports (only if AutoGen is available)
            if AUTOGEN_AVAILABLE and GroupChat and GroupChatManager:
                group_chat = GroupChat(agents=autogen_agents, messages=[], max_round=10)
                manager = GroupChatManager(groupchat=group_chat)
            else:
                logger.warning("AutoGen classes not available")
                return {"error": "AutoGen classes not available", "status": "fallback"}

            chat_info = {
                "chat_id": chat_id,
                "agents": agents,
                "project_id": project_id,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "autogen_available": True,
            }

            self.group_chats[chat_id] = {
                "group_chat": group_chat,
                "manager": manager,
                "info": chat_info,
            }

            logger.info(f"Created AutoGen group chat: {chat_id}")
            return chat_info

        except Exception as e:
            logger.error(f"Failed to create group chat with AutoGen: {e}")
            logger.info("Falling back to fallback system")
            self.fallback_mode = True
            return self.fallback_system.create_group_chat(chat_id, agents, project_id)

    def start_workflow(
        self, workflow_id: str, workflow_type: str, participants: List[str]
    ) -> Dict[str, Any]:
        """Start a workflow."""
        if self.fallback_mode:
            return self.fallback_system.start_workflow(
                workflow_id, workflow_type, participants
            )

        try:
            # Create workflow with AutoGen
            workflow = {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type,
                "participants": participants,
                "status": "active",
                "created_at": datetime.now().isoformat(),
                "autogen_available": True,
            }

            self.workflows[workflow_id] = workflow
            logger.info(f"Started AutoGen workflow: {workflow_id}")
            return workflow

        except Exception as e:
            logger.error(f"Failed to start workflow with AutoGen: {e}")
            logger.info("Falling back to fallback system")
            self.fallback_mode = True
            return self.fallback_system.start_workflow(
                workflow_id, workflow_type, participants
            )

    def get_roles(self) -> List[Dict[str, Any]]:
        """Get available roles."""
        return self.fallback_system.get_roles()

    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get available workflows."""
        return self.fallback_system.get_workflows()

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent information."""
        if agent_id in self.agents:
            return self.agents[agent_id].get_info()
        return self.fallback_system.get_agent_info(agent_id)

    def get_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get chat information."""
        if chat_id in self.group_chats:
            return self.group_chats[chat_id]["info"]
        return self.fallback_system.get_chat_info(chat_id)

    def start_conversation(
        self,
        conversation_id: str,
        participants: List[str],
        conversation_type: str = "general",
    ) -> Dict[str, Any]:
        """Start a conversation."""
        return self.fallback_system.start_conversation(
            conversation_id, participants, conversation_type
        )

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "autogen_available": AUTOGEN_AVAILABLE,
            "fallback_mode": self.fallback_mode,
            "total_agents": len(self.agents),
            "total_chats": len(self.group_chats),
            "total_workflows": len(self.workflows),
            "status": "active",
        }


# Global instance
_enhanced_autogen = None


def get_enhanced_autogen() -> EnhancedAutoGen:
    """Get the global enhanced AutoGen instance."""
    global _enhanced_autogen
    if _enhanced_autogen is None:
        _enhanced_autogen = EnhancedAutoGen()
        # Initialize default agents for MCP delegation
        _initialize_default_agents(_enhanced_autogen)
    return _enhanced_autogen


def _initialize_default_agents(enhanced_autogen: EnhancedAutoGen):
    """Initialize default agents required for MCP delegation."""
    try:
        logger.info("🚀 Initializing default AutoGen agents...")

        # Create coordinator agent role
        coordinator_role = AgentRole(
            role_name="coordinator",
            capabilities=["project_management", "task_delegation", "coordination"],
            system_message="""You are a Coordinator Agent responsible for managing projects and delegating tasks to other agents.
Your role is to:
1. Understand project requirements and break them down into actionable tasks
2. Delegate specific tasks to appropriate specialized agents
3. Coordinate between different agents to ensure project completion
4. Provide status updates and manage project timelines

When you receive a task, analyze it and delegate to the appropriate specialized agent.
Always be clear about the scope and requirements when delegating.""",
            preferred_models=["gpt-4o", "claude-3.5-sonnet", "gpt-4-turbo"],
            temperature=0.3,
        )

        # Create frontend agent role
        frontend_role = AgentRole(
            role_name="frontend_developer",
            capabilities=["react", "typescript", "frontend_development", "ui_design"],
            system_message="""You are a Frontend Development Agent specialized in React TypeScript applications.
Your expertise includes:
1. React component development with TypeScript
2. Modern frontend architecture and best practices
3. State management, routing, and UI libraries
4. Building responsive and accessible user interfaces
5. Project structure and development workflow setup

When given a task, provide complete, working solutions with:
- Proper TypeScript types and interfaces
- Modern React patterns (hooks, functional components)
- Clean, maintainable code structure
- Clear documentation and comments
- Best practices for performance and accessibility

Always create production-ready code that follows current industry standards.""",
            preferred_models=["gpt-4o", "claude-3.5-sonnet", "gpt-4-turbo"],
            temperature=0.1,
        )

        # Create the agents
        coordinator_result = enhanced_autogen.create_agent(
            "coordinator_agent", coordinator_role
        )
        frontend_result = enhanced_autogen.create_agent(
            "cursor_frontend_agent", frontend_role
        )

        # Log results
        if coordinator_result.get("status") != "error":
            logger.info("✅ Created coordinator_agent successfully")
        else:
            logger.error(f"❌ Failed to create coordinator_agent: {coordinator_result}")

        if frontend_result.get("status") != "error":
            logger.info("✅ Created cursor_frontend_agent successfully")
        else:
            logger.error(
                f"❌ Failed to create cursor_frontend_agent: {frontend_result}"
            )

        logger.info(
            f"🎯 AutoGen initialization complete. Total agents: {len(enhanced_autogen.agents)}"
        )

    except Exception as e:
        logger.error(f"❌ Failed to initialize default agents: {e}")
        import traceback

        traceback.print_exc()
