"""Memory-Enhanced Coordinator Agent with Qdrant Integration for Intelligent PDCA Workflows."""

import logging
import asyncio
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field

from .coordinator_agent import CoordinatorAgent, ProjectPlan
from .pdca_framework import PDCAFramework, PDCACycle, PDCAPhase
from ...database.enhanced_vector_store import get_enhanced_vector_store
from ...knowledge.predetermined_knowledge import get_predetermined_knowledge
from ...llm.llm_gateway import llm_gateway

logger = logging.getLogger(__name__)


@dataclass
class MemoryContext:
    """Context retrieved from Qdrant memory for decision making."""

    similar_projects: List[Dict[str, Any]] = field(default_factory=list)
    relevant_knowledge: List[Dict[str, Any]] = field(default_factory=list)
    agent_experiences: List[Dict[str, Any]] = field(default_factory=list)
    success_patterns: List[Dict[str, Any]] = field(default_factory=list)
    lessons_learned: List[Dict[str, Any]] = field(default_factory=list)
    risk_patterns: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ConversationMemory:
    """Stores conversation context in Qdrant for continuity."""

    session_id: str
    user_message: str
    coordinator_response: str
    pdca_phase: str
    project_context: Dict[str, Any]
    decisions_made: List[str]
    next_actions: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class LLMToolSuggestion:
    """LLM-suggested tool calls and responses."""

    response: str
    suggested_tools: List[Dict[str, Any]] = field(default_factory=list)
    next_phase: str = "continue"
    confidence: float = 0.8
    reasoning: str = ""


class MemoryEnhancedCoordinator(CoordinatorAgent):
    """Coordinator Agent enhanced with Qdrant memory for intelligent workflows."""

    def __init__(
        self,
        agent_id: str = "memory_coordinator_001",
        name: str = "Memory-Enhanced Coordinator",
    ):
        """Initialize the memory-enhanced coordinator."""
        super().__init__(agent_id, name)

        # Memory components
        self.vector_store = get_enhanced_vector_store()
        self.knowledge_base = get_predetermined_knowledge()

        # Conversation management
        self.current_session_id = None
        self.conversation_history: List[ConversationMemory] = []
        self.memory_context_cache: Dict[str, MemoryContext] = {}

        # Memory-driven decision making
        self.decision_confidence_threshold = 0.7
        self.memory_search_limit = 10

        logger.info(
            f"Memory-Enhanced Coordinator {name} initialized with Qdrant integration"
        )

    def _create_basic_collections(self) -> None:
        """Create basic collections needed for the coordinator."""
        try:
            # Set current project to general for basic collections
            current_project = self.vector_store.current_project_id
            self.vector_store.set_current_project("coordinator_system")

            # Create basic collections
            collections = ["conversations", "knowledge", "agents"]
            for collection in collections:
                try:
                    self.vector_store.create_collection(collection, vector_size=384)
                    logger.info(f"Created collection: {collection}")
                except Exception as e:
                    logger.warning(f"Collection {collection} might already exist: {e}")

            # Restore previous project context
            if current_project:
                self.vector_store.set_current_project(current_project)

        except Exception as e:
            logger.error(f"Error creating basic collections: {e}")

    async def initialize(self) -> bool:
        """Initialize the memory-enhanced coordinator."""
        try:
            # Initialize base coordinator
            base_initialized = await super().initialize()
            if not base_initialized:
                return False

            # Initialize LLM interface if available (optional)
            # Note: LLM interface integration can be added later for enhanced reasoning
            logger.info("Memory-Enhanced Coordinator ready without LLM interface")

            # Initialize current session
            self.current_session_id = str(uuid.uuid4())

            # Create basic collections for conversations and knowledge
            self._create_basic_collections()

            # Create or ensure knowledge is loaded in vector store
            await self._initialize_knowledge_in_vector_store()

            logger.info("Memory-Enhanced Coordinator initialization completed")
            return True

        except Exception as e:
            logger.error(f"Memory-Enhanced Coordinator initialization failed: {e}")
            return False

    async def _initialize_knowledge_in_vector_store(self) -> None:
        """Initialize predetermined knowledge in vector store for semantic search."""
        try:
            # Set a general knowledge project context
            self.vector_store.set_current_project("general_knowledge")

            # Create knowledge collection first
            collection_created = self.vector_store.create_collection(
                "knowledge", vector_size=384
            )
            if not collection_created:
                logger.warning(
                    "Knowledge collection already exists or failed to create"
                )

            # Get all knowledge domains
            all_knowledge = self.knowledge_base.get_all_knowledge()

            for domain, knowledge_items in all_knowledge.items():
                for item in knowledge_items:
                    # Create embedding for knowledge content
                    content = f"{item.title}. {item.content}"

                    # Generate a simple embedding (in real implementation, use actual embedding model)
                    embedding = await self._generate_embedding(content)

                    # Store in vector database
                    success = self.vector_store.upsert_knowledge(
                        knowledge_id=f"{domain}_{item.title.replace(' ', '_').lower()}",
                        content=content,
                        embedding=embedding,
                        metadata={
                            "domain": domain,
                            "category": item.category,
                            "subcategory": item.subcategory,
                            "priority": item.priority,
                            "tags": item.tags,
                            "source": item.source,
                            "version": item.version,
                            "last_updated": item.last_updated,
                        },
                    )

                    if not success:
                        logger.warning(f"Failed to store knowledge item: {item.title}")

            logger.info(
                f"Initialized {sum(len(items) for items in all_knowledge.values())} knowledge items in vector store"
            )

        except Exception as e:
            logger.error(f"Failed to initialize knowledge in vector store: {e}")
            # Continue anyway - the system can work without pre-loaded knowledge

    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text (placeholder - use actual embedding model in production)."""
        # This is a placeholder - in production, use actual embedding models like OpenAI, Sentence Transformers, etc.
        import hashlib
        import struct

        # Create a deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).digest()
        embedding = []

        for i in range(0, len(text_hash), 4):
            chunk = text_hash[i : i + 4]
            if len(chunk) == 4:
                val = struct.unpack("f", chunk)[0]
                embedding.append(val)

        # Pad to standard embedding size (384 dimensions)
        while len(embedding) < 384:
            embedding.append(0.0)

        return embedding[:384]

    async def start_intelligent_conversation(self, user_message: str) -> Dict[str, Any]:
        """Start an intelligent conversation with memory-driven context."""
        try:
            # Load previous conversation history from vector store if available
            await self._load_conversation_history()

            # Generate embedding for user message
            message_embedding = await self._generate_embedding(user_message)

            # Search memory for relevant context (now includes conversation history)
            memory_context = await self._search_memory_context(
                user_message, message_embedding
            )

            # Enhance memory context with recent conversation history
            memory_context = await self._enhance_context_with_conversation_history(
                memory_context, user_message
            )

            # Analyze user intent with enhanced memory context
            intent_analysis = await self._analyze_user_intent(
                user_message, memory_context
            )

            # Generate intelligent response
            response = await self._generate_intelligent_response(
                user_message, intent_analysis, memory_context
            )

            # Store conversation in memory
            await self._store_conversation_memory(
                user_message, response, intent_analysis
            )

            return response

        except Exception as e:
            logger.error(f"Error in intelligent conversation: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request. Let me try a different approach.",
            }

    async def _search_memory_context(
        self, user_message: str, message_embedding: List[float]
    ) -> MemoryContext:
        """Search Qdrant memory for relevant context."""
        try:
            memory_context = MemoryContext()

            # Search for similar conversations
            similar_conversations = self.vector_store.search_conversations(
                message_embedding, limit=self.memory_search_limit
            )
            memory_context.similar_projects = similar_conversations

            # Search for relevant knowledge
            relevant_knowledge = self.vector_store.search_knowledge(
                message_embedding, limit=self.memory_search_limit
            )
            memory_context.relevant_knowledge = relevant_knowledge

            # Search for agent experiences (if any exist)
            try:
                agent_experiences = self.vector_store.search_points(
                    "agents", message_embedding, limit=5
                )
                memory_context.agent_experiences = agent_experiences
            except Exception:
                # Agents collection might not exist yet
                memory_context.agent_experiences = []

            # Extract success patterns from similar projects
            memory_context.success_patterns = [
                conv
                for conv in similar_conversations
                if conv.get("payload", {}).get("success", False)
            ]

            # Extract lessons learned
            memory_context.lessons_learned = [
                conv
                for conv in similar_conversations
                if "lesson" in conv.get("payload", {}).get("message", "").lower()
            ]

            logger.info(
                f"Retrieved memory context: {len(similar_conversations)} conversations, {len(relevant_knowledge)} knowledge items"
            )
            return memory_context

        except Exception as e:
            logger.error(f"Error searching memory context: {e}")
            return MemoryContext()

    async def _analyze_user_intent(
        self, user_message: str, memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Analyze user intent with memory context and conversation history."""
        try:
            message_lower = user_message.lower()

            # Get conversation context for better intent detection
            conversation_context = self._get_conversation_context()
            last_phase = conversation_context.get("last_phase", "unknown")

            # Check if this appears to be a continuation response
            is_continuation = self._is_continuation_response(user_message, last_phase)

            # Detect specific option selections FIRST (most specific)
            if any(
                phrase in message_lower
                for phrase in [
                    "option 1",
                    "option 2",
                    "option 3",
                    "option 4",
                    "choose option",
                    "select option",
                    "i choose",
                ]
            ):
                return {
                    "intent": "option_selection",
                    "confidence": 0.95,
                    "selected_option": self._extract_option_number(user_message),
                    "conversation_context": conversation_context,
                }

            # Detect detailed planning requests (very specific)
            elif any(
                phrase in message_lower
                for phrase in [
                    "detailed planning",
                    "planning questions",
                    "pdca planning",
                    "ask me questions",
                    "specific questions",
                ]
            ):
                return {
                    "intent": "detailed_planning",
                    "confidence": 0.95,
                    "planning_type": "pdca",
                    "project_context": memory_context,
                }

            # Detect requirements gathering requests (specific)
            elif any(
                phrase in message_lower
                for phrase in [
                    "requirements",
                    "gathering requirements",
                    "analyze requirements",
                    "project requirements",
                    "functional requirements",
                ]
            ):
                return {
                    "intent": "requirements_gathering",
                    "confidence": 0.9,
                    "gathering_focus": "project_requirements",
                }

            # Detect agent creation intent (specific phrases)
            elif any(
                phrase in message_lower
                for phrase in [
                    "create agents",
                    "agent team",
                    "specialized agents",
                    "build team",
                    "team building",
                ]
            ):
                return {
                    "intent": "create_agents",
                    "confidence": 0.95,
                    "suggested_agents": await self._suggest_optimal_agents(
                        memory_context
                    ),
                }

            # Detect project creation intent (broader patterns)
            elif any(
                phrase in message_lower
                for phrase in [
                    "start project",
                    "create project",
                    "build project",
                    "develop project",
                    "new project",
                ]
            ):
                project_type = await self._detect_project_type(
                    user_message, memory_context
                )
                return {
                    "intent": "create_project",
                    "project_type": project_type,
                    "confidence": 0.9,
                    "suggested_approach": await self._suggest_project_approach(
                        project_type, memory_context
                    ),
                }

            # Detect information seeking (very broad patterns)
            elif any(
                word in message_lower
                for word in ["how", "what", "why", "explain", "help"]
            ):
                return {
                    "intent": "information_seeking",
                    "confidence": 0.8,
                    "relevant_knowledge": memory_context.relevant_knowledge[:3],
                }

            # Detect continuation of existing conversation (enhanced)
            elif is_continuation:
                return {
                    "intent": "continue_conversation",
                    "confidence": 0.9,  # Higher confidence for detected continuations
                    "context": conversation_context,
                    "continuation_type": "detailed_response",
                    "previous_phase": last_phase,
                }

            # Detect continuation of existing conversation (basic)
            elif len(self.conversation_history) > 0:
                return {
                    "intent": "continue_conversation",
                    "confidence": 0.7,
                    "context": conversation_context,
                    "continuation_type": "follow_up",
                    "previous_phase": last_phase,
                }

            else:
                return {
                    "intent": "general_inquiry",
                    "confidence": 0.5,
                    "suggested_actions": [
                        "project_planning",
                        "system_overview",
                        "capability_explanation",
                    ],
                }

        except Exception as e:
            logger.error(f"Error analyzing user intent: {e}")
            return {"intent": "unknown", "confidence": 0.0, "error": str(e)}

    def _extract_option_number(self, user_message: str) -> str:
        """Extract option number from user message."""
        message_lower = user_message.lower()

        if (
            "option 1" in message_lower
            or "detailed pdca" in message_lower
            or "start detailed" in message_lower
        ):
            return "1"
        elif (
            "option 2" in message_lower
            or "create agent" in message_lower
            or "agent team" in message_lower
        ):
            return "2"
        elif (
            "option 3" in message_lower
            or "analyze requirements" in message_lower
            or "specific requirements" in message_lower
        ):
            return "3"
        elif (
            "option 4" in message_lower
            or "show insights" in message_lower
            or "similar projects" in message_lower
        ):
            return "4"
        else:
            return "unknown"

    def _get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context from history."""
        if not self.conversation_history:
            return {"last_phase": "unknown", "conversation_count": 0}

        last_conversation = self.conversation_history[-1]

        return {
            "last_phase": last_conversation.pdca_phase,
            "conversation_count": len(self.conversation_history),
            "last_user_message": last_conversation.user_message,
            "last_coordinator_response": last_conversation.coordinator_response[:200],
            "project_context": last_conversation.project_context,
            "next_actions": last_conversation.next_actions,
            "session_id": self.current_session_id,
        }

    def _is_continuation_response(self, user_message: str, last_phase: str) -> bool:
        """Determine if user message is a continuation of previous conversation."""
        message_lower = user_message.lower()

        # Explicit continuation phrases
        explicit_continuation = [
            "building on our previous conversation",
            "based on our previous discussion",
            "here are the detailed answers",
            "to answer your questions",
            "following up on",
            "continuing from",
            "as discussed",
        ]

        # Strong indicators of detailed responses by phase
        detailed_response_indicators = {
            "plan": [
                "primary goal",
                "target audience",
                "specific problems",
                "vue 3",
                "task management",
            ],
            "detailed_planning": [
                "timeline",
                "3 months",
                "mvp",
                "team",
                "developers",
                "budget",
                "resources",
            ],
            "resource_assessment": [
                "hosting",
                "aws",
                "postgresql",
                "database",
                "concurrent users",
                "infrastructure",
            ],
            "requirements_gathering": [
                "functional requirements",
                "user authentication",
                "performance",
                "scalability",
            ],
        }

        # Check for explicit continuation phrases (highest confidence)
        if any(phrase in message_lower for phrase in explicit_continuation):
            return True

        # Check for detailed responses appropriate to current phase
        phase_indicators = detailed_response_indicators.get(last_phase, [])
        has_phase_specific_content = any(
            indicator in message_lower for indicator in phase_indicators
        )

        # Check if message contains substantial detailed content
        has_detailed_content = len(user_message.split()) > 15
        word_count = len(user_message.split())

        # Strong continuation indicators
        strong_indicators = [
            "primary goal",
            "target audience",
            "timeline",
            "team",
            "budget",
            "success criteria",
            "kpis",
            "requirements",
            "infrastructure",
        ]
        has_strong_indicators = any(
            indicator in message_lower for indicator in strong_indicators
        )

        # If last phase was asking for details and user provides comprehensive response
        asking_phases = [
            "plan",
            "detailed_planning",
            "resource_assessment",
            "requirements_gathering",
            "option_selected",
        ]

        return (
            last_phase in asking_phases
            and (
                (has_detailed_content and has_strong_indicators)
                or (word_count > 20 and has_phase_specific_content)
                or has_phase_specific_content
            )
            and
            # Exclude obvious new requests
            not any(
                phrase in message_lower
                for phrase in [
                    "new project",
                    "start over",
                    "different project",
                    "help me with",
                ]
            )
        )

    async def _detect_project_type(
        self, user_message: str, memory_context: MemoryContext
    ) -> str:
        """Detect project type from user message and memory context."""
        message_lower = user_message.lower()

        # Technology-based detection
        if any(
            tech in message_lower for tech in ["react", "vue", "angular", "frontend"]
        ):
            return "frontend_web_application"
        elif any(
            tech in message_lower
            for tech in ["api", "backend", "server", "nodejs", "express"]
        ):
            return "backend_api"
        elif any(
            tech in message_lower for tech in ["dashboard", "admin", "management"]
        ):
            return "management_dashboard"
        elif any(tech in message_lower for tech in ["mobile", "ios", "android"]):
            return "mobile_application"
        elif any(tech in message_lower for tech in ["data", "analytics", "ml", "ai"]):
            return "data_science_project"

        # Use memory context to suggest similar project types
        if memory_context.similar_projects:
            most_common_type = (
                memory_context.similar_projects[0]
                .get("payload", {})
                .get("project_type", "web_application")
            )
            return most_common_type

        return "web_application"  # Default

    async def _suggest_project_approach(
        self, project_type: str, memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Suggest project approach based on type and memory context."""
        try:
            # Base approach for different project types
            approaches = {
                "frontend_web_application": {
                    "methodology": "Component-driven development with modern frameworks",
                    "key_phases": [
                        "UI/UX Planning",
                        "Component Architecture",
                        "Implementation",
                        "Testing",
                    ],
                    "recommended_agents": [
                        "Frontend Agent",
                        "UI/UX Agent",
                        "Testing Agent",
                    ],
                    "technologies": ["Vue.js", "React", "TypeScript", "CSS Framework"],
                },
                "backend_api": {
                    "methodology": "API-first development with microservices architecture",
                    "key_phases": [
                        "API Design",
                        "Database Schema",
                        "Implementation",
                        "Testing",
                    ],
                    "recommended_agents": [
                        "Backend Agent",
                        "Database Agent",
                        "API Agent",
                        "Testing Agent",
                    ],
                    "technologies": [
                        "Node.js",
                        "Express",
                        "Database",
                        "Authentication",
                    ],
                },
                "management_dashboard": {
                    "methodology": "Data-driven dashboard development",
                    "key_phases": [
                        "Requirements Analysis",
                        "Data Architecture",
                        "Dashboard Design",
                        "Implementation",
                    ],
                    "recommended_agents": [
                        "Frontend Agent",
                        "Backend Agent",
                        "Data Agent",
                        "Testing Agent",
                    ],
                    "technologies": [
                        "Vue.js",
                        "Charts Library",
                        "REST API",
                        "Database",
                    ],
                },
            }

            base_approach = approaches.get(
                project_type, approaches["frontend_web_application"]
            )

            # Enhance with memory context insights
            if memory_context.success_patterns:
                successful_technologies = []
                for pattern in memory_context.success_patterns:
                    tech_used = pattern.get("payload", {}).get("technologies", [])
                    successful_technologies.extend(tech_used)

                if successful_technologies:
                    base_approach["proven_technologies"] = list(
                        set(successful_technologies)
                    )

            # Add lessons learned
            if memory_context.lessons_learned:
                base_approach["lessons_learned"] = [
                    lesson.get("payload", {}).get("lesson", "")
                    for lesson in memory_context.lessons_learned[:3]
                ]

            return base_approach

        except Exception as e:
            logger.error(f"Error suggesting project approach: {e}")
            return {"methodology": "Agile development with PDCA cycles"}

    async def _suggest_optimal_agents(
        self, memory_context: MemoryContext
    ) -> List[Dict[str, Any]]:
        """Suggest optimal agent team based on memory context."""
        try:
            # Base agent suggestions
            base_agents = [
                {
                    "type": "agile",
                    "name": "Agile/Scrum Agent",
                    "description": "Sprint planning, user stories, retrospectives",
                    "priority": "high",
                },
                {
                    "type": "frontend",
                    "name": "Frontend Agent",
                    "description": "UI/UX development, component architecture",
                    "priority": "high",
                },
                {
                    "type": "backend",
                    "name": "Backend Agent",
                    "description": "API development, database design",
                    "priority": "high",
                },
                {
                    "type": "testing",
                    "name": "Testing Agent",
                    "description": "Test strategies, automation, quality assurance",
                    "priority": "high",
                },
            ]

            # Add specialized agents based on memory context
            if memory_context.agent_experiences:
                # Analyze which agents were successful in similar projects
                successful_agent_types = set()
                for exp in memory_context.agent_experiences:
                    agent_type = exp.get("payload", {}).get("agent_type", "")
                    success_rate = exp.get("payload", {}).get("success_rate", 0)
                    if success_rate > 0.8:  # High success rate
                        successful_agent_types.add(agent_type)

                # Add specialized agents that were successful
                specialized_agents = [
                    {
                        "type": "git",
                        "name": "Git Management Agent",
                        "description": "Branch management, commit strategies, CI/CD",
                        "priority": "medium",
                    },
                    {
                        "type": "security",
                        "name": "Security Agent",
                        "description": "Security reviews, vulnerability scanning",
                        "priority": "medium",
                    },
                    {
                        "type": "documentation",
                        "name": "Documentation Agent",
                        "description": "Technical documentation, API docs",
                        "priority": "medium",
                    },
                ]

                for agent in specialized_agents:
                    if agent["type"] in successful_agent_types:
                        agent["priority"] = "high"
                        agent["reason"] = "Proven successful in similar projects"
                        base_agents.append(agent)

            return base_agents

        except Exception as e:
            logger.error(f"Error suggesting optimal agents: {e}")
            return base_agents[:4]  # Return base agents if error

    async def _generate_intelligent_response(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any],
        memory_context: MemoryContext,
    ) -> Dict[str, Any]:
        """Generate intelligent response using intent analysis and memory context."""
        try:
            intent = intent_analysis.get("intent", "unknown")
            confidence = intent_analysis.get("confidence", 0.0)

            if (
                intent == "create_project"
                and confidence > self.decision_confidence_threshold
            ):
                return await self._generate_project_creation_response(
                    intent_analysis, memory_context
                )

            elif (
                intent == "create_agents"
                and confidence > self.decision_confidence_threshold
            ):
                return await self._generate_agent_creation_response(
                    intent_analysis, memory_context
                )

            elif intent == "information_seeking":
                return await self._generate_information_response(
                    intent_analysis, memory_context
                )

            elif intent == "continue_conversation":
                return await self._generate_continuation_response(
                    intent_analysis, memory_context
                )

            elif intent == "detailed_planning":
                return await self._generate_detailed_planning_response(
                    intent_analysis, memory_context
                )

            elif intent == "requirements_gathering":
                return await self._generate_requirements_gathering_response(
                    intent_analysis, memory_context
                )

            elif intent == "option_selection":
                return await self._generate_option_selection_response(
                    intent_analysis, memory_context
                )

            else:
                return await self._generate_general_response(
                    user_message, memory_context
                )

        except Exception as e:
            logger.error(f"Error generating intelligent response: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while generating a response.",
            }

    async def _generate_project_creation_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate intelligent project creation response."""
        project_type = intent_analysis.get("project_type", "web_application")
        suggested_approach = intent_analysis.get("suggested_approach", {})

        response = f"""🎯 **Intelligent Project Planning with Memory-Driven Insights**

Based on my analysis of your request and similar successful projects in my memory:

**📊 Project Type Detected:** {project_type.replace('_', ' ').title()}

**🧠 Memory Insights:**"""

        if memory_context.similar_projects:
            response += f"""
- Found {len(memory_context.similar_projects)} similar projects in memory
- Success rate for this project type: {self._calculate_success_rate(memory_context.similar_projects):.1%}"""

        if memory_context.success_patterns:
            response += f"""
- {len(memory_context.success_patterns)} proven successful patterns identified"""

        response += f"""

**🚀 Recommended Approach:**
- **Methodology:** {suggested_approach.get('methodology', 'Agile development with PDCA cycles')}
- **Key Phases:** {', '.join(suggested_approach.get('key_phases', ['Planning', 'Development', 'Testing', 'Deployment']))}"""

        if suggested_approach.get("proven_technologies"):
            response += f"""
- **Proven Technologies:** {', '.join(suggested_approach['proven_technologies'][:5])}"""

        if suggested_approach.get("lessons_learned"):
            response += f"""

**📚 Lessons from Similar Projects:**"""
            for lesson in suggested_approach["lessons_learned"]:
                response += f"""
- {lesson}"""

        response += f"""

**🤖 Recommended Agent Team:**"""

        optimal_agents = await self._suggest_optimal_agents(memory_context)
        for agent in optimal_agents[:4]:  # Show top 4 agents
            priority_icon = "🔥" if agent["priority"] == "high" else "📋"
            response += f"""
{priority_icon} **{agent['name']}**: {agent['description']}"""

        response += f"""

**✅ Ready to proceed with PDCA planning!**

Would you like me to:
1. Start detailed PDCA planning for this project type?
2. Create the recommended agent team?
3. Analyze specific requirements in more detail?
4. Show more insights from similar projects?"""

        return {
            "success": True,
            "response": response,
            "phase": "plan",
            "next_steps": "detailed_pdca_planning",
            "project_type": project_type,
            "memory_insights": {
                "similar_projects_count": len(memory_context.similar_projects),
                "success_patterns_count": len(memory_context.success_patterns),
                "relevant_knowledge_count": len(memory_context.relevant_knowledge),
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_agent_creation_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate intelligent agent creation response."""
        optimal_agents = intent_analysis.get("suggested_agents", [])

        response = """🤖 **Creating Intelligent Agent Team with Memory Insights**

Based on successful patterns from previous projects, I'm creating an optimized agent team:

**✅ Core Agents Created:**"""

        agents_created = []
        for agent_config in optimal_agents[:4]:  # Create top 4 agents
            agent_result = await self.create_agent(
                agent_type=agent_config["type"],
                name=agent_config["name"],
                description=agent_config["description"],
                capabilities=agent_config.get("capabilities", []),
            )

            if agent_result.get("success"):
                agents_created.append(agent_result["agent_info"])
                priority_icon = "🔥" if agent_config["priority"] == "high" else "📋"
                response += f"""
{priority_icon} **{agent_config['name']}** - {agent_config['description']}"""

                if agent_config.get("reason"):
                    response += f" ({agent_config['reason']})"

        if memory_context.agent_experiences:
            response += f"""

**🧠 Memory-Driven Optimizations:**
- Analyzed {len(memory_context.agent_experiences)} previous agent experiences
- Selected agents with proven track records in similar projects
- Optimized team composition based on historical success patterns"""

        response += f"""

**🚀 Agent Team Status:**
- **Total Agents Created:** {len(agents_created)}
- **Team Readiness:** 100%
- **Collaboration Mode:** AutoGen-enabled for seamless communication

**📋 Next Steps:**
1. **Sprint Planning**: Agile Agent ready to create project roadmap
2. **Architecture Design**: Technical agents ready for system design
3. **Implementation Strategy**: Development agents ready for coding
4. **Quality Assurance**: Testing agent ready for QA framework

The agent team is now active and ready for collaborative project development!

What would you like the team to start working on first?"""

        return {
            "success": True,
            "response": response,
            "phase": "do",
            "next_steps": "agent_collaboration",
            "agents_created": len(agents_created),
            "agent_details": agents_created,
            "memory_optimizations": {
                "experiences_analyzed": len(memory_context.agent_experiences),
                "success_patterns_applied": len(memory_context.success_patterns),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def _calculate_success_rate(self, projects: List[Dict[str, Any]]) -> float:
        """Calculate success rate from project history."""
        if not projects:
            return 0.0

        successful_projects = sum(
            1
            for project in projects
            if project.get("payload", {}).get("success", False)
        )

        return successful_projects / len(projects)

    async def _store_conversation_memory(
        self,
        user_message: str,
        response: Dict[str, Any],
        intent_analysis: Dict[str, Any],
    ) -> None:
        """Store conversation in Qdrant for future reference."""
        try:
            # Create conversation memory object
            session_id = (
                self.current_session_id or f"session_{int(datetime.now().timestamp())}"
            )
            conversation = ConversationMemory(
                session_id=session_id,
                user_message=user_message,
                coordinator_response=response.get("response", ""),
                pdca_phase=response.get("phase", "unknown"),
                project_context=intent_analysis,
                decisions_made=response.get("decisions", []),
                next_actions=response.get("next_steps", []),
            )

            # Add to conversation history
            self.conversation_history.append(conversation)

            # Generate embedding for the conversation
            conversation_text = (
                f"User: {user_message} Coordinator: {conversation.coordinator_response}"
            )
            embedding = await self._generate_embedding(conversation_text)

            # Store in vector database
            self.vector_store.upsert_conversation(
                conversation_id=f"{self.current_session_id}_{len(self.conversation_history)}",
                message=user_message,
                response=conversation.coordinator_response,
                embedding=embedding,
                metadata={
                    "session_id": self.current_session_id,
                    "pdca_phase": conversation.pdca_phase,
                    "intent": intent_analysis.get("intent", "unknown"),
                    "confidence": intent_analysis.get("confidence", 0.0),
                    "project_type": intent_analysis.get("project_type", "unknown"),
                    "success": response.get("success", True),
                    "timestamp": conversation.timestamp.isoformat(),
                    "decisions_made": conversation.decisions_made,
                    "next_actions": conversation.next_actions,
                },
            )

            logger.info(
                f"Stored conversation memory for session {self.current_session_id}"
            )

        except Exception as e:
            logger.error(f"Error storing conversation memory: {e}")

    async def _generate_information_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate information response using relevant knowledge."""
        relevant_knowledge = intent_analysis.get("relevant_knowledge", [])

        if not relevant_knowledge:
            relevant_knowledge = memory_context.relevant_knowledge[:3]

        response = """📚 **Knowledge-Based Response**

Based on my knowledge base and previous experiences:

"""

        for i, knowledge in enumerate(relevant_knowledge, 1):
            payload = knowledge.get("payload", {})
            domain = payload.get("domain", "General")
            content = payload.get("content", "No content available")

            response += f"""**{i}. {domain.title()} Knowledge:**
{content[:200]}{'...' if len(content) > 200 else ''}

"""

        response += """Would you like me to provide more specific information about any of these topics?"""

        return {
            "success": True,
            "response": response,
            "phase": "information",
            "knowledge_sources": len(relevant_knowledge),
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_continuation_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate LLM-powered continuation response with tool orchestration."""
        try:
            # Use LLM to generate dynamic response with tool suggestions
            llm_suggestion = await self._generate_llm_response_with_tools(
                user_message=intent_analysis.get("user_message", ""),
                intent_analysis=intent_analysis,
                memory_context=memory_context,
            )

            # Execute suggested tools automatically
            tool_results = []
            if llm_suggestion.suggested_tools:
                tool_results = await self._execute_suggested_tools(
                    llm_suggestion.suggested_tools,
                    context={
                        "session_id": self.current_session_id,
                        "intent": intent_analysis,
                    },
                )

            # Build response with tool execution results
            response = llm_suggestion.response

            if tool_results:
                response += f"\n\n**🔧 Automated Actions Taken:**\n"
                for result in tool_results:
                    if result.get("status") == "simulated":
                        response += f"- {result['tool']}: {result.get('params', 'Ready to execute')}\n"

            return {
                "success": True,
                "response": response,
                "phase": llm_suggestion.next_phase,
                "suggested_tools": llm_suggestion.suggested_tools,
                "tool_results": tool_results,
                "llm_reasoning": llm_suggestion.reasoning,
                "next_steps": [
                    "continue_pdca_planning",
                    "tool_execution",
                    "user_feedback",
                ],
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in LLM continuation response: {e}")
            # Fallback to basic continuation
            context = intent_analysis.get("context", {})
            last_phase = context.get("last_phase", "continue")

            return {
                "success": True,
                "response": f"🔄 **Continuing from {last_phase.replace('_', ' ').title()}**\n\nLet me help you continue with your project planning. What would you like to focus on next?",
                "phase": last_phase,
                "next_steps": [
                    "detailed_planning",
                    "requirements_gathering",
                    "tool_execution",
                ],
                "timestamp": datetime.now().isoformat(),
            }

    async def _generate_general_response(
        self, user_message: str, memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate general response with memory insights."""
        response = """🤖 **Memory-Enhanced Coordinator Ready**

I'm your intelligent project coordinator with access to:
"""

        if memory_context.similar_projects:
            response += f"📊 {len(memory_context.similar_projects)} similar project experiences\n"

        if memory_context.relevant_knowledge:
            response += f"📚 {len(memory_context.relevant_knowledge)} relevant knowledge items\n"

        if memory_context.success_patterns:
            response += (
                f"✅ {len(memory_context.success_patterns)} proven success patterns\n"
            )

        response += f"""
**I can help you with:**
1. **Intelligent Project Planning** - Using PDCA methodology enhanced with memory insights
2. **Agent Team Creation** - Building optimal teams based on successful patterns
3. **Knowledge-Driven Decisions** - Leveraging curated expertise and past experiences
4. **Continuous Learning** - Every interaction improves future recommendations

What would you like to work on today?"""

        return {
            "success": True,
            "response": response,
            "phase": "ready",
            "capabilities": [
                "project_planning",
                "agent_coordination",
                "knowledge_access",
                "memory_insights",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_detailed_planning_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate response for detailed planning requests."""
        project_type = intent_analysis.get("project_type", "general")
        planning_phase = intent_analysis.get("planning_phase", "initial")

        response = f"""🎯 **Detailed PDCA Planning Session**

I'll help you create a comprehensive plan using the PDCA (Plan-Do-Check-Act) methodology enhanced with memory insights.

**Current Focus:** {project_type.replace('_', ' ').title()} - {planning_phase.replace('_', ' ').title()} Phase

Let me ask you some specific questions to create the most effective plan:

**🔍 PLAN Phase - Discovery Questions:**

1. **Project Scope & Objectives:**
   - What is the primary goal you want to achieve?
   - What specific problems are you trying to solve?
   - Who is the target audience or end user?

2. **Resources & Constraints:**
   - What timeline are you working with?
   - What resources (team, budget, tools) do you have available?
   - Are there any specific constraints or limitations I should know about?

3. **Success Criteria:**
   - How will you measure success?
   - What are the key performance indicators (KPIs)?
   - What would a successful outcome look like?

Please start by answering question 1 about your project scope and objectives. I'll use your answers to create a detailed, actionable plan with specific next steps."""

        if memory_context.similar_projects:
            response += f"""

**💡 Memory Insight:** I found {len(memory_context.similar_projects)} similar projects in my memory. Based on these patterns, I can provide specific recommendations tailored to your situation."""

        return {
            "success": True,
            "response": response,
            "phase": "detailed_planning",
            "next_steps": [
                "scope_definition",
                "resource_assessment",
                "success_criteria",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_requirements_gathering_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate response for requirements gathering."""
        requirement_type = intent_analysis.get("requirement_type", "functional")
        project_context = intent_analysis.get("project_context", {})

        response = f"""📋 **Requirements Gathering Session**

Let's systematically gather all the requirements for your project. I'll guide you through a structured approach to ensure we don't miss anything important.

**Current Focus:** {requirement_type.replace('_', ' ').title()} Requirements

**🔍 Requirement Categories to Explore:**

**1. Functional Requirements (What the system should do):**
   - Core features and functionality
   - User interactions and workflows
   - Data processing and storage needs
   - Integration requirements

**2. Non-Functional Requirements (How the system should perform):**
   - Performance expectations (speed, scalability)
   - Security and privacy requirements
   - Usability and user experience standards
   - Reliability and availability needs

**3. Technical Requirements:**
   - Technology stack preferences
   - Platform and deployment requirements
   - Third-party integrations
   - Development and testing environments

**Let's start with the most critical area:**

What are the **core features** your system absolutely must have? Please describe:
- The main functionality users will interact with
- Any critical business processes it needs to support
- Key workflows from user perspective

Please provide as much detail as possible for the core features."""

        if memory_context.success_patterns:
            response += f"""

**💡 Best Practice Insight:** Based on {len(memory_context.success_patterns)} successful patterns, I recommend prioritizing requirements by business value and technical feasibility."""

        return {
            "success": True,
            "response": response,
            "phase": "requirements_gathering",
            "next_steps": [
                "functional_requirements",
                "non_functional_requirements",
                "technical_requirements",
            ],
            "timestamp": datetime.now().isoformat(),
        }

    async def _generate_option_selection_response(
        self, intent_analysis: Dict[str, Any], memory_context: MemoryContext
    ) -> Dict[str, Any]:
        """Generate response for option selection."""
        selected_option = intent_analysis.get("selected_option")
        option_context = intent_analysis.get("option_context", {})

        if selected_option:
            response = f"""✅ **Option Selected: {selected_option}**

Excellent choice! Let me provide detailed guidance for this option.

**📋 Next Steps for "{selected_option}":**

Based on your selection, here's what we'll focus on:"""

            # Parse the option number to provide specific guidance
            if (
                "1" in str(selected_option)
                or "project planning" in str(selected_option).lower()
            ):
                response += """

**🎯 Project Planning Path:**
1. **Define Project Scope** - Clear objectives and boundaries
2. **Resource Assessment** - Team, timeline, and budget planning
3. **Risk Analysis** - Identify potential challenges and mitigation strategies
4. **Implementation Roadmap** - Phased approach with milestones

What type of project are you planning? This will help me provide more specific guidance."""

            elif "2" in str(selected_option) or "team" in str(selected_option).lower():
                response += """

**👥 Team Building Path:**
1. **Role Definition** - Identify required skills and responsibilities
2. **Agent Configuration** - Set up specialized AI agents for different tasks
3. **Communication Setup** - Establish collaboration workflows
4. **Performance Monitoring** - Track team effectiveness

What specific roles or skills do you need for your team?"""

            elif (
                "3" in str(selected_option)
                or "requirements" in str(selected_option).lower()
            ):
                response += """

**📝 Requirements Gathering Path:**
1. **Stakeholder Identification** - Who are the key decision makers?
2. **Functional Requirements** - What should the system do?
3. **Non-Functional Requirements** - Performance, security, usability
4. **Acceptance Criteria** - How will we know when it's done?

Let's start with identifying your key stakeholders. Who will be using this system?"""

            else:
                response += f"""

I'll help you with the specific aspects of "{selected_option}".

Could you provide more details about what you'd like to focus on? This will help me give you the most relevant and actionable guidance."""

        else:
            response = """🤔 **Option Selection Needed**

I notice you're trying to make a selection, but I'm not sure which option you're referring to.

Could you please:
1. Specify the option number (e.g., "Option 1", "Choice 2")
2. Or clearly state what you'd like to focus on

This will help me provide the most relevant guidance for your needs."""

        if memory_context.relevant_knowledge:
            response += f"""

**📚 Knowledge Base:** I have {len(memory_context.relevant_knowledge)} relevant resources to help guide this process."""

        return {
            "success": True,
            "response": response,
            "phase": "option_selected",
            "selected_option": selected_option,
            "next_steps": ["detailed_guidance", "action_planning"],
            "timestamp": datetime.now().isoformat(),
        }

    async def get_memory_insights(self, query: str = "") -> Dict[str, Any]:
        """Get insights from memory for debugging and analysis."""
        try:
            if query:
                query_embedding = await self._generate_embedding(query)
                memory_context = await self._search_memory_context(
                    query, query_embedding
                )
            else:
                memory_context = MemoryContext()

            # Get general statistics
            general_stats = self.vector_store.get_project_stats("general_knowledge")

            return {
                "success": True,
                "memory_stats": general_stats,
                "current_session": self.current_session_id,
                "conversation_count": len(self.conversation_history),
                "memory_context": {
                    "similar_projects": len(memory_context.similar_projects),
                    "relevant_knowledge": len(memory_context.relevant_knowledge),
                    "agent_experiences": len(memory_context.agent_experiences),
                    "success_patterns": len(memory_context.success_patterns),
                    "lessons_learned": len(memory_context.lessons_learned),
                },
                "knowledge_domains": self.knowledge_base.get_available_domains(),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting memory insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def _generate_llm_response_with_tools(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any],
        memory_context: MemoryContext,
    ) -> LLMToolSuggestion:
        """Generate dynamic LLM response with tool suggestions for intelligent orchestration."""
        try:
            conversation_summary = await self._build_conversation_summary()

            # Build comprehensive context for LLM
            context_prompt = self._build_llm_context_prompt(
                user_message, intent_analysis, memory_context, conversation_summary
            )

            # Generate LLM response with tool suggestions
            llm_response = await llm_gateway.generate_with_fallback(
                prompt=context_prompt,
                task_type="analysis",
                preferred_model="cursor-small",
            )

            # Parse LLM response for tool suggestions
            tool_suggestion = await self._parse_llm_tool_response(
                llm_response, intent_analysis
            )

            logger.info(
                f"LLM generated response with {len(tool_suggestion.suggested_tools)} tool suggestions"
            )
            return tool_suggestion

        except Exception as e:
            logger.error(f"Error generating LLM response with tools: {e}")
            # Fallback to basic response
            return LLMToolSuggestion(
                response="I understand your request. Let me help you with that.",
                suggested_tools=[],
                next_phase="continue",
                reasoning="Error fallback",
            )

    def _build_llm_context_prompt(
        self,
        user_message: str,
        intent_analysis: Dict[str, Any],
        memory_context: MemoryContext,
        conversation_summary: str,
    ) -> str:
        """Build comprehensive context prompt for LLM."""
        intent = intent_analysis.get("intent", "unknown")
        confidence = intent_analysis.get("confidence", 0.0)
        conversation_context = intent_analysis.get("conversation_context", {})

        prompt = f"""You are an intelligent PDCA (Plan-Do-Check-Act) project coordinator with tool orchestration capabilities.

CONVERSATION CONTEXT:
{conversation_summary}

CURRENT USER MESSAGE: "{user_message}"
DETECTED INTENT: {intent} (confidence: {confidence:.2f})

MEMORY INSIGHTS:
- Similar Projects: {len(memory_context.similar_projects)}
- Success Patterns: {len(memory_context.success_patterns)}
- Relevant Knowledge: {len(memory_context.relevant_knowledge)}

CURRENT PHASE: {conversation_context.get('last_phase', 'initial')}

TASK: Generate a natural, conversational response that:
1. Acknowledges the user's specific details (Vue 3, team size, timeline, etc.)
2. Provides actionable next steps in PDCA methodology
3. Suggests appropriate tools to execute automatically

AVAILABLE TOOLS:
- create_sprint: Create agile sprint for project
- create_user_story: Create user stories from requirements
- create_agents: Set up specialized agent team
- start_workflow: Begin AutoGen multi-agent collaboration
- create_agile_project: Initialize agile project structure
- plan_sprint: Plan sprint with story assignments

RESPONSE FORMAT:
RESPONSE: [Natural conversational response building on user's specific details]
TOOLS: [tool1:params, tool2:params] (if appropriate)
NEXT_PHASE: [next_pdca_phase]
REASONING: [Why these tools and next phase]

Generate a response that feels natural and builds on the conversation context:"""

        return prompt

    async def _parse_llm_tool_response(
        self, llm_response: str, intent_analysis: Dict[str, Any]
    ) -> LLMToolSuggestion:
        """Parse LLM response to extract response text and tool suggestions."""
        try:
            lines = llm_response.strip().split("\n")
            response_text = ""
            suggested_tools = []
            next_phase = "continue"
            reasoning = ""

            current_section = None

            for line in lines:
                line = line.strip()
                if line.startswith("RESPONSE:"):
                    current_section = "response"
                    response_text = line.replace("RESPONSE:", "").strip()
                elif line.startswith("TOOLS:"):
                    current_section = "tools"
                    tools_text = line.replace("TOOLS:", "").strip()
                    if tools_text and tools_text != "none":
                        # Parse tool suggestions
                        tool_parts = tools_text.split(",")
                        for tool_part in tool_parts:
                            tool_part = tool_part.strip()
                            if ":" in tool_part:
                                tool_name, params = tool_part.split(":", 1)
                                suggested_tools.append(
                                    {
                                        "tool": tool_name.strip(),
                                        "params": params.strip(),
                                    }
                                )
                            else:
                                suggested_tools.append(
                                    {"tool": tool_part, "params": ""}
                                )
                elif line.startswith("NEXT_PHASE:"):
                    current_section = "next_phase"
                    next_phase = line.replace("NEXT_PHASE:", "").strip()
                elif line.startswith("REASONING:"):
                    current_section = "reasoning"
                    reasoning = line.replace("REASONING:", "").strip()
                elif current_section == "response" and line:
                    response_text += " " + line
                elif current_section == "reasoning" and line:
                    reasoning += " " + line

            # Fallback if no structured response
            if not response_text:
                response_text = llm_response.strip()

            return LLMToolSuggestion(
                response=response_text,
                suggested_tools=suggested_tools,
                next_phase=next_phase,
                reasoning=reasoning,
            )

        except Exception as e:
            logger.error(f"Error parsing LLM tool response: {e}")
            return LLMToolSuggestion(
                response=llm_response.strip(),
                suggested_tools=[],
                next_phase="continue",
                reasoning="Parse error fallback",
            )

    async def _build_conversation_summary(self) -> str:
        """Build a summary of the conversation history for LLM context."""
        if not self.conversation_history:
            return "This is the start of a new conversation."

        summary_parts = []
        for i, conv in enumerate(
            self.conversation_history[-3:], 1
        ):  # Last 3 conversations
            summary_parts.append(f"{i}. User: {conv.user_message[:100]}...")
            summary_parts.append(
                f"   Coordinator: {conv.coordinator_response[:100]}..."
            )
            summary_parts.append(f"   Phase: {conv.pdca_phase}")

        return "\n".join(summary_parts)

    async def _execute_suggested_tools(
        self, suggested_tools: List[Dict[str, Any]], context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Execute tools suggested by LLM with AutoGen integration."""
        execution_results = []
        autogen_workflow_candidates = []

        for tool_spec in suggested_tools:
            tool_name = tool_spec.get("tool", "")
            tool_params = tool_spec.get("params", "")

            try:
                logger.info(
                    f"Executing suggested tool: {tool_name} with params: {tool_params}"
                )

                # Execute tool based on name (this would integrate with MCP tools)
                if tool_name == "create_sprint":
                    result = {
                        "tool": tool_name,
                        "status": "simulated",
                        "params": tool_params,
                    }
                    autogen_workflow_candidates.append(tool_name)
                elif tool_name == "create_user_story":
                    result = {
                        "tool": tool_name,
                        "status": "simulated",
                        "params": tool_params,
                    }
                    autogen_workflow_candidates.append(tool_name)
                elif tool_name == "create_agents":
                    result = {
                        "tool": tool_name,
                        "status": "simulated",
                        "params": tool_params,
                    }
                    autogen_workflow_candidates.append(tool_name)
                elif tool_name == "start_workflow":
                    result = {
                        "tool": tool_name,
                        "status": "simulated",
                        "params": tool_params,
                    }
                    autogen_workflow_candidates.append(tool_name)
                elif tool_name == "initiate_collaboration":
                    # Direct AutoGen workflow initiation
                    workflow_result = await self.initiate_autogen_workflow(
                        context.get("project_context", {}),
                        [t.get("tool", "") for t in suggested_tools],
                    )
                    result = {
                        "tool": tool_name,
                        "status": "executed",
                        "workflow": workflow_result,
                    }
                else:
                    result = {
                        "tool": tool_name,
                        "status": "unknown",
                        "params": tool_params,
                    }

                execution_results.append(result)

            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}")
                execution_results.append(
                    {
                        "tool": tool_name,
                        "status": "error",
                        "error": str(e),
                        "params": tool_params,
                    }
                )

        # Check if we should initiate AutoGen workflow based on executed tools
        if (
            len(autogen_workflow_candidates) >= 2
        ):  # Multiple collaborative tools suggest workflow readiness
            try:
                logger.info(
                    f"Multiple collaborative tools detected: {autogen_workflow_candidates}"
                )

                # Assess collaboration readiness
                bridge_result = await self.bridge_to_multi_agent_collaboration(
                    context, autogen_workflow_candidates
                )

                # Add workflow bridge result to execution results
                execution_results.append(
                    {
                        "tool": "autogen_workflow_bridge",
                        "status": "bridge_attempted",
                        "bridge_result": bridge_result,
                        "triggered_by": autogen_workflow_candidates,
                    }
                )

            except Exception as e:
                logger.error(f"Error bridging to AutoGen workflow: {e}")
                execution_results.append(
                    {
                        "tool": "autogen_workflow_bridge",
                        "status": "bridge_error",
                        "error": str(e),
                    }
                )

        return execution_results

    async def _load_conversation_history(self) -> None:
        """Load previous conversation history from vector store for context continuity."""
        try:
            if not self.current_session_id:
                logger.debug("No session ID available, starting fresh conversation")
                return

            # Search for previous conversations from this session
            search_results = self.vector_store.search_conversations_simple(
                query=f"session:{self.current_session_id}",
                limit=10,  # Load last 10 conversations for context
            )

            if search_results:
                logger.info(f"Found {len(search_results)} previous conversations")

                # Convert search results back to ConversationMemory objects
                loaded_conversations = []
                for result in search_results:
                    # Each result should be a dictionary with conversation data
                    if (
                        isinstance(result, dict)
                        and result.get("session_id") == self.current_session_id
                    ):
                        conversation = ConversationMemory(
                            session_id=result.get("session_id", ""),
                            user_message=result.get("user_message", ""),
                            coordinator_response=result.get("coordinator_response", ""),
                            pdca_phase=result.get("pdca_phase", "unknown"),
                            project_context=result.get("project_context", {}),
                            decisions_made=result.get("decisions_made", []),
                            next_actions=result.get("next_actions", []),
                            timestamp=result.get("timestamp", datetime.now()),
                        )
                        loaded_conversations.append(conversation)

                # Sort by timestamp and update conversation history
                loaded_conversations.sort(key=lambda x: x.timestamp)
                self.conversation_history = loaded_conversations

                logger.info(
                    f"Loaded {len(self.conversation_history)} previous conversations into context"
                )
            else:
                logger.debug("No previous conversations found for this session")

        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            # Continue without previous history rather than failing

    async def _enhance_context_with_conversation_history(
        self, memory_context: MemoryContext, current_message: str
    ) -> MemoryContext:
        """Enhance memory context with conversation history for better intent analysis."""
        try:
            if not self.conversation_history:
                return memory_context

            # Add conversation context to memory context
            conversation_context = []
            for conv in self.conversation_history[
                -3:
            ]:  # Use last 3 conversations for context
                conversation_context.append(
                    {
                        "user_message": conv.user_message,
                        "coordinator_response": conv.coordinator_response[
                            :200
                        ],  # Truncate for brevity
                        "phase": conv.pdca_phase,
                        "decisions": conv.decisions_made,
                        "next_actions": conv.next_actions,
                    }
                )

            # Create enhanced context
            enhanced_context = MemoryContext(
                similar_projects=memory_context.similar_projects,
                relevant_knowledge=memory_context.relevant_knowledge,
                agent_experiences=memory_context.agent_experiences,
                success_patterns=memory_context.success_patterns,
                lessons_learned=memory_context.lessons_learned,
                risk_patterns=memory_context.risk_patterns,
            )

            # Add conversation history as a special knowledge item
            if conversation_context:
                enhanced_context.relevant_knowledge.append(
                    {
                        "type": "conversation_history",
                        "content": f"Recent conversation context: {conversation_context}",
                        "phase_progression": [
                            conv.pdca_phase for conv in self.conversation_history
                        ],
                        "last_phase": (
                            self.conversation_history[-1].pdca_phase
                            if self.conversation_history
                            else "unknown"
                        ),
                    }
                )

            logger.debug(
                f"Enhanced context with {len(conversation_context)} recent conversations"
            )
            return enhanced_context

        except Exception as e:
            logger.error(f"Error enhancing context with conversation history: {e}")
            return memory_context

    async def initiate_autogen_workflow(
        self, project_context: Dict[str, Any], suggested_tools: List[str]
    ) -> Dict[str, Any]:
        """Initiate AutoGen multi-agent workflow based on LLM suggestions."""
        try:
            logger.info(
                f"Initiating AutoGen workflow for project: {project_context.get('project_type', 'unknown')}"
            )

            # Analyze project requirements to determine optimal agent team
            agent_team = self._determine_optimal_agent_team(
                project_context, suggested_tools
            )

            # Create workflow configuration
            workflow_config = self._create_workflow_configuration(
                project_context, agent_team
            )

            # Initialize AutoGen group chat or conversation
            workflow_result = await self._start_autogen_collaboration(workflow_config)

            return {
                "success": True,
                "workflow_id": workflow_result.get("workflow_id"),
                "agent_team": agent_team,
                "workflow_config": workflow_config,
                "status": "initiated",
                "next_actions": [
                    "agent_collaboration",
                    "progress_monitoring",
                    "outcome_integration",
                ],
            }

        except Exception as e:
            logger.error(f"Error initiating AutoGen workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback": "Manual tool execution recommended",
            }

    def _determine_optimal_agent_team(
        self, project_context: Dict[str, Any], suggested_tools: List[str]
    ) -> List[Dict[str, Any]]:
        """Determine optimal agent team based on project requirements."""
        project_type = project_context.get("project_type", "general")

        # Base agent configurations
        agent_templates = {
            "frontend_web_application": [
                {
                    "role": "coordinator",
                    "name": "ProjectManager",
                    "capabilities": ["planning", "coordination"],
                },
                {
                    "role": "developer",
                    "name": "FrontendDeveloper",
                    "capabilities": ["vue", "javascript", "ui"],
                },
                {
                    "role": "reviewer",
                    "name": "CodeReviewer",
                    "capabilities": ["quality_assurance", "security"],
                },
                {
                    "role": "tester",
                    "name": "TestEngineer",
                    "capabilities": ["testing", "validation"],
                },
            ],
            "data_science_project": [
                {
                    "role": "coordinator",
                    "name": "DataProjectManager",
                    "capabilities": ["planning", "data_strategy"],
                },
                {
                    "role": "developer",
                    "name": "DataScientist",
                    "capabilities": ["analysis", "modeling", "visualization"],
                },
                {
                    "role": "developer",
                    "name": "DataEngineer",
                    "capabilities": ["pipelines", "databases", "etl"],
                },
                {
                    "role": "reviewer",
                    "name": "DataReviewer",
                    "capabilities": ["validation", "accuracy"],
                },
            ],
            "management_dashboard": [
                {
                    "role": "coordinator",
                    "name": "DashboardManager",
                    "capabilities": ["planning", "requirements"],
                },
                {
                    "role": "developer",
                    "name": "FullStackDeveloper",
                    "capabilities": ["frontend", "backend", "api"],
                },
                {
                    "role": "developer",
                    "name": "DataVisualizationExpert",
                    "capabilities": ["charts", "dashboards", "ui"],
                },
                {
                    "role": "reviewer",
                    "name": "BusinessAnalyst",
                    "capabilities": ["requirements", "validation"],
                },
            ],
        }

        # Get base team or default
        team = agent_templates.get(
            project_type, agent_templates["frontend_web_application"]
        )

        # Enhance team based on suggested tools
        if "create_agile_project" in suggested_tools:
            team.append(
                {
                    "role": "tester",
                    "name": "ScrumMaster",
                    "capabilities": ["agile", "sprint_planning"],
                }
            )

        if "create_user_story" in suggested_tools:
            team.append(
                {
                    "role": "reviewer",
                    "name": "ProductOwner",
                    "capabilities": ["requirements", "user_stories"],
                }
            )

        return team

    def _create_workflow_configuration(
        self, project_context: Dict[str, Any], agent_team: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create AutoGen workflow configuration."""
        return {
            "workflow_type": "collaborative_planning",
            "project_context": project_context,
            "agent_team": agent_team,
            "communication_pattern": "group_chat",
            "termination_condition": "consensus_reached",
            "max_rounds": 10,
            "workflow_phases": ["planning", "execution", "review", "delivery"],
            "success_criteria": [
                "Project plan created",
                "Tasks distributed",
                "Initial implementation started",
                "Quality gates passed",
            ],
        }

    async def _start_autogen_collaboration(
        self, workflow_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start AutoGen multi-agent collaboration."""
        try:
            # For now, simulate AutoGen integration
            # In full implementation, this would initialize actual AutoGen group chat
            workflow_id = f"autogen_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            logger.info(f"Starting AutoGen workflow: {workflow_id}")

            # Simulate agent initialization
            agents = []
            for agent_config in workflow_config["agent_team"]:
                agents.append(
                    {
                        "id": f"{agent_config['name'].lower()}_{workflow_id}",
                        "role": agent_config["role"],
                        "name": agent_config["name"],
                        "capabilities": agent_config["capabilities"],
                        "status": "initialized",
                    }
                )

            return {
                "workflow_id": workflow_id,
                "agents": agents,
                "status": "started",
                "communication_channel": f"group_chat_{workflow_id}",
                "progress": "agent_initialization_complete",
            }

        except Exception as e:
            logger.error(f"Error starting AutoGen collaboration: {e}")
            raise

    async def bridge_to_multi_agent_collaboration(
        self, context: Dict[str, Any], suggested_actions: List[str]
    ) -> Dict[str, Any]:
        """Bridge individual planning to multi-agent collaborative execution."""
        try:
            logger.info("Bridging to multi-agent collaboration")

            # Prepare handoff context
            handoff_context = {
                "project_summary": context.get("project_context", {}),
                "individual_planning_results": {
                    "intent_analysis": context.get("intent_analysis", {}),
                    "suggested_tools": suggested_actions,
                    "memory_insights": context.get("memory_context", {}),
                    "coordinator_recommendations": context.get(
                        "coordinator_response", ""
                    ),
                },
                "collaboration_readiness": self._assess_collaboration_readiness(
                    context
                ),
                "recommended_workflow": "autogen_group_chat",
            }

            # Initiate AutoGen workflow if ready
            if handoff_context["collaboration_readiness"]["ready"]:
                workflow_result = await self.initiate_autogen_workflow(
                    handoff_context["project_summary"], suggested_actions
                )

                return {
                    "success": True,
                    "bridge_status": "collaboration_initiated",
                    "handoff_context": handoff_context,
                    "workflow_result": workflow_result,
                    "message": "Successfully transitioned from individual planning to multi-agent collaboration",
                }
            else:
                return {
                    "success": False,
                    "bridge_status": "collaboration_not_ready",
                    "handoff_context": handoff_context,
                    "required_actions": handoff_context["collaboration_readiness"][
                        "required_actions"
                    ],
                    "message": "Additional planning required before multi-agent collaboration",
                }

        except Exception as e:
            logger.error(f"Error bridging to multi-agent collaboration: {e}")
            return {"success": False, "error": str(e), "bridge_status": "bridge_failed"}

    def _assess_collaboration_readiness(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess if project is ready for multi-agent collaboration."""
        required_elements = [
            "project_type_identified",
            "basic_requirements_defined",
            "suggested_approach_available",
            "success_criteria_outlined",
        ]

        readiness_score = 0
        missing_elements = []

        # Check project context completeness
        project_context = context.get("project_context", {})
        if project_context.get("project_type"):
            readiness_score += 25
        else:
            missing_elements.append("project_type_identification")

        if project_context.get("suggested_approach"):
            readiness_score += 25
        else:
            missing_elements.append("project_approach_definition")

        # Check intent analysis quality
        intent_analysis = context.get("intent_analysis", {})
        if intent_analysis.get("confidence", 0) > 0.7:
            readiness_score += 25
        else:
            missing_elements.append("clear_user_intent")

        # Check suggested tools availability
        if context.get("suggested_tools") or context.get("suggested_actions"):
            readiness_score += 25
        else:
            missing_elements.append("actionable_next_steps")

        return {
            "ready": readiness_score >= 75,
            "readiness_score": readiness_score,
            "missing_elements": missing_elements,
            "required_actions": [
                f"Complete {elem.replace('_', ' ')}" for elem in missing_elements
            ],
        }


# Global instance for easy access
_memory_enhanced_coordinator = None


def get_memory_enhanced_coordinator() -> MemoryEnhancedCoordinator:
    """Get the global memory-enhanced coordinator instance."""
    global _memory_enhanced_coordinator
    if _memory_enhanced_coordinator is None:
        _memory_enhanced_coordinator = MemoryEnhancedCoordinator()
    return _memory_enhanced_coordinator
