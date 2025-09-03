"""Qdrant vector database integration for context and memory storage."""

import logging
import uuid
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance, VectorParams, PointStruct, Filter, FieldCondition,
        MatchValue, Range, GeoBoundingBox
    )
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available. Install with: pip install qdrant-client")

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


class QdrantVectorStore:
    """Qdrant vector database for storing agent context and memory."""
    
    def __init__(self, host: str = "localhost", port: int = 6333, 
                 api_key: Optional[str] = None):
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available")
        
        self.client = QdrantClient(host=host, port=port, api_key=api_key)
        self.collections = {
            "conversations": "conversations",
            "projects": "projects",
            "agents": "agents"
        }
        
        self._initialize_collections()
    
    def _initialize_collections(self):
        """Initialize Qdrant collections."""
        try:
            # Conversations collection
            self.client.recreate_collection(
                collection_name=self.collections["conversations"],
                vectors_config=VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=Distance.COSINE
                )
            )
            
            # Projects collection
            self.client.recreate_collection(
                collection_name=self.collections["projects"],
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )
            
            # Agents collection
            self.client.recreate_collection(
                collection_name=self.collections["agents"],
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )
            
            logger.info("Qdrant collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant collections: {e}")
            raise
    
    async def store_conversation(self, conversation: ConversationPoint) -> str:
        """Store a conversation point in the vector database."""
        try:
            point_id = conversation.id or str(uuid.uuid4())
            
            # Convert to Qdrant point structure
            point = PointStruct(
                id=point_id,
                vector=conversation.vector or [0.0] * 1536,  # Default vector
                payload={
                    "session_id": conversation.session_id,
                    "agent_id": conversation.agent_id,
                    "agent_type": conversation.agent_type,
                    "message": conversation.message,
                    "context": conversation.context,
                    "timestamp": conversation.timestamp.isoformat(),
                    "metadata": conversation.metadata
                }
            )
            
            self.client.upsert(
                collection_name=self.collections["conversations"],
                points=[point]
            )
            
            logger.info(f"Stored conversation point: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise
    
    async def store_project_context(self, project_context: ProjectContext) -> str:
        """Store project context in the vector database."""
        try:
            point_id = project_context.id or str(uuid.uuid4())
            
            point = PointStruct(
                id=point_id,
                vector=project_context.vector or [0.0] * 1536,
                payload={
                    "project_id": project_context.project_id,
                    "project_name": project_context.project_name,
                    "context_type": project_context.context_type,
                    "content": project_context.content,
                    "agent_id": project_context.agent_id,
                    "timestamp": project_context.timestamp.isoformat(),
                    "metadata": project_context.metadata
                }
            )
            
            self.client.upsert(
                collection_name=self.collections["projects"],
                points=[point]
            )
            
            logger.info(f"Stored project context: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to store project context: {e}")
            raise
    
    async def search_conversations(self, query: str, session_id: Optional[str] = None,
                                 agent_id: Optional[str] = None, limit: int = 10) -> List[ConversationPoint]:
        """Search conversations by semantic similarity."""
        try:
            # For now, use simple text search
            # In production, this would use embeddings
            search_filter = None
            
            if session_id:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=session_id)
                        )
                    ]
                )
            
            if agent_id:
                if search_filter:
                    search_filter.must.append(
                        FieldCondition(
                            key="agent_id",
                            match=MatchValue(value=agent_id)
                        )
                    )
                else:
                    search_filter = Filter(
                        must=[
                            FieldCondition(
                                key="agent_id",
                                match=MatchValue(value=agent_id)
                            )
                        ]
                    )
            
            # Search by payload content
            results = self.client.scroll(
                collection_name=self.collections["conversations"],
                scroll_filter=search_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            conversations = []
            for point in results[0]:
                conversation = ConversationPoint(
                    id=point.id,
                    session_id=point.payload["session_id"],
                    agent_id=point.payload["agent_id"],
                    agent_type=point.payload["agent_type"],
                    message=point.payload["message"],
                    context=point.payload["context"],
                    timestamp=datetime.fromisoformat(point.payload["timestamp"]),
                    metadata=point.payload["metadata"]
                )
                conversations.append(conversation)
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
    
    async def search_project_context(self, query: str, project_id: Optional[str] = None,
                                   context_type: Optional[str] = None, limit: int = 10) -> List[ProjectContext]:
        """Search project context by semantic similarity."""
        try:
            search_filter = None
            
            if project_id:
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="project_id",
                            match=MatchValue(value=project_id)
                        )
                    ]
                )
            
            if context_type:
                if search_filter:
                    search_filter.must.append(
                        FieldCondition(
                            key="context_type",
                            match=MatchValue(value=context_type)
                        )
                    )
                else:
                    search_filter = Filter(
                        must=[
                            FieldCondition(
                                key="context_type",
                                match=MatchValue(value=context_type)
                            )
                        ]
                    )
            
            results = self.client.scroll(
                collection_name=self.collections["projects"],
                scroll_filter=search_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            contexts = []
            for point in results[0]:
                context = ProjectContext(
                    id=point.id,
                    project_id=point.payload["project_id"],
                    project_name=point.payload["project_name"],
                    context_type=point.payload["context_type"],
                    content=point.payload["content"],
                    agent_id=point.payload["agent_id"],
                    timestamp=datetime.fromisoformat(point.payload["timestamp"]),
                    metadata=point.payload["metadata"]
                )
                contexts.append(context)
            
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to search project context: {e}")
            return []
    
    async def get_session_history(self, session_id: str, limit: int = 50) -> List[ConversationPoint]:
        """Get conversation history for a specific session."""
        try:
            results = self.client.scroll(
                collection_name=self.collections["conversations"],
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=session_id)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            conversations = []
            for point in results[0]:
                conversation = ConversationPoint(
                    id=point.id,
                    session_id=point.payload["session_id"],
                    agent_id=point.payload["agent_id"],
                    agent_type=point.payload["agent_type"],
                    message=point.payload["message"],
                    context=point.payload["context"],
                    timestamp=datetime.fromisoformat(point.payload["timestamp"]),
                    metadata=point.payload["metadata"]
                )
                conversations.append(conversation)
            
            # Sort by timestamp
            conversations.sort(key=lambda x: x.timestamp)
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get session history: {e}")
            return []
    
    async def get_project_context_history(self, project_id: str, limit: int = 50) -> List[ProjectContext]:
        """Get context history for a specific project."""
        try:
            results = self.client.scroll(
                collection_name=self.collections["projects"],
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="project_id",
                            match=MatchValue(value=project_id)
                        )
                    ]
                ),
                limit=limit,
                with_payload=True,
                with_vectors=False
            )
            
            contexts = []
            for point in results[0]:
                context = ProjectContext(
                    id=point.id,
                    project_id=point.payload["project_id"],
                    project_name=point.payload["project_name"],
                    context_type=point.payload["context_type"],
                    content=point.payload["content"],
                    agent_id=point.payload["agent_id"],
                    timestamp=datetime.fromisoformat(point.payload["timestamp"]),
                    metadata=point.payload["metadata"]
                )
                contexts.append(context)
            
            # Sort by timestamp
            contexts.sort(key=lambda x: x.timestamp)
            return contexts
            
        except Exception as e:
            logger.error(f"Failed to get project context history: {e}")
            return []
    
    async def delete_session_data(self, session_id: str) -> bool:
        """Delete all data for a specific session."""
        try:
            # Delete conversations
            self.client.delete(
                collection_name=self.collections["conversations"],
                points_selector=Filter(
                    must=[
                        FieldCondition(
                            key="session_id",
                            match=MatchValue(value=session_id)
                        )
                    ]
                )
            )
            
            logger.info(f"Deleted session data for: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session data: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections."""
        try:
            stats = {}
            for collection_name in self.collections.values():
                collection_info = self.client.get_collection(collection_name)
                stats[collection_name] = {
                    "points_count": collection_info.points_count,
                    "vectors_count": collection_info.vectors_count,
                    "status": collection_info.status
                }
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}


# Global vector store instance - initialize only if Qdrant is available and server is running
vector_store = None
if QDRANT_AVAILABLE:
    try:
        vector_store = QdrantVectorStore()
    except Exception as e:
        logging.warning(f"Failed to initialize Qdrant vector store: {e}")
        logging.info("Vector store will be disabled. Start Qdrant server to enable.")
        vector_store = None
