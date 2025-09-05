"""MCP tools for Phase 9.1: Project-Specific Qdrant Databases."""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from ..database import get_enhanced_vector_store, get_project_manager, get_docker_manager

logger = logging.getLogger(__name__)

# Global instance for synchronous access
_phase9_tools = None

def get_phase9_tools():
    """Get the global Phase9MCPTools instance."""
    global _phase9_tools
    if _phase9_tools is None:
        _phase9_tools = Phase9MCPTools()
    return _phase9_tools


class Phase9MCPTools:
    """MCP tools for Phase 9.1 project-specific Qdrant databases."""
    
    def __init__(self):
        self.enhanced_vector_store = None
        self.project_manager = None
        self.docker_manager = None
    
    def _ensure_initialized(self):
        """Ensure components are initialized."""
        if not self.enhanced_vector_store:
            self.enhanced_vector_store = get_enhanced_vector_store()
        if not self.project_manager:
            self.project_manager = get_project_manager()
        if not self.docker_manager:
            self.docker_manager = get_docker_manager()
    
    async def start_qdrant_container(self) -> Dict[str, Any]:
        """Start Qdrant Docker container."""
        try:
            self._ensure_initialized()
            
            success = await self.docker_manager.start_qdrant()
            status = await self.docker_manager.get_qdrant_status()
            
            return {
                "success": success,
                "status": status,
                "message": "Qdrant container started successfully" if success else "Failed to start Qdrant container"
            }
            
        except Exception as e:
            logger.error(f"Failed to start Qdrant container: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to start Qdrant container"
            }
    
    async def stop_qdrant_container(self) -> Dict[str, Any]:
        """Stop Qdrant Docker container."""
        try:
            self._ensure_initialized()
            
            success = await self.docker_manager.stop_qdrant()
            status = await self.docker_manager.get_qdrant_status()
            
            return {
                "success": success,
                "status": status,
                "message": "Qdrant container stopped successfully" if success else "Failed to stop Qdrant container"
            }
            
        except Exception as e:
            logger.error(f"Failed to stop Qdrant container: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to stop Qdrant container"
            }
    
    async def get_qdrant_status(self) -> Dict[str, Any]:
        """Get Qdrant container status."""
        try:
            self._ensure_initialized()
            
            status = await self.docker_manager.get_qdrant_status()
            
            return {
                "success": True,
                "status": status,
                "message": "Qdrant status retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Qdrant status: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get Qdrant status"
            }
    
    async def create_project_database(self, project_name: str, project_id: str = None) -> Dict[str, Any]:
        """Create a new project-specific database."""
        try:
            self._ensure_initialized()
            
            project_db = await self.project_manager.create_project_database(project_name, project_id)
            
            return {
                "success": True,
                "project_id": project_db.project_id,
                "project_name": project_db.project_name,
                "database_name": project_db.database_name,
                "collections": project_db.collections,
                "message": f"Project database created successfully: {project_db.database_name}"
            }
            
        except Exception as e:
            logger.error(f"Failed to create project database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create project database"
            }
    
    async def list_project_databases(self) -> Dict[str, Any]:
        """List all project databases."""
        try:
            self._ensure_initialized()
            
            projects = await self.project_manager.list_projects()
            project_list = []
            
            for project in projects:
                project_list.append({
                    "project_id": project.project_id,
                    "project_name": project.project_name,
                    "database_name": project.database_name,
                    "status": project.status,
                    "created_at": project.created_at.isoformat(),
                    "last_accessed": project.last_accessed.isoformat(),
                    "collections": project.collections
                })
            
            return {
                "success": True,
                "projects": project_list,
                "count": len(project_list),
                "message": f"Retrieved {len(project_list)} project databases"
            }
            
        except Exception as e:
            logger.error(f"Failed to list project databases: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list project databases"
            }
    
    async def switch_project_database(self, project_id: str) -> Dict[str, Any]:
        """Switch to a different project database."""
        try:
            self._ensure_initialized()
            
            project_db = await self.project_manager.get_project_database(project_id)
            if not project_db:
                return {
                    "success": False,
                    "error": "Project not found",
                    "message": f"Project database {project_id} not found"
                }
            
            # Switch the enhanced vector store to the new project
            self.enhanced_vector_store.switch_project(project_id)
            
            return {
                "success": True,
                "project_id": project_db.project_id,
                "project_name": project_db.project_name,
                "database_name": project_db.database_name,
                "collections": project_db.collections,
                "message": f"Switched to project database: {project_db.database_name}"
            }
            
        except Exception as e:
            logger.error(f"Failed to switch project database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to switch project database"
            }
    
    async def archive_project_database(self, project_id: str) -> Dict[str, Any]:
        """Archive a project database."""
        try:
            self._ensure_initialized()
            
            success = await self.project_manager.archive_project(project_id)
            
            return {
                "success": success,
                "project_id": project_id,
                "message": f"Project database {project_id} archived successfully" if success else f"Failed to archive project database {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to archive project database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to archive project database"
            }
    
    async def restore_project_database(self, project_id: str) -> Dict[str, Any]:
        """Restore an archived project database."""
        try:
            self._ensure_initialized()
            
            success = await self.project_manager.restore_project(project_id)
            
            return {
                "success": success,
                "project_id": project_id,
                "message": f"Project database {project_id} restored successfully" if success else f"Failed to restore project database {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to restore project database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to restore project database"
            }
    
    async def delete_project_database(self, project_id: str, permanent: bool = False) -> Dict[str, Any]:
        """Delete a project database."""
        try:
            self._ensure_initialized()
            
            success = await self.project_manager.delete_project(project_id, permanent)
            
            return {
                "success": success,
                "project_id": project_id,
                "permanent": permanent,
                "message": f"Project database {project_id} deleted successfully" if success else f"Failed to delete project database {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Failed to delete project database: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to delete project database"
            }
    
    async def get_project_collection_stats(self, project_id: str = None) -> Dict[str, Any]:
        """Get collection statistics for a project."""
        try:
            self._ensure_initialized()
            
            if project_id:
                # Switch to specific project
                self.enhanced_vector_store.switch_project(project_id)
            
            stats = await self.enhanced_vector_store.get_collection_stats()
            
            return {
                "success": True,
                "project_id": project_id or self.enhanced_vector_store.project_id,
                "stats": stats,
                "message": "Collection statistics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get collection statistics"
            }
    
    async def initialize_predetermined_knowledge(self, project_id: str = None) -> Dict[str, Any]:
        """Initialize predetermined knowledge bases for a project."""
        try:
            self._ensure_initialized()
            
            if project_id:
                # Switch to specific project
                self.enhanced_vector_store.switch_project(project_id)
            
            await self.enhanced_vector_store.initialize_predetermined_knowledge()
            
            return {
                "success": True,
                "project_id": project_id or self.enhanced_vector_store.project_id,
                "message": "Predetermined knowledge bases initialized successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize predetermined knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize predetermined knowledge"
            }
    
    async def search_project_knowledge(self, query: str, knowledge_type: str = None, 
                                     project_id: str = None, limit: int = 10) -> Dict[str, Any]:
        """Search knowledge base in a project."""
        try:
            self._ensure_initialized()
            
            if project_id:
                # Switch to specific project
                self.enhanced_vector_store.switch_project(project_id)
            
            results = await self.enhanced_vector_store.search_knowledge(query, knowledge_type, limit)
            
            return {
                "success": True,
                "project_id": project_id or self.enhanced_vector_store.project_id,
                "query": query,
                "knowledge_type": knowledge_type,
                "results": results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge entries"
            }
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to search knowledge"
            }
    
    async def backup_project_data(self, project_id: str, backup_path: str) -> Dict[str, Any]:
        """Backup project data."""
        try:
            self._ensure_initialized()
            
            success = await self.docker_manager.backup_qdrant_data(backup_path)
            
            return {
                "success": success,
                "project_id": project_id,
                "backup_path": backup_path,
                "message": f"Project data backed up successfully to {backup_path}" if success else "Failed to backup project data"
            }
            
        except Exception as e:
            logger.error(f"Failed to backup project data: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to backup project data"
            }
    
    async def restore_project_data(self, project_id: str, backup_path: str) -> Dict[str, Any]:
        """Restore project data from backup."""
        try:
            self._ensure_initialized()
            
            success = await self.docker_manager.restore_qdrant_data(backup_path)
            
            return {
                "success": success,
                "project_id": project_id,
                "backup_path": backup_path,
                "message": f"Project data restored successfully from {backup_path}" if success else "Failed to restore project data"
            }
            
        except Exception as e:
            logger.error(f"Failed to restore project data: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to restore project data"
            }


# Synchronous wrapper functions for MCP server
def start_qdrant_container() -> Dict[str, Any]:
    """Start Qdrant Docker container (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.start_qdrant_container())

def stop_qdrant_container() -> Dict[str, Any]:
    """Stop Qdrant Docker container (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.stop_qdrant_container())

def get_qdrant_status() -> Dict[str, Any]:
    """Get Qdrant container status (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.get_qdrant_status())

def create_project_database(project_id: str, project_name: str, description: str = "") -> Dict[str, Any]:
    """Create a new project-specific Qdrant database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.create_project_database(project_name, project_id))

def list_project_databases() -> Dict[str, Any]:
    """List all project databases (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.list_project_databases())

def switch_project_database(project_id: str) -> Dict[str, Any]:
    """Switch to a specific project database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.switch_project_database(project_id))

def archive_project_database(project_id: str) -> Dict[str, Any]:
    """Archive a project database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.archive_project_database(project_id))

def restore_project_database(project_id: str) -> Dict[str, Any]:
    """Restore an archived project database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.restore_project_database(project_id))

def delete_project_database(project_id: str) -> Dict[str, Any]:
    """Delete a project database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.delete_project_database(project_id))

def get_project_collection_stats(project_id: str) -> Dict[str, Any]:
    """Get collection statistics for a project (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.get_project_collection_stats(project_id))

def initialize_predetermined_knowledge(project_id: str = None) -> Dict[str, Any]:
    """Initialize predetermined knowledge base for a project (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.initialize_predetermined_knowledge(project_id))

def search_project_knowledge(project_id: str, query: str, collection: str = "knowledge", limit: int = 10) -> Dict[str, Any]:
    """Search knowledge in a project database (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.search_project_knowledge(project_id, query, collection, limit))

def backup_project_data(project_id: str, backup_path: str = None) -> Dict[str, Any]:
    """Backup project data (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.backup_project_data(project_id, backup_path))

def restore_project_data(project_id: str, backup_path: str) -> Dict[str, Any]:
    """Restore project data (synchronous wrapper)."""
    tools = get_phase9_tools()
    return asyncio.run(tools.restore_project_data(project_id, backup_path))
