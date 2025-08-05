# Resilience Patterns

Patterns for fault tolerance, recovery, and system stability.

## Overview

Resilience patterns help systems survive and recover from failures. They address the reality that in distributed systems, failures are not just possible but inevitable. These patterns provide strategies for:

- **Fault Isolation** - Preventing cascade failures
- **Graceful Degradation** - Maintaining partial functionality
- **Quick Recovery** - Minimizing downtime
- **Failure Detection** - Identifying problems early

## Available Patterns

### Core Resilience Patterns
- **[Circuit Breaker](/pattern-library/resilience/circuit-breaker/)** - Prevent cascade failures by detecting service failures
- **[Retry & Backoff](/pattern-library/resilience/retry-backoff/)** - Handle transient failures with intelligent retries
- **[Timeout](/pattern-library/resilience/timeout/)** - Prevent indefinite waits and resource exhaustion
- **[Bulkhead](/pattern-library/resilience/bulkhead/)** - Isolate resources to contain failures

### Health & Monitoring
- **[Health Check](/pattern-library/resilience/health-check/)** - Monitor and report service health status
- **[Heartbeat](/pattern-library/resilience/heartbeat/)** - Detect service liveness through periodic signals

### Failure Handling
- **[Failover](/pattern-library/resilience/failover/)** - Switch to backup systems when primary fails
- **[Graceful Degradation](/pattern-library/resilience/graceful-degradation/)** - Maintain partial functionality during failures
- **[Load Shedding](/pattern-library/resilience/load-shedding/)** - Drop requests to prevent overload
- **[Split Brain](/pattern-library/resilience/split-brain/)** - Handle network partitions in distributed systems

### Advanced Topics
- **[Timeout Advanced](timeout-advanced.md)** - Production-grade timeout strategies

## Quick Decision Guide

| Failure Type | Pattern | When to Use |
|--------------|---------|-------------|
| Service unresponsive | [Circuit Breaker](/pattern-library/resilience/circuit-breaker/) | External service calls |
| Temporary network issues | [Retry with Backoff](/pattern-library/resilience/retry-backoff/) | Transient failures expected |
| Resource exhaustion | [Bulkhead](/pattern-library/resilience/bulkhead/) | Shared resource protection |
| Slow dependency | [Timeout](/pattern-library/resilience/timeout/) | Any network operation |
| Complete service failure | [Failover](/pattern-library/resilience/failover/) | Critical services |
| Overload conditions | [Load Shedding](/pattern-library/resilience/load-shedding/) | High traffic scenarios |
| Service health monitoring | [Health Check](/pattern-library/resilience/health-check/) | All services |
| Network partition | [Split Brain](/pattern-library/resilience/split-brain/) | Distributed consensus |

## Pattern Relationships

```mermaid
graph TD
    CB[Circuit Breaker] --> TO[Timeout]
    CB --> RB[Retry & Backoff]
    BH[Bulkhead] --> CB
    HC[Health Check] --> FO[Failover]
    HB[Heartbeat] --> HC
    GD[Graceful Degradation] --> LS[Load Shedding]
    TO --> RB
    
    style CB fill:#f9f,stroke:#333,stroke-width:4px
    style TO fill:#bbf,stroke:#333,stroke-width:2px
    style BH fill:#bbf,stroke:#333,stroke-width:2px
```

## Key Principles

1. **Fail Fast** - Don't wait for timeouts
2. **Isolate Failures** - Contain the blast radius
3. **Degrade Gracefully** - Partial service > no service
4. **Monitor Everything** - You can't fix what you can't see
5. **Test Failures** - Practice recovery before production

## Implementation Order

For new systems, implement patterns in this order:

1. **[Timeout](/pattern-library/resilience/timeout/)** - Foundation for all network calls
2. **[Health Check](/pattern-library/resilience/health-check/)** - Know when services are unhealthy
3. **[Circuit Breaker](/pattern-library/resilience/circuit-breaker/)** - Prevent cascade failures
4. **[Retry & Backoff](/pattern-library/resilience/retry-backoff/)** - Handle transient failures
5. **[Bulkhead](/pattern-library/resilience/bulkhead/)** - Isolate critical resources
6. **[Graceful Degradation](/pattern-library/resilience/graceful-degradation/)** - Maintain partial service

---

*Return to the [Pattern Library](../) or explore [Communication Patterns](/pattern-library/communication/index/).*