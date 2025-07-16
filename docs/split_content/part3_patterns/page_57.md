Page 57: Caching Hierarchies
Memory is the new disk, disk is the new tape
THE PROBLEM
Database queries are expensive:
- Network round trip
- Query parsing/planning
- Disk I/O
- Lock contention
Repeat queries waste resources
THE SOLUTION
Multi-level cache hierarchy:

Browser → CDN → Load Balancer → App Cache → DB Cache → Database
  L1      L2         L3             L4          L5         L6
<1ms    <10ms      <20ms          <5ms        <10ms     <100ms
Cache Patterns:
1. CACHE-ASIDE (Lazy Loading)
   Read: Check cache → Miss? → Load from DB → Update cache
   Write: Update DB → Invalidate cache

2. WRITE-THROUGH
   Write: Update cache → Update DB (sync)
   Read: Always from cache

3. WRITE-BEHIND (Write-Back)
   Write: Update cache → Update DB (async)
   Risk: Data loss if cache fails

4. REFRESH-AHEAD
   Proactively refresh before expiration
   Good for predictable access
PSEUDO CODE IMPLEMENTATION
HierarchicalCache:
    levels = [L1_local, L2_redis, L3_cdn]
    
    get(key):
        // Check each level
        for level in levels:
            value = level.get(key)
            if value:
                // Promote to higher levels
                promote_to_upper_levels(key, value, level)
                return value
                
        // Not in any cache
        value = database.get(key)
        if value:
            populate_all_levels(key, value)
        return value
        
    set(key, value, ttl):
        // Write-through all levels
        for level in levels:
            level.set(key, value, ttl)
        database.set(key, value)
        
    invalidate(key):
        // Cascade invalidation
        for level in levels:
            level.delete(key)

CacheWarming:
    warm_cache_on_startup():
        // Prevent thundering herd
        hot_keys = identify_hot_keys()
        
        for batch in chunk(hot_keys, 100):
            parallel_load(batch)
            sleep(100ms)  // Rate limit
            
    predict_and_warm():
        // ML-based prediction
        predicted_keys = ml_model.predict_next_hour()
        for key in predicted_keys:
            if not cache.exists(key):
                async_warm(key)

TTLStrategy:
    calculate_ttl(key, access_pattern):
        base_ttl = 3600  // 1 hour default
        
        // Adjust based on patterns
        if access_pattern.is_frequent():
            ttl = base_ttl * 4
        elif access_pattern.is_periodic():
            ttl = align_to_period(access_pattern.period)
        elif access_pattern.is_rare():
            ttl = base_ttl / 4
            
        // Add jitter to prevent stampede
        jitter = random(-0.1, 0.1) * ttl
        return ttl + jitter

CacheInvalidation:
    // The hard problem
    strategies = {
        'TTL': Simple but may serve stale,
        'Event-based': DB triggers cache invalidation,
        'Tag-based': Invalidate groups of keys,
        'Version-based': Include version in key
    }
    
    tag_based_invalidation(tag):
        keys = cache_tag_index.get_keys(tag)
        for batch in chunk(keys, 1000):
            parallel_invalidate(batch)
Advanced Caching Strategies:
1. BLOOM FILTER NEGATIVE CACHE
   // Avoid repeated misses
   if bloom_filter.might_contain(key):
       check_cache_and_db()
   else:
       return null  // Definitely not there

2. TWO-TIER WITH DIFFERENT CONSISTENCY
   L1: Eventually consistent (fast)
   L2: Strong consistency (slower)
   
   critical_read(key):
       return L2.get(key)
   
   normal_read(key):
       return L1.get(key) || L2.get(key)

3. ADAPTIVE REPLACEMENT CACHE (ARC)
   // Self-tuning between recency and frequency
   maintain_two_lists(LRU, LFU)
   adapt_based_on_hit_rates()
✓ CHOOSE THIS WHEN:

Read >> Write workload
Data has temporal locality
Can tolerate stale data
Database load too high
Latency requirements strict

⚠️ BEWARE OF:

Cache invalidation complexity
Stale data issues
Cache stampede/thundering herd
Memory costs
Debugging cached behavior

REAL EXAMPLES

Facebook: TAO graph cache
Netflix: EVCache for streaming
Reddit: Multi-tier caching
