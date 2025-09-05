"""MCP tools for Phase 9.4: Predetermined Knowledge Bases."""

import logging
from typing import Dict, Any, List
import asyncio
from datetime import datetime

from ..knowledge.predetermined_knowledge import get_predetermined_knowledge, KnowledgeItem

logger = logging.getLogger(__name__)


class Phase9_4MCPTools:
    """MCP tools for Phase 9.4 predetermined knowledge bases."""
    
    def __init__(self):
        self.knowledge_base = None
    
    def _ensure_initialized(self):
        """Ensure knowledge base is initialized."""
        if not self.knowledge_base:
            self.knowledge_base = get_predetermined_knowledge()
    
    async def get_available_knowledge_domains(self) -> Dict[str, Any]:
        """Get available knowledge domains."""
        try:
            self._ensure_initialized()
            domains = self.knowledge_base.get_available_domains()
            
            return {
                "success": True,
                "domains": domains,
                "count": len(domains),
                "message": f"Retrieved {len(domains)} knowledge domains"
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge domains: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve knowledge domains"
            }
    
    async def get_knowledge_for_domain(self, domain: str) -> Dict[str, Any]:
        """Get knowledge items for a specific domain."""
        try:
            self._ensure_initialized()
            knowledge_items = self.knowledge_base.get_knowledge_for_domain(domain)
            
            # Convert KnowledgeItem objects to dictionaries
            items_data = []
            for item in knowledge_items:
                items_data.append({
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "tags": item.tags,
                    "priority": item.priority,
                    "source": item.source,
                    "version": item.version,
                    "last_updated": item.last_updated
                })
            
            return {
                "success": True,
                "domain": domain,
                "items": items_data,
                "count": len(items_data),
                "message": f"Retrieved {len(items_data)} knowledge items for domain '{domain}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge for domain {domain}: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve knowledge for domain '{domain}'"
            }
    
    async def get_all_knowledge(self) -> Dict[str, Any]:
        """Get all knowledge bases."""
        try:
            self._ensure_initialized()
            all_knowledge = self.knowledge_base.get_all_knowledge()
            
            # Convert to serializable format
            knowledge_data = {}
            total_items = 0
            
            for domain, items in all_knowledge.items():
                items_data = []
                for item in items:
                    items_data.append({
                        "title": item.title,
                        "content": item.content,
                        "category": item.category,
                        "subcategory": item.subcategory,
                        "tags": item.tags,
                        "priority": item.priority,
                        "source": item.source,
                        "version": item.version,
                        "last_updated": item.last_updated
                    })
                knowledge_data[domain] = {
                    "items": items_data,
                    "count": len(items_data)
                }
                total_items += len(items_data)
            
            return {
                "success": True,
                "knowledge_bases": knowledge_data,
                "total_items": total_items,
                "domains": list(knowledge_data.keys()),
                "message": f"Retrieved all knowledge bases with {total_items} total items"
            }
            
        except Exception as e:
            logger.error(f"Failed to get all knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve all knowledge bases"
            }
    
    async def search_knowledge(self, query: str, domain: str = None, category: str = None, 
                              priority: str = None) -> Dict[str, Any]:
        """Search knowledge items by query and filters."""
        try:
            self._ensure_initialized()
            
            # Get knowledge to search
            if domain:
                knowledge_items = self.knowledge_base.get_knowledge_for_domain(domain)
            else:
                all_knowledge = self.knowledge_base.get_all_knowledge()
                knowledge_items = []
                for items in all_knowledge.values():
                    knowledge_items.extend(items)
            
            # Filter and search
            results = []
            query_lower = query.lower()
            
            for item in knowledge_items:
                # Apply filters
                if category and item.category != category:
                    continue
                if priority and item.priority != priority:
                    continue
                
                # Search in content
                if (query_lower in item.title.lower() or 
                    query_lower in item.content.lower() or
                    any(query_lower in tag.lower() for tag in item.tags)):
                    
                    results.append({
                        "title": item.title,
                        "content": item.content[:200] + "..." if len(item.content) > 200 else item.content,
                        "category": item.category,
                        "subcategory": item.subcategory,
                        "tags": item.tags,
                        "priority": item.priority,
                        "source": item.source,
                        "domain": domain or "all"
                    })
            
            return {
                "success": True,
                "query": query,
                "filters": {
                    "domain": domain,
                    "category": category,
                    "priority": priority
                },
                "results": results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge items matching query"
            }
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to search knowledge with query '{query}'"
            }
    
    async def get_knowledge_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            self._ensure_initialized()
            all_knowledge = self.knowledge_base.get_all_knowledge()
            
            # Calculate statistics
            total_items = 0
            domain_stats = {}
            category_stats = {}
            priority_stats = {}
            tag_stats = {}
            
            for domain, items in all_knowledge.items():
                domain_stats[domain] = len(items)
                total_items += len(items)
                
                for item in items:
                    # Category statistics
                    category_stats[item.category] = category_stats.get(item.category, 0) + 1
                    
                    # Priority statistics
                    priority_stats[item.priority] = priority_stats.get(item.priority, 0) + 1
                    
                    # Tag statistics
                    for tag in item.tags:
                        tag_stats[tag] = tag_stats.get(tag, 0) + 1
            
            # Sort by count
            top_categories = sorted(category_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            top_priorities = sorted(priority_stats.items(), key=lambda x: x[1], reverse=True)
            top_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "success": True,
                "statistics": {
                    "total_items": total_items,
                    "total_domains": len(domain_stats),
                    "domain_breakdown": domain_stats,
                    "category_breakdown": category_stats,
                    "priority_breakdown": priority_stats,
                    "top_categories": top_categories,
                    "top_priorities": top_priorities,
                    "top_tags": top_tags
                },
                "message": f"Retrieved statistics for {total_items} knowledge items across {len(domain_stats)} domains"
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge statistics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve knowledge statistics"
            }
    
    async def initialize_project_knowledge(self, project_id: str, domains: List[str] = None) -> Dict[str, Any]:
        """Initialize predetermined knowledge for a project."""
        try:
            self._ensure_initialized()
            
            # If no domains specified, use all available domains
            if not domains:
                domains = self.knowledge_base.get_available_domains()
            
            # Get knowledge items for specified domains
            knowledge_items = []
            for domain in domains:
                domain_items = self.knowledge_base.get_knowledge_for_domain(domain)
                knowledge_items.extend(domain_items)
            
            # Convert to format suitable for storage
            knowledge_data = []
            for item in knowledge_items:
                knowledge_data.append({
                    "title": item.title,
                    "content": item.content,
                    "category": item.category,
                    "subcategory": item.subcategory,
                    "tags": item.tags,
                    "priority": item.priority,
                    "source": item.source,
                    "version": item.version,
                    "last_updated": item.last_updated,
                    "domain": domains[0] if len(domains) == 1 else "multiple"
                })
            
            return {
                "success": True,
                "project_id": project_id,
                "domains": domains,
                "knowledge_items": knowledge_data,
                "count": len(knowledge_data),
                "message": f"Initialized {len(knowledge_data)} knowledge items for project '{project_id}' from {len(domains)} domains"
            }
            
        except Exception as e:
            logger.error(f"Failed to initialize project knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to initialize knowledge for project '{project_id}'"
            }
    
    async def get_knowledge_by_category(self, category: str) -> Dict[str, Any]:
        """Get knowledge items by category."""
        try:
            self._ensure_initialized()
            all_knowledge = self.knowledge_base.get_all_knowledge()
            
            results = []
            for domain, items in all_knowledge.items():
                for item in items:
                    if item.category == category:
                        results.append({
                            "title": item.title,
                            "content": item.content,
                            "category": item.category,
                            "subcategory": item.subcategory,
                            "tags": item.tags,
                            "priority": item.priority,
                            "source": item.source,
                            "domain": domain
                        })
            
            return {
                "success": True,
                "category": category,
                "items": results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge items in category '{category}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge by category: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve knowledge for category '{category}'"
            }
    
    async def get_knowledge_by_priority(self, priority: str) -> Dict[str, Any]:
        """Get knowledge items by priority."""
        try:
            self._ensure_initialized()
            all_knowledge = self.knowledge_base.get_all_knowledge()
            
            results = []
            for domain, items in all_knowledge.items():
                for item in items:
                    if item.priority == priority:
                        results.append({
                            "title": item.title,
                            "content": item.content,
                            "category": item.category,
                            "subcategory": item.subcategory,
                            "tags": item.tags,
                            "priority": item.priority,
                            "source": item.source,
                            "domain": domain
                        })
            
            return {
                "success": True,
                "priority": priority,
                "items": results,
                "count": len(results),
                "message": f"Found {len(results)} knowledge items with priority '{priority}'"
            }
            
        except Exception as e:
            logger.error(f"Failed to get knowledge by priority: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to retrieve knowledge for priority '{priority}'"
            }


# Global instance for synchronous access
_phase9_4_tools = None

def get_phase9_4_tools():
    """Get the global Phase9_4MCPTools instance."""
    global _phase9_4_tools
    if _phase9_4_tools is None:
        _phase9_4_tools = Phase9_4MCPTools()
    return _phase9_4_tools


# Synchronous wrapper functions for MCP server
def get_available_knowledge_domains() -> Dict[str, Any]:
    """Get available knowledge domains (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_available_knowledge_domains())

def get_knowledge_for_domain(domain: str) -> Dict[str, Any]:
    """Get knowledge items for a specific domain (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_knowledge_for_domain(domain))

def get_all_knowledge() -> Dict[str, Any]:
    """Get all knowledge bases (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_all_knowledge())

def search_knowledge(query: str, domain: str = None, category: str = None, priority: str = None) -> Dict[str, Any]:
    """Search knowledge items by query and filters (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.search_knowledge(query, domain, category, priority))

def get_knowledge_statistics() -> Dict[str, Any]:
    """Get statistics about the knowledge base (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_knowledge_statistics())

def initialize_project_knowledge(project_id: str, domains: List[str] = None) -> Dict[str, Any]:
    """Initialize predetermined knowledge for a project (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.initialize_project_knowledge(project_id, domains))

def get_knowledge_by_category(category: str) -> Dict[str, Any]:
    """Get knowledge items by category (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_knowledge_by_category(category))

def get_knowledge_by_priority(priority: str) -> Dict[str, Any]:
    """Get knowledge items by priority (synchronous wrapper)."""
    tools = get_phase9_4_tools()
    return asyncio.run(tools.get_knowledge_by_priority(priority))
