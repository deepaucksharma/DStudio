# Law 5: Distributed Knowledge - Comprehensive Examination

**Topic**: Distributed Knowledge in Distributed Systems  
**Exam Duration**: 120 minutes  
**Total Points**: 100 points  

## Instructions

This examination tests your mastery of distributed knowledge concepts including CAP theorem implications, consensus algorithms, conflict-free replicated data types (CRDTs), Byzantine fault tolerance, and event sourcing patterns.

**Time Management**:
- Hard Questions (1-5): 60 minutes total (12 minutes each)
- Very Hard Questions (6-8): 60 minutes total (20 minutes each)

**Scoring Rubric**:
- **Technical Excellence** (40%): Correctness, algorithms, calculations
- **System Design** (30%): Architecture, trade-offs, scalability
- **Operational Excellence** (20%): Monitoring, failure handling, recovery
- **Innovation** (10%): Creative solutions, optimization insights

---

## Hard Questions (60 minutes total)

### Question 1: CAP Theorem Trade-offs (12 minutes)
**Points: 12**

You're designing a global inventory management system for an e-commerce platform with data centers in New York, London, and Tokyo.

**Scenario**: 
- 10M products with real-time inventory counts
- Network partitions occur 2-3 times monthly (30-120 minutes each)
- Business requirement: No overselling (inventory must never go negative)
- Performance requirement: <100ms response time for inventory checks

**Part A (4 points)**: Choose your CAP theorem preference (CP or AP) and justify your decision with specific business impact analysis.

**Part B (4 points)**: Design your system architecture showing how you handle:
- Inventory updates during network partitions
- Read operations during partitions  
- Reconciliation after partition recovery

**Part C (4 points)**: Calculate the maximum staleness window and explain the 3f+1 formula application if using consensus (show your work).

---

### Question 2: CRDT Implementation (12 minutes)
**Points: 12**

Implement a CRDT for a collaborative shopping cart that supports adding/removing items and quantity changes.

**Part A (6 points)**: Design the CRDT structure using appropriate types:
```python
class CollaborativeShoppingCart:
    def __init__(self, node_id):
        # Your CRDT design here
        pass
    
    def add_item(self, product_id, quantity, price):
        # Implementation
        pass
    
    def remove_item(self, product_id):
        # Implementation  
        pass
    
    def update_quantity(self, product_id, new_quantity):
        # Implementation
        pass
    
    def merge(self, other_cart):
        # Conflict-free merge implementation
        pass
```

**Part B (3 points)**: Demonstrate convergence by showing two nodes making conflicting updates and reaching the same final state.

**Part C (3 points)**: Explain why your design satisfies the CRDTs mathematical properties (commutativity, associativity, idempotence).

---

### Question 3: Consensus Algorithm Selection (12 minutes) 
**Points: 12**

You need to implement consensus for a distributed configuration service serving 1000+ microservices.

**Requirements**:
- 7 nodes across 3 data centers
- Must tolerate 2 node failures
- Configuration changes are infrequent (5-10 per day)
- Read requests are frequent (1000/sec)
- Strong consistency required

**Part A (4 points)**: Choose between Raft, PBFT, or Gossip protocols. Justify your choice with failure tolerance calculations.

**Part B (4 points)**: Design the leader election process showing:
- Timeout mechanisms
- Vote collection logic
- Split-brain prevention

**Part C (4 points)**: Implement the log replication algorithm:
```python
def replicate_config_change(self, change):
    # Your consensus implementation
    pass
```

---

### Question 4: Byzantine Fault Tolerance (12 minutes)
**Points: 12**

Design a Byzantine fault-tolerant voting system for a blockchain network with 10 nodes.

**Part A (4 points)**: Calculate the maximum number of Byzantine failures you can tolerate. Show your work using the 3f+1 formula.

**Part B (4 points)**: Implement the 3-phase PBFT protocol:
```python
class PBFTVotingNode:
    def pre_prepare_phase(self, proposal):
        # Phase 1 implementation
        pass
    
    def prepare_phase(self, message):
        # Phase 2 implementation  
        pass
    
    def commit_phase(self, message):
        # Phase 3 implementation
        pass
```

**Part C (4 points)**: Design Byzantine attack detection and mitigation strategies including:
- Conflicting message detection
- View change mechanisms
- Node reputation scoring

---

### Question 5: Quorum Systems Design (12 minutes)
**Points: 12**

Design a quorum-based storage system with tunable consistency levels.

**System Parameters**:
- N = 9 replicas across 3 data centers (3 per DC)
- Configurable R (read quorum) and W (write quorum)
- Must handle single data center failures

**Part A (4 points)**: Calculate optimal R and W values for:
- Strong consistency requirements
- High availability requirements  
- Balanced approach

**Part B (4 points)**: Implement the quorum read/write logic:
```python
def quorum_write(self, key, value, consistency_level):
    # Implementation with configurable consistency
    pass

def quorum_read(self, key, consistency_level):
    # Implementation with version resolution
    pass
```

**Part C (4 points)**: Design your split-brain prevention strategy during data center partitions.

---

## Very Hard Questions (60 minutes total)

### Question 6: Event Sourcing with Split-Brain Recovery (20 minutes)
**Points: 20**

Design an event-sourced order management system that can recover from split-brain scenarios.

**Scenario**: 
- Orders processed in two data centers during network partition
- Same order ID processed differently in each partition
- Must maintain audit compliance and financial accuracy

**Part A (8 points)**: Design the event store architecture:
```python
class OrderEventStore:
    def save_events(self, aggregate_id, events, expected_version):
        # Implement with optimistic concurrency control
        pass
    
    def get_events(self, aggregate_id, from_version=0):
        # Event retrieval with filtering
        pass
    
    def resolve_split_brain_conflict(self, partition_a_events, partition_b_events):
        # Conflict resolution algorithm
        pass
```

**Part B (6 points)**: Implement split-brain detection and resolution:
- Detect conflicting event streams
- Design deterministic merge strategy
- Handle compensation events for conflicts

**Part C (6 points)**: Create the audit trail reconstruction:
- Show complete order state at any point in time
- Generate compliance reports showing all state changes
- Implement snapshot optimization for large event streams

---

### Question 7: Complex Coordination Patterns (20 minutes)
**Points: 20**

Build a distributed lock manager with fairness guarantees and deadlock prevention.

**Requirements**:
- Support for multiple lock types (shared/exclusive)
- FIFO ordering for fairness
- Automatic deadlock detection and resolution
- Partition-tolerant operation

**Part A (8 points)**: Design the distributed lock algorithm:
```python
class DistributedLockManager:
    def acquire_lock(self, resource_id, lock_type, timeout):
        # FIFO-ordered lock acquisition with fairness
        pass
    
    def release_lock(self, resource_id, lock_token):
        # Safe lock release with validation
        pass
    
    def detect_deadlocks(self):
        # Deadlock detection algorithm
        pass
```

**Part B (6 points)**: Implement deadlock prevention:
- Wait-die vs wound-wait strategy selection
- Transaction priority assignment
- Automatic rollback mechanisms

**Part C (6 points)**: Design partition handling:
- Lock state during network partitions
- Fencing tokens to prevent dual ownership
- Recovery protocol after partition healing

---

### Question 8: Distributed Knowledge Integration (20 minutes)
**Points: 20**

Design a complete distributed knowledge system integrating multiple patterns.

**Challenge**: Build a globally distributed content management system for a social media platform.

**Requirements**:
- 100M+ posts, 1B+ users across 5 continents
- Real-time collaboration on posts (multiple authors)
- Strong consistency for user authentication
- Eventual consistency acceptable for content distribution
- Must handle submarine cable cuts (continent-level partitions)

**Part A (8 points)**: Design the multi-consistency architecture:
- User service (strong consistency)
- Content service (eventual consistency)  
- Collaboration service (CRDTs)
- Coordination between services

**Part B (6 points)**: Implement the global coordination strategy:
```python
class GlobalContentPlatform:
    def coordinate_cross_service_operation(self, operation):
        # Multi-service coordination
        pass
    
    def handle_continental_partition(self, affected_regions):
        # Partition handling strategy
        pass
    
    def reconcile_after_partition(self, partition_duration):
        # Recovery and reconciliation
        pass
```

**Part C (6 points)**: Design operational excellence:
- Monitoring distributed knowledge consistency
- Automated partition detection and response
- Performance optimization strategies for global scale

---

## Evaluation Criteria

### Technical Excellence (40 points)
- **Algorithm Correctness**: Proper implementation of consensus, CRDTs, event sourcing
- **Mathematical Accuracy**: Correct calculations for 3f+1, quorum sizes, consistency levels  
- **Code Quality**: Clean, production-ready implementations with error handling
- **Protocol Understanding**: Proper application of distributed protocols

### System Design (30 points)
- **Architecture Quality**: Well-structured, scalable system designs
- **Trade-off Analysis**: Clear understanding of CAP theorem implications
- **Failure Handling**: Comprehensive partition and failure recovery strategies
- **Integration Patterns**: Effective coordination between system components

### Operational Excellence (20 points)
- **Monitoring Strategy**: Observable systems with appropriate metrics
- **Recovery Procedures**: Clear operational runbooks for partition scenarios
- **Performance Optimization**: Efficient algorithms and data structures
- **Compliance**: Audit trails and regulatory requirements handling

### Innovation (10 points)
- **Creative Solutions**: Novel approaches to distributed coordination challenges
- **Optimization Insights**: Performance improvements and resource efficiency
- **Advanced Patterns**: Integration of cutting-edge distributed systems concepts
- **Practical Value**: Solutions applicable to real-world production scenarios

---

## Post-Exam Reflection

After completing this exam, reflect on these questions:

1. **Knowledge Gaps**: Which distributed knowledge concepts need further study?
2. **Practical Application**: How would you apply these patterns in your current system?
3. **Trade-off Decisions**: What factors influence your consistency model choices?
4. **Operational Readiness**: Are you prepared to operate these systems in production?

## Additional Resources

- **CAP Theorem**: "CAP Theorem Revisited" by Eric Brewer
- **Consensus Algorithms**: "In Search of an Understandable Consensus Algorithm" (Raft paper)
- **CRDTs**: "A comprehensive study of Convergent and Commutative Replicated Data Types"
- **Byzantine Fault Tolerance**: "Practical Byzantine Fault Tolerance" by Castro and Liskov
- **Event Sourcing**: "Event Sourcing" by Martin Fowler

---

**Estimated Completion Time**: 120 minutes
**Difficulty Level**: Advanced
**Prerequisites**: Understanding of distributed systems fundamentals, basic consensus algorithms, data replication concepts

*This examination validates your ability to design and implement sophisticated distributed knowledge systems that maintain consistency guarantees while providing appropriate availability and partition tolerance for production environments.*