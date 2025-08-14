#!/usr/bin/env python3
"""
Complex Event Processing (CEP) for Mumbai Traffic Management
============================================================
मुंबई ट्रैफिक प्रबंधन के लिए कॉम्प्लेक्स इवेंट प्रोसेसिंग (CEP)

Production-ready Complex Event Processing system for Mumbai Traffic Police to 
monitor real-time traffic patterns, detect congestion, manage signal timings,
and coordinate emergency response using event correlation and pattern matching.

This example demonstrates:
यह उदाहरण प्रदर्शित करता है:

1. Complex Event Processing patterns - कॉम्प्लेक्स इवेंट प्रोसेसिंग पैटर्न
2. Real-time event stream correlation - रियल-टाइम इवेंट स्ट्रीम सहसंबंध
3. Sliding window aggregations - स्लाइडिंग विंडो एकीकरण
4. Pattern detection and alerting - पैटर्न पहचान और चेतावनी
5. Event-driven traffic signal control - इवेंट-संचालित ट्रैफिक सिग्नल नियंत्रण
6. Emergency vehicle priority system - आपातकालीन वाहन प्राथमिकता प्रणाली

Author: Hindi Podcast Series
Episode: 020 - Event-Driven Architecture
Context: Mumbai Traffic Police intelligent traffic management system
"""

import asyncio
import json
import uuid
import time
import logging
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Any, Callable, Tuple
from collections import defaultdict, deque
import random
import statistics
import math
from abc import ABC, abstractmethod

# Configure logging - लॉगिंग कॉन्फ़िगरेशन
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TrafficEventType(Enum):
    """Traffic event types - ट्रैफिक इवेंट प्रकार"""
    VEHICLE_DETECTED = "vehicle.detected"
    CONGESTION_DETECTED = "congestion.detected"
    EMERGENCY_VEHICLE = "emergency.vehicle"
    SIGNAL_CHANGED = "signal.changed"
    ACCIDENT_REPORTED = "accident.reported"
    WEATHER_UPDATE = "weather.update"
    SPEED_VIOLATION = "speed.violation"
    PARKING_VIOLATION = "parking.violation"
    ROUTE_BLOCKED = "route.blocked"
    TRAFFIC_CLEARED = "traffic.cleared"

class VehicleType(Enum):
    """Vehicle types - वाहन प्रकार"""
    CAR = "CAR"                     # कार
    TRUCK = "TRUCK"                 # ट्रक
    BUS = "BUS"                     # बस
    MOTORCYCLE = "MOTORCYCLE"       # मोटरसाइकिल
    AUTO_RICKSHAW = "AUTO_RICKSHAW" # ऑटो रिक्शा
    AMBULANCE = "AMBULANCE"         # एम्बुलेंस
    FIRE_TRUCK = "FIRE_TRUCK"       # दमकल
    POLICE = "POLICE"               # पुलिस

class SignalState(Enum):
    """Traffic signal states - ट्रैफिक सिग्नल स्थिति"""
    RED = "RED"                     # लाल
    YELLOW = "YELLOW"               # पीला
    GREEN = "GREEN"                 # हरा

class CongestionLevel(Enum):
    """Traffic congestion levels - ट्रैफिक जाम स्तर"""
    LIGHT = "LIGHT"                 # हल्का
    MODERATE = "MODERATE"           # मध्यम
    HEAVY = "HEAVY"                 # भारी
    CRITICAL = "CRITICAL"           # गंभीर

@dataclass
class Location:
    """Geographic location - भौगोलिक स्थान"""
    latitude: float
    longitude: float
    area: str
    landmark: str
    
    def distance_to(self, other: 'Location') -> float:
        """Calculate distance in kilometers - किलोमीटर में दूरी की गणना करें"""
        # Simplified haversine formula for Mumbai scale
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return 6371 * c  # Earth's radius in km

@dataclass
class TrafficEvent:
    """Base traffic event - बेस ट्रैफिक इवेंट"""
    event_id: str
    event_type: TrafficEventType
    timestamp: datetime
    location: Location
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "traffic_sensor"
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'location': {
                'latitude': self.location.latitude,
                'longitude': self.location.longitude,
                'area': self.location.area,
                'landmark': self.location.landmark
            },
            'data': self.data,
            'source': self.source,
            'correlation_id': self.correlation_id
        }

@dataclass
class VehicleDetectionEvent(TrafficEvent):
    """Vehicle detection event - वाहन पहचान इवेंट"""
    vehicle_type: VehicleType
    speed: float  # km/h
    direction: str
    license_plate: Optional[str] = None
    
    def __post_init__(self):
        self.event_type = TrafficEventType.VEHICLE_DETECTED
        self.data.update({
            'vehicle_type': self.vehicle_type.value,
            'speed': self.speed,
            'direction': self.direction,
            'license_plate': self.license_plate
        })

@dataclass
class CongestionEvent(TrafficEvent):
    """Traffic congestion event - ट्रैफिक जाम इवेंट"""
    congestion_level: CongestionLevel
    avg_speed: float
    vehicle_count: int
    duration_minutes: int
    
    def __post_init__(self):
        self.event_type = TrafficEventType.CONGESTION_DETECTED
        self.data.update({
            'congestion_level': self.congestion_level.value,
            'avg_speed': self.avg_speed,
            'vehicle_count': self.vehicle_count,
            'duration_minutes': self.duration_minutes
        })

@dataclass
class EmergencyVehicleEvent(TrafficEvent):
    """Emergency vehicle event - आपातकालीन वाहन इवेंट"""
    vehicle_type: VehicleType
    priority_level: int  # 1-10, 10 being highest
    destination: Optional[Location] = None
    
    def __post_init__(self):
        self.event_type = TrafficEventType.EMERGENCY_VEHICLE
        self.data.update({
            'vehicle_type': self.vehicle_type.value,
            'priority_level': self.priority_level,
            'destination': self.destination.__dict__ if self.destination else None
        })

class EventWindow:
    """Time-based event window for aggregation - एकीकरण के लिए समय-आधारित इवेंट विंडो"""
    
    def __init__(self, window_size_seconds: int, slide_interval_seconds: int = None):
        self.window_size = timedelta(seconds=window_size_seconds)
        self.slide_interval = timedelta(seconds=slide_interval_seconds or window_size_seconds // 4)
        self.events: deque = deque()
        self.last_slide = datetime.now()
    
    def add_event(self, event: TrafficEvent):
        """Add event to window - विंडो में इवेंट जोड़ें"""
        self.events.append(event)
        self._cleanup_old_events()
    
    def _cleanup_old_events(self):
        """Remove events outside window - विंडो के बाहर के इवेंट हटाएं"""
        cutoff_time = datetime.now() - self.window_size
        while self.events and self.events[0].timestamp < cutoff_time:
            self.events.popleft()
    
    def get_events_in_window(self, event_type: TrafficEventType = None) -> List[TrafficEvent]:
        """Get events in current window - वर्तमान विंडो में इवेंट प्राप्त करें"""
        self._cleanup_old_events()
        
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return list(self.events)
    
    def get_events_near_location(self, location: Location, radius_km: float = 0.5) -> List[TrafficEvent]:
        """Get events near specific location - विशिष्ट स्थान के पास के इवेंट प्राप्त करें"""
        nearby_events = []
        for event in self.get_events_in_window():
            if event.location.distance_to(location) <= radius_km:
                nearby_events.append(event)
        return nearby_events

class PatternRule(ABC):
    """Abstract base class for CEP pattern rules - CEP पैटर्न नियमों के लिए अमूर्त बेस क्लास"""
    
    @abstractmethod
    def matches(self, window: EventWindow) -> List[Dict[str, Any]]:
        """Check if pattern matches events in window - जांचें कि क्या पैटर्न विंडो में इवेंट्स से मेल खाता है"""
        pass
    
    @abstractmethod
    def get_rule_name(self) -> str:
        """Get rule name - नियम का नाम प्राप्त करें"""
        pass

class CongestionDetectionRule(PatternRule):
    """Detect traffic congestion patterns - ट्रैफिक जाम पैटर्न का पता लगाएं"""
    
    def __init__(self, min_vehicles: int = 20, max_avg_speed: float = 15.0, min_duration_minutes: int = 5):
        self.min_vehicles = min_vehicles
        self.max_avg_speed = max_avg_speed
        self.min_duration = timedelta(minutes=min_duration_minutes)
    
    def matches(self, window: EventWindow) -> List[Dict[str, Any]]:
        """Detect congestion based on vehicle count and speed - वाहन संख्या और गति के आधार पर जाम का पता लगाएं"""
        matches = []
        
        # Group vehicle detections by location (within 200m radius)
        # स्थान के अनुसार वाहन पहचान को समूहित करें (200m त्रिज्या के भीतर)
        location_groups = defaultdict(list)
        
        vehicle_events = window.get_events_in_window(TrafficEventType.VEHICLE_DETECTED)
        
        for event in vehicle_events:
            # Find existing group or create new one
            assigned = False
            for location_key, events in location_groups.items():
                if events and events[0].location.distance_to(event.location) <= 0.2:  # 200m
                    location_groups[location_key].append(event)
                    assigned = True
                    break
            
            if not assigned:
                location_key = f"{event.location.area}_{len(location_groups)}"
                location_groups[location_key] = [event]
        
        # Check each location group for congestion
        for location_key, events in location_groups.items():
            if len(events) >= self.min_vehicles:
                speeds = [e.data['speed'] for e in events if 'speed' in e.data and e.data['speed'] > 0]
                
                if speeds:
                    avg_speed = statistics.mean(speeds)
                    if avg_speed <= self.max_avg_speed:
                        # Check duration
                        time_span = max(events, key=lambda x: x.timestamp).timestamp - \
                                  min(events, key=lambda x: x.timestamp).timestamp
                        
                        if time_span >= self.min_duration:
                            congestion_level = self._determine_congestion_level(avg_speed, len(events))
                            
                            matches.append({
                                'rule_name': self.get_rule_name(),
                                'location': events[0].location,
                                'vehicle_count': len(events),
                                'avg_speed': avg_speed,
                                'duration_minutes': time_span.total_seconds() / 60,
                                'congestion_level': congestion_level,
                                'contributing_events': [e.event_id for e in events]
                            })
        
        return matches
    
    def _determine_congestion_level(self, avg_speed: float, vehicle_count: int) -> CongestionLevel:
        """Determine congestion level - जाम स्तर निर्धारित करें"""
        if avg_speed < 5 or vehicle_count > 100:
            return CongestionLevel.CRITICAL
        elif avg_speed < 10 or vehicle_count > 60:
            return CongestionLevel.HEAVY
        elif avg_speed < 15 or vehicle_count > 30:
            return CongestionLevel.MODERATE
        else:
            return CongestionLevel.LIGHT
    
    def get_rule_name(self) -> str:
        return "CongestionDetection"

class EmergencyVehicleCorridorRule(PatternRule):
    """Create emergency corridor for ambulances/fire trucks - एम्बुलेंस/दमकल के लिए आपातकालीन कॉरिडोर बनाएं"""
    
    def __init__(self, corridor_width_km: float = 0.5, ahead_distance_km: float = 2.0):
        self.corridor_width = corridor_width_km
        self.ahead_distance = ahead_distance_km
    
    def matches(self, window: EventWindow) -> List[Dict[str, Any]]:
        """Detect emergency vehicles and create corridors - आपातकालीन वाहन पहचानें और कॉरिडोर बनाएं"""
        matches = []
        
        emergency_events = window.get_events_in_window(TrafficEventType.EMERGENCY_VEHICLE)
        
        for emergency_event in emergency_events:
            # Find all regular vehicles in the emergency vehicle's path
            # आपातकालीन वाहन के रास्ते में सभी नियमित वाहन खोजें
            nearby_vehicles = window.get_events_near_location(
                emergency_event.location, 
                self.corridor_width
            )
            
            regular_vehicles = [
                v for v in nearby_vehicles 
                if v.event_type == TrafficEventType.VEHICLE_DETECTED and 
                v.data.get('vehicle_type') not in ['AMBULANCE', 'FIRE_TRUCK', 'POLICE']
            ]
            
            if regular_vehicles:
                matches.append({
                    'rule_name': self.get_rule_name(),
                    'emergency_vehicle': emergency_event.event_id,
                    'emergency_type': emergency_event.data.get('vehicle_type'),
                    'priority_level': emergency_event.data.get('priority_level', 5),
                    'location': emergency_event.location,
                    'affected_vehicles': [v.event_id for v in regular_vehicles],
                    'corridor_action': 'CLEAR_PATH',
                    'estimated_clearance_time': len(regular_vehicles) * 10  # seconds
                })
        
        return matches
    
    def get_rule_name(self) -> str:
        return "EmergencyVehicleCorridor"

class SpeedViolationRule(PatternRule):
    """Detect speed violations - गति उल्लंघन का पता लगाएं"""
    
    def __init__(self):
        # Mumbai area speed limits - मुंबई क्षेत्र की गति सीमा
        self.speed_limits = {
            'Bandra-Kurla Complex': 60,
            'Colaba': 40,
            'Andheri': 50,
            'Powai': 60,
            'Malad': 50,
            'Thane': 60,
            'Navi Mumbai': 70,
            'Fort': 30,  # Business district
            'Default': 50
        }
    
    def matches(self, window: EventWindow) -> List[Dict[str, Any]]:
        """Detect vehicles exceeding speed limits - गति सीमा पार करने वाले वाहन पहचानें"""
        matches = []
        
        vehicle_events = window.get_events_in_window(TrafficEventType.VEHICLE_DETECTED)
        
        for event in vehicle_events:
            vehicle_speed = event.data.get('speed', 0)
            area = event.location.area
            
            speed_limit = self.speed_limits.get(area, self.speed_limits['Default'])
            
            # Allow 10% tolerance - 10% सहनशीलता दें
            tolerance = speed_limit * 0.1
            
            if vehicle_speed > (speed_limit + tolerance):
                violation_severity = self._calculate_violation_severity(vehicle_speed, speed_limit)
                
                matches.append({
                    'rule_name': self.get_rule_name(),
                    'vehicle_event': event.event_id,
                    'location': event.location,
                    'actual_speed': vehicle_speed,
                    'speed_limit': speed_limit,
                    'excess_speed': vehicle_speed - speed_limit,
                    'violation_severity': violation_severity,
                    'license_plate': event.data.get('license_plate'),
                    'fine_amount': self._calculate_fine(violation_severity)
                })
        
        return matches
    
    def _calculate_violation_severity(self, actual_speed: float, speed_limit: float) -> str:
        """Calculate violation severity - उल्लंघन गंभीरता की गणना करें"""
        excess_percentage = ((actual_speed - speed_limit) / speed_limit) * 100
        
        if excess_percentage >= 50:
            return "CRITICAL"
        elif excess_percentage >= 30:
            return "HIGH"
        elif excess_percentage >= 15:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_fine(self, severity: str) -> int:
        """Calculate fine amount in INR - जुर्माना राशि की गणना करें (रुपए में)"""
        fine_amounts = {
            "LOW": 500,
            "MEDIUM": 1000,
            "HIGH": 2000,
            "CRITICAL": 5000
        }
        return fine_amounts.get(severity, 500)
    
    def get_rule_name(self) -> str:
        return "SpeedViolation"

class ComplexEventProcessor:
    """Complex Event Processing engine - कॉम्प्लेक्स इवेंट प्रोसेसिंग इंजन"""
    
    def __init__(self, window_size_seconds: int = 300):  # 5 minute window
        self.window = EventWindow(window_size_seconds)
        self.rules: List[PatternRule] = []
        self.pattern_matches: List[Dict[str, Any]] = []
        self.is_processing = False
    
    def add_rule(self, rule: PatternRule):
        """Add pattern rule - पैटर्न नियम जोड़ें"""
        self.rules.append(rule)
        logger.info(f"Added CEP rule: {rule.get_rule_name()}")
    
    async def process_event(self, event: TrafficEvent):
        """Process incoming event - आने वाले इवेंट को प्रोसेस करें"""
        self.window.add_event(event)
        
        # Apply all rules to detect patterns - पैटर्न पहचानने के लिए सभी नियम लागू करें
        for rule in self.rules:
            try:
                matches = rule.matches(self.window)
                for match in matches:
                    match['detected_at'] = datetime.now().isoformat()
                    match['trigger_event'] = event.event_id
                    self.pattern_matches.append(match)
                    
                    # Emit pattern detection event - पैटर्न पहचान इवेंट उत्सर्जित करें
                    await self._emit_pattern_detected(match)
                    
            except Exception as e:
                logger.error(f"Error in rule {rule.get_rule_name()}: {e}")
    
    async def _emit_pattern_detected(self, match: Dict[str, Any]):
        """Emit pattern detection event - पैटर्न पहचान इवेंट उत्सर्जित करें"""
        rule_name = match['rule_name']
        logger.info(f"🎯 Pattern detected: {rule_name} - {match.get('location', {}).get('area', 'Unknown')}")
        
        # Here you would typically publish to event bus or notification system
        # यहाँ आप आमतौर पर इवेंट बस या नोटिफिकेशन सिस्टम को प्रकाशित करते हैं
        
    def get_recent_patterns(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Get recently detected patterns - हाल ही में पहचाने गए पैटर्न प्राप्त करें"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            match for match in self.pattern_matches
            if datetime.fromisoformat(match['detected_at']) >= cutoff_time
        ]

class TrafficSignalController:
    """Intelligent traffic signal controller - बुद्धिमान ट्रैफिक सिग्नल नियंत्रक"""
    
    def __init__(self):
        self.signals: Dict[str, Dict[str, Any]] = {}
        self.default_timings = {
            'RED': 60,      # seconds
            'YELLOW': 10,
            'GREEN': 90
        }
    
    def initialize_signal(self, intersection_name: str, location: Location):
        """Initialize traffic signal - ट्रैफिक सिग्नल इनिशियलाइज़ करें"""
        self.signals[intersection_name] = {
            'location': location,
            'current_state': SignalState.RED,
            'state_changed_at': datetime.now(),
            'timings': self.default_timings.copy(),
            'emergency_override': False,
            'congestion_adjusted': False
        }
    
    async def handle_congestion_pattern(self, congestion_match: Dict[str, Any]):
        """Adjust signal timing based on congestion - जाम के आधार पर सिग्नल समय समायोजित करें"""
        location = congestion_match['location']
        congestion_level = congestion_match['congestion_level']
        
        # Find nearest traffic signal - निकटतम ट्रैफिक सिग्नल खोजें
        nearest_signal = self._find_nearest_signal(location)
        
        if nearest_signal:
            signal_data = self.signals[nearest_signal]
            
            # Adjust timings based on congestion level - जाम स्तर के आधार पर समय समायोजित करें
            if congestion_level == 'CRITICAL':
                signal_data['timings']['GREEN'] = 120  # Extend green time
                signal_data['timings']['RED'] = 45     # Reduce red time
            elif congestion_level == 'HEAVY':
                signal_data['timings']['GREEN'] = 105
                signal_data['timings']['RED'] = 50
            elif congestion_level == 'MODERATE':
                signal_data['timings']['GREEN'] = 100
                signal_data['timings']['RED'] = 55
            
            signal_data['congestion_adjusted'] = True
            
            logger.info(f"🚦 Adjusted signal timing at {nearest_signal} for {congestion_level} congestion")
    
    async def handle_emergency_corridor(self, corridor_match: Dict[str, Any]):
        """Create emergency corridor by controlling signals - सिग्नल नियंत्रण द्वारा आपातकालीन कॉरिडोर बनाएं"""
        location = corridor_match['location']
        priority_level = corridor_match.get('priority_level', 5)
        
        # Find signals in emergency path - आपातकालीन रास्ते में सिग्नल खोजें
        affected_signals = []
        for signal_name, signal_data in self.signals.items():
            if signal_data['location'].distance_to(location) <= 1.0:  # Within 1km
                affected_signals.append(signal_name)
        
        # Override signals for emergency passage - आपातकालीन गुजारे के लिए सिग्नल ओवरराइड करें
        for signal_name in affected_signals:
            signal_data = self.signals[signal_name]
            signal_data['emergency_override'] = True
            signal_data['current_state'] = SignalState.GREEN
            signal_data['state_changed_at'] = datetime.now()
            
            # Schedule return to normal after emergency passes - आपातकाल के बाद सामान्य स्थिति में वापसी का शेड्यूल
            override_duration = 120 if priority_level >= 8 else 90  # seconds
            
            logger.info(f"🚨 Emergency override: {signal_name} GREEN for {override_duration}s")
    
    def _find_nearest_signal(self, location: Location) -> Optional[str]:
        """Find nearest traffic signal to location - स्थान के निकटतम ट्रैफिक सिग्नल खोजें"""
        nearest_signal = None
        min_distance = float('inf')
        
        for signal_name, signal_data in self.signals.items():
            distance = signal_data['location'].distance_to(location)
            if distance < min_distance:
                min_distance = distance
                nearest_signal = signal_name
        
        return nearest_signal if min_distance <= 2.0 else None  # Within 2km

class TrafficDataGenerator:
    """Generate realistic Mumbai traffic data - यथार्थवादी मुंबई ट्रैफिक डेटा जेनरेट करें"""
    
    def __init__(self):
        # Mumbai key locations - मुंबई के मुख्य स्थान
        self.locations = {
            'Bandra-Kurla Complex': Location(19.0596, 72.8656, 'Bandra-Kurla Complex', 'BKC'),
            'Andheri West': Location(19.1368, 72.8280, 'Andheri', 'Andheri Station'),
            'Powai': Location(19.1176, 72.9060, 'Powai', 'Hiranandani'),
            'Colaba': Location(18.9067, 72.8147, 'Colaba', 'Gateway of India'),
            'Fort': Location(18.9388, 72.8354, 'Fort', 'CST Station'),
            'Malad': Location(19.1864, 72.8493, 'Malad', 'Malad Station'),
            'Thane': Location(19.2183, 72.9781, 'Thane', 'Thane Station'),
            'Navi Mumbai': Location(19.0330, 73.0297, 'Navi Mumbai', 'Vashi')
        }
        
        # Vehicle distribution for Mumbai - मुंबई के लिए वाहन वितरण
        self.vehicle_distribution = {
            VehicleType.MOTORCYCLE: 0.35,      # 35% bikes
            VehicleType.CAR: 0.30,             # 30% cars
            VehicleType.AUTO_RICKSHAW: 0.15,   # 15% autos
            VehicleType.BUS: 0.10,             # 10% buses
            VehicleType.TRUCK: 0.09,           # 9% trucks
            VehicleType.AMBULANCE: 0.005,      # 0.5% ambulances
            VehicleType.POLICE: 0.003,         # 0.3% police
            VehicleType.FIRE_TRUCK: 0.002      # 0.2% fire trucks
        }
    
    def generate_vehicle_event(self, location_name: str = None) -> VehicleDetectionEvent:
        """Generate random vehicle detection event - यादृच्छिक वाहन पहचान इवेंट जेनरेट करें"""
        if location_name:
            location = self.locations[location_name]
        else:
            location = random.choice(list(self.locations.values()))
        
        # Select vehicle type based on distribution - वितरण के आधार पर वाहन प्रकार चुनें
        rand = random.random()
        cumulative = 0
        vehicle_type = VehicleType.CAR  # default
        
        for vtype, prob in self.vehicle_distribution.items():
            cumulative += prob
            if rand <= cumulative:
                vehicle_type = vtype
                break
        
        # Generate realistic speed based on area and time - क्षेत्र और समय के आधार पर यथार्थवादी गति जेनरेट करें
        base_speed = self._get_area_base_speed(location.area)
        speed_variance = random.uniform(0.7, 1.3)  # ±30% variance
        speed = max(5, base_speed * speed_variance)
        
        # Add Mumbai-specific license plate format - मुंबई-विशिष्ट लाइसेंस प्लेट प्रारूप जोड़ें
        license_plate = None
        if random.random() < 0.8:  # 80% chance of readable plate
            mh_code = random.choice(['MH01', 'MH02', 'MH03', 'MH04', 'MH05'])
            series = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
            number = random.randint(1000, 9999)
            license_plate = f"{mh_code}{series}{number}"
        
        return VehicleDetectionEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            location=location,
            vehicle_type=vehicle_type,
            speed=speed,
            direction=random.choice(['North', 'South', 'East', 'West', 'Northeast', 'Northwest', 'Southeast', 'Southwest']),
            license_plate=license_plate
        )
    
    def generate_emergency_event(self) -> EmergencyVehicleEvent:
        """Generate emergency vehicle event - आपातकालीन वाहन इवेंट जेनरेट करें"""
        emergency_types = [VehicleType.AMBULANCE, VehicleType.FIRE_TRUCK, VehicleType.POLICE]
        vehicle_type = random.choice(emergency_types)
        
        location = random.choice(list(self.locations.values()))
        
        # Higher priority for ambulances and fire trucks - एम्बुलेंस और दमकल के लिए उच्च प्राथमिकता
        if vehicle_type == VehicleType.AMBULANCE:
            priority = random.randint(7, 10)
        elif vehicle_type == VehicleType.FIRE_TRUCK:
            priority = random.randint(8, 10)
        else:  # Police
            priority = random.randint(5, 8)
        
        return EmergencyVehicleEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            location=location,
            vehicle_type=vehicle_type,
            priority_level=priority
        )
    
    def _get_area_base_speed(self, area: str) -> float:
        """Get base speed for area - क्षेत्र के लिए बेस गति प्राप्त करें"""
        area_speeds = {
            'Fort': 25,                    # Business district - slow
            'Colaba': 35,                  # Tourist area
            'Bandra-Kurla Complex': 45,    # Corporate area
            'Andheri': 40,                 # Suburban
            'Powai': 50,                   # Planned area
            'Malad': 35,                   # Dense suburban
            'Thane': 45,                   # Extended suburb
            'Navi Mumbai': 55              # Planned city
        }
        return area_speeds.get(area, 40)

async def demonstrate_complex_event_processing():
    """Demonstrate Mumbai traffic CEP system"""
    """मुंबई ट्रैफिक CEP सिस्टम का प्रदर्शन"""
    
    print("🚦 Starting Mumbai Traffic Management CEP Demo")
    print("🚦 मुंबई ट्रैफिक प्रबंधन CEP डेमो शुरू कर रहे हैं\n")
    
    # Initialize systems - सिस्टम इनिशियलाइज़ करें
    cep_engine = ComplexEventProcessor(window_size_seconds=300)  # 5 minutes
    traffic_controller = TrafficSignalController()
    data_generator = TrafficDataGenerator()
    
    # Add CEP rules - CEP नियम जोड़ें
    cep_engine.add_rule(CongestionDetectionRule())
    cep_engine.add_rule(EmergencyVehicleCorridorRule())
    cep_engine.add_rule(SpeedViolationRule())
    
    # Initialize traffic signals at key intersections - मुख्य चौराहों पर ट्रैफिक सिग्नल इनिशियलाइज़ करें
    key_intersections = [
        ('BKC Junction', data_generator.locations['Bandra-Kurla Complex']),
        ('Andheri Bridge', data_generator.locations['Andheri West']),
        ('Powai Chowk', data_generator.locations['Powai']),
        ('CST Cross', data_generator.locations['Fort'])
    ]
    
    for intersection_name, location in key_intersections:
        traffic_controller.initialize_signal(intersection_name, location)
    
    print(f"🚦 Initialized {len(key_intersections)} traffic signals")
    print("📋 Active CEP Rules:")
    for rule in cep_engine.rules:
        print(f"   • {rule.get_rule_name()}")
    
    # Simulation parameters - सिमुलेशन पैरामीटर
    total_events = 0
    congestion_events = 0
    emergency_events = 0
    speed_violations = 0
    
    print("\n🚗 Starting traffic simulation...")
    print("   (Generating realistic Mumbai traffic patterns)")
    
    # Main simulation loop - मुख्य सिमुलेशन लूप
    simulation_start = datetime.now()
    
    for cycle in range(60):  # 60 cycles (~5 minutes of simulation)
        # Generate traffic events based on realistic patterns - यथार्थवादी पैटर्न के आधार पर ट्रैफिक इवेंट जेनरेट करें
        
        # More traffic during peak hours simulation - पीक आवर्स के दौरान अधिक ट्रैफिक सिमुलेशन
        events_this_cycle = random.randint(5, 15)
        
        # Higher emergency probability during peak hours - पीक आवर्स के दौरान उच्च आपातकालीन संभावना
        emergency_probability = 0.02 if cycle % 10 < 5 else 0.05  # Higher during "rush hour" cycles
        
        for _ in range(events_this_cycle):
            if random.random() < emergency_probability:
                # Generate emergency vehicle event - आपातकालीन वाहन इवेंट जेनरेट करें
                event = data_generator.generate_emergency_event()
                emergency_events += 1
                print(f"🚨 Emergency: {event.vehicle_type.value} at {event.location.area}")
            else:
                # Generate regular vehicle event - नियमित वाहन इवेंट जेनरेट करें
                event = data_generator.generate_vehicle_event()
            
            # Process event through CEP engine - CEP इंजन के माध्यम से इवेंट प्रोसेस करें
            await cep_engine.process_event(event)
            total_events += 1
        
        # Check for pattern matches and take actions - पैटर्न मैच की जांच करें और कार्रवाई करें
        recent_patterns = cep_engine.get_recent_patterns(minutes=1)
        
        for pattern in recent_patterns:
            rule_name = pattern['rule_name']
            
            if rule_name == 'CongestionDetection':
                congestion_events += 1
                congestion_level = pattern['congestion_level']
                location = pattern['location']
                vehicle_count = pattern['vehicle_count']
                
                print(f"🚗💨 CONGESTION detected: {congestion_level} at {location.area} ({vehicle_count} vehicles)")
                
                # Adjust traffic signals - ट्रैफिक सिग्नल समायोजित करें
                await traffic_controller.handle_congestion_pattern(pattern)
                
            elif rule_name == 'EmergencyVehicleCorridor':
                emergency_type = pattern['emergency_type']
                location = pattern['location']
                affected_count = len(pattern['affected_vehicles'])
                
                print(f"🚨 EMERGENCY corridor: {emergency_type} at {location.area} (clearing {affected_count} vehicles)")
                
                # Create emergency corridor - आपातकालीन कॉरिडोर बनाएं
                await traffic_controller.handle_emergency_corridor(pattern)
                
            elif rule_name == 'SpeedViolation':
                speed_violations += 1
                actual_speed = pattern['actual_speed']
                speed_limit = pattern['speed_limit']
                location = pattern['location']
                fine_amount = pattern['fine_amount']
                
                print(f"⚡ SPEED violation: {actual_speed:.1f} km/h in {speed_limit} zone at {location.area} (Fine: ₹{fine_amount})")
        
        # Progress update every 10 cycles - हर 10 चक्रों में प्रगति अपडेट
        if (cycle + 1) % 10 == 0:
            elapsed = (datetime.now() - simulation_start).total_seconds()
            print(f"\n📊 Progress: {cycle + 1}/60 cycles ({elapsed:.1f}s elapsed)")
            print(f"   Events processed: {total_events}")
            print(f"   Patterns detected: {len(cep_engine.pattern_matches)}")
        
        # Simulate real-time processing delay - रियल-टाइम प्रोसेसिंग देरी का सिमुलेशन
        await asyncio.sleep(0.1)
    
    # Final statistics - अंतिम आंकड़े
    total_simulation_time = (datetime.now() - simulation_start).total_seconds()
    
    print("\n" + "="*60)
    print("📈 MUMBAI TRAFFIC CEP SIMULATION RESULTS")
    print("📈 मुंबई ट्रैफिक CEP सिमुलेशन परिणाम")
    print("="*60)
    
    print(f"\n🕒 Simulation Duration: {total_simulation_time:.1f} seconds")
    print(f"📊 Total Events Processed: {total_events:,}")
    print(f"⚡ Events per Second: {total_events/total_simulation_time:.1f}")
    
    print(f"\n🎯 Pattern Detection Summary:")
    print(f"   🚗💨 Congestion Events: {congestion_events}")
    print(f"   🚨 Emergency Corridors: {emergency_events}")
    print(f"   ⚡ Speed Violations: {speed_violations}")
    print(f"   📋 Total Patterns: {len(cep_engine.pattern_matches)}")
    
    # Show pattern details - पैटर्न विवरण दिखाएं
    if cep_engine.pattern_matches:
        print(f"\n🔍 Recent Pattern Details (Last 5):")
        for pattern in cep_engine.pattern_matches[-5:]:
            rule_name = pattern['rule_name']
            detected_at = pattern['detected_at']
            
            if rule_name == 'CongestionDetection':
                location = pattern['location']
                level = pattern['congestion_level']
                vehicles = pattern['vehicle_count']
                print(f"   🚗💨 {detected_at[:19]}: {level} congestion at {location.area} ({vehicles} vehicles)")
                
            elif rule_name == 'SpeedViolation':
                location = pattern['location']
                speed = pattern['actual_speed']
                limit = pattern['speed_limit']
                fine = pattern['fine_amount']
                print(f"   ⚡ {detected_at[:19]}: {speed:.1f}km/h in {limit}km/h zone at {location.area} (₹{fine})")
                
            elif rule_name == 'EmergencyVehicleCorridor':
                location = pattern['location']
                vehicle_type = pattern['emergency_type']
                affected = len(pattern['affected_vehicles'])
                print(f"   🚨 {detected_at[:19]}: {vehicle_type} corridor at {location.area} ({affected} vehicles affected)")
    
    # Show traffic signal status - ट्रैफिक सिग्नल स्थिति दिखाएं
    print(f"\n🚦 Traffic Signal Status:")
    for signal_name, signal_data in traffic_controller.signals.items():
        state = signal_data['current_state'].value
        emergency = " [EMERGENCY]" if signal_data['emergency_override'] else ""
        congestion = " [ADJUSTED]" if signal_data['congestion_adjusted'] else ""
        
        print(f"   {signal_name}: {state}{emergency}{congestion}")
    
    # Performance metrics - प्रदर्शन मेट्रिक्स
    print(f"\n⚡ Performance Metrics:")
    print(f"   Average Processing Time: {total_simulation_time/total_events*1000:.2f}ms per event")
    print(f"   Pattern Detection Rate: {len(cep_engine.pattern_matches)/total_events*100:.2f}%")
    print(f"   Memory Usage: ~{len(cep_engine.window.events)} events in sliding window")
    
    # Business impact - व्यावसायिक प्रभाव
    total_fine_amount = sum(
        pattern.get('fine_amount', 0) 
        for pattern in cep_engine.pattern_matches 
        if pattern['rule_name'] == 'SpeedViolation'
    )
    
    estimated_time_saved = emergency_events * 3  # 3 minutes per emergency corridor
    estimated_fuel_saved = congestion_events * 50  # 50 liters per congestion resolution
    
    print(f"\n💼 Estimated Business Impact:")
    print(f"   🚨 Emergency Response Time Saved: {estimated_time_saved} minutes")
    print(f"   ⛽ Fuel Consumption Reduced: ~{estimated_fuel_saved} liters")
    print(f"   💰 Traffic Fines Collected: ₹{total_fine_amount:,}")
    print(f"   🌱 CO2 Emissions Reduced: ~{estimated_fuel_saved * 2.3:.1f} kg")
    
    print("\n✅ Mumbai Traffic CEP Demo Complete!")
    print("✅ मुंबई ट्रैफिक CEP डेमो पूरा हुआ!")
    
    print("\n📋 Key Takeaways:")
    print("   • CEP enables real-time pattern detection in traffic streams")
    print("   • Sliding window processing handles continuous data efficiently") 
    print("   • Event correlation helps optimize traffic signal timing")
    print("   • Emergency vehicle prioritization improves response times")
    print("   • Speed violation detection enables automated enforcement")

if __name__ == "__main__":
    """
    Run the Complex Event Processing demonstration
    कॉम्प्लेक्स इवेंट प्रोसेसिंग प्रदर्शन चलाएं
    
    This demonstrates:
    यह प्रदर्शित करता है:
    
    1. Complex Event Processing (CEP) patterns - कॉम्प्लेक्स इवेंट प्रोसेसिंग (CEP) पैटर्न
    2. Real-time event stream correlation - रियल-टाइम इवेंट स्ट्रीम सहसंबंध
    3. Sliding window aggregations - स्लाइडिंग विंडो एकीकरण
    4. Pattern-based rule engine - पैटर्न-आधारित नियम इंजन
    5. Event-driven traffic control system - इवेंट-संचालित ट्रैफिक नियंत्रण प्रणाली
    6. Real-time Mumbai traffic management - रियल-टाइम मुंबई ट्रैफिक प्रबंधन
    
    Key learnings:
    मुख्य सीख:
    
    - CEP enables intelligent event correlation across time windows - CEP समय विंडो में बुद्धिमान इवेंट सहसंबंध सक्षम बनाता है
    - Pattern matching detects complex scenarios from simple events - पैटर्न मैचिंग सरल इवेंट्स से जटिल परिस्थितियों का पता लगाती है
    - Sliding windows provide efficient real-time processing - स्लाइडिंग विंडो कुशल रियल-टाइम प्रोसेसिंग प्रदान करती है
    - Event-driven control systems respond faster than polling - इवेंट-संचालित नियंत्रण प्रणाली polling से तेज़ प्रतिक्रिया करती है
    - CEP scales to handle high-volume event streams - CEP उच्च-वॉल्यूम इवेंट स्ट्रीम को संभालने के लिए स्केल करता है
    """
    
    try:
        asyncio.run(demonstrate_complex_event_processing())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user - डेमो उपयोगकर्ता द्वारा बाधित")
    except Exception as e:
        print(f"\n❌ Demo failed with error - डेमो त्रुटि के साथ असफल: {e}")
        raise