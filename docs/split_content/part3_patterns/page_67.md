Page 67: Queueing Models (M/M/1)
When will your system hit the wall?
M/M/1 QUEUE BASICS
M/M/1 means:
- Markovian (exponential) arrivals
- Markovian (exponential) service times  
- 1 server

Key metrics:
ρ = λ/μ (utilization)
Where λ = arrival rate, μ = service rate
FUNDAMENTAL FORMULAS
Average Queue Length
Lq = ρ²/(1-ρ)

Example:
50% utilization: 0.5²/0.5 = 0.5 customers
80% utilization: 0.8²/0.2 = 3.2 customers
90% utilization: 0.9²/0.1 = 8.1 customers
95% utilization: 0.95²/0.05 = 18 customers!
Average Wait Time
Wq = Lq/λ = ρ/(μ-λ)

Example (μ=100 req/s):
λ=50: Wait = 0.5/(100-50) = 10ms
λ=80: Wait = 0.8/(100-80) = 40ms
λ=90: Wait = 0.9/(100-90) = 90ms
λ=95: Wait = 0.95/(100-95) = 190ms!
Response Time Distribution
P(response time > t) = e^(-μ(1-ρ)t)

Probability of response > 1 second:
At 50% util: e^(-50×0.5×1) = 0.0000%
At 80% util: e^(-20×0.2×1) = 0.02%
At 90% util: e^(-10×0.1×1) = 0.37%
At 95% util: e^(-5×0.05×1) = 7.8%!
M/M/c MULTI-SERVER QUEUE
Erlang C Formula (probability of queueing)
Complex formula, but key insights:
- Adding servers helps dramatically
- Diminishing returns past a point
- Load balancing critical

Rule of thumb:
2 servers at 80% > 1 server at 40%
REAL-WORLD APPLICATIONS
API Server Sizing
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
Database Connection Pool
Queries: 500/s
Query time: 20ms
Target wait: <5ms

Utilization for 5ms wait:
5 = 20×ρ/(1-ρ)
ρ = 0.2 (20% utilization)

Connections needed = 500×0.02/0.2 = 50
WHEN M/M/1 BREAKS DOWN
Real Traffic is Bursty
Actual pattern:
- Morning spike: 2x average
- Lunch lull: 0.5x average  
- End of day: 1.5x average

Solution: Use peak, not average
Safety factor: 1.5-2x
Service Times Vary
Real distribution:
- Fast queries: 10ms (80%)
- Slow queries: 200ms (20%)

High variance → Worse queueing
Use M/G/1 model or simulation
QUEUE MANAGEMENT STRATEGIES
Admission Control
if queue_length > threshold:
    reject_with_503()
    
Prevents:
- Unbounded queue growth
- Memory exhaustion
- Cascade failures
Adaptive Capacity
if avg_wait_time > target:
    scale_up()
elif avg_wait_time < target/2:
    scale_down()
    
Maintains:
- Consistent performance
- Cost efficiency
Priority Queues
High priority: Payment processing
Normal priority: Regular API calls
Low priority: Batch operations

Separate queues or weighted fair queueing