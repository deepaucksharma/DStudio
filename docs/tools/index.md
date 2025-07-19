# Interactive Tools

Apply the axioms and pillars with practical calculators, worksheets, and decision frameworks that help you design systems within physics constraints.

---

## 🧮 Latency Calculator

**Apply Axiom 1: Understand the speed of causality**

<div class="latency-calculator">
<h3>📡 Speed of Light Distance Calculator</h3>

**Calculate minimum possible latency between locations:**

| From | To | Distance (km) | Light Speed Latency | Fiber Latency (×1.5) | Realistic Latency |
|------|----|--------------|--------------------|-------------------|------------------|
| New York | London | 5,585 | 18.6ms | 27.9ms | 35-50ms |
| San Francisco | Tokyo | 8,280 | 27.6ms | 41.4ms | 50-80ms |
| Sydney | Frankfurt | 16,000 | 53.3ms | 80.0ms | 100-150ms |

**Quick Calculator Formulas:**
```
Light Speed Latency = Distance ÷ 300,000 km/s
Fiber Latency = Light Speed × 1.5 (refractive index)
Internet Latency = Fiber × 1.2-2.0 (routing overhead)
```

**Design Rule**: If your system requires <10ms response, ensure components are within 1,500km
</div>

---

## ⚖️ Capacity Planning Worksheet

**Apply Axiom 2: Size your finite boxes**

<div class="capacity-worksheet">
<h3>🗃️ System Capacity Planner</h3>

**Step 1: Define Your Workload**
```
Peak Users: _________ concurrent users
Requests per User: _________ requests/minute
Peak Traffic: _________ requests/second (RPS)
```

**Step 2: Resource Requirements per Request**
```
CPU Time: _________ ms per request
Memory: _________ MB per request  
Storage I/O: _________ IOPS per request
Network: _________ KB per request
```

**Step 3: Calculate Infrastructure Needs**

| Resource | Formula | Your Calculation |
|----------|---------|------------------|
| **CPU Cores** | (Peak RPS × CPU ms/req) ÷ 1000 | _________ cores |
| **Memory** | Peak RPS × Memory per req × Buffer | _________ GB |
| **Storage IOPS** | Peak RPS × IOPS per req | _________ IOPS |
| **Network** | Peak RPS × KB per req | _________ MB/s |

**Buffer Factors:**
- Memory: 2x (garbage collection, buffers)
- CPU: 1.5x (OS overhead, context switching)
- Storage: 1.8x (write amplification, fragmentation)
- Network: 1.3x (protocol overhead, retransmissions)
</div>

---

## 💥 Failure Analysis Framework

**Apply Axiom 3: Plan for inevitable entropy**

<div class="failure-framework">
<h3>🎯 Failure Mode Assessment</h3>

**FMEA (Failure Mode Effects Analysis) Worksheet:**

| Component | Failure Mode | Probability | Impact | Detection | Risk Score |
|-----------|--------------|-------------|--------|-----------|------------|
| Load Balancer | Hardware failure | Low (1) | High (4) | Good (2) | 8 |
| Database | Disk corruption | Medium (3) | Critical (5) | Poor (4) | 60 |
| Network | Packet loss | High (4) | Medium (3) | Good (2) | 24 |

**Risk Score = Probability × Impact × Detection Difficulty**

**Mitigation Priority:**
1. **Score >50**: Immediate action required
2. **Score 20-50**: Plan mitigation within quarter
3. **Score <20**: Monitor and document

**Common Failure Patterns:**
```
Hardware Failures:
- MTBF: 3-5 years for servers
- Disk failure: 2-4% annually
- Network equipment: 1-2% annually

Software Failures:
- Memory leaks: Gradual degradation
- Race conditions: Intermittent failures
- Configuration errors: Immediate impact

Operational Failures:
- Human error: 70% of outages
- Process failures: Inadequate procedures
- Communication failures: Poor incident response
```
</div>

---

## 🎲 Concurrency Analysis Tools

**Apply Axiom 4: Model distributed timelines**

<div class="concurrency-tools">
<h3>⏱️ Race Condition Detector</h3>

**Critical Section Analysis:**
```
Identify Shared Resources:
□ Shared variables/state
□ Database records
□ File system objects
□ Network connections

Check Synchronization:
□ Proper locking mechanisms
□ Atomic operations where needed
□ Consistent lock ordering
□ Deadlock prevention

Timing Dependencies:
□ Message ordering guarantees
□ Happens-before relationships
□ Clock synchronization needs
□ Causal ordering requirements
```

**Concurrency Pattern Selector:**

| Scenario | Pattern | When to Use | Trade-offs |
|----------|---------|-------------|------------|
| Shared Counter | Atomic Operations | High frequency updates | CPU overhead |
| Critical Section | Mutexes/Locks | Complex state changes | Blocking |
| Producer-Consumer | Queues | Async processing | Memory usage |
| Reader-Writer | RW Locks | Read-heavy workloads | Complexity |
</div>

---

## 🤝 Consensus Decision Matrix

**Apply Axiom 5: Choose coordination mechanisms**

<div class="consensus-matrix">
<h3>⚖️ Consensus Algorithm Selector</h3>

**System Requirements Assessment:**

| Requirement | Weight | Raft | Paxos | PBFT | Gossip |
|-------------|--------|------|-------|------|--------|
| **Simplicity** | High | 9 | 4 | 3 | 8 |
| **Performance** | Medium | 7 | 8 | 4 | 9 |
| **Byzantine Tolerance** | Low | 0 | 0 | 9 | 6 |
| **Network Efficiency** | High | 6 | 6 | 3 | 9 |
| **Strong Consistency** | High | 9 | 9 | 9 | 3 |

**Decision Framework:**
```
If strong consistency required:
├─ Byzantine faults possible? → PBFT
├─ Network efficiency critical? → Gossip + Eventual
├─ Team prefers simplicity? → Raft
└─ Maximum performance? → Paxos

If eventual consistency acceptable:
├─ High scalability needed? → Gossip
├─ Conflict resolution easy? → CRDTs
└─ Simple use case? → Last-Write-Wins
```
</div>

---

## 👁️ Observability Metrics Dashboard

**Apply Axiom 6: Instrument for knowledge**

<div class="observability-dashboard">
<h3>📊 Golden Signals Tracker</h3>

**Service Health Scorecard:**

| Signal | Metric | Target | Current | Status |
|--------|--------|--------|---------|--------|
| **Latency** | P95 Response Time | <100ms | ___ms | ⚪ |
| **Traffic** | Requests/Second | ___k RPS | ___k RPS | ⚪ |
| **Errors** | Error Rate | <0.1% | __% | ⚪ |
| **Saturation** | CPU Utilization | <70% | __% | ⚪ |

**SLA Calculator:**
```
Availability Target: 99.9% (8h 45m downtime/year)
Error Budget: 0.1% (43.8 minutes/month)

Current Month:
Downtime so far: _____ minutes
Error budget remaining: _____ minutes
Burn rate: _____ × (normal = 1.0)
```

**Alert Design Checklist:**
```
□ Actionable (tells you what to do)
□ User-impacting (affects real users)
□ Includes context (what's happening)
□ Has runbook link
□ Avoids alert fatigue
□ Escalates appropriately
```
</div>

---

## 👤 Human Interface Assessment

**Apply Axiom 7: Design the organic API**

<div class="human-interface-assessment">
<h3>🧠 Cognitive Load Calculator</h3>

**Mental Model Complexity Score:**

| Factor | Weight | Score (1-5) | Weighted Score |
|--------|--------|-------------|----------------|
| **Information Density** | 3x | ___ | ___ |
| **Context Switching** | 2x | ___ | ___ |
| **Decision Points** | 3x | ___ | ___ |
| **Tool Fragmentation** | 2x | ___ | ___ |
| **Time Pressure** | 4x | ___ | ___ |

**Total Cognitive Load: _____ / 70**

**Interpretation:**
- 0-20: Low load, operators comfortable
- 21-40: Moderate load, manageable
- 41-55: High load, training needed
- 56-70: Extreme load, redesign required

**NASA TLX Factors:**
```
Mental Demand: How much thinking was required?
Physical Demand: How much physical activity?
Temporal Demand: How hurried was the pace?
Performance: How successful were you?
Effort: How hard did you work?
Frustration: How stressed/annoyed were you?
```
</div>

---

## 💰 Economics Calculator

**Apply Axiom 8: Optimize cost at scale**

<div class="economics-calculator">
<h3>💸 Total Cost of Ownership (TCO) Calculator</h3>

**Infrastructure Costs (Annual):**
```
Compute: $_____ /year
Storage: $_____ /year  
Network: $_____ /year
Licenses: $_____ /year
Support: $_____ /year
```

**Operational Costs (Annual):**
```
Engineering: $_____ /year (_____ FTE × $150k)
Operations: $_____ /year (_____ FTE × $120k)
Incident Cost: $_____ /year (_____ hours × $500/hour)
Training: $_____ /year
```

**Scale Economics Analysis:**

| Users | Infrastructure | Ops Cost | Cost/User | Margin |
|-------|---------------|----------|-----------|--------|
| 1K | $10K | $50K | $60.00 | -% |
| 10K | $50K | $100K | $15.00 | +% |
| 100K | $200K | $200K | $4.00 | ++% |
| 1M | $800K | $400K | $1.20 | +++% |

**Break-even Analysis:**
```
Fixed Costs: $_____ /month
Variable Cost per User: $_____ /user/month
Revenue per User: $_____ /user/month

Break-even Users = Fixed Costs ÷ (Revenue - Variable Cost)
```
</div>

---

## 🏗️ Architecture Decision Records (ADRs)

**Apply All Axioms: Document trade-offs**

<div class="adr-template">
<h3>📋 ADR Template</h3>

**Use this template for major architectural decisions:**

```markdown
# ADR-001: [Decision Title]

## Status
[Proposed | Accepted | Superseded]

## Context
What is the issue motivating this decision?

## Axiom Analysis
- Latency: How does this affect response times?
- Capacity: What are the resource implications?
- Failure: What can go wrong? How do we handle it?
- Concurrency: Any race conditions or timing issues?
- Coordination: What consensus/consistency model?
- Observability: How will we monitor this?
- Human Interface: Impact on operator complexity?
- Economics: Cost implications and scaling?

## Decision
What is the change we're proposing/doing?

## Consequences
What becomes easier or more difficult after this change?

## Alternatives Considered
What other options did we evaluate?
```
</div>

---

## 🎯 Quick Decision Frameworks

**Rapid architectural guidance**

<div class="decision-frameworks">
<h3>⚡ 5-Minute Architecture Decisions</h3>

**Database Choice Framework:**
```
┌─────────────────────────────────┐
│ ACID transactions required?     │
│ ↓ YES              ↓ NO         │
│ SQL Database       NoSQL DB     │
│                                 │
│ Scale > 1TB?                    │
│ ↓ YES              ↓ NO         │
│ Distributed SQL    Single Node  │
│                                 │
│ Strong consistency?             │
│ ↓ YES              ↓ NO         │
│ PostgreSQL/MySQL   MongoDB/Cassandra │
└─────────────────────────────────┘
```

**Caching Strategy Decision:**
```
Data Change Frequency:
├─ Rarely (hours): Database caching
├─ Occasionally (minutes): Application caching  
├─ Frequently (seconds): In-memory only
└─ Constantly: No caching

Cache Invalidation:
├─ Time-based: TTL expiration
├─ Event-based: Pub/sub notifications
├─ Manual: Explicit cache clearing
└─ Write-through: Update cache on write
```

**Microservices Boundary Decision:**
```
Split services when:
□ Different teams own the logic
□ Different scaling requirements
□ Different technology needs
□ Different data access patterns
□ Different change frequencies

Keep together when:
□ Strong data consistency needed
□ Low latency communication required  
□ Shared complex business logic
□ Small team (< 8 people)
□ Early stage/prototype
```
</div>

---

## 📚 Reference Quick Cards

**Essential formulas and rules of thumb**

<div class="reference-cards">
<h3>🃏 Distributed Systems Cheat Sheet</h3>

**Latency Rules:**
```
L1 cache: 0.5 ns
L2 cache: 7 ns  
RAM: 100 ns
SSD: 150 μs
HDD: 10 ms
Network: 150 ms (cross-continent)
```

**Capacity Rules:**
```
Little's Law: N = λ × W
- N = items in system
- λ = arrival rate  
- W = time in system

Rule of thumb: 2x capacity for 99% availability
```

**Availability Math:**
```
99%: 3.65 days/year downtime
99.9%: 8.77 hours/year downtime  
99.99%: 52.6 minutes/year downtime
99.999%: 5.26 minutes/year downtime
```

**Cost Scaling Patterns:**
```
Linear: Storage, bandwidth
Logarithmic: Caching efficiency
Quadratic: Network mesh, consensus
Exponential: Coordination overhead
```
</div>

---

*"The best tools amplify human judgment rather than replace it."*