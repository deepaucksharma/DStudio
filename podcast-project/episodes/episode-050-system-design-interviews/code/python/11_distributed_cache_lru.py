#!/usr/bin/env python3
"""
Distributed Cache with LRU Eviction - Episode 50: System Design Interview Mastery
Flipkart Product Cache System with Regional Distribution

Distributed cache जैसे Mumbai के dabbawalas का network है।
हर region में fresh data cache करके fast delivery करते हैं।

Author: Hindi Podcast Series
Topic: Distributed Caching with LRU Eviction and Indian Context
"""

import time
import threading
import hashlib
import json
import pickle
import redis
from collections import OrderedDict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging
from datetime import datetime, timezone, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache eviction strategies - Memory management ke tarike"""
    LRU = "least_recently_used"        # Mumbai dabba delivery - least used first
    LFU = "least_frequently_used"      # Frequency based eviction
    FIFO = "first_in_first_out"       # Queue based eviction
    TTL = "time_to_live"              # Time based expiration

@dataclass
class CacheEntry:
    """Cache entry with metadata - Dabba delivery slip"""
    key: str
    value: Any
    created_at: float
    last_accessed: float
    access_count: int = 0
    ttl: Optional[int] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        """Calculate approximate size"""
        try:
            self.size_bytes = len(pickle.dumps(self.value))
        except:
            self.size_bytes = len(str(self.value).encode('utf-8'))
    
    def is_expired(self) -> bool:
        """Check if entry is expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    def touch(self):
        """Update access information - Dabba delivery timestamp"""
        self.last_accessed = time.time()
        self.access_count += 1

class LRUCache:
    """Local LRU Cache Implementation - Mumbai Dabba Cache"""
    
    def __init__(self, max_size: int, max_memory_mb: int = 100):
        """Initialize LRU cache with size and memory limits"""
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.current_memory_bytes = 0
        
        # OrderedDict maintains insertion order (LRU order)
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'memory_evictions': 0,
            'expired_evictions': 0
        }
        
        print(f"🏪 LRU Cache initialized - Size: {max_size}, Memory: {max_memory_mb}MB")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache - Dabba retrieve करना"""
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                logger.debug(f"Cache MISS: {key}")
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.is_expired():
                self._remove_entry(key)
                self.stats['misses'] += 1
                self.stats['expired_evictions'] += 1
                logger.debug(f"Cache EXPIRED: {key}")
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            entry.touch()
            
            self.stats['hits'] += 1
            logger.debug(f"Cache HIT: {key}")
            return entry.value
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in cache - Dabba store करना"""
        with self.lock:
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=time.time(),
                last_accessed=time.time(),
                ttl=ttl
            )
            
            # Check memory limit
            if entry.size_bytes > self.max_memory_bytes:
                logger.warning(f"Entry too large: {key} ({entry.size_bytes} bytes)")
                return False
            
            # Remove existing entry if present
            if key in self.cache:
                old_entry = self.cache[key]
                self.current_memory_bytes -= old_entry.size_bytes
            
            # Evict entries to make space
            self._ensure_capacity(entry.size_bytes)
            
            # Add new entry
            self.cache[key] = entry
            self.current_memory_bytes += entry.size_bytes
            
            logger.debug(f"Cache PUT: {key} ({entry.size_bytes} bytes)")
            return True
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        with self.lock:
            if key in self.cache:
                self._remove_entry(key)
                logger.debug(f"Cache DELETE: {key}")
                return True
            return False
    
    def _ensure_capacity(self, new_entry_size: int):
        """Ensure cache has capacity for new entry"""
        # Size-based eviction
        while len(self.cache) >= self.max_size and self.cache:
            self._evict_lru()
        
        # Memory-based eviction
        while (self.current_memory_bytes + new_entry_size > self.max_memory_bytes 
               and self.cache):
            self._evict_lru()
            self.stats['memory_evictions'] += 1
    
    def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Get LRU key (first item in OrderedDict)
        lru_key = next(iter(self.cache))
        self._remove_entry(lru_key)
        self.stats['evictions'] += 1
        logger.debug(f"Cache EVICT LRU: {lru_key}")
    
    def _remove_entry(self, key: str):
        """Remove entry and update memory usage"""
        if key in self.cache:
            entry = self.cache.pop(key)
            self.current_memory_bytes -= entry.size_bytes
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'size': len(self.cache),
                'max_size': self.max_size,
                'memory_usage_mb': self.current_memory_bytes / (1024 * 1024),
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024),
                'hit_rate': hit_rate
            }
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            self.current_memory_bytes = 0
            logger.info("Cache cleared")

class ConsistentHashRing:
    """Consistent Hash Ring for cache distribution - Mumbai area distribution"""
    
    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        """Initialize consistent hash ring"""
        self.nodes = set(nodes)
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        
        self._build_ring()
        print(f"🔄 Consistent Hash Ring built - Nodes: {len(nodes)}, Virtual: {virtual_nodes}")
    
    def _build_ring(self):
        """Build the hash ring with virtual nodes"""
        self.ring.clear()
        
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def _hash(self, key: str) -> int:
        """Generate hash value for key"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)
    
    def get_node(self, key: str) -> str:
        """Get node for given key - Mumbai area assign करना"""
        if not self.ring:
            return None
        
        hash_value = self._hash(key)
        
        # Find first node clockwise
        for ring_key in self.sorted_keys:
            if hash_value <= ring_key:
                return self.ring[ring_key]
        
        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]
    
    def add_node(self, node: str):
        """Add new node to ring"""
        self.nodes.add(node)
        self._build_ring()
        logger.info(f"Node added to ring: {node}")
    
    def remove_node(self, node: str):
        """Remove node from ring"""
        if node in self.nodes:
            self.nodes.remove(node)
            self._build_ring()
            logger.info(f"Node removed from ring: {node}")

class DistributedCache:
    """Distributed Cache System - Flipkart Multi-Region Cache"""
    
    def __init__(self, nodes: List[str], replication_factor: int = 2):
        """Initialize distributed cache system"""
        self.nodes = nodes
        self.replication_factor = min(replication_factor, len(nodes))
        self.hash_ring = ConsistentHashRing(nodes)
        
        # Local caches for each node (simulation)
        self.local_caches: Dict[str, LRUCache] = {}
        for node in nodes:
            self.local_caches[node] = LRUCache(max_size=1000, max_memory_mb=50)
        
        # Redis connections (optional distributed backend)
        self.redis_connections: Dict[str, redis.Redis] = {}
        
        self.stats = {
            'distributed_gets': 0,
            'distributed_puts': 0,
            'replication_writes': 0,
            'consistency_checks': 0
        }
        
        print(f"🌐 Distributed Cache initialized")
        print(f"   Nodes: {len(nodes)}, Replication: {replication_factor}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache"""
        self.stats['distributed_gets'] += 1
        
        # Get primary and replica nodes
        primary_node = self.hash_ring.get_node(key)
        replica_nodes = self._get_replica_nodes(key, exclude=[primary_node])
        
        logger.debug(f"GET {key} - Primary: {primary_node}, Replicas: {replica_nodes}")
        
        # Try primary node first
        if primary_node and primary_node in self.local_caches:
            value = self.local_caches[primary_node].get(key)
            if value is not None:
                return value
        
        # Try replica nodes
        for replica_node in replica_nodes:
            if replica_node in self.local_caches:
                value = self.local_caches[replica_node].get(key)
                if value is not None:
                    # Repair primary node
                    if primary_node and primary_node in self.local_caches:
                        self.local_caches[primary_node].put(key, value)
                    return value
        
        return None
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Put value in distributed cache with replication"""
        self.stats['distributed_puts'] += 1
        
        # Get primary and replica nodes
        primary_node = self.hash_ring.get_node(key)
        replica_nodes = self._get_replica_nodes(key, exclude=[primary_node])
        
        logger.debug(f"PUT {key} - Primary: {primary_node}, Replicas: {replica_nodes}")
        
        success_count = 0
        
        # Write to primary node
        if primary_node and primary_node in self.local_caches:
            if self.local_caches[primary_node].put(key, value, ttl):
                success_count += 1
        
        # Write to replica nodes
        for replica_node in replica_nodes:
            if replica_node in self.local_caches:
                if self.local_caches[replica_node].put(key, value, ttl):
                    success_count += 1
                    self.stats['replication_writes'] += 1
        
        # Consider success if at least one write succeeded
        return success_count > 0
    
    def delete(self, key: str) -> bool:
        """Delete key from distributed cache"""
        primary_node = self.hash_ring.get_node(key)
        replica_nodes = self._get_replica_nodes(key, exclude=[primary_node])
        
        success_count = 0
        
        # Delete from primary node
        if primary_node and primary_node in self.local_caches:
            if self.local_caches[primary_node].delete(key):
                success_count += 1
        
        # Delete from replica nodes
        for replica_node in replica_nodes:
            if replica_node in self.local_caches:
                if self.local_caches[replica_node].delete(key):
                    success_count += 1
        
        return success_count > 0
    
    def _get_replica_nodes(self, key: str, exclude: List[str] = None) -> List[str]:
        """Get replica nodes for key"""
        if exclude is None:
            exclude = []
        
        # Simple implementation: get next N-1 nodes in ring
        primary_node = self.hash_ring.get_node(key)
        replica_nodes = []
        
        available_nodes = [n for n in self.nodes if n not in exclude]
        
        # Add nodes in hash ring order
        for node in available_nodes:
            if len(replica_nodes) < self.replication_factor - 1:
                replica_nodes.append(node)
        
        return replica_nodes
    
    def get_cluster_stats(self) -> Dict:
        """Get distributed cache cluster statistics"""
        cluster_stats = {
            'nodes': len(self.nodes),
            'replication_factor': self.replication_factor,
            **self.stats,
            'node_stats': {}
        }
        
        for node in self.nodes:
            if node in self.local_caches:
                cluster_stats['node_stats'][node] = self.local_caches[node].get_stats()
        
        return cluster_stats
    
    def simulate_node_failure(self, failed_node: str):
        """Simulate node failure for testing"""
        if failed_node in self.local_caches:
            print(f"🚨 Simulating node failure: {failed_node}")
            # Don't actually remove, just mark as failed
            self.local_caches[failed_node].clear()
    
    def add_node(self, new_node: str):
        """Add new node to cluster"""
        if new_node not in self.nodes:
            self.nodes.append(new_node)
            self.local_caches[new_node] = LRUCache(max_size=1000, max_memory_mb=50)
            self.hash_ring.add_node(new_node)
            print(f"✅ Node added to cluster: {new_node}")

class FlipkartProductCache:
    """Flipkart Product Cache System with Regional Distribution"""
    
    def __init__(self):
        """Initialize Flipkart-style product cache"""
        # Indian regional nodes
        indian_regions = [
            "mumbai-west",      # Mumbai, Maharashtra
            "delhi-ncr",        # Delhi NCR
            "bangalore-south",  # Bangalore, Karnataka
            "hyderabad-south",  # Hyderabad, Telangana
            "kolkata-east",     # Kolkata, West Bengal
            "chennai-south",    # Chennai, Tamil Nadu
            "pune-west",        # Pune, Maharashtra
            "ahmedabad-west"    # Ahmedabad, Gujarat
        ]
        
        self.cache = DistributedCache(
            nodes=indian_regions,
            replication_factor=3  # 3x replication for high availability
        )
        
        # Product categories with different TTL
        self.category_ttl = {
            'electronics': 300,      # 5 minutes - fast changing prices
            'fashion': 1800,         # 30 minutes - seasonal changes
            'books': 3600,           # 1 hour - stable inventory
            'groceries': 900,        # 15 minutes - fresh products
            'mobiles': 600,          # 10 minutes - frequent updates
        }
        
        print("🛍️ Flipkart Product Cache initialized with Indian regional distribution")
    
    def cache_product(self, product_id: str, product_data: Dict, category: str = 'general') -> bool:
        """Cache product data with appropriate TTL"""
        # Add Indian context to product data
        enhanced_data = {
            **product_data,
            'cached_at': datetime.now(timezone.utc).isoformat(),
            'region': 'India',
            'currency': 'INR',
            'tax_included': True,  # Indian prices include GST
        }
        
        ttl = self.category_ttl.get(category, 1800)  # Default 30 minutes
        
        success = self.cache.put(f"product:{product_id}", enhanced_data, ttl=ttl)
        
        if success:
            logger.info(f"Product cached: {product_id} (Category: {category}, TTL: {ttl}s)")
        
        return success
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Get cached product data"""
        product_data = self.cache.get(f"product:{product_id}")
        
        if product_data:
            logger.info(f"Product cache hit: {product_id}")
        else:
            logger.info(f"Product cache miss: {product_id}")
        
        return product_data
    
    def cache_user_recommendations(self, user_id: str, recommendations: List[str]) -> bool:
        """Cache user recommendations"""
        cache_key = f"recommendations:user:{user_id}"
        
        recommendation_data = {
            'user_id': user_id,
            'product_ids': recommendations,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'algorithm': 'collaborative_filtering_v2',
            'region': 'India'
        }
        
        return self.cache.put(cache_key, recommendation_data, ttl=7200)  # 2 hours
    
    def get_user_recommendations(self, user_id: str) -> Optional[List[str]]:
        """Get cached user recommendations"""
        cache_key = f"recommendations:user:{user_id}"
        rec_data = self.cache.get(cache_key)
        
        if rec_data and 'product_ids' in rec_data:
            return rec_data['product_ids']
        
        return None
    
    def get_cache_health(self) -> Dict:
        """Get cache health metrics"""
        stats = self.cache.get_cluster_stats()
        
        # Calculate overall health score
        total_hit_rate = 0
        healthy_nodes = 0
        
        for node_stats in stats['node_stats'].values():
            if node_stats['hit_rate'] > 0:
                total_hit_rate += node_stats['hit_rate']
                healthy_nodes += 1
        
        avg_hit_rate = total_hit_rate / max(healthy_nodes, 1)
        
        health_score = min(100, (healthy_nodes / len(self.cache.nodes)) * 100 * (avg_hit_rate / 100))
        
        return {
            **stats,
            'health_score': health_score,
            'healthy_nodes': healthy_nodes,
            'average_hit_rate': avg_hit_rate
        }

def demonstrate_lru_cache():
    """Demonstrate LRU Cache functionality"""
    print("🏪 LRU Cache Demo - Mumbai Dabba Cache System")
    print("=" * 60)
    
    # Create small cache for demo
    cache = LRUCache(max_size=5, max_memory_mb=1)
    
    # Test basic operations
    print("\n📝 Basic Cache Operations:")
    print("-" * 30)
    
    # Put some items
    cache.put("user:123", {"name": "Raj", "city": "Mumbai", "age": 28})
    cache.put("user:456", {"name": "Priya", "city": "Delhi", "age": 25})
    cache.put("user:789", {"name": "Amit", "city": "Bangalore", "age": 30})
    
    # Get items (changes LRU order)
    print(f"Get user:123: {cache.get('user:123')}")
    print(f"Get user:456: {cache.get('user:456')}")
    
    # Add more items to trigger eviction
    cache.put("user:101", {"name": "Sneha", "city": "Pune", "age": 26})
    cache.put("user:102", {"name": "Vikash", "city": "Chennai", "age": 29})
    cache.put("user:103", {"name": "Anita", "city": "Kolkata", "age": 27})
    cache.put("user:104", {"name": "Rohit", "city": "Hyderabad", "age": 31})
    
    print(f"\nCache Stats after operations:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

def demonstrate_distributed_cache():
    """Demonstrate Distributed Cache functionality"""
    print("\n🌐 Distributed Cache Demo - Multi-Region Product Cache")
    print("=" * 65)
    
    # Initialize Flipkart product cache
    flipkart_cache = FlipkartProductCache()
    
    # Sample product data
    sample_products = [
        {
            'id': 'MOB001',
            'name': 'iPhone 15 Pro',
            'price': 134900,  # INR
            'category': 'mobiles',
            'brand': 'Apple',
            'in_stock': True,
            'seller': 'Flipkart',
            'rating': 4.5
        },
        {
            'id': 'BOOK001', 
            'name': 'Atomic Habits Hindi',
            'price': 399,
            'category': 'books',
            'author': 'James Clear',
            'language': 'Hindi',
            'in_stock': True,
            'rating': 4.7
        },
        {
            'id': 'ELEC001',
            'name': 'Samsung 55" 4K Smart TV',
            'price': 54990,
            'category': 'electronics',
            'brand': 'Samsung',
            'in_stock': True,
            'warranty': '2 years',
            'rating': 4.3
        }
    ]
    
    print("\n📦 Caching Products:")
    print("-" * 25)
    
    # Cache products
    for product in sample_products:
        success = flipkart_cache.cache_product(
            product_id=product['id'],
            product_data=product,
            category=product['category']
        )
        print(f"   {product['name']}: {'✅ Cached' if success else '❌ Failed'}")
    
    print("\n🔍 Retrieving Products:")
    print("-" * 25)
    
    # Retrieve products
    for product in sample_products:
        cached_product = flipkart_cache.get_product(product['id'])
        if cached_product:
            print(f"   {cached_product['name']}: ₹{cached_product['price']:,} "
                  f"(Cached at: {cached_product['cached_at'][:19]})")
        else:
            print(f"   {product['id']}: ❌ Not found in cache")
    
    # Cache user recommendations
    print("\n👤 User Recommendations:")
    print("-" * 25)
    
    user_id = "user_mumbai_9876543210"
    recommendations = ['MOB001', 'ELEC001', 'BOOK001']
    
    flipkart_cache.cache_user_recommendations(user_id, recommendations)
    cached_recs = flipkart_cache.get_user_recommendations(user_id)
    
    if cached_recs:
        print(f"   User {user_id}: {cached_recs}")
    
    # Show cache health
    print(f"\n🏥 Cache Health Report:")
    print("-" * 25)
    health = flipkart_cache.get_cache_health()
    print(f"   Health Score: {health['health_score']:.1f}%")
    print(f"   Healthy Nodes: {health['healthy_nodes']}/{len(flipkart_cache.cache.nodes)}")
    print(f"   Average Hit Rate: {health['average_hit_rate']:.1f}%")
    
    # Simulate node failure
    print(f"\n🚨 Simulating Node Failure:")
    print("-" * 30)
    flipkart_cache.cache.simulate_node_failure("mumbai-west")
    
    # Try to get product after node failure
    cached_product = flipkart_cache.get_product('MOB001')
    print(f"   Product retrieval after failure: {'✅ Success' if cached_product else '❌ Failed'}")
    
    return flipkart_cache

def demonstrate_cache_performance():
    """Demonstrate cache performance under load"""
    print("\n⚡ Cache Performance Demo - High Load Simulation")
    print("=" * 60)
    
    cache = LRUCache(max_size=1000, max_memory_mb=10)
    
    # Simulate high load
    import random
    
    operations = 10000
    keys = [f"key_{i}" for i in range(5000)]  # More keys than cache size
    
    start_time = time.time()
    
    for i in range(operations):
        operation = random.choice(['get', 'put', 'put', 'put'])  # More puts than gets
        key = random.choice(keys)
        
        if operation == 'get':
            cache.get(key)
        else:
            value = {
                'data': f"value_{i}",
                'timestamp': time.time(),
                'user_id': random.randint(1000, 9999)
            }
            cache.put(key, value, ttl=300)
        
        if i % 1000 == 0:
            print(f"   Operations completed: {i}")
    
    end_time = time.time()
    
    print(f"\n📊 Performance Results:")
    stats = cache.get_stats()
    print(f"   Operations: {operations}")
    print(f"   Duration: {end_time - start_time:.2f}s")
    print(f"   Ops/sec: {operations / (end_time - start_time):.0f}")
    print(f"   Hit Rate: {stats['hit_rate']:.1f}%")
    print(f"   Cache Size: {stats['size']}/{stats['max_size']}")
    print(f"   Memory Usage: {stats['memory_usage_mb']:.1f}MB")
    print(f"   Evictions: {stats['evictions']}")

if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_lru_cache()
    
    print("\n" + "="*80 + "\n")
    
    flipkart_cache = demonstrate_distributed_cache()
    
    print("\n" + "="*80 + "\n")
    
    demonstrate_cache_performance()
    
    print(f"\n✅ Distributed Cache Demo Complete!")
    print(f"📚 Key Concepts Demonstrated:")
    print(f"   • LRU Eviction - Least recently used removal")
    print(f"   • Memory Management - Size and memory-based eviction") 
    print(f"   • Distributed Caching - Multi-region data distribution")
    print(f"   • Consistent Hashing - Uniform cache distribution")
    print(f"   • Replication - Data redundancy for availability")
    print(f"   • TTL Support - Time-based expiration")
    print(f"   • Indian Context - Flipkart, regional nodes, INR pricing")
    print(f"   • Performance Optimization - High-throughput caching")