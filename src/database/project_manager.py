"""Project-specific Qdrant database manager for Phase 9.1."""

import logging
import os
import uuid
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import asyncio
import subprocess
import time

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None
    logging.error("Qdrant client not available. Install with: pip install qdrant-client")

logger = logging.getLogger(__name__)


@dataclass
class ProjectDatabase:
    """Project-specific database configuration."""
    project_id: str
    project_name: str
    database_name: str
    collections: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    status: str = "active"  # active, archived, deleted
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.collections:
            self.collections = {
                "conversations": f"{self.database_name}_conversations",
                "projects": f"{self.database_name}_projects", 
                "agents": f"{self.database_name}_agents",
                "knowledge": f"{self.database_name}_knowledge",
                "sprints": f"{self.database_name}_sprints",
                "documents": f"{self.database_name}_documents"
            }


class ProjectDatabaseManager:
    """Manages project-specific Qdrant databases."""
    
    def __init__(self, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant client not available. Install with: pip install qdrant-client")
        
        self.qdrant_host = qdrant_host
        self.qdrant_port = qdrant_port
        self.client: Optional[QdrantClient] = None
        self.projects: Dict[str, ProjectDatabase] = {}
        self.is_connected = False
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Qdrant connection."""
        try:
            self.client = QdrantClient(host=self.qdrant_host, port=self.qdrant_port)
            # Test connection
            self.client.get_collections()
            self.is_connected = True
            logger.info(f"Connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise Exception(f"Qdrant connection failed: {e}")
    
    async def create_project_database(self, project_name: str, project_id: str = None) -> ProjectDatabase:
        """Create a new project-specific database."""
        if not self.is_connected:
            raise Exception("Qdrant not connected")
        
        project_id = project_id or str(uuid.uuid4())
        database_name = f"project_{project_id}_{project_name.lower().replace(' ', '_')}"
        
        # Create project database configuration
        project_db = ProjectDatabase(
            project_id=project_id,
            project_name=project_name,
            database_name=database_name
        )
        
        # Create collections for this project
        await self._create_project_collections(project_db)
        
        # Store project metadata
        self.projects[project_id] = project_db
        await self._save_project_registry()
        
        logger.info(f"Created project database: {database_name}")
        return project_db
    
    async def _create_project_collections(self, project_db: ProjectDatabase):
        """Create all collections for a project."""
        vector_config = VectorParams(
            size=1536,  # OpenAI embedding size
            distance=Distance.COSINE
        )
        
        for collection_name, full_name in project_db.collections.items():
            try:
                self.client.recreate_collection(
                    collection_name=full_name,
                    vectors_config=vector_config
                )
                logger.info(f"Created collection: {full_name}")
            except Exception as e:
                logger.error(f"Failed to create collection {full_name}: {e}")
                raise
    
    async def get_project_database(self, project_id: str) -> Optional[ProjectDatabase]:
        """Get project database by ID."""
        if project_id in self.projects:
            project_db = self.projects[project_id]
            project_db.last_accessed = datetime.now()
            return project_db
        return None
    
    async def list_projects(self) -> List[ProjectDatabase]:
        """List all project databases."""
        return list(self.projects.values())
    
    async def archive_project(self, project_id: str) -> bool:
        """Archive a project database."""
        if project_id not in self.projects:
            return False
        
        project_db = self.projects[project_id]
        project_db.status = "archived"
        project_db.last_accessed = datetime.now()
        
        await self._save_project_registry()
        logger.info(f"Archived project: {project_db.project_name}")
        return True
    
    async def restore_project(self, project_id: str) -> bool:
        """Restore an archived project."""
        if project_id not in self.projects:
            return False
        
        project_db = self.projects[project_id]
        if project_db.status != "archived":
            return False
        
        project_db.status = "active"
        project_db.last_accessed = datetime.now()
        
        await self._save_project_registry()
        logger.info(f"Restored project: {project_db.project_name}")
        return True
    
    async def delete_project(self, project_id: str, permanent: bool = False) -> bool:
        """Delete a project database."""
        if project_id not in self.projects:
            return False
        
        project_db = self.projects[project_id]
        
        if permanent:
            # Permanently delete collections
            for collection_name in project_db.collections.values():
                try:
                    self.client.delete_collection(collection_name)
                    logger.info(f"Deleted collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"Failed to delete collection {collection_name}: {e}")
            
            # Remove from registry
            del self.projects[project_id]
            await self._save_project_registry()
            logger.info(f"Permanently deleted project: {project_db.project_name}")
        else:
            # Mark as deleted (soft delete)
            project_db.status = "deleted"
            project_db.last_accessed = datetime.now()
            await self._save_project_registry()
            logger.info(f"Soft deleted project: {project_db.project_name}")
        
        return True
    
    async def _save_project_registry(self):
        """Save project registry to Qdrant."""
        try:
            registry_data = {
                "projects": {
                    project_id: {
                        "project_id": project_db.project_id,
                        "project_name": project_db.project_name,
                        "database_name": project_db.database_name,
                        "collections": project_db.collections,
                        "created_at": project_db.created_at.isoformat(),
                        "last_accessed": project_db.last_accessed.isoformat(),
                        "status": project_db.status,
                        "metadata": project_db.metadata
                    }
                    for project_id, project_db in self.projects.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            
            # Store in a special registry collection
            registry_point = PointStruct(
                id="project_registry",
                vector=[0.0] * 1536,  # Dummy vector
                payload=registry_data
            )
            
            self.client.upsert(
                collection_name="project_registry",
                points=[registry_point]
            )
            
        except Exception as e:
            logger.error(f"Failed to save project registry: {e}")
    
    async def _load_project_registry(self):
        """Load project registry from Qdrant."""
        try:
            # Create registry collection if it doesn't exist
            try:
                self.client.get_collection("project_registry")
            except:
                self.client.create_collection(
                    collection_name="project_registry",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
            
            # Try to retrieve registry data
            result = self.client.retrieve(
                collection_name="project_registry",
                ids=["project_registry"]
            )
            
            if result:
                registry_data = result[0].payload
                projects_data = registry_data.get("projects", {})
                
                for project_id, project_data in projects_data.items():
                    project_db = ProjectDatabase(
                        project_id=project_data["project_id"],
                        project_name=project_data["project_name"],
                        database_name=project_data["database_name"],
                        collections=project_data["collections"],
                        created_at=datetime.fromisoformat(project_data["created_at"]),
                        last_accessed=datetime.fromisoformat(project_data["last_accessed"]),
                        status=project_data["status"],
                        metadata=project_data["metadata"]
                    )
                    self.projects[project_id] = project_db
                
                logger.info(f"Loaded {len(self.projects)} projects from registry")
            
        except Exception as e:
            logger.warning(f"Failed to load project registry: {e}")
            # Continue with empty registry
    
    def get_project_client(self, project_id: str) -> Optional[QdrantClient]:
        """Get Qdrant client for a specific project."""
        if not self.is_connected or project_id not in self.projects:
            return None
        
        # Return the same client but with project context
        return self.client
    
    def get_project_collections(self, project_id: str) -> Dict[str, str]:
        """Get collection names for a project."""
        if project_id not in self.projects:
            return {}
        
        return self.projects[project_id].collections


# Global project database manager instance
project_db_manager = None

def get_project_manager() -> ProjectDatabaseManager:
    """Get the global project database manager."""
    global project_db_manager
    if project_db_manager is None:
        project_db_manager = ProjectDatabaseManager()
    return project_db_manager
