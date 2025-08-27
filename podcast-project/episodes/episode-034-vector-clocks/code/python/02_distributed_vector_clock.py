#!/usr/bin/env python3
"""
Episode 34: Vector Clocks - Distributed Vector Clock Implementation
Mumbai Local Train Coordination System

Demonstrates: Vector clocks in distributed train coordination system
Context: Western Line, Central Line, Harbor Line train coordination
"""

import json
import time
import threading
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TrainEvent:
    """Event happening in Mumbai Local Train System"""
    train_id: str
    station: str
    event_type: str  # ARRIVAL, DEPARTURE, DELAY
    timestamp: datetime
    vector_clock: Dict[str, int]
    passenger_count: int = 0

class MumbaiTrainVectorClock:
    """
    Vector Clock implementation for Mumbai Train System
    
    Har train line ka apna vector clock hai:
    - Western Line: WR_001, WR_002, ...
    - Central Line: CR_001, CR_002, ...
    - Harbor Line: HR_001, HR_002, ...
    """
    
    def __init__(self, node_id: str, railway_nodes: List[str]):
        self.node_id = node_id
        self.clock = {node: 0 for node in railway_nodes}
        self.events_log = []
        self.lock = threading.Lock()
        
    def local_event(self, station: str, event_type: str, passenger_count: int = 0):
        """
        Local event - train reaches station
        Example: Andheri station pe train arrival
        """
        with self.lock:
            # Increment own clock
            self.clock[self.node_id] += 1
            
            event = TrainEvent(
                train_id=self.node_id,
                station=station,
                event_type=event_type,
                timestamp=datetime.now(),
                vector_clock=self.clock.copy(),
                passenger_count=passenger_count
            )
            
            self.events_log.append(event)
            print(f"🚊 {self.node_id} | {event_type} at {station} | Clock: {self.clock}")
            return event
    
    def receive_event(self, received_event: TrainEvent):
        """
        Receive event from another train
        Example: Information about delay from another train
        """
        with self.lock:
            # Update clock using max rule
            for node in self.clock:
                if node in received_event.vector_clock:
                    self.clock[node] = max(self.clock[node], received_event.vector_clock[node])
            
            # Increment own clock
            self.clock[self.node_id] += 1
            
            self.events_log.append(received_event)
            print(f"📨 {self.node_id} received from {received_event.train_id}: {received_event.event_type}")
            print(f"   Updated Clock: {self.clock}")
    
    def send_event(self, event: TrainEvent):
        """Send event to other trains - message passing simulation"""
        with self.lock:
            # Include current vector clock in the event
            event.vector_clock = self.clock.copy()
            return event
    
    def compare_events(self, event1: TrainEvent, event2: TrainEvent) -> str:
        """
        Compare two events using vector clocks
        Returns: 'before', 'after', 'concurrent', or 'same'
        """
        clock1 = event1.vector_clock
        clock2 = event2.vector_clock
        
        # Check if event1 happened before event2
        before = all(clock1.get(node, 0) <= clock2.get(node, 0) for node in clock1)
        strictly_before = before and any(clock1.get(node, 0) < clock2.get(node, 0) for node in clock1)
        
        # Check if event2 happened before event1
        after = all(clock2.get(node, 0) <= clock1.get(node, 0) for node in clock2)
        strictly_after = after and any(clock2.get(node, 0) < clock1.get(node, 0) for node in clock2)
        
        if strictly_before:
            return 'before'
        elif strictly_after:
            return 'after'
        elif clock1 == clock2:
            return 'same'
        else:
            return 'concurrent'

class MumbaiRailwayCoordination:
    """
    Mumbai Railway Network Coordination using Vector Clocks
    Simulates Western, Central, and Harbor lines coordination
    """
    
    def __init__(self):
        self.lines = ['WR_VIRAR_FAST', 'CR_KALYAN_FAST', 'HR_PANVEL_LOCAL']
        self.trains = {}
        self.coordination_log = []
        
        # Initialize trains with vector clocks
        for train_id in self.lines:
            self.trains[train_id] = MumbaiTrainVectorClock(train_id, self.lines)
    
    def simulate_rush_hour(self):
        """
        Simulate morning rush hour - 8 AM to 10 AM
        Multiple events happening across different lines
        """
        print("🌅 Mumbai Morning Rush Hour Simulation")
        print("=" * 50)
        
        # Event 1: Virar Fast arrives at Andheri (8:15 AM)
        event1 = self.trains['WR_VIRAR_FAST'].local_event('ANDHERI', 'ARRIVAL', 850)
        
        # Event 2: Kalyan Fast arrives at Ghatkopar (8:16 AM)  
        event2 = self.trains['CR_KALYAN_FAST'].local_event('GHATKOPAR', 'ARRIVAL', 920)
        
        # Event 3: Panvel Local reports delay
        event3 = self.trains['HR_PANVEL_LOCAL'].local_event('VASHI', 'DELAY', 600)
        
        # Trains communicate with each other
        print("\n📡 Inter-train Communication:")
        self.trains['CR_KALYAN_FAST'].receive_event(event1)
        self.trains['HR_PANVEL_LOCAL'].receive_event(event2)
        self.trains['WR_VIRAR_FAST'].receive_event(event3)
        
        # Event 4: After receiving delay info, Virar Fast adjusts speed
        event4 = self.trains['WR_VIRAR_FAST'].local_event('BANDRA', 'SPEED_ADJUSTMENT', 780)
        
        print("\n🔍 Event Ordering Analysis:")
        print(f"Event 1 vs Event 2: {self.trains['WR_VIRAR_FAST'].compare_events(event1, event2)}")
        print(f"Event 2 vs Event 3: {self.trains['CR_KALYAN_FAST'].compare_events(event2, event3)}")
        print(f"Event 3 vs Event 4: {self.trains['HR_PANVEL_LOCAL'].compare_events(event3, event4)}")
    
    def analyze_causality(self):
        """Analyze causal relationships in the train system"""
        print("\n🔗 Causality Analysis:")
        
        for train_id, train in self.trains.items():
            print(f"\n{train_id} Event Timeline:")
            for i, event in enumerate(train.events_log):
                print(f"  {i+1}. {event.timestamp.strftime('%H:%M:%S')} - "
                      f"{event.event_type} at {event.station} | Clock: {event.vector_clock}")
    
    def detect_concurrent_events(self):
        """Find events that happened concurrently (no causal relationship)"""
        print("\n⏱️  Concurrent Events Detection:")
        
        all_events = []
        for train in self.trains.values():
            all_events.extend(train.events_log)
        
        concurrent_pairs = []
        for i, event1 in enumerate(all_events):
            for j, event2 in enumerate(all_events[i+1:], i+1):
                comparison = self.trains[event1.train_id].compare_events(event1, event2)
                if comparison == 'concurrent':
                    concurrent_pairs.append((event1, event2))
        
        for event1, event2 in concurrent_pairs:
            print(f"  • {event1.train_id} {event1.event_type} || {event2.train_id} {event2.event_type}")

def production_example_zomato_delivery():
    """
    Production Example: Zomato Delivery Coordination
    Multiple delivery partners coordinating using vector clocks
    """
    print("\n" + "="*60)
    print("🍔 PRODUCTION EXAMPLE: Zomato Delivery Coordination")
    print("="*60)
    
    delivery_partners = ['PARTNER_MUMBAI_001', 'PARTNER_MUMBAI_002', 'PARTNER_MUMBAI_003']
    partners = {}
    
    for partner_id in delivery_partners:
        partners[partner_id] = MumbaiTrainVectorClock(partner_id, delivery_partners)
    
    # Order coordination scenario
    print("📱 Order #ZOM12345 coordination:")
    
    # Partner 1 picks up order from restaurant
    event1 = partners['PARTNER_MUMBAI_001'].local_event('RESTAURANT_PICKUP', 'ORDER_COLLECTED', 1)
    
    # Partner 2 gets notification about traffic jam
    event2 = partners['PARTNER_MUMBAI_002'].local_event('TRAFFIC_UPDATE', 'JAM_DETECTED', 0)
    
    # Partners share information
    partners['PARTNER_MUMBAI_001'].receive_event(event2)
    
    # Partner 1 chooses alternate route based on traffic info
    event3 = partners['PARTNER_MUMBAI_001'].local_event('ROUTE_CHANGE', 'ALTERNATE_PATH', 1)
    
    # Partner 1 delivers order
    event4 = partners['PARTNER_MUMBAI_001'].local_event('CUSTOMER_DELIVERY', 'ORDER_DELIVERED', 1)
    
    print(f"\nCausality: Traffic jam vs Route change = {partners['PARTNER_MUMBAI_001'].compare_events(event2, event3)}")
    print(f"Causality: Pickup vs Delivery = {partners['PARTNER_MUMBAI_001'].compare_events(event1, event4)}")

if __name__ == "__main__":
    # Mumbai Railway Coordination Simulation
    railway = MumbaiRailwayCoordination()
    railway.simulate_rush_hour()
    railway.analyze_causality()
    railway.detect_concurrent_events()
    
    # Production example
    production_example_zomato_delivery()
    
    print("\n✅ Vector Clock simulation complete!")
    print("💡 Key Learning: Vector clocks help establish causal relationships")
    print("   in distributed systems without relying on synchronized physical time")