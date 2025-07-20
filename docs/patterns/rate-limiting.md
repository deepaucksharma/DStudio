# Rate Limiting Pattern

**Controlling request flow to protect system resources**

> *"Speed limits exist not to slow you down, but to keep everyone safe."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 2: Capacity](/part1-axioms/axiom2-capacity/) - Enforcing resource limits
- [Axiom 7: Human Interface](/part1-axioms/axiom7-human-interface/) - Preventing abuse

**🔧 Solves These Problems**:
- API abuse and DDoS protection
- Fair resource allocation among users
- Cost control in pay-per-use systems
- Preventing system overload

**🤝 Works Best With**:
- [Load Shedding](/patterns/load-shedding/) - Complementary overload protection
- [Circuit Breaker](/patterns/circuit-breaker/) - Failure handling
- [Quota Management](/patterns/quota/) - Long-term limits
</div>

---

## 🎯 Level 1: Intuition

### The Highway Speed Limit Analogy

Rate limiting is like highway speed limits:
- **Safety**: Prevents accidents from excessive speed
- **Fairness**: Everyone follows the same rules
- **Flow**: Optimizes overall traffic flow
- **Enforcement**: Automatic speed cameras (rate limiters)

### Basic Rate Limiter

```python
import time
from collections import defaultdict

class SimpleRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, user_id: str) -> bool:
        """Check if request is allowed for user"""
        now = time.time()
        
        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check limit
        if len(self.requests[user_id]) < self.max_requests:
            self.requests[user_id].append(now)
            return True
        
        return False

# Usage
limiter = SimpleRateLimiter(max_requests=100, window_seconds=60)

def handle_request(user_id: str):
    if not limiter.is_allowed(user_id):
        return {"error": "Rate limit exceeded"}, 429
    
    # Process request
    return {"result": "success"}, 200
```

---

## 🏗️ Level 2: Foundation

### Rate Limiting Algorithms

| Algorithm | Description | Pros | Cons |
|-----------|-------------|------|------|
| **Fixed Window** | Count in fixed time windows | Simple, low memory | Burst at window boundaries |
| **Sliding Window** | Rolling time window | Smooth rate limiting | Higher memory usage |
| **Token Bucket** | Tokens consumed per request | Allows bursts | Complex to tune |
| **Leaky Bucket** | Fixed output rate | Smooth traffic | No burst handling |

### Implementing Core Algorithms

```python
import time
import threading
from abc import ABC, abstractmethod

class RateLimiter(ABC):
    @abstractmethod
    def allow_request(self, key: str, tokens: int = 1) -> bool:
        pass

class TokenBucket(RateLimiter):
    """Token bucket algorithm implementation"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.buckets = {}
        self.lock = threading.Lock()
    
    def allow_request(self, key: str, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            
            if key not in self.buckets:
                self.buckets[key] = {
                    'tokens': self.capacity,
                    'last_refill': now
                }
            
            bucket = self.buckets[key]
            
            # Refill tokens
            time_passed = now - bucket['last_refill']
            new_tokens = time_passed * self.refill_rate
            bucket['tokens'] = min(
                self.capacity,
                bucket['tokens'] + new_tokens
            )
            bucket['last_refill'] = now
            
            # Check if enough tokens
            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True
            
            return False

class SlidingWindowLog(RateLimiter):
    """Sliding window log algorithm"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def allow_request(self, key: str, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            cutoff = now - self.window_seconds
            
            # Remove old entries
            self.requests[key] = [
                timestamp for timestamp in self.requests[key]
                if timestamp > cutoff
            ]
            
            # Check if we can add new request
            if len(self.requests[key]) + tokens <= self.max_requests:
                for _ in range(tokens):
                    self.requests[key].append(now)
                return True
            
            return False

class SlidingWindowCounter(RateLimiter):
    """Sliding window counter - hybrid approach"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.windows = defaultdict(lambda: {'current': 0, 'previous': 0})
        self.lock = threading.Lock()
    
    def allow_request(self, key: str, tokens: int = 1) -> bool:
        with self.lock:
            now = time.time()
            current_window = int(now / self.window_seconds)
            
            window_data = self.windows[key]
            
            # Reset if we're in a new window
            if current_window != window_data.get('window_id', 0):
                window_data['previous'] = window_data.get('current', 0)
                window_data['current'] = 0
                window_data['window_id'] = current_window
            
            # Calculate weighted count
            window_position = (now % self.window_seconds) / self.window_seconds
            weighted_count = (
                window_data['current'] +
                window_data['previous'] * (1 - window_position)
            )
            
            if weighted_count + tokens <= self.max_requests:
                window_data['current'] += tokens
                return True
            
            return False
```

---

## 🔧 Level 3: Deep Dive

### Distributed Rate Limiting

```python
import redis
import time
from typing import Optional, Tuple

class DistributedRateLimiter:
    """Redis-based distributed rate limiter"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
        # Lua script for atomic token bucket
        self.token_bucket_script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('HGETALL', key)
        local tokens = capacity
        local last_refill = now
        
        if #bucket > 0 then
            tokens = tonumber(bucket[2])
            last_refill = tonumber(bucket[4])
            
            -- Refill tokens
            local time_passed = now - last_refill
            local new_tokens = time_passed * refill_rate
            tokens = math.min(capacity, tokens + new_tokens)
        end
        
        if tokens >= requested then
            tokens = tokens - requested
            redis.call('HSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)  -- 1 hour TTL
            return {1, tokens}
        else
            redis.call('HSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 3600)
            return {0, tokens}
        end
        """
        
        self.script_sha = self.redis.script_load(self.token_bucket_script)
    
    def check_rate_limit(self, 
                        key: str,
                        capacity: int,
                        refill_rate: float,
                        requested: int = 1) -> Tuple[bool, float]:
        """Check if request is allowed"""
        try:
            result = self.redis.evalsha(
                self.script_sha,
                1,  # number of keys
                key,
                capacity,
                refill_rate,
                requested,
                time.time()
            )
            
            allowed = bool(result[0])
            remaining_tokens = float(result[1])
            
            return allowed, remaining_tokens
            
        except redis.RedisError as e:
            # Fallback to local decision or fail open/closed
            print(f"Redis error: {e}")
            return True, 0  # Fail open in this example

class HierarchicalRateLimiter:
    """Multi-level rate limiting (user, API key, IP)"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.limiters = {}
        
        # Define hierarchy
        self.limits = {
            'ip': {'capacity': 1000, 'window': 3600},  # Per hour
            'user': {'capacity': 10000, 'window': 3600},
            'api_key': {'capacity': 100000, 'window': 3600},
            'global': {'capacity': 1000000, 'window': 3600}
        }
    
    def check_all_limits(self, 
                        ip: str,
                        user_id: Optional[str] = None,
                        api_key: Optional[str] = None) -> Tuple[bool, str]:
        """Check all applicable rate limits"""
        
        # Check in order of granularity
        checks = [
            ('ip', f"ip:{ip}"),
            ('user', f"user:{user_id}") if user_id else None,
            ('api_key', f"api:{api_key}") if api_key else None,
            ('global', "global")
        ]
        
        for limit_type, key in filter(lambda x: x[1], checks):
            limit = self.limits[limit_type]
            
            # Use sliding window counter
            current = self.redis.incr(key)
            
            if current == 1:
                # First request, set expiry
                self.redis.expire(key, limit['window'])
            
            if current > limit['capacity']:
                return False, f"{limit_type} rate limit exceeded"
        
        return True, "OK"
```

### Advanced Rate Limiting Patterns

```python
class AdaptiveRateLimiter:
    """Rate limiter that adapts based on system load"""
    
    def __init__(self, base_rate: int):
        self.base_rate = base_rate
        self.current_multiplier = 1.0
        self.load_monitor = SystemLoadMonitor()
    
    def get_current_limit(self) -> int:
        """Calculate current rate limit based on system load"""
        system_load = self.load_monitor.get_load()
        
        if system_load < 0.5:
            # Low load, allow more
            self.current_multiplier = min(2.0, self.current_multiplier * 1.1)
        elif system_load > 0.8:
            # High load, restrict more
            self.current_multiplier = max(0.1, self.current_multiplier * 0.9)
        else:
            # Normal load, slowly return to baseline
            self.current_multiplier = 0.95 * self.current_multiplier + 0.05 * 1.0
        
        return int(self.base_rate * self.current_multiplier)

class CostBasedRateLimiter:
    """Rate limit based on operation cost"""
    
    def __init__(self, cost_budget_per_minute: int):
        self.budget = cost_budget_per_minute
        self.costs = {
            'read': 1,
            'write': 10,
            'search': 5,
            'analytics': 50
        }
        self.usage = defaultdict(lambda: {'cost': 0, 'reset_time': 0})
    
    def check_budget(self, user_id: str, operation: str) -> Tuple[bool, int]:
        """Check if user has budget for operation"""
        now = time.time()
        cost = self.costs.get(operation, 10)
        
        user_usage = self.usage[user_id]
        
        # Reset if minute has passed
        if now - user_usage['reset_time'] > 60:
            user_usage['cost'] = 0
            user_usage['reset_time'] = now
        
        # Check budget
        if user_usage['cost'] + cost <= self.budget:
            user_usage['cost'] += cost
            remaining = self.budget - user_usage['cost']
            return True, remaining
        
        return False, 0
```

---

## 🚀 Level 4: Expert

### Production Rate Limiting Systems

#### Stripe's Rate Limiting Strategy
```python
class StripeRateLimiter:
    """
    Stripe's approach to API rate limiting
    """
    
    def __init__(self):
        self.limits = {
            'default': {
                'requests_per_second': 100,
                'burst_multiplier': 2
            },
            'search': {
                'requests_per_second': 20,
                'burst_multiplier': 1.5
            },
            'webhooks': {
                'requests_per_second': 400,
                'burst_multiplier': 1.2
            }
        }
    
    def get_rate_limit_headers(self, 
                              endpoint_type: str,
                              remaining: int,
                              reset_time: int) -> dict:
        """Generate standard rate limit headers"""
        limit = self.limits[endpoint_type]['requests_per_second']
        
        return {
            'X-RateLimit-Limit': str(limit),
            'X-RateLimit-Remaining': str(remaining),
            'X-RateLimit-Reset': str(reset_time),
            'Retry-After': str(max(0, reset_time - int(time.time())))
        }
    
    def handle_rate_limited_request(self, request_type: str) -> dict:
        """Return rate limit error with helpful information"""
        return {
            'error': {
                'type': 'rate_limit_error',
                'message': 'Too many requests',
                'code': 'rate_limit_exceeded',
                'doc_url': 'https://stripe.com/docs/rate-limits',
                'request_id': generate_request_id(),
                'idempotency_key': request.headers.get('Idempotency-Key')
            }
        }, 429

class CloudflareRateLimiter:
    """
    Cloudflare's advanced rate limiting
    """
    
    def __init__(self):
        self.rules = []
    
    def add_rule(self, 
                 path_pattern: str,
                 threshold: int,
                 period: int,
                 action: str,
                 characteristics: List[str]):
        """Add rate limiting rule"""
        self.rules.append({
            'path': path_pattern,
            'threshold': threshold,
            'period': period,
            'action': action,  # 'block', 'challenge', 'log'
            'characteristics': characteristics  # ['ip', 'user_agent', 'api_key']
        })
    
    def evaluate_request(self, request) -> Optional[str]:
        """Evaluate request against all rules"""
        for rule in self.rules:
            if self.matches_pattern(request.path, rule['path']):
                key = self.build_key(request, rule['characteristics'])
                
                if self.exceeds_threshold(key, rule):
                    return rule['action']
        
        return None
    
    def build_key(self, request, characteristics: List[str]) -> str:
        """Build rate limit key from request characteristics"""
        parts = []
        
        for char in characteristics:
            if char == 'ip':
                parts.append(request.remote_addr)
            elif char == 'user_agent':
                parts.append(hashlib.md5(
                    request.headers.get('User-Agent', '').encode()
                ).hexdigest()[:8])
            elif char == 'api_key':
                parts.append(request.headers.get('X-API-Key', 'anonymous'))
            elif char == 'jwt_sub':
                # Extract subject from JWT
                token = request.headers.get('Authorization', '').split(' ')[-1]
                sub = self.extract_jwt_subject(token)
                parts.append(sub)
        
        return ':'.join(parts)
```

### Real-World Case Study: GitHub's Rate Limiting

```python
class GitHubRateLimiter:
    """
    GitHub's sophisticated rate limiting system
    """
    
    def __init__(self):
        self.limits = {
            'core': {
                'unauthenticated': 60,      # per hour
                'authenticated': 5000,       # per hour
                'oauth_app': 5000,          # per hour per user
                'github_app': 5000          # per hour per installation
            },
            'search': {
                'unauthenticated': 10,      # per minute
                'authenticated': 30         # per minute
            },
            'graphql': {
                'node_limit': 500000,       # per hour
                'complexity_limit': 5000    # per query
            }
        }
    
    def calculate_graphql_complexity(self, query: str) -> int:
        """
        Calculate GraphQL query complexity
        """
        # Simplified complexity calculation
        complexity = 0
        
        # Count nodes requested
        node_count = query.count('{')
        complexity += node_count
        
        # Penalize pagination
        if 'first:' in query or 'last:' in query:
            import re
            matches = re.findall(r'(?:first|last):\s*(\d+)', query)
            for match in matches:
                complexity += int(match) * 0.1
        
        # Penalize deep nesting
        max_depth = self.calculate_query_depth(query)
        complexity += max_depth ** 2
        
        return int(complexity)
    
    def check_graphql_limits(self, 
                            user_id: str,
                            query: str) -> Tuple[bool, dict]:
        """Check GraphQL-specific limits"""
        complexity = self.calculate_graphql_complexity(query)
        
        # Check complexity limit
        if complexity > self.limits['graphql']['complexity_limit']:
            return False, {
                'message': 'Query complexity exceeds limit',
                'complexity': complexity,
                'limit': self.limits['graphql']['complexity_limit']
            }
        
        # Check node limit
        nodes_used = self.get_user_node_usage(user_id)
        nodes_requested = self.estimate_nodes_from_query(query)
        
        if nodes_used + nodes_requested > self.limits['graphql']['node_limit']:
            return False, {
                'message': 'Node limit exceeded',
                'used': nodes_used,
                'requested': nodes_requested,
                'limit': self.limits['graphql']['node_limit']
            }
        
        return True, {'complexity': complexity, 'nodes': nodes_requested}
    
    def get_reset_time(self, limit_type: str) -> int:
        """Calculate when rate limit resets"""
        now = int(time.time())
        
        if limit_type in ['core', 'graphql']:
            # Hourly reset
            return now + (3600 - now % 3600)
        elif limit_type == 'search':
            # Minute reset
            return now + (60 - now % 60)
        
        return now + 3600
```

---

## 🎯 Level 5: Mastery

### Theoretical Optimal Rate Limiting

```python
import numpy as np
from scipy.stats import poisson

class OptimalRateLimiter:
    """
    Mathematically optimal rate limiting
    """
    
    def __init__(self):
        self.request_history = []
        self.service_capacity = None
        
    def calculate_optimal_rate(self,
                             service_time_distribution: dict,
                             target_latency_percentile: float = 0.95,
                             target_latency_ms: float = 100) -> float:
        """
        Calculate optimal rate using queueing theory
        """
        # Use M/G/1 queue model
        mean_service_time = service_time_distribution['mean']
        var_service_time = service_time_distribution['variance']
        
        # Calculate maximum arrival rate for target latency
        # Using Pollaczek-Khinchine formula
        c_squared = var_service_time / (mean_service_time ** 2)
        
        # Binary search for optimal rate
        low, high = 0, 1 / mean_service_time
        
        while high - low > 0.001:
            rate = (low + high) / 2
            rho = rate * mean_service_time  # Utilization
            
            if rho >= 1:
                high = rate
                continue
            
            # Expected wait time in queue
            W_q = (rho ** 2 * (1 + c_squared)) / (2 * (1 - rho) * rate)
            
            # Total response time
            W = W_q + mean_service_time
            
            # Check if meets latency target
            # Using approximation for percentile
            latency_percentile = W * (-np.log(1 - target_latency_percentile))
            
            if latency_percentile * 1000 <= target_latency_ms:
                low = rate
            else:
                high = rate
        
        return rate
    
    def dynamic_fair_queuing(self, 
                           users: List[str],
                           weights: Dict[str, float]) -> Dict[str, float]:
        """
        Implement weighted fair queuing for rate limits
        """
        total_capacity = self.service_capacity
        total_weight = sum(weights.values())
        
        # Base allocation
        allocations = {}
        for user in users:
            weight = weights.get(user, 1.0)
            allocations[user] = (weight / total_weight) * total_capacity
        
        # Adjust for actual usage patterns
        usage_efficiency = self.calculate_usage_efficiency(users)
        
        # Redistribute unused capacity
        unused_capacity = 0
        efficient_users = []
        
        for user, allocation in allocations.items():
            efficiency = usage_efficiency.get(user, 1.0)
            
            if efficiency < 0.8:  # User not fully utilizing allocation
                unused = allocation * (1 - efficiency)
                unused_capacity += unused
                allocations[user] *= efficiency
            else:
                efficient_users.append(user)
        
        # Give unused capacity to efficient users
        if efficient_users and unused_capacity > 0:
            bonus_per_user = unused_capacity / len(efficient_users)
            for user in efficient_users:
                allocations[user] += bonus_per_user
        
        return allocations
```

### Future Directions

1. **ML-Based Rate Limiting**: Predict optimal limits using usage patterns
2. **Blockchain Rate Limiting**: Decentralized rate limit consensus
3. **Zero-Knowledge Rate Limiting**: Prove rate compliance without revealing identity
4. **Adaptive Fairness**: Real-time fairness adjustment based on system state

---

## 📋 Quick Reference

### Rate Limiting Strategy Selection

| Use Case | Algorithm | Key Parameters |
|----------|-----------|----------------|
| API Gateway | Token Bucket | 1000 req/min, burst 2x |
| User Actions | Sliding Window | 100 actions/hour |
| Search API | Fixed Window | 30 searches/min |
| Webhooks | Leaky Bucket | 10 req/sec steady |
| GraphQL | Complexity-based | 5000 points/query |

### Implementation Checklist

- [ ] Choose appropriate algorithm
- [ ] Define rate limit dimensions (user, IP, API key)
- [ ] Implement distributed coordination
- [ ] Add standard rate limit headers
- [ ] Create helpful error messages
- [ ] Monitor and adjust limits
- [ ] Document rate limits clearly

---

<div class="navigation-footer">
<div class="pattern-relationships">
<h3>🔗 Related Patterns & Concepts</h3>

**🤝 Complementary Patterns**:
- [Load Shedding](/patterns/load-shedding/) - Drop requests when overwhelmed
- [Circuit Breaker](/patterns/circuit-breaker/) - Fail fast on errors
- [Bulkhead](/patterns/bulkhead/) - Isolate resources

**🧠 Foundational Concepts**:
- [Axiom 2: Capacity](/part1-axioms/axiom2-capacity/) - Why limits exist
- [Control Pillar](/part2-pillars/control/) - System control theory
</div>
</div>

---

*"Rate limiting is not about saying no, it's about saying yes sustainably."*