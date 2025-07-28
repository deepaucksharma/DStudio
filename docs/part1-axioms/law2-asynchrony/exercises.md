# Law 2: Exercises - Build Your Async Instincts ⚡

<div class="axiom-box">
<h2>The Time Warrior Training Camp</h2>
<p>These exercises will rewire your brain to think asynchronously. Each one comes from a real production disaster. Master these, and you'll spot async bugs before they bite.</p>
</div>

## Quick Skills Assessment

```
YOUR ASYNC MATURITY LEVEL
═════════════════════════

□ Level 0: "What's clock skew?"
□ Level 1: "I use NTP, so I'm fine"
□ Level 2: "I know about timeouts"
□ Level 3: "I use idempotency keys"
□ Level 4: "I debug with Lamport clocks"
□ Level 5: "I dream in vector clocks"

Complete these exercises to level up! 🎮
```

---

## Exercise 1: The Deployment Detective 🕵️

<div class="failure-vignette">
<h3>Scenario: The Mysterious Monday Meltdown</h3>

Your e-commerce site crashes every Monday at 9:00 AM. Here's what you know:

```
SYSTEM ARCHITECTURE
═══════════════════

[Load Balancer]
      ↓
┌─────┴─────┬─────────┬─────────┐
│ Server A  │ Server B │ Server C │
│ (US-East) │ (US-East)│ (US-West)│
└───────────┴─────────┴─────────┘

CLUES FROM LOGS
═══════════════

Server A (Monday 8:59:59): "Starting flash sale"
Server B (Monday 9:00:00): "Starting flash sale"  
Server C (Monday 8:57:03): "Starting flash sale"

Customer complaints:
- "I see the sale!"
- "What sale?"
- "Site is down!"
```

**Your Mission:**
1. What's causing the crash?
2. Draw the timeline of events
3. Propose a fix

<details>
<summary>💡 Hint</summary>
Check the timestamps carefully. What time zone is Server C in?
</details>

<details>
<summary>✅ Solution</summary>

```
THE PROBLEM VISUALIZED
════════════════════

Real time:           What servers think:
9:00 AM EST         A: 9:00 AM ✓
                    B: 9:00 AM ✓
                    C: 9:00 AM (but PST = 6:00 AM EST!)
                    
Server C starts sale 3 hours early!

WHAT HAPPENS
════════════
6:00 AM EST: Server C starts serving sale prices
6:01 AM EST: Early birds flood Server C
6:30 AM EST: Server C overwhelmed, starts dropping requests
9:00 AM EST: Servers A & B start sale
9:01 AM EST: Full system meltdown from asymmetric load

THE FIX
═══════
// Instead of wall clock time:
if (Date.now() >= SALE_START_TIME) { ... }

// Use logical events:
if (received_message("START_SALE")) { ... }
```
</details>
</div>

---

## Exercise 2: The Timeout Puzzle 🧩

<div class="decision-box">
<h3>Challenge: Fix the Cascade</h3>

Your microservice architecture is timing out. Calculate the correct timeout values:

```
SERVICE CHAIN
═════════════

Client → API Gateway → Service A → Service B → Database
  ?          ?             ?           ?         2s

CONSTRAINTS
═══════════
- Database queries take 2 seconds (p99)
- Each network hop adds 50ms (p99)
- Users abandon after 10 seconds
- Each service should retry once on timeout

YOUR TASK: Fill in the timeout values
═════════════════════════════════════

Database timeout:  2s (given)
Service B timeout: _____ (must handle DB + network)
Service A timeout: _____ (must handle B + retry + network)  
Gateway timeout:   _____ (must handle A + retry + network)
Client timeout:    _____ (must handle Gateway + retry)
```

<details>
<summary>📐 Show the math</summary>

```
TIMEOUT CALCULATION
═══════════════════

Database:     2.0s (given)

Service B:    2.0s (DB)
            + 0.05s (network to DB)
            = 2.05s
            × 2 (one retry)
            = 4.1s timeout

Service A:    4.1s (Service B)
            + 0.05s (network to B)
            = 4.15s
            × 2 (one retry)
            = 8.3s timeout

API Gateway:  8.3s (Service A)
            + 0.05s (network to A)
            = 8.35s
            × 2 (one retry)
            = 16.7s timeout ❌ (> 10s user limit!)

PROBLEM: Total time exceeds user patience!
```
</details>

<details>
<summary>✅ Better solution</summary>

```
TIMEOUT BUDGET APPROACH
═════════════════════

Start with user constraint: 10s total

Client timeout:    9.5s (leaving 0.5s buffer)
Gateway timeout:   9.0s (0.5s for client overhead)
Service A timeout: 4.0s (allows one retry: 4s × 2 = 8s)
Service B timeout: 1.8s (allows one retry: 1.8s × 2 = 3.6s)
Database timeout:  1.5s (tighter SLA needed!)

If can't meet timing:
- Return cached results
- Degrade gracefully
- Pre-compute expensive queries
```
</details>
</div>

---

## Exercise 3: The Race Condition Range 🏃

<div class="axiom-box">
<h3>Spot the Bug: Concurrent Counter</h3>

Two servers are incrementing a shared counter:

```python
# Current implementation
async def increment_user_points(user_id, points):
    current = await db.get(f"points:{user_id}")
    new_value = current + points
    await db.set(f"points:{user_id}", new_value)
    return new_value
```

**Scenario Timeline:**
```
Time    Server A              Server B            Database
────    ────────              ────────            ────────
T0                                               points:123 = 100
T1      get(points:123)                          → returns 100
T2                           get(points:123)     → returns 100  
T3      new = 100 + 10                          
T4                           new = 100 + 20
T5      set(points:123, 110)                    → stores 110
T6                           set(points:123, 120) → stores 120

Expected: 100 + 10 + 20 = 130
Actual: 120 ❌ (Lost 10 points!)
```

**Your Tasks:**
1. Draw the race condition
2. Write three different fixes
3. Rank them by performance

<details>
<summary>✅ Solutions</summary>

```
SOLUTION 1: ATOMIC INCREMENT (BEST)
═══════════════════════════════════
await db.increment(f"points:{user_id}", points)
# Single atomic operation, no race possible

SOLUTION 2: OPTIMISTIC LOCKING
══════════════════════════════
async def increment_with_version(user_id, points):
    while True:
        current, version = await db.get_with_version(f"points:{user_id}")
        new_value = current + points
        if await db.set_if_version(f"points:{user_id}", new_value, version):
            return new_value
        # Retry if version changed

SOLUTION 3: DISTRIBUTED LOCK (WORST)
═══════════════════════════════════
async def increment_with_lock(user_id, points):
    lock = await acquire_lock(f"lock:points:{user_id}")
    try:
        current = await db.get(f"points:{user_id}")
        new_value = current + points
        await db.set(f"points:{user_id}", new_value)
        return new_value
    finally:
        await release_lock(lock)

Performance ranking:
1. Atomic: ~1ms (single operation)
2. Optimistic: ~2-5ms (may retry)
3. Lock: ~10-50ms (coordination overhead)
```
</details>
</div>

---

## Exercise 4: The Phantom Write Workshop 👻

<div class="truth-box">
<h3>Debug the Double-Charge</h3>

Your payment service has this code:

```javascript
async function processPayment(orderId, amount, cardToken) {
    try {
        const chargeId = await paymentGateway.charge(cardToken, amount, {
            timeout: 5000  // 5 second timeout
        });
        
        await orderDB.markPaid(orderId, chargeId);
        await emailService.sendReceipt(orderId);
        
        return { success: true, chargeId };
    } catch (error) {
        if (error.code === 'TIMEOUT') {
            // Retry once
            return processPayment(orderId, amount, cardToken);
        }
        throw error;
    }
}
```

**The Bug Report:**
```
Customer: "I was charged 3 times for one order!"
Logs show:
- 10:00:00 - First charge attempt (timeout after 5s)
- 10:00:05 - Retry attempt (timeout after 5s)  
- 10:00:10 - Retry attempt (success)
- Payment gateway shows: 3 successful charges!
```

**Your Mission:**
1. Explain why 3 charges happened
2. Fix the code
3. Handle the existing duplicate charges

<details>
<summary>🔍 Root Cause</summary>

```
WHAT REALLY HAPPENED
═══════════════════

10:00:00: Charge #1 starts
10:00:05: Client times out (but charge continues!)
10:00:05: Charge #2 starts  
10:00:10: Client times out (but charge continues!)
10:00:10: Charge #3 starts
10:00:12: Charge #1 completes ✓ (client doesn't know)
10:00:13: Charge #2 completes ✓ (client doesn't know)
10:00:11: Charge #3 completes ✓ (client knows this one)

The timeout doesn't cancel the charge!
```
</details>

<details>
<summary>✅ Complete Solution</summary>

```javascript
// FIXED VERSION WITH IDEMPOTENCY
async function processPayment(orderId, amount, cardToken) {
    // Generate idempotency key from order (not request!)
    const idempotencyKey = `payment_${orderId}`;
    
    try {
        // Check if already processed
        const existing = await paymentDB.get(idempotencyKey);
        if (existing) {
            return existing;
        }
        
        const chargeId = await paymentGateway.charge(cardToken, amount, {
            idempotencyKey,  // Gateway prevents duplicates
            timeout: 30000   // Longer timeout
        });
        
        // Store result
        const result = { success: true, chargeId };
        await paymentDB.set(idempotencyKey, result, { ttl: 86400 });
        
        await orderDB.markPaid(orderId, chargeId);
        await emailService.sendReceipt(orderId);
        
        return result;
    } catch (error) {
        if (error.code === 'TIMEOUT') {
            // Check if charge succeeded despite timeout
            const status = await paymentGateway.checkCharge(idempotencyKey);
            if (status.success) {
                return { success: true, chargeId: status.chargeId };
            }
        }
        throw error;
    }
}

// HANDLE EXISTING DUPLICATES
async function refundDuplicates(orderId) {
    const charges = await paymentGateway.listCharges({ orderId });
    const validCharge = charges[0];  // Keep first one
    
    for (let i = 1; i < charges.length; i++) {
        await paymentGateway.refund(charges[i].id, {
            reason: "Duplicate charge due to timeout"
        });
    }
}
```
</details>
</div>

---

## Exercise 5: The Clock Skew Simulator 🕰️

<div class="decision-box">
<h3>Hands-On: Build a Clock Skew Detector</h3>

```javascript
// Your distributed system has 5 nodes
const nodes = [
    { id: 'A', getTime: () => Date.now() + 0 },     // Accurate
    { id: 'B', getTime: () => Date.now() + 3000 },  // 3s fast
    { id: 'C', getTime: () => Date.now() - 2000 },  // 2s slow
    { id: 'D', getTime: () => Date.now() + 100 },   // 100ms fast
    { id: 'E', getTime: () => Date.now() - 5000 },  // 5s slow!
];

// TODO: Implement these functions
function detectClockSkew(nodes) {
    // Return maximum skew between any two nodes
}

function findSkewedNodes(nodes, threshold = 1000) {
    // Return nodes that differ from median by > threshold
}

function calculateTrueTime(nodes) {
    // Return best estimate of true time with uncertainty bounds
    // Format: { earliest: timestamp, latest: timestamp }
}
```

<details>
<summary>✅ Implementation</summary>

```javascript
function detectClockSkew(nodes) {
    const times = nodes.map(n => n.getTime());
    const maxTime = Math.max(...times);
    const minTime = Math.min(...times);
    return maxTime - minTime;
}

function findSkewedNodes(nodes, threshold = 1000) {
    const times = nodes.map(n => ({ id: n.id, time: n.getTime() }));
    const sortedTimes = times.map(t => t.time).sort((a, b) => a - b);
    const median = sortedTimes[Math.floor(sortedTimes.length / 2)];
    
    return times
        .filter(t => Math.abs(t.time - median) > threshold)
        .map(t => ({
            id: t.id,
            skew: t.time - median
        }));
}

function calculateTrueTime(nodes) {
    const times = nodes.map(n => n.getTime());
    
    // Remove outliers (more than 2 std dev from mean)
    const mean = times.reduce((a, b) => a + b) / times.length;
    const stdDev = Math.sqrt(
        times.reduce((sum, time) => sum + Math.pow(time - mean, 2), 0) / times.length
    );
    
    const filtered = times.filter(t => Math.abs(t - mean) <= 2 * stdDev);
    const avgTime = filtered.reduce((a, b) => a + b) / filtered.length;
    const maxDeviation = Math.max(...filtered.map(t => Math.abs(t - avgTime)));
    
    return {
        earliest: avgTime - maxDeviation,
        latest: avgTime + maxDeviation,
        uncertainty: maxDeviation * 2
    };
}

// Test your implementation
console.log('Max skew:', detectClockSkew(nodes));  // 8000ms
console.log('Skewed nodes:', findSkewedNodes(nodes));
// [{ id: 'B', skew: 3000 }, { id: 'C', skew: -2000 }, { id: 'E', skew: -5000 }]
console.log('True time:', calculateTrueTime(nodes));
// { earliest: timestamp-X, latest: timestamp+X, uncertainty: 2X }
```
</details>
</div>

---

## Exercise 6: The Distributed Trace Debugger 🔍

<div class="failure-vignette">
<h3>Mystery: The Backwards Request</h3>

Your distributed tracing shows this impossible sequence:

```
REQUEST ID: abc-123
═══════════════════

Service A │10:00:00.100│──request──→│10:00:00.050│ Service B
          │            │             │            │
          │10:00:00.200│←─response──│10:00:00.180│
          
Wait... B received the request BEFORE A sent it?! 🤯
```

**Your Tasks:**
1. List 3 possible causes
2. Design a fix using Lamport clocks
3. Implement vector clocks for causality

<details>
<summary>💡 Analysis</summary>

```
POSSIBLE CAUSES
═══════════════

1. Clock Skew: B's clock is 50ms+ behind A's clock
2. NTP Jump: Clock adjusted during request
3. Tracign Bug: Timestamps captured at wrong point

LAMPORT CLOCK SOLUTION
═════════════════════

Service A:                       Service B:
LC = 0                          LC = 0
                               
LC = 1                          
Send(request, LC=1) ─────→      Receive(request, LC=1)
                                LC = max(0, 1) + 1 = 2
                                
                                Process request...
                                
Receive(response, LC=3)  ←───── Send(response, LC=3)
LC = max(1, 3) + 1 = 4          LC = 3

Now order is clear: 1 → 2 → 3 → 4
```
</details>

<details>
<summary>✅ Vector Clock Implementation</summary>

```javascript
class VectorClock {
    constructor(nodeId, nodeList) {
        this.nodeId = nodeId;
        this.clock = {};
        nodeList.forEach(id => this.clock[id] = 0);
    }
    
    increment() {
        this.clock[this.nodeId]++;
        return this.toArray();
    }
    
    update(otherClock) {
        // Take maximum of each component
        Object.keys(this.clock).forEach(id => {
            this.clock[id] = Math.max(this.clock[id], otherClock[id] || 0);
        });
        // Increment own component
        this.clock[this.nodeId]++;
        return this.toArray();
    }
    
    isBefore(otherClock) {
        // True if all components ≤ and at least one <
        let hasLess = false;
        for (let id in this.clock) {
            if (this.clock[id] > (otherClock[id] || 0)) return false;
            if (this.clock[id] < (otherClock[id] || 0)) hasLess = true;
        }
        return hasLess;
    }
    
    isConcurrent(otherClock) {
        return !this.isBefore(otherClock) && !otherClock.isBefore(this);
    }
    
    toArray() {
        return { ...this.clock };
    }
}

// Usage in distributed trace
const serviceA = new VectorClock('A', ['A', 'B']);
const serviceB = new VectorClock('B', ['A', 'B']);

// A sends request
serviceA.increment();  // {A:1, B:0}
const msgClock = serviceA.toArray();

// B receives request
serviceB.update(msgClock);  // {A:1, B:1}

// Now we can detect causality without wall clocks!
```
</details>
</div>

---

## Final Boss: The Production Postmortem 🎮

<div class="truth-box" style="background: #1a1a1a; border: 2px solid #ff5555;">
<h3>Ultimate Challenge: Real Incident Analysis</h3>

**The Incident:**
Your e-commerce site had a 2-hour outage during Black Friday. Here are the facts:

```
TIMELINE OF DOOM
════════════════

14:00:00 - Black Friday sale starts
14:00:15 - Response times increase 50ms → 500ms
14:00:30 - Health checks start failing
14:00:45 - Auto-scaling triggers
14:01:00 - New instances come online
14:01:30 - MORE health checks fail (?!)
14:02:00 - Cascading failures begin
14:04:00 - Full site outage

ARCHITECTURE
════════════
                 [Load Balancer]
                        ↓
         ┌──────────────┼──────────────┐
    [Web Tier]     [Web Tier]     [Web Tier]
         ↓              ↓              ↓
    [App Tier]     [App Tier]     [App Tier]
         ↓              ↓              ↓
    [Cache]        [Cache]        [Cache]
         ↓              ↓              ↓
         └──────────[Database]─────────┘

CLUES
═════
- Database CPU: 20% throughout
- Cache hit rate: 95% → 5% after scale-up
- New instances took 90s to fully initialize
- Health check timeout: 1s
- Cache warmup time: 2 minutes
```

**Your Mission:**
1. What caused the outage?
2. Why did scaling make it worse?
3. Design a fix that prevents recurrence
4. Calculate the revenue impact

<details>
<summary>🔎 Root Cause Analysis</summary>

```
THE CHAIN OF EVENTS
═══════════════════

1. Sale starts → Traffic spike
2. Response times increase (cache misses on new items)
3. Health checks timeout (1s < response time)
4. LB marks instances unhealthy
5. Auto-scaling adds new instances
6. New instances have COLD CACHES
7. All traffic hits database directly
8. Database overwhelmed → cascading failure

WHY SCALING MADE IT WORSE
════════════════════════

Before scaling:
- 3 instances with 95% cache hit rate
- Database load: 5% of requests

After scaling:  
- 6 instances, but 3 have 0% cache hit rate
- Database load: 52.5% of requests!
- 10x increase in database load

THE VICIOUS CYCLE
═════════════════

More instances → More cold caches → More DB load
     ↑                                    ↓
Failed health checks ← Slower responses ←┘
```
</details>

<details>
<summary>✅ The Solution</summary>

```
IMMEDIATE FIXES
═══════════════

1. Increase health check timeout: 1s → 5s
2. Implement cache prewarming:
   ```
   async function warmCache(instance) {
       const hotItems = await getTopItems(1000);
       await Promise.all(
           hotItems.map(item => cache.set(item.id, item))
       );
   }
   ```

3. Gradual traffic shifting:
   ```
   function shiftTraffic(newInstance) {
       // Start with 1% traffic
       setWeight(newInstance, 0.01);
       
       // Gradually increase over 5 minutes
       const interval = setInterval(() => {
           const current = getWeight(newInstance);
           if (current >= 1.0) {
               clearInterval(interval);
           } else {
               setWeight(newInstance, current + 0.2);
           }
       }, 60000);
   }
   ```

LONG-TERM FIXES
═══════════════

1. Circuit breaker on database:
   ```
   if (dbRequestRate > threshold) {
       return cachedOrDefaultResponse();
   }
   ```

2. Read replicas with lag monitoring:
   ```
   const replica = selectReplica();
   if (replica.lag > 1000) {  // 1s behind
       return primaryDB.query(...);
   }
   ```

3. Predictive scaling (not reactive):
   - Scale BEFORE the sale
   - Prewarm all caches
   - Load test with realistic data

REVENUE IMPACT
══════════════

Sale hour revenue: $1M/hour normal
Outage duration: 2 hours
Lost revenue: $2M minimum

But worse:
- Customer trust damaged
- Competitors captured traffic  
- Social media nightmare
- Actual impact: $5-10M
```
</details>
</div>

---

## Your Graduation Certificate 🎓

<div class="axiom-box">
<h3>Congratulations, Time Warrior!</h3>

If you completed all exercises, you've learned:

✅ **Pattern Recognition**: Spot async bugs in seconds  
✅ **Timeout Math**: Calculate proper timeout chains  
✅ **Clock Management**: Handle skew like a pro  
✅ **Idempotency**: Make operations retry-safe  
✅ **Logical Time**: Order events without wall clocks  
✅ **Incident Analysis**: Debug production mysteries  

**Your next steps:**
1. Audit your production systems using these patterns
2. Implement monitoring for the "impossible" scenarios  
3. Share these exercises with your team
4. Run a "Time Attack" chaos day

Remember: In distributed systems, time is not your friend—but now you know its tricks!
</div>

**Next Law**: [Law 3: Emergent Chaos](../law3-emergence/) - Where complexity comes alive