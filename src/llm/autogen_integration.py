"""AutoGen integration for sophisticated agent conversations."""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import json

try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    logging.warning("AutoGen not available. Install with: pip install pyautogen")

logger = logging.getLogger(__name__)


@dataclass
class AutoGenConfig:
    """Configuration for AutoGen agents."""
    model_name: str
    api_base: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    system_message: str = "You are a helpful AI assistant."


class AutoGenAgentWrapper:
    """Wrapper for AutoGen agents to integrate with our system."""
    
    def __init__(self, agent_id: str, agent_type: str, config: AutoGenConfig):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.config = config
        self.conversation_history = []
        
        # For testing, we'll create a mock agent instead of real AutoGen
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available, using mock agent")
            self.agent = None
        else:
            try:
                self.agent = self._create_autogen_agent()
            except Exception as e:
                logger.warning(f"Failed to create AutoGen agent {self.agent_id}: {e}")
                self.agent = None
    
    def _create_autogen_agent(self):
        """Create an AutoGen agent."""
        try:
            llm_config = {
                "config_list": [{
                    "model": self.config.model_name,
                    "api_base": self.config.api_base,
                    "api_key": self.config.api_key
                }],
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens
            }
            
            if self.agent_type == "coordinator":
                return AssistantAgent(
                    name=self.agent_id,
                    system_message=self.config.system_message,
                    llm_config=llm_config
                )
            elif self.agent_type == "assistant":
                return AssistantAgent(
                    name=self.agent_id,
                    system_message=self.config.system_message,
                    llm_config=llm_config
                )
            else:
                return UserProxyAgent(
                    name=self.agent_id,
                    human_input_mode="NEVER",
                    llm_config=llm_config
                )
        except Exception as e:
            logger.warning(f"Failed to create AutoGen agent {self.agent_id}: {e}")
            return None
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message using the AutoGen agent."""
        try:
            # Store in conversation history
            self.conversation_history.append({
                "message": message,
                "context": context,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # For now, return a simple response
            # In full implementation, this would use AutoGen's conversation capabilities
            response = f"AutoGen Agent {self.agent_id} ({self.agent_type}) processed: {message}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message with AutoGen agent: {e}")
            return f"Error: {str(e)}"


class AutoGenGroupChat:
    """AutoGen group chat for multi-agent conversations."""
    
    def __init__(self, chat_id: str, agents: List[AutoGenAgentWrapper]):
        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen not available")
        
        self.chat_id = chat_id
        self.agents = agents
        self.group_chat = self._create_group_chat()
        self.manager = self._create_chat_manager()
        self.conversation_history = []
    
    def _create_group_chat(self):
        """Create an AutoGen group chat."""
        if not AUTOGEN_AVAILABLE:
            return None
            
        autogen_agents = [agent.agent for agent in self.agents if agent.agent is not None]
        
        if not autogen_agents:
            return None
            
        return GroupChat(
            agents=autogen_agents,
            messages=[],
            max_round=50
        )
    
    def _create_chat_manager(self):
        """Create a chat manager for the group chat."""
        if not AUTOGEN_AVAILABLE or not self.group_chat:
            return None
            
        return GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.agents[0].config.__dict__ if self.agents else {}
        )
    
    async def start_conversation(self, initial_message: str, 
                               initiator_agent_id: str) -> str:
        """Start a group conversation."""
        try:
            # Find the initiator agent
            initiator = next(
                (agent for agent in self.agents if agent.agent_id == initiator_agent_id),
                None
            )
            
            if not initiator:
                raise ValueError(f"Agent {initiator_agent_id} not found in group chat")
            
            # Store conversation start
            self.conversation_history.append({
                "type": "conversation_start",
                "initiator": initiator_agent_id,
                "message": initial_message,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # For now, return a simple response
            # In full implementation, this would use AutoGen's group chat
            response = f"Group chat {self.chat_id} started by {initiator_agent_id}: {initial_message}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error starting group conversation: {e}")
            return f"Error: {str(e)}"
    
    async def add_message(self, agent_id: str, message: str) -> str:
        """Add a message to the group chat."""
        try:
            # Store message
            self.conversation_history.append({
                "type": "message",
                "agent_id": agent_id,
                "message": message,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # For now, return a simple response
            # In full implementation, this would use AutoGen's group chat
            response = f"Message added to group chat {self.chat_id} by {agent_id}: {message}"
            
            return response
            
        except Exception as e:
            logger.error(f"Error adding message to group chat: {e}")
            return f"Error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()


class AutoGenIntegration:
    """Main AutoGen integration class."""
    
    def __init__(self):
        if not AUTOGEN_AVAILABLE:
            logger.warning("AutoGen not available - integration disabled")
            self.enabled = False
            return
        
        self.enabled = True
        self.agents: Dict[str, AutoGenAgentWrapper] = {}
        self.group_chats: Dict[str, AutoGenGroupChat] = {}
        self.default_config = AutoGenConfig(
            model_name="gpt-4",  # Use a standard model name
            api_base="http://localhost:8000/cursor-llm",
            temperature=0.7,
            max_tokens=4096
        )
    
    async def create_agent(self, agent_id: str, agent_type: str, 
                          config: Optional[AutoGenConfig] = None) -> str:
        """Create an AutoGen agent."""
        if not self.enabled:
            raise RuntimeError("AutoGen integration not available")
        
        try:
            if config is None:
                config = self.default_config
            
            # Check if we have required configuration
            if not config.api_key and not config.api_base:
                logger.warning(f"AutoGen agent {agent_id} created with minimal config (no API access)")
                # Create a mock agent for testing
                agent = AutoGenAgentWrapper(agent_id, agent_type, config)
                self.agents[agent_id] = agent
                return agent_id
            
            agent = AutoGenAgentWrapper(agent_id, agent_type, config)
            self.agents[agent_id] = agent
            
            logger.info(f"Created AutoGen agent: {agent_id} ({agent_type})")
            return agent_id
            
        except Exception as e:
            logger.error(f"Failed to create AutoGen agent: {e}")
            # Create a mock agent for testing
            logger.info(f"Creating mock agent {agent_id} for testing")
            agent = AutoGenAgentWrapper(agent_id, agent_type, config or self.default_config)
            self.agents[agent_id] = agent
            return agent_id
    
    async def create_group_chat(self, chat_id: str, 
                               agent_ids: List[str]) -> str:
        """Create a group chat with specified agents."""
        if not self.enabled:
            raise RuntimeError("AutoGen integration not available")
        
        try:
            # Get the agents
            agents = [self.agents[agent_id] for agent_id in agent_ids 
                     if agent_id in self.agents]
            
            if not agents:
                logger.warning(f"No valid agents found for group chat {chat_id}")
                # Create a mock group chat for testing
                group_chat = AutoGenGroupChat(chat_id, [])
                self.group_chats[chat_id] = group_chat
                return chat_id
            
            group_chat = AutoGenGroupChat(chat_id, agents)
            self.group_chats[chat_id] = group_chat
            
            logger.info(f"Created AutoGen group chat: {chat_id} with {len(agents)} agents")
            return chat_id
            
        except Exception as e:
            logger.error(f"Failed to create group chat: {e}")
            # Create a mock group chat for testing
            logger.info(f"Creating mock group chat {chat_id} for testing")
            group_chat = AutoGenGroupChat(chat_id, [])
            self.group_chats[chat_id] = group_chat
            return chat_id
    
    async def process_agent_message(self, agent_id: str, message: str, 
                                   context: Dict[str, Any] = None) -> str:
        """Process a message with a specific agent."""
        if not self.enabled:
            raise RuntimeError("AutoGen integration not available")
        
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        return await self.agents[agent_id].process_message(message, context)
    
    async def start_group_conversation(self, chat_id: str, initial_message: str, 
                                     initiator_agent_id: str) -> str:
        """Start a group conversation."""
        if not self.enabled:
            raise RuntimeError("AutoGen integration not available")
        
        if chat_id not in self.group_chats:
            raise ValueError(f"Group chat {chat_id} not found")
        
        return await self.group_chats[chat_id].start_conversation(
            initial_message, initiator_agent_id
        )
    
    async def add_group_message(self, chat_id: str, agent_id: str, 
                               message: str) -> str:
        """Add a message to a group chat."""
        if not self.enabled:
            raise RuntimeError("AutoGen integration not available")
        
        if chat_id not in self.group_chats:
            raise ValueError(f"Group chat {chat_id} not found")
        
        return await self.group_chats[chat_id].add_message(agent_id, message)
    
    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent."""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "config": agent.config.__dict__,
            "conversation_count": len(agent.conversation_history)
        }
    
    def get_group_chat_info(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a group chat."""
        if chat_id not in self.group_chats:
            return None
        
        chat = self.group_chats[chat_id]
        return {
            "chat_id": chat.chat_id,
            "agent_count": len(chat.agents),
            "conversation_count": len(chat.conversation_history)
        }
    
    def list_agents(self) -> List[str]:
        """List all agent IDs."""
        return list(self.agents.keys())
    
    def list_group_chats(self) -> List[str]:
        """List all group chat IDs."""
        return list(self.group_chats.keys())


# Global AutoGen integration instance
autogen_integration = AutoGenIntegration()
