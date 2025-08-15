#!/usr/bin/env python3
"""
14_graphql_caching_strategies.py
GraphQL Caching Strategies - Redis, In-Memory, और Database-level caching
Indian e-commerce scale के लिए optimized caching patterns
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import aioredis
import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List as GrapheneList, Field, Schema
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from starlette.graphql import GraphQLApp
import pickle

# Cache Strategy Enums
class CacheStrategy(Enum):
    NO_CACHE = "no_cache"
    MEMORY_CACHE = "memory_cache"
    REDIS_CACHE = "redis_cache"
    DATABASE_CACHE = "database_cache"
    HYBRID_CACHE = "hybrid_cache"
    CDN_CACHE = "cdn_cache"

class CacheTTL(Enum):
    VERY_SHORT = 30      # 30 seconds - real-time data
    SHORT = 300          # 5 minutes - frequently changing
    MEDIUM = 1800        # 30 minutes - moderate changes  
    LONG = 3600          # 1 hour - stable data
    VERY_LONG = 86400    # 24 hours - rarely changing
    PERMANENT = 31536000 # 1 year - static data

# Data Models for Indian E-commerce
@dataclass
class Product:
    id: str
    name: str
    price: float
    original_price: float
    discount_percentage: float
    brand: str
    category: str
    seller_id: str
    stock_count: int
    rating: float
    review_count: int
    image_urls: List[str]
    specifications: Dict[str, str]
    is_bestseller: bool = False
    is_prime_eligible: bool = False
    delivery_time: str = "2-3 days"
    created_at: str = ""
    updated_at: str = ""

@dataclass  
class Seller:
    id: str
    name: str
    business_name: str
    city: str
    state: str
    rating: float
    total_products: int
    years_in_business: int
    is_verified: bool = True
    fulfillment_speed: str = "same-day"

@dataclass
class Category:
    id: str
    name: str
    parent_id: Optional[str]
    level: int
    product_count: int
    popular_brands: List[str]
    trending_keywords: List[str]

@dataclass
class Review:
    id: str
    product_id: str
    user_id: str
    rating: int
    title: str
    comment: str
    verified_purchase: bool
    helpful_votes: int
    created_at: str

# Advanced Caching System
class GraphQLCacheManager:
    def __init__(self):
        self.memory_cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        self.cache_hit_stats: Dict[str, int] = {}
        self.cache_miss_stats: Dict[str, int] = {}
        self.redis_client: Optional[aioredis.Redis] = None
        
        # Cache configuration for different query types
        self.cache_configs = {
            # Product queries - महंगे operations हैं
            'product': {'strategy': CacheStrategy.HYBRID_CACHE, 'ttl': CacheTTL.MEDIUM.value},
            'products_by_category': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.SHORT.value},
            'popular_products': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.VERY_SHORT.value},
            'trending_products': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.SHORT.value},
            
            # Search queries - बहुत expensive हैं
            'search_products': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.SHORT.value},
            'search_suggestions': {'strategy': CacheStrategy.MEMORY_CACHE, 'ttl': CacheTTL.MEDIUM.value},
            
            # Seller queries - कम frequently change होते हैं
            'seller': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.LONG.value},
            'seller_products': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.MEDIUM.value},
            
            # Category queries - very stable data
            'categories': {'strategy': CacheStrategy.MEMORY_CACHE, 'ttl': CacheTTL.VERY_LONG.value},
            'category_tree': {'strategy': CacheStrategy.MEMORY_CACHE, 'ttl': CacheTTL.VERY_LONG.value},
            
            # Review queries - moderate caching
            'product_reviews': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.MEDIUM.value},
            'review_stats': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.LONG.value},
            
            # Price queries - frequently changing during sales
            'price_comparison': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.VERY_SHORT.value},
            'flash_sale_prices': {'strategy': CacheStrategy.MEMORY_CACHE, 'ttl': CacheTTL.VERY_SHORT.value},
            
            # Analytics queries - expensive computations
            'analytics_dashboard': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.LONG.value},
            'trending_keywords': {'strategy': CacheStrategy.REDIS_CACHE, 'ttl': CacheTTL.MEDIUM.value}
        }
    
    async def initialize_redis(self):
        """Redis connection initialize करता है"""
        try:
            self.redis_client = aioredis.from_url("redis://localhost:6379", decode_responses=True)
            await self.redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}. Using memory cache only.")
            self.redis_client = None
    
    def get_cache_key(self, query_type: str, **kwargs) -> str:
        """Cache key generate करता है query parameters के साथ"""
        # Parameters को sort करके consistent key बनाते हैं
        params = sorted(kwargs.items())
        params_str = "&".join([f"{k}={v}" for k, v in params])
        
        # Hash करते हैं long keys के लिए
        if len(params_str) > 100:
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            return f"gql:{query_type}:{params_hash}"
        
        return f"gql:{query_type}:{params_str}"
    
    async def get_cached_data(self, cache_key: str, query_type: str) -> Optional[Any]:
        """Cache से data retrieve करता है"""
        config = self.cache_configs.get(query_type, {})
        strategy = config.get('strategy', CacheStrategy.NO_CACHE)
        
        if strategy == CacheStrategy.NO_CACHE:
            return None
        
        try:
            # Memory cache check (fastest)
            if strategy in [CacheStrategy.MEMORY_CACHE, CacheStrategy.HYBRID_CACHE]:
                if cache_key in self.memory_cache:
                    timestamp = self.cache_timestamps.get(cache_key)
                    if timestamp and (datetime.now() - timestamp).seconds < config.get('ttl', 300):
                        self.cache_hit_stats[query_type] = self.cache_hit_stats.get(query_type, 0) + 1
                        print(f"🎯 Memory cache HIT: {query_type}")
                        return self.memory_cache[cache_key]
                    else:
                        # Expired - remove from memory
                        del self.memory_cache[cache_key]
                        del self.cache_timestamps[cache_key]
            
            # Redis cache check
            if strategy in [CacheStrategy.REDIS_CACHE, CacheStrategy.HYBRID_CACHE] and self.redis_client:
                redis_data = await self.redis_client.get(cache_key)
                if redis_data:
                    self.cache_hit_stats[query_type] = self.cache_hit_stats.get(query_type, 0) + 1
                    print(f"🎯 Redis cache HIT: {query_type}")
                    
                    # Deserialize data
                    try:
                        return json.loads(redis_data)
                    except:
                        # Try pickle for complex objects
                        import base64
                        return pickle.loads(base64.b64decode(redis_data))
            
            # Cache miss
            self.cache_miss_stats[query_type] = self.cache_miss_stats.get(query_type, 0) + 1
            print(f"❌ Cache MISS: {query_type}")
            return None
            
        except Exception as e:
            print(f"❌ Cache retrieval error for {query_type}: {e}")
            return None
    
    async def set_cached_data(self, cache_key: str, data: Any, query_type: str):
        """Data को cache में store करता है"""
        config = self.cache_configs.get(query_type, {})
        strategy = config.get('strategy', CacheStrategy.NO_CACHE)
        ttl = config.get('ttl', 300)
        
        if strategy == CacheStrategy.NO_CACHE:
            return
        
        try:
            # Memory cache (for frequently accessed data)
            if strategy in [CacheStrategy.MEMORY_CACHE, CacheStrategy.HYBRID_CACHE]:
                self.memory_cache[cache_key] = data
                self.cache_timestamps[cache_key] = datetime.now()
                print(f"💾 Stored in memory cache: {query_type}")
                
                # Memory cache size management
                if len(self.memory_cache) > 1000:  # Limit memory usage
                    # Remove oldest entries
                    oldest_keys = sorted(self.cache_timestamps.items(), key=lambda x: x[1])[:100]
                    for key, _ in oldest_keys:
                        del self.memory_cache[key]
                        del self.cache_timestamps[key]
            
            # Redis cache  
            if strategy in [CacheStrategy.REDIS_CACHE, CacheStrategy.HYBRID_CACHE] and self.redis_client:
                try:
                    # Try JSON serialization first
                    serialized_data = json.dumps(data, default=str, ensure_ascii=False)
                except:
                    # Fall back to pickle for complex objects
                    import base64
                    serialized_data = base64.b64encode(pickle.dumps(data)).decode()
                
                await self.redis_client.setex(cache_key, ttl, serialized_data)
                print(f"💾 Stored in Redis cache: {query_type} (TTL: {ttl}s)")
                
        except Exception as e:
            print(f"❌ Cache storage error for {query_type}: {e}")
    
    async def invalidate_cache(self, pattern: str):
        """Cache invalidation - pattern के आधार पर"""
        try:
            # Memory cache invalidation
            keys_to_remove = [key for key in self.memory_cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
            
            print(f"🧹 Invalidated {len(keys_to_remove)} memory cache entries")
            
            # Redis cache invalidation
            if self.redis_client:
                keys = await self.redis_client.keys(f"*{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                    print(f"🧹 Invalidated {len(keys)} Redis cache entries")
                    
        except Exception as e:
            print(f"❌ Cache invalidation error: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Cache statistics return करता है"""
        total_hits = sum(self.cache_hit_stats.values())
        total_misses = sum(self.cache_miss_stats.values())
        total_requests = total_hits + total_misses
        
        hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'cache_hits': total_hits,
            'cache_misses': total_misses,
            'hit_rate_percentage': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'detailed_stats': {
                'hits_by_query_type': self.cache_hit_stats,
                'misses_by_query_type': self.cache_miss_stats
            }
        }

# Initialize cache manager
cache_manager = GraphQLCacheManager()

# Mock Database - Production में real database होगा
class MockDatabase:
    def __init__(self):
        self.products = self._generate_products()
        self.sellers = self._generate_sellers()
        self.categories = self._generate_categories()
        self.reviews = self._generate_reviews()
    
    def _generate_products(self) -> Dict[str, Product]:
        """Mock product data generate करता है"""
        print("🏪 Generating mock product data...")
        
        products = {}
        
        # Indian brands और products
        indian_products = [
            # Smartphones
            ("iPhone 15 Pro", "Apple", "smartphones", 134900, "Delhi Electronics"),
            ("Samsung Galaxy S24", "Samsung", "smartphones", 84999, "Mumbai Gadgets"),
            ("OnePlus 12", "OnePlus", "smartphones", 64999, "Bangalore Tech"),
            ("Realme GT Neo", "Realme", "smartphones", 23999, "Chennai Mobile"),
            ("Xiaomi 14", "Xiaomi", "smartphones", 54999, "Pune Electronics"),
            
            # Fashion
            ("Banarasi Silk Saree", "Traditional Weavers", "fashion", 12999, "Varanasi Textiles"),
            ("Khadi Cotton Kurta", "Fabindia", "fashion", 1899, "Delhi Fashion"),
            ("Leather Kolhapuri Chappals", "Kolhapuri", "footwear", 2499, "Maharashtra Leather"),
            ("Pashmina Shawl", "Kashmir Handicrafts", "fashion", 8999, "Srinagar Crafts"),
            
            # Books
            ("Wings of Fire", "APJ Abdul Kalam", "books", 399, "Agra Books"),
            ("Ramayana (Hindi)", "Tulsidas", "books", 599, "Ayodhya Publications"),
            ("Geetanjali", "Rabindranath Tagore", "books", 299, "Kolkata Literature"),
            
            # Electronics
            ("Bajaj Mixer Grinder", "Bajaj", "appliances", 4999, "Mumbai Appliances"),
            ("Prestige Pressure Cooker", "Prestige", "appliances", 2199, "Bangalore Kitchen"),
            ("Voltas Air Conditioner", "Voltas", "appliances", 35999, "Delhi Cooling"),
            
            # Sports
            ("Cricket Bat SS Ton", "SS", "sports", 5999, "Jalandhar Sports"),
            ("Football Nike", "Nike", "sports", 2999, "Mumbai Sports"),
            ("Badminton Racket Yonex", "Yonex", "sports", 8999, "Hyderabad Rackets")
        ]
        
        for i, (name, brand, category, price, seller) in enumerate(indian_products):
            product_id = str(i + 1)
            
            # Calculate discount
            original_price = price * (1 + 0.1 + (i % 5) * 0.05)  # 10-30% markup
            discount_pct = round((original_price - price) / original_price * 100)
            
            products[product_id] = Product(
                id=product_id,
                name=name,
                price=price,
                original_price=original_price,
                discount_percentage=discount_pct,
                brand=brand,
                category=category,
                seller_id=str((i % 10) + 1),
                stock_count=50 + (i % 100),
                rating=3.8 + (i % 15) * 0.1,
                review_count=100 + (i % 500),
                image_urls=[f"https://cdn.flipkart.com/{product_id}_1.jpg", f"https://cdn.flipkart.com/{product_id}_2.jpg"],
                specifications={
                    "Brand": brand,
                    "Category": category.title(),
                    "Made in": "India" if i % 3 == 0 else "China/Taiwan",
                    "Warranty": "1 year" if category == "electronics" else "No warranty",
                    "Color": ["Black", "White", "Red", "Blue", "Gold"][i % 5]
                },
                is_bestseller=(i % 7 == 0),
                is_prime_eligible=(i % 3 == 0),
                delivery_time=["Same day", "Next day", "2-3 days", "3-5 days"][i % 4],
                created_at=(datetime.now() - timedelta(days=i*10)).isoformat(),
                updated_at=datetime.now().isoformat()
            )
        
        print(f"✅ Generated {len(products)} products")
        return products
    
    def _generate_sellers(self) -> Dict[str, Seller]:
        """Mock seller data generate करता है"""
        sellers = {}
        
        seller_data = [
            ("Delhi Electronics", "Tech Hub Delhi", "Delhi", "Delhi", 4.2),
            ("Mumbai Gadgets", "Mumbai Electronics Pvt Ltd", "Mumbai", "Maharashtra", 4.5),
            ("Bangalore Tech", "Silicon Valley Stores", "Bangalore", "Karnataka", 4.7),
            ("Chennai Mobile", "South India Mobiles", "Chennai", "Tamil Nadu", 4.1),
            ("Pune Electronics", "Pune Digital Store", "Pune", "Maharashtra", 4.3),
            ("Varanasi Textiles", "Traditional Silk Weavers", "Varanasi", "Uttar Pradesh", 4.6),
            ("Delhi Fashion", "Capital Fashion House", "Delhi", "Delhi", 4.0),
            ("Maharashtra Leather", "Kolhapuri Leather Crafts", "Kolhapur", "Maharashtra", 4.4),
            ("Srinagar Crafts", "Kashmir Handicrafts Co", "Srinagar", "Jammu & Kashmir", 4.8),
            ("Agra Books", "Uttar Pradesh Book House", "Agra", "Uttar Pradesh", 4.2)
        ]
        
        for i, (name, business, city, state, rating) in enumerate(seller_data):
            seller_id = str(i + 1)
            sellers[seller_id] = Seller(
                id=seller_id,
                name=name,
                business_name=business,
                city=city,
                state=state,
                rating=rating,
                total_products=20 + (i * 5),
                years_in_business=5 + (i % 10),
                is_verified=(i % 4 != 0),  # 75% verified
                fulfillment_speed=["same-day", "next-day", "2-3 days"][i % 3]
            )
        
        return sellers
    
    def _generate_categories(self) -> Dict[str, Category]:
        """Mock category data generate करता है"""
        categories = {}
        
        category_data = [
            ("1", "Electronics", None, 1, 5000, ["Apple", "Samsung", "OnePlus"], ["smartphone", "laptop", "headphone"]),
            ("2", "Fashion", None, 1, 8000, ["Nike", "Adidas", "Fabindia"], ["kurta", "saree", "jeans"]),
            ("3", "Books", None, 1, 2000, ["Penguin", "Harper", "Rupa"], ["fiction", "biography", "hindi"]),
            ("4", "Sports", None, 1, 1500, ["Nike", "Adidas", "Yonex"], ["cricket", "football", "badminton"]),
            ("5", "Smartphones", "1", 2, 2500, ["Apple", "Samsung", "OnePlus", "Realme"], ["5G", "camera", "battery"]),
            ("6", "Laptops", "1", 2, 1200, ["Dell", "HP", "Lenovo", "Apple"], ["gaming", "ultrabook", "business"]),
            ("7", "Sarees", "2", 2, 3000, ["Fabindia", "Biba", "Traditional"], ["silk", "cotton", "banarasi"]),
            ("8", "Cricket", "4", 2, 800, ["SS", "MRF", "SG"], ["bat", "ball", "pads"])
        ]
        
        for cat_id, name, parent, level, count, brands, keywords in category_data:
            categories[cat_id] = Category(
                id=cat_id,
                name=name,
                parent_id=parent,
                level=level,
                product_count=count,
                popular_brands=brands,
                trending_keywords=keywords
            )
        
        return categories
    
    def _generate_reviews(self) -> Dict[str, Review]:
        """Mock review data generate करता है"""
        reviews = {}
        
        hindi_comments = [
            "बहुत अच्छा product है! Quality superb है।",
            "Price के हिसाब से value for money है।", 
            "Delivery fast थी, packaging भी अच्छी थी।",
            "Quality average है, price थोड़ी ज्यादा लगी।",
            "Excellent product! Highly recommended।",
            "Good quality, लेकिन delivery time ज्यादा था।",
            "Amazing product! पैसा वसूल है।",
            "सो-सो product है, better options available हैं।"
        ]
        
        for i in range(50):  # 50 sample reviews
            review_id = str(i + 1)
            reviews[review_id] = Review(
                id=review_id,
                product_id=str((i % 18) + 1),  # Product IDs 1-18
                user_id=str((i % 20) + 1),     # User IDs 1-20
                rating=(i % 5) + 1,            # Ratings 1-5
                title=f"Review {i+1}",
                comment=hindi_comments[i % len(hindi_comments)],
                verified_purchase=(i % 4 != 0),  # 75% verified
                helpful_votes=i % 25,
                created_at=(datetime.now() - timedelta(days=i*2)).isoformat()
            )
        
        return reviews
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Product fetch करता है with simulated DB delay"""
        await asyncio.sleep(0.1)  # Simulate DB query time
        return self.products.get(product_id)
    
    async def get_products_by_category(self, category: str, limit: int = 10) -> List[Product]:
        """Category के products fetch करता है"""
        await asyncio.sleep(0.2)  # Simulate expensive query
        
        filtered_products = [p for p in self.products.values() if p.category == category]
        return filtered_products[:limit]
    
    async def search_products(self, query: str, limit: int = 20) -> List[Product]:
        """Product search - expensive operation"""
        await asyncio.sleep(0.5)  # Simulate expensive search
        
        query_lower = query.lower()
        results = []
        
        for product in self.products.values():
            if (query_lower in product.name.lower() or 
                query_lower in product.brand.lower() or
                query_lower in product.category.lower()):
                results.append(product)
        
        return results[:limit]
    
    async def get_popular_products(self, limit: int = 10) -> List[Product]:
        """Popular products - frequently requested"""
        await asyncio.sleep(0.3)
        
        # Sort by rating and review count
        sorted_products = sorted(
            self.products.values(),
            key=lambda p: (p.rating * p.review_count),
            reverse=True
        )
        
        return sorted_products[:limit]

# Initialize database
db = MockDatabase()

# GraphQL Types
class ProductType(ObjectType):
    id = String()
    name = String()
    price = Float()
    original_price = Float()
    discount_percentage = Float()
    brand = String()
    category = String()
    seller_id = String()
    stock_count = Int()
    rating = Float()
    review_count = Int()
    image_urls = GrapheneList(String)
    specifications = String()  # JSON string
    is_bestseller = Boolean()
    is_prime_eligible = Boolean()
    delivery_time = String()
    created_at = String()
    updated_at = String()
    
    def resolve_specifications(self, info):
        return json.dumps(self.specifications, ensure_ascii=False)

class SellerType(ObjectType):
    id = String()
    name = String()
    business_name = String()
    city = String()
    state = String()
    rating = Float()
    total_products = Int()
    years_in_business = Int()
    is_verified = Boolean()
    fulfillment_speed = String()

class CategoryType(ObjectType):
    id = String()
    name = String()
    parent_id = String()
    level = Int()
    product_count = Int()
    popular_brands = GrapheneList(String)
    trending_keywords = GrapheneList(String)

class ReviewType(ObjectType):
    id = String()
    product_id = String()
    user_id = String()
    rating = Int()
    title = String()
    comment = String()
    verified_purchase = Boolean()
    helpful_votes = Int()
    created_at = String()

class CacheStatsType(ObjectType):
    total_requests = Int()
    cache_hits = Int()
    cache_misses = Int()
    hit_rate_percentage = Float()
    memory_cache_size = Int()
    detailed_stats = String()  # JSON string

# Cached Resolver Decorator
def cached_resolver(query_type: str):
    """Decorator for caching GraphQL resolvers"""
    def decorator(func):
        async def wrapper(self, info, **kwargs):
            # Generate cache key
            cache_key = cache_manager.get_cache_key(query_type, **kwargs)
            
            # Try to get from cache
            cached_data = await cache_manager.get_cached_data(cache_key, query_type)
            if cached_data is not None:
                return cached_data
            
            # Execute original function
            start_time = time.time()
            result = await func(self, info, **kwargs)
            execution_time = time.time() - start_time
            
            print(f"⏱️ Query {query_type} executed in {execution_time:.3f}s")
            
            # Store in cache
            await cache_manager.set_cached_data(cache_key, result, query_type)
            
            return result
        
        return wrapper
    return decorator

# GraphQL Queries with Caching
class Query(ObjectType):
    # Product queries with different caching strategies
    product = Field(ProductType, id=String(required=True))
    products_by_category = GrapheneList(ProductType, category=String(required=True), limit=Int(default_value=10))
    popular_products = GrapheneList(ProductType, limit=Int(default_value=10))
    trending_products = GrapheneList(ProductType, limit=Int(default_value=10))
    
    # Search queries - expensive operations
    search_products = GrapheneList(ProductType, query=String(required=True), limit=Int(default_value=20))
    search_suggestions = GrapheneList(String, query=String(required=True))
    
    # Seller queries
    seller = Field(SellerType, id=String(required=True))
    seller_products = GrapheneList(ProductType, seller_id=String(required=True))
    
    # Category queries - rarely changing
    categories = GrapheneList(CategoryType)
    category_tree = GrapheneList(CategoryType, parent_id=String())
    
    # Review queries
    product_reviews = GrapheneList(ReviewType, product_id=String(required=True))
    review_stats = Field(String, product_id=String(required=True))
    
    # Price comparison - frequently changing
    price_comparison = GrapheneList(ProductType, product_name=String(required=True))
    flash_sale_prices = GrapheneList(ProductType, sale_id=String(required=True))
    
    # Analytics - expensive computations
    analytics_dashboard = Field(String)
    trending_keywords = GrapheneList(String, category=String())
    
    # Cache management
    cache_stats = Field(CacheStatsType)
    
    @cached_resolver('product')
    async def resolve_product(self, info, id):
        """Single product - hybrid caching"""
        return await db.get_product(id)
    
    @cached_resolver('products_by_category')
    async def resolve_products_by_category(self, info, category, limit):
        """Category products - Redis caching"""
        result = await db.get_products_by_category(category, limit)
        # Convert to dict for JSON serialization
        return [asdict(p) for p in result]
    
    @cached_resolver('popular_products') 
    async def resolve_popular_products(self, info, limit):
        """Popular products - frequent updates, short TTL"""
        result = await db.get_popular_products(limit)
        return [asdict(p) for p in result]
    
    @cached_resolver('search_products')
    async def resolve_search_products(self, info, query, limit):
        """Search - expensive operation, Redis caching"""
        result = await db.search_products(query, limit)
        return [asdict(p) for p in result]
    
    @cached_resolver('search_suggestions')
    async def resolve_search_suggestions(self, info, query):
        """Search suggestions - in-memory caching"""
        await asyncio.sleep(0.1)  # Simulate computation
        
        # Mock suggestions based on query
        suggestions = [
            f"{query} phone",
            f"{query} price",
            f"{query} review",
            f"{query} specifications",
            f"best {query}",
            f"{query} vs",
            f"cheap {query}",
            f"{query} online"
        ]
        
        return suggestions[:5]
    
    @cached_resolver('seller')
    async def resolve_seller(self, info, id):
        """Seller info - long TTL as rarely changes"""
        seller = db.sellers.get(id)
        return asdict(seller) if seller else None
    
    @cached_resolver('categories')
    async def resolve_categories(self, info):
        """Categories - very long TTL, memory cache"""
        await asyncio.sleep(0.05)  # Simulate DB query
        return [asdict(cat) for cat in db.categories.values()]
    
    @cached_resolver('product_reviews')
    async def resolve_product_reviews(self, info, product_id):
        """Product reviews - medium TTL"""
        await asyncio.sleep(0.2)  # Simulate DB query
        
        reviews = [r for r in db.reviews.values() if r.product_id == product_id]
        return [asdict(r) for r in reviews]
    
    @cached_resolver('analytics_dashboard')
    async def resolve_analytics_dashboard(self, info):
        """Analytics - expensive computation, long TTL"""
        await asyncio.sleep(1.0)  # Simulate heavy computation
        
        total_products = len(db.products)
        total_sellers = len(db.sellers)
        avg_rating = sum(p.rating for p in db.products.values()) / total_products
        
        analytics = {
            'total_products': total_products,
            'total_sellers': total_sellers,
            'average_rating': round(avg_rating, 2),
            'total_reviews': len(db.reviews),
            'bestseller_count': len([p for p in db.products.values() if p.is_bestseller]),
            'categories_count': len(db.categories),
            'generated_at': datetime.now().isoformat()
        }
        
        return json.dumps(analytics, ensure_ascii=False)
    
    def resolve_cache_stats(self, info):
        """Cache statistics"""
        stats = cache_manager.get_cache_stats()
        return CacheStatsType(**{
            **stats,
            'detailed_stats': json.dumps(stats['detailed_stats'], ensure_ascii=False)
        })

# Mutations for cache invalidation
class InvalidateCache(graphene.Mutation):
    class Arguments:
        pattern = String(required=True)
    
    success = Boolean()
    message = String()
    
    async def mutate(self, info, pattern):
        await cache_manager.invalidate_cache(pattern)
        return InvalidateCache(
            success=True,
            message=f"Cache invalidated for pattern: {pattern}"
        )

class ClearAllCache(graphene.Mutation):
    success = Boolean()
    message = String()
    
    async def mutate(self, info):
        cache_manager.memory_cache.clear()
        cache_manager.cache_timestamps.clear()
        
        if cache_manager.redis_client:
            await cache_manager.redis_client.flushdb()
        
        return ClearAllCache(
            success=True,
            message="All caches cleared successfully"
        )

class Mutations(ObjectType):
    invalidate_cache = InvalidateCache.Field()
    clear_all_cache = ClearAllCache.Field()

# Schema
schema = Schema(query=Query, mutation=Mutations)

# FastAPI App
app = FastAPI(title="GraphQL Caching Strategies Demo")

# Context function
async def get_context(request: Request):
    return {
        'request': request,
        'user_id': request.headers.get('x-user-id', 'anonymous'),
        'cache_manager': cache_manager
    }

# GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema, context_value=get_context))

# Cache management endpoints
@app.get("/cache/stats")
async def cache_stats():
    """Cache statistics API endpoint"""
    return cache_manager.get_cache_stats()

@app.post("/cache/invalidate/{pattern}")
async def invalidate_cache_pattern(pattern: str):
    """Cache invalidation API endpoint"""
    await cache_manager.invalidate_cache(pattern)
    return {"message": f"Cache invalidated for pattern: {pattern}"}

@app.delete("/cache/clear")
async def clear_all_cache():
    """Clear all cache API endpoint"""
    cache_manager.memory_cache.clear()
    cache_manager.cache_timestamps.clear()
    
    if cache_manager.redis_client:
        await cache_manager.redis_client.flushdb()
    
    return {"message": "All caches cleared"}

# Health check
@app.get("/health")
async def health_check():
    redis_status = "connected" if cache_manager.redis_client else "not connected"
    cache_stats = cache_manager.get_cache_stats()
    
    return {
        "service": "graphql-caching-strategies",
        "status": "healthy",
        "redis": redis_status,
        "cache_stats": cache_stats,
        "features": [
            "Multi-level caching (Memory + Redis)",
            "Query-specific cache strategies",
            "Automatic cache invalidation",
            "Cache hit/miss tracking",
            "TTL-based expiration",
            "Indian e-commerce optimizations"
        ]
    }

@app.get("/")
async def root():
    return {
        "title": "GraphQL Caching Strategies",
        "description": "Comprehensive caching for Indian e-commerce GraphQL APIs",
        "caching_strategies": {
            "memory_cache": "Fastest access, limited size, local to server",
            "redis_cache": "Distributed, persistent, good for shared data",
            "hybrid_cache": "Memory first, Redis fallback - best performance",
            "no_cache": "Real-time data that shouldn't be cached"
        },
        "cache_ttl_strategies": {
            "very_short_30s": "Real-time prices, flash sales",
            "short_5min": "Popular products, search results", 
            "medium_30min": "Product details, reviews",
            "long_1hour": "Seller info, analytics",
            "very_long_24hours": "Categories, static data"
        },
        "sample_queries": {
            "cached_product": """
                query {
                  product(id: "1") {
                    name
                    price
                    rating
                  }
                }
            """,
            "cached_search": """
                query {
                  searchProducts(query: "iPhone", limit: 10) {
                    name
                    price
                    brand
                  }
                }
            """,
            "cached_analytics": """
                query {
                  analyticsDashboard
                  cacheStats {
                    totalRequests
                    hitRatePercentage
                    memoryCacheSize
                  }
                }
            """
        },
        "indian_optimizations": [
            "Regional product caching",
            "Festival sale cache strategies",
            "Multi-language content caching",
            "Pincode-based delivery caching",
            "Currency conversion caching"
        ]
    }

# Startup event
@app.on_event("startup")
async def startup():
    print("🚀 Starting GraphQL Caching Server...")
    print("🇮🇳 Indian E-commerce Caching Strategies:")
    print("   - Product catalogs with regional preferences")
    print("   - Search results with Hindi/English queries")
    print("   - Seller information by city/state")
    print("   - Price comparisons during festivals")
    print("   - Category trees with Indian brands")
    
    # Initialize Redis
    await cache_manager.initialize_redis()
    
    print("\n📊 Cache Strategy Examples:")
    for query_type, config in cache_manager.cache_configs.items():
        print(f"   - {query_type}: {config['strategy'].value} (TTL: {config['ttl']}s)")

if __name__ == "__main__":
    print("📦 Starting GraphQL Caching Strategies Server...")
    print("🎯 Features:")
    print("   - Multi-level caching (Memory + Redis)")
    print("   - Query-specific cache strategies")
    print("   - Indian e-commerce optimizations")
    print("   - Real-time cache statistics")
    print("   - Intelligent cache invalidation")
    
    uvicorn.run(
        "14_graphql_caching_strategies:app",
        host="0.0.0.0",
        port=4028,
        reload=True,
        log_level="info"
    )