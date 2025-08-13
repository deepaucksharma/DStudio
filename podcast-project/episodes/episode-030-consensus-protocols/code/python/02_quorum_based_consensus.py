#!/usr/bin/env python3
"""
Quorum-Based Consensus Implementation
====================================

Mumbai Parliament ki tarah - minimum members chahiye valid decision ke liye!
Just like Mumbai requires minimum members for valid parliamentary decisions,
distributed systems need quorum for consensus.

Key Concepts:
- Read Quorum: Minimum nodes to read consistent data
- Write Quorum: Minimum nodes to write data
- R + W > N ensures consistency

Author: Hindi Tech Podcast
Episode: 030 - Consensus Protocols
"""

import time
import random
import threading
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, Counter
import uuid

class NodeState(Enum):
    """Node states - Mumbai MLA ki tarah"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    SUSPECTED = "suspected"
    FAILED = "failed"

class OperationType(Enum):
    """Operation types"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

@dataclass
class QuorumConfig:
    """
    Quorum configuration - Mumbai Parliament rules
    """
    total_nodes: int
    read_quorum: int
    write_quorum: int
    
    def __post_init__(self):
        # Validate quorum rules - Mumbai style validation
        if self.read_quorum + self.write_quorum <= self.total_nodes:
            print("⚠️  Warning: R + W <= N, consistency not guaranteed!")
        
        if self.read_quorum > self.total_nodes or self.write_quorum > self.total_nodes:
            raise ValueError("Quorum size cannot exceed total nodes!")
        
        print(f"🏛️ Quorum Config: N={self.total_nodes}, R={self.read_quorum}, W={self.write_quorum}")

@dataclass
class DataRecord:
    """
    Data record with version - Mumbai database entry
    """
    key: str
    value: str
    version: int
    timestamp: float
    node_id: str
    checksum: str = field(default="")
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> str:
        """Calculate record checksum - data integrity check"""
        data = f"{self.key}:{self.value}:{self.version}:{self.timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:8]
    
    def is_valid(self) -> bool:
        """Validate record integrity"""
        return self.checksum == self.calculate_checksum()

@dataclass 
class QuorumRequest:
    """
    Quorum operation request
    """
    request_id: str
    operation: OperationType
    key: str
    value: Optional[str] = None
    client_id: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class QuorumResponse:
    """
    Response from quorum node
    """
    request_id: str
    node_id: str
    success: bool
    data: Optional[DataRecord] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class QuorumNode:
    """
    Quorum-based consensus node - Mumbai Parliament member
    """
    
    def __init__(self, node_id: str, quorum_config: QuorumConfig):
        self.node_id = node_id
        self.config = quorum_config
        self.state = NodeState.ACTIVE
        self.data_store: Dict[str, DataRecord] = {}
        self.version_vector: Dict[str, int] = defaultdict(int)
        
        # Mumbai network characteristics
        self.network_delay = random.uniform(0.05, 0.3)  # Mumbai Internet latency
        self.reliability = random.uniform(0.85, 0.99)   # Node reliability
        self.processing_time = random.uniform(0.01, 0.1)  # Processing delay
        
        # Performance metrics
        self.requests_served = 0
        self.failed_requests = 0
        self.last_heartbeat = time.time()
        
        print(f"🏛️ QuorumNode {self.node_id} initialized (reliability: {self.reliability:.2f})")
    
    def heartbeat(self) -> bool:
        """
        Node heartbeat - Mumbai MLA attendance check
        """
        self.last_heartbeat = time.time()
        
        # Simulate occasional node failures (Mumbai power cuts!)
        if random.random() > self.reliability:
            self.state = NodeState.SUSPECTED
            return False
        
        self.state = NodeState.ACTIVE
        return True
    
    def process_read_request(self, request: QuorumRequest) -> QuorumResponse:
        """
        Process read request - Mumbai database query
        """
        self.requests_served += 1
        
        # Simulate processing delay
        time.sleep(self.processing_time)
        
        # Check if node is active
        if self.state != NodeState.ACTIVE:
            self.failed_requests += 1
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=False,
                error=f"Node {self.node_id} is {self.state.value}"
            )
        
        # Simulate network issues
        if random.random() > self.reliability:
            self.failed_requests += 1
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=False,
                error="Network timeout - Mumbai bandwidth issue!"
            )
        
        # Get data record
        if request.key in self.data_store:
            record = self.data_store[request.key]
            if record.is_valid():
                return QuorumResponse(
                    request_id=request.request_id,
                    node_id=self.node_id,
                    success=True,
                    data=record
                )
            else:
                return QuorumResponse(
                    request_id=request.request_id,
                    node_id=self.node_id,
                    success=False,
                    error="Data corruption detected!"
                )
        else:
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=True,
                data=None  # Key not found
            )
    
    def process_write_request(self, request: QuorumRequest) -> QuorumResponse:
        """
        Process write request - Mumbai database update
        """
        self.requests_served += 1
        
        # Simulate processing delay
        time.sleep(self.processing_time)
        
        # Check if node is active
        if self.state != NodeState.ACTIVE:
            self.failed_requests += 1
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=False,
                error=f"Node {self.node_id} is {self.state.value}"
            )
        
        # Simulate network issues
        if random.random() > self.reliability:
            self.failed_requests += 1
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=False,
                error="Write failed - Mumbai server overload!"
            )
        
        try:
            # Update version
            current_version = self.version_vector[request.key]
            new_version = current_version + 1
            
            # Create new record
            record = DataRecord(
                key=request.key,
                value=request.value,
                version=new_version,
                timestamp=time.time(),
                node_id=self.node_id
            )
            
            # Store record
            self.data_store[request.key] = record
            self.version_vector[request.key] = new_version
            
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=True,
                data=record
            )
            
        except Exception as e:
            self.failed_requests += 1
            return QuorumResponse(
                request_id=request.request_id,
                node_id=self.node_id,
                success=False,
                error=f"Write error: {str(e)}"
            )
    
    def get_stats(self) -> Dict:
        """Get node statistics"""
        uptime = time.time() - self.last_heartbeat
        success_rate = (self.requests_served - self.failed_requests) / max(1, self.requests_served)
        
        return {
            "node_id": self.node_id,
            "state": self.state.value,
            "requests_served": self.requests_served,
            "failed_requests": self.failed_requests,
            "success_rate": success_rate,
            "uptime": uptime,
            "data_records": len(self.data_store),
            "reliability": self.reliability
        }

class QuorumConsensusSystem:
    """
    Quorum-based consensus system - Mumbai Parliament System
    """
    
    def __init__(self, config: QuorumConfig):
        self.config = config
        self.nodes: List[QuorumNode] = []
        self.client_id = f"client_{uuid.uuid4().hex[:8]}"
        
        # Create nodes
        mumbai_constituencies = [
            "Bandra_East", "Andheri_West", "Borivali", "Thane", "Kurla",
            "Worli", "Colaba", "Powai", "Vikhroli", "Malad"
        ]
        
        for i in range(config.total_nodes):
            constituency = mumbai_constituencies[i] if i < len(mumbai_constituencies) else f"Node_{i}"
            node = QuorumNode(constituency, config)
            self.nodes.append(node)
        
        print(f"🏛️ Quorum System initialized with {len(self.nodes)} nodes")
        print(f"   Read Quorum: {config.read_quorum}")
        print(f"   Write Quorum: {config.write_quorum}")
    
    def select_nodes_for_operation(self, operation: OperationType) -> List[QuorumNode]:
        """
        Select nodes for operation - Mumbai constituency selection
        """
        # Filter active nodes
        active_nodes = [node for node in self.nodes if node.state == NodeState.ACTIVE]
        
        if operation == OperationType.READ:
            required = self.config.read_quorum
        elif operation == OperationType.WRITE:
            required = self.config.write_quorum
        else:
            required = self.config.write_quorum
        
        if len(active_nodes) < required:
            raise Exception(f"Insufficient active nodes: need {required}, have {len(active_nodes)}")
        
        # Select nodes (could be random, round-robin, or load-based)
        # For now, using random selection
        selected = random.sample(active_nodes, required)
        
        node_names = [node.node_id for node in selected]
        print(f"🎯 Selected {len(selected)} nodes for {operation.value}: {node_names}")
        
        return selected
    
    def execute_read_operation(self, key: str) -> Tuple[bool, Optional[DataRecord], str]:
        """
        Execute quorum read - Mumbai Parliament vote counting
        """
        request_id = f"read_{uuid.uuid4().hex[:8]}"
        print(f"\n📖 Executing READ operation for key: {key}")
        print(f"   Request ID: {request_id}")
        
        try:
            # Select nodes for read quorum
            selected_nodes = self.select_nodes_for_operation(OperationType.READ)
            
            # Create read request
            request = QuorumRequest(
                request_id=request_id,
                operation=OperationType.READ,
                key=key,
                client_id=self.client_id
            )
            
            # Send requests in parallel
            responses = []
            threads = []
            
            def send_read_request(node: QuorumNode):
                response = node.process_read_request(request)
                responses.append(response)
            
            # Start parallel requests
            for node in selected_nodes:
                thread = threading.Thread(target=send_read_request, args=(node,))
                threads.append(thread)
                thread.start()
            
            # Wait for responses
            for thread in threads:
                thread.join()
            
            # Analyze responses
            successful_responses = [r for r in responses if r.success]
            
            print(f"   Responses: {len(successful_responses)}/{len(selected_nodes)} successful")
            
            if len(successful_responses) < self.config.read_quorum:
                return False, None, f"Read quorum not met: {len(successful_responses)}/{self.config.read_quorum}"
            
            # Find most recent version (conflict resolution)
            valid_records = [r.data for r in successful_responses if r.data is not None]
            
            if not valid_records:
                return True, None, "Key not found"
            
            # Select record with highest version (last write wins)
            latest_record = max(valid_records, key=lambda r: (r.version, r.timestamp))
            
            print(f"   ✅ Read successful: key={key}, version={latest_record.version}")
            return True, latest_record, "Success"
            
        except Exception as e:
            error_msg = f"Read operation failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            return False, None, error_msg
    
    def execute_write_operation(self, key: str, value: str) -> Tuple[bool, str]:
        """
        Execute quorum write - Mumbai Parliament bill passing
        """
        request_id = f"write_{uuid.uuid4().hex[:8]}"
        print(f"\n✏️ Executing WRITE operation for key: {key}")
        print(f"   Request ID: {request_id}")
        print(f"   Value: {value}")
        
        try:
            # Select nodes for write quorum
            selected_nodes = self.select_nodes_for_operation(OperationType.WRITE)
            
            # Create write request
            request = QuorumRequest(
                request_id=request_id,
                operation=OperationType.WRITE,
                key=key,
                value=value,
                client_id=self.client_id
            )
            
            # Send requests in parallel
            responses = []
            threads = []
            
            def send_write_request(node: QuorumNode):
                response = node.process_write_request(request)
                responses.append(response)
            
            # Start parallel requests
            for node in selected_nodes:
                thread = threading.Thread(target=send_write_request, args=(node,))
                threads.append(thread)
                thread.start()
            
            # Wait for responses
            for thread in threads:
                thread.join()
            
            # Analyze responses
            successful_responses = [r for r in responses if r.success]
            
            print(f"   Responses: {len(successful_responses)}/{len(selected_nodes)} successful")
            
            if len(successful_responses) < self.config.write_quorum:
                return False, f"Write quorum not met: {len(successful_responses)}/{self.config.write_quorum}"
            
            print(f"   ✅ Write successful: key={key}")
            return True, "Success"
            
        except Exception as e:
            error_msg = f"Write operation failed: {str(e)}"
            print(f"   ❌ {error_msg}")
            return False, error_msg
    
    def simulate_node_failures(self, num_failures: int):
        """
        Simulate node failures - Mumbai power cuts
        """
        if num_failures >= len(self.nodes):
            print("⚠️  Cannot fail all nodes!")
            return
        
        failed_nodes = random.sample(self.nodes, num_failures)
        for node in failed_nodes:
            node.state = NodeState.FAILED
            print(f"💥 Node {node.node_id} failed (Mumbai power cut!)")
    
    def recover_nodes(self):
        """
        Recover failed nodes - Mumbai power restoration
        """
        failed_nodes = [node for node in self.nodes if node.state == NodeState.FAILED]
        for node in failed_nodes:
            node.state = NodeState.ACTIVE
            node.last_heartbeat = time.time()
            print(f"🔄 Node {node.node_id} recovered (power restored!)")
    
    def get_system_stats(self) -> Dict:
        """
        Get system statistics
        """
        node_stats = [node.get_stats() for node in self.nodes]
        
        active_nodes = len([n for n in self.nodes if n.state == NodeState.ACTIVE])
        total_requests = sum(stats['requests_served'] for stats in node_stats)
        total_failures = sum(stats['failed_requests'] for stats in node_stats)
        avg_success_rate = sum(stats['success_rate'] for stats in node_stats) / len(node_stats)
        
        return {
            "total_nodes": len(self.nodes),
            "active_nodes": active_nodes,
            "failed_nodes": len(self.nodes) - active_nodes,
            "total_requests": total_requests,
            "total_failures": total_failures,
            "average_success_rate": avg_success_rate,
            "read_quorum": self.config.read_quorum,
            "write_quorum": self.config.write_quorum,
            "node_details": node_stats
        }

def demonstrate_quorum_operations():
    """
    Demonstrate quorum operations - Mumbai Parliament sessions
    """
    print("🏛️ MUMBAI PARLIAMENT QUORUM DEMONSTRATION")
    print("=" * 60)
    
    # Create different quorum configurations
    configs = [
        QuorumConfig(total_nodes=5, read_quorum=3, write_quorum=3),  # Strong consistency
        QuorumConfig(total_nodes=5, read_quorum=2, write_quorum=4),  # Write-heavy
        QuorumConfig(total_nodes=7, read_quorum=4, write_quorum=4),  # Balanced
    ]
    
    results = []
    
    for i, config in enumerate(configs):
        print(f"\n📍 Configuration {i+1}: N={config.total_nodes}, R={config.read_quorum}, W={config.write_quorum}")
        print("-" * 50)
        
        system = QuorumConsensusSystem(config)
        
        # Test operations
        test_data = [
            ("mumbai_population", "12500000"),
            ("mumbai_area", "603.4_sq_km"),
            ("local_train_lines", "3_main_lines"),
            ("monsoon_months", "june_to_september"),
            ("cricket_stadiums", "wankhede_stadium")
        ]
        
        operation_results = []
        
        # Write operations
        for key, value in test_data:
            success, msg = system.execute_write_operation(key, value)
            operation_results.append(("write", key, success, msg))
        
        # Read operations
        for key, expected_value in test_data:
            success, record, msg = system.execute_read_operation(key)
            operation_results.append(("read", key, success, msg))
            
            if success and record:
                print(f"     Retrieved: {record.value} (version: {record.version})")
        
        # Test with node failures
        print(f"\n💥 Simulating node failures...")
        system.simulate_node_failures(2)
        
        # Try operations with failed nodes
        success, record, msg = system.execute_read_operation("mumbai_population")
        operation_results.append(("read_with_failures", "mumbai_population", success, msg))
        
        # Recover nodes
        system.recover_nodes()
        
        # Get stats
        stats = system.get_system_stats()
        operation_results.append(("stats", "", True, stats))
        
        results.append({
            "config": config,
            "operations": operation_results,
            "final_stats": stats
        })
    
    return results

def test_consistency_guarantees():
    """
    Test consistency guarantees with different quorum configurations
    """
    print("\n🔒 CONSISTENCY GUARANTEES TEST")
    print("=" * 50)
    
    # Test strong consistency (R + W > N)
    config = QuorumConfig(total_nodes=5, read_quorum=3, write_quorum=3)
    system = QuorumConsensusSystem(config)
    
    test_scenarios = [
        {
            "name": "Concurrent writes to same key",
            "operations": [
                ("write", "mumbai_mayor", "candidate_A"),
                ("write", "mumbai_mayor", "candidate_B"),
                ("read", "mumbai_mayor", None)
            ]
        },
        {
            "name": "Read after write consistency", 
            "operations": [
                ("write", "mumbai_budget", "50000_crores"),
                ("read", "mumbai_budget", None)
            ]
        }
    ]
    
    results = []
    for scenario in test_scenarios:
        print(f"\n📋 Test: {scenario['name']}")
        print("-" * 30)
        
        scenario_results = []
        for op_type, key, value in scenario['operations']:
            if op_type == "write":
                success, msg = system.execute_write_operation(key, value)
                scenario_results.append((op_type, key, success, msg))
            elif op_type == "read":
                success, record, msg = system.execute_read_operation(key)
                scenario_results.append((op_type, key, success, record.value if record else None))
        
        results.append({
            "scenario": scenario['name'],
            "results": scenario_results
        })
    
    return results

if __name__ == "__main__":
    print("🚀 QUORUM-BASED CONSENSUS SYSTEM")
    print("Mumbai Parliament Simulation")
    print("=" * 60)
    
    try:
        # Demonstrate quorum operations
        quorum_results = demonstrate_quorum_operations()
        
        # Test consistency guarantees
        consistency_results = test_consistency_guarantees()
        
        print("\n📊 FINAL SUMMARY")
        print("=" * 30)
        print(f"Configurations tested: {len(quorum_results)}")
        print(f"Consistency scenarios: {len(consistency_results)}")
        
        print("\n🎯 Key Insights:")
        print("• Higher quorum = stronger consistency but lower availability")
        print("• R + W > N guarantees strong consistency")
        print("• Quorum systems handle partial failures gracefully")
        print("• Like Mumbai Parliament - need minimum members for valid decisions!")
        
        print("\n🎊 QUORUM SIMULATION COMPLETED SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ Error in quorum simulation: {e}")
        raise