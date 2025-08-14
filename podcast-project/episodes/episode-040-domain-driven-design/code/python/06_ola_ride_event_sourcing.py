#!/usr/bin/env python3
"""
Domain-Driven Design: Event Sourcing Pattern - Ola Ride Example
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में Event Sourcing pattern का इस्तेमाल करके
Ola ride booking की complete history maintain करते हैं। सारा state events से derive होता है।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass, asdict
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import json
import copy

# Event Store - Events को store करने के लिए
class EventStore:
    """
    Simple in-memory event store
    Production में यह database में होगा
    """
    
    def __init__(self):
        self._events: Dict[str, List[dict]] = {}
        self._snapshots: Dict[str, dict] = {}
    
    def append_events(self, stream_id: str, events: List[dict], expected_version: int) -> None:
        """Append events to stream with optimistic concurrency"""
        if stream_id not in self._events:
            self._events[stream_id] = []
        
        current_version = len(self._events[stream_id])
        if current_version != expected_version:
            raise Exception(f"Concurrency conflict. Expected {expected_version}, got {current_version}")
        
        self._events[stream_id].extend(events)
        print(f"📝 Stored {len(events)} events for stream: {stream_id}")
    
    def get_events(self, stream_id: str, from_version: int = 0) -> List[dict]:
        """Get events from stream starting from version"""
        if stream_id not in self._events:
            return []
        
        return self._events[stream_id][from_version:]
    
    def save_snapshot(self, stream_id: str, snapshot: dict, version: int) -> None:
        """Save aggregate snapshot for performance"""
        self._snapshots[stream_id] = {
            "data": snapshot,
            "version": version,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_snapshot(self, stream_id: str) -> Optional[dict]:
        """Get latest snapshot"""
        return self._snapshots.get(stream_id)

# Base Domain Event
@dataclass
class DomainEvent:
    """Base class for all domain events"""
    event_id: str
    aggregate_id: str
    event_type: str
    version: int
    timestamp: datetime
    
    def to_dict(self) -> dict:
        """Convert event to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DomainEvent':
        """Create event from dictionary"""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

# Ride Domain Events
@dataclass
class RideBookedEvent(DomainEvent):
    customer_id: str
    pickup_location: str
    drop_location: str
    ride_type: str
    estimated_fare: float

@dataclass
class DriverAssignedEvent(DomainEvent):
    driver_id: str
    driver_name: str
    driver_rating: float
    vehicle_number: str
    estimated_arrival_time: int  # minutes

@dataclass
class DriverArrivedEvent(DomainEvent):
    actual_arrival_time: datetime

@dataclass
class RideStartedEvent(DomainEvent):
    start_time: datetime
    start_odometer_reading: float

@dataclass
class RideCompletedEvent(DomainEvent):
    end_time: datetime
    end_odometer_reading: float
    actual_distance: float
    final_fare: float

@dataclass
class RideCancelledEvent(DomainEvent):
    cancelled_by: str  # customer, driver, system
    cancellation_reason: str
    cancellation_fee: float

@dataclass
class PaymentProcessedEvent(DomainEvent):
    payment_method: str
    amount: float
    payment_status: str
    transaction_id: str

@dataclass
class RatingGivenEvent(DomainEvent):
    rating: float
    feedback: str
    rated_by: str  # customer, driver

# Enums
class RideStatus(Enum):
    BOOKED = "booked"
    DRIVER_ASSIGNED = "driver_assigned"
    DRIVER_ARRIVED = "driver_arrived"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class RideType(Enum):
    MINI = "mini"
    PRIME = "prime"
    PRIME_SUV = "prime_suv"
    AUTO = "auto"
    BIKE = "bike"

# Value Objects
@dataclass(frozen=True)
class Location:
    """Location value object"""
    latitude: float
    longitude: float
    address: str
    landmark: Optional[str] = None
    
    def __post_init__(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("Invalid latitude")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("Invalid longitude")

@dataclass(frozen=True)
class Money:
    """Money value object"""
    amount: Decimal
    currency: str = "INR"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

@dataclass(frozen=True)
class RideId:
    """Ride identifier"""
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.startswith("OLA_"):
            raise ValueError("Ride ID must start with OLA_")

# Aggregate Root with Event Sourcing
class RideAggregate:
    """
    Ride Aggregate with Event Sourcing
    
    यह aggregate अपना state events से maintain करता है।
    कोई भी state change एक event generate करता है।
    """
    
    def __init__(self, ride_id: RideId):
        # Identity
        self._ride_id = ride_id
        
        # Current State (derived from events)
        self._status = None
        self._customer_id: Optional[str] = None
        self._pickup_location: Optional[Location] = None
        self._drop_location: Optional[Location] = None
        self._ride_type: Optional[RideType] = None
        
        # Driver information
        self._driver_id: Optional[str] = None
        self._driver_name: Optional[str] = None
        self._driver_rating: Optional[float] = None
        self._vehicle_number: Optional[str] = None
        
        # Ride progress
        self._booked_at: Optional[datetime] = None
        self._driver_assigned_at: Optional[datetime] = None
        self._driver_arrived_at: Optional[datetime] = None
        self._ride_started_at: Optional[datetime] = None
        self._ride_ended_at: Optional[datetime] = None
        
        # Financial
        self._estimated_fare: Optional[Decimal] = None
        self._final_fare: Optional[Decimal] = None
        self._cancellation_fee: Optional[Decimal] = None
        
        # Trip details
        self._estimated_distance: Optional[float] = None
        self._actual_distance: Optional[float] = None
        self._start_odometer: Optional[float] = None
        self._end_odometer: Optional[float] = None
        
        # Ratings and feedback
        self._customer_rating: Optional[float] = None
        self._driver_rating_for_customer: Optional[float] = None
        self._customer_feedback: Optional[str] = None
        
        # Payment
        self._payment_method: Optional[str] = None
        self._payment_status: Optional[str] = None
        self._transaction_id: Optional[str] = None
        
        # Event sourcing metadata
        self._version = 0
        self._uncommitted_events: List[DomainEvent] = []
        self._last_snapshot_version = 0
    
    @property
    def ride_id(self) -> RideId:
        return self._ride_id
    
    @property
    def status(self) -> Optional[RideStatus]:
        return self._status
    
    @property
    def version(self) -> int:
        return self._version
    
    @property
    def customer_id(self) -> Optional[str]:
        return self._customer_id
    
    @property
    def driver_id(self) -> Optional[str]:
        return self._driver_id
    
    @property
    def estimated_fare(self) -> Optional[Decimal]:
        return self._estimated_fare
    
    @property
    def final_fare(self) -> Optional[Decimal]:
        return self._final_fare
    
    # Command Methods - Public API
    
    def book_ride(
        self,
        customer_id: str,
        pickup_location: Location,
        drop_location: Location,
        ride_type: RideType,
        estimated_fare: Decimal
    ) -> None:
        """
        Book a new ride
        नयी ride book करना
        """
        if self._status is not None:
            raise ValueError("Ride already exists")
        
        if estimated_fare.amount <= 0:
            raise ValueError("Estimated fare must be positive")
        
        # Create and apply event
        event = RideBookedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="RideBooked",
            version=self._version + 1,
            timestamp=datetime.now(),
            customer_id=customer_id,
            pickup_location=f"{pickup_location.latitude},{pickup_location.longitude}",
            drop_location=f"{drop_location.latitude},{drop_location.longitude}",
            ride_type=ride_type.value,
            estimated_fare=float(estimated_fare.amount)
        )
        
        self._apply_event(event)
        print(f"📱 Ride booked: {self._ride_id.value}")
        print(f"   Customer: {customer_id}")
        print(f"   Type: {ride_type.value}")
        print(f"   Estimated fare: ₹{estimated_fare.amount}")
    
    def assign_driver(
        self,
        driver_id: str,
        driver_name: str,
        driver_rating: float,
        vehicle_number: str,
        estimated_arrival_minutes: int
    ) -> None:
        """
        Assign driver to ride
        Ride को driver assign करना
        """
        if self._status != RideStatus.BOOKED:
            raise ValueError("Can only assign driver to booked ride")
        
        if not (1.0 <= driver_rating <= 5.0):
            raise ValueError("Driver rating must be between 1.0 and 5.0")
        
        event = DriverAssignedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="DriverAssigned",
            version=self._version + 1,
            timestamp=datetime.now(),
            driver_id=driver_id,
            driver_name=driver_name,
            driver_rating=driver_rating,
            vehicle_number=vehicle_number,
            estimated_arrival_time=estimated_arrival_minutes
        )
        
        self._apply_event(event)
        print(f"🚗 Driver assigned: {driver_name}")
        print(f"   Rating: {driver_rating}⭐")
        print(f"   Vehicle: {vehicle_number}")
        print(f"   ETA: {estimated_arrival_minutes} minutes")
    
    def mark_driver_arrived(self) -> None:
        """
        Mark driver as arrived
        Driver पहुंच गया mark करना
        """
        if self._status != RideStatus.DRIVER_ASSIGNED:
            raise ValueError("Driver must be assigned first")
        
        event = DriverArrivedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="DriverArrived",
            version=self._version + 1,
            timestamp=datetime.now(),
            actual_arrival_time=datetime.now()
        )
        
        self._apply_event(event)
        print(f"📍 Driver arrived at pickup location")
    
    def start_ride(self, start_odometer_reading: float) -> None:
        """
        Start the ride
        Ride शुरू करना
        """
        if self._status != RideStatus.DRIVER_ARRIVED:
            raise ValueError("Driver must have arrived first")
        
        if start_odometer_reading < 0:
            raise ValueError("Odometer reading must be positive")
        
        event = RideStartedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="RideStarted",
            version=self._version + 1,
            timestamp=datetime.now(),
            start_time=datetime.now(),
            start_odometer_reading=start_odometer_reading
        )
        
        self._apply_event(event)
        print(f"🏁 Ride started")
        print(f"   Start time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   Odometer: {start_odometer_reading} km")
    
    def complete_ride(
        self,
        end_odometer_reading: float,
        final_fare: Decimal
    ) -> None:
        """
        Complete the ride
        Ride complete करना
        """
        if self._status != RideStatus.IN_PROGRESS:
            raise ValueError("Ride must be in progress")
        
        if end_odometer_reading <= self._start_odometer:
            raise ValueError("End odometer must be greater than start")
        
        if final_fare.amount <= 0:
            raise ValueError("Final fare must be positive")
        
        actual_distance = end_odometer_reading - self._start_odometer
        
        event = RideCompletedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="RideCompleted",
            version=self._version + 1,
            timestamp=datetime.now(),
            end_time=datetime.now(),
            end_odometer_reading=end_odometer_reading,
            actual_distance=actual_distance,
            final_fare=float(final_fare.amount)
        )
        
        self._apply_event(event)
        print(f"🏆 Ride completed")
        print(f"   Distance: {actual_distance:.2f} km")
        print(f"   Final fare: ₹{final_fare.amount}")
        
        # Calculate ride duration
        if self._ride_started_at:
            duration = datetime.now() - self._ride_started_at
            print(f"   Duration: {int(duration.total_seconds() / 60)} minutes")
    
    def cancel_ride(
        self,
        cancelled_by: str,
        reason: str,
        cancellation_fee: Decimal = Decimal('0')
    ) -> None:
        """
        Cancel the ride
        Ride cancel करना
        """
        if self._status in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
            raise ValueError("Cannot cancel completed or already cancelled ride")
        
        if cancelled_by not in ["customer", "driver", "system"]:
            raise ValueError("Invalid cancellation source")
        
        event = RideCancelledEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="RideCancelled",
            version=self._version + 1,
            timestamp=datetime.now(),
            cancelled_by=cancelled_by,
            cancellation_reason=reason,
            cancellation_fee=float(cancellation_fee.amount)
        )
        
        self._apply_event(event)
        print(f"❌ Ride cancelled by {cancelled_by}")
        print(f"   Reason: {reason}")
        if cancellation_fee.amount > 0:
            print(f"   Cancellation fee: ₹{cancellation_fee.amount}")
    
    def process_payment(
        self,
        payment_method: str,
        amount: Decimal,
        transaction_id: str
    ) -> None:
        """
        Process payment for ride
        Ride का payment process करना
        """
        if self._status not in [RideStatus.COMPLETED, RideStatus.CANCELLED]:
            raise ValueError("Can only process payment for completed or cancelled rides")
        
        event = PaymentProcessedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="PaymentProcessed",
            version=self._version + 1,
            timestamp=datetime.now(),
            payment_method=payment_method,
            amount=float(amount.amount),
            payment_status="success",
            transaction_id=transaction_id
        )
        
        self._apply_event(event)
        print(f"💳 Payment processed")
        print(f"   Method: {payment_method}")
        print(f"   Amount: ₹{amount.amount}")
        print(f"   Transaction ID: {transaction_id}")
    
    def give_rating(
        self,
        rating: float,
        feedback: str,
        rated_by: str
    ) -> None:
        """
        Give rating and feedback
        Rating और feedback देना
        """
        if self._status != RideStatus.COMPLETED:
            raise ValueError("Can only rate completed rides")
        
        if not (1.0 <= rating <= 5.0):
            raise ValueError("Rating must be between 1.0 and 5.0")
        
        if rated_by not in ["customer", "driver"]:
            raise ValueError("Rating can only be given by customer or driver")
        
        event = RatingGivenEvent(
            event_id=str(uuid4()),
            aggregate_id=self._ride_id.value,
            event_type="RatingGiven",
            version=self._version + 1,
            timestamp=datetime.now(),
            rating=rating,
            feedback=feedback,
            rated_by=rated_by
        )
        
        self._apply_event(event)
        print(f"⭐ Rating given by {rated_by}: {rating}/5")
        print(f"   Feedback: {feedback}")
    
    # Event Application - यहाँ state changes होते हैं
    
    def _apply_event(self, event: DomainEvent) -> None:
        """Apply event to aggregate state"""
        # Update version
        self._version = event.version
        
        # Apply event to state
        if isinstance(event, RideBookedEvent):
            self._status = RideStatus.BOOKED
            self._customer_id = event.customer_id
            self._ride_type = RideType(event.ride_type)
            self._estimated_fare = Decimal(str(event.estimated_fare))
            self._booked_at = event.timestamp
            
            # Parse locations (simplified)
            pickup_coords = event.pickup_location.split(',')
            drop_coords = event.drop_location.split(',')
            self._pickup_location = Location(
                float(pickup_coords[0]), float(pickup_coords[1]), "Pickup Address"
            )
            self._drop_location = Location(
                float(drop_coords[0]), float(drop_coords[1]), "Drop Address"
            )
        
        elif isinstance(event, DriverAssignedEvent):
            self._status = RideStatus.DRIVER_ASSIGNED
            self._driver_id = event.driver_id
            self._driver_name = event.driver_name
            self._driver_rating = event.driver_rating
            self._vehicle_number = event.vehicle_number
            self._driver_assigned_at = event.timestamp
        
        elif isinstance(event, DriverArrivedEvent):
            self._status = RideStatus.DRIVER_ARRIVED
            self._driver_arrived_at = event.timestamp
        
        elif isinstance(event, RideStartedEvent):
            self._status = RideStatus.IN_PROGRESS
            self._ride_started_at = event.timestamp
            self._start_odometer = event.start_odometer_reading
        
        elif isinstance(event, RideCompletedEvent):
            self._status = RideStatus.COMPLETED
            self._ride_ended_at = event.timestamp
            self._end_odometer = event.end_odometer_reading
            self._actual_distance = event.actual_distance
            self._final_fare = Decimal(str(event.final_fare))
        
        elif isinstance(event, RideCancelledEvent):
            self._status = RideStatus.CANCELLED
            self._cancellation_fee = Decimal(str(event.cancellation_fee))
        
        elif isinstance(event, PaymentProcessedEvent):
            self._payment_method = event.payment_method
            self._payment_status = event.payment_status
            self._transaction_id = event.transaction_id
        
        elif isinstance(event, RatingGivenEvent):
            if event.rated_by == "customer":
                self._driver_rating_for_customer = event.rating
            else:
                self._customer_rating = event.rating
            self._customer_feedback = event.feedback
        
        # Add to uncommitted events
        self._uncommitted_events.append(event)
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Get uncommitted events"""
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        """Mark events as committed to event store"""
        self._uncommitted_events.clear()
    
    def load_from_history(self, events: List[dict]) -> None:
        """
        Load aggregate state from event history
        Event history से state को recreate करना
        """
        # Clear current state
        self._version = 0
        self._uncommitted_events.clear()
        
        # Apply all events in order
        for event_data in events:
            event = self._deserialize_event(event_data)
            # Don't add to uncommitted events when loading history
            uncommitted_backup = self._uncommitted_events.copy()
            self._apply_event(event)
            self._uncommitted_events = uncommitted_backup
        
        print(f"📚 Loaded aggregate from {len(events)} events")
    
    def _deserialize_event(self, event_data: dict) -> DomainEvent:
        """Deserialize event from dictionary"""
        event_type = event_data['event_type']
        event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'])
        
        # Map event types to classes
        event_classes = {
            'RideBooked': RideBookedEvent,
            'DriverAssigned': DriverAssignedEvent,
            'DriverArrived': DriverArrivedEvent,
            'RideStarted': RideStartedEvent,
            'RideCompleted': RideCompletedEvent,
            'RideCancelled': RideCancelledEvent,
            'PaymentProcessed': PaymentProcessedEvent,
            'RatingGiven': RatingGivenEvent
        }
        
        event_class = event_classes.get(event_type)
        if not event_class:
            raise ValueError(f"Unknown event type: {event_type}")
        
        return event_class(**event_data)
    
    def create_snapshot(self) -> dict:
        """Create aggregate snapshot for performance"""
        return {
            "ride_id": self._ride_id.value,
            "status": self._status.value if self._status else None,
            "customer_id": self._customer_id,
            "driver_id": self._driver_id,
            "driver_name": self._driver_name,
            "vehicle_number": self._vehicle_number,
            "estimated_fare": float(self._estimated_fare.amount) if self._estimated_fare else None,
            "final_fare": float(self._final_fare.amount) if self._final_fare else None,
            "actual_distance": self._actual_distance,
            "payment_status": self._payment_status,
            "customer_rating": self._customer_rating,
            "version": self._version
        }
    
    def get_ride_timeline(self) -> List[Dict]:
        """Get complete ride timeline"""
        timeline = []
        
        if self._booked_at:
            timeline.append({
                "event": "Ride Booked",
                "timestamp": self._booked_at,
                "details": f"Customer: {self._customer_id}, Fare: ₹{self._estimated_fare}"
            })
        
        if self._driver_assigned_at:
            timeline.append({
                "event": "Driver Assigned",
                "timestamp": self._driver_assigned_at,
                "details": f"Driver: {self._driver_name}, Vehicle: {self._vehicle_number}"
            })
        
        if self._driver_arrived_at:
            timeline.append({
                "event": "Driver Arrived",
                "timestamp": self._driver_arrived_at,
                "details": "Driver reached pickup location"
            })
        
        if self._ride_started_at:
            timeline.append({
                "event": "Ride Started",
                "timestamp": self._ride_started_at,
                "details": f"Odometer: {self._start_odometer} km"
            })
        
        if self._ride_ended_at:
            timeline.append({
                "event": "Ride Completed",
                "timestamp": self._ride_ended_at,
                "details": f"Distance: {self._actual_distance:.2f} km, Fare: ₹{self._final_fare}"
            })
        
        return timeline
    
    def __str__(self) -> str:
        return f"Ride({self._ride_id.value}: {self._status.value if self._status else 'None'})"

# Repository with Event Store
class RideRepository:
    """
    Repository for Ride aggregates using Event Store
    Event Store के साथ Ride repository
    """
    
    def __init__(self, event_store: EventStore):
        self._event_store = event_store
    
    def save(self, ride: RideAggregate) -> None:
        """Save ride to event store"""
        uncommitted_events = ride.get_uncommitted_events()
        if not uncommitted_events:
            return
        
        # Convert events to dictionaries
        event_dicts = [event.to_dict() for event in uncommitted_events]
        
        # Save to event store
        expected_version = ride.version - len(uncommitted_events)
        self._event_store.append_events(
            ride.ride_id.value,
            event_dicts,
            expected_version
        )
        
        # Mark events as committed
        ride.mark_events_as_committed()
        
        print(f"💾 Saved {len(event_dicts)} events for ride: {ride.ride_id.value}")
    
    def get_by_id(self, ride_id: RideId) -> Optional[RideAggregate]:
        """Load ride from event store"""
        # Try to load from snapshot first
        snapshot = self._event_store.get_snapshot(ride_id.value)
        
        if snapshot:
            # Load from snapshot + events after snapshot
            ride = RideAggregate(ride_id)
            events = self._event_store.get_events(ride_id.value, snapshot['version'])
            ride.load_from_history(events)
            print(f"📸 Loaded ride from snapshot + {len(events)} events")
            return ride
        else:
            # Load from complete event history
            events = self._event_store.get_events(ride_id.value)
            if not events:
                return None
            
            ride = RideAggregate(ride_id)
            ride.load_from_history(events)
            return ride
    
    def create_snapshot(self, ride_id: RideId) -> None:
        """Create snapshot for performance"""
        ride = self.get_by_id(ride_id)
        if ride:
            snapshot = ride.create_snapshot()
            self._event_store.save_snapshot(ride_id.value, snapshot, ride.version)
            print(f"📸 Created snapshot for ride: {ride_id.value}")

def simulate_complete_ola_ride():
    """Simulate complete Ola ride with Event Sourcing"""
    
    print("🚗 Ola Ride Event Sourcing Simulation")
    print("=" * 40)
    
    # Create event store and repository
    event_store = EventStore()
    repository = RideRepository(event_store)
    
    # Create new ride
    ride_id = RideId("OLA_RIDE_001")
    ride = RideAggregate(ride_id)
    
    # Locations
    pickup = Location(19.0596, 72.8295, "Bandra West, Mumbai")
    drop = Location(19.1197, 72.8464, "Andheri West, Mumbai")
    
    print("\n🔄 Ride Lifecycle Simulation:")
    
    # 1. Book ride
    ride.book_ride(
        customer_id="CUST_12345",
        pickup_location=pickup,
        drop_location=drop,
        ride_type=RideType.PRIME,
        estimated_fare=Decimal("285.50")
    )
    repository.save(ride)
    
    # 2. Assign driver
    ride.assign_driver(
        driver_id="DRV_67890",
        driver_name="Rajesh Kumar",
        driver_rating=4.7,
        vehicle_number="MH 01 AB 1234",
        estimated_arrival_minutes=5
    )
    repository.save(ride)
    
    # 3. Driver arrives
    import time
    print("\n⏰ Simulating 5 minutes for driver arrival...")
    ride.mark_driver_arrived()
    repository.save(ride)
    
    # 4. Start ride
    ride.start_ride(start_odometer_reading=45678.5)
    repository.save(ride)
    
    # 5. Complete ride
    print("\n⏰ Simulating 25 minutes ride...")
    ride.complete_ride(
        end_odometer_reading=45693.2,
        final_fare=Decimal("298.75")
    )
    repository.save(ride)
    
    # 6. Process payment
    ride.process_payment(
        payment_method="Paytm Wallet",
        amount=Decimal("298.75"),
        transaction_id="TXN_98765"
    )
    repository.save(ride)
    
    # 7. Customer gives rating
    ride.give_rating(
        rating=4.5,
        feedback="Good ride, driver was polite",
        rated_by="customer"
    )
    repository.save(ride)
    
    print(f"\n📊 Final Ride State:")
    print(f"   Ride ID: {ride.ride_id.value}")
    print(f"   Status: {ride.status.value}")
    print(f"   Final Fare: ₹{ride.final_fare.amount}")
    print(f"   Version: {ride.version}")
    
    # Show complete timeline
    print(f"\n📅 Ride Timeline:")
    timeline = ride.get_ride_timeline()
    for i, event in enumerate(timeline, 1):
        print(f"   {i}. {event['event']} at {event['timestamp'].strftime('%H:%M:%S')}")
        print(f"      {event['details']}")
    
    # Create snapshot for performance
    repository.create_snapshot(ride_id)
    
    # Demonstrate event sourcing - reload from events
    print(f"\n🔄 Demonstrating Event Sourcing - Reloading from events...")
    
    # Create new instance and load from event store
    new_ride_instance = repository.get_by_id(ride_id)
    
    if new_ride_instance:
        print(f"✅ Successfully reloaded ride from events")
        print(f"   Status: {new_ride_instance.status.value}")
        print(f"   Version: {new_ride_instance.version}")
        print(f"   Final Fare: ₹{new_ride_instance.final_fare.amount}")
        print(f"   Customer Rating: {new_ride_instance._customer_rating}")
    
    # Show all stored events
    stored_events = event_store.get_events(ride_id.value)
    print(f"\n📝 Total Events Stored: {len(stored_events)}")
    for i, event in enumerate(stored_events, 1):
        print(f"   {i}. {event['event_type']} (v{event['version']})")
    
    return ride, event_store

if __name__ == "__main__":
    print("🏛️ Ola Ride Event Sourcing - DDD Example")
    print("=" * 45)
    
    # Run complete simulation
    final_ride, final_event_store = simulate_complete_ola_ride()
    
    print(f"\n✨ Event Sourcing Benefits Demonstrated:")
    print(f"   ✅ Complete audit trail maintained")
    print(f"   ✅ State can be recreated from events")
    print(f"   ✅ Time travel possible to any point")
    print(f"   ✅ Perfect for compliance and debugging")
    
    print(f"\n✨ Ready for production Ola-scale system!")
    print(f"✨ All ride state changes captured as immutable events!")