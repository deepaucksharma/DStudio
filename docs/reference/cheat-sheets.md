---
title: Distributed Systems Cheat Sheets
description: Quick reference guides for calculations, decisions, and common patterns.
type: reference
difficulty: advanced
reading_time: 15 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Reference](/reference/) → **Distributed Systems Cheat Sheets**


# Distributed Systems Cheat Sheets

Quick reference guides for calculations, decisions, and common patterns.

---

## 🧮 Essential Calculations

### Little's Law
**Formula**: `L = λW`
- **L**: Average number in system
- **λ**: Arrival rate (requests/second)  
- **W**: Average time in system (seconds)

**Example**: 100 req/s × 0.5s = 50 concurrent requests

**Usage**: Capacity planning, queue analysis

---

### Availability Math

**Formula**: `Availability = MTBF / (MTBF + MTTR)`

**Common SLA Targets**:
| Availability | Downtime/Year | Downtime/Month | Use Case |
|--------------|---------------|----------------|----------|
| 90% | 36.53 days | 73 hours | Internal tools |
| 99% | 3.65 days | 7.31 hours | Standard services |
| 99.9% | 8.77 hours | 43.8 minutes | Production services |
| 99.99% | 52.6 minutes | 4.38 minutes | Critical services |
| 99.999% | 5.26 minutes | 26.3 seconds | Mission critical |

**Parallel Systems**: `A_total = 1 - (1 - A₁)(1 - A₂)...(1 - Aₙ)`

**Series Systems**: `A_total = A₁ × A₂ × ... × Aₙ`

---

### Latency Budget Planning

**Speed of Light Limits**:
- NYC ↔ SF: 21ms minimum (4,000km)
- NYC ↔ London: 28ms minimum (5,600km)  
- NYC ↔ Tokyo: 67ms minimum (10,800km)
- Satellite (GEO): 240ms minimum (round trip)

**Budget Allocation Rules**:
- User perception: <100ms feels instant
- Network: 30-50% of budget
- Processing: 20-40% of budget
- Database: 20-30% of budget
- Buffer: 10-20% for variance

**Example 200ms Budget**:
- Network: 60ms
- Load balancer: 10ms
- Application: 50ms
- Database: 60ms
- Buffer: 20ms

---

### Capacity Planning Formulas

**Queueing (M/M/1)**:
- Utilization: `ρ = λ/μ`
- Average queue length: `L = ρ/(1-ρ)`
- Average wait time: `W = ρ/[μ(1-ρ)]`

**Rule of Thumb**: Keep utilization < 80% for good performance

**Scaling Estimates**:
- Linear: Cost = O(n)
- Database: Cost = O(n log n) 
- Coordination: Cost = O(n²)

---

## 🎯 Decision Trees

### Consistency Model Selection

```text
Need strong consistency?
├─ YES → Financial/Safety Critical
│   ├─ Single region? → ACID database
│   └─ Multi-region? → Consensus (Raft/Paxos)
└─ NO → Can tolerate eventual consistency?
    ├─ YES → 
    │   ├─ Conflict resolution needed? → CRDTs
    │   └─ Simple case? → Last-write-wins
    └─ NO → Causal consistency
```

### Pattern Selection Guide

**For Latency Problems**:
1. **Caching** - Store results closer to users
2. **Edge Computing** - Process closer to users  
3. **Circuit Breaker** - Fail fast when slow
4. **Async Processing** - Don't wait for slow operations

**For Reliability Problems**:
1. **Retry with Backoff** - Handle transient failures
2. **Circuit Breaker** - Prevent cascade failures
3. **Bulkhead** - Isolate failure domains
4. **Health Checks** - Detect failures quickly

**For Scale Problems**:
1. **Sharding** - Distribute data
2. **Load Balancing** - Distribute requests
3. **Caching** - Reduce backend load
4. **Async Processing** - Smooth load spikes

**For Consistency Problems**:
1. **Event Sourcing** - Audit trail needed
2. **CQRS** - Different read/write requirements
3. **Saga** - Cross-service transactions
4. **Outbox** - Reliable event publishing

---

## 📊 Performance Baselines

### Latency Reference Points

**Memory/Storage Access**:
- L1 cache: 0.5ns
- L2 cache: 7ns
- RAM: 100ns
- SSD: 150μs
- HDD: 10ms

**Network Calls**:
- Same datacenter: 0.5ms
- Cross-AZ: 1-5ms
- Cross-region: 50-200ms
- Cross-continent: 100-300ms

**Database Operations**:
- Key-value lookup: 1ms
- SQL query (indexed): 10ms
- SQL query (scan): 100ms+
- Transaction commit: 10ms

### Throughput Baselines

**Network**:
- Gigabit ethernet: 125 MB/s
- 10G ethernet: 1.25 GB/s
- Internet (typical): 10-100 Mbps

**Storage**:
- HDD sequential: 100 MB/s
- SSD sequential: 500 MB/s
- NVMe SSD: 3 GB/s
- RAM: 50 GB/s

**CPU**:
- Hash calculation: 1M ops/sec
- JSON parsing: 100K ops/sec
- Crypto operations: 10K ops/sec

---

## 🛠️ Configuration Templates

### Circuit Breaker Settings

**Conservative (Financial)**:
```yaml
failure_threshold: 5
timeout: 30s
recovery_timeout: 60s
success_threshold: 3
```

**Aggressive (Non-critical)**:
```yaml
failure_threshold: 10
timeout: 10s
recovery_timeout: 30s
success_threshold: 5
```

### Retry Configuration

**Exponential Backoff**:
```yaml
initial_delay: 100ms
max_delay: 30s
multiplier: 2.0
jitter: 25%
max_attempts: 5
```

**Linear Backoff**:
```yaml
initial_delay: 500ms
increment: 500ms
max_delay: 10s
max_attempts: 3
```

### Timeout Settings

**Service Call Timeouts**:
- Database: 1-5s
- External API: 10-30s
- Internal service: 100ms-1s
- File operations: 30s-5min

**Connection Timeouts**:
- TCP connect: 3-10s
- HTTP request: 30s
- Database connection: 5-30s

---

## 📈 Monitoring Thresholds

### Golden Signals

**Latency**:
- P50 < 100ms
- P95 < 500ms
- P99 < 1s

**Throughput**:
- Track trends, not absolutes
- Alert on >20% deviation

**Error Rate**:
- <0.1% for critical services
- <1% for standard services
- <5% for experimental features

**Saturation**:
- CPU: <70% average
- Memory: <80% used
- Disk: <85% used
- Network: <70% capacity

### Alert Levels

**Critical (Page immediately)**:
- Service down
- Error rate >5%
- Latency P95 >5x baseline

**Warning (Next business day)**:
- Error rate >1%
- Latency P95 >2x baseline
- Resource usage >80%

**Info (Weekly review)**:
- Capacity trending
- Performance degradation
- Usage patterns

---

## 🔄 Incident Response

### Triage Questions
1. **Scope**: How many users affected?
2. **Impact**: What functionality is broken?
3. **Timeline**: When did it start?
4. **Trend**: Getting better or worse?
5. **Recent Changes**: Any deployments/config changes?

### Escalation Criteria
- **Severity 1**: Complete service outage
- **Severity 2**: Major feature broken
- **Severity 3**: Minor feature broken
- **Severity 4**: Cosmetic/performance issue

### Communication Template
```text
Status: [INVESTIGATING/IDENTIFIED/MONITORING/RESOLVED]
Impact: [brief description]
Current Actions: [what we're doing]
Next Update: [when we'll update again]
```

---

## 🎯 Testing Strategies

### Chaos Engineering Targets
1. **Kill instances** - Test auto-scaling
2. **Introduce latency** - Test timeouts
3. **Fail dependencies** - Test circuit breakers
4. **Network partitions** - Test split-brain handling
5. **Resource exhaustion** - Test backpressure

### Load Testing Scenarios
1. **Baseline** - Normal traffic patterns
2. **Peak** - 2-3x normal load
3. **Spike** - 10x sudden increase
4. **Soak** - Extended high load
5. **Failure** - Load during failures

---

*These cheat sheets provide quick reference for common calculations and decisions in distributed systems design and operations.*
