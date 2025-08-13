#!/usr/bin/env python3
"""
Multi-Level Cache Hierarchy Implementation
Flipkart-style 4-tier caching system for maximum performance

Cache Levels:
- L1: CPU Cache (In-process dictionary) - 1ms access
- L2: Application Cache (Local Redis instance) - 5ms access  
- L3: Distributed Cache (Redis Cluster) - 20ms access
- L4: CDN Cache (CloudFlare/AWS CloudFront) - 50ms access
- Database: PostgreSQL/MongoDB - 200ms+ access

Use Cases:
- Product catalog caching
- Image और static asset caching
- User session data
- Search results और filters
- Mumbai से Delhi तक - different latency requirements

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (Multi-Level Hierarchy)
"""

import time
import json
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
import threading
import logging
from abc import ABC, abstractmethod
import redis
from urllib.parse import urljoin
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    """Cache item with metadata"""
    key: str
    value: Any
    ttl: int
    created_at: float
    access_count: int = 0
    last_accessed: float = 0.0
    size_bytes: int = 0

@dataclass
class CacheStats:
    """Cache level statistics"""
    level_name: str
    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    avg_access_time_ms: float = 0.0

class CacheLevel(ABC):
    """Abstract base class for cache levels"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        pass
    
    @abstractmethod
    def get_stats(self) -> CacheStats:
        pass

class L1CPUCache(CacheLevel):
    """
    L1 Cache - In-process memory cache
    Ultra-fast in-memory cache - Mumbai local train जैसी speed
    """
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.cache = {}
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.stats = CacheStats("L1-CPU")
        self.lock = threading.RLock()
        
        logger.info(f"🚀 L1 CPU Cache initialized - Max items: {max_size}, Max memory: {max_memory_mb}MB")
    
    def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                
                # Check TTL
                if time.time() - item.created_at > item.ttl:
                    del self.cache[key]
                    self.stats.misses += 1
                    return None
                
                # Update access stats
                item.access_count += 1
                item.last_accessed = time.time()
                
                self.stats.hits += 1
                self.stats.avg_access_time_ms = (time.time() - start_time) * 1000
                
                logger.debug(f"L1 Cache hit: {key}")
                return item.value
            else:
                self.stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        with self.lock:
            try:
                # Calculate item size
                value_json = json.dumps(value)
                size_bytes = len(value_json.encode('utf-8'))
                
                # Check memory limits
                if size_bytes > self.max_memory_bytes:
                    logger.warning(f"Item too large for L1 cache: {size_bytes} bytes")
                    return False
                
                # Evict if necessary
                self._evict_if_needed(size_bytes)
                
                # Create cache item
                item = CacheItem(
                    key=key,
                    value=value,
                    ttl=ttl,
                    created_at=time.time(),
                    size_bytes=size_bytes
                )
                
                self.cache[key] = item
                self.stats.sets += 1
                self.stats.total_size_bytes += size_bytes
                
                logger.debug(f"L1 Cache set: {key} ({size_bytes} bytes)")
                return True
                
            except Exception as e:
                logger.error(f"L1 Cache set error: {str(e)}")
                return False
    
    def delete(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                item = self.cache[key]
                self.stats.total_size_bytes -= item.size_bytes
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> bool:
        with self.lock:
            self.cache.clear()
            self.stats.total_size_bytes = 0
            return True
    
    def _evict_if_needed(self, new_item_size: int):
        """Evict items using LRU policy"""
        # Check size limit
        while len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Check memory limit
        while (self.stats.total_size_bytes + new_item_size) > self.max_memory_bytes:
            if not self._evict_lru():
                break
    
    def _evict_lru(self) -> bool:
        """Evict least recently used item"""
        if not self.cache:
            return False
        
        # Find LRU item
        lru_key = min(self.cache.keys(), 
                     key=lambda k: self.cache[k].last_accessed or self.cache[k].created_at)
        
        item = self.cache[lru_key]
        self.stats.total_size_bytes -= item.size_bytes
        self.stats.evictions += 1
        del self.cache[lru_key]
        
        logger.debug(f"L1 Cache evicted: {lru_key}")
        return True
    
    def get_stats(self) -> CacheStats:
        return self.stats

class L2LocalRedisCache(CacheLevel):
    """
    L2 Cache - Local Redis instance
    Fast local Redis cache - Mumbai metro जैसी speed
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.stats = CacheStats("L2-LocalRedis")
        
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            self.redis_client.ping()
            self.available = True
            logger.info(f"✅ L2 Local Redis Cache connected - {host}:{port}")
        except Exception as e:
            logger.warning(f"⚠️ L2 Redis not available: {str(e)}")
            self.available = False
    
    def get(self, key: str) -> Optional[Any]:
        if not self.available:
            self.stats.misses += 1
            return None
        
        start_time = time.time()
        
        try:
            value = self.redis_client.get(f"l2:{key}")
            
            if value:
                self.stats.hits += 1
                self.stats.avg_access_time_ms = (time.time() - start_time) * 1000
                logger.debug(f"L2 Cache hit: {key}")
                return json.loads(value)
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"L2 Cache get error: {str(e)}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if not self.available:
            return False
        
        try:
            value_json = json.dumps(value)
            self.redis_client.setex(f"l2:{key}", ttl, value_json)
            self.stats.sets += 1
            logger.debug(f"L2 Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"L2 Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.available:
            return False
        
        try:
            return bool(self.redis_client.delete(f"l2:{key}"))
        except Exception as e:
            logger.error(f"L2 Cache delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        if not self.available:
            return False
        
        try:
            # Clear only L2 keys
            keys = self.redis_client.keys("l2:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"L2 Cache clear error: {str(e)}")
            return False
    
    def get_stats(self) -> CacheStats:
        return self.stats

class L3DistributedCache(CacheLevel):
    """
    L3 Cache - Distributed Redis Cluster
    Distributed cache - Mumbai से Pune जैसी speed
    """
    
    def __init__(self, cluster_nodes: List[str] = None):
        self.stats = CacheStats("L3-Distributed")
        self.cluster_nodes = cluster_nodes or ['localhost:6380', 'localhost:6381']
        
        try:
            # Simulate cluster connection (in real implementation, use Redis Cluster)
            self.redis_client = redis.Redis(
                host='localhost', port=6380, db=1,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.redis_client.ping()
            self.available = True
            logger.info(f"✅ L3 Distributed Cache connected to cluster")
        except Exception as e:
            logger.warning(f"⚠️ L3 Distributed cache not available: {str(e)}")
            self.available = False
    
    def get(self, key: str) -> Optional[Any]:
        if not self.available:
            self.stats.misses += 1
            return None
        
        start_time = time.time()
        
        # Simulate network latency
        time.sleep(0.02)  # 20ms network latency
        
        try:
            value = self.redis_client.get(f"l3:{key}")
            
            if value:
                self.stats.hits += 1
                self.stats.avg_access_time_ms = (time.time() - start_time) * 1000
                logger.debug(f"L3 Cache hit: {key}")
                return json.loads(value)
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"L3 Cache get error: {str(e)}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        if not self.available:
            return False
        
        # Simulate network latency
        time.sleep(0.02)  # 20ms network latency
        
        try:
            value_json = json.dumps(value)
            self.redis_client.setex(f"l3:{key}", ttl, value_json)
            self.stats.sets += 1
            logger.debug(f"L3 Cache set: {key}")
            return True
        except Exception as e:
            logger.error(f"L3 Cache set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        if not self.available:
            return False
        
        try:
            return bool(self.redis_client.delete(f"l3:{key}"))
        except Exception as e:
            logger.error(f"L3 Cache delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        if not self.available:
            return False
        
        try:
            keys = self.redis_client.keys("l3:*")
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"L3 Cache clear error: {str(e)}")
            return False
    
    def get_stats(self) -> CacheStats:
        return self.stats

class L4CDNCache(CacheLevel):
    """
    L4 Cache - CDN Cache (CloudFlare/AWS CloudFront simulation)
    CDN caching for static assets - Delhi से Mumbai जैसी speed
    """
    
    def __init__(self, cdn_base_url: str = "https://cdn.flipkart.com"):
        self.stats = CacheStats("L4-CDN")
        self.cdn_base_url = cdn_base_url
        self.available = True  # Assume CDN is always available
        
        # Simulate CDN cache with local storage
        self.cdn_cache = {}
        
        logger.info(f"🌍 L4 CDN Cache initialized - Base URL: {cdn_base_url}")
    
    def get(self, key: str) -> Optional[Any]:
        start_time = time.time()
        
        # Simulate CDN latency
        time.sleep(0.05)  # 50ms CDN latency
        
        try:
            if key in self.cdn_cache:
                item = self.cdn_cache[key]
                
                # Check TTL
                if time.time() - item['created_at'] > item['ttl']:
                    del self.cdn_cache[key]
                    self.stats.misses += 1
                    return None
                
                self.stats.hits += 1
                self.stats.avg_access_time_ms = (time.time() - start_time) * 1000
                logger.debug(f"L4 CDN hit: {key}")
                return item['value']
            else:
                self.stats.misses += 1
                return None
                
        except Exception as e:
            logger.error(f"L4 CDN get error: {str(e)}")
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 86400) -> bool:  # Default 24h TTL for CDN
        # Simulate CDN upload latency
        time.sleep(0.1)  # 100ms upload time
        
        try:
            self.cdn_cache[key] = {
                'value': value,
                'ttl': ttl,
                'created_at': time.time()
            }
            self.stats.sets += 1
            logger.debug(f"L4 CDN set: {key}")
            return True
        except Exception as e:
            logger.error(f"L4 CDN set error: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        try:
            if key in self.cdn_cache:
                del self.cdn_cache[key]
                return True
            return False
        except Exception as e:
            logger.error(f"L4 CDN delete error: {str(e)}")
            return False
    
    def clear(self) -> bool:
        try:
            self.cdn_cache.clear()
            return True
        except Exception as e:
            logger.error(f"L4 CDN clear error: {str(e)}")
            return False
    
    def get_stats(self) -> CacheStats:
        return self.stats

class DatabaseLayer:
    """
    Database layer - Final data source
    Simulated database - Real database access होगा production में
    """
    
    def __init__(self):
        # Simulated product database
        self.products_db = {
            'product_001': {
                'id': 'product_001',
                'name': 'iPhone 15 Pro Max',
                'price': 159900,
                'category': 'Smartphones',
                'brand': 'Apple',
                'description': 'Latest iPhone with A17 Pro chip',
                'images': ['iphone15-1.jpg', 'iphone15-2.jpg'],
                'rating': 4.5,
                'reviews': 12500,
                'in_stock': True
            },
            'product_002': {
                'id': 'product_002',
                'name': 'MacBook Pro 14"',
                'price': 199900,
                'category': 'Laptops',
                'brand': 'Apple',
                'description': 'M3 Pro chip with 18-core GPU',
                'images': ['macbook-1.jpg', 'macbook-2.jpg'],
                'rating': 4.7,
                'reviews': 8300,
                'in_stock': True
            },
            'product_003': {
                'id': 'product_003',
                'name': 'Samsung Galaxy S24 Ultra',
                'price': 124999,
                'category': 'Smartphones',
                'brand': 'Samsung',
                'description': 'AI-powered smartphone with S Pen',
                'images': ['s24-1.jpg', 's24-2.jpg'],
                'rating': 4.4,
                'reviews': 15600,
                'in_stock': False
            }
        }
        
        self.access_count = 0
        logger.info("💾 Database layer initialized with sample products")
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """Simulate database query with latency"""
        # Simulate database query latency
        time.sleep(0.2)  # 200ms database query time
        
        self.access_count += 1
        logger.info(f"💾 Database query: {product_id} (Total queries: {self.access_count})")
        
        return self.products_db.get(product_id)

class MultiLevelCacheManager:
    """
    Multi-Level Cache Manager
    4-tier caching system orchestrator
    """
    
    def __init__(self):
        # Initialize cache levels
        self.l1_cache = L1CPUCache(max_size=500, max_memory_mb=50)
        self.l2_cache = L2LocalRedisCache()
        self.l3_cache = L3DistributedCache()
        self.l4_cache = L4CDNCache()
        self.database = DatabaseLayer()
        
        # Cache promotion strategy
        self.promotion_threshold = 3  # Promote after 3 accesses
        self.access_tracking = {}
        
        logger.info("🏗️ Multi-Level Cache Manager initialized")
        logger.info("📋 Cache hierarchy: L1 (CPU) → L2 (Local Redis) → L3 (Distributed) → L4 (CDN) → Database")
    
    def get_product(self, product_id: str) -> Optional[Dict]:
        """
        Get product with multi-level cache hierarchy
        Cache hierarchy के through product data retrieve करते हैं
        """
        start_time = time.time()
        cache_level_hit = None
        
        # Track access for promotion strategy
        self.access_tracking[product_id] = self.access_tracking.get(product_id, 0) + 1
        
        # Try L1 Cache first
        product = self.l1_cache.get(product_id)
        if product is not None:
            cache_level_hit = "L1-CPU"
            total_time = (time.time() - start_time) * 1000
            logger.info(f"🚀 L1 Cache hit: {product_id} ({total_time:.1f}ms)")
            return product
        
        # Try L2 Cache
        product = self.l2_cache.get(product_id)
        if product is not None:
            cache_level_hit = "L2-LocalRedis"
            
            # Promote to L1 if frequently accessed
            if self.access_tracking[product_id] >= self.promotion_threshold:
                self.l1_cache.set(product_id, product, ttl=1800)  # 30 min TTL for L1
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"⚡ L2 Cache hit: {product_id} ({total_time:.1f}ms)")
            return product
        
        # Try L3 Cache
        product = self.l3_cache.get(product_id)
        if product is not None:
            cache_level_hit = "L3-Distributed"
            
            # Promote to L2 and possibly L1
            self.l2_cache.set(product_id, product, ttl=3600)  # 1 hour TTL for L2
            if self.access_tracking[product_id] >= self.promotion_threshold:
                self.l1_cache.set(product_id, product, ttl=1800)
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"🌐 L3 Cache hit: {product_id} ({total_time:.1f}ms)")
            return product
        
        # Try L4 CDN Cache
        product = self.l4_cache.get(product_id)
        if product is not None:
            cache_level_hit = "L4-CDN"
            
            # Promote to all lower levels
            self.l3_cache.set(product_id, product, ttl=7200)   # 2 hours TTL for L3
            self.l2_cache.set(product_id, product, ttl=3600)   # 1 hour TTL for L2
            if self.access_tracking[product_id] >= self.promotion_threshold:
                self.l1_cache.set(product_id, product, ttl=1800)
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"🌍 L4 CDN hit: {product_id} ({total_time:.1f}ms)")
            return product
        
        # Cache miss - fetch from database
        product = self.database.get_product(product_id)
        if product is not None:
            # Store in all cache levels (write-through)
            self.l4_cache.set(product_id, product, ttl=86400)  # 24 hours TTL for CDN
            self.l3_cache.set(product_id, product, ttl=7200)   # 2 hours TTL for L3
            self.l2_cache.set(product_id, product, ttl=3600)   # 1 hour TTL for L2
            
            # Only store in L1 if it's a hot item
            if self.access_tracking[product_id] >= self.promotion_threshold:
                self.l1_cache.set(product_id, product, ttl=1800)
            
            total_time = (time.time() - start_time) * 1000
            logger.info(f"💾 Database hit: {product_id} ({total_time:.1f}ms)")
            return product
        
        total_time = (time.time() - start_time) * 1000
        logger.warning(f"❌ Product not found: {product_id} ({total_time:.1f}ms)")
        return None
    
    def set_product(self, product_id: str, product_data: Dict, invalidate_cache: bool = True):
        """
        Update product data and manage cache invalidation
        Product update के साथ cache invalidation
        """
        # Update database
        self.database.products_db[product_id] = product_data
        
        if invalidate_cache:
            # Invalidate all cache levels
            self.l1_cache.delete(product_id)
            self.l2_cache.delete(product_id)
            self.l3_cache.delete(product_id)
            self.l4_cache.delete(product_id)
            
            logger.info(f"🔄 Cache invalidated for product: {product_id}")
        else:
            # Update all cache levels (write-through)
            self.l4_cache.set(product_id, product_data, ttl=86400)
            self.l3_cache.set(product_id, product_data, ttl=7200)
            self.l2_cache.set(product_id, product_data, ttl=3600)
            self.l1_cache.set(product_id, product_data, ttl=1800)
            
            logger.info(f"✅ Cache updated for product: {product_id}")
    
    def get_comprehensive_stats(self) -> Dict:
        """Get statistics from all cache levels"""
        stats = {}
        
        # Individual cache stats
        stats['l1'] = asdict(self.l1_cache.get_stats())
        stats['l2'] = asdict(self.l2_cache.get_stats())
        stats['l3'] = asdict(self.l3_cache.get_stats())
        stats['l4'] = asdict(self.l4_cache.get_stats())
        
        # Overall statistics
        total_hits = sum([stats[level]['hits'] for level in stats])
        total_misses = sum([stats[level]['misses'] for level in stats])
        total_requests = total_hits + total_misses
        
        stats['overall'] = {
            'total_requests': total_requests,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'overall_hit_ratio': (total_hits / total_requests * 100) if total_requests > 0 else 0,
            'database_queries': self.database.access_count,
            'cache_efficiency': ((total_requests - self.database.access_count) / total_requests * 100) if total_requests > 0 else 0
        }
        
        return stats
    
    def clear_all_caches(self):
        """Clear all cache levels"""
        self.l1_cache.clear()
        self.l2_cache.clear()
        self.l3_cache.clear()
        self.l4_cache.clear()
        self.access_tracking.clear()
        logger.info("🧹 All caches cleared")

def demo_multi_level_cache():
    """
    Demo multi-level cache hierarchy
    4-tier caching system का comprehensive demo
    """
    print("🏗️ Multi-Level Cache Hierarchy Demo")
    print("🛒 Flipkart Product Catalog Simulation")
    print("=" * 60)
    
    cache_manager = MultiLevelCacheManager()
    
    print("\n1. Cache Hierarchy Overview")
    print("-" * 35)
    print("🚀 L1: CPU Cache (In-Memory)      - ~1ms")
    print("⚡ L2: Local Redis              - ~5ms")
    print("🌐 L3: Distributed Redis Cluster - ~20ms")
    print("🌍 L4: CDN Cache                 - ~50ms")
    print("💾 Database: PostgreSQL/MongoDB  - ~200ms")
    
    products_to_test = ['product_001', 'product_002', 'product_003']
    
    print("\n2. First Access (Cold Cache)")
    print("-" * 35)
    
    # First access - all caches are cold
    for product_id in products_to_test:
        print(f"\n🔍 Fetching {product_id} (Cold cache):")
        start_time = time.time()
        
        product = cache_manager.get_product(product_id)
        access_time = (time.time() - start_time) * 1000
        
        if product:
            print(f"   ✅ {product['name']} - ₹{product['price']}")
            print(f"   ⏱️  Access time: {access_time:.1f}ms")
        else:
            print(f"   ❌ Product not found")
    
    print("\n3. Second Access (Warm Cache)")
    print("-" * 35)
    
    # Second access - should hit various cache levels
    for product_id in products_to_test:
        print(f"\n🔍 Fetching {product_id} (Warm cache):")
        start_time = time.time()
        
        product = cache_manager.get_product(product_id)
        access_time = (time.time() - start_time) * 1000
        
        if product:
            print(f"   ✅ {product['name']} - ₹{product['price']}")
            print(f"   ⚡ Access time: {access_time:.1f}ms (Much faster!)")
    
    print("\n4. Hot Item Simulation (L1 Promotion)")
    print("-" * 45)
    
    # Access product_001 multiple times to trigger L1 promotion
    hot_product = 'product_001'
    print(f"📈 Making {hot_product} a hot item (accessing 5 times):")
    
    for i in range(5):
        start_time = time.time()
        product = cache_manager.get_product(hot_product)
        access_time = (time.time() - start_time) * 1000
        print(f"   Access {i+1}: {access_time:.2f}ms")
    
    print("\n5. Cache Statistics Analysis")
    print("-" * 35)
    
    stats = cache_manager.get_comprehensive_stats()
    
    print("📊 Individual Cache Level Stats:")
    for level in ['l1', 'l2', 'l3', 'l4']:
        level_stats = stats[level]
        hit_ratio = (level_stats['hits'] / (level_stats['hits'] + level_stats['misses']) * 100) if (level_stats['hits'] + level_stats['misses']) > 0 else 0
        print(f"   {level_stats['level_name']:20}: Hits={level_stats['hits']:2}, Misses={level_stats['misses']:2}, Hit Ratio={hit_ratio:5.1f}%")
    
    overall = stats['overall']
    print(f"\n🎯 Overall Performance:")
    print(f"   Total Requests: {overall['total_requests']}")
    print(f"   Cache Hit Ratio: {overall['overall_hit_ratio']:.1f}%")
    print(f"   Database Queries: {overall['database_queries']}")
    print(f"   Cache Efficiency: {overall['cache_efficiency']:.1f}%")
    
    print("\n6. Cache Update and Invalidation")
    print("-" * 40)
    
    # Update a product and test invalidation
    product_to_update = 'product_001'
    print(f"📝 Updating {product_to_update} price...")
    
    # Get original product
    original_product = cache_manager.get_product(product_to_update)
    print(f"   Original price: ₹{original_product['price']}")
    
    # Update product with cache invalidation
    updated_product = original_product.copy()
    updated_product['price'] = 149900  # New price
    cache_manager.set_product(product_to_update, updated_product, invalidate_cache=True)
    
    # Fetch updated product
    new_product = cache_manager.get_product(product_to_update)
    print(f"   Updated price: ₹{new_product['price']}")
    
    print("\n7. Performance Comparison")
    print("-" * 30)
    
    # Performance comparison: with vs without cache
    cache_manager.clear_all_caches()
    
    print("🐌 Without cache (Database only):")
    no_cache_times = []
    for i in range(3):
        start_time = time.time()
        product = cache_manager.database.get_product('product_001')
        access_time = (time.time() - start_time) * 1000
        no_cache_times.append(access_time)
        print(f"   Query {i+1}: {access_time:.1f}ms")
    
    print("\n🚀 With multi-level cache:")
    cache_times = []
    for i in range(3):
        start_time = time.time()
        product = cache_manager.get_product('product_001')
        access_time = (time.time() - start_time) * 1000
        cache_times.append(access_time)
        print(f"   Query {i+1}: {access_time:.1f}ms")
    
    avg_no_cache = sum(no_cache_times) / len(no_cache_times)
    avg_with_cache = sum(cache_times) / len(cache_times)
    speedup = avg_no_cache / avg_with_cache
    
    print(f"\n📈 Performance Improvement:")
    print(f"   Average without cache: {avg_no_cache:.1f}ms")
    print(f"   Average with cache: {avg_with_cache:.1f}ms")
    print(f"   Speedup factor: {speedup:.1f}x faster")
    
    print("\n" + "=" * 60)
    print("🎉 Multi-Level Cache Demo Completed!")
    print("💡 Key Benefits:")
    print("   - Ultra-fast L1 cache for hot items")
    print("   - Automatic cache promotion based on access patterns")
    print("   - Fault tolerance - if one level fails, others continue")
    print("   - Optimal resource utilization across cache tiers")
    print("   - Scalable from single machine to global distribution")
    print("\n🏗️ Production Recommendations:")
    print("   - Monitor cache hit ratios per level")
    print("   - Tune TTL values based on data freshness requirements")
    print("   - Implement cache warming for critical data")
    print("   - Use consistent hashing for distributed cache")
    print("   - Set up alerting for cache failures")

if __name__ == "__main__":
    demo_multi_level_cache()