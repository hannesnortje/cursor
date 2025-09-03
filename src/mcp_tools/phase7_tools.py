#!/usr/bin/env python3
"""MCP Tools for Phase 7 Advanced Features."""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from uuid import uuid4

from src.agents.dynamic_agent_manager import dynamic_agent_manager
from src.performance.performance_optimizer import performance_optimizer
from src.communication.advanced_communication import (
    advanced_communication, 
    AdvancedMessage, 
    MessagePriority, 
    MessageType,
    MessageFilter
)

logger = logging.getLogger(__name__)

class Phase7Tools:
    """MCP tools for Phase 7 advanced features."""
    
    def __init__(self):
        self.tools = {
            "dynamic_agent_management": self.dynamic_agent_management,
            "performance_optimization": self.performance_optimization,
            "advanced_communication": self.advanced_communication,
            "system_health_check": self.system_health_check
        }
    
    async def dynamic_agent_management(self, action: str, **kwargs) -> Dict[str, Any]:
        """Dynamic agent management tools."""
        try:
            if action == "discover_agents":
                # Add discovery paths and discover agents
                discovery_paths = kwargs.get("discovery_paths", ["src/agents"])
                for path in discovery_paths:
                    await dynamic_agent_manager.add_discovery_path(path)
                
                discovered = await dynamic_agent_manager.discover_agents()
                return {
                    "success": True,
                    "discovered_agents": discovered,
                    "message": f"Discovered {len(discovered)} potential agent classes"
                }
            
            elif action == "load_agent":
                # Load a specific agent
                agent_class_path = kwargs.get("agent_class_path")
                if not agent_class_path:
                    return {"success": False, "error": "agent_class_path required"}
                
                agent_info = await dynamic_agent_manager.load_agent(agent_class_path, **kwargs)
                if agent_info:
                    return {
                        "success": True,
                        "agent_info": {
                            "name": agent_info.name,
                            "status": agent_info.status.value,
                            "agent_type": agent_info.agent_type.value
                        },
                        "message": f"Agent {agent_info.name} loaded successfully"
                    }
                else:
                    return {"success": False, "error": "Failed to load agent"}
            
            elif action == "list_agents":
                # List all managed agents
                agents = await dynamic_agent_manager.list_agents()
                return {
                    "success": True,
                    "agents": [
                        {
                            "name": agent.name,
                            "status": agent.status.value,
                            "agent_type": agent.agent_type.value,
                            "load_time": agent.load_time
                        }
                        for agent in agents
                    ],
                    "total": len(agents)
                }
            
            elif action == "health_check":
                # Get agent health status
                health = await dynamic_agent_manager.health_check()
                return {
                    "success": True,
                    "health": health
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Dynamic agent management error: {e}")
            return {"success": False, "error": str(e)}
    
    async def performance_optimization(self, action: str, **kwargs) -> Dict[str, Any]:
        """Performance optimization tools."""
        try:
            if action == "cache_operations":
                # Cache operations
                operation = kwargs.get("operation")
                key = kwargs.get("key")
                value = kwargs.get("value")
                ttl = kwargs.get("ttl")
                
                if operation == "get":
                    result = performance_optimizer.cache_get(key)
                    return {
                        "success": True,
                        "operation": "get",
                        "key": key,
                        "value": result,
                        "found": result is not None
                    }
                
                elif operation == "put":
                    performance_optimizer.cache_put(key, value, ttl)
                    return {
                        "success": True,
                        "operation": "put",
                        "key": key,
                        "message": "Value cached successfully"
                    }
                
                elif operation == "clear":
                    performance_optimizer.cache.clear()
                    return {
                        "success": True,
                        "operation": "clear",
                        "message": "Cache cleared successfully"
                    }
                
                else:
                    return {"success": False, "error": f"Unknown cache operation: {operation}"}
            
            elif action == "resource_monitoring":
                # Resource monitoring
                resource = kwargs.get("resource")
                usage = kwargs.get("usage")
                
                if usage is not None:
                    performance_optimizer.resource_manager.record_usage(resource, usage)
                    return {
                        "success": True,
                        "message": f"Resource usage recorded for {resource}"
                    }
                
                current_usage = performance_optimizer.resource_manager.get_usage(resource)
                history = performance_optimizer.resource_manager.get_usage_history(resource)
                
                return {
                    "success": True,
                    "resource": resource,
                    "current_usage": current_usage,
                    "history": history[-10:] if history else []  # Last 10 entries
                }
            
            elif action == "load_balancing":
                # Load balancer operations
                operation = kwargs.get("operation")
                worker = kwargs.get("worker")
                
                if operation == "add_worker":
                    performance_optimizer.load_balancer.add_worker(worker)
                    return {
                        "success": True,
                        "message": "Worker added to load balancer"
                    }
                
                elif operation == "get_worker":
                    worker = performance_optimizer.load_balancer.get_next_worker()
                    return {
                        "success": True,
                        "worker": str(worker) if worker else None
                    }
                
                else:
                    return {"success": False, "error": f"Unknown load balancer operation: {operation}"}
            
            elif action == "metrics":
                # Performance metrics
                metric = kwargs.get("metric")
                value = kwargs.get("value")
                
                if value is not None:
                    performance_optimizer.record_metric(metric, value)
                    return {
                        "success": True,
                        "message": f"Metric {metric} recorded"
                    }
                
                stats = performance_optimizer.get_metric_stats(metric)
                return {
                    "success": True,
                    "metric": metric,
                    "stats": stats
                }
            
            elif action == "system_status":
                # Get overall system status
                status = performance_optimizer.get_system_status()
                return {
                    "success": True,
                    "status": status
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Performance optimization error: {e}")
            return {"success": False, "error": str(e)}
    
    async def advanced_communication(self, action: str, **kwargs) -> Dict[str, Any]:
        """Advanced communication tools."""
        try:
            if action == "send_message":
                # Send a message through the advanced system
                message_id = str(uuid4())
                message = AdvancedMessage(
                    id=message_id,
                    content=kwargs.get("content", ""),
                    sender=kwargs.get("sender", "system"),
                    recipients=kwargs.get("recipients", []),
                    message_type=MessageType(kwargs.get("message_type", "system")),
                    priority=MessagePriority(kwargs.get("priority", 2)),
                    timestamp=time.time(),
                    ttl=kwargs.get("ttl"),
                    compression=kwargs.get("compression", False)
                )
                
                success = await advanced_communication.send_message(message)
                return {
                    "success": success,
                    "message_id": message_id,
                    "message": "Message sent successfully" if success else "Failed to send message"
                }
            
            elif action == "add_filter":
                # Add a message filter
                filter_type = kwargs.get("filter_type")
                message_type = kwargs.get("message_type", "system")
                
                if filter_type == "rate_limit":
                    max_messages = kwargs.get("max_messages_per_second", 100)
                    filter_func = await MessageFilter.rate_limit_filter(max_messages)
                    advanced_communication.add_filter(message_type, filter_func)
                
                elif filter_type == "size":
                    max_size = kwargs.get("max_size", 1024 * 1024)
                    filter_func = await MessageFilter.size_filter(max_size)
                    advanced_communication.add_filter(message_type, filter_func)
                
                elif filter_type == "content":
                    patterns = kwargs.get("forbidden_patterns", [])
                    filter_func = await MessageFilter.content_filter(patterns)
                    advanced_communication.add_filter(message_type, filter_func)
                
                else:
                    return {"success": False, "error": f"Unknown filter type: {filter_type}"}
                
                return {
                    "success": True,
                    "message": f"Filter {filter_type} added for {message_type} messages"
                }
            
            elif action == "add_route":
                # Add a message route handler
                message_type = kwargs.get("message_type", "system")
                handler_name = kwargs.get("handler_name", "default")
                
                # For now, we'll add a simple logging handler
                async def log_handler(message: AdvancedMessage):
                    logger.info(f"Message {message.id} routed to {handler_name}: {message.content}")
                
                advanced_communication.add_route(message_type, log_handler)
                
                return {
                    "success": True,
                    "message": f"Route handler {handler_name} added for {message_type} messages"
                }
            
            elif action == "get_stats":
                # Get communication system statistics
                stats = advanced_communication.get_stats()
                return {
                    "success": True,
                    "stats": stats
                }
            
            elif action == "start":
                # Start the advanced communication system
                await advanced_communication.start()
                return {
                    "success": True,
                    "message": "Advanced communication system started"
                }
            
            elif action == "stop":
                # Stop the advanced communication system
                await advanced_communication.stop()
                return {
                    "success": True,
                    "message": "Advanced communication system stopped"
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
                
        except Exception as e:
            logger.error(f"Advanced communication error: {e}")
            return {"success": False, "error": str(e)}
    
    async def system_health_check(self) -> Dict[str, Any]:
        """Comprehensive system health check."""
        try:
            # Agent health
            agent_health = await dynamic_agent_manager.health_check()
            
            # Performance status
            perf_status = performance_optimizer.get_system_status()
            
            # Communication stats
            comm_stats = advanced_communication.get_stats()
            
            # Overall health assessment
            overall_health = "healthy"
            issues = []
            
            # Check for agent errors
            if agent_health.get("errors"):
                overall_health = "degraded"
                issues.extend([f"Agent error: {e['error']}" for e in agent_health["errors"]])
            
            # Check resource limits
            for resource, usage in perf_status.get("resources", {}).items():
                if performance_optimizer.resource_manager.is_over_limit(resource):
                    overall_health = "degraded"
                    issues.append(f"Resource {resource} over limit: {usage}")
            
            # Check communication system
            if not advanced_communication._processing_task or advanced_communication._processing_task.done():
                overall_health = "degraded"
                issues.append("Communication system not running")
            
            return {
                "success": True,
                "overall_health": overall_health,
                "timestamp": time.time(),
                "agent_health": agent_health,
                "performance_status": perf_status,
                "communication_stats": comm_stats,
                "issues": issues,
                "summary": {
                    "total_agents": agent_health.get("total_agents", 0),
                    "cache_size": perf_status.get("cache", {}).get("size", 0),
                    "messages_processed": comm_stats.get("messages_received", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"System health check error: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_health": "error"
            }

# Global instance
phase7_tools = Phase7Tools()
