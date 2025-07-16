Page 12: Four-Golden-Signals Dashboard Sample
The Universal Health Metrics:
┌─────────────────────── Service Health Dashboard ───────────────────────┐
│                                                                         │
│  1. LATENCY (Response Time)                                           │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  P50: 45ms  P95: 120ms  P99: 450ms  P99.9: 1.2s           │    │
│  │  ▁▂▁▂▃▂▁▂▁▂▃▄▅▄▃▂▁▂▁▂▃▂▁▂ ← Live graph               │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  2. TRAFFIC (Request Rate)                                            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Current: 8.5K req/s  Peak today: 12K req/s                │    │
│  │  ████████████▌               Capacity: 15K req/s           │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  3. ERRORS (Failure Rate)                                             │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  Rate: 0.12%  SLO: <0.1%  🔴 VIOLATING SLO                │    │
│  │  Top errors: [504 Gateway Timeout: 0.08%]                  │    │
│  │              [429 Too Many Requests: 0.03%]                │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  4. SATURATION (Resource Usage)                                       │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │  CPU: ████████░░ 78%    Memory: ██████░░░░ 62%           │    │
│  │  Disk I/O: ███░░░░░░░ 31%   Network: █████░░░░░ 53%      │    │
│  │  Thread Pool: ████████░░ 81% ⚠️                           │    │
│  └──────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
Why These Four?

Latency: User experience indicator
Traffic: Load and growth indicator
Errors: Reliability indicator
Saturation: Capacity indicator

Per-Signal Deep Dive:
LATENCY:
Always track percentiles, never just average:
- P50: Typical user experience
- P95: Power users / complex queries
- P99: Worst case that happens regularly
- P99.9: The pathological cases

Latency breakdown:
Total = Network + Queue + Processing + External calls
TRAFFIC:
Track multiple dimensions:
- Request rate (req/s)
- Bandwidth (MB/s)
- Active connections
- Request types distribution

Business correlation:
- Day/hour patterns
- Marketing campaign spikes
- Seasonal variations
ERRORS:
Categorize by:
- Client errors (4xx): Not your fault, but monitor
- Server errors (5xx): Your fault, alert!
- Timeout errors: Often capacity issues
- Business errors: Valid but failed operations

Error budget calculation:
Monthly budget = (1 - SLO) × requests
e.g., 99.9% SLO = 0.1% × 2.6B = 2.6M errors allowed
SATURATION:
Resource hierarchy:
1. CPU: First to saturate usually
2. Memory: Causes GC pressure
3. Network: Often forgotten
4. Disk I/O: Database bottleneck
5. Application-specific: Thread pools, connections

Utilization targets:
- Development: < 20% (room to debug)
- Production: 40-70% (efficient but safe)
- Alert threshold: > 80%
- Panic threshold: > 90%