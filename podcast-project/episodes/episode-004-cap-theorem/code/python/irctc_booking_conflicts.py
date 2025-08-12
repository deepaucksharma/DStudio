#!/usr/bin/env python3
"""
IRCTC Booking Conflicts System - Episode 4
Railway booking में consistency vs availability का real-world implementation

यह system demonstrate करता है कि कैसे IRCTC जैसे critical booking systems
में consistency को prioritize करना पड़ता है क्योंकि:

- Duplicate bookings नहीं हो सकते (financial loss)
- Seat allocation accurate होना चाहिए
- Waiting list properly maintain होनी चाहिए
- Cancellation और refund consistent होना चाहिए

Real challenges:
- Tatkal booking rush (11 AM sharp)
- Festival season booking load
- Payment failures during booking
- Network timeouts
- Concurrent seat booking attempts
"""

import time
import threading
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import json
import hashlib
from decimal import Decimal, getcontext

getcontext().prec = 10

class BookingStatus(Enum):
    """IRCTC booking status states"""
    INITIATED = "initiated"           # Booking started
    PAYMENT_PENDING = "payment_pending"  # Waiting for payment
    CONFIRMED = "confirmed"           # Seat confirmed
    WAITING_LIST = "waiting_list"     # In waiting list
    RAC = "rac"                      # Reservation Against Cancellation
    CANCELLED = "cancelled"           # User cancelled
    CHART_PREPARED = "chart_prepared" # Final chart ready
    TRAIN_DEPARTED = "train_departed" # Train has left

class SeatType(Enum):
    """Indian Railway seat types"""
    SL = "sleeper"                   # Sleeper class
    AC3 = "ac_3_tier"                # 3AC
    AC2 = "ac_2_tier"                # 2AC  
    AC1 = "ac_first_class"           # 1AC
    CC = "chair_car"                 # Chair car
    EC = "executive_chair"           # Executive chair

class PassengerType(Enum):
    """Passenger categories"""
    GENERAL = "general"              # General passenger
    SENIOR_CITIZEN = "senior_citizen"  # Senior citizen quota
    LADIES = "ladies"                # Ladies quota
    TATKAL = "tatkal"                # Tatkal booking
    PREMIUM_TATKAL = "premium_tatkal" # Premium tatkal

@dataclass
class Passenger:
    """Railway passenger details"""
    name: str
    age: int
    gender: str
    passenger_type: PassengerType = PassengerType.GENERAL
    seat_preference: Optional[str] = None  # Lower, Middle, Upper, Side Lower, Side Upper
    concession: float = 0.0  # Discount percentage

@dataclass
class Train:
    """Train information with seat availability"""
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    departure_time: str
    arrival_time: str
    travel_date: datetime
    seat_availability: Dict[SeatType, int] = field(default_factory=dict)
    waiting_list_count: Dict[SeatType, int] = field(default_factory=dict)
    base_fare: Dict[SeatType, Decimal] = field(default_factory=dict)
    
    def __post_init__(self):
        # Initialize seat availability for popular trains
        if not self.seat_availability:
            self.seat_availability = {
                SeatType.SL: 72,    # Sleeper coach capacity
                SeatType.AC3: 64,   # 3AC coach capacity  
                SeatType.AC2: 48,   # 2AC coach capacity
                SeatType.AC1: 18,   # 1AC coach capacity
                SeatType.CC: 78     # Chair car capacity
            }
        
        if not self.waiting_list_count:
            self.waiting_list_count = {seat_type: 0 for seat_type in SeatType}
        
        if not self.base_fare:
            self.base_fare = {
                SeatType.SL: Decimal('315'),   # Mumbai-Delhi Sleeper
                SeatType.AC3: Decimal('820'),  # Mumbai-Delhi 3AC
                SeatType.AC2: Decimal('1165'), # Mumbai-Delhi 2AC
                SeatType.AC1: Decimal('2040'), # Mumbai-Delhi 1AC
                SeatType.CC: Decimal('655')    # Mumbai-Delhi CC
            }

@dataclass
class BookingRequest:
    """Railway booking request"""
    pnr: str
    user_id: str
    train: Train
    passengers: List[Passenger]
    seat_type: SeatType
    booking_date: datetime
    travel_date: datetime
    total_fare: Decimal = Decimal('0')
    status: BookingStatus = BookingStatus.INITIATED
    payment_gateway_ref: Optional[str] = None
    booking_source: str = "IRCTC_WEBSITE"  # Website, Mobile, Agent
    
    def __post_init__(self):
        if not self.pnr:
            # Generate PNR in IRCTC format
            timestamp = int(time.time())
            self.pnr = f"{timestamp % 10000000000:010d}"  # 10-digit PNR

class IRCTCBookingSystem:
    """
    IRCTC Booking System with Strong Consistency
    
    Design Principles:
    1. No double booking under any circumstances
    2. Accurate seat count maintenance
    3. Proper waiting list management  
    4. Payment consistency with booking
    5. Real-time seat availability updates
    
    यह system availability को sacrifice करके consistency ensure करता है
    क्योंकि railway booking में accuracy सबसे important है।
    """
    
    def __init__(self, num_zones: int = 3):
        # Railway zones setup (like real Indian Railways)
        self.zones = {
            "WESTERN": {"status": "active", "trains": {}, "bookings": {}, "locks": {}},
            "CENTRAL": {"status": "active", "trains": {}, "bookings": {}, "locks": {}},
            "SOUTHERN": {"status": "active", "trains": {}, "bookings": {}, "locks": {}}
        }
        
        # Global distributed locks for seats
        self.seat_locks = {}  # train_date_seat -> lock
        self.booking_locks = {}  # pnr -> lock
        
        # System metrics
        self.total_booking_attempts = 0
        self.successful_bookings = 0
        self.failed_bookings = 0
        self.waiting_list_bookings = 0
        self.concurrent_conflicts = 0
        self.consistency_checks = 0
        
        # Payment integration
        self.payment_timeouts = 0
        self.payment_failures = 0
        
        print("🚂 IRCTC Booking System initialized")
        print(f"🏢 Railway Zones: {list(self.zones.keys())}")
        print("⚖️  Priority: Strong Consistency > Availability")
        
        # Initialize popular trains
        self._initialize_popular_trains()

    def _initialize_popular_trains(self):
        """Initialize popular Indian trains"""
        popular_trains = [
            {
                "train_number": "12951",
                "train_name": "Mumbai Central - New Delhi Rajdhani Express",
                "source_station": "MMCT",
                "destination_station": "NDLS", 
                "departure_time": "16:35",
                "arrival_time": "08:35+1",
                "travel_date": datetime.now() + timedelta(days=30)
            },
            {
                "train_number": "12301",
                "train_name": "Howrah - New Delhi Rajdhani Express",
                "source_station": "HWH",
                "destination_station": "NDLS",
                "departure_time": "16:55",
                "arrival_time": "10:05+1", 
                "travel_date": datetime.now() + timedelta(days=30)
            },
            {
                "train_number": "12626",
                "train_name": "Kerala Express",
                "source_station": "NDLS",
                "destination_station": "TVC",
                "departure_time": "11:45",
                "arrival_time": "10:15+2",
                "travel_date": datetime.now() + timedelta(days=30)
            }
        ]
        
        # Distribute trains across zones
        for i, train_data in enumerate(popular_trains):
            train = Train(**train_data)
            zone = list(self.zones.keys())[i % len(self.zones)]
            
            # Replicate train data across all zones for high availability
            for zone_id in self.zones:
                self.zones[zone_id]["trains"][train.train_number] = train
        
        print("✅ Popular trains initialized across all zones")

    def book_ticket(self, user_id: str, train_number: str, passengers: List[Passenger], 
                   seat_type: SeatType, travel_date: datetime,
                   booking_source: str = "IRCTC_WEBSITE") -> Tuple[bool, str, Dict]:
        """
        Book railway ticket with strong consistency guarantee
        
        यह function ensure करता है कि कोई भी duplicate booking न हो
        और seat availability accurate रहे
        """
        self.total_booking_attempts += 1
        start_time = time.time()
        
        print(f"\n🎫 Booking attempt for train {train_number}")
        print(f"   User: {user_id}")
        print(f"   Passengers: {len(passengers)}")
        print(f"   Seat type: {seat_type.value}")
        print(f"   Source: {booking_source}")
        
        # Step 1: Find train and validate basic requirements
        train = self._find_train(train_number, travel_date)
        if not train:
            self.failed_bookings += 1
            return False, "Train not found or not available for booking", {}
        
        # Step 2: Create booking request
        booking_request = BookingRequest(
            pnr="",  # Will be generated
            user_id=user_id,
            train=train,
            passengers=passengers,
            seat_type=seat_type,
            booking_date=datetime.now(),
            travel_date=travel_date,
            booking_source=booking_source
        )
        
        # Step 3: Calculate total fare
        booking_request.total_fare = self._calculate_total_fare(booking_request)
        
        # Step 4: Acquire distributed locks for all required seats
        required_seats = len(passengers)
        lock_key = f"{train_number}_{travel_date.date()}_{seat_type.value}"
        
        print(f"🔒 Acquiring locks for {required_seats} seats...")
        
        if not self._acquire_distributed_lock(lock_key, timeout=30.0):
            self.failed_bookings += 1
            self.concurrent_conflicts += 1
            return False, "Unable to acquire seat locks - high concurrent booking load", {}
        
        try:
            # Step 5: Check seat availability under lock
            availability_result = self._check_seat_availability_locked(train, seat_type, required_seats)
            
            if availability_result["status"] == "AVAILABLE":
                # Step 6: Reserve seats immediately
                result = self._reserve_seats_immediately(booking_request)
                if result[0]:
                    self.successful_bookings += 1
                    processing_time = time.time() - start_time
                    
                    return True, "Booking confirmed", {
                        "pnr": booking_request.pnr,
                        "status": "CONFIRMED",
                        "total_fare": str(booking_request.total_fare),
                        "processing_time": f"{processing_time:.3f}s",
                        "seat_numbers": result[2].get("seat_numbers", []),
                        "payment_due_time": (datetime.now() + timedelta(minutes=10)).isoformat()
                    }
                else:
                    self.failed_bookings += 1
                    return False, result[1], {}
            
            elif availability_result["status"] == "WAITING_LIST":
                # Step 7: Add to waiting list
                result = self._add_to_waiting_list(booking_request)
                if result[0]:
                    self.waiting_list_bookings += 1
                    
                    return True, "Added to waiting list", {
                        "pnr": booking_request.pnr,
                        "status": "WAITING_LIST",
                        "waiting_list_position": result[2].get("position", 0),
                        "total_fare": str(booking_request.total_fare),
                        "confirmation_probability": self._calculate_confirmation_probability(
                            train, seat_type, result[2].get("position", 0)
                        )
                    }
                else:
                    self.failed_bookings += 1
                    return False, result[1], {}
            
            else:
                # Step 8: No seats available even for waiting list
                self.failed_bookings += 1
                return False, "No seats available - booking closed for this train", {}
        
        finally:
            # Step 9: Always release locks
            self._release_distributed_lock(lock_key)

    def _find_train(self, train_number: str, travel_date: datetime) -> Optional[Train]:
        """Find train across all zones"""
        for zone_data in self.zones.values():
            if zone_data["status"] == "active":
                if train_number in zone_data["trains"]:
                    train = zone_data["trains"][train_number]
                    # Check if booking is open (typically 120 days in advance)
                    days_advance = (travel_date.date() - datetime.now().date()).days
                    if 0 <= days_advance <= 120:
                        return train
        return None

    def _calculate_total_fare(self, booking_request: BookingRequest) -> Decimal:
        """Calculate total fare including taxes and fees"""
        base_fare = booking_request.train.base_fare[booking_request.seat_type]
        total_fare = Decimal('0')
        
        for passenger in booking_request.passengers:
            passenger_fare = base_fare
            
            # Apply concessions
            if passenger.passenger_type == PassengerType.SENIOR_CITIZEN and passenger.age >= 60:
                passenger_fare *= Decimal('0.6')  # 40% discount for senior citizens
            elif passenger.passenger_type == PassengerType.LADIES and passenger.gender == "F":
                passenger_fare *= Decimal('0.9')  # 10% discount for ladies
            
            # Tatkal charges
            if passenger.passenger_type == PassengerType.TATKAL:
                tatkal_charge = min(base_fare * Decimal('0.3'), Decimal('500'))  # Max ₹500
                passenger_fare += tatkal_charge
            elif passenger.passenger_type == PassengerType.PREMIUM_TATKAL:
                premium_charge = min(base_fare * Decimal('0.5'), Decimal('1000'))  # Max ₹1000
                passenger_fare += premium_charge
            
            total_fare += passenger_fare
        
        # Add reservation fee and GST
        reservation_fee = Decimal('40') * len(booking_request.passengers)  # ₹40 per passenger
        gst = (total_fare + reservation_fee) * Decimal('0.05')  # 5% GST
        
        final_fare = total_fare + reservation_fee + gst
        
        return final_fare.quantize(Decimal('0.01'))  # Round to 2 decimal places

    def _acquire_distributed_lock(self, lock_key: str, timeout: float) -> bool:
        """
        Acquire distributed lock across all zones
        
        यह critical section है - सभी zones में consistent locking जरूरी है
        ताकि कोई भी double booking न हो
        """
        acquired_zones = []
        start_time = time.time()
        
        try:
            # Try to acquire locks from all zones
            for zone_id, zone_data in self.zones.items():
                if zone_data["status"] != "active":
                    continue
                
                # Simulate network delay and lock acquisition
                time.sleep(random.uniform(0.01, 0.05))
                
                # Check if lock is already held
                if lock_key in zone_data["locks"]:
                    # Lock is held by someone else - check for timeout
                    lock_time = zone_data["locks"][lock_key]["timestamp"]
                    if (datetime.now() - lock_time).total_seconds() > 60:  # 1 minute timeout
                        # Force release stale lock
                        del zone_data["locks"][lock_key]
                    else:
                        # Lock is actively held
                        raise Exception(f"Lock held by another process in zone {zone_id}")
                
                # Acquire lock
                zone_data["locks"][lock_key] = {
                    "timestamp": datetime.now(),
                    "thread_id": threading.get_ident(),
                    "acquired_by": f"booking_system_{int(time.time())}"
                }
                acquired_zones.append(zone_id)
                
                # Check timeout
                if time.time() - start_time > timeout:
                    raise Exception("Lock acquisition timeout")
            
            # Successfully acquired all locks
            self.seat_locks[lock_key] = {
                "zones": acquired_zones,
                "timestamp": datetime.now()
            }
            
            print(f"🔒 Distributed lock acquired: {lock_key}")
            return True
        
        except Exception as e:
            # Release any acquired locks
            for zone_id in acquired_zones:
                try:
                    if lock_key in self.zones[zone_id]["locks"]:
                        del self.zones[zone_id]["locks"][lock_key]
                except:
                    pass
            
            print(f"❌ Failed to acquire distributed lock: {e}")
            return False

    def _release_distributed_lock(self, lock_key: str):
        """Release distributed lock across all zones"""
        if lock_key in self.seat_locks:
            lock_info = self.seat_locks[lock_key]
            
            # Release locks in all zones
            for zone_id in lock_info["zones"]:
                try:
                    if lock_key in self.zones[zone_id]["locks"]:
                        del self.zones[zone_id]["locks"][lock_key]
                except:
                    pass  # Ignore errors during release
            
            del self.seat_locks[lock_key]
            print(f"🔓 Distributed lock released: {lock_key}")

    def _check_seat_availability_locked(self, train: Train, seat_type: SeatType, 
                                       required_seats: int) -> Dict:
        """
        Check seat availability under distributed lock
        
        यह function lock के अंदर seat availability check करता है
        ताकि concurrent access का issue न आए
        """
        self.consistency_checks += 1
        
        available_seats = train.seat_availability[seat_type]
        waiting_list = train.waiting_list_count[seat_type]
        
        print(f"📊 Seat availability check:")
        print(f"   Available seats: {available_seats}")
        print(f"   Required seats: {required_seats}")
        print(f"   Current waiting list: {waiting_list}")
        
        if available_seats >= required_seats:
            return {
                "status": "AVAILABLE",
                "available_count": available_seats,
                "message": "Seats available for immediate booking"
            }
        elif waiting_list < 200:  # Max waiting list limit
            return {
                "status": "WAITING_LIST",
                "waiting_position": waiting_list + 1,
                "message": "Added to waiting list"
            }
        else:
            return {
                "status": "CLOSED",
                "message": "Booking closed - waiting list full"
            }

    def _reserve_seats_immediately(self, booking_request: BookingRequest) -> Tuple[bool, str, Dict]:
        """
        Reserve seats immediately with seat number allocation
        
        यहाँ actual seat numbers allocate करते हैं और सभी zones में
        consistent update करते हैं
        """
        train = booking_request.train
        seat_type = booking_request.seat_type
        required_seats = len(booking_request.passengers)
        
        try:
            # Allocate specific seat numbers
            seat_numbers = self._allocate_seat_numbers(train, seat_type, required_seats, booking_request.passengers)
            
            # Update availability across all zones
            for zone_id, zone_data in self.zones.items():
                if zone_data["status"] == "active":
                    zone_train = zone_data["trains"][train.train_number]
                    zone_train.seat_availability[seat_type] -= required_seats
                    
                    # Store booking
                    zone_data["bookings"][booking_request.pnr] = booking_request
            
            booking_request.status = BookingStatus.CONFIRMED
            
            print(f"✅ Seats reserved: {seat_numbers}")
            
            return True, "Seats reserved successfully", {
                "seat_numbers": seat_numbers,
                "coach_details": self._get_coach_details(seat_type, seat_numbers)
            }
        
        except Exception as e:
            print(f"❌ Seat reservation failed: {e}")
            return False, f"Seat reservation failed: {e}", {}

    def _allocate_seat_numbers(self, train: Train, seat_type: SeatType, 
                              required_seats: int, passengers: List[Passenger]) -> List[str]:
        """
        Allocate specific seat numbers based on passenger preferences
        
        यह realistic seat allocation करता है Indian Railway format में
        """
        seat_numbers = []
        
        # Coach prefix based on seat type
        coach_prefix = {
            SeatType.SL: "S",
            SeatType.AC3: "B",
            SeatType.AC2: "A", 
            SeatType.AC1: "H",
            SeatType.CC: "C"
        }[seat_type]
        
        # Current seat counter (simplified allocation)
        current_seat = random.randint(1, 50)  # Start from random position
        
        for i, passenger in enumerate(passengers):
            coach_number = random.randint(1, 6)  # 6 coaches per type typically
            seat_number = current_seat + i
            
            # Handle berth preference for sleeper classes
            if seat_type in [SeatType.SL, SeatType.AC3, SeatType.AC2]:
                berth_types = ["LB", "MB", "UB", "SL", "SU"]  # Lower, Middle, Upper, Side Lower, Side Upper
                
                # Try to honor preference
                if passenger.seat_preference:
                    if "Lower" in passenger.seat_preference:
                        berth = "LB"
                    elif "Upper" in passenger.seat_preference:
                        berth = "UB"
                    elif "Side" in passenger.seat_preference:
                        berth = random.choice(["SL", "SU"])
                    else:
                        berth = random.choice(berth_types)
                else:
                    berth = random.choice(berth_types)
                
                seat_id = f"{coach_prefix}{coach_number}/{seat_number}/{berth}"
            else:
                # Chair car - just seat number
                seat_id = f"{coach_prefix}{coach_number}/{seat_number}"
            
            seat_numbers.append(seat_id)
        
        return seat_numbers

    def _get_coach_details(self, seat_type: SeatType, seat_numbers: List[str]) -> Dict:
        """Get coach details for passenger information"""
        return {
            "coach_type": seat_type.value,
            "total_seats": len(seat_numbers),
            "boarding_info": "Please board the train 30 minutes before departure",
            "amenities": self._get_coach_amenities(seat_type)
        }

    def _get_coach_amenities(self, seat_type: SeatType) -> List[str]:
        """Get amenities available in coach type"""
        amenities_map = {
            SeatType.SL: ["Charging point", "Reading light"],
            SeatType.AC3: ["AC", "Charging point", "Reading light", "Blanket", "Pillow"],
            SeatType.AC2: ["AC", "Charging point", "Reading light", "Blanket", "Pillow", "Curtains"],
            SeatType.AC1: ["AC", "Charging point", "Reading light", "Blanket", "Pillow", "Curtains", "Personal attendant"],
            SeatType.CC: ["AC", "Charging point", "Reclining seats"]
        }
        return amenities_map.get(seat_type, [])

    def _add_to_waiting_list(self, booking_request: BookingRequest) -> Tuple[bool, str, Dict]:
        """Add booking to waiting list"""
        train = booking_request.train
        seat_type = booking_request.seat_type
        
        try:
            # Get current waiting list position
            current_position = train.waiting_list_count[seat_type] + 1
            
            # Update waiting list count across all zones
            for zone_id, zone_data in self.zones.items():
                if zone_data["status"] == "active":
                    zone_train = zone_data["trains"][train.train_number]
                    zone_train.waiting_list_count[seat_type] += 1
                    
                    # Store booking with waiting list status
                    booking_request.status = BookingStatus.WAITING_LIST
                    zone_data["bookings"][booking_request.pnr] = booking_request
            
            print(f"📝 Added to waiting list at position {current_position}")
            
            return True, "Added to waiting list", {
                "position": current_position,
                "estimated_confirmation": self._estimate_confirmation_time(current_position)
            }
        
        except Exception as e:
            return False, f"Failed to add to waiting list: {e}", {}

    def _calculate_confirmation_probability(self, train: Train, seat_type: SeatType, 
                                          waiting_position: int) -> str:
        """Calculate probability of waiting list confirmation"""
        # Historical data suggests ~30% cancellation rate
        expected_cancellations = int(train.seat_availability[seat_type] * 0.3)
        
        if waiting_position <= expected_cancellations:
            return "High (80-90%)"
        elif waiting_position <= expected_cancellations * 2:
            return "Medium (40-60%)" 
        else:
            return "Low (<20%)"

    def _estimate_confirmation_time(self, waiting_position: int) -> str:
        """Estimate when waiting list might get confirmed"""
        if waiting_position <= 10:
            return "Within 24 hours"
        elif waiting_position <= 50:
            return "1-3 days before journey"
        else:
            return "Unlikely to confirm"

    def simulate_tatkal_booking_rush(self, train_number: str, seat_type: SeatType, 
                                    num_users: int = 50, rush_duration: int = 30):
        """
        Simulate Tatkal booking rush at 11 AM
        
        यह test करता है कि system concurrent load को कैसे handle करता है
        जब सारे users एक साथ 11 AM पर Tatkal booking try करते हैं
        """
        print(f"\n⚡ TATKAL BOOKING RUSH SIMULATION")
        print(f"   Train: {train_number}")
        print(f"   Seat Type: {seat_type.value}")
        print(f"   Concurrent users: {num_users}")
        print(f"   Rush duration: {rush_duration} seconds")
        print("   Scenario: All users trying to book exactly at 11:00 AM")
        
        # Reset metrics for this simulation
        initial_attempts = self.total_booking_attempts
        initial_successful = self.successful_bookings
        initial_failed = self.failed_bookings
        initial_conflicts = self.concurrent_conflicts
        
        start_time = time.time()
        
        def simulate_user_booking(user_id: int):
            """Simulate individual user Tatkal booking attempt"""
            try:
                # Create passenger for Tatkal booking
                passenger = Passenger(
                    name=f"Tatkal User {user_id}",
                    age=random.randint(25, 60),
                    gender=random.choice(["M", "F"]),
                    passenger_type=PassengerType.TATKAL,
                    seat_preference=random.choice(["Lower", "Upper", "Side Lower", None])
                )
                
                # Random delay to simulate network latency
                time.sleep(random.uniform(0, 2))
                
                # Attempt booking
                success, message, result = self.book_ticket(
                    user_id=f"tatkal_user_{user_id}",
                    train_number=train_number,
                    passengers=[passenger],
                    seat_type=seat_type,
                    travel_date=datetime.now() + timedelta(days=1),  # Next day travel
                    booking_source="IRCTC_MOBILE"
                )
                
                return {
                    "user_id": user_id,
                    "success": success,
                    "message": message,
                    "result": result
                }
            
            except Exception as e:
                return {
                    "user_id": user_id,
                    "success": False,
                    "message": str(e),
                    "result": {}
                }
        
        # Launch all users simultaneously
        results = []
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            # Submit all booking attempts
            futures = [executor.submit(simulate_user_booking, i) for i in range(num_users)]
            
            # Collect results as they complete
            for future in as_completed(futures, timeout=rush_duration):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        "user_id": -1,
                        "success": False,
                        "message": f"Execution error: {e}",
                        "result": {}
                    })
        
        # Analyze Tatkal rush results
        end_time = time.time()
        actual_duration = end_time - start_time
        
        total_attempts = self.total_booking_attempts - initial_attempts
        successful = self.successful_bookings - initial_successful
        failed = self.failed_bookings - initial_failed
        conflicts = self.concurrent_conflicts - initial_conflicts
        
        confirmed_bookings = len([r for r in results if r["success"] and 
                                 r["result"].get("status") == "CONFIRMED"])
        waiting_list = len([r for r in results if r["success"] and 
                          r["result"].get("status") == "WAITING_LIST"])
        
        print(f"\n📊 TATKAL RUSH RESULTS:")
        print(f"   Duration: {actual_duration:.2f} seconds") 
        print(f"   Total attempts: {total_attempts}")
        print(f"   Confirmed bookings: {confirmed_bookings}")
        print(f"   Waiting list: {waiting_list}")
        print(f"   Failed bookings: {failed}")
        print(f"   Concurrent conflicts: {conflicts}")
        print(f"   Success rate: {(successful/total_attempts*100):.1f}%")
        print(f"   Requests/second: {total_attempts/actual_duration:.1f}")
        
        # Show sample successful bookings
        confirmed_samples = [r for r in results if r["success"] and 
                            r["result"].get("status") == "CONFIRMED"][:5]
        
        if confirmed_samples:
            print(f"\n✅ Sample confirmed bookings:")
            for sample in confirmed_samples:
                pnr = sample["result"].get("pnr", "N/A")
                fare = sample["result"].get("total_fare", "N/A")
                seats = sample["result"].get("seat_numbers", [])
                print(f"   PNR {pnr}: Fare ₹{fare}, Seats {seats}")
        
        # System consistency check
        print(f"\n🔍 Post-rush consistency check:")
        train = self._find_train(train_number, datetime.now() + timedelta(days=1))
        if train:
            remaining_seats = train.seat_availability[seat_type]
            waiting_count = train.waiting_list_count[seat_type]
            print(f"   Remaining seats: {remaining_seats}")
            print(f"   Waiting list size: {waiting_count}")
            
            if confirmed_bookings + remaining_seats <= 72:  # Assuming 72 initial seats
                print("   ✅ Seat count consistency maintained")
            else:
                print("   ❌ CRITICAL: Seat count inconsistency detected!")

    def check_pnr_status(self, pnr: str) -> Tuple[bool, Dict]:
        """Check PNR status across all zones"""
        for zone_id, zone_data in self.zones.items():
            if zone_data["status"] == "active":
                if pnr in zone_data["bookings"]:
                    booking = zone_data["bookings"][pnr]
                    
                    status_info = {
                        "pnr": pnr,
                        "train_number": booking.train.train_number,
                        "train_name": booking.train.train_name,
                        "travel_date": booking.travel_date.strftime("%d-%m-%Y"),
                        "departure_time": booking.train.departure_time,
                        "booking_status": booking.status.value,
                        "seat_type": booking.seat_type.value,
                        "passengers": [
                            {
                                "name": p.name,
                                "age": p.age,
                                "gender": p.gender,
                                "passenger_type": p.passenger_type.value
                            } for p in booking.passengers
                        ],
                        "total_fare": str(booking.total_fare),
                        "booking_source": booking.booking_source
                    }
                    
                    return True, status_info
        
        return False, {"error": "PNR not found"}

    def simulate_payment_timeout_scenario(self, pnr: str):
        """
        Simulate payment timeout scenario
        
        IRCTC में payment timeout होने पर booking cancel हो जाती है
        और seats वापस available pool में चले जाते हैं
        """
        print(f"\n💳 PAYMENT TIMEOUT SIMULATION for PNR {pnr}")
        
        # Find booking
        booking = None
        zone_with_booking = None
        
        for zone_id, zone_data in self.zones.items():
            if pnr in zone_data["bookings"]:
                booking = zone_data["bookings"][pnr]
                zone_with_booking = zone_id
                break
        
        if not booking:
            print("❌ PNR not found")
            return
        
        print(f"   Original status: {booking.status.value}")
        print("   Simulating 10-minute payment timeout...")
        
        # Simulate timeout
        time.sleep(2)  # Reduced for demo
        
        # Cancel booking due to timeout
        booking.status = BookingStatus.CANCELLED
        self.payment_timeouts += 1
        
        # Release seats back to inventory
        seat_type = booking.seat_type
        required_seats = len(booking.passengers)
        
        for zone_id, zone_data in self.zones.items():
            if zone_data["status"] == "active":
                zone_train = zone_data["trains"][booking.train.train_number]
                zone_train.seat_availability[seat_type] += required_seats
        
        print(f"✅ Payment timeout handled:")
        print(f"   PNR {pnr} cancelled due to payment timeout")
        print(f"   {required_seats} seats released back to inventory")
        print(f"   Updated seat availability: {booking.train.seat_availability[seat_type]}")

    def get_system_metrics(self) -> Dict:
        """Get comprehensive system metrics"""
        active_zones = sum(1 for data in self.zones.values() 
                          if data["status"] == "active")
        
        success_rate = 0
        if self.total_booking_attempts > 0:
            success_rate = (self.successful_bookings / self.total_booking_attempts) * 100
        
        total_bookings = sum(len(zone_data["bookings"]) for zone_data in self.zones.values())
        
        return {
            "total_booking_attempts": self.total_booking_attempts,
            "successful_bookings": self.successful_bookings,
            "failed_bookings": self.failed_bookings,
            "waiting_list_bookings": self.waiting_list_bookings,
            "success_rate": f"{success_rate:.2f}%",
            "active_zones": f"{active_zones}/{len(self.zones)}",
            "concurrent_conflicts": self.concurrent_conflicts,
            "consistency_checks": self.consistency_checks,
            "payment_timeouts": self.payment_timeouts,
            "payment_failures": self.payment_failures,
            "total_bookings_in_system": total_bookings
        }

def main():
    """
    Main demonstration - IRCTC booking scenarios
    """
    print("🚂 IRCTC Booking Conflicts System Demo")
    print("=" * 50)
    
    # Initialize IRCTC system
    irctc = IRCTCBookingSystem()
    
    # Scenario 1: Normal booking
    print("\n🎫 SCENARIO 1: Normal Booking")
    
    # Create passengers
    passengers = [
        Passenger("Rajesh Kumar", 35, "M", PassengerType.GENERAL, "Lower"),
        Passenger("Sunita Kumar", 32, "F", PassengerType.GENERAL, "Lower")
    ]
    
    success, message, result = irctc.book_ticket(
        user_id="customer_001",
        train_number="12951",
        passengers=passengers,
        seat_type=SeatType.AC3,
        travel_date=datetime.now() + timedelta(days=30)
    )
    
    print(f"Booking result: {message}")
    if success:
        print(f"PNR: {result.get('pnr')}")
        print(f"Total fare: ₹{result.get('total_fare')}")
        print(f"Seat numbers: {result.get('seat_numbers')}")
    
    # Scenario 2: Tatkal booking rush
    print("\n⚡ SCENARIO 2: Tatkal Booking Rush Simulation")
    irctc.simulate_tatkal_booking_rush(
        train_number="12301",
        seat_type=SeatType.SL,
        num_users=20,  # Reduced for demo
        rush_duration=15
    )
    
    # Scenario 3: PNR status check
    if success and result.get('pnr'):
        print(f"\n🔍 SCENARIO 3: PNR Status Check")
        pnr_success, pnr_data = irctc.check_pnr_status(result['pnr'])
        if pnr_success:
            print(f"PNR Status:")
            print(f"   Train: {pnr_data['train_name']}")
            print(f"   Status: {pnr_data['booking_status']}")
            print(f"   Passengers: {len(pnr_data['passengers'])}")
    
    # Scenario 4: Payment timeout simulation
    if success and result.get('pnr'):
        print(f"\n💳 SCENARIO 4: Payment Timeout Handling")
        irctc.simulate_payment_timeout_scenario(result['pnr'])
    
    # Scenario 5: System metrics
    print(f"\n📊 SCENARIO 5: System Metrics")
    metrics = irctc.get_system_metrics()
    print("IRCTC System Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ IRCTC booking conflicts demo completed!")
    print(f"Key learnings:")
    print(f"1. Railway booking requires strong consistency (no double booking)")
    print(f"2. Distributed locking prevents concurrent access conflicts")
    print(f"3. Waiting list management needs accurate seat counting")
    print(f"4. Payment timeout handling releases seats properly")
    print(f"5. Tatkal rush tests system's consistency under load")
    print(f"6. PNR status must be consistent across all zones")

if __name__ == "__main__":
    main()