Page 11: AXIOM 6 – Observability
Learning Objective: You can't debug what you can't see; distributed systems multiply blindness.
The Heisenberg Principle of Systems:
Observer Effect: The act of observing a distributed system changes its behavior
- Logging adds latency
- Metrics consume CPU
- Tracing uses network bandwidth
- All observation has cost

Uncertainty Principle: You cannot simultaneously know:
- Exact state of all nodes (snapshot inconsistency)
- Complete ordering of all events (clock skew)
- Full causality chain (trace sampling)
🎬 Failure Vignette: The Invisible Memory Leak
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
The Three Pillars of Observability:
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
The Observability Cost Equation:
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
🎯 Decision Tree: What to Instrument
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
Anti-Patterns in Observability:

Log Everything: Drowns signal in noise
Average Everything: Hides spikes and outliers
Never Delete: Infinite retention = infinite cost
Dashboard Sprawl: 1000 dashboards = 0 useful dashboards
Alert Fatigue: Everything pages = nothing matters
No Correlation IDs: Can't trace requests across services

The RIGHT Observability:
For each service:
- 4 Golden Signals (see page 12)
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
🔧 Try This: Structured Logging
pythonimport json
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