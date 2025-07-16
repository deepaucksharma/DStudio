Page 2: Latency Budget Worksheet
Purpose: Transform latency from abstract concept to concrete budget.
The Latency P&L Statement:
REVENUE (Total Budget)
├── User Expectation:        [___] ms
├── Minus Browser Render:    -50 ms
├── Minus Network Last Mile: -20 ms
└── = Backend Budget:        [___] ms

EXPENSES (Allocations)
├── Load Balancer:     [___] ms (typical: 1-2)
├── API Gateway:       [___] ms (typical: 2-5)
├── Service Mesh:      [___] ms (typical: 1-3)
├── Business Logic:    [___] ms (varies)
├── Database Call:     [___] ms (typical: 5-50)
├── Cache Check:       [___] ms (typical: 0.5-2)
└── Total Spent:       [___] ms

MARGIN: [___] ms (must be > 0!)
Real-World Budgets by Industry:
Stock Trading:     10 ms (regulatory requirement)
Gaming:            16 ms (60 fps requirement)
Video Conference:  150 ms (conversation flow)
E-commerce:        1000 ms (conversion dropoff)
Email:             5000 ms (user expectation)
🧮 Worked Example: Photo Sharing App
User uploads photo, expects thumbnail in < 2 seconds

Budget Allocation:
- Upload to CDN edge:          100 ms (physics: user to edge)
- Edge to origin DC:           50 ms (physics: edge to DC)
- Queue wait time:             200 ms (p95 during peak)
- Resize processing:           500 ms (CPU bound)
- Thumbnail generation:        300 ms (GPU accelerated)
- Write to 3 replicas:         150 ms (parallel writes)
- CDN cache population:        200 ms (push to edges)
- Response to user:            100 ms (physics: edge to user)
TOTAL:                         1600 ms ✓ (400ms margin)

Optimization opportunities:
1. Pre-warm GPU containers (-200ms cold start)
2. Regional processing (-50ms physics tax)
3. Optimistic UI (-1600ms perceived!)
Budget Violation Patterns:

Death by Thousand Cuts: Each service "only" adds 5ms
Retry Multiplication: 3 retries × 100ms = 300ms gone
Serial Staircase: Waterfall instead of parallel
Cold Start Surprise: Lambda/container warm-up
GC Pause Gambling: 99th percentile GC stops

🔧 Try This: Profile Your Critical Path
pythonimport time
from contextlib import contextmanager

@contextmanager
def latency_budget(operation, budget_ms):
    start = time.time()
    yield
    elapsed_ms = (time.time() - start) * 1000
    remaining = budget_ms - elapsed_ms
    print(f"{operation}: {elapsed_ms:.1f}ms (budget: {remaining:+.1f}ms)")
    if remaining < 0:
        print(f"⚠️  BUDGET VIOLATION: {-remaining:.1f}ms over!")

# Use in your code:
with latency_budget("Database query", 50):
    results = db.query("SELECT ...")