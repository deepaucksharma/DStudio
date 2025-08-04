---
best-for:
- Database bulk inserts and updates
- High-frequency API calls with rate limits
- Network-bound microservice communication
category: scaling
current_relevance: mainstream
description: Group multiple requests together to amortize fixed costs and improve
  throughput
difficulty: intermediate
essential_question: How do we handle increasing load without sacrificing performance
  using request batching/pipelining?
excellence_tier: silver
introduced: 2005-03
last-updated: 2025-01-26
pattern_status: use-with-expertise
prerequisites:
- queueing-theory
- network-protocols
- concurrency
reading-time: 25 min
status: complete
tagline: Master request batching/pipelining for distributed systems success
title: Request Batching/Pipelining
trade-offs:
  cons:
  - Increases latency for individual requests
  - Complex error handling for partial failures
  - Memory overhead from buffering requests
  pros:
  - Dramatically improves throughput for small operations
  - Reduces network overhead and protocol costs
  - Better resource utilization and efficiency
type: pattern
when-not-to-use: Real-time systems with strict latency requirements, large individual
  requests, heterogeneous operations
when-to-use: High-frequency small requests, network-bound operations, database bulk
  operations, API rate limiting
---

## Essential Question
## When to Use / When NOT to Use

### When to Use

| Scenario | Why It Fits | Alternative If Not |
|----------|-------------|-------------------|
| High availability required | Pattern provides resilience | Consider simpler approach |
| Scalability is critical | Handles load distribution | Monolithic might suffice |
| Distributed coordination needed | Manages complexity | Centralized coordination |

### When NOT to Use

| Scenario | Why to Avoid | Better Alternative |
|----------|--------------|-------------------|
| Simple applications | Unnecessary complexity | Direct implementation |
| Low traffic systems | Overhead not justified | Basic architecture |
| Limited resources | High operational cost | Simpler patterns |
**How do we handle increasing load without sacrificing performance using request batching/pipelining?**


# Request Batching/Pipelining

!!! warning "🥈 Silver Tier Pattern"
    **Massive throughput gains with latency trade-offs** • Use when amortizing fixed costs matters more than individual request latency
    
    Request batching can improve throughput by 10-100x for small operations, but adds complexity in error handling and increases p99 latency. Requires careful tuning of batch sizes and timeouts for each use case.

## The Pattern

Request batching and pipelining are performance optimization techniques that amortize fixed costs across multiple operations by grouping them together.

<div class="grid cards">
  <div class="card">
    <h3>🎯 Purpose</h3>
    <p>Transform multiple individual requests into grouped operations to reduce overhead and improve throughput</p>
  </div>
  <div class="card">
    <h3>🔧 Problem</h3>
    <p>Individual requests incur fixed costs (network RTT, protocol overhead, context switching) that dominate for small operations</p>
  </div>
  <div class="card">
    <h3>💡 Solution</h3>
    <p>Aggregate multiple requests and process them together, amortizing fixed costs across the batch</p>
  </div>
</div>

## Core Concepts

### Batching vs Pipelining

```mermaid
graph TB
    subgraph "Individual Requests"
        A1[Request 1] -->|RTT| R1[Response 1]
        A2[Request 2] -->|RTT| R2[Response 2]
        A3[Request 3] -->|RTT| R3[Response 3]
    end
    
    subgraph "Batching"
        B[Batch<br/>R1+R2+R3] -->|Single RTT| BR[Batch<br/>Response]
    end
    
    subgraph "Pipelining"
        P1[Request 1] --> PR1[Response 1]
        P2[Request 2] --> PR2[Response 2]
        P3[Request 3] --> PR3[Response 3]
        
        P1 -.->|No wait| P2
        P2 -.->|No wait| P3
    end
```

| Aspect | Batching | Pipelining |
|--------|----------|------------|
| **Mechanism** | Combine multiple requests into one | Send requests without waiting for responses |
| **Latency** | Higher (wait for batch) | Lower (immediate send) |
| **Throughput** | Maximum | High |
| **Complexity** | Medium | Low |
| **Error Handling** | All-or-nothing | Per-request |
| **Memory Usage** | Higher (buffering) | Lower |


## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Strategies

### Strategy Comparison

```mermaid
graph LR
    subgraph "Time-Based"
        T1[Request] --> TB[Buffer]
        T2[Request] --> TB
        TB -->|10ms timer| TS[Send Batch]
    end
    
    subgraph "Size-Based"
        S1[Request] --> SB[Buffer]
        S2[Request] --> SB
        SB -->|100 items| SS[Send Batch]
    end
    
    subgraph "Hybrid"
        H1[Request] --> HB[Buffer]
        H2[Request] --> HB
        HB -->|10ms OR<br/>100 items| HS[Send Batch]
    end
```

| Strategy | Pros | Cons | Use When |
|----------|------|------|----------|
| **Time-Based** | Predictable latency | May send small batches | Latency-sensitive |
| **Size-Based** | Optimal batch size | Unpredictable latency | Throughput-focused |
| **Hybrid** | Balanced approach | More complex | General purpose |
| **Adaptive** | Self-tuning | Most complex | Variable workloads |

### Adaptive Batching Algorithm

```mermaid
flowchart TD
    A[New Request] --> B{Buffer Full?}
    B -->|Yes| C[Send Immediately]
    B -->|No| D[Add to Buffer]
    D --> E{Timer Expired?}
    E -->|Yes| C
    E -->|No| F[Wait]
    
    C --> G[Measure Latency]
    G --> H{Latency > Target?}
    H -->|Yes| I[Decrease Batch Size]
    H -->|No| J{Throughput < Target?}
    J -->|Yes| K[Increase Batch Size]
    J -->|No| L[Maintain Size]
```

## Performance Characteristics

### Latency vs Throughput Trade-off

```mermaid
graph LR
    subgraph "Metrics"
        direction TB
        L[Latency] -.->|Inverse<br/>Relationship| T[Throughput]
        BS[Batch Size] -->|Increases| T
        BS -->|Increases| L
    end
```

| Batch Size | Latency | Throughput | Overhead/Request |
|------------|---------|------------|------------------|
| 1 | Minimum | Minimum | Maximum |
| 10 | +5ms | 8x | 10% |
| 100 | +20ms | 50x | 1% |
| 1000 | +100ms | 200x | 0.1% |

### Cost Analysis

<div class="decision-box">
<h4>🔍 When Batching Wins</h4>

**Fixed Cost per Request**: `C_fixed`  
**Variable Cost per Item**: `C_var`  
**Batch Size**: `N`

**Without Batching**: `N × (C_fixed + C_var)`  
**With Batching**: `C_fixed + N × C_var`

**Savings**: `(N - 1) × C_fixed`
</div>

## Real-World Implementations

### Redis Pipelining

```mermaid
sequenceDiagram
    participant Client
    participant Redis
    
    Note over Client,Redis: Without Pipelining (3 RTTs)
    Client->>Redis: SET key1 value1
    Redis->>Client: OK
    Client->>Redis: SET key2 value2
    Redis->>Client: OK
    Client->>Redis: SET key3 value3
    Redis->>Client: OK
    
    Note over Client,Redis: With Pipelining (1 RTT)
    Client->>Redis: SET key1 value1<br/>SET key2 value2<br/>SET key3 value3
    Redis->>Client: OK<br/>OK<br/>OK
```

**Performance Impact**:
- Single commands: ~100 ops/sec (network limited)
- Pipelined: ~500,000 ops/sec (CPU limited)
- 5000x improvement for small operations

### HTTP/2 Multiplexing

```mermaid
graph TB
    subgraph "HTTP/1.1"
        C1[Client] -->|Request 1| S1[Server]
        S1 -->|Response 1| C1
        C1 -->|Request 2| S1
        S1 -->|Response 2| C1
    end
    
    subgraph "HTTP/2"
        C2[Client] ==>|Stream 1| S2[Server]
        C2 ==>|Stream 2| S2
        C2 ==>|Stream 3| S2
        S2 ==>|Responses<br/>Interleaved| C2
    end
```

### Database Batch Operations

| Operation Type | Individual Time | Batch Time (1000) | Speedup |
|----------------|-----------------|-------------------|---------|
| INSERT | 5ms × 1000 = 5s | 50ms | 100x |
| UPDATE | 4ms × 1000 = 4s | 40ms | 100x |
| DELETE | 3ms × 1000 = 3s | 30ms | 100x |


## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Patterns

### Producer-Consumer with Batching

```mermaid
graph LR
    P1[Producer 1] --> Q[Queue]
    P2[Producer 2] --> Q
    P3[Producer 3] --> Q
    
    Q --> B[Batcher]
    B -->|Batch of N| C[Consumer]
    
    B -.->|Timer| B
    B -.->|Size Check| B
```

### Scatter-Gather with Batching

```mermaid
graph TB
    C[Coordinator] -->|Batched Request| S1[Shard 1]
    C -->|Batched Request| S2[Shard 2]
    C -->|Batched Request| S3[Shard 3]
    
    S1 -->|Batch Response| A[Aggregator]
    S2 -->|Batch Response| A
    S3 -->|Batch Response| A
    
    A -->|Combined Result| C
```

## Anti-Patterns

### When NOT to Use Batching

<div class="failure-vignette">
<h4>❌ Batching Failures</h4>

1. **Large Individual Items**: Batching 1MB objects provides minimal benefit
2. **Heterogeneous Operations**: Mixing reads and writes can cause conflicts
3. **Real-time Systems**: Added latency violates SLA requirements
4. **Stateful Operations**: Operations that depend on previous results
5. **Limited Memory**: Buffering can cause OOM in constrained environments
</div>

### Common Pitfalls

| Pitfall | Symptom | Solution |
|---------|---------|----------|
| **Head-of-line Blocking** | One slow item delays entire batch | Use timeouts, split batches |
| **Memory Exhaustion** | OOM from large buffers | Set maximum batch size |
| **Latency Spikes** | P99 latency increases | Use hybrid strategy |
| **Error Amplification** | One error fails entire batch | Implement partial success |

## Design Decisions

### Choosing Batch Size

```mermaid
flowchart TD
    A[Start] --> B{Latency<br/>Sensitive?}
    B -->|Yes| C[Small Batches<br/>10-100]
    B -->|No| D{Memory<br/>Constrained?}
    D -->|Yes| E[Medium Batches<br/>100-1000]
    D -->|No| F{Network<br/>Overhead High?}
    F -->|Yes| G[Large Batches<br/>1000-10000]
    F -->|No| H[Adaptive<br/>Strategy]
```

#
## Level 1: Intuition (5 minutes)

*Start your journey with relatable analogies*

### The Elevator Pitch
[Pattern explanation in simple terms]

### Real-World Analogy
[Everyday comparison that explains the concept]

## Level 2: Foundation (10 minutes)

*Build core understanding*

### Core Concepts
- Key principle 1
- Key principle 2
- Key principle 3

### Basic Example
```mermaid
graph LR
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

## Level 3: Deep Dive (15 minutes)

*Understand implementation details*

### How It Really Works
[Technical implementation details]

### Common Patterns
[Typical usage patterns]

## Level 4: Expert (20 minutes)

*Master advanced techniques*

### Advanced Configurations
[Complex scenarios and optimizations]

### Performance Tuning
[Optimization strategies]

## Level 5: Mastery (30 minutes)

*Apply in production*

### Real-World Case Studies
[Production examples from major companies]

### Lessons from the Trenches
[Common pitfalls and solutions]


## Decision Matrix

```mermaid
graph TD
    Start[Need This Pattern?] --> Q1{High Traffic?}
    Q1 -->|Yes| Q2{Distributed System?}
    Q1 -->|No| Simple[Use Simple Approach]
    Q2 -->|Yes| Q3{Complex Coordination?}
    Q2 -->|No| Basic[Use Basic Pattern]
    Q3 -->|Yes| Advanced[Use This Pattern]
    Q3 -->|No| Intermediate[Consider Alternatives]
    
    style Start fill:#f9f,stroke:#333,stroke-width:2px
    style Advanced fill:#bfb,stroke:#333,stroke-width:2px
    style Simple fill:#ffd,stroke:#333,stroke-width:2px
```

### Quick Decision Table

| Factor | Low Complexity | Medium Complexity | High Complexity |
|--------|----------------|-------------------|-----------------|
| Team Size | < 5 developers | 5-20 developers | > 20 developers |
| Traffic | < 1K req/s | 1K-100K req/s | > 100K req/s |
| Data Volume | < 1GB | 1GB-1TB | > 1TB |
| **Recommendation** | ❌ Avoid | ⚠️ Consider | ✅ Implement |

## Implementation Checklist

<div class="decision-box">
<h4>✅ Batching Implementation Guide</h4>

**Must Have**:
- [ ] Maximum batch size limit
- [ ] Timeout mechanism
- [ ] Error handling per item
- [ ] Metrics collection
- [ ] Back-pressure handling

**Should Have**:
- [ ] Adaptive sizing
- [ ] Priority queues
- [ ] Partial batch sending
- [ ] Circuit breaker
- [ ] Request deduplication

**Nice to Have**:
- [ ] Compression
- [ ] Request coalescing
- [ ] Predictive batching
- [ ] Multi-level batching
</div>

## Performance Monitoring

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Batch Size** | Items per batch | Depends on use case |
| **Queue Depth** | Pending items | < 1000 |
| **Batch Latency** | Time to fill batch | < 50ms |
| **Processing Time** | Batch execution time | < 100ms |
| **Throughput** | Items/second | Maximize |
| **Error Rate** | Failed batches | < 0.1% |

### Observability

```mermaid
graph TB
    M[Metrics] --> D[Dashboard]
    L[Logs] --> D
    T[Traces] --> D
    
    D --> A[Alerts]
    A -->|Queue Full| P1[Increase Workers]
    A -->|High Latency| P2[Reduce Batch Size]
    A -->|Low Throughput| P3[Increase Batch Size]
```

## Related Patterns

- [Work Distribution](../part2-pillars/1-work-distribution/index.md) - Batching as work distribution strategy
- [Circuit Breaker](circuit-breaker.md) - Protecting batch processors
- [Bulkhead](bulkhead.md) - Isolating batch processing
- [Queue-Based Load Leveling](queue-load-leveling.md) - Buffering for batches
- [Saga Pattern](saga.md) - Managing batch transactions

## References

<div class="truth-box">
<h4>🔑 Key Insights</h4>

1. **Amortization is Key**: Fixed costs dominate small operations
2. **Latency vs Throughput**: Fundamental trade-off in batch sizing
3. **Adaptive is Best**: Self-tuning based on workload
4. **Partial Success**: Design for item-level error handling
5. **Monitor Everything**: Batch performance is highly workload-dependent
</div>

### Further Reading

- [Little's Law](../architects-handbook/quantitative-analysis/littles-law.md) - Queue theory for batch systems
- [Queueing Theory](../architects-handbook/quantitative-analysis/queueing-models.md) - Mathematical foundations
- [Capacity Planning](../quantitative/capacity-planning.md) - Sizing batch systems
- [Performance Testing](../human-factors/performance-testing.md) - Validating batch performance