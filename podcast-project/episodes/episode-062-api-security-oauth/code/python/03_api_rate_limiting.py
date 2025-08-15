"""
Advanced API Rate Limiting System
=================================

यह system comprehensive rate limiting implement करता है।
Zomato, Swiggy जैसे high traffic apps में इसी level की
rate limiting होती है API abuse prevent करने के लिए।

Features:
- Multiple Rate Limiting Algorithms
- Distributed Rate Limiting with Redis
- Dynamic Rate Limits
- Burst Protection
- IP-based and User-based Limiting
- Circuit Breaker Integration

Author: Hindi Tech Podcast
Episode: 062 - API Security & OAuth
"""

import redis
import time
import json
import math
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass, asdict
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms"""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    limit: int                    # Requests per window
    window_seconds: int          # Time window in seconds
    algorithm: RateLimitAlgorithm
    burst_limit: Optional[int] = None    # Burst allowance
    identifier_type: str = "ip"          # ip, user_id, api_key
    
@dataclass
class RateLimitResult:
    """Rate limit check result"""
    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None
    limit: int = 0
    used: int = 0

class DistributedRateLimiter:
    """
    Distributed Rate Limiter using Redis
    
    यह Flipkart/Amazon level की distributed rate limiting provide करता है
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Different rate limits for different scenarios
        self.rate_limits = {
            # API endpoint specific limits
            "auth_login": RateLimitConfig(
                limit=5, window_seconds=300, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
            "auth_register": RateLimitConfig(
                limit=3, window_seconds=3600, algorithm=RateLimitAlgorithm.FIXED_WINDOW
            ),
            "payment_initiate": RateLimitConfig(
                limit=10, window_seconds=60, algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                burst_limit=5
            ),
            "api_general": RateLimitConfig(
                limit=1000, window_seconds=3600, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
            "search_query": RateLimitConfig(
                limit=100, window_seconds=60, algorithm=RateLimitAlgorithm.LEAKY_BUCKET
            ),
            
            # User tier based limits - Premium vs Free users
            "free_user": RateLimitConfig(
                limit=100, window_seconds=3600, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
            "premium_user": RateLimitConfig(
                limit=1000, window_seconds=3600, algorithm=RateLimitAlgorithm.SLIDING_WINDOW
            ),
            "enterprise_user": RateLimitConfig(
                limit=10000, window_seconds=3600, algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
                burst_limit=1000
            )
        }
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        endpoint: str,
        user_tier: str = "free_user"
    ) -> RateLimitResult:
        """
        Rate limit check करता है - Multiple algorithms support
        
        identifier: IP address या user_id
        endpoint: API endpoint name
        user_tier: User की tier (free, premium, enterprise)
        """
        
        # Get rate limit config
        config = self.rate_limits.get(endpoint, self.rate_limits["api_general"])
        user_config = self.rate_limits.get(user_tier, self.rate_limits["free_user"])
        
        # Use more restrictive limit
        effective_config = self._get_effective_config(config, user_config)
        
        if effective_config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._token_bucket_check(identifier, endpoint, effective_config)
        elif effective_config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._sliding_window_check(identifier, endpoint, effective_config)
        elif effective_config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._fixed_window_check(identifier, endpoint, effective_config)
        elif effective_config.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            return await self._leaky_bucket_check(identifier, endpoint, effective_config)
        else:
            # Fallback to sliding window
            return await self._sliding_window_check(identifier, endpoint, effective_config)
    
    async def _token_bucket_check(
        self, 
        identifier: str, 
        endpoint: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """
        Token Bucket Algorithm - Best for burst handling
        
        Paytm payment APIs में इसी algorithm का use होता है
        """
        
        key = f"rate_limit:token_bucket:{endpoint}:{identifier}"
        now = time.time()
        
        # Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local burst_limit = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        -- Get current bucket state
        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or limit
        local last_refill = tonumber(bucket[2]) or now
        
        -- Calculate refill
        local elapsed = now - last_refill
        local refill_rate = limit / window
        local new_tokens = math.min(limit + burst_limit, tokens + (elapsed * refill_rate))
        
        if new_tokens >= 1 then
            new_tokens = new_tokens - 1
            redis.call('HMSET', key, 'tokens', new_tokens, 'last_refill', now)
            redis.call('EXPIRE', key, window * 2)
            return {1, math.floor(new_tokens), math.floor((limit - new_tokens) / refill_rate)}
        else
            return {0, 0, math.floor((1 - new_tokens) / refill_rate)}
        end
        """
        
        burst_limit = config.burst_limit or 0
        result = self.redis.eval(
            lua_script, 1, key, 
            config.limit, config.window_seconds, burst_limit, now
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        retry_after = int(result[2]) if not allowed else None
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=int(now + config.window_seconds),
            retry_after=retry_after,
            limit=config.limit,
            used=config.limit - remaining
        )
    
    async def _sliding_window_check(
        self, 
        identifier: str, 
        endpoint: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """
        Sliding Window Algorithm - Most accurate rate limiting
        
        WhatsApp Business API में इसी algorithm का use होता है
        """
        
        key = f"rate_limit:sliding_window:{endpoint}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds
        
        # Lua script for atomic sliding window
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window_start = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local window_seconds = tonumber(ARGV[4])
        
        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, '-inf', window_start)
        
        -- Count current requests
        local current_count = redis.call('ZCARD', key)
        
        if current_count < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window_seconds)
            return {1, limit - current_count - 1, current_count + 1}
        else
            return {0, 0, current_count}
        end
        """
        
        result = self.redis.eval(
            lua_script, 1, key,
            config.limit, window_start, now, config.window_seconds
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        used = int(result[2])
        
        # Calculate reset time (when oldest request will expire)
        if not allowed:
            oldest_key = f"{key}:oldest"
            oldest_time = self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest_time[0][1] + config.window_seconds) if oldest_time else int(now + config.window_seconds)
        else:
            reset_time = int(now + config.window_seconds)
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=reset_time,
            retry_after=reset_time - int(now) if not allowed else None,
            limit=config.limit,
            used=used
        )
    
    async def _fixed_window_check(
        self, 
        identifier: str, 
        endpoint: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """
        Fixed Window Algorithm - Simple और fast
        
        Simple applications के लिए suitable है
        """
        
        now = time.time()
        window_start = int(now // config.window_seconds) * config.window_seconds
        key = f"rate_limit:fixed_window:{endpoint}:{identifier}:{window_start}"
        
        # Get current count
        current_count = self.redis.get(key)
        current_count = int(current_count) if current_count else 0
        
        if current_count < config.limit:
            # Increment counter
            pipeline = self.redis.pipeline()
            pipeline.incr(key)
            pipeline.expire(key, config.window_seconds)
            pipeline.execute()
            
            return RateLimitResult(
                allowed=True,
                remaining=config.limit - current_count - 1,
                reset_time=window_start + config.window_seconds,
                limit=config.limit,
                used=current_count + 1
            )
        else:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=window_start + config.window_seconds,
                retry_after=window_start + config.window_seconds - int(now),
                limit=config.limit,
                used=current_count
            )
    
    async def _leaky_bucket_check(
        self, 
        identifier: str, 
        endpoint: str, 
        config: RateLimitConfig
    ) -> RateLimitResult:
        """
        Leaky Bucket Algorithm - Smooth rate limiting
        
        Search APIs जैसे continuous requests के लिए good है
        """
        
        key = f"rate_limit:leaky_bucket:{endpoint}:{identifier}"
        now = time.time()
        
        # Lua script for leaky bucket
        lua_script = """
        local key = KEYS[1]
        local limit = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        
        -- Get current state
        local bucket = redis.call('HMGET', key, 'level', 'last_leak')
        local level = tonumber(bucket[1]) or 0
        local last_leak = tonumber(bucket[2]) or now
        
        -- Calculate leak
        local elapsed = now - last_leak
        local leak_rate = limit / window
        local leaked = elapsed * leak_rate
        local new_level = math.max(0, level - leaked)
        
        if new_level < limit then
            new_level = new_level + 1
            redis.call('HMSET', key, 'level', new_level, 'last_leak', now)
            redis.call('EXPIRE', key, window * 2)
            return {1, limit - new_level, new_level}
        else
            return {0, 0, new_level}
        end
        """
        
        result = self.redis.eval(
            lua_script, 1, key,
            config.limit, config.window_seconds, now
        )
        
        allowed = bool(result[0])
        remaining = int(result[1])
        used = int(result[2])
        
        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            reset_time=int(now + config.window_seconds),
            retry_after=1 if not allowed else None,  # Try again in 1 second
            limit=config.limit,
            used=used
        )
    
    def _get_effective_config(
        self, 
        endpoint_config: RateLimitConfig, 
        user_config: RateLimitConfig
    ) -> RateLimitConfig:
        """Most restrictive config return करता है"""
        
        # Use minimum of both limits
        effective_limit = min(endpoint_config.limit, user_config.limit)
        effective_window = min(endpoint_config.window_seconds, user_config.window_seconds)
        
        return RateLimitConfig(
            limit=effective_limit,
            window_seconds=effective_window,
            algorithm=endpoint_config.algorithm,
            burst_limit=endpoint_config.burst_limit
        )
    
    async def get_rate_limit_stats(self, identifier: str, endpoint: str) -> Dict[str, Any]:
        """Rate limit statistics return करता है"""
        
        stats = {}
        
        for algo in RateLimitAlgorithm:
            key_pattern = f"rate_limit:{algo.value}:{endpoint}:{identifier}*"
            keys = self.redis.keys(key_pattern)
            
            if keys:
                stats[algo.value] = {
                    "active_keys": len(keys),
                    "keys": keys
                }
        
        return stats
    
    async def reset_rate_limit(self, identifier: str, endpoint: str) -> bool:
        """Rate limit को reset करता है - Admin function"""
        
        pattern = f"rate_limit:*:{endpoint}:{identifier}*"
        keys = self.redis.keys(pattern)
        
        if keys:
            self.redis.delete(*keys)
            return True
        
        return False

class CircuitBreaker:
    """
    Circuit Breaker for API protection
    
    Rate limiting के साथ circuit breaker भी zaroori है
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.failure_threshold = 5      # 5 failures में trip
        self.success_threshold = 3      # 3 success में close
        self.timeout_seconds = 60       # 1 minute timeout
    
    async def call_api(self, endpoint: str, func, *args, **kwargs):
        """API call with circuit breaker protection"""
        
        state_key = f"circuit_breaker:{endpoint}"
        
        # Get current state
        state_data = self.redis.get(state_key)
        if state_data:
            state_data = json.loads(state_data)
            state = state_data.get("state", "closed")
            last_failure = state_data.get("last_failure", 0)
            failure_count = state_data.get("failure_count", 0)
        else:
            state = "closed"
            last_failure = 0
            failure_count = 0
        
        # Check if circuit should be half-open
        if state == "open" and (time.time() - last_failure) > self.timeout_seconds:
            state = "half_open"
        
        # Reject if circuit is open
        if state == "open":
            raise HTTPException(
                status_code=503, 
                detail="Service temporarily unavailable - Circuit breaker open"
            )
        
        try:
            # Call the function
            result = await func(*args, **kwargs)
            
            # Success - reset or close circuit
            if state == "half_open":
                # Close circuit
                self.redis.delete(state_key)
            elif failure_count > 0:
                # Reduce failure count
                new_state_data = {
                    "state": "closed",
                    "failure_count": max(0, failure_count - 1),
                    "last_failure": last_failure
                }
                self.redis.setex(state_key, 3600, json.dumps(new_state_data))
            
            return result
            
        except Exception as e:
            # Failure - increment count or open circuit
            failure_count += 1
            
            if failure_count >= self.failure_threshold:
                # Open circuit
                new_state_data = {
                    "state": "open",
                    "failure_count": failure_count,
                    "last_failure": time.time()
                }
            else:
                # Increment failure count
                new_state_data = {
                    "state": "closed",
                    "failure_count": failure_count,
                    "last_failure": time.time()
                }
            
            self.redis.setex(state_key, 3600, json.dumps(new_state_data))
            raise e

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic rate limiting
    
    हर request पर automatically rate limit check करता है
    """
    
    def __init__(self, app, rate_limiter: DistributedRateLimiter):
        super().__init__(app)
        self.rate_limiter = rate_limiter
    
    async def dispatch(self, request: Request, call_next):
        # Extract identifier (IP or user ID)
        identifier = self._get_identifier(request)
        
        # Extract endpoint
        endpoint = self._get_endpoint(request)
        
        # Extract user tier from token (if available)
        user_tier = self._get_user_tier(request)
        
        # Check rate limit
        result = await self.rate_limiter.check_rate_limit(
            identifier, endpoint, user_tier
        )
        
        if not result.allowed:
            # Rate limit exceeded
            headers = {
                "X-RateLimit-Limit": str(result.limit),
                "X-RateLimit-Remaining": str(result.remaining),
                "X-RateLimit-Reset": str(result.reset_time),
            }
            
            if result.retry_after:
                headers["Retry-After"] = str(result.retry_after)
            
            logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Try again in {result.retry_after} seconds.",
                    "limit": result.limit,
                    "remaining": result.remaining,
                    "reset_time": result.reset_time
                },
                headers=headers
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(result.reset_time)
        response.headers["X-RateLimit-Used"] = str(result.used)
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Request से identifier extract करता है"""
        
        # Try to get user ID from token first
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Parse JWT token and extract user ID
            # Simplified version - actual implementation would parse JWT
            try:
                token = auth_header.split(" ")[1]
                # In real implementation, parse JWT and extract user_id
                # For demo, we'll use a mock user ID
                if "user" in token:
                    return f"user:{token[-10:]}"
            except:
                pass
        
        # Fallback to IP address
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host}"
    
    def _get_endpoint(self, request: Request) -> str:
        """Request से endpoint extract करता है"""
        
        path = request.url.path
        method = request.method
        
        # Map specific endpoints to rate limit categories
        endpoint_map = {
            "/auth/login": "auth_login",
            "/auth/register": "auth_register",
            "/payment/initiate": "payment_initiate",
            "/search": "search_query"
        }
        
        return endpoint_map.get(path, "api_general")
    
    def _get_user_tier(self, request: Request) -> str:
        """User tier extract करता है token से"""
        
        auth_header = request.headers.get("authorization")
        if auth_header:
            try:
                token = auth_header.split(" ")[1]
                # Parse JWT and extract user tier
                # Simplified version
                if "premium" in token:
                    return "premium_user"
                elif "enterprise" in token:
                    return "enterprise_user"
            except:
                pass
        
        return "free_user"

# FastAPI app with rate limiting
app = FastAPI(title="Rate Limited API")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Rate limiter
rate_limiter = DistributedRateLimiter(redis_client)
circuit_breaker = CircuitBreaker(redis_client)

# Add middleware
app.add_middleware(RateLimitMiddleware, rate_limiter=rate_limiter)

@app.get("/auth/login")
async def login(request: Request):
    """Login endpoint with strict rate limiting"""
    
    # Simulate login logic
    await asyncio.sleep(0.1)  # Simulate processing
    
    return {
        "message": "Login successful",
        "token": "mock_jwt_token_user_premium",
        "expires_in": 3600
    }

@app.post("/payment/initiate")
async def initiate_payment(request: Request):
    """Payment endpoint with burst protection"""
    
    async def payment_logic():
        # Simulate payment processing
        await asyncio.sleep(0.2)
        return {"payment_id": "pay_12345", "status": "initiated"}
    
    # Use circuit breaker for payment API
    return await circuit_breaker.call_api("payment_api", payment_logic)

@app.get("/search")
async def search(request: Request, q: str):
    """Search endpoint with leaky bucket rate limiting"""
    
    # Simulate search
    await asyncio.sleep(0.05)
    
    return {
        "query": q,
        "results": [f"Result {i} for {q}" for i in range(1, 6)]
    }

@app.get("/rate-limit/stats/{identifier}")
async def get_rate_limit_stats(identifier: str, endpoint: str = "api_general"):
    """Rate limit statistics - Admin endpoint"""
    
    stats = await rate_limiter.get_rate_limit_stats(identifier, endpoint)
    return stats

@app.delete("/rate-limit/reset/{identifier}")
async def reset_rate_limit(identifier: str, endpoint: str = "api_general"):
    """Reset rate limit - Admin endpoint"""
    
    success = await rate_limiter.reset_rate_limit(identifier, endpoint)
    return {"reset": success}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except:
        return {"status": "unhealthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    
    print("🚦 Advanced API Rate Limiting System")
    print("📱 Zomato/Swiggy level traffic protection")
    print("⚡ Multiple algorithms: Token Bucket, Sliding Window, Fixed Window, Leaky Bucket")
    print("🔄 Circuit Breaker integration")
    print("📊 Real-time monitoring और analytics")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)

"""
Production Deployment Notes:
============================

1. Redis Configuration:
   - Use Redis Cluster for high availability
   - Set appropriate memory limits
   - Configure persistence for rate limit data
   - Monitor Redis performance

2. Rate Limit Tuning:
   - Monitor API usage patterns
   - Adjust limits based on user behavior
   - Implement gradual limit increases
   - A/B test different algorithms

3. Monitoring और Alerting:
   - Rate limit breach alerts
   - Redis connectivity monitoring
   - Performance metrics tracking
   - User experience impact analysis

4. Advanced Features:
   - Geolocation-based limits
   - Time-of-day rate adjustments
   - Machine learning based dynamic limits
   - Integration with CDN rate limiting

यह system Zomato/Swiggy level की high traffic handle कर सकता है!
"""