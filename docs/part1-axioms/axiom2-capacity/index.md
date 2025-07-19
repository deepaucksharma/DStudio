# Axiom 2: Finite Capacity

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Every resource has a breaking point; find it before production does.
  </div>
</div>

## Core Principle

<div class="definition-box">
Every system component has finite:
- CPU cycles per second
- Memory bytes
- Network packets/sec
- Disk IOPS
- Connection pool slots
- Thread count  
- Queue depth

**Corollary**: Infinite scaling is a lie sold by cloud vendors.
</div>

## The Thermodynamics Angle

> "Just as energy cannot be created or destroyed, computational capacity cannot be materialized from nothing. It can only be moved (migration), transformed (optimization), or purchased (scaling)."

## 🎬 Failure Vignette: Black Friday Database Meltdown

**Company**: Major Retailer, $2B Revenue  
**Date**: Black Friday 2021, 6:00 AM EST  
**Impact**: $50M lost sales

**The Timeline**:
```
06:00 - Marketing sends "50% off everything" email
06:01 - 2M users click simultaneously
06:02 - API servers scale from 100 to 1,000 pods
06:03 - Each pod opens 10 connections to DB
06:04 - Database connection limit: 5,000
06:05 - 10,000 connections attempted
06:06 - Database rejects new connections
06:07 - Health checks fail, cascading restarts
06:15 - Site completely down
08:00 - Manual intervention restores service
```

**Root Cause**: Scaled compute, forgot DB connections are finite

**Fix**: Connection pooling, admission control, backpressure

**Lesson**: Every resource has a limit. Find yours before your customers do.

## The Capacity Staircase

<div class="capacity-levels">
<h3>📊 Levels of Resource Limits</h3>

**Level 1: Single Server Limits**
- 16 cores = 16 truly parallel operations
- 64GB RAM = ~1M concurrent user sessions  
- 10Gbps NIC = 1.25GB/sec theoretical max

**Level 2: Distributed Limits**
- Coordination overhead eats 20-30% capacity
- Network becomes the bottleneck
- Shared storage creates contention

**Level 3: Planetary Limits**
- Speed of light creates coordination delays
- CAP theorem forces trade-offs
- Human operators become bottleneck
</div>

## Decision Framework

<div class="decision-box">
<h3>🎯 Scale-Up vs Scale-Out Decision Tree</h3>

```
START: Need more capacity
  │
  ├─ Is workload parallelizable?
  │   ├─ NO → Scale UP (bigger box)
  │   └─ YES → Continue
  │
  ├─ Is data easily partitioned?
  │   ├─ NO → Scale UP + Read replicas
  │   └─ YES → Continue
  │
  ├─ Can tolerate eventual consistency?
  │   ├─ NO → Scale UP to limits, then shard carefully
  │   └─ YES → Scale OUT (add nodes)
  │
  └─ Result: Your scaling strategy
```
</div>

## Capacity Arithmetic

<div class="formula-box">
<h3>🧮 The Effective Capacity Formula</h3>

```
Effective Capacity = Raw Capacity × Utilization Factor × Efficiency Factor

Where:
- Utilization Factor = 1 - (idle + overhead)
- Efficiency Factor = 1 / (1 + coordination_cost)

Example:
- Raw: 100 CPU cores
- Utilization: 0.7 (30% overhead)
- Efficiency: 0.8 (25% coordination cost)
- Effective: 100 × 0.7 × 0.8 = 56 cores actual work
```
</div>

## 🔧 Try This: Find Your Breaking Point (DO NOT RUN IN PROD!)

```bash
# Terminal 1: Start a simple server
python -m http.server 8000

# Terminal 2: Find the limit
ab -n 10000 -c 100 http://localhost:8000/
# Watch for the cliff where latency spikes

# Terminal 3: Monitor resources
htop  # Watch CPU, memory
iftop # Watch network
iotop # Watch disk
```

**What you'll learn**: Systems don't degrade gracefully—they hit a cliff.

## Real Capacity Limits (2024)

<div class="limits-table">
<h3>📋 Production Capacity Limits</h3>

| Component | Practical Limit | Why |
|-----------|----------------|-----|
| PostgreSQL | 5,000 connections | Connection overhead |
| Redis | 10K ops/sec/core | Single-threaded |
| Kafka | 1M messages/sec/broker | Disk I/O |
| Load Balancer | 100K concurrent | Memory per connection |
| Docker | ~10K containers/host | Kernel limits |
| Kubernetes | 5,000 nodes/cluster | etcd limits |
| Elasticsearch | 1,000 shards/node | Memory overhead |
</div>

## Counter-Intuitive Truth

<div class="insight-box">
<h3>💡 100% Utilization = Over Capacity</h3>

Running at 100% capacity means you're already over capacity. Systems need breathing room for:
- Garbage collection pauses
- Background maintenance
- Traffic spikes
- Failed node compensation

**Target**: 60-70% steady-state utilization
</div>

## Worked Example: Video Streaming

<div class="example-box">
<h3>🧮 Capacity Planning for 1M Concurrent Viewers</h3>

```
Requirements:
- 1M concurrent streams
- 4K video = 25 Mbps per stream
- 3 availability zones
- N+1 redundancy

Calculations:
Total bandwidth: 1M × 25 Mbps = 25 Tbps
Per AZ (with headroom): 25 Tbps / 3 × 1.5 = 12.5 Tbps
Per edge node (100G NIC): 12.5 Tbps / 100 Gbps = 125 nodes
With N+1: 125 × 1.2 = 150 nodes per AZ
Total: 450 edge nodes

Cost reality check:
450 nodes × $5k/month = $2.25M/month
Revenue needed at $10/user: 225k subscribers
```
</div>

## Common Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Capacity Mistakes to Avoid</h3>

1. **Infinite Queue Syndrome**: Unbounded queues = unbounded memory
2. **Connection Leak Lottery**: Forget to close = slow death
3. **Thundering Herd**: Everyone retries at once
4. **Resource Starvation**: One bad query blocks everything
5. **Cascade Failure**: Overload propagates through system
</div>

## The Backpressure Pattern

<div class="pattern-box">
<h3>🔧 Handling Capacity Limits Gracefully</h3>

```python
class BoundedQueue:
    def __init__(self, max_size=1000):
        self.queue = []
        self.max_size = max_size
    
    def push(self, item):
        if len(self.queue) >= self.max_size:
            # Apply backpressure
            raise QueueFullError("System at capacity")
        self.queue.append(item)
    
    def pop(self):
        if not self.queue:
            return None
        return self.queue.pop(0)

# Usage with exponential backoff
for attempt in range(5):
    try:
        queue.push(work_item)
        break
    except QueueFullError:
        wait_time = 2 ** attempt
        time.sleep(wait_time)
```
</div>

## Measurement Points

<div class="measure-this">
<h3>📊 Critical Capacity Metrics</h3>

- **Utilization**: Current / Maximum (alert at 70%)
- **Saturation**: Queue depth (alert at 80% of limit)
- **Errors**: Rate of capacity rejections
- **Latency**: Response time at percentiles

```yaml
# Prometheus alerts
- alert: HighCPUUtilization
  expr: cpu_usage_percent > 70
  for: 5m
  
- alert: ConnectionPoolExhaustion
  expr: connection_pool_active / connection_pool_max > 0.8
  for: 1m
```
</div>

## Cross-References

<div class="cross-links">
<h3>🔗 Related Concepts</h3>

- → [Axiom 3: Failure](../axiom3-failure/): What happens at capacity
- → [Load Balancing Patterns](../../patterns/load-balancing): Distributing load
- → [Admission Control](../../patterns/admission-control): Rejecting gracefully
- → [Circuit Breakers](../../patterns/circuit-breaker): Preventing cascade
</div>

## Summary: Key Takeaways

1. **Every resource is finite**—know your limits
2. **Measure before you hit limits**—cliffs are sudden
3. **Plan for 60-70% utilization**—leave headroom
4. **Backpressure > dropping**—fail fast and explicitly
5. **Capacity is multiplicative**—weakest link matters

## Quick Reference Card

<div class="reference-card">
<h3>📋 Capacity Planning Checklist</h3>

**For each resource, know:**
- [ ] Hard limit (connections, memory, etc.)
- [ ] Current utilization percentage
- [ ] Growth rate (daily/weekly)
- [ ] Time to provision more
- [ ] Cost of additional capacity
- [ ] Graceful degradation plan

**Red flags:**
- Unbounded growth (queues, connections)
- No backpressure mechanisms
- Single points of capacity failure
- No capacity monitoring
</div>

---

**Next**: [Axiom 3: Failure →](../axiom3-failure/)

*"The question is not IF you'll hit capacity limits, but WHEN."*