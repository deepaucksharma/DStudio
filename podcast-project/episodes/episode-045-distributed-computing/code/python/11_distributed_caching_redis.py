#!/usr/bin/env python3
"""
Distributed Caching System with Redis Cluster
Episode 45: Distributed Computing at Scale

यह example distributed caching system दिखाता है Redis cluster के साथ
Multiple cache nodes, consistent hashing, और failover mechanisms
के साथ high-performance caching for Indian scale applications।

Production Stats:
- Hotstar: 25M+ concurrent users during cricket matches
- Cache hit rate: 95%+ for live streaming metadata
- Latency: <1ms for cache operations
- Data volume: 100TB+ cached data
- Geographic distribution: 12+ regions across India
"""

import asyncio
import json
import logging
import time
import uuid
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from enum import Enum
import random
from collections import defaultdict, deque
import threading
from concurrent.futures import ThreadPoolExecutor
import bisect
import pickle
import zlib

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheOperation(Enum):
    GET = "GET"
    SET = "SET"
    DELETE = "DELETE"
    EXISTS = "EXISTS"
    EXPIRE = "EXPIRE"
    INCR = "INCR"
    DECR = "DECR"

class NodeStatus(Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    RECOVERING = "RECOVERING"

@dataclass
class CacheItem:
    """Cache item with metadata"""
    key: str
    value: Any
    ttl: Optional[int] = None  # Time to live in seconds
    created_at: datetime = None
    accessed_at: datetime = None
    access_count: int = 0
    size_bytes: int = 0
    compression_enabled: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.accessed_at is None:
            self.accessed_at = self.created_at
        if self.size_bytes == 0:
            self.size_bytes = len(str(self.value).encode('utf-8'))

@dataclass
class CacheStats:
    """Cache performance statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_keys: int = 0
    memory_used_bytes: int = 0
    memory_limit_bytes: int = 0
    avg_response_time_ms: float = 0.0
    
    @property
    def hit_rate(self) -> float:
        total_requests = self.hits + self.misses
        return (self.hits / total_requests * 100) if total_requests > 0 else 0.0
    
    @property
    def memory_usage_percent(self) -> float:
        return (self.memory_used_bytes / self.memory_limit_bytes * 100) if self.memory_limit_bytes > 0 else 0.0

class ConsistentHashRing:
    """Consistent hashing for distributed cache nodes"""
    
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        
        for node in nodes:
            self.add_node(node)
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing"""
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)
    
    def add_node(self, node: str):
        """Add node to hash ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
            bisect.insort(self.sorted_keys, hash_value)
    
    def remove_node(self, node: str):
        """Remove node from hash ring"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
                self.sorted_keys.remove(hash_value)
    
    def get_node(self, key: str) -> str:
        """Get responsible node for a key"""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find the first node with hash >= key_hash
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        if idx == len(self.sorted_keys):
            idx = 0
        
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes_for_replication(self, key: str, replica_count: int = 2) -> List[str]:
        """Get multiple nodes for replication"""
        if not self.ring:
            return []
        
        hash_value = self._hash(key)
        nodes = []
        seen_physical_nodes = set()
        
        # Start from the responsible node and move clockwise
        idx = bisect.bisect_right(self.sorted_keys, hash_value)
        
        for _ in range(len(self.sorted_keys)):
            if idx >= len(self.sorted_keys):
                idx = 0
            
            node = self.ring[self.sorted_keys[idx]]
            if node not in seen_physical_nodes:
                nodes.append(node)
                seen_physical_nodes.add(node)
                
                if len(nodes) >= replica_count + 1:  # +1 for primary
                    break
            
            idx += 1
        
        return nodes

class DistributedCacheNode:
    """Individual cache node in distributed system"""
    
    def __init__(self, node_id: str, region: str, memory_limit_mb: int = 1024):
        self.node_id = node_id
        self.region = region
        self.memory_limit_bytes = memory_limit_mb * 1024 * 1024
        
        # Cache storage
        self.cache_data = {}  # key -> CacheItem
        self.expiry_queue = {}  # key -> expiry_time
        
        # Node status
        self.status = NodeStatus.ACTIVE
        self.last_heartbeat = datetime.now()
        
        # Performance metrics
        self.stats = CacheStats(memory_limit_bytes=self.memory_limit_bytes)
        self.response_times = deque(maxlen=1000)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Cleanup thread
        self.cleanup_interval = 60  # seconds
        self.start_cleanup_thread()
        
        logger.info(f"🚀 Cache node {node_id} initialized in {region} with {memory_limit_mb}MB memory")
    
    def start_cleanup_thread(self):
        """Start background thread for cache cleanup"""
        def cleanup_expired():
            while self.status != NodeStatus.FAILED:
                try:
                    self.cleanup_expired_keys()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Error in cleanup thread: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_expired, daemon=True)
        cleanup_thread.start()
    
    def cleanup_expired_keys(self):
        """Remove expired keys from cache"""
        current_time = datetime.now()
        expired_keys = []
        
        with self.lock:
            for key, expiry_time in self.expiry_queue.items():
                if current_time >= expiry_time:
                    expired_keys.append(key)
            
            for key in expired_keys:
                if key in self.cache_data:
                    item = self.cache_data[key]
                    self.stats.memory_used_bytes -= item.size_bytes
                    del self.cache_data[key]
                    
                if key in self.expiry_queue:
                    del self.expiry_queue[key]
                
                self.stats.evictions += 1
                self.stats.total_keys -= 1
        
        if expired_keys:
            logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired keys from {self.node_id}")
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data if beneficial"""
        serialized = pickle.dumps(data)
        compressed = zlib.compress(serialized)
        
        # Only use compression if it reduces size significantly
        if len(compressed) < len(serialized) * 0.8:
            return compressed
        return serialized
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Decompress data if needed"""
        if compressed:
            decompressed = zlib.decompress(data)
            return pickle.loads(decompressed)
        return pickle.loads(data)
    
    def get(self, key: str) -> Tuple[Any, bool]:
        """Get value from cache"""
        start_time = time.time()
        
        with self.lock:
            # Check if key exists and not expired
            if key in self.cache_data:
                item = self.cache_data[key]
                
                # Check expiry
                if key in self.expiry_queue:
                    if datetime.now() >= self.expiry_queue[key]:
                        # Key expired, remove it
                        self.stats.memory_used_bytes -= item.size_bytes
                        del self.cache_data[key]
                        del self.expiry_queue[key]
                        self.stats.total_keys -= 1
                        self.stats.evictions += 1
                        self.stats.misses += 1
                        return None, False
                
                # Update access metadata
                item.accessed_at = datetime.now()
                item.access_count += 1
                
                response_time = (time.time() - start_time) * 1000
                self.response_times.append(response_time)
                self.stats.hits += 1
                
                return item.value, True
            else:
                self.stats.misses += 1
                return None, False
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        start_time = time.time()
        
        try:
            with self.lock:
                # Serialize and potentially compress the value
                if isinstance(value, (str, int, float, bool)):
                    stored_value = value
                    compressed = False
                    size_bytes = len(str(value).encode('utf-8'))
                else:
                    stored_value = self._compress_data(value)
                    compressed = True
                    size_bytes = len(stored_value)
                
                # Check memory limits
                if key not in self.cache_data:
                    if self.stats.memory_used_bytes + size_bytes > self.memory_limit_bytes:
                        # Evict least recently used items
                        if not self._evict_lru(size_bytes):
                            return False
                
                # Remove old item if exists
                if key in self.cache_data:
                    old_item = self.cache_data[key]
                    self.stats.memory_used_bytes -= old_item.size_bytes
                else:
                    self.stats.total_keys += 1
                
                # Create cache item
                item = CacheItem(
                    key=key,
                    value=stored_value,
                    ttl=ttl,
                    size_bytes=size_bytes,
                    compression_enabled=compressed
                )
                
                self.cache_data[key] = item
                self.stats.memory_used_bytes += size_bytes
                
                # Set expiry if TTL provided
                if ttl:
                    self.expiry_queue[key] = datetime.now() + timedelta(seconds=ttl)
                
                response_time = (time.time() - start_time) * 1000
                self.response_times.append(response_time)
                self.stats.sets += 1
                
                return True
                
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache_data:
                item = self.cache_data[key]
                self.stats.memory_used_bytes -= item.size_bytes
                del self.cache_data[key]
                
                if key in self.expiry_queue:
                    del self.expiry_queue[key]
                
                self.stats.total_keys -= 1
                self.stats.deletes += 1
                return True
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        with self.lock:
            if key in self.cache_data:
                # Check expiry
                if key in self.expiry_queue:
                    if datetime.now() >= self.expiry_queue[key]:
                        return False
                return True
            return False
    
    def _evict_lru(self, required_bytes: int) -> bool:
        """Evict least recently used items to free memory"""
        if not self.cache_data:
            return False
        
        # Sort items by last access time
        items_by_access = sorted(
            self.cache_data.items(),
            key=lambda x: x[1].accessed_at
        )
        
        freed_bytes = 0
        evicted_keys = []
        
        for key, item in items_by_access:
            if freed_bytes >= required_bytes:
                break
            
            freed_bytes += item.size_bytes
            evicted_keys.append(key)
        
        # Remove evicted items
        for key in evicted_keys:
            if key in self.cache_data:
                item = self.cache_data[key]
                self.stats.memory_used_bytes -= item.size_bytes
                del self.cache_data[key]
                
                if key in self.expiry_queue:
                    del self.expiry_queue[key]
                
                self.stats.total_keys -= 1
                self.stats.evictions += 1
        
        logger.debug(f"🗑️ Evicted {len(evicted_keys)} LRU items, freed {freed_bytes} bytes")
        return freed_bytes >= required_bytes
    
    def get_node_stats(self) -> Dict[str, Any]:
        """Get comprehensive node statistics"""
        with self.lock:
            avg_response_time = sum(self.response_times) / max(len(self.response_times), 1)
            
            return {
                "node_id": self.node_id,
                "region": self.region,
                "status": self.status.value,
                "hit_rate_percent": self.stats.hit_rate,
                "memory_usage_percent": self.stats.memory_usage_percent,
                "total_keys": self.stats.total_keys,
                "memory_used_mb": self.stats.memory_used_bytes / (1024 * 1024),
                "memory_limit_mb": self.stats.memory_limit_bytes / (1024 * 1024),
                "hits": self.stats.hits,
                "misses": self.stats.misses,
                "sets": self.stats.sets,
                "deletes": self.stats.deletes,
                "evictions": self.stats.evictions,
                "avg_response_time_ms": avg_response_time,
                "last_heartbeat": self.last_heartbeat.isoformat()
            }

class DistributedCacheCluster:
    """Distributed cache cluster with consistent hashing"""
    
    def __init__(self, replication_factor: int = 2):
        self.nodes = {}  # node_id -> DistributedCacheNode
        self.hash_ring = ConsistentHashRing([])
        self.replication_factor = replication_factor
        
        # Cluster metrics
        self.total_operations = 0
        self.cluster_start_time = datetime.now()
        
        # Initialize Indian region nodes
        self.setup_indian_cache_cluster()
        
        logger.info(f"🌐 Distributed cache cluster initialized with {len(self.nodes)} nodes")
    
    def setup_indian_cache_cluster(self):
        """Setup cache nodes across Indian regions"""
        indian_regions = [
            {"id": "cache_mumbai_1", "region": "Mumbai", "memory_mb": 2048},
            {"id": "cache_mumbai_2", "region": "Mumbai", "memory_mb": 2048},
            {"id": "cache_delhi_1", "region": "Delhi", "memory_mb": 1536},
            {"id": "cache_delhi_2", "region": "Delhi", "memory_mb": 1536},
            {"id": "cache_bangalore_1", "region": "Bangalore", "memory_mb": 1024},
            {"id": "cache_bangalore_2", "region": "Bangalore", "memory_mb": 1024},
            {"id": "cache_hyderabad_1", "region": "Hyderabad", "memory_mb": 1024},
            {"id": "cache_chennai_1", "region": "Chennai", "memory_mb": 512},
        ]
        
        node_ids = []
        for region_info in indian_regions:
            node = DistributedCacheNode(
                region_info["id"],
                region_info["region"],
                region_info["memory_mb"]
            )
            self.nodes[region_info["id"]] = node
            node_ids.append(region_info["id"])
        
        # Initialize consistent hash ring
        self.hash_ring = ConsistentHashRing(node_ids)
    
    async def get(self, key: str) -> Tuple[Any, bool]:
        """Get value from distributed cache"""
        # Get responsible nodes
        responsible_nodes = self.hash_ring.get_nodes_for_replication(key, self.replication_factor)
        
        if not responsible_nodes:
            return None, False
        
        # Try primary node first
        primary_node_id = responsible_nodes[0]
        primary_node = self.nodes.get(primary_node_id)
        
        if primary_node and primary_node.status == NodeStatus.ACTIVE:
            value, found = primary_node.get(key)
            if found:
                self.total_operations += 1
                return value, True
        
        # Try replica nodes if primary fails
        for replica_node_id in responsible_nodes[1:]:
            replica_node = self.nodes.get(replica_node_id)
            if replica_node and replica_node.status == NodeStatus.ACTIVE:
                value, found = replica_node.get(key)
                if found:
                    # Repair primary if needed
                    if primary_node and primary_node.status == NodeStatus.ACTIVE:
                        await self._repair_primary(key, value, primary_node)
                    
                    self.total_operations += 1
                    return value, True
        
        self.total_operations += 1
        return None, False
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in distributed cache with replication"""
        # Get responsible nodes
        responsible_nodes = self.hash_ring.get_nodes_for_replication(key, self.replication_factor)
        
        if not responsible_nodes:
            return False
        
        # Write to all replicas
        success_count = 0
        tasks = []
        
        for node_id in responsible_nodes:
            node = self.nodes.get(node_id)
            if node and node.status == NodeStatus.ACTIVE:
                task = asyncio.create_task(self._set_on_node(node, key, value, ttl))
                tasks.append(task)
        
        # Wait for all writes
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for result in results if result is True)
        
        self.total_operations += 1
        
        # Consider successful if written to majority of replicas
        return success_count > len(responsible_nodes) // 2
    
    async def _set_on_node(self, node: DistributedCacheNode, key: str, value: Any, ttl: Optional[int]) -> bool:
        """Set value on specific node (async wrapper)"""
        return node.set(key, value, ttl)
    
    async def _repair_primary(self, key: str, value: Any, primary_node: DistributedCacheNode):
        """Repair primary node by writing missing data"""
        try:
            await self._set_on_node(primary_node, key, value, None)
            logger.debug(f"🔧 Repaired key {key} on primary node {primary_node.node_id}")
        except Exception as e:
            logger.error(f"Failed to repair primary node: {e}")
    
    async def delete(self, key: str) -> bool:
        """Delete key from distributed cache"""
        # Get responsible nodes
        responsible_nodes = self.hash_ring.get_nodes_for_replication(key, self.replication_factor)
        
        if not responsible_nodes:
            return False
        
        # Delete from all replicas
        success_count = 0
        for node_id in responsible_nodes:
            node = self.nodes.get(node_id)
            if node and node.status == NodeStatus.ACTIVE:
                if node.delete(key):
                    success_count += 1
        
        self.total_operations += 1
        return success_count > 0
    
    def add_node(self, node_id: str, region: str, memory_mb: int = 1024):
        """Add new node to cluster"""
        if node_id in self.nodes:
            logger.warning(f"Node {node_id} already exists")
            return False
        
        new_node = DistributedCacheNode(node_id, region, memory_mb)
        self.nodes[node_id] = new_node
        self.hash_ring.add_node(node_id)
        
        logger.info(f"➕ Added new cache node: {node_id} in {region}")
        return True
    
    def remove_node(self, node_id: str):
        """Remove node from cluster"""
        if node_id not in self.nodes:
            logger.warning(f"Node {node_id} not found")
            return False
        
        # Mark node as failed
        self.nodes[node_id].status = NodeStatus.FAILED
        self.hash_ring.remove_node(node_id)
        
        # TODO: In production, would migrate data to other nodes
        del self.nodes[node_id]
        
        logger.info(f"➖ Removed cache node: {node_id}")
        return True
    
    def get_cluster_stats(self) -> Dict[str, Any]:
        """Get comprehensive cluster statistics"""
        uptime = datetime.now() - self.cluster_start_time
        
        # Aggregate stats from all nodes
        total_hits = sum(node.stats.hits for node in self.nodes.values())
        total_misses = sum(node.stats.misses for node in self.nodes.values())
        total_sets = sum(node.stats.sets for node in self.nodes.values())
        total_deletes = sum(node.stats.deletes for node in self.nodes.values())
        total_evictions = sum(node.stats.evictions for node in self.nodes.values())
        
        total_memory_used = sum(node.stats.memory_used_bytes for node in self.nodes.values())
        total_memory_limit = sum(node.stats.memory_limit_bytes for node in self.nodes.values())
        total_keys = sum(node.stats.total_keys for node in self.nodes.values())
        
        cluster_hit_rate = (total_hits / max(total_hits + total_misses, 1)) * 100
        cluster_memory_usage = (total_memory_used / max(total_memory_limit, 1)) * 100
        
        # Node statuses
        node_stats = {node_id: node.get_node_stats() for node_id, node in self.nodes.items()}
        
        # Regional distribution
        regional_stats = defaultdict(lambda: {"nodes": 0, "memory_mb": 0, "keys": 0})
        for node in self.nodes.values():
            region = node.region
            regional_stats[region]["nodes"] += 1
            regional_stats[region]["memory_mb"] += node.stats.memory_limit_bytes / (1024 * 1024)
            regional_stats[region]["keys"] += node.stats.total_keys
        
        return {
            "cluster_uptime": str(uptime),
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for node in self.nodes.values() if node.status == NodeStatus.ACTIVE),
            "total_operations": self.total_operations,
            "cluster_hit_rate_percent": cluster_hit_rate,
            "cluster_memory_usage_percent": cluster_memory_usage,
            "total_keys": total_keys,
            "total_memory_used_mb": total_memory_used / (1024 * 1024),
            "total_memory_limit_mb": total_memory_limit / (1024 * 1024),
            "total_hits": total_hits,
            "total_misses": total_misses,
            "total_sets": total_sets,
            "total_deletes": total_deletes,
            "total_evictions": total_evictions,
            "operations_per_second": self.total_operations / max(uptime.total_seconds(), 1),
            "regional_distribution": dict(regional_stats),
            "nodes": node_stats,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_cluster_dashboard(self):
        """Print comprehensive cluster dashboard"""
        stats = self.get_cluster_stats()
        
        print(f"\n{'='*80}")
        print(f"⚡ DISTRIBUTED CACHE CLUSTER DASHBOARD ⚡")
        print(f"{'='*80}")
        
        print(f"🌐 Cluster Overview:")
        print(f"   Total Nodes: {stats['total_nodes']}")
        print(f"   Active Nodes: {stats['active_nodes']}")
        print(f"   Cluster Uptime: {stats['cluster_uptime']}")
        print(f"   Total Operations: {stats['total_operations']:,}")
        
        print(f"\n📊 Performance Metrics:")
        print(f"   Cluster Hit Rate: {stats['cluster_hit_rate_percent']:.2f}%")
        print(f"   Memory Usage: {stats['cluster_memory_usage_percent']:.1f}%")
        print(f"   Total Keys: {stats['total_keys']:,}")
        print(f"   Operations/Second: {stats['operations_per_second']:.1f}")
        
        print(f"\n💾 Memory Statistics:")
        print(f"   Total Memory Used: {stats['total_memory_used_mb']:.1f} MB")
        print(f"   Total Memory Limit: {stats['total_memory_limit_mb']:.1f} MB")
        print(f"   Total Hits: {stats['total_hits']:,}")
        print(f"   Total Misses: {stats['total_misses']:,}")
        print(f"   Total Evictions: {stats['total_evictions']:,}")
        
        print(f"\n🗺️ Regional Distribution:")
        for region, region_stats in stats['regional_distribution'].items():
            print(f"   {region}:")
            print(f"     Nodes: {region_stats['nodes']}")
            print(f"     Memory: {region_stats['memory_mb']:.0f} MB")
            print(f"     Keys: {region_stats['keys']:,}")
        
        print(f"\n🖥️ Node Details:")
        for node_id, node_stats in stats['nodes'].items():
            print(f"   {node_id} ({node_stats['region']}):")
            print(f"     Status: {node_stats['status']}")
            print(f"     Hit Rate: {node_stats['hit_rate_percent']:.1f}%")
            print(f"     Memory: {node_stats['memory_used_mb']:.1f}/{node_stats['memory_limit_mb']:.0f} MB")
            print(f"     Keys: {node_stats['total_keys']:,}")
            print(f"     Response Time: {node_stats['avg_response_time_ms']:.2f} ms")
        
        print(f"\n🕐 Last Updated: {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*80}")

# Test data generators for Indian context
def generate_hotstar_metadata() -> Dict[str, Any]:
    """Generate cricket match metadata for Hotstar-like caching"""
    match_types = ["Test", "ODI", "T20", "IPL"]
    teams = ["India", "Australia", "England", "Pakistan", "South Africa", "New Zealand"]
    
    return {
        "match_id": f"MATCH_{random.randint(100000, 999999)}",
        "match_type": random.choice(match_types),
        "teams": random.sample(teams, 2),
        "venue": random.choice(["Wankhede", "Eden Gardens", "M. Chinnaswamy", "Feroz Shah Kotla"]),
        "live_score": {
            "team1_score": f"{random.randint(150, 350)}/{random.randint(3, 10)}",
            "team2_score": f"{random.randint(100, 200)}/{random.randint(2, 8)}",
            "overs": f"{random.randint(10, 50)}.{random.randint(0, 5)}"
        },
        "viewers": random.randint(5000000, 25000000),
        "commentary": [f"Ball {i}: Great shot!" for i in range(1, 6)],
        "last_updated": datetime.now().isoformat()
    }

def generate_user_session_data() -> Dict[str, Any]:
    """Generate user session data for caching"""
    return {
        "user_id": f"user_{random.randint(100000, 999999)}",
        "session_id": str(uuid.uuid4()),
        "preferences": {
            "language": random.choice(["Hindi", "English", "Tamil", "Telugu", "Bengali"]),
            "quality": random.choice(["HD", "Full HD", "4K"]),
            "region": random.choice(["North", "South", "East", "West"])
        },
        "viewing_history": [f"content_{i}" for i in range(random.randint(5, 20))],
        "device_info": {
            "type": random.choice(["mobile", "tablet", "tv", "desktop"]),
            "os": random.choice(["Android", "iOS", "WebOS", "Windows"])
        },
        "subscription": {
            "type": random.choice(["Free", "VIP", "Premium"]),
            "expires_at": (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat()
        }
    }

async def simulate_hotstar_traffic(cluster: DistributedCacheCluster, duration_minutes: int = 5):
    """Simulate Hotstar-like high traffic with live cricket streaming"""
    logger.info(f"🏏 Starting Hotstar-like traffic simulation for {duration_minutes} minutes")
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    operation_count = 0
    
    try:
        while time.time() < end_time:
            # Simulate live cricket match traffic patterns
            current_minute = int((time.time() - start_time) / 60)
            
            # Peak traffic during exciting moments (every 30 seconds)
            if current_minute % 1 == 0 and int(time.time()) % 30 < 5:
                operations_per_second = random.randint(500, 1000)  # High traffic
            else:
                operations_per_second = random.randint(100, 300)   # Normal traffic
            
            # Generate cache operations
            tasks = []
            for _ in range(operations_per_second):
                operation_type = random.choices(
                    ["get", "set", "get", "get", "set"],  # More reads than writes
                    weights=[40, 10, 30, 15, 5]
                )[0]
                
                if operation_type == "get":
                    # Simulate popular content access
                    key = random.choice([
                        "live_match_data",
                        "trending_videos",
                        "user_recommendations",
                        f"user_session_{random.randint(1, 10000)}",
                        f"match_highlights_{random.randint(1, 100)}"
                    ])
                    task = cluster.get(key)
                
                elif operation_type == "set":
                    if random.random() < 0.3:
                        # Live match data (short TTL)
                        key = "live_match_data"
                        value = generate_hotstar_metadata()
                        ttl = 5  # 5 seconds TTL for live data
                    else:
                        # User session data
                        session_data = generate_user_session_data()
                        key = f"user_session_{session_data['user_id']}"
                        value = session_data
                        ttl = 3600  # 1 hour TTL
                    
                    task = cluster.set(key, value, ttl)
                
                tasks.append(task)
                operation_count += 1
            
            # Execute batch of operations
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Print dashboard every 30 seconds during peak traffic
            if operation_count % 1000 == 0:
                cluster.print_cluster_dashboard()
            
            # Small delay to control rate
            await asyncio.sleep(0.1)
    
    except KeyboardInterrupt:
        logger.info("Simulation stopped by user")
    
    logger.info(f"🏁 Traffic simulation completed! Processed {operation_count} operations")
    
    # Final dashboard
    cluster.print_cluster_dashboard()

async def main():
    """Main demo function"""
    print("🇮🇳 Distributed Cache Cluster System")
    print("⚡ Redis-like distributed caching with consistent hashing")
    print("🏏 Simulating Hotstar-scale live cricket streaming traffic...\n")
    
    # Initialize distributed cache cluster
    cluster = DistributedCacheCluster(replication_factor=2)
    
    try:
        # Show initial cluster status
        cluster.print_cluster_dashboard()
        
        # Pre-populate with some data
        logger.info("📊 Pre-populating cache with sample data...")
        
        # Add popular content
        await cluster.set("trending_videos", [f"video_{i}" for i in range(1, 101)], ttl=3600)
        await cluster.set("live_match_data", generate_hotstar_metadata(), ttl=5)
        
        # Add user sessions
        for i in range(100):
            session_data = generate_user_session_data()
            await cluster.set(f"user_session_{session_data['user_id']}", session_data, ttl=3600)
        
        # Run traffic simulation
        await simulate_hotstar_traffic(cluster, duration_minutes=3)
        
        print(f"\n🎯 SIMULATION COMPLETED!")
        print(f"💡 Production system capabilities:")
        print(f"   - Handle 25M+ concurrent users")
        print(f"   - 95%+ cache hit rate for live streaming")
        print(f"   - <1ms latency for cache operations")
        print(f"   - Geographic distribution across India")
        print(f"   - Automatic failover और replication")
        print(f"   - Memory-efficient data compression")
        
    except Exception as e:
        logger.error(f"❌ Error in simulation: {e}")

if __name__ == "__main__":
    # Run the distributed cache system demo
    asyncio.run(main())