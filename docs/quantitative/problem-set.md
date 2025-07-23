---
title: Numerical Problem Set
description: Practice problems with real-world parameters
type: quantitative
difficulty: advanced
reading_time: 10 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../introduction/index.md) → [Part IV: Quantitative](index.md) → **Numerical Problem Set**

# Numerical Problem Set

**Practice problems with real-world parameters**

## Problem 1: API Gateway Sizing

**Given:**
- Expected traffic: 50,000 requests/second
- Response time target: < 100ms (p99)
- Each request: 10KB in, 50KB out
- Processing time: 5ms CPU per request

**Calculate:**
a) Minimum servers needed
b) Network bandwidth required
c) Connection pool size
d) Monthly data transfer cost ($0.09/GB)

<details>
<summary>Solution</summary>

a) **Minimum servers needed:**
- CPU time per request: 5ms
- Requests per CPU per second: 1000ms/5ms = 200
- Total CPUs needed: 50,000/200 = 250 CPUs
- With 8 CPUs per server: 250/8 = 32 servers
- Add 40% safety margin: 32 × 1.4 = 45 servers

b) **Network bandwidth required:**
- Inbound: 50,000 × 10KB = 500MB/s = 4Gbps
- Outbound: 50,000 × 50KB = 2,500MB/s = 20Gbps
- Total: 24Gbps minimum, provision 30Gbps

c) **Connection pool size:**
- Apply Little's Law: L = λ × W
- λ = 50,000 req/s
- W = 0.1s (response time)
- L = 50,000 × 0.1 = 5,000 concurrent connections
- Per server: 5,000/45 ≈ 111 connections

d) **Monthly data transfer cost:**
- Daily outbound: 2.5GB/s × 86,400s = 216TB
- Monthly: 216TB × 30 = 6,480TB
- Cost: 6,480TB × $0.09/GB = $583,200/month
</details>

## Problem 2: Cache Hit Rate Economics

**Given:**
- Database query cost: $0.001 per query
- Cache infrastructure: $2,000/month
- Traffic: 100M queries/month
- Cache capacity: 10M entries
- Query distribution: Zipfian (80/20 rule)

**Calculate:**
a) Break-even hit rate
b) Expected hit rate with LRU
c) Monthly savings
d) Optimal cache size

<details>
<summary>Solution</summary>

a) **Break-even hit rate:**
- Cache cost: $2,000/month
- Cost per saved query: $0.001
- Queries to save: $2,000/$0.001 = 2M
- Break-even rate: 2M/100M = 2%

b) **Expected hit rate with LRU:**
- 80/20 rule: 20% of queries access 80% of data
- 20M unique queries access 10M entries (cache size)
- These represent 80% of traffic
- Hit rate ≈ 80%

c) **Monthly savings:**
- Queries saved: 100M × 0.8 = 80M
- Savings: 80M × $0.001 = $80,000
- Net savings: $80,000 - $2,000 = $78,000/month

d) **Optimal cache size:**
- Current: 10M entries → 80% hit rate
- Diminishing returns beyond covering hot set
- 15M entries → ~85% hit rate (+5%)
- Additional savings: 5M × $0.001 = $5,000
- If extra 5M entries cost < $5,000, expand
</details>

## Problem 3: Distributed Consensus Latency

**Given:**
- 5 nodes across 3 regions
- Region latencies:
  - US-East ↔ US-West: 70ms
  - US ↔ Europe: 120ms
  - Europe ↔ Asia: 180ms
- Paxos protocol (2 rounds)

**Calculate:**
a) Best-case consensus time
b) Worst-case consensus time
c) Expected time (uniform leader)
d) Optimal leader placement

<details>
<summary>Solution</summary>

a) **Best-case consensus time:**
- Leader in US-East, majority in US
- Round 1: US-East → US-West = 70ms
- Round 2: US-West → US-East = 70ms
- Total: 140ms

b) **Worst-case consensus time:**
- Leader in Asia, needs Europe + one US
- Round 1: Asia → Europe = 180ms
- Round 2: Europe → Asia = 180ms
- Total: 360ms

c) **Expected time (uniform leader):**
- P(US leader) = 3/5, time = 140-240ms
- P(EU leader) = 1/5, time = 240ms
- P(Asia leader) = 1/5, time = 360ms
- Expected: 0.6×190 + 0.2×240 + 0.2×360 = 234ms

d) **Optimal leader placement:**
- US-East minimizes maximum latency
- Worst case becomes US-East ↔ Asia = 290ms
- Better than Asia leader's 360ms
</details>

## Problem 4: Queue Depth Under Load

**Given:**
- Arrival rate: λ = 1000 req/s (Poisson)
- Service rate: μ = 1200 req/s (exponential)
- System starts empty

**Calculate:**
a) Steady-state queue length
b) 95th percentile queue length
c) Probability queue > 100
d) Time to reach steady state

<details>
<summary>Solution</summary>

a) **Steady-state queue length:**
- ρ = λ/μ = 1000/1200 = 0.833
- Lq = ρ²/(1-ρ) = 0.694/0.167 = 4.15

b) **95th percentile queue length:**
- For M/M/1: P(N > n) = ρ^(n+1)
- Need n where ρ^(n+1) = 0.05
- (0.833)^(n+1) = 0.05
- n = 15 (95th percentile)

c) **Probability queue > 100:**
- P(N > 100) = ρ^101 = 0.833^101
- = 1.1 × 10^-8 (extremely rare)

d) **Time to reach steady state:**
- Rule of thumb: 3/(μ-λ) = 3/200 = 15ms
- System reaches steady state very quickly
</details>

## Problem 5: Multi-Region Availability

**Given:**
- 3 regions: US (99.9%), EU (99.8%), Asia (99.7%)
- Application requires 2 regions operational
- Inter-region replication: 99.5% reliable

**Calculate:**
a) System availability
b) Monthly downtime expectation
c) Probability of total failure
d) Cost/benefit of 4th region

<details>
<summary>Solution</summary>

a) **System availability:**
- Need 2 of 3 regions working
- P(all 3 up) = 0.999 × 0.998 × 0.997 = 0.994
- P(exactly 2 up) = 3 × [0.999×0.998×0.003 + similar] = 0.00588
- P(at least 2 up) = 0.994 + 0.00588 = 0.99988 = 99.988%

b) **Monthly downtime:**
- Availability: 99.988%
- Downtime: 0.012% × 43,200 min = 5.2 minutes/month

c) **Probability of total failure:**
- All regions down: 0.001 × 0.002 × 0.003 = 6 × 10^-9
- Once per 166 million months

d) **Cost/benefit of 4th region:**
- New availability: ~99.9997% (need 2 of 4)
- Improvement: 5.2 min → 1.3 min/month
- If 4 min/month downtime costs > region cost, justified
</details>

## Problem 6: Sharding Overhead

**Given:**
- Data size: 10TB
- Single node capacity: 500GB
- Query types:
  - Single key: 70%
  - Range scan: 20%
  - Full scan: 10%
- Cross-shard overhead: 10ms

**Calculate:**
a) Minimum shards needed
b) Expected query latency increase
c) Network traffic multiplier
d) Optimal shard key selection

<details>
<summary>Solution</summary>

a) **Minimum shards needed:**
- 10TB / 500GB = 20 shards minimum
- Add 20% headroom: 24 shards

b) **Expected query latency increase:**
- Single key: No overhead (70%)
- Range scan: Hits ~5 shards avg = 10ms (20%)
- Full scan: Hits all 24 = 10ms (10%)
- Expected: 0.7×0 + 0.2×10 + 0.1×10 = 3ms

c) **Network traffic multiplier:**
- Single key: 1x (70%)
- Range scan: 5x average (20%)
- Full scan: 24x (10%)
- Expected: 0.7×1 + 0.2×5 + 0.1×24 = 4.1x

d) **Optimal shard key selection:**
- High cardinality (user_id good, country bad)
- Aligns with access patterns
- Minimizes range scans across shards
- Consider: user_id, timestamp, or composite
</details>

## Problem 7: Autoscaling Economics

**Given:**
- Base load: 100 instances
- Peak load: 500 instances (2 hours/day)
- On-demand: $0.10/hour
- Reserved: $0.06/hour (1-year)
- Spot: $0.03/hour (90% availability)

**Calculate:**
a) Optimal instance mix
b) Monthly cost comparison
c) Availability impact
d) Break-even utilization

<details>
<summary>Solution</summary>

a) **Optimal instance mix:**
- Reserved: 100 (base load)
- On-demand: 50 (buffer)
- Spot: 350 (peak, can tolerate 10% interruption)

b) **Monthly cost comparison:**
- All on-demand: 100×730×$0.10 + 400×60×$0.10 = $9,700
- Optimized: 100×730×$0.06 + 50×60×$0.10 + 350×60×$0.03 = $5,410
- Savings: $4,290/month (44%)

c) **Availability impact:**
- 10% spot interruption × 350 instances = 35 instances
- During peak: 465/500 = 93% capacity
- Acceptable if load balancer distributes well

d) **Break-even utilization:**
- Reserved vs on-demand: $0.06/$0.10 = 60%
- Need 60% utilization to justify reserved
- Base load is 100/500 = 20% of peak
- But runs 24/7, so justified
</details>

## Problem 8: Little's Law Application

**Given:**
- E-commerce checkout flow
- 10,000 concurrent users
- 5 pages × 2 seconds each
- 30% abandon at each step

**Calculate:**
a) Required system throughput
b) Memory for session storage
c) Database connection needs
d) Revenue impact of -1 second

<details>
<summary>Solution</summary>

a) **Required system throughput:**
- Average time in system: 5 × 2 = 10 seconds
- But with abandonment: 2 + 0.7×2 + 0.49×2 + 0.343×2 + 0.24×2 = 5.57s
- L = λW, so λ = L/W = 10,000/5.57 = 1,795 users/second entering

b) **Memory for session storage:**
- Concurrent sessions: 10,000
- Session size: ~50KB typical
- Memory: 10,000 × 50KB = 500MB
- Add overhead: 750MB total

c) **Database connection needs:**
- DB operations per page: 3
- Completion rate per page: [1, 0.7, 0.49, 0.343, 0.24]
- Total DB ops/user: 3×(1+0.7+0.49+0.343+0.24) = 8.35
- DB ops/sec: 1,795 × 8.35 / 5.57 = 2,690
- Query time: 20ms
- Connections: 2,690 × 0.02 = 54 connections

d) **Revenue impact of -1 second:**
- Faster → less abandonment
- New time: 4.57s
- New λ: 10,000/4.57 = 2,188 users/s
- Increase: 393 more users/s completing
- If conversion = 2.4% × $100 AOV
- Revenue increase: 393 × 0.024 × $100 = $943/second
</details>

## Problem 9: Circuit Breaker Tuning

**Given:**
- Service SLA: 99.9% success rate
- Normal failure rate: 0.1%
- Failure detection window: 10 seconds
- Recovery probe interval: 30 seconds

**Calculate:**
a) Optimal failure threshold
b) Expected false positives/day
c) Availability impact
d) Mean time to recovery

<details>
<summary>Solution</summary>

a) **Optimal failure threshold:**
- Expected failures in 10s: 0.001 × requests_in_10s
- Use 5σ rule: threshold = mean + 5×√mean
- At 100 req/s: mean = 1, threshold = 6
- At 1000 req/s: mean = 10, threshold = 26

b) **Expected false positives/day:**
- P(false positive) ≈ 10^-6 (5σ)
- Windows per day: 8,640
- False positives: 0.0086/day ≈ 1 per 116 days

c) **Availability impact:**
- Circuit open duration: 30s
- False positive impact: 30s/month
- = 0.0012% availability loss
- New availability: 99.9% - 0.0012% = 99.8988%

d) **Mean time to recovery:**
- Detection time: 10s (worst case)
- Circuit open: 30s
- Half-open test: ~1s
- Total MTTR: 41s
</details>

## Problem 10: Capacity Planning

**Given:**
- Current: 1M daily active users
- Growth: 25% monthly
- Peak ratio: 5x average
- Per-user: 10 requests/minute peak
- Server capacity: 1000 requests/second

**Calculate:**
a) 6-month server needs
b) Database growth projection
c) Bandwidth requirements
d) Architecture change trigger

<details>
<summary>Solution</summary>

a) **6-month server needs:**
- Users in 6 months: 1M × 1.25^6 = 3.8M
- Peak concurrent: 3.8M × 0.2 = 760K (20% concurrency)
- Requests/second: 760K × 10/60 = 126K req/s
- Servers needed: 126K/1K = 126 servers
- With 40% margin: 177 servers

b) **Database growth projection:**
- Data per user: 10MB typical
- Current: 1M × 10MB = 10TB
- 6 months: 3.8M × 10MB = 38TB
- Plus historical data: ~50TB total
- Need sharding beyond 20TB

c) **Bandwidth requirements:**
- Request size: 5KB average
- Response size: 50KB average
- Peak bandwidth: 126K × 55KB = 6.9GB/s
- = 55.2 Gbps
- Provision: 70 Gbps

d) **Architecture change trigger:**
- Month 4: 2.4M users, 80 servers
- Month 5: 3.1M users, 103 servers
- Database hits 25TB limit
- Trigger: Begin sharding in month 4
</details>

## Key Patterns from Problems

1. **Little's Law appears everywhere** (connections, queues, sessions)
2. **Safety margins matter** (40% CPU, 50% network typical)
3. **Growth is exponential** (compounds faster than expected)
4. **Architecture breaks before resources** (plan transitions early)
5. **Cost optimization has huge impact** (40-60% savings common)
