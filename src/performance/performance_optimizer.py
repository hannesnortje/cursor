#!/usr/bin/env python3
"""Performance Optimization System for Phase 7.2."""

import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import weakref

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy enumeration."""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    NONE = "none"

@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl is None:
            return False
        return time.time() > self.created_at + self.ttl
    
    def access(self):
        """Mark entry as accessed."""
        self.last_accessed = time.time()
        self.access_count += 1

class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: deque = deque()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            if entry.is_expired():
                del self.cache[key]
                self.access_order.remove(key)
                return None
            
            entry.access()
            # Move to front (most recently used)
            self.access_order.remove(key)
            self.access_order.appendleft(key)
            return entry.value
        return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None):
        """Put value in cache."""
        if key in self.cache:
            # Update existing entry
            self.cache[key].value = value
            self.cache[key].ttl = ttl
            self.access_order.remove(key)
            self.access_order.appendleft(key)
        else:
            # Add new entry
            if len(self.cache) >= self.max_size:
                # Remove least recently used
                lru_key = self.access_order.pop()
                del self.cache[lru_key]
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl
            )
            self.cache[key] = entry
            self.access_order.appendleft(key)
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self.access_order.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

class ConnectionPool:
    """Connection pooling for database and external services."""
    
    def __init__(self, max_connections: int = 10, max_idle: int = 5):
        self.max_connections = max_connections
        self.max_idle = max_idle
        self.active_connections: List[Any] = []
        self.idle_connections: deque = deque()
        self._lock = asyncio.Lock()
    
    async def get_connection(self) -> Any:
        """Get a connection from the pool."""
        async with self._lock:
            if self.idle_connections:
                return self.idle_connections.popleft()
            elif len(self.active_connections) < self.max_connections:
                # Create new connection
                connection = await self._create_connection()
                self.active_connections.append(connection)
                return connection
            else:
                # Wait for a connection to become available
                while not self.idle_connections and len(self.active_connections) >= self.max_connections:
                    await asyncio.sleep(0.1)
                return await self.get_connection()
    
    async def return_connection(self, connection: Any):
        """Return a connection to the pool."""
        async with self._lock:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
                
                if len(self.idle_connections) < self.max_idle:
                    self.idle_connections.append(connection)
                else:
                    await self._close_connection(connection)
    
    async def _create_connection(self) -> Any:
        """Create a new connection (to be implemented by subclasses)."""
        raise NotImplementedError
    
    async def _close_connection(self, connection: Any):
        """Close a connection (to be implemented by subclasses)."""
        raise NotImplementedError

class ResourceManager:
    """Resource management and monitoring."""
    
    def __init__(self):
        self.resource_usage: Dict[str, float] = defaultdict(float)
        self.resource_limits: Dict[str, float] = {}
        self.usage_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def set_resource_limit(self, resource: str, limit: float):
        """Set resource limit."""
        self.resource_limits[resource] = limit
    
    def record_usage(self, resource: str, usage: float):
        """Record resource usage."""
        self.resource_usage[resource] = usage
        self.usage_history[resource].append((time.time(), usage))
    
    def get_usage(self, resource: str) -> float:
        """Get current resource usage."""
        return self.resource_usage.get(resource, 0.0)
    
    def is_over_limit(self, resource: str) -> bool:
        """Check if resource usage is over limit."""
        limit = self.resource_limits.get(resource)
        if limit is None:
            return False
        return self.resource_usage.get(resource, 0.0) > limit
    
    def get_usage_history(self, resource: str) -> List[tuple]:
        """Get resource usage history."""
        return list(self.usage_history[resource])
    
    async def start_monitoring(self):
        """Start resource monitoring."""
        if self._monitoring_task is None:
            self._monitoring_task = asyncio.create_task(self._monitor_resources())
    
    async def stop_monitoring(self):
        """Stop resource monitoring."""
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
    
    async def _monitor_resources(self):
        """Monitor resource usage."""
        while True:
            try:
                # Record current resource usage
                for resource in self.resource_usage:
                    # Here you could add actual resource monitoring
                    # For now, we'll just maintain the existing data
                    pass
                
                await asyncio.sleep(5)  # Monitor every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in resource monitoring: {e}")
                await asyncio.sleep(5)

class LoadBalancer:
    """Simple load balancer for distributing work."""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.workers: List[Any] = []
        self.current_worker_index = 0
        self.worker_loads: Dict[int, int] = defaultdict(int)
    
    def add_worker(self, worker: Any):
        """Add a worker to the load balancer."""
        self.workers.append(worker)
        self.worker_loads[len(self.workers) - 1] = 0
    
    def remove_worker(self, worker: Any):
        """Remove a worker from the load balancer."""
        if worker in self.workers:
            index = self.workers.index(worker)
            del self.workers[index]
            del self.worker_loads[index]
            # Reindex remaining workers
            new_worker_loads = {}
            for i, load in enumerate(self.worker_loads.values()):
                new_worker_loads[i] = load
            self.worker_loads = new_worker_loads
    
    def get_next_worker(self) -> Optional[Any]:
        """Get the next worker based on strategy."""
        if not self.workers:
            return None
        
        if self.strategy == "round_robin":
            worker = self.workers[self.current_worker_index]
            self.current_worker_index = (self.current_worker_index + 1) % len(self.workers)
            return worker
        
        elif self.strategy == "least_loaded":
            # Find worker with lowest load
            min_load = float('inf')
            min_worker_index = 0
            
            for i, load in self.worker_loads.items():
                if load < min_load:
                    min_load = load
                    min_worker_index = i
            
            return self.workers[min_worker_index]
        
        else:
            # Default to first worker
            return self.workers[0]
    
    def record_work_start(self, worker: Any):
        """Record that work has started on a worker."""
        if worker in self.workers:
            index = self.workers.index(worker)
            self.worker_loads[index] += 1
    
    def record_work_complete(self, worker: Any):
        """Record that work has completed on a worker."""
        if worker in self.workers:
            index = self.workers.index(worker)
            self.worker_loads[index] = max(0, self.worker_loads[index] - 1)

class PerformanceOptimizer:
    """Main performance optimization system."""
    
    def __init__(self):
        self.cache = LRUCache()
        self.resource_manager = ResourceManager()
        self.load_balancer = LoadBalancer()
        self.connection_pools: Dict[str, ConnectionPool] = {}
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
    
    def add_connection_pool(self, name: str, pool: ConnectionPool):
        """Add a connection pool."""
        self.connection_pools[name] = pool
    
    def get_connection_pool(self, name: str) -> Optional[ConnectionPool]:
        """Get a connection pool by name."""
        return self.connection_pools.get(name)
    
    def cache_get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self.cache.get(key)
    
    def cache_put(self, key: str, value: Any, ttl: Optional[float] = None):
        """Put value in cache."""
        self.cache.put(key, value, ttl)
    
    def record_metric(self, metric: str, value: float):
        """Record a performance metric."""
        self.performance_metrics[metric].append(value)
        # Keep only last 1000 values
        if len(self.performance_metrics[metric]) > 1000:
            self.performance_metrics[metric] = self.performance_metrics[metric][-1000:]
    
    def get_metric_average(self, metric: str, window: int = 100) -> Optional[float]:
        """Get average of a metric over a window."""
        values = self.performance_metrics[metric]
        if not values:
            return None
        
        recent_values = values[-window:] if len(values) > window else values
        return sum(recent_values) / len(recent_values)
    
    def get_metric_stats(self, metric: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        values = self.performance_metrics[metric]
        if not values:
            return {}
        
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "average": sum(values) / len(values),
            "recent_average": self.get_metric_average(metric, 100) or 0.0
        }
    
    async def start_monitoring(self):
        """Start performance monitoring."""
        await self.resource_manager.start_monitoring()
    
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        await self.resource_manager.stop_monitoring()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system performance status."""
        return {
            "cache": {
                "size": self.cache.size(),
                "max_size": self.cache.max_size
            },
            "resources": dict(self.resource_manager.resource_usage),
            "load_balancer": {
                "workers": len(self.load_balancer.workers),
                "strategy": self.load_balancer.strategy
            },
            "connection_pools": {
                name: {
                    "active": len(pool.active_connections),
                    "idle": len(pool.idle_connections),
                    "max": pool.max_connections
                }
                for name, pool in self.connection_pools.items()
            },
            "metrics": {
                metric: self.get_metric_stats(metric)
                for metric in self.performance_metrics
            }
        }

# Global instance
performance_optimizer = PerformanceOptimizer()
