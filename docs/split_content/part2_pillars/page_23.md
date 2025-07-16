Page 23: Autoscaling & Back-Pressure
The Control Theory of Autoscaling:
                     Target
                       ↓
Error = Target - Current
         ↓
    PID Controller
         ↓
Scale Decision = Kp×Error + Ki×∫Error + Kd×(dError/dt)
         ↓
    Add/Remove Instances
         ↓
    Measure Current ←────┘
Autoscaling Strategies Compared:
Strategy         Response Time    Stability    Cost
--------         -------------    ---------    ----
Reactive         Slow (minutes)   Good         Low
Predictive       Fast (seconds)   Medium       Medium
Scheduled        Instant          High         Medium
ML-based         Fast            Low-Med      High
Back-Pressure Mechanisms:
1. Token Bucket:
Tokens added at fixed rate → [||||||||  ]
Request consumes token    → [|||||||   ]
No tokens = reject        → [          ] → 429 Error

Config:
- Bucket size: Burst capacity
- Refill rate: Sustained capacity
- Token cost: Per request or per byte
2. Sliding Window:
Time window: [===========]
              ↑         ↑
           10s ago    Now

Requests in window: 847/1000 allowed
New request: Check if under limit
3. Adaptive Concurrency (BBR-style):
Gradient descent on concurrency limit:
1. Measure: RTT and throughput
2. Probe: Increase limit slightly
3. Observe: Did throughput increase?
4. Adjust: If latency spiked, back off

Finds optimal concurrency automatically!
Real Implementation: Go Rate Limiter:
gotype RateLimiter struct {
    tokens    float64
    capacity  float64
    rate      float64
    lastRefill time.Time
    mu        sync.Mutex
}

func (rl *RateLimiter) Allow() bool {
    rl.mu.Lock()
    defer rl.mu.Unlock()
    
    // Refill tokens
    now := time.Now()
    elapsed := now.Sub(rl.lastRefill).Seconds()
    rl.tokens = min(rl.capacity, rl.tokens + elapsed*rl.rate)
    rl.lastRefill = now
    
    // Try to consume
    if rl.tokens >= 1.0 {
        rl.tokens--
        return true
    }
    return false
}
Back-Pressure Propagation:
User → API Gateway → Service A → Service B → Database
  ↑        ↑            ↑           ↑          ↑
  └────────┴────────────┴───────────┴──────────┘
         Back-pressure flows upstream
Common Back-Pressure Mistakes:

No Timeout Coordination: Upstream timeout < downstream
Buffer Bloat: Queues too large, hide problems
Unfair Rejection: No priority/fairness
No Gradient: Binary accept/reject vs gradual
