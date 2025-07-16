Page 56: Sharding & Partitioning
Divide and conquer at scale
THE PROBLEM
Single database limits:
- Storage: Disk full
- CPU: Queries slow
- Memory: Can't cache
- Network: Bandwidth saturated
- Availability: Single point of failure
THE SOLUTION
Split data across multiple nodes:

Logical Database
    ↓
[Shard 1] [Shard 2] [Shard 3] [Shard N]
 User A-F  User G-M  User N-S  User T-Z
Sharding Strategies:
1. RANGE SHARDING
   Shard by ordered key range
   + Simple, range queries work
   - Hotspots possible

2. HASH SHARDING  
   Shard by hash(key) % N
   + Even distribution
   - Range queries don't work
   - Resharding painful

3. GEOGRAPHIC SHARDING
   Shard by location
   + Data locality
   - Cross-region queries

4. DIRECTORY SHARDING
   Lookup table for shard location
   + Flexible mapping
   - Extra hop, SPOF
PSEUDO CODE IMPLEMENTATION
ShardingRouter:
    shard_map = load_shard_configuration()
    
    get_shard(key):
        // Consistent hashing
        hash = hash_function(key)
        shard = find_shard_for_hash(hash)
        return shard
        
    query(sql, sharding_key):
        if sharding_key:
            // Single shard query
            shard = get_shard(sharding_key)
            return shard.execute(sql)
        else:
            // Scatter-gather
            return scatter_gather_query(sql)
            
    scatter_gather_query(sql):
        // Parallel query all shards
        futures = []
        for shard in all_shards:
            futures.append(
                async_query(shard, sql)
            )
            
        // Merge results
        results = wait_all(futures)
        return merge_results(results, sql.order_by)

ReshardingManager:
    add_shard(new_shard):
        // Online resharding
        
        // 1. Add new shard to ring
        shard_ring.add(new_shard)
        
        // 2. Calculate data to move
        migrations = calculate_migrations()
        
        // 3. Start dual writes
        for range in migrations:
            enable_dual_writes(range, new_shard)
            
        // 4. Copy historical data
        for range in migrations:
            copy_data_async(range, new_shard)
            verify_consistency(range)
            
        // 5. Cut over
        for range in migrations:
            atomic_cutover(range, new_shard)
            disable_dual_writes(range)

CrossShardTransaction:
    execute_transaction(operations):
        // 2PC across shards
        coordinator = TransactionCoordinator()
        
        // Prepare phase
        for op in operations:
            shard = get_shard(op.key)
            if not coordinator.prepare(shard, op):
                coordinator.abort_all()
                raise TransactionAborted()
                
        // Commit phase
        coordinator.commit_all()
Advanced Sharding Patterns:
1. VIRTUAL SHARDS
   // Decouple logical from physical
   1000 virtual shards → 10 physical nodes
   Easy rebalancing by moving virtual shards

2. HIERARCHICAL SHARDING
   // Multiple levels
   Region → Customer → Time
   US → CustomerA → 2024-01

3. DYNAMIC SHARDING
   // Auto-split when shard too large
   if shard.size > threshold:
       split_point = find_median_key()
       create_new_shard(split_point)Mapped out remaining pattern summaries using pseudo code.2sThe user asked me to continue with the remaining patterns (pages 50-64) using pseudo code summaries instead of full implementations. I'm currently on page 56 and need to continue through page 64. Let me continue with the same format - keeping the structure but using pseudo code summaries.✓ CHOOSE THIS WHEN:

Data doesn't fit on one machine
Need linear scalability
Clear sharding key exists
Queries are shard-local
Geographic distribution needed

⚠️ BEWARE OF:

Cross-shard queries expensive
Transactions across shards
Resharding complexity
Hot shard problems
Operational overhead

REAL EXAMPLES

Discord: Message sharding by channel
Uber: Geospatial sharding by city
Pinterest: User-based sharding
