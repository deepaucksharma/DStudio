---
title: Saga Pattern
description: Manage distributed transactions without two-phase commit
pattern_status: recommended
category: data-management
---

## The Complete Blueprint

The Saga pattern manages distributed transactions across multiple services by breaking them into a sequence of local transactions, where each service performs its own local transaction and publishes events to trigger the next step. Unlike traditional two-phase commit which locks resources and doesn't scale, sagas maintain eventual consistency through a choreographed or orchestrated sequence of operations with explicit compensation logic for rollback scenarios. When a step in the saga fails, compensating transactions are executed in reverse order to undo the changes made by preceding steps, ensuring the system returns to a consistent state. This pattern is essential for complex business transactions that span multiple services - like an e-commerce order that involves inventory, payment, shipping, and notification services - where each step must complete successfully or the entire transaction must be rolled back. Sagas excel in microservices architectures where you need transactional guarantees without the coupling and performance penalties of distributed locks.

```mermaid
graph TB
    subgraph "Saga Pattern Complete System"
        subgraph "Transaction Flow"
            Start["Order Placed"]
            S1["1. Reserve<br/>Inventory"]
            S2["2. Process<br/>Payment"]
            S3["3. Create<br/>Shipment"]
            S4["4. Send<br/>Notification"]
            End["Order Complete"]
            
            Start --> S1
            S1 -->|Success| S2
            S2 -->|Success| S3
            S3 -->|Success| S4
            S4 -->|Success| End
        end
        
        subgraph "Compensation Flow"
            C4["Undo<br/>Notification"]
            C3["Cancel<br/>Shipment"]
            C2["Refund<br/>Payment"]
            C1["Release<br/>Inventory"]
            Failed["Transaction<br/>Rolled Back"]
            
            S3 -->|Failure| C2
            C2 --> C1
            C1 --> Failed
        end
        
        subgraph "Coordination"
            Orch["Orchestrator<br/>(Centralized)"]
            Chor["Events<br/>(Choreography)"]
        end
        
        style Start fill:#51cf66
        style End fill:#51cf66
        style Failed fill:#ff6b6b
    end
```

### What You'll Master

!!! success "By understanding the Saga pattern, you'll be able to:"
    - **Manage distributed transactions** - Coordinate multi-service operations without distributed locks
    - **Implement compensations** - Design rollback strategies for complex business flows
    - **Choose coordination styles** - Select between orchestration and choreography approaches
    - **Maintain consistency** - Achieve eventual consistency across service boundaries
    - **Handle partial failures** - Gracefully recover from failures at any step
    - **Scale transactions** - Process high-volume transactions without blocking

# Saga Pattern

## Core Concepts

### Orchestration vs Choreography

| Aspect | Orchestration | Choreography |
|--------|--------------|--------------|
| **Control** | Centralized orchestrator | Distributed via events |
| **Coupling** | Services coupled to orchestrator | Services loosely coupled |
| **Complexity** | Simple flow logic | Complex event chains |
| **Debugging** | Easy to trace | Harder to follow |
| **Scaling** | Orchestrator can bottleneck | Naturally distributed |

### Compensation Strategies

```mermaid
graph LR
    subgraph "Forward Transaction"
        T1["Reserve Room"] --> T2["Charge Card"] --> T3["Send Email"]
    end
    
    subgraph "Compensating Transaction"
        C3["Retract Email"] --> C2["Refund Card"] --> C1["Release Room"]
    end
    
    T2 -->|Failure| C2
```

## Implementation Patterns

### Orchestrated Saga

```python
class OrderSagaOrchestrator:
    def __init__(self):
        self.steps = [
            (self.reserve_inventory, self.release_inventory),
            (self.process_payment, self.refund_payment),
            (self.create_shipment, self.cancel_shipment),
            (self.send_notification, self.retract_notification)
        ]
    
    async def execute(self, order):
        completed_steps = []
        
        try:
            for step, compensate in self.steps:
                result = await step(order)
                completed_steps.append((compensate, result))
                
        except Exception as e:
            # Compensate in reverse order
            for compensate, result in reversed(completed_steps):
                await compensate(result)
            raise SagaFailedException(f"Failed at step {len(completed_steps)}")
```

### Choreographed Saga

```python
class InventoryService:
    async def handle_order_created(self, event):
        try:
            await self.reserve_inventory(event.order_id, event.items)
            await self.publish("InventoryReserved", {
                "order_id": event.order_id,
                "reservation_id": reservation_id
            })
        except InsufficientInventory:
            await self.publish("InventoryReservationFailed", {
                "order_id": event.order_id,
                "reason": "Insufficient inventory"
            })

class PaymentService:
    async def handle_inventory_reserved(self, event):
        try:
            await self.process_payment(event.order_id)
            await self.publish("PaymentProcessed", {
                "order_id": event.order_id,
                "transaction_id": transaction_id
            })
        except PaymentFailed:
            # Trigger compensation
            await self.publish("PaymentFailed", {
                "order_id": event.order_id,
                "reservation_id": event.reservation_id
            })
```

## Failure Handling

### State Machine Approach

```mermaid
stateDiagram-v2
    [*] --> OrderCreated
    OrderCreated --> InventoryReserved: Reserve Success
    OrderCreated --> Failed: Reserve Failed
    
    InventoryReserved --> PaymentProcessed: Payment Success
    InventoryReserved --> Compensating: Payment Failed
    
    PaymentProcessed --> ShipmentCreated: Shipment Success
    PaymentProcessed --> Compensating: Shipment Failed
    
    ShipmentCreated --> Completed: Notification Sent
    
    Compensating --> Failed: All Compensated
    Failed --> [*]
    Completed --> [*]
```

## Production Considerations

### Idempotency Requirements

Each step must be idempotent to handle:
- Retries after network failures
- Duplicate events in choreography
- Reprocessing after crashes

### Timeout Management

```yaml
saga_timeouts:
  reserve_inventory: 5s
  process_payment: 30s
  create_shipment: 10s
  send_notification: 2s
  total_saga: 60s
```

### Monitoring & Observability

Key metrics to track:
- Saga completion rate
- Average completion time
- Compensation trigger rate
- Step failure distribution

## Common Patterns

### Pivot Transaction

Some operations can't be compensated (e.g., sending email). Place these at the end:

```
Compensatable → Compensatable → Pivot → Retriable Only
```

### Semantic Lock

Reserve resources with expiration to prevent indefinite locks:

```python
await inventory.reserve(
    order_id=order.id,
    items=order.items,
    expires_in=timedelta(minutes=15)
)
```

## Real-World Examples

| Company | Use Case | Scale | Approach |
|---------|----------|-------|----------|
| **Uber** | Trip booking | 20M trips/day | Choreographed |
| **Amazon** | Order processing | 300+ orders/sec | Orchestrated |
| **Booking.com** | Hotel reservation | 1.5M bookings/day | Hybrid |
| **Airbnb** | Booking flow | 2M+ nights/day | Choreographed |

## Anti-Patterns to Avoid

1. **Synchronous Chains** - Don't chain synchronous calls
2. **Missing Timeouts** - Always set saga timeout
3. **Non-idempotent Steps** - Ensure all operations are idempotent
4. **Implicit Compensations** - Make rollback logic explicit
5. **Circular Dependencies** - Avoid circular event chains

## Related Patterns

- [Event Sourcing](./event-sourcing.md) - Store saga state as events
- [Outbox Pattern](./outbox.md) - Ensure event publication
- [Two-Phase Commit](../coordination/two-phase-commit.md) - Alternative approach
- [Circuit Breaker](../resilience/circuit-breaker.md) - Protect saga steps
- [Retry Pattern](../resilience/retry-backoff.md) - Handle transient failures

## See Also

- [Eventual Consistency](/pattern-library/data-management/eventual-consistency)
- [Event Streaming](/pattern-library/architecture/event-streaming)
- [Rate Limiting Pattern](/pattern-library/scaling/rate-limiting)