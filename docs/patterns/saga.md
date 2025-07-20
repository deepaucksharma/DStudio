---
title: Saga (Distributed Transactions)
description: "Manage distributed transactions using coordinated sequences of local transactions with compensation"
type: pattern
difficulty: advanced
reading_time: 25 min
prerequisites: []
pattern_type: "coordination"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Saga (Distributed Transactions)**

# Saga (Distributed Transactions)

**When ACID meets distributed reality**

## THE PROBLEM

```
Distributed transaction across services:
1. Debit payment account
2. Credit merchant account
3. Update inventory
4. Send notification

What if step 3 fails after 1 & 2 succeed?
```bash
## THE SOLUTION

```
Saga: A sequence of local transactions with compensations

Happy Path:          Failure Path:
T1 ✓                T1 ✓
T2 ✓                T2 ✓
T3 ✓                T3 ✗
T4 ✓                C2 ← Compensate
                    C1 ← Compensate
```bash
## Saga Patterns

```
1. ORCHESTRATION (Central Coordinator)
        Saga Orchestrator
       /      |      \
     T1      T2      T3

2. CHOREOGRAPHY (Event Chain)
   T1 → [Event] → T2 → [Event] → T3
```bash
## IMPLEMENTATION

```python
from abc import ABC, abstractmethod
from enum import Enum

class SagaStatus(Enum):
    STARTED = "started"
    RUNNING = "running"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"

class SagaStep(ABC):
    @abstractmethod
    async def execute(self, context):
        """Execute forward transaction"""
        pass

    @abstractmethod
    async def compensate(self, context):
        """Compensate on failure"""
        pass

# Example: Hotel Booking Saga
class BookHotelStep(SagaStep):
    def __init__(self, hotel_service):
        self.hotel_service = hotel_service

    async def execute(self, context):
        booking = await self.hotel_service.reserve(
            hotel_id=context['hotel_id'],
            dates=context['dates'],
            guest=context['guest']
        )
        context['hotel_booking_id'] = booking.id
        return booking

    async def compensate(self, context):
        if 'hotel_booking_id' in context:
            await self.hotel_service.cancel(
                context['hotel_booking_id']
            )

class ChargePaymentStep(SagaStep):
    def __init__(self, payment_service):
        self.payment_service = payment_service

    async def execute(self, context):
        charge = await self.payment_service.charge(
            amount=context['total_amount'],
            card=context['payment_card'],
            idempotency_key=context['saga_id']
        )
        context['payment_id'] = charge.id
        return charge

    async def compensate(self, context):
        if 'payment_id' in context:
            await self.payment_service.refund(
                context['payment_id']
            )

# Orchestrator implementation
class SagaOrchestrator:
    def __init__(self, saga_id):
        self.saga_id = saga_id
        self.steps = []
        self.completed_steps = []
        self.status = SagaStatus.STARTED
        self.context = {'saga_id': saga_id}

    def add_step(self, step: SagaStep):
        self.steps.append(step)
        return self

    async def execute(self):
        """Execute saga with automatic compensation"""
        self.status = SagaStatus.RUNNING

        try:
            # Forward path
            for step in self.steps:
                result = await step.execute(self.context)
                self.completed_steps.append(step)
                await self._save_progress()

            self.status = SagaStatus.COMPLETED
            return self.context

        except Exception as e:
            # Compensation path
            self.status = SagaStatus.COMPENSATING
            await self._compensate()
            self.status = SagaStatus.FAILED
            raise SagaFailedException(f"Saga {self.saga_id} failed: {e}")

    async def _compensate(self):
        """Run compensations in reverse order"""
        for step in reversed(self.completed_steps):
            try:
                await step.compensate(self.context)
                await self._save_progress()
            except Exception as e:
                # Log but continue compensating
                print(f"Compensation failed for {step}: {e}")

    async def _save_progress(self):
        """Persist saga state for recovery"""
        # In production, save to database
        pass

# Choreography implementation with event bus
class ChoreographySaga:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.sagas = {}  # Track active sagas

        # Subscribe to events
        event_bus.subscribe('TripBooked', self.handle_trip_booked)
        event_bus.subscribe('FlightBooked', self.handle_flight_booked)
        event_bus.subscribe('HotelBooked', self.handle_hotel_booked)
        event_bus.subscribe('PaymentCharged', self.handle_payment_charged)
        event_bus.subscribe('BookingFailed', self.handle_failure)

    async def handle_trip_booked(self, event):
        saga_id = event.correlation_id
        self.sagas[saga_id] = {
            'status': 'booking_flight',
            'trip': event.payload
        }

        # Trigger next step
        self.event_bus.publish(Event(
            type='BookFlight',
            payload={
                'flight_id': event.payload['flight_id'],
                'passengers': event.payload['passengers']
            },
            correlation_id=saga_id
        ))

    async def handle_flight_booked(self, event):
        saga_id = event.correlation_id
        self.sagas[saga_id]['flight_booking'] = event.payload
        self.sagas[saga_id]['status'] = 'booking_hotel'

        # Next step
        self.event_bus.publish(Event(
            type='BookHotel',
            payload={
                'hotel_id': self.sagas[saga_id]['trip']['hotel_id'],
                'dates': self.sagas[saga_id]['trip']['dates']
            },
            correlation_id=saga_id
        ))

    async def handle_failure(self, event):
        saga_id = event.correlation_id
        saga = self.sagas.get(saga_id)

        if not saga:
            return

        # Compensate based on how far we got
        if 'payment_id' in saga:
            self.event_bus.publish(Event(
                type='RefundPayment',
                payload={'payment_id': saga['payment_id']},
                correlation_id=saga_id
            ))

        if 'hotel_booking' in saga:
            self.event_bus.publish(Event(
                type='CancelHotel',
                payload={'booking_id': saga['hotel_booking']['id']},
                correlation_id=saga_id
            ))

        if 'flight_booking' in saga:
            self.event_bus.publish(Event(
                type='CancelFlight',
                payload={'booking_id': saga['flight_booking']['id']},
                correlation_id=saga_id
            ))
```bash
## Saga State Machine

```python
class SagaStateMachine:
    def __init__(self):
        self.states = {}
        self.transitions = {}

    def add_state(self, name, on_enter=None, on_exit=None):
        self.states[name] = {
            'on_enter': on_enter,
            'on_exit': on_exit
        }

    def add_transition(self, from_state, to_state, event, action=None):
        key = (from_state, event)
        self.transitions[key] = {
            'to_state': to_state,
            'action': action
        }

    async def handle_event(self, current_state, event, context):
        key = (current_state, event.type)

        if key not in self.transitions:
            return current_state  # No transition

        transition = self.transitions[key]

        # Exit current state
        if self.states[current_state]['on_exit']:
            await self.states[current_state]['on_exit'](context)

        # Execute transition action
        if transition['action']:
            await transition['action'](event, context)

        # Enter new state
        new_state = transition['to_state']
        if self.states[new_state]['on_enter']:
            await self.states[new_state]['on_enter'](context)

        return new_state
```

## ✓ CHOOSE THIS WHEN:
• Distributed transactions needed
• Each step can be made idempotent
• Compensation is possible
• Eventually consistent is OK
• Workflow spans multiple services

## ⚠️ BEWARE OF:
• Complexity of compensation logic
• Partial failure states
• Testing all failure paths
• Monitoring saga progress
• Long-running saga timeout

## REAL EXAMPLES
• **Uber**: Trip booking across services
• **Airbnb**: Reservation workflow
• **Amazon**: Order fulfillment pipeline

---

**Previous**: [← Retry & Backoff Strategies](retry-backoff.md) | **Next**: [Serverless/FaaS (Function-as-a-Service) →](serverless-faas.md)
---

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
class SagaPattern:
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
pattern = SagaPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
saga:
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
def test_saga_behavior():
    pattern = SagaPattern(test_config)

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

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes
**Objective**: Identify Saga (Distributed Transactions) in existing systems

**Task**:
Find 2 real-world examples where Saga (Distributed Transactions) is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Saga (Distributed Transactions)

**Scenario**: You need to implement Saga (Distributed Transactions) for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Saga (Distributed Transactions)
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Saga (Distributed Transactions)

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Saga (Distributed Transactions) be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Saga (Distributed Transactions) later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Saga (Distributed Transactions) in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**:
- How would you introduce Saga (Distributed Transactions) to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
