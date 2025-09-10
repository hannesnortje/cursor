"""Enhanced vector store with project-specific databases and fallback support."""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio
from dataclasses import dataclass

# Try to import Qdrant with fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
    )

    QDRANT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Qdrant client available for enhanced vector store")
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None
    Filter = None
    FieldCondition = None
    MatchValue = None
    logger = logging.getLogger(__name__)
    logger.warning("Qdrant client not available - using in-memory fallback")

logger = logging.getLogger(__name__)


@dataclass
class ConversationPoint:
    """A conversation point stored in the vector database."""

    id: str
    session_id: str
    agent_id: str
    agent_type: str
    message: str
    context: str
    timestamp: datetime
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass
class ProjectContext:
    """Project context stored in the vector database."""

    id: str
    project_id: str
    project_name: str
    context_type: str  # planning, development, review, etc.
    content: str
    agent_id: str
    timestamp: datetime
    metadata: Dict[str, Any]
    vector: Optional[List[float]] = None


@dataclass
class CursorKnowledgePoint:
    """A knowledge point from Cursor development actions."""

    id: str
    action_type: str  # file_creation, code_modification, debugging, etc.
    content: str
    file_path: str
    project_context: str
    user_feedback: Optional[str]
    success_metrics: Dict[str, Any]
    technology_stack: List[str]
    patterns_identified: List[str]
    timestamp: datetime
    vector: Optional[List[float]] = None


class InMemoryVectorStore:
    """In-memory fallback for vector storage."""

    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        logger.info("Initialized in-memory vector store fallback")

    def create_collection(self, collection_name: str, vector_size: int = 1536) -> bool:
        """Create a collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = []
            self.embeddings[collection_name] = []
            logger.info(f"Created in-memory collection: {collection_name}")
            return True
        return False

    def upsert_points(self, collection_name: str, points: List[Dict[str, Any]]) -> bool:
        """Upsert points to collection."""
        if collection_name not in self.collections:
            self.create_collection(collection_name)

        for point in points:
            point_id = point.get("id", str(uuid.uuid4()))
            vector = point.get("vector", [0.0] * 1536)  # Default vector
            payload = point.get("payload", {})

            # Store in memory
            self.collections[collection_name].append(
                {
                    "id": point_id,
                    "payload": payload,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            self.embeddings[collection_name].append(vector)

        logger.info(f"Upserted {len(points)} points to {collection_name}")
        return True

    def search_points(
        self, collection_name: str, query_vector: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search points in collection."""
        if collection_name not in self.collections:
            return []

        # Simple cosine similarity search (simplified)
        results = []
        for i, stored_vector in enumerate(self.embeddings[collection_name]):
            # Calculate simple similarity (dot product for normalized vectors)
            similarity = sum(a * b for a, b in zip(query_vector, stored_vector))
            results.append(
                {
                    "id": self.collections[collection_name][i]["id"],
                    "score": similarity,
                    "payload": self.collections[collection_name][i]["payload"],
                }
            )

        # Sort by similarity and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        if collection_name not in self.collections:
            return {"points_count": 0, "status": "not_found"}

        return {
            "points_count": len(self.collections[collection_name]),
            "status": "ok",
            "vector_size": (
                len(self.embeddings[collection_name][0])
                if self.embeddings[collection_name]
                else 0
            ),
        }


class EnhancedVectorStore:
    """Enhanced vector store with project-specific databases and fallback support."""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant_url = qdrant_url
        self.client = None
        self.in_memory_store = InMemoryVectorStore()
        self.fallback_mode = False
        self.current_project_id = None
        self.project_collections = {}

        # Try to initialize Qdrant client
        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(url=qdrant_url)
                # Test connection
                self.client.get_collections()
                logger.info(f"Connected to Qdrant at {qdrant_url}")
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant: {e}")
                logger.info("Falling back to in-memory storage")
                self.fallback_mode = True
                self.client = None
        else:
            logger.info("Qdrant not available - using in-memory fallback")
            self.fallback_mode = True

    def set_current_project(self, project_id: str) -> bool:
        """Set the current project context."""
        self.current_project_id = project_id
        logger.info(f"Set current project context: {project_id}")
        return True

    def get_collection_name(self, base_name: str) -> str:
        """Get full collection name with project prefix."""
        if self.current_project_id:
            return f"project_{self.current_project_id}_{base_name}"
        return base_name

    def create_project_collections(self, project_id: str) -> bool:
        """Create all collections for a project."""
        self.set_current_project(project_id)

        collections = [
            "conversations",
            "projects",
            "agents",
            "knowledge",
            "cursor_knowledge",
            "sprints",
            "documents",
        ]

        success = True
        for collection in collections:
            if not self.create_collection(collection):
                success = False

        if success:
            logger.info(f"Created all collections for project {project_id}")
        else:
            logger.warning(
                f"Some collections failed to create for project {project_id}"
            )

        return success

    def create_collection(self, collection_name: str, vector_size: int = 1536) -> bool:
        """Create a collection."""
        full_name = self.get_collection_name(collection_name)

        if self.fallback_mode:
            return self.in_memory_store.create_collection(full_name, vector_size)

        try:
            self.client.create_collection(
                collection_name=full_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {full_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {full_name}: {e}")
            logger.info("Falling back to in-memory storage")
            self.fallback_mode = True
            return self.in_memory_store.create_collection(full_name, vector_size)

    def upsert_conversation(
        self,
        conversation_id: str,
        message: str,
        response: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """Upsert a conversation point."""
        collection_name = self.get_collection_name("conversations")

        # Convert string ID to UUID for Qdrant compatibility
        try:
            if (
                isinstance(conversation_id, str)
                and not conversation_id.replace("-", "").isalnum()
            ):
                # If it's not a valid UUID format, generate one
                point_id = str(uuid.uuid4())
            else:
                point_id = conversation_id
        except:
            point_id = str(uuid.uuid4())

        point = {
            "id": point_id,
            "vector": embedding,
            "payload": {
                "conversation_id": conversation_id,  # Store original ID in payload
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "project_id": self.current_project_id,
                **(metadata or {}),
            },
        }

        return self.upsert_points(collection_name, [point])

    def upsert_knowledge(
        self,
        knowledge_id: str,
        content: str,
        embedding: List[float],
        metadata: Dict[str, Any] = None,
    ) -> bool:
        """Upsert a knowledge point."""
        collection_name = self.get_collection_name("knowledge")

        # Convert string ID to UUID for Qdrant compatibility
        try:
            if (
                isinstance(knowledge_id, str)
                and not knowledge_id.replace("-", "").isalnum()
            ):
                # If it's not a valid UUID format, generate one
                point_id = str(uuid.uuid4())
            else:
                point_id = knowledge_id
        except:
            point_id = str(uuid.uuid4())

        point = {
            "id": point_id,
            "vector": embedding,
            "payload": {
                "knowledge_id": knowledge_id,  # Store original ID in payload
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "project_id": self.current_project_id,
                **(metadata or {}),
            },
        }

        return self.upsert_points(collection_name, [point])

    def upsert_points(self, collection_name: str, points: List[Dict[str, Any]]) -> bool:
        """Upsert points to collection."""
        if self.fallback_mode:
            return self.in_memory_store.upsert_points(collection_name, points)

        try:
            # Convert to Qdrant format
            qdrant_points = []
            for point in points:
                qdrant_points.append(
                    PointStruct(
                        id=point["id"],
                        vector=point["vector"],
                        payload=point.get("payload", {}),
                    )
                )

            self.client.upsert(collection_name=collection_name, points=qdrant_points)
            logger.info(f"Upserted {len(points)} points to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points to {collection_name}: {e}")
            logger.info("Falling back to in-memory storage")
            self.fallback_mode = True
            return self.in_memory_store.upsert_points(collection_name, points)

    def search_conversations(
        self, query_embedding: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search conversations."""
        collection_name = self.get_collection_name("conversations")
        return self.search_points(collection_name, query_embedding, limit)

    def search_knowledge(
        self, query_embedding: List[float], limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        collection_name = self.get_collection_name("knowledge")
        return self.search_points(collection_name, query_embedding, limit)

    def search_points(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 10,
        filter_conditions: Dict[str, Any] = None,
    ) -> List[Dict[str, Any]]:
        """Search points in collection."""
        if self.fallback_mode:
            return self.in_memory_store.search_points(
                collection_name, query_vector, limit
            )

        try:
            # Build filter if provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                search_filter = Filter(must=conditions)

            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter,
            )

            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append(
                    {"id": result.id, "score": result.score, "payload": result.payload}
                )

            return formatted_results
        except Exception as e:
            logger.error(f"Failed to search in {collection_name}: {e}")
            logger.info("Falling back to in-memory search")
            self.fallback_mode = True
            return self.in_memory_store.search_points(
                collection_name, query_vector, limit
            )

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get collection information."""
        full_name = self.get_collection_name(collection_name)

        if self.fallback_mode:
            return self.in_memory_store.get_collection_info(full_name)

        try:
            info = self.client.get_collection(full_name)
            return {
                "points_count": info.points_count,
                "status": "ok",
                "vector_size": info.config.params.vectors.size,
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {full_name}: {e}")
            return {"points_count": 0, "status": "error", "error": str(e)}

    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project."""
        self.set_current_project(project_id)

        collections = [
            "conversations",
            "projects",
            "agents",
            "knowledge",
            "sprints",
            "documents",
        ]
        stats = {
            "project_id": project_id,
            "mode": "in_memory_fallback" if self.fallback_mode else "qdrant",
            "collections": {},
        }

        for collection in collections:
            info = self.get_collection_info(collection)
            stats["collections"][collection] = info

        return stats

    def reset_project_memory(
        self, project_id: str, preserve_general_knowledge: bool = True
    ) -> bool:
        """Reset memory for a specific project while optionally preserving general knowledge."""
        try:
            self.set_current_project(project_id)

            if self.fallback_mode:
                # Reset in-memory store for this project
                for collection_name in [
                    "conversations",
                    "knowledge",
                    "agents",
                    "cursor_knowledge",
                ]:
                    full_name = self.get_collection_name(collection_name)
                    if full_name in self.in_memory_store.collections:
                        if (
                            preserve_general_knowledge
                            and collection_name == "knowledge"
                        ):
                            # Keep only general knowledge (not project-specific)
                            original_collection = self.in_memory_store.collections[
                                full_name
                            ]
                            self.in_memory_store.collections[full_name] = [
                                point
                                for point in original_collection
                                if point.get("payload", {}).get("project_id")
                                != project_id
                            ]
                        else:
                            # Clear all project-specific data
                            self.in_memory_store.collections[full_name] = []

                logger.info(f"Reset project memory for {project_id} (in-memory mode)")
                return True
            else:
                # Reset Qdrant collections for this project
                for collection_name in [
                    "conversations",
                    "knowledge",
                    "agents",
                    "cursor_knowledge",
                ]:
                    full_name = self.get_collection_name(collection_name)
                    try:
                        if (
                            preserve_general_knowledge
                            and collection_name == "knowledge"
                        ):
                            # Delete only project-specific knowledge points
                            self.client.delete(
                                collection_name=full_name,
                                points_selector=Filter(
                                    must=[
                                        FieldCondition(
                                            key="project_id",
                                            match=MatchValue(value=project_id),
                                        )
                                    ]
                                ),
                            )
                        else:
                            # Clear all project-specific data
                            self.client.delete(
                                collection_name=full_name,
                                points_selector=Filter(
                                    must=[
                                        FieldCondition(
                                            key="project_id",
                                            match=MatchValue(value=project_id),
                                        )
                                    ]
                                ),
                            )
                    except Exception as e:
                        logger.warning(
                            f"Failed to reset {collection_name} for project {project_id}: {e}"
                        )

                logger.info(f"Reset project memory for {project_id} (Qdrant mode)")
                return True

        except Exception as e:
            logger.error(f"Failed to reset project memory for {project_id}: {e}")
            return False

    def archive_project_memory(self, project_id: str) -> bool:
        """Archive project memory by moving it to an archived collection."""
        try:
            self.set_current_project(project_id)

            if self.fallback_mode:
                # In-memory archiving - just mark as archived
                for collection_name in [
                    "conversations",
                    "knowledge",
                    "agents",
                    "cursor_knowledge",
                ]:
                    full_name = self.get_collection_name(collection_name)
                    if full_name in self.in_memory_store.collections:
                        for point in self.in_memory_store.collections[full_name]:
                            point["payload"]["archived"] = True
                            point["payload"]["archived_at"] = datetime.now().isoformat()

                logger.info(
                    f"Archived project memory for {project_id} (in-memory mode)"
                )
                return True
            else:
                # Qdrant archiving - move to archived collections
                for collection_name in [
                    "conversations",
                    "knowledge",
                    "agents",
                    "cursor_knowledge",
                ]:
                    full_name = self.get_collection_name(collection_name)
                    archived_name = f"{full_name}_archived"

                    try:
                        # Create archived collection if it doesn't exist
                        self.client.create_collection(
                            collection_name=archived_name,
                            vectors_config=VectorParams(
                                size=384,  # Default embedding size
                                distance=Distance.COSINE,
                            ),
                        )

                        # Move project data to archived collection
                        # (This would require more complex logic in a real implementation)
                        logger.info(
                            f"Archived {collection_name} for project {project_id}"
                        )

                    except Exception as e:
                        logger.warning(
                            f"Failed to archive {collection_name} for project {project_id}: {e}"
                        )

                logger.info(f"Archived project memory for {project_id} (Qdrant mode)")
                return True

        except Exception as e:
            logger.error(f"Failed to archive project memory for {project_id}: {e}")
            return False

    # Fast search methods for performance-optimized coordinator

    def search_knowledge_simple(self, query: str, limit: int = 5) -> List[Any]:
        """Fast knowledge search with minimal processing."""
        try:
            if self.fallback_mode:
                # Simple text matching for fallback
                results = []
                knowledge_collection = self.in_memory_store.collections.get(
                    self.get_collection_name("knowledge"), []
                )

                query_lower = query.lower()
                for point in knowledge_collection:
                    payload = point.get("payload", {})
                    content = str(payload.get("content", "")).lower()
                    title = str(payload.get("title", "")).lower()

                    if query_lower in content or query_lower in title:
                        results.append(payload)

                    if len(results) >= limit:
                        break

                return results
            else:
                # Fast Qdrant search without heavy embedding
                collection_name = self.get_collection_name("knowledge")

                # Use a simple embedding or fallback to text search
                try:
                    embedding = self._get_simple_embedding(query)
                    search_result = self.client.search(
                        collection_name=collection_name,
                        query_vector=embedding,
                        limit=limit,
                        with_payload=True,
                    )

                    return [hit.payload for hit in search_result]
                except Exception:
                    # Fallback to empty results if search fails
                    return []

        except Exception as e:
            logger.warning(f"Fast knowledge search failed: {e}")
            return []

    def search_conversations_simple(self, query: str, limit: int = 3) -> List[Any]:
        """Fast conversation search with minimal processing."""
        try:
            if self.fallback_mode:
                # Simple text matching for fallback
                results = []
                conv_collection = self.in_memory_store.collections.get(
                    self.get_collection_name("conversations"), []
                )

                query_lower = query.lower()
                for point in conv_collection:
                    payload = point.get("payload", {})
                    message = str(payload.get("message", "")).lower()

                    if query_lower in message:
                        results.append(payload)

                    if len(results) >= limit:
                        break

                return results
            else:
                # Fast Qdrant search
                collection_name = self.get_collection_name("conversations")

                try:
                    embedding = self._get_simple_embedding(query)
                    search_result = self.client.search(
                        collection_name=collection_name,
                        query_vector=embedding,
                        limit=limit,
                        with_payload=True,
                    )

                    return [hit.payload for hit in search_result]
                except Exception:
                    return []

        except Exception as e:
            logger.warning(f"Fast conversation search failed: {e}")
            return []

    def get_success_patterns_fast(self, project_type: str) -> List[Any]:
        """Get success patterns for project type quickly."""
        try:
            # Simple pattern matching based on project type
            patterns = [
                {
                    "pattern": "Component-driven development",
                    "success_rate": 0.95,
                    "project_type": project_type,
                },
                {
                    "pattern": "Iterative PDCA cycles",
                    "success_rate": 0.90,
                    "project_type": project_type,
                },
                {
                    "pattern": "Early testing integration",
                    "success_rate": 0.85,
                    "project_type": project_type,
                },
            ]

            return patterns

        except Exception as e:
            logger.warning(f"Fast success pattern retrieval failed: {e}")
            return []

    def _get_simple_embedding(self, text: str) -> List[float]:
        """Get a simple embedding for fast search."""
        try:
            # Try to use the embeddings if available
            if hasattr(self, "embeddings") and self.embeddings:
                return self.embeddings.encode_text(text)
            else:
                # Fallback to a simple hash-based embedding
                import hashlib

                text_hash = hashlib.md5(text.encode()).hexdigest()
                # Convert hash to float vector
                embedding = []
                for i in range(0, len(text_hash), 2):
                    val = int(text_hash[i : i + 2], 16) / 255.0
                    embedding.append(val)

                # Pad or truncate to 384 dimensions
                while len(embedding) < 384:
                    embedding.extend(embedding[: 384 - len(embedding)])

                return embedding[:384]

        except Exception as e:
            logger.warning(f"Simple embedding failed: {e}")
            # Return zero vector as ultimate fallback
            return [0.0] * 384


# Global instance
_enhanced_vector_store = None


def get_enhanced_vector_store() -> EnhancedVectorStore:
    """Get the global enhanced vector store instance."""
    global _enhanced_vector_store
    if _enhanced_vector_store is None:
        _enhanced_vector_store = EnhancedVectorStore()
    return _enhanced_vector_store
