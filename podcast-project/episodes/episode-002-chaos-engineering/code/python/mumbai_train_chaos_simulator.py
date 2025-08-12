#!/usr/bin/env python3
"""
Mumbai Local Train Chaos Engineering Simulator
मुंबई लोकल ट्रेन system की chaos engineering के लिए realistic simulator

Indian Context: Western Railway की daily disruptions का chaos testing
Real Example: Monsoon के दौरान train delays और crowd management simulation
"""

import random
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import threading
from queue import Queue, Empty

class TrainLine(Enum):
    WESTERN = "Western"
    CENTRAL = "Central" 
    HARBOUR = "Harbour"

class DisruptionType(Enum):
    SIGNAL_FAILURE = "Signal Failure"
    OVERHEAD_WIRE_DAMAGE = "Overhead Wire Damage"
    WATERLOGGING = "Track Waterlogging"
    CROWD_CONGESTION = "Platform Overcrowding"
    TECHNICAL_SNAG = "Train Technical Problem"
    POWER_OUTAGE = "Power Supply Failure"
    TRACK_MAINTENANCE = "Emergency Track Work"

@dataclass
class Station:
    name: str
    line: TrainLine
    daily_footfall: int
    platform_capacity: int
    current_crowd: int = 0
    
class TrainService:
    def __init__(self, train_id: str, line: TrainLine, route: List[str]):
        self.train_id = train_id
        self.line = line
        self.route = route
        self.current_position = 0
        self.passenger_count = 0
        self.capacity = 1500  # Mumbai local train capacity
        self.status = "RUNNING"
        self.delay_minutes = 0
        self.last_update = datetime.now()

class MumbaiTrainChaosSimulator:
    """
    Mumbai Local Train system का comprehensive chaos engineering simulator
    Real Mumbai Railway scenarios को accurately simulate करता है
    """
    
    def __init__(self):
        # Mumbai local train stations - real routes
        self.western_route = [
            "Churchgate", "Marine Lines", "Charni Road", "Grant Road",
            "Mumbai Central", "Mahalaxmi", "Lower Parel", "Prabhadevi",
            "Dadar", "Matunga Road", "Mahim", "Bandra", "Khar Road",
            "Santacruz", "Vile Parle", "Andheri", "Jogeshwari", "Ram Mandir",
            "Goregaon", "Malad", "Kandivali", "Borivali", "Dahisar", "Virar"
        ]
        
        self.central_route = [
            "CST", "Masjid", "Sandhurst Road", "Dockyard Road", "Reay Road",
            "Cotton Green", "Sewri", "Wadala Road", "Kings Circle", "Mahim",
            "Dadar", "Matunga", "Sion", "Kurla", "Vidyavihar", "Ghatkopar",
            "Vikhroli", "Kanjurmarg", "Bhandup", "Mulund", "Thane", "Kalyan"
        ]
        
        # Initialize stations
        self.stations = self._initialize_stations()
        
        # Active train services
        self.active_trains = []
        
        # System metrics
        self.total_passengers = 0
        self.system_health = 1.0  # 1.0 = perfect, 0.0 = complete failure
        self.disruptions = []
        
        # Chaos engineering parameters
        self.chaos_enabled = False
        self.failure_injection_rate = 0.1  # 10% base failure rate
        
        # Peak hours - Mumbai reality
        self.peak_hours = [(7, 11), (17, 22)]  # Morning और evening rush
        
        # Monsoon season multipliers
        self.monsoon_active = False
        self.monsoon_failure_multiplier = 3.0

    def _initialize_stations(self) -> Dict[str, Station]:
        """Initialize Mumbai local stations with realistic footfall data"""
        stations = {}
        
        # Western line stations
        western_footfalls = {
            "Churchgate": 500000, "Dadar": 450000, "Andheri": 400000,
            "Bandra": 350000, "Borivali": 300000, "Virar": 250000
        }
        
        for station_name in self.western_route:
            footfall = western_footfalls.get(station_name, 100000)  # Default 1L
            stations[station_name] = Station(
                name=station_name,
                line=TrainLine.WESTERN,
                daily_footfall=footfall,
                platform_capacity=2000,  # Typical platform capacity
                current_crowd=random.randint(50, 500)  # Initial crowd
            )
        
        # Central line stations
        central_footfalls = {
            "CST": 600000, "Dadar": 450000, "Kurla": 300000,
            "Thane": 350000, "Kalyan": 200000
        }
        
        for station_name in self.central_route:
            if station_name not in stations:  # Avoid duplicates like Dadar
                footfall = central_footfalls.get(station_name, 80000)
                stations[station_name] = Station(
                    name=station_name,
                    line=TrainLine.CENTRAL,
                    daily_footfall=footfall,
                    platform_capacity=1800,
                    current_crowd=random.randint(40, 400)
                )
        
        return stations

    def start_train_service(self, train_id: str, line: TrainLine, direction: str):
        """Start a new train service on specified line"""
        if line == TrainLine.WESTERN:
            route = self.western_route if direction == "UP" else self.western_route[::-1]
        else:  # CENTRAL
            route = self.central_route if direction == "UP" else self.central_route[::-1]
            
        train = TrainService(train_id, line, route)
        self.active_trains.append(train)
        
        print(f"🚂 Started {train_id} on {line.value} line ({direction} direction)")
        return train

    def inject_chaos_failure(self, disruption_type: DisruptionType, 
                           affected_area: str, severity: float) -> Dict:
        """
        Inject realistic chaos failures in Mumbai local system
        
        Args:
            disruption_type: Type of failure to inject
            affected_area: Station or section affected
            severity: 0.0 to 1.0 (impact level)
        """
        
        disruption = {
            "id": f"CHAOS_{len(self.disruptions)+1}",
            "type": disruption_type.value,
            "affected_area": affected_area,
            "severity": severity,
            "start_time": datetime.now(),
            "estimated_duration": self._calculate_disruption_duration(disruption_type, severity),
            "impact_description": self._get_disruption_impact(disruption_type, severity)
        }
        
        self.disruptions.append(disruption)
        
        print(f"\n⚡ CHAOS INJECTION: {disruption_type.value}")
        print(f"   📍 Location: {affected_area}")
        print(f"   📊 Severity: {severity:.1%}")
        print(f"   ⏱️  Duration: {disruption['estimated_duration']} minutes")
        print(f"   💥 Impact: {disruption['impact_description']}")
        
        # Apply immediate effects
        self._apply_disruption_effects(disruption)
        
        return disruption

    def _calculate_disruption_duration(self, disruption_type: DisruptionType, severity: float) -> int:
        """Calculate realistic duration for different disruption types"""
        
        base_durations = {
            DisruptionType.SIGNAL_FAILURE: 15,      # 15 minutes base
            DisruptionType.OVERHEAD_WIRE_DAMAGE: 45, # 45 minutes base
            DisruptionType.WATERLOGGING: 120,       # 2 hours base (Mumbai monsoon reality)
            DisruptionType.CROWD_CONGESTION: 10,    # 10 minutes base
            DisruptionType.TECHNICAL_SNAG: 30,      # 30 minutes base
            DisruptionType.POWER_OUTAGE: 20,        # 20 minutes base
            DisruptionType.TRACK_MAINTENANCE: 60    # 1 hour base
        }
        
        base_duration = base_durations[disruption_type]
        
        # Severity multiplier
        severity_multiplier = 1.0 + (severity * 2.0)  # 1x to 3x
        
        # Monsoon multiplier - everything takes longer in Mumbai rains
        monsoon_multiplier = 2.0 if self.monsoon_active else 1.0
        
        final_duration = int(base_duration * severity_multiplier * monsoon_multiplier)
        
        return final_duration

    def _get_disruption_impact(self, disruption_type: DisruptionType, severity: float) -> str:
        """Get realistic impact description for disruption"""
        
        if severity < 0.3:
            severity_desc = "Minor"
        elif severity < 0.6:
            severity_desc = "Moderate" 
        else:
            severity_desc = "Severe"
            
        impact_templates = {
            DisruptionType.SIGNAL_FAILURE: f"{severity_desc} delays, trains running 5-15 minutes late",
            DisruptionType.OVERHEAD_WIRE_DAMAGE: f"{severity_desc} service disruption, single line working",
            DisruptionType.WATERLOGGING: f"{severity_desc} flooding, services suspended on affected section",
            DisruptionType.CROWD_CONGESTION: f"{severity_desc} platform congestion, slower boarding",
            DisruptionType.TECHNICAL_SNAG: f"{severity_desc} train breakdown, following services delayed",
            DisruptionType.POWER_OUTAGE: f"{severity_desc} power supply issue, reduced service frequency",
            DisruptionType.TRACK_MAINTENANCE: f"{severity_desc} emergency work, diverted traffic"
        }
        
        return impact_templates[disruption_type]

    def _apply_disruption_effects(self, disruption: Dict):
        """Apply immediate effects of disruption on system"""
        
        disruption_type = disruption["type"]
        severity = disruption["severity"]
        affected_area = disruption["affected_area"]
        
        # Reduce overall system health
        health_reduction = severity * 0.3  # Up to 30% health reduction
        self.system_health = max(0.1, self.system_health - health_reduction)
        
        # Affect trains in the disrupted area
        for train in self.active_trains:
            if affected_area in train.route:
                # Add delays based on disruption type
                if "Signal Failure" in disruption_type:
                    train.delay_minutes += random.randint(5, 15)
                elif "Waterlogging" in disruption_type:
                    train.delay_minutes += random.randint(30, 90)  # Heavy delays in monsoon
                    train.status = "DELAYED"
                elif "Technical" in disruption_type:
                    if random.random() < severity:
                        train.status = "CANCELLED"
                        print(f"   🚫 {train.train_id} cancelled due to technical issues")
                
                print(f"   📉 {train.train_id} affected - Delay: {train.delay_minutes} min")
        
        # Increase crowd at affected stations
        if affected_area in self.stations:
            station = self.stations[affected_area]
            crowd_increase = int(severity * 500)  # Up to 500 extra people
            station.current_crowd = min(station.platform_capacity * 1.5, 
                                      station.current_crowd + crowd_increase)

    def simulate_peak_hour_chaos(self, duration_minutes: int = 60):
        """
        Simulate chaos during Mumbai peak hours
        Peak hour का realistic simulation with multiple failures
        """
        
        print(f"\n🌅 PEAK HOUR CHAOS SIMULATION")
        print(f"   Duration: {duration_minutes} minutes")
        print(f"   Peak multiplier active: 2.5x failure rate")
        print("=" * 50)
        
        # Start multiple train services for peak hour
        peak_trains = [
            ("WESTERN_FAST_UP_1", TrainLine.WESTERN, "UP"),
            ("WESTERN_SLOW_UP_2", TrainLine.WESTERN, "UP"),
            ("WESTERN_FAST_DOWN_3", TrainLine.WESTERN, "DOWN"),
            ("CENTRAL_FAST_UP_4", TrainLine.CENTRAL, "UP"),
            ("CENTRAL_SLOW_DOWN_5", TrainLine.CENTRAL, "DOWN"),
        ]
        
        for train_id, line, direction in peak_trains:
            self.start_train_service(train_id, line, direction)
        
        # Enable chaos engineering
        self.chaos_enabled = True
        original_failure_rate = self.failure_injection_rate
        self.failure_injection_rate = 0.25  # 25% failure rate during peak
        
        start_time = datetime.now()
        simulation_events = []
        
        # Simulate minute by minute
        for minute in range(duration_minutes):
            current_time = start_time + timedelta(minutes=minute)
            
            print(f"\n⏰ Minute {minute+1}: {current_time.strftime('%H:%M')}")
            
            # Random chaos injections during peak hours
            if random.random() < self.failure_injection_rate:
                
                # Select random disruption type weighted by Mumbai reality
                disruption_weights = [
                    (DisruptionType.CROWD_CONGESTION, 0.3),   # Most common
                    (DisruptionType.SIGNAL_FAILURE, 0.25),   # Very common
                    (DisruptionType.TECHNICAL_SNAG, 0.2),    # Common
                    (DisruptionType.POWER_OUTAGE, 0.1),      # Occasional
                    (DisruptionType.WATERLOGGING, 0.1 if self.monsoon_active else 0.05),
                    (DisruptionType.OVERHEAD_WIRE_DAMAGE, 0.05),
                    (DisruptionType.TRACK_MAINTENANCE, 0.05)
                ]
                
                # Weighted random selection
                rand_val = random.random()
                cumulative = 0.0
                selected_disruption = DisruptionType.SIGNAL_FAILURE
                
                for disruption, weight in disruption_weights:
                    cumulative += weight
                    if rand_val <= cumulative:
                        selected_disruption = disruption
                        break
                
                # Random affected area
                all_stations = list(self.stations.keys())
                affected_station = random.choice(all_stations)
                
                # Random severity (peak hours tend to have higher impact)
                severity = 0.3 + random.random() * 0.7  # 0.3 to 1.0
                
                # Inject chaos
                disruption = self.inject_chaos_failure(
                    selected_disruption, affected_station, severity
                )
                simulation_events.append(disruption)
            
            # Update train positions and status
            self._update_train_services()
            
            # Print system status every 10 minutes
            if (minute + 1) % 10 == 0:
                self._print_system_status()
            
            # Small delay for realistic simulation
            time.sleep(0.1)
        
        # Restore original settings
        self.chaos_enabled = False
        self.failure_injection_rate = original_failure_rate
        
        # Final analysis
        self._analyze_simulation_results(simulation_events, duration_minutes)

    def _update_train_services(self):
        """Update all active train services"""
        for train in self.active_trains:
            if train.status == "RUNNING":
                # Simulate train movement
                if random.random() < 0.8:  # 80% chance to move to next station
                    train.current_position = min(
                        len(train.route) - 1,
                        train.current_position + 1
                    )
                
                # Update passenger count based on station
                current_station_name = train.route[train.current_position]
                if current_station_name in self.stations:
                    station = self.stations[current_station_name]
                    
                    # Passengers boarding/alighting
                    boarding = min(station.current_crowd // 4, 
                                 train.capacity - train.passenger_count)
                    alighting = random.randint(0, train.passenger_count // 3)
                    
                    train.passenger_count += boarding - alighting
                    station.current_crowd -= boarding
                    station.current_crowd = max(0, station.current_crowd)

    def _print_system_status(self):
        """Print current system status"""
        print(f"\n📊 SYSTEM STATUS")
        print(f"   🏥 System Health: {self.system_health:.1%}")
        print(f"   🚂 Active Trains: {len([t for t in self.active_trains if t.status != 'CANCELLED'])}")
        print(f"   ⚠️  Active Disruptions: {len(self.disruptions)}")
        
        # Most crowded stations
        crowded_stations = sorted(
            self.stations.values(),
            key=lambda s: s.current_crowd,
            reverse=True
        )[:3]
        
        print(f"   👥 Most Crowded Stations:")
        for station in crowded_stations:
            occupancy = (station.current_crowd / station.platform_capacity) * 100
            print(f"      {station.name}: {station.current_crowd} people ({occupancy:.1f}% capacity)")

    def _analyze_simulation_results(self, events: List[Dict], duration: int):
        """Analyze and report simulation results"""
        
        print(f"\n📈 SIMULATION ANALYSIS")
        print("=" * 50)
        
        # Event type distribution
        event_types = {}
        total_severity = 0.0
        
        for event in events:
            event_type = event["type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
            total_severity += event["severity"]
        
        print(f"📊 Chaos Events Summary:")
        print(f"   Total Events: {len(events)}")
        print(f"   Events per Hour: {len(events) / (duration/60):.1f}")
        print(f"   Average Severity: {total_severity/len(events) if events else 0:.1%}")
        
        # Most common disruptions
        if event_types:
            print(f"\n🔥 Most Common Disruptions:")
            sorted_events = sorted(event_types.items(), key=lambda x: x[1], reverse=True)
            for event_type, count in sorted_events:
                print(f"   {event_type}: {count} times")
        
        # System resilience metrics
        print(f"\n🛡️ System Resilience Metrics:")
        print(f"   Final System Health: {self.system_health:.1%}")
        
        running_trains = len([t for t in self.active_trains if t.status == "RUNNING"])
        cancelled_trains = len([t for t in self.active_trains if t.status == "CANCELLED"])
        
        print(f"   Train Services:")
        print(f"     Running: {running_trains}")
        print(f"     Cancelled: {cancelled_trains}")
        print(f"     Service Availability: {running_trains/(running_trains+cancelled_trains)*100:.1f}%")
        
        # Average delays
        total_delays = sum(train.delay_minutes for train in self.active_trains)
        avg_delay = total_delays / len(self.active_trains) if self.active_trains else 0
        
        print(f"   Average Train Delay: {avg_delay:.1f} minutes")
        
        # Mumbai context insights
        print(f"\n🏙️ Mumbai Local Reality Check:")
        print(f"   💡 Peak hour disruptions are 2.5x more frequent")
        print(f"   💡 Crowd congestion is the #1 cause of delays")
        print(f"   💡 Waterlogging during monsoon can cause 2+ hour delays")
        print(f"   💡 System health below 50% = major service disruption")
        print(f"   💡 Passengers adapt by taking earlier trains during chaos")

def demonstrate_chaos_patterns():
    """Demonstrate different chaos engineering patterns"""
    
    print("🇮🇳 Mumbai Local Train Chaos Engineering Demonstration")
    print("=" * 60)
    
    simulator = MumbaiTrainChaosSimulator()
    
    # Pattern 1: Single Point of Failure Test
    print("\n🎯 Pattern 1: Single Point of Failure")
    print("   Testing Dadar station failure impact (major junction)")
    
    dadar_failure = simulator.inject_chaos_failure(
        DisruptionType.SIGNAL_FAILURE,
        "Dadar",  # Major junction affecting both lines
        0.8  # High severity
    )
    
    # Pattern 2: Cascading Failure Test
    print("\n🎯 Pattern 2: Cascading Failure Chain")
    print("   Simulating monsoon waterlogging chain reaction")
    
    # Enable monsoon conditions
    simulator.monsoon_active = True
    
    # Inject multiple related failures
    simulator.inject_chaos_failure(DisruptionType.WATERLOGGING, "Mahim", 0.7)
    time.sleep(1)
    simulator.inject_chaos_failure(DisruptionType.POWER_OUTAGE, "Bandra", 0.6)
    time.sleep(1)
    simulator.inject_chaos_failure(DisruptionType.CROWD_CONGESTION, "Andheri", 0.9)
    
    # Pattern 3: Peak Hour Stress Test
    print("\n🎯 Pattern 3: Peak Hour Stress Test")
    simulator.simulate_peak_hour_chaos(duration_minutes=20)  # 20-minute simulation
    
    print(f"\n💡 Key Learnings from Chaos Engineering:")
    print(f"   1. Mumbai locals are surprisingly resilient to individual failures")
    print(f"   2. Cascading failures during monsoon cause maximum disruption")
    print(f"   3. Dadar junction failure affects entire network")
    print(f"   4. Crowd management is critical during disruptions")
    print(f"   5. Peak hour failures have 3x impact on passenger experience")

if __name__ == "__main__":
    demonstrate_chaos_patterns()