---
title: Event-Driven Architecture
description: Service A → [OrderPlaced] → Event Bus
                              ↓ ↓ ↓
                    Inventory Payment Shipping
                    Servic...
type: pattern
difficulty: beginner
reading_time: 10 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Event-Driven Architecture**

# Event-Driven Architecture

**Everything is an event; the universe is eventual**

## THE PROBLEM

```proto
Synchronous coupling creates brittleness:
Service A calls B calls C calls D
- One slow service slows all
- One failure fails all
- Changes require coordination
```

## THE SOLUTION

```proto
Events enable autonomous services:

Service A → [OrderPlaced] → Event Bus
                              ↓ ↓ ↓
                    Inventory Payment Shipping
                    Service   Service Service
                    (async)   (async)  (async)
```

## Event Patterns Hierarchy

```javascript
1. EVENT NOTIFICATION
   "Something happened"
   {type: "OrderPlaced", orderId: 123}

2. EVENT-CARRIED STATE TRANSFER
   "Here's what changed"
   {type: "OrderPlaced", order: {...full data...}}

3. EVENT SOURCING
   "Events are the source of truth"
   [Created] → [Updated] → [Shipped] = Current State

4. CQRS
   "Commands create events create queries"
   Command → Event → Read Model
```

## IMPLEMENTATION

```python
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Callable
import asyncio

class EventPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10

@dataclass
class Event:
    id: str
    type: str
    payload: dict
    metadata: dict
    priority: EventPriority = EventPriority.NORMAL

class EventBus:
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.dlq = []  # Dead letter queue

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)

    def publish(self, event: Event):
        handlers = self.subscribers.get(event.type, [])
        handlers.extend(self.subscribers.get('*', []))  # Wildcard

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(self._async_handle(handler, event))
                else:
                    handler(event)
            except Exception as e:
                print(f"Handler {handler.__name__} failed: {e}")
                self.dlq.append((event, handler, e))

    async def _async_handle(self, handler, event):
        try:
            await handler(event)
        except Exception as e:
            print(f"Async handler {handler.__name__} failed: {e}")
            self.dlq.append((event, handler, e))

# Saga orchestration via events
class OrderSaga:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.state = {}

        # Subscribe to events
        event_bus.subscribe('OrderPlaced', self.handle_order_placed)
        event_bus.subscribe('PaymentProcessed', self.handle_payment)
        event_bus.subscribe('PaymentFailed', self.handle_payment_failed)
        event_bus.subscribe('InventoryReserved', self.handle_inventory)
        event_bus.subscribe('InventoryFailed', self.handle_inventory_failed)

    async def handle_order_placed(self, event: Event):
        order_id = event.payload['order_id']
        self.state[order_id] = {
            'status': 'pending_payment',
            'order': event.payload
        }

        # Trigger payment
        self.event_bus.publish(Event(
            id=f"pay_{order_id}",
            type='ProcessPayment',
            payload={
                'order_id': order_id,
                'amount': event.payload['total']
            },
            metadata={'saga_id': order_id}
        ))

    async def handle_payment(self, event: Event):
        order_id = event.payload['order_id']
        self.state[order_id]['status'] = 'pending_inventory'

        # Trigger inventory reservation
        self.event_bus.publish(Event(
            id=f"inv_{order_id}",
            type='ReserveInventory',
            payload={
                'order_id': order_id,
                'items': self.state[order_id]['order']['items']
            },
            metadata={'saga_id': order_id}
        ))

    async def handle_payment_failed(self, event: Event):
        order_id = event.payload['order_id']
        self.state[order_id]['status'] = 'failed'

        # Compensate - cancel order
        self.event_bus.publish(Event(
            id=f"cancel_{order_id}",
            type='OrderCancelled',
            payload={'order_id': order_id, 'reason': 'payment_failed'},
            metadata={'saga_id': order_id}
        ))

# Event store with replay
class EventStore:
    def __init__(self):
        self.events = []
        self.snapshots = {}

    def append(self, aggregate_id: str, event: Event):
        self.events.append({
            'aggregate_id': aggregate_id,
            'event': event,
            'timestamp': time.time()
        })

    def get_events(self, aggregate_id: str, after_version: int = 0):
        return [
            e['event'] for e in self.events
            if e['aggregate_id'] == aggregate_id
        ][after_version:]

    def replay_to(self, aggregate_id: str, target: object):
        """Replay events to rebuild state"""
        events = self.get_events(aggregate_id)
        for event in events:
            target.apply(event)
        return target
```

## Event Design Best Practices

```python
# Good event design
class OrderEvent:
    @staticmethod
    def order_placed(order_id, customer_id, items, total):
        return Event(
            id=str(uuid4()),
            type='order.placed',  # Namespaced
            payload={
                'order_id': order_id,
                'customer_id': customer_id,
                'items': items,
                'total': total
            },
            metadata={
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0',
                'source': 'order-service',
                'correlation_id': str(uuid4())
            }
        )
```

## ✓ CHOOSE THIS WHEN:
• Need loose coupling between services
• Complex workflows across teams
• Audit trail requirements
• High scalability needs
• Multiple consumers of same data

## ⚠️ BEWARE OF:
• Debugging event flows
• Out-of-order delivery
• Duplicate events
• Event schema evolution
• Eventual consistency confusion

## REAL EXAMPLES
• **Netflix**: 150 billion events/day
• **Uber**: Trip events drive 100+ services
• **PayPal**: Payment events across systems

---

**Previous**: [← Edge Computing/IoT Patterns](edge-computing.md) | **Next**: [Event Sourcing Pattern →](event-sourcing.md)
## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical

## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems

## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand

## 💻 Code Sample

### Basic Implementation

```python
class Event_DrivenPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"

    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)

        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)

    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold

    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass

    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}

    def _record_success(self):
        self.metrics.record_success()

    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = Event_DrivenPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
event_driven:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_event_driven_behavior():
    pattern = Event_DrivenPattern(test_config)

    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'

    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'

    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```
