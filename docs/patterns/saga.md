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
```

## THE SOLUTION

```
Saga: A sequence of local transactions with compensations

Happy Path:          Failure Path:
T1 ✓                T1 ✓
T2 ✓                T2 ✓  
T3 ✓                T3 ✗
T4 ✓                C2 ← Compensate
                    C1 ← Compensate
```

## Saga Patterns

```
1. ORCHESTRATION (Central Coordinator)
        Saga Orchestrator
       /      |      \
     T1      T2      T3
      
2. CHOREOGRAPHY (Event Chain)
   T1 → [Event] → T2 → [Event] → T3
```

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
```

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