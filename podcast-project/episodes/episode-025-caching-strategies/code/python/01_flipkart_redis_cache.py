#!/usr/bin/env python3
"""
Flipkart Product Catalog Redis Caching System
फ्लिपकार्ट style product catalog caching with Redis

Caching Strategies Implemented:
1. Cache-Aside Pattern - Application manages cache
2. TTL-based expiration - Products expire after time
3. Cache warming - Pre-load popular products
4. Multi-tier caching - L1 (memory) + L2 (Redis)
5. Cache invalidation - Update on inventory changes
6. Distributed caching - Multiple app instances share cache

Mumbai Use Cases:
- Big Billion Day sale load handling
- Product search result caching
- Category page caching
- User session caching
- Cart persistence across sessions

Author: Code Developer Agent for Hindi Tech Podcast
Episode: 25 - Caching Strategies (Redis Implementation)
"""

import redis
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import threading
from dataclasses import dataclass, asdict
import hashlib
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection setup
try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,  # Auto-decode bytes to strings
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )
    # Test connection
    redis_client.ping()
    redis_available = True
    logger.info("✅ Redis connection established")
except Exception as e:
    logger.warning(f"⚠️ Redis not available: {str(e)}")
    redis_available = False

# In-memory fallback cache
class MemoryCache:
    """Simple in-memory cache for fallback when Redis is not available"""
    def __init__(self):
        self._cache = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[str]:
        if key in self._expiry and time.time() > self._expiry[key]:
            self.delete(key)
            return None
        return self._cache.get(key)
    
    def set(self, key: str, value: str, ex: Optional[int] = None):
        self._cache[key] = value
        if ex:
            self._expiry[key] = time.time() + ex
    
    def delete(self, key: str):
        self._cache.pop(key, None)
        self._expiry.pop(key, None)
    
    def exists(self, key: str) -> bool:
        return key in self._cache
    
    def flushall(self):
        self._cache.clear()
        self._expiry.clear()

# Initialize cache client
cache_client = redis_client if redis_available else MemoryCache()

# Product data structures
@dataclass
class Product:
    """Flipkart product model"""
    product_id: str
    name: str
    brand: str
    category: str
    price: float
    mrp: float
    discount_percent: int
    rating: float
    review_count: int
    in_stock: bool
    stock_quantity: int
    description: str
    images: List[str]
    seller_name: str
    is_flipkart_assured: bool
    is_plus_product: bool
    delivery_days: int
    tags: List[str]
    created_at: str
    updated_at: str

@dataclass
class SearchResult:
    """Product search result with metadata"""
    query: str
    total_results: int
    products: List[Product]
    filters_applied: Dict[str, Any]
    search_time: float
    cached: bool = False

# Cache configuration
CACHE_CONFIG = {
    'product_ttl': 3600,      # 1 hour - Individual products
    'search_ttl': 1800,       # 30 minutes - Search results
    'category_ttl': 7200,     # 2 hours - Category pages
    'popular_ttl': 86400,     # 24 hours - Popular products
    'user_cart_ttl': 604800,  # 7 days - Shopping cart
    'session_ttl': 1800,      # 30 minutes - User sessions
    'warming_interval': 3600   # 1 hour - Cache warming frequency
}

# Cache key generators
def product_cache_key(product_id: str) -> str:
    """Generate product cache key"""
    return f"flipkart:product:{product_id}"

def search_cache_key(query: str, filters: Dict = None, page: int = 1) -> str:
    """Generate search results cache key with filters"""
    filter_hash = ""
    if filters:
        # Create deterministic hash from filters
        filter_str = json.dumps(filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
    
    return f"flipkart:search:{query}:filters:{filter_hash}:page:{page}"

def category_cache_key(category: str, subcategory: str = None) -> str:
    """Generate category page cache key"""
    key = f"flipkart:category:{category}"
    if subcategory:
        key += f":{subcategory}"
    return key

def user_cart_key(user_id: str) -> str:
    """Generate user cart cache key"""
    return f"flipkart:cart:{user_id}"

# Mock product database (Production में यह MongoDB/PostgreSQL होगा)
PRODUCTS_DB = {
    "MOBILE_IPHONE15": Product(
        product_id="MOBILE_IPHONE15",
        name="Apple iPhone 15",
        brand="Apple",
        category="Mobile",
        price=76900.0,
        mrp=79900.0,
        discount_percent=4,
        rating=4.4,
        review_count=15420,
        in_stock=True,
        stock_quantity=45,
        description="Latest iPhone with advanced camera system",
        images=["iphone15-1.jpg", "iphone15-2.jpg"],
        seller_name="Flipkart Retail Ltd.",
        is_flipkart_assured=True,
        is_plus_product=True,
        delivery_days=1,
        tags=["smartphone", "apple", "5g", "premium"],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    ),
    
    "BOOK_SYSTEM_DESIGN": Product(
        product_id="BOOK_SYSTEM_DESIGN", 
        name="System Design Interview Book",
        brand="Tech Publications",
        category="Books",
        price=1049.0,
        mrp=1499.0,
        discount_percent=30,
        rating=4.7,
        review_count=2840,
        in_stock=True,
        stock_quantity=120,
        description="Complete guide for system design interviews",
        images=["system-design-book.jpg"],
        seller_name="Book Paradise",
        is_flipkart_assured=False,
        is_plus_product=False,
        delivery_days=3,
        tags=["technical", "interview", "system-design"],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    ),
    
    "LAPTOP_DELL_INSPIRON": Product(
        product_id="LAPTOP_DELL_INSPIRON",
        name="Dell Inspiron 15 3000 Laptop",
        brand="Dell",
        category="Laptops",
        price=45999.0,
        mrp=52999.0,
        discount_percent=13,
        rating=4.1,
        review_count=8920,
        in_stock=True,
        stock_quantity=25,
        description="Intel Core i5, 8GB RAM, 512GB SSD",
        images=["dell-inspiron-1.jpg", "dell-inspiron-2.jpg"],
        seller_name="Dell Exclusive Store",
        is_flipkart_assured=True,
        is_plus_product=True,
        delivery_days=2,
        tags=["laptop", "dell", "core-i5", "business"],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
}

# Popular products for cache warming (Big Billion Day style)
POPULAR_PRODUCTS = [
    "MOBILE_IPHONE15",
    "LAPTOP_DELL_INSPIRON", 
    "BOOK_SYSTEM_DESIGN"
]

class FlipkartCacheManager:
    """
    Comprehensive cache management for Flipkart-style e-commerce
    Multi-tier caching with Redis as primary and memory as fallback
    """
    
    def __init__(self):
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_sets': 0,
            'cache_invalidations': 0
        }
        
        # L1 Cache - In-memory for ultra-fast access
        self.l1_cache = {}
        self.l1_max_size = 1000  # Max items in L1 cache
        
        logger.info("🏪 Flipkart Cache Manager initialized")
        if redis_available:
            logger.info("✅ Using Redis (L2) + Memory (L1) caching")
        else:
            logger.info("⚠️ Using Memory-only caching")
    
    def _get_from_l1(self, key: str) -> Optional[str]:
        """Get from L1 (memory) cache"""
        return self.l1_cache.get(key)
    
    def _set_to_l1(self, key: str, value: str):
        """Set to L1 cache with size limit"""
        if len(self.l1_cache) >= self.l1_max_size:
            # Remove oldest item (simple FIFO)
            oldest_key = next(iter(self.l1_cache))
            del self.l1_cache[oldest_key]
        
        self.l1_cache[key] = value
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Get product with multi-tier caching
        L1 (Memory) → L2 (Redis) → Database
        """
        cache_key = product_cache_key(product_id)
        
        # Try L1 cache first
        l1_data = self._get_from_l1(cache_key)
        if l1_data:
            logger.debug(f"L1 Cache hit for product: {product_id}")
            self.stats['cache_hits'] += 1
            return Product(**json.loads(l1_data))
        
        # Try L2 cache (Redis)
        try:
            cached_data = cache_client.get(cache_key)
            if cached_data:
                logger.info(f"L2 Cache hit for product: {product_id}")
                self.stats['cache_hits'] += 1
                
                # Store in L1 for next access
                self._set_to_l1(cache_key, cached_data)
                
                return Product(**json.loads(cached_data))
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
        
        # Cache miss - fetch from database
        logger.info(f"Cache miss for product: {product_id}")
        self.stats['cache_misses'] += 1
        
        if product_id in PRODUCTS_DB:
            product = PRODUCTS_DB[product_id]
            
            # Store in both caches
            self.set_product(product)
            
            return product
        
        return None
    
    def set_product(self, product: Product) -> bool:
        """
        Store product in cache with TTL
        """
        cache_key = product_cache_key(product.product_id)
        product_data = json.dumps(asdict(product))
        
        try:
            # Set in L2 cache (Redis) with TTL
            cache_client.set(cache_key, product_data, ex=CACHE_CONFIG['product_ttl'])
            
            # Set in L1 cache
            self._set_to_l1(cache_key, product_data)
            
            self.stats['cache_sets'] += 1
            logger.debug(f"Product cached: {product.product_id}")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    def search_products(self, query: str, filters: Dict = None, page: int = 1, limit: int = 20) -> SearchResult:
        """
        Product search with result caching
        """
        start_time = time.time()
        cache_key = search_cache_key(query, filters, page)
        
        # Try cache first
        try:
            cached_result = cache_client.get(cache_key)
            if cached_result:
                logger.info(f"Search cache hit: {query}")
                self.stats['cache_hits'] += 1
                
                search_data = json.loads(cached_result)
                # Reconstruct SearchResult with products
                products = [Product(**p) for p in search_data['products']]
                
                return SearchResult(
                    query=search_data['query'],
                    total_results=search_data['total_results'],
                    products=products,
                    filters_applied=search_data['filters_applied'],
                    search_time=time.time() - start_time,
                    cached=True
                )
        except Exception as e:
            logger.error(f"Search cache error: {str(e)}")
        
        # Cache miss - perform search
        logger.info(f"Search cache miss: {query}")
        self.stats['cache_misses'] += 1
        
        # Mock search logic
        matching_products = []
        for product_id, product in PRODUCTS_DB.items():
            if (query.lower() in product.name.lower() or 
                query.lower() in product.category.lower() or
                query.lower() in product.brand.lower()):
                
                # Apply filters
                if self._apply_filters(product, filters or {}):
                    matching_products.append(product)
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        page_products = matching_products[start_idx:end_idx]
        
        search_result = SearchResult(
            query=query,
            total_results=len(matching_products),
            products=page_products,
            filters_applied=filters or {},
            search_time=time.time() - start_time,
            cached=False
        )
        
        # Cache the result
        self.cache_search_result(search_result, cache_key)
        
        return search_result
    
    def _apply_filters(self, product: Product, filters: Dict) -> bool:
        """Apply search filters to product"""
        if 'min_price' in filters and product.price < filters['min_price']:
            return False
        if 'max_price' in filters and product.price > filters['max_price']:
            return False
        if 'brand' in filters and product.brand.lower() != filters['brand'].lower():
            return False
        if 'category' in filters and product.category.lower() != filters['category'].lower():
            return False
        if 'in_stock' in filters and filters['in_stock'] and not product.in_stock:
            return False
        
        return True
    
    def cache_search_result(self, search_result: SearchResult, cache_key: str):
        """Cache search result"""
        try:
            # Convert to serializable format
            cache_data = {
                'query': search_result.query,
                'total_results': search_result.total_results,
                'products': [asdict(p) for p in search_result.products],
                'filters_applied': search_result.filters_applied,
                'cached_at': datetime.now().isoformat()
            }
            
            cache_client.set(cache_key, json.dumps(cache_data), ex=CACHE_CONFIG['search_ttl'])
            self.stats['cache_sets'] += 1
            
        except Exception as e:
            logger.error(f"Search cache set error: {str(e)}")
    
    def get_user_cart(self, user_id: str) -> Dict:
        """Get user's shopping cart from cache"""
        cache_key = user_cart_key(user_id)
        
        try:
            cart_data = cache_client.get(cache_key)
            if cart_data:
                logger.info(f"Cart cache hit for user: {user_id}")
                self.stats['cache_hits'] += 1
                return json.loads(cart_data)
        except Exception as e:
            logger.error(f"Cart cache error: {str(e)}")
        
        # Return empty cart if not cached
        logger.info(f"Cart cache miss for user: {user_id}")
        self.stats['cache_misses'] += 1
        return {'user_id': user_id, 'items': [], 'total_amount': 0.0, 'item_count': 0}
    
    def update_user_cart(self, user_id: str, cart_data: Dict) -> bool:
        """Update user's cart in cache"""
        cache_key = user_cart_key(user_id)
        
        try:
            cart_data['updated_at'] = datetime.now().isoformat()
            cache_client.set(cache_key, json.dumps(cart_data), ex=CACHE_CONFIG['user_cart_ttl'])
            self.stats['cache_sets'] += 1
            logger.info(f"Cart updated for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Cart update error: {str(e)}")
            return False
    
    def invalidate_product(self, product_id: str):
        """
        Invalidate product from all cache levels
        When inventory or price changes
        """
        cache_key = product_cache_key(product_id)
        
        try:
            # Remove from L2 (Redis)
            cache_client.delete(cache_key)
            
            # Remove from L1 (Memory)
            self.l1_cache.pop(cache_key, None)
            
            self.stats['cache_invalidations'] += 1
            logger.info(f"Product cache invalidated: {product_id}")
            
            # Also invalidate related search results (simplified approach)
            # In production, you'd use cache tags or more sophisticated invalidation
            if redis_available:
                pattern = f"flipkart:search:*"
                for key in redis_client.scan_iter(match=pattern):
                    redis_client.delete(key)
                logger.info("Related search caches invalidated")
                
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")
    
    def warm_cache(self):
        """
        Cache warming - Pre-load popular products
        Big Billion Day के लिए popular products को पहले से cache में load कर देते हैं
        """
        logger.info("🔥 Starting cache warming for popular products...")
        
        warmed_count = 0
        for product_id in POPULAR_PRODUCTS:
            if product_id in PRODUCTS_DB:
                product = PRODUCTS_DB[product_id]
                if self.set_product(product):
                    warmed_count += 1
                    logger.debug(f"Warmed cache for: {product.name}")
        
        logger.info(f"✅ Cache warming completed: {warmed_count} products pre-loaded")
    
    def get_cache_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        try:
            redis_info = {}
            if redis_available:
                info = redis_client.info()
                redis_info = {
                    'redis_connected_clients': info.get('connected_clients', 0),
                    'redis_used_memory_human': info.get('used_memory_human', '0B'),
                    'redis_keyspace_hits': info.get('keyspace_hits', 0),
                    'redis_keyspace_misses': info.get('keyspace_misses', 0),
                    'redis_evicted_keys': info.get('evicted_keys', 0)
                }
        except Exception:
            redis_info = {'error': 'Redis stats unavailable'}
        
        # Calculate hit ratio
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_ratio = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'application_stats': self.stats,
            'hit_ratio_percent': round(hit_ratio, 2),
            'l1_cache_size': len(self.l1_cache),
            'l1_cache_max_size': self.l1_max_size,
            'redis_stats': redis_info,
            'cache_config': CACHE_CONFIG,
            'cache_status': 'Redis + Memory' if redis_available else 'Memory Only'
        }

# Background cache warming scheduler
def cache_warming_scheduler(cache_manager: FlipkartCacheManager):
    """Background thread for periodic cache warming"""
    while True:
        try:
            time.sleep(CACHE_CONFIG['warming_interval'])
            cache_manager.warm_cache()
        except Exception as e:
            logger.error(f"Cache warming error: {str(e)}")
            time.sleep(60)  # Wait 1 minute on error

# Demo and testing functions
def demo_flipkart_caching():
    """
    Comprehensive demo of Flipkart caching patterns
    Mumbai Big Billion Day simulation
    """
    print("🏪 Flipkart Redis Caching System Demo")
    print("="*50)
    
    cache_manager = FlipkartCacheManager()
    
    # Start cache warming thread
    warming_thread = threading.Thread(target=cache_warming_scheduler, args=(cache_manager,), daemon=True)
    warming_thread.start()
    
    print("\n1. Initial Cache Warming (Big Billion Day prep)")
    cache_manager.warm_cache()
    
    print("\n2. Product Retrieval Tests")
    
    # Test product cache hit
    print("\n   Testing product cache hit:")
    start_time = time.time()
    product = cache_manager.get_product("MOBILE_IPHONE15")
    if product:
        print(f"   ✅ Retrieved: {product.name}")
        print(f"   📈 Price: ₹{product.price} (from cache)")
        print(f"   ⚡ Response time: {(time.time() - start_time)*1000:.2f}ms")
    
    # Test product cache miss
    print("\n   Testing product cache miss:")
    start_time = time.time()
    product = cache_manager.get_product("NONEXISTENT_PRODUCT")
    print(f"   ❌ Product not found")
    print(f"   ⚡ Response time: {(time.time() - start_time)*1000:.2f}ms")
    
    print("\n3. Product Search with Caching")
    
    # First search (cache miss)
    print("\n   First search - Cache miss:")
    start_time = time.time()
    results = cache_manager.search_products("phone", filters={'min_price': 50000})
    print(f"   🔍 Search: 'phone' with filters")
    print(f"   📊 Results: {results.total_results} products found")
    print(f"   ⚡ Search time: {results.search_time*1000:.2f}ms")
    print(f"   💾 Cached: {results.cached}")
    
    # Same search again (cache hit)
    print("\n   Same search again - Cache hit:")
    start_time = time.time()
    results = cache_manager.search_products("phone", filters={'min_price': 50000})
    print(f"   🔍 Search: 'phone' with filters")
    print(f"   📊 Results: {results.total_results} products found")
    print(f"   ⚡ Search time: {results.search_time*1000:.2f}ms")
    print(f"   💾 Cached: {results.cached}")
    
    print("\n4. Shopping Cart Operations")
    
    # Test user cart operations
    user_id = "user_mumbai_123"
    
    # Get empty cart
    cart = cache_manager.get_user_cart(user_id)
    print(f"   🛒 Initial cart for {user_id}: {cart['item_count']} items")
    
    # Add items to cart
    cart['items'] = [
        {'product_id': 'MOBILE_IPHONE15', 'quantity': 1, 'price': 76900.0},
        {'product_id': 'BOOK_SYSTEM_DESIGN', 'quantity': 2, 'price': 1049.0}
    ]
    cart['item_count'] = 3
    cart['total_amount'] = 76900.0 + (1049.0 * 2)
    
    cache_manager.update_user_cart(user_id, cart)
    print(f"   ✅ Cart updated: {cart['item_count']} items, ₹{cart['total_amount']}")
    
    # Retrieve updated cart
    cached_cart = cache_manager.get_user_cart(user_id)
    print(f"   🛒 Retrieved cart: {cached_cart['item_count']} items")
    
    print("\n5. Cache Invalidation Test")
    
    # Update product (simulate inventory change)
    print("   📦 Simulating inventory update...")
    cache_manager.invalidate_product("MOBILE_IPHONE15")
    
    # Update product in database
    PRODUCTS_DB["MOBILE_IPHONE15"].stock_quantity = 10
    PRODUCTS_DB["MOBILE_IPHONE15"].updated_at = datetime.now().isoformat()
    
    # Fetch again (should be cache miss and get updated data)
    updated_product = cache_manager.get_product("MOBILE_IPHONE15")
    print(f"   ✅ Updated stock: {updated_product.stock_quantity} units")
    
    print("\n6. Cache Statistics")
    stats = cache_manager.get_cache_stats()
    print(f"   📊 Cache Hit Ratio: {stats['hit_ratio_percent']}%")
    print(f"   🎯 Cache Hits: {stats['application_stats']['cache_hits']}")
    print(f"   ❌ Cache Misses: {stats['application_stats']['cache_misses']}")
    print(f"   💾 L1 Cache Size: {stats['l1_cache_size']}/{stats['l1_cache_max_size']}")
    print(f"   🔄 Cache Status: {stats['cache_status']}")
    
    if 'redis_stats' in stats and 'error' not in stats['redis_stats']:
        redis_stats = stats['redis_stats']
        print(f"   🔴 Redis Memory: {redis_stats.get('redis_used_memory_human', 'N/A')}")
        print(f"   👥 Redis Clients: {redis_stats.get('redis_connected_clients', 'N/A')}")
    
    print("\n" + "="*50)
    print("🎉 Flipkart caching demo completed!")
    print("Mumbai से Delhi tak - सभी products cached efficiently!")
    
    return cache_manager

if __name__ == '__main__':
    demo_flipkart_caching()