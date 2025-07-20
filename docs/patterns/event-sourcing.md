---
title: Event Sourcing Pattern
description: Store all changes as events rather than current state - the log is the truth
type: pattern
difficulty: advanced
reading_time: 10 min
prerequisites: []
pattern_type: "data"
when_to_use: "Audit trails, complex domains, time-travel debugging, event-driven systems"
when_not_to_use: "Simple CRUD, storage constraints, real-time queries"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Event Sourcing Pattern**


# Event Sourcing

**The database is a cache; the log is the truth**

## THE PROBLEM

```redis
Current state loses history:
UPDATE account SET balance = 150

What happened?
- Previous balance?
- Who changed it?
- When?
- Why?
```

## THE SOLUTION

```bash
Events tell the whole story:
[AccountOpened, $0] → [Deposited, $100] → [Withdrew, $50] → [Deposited, $100]
                                                                      ↓
                                                              Balance: $150
                                                              
Replay events = Current state
Time travel = Replay to point
```

## IMPLEMENTATION

```python
class EventSourcedAggregate:
    def __init__(self, aggregate_id):
        self.id = aggregate_id
        self.version = 0
        self.uncommitted_events = []
        
    def apply_event(self, event):
        """Apply event to update state"""
        handler = getattr(self, f'_handle_{event.type}', None)
        if handler:
            handler(event)
        self.version += 1
        
    def raise_event(self, event):
        """Raise new event"""
        event.aggregate_id = self.id
        event.version = self.version + 1
        self.apply_event(event)
        self.uncommitted_events.append(event)
        
    def mark_committed(self):
        """Clear uncommitted events after save"""
        self.uncommitted_events = []

# Example: Shopping Cart
class ShoppingCart(EventSourcedAggregate):
    def __init__(self, cart_id):
        super().__init__(cart_id)
        self.items = {}
        self.customer_id = None
        
    def create(self, customer_id):
        self.raise_event(Event(
            type='cart_created',
            payload={'customer_id': customer_id}
        ))
        
    def add_item(self, product_id, quantity, price):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        self.raise_event(Event(
            type='item_added',
            payload={
                'product_id': product_id,
                'quantity': quantity,
                'price': price
            }
        ))
        
    def remove_item(self, product_id):
        if product_id not in self.items:
            raise ValueError("Item not in cart")
            
        self.raise_event(Event(
            type='item_removed',
            payload={'product_id': product_id}
        ))
        
    def checkout(self):
        if not self.items:
            raise ValueError("Cart is empty")
            
        self.raise_event(Event(
            type='cart_checked_out',
            payload={
                'total': sum(i['quantity'] * i['price'] 
                           for i in self.items.values())
            }
        ))
    
    # Event handlers
    def _handle_cart_created(self, event):
        self.customer_id = event.payload['customer_id']
        
    def _handle_item_added(self, event):
        product_id = event.payload['product_id']
        if product_id in self.items:
            self.items[product_id]['quantity'] += event.payload['quantity']
        else:
            self.items[product_id] = {
                'quantity': event.payload['quantity'],
                'price': event.payload['price']
            }
            
    def _handle_item_removed(self, event):
        del self.items[event.payload['product_id']]
        
    def _handle_cart_checked_out(self, event):
        self.checked_out = True

# Event Store with snapshots
class EventStore:
    def __init__(self, snapshot_frequency=100):
        self.events = {}  # aggregate_id -> list of events
        self.snapshots = {}  # aggregate_id -> (version, state)
        self.snapshot_frequency = snapshot_frequency
        
    def save(self, aggregate):
        """Save uncommitted events"""
        agg_id = aggregate.id
        
        if agg_id not in self.events:
            self.events[agg_id] = []
            
        # Append new events
        for event in aggregate.uncommitted_events:
            self.events[agg_id].append(event)
            
        # Create snapshot if needed
        if len(self.events[agg_id]) % self.snapshot_frequency == 0:
            self.snapshots[agg_id] = (
                aggregate.version,
                pickle.dumps(aggregate)  # In practice, use proper serialization
            )
            
        aggregate.mark_committed()
        
    def load(self, aggregate_class, aggregate_id):
        """Load aggregate from events"""
        if aggregate_id not in self.events:
            return None
            
        # Start from snapshot if available
        if aggregate_id in self.snapshots:
            version, state = self.snapshots[aggregate_id]
            aggregate = pickle.loads(state)
            events_to_replay = self.events[aggregate_id][version:]
        else:
            aggregate = aggregate_class(aggregate_id)
            events_to_replay = self.events[aggregate_id]
            
        # Replay events
        for event in events_to_replay:
            aggregate.apply_event(event)
            
        return aggregate
    
    def get_events_since(self, aggregate_id, version):
        """Get events after a specific version"""
        if aggregate_id not in self.events:
            return []
        return self.events[aggregate_id][version:]

# Temporal queries
class TemporalQuery:
    def __init__(self, event_store):
        self.event_store = event_store
        
    def state_at(self, aggregate_class, aggregate_id, timestamp):
        """Get state at specific time"""
        aggregate = aggregate_class(aggregate_id)
        
        events = self.event_store.events.get(aggregate_id, [])
        for event in events:
            if event.metadata['timestamp'] <= timestamp:
                aggregate.apply_event(event)
            else:
                break
                
        return aggregate
    
    def audit_trail(self, aggregate_id, start_time, end_time):
        """Get all changes in time range"""
        events = self.event_store.events.get(aggregate_id, [])
        
        return [
            {
                'version': e.version,
                'type': e.type,
                'timestamp': e.metadata['timestamp'],
                'payload': e.payload,
                'user': e.metadata.get('user_id')
            }
            for e in events
            if start_time <= e.metadata['timestamp'] <= end_time
        ]
```

## Advanced: Event Upcasting

```python
class EventUpgrader:
    """Handle event schema evolution"""
    
    def __init__(self):
        self.upgraders = {}
        
    def register(self, event_type, from_version, to_version, upgrader):
        key = (event_type, from_version, to_version)
        self.upgraders[key] = upgrader
        
    def upgrade(self, event):
        current_version = event.metadata.get('version', '1.0')
        target_version = '2.0'  # Current version
        
        while current_version < target_version:
            key = (event.type, current_version, target_version)
            if key in self.upgraders:
                event = self.upgraders[key](event)
                current_version = event.metadata['version']
            else:
                break
                
        return event

# Example upgrader
def upgrade_item_added_v1_to_v2(event):
    """Add currency field to old events"""
    event.payload['currency'] = 'USD'  # Default
    event.metadata['version'] = '2.0'
    return event
```

## ✓ CHOOSE THIS WHEN:
• Complete audit trail required
• Time travel queries needed
• Complex state transitions
• Debugging production issues
• Compliance/regulatory needs

## ⚠️ BEWARE OF:
• Storage growth (events forever)
• Query complexity (no simple SELECT)
• Schema evolution complexity
• Replay performance
• Eventually consistent reads

## REAL EXAMPLES
• **Banking**: Every transaction stored
• **Healthcare**: Patient history immutable
• **Git**: Commits are event sourcing!

---

**Previous**: [← Event-Driven Architecture](event-driven.md) | **Next**: [FinOps Patterns →](finops.md)

**Related**: [Cqrs](/patterns/cqrs/) • [Saga](/patterns/saga/) • [Event Driven](/patterns/event-driven/)
