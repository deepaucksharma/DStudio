"""
API Gateway Security Layer
=========================

यह comprehensive API Gateway security implementation है।
AWS API Gateway, Kong, Envoy जैसे enterprise API gateways
में इसी level की security होती है।

Features:
- Request/Response Transformation
- Authentication/Authorization
- Rate Limiting
- Load Balancing
- Circuit Breaker
- Request Validation
- Response Filtering

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import asyncio
import aiohttp
import json
import time
import hashlib
import redis
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import jwt
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import yaml
from urllib.parse import urlparse, urljoin

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityPolicy(Enum):
    """Security policy types"""
    NONE = "none"
    API_KEY = "api_key"
    JWT_BEARER = "jwt_bearer"
    OAUTH2 = "oauth2"
    CUSTOM = "custom"

class LoadBalanceMethod(Enum):
    """Load balancing methods"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED = "weighted"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"

@dataclass
class UpstreamService:
    """Upstream service configuration"""
    service_id: str
    name: str
    base_url: str
    health_check_path: str
    weight: int = 1
    max_connections: int = 100
    timeout_seconds: int = 30
    retry_attempts: int = 3
    is_healthy: bool = True

@dataclass
class RouteConfig:
    """API route configuration"""
    route_id: str
    path_pattern: str
    methods: List[str]
    upstream_services: List[str]
    security_policy: SecurityPolicy
    rate_limit: Optional[Dict[str, int]] = None
    transformations: Optional[Dict[str, Any]] = None
    caching: Optional[Dict[str, Any]] = None
    validation_schema: Optional[Dict[str, Any]] = None

@dataclass
class SecurityContext:
    """Request security context"""
    authenticated: bool
    user_id: Optional[str]
    client_id: Optional[str]
    scopes: List[str]
    roles: List[str]
    api_key: Optional[str]
    rate_limit_key: str

class APIGatewaySecurityLayer:
    """
    Enterprise-grade API Gateway Security
    
    यह AWS API Gateway या Kong level की security provide करता है
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.upstream_services = {}
        self.routes = {}
        self.load_balancer_state = {}
        
        # JWT settings
        self.jwt_secret = "api_gateway_jwt_secret_change_in_production"
        self.jwt_algorithm = "HS256"
        
        # Default configurations
        self._load_default_configurations()
        
        # Health check scheduler
        self._start_health_checks()
    
    def _load_default_configurations(self):
        """Default services और routes load करता है"""
        
        # Upstream services (microservices)
        self.upstream_services = {
            "user_service": UpstreamService(
                service_id="user_service",
                name="User Management Service",
                base_url="http://localhost:8001",
                health_check_path="/health",
                weight=1,
                max_connections=50
            ),
            "payment_service": UpstreamService(
                service_id="payment_service", 
                name="Payment Service",
                base_url="http://localhost:8002",
                health_check_path="/health",
                weight=2,  # Higher weight
                max_connections=100
            ),
            "order_service": UpstreamService(
                service_id="order_service",
                name="Order Management Service", 
                base_url="http://localhost:8003",
                health_check_path="/health",
                weight=1,
                max_connections=75
            )
        }
        
        # API routes configuration
        self.routes = {
            "user_api": RouteConfig(
                route_id="user_api",
                path_pattern="/api/v1/users/*",
                methods=["GET", "POST", "PUT", "DELETE"],
                upstream_services=["user_service"],
                security_policy=SecurityPolicy.JWT_BEARER,
                rate_limit={"requests": 100, "window_seconds": 60},
                validation_schema={
                    "required_headers": ["authorization"],
                    "max_body_size": 1024 * 1024  # 1MB
                }
            ),
            "payment_api": RouteConfig(
                route_id="payment_api",
                path_pattern="/api/v1/payments/*",
                methods=["POST", "GET"],
                upstream_services=["payment_service"],
                security_policy=SecurityPolicy.OAUTH2,
                rate_limit={"requests": 50, "window_seconds": 60},
                validation_schema={
                    "required_headers": ["authorization", "x-idempotency-key"],
                    "max_body_size": 512 * 1024,  # 512KB
                    "required_scopes": ["payment:write"]
                }
            ),
            "order_api": RouteConfig(
                route_id="order_api",
                path_pattern="/api/v1/orders/*",
                methods=["GET", "POST", "PUT"],
                upstream_services=["order_service", "payment_service"],  # Multi-service
                security_policy=SecurityPolicy.JWT_BEARER,
                rate_limit={"requests": 200, "window_seconds": 60},
                caching={"ttl_seconds": 300, "cache_key_pattern": "order:{user_id}"}
            ),
            "public_api": RouteConfig(
                route_id="public_api",
                path_pattern="/api/v1/public/*",
                methods=["GET"],
                upstream_services=["user_service"],
                security_policy=SecurityPolicy.NONE,
                rate_limit={"requests": 1000, "window_seconds": 60},
                caching={"ttl_seconds": 3600}  # 1 hour cache
            )
        }
    
    async def process_request(self, request: Request) -> tuple[SecurityContext, RouteConfig, UpstreamService]:
        """
        Request processing pipeline
        
        1. Route matching
        2. Security validation
        3. Rate limiting
        4. Load balancing
        5. Request transformation
        """
        
        # 1. Route matching
        route_config = self._match_route(request.url.path, request.method)
        if not route_config:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # 2. Security validation
        security_context = await self._validate_security(request, route_config)
        
        # 3. Request validation
        await self._validate_request(request, route_config)
        
        # 4. Rate limiting
        await self._check_rate_limit(security_context, route_config)
        
        # 5. Load balancing
        upstream_service = await self._select_upstream_service(route_config)
        
        return security_context, route_config, upstream_service
    
    def _match_route(self, path: str, method: str) -> Optional[RouteConfig]:
        """Request path को routes के साथ match करता है"""
        
        for route_config in self.routes.values():
            # Simple pattern matching (production में regex use करें)
            pattern = route_config.path_pattern.replace("*", "")
            
            if path.startswith(pattern) and method in route_config.methods:
                return route_config
        
        return None
    
    async def _validate_security(self, request: Request, route_config: RouteConfig) -> SecurityContext:
        """Security policy के अनुसार request validate करता है"""
        
        security_context = SecurityContext(
            authenticated=False,
            user_id=None,
            client_id=None,
            scopes=[],
            roles=[],
            api_key=None,
            rate_limit_key=self._get_rate_limit_key(request)
        )
        
        if route_config.security_policy == SecurityPolicy.NONE:
            # Public endpoint - no authentication required
            return security_context
        
        elif route_config.security_policy == SecurityPolicy.API_KEY:
            return await self._validate_api_key(request, security_context)
        
        elif route_config.security_policy == SecurityPolicy.JWT_BEARER:
            return await self._validate_jwt_token(request, security_context)
        
        elif route_config.security_policy == SecurityPolicy.OAUTH2:
            return await self._validate_oauth2_token(request, security_context, route_config)
        
        else:
            raise HTTPException(status_code=500, detail="Unknown security policy")
    
    async def _validate_api_key(self, request: Request, context: SecurityContext) -> SecurityContext:
        """API key validation"""
        
        api_key = request.headers.get("x-api-key")
        if not api_key:
            raise HTTPException(status_code=401, detail="API key required")
        
        # Validate API key in Redis
        key_data = self.redis.get(f"api_key:{api_key}")
        if not key_data:
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        key_info = json.loads(key_data)
        
        context.authenticated = True
        context.client_id = key_info.get("client_id")
        context.scopes = key_info.get("scopes", [])
        context.api_key = api_key
        context.rate_limit_key = f"client:{context.client_id}"
        
        return context
    
    async def _validate_jwt_token(self, request: Request, context: SecurityContext) -> SecurityContext:
        """JWT token validation"""
        
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Bearer token required")
        
        token = auth_header[7:]  # Remove "Bearer "
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            context.authenticated = True
            context.user_id = payload.get("sub")
            context.client_id = payload.get("client_id")
            context.scopes = payload.get("scope", [])
            context.roles = payload.get("roles", [])
            context.rate_limit_key = f"user:{context.user_id}"
            
            return context
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def _validate_oauth2_token(
        self, 
        request: Request, 
        context: SecurityContext, 
        route_config: RouteConfig
    ) -> SecurityContext:
        """OAuth2 token validation with scope checking"""
        
        # First validate JWT
        context = await self._validate_jwt_token(request, context)
        
        # Check required scopes
        required_scopes = route_config.validation_schema.get("required_scopes", [])
        if required_scopes:
            if not all(scope in context.scopes for scope in required_scopes):
                raise HTTPException(status_code=403, detail="Insufficient scope")
        
        return context
    
    async def _validate_request(self, request: Request, route_config: RouteConfig):
        """Request validation (headers, body size, etc.)"""
        
        validation_schema = route_config.validation_schema
        if not validation_schema:
            return
        
        # Check required headers
        required_headers = validation_schema.get("required_headers", [])
        for header in required_headers:
            if header not in request.headers:
                raise HTTPException(status_code=400, detail=f"Missing required header: {header}")
        
        # Check body size
        max_body_size = validation_schema.get("max_body_size")
        if max_body_size:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > max_body_size:
                raise HTTPException(status_code=413, detail="Request body too large")
    
    async def _check_rate_limit(self, context: SecurityContext, route_config: RouteConfig):
        """Rate limiting check"""
        
        rate_limit = route_config.rate_limit
        if not rate_limit:
            return
        
        key = f"rate_limit:{route_config.route_id}:{context.rate_limit_key}"
        window = rate_limit["window_seconds"]
        limit = rate_limit["requests"]
        
        # Sliding window rate limiting
        now = time.time()
        window_start = now - window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_count = self.redis.zcard(key)
        
        if current_count >= limit:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded",
                headers={"Retry-After": str(window)}
            )
        
        # Add current request
        self.redis.zadd(key, {str(now): now})
        self.redis.expire(key, window)
    
    async def _select_upstream_service(self, route_config: RouteConfig) -> UpstreamService:
        """Load balancing के लिए upstream service select करता है"""
        
        available_services = []
        
        for service_id in route_config.upstream_services:
            service = self.upstream_services.get(service_id)
            if service and service.is_healthy:
                available_services.append(service)
        
        if not available_services:
            raise HTTPException(status_code=503, detail="No healthy upstream services")
        
        # Round-robin load balancing
        route_id = route_config.route_id
        if route_id not in self.load_balancer_state:
            self.load_balancer_state[route_id] = 0
        
        index = self.load_balancer_state[route_id] % len(available_services)
        self.load_balancer_state[route_id] += 1
        
        return available_services[index]
    
    async def proxy_request(
        self, 
        request: Request, 
        upstream_service: UpstreamService,
        route_config: RouteConfig
    ) -> JSONResponse:
        """Request को upstream service पर proxy करता है"""
        
        # Build upstream URL
        upstream_path = request.url.path
        upstream_url = urljoin(upstream_service.base_url, upstream_path)
        
        # Prepare headers
        headers = dict(request.headers)
        headers["X-Forwarded-For"] = request.client.host
        headers["X-Gateway-Route"] = route_config.route_id
        
        # Get request body
        body = await request.body()
        
        try:
            # Make upstream request
            timeout = aiohttp.ClientTimeout(total=upstream_service.timeout_seconds)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    method=request.method,
                    url=upstream_url,
                    headers=headers,
                    data=body,
                    params=request.query_params
                ) as response:
                    
                    # Get response data
                    response_body = await response.text()
                    response_headers = dict(response.headers)
                    
                    # Apply response transformations
                    response_body = await self._transform_response(
                        response_body, route_config
                    )
                    
                    # Cache response if configured
                    await self._cache_response(
                        request, response_body, route_config
                    )
                    
                    # Add gateway headers
                    response_headers["X-Gateway-Service"] = upstream_service.service_id
                    response_headers["X-Gateway-Latency"] = str(time.time())
                    
                    return JSONResponse(
                        content=json.loads(response_body) if response_body else {},
                        status_code=response.status,
                        headers=response_headers
                    )
        
        except asyncio.TimeoutError:
            # Mark service as potentially unhealthy
            await self._record_service_error(upstream_service.service_id, "timeout")
            raise HTTPException(status_code=504, detail="Upstream service timeout")
        
        except Exception as e:
            await self._record_service_error(upstream_service.service_id, str(e))
            raise HTTPException(status_code=502, detail="Upstream service error")
    
    async def _transform_response(self, response_body: str, route_config: RouteConfig) -> str:
        """Response transformation (filtering, formatting)"""
        
        transformations = route_config.transformations
        if not transformations:
            return response_body
        
        try:
            data = json.loads(response_body) if response_body else {}
            
            # Filter sensitive fields
            sensitive_fields = transformations.get("filter_fields", [])
            if sensitive_fields:
                data = self._filter_sensitive_data(data, sensitive_fields)
            
            # Add computed fields
            computed_fields = transformations.get("add_fields", {})
            if computed_fields:
                data.update(computed_fields)
            
            return json.dumps(data)
            
        except json.JSONDecodeError:
            return response_body
    
    def _filter_sensitive_data(self, data: Any, sensitive_fields: List[str]) -> Any:
        """Sensitive data को response से filter करता है"""
        
        if isinstance(data, dict):
            return {
                key: self._filter_sensitive_data(value, sensitive_fields)
                for key, value in data.items()
                if key not in sensitive_fields
            }
        elif isinstance(data, list):
            return [self._filter_sensitive_data(item, sensitive_fields) for item in data]
        else:
            return data
    
    async def _cache_response(self, request: Request, response_body: str, route_config: RouteConfig):
        """Response caching"""
        
        caching = route_config.caching
        if not caching:
            return
        
        # Generate cache key
        cache_key_pattern = caching.get("cache_key_pattern", "default:{path}")
        cache_key = cache_key_pattern.format(
            path=request.url.path,
            user_id="anonymous",  # Would be extracted from security context
            query=str(request.query_params)
        )
        
        # Store in Redis with TTL
        ttl = caching.get("ttl_seconds", 300)
        self.redis.setex(f"cache:{cache_key}", ttl, response_body)
    
    async def _get_cached_response(self, request: Request, route_config: RouteConfig) -> Optional[str]:
        """Cached response retrieve करता है"""
        
        caching = route_config.caching
        if not caching:
            return None
        
        cache_key_pattern = caching.get("cache_key_pattern", "default:{path}")
        cache_key = cache_key_pattern.format(
            path=request.url.path,
            user_id="anonymous",
            query=str(request.query_params)
        )
        
        return self.redis.get(f"cache:{cache_key}")
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Rate limiting के लिए key generate करता है"""
        
        # Fallback to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    async def _record_service_error(self, service_id: str, error: str):
        """Service error को record करता है health check के लिए"""
        
        error_key = f"service_errors:{service_id}"
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": error
        }
        
        self.redis.lpush(error_key, json.dumps(error_data))
        self.redis.ltrim(error_key, 0, 99)  # Keep last 100 errors
        
        # Check if service should be marked unhealthy
        recent_errors = self.redis.llen(error_key)
        if recent_errors > 10:  # More than 10 recent errors
            service = self.upstream_services.get(service_id)
            if service:
                service.is_healthy = False
                logger.warning(f"Marked service {service_id} as unhealthy due to errors")
    
    def _start_health_checks(self):
        """Health check scheduler start करता है"""
        
        async def health_check_worker():
            while True:
                for service in self.upstream_services.values():
                    try:
                        health_url = urljoin(service.base_url, service.health_check_path)
                        
                        timeout = aiohttp.ClientTimeout(total=5)
                        async with aiohttp.ClientSession(timeout=timeout) as session:
                            async with session.get(health_url) as response:
                                if response.status == 200:
                                    if not service.is_healthy:
                                        logger.info(f"Service {service.service_id} is healthy again")
                                    service.is_healthy = True
                                else:
                                    service.is_healthy = False
                                    
                    except Exception as e:
                        service.is_healthy = False
                        logger.warning(f"Health check failed for {service.service_id}: {e}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
        
        # Start health check in background
        asyncio.create_task(health_check_worker())

# FastAPI application with Gateway middleware
app = FastAPI(title="API Gateway Security Layer")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# API Gateway
api_gateway = APIGatewaySecurityLayer(redis_client)

class APIGatewayMiddleware(BaseHTTPMiddleware):
    """API Gateway middleware"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            # Check cache first
            route_config = api_gateway._match_route(request.url.path, request.method)
            if route_config:
                cached_response = await api_gateway._get_cached_response(request, route_config)
                if cached_response:
                    return JSONResponse(content=json.loads(cached_response))
            
            # Process request through gateway
            security_context, route_config, upstream_service = await api_gateway.process_request(request)
            
            # Proxy to upstream service
            return await api_gateway.proxy_request(request, upstream_service, route_config)
            
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
        except Exception as e:
            logger.error(f"Gateway error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal gateway error"}
            )

# Add middleware
app.add_middleware(APIGatewayMiddleware)

@app.get("/gateway/health")
async def gateway_health():
    """Gateway health check"""
    
    healthy_services = sum(1 for service in api_gateway.upstream_services.values() if service.is_healthy)
    total_services = len(api_gateway.upstream_services)
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "upstream_services": {
            "healthy": healthy_services,
            "total": total_services,
            "services": [
                {
                    "service_id": service.service_id,
                    "name": service.name,
                    "healthy": service.is_healthy
                }
                for service in api_gateway.upstream_services.values()
            ]
        }
    }

@app.get("/gateway/routes")
async def gateway_routes():
    """Gateway routes configuration"""
    
    return {
        "routes": [
            {
                "route_id": route.route_id,
                "path_pattern": route.path_pattern,
                "methods": route.methods,
                "security_policy": route.security_policy.value,
                "upstream_services": route.upstream_services
            }
            for route in api_gateway.routes.values()
        ]
    }

@app.post("/gateway/invalidate-cache")
async def invalidate_cache(pattern: str = "*"):
    """Cache invalidation"""
    
    keys = redis_client.keys(f"cache:{pattern}")
    if keys:
        redis_client.delete(*keys)
    
    return {"message": f"Invalidated {len(keys)} cache entries"}

# Mock upstream service endpoints for testing
@app.get("/mock/user-service/health")
async def mock_user_service_health():
    return {"status": "healthy", "service": "user_service"}

@app.get("/api/v1/users/profile")
async def mock_user_profile():
    return {"user_id": "123", "name": "Test User", "email": "test@example.com"}

@app.get("/api/v1/public/status")
async def mock_public_status():
    return {"status": "API is running", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    
    print("🚪 API Gateway Security Layer")
    print("🔒 Enterprise-grade request processing")
    print("⚖️ Load balancing और health checking")
    print("🔄 Request/Response transformation")
    print("📊 Caching और rate limiting")
    print("🏦 AWS API Gateway level functionality")
    
    uvicorn.run(app, host="0.0.0.0", port=8006)

"""
Production Deployment Notes:
============================

1. High Availability:
   - Multiple gateway instances behind load balancer
   - Redis Cluster for shared state
   - Circuit breaker for upstream services
   - Graceful degradation strategies

2. Monitoring:
   - Request/Response metrics
   - Latency tracking
   - Error rate monitoring
   - Upstream service health
   - Cache hit ratios

3. Security Enhancements:
   - WAF integration
   - DDoS protection
   - IP whitelisting/blacklisting
   - SSL/TLS termination
   - Request signing verification

4. Performance Optimization:
   - Connection pooling
   - HTTP/2 support
   - Compression
   - CDN integration
   - Intelligent caching strategies

यह API Gateway AWS API Gateway, Kong, Istio level की functionality provide करता है!
"""