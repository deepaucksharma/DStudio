---
title: Timeout Pattern
description: Prevent indefinite waits and resource exhaustion by setting time limits on operations
type: pattern
category: resilience
difficulty: beginner
reading_time: 10 min
prerequisites: [network-programming, distributed-systems, error-handling]
when_to_use: Network calls, database queries, API requests, distributed transactions, service-to-service communication
when_not_to_use: CPU-bound operations, local function calls, operations with unpredictable duration
status: complete
last_updated: 2025-07-26
tags: [fault-tolerance, resource-management, resilience, network-reliability]
excellence_tier: gold
pattern_status: recommended
introduced: 1980-01
current_relevance: mainstream
modern_examples:
  - company: Netflix
    implementation: "Hystrix library enforces timeouts on all service calls"
    scale: "Billions of requests/day with 99.99% availability"
  - company: Amazon
    implementation: "Every AWS API has configurable timeouts"
    scale: "Prevents cascade failures across millions of EC2 instances"
  - company: Google
    implementation: "gRPC deadline propagation across service boundaries"
    scale: "Sub-second timeouts for billions of RPC calls"
production_checklist:
  - "Set appropriate timeout values (p99 latency + buffer)"
  - "Configure connection vs request timeouts separately"
  - "Implement timeout propagation across service calls"
  - "Monitor timeout rates and adjust thresholds"
  - "Test timeout behavior under load"
---

# Timeout Pattern

!!! success "🏆 Gold Standard Pattern"
    **Fundamental Resilience Control** • Netflix, Amazon, Google proven
    
    The most basic yet critical resilience pattern. Timeouts prevent resource exhaustion and cascading failures by ensuring no operation waits indefinitely.

## Core Concept

```mermaid
flowchart LR
    subgraph "Without Timeout"
        R1[Request] --> W1[Wait...] --> W2[Wait...] --> W3[∞]
    end
    
    subgraph "With Timeout"
        R2[Request] --> T[Timer: 5s] --> E{Expired?}
        E -->|Yes| H[Handle Error]
        E -->|No| S[Success]
    end
    
    style W3 fill:#f99
    style S fill:#9f9
    style H fill:#ff9
```

## Timeout Types & Values

| Type | Purpose | Typical Value | Example |
|------|---------|---------------|---------|  
| **Connection** | TCP handshake | 1-5s | Database connect |
| **Read** | Response data | 5-30s | API response |
| **Write** | Request data | 5-10s | File upload |
| **Total** | End-to-end | 30-60s | Full transaction |
| **Idle** | Keep-alive | 60-300s | Connection pool |

## Timeout Strategies

```mermaid
graph TD
    subgraph "Strategy Decision Tree"
        S[Select Strategy] --> Q1{System Type?}
        
        Q1 -->|Simple| Fixed[Fixed Timeout<br/>All ops: 30s]
        Q1 -->|Complex| Q2{Load Pattern?}
        
        Q2 -->|Predictable| Tiered[Tiered Timeout<br/>Read: 5s, Write: 30s]
        Q2 -->|Variable| Q3{Critical Path?}
        
        Q3 -->|Yes| Hedged[Hedged Request<br/>Primary: 2s, Backup: 0.5s]
        Q3 -->|No| Adaptive[Adaptive Timeout<br/>P99 × 1.5]
    end
    
    style Fixed fill:#9f9
    style Tiered fill:#9ff
    style Adaptive fill:#ff9
    style Hedged fill:#f9f
```

## Cascading Timeouts

```mermaid
graph TB
    subgraph "Timeout Hierarchy"
        Client["Client<br/>60s total"] --> Gateway["API Gateway<br/>50s budget"]
        Gateway --> S1["Service A<br/>20s budget"]
        Gateway --> S2["Service B<br/>20s budget"]
        S1 --> DB["Database<br/>10s budget"]
        S1 --> Cache["Cache<br/>2s budget"]
        S2 --> API["External API<br/>15s budget"]
    end
    
    style Client fill:#ff9
    style Gateway fill:#9ff
```

**Key Rule**: Child timeout < Parent timeout - Network overhead

## Implementation Patterns

### Basic Timeout

```python
import asyncio
from typing import TypeVar, Callable, Any

T = TypeVar('T')

async def with_timeout(
    operation: Callable[[], T], 
    seconds: float
) -> T:
    """Execute operation with timeout"""
    try:
        return await asyncio.wait_for(
            operation(), 
            timeout=seconds
        )
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {seconds}s")
```

### Cascading Timeout Budget

```python
import time
from typing import Dict, Any

class TimeoutBudget:
    """Manage timeout budget across service calls"""
    
    def __init__(self, total_seconds: float):
        self.total = total_seconds
        self.start = time.time()
    
    def remaining(self) -> float:
        """Get remaining timeout budget"""
        elapsed = time.time() - self.start
        return max(0, self.total - elapsed)
    
    def allocate(self, requested: float) -> float:
        """Allocate timeout from budget"""
        return min(requested, self.remaining())

# Usage
budget = TimeoutBudget(total_seconds=30)
db_timeout = budget.allocate(10)  # Get up to 10s
api_timeout = budget.allocate(15) # Get remaining time
```

## Timeout Calculation

| Metric | Formula | Example |
|--------|---------|---------|  
| **Basic** | P99 latency × 2 | 500ms × 2 = 1s |
| **Conservative** | P999 latency × 1.5 | 2s × 1.5 = 3s |
| **Aggressive** | P95 latency × 1.2 | 300ms × 1.2 = 360ms |
| **Adaptive** | Recent P99 × (1 + jitter) | Dynamic adjustment |

## Production Patterns

### 1. Timeout with Retry

```python
async def reliable_call(
    operation: Callable,
    timeout: float = 5.0,
    retries: int = 3
) -> Any:
    """Call with timeout and exponential backoff retry"""
    for attempt in range(retries):
        try:
            return await with_timeout(operation, timeout)
        except TimeoutError:
            if attempt == retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Hedged Requests

```python
async def hedged_request(
    primary: Callable,
    backup: Callable,
    hedge_delay: float = 0.5
) -> Any:
    """Send backup request if primary is slow"""
    primary_task = asyncio.create_task(primary())
    
    # Wait briefly for primary
    try:
        return await asyncio.wait_for(primary_task, hedge_delay)
    except asyncio.TimeoutError:
        # Primary slow, race both
        backup_task = asyncio.create_task(backup())
        done, pending = await asyncio.wait(
            {primary_task, backup_task},
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel loser
        for task in pending:
            task.cancel()
            
        return await done.pop()
```

## Monitoring & Alerts

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| **Timeout Rate** | > 1% | Investigate latency |
| **P99 vs Timeout** | > 80% | Increase timeout |
| **Timeout Storms** | > 10% in 1min | Circuit breaker |
| **Budget Exhaustion** | > 5% | Review hierarchy |

## Common Pitfalls

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|  
| **Infinite Timeout** | Resource leak | Always set limits |
| **One-Size-Fits-All** | Poor performance | Operation-specific values |
| **No Propagation** | Cascade failures | Pass deadline context |
| **Tight Timeouts** | False positives | P99 + buffer |
| **No Monitoring** | Silent failures | Track timeout metrics |

## Decision Framework

```mermaid
graph TD
    Start[Configure Timeout] --> Type{Operation Type?}
    
    Type -->|User-Facing| UF[1-5 seconds]
    Type -->|Background| BG[Minutes-Hours]
    Type -->|External API| EA[10-30 seconds]
    
    UF --> Critical{Critical Path?}
    Critical -->|Yes| Hedge[Add Hedging]
    Critical -->|No| Monitor[Monitor Only]
    
    EA --> Retry{Idempotent?}
    Retry -->|Yes| AddRetry[Add Retry Logic]
    Retry -->|No| CB[Circuit Breaker]
    
    style UF fill:#9f9
    style Hedge fill:#f9f
    style AddRetry fill:#9ff
```

## Quick Reference

### Essential Timeouts
```yaml
# API Gateway
connection_timeout: 5s
request_timeout: 30s
idle_timeout: 60s

# Database
connect_timeout: 5s
query_timeout: 10s
transaction_timeout: 30s

# HTTP Client  
connect_timeout: 3s
read_timeout: 10s
total_timeout: 30s
```

### Implementation Checklist
- [ ] Set timeouts for ALL network operations
- [ ] Configure cascading timeout budgets  
- [ ] Monitor timeout rates and P99 latency
- [ ] Test timeout behavior under load
- [ ] Document timeout values and rationale
- [ ] Implement graceful degradation
- [ ] Add timeout context to logs
- [ ] Review and tune regularly

<div class="truth-box">
<h4>💡 Timeout Production Insights</h4>

**The 3-30-300 Rule:**
- 3 seconds: Maximum for user-facing operations
- 30 seconds: Maximum for background processes
- 300 seconds: Maximum for batch operations

**Timeout Hierarchy:**
```
Total Timeout (60s)
├── Connection Timeout (5s)
├── Request Write Timeout (10s)
└── Response Read Timeout (45s)
```

**Real-World Patterns:**
- 50% of timeout values are never tuned after initial setup
- 90% of timeout failures happen in the first 10% of the timeout period
- Timeout errors increase 10x during deployments
- Network timeouts should be 2-3x application timeouts

**Economic Impact:**
> "Every second of unnecessary timeout costs $1000 in engineer productivity. Every missing timeout costs $100,000 in outage recovery."

**Anti-Patterns to Avoid:**
1. **Infinite timeouts**: Resource exhaustion guaranteed
2. **Timeout = Retry**: Creates amplification attacks
3. **Same timeout everywhere**: Different operations need different limits
4. **No timeout monitoring**: Flying blind
</div>

## See Also

- [Circuit Breaker](circuit-breaker.md) - Prevent cascade failures
- [Retry & Backoff](retry-backoff.md) - Handle transient failures
- [Bulkhead](bulkhead.md) - Isolate resources
- [Timeout Advanced](timeout-advanced.md) - Production optimizations

---

## Advanced Topics

For production-grade timeout implementations including cascading timeouts, adaptive strategies, and chaos engineering, see [Timeout Advanced Topics](timeout-advanced.md).

---

## 🎓 Key Takeaways

1. **Timeouts are mandatory** - Every network call must have a timeout
2. **Cascade your timeouts** - Respect parent timeout constraints
3. **Monitor and adapt** - Use metrics to optimize timeout values
4. **Test timeout behavior** - Chaos engineering for timeout scenarios
5. **Consider economics** - Balance user experience with resource costs

---

*"The absence of a timeout is the presence of a bug waiting to happen."*

---

**Previous**: [← Retry & Backoff](retry-backoff.md) | **Next**: [Tunable Consistency →](tunable-consistency.md)