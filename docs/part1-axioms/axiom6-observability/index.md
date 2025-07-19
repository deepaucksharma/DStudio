# Axiom 6: Observability

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: You can't debug what you can't see; distributed systems multiply blindness.
  </div>
</div>

## Core Principle

```
Observer Effect: The act of observing a distributed system changes its behavior
- Logging adds latency
- Metrics consume CPU
- Tracing uses network bandwidth
- All observation has cost

Uncertainty Principle: You cannot simultaneously know:
- Exact state of all nodes (snapshot inconsistency)
- Complete ordering of all events (clock skew)
- Full causality chain (trace sampling)
```

## 🎬 Failure Vignette: The Invisible Memory Leak

```
Company: Video streaming platform
Symptom: Random user disconnections, increasing over weeks
Monitoring in place:
- CPU metrics: Normal (40%)
- Memory metrics: Averaged per minute, looked fine
- Network metrics: Normal
- Error logs: Nothing unusual

Investigation timeline:
Week 1: "Must be client-side issues"
Week 2: "Maybe network problems?"
Week 3: Customer complaints spike
Week 4: Engineer notices during manual debug:
  - Memory usage sawtooth pattern
  - Spikes to 95% every 58 seconds
  - Averaged out to 70% in 1-min metrics
  - GC pause during spike: 2 seconds
  - Clients timeout during pause

Root cause: Goroutine leak in WebSocket handler
- Each connection leaked 1MB
- 58 seconds to accumulate ~2GB
- Massive GC pause, connections drop

Fix: 
1. Add per-second memory metrics
2. Add GC pause tracking
3. Fix the leak

Lesson: 1-minute averages hide 1-second disasters
```

## The Three Pillars of Observability

```
1. LOGS (Events)
   What: Discrete events with context
   When: Something interesting happens
   Cost: High (storage, ingestion)
   Use: Debugging specific issues

2. METRICS (Aggregates)  
   What: Numeric values over time
   When: Continuous system health
   Cost: Low (pre-aggregated)
   Use: Alerting, capacity planning

3. TRACES (Flows)
   What: Request path through system
   When: Understanding latency, dependencies
   Cost: Medium (sampling required)
   Use: Performance optimization, debugging
```

## The Observability Cost Equation

```
Total Cost = Collection + Transport + Storage + Query + Human Analysis

Where:
- Collection: CPU/memory on each node
- Transport: Network bandwidth × distance
- Storage: Size × retention × replication
- Query: Compute for aggregation/search
- Human: Engineer time (highest cost!)

Example (1000-node cluster):
- Logs: 10GB/node/day = 10TB/day = $900/day
- Metrics: 1000 metrics × 10s × 8 bytes = 70GB/day = $7/day  
- Traces: 1% sampling × 1KB/trace × 1M req/sec = 860GB/day = $80/day
- Engineers debugging without good data = $10,000/day
```

## 🎯 Decision Tree: What to Instrument

```
START: Should I add observability here?
│
├─ Is this on the critical path?
│  └─ YES → Add metrics + traces
│
├─ Can this fail independently?
│  └─ YES → Add error logs + metrics
│
├─ Does this affect user experience?
│  └─ YES → Add SLI metrics
│
├─ Is this a resource boundary?
│  └─ YES → Add utilization metrics
│
├─ Is this a system boundary?
│  └─ YES → Add traces
│
└─ Otherwise → Sample logs only
```

## Anti-Patterns in Observability

1. **Log Everything**: Drowns signal in noise
2. **Average Everything**: Hides spikes and outliers
3. **Never Delete**: Infinite retention = infinite cost
4. **Dashboard Sprawl**: 1000 dashboards = 0 useful dashboards
5. **Alert Fatigue**: Everything pages = nothing matters
6. **No Correlation IDs**: Can't trace requests across services

## The RIGHT Observability

```
For each service:
- 4 Golden Signals (see next section)
- Error logs with context
- Trace sampling (adaptive)
- Business metrics that matter

Per request:
- Correlation ID
- User ID (if applicable)  
- Key business context
- Timing at boundaries

Retention policy:
- Raw logs: 7 days
- Metrics: 13 months (year-over-year)
- Traces: 30 days (sampled)
- Aggregates: Forever
```

## 🔧 Try This: Structured Logging

```python
import json
import time
import uuid
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name):
        self.service = service_name
        
    def log(self, level, message, **kwargs):
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.service,
            'message': message,
            'correlation_id': kwargs.get('correlation_id', str(uuid.uuid4())),
            **kwargs
        }
        print(json.dumps(event))
    
    def with_timing(self, operation):
        def wrapper(*args, **kwargs):
            start = time.time()
            correlation_id = str(uuid.uuid4())
            
            self.log('INFO', f'{operation} started', 
                    correlation_id=correlation_id)
            try:
                result = operation(*args, **kwargs)
                elapsed = time.time() - start
                self.log('INFO', f'{operation} completed',
                        correlation_id=correlation_id,
                        duration_ms=elapsed * 1000)
                return result
            except Exception as e:
                elapsed = time.time() - start
                self.log('ERROR', f'{operation} failed',
                        correlation_id=correlation_id,
                        duration_ms=elapsed * 1000,
                        error=str(e))
                raise
        return wrapper

# Usage
logger = StructuredLogger('payment-service')

@logger.with_timing
def process_payment(amount, currency):
    # Simulate processing
    time.sleep(0.1)
    return {'status': 'success', 'amount': amount}
```

## Four-Golden-Signals Dashboard

### The Universal Health Metrics

```
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
```

### Why These Four?

1. **Latency**: User experience indicator
2. **Traffic**: Load and growth indicator  
3. **Errors**: Reliability indicator
4. **Saturation**: Capacity indicator

### Per-Signal Deep Dive

**LATENCY**:
```
Always track percentiles, never just average:
- P50: Typical user experience
- P95: Power users / complex queries
- P99: Worst case that happens regularly
- P99.9: The pathological cases

Latency breakdown:
Total = Network + Queue + Processing + External calls
```

**TRAFFIC**:
```
Track multiple dimensions:
- Request rate (req/s)
- Bandwidth (MB/s)
- Active connections
- Request types distribution

Business correlation:
- Day/hour patterns
- Marketing campaign spikes
- Seasonal variations
```

**ERRORS**:
```
Categorize by:
- Client errors (4xx): Not your fault, but monitor
- Server errors (5xx): Your fault, alert!
- Timeout errors: Often capacity issues
- Business errors: Valid but failed operations

Error budget calculation:
Monthly budget = (1 - SLO) × requests
e.g., 99.9% SLO = 0.1% × 2.6B = 2.6M errors allowed
```

**SATURATION**:
```
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
```

## Cross-References

- → [Axiom 2: Capacity](../axiom2-capacity/index.md): What to observe for saturation
- → [Axiom 7: Human Interface](../axiom7-human/index.md): Making observability usable
<!-- - → [Monitoring Patterns](../../patterns/monitoring): Implementation strategies -->

---

**Next**: [Axiom 7: Human Interface →](../axiom7-human/index.md)

*"You can observe a lot by watching." - Yogi Berra*