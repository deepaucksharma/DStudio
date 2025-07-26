---
title: Scatter-Gather
description: Parallel request distribution and result aggregation pattern for efficient distributed processing
type: pattern
category: communication
difficulty: intermediate
reading_time: 15 min
prerequisites: [async-messaging, load-balancing, circuit-breaker]
when_to_use: When you need to query multiple services in parallel and aggregate results
when_not_to_use: When sequential processing is required or when the overhead of parallelization exceeds benefits
status: complete
last_updated: 2025-01-26
---

# Scatter-Gather

!!! success "Problem → Solution"
    **Problem**: Need to query multiple services and aggregate results efficiently  
    **Solution**: Distribute requests in parallel, then gather and combine responses

## Architecture

```mermaid
graph TB
    Client[Client]
    SG[Scatter-Gather<br/>Coordinator]
    S1[Service 1]
    S2[Service 2]
    S3[Service 3]
    S4[Service 4]
    
    Client -->|Request| SG
    SG -->|Scatter| S1
    SG -->|Scatter| S2
    SG -->|Scatter| S3
    SG -->|Scatter| S4
    
    S1 -.->|Response| SG
    S2 -.->|Response| SG
    S3 -.->|Response| SG
    S4 -.->|Response| SG
    
    SG -->|Aggregated<br/>Result| Client
    
    style SG fill:#5448C8,stroke:#333,stroke-width:2px,color:#fff
```

## Request Flow Patterns

```mermaid
sequenceDiagram
    participant C as Client
    participant SG as Scatter-Gather
    participant S1 as Service 1
    participant S2 as Service 2
    participant S3 as Service 3
    
    C->>SG: Request
    
    par Parallel Execution
        SG->>S1: Scatter Request
        and
        SG->>S2: Scatter Request
        and
        SG->>S3: Scatter Request
    end
    
    S2-->>SG: Response (50ms)
    S1-->>SG: Response (100ms)
    S3-->>SG: Response (150ms)
    
    SG->>SG: Aggregate Results
    SG-->>C: Combined Response
    
    Note over SG: Total time: 150ms<br/>(vs 300ms sequential)
```

## Aggregation Strategies

| Strategy | Description | Use Case | Pros | Cons |
|----------|-------------|----------|------|------|
| **All Responses** | Wait for all services | Complete data required | Full result set | Slowest service bottleneck |
| **First-N** | Return after N responses | Speed critical | Fast response | Potentially incomplete |
| **Quorum** | Majority agreement | Consensus needed | Balance speed/accuracy | Complex for ties |
| **Timeout-Based** | Best effort within time | SLA constrained | Predictable latency | May miss responses |
| **Quality-Based** | Sufficient quality threshold | Search/recommendations | Adaptive performance | Quality metrics needed |

## Implementation Patterns

### Futures-Based Approach

```mermaid
flowchart TB
    Start[Incoming Request]
    Create[Create Future<br/>for Each Service]
    Submit[Submit All<br/>Requests]
    
    Wait{Aggregation<br/>Strategy}
    All[Wait All<br/>Futures]
    FirstN[Wait First N<br/>Futures]
    Timeout[Wait Until<br/>Timeout]
    
    Collect[Collect<br/>Results]
    Aggregate[Apply<br/>Aggregation Logic]
    Return[Return<br/>Combined Result]
    
    Start --> Create
    Create --> Submit
    Submit --> Wait
    
    Wait -->|All Required| All
    Wait -->|Speed Priority| FirstN
    Wait -->|SLA Bound| Timeout
    
    All --> Collect
    FirstN --> Collect
    Timeout --> Collect
    
    Collect --> Aggregate
    Aggregate --> Return
    
    style Wait fill:#00BCD4,stroke:#333,stroke-width:2px,color:#fff
```

### Error Handling Strategies

```mermaid
graph TB
    Request[Request]
    Scatter[Scatter Phase]
    
    S1[Service 1<br/>✓ Success]
    S2[Service 2<br/>✗ Timeout]
    S3[Service 3<br/>✓ Success]
    S4[Service 4<br/>✗ Error]
    
    Request --> Scatter
    Scatter --> S1
    Scatter --> S2
    Scatter --> S3
    Scatter --> S4
    
    Gather[Gather Phase]
    S1 --> Gather
    S2 -.->|Timeout| Gather
    S3 --> Gather
    S4 -.->|Error| Gather
    
    Decision{Error<br/>Strategy}
    Gather --> Decision
    
    Partial[Return Partial<br/>Results]
    Retry[Retry Failed<br/>Services]
    Fail[Fail Entire<br/>Request]
    Fallback[Use Fallback<br/>Values]
    
    Decision -->|Degrade Gracefully| Partial
    Decision -->|Critical Service| Retry
    Decision -->|All Required| Fail
    Decision -->|Default Available| Fallback
    
    style Decision fill:#F44336,stroke:#333,stroke-width:2px,color:#fff
```

## Performance Optimization

### Parallel Execution Benefits

| Scenario | Sequential Time | Scatter-Gather Time | Improvement |
|----------|----------------|---------------------|-------------|
| 4 services × 100ms | 400ms | 100ms | 4× faster |
| 10 services × 50ms | 500ms | 50ms | 10× faster |
| Mixed latencies (50,100,150,200ms) | 500ms | 200ms | 2.5× faster |

### Resource Pool Management

```mermaid
graph LR
    subgraph Thread Pool
        T1[Thread 1]
        T2[Thread 2]
        T3[Thread 3]
        T4[Thread 4]
    end
    
    subgraph Request Queue
        R1[Request A]
        R2[Request B]
        R3[Request C]
    end
    
    subgraph Services
        S1[Service 1]
        S2[Service 2]
        S3[Service 3]
        S4[Service 4]
        S5[Service 5]
        S6[Service 6]
    end
    
    R1 --> T1
    R1 --> T2
    R2 --> T3
    R2 --> T4
    
    T1 --> S1
    T2 --> S2
    T3 --> S3
    T4 --> S4
    
    style T1 fill:#5448C8,stroke:#333,stroke-width:2px,color:#fff
    style T2 fill:#5448C8,stroke:#333,stroke-width:2px,color:#fff
    style T3 fill:#5448C8,stroke:#333,stroke-width:2px,color:#fff
    style T4 fill:#5448C8,stroke:#333,stroke-width:2px,color:#fff
```

## Real-World Examples

### Search Engine Architecture

```mermaid
graph TB
    Query[Search Query]
    SG[Scatter-Gather<br/>Coordinator]
    
    subgraph Shards
        S1[Shard 1<br/>0-25%]
        S2[Shard 2<br/>25-50%]
        S3[Shard 3<br/>50-75%]
        S4[Shard 4<br/>75-100%]
    end
    
    subgraph Features
        Web[Web Results]
        Image[Image Results]
        News[News Results]
        Video[Video Results]
    end
    
    Query --> SG
    SG --> S1
    SG --> S2
    SG --> S3
    SG --> S4
    
    SG --> Web
    SG --> Image
    SG --> News
    SG --> Video
    
    Rank[Ranking<br/>Service]
    Result[Blended<br/>Results]
    
    S1 --> Rank
    S2 --> Rank
    S3 --> Rank
    S4 --> Rank
    Web --> Rank
    Image --> Rank
    News --> Rank
    Video --> Rank
    
    Rank --> Result
```

### Microservices Aggregation

```mermaid
graph TB
    API[API Gateway]
    SG[Product Page<br/>Aggregator]
    
    subgraph Services
        Catalog[Product<br/>Catalog]
        Pricing[Pricing<br/>Service]
        Inventory[Inventory<br/>Service]
        Reviews[Reviews<br/>Service]
        Recommend[Recommendations]
    end
    
    API --> SG
    SG -->|Get Details| Catalog
    SG -->|Get Price| Pricing
    SG -->|Check Stock| Inventory
    SG -->|Get Reviews| Reviews
    SG -->|Get Similar| Recommend
    
    subgraph Response Times
        CT[Catalog: 50ms]
        PT[Pricing: 30ms]
        IT[Inventory: 40ms]
        RT[Reviews: 100ms]
        RCT[Recommend: 150ms]
    end
    
    Note[Total Time: 150ms<br/>vs 370ms sequential]
```

## Comparison with Related Patterns

| Pattern | Scatter-Gather | Map-Reduce | Fork-Join | Pub-Sub |
|---------|---------------|------------|-----------|---------|
| **Purpose** | Query aggregation | Data processing | Divide & conquer | Event distribution |
| **Communication** | Request-response | Batch processing | Recursive splitting | Fire-and-forget |
| **Result Handling** | Real-time aggregation | Staged reduction | Recursive merge | Independent handlers |
| **Latency** | Low (parallel) | High (batch) | Medium | N/A |
| **Use Case** | Service queries | Big data | Computation | Events |

## Implementation Considerations

!!! warning "Common Pitfalls"
    - **Thread exhaustion**: Limit concurrent requests
    - **Timeout cascades**: Set appropriate timeouts
    - **Memory pressure**: Stream large results
    - **Partial failures**: Define clear degradation strategy

!!! tip "Best Practices"
    - Use circuit breakers for each downstream service
    - Implement request deduplication
    - Cache aggregated results when appropriate
    - Monitor individual service latencies
    - Set service-specific timeouts

## When to Use

✅ **Use Scatter-Gather when:**
- Multiple independent data sources
- Parallel processing improves latency
- Partial results are acceptable
- Services have similar response times

❌ **Avoid when:**
- Sequential dependencies exist
- Single source of truth required
- Overhead exceeds parallelization benefits
- Strong consistency needed

## Related Patterns

- [**Circuit Breaker**](circuit-breaker.md) - Protect against service failures
- [**Load Balancing**](load-balancing.md) - Distribute scatter requests
- [**Saga**](saga.md) - Coordinate distributed transactions
- [**API Gateway**](api-gateway.md) - Common implementation location