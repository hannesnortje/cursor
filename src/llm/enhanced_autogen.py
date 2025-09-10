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
        self, agent_id: str, role: AgentRole, project_id: str = None
    ) -> Dict[str, Any]:
        """Create a fallback agent."""
        agent = {
            "agent_id": agent_id,
            "role": role,
            "project_id": project_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "capabilities": role.capabilities,
            "specializations": role.specializations,
        }
        self.agents[agent_id] = agent
        logger.info(f"Created fallback agent: {agent_id} with role: {role.role_name}")
        return agent

    def create_group_chat(
        self, chat_id: str, agents: List[str], project_id: str = None
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

    def __init__(self, agent_id: str, role: AgentRole, project_id: str = None):
        self.agent_id = agent_id
        self.role = role
        self.project_id = project_id
        self.status = "active"
        self.created_at = datetime.now()

        if AUTOGEN_AVAILABLE:
            try:
                # Create AutoGen agent
                self.autogen_agent = AssistantAgent(
                    name=agent_id,
                    system_message=role.system_message,
                    llm_config={
                        "model": (
                            role.preferred_models[0]
                            if role.preferred_models
                            else "gpt-4"
                        ),
                        "temperature": role.temperature,
                        "max_tokens": role.max_tokens,
                    },
                )
                logger.info(f"Created AutoGen agent: {agent_id}")
            except Exception as e:
                logger.error(f"Failed to create AutoGen agent: {e}")
                self.autogen_agent = None
        else:
            self.autogen_agent = None
            logger.info(f"Created fallback agent: {agent_id}")

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
        self, agent_id: str, role: AgentRole, project_id: str = None
    ) -> Dict[str, Any]:
        """Create an enhanced agent."""
        if self.fallback_mode:
            return self.fallback_system.create_agent(agent_id, role, project_id)

        try:
            agent = EnhancedAutoGenAgent(agent_id, role, project_id)
            self.agents[agent_id] = agent
            return agent.get_info()
        except Exception as e:
            logger.error(f"Failed to create agent with AutoGen: {e}")
            logger.info("Falling back to fallback system")
            self.fallback_mode = True
            return self.fallback_system.create_agent(agent_id, role, project_id)

    def create_group_chat(
        self, chat_id: str, agents: List[str], project_id: str = None
    ) -> Dict[str, Any]:
        """Create a group chat."""
        if self.fallback_mode:
            return self.fallback_system.create_group_chat(chat_id, agents, project_id)

        try:
            # Get AutoGen agents
            autogen_agents = []
            for agent_id in agents:
                if agent_id in self.agents:
                    autogen_agents.append(self.agents[agent_id].autogen_agent)

            if not autogen_agents:
                raise ValueError("No valid agents found")

            # Create group chat
            group_chat = GroupChat(agents=autogen_agents, messages=[], max_round=10)

            manager = GroupChatManager(groupchat=group_chat)

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
    return _enhanced_autogen
