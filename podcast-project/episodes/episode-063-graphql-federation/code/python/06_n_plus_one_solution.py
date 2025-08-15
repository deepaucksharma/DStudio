#!/usr/bin/env python3
"""
06_n_plus_one_solution.py
GraphQL में N+1 Query Problem का solution
यह बहुत common problem है जो performance को बर्बाद कर देती है
"""

import asyncio
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import graphene
from graphene import ObjectType, String, Int, Float, List as GrapheneList, Field, Schema
import uvicorn
from fastapi import FastAPI
from starlette.graphql import GraphQLApp

# Data Models
@dataclass
class Product:
    id: str
    name: str
    price: float
    category: str
    brand: str

@dataclass
class User:
    id: str
    name: str
    email: str
    city: str

@dataclass
class Order:
    id: str
    user_id: str
    product_ids: List[str]
    total_amount: float
    status: str

@dataclass
class Review:
    id: str
    user_id: str
    product_id: str
    rating: int
    comment: str

# Mock Database - Production में real database होगा
class MockDatabase:
    def __init__(self):
        # Sample data
        self.products = {
            '1': Product('1', 'iPhone 15 Pro', 134900.0, 'smartphones', 'Apple'),
            '2': Product('2', 'Samsung Galaxy S24', 84999.0, 'smartphones', 'Samsung'),
            '3': Product('3', 'OnePlus 12', 64999.0, 'smartphones', 'OnePlus'),
            '4': Product('4', 'iPad Air', 59900.0, 'tablets', 'Apple'),
            '5': Product('5', 'MacBook Air M2', 114900.0, 'laptops', 'Apple'),
        }
        
        self.users = {
            '1': User('1', 'Rahul Sharma', 'rahul@gmail.com', 'Mumbai'),
            '2': User('2', 'Priya Singh', 'priya@yahoo.com', 'Delhi'), 
            '3': User('3', 'Amit Kumar', 'amit@hotmail.com', 'Bangalore'),
            '4': User('4', 'Sneha Patel', 'sneha@gmail.com', 'Pune'),
        }
        
        self.orders = {
            '1': Order('1', '1', ['1', '4'], 194800.0, 'delivered'),
            '2': Order('2', '2', ['2'], 84999.0, 'shipped'),
            '3': Order('3', '1', ['3', '5'], 179899.0, 'processing'),
            '4': Order('4', '3', ['1'], 134900.0, 'delivered'),
        }
        
        self.reviews = {
            '1': Review('1', '1', '1', 5, 'Bahut accha phone hai! Camera quality amazing hai.'),
            '2': Review('2', '2', '1', 4, 'Good phone but battery life could be better'),
            '3': Review('3', '1', '2', 3, 'Samsung hai to theek hai, but price thoda zyada hai'),
            '4': Review('4', '3', '3', 5, 'OnePlus ka best phone! Value for money.'),
            '5': Review('5', '4', '4', 4, 'iPad Air bahut smooth hai, drawing ke liye perfect'),
        }
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        """Single product fetch - database query simulation"""
        print(f"🔍 DB Query: Fetching product {product_id}")
        await asyncio.sleep(0.1)  # Database latency simulation
        return self.products.get(product_id)
    
    async def get_products(self, product_ids: List[str]) -> List[Optional[Product]]:
        """Batch product fetch - एक ही query में multiple products"""
        print(f"🔍 DB Batch Query: Fetching {len(product_ids)} products: {product_ids}")
        await asyncio.sleep(0.1)  # Single database query
        return [self.products.get(pid) for pid in product_ids]
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Single user fetch"""
        print(f"👤 DB Query: Fetching user {user_id}")
        await asyncio.sleep(0.1)
        return self.users.get(user_id)
    
    async def get_users(self, user_ids: List[str]) -> List[Optional[User]]:
        """Batch user fetch"""
        print(f"👤 DB Batch Query: Fetching {len(user_ids)} users: {user_ids}")
        await asyncio.sleep(0.1)
        return [self.users.get(uid) for uid in user_ids]
    
    async def get_orders_by_user(self, user_id: str) -> List[Order]:
        """User के सारे orders"""
        print(f"📦 DB Query: Fetching orders for user {user_id}")
        await asyncio.sleep(0.1)
        return [order for order in self.orders.values() if order.user_id == user_id]
    
    async def get_reviews_by_product(self, product_id: str) -> List[Review]:
        """Product के सारे reviews"""
        print(f"⭐ DB Query: Fetching reviews for product {product_id}")
        await asyncio.sleep(0.1)
        return [review for review in self.reviews.values() if review.product_id == product_id]
    
    async def get_reviews_by_products(self, product_ids: List[str]) -> Dict[str, List[Review]]:
        """Batch reviews fetch - multiple products के लिए"""
        print(f"⭐ DB Batch Query: Fetching reviews for {len(product_ids)} products")
        await asyncio.sleep(0.1)
        
        result = defaultdict(list)
        for review in self.reviews.values():
            if review.product_id in product_ids:
                result[review.product_id].append(review)
        return dict(result)

# Database instance
db = MockDatabase()

# DataLoader Implementation (Simple Python version)
class DataLoader:
    def __init__(self, batch_load_fn, max_batch_size=100):
        self.batch_load_fn = batch_load_fn
        self.max_batch_size = max_batch_size
        self._promise_cache = {}
        self._batch = []
        self._batch_timer = None
    
    async def load(self, key):
        """Single key load करता है, automatically batches करता है"""
        if key in self._promise_cache:
            return await self._promise_cache[key]
        
        # Create promise for this key
        future = asyncio.Future()
        self._promise_cache[key] = future
        self._batch.append(key)
        
        # Schedule batch execution if not already scheduled
        if self._batch_timer is None:
            self._batch_timer = asyncio.create_task(self._dispatch_batch())
        
        return await future
    
    async def load_many(self, keys):
        """Multiple keys load करता है"""
        return await asyncio.gather(*[self.load(key) for key in keys])
    
    async def _dispatch_batch(self):
        """Batch को execute करता है"""
        await asyncio.sleep(0.01)  # Small delay to collect more keys
        
        if not self._batch:
            return
        
        batch = self._batch[:]
        self._batch = []
        self._batch_timer = None
        
        try:
            # Batch function call करते हैं
            results = await self.batch_load_fn(batch)
            
            # Results को respective promises में resolve करते हैं
            for i, key in enumerate(batch):
                if key in self._promise_cache:
                    future = self._promise_cache[key]
                    if not future.done():
                        if i < len(results):
                            future.set_result(results[i])
                        else:
                            future.set_result(None)
        
        except Exception as e:
            # Error को सारे promises में propagate करते हैं
            for key in batch:
                if key in self._promise_cache:
                    future = self._promise_cache[key]
                    if not future.done():
                        future.set_exception(e)
    
    def clear(self, key=None):
        """Cache clear करता है"""
        if key:
            self._promise_cache.pop(key, None)
        else:
            self._promise_cache.clear()

# GraphQL Types
class ProductType(ObjectType):
    id = String()
    name = String()
    price = Float()
    category = String()
    brand = String()
    # N+1 problem वाले fields
    reviews = GrapheneList(lambda: ReviewType)
    average_rating = Float()
    
    async def resolve_reviews(self, info):
        """यहाँ N+1 problem होती है without DataLoader"""
        loader = info.context.get('reviews_by_product_loader')
        if loader:
            print(f"🚀 Using DataLoader for product {self.id} reviews")
            reviews = await loader.load(self.id)
            return reviews
        else:
            # Traditional approach - N+1 problem
            print(f"⚠️ Traditional query for product {self.id} reviews")
            return await db.get_reviews_by_product(self.id)
    
    async def resolve_average_rating(self, info):
        reviews = await self.resolve_reviews(info)
        if not reviews:
            return 0.0
        return sum(review.rating for review in reviews) / len(reviews)

class UserType(ObjectType):
    id = String()
    name = String()
    email = String()
    city = String()
    orders = GrapheneList(lambda: OrderType)
    
    async def resolve_orders(self, info):
        return await db.get_orders_by_user(self.id)

class OrderType(ObjectType):
    id = String()
    user_id = String()
    product_ids = GrapheneList(String)
    total_amount = Float()
    status = String()
    # N+1 problem fields
    user = Field(UserType)
    products = GrapheneList(ProductType)
    
    async def resolve_user(self, info):
        loader = info.context.get('user_loader')
        if loader:
            print(f"🚀 Using DataLoader for order {self.id} user")
            user = await loader.load(self.user_id)
            return user
        else:
            print(f"⚠️ Traditional query for order {self.id} user")
            return await db.get_user(self.user_id)
    
    async def resolve_products(self, info):
        loader = info.context.get('product_loader')
        if loader:
            print(f"🚀 Using DataLoader for order {self.id} products")
            products = await loader.load_many(self.product_ids)
            return [p for p in products if p is not None]
        else:
            print(f"⚠️ Traditional queries for order {self.id} products")
            products = []
            for product_id in self.product_ids:
                product = await db.get_product(product_id)
                if product:
                    products.append(product)
            return products

class ReviewType(ObjectType):
    id = String()
    user_id = String()
    product_id = String()
    rating = Int()
    comment = String()
    user = Field(UserType)
    product = Field(ProductType)
    
    async def resolve_user(self, info):
        loader = info.context.get('user_loader')
        if loader:
            user = await loader.load(self.user_id)
            return user
        else:
            return await db.get_user(self.user_id)
    
    async def resolve_product(self, info):
        loader = info.context.get('product_loader')
        if loader:
            product = await loader.load(self.product_id)
            return product
        else:
            return await db.get_product(self.product_id)

class Query(ObjectType):
    # Individual queries
    product = Field(ProductType, id=String(required=True))
    user = Field(UserType, id=String(required=True))
    order = Field(OrderType, id=String(required=True))
    
    # List queries - यहाँ N+1 problem demonstrate होती है
    all_products = GrapheneList(ProductType)
    all_orders = GrapheneList(OrderType)
    all_users = GrapheneList(UserType)
    
    # Performance test queries
    products_with_reviews = GrapheneList(ProductType)
    orders_with_details = GrapheneList(OrderType)
    
    async def resolve_product(self, info, id):
        return await db.get_product(id)
    
    async def resolve_user(self, info, id):
        return await db.get_user(id)
    
    async def resolve_order(self, info, id):
        return db.orders.get(id)
    
    async def resolve_all_products(self, info):
        print("🛍️ Fetching all products")
        return list(db.products.values())
    
    async def resolve_all_orders(self, info):
        print("📦 Fetching all orders")
        return list(db.orders.values())
    
    async def resolve_all_users(self, info):
        print("👥 Fetching all users")
        return list(db.users.values())
    
    async def resolve_products_with_reviews(self, info):
        """Performance test: Products with reviews"""
        print("🧪 Performance Test: Products with reviews")
        start_time = time.time()
        
        products = list(db.products.values())
        
        end_time = time.time()
        print(f"⏱️ Query completed in {(end_time - start_time)*1000:.2f}ms")
        
        return products
    
    async def resolve_orders_with_details(self, info):
        """Performance test: Orders with user and products"""
        print("🧪 Performance Test: Orders with user and products")
        start_time = time.time()
        
        orders = list(db.orders.values())
        
        end_time = time.time()
        print(f"⏱️ Query completed in {(end_time - start_time)*1000:.2f}ms")
        
        return orders

# DataLoader factory function
def create_data_loaders():
    """हर request के लिए fresh DataLoaders create करते हैं"""
    print("🏭 Creating DataLoaders...")
    
    # Product DataLoader
    product_loader = DataLoader(db.get_products)
    
    # User DataLoader
    user_loader = DataLoader(db.get_users)
    
    # Reviews by Product DataLoader
    async def batch_reviews_by_product(product_ids):
        reviews_dict = await db.get_reviews_by_products(product_ids)
        return [reviews_dict.get(pid, []) for pid in product_ids]
    
    reviews_by_product_loader = DataLoader(batch_reviews_by_product)
    
    return {
        'product_loader': product_loader,
        'user_loader': user_loader,
        'reviews_by_product_loader': reviews_by_product_loader
    }

# GraphQL Schema
schema = Schema(query=Query)

# FastAPI app
app = FastAPI(title="GraphQL N+1 Problem Solution")

# Context function with DataLoaders
async def get_context(request):
    """हर request के लिए context create करते हैं"""
    use_dataloaders = request.headers.get('X-Use-DataLoaders', 'true').lower() == 'true'
    
    context = {
        'request_id': f"req_{int(time.time() * 1000)}",
        'start_time': time.time(),
        'use_dataloaders': use_dataloaders
    }
    
    if use_dataloaders:
        # DataLoaders add करते हैं
        context.update(create_data_loaders())
        print("✅ Request using DataLoaders (optimized)")
    else:
        print("⚠️ Request NOT using DataLoaders (will have N+1 problem)")
    
    return context

# GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema, context_value=get_context))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "service": "graphql-n-plus-one-solution",
        "status": "healthy",
        "features": [
            "DataLoader implementation",
            "N+1 problem demonstration",
            "Batch loading",
            "Request-scoped caching"
        ]
    }

# Performance comparison endpoint
@app.get("/performance-test")
async def performance_test():
    """DataLoader vs Traditional approach का performance comparison"""
    
    results = {
        "test_description": "Performance comparison between DataLoader and traditional approach",
        "tests": []
    }
    
    # Test 1: Products with reviews (DataLoader)
    start_time = time.time()
    
    # Simulate DataLoader approach
    all_product_ids = list(db.products.keys())
    reviews_dict = await db.get_reviews_by_products(all_product_ids)
    
    dataloader_time = (time.time() - start_time) * 1000
    
    # Test 2: Products with reviews (Traditional)
    start_time = time.time()
    
    # Simulate traditional approach (N+1)
    for product_id in all_product_ids:
        await db.get_reviews_by_product(product_id)
    
    traditional_time = (time.time() - start_time) * 1000
    
    results["tests"].append({
        "test_name": "Products with Reviews",
        "dataloader_time_ms": round(dataloader_time, 2),
        "traditional_time_ms": round(traditional_time, 2),
        "improvement_factor": round(traditional_time / dataloader_time, 2),
        "queries_saved": len(all_product_ids) - 1
    })
    
    return results

# Usage instructions endpoint
@app.get("/")
async def usage_instructions():
    return {
        "title": "GraphQL N+1 Problem Solution Demo",
        "description": "यह demo दिखाता है कि DataLoader कैसे N+1 problem solve करता है",
        "endpoints": {
            "/graphql": "GraphQL endpoint (POST)",
            "/health": "Health check",
            "/performance-test": "Performance comparison",
            "/": "Usage instructions"
        },
        "sample_queries": {
            "with_dataloader": {
                "description": "DataLoader के साथ - optimized",
                "headers": {"X-Use-DataLoaders": "true"},
                "query": """
                {
                  productsWithReviews {
                    id
                    name
                    reviews {
                      rating
                      comment
                      user {
                        name
                      }
                    }
                    averageRating
                  }
                }
                """
            },
            "without_dataloader": {
                "description": "DataLoader के बिना - N+1 problem",
                "headers": {"X-Use-DataLoaders": "false"},
                "query": """
                {
                  productsWithReviews {
                    id
                    name
                    reviews {
                      rating
                      comment
                    }
                  }
                }
                """
            },
            "orders_with_details": {
                "description": "Orders with user and products",
                "query": """
                {
                  ordersWithDetails {
                    id
                    totalAmount
                    user {
                      name
                      city
                    }
                    products {
                      name
                      price
                    }
                  }
                }
                """
            }
        },
        "n_plus_one_problem": {
            "description": "N+1 problem तब होती है जब main query करने के बाद हर related item के लिए separate query चलानी पड़ती है",
            "example": "अगर 100 products हैं और हर product के reviews चाहिए, तो traditional approach में 101 queries चलेंगी (1 for products + 100 for reviews)",
            "dataloader_solution": "DataLoader सारे reviews एक ही query में fetch करता है, total 2 queries (1 for products + 1 for all reviews)"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting GraphQL N+1 Problem Solution Server...")
    print("📚 यह server demonstrate करता है:")
    print("   1. N+1 query problem क्या होती है")
    print("   2. DataLoader कैसे इसे solve करता है") 
    print("   3. Performance improvement कितनी होती है")
    print("\n🧪 Test करने के लिए:")
    print("   - Header 'X-Use-DataLoaders: true' के साथ DataLoader use करें")
    print("   - Header 'X-Use-DataLoaders: false' के साथ traditional approach test करें")
    print("   - /performance-test endpoint से comparison देखें")
    
    uvicorn.run(
        "06_n_plus_one_solution:app",
        host="0.0.0.0",
        port=4021,
        reload=True,
        log_level="info"
    )