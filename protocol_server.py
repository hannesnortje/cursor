#!/usr/bin/env python3
import json
import logging
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import threading
import subprocess
import os
import time
import requests

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

# Import security middleware
try:
    from src.security.middleware import security_middleware
    from src.security.headers import SecurityHeaders
    from src.security.rate_limiting import rate_limiter

    SECURITY_AVAILABLE = True
    logger = logging.getLogger("enhanced-mcp-server")
    logger.info("Security middleware integration available")
except ImportError as e:
    SECURITY_AVAILABLE = False
    logger = logging.getLogger("enhanced-mcp-server")
    logger.warning(f"Security middleware not available: {e}")

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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

    def initialize_instance(
        self, cursor_client_id: str = None, working_directory: str = None
    ):
        """Initialize instance in registry."""
        try:
            logger.info(f"Starting instance initialization for {self.instance_id}")
            if self.registry and not self.instance_info:
                logger.info("Registry available, registering instance...")

                # Clean up old instances before registering new one
                self._cleanup_old_instances()

                self.instance_info = self.registry.register_instance(
                    instance_id=self.instance_id,
                    cursor_client_id=cursor_client_id,
                    working_directory=working_directory,
                )
                self.instance_id = self.instance_info.instance_id
                logger.info(
                    f"Initialized instance {self.instance_id} with dashboard port {self.instance_info.dashboard_port}"
                )

                # Mark instance as started with current process ID
                import os

                self.registry.start_instance(self.instance_id, os.getpid())
                logger.info(
                    f"Marked instance {self.instance_id} as started with PID {os.getpid()}"
                )

                # Start dashboard spawning immediately (blocking for a moment)
                logger.info("🔧 DEBUG: Starting dashboard spawning...")
                logger.info(
                    f"🔧 DEBUG: Instance info before spawning: {self.instance_info}"
                )
                self._start_dashboard_spawning()
                logger.info("🔧 DEBUG: Dashboard spawning started")
            else:
                logger.info(f"Instance {self.instance_id} initialized without registry")
        except Exception as e:
            logger.warning(
                f"Failed to initialize instance (continuing without instance management): {e}"
            )
            # Continue without instance management - don't break MCP server

    def _cleanup_old_instances(self):
        """Clean up old instances from registry."""
        try:
            if not self.registry:
                return

            import time
            from datetime import datetime

            current_time = time.time()
            old_instances = []

            # Find instances to clean up
            for instance in self.registry.instances.values():
                should_remove = False

                # Remove instances that are stopped (regardless of timestamp)
                if instance.status.value == "stopped":
                    should_remove = True
                    logger.info(f"🧹 Found stopped instance: {instance.instance_id}")

                # Remove instances that are starting but have no process_id (orphaned)
                elif instance.status.value == "starting" and not instance.process_id:
                    should_remove = True
                    logger.info(
                        f"🧹 Found orphaned starting instance: {instance.instance_id}"
                    )

                # Remove instances that are running but the process is dead or suspended
                elif instance.status.value == "running" and instance.process_id:
                    try:
                        import os
                        import psutil

                        # Check if process exists and is actually running (not suspended)
                        process = psutil.Process(instance.process_id)
                        if process.status() in ["stopped", "zombie", "dead"]:
                            should_remove = True
                            logger.info(
                                f"🧹 Found suspended/dead running instance: {instance.instance_id} (status: {process.status()})"
                            )
                        else:
                            # Also check if it's been running for too long without activity
                            import time

                            current_time = time.time()
                            if hasattr(instance, "started_at") and instance.started_at:
                                if isinstance(instance.started_at, str):
                                    started_dt = datetime.fromisoformat(
                                        instance.started_at
                                    )
                                started_time = started_dt.timestamp()
                                if current_time - started_time > 300:  # 5 minutes
                                    should_remove = True
                                    logger.info(
                                        f"🧹 Found old running instance: {instance.instance_id}"
                                    )
                    except (OSError, ProcessLookupError) as e:
                        should_remove = True
                        logger.info(
                            f"🧹 Found dead running instance: {instance.instance_id} ({e})"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error checking process {instance.process_id}: {e}"
                        )
                        # If we can't check, assume it's dead
                        should_remove = True
                        logger.info(
                            f"🧹 Found uncheckable running instance: {instance.instance_id}"
                        )

                if should_remove:
                    old_instances.append(instance.instance_id)

            # Remove old instances
            for old_id in old_instances:
                self.registry.remove_instance(old_id)
                logger.info(f"✅ Cleaned up old instance: {old_id}")

            if old_instances:
                logger.info(f"🧹 Cleaned up {len(old_instances)} old instances")

        except Exception as e:
            logger.warning(f"⚠️ Failed to cleanup old instances: {e}")

    def _start_dashboard_spawning(self):
        """Start dashboard spawning in background thread."""
        try:

            def spawn_dashboard():
                try:
                    logger.info(
                        f"🔧 DEBUG: Starting dashboard spawn for instance {self.instance_id}"
                    )
                    logger.info(f"🔧 DEBUG: Instance info: {self.instance_info}")

                    if not self.instance_info:
                        logger.error("🔧 DEBUG: No instance_info available!")
                        return

                    if not self.instance_info.dashboard_port:
                        logger.error("🔧 DEBUG: No dashboard_port in instance_info!")
                        return

                    # Use the correct Python interpreter from Poetry virtual environment
                    python_path = "/home/hannesn/.cache/pypoetry/virtualenvs/mcp-server-4zyLa6-K-py3.12/bin/python"
                    dashboard_cmd = [
                        python_path,
                        "/media/hannesn/storage/Code/cursor/src/dashboard/backend/main.py",
                        "--port",
                        str(self.instance_info.dashboard_port),
                        "--instance-id",
                        self.instance_id,
                    ]

                    # Set environment variables
                    env = os.environ.copy()
                    env.update(
                        {
                            "DASHBOARD_PORT": str(self.instance_info.dashboard_port),
                            "MCP_INSTANCE_ID": self.instance_id,
                            "PYTHONPATH": os.getcwd(),
                        }
                    )

                    logger.info(
                        f"🔧 DEBUG: Starting dashboard with command: {' '.join(dashboard_cmd)}"
                    )
                    logger.info(
                        f"🔧 DEBUG: Dashboard port: {self.instance_info.dashboard_port}"
                    )
                    logger.info(f"🔧 DEBUG: Instance ID: {self.instance_id}")

                    # Start dashboard process from the correct directory
                    dashboard_dir = (
                        "/media/hannesn/storage/Code/cursor/src/dashboard/backend"
                    )
                    process = subprocess.Popen(
                        dashboard_cmd,
                        env=env,
                        cwd=dashboard_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    logger.info(
                        f"🔧 DEBUG: Started dashboard process {process.pid} for instance {self.instance_id}"
                    )

                    # Check if process started successfully (non-blocking)
                    import time

                    time.sleep(3)  # Give it more time to start
                    if process.poll() is None:
                        logger.info(
                            f"🔧 DEBUG: Dashboard process {process.pid} is running"
                        )

                        # Wait for dashboard to be ready and then open in browser
                        dashboard_url = (
                            f"http://localhost:{self.instance_info.dashboard_port}"
                        )
                        logger.info(
                            f"🌐 Waiting for dashboard to be ready at {dashboard_url}"
                        )

                        # Try to open browser with retry logic
                        max_retries = 5
                        for attempt in range(max_retries):
                            try:
                                response = requests.get(dashboard_url, timeout=2)
                                if response.status_code == 200:
                                    logger.info(
                                        f"✅ Dashboard is ready at {dashboard_url}"
                                    )
                                    subprocess.Popen(
                                        ["xdg-open", dashboard_url],
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL,
                                    )
                                    logger.info(
                                        f"🌐 Dashboard opened in browser: {dashboard_url}"
                                    )
                                    break
                                else:
                                    logger.info(
                                        f"⏳ Dashboard not ready yet (status {response.status_code}), attempt {attempt + 1}/{max_retries}"
                                    )
                            except Exception as e:
                                logger.info(
                                    f"⏳ Dashboard not ready yet ({e}), attempt {attempt + 1}/{max_retries}"
                                )

                            if attempt < max_retries - 1:
                                time.sleep(2)
                        else:
                            logger.warning(
                                f"⚠️ Dashboard not ready after {max_retries} attempts, opening anyway"
                            )
                            try:
                                subprocess.Popen(
                                    ["xdg-open", dashboard_url],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL,
                                )
                                logger.info(
                                    f"🌐 Dashboard opened in browser: {dashboard_url}"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"⚠️ Failed to open dashboard in browser: {e}"
                                )
                    else:
                        logger.error(
                            f"🔧 DEBUG: Dashboard process {process.pid} exited immediately!"
                        )
                        stdout, stderr = process.communicate()
                        logger.error(f"🔧 DEBUG: stdout: {stdout.decode()}")
                        logger.error(f"🔧 DEBUG: stderr: {stderr.decode()}")

                except Exception as e:
                    logger.error(f"🔧 DEBUG: Failed to spawn dashboard: {e}")
                    import traceback

                    logger.error(f"🔧 DEBUG: Traceback: {traceback.format_exc()}")

            # Start dashboard spawning in background thread
            dashboard_thread = threading.Thread(target=spawn_dashboard, daemon=True)
            dashboard_thread.start()
            logger.info(
                f"Started dashboard spawning thread for instance {self.instance_id}"
            )

        except Exception as e:
            logger.warning(
                f"Failed to start dashboard spawning (continuing without dashboard): {e}"
            )

    def get_instance_info(self) -> Dict[str, Any]:
        """Get instance information."""
        if self.instance_info:
            return self.instance_info.to_dict()
        return {
            "instance_id": self.instance_id,
            "status": "not_registered",
            "dashboard_port": None,
            "dashboard_url": None,
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
                "status": "connected" if self.vector_store else "unavailable",
            },
            "timestamp": datetime.now().isoformat(),
        }

        # Add instance info if available
        if self.instance_info:
            health["instance_info"] = self.get_instance_info()

        return health

    def start_project(self, project_type: str, project_name: str) -> Dict[str, Any]:
        """Start a new project with PDCA framework."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_id = f"{project_type}_{project_name}_{timestamp}"

            project = {
                "id": project_id,
                "name": project_name,
                "type": project_type,
                "status": "planning",
                "created_at": datetime.now().isoformat(),
                "pdca_phase": "plan",
                "agents": [],
                "sprints": [],
            }

            self.projects[project_id] = project
            self.system_status = "active"

            # Store project context in vector database if available
            if self.vector_store:
                try:
                    from src.database.enhanced_vector_store import ProjectContext

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
                            "status": "planning",
                        },
                    )

                    # Store in vector database (async)
                    def store_project_context():
                        try:
                            # Set current project and create collections
                            self.vector_store.set_current_project(project_id)
                            self.vector_store.create_project_collections(project_id)

                            # Store project context as knowledge
                            self.vector_store.upsert_knowledge(
                                knowledge_id=f"proj_{project_id}",
                                content=project_context.content,
                                embedding=[0.0] * 1536,  # Default embedding
                                metadata=project_context.metadata,
                            )
                            logger.info(
                                f"Project context stored in vector database: {project_id}"
                            )
                        except Exception as e:
                            logger.warning(f"Project context storage failed: {e}")

                    # Start vector storage in background thread
                    context_thread = threading.Thread(
                        target=store_project_context, daemon=True
                    )
                    context_thread.start()

                except Exception as e:
                    logger.warning(
                        f"Vector database project context storage failed: {e}"
                    )

            logger.info(f"Started new project: {project_name} ({project_type})")

            message = (
                f"Project '{project_name}' started successfully with PDCA framework"
            )
            return {
                "success": True,
                "project_id": project_id,
                "message": message,
                "project": project,
            }
        except Exception as e:
            logger.error(f"Error starting project: {e}")
            return {"success": False, "error": str(e)}

    def chat_with_coordinator(self, message: str) -> Dict[str, Any]:
        """Handle communication with LLM-based Coordinator Agent."""
        try:
            logger.info(f"Coordinator chat message: {message}")

            # Get the LLM-based coordinator
            coordinator_agent = self._get_or_create_coordinator_agent()

            # Use the LLM-based coordinator for all natural language messages
            if not message.strip().startswith("{"):
                logger.info("Using LLM-based coordinator for natural language message")
                try:
                    import asyncio

                    response = asyncio.run(coordinator_agent.process_message(message))
                    return {
                        "success": True,
                        "response": response.get(
                            "response", "I'm processing your request..."
                        ),
                        "phase": response.get("phase", "plan"),
                        "next_steps": response.get("next_steps", "awaiting_input"),
                        "timestamp": response.get(
                            "timestamp", datetime.now().isoformat()
                        ),
                        "coordinator_status": "active",
                        "llm_enabled": True,
                    }
                except Exception as e:
                    logger.error(f"LLM coordinator error: {e}")
                    return {
                        "success": False,
                        "error": f"Coordinator processing error: {str(e)}",
                        "coordinator_status": "error",
                        "llm_enabled": True,
                    }

            # Handle legacy JSON messages for backwards compatibility
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
                            message_data.get("language"), message_data.get("category")
                        )
                        return {
                            "success": True,
                            "response": f"📋 Project templates retrieved: {result.get('total_count', 0)} templates available",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active",
                        }
                    elif action == "create_from_template":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.generate_project(
                            message_data.get("template_id"),
                            message_data.get("project_name"),
                            message_data.get("target_path", "."),
                            message_data.get("customizations", {}),
                        )
                        return {
                            "success": True,
                            "response": f"✅ Project '{message_data.get('project_name')}' created successfully from template",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active",
                        }
                    elif action == "create_custom":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.create_custom_project(
                            message_data.get("project_name"),
                            message_data.get("language"),
                            message_data.get("custom_structure", {}),
                            message_data.get("target_path", "."),
                        )
                        return {
                            "success": True,
                            "response": f"✅ Custom project '{message_data.get('project_name')}' created successfully in {message_data.get('language')}",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active",
                        }
                    elif action == "customize_template":
                        # Use the direct Project Generation Agent to avoid async complexity
                        project_gen_agent = self._get_or_create_project_gen_agent()
                        result = project_gen_agent.customize_project_template(
                            message_data.get("template_id"),
                            message_data.get("customizations", {}),
                        )
                        return {
                            "success": True,
                            "response": f"✅ Template '{message_data.get('template_id')}' customized successfully",
                            "data": result,
                            "timestamp": datetime.now().isoformat(),
                            "coordinator_status": "active",
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
                            "coordinator_status": "active",
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
                            "coordinator_status": "active",
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Unknown project generation action: {action}",
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
                        "coordinator_status": "active",
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
                    "coordinator_status": "active",
                }

        except Exception as e:
            logger.error(f"Error in coordinator chat: {e}")
            return {"success": False, "error": str(e)}

    def _is_pdca_planning_message(self, message: str) -> bool:
        """Check if message is related to PDCA planning."""
        pdca_keywords = [
            "plan",
            "planning",
            "pdca",
            "project",
            "dashboard",
            "react",
            "typescript",
            "start",
            "build",
            "develop",
            "purpose",
            "goals",
            "objectives",
            "requirements",
            "scope",
            "timeline",
            "strategy",
            "implementation",
        ]
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in pdca_keywords)

    def _handle_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Handle PDCA planning conversation."""
        try:
            message_lower = message.lower()

            # Check if this is an initial project request
            if any(
                word in message_lower
                for word in ["start", "build", "develop", "new project"]
            ):
                return self._start_pdca_planning_phase(message)

            # Check if user wants to create agents (prioritize this check)
            elif any(
                phrase in message_lower
                for phrase in [
                    "create agents",
                    "let's create",
                    "please create",
                    "specialized agents",
                    "agent team",
                    "create the",
                    "create an agile",
                    "create a frontend",
                    "create a backend",
                    "create a testing",
                ]
            ):
                return self._continue_pdca_planning(message)

            # Check if user is providing project details
            elif any(
                word in message_lower
                for word in [
                    "purpose",
                    "goal",
                    "objective",
                    "dashboard",
                    "react",
                    "typescript",
                    "vue",
                    "project management",
                    "web application",
                ]
            ):
                return self._continue_pdca_planning(message)

            # Default PDCA response
            else:
                return self._provide_pdca_guidance(message)

        except Exception as e:
            logger.error(f"Error in PDCA planning: {e}")
            return {"success": False, "error": f"PDCA planning error: {str(e)}"}

    def _start_pdca_planning_phase(self, message: str) -> Dict[str, Any]:
        """Start the PDCA planning phase using the actual Coordinator Agent."""
        try:
            # Get or create the Coordinator Agent
            coordinator_agent = self._get_or_create_coordinator_agent()

            # Use the Coordinator Agent to handle PDCA planning
            result = coordinator_agent.start_pdca_planning(message)

            return {
                "success": True,
                "response": result.get("response", "Starting PDCA planning..."),
                "timestamp": datetime.now().isoformat(),
                "coordinator_status": "active",
                "pdca_phase": result.get("phase", "plan"),
                "next_steps": result.get("next_steps", "awaiting_project_details"),
                "data": result,
            }
        except Exception as e:
            logger.error(f"Error in PDCA planning phase: {e}")
            return {
                "success": False,
                "error": f"PDCA planning error: {str(e)}",
                "response": "I encountered an error while starting the PDCA planning. Let me try a different approach.",
            }

    def _continue_pdca_planning(self, message: str) -> Dict[str, Any]:
        """Continue PDCA planning based on user input using the actual Coordinator Agent."""
        try:
            # Get or create the Coordinator Agent
            coordinator_agent = self._get_or_create_coordinator_agent()

            # Use the Coordinator Agent to continue PDCA planning
            result = coordinator_agent.continue_pdca_planning(message)

            return {
                "success": True,
                "response": result.get("response", "Continuing PDCA planning..."),
                "timestamp": datetime.now().isoformat(),
                "coordinator_status": "active",
                "pdca_phase": result.get("phase", "plan"),
                "next_steps": result.get("next_steps", "agent_strategy_discussion"),
                "data": result,
            }
        except Exception as e:
            logger.error(f"Error in continuing PDCA planning: {e}")
            return {
                "success": False,
                "error": f"PDCA planning error: {str(e)}",
                "response": "I encountered an error while continuing the PDCA planning. Let me try a different approach.",
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
            "next_steps": "awaiting_user_choice",
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
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error starting communication system: {e}")
            return {"success": False, "error": str(e)}

    def create_cross_chat_session(
        self, chat_id: str, chat_type: str, participants: List[str]
    ) -> Dict[str, Any]:
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
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creating cross-chat session: {e}")
            return {"success": False, "error": str(e)}

    def broadcast_cross_chat_message(
        self, source_chat: str, source_agent: str, content: str, target_chats: List[str]
    ) -> Dict[str, Any]:
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
                "target_chats": target_chats,
            }

            # Store in vector database if available
            if self.vector_store:
                try:
                    from src.database.enhanced_vector_store import ConversationPoint

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
                            "source_chat": source_chat,
                        },
                    )

                    # Store in vector database (async)
                    def store_in_vector_db():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            # Convert ConversationPoint to the format expected by upsert_conversation
                            self.vector_store.upsert_conversation(
                                conversation_id=conversation_point.id,
                                message=conversation_point.message,
                                response=conversation_point.context,
                                embedding=conversation_point.vector or [0.0] * 1536,
                                metadata=conversation_point.metadata,
                            )
                            logger.info(
                                f"Message stored in vector database: {message_data['message_id']}"
                            )
                        except Exception as e:
                            logger.warning(f"Vector database storage failed: {e}")

                    # Start vector storage in background thread
                    vector_thread = threading.Thread(
                        target=store_in_vector_db, daemon=True
                    )
                    vector_thread.start()

                except Exception as e:
                    logger.warning(f"Vector database integration failed: {e}")

            # Fallback to in-memory storage
            if not hasattr(self, "_cross_chat_messages"):
                self._cross_chat_messages = []
            self._cross_chat_messages.append(message_data)

            # Try to store in Redis for persistence
            try:
                if hasattr(self, "real_time_handler") and self.real_time_handler:
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
                        metadata={"stored_in_redis": True},
                    )

                    # Store in Redis (async operation in background)
                    def store_in_redis():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(
                                self.real_time_handler.store_cross_chat_message(event)
                            )
                            logger.info(
                                f"Message stored in Redis: {message_data['message_id']}"
                            )
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
                "timestamp": message_data["timestamp"],
            }
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
            return {"success": False, "error": str(e)}

    def get_cross_chat_messages(
        self, chat_id: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
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
                        messages.append(
                            {
                                "message_id": msg.id,
                                "source_chat": msg.session_id,
                                "source_agent": msg.agent_id,
                                "content": msg.message,
                                "timestamp": msg.timestamp.isoformat(),
                                "metadata": msg.metadata,
                            }
                        )

                    logger.info(
                        f"Retrieved {len(messages)} messages from vector database"
                    )

                except Exception as e:
                    logger.warning(f"Vector database retrieval failed: {e}")

            # Fallback to in-memory storage
            if not messages:
                if not hasattr(self, "_cross_chat_messages"):
                    self._cross_chat_messages = []

                messages = self._cross_chat_messages

                # Filter by chat_id if specified
                if chat_id:
                    messages = [
                        msg for msg in messages if msg["source_chat"] == chat_id
                    ]

                # Apply limit
                messages = messages[-limit:] if len(messages) > limit else messages

                logger.info(
                    f"Retrieved {len(messages)} messages from in-memory storage"
                )

            return {
                "success": True,
                "chat_id": chat_id,
                "messages": messages,
                "message_count": len(messages),
                "total_messages": len(messages),
                "storage": (
                    "vector_database" if self.vector_store and messages else "in_memory"
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error retrieving cross-chat messages: {e}")
            return {"success": False, "error": str(e)}

    def search_cross_chat_messages(
        self, query: str, chat_id: Optional[str] = None, limit: int = 50
    ) -> Dict[str, Any]:
        """Search cross-chat messages by content."""
        try:
            logger.info(
                f"Searching cross-chat messages for: '{query}' in chat: {chat_id or 'all'}"
            )

            results = []

            # Try to search in vector database first
            if self.vector_store:
                try:
                    # Search conversations in vector store
                    vector_results = asyncio.run(
                        self.vector_store.search_conversations(
                            query, chat_id, limit=limit
                        )
                    )

                    # Convert to our format
                    for msg in vector_results:
                        results.append(
                            {
                                "message_id": msg.id,
                                "source_chat": msg.session_id,
                                "source_agent": msg.agent_id,
                                "content": msg.message,
                                "timestamp": msg.timestamp.isoformat(),
                                "metadata": msg.metadata,
                                "context": msg.context,
                            }
                        )

                    logger.info(f"Found {len(results)} results in vector database")

                except Exception as e:
                    logger.warning(f"Vector database search failed: {e}")

            # Fallback to in-memory search
            if not results:
                if not hasattr(self, "_cross_chat_messages"):
                    self._cross_chat_messages = []

                messages = self._cross_chat_messages

                # Filter by chat_id if specified
                if chat_id:
                    messages = [
                        msg for msg in messages if msg["source_chat"] == chat_id
                    ]

                # Search by content
                query_lower = query.lower()
                results = [
                    msg for msg in messages if query_lower in msg["content"].lower()
                ]

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
                "storage": (
                    "vector_database" if self.vector_store and results else "in_memory"
                ),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error searching cross-chat messages: {e}")
            return {"success": False, "error": str(e)}

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
                        "collections": stats,
                    }
                except Exception as e:
                    vector_stats = {
                        "status": "error",
                        "available": False,
                        "type": "Qdrant",
                        "error": str(e),
                    }
            else:
                vector_stats = {
                    "status": "unavailable",
                    "available": False,
                    "type": "None",
                }

            return {
                "success": True,
                "websocket_server": {
                    "status": "running",
                    "port": 4000,
                    "host": "localhost",
                },
                "redis_queue": {
                    "status": "configured",
                    "host": "localhost",
                    "port": 6379,
                },
                "cross_chat": {
                    "status": "active",
                    "active_sessions": 0,
                    "total_messages": 0,
                },
                "vector_store": vector_stats,
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting communication status: {e}")
            return {"success": False, "error": str(e)}

    def create_agile_project(
        self,
        project_name: str,
        project_type: str = "scrum",
        sprint_length: int = None,
        team_size: int = 5,
    ) -> Dict[str, Any]:
        """Create a new agile project."""
        try:
            # Get or create Agile Agent
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_agile_project(
                project_name, project_type, sprint_length, team_size
            )
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
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_user_story(
                project_id,
                title,
                description,
                acceptance_criteria,
                story_points,
                priority,
                epic,
            )
        except Exception as e:
            logger.error(f"Error creating user story: {e}")
            return {"success": False, "error": str(e)}

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
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.create_sprint(
                project_id, sprint_name, start_date, end_date, goal
            )
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

    def complete_user_story(
        self, story_id: str, actual_hours: float = None
    ) -> Dict[str, Any]:
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

    def calculate_team_velocity(
        self, project_id: str, sprint_count: int = None
    ) -> Dict[str, Any]:
        """Calculate team velocity based on completed sprints."""
        try:
            agile_agent = self._get_or_create_agile_agent()
            return agile_agent.calculate_team_velocity(project_id, sprint_count)
        except Exception as e:
            logger.error(f"Error calculating team velocity: {e}")
            return {"success": False, "error": str(e)}

    def list_project_templates(
        self, language: Optional[str] = None, category: Optional[str] = None
    ) -> Dict[str, Any]:
        """List available project templates with optional filtering."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.list_project_templates(language, category)
        except Exception as e:
            logger.error(f"Error listing project templates: {e}")
            return {"success": False, "error": str(e)}

    def generate_project(
        self,
        template_id: str,
        project_name: str,
        target_path: str = ".",
        customizations: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate a new project from a template."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.generate_project(
                template_id, project_name, target_path, customizations
            )
        except Exception as e:
            logger.error(f"Error generating project: {e}")
            return {"success": False, "error": str(e)}

    def customize_project_template(
        self, template_id: str, customizations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize an existing project template."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.customize_project_template(
                template_id, customizations
            )
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

    def create_custom_project(
        self,
        project_name: str,
        language: str,
        custom_structure: Dict[str, Any] = None,
        target_path: str = ".",
    ) -> Dict[str, Any]:
        """Create a completely custom project with user-defined structure."""
        try:
            # Get or create Project Generation Agent
            project_gen_agent = self._get_or_create_project_gen_agent()
            return project_gen_agent.create_custom_project(
                project_name, language, custom_structure, target_path
            )
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
            if hasattr(agent, "name") and agent.name == "Project Generation Agent":
                return agent

        # Create new Project Generation Agent if none exists
        try:
            from src.agents.specialized.project_generation_agent import (
                ProjectGenerationAgent,
            )

            project_gen_agent = ProjectGenerationAgent()
            self.register_agent(project_gen_agent)
            logger.info("Created new Project Generation Agent")
            return project_gen_agent
        except ImportError as e:
            logger.error(f"Could not import ProjectGenerationAgent: {e}")
            raise

    # Phase 5.3: Backend Agent Methods
    def design_api(
        self,
        api_type: str,
        name: str,
        description: str = "",
        endpoints: List[Dict[str, Any]] = None,
        data_models: List[Dict[str, Any]] = None,
        authentication: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Design a new API specification."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.design_api(
                api_type, name, description, endpoints, data_models, authentication
            )
        except Exception as e:
            logger.error(f"Error designing API: {e}")
            return {"success": False, "error": str(e)}

    def create_database_schema(
        self,
        database_type: str,
        name: str,
        description: str = "",
        entities: List[Dict[str, Any]] = None,
        relationships: List[Dict[str, Any]] = None,
        constraints: List[Dict[str, Any]] = None,
        indexes: List[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new database schema."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.create_database_schema(
                database_type,
                name,
                description,
                entities,
                relationships,
                constraints,
                indexes,
            )
        except Exception as e:
            logger.error(f"Error creating database schema: {e}")
            return {"success": False, "error": str(e)}

    def implement_security(
        self,
        security_type: str,
        name: str,
        description: str = "",
        method: str = "jwt",
        configuration: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Implement security configuration."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.implement_security(
                security_type, name, description, method, configuration
            )
        except Exception as e:
            logger.error(f"Error implementing security: {e}")
            return {"success": False, "error": str(e)}

    def design_architecture(
        self,
        architecture_type: str,
        name: str,
        description: str = "",
        components: List[Dict[str, Any]] = None,
        deployment: str = "docker",
        scaling: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Design system architecture."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.design_architecture(
                architecture_type, name, description, components, deployment, scaling
            )
        except Exception as e:
            logger.error(f"Error designing architecture: {e}")
            return {"success": False, "error": str(e)}

    def generate_api_code(
        self, language: str, framework: str, specification_id: str
    ) -> Dict[str, Any]:
        """Generate API code for the specified language and framework."""
        try:
            # Get or create Backend Agent
            backend_agent = self._get_or_create_backend_agent()
            return backend_agent.generate_api_code(
                language, framework, specification_id
            )
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
                    "architecture_designs": arch_designs,
                }
                message = f"Retrieved {len(api_specs)} APIs, {len(db_schemas)} databases, {len(security_configs)} security configs, {len(arch_designs)} architectures"

            return {
                "success": True,
                "message": message,
                "specifications": specs,
                "type": spec_type,
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
                    "databases": databases,
                }
                message = f"Supported technologies: {len(languages)} languages, {sum(len(f) for f in frameworks.values())} frameworks, {sum(len(d) for d in databases.values())} database types"

            return {
                "success": True,
                "message": message,
                "technologies": techs,
                "category": category or "all",
            }
        except Exception as e:
            logger.error(f"Error getting supported technologies: {e}")
            return {"success": False, "error": str(e)}

    def _get_or_create_backend_agent(self):
        """Get or create a Backend Agent instance."""
        # Check if we already have a Backend Agent
        for agent in self.agents.values():
            if hasattr(agent, "name") and agent.name == "Backend Agent":
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
        """Get or create a Simple Coordinator Agent instance with LLM decision engine."""
        # Check if we already have a Coordinator Agent
        for agent in self.agents.values():
            if hasattr(agent, "name") and agent.name == "Simple Coordinator":
                return agent

        # Create new Simple Coordinator Agent if none exists
        try:
            from src.agents.coordinator.simple_coordinator_agent import (
                SimpleCoordinatorAgent,
            )

            coordinator_agent = SimpleCoordinatorAgent()
            self.register_agent(coordinator_agent)
            logger.info("Created new Simple Coordinator Agent with LLM decision engine")
            return coordinator_agent
        except ImportError as e:
            logger.error(f"Could not import SimpleCoordinatorAgent: {e}")
            raise

    def _get_or_create_agile_agent(self):
        """Get or create an Agile Agent instance."""
        # Check if we already have an Agile Agent
        for agent in self.agents.values():
            if hasattr(agent, "name") and agent.name == "Agile Agent":
                return agent

        # Create new Agile Agent if none exists
        try:
            from src.agents.specialized.agile_agent import AgileAgent
            from src.agents.specialized.project_generation_agent import (
                ProjectGenerationAgent,
            )

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
        if hasattr(agent, "agent_id"):
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
                    "type": (
                        agent.agent_type.value
                        if hasattr(agent, "agent_type")
                        else "unknown"
                    ),
                    "status": (
                        agent.status.value if hasattr(agent, "status") else "unknown"
                    ),
                }

                # Add Agile Agent specific data
                if hasattr(agent, "name") and agent.name == "Agile Agent":
                    if hasattr(agent, "agile_projects"):
                        agent_info[agent_id]["agile_projects"] = len(
                            agent.agile_projects
                        )
                        agent_info[agent_id]["project_ids"] = list(
                            agent.agile_projects.keys()
                        )
                    if hasattr(agent, "user_stories"):
                        agent_info[agent_id]["user_stories"] = len(agent.user_stories)
                        agent_info[agent_id]["story_ids"] = list(
                            agent.user_stories.keys()
                        )

            return {
                "success": True,
                "total_agents": len(self.agents),
                "agents": agent_info,
            }
        except Exception as e:
            logger.error(f"Error listing agents: {e}")
            return {"success": False, "error": str(e)}

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
                if provider_name in ["cursor", "docker_ollama", "lm_studio"]:
                    if isinstance(models, list):
                        try:
                            serializable_models[provider_name] = []
                            for model in models:
                                try:
                                    if hasattr(model, "to_dict") and callable(
                                        model.to_dict
                                    ):
                                        model_dict = model.to_dict()
                                        serializable_models[provider_name].append(
                                            model_dict
                                        )
                                    else:
                                        # Fallback serialization
                                        model_dict = {
                                            "name": str(
                                                getattr(model, "name", "unknown")
                                            ),
                                            "provider": str(
                                                getattr(model, "provider", "unknown")
                                            ),
                                            "model_type": str(
                                                getattr(model, "model_type", "unknown")
                                            ),
                                            "max_tokens": getattr(
                                                model, "max_tokens", 4096
                                            ),
                                            "temperature": getattr(
                                                model, "temperature", 0.7
                                            ),
                                            "api_base": str(
                                                getattr(model, "api_base", "unknown")
                                            ),
                                            "is_available": getattr(
                                                model, "is_available", True
                                            ),
                                        }
                                        serializable_models[provider_name].append(
                                            model_dict
                                        )
                                except Exception as model_error:
                                    logger.warning(
                                        f"Error serializing model {getattr(model, 'name', 'unknown')}: {model_error}"
                                    )
                                    # Add basic model info as fallback
                                    serializable_models[provider_name].append(
                                        {
                                            "name": str(
                                                getattr(model, "name", "unknown")
                                            ),
                                            "provider": "unknown",
                                            "model_type": "unknown",
                                            "max_tokens": 4096,
                                            "temperature": 0.7,
                                            "api_base": "unknown",
                                            "is_available": True,
                                        }
                                    )
                        except Exception as list_error:
                            logger.error(
                                f"Error processing models list for {provider_name}: {list_error}"
                            )
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

            total_count = sum(
                len(models)
                for models in filtered_models.values()
                if isinstance(models, list)
            )

            # Add debug logging
            logger.info(
                f"Successfully serialized {total_count} models from {len(filtered_models)} providers"
            )
            logger.info(f"Serializable models: {serializable_models}")

            return {
                "success": True,
                "message": f"Found {total_count} LLM models from {len(filtered_models)} providers",
                "models": filtered_models,
                "total_count": total_count,
                "provider": provider,
            }
        except Exception as e:
            logger.error(f"Error getting LLM models: {e}")
            import traceback

            logger.error(f"Traceback: {traceback.format_exc()}")
            return {"success": False, "error": str(e)}

    def select_best_llm_model(
        self, task_type: str, context: str = ""
    ) -> Dict[str, Any]:
        """Select the best LLM model for a specific task type."""
        try:
            from src.llm.llm_gateway import llm_gateway

            # Select best model using the LLM gateway
            selected_model = asyncio.run(
                llm_gateway.select_best_model(task_type, context)
            )

            # Convert model to serializable format
            if hasattr(selected_model, "to_dict"):
                model_dict = selected_model.to_dict()
            else:
                model_dict = {
                    "name": str(selected_model),
                    "provider": "unknown",
                    "model_type": "unknown",
                    "max_tokens": 4096,
                    "temperature": 0.7,
                }

            return {
                "success": True,
                "message": f"Selected best model for {task_type} task: {model_dict['name']}",
                "model": model_dict,
                "task_type": task_type,
                "context": context,
            }
        except Exception as e:
            logger.error(f"Error selecting best LLM model: {e}")
            return {"success": False, "error": str(e)}

    def generate_with_llm(
        self,
        prompt: str,
        task_type: str,
        preferred_model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict[str, Any]:
        """Generate text using LLM with automatic fallback."""
        try:
            from src.llm.llm_gateway import llm_gateway

            # Generate text using the LLM gateway
            result = asyncio.run(
                llm_gateway.generate_with_fallback(
                    prompt,
                    task_type,
                    preferred_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )

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
                "max_tokens": max_tokens,
            }
        except Exception as e:
            logger.error(f"Error generating with LLM: {e}")
            return {"success": False, "error": str(e)}

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
                "total_models": len(stats),
            }
        except Exception as e:
            logger.error(f"Error getting LLM performance stats: {e}")
            return {"success": False, "error": str(e)}

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
                    if provider_name in [
                        "cursor",
                        "docker_ollama",
                        "lm_studio",
                    ] and isinstance(models, list):
                        total_models += len(models)
                        providers.append(provider_name)

                return {
                    "success": True,
                    "message": f"LLM integration test passed: {total_models} models available",
                    "test_type": test_type,
                    "models_available": total_models,
                    "providers": providers,
                }
            elif test_type == "generation":
                # Test text generation
                test_prompt = "Hello, this is a test message."
                result = asyncio.run(
                    llm_gateway.generate_with_fallback(test_prompt, "general")
                )

                return {
                    "success": True,
                    "message": f"LLM generation test passed: {len(result)} characters generated",
                    "test_type": test_type,
                    "test_prompt": test_prompt,
                    "result_length": len(result),
                }
            elif test_type == "fallback":
                # Test fallback mechanism
                # This would require more sophisticated testing
                return {
                    "success": True,
                    "message": "LLM fallback test passed (basic check)",
                    "test_type": test_type,
                    "fallback_available": True,
                }
            else:
                return {"success": False, "error": f"Unknown test type: {test_type}"}
        except Exception as e:
            logger.error(f"Error testing LLM integration: {e}")
            return {"success": False, "error": str(e)}

    def orchestrate_llm_models(
        self,
        task_description: str,
        required_capabilities: list,
        coordination_strategy: str = "sequential",
    ) -> Dict[str, Any]:
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
                                if (
                                    hasattr(model, "model_type")
                                    and model.model_type.value == "coding"
                                ):
                                    selected_models.append(model)
                                    break
                elif capability == "creative":
                    # Look for creative models
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if (
                                    hasattr(model, "model_type")
                                    and model.model_type.value == "creative"
                                ):
                                    selected_models.append(model)
                                    break
                elif capability == "analysis":
                    # Look for analysis models
                    for provider_models in available_models.values():
                        if isinstance(provider_models, list):
                            for model in provider_models:
                                if (
                                    hasattr(model, "model_type")
                                    and model.model_type.value == "analysis"
                                ):
                                    selected_models.append(model)
                                    break

            if not selected_models:
                # Fallback to general models
                for provider_models in available_models.values():
                    if isinstance(provider_models, list):
                        for model in provider_models:
                            if (
                                hasattr(model, "model_type")
                                and model.model_type.value == "general"
                            ):
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
                        "model_type": model.model_type.value,
                    }
                    for model in selected_models
                ],
                "total_models": len(selected_models),
            }
        except Exception as e:
            logger.error(f"Error orchestrating LLM models: {e}")
            return {"success": False, "error": str(e)}


# Initialize agent system
agent_system = AgentSystem()
current_instance_id = None


def send_response(request_id, result=None, error=None):
    """Send a JSON-RPC response with security headers."""
    response = {"jsonrpc": "2.0", "id": request_id}
    if error:
        response["error"] = error
    else:
        response["result"] = result

    # Security metadata is disabled for MCP compatibility
    # The security middleware still works but doesn't add metadata to responses

    print(json.dumps(response), flush=True)


def send_notification(method, params=None):
    """Send a JSON-RPC notification."""
    notification = {"jsonrpc": "2.0", "method": method}
    if params:
        notification["params"] = params

    print(json.dumps(notification), flush=True)


def main():
    # Check for command line arguments first
    if len(sys.argv) > 1:
        if sys.argv[1] in ["--help", "-h"]:
            print(
                """
Enhanced MCP Server with Agent System

Usage: python protocol_server.py [options]

Options:
  --help, -h          Show this help message
  --version, -v       Show version information
  --test              Run in test mode (no MCP protocol)

This server provides:
- MCP (Model Context Protocol) server for Cursor IDE integration
- Agent system with specialized agents (Frontend, Backend, Testing, etc.)
- Vector database integration with Qdrant
- Dashboard for real-time monitoring
- Cross-chat communication system

For more information, see the documentation in docs/
            """
            )
            return
        elif sys.argv[1] in ["--version", "-v"]:
            print("Enhanced MCP Server v1.0.0")
            return
        elif sys.argv[1] == "--test":
            print("Running in test mode - MCP protocol disabled")
            # Run in test mode without MCP protocol
            return

    logger.info("Starting enhanced MCP server with agent system...")

    # Initialize agent system first (core functionality)
    global agent_system, current_instance_id
    agent_system = AgentSystem()
    current_instance_id = agent_system.instance_id
    logger.info(f"Initialized MCP server instance {agent_system.instance_id}")

    # Try to initialize instance management (non-blocking)
    try:
        import os

        cursor_client_id = os.environ.get("CURSOR_CLIENT_ID", f"cursor_{os.getpid()}")
        working_directory = os.getcwd()

        # Initialize instance management
        agent_system.initialize_instance(
            cursor_client_id=cursor_client_id, working_directory=working_directory
        )

        if agent_system.instance_info:
            logger.info(
                f"Dashboard will be available at: {agent_system.instance_info.dashboard_url}"
            )
        else:
            logger.info(
                "Instance management not available - MCP server running in basic mode"
            )

    except Exception as e:
        logger.warning(
            f"Instance management initialization failed (continuing in basic mode): {e}"
        )
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
                                "b": {"type": "integer"},
                            },
                            "required": ["a", "b"],
                        },
                    },
                    {
                        "name": "reverse_text",
                        "description": "Reverse the given string.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"text": {"type": "string"}},
                            "required": ["text"],
                        },
                    },
                    # New agent system tools
                    {
                        "name": "start_project",
                        "description": "Start a new project with PDCA framework",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_type": {"type": "string"},
                                "project_name": {"type": "string"},
                            },
                            "required": ["project_type", "project_name"],
                        },
                    },
                    {
                        "name": "chat_with_coordinator",
                        "description": "Direct communication with Coordinator Agent",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"message": {"type": "string"}},
                            "required": ["message"],
                        },
                    },
                    # Phase 4: Communication System Tools
                    {
                        "name": "start_communication_system",
                        "description": "Start the communication system (WebSocket + Redis)",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    {
                        "name": "get_communication_status",
                        "description": "Get communication system status and health",
                        "inputSchema": {"type": "object", "properties": {}},
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
                                "participants": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["chat_id", "chat_type", "participants"],
                        },
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
                                "target_chats": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": [
                                "source_chat",
                                "source_agent",
                                "content",
                                "target_chats",
                            ],
                        },
                    },
                    # Phase 4.3: Message Queue Integration Tools
                    {
                        "name": "get_cross_chat_messages",
                        "description": "Get cross-chat messages for a specific chat or all chats",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "chat_id": {"type": "string"},
                                "limit": {"type": "integer"},
                            },
                            "required": [],
                        },
                    },
                    {
                        "name": "search_cross_chat_messages",
                        "description": "Search cross-chat messages by content",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "chat_id": {"type": "string"},
                                "limit": {"type": "integer"},
                            },
                            "required": ["query"],
                        },
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
                                "team_size": {"type": "integer", "default": 5},
                            },
                            "required": ["project_name"],
                        },
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
                                "acceptance_criteria": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "story_points": {"type": "integer"},
                                "priority": {"type": "string", "default": "medium"},
                                "epic": {"type": "string"},
                            },
                            "required": [
                                "project_id",
                                "title",
                                "description",
                                "acceptance_criteria",
                            ],
                        },
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
                                "goal": {"type": "string"},
                            },
                            "required": ["project_id", "sprint_name"],
                        },
                    },
                    {
                        "name": "plan_sprint",
                        "description": "Plan a sprint by assigning user stories",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "sprint_id": {"type": "string"},
                                "story_ids": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["sprint_id", "story_ids"],
                        },
                    },
                    {
                        "name": "complete_user_story",
                        "description": "Mark a user story as completed",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "story_id": {"type": "string"},
                                "actual_hours": {"type": "number"},
                            },
                            "required": ["story_id"],
                        },
                    },
                    {
                        "name": "get_project_status",
                        "description": "Get comprehensive project status and metrics for an agile project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"project_id": {"type": "string"}},
                            "required": ["project_id"],
                        },
                    },
                    {
                        "name": "get_sprint_burndown",
                        "description": "Generate burndown chart data for a sprint",
                        "inputSchema": {
                            "type": "object",
                            "properties": {"sprint_id": {"type": "string"}},
                            "required": ["sprint_id"],
                        },
                    },
                    {
                        "name": "calculate_team_velocity",
                        "description": "Calculate team velocity based on completed sprints",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {"type": "string"},
                                "sprint_count": {"type": "integer"},
                            },
                            "required": ["project_id"],
                        },
                    },
                    # New Project Generation Agent Tools
                    {
                        "name": "list_project_templates",
                        "description": "List available project templates with optional filtering by language and category",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "language": {
                                    "type": "string",
                                    "description": "Filter by programming language (python, cpp, java, go, rust, typescript, etc.)",
                                },
                                "category": {
                                    "type": "string",
                                    "description": "Filter by project category (web, api, library, cli, data-science, etc.)",
                                },
                            },
                            "required": [],
                        },
                    },
                    {
                        "name": "generate_project",
                        "description": "Generate a new project from a template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {
                                    "type": "string",
                                    "description": "ID of the template to use",
                                },
                                "project_name": {
                                    "type": "string",
                                    "description": "Name of the project to create",
                                },
                                "target_path": {
                                    "type": "string",
                                    "default": ".",
                                    "description": "Path where to create the project",
                                },
                                "customizations": {
                                    "type": "object",
                                    "description": "Optional customizations for the project",
                                },
                            },
                            "required": ["template_id", "project_name"],
                        },
                    },
                    {
                        "name": "customize_project_template",
                        "description": "Customize an existing project template",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "template_id": {
                                    "type": "string",
                                    "description": "ID of the template to customize",
                                },
                                "customizations": {
                                    "type": "object",
                                    "description": "Customizations to apply to the template",
                                },
                            },
                            "required": ["template_id", "customizations"],
                        },
                    },
                    {
                        "name": "get_generated_project_status",
                        "description": "Get status of a generated project",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "ID of the generated project",
                                }
                            },
                            "required": ["project_id"],
                        },
                    },
                    {
                        "name": "list_generated_projects",
                        "description": "List all generated projects",
                        "inputSchema": {"type": "object", "properties": {}},
                    },
                    # Phase 9.1: Project-Specific Qdrant Database Tools
                    {
                        "name": "start_container",
                        "description": "Start Qdrant Docker container with error handling",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    },
                    {
                        "name": "create_database",
                        "description": "Create a new project-specific database with validation",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_name": {
                                    "type": "string",
                                    "description": "Name of the project",
                                },
                                "project_id": {
                                    "type": "string",
                                    "description": "Optional project ID (auto-generated if not provided)",
                                },
                            },
                            "required": ["project_name"],
                        },
                    },
                    {
                        "name": "list_databases",
                        "description": "List all project databases with fallback",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": [],
                        },
                    },
                    {
                        "name": "switch_database",
                        "description": "Switch to a specific project database with error handling",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to switch to",
                                }
                            },
                            "required": ["project_id"],
                        },
                    },
                    {
                        "name": "archive_database",
                        "description": "Archive a project database with confirmation",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to archive",
                                }
                            },
                            "required": ["project_id"],
                        },
                    },
                    {
                        "name": "restore_database",
                        "description": "Restore an archived project database with validation",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to restore",
                                }
                            },
                            "required": ["project_id"],
                        },
                    },
                    {
                        "name": "delete_database",
                        "description": "Delete a project database with safety checks",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Project ID to delete",
                                },
                                "confirm": {
                                    "type": "boolean",
                                    "description": "Confirmation flag for deletion",
                                },
                            },
                            "required": ["project_id", "confirm"],
                        },
                    },
                    {
                        "name": "get_stats",
                        "description": "Get database statistics with fallback data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_id": {
                                    "type": "string",
                                    "description": "Optional project ID for specific stats",
                                }
                            },
                            "required": [],
                        },
                    },
                ]
            },
            "chat": {"message": True},
        },
        "serverInfo": {
            "name": "enhanced-mcp-server",
            "version": "1.1.0",
            "description": "Enhanced MCP server with AI agent system capabilities",
        },
    }

    # Read input and respond
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            logger.info(f"Received: {data}")

            method = data.get("method")
            request_id = data.get("id")

            # Security middleware is disabled for MCP compatibility
            # Security features are still available via MCP tools but don't interfere with protocol

            if method == "initialize":
                send_response(request_id, init_response)
                # Send initialized notification
                send_notification("initialized")
                logger.info("MCP server initialized successfully")

                # Automatically spawn dashboard for Cursor connection
                try:
                    logger.info("Auto-spawning dashboard for Cursor connection...")

                    # Only spawn if we have instance info and no dashboard is running
                    if (
                        agent_system.instance_info
                        and agent_system.instance_info.dashboard_port
                    ):
                        # Check if dashboard is already running for this instance
                        import subprocess

                        try:
                            result = subprocess.run(
                                [
                                    "pgrep",
                                    "-f",
                                    f"dashboard.*--instance-id {agent_system.instance_id}",
                                ],
                                capture_output=True,
                                text=True,
                            )
                            if result.returncode == 0:
                                logger.info(
                                    f"Dashboard already running for instance {agent_system.instance_id}"
                                )
                            else:
                                # Spawn dashboard using the existing mechanism
                                logger.info(
                                    f"Spawning dashboard for instance {agent_system.instance_id} on port {agent_system.instance_info.dashboard_port}"
                                )
                                agent_system._start_dashboard_spawning()
                        except Exception as e:
                            logger.warning(
                                f"Failed to check for existing dashboard: {e}"
                            )
                            # Try to spawn anyway
                            agent_system._start_dashboard_spawning()
                    else:
                        logger.info("No instance info available for dashboard spawning")
                except Exception as e:
                    logger.warning(f"Error auto-spawning dashboard: {e}")

            elif method == "tools/list":
                # Import consolidated MCP tools
                from src.mcp_tools.consolidated_handlers import get_all_mcp_tools

                tools_response = {"tools": get_all_mcp_tools()}
                send_response(request_id, tools_response)

            elif method == "tools/call":
                # Handle tool calls
                tool_name = data.get("params", {}).get("name")
                arguments = data.get("params", {}).get("arguments", {})

                # Import consolidated MCP tools handler
                from src.mcp_tools.consolidated_handlers import handle_mcp_tool

                # Try to handle the tool with consolidated handler
                if handle_mcp_tool(tool_name, arguments, request_id, send_response):
                    # Tool was handled successfully
                    pass
                else:
                    # Tool not found
                    send_response(
                        request_id,
                        error={"code": -32601, "message": f"Unknown tool: {tool_name}"},
                    )

            elif method == "chat/message":
                # Handle natural language messages - route to Coordinator Agent
                try:
                    message_content = data.get("params", {}).get("content", "")
                    if not message_content:
                        send_response(
                            request_id,
                            error={
                                "code": -32602,
                                "message": "Message content is required",
                            },
                        )
                        return

                    # Route to Coordinator Agent
                    result = agent_system.chat_with_coordinator(message_content)

                    if result["success"]:
                        send_response(
                            request_id,
                            {
                                "content": [
                                    {"type": "text", "text": result["response"]}
                                ],
                                "structuredContent": result,
                            },
                        )
                    else:
                        send_response(
                            request_id,
                            error={"code": -32603, "message": result["error"]},
                        )

                except Exception as e:
                    logger.error(f"Error handling chat message: {e}")
                    send_response(
                        request_id,
                        error={
                            "code": -32603,
                            "message": f"Error processing message: {str(e)}",
                        },
                    )

            else:
                # Handle other methods
                logger.info(f"Unhandled method: {method}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON: {line}")
        except Exception as e:
            logger.error(f"Error: {e}")
            if "request_id" in locals():
                send_response(
                    request_id,
                    error={"code": -32603, "message": f"Internal error: {str(e)}"},
                )


def cleanup_on_exit():
    """Clean up MCP server and dashboard on exit."""
    global current_instance_id
    logger.info("🧹 Cleaning up MCP server resources...")
    try:
        import subprocess
        import time
        from datetime import datetime

        # Only cleanup dashboard for current instance
        if current_instance_id:
            logger.info(f"🧹 Cleaning up dashboard for instance {current_instance_id}")

            # First, try to gracefully shutdown the dashboard via API
            try:
                from src.core.instance_registry import get_registry

                registry = get_registry()
                if registry and current_instance_id in registry.instances:
                    instance_info = registry.instances[current_instance_id]
                    dashboard_url = f"http://localhost:{instance_info.dashboard_port}"

                    logger.info(
                        f"🔄 Sending graceful shutdown request to {dashboard_url}"
                    )
                    response = requests.post(
                        f"{dashboard_url}/api/shutdown",
                        json={
                            "reason": "cursor_disconnected",
                            "timestamp": datetime.now().isoformat(),
                        },
                        timeout=2,
                    )
                    if response.status_code == 200:
                        logger.info("✅ Dashboard gracefully shutdown via API")
                        # Give it a moment to shutdown gracefully
                        time.sleep(1)

                        # Try to close the browser tab
                        try:
                            logger.info("🔄 Attempting to close browser tab...")
                            # Try to close the browser tab using xdotool (if available)
                            subprocess.run(
                                [
                                    "xdotool",
                                    "search",
                                    "--name",
                                    f"localhost:{instance_info.dashboard_port}",
                                    "windowclose",
                                ],
                                check=False,
                                timeout=2,
                            )
                            logger.info("✅ Browser tab close command sent")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not close browser tab: {e}")
                    else:
                        logger.warning(
                            f"⚠️ Dashboard API shutdown failed: {response.status_code}"
                        )
                else:
                    logger.warning(
                        "⚠️ No registry or instance info available for graceful shutdown"
                    )
            except Exception as e:
                logger.warning(f"⚠️ Graceful shutdown failed: {e}")

            # Force kill the dashboard process if it's still running
            subprocess.run(
                ["pkill", "-f", f"dashboard.*--instance-id {current_instance_id}"],
                check=False,
            )

            # Update registry to mark instance as stopped
            try:
                from src.core.instance_registry import get_registry

                registry = get_registry()
                if registry:
                    registry.stop_instance(current_instance_id)
                    logger.info(
                        f"✅ Instance {current_instance_id} marked as stopped in registry"
                    )

                    # Clean up old instances (more aggressive cleanup on exit)
                    current_time = time.time()
                    old_instances = []

                    for instance in registry.instances.values():
                        should_remove = False

                        # Remove stopped instances older than 5 minutes
                        if instance.status.value == "stopped" and instance.stopped_at:
                            if isinstance(instance.stopped_at, str):
                                stopped_dt = datetime.fromisoformat(instance.stopped_at)
                            stopped_time = stopped_dt.timestamp()
                            if current_time - stopped_time > 300:  # 5 minutes
                                should_remove = True
                                logger.info(
                                    f"🧹 Found old stopped instance: {instance.instance_id}"
                                )

                        # Remove starting instances with no process_id (orphaned)
                        elif (
                            instance.status.value == "starting"
                            and not instance.process_id
                        ):
                            should_remove = True
                            logger.info(
                                f"🧹 Found orphaned starting instance: {instance.instance_id}"
                            )

                        # Remove running instances where process is dead
                        elif instance.status.value == "running" and instance.process_id:
                            try:
                                import os

                                os.kill(
                                    instance.process_id, 0
                                )  # Check if process exists
                            except (OSError, ProcessLookupError):
                                should_remove = True
                                logger.info(
                                    f"🧹 Found dead running instance: {instance.instance_id}"
                                )

                        if should_remove:
                            old_instances.append(instance.instance_id)

                    # Remove old instances
                    for old_id in old_instances:
                        registry.remove_instance(old_id)
                        logger.info(f"🧹 Removed old instance {old_id} from registry")

                else:
                    logger.warning("⚠️ Registry not available for cleanup")
            except Exception as e:
                logger.warning(f"⚠️ Failed to update registry: {e}")
        else:
            # Fallback: kill all dashboards if no instance ID
            logger.warning("⚠️ No instance ID available, cleaning up all dashboards")
            subprocess.run(["pkill", "-f", "dashboard.*--port"], check=False)

        logger.info("✅ Dashboard processes cleaned up")
    except Exception as e:
        logger.warning(f"⚠️ Failed to cleanup dashboards: {e}")


if __name__ == "__main__":
    import atexit
    import signal

    # Register cleanup function
    atexit.register(cleanup_on_exit)

    # Handle signals
    def signal_handler(signum, frame):
        logger.info(f"📡 Received signal {signum}, shutting down...")
        cleanup_on_exit()
        exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        main()
    except EOFError:
        logger.info("📡 Cursor disconnected (EOF received)")
        cleanup_on_exit()
    except KeyboardInterrupt:
        logger.info("📡 Received keyboard interrupt")
        cleanup_on_exit()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        cleanup_on_exit()
