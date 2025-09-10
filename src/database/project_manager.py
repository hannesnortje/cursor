"""Project-specific Qdrant database manager for Phase 9.1 with fallbacks."""

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

# Try to import Qdrant with fallback
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct

    QDRANT_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Qdrant client available")
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None
    logger = logging.getLogger(__name__)
    logger.warning("Qdrant client not available - using in-memory fallback")

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
                "documents": f"{self.database_name}_documents",
            }


class InMemoryProjectStore:
    """In-memory fallback for project database storage."""

    def __init__(self):
        self.projects: Dict[str, ProjectDatabase] = {}
        self.collections: Dict[str, Dict[str, Any]] = {}
        logger.info("Initialized in-memory project store fallback")

    def create_project(
        self, project_id: str, project_name: str, database_name: str
    ) -> ProjectDatabase:
        """Create a new project database."""
        project = ProjectDatabase(
            project_id=project_id,
            project_name=project_name,
            database_name=database_name,
        )
        self.projects[project_id] = project
        self.collections[database_name] = {}
        logger.info(f"Created project {project_name} in memory store")
        return project

    def get_project(self, project_id: str) -> Optional[ProjectDatabase]:
        """Get project by ID."""
        return self.projects.get(project_id)

    def list_projects(self) -> List[ProjectDatabase]:
        """List all projects."""
        return list(self.projects.values())

    def archive_project(self, project_id: str) -> bool:
        """Archive a project."""
        if project_id in self.projects:
            self.projects[project_id].status = "archived"
            return True
        return False

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        if project_id in self.projects:
            del self.projects[project_id]
            return True
        return False


class ProjectDatabaseManager:
    """Manager for project-specific Qdrant databases with fallback support."""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant_url = qdrant_url
        self.client = None
        self.in_memory_store = InMemoryProjectStore()
        self.fallback_mode = False

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

    def create_project_database(
        self, project_name: str, project_id: str = None
    ) -> ProjectDatabase:
        """Create a new project-specific database."""
        if not project_id:
            project_id = str(uuid.uuid4())

        database_name = f"project_{project_id.replace('-', '_')}"

        if self.fallback_mode:
            return self.in_memory_store.create_project(
                project_id, project_name, database_name
            )

        try:
            # Create project database
            project = ProjectDatabase(
                project_id=project_id,
                project_name=project_name,
                database_name=database_name,
            )

            # Create collections in Qdrant
            for collection_name, full_name in project.collections.items():
                try:
                    self.client.create_collection(
                        collection_name=full_name,
                        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                    )
                    logger.info(f"Created collection {full_name}")
                except Exception as e:
                    logger.warning(f"Failed to create collection {full_name}: {e}")

            logger.info(f"Created project database {database_name} for {project_name}")
            return project

        except Exception as e:
            logger.error(f"Failed to create project database: {e}")
            logger.info("Falling back to in-memory storage")
            self.fallback_mode = True
            return self.in_memory_store.create_project(
                project_id, project_name, database_name
            )

    def get_project_database(self, project_id: str) -> Optional[ProjectDatabase]:
        """Get project database by ID."""
        if self.fallback_mode:
            return self.in_memory_store.get_project(project_id)

        # In Qdrant mode, we'd need to store project metadata
        # For now, return None and let the caller handle it
        return None

    def list_project_databases(self) -> List[ProjectDatabase]:
        """List all project databases."""
        if self.fallback_mode:
            return self.in_memory_store.list_projects()

        # In Qdrant mode, we'd need to query stored project metadata
        # For now, return empty list
        return []

    def archive_project_database(self, project_id: str) -> bool:
        """Archive a project database."""
        if self.fallback_mode:
            return self.in_memory_store.archive_project(project_id)

        # In Qdrant mode, we'd update project metadata
        # For now, return False
        return False

    def delete_project_database(self, project_id: str) -> bool:
        """Delete a project database."""
        if self.fallback_mode:
            return self.in_memory_store.delete_project(project_id)

        # In Qdrant mode, we'd delete collections and metadata
        # For now, return False
        return False

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        if self.fallback_mode:
            projects = self.in_memory_store.list_projects()
            return {
                "mode": "in_memory_fallback",
                "total_projects": len(projects),
                "active_projects": len([p for p in projects if p.status == "active"]),
                "archived_projects": len(
                    [p for p in projects if p.status == "archived"]
                ),
                "qdrant_available": False,
            }

        try:
            collections = self.client.get_collections()
            return {
                "mode": "qdrant",
                "total_collections": len(collections.collections),
                "qdrant_url": self.qdrant_url,
                "qdrant_available": True,
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {"mode": "error", "error": str(e), "qdrant_available": False}


# Global instance
_project_manager = None


def get_project_manager() -> ProjectDatabaseManager:
    """Get the global project manager instance."""
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectDatabaseManager()
    return _project_manager
