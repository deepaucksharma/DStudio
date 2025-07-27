---
title: Actor Model
description: Message-passing concurrency model with isolated actors communicating asynchronously
type: pattern
category: concurrency
difficulty: advanced
reading_time: 15 min
prerequisites: [concurrency, distributed-systems]
when_to_use: Building highly concurrent, fault-tolerant systems with millions of independent entities
when_not_to_use: Simple request-response applications, systems requiring shared mutable state
status: complete
last_updated: 2025-01-26
excellence_tier: bronze
pattern_status: legacy
modern_alternatives: ["service-mesh", "serverless-faas", "event-driven"]
still_valid_for: "Erlang/Elixir systems, specific IoT scenarios, academic study"
migration_guide: "/excellence/migrations/actor-to-service-mesh"
related_laws: [law2-asynchrony, law3-emergence, law6-human-api]
related_pillars: [work, control]
---

# Actor Model

!!! info "🥉 Bronze Tier Pattern"
    **Legacy pattern with limited modern applicability**
    
    While the Actor Model pioneered important concurrency concepts, modern alternatives like service mesh and serverless provide better solutions for most use cases. The complexity without clear benefits makes it unsuitable for new projects.
    
    **Consider instead:**
    - **Service Mesh** for microservice communication
    - **Serverless Functions** for isolated compute
    - **Event-Driven Architecture** for async processing

> *"Don't communicate by sharing memory; share memory by communicating."* - The actor model takes this principle to its logical extreme.

## Core Principles

```mermaid
graph TB
    subgraph "Actor Model Principles"
        A1[No Shared State] --> B1[Message Passing Only]
        A2[Location Transparency] --> B2[Actors Can Be Anywhere]
        A3[Asynchronous Processing] --> B3[Non-blocking Operations]
        A4[Supervision Hierarchy] --> B4[Fault Isolation]
    end
    
    style A1 fill:#e8f5e9
    style A2 fill:#e3f2fd
    style A3 fill:#fff3e0
    style A4 fill:#fce4ec
```

## Actor Hierarchy & Supervision

```mermaid
graph TD
    subgraph "Actor System"
        Root[Root Guardian]
        Root --> User[User Guardian]
        Root --> System[System Guardian]
        
        User --> S1[Supervisor 1]
        User --> S2[Supervisor 2]
        
        S1 --> W1[Worker 1]
        S1 --> W2[Worker 2]
        S1 --> W3[Worker 3]
        
        S2 --> DB1[DB Actor 1]
        S2 --> DB2[DB Actor 2]
        
        System --> Logger[Logger Actor]
        System --> Metrics[Metrics Actor]
    end
    
    style Root fill:#b39ddb
    style User fill:#90caf9
    style System fill:#a5d6a7
```

## Message Flow Architecture

```mermaid
sequenceDiagram
    participant Client
    participant Router as Router Actor
    participant Worker1 as Worker Actor 1
    participant Worker2 as Worker Actor 2
    participant DB as Database Actor
    
    Client->>Router: Request(id: 123)
    Router->>Router: Select worker
    Router->>Worker1: Process(id: 123)
    Worker1->>DB: Query(id: 123)
    DB-->>Worker1: Result(data)
    Worker1-->>Router: Response(data)
    Router-->>Client: Response(data)
    
    Note over Worker2: Idle - Can process<br/>other requests
    
    Router->>Worker2: Process(id: 456)
    Note over Worker1,Worker2: Concurrent processing
```

## Actor Implementation Components

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| **Mailbox** | Message queue for actor | - FIFO or priority ordering<br/>- Bounded/unbounded options<br/>- Overflow strategies |
| **Message Handler** | Process incoming messages | - Pattern matching<br/>- State transitions<br/>- Side effect isolation |
| **Supervision Strategy** | Handle child failures | - One-for-one restart<br/>- All-for-one restart<br/>- Escalate to parent |
| **Actor Context** | Runtime environment | - Self reference<br/>- Parent/children refs<br/>- System access |
| **Dispatcher** | Thread management | - Thread pool config<br/>- Scheduling strategy<br/>- Blocking I/O handling |

## Concurrency Models Comparison

| Aspect | Actor Model | Thread-Based | CSP (Channels) | Event Loop |
|--------|-------------|--------------|----------------|------------|
| **Communication** | Async messages | Shared memory + locks | Synchronous channels | Callbacks/Promises |
| **Isolation** | Complete | Manual via locks | Channel-based | Single thread |
| **Scalability** | Millions of actors | Limited by OS threads | Good | Limited by one thread |
| **Fault Tolerance** | Built-in supervision | Manual try-catch | Manual | Error callbacks |
| **Debugging** | Message traces | Thread dumps | Channel monitoring | Stack traces |
| **Use Case** | Distributed systems | CPU-bound tasks | Pipeline processing | I/O-bound tasks |

## Supervision Strategies

```mermaid
graph LR
    subgraph "Failure Handling"
        F[Child Failure] --> D{Supervision<br/>Decision}
        D -->|Resume| R[Continue Processing]
        D -->|Restart| RS[Restart Child]
        D -->|Stop| S[Stop Child]
        D -->|Escalate| E[Propagate to Parent]
        
        RS --> ST{Strategy}
        ST -->|One-for-One| O1[Restart Failed Only]
        ST -->|All-for-One| A1[Restart All Children]
        ST -->|Rest-for-One| R1[Restart Failed + Later]
    end
    
    style F fill:#ffcdd2
    style D fill:#fff9c4
    style E fill:#ffccbc
```

## Real-World Implementations

### Erlang/Elixir (BEAM VM)

<div class="decision-box">
<h4>WhatsApp Architecture</h4>

- **2M connections/server** using Erlang actors
- **Supervision trees** for 99.999% uptime
- **Hot code swapping** without downtime
- **Pattern**: One actor per user session

</div>

### Akka (JVM)

```scala
// Actor definition
class OrderProcessor extends Actor {
  def receive = {
    case Order(id, items) =>
      val total = items.map(_.price).sum
      sender() ! OrderConfirmation(id, total)
    case Cancel(id) =>
      // Handle cancellation
  }
}

// Supervision
class OrderSupervisor extends Actor {
  override val supervisorStrategy = 
    OneForOneStrategy(maxNrOfRetries = 10) {
      case _: SQLException => Restart
      case _: Exception => Escalate
    }
}
```

### Orleans (Virtual Actors)

| Feature | Orleans Approach | Traditional Actors |
|---------|------------------|-------------------|
| **Lifecycle** | Automatic activation/deactivation | Manual management |
| **Location** | Transparent migration | Fixed placement |
| **Persistence** | Built-in state management | Manual implementation |
| **Concurrency** | Turn-based (single-threaded) | Message interleaving |

## Message Patterns

```mermaid
graph TB
    subgraph "Common Patterns"
        P1[Request-Reply] --> D1[Correlation IDs]
        P2[Publish-Subscribe] --> D2[Event Bus Actor]
        P3[Scatter-Gather] --> D3[Aggregator Actor]
        P4[Routing Slip] --> D4[Chain of Actors]
        P5[Saga] --> D5[Coordinator Actor]
    end
    
    style P1 fill:#e1f5fe
    style P2 fill:#f3e5f5
    style P3 fill:#e8f5e9
    style P4 fill:#fff8e1
    style P5 fill:#fce4ec
```

## When to Use Actor Model

<div class="axiom-box">
<h4>Use Actor Model When:</h4>

✅ **High Concurrency**: Millions of independent entities  
✅ **Fault Tolerance**: Isolated failure domains required  
✅ **Distribution**: Natural fit for distributed systems  
✅ **State Encapsulation**: Each entity owns its state  
✅ **Event-Driven**: Async message processing fits domain  

</div>

<div class="failure-vignette">
<h4>Avoid Actor Model When:</h4>

❌ **Shared State**: Need efficient shared data structures  
❌ **Synchronous Operations**: Require immediate responses  
❌ **Simple CRUD**: Over-engineering for basic operations  
❌ **Data Processing**: Better suited for stream processing  
❌ **Team Expertise**: Steep learning curve for teams  

</div>

## Performance Characteristics

| Metric | Typical Range | Factors |
|--------|---------------|---------|
| **Message Throughput** | 1M-50M msgs/sec | Mailbox implementation, message size |
| **Actor Creation** | 1M actors/sec | Memory allocation, supervision setup |
| **Latency** | 1-100 μs | Message passing overhead, scheduling |
| **Memory/Actor** | 300B-2KB | State size, mailbox depth |

## Anti-Patterns to Avoid

<div class="failure-vignette">
<h4>Common Actor Model Mistakes</h4>

1. **Blocking Operations**: Never block in message handler
2. **Shared Mutable State**: Breaks isolation guarantees  
3. **Synchronous Asks**: Defeats async benefits
4. **Deep Hierarchies**: Hard to reason about failures
5. **Large Messages**: Use references for big data

</div>

## Implementation Checklist

- [ ] **Message Protocol**: Define immutable message types
- [ ] **Supervision Tree**: Design failure handling hierarchy
- [ ] **Mailbox Strategy**: Choose bounded vs unbounded
- [ ] **Dispatcher Config**: Tune thread pools for workload
- [ ] **Monitoring**: Add metrics for mailbox depth, processing time
- [ ] **Testing**: Use test probes for message verification
- [ ] **Deployment**: Plan for actor distribution across nodes

## Related Patterns

- [Event Sourcing](event-sourcing.md) - Natural fit for actor state
- [CQRS](cqrs.md) - Actors for command processing
- [Saga](saga.md) - Coordinate with actor supervisors
- [Circuit Breaker](circuit-breaker.md) - Protect external calls

## References

- [Hewitt's Original Paper (1973)](https://doi.org/10.3233/978-1-58603-578-1-151)
- [Akka Documentation](https://doc.akka.io/)
- [Orleans Documentation](https://dotnet.github.io/orleans/)
- [Erlang OTP Principles](https://erlang.org/doc/design_principles/des_princ.html)