# The Patterns: Six Horsemen of the Emergent Apocalypse 💀

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

## Pattern 1: The Retry Storm ⛈️

<div class="failure-vignette">
<h3>Anatomy of Exponential Destruction</h3>

```
MINUTE-BY-MINUTE: GITHUB 2018 OUTAGE
════════════════════════════════════

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
    Load ──────────────┼╱╱╱╱╱╱╱╱╱╱╱
                      ╱│
                    ╱  │
    ──────────────╱────┼──────────► Time
                 ╱     │
    Latency ───╱───────┼──────────►
              ╱        │
    Errors ─╱──────────┼──────────►
```
</div>

## Pattern 2: The Thundering Herd 🦬

<div class="axiom-box">
<h3>When Cache Becomes Curse</h3>

```
THE FACEBOOK "LIKE" DISASTER
════════════════════════════

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
</div>

## Pattern 3: The Death Spiral 🌀

<div class="decision-box">
<h3>When Garbage Collection Becomes the Application</h3>

```
JVM DEATH SPIRAL STAGES
═══════════════════════

HEALTHY STATE:
GC runs: ████ 2% of time
App runs: ████████████████████ 98% of time

PRESSURE BUILDING:
GC runs: ████████ 10% of time
App runs: ████████████████ 90% of time
First signs of trouble...

ENTERING SPIRAL:
GC runs: ████████████████ 40% of time
App runs: ████████████ 60% of time
Less time to process = More objects created

POINT OF NO RETURN:
GC runs: ████████████████████████ 80% of time
App runs: ████ 20% of time
Spending more time cleaning than working!

DEATH:
GC runs: ████████████████████████████ 99% of time
App runs: ▄ 1% of time
OutOfMemoryError in 3... 2... 1...

BREAK THE SPIRAL:
1. Increase heap (temporary fix)
2. Reduce allocation rate (real fix)
3. Circuit break at 50% GC time
4. Shed load before spiral starts
```
</div>

## Pattern 4: Service Synchronization 🔄

<div class="truth-box">
<h3>When Independent Services Start Dancing Together</h3>

```
THE SYNCHRONIZATION MATRIX
═════════════════════════

MINUTE 0: Services Independent
     A  B  C  D  E
A   [1 ][.1][.1][.1][.1]    Correlation < 0.3
B   [.1][1 ][.1][.2][.1]    Everything normal
C   [.1][.1][1 ][.1][.2]    Random behavior
D   [.1][.2][.1][1 ][.1]
E   [.1][.1][.2][.1][1 ]

MINUTE 5: Patterns Emerging
     A  B  C  D  E
A   [1 ][.2][.3][.1][.2]    B-C correlation growing
B   [.2][1 ][.6][.5][.3]    Something's coupling them
C   [.3][.6][1 ][.6][.4]    Feedback loop forming
D   [.1][.5][.6][1 ][.3]
E   [.2][.3][.4][.3][1 ]

MINUTE 10: SYNCHRONIZED DEATH
     A  B  C  D  E
A   [1 ][.9][.9][.9][.9]    CORRELATION > 0.9!
B   [.9][1 ][.95][.98][.92]  All services in lockstep
C   [.9][.95][1 ][.97][.94]  Moving as one entity
D   [.9][.98][.97][1 ][.93]  Resonance achieved
E   [.9][.92][.94][.93][1 ]  SYSTEM-WIDE FAILURE

HOW IT HAPPENS:
1. Shared resource (DB, queue, cache)
2. Similar timeout/retry configs
3. Load balancer round-robin
4. Services start "beating" together
5. Constructive interference
6. BOOM - Resonance cascade
```

**Real Fix from Netflix:**
```python
# Add jitter to break synchronization
def make_request():
    jitter = random.uniform(0, 100)  # ms
    time.sleep(jitter / 1000)
    return actual_request()
```
</div>

## Pattern 5: The Cascade Failure 🏔️

<div class="failure-vignette">
<h3>One Service to Kill Them All</h3>

```
AWS KINESIS OUTAGE 2020: THE DEPENDENCY AVALANCHE
═════════════════════════════════════════════════

THE INNOCENT START:
Kinesis has a small capacity issue...

THE CASCADE MAP:
                    Kinesis
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     CloudWatch              Cognito (auth)
          │                       │
          ▼                       ▼
    All Monitoring          All User Logins
          │                       │
    ┌─────┴─────┐           ┌─────┴─────┐
    ▼           ▼           ▼           ▼
AutoScaling   Alarms    S3 Events   Lambda
    │           │           │           │
    ▼           ▼           ▼           ▼
  BROKEN      SILENT    NO UPLOADS  NO CODE

SERVICES THAT DIED:
├─ Kinesis (root cause)
├─ CloudWatch (depends on Kinesis)
├─ AutoScaling (needs CloudWatch)
├─ Lambda (needs CloudWatch)
├─ Cognito (uses Kinesis)
├─ S3 Events (needs Kinesis)
├─ ... 47 other services

TIME TO TOTAL FAILURE: 11 minutes

THE TERRIFYING REALIZATION:
"Kinesis is just for streaming data"
BUT it's in EVERY monitoring path!
```

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
</div>

## Pattern 6: Metastable Failure 🎭

<div class="axiom-box">
<h3>The Hidden State Bomb</h3>

```
THE METASTABLE NIGHTMARE
════════════════════════

Your system has TWO stable states:

STATE 1: Happy Mode 😊
├─ Load: 80%
├─ Cache: Warm
├─ Queues: Flowing
└─ Response: 50ms

STATE 2: Death Mode 💀
├─ Load: 60% (LOWER!)
├─ Cache: Cold
├─ Queues: Backed up
└─ Response: TIMEOUT

THE TERRIFYING PART:
At 60% load, BOTH states are stable!
Tiny trigger flips between them.

REAL EXAMPLE - SLACK 2021:
───────────────────────────
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

THE PHYSICS:
This is a "bistable system" with hysteresis
Like magnetic materials that stay magnetized
Your system gets "stuck" in bad state

ESCAPE PATTERN:
if (in_death_mode()) {
    // Load reduction won't help!
    // Must "shock" system out
    
    1. Prewarm all caches
    2. Drain all queues  
    3. Reset all state
    4. Gradually reintroduce load
}
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
</div>

## Pattern Combinations: The Perfect Storm

<div class="failure-vignette">
<h3>When Multiple Patterns Combine</h3>

```
THE GITHUB MEGA-OUTAGE 2023
═══════════════════════════

Start: Database replica lag (innocent enough)
         ↓
Pattern 1: RETRY STORM
Clients retry on stale reads
         ↓
Pattern 2: SYNCHRONIZATION  
All services query same shards
         ↓
Pattern 3: CASCADE FAILURE
Auth service dies, everything needs auth
         ↓
Pattern 4: DEATH SPIRAL
Redis memory pressure, constant evictions
         ↓
Pattern 5: THUNDERING HERD
Cache stampede on user profiles
         ↓
Pattern 6: METASTABLE LOCK
System stuck even at 20% load

TOTAL OUTAGE TIME: 9 hours
PATTERNS ACTIVE: All 6
DAMAGE: $10M+ in SLA credits
```
</div>

## Your Pattern Survival Guide

<div class="decision-box">
<h3>🛡️ Pattern-Specific Defenses</h3>

```
PATTERN              EARLY SIGNAL           DEFENSE
═══════              ════════════           ═══════
Retry Storm          Retry rate > 5%        Circuit breakers
                                           Exponential backoff
                                           Retry budgets

Thundering Herd      Cache miss spike       Request coalescing
                                           Probabilistic refresh
                                           Cache warming

Death Spiral         GC time > 20%          Memory circuit breaker
                                           Allocation budgets
                                           Preemptive restarts

Synchronization      Correlation > 0.7      Add jitter everywhere
                                           Randomize timers
                                           Desync protocols

Cascade              Error in shared svc    Cellular architecture
                                           Dependency limits
                                           Graceful degradation

Metastable           Low load, high latency State reset protocols
                                           Cache prewarming
                                           Bistable detection
```
</div>

!!! warning "The Meta-Truth About Patterns"
    These patterns aren't bugs. They're emergent properties of complex systems. You can't eliminate them—only prepare for them.

**Next**: [The Solutions](../the-solutions/) - Weapons to fight these monsters →