---
title: Immutable Laws Quiz
description: Test your understanding of the fundamental laws with these questions.
type: law
difficulty: advanced
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Immutable Laws Quiz

Test your understanding of the fundamental laws with these questions.

## Sample Questions

### Question 1
Your service makes 3 sequential calls to a database 100ms away. Minimum possible latency?

a) 100ms (parallel calls)
b) 150ms (connection reuse)
c) 300ms (speed of light) ✓
d) 600ms (round trips)

**Explanation**: Sequential calls cannot be parallelized. Each call requires a round trip (request + response), so 3 calls = 3 × 100ms = 300ms minimum due to physics.

### Question 2
You have 99.9% reliable components. Probability that a 10-component serial system works?

a) 99.9% (weakest link)
b) 99.0% (rough estimate)
c) 99.0% (0.999^10) ✓
d) 90.0% (10% failure)

**Explanation**: In a serial system, all components must work. Probability = 0.999^10 ≈ 0.990 or 99.0%

### Question 3
Your queue is 80% utilized. A 10% traffic increase will increase response time by:

a) 10% (linear)
b) 50% (sublinear)
c) 100% (double) ✓
d) 500% (exponential)

**Explanation**: Using M/M/1 queue theory: At 80% utilization, wait time = 4 × service time. At 88% utilization (80% × 1.1), wait time = 8 × service time. This is a 100% increase.

### Question 4
Which coordination pattern has the lowest latency cost?

a) Two-phase commit
b) Paxos/Raft
c) Gossip protocol ✓
d) Byzantine consensus

**Explanation**: Gossip protocols have O(log N) convergence time and don't require synchronous coordination, making them lowest latency but with eventual consistency trade-off.

### Question 5
A system with partial failure is best described as:

a) Completely broken
b) Completely working
c) Working AND broken ✓
d) About to fail

**Explanation**: Distributed systems can be in superposition - some parts working while others have failed, creating complex failure modes.

### Question 6
The observer effect in distributed systems means:

a) You need more engineers
b) Monitoring changes system behavior ✓
c) Logs are unreliable
d) Metrics are always delayed

**Explanation**: Adding observability (logs, metrics, traces) consumes resources and adds latency, changing the system's behavior.

### Question 7
Human error rate increases most with:

a) System complexity
b) Time of day
c) Stress ✓
d) Experience level

**Explanation**: Under stress (like during an outage), human error rates can increase from 1 in 1000 to 1 in 100 actions.

### Question 8
The hidden cost multiplier in serverless often comes from:

a) Cold starts
b) Memory allocation
c) Retries ✓
d) Deployment time

**Explanation**: Retries can multiply costs dramatically - 5 retries means 6x the invocations, 6x the cost.

### Question 9
Which law most directly leads to eventual consistency?

a) Asynchronous Reality ✓
b) Emergent Complexity
c) Correlated Failure
d) Economic Reality

**Explanation**: Asynchronous Reality (latency constraints) makes synchronous global consistency too slow, leading to eventual consistency as a practical choice.

### Question 10
The CAP theorem is best understood as a consequence of:

a) Poor design
b) Physics and laws ✓
c) Database limitations
d) Network protocols

**Explanation**: CAP emerges from the fundamental laws - latency makes partitions inevitable, forcing a choice between consistency and availability.

## More Practice Questions

Want more questions? Each law section includes specific exercises and scenarios to test your understanding.

## Advanced Scenario Questions

### Scenario 1: Global Payment System
You're designing a payment system across 5 continents. Which law combination most constrains your design?

a) Asynchronous Reality + Emergent Complexity
b) Distributed Knowledge + Economic Reality
c) Asynchronous Reality + Distributed Knowledge + Economic Reality ✓
d) Correlated Failure + Cognitive Load

**Explanation**: 
- **Asynchronous Reality**: Cross-continent RTT = 150-300ms
- **Distributed Knowledge**: Money state must be consistent globally (no double-spend)
- **Economic Reality**: Each region needs local infrastructure
Together they force complex trade-offs between speed, correctness, and cost.

### Scenario 2: Distributed Lock Service
Your lock service sees 50% failure in leader election. Most likely cause?

a) Network partition
b) Clock skew ✓
c) CPU overload
d) Memory leak

**Explanation**: Leader election relies on timeouts. Clock skew between nodes can cause them to disagree on when timeouts occur, leading to split-brain scenarios.

### Scenario 3: Microservices Debugging
Debugging takes 10x longer in microservices vs monolith. Primary law responsible?

a) Asynchronous Reality
b) Correlated Failure
c) Distributed Knowledge ✓
d) Cognitive Load

**Explanation**: Distributed Knowledge means each service has only partial knowledge of the system state. You can't see the full system state from any single vantage point, making debugging exponentially harder.

## Quiz Results Interpretation

| Score | Level | What It Means |
|-------|-------|---------------|
| 0-3 | Beginner | Review laws fundamentals |
| 4-6 | Intermediate | Good grasp, practice applications |
| 7-9 | Advanced | Ready for complex scenarios |
| 10+ | Expert | Teach others! |

## Law Mastery Assessment

Rate your understanding of each law:

| Law | Concept | Math/Formulas | Real Applications | Trade-offs |
|-------|---------|---------------|-------------------|------------|
| 1. Correlated Failure ⛓️ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 2. Asynchronous Reality ⏳ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 3. Emergent Complexity 🌪️ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 4. Multidimensional Optimization ⚖️ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 5. Distributed Knowledge 🧠 | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 6. Cognitive Load 🤯 | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |
| 7. Economic Reality 💰 | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ | ⬜⬜⬜⬜⬜ |

Fill in boxes to track progress: ⬜ = Not started, 🟦 = Learning, 🟩 = Confident

## Common Misconceptions

### ❌ Myth vs ✅ Reality

| Myth | Reality | Law |
|------|---------|-------|
| "Just add more servers" | Coordination costs grow with emergent complexity | Law 3: Emergent Complexity |
| "Use microservices for speed" | Network calls add latency | Law 2: Asynchronous Reality |
| "100% uptime is possible" | Failures are inevitable and correlated | Law 1: Correlated Failure |
| "Strong consistency is always best" | It has latency and availability costs | Law 4: Multidimensional Optimization |
| "More monitoring is always better" | Observer effect has cognitive and economic costs | Laws 6 & 7 |

## Study Resources by Learning Style

### Visual Learners
- Review law diagrams
- Trace through architecture diagrams
- Watch latency animations

### 📖 Reading/Writing Learners
- Work through exercises
- Write reflection journal entries
- Create your own examples

### 🎧 Auditory Learners
- Explain laws to a colleague
- Join study groups
- Listen to distributed systems podcasts

### 🔨 Kinesthetic Learners
- Build the lab exercises
- Experiment with failure scenarios
- Measure real system behavior

## Next Steps

1. **Weak Areas**: Focus on laws where you scored lowest
2. **Practice**: Work through exercises in each law section
3. **Apply**: Use the reflection journal to connect to your work
4. **Share**: Teach someone else - best way to solidify understanding

Remember: These aren't trivia questions - they test whether you truly understand the fundamental constraints that govern all distributed systems.
