#!/usr/bin/env python3
"""
Multi-Level Caching System - Production-ready caching with Redis, Memcached, and in-memory
Flipkart-style product caching system

Author: Performance Engineering Team
Context: Mumbai ke dabbawala system ki tarah - different levels pe cache karte hain
"""

import redis
import memcache
import time
import json
import hashlib
import threading
from typing import Any, Optional, Dict, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from functools import wraps
from concurrent.futures import ThreadPoolExecutor
import pickle
import zlib

@dataclass
class CacheStats:
    """
    Cache statistics tracking - Flipkart analytics dashboard जैसे
    """
    level: str
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    last_updated: datetime = None

class FlipkartCacheLevel:
    """
    Individual cache level implementation - har level ka apna behavior
    """
    
    def __init__(self, name: str, max_size: int = 1000, ttl: int = 3600):
        self.name = name
        self.max_size = max_size
        self.ttl = ttl
        self.data = {}
        self.access_times = {}
        self.stats = CacheStats(level=name, last_updated=datetime.now())
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Cache se value retrieve करते हैं
        """
        with self._lock:
            if key in self.data:
                # Check TTL
                if self._is_expired(key):
                    self.delete(key)
                    self.stats.misses += 1
                    return None
                
                # Update access time for LRU
                self.access_times[key] = time.time()
                self.stats.hits += 1
                return self.data[key]['value']
            else:
                self.stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Cache में value set करते हैं
        """
        with self._lock:
            # Check if we need to evict
            if len(self.data) >= self.max_size and key not in self.data:
                self._evict_lru()
            
            ttl = ttl or self.ttl
            expiry_time = time.time() + ttl if ttl > 0 else None
            
            self.data[key] = {
                'value': value,
                'created_at': time.time(),
                'expiry_time': expiry_time,
                'access_count': 1,
                'size_bytes': len(str(value))  # Approximate size
            }
            self.access_times[key] = time.time()
            self.stats.sets += 1
            self._update_stats()
            return True
    
    def delete(self, key: str) -> bool:
        """
        Cache से value delete करते हैं
        """
        with self._lock:
            if key in self.data:
                del self.data[key]
                if key in self.access_times:
                    del self.access_times[key]
                self.stats.deletes += 1
                self._update_stats()
                return True
            return False
    
    def _is_expired(self, key: str) -> bool:
        """
        Check if key has expired
        """
        if key not in self.data:
            return True
        
        expiry_time = self.data[key].get('expiry_time')
        if expiry_time is None:
            return False
        
        return time.time() > expiry_time
    
    def _evict_lru(self):
        """
        LRU eviction - sabse kam use hone wala remove करते हैं
        """
        if not self.access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(lru_key)
        self.stats.evictions += 1
    
    def _update_stats(self):
        """
        Statistics update करते हैं
        """
        self.stats.total_size_bytes = sum(
            item['size_bytes'] for item in self.data.values()
        )
        self.stats.last_updated = datetime.now()
    
    def get_stats(self) -> CacheStats:
        """
        Cache statistics return करते हैं
        """
        return self.stats
    
    def clear(self):
        """
        Cache clear करते हैं
        """
        with self._lock:
            self.data.clear()
            self.access_times.clear()
            self.stats = CacheStats(level=self.name, last_updated=datetime.now())

class RedisCache:
    """
    Redis cache implementation - distributed caching के लिए
    """
    
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        try:
            self.redis_client = redis.Redis(
                host=host, port=port, db=db, password=password,
                decode_responses=False, socket_timeout=1
            )
            # Test connection
            self.redis_client.ping()
            self.available = True
        except:
            self.available = False
            self.redis_client = None
        
        self.stats = CacheStats(level='Redis', last_updated=datetime.now())
    
    def get(self, key: str) -> Optional[Any]:
        """
        Redis से value get करते हैं
        """
        if not self.available:
            self.stats.misses += 1
            return None
        
        try:
            data = self.redis_client.get(key)
            if data:
                # Decompress and deserialize
                decompressed = zlib.decompress(data)
                value = pickle.loads(decompressed)
                self.stats.hits += 1
                return value
            else:
                self.stats.misses += 1
                return None
        except Exception as e:
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Redis में value set करते हैं
        """
        if not self.available:
            return False
        
        try:
            # Serialize and compress
            serialized = pickle.dumps(value)
            compressed = zlib.compress(serialized)
            
            result = self.redis_client.setex(key, ttl, compressed)
            if result:
                self.stats.sets += 1
            return result
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        """
        Redis से value delete करते हैं
        """
        if not self.available:
            return False
        
        try:
            result = self.redis_client.delete(key)
            if result > 0:
                self.stats.deletes += 1
            return result > 0
        except Exception as e:
            return False

class MemcachedCache:
    """
    Memcached cache implementation
    """
    
    def __init__(self, servers=['127.0.0.1:11211']):
        try:
            self.mc = memcache.Client(servers)
            # Test connection
            self.mc.set('test_key', 'test_value', time=1)
            self.available = True
        except:
            self.available = False
            self.mc = None
        
        self.stats = CacheStats(level='Memcached', last_updated=datetime.now())
    
    def get(self, key: str) -> Optional[Any]:
        """
        Memcached से value get करते हैं
        """
        if not self.available:
            self.stats.misses += 1
            return None
        
        try:
            value = self.mc.get(key)
            if value is not None:
                self.stats.hits += 1
                return value
            else:
                self.stats.misses += 1
                return None
        except Exception as e:
            self.stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Memcached में value set करते हैं
        """
        if not self.available:
            return False
        
        try:
            result = self.mc.set(key, value, time=ttl)
            if result:
                self.stats.sets += 1
            return result
        except Exception as e:
            return False
    
    def delete(self, key: str) -> bool:
        """
        Memcached से value delete करते हैं
        """
        if not self.available:
            return False
        
        try:
            result = self.mc.delete(key)
            if result:
                self.stats.deletes += 1
            return result
        except Exception as e:
            return False

class FlipkartMultiLevelCache:
    """
    Multi-level cache system - L1: Memory, L2: Redis, L3: Memcached
    Mumbai local train की tarah - fast, medium, slow levels
    """
    
    def __init__(self, 
                 l1_size: int = 1000, l1_ttl: int = 300,  # 5 min
                 l2_ttl: int = 3600,                        # 1 hour
                 l3_ttl: int = 86400,                       # 1 day
                 redis_config: Optional[Dict] = None,
                 memcached_servers: Optional[List[str]] = None):
        
        # L1: In-memory cache (fastest)
        self.l1_cache = FlipkartCacheLevel('L1-Memory', l1_size, l1_ttl)
        
        # L2: Redis cache (medium speed, distributed)
        redis_config = redis_config or {}
        self.l2_cache = RedisCache(**redis_config)
        self.l2_ttl = l2_ttl
        
        # L3: Memcached (slower but large capacity)
        memcached_servers = memcached_servers or ['127.0.0.1:11211']
        self.l3_cache = MemcachedCache(memcached_servers)
        self.l3_ttl = l3_ttl
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Overall stats
        self.total_requests = 0
        self.cache_hierarchy_hits = {'L1': 0, 'L2': 0, 'L3': 0, 'MISS': 0}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Multi-level cache se value get करते हैं
        Flipkart product search की tarah - pehle fast cache check करते हैं
        """
        self.total_requests += 1
        
        # L1 (Memory) cache check
        value = self.l1_cache.get(key)
        if value is not None:
            self.cache_hierarchy_hits['L1'] += 1
            return value
        
        # L2 (Redis) cache check
        value = self.l2_cache.get(key)
        if value is not None:
            self.cache_hierarchy_hits['L2'] += 1
            # Populate L1 cache asynchronously
            self.executor.submit(self.l1_cache.set, key, value, self.l1_cache.ttl)
            return value
        
        # L3 (Memcached) cache check
        value = self.l3_cache.get(key)
        if value is not None:
            self.cache_hierarchy_hits['L3'] += 1
            # Populate upper levels asynchronously
            self.executor.submit(self._populate_upper_levels, key, value)
            return value
        
        # Cache miss
        self.cache_hierarchy_hits['MISS'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl_override: Optional[Dict[str, int]] = None) -> bool:
        """
        All cache levels में value set करते हैं
        """
        ttl_config = ttl_override or {}
        
        success_count = 0
        
        # Set in L1 (Memory)
        l1_ttl = ttl_config.get('L1', self.l1_cache.ttl)
        if self.l1_cache.set(key, value, l1_ttl):
            success_count += 1
        
        # Set in L2 (Redis) asynchronously
        l2_ttl = ttl_config.get('L2', self.l2_ttl)
        self.executor.submit(self.l2_cache.set, key, value, l2_ttl)
        
        # Set in L3 (Memcached) asynchronously
        l3_ttl = ttl_config.get('L3', self.l3_ttl)
        self.executor.submit(self.l3_cache.set, key, value, l3_ttl)
        
        return success_count > 0
    
    def delete(self, key: str) -> bool:
        """
        All cache levels se value delete करते हैं
        """
        results = []
        
        # Delete from all levels
        results.append(self.l1_cache.delete(key))
        
        # Async deletes for distributed caches
        future_l2 = self.executor.submit(self.l2_cache.delete, key)
        future_l3 = self.executor.submit(self.l3_cache.delete, key)
        
        # Wait for distributed cache deletes
        try:
            results.append(future_l2.result(timeout=1))
            results.append(future_l3.result(timeout=1))
        except:
            pass  # Don't fail if distributed caches are unavailable
        
        return any(results)
    
    def _populate_upper_levels(self, key: str, value: Any):
        """
        Upper cache levels को populate करते हैं
        """
        # Set in L1
        self.l1_cache.set(key, value, self.l1_cache.ttl)
        # Set in L2
        self.l2_cache.set(key, value, self.l2_ttl)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Complete cache statistics return करते हैं
        """
        hit_rate_l1 = (self.cache_hierarchy_hits['L1'] / self.total_requests * 100) if self.total_requests > 0 else 0
        hit_rate_l2 = (self.cache_hierarchy_hits['L2'] / self.total_requests * 100) if self.total_requests > 0 else 0
        hit_rate_l3 = (self.cache_hierarchy_hits['L3'] / self.total_requests * 100) if self.total_requests > 0 else 0
        overall_hit_rate = ((self.total_requests - self.cache_hierarchy_hits['MISS']) / self.total_requests * 100) if self.total_requests > 0 else 0
        
        return {
            'total_requests': self.total_requests,
            'cache_hierarchy_hits': self.cache_hierarchy_hits,
            'hit_rates': {
                'L1_memory': round(hit_rate_l1, 2),
                'L2_redis': round(hit_rate_l2, 2),
                'L3_memcached': round(hit_rate_l3, 2),
                'overall': round(overall_hit_rate, 2)
            },
            'individual_cache_stats': {
                'L1': asdict(self.l1_cache.get_stats()),
                'L2': asdict(self.l2_cache.stats),
                'L3': asdict(self.l3_cache.stats)
            },
            'cache_availability': {
                'L2_redis': self.l2_cache.available,
                'L3_memcached': self.l3_cache.available
            }
        }
    
    def clear_all_caches(self):
        """
        All cache levels clear करते हैं
        """
        self.l1_cache.clear()
        
        # Clear distributed caches asynchronously
        if self.l2_cache.available:
            self.executor.submit(self.l2_cache.redis_client.flushdb)
        
        # Memcached doesn't have a simple clear all, so we'll skip it
        # In production, you'd want to track keys or use namespaces
        
        # Reset stats
        self.total_requests = 0
        self.cache_hierarchy_hits = {'L1': 0, 'L2': 0, 'L3': 0, 'MISS': 0}

def flipkart_cache_decorator(cache_instance, ttl=3600, key_prefix=""):
    """
    Caching decorator - Flipkart product caching के लिए
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            key_parts.extend(str(arg) for arg in args)
            key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, {'L1': ttl, 'L2': ttl, 'L3': ttl})
            
            return result
        
        return wrapper
    return decorator

# Example usage - Flipkart product service simulation
class FlipkartProductService:
    """
    Flipkart product service with multi-level caching
    """
    
    def __init__(self):
        # Initialize multi-level cache
        self.cache = FlipkartMultiLevelCache(
            l1_size=500,  # 500 products in memory
            l1_ttl=300,   # 5 minutes
            l2_ttl=3600,  # 1 hour in Redis
            l3_ttl=86400  # 1 day in Memcached
        )
    
    @flipkart_cache_decorator(None, ttl=600, key_prefix="product")
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        Product details get करते हैं - database call simulate करते हैं
        """
        # Simulate database call delay
        time.sleep(0.1)  # 100ms database query
        
        # Simulate product data
        product = {
            'id': product_id,
            'name': f'Product {product_id}',
            'price': 999.99,
            'category': 'Electronics',
            'rating': 4.2,
            'reviews_count': 1250,
            'availability': 'In Stock',
            'description': f'High quality product {product_id} with excellent features',
            'images': [f'https://images.flipkart.com/{product_id}_1.jpg'],
            'specifications': {
                'brand': 'Flipkart Brand',
                'warranty': '1 Year',
                'color': 'Black'
            },
            'fetched_at': datetime.now().isoformat()
        }
        
        return product
    
    def get_product_details_cached(self, product_id: str) -> Dict[str, Any]:
        """
        Multi-level cache के साथ product details
        """
        cache_key = f"product:{product_id}"
        
        # Try cache first
        cached_product = self.cache.get(cache_key)
        if cached_product:
            cached_product['cache_hit'] = True
            return cached_product
        
        # Cache miss - fetch from database
        product = self.get_product_details(product_id)
        product['cache_hit'] = False
        
        # Store in cache
        self.cache.set(cache_key, product)
        
        return product
    
    @flipkart_cache_decorator(None, ttl=1800, key_prefix="search")
    def search_products(self, query: str, category: str = None, price_range: tuple = None) -> List[Dict]:
        """
        Product search with caching - heavy operation
        """
        # Simulate complex search query
        time.sleep(0.2)  # 200ms search operation
        
        # Generate mock search results
        results = []
        for i in range(20):  # Return 20 products
            product = {
                'id': f'PROD{i:04d}',
                'name': f'{query} Product {i+1}',
                'price': 500 + (i * 50),
                'rating': 3.5 + (i % 3) * 0.5,
                'image_url': f'https://images.flipkart.com/PROD{i:04d}.jpg',
                'category': category or 'General'
            }
            results.append(product)
        
        return results
    
    def search_products_cached(self, query: str, category: str = None, price_range: tuple = None) -> List[Dict]:
        """
        Cached product search
        """
        # Create cache key
        key_parts = ['search', query]
        if category:
            key_parts.append(f'cat:{category}')
        if price_range:
            key_parts.append(f'price:{price_range[0]}-{price_range[1]}')
        
        cache_key = hashlib.md5('|'.join(key_parts).encode()).hexdigest()
        
        # Try cache first
        cached_results = self.cache.get(cache_key)
        if cached_results:
            return {
                'results': cached_results,
                'cache_hit': True,
                'total_count': len(cached_results)
            }
        
        # Cache miss
        results = self.search_products(query, category, price_range)
        
        # Store in cache
        self.cache.set(cache_key, results)
        
        return {
            'results': results,
            'cache_hit': False,
            'total_count': len(results)
        }

def demonstrate_multilevel_caching():
    """
    Multi-level caching का demonstration
    """
    print("🛒 Flipkart Multi-Level Caching Demonstration")
    print("=" * 55)
    
    # Initialize service
    service = FlipkartProductService()
    
    # Test product details caching
    print("\n1. Product Details Caching Test:")
    print("-" * 35)
    
    product_id = "LAPTOP001"
    
    # First call - cache miss
    start_time = time.time()
    product1 = service.get_product_details_cached(product_id)
    time1 = time.time() - start_time
    print(f"First call (cache miss): {time1*1000:.2f}ms - Cache Hit: {product1['cache_hit']}")
    
    # Second call - should be cache hit
    start_time = time.time()
    product2 = service.get_product_details_cached(product_id)
    time2 = time.time() - start_time
    print(f"Second call (cache hit): {time2*1000:.2f}ms - Cache Hit: {product2['cache_hit']}")
    
    print(f"Performance improvement: {((time1-time2)/time1)*100:.1f}%")
    
    # Test search caching
    print("\n2. Product Search Caching Test:")
    print("-" * 35)
    
    search_query = "smartphone"
    
    # First search - cache miss
    start_time = time.time()
    results1 = service.search_products_cached(search_query, category="Electronics")
    time1 = time.time() - start_time
    print(f"First search (cache miss): {time1*1000:.2f}ms - Cache Hit: {results1['cache_hit']}")
    print(f"Results count: {results1['total_count']}")
    
    # Second search - should be cache hit
    start_time = time.time()
    results2 = service.search_products_cached(search_query, category="Electronics")
    time2 = time.time() - start_time
    print(f"Second search (cache hit): {time2*1000:.2f}ms - Cache Hit: {results2['cache_hit']}")
    
    print(f"Performance improvement: {((time1-time2)/time1)*100:.1f}%")
    
    # Cache multiple products to show hierarchy
    print("\n3. Cache Hierarchy Test:")
    print("-" * 25)
    
    product_ids = [f"PROD{i:03d}" for i in range(10)]
    
    # First round - populate cache
    print("Populating cache...")
    for pid in product_ids:
        service.get_product_details_cached(pid)
    
    # Second round - test cache hits
    print("Testing cache hits...")
    for pid in product_ids[:3]:
        product = service.get_product_details_cached(pid)
        print(f"Product {pid}: Cache Hit - {product['cache_hit']}")
    
    # Show cache statistics
    print("\n4. Cache Performance Statistics:")
    print("-" * 35)
    
    stats = service.cache.get_cache_stats()
    
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Overall Hit Rate: {stats['hit_rates']['overall']:.2f}%")
    print(f"L1 (Memory) Hit Rate: {stats['hit_rates']['L1_memory']:.2f}%")
    print(f"L2 (Redis) Hit Rate: {stats['hit_rates']['L2_redis']:.2f}%")
    print(f"L3 (Memcached) Hit Rate: {stats['hit_rates']['L3_memcached']:.2f}%")
    
    print(f"\nCache Availability:")
    print(f"Redis: {'✅' if stats['cache_availability']['L2_redis'] else '❌'}")
    print(f"Memcached: {'✅' if stats['cache_availability']['L3_memcached'] else '❌'}")
    
    print(f"\nIndividual Cache Stats:")
    for level, cache_stats in stats['individual_cache_stats'].items():
        print(f"{level}: Hits={cache_stats['hits']}, Misses={cache_stats['misses']}, Sets={cache_stats['sets']}")

if __name__ == "__main__":
    # Apply caching decorator to the service methods
    service = FlipkartProductService()
    service.get_product_details = flipkart_cache_decorator(service.cache, ttl=600, key_prefix="product")(service.get_product_details)
    service.search_products = flipkart_cache_decorator(service.cache, ttl=1800, key_prefix="search")(service.search_products)
    
    demonstrate_multilevel_caching()