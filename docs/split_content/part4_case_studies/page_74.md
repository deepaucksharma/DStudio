Page 74: Numerical Problem Set
Practice problems with real-world parameters
PROBLEM 1: API Gateway Sizing
Given:
- Expected traffic: 50,000 requests/second
- Response time target: < 100ms (p99)
- Each request: 10KB in, 50KB out
- Processing time: 5ms CPU per request

Calculate:
a) Minimum servers needed
b) Network bandwidth required
c) Connection pool size
d) Monthly data transfer cost ($0.09/GB)

[Solution on page 98]
PROBLEM 2: Cache Hit Rate Economics
Given:
- Database query cost: $0.001 per query
- Cache infrastructure: $2,000/month
- Traffic: 100M queries/month
- Cache capacity: 10M entries
- Query distribution: Zipfian (80/20 rule)

Calculate:
a) Break-even hit rate
b) Expected hit rate with LRU
c) Monthly savings
d) Optimal cache size

[Solution on page 98]
PROBLEM 3: Distributed Consensus Latency
Given:
- 5 nodes across 3 regions
- Region latencies:
  - US-East ↔ US-West: 70ms
  - US ↔ Europe: 120ms
  - Europe ↔ Asia: 180ms
- Paxos protocol (2 rounds)

Calculate:
a) Best-case consensus time
b) Worst-case consensus time
c) Expected time (uniform leader)
d) Optimal leader placement

[Solution on page 98]
PROBLEM 4: Queue Depth Under Load
Given:
- Arrival rate: λ = 1000 req/s (Poisson)
- Service rate: μ = 1200 req/s (exponential)
- System starts empty

Calculate:
a) Steady-state queue length
b) 95th percentile queue length
c) Probability queue > 100
d) Time to reach steady state

[Solution on page 98]
PROBLEM 5: Multi-Region Availability
Given:
- 3 regions: US (99.9%), EU (99.8%), Asia (99.7%)
- Application requires 2 regions operational
- Inter-region replication: 99.5% reliable

Calculate:
a) System availability
b) Monthly downtime expectation
c) Probability of total failure
d) Cost/benefit of 4th region

[Solution on page 98]
PROBLEM 6: Sharding Overhead
Given:
- Data size: 10TB
- Single node capacity: 500GB
- Query types:
  - Single key: 70%
  - Range scan: 20%
  - Full scan: 10%
- Cross-shard overhead: 10ms

Calculate:
a) Minimum shards needed
b) Expected query latency increase
c) Network traffic multiplier
d) Optimal shard key selection

[Solution on page 98]
PROBLEM 7: Autoscaling Economics
Given:
- Base load: 100 instances
- Peak load: 500 instances (2 hours/day)
- On-demand: $0.10/hour
- Reserved: $0.06/hour (1-year)
- Spot: $0.03/hour (90% availability)

Calculate:
a) Optimal instance mix
b) Monthly cost comparison
c) Availability impact
d) Break-even utilization

[Solution on page 98]
PROBLEM 8: Little's Law Application
Given:
- E-commerce checkout flow
- 10,000 concurrent users
- 5 pages × 2 seconds each
- 30% abandon at each step

Calculate:
a) Required system throughput
b) Memory for session storage
c) Database connection needs
d) Revenue impact of -1 second

[Solution on page 98]
PROBLEM 9: Circuit Breaker Tuning
Given:
- Service SLA: 99.9% success rate
- Normal failure rate: 0.1%
- Failure detection window: 10 seconds
- Recovery probe interval: 30 seconds

Calculate:
a) Optimal failure threshold
b) Expected false positives/day
c) Availability impact
d) Mean time to recovery

[Solution on page 98]
PROBLEM 10: Capacity Planning
Given:
- Current: 1M daily active users
- Growth: 25% monthly
- Peak ratio: 5x average
- Per-user: 10 requests/minute peak
- Server capacity: 1000 requests/second

Calculate:
a) 6-month server needs
b) Database growth projection
c) Bandwidth requirements
d) Architecture change trigger

[Solution on page 98]

Part V Preview: Human & Operational Factors
Pure math and patterns aren't enough. Systems are built, operated, and debugged by humans. Part V explores:

Tuning consistency in production
Chaos engineering practices
Building observable systems
SRE principles that work
Organizational physics
Runbook excellence

Where the silicon meets the soul...RetryDcontinueEdit2 / 2Mapped out comprehensive plan for remaining document sections.4sThe user wants me to continue with Part V: Human & Operational Factors (pages 75-80), then Part VI: Case Studies (pages 81-90), Part VII: Active Learning & Capstone (pages 91-95), and Part VIII: Solutions & Appendices (pages 96-100).
I should maintain the same comprehensive, first-principles approach I've been using, with detailed content for each page. For Part V, I'll focus on the human and operational aspects of distributed systems. For Part VI, I'll create realistic case studies that tie together the concepts from previous parts. Part VII will have interactive learning elements, and Part VIII will provide solutions and reference materials.Response 9: PART V - Human & Operational Factors (Pages 75-80)