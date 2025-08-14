#!/usr/bin/env python3
"""
Domain-Driven Design: CQRS Pattern - IRCTC Booking System
Hindi Tech Podcast Series - Episode 40

यह example दिखाता है कि कैसे DDD में CQRS (Command Query Responsibility Segregation) 
pattern का इस्तेमाल करके IRCTC booking system बनाते हैं। 
Commands और Queries अलग-अलग models use करते हैं।

Author: Hindi Tech Podcast
Date: 2025
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from uuid import uuid4
from decimal import Decimal
from enum import Enum
import json
import threading
import time

# ====================================================================
# COMMAND SIDE - Write Model (Transactional consistency)
# यह side transactions को handle करता है
# ====================================================================

# Domain Events
@dataclass
class DomainEvent:
    event_id: str
    aggregate_id: str
    version: int
    timestamp: datetime
    event_type: str

@dataclass
class BookingInitiatedEvent(DomainEvent):
    user_id: str
    train_number: str
    journey_date: date
    class_type: str
    passenger_count: int

@dataclass
class SeatAllocatedEvent(DomainEvent):
    seat_numbers: List[str]
    coach_number: str

@dataclass
class PaymentProcessedEvent(DomainEvent):
    amount: Decimal
    payment_method: str
    transaction_id: str

@dataclass
class BookingConfirmedEvent(DomainEvent):
    pnr: str
    booking_status: str

@dataclass
class BookingCancelledEvent(DomainEvent):
    cancellation_reason: str
    refund_amount: Decimal

# Enums
class BookingStatus(Enum):
    INITIATED = "initiated"
    PAYMENT_PENDING = "payment_pending"
    CONFIRMED = "confirmed"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"
    RAC = "rac"

class ClassType(Enum):
    SLEEPER = "SL"
    AC_3_TIER = "3A"
    AC_2_TIER = "2A"
    AC_1_TIER = "1A"
    CHAIR_CAR = "CC"
    EXECUTIVE_CHAIR = "EC"

class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

# Value Objects
@dataclass(frozen=True)
class PNR:
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) != 10:
            raise ValueError("PNR must be 10 characters")

@dataclass(frozen=True)
class TrainNumber:
    value: str
    
    def __post_init__(self):
        if not self.value or not self.value.isdigit() or len(self.value) != 5:
            raise ValueError("Train number must be 5 digits")

@dataclass(frozen=True)
class Passenger:
    name: str
    age: int
    gender: str
    berth_preference: Optional[str] = None
    
    def __post_init__(self):
        if self.age < 1 or self.age > 120:
            raise ValueError("Invalid age")
        if self.gender not in ["M", "F", "T"]:
            raise ValueError("Gender must be M, F, or T")

@dataclass(frozen=True)
class SeatAllocation:
    coach_number: str
    seat_number: str
    berth_type: str
    passenger_name: str

# Command Aggregate - Write Model
class TrainBookingAggregate:
    """
    Train Booking Aggregate - Command Side (Write Model)
    
    यह aggregate booking commands को handle करता है।
    Optimized for transactional consistency.
    """
    
    def __init__(self, booking_id: str):
        # Identity
        self._booking_id = booking_id
        
        # Booking details
        self._user_id: Optional[str] = None
        self._train_number: Optional[TrainNumber] = None
        self._journey_date: Optional[date] = None
        self._class_type: Optional[ClassType] = None
        self._passengers: List[Passenger] = []
        
        # Status and processing
        self._status = BookingStatus.INITIATED
        self._pnr: Optional[PNR] = None
        self._created_at = datetime.now()
        self._updated_at = datetime.now()
        
        # Financial
        self._total_amount: Optional[Decimal] = None
        self._payment_status = PaymentStatus.PENDING
        self._transaction_id: Optional[str] = None
        
        # Seat allocation
        self._seat_allocations: List[SeatAllocation] = []
        
        # Concurrency control
        self._version = 0
        self._uncommitted_events: List[DomainEvent] = []
    
    @property
    def booking_id(self) -> str:
        return self._booking_id
    
    @property
    def status(self) -> BookingStatus:
        return self._status
    
    @property
    def pnr(self) -> Optional[PNR]:
        return self._pnr
    
    @property
    def version(self) -> int:
        return self._version
    
    # Command Methods
    
    def initiate_booking(
        self,
        user_id: str,
        train_number: str,
        journey_date: date,
        class_type: str,
        passengers: List[Passenger]
    ) -> None:
        """
        Initiate train booking
        Train booking शुरू करना
        """
        if self._status != BookingStatus.INITIATED:
            raise ValueError("Booking already processed")
        
        if not passengers or len(passengers) > 6:
            raise ValueError("Passenger count must be between 1-6")
        
        if journey_date <= date.today():
            raise ValueError("Journey date must be in future")
        
        # Validate train number
        train_num = TrainNumber(train_number)
        class_enum = ClassType(class_type)
        
        self._user_id = user_id
        self._train_number = train_num
        self._journey_date = journey_date
        self._class_type = class_enum
        self._passengers = passengers.copy()
        
        # Calculate amount based on class and distance (simplified)
        base_fare = self._calculate_fare(class_enum, len(passengers))
        self._total_amount = base_fare
        
        self._status = BookingStatus.PAYMENT_PENDING
        self._version += 1
        
        # Add domain event
        event = BookingInitiatedEvent(
            event_id=str(uuid4()),
            aggregate_id=self._booking_id,
            version=self._version,
            timestamp=datetime.now(),
            event_type="BookingInitiated",
            user_id=user_id,
            train_number=train_number,
            journey_date=journey_date,
            class_type=class_type,
            passenger_count=len(passengers)
        )
        self._uncommitted_events.append(event)
        
        print(f"🎫 Booking initiated: {self._booking_id}")
        print(f"   Train: {train_number}")
        print(f"   Date: {journey_date}")
        print(f"   Passengers: {len(passengers)}")
        print(f"   Amount: ₹{self._total_amount}")
    
    def process_payment(self, payment_method: str, transaction_id: str) -> None:
        """
        Process payment for booking
        Booking के लिए payment process करना
        """
        if self._status != BookingStatus.PAYMENT_PENDING:
            raise ValueError("Payment not pending")
        
        if not transaction_id or len(transaction_id) < 10:
            raise ValueError("Invalid transaction ID")
        
        # Simulate payment processing
        import random
        if random.random() > 0.05:  # 95% success rate
            self._payment_status = PaymentStatus.SUCCESS
            self._transaction_id = transaction_id
            
            # Try to allocate seats
            allocation_result = self._attempt_seat_allocation()
            
            if allocation_result['success']:
                self._status = BookingStatus.CONFIRMED
                self._pnr = PNR(self._generate_pnr())
                self._seat_allocations = allocation_result['seats']
                
                # Add confirmation event
                event = BookingConfirmedEvent(
                    event_id=str(uuid4()),
                    aggregate_id=self._booking_id,
                    version=self._version + 1,
                    timestamp=datetime.now(),
                    event_type="BookingConfirmed",
                    pnr=self._pnr.value,
                    booking_status=self._status.value
                )
                self._uncommitted_events.append(event)
                
                print(f"✅ Booking confirmed!")
                print(f"   PNR: {self._pnr.value}")
                print(f"   Seats allocated: {len(self._seat_allocations)}")
                
            else:
                # No seats available - add to waitlist
                self._status = BookingStatus.WAITLISTED
                self._pnr = PNR(self._generate_pnr())
                
                print(f"📋 Added to waitlist")
                print(f"   PNR: {self._pnr.value}")
            
            # Add payment event
            payment_event = PaymentProcessedEvent(
                event_id=str(uuid4()),
                aggregate_id=self._booking_id,
                version=self._version + 1,
                timestamp=datetime.now(),
                event_type="PaymentProcessed",
                amount=self._total_amount,
                payment_method=payment_method,
                transaction_id=transaction_id
            )
            self._uncommitted_events.append(payment_event)
            
        else:
            # Payment failed
            self._payment_status = PaymentStatus.FAILED
            print(f"❌ Payment failed for booking: {self._booking_id}")
        
        self._version += 1
        self._updated_at = datetime.now()
    
    def cancel_booking(self, cancellation_reason: str) -> None:
        """
        Cancel booking
        Booking cancel करना
        """
        if self._status not in [BookingStatus.CONFIRMED, BookingStatus.WAITLISTED]:
            raise ValueError("Can only cancel confirmed or waitlisted bookings")
        
        # Calculate refund amount based on cancellation rules
        refund_amount = self._calculate_refund_amount()
        
        self._status = BookingStatus.CANCELLED
        self._version += 1
        
        # Add cancellation event
        event = BookingCancelledEvent(
            event_id=str(uuid4()),
            aggregate_id=self._booking_id,
            version=self._version,
            timestamp=datetime.now(),
            event_type="BookingCancelled",
            cancellation_reason=cancellation_reason,
            refund_amount=refund_amount
        )
        self._uncommitted_events.append(event)
        
        print(f"❌ Booking cancelled: {self._booking_id}")
        print(f"   Reason: {cancellation_reason}")
        print(f"   Refund: ₹{refund_amount}")
    
    def _calculate_fare(self, class_type: ClassType, passenger_count: int) -> Decimal:
        """Calculate fare based on class and passenger count"""
        base_rates = {
            ClassType.SLEEPER: Decimal("250"),
            ClassType.AC_3_TIER: Decimal("400"),
            ClassType.AC_2_TIER: Decimal("600"),
            ClassType.AC_1_TIER: Decimal("1200"),
            ClassType.CHAIR_CAR: Decimal("150"),
            ClassType.EXECUTIVE_CHAIR: Decimal("300")
        }
        
        base_fare = base_rates.get(class_type, Decimal("250"))
        total_fare = base_fare * passenger_count
        
        # Add taxes and reservation charges
        taxes = total_fare * Decimal("0.05")  # 5% tax
        reservation_charge = Decimal("40") * passenger_count
        
        return total_fare + taxes + reservation_charge
    
    def _attempt_seat_allocation(self) -> Dict[str, Any]:
        """Attempt to allocate seats (simplified logic)"""
        # Simulate seat availability check
        import random
        
        # 80% chance of getting confirmed seats
        if random.random() > 0.2:
            seats = []
            coach_number = f"{self._class_type.value}1"
            
            for i, passenger in enumerate(self._passengers):
                seat_number = f"{20 + i}"
                berth_type = ["LB", "MB", "UB", "SL", "SU"][i % 5]
                
                seat = SeatAllocation(
                    coach_number=coach_number,
                    seat_number=seat_number,
                    berth_type=berth_type,
                    passenger_name=passenger.name
                )
                seats.append(seat)
            
            return {"success": True, "seats": seats}
        else:
            return {"success": False, "seats": []}
    
    def _generate_pnr(self) -> str:
        """Generate 10-digit PNR"""
        import random
        return f"{random.randint(1000000000, 9999999999)}"
    
    def _calculate_refund_amount(self) -> Decimal:
        """Calculate refund amount based on cancellation time"""
        if not self._total_amount:
            return Decimal("0")
        
        # Simple refund logic - 75% refund if cancelled before journey date
        return self._total_amount * Decimal("0.75")
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        return self._uncommitted_events.copy()
    
    def mark_events_as_committed(self) -> None:
        self._uncommitted_events.clear()

# ====================================================================
# QUERY SIDE - Read Model (Optimized for queries)
# यह side queries को handle करता है
# ====================================================================

@dataclass
class BookingReadModel:
    """
    Booking Read Model - Optimized for queries
    यह model fast queries के लिए optimized है
    """
    booking_id: str
    user_id: str
    pnr: Optional[str]
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    journey_date: date
    departure_time: str
    arrival_time: str
    class_type: str
    passenger_names: List[str]
    seat_details: List[Dict[str, str]]
    booking_status: str
    total_amount: float
    payment_status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class TrainReadModel:
    """Train information read model"""
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    departure_time: str
    arrival_time: str
    available_classes: List[str]
    seat_availability: Dict[str, int]  # class -> available seats
    base_fare: Dict[str, float]       # class -> fare

@dataclass
class UserBookingHistoryReadModel:
    """User booking history read model"""
    user_id: str
    total_bookings: int
    confirmed_bookings: int
    cancelled_bookings: int
    total_amount_spent: float
    recent_bookings: List[Dict[str, Any]]
    frequent_routes: List[Dict[str, Any]]

# Query Handlers - Read side operations
class BookingQueryHandler:
    """
    Handles all booking-related queries
    सारे booking queries को handle करता है
    """
    
    def __init__(self):
        # Simulated read database (in production यह actual database होगा)
        self._booking_read_models: Dict[str, BookingReadModel] = {}
        self._train_read_models: Dict[str, TrainReadModel] = {}
        self._user_booking_history: Dict[str, UserBookingHistoryReadModel] = {}
        self._pnr_to_booking_id: Dict[str, str] = {}
        
        # Initialize sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize sample train data"""
        # Popular Indian trains
        trains = [
            {
                "number": "12951",
                "name": "Mumbai Rajdhani Express",
                "source": "Mumbai Central",
                "destination": "New Delhi",
                "departure": "16:55",
                "arrival": "08:35+1"
            },
            {
                "number": "12002",
                "name": "Shatabdi Express",
                "source": "New Delhi", 
                "destination": "Chandigarh",
                "departure": "07:20",
                "arrival": "10:45"
            },
            {
                "number": "16649",
                "name": "Parasuram Express",
                "source": "Mangalore",
                "destination": "Thiruvananthapuram",
                "departure": "14:30",
                "arrival": "06:00+1"
            }
        ]
        
        for train in trains:
            self._train_read_models[train["number"]] = TrainReadModel(
                train_number=train["number"],
                train_name=train["name"],
                source_station=train["source"],
                destination_station=train["destination"],
                departure_time=train["departure"],
                arrival_time=train["arrival"],
                available_classes=["SL", "3A", "2A", "1A"],
                seat_availability={
                    "SL": 75,
                    "3A": 32,
                    "2A": 28,
                    "1A": 12
                },
                base_fare={
                    "SL": 250.0,
                    "3A": 400.0,
                    "2A": 600.0,
                    "1A": 1200.0
                }
            )
    
    def get_booking_by_pnr(self, pnr: str) -> Optional[BookingReadModel]:
        """
        Get booking details by PNR
        PNR से booking details निकालना
        """
        booking_id = self._pnr_to_booking_id.get(pnr)
        if booking_id:
            return self._booking_read_models.get(booking_id)
        return None
    
    def get_booking_by_id(self, booking_id: str) -> Optional[BookingReadModel]:
        """Get booking by booking ID"""
        return self._booking_read_models.get(booking_id)
    
    def search_trains(
        self,
        source: str,
        destination: str,
        journey_date: date,
        class_preference: Optional[str] = None
    ) -> List[TrainReadModel]:
        """
        Search trains between stations
        Stations के बीच trains search करना
        """
        results = []
        
        for train in self._train_read_models.values():
            # Simple matching logic (production में complex होगा)
            if (source.lower() in train.source_station.lower() and 
                destination.lower() in train.destination_station.lower()):
                
                if class_preference:
                    if class_preference in train.available_classes:
                        results.append(train)
                else:
                    results.append(train)
        
        return results
    
    def get_user_booking_history(self, user_id: str) -> Optional[UserBookingHistoryReadModel]:
        """
        Get user's booking history
        User की booking history निकालना
        """
        return self._user_booking_history.get(user_id)
    
    def get_bookings_by_date_range(
        self,
        start_date: date,
        end_date: date,
        status_filter: Optional[str] = None
    ) -> List[BookingReadModel]:
        """Get bookings within date range"""
        results = []
        
        for booking in self._booking_read_models.values():
            if start_date <= booking.journey_date <= end_date:
                if status_filter is None or booking.booking_status == status_filter:
                    results.append(booking)
        
        return results
    
    def get_revenue_analytics(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get revenue analytics for date range
        Date range के लिए revenue analytics
        """
        bookings = self.get_bookings_by_date_range(start_date, end_date, "confirmed")
        
        total_revenue = sum(booking.total_amount for booking in bookings)
        booking_count = len(bookings)
        
        # Class-wise revenue
        class_revenue = {}
        for booking in bookings:
            class_type = booking.class_type
            class_revenue[class_type] = class_revenue.get(class_type, 0) + booking.total_amount
        
        return {
            "total_revenue": total_revenue,
            "booking_count": booking_count,
            "average_booking_value": total_revenue / max(booking_count, 1),
            "class_wise_revenue": class_revenue,
            "period": f"{start_date} to {end_date}"
        }
    
    def update_booking_read_model(self, booking_aggregate: TrainBookingAggregate) -> None:
        """
        Update read model from aggregate (Event handler में call होगा)
        Aggregate से read model को update करना
        """
        # Convert aggregate to read model
        seat_details = []
        for allocation in booking_aggregate._seat_allocations:
            seat_details.append({
                "coach": allocation.coach_number,
                "seat": allocation.seat_number,
                "berth": allocation.berth_type,
                "passenger": allocation.passenger_name
            })
        
        # Get train details
        train = self._train_read_models.get(booking_aggregate._train_number.value if booking_aggregate._train_number else "")
        train_name = train.train_name if train else "Unknown Train"
        source_station = train.source_station if train else "Unknown"
        destination_station = train.destination_station if train else "Unknown"
        departure_time = train.departure_time if train else "Unknown"
        arrival_time = train.arrival_time if train else "Unknown"
        
        # Create read model
        read_model = BookingReadModel(
            booking_id=booking_aggregate.booking_id,
            user_id=booking_aggregate._user_id or "",
            pnr=booking_aggregate._pnr.value if booking_aggregate._pnr else None,
            train_number=booking_aggregate._train_number.value if booking_aggregate._train_number else "",
            train_name=train_name,
            source_station=source_station,
            destination_station=destination_station,
            journey_date=booking_aggregate._journey_date or date.today(),
            departure_time=departure_time,
            arrival_time=arrival_time,
            class_type=booking_aggregate._class_type.value if booking_aggregate._class_type else "",
            passenger_names=[p.name for p in booking_aggregate._passengers],
            seat_details=seat_details,
            booking_status=booking_aggregate._status.value,
            total_amount=float(booking_aggregate._total_amount or Decimal("0")),
            payment_status=booking_aggregate._payment_status.value,
            created_at=booking_aggregate._created_at,
            updated_at=booking_aggregate._updated_at
        )
        
        # Store in read database
        self._booking_read_models[booking_aggregate.booking_id] = read_model
        
        # Update PNR mapping
        if read_model.pnr:
            self._pnr_to_booking_id[read_model.pnr] = read_model.booking_id
        
        # Update user history
        self._update_user_booking_history(read_model)
        
        print(f"📊 Read model updated for booking: {booking_aggregate.booking_id}")
    
    def _update_user_booking_history(self, booking: BookingReadModel) -> None:
        """Update user booking history"""
        user_id = booking.user_id
        
        if user_id not in self._user_booking_history:
            self._user_booking_history[user_id] = UserBookingHistoryReadModel(
                user_id=user_id,
                total_bookings=0,
                confirmed_bookings=0,
                cancelled_bookings=0,
                total_amount_spent=0.0,
                recent_bookings=[],
                frequent_routes=[]
            )
        
        history = self._user_booking_history[user_id]
        history.total_bookings += 1
        
        if booking.booking_status == "confirmed":
            history.confirmed_bookings += 1
            history.total_amount_spent += booking.total_amount
        elif booking.booking_status == "cancelled":
            history.cancelled_bookings += 1
        
        # Add to recent bookings (keep last 10)
        booking_summary = {
            "booking_id": booking.booking_id,
            "pnr": booking.pnr,
            "train": f"{booking.train_number} - {booking.train_name}",
            "date": booking.journey_date.isoformat(),
            "status": booking.booking_status,
            "amount": booking.total_amount
        }
        
        history.recent_bookings.append(booking_summary)
        if len(history.recent_bookings) > 10:
            history.recent_bookings = history.recent_bookings[-10:]

# Command Handlers - Write side operations
class BookingCommandHandler:
    """
    Handles all booking commands
    सारे booking commands को handle करता है
    """
    
    def __init__(self, query_handler: BookingQueryHandler):
        self._query_handler = query_handler
        self._aggregates: Dict[str, TrainBookingAggregate] = {}
    
    def handle_initiate_booking(self, command: Dict[str, Any]) -> str:
        """Handle booking initiation command"""
        booking_id = str(uuid4())
        aggregate = TrainBookingAggregate(booking_id)
        
        # Convert passengers
        passengers = []
        for p_data in command['passengers']:
            passenger = Passenger(
                name=p_data['name'],
                age=p_data['age'],
                gender=p_data['gender'],
                berth_preference=p_data.get('berth_preference')
            )
            passengers.append(passenger)
        
        aggregate.initiate_booking(
            user_id=command['user_id'],
            train_number=command['train_number'],
            journey_date=command['journey_date'],
            class_type=command['class_type'],
            passengers=passengers
        )
        
        # Store aggregate
        self._aggregates[booking_id] = aggregate
        
        # Update read model
        self._query_handler.update_booking_read_model(aggregate)
        
        return booking_id
    
    def handle_process_payment(self, command: Dict[str, Any]) -> None:
        """Handle payment processing command"""
        booking_id = command['booking_id']
        aggregate = self._aggregates.get(booking_id)
        
        if not aggregate:
            raise ValueError("Booking not found")
        
        aggregate.process_payment(
            payment_method=command['payment_method'],
            transaction_id=command['transaction_id']
        )
        
        # Update read model
        self._query_handler.update_booking_read_model(aggregate)
    
    def handle_cancel_booking(self, command: Dict[str, Any]) -> None:
        """Handle booking cancellation command"""
        booking_id = command['booking_id']
        aggregate = self._aggregates.get(booking_id)
        
        if not aggregate:
            raise ValueError("Booking not found")
        
        aggregate.cancel_booking(command['cancellation_reason'])
        
        # Update read model
        self._query_handler.update_booking_read_model(aggregate)

# ====================================================================
# CQRS APPLICATION SERVICE
# ====================================================================

class IRCTCBookingService:
    """
    IRCTC Booking Service with CQRS
    CQRS के साथ IRCTC booking service
    """
    
    def __init__(self):
        self._query_handler = BookingQueryHandler()
        self._command_handler = BookingCommandHandler(self._query_handler)
    
    # Command methods (Write operations)
    
    def book_train_ticket(
        self,
        user_id: str,
        train_number: str,
        journey_date: date,
        class_type: str,
        passengers: List[Dict[str, Any]],
        payment_method: str
    ) -> Dict[str, Any]:
        """
        Complete train ticket booking
        Complete train ticket booking process
        """
        print(f"\n🎫 Processing train booking...")
        
        # Step 1: Initiate booking (Command)
        initiate_command = {
            'user_id': user_id,
            'train_number': train_number,
            'journey_date': journey_date,
            'class_type': class_type,
            'passengers': passengers
        }
        
        booking_id = self._command_handler.handle_initiate_booking(initiate_command)
        
        # Step 2: Process payment (Command)
        payment_command = {
            'booking_id': booking_id,
            'payment_method': payment_method,
            'transaction_id': f"TXN_{int(datetime.now().timestamp())}"
        }
        
        self._command_handler.handle_process_payment(payment_command)
        
        # Step 3: Return booking details (Query)
        booking_details = self._query_handler.get_booking_by_id(booking_id)
        
        return {
            'booking_id': booking_id,
            'pnr': booking_details.pnr if booking_details else None,
            'status': booking_details.booking_status if booking_details else 'unknown',
            'amount': booking_details.total_amount if booking_details else 0
        }
    
    def cancel_booking(self, booking_id: str, reason: str) -> bool:
        """Cancel booking (Command)"""
        cancel_command = {
            'booking_id': booking_id,
            'cancellation_reason': reason
        }
        
        try:
            self._command_handler.handle_cancel_booking(cancel_command)
            return True
        except Exception as e:
            print(f"❌ Cancellation failed: {e}")
            return False
    
    # Query methods (Read operations)
    
    def get_booking_details(self, pnr: str) -> Optional[Dict[str, Any]]:
        """Get booking details by PNR (Query)"""
        booking = self._query_handler.get_booking_by_pnr(pnr)
        if booking:
            return asdict(booking)
        return None
    
    def search_trains(
        self,
        source: str,
        destination: str,
        journey_date: date,
        class_preference: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search trains (Query)"""
        trains = self._query_handler.search_trains(
            source, destination, journey_date, class_preference
        )
        return [asdict(train) for train in trains]
    
    def get_user_history(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user booking history (Query)"""
        history = self._query_handler.get_user_booking_history(user_id)
        if history:
            return asdict(history)
        return None
    
    def get_revenue_report(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get revenue analytics (Query)"""
        return self._query_handler.get_revenue_analytics(start_date, end_date)

def simulate_irctc_cqrs_system():
    """Simulate IRCTC system with CQRS pattern"""
    
    print("🚂 IRCTC CQRS System Simulation")
    print("=" * 35)
    
    # Create service
    booking_service = IRCTCBookingService()
    
    print(f"\n🔍 Step 1: Search trains (Query Side)")
    trains = booking_service.search_trains(
        source="Mumbai",
        destination="Delhi",
        journey_date=date.today() + timedelta(days=15)
    )
    
    print(f"   Found {len(trains)} trains:")
    for train in trains:
        print(f"   - {train['train_number']}: {train['train_name']}")
        print(f"     {train['departure_time']} - {train['arrival_time']}")
    
    if trains:
        selected_train = trains[0]
        print(f"\n✅ Selected train: {selected_train['train_name']}")
        
        print(f"\n📝 Step 2: Book ticket (Command Side)")
        
        # Sample passengers
        passengers = [
            {
                'name': 'Rahul Sharma',
                'age': 35,
                'gender': 'M',
                'berth_preference': 'LB'
            },
            {
                'name': 'Priya Sharma',
                'age': 32,
                'gender': 'F',
                'berth_preference': 'LB'
            }
        ]
        
        # Book ticket
        booking_result = booking_service.book_train_ticket(
            user_id="USER_12345",
            train_number=selected_train['train_number'],
            journey_date=date.today() + timedelta(days=15),
            class_type="3A",
            passengers=passengers,
            payment_method="UPI"
        )
        
        print(f"   Booking Result: {booking_result}")
        
        if booking_result['pnr']:
            print(f"\n🎫 Step 3: Get booking details (Query Side)")
            
            # Get booking details by PNR
            booking_details = booking_service.get_booking_details(booking_result['pnr'])
            if booking_details:
                print(f"   PNR: {booking_details['pnr']}")
                print(f"   Status: {booking_details['booking_status']}")
                print(f"   Train: {booking_details['train_name']}")
                print(f"   Passengers: {len(booking_details['passenger_names'])}")
                print(f"   Amount: ₹{booking_details['total_amount']}")
            
            print(f"\n📊 Step 4: User history (Query Side)")
            user_history = booking_service.get_user_history("USER_12345")
            if user_history:
                print(f"   Total bookings: {user_history['total_bookings']}")
                print(f"   Confirmed: {user_history['confirmed_bookings']}")
                print(f"   Total spent: ₹{user_history['total_amount_spent']}")
            
            print(f"\n📈 Step 5: Revenue analytics (Query Side)")
            revenue_report = booking_service.get_revenue_report(
                date.today() - timedelta(days=30),
                date.today()
            )
            print(f"   Total Revenue: ₹{revenue_report['total_revenue']}")
            print(f"   Bookings: {revenue_report['booking_count']}")
            print(f"   Average Value: ₹{revenue_report['average_booking_value']:.2f}")
            
            # Demonstrate cancellation
            print(f"\n❌ Step 6: Cancel booking (Command Side)")
            cancel_success = booking_service.cancel_booking(
                booking_result['booking_id'],
                "Change of plan"
            )
            print(f"   Cancellation: {'Success' if cancel_success else 'Failed'}")
    
    print(f"\n✨ CQRS Benefits Demonstrated:")
    print(f"   ✅ Commands and Queries separated")
    print(f"   ✅ Write model optimized for consistency")  
    print(f"   ✅ Read model optimized for performance")
    print(f"   ✅ Independent scaling possible")
    print(f"   ✅ Complex analytics without impacting writes")

if __name__ == "__main__":
    print("🏛️ IRCTC CQRS Implementation - DDD Example")
    print("=" * 50)
    
    simulate_irctc_cqrs_system()
    
    print(f"\n✨ CQRS pattern successfully implemented!")
    print(f"✨ Ready for high-scale IRCTC-like system!")
    print(f"✨ Commands and Queries completely separated!")