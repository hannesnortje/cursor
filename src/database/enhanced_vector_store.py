"""Enhanced vector store with project-specific databases and fallback support."""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import asyncio

# Try to import Qdrant with fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
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


class InMemoryVectorStore:
    """In-memory fallback for vector storage."""
    
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        logger.info("Initialized in-memory vector store fallback")
    
    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
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
            vector = point.get("vector", [0.0] * 384)  # Default vector
            payload = point.get("payload", {})
            
            # Store in memory
            self.collections[collection_name].append({
                "id": point_id,
                "payload": payload,
                "timestamp": datetime.now().isoformat()
            })
            self.embeddings[collection_name].append(vector)
        
        logger.info(f"Upserted {len(points)} points to {collection_name}")
        return True
    
    def search_points(self, collection_name: str, query_vector: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search points in collection."""
        if collection_name not in self.collections:
            return []
        
        # Simple cosine similarity search (simplified)
        results = []
        for i, stored_vector in enumerate(self.embeddings[collection_name]):
            # Calculate simple similarity (dot product for normalized vectors)
            similarity = sum(a * b for a, b in zip(query_vector, stored_vector))
            results.append({
                "id": self.collections[collection_name][i]["id"],
                "score": similarity,
                "payload": self.collections[collection_name][i]["payload"]
            })
        
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
            "vector_size": len(self.embeddings[collection_name][0]) if self.embeddings[collection_name] else 0
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
            "sprints",
            "documents"
        ]
        
        success = True
        for collection in collections:
            if not self.create_collection(collection):
                success = False
        
        if success:
            logger.info(f"Created all collections for project {project_id}")
        else:
            logger.warning(f"Some collections failed to create for project {project_id}")
        
        return success
    
    def create_collection(self, collection_name: str, vector_size: int = 384) -> bool:
        """Create a collection."""
        full_name = self.get_collection_name(collection_name)
        
        if self.fallback_mode:
            return self.in_memory_store.create_collection(full_name, vector_size)
        
        try:
            self.client.create_collection(
                collection_name=full_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
            logger.info(f"Created Qdrant collection: {full_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection {full_name}: {e}")
            logger.info("Falling back to in-memory storage")
            self.fallback_mode = True
            return self.in_memory_store.create_collection(full_name, vector_size)
    
    def upsert_conversation(self, conversation_id: str, message: str, response: str, 
                          embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """Upsert a conversation point."""
        collection_name = self.get_collection_name("conversations")
        
        point = {
            "id": conversation_id,
            "vector": embedding,
            "payload": {
                "message": message,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "project_id": self.current_project_id,
                **(metadata or {})
            }
        }
        
        return self.upsert_points(collection_name, [point])
    
    def upsert_knowledge(self, knowledge_id: str, content: str, 
                        embedding: List[float], metadata: Dict[str, Any] = None) -> bool:
        """Upsert a knowledge point."""
        collection_name = self.get_collection_name("knowledge")
        
        point = {
            "id": knowledge_id,
            "vector": embedding,
            "payload": {
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "project_id": self.current_project_id,
                **(metadata or {})
            }
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
                qdrant_points.append(PointStruct(
                    id=point["id"],
                    vector=point["vector"],
                    payload=point.get("payload", {})
                ))
            
            self.client.upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
            logger.info(f"Upserted {len(points)} points to {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to upsert points to {collection_name}: {e}")
            logger.info("Falling back to in-memory storage")
            self.fallback_mode = True
            return self.in_memory_store.upsert_points(collection_name, points)
    
    def search_conversations(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations."""
        collection_name = self.get_collection_name("conversations")
        return self.search_points(collection_name, query_embedding, limit)
    
    def search_knowledge(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base."""
        collection_name = self.get_collection_name("knowledge")
        return self.search_points(collection_name, query_embedding, limit)
    
    def search_points(self, collection_name: str, query_vector: List[float], 
                     limit: int = 10, filter_conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Search points in collection."""
        if self.fallback_mode:
            return self.in_memory_store.search_points(collection_name, query_vector, limit)
        
        try:
            # Build filter if provided
            search_filter = None
            if filter_conditions:
                conditions = []
                for key, value in filter_conditions.items():
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
                search_filter = Filter(must=conditions)
            
            results = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
            
            # Convert to standard format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload
                })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Failed to search in {collection_name}: {e}")
            logger.info("Falling back to in-memory search")
            self.fallback_mode = True
            return self.in_memory_store.search_points(collection_name, query_vector, limit)
    
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
                "vector_size": info.config.params.vectors.size
            }
        except Exception as e:
            logger.error(f"Failed to get collection info for {full_name}: {e}")
            return {"points_count": 0, "status": "error", "error": str(e)}
    
    def get_project_stats(self, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project."""
        self.set_current_project(project_id)
        
        collections = ["conversations", "projects", "agents", "knowledge", "sprints", "documents"]
        stats = {
            "project_id": project_id,
            "mode": "in_memory_fallback" if self.fallback_mode else "qdrant",
            "collections": {}
        }
        
        for collection in collections:
            info = self.get_collection_info(collection)
            stats["collections"][collection] = info
        
        return stats


# Global instance
_enhanced_vector_store = None

def get_enhanced_vector_store() -> EnhancedVectorStore:
    """Get the global enhanced vector store instance."""
    global _enhanced_vector_store
    if _enhanced_vector_store is None:
        _enhanced_vector_store = EnhancedVectorStore()
    return _enhanced_vector_store
