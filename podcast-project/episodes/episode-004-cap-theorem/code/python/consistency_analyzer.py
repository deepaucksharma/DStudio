#!/usr/bin/env python3
"""
Consistency Level Analyzer - Episode 4
व्यावहारिक Consistency Level का measurement और analysis

यह system distributed systems में different consistency levels को measure करता है
और violations को detect करता है।

Indian Context Examples:
- Paytm payment consistency across regions
- Flipkart inventory consistency analysis
- WhatsApp message ordering verification
- IRCTC booking data consistency audit

Consistency Levels measured:
1. Strong Consistency - All reads get latest write
2. Sequential Consistency - Operations appear in some sequential order
3. Causal Consistency - Causally related operations in order
4. Eventual Consistency - Eventually all nodes converge
5. Weak Consistency - No guarantees

Analysis Types:
- Read-after-write consistency
- Monotonic read consistency  
- Monotonic write consistency
- Write-write conflicts
- Causal ordering violations
"""

import time
import uuid
import threading
import random
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict
import statistics
from datetime import datetime, timedelta

class ConsistencyLevel(Enum):
    """Different consistency levels"""
    STRONG = "strong"                    # Linearizable
    SEQUENTIAL = "sequential"            # Sequential consistency
    CAUSAL = "causal"                   # Causal consistency
    EVENTUAL = "eventual"               # Eventually consistent
    WEAK = "weak"                       # No guarantees

class ConsistencyViolationType(Enum):
    """Types of consistency violations"""
    READ_AFTER_WRITE = "read_after_write"        # Read doesn't see recent write
    MONOTONIC_READ = "monotonic_read"            # Read goes backward in time
    MONOTONIC_WRITE = "monotonic_write"          # Write reordering
    CAUSAL_ORDER = "causal_order"               # Causal relationships violated
    WRITE_CONFLICT = "write_conflict"            # Concurrent writes conflict
    STALE_READ = "stale_read"                   # Reading very old data

@dataclass
class Operation:
    """Represents a single read/write operation"""
    op_id: str
    op_type: str  # "read" or "write"
    key: str
    value: Any
    timestamp: float
    node_id: str
    session_id: str
    vector_clock: Optional[Dict[str, int]] = None
    causal_dependencies: Set[str] = field(default_factory=set)

@dataclass
class ConsistencyViolation:
    """Represents a consistency violation"""
    violation_type: ConsistencyViolationType
    violation_id: str
    timestamp: float
    description: str
    affected_operations: List[str]
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    node_ids: List[str]
    suggested_action: str
    business_impact: str

@dataclass
class ConsistencyMetrics:
    """Consistency metrics for analysis"""
    total_operations: int = 0
    violations_count: int = 0
    consistency_score: float = 1.0  # 0.0 to 1.0
    avg_staleness_ms: float = 0.0
    max_staleness_ms: float = 0.0
    read_after_write_success_rate: float = 1.0
    monotonic_read_success_rate: float = 1.0
    causal_order_success_rate: float = 1.0
    analysis_period_start: datetime = field(default_factory=datetime.now)
    analysis_period_end: datetime = field(default_factory=datetime.now)

class DistributedNode:
    """Represents a node in distributed system"""
    
    def __init__(self, node_id: str, location: str = "Mumbai"):
        self.node_id = node_id
        self.location = location
        self.data_store: Dict[str, Any] = {}
        self.version_store: Dict[str, int] = {}  # Track versions
        self.operation_log: List[Operation] = []
        self.vector_clock: Dict[str, int] = defaultdict(int)
        
        # Network simulation parameters
        self.network_delay_ms = random.uniform(10, 100)  # India network latency
        self.failure_rate = 0.05  # 5% operation failure rate
        
        print(f"🖥️ Node {node_id} ({location}) initialized with {self.network_delay_ms:.1f}ms avg latency")
    
    def write(self, key: str, value: Any, session_id: str) -> Operation:
        """Perform write operation"""
        # Simulate network delay
        time.sleep(self.network_delay_ms / 1000.0)
        
        # Check for failure
        if random.random() < self.failure_rate:
            raise Exception(f"Network failure on node {self.node_id}")
        
        # Update vector clock
        self.vector_clock[self.node_id] += 1
        
        # Create operation
        operation = Operation(
            op_id=str(uuid.uuid4()),
            op_type="write",
            key=key,
            value=value,
            timestamp=time.time(),
            node_id=self.node_id,
            session_id=session_id,
            vector_clock=dict(self.vector_clock)
        )
        
        # Update data and version
        self.data_store[key] = value
        self.version_store[key] = self.version_store.get(key, 0) + 1
        
        # Log operation
        self.operation_log.append(operation)
        
        print(f"✍️ Node {self.node_id}: WRITE {key}={value} (v{self.version_store[key]})")
        return operation
    
    def read(self, key: str, session_id: str) -> Operation:
        """Perform read operation"""
        # Simulate network delay
        time.sleep(self.network_delay_ms / 1000.0)
        
        # Check for failure
        if random.random() < self.failure_rate:
            raise Exception(f"Network failure on node {self.node_id}")
        
        # Update vector clock for read
        self.vector_clock[self.node_id] += 1
        
        # Read value
        value = self.data_store.get(key, None)
        
        # Create operation
        operation = Operation(
            op_id=str(uuid.uuid4()),
            op_type="read",
            key=key,
            value=value,
            timestamp=time.time(),
            node_id=self.node_id,
            session_id=session_id,
            vector_clock=dict(self.vector_clock)
        )
        
        # Log operation
        self.operation_log.append(operation)
        
        print(f"📖 Node {self.node_id}: READ {key}={value}")
        return operation
    
    def sync_with_node(self, other_node: 'DistributedNode', key: str):
        """Sync specific key with another node (eventual consistency)"""
        if key in other_node.data_store:
            other_version = other_node.version_store.get(key, 0)
            my_version = self.version_store.get(key, 0)
            
            # Last-write-wins based on version
            if other_version > my_version:
                self.data_store[key] = other_node.data_store[key]
                self.version_store[key] = other_version
                
                # Update vector clock
                for node_id, clock_value in other_node.vector_clock.items():
                    self.vector_clock[node_id] = max(self.vector_clock[node_id], clock_value)
                
                print(f"🔄 Node {self.node_id}: Synced {key} from {other_node.node_id} (v{other_version})")

class ConsistencyAnalyzer:
    """
    Consistency Level Analyzer - Distributed systems की consistency को analyze करता है
    
    Real usage:
    - Database consistency auditing
    - Microservice consistency verification
    - Cache consistency monitoring  
    - Replication lag analysis
    """
    
    def __init__(self):
        self.nodes: Dict[str, DistributedNode] = {}
        self.all_operations: List[Operation] = []
        self.violations: List[ConsistencyViolation] = []
        self.sessions: Dict[str, List[Operation]] = defaultdict(list)
        
        # Analysis configuration
        self.analysis_window_minutes = 60  # Analysis window
        self.staleness_threshold_ms = 1000  # 1 second staleness threshold
        
        print("🔍 Consistency Analyzer initialized")
    
    def add_node(self, node: DistributedNode):
        """Add node to analyzer"""
        self.nodes[node.node_id] = node
        print(f"➕ Added node {node.node_id} to consistency analyzer")
    
    def analyze_consistency(self) -> ConsistencyMetrics:
        """
        Comprehensive consistency analysis
        """
        print(f"\n📊 Starting consistency analysis...")
        
        # Collect all operations from all nodes
        self._collect_operations()
        
        # Analyze different consistency violations
        self._analyze_read_after_write_consistency()
        self._analyze_monotonic_read_consistency()
        self._analyze_causal_consistency()
        self._analyze_staleness()
        self._analyze_write_conflicts()
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        print(f"✅ Consistency analysis complete")
        return metrics
    
    def _collect_operations(self):
        """Collect operations from all nodes and organize by session"""
        self.all_operations = []
        self.sessions = defaultdict(list)
        
        for node in self.nodes.values():
            for operation in node.operation_log:
                self.all_operations.append(operation)
                self.sessions[operation.session_id].append(operation)
        
        # Sort operations by timestamp
        self.all_operations.sort(key=lambda op: op.timestamp)
        
        # Sort operations within each session
        for session_ops in self.sessions.values():
            session_ops.sort(key=lambda op: op.timestamp)
        
        print(f"📋 Collected {len(self.all_operations)} operations across {len(self.sessions)} sessions")
    
    def _analyze_read_after_write_consistency(self):
        """
        Analyze read-after-write consistency
        
        Check if reads see writes from the same session
        """
        print("🔍 Analyzing read-after-write consistency...")
        
        for session_id, operations in self.sessions.items():
            writes_by_key = {}
            
            for operation in operations:
                if operation.op_type == "write":
                    writes_by_key[operation.key] = operation
                
                elif operation.op_type == "read":
                    key = operation.key
                    if key in writes_by_key:
                        last_write = writes_by_key[key]
                        
                        # Check if read sees the write from same session
                        if operation.value != last_write.value:
                            violation = ConsistencyViolation(
                                violation_type=ConsistencyViolationType.READ_AFTER_WRITE,
                                violation_id=str(uuid.uuid4()),
                                timestamp=operation.timestamp,
                                description=f"Read in session {session_id} didn't see recent write",
                                affected_operations=[last_write.op_id, operation.op_id],
                                severity="HIGH",
                                node_ids=[last_write.node_id, operation.node_id],
                                suggested_action="Implement read-your-writes consistency",
                                business_impact="User may see inconsistent data after updates"
                            )
                            self.violations.append(violation)
                            
                            print(f"❌ Read-after-write violation: Session {session_id}, Key {key}")
    
    def _analyze_monotonic_read_consistency(self):
        """
        Analyze monotonic read consistency
        
        Check if reads don't go backward in time for same key
        """
        print("🔍 Analyzing monotonic read consistency...")
        
        for session_id, operations in self.sessions.items():
            reads_by_key = defaultdict(list)
            
            # Group reads by key
            for operation in operations:
                if operation.op_type == "read":
                    reads_by_key[operation.key].append(operation)
            
            # Check monotonicity for each key
            for key, reads in reads_by_key.items():
                if len(reads) < 2:
                    continue
                
                # Check if any read sees older data than previous read
                for i in range(1, len(reads)):
                    prev_read = reads[i-1]
                    curr_read = reads[i]
                    
                    # For simplicity, assume version numbers in data
                    # In real implementation, you'd track versions properly
                    if (prev_read.value is not None and curr_read.value is not None and
                        str(prev_read.value) > str(curr_read.value)):  # Simplified version comparison
                        
                        violation = ConsistencyViolation(
                            violation_type=ConsistencyViolationType.MONOTONIC_READ,
                            violation_id=str(uuid.uuid4()),
                            timestamp=curr_read.timestamp,
                            description=f"Monotonic read violation for key {key} in session {session_id}",
                            affected_operations=[prev_read.op_id, curr_read.op_id],
                            severity="MEDIUM",
                            node_ids=[prev_read.node_id, curr_read.node_id],
                            suggested_action="Implement monotonic read consistency",
                            business_impact="User may see data going backward in time"
                        )
                        self.violations.append(violation)
                        
                        print(f"❌ Monotonic read violation: Session {session_id}, Key {key}")
    
    def _analyze_causal_consistency(self):
        """
        Analyze causal consistency using vector clocks
        """
        print("🔍 Analyzing causal consistency...")
        
        # Group operations by key
        operations_by_key = defaultdict(list)
        for operation in self.all_operations:
            operations_by_key[operation.key].append(operation)
        
        for key, key_operations in operations_by_key.items():
            # Check causal ordering for each key
            for i in range(len(key_operations)):
                for j in range(i + 1, len(key_operations)):
                    op1 = key_operations[i]
                    op2 = key_operations[j]
                    
                    # Skip if no vector clocks
                    if not op1.vector_clock or not op2.vector_clock:
                        continue
                    
                    # Check if op1 causally precedes op2
                    if self._happens_before(op1.vector_clock, op2.vector_clock):
                        # op1 -> op2 causally, but check if op2 timestamp < op1 timestamp
                        if op2.timestamp < op1.timestamp:
                            violation = ConsistencyViolation(
                                violation_type=ConsistencyViolationType.CAUSAL_ORDER,
                                violation_id=str(uuid.uuid4()),
                                timestamp=op2.timestamp,
                                description=f"Causal ordering violation for key {key}",
                                affected_operations=[op1.op_id, op2.op_id],
                                severity="HIGH",
                                node_ids=[op1.node_id, op2.node_id],
                                suggested_action="Implement causal consistency protocol",
                                business_impact="Related operations may appear out of order"
                            )
                            self.violations.append(violation)
                            
                            print(f"❌ Causal consistency violation: Key {key}")
    
    def _analyze_staleness(self):
        """
        Analyze data staleness across nodes
        """
        print("🔍 Analyzing data staleness...")
        
        current_time = time.time()
        
        for operation in self.all_operations:
            if operation.op_type == "read":
                staleness_ms = (current_time - operation.timestamp) * 1000
                
                if staleness_ms > self.staleness_threshold_ms:
                    violation = ConsistencyViolation(
                        violation_type=ConsistencyViolationType.STALE_READ,
                        violation_id=str(uuid.uuid4()),
                        timestamp=operation.timestamp,
                        description=f"Stale read detected: {staleness_ms:.0f}ms old",
                        affected_operations=[operation.op_id],
                        severity="LOW" if staleness_ms < 5000 else "MEDIUM",
                        node_ids=[operation.node_id],
                        suggested_action="Reduce replication lag or implement bounded staleness",
                        business_impact="Users see outdated information"
                    )
                    self.violations.append(violation)
    
    def _analyze_write_conflicts(self):
        """
        Analyze concurrent write conflicts
        """
        print("🔍 Analyzing write conflicts...")
        
        # Group writes by key and detect concurrent writes
        writes_by_key = defaultdict(list)
        for operation in self.all_operations:
            if operation.op_type == "write":
                writes_by_key[operation.key].append(operation)
        
        for key, writes in writes_by_key.items():
            if len(writes) < 2:
                continue
            
            # Check for concurrent writes (within small time window)
            time_window = 0.1  # 100ms window
            
            for i in range(len(writes)):
                concurrent_writes = []
                for j in range(len(writes)):
                    if i != j and abs(writes[i].timestamp - writes[j].timestamp) <= time_window:
                        concurrent_writes.append(writes[j])
                
                if concurrent_writes:
                    all_writes = [writes[i]] + concurrent_writes
                    violation = ConsistencyViolation(
                        violation_type=ConsistencyViolationType.WRITE_CONFLICT,
                        violation_id=str(uuid.uuid4()),
                        timestamp=writes[i].timestamp,
                        description=f"Concurrent write conflict for key {key}",
                        affected_operations=[w.op_id for w in all_writes],
                        severity="CRITICAL",
                        node_ids=[w.node_id for w in all_writes],
                        suggested_action="Implement conflict resolution strategy",
                        business_impact="Data may be lost or corrupted"
                    )
                    self.violations.append(violation)
                    
                    print(f"❌ Write conflict: Key {key}, {len(all_writes)} concurrent writes")
                    break  # Avoid duplicate reports
    
    def _happens_before(self, clock1: Dict[str, int], clock2: Dict[str, int]) -> bool:
        """
        Check if clock1 happens-before clock2 using vector clocks
        """
        # clock1 <= clock2 for all nodes AND clock1 < clock2 for at least one node
        all_leq = True
        exists_less = False
        
        all_nodes = set(clock1.keys()) | set(clock2.keys())
        
        for node in all_nodes:
            val1 = clock1.get(node, 0)
            val2 = clock2.get(node, 0)
            
            if val1 > val2:
                all_leq = False
                break
            elif val1 < val2:
                exists_less = True
        
        return all_leq and exists_less
    
    def _calculate_metrics(self) -> ConsistencyMetrics:
        """Calculate overall consistency metrics"""
        
        if not self.all_operations:
            return ConsistencyMetrics()
        
        total_ops = len(self.all_operations)
        violations_count = len(self.violations)
        
        # Calculate consistency score (1.0 = perfect, 0.0 = terrible)
        consistency_score = max(0.0, 1.0 - (violations_count / max(total_ops, 1)))
        
        # Calculate staleness metrics
        read_operations = [op for op in self.all_operations if op.op_type == "read"]
        current_time = time.time()
        staleness_values = [(current_time - op.timestamp) * 1000 for op in read_operations]
        
        avg_staleness = statistics.mean(staleness_values) if staleness_values else 0.0
        max_staleness = max(staleness_values) if staleness_values else 0.0
        
        # Calculate success rates for different consistency types
        read_after_write_violations = len([v for v in self.violations 
                                          if v.violation_type == ConsistencyViolationType.READ_AFTER_WRITE])
        monotonic_read_violations = len([v for v in self.violations 
                                        if v.violation_type == ConsistencyViolationType.MONOTONIC_READ])
        causal_violations = len([v for v in self.violations 
                               if v.violation_type == ConsistencyViolationType.CAUSAL_ORDER])
        
        session_count = len(self.sessions)
        read_after_write_success = max(0.0, 1.0 - (read_after_write_violations / max(session_count, 1)))
        monotonic_read_success = max(0.0, 1.0 - (monotonic_read_violations / max(session_count, 1)))
        causal_order_success = max(0.0, 1.0 - (causal_violations / max(total_ops, 1)))
        
        return ConsistencyMetrics(
            total_operations=total_ops,
            violations_count=violations_count,
            consistency_score=consistency_score,
            avg_staleness_ms=avg_staleness,
            max_staleness_ms=max_staleness,
            read_after_write_success_rate=read_after_write_success,
            monotonic_read_success_rate=monotonic_read_success,
            causal_order_success_rate=causal_order_success,
            analysis_period_start=datetime.now() - timedelta(minutes=self.analysis_window_minutes),
            analysis_period_end=datetime.now()
        )
    
    def print_analysis_report(self, metrics: ConsistencyMetrics):
        """Print comprehensive analysis report"""
        
        print(f"\n📊 CONSISTENCY ANALYSIS REPORT")
        print("=" * 50)
        
        print(f"Analysis Period: {metrics.analysis_period_start.strftime('%H:%M:%S')} - {metrics.analysis_period_end.strftime('%H:%M:%S')}")
        print(f"Total Operations: {metrics.total_operations}")
        print(f"Total Violations: {metrics.violations_count}")
        print(f"Overall Consistency Score: {metrics.consistency_score:.2%}")
        
        print(f"\n📈 CONSISTENCY METRICS:")
        print(f"Read-after-write success: {metrics.read_after_write_success_rate:.2%}")
        print(f"Monotonic read success: {metrics.monotonic_read_success_rate:.2%}")
        print(f"Causal order success: {metrics.causal_order_success_rate:.2%}")
        
        print(f"\n⏰ STALENESS METRICS:")
        print(f"Average staleness: {metrics.avg_staleness_ms:.0f}ms")
        print(f"Maximum staleness: {metrics.max_staleness_ms:.0f}ms")
        
        # Group violations by type
        violations_by_type = defaultdict(int)
        for violation in self.violations:
            violations_by_type[violation.violation_type] += 1
        
        if violations_by_type:
            print(f"\n🚨 VIOLATIONS BY TYPE:")
            for violation_type, count in violations_by_type.items():
                print(f"  {violation_type.value}: {count}")
        
        # Show critical violations
        critical_violations = [v for v in self.violations if v.severity == "CRITICAL"]
        if critical_violations:
            print(f"\n🚨 CRITICAL VIOLATIONS:")
            for violation in critical_violations[:5]:  # Show top 5
                print(f"  • {violation.description}")
                print(f"    Impact: {violation.business_impact}")
                print(f"    Action: {violation.suggested_action}")
        
        # Consistency level recommendation
        print(f"\n🎯 CONSISTENCY LEVEL ASSESSMENT:")
        if metrics.consistency_score >= 0.95:
            print("✅ STRONG CONSISTENCY - System maintains strong consistency guarantees")
        elif metrics.consistency_score >= 0.80:
            print("🔶 SEQUENTIAL CONSISTENCY - Good consistency with some reordering")
        elif metrics.consistency_score >= 0.60:
            print("🔸 CAUSAL CONSISTENCY - Causally related operations are ordered")
        elif metrics.consistency_score >= 0.40:
            print("🔹 EVENTUAL CONSISTENCY - System will eventually converge")
        else:
            print("❌ WEAK CONSISTENCY - Significant consistency issues detected")

def simulate_paytm_consistency():
    """Simulate Paytm wallet consistency across regions"""
    print("💰 DEMO: Paytm Wallet Consistency Analysis")
    print("-" * 45)
    
    # Create analyzer
    analyzer = ConsistencyAnalyzer()
    
    # Create nodes for different regions
    mumbai_node = DistributedNode("paytm_mumbai", "Mumbai")
    delhi_node = DistributedNode("paytm_delhi", "Delhi") 
    bangalore_node = DistributedNode("paytm_bangalore", "Bangalore")
    
    analyzer.add_node(mumbai_node)
    analyzer.add_node(delhi_node)
    analyzer.add_node(bangalore_node)
    
    # Simulate user operations
    session_id = "user_rajesh_session"
    
    try:
        # User updates wallet in Mumbai
        mumbai_node.write("wallet_balance", 5000, session_id)
        time.sleep(0.1)
        
        # User immediately reads from Delhi (should see recent write)
        delhi_node.read("wallet_balance", session_id)
        
        # Async replication (eventually consistent)
        mumbai_node.sync_with_node(delhi_node, "wallet_balance")
        mumbai_node.sync_with_node(bangalore_node, "wallet_balance")
        
        # More operations
        mumbai_node.write("wallet_balance", 4500, session_id)  # Payment
        time.sleep(0.05)
        bangalore_node.read("wallet_balance", session_id)      # Read from Bangalore
        
        # Concurrent writes (conflict scenario)
        mumbai_node.write("wallet_balance", 4000, session_id)  # User payment
        delhi_node.write("wallet_balance", 4300, session_id)   # Refund processed
        
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Analyze consistency
    metrics = analyzer.analyze_consistency()
    analyzer.print_analysis_report(metrics)

def simulate_flipkart_inventory():
    """Simulate Flipkart inventory consistency"""
    print("\n🛒 DEMO: Flipkart Inventory Consistency")
    print("-" * 40)
    
    analyzer = ConsistencyAnalyzer()
    
    # Create warehouse nodes
    mumbai_warehouse = DistributedNode("flipkart_mumbai_wh", "Mumbai")
    delhi_warehouse = DistributedNode("flipkart_delhi_wh", "Delhi")
    
    analyzer.add_node(mumbai_warehouse)
    analyzer.add_node(delhi_warehouse)
    
    # Simulate inventory operations
    session1 = "inventory_manager_1"
    session2 = "inventory_manager_2"
    
    try:
        # Initial inventory
        mumbai_warehouse.write("iphone14_stock", 100, session1)
        time.sleep(0.1)
        
        # Orders reducing inventory
        mumbai_warehouse.write("iphone14_stock", 99, session1)  # Order 1
        delhi_warehouse.write("iphone14_stock", 98, session2)   # Order 2 (concurrent)
        
        # Read inventory levels
        mumbai_warehouse.read("iphone14_stock", session1)
        delhi_warehouse.read("iphone14_stock", session2)
        
        # Sync inventory between warehouses
        mumbai_warehouse.sync_with_node(delhi_warehouse, "iphone14_stock")
        
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Analyze consistency
    metrics = analyzer.analyze_consistency()
    analyzer.print_analysis_report(metrics)

def main():
    """Main demonstration of consistency analysis"""
    print("🇮🇳 Consistency Level Analyzer - Indian Tech Context")
    print("=" * 60)
    
    # Demo 1: Paytm wallet consistency
    simulate_paytm_consistency()
    
    # Demo 2: Flipkart inventory consistency
    simulate_flipkart_inventory()
    
    print(f"\n✅ Consistency analysis demonstrations complete!")
    
    print(f"\n📚 KEY LEARNINGS:")
    print(f"1. Consistency analysis helps detect system issues early")
    print(f"2. Different violation types have different business impacts")
    print(f"3. Metrics help quantify consistency levels:")
    print(f"   • Strong: 95%+ consistency score")
    print(f"   • Sequential: 80-95% consistency score")
    print(f"   • Eventual: 40-80% consistency score")
    print(f"   • Weak: <40% consistency score")
    print(f"4. Indian context considerations:")
    print(f"   • Network latency between cities")
    print(f"   • Mobile-first architecture challenges")
    print(f"   • Scale requirements vs consistency trade-offs")
    print(f"5. Common violations:")
    print(f"   • Read-after-write: User doesn't see their changes")
    print(f"   • Monotonic read: Data appears to go backward")
    print(f"   • Write conflicts: Concurrent updates clash")
    print(f"6. Business impact awareness crucial for prioritization")

if __name__ == "__main__":
    main()