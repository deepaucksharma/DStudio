#!/usr/bin/env python3
"""
CAP Theorem Simulator - Episode 4
व्यावहारिक CAP theorem demonstration

यह सिम्युलेटर दिखाता है कि कैसे distributed systems में
Consistency, Availability, और Partition tolerance के बीच trade-offs होते हैं।

Indian Context: IRCTC ticket booking vs UPI payment systems
IRCTC (CP): High consistency जरूरी है - duplicate bookings नहीं हो सकते
UPI (AP): High availability चाहिए - payment fail नहीं होना चाहिए
"""

import time
import random
import threading
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json

class PartitionState(Enum):
    """Network partition ki state"""
    HEALTHY = "healthy"          # सब nodes connected हैं
    PARTITIONED = "partitioned"  # Network split हो गया है
    RECOVERING = "recovering"    # Partition heal हो रहा है

class ConsistencyModel(Enum):
    """Consistency levels जैसे real production में होते हैं"""
    STRONG = "strong"           # IRCTC ticket booking
    EVENTUAL = "eventual"       # WhatsApp message delivery  
    WEAK = "weak"              # Live cricket score updates

@dataclass
class Node:
    """Distributed system में एक node का representation"""
    node_id: str
    data: Dict[str, any] = None
    is_available: bool = True
    partition_group: int = 0    # कौन से partition में है
    last_heartbeat: float = 0
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        self.last_heartbeat = time.time()

class CAPSimulator:
    """
    CAP Theorem का practical demonstration
    
    Real scenarios:
    - IRCTC: Consistency > Availability (no double booking)
    - Paytm: Availability > Consistency (payment should go through)
    - WhatsApp: Partition tolerance जरूरी (mobile networks unreliable)
    """
    
    def __init__(self, num_nodes: int = 5):
        self.nodes: List[Node] = []
        self.partition_state = PartitionState.HEALTHY
        self.consistency_model = ConsistencyModel.STRONG
        self.total_requests = 0
        self.successful_reads = 0
        self.successful_writes = 0
        self.consistency_violations = 0
        self.availability_failures = 0
        self.partition_events = 0
        
        # Initialize nodes - जैसे real data centers में होते हैं
        for i in range(num_nodes):
            node = Node(
                node_id=f"node-{i}",
                data={"user_balance": {}, "ticket_bookings": {}},
                partition_group=0
            )
            self.nodes.append(node)
        
        print(f"🚀 CAP Simulator initialized with {num_nodes} nodes")
        print("💡 Indian context examples:")
        print("   - IRCTC (CP): Consistency > Availability")
        print("   - UPI (AP): Availability > Partition tolerance")
        print("   - WhatsApp (PA): Partition tolerance + Availability")

    def simulate_network_partition(self, duration: int = 10):
        """
        Network partition simulation - जैसे ISP failure में होता है
        
        Real example: जब Jio network down हो जाता है तो
        कुछ users Airtel से connect होते हैं, कुछ BSNL से
        """
        print(f"\n🔥 NETWORK PARTITION SIMULATED for {duration}s")
        print("📱 Scenario: Jio network failure - users switching to Airtel/BSNL")
        
        self.partition_state = PartitionState.PARTITIONED
        self.partition_events += 1
        
        # Split nodes into different partition groups
        mid_point = len(self.nodes) // 2
        for i, node in enumerate(self.nodes):
            node.partition_group = 0 if i < mid_point else 1
            print(f"   Node {node.node_id}: Partition Group {node.partition_group}")
        
        # Simulate partition duration
        time.sleep(duration)
        
        # Heal partition
        print("🔄 Network healing - ISP restored connection")
        self.partition_state = PartitionState.RECOVERING
        for node in self.nodes:
            node.partition_group = 0  # All nodes back to same group
        
        time.sleep(2)  # Recovery time
        self.partition_state = PartitionState.HEALTHY
        print("✅ Network partition healed - all nodes connected")

    def read_operation(self, key: str, user_id: str = "user123") -> Tuple[bool, any]:
        """
        Read operation with different consistency guarantees
        
        IRCTC example: Checking available seats
        UPI example: Checking account balance
        """
        self.total_requests += 1
        
        if self.consistency_model == ConsistencyModel.STRONG:
            return self._strong_consistent_read(key, user_id)
        elif self.consistency_model == ConsistencyModel.EVENTUAL:
            return self._eventually_consistent_read(key, user_id)
        else:  # WEAK
            return self._weak_consistent_read(key, user_id)

    def write_operation(self, key: str, value: any, user_id: str = "user123") -> bool:
        """
        Write operation with CAP trade-offs
        
        IRCTC example: Booking a train ticket
        Paytm example: Transferring money
        """
        self.total_requests += 1
        
        if self.consistency_model == ConsistencyModel.STRONG:
            return self._strong_consistent_write(key, value, user_id)
        elif self.consistency_model == ConsistencyModel.EVENTUAL:
            return self._eventually_consistent_write(key, value, user_id)
        else:  # WEAK
            return self._weak_consistent_write(key, value, user_id)

    def _strong_consistent_read(self, key: str, user_id: str) -> Tuple[bool, any]:
        """
        Strong consistency read - IRCTC style
        सभी nodes से same data मिलना चाहिए
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        if len(available_nodes) == 0:
            self.availability_failures += 1
            return False, None
        
        # Check if we have majority of nodes available
        if len(available_nodes) < len(self.nodes) // 2 + 1:
            if self.partition_state == PartitionState.PARTITIONED:
                print(f"❌ Strong consistency read failed - no quorum available")
                self.availability_failures += 1
                return False, None
        
        # Read from majority of nodes
        values = []
        for node in available_nodes[:len(self.nodes)//2 + 1]:
            if key in node.data:
                values.append(node.data[key])
        
        if not values:
            self.successful_reads += 1
            return True, None
        
        # Check consistency - सभी values same होनी चाहिए
        first_value = values[0]
        if not all(v == first_value for v in values):
            self.consistency_violations += 1
            print(f"⚠️ Consistency violation detected for key: {key}")
        
        self.successful_reads += 1
        return True, first_value

    def _eventually_consistent_read(self, key: str, user_id: str) -> Tuple[bool, any]:
        """
        Eventually consistent read - WhatsApp message style
        कोई भी available node से read कर सकते हैं
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        if not available_nodes:
            self.availability_failures += 1
            return False, None
        
        # Read from any available node (highest availability)
        node = random.choice(available_nodes)
        value = node.data.get(key)
        
        self.successful_reads += 1
        return True, value

    def _weak_consistent_read(self, key: str, user_id: str) -> Tuple[bool, any]:
        """
        Weak consistency read - Live cricket score style
        Latest available data, consistency not guaranteed
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        if not available_nodes:
            self.availability_failures += 1
            return False, None
        
        # Just return from first available node
        node = available_nodes[0]
        value = node.data.get(key)
        
        self.successful_reads += 1
        return True, value

    def _strong_consistent_write(self, key: str, value: any, user_id: str) -> bool:
        """
        Strong consistency write - IRCTC ticket booking
        Majority of nodes must acknowledge write
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        # Need majority for strong consistency
        required_nodes = len(self.nodes) // 2 + 1
        
        if len(available_nodes) < required_nodes:
            print(f"❌ Strong write failed - only {len(available_nodes)}/{required_nodes} nodes available")
            self.availability_failures += 1
            return False
        
        # Write to majority of nodes
        successful_writes = 0
        for node in available_nodes[:required_nodes]:
            try:
                node.data[key] = value
                node.last_heartbeat = time.time()
                successful_writes += 1
            except Exception as e:
                print(f"Write failed on node {node.node_id}: {e}")
        
        if successful_writes >= required_nodes:
            self.successful_writes += 1
            print(f"✅ Strong write successful: {key} = {value}")
            return True
        else:
            self.availability_failures += 1
            return False

    def _eventually_consistent_write(self, key: str, value: any, user_id: str) -> bool:
        """
        Eventually consistent write - Social media post
        Write to available nodes, propagate later
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        if not available_nodes:
            self.availability_failures += 1
            return False
        
        # Write to at least one node for availability
        successful_writes = 0
        for node in available_nodes:
            try:
                node.data[key] = value
                node.last_heartbeat = time.time()
                successful_writes += 1
            except Exception:
                continue
        
        if successful_writes > 0:
            self.successful_writes += 1
            print(f"✅ Eventually consistent write: {key} = {value}")
            
            # Async propagation to other nodes (simplified)
            self._async_propagate(key, value)
            return True
        else:
            self.availability_failures += 1
            return False

    def _weak_consistent_write(self, key: str, value: any, user_id: str) -> bool:
        """
        Weak consistency write - Live data updates
        Best effort write
        """
        available_nodes = [n for n in self.nodes if n.is_available]
        
        if not available_nodes:
            self.availability_failures += 1
            return False
        
        # Write to first available node
        node = available_nodes[0]
        node.data[key] = value
        node.last_heartbeat = time.time()
        
        self.successful_writes += 1
        return True

    def _async_propagate(self, key: str, value: any):
        """
        Background propagation for eventual consistency
        Real में यह gossip protocol या async replication होता है
        """
        def propagate():
            time.sleep(0.1)  # Simulate network delay
            for node in self.nodes:
                if node.is_available:
                    node.data[key] = value
        
        thread = threading.Thread(target=propagate)
        thread.daemon = True
        thread.start()

    def simulate_node_failure(self, node_id: str):
        """
        Simulate node failure - जैसे AWS EC2 instance crash
        """
        for node in self.nodes:
            if node.node_id == node_id:
                node.is_available = False
                print(f"💥 Node {node_id} failed (simulating EC2 instance crash)")
                break

    def recover_node(self, node_id: str):
        """
        Recover failed node - जैसे auto-scaling में नया instance आता है
        """
        for node in self.nodes:
            if node.node_id == node_id:
                node.is_available = True
                print(f"🔄 Node {node_id} recovered (new EC2 instance launched)")
                break

    def run_benchmark(self, duration: int = 30, operations_per_second: int = 10):
        """
        Comprehensive benchmark - Real production load simulation
        """
        print(f"\n🏁 Starting CAP benchmark for {duration}s at {operations_per_second} ops/sec")
        print(f"Consistency model: {self.consistency_model.value}")
        
        start_time = time.time()
        
        def run_operations():
            while time.time() - start_time < duration:
                # Mix of read/write operations
                if random.random() < 0.7:  # 70% reads, 30% writes
                    key = f"balance_user_{random.randint(1, 1000)}"
                    success, value = self.read_operation(key)
                else:
                    key = f"balance_user_{random.randint(1, 1000)}"
                    value = random.randint(100, 10000)
                    success = self.write_operation(key, value)
                
                time.sleep(1.0 / operations_per_second)
        
        # Run operations in background
        op_thread = threading.Thread(target=run_operations)
        op_thread.start()
        
        # Simulate random failures during benchmark
        failure_thread = threading.Thread(target=self._simulate_random_failures, args=(duration,))
        failure_thread.start()
        
        op_thread.join()
        failure_thread.join()
        
        self.print_benchmark_results()

    def _simulate_random_failures(self, duration: int):
        """
        Random failure injection during benchmark
        """
        end_time = time.time() + duration
        while time.time() < end_time:
            time.sleep(random.uniform(5, 15))  # Random failure intervals
            
            failure_type = random.choice(['node_failure', 'network_partition'])
            
            if failure_type == 'node_failure':
                available_nodes = [n for n in self.nodes if n.is_available]
                if available_nodes:
                    node = random.choice(available_nodes)
                    self.simulate_node_failure(node.node_id)
                    time.sleep(3)  # Failure duration
                    self.recover_node(node.node_id)
            
            elif failure_type == 'network_partition':
                self.simulate_network_partition(duration=5)

    def print_benchmark_results(self):
        """
        Detailed benchmark results - Production metrics style
        """
        print("\n" + "="*60)
        print("📊 CAP THEOREM BENCHMARK RESULTS")
        print("="*60)
        
        total_ops = self.successful_reads + self.successful_writes + self.availability_failures
        availability_pct = (self.successful_reads + self.successful_writes) / total_ops * 100 if total_ops > 0 else 0
        
        print(f"Total Operations: {total_ops}")
        print(f"Successful Reads: {self.successful_reads}")
        print(f"Successful Writes: {self.successful_writes}")
        print(f"Availability Failures: {self.availability_failures}")
        print(f"Consistency Violations: {self.consistency_violations}")
        print(f"Network Partition Events: {self.partition_events}")
        print(f"Overall Availability: {availability_pct:.2f}%")
        
        print("\n🎯 CAP Trade-off Analysis:")
        if self.consistency_model == ConsistencyModel.STRONG:
            print("✅ High Consistency (IRCTC style)")
            print("❌ Lower Availability during partitions")
            print("⚖️  Trade-off: CA > P")
        elif self.consistency_model == ConsistencyModel.EVENTUAL:
            print("✅ High Availability (WhatsApp style)")
            print("⚠️  Eventual Consistency")
            print("⚖️  Trade-off: AP > C")
        else:
            print("✅ Maximum Availability (Live score style)")
            print("❌ Weak Consistency guarantees")
            print("⚖️  Trade-off: A > CP")
        
        print(f"\n💰 Indian Context Analysis:")
        print(f"IRCTC booking success rate: {(self.successful_writes/total_ops*100):.1f}%")
        print(f"UPI payment availability: {availability_pct:.1f}%")
        print(f"WhatsApp message delivery: {((total_ops-self.availability_failures)/total_ops*100):.1f}%")

def main():
    """
    Main demonstration - Real scenarios from Indian tech companies
    """
    print("🇮🇳 CAP Theorem Simulator - Indian Tech Context")
    print("=" * 50)
    
    # Scenario 1: IRCTC Ticket Booking (Strong Consistency)
    print("\n🚆 SCENARIO 1: IRCTC Ticket Booking System")
    print("Requirement: Strong consistency (no double booking)")
    
    irctc_sim = CAPSimulator(num_nodes=5)
    irctc_sim.consistency_model = ConsistencyModel.STRONG
    
    # Simulate ticket booking
    success = irctc_sim.write_operation("train_12345_seat_A1", {"user": "rajesh_mumbai", "status": "booked"})
    print(f"Ticket booking result: {'SUCCESS' if success else 'FAILED'}")
    
    # Simulate reading seat availability
    success, seat_info = irctc_sim.read_operation("train_12345_seat_A1")
    print(f"Seat check result: {seat_info if success else 'UNAVAILABLE'}")
    
    # Simulate network issues (partition)
    partition_thread = threading.Thread(target=irctc_sim.simulate_network_partition, args=(5,))
    partition_thread.start()
    
    time.sleep(1)  # Let partition start
    success = irctc_sim.write_operation("train_12345_seat_B2", {"user": "priya_delhi", "status": "booked"})
    print(f"Booking during partition: {'SUCCESS' if success else 'FAILED'}")
    
    partition_thread.join()
    
    # Scenario 2: UPI Payment System (High Availability)
    print("\n💳 SCENARIO 2: UPI Payment System")
    print("Requirement: High availability (payment must go through)")
    
    upi_sim = CAPSimulator(num_nodes=3)
    upi_sim.consistency_model = ConsistencyModel.EVENTUAL
    
    # Simulate payment
    success = upi_sim.write_operation("payment_txn_123", {"amount": 500, "from": "alice_paytm", "to": "bob_phonepe"})
    print(f"Payment result: {'SUCCESS' if success else 'FAILED'}")
    
    # Run comprehensive benchmark
    print("\n🔥 Running comprehensive benchmark...")
    upi_sim.run_benchmark(duration=10, operations_per_second=5)
    
    # Scenario 3: WhatsApp Message Delivery (Partition Tolerance)
    print("\n📱 SCENARIO 3: WhatsApp Message System")
    print("Requirement: Work during network partitions")
    
    whatsapp_sim = CAPSimulator(num_nodes=4)
    whatsapp_sim.consistency_model = ConsistencyModel.EVENTUAL
    
    # Messages should work even during partition
    partition_thread = threading.Thread(target=whatsapp_sim.simulate_network_partition, args=(3,))
    partition_thread.start()
    
    time.sleep(0.5)
    success = whatsapp_sim.write_operation("msg_group_123", {"sender": "rohit", "text": "Kya haal hai?"})
    print(f"Message during partition: {'DELIVERED' if success else 'FAILED'}")
    
    partition_thread.join()
    
    print("\n✅ CAP Theorem demonstration complete!")
    print("Key learnings:")
    print("1. IRCTC needs CP (Consistency + Partition tolerance)")
    print("2. UPI needs AP (Availability + Partition tolerance)")
    print("3. WhatsApp needs AP with eventual consistency")
    print("4. You cannot have all three (C+A+P) simultaneously!")

if __name__ == "__main__":
    main()