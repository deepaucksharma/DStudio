#!/usr/bin/env python3
"""
Quorum-Based Replication System - Episode 4
व्यावहारिक Quorum replication का implementation

यह सिस्टम दिखाता है कि कैसे R + W > N formula का उपयोग करके
tunable consistency achieve कर सकते हैं।

Indian Context: 
- Flipkart inventory system (strong consistency needed)
- Zomato restaurant availability (eventual consistency OK)
- IRCTC seat booking (strict quorum needed)

Quorum Rules:
- N = Total replicas (जैसे 5 data centers)
- R = Read quorum (कितने से read करना है)
- W = Write quorum (कितने में write करना है)
- R + W > N ensures strong consistency
"""

import time
import random
import threading
from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class ReplicaStatus(Enum):
    """Replica की current state"""
    HEALTHY = "healthy"        # Normal operation
    SLOW = "slow"              # High latency but working
    FAILED = "failed"          # Complete failure
    RECOVERING = "recovering"   # Coming back online

class ConsistencyLevel(Enum):
    """Different consistency levels"""
    ONE = "one"               # Fast but weak (R=1, W=1)
    QUORUM = "quorum"         # Balanced (R=N/2+1, W=N/2+1)
    ALL = "all"               # Strong but slow (R=N, W=N)

@dataclass
class WriteOperation:
    """Write operation का metadata"""
    key: str
    value: any
    timestamp: float
    version: int
    client_id: str
    operation_id: str

@dataclass
class ReadResult:
    """Read operation का result"""
    value: any
    version: int
    timestamp: float
    replica_id: str
    consistent: bool = True

@dataclass 
class Replica:
    """एक replica node की complete information"""
    replica_id: str
    data: Dict[str, any] = field(default_factory=dict)
    versions: Dict[str, int] = field(default_factory=dict)  
    timestamps: Dict[str, float] = field(default_factory=dict)
    status: ReplicaStatus = ReplicaStatus.HEALTHY
    location: str = "Mumbai"  # Data center location
    latency_ms: int = 50      # Network latency
    last_heartbeat: float = field(default_factory=time.time)
    pending_writes: List[WriteOperation] = field(default_factory=list)
    
    def write_data(self, key: str, value: any, version: int, timestamp: float) -> bool:
        """
        Data write operation with version control
        """
        try:
            # Simulate network latency
            time.sleep(self.latency_ms / 1000.0)
            
            if self.status == ReplicaStatus.FAILED:
                return False
                
            # Version check for consistency
            current_version = self.versions.get(key, 0)
            if version < current_version:
                print(f"⚠️ Version conflict at {self.replica_id}: current={current_version}, incoming={version}")
                return False
            
            # Write data
            self.data[key] = value
            self.versions[key] = version
            self.timestamps[key] = timestamp
            self.last_heartbeat = time.time()
            
            print(f"✅ Write successful at {self.replica_id}: {key}={value} (v{version})")
            return True
            
        except Exception as e:
            print(f"❌ Write failed at {self.replica_id}: {e}")
            return False
    
    def read_data(self, key: str) -> Optional[ReadResult]:
        """
        Data read operation
        """
        try:
            # Simulate network latency
            time.sleep(self.latency_ms / 1000.0)
            
            if self.status == ReplicaStatus.FAILED:
                return None
            
            if key not in self.data:
                return ReadResult(
                    value=None,
                    version=0,
                    timestamp=0,
                    replica_id=self.replica_id
                )
            
            return ReadResult(
                value=self.data[key],
                version=self.versions.get(key, 1),
                timestamp=self.timestamps.get(key, time.time()),
                replica_id=self.replica_id
            )
            
        except Exception as e:
            print(f"❌ Read failed at {self.replica_id}: {e}")
            return None

class QuorumReplicationSystem:
    """
    Production-ready Quorum Replication System
    
    Real usage examples:
    - Flipkart product inventory (N=5, R=3, W=3)
    - Zomato restaurant menu (N=3, R=1, W=2) 
    - IRCTC ticket availability (N=7, R=4, W=4)
    """
    
    def __init__(self, replicas: List[str], consistency_level: ConsistencyLevel = ConsistencyLevel.QUORUM):
        self.replicas: Dict[str, Replica] = {}
        self.consistency_level = consistency_level
        self.N = len(replicas)  # Total replicas
        self.version_counter = 0
        self.operation_counter = 0
        
        # Initialize replicas with Indian data center locations
        indian_locations = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Pune", "Kolkata"]
        
        for i, replica_id in enumerate(replicas):
            location = indian_locations[i % len(indian_locations)]
            latency = random.randint(20, 100)  # Realistic India latency
            
            replica = Replica(
                replica_id=replica_id,
                location=location,
                latency_ms=latency
            )
            self.replicas[replica_id] = replica
        
        # Set quorum sizes based on consistency level
        self._set_quorum_sizes()
        
        print(f"🚀 Quorum Replication System initialized")
        print(f"📊 N={self.N}, R={self.R}, W={self.W}")
        print(f"🔒 Consistency Level: {consistency_level.value}")
        print(f"🌍 Replicas across India:")
        for replica in self.replicas.values():
            print(f"   {replica.replica_id}: {replica.location} ({replica.latency_ms}ms)")

    def _set_quorum_sizes(self):
        """Set R and W based on consistency level"""
        if self.consistency_level == ConsistencyLevel.ONE:
            self.R = 1
            self.W = 1
        elif self.consistency_level == ConsistencyLevel.ALL:
            self.R = self.N
            self.W = self.N
        else:  # QUORUM
            self.R = self.N // 2 + 1
            self.W = self.N // 2 + 1
        
        # Verify R + W > N for strong consistency
        if self.R + self.W > self.N:
            print(f"✅ Strong consistency guaranteed: R({self.R}) + W({self.W}) > N({self.N})")
        else:
            print(f"⚠️ Weak consistency: R({self.R}) + W({self.W}) ≤ N({self.N})")

    def write(self, key: str, value: any, client_id: str = "client_mumbai") -> Tuple[bool, Dict]:
        """
        Quorum write operation
        
        Example: Flipkart updating product inventory
        - Must succeed on W replicas to be considered successful
        - Version control prevents conflicts
        """
        self.operation_counter += 1
        self.version_counter += 1
        
        operation_id = f"write_{self.operation_counter}_{int(time.time())}"
        timestamp = time.time()
        
        print(f"\n📝 WRITE Operation: {key} = {value}")
        print(f"🎯 Target: Write to {self.W}/{self.N} replicas")
        print(f"🏪 Context: Flipkart inventory update")
        
        write_op = WriteOperation(
            key=key,
            value=value,
            timestamp=timestamp,
            version=self.version_counter,
            client_id=client_id,
            operation_id=operation_id
        )
        
        # Get healthy replicas
        healthy_replicas = [r for r in self.replicas.values() 
                           if r.status in [ReplicaStatus.HEALTHY, ReplicaStatus.SLOW]]
        
        if len(healthy_replicas) < self.W:
            print(f"❌ Write failed: Only {len(healthy_replicas)}/{self.W} healthy replicas")
            return False, {
                "operation_id": operation_id,
                "success": False,
                "reason": "insufficient_replicas",
                "healthy_count": len(healthy_replicas),
                "required": self.W
            }
        
        # Parallel write to replicas
        successful_writes = 0
        write_results = []
        
        with ThreadPoolExecutor(max_workers=self.N) as executor:
            # Submit write operations
            future_to_replica = {}
            for replica in healthy_replicas[:self.W + 2]:  # Extra replicas for redundancy
                future = executor.submit(
                    replica.write_data, 
                    key, value, self.version_counter, timestamp
                )
                future_to_replica[future] = replica.replica_id
            
            # Collect results as they complete
            for future in as_completed(future_to_replica, timeout=5.0):
                replica_id = future_to_replica[future]
                try:
                    success = future.result()
                    write_results.append({
                        "replica_id": replica_id,
                        "success": success,
                        "location": self.replicas[replica_id].location
                    })
                    if success:
                        successful_writes += 1
                        # Early return if we have enough successful writes
                        if successful_writes >= self.W:
                            break
                except Exception as e:
                    print(f"Write timeout/error for {replica_id}: {e}")
                    write_results.append({
                        "replica_id": replica_id,
                        "success": False,
                        "error": str(e)
                    })
        
        # Check if write was successful
        write_successful = successful_writes >= self.W
        
        if write_successful:
            print(f"✅ Write successful: {successful_writes}/{self.W} replicas confirmed")
            print(f"💾 Version {self.version_counter} committed")
        else:
            print(f"❌ Write failed: Only {successful_writes}/{self.W} replicas confirmed")
        
        return write_successful, {
            "operation_id": operation_id,
            "success": write_successful,
            "successful_writes": successful_writes,
            "required_writes": self.W,
            "version": self.version_counter,
            "write_results": write_results,
            "latency_ms": (time.time() - timestamp) * 1000
        }

    def read(self, key: str, client_id: str = "client_delhi") -> Tuple[bool, any, Dict]:
        """
        Quorum read operation
        
        Example: IRCTC checking seat availability
        - Must read from R replicas
        - Return most recent version if conflicts exist
        """
        self.operation_counter += 1
        operation_id = f"read_{self.operation_counter}_{int(time.time())}"
        start_time = time.time()
        
        print(f"\n📖 READ Operation: {key}")
        print(f"🎯 Target: Read from {self.R}/{self.N} replicas")
        print(f"🚆 Context: IRCTC seat availability check")
        
        # Get healthy replicas
        healthy_replicas = [r for r in self.replicas.values() 
                           if r.status in [ReplicaStatus.HEALTHY, ReplicaStatus.SLOW]]
        
        if len(healthy_replicas) < self.R:
            print(f"❌ Read failed: Only {len(healthy_replicas)}/{self.R} healthy replicas")
            return False, None, {
                "operation_id": operation_id,
                "success": False,
                "reason": "insufficient_replicas"
            }
        
        # Parallel read from replicas
        read_results = []
        
        with ThreadPoolExecutor(max_workers=self.N) as executor:
            # Submit read operations  
            future_to_replica = {}
            for replica in healthy_replicas[:self.R + 1]:  # Extra replica for redundancy
                future = executor.submit(replica.read_data, key)
                future_to_replica[future] = replica.replica_id
            
            # Collect results
            for future in as_completed(future_to_replica, timeout=3.0):
                replica_id = future_to_replica[future]
                try:
                    result = future.result()
                    if result:
                        read_results.append(result)
                        # Early return if we have enough reads
                        if len(read_results) >= self.R:
                            break
                except Exception as e:
                    print(f"Read timeout/error for {replica_id}: {e}")
        
        if len(read_results) < self.R:
            print(f"❌ Read failed: Only {len(read_results)}/{self.R} replicas responded")
            return False, None, {
                "operation_id": operation_id,
                "success": False,
                "reason": "insufficient_responses",
                "responses": len(read_results)
            }
        
        # Resolve conflicts using latest version
        latest_result = max(read_results, key=lambda r: r.version)
        
        # Check for consistency violations
        versions = [r.version for r in read_results]
        consistent = len(set(versions)) == 1
        
        if not consistent:
            print(f"⚠️ Read inconsistency detected: versions {versions}")
            print(f"📊 Returning latest version {latest_result.version} from {latest_result.replica_id}")
        
        print(f"✅ Read successful: {key} = {latest_result.value}")
        print(f"📍 Source: {latest_result.replica_id} (v{latest_result.version})")
        
        return True, latest_result.value, {
            "operation_id": operation_id,
            "success": True,
            "value": latest_result.value,
            "version": latest_result.version,
            "consistent": consistent,
            "source_replica": latest_result.replica_id,
            "total_responses": len(read_results),
            "latency_ms": (time.time() - start_time) * 1000,
            "all_versions": versions
        }

    def simulate_replica_failure(self, replica_id: str):
        """
        Simulate replica failure - जैसे AWS zone failure
        """
        if replica_id in self.replicas:
            self.replicas[replica_id].status = ReplicaStatus.FAILED
            print(f"💥 Replica {replica_id} failed (simulating AWS zone down)")
            
            # Check if system can still operate
            healthy_count = sum(1 for r in self.replicas.values() 
                              if r.status in [ReplicaStatus.HEALTHY, ReplicaStatus.SLOW])
            
            print(f"📊 System status: {healthy_count}/{self.N} replicas healthy")
            if healthy_count < max(self.R, self.W):
                print(f"🚨 WARNING: System may not meet consistency requirements!")

    def recover_replica(self, replica_id: str):
        """
        Recover failed replica - जैसे auto-scaling recovery
        """
        if replica_id in self.replicas:
            self.replicas[replica_id].status = ReplicaStatus.RECOVERING
            print(f"🔄 Replica {replica_id} recovering...")
            
            # Simulate recovery time
            time.sleep(1)
            
            self.replicas[replica_id].status = ReplicaStatus.HEALTHY
            print(f"✅ Replica {replica_id} recovered")

    def tune_consistency(self, new_level: ConsistencyLevel):
        """
        Dynamically tune consistency level
        
        Production use case: Lower consistency during high load
        """
        old_level = self.consistency_level
        self.consistency_level = new_level
        self._set_quorum_sizes()
        
        print(f"🔧 Consistency tuned: {old_level.value} → {new_level.value}")
        print(f"📊 New quorum sizes: R={self.R}, W={self.W}")

    def get_system_stats(self) -> Dict:
        """
        Comprehensive system statistics for monitoring
        """
        healthy_replicas = sum(1 for r in self.replicas.values() 
                             if r.status == ReplicaStatus.HEALTHY)
        failed_replicas = sum(1 for r in self.replicas.values() 
                            if r.status == ReplicaStatus.FAILED)
        
        avg_latency = sum(r.latency_ms for r in self.replicas.values()) / len(self.replicas)
        
        return {
            "total_replicas": self.N,
            "healthy_replicas": healthy_replicas,
            "failed_replicas": failed_replicas,
            "read_quorum": self.R,
            "write_quorum": self.W,
            "consistency_level": self.consistency_level.value,
            "avg_latency_ms": avg_latency,
            "operations_performed": self.operation_counter,
            "current_version": self.version_counter,
            "strong_consistency": self.R + self.W > self.N
        }

    def run_consistency_test(self, num_operations: int = 20):
        """
        Comprehensive consistency test with Indian scenarios
        """
        print(f"\n🧪 CONSISTENCY TEST: {num_operations} operations")
        print("=" * 60)
        
        test_scenarios = [
            ("flipkart_product_123", "inventory", 100),
            ("zomato_restaurant_456", "available_tables", 25),
            ("irctc_train_12345_A1", "seat_status", "available"),
            ("paytm_user_789", "account_balance", 5000),
            ("ola_driver_101", "location", {"lat": 19.0760, "lng": 72.8777})
        ]
        
        successful_operations = 0
        consistency_violations = 0
        
        for i, (key, field, initial_value) in enumerate(test_scenarios):
            print(f"\n📋 Test {i+1}: {field} for {key}")
            
            # Write operation
            write_success, write_meta = self.write(key, initial_value, f"test_client_{i}")
            if write_success:
                successful_operations += 1
            
            # Immediate read to test consistency
            read_success, read_value, read_meta = self.read(key, f"test_client_{i}")
            if read_success:
                successful_operations += 1
                if not read_meta.get("consistent", True):
                    consistency_violations += 1
            
            # Random operation
            if random.random() < 0.5:
                # Another write
                new_value = f"updated_{initial_value}_{int(time.time())}"
                write_success, _ = self.write(key, new_value, f"test_client_{i}_update")
                if write_success:
                    successful_operations += 1
            
            time.sleep(0.1)  # Small delay between operations
        
        # Final statistics
        total_expected_ops = len(test_scenarios) * 2 + (num_operations - len(test_scenarios))
        success_rate = (successful_operations / total_expected_ops) * 100
        
        print(f"\n📊 CONSISTENCY TEST RESULTS")
        print("=" * 40)
        print(f"Total Operations: {successful_operations}/{total_expected_ops}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Consistency Violations: {consistency_violations}")
        print(f"System Stats: {self.get_system_stats()}")

def main():
    """
    Main demonstration with real Indian tech company scenarios
    """
    print("🇮🇳 Quorum Replication System - Indian Tech Context")
    print("=" * 60)
    
    # Initialize system with 5 replicas across India
    replicas = ["replica_mumbai", "replica_delhi", "replica_bangalore", 
                "replica_chennai", "replica_hyderabad"]
    
    # Scenario 1: Flipkart Inventory Management (Strong Consistency)
    print("\n🛒 SCENARIO 1: Flipkart Product Inventory")
    print("Requirement: Strong consistency for accurate inventory")
    
    flipkart_system = QuorumReplicationSystem(replicas, ConsistencyLevel.QUORUM)
    
    # Product inventory operations
    flipkart_system.write("iphone_14_blue", {"stock": 50, "price": 79999}, "flipkart_inventory_service")
    flipkart_system.read("iphone_14_blue", "flipkart_web_frontend")
    
    # Simulate high load scenario
    print("\n📈 Simulating Black Friday sale load...")
    
    def simulate_concurrent_inventory_updates():
        for i in range(5):
            current_stock = 50 - (i * 10)  # Stock decreasing
            flipkart_system.write(
                "iphone_14_blue", 
                {"stock": current_stock, "price": 79999, "updated_at": time.time()},
                f"order_service_{i}"
            )
            time.sleep(0.1)
    
    # Run concurrent updates
    inventory_thread = threading.Thread(target=simulate_concurrent_inventory_updates)
    inventory_thread.start()
    inventory_thread.join()
    
    # Scenario 2: Zomato Restaurant Availability (Eventual Consistency OK)
    print("\n🍽️ SCENARIO 2: Zomato Restaurant Menu")
    print("Requirement: High availability, eventual consistency acceptable")
    
    zomato_system = QuorumReplicationSystem(
        replicas[:3],  # Fewer replicas for faster operations
        ConsistencyLevel.ONE
    )
    
    # Menu updates
    zomato_system.write("restaurant_123_menu", {
        "items": ["Butter Chicken", "Dal Makhani", "Naan"],
        "available": True,
        "updated_by": "restaurant_owner"
    }, "zomato_restaurant_app")
    
    # Multiple reads (should be fast)
    for i in range(3):
        success, menu, meta = zomato_system.read("restaurant_123_menu", f"zomato_user_{i}")
        print(f"User {i} read latency: {meta.get('latency_ms', 0):.1f}ms")
    
    # Scenario 3: IRCTC Ticket Booking (Maximum Consistency)
    print("\n🚆 SCENARIO 3: IRCTC Seat Booking")
    print("Requirement: Maximum consistency - no double booking allowed")
    
    irctc_system = QuorumReplicationSystem(replicas, ConsistencyLevel.ALL)
    
    # Seat booking with strict consistency
    irctc_system.write("train_12345_coach_A1_seat_23", {
        "status": "available",
        "price": 1200,
        "train": "Rajdhani Express",
        "date": "2025-08-15"
    }, "irctc_booking_system")
    
    # Simulate multiple users trying to book same seat
    def attempt_booking(user_id: str, seat_id: str):
        # Read current status
        success, seat_info, _ = irctc_system.read(seat_id, f"user_{user_id}")
        if success and seat_info and seat_info.get("status") == "available":
            # Try to book
            booking_success, _ = irctc_system.write(seat_id, {
                "status": "booked",
                "booked_by": user_id,
                "booking_time": time.time(),
                "price": seat_info.get("price", 1200)
            }, f"user_{user_id}")
            
            if booking_success:
                print(f"✅ User {user_id} successfully booked seat")
            else:
                print(f"❌ User {user_id} booking failed")
    
    # Concurrent booking attempts
    seat_id = "train_12345_coach_A1_seat_23"
    booking_threads = []
    
    for user_id in ["rajesh", "priya", "amit", "sneha"]:
        thread = threading.Thread(target=attempt_booking, args=(user_id, seat_id))
        booking_threads.append(thread)
        thread.start()
    
    for thread in booking_threads:
        thread.join()
    
    # Final seat status check
    success, final_status, _ = irctc_system.read(seat_id, "irctc_admin")
    print(f"Final seat status: {final_status}")
    
    # Scenario 4: Failure Resilience Test
    print("\n💥 SCENARIO 4: Failure Resilience")
    print("Testing system behavior during replica failures")
    
    # Simulate replica failure
    flipkart_system.simulate_replica_failure("replica_mumbai")
    
    # Try operations with failed replica
    success, _ = flipkart_system.write("test_failure_resilience", "test_value", "test_client")
    print(f"Write with failed replica: {'SUCCESS' if success else 'FAILED'}")
    
    # Recover replica
    flipkart_system.recover_replica("replica_mumbai")
    
    # Run comprehensive consistency test
    print("\n🔬 COMPREHENSIVE CONSISTENCY TEST")
    flipkart_system.run_consistency_test(15)
    
    # Demonstrate consistency level tuning
    print("\n⚙️ DYNAMIC CONSISTENCY TUNING")
    print("Scenario: Reduce consistency during high load")
    
    flipkart_system.tune_consistency(ConsistencyLevel.ONE)
    success, _ = flipkart_system.write("high_load_test", "fast_write", "load_balancer")
    print(f"Fast write during high load: {'SUCCESS' if success else 'FAILED'}")
    
    # Restore strong consistency
    flipkart_system.tune_consistency(ConsistencyLevel.QUORUM)
    
    print("\n✅ Quorum Replication demonstration complete!")
    print("\nKey learnings:")
    print("1. R + W > N guarantees strong consistency")
    print("2. Tunable consistency allows performance trade-offs")
    print("3. Quorum systems handle replica failures gracefully")
    print("4. Different applications need different consistency models:")
    print("   • Flipkart inventory: Strong consistency (QUORUM)")
    print("   • Zomato menu: High availability (ONE)")
    print("   • IRCTC booking: Maximum consistency (ALL)")

if __name__ == "__main__":
    main()