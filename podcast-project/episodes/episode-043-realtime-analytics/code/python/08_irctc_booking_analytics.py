#!/usr/bin/env python3
"""
IRCTC Real-time Booking Analytics
Episode 43: Real-time Analytics at Scale

यह example IRCTC का real-time booking analytics दिखाता है
Tatkal booking के दौरान massive concurrent load और booking patterns को track करता है।

Real Production Stats:
- IRCTC: 12 lakh tickets booked daily
- Peak booking rate: 5000+ tickets/minute (Tatkal time)
- Concurrent users: 50,000+ during peak hours
- Payment success rate tracking: Critical for revenue
"""

import asyncio
import json
import time
import random
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from enum import Enum
import logging

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookingStatus(Enum):
    INITIATED = "INITIATED"
    SEAT_SELECTED = "SEAT_SELECTED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    WAITLISTED = "WAITLISTED"

class TrainClass(Enum):
    SL = "Sleeper"
    AC3 = "AC 3 Tier"
    AC2 = "AC 2 Tier" 
    AC1 = "AC First Class"
    CC = "Chair Car"
    EC = "Executive Chair"

@dataclass
class BookingAttempt:
    """Individual booking attempt"""
    booking_id: str
    user_id: str
    train_number: str
    train_name: str
    journey_date: str
    from_station: str
    to_station: str
    passenger_count: int
    train_class: TrainClass
    fare_amount: float
    booking_time: datetime
    status: BookingStatus
    payment_mode: str
    session_duration: float  # How long user took to book
    is_tatkal: bool

@dataclass
class TrainOccupancy:
    """Train occupancy data"""
    train_number: str
    journey_date: str
    total_seats: Dict[str, int]  # class -> seat count
    available_seats: Dict[str, int]
    booked_seats: Dict[str, int]
    waitlist: Dict[str, int]
    occupancy_percent: float

class IRCTCBookingAnalytics:
    """
    Real-time IRCTC booking analytics
    Production-level implementation for railway booking insights
    """
    
    def __init__(self):
        # Booking data storage
        self.booking_attempts = deque(maxlen=50000)  # Last 50k bookings
        self.successful_bookings = {}  # booking_id -> BookingAttempt
        self.failed_bookings = []
        
        # Train data
        self.train_occupancy = {}  # train_number_date -> TrainOccupancy
        self.popular_routes = defaultdict(int)
        self.station_traffic = defaultdict(int)
        
        # Real-time metrics
        self.metrics = {
            "bookings_per_minute": 0,
            "success_rate": 0.0,
            "average_booking_time": 0.0,
            "payment_success_rate": 0.0,
            "tatkal_bookings": 0,
            "total_revenue": 0.0,
            "peak_concurrent_users": 0,
            "server_load": 0.0,
            "top_routes": [],
            "class_wise_demand": defaultdict(int),
            "payment_mode_breakdown": defaultdict(int),
            "last_updated": datetime.now()
        }
        
        # Popular Indian train routes
        self.popular_trains = {
            "12951": {"name": "Mumbai Rajdhani", "route": "Mumbai-Delhi", "classes": ["AC1", "AC2", "AC3"], "fare": 3000},
            "12301": {"name": "Howrah Rajdhani", "route": "Delhi-Kolkata", "classes": ["AC1", "AC2", "AC3"], "fare": 2800},
            "12002": {"name": "Bhopal Shatabdi", "route": "Delhi-Bhopal", "classes": ["CC", "EC"], "fare": 1800},
            "12009": {"name": "Shatabdi Express", "route": "Mumbai-Ahmedabad", "classes": ["CC", "EC"], "fare": 1200},
            "12264": {"name": "Duronto Express", "route": "Delhi-Kochi", "classes": ["SL", "AC3", "AC2"], "fare": 2200},
            "22691": {"name": "Rajdhani Express", "route": "Delhi-Bangalore", "classes": ["AC1", "AC2", "AC3"], "fare": 3200},
            "12424": {"name": "Dibrugarh Express", "route": "Delhi-Dibrugarh", "classes": ["SL", "AC3", "AC2"], "fare": 2600},
            "12650": {"name": "Karnataka Express", "route": "Delhi-Bangalore", "classes": ["SL", "AC3", "AC2"], "fare": 2400},
        }
        
        self.major_stations = [
            "NDLS", "CSTM", "HWH", "MAS", "SBC", "PUNE", "BPL", "LTT", 
            "KYN", "ADI", "JP", "JUC", "GWL", "AGC", "CNB", "ALD"
        ]
        
        # Initialize train occupancy
        self._initialize_train_data()
    
    def _initialize_train_data(self):
        """Initialize train occupancy data"""
        for train_num, train_data in self.popular_trains.items():
            for i in range(7):  # Next 7 days
                journey_date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
                key = f"{train_num}_{journey_date}"
                
                # Seat configuration based on train class
                total_seats = {}
                available_seats = {}
                
                for cls in train_data["classes"]:
                    if cls in ["AC1"]:
                        total_seats[cls] = 60
                        available_seats[cls] = random.randint(10, 60)
                    elif cls in ["AC2"]:
                        total_seats[cls] = 120
                        available_seats[cls] = random.randint(20, 120)
                    elif cls in ["AC3"]:
                        total_seats[cls] = 300
                        available_seats[cls] = random.randint(50, 300)
                    elif cls in ["CC", "EC"]:
                        total_seats[cls] = 150
                        available_seats[cls] = random.randint(30, 150)
                    else:  # SL
                        total_seats[cls] = 400
                        available_seats[cls] = random.randint(100, 400)
                
                booked_seats = {cls: total_seats[cls] - available_seats[cls] for cls in total_seats}
                total_capacity = sum(total_seats.values())
                total_booked = sum(booked_seats.values())
                occupancy = (total_booked / total_capacity) * 100
                
                self.train_occupancy[key] = TrainOccupancy(
                    train_number=train_num,
                    journey_date=journey_date,
                    total_seats=total_seats,
                    available_seats=available_seats,
                    booked_seats=booked_seats,
                    waitlist={cls: max(0, random.randint(-10, 50)) for cls in total_seats},
                    occupancy_percent=occupancy
                )
    
    def generate_booking_attempt(self, is_tatkal_time: bool = False) -> BookingAttempt:
        """Generate realistic booking attempt"""
        train_num = random.choice(list(self.popular_trains.keys()))
        train_data = self.popular_trains[train_num]
        
        # Journey date - Tatkal bookings are for specific dates
        if is_tatkal_time:
            # Tatkal opens 1 day prior for AC, same day for sleeper
            journey_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            journey_date = (datetime.now() + timedelta(days=random.randint(1, 120))).strftime('%Y-%m-%d')
        
        # Route stations
        route_stations = self.get_route_stations(train_data["route"])
        from_station = route_stations[0]
        to_station = route_stations[1]
        
        # Passenger count (families travel together)
        passenger_count = random.choices([1, 2, 3, 4, 5, 6], weights=[25, 35, 20, 15, 3, 2])[0]
        
        # Train class selection (AC preferred during summer, Sleeper preferred by budget travelers)
        available_classes = train_data["classes"]
        if is_tatkal_time:
            # Tatkal users prefer faster bookings, often higher class
            class_weights = [10, 30, 60] if len(available_classes) == 3 else [40, 60]
        else:
            # Regular users more price sensitive
            class_weights = [60, 30, 10] if len(available_classes) == 3 else [70, 30]
        
        selected_class = random.choices(available_classes, weights=class_weights)[0]
        train_class = TrainClass(selected_class)
        
        # Fare calculation (base fare * passenger count * surge multiplier)
        base_fare = train_data["fare"]
        class_multiplier = {"SL": 1.0, "AC3": 1.8, "AC2": 2.5, "AC1": 4.0, "CC": 1.2, "EC": 1.5}
        surge_multiplier = 1.4 if is_tatkal_time else 1.0
        
        total_fare = base_fare * class_multiplier.get(selected_class, 1.0) * passenger_count * surge_multiplier
        
        # Booking session duration (Tatkal users are much faster)
        if is_tatkal_time:
            session_duration = random.uniform(30, 120)  # 30 seconds to 2 minutes - very fast
        else:
            session_duration = random.uniform(180, 1200)  # 3 to 20 minutes - normal browsing
        
        # Payment mode preferences
        payment_modes = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet"]
        payment_weights = [45, 25, 15, 10, 5]  # UPI dominance in India
        
        return BookingAttempt(
            booking_id=f"IRCTC_{int(time.time())}_{random.randint(10000, 99999)}",
            user_id=f"user_{random.randint(1, 5000000)}",  # 50 lakh registered users
            train_number=train_num,
            train_name=train_data["name"],
            journey_date=journey_date,
            from_station=from_station,
            to_station=to_station,
            passenger_count=passenger_count,
            train_class=train_class,
            fare_amount=round(total_fare, 2),
            booking_time=datetime.now(),
            status=BookingStatus.INITIATED,
            payment_mode=random.choices(payment_modes, weights=payment_weights)[0],
            session_duration=session_duration,
            is_tatkal=is_tatkal_time
        )
    
    def get_route_stations(self, route: str) -> Tuple[str, str]:
        """Get from/to stations for a route"""
        route_mapping = {
            "Mumbai-Delhi": ("CSTM", "NDLS"),
            "Delhi-Kolkata": ("NDLS", "HWH"),
            "Delhi-Bhopal": ("NDLS", "BPL"),
            "Mumbai-Ahmedabad": ("CSTM", "ADI"),
            "Delhi-Kochi": ("NDLS", "ERS"),
            "Delhi-Bangalore": ("NDLS", "SBC"),
            "Delhi-Dibrugarh": ("NDLS", "DBRG")
        }
        return route_mapping.get(route, ("NDLS", "CSTM"))
    
    async def process_booking_attempt(self, booking: BookingAttempt):
        """Process booking attempt through various stages"""
        self.booking_attempts.append(booking)
        
        # Stage 1: Seat availability check
        train_key = f"{booking.train_number}_{booking.journey_date}"
        if train_key not in self.train_occupancy:
            booking.status = BookingStatus.FAILED
            self.failed_bookings.append(booking)
            return
        
        occupancy = self.train_occupancy[train_key]
        available = occupancy.available_seats.get(booking.train_class.value, 0)
        
        if available >= booking.passenger_count:
            # Seats available
            booking.status = BookingStatus.SEAT_SELECTED
            
            # Stage 2: Payment processing
            # Payment success rates vary by mode and server load
            payment_success_rates = {
                "UPI": 0.95,
                "Credit Card": 0.92,
                "Debit Card": 0.88,
                "Net Banking": 0.85,
                "Wallet": 0.96
            }
            
            # Reduce success rate during high load (Tatkal time)
            base_success_rate = payment_success_rates.get(booking.payment_mode, 0.9)
            if booking.is_tatkal:
                base_success_rate *= 0.85  # 15% reduction during peak load
            
            # Server load impact
            load_impact = max(0.7, 1.0 - (self.metrics["server_load"] * 0.3))
            final_success_rate = base_success_rate * load_impact
            
            booking.status = BookingStatus.PAYMENT_PENDING
            
            if random.random() < final_success_rate:
                # Payment successful
                booking.status = BookingStatus.CONFIRMED
                self.successful_bookings[booking.booking_id] = booking
                
                # Update train occupancy
                occupancy.available_seats[booking.train_class.value] -= booking.passenger_count
                occupancy.booked_seats[booking.train_class.value] += booking.passenger_count
                
                # Update metrics
                self.metrics["total_revenue"] += booking.fare_amount
                self.metrics["class_wise_demand"][booking.train_class.value] += booking.passenger_count
                self.metrics["payment_mode_breakdown"][booking.payment_mode] += 1
                
                route = f"{booking.from_station}-{booking.to_station}"
                self.popular_routes[route] += 1
                self.station_traffic[booking.from_station] += 1
                self.station_traffic[booking.to_station] += 1
                
                if booking.is_tatkal:
                    self.metrics["tatkal_bookings"] += 1
                
                logger.info(f"✅ Booking Confirmed: {booking.booking_id} | {booking.train_name} | ₹{booking.fare_amount}")
            
            else:
                # Payment failed
                booking.status = BookingStatus.FAILED
                self.failed_bookings.append(booking)
                logger.warning(f"❌ Payment Failed: {booking.booking_id}")
        
        elif occupancy.waitlist.get(booking.train_class.value, 0) < 200:  # Waitlist limit
            # Add to waitlist
            booking.status = BookingStatus.WAITLISTED
            occupancy.waitlist[booking.train_class.value] += booking.passenger_count
            logger.info(f"⏳ Waitlisted: {booking.booking_id}")
        
        else:
            # No seats, no waitlist
            booking.status = BookingStatus.FAILED
            self.failed_bookings.append(booking)
            logger.info(f"🚫 No Seats: {booking.booking_id}")
    
    def calculate_real_time_metrics(self):
        """Calculate real-time performance metrics"""
        if not self.booking_attempts:
            return
        
        # Last minute booking attempts
        cutoff_time = datetime.now() - timedelta(minutes=1)
        recent_bookings = [b for b in self.booking_attempts if b.booking_time > cutoff_time]
        
        self.metrics["bookings_per_minute"] = len(recent_bookings)
        
        # Success rate calculation
        if self.booking_attempts:
            successful = sum(1 for b in recent_bookings if b.status == BookingStatus.CONFIRMED)
            total = len(recent_bookings)
            self.metrics["success_rate"] = (successful / max(1, total)) * 100
        
        # Payment success rate
        payment_attempts = [b for b in recent_bookings if b.status in [BookingStatus.CONFIRMED, BookingStatus.FAILED]]
        if payment_attempts:
            payment_successes = [b for b in payment_attempts if b.status == BookingStatus.CONFIRMED]
            self.metrics["payment_success_rate"] = (len(payment_successes) / len(payment_attempts)) * 100
        
        # Average booking time
        completed_bookings = [b for b in recent_bookings if b.status in [BookingStatus.CONFIRMED, BookingStatus.FAILED]]
        if completed_bookings:
            avg_time = sum(b.session_duration for b in completed_bookings) / len(completed_bookings)
            self.metrics["average_booking_time"] = avg_time
        
        # Server load simulation (based on booking rate)
        max_capacity = 5000  # bookings per minute
        current_load = self.metrics["bookings_per_minute"]
        self.metrics["server_load"] = min(1.0, current_load / max_capacity)
        
        # Peak concurrent users (approximation)
        self.metrics["peak_concurrent_users"] = current_load * 10  # Assume 10 users per booking
        
        # Top routes
        if self.popular_routes:
            sorted_routes = sorted(self.popular_routes.items(), key=lambda x: x[1], reverse=True)
            self.metrics["top_routes"] = sorted_routes[:5]
        
        self.metrics["last_updated"] = datetime.now()
    
    def print_booking_dashboard(self):
        """Print real-time booking dashboard"""
        print(f"\n{'='*70}")
        print(f"🚂 IRCTC REAL-TIME BOOKING ANALYTICS 🚂")
        print(f"{'='*70}")
        print(f"Bookings per Minute: {self.metrics['bookings_per_minute']:,}")
        print(f"Success Rate: {self.metrics['success_rate']:.1f}%")
        print(f"Payment Success Rate: {self.metrics['payment_success_rate']:.1f}%")
        print(f"Average Booking Time: {self.metrics['average_booking_time']:.0f} seconds")
        print(f"Total Revenue Today: ₹{self.metrics['total_revenue']/100000:.2f} Lakhs")
        print(f"Tatkal Bookings: {self.metrics['tatkal_bookings']:,}")
        print(f"Concurrent Users: {self.metrics['peak_concurrent_users']:,}")
        print(f"Server Load: {self.metrics['server_load']*100:.1f}%")
        
        # Class-wise demand
        if self.metrics["class_wise_demand"]:
            print(f"\n🎫 Class-wise Demand:")
            for class_name, count in sorted(self.metrics["class_wise_demand"].items(), key=lambda x: x[1], reverse=True):
                print(f"  {class_name}: {count:,} passengers")
        
        # Payment mode breakdown
        if self.metrics["payment_mode_breakdown"]:
            print(f"\n💳 Payment Mode Breakdown:")
            total_payments = sum(self.metrics["payment_mode_breakdown"].values())
            for mode, count in sorted(self.metrics["payment_mode_breakdown"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_payments) * 100
                print(f"  {mode}: {count:,} ({percentage:.1f}%)")
        
        # Top routes
        if self.metrics["top_routes"]:
            print(f"\n🛤️ Popular Routes:")
            for route, bookings in self.metrics["top_routes"]:
                print(f"  {route}: {bookings:,} bookings")
        
        print(f"\n🕐 Last Updated: {self.metrics['last_updated'].strftime('%H:%M:%S')}")
    
    def print_train_occupancy_report(self):
        """Print train occupancy report"""
        print(f"\n{'='*60}")
        print(f"🚆 TRAIN OCCUPANCY REPORT")
        print(f"{'='*60}")
        
        # Get today's trains
        today = datetime.now().strftime('%Y-%m-%d')
        today_trains = [occ for key, occ in self.train_occupancy.items() if today in key]
        
        if not today_trains:
            print("No train data available for today")
            return
        
        # Sort by occupancy percentage
        today_trains.sort(key=lambda x: x.occupancy_percent, reverse=True)
        
        for train in today_trains[:10]:  # Top 10 trains
            train_name = self.popular_trains[train.train_number]["name"]
            print(f"\n{train_name} ({train.train_number})")
            print(f"  Occupancy: {train.occupancy_percent:.1f}%")
            
            for class_name in train.total_seats:
                total = train.total_seats[class_name]
                available = train.available_seats[class_name]
                waitlist = train.waitlist[class_name]
                occupancy = ((total - available) / total) * 100
                
                status = "🔴" if occupancy > 90 else "🟡" if occupancy > 75 else "🟢"
                print(f"  {class_name}: {status} {available}/{total} available (WL: {waitlist})")
    
    async def simulate_tatkal_booking_rush(self, duration_minutes: int = 5):
        """
        Simulate Tatkal booking rush
        Real Tatkal booking में 10:00 AM पर massive rush आता है
        """
        logger.info(f"🔥 Starting Tatkal booking rush simulation for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Tatkal booking patterns
        rush_patterns = [
            (0.0, 0.1, 8000, "Opening Rush - 10:00 AM Sharp"),    # First 10% - massive spike
            (0.1, 0.3, 5000, "High Activity - Peak Demand"),      # Next 20% - high activity
            (0.3, 0.6, 3000, "Sustained Demand"),                 # Middle - sustained
            (0.6, 0.8, 1500, "Demand Tapering"),                  # Later - demand reduces
            (0.8, 1.0, 800, "Normal Booking Rate")                # End - normal rate
        ]
        
        current_pattern_index = 0
        
        try:
            while time.time() < end_time:
                current_progress = (time.time() - start_time) / (duration_minutes * 60)
                
                # Update rush pattern
                if current_pattern_index < len(rush_patterns):
                    pattern_start, pattern_end, bookings_per_min, pattern_name = rush_patterns[current_pattern_index]
                    
                    if current_progress >= pattern_end and current_pattern_index < len(rush_patterns) - 1:
                        current_pattern_index += 1
                        logger.info(f"📊 Pattern Change: {pattern_name}")
                        bookings_per_min = rush_patterns[current_pattern_index][2]
                    elif pattern_start <= current_progress <= pattern_end:
                        bookings_per_min = rush_patterns[current_pattern_index][2]
                
                # Generate booking attempts
                bookings_this_second = random.poisson(bookings_per_min // 60)  # Convert to per second
                
                for _ in range(bookings_this_second):
                    is_tatkal = current_progress < 0.6  # First 60% are tatkal bookings
                    booking = self.generate_booking_attempt(is_tatkal_time=is_tatkal)
                    await self.process_booking_attempt(booking)
                
                # Calculate metrics
                self.calculate_real_time_metrics()
                
                # Print dashboard every 30 seconds
                if int(time.time()) % 30 == 0:
                    self.print_booking_dashboard()
                
                await asyncio.sleep(0.5)  # 500ms processing cycle
                
        except KeyboardInterrupt:
            logger.info("Tatkal simulation stopped by user")
        
        logger.info("🔥 Tatkal booking rush simulation completed!")
        
        # Final reports
        self.print_booking_dashboard()
        self.print_train_occupancy_report()

async def main():
    """Main demo function"""
    print("🚀 Starting IRCTC Real-time Booking Analytics Demo")
    
    analytics = IRCTCBookingAnalytics()
    
    try:
        # Run Tatkal booking rush simulation
        await analytics.simulate_tatkal_booking_rush(duration_minutes=3)
        
        # Final summary
        total_bookings = len(analytics.booking_attempts)
        successful_bookings = len(analytics.successful_bookings)
        failed_bookings = len(analytics.failed_bookings)
        
        print(f"\n🏁 BOOKING SUMMARY")
        print(f"Total Booking Attempts: {total_bookings:,}")
        print(f"Successful Bookings: {successful_bookings:,}")
        print(f"Failed Bookings: {failed_bookings:,}")
        print(f"Overall Success Rate: {(successful_bookings/max(1,total_bookings))*100:.1f}%")
        print(f"Total Revenue Generated: ₹{analytics.metrics['total_revenue']/100000:.2f} Lakhs")
        
    except Exception as e:
        logger.error(f"Error in IRCTC simulation: {e}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())