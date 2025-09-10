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
            # Generate embedding for user message
            message_embedding = await self._generate_embedding(user_message)

            # Search memory for relevant context
            memory_context = await self._search_memory_context(
                user_message, message_embedding
            )

            # Analyze user intent with memory context
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
        """Analyze user intent with memory context."""
        try:
            message_lower = user_message.lower()

            # Detect project creation intent
            if any(
                word in message_lower
                for word in ["start", "create", "build", "develop", "new project"]
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

            # Detect agent creation intent
            elif any(
                phrase in message_lower
                for phrase in ["create agents", "agent team", "specialized agents"]
            ):
                return {
                    "intent": "create_agents",
                    "confidence": 0.95,
                    "suggested_agents": await self._suggest_optimal_agents(
                        memory_context
                    ),
                }

            # Detect information seeking
            elif any(
                word in message_lower
                for word in ["how", "what", "why", "explain", "help"]
            ):
                return {
                    "intent": "information_seeking",
                    "confidence": 0.8,
                    "relevant_knowledge": memory_context.relevant_knowledge[:3],
                }

            # Detect continuation of existing conversation
            elif len(self.conversation_history) > 0:
                return {
                    "intent": "continue_conversation",
                    "confidence": 0.7,
                    "context": self.conversation_history[-1],
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
            conversation = ConversationMemory(
                session_id=self.current_session_id,
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
        """Generate continuation response based on conversation context."""
        last_conversation = intent_analysis.get("context")

        if not last_conversation:
            return await self._generate_general_response("", memory_context)

        last_phase = last_conversation.pdca_phase
        next_actions = last_conversation.next_actions

        response = f"""🔄 **Continuing from {last_phase.upper()} Phase**

Based on our previous conversation, the next steps were:
"""

        for i, action in enumerate(next_actions, 1):
            response += f"{i}. {action}\n"

        response += f"""
Which of these would you like to proceed with, or do you have other priorities?"""

        return {
            "success": True,
            "response": response,
            "phase": last_phase,
            "next_steps": next_actions,
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


# Global instance for easy access
_memory_enhanced_coordinator = None


def get_memory_enhanced_coordinator() -> MemoryEnhancedCoordinator:
    """Get the global memory-enhanced coordinator instance."""
    global _memory_enhanced_coordinator
    if _memory_enhanced_coordinator is None:
        _memory_enhanced_coordinator = MemoryEnhancedCoordinator()
    return _memory_enhanced_coordinator
