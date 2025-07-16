Page 55: Tunable Consistency
One size doesn't fit all
THE PROBLEM
Fixed consistency levels:
- Strong consistency for everything = slow
- Eventual consistency for everything = confusing
- No middle ground
- Can't optimize per operation
THE SOLUTION
Make consistency a dial, not a switch:

Operation Types:
- User profile read: Eventual (fast)
- Password check: Strong (secure)
- Shopping cart: Session (user's view)
- Analytics: Eventual (volume)
Consistency Levels Spectrum:
PER-OPERATION CHOICE:
Strong ←────────────────────→ Eventual
  │         │        │           │
ALL      QUORUM   LOCAL_ONE    ANY
nodes    majority  local DC    first

Write: W replicas must acknowledge
Read: R replicas must respond
W + R > N = Strong consistency
PSEUDO CODE IMPLEMENTATION
TunableDataStore:
    write(key, value, consistency_level):
        replicas = get_replicas(key)
        
        write_count = consistency_level.required_writes()
        write_timeout = consistency_level.timeout()
        
        // Parallel writes
        futures = []
        for replica in replicas:
            futures.append(
                async_write(replica, key, value)
            )
            
        // Wait for enough confirmations
        confirmed = wait_for_n(futures, write_count, write_timeout)
        
        if confirmed < write_count:
            raise InsufficientReplicas()
            
        // Continue async for remaining
        fire_and_forget(futures)
        
    read(key, consistency_level):
        replicas = get_replicas(key)
        read_count = consistency_level.required_reads()
        
        // Read from replicas
        responses = parallel_read(replicas, key, read_count)
        
        // Resolve conflicts
        if consistency_level.requires_quorum():
            value = resolve_conflicts(responses)
            
            // Read repair if mismatched
            if has_conflicts(responses):
                async_repair(replicas, key, value)
                
        return value

ConsistencyAdvisor:
    recommend_level(operation):
        // Analyze operation characteristics
        if operation.is_financial():
            return ConsistencyLevel.ALL
            
        if operation.is_authentication():
            return ConsistencyLevel.QUORUM
            
        if operation.affects_only_user():
            return ConsistencyLevel.LOCAL_QUORUM
            
        if operation.is_analytics():
            return ConsistencyLevel.ONE
            
        return ConsistencyLevel.QUORUM  // default

DynamicTuning:
    adjust_consistency_based_on_slo():
        if current_latency > slo_target:
            // Temporarily reduce consistency
            downgrade_consistency_level()
            alert_operators()
            
        if error_rate > threshold:
            // Increase consistency
            upgrade_consistency_level()
Tuning Strategies:
1. TIME-BASED
   // Strong during business hours
   if business_hours():
       level = QUORUM
   else:
       level = LOCAL_ONE

2. USER-BASED
   // Premium users get strong consistency
   if user.is_premium():
       level = STRONG
   else:
       level = EVENTUAL

3. OPERATION-BASED
   // Critical operations strong
   critical_ops = ['payment', 'login', 'order']
   if op_type in critical_ops:
       level = ALL
✓ CHOOSE THIS WHEN:

Mixed consistency requirements
Need to optimize cost/performance
Geographic distribution
SLA flexibility needed
Read/write patterns vary

⚠️ BEWARE OF:

Complexity for developers
Debugging consistency issues
Monitoring requirements
Documentation needs
Testing all combinations

REAL EXAMPLES

Cassandra: Per-query consistency
DynamoDB: Eventually/Strong reads
CosmosDB: 5 consistency levels
