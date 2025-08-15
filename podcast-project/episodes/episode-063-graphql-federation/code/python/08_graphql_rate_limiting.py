#!/usr/bin/env python3
"""
08_graphql_rate_limiting.py
GraphQL Rate Limiting और Query Complexity Analysis
DoS attacks से बचने के लिए comprehensive protection
"""

import time
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime, timedelta
import json
import graphene
from graphene import ObjectType, String, Int, Float, Boolean, List as GrapheneList, Field, Schema
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from starlette.graphql import GraphQLApp
from starlette.middleware.base import BaseHTTPMiddleware
from graphql import build_ast_schema, parse, validate, ValidationRule
from graphql.error import GraphQLError
from graphql.validation.rules.query_complexity import QueryComplexityRule
import redis
import hashlib

# Rate Limiting Configuration
@dataclass
class RateLimitConfig:
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    query_complexity_limit: int = 1000
    query_depth_limit: int = 10
    burst_limit: int = 10  # Burst requests allowed
    
    # Different limits for different user types
    guest_limits: Dict[str, int] = field(default_factory=lambda: {
        'rpm': 30, 'rph': 500, 'rpd': 2000, 'complexity': 500, 'depth': 5
    })
    
    customer_limits: Dict[str, int] = field(default_factory=lambda: {
        'rpm': 120, 'rph': 2000, 'rpd': 20000, 'complexity': 1500, 'depth': 8
    })
    
    seller_limits: Dict[str, int] = field(default_factory=lambda: {
        'rpm': 300, 'rph': 5000, 'rpd': 50000, 'complexity': 3000, 'depth': 12
    })
    
    admin_limits: Dict[str, int] = field(default_factory=lambda: {
        'rpm': 1000, 'rph': 20000, 'rpd': 200000, 'complexity': 10000, 'depth': 20
    })

# Rate Limiter Implementation
class GraphQLRateLimiter:
    def __init__(self, config: RateLimitConfig, use_redis: bool = False):
        self.config = config
        self.use_redis = use_redis
        
        if use_redis:
            try:
                self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
                self.redis_client.ping()
                print("✅ Redis connected for distributed rate limiting")
            except:
                print("⚠️ Redis not available, falling back to in-memory rate limiting")
                self.use_redis = False
                
        if not self.use_redis:
            # In-memory storage
            self.request_counts = defaultdict(lambda: {
                'minute': {'count': 0, 'window': datetime.now()},
                'hour': {'count': 0, 'window': datetime.now()},
                'day': {'count': 0, 'window': datetime.now()},
                'burst': {'count': 0, 'window': datetime.now()}
            })
    
    def get_user_limits(self, user_role: str) -> Dict[str, int]:
        """User role के हिसाब से limits return करता है"""
        role_limits = {
            'guest': self.config.guest_limits,
            'customer': self.config.customer_limits,
            'seller': self.config.seller_limits,
            'admin': self.config.admin_limits
        }
        return role_limits.get(user_role.lower(), self.config.guest_limits)
    
    def get_client_id(self, request: Request, user_id: Optional[str] = None) -> str:
        """Client identification के लिए unique ID generate करता है"""
        if user_id:
            return f"user:{user_id}"
        
        # IP-based identification for anonymous users
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', '')
        
        # Create hash for privacy
        client_hash = hashlib.md5(f"{client_ip}:{user_agent}".encode()).hexdigest()[:12]
        return f"ip:{client_hash}"
    
    async def check_rate_limit(
        self, 
        client_id: str, 
        user_role: str = 'guest', 
        query_complexity: int = 0,
        query_depth: int = 0
    ) -> Dict[str, Any]:
        """Rate limit check करता है"""
        
        limits = self.get_user_limits(user_role)
        now = datetime.now()
        
        if self.use_redis:
            return await self._check_redis_limits(client_id, limits, now, query_complexity, query_depth)
        else:
            return self._check_memory_limits(client_id, limits, now, query_complexity, query_depth)
    
    def _check_memory_limits(
        self, 
        client_id: str, 
        limits: Dict[str, int], 
        now: datetime,
        query_complexity: int,
        query_depth: int
    ) -> Dict[str, Any]:
        """In-memory rate limiting"""
        
        client_data = self.request_counts[client_id]
        
        # Check and reset windows
        time_windows = {
            'minute': (limits['rpm'], 1),
            'hour': (limits['rph'], 60), 
            'day': (limits['rpd'], 1440),
            'burst': (self.config.burst_limit, 0.1)  # 6 second window
        }
        
        violations = []
        
        for window, (limit, window_minutes) in time_windows.items():
            window_data = client_data[window]
            window_delta = timedelta(minutes=window_minutes)
            
            # Reset window if expired
            if now - window_data['window'] > window_delta:
                window_data['count'] = 0
                window_data['window'] = now
            
            # Check limit
            if window_data['count'] >= limit:
                violations.append({
                    'type': f'{window}_limit_exceeded',
                    'current': window_data['count'],
                    'limit': limit,
                    'reset_time': (window_data['window'] + window_delta).isoformat()
                })
        
        # Query complexity check
        if query_complexity > limits['complexity']:
            violations.append({
                'type': 'complexity_limit_exceeded',
                'current': query_complexity,
                'limit': limits['complexity']
            })
        
        # Query depth check  
        if query_depth > limits['depth']:
            violations.append({
                'type': 'depth_limit_exceeded',
                'current': query_depth,
                'limit': limits['depth']
            })
        
        if violations:
            return {
                'allowed': False,
                'violations': violations,
                'retry_after': 60  # 1 minute
            }
        
        # Increment counters
        for window in time_windows.keys():
            client_data[window]['count'] += 1
        
        return {
            'allowed': True,
            'remaining': {
                'minute': limits['rpm'] - client_data['minute']['count'],
                'hour': limits['rph'] - client_data['hour']['count'],
                'day': limits['rpd'] - client_data['day']['count']
            }
        }
    
    async def _check_redis_limits(
        self,
        client_id: str,
        limits: Dict[str, int],
        now: datetime,
        query_complexity: int,
        query_depth: int
    ) -> Dict[str, Any]:
        """Redis-based distributed rate limiting"""
        
        pipeline = self.redis_client.pipeline()
        
        # Different time windows
        minute_key = f"rl:{client_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rl:{client_id}:hour:{now.strftime('%Y%m%d%H')}"
        day_key = f"rl:{client_id}:day:{now.strftime('%Y%m%d')}"
        
        # Get current counts
        pipeline.get(minute_key)
        pipeline.get(hour_key)
        pipeline.get(day_key)
        
        results = await pipeline.execute()
        
        minute_count = int(results[0] or 0)
        hour_count = int(results[1] or 0) 
        day_count = int(results[2] or 0)
        
        violations = []
        
        # Check limits
        if minute_count >= limits['rpm']:
            violations.append({
                'type': 'minute_limit_exceeded',
                'current': minute_count,
                'limit': limits['rpm']
            })
        
        if hour_count >= limits['rph']:
            violations.append({
                'type': 'hour_limit_exceeded', 
                'current': hour_count,
                'limit': limits['rph']
            })
        
        if day_count >= limits['rpd']:
            violations.append({
                'type': 'day_limit_exceeded',
                'current': day_count,
                'limit': limits['rpd']
            })
        
        # Query complexity and depth checks
        if query_complexity > limits['complexity']:
            violations.append({
                'type': 'complexity_limit_exceeded',
                'current': query_complexity,
                'limit': limits['complexity']
            })
        
        if query_depth > limits['depth']:
            violations.append({
                'type': 'depth_limit_exceeded',
                'current': query_depth,
                'limit': limits['depth']
            })
        
        if violations:
            return {
                'allowed': False,
                'violations': violations,
                'retry_after': 60
            }
        
        # Increment counters
        pipeline = self.redis_client.pipeline()
        pipeline.incr(minute_key)
        pipeline.expire(minute_key, 60)  # 1 minute
        pipeline.incr(hour_key)
        pipeline.expire(hour_key, 3600)  # 1 hour
        pipeline.incr(day_key)
        pipeline.expire(day_key, 86400)  # 1 day
        
        await pipeline.execute()
        
        return {
            'allowed': True,
            'remaining': {
                'minute': limits['rpm'] - minute_count - 1,
                'hour': limits['rph'] - hour_count - 1,
                'day': limits['rpd'] - day_count - 1
            }
        }

# Query Complexity Analyzer
class QueryComplexityAnalyzer:
    def __init__(self):
        # Field complexity weights
        self.field_costs = {
            # Expensive operations
            'search': 10,
            'analytics': 15,
            'recommendations': 12,
            'reports': 20,
            
            # Database queries
            'products': 3,
            'orders': 5,
            'users': 4,
            'reviews': 2,
            
            # Simple fields
            'id': 0,
            'name': 1,
            'price': 1,
            'status': 1,
            
            # Computed fields
            'averageRating': 3,
            'totalCount': 2,
            'statistics': 8
        }
    
    def analyze_query(self, query_ast) -> Dict[str, Any]:
        """Query की complexity और depth analyze करता है"""
        
        complexity = 0
        depth = 0
        field_count = 0
        
        def traverse_field(field_node, current_depth=1):
            nonlocal complexity, depth, field_count
            
            field_name = field_node.name.value
            field_count += 1
            
            # Update max depth
            depth = max(depth, current_depth)
            
            # Add field cost
            field_cost = self.field_costs.get(field_name, 1)
            
            # Arguments increase complexity
            if hasattr(field_node, 'arguments') and field_node.arguments:
                arg_multiplier = 1 + len(field_node.arguments) * 0.5
                field_cost *= arg_multiplier
            
            complexity += field_cost
            
            # Recursively analyze selection set
            if hasattr(field_node, 'selection_set') and field_node.selection_set:
                for selection in field_node.selection_set.selections:
                    if hasattr(selection, 'name'):  # Field selection
                        traverse_field(selection, current_depth + 1)
                    # Handle fragments if needed
        
        # Start traversal from root
        if hasattr(query_ast, 'definitions'):
            for definition in query_ast.definitions:
                if hasattr(definition, 'selection_set'):
                    for selection in definition.selection_set.selections:
                        if hasattr(selection, 'name'):
                            traverse_field(selection)
        
        return {
            'complexity': complexity,
            'depth': depth,
            'field_count': field_count,
            'estimated_cost': complexity * 0.1  # Rough time estimate in seconds
        }

# Mock data for testing
MOCK_DATA = {
    'products': [
        {'id': str(i), 'name': f'Product {i}', 'price': 1000 + i*100} 
        for i in range(1, 101)
    ],
    'users': [
        {'id': str(i), 'name': f'User {i}', 'email': f'user{i}@example.com'}
        for i in range(1, 51)
    ],
    'orders': [
        {'id': str(i), 'user_id': str((i % 50) + 1), 'total': 2000 + i*50}
        for i in range(1, 201)
    ]
}

# GraphQL Types
class ProductType(ObjectType):
    id = String()
    name = String()
    price = Float()
    description = String()
    reviews = GrapheneList(lambda: ReviewType)
    average_rating = Float()
    
    # Expensive computed field
    async def resolve_reviews(self, info):
        # Simulate expensive operation
        await asyncio.sleep(0.1)
        return [
            {'id': f"{self.id}_review_{i}", 'rating': 4 + (i % 2), 'comment': f'Review {i}'}
            for i in range(1, 6)
        ]
    
    async def resolve_average_rating(self, info):
        await asyncio.sleep(0.05)
        return 4.2

class ReviewType(ObjectType):
    id = String()
    rating = Int()
    comment = String()
    user = Field(lambda: UserType)
    
    async def resolve_user(self, info):
        # Simulate N+1 problem for complexity testing
        await asyncio.sleep(0.02)
        return {'id': '1', 'name': 'Test User', 'email': 'test@example.com'}

class UserType(ObjectType):
    id = String()
    name = String()
    email = String()
    orders = GrapheneList(lambda: OrderType)
    statistics = Field(lambda: UserStatsType)
    
    async def resolve_orders(self, info):
        await asyncio.sleep(0.1)
        return [order for order in MOCK_DATA['orders'] if order['user_id'] == self.id]
    
    async def resolve_statistics(self, info):
        # Expensive computation
        await asyncio.sleep(0.2)
        return {'total_orders': 5, 'total_spent': 15000.0, 'average_order': 3000.0}

class OrderType(ObjectType):
    id = String()
    user_id = String()
    total = Float()
    status = String()
    items = GrapheneList(lambda: OrderItemType)
    
    async def resolve_items(self, info):
        await asyncio.sleep(0.08)
        return [
            {'product_id': '1', 'quantity': 2, 'price': 1000},
            {'product_id': '2', 'quantity': 1, 'price': 1500}
        ]

class OrderItemType(ObjectType):
    product_id = String()
    quantity = Int()
    price = Float()
    product = Field(ProductType)
    
    async def resolve_product(self, info):
        product_data = next((p for p in MOCK_DATA['products'] if p['id'] == self.product_id), None)
        return product_data

class UserStatsType(ObjectType):
    total_orders = Int()
    total_spent = Float()
    average_order = Float()

class SearchResultType(ObjectType):
    products = GrapheneList(ProductType)
    users = GrapheneList(UserType)
    total_count = Int()

class Query(ObjectType):
    # Simple queries
    product = Field(ProductType, id=String(required=True))
    user = Field(UserType, id=String(required=True))
    
    # List queries with pagination
    products = GrapheneList(ProductType, limit=Int(default_value=10), offset=Int(default_value=0))
    users = GrapheneList(UserType, limit=Int(default_value=10))
    orders = GrapheneList(OrderType, limit=Int(default_value=10))
    
    # Expensive queries for testing
    search = Field(SearchResultType, query=String(required=True), limit=Int(default_value=50))
    analytics = Field(String)
    reports = Field(String, type=String(required=True))
    recommendations = GrapheneList(ProductType, user_id=String(required=True), limit=Int(default_value=20))
    
    async def resolve_product(self, info, id):
        product = next((p for p in MOCK_DATA['products'] if p['id'] == id), None)
        if not product:
            raise Exception(f"Product {id} not found")
        return product
    
    async def resolve_user(self, info, id):
        user = next((u for u in MOCK_DATA['users'] if u['id'] == id), None)
        if not user:
            raise Exception(f"User {id} not found")
        return user
    
    async def resolve_products(self, info, limit, offset):
        return MOCK_DATA['products'][offset:offset+limit]
    
    async def resolve_users(self, info, limit):
        return MOCK_DATA['users'][:limit]
    
    async def resolve_orders(self, info, limit):
        return MOCK_DATA['orders'][:limit]
    
    # Expensive query resolvers
    async def resolve_search(self, info, query, limit):
        """Search operation - computationally expensive"""
        print(f"🔍 Expensive search query: '{query}' (limit: {limit})")
        
        # Simulate expensive search operation
        await asyncio.sleep(0.5)
        
        matching_products = [
            p for p in MOCK_DATA['products']
            if query.lower() in p['name'].lower()
        ][:limit//2]
        
        matching_users = [
            u for u in MOCK_DATA['users']
            if query.lower() in u['name'].lower()
        ][:limit//2]
        
        return {
            'products': matching_products,
            'users': matching_users,
            'total_count': len(matching_products) + len(matching_users)
        }
    
    async def resolve_analytics(self, info):
        """Analytics query - very expensive"""
        print("📊 Expensive analytics query")
        
        # Simulate heavy computation
        await asyncio.sleep(1.0)
        
        return json.dumps({
            'total_products': len(MOCK_DATA['products']),
            'total_users': len(MOCK_DATA['users']),
            'total_orders': len(MOCK_DATA['orders']),
            'revenue': sum(order['total'] for order in MOCK_DATA['orders'])
        })
    
    async def resolve_reports(self, info, type):
        """Report generation - extremely expensive"""
        print(f"📋 Expensive report query: {type}")
        
        # Simulate report generation
        await asyncio.sleep(2.0)
        
        return f"Generated {type} report with comprehensive data analysis"
    
    async def resolve_recommendations(self, info, user_id, limit):
        """Recommendation engine - expensive ML operation"""
        print(f"🤖 Expensive recommendations for user {user_id}")
        
        # Simulate ML recommendation engine
        await asyncio.sleep(0.8)
        
        return MOCK_DATA['products'][:limit]

# Rate limiting middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limiter: GraphQLRateLimiter, complexity_analyzer: QueryComplexityAnalyzer):
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.complexity_analyzer = complexity_analyzer
    
    async def dispatch(self, request: Request, call_next):
        # Only check GraphQL requests
        if not request.url.path.startswith('/graphql'):
            return await call_next(request)
        
        start_time = time.time()
        
        # Get user info (simplified)
        user_role = request.headers.get('X-User-Role', 'guest')
        user_id = request.headers.get('X-User-ID')
        
        client_id = self.rate_limiter.get_client_id(request, user_id)
        
        # For POST requests (GraphQL queries), analyze the query
        query_complexity = 0
        query_depth = 0
        
        if request.method == 'POST':
            try:
                body = await request.body()
                if body:
                    query_data = json.loads(body)
                    query = query_data.get('query', '')
                    
                    if query.strip():
                        # Parse and analyze query
                        query_ast = parse(query)
                        analysis = self.complexity_analyzer.analyze_query(query_ast)
                        
                        query_complexity = analysis['complexity']
                        query_depth = analysis['depth']
                        
                        print(f"📊 Query analysis - Complexity: {query_complexity}, Depth: {query_depth}")
                        
                        # Recreate request with body for next handler
                        request._body = body
            
            except Exception as e:
                print(f"❌ Query analysis error: {e}")
        
        # Check rate limits
        rate_limit_result = await self.rate_limiter.check_rate_limit(
            client_id=client_id,
            user_role=user_role,
            query_complexity=query_complexity,
            query_depth=query_depth
        )
        
        # If rate limited, return error
        if not rate_limit_result['allowed']:
            violations = rate_limit_result['violations']
            
            error_message = "Rate limit exceeded. Violations: " + ", ".join([
                f"{v['type']} (current: {v['current']}, limit: {v['limit']})"
                for v in violations
            ])
            
            print(f"🚫 Rate limited: {client_id} - {error_message}")
            
            return Response(
                content=json.dumps({
                    'errors': [{
                        'message': error_message,
                        'extensions': {
                            'code': 'RATE_LIMITED',
                            'violations': violations,
                            'retry_after': rate_limit_result.get('retry_after', 60)
                        }
                    }]
                }),
                status_code=429,
                headers={
                    'Content-Type': 'application/json',
                    'Retry-After': str(rate_limit_result.get('retry_after', 60)),
                    'X-RateLimit-Remaining-Minute': str(rate_limit_result.get('remaining', {}).get('minute', 0)),
                    'X-RateLimit-Remaining-Hour': str(rate_limit_result.get('remaining', {}).get('hour', 0))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = rate_limit_result.get('remaining', {})
        response.headers['X-RateLimit-Remaining-Minute'] = str(remaining.get('minute', 0))
        response.headers['X-RateLimit-Remaining-Hour'] = str(remaining.get('hour', 0))
        response.headers['X-RateLimit-Remaining-Day'] = str(remaining.get('day', 0))
        response.headers['X-Query-Complexity'] = str(query_complexity)
        response.headers['X-Query-Depth'] = str(query_depth)
        
        # Response timing
        process_time = time.time() - start_time
        response.headers['X-Process-Time'] = f"{process_time:.3f}s"
        
        print(f"✅ Request processed: {client_id} ({user_role}) - {process_time:.3f}s")
        
        return response

# Initialize components
rate_limiter = GraphQLRateLimiter(RateLimitConfig())
complexity_analyzer = QueryComplexityAnalyzer()
schema = Schema(query=Query)

# FastAPI app
app = FastAPI(title="GraphQL Rate Limiting System")

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter, complexity_analyzer=complexity_analyzer)

# Context function
async def get_context(request: Request):
    return {
        'request': request,
        'user_role': request.headers.get('X-User-Role', 'guest'),
        'user_id': request.headers.get('X-User-ID'),
        'request_time': datetime.now()
    }

# GraphQL endpoint
app.add_route("/graphql", GraphQLApp(schema=schema, context_value=get_context))

# Health and info endpoints
@app.get("/health")
async def health_check():
    return {
        "service": "graphql-rate-limiting",
        "status": "healthy",
        "features": [
            "Request rate limiting",
            "Query complexity analysis",
            "Query depth limiting",
            "Role-based limits",
            "Distributed limiting (Redis)"
        ]
    }

@app.get("/")
async def root():
    return {
        "title": "GraphQL Rate Limiting System",
        "description": "Comprehensive rate limiting with query complexity analysis",
        "rate_limits": {
            "guest": "30 req/min, 500 req/hour, complexity: 500",
            "customer": "120 req/min, 2000 req/hour, complexity: 1500",
            "seller": "300 req/min, 5000 req/hour, complexity: 3000",
            "admin": "1000 req/min, 20000 req/hour, complexity: 10000"
        },
        "headers": {
            "X-User-Role": "Set to guest, customer, seller, or admin",
            "X-User-ID": "Optional user identification"
        },
        "sample_queries": {
            "simple": "{ products(limit: 5) { id name price } }",
            "complex": "{ products { id name reviews { rating user { name orders { id total } } } } }",
            "expensive": "{ search(query: \"phone\") { products { id name reviews { rating comment } } } }",
            "very_expensive": "{ analytics reports(type: \"sales\") recommendations(userId: \"1\") { id name } }"
        }
    }

@app.get("/rate-limit-status")
async def rate_limit_status(request: Request):
    """Current rate limit status check"""
    user_role = request.headers.get('X-User-Role', 'guest')
    user_id = request.headers.get('X-User-ID')
    
    client_id = rate_limiter.get_client_id(request, user_id)
    
    # Get current status without incrementing counters
    if rate_limiter.use_redis:
        # Redis implementation for status check
        now = datetime.now()
        minute_key = f"rl:{client_id}:minute:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rl:{client_id}:hour:{now.strftime('%Y%m%d%H')}"
        day_key = f"rl:{client_id}:day:{now.strftime('%Y%m%d')}"
        
        pipeline = rate_limiter.redis_client.pipeline()
        pipeline.get(minute_key)
        pipeline.get(hour_key) 
        pipeline.get(day_key)
        
        results = await pipeline.execute()
        
        minute_count = int(results[0] or 0)
        hour_count = int(results[1] or 0)
        day_count = int(results[2] or 0)
    else:
        # In-memory implementation
        client_data = rate_limiter.request_counts[client_id]
        minute_count = client_data['minute']['count']
        hour_count = client_data['hour']['count']
        day_count = client_data['day']['count']
    
    limits = rate_limiter.get_user_limits(user_role)
    
    return {
        "client_id": client_id,
        "user_role": user_role,
        "current_usage": {
            "minute": f"{minute_count}/{limits['rpm']}",
            "hour": f"{hour_count}/{limits['rph']}",
            "day": f"{day_count}/{limits['rpd']}"
        },
        "remaining": {
            "minute": max(0, limits['rpm'] - minute_count),
            "hour": max(0, limits['rph'] - hour_count),
            "day": max(0, limits['rpd'] - day_count)
        },
        "limits": limits
    }

@app.get("/complexity-demo")
async def complexity_demo():
    """Query complexity examples"""
    return {
        "query_complexity_examples": {
            "simple_query": {
                "query": "{ products(limit: 5) { id name } }",
                "estimated_complexity": 20,
                "description": "Simple product listing"
            },
            "moderate_query": {
                "query": "{ products { id name price reviews { rating } } }",
                "estimated_complexity": 150,
                "description": "Products with reviews"
            },
            "complex_query": {
                "query": "{ products { reviews { user { orders { items { product { reviews } } } } } } }",
                "estimated_complexity": 800,
                "description": "Deep nested relationships"
            },
            "expensive_query": {
                "query": "{ search(query: \"phone\") { products { reviews { user { statistics } } } } analytics }",
                "estimated_complexity": 2000,
                "description": "Search + analytics + deep nesting"
            }
        },
        "complexity_calculation": {
            "field_costs": complexity_analyzer.field_costs,
            "factors": [
                "Base field cost",
                "Argument multipliers", 
                "Nested field costs",
                "List field multipliers"
            ]
        }
    }

if __name__ == "__main__":
    print("🚦 Starting GraphQL Rate Limiting Server...")
    print("🎯 Features:")
    print("   - Request rate limiting (minute/hour/day)")
    print("   - Query complexity analysis")
    print("   - Query depth limiting")
    print("   - Role-based limits")
    print("   - Burst protection")
    print("   - Redis support for distributed limiting")
    print("\n👥 User roles और limits:")
    config = RateLimitConfig()
    for role, limits in [
        ('guest', config.guest_limits),
        ('customer', config.customer_limits), 
        ('seller', config.seller_limits),
        ('admin', config.admin_limits)
    ]:
        print(f"   - {role}: {limits['rpm']}/min, {limits['rph']}/hour, complexity: {limits['complexity']}")
    
    print("\n🧪 Testing:")
    print("   - Use X-User-Role header (guest/customer/seller/admin)")
    print("   - Use X-User-ID header for user identification")
    print("   - Check /rate-limit-status for current usage")
    print("   - Try /complexity-demo for query examples")
    
    uvicorn.run(
        "08_graphql_rate_limiting:app",
        host="0.0.0.0",
        port=4023,
        reload=True,
        log_level="info"
    )