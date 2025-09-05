"""Enhanced vector store with mandatory Qdrant integration and project-specific databases."""

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
    logging.error("Qdrant client not available. Install with: pip install qdrant-client")

from .project_manager import get_project_manager, ProjectDatabase
from .docker_manager import get_docker_manager

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
    project_id: str  # Added for project-specific storage
    vector: Optional[List[float]] = None


@dataclass
class ProjectContext:
    """Project context stored in the vector database."""
    id: str
    project_id: str
    project_name: str
    context_type: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    vector: Optional[List[float]] = None


@dataclass
class KnowledgeBase:
    """Knowledge base entry for predetermined knowledge."""
    id: str
    project_id: str
    knowledge_type: str  # pdca, agile, security, testing, etc.
    title: str
    content: str
    tags: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    vector: Optional[List[float]] = None


class EnhancedVectorStore:
    """Enhanced vector store with mandatory Qdrant integration and project-specific databases."""
    
    def __init__(self, project_id: str = None, auto_start_qdrant: bool = True):
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available. Install with: pip install qdrant-client")
        
        self.project_id = project_id
        self.project_manager = get_project_manager()
        self.docker_manager = get_docker_manager()
        self.client: Optional[QdrantClient] = None
        self.project_db: Optional[ProjectDatabase] = None
        self.is_connected = False
        
        # Initialize with automatic Qdrant startup
        if auto_start_qdrant:
            self._ensure_qdrant_running()
        
        # Initialize project database
        self._initialize_project_database()
    
    def _ensure_qdrant_running(self):
        """Ensure Qdrant is running, start if necessary."""
        try:
            # Check if Qdrant is already running
            status = self.docker_manager.get_qdrant_status()
            if status.get("running", False):
                logger.info("Qdrant is already running")
                return
            
            # Start Qdrant container
            logger.info("Starting Qdrant container...")
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(self.docker_manager.start_qdrant())
            
            if not success:
                raise Exception("Failed to start Qdrant container")
            
            logger.info("Qdrant container started successfully")
            
        except Exception as e:
            logger.error(f"Failed to ensure Qdrant is running: {e}")
            raise Exception(f"Qdrant startup failed: {e}")
    
    def _initialize_project_database(self):
        """Initialize project-specific database."""
        try:
            if not self.project_id:
                # Create default project
                self.project_id = "default"
                project_name = "Default Project"
            else:
                project_name = f"Project {self.project_id}"
            
            # Get or create project database
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            self.project_db = loop.run_until_complete(
                self.project_manager.get_project_database(self.project_id)
            )
            
            if not self.project_db:
                # Create new project database
                self.project_db = loop.run_until_complete(
                    self.project_manager.create_project_database(project_name, self.project_id)
                )
                logger.info(f"Created project database: {self.project_db.database_name}")
            else:
                logger.info(f"Using existing project database: {self.project_db.database_name}")
            
            # Initialize Qdrant client
            self.client = self.project_manager.get_project_client(self.project_id)
            if not self.client:
                raise Exception("Failed to get Qdrant client for project")
            
            self.is_connected = True
            logger.info("Enhanced vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize project database: {e}")
            raise Exception(f"Project database initialization failed: {e}")
    
    async def store_conversation(self, conversation: ConversationPoint) -> str:
        """Store conversation in project-specific database."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
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
                    "project_id": conversation.project_id,
                    "metadata": conversation.metadata
                }
            )
            
            # Store in project-specific conversations collection
            collection_name = self.project_db.collections["conversations"]
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"Stored conversation in project {self.project_id}: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")
            raise
    
    async def store_project_context(self, project_context: ProjectContext) -> str:
        """Store project context in project-specific database."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
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
                    "timestamp": project_context.timestamp.isoformat(),
                    "metadata": project_context.metadata
                }
            )
            
            collection_name = self.project_db.collections["projects"]
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"Stored project context in project {self.project_id}: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to store project context: {e}")
            raise
    
    async def store_knowledge(self, knowledge: KnowledgeBase) -> str:
        """Store knowledge base entry in project-specific database."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
        try:
            point_id = knowledge.id or str(uuid.uuid4())
            
            point = PointStruct(
                id=point_id,
                vector=knowledge.vector or [0.0] * 1536,
                payload={
                    "project_id": knowledge.project_id,
                    "knowledge_type": knowledge.knowledge_type,
                    "title": knowledge.title,
                    "content": knowledge.content,
                    "tags": knowledge.tags,
                    "timestamp": knowledge.timestamp.isoformat(),
                    "metadata": knowledge.metadata
                }
            )
            
            collection_name = self.project_db.collections["knowledge"]
            self.client.upsert(
                collection_name=collection_name,
                points=[point]
            )
            
            logger.info(f"Stored knowledge in project {self.project_id}: {point_id}")
            return point_id
            
        except Exception as e:
            logger.error(f"Failed to store knowledge: {e}")
            raise
    
    async def search_conversations(self, query: str, limit: int = 10, 
                                 session_id: str = None, agent_id: str = None) -> List[Dict[str, Any]]:
        """Search conversations in project-specific database."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
        try:
            # Build filter
            filter_conditions = []
            if session_id:
                filter_conditions.append(
                    FieldCondition(key="session_id", match=MatchValue(value=session_id))
                )
            if agent_id:
                filter_conditions.append(
                    FieldCondition(key="agent_id", match=MatchValue(value=agent_id))
                )
            
            # Add project filter
            filter_conditions.append(
                FieldCondition(key="project_id", match=MatchValue(value=self.project_id))
            )
            
            search_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            collection_name = self.project_db.collections["conversations"]
            results = self.client.search(
                collection_name=collection_name,
                query_vector=[0.0] * 1536,  # Dummy vector for now
                query_filter=search_filter,
                limit=limit
            )
            
            return [result.payload for result in results]
            
        except Exception as e:
            logger.error(f"Failed to search conversations: {e}")
            return []
    
    async def search_knowledge(self, query: str, knowledge_type: str = None, 
                             limit: int = 10) -> List[Dict[str, Any]]:
        """Search knowledge base in project-specific database."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
        try:
            # Build filter
            filter_conditions = [
                FieldCondition(key="project_id", match=MatchValue(value=self.project_id))
            ]
            
            if knowledge_type:
                filter_conditions.append(
                    FieldCondition(key="knowledge_type", match=MatchValue(value=knowledge_type))
                )
            
            search_filter = Filter(must=filter_conditions)
            
            collection_name = self.project_db.collections["knowledge"]
            results = self.client.search(
                collection_name=collection_name,
                query_vector=[0.0] * 1536,  # Dummy vector for now
                query_filter=search_filter,
                limit=limit
            )
            
            return [result.payload for result in results]
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return []
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics for the project."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
        try:
            stats = {}
            for collection_type, collection_name in self.project_db.collections.items():
                try:
                    collection_info = self.client.get_collection(collection_name)
                    stats[collection_type] = {
                        "name": collection_name,
                        "points_count": collection_info.points_count,
                        "vectors_count": collection_info.vectors_count,
                        "indexed_vectors_count": collection_info.indexed_vectors_count
                    }
                except Exception as e:
                    stats[collection_type] = {
                        "name": collection_name,
                        "error": str(e)
                    }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {}
    
    def switch_project(self, project_id: str):
        """Switch to a different project database."""
        self.project_id = project_id
        self._initialize_project_database()
    
    async def initialize_predetermined_knowledge(self):
        """Initialize predetermined knowledge bases for the project."""
        if not self.is_connected or not self.project_db:
            raise Exception("Vector store not connected to project database")
        
        # PDCA Framework knowledge
        pdca_knowledge = KnowledgeBase(
            id=str(uuid.uuid4()),
            project_id=self.project_id,
            knowledge_type="pdca",
            title="PDCA Framework",
            content="Plan-Do-Check-Act (PDCA) is a four-step management method for continuous improvement...",
            tags=["framework", "improvement", "management"],
            metadata={"source": "predetermined", "version": "1.0"},
            timestamp=datetime.now()
        )
        
        # Agile/Scrum knowledge
        agile_knowledge = KnowledgeBase(
            id=str(uuid.uuid4()),
            project_id=self.project_id,
            knowledge_type="agile",
            title="Agile/Scrum Methodology",
            content="Agile is an iterative approach to project management and software development...",
            tags=["agile", "scrum", "methodology", "development"],
            metadata={"source": "predetermined", "version": "1.0"},
            timestamp=datetime.now()
        )
        
        # Store predetermined knowledge
        await self.store_knowledge(pdca_knowledge)
        await self.store_knowledge(agile_knowledge)
        
        logger.info(f"Initialized predetermined knowledge for project {self.project_id}")


# Global enhanced vector store instance
enhanced_vector_store = None

def get_enhanced_vector_store(project_id: str = None) -> EnhancedVectorStore:
    """Get the global enhanced vector store."""
    global enhanced_vector_store
    if enhanced_vector_store is None or (project_id and enhanced_vector_store.project_id != project_id):
        enhanced_vector_store = EnhancedVectorStore(project_id=project_id)
    return enhanced_vector_store
