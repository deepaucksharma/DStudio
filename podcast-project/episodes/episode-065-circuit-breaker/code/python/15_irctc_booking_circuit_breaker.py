#!/usr/bin/env python3
"""
IRCTC-style Train Booking Circuit Breaker
Indian Railway ticket booking system के लिए specialized circuit breaker

IRCTC में Tatkal booking, heavy load, और seasonal traffic patterns होते हैं
यह implementation railway booking की unique challenges handle करती है
"""

import time
import random
import threading
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
import uuid
import queue
from collections import defaultdict


class TrainClass(Enum):
    """Different train classes in Indian Railways"""
    SL = "sleeper"              # Sleeper Class
    AC_3A = "ac_3_tier"         # AC 3 Tier
    AC_2A = "ac_2_tier"         # AC 2 Tier
    AC_1A = "ac_1_tier"         # AC First Class
    CC = "chair_car"            # Chair Car
    EC = "executive_chair"      # Executive Chair Car
    FC = "first_class"          # First Class


class BookingType(Enum):
    """Types of bookings"""
    GENERAL = "general"         # General booking (normal)
    TATKAL = "tatkal"          # Tatkal booking (premium, 1 day advance)
    PREMIUM_TATKAL = "premium_tatkal"  # Premium Tatkal (higher price)
    LADIES_QUOTA = "ladies_quota"      # Ladies quota
    SENIOR_CITIZEN = "senior_citizen"  # Senior citizen quota
    PHYSICALLY_HANDICAPPED = "physically_handicapped"  # PH quota


class BookingStatus(Enum):
    """Booking status states"""
    CONFIRMED = "confirmed"     # Confirmed seat
    RAC = "rac"                # Reservation Against Cancellation
    WAITING = "waiting"         # Waiting list
    FAILED = "failed"          # Booking failed
    TIMEOUT = "timeout"         # Booking timed out


class IRCTCError(Enum):
    """Common IRCTC booking errors"""
    SERVER_TIMEOUT = "server_timeout"
    PAYMENT_GATEWAY_FAILURE = "payment_gateway_failure"
    SEAT_NOT_AVAILABLE = "seat_not_available"
    TATKAL_TIME_NOT_STARTED = "tatkal_booking_not_started"
    QUOTA_EXHAUSTED = "quota_seats_exhausted"
    BERTH_NOT_AVAILABLE = "preferred_berth_not_available"
    TRAIN_CANCELLED = "train_cancelled_by_railway"
    CHART_PREPARED = "chart_already_prepared"
    INVALID_PASSENGER_DETAILS = "invalid_passenger_details"
    WAITING_LIST_FULL = "waiting_list_full"
    MULTIPLE_BOOKING_ATTEMPT = "multiple_booking_for_same_journey"
    SYSTEM_UNDER_MAINTENANCE = "system_under_maintenance"


@dataclass
class TrainInfo:
    """Train information"""
    train_number: str
    train_name: str
    source_station: str
    destination_station: str
    departure_time: str
    arrival_time: str
    journey_date: date
    available_classes: List[TrainClass]


@dataclass
class PassengerInfo:
    """Passenger details"""
    name: str
    age: int
    gender: str  # M/F/T
    berth_preference: Optional[str] = None  # UB/MB/LB/SU/SL


@dataclass
class BookingRequest:
    """IRCTC booking request"""
    booking_id: str
    train_info: TrainInfo
    train_class: TrainClass
    booking_type: BookingType
    passengers: List[PassengerInfo]
    user_id: str
    mobile_number: str
    payment_method: str = "UPI"
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BookingResponse:
    """IRCTC booking response"""
    booking_id: str
    pnr_number: Optional[str] = None
    status: BookingStatus = BookingStatus.FAILED
    confirmed_seats: List[str] = field(default_factory=list)
    rac_seats: List[str] = field(default_factory=list)
    waiting_list_numbers: List[int] = field(default_factory=list)
    fare_amount: float = 0.0
    booking_time: datetime = field(default_factory=datetime.now)
    error_message: Optional[str] = None
    chart_status: str = "Not Prepared"


class IRCTCCircuitBreakerConfig:
    """IRCTC specific circuit breaker configuration"""
    
    def __init__(self):
        # Basic circuit breaker settings
        self.failure_threshold = 10
        self.success_threshold = 5
        self.timeout_seconds = 30.0
        
        # IRCTC specific settings
        self.tatkal_booking_start_time = "10:00"  # Tatkal starts at 10 AM
        self.premium_tatkal_start_time = "10:15"  # Premium Tatkal starts at 10:15 AM
        self.chart_preparation_time = "04:00"     # Charts prepared at 4 AM
        
        # Load multipliers for different scenarios
        self.tatkal_rush_multiplier = 5.0         # Tatkal time high load
        self.holiday_season_multiplier = 3.0      # Diwali, Holi, Summer holidays
        self.weekend_multiplier = 2.0             # Friday/Saturday bookings
        self.exam_season_multiplier = 2.5         # Student travel during exams
        
        # Quota-wise seat availability (approximate)
        self.quota_availability = {
            BookingType.GENERAL: 0.7,              # 70% seats in general quota
            BookingType.TATKAL: 0.1,               # 10% for Tatkal
            BookingType.PREMIUM_TATKAL: 0.05,      # 5% for Premium Tatkal
            BookingType.LADIES_QUOTA: 0.1,         # 10% for ladies
            BookingType.SENIOR_CITIZEN: 0.03,      # 3% for senior citizens
            BookingType.PHYSICALLY_HANDICAPPED: 0.02  # 2% for PH quota
        }
        
        # Class-wise demand patterns
        self.class_demand = {
            TrainClass.SL: 0.6,      # Highest demand
            TrainClass.AC_3A: 0.25,  # Second highest
            TrainClass.AC_2A: 0.1,   # Moderate demand
            TrainClass.CC: 0.04,     # Low demand
            TrainClass.AC_1A: 0.005, # Very low demand
            TrainClass.EC: 0.003,    # Very low demand
            TrainClass.FC: 0.002     # Lowest demand
        }


class IRCTCCircuitBreaker:
    """
    IRCTC-style Train Booking Circuit Breaker
    Indian Railway booking system की complexity और load patterns handle करता है
    """
    
    def __init__(self, config: IRCTCCircuitBreakerConfig):
        self.config = config
        
        # Circuit states per booking type and class combination
        self.circuit_states: Dict[str, str] = {}  # key = f"{booking_type}_{train_class}"
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}
        self.last_failure_times: Dict[str, float] = {}
        
        # Booking metrics and patterns
        self.booking_metrics: Dict[str, Dict] = {}
        self.active_bookings: Dict[str, int] = {}  # Current active booking attempts
        
        # IRCTC specific tracking
        self.quota_utilization: Dict[BookingType, float] = {}
        self.peak_hour_multiplier = 1.0
        self.is_tatkal_time = False
        self.is_holiday_season = False
        
        # Seat availability simulation (per train-class combination)
        self.seat_availability: Dict[str, Dict[TrainClass, int]] = defaultdict(
            lambda: {cls: random.randint(50, 300) for cls in TrainClass}
        )
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Booking queue for high-load scenarios
        self.booking_queue = queue.PriorityQueue(maxsize=10000)
        
        # Initialize circuits
        self._initialize_circuits()
        
        print("🚂 IRCTC Train Booking Circuit Breaker initialized")
        print(f"   - Supporting {len(BookingType)} booking types")
        print(f"   - Supporting {len(TrainClass)} train classes")
        print(f"   - Total circuits: {len(self.circuit_states)}")
    
    def _initialize_circuits(self):
        """Initialize circuit breaker for each booking type and class combination"""
        for booking_type in BookingType:
            for train_class in TrainClass:
                circuit_key = f"{booking_type.value}_{train_class.value}"
                
                self.circuit_states[circuit_key] = "CLOSED"
                self.failure_counts[circuit_key] = 0
                self.success_counts[circuit_key] = 0
                self.last_failure_times[circuit_key] = 0
                self.active_bookings[circuit_key] = 0
                
                self.booking_metrics[circuit_key] = {
                    "total_bookings": 0,
                    "successful_bookings": 0,
                    "failed_bookings": 0,
                    "avg_booking_time": 0.0,
                    "confirmed_bookings": 0,
                    "rac_bookings": 0,
                    "waiting_list_bookings": 0,
                    "tatkal_success_rate": 0.0
                }
        
        # Initialize quota utilization
        for booking_type in BookingType:
            self.quota_utilization[booking_type] = 0.0
    
    def book_ticket(self, request: BookingRequest) -> BookingResponse:
        """
        Process train ticket booking through circuit breaker
        """
        circuit_key = f"{request.booking_type.value}_{request.train_class.value}"
        start_time = time.time()
        
        # Check current load conditions
        self._update_load_conditions()
        
        with self._lock:
            # Check if booking should be rejected
            rejection_reason = self._should_reject_booking(circuit_key, request)
            if rejection_reason:
                return self._create_failure_response(request, rejection_reason)
            
            # Check capacity limits
            max_concurrent = self._get_max_concurrent_bookings(circuit_key)
            if self.active_bookings[circuit_key] >= max_concurrent:
                return self._create_failure_response(
                    request,
                    "System overloaded. Please try again in a few minutes."
                )
            
            # Track active booking
            self.active_bookings[circuit_key] += 1
        
        try:
            # Process booking
            response = self._process_booking_internal(request, circuit_key)
            
            # Record success/failure
            booking_time = time.time() - start_time
            if response.status in [BookingStatus.CONFIRMED, BookingStatus.RAC, BookingStatus.WAITING]:
                self._record_success(circuit_key, response, booking_time)
            else:
                self._record_failure(circuit_key, response.error_message or "Unknown error", booking_time)
            
            return response
        
        except Exception as e:
            booking_time = time.time() - start_time
            self._record_failure(circuit_key, str(e), booking_time)
            return self._create_failure_response(request, str(e))
        
        finally:
            with self._lock:
                self.active_bookings[circuit_key] -= 1
    
    def _should_reject_booking(self, circuit_key: str, request: BookingRequest) -> Optional[str]:
        """Check if booking should be rejected"""
        state = self.circuit_states[circuit_key]
        
        if state == "CLOSED":
            # Check Tatkal timing restrictions
            if request.booking_type in [BookingType.TATKAL, BookingType.PREMIUM_TATKAL]:
                if not self._is_tatkal_time_valid(request):
                    return "Tatkal booking not yet started for this journey date"
            
            return None
        
        if state == "OPEN":
            # Check if recovery timeout has passed
            last_failure = self.last_failure_times[circuit_key]
            if time.time() - last_failure >= self.config.timeout_seconds:
                self.circuit_states[circuit_key] = "HALF_OPEN"
                self.success_counts[circuit_key] = 0
                print(f"🟡 Circuit {circuit_key} moved to HALF_OPEN")
                return None
            return f"Booking service temporarily unavailable for {circuit_key.replace('_', ' ').title()}"
        
        # HALF_OPEN state - allow limited bookings
        return None
    
    def _is_tatkal_time_valid(self, request: BookingRequest) -> bool:
        """Check if Tatkal booking time is valid"""
        current_time = datetime.now()
        journey_date = request.train_info.journey_date
        
        # Tatkal opens 1 day before journey (excluding journey date)
        tatkal_date = journey_date - timedelta(days=1)
        
        if current_time.date() != tatkal_date:
            return False
        
        # Check time constraints
        current_time_str = current_time.strftime("%H:%M")
        
        if request.booking_type == BookingType.TATKAL:
            return current_time_str >= self.config.tatkal_booking_start_time
        elif request.booking_type == BookingType.PREMIUM_TATKAL:
            return current_time_str >= self.config.premium_tatkal_start_time
        
        return True
    
    def _get_max_concurrent_bookings(self, circuit_key: str) -> int:
        """Get maximum concurrent bookings allowed"""
        base_limit = 50  # Base concurrent booking limit
        
        # Apply load multipliers
        adjusted_limit = base_limit * self.peak_hour_multiplier
        
        # Booking type specific adjustments
        if "tatkal" in circuit_key:
            adjusted_limit *= 0.5  # Reduce limit for Tatkal due to high contention
        
        return max(1, int(adjusted_limit))
    
    def _update_load_conditions(self):
        """Update load conditions based on time and season"""
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Reset multiplier
        self.peak_hour_multiplier = 1.0
        
        # Tatkal rush hour (10 AM - 11 AM)
        if 10 <= current_hour <= 11:
            self.is_tatkal_time = True
            self.peak_hour_multiplier *= self.config.tatkal_rush_multiplier
        else:
            self.is_tatkal_time = False
        
        # Weekend booking rush (Friday evening, Saturday morning)
        if ((current_time.weekday() == 4 and current_hour >= 18) or  # Friday evening
            (current_time.weekday() == 5 and current_hour <= 12)):   # Saturday morning
            self.peak_hour_multiplier *= self.config.weekend_multiplier
        
        # Holiday season detection (approximate)
        month = current_time.month
        if month in [4, 5, 10, 11, 12]:  # Summer holidays, Diwali, Christmas
            self.is_holiday_season = True
            self.peak_hour_multiplier *= self.config.holiday_season_multiplier
        else:
            self.is_holiday_season = False
        
        # Exam season (March-April, May-June)
        if month in [3, 4, 5, 6]:
            self.peak_hour_multiplier *= self.config.exam_season_multiplier
    
    def _process_booking_internal(self, request: BookingRequest, circuit_key: str) -> BookingResponse:
        """
        Internal booking processing simulation
        """
        train_key = f"{request.train_info.train_number}_{request.train_info.journey_date}"
        
        # Simulate booking processing time
        processing_time = self._get_processing_time(request.booking_type, request.train_class)
        time.sleep(processing_time)
        
        # Check seat availability
        available_seats = self.seat_availability[train_key][request.train_class]
        quota_seats = int(available_seats * self.config.quota_availability[request.booking_type])
        
        # Calculate booking probability based on various factors
        booking_success_probability = self._calculate_booking_success_probability(
            request, available_seats, quota_seats
        )
        
        # Generate booking result
        if random.random() > booking_success_probability:
            # Booking failed
            error = self._generate_realistic_booking_error(request, available_seats)
            return BookingResponse(
                booking_id=request.booking_id,
                status=BookingStatus.FAILED,
                error_message=error.value,
                booking_time=datetime.now()
            )
        
        # Booking successful - determine confirmation status
        return self._generate_successful_booking(request, available_seats, quota_seats, train_key)
    
    def _get_processing_time(self, booking_type: BookingType, train_class: TrainClass) -> float:
        """Get realistic processing time based on booking type and class"""
        base_times = {
            BookingType.GENERAL: 3.0,
            BookingType.TATKAL: 8.0,        # Tatkal takes longer due to high load
            BookingType.PREMIUM_TATKAL: 6.0,
            BookingType.LADIES_QUOTA: 4.0,
            BookingType.SENIOR_CITIZEN: 5.0,
            BookingType.PHYSICALLY_HANDICAPPED: 5.0
        }
        
        class_factors = {
            TrainClass.SL: 1.0,
            TrainClass.AC_3A: 1.1,
            TrainClass.AC_2A: 1.2,
            TrainClass.AC_1A: 1.3,
            TrainClass.CC: 0.8,
            TrainClass.EC: 1.4,
            TrainClass.FC: 1.5
        }
        
        base_time = base_times.get(booking_type, 4.0)
        class_factor = class_factors.get(train_class, 1.0)
        load_factor = self.peak_hour_multiplier * 0.3  # Load affects processing time
        
        # Add random jitter
        jitter = random.uniform(0.5, 2.0)
        
        total_time = base_time * class_factor * (1 + load_factor) + jitter
        return max(1.0, total_time)
    
    def _calculate_booking_success_probability(
        self, 
        request: BookingRequest, 
        available_seats: int, 
        quota_seats: int
    ) -> float:
        """Calculate probability of booking success"""
        # Base success rate
        if quota_seats <= 0:
            return 0.1  # Very low chance if quota exhausted
        
        # Demand vs availability ratio
        demand_factor = self.config.class_demand[request.train_class]
        availability_ratio = quota_seats / (available_seats * demand_factor + 1)
        
        # Booking type specific success rates
        type_success_rates = {
            BookingType.GENERAL: 0.7,
            BookingType.TATKAL: 0.3,        # Very competitive
            BookingType.PREMIUM_TATKAL: 0.5,
            BookingType.LADIES_QUOTA: 0.8,
            BookingType.SENIOR_CITIZEN: 0.9,
            BookingType.PHYSICALLY_HANDICAPPED: 0.95
        }
        
        base_success = type_success_rates.get(request.booking_type, 0.7)
        
        # Time-based factors
        time_factor = 1.0
        if self.is_tatkal_time and request.booking_type in [BookingType.TATKAL, BookingType.PREMIUM_TATKAL]:
            time_factor = 0.6  # Much harder during Tatkal rush
        
        # Load-based reduction
        load_factor = 1.0 / max(1.0, self.peak_hour_multiplier * 0.5)
        
        final_probability = base_success * availability_ratio * time_factor * load_factor
        return min(0.95, max(0.05, final_probability))
    
    def _generate_realistic_booking_error(self, request: BookingRequest, available_seats: int) -> IRCTCError:
        """Generate realistic booking errors based on context"""
        if self.is_tatkal_time and request.booking_type not in [BookingType.TATKAL, BookingType.PREMIUM_TATKAL]:
            if random.random() < 0.3:
                return IRCTCError.SERVER_TIMEOUT
        
        if available_seats <= 0:
            return IRCTCError.SEAT_NOT_AVAILABLE
        
        if request.booking_type in [BookingType.TATKAL, BookingType.PREMIUM_TATKAL]:
            tatkal_errors = [
                IRCTCError.SERVER_TIMEOUT,
                IRCTCError.QUOTA_EXHAUSTED,
                IRCTCError.MULTIPLE_BOOKING_ATTEMPT,
                IRCTCError.PAYMENT_GATEWAY_FAILURE
            ]
            return random.choice(tatkal_errors)
        
        # General booking errors
        general_errors = [
            IRCTCError.SEAT_NOT_AVAILABLE,
            IRCTCError.BERTH_NOT_AVAILABLE,
            IRCTCError.QUOTA_EXHAUSTED,
            IRCTCError.PAYMENT_GATEWAY_FAILURE,
            IRCTCError.INVALID_PASSENGER_DETAILS,
            IRCTCError.WAITING_LIST_FULL
        ]
        
        return random.choice(general_errors)
    
    def _generate_successful_booking(
        self, 
        request: BookingRequest, 
        available_seats: int, 
        quota_seats: int,
        train_key: str
    ) -> BookingResponse:
        """Generate successful booking response with realistic seat allocation"""
        passenger_count = len(request.passengers)
        
        # Determine booking status based on availability
        if quota_seats >= passenger_count:
            # Confirmed booking
            status = BookingStatus.CONFIRMED
            confirmed_seats = [f"S{i+1}" for i in range(passenger_count)]
            fare = self._calculate_fare(request.train_class, passenger_count, request.booking_type)
            
            # Update seat availability
            self.seat_availability[train_key][request.train_class] -= passenger_count
            
        elif quota_seats > 0:
            # Partial confirmation + RAC
            status = BookingStatus.RAC
            confirmed_seats = [f"S{i+1}" for i in range(quota_seats)]
            rac_seats = [f"RAC{i+1}" for i in range(passenger_count - quota_seats)]
            fare = self._calculate_fare(request.train_class, passenger_count, request.booking_type)
            
        else:
            # Waiting list
            status = BookingStatus.WAITING
            waiting_numbers = list(range(1, passenger_count + 1))
            fare = self._calculate_fare(request.train_class, passenger_count, request.booking_type)
        
        # Generate PNR
        pnr = f"{random.randint(1000000000, 9999999999)}"
        
        return BookingResponse(
            booking_id=request.booking_id,
            pnr_number=pnr,
            status=status,
            confirmed_seats=confirmed_seats if status == BookingStatus.CONFIRMED else [],
            rac_seats=rac_seats if status == BookingStatus.RAC else [],
            waiting_list_numbers=waiting_numbers if status == BookingStatus.WAITING else [],
            fare_amount=fare,
            booking_time=datetime.now(),
            chart_status="Not Prepared"
        )
    
    def _calculate_fare(self, train_class: TrainClass, passenger_count: int, booking_type: BookingType) -> float:
        """Calculate train fare (simplified)"""
        base_fares = {
            TrainClass.SL: 300,
            TrainClass.AC_3A: 800,
            TrainClass.AC_2A: 1200,
            TrainClass.AC_1A: 2000,
            TrainClass.CC: 400,
            TrainClass.EC: 600,
            TrainClass.FC: 500
        }
        
        base_fare = base_fares.get(train_class, 400)
        
        # Tatkal surcharge
        if booking_type == BookingType.TATKAL:
            base_fare *= 1.3  # 30% surcharge
        elif booking_type == BookingType.PREMIUM_TATKAL:
            base_fare *= 1.5  # 50% surcharge
        
        return base_fare * passenger_count
    
    def _create_failure_response(self, request: BookingRequest, error_message: str) -> BookingResponse:
        """Create failure response"""
        return BookingResponse(
            booking_id=request.booking_id,
            status=BookingStatus.FAILED,
            error_message=error_message,
            booking_time=datetime.now()
        )
    
    def _record_success(self, circuit_key: str, response: BookingResponse, booking_time: float):
        """Record successful booking"""
        with self._lock:
            metrics = self.booking_metrics[circuit_key]
            metrics["total_bookings"] += 1
            metrics["successful_bookings"] += 1
            
            # Update booking status specific metrics
            if response.status == BookingStatus.CONFIRMED:
                metrics["confirmed_bookings"] += 1
            elif response.status == BookingStatus.RAC:
                metrics["rac_bookings"] += 1
            elif response.status == BookingStatus.WAITING:
                metrics["waiting_list_bookings"] += 1
            
            # Update average booking time
            total_bookings = metrics["total_bookings"]
            old_avg = metrics["avg_booking_time"]
            metrics["avg_booking_time"] = ((old_avg * (total_bookings - 1)) + booking_time) / total_bookings
            
            # Update Tatkal success rate if applicable
            if "tatkal" in circuit_key and response.status == BookingStatus.CONFIRMED:
                tatkal_bookings = metrics["confirmed_bookings"] + metrics["rac_bookings"]
                metrics["tatkal_success_rate"] = (metrics["confirmed_bookings"] / max(tatkal_bookings, 1)) * 100
            
            # Circuit state management
            state = self.circuit_states[circuit_key]
            if state == "HALF_OPEN":
                self.success_counts[circuit_key] += 1
                if self.success_counts[circuit_key] >= self.config.success_threshold:
                    self.circuit_states[circuit_key] = "CLOSED"
                    self.failure_counts[circuit_key] = 0
                    print(f"✅ Circuit {circuit_key} CLOSED - Booking service recovered")
            elif state == "CLOSED":
                self.failure_counts[circuit_key] = 0
    
    def _record_failure(self, circuit_key: str, error: str, booking_time: float):
        """Record booking failure"""
        with self._lock:
            metrics = self.booking_metrics[circuit_key]
            metrics["total_bookings"] += 1
            metrics["failed_bookings"] += 1
            
            self.failure_counts[circuit_key] += 1
            self.last_failure_times[circuit_key] = time.time()
            
            # Circuit state management
            state = self.circuit_states[circuit_key]
            adjusted_threshold = max(
                self.config.failure_threshold // int(self.peak_hour_multiplier), 
                5
            )
            
            if state == "CLOSED" and self.failure_counts[circuit_key] >= adjusted_threshold:
                self.circuit_states[circuit_key] = "OPEN"
                print(f"🔴 Circuit {circuit_key} OPENED - {error}")
            elif state == "HALF_OPEN":
                self.circuit_states[circuit_key] = "OPEN"
                self.success_counts[circuit_key] = 0
                print(f"🔴 Circuit {circuit_key} back to OPEN - {error}")
    
    def get_booking_system_status(self) -> Dict[str, Any]:
        """Get comprehensive booking system status"""
        total_circuits = len(self.circuit_states)
        healthy_circuits = sum(1 for state in self.circuit_states.values() if state == "CLOSED")
        degraded_circuits = sum(1 for state in self.circuit_states.values() if state == "HALF_OPEN")
        failed_circuits = sum(1 for state in self.circuit_states.values() if state == "OPEN")
        
        # Calculate booking statistics
        booking_stats = {
            "by_type": defaultdict(lambda: {"total": 0, "successful": 0, "confirmed": 0}),
            "by_class": defaultdict(lambda: {"total": 0, "successful": 0, "confirmed": 0})
        }
        
        for circuit_key, metrics in self.booking_metrics.items():
            booking_type, train_class = circuit_key.split('_', 1)
            
            booking_stats["by_type"][booking_type]["total"] += metrics["total_bookings"]
            booking_stats["by_type"][booking_type]["successful"] += metrics["successful_bookings"] 
            booking_stats["by_type"][booking_type]["confirmed"] += metrics["confirmed_bookings"]
            
            booking_stats["by_class"][train_class]["total"] += metrics["total_bookings"]
            booking_stats["by_class"][train_class]["successful"] += metrics["successful_bookings"]
            booking_stats["by_class"][train_class]["confirmed"] += metrics["confirmed_bookings"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": {
                "total_circuits": total_circuits,
                "healthy_circuits": healthy_circuits,
                "degraded_circuits": degraded_circuits,
                "failed_circuits": failed_circuits,
                "overall_health_percentage": (healthy_circuits / total_circuits) * 100
            },
            "load_conditions": {
                "peak_hour_multiplier": self.peak_hour_multiplier,
                "is_tatkal_time": self.is_tatkal_time,
                "is_holiday_season": self.is_holiday_season,
                "current_time": datetime.now().strftime("%H:%M")
            },
            "booking_statistics": dict(booking_stats),
            "top_performing_routes": self._get_top_performing_circuits(),
            "system_alerts": self._get_system_alerts(),
            "recommendations": self._get_irctc_recommendations()
        }
    
    def _get_top_performing_circuits(self) -> List[Dict[str, Any]]:
        """Get best and worst performing circuits"""
        performing_circuits = []
        
        for circuit_key, metrics in self.booking_metrics.items():
            if metrics["total_bookings"] >= 10:
                success_rate = (metrics["successful_bookings"] / metrics["total_bookings"]) * 100
                confirmation_rate = (metrics["confirmed_bookings"] / max(metrics["successful_bookings"], 1)) * 100
                
                performing_circuits.append({
                    "circuit": circuit_key.replace('_', ' ').title(),
                    "success_rate": round(success_rate, 1),
                    "confirmation_rate": round(confirmation_rate, 1),
                    "avg_booking_time": round(metrics["avg_booking_time"], 2),
                    "total_bookings": metrics["total_bookings"],
                    "state": self.circuit_states[circuit_key]
                })
        
        # Sort by success rate
        performing_circuits.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return {
            "best_performing": performing_circuits[:3],
            "worst_performing": performing_circuits[-3:] if len(performing_circuits) > 3 else []
        }
    
    def _get_system_alerts(self) -> List[str]:
        """Get system alerts and warnings"""
        alerts = []
        
        failed_circuits = sum(1 for state in self.circuit_states.values() if state == "OPEN")
        total_circuits = len(self.circuit_states)
        
        if failed_circuits > total_circuits * 0.3:
            alerts.append("🚨 High circuit failure rate - Consider system maintenance")
        
        if self.is_tatkal_time:
            alerts.append("⚡ Tatkal booking rush hour - Expect high load and timeouts")
        
        if self.peak_hour_multiplier > 3.0:
            alerts.append("📈 Extremely high load detected - Consider additional server capacity")
        
        if self.is_holiday_season:
            alerts.append("🎊 Holiday season traffic - Monitor seat availability closely")
        
        # Check for specific booking type failures
        for booking_type in [BookingType.TATKAL, BookingType.PREMIUM_TATKAL]:
            tatkal_circuits = [k for k in self.circuit_states.keys() if booking_type.value in k]
            failed_tatkal = sum(1 for k in tatkal_circuits if self.circuit_states[k] == "OPEN")
            
            if failed_tatkal > len(tatkal_circuits) * 0.5:
                alerts.append(f"⚠️  {booking_type.value.title()} bookings severely impacted")
        
        return alerts
    
    def _get_irctc_recommendations(self) -> List[str]:
        """Get IRCTC specific recommendations"""
        recommendations = []
        
        if self.is_tatkal_time:
            recommendations.append("🎯 Enable Tatkal-specific rate limiting and queuing")
            recommendations.append("💾 Use cached seat availability data for faster responses")
        
        if self.peak_hour_multiplier > 2.0:
            recommendations.append("🔄 Implement request queuing for high-demand bookings")
            recommendations.append("📱 Show expected wait times to users")
        
        if self.is_holiday_season:
            recommendations.append("🚆 Consider increasing train frequency on popular routes")
            recommendations.append("📊 Provide real-time seat availability dashboards")
        
        # Performance-based recommendations
        avg_booking_time = sum(
            m["avg_booking_time"] for m in self.booking_metrics.values() 
            if m["total_bookings"] > 0
        ) / len([m for m in self.booking_metrics.values() if m["total_bookings"] > 0])
        
        if avg_booking_time > 10.0:
            recommendations.append("⚡ Optimize booking processing pipeline - Average time too high")
        
        return recommendations


def test_irctc_circuit_breaker():
    """Test IRCTC booking circuit breaker with realistic scenarios"""
    print("🧪 Testing IRCTC Train Booking Circuit Breaker")
    print("=" * 70)
    
    # Create IRCTC circuit breaker
    config = IRCTCCircuitBreakerConfig()
    icb = IRCTCCircuitBreaker(config)
    
    # Simulate Tatkal time for testing
    icb.is_tatkal_time = True
    icb._update_load_conditions()
    
    print("\n📊 Phase 1: General booking simulation")
    print("-" * 60)
    
    # Create sample train
    train = TrainInfo(
        train_number="12301",
        train_name="Howrah Rajdhani Express",
        source_station="NDLS",
        destination_station="HWH", 
        departure_time="17:00",
        arrival_time="10:00+1",
        journey_date=date.today() + timedelta(days=1),
        available_classes=[TrainClass.AC_1A, TrainClass.AC_2A, TrainClass.AC_3A]
    )
    
    # Sample passengers
    passengers = [
        PassengerInfo("Rahul Kumar", 28, "M", "LB"),
        PassengerInfo("Priya Singh", 25, "F", "UB")
    ]
    
    # Test different booking scenarios
    booking_scenarios = [
        (BookingType.GENERAL, TrainClass.AC_3A),
        (BookingType.GENERAL, TrainClass.AC_2A),
        (BookingType.LADIES_QUOTA, TrainClass.AC_3A),
        (BookingType.SENIOR_CITIZEN, TrainClass.AC_2A),
        (BookingType.TATKAL, TrainClass.AC_3A),
        (BookingType.PREMIUM_TATKAL, TrainClass.AC_2A)
    ]
    
    for booking_type, train_class in booking_scenarios:
        for attempt in range(3):  # 3 attempts each
            booking_request = BookingRequest(
                booking_id=f"BK_{booking_type.value}_{attempt+1}",
                train_info=train,
                train_class=train_class,
                booking_type=booking_type,
                passengers=passengers,
                user_id=f"user_{random.randint(1000, 9999)}",
                mobile_number=f"98765{random.randint(10000, 99999)}"
            )
            
            response = icb.book_ticket(booking_request)
            
            status_emoji = {
                BookingStatus.CONFIRMED: "✅",
                BookingStatus.RAC: "🟡", 
                BookingStatus.WAITING: "🟠",
                BookingStatus.FAILED: "❌",
                BookingStatus.TIMEOUT: "⏰"
            }.get(response.status, "❓")
            
            print(f"{status_emoji} {booking_type.value.upper()} {train_class.value.upper()}: "
                  f"{response.status.value.upper()}")
            
            if response.pnr_number:
                print(f"   PNR: {response.pnr_number}, Fare: ₹{response.fare_amount}")
            elif response.error_message:
                print(f"   Error: {response.error_message}")
            
            time.sleep(0.5)
    
    print("\n📊 Phase 2: Tatkal booking rush simulation")
    print("-" * 60)
    
    # Simulate Tatkal booking rush at 10:00 AM
    tatkal_requests = []
    for i in range(20):
        booking_type = random.choice([BookingType.TATKAL, BookingType.PREMIUM_TATKAL])
        train_class = random.choice([TrainClass.SL, TrainClass.AC_3A, TrainClass.AC_2A])
        
        request = BookingRequest(
            booking_id=f"TATKAL_{i+1:03d}",
            train_info=train,
            train_class=train_class,
            booking_type=booking_type,
            passengers=[PassengerInfo(f"Passenger_{i+1}", 30, "M")],
            user_id=f"tatkal_user_{i+1}",
            mobile_number=f"90000{i+10000:05d}"
        )
        
        tatkal_requests.append(request)
    
    # Process Tatkal requests concurrently (simulate rush)
    import concurrent.futures
    
    def process_tatkal_booking(request):
        response = icb.book_ticket(request)
        return request.booking_id, response.status, response.pnr_number
    
    successful_tatkal = 0
    failed_tatkal = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(process_tatkal_booking, req) for req in tatkal_requests]
        
        for future in concurrent.futures.as_completed(futures):
            booking_id, status, pnr = future.result()
            
            if status in [BookingStatus.CONFIRMED, BookingStatus.RAC]:
                successful_tatkal += 1
                print(f"✅ {booking_id}: {status.value.upper()} - PNR: {pnr}")
            else:
                failed_tatkal += 1
                print(f"❌ {booking_id}: {status.value.upper()}")
    
    print(f"\n🎯 Tatkal Rush Results:")
    print(f"   Successful: {successful_tatkal}")
    print(f"   Failed: {failed_tatkal}")
    print(f"   Success Rate: {(successful_tatkal/(successful_tatkal+failed_tatkal)*100):.1f}%")
    
    print("\n📊 Phase 3: Holiday season load test")
    print("-" * 60)
    
    # Simulate holiday season booking
    icb.is_holiday_season = True
    icb._update_load_conditions()
    
    popular_routes = [
        ("12301", "Howrah Rajdhani", "NDLS", "HWH"),
        ("12002", "Shatabdi Express", "NDLS", "KLK"),
        ("12617", "Mangala Express", "NDLS", "MAO"),
        ("22691", "Rajdhani Express", "NDLS", "BPL")
    ]
    
    holiday_bookings = 0
    holiday_confirmations = 0
    
    for train_num, train_name, src, dest in popular_routes:
        holiday_train = TrainInfo(
            train_number=train_num,
            train_name=train_name,
            source_station=src,
            destination_station=dest,
            departure_time="18:00",
            arrival_time="08:00+1",
            journey_date=date.today() + timedelta(days=15),  # Holiday booking
            available_classes=[TrainClass.SL, TrainClass.AC_3A, TrainClass.AC_2A]
        )
        
        for i in range(5):  # 5 bookings per route
            request = BookingRequest(
                booking_id=f"HOLIDAY_{train_num}_{i+1}",
                train_info=holiday_train,
                train_class=random.choice([TrainClass.SL, TrainClass.AC_3A]),
                booking_type=BookingType.GENERAL,
                passengers=[PassengerInfo(f"Holiday_Traveler_{i+1}", 35, "M")],
                user_id=f"holiday_user_{i+1}",
                mobile_number=f"95000{i+10000:05d}"
            )
            
            response = icb.book_ticket(request)
            holiday_bookings += 1
            
            if response.status == BookingStatus.CONFIRMED:
                holiday_confirmations += 1
                print(f"✅ Holiday booking {train_num}: CONFIRMED")
            else:
                print(f"❌ Holiday booking {train_num}: {response.status.value.upper()}")
            
            time.sleep(0.3)
    
    print(f"\n🎊 Holiday Season Results:")
    print(f"   Total Bookings: {holiday_bookings}")
    print(f"   Confirmations: {holiday_confirmations}")
    print(f"   Confirmation Rate: {(holiday_confirmations/holiday_bookings*100):.1f}%")
    
    print("\n📈 Final System Status Report:")
    print("=" * 60)
    
    status_report = icb.get_booking_system_status()
    
    print("🏥 System Health:")
    health = status_report["system_health"]
    print(f"   Overall Health: {health['overall_health_percentage']:.1f}%")
    print(f"   Healthy Circuits: {health['healthy_circuits']}/{health['total_circuits']}")
    print(f"   Failed Circuits: {health['failed_circuits']}")
    
    print("\n📊 Booking Performance:")
    stats = status_report["booking_statistics"]
    
    print("   By Booking Type:")
    for booking_type, data in stats["by_type"].items():
        if data["total"] > 0:
            success_rate = (data["successful"] / data["total"]) * 100
            print(f"     {booking_type.upper()}: {success_rate:.1f}% success ({data['confirmed']} confirmed)")
    
    print("\n   By Train Class:")
    for train_class, data in stats["by_class"].items():
        if data["total"] > 0:
            success_rate = (data["successful"] / data["total"]) * 100
            print(f"     {train_class.upper()}: {success_rate:.1f}% success ({data['confirmed']} confirmed)")
    
    if status_report["system_alerts"]:
        print("\n⚠️  System Alerts:")
        for alert in status_report["system_alerts"]:
            print(f"   {alert}")
    
    if status_report["recommendations"]:
        print("\n💡 IRCTC Recommendations:")
        for rec in status_report["recommendations"]:
            print(f"   {rec}")
    
    print("\n🚂 Indian Railway Insights:")
    print("   - Tatkal bookings have 30% success rate due to high demand")
    print("   - AC 3 Tier has highest demand, followed by Sleeper Class")
    print("   - Holiday seasons see 3x normal traffic with more waiting lists")
    print("   - Ladies and Senior Citizen quotas have higher confirmation rates")
    print("   - Premium Tatkal offers better chances than regular Tatkal")
    print("   - Early morning bookings (4-6 AM) have better success rates")


if __name__ == "__main__":
    test_irctc_circuit_breaker()