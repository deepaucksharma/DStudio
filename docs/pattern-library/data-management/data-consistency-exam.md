# Data Consistency in Distributed Systems - Comprehensive Examination

## Exam Information

**Duration**: 3 hours (180 minutes)  
**Total Points**: 100 points  
**Format**: Mixed (Conceptual, Implementation, Design, Debugging, Case Study)  
**Difficulty**: Advanced  

### Time Management Guide

- **Conceptual Questions (15)**: 45 minutes (3 min each)
- **Implementation Problems (5)**: 60 minutes (12 min each)
- **System Design Scenarios (3)**: 45 minutes (15 min each)
- **Debugging Exercises (2)**: 20 minutes (10 min each)
- **Case Study (1)**: 10 minutes final review

---

## Part I: Conceptual Questions (30 points, 2 points each)

### Question 1: CAP Theorem Fundamentals
**Scenario**: A global e-commerce platform processes millions of transactions across multiple data centers.

Explain how the CAP theorem applies when:
a) A network partition occurs between US and EU data centers during Black Friday
b) The system must maintain inventory consistency while serving users
c) Compare the trade-offs of choosing CP vs AP in this scenario

### Question 2: Consistency Models Hierarchy
Given the following consistency models, arrange them from strongest to weakest and explain when each would be appropriate:
- Sequential consistency
- Linearizability
- Causal consistency
- Eventual consistency
- Strong consistency

### Question 3: Read-After-Write Consistency
**Banking Context**: A customer transfers $1000 from Account A to Account B.

Design a read-after-write consistency mechanism that ensures:
- The customer sees their updated balance immediately
- Other users eventually see the correct balances
- The system handles concurrent transfers

### Question 4: Vector Clocks vs Logical Clocks
Compare Lamport timestamps and Vector clocks for a social media platform where:
- Users post updates across multiple devices
- Comments must be causally ordered
- The system serves 100M+ users globally

When would you choose each approach?

### Question 5: CRDT Trade-offs
**Gaming Leaderboard**: Design considerations for a real-time leaderboard using CRDTs.

Analyze the trade-offs between:
- G-Counter vs PN-Counter for scores
- OR-Set vs LWW-Set for player rankings
- Memory overhead vs consistency guarantees

### Question 6: Saga Pattern Variants
Compare Orchestrator vs Choreography patterns for an e-commerce order process:

```
Order → Payment → Inventory → Shipping → Notification
```

Discuss failure handling, complexity, and monitoring for each approach.

### Question 7: Distributed Transactions
**Multi-bank Transfer**: $5000 transfer between banks using different databases.

Why would you avoid 2PC in favor of saga patterns? Include:
- Blocking behavior analysis
- Failure scenarios
- Recovery mechanisms

### Question 8: Consensus in Practice
Compare Raft vs Multi-Paxos for:
- A distributed configuration service (like etcd)
- Leader election frequency
- Network partition tolerance
- Implementation complexity

### Question 9: Quorum Systems
Design quorum configurations for a global document store with 9 replicas across 3 regions (3 per region).

Calculate and justify:
- Read quorum (R)
- Write quorum (W)
- Total replicas (N)
For strong consistency vs high availability scenarios.

### Question 10: Causal Consistency Implementation
**Social Network**: Posts, comments, and likes must maintain causal relationships.

Explain how to implement causal consistency using:
- Dependency tracking
- Version vectors
- Client-centric consistency guarantees

### Question 11: Linearizability vs Sequential Consistency
Given this execution:
```
P1: write(x, 1) → read(y) → 0
P2: write(y, 1) → read(x) → 0
```

Is this execution:
a) Linearizable? Why/why not?
b) Sequentially consistent? Why/why not?

### Question 12: Byzantine Fault Tolerance
**Financial Settlement System**: Requires BFT consensus among 7 banks.

Design considerations for:
- PBFT vs other BFT algorithms
- Message complexity
- Performance trade-offs vs crash fault tolerance

### Question 13: Session Guarantees
Implement session guarantees for a distributed shopping cart:
- Read your writes
- Monotonic reads
- Monotonic writes
- Writes follow reads

### Question 14: Conflict-Free Replicated Data Types
**Collaborative Document Editor**: Choose appropriate CRDTs for:
- Text editing (insertions/deletions)
- User presence indicators
- Document permissions
- Comment threads

### Question 15: Consistency vs Performance
**Trading Platform**: Sub-millisecond latency requirements with strict consistency needs.

Analyze the tension between:
- Synchronous replication for consistency
- Asynchronous replication for performance
- Hybrid approaches and their trade-offs

---

## Part II: Implementation Problems (25 points, 5 points each)

### Problem 1: Vector Clock Implementation (5 points)
Implement a vector clock system for a distributed chat application:

```python
class VectorClock:
    def __init__(self, node_id, nodes):
        """
        Initialize vector clock for a node
        node_id: unique identifier for this node
        nodes: list of all node identifiers
        """
        pass
    
    def tick(self):
        """Increment local counter"""
        pass
    
    def update(self, other_clock):
        """Update with received vector clock"""
        pass
    
    def happens_before(self, other_clock):
        """Check if this event happens before other"""
        pass
    
    def concurrent(self, other_clock):
        """Check if events are concurrent"""
        pass
```

**Test your implementation with this scenario**:
```
Node A sends message M1 (tick, send)
Node B receives M1, sends M2 (update, tick, send)  
Node C receives both M1 and M2
```

### Problem 2: Saga Orchestrator (5 points)
Implement a saga orchestrator for order processing:

```python
class SagaOrchestrator:
    def __init__(self):
        self.steps = []
        self.compensations = []
    
    def add_step(self, action, compensation):
        """Add a step with its compensation"""
        pass
    
    async def execute(self, context):
        """Execute saga with failure handling"""
        pass
    
    async def compensate(self, context, failed_step):
        """Execute compensating actions"""
        pass

# Usage example:
saga = SagaOrchestrator()
saga.add_step(reserve_inventory, release_inventory)
saga.add_step(process_payment, refund_payment)
saga.add_step(ship_order, cancel_shipment)
```

### Problem 3: Read-After-Write Consistency (5 points)
Implement read-after-write consistency for a user profile service:

```python
class ConsistentProfileService:
    def __init__(self):
        self.primary_db = None
        self.read_replicas = []
        self.user_sessions = {}  # track user writes
    
    async def update_profile(self, user_id, profile_data, session_id):
        """Update profile ensuring read-after-write"""
        pass
    
    async def get_profile(self, user_id, session_id):
        """Get profile with read-after-write guarantee"""
        pass
    
    def _should_read_from_primary(self, user_id, session_id):
        """Determine if should read from primary"""
        pass
```

### Problem 4: CRDT G-Counter (5 points)
Implement a grow-only counter CRDT for distributed analytics:

```python
class GCounter:
    def __init__(self, node_id, nodes):
        """
        Initialize G-Counter
        node_id: this node's identifier
        nodes: all node identifiers in the system
        """
        pass
    
    def increment(self, value=1):
        """Increment counter by value"""
        pass
    
    def value(self):
        """Get current counter value"""
        pass
    
    def merge(self, other_counter):
        """Merge with another G-Counter"""
        pass
    
    def state(self):
        """Return internal state for replication"""
        pass
```

### Problem 5: Quorum-Based Storage (5 points)
Implement a quorum-based key-value store:

```python
class QuorumKVStore:
    def __init__(self, nodes, read_quorum, write_quorum):
        self.nodes = nodes
        self.r = read_quorum
        self.w = write_quorum
        self.local_data = {}
    
    async def write(self, key, value, version):
        """Write with quorum consistency"""
        pass
    
    async def read(self, key):
        """Read with quorum consistency"""
        pass
    
    def _resolve_conflicts(self, responses):
        """Resolve version conflicts"""
        pass
```

---

## Part III: System Design Scenarios (30 points, 10 points each)

### Scenario 1: Global Banking System (10 points)
**Context**: Design a distributed banking system spanning 5 continents with the following requirements:

**Requirements**:
- Handle 1M+ transactions per second globally
- Strict ACID compliance for monetary operations
- Sub-second balance queries
- 99.99% availability
- Cross-border transfers within 30 seconds

**Design Tasks**:
1. Choose consistency model and justify
2. Design transaction processing flow
3. Handle network partitions
4. Implement conflict resolution
5. Design monitoring and alerting

**Consider**:
- Regulatory compliance (GDPR, PCI-DSS)
- Disaster recovery
- Audit trails
- Performance optimization

### Scenario 2: Real-time Gaming Leaderboard (10 points)
**Context**: Design a leaderboard system for a battle royale game with 100M players.

**Requirements**:
- Real-time score updates (< 100ms latency)
- Global and regional rankings
- Handle 10K+ concurrent matches
- Anti-cheat integration
- Historical statistics

**Design Tasks**:
1. Choose appropriate CRDT types
2. Design score aggregation strategy
3. Handle concurrent updates
4. Implement ranking algorithms
5. Design caching strategy

**Consider**:
- Cheating prevention
- Seasonal resets
- Performance under load
- Data consistency guarantees

### Scenario 3: Social Media Content Distribution (10 points)
**Context**: Design content consistency for a Twitter-like platform with 500M users.

**Requirements**:
- Posts appear in followers' feeds consistently
- Handle viral content (1M+ interactions/minute)
- Support real-time comments and likes
- Global content moderation
- Personalized timeline consistency

**Design Tasks**:
1. Choose timeline consistency model
2. Design content propagation
3. Handle viral content scaling
4. Implement causal ordering for comments
5. Design content moderation integration

**Consider**:
- Celebrity accounts with millions of followers
- Geographic content restrictions
- Content editing and deletion
- Feed ranking algorithms

---

## Part IV: Debugging Exercises (10 points, 5 points each)

### Debug Exercise 1: Distributed Deadlock (5 points)
**Scenario**: An e-commerce platform experiences intermittent order processing failures.

```python
# Transaction logs show this pattern:
# Node A: BEGIN → LOCK inventory_item_123 → LOCK user_account_456
# Node B: BEGIN → LOCK user_account_456 → LOCK inventory_item_123
# Result: Both transactions timeout after 30 seconds

class OrderProcessor:
    async def process_order(self, user_id, item_id, quantity):
        async with self.db.transaction():
            # Step 1: Lock inventory
            inventory = await self.db.lock_row(
                "inventory", 
                f"item_id = {item_id}"
            )
            
            # Step 2: Lock user account
            account = await self.db.lock_row(
                "accounts", 
                f"user_id = {user_id}"
            )
            
            # Step 3: Process business logic
            if inventory.quantity >= quantity:
                inventory.quantity -= quantity
                account.balance -= inventory.price * quantity
                
                await self.db.save(inventory)
                await self.db.save(account)
                return True
            return False
```

**Tasks**:
1. Identify the root cause of the deadlock
2. Propose 3 different solutions
3. Analyze trade-offs of each solution
4. Implement the best solution with code

### Debug Exercise 2: Consistency Violation (5 points)
**Scenario**: A distributed counter shows inconsistent values across regions.

```python
# Observed behavior:
# Region US: Counter = 1247
# Region EU: Counter = 1251  
# Region ASIA: Counter = 1243
# 
# Expected: All regions should eventually converge

class DistributedCounter:
    def __init__(self, region_id):
        self.region_id = region_id
        self.value = 0
        self.vector_clock = {}
    
    async def increment(self, amount=1):
        self.value += amount
        self.vector_clock[self.region_id] += 1
        
        # Replicate to other regions
        await self.replicate_to_peers({
            'value': self.value,
            'vector_clock': self.vector_clock,
            'operation': 'increment',
            'amount': amount
        })
    
    async def handle_replication(self, message):
        remote_clock = message['vector_clock']
        
        # Update local state
        if self._is_newer(remote_clock):
            self.value = message['value']
            self.vector_clock.update(remote_clock)
    
    def _is_newer(self, remote_clock):
        # Bug is likely here
        return any(
            remote_clock.get(region, 0) > self.vector_clock.get(region, 0)
            for region in remote_clock
        )
```

**Tasks**:
1. Identify why counters aren't converging
2. Explain the semantic issue with the increment operation
3. Fix the implementation to ensure eventual consistency
4. Propose testing strategy to prevent regression

---

## Part V: Case Study (5 points)

### Case Study: Netflix Content Distribution Consistency

**Background**: Netflix serves 200M+ subscribers globally with a catalog of 15,000+ titles. Content availability varies by region due to licensing, and the system must handle:

- New content launches (global synchronization)
- Regional content removal
- User watch history consistency
- Recommendation engine data consistency
- A/B test consistency for UI changes

**The Problem**: 
During a major movie release, Netflix experienced:
1. Some users couldn't see the new movie despite global launch
2. Watch progress sync issues across devices  
3. Recommendations showed unavailable content
4. A/B test variants inconsistently applied

**System Architecture**:
```
Global Catalog Service (Master) → Regional CDN Caches → Client Apps
User Data Service → Multiple DCs → Device Sync
Recommendation Engine → ML Pipeline → Content Ranking
A/B Test Service → Feature Flags → UI Rendering
```

**Your Task**: 
Analyze this multi-faceted consistency problem and propose a comprehensive solution addressing:

1. **Content Catalog Consistency**: How to ensure global content launches are atomic across regions while handling licensing restrictions

2. **User Data Consistency**: Design watch progress synchronization across devices with offline capability

3. **Cross-Service Consistency**: Ensure recommendations only show available content and A/B tests are consistently applied

4. **Performance vs Consistency**: Balance consistency requirements with Netflix's <1 second response time goals

5. **Failure Handling**: Design system behavior during:
   - Regional data center failures
   - Network partitions between regions
   - Partial service degradation

**Deliverables**:
- Consistency model choice and justification
- Service interaction design
- Conflict resolution strategies
- Monitoring and alerting approach
- Recovery procedures

---

## Answer Key and Solutions

### Part I Solutions: Conceptual Questions

#### Question 1: CAP Theorem Application
**Answer**: 
a) **Network partition scenario**: During Black Friday with US-EU partition, the system faces a classic CP vs AP choice. The platform must choose between:
- **CP approach**: Stop serving requests that require cross-region consistency, maintaining data consistency but sacrificing availability
- **AP approach**: Continue serving requests in each region independently, maintaining availability but risking inventory overselling

b) **Inventory consistency**: The challenge is maintaining accurate inventory counts across regions while serving customers. Solutions include:
- Regional inventory allocation with reserved buffers
- Conflict resolution protocols for overselling scenarios
- Compensating transactions for inventory corrections

c) **Trade-off analysis**:
- **CP Choice**: Ensures no overselling but may result in lost sales during network issues
- **AP Choice**: Maximizes sales but may lead to overselling and customer disappointment
- **Recommendation**: Hybrid approach with inventory buffers and eventual consistency for non-critical data

#### Question 2: Consistency Models Hierarchy
**Answer** (Strongest to Weakest):
1. **Linearizability** - Operations appear to execute atomically at some point between start and completion
2. **Strong Consistency** - All nodes see the same data simultaneously  
3. **Sequential Consistency** - Operations appear to execute in some sequential order consistent with program order
4. **Causal Consistency** - Operations that are causally related are seen in the same order by all nodes
5. **Eventual Consistency** - All nodes will eventually converge to the same state

**When to use each**:
- **Linearizability**: Financial transactions, critical system state
- **Sequential**: Distributed databases with ACID requirements  
- **Causal**: Social networks, collaborative systems
- **Eventual**: Content distribution, shopping carts, user profiles

#### Question 3: Read-After-Write Banking Solution
**Answer**:
```python
class BankingService:
    def __init__(self):
        self.primary_db = PrimaryDatabase()
        self.read_replicas = [ReplicaDatabase() for _ in range(3)]
        self.user_write_tracker = {}
    
    async def transfer_funds(self, user_id, from_account, to_account, amount):
        # Write to primary with timestamp
        write_timestamp = await self.primary_db.execute_transaction({
            'from_account': from_account,
            'to_account': to_account, 
            'amount': amount,
            'timestamp': time.now()
        })
        
        # Track user's last write
        self.user_write_tracker[user_id] = write_timestamp
        
        return write_timestamp
    
    async def get_balance(self, user_id, account_id):
        user_last_write = self.user_write_tracker.get(user_id, 0)
        
        # For reads after writes, use primary DB
        if user_last_write and (time.now() - user_last_write < REPLICATION_LAG):
            return await self.primary_db.get_balance(account_id)
        
        # Otherwise use load-balanced replicas
        replica = self._choose_replica()
        return await replica.get_balance(account_id)
```

### Part II Solutions: Implementation Problems

#### Problem 1: Vector Clock Solution
```python
class VectorClock:
    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = sorted(nodes)  # Ensure consistent ordering
        self.clock = {node: 0 for node in self.nodes}
    
    def tick(self):
        """Increment local counter"""
        self.clock[self.node_id] += 1
        return self.copy()
    
    def update(self, other_clock):
        """Update with received vector clock"""
        for node in self.nodes:
            self.clock[node] = max(
                self.clock[node], 
                other_clock.clock.get(node, 0)
            )
        # Increment local clock
        self.clock[self.node_id] += 1
    
    def happens_before(self, other_clock):
        """Check if this event happens before other"""
        # Self <= other AND self != other
        all_less_equal = all(
            self.clock[node] <= other_clock.clock.get(node, 0)
            for node in self.nodes
        )
        at_least_one_less = any(
            self.clock[node] < other_clock.clock.get(node, 0)
            for node in self.nodes
        )
        return all_less_equal and at_least_one_less
    
    def concurrent(self, other_clock):
        """Check if events are concurrent"""
        return not (self.happens_before(other_clock) or 
                   other_clock.happens_before(self))
    
    def copy(self):
        new_clock = VectorClock(self.node_id, self.nodes)
        new_clock.clock = self.clock.copy()
        return new_clock

# Test scenario
node_a = VectorClock('A', ['A', 'B', 'C'])
node_b = VectorClock('B', ['A', 'B', 'C']) 
node_c = VectorClock('C', ['A', 'B', 'C'])

# A sends M1
m1_clock = node_a.tick()

# B receives M1, sends M2
node_b.update(m1_clock)
m2_clock = node_b.tick()

# C receives both
node_c.update(m1_clock)
node_c.update(m2_clock)
```

#### Problem 2: Saga Orchestrator Solution
```python
import asyncio
from enum import Enum
from typing import List, Callable, Any, Dict

class SagaStatus(Enum):
    STARTED = "started"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"

class SagaStep:
    def __init__(self, name: str, action: Callable, compensation: Callable):
        self.name = name
        self.action = action
        self.compensation = compensation

class SagaOrchestrator:
    def __init__(self):
        self.steps: List[SagaStep] = []
        self.completed_steps: List[int] = []
        self.status = SagaStatus.STARTED
    
    def add_step(self, name: str, action: Callable, compensation: Callable):
        """Add a step with its compensation"""
        step = SagaStep(name, action, compensation)
        self.steps.append(step)
    
    async def execute(self, context: Dict[str, Any]) -> bool:
        """Execute saga with failure handling"""
        try:
            for i, step in enumerate(self.steps):
                print(f"Executing step {i}: {step.name}")
                
                # Execute the step
                result = await step.action(context)
                
                if not result:
                    print(f"Step {i} failed, starting compensation")
                    await self.compensate(context, i)
                    return False
                
                self.completed_steps.append(i)
            
            self.status = SagaStatus.COMPLETED
            return True
            
        except Exception as e:
            print(f"Exception during saga execution: {e}")
            await self.compensate(context, len(self.completed_steps))
            return False
    
    async def compensate(self, context: Dict[str, Any], failed_step: int):
        """Execute compensating actions"""
        self.status = SagaStatus.COMPENSATING
        
        # Compensate in reverse order
        for step_index in reversed(self.completed_steps):
            step = self.steps[step_index]
            try:
                print(f"Compensating step {step_index}: {step.name}")
                await step.compensation(context)
            except Exception as e:
                print(f"Compensation failed for step {step_index}: {e}")
        
        self.status = SagaStatus.FAILED

# Usage example with order processing:
async def reserve_inventory(context):
    print(f"Reserving {context['quantity']} items")
    # Simulate inventory check
    if context['quantity'] > 100:  # Simulate insufficient stock
        return False
    context['inventory_reserved'] = True
    return True

async def release_inventory(context):
    print("Releasing inventory reservation")
    context['inventory_reserved'] = False

async def process_payment(context):
    print(f"Processing payment of ${context['amount']}")
    # Simulate payment processing
    context['payment_processed'] = True
    return True

async def refund_payment(context):
    print("Refunding payment")
    context['payment_processed'] = False

async def ship_order(context):
    print("Shipping order")
    context['order_shipped'] = True
    return True

async def cancel_shipment(context):
    print("Canceling shipment")
    context['order_shipped'] = False

# Test the saga
async def test_saga():
    saga = SagaOrchestrator()
    saga.add_step("Reserve Inventory", reserve_inventory, release_inventory)
    saga.add_step("Process Payment", process_payment, refund_payment)
    saga.add_step("Ship Order", ship_order, cancel_shipment)
    
    context = {
        'quantity': 50,  # Change to 150 to test failure
        'amount': 99.99
    }
    
    success = await saga.execute(context)
    print(f"Saga completed successfully: {success}")
```

### Part III Solutions: System Design Scenarios

#### Scenario 1: Global Banking System Solution

**1. Consistency Model Choice**:
- **Strong consistency** for monetary operations using synchronous replication
- **Eventual consistency** for non-critical data (user preferences, notifications)
- **Causal consistency** for related transactions (transfer sequences)

**2. Architecture Design**:
```
Regional Transaction Coordinators
├── Primary Transaction DB (Strong Consistency)
├── Read Replicas (Timeline Consistency) 
├── Event Store (Immutable Transaction Log)
└── Cross-Region Sync (Saga Pattern)

Cross-Border Transfer Flow:
1. Source bank validates and reserves funds
2. Compliance checks and regulatory validation  
3. Cross-border message via secure channel
4. Destination bank credits account
5. Settlement reconciliation
6. Notification to both parties
```

**3. Network Partition Handling**:
- Regional autonomy for domestic transactions
- Cross-border transfers queue during partitions
- Automated reconciliation when partition heals
- Manual intervention protocols for extended outages

**4. Implementation Details**:
```python
class GlobalBankingOrchestrator:
    async def cross_border_transfer(self, transfer_request):
        saga = TransferSaga()
        saga.add_step("validate_source", self.validate_and_reserve)
        saga.add_step("compliance_check", self.regulatory_validation)  
        saga.add_step("cross_border_message", self.send_swift_message)
        saga.add_step("destination_credit", self.credit_destination)
        saga.add_step("settlement", self.record_settlement)
        
        return await saga.execute(transfer_request)
```

#### Scenario 2: Gaming Leaderboard Solution

**1. CRDT Selection**:
- **G-Counter** for individual player scores (monotonic increases)
- **OR-Set** for active players in leaderboard
- **LWW-Register** for player metadata (name, level)

**2. Architecture Design**:
```
Game Servers → Regional Score Aggregators → Global Leaderboard
              ↓
           CRDT Merge Points → Ranking Service → Client APIs
```

**3. Implementation**:
```python
class GameLeaderboard:
    def __init__(self, region_id):
        self.region_id = region_id
        self.player_scores = {}  # player_id -> G-Counter
        self.ranking_cache = []
        self.last_update = 0
    
    async def update_score(self, player_id, points):
        if player_id not in self.player_scores:
            self.player_scores[player_id] = GCounter(self.region_id, ALL_REGIONS)
        
        self.player_scores[player_id].increment(points)
        await self.propagate_update(player_id, points)
        self.invalidate_ranking_cache()
    
    async def get_top_players(self, limit=100):
        if self.needs_ranking_update():
            await self.rebuild_rankings()
        return self.ranking_cache[:limit]
    
    def merge_from_region(self, other_region_data):
        for player_id, counter_state in other_region_data.items():
            if player_id not in self.player_scores:
                self.player_scores[player_id] = GCounter(self.region_id, ALL_REGIONS)
            self.player_scores[player_id].merge(counter_state)
```

### Part IV Solutions: Debugging Exercises

#### Debug Exercise 1: Distributed Deadlock Solution

**Root Cause**: Classic deadlock due to inconsistent lock ordering between transactions.

**Solutions**:

1. **Lock Ordering Solution** (Recommended):
```python
class OrderProcessor:
    async def process_order(self, user_id, item_id, quantity):
        # Always lock in consistent order: inventory first, then account
        lock_order = [f"inventory:{item_id}", f"account:{user_id}"]
        lock_order.sort()  # Ensures consistent ordering
        
        async with self.db.transaction():
            for lock_key in lock_order:
                await self.db.acquire_lock(lock_key)
            
            # Business logic remains the same
            inventory = await self.db.get("inventory", item_id)
            account = await self.db.get("accounts", user_id)
            
            if inventory.quantity >= quantity:
                inventory.quantity -= quantity
                account.balance -= inventory.price * quantity
                
                await self.db.save(inventory)
                await self.db.save(account)
                return True
            return False
```

2. **Timeout with Retry**:
```python
async def process_order_with_retry(self, user_id, item_id, quantity, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await self.process_order_with_timeout(user_id, item_id, quantity)
        except DeadlockException:
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Jittered backoff
    raise MaxRetriesExceededException()
```

3. **Optimistic Locking**:
```python
async def process_order_optimistic(self, user_id, item_id, quantity):
    while True:
        # Read with version numbers
        inventory = await self.db.get_with_version("inventory", item_id)
        account = await self.db.get_with_version("accounts", user_id)
        
        if inventory.quantity >= quantity:
            # Attempt atomic update
            try:
                await self.db.update_with_version("inventory", inventory.version, {
                    'quantity': inventory.quantity - quantity
                })
                await self.db.update_with_version("accounts", account.version, {
                    'balance': account.balance - (inventory.price * quantity)
                })
                return True
            except VersionMismatchException:
                continue  # Retry
        return False
```

#### Debug Exercise 2: Consistency Violation Solution

**Root Cause**: The `_is_newer` method incorrectly handles concurrent updates. It only checks if any timestamp is newer, not if the entire vector clock represents a newer state.

**Fixed Implementation**:
```python
class DistributedCounter:
    def __init__(self, region_id):
        self.region_id = region_id
        self.counters = {region_id: 0}  # Per-region counters
        self.vector_clock = {region_id: 0}
    
    async def increment(self, amount=1):
        # Update local counter and vector clock
        self.counters[self.region_id] += amount
        self.vector_clock[self.region_id] += 1
        
        # Replicate to other regions
        await self.replicate_to_peers({
            'region_id': self.region_id,
            'counters': self.counters,
            'vector_clock': self.vector_clock,
            'operation': 'increment',
            'amount': amount
        })
    
    async def handle_replication(self, message):
        remote_region = message['region_id']
        remote_counters = message['counters']
        remote_clock = message['vector_clock']
        
        # Merge counters (taking maximum for each region)
        for region, count in remote_counters.items():
            self.counters[region] = max(
                self.counters.get(region, 0), 
                count
            )
        
        # Merge vector clocks
        for region, timestamp in remote_clock.items():
            self.vector_clock[region] = max(
                self.vector_clock.get(region, 0),
                timestamp
            )
    
    def value(self):
        """Total counter value across all regions"""
        return sum(self.counters.values())
```

**Key Fixes**:
1. Separate per-region counters instead of single global counter
2. Proper CRDT merge semantics (taking maximum per region)
3. Correct vector clock merging

### Part V Solution: Netflix Case Study

**Comprehensive Solution Architecture**:

**1. Content Catalog Consistency**:
```python
class GlobalContentOrchestrator:
    async def launch_content_globally(self, content_id, regional_restrictions):
        # Use distributed transaction across regions
        launch_saga = ContentLaunchSaga()
        
        for region in REGIONS:
            if region not in regional_restrictions:
                launch_saga.add_step(
                    f"launch_{region}",
                    lambda: self.launch_in_region(content_id, region),
                    lambda: self.remove_from_region(content_id, region)
                )
        
        # Execute with compensation on failure
        return await launch_saga.execute({
            'content_id': content_id,
            'launch_time': datetime.utcnow()
        })
```

**2. User Data Consistency Design**:
```python
class WatchProgressService:
    def __init__(self):
        self.vector_clocks = {}  # user_id -> VectorClock
        self.conflict_resolver = LastWriterWinsResolver()
    
    async def update_progress(self, user_id, device_id, content_id, position):
        # Update with vector clock
        clock = self.vector_clocks.get(user_id, VectorClock(device_id, ALL_DEVICES))
        clock.tick()
        
        update = {
            'user_id': user_id,
            'device_id': device_id, 
            'content_id': content_id,
            'position': position,
            'vector_clock': clock.state(),
            'timestamp': time.utcnow()
        }
        
        # Replicate to other devices
        await self.replicate_to_user_devices(user_id, update)
```

**3. Cross-Service Consistency**:
```python
class ConsistentRecommendationService:
    async def get_recommendations(self, user_id, region):
        # Get user's content availability view
        available_content = await self.content_service.get_available_content(
            region, 
            consistent_read=True
        )
        
        # Get recommendations with availability filter
        recommendations = await self.ml_service.get_recommendations(user_id)
        
        # Filter by availability with eventual consistency tolerance
        filtered_recs = [
            rec for rec in recommendations 
            if rec.content_id in available_content or 
               await self.is_eventually_available(rec.content_id, region)
        ]
        
        return filtered_recs
```

**4. Monitoring and Alerting**:
```python
class ConsistencyMonitor:
    def __init__(self):
        self.metrics = ConsistencyMetrics()
    
    async def check_content_consistency(self):
        """Monitor content catalog consistency across regions"""
        inconsistencies = []
        
        for content_id in self.get_critical_content():
            regional_states = await self.get_regional_availability(content_id)
            
            if not self.is_consistent(regional_states):
                inconsistencies.append({
                    'content_id': content_id,
                    'regions': regional_states,
                    'severity': self.calculate_impact(content_id)
                })
        
        if inconsistencies:
            await self.alert_operations_team(inconsistencies)
```

**Key Design Principles Applied**:
1. **Hybrid Consistency**: Strong consistency for critical paths, eventual for others
2. **Compensation Patterns**: Saga pattern for multi-region operations
3. **Vector Clocks**: For user data synchronization across devices
4. **Circuit Breakers**: Fallback to cached data during consistency violations
5. **Monitoring**: Real-time consistency violation detection

**Performance vs Consistency Balance**:
- Critical user actions (play, pause): Strong consistency with <100ms timeout
- Recommendations: Eventual consistency with 5-minute staleness tolerance  
- Content metadata: Regional consistency with global eventual convergence
- A/B test assignments: Session-level consistency with sticky routing

This comprehensive solution addresses all aspects of Netflix's multi-faceted consistency challenges while maintaining performance requirements.

---

## Grading Rubric

### Part I - Conceptual Questions (30 points)
- **Excellent (2 points)**: Complete understanding with practical examples
- **Good (1.5 points)**: Good grasp with minor gaps  
- **Satisfactory (1 point)**: Basic understanding, lacks depth
- **Poor (0.5 points)**: Minimal understanding
- **No Answer (0 points)**: No response or completely incorrect

### Part II - Implementation Problems (25 points)  
- **Excellent (5 points)**: Working code with edge cases handled
- **Good (4 points)**: Working code with minor issues
- **Satisfactory (3 points)**: Basic implementation, some bugs
- **Poor (2 points)**: Significant issues, partial functionality
- **No Answer (0 points)**: No implementation attempt

### Part III - System Design (30 points)
- **Excellent (10 points)**: Comprehensive design with trade-offs analysis
- **Good (8 points)**: Good design with most requirements addressed  
- **Satisfactory (6 points)**: Basic design, missing some requirements
- **Poor (4 points)**: Limited design, significant gaps
- **No Answer (0 points)**: No design provided

### Part IV - Debugging (10 points)
- **Excellent (5 points)**: Root cause identified with multiple solutions
- **Good (4 points)**: Correct diagnosis with viable solution
- **Satisfactory (3 points)**: Partial diagnosis, basic solution
- **Poor (2 points)**: Incorrect diagnosis or poor solution  
- **No Answer (0 points)**: No debugging attempt

### Part V - Case Study (5 points)
- **Excellent (5 points)**: Comprehensive analysis with innovative solutions
- **Good (4 points)**: Good analysis addressing most aspects
- **Satisfactory (3 points)**: Basic analysis, limited depth
- **Poor (2 points)**: Surface-level analysis  
- **No Answer (0 points)**: No analysis provided

### Overall Grade Scale
- **A (90-100 points)**: Exceptional understanding of distributed consistency
- **B (80-89 points)**: Strong grasp with good practical application
- **C (70-79 points)**: Adequate understanding, needs improvement  
- **D (60-69 points)**: Basic understanding, significant gaps
- **F (Below 60 points)**: Insufficient understanding for production systems

---

## Additional Study Resources

### Recommended Papers
1. "Consistency in Non-Transactional Distributed Storage Systems" - Viotti & Vukolić
2. "Dynamo: Amazon's Highly Available Key-value Store" - DeCandia et al.
3. "In Search of an Understandable Consensus Algorithm" - Raft Paper
4. "Time, Clocks, and the Ordering of Events" - Lamport
5. "Conflict-free Replicated Data Types" - Shapiro et al.

### Online Resources
- Jepsen.io (distributed systems testing)
- High Scalability blog
- AWS Architecture Center
- Google SRE Book (Consistency chapters)
- Martin Kleppmann's "Designing Data-Intensive Applications"

### Practical Labs
1. Implement Raft consensus in your preferred language
2. Build a distributed key-value store with quorum consistency
3. Create CRDT implementations for collaborative editing
4. Design and test saga patterns for microservices
5. Implement vector clocks for event ordering

Good luck with your examination!