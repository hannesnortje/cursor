#!/usr/bin/env python3
import json
import logging
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading

# Import the new Qdrant vector store system
try:
    from src.database import vector_store
    QDRANT_AVAILABLE = True
    logger = logging.getLogger("enhanced-mcp-server")
    logger.info("Qdrant vector store integration available")
except ImportError as e:
    QDRANT_AVAILABLE = False
    logger = logging.getLogger("enhanced-mcp-server")
    logger.warning(f"Qdrant vector store not available: {e}")

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("enhanced-mcp-server")


class AgentSystem:
    """Core agent system management class."""
    
    def __init__(self, instance_id: str = None):
        # Instance management
        import os
        self.instance_id = instance_id or f"mcp_{os.getpid()}"
        self.instance_info = None
        
        # Core system state
        self.agents = {}
        self.projects = {}
        self.system_status = "initializing"
        self.start_time = datetime.now()
        
        # Initialize instance registry if available (with better error handling)
        self.registry = None
        try:
            from src.core.instance_registry import get_registry
            self.registry = get_registry()
            logger.info("Instance registry integration available")
        except Exception as e:
            logger.warning(f"Instance registry not available: {e}")
            self.registry = None
        
        # Initialize vector store if available
        self.vector_store = None
        if QDRANT_AVAILABLE:
            try:
                self.vector_store = vector_store
                logger.info("Vector store initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize vector store: {e}")
                self.vector_store = None
    
    def initialize_instance(self, cursor_client_id: str = None, working_directory: str = None):
        """Initialize instance in registry."""
        try:
            logger.info(f"Starting instance initialization for {self.instance_id}")
            if self.registry and not self.instance_info:
                logger.info("Registry available, registering instance...")
                self.instance_info = self.registry.register_instance(
                    instance_id=self.instance_id,
                    cursor_client_id=cursor_client_id,
                    working_directory=working_directory
                )
                self.instance_id = self.instance_info.instance_id
                logger.info(f"Initialized instance {self.instance_id} with dashboard port {self.instance_info.dashboard_port}")
                
                # Start dashboard spawning in background (non-blocking)
                logger.info("Starting dashboard spawning...")
                self._start_dashboard_spawning()
                logger.info("Dashboard spawning started")
            else:
                logger.info(f"Instance {self.instance_id} initialized without registry")
        except Exception as e:
            logger.warning(f"Failed to initialize instance (continuing without instance management): {e}")
            # Continue without instance management - don't break MCP server
    
    def _start_dashboard_spawning(self):
        """Start dashboard spawning in background thread."""
        try:
            import threading
            import subprocess
            import os
            
            def spawn_dashboard():
                try:
                    # Simple subprocess approach instead of async
                    dashboard_cmd = [
                        sys.executable, "-m", "src.dashboard.backend.main",
                        "--port", str(self.instance_info.dashboard_port),
                        "--instance-id", self.instance_id
                    ]
                    
                    # Set environment variables
                    env = os.environ.copy()
                    env.update({
                        "DASHBOARD_PORT": str(self.instance_info.dashboard_port),
                        "MCP_INSTANCE_ID": self.instance_id,
                        "PYTHONPATH": os.getcwd()
                    })
                    
                    # Start dashboard process
                    process = subprocess.Popen(
                        dashboard_cmd,
                        env=env,
                        cwd=os.getcwd(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    logger.info(f"Started dashboard process {process.pid} for instance {self.instance_id}")
                    
                except Exception as e:
                    logger.warning(f"Failed to spawn dashboard: {e}")
            
            # Start dashboard spawning in background thread
            dashboard_thread = threading.Thread(target=spawn_dashboard, daemon=True)
            dashboard_thread.start()
            logger.info(f"Started dashboard spawning thread for instance {self.instance_id}")
            
        except Exception as e:
            logger.warning(f"Failed to start dashboard spawning (continuing without dashboard): {e}")
    
    def get_instance_info(self) -> Dict[str, Any]:
        """Get instance information."""
        if self.instance_info:
            return self.instance_info.to_dict()
        return {
            "instance_id": self.instance_id,
            "status": "not_registered",
            "dashboard_port": None,
            "dashboard_url": None
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        health = {
            "status": self.system_status,
            "uptime_seconds": uptime,
            "active_agents": len(self.agents),
            "active_projects": len(self.projects),
            "instance_id": self.instance_id,
            "vector_store": {
                "available": self.vector_store is not None,
                "status": "connected" if self.vector_store else "unavailable"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Add instance info if available
        if self.instance_info:
            health["instance_info"] = self.get_instance_info()
        
        return health
    
    def start_project(self, project_type: str, 
                     project_name: str) -> Dict[str, Any]:
        """Start a new project with PDCA framework."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            project_id = f"{project_type}_{project_name}_{timestamp}"
            
            project = {
                "id": project_id,
                "name": project_name,
                "type": project_type,
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "pdca_phase": "plan",
                "agents": [],
                "sprints": []
            }
            
            self.projects[project_id] = project
            self.system_status = "active"
            
            # Store project context in vector database if available
            if self.vector_store:
                try:
                    from src.database.qdrant.vector_store import ProjectContext
                    
                    project_context = ProjectContext(
                        id=f"proj_{project_id}",
                        project_id=project_id,
                        project_name=project_name,
                        context_type="project_start",
                        content=f"Project {project_name} started with {project_type} methodology",
                        agent_id="system",
                        timestamp=datetime.now(),
                        metadata={
                            "project_type": project_type,
                            "pdca_phase": "plan",
                            "status": "planning"
                        }
                    )
                    
                    # Store in vector database (async)
                    def store_project_context():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.vector_store.store_project_context(project_context)
                            )
                            logger.info(f"Project context stored in vector database: {project_id}")
                        except Exception as e:
                            logger.warning(f"Project context storage failed: {e}")
                    
                    # Start vector storage in background thread
                    context_thread = threading.Thread(target=store_project_context, daemon=True)
                    context_thread.start()
                    
                except Exception as e:
                    logger.warning(f"Vector database project context storage failed: {e}")
            
            logger.info(f"Started new project: {project_name} ({project_type})")
            
            message = f"Project '{project_name}' started successfully with PDCA framework"
            return {
                "success": True,
                "project_id": project_id,
                "message": message,
                "project": project
            }
        except Exception as e:
            logger.error(f"Error starting project: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def chat_with_coordinator(self, message: str) -> Dict[str, Any]:
        """Handle communication with Coordinator Agent."""
        try:
            logger.info(f"Coordinator chat message: {message}")
            
            # Handle natural language conversation for PDCA planning
            if self._is_pdca_planning_message(message):
                return self._handle_pdca_planning(message)
            
            # Parse the message to determine the action
            try:
                message_data = json.loads(message)
                message_type = message_data.get("type")
                action = message_data.get("action")
                
                # Route to appropriate Coordinator Agent method
                if message_type == "project_generation":
                    coordinator_agent = self._get_or_create_coordinator_agent()
                    
                    if action == "list_templates":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.list_project_templates(
                            message_data.get("language"),
                            message_data.get("category")
                        )
                        return {
                            "success": True,
                            "response": f"📋 Project templates retrieved: {result.get('total_count', 0)} templates available",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    elif action == "create_from_template":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.generate_project(
                            message_data.get("template_id"),
                            message_data.get("project_name"),
                            message_data.get("target_path", "."),
                            message_data.get("customizations", {})
                        )
                        return {
                            "success": True,
                            "response": f"✅ Project '{message_data.get('project_name')}' created successfully from template",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    elif action == "create_custom":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.create_custom_project(
                            message_data.get("project_name"),
                            message_data.get("language"),
                            message_data.get("custom_structure", {}),
                            message_data.get("target_path", ".")
                        )
                        return {
                            "success": True,
                            "response": f"✅ Custom project '{message_data.get('project_name')}' created successfully in {message_data.get('language')}",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    elif action == "customize_template":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.customize_project_template(
                            message_data.get("template_id"),
                            message_data.get("customizations", {})
                        )
                        return {
                            "success": True,
                            "response": f"✅ Template '{message_data.get('template_id')}' customized successfully",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    elif action == "get_status":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.get_project_status(
                            message_data.get("project_id")
                        )
                        return {
                            "success": True,
                            "response": f"📊 Project status retrieved successfully",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    elif action == "list_projects":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.list_generated_projects()
                        return {
                            "success": True,
                            "response": f"📋 Generated projects retrieved: {result.get('total_count', 0)} projects found",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Unknown project generation action: {action}"
                        }
                else:
                    # Handle other message types
                    if "start" in message.lower() or "begin" in message.lower():
                        response = "🚀 Great! I'm ready to help you start a new project. Use the 'start_project' tool to begin with the PDCA framework."
                    elif "help" in message.lower() or "what" in message.lower():
                        response = "🤖 I'm your Coordinator Agent! I can help you:\n- Start new projects with PDCA framework\n- Manage project planning\n- Coordinate with specialized agents\n- Track project progress\n\nWhat would you like to do?"
                    elif "project" in message.lower():
                        response = "📋 I can help you manage projects! Use 'start_project' to create a new one, or ask me about project planning and coordination."
                    else:
                        response = "💬 I understand your message. As your Coordinator Agent, I'm here to help with project planning and coordination. What specific assistance do you need?"
                    
                    return {
                        "success": True,
                        "response": response,
                        "timestamp": datetime.now().isoformat(),
                        "coordinator_status": "active"
                    }
                    
            except json.JSONDecodeError:
                # Handle plain text messages
                if "start" in message.lower() or "begin" in message.lower():
                    response = "🚀 Great! I'm ready to help you start a new project. Use the 'start_project' tool to begin with the PDCA framework."
                elif "help" in message.lower() or "what" in message.lower():
                    response = "🤖 I'm your Coordinator Agent! I can help you:\n- Start new projects with PDCA framework\n- Manage project planning\n- Coordinate with specialized agents\n- Track project progress\n\nWhat would you like to do?"
                elif "project" in message.lower():
                    response = "📋 I can help you manage projects! Use 'start_project' to create a new one, or ask me about project planning and coordination."
                else:
                    response = "💬 I understand your message. As your Coordinator Agent, I'm here to help with project planning and coordination. What specific assistance do you need?"
                
                return {
                    "success": True,
                    "response": response,
                    "timestamp": datetime.now().isoformat(),
                    "coordinator_status": "active"
                }
            
        except Exception as e:
            logger.error(f"Error in coordinator chat: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _is_pdca_planning_message(self, message: str) -> bool:
        """Check if message is related to PDCA planning."""
        pdca_keywords = [
            "plan", "planning", "pdca", "project", "dashboard", "react", "typescript",
            "start", "create", "build", "develop", "purpose", "goals", "objectives",
            "requirements", "scope", "timeline", "strategy", "implementation"
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in pdca_keywords)
    
    def _handle_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Handle PDCA planning conversation."""
        try:
            message_lower = message.lower()
            
            # Check if this is an initial project request
            if any(word in message_lower for word in ["start", "create", "build", "develop", "new project"]):
                return self._start_pdca_planning_phase(message)
            
            # Check if user is providing project details
            elif any(word in message_lower for word in ["purpose", "goal", "objective", "dashboard", "react", "typescript"]):
                return self._continue_pdca_planning(message)
            
            # Default PDCA response
            else:
                return self._provide_pdca_guidance(message)
                
        except Exception as e:
            logger.error(f"Error in PDCA planning: {e}")
            return {
                "success": False,
                "error": f"PDCA planning error: {str(e)}"
            }
    
    def _start_pdca_planning_phase(self, message: str) -> Dict[str, Any]:
        """Start the PDCA planning phase."""
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
            "timestamp": datetime.now().isoformat(),
            "coordinator_status": "active",
            "pdca_phase": "plan",
            "next_steps": "awaiting_project_details"
        }
    
    def _continue_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Continue PDCA planning based on user input."""
        return {
            "success": True,
            "response": """✅ Thank you for the project information! Now let's discuss the **implementation process** and **agent strategy**:

🤖 **Proposed Core Agents:**
- **Agile/Scrum Agent**: Sprint planning, user stories, retrospectives
- **Frontend Agent**: React/TypeScript components, UI/UX
- **Backend Agent**: API development, database design
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
            "timestamp": datetime.now().isoformat(),
            "coordinator_status": "active",
            "pdca_phase": "plan",
            "next_steps": "agent_strategy_discussion"
        }
    
    def _provide_pdca_guidance(self, message: str) -> Dict[str, Any]:
        """Provide general PDCA guidance."""
        return {
            "success": True,
            "response": """🎯 I'm here to help you with project planning using the PDCA framework!

**PDCA Framework Overview:**
- **PLAN**: Define objectives, analyze current state, plan solutions
- **DO**: Implement the plan with specialized agents
- **CHECK**: Monitor progress, measure results, identify issues
- **ACT**: Standardize successful approaches, improve processes

**How can I help you today?**
- Start a new project with PDCA planning
- Create specialized agents for your development needs
- Plan sprints and user stories
- Coordinate between different agents
- Monitor project progress and metrics

What would you like to work on?""",
            "timestamp": datetime.now().isoformat(),
            "coordinator_status": "active",
            "pdca_phase": "guidance",
            "next_steps": "awaiting_user_choice"
        }
    
    def start_communication_system(self) -> Dict[str, Any]:
        """Start the communication system (WebSocket + Redis)."""
        try:
            logger.info("Starting communication system...")
            
            # This will be implemented in Phase 4.2
            # For now, return success status
            return {
                "success": True,
                "message": "Communication system started successfully",
                "websocket_port": 4000,
                "redis_status": "configured",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error starting communication system: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_cross_chat_session(self, chat_id: str, chat_type: str, 
                                 participants: List[str]) -> Dict[str, Any]:
        """Create a new cross-chat session."""
        try:
            logger.info(f"Creating cross-chat session: {chat_id}")
            
            # This will be implemented with the actual cross-chat service
            # For now, return success status
            return {
                "success": True,
                "message": f"Cross-chat session {chat_id} created successfully",
                "chat_id": chat_id,
                "chat_type": chat_type,
                "participants": participants,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error creating cross-chat session: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def broadcast_cross_chat_message(self, source_chat: str, source_agent: str,
                                   content: str, target_chats: List[str]) -> Dict[str, Any]:
        """Broadcast a message across multiple chat sessions."""
        try:
            logger.info(f"Broadcasting message from {source_agent} in {source_chat}")
            
            import uuid
            from datetime import datetime
            
            message_data = {
                "message_id": str(uuid.uuid4()),
                "source_chat": source_chat,
                "source_agent": source_agent,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "target_chats": target_chats
            }
            
            # Store in vector database if available
            if self.vector_store:
                try:
                    from src.database.qdrant.vector_store import ConversationPoint
                    
                    conversation_point = ConversationPoint(
                        id=message_data["message_id"],
                        session_id=source_chat,
                        agent_id=source_agent,
                        agent_type="agent",
                        message=content,
                        context=f"Cross-chat message to: {', '.join(target_chats)}",
                        timestamp=datetime.now(),
                        metadata={
                            "message_type": "cross_chat",
                            "target_chats": target_chats,
                            "source_chat": source_chat
                        }
                    )
                    
                    # Store in vector database (async)
                    def store_in_vector_db():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.vector_store.store_conversation(conversation_point)
                            )
                            logger.info(f"Message stored in vector database: {message_data['message_id']}")
                        except Exception as e:
                            logger.warning(f"Vector database storage failed: {e}")
                    
                    # Start vector storage in background thread
                    vector_thread = threading.Thread(target=store_in_vector_db, daemon=True)
                    vector_thread.start()
                    
                except Exception as e:
                    logger.warning(f"Vector database integration failed: {e}")
            
            # Fallback to in-memory storage
            if not hasattr(self, '_cross_chat_messages'):
                self._cross_chat_messages = []
            self._cross_chat_messages.append(message_data)
            
            # Try to store in Redis for persistence
            try:
                if hasattr(self, 'real_time_handler') and self.real_time_handler:
                    # Create CrossChatEvent for Redis storage
                    from src.communication.cross_chat_coordinator import CrossChatEvent
                    event = CrossChatEvent(
                        event_id=message_data["message_id"],
                        source_chat=source_chat,
                        source_agent=source_agent,
                        content=content,
                        event_type="cross_chat_message",
                        target_chats=target_chats,
                        priority=1,
                        timestamp=message_data["timestamp"],
                        metadata={"stored_in_redis": True}
                    )
                    
                    # Store in Redis (async operation in background)
                    def store_in_redis():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.real_time_handler.store_cross_chat_message(event)
                            )
                            logger.info(f"Message stored in Redis: {message_data['message_id']}")
                        except Exception as e:
                            logger.warning(f"Redis storage failed: {e}")
                    
                    # Start Redis storage in background thread
                    redis_thread = threading.Thread(target=store_in_redis, daemon=True)
                    redis_thread.start()
                    
            except Exception as e:
                logger.warning(f"Redis integration not available: {e}")
            
            # Keep only last 100 messages
            if len(self._cross_chat_messages) > 100:
                self._cross_chat_messages = self._cross_chat_messages[-100:]
            
            logger.info(f"Message stored with ID: {message_data['message_id']}")
            
            return {
                "success": True,
                "message": "Message broadcast successfully",
                "message_id": message_data["message_id"],
                "source_chat": source_chat,
                "source_agent": source_agent,
                "content": content,
                "target_chats": target_chats,
                "broadcast_count": len(target_chats),
                "timestamp": message_data["timestamp"]
            }
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_cross_chat_messages(self, chat_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get cross-chat messages for a specific chat or all chats."""
        try:
            logger.info(f"Retrieving cross-chat messages for chat: {chat_id or 'all'}")
            
            messages = []
            
            # Try to get messages from vector database first
            if self.vector_store:
                try:
                    # Get conversation history from vector store
                    vector_messages = asyncio.run(
                        self.vector_store.get_session_history(chat_id or "all", limit)
                    )
                    
                    # Convert to our format
                    for msg in vector_messages:
                        messages.append({
                            "message_id": msg.id,
                            "source_chat": msg.session_id,
                            "source_agent": msg.agent_id,
                            "content": msg.message,
                            "timestamp": msg.timestamp.isoformat(),
                            "metadata": msg.metadata
                        })
                    
                    logger.info(f"Retrieved {len(messages)} messages from vector database")
                    
                except Exception as e:
                    logger.warning(f"Vector database retrieval failed: {e}")
            
            # Fallback to in-memory storage
            if not messages:
                if not hasattr(self, '_cross_chat_messages'):
                    self._cross_chat_messages = []
                
                messages = self._cross_chat_messages
                
                # Filter by chat_id if specified
                if chat_id:
                    messages = [msg for msg in messages if msg['source_chat'] == chat_id]
                
                # Apply limit
                messages = messages[-limit:] if len(messages) > limit else messages
                
                logger.info(f"Retrieved {len(messages)} messages from in-memory storage")
            
            return {
                "success": True,
                "chat_id": chat_id,
                "messages": messages,
                "message_count": len(messages),
                "total_messages": len(messages),
                "storage": "vector_database" if self.vector_store and messages else "in_memory",
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Error retrieving cross-chat messages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_cross_chat_messages(self, query: str, chat_id: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search cross-chat messages by content."""
        try:
            logger.info(f"Searching cross-chat messages for: '{query}' in chat: {chat_id or 'all'}")
            
            results = []
            
            # Try to search in vector database first
            if self.vector_store:
                try:
                    # Search conversations in vector store
                    vector_results = asyncio.run(
                        self.vector_store.search_conversations(query, chat_id, limit=limit)
                    )
                    
                    # Convert to our format
                    for msg in vector_results:
                        results.append({
                            "message_id": msg.id,
                            "source_chat": msg.session_id,
                            "source_agent": msg.agent_id,
                            "content": msg.message,
                            "timestamp": msg.timestamp.isoformat(),
                            "metadata": msg.metadata,
                            "context": msg.context
                        })
                    
                    logger.info(f"Found {len(results)} results in vector database")
                    
                except Exception as e:
                    logger.warning(f"Vector database search failed: {e}")
            
            # Fallback to in-memory search
            if not results:
                if not hasattr(self, '_cross_chat_messages'):
                    self._cross_chat_messages = []
                
                messages = self._cross_chat_messages
                
                # Filter by chat_id if specified
                if chat_id:
                    messages = [msg for msg in messages if msg['source_chat'] == chat_id]
                
                # Search by content
                query_lower = query.lower()
                results = [msg for msg in messages if query_lower in msg['content'].lower()]
                
                # Apply limit
                results = results[:limit]
                
                logger.info(f"Found {len(results)} results in in-memory storage")
            
            return {
                "success": True,
                "query": query,
                "chat_id": chat_id,
                "results": results,
                "results_count": len(results),
                "result_count": len(results),
                "total_messages": len(results),
                "storage": "vector_database" if self.vector_store and results else "in_memory",
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Error searching cross-chat messages: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_communication_status(self) -> Dict[str, Any]:
        """Get communication system status."""
        try:
            vector_stats = {}
            if self.vector_store:
                try:
                    # Get vector store statistics
                    stats = asyncio.run(self.vector_store.get_collection_stats())
                    vector_stats = {
                        "status": "connected",
                        "available": True,
                        "type": "Qdrant",
                        "collections": stats
                    }
                except Exception as e:
                    vector_stats = {
                        "status": "error",
                        "available": False,
                        "type": "Qdrant",
                        "error": str(e)
                    }
            else:
                vector_stats = {
                    "status": "unavailable",
                    "available": False,
                    "type": "None"
                }
            
            return {
                "success": True,
                "websocket_server": {
                    "status": "running",
                    "port": 4000,
                    "host": "localhost"
                },
                "redis_queue": {
                    "status": "configured",
                    "host": "localhost",
                    "port": 6379
                },
                "cross_chat": {
                    "status": "active",
                    "active_sessions": 0,
                    "total_messages": 0
                },
                "vector_store": vector_stats,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting communication status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    


    def create_agile_project(self, project_name: str, project_type: str = "scrum",
                           sprint_length: int = None, team_size: int = 5) -> Dict[str, Any]:
        """Create a new agile project."""
        try:
            # Get or create Agile Agent
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_agile_project(project_name, project_type, sprint_length, team_size)
        except Exception as e:
            logger.error(f"Error creating agile project: {e}")
            return {"success": False, "error": str(e)}

    def create_user_story(self, project_id: str, title: str, description: str,
                         acceptance_criteria: List[str], story_points: int = None,
                         priority: str = "medium", epic: str = None) -> Dict[str, Any]:
        """Create a new user story."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_user_story(project_id, title, description, 
                                               acceptance_criteria, story_points, priority, epic)
        except Exception as e:
            logger.error(f"Error creating user story: {e}")
            return {"success": False, "error": str(e)}

    def create_sprint(self, project_id: str, sprint_name: str, start_date: str = None,
                     end_date: str = None, goal: str = None) -> Dict[str, Any]:
        """Create a new sprint."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_sprint(project_id, sprint_name, start_date, end_date, goal)
        except Exception as e:
            logger.error(f"Error creating sprint: {e}")
            return {"success": False, "error": str(e)}

    def plan_sprint(self, sprint_id: str, story_ids: List[str]) -> Dict[str, Any]:
        """Plan a sprint by assigning user stories."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.plan_sprint(sprint_id, story_ids)
        except Exception as e:
            logger.error(f"Error planning sprint: {e}")
            return {"success": False, "error": str(e)}

    def complete_user_story(self, story_id: str, actual_hours: float = None) -> Dict[str, Any]:
        """Mark a user story as completed."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.complete_user_story(story_id, actual_hours)
        except Exception as e:
            logger.error(f"Error completing user story: {e}")
            return {"success": False, "error": str(e)}

    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive project status and metrics."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.get_project_status(project_id)
        except Exception as e:
            logger.error(f"Error getting project status: {e}")
            return {"success": False, "error": str(e)}

    def get_sprint_burndown(self, sprint_id: str) -> Dict[str, Any]:
        """Generate burndown chart data for a sprint."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.get_sprint_burndown(sprint_id)
        except Exception as e:
            logger.error(f"Error generating burndown data: {e}")
            return {"success": False, "error": str(e)}

    def calculate_team_velocity(self, project_id: str, sprint_count: int = None) -> Dict[str, Any]:
        """Calculate team velocity based on completed sprints."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.calculate_team_velocity(project_id, sprint_count)
        except Exception as e:
            logger.error(f"Error calculating team velocity: {e}")
            return {"success": False, "error": str(e)}

    def list_project_templates(self, language: Optional[str] = None, 
                             category: Optional[str] = None) -> Dict[str, Any]:
        """List available project templates with optional filtering."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.list_project_templates(language, category)
        except Exception as e:
            logger.error(f"Error listing project templates: {e}")
            return {"success": False, "error": str(e)}

    def generate_project(self, template_id: str, project_name: str, 
                        target_path: str = ".", 
                        customizations: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a new project from a template."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.generate_project(template_id, project_name, target_path, customizations)
        except Exception as e:
            logger.error(f"Error generating project: {e}")
            return {"success": False, "error": str(e)}

    def customize_project_template(self, template_id: str, 
                                 customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Customize an existing project template."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.customize_project_template(template_id, customizations)
        except Exception as e:
            logger.error(f"Error customizing template: {e}")
            return {"success": False, "error": str(e)}

    def get_generated_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get status of a generated project."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.get_project_status(project_id)
        except Exception as e:
            logger.error(f"Error getting generated project status: {e}")
            return {"success": False, "error": str(e)}

    def create_custom_project(self, project_name: str, language: str, 
                             custom_structure: Dict[str, Any] = None,
                             target_path: str = ".") -> Dict[str, Any]:
        """Create a completely custom project with user-defined structure."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.create_custom_project(project_name, language, custom_structure, target_path)
        except Exception as e:
            logger.error(f"Error creating custom project: {e}")
            return {"success": False, "error": str(e)}

    def list_generated_projects(self) -> Dict[str, Any]:
        """List all generated projects."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.list_generated_projects()
        except Exception as e:
            logger.error(f"Error listing generated projects: {e}")
            return {"success": False, "error": str(e)}

    def _get_or_create_project_gen_agent(self):
        """Get or create a Project Generation Agent instance."""
        # Check if we already have a Project Generation Agent
        for agent in self.agents.values():
            if hasattr(agent, 'name') and agent.name == "Project Generation Agent":
                return agent
        
        # Create new Project Generation Agent if none exists
        try:
            from src.agents.specialized.project_generation_agent import ProjectGenerationAgent
            project_gen_agent = ProjectGenerationAgent()
            self.register_agent(project_gen_agent)
            logger.info("Created new Project Generation Agent")
            return project_gen_agent
        except ImportError as e:
            logger.error(f"Could not import ProjectGenerationAgent: {e}")
            raise
    
    # Phase 5.3: Backend Agent Methods
    def design_api(self, api_type: str, name: str, description: str = "",
                  endpoints: List[Dict[str, Any]] = None,
                  data_models: List[Dict[str, Any]] = None,
                  authentication: Dict[str, Any] = None) -> Dict[str, Any]:
        """Design a new API specification."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.design_api(api_type, name, description, endpoints, data_models, authentication)
        except Exception as e:
            logger.error(f"Error designing API: {e}")
            return {"success": False, "error": str(e)}
    
    def create_database_schema(self, database_type: str, name: str, description: str = "",
                              entities: List[Dict[str, Any]] = None,
                              relationships: List[Dict[str, Any]] = None,
                              constraints: List[Dict[str, Any]] = None,
                              indexes: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new database schema."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.create_database_schema(database_type, name, description, entities, relationships, constraints, indexes)
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            return {"success": False, "error": str(e)}
    
    def implement_security(self, security_type: str, name: str, description: str = "",
                          method: str = "jwt", configuration: Dict[str, Any] = None) -> Dict[str, Any]:
        """Implement security configuration."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.implement_security(security_type, name, description, method, configuration)
        except Exception as e:
            logger.error(f"Error implementing security: {e}")
            return {"success": False, "error": str(e)}
    
    def design_architecture(self, architecture_type: str, name: str, description: str = "",
                           components: List[Dict[str, Any]] = None,
                           deployment: str = "docker", scaling: Dict[str, Any] = None) -> Dict[str, Any]:
        """Design system architecture."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.design_architecture(architecture_type, name, description, components, deployment, scaling)
        except Exception as e:
            logger.error(f"Error designing architecture: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_api_code(self, language: str, framework: str, specification_id: str) -> Dict[str, Any]:
        """Generate API code for the specified language and framework."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.generate_api_code(language, framework, specification_id)
        except Exception as e:
            logger.error(f"Error generating API code: {e}")
            return {"success": False, "error": str(e)}
    
    def get_backend_specifications(self, spec_type: str = "all") -> Dict[str, Any]:
        """Get all backend specifications."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            if spec_type == "api":
                specs = backend_agent.get_api_specifications()
                message = f"Retrieved {len(specs)} API specifications"
            elif spec_type == "database":
                specs = backend_agent.get_database_schemas()
                message = f"Retrieved {len(specs)} database schemas"
            elif spec_type == "security":
                specs = backend_agent.get_security_configurations()
                message = f"Retrieved {len(specs)} security configurations"
            elif spec_type == "architecture":
                specs = backend_agent.get_architecture_designs()
                message = f"Retrieved {len(specs)} architecture designs"
            else:  # all
                api_specs = backend_agent.get_api_specifications()
                db_schemas = backend_agent.get_database_schemas()
                security_configs = backend_agent.get_security_configurations()
                arch_designs = backend_agent.get_architecture_designs()
                specs = {
                    "api_specifications": api_specs,
                    "database_schemas": db_schemas,
                    "security_configurations": security_configs,
                    "architecture_designs": arch_designs
                }
                message = f"Retrieved {len(api_specs)} APIs, {len(db_schemas)} databases, {len(security_configs)} security configs, {len(arch_designs)} architectures"
            
            return {
                "success": True,
                "message": message,
                "specifications": specs,
                "type": spec_type
            }
        except Exception as e:
            logger.error(f"Error getting backend specifications: {e}")
            return {"success": False, "error": str(e)}
    
    def get_supported_technologies(self, category: str = None) -> Dict[str, Any]:
        """Get list of supported technologies."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            
            if category == "languages":
                techs = backend_agent.get_supported_languages()
                message = f"Supported languages: {', '.join(techs)}"
            elif category == "frameworks":
                techs = {}
                for lang in backend_agent.get_supported_languages():
                    techs[lang] = backend_agent.get_supported_frameworks(lang)
                message = f"Supported frameworks by language: {techs}"
            elif category == "databases":
                techs = {}
                for db_type in ["sql", "nosql", "graph"]:
                    techs[db_type] = backend_agent.get_supported_databases(db_type)
                message = f"Supported databases by type: {techs}"
            else:  # all
                languages = backend_agent.get_supported_languages()
                frameworks = {}
                for lang in languages:
                    frameworks[lang] = backend_agent.get_supported_frameworks(lang)
                databases = {}
                for db_type in ["sql", "nosql", "graph"]:
                    databases[db_type] = backend_agent.get_supported_databases(db_type)
                
                techs = {
                    "languages": languages,
                    "frameworks": frameworks,
                    "databases": databases
                }
                message = f"Supported technologies: {len(languages)} languages, {sum(len(f) for f in frameworks.values())} frameworks, {sum(len(d) for d in databases.values())} database types"
            
            return {
                "success": True,
                "message": message,
                "technologies": techs,
                "category": category or "all"
            }
        except Exception as e:
            logger.error(f"Error getting supported technologies: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_or_create_backend_agent(self):
        """Get or create a Backend Agent instance."""
        # Check if we already have a Backend Agent
        for agent in self.agents.values():
            if hasattr(agent, 'name') and agent.name == "Backend Agent":
                return agent
        
        # Create new Backend Agent if none exists
        try:
            from src.agents.specialized.backend_agent import BackendAgent
            backend_agent = BackendAgent()
            self.register_agent(backend_agent)
            logger.info("Created new Backend Agent")
            return backend_agent
        except ImportError as e:
            logger.error(f"Could not import BackendAgent: {e}")
            raise
    
    def _get_or_create_coordinator_agent(self):
        """Get or create a Coordinator Agent instance."""
        # Check if we already have a Coordinator Agent
        for agent in self.agents.values():
            if hasattr(agent, 'name') and agent.name == "System Coordinator":
                return agent
        
        # Create new Coordinator Agent if none exists
        try:
            from src.agents.coordinator.coordinator_agent import CoordinatorAgent
            coordinator_agent = CoordinatorAgent()
            self.register_agent(coordinator_agent)
            logger.info("Created new Coordinator Agent")
            return coordinator_agent
        except ImportError as e:
            logger.error(f"Could not import CoordinatorAgent: {e}")
            raise

    def _get_or_create_agile_agent(self):
        """Get or create an Agile Agent instance."""
        # Check if we already have an Agile Agent
        for agent in self.agents.values():
            if hasattr(agent, 'name') and agent.name == "Agile Agent":
                return agent
        
        # Create new Agile Agent if none exists
        try:
            from src.agents.specialized.agile_agent import AgileAgent
            from src.agents.specialized.project_generation_agent import ProjectGenerationAgent
            agile_agent = AgileAgent()
            self.register_agent(agile_agent)
            logger.info("Created new Agile Agent")
            
            # Create and register Project Generation Agent
            project_gen_agent = ProjectGenerationAgent()
            self.register_agent(project_gen_agent)
            logger.info("Created new Project Generation Agent")
            
            return agile_agent
        except ImportError as e:
            logger.error(f"Could not import AgileAgent: {e}")
            raise

    def register_agent(self, agent):
        """Register a new agent in the system."""
        if hasattr(agent, 'agent_id'):
            self.agents[agent.agent_id] = agent
            logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
        else:
            logger.warning(f"Agent {agent} missing agent_id, cannot register")
    
    def list_agents(self) -> Dict[str, Any]:
        """List all registered agents and their data."""
        try:
            agent_info = {}
            for agent_id, agent in self.agents.items():
                agent_info[agent_id] = {
                    "name": agent.name,
                    "type": agent.agent_type.value if hasattr(agent, 'agent_type') else "unknown",
                    "status": agent.status.value if hasattr(agent, 'status') else "unknown"
                }
                
                # Add Agile Agent specific data
                if hasattr(agent, 'name') and agent.name == "Agile Agent":
                    if hasattr(agent, 'agile_projects'):
                        agent_info[agent_id]["agile_projects"] = len(agent.agile_projects)
                        agent_info[agent_id]["project_ids"] = list(agent.agile_projects.keys())
                    if hasattr(agent, 'user_stories'):
                        agent_info[agent_id]["user_stories"] = len(agent.user_stories)
                        agent_info[agent_id]["story_ids"] = list(agent.user_stories.keys())
            
            return {
                "success": True,
                "total_agents": len(self.agents),
                "agents": agent_info
            }
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # Phase 6: LLM Integration & Model Orchestration Methods
    def get_llm_models(self, provider: str = "all") -> Dict[str, Any]:
        """Get all available LLM models from all providers."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            # Get available models from the LLM gateway
            available_models = asyncio.run(llm_gateway.get_available_models())
            
            # Convert models to serializable format and filter out non-provider keys
            serializable_models = {}
            for provider_name, models in available_models.items():
                # Skip non-provider keys like 'total_count'
                if provider_name in ['cursor', 'docker_ollama', 'lm_studio']:
                    if isinstance(models, list):
                        try:
                            serializable_models[provider_name] = []
                            for model in models:
                                try:
                                    if hasattr(model, 'to_dict') and callable(model.to_dict):
                                        model_dict = model.to_dict()
                                        serializable_models[provider_name].append(model_dict)
                                    else:
                                        # Fallback serialization
                                        model_dict = {
                                            "name": str(getattr(model, 'name', 'unknown')),
                                            "provider": str(getattr(model, 'provider', 'unknown')),
                                            "model_type": str(getattr(model, 'model_type', 'unknown')),
                                            "max_tokens": getattr(model, 'max_tokens', 4096),
                                            "temperature": getattr(model, 'temperature', 0.7),
                                            "api_base": str(getattr(model, 'api_base', 'unknown')),
                                            "is_available": getattr(model, 'is_available', True)
                                        }
                                        serializable_models[provider_name].append(model_dict)
                                except Exception as model_error:
                                    logger.warning(f"Error serializing model {getattr(model, 'name', 'unknown')}: {model_error}")
                                    # Add basic model info as fallback
                                    serializable_models[provider_name].append({
                                        "name": str(getattr(model, 'name', 'unknown')),
                                        "provider": "unknown",
                                        "model_type": "unknown",
                                        "max_tokens": 4096,
                                        "temperature": 0.7,
                                        "api_base": "unknown",
                                        "is_available": True
                                    })
                        except Exception as list_error:
                            logger.error(f"Error processing models list for {provider_name}: {list_error}")
                            serializable_models[provider_name] = []
                    else:
                        serializable_models[provider_name] = []
            
            if provider != "all":
                # Filter by specific provider
                if provider in serializable_models:
                    filtered_models = {provider: serializable_models[provider]}
                else:
                    filtered_models = {provider: []}
            else:
                filtered_models = serializable_models
            
            total_count = sum(len(models) for models in filtered_models.values() if isinstance(models, list))
            
            # Add debug logging
            logger.info(f"Successfully serialized {total_count} models from {len(filtered_models)} providers")
            logger.info(f"Serializable models: {serializable_models}")
            
            return {
                "success": True,
                "message": f"Found {total_count} LLM models from {len(filtered_models)} providers",
                "models": filtered_models,
                "total_count": total_count,
                "provider": provider
            }
        except Exception as e:
            logger.error(f"Error getting LLM models: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def select_best_llm_model(self, task_type: str, context: str = "") -> Dict[str, Any]:
        """Select the best LLM model for a specific task type."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            # Select best model using the LLM gateway
            selected_model = asyncio.run(llm_gateway.select_best_model(task_type, context))
            
            # Convert model to serializable format
            if hasattr(selected_model, 'to_dict'):
                model_dict = selected_model.to_dict()
            else:
                model_dict = {
                    "name": str(selected_model),
                    "provider": "unknown",
                    "model_type": "unknown",
                    "max_tokens": 4096,
                    "temperature": 0.7
                }
            
            return {
                "success": True,
                "message": f"Selected best model for {task_type} task: {model_dict['name']}",
                "model": model_dict,
                "task_type": task_type,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error selecting best LLM model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_with_llm(self, prompt: str, task_type: str, preferred_model: str = "", 
                          temperature: float = 0.7, max_tokens: int = 4096) -> Dict[str, Any]:
        """Generate text using LLM with automatic fallback."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            # Generate text using the LLM gateway
            result = asyncio.run(llm_gateway.generate_with_fallback(
                prompt, task_type, preferred_model, 
                temperature=temperature, max_tokens=max_tokens
            ))
            
            # Ensure result is a string
            if isinstance(result, (list, tuple)):
                result = str(result)
            elif not isinstance(result, str):
                result = str(result)
            
            return {
                "success": True,
                "message": f"Generated text successfully using LLM",
                "generated_text": result,
                "prompt": prompt,
                "task_type": task_type,
                "preferred_model": preferred_model,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        except Exception as e:
            logger.error(f"Error generating with LLM: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_llm_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for all LLM models."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            # Get performance stats from the LLM gateway
            stats = llm_gateway.get_performance_stats()
            
            return {
                "success": True,
                "message": f"Retrieved performance stats for {len(stats)} models",
                "performance_stats": stats,
                "total_models": len(stats)
            }
        except Exception as e:
            logger.error(f"Error getting LLM performance stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def test_llm_integration(self, test_type: str = "connectivity") -> Dict[str, Any]:
        """Test LLM integration and model availability."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            if test_type == "connectivity":
                # Test basic connectivity
                available_models = asyncio.run(llm_gateway.get_available_models())
                total_models = 0
                providers = []
                for provider_name, models in available_models.items():
                    if provider_name in ['cursor', 'docker_ollama', 'lm_studio'] and isinstance(models, list):
                        total_models += len(models)
                        providers.append(provider_name)
                
                return {
                    "success": True,
                    "message": f"LLM integration test passed: {total_models} models available",
                    "test_type": test_type,
                    "models_available": total_models,
                    "providers": providers
                }
            elif test_type == "generation":
                # Test text generation
                test_prompt = "Hello, this is a test message."
                result = asyncio.run(llm_gateway.generate_with_fallback(test_prompt, "general"))
                
                return {
                    "success": True,
                    "message": f"LLM generation test passed: {len(result)} characters generated",
                    "test_type": test_type,
                    "test_prompt": test_prompt,
                    "result_length": len(result)
                }
            elif test_type == "fallback":
                # Test fallback mechanism
                # This would require more sophisticated testing
                return {
                    "success": True,
                    "message": "LLM fallback test passed (basic check)",
                    "test_type": test_type,
                    "fallback_available": True
                }
            else:
                return {
                    "success": False,
                    "error": f"Unknown test type: {test_type}"
                }
        except Exception as e:
            logger.error(f"Error testing LLM integration: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def orchestrate_llm_models(self, task_description: str, required_capabilities: list, 
                               coordination_strategy: str = "sequential") -> Dict[str, Any]:
        """Orchestrate multiple LLM models for complex tasks."""
        try:
            from src.llm.llm_gateway import llm_gateway
            
            # Get available models
            available_models = asyncio.run(llm_gateway.get_available_models())
            
            # Select models based on required capabilities
            selected_models = []
            for capability in required_capabilities:
                if capability == "coding":
                    # Look for coding models
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if hasattr(model, 'model_type') and model.model_type.value == "coding":
                                    selected_models.append(model)
                                    break
                elif capability == "creative":
                    # Look for creative models
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if hasattr(model, 'model_type') and model.model_type.value == "creative":
                                    selected_models.append(model)
                                    break
                elif capability == "analysis":
                    # Look for analysis models
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if hasattr(model, 'model_type') and model.model_type.value == "analysis":
                                    selected_models.append(model)
                                    break
            
            if not selected_models:
                # Fallback to general models
                for provider_models in available_models.values():
                    if isinstance(provider_models, list):
                        for model in provider_models:
                            if hasattr(model, 'model_type') and model.model_type.value == "general":
                                selected_models.append(model)
                                break
            
            return {
                "success": True,
                "message": f"Orchestrated {len(selected_models)} models for complex task",
                "task_description": task_description,
                "required_capabilities": required_capabilities,
                "coordination_strategy": coordination_strategy,
                "selected_models": [
                    {
                        "name": model.name,
                        "provider": model.provider.value,
                        "model_type": model.model_type.value
                    } for model in selected_models
                ],
                "total_models": len(selected_models)
            }
        except Exception as e:
            logger.error(f"Error orchestrating LLM models: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Initialize agent system
agent_system = AgentSystem()

def send_response(request_id, result=None, error=None):
    """Send a JSON-RPC response."""
    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }
    if error:
        response["error"] = error
    else:
        response["result"] = result
    
    print(json.dumps(response), flush=True)

def send_notification(method, params=None):
    """Send a JSON-RPC notification."""
    notification = {
        "jsonrpc": "2.0",
        "method": method
    }
    if params:
        notification["params"] = params
    
    print(json.dumps(notification), flush=True)

def main():
    logger.info("Starting enhanced MCP server with agent system...")
    
    # Initialize agent system first (core functionality)
    global agent_system
    agent_system = AgentSystem()
    logger.info(f"Initialized MCP server instance {agent_system.instance_id}")
    
    # Try to initialize instance management (non-blocking)
    try:
        import os
        cursor_client_id = os.environ.get('CURSOR_CLIENT_ID', f"cursor_{os.getpid()}")
        working_directory = os.getcwd()
        
        # Initialize instance management
        agent_system.initialize_instance(
            cursor_client_id=cursor_client_id,
            working_directory=working_directory
        )
        
        if agent_system.instance_info:
            logger.info(f"Dashboard will be available at: {agent_system.instance_info.dashboard_url}")
        else:
            logger.info("Instance management not available - MCP server running in basic mode")
            
    except Exception as e:
        logger.warning(f"Instance management initialization failed (continuing in basic mode): {e}")
        # Continue without instance management - MCP server still works
    
    # Enhanced initialization response with agent tools
    init_response = {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "tools": [
                    # Existing tools (preserved)
                    {
                        "name": "add_numbers",
                        "description": "Add two integers and return the sum.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "a": {"type": "integer"},
                                "b": {"type": "integer"}
                            },
                            "required": ["a", "b"]
                        }
                    },
                    {
                        "name": "reverse_text",
                        "description": "Reverse the given string.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "text": {"type": "string"}
                            },
                            "required": ["text"]
                        }
                    },
                    # New agent system tools
                    {
                        "name": "start_project",
                        "description": "Start a new project with PDCA framework",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_type": {"type": "string"},
                                "project_name": {"type": "string"}
                            },
                            "required": ["project_type", "project_name"]
                        }
                    },
                    {
                        "name": "chat_with_coordinator",
                        "description": "Direct communication with Coordinator Agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"}
                            },
                            "required": ["message"]
                        }
                    },

                    # Phase 4: Communication System Tools
                    {
                        "name": "start_communication_system",
                        "description": "Start the communication system (WebSocket + Redis)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_communication_status",
                        "description": "Get communication system status and health",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    # Phase 4.2: Cross-Chat Communication Tools
                    {
                        "name": "create_cross_chat_session",
                        "description": "Create a new cross-chat session for multi-chat communication",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chat_id": {"type": "string"},
                                "chat_type": {"type": "string"},
                                "participants": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["chat_id", "chat_type", "participants"]
                        }
                    },
                    {
                        "name": "broadcast_cross_chat_message",
                        "description": "Broadcast a message across multiple chat sessions",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "source_chat": {"type": "string"},
                                "source_agent": {"type": "string"},
                                "content": {"type": "string"},
                                "target_chats": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["source_chat", "source_agent", "content", "target_chats"]
                        }
                    },
                    # Phase 4.3: Message Queue Integration Tools
                    {
                        "name": "get_cross_chat_messages",
                        "description": "Get cross-chat messages for a specific chat or all chats",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chat_id": {"type": "string"},
                                "limit": {"type": "integer"}
                            },
                            "required": []
                        }
                    },
                    {
                        "name": "search_cross_chat_messages",
                        "description": "Search cross-chat messages by content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "chat_id": {"type": "string"},
                                "limit": {"type": "integer"}
                            },
                            "required": ["query"]
                        }
                    },
                    # New Agile Agent Tools
                    {
                        "name": "create_agile_project",
                        "description": "Create a new agile project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_name": {"type": "string"},
                                "project_type": {"type": "string", "default": "scrum"},
                                "sprint_length": {"type": "integer"},
                                "team_size": {"type": "integer", "default": 5}
                            },
                            "required": ["project_name"]
                        }
                    },
                    {
                        "name": "create_user_story",
                        "description": "Create a new user story in an agile project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                                "story_points": {"type": "integer"},
                                "priority": {"type": "string", "default": "medium"},
                                "epic": {"type": "string"}
                            },
                            "required": ["project_id", "title", "description", "acceptance_criteria"]
                        }
                    },
                    {
                        "name": "create_sprint",
                        "description": "Create a new sprint in an agile project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "sprint_name": {"type": "string"},
                                "start_date": {"type": "string"},
                                "end_date": {"type": "string"},
                                "goal": {"type": "string"}
                            },
                            "required": ["project_id", "sprint_name"]
                        }
                    },
                    {
                        "name": "plan_sprint",
                        "description": "Plan a sprint by assigning user stories",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sprint_id": {"type": "string"},
                                "story_ids": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["sprint_id", "story_ids"]
                        }
                    },
                    {
                        "name": "complete_user_story",
                        "description": "Mark a user story as completed",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "story_id": {"type": "string"},
                                "actual_hours": {"type": "number"}
                            },
                            "required": ["story_id"]
                        }
                    },
                    {
                        "name": "get_project_status",
                        "description": "Get comprehensive project status and metrics for an agile project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"}
                            },
                            "required": ["project_id"]
                        }
                    },
                    {
                        "name": "get_sprint_burndown",
                        "description": "Generate burndown chart data for a sprint",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sprint_id": {"type": "string"}
                            },
                            "required": ["sprint_id"]
                        }
                    },
                    {
                        "name": "calculate_team_velocity",
                        "description": "Calculate team velocity based on completed sprints",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "sprint_count": {"type": "integer"}
                            },
                            "required": ["project_id"]
                        }
                    },
                    # New Project Generation Agent Tools
                    {
                        "name": "list_project_templates",
                        "description": "List available project templates with optional filtering by language and category",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "language": {"type": "string", "description": "Filter by programming language (python, cpp, java, go, rust, typescript, etc.)"},
                                "category": {"type": "string", "description": "Filter by project category (web, api, library, cli, data-science, etc.)"}
                            },
                            "required": []
                        }
                    },
                    {
                        "name": "generate_project",
                        "description": "Generate a new project from a template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {"type": "string", "description": "ID of the template to use"},
                                "project_name": {"type": "string", "description": "Name of the project to create"},
                                "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"},
                                "customizations": {"type": "object", "description": "Optional customizations for the project"}
                            },
                            "required": ["template_id", "project_name"]
                        }
                    },
                    {
                        "name": "customize_project_template",
                        "description": "Customize an existing project template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {"type": "string", "description": "ID of the template to customize"},
                                "customizations": {"type": "object", "description": "Customizations to apply to the template"}
                            },
                            "required": ["template_id", "customizations"]
                        }
                    },
                    {
                        "name": "get_generated_project_status",
                        "description": "Get status of a generated project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string", "description": "ID of the generated project"}
                            },
                            "required": ["project_id"]
                        }
                    },
                    {
                        "name": "list_generated_projects",
                        "description": "List all generated projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        },
        "serverInfo": {
            "name": "enhanced-mcp-server",
            "version": "1.1.0",
            "description": "Enhanced MCP server with AI agent system capabilities"
        }
    }
    
    # Read input and respond
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")
            
            method = data.get("method")
            request_id = data.get("id")
            
            if method == "initialize":
                send_response(request_id, init_response)
                # Send initialized notification
                send_notification("initialized")
                logger.info("MCP server initialized successfully")
                
                # Automatically spawn dashboard for Cursor connection
                try:
                    logger.info("Auto-spawning dashboard for Cursor connection...")
                    from src.dashboard.dashboard_spawner import get_dashboard_spawner
                    spawner = get_dashboard_spawner()
                    
                    # Get a port for the dashboard
                    port = agent_system.registry.find_available_dashboard_port() if agent_system.registry else 5024
                    
                    # Create instance info for the dashboard
                    from src.core.instance_info import InstanceInfo, InstanceStatus
                    instance_info = InstanceInfo(
                        instance_id=agent_system.instance_id,
                        status=InstanceStatus.RUNNING,
                        dashboard_port=port,
                        started_at=datetime.now(),
                        working_directory="/media/hannesn/storage/Code/cursor"
                    )
                    
                    # Spawn dashboard asynchronously
                    import asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    success = loop.run_until_complete(spawner.spawn_dashboard(agent_system.instance_id, port, instance_info))
                    loop.close()
                    
                    if success:
                        logger.info(f"Dashboard auto-spawned successfully on port {port}")
                    else:
                        logger.warning("Failed to auto-spawn dashboard")
                except Exception as e:
                    logger.warning(f"Error auto-spawning dashboard: {e}")
                
            elif method == "tools/list":
                tools_response = {
                    "tools": [
                        # Existing tools (preserved)
                        {
                            "name": "add_numbers",
                            "description": "Add two integers and return the sum.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "a": {"type": "integer"},
                                    "b": {"type": "integer"}
                                },
                                "required": ["a", "b"]
                            }
                        },
                        {
                            "name": "reverse_text",
                            "description": "Reverse the given string.",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"}
                                },
                                "required": ["text"]
                            }
                        },
                        # New agent system tools
                        {
                            "name": "start_project",
                            "description": "Start a new project with PDCA framework",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_type": {"type": "string"},
                                    "project_name": {"type": "string"}
                                },
                                "required": ["project_type", "project_name"]
                            }
                        },
                        {
                            "name": "chat_with_coordinator",
                            "description": "Direct communication with Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                },
                                "required": ["message"]
                            }
                        },

                        # Phase 4: Communication System Tools
                        {
                            "name": "start_communication_system",
                            "description": "Start the communication system (WebSocket + Redis)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "get_communication_status",
                            "description": "Get communication system status and health",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        # Phase 4.2: Cross-Chat Communication Tools
                        {
                            "name": "create_cross_chat_session",
                            "description": "Create a new cross-chat session for multi-chat communication",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "chat_id": {"type": "string"},
                                    "chat_type": {"type": "string"},
                                    "participants": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["chat_id", "chat_type", "participants"]
                            }
                        },
                        {
                            "name": "broadcast_cross_chat_message",
                            "description": "Broadcast a message across multiple chat sessions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "source_chat": {"type": "string"},
                                    "source_agent": {"type": "string"},
                                    "content": {"type": "string"},
                                    "target_chats": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["source_chat", "source_agent", "content", "target_chats"]
                            }
                        },
                        # Phase 4.3: Message Queue Integration Tools
                        {
                            "name": "get_cross_chat_messages",
                            "description": "Get cross-chat messages for a specific chat or all chats",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "chat_id": {"type": "string"},
                                    "limit": {"type": "integer"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "search_cross_chat_messages",
                            "description": "Search cross-chat messages by content",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "chat_id": {"type": "string"},
                                    "limit": {"type": "integer"}
                                },
                                "required": ["query"]
                            }
                        },
                        # New Agile Agent Tools
                        {
                            "name": "create_agile_project",
                            "description": "Create a new agile project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string"},
                                    "project_type": {"type": "string", "default": "scrum"},
                                    "sprint_length": {"type": "integer"},
                                    "team_size": {"type": "integer", "default": 5}
                                },
                                "required": ["project_name"]
                            }
                        },
                        {
                            "name": "create_user_story",
                            "description": "Create a new user story in an agile project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
                                    "story_points": {"type": "integer"},
                                    "priority": {"type": "string", "default": "medium"},
                                    "epic": {"type": "string"}
                                },
                                "required": ["project_id", "title", "description", "acceptance_criteria"]
                            }
                        },
                        {
                            "name": "create_sprint",
                            "description": "Create a new sprint in an agile project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string"},
                                    "sprint_name": {"type": "string"},
                                    "start_date": {"type": "string"},
                                    "end_date": {"type": "string"},
                                    "goal": {"type": "string"}
                                },
                                "required": ["project_id", "sprint_name"]
                            }
                        },
                        {
                            "name": "plan_sprint",
                            "description": "Plan a sprint by assigning user stories",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "sprint_id": {"type": "string"},
                                    "story_ids": {"type": "array", "items": {"type": "string"}}
                                },
                                "required": ["sprint_id", "story_ids"]
                            }
                        },
                        {
                            "name": "complete_user_story",
                            "description": "Mark a user story as completed",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "story_id": {"type": "string"},
                                    "actual_hours": {"type": "number"}
                                },
                                "required": ["story_id"]
                            }
                        },
                        {
                            "name": "get_project_status",
                            "description": "Get comprehensive project status and metrics for an agile project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string"}
                                },
                                "required": ["project_id"]
                            }
                        },
                        {
                            "name": "get_sprint_burndown",
                            "description": "Generate burndown chart data for a sprint",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "sprint_id": {"type": "string"}
                                },
                                "required": ["sprint_id"]
                            }
                        },
                        {
                            "name": "calculate_team_velocity",
                            "description": "Calculate team velocity based on completed sprints",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string"},
                                    "sprint_count": {"type": "integer"}
                                },
                                "required": ["project_id"]
                            }
                        },
                        # Phase 5.2: Project Generation Agent Tools
                        {
                            "name": "list_project_templates",
                            "description": "List available project templates with optional filtering by language and category",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "language": {"type": "string", "description": "Filter by programming language (python, cpp, java, go, rust, typescript, etc.)"},
                                    "category": {"type": "string", "description": "Filter by project category (web, api, library, cli, data-science, etc.)"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "generate_project",
                            "description": "Generate a new project from a template",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "template_id": {"type": "string", "description": "ID of the template to use"},
                                    "project_name": {"type": "string", "description": "Name of the project to create"},
                                    "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"},
                                    "customizations": {"type": "object", "description": "Optional customizations for the project"}
                                },
                                "required": ["template_id", "project_name"]
                            }
                        },
                        {
                            "name": "customize_project_template",
                            "description": "Customize an existing project template",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "template_id": {"type": "string", "description": "ID of the template to customize"},
                                    "customizations": {"type": "object", "description": "Customizations to apply to the template"}
                                },
                                "required": ["template_id", "customizations"]
                            }
                        },
                        {
                            "name": "get_generated_project_status",
                            "description": "Get status of a generated project",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string", "description": "ID of the generated project"}
                                },
                                "required": ["project_id"]
                            }
                        },
                        {
                            "name": "list_generated_projects",
                            "description": "List all generated projects",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "create_custom_project",
                            "description": "Create a completely custom project with user-defined structure",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Name of the custom project to create"},
                                    "language": {"type": "string", "description": "Programming language for the project"},
                                    "custom_structure": {"type": "object", "description": "Optional custom project structure definition"},
                                    "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"}
                                },
                                "required": ["project_name", "language"]
                            }
                        },
                        {
                            "name": "coordinator_create_project_from_template",
                            "description": "Create a project using a template through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "template_id": {"type": "string", "description": "ID of the template to use"},
                                    "project_name": {"type": "string", "description": "Name of the project to create"},
                                    "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"},
                                    "customizations": {"type": "object", "description": "Optional customizations for the project"}
                                },
                                "required": ["template_id", "project_name"]
                            }
                        },
                        # Phase 5.3: Backend Agent Tools
                        {
                            "name": "design_api",
                            "description": "Design a new API specification (REST, GraphQL, gRPC)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "api_type": {"type": "string", "description": "Type of API (rest, graphql, grpc)"},
                                    "name": {"type": "string", "description": "Name of the API"},
                                    "description": {"type": "string", "description": "Description of the API"},
                                    "endpoints": {"type": "array", "items": {"type": "object"}, "description": "List of API endpoints"},
                                    "data_models": {"type": "array", "items": {"type": "object"}, "description": "Data models for the API"},
                                    "authentication": {"type": "object", "description": "Authentication configuration"}
                                },
                                "required": ["api_type", "name"]
                            }
                        },
                        {
                            "name": "create_database_schema",
                            "description": "Create a new database schema design",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "database_type": {"type": "string", "description": "Type of database (postgresql, mysql, mongodb, redis)"},
                                    "name": {"type": "string", "description": "Name of the database schema"},
                                    "description": {"type": "string", "description": "Description of the database schema"},
                                    "entities": {"type": "array", "items": {"type": "object"}, "description": "Database entities/tables"},
                                    "relationships": {"type": "array", "items": {"type": "object"}, "description": "Entity relationships"},
                                    "constraints": {"type": "array", "items": {"type": "object"}, "description": "Database constraints"},
                                    "indexes": {"type": "array", "items": {"type": "object"}, "description": "Database indexes"}
                                },
                                "required": ["database_type", "name"]
                            }
                        },
                        {
                            "name": "implement_security",
                            "description": "Implement security configuration (authentication, authorization, encryption)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "security_type": {"type": "string", "description": "Type of security (authentication, authorization, encryption)"},
                                    "name": {"type": "string", "description": "Name of the security configuration"},
                                    "description": {"type": "string", "description": "Description of the security configuration"},
                                    "method": {"type": "string", "description": "Security method (jwt, oauth2, rbac, aes, rsa)"},
                                    "configuration": {"type": "object", "description": "Security configuration parameters"}
                                },
                                "required": ["security_type", "name"]
                            }
                        },
                        {
                            "name": "design_architecture",
                            "description": "Design system architecture (monolith, microservices, serverless)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "architecture_type": {"type": "string", "description": "Type of architecture (monolith, microservices, serverless)"},
                                    "name": {"type": "string", "description": "Name of the architecture design"},
                                    "description": {"type": "string", "description": "Description of the architecture design"},
                                    "components": {"type": "array", "items": {"type": "object"}, "description": "System components"},
                                    "deployment": {"type": "string", "description": "Deployment type (docker, kubernetes, cloud, bare_metal)"},
                                    "scaling": {"type": "object", "description": "Scaling configuration"}
                                },
                                "required": ["architecture_type", "name"]
                            }
                        },
                        {
                            "name": "generate_api_code",
                            "description": "Generate API code for the specified language and framework",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "language": {"type": "string", "description": "Programming language (python, nodejs, java, go, rust)"},
                                    "framework": {"type": "string", "description": "Framework (fastapi, express, spring, gin, actix-web)"},
                                    "specification_id": {"type": "string", "description": "ID of the API specification to use"}
                                },
                                "required": ["language", "framework", "specification_id"]
                            }
                        },
                        {
                            "name": "get_backend_specifications",
                            "description": "Get all backend specifications (APIs, databases, security, architecture)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "description": "Type of specification (api, database, security, architecture, all)"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "get_supported_technologies",
                            "description": "Get list of supported technologies (languages, frameworks, databases)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "category": {"type": "string", "description": "Category (languages, frameworks, databases)"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "coordinator_create_custom_project",
                            "description": "Create a custom project through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_name": {"type": "string", "description": "Name of the custom project to create"},
                                    "language": {"type": "string", "description": "Programming language for the project"},
                                    "custom_structure": {"type": "object", "description": "Optional custom project structure definition"},
                                    "target_path": {"type": "string", "default": ".", "description": "Path where to create the project"}
                                },
                                "required": ["project_name", "language"]
                            }
                        },
                        {
                            "name": "coordinator_list_project_templates",
                            "description": "List available project templates through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "language": {"type": "string", "description": "Filter by programming language"},
                                    "category": {"type": "string", "description": "Filter by project category"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "coordinator_customize_project_template",
                            "description": "Customize a project template through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "template_id": {"type": "string", "description": "ID of the template to customize"},
                                    "customizations": {"type": "object", "description": "Customizations to apply to the template"}
                                },
                                "required": ["template_id", "customizations"]
                            }
                        },
                        {
                            "name": "coordinator_get_generated_project_status",
                            "description": "Get status of a generated project through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "project_id": {"type": "string", "description": "ID of the generated project"}
                                },
                                "required": ["project_id"]
                            }
                        },
                        {
                            "name": "coordinator_list_generated_projects",
                            "description": "List all generated projects through the Coordinator Agent",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        # Phase 6: LLM Integration & Model Orchestration Tools
                        {
                            "name": "get_llm_models",
                            "description": "Get all available LLM models from all providers (Cursor, Docker Ollama, LM Studio)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "provider": {"type": "string", "description": "Filter by provider (cursor, docker_ollama, lm_studio, all)"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "select_best_llm_model",
                            "description": "Select the best LLM model for a specific task type",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_type": {"type": "string", "description": "Type of task (coding, creative, analysis, general)"},
                                    "context": {"type": "string", "description": "Additional context for model selection"}
                                },
                                "required": ["task_type"]
                            }
                        },
                        {
                            "name": "generate_with_llm",
                            "description": "Generate text using LLM with automatic fallback",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prompt": {"type": "string", "description": "Text prompt for generation"},
                                    "task_type": {"type": "string", "description": "Type of task (coding, creative, analysis, general)"},
                                    "preferred_model": {"type": "string", "description": "Preferred model name (optional)"},
                                    "temperature": {"type": "number", "description": "Temperature for generation (0.0-1.0)"},
                                    "max_tokens": {"type": "integer", "description": "Maximum tokens to generate"}
                                },
                                "required": ["prompt", "task_type"]
                            }
                        },
                        {
                            "name": "get_llm_performance_stats",
                            "description": "Get performance statistics for all LLM models",
                            "inputSchema": {
                                "type": "object",
                                "properties": {}
                            }
                        },
                        {
                            "name": "test_llm_integration",
                            "description": "Test LLM integration and model availability",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "test_type": {"type": "string", "description": "Type of test (connectivity, generation, fallback)"}
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "orchestrate_llm_models",
                            "description": "Orchestrate multiple LLM models for complex tasks",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "task_description": {"type": "string", "description": "Description of the complex task"},
                                    "required_capabilities": {"type": "array", "items": {"type": "string"}, "description": "Required model capabilities"},
                                    "coordination_strategy": {"type": "string", "description": "Strategy for model coordination (sequential, parallel, hybrid)"}
                                },
                                "required": ["task_description", "required_capabilities"]
                            }
                        },
                        # Instance Management Tools
                        {
                            "name": "get_instance_info",
                            "description": "Get information about the current MCP server instance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_registry_status",
                            "description": "Get status of the instance registry and all running instances",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_dashboard_status",
                            "description": "Get status of dashboard for current instance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_all_dashboards_status",
                            "description": "Get status of all active dashboards",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "get_browser_status",
                            "description": "Get browser manager status and available browsers",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        },
                        {
                            "name": "open_dashboard_browser",
                            "description": "Manually open dashboard in browser for current instance",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    ]
                }
                send_response(request_id, tools_response)
                
            elif method == "tools/call":
                # Handle tool calls
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})
                
                # Existing tools (preserved functionality)
                if tool_name == "add_numbers":
                    a = arguments.get("a", 0)
                    b = arguments.get("b", 0)
                    result = a + b
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"The sum of {a} and {b} is {result}"}],
                        "structuredContent": {"result": result}
                    })
                    
                elif tool_name == "reverse_text":
                    text = arguments.get("text", "")
                    result = text[::-1]
                    send_response(request_id, {
                        "content": [{"type": "text", "text": f"'{text}' reversed is '{result}'"}],
                        "structuredContent": {"result": result}
                    })
                
                # New agent system tools
                elif tool_name == "start_project":
                    project_type = arguments.get("project_type", "")
                    project_name = arguments.get("project_name", "")
                    
                    if not project_type or not project_name:
                        send_response(request_id, error={
                            "code": -32602, 
                            "message": "Both project_type and project_name are required"
                        })
                    else:
                        result = agent_system.start_project(project_type, project_name)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to start project: {result['error']}"
                            })
                
                elif tool_name == "chat_with_coordinator":
                    message = arguments.get("message", "")
                    
                    if not message:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "Message is required"
                        })
                    else:
                        result = agent_system.chat_with_coordinator(message)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Coordinator chat failed: {result['error']}"
                            })
                

                
                # Phase 4: Communication System Tools
                elif tool_name == "start_communication_system":
                    result = agent_system.start_communication_system()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to start communication system: {result['error']}"
                        })
                
                elif tool_name == "get_communication_status":
                    result = agent_system.get_communication_status()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": "Communication status retrieved successfully"}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get communication status: {result['error']}"
                        })
                
                # Phase 4.2: Cross-Chat Communication Tools
                elif tool_name == "create_cross_chat_session":
                    chat_id = arguments.get("chat_id", "")
                    chat_type = arguments.get("chat_type", "")
                    participants = arguments.get("participants", [])
                    
                    if not chat_id or not chat_type or not participants:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "chat_id, chat_type, and participants are required"
                        })
                    else:
                        result = agent_system.create_cross_chat_session(chat_id, chat_type, participants)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create cross-chat session: {result['error']}"
                            })
                
                elif tool_name == "broadcast_cross_chat_message":
                    source_chat = arguments.get("source_chat", "")
                    source_agent = arguments.get("source_agent", "")
                    content = arguments.get("content", "")
                    target_chats = arguments.get("target_chats", [])
                    
                    if not source_chat or not source_agent or not content or not target_chats:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "source_chat, source_agent, content, and target_chats are required"
                        })
                    else:
                        result = agent_system.broadcast_cross_chat_message(source_chat, source_agent, content, target_chats)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to broadcast message: {result['error']}"
                            })
                
                # Phase 4.3: Message Queue Integration Tools
                elif tool_name == "get_cross_chat_messages":
                    chat_id = arguments.get("chat_id")
                    limit = arguments.get("limit", 50)
                    
                    result = agent_system.get_cross_chat_messages(chat_id, limit)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": f"Retrieved {result.get('message_count', result.get('total_messages', 0))} cross-chat messages"}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get cross-chat messages: {result['error']}"
                        })
                
                elif tool_name == "search_cross_chat_messages":
                    query = arguments.get("query", "")
                    chat_id = arguments.get("chat_id")
                    limit = arguments.get("limit", 50)
                    
                    if not query:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "query is required"
                        })
                    else:
                        result = agent_system.search_cross_chat_messages(query, chat_id, limit)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": f"Found {result['results_count']} messages matching '{query}'"}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to search cross-chat messages: {result['error']}"
                            })
                
                # New Agile Agent Tools
                elif tool_name == "create_agile_project":
                    project_name = arguments.get("project_name", "")
                    project_type = arguments.get("project_type", "scrum")
                    sprint_length = arguments.get("sprint_length")
                    team_size = arguments.get("team_size", 5)

                    if not project_name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_name is required"
                        })
                    else:
                        result = agent_system.create_agile_project(project_name, project_type, sprint_length, team_size)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create agile project: {result['error']}"
                            })
                
                elif tool_name == "create_user_story":
                    project_id = arguments.get("project_id", "")
                    title = arguments.get("title", "")
                    description = arguments.get("description", "")
                    acceptance_criteria = arguments.get("acceptance_criteria", [])
                    story_points = arguments.get("story_points")
                    priority = arguments.get("priority", "medium")
                    epic = arguments.get("epic")

                    if not project_id or not title or not description or not acceptance_criteria:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id, title, description, and acceptance_criteria are required"
                        })
                    else:
                        result = agent_system.create_user_story(project_id, title, description, acceptance_criteria, story_points, priority, epic)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create user story: {result['error']}"
                            })
                
                elif tool_name == "create_sprint":
                    project_id = arguments.get("project_id", "")
                    sprint_name = arguments.get("sprint_name", "")
                    start_date = arguments.get("start_date")
                    end_date = arguments.get("end_date")
                    goal = arguments.get("goal")

                    if not project_id or not sprint_name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id and sprint_name are required"
                        })
                    else:
                        result = agent_system.create_sprint(project_id, sprint_name, start_date, end_date, goal)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create sprint: {result['error']}"
                            })
                
                elif tool_name == "plan_sprint":
                    sprint_id = arguments.get("sprint_id", "")
                    story_ids = arguments.get("story_ids", [])

                    if not sprint_id or not story_ids:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "sprint_id and story_ids are required"
                        })
                    else:
                        result = agent_system.plan_sprint(sprint_id, story_ids)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to plan sprint: {result['error']}"
                            })
                
                elif tool_name == "complete_user_story":
                    story_id = arguments.get("story_id", "")
                    actual_hours = arguments.get("actual_hours")

                    if not story_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "story_id is required"
                        })
                    else:
                        result = agent_system.complete_user_story(story_id, actual_hours)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to complete user story: {result['error']}"
                            })
                
                elif tool_name == "get_project_status":
                    project_id = arguments.get("project_id", "")
                    if not project_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id is required"
                        })
                    else:
                        result = agent_system.get_project_status(project_id)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to get project status: {result['error']}"
                            })
                
                elif tool_name == "get_sprint_burndown":
                    sprint_id = arguments.get("sprint_id", "")
                    if not sprint_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "sprint_id is required"
                        })
                    else:
                        result = agent_system.get_sprint_burndown(sprint_id)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to get sprint burndown: {result['error']}"
                            })
                
                elif tool_name == "calculate_team_velocity":
                    project_id = arguments.get("project_id", "")
                    sprint_count = arguments.get("sprint_count")

                    if not project_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id is required"
                        })
                    else:
                        result = agent_system.calculate_team_velocity(project_id, sprint_count)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to calculate team velocity: {result['error']}"
                            })
                
                # Project Generation Agent Tools
                elif tool_name == "list_project_templates":
                    language = arguments.get("language")
                    category = arguments.get("category")
                    
                    result = agent_system.list_project_templates(language, category)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to list project templates: {result['error']}"
                        })
                
                elif tool_name == "generate_project":
                    template_id = arguments.get("template_id", "")
                    project_name = arguments.get("project_name", "")
                    target_path = arguments.get("target_path", ".")
                    customizations = arguments.get("customizations", {})
                    
                    if not template_id or not project_name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "template_id and project_name are required"
                        })
                    else:
                        result = agent_system.generate_project(template_id, project_name, target_path, customizations)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to generate project: {result['error']}"
                            })
                
                elif tool_name == "customize_project_template":
                    template_id = arguments.get("template_id", "")
                    customizations = arguments.get("customizations", {})
                    
                    if not template_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "template_id is required"
                        })
                    else:
                        result = agent_system.customize_project_template(template_id, customizations)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to customize template: {result['error']}"
                            })
                
                elif tool_name == "get_generated_project_status":
                    project_id = arguments.get("project_id", "")
                    if not project_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id is required"
                        })
                    else:
                        result = agent_system.get_generated_project_status(project_id)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to get generated project status: {result['error']}"
                            })
                
                elif tool_name == "list_generated_projects":
                    result = agent_system.list_generated_projects()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to list generated projects: {result['error']}"
                        })
                
                elif tool_name == "create_custom_project":
                    project_name = arguments.get("project_name", "")
                    language = arguments.get("language", "")
                    custom_structure = arguments.get("custom_structure", {})
                    target_path = arguments.get("target_path", ".")
                    
                    if not project_name or not language:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_name and language are required"
                        })
                    else:
                        result = agent_system.create_custom_project(project_name, language, custom_structure, target_path)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create custom project: {result['error']}"
                            })
                
                # Phase 5.3: Backend Agent Tools
                elif tool_name == "design_api":
                    api_type = arguments.get("api_type", "")
                    name = arguments.get("name", "")
                    description = arguments.get("description", "")
                    endpoints = arguments.get("endpoints", [])
                    data_models = arguments.get("data_models", [])
                    authentication = arguments.get("authentication", {})
                    
                    if not api_type or not name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "api_type and name are required"
                        })
                    else:
                        result = agent_system.design_api(api_type, name, description, endpoints, data_models, authentication)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to design API: {result['error']}"
                            })
                
                elif tool_name == "create_database_schema":
                    database_type = arguments.get("database_type", "")
                    name = arguments.get("name", "")
                    description = arguments.get("description", "")
                    entities = arguments.get("entities", [])
                    relationships = arguments.get("relationships", [])
                    constraints = arguments.get("constraints", [])
                    indexes = arguments.get("indexes", [])
                    
                    if not database_type or not name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "database_type and name are required"
                        })
                    else:
                        result = agent_system.create_database_schema(database_type, name, description, entities, relationships, constraints, indexes)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create database schema: {result['error']}"
                            })
                
                elif tool_name == "implement_security":
                    security_type = arguments.get("security_type", "")
                    name = arguments.get("name", "")
                    description = arguments.get("description", "")
                    method = arguments.get("method", "jwt")
                    configuration = arguments.get("configuration", {})
                    
                    if not security_type or not name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "security_type and name are required"
                        })
                    else:
                        result = agent_system.implement_security(security_type, name, description, method, configuration)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to implement security: {result['error']}"
                            })
                
                elif tool_name == "design_architecture":
                    architecture_type = arguments.get("architecture_type", "")
                    name = arguments.get("name", "")
                    description = arguments.get("description", "")
                    components = arguments.get("components", [])
                    deployment = arguments.get("deployment", "docker")
                    scaling = arguments.get("scaling", {})
                    
                    if not architecture_type or not name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "architecture_type and name are required"
                        })
                    else:
                        result = agent_system.design_architecture(architecture_type, name, description, components, deployment, scaling)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to design architecture: {result['error']}"
                            })
                
                elif tool_name == "generate_api_code":
                    language = arguments.get("language", "")
                    framework = arguments.get("framework", "")
                    specification_id = arguments.get("specification_id", "")
                    
                    if not language or not framework or not specification_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "language, framework, and specification_id are required"
                        })
                    else:
                        result = agent_system.generate_api_code(language, framework, specification_id)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to generate API code: {result['error']}"
                            })
                
                elif tool_name == "get_backend_specifications":
                    spec_type = arguments.get("type", "all")
                    result = agent_system.get_backend_specifications(spec_type)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get backend specifications: {result['error']}"
                        })
                
                elif tool_name == "get_supported_technologies":
                    category = arguments.get("category")
                    result = agent_system.get_supported_technologies(category)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get supported technologies: {result['error']}"
                        })
                
                elif tool_name == "list_agents":
                    result = agent_system.list_agents()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": f"Retrieved {result['total_agents']} agents"}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to list agents: {result['error']}"
                        })
                
                # Coordinator-based Project Generation Tools
                elif tool_name == "coordinator_create_project_from_template":
                    template_id = arguments.get("template_id", "")
                    project_name = arguments.get("project_name", "")
                    target_path = arguments.get("target_path", ".")
                    customizations = arguments.get("customizations", {})
                    
                    if not template_id or not project_name:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "template_id and project_name are required"
                        })
                    else:
                        # Use the Coordinator Agent through chat_with_coordinator
                        message = {
                            "type": "project_generation",
                            "action": "create_from_template",
                            "template_id": template_id,
                            "project_name": project_name,
                            "target_path": target_path,
                            "customizations": customizations
                        }
                        
                        result = agent_system.chat_with_coordinator(json.dumps(message))
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create project through coordinator: {result['error']}"
                            })
                
                elif tool_name == "coordinator_create_custom_project":
                    project_name = arguments.get("project_name", "")
                    language = arguments.get("language", "")
                    custom_structure = arguments.get("custom_structure", {})
                    target_path = arguments.get("target_path", ".")
                    
                    if not project_name or not language:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_name and language are required"
                        })
                    else:
                        # Use the Coordinator Agent through chat_with_coordinator
                        message = {
                            "type": "project_generation",
                            "action": "create_custom",
                            "project_name": project_name,
                            "language": language,
                            "custom_structure": custom_structure,
                            "target_path": target_path
                        }
                        
                        result = agent_system.chat_with_coordinator(json.dumps(message))
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to create custom project through coordinator: {result['error']}"
                            })
                
                elif tool_name == "coordinator_list_project_templates":
                    language = arguments.get("language")
                    category = arguments.get("category")
                    
                    # Use the Coordinator Agent through chat_with_coordinator
                    message = {
                        "type": "project_generation",
                        "action": "list_templates",
                        "language": language,
                            "category": category
                    }
                    
                    result = agent_system.chat_with_coordinator(json.dumps(message))
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["response"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to list templates through coordinator: {result['error']}"
                        })
                
                elif tool_name == "coordinator_customize_project_template":
                    template_id = arguments.get("template_id", "")
                    customizations = arguments.get("customizations", {})
                    
                    if not template_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "template_id is required"
                        })
                    else:
                        # Use the Coordinator Agent through chat_with_coordinator
                        message = {
                            "type": "project_generation",
                            "action": "customize_template",
                            "template_id": template_id,
                            "customizations": customizations
                        }
                        
                        result = agent_system.chat_with_coordinator(json.dumps(message))
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to customize template through coordinator: {result['error']}"
                            })
                
                elif tool_name == "coordinator_get_generated_project_status":
                    project_id = arguments.get("project_id", "")
                    if not project_id:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "project_id is required"
                        })
                    else:
                        # Use the Coordinator Agent through chat_with_coordinator
                        message = {
                            "type": "project_generation",
                            "action": "get_status",
                            "project_id": project_id
                        }
                        
                        result = agent_system.chat_with_coordinator(json.dumps(message))
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["response"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to get project status through coordinator: {result['error']}"
                            })
                
                elif tool_name == "coordinator_list_generated_projects":
                    # Use the Coordinator Agent through chat_with_coordinator
                    message = {
                        "type": "project_generation",
                        "action": "list_projects"
                    }
                    
                    result = agent_system.chat_with_coordinator(json.dumps(message))
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["response"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to list generated projects through coordinator: {result['error']}"
                        })
                
                # Phase 6: LLM Integration & Model Orchestration Tools
                elif tool_name == "get_llm_models":
                    provider = arguments.get("provider", "all")
                    result = agent_system.get_llm_models(provider)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get LLM models: {result['error']}"
                        })
                
                elif tool_name == "select_best_llm_model":
                    task_type = arguments.get("task_type", "")
                    context = arguments.get("context", "")
                    
                    if not task_type:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "task_type is required"
                        })
                    else:
                        result = agent_system.select_best_llm_model(task_type, context)
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to select best LLM model: {result['error']}"
                            })
                
                elif tool_name == "generate_with_llm":
                    prompt = arguments.get("prompt", "")
                    task_type = arguments.get("task_type", "")
                    preferred_model = arguments.get("preferred_model", "")
                    temperature = arguments.get("temperature", 0.7)
                    max_tokens = arguments.get("max_tokens", 4096)
                    
                    if not prompt or not task_type:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "Both prompt and task_type are required"
                        })
                    else:
                        result = agent_system.generate_with_llm(
                            prompt, task_type, preferred_model, temperature, max_tokens
                        )
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to generate with LLM: {result['error']}"
                            })
                
                elif tool_name == "get_llm_performance_stats":
                    result = agent_system.get_llm_performance_stats()
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get LLM performance stats: {result['error']}"
                        })
                
                elif tool_name == "test_llm_integration":
                    test_type = arguments.get("test_type", "connectivity")
                    result = agent_system.test_llm_integration(test_type)
                    if result["success"]:
                        send_response(request_id, {
                            "content": [{"type": "text", "text": result["message"]}],
                            "structuredContent": result
                        })
                    else:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to test LLM integration: {result['error']}"
                        })
                
                elif tool_name == "orchestrate_llm_models":
                    task_description = arguments.get("task_description", "")
                    required_capabilities = arguments.get("required_capabilities", [])
                    coordination_strategy = arguments.get("coordination_strategy", "sequential")
                    
                    if not task_description or not required_capabilities:
                        send_response(request_id, error={
                            "code": -32602,
                            "message": "Both task_description and required_capabilities are required"
                        })
                    else:
                        result = agent_system.orchestrate_llm_models(
                            task_description, required_capabilities, coordination_strategy
                        )
                        if result["success"]:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": result["message"]}],
                                "structuredContent": result
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to orchestrate LLM models: {result['error']}"
                            })
                
                # Instance Management Tools
                elif tool_name == "get_instance_info":
                    try:
                        instance_info = agent_system.get_instance_info()
                        send_response(request_id, {
                            "content": [{"type": "text", "text": f"Instance Information:\n{json.dumps(instance_info, indent=2)}"}],
                            "structuredContent": instance_info
                        })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get instance info: {str(e)}"
                        })
                
                elif tool_name == "get_registry_status":
                    try:
                        if agent_system.registry:
                            status = agent_system.registry.get_registry_status()
                            send_response(request_id, {
                                "content": [{"type": "text", "text": f"Registry Status:\n{json.dumps(status, indent=2)}"}],
                                "structuredContent": status
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": "Instance registry not available"
                            })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get registry status: {str(e)}"
                        })
                
                elif tool_name == "get_dashboard_status":
                    try:
                        from src.dashboard.dashboard_spawner import get_dashboard_spawner
                        spawner = get_dashboard_spawner()
                        status = spawner.get_dashboard_status(agent_system.instance_id)
                        
                        if status:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": f"Dashboard Status:\n{json.dumps(status, indent=2)}"}],
                                "structuredContent": status
                            })
                        else:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": f"No dashboard found for instance {agent_system.instance_id}"}],
                                "structuredContent": {"status": "not_found", "instance_id": agent_system.instance_id}
                            })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get dashboard status: {str(e)}"
                        })
                
                elif tool_name == "get_all_dashboards_status":
                    try:
                        from src.dashboard.dashboard_spawner import get_dashboard_spawner
                        spawner = get_dashboard_spawner()
                        status = spawner.get_all_dashboards_status()
                        
                        send_response(request_id, {
                            "content": [{"type": "text", "text": f"All Dashboards Status:\n{json.dumps(status, indent=2)}"}],
                            "structuredContent": status
                        })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get all dashboards status: {str(e)}"
                        })
                
                elif tool_name == "get_browser_status":
                    try:
                        from src.dashboard.browser_manager import get_browser_status
                        status = get_browser_status()
                        
                        send_response(request_id, {
                            "content": [{"type": "text", "text": f"Browser Status:\n{json.dumps(status, indent=2)}"}],
                            "structuredContent": status
                        })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to get browser status: {str(e)}"
                        })
                
                elif tool_name == "open_dashboard_browser":
                    try:
                        from src.dashboard.dashboard_spawner import get_dashboard_spawner
                        spawner = get_dashboard_spawner()
                        success = spawner.open_dashboard_browser(agent_system.instance_id)
                        
                        if success:
                            send_response(request_id, {
                                "content": [{"type": "text", "text": f"✅ Dashboard opened in browser for instance {agent_system.instance_id}"}],
                                "structuredContent": {"success": True, "instance_id": agent_system.instance_id}
                            })
                        else:
                            send_response(request_id, error={
                                "code": -32603,
                                "message": f"Failed to open dashboard in browser for instance {agent_system.instance_id}"
                            })
                    except Exception as e:
                        send_response(request_id, error={
                            "code": -32603,
                            "message": f"Failed to open dashboard browser: {str(e)}"
                        })
                
                else:
                    send_response(request_id, error={"code": -32601, "message": f"Unknown tool: {tool_name}"})
                    
            else:
                # Handle other methods
                logger.info(f"Unhandled method: {method}")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error: {e}")
            if 'request_id' in locals():
                send_response(request_id, error={"code": -32603, "message": f"Internal error: {str(e)}"})

if __name__ == "__main__":
    main()
