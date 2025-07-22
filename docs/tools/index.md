---
title: Interactive Tools & Calculators
description: Apply the axioms and pillars with practical calculators, worksheets, and decision frameworks that help you design systems within physics constraints.
type: general
difficulty: intermediate
reading_time: 30 min
prerequisites: ["part1-axioms", "part2-pillars"]
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → **Interactive Tools & Calculators**

# Interactive Tools & Calculators

Apply the axioms and pillars with practical calculators, worksheets, and decision frameworks that help you design systems within physics constraints.

---

## 🧮 Latency Calculator

**Apply Axiom 1: Understand the speed of causality**

### Geographic Latency Estimator

```text
Distance-Based Latency Calculator:

Speed of Light in Fiber: ~200,000 km/s (2/3 speed of light in vacuum)
Network Overhead: 1.5-2x multiplier for routing

Formula: One-way latency = (Distance × 1.5) / 200,000 + Processing

Examples:
- NYC ↔ LA: 4,000 km → 30ms minimum
- NYC ↔ London: 5,600 km → 42ms minimum  
- NYC ↔ Sydney: 16,000 km → 120ms minimum
- Around the world: 40,000 km → 300ms minimum
```

### Latency Budget Worksheet

| Component | Typical Range | Your System | Notes |
|-----------|--------------|-------------|-------|
| **Network RTT** | 1-200ms | ___ms | Depends on distance |
| **DNS Lookup** | 1-100ms | ___ms | Can be cached |
| **TLS Handshake** | 10-200ms | ___ms | Reuse connections |
| **Load Balancer** | 1-5ms | ___ms | Layer 4 vs 7 |
| **API Gateway** | 5-20ms | ___ms | Auth, routing |
| **Service Mesh** | 1-5ms | ___ms | Per hop |
| **Database Query** | 1-1000ms | ___ms | Depends on query |
| **Serialization** | 1-50ms | ___ms | JSON vs Protocol Buffers |
| **Business Logic** | Variable | ___ms | Your code |
| **Total Budget** | **Target** | ___ms | Sum all components |

### Quick Latency Rules
- **Human Perception**: <100ms feels instant
- **Productivity Threshold**: <1s maintains flow
- **Attention Span**: <10s before frustration
- **SEO Impact**: >3s hurts rankings

---

## ⚖️ Capacity Planning Worksheet

**Apply Axiom 2: Size your finite boxes**

### Resource Calculator

```python
# Capacity Planning Formula
Required Capacity = (Peak Load × Safety Factor) / Utilization Target

Where:
- Peak Load = Avg Load × Peak-to-Average Ratio
- Safety Factor = 1.5-2x (for unexpected spikes)
- Utilization Target = 60-80% (leave headroom)

Example: E-commerce Site
- Average Load: 1000 req/s
- Peak-to-Average: 3x (during sales)
- Peak Load: 3000 req/s
- Safety Factor: 1.5x
- Target Utilization: 70%
- Required Capacity: (3000 × 1.5) / 0.7 = 6,428 req/s
```

### Server Sizing Matrix

| Workload Type | vCPUs | Memory | Storage | Network | Example Use Case |
|---------------|-------|---------|---------|---------|------------------|
| **Web Server** | 2-4 | 4-8 GB | 20 GB | 1 Gbps | Stateless APIs |
| **App Server** | 4-8 | 8-16 GB | 50 GB | 10 Gbps | Business logic |
| **Cache Server** | 4-8 | 16-64 GB | 100 GB | 10 Gbps | Redis, Memcached |
| **Database** | 8-32 | 32-256 GB | 1-10 TB | 10-25 Gbps | PostgreSQL, MySQL |
| **Analytics** | 16-64 | 64-512 GB | 10+ TB | 25 Gbps | Spark, Presto |
| **ML Training** | 8-96 + GPU | 64GB-1TB | 1-10 TB | 100 Gbps | TensorFlow, PyTorch |

### Storage Calculator

```text
Storage Needs = (Data per Day × Retention Days × Replication Factor) × (1 + Growth Rate)

Example: Logging System
- Log Volume: 100 GB/day
- Retention: 30 days
- Replication: 3x
- Growth Rate: 20% annually
- Base Need: 100 × 30 × 3 = 9 TB
- With Growth: 9 TB × 1.2 = 10.8 TB
- Add 50% Buffer: 16.2 TB recommended
```

---

## 💥 Failure Analysis Framework

**Apply Axiom 3: Plan for inevitable entropy**

### Failure Mode Scoring

| Failure Mode | Probability (1-5) | Impact (1-5) | Detection (1-5) | Risk Score | Priority |
|--------------|-------------------|--------------|-----------------|------------|----------|
| Server crash | ___ | ___ | ___ | P×I×D = ___ | ___ |
| Network partition | ___ | ___ | ___ | P×I×D = ___ | ___ |
| Database corruption | ___ | ___ | ___ | P×I×D = ___ | ___ |
| DDoS attack | ___ | ___ | ___ | P×I×D = ___ | ___ |
| Human error | ___ | ___ | ___ | P×I×D = ___ | ___ |
| Dependency failure | ___ | ___ | ___ | P×I×D = ___ | ___ |

**Scoring Guide**:
- **Probability**: 1=Rare, 5=Frequent
- **Impact**: 1=Minor, 5=Catastrophic
- **Detection**: 1=Obvious, 5=Hidden
- **Priority**: >50=Critical, 25-50=High, <25=Medium

### MTBF/MTTR Calculator

```text
Availability = MTBF / (MTBF + MTTR)

Where:
- MTBF = Mean Time Between Failures
- MTTR = Mean Time To Recovery

Availability Targets:
- 99% = 3.65 days/year downtime
- 99.9% = 8.76 hours/year
- 99.99% = 52.6 minutes/year
- 99.999% = 5.26 minutes/year

Required MTBF:
If MTTR = 1 hour, then:
- 99% availability needs MTBF = 99 hours
- 99.9% needs MTBF = 999 hours
- 99.99% needs MTBF = 9,999 hours
```

---

## 🎲 Concurrency Analysis Tools

**Apply Axiom 4: Model distributed timelines**

### Race Condition Detector

```python
# Concurrent Access Pattern Analyzer

Scenarios to Check:
□ Multiple writers to same resource
□ Read-modify-write without locking
□ Check-then-act patterns
□ Shared mutable state
□ Non-atomic operations
□ Missing happens-before relationships

Risk Matrix:
| Pattern | Risk Level | Mitigation |
|---------|------------|------------|
| Shared counter | High | Atomic operations |
| Config reload | Medium | Versioning |
| Cache invalidation | High | Distributed lock |
| Session state | Medium | Sticky sessions |
| File uploads | Low | Unique names |
```

### Deadlock Prevention Checklist

```text
Coffman Conditions (ALL must be true for deadlock):
□ Mutual Exclusion - Resources can't be shared
□ Hold and Wait - Process holds resource while waiting
□ No Preemption - Can't force resource release
□ Circular Wait - Circular chain of dependencies

Prevention Strategies:
- Resource Ordering ✓ (prevent circular wait)
- Timeouts ✓ (break hold and wait)
- Lock-free algorithms ✓ (no mutual exclusion)
- Deadlock detection ✓ (recovery mechanism)
```

---

## 🤝 Consensus Decision Matrix

**Apply Axiom 5: Choose coordination mechanisms**

### Consensus Algorithm Selector

| If You Need... | And You Have... | Consider... | Trade-offs |
|----------------|-----------------|-------------|------------|
| **Strong consistency** | 3-7 nodes | Raft | Simple but leader-based |
| **Byzantine tolerance** | Untrusted nodes | PBFT | Complex, slow |
| **High throughput** | Many readers | Chain replication | Eventual consistency |
| **Geo-distribution** | Global deployment | Multi-Paxos | Complex operations |
| **Simple operations** | Key-value only | Consistent hashing | No transactions |
| **No coordination** | Commutative ops | CRDTs | Limited operations |

### Quorum Calculator

```text
Quorum Sizes for N nodes:

Read Quorum (R) + Write Quorum (W) > N

Common Configurations:
- Strong Consistency: R = W = (N/2) + 1
- Read Heavy: R = 1, W = N
- Write Heavy: R = N, W = 1
- Balanced: R = W = (N+1)/2

Examples for N=5:
- Strong: R=3, W=3 (tolerates 2 failures)
- Read Optimized: R=1, W=5 (fast reads)
- Write Optimized: R=5, W=1 (fast writes)
```

---

## 👁️ Observability Metrics Dashboard

**Apply Axiom 6: Instrument for knowledge**

### Golden Signals Calculator

```text
The Four Golden Signals:

1. Latency
   - P50: ___ms (typical experience)
   - P95: ___ms (slower users)
   - P99: ___ms (worst case)
   - Target SLO: ___ms

2. Traffic  
   - Current: ___ req/s
   - Peak: ___ req/s
   - Growth rate: ___% monthly

3. Errors
   - Rate: ___% 
   - Threshold: ___% 
   - Types: [4xx: ___%] [5xx: ___%]

4. Saturation
   - CPU: ___%
   - Memory: ___%
   - Disk I/O: ___%
   - Network: ___%
```

### Alert Design Worksheet

| Metric | Threshold | Duration | Severity | Action | Owner |
|--------|-----------|----------|----------|--------|-------|
| API Latency P99 | >500ms | 5 min | Warning | Check load | SRE |
| Error Rate | >1% | 2 min | Critical | Page on-call | SRE |
| CPU Usage | >80% | 10 min | Warning | Scale up | Platform |
| Disk Space | <10% | - | Critical | Clean up | Platform |
| Queue Depth | >1000 | 5 min | Warning | Add workers | App |

---

## 👤 Human Interface Assessment

**Apply Axiom 7: Design the organic API**

### Cognitive Load Scorer

```text
Rate each factor (1-5, where 5 = high load):

Information Density:
□ Number of items on screen: ___
□ Depth of navigation: ___
□ Technical jargon used: ___
□ Required mental model complexity: ___

Decision Complexity:
□ Number of choices presented: ___
□ Irreversibility of actions: ___
□ Dependencies between choices: ___
□ Time pressure: ___

Total Score: ___/40
- <10: Well designed
- 10-20: Acceptable
- 20-30: Needs improvement
- >30: Redesign required
```

### Runbook Quality Checklist

```text
Essential Elements:
□ Clear trigger conditions
□ Step-by-step instructions
□ Copy-pasteable commands
□ Decision trees for variations
□ Rollback procedures
□ Success criteria
□ Escalation paths
□ Time estimates

Quality Metrics:
□ Can be followed at 3 AM?
□ No assumed knowledge?
□ All links working?
□ Recently tested?
□ Peer reviewed?
```

---

## 💰 Cost Calculator

**Apply Axiom 8: Optimize cost at scale**

### Cloud Cost Estimator

```python
# Monthly Cost Calculator

Compute:
- Instance Type: _______
- Quantity: ___ instances
- Hours/month: ___ (max 730)
- Reserved? □ Yes (___% discount)
- Spot? □ Yes (___% discount)
- Subtotal: $____

Storage:
- Type: □ SSD □ HDD □ Object
- Size: ___ GB
- Operations: ___ million/month
- Transfer OUT: ___ GB
- Subtotal: $____

Network:
- Data Transfer: ___ GB
- Regions: □ Same □ Cross
- Load Balancer: □ Yes
- Subtotal: $____

Total Monthly: $____
Annual (12x): $____
With Growth (20%): $____
```

### Build vs Buy Calculator

| Factor | Build | Buy | Winner |
|--------|-------|-----|--------|
| **Initial Cost** | $___ | $___ | ___ |
| **Monthly OpEx** | $___ | $___ | ___ |
| **Dev Time** | ___ months | ___ weeks | ___ |
| **Maintenance** | ___ hrs/month | ___ hrs/month | ___ |
| **Customization** | ___/10 | ___/10 | ___ |
| **5-Year TCO** | $___ | $___ | ___ |

**Decision**: □ Build □ Buy

---

## 🏗️ Architecture Decision Records (ADRs)

**Apply All Axioms: Document trade-offs**

### ADR Template

```markdown
# ADR-001: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative  
- Drawback 1
- Drawback 2

### Neutral
- Side effect 1
- Side effect 2

## Axioms Applied
- Axiom 1 (Latency): How does this affect speed?
- Axiom 2 (Capacity): How does this affect resources?
- Axiom 3 (Failure): How does this handle failures?
- [Continue for relevant axioms...]
```

---

## 🎯 Quick Decision Frameworks

**Rapid architectural guidance**

### Database Selection Matrix

| If You Have... | Consider... | Because... |
|----------------|-------------|------------|
| <1GB, ACID needed | PostgreSQL | Best of both worlds |
| >1TB, analytics | Columnar (Parquet) | Compression & speed |
| Key-value, <ms latency | Redis | In-memory speed |
| Documents, flexible | MongoDB | Schema flexibility |
| Time series | InfluxDB | Optimized for time |
| Graph relationships | Neo4j | Graph algorithms |
| Global scale | DynamoDB | Managed, scalable |

### Caching Strategy Selector

```text
Decision Tree:
Is data user-specific?
├─ Yes → Session/local cache
└─ No → Is it expensive to compute?
    ├─ Yes → Application cache (Redis)
    └─ No → Is it static content?
        ├─ Yes → CDN
        └─ No → Maybe don't cache
```

---

## 📚 Reference Quick Cards

**Essential formulas and rules of thumb**

### Little's Law
```math
L = λ × W
- L = Items in system
- λ = Arrival rate
- W = Time in system
```

### Amdahl's Law
```math
Speedup = 1 / (S + P/N)
- S = Serial fraction
- P = Parallel fraction  
- N = Number of processors
```

### Network Bandwidth
```math
Bandwidth (Mbps) = File Size (MB) × 8 / Time (seconds)
Time = Distance (km) / 200,000 km/s + Processing
```

### Storage IOPS
```math
IOPS = 1000 / (Seek Time + Latency)
Throughput = IOPS × Block Size
```

### Availability Math
```math
Serial: A = A₁ × A₂ × ... × Aₙ
Parallel: A = 1 - (1-A₁) × (1-A₂) × ... × (1-Aₙ)
```

---

*"The best tools amplify human judgment rather than replace it. Use these calculators as starting points, not final answers."*