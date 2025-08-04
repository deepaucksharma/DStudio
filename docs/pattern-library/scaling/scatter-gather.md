---
best-for:
- Search engines aggregating from multiple shards
- Microservice API composition and aggregation
- Real-time dashboards pulling from multiple sources
category: scaling
current_relevance: mainstream
description: Parallel request distribution and result aggregation pattern for efficient
  distributed processing
difficulty: intermediate
essential_question: How do we handle increasing load without sacrificing performance
  using scatter-gather?
excellence_tier: silver
introduced: 2008-06
last-updated: 2025-01-26
pattern_status: use-with-expertise
prerequisites:
- async-messaging
- load-balancing
- circuit-breaker
reading-time: 15 min
status: complete
tagline: Master scatter-gather for distributed systems success
title: Scatter-Gather
trade-offs:
  cons:
  - Increased resource consumption from parallelism
  - Complex error handling and timeout management
  - Potential for thundering herd problems
  pros:
  - Reduces overall latency through parallelization
  - Enables graceful degradation with partial results
  - Scales well with independent services
type: pattern
when-not-to-use: When sequential processing is required or when the overhead of parallelization
  exceeds benefits
when-to-use: When you need to query multiple services in parallel and aggregate results
---

## Essential Question

**How do we handle increasing load without sacrificing performance using scatter-gather?**


# Scatter-Gather

!!! warning "🥈 Silver Tier Pattern"
    **Parallel power with coordination complexity** • Use when parallelization benefits outweigh orchestration overhead
    
    Scatter-Gather can reduce latency by up to 10x for independent service calls but requires careful timeout tuning, error handling strategies, and resource pool management. Consider simpler sequential calls for small request volumes.

!!! success "Problem → Solution"
    **Problem**: Need to query multiple services and aggregate results efficiently  
    **Solution**: Distribute requests in parallel, then gather and combine responses

## Architecture

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

## Request Flow Patterns

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

## Aggregation Strategies

| Strategy | Description | Use Case | Pros | Cons |
|----------|-------------|----------|------|------|
| **All Responses** | Wait for all services | Complete data required | Full result set | Slowest service bottleneck |
| **First-N** | Return after N responses | Speed critical | Fast response | Potentially incomplete |
| **Quorum** | Majority agreement | Consensus needed | Balance speed/accuracy | Complex for ties |
| **Timeout-Based** | Best effort within time | SLA constrained | Predictable latency | May miss responses |
| **Quality-Based** | Sufficient quality threshold | Search/recommendations | Adaptive performance | Quality metrics needed |


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

### Futures-Based Approach

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

### Error Handling Strategies

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

## Performance Optimization

### Parallel Execution Benefits

| Scenario | Sequential Time | Scatter-Gather Time | Improvement |
|----------|----------------|---------------------|-------------|
| 4 services × 100ms | 400ms | 100ms | 4× faster |
| 10 services × 50ms | 500ms | 50ms | 10× faster |
| Mixed latencies (50,100,150,200ms) | 500ms | 200ms | 2.5× faster |

### Resource Pool Management

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

## Real-World Examples

### Search Engine Architecture

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

### Microservices Aggregation

```mermaid
graph TD
    A[Input] --> B[Process]
    B --> C[Output]
    B --> D[Error Handling]
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bfb,stroke:#333,stroke-width:2px
    style D fill:#fbb,stroke:#333,stroke-width:2px
```

<details>
<summary>View implementation code</summary>

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

</details>

## Comparison with Related Patterns

| Pattern | Scatter-Gather | Map-Reduce | Fork-Join | Pub-Sub |
|---------|---------------|------------|-----------|---------|
| **Purpose** | Query aggregation | Data processing | Divide & conquer | Event distribution |
| **Communication** | Request-response | Batch processing | Recursive splitting | Fire-and-forget |
| **Result Handling** | Real-time aggregation | Staged reduction | Recursive merge | Independent handlers |
| **Latency** | Low (parallel) | High (batch) | Medium | N/A |
| **Use Case** | Service queries | Big data | Computation | Events |


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