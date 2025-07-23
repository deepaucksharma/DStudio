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
[Home](../index.md) → [Reference](index.md) → **Distributed Systems Cheat Sheets**

# Distributed Systems Cheat Sheets

---

## 🧮 Essential Calculations

### Little's Law
`L = λW`
- L: Average number in system
- λ: Arrival rate (req/s)
- W: Average time in system (s)

**Example**: 100 req/s × 0.5s = 50 concurrent requests

---

### Availability Math

`Availability = MTBF / (MTBF + MTTR)`

**SLA Targets**:
| Availability | Downtime/Year | Downtime/Month | Use Case |
|--------------|---------------|----------------|----------|
| 90% | 36.53 days | 73 hours | Internal tools |
| 99% | 3.65 days | 7.31 hours | Standard services |
| 99.9% | 8.77 hours | 43.8 minutes | Production services |
| 99.99% | 52.6 minutes | 4.38 minutes | Critical services |
| 99.999% | 5.26 minutes | 26.3 seconds | Mission critical |

**Parallel**: `A_total = 1 - (1 - A₁)(1 - A₂)...(1 - Aₙ)`
**Series**: `A_total = A₁ × A₂ × ... × Aₙ`

---

### Latency Budget Planning

**Speed of Light**:
- NYC ↔ SF: 21ms (4,000km)
- NYC ↔ London: 28ms (5,600km)
- NYC ↔ Tokyo: 67ms (10,800km)
- Satellite: 240ms (round trip)

**200ms Budget Example**:
- Network: 60ms (30%)
- Load balancer: 10ms
- Application: 50ms (25%)
- Database: 60ms (30%)
- Buffer: 20ms (10%)

---

### Capacity Planning

**M/M/1 Queue**:
- Utilization: `ρ = λ/μ`
- Queue length: `L = ρ/(1-ρ)`
- Wait time: `W = ρ/[μ(1-ρ)]`

**Keep utilization < 80%**

**Scaling**: Linear O(n), Database O(n log n), Coordination O(n²)

---

## 🎯 Decision Trees

### Consistency Model Selection

```text
Need strong consistency?
├─ YES → Financial/Safety Critical
│   ├─ Single region? → ACID database
│   └─ Multi-region? → Consensus (Raft/Paxos)
│       └─ Consider Law 4: Multidimensional Optimization ⚖️
└─ NO → Can tolerate eventual consistency?
    ├─ YES →
    │   ├─ Conflict resolution needed? → CRDTs
    │   └─ Simple case? → Last-write-wins
    │       └─ See Law 2: Asynchronous Reality ⏳
    └─ NO → Causal consistency
```

### Pattern Selection

**Law 2 (Asynchronous Reality ⏳)**: Caching, Edge Computing, Circuit Breaker, Async Processing

**Law 1 (Correlated Failure ⛓️)**: Retry+Backoff, Circuit Breaker, Bulkhead, Health Checks

**Law 3 (Emergent Chaos 🌪️)**: Sharding, Load Balancing, Caching, Async Processing

**Law 4 (Multidimensional Optimization ⚖️)**: Event Sourcing, CQRS, Saga, Outbox

---

## 📊 Performance Baselines

### Latency Reference

**Memory**: L1 0.5ns, L2 7ns, RAM 100ns, SSD 150μs, HDD 10ms

**Network**: Same DC 0.5ms, Cross-AZ 1-5ms, Cross-region 50-200ms

**Database**: KV lookup 1ms, Indexed query 10ms, Scan 100ms+, Commit 10ms

### Throughput Baselines

**Network**: 1G 125MB/s, 10G 1.25GB/s, Internet 10-100Mbps

**Storage**: HDD 100MB/s, SSD 500MB/s, NVMe 3GB/s, RAM 50GB/s

**CPU**: Hash 1M/s, JSON 100K/s, Crypto 10K/s

---

## 🛠️ Configuration Templates

### Circuit Breaker Settings

**Conservative**: failure_threshold: 5, timeout: 30s, recovery: 60s

**Aggressive**: failure_threshold: 10, timeout: 10s, recovery: 30s

### Retry Configuration

**Exponential**: 100ms initial, 2x multiplier, 30s max, 25% jitter

**Linear**: 500ms initial, 500ms increment, 10s max

### Timeouts

**Service Calls**: DB 1-5s, External API 10-30s, Internal 100ms-1s

**Connections**: TCP 3-10s, HTTP 30s, DB connection 5-30s

---

## 📈 Monitoring Thresholds

### Golden Signals

**Latency**: P50 <100ms, P95 <500ms, P99 <1s

**Throughput**: Alert on >20% deviation

**Errors**: Critical <0.1%, Standard <1%, Experimental <5%

**Saturation**: CPU <70%, Memory <80%, Disk <85%, Network <70%

### Alert Levels

**Critical**: Service down, Errors >5%, Latency >5x baseline

**Warning**: Errors >1%, Latency >2x baseline, Resources >80%

**Info**: Capacity trends, Performance degradation

---

## 🔄 Incident Response

### Incident Response

**Triage**: Scope? Impact? Timeline? Trend? Recent changes?

**Severity**: S1 Complete outage, S2 Major feature, S3 Minor feature, S4 Cosmetic

**Template**: Status: [STATE] | Impact: [DESC] | Actions: [DOING] | Next: [TIME]

---

## 🎯 Testing Strategies

### Testing Strategies

**Chaos**: Kill instances, Add latency, Fail dependencies, Network partitions, Resource exhaustion

**Load**: Baseline (1x), Peak (2-3x), Spike (10x), Soak (extended), Failure (with outages)

---

