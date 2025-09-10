"""Bidirectional Knowledge Bridge between Cursor AI and MCP/Qdrant System.

This module implements the knowledge flow between Cursor AI tactical operations
and the MCP Server's strategic memory system, enabling both to learn and improve.
"""

import logging
import uuid
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from ..database.enhanced_vector_store import (
    get_enhanced_vector_store,
    CursorKnowledgePoint,
)

logger = logging.getLogger(__name__)


@dataclass
class KnowledgePattern:
    """A knowledge pattern for Cursor to use."""

    pattern_type: str
    confidence: float
    template: str
    success_rate: float
    common_modifications: List[str]
    technology_stack: List[str]
    project_context: str
    metadata: Dict[str, Any]


@dataclass
class CursorKnowledgeRequest:
    """Request format for Cursor knowledge ingestion."""

    action_type: str  # 'file_created', 'code_modified', 'pattern_used'
    content: str  # Code content or pattern description
    file_path: str  # File location
    project_context: str  # Current project ID
    user_feedback: Optional[str] = None  # User satisfaction/modifications
    success_metrics: Optional[Dict[str, Any]] = None  # Performance metrics
    technology_stack: Optional[List[str]] = None  # Technologies used


@dataclass
class PatternResponse:
    """Response format for pattern queries."""

    relevant_patterns: List[Dict[str, Any]]
    project_conventions: Dict[str, str]
    context_metadata: Dict[str, Any]


class CursorKnowledgeBridge:
    """Bidirectional knowledge bridge between Cursor and MCP/Qdrant."""

    def __init__(self, vector_store=None):
        """Initialize the knowledge bridge."""
        self.vector_store = vector_store or get_enhanced_vector_store()
        self.knowledge_collection = "cursor_knowledge"
        self.pattern_collection = "cursor_patterns"

        # Ensure collections exist
        self._initialize_collections()

        logger.info("CursorKnowledgeBridge initialized with vector store integration")

    def _initialize_collections(self):
        """Initialize required collections in vector store."""
        try:
            # Create collections for Cursor knowledge
            collections_to_create = [
                (self.knowledge_collection, 384),  # For knowledge points
                (self.pattern_collection, 384),  # For extracted patterns
            ]

            for collection_name, vector_size in collections_to_create:
                try:
                    self.vector_store.create_collection(collection_name, vector_size)
                    logger.info(f"Created collection: {collection_name}")
                except Exception as e:
                    logger.debug(f"Collection {collection_name} may already exist: {e}")

        except Exception as e:
            logger.warning(f"Failed to initialize collections: {e}")

    def ingest_cursor_action(
        self,
        action_type: str,
        content: str,
        file_path: str,
        project_context: str,
        user_feedback: Optional[str] = None,
        success_metrics: Optional[Dict[str, Any]] = None,
        technology_stack: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Capture Cursor development actions into Qdrant.

        Args:
            action_type: Type of action ('file_created', 'code_modified', 'pattern_used')
            content: Code content or pattern description
            file_path: File location where action occurred
            project_context: Current project identifier
            user_feedback: Optional user satisfaction or modifications
            success_metrics: Optional performance/usability metrics
            technology_stack: Technologies used (Vue, TypeScript, etc.)

        Returns:
            Dict with success status and knowledge point ID
        """
        try:
            # Create knowledge point
            knowledge_point = {
                "id": str(uuid.uuid4()),
                "action_type": action_type,
                "file_path": file_path,
                "content_summary": self._summarize_content(content),
                "pattern_type": self._extract_pattern_type(file_path, content),
                "success_score": self._calculate_success_score(
                    user_feedback, success_metrics
                ),
                "project_context": project_context,
                "technology_stack": technology_stack
                or self._detect_technologies(file_path, content),
                "user_modifications": user_feedback,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "file_extension": self._get_file_extension(file_path),
                    "content_length": len(content),
                    "success_metrics": success_metrics or {},
                    "ingestion_source": "cursor_ai",
                },
            }

            # Store in vector database
            success = self._store_knowledge_point_sync(knowledge_point)

            if success:
                # Extract and store patterns
                self._extract_and_store_patterns_sync(knowledge_point, content)

                logger.info(
                    f"Successfully ingested Cursor action: {action_type} for {file_path}"
                )
                return {
                    "success": True,
                    "knowledge_id": knowledge_point["id"],
                    "message": "Knowledge successfully captured",
                }
            else:
                return {"success": False, "error": "Failed to store knowledge point"}

        except Exception as e:
            logger.error(f"Error ingesting Cursor action: {e}")
            return {"success": False, "error": str(e)}

    def query_relevant_patterns(
        self,
        requirements: str,
        file_type: str,
        project_context: str,
        similarity_threshold: float = 0.8,
    ) -> PatternResponse:
        """Retrieve relevant patterns for Cursor to use.

        Args:
            requirements: What Cursor is trying to build
            file_type: File extension (.vue, .ts, .css, etc.)
            project_context: Current project context
            similarity_threshold: Minimum similarity for pattern matching

        Returns:
            PatternResponse with relevant patterns and conventions
        """
        try:
            # Search for relevant patterns
            relevant_patterns = self._search_patterns_sync(
                requirements, file_type, project_context, similarity_threshold
            )

            # Get project conventions
            project_conventions = self._get_project_conventions_sync(project_context)

            # Prepare context metadata
            context_metadata = {
                "query_timestamp": datetime.now().isoformat(),
                "total_patterns_found": len(relevant_patterns),
                "file_type": file_type,
                "project_context": project_context,
                "similarity_threshold": similarity_threshold,
            }

            logger.info(
                f"Found {len(relevant_patterns)} relevant patterns for {file_type}"
            )

            return PatternResponse(
                relevant_patterns=relevant_patterns,
                project_conventions=project_conventions,
                context_metadata=context_metadata,
            )

        except Exception as e:
            logger.error(f"Error querying patterns: {e}")
            return PatternResponse(
                relevant_patterns=[],
                project_conventions={},
                context_metadata={"error": str(e)},
            )

    def _summarize_content(self, content: str, max_length: int = 200) -> str:
        """Create a summary of the content for storage."""
        if len(content) <= max_length:
            return content

        # Simple truncation with ellipsis
        return content[: max_length - 3] + "..."

    def _extract_pattern_type(self, file_path: str, content: str) -> str:
        """Extract the type of pattern from file path and content."""
        file_ext = self._get_file_extension(file_path)

        # Pattern type mapping
        pattern_map = {
            ".vue": "vue_component",
            ".ts": "typescript_module",
            ".js": "javascript_module",
            ".css": "stylesheet",
            ".scss": "sass_stylesheet",
            ".json": "configuration",
            ".md": "documentation",
            ".py": "python_module",
        }

        base_type = pattern_map.get(file_ext, "general_file")

        # Enhance with content analysis
        if "component" in content.lower():
            return f"{base_type}_component"
        elif "service" in content.lower():
            return f"{base_type}_service"
        elif "util" in content.lower() or "helper" in content.lower():
            return f"{base_type}_utility"

        return base_type

    def _calculate_success_score(
        self, user_feedback: Optional[str], success_metrics: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate success score based on feedback and metrics."""
        base_score = 0.8  # Default positive score

        # Adjust based on user feedback
        if user_feedback:
            feedback_lower = user_feedback.lower()
            if any(
                word in feedback_lower for word in ["excellent", "perfect", "great"]
            ):
                base_score = 0.95
            elif any(word in feedback_lower for word in ["good", "works", "nice"]):
                base_score = 0.85
            elif any(
                word in feedback_lower for word in ["modified", "changed", "updated"]
            ):
                base_score = 0.7
            elif any(word in feedback_lower for word in ["bad", "wrong", "error"]):
                base_score = 0.3

        # Adjust based on success metrics
        if success_metrics:
            if success_metrics.get("compilation_success"):
                base_score += 0.1
            if success_metrics.get("tests_passed"):
                base_score += 0.1
            if success_metrics.get("user_satisfaction", 0) > 0.8:
                base_score += 0.05

        return min(1.0, base_score)

    def _detect_technologies(self, file_path: str, content: str) -> List[str]:
        """Detect technologies used in the file."""
        technologies = []

        file_ext = self._get_file_extension(file_path)
        content_lower = content.lower()

        # File extension based detection
        if file_ext == ".vue":
            technologies.append("vue3")
        elif file_ext in [".ts", ".tsx"]:
            technologies.append("typescript")
        elif file_ext in [".js", ".jsx"]:
            technologies.append("javascript")

        # Content-based detection
        tech_patterns = {
            "tailwind": ["tailwind", "tw-", "@apply"],
            "pinia": ["pinia", "defineStore", "useStore"],
            "vite": ["vite", "import.meta"],
            "axios": ["axios", "axios."],
            "fastapi": ["fastapi", "FastAPI"],
            "sqlite": ["sqlite", "SQLite"],
            "postgresql": ["postgresql", "postgres"],
        }

        for tech, patterns in tech_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                technologies.append(tech)

        return technologies

    def _get_file_extension(self, file_path: str) -> str:
        """Get file extension from path."""
        import os

        return os.path.splitext(file_path)[1].lower()

    async def _store_knowledge_point(self, knowledge_point: Dict[str, Any]) -> bool:
        """Store knowledge point in vector database."""
        try:
            # Set current project context
            original_project = self.vector_store.current_project_id
            self.vector_store.set_current_project(knowledge_point["project_context"])

            # Create vector point
            vector_point = {
                "id": knowledge_point["id"],
                "vector": [0.0]
                * 384,  # Default embedding - could be enhanced with actual embeddings
                "payload": knowledge_point,
            }

            # Store in vector database
            success = self.vector_store.upsert_points(
                self.knowledge_collection, [vector_point]
            )

            # Restore original project context
            if original_project:
                self.vector_store.set_current_project(original_project)

            return success

        except Exception as e:
            logger.error(f"Failed to store knowledge point: {e}")
            return False

    async def _extract_and_store_patterns(
        self, knowledge_point: Dict[str, Any], content: str
    ):
        """Extract patterns from knowledge point and store them."""
        try:
            # Extract patterns based on content type
            patterns = self._extract_patterns_from_content(content, knowledge_point)

            for pattern in patterns:
                pattern_point = {
                    "id": str(uuid.uuid4()),
                    "vector": [0.0] * 384,  # Default embedding
                    "payload": {
                        **pattern,
                        "source_knowledge_id": knowledge_point["id"],
                        "timestamp": datetime.now().isoformat(),
                    },
                }

                self.vector_store.upsert_points(
                    self.pattern_collection, [pattern_point]
                )

            logger.debug(f"Extracted and stored {len(patterns)} patterns")

        except Exception as e:
            logger.error(f"Failed to extract patterns: {e}")

    def _extract_patterns_from_content(
        self, content: str, knowledge_point: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract reusable patterns from content."""
        patterns = []

        try:
            file_ext = knowledge_point["metadata"]["file_extension"]

            if file_ext == ".vue":
                patterns.extend(self._extract_vue_patterns(content, knowledge_point))
            elif file_ext in [".ts", ".js"]:
                patterns.extend(
                    self._extract_typescript_patterns(content, knowledge_point)
                )

        except Exception as e:
            logger.debug(f"Pattern extraction failed: {e}")

        return patterns

    def _extract_vue_patterns(
        self, content: str, knowledge_point: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract Vue-specific patterns."""
        patterns = []

        # Template structure pattern
        if "<template>" in content and "</template>" in content:
            template_start = content.find("<template>")
            template_end = content.find("</template>") + len("</template>")
            template_content = content[template_start:template_end]

            patterns.append(
                {
                    "pattern_type": "vue_template_structure",
                    "template": template_content,
                    "success_rate": knowledge_point["success_score"],
                    "technology_stack": knowledge_point["technology_stack"],
                    "project_context": knowledge_point["project_context"],
                }
            )

        # Script setup pattern
        if "<script setup" in content:
            patterns.append(
                {
                    "pattern_type": "vue_script_setup",
                    "template": "Vue 3 Composition API with script setup",
                    "success_rate": knowledge_point["success_score"],
                    "technology_stack": knowledge_point["technology_stack"],
                    "project_context": knowledge_point["project_context"],
                }
            )

        return patterns

    def _extract_typescript_patterns(
        self, content: str, knowledge_point: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract TypeScript-specific patterns."""
        patterns = []

        # Interface pattern
        if "interface " in content:
            patterns.append(
                {
                    "pattern_type": "typescript_interface",
                    "template": "TypeScript interface definition",
                    "success_rate": knowledge_point["success_score"],
                    "technology_stack": knowledge_point["technology_stack"],
                    "project_context": knowledge_point["project_context"],
                }
            )

        # Function pattern
        if "function " in content or "const " in content and "=>" in content:
            patterns.append(
                {
                    "pattern_type": "typescript_function",
                    "template": "TypeScript function definition",
                    "success_rate": knowledge_point["success_score"],
                    "technology_stack": knowledge_point["technology_stack"],
                    "project_context": knowledge_point["project_context"],
                }
            )

        return patterns

    async def _search_patterns(
        self,
        requirements: str,
        file_type: str,
        project_context: str,
        similarity_threshold: float,
    ) -> List[KnowledgePattern]:
        """Search for relevant patterns in the vector store."""
        try:
            # Set project context
            original_project = self.vector_store.current_project_id
            self.vector_store.set_current_project(project_context)

            # Search patterns collection
            # For now, use simple metadata filtering - could be enhanced with semantic search
            all_patterns = self._get_patterns_by_file_type(file_type)

            # Filter by success rate and convert to KnowledgePattern objects
            relevant_patterns = []
            for pattern_data in all_patterns:
                if pattern_data.get("success_rate", 0) >= similarity_threshold * 0.8:
                    pattern = KnowledgePattern(
                        pattern_type=pattern_data.get("pattern_type", "unknown"),
                        confidence=pattern_data.get("success_rate", 0.5),
                        template=pattern_data.get("template", ""),
                        success_rate=pattern_data.get("success_rate", 0.5),
                        common_modifications=pattern_data.get(
                            "common_modifications", []
                        ),
                        technology_stack=pattern_data.get("technology_stack", []),
                        project_context=pattern_data.get("project_context", ""),
                        metadata=pattern_data.get("metadata", {}),
                    )
                    relevant_patterns.append(pattern)

            # Restore original project context
            if original_project:
                self.vector_store.set_current_project(original_project)

            return relevant_patterns[:5]  # Limit to top 5 patterns

        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return []

    def _get_patterns_by_file_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get patterns filtered by file type."""
        # This is a simplified version - in a full implementation,
        # this would query the vector store with proper filtering
        return []

    async def _get_project_conventions(self, project_context: str) -> Dict[str, str]:
        """Get established conventions for the project."""
        try:
            # Set project context
            original_project = self.vector_store.current_project_id
            self.vector_store.set_current_project(project_context)

            # Analyze stored knowledge to extract conventions
            conventions = {
                "naming": "camelCase for variables, PascalCase for components",
                "styling": "Tailwind CSS utility classes preferred",
                "state_management": "Pinia for global state",
                "file_structure": "Feature-based organization",
            }

            # This could be enhanced to actually analyze patterns and extract conventions

            # Restore original project context
            if original_project:
                self.vector_store.set_current_project(original_project)

            return conventions

        except Exception as e:
            logger.error(f"Failed to get project conventions: {e}")
            return {}

    # Simplified synchronous implementations for immediate functionality
    def _store_knowledge_point_sync(self, knowledge_point: Dict[str, Any]) -> bool:
        """Simple in-memory storage for knowledge points."""
        try:
            if not hasattr(self, "_knowledge_store"):
                self._knowledge_store = []
            self._knowledge_store.append(knowledge_point)
            logger.info(f"Stored knowledge point: {knowledge_point['id']}")
            return True
        except Exception as e:
            logger.error(f"Error storing knowledge point: {e}")
            return False

    def _extract_and_store_patterns_sync(
        self, knowledge_point: Dict[str, Any], content: str
    ):
        """Simple pattern extraction and storage."""
        try:
            if not hasattr(self, "_pattern_store"):
                self._pattern_store = []

            patterns = self._extract_patterns(content, knowledge_point["file_path"])
            for pattern in patterns:
                pattern_entry = {
                    "id": f"pattern_{uuid.uuid4().hex[:8]}",
                    "pattern_type": pattern,
                    "source_knowledge_id": knowledge_point["id"],
                    "file_path": knowledge_point["file_path"],
                    "technology_stack": knowledge_point.get("technology_stack", []),
                    "timestamp": datetime.now().isoformat(),
                }
                self._pattern_store.append(pattern_entry)

            logger.info(f"Extracted {len(patterns)} patterns")
        except Exception as e:
            logger.error(f"Error extracting patterns: {e}")

    def _search_patterns_sync(
        self,
        requirements: str,
        file_type: str,
        project_context: str,
        similarity_threshold: float,
    ) -> List[Dict[str, Any]]:
        """Simple pattern search in memory."""
        try:
            if not hasattr(self, "_pattern_store"):
                self._pattern_store = []

            # Simple keyword matching for now
            results = []
            requirements_lower = requirements.lower()

            for pattern in self._pattern_store:
                score = 0.0

                # Check file type match
                if file_type in pattern.get("file_path", ""):
                    score += 0.3

                # Check technology stack match
                for tech in pattern.get("technology_stack", []):
                    if tech.lower() in requirements_lower:
                        score += 0.2

                # Check pattern type relevance
                pattern_type = pattern.get("pattern_type", "")
                if any(word in pattern_type for word in requirements_lower.split()):
                    score += 0.2

                if score >= similarity_threshold:
                    pattern_with_score = pattern.copy()
                    pattern_with_score["score"] = score
                    results.append(pattern_with_score)

            # Sort by score
            results.sort(key=lambda x: x.get("score", 0), reverse=True)

            logger.info(f"Found {len(results)} matching patterns")
            return results

        except Exception as e:
            logger.error(f"Error searching patterns: {e}")
            return []

    def _get_project_conventions_sync(self, project_context: str) -> Dict[str, str]:
        """Simple project conventions."""
        return {
            "coding_style": "TypeScript with strict typing",
            "component_structure": "Vue 3 Composition API",
            "file_naming": "kebab-case for components",
            "import_style": "ES6 imports with explicit extensions",
        }

    # Missing helper methods
    def _extract_patterns(self, content: str, file_path: str) -> List[str]:
        """Extract patterns from code content."""
        patterns = []

        # Basic pattern detection
        if file_path.endswith(".vue"):
            if "<template>" in content:
                patterns.append("vue_template")
            if "<script setup" in content:
                patterns.append("vue_composition_api")
            if "defineProps" in content:
                patterns.append("vue_props_definition")
            if "defineEmits" in content:
                patterns.append("vue_emits_definition")

        elif file_path.endswith((".ts", ".tsx")):
            if "interface " in content:
                patterns.append("typescript_interface")
            if "export const" in content:
                patterns.append("typescript_const_export")
            if "React.FC" in content:
                patterns.append("react_functional_component")

        elif file_path.endswith(".js"):
            if "export default" in content:
                patterns.append("es6_default_export")
            if "async function" in content:
                patterns.append("async_function")

        return patterns


# Global instance
_knowledge_bridge = None


def get_knowledge_bridge() -> CursorKnowledgeBridge:
    """Get the global knowledge bridge instance."""
    global _knowledge_bridge
    if _knowledge_bridge is None:
        _knowledge_bridge = CursorKnowledgeBridge()
    return _knowledge_bridge
