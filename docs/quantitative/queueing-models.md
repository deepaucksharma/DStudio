# Queueing Models (M/M/1)

**When will your system hit the wall?**

## M/M/1 Queue Basics

M/M/1 notation means:
- **M**arkovian (exponential) arrivals
- **M**arkovian (exponential) service times  
- **1** server

Key parameter:
```
ρ = λ/μ (utilization)
Where:
λ = arrival rate
μ = service rate
```

## Fundamental Formulas

### Average Queue Length
```
Lq = ρ²/(1-ρ)

Example:
50% utilization: 0.5²/0.5 = 0.5 customers
80% utilization: 0.8²/0.2 = 3.2 customers
90% utilization: 0.9²/0.1 = 8.1 customers
95% utilization: 0.95²/0.05 = 18 customers!
```

### Average Wait Time
```
Wq = Lq/λ = ρ/(μ-λ)

Example (μ=100 req/s):
λ=50: Wait = 0.5/(100-50) = 10ms
λ=80: Wait = 0.8/(100-80) = 40ms
λ=90: Wait = 0.9/(100-90) = 90ms
λ=95: Wait = 0.95/(100-95) = 190ms!
```

### Response Time Distribution
```
P(response time > t) = e^(-μ(1-ρ)t)

Probability of response > 1 second:
At 50% util: e^(-50×0.5×1) = 0.0000%
At 80% util: e^(-20×0.2×1) = 0.02%
At 90% util: e^(-10×0.1×1) = 0.37%
At 95% util: e^(-5×0.05×1) = 7.8%!
```

## The Knee of the Curve

Response time vs utilization shows exponential growth:

```
Utilization  Queue Time   Total Response
-----------  ----------   --------------
50%          10ms         20ms
60%          15ms         25ms
70%          23ms         33ms
80%          40ms         50ms
85%          57ms         67ms
90%          90ms         100ms
95%          190ms        200ms
99%          990ms        1000ms!
```

**Key insight**: Beyond 80% utilization, small load increases cause massive latency spikes.

## M/M/c Multi-Server Queue

With multiple servers, the math gets complex but the insights remain:

### Erlang C Formula
Probability that an arriving customer must queue:
```
P(queue) = (ρ^c / c!) / Σ(k=0 to c-1)[(ρ^k / k!) + (ρ^c / c!) × (1/(1-ρ/c))]
```

### Practical Impact
```
Servers  Utilization  Queue Probability
-------  -----------  -----------------
1        80%          80%
2        80%          44%
4        80%          23%
8        80%          11%
16       80%          5%
```

**Rule of thumb**: 2 servers at 80% > 1 server at 40%

## Real-World Applications

### API Server Sizing
```
Given:
- Request rate: 1000 req/s
- Service time: 50ms
- Target: 95% < 200ms

Single server: ρ = 1000×0.05 = 50 (impossible!)
Need: 50+ servers

With 60 servers: ρ = 50/60 = 83%
Queue time ≈ 250ms (too high)

With 70 servers: ρ = 50/70 = 71%
Queue time ≈ 100ms (acceptable)
```

### Database Connection Pool
```
Queries: 500/s
Query time: 20ms
Target wait: <5ms

Utilization for 5ms wait:
5 = 20×ρ/(1-ρ)
ρ = 0.2 (20% utilization!)

Connections needed = 500×0.02/0.2 = 50
```

### Message Queue Sizing
```
Messages: 1000/s
Process time: 10ms
Target: <100ms latency

ρ for 100ms total:
100 = 10 + 10×ρ/(1-ρ)
ρ ≈ 0.9

Workers needed = 1000×0.01/0.9 = 11
Add safety: 15 workers
```

## When M/M/1 Breaks Down

### Real Traffic is Bursty
```
Actual pattern:
- Morning spike: 2x average
- Lunch lull: 0.5x average  
- End of day: 1.5x average

Solution: Use peak, not average
Safety factor: 1.5-2x
```

### Service Times Vary
```
Real distribution:
- Fast queries: 10ms (80%)
- Slow queries: 200ms (20%)

High variance → Worse queueing
Use M/G/1 model or simulation
```

### Correlated Arrivals
```
Real pattern:
- User sessions generate bursts
- Failures cause retries
- Batch jobs create spikes

Impact: Actual queue >> M/M/1 prediction
```

## Queue Management Strategies

### Admission Control
```python
if queue_length > threshold:
    reject_with_503()
    
# Prevents:
# - Unbounded queue growth
# - Memory exhaustion
# - Cascade failures
```

### Adaptive Capacity
```python
if avg_wait_time > target:
    scale_up()
elif avg_wait_time < target/2:
    scale_down()
    
# Maintains:
# - Consistent performance
# - Cost efficiency
```

### Priority Queues
```
High priority: Payment processing
Normal priority: Regular API calls
Low priority: Batch operations

Separate queues or weighted fair queueing
```

## Advanced Queueing Patterns

### Queue with Timeout
```
Effective arrival rate when customers leave:
λ_eff = λ × P(wait < timeout)

Improves system stability but reduces throughput
```

### Bulk Service
```
Process N items together:
- Reduces per-item overhead
- Increases minimum latency
- Better for batch workloads
```

### Processor Sharing
```
All customers served simultaneously at reduced rate
- Used in CPU scheduling
- Fair but higher average latency
- No queue buildup
```

## Practical Guidelines

### Sizing for Latency
```
Target Latency  Max Utilization
--------------  ---------------
2x service time      50%
5x service time      80%
10x service time     90%
20x service time     95%
```

### Queue Monitoring
Key metrics to track:
- Queue depth (L)
- Wait time (W)
- Utilization (ρ)
- Arrival rate (λ)
- Service rate (μ)

### Capacity Planning
```
Current: 70% utilization, 30ms response
Future: 2x traffic

New utilization: 140% (system fails!)

Options:
1. Double servers: 70% util maintained
2. Optimize service: Reduce service time 50%
3. Add cache: Reduce arrival rate 50%
```

## Key Takeaways

1. **80% is the practical limit** - Beyond this, queues explode
2. **Variance matters** - High variance = worse queuing
3. **Multiple servers help** - But with diminishing returns
4. **Monitor utilization** - It predicts response time
5. **Plan for peaks** - Average traffic is misleading

Remember: Queues are everywhere - CPU, network, disk, application. Understanding queueing theory helps predict system behavior before it breaks.