#!/usr/bin/env python3
"""
API Gateway Implementation using Kong
Production-ready gateway for Indian scale applications

जैसे Mumbai में Toll Plaza सभी vehicles को manage करता है,
वैसे ही API Gateway सभी requests को handle करता है
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import jwt
import redis
import requests
import aiohttp
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# Mumbai-style logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("KongGateway")

# Metrics for monitoring - जैसे BEST bus की live tracking
REQUEST_COUNT = Counter('api_gateway_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('api_gateway_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('api_gateway_active_connections', 'Active connections')
RATE_LIMIT_HITS = Counter('api_gateway_rate_limit_hits_total', 'Rate limit hits', ['service'])

@dataclass
class ServiceRoute:
    """Service routing configuration - जैसे Mumbai local train routes"""
    path: str
    service_url: str
    method: str = "GET"
    rate_limit: int = 1000  # requests per minute
    auth_required: bool = True
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker_enabled: bool = True
    
class RateLimiter:
    """Rate limiting like Mumbai local train entry gates"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def is_allowed(self, key: str, limit: int, window: int = 60) -> tuple[bool, dict]:
        """
        Check if request is within rate limit
        Args:
            key: Unique identifier (IP, user_id, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
        """
        current_time = int(time.time())
        pipeline = self.redis.pipeline()
        
        # Sliding window algorithm - जैसे local train में people counting
        window_start = current_time - window
        
        # Remove old entries
        pipeline.zremrangebyscore(key, 0, window_start)
        # Count current entries
        pipeline.zcard(key)
        # Add current request
        pipeline.zadd(key, {str(current_time): current_time})
        # Set expiry
        pipeline.expire(key, window)
        
        results = pipeline.execute()
        current_requests = results[1]
        
        allowed = current_requests < limit
        remaining = max(0, limit - current_requests - 1)
        
        rate_limit_info = {
            "allowed": allowed,
            "limit": limit,
            "remaining": remaining,
            "reset_time": current_time + window,
            "window": window
        }
        
        if not allowed:
            RATE_LIMIT_HITS.labels(service=key.split(':')[0]).inc()
            logger.warning(f"Rate limit exceeded for {key}: {current_requests}/{limit}")
        
        return allowed, rate_limit_info

class CircuitBreaker:
    """Circuit breaker pattern - जैसे Mumbai में power cut protection"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def is_allowed(self) -> bool:
        """Check if request should be allowed through circuit breaker"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                logger.info("Circuit breaker transitioning to HALF_OPEN")
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful request"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            logger.info("Circuit breaker CLOSED - Service recovered like Mumbai after monsoon!")
    
    def record_failure(self):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.error(f"Circuit breaker OPENED - Service down like Harbour line during heavy rains!")

class AuthManager:
    """JWT Authentication manager - जैसे Mumbai Metro card validation"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            if not token.startswith("Bearer "):
                return None
            
            token = token[7:]  # Remove "Bearer " prefix
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check expiration
            if payload.get('exp', 0) < time.time():
                return None
                
            return payload
        except jwt.InvalidTokenError:
            return None
    
    def create_token(self, user_id: str, role: str = "user", expires_in: int = 3600) -> str:
        """Create JWT token for testing"""
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": time.time() + expires_in,
            "iat": time.time(),
            "iss": "kong-gateway"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

class LoadBalancer:
    """Load balancer - जैसे Mumbai traffic signals optimization"""
    
    def __init__(self):
        self.servers = []
        self.current_index = 0
        self.health_status = {}
        
    def add_server(self, server_url: str):
        """Add server to load balancer"""
        self.servers.append(server_url)
        self.health_status[server_url] = True
        
    def get_next_server(self) -> Optional[str]:
        """Get next healthy server using round-robin"""
        healthy_servers = [s for s in self.servers if self.health_status.get(s, True)]
        
        if not healthy_servers:
            logger.error("No healthy servers available!")
            return None
            
        server = healthy_servers[self.current_index % len(healthy_servers)]
        self.current_index += 1
        
        return server
    
    async def check_health(self, server_url: str) -> bool:
        """Check server health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{server_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    healthy = response.status == 200
                    self.health_status[server_url] = healthy
                    return healthy
        except:
            self.health_status[server_url] = False
            return False

class KongGateway:
    """Main API Gateway class - जैसे Mumbai CST station का main control room"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.app = FastAPI(title="Kong Gateway", version="1.0.0")
        
        # Initialize components
        self.redis = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        self.rate_limiter = RateLimiter(self.redis)
        self.auth_manager = AuthManager(config.get('jwt_secret', 'mumbai-secret-key'))
        self.load_balancer = LoadBalancer()
        self.circuit_breakers = {}
        self.routes = {}
        
        # Setup middleware
        self._setup_middleware()
        self._setup_routes()
        
        # Health check task
        asyncio.create_task(self._health_check_loop())
        
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            
            # Track active connections
            ACTIVE_CONNECTIONS.inc()
            
            try:
                response = await call_next(request)
                
                # Record metrics
                duration = time.time() - start_time
                REQUEST_DURATION.observe(duration)
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=response.status_code
                ).inc()
                
                logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
                return response
                
            finally:
                ACTIVE_CONNECTIONS.dec()
    
    def add_route(self, route: ServiceRoute):
        """Add new service route"""
        self.routes[route.path] = route
        
        # Initialize circuit breaker for this route
        if route.circuit_breaker_enabled:
            self.circuit_breakers[route.path] = CircuitBreaker()
            
        logger.info(f"Added route: {route.path} -> {route.service_url}")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Gateway health check"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Gateway running smoothly like Mumbai Dabbawalas!",
                "active_routes": len(self.routes),
                "redis_connected": await self._check_redis()
            }
        
        @self.app.get("/metrics")
        async def metrics():
            """Prometheus metrics endpoint"""
            from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
            
        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy_request(path: str, request: Request):
            """Main proxy handler - सभी requests यहाँ आती हैं"""
            return await self._handle_request(path, request)
    
    async def _handle_request(self, path: str, request: Request):
        """Handle incoming request with all middleware"""
        
        # Find matching route
        route = self._find_route(path)
        if not route:
            raise HTTPException(status_code=404, detail="Route not found")
        
        # Authentication check
        if route.auth_required:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(status_code=401, detail="Authorization header required")
            
            user_data = self.auth_manager.verify_token(auth_header)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid token")
        
        # Rate limiting
        client_ip = request.client.host
        rate_limit_key = f"{route.path}:{client_ip}"
        allowed, rate_info = await self.rate_limiter.is_allowed(
            rate_limit_key, route.rate_limit
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429, 
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset_time"])
                }
            )
        
        # Circuit breaker check
        circuit_breaker = self.circuit_breakers.get(route.path)
        if circuit_breaker and not circuit_breaker.is_allowed():
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable - Circuit breaker open"
            )
        
        # Forward request to backend service
        try:
            response_data = await self._forward_request(route, request)
            
            if circuit_breaker:
                circuit_breaker.record_success()
            
            return response_data
            
        except Exception as e:
            if circuit_breaker:
                circuit_breaker.record_failure()
            
            logger.error(f"Request forwarding failed: {str(e)}")
            raise HTTPException(status_code=502, detail="Backend service error")
    
    def _find_route(self, path: str) -> Optional[ServiceRoute]:
        """Find matching route for given path"""
        # Simple prefix matching - production में proper regex matching करेंगे
        for route_path, route in self.routes.items():
            if path.startswith(route_path.strip('/')):
                return route
        return None
    
    async def _forward_request(self, route: ServiceRoute, request: Request):
        """Forward request to backend service"""
        
        # Get backend server
        backend_url = route.service_url
        if hasattr(self.load_balancer, 'servers') and self.load_balancer.servers:
            backend_url = self.load_balancer.get_next_server() or route.service_url
        
        # Build target URL
        target_url = f"{backend_url.rstrip('/')}/{request.url.path.lstrip('/')}"
        
        # Prepare headers (remove hop-by-hop headers)
        headers = dict(request.headers)
        hop_by_hop_headers = ['connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers', 'transfer-encoding', 'upgrade']
        for header in hop_by_hop_headers:
            headers.pop(header, None)
        
        # Add tracing headers
        headers['X-Forwarded-For'] = request.client.host
        headers['X-Gateway-Request-ID'] = hashlib.md5(f"{time.time()}{request.url.path}".encode()).hexdigest()[:16]
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=route.timeout)) as session:
            # Handle request body for POST/PUT requests
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.body()
            
            for attempt in range(route.retry_count):
                try:
                    async with session.request(
                        method=request.method,
                        url=target_url,
                        headers=headers,
                        params=dict(request.query_params),
                        data=body
                    ) as response:
                        response_data = await response.read()
                        
                        # Return response with original headers
                        return JSONResponse(
                            content=json.loads(response_data.decode()) if response_data else {},
                            status_code=response.status,
                            headers=dict(response.headers)
                        )
                        
                except asyncio.TimeoutError:
                    if attempt == route.retry_count - 1:
                        raise HTTPException(status_code=504, detail="Gateway timeout")
                    logger.warning(f"Request timeout, retrying... ({attempt + 1}/{route.retry_count})")
                    await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
                except Exception as e:
                    if attempt == route.retry_count - 1:
                        raise e
                    logger.warning(f"Request failed, retrying... ({attempt + 1}/{route.retry_count}): {str(e)}")
                    await asyncio.sleep(0.5 * (attempt + 1))
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            self.redis.ping()
            return True
        except:
            return False
    
    async def _health_check_loop(self):
        """Background task for health checking backend services"""
        while True:
            for server in self.load_balancer.servers:
                await self.load_balancer.check_health(server)
            await asyncio.sleep(30)  # Check every 30 seconds

def create_production_gateway():
    """Create production-ready gateway configuration"""
    
    config = {
        'jwt_secret': 'mumbai-production-secret-2025',
        'redis_host': 'localhost',
        'redis_port': 6379,
        'redis_db': 0
    }
    
    gateway = KongGateway(config)
    
    # Add service routes - Flipkart example
    routes = [
        # User service
        ServiceRoute(
            path="/api/users",
            service_url="http://user-service:8001",
            rate_limit=500,  # 500 req/min for user operations
            auth_required=True
        ),
        
        # Product catalog service
        ServiceRoute(
            path="/api/products",
            service_url="http://product-service:8002",
            rate_limit=1000,  # High traffic for product browsing
            auth_required=False  # Public product catalog
        ),
        
        # Order service  
        ServiceRoute(
            path="/api/orders",
            service_url="http://order-service:8003",
            rate_limit=200,  # Limited order rate
            auth_required=True,
            timeout=60  # Orders might take longer
        ),
        
        # Payment service
        ServiceRoute(
            path="/api/payments",
            service_url="http://payment-service:8004",
            rate_limit=100,  # Very limited payment rate
            auth_required=True,
            timeout=30,
            circuit_breaker_enabled=True
        ),
        
        # Search service
        ServiceRoute(
            path="/api/search",
            service_url="http://search-service:8005",
            rate_limit=2000,  # High search traffic
            auth_required=False,
            timeout=10  # Quick search responses
        )
    ]
    
    for route in routes:
        gateway.add_route(route)
    
    # Add backend servers for load balancing
    gateway.load_balancer.add_server("http://backend-1:8001")
    gateway.load_balancer.add_server("http://backend-2:8001")
    gateway.load_balancer.add_server("http://backend-3:8001")
    
    return gateway

if __name__ == "__main__":
    # Create and run gateway
    gateway = create_production_gateway()
    
    # Production deployment - जैसे Mumbai local train का time table
    logger.info("Starting Kong Gateway - Ready for Mumbai scale traffic! 🚉")
    logger.info("Endpoints:")
    logger.info("  - Health: http://localhost:8000/health")
    logger.info("  - Metrics: http://localhost:8000/metrics")
    logger.info("  - API routes: /api/*")
    
    # Test token generation for development
    test_token = gateway.auth_manager.create_token("user123", "premium")
    logger.info(f"Test token: Bearer {test_token}")
    
    uvicorn.run(
        gateway.app,
        host="0.0.0.0",
        port=8000,
        workers=4,  # Multi-worker for production
        log_level="info",
        access_log=True
    )