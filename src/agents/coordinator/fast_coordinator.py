"""Fast Rule-Based Coordinator with Optional LLM Polish.

This coordinator uses fast rule-based logic and templates for most tasks,
with optional local LLM enhancement for communication polish only.
"""

import logging
import asyncio
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class FastIntentResult:
    """Fast intent detection result."""

    intent: str
    confidence: float
    extracted_data: Dict[str, Any]
    keywords: List[str]


@dataclass
class ResponseTemplate:
    """Template for response generation."""

    template: str
    variables: Dict[str, Any]
    polish_recommended: bool = False


class FastCoordinator:
    """Fast rule-based coordinator with optional LLM polish."""

    def __init__(self, vector_store=None, llm_gateway=None):
        self.vector_store = vector_store
        self.llm_gateway = llm_gateway
        self.enable_llm_polish = True  # Optional LLM enhancement

        # Fast intent patterns
        self.intent_patterns = {
            "project_planning": [
                r"create.*project",
                r"build.*dashboard",
                r"develop.*application",
                r"plan.*project",
                r"start.*project",
                r"new.*project",
                r"vue\.?js",
                r"react",
                r"angular",
                r"frontend",
                r"backend",
                r"dashboard",
                r"webapp",
                r"website",
                r"api",
            ],
            "agent_creation": [
                r"create.*agent",
                r"build.*team",
                r"need.*agent",
                r"agent.*team",
                r"recommendation.*agent",
                r"agent.*help",
            ],
            "methodology_help": [
                r"pdca",
                r"agile",
                r"scrum",
                r"methodology",
                r"framework",
                r"process",
                r"approach",
                r"best.*practice",
            ],
            "knowledge_search": [
                r"how.*to",
                r"what.*is",
                r"explain",
                r"tell.*me",
                r"help.*with",
                r"information",
                r"learn",
                r"understand",
                r"documentation",
            ],
            "status_check": [
                r"status",
                r"progress",
                r"what.*happening",
                r"current.*state",
                r"how.*going",
                r"update",
            ],
        }

        # Response templates
        self.response_templates = {
            "project_planning": {
                "template": """🎯 **Fast Project Planning Ready**

**📊 Project Type Detected:** {project_type}

**🧠 Memory Insights:**
- Found {similar_projects_count} similar projects
- Success rate: {success_rate}%
- {knowledge_items_count} relevant knowledge items

**🚀 Recommended Approach:**
- **Methodology:** {methodology}
- **Key Phases:** {key_phases}
- **Proven Technologies:** {technologies}

**🤖 Recommended Agent Team:**
{agent_recommendations}

**✅ Ready to proceed!**

Would you like me to:
1. Start detailed planning for this project type?
2. Create the recommended agent team?
3. Show specific implementation guidance?""",
                "polish_recommended": True,
            },
            "agent_creation": {
                "template": """🤖 **Agent Team Recommendation**

**👥 Recommended Team for {project_type}:**
{agent_list}

**📊 Team Composition:**
- **Size:** {team_size} agents
- **Specializations:** {specializations}
- **Success Pattern:** Based on {success_projects} successful projects

**🎯 Next Steps:**
1. Create these agents with specialized roles
2. Set up collaboration patterns
3. Define communication protocols

Ready to create this team?""",
                "polish_recommended": False,
            },
            "knowledge_search": {
                "template": """📚 **Knowledge Search Results**

**🔍 Found {results_count} relevant items:**

{knowledge_results}

**💡 Key Insights:**
{key_insights}

**📖 Recommended Reading:**
{recommendations}

Need more specific information?""",
                "polish_recommended": True,
            },
            "methodology_help": {
                "template": """📋 **{methodology} Methodology Guide**

**🎯 Current Phase:** {current_phase}

**📊 Framework Overview:**
{framework_overview}

**✅ Recommended Actions:**
{recommended_actions}

**📈 Success Metrics:**
{success_metrics}

Ready to apply this methodology?""",
                "polish_recommended": False,
            },
            "general": {
                "template": """🤖 **Memory-Enhanced Coordinator Ready**

I'm your intelligent project coordinator with access to:
📚 {knowledge_count} knowledge items
💭 {conversation_count} stored conversations
🎯 {success_patterns_count} proven success patterns

**I can help you with:**
1. **Fast Project Planning** - Using proven templates and patterns
2. **Agent Team Creation** - Based on successful project patterns
3. **Knowledge Search** - Instant access to curated expertise
4. **Methodology Guidance** - PDCA, Agile, and best practices

What would you like to work on?""",
                "polish_recommended": True,
            },
        }

    async def process_message_fast(self, user_message: str) -> Dict[str, Any]:
        """Fast message processing with rule-based logic."""
        try:
            start_time = datetime.now()

            # Step 1: Fast intent detection (< 0.1s)
            intent_result = self._detect_intent_fast(user_message)

            # Step 2: Quick memory search (< 0.5s)
            memory_context = await self._search_memory_fast(user_message, intent_result)

            # Step 3: Template-based response generation (< 0.1s)
            response_template = self._generate_response_template(
                intent_result, memory_context
            )

            # Step 4: Optional LLM polish (< 3s, only if beneficial)
            final_response = await self._apply_optional_polish(
                response_template, user_message
            )

            # Calculate timing
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()

            return {
                "success": True,
                "response": final_response,
                "intent": intent_result.intent,
                "confidence": intent_result.confidence,
                "processing_time": processing_time,
                "memory_items": len(memory_context.get("knowledge_items", [])),
                "similar_projects": len(memory_context.get("similar_projects", [])),
                "timestamp": end_time.isoformat(),
                "coordinator_type": "fast_rule_based",
                "llm_enhanced": response_template.polish_recommended
                and self.enable_llm_polish,
            }

        except Exception as e:
            logger.error(f"Error in fast message processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error while processing your request quickly. Let me try a simpler approach.",
                "coordinator_type": "fast_rule_based",
            }

    def _detect_intent_fast(self, user_message: str) -> FastIntentResult:
        """Fast rule-based intent detection using pattern matching."""
        message_lower = user_message.lower()
        intent_scores = {}
        matched_keywords = []

        # Score each intent based on pattern matches
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
                    matched_keywords.extend(re.findall(pattern, message_lower))

            if score > 0:
                intent_scores[intent] = score / len(
                    patterns
                )  # Normalize by pattern count

        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores.keys(), key=lambda k: intent_scores[k])
            confidence = min(intent_scores[best_intent] * 2, 1.0)  # Scale confidence
        else:
            best_intent = "general"
            confidence = 0.8

        # Extract project type for project planning
        extracted_data = {}
        if best_intent == "project_planning":
            extracted_data["project_type"] = self._extract_project_type(message_lower)

        return FastIntentResult(
            intent=best_intent,
            confidence=confidence,
            extracted_data=extracted_data,
            keywords=matched_keywords,
        )

    def _extract_project_type(self, message: str) -> str:
        """Extract project type from message."""
        if any(term in message for term in ["dashboard", "analytics", "monitoring"]):
            return "dashboard_application"
        elif any(term in message for term in ["vue", "react", "angular", "frontend"]):
            return "frontend_web_application"
        elif any(term in message for term in ["api", "backend", "server"]):
            return "backend_api_service"
        elif any(
            term in message
            for term in [
                "mobile app",
                "ios",
                "android",
                "native app",
                "smartphone",
                "tablet",
            ]
        ):
            return "mobile_application"
        else:
            return "web_application"

    async def _search_memory_fast(
        self, user_message: str, intent_result: FastIntentResult
    ) -> Dict[str, Any]:
        """Fast memory search with minimal overhead."""
        memory_context = {
            "similar_projects": [],
            "knowledge_items": [],
            "success_patterns": [],
            "agent_experiences": [],
        }

        if not self.vector_store:
            return memory_context

        try:
            # Quick knowledge search (limit results for speed)
            if intent_result.intent in ["knowledge_search", "methodology_help"]:
                knowledge_items = self.vector_store.search_knowledge_simple(
                    user_message, limit=5
                )
                memory_context["knowledge_items"] = knowledge_items

            # Quick project search for project planning
            if intent_result.intent == "project_planning":
                similar_projects = self.vector_store.search_conversations_simple(
                    user_message, limit=3
                )
                memory_context["similar_projects"] = similar_projects

                # Get success patterns for this project type
                project_type = intent_result.extracted_data.get(
                    "project_type", "web_application"
                )
                success_patterns = self.vector_store.get_success_patterns_fast(
                    project_type
                )
                memory_context["success_patterns"] = success_patterns

        except Exception as e:
            logger.warning(f"Fast memory search failed: {e}")
            # Continue with empty context - don't fail the whole request

        return memory_context

    def _generate_response_template(
        self, intent_result: FastIntentResult, memory_context: Dict[str, Any]
    ) -> ResponseTemplate:
        """Generate response using templates (very fast)."""
        intent = intent_result.intent
        template_config = self.response_templates.get(
            intent, self.response_templates["general"]
        )

        # Prepare template variables based on intent
        variables = self._prepare_template_variables(
            intent, intent_result, memory_context
        )

        # Fill template
        try:
            response_text = template_config["template"].format(**variables)
        except KeyError as e:
            logger.warning(f"Template variable missing: {e}")
            # Fallback to general template
            template_config = self.response_templates["general"]
            variables = self._prepare_general_variables(memory_context)
            response_text = template_config["template"].format(**variables)

        return ResponseTemplate(
            template=response_text,
            variables=variables,
            polish_recommended=template_config.get("polish_recommended", False),
        )

    def _prepare_template_variables(
        self,
        intent: str,
        intent_result: FastIntentResult,
        memory_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare variables for template filling."""
        base_vars = {
            "knowledge_count": len(memory_context.get("knowledge_items", [])),
            "conversation_count": len(memory_context.get("similar_projects", [])),
            "success_patterns_count": len(memory_context.get("success_patterns", [])),
        }

        if intent == "project_planning":
            return {
                **base_vars,
                "project_type": intent_result.extracted_data.get(
                    "project_type", "Web Application"
                )
                .replace("_", " ")
                .title(),
                "similar_projects_count": len(
                    memory_context.get("similar_projects", [])
                ),
                "success_rate": self._calculate_success_rate_fast(
                    memory_context.get("similar_projects", [])
                ),
                "knowledge_items_count": len(memory_context.get("knowledge_items", [])),
                "methodology": "PDCA-driven development with proven patterns",
                "key_phases": "Plan → Do → Check → Act cycles",
                "technologies": self._get_recommended_technologies(
                    intent_result.extracted_data.get("project_type", "")
                ),
                "agent_recommendations": self._get_agent_recommendations_fast(
                    intent_result.extracted_data.get("project_type", "")
                ),
            }

        elif intent == "agent_creation":
            project_type = self._infer_project_type_from_context(memory_context)
            return {
                **base_vars,
                "project_type": project_type.replace("_", " ").title(),
                "agent_list": self._format_agent_list(project_type),
                "team_size": self._get_recommended_team_size(project_type),
                "specializations": self._get_specializations(project_type),
                "success_projects": len(memory_context.get("similar_projects", [])),
            }

        elif intent == "knowledge_search":
            return {
                **base_vars,
                "results_count": len(memory_context.get("knowledge_items", [])),
                "knowledge_results": self._format_knowledge_results(
                    memory_context.get("knowledge_items", [])
                ),
                "key_insights": self._extract_key_insights_fast(
                    memory_context.get("knowledge_items", [])
                ),
                "recommendations": self._get_reading_recommendations(
                    memory_context.get("knowledge_items", [])
                ),
            }

        elif intent == "methodology_help":
            return {
                **base_vars,
                "methodology": "PDCA (Plan-Do-Check-Act)",
                "current_phase": "Plan",
                "framework_overview": self._get_pdca_overview(),
                "recommended_actions": self._get_pdca_actions(),
                "success_metrics": self._get_pdca_metrics(),
            }

        else:
            return self._prepare_general_variables(memory_context)

    def _prepare_general_variables(
        self, memory_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare variables for general response."""
        return {
            "knowledge_count": len(memory_context.get("knowledge_items", []))
            or 24,  # Default if no search
            "conversation_count": len(memory_context.get("similar_projects", [])),
            "success_patterns_count": len(memory_context.get("success_patterns", []))
            or 3,
        }

    def _calculate_success_rate_fast(self, projects: List[Any]) -> int:
        """Fast success rate calculation."""
        if not projects:
            return 100  # Default optimistic rate
        # Simple heuristic - most projects in memory are successful
        return min(95, 85 + len(projects) * 5)

    def _get_recommended_technologies(self, project_type: str) -> str:
        """Get recommended technologies for project type."""
        tech_map = {
            "frontend_web_application": "Vue.js, TypeScript, Vite, Tailwind CSS",
            "dashboard_application": "Vue.js, Chart.js, WebSocket, REST APIs",
            "backend_api_service": "Python, FastAPI, PostgreSQL, Redis",
            "mobile_application": "React Native, TypeScript, Expo, Async Storage",
        }
        return tech_map.get(
            project_type, "Modern web technologies with proven frameworks"
        )

    def _get_agent_recommendations_fast(self, project_type: str) -> str:
        """Get fast agent recommendations."""
        agent_map = {
            "frontend_web_application": """🔥 **Frontend Agent**: Vue.js/React development, UI/UX design
🔥 **Backend Agent**: API development, database design
🔥 **Testing Agent**: Component testing, E2E automation
🔥 **DevOps Agent**: Build pipelines, deployment automation""",
            "dashboard_application": """🔥 **Data Agent**: Analytics, metrics, visualization
🔥 **Frontend Agent**: Dashboard UI, real-time updates
🔥 **Backend Agent**: Data APIs, aggregation services
🔥 **Monitoring Agent**: Performance, alerts, health checks""",
        }
        return agent_map.get(
            project_type,
            """🔥 **Development Agent**: Core implementation and architecture
🔥 **Testing Agent**: Quality assurance and automation
🔥 **DevOps Agent**: Deployment and infrastructure
🔥 **Project Agent**: Planning and coordination""",
        )

    async def _apply_optional_polish(
        self, response_template: ResponseTemplate, user_message: str
    ) -> str:
        """Apply optional LLM polish for communication enhancement."""
        if not (
            response_template.polish_recommended
            and self.enable_llm_polish
            and self.llm_gateway
        ):
            return response_template.template

        try:
            # Quick polish with local LLM (short prompt, quick response)
            polish_prompt = f"""Make this response more conversational and natural while keeping all the content and structure exactly the same. Just improve the flow and tone:

{response_template.template}

Keep it professional but friendly. Don't add or remove any information."""

            polished = await self.llm_gateway.generate_with_fallback(
                polish_prompt,
                task_type="communication",
                max_tokens=len(response_template.template) + 100,  # Limit output size
            )

            # Fallback if polish failed or is too different
            if len(polished) > len(response_template.template) * 1.5:
                logger.warning("Polish result too long, using template")
                return response_template.template

            return polished

        except Exception as e:
            logger.warning(f"LLM polish failed: {e}")
            return response_template.template

    # Helper methods for template filling
    def _format_agent_list(self, project_type: str) -> str:
        """Format agent list for template."""
        return self._get_agent_recommendations_fast(project_type)

    def _get_recommended_team_size(self, project_type: str) -> int:
        """Get recommended team size."""
        return 4 if "dashboard" in project_type else 3

    def _get_specializations(self, project_type: str) -> str:
        """Get specializations for project type."""
        spec_map = {
            "frontend_web_application": "Frontend, Backend, Testing, DevOps",
            "dashboard_application": "Data, Frontend, Backend, Monitoring",
            "backend_api_service": "API, Database, Security, Testing",
        }
        return spec_map.get(project_type, "Development, Testing, Operations")

    def _infer_project_type_from_context(self, memory_context: Dict[str, Any]) -> str:
        """Infer project type from memory context."""
        # Simple heuristic based on knowledge items
        knowledge_items = memory_context.get("knowledge_items", [])
        if any("dashboard" in str(item).lower() for item in knowledge_items):
            return "dashboard_application"
        return "web_application"

    def _format_knowledge_results(self, knowledge_items: List[Any]) -> str:
        """Format knowledge results for display."""
        if not knowledge_items:
            return "No specific knowledge items found in memory."

        results = []
        for i, item in enumerate(knowledge_items[:3], 1):
            title = getattr(item, "title", f"Knowledge Item {i}")
            content = getattr(item, "content", str(item))[:100]
            results.append(f"{i}. **{title}**: {content}...")

        return "\n".join(results)

    def _extract_key_insights_fast(self, knowledge_items: List[Any]) -> str:
        """Extract key insights quickly."""
        if not knowledge_items:
            return "Use proven patterns and best practices for reliable results."

        # Simple pattern-based insight extraction
        insights = [
            "Focus on user experience and clear requirements",
            "Use proven technologies with strong community support",
            "Implement testing early and continuously",
            "Plan for scalability and maintainability",
        ]
        return "\n".join(f"• {insight}" for insight in insights[: len(knowledge_items)])

    def _get_reading_recommendations(self, knowledge_items: List[Any]) -> str:
        """Get reading recommendations."""
        if not knowledge_items:
            return "Check documentation for your chosen technologies."

        return "Review best practices for your project type and chosen technologies."

    def _get_pdca_overview(self) -> str:
        """Get PDCA framework overview."""
        return """• **Plan**: Define objectives, analyze requirements, design solution
• **Do**: Implement planned features in small iterations
• **Check**: Test, review, measure against objectives
• **Act**: Adjust based on feedback, improve process"""

    def _get_pdca_actions(self) -> str:
        """Get PDCA recommended actions."""
        return """1. **Set Clear Objectives**: Define what success looks like
2. **Break Into Iterations**: Small, measurable deliverables
3. **Gather Feedback Early**: Regular check-ins and reviews
4. **Continuous Improvement**: Learn and adapt each cycle"""

    def _get_pdca_metrics(self) -> str:
        """Get PDCA success metrics."""
        return """• **Quality**: Tests passing, requirements met
• **Speed**: Iteration velocity, delivery time
• **Learning**: Knowledge gained, improvements made
• **Value**: User satisfaction, business goals achieved"""
