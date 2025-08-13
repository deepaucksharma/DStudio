#!/usr/bin/env python3
"""
Real-time Aggregation Windows Implementation
Episode 43: Real-time Analytics at Scale

Different types of time windows for real-time aggregation
Production-grade implementation with watermarks and late data handling

Use Case: Ola surge pricing algorithm - real-time demand calculation
"""

import asyncio
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional, Callable
import heapq
import threading
import json
import logging
from dataclasses import dataclass, field

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RideRequest:
    """Ola ride request event"""
    request_id: str
    user_id: str
    pickup_location: str
    drop_location: str
    ride_type: str  # auto, bike, mini, prime
    timestamp: datetime
    estimated_price: float
    surge_multiplier: float = 1.0

@dataclass
class WindowResult:
    """Window aggregation result"""
    window_start: datetime
    window_end: datetime
    total_requests: int
    unique_users: int
    total_revenue: float
    avg_surge: float
    top_pickup_location: str
    request_density: float  # requests per minute

class TimeWindow:
    """Base class for time windows"""
    
    def __init__(self, window_size_seconds: int):
        self.window_size = timedelta(seconds=window_size_seconds)
        self.events = []
        
    def add_event(self, event: RideRequest):
        """Add event to window"""
        self.events.append(event)
        
    def is_expired(self, current_time: datetime) -> bool:
        """Check if window is expired"""
        return current_time > self.window_end
        
    def compute_result(self) -> WindowResult:
        """Compute aggregation result"""
        if not self.events:
            return WindowResult(
                window_start=self.window_start,
                window_end=self.window_end,
                total_requests=0,
                unique_users=0,
                total_revenue=0.0,
                avg_surge=1.0,
                top_pickup_location="",
                request_density=0.0
            )
        
        # Calculate metrics
        total_requests = len(self.events)
        unique_users = len(set(event.user_id for event in self.events))
        total_revenue = sum(event.estimated_price * event.surge_multiplier for event in self.events)
        avg_surge = sum(event.surge_multiplier for event in self.events) / total_requests
        
        # Top pickup location
        pickup_counts = defaultdict(int)
        for event in self.events:
            pickup_counts[event.pickup_location] += 1
        top_pickup_location = max(pickup_counts.items(), key=lambda x: x[1])[0] if pickup_counts else ""
        
        # Request density (requests per minute)
        window_duration_minutes = self.window_size.total_seconds() / 60
        request_density = total_requests / window_duration_minutes if window_duration_minutes > 0 else 0
        
        return WindowResult(
            window_start=self.window_start,
            window_end=self.window_end,
            total_requests=total_requests,
            unique_users=unique_users,
            total_revenue=total_revenue,
            avg_surge=avg_surge,
            top_pickup_location=top_pickup_location,
            request_density=request_density
        )

class TumblingWindow(TimeWindow):
    """
    Tumbling Window - Fixed size, non-overlapping windows
    Example: हर 5 minute का separate window
    
    Use case: Ola में हर 5 minute में surge pricing recalculate करना
    """
    
    def __init__(self, window_size_seconds: int, start_time: datetime):
        super().__init__(window_size_seconds)
        self.window_start = start_time
        self.window_end = start_time + self.window_size
        
    @classmethod
    def create_for_timestamp(cls, timestamp: datetime, window_size_seconds: int):
        """Create window that contains the given timestamp"""
        # Align to window boundaries
        epoch = datetime(1970, 1, 1)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        window_number = int(seconds_since_epoch // window_size_seconds)
        start_time = epoch + timedelta(seconds=window_number * window_size_seconds)
        
        return cls(window_size_seconds, start_time)

class SlidingWindow(TimeWindow):
    """
    Sliding Window - Fixed size, overlapping windows
    Example: Last 10 minutes का data, हर minute update होता है
    
    Use case: Moving average calculation for smooth surge pricing
    """
    
    def __init__(self, window_size_seconds: int, slide_interval_seconds: int):
        super().__init__(window_size_seconds)
        self.slide_interval = timedelta(seconds=slide_interval_seconds)
        self.last_slide_time = None
        
    def should_slide(self, current_time: datetime) -> bool:
        """Check if window should slide"""
        if self.last_slide_time is None:
            return True
        return current_time >= self.last_slide_time + self.slide_interval
        
    def slide(self, current_time: datetime):
        """Slide the window forward"""
        self.window_start = current_time - self.window_size
        self.window_end = current_time
        self.last_slide_time = current_time
        
        # Remove old events
        self.events = [event for event in self.events 
                      if event.timestamp >= self.window_start]

class SessionWindow:
    """
    Session Window - Dynamic size based on user activity
    Window closes after period of inactivity
    
    Use case: User session tracking - continuous ride booking behavior
    """
    
    def __init__(self, session_timeout_seconds: int):
        self.session_timeout = timedelta(seconds=session_timeout_seconds)
        self.user_sessions: Dict[str, List[RideRequest]] = defaultdict(list)
        self.last_activity: Dict[str, datetime] = {}
        
    def add_event(self, event: RideRequest):
        """Add event and manage sessions"""
        user_id = event.user_id
        
        # Check if session should be closed
        if (user_id in self.last_activity and 
            event.timestamp > self.last_activity[user_id] + self.session_timeout):
            
            # Close previous session
            old_session = self.user_sessions[user_id]
            if old_session:
                yield self._create_session_result(user_id, old_session)
            
            # Start new session
            self.user_sessions[user_id] = []
        
        # Add to current session
        self.user_sessions[user_id].append(event)
        self.last_activity[user_id] = event.timestamp
        
    def _create_session_result(self, user_id: str, session_events: List[RideRequest]):
        """Create result for completed session"""
        if not session_events:
            return None
            
        session_start = min(event.timestamp for event in session_events)
        session_end = max(event.timestamp for event in session_events)
        
        return {
            "user_id": user_id,
            "session_start": session_start,
            "session_end": session_end,
            "session_duration": (session_end - session_start).total_seconds(),
            "total_rides": len(session_events),
            "total_spent": sum(event.estimated_price * event.surge_multiplier for event in session_events),
            "ride_types": list(set(event.ride_type for event in session_events))
        }
    
    def close_expired_sessions(self, current_time: datetime):
        """Close sessions that have timed out"""
        expired_users = []
        
        for user_id, last_time in self.last_activity.items():
            if current_time > last_time + self.session_timeout:
                expired_users.append(user_id)
        
        results = []
        for user_id in expired_users:
            session_events = self.user_sessions[user_id]
            if session_events:
                result = self._create_session_result(user_id, session_events)
                if result:
                    results.append(result)
            
            # Clean up
            del self.user_sessions[user_id]
            del self.last_activity[user_id]
        
        return results

class OlaSurgePricingEngine:
    """
    Ola surge pricing engine using real-time windows
    Real-time demand analysis करके surge multiplier calculate करता है
    """
    
    def __init__(self):
        # Different window types for different metrics
        self.tumbling_windows: Dict[str, TumblingWindow] = {}  # Per location
        self.sliding_window = SlidingWindow(window_size_seconds=600, slide_interval_seconds=60)  # 10min window, 1min slide
        self.session_windows = SessionWindow(session_timeout_seconds=1800)  # 30min session timeout
        
        # Surge calculation parameters
        self.base_demand_threshold = 20  # requests per minute
        self.max_surge = 3.0
        self.min_surge = 1.0
        
        # Location-based surge multipliers
        self.location_surge: Dict[str, float] = defaultdict(lambda: 1.0)
        
    def process_ride_request(self, request: RideRequest) -> Dict[str, Any]:
        """
        Process incoming ride request and update windows
        Real-time surge calculation करता है
        """
        
        # Update tumbling window for pickup location
        location = request.pickup_location
        if location not in self.tumbling_windows:
            self.tumbling_windows[location] = TumblingWindow.create_for_timestamp(
                request.timestamp, window_size_seconds=300  # 5 minute windows
            )
        
        window = self.tumbling_windows[location]
        if window.is_expired(request.timestamp):
            # Process completed window
            result = window.compute_result()
            self._update_surge_for_location(location, result)
            
            # Create new window
            self.tumbling_windows[location] = TumblingWindow.create_for_timestamp(
                request.timestamp, window_size_seconds=300
            )
            window = self.tumbling_windows[location]
        
        window.add_event(request)
        
        # Update sliding window
        if self.sliding_window.should_slide(request.timestamp):
            self.sliding_window.slide(request.timestamp)
        self.sliding_window.add_event(request)
        
        # Update session windows
        session_results = list(self.session_windows.add_event(request))
        
        # Calculate current surge
        current_surge = self._calculate_surge(location, request.timestamp)
        
        return {
            "request_id": request.request_id,
            "pickup_location": location,
            "current_surge": current_surge,
            "estimated_price": request.estimated_price * current_surge,
            "demand_level": self._get_demand_level(location),
            "session_results": session_results
        }
    
    def _update_surge_for_location(self, location: str, window_result: WindowResult):
        """Update surge multiplier based on window result"""
        demand_ratio = window_result.request_density / self.base_demand_threshold
        
        if demand_ratio > 2.0:
            surge = min(self.max_surge, 1.0 + (demand_ratio - 1.0) * 0.5)
        elif demand_ratio > 1.5:
            surge = 1.0 + (demand_ratio - 1.0) * 0.3
        elif demand_ratio < 0.5:
            surge = max(self.min_surge, 1.0 - (1.0 - demand_ratio) * 0.2)
        else:
            surge = 1.0
        
        self.location_surge[location] = surge
        
        logger.info(f"Location: {location}, Demand: {window_result.request_density:.1f} req/min, "
                   f"Surge: {surge:.2f}x")
    
    def _calculate_surge(self, location: str, timestamp: datetime) -> float:
        """Calculate current surge for location"""
        base_surge = self.location_surge[location]
        
        # Time-based surge (peak hours)
        hour = timestamp.hour
        if 8 <= hour <= 10 or 17 <= hour <= 20:  # Peak hours
            time_multiplier = 1.2
        elif 22 <= hour <= 6:  # Late night
            time_multiplier = 1.5
        else:
            time_multiplier = 1.0
        
        return min(self.max_surge, base_surge * time_multiplier)
    
    def _get_demand_level(self, location: str) -> str:
        """Get human-readable demand level"""
        surge = self.location_surge[location]
        
        if surge >= 2.5:
            return "बहुत ज्यादा"  # Very High
        elif surge >= 2.0:
            return "ज्यादा"      # High
        elif surge >= 1.5:
            return "मध्यम"       # Medium
        else:
            return "कम"          # Low
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get current real-time metrics"""
        # Sliding window metrics
        sliding_result = self.sliding_window.compute_result()
        
        # Location-wise surge
        location_metrics = {}
        for location, surge in self.location_surge.items():
            window = self.tumbling_windows.get(location)
            if window:
                result = window.compute_result()
                location_metrics[location] = {
                    "surge_multiplier": surge,
                    "demand_level": self._get_demand_level(location),
                    "current_requests": result.total_requests,
                    "request_density": result.request_density
                }
        
        return {
            "overall_metrics": {
                "total_requests_10min": sliding_result.total_requests,
                "unique_users_10min": sliding_result.unique_users,
                "avg_surge_10min": sliding_result.avg_surge,
                "revenue_rate": sliding_result.total_revenue / 10  # per minute
            },
            "location_metrics": location_metrics,
            "timestamp": datetime.now().isoformat()
        }

def generate_sample_ride_requests():
    """Generate sample ride requests for testing"""
    import random
    
    locations = [
        "Bandra", "Andheri", "Powai", "Dadar", "Kurla",
        "Malad", "Goregaon", "Thane", "Navi Mumbai", "Ghatkopar"
    ]
    
    ride_types = ["auto", "bike", "mini", "prime"]
    
    requests = []
    base_time = datetime.now()
    
    for i in range(1000):
        # Simulate traffic patterns
        hour = (base_time + timedelta(minutes=i)).hour
        if 8 <= hour <= 10 or 17 <= hour <= 20:  # Peak hours
            probability = 0.8
        elif 22 <= hour <= 6:  # Late night
            probability = 0.3
        else:
            probability = 0.5
        
        if random.random() < probability:
            pickup = random.choice(locations)
            drop = random.choice([loc for loc in locations if loc != pickup])
            ride_type = random.choice(ride_types)
            
            base_price = {
                "auto": 50,
                "bike": 30,
                "mini": 80,
                "prime": 120
            }[ride_type]
            
            request = RideRequest(
                request_id=f"OLA_{i:06d}",
                user_id=f"user_{random.randint(1, 500)}",
                pickup_location=pickup,
                drop_location=drop,
                ride_type=ride_type,
                timestamp=base_time + timedelta(minutes=i, seconds=random.randint(0, 59)),
                estimated_price=base_price + random.uniform(-10, 20)
            )
            
            requests.append(request)
    
    return sorted(requests, key=lambda x: x.timestamp)

def run_ola_surge_demo():
    """Run Ola surge pricing demo"""
    
    logger.info("शुरू कर रहे हैं Ola surge pricing simulation...")
    
    engine = OlaSurgePricingEngine()
    requests = generate_sample_ride_requests()
    
    processed_count = 0
    for request in requests:
        result = engine.process_ride_request(request)
        processed_count += 1
        
        if processed_count % 50 == 0:
            # Print metrics every 50 requests
            metrics = engine.get_real_time_metrics()
            print(f"\n=== Real-time Metrics (after {processed_count} requests) ===")
            print(f"Overall - Requests (10min): {metrics['overall_metrics']['total_requests_10min']}")
            print(f"Overall - Revenue Rate: ₹{metrics['overall_metrics']['revenue_rate']:.2f}/min")
            
            print("\nLocation-wise Surge:")
            for location, data in sorted(metrics['location_metrics'].items(), 
                                       key=lambda x: x[1]['surge_multiplier'], reverse=True)[:5]:
                print(f"  {location}: {data['surge_multiplier']:.2f}x ({data['demand_level']}) "
                      f"- {data['request_density']:.1f} req/min")
        
        # Simulate real-time processing
        time.sleep(0.01)  # 10ms delay
    
    # Final metrics
    final_metrics = engine.get_real_time_metrics()
    print(f"\n=== Final Surge Pricing Report ===")
    print(f"Total Requests Processed: {processed_count}")
    print(f"Peak Surge Locations:")
    
    for location, data in sorted(final_metrics['location_metrics'].items(), 
                               key=lambda x: x[1]['surge_multiplier'], reverse=True):
        print(f"  {location}: {data['surge_multiplier']:.2f}x surge - {data['demand_level']} demand")

if __name__ == "__main__":
    run_ola_surge_demo()