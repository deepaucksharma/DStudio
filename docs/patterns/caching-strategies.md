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
```

## THE SOLUTION

```
Cache frequently accessed data:

Request → Cache (fast) → Found? Return
            ↓
          Miss? → Database → Cache → Return
          
10ms vs 500ms = 50x faster
```

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
```

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
```

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