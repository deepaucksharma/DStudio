---
title: Saga Pattern
description: Manage distributed transactions using coordinated sequences of local transactions with compensations
type: pattern
difficulty: advanced
reading_time: 35 min
prerequisites: 
  - "Microservices architecture"
  - "Event-driven systems"
  - "ACID transactions"
pattern_type: "coordination"
when_to_use: "Cross-service transactions, workflow orchestration, distributed business processes"
when_not_to_use: "Simple local transactions, strongly consistent requirements, simple CRUD operations"
related_axioms:
  - optimization
  - failure
  - chaos
  - knowledge
related_patterns:
  - "Event Sourcing"
  - "CQRS"
  - "Outbox Pattern"
status: complete
last_updated: 2025-07-21
---

# Saga Pattern

<div class="navigation-breadcrumb">
<a href="/">Home</a> > <a href="/patterns/">Patterns</a> > Saga Pattern
</div>

> "A distributed system is one in which the failure of a computer you didn't even know existed can render your own computer unusable"
> — Leslie Lamport

## The Essential Question

**How can we maintain data consistency across multiple services when ACID transactions can't span service boundaries?**

---

## Level 1: Intuition (5 minutes)

### The Story

Vacation booking requires: flight, hotel, car, payment. Traditional agents handled all at once - fail anywhere, cancel everything.

But with separate companies per booking, you can't "rollback" United when Hertz fails. You must explicitly cancel each success.

Saga pattern: sequence of local transactions with compensating actions.

### Visual Metaphor

```
Traditional Transaction:          Saga Pattern:

┌─────────────────┐              Step 1: Book Flight ✓
│ BEGIN           │              ↓
│  Book Flight    │              Step 2: Book Hotel ✓
│  Book Hotel     │              ↓
│  Book Car       │              Step 3: Book Car ✗
│  Charge Card    │              ↓
│ COMMIT/ROLLBACK │              Compensate: Cancel Hotel
└─────────────────┘              ↓
                                Compensate: Cancel Flight
All or Nothing                   Each step + compensation
```

### In One Sentence

**Saga Pattern**: Distributed transactions as local transaction sequences with compensating actions.

### Real-World Parallel

Like reversible dominoes - knock them down in sequence, but can stand them back up in reverse if needed.

---

## Level 2: Foundation (10 minutes)

### The Problem Space

<div class="failure-vignette">
<h4>🔥 Without Saga: Ticketmaster Disaster</h4>
Concert sale: Charged cards but seat reservation failed.
- 50K+ charged without tickets
- 3-week manual refunds
- $5M fees/penalties
- Major reputation damage
</div>

### Core Concept

Saga pattern essentials:

1. **Local Transactions**: Each service's ACID transaction
2. **Compensating Transactions**: Undo operations
3. **Coordination**: Orchestrated or choreographed
4. **Eventually Consistent**: Via saga completion
5. **Failure Recovery**: Reverse compensations

### Basic Architecture

```mermaid
graph LR
    subgraph "Orchestrated Saga"
        O[Saga Orchestrator]
        O --> S1[Service 1<br/>Transaction]
        O --> S2[Service 2<br/>Transaction]
        O --> S3[Service 3<br/>Transaction]
        O --> C1[Service 1<br/>Compensation]
        O --> C2[Service 2<br/>Compensation]
        
        style O fill:#f9f,stroke:#333,stroke-width:3px
    end
    
    subgraph "Choreographed Saga"
        E1[Service 1] -->|Event| E2[Service 2]
        E2 -->|Event| E3[Service 3]
        E3 -->|Failure| E2
        E2 -->|Compensate| E1
        
        style E1 fill:#9f9,stroke:#333,stroke-width:2px
        style E2 fill:#9f9,stroke:#333,stroke-width:2px
        style E3 fill:#f99,stroke:#333,stroke-width:2px
    end
```

### Key Benefits

1. **Consistency**: Without distributed locks
2. **Autonomy**: Service-owned data
3. **Recovery**: Automatic compensation
4. **Long-Running**: Extended workflows

### Trade-offs

| Aspect | Gain | Cost |
|--------|------|------|
| Consistency | Eventual consistency | No immediate consistency |
| Complexity | Service independence | Compensation logic |
| Debugging | Clear transaction flow | Distributed tracing needed |
| Testing | Isolated service tests | Complex integration tests |

---

## Level 3: Deep Dive (20 minutes)

### Detailed Architecture

```mermaid
graph TB
    subgraph "Saga Orchestrator Pattern"
        Client[Client Request]
        Client --> SO[Saga Orchestrator]
        
        SO --> SM[State Machine]
        SM --> P[Persistence]
        
        SO --> |1. Execute| T1[Payment Service<br/>Debit Account]
        SO --> |2. Execute| T2[Inventory Service<br/>Reserve Items]
        SO --> |3. Execute| T3[Shipping Service<br/>Create Shipment]
        SO --> |4. Execute| T4[Notification Service<br/>Send Confirmation]
        
        T3 -->|Failure| SO
        SO -->|3. Compensate| C2[Inventory Service<br/>Release Items]
        SO -->|2. Compensate| C1[Payment Service<br/>Credit Account]
        
        style SO fill:#f9f,stroke:#333,stroke-width:3px
        style SM fill:#bbf,stroke:#333,stroke-width:2px
    end
    
    subgraph "Saga Choreography Pattern"
        O[Order Service] -->|OrderCreated| PS[Payment Service]
        PS -->|PaymentDebited| IS[Inventory Service]
        IS -->|ItemsReserved| SS[Shipping Service]
        SS -->|ShipmentCreated| NS[Notification Service]
        
        SS -->|ShipmentFailed| IS
        IS -->|ReleaseItems| PS
        PS -->|RefundPayment| O
        
        EB[Event Bus]
        O -.-> EB
        PS -.-> EB
        IS -.-> EB
        SS -.-> EB
        NS -.-> EB
        
        style EB fill:#9f9,stroke:#333,stroke-width:2px
    end
```

### Implementation Patterns

#### Basic Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import uuid
import asyncio
import logging

# Saga Step Definition
class StepStatus(Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"

@dataclass
class SagaContext:
    """Shared context across saga steps"""
    saga_id: str
    initial_request: Dict[str, Any]
    step_results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.step_results is None:
            self.step_results = {}

class SagaStep(ABC):
    """Base class for saga steps"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = StepStatus.PENDING
        
    @abstractmethod
    async def execute(self, context: SagaContext) -> Any:
        """Execute the forward transaction"""
        pass
        
    @abstractmethod
    async def compensate(self, context: SagaContext) -> None:
        """Compensate (undo) the transaction"""
        pass
        
    def can_compensate(self) -> bool:
        """Check if this step can be compensated"""
        return self.status == StepStatus.COMPLETED

# Example Saga Steps
class CreateOrderStep(SagaStep):
    def __init__(self, order_service):
        super().__init__("create_order")
        self.order_service = order_service
        
    async def execute(self, context: SagaContext) -> str:
        self.status = StepStatus.EXECUTING
        try:
            order = await self.order_service.create_order(
                customer_id=context.initial_request['customer_id'],
                items=context.initial_request['items']
            )
            context.step_results['order_id'] = order.id
            self.status = StepStatus.COMPLETED
            return order.id
        except Exception as e:
            self.status = StepStatus.FAILED
            raise
            
    async def compensate(self, context: SagaContext) -> None:
        if 'order_id' in context.step_results:
            self.status = StepStatus.COMPENSATING
            await self.order_service.cancel_order(
                context.step_results['order_id']
            )
            self.status = StepStatus.COMPENSATED

class ProcessPaymentStep(SagaStep):
    def __init__(self, payment_service):
        super().__init__("process_payment")
        self.payment_service = payment_service
        
    async def execute(self, context: SagaContext) -> str:
        self.status = StepStatus.EXECUTING
        try:
            payment = await self.payment_service.charge(
                amount=context.initial_request['total_amount'],
                payment_method=context.initial_request['payment_method'],
                idempotency_key=f"{context.saga_id}-payment"
            )
            context.step_results['payment_id'] = payment.id
            self.status = StepStatus.COMPLETED
            return payment.id
        except Exception as e:
            self.status = StepStatus.FAILED
            raise
            
    async def compensate(self, context: SagaContext) -> None:
        if 'payment_id' in context.step_results:
            self.status = StepStatus.COMPENSATING
            await self.payment_service.refund(
                payment_id=context.step_results['payment_id'],
                reason="Saga compensation"
            )
            self.status = StepStatus.COMPENSATED

# Saga Orchestrator
class SagaOrchestrator:
    """Orchestrates saga execution with automatic compensation"""
    
    def __init__(self, saga_id: Optional[str] = None):
        self.saga_id = saga_id or str(uuid.uuid4())
        self.steps: List[SagaStep] = []
        self.completed_steps: List[SagaStep] = []
        self.status = "initialized"
        self.logger = logging.getLogger(__name__)
        
    def add_step(self, step: SagaStep) -> 'SagaOrchestrator':
        """Add a step to the saga"""
        self.steps.append(step)
        return self
        
    async def execute(self, initial_request: Dict[str, Any]) -> SagaContext:
        """Execute the saga with automatic compensation on failure"""
        context = SagaContext(
            saga_id=self.saga_id,
            initial_request=initial_request
        )
        
        self.status = "running"
        self.logger.info(f"Starting saga {self.saga_id}")
        
        try:
            # Execute steps in sequence
            for step in self.steps:
                self.logger.info(f"Executing step: {step.name}")
                
                result = await step.execute(context)
                self.completed_steps.append(step)
                
                # Persist saga state after each step
                await self._persist_state(context)
                
                self.logger.info(f"Step {step.name} completed: {result}")
                
            self.status = "completed"
            self.logger.info(f"Saga {self.saga_id} completed successfully")
            return context
            
        except Exception as e:
            self.logger.error(f"Saga {self.saga_id} failed at step {step.name}: {e}")
            self.status = "compensating"
            
            # Run compensations in reverse order
            await self._run_compensations(context)
            
            self.status = "failed"
            raise SagaFailedException(
                f"Saga {self.saga_id} failed and was compensated"
            ) from e
            
    async def _run_compensations(self, context: SagaContext):
        """Run compensation for completed steps in reverse order"""
        for step in reversed(self.completed_steps):
            if step.can_compensate():
                try:
                    self.logger.info(f"Compensating step: {step.name}")
                    await step.compensate(context)
                    await self._persist_state(context)
                except Exception as e:
                    self.logger.error(
                        f"Compensation failed for {step.name}: {e}"
                    )
                    # Continue compensating other steps
                    
    async def _persist_state(self, context: SagaContext):
        """Persist saga state for recovery"""
        # In production, save to database
        # This enables saga recovery after crashes
        pass
```

#### Production-Ready Implementation

```python
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

# Saga Persistence for Recovery
class SagaRepository:
    """Persist saga state for crash recovery"""
    
    def __init__(self, db_pool):
        self.db_pool = db_pool
        
    async def save_saga(self, saga_id: str, state: Dict[str, Any]):
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO sagas (id, state, updated_at)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE
                SET state = $2, updated_at = $3
            """, saga_id, json.dumps(state), datetime.utcnow())
            
    async def load_saga(self, saga_id: str) -> Optional[Dict[str, Any]]:
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchone(
                "SELECT state FROM sagas WHERE id = $1",
                saga_id
            )
            return json.loads(row['state']) if row else None
            
    async def delete_saga(self, saga_id: str):
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM sagas WHERE id = $1",
                saga_id
            )

# Event-Driven Choreography
@dataclass
class SagaEvent:
    saga_id: str
    step_name: str
    status: str
    payload: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class ChoreographedSaga:
    """Event-driven saga implementation"""
    
    def __init__(self, event_bus, saga_repository):
        self.event_bus = event_bus
        self.saga_repository = saga_repository
        self.active_sagas: Dict[str, Dict] = {}
        
        # Subscribe to events
        self._subscribe_to_events()
        
    def _subscribe_to_events(self):
        """Subscribe to all saga-related events"""
        self.event_bus.subscribe('OrderCreated', self.handle_order_created)
        self.event_bus.subscribe('PaymentProcessed', self.handle_payment_processed)
        self.event_bus.subscribe('InventoryReserved', self.handle_inventory_reserved)
        self.event_bus.subscribe('ShipmentCreated', self.handle_shipment_created)
        
        # Failure events
        self.event_bus.subscribe('PaymentFailed', self.handle_payment_failed)
        self.event_bus.subscribe('InventoryFailed', self.handle_inventory_failed)
        self.event_bus.subscribe('ShipmentFailed', self.handle_shipment_failed)
        
    async def handle_order_created(self, event: SagaEvent):
        """Start saga when order is created"""
        saga_id = event.saga_id
        
        # Initialize saga state
        self.active_sagas[saga_id] = {
            'status': 'processing_payment',
            'order': event.payload,
            'completed_steps': ['order_created']
        }
        
        await self.saga_repository.save_saga(saga_id, self.active_sagas[saga_id])
        
        # Trigger next step
        await self.event_bus.publish(SagaEvent(
            saga_id=saga_id,
            step_name='process_payment',
            status='started',
            payload={
                'amount': event.payload['total_amount'],
                'payment_method': event.payload['payment_method']
            }
        ))
        
    async def handle_payment_processed(self, event: SagaEvent):
        """Handle successful payment"""
        saga_id = event.saga_id
        saga = self.active_sagas.get(saga_id)
        
        if not saga:
            saga = await self.saga_repository.load_saga(saga_id)
            if not saga:
                return
                
        saga['payment'] = event.payload
        saga['completed_steps'].append('payment_processed')
        saga['status'] = 'reserving_inventory'
        
        await self.saga_repository.save_saga(saga_id, saga)
        
        # Next step
        await self.event_bus.publish(SagaEvent(
            saga_id=saga_id,
            step_name='reserve_inventory',
            status='started',
            payload={
                'items': saga['order']['items']
            }
        ))
        
    async def handle_inventory_failed(self, event: SagaEvent):
        """Handle inventory reservation failure - start compensation"""
        saga_id = event.saga_id
        saga = self.active_sagas.get(saga_id)
        
        if not saga:
            saga = await self.saga_repository.load_saga(saga_id)
            if not saga:
                return
                
        saga['status'] = 'compensating'
        saga['failure_reason'] = event.payload.get('reason')
        
        # Start compensation based on completed steps
        if 'payment_processed' in saga['completed_steps']:
            await self.event_bus.publish(SagaEvent(
                saga_id=saga_id,
                step_name='refund_payment',
                status='started',
                payload={
                    'payment_id': saga['payment']['payment_id']
                }
            ))
            
        if 'order_created' in saga['completed_steps']:
            await self.event_bus.publish(SagaEvent(
                saga_id=saga_id,
                step_name='cancel_order',
                status='started',
                payload={
                    'order_id': saga['order']['order_id']
                }
            ))

# Saga Monitoring and Timeouts
class SagaMonitor:
    """Monitor saga execution and handle timeouts"""
    
    def __init__(self, saga_repository, event_bus, timeout_minutes=30):
        self.saga_repository = saga_repository
        self.event_bus = event_bus
        self.timeout_minutes = timeout_minutes
        
    async def check_stuck_sagas(self):
        """Periodically check for stuck sagas"""
        while True:
            try:
                stuck_sagas = await self._find_stuck_sagas()
                
                for saga_id, saga_state in stuck_sagas:
                    await self._handle_stuck_saga(saga_id, saga_state)
                    
            except Exception as e:
                logging.error(f"Error checking stuck sagas: {e}")
                
            await asyncio.sleep(60)  # Check every minute
            
    async def _find_stuck_sagas(self) -> List[tuple]:
        """Find sagas that haven't progressed"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.timeout_minutes)
        
        async with self.saga_repository.db_pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, state 
                FROM sagas 
                WHERE updated_at < $1 
                AND state->>'status' NOT IN ('completed', 'failed')
            """, cutoff_time)
            
            return [(row['id'], json.loads(row['state'])) for row in rows]
            
    async def _handle_stuck_saga(self, saga_id: str, saga_state: Dict):
        """Handle a saga that's stuck"""
        logging.warning(f"Saga {saga_id} is stuck in state: {saga_state['status']}")
        
        # Trigger timeout compensation
        await self.event_bus.publish(SagaEvent(
            saga_id=saga_id,
            step_name='saga_timeout',
            status='failed',
            payload={
                'reason': 'Saga execution timeout',
                'last_status': saga_state['status']
            }
        ))

# Saga with Distributed Locking
class DistributedSagaLock:
    """Ensure only one instance processes a saga"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.lock_timeout = 300  # 5 minutes
        
    async def acquire_lock(self, saga_id: str) -> bool:
        """Try to acquire exclusive lock for saga"""
        lock_key = f"saga_lock:{saga_id}"
        lock_value = str(uuid.uuid4())
        
        acquired = await self.redis.set(
            lock_key, 
            lock_value,
            nx=True,  # Only set if not exists
            ex=self.lock_timeout
        )
        
        if acquired:
            # Store lock value for safe release
            return lock_value
        return None
        
    async def release_lock(self, saga_id: str, lock_value: str):
        """Safely release lock if we own it"""
        lock_key = f"saga_lock:{saga_id}"
        
        # Lua script for atomic check and delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        await self.redis.eval(lua_script, 1, lock_key, lock_value)
```

### State Management

Sagas manage state through explicit state machines:

```mermaid
stateDiagram-v2
    [*] --> Started: Begin Saga
    
    Started --> Step1_Executing: Execute Step 1
    Step1_Executing --> Step1_Completed: Success
    Step1_Executing --> Compensating: Failure
    
    Step1_Completed --> Step2_Executing: Execute Step 2
    Step2_Executing --> Step2_Completed: Success
    Step2_Executing --> Step1_Compensating: Failure
    
    Step2_Completed --> Step3_Executing: Execute Step 3
    Step3_Executing --> Completed: Success
    Step3_Executing --> Step2_Compensating: Failure
    
    Step2_Compensating --> Step1_Compensating: Compensate Step 2
    Step1_Compensating --> Failed: Compensate Step 1
    
    Completed --> [*]: Success
    Failed --> [*]: Compensated
    Compensating --> Failed: All Compensated
```

### Common Variations

1. **Orchestrated**: Complex workflows → Central failure point, easier debug
2. **Choreographed**: Loose coupling → No central point, harder monitoring
3. **Hybrid**: Mixed approach → Flexible but complex

### Integration Points

- **Event Sourcing**: Saga events in stream
- **CQRS**: Commands via saga, queries from read side
- **Outbox**: Reliable event publishing
- **Circuit Breaker**: Protect saga steps

---

## Level 4: Expert Practitioner (30 minutes)

### Advanced Techniques

#### Saga Composition

```python
class CompositeSaga:
    """Compose sagas from smaller sagas"""
    
    def __init__(self):
        self.sub_sagas: List[SagaOrchestrator] = []
        
    def add_sub_saga(self, saga: SagaOrchestrator):
        self.sub_sagas.append(saga)
        return self
        
    async def execute(self, context: Dict[str, Any]):
        """Execute sub-sagas with proper isolation"""
        completed_sagas = []
        
        try:
            for sub_saga in self.sub_sagas:
                # Each sub-saga gets its own context
                sub_context = self._create_sub_context(context, sub_saga)
                
                result = await sub_saga.execute(sub_context)
                completed_sagas.append((sub_saga, result))
                
                # Update parent context
                self._merge_results(context, result)
                
        except Exception as e:
            # Compensate completed sub-sagas
            for saga, result in reversed(completed_sagas):
                await saga._run_compensations(result)
            raise

# Parallel Saga Execution
class ParallelSagaOrchestrator(SagaOrchestrator):
    """Execute independent saga steps in parallel"""
    
    def __init__(self, saga_id: Optional[str] = None):
        super().__init__(saga_id)
        self.parallel_groups: List[List[SagaStep]] = []
        
    def add_parallel_group(self, steps: List[SagaStep]):
        """Add steps that can execute in parallel"""
        self.parallel_groups.append(steps)
        return self
        
    async def execute(self, initial_request: Dict[str, Any]) -> SagaContext:
        """Execute with parallel step groups"""
        context = SagaContext(
            saga_id=self.saga_id,
            initial_request=initial_request
        )
        
        try:
            for group in self.parallel_groups:
                # Execute steps in parallel
                tasks = [
                    self._execute_step(step, context) 
                    for step in group
                ]
                
                results = await asyncio.gather(*tasks)
                
                # All succeeded, mark as completed
                self.completed_steps.extend(group)
                
        except Exception as e:
            # Compensate in parallel too
            await self._run_parallel_compensations(context)
            raise
```

#### Saga Testing Framework

```python
class SagaTestFramework:
    """Comprehensive testing for sagas"""
    
    def __init__(self):
        self.mocked_services = {}
        self.execution_log = []
        
    async def test_happy_path(self, saga: SagaOrchestrator):
        """Test successful execution"""
        # Mock all services to succeed
        self._setup_success_mocks()
        
        context = await saga.execute(self._get_test_request())
        
        # Verify all steps executed
        assert all(
            step.status == StepStatus.COMPLETED 
            for step in saga.steps
        )
        
        return context
        
    async def test_compensation_at_step(self, 
                                       saga: SagaOrchestrator,
                                       failing_step: int):
        """Test compensation when specific step fails"""
        # Setup mocks
        for i, step in enumerate(saga.steps):
            if i < failing_step:
                self._mock_step_success(step)
            elif i == failing_step:
                self._mock_step_failure(step)
                
        # Execute and expect failure
        with pytest.raises(SagaFailedException):
            await saga.execute(self._get_test_request())
            
        # Verify compensations
        for i in range(failing_step):
            step = saga.steps[i]
            assert step.status == StepStatus.COMPENSATED
            
    async def test_idempotency(self, saga: SagaOrchestrator):
        """Test saga can be safely retried"""
        request = self._get_test_request()
        
        # First execution
        context1 = await saga.execute(request)
        
        # Retry with same request
        saga2 = self._rebuild_saga()
        context2 = await saga2.execute(request)
        
        # Results should be identical
        assert context1.step_results == context2.step_results
```

### Performance Optimization

<div class="decision-box">
<h4>🎯 Performance Tuning Checklist</h4>

- [ ] **Parallel Execution**: Run independent steps concurrently
- [ ] **Async I/O**: Use async/await throughout
- [ ] **Connection Pooling**: Reuse database connections
- [ ] **Batch Operations**: Group related operations
- [ ] **Caching**: Cache read-only data during saga
- [ ] **Timeout Tuning**: Set appropriate step timeouts
- [ ] **Circuit Breakers**: Fail fast on unavailable services
- [ ] **Monitoring**: Track saga execution times
</div>

### Monitoring & Observability

Key metrics to track:

```yaml
metrics:
  # Saga Execution Metrics
  - name: saga_duration
    description: Total saga execution time
    alert_threshold: p99 > 30s
    
  - name: saga_success_rate
    description: Percentage of successful sagas
    alert_threshold: < 95%
    
  - name: compensation_rate
    description: Percentage of sagas requiring compensation
    alert_threshold: > 10%
    
  # Step Metrics
  - name: step_duration
    description: Individual step execution time
    alert_threshold: p99 > 5s
    
  - name: step_failure_rate
    description: Step failure rate by type
    alert_threshold: > 5%
    
  # Compensation Metrics
  - name: compensation_success_rate
    description: Successful compensation percentage
    alert_threshold: < 99%
    
  - name: stuck_sagas
    description: Sagas not progressing
    alert_threshold: > 10
    
  # Resource Metrics
  - name: concurrent_sagas
    description: Number of active sagas
    alert_threshold: > 1000
```

### Common Pitfalls

<div class="failure-vignette">
<h4>⚠️ Pitfall: Non-Idempotent Steps</h4>
Network retries → Multiple charges, double inventory decrements.

**Solution**: Idempotent steps with keys and duplicate checks.
</div>

<div class="failure-vignette">
<h4>⚠️ Pitfall: Missing Compensation Logic</h4>
No compensation → Inconsistent state → Manual fixes.

**Solution**: Every forward transaction needs compensation. Test all paths.
</div>

### Production Checklist

- [ ] **Idempotency** implemented for all steps
- [ ] **Compensation logic** for every forward transaction
- [ ] **Timeout handling** for long-running steps
- [ ] **State persistence** for crash recovery
- [ ] **Monitoring** for saga execution and compensation
- [ ] **Testing** of all failure scenarios
- [ ] **Documentation** of saga flows and compensations
- [ ] **Alerting** for stuck or failed sagas

---

## Level 5: Mastery (45 minutes)

### Case Study: Uber's Trip Booking Saga

<div class="truth-box">
<h4>🏢 Real-World Implementation</h4>

**Company**: Uber  
**Scale**: 25M+ trips/day, 100+ services, sub-second response, 99.99% consistency

**Challenge**: Coordinate driver matching, fare, payment, tracking with graceful failures.

**Steps**: Driver reservation → Fare calculation → Payment auth → Trip creation → Notifications → Tracking

**Architecture**:

```mermaid
graph TB
    RA[Rider App] --> AG[API Gateway]
    AG --> TSO[Trip Saga Orchestrator]
    
    TSO --> DS[Driver Service]
    TSO --> PS[Payment Service]
    TSO --> FS[Fare Service]
    TSO --> NS[Notification Service]
    TSO --> TS[Trip Service]
    TSO --> TRS[Tracking Service]
    
    subgraph "Saga Services"
        DS
        PS
        FS
        NS
        TS
        TRS
    end
    
    style TSO fill:#9c27b0,stroke:#6a1b9a,stroke-width:3px,color:#fff
    style DS fill:#4caf50
    style PS fill:#2196f3
    style FS fill:#ff9800
    style NS fill:#9c27b0
    style TS fill:#00bcd4
    style TRS fill:#795548
```

**Decisions**:
1. Hybrid: Orchestration for creation, choreography for updates
2. Optimistic driver locking with compensation
3. Allow partial completion for non-critical steps
4. Geographic saga sharding

**Results**: <500ms latency, 99.7% success, 2.3% compensations, zero inconsistencies

**Lessons**:
1. Design for partial failure
2. Compensation isn't always reverse
3. Monitor compensation paths
4. Saga observability crucial
</div>

### Economic Analysis

#### Cost Model

```python
def calculate_saga_roi(
    transactions_per_day: int,
    services_involved: int,
    failure_rate: float,
    manual_resolution_cost: float
) -> dict:
    """Calculate ROI for implementing Saga pattern"""
    
    # Cost without saga (distributed transactions or manual)
    distributed_tx_overhead = 0.5  # 50% performance overhead
    manual_resolutions = transactions_per_day * failure_rate
    
    without_saga_costs = {
        'performance_cost': transactions_per_day * 0.001 * distributed_tx_overhead,
        'manual_resolution': manual_resolutions * manual_resolution_cost,
        'downtime_cost': failure_rate * 10000,  # Downtime impact
        'development_complexity': services_involved * 5000
    }
    
    # Cost with saga
    saga_compensation_rate = failure_rate * 0.1  # 90% auto-recovery
    
    with_saga_costs = {
        'implementation': services_involved * 8000,
        'saga_overhead': transactions_per_day * 0.0001,
        'compensation_cost': transactions_per_day * saga_compensation_rate * 0.1,
        'monitoring': 2000  # Monthly monitoring cost
    }
    
    # Benefits
    monthly_savings = (
        sum(without_saga_costs.values()) - 
        sum(with_saga_costs.values())
    )
    
    return {
        'monthly_savings': monthly_savings,
        'payback_months': with_saga_costs['implementation'] / monthly_savings,
        'reliability_improvement': (1 - saga_compensation_rate) * 100,
        'recommended': services_involved >= 3 and failure_rate > 0.01
    }

# Example calculation
roi = calculate_saga_roi(
    transactions_per_day=100_000,
    services_involved=5,
    failure_rate=0.05,  # 5% failure rate
    manual_resolution_cost=10  # $10 per manual fix
)
print(f"ROI: ${roi['monthly_savings']:,.0f}/month, "
      f"Payback: {roi['payback_months']:.1f} months")
```

#### When It Pays Off

- **Break-even**: 3+ services, 1%+ failure rate
- **High ROI**: E-commerce checkout, financial transactions, bookings, fulfillment
- **Low ROI**: Simple CRUD, read-only, single service

### Pattern Evolution

```mermaid
timeline
    title Evolution of Saga Pattern
    
    1987 : Original paper by Garcia-Molina
         : Database-focused solution
    
    1990s : Workflow engines adopt sagas
          : Long-running business processes
    
    2000s : SOA brings distributed sagas
          : Web services coordination
    
    2010 : Microservices popularize pattern
         : Service autonomy focus
    
    2015 : Event-driven sagas emerge
         : Choreography over orchestration
    
    2020 : Serverless sagas
         : Function-based coordination
    
    2025 : Current State
         : AI-assisted compensation
         : Automatic saga generation
```

### Axiom Connections

<div class="axiom-box">
<h4>🔗 Fundamental Laws</h4>

This pattern directly addresses:

1. **[Law 4 (Multidimensional Optimization ⚖️)](../part1-axioms/axiom4-optimization/index.md)**: Manages distributed consensus without locks
2. **[Law 1 (Correlated Failure ⛓️)](../part1-axioms/axiom1-failure/index.md)**: Explicit handling of partial failures
3. **[Law 3 (Emergent Chaos 🌪️)](../part1-axioms/axiom3-chaos/index.md)**: Handles concurrent saga executions
4. **[Law 5 (Distributed Knowledge 🧠)](../part1-axioms/axiom5-knowledge/index.md)**: Full audit trail of all steps
5. **[Law 7 (Economic Reality 💰)](../part1-axioms/axiom7-economics/index.md)**: Balances consistency costs with business needs
</div>

### Future Directions

**Emerging Trends**:

1. **ML-Driven Compensation**: AI determines optimal compensation strategy
2. **Predictive Saga Routing**: ML predicts likely failures and adjusts flow
3. **Blockchain Sagas**: Immutable saga execution logs
4. **Edge Sagas**: Distributed saga execution at edge locations

**What's Next**:
- Automatic saga generation from business requirements
- Self-healing sagas that adapt to failures
- Cross-cloud saga orchestration
- Real-time saga optimization based on conditions

---

## Quick Reference

### Decision Matrix

```mermaid
graph TD
    Start[Need distributed transaction?] --> Q1{Multiple<br/>services?}
    Q1 -->|No| Local[Use local<br/>transaction]
    Q1 -->|Yes| Q2{Can tolerate<br/>eventual consistency?}
    
    Q2 -->|No| Q3{Can use<br/>2PC?}
    Q2 -->|Yes| Q4{Complex<br/>workflow?}
    
    Q3 -->|No| Redesign[Redesign to<br/>avoid distribution]
    Q3 -->|Yes| TwoPC[Use 2PC<br/>if possible]
    
    Q4 -->|No| Q5{Events<br/>sufficient?}
    Q4 -->|Yes| Saga[Use Saga<br/>Pattern]
    
    Q5 -->|Yes| Events[Use simple<br/>events]
    Q5 -->|No| Saga
    
    Saga --> Q6{Service<br/>coupling OK?}
    Q6 -->|Yes| Orchestration[Orchestrated<br/>Saga]
    Q6 -->|No| Choreography[Choreographed<br/>Saga]
```

### Command Cheat Sheet

```bash
# Saga Management
saga start <type> <request>          # Start new saga
saga status <saga-id>                # Check saga status
saga retry <saga-id>                 # Retry failed saga
saga compensate <saga-id>            # Force compensation

# Monitoring
saga list --status=running           # List active sagas
saga list --stuck --timeout=30m      # Find stuck sagas
saga metrics --period=1h             # Saga metrics

# Testing
saga test <definition> --happy-path  # Test success path
saga test <definition> --fail-at=3   # Test failure at step 3
saga test <definition> --chaos       # Random failure testing

# Debugging
saga trace <saga-id>                 # Show execution trace
saga events <saga-id>                # List all events
saga replay <saga-id>                # Replay saga execution
```

### Configuration Template

```yaml
# Production Saga configuration
saga:
  orchestrator:
    type: "centralized"  # or distributed
    persistence: "postgresql"
    state_timeout: 30m
    
  execution:
    max_retries: 3
    retry_delay: "exponential"
    parallel_steps: true
    max_concurrent: 100
    
  compensation:
    strategy: "immediate"  # or batched
    timeout: 5m
    max_attempts: 3
    
  monitoring:
    trace_sampling: 0.1
    metrics_interval: 10s
    stuck_check_interval: 1m
    
  steps:
    default_timeout: 30s
    circuit_breaker:
      enabled: true
      failure_threshold: 5
      timeout: 30s
      
  events:
    bus: "kafka"  # or rabbitmq, redis
    retention: 7d
    compression: true
    
  recovery:
    enabled: true
    checkpoint_interval: "after_each_step"
    recovery_workers: 5
```

---

## Related Resources

### Patterns
- [Event Sourcing](../patterns/event-sourcing.md) - Natural event log for sagas
- [CQRS](../patterns/cqrs.md) - Separate saga execution from queries
- [Outbox Pattern](../patterns/outbox.md) - Reliable event publishing
- [Circuit Breaker](../patterns/circuit-breaker.md) - Protect saga steps

### Laws
- [Law 4 (Multidimensional Optimization ⚖️)](../part1-axioms/axiom4-optimization/index.md) - Why distributed consensus is hard
- [Law 1 (Correlated Failure ⛓️)](../part1-axioms/axiom1-failure/index.md) - Handling partial failures
- [Law 3 (Emergent Chaos 🌪️)](../part1-axioms/axiom3-chaos/index.md) - Managing parallel execution

### Further Reading
- [Original Sagas Paper (1987)](https://www.cs.cornell.edu/andru/cs711/2002fa/reading/sagas.pdf) - Garcia-Molina & Salem
- [Microservices.io Saga Pattern](https://microservices.io/patterns/data/saga.html) - Chris Richardson
- [Saga Orchestration vs Choreography](https://blog.couchbase.com/saga-pattern-implement-business-transactions-using-microservices/) - Comparison
- [Building Sagas with AWS Step Functions](https://aws.amazon.com/step-functions/use-cases/#saga) - Serverless sagas

### Tools & Libraries
- **Java**: Axon Framework, Eventuate Tram
- **C#/.NET**: MassTransit, NServiceBus
- **Python**: Faust, Celery with Saga support
- **Node.js**: Moleculer, Node-Saga
- **Go**: Temporal, Cadence
- **Orchestrators**: AWS Step Functions, Azure Durable Functions, Camunda

---

<div class="navigation-links">
<div class="prev-link">
<a href="/patterns/event-sourcing">← Previous: Event Sourcing</a>
</div>
<div class="next-link">
<a href="/patterns/service-mesh">Next: Service Mesh →</a>
</div>
</div>