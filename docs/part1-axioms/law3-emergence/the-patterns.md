# The Patterns: Six Horsemen of the Emergent Apocalypse

!!! danger "These patterns killed companies worth billions"
    Knight Capital: 45 minutes → bankruptcy. Facebook: 6 hours → darkness. Learn these patterns or join the graveyard.

## Pattern Recognition Quick Reference

```
THE EMERGENCE BESTIARY
═════════════════════

Pattern         Trigger              Signature           Time to Death
───────         ───────              ─────────           ─────────────
Retry Storm     One timeout          Exponential load    5-10 minutes
Thundering Herd Cache expiry         Instant spike       30 seconds
Death Spiral    Memory pressure      GC dominates CPU    10-20 minutes
Synchronization Random delays align  Lock-step behavior  15-30 minutes
Cascade         One service fails    Dominoes fall       5-15 minutes
Metastable      Hidden state + load  Works until it doesn't  Instant
```

## Pattern 1: The Retry Storm

!!! example "Anatomy of Exponential Destruction - GitHub 2018 Outage"
    ```
    Initial State: 1,000 req/s, 10ms latency, life is good
    
    00:00 - Small database hiccup
            └─ 100 requests timeout (1s timeout)
    
    00:01 - Clients retry 3x each
            └─ Load: 1,000 + 300 = 1,300 req/s
            └─ Latency increases to 100ms
    
    00:02 - More timeouts trigger
            └─ 500 requests timeout
            └─ Retries: 500 × 3 = 1,500
            └─ Load: 1,000 + 1,500 = 2,500 req/s
    
    00:03 - System overwhelmed
            └─ ALL requests timing out
            └─ Retries: 2,500 × 3 = 7,500
            └─ Load: 1,000 + 7,500 = 8,500 req/s
    
    00:04 - COMPLETE MELTDOWN
            └─ Database connections exhausted
            └─ Health checks failing
            └─ Cascade to all services
    
    THE MATHEMATICAL HORROR:
    Load(t) = BaseLoad × 3^(t/timeout_period)
    
    At t=5 timeouts: 1,000 × 3^5 = 243,000 req/s
    Your database designed for: 10,000 req/s
    Result: TOTAL ANNIHILATION
    ```
    
    **Pattern Signature in Metrics:**
    ```
                    Retry Storm Active
                           │
        Load ──────────────│╱╱╱╱╱╱╱╱╱╱╱
                          ╱│
                        ╱  │
        ──────────────╱────│──────────► Time
                     ╱     │
        Latency ───╱───────│──────────►
                  ╱        │
        Errors ─╱──────────│──────────►
    ```

## Pattern 2: The Thundering Herd

!!! info "When Cache Becomes Curse - The Facebook \"Like\" Disaster"
    ```
    Popular post cache expires:
    ├─ Cristiano Ronaldo scores
    ├─ 100M fans refresh
    ├─ Cache miss on same key
    └─ 100M queries hit DB
    
    Timeline of Destruction:
    ───────────────────────
    T+0ms:    Cache expires
    T+1ms:    First user queries
    T+2ms:    1,000 users query
    T+5ms:    10,000 users query
    T+10ms:   1M users querying
    T+50ms:   DB connections exhausted
    T+100ms:  DB unresponsive
    T+500ms:  Cascading failures
    T+1000ms: Site down globally
    
    THE PHYSICS:
    Normal:   Cache Hit → 0.1ms response
    Stampede: DB Query → 100ms response × 100M users
              = 10M seconds of DB time needed
              = 115 DAYS of work in 1 second
    
    ACTUAL FIX THAT SAVED FACEBOOK:
    if (cache_miss) {
        if (already_computing(key)) {
            wait_for_result(key);  // Coalesce!
        } else {
            mark_computing(key);
            result = expensive_query();
            cache_set(key, result);
        }
    }
    ```

## Pattern 3: The Death Spiral

!!! tip "When Garbage Collection Becomes the Application"
    === "Healthy State"
        ```
        GC runs: ████ 2% of time
        App runs: ████████████████████ 98% of time
        ```
    
    === "Pressure Building"
        ```
        GC runs: ████████ 10% of time
        App runs: ████████████████ 90% of time
        First signs of trouble...
        ```
    
    === "Entering Spiral"
        ```
        GC runs: ████████████████ 40% of time
        App runs: ████████████ 60% of time
        Less time to process = More objects created
        ```
    
    === "Point of No Return"
        ```
        GC runs: ████████████████████████ 80% of time
        App runs: ████ 20% of time
        Spending more time cleaning than working!
        ```
    
    === "Death"
        ```
        GC runs: ████████████████████████████ 99% of time
        App runs: ▄ 1% of time
        OutOfMemoryError in 3... 2... 1...
        ```
    
    **Break the Spiral:**
    
    1. Increase heap (temporary fix)
    2. Reduce allocation rate (real fix)
    3. Circuit break at 50% GC time
    4. Shed load before spiral starts

## Pattern 4: Service Synchronization

!!! note "When Independent Services Start Dancing Together"
    | Time | Service Correlation Matrix | Status |
    |------|---------------------------|--------|
    | **Minute 0** | A:[1.0, 0.1, 0.1, 0.1, 0.1]<br/>B:[0.1, 1.0, 0.1, 0.2, 0.1]<br/>C:[0.1, 0.1, 1.0, 0.1, 0.2]<br/>D:[0.1, 0.2, 0.1, 1.0, 0.1]<br/>E:[0.1, 0.1, 0.2, 0.1, 1.0] | Correlation < 0.3<br/>Everything normal<br/>Random behavior |
    | **Minute 5** | A:[1.0, 0.2, 0.3, 0.1, 0.2]<br/>B:[0.2, 1.0, 0.6, 0.5, 0.3]<br/>C:[0.3, 0.6, 1.0, 0.6, 0.4]<br/>D:[0.1, 0.5, 0.6, 1.0, 0.3]<br/>E:[0.2, 0.3, 0.4, 0.3, 1.0] | B-C correlation growing<br/>Something's coupling them<br/>Feedback loop forming |
    | **Minute 10** | A:[1.0, 0.9, 0.9, 0.9, 0.9]<br/>B:[0.9, 1.0, 0.95, 0.98, 0.92]<br/>C:[0.9, 0.95, 1.0, 0.97, 0.94]<br/>D:[0.9, 0.98, 0.97, 1.0, 0.93]<br/>E:[0.9, 0.92, 0.94, 0.93, 1.0] | **CORRELATION > 0.9!**<br/>All services in lockstep<br/>Moving as one entity<br/>Resonance achieved<br/>**SYSTEM-WIDE FAILURE** |
    
    **How it happens:**
    
    1. Shared resource (DB, queue, cache)
    2. Similar timeout/retry configs
    3. Load balancer round-robin
    4. Services start "beating" together
    5. Constructive interference
    6. BOOM - Resonance cascade
    
    **Real Fix from Netflix:**
    ```python
    # Add jitter to break synchronization
    def make_request():
        jitter = random.uniform(0, 100)  # ms
        time.sleep(jitter / 1000)
        return actual_request()
    ```

## Pattern 5: The Cascade Failure

!!! failure "One Service to Kill Them All - AWS Kinesis Outage 2020"
    ```mermaid
    graph TD
        K[Kinesis] --> CW[CloudWatch]
        K --> C[Cognito]
        CW --> AS[AutoScaling]
        CW --> A[Alarms]
        CW --> L[Lambda]
        C --> UL[All User Logins]
        K --> S3[S3 Events]
        
        style K fill:#ff6b6b,stroke:#ff4757
        style CW fill:#ff9ff3,stroke:#ee5a6f
        style C fill:#ff9ff3,stroke:#ee5a6f
    ```
    
    **The Innocent Start:**
    Kinesis has a small capacity issue...
    
    **Services That Died:**
    - Kinesis (root cause)
    - CloudWatch (depends on Kinesis)
    - AutoScaling (needs CloudWatch)
    - Lambda (needs CloudWatch)
    - Cognito (uses Kinesis)
    - S3 Events (needs Kinesis)
    - ... 47 other services
    
    **TIME TO TOTAL FAILURE: 11 minutes**
    
    **The Terrifying Realization:**
    "Kinesis is just for streaming data" BUT it's in EVERY monitoring path!
    
    **Cascade Prevention Pattern:**
    ```
    BULKHEAD YOUR DEPENDENCIES
    ═════════════════════════
    
    Instead of:  A → B → C → D → E
                 (one failure kills all)
    
    Build:       A → B     C → D
                     ↓     ↓
                     E1    E2
                 (isolated failure domains)
    ```

## Pattern 6: Metastable Failure

!!! abstract "The Hidden State Bomb"
    **Your system has TWO stable states:**
    
    | State | Load | Cache | Queues | Response |
    |-------|------|-------|--------|----------|
    | **Happy Mode** | 80% | Warm | Flowing | 50ms |
    | **Death Mode** | 60% (LOWER!) | Cold | Backed up | TIMEOUT |
    
    **THE TERRIFYING PART:**
    At 60% load, BOTH states are stable! Tiny trigger flips between them.
    
    === "Real Example - Slack 2021"
        ```
        Running fine at 75% load
        ↓
        Brief network blip (100ms)
        ↓
        Caches miss a few updates
        ↓
        Cold cache increases load
        ↓
        System enters Death Mode
        ↓
        Reduce load to 40%... STILL BROKEN
        ↓
        Death Mode is stable at 40%!
        ↓
        Must restart everything to escape
        ```
    
    === "The Physics"
        This is a "bistable system" with hysteresis
        Like magnetic materials that stay magnetized
        Your system gets "stuck" in bad state
    
    === "Escape Pattern"
        ```python
        if (in_death_mode()):
            # Load reduction won't help!
            # Must "shock" system out
            
            # 1. Prewarm all caches
            # 2. Drain all queues  
            # 3. Reset all state
            # 4. Gradually reintroduce load
        ```
    
    **Metastable Detection:**
    ```python
    def detect_metastable_state():
        current_load = get_load()
        current_latency = get_latency()
        
        if current_load < 0.7 and current_latency > 1000:
            alert("METASTABLE FAILURE DETECTED!")
            alert("System stuck in death state")
            alert("Load reduction won't help")
            alert("Full state reset required")
    ```

## Pattern Combinations: The Perfect Storm

!!! danger "When Multiple Patterns Combine - GitHub Mega-Outage 2023"
    ```mermaid
    graph TD
        A[Database replica lag] -->|Triggers| B[Pattern 1: RETRY STORM]
        B -->|Causes| C[Pattern 2: SYNCHRONIZATION]
        C -->|Leads to| D[Pattern 3: CASCADE FAILURE]
        D -->|Creates| E[Pattern 4: DEATH SPIRAL]
        E -->|Triggers| F[Pattern 5: THUNDERING HERD]
        F -->|Results in| G[Pattern 6: METASTABLE LOCK]
        
        style G fill:#ff6b6b,stroke:#ff4757,stroke-width:3px
    ```
    
    **Impact:**
    - TOTAL OUTAGE TIME: 9 hours
    - PATTERNS ACTIVE: All 6
    - DAMAGE: $10M+ in SLA credits

## Your Pattern Survival Guide

!!! tip "Pattern-Specific Defenses"
    | Pattern | Early Signal | Defense |
    |---------|--------------|---------|
    | **Retry Storm** | Retry rate > 5% | Circuit breakers<br/>Exponential backoff<br/>Retry budgets |
    | **Thundering Herd** | Cache miss spike | Request coalescing<br/>Probabilistic refresh<br/>Cache warming |
    | **Death Spiral** | GC time > 20% | Memory circuit breaker<br/>Allocation budgets<br/>Preemptive restarts |
    | **Synchronization** | Correlation > 0.7 | Add jitter everywhere<br/>Randomize timers<br/>Desync protocols |
    | **Cascade** | Error in shared svc | Cellular architecture<br/>Dependency limits<br/>Graceful degradation |
    | **Metastable** | Low load, high latency | State reset protocols<br/>Cache prewarming<br/>Bistable detection |

!!! warning "The Meta-Truth About Patterns"
    These patterns aren't bugs. They're emergent properties of complex systems. You can't eliminate them—only prepare for them.

**Next**: [The Solutions](../the-solutions/) - Weapons to fight these monsters →