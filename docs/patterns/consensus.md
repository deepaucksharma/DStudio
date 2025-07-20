---
title: Consensus Pattern
description: Achieving agreement among distributed nodes in the presence of failures
type: pattern
difficulty: advanced
reading_time: 30 min
prerequisites: []
pattern_type: "coordination"
when_to_use: "Leader election, distributed configuration, replicated state machines"
when_not_to_use: "High-throughput data processing, eventually consistent systems"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Consensus Pattern**


# Consensus Pattern

**Agreement in a world of unreliable networks and failing nodes**

> *"Consensus is impossibly hard in theory, merely very hard in practice."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 5: Coordination](/part1-axioms/axiom5-coordination/) - Distributed agreement
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Handling node failures

**🔧 Solves These Problems**:
- Split-brain scenarios
- Distributed configuration management
- Replicated state machines
- Ordering of distributed events

**🤝 Works Best With**:
- [Leader Election](/patterns/leader-election/) - Choosing coordinators
- [Distributed Lock](/patterns/distributed-lock/) - Mutual exclusion
- [Event Sourcing](/patterns/event-sourcing/) - Ordered event logs
</div>

---

## 🎯 Level 1: Intuition

### The Jury Deliberation Analogy

Consensus is like a jury reaching a verdict:
- **Unanimous decision**: All jurors must agree
- **Majority rule**: More than half must agree
- **Discussion rounds**: Multiple rounds of voting
- **No changing minds**: Once decided, verdict stands

The challenge: What if some jurors leave mid-deliberation?

### Basic Consensus Concepts

```python
from enum import Enum
from typing import List, Optional, Dict

class ConsensusState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate" 
    LEADER = "leader"

class SimpleConsensus:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.state = ConsensusState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []
        
    def propose_value(self, value: any) -> bool:
        """Propose a value for consensus"""
        if self.state != ConsensusState.LEADER:
            return False  # Only leader can propose
        
        # Simplified: broadcast to all peers
        votes = 1  # Self vote
        
        for peer in self.peers:
            if self.get_vote_from_peer(peer, value):
                votes += 1
        
        # Need majority
        if votes > len(self.peers) // 2 + 1:
            self.log.append(value)
            self.broadcast_commit(value)
            return True
        
        return False
    
    def get_vote_from_peer(self, peer: str, value: any) -> bool:
        """Request vote from peer (simplified)"""
        # In reality, this would be an RPC call
        # Peer votes yes if value is acceptable
        return True  # Simplified
```

---

## 🏗️ Level 2: Foundation

### Consensus Properties

| Property | Description | Why It Matters |
|----------|-------------|----------------|
| **Agreement** | All nodes decide same value | Consistency |
| **Validity** | Decided value was proposed | No arbitrary decisions |
| **Termination** | Eventually decides | Progress guarantee |
| **Integrity** | Decide at most once | No flip-flopping |

### Implementing Basic Paxos

```python
import time
from dataclasses import dataclass
from typing import Optional, Tuple, Set

@dataclass
class Proposal:
    number: int
    value: any

class PaxosNode:
    """Basic Paxos implementation"""
    
    def __init__(self, node_id: int, nodes: Set[int]):
        self.node_id = node_id
        self.nodes = nodes
        self.quorum_size = len(nodes) // 2 + 1
        
        # Proposer state
        self.proposal_number = 0
        
        # Acceptor state
        self.promised_proposal = None
        self.accepted_proposal = None
        
    def propose(self, value: any) -> Optional[any]:
        """Propose a value (Proposer role)"""
        # Phase 1: Prepare
        self.proposal_number += 1
        proposal_num = self.proposal_number * 100 + self.node_id
        
        promises = self.send_prepare(proposal_num)
        
        if len(promises) < self.quorum_size:
            return None  # No quorum
        
        # Find highest numbered accepted proposal
        highest_accepted = None
        for promise in promises:
            if promise['accepted'] and (
                not highest_accepted or 
                promise['accepted'].number > highest_accepted.number
            ):
                highest_accepted = promise['accepted']
        
        # Phase 2: Accept
        if highest_accepted:
            # Must use previously accepted value
            final_value = highest_accepted.value
        else:
            # Can use our proposed value
            final_value = value
        
        proposal = Proposal(proposal_num, final_value)
        accepts = self.send_accept(proposal)
        
        if len(accepts) >= self.quorum_size:
            return final_value
        
        return None
    
    def handle_prepare(self, proposal_num: int) -> dict:
        """Handle prepare request (Acceptor role)"""
        if self.promised_proposal is None or proposal_num > self.promised_proposal:
            self.promised_proposal = proposal_num
            return {
                'promise': True,
                'accepted': self.accepted_proposal
            }
        
        return {'promise': False}
    
    def handle_accept(self, proposal: Proposal) -> bool:
        """Handle accept request (Acceptor role)"""
        if self.promised_proposal is None or proposal.number >= self.promised_proposal:
            self.promised_proposal = proposal.number
            self.accepted_proposal = proposal
            return True
        
        return False
```

### Multi-Paxos for Log Replication

```python
class MultiPaxos:
    """Multi-Paxos for replicated log"""
    
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.log = []  # Replicated log
        self.current_leader = None
        self.last_applied = -1
        
    def append_entry(self, entry: dict) -> bool:
        """Append entry to replicated log"""
        if self.current_leader != self.node_id:
            # Forward to leader
            return self.forward_to_leader(entry)
        
        # Leader path
        log_index = len(self.log)
        
        # Run Paxos for this log slot
        if self.run_paxos_for_slot(log_index, entry):
            self.log.append(entry)
            self.replicate_to_followers(log_index, entry)
            return True
        
        return False
    
    def run_paxos_for_slot(self, slot: int, value: any) -> bool:
        """Run Paxos for specific log slot"""
        # Optimization: leader can skip prepare phase
        # if it's still the recognized leader
        
        if self.am_i_still_leader():
            # Fast path: skip prepare
            return self.fast_paxos(slot, value)
        else:
            # Full Paxos
            return self.full_paxos(slot, value)
```

---

## 🔧 Level 3: Deep Dive

### Raft Consensus Algorithm

```python
import random
import asyncio
from enum import Enum
from typing import List, Optional, Dict

class RaftState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class LogEntry:
    def __init__(self, term: int, command: any, index: int):
        self.term = term
        self.command = command
        self.index = index

class RaftNode:
    """Raft consensus implementation"""
    
    def __init__(self, node_id: str, peers: List[str]):
        # Persistent state
        self.current_term = 0
        self.voted_for = None
        self.log: List[LogEntry] = []
        
        # Volatile state
        self.state = RaftState.FOLLOWER
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index = {}  # For each follower
        self.match_index = {}  # For each follower
        
        # Configuration
        self.node_id = node_id
        self.peers = peers
        self.election_timeout = None
        self.heartbeat_interval = 0.05  # 50ms
        
    async def run(self):
        """Main Raft loop"""
        while True:
            if self.state == RaftState.FOLLOWER:
                await self.follower_loop()
            elif self.state == RaftState.CANDIDATE:
                await self.candidate_loop()
            elif self.state == RaftState.LEADER:
                await self.leader_loop()
    
    async def follower_loop(self):
        """Follower behavior"""
        # Reset election timeout
        timeout = random.uniform(0.15, 0.3)  # 150-300ms
        
        try:
            # Wait for heartbeat or timeout
            await asyncio.wait_for(
                self.wait_for_heartbeat(),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            # No heartbeat, become candidate
            self.become_candidate()
    
    def become_candidate(self):
        """Transition to candidate state"""
        self.state = RaftState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.reset_election_timeout()
    
    async def candidate_loop(self):
        """Candidate behavior - run election"""
        votes_received = 1  # Vote for self
        
        # Request votes from all peers
        vote_futures = []
        for peer in self.peers:
            future = self.request_vote(peer)
            vote_futures.append(future)
        
        # Wait for votes or timeout
        majority = (len(self.peers) + 1) // 2 + 1
        
        try:
            while votes_received < majority:
                done, pending = await asyncio.wait(
                    vote_futures,
                    timeout=self.election_timeout_remaining(),
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for future in done:
                    if future.result():
                        votes_received += 1
                
                vote_futures = list(pending)
                
                if votes_received >= majority:
                    self.become_leader()
                    return
                    
        except asyncio.TimeoutError:
            # Election timeout, start new election
            self.become_candidate()
    
    def become_leader(self):
        """Transition to leader state"""
        self.state = RaftState.LEADER
        
        # Initialize leader state
        for peer in self.peers:
            self.next_index[peer] = len(self.log)
            self.match_index[peer] = 0
        
        # Send initial heartbeat
        asyncio.create_task(self.send_heartbeats())
    
    async def leader_loop(self):
        """Leader behavior"""
        while self.state == RaftState.LEADER:
            # Send periodic heartbeats
            await self.send_heartbeats()
            await asyncio.sleep(self.heartbeat_interval)
    
    async def append_entries(self, entries: List[LogEntry]) -> bool:
        """Append entries to log (leader only)"""
        if self.state != RaftState.LEADER:
            return False
        
        # Append to local log
        for entry in entries:
            entry.term = self.current_term
            entry.index = len(self.log)
            self.log.append(entry)
        
        # Replicate to followers
        success_count = 1  # Self
        replication_futures = []
        
        for peer in self.peers:
            future = self.replicate_to_peer(peer)
            replication_futures.append((peer, future))
        
        # Wait for majority
        majority = (len(self.peers) + 1) // 2 + 1
        
        for peer, future in replication_futures:
            try:
                success = await future
                if success:
                    success_count += 1
                    
                if success_count >= majority:
                    # Commit entries
                    self.commit_index = self.log[-1].index
                    return True
            except:
                pass
        
        return success_count >= majority
```

### Byzantine Fault Tolerant Consensus

```python
class PBFTNode:
    """Practical Byzantine Fault Tolerance"""
    
    def __init__(self, node_id: int, nodes: List[int], f: int):
        self.node_id = node_id
        self.nodes = nodes
        self.f = f  # Max faulty nodes
        self.view = 0
        self.sequence = 0
        
    def is_primary(self) -> bool:
        """Check if this node is primary"""
        return self.nodes[self.view % len(self.nodes)] == self.node_id
    
    def process_request(self, request: dict) -> Optional[dict]:
        """Process client request"""
        if not self.is_primary():
            # Forward to primary
            return None
        
        # Three-phase protocol
        # Phase 1: Pre-prepare
        pre_prepare = {
            'view': self.view,
            'sequence': self.sequence,
            'digest': self.digest(request),
            'request': request
        }
        self.broadcast_pre_prepare(pre_prepare)
        
        # Phase 2: Prepare
        prepare_votes = self.collect_prepares(pre_prepare)
        
        if len(prepare_votes) < 2 * self.f:
            return None  # Not enough prepares
        
        # Phase 3: Commit
        commit_votes = self.collect_commits(pre_prepare)
        
        if len(commit_votes) < 2 * self.f:
            return None  # Not enough commits
        
        # Execute request
        result = self.execute(request)
        self.sequence += 1
        
        return result
```

### Consensus Anti-Patterns

<div class="antipatterns">
<h3>⚠️ Common Consensus Mistakes</h3>

1. **Assuming Synchronous Network**
   ```python
   # BAD: Assumes messages arrive in order
   def bad_consensus(value):
       broadcast("propose", value)
       wait_fixed_time(1.0)  # Assumes all messages arrive in 1 second
       return majority_value()
   
   # GOOD: Handle asynchronous network
   def good_consensus(value):
       responses = []
       while len(responses) < quorum:
           response = wait_for_any_response()
           responses.append(response)
       return process_quorum(responses)
   ```

2. **Split Brain Without Quorum**
   ```python
   # BAD: Can have two leaders
   def elect_leader():
       if len(active_nodes) >= 2:  # Wrong!
           become_leader()
   
   # GOOD: Require majority quorum
   def elect_leader():
       if len(active_nodes) > total_nodes // 2:
           become_leader()
   ```

3. **Not Handling Duplicate Messages**
   ```python
   # BAD: Process every message
   def handle_vote(vote):
       votes.append(vote)
   
   # GOOD: Idempotent message handling
   def handle_vote(vote):
       if vote.id not in processed_votes:
           votes.append(vote)
           processed_votes.add(vote.id)
   ```
</div>

---

## 🚀 Level 4: Expert

### Production Consensus Systems

#### etcd's Raft Implementation
```python
class EtcdRaftImplementation:
    """
    Production-grade Raft as used in etcd
    """
    
    def __init__(self):
        self.raft_config = {
            'election_tick': 10,  # 10 * tick_interval
            'heartbeat_tick': 1,
            'max_size_per_msg': 1024 * 1024,  # 1MB
            'max_uncommitted_entries': 5000,
            'snapshot_interval': 10000  # Entries
        }
        
    def apply_entry(self, entry: bytes) -> bytes:
        """Apply log entry to state machine"""
        # Deserialize command
        command = self.deserialize(entry)
        
        # Apply to key-value store
        if command.type == 'PUT':
            old_value = self.kv_store.get(command.key)
            self.kv_store[command.key] = command.value
            
            # Track revision
            self.revision += 1
            self.revision_index[command.key] = self.revision
            
            return self.serialize_response(old_value)
            
        elif command.type == 'DELETE':
            old_value = self.kv_store.pop(command.key, None)
            self.revision += 1
            
            return self.serialize_response(old_value)
    
    def take_snapshot(self) -> bytes:
        """Create snapshot of current state"""
        snapshot = {
            'kv_store': dict(self.kv_store),
            'revision': self.revision,
            'revision_index': dict(self.revision_index),
            'applied_index': self.last_applied
        }
        
        return self.serialize_snapshot(snapshot)
    
    def restore_snapshot(self, snapshot_data: bytes):
        """Restore from snapshot"""
        snapshot = self.deserialize_snapshot(snapshot_data)
        
        self.kv_store = snapshot['kv_store']
        self.revision = snapshot['revision']
        self.revision_index = snapshot['revision_index']
        self.last_applied = snapshot['applied_index']
```bash
#### Google's Spanner Consensus
```python
class SpannerConsensus:
    """
    Google Spanner's consensus with TrueTime
    """
    
    def __init__(self):
        self.true_time = TrueTimeAPI()
        self.paxos_groups = {}
        
    def commit_transaction(self, transaction: dict) -> bool:
        """
        Commit with external consistency guarantee
        """
        # Get commit timestamp from TrueTime
        commit_ts = self.true_time.now()
        
        # Wait for timestamp to be certainly in the past
        self.true_time.wait_until_past(commit_ts)
        
        # Run 2PC across Paxos groups
        prepare_ok = self.two_phase_commit_prepare(
            transaction,
            commit_ts
        )
        
        if not prepare_ok:
            self.two_phase_commit_abort(transaction)
            return False
        
        # Commit across all groups
        self.two_phase_commit_commit(transaction, commit_ts)
        
        return True
    
    def two_phase_commit_prepare(self, txn: dict, ts: int) -> bool:
        """Prepare phase of 2PC"""
        prepare_promises = []
        
        for shard in txn['affected_shards']:
            paxos_group = self.get_paxos_group(shard)
            
            # Each shard runs Paxos to agree on prepare
            promise = paxos_group.propose({
                'type': 'prepare',
                'txn_id': txn['id'],
                'timestamp': ts,
                'locks': txn['locks'][shard]
            })
            
            prepare_promises.append(promise)
        
        # All must succeed
        return all(prepare_promises)
```bash
### Real-World Case Study: CockroachDB Consensus

```python
class CockroachDBConsensus:
    """
    CockroachDB's consensus implementation
    """
    
    def __init__(self):
        self.ranges = {}  # Range ID -> Raft group
        self.leaseholders = {}  # Range ID -> Node ID
        
    def execute_request(self, request: dict):
        """Execute request with consensus"""
        # Find range for key
        range_id = self.find_range(request['key'])
        
        # Check if we're leaseholder
        if self.leaseholders.get(range_id) == self.node_id:
            # Fast path - we can serve read locally
            if request['type'] == 'read':
                return self.local_read(request)
        
        # Get Raft group for range
        raft_group = self.ranges[range_id]
        
        # Propose through Raft
        entry = {
            'request': request,
            'timestamp': self.hybrid_clock.now(),
            'node_id': self.node_id
        }
        
        # Wait for consensus
        index = raft_group.propose(entry)
        
        # Wait for application
        result = self.wait_for_application(index)
        
        return result
    
    def handle_range_split(self, range_id: str, split_key: bytes):
        """Split range with consensus"""
        # Propose split through Raft
        split_proposal = {
            'type': 'split',
            'range_id': range_id,
            'split_key': split_key,
            'new_range_id': self.generate_range_id()
        }
        
        raft_group = self.ranges[range_id]
        raft_group.propose(split_proposal)
        
        # Wait for split to complete
        # This creates new Raft group for new range
    
    def acquire_lease(self, range_id: str) -> bool:
        """Acquire lease for range"""
        lease_request = {
            'type': 'lease_request',
            'range_id': range_id,
            'node_id': self.node_id,
            'expiration': time.time() + 9.0  # 9 second lease
        }
        
        # Propose through Raft
        raft_group = self.ranges[range_id]
        
        if raft_group.propose(lease_request):
            self.leaseholders[range_id] = self.node_id
            
            # Set up lease renewal
            self.schedule_lease_renewal(range_id)
            
            return True
        
        return False
```yaml
---

## 🎯 Level 5: Mastery

### Theoretical Foundations

#### FLP Impossibility and Practical Solutions
```python
class ConsensusTheory:
    """
    Theoretical foundations of consensus
    """
    
    @staticmethod
    def demonstrate_flp_impossibility():
        """
        Fischer-Lynch-Paterson: No deterministic consensus
        in asynchronous systems with one faulty process
        """
        return {
            'impossibility': 'Cannot distinguish slow from failed',
            'practical_solutions': [
                'Timeouts (partial synchrony)',
                'Randomization (probabilistic termination)',
                'Failure detectors (unreliable but useful)'
            ]
        }
    
    @staticmethod
    def calculate_byzantine_tolerance(n: int) -> int:
        """
        Maximum Byzantine faults tolerable
        """
        # Need n > 3f for f Byzantine faults
        return (n - 1) // 3
    
    @staticmethod
    def latency_lower_bound(nodes: int, f: int) -> dict:
        """
        Theoretical lower bounds on consensus latency
        """
        return {
            'best_case_rounds': 2,  # Paxos fast path
            'worst_case_rounds': f + 1,  # f failures
            'message_complexity': nodes ** 2,
            'optimal_quorum': nodes // 2 + 1
        }
```bash
#### Optimal Consensus Protocols
```python
class OptimalConsensus:
    """
    Theoretically optimal consensus approaches
    """
    
    def vertical_paxos(self):
        """
        Vertical Paxos - reconfiguration during consensus
        """
        # Can change configuration without stopping
        pass
    
    def speculative_paxos(self):
        """
        Speculative execution with rollback
        """
        # Execute before consensus, rollback if needed
        pass
    
    def egalitarian_paxos(self):
        """
        EPaxos - no designated leader, optimal commit latency
        """
        # Any node can propose, conflict resolution
        pass
```

### Future Directions

1. **Quantum Consensus**: Using quantum entanglement for instant agreement
2. **ML-Optimized Consensus**: Learning optimal timeouts and parameters
3. **Blockchain Consensus**: Proof-of-stake and other mechanisms
4. **Edge Consensus**: Consensus in disconnected edge environments

---

## 📋 Quick Reference

### Consensus Algorithm Selection

| Scenario | Algorithm | Why |
|----------|-----------|-----|
| Key-value store | Raft | Simple, understandable |
| Financial system | PBFT | Byzantine fault tolerance |
| Geo-distributed | Multi-Paxos | Flexible, proven |
| High throughput | EPaxos | Optimal latency |
| Blockchain | PoS/PoW | Permissionless |

### Implementation Checklist

- [ ] Define failure model (crash vs Byzantine)
- [ ] Choose algorithm based on requirements
- [ ] Implement leader election
- [ ] Add log replication
- [ ] Handle network partitions
- [ ] Implement snapshotting
- [ ] Add monitoring and metrics
- [ ] Test with chaos engineering

---

---

*"In distributed systems, consensus is the art of getting everyone to agree when no one trusts anyone completely."*

---

**Previous**: [← Circuit Breaker Pattern](circuit-breaker.md) | **Next**: [CQRS (Command Query Responsibility Segregation) →](cqrs.md)
## 🎯 Problem Statement

### The Challenge
This pattern addresses common distributed systems challenges where consensus pattern becomes critical for system reliability and performance.

### Why This Matters
In distributed systems, this problem manifests as:
- **Reliability Issues**: System failures cascade and affect multiple components
- **Performance Degradation**: Poor handling leads to resource exhaustion  
- **User Experience**: Inconsistent or poor response times
- **Operational Complexity**: Difficult to debug and maintain

### Common Symptoms
- Intermittent failures that are hard to reproduce
- Performance that degrades under load
- Resource exhaustion (connections, threads, memory)
- Difficulty isolating root causes of issues

### Without This Pattern
Systems become fragile, unreliable, and difficult to operate at scale.



## 💡 Solution Overview

### Core Concept
The Consensus Pattern pattern provides a structured approach to handling this distributed systems challenge.

### Key Principles
1. **Isolation**: Separate concerns to prevent failures from spreading
2. **Resilience**: Build systems that gracefully handle failures
3. **Observability**: Make system behavior visible and measurable
4. **Simplicity**: Keep solutions understandable and maintainable

### How It Works
The Consensus Pattern pattern works by:
- Monitoring system behavior and health
- Implementing protective mechanisms
- Providing fallback strategies
- Enabling rapid recovery from failures

### Benefits
- **Improved Reliability**: System continues operating during partial failures
- **Better Performance**: Resources are protected from overload
- **Easier Operations**: Clear indicators of system health
- **Reduced Risk**: Failures are contained and predictable



## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical



## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems



## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand



## 🌟 Real Examples

### Production Implementations

**Major Cloud Provider**: Uses this pattern for service reliability across global infrastructure

**Popular Framework**: Implements this pattern by default in their distributed systems toolkit

**Enterprise System**: Applied this pattern to improve uptime from 99% to 99.9%

### Open Source Examples
- **Libraries**: Resilience4j, Polly, circuit-breaker-js
- **Frameworks**: Spring Cloud, Istio, Envoy
- **Platforms**: Kubernetes, Docker Swarm, Consul

### Case Study: E-commerce Platform
A major e-commerce platform implemented Consensus Pattern to handle critical user flows:

**Challenge**: System failures affected user experience and revenue

**Implementation**: 
- Applied Consensus Pattern pattern to critical service calls
- Added fallback mechanisms for degraded operation
- Monitored service health continuously

**Results**:
- 99.9% availability during service disruptions
- Customer satisfaction improved due to reliable experience
- Revenue protected during partial outages

### Lessons Learned
- Start with conservative thresholds and tune based on data
- Monitor the pattern itself, not just the protected service
- Have clear runbooks for when the pattern activates
- Test failure scenarios regularly in production



## 💻 Code Sample

### Basic Implementation

```python
class ConsensusPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"
    
    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)
        
        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)
    
    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold
    
    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass
    
    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}
    
    def _record_success(self):
        self.metrics.record_success()
    
    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = ConsensusPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
consensus:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_consensus_behavior():
    pattern = ConsensusPattern(test_config)
    
    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
    
    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'
    
    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```



