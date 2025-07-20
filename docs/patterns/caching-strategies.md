---
title: Caching Strategies
description: "Optimize performance by storing frequently accessed data in fast storage layers"
type: pattern
difficulty: beginner
reading_time: 10 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Caching Strategies**

# Caching Strategies

**Remember to forget**

## THE PROBLEM

```
Every request hits the database:
- Database CPU: 90%
- Response time: 500ms
- Cost: $10,000/month
- Users: "Why is it so slow?"

But 80% of requests are for same data!
```bash
## THE SOLUTION

```
Cache frequently accessed data:

Request → Cache (fast) → Found? Return
            ↓
          Miss? → Database → Cache → Return

10ms vs 500ms = 50x faster
```bash
## Caching Patterns

```
1. CACHE-ASIDE (Lazy Loading)
   App manages cache explicitly

2. WRITE-THROUGH
   Write to cache + DB together

3. WRITE-BACK (Write-Behind)
   Write to cache, async to DB

4. REFRESH-AHEAD
   Proactively refresh before expiry
```bash
## IMPLEMENTATION

```python
# Cache-aside pattern
class CacheAsidePattern:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database

    async def get(self, key):
        """Read with cache-aside"""

        # 1. Check cache
        value = await self.cache.get(key)
        if value is not None:
            return value  # Cache hit

        # 2. Cache miss - fetch from DB
        value = await self.db.get(key)
        if value is None:
            return None

        # 3. Populate cache for next time
        await self.cache.set(key, value, ttl=300)  # 5 min TTL

        return value

    async def update(self, key, value):
        """Update with cache invalidation"""

        # 1. Update database
        await self.db.update(key, value)

        # 2. Invalidate cache
        await self.cache.delete(key)

        # Note: Next read will populate cache

# Write-through pattern
class WriteThroughPattern:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database

    async def write(self, key, value):
        """Write to cache and DB together"""

        # Start both writes concurrently
        cache_write = self.cache.set(key, value, ttl=300)
        db_write = self.db.write(key, value)

        # Wait for both to complete
        await asyncio.gather(cache_write, db_write)

    async def read(self, key):
        """Read from cache first"""

        # Try cache first
        value = await self.cache.get(key)
        if value is not None:
            return value

        # Fall back to DB (cache miss)
        value = await self.db.get(key)
        if value is not None:
            # Populate cache
            await self.cache.set(key, value, ttl=300)

        return value

# Write-back pattern (dangerous but fast)
class WriteBackPattern:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database
        self.write_queue = asyncio.Queue()
        self.start_background_writer()

    async def write(self, key, value):
        """Write to cache immediately, DB eventually"""

        # 1. Write to cache immediately
        await self.cache.set(key, value, ttl=3600)

        # 2. Queue for DB write
        await self.write_queue.put((key, value))

        # Return fast!

    def start_background_writer(self):
        """Background task to flush to DB"""
        asyncio.create_task(self._background_writer())

    async def _background_writer(self):
        batch = []

        while True:
            try:
                # Collect writes for batching
                key, value = await asyncio.wait_for(
                    self.write_queue.get(),
                    timeout=1.0
                )
                batch.append((key, value))

                # Flush when batch is full
                if len(batch) >= 100:
                    await self._flush_batch(batch)
                    batch = []

            except asyncio.TimeoutError:
                # Timeout - flush whatever we have
                if batch:
                    await self._flush_batch(batch)
                    batch = []

    async def _flush_batch(self, batch):
        """Write batch to database"""
        try:
            await self.db.write_batch(batch)
        except Exception as e:
            # Failed writes go to DLQ
            await self.handle_write_failure(batch, e)

# Refresh-ahead pattern
class RefreshAheadPattern:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database
        self.refresh_threshold = 0.8  # Refresh at 80% of TTL

    async def get(self, key):
        """Get with proactive refresh"""

        # Get from cache with metadata
        result = await self.cache.get_with_metadata(key)

        if result is None:
            # Cache miss
            value = await self.db.get(key)
            if value:
                await self.cache.set(key, value, ttl=300)
            return value

        value, metadata = result

        # Check if close to expiry
        age = time.time() - metadata['created_at']
        ttl_remaining = metadata['ttl'] - age

        if ttl_remaining < metadata['ttl'] * (1 - self.refresh_threshold):
            # Refresh in background
            asyncio.create_task(self._refresh_cache(key))

        return value

    async def _refresh_cache(self, key):
        """Background refresh"""
        try:
            fresh_value = await self.db.get(key)
            if fresh_value:
                await self.cache.set(key, fresh_value, ttl=300)
        except Exception:
            # Log but don't crash
            pass

# Multi-level caching
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = LocalMemoryCache(size_mb=100)      # Process memory
        self.l2_cache = RedisCache(size_gb=10)             # Redis
        self.l3_storage = Database()                        # Database

    async def get(self, key):
        """Try each level in order"""

        # L1: Local memory (microseconds)
        value = self.l1_cache.get(key)
        if value is not None:
            return value

        # L2: Redis (milliseconds)
        value = await self.l2_cache.get(key)
        if value is not None:
            # Populate L1
            self.l1_cache.set(key, value)
            return value

        # L3: Database (tens of milliseconds)
        value = await self.l3_storage.get(key)
        if value is not None:
            # Populate L2 and L1
            await self.l2_cache.set(key, value, ttl=3600)
            self.l1_cache.set(key, value)

        return value

# Cache warming
class CacheWarmer:
    def __init__(self, cache, database):
        self.cache = cache
        self.db = database

    async def warm_cache(self, keys=None):
        """Pre-populate cache with hot data"""

        if keys is None:
            # Get most accessed keys from analytics
            keys = await self.get_hot_keys()

        # Batch fetch from database
        batch_size = 100
        for i in range(0, len(keys), batch_size):
            batch_keys = keys[i:i + batch_size]

            # Fetch batch
            values = await self.db.multi_get(batch_keys)

            # Populate cache
            cache_ops = []
            for key, value in values.items():
                if value is not None:
                    cache_op = self.cache.set(key, value, ttl=3600)
                    cache_ops.append(cache_op)

            await asyncio.gather(*cache_ops)

            print(f"Warmed {len(cache_ops)} keys")

    async def get_hot_keys(self):
        """Identify frequently accessed keys"""
        # From analytics or access logs
        return await self.db.query("""
            SELECT key, COUNT(*) as access_count
            FROM access_logs
            WHERE timestamp > NOW() - INTERVAL '1 hour'
            GROUP BY key
            ORDER BY access_count DESC
            LIMIT 1000
        """)
```bash
## Advanced Caching Strategies

```python
# Probabilistic early expiration
class ProbabilisticExpiration:
    """Avoid thundering herd on expiry"""

    def __init__(self, cache):
        self.cache = cache
        self.beta = 1.0  # Tuning parameter

    async def get(self, key, compute_fn):
        result = await self.cache.get_with_metadata(key)

        if result is None:
            # Compute and cache
            value = await compute_fn()
            await self.cache.set(key, value, ttl=300)
            return value

        value, metadata = result
        age = time.time() - metadata['created_at']
        ttl = metadata['ttl']

        # Probabilistic early expiration
        # Higher probability as we approach TTL
        expiry_probability = age / ttl * self.beta

        if random.random() < expiry_probability:
            # Recompute early to avoid stampede
            asyncio.create_task(self._recompute(key, compute_fn))

        return value

# Adaptive TTL based on access patterns
class AdaptiveTTL:
    def __init__(self, cache):
        self.cache = cache
        self.access_history = defaultdict(list)

    async def set(self, key, value):
        """Set with adaptive TTL"""

        # Calculate TTL based on access pattern
        ttl = self.calculate_ttl(key)

        await self.cache.set(key, value, ttl=ttl)

    def calculate_ttl(self, key):
        """TTL based on access frequency"""

        history = self.access_history[key]

        if len(history) < 2:
            return 300  # Default 5 minutes

        # Calculate average time between accesses
        intervals = []
        for i in range(1, len(history)):
            interval = history[i] - history[i-1]
            intervals.append(interval)

        avg_interval = sum(intervals) / len(intervals)

        # TTL = 2x average interval (with bounds)
        ttl = max(60, min(3600, avg_interval * 2))

        return int(ttl)

# Cache stampede protection
class StampedeProtection:
    def __init__(self, cache, semaphore_limit=1):
        self.cache = cache
        self.locks = {}  # Per-key locks
        self.semaphore_limit = semaphore_limit

    async def get(self, key, compute_fn):
        """Get with stampede protection"""

        # Try cache first
        value = await self.cache.get(key)
        if value is not None:
            return value

        # Acquire lock for this key
        if key not in self.locks:
            self.locks[key] = asyncio.Semaphore(self.semaphore_limit)

        async with self.locks[key]:
            # Double-check (another thread might have populated)
            value = await self.cache.get(key)
            if value is not None:
                return value

            # We're the chosen one - compute value
            value = await compute_fn()
            await self.cache.set(key, value, ttl=300)

            return value
```

## ✓ CHOOSE THIS WHEN:
• Read-heavy workloads
• Expensive computations
• Slow database queries
• Static or slow-changing data
• Need to reduce latency

## ⚠️ BEWARE OF:
• Cache invalidation complexity
• Stale data problems
• Cache stampede/thundering herd
• Memory limits
• Cold start performance

## REAL EXAMPLES
• **Facebook**: TAO graph cache
• **Twitter**: Tweet timeline caching
• **Reddit**: Comment tree caching

---

**Previous**: [← Bulkhead Pattern](bulkhead.md) | **Next**: [Change Data Capture (CDC) →](cdc.md)
---

## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical

## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems

## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand

## 💻 Code Sample

### Basic Implementation

```python
class Caching_StrategiesPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"

    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)

        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)

    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold

    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass

    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}

    def _record_success(self):
        self.metrics.record_success()

    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = Caching_StrategiesPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
caching_strategies:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_caching_strategies_behavior():
    pattern = Caching_StrategiesPattern(test_config)

    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'

    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'

    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes
**Objective**: Identify Caching Strategies in existing systems

**Task**:
Find 2 real-world examples where Caching Strategies is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Caching Strategies

**Scenario**: You need to implement Caching Strategies for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Caching Strategies
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Caching Strategies

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Caching Strategies be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Caching Strategies later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Caching Strategies in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**:
- How would you introduce Caching Strategies to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
