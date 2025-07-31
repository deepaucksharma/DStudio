# Coordination Patterns - Platinum Tier Enhancement
**For Integration into Foundational Series**

## Deep Dive into Distributed Coordination

### The Fundamental Challenge of Coordination

**The Core Problem**: How do multiple nodes agree on anything when:
- Messages can be lost, delayed, or reordered
- Nodes can crash at any time
- Clocks are not synchronized
- Networks can partition

### Pattern 1: Consensus Algorithms - The Heart of Coordination

#### Raft: The Understandable Consensus Algorithm

**Conceptual Overview**:
```
Raft ensures a group of nodes agree on values by:
1. Electing a leader
2. Leader receives all requests
3. Leader replicates to followers
4. Commits when majority acknowledge
```

**Detailed Raft Implementation**:

```python
class RaftNode:
    """
    Simplified Raft implementation showing core concepts
    """
    
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        
        # Persistent state (survives restarts)
        self.current_term = 0
        self.voted_for = None
        self.log = []
        
        # Volatile state
        self.state = 'FOLLOWER'  # FOLLOWER, CANDIDATE, LEADER
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index = {}
        self.match_index = {}
        
        # Timing
        self.election_timeout = self.random_election_timeout()
        self.last_heartbeat = time.time()
        
    def random_election_timeout(self):
        """
        Random timeout between 150-300ms to prevent split votes
        """
        return random.uniform(0.150, 0.300)
    
    def start_election(self):
        """
        Transition to candidate and start leader election
        """
        self.state = 'CANDIDATE'
        self.current_term += 1
        self.voted_for = self.node_id
        self.reset_election_timeout()
        
        # Vote for self
        votes = 1
        
        # Request votes from all peers
        for peer in self.peers:
            vote_request = {
                'term': self.current_term,
                'candidate_id': self.node_id,
                'last_log_index': len(self.log) - 1,
                'last_log_term': self.log[-1].term if self.log else 0
            }
            
            response = self.send_request_vote(peer, vote_request)
            
            if response and response['vote_granted']:
                votes += 1
                
            # Become leader if majority votes received
            if votes > len(self.peers) // 2 + 1:
                self.become_leader()
                return
        
        # If election failed, return to follower
        self.state = 'FOLLOWER'
    
    def become_leader(self):
        """
        Transition to leader state
        """
        self.state = 'LEADER'
        
        # Initialize leader state
        for peer in self.peers:
            self.next_index[peer] = len(self.log)
            self.match_index[peer] = 0
            
        # Send initial heartbeats
        self.send_heartbeats()
    
    def append_entries(self, entries, leader_commit):
        """
        Handle AppendEntries RPC from leader
        """
        # Reset election timeout
        self.reset_election_timeout()
        
        # Check term
        if entries['term'] < self.current_term:
            return {'success': False, 'term': self.current_term}
        
        # Update term if needed
        if entries['term'] > self.current_term:
            self.current_term = entries['term']
            self.state = 'FOLLOWER'
            self.voted_for = None
        
        # Check log consistency
        if entries['prev_log_index'] >= 0:
            if len(self.log) <= entries['prev_log_index'] or \
               self.log[entries['prev_log_index']].term != entries['prev_log_term']:
                return {'success': False, 'term': self.current_term}
        
        # Append new entries
        for i, entry in enumerate(entries['entries']):
            log_index = entries['prev_log_index'] + 1 + i
            if log_index < len(self.log):
                if self.log[log_index].term != entry.term:
                    # Remove conflicting entries
                    self.log = self.log[:log_index]
                    self.log.append(entry)
            else:
                self.log.append(entry)
        
        # Update commit index
        if leader_commit > self.commit_index:
            self.commit_index = min(leader_commit, len(self.log) - 1)
        
        return {'success': True, 'term': self.current_term}
    
    def replicate_log_entry(self, command):
        """
        Leader replicates a new log entry to followers
        """
        if self.state != 'LEADER':
            return False
        
        # Append to own log
        entry = LogEntry(
            term=self.current_term,
            index=len(self.log),
            command=command
        )
        self.log.append(entry)
        
        # Replicate to followers
        successful_replications = 1  # Count self
        
        for peer in self.peers:
            if self.send_append_entries(peer, [entry]):
                successful_replications += 1
        
        # Commit if majority replicated
        if successful_replications > len(self.peers) // 2 + 1:
            self.commit_index = len(self.log) - 1
            return True
            
        return False
```

**Raft Failure Modes and Handling**:

```python
class RaftFailureScenarios:
    """
    Common Raft failure modes and their resolutions
    """
    
    def split_brain_prevention(self):
        """
        How Raft prevents split-brain scenarios
        """
        return {
            'scenario': 'Network partitions into two groups',
            'mechanism': 'Majority requirement for elections',
            'result': 'At most one partition can have a leader',
            'example': {
                '5_nodes': 'Need 3 votes to become leader',
                'partition_2_3': 'Only 3-node partition can elect leader',
                'partition_1_4': 'Neither partition has majority'
            }
        }
    
    def leader_failure_recovery(self):
        """
        Leader crash and recovery process
        """
        timeline = [
            {'t': 0, 'event': 'Leader sends heartbeat'},
            {'t': 50, 'event': 'Leader crashes'},
            {'t': 150, 'event': 'First follower election timeout'},
            {'t': 151, 'event': 'Follower becomes candidate'},
            {'t': 160, 'event': 'Candidate sends RequestVote RPCs'},
            {'t': 170, 'event': 'Majority votes received'},
            {'t': 171, 'event': 'New leader elected'},
            {'t': 172, 'event': 'New leader sends heartbeats'},
            {'t': 200, 'event': 'System operational again'}
        ]
        return {
            'detection_time': '150-300ms (election timeout)',
            'recovery_time': '~200ms typical',
            'data_loss': 'None - uncommitted entries may be lost',
            'timeline': timeline
        }
    
    def network_partition_behavior(self):
        """
        How Raft handles network partitions
        """
        return {
            'minority_partition': {
                'can_elect_leader': False,
                'can_serve_reads': 'Stale reads only',
                'can_serve_writes': False,
                'client_experience': 'Unavailable'
            },
            'majority_partition': {
                'can_elect_leader': True,
                'can_serve_reads': 'Consistent reads',
                'can_serve_writes': True,
                'client_experience': 'Full availability'
            },
            'partition_heals': {
                'process': [
                    'Old leader detects higher term',
                    'Old leader steps down to follower',
                    'Followers sync missing entries',
                    'System converges to single leader'
                ],
                'time_to_consistency': '< 1 round-trip time'
            }
        }
```

#### Paxos: The Original Consensus Algorithm

**Conceptual Comparison with Raft**:

```python
class PaxosVsRaft:
    """
    Understanding Paxos by comparing with Raft
    """
    
    def core_differences(self):
        return {
            'paxos': {
                'approach': 'Single value consensus',
                'phases': ['Prepare/Promise', 'Accept/Accepted'],
                'leader': 'No explicit leader concept',
                'understandability': 'Notoriously difficult'
            },
            'raft': {
                'approach': 'Log replication',
                'phases': ['Leader election', 'Log replication'],
                'leader': 'Strong leader model',
                'understandability': 'Designed for clarity'
            }
        }
    
    def basic_paxos_flow(self):
        """
        Basic Paxos algorithm flow
        """
        return {
            'phase_1a_prepare': {
                'proposer': 'Select proposal number n',
                'action': 'Send Prepare(n) to acceptors'
            },
            'phase_1b_promise': {
                'acceptor': 'If n > highest seen',
                'action': 'Promise not to accept proposals < n',
                'response': 'Return any accepted value'
            },
            'phase_2a_accept': {
                'proposer': 'If majority promised',
                'action': 'Send Accept(n, value) to acceptors'
            },
            'phase_2b_accepted': {
                'acceptor': 'If n >= promised number',
                'action': 'Accept the value',
                'response': 'Notify learners'
            }
        }
```

### Pattern 2: Distributed Locking - Mutual Exclusion at Scale

**Lock Implementation Strategies**:

```python
class DistributedLockImplementations:
    """
    Various distributed lock implementations and trade-offs
    """
    
    def redis_redlock(self):
        """
        Redis Redlock algorithm for distributed locking
        """
        class RedLock:
            def __init__(self, redis_nodes):
                self.redis_nodes = redis_nodes
                self.quorum = len(redis_nodes) // 2 + 1
                
            def acquire_lock(self, resource, ttl=10000):
                """
                Acquire lock on majority of Redis nodes
                """
                retry_count = 3
                retry_delay = random.uniform(0, 0.2)
                
                for attempt in range(retry_count):
                    acquired_locks = 0
                    start_time = time.time() * 1000  # ms
                    
                    # Try to acquire lock on all nodes
                    for node in self.redis_nodes:
                        if self.acquire_single_lock(node, resource, ttl):
                            acquired_locks += 1
                    
                    # Calculate elapsed time
                    elapsed = (time.time() * 1000) - start_time
                    validity_time = ttl - elapsed
                    
                    # Check if we have quorum and time left
                    if acquired_locks >= self.quorum and validity_time > 0:
                        return Lock(resource, validity_time)
                    else:
                        # Release all locks and retry
                        self.release_all_locks(resource)
                        time.sleep(retry_delay)
                
                return None
            
            def acquire_single_lock(self, node, resource, ttl):
                """
                SET resource_name random_value NX PX ttl
                """
                try:
                    return node.set(
                        resource,
                        self.lock_id,
                        nx=True,  # Only if not exists
                        px=ttl    # Expire after ttl ms
                    )
                except:
                    return False
        
        return RedLock
    
    def zookeeper_lock(self):
        """
        ZooKeeper's sequential znode approach
        """
        class ZooKeeperLock:
            def __init__(self, zk_client, lock_path):
                self.zk = zk_client
                self.lock_path = lock_path
                self.my_znode = None
                
            def acquire(self):
                """
                Create sequential ephemeral znode
                """
                # Create sequential znode
                self.my_znode = self.zk.create(
                    f"{self.lock_path}/lock-",
                    ephemeral=True,
                    sequence=True
                )
                
                while True:
                    # Get all lock znodes
                    children = sorted(self.zk.get_children(self.lock_path))
                    
                    # Check if we have the lowest sequence number
                    if self.my_znode.split('/')[-1] == children[0]:
                        return True  # We have the lock
                    
                    # Watch the znode with next lower sequence
                    my_index = children.index(self.my_znode.split('/')[-1])
                    watch_znode = f"{self.lock_path}/{children[my_index - 1]}"
                    
                    # Wait for predecessor to be deleted
                    if self.zk.exists(watch_znode, watch=True):
                        self.wait_for_notification()
        
        return ZooKeeperLock
    
    def lock_timeout_handling(self):
        """
        Handling lock timeout and fencing
        """
        class FencedLock:
            def __init__(self):
                self.fence_token = 0
                
            def acquire_with_fence(self, resource):
                """
                Monotonically increasing fence token
                """
                self.fence_token += 1
                
                lock = Lock(
                    resource=resource,
                    fence_token=self.fence_token,
                    acquired_at=time.time()
                )
                
                # Storage must check fence token
                # Reject operations with lower fence tokens
                return lock
            
            def protected_operation(self, lock, operation):
                """
                Execute operation with fence protection
                """
                # Include fence token in all operations
                return self.storage.execute(
                    operation,
                    fence_token=lock.fence_token
                )
        
        return FencedLock
```

**Distributed Lock Failure Modes**:

```python
class DistributedLockFailures:
    """
    Common distributed lock failures and mitigations
    """
    
    def process_pause_problem(self):
        """
        The infamous process pause problem
        """
        return {
            'scenario': [
                '1. Process A acquires lock (expires in 10s)',
                '2. Process A experiences GC pause for 15s',
                '3. Lock expires during pause',
                '4. Process B acquires same lock',
                '5. Process A resumes, thinks it has lock',
                '6. Both A and B access protected resource!'
            ],
            'mitigations': {
                'fencing_tokens': 'Monotonic tokens prevent stale operations',
                'lease_validation': 'Check lease validity before each operation',
                'storage_support': 'Storage layer enforces fencing'
            }
        }
    
    def clock_skew_issues(self):
        """
        How clock skew breaks distributed locks
        """
        return {
            'problem': 'Nodes have different wall clock times',
            'impact': 'Lock TTL calculations incorrect',
            'example': {
                'node_a_time': '12:00:00',
                'node_b_time': '12:00:30',  # 30s ahead
                'lock_ttl': '10s',
                'result': 'Node B thinks lock expired 20s early!'
            },
            'solutions': [
                'Use logical clocks for ordering',
                'Compensate for known clock skew',
                'Use consensus for time agreement'
            ]
        }
```

### Pattern 3: Clock Synchronization - Time in Distributed Systems

**Types of Clocks**:

```python
class DistributedClocks:
    """
    Different approaches to time in distributed systems
    """
    
    def physical_clocks(self):
        """
        Wall clock time synchronization
        """
        class NTPSync:
            def __init__(self):
                self.ntp_servers = [
                    'time.google.com',
                    'pool.ntp.org'
                ]
                
            def calculate_offset(self, server):
                """
                NTP offset calculation
                """
                t1 = time.time()  # Request sent
                server_time = self.query_ntp_server(server)
                t4 = time.time()  # Response received
                
                # Server timestamps
                t2 = server_time['receive']
                t3 = server_time['transmit']
                
                # Calculate offset and round-trip delay
                offset = ((t2 - t1) + (t3 - t4)) / 2
                delay = (t4 - t1) - (t3 - t2)
                
                return {
                    'offset': offset,
                    'delay': delay,
                    'accuracy': delay / 2  # Maximum error
                }
        
        return {
            'ntp': NTPSync(),
            'typical_accuracy': '1-50ms over internet',
            'datacenter_accuracy': '< 1ms with PTP'
        }
    
    def logical_clocks(self):
        """
        Lamport timestamps for causality
        """
        class LamportClock:
            def __init__(self):
                self.counter = 0
                
            def increment(self):
                """Local event"""
                self.counter += 1
                return self.counter
                
            def update(self, received_timestamp):
                """Receive event"""
                self.counter = max(self.counter, received_timestamp) + 1
                return self.counter
        
        return LamportClock()
    
    def vector_clocks(self):
        """
        Track causality between all nodes
        """
        class VectorClock:
            def __init__(self, node_id, num_nodes):
                self.node_id = node_id
                self.clock = [0] * num_nodes
                
            def increment(self):
                """Local event"""
                self.clock[self.node_id] += 1
                return self.clock.copy()
                
            def update(self, received_clock):
                """Merge on receive"""
                for i in range(len(self.clock)):
                    self.clock[i] = max(self.clock[i], received_clock[i])
                self.clock[self.node_id] += 1
                return self.clock.copy()
                
            def happens_before(self, other):
                """Check if self → other"""
                return all(self.clock[i] <= other[i] for i in range(len(self.clock)))
        
        return VectorClock
    
    def hybrid_logical_clocks(self):
        """
        HLC: Best of physical and logical clocks
        """
        class HybridLogicalClock:
            def __init__(self):
                self.physical_time = 0
                self.logical_time = 0
                
            def now(self):
                """
                Generate HLC timestamp
                """
                physical_now = time.time()
                
                if physical_now > self.physical_time:
                    self.physical_time = physical_now
                    self.logical_time = 0
                else:
                    self.logical_time += 1
                    
                return (self.physical_time, self.logical_time)
                
            def update(self, received_physical, received_logical):
                """
                Update on message receive
                """
                physical_now = time.time()
                
                if physical_now > max(self.physical_time, received_physical):
                    self.physical_time = physical_now
                    self.logical_time = 0
                elif self.physical_time == received_physical:
                    self.logical_time = max(self.logical_time, received_logical) + 1
                elif self.physical_time > received_physical:
                    self.logical_time += 1
                else:
                    self.physical_time = received_physical
                    self.logical_time = received_logical + 1
                    
                return (self.physical_time, self.logical_time)
        
        return HybridLogicalClock()
```

**Google's TrueTime**:

```python
class TrueTimeImplementation:
    """
    Understanding Google Spanner's TrueTime
    """
    
    def truetime_api(self):
        """
        TrueTime provides uncertainty bounds
        """
        class TrueTime:
            def __init__(self, uncertainty_ms=7):
                self.uncertainty = uncertainty_ms / 1000.0
                
            def now(self):
                """
                Returns interval [earliest, latest]
                """
                current = time.time()
                return TimeInterval(
                    earliest=current - self.uncertainty,
                    latest=current + self.uncertainty
                )
                
            def after(self, timestamp):
                """
                True if timestamp is definitely in the past
                """
                return time.time() - self.uncertainty > timestamp
                
            def before(self, timestamp):
                """
                True if timestamp is definitely in the future
                """
                return time.time() + self.uncertainty < timestamp
        
        return TrueTime()
    
    def spanner_commit_wait(self):
        """
        How Spanner uses TrueTime for consistency
        """
        class SpannerTransaction:
            def __init__(self, truetime):
                self.tt = truetime
                
            def commit(self, transaction):
                """
                Commit with TrueTime guarantee
                """
                # Assign timestamp
                commit_timestamp = self.tt.now().latest
                
                # Wait until timestamp is definitely in the past
                while not self.tt.after(commit_timestamp):
                    time.sleep(0.001)  # Wait 1ms
                    
                # Now safe to release locks
                # All other transactions will see this one
                return commit_timestamp
        
        return SpannerTransaction
```

### Pattern 4: Leader Election - Choosing Who's in Charge

**Leader Election Algorithms**:

```python
class LeaderElectionPatterns:
    """
    Different approaches to leader election
    """
    
    def bully_algorithm(self):
        """
        Simple but aggressive leader election
        """
        class BullyElection:
            def __init__(self, node_id, all_nodes):
                self.node_id = node_id
                self.all_nodes = all_nodes
                self.leader = None
                
            def start_election(self):
                """
                Node notices leader failure
                """
                higher_nodes = [n for n in self.all_nodes if n > self.node_id]
                
                if not higher_nodes:
                    # I'm the highest, become leader
                    self.become_leader()
                    return
                
                # Send election message to higher nodes
                responses = []
                for node in higher_nodes:
                    response = self.send_election_message(node)
                    if response:
                        responses.append(response)
                
                if not responses:
                    # No higher node responded, become leader
                    self.become_leader()
                else:
                    # Wait for new leader announcement
                    self.wait_for_coordinator()
        
        return BullyElection
    
    def ring_election(self):
        """
        Token ring based election
        """
        class RingElection:
            def __init__(self, node_id, next_node):
                self.node_id = node_id
                self.next_node = next_node
                self.participants = []
                
            def start_election(self):
                """
                Create election token
                """
                token = ElectionToken(initiator=self.node_id)
                token.add_participant(self.node_id)
                self.forward_token(token)
                
            def receive_token(self, token):
                """
                Handle election token
                """
                if token.initiator == self.node_id:
                    # Token completed circuit
                    leader = max(token.participants)
                    self.announce_leader(leader)
                elif self.node_id in token.participants:
                    # Already participated, just forward
                    self.forward_token(token)
                else:
                    # Add self and forward
                    token.add_participant(self.node_id)
                    self.forward_token(token)
        
        return RingElection
```

### Pattern 5: Distributed Transactions - ACID at Scale

**Two-Phase Commit (2PC)**:

```python
class TwoPhaseCommit:
    """
    Classic 2PC implementation and its problems
    """
    
    def __init__(self):
        self.state = 'INIT'
        self.participants = []
        self.votes = {}
        
    def coordinate_transaction(self, transaction):
        """
        Coordinator's 2PC flow
        """
        # Phase 1: Voting Phase
        self.state = 'PREPARING'
        
        # Send prepare to all participants
        for participant in self.participants:
            vote = participant.prepare(transaction)
            self.votes[participant.id] = vote
            
            if not vote:
                # Any NO vote aborts transaction
                self.abort_transaction()
                return False
        
        # Phase 2: Commit Phase
        self.state = 'COMMITTING'
        
        # All voted YES, send commit
        for participant in self.participants:
            participant.commit(transaction)
            
        self.state = 'COMMITTED'
        return True
    
    def failure_scenarios(self):
        """
        2PC failure modes and their impact
        """
        return {
            'coordinator_fails_before_prepare': {
                'impact': 'Transaction aborted',
                'recovery': 'Participants timeout and abort'
            },
            'coordinator_fails_after_prepare': {
                'impact': 'Participants blocked!',
                'recovery': 'Need coordinator recovery',
                'problem': 'Participants hold locks indefinitely'
            },
            'participant_fails_before_vote': {
                'impact': 'Transaction aborted',
                'recovery': 'Coordinator timeouts and aborts'
            },
            'participant_fails_after_yes_vote': {
                'impact': 'Must commit when recovers',
                'recovery': 'Participant checks log on recovery'
            },
            'network_partition_during_commit': {
                'impact': 'Some commit, some blocked',
                'recovery': 'Complex - need termination protocol'
            }
        }
```

**Three-Phase Commit (3PC)**:

```python
class ThreePhaseCommit:
    """
    3PC adds a prepare-to-commit phase
    """
    
    def coordinate_transaction(self, transaction):
        """
        3PC flow with extra phase
        """
        # Phase 1: CanCommit
        can_commit_votes = self.collect_votes(transaction)
        if not all(can_commit_votes.values()):
            return self.abort()
            
        # Phase 2: PreCommit
        pre_commit_acks = self.send_pre_commit()
        if not all(pre_commit_acks.values()):
            return self.abort()
            
        # Phase 3: DoCommit
        self.send_do_commit()
        return True
    
    def advantages_over_2pc(self):
        return {
            'non_blocking': 'Can make progress without coordinator',
            'recovery': 'Participants can deduce outcome',
            'cost': 'Extra round of messages',
            'assumption': 'No network partitions (unrealistic!)'
        }
```

### Observability Tie-in for Coordination

**Distributed Tracing for Coordination**:

```python
class CoordinationObservability:
    """
    Making coordination visible through tracing
    """
    
    def trace_consensus_round(self):
        """
        Instrument Raft consensus with OpenTelemetry
        """
        class InstrumentedRaftNode(RaftNode):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.tracer = trace.get_tracer(__name__)
                
            def start_election(self):
                with self.tracer.start_as_current_span("raft.election") as span:
                    span.set_attribute("node.id", self.node_id)
                    span.set_attribute("term", self.current_term)
                    
                    # Original election logic
                    result = super().start_election()
                    
                    span.set_attribute("election.result", self.state)
                    span.set_attribute("votes.received", self.votes_received)
                    
                    return result
                    
            def append_entries(self, entries, leader_commit):
                with self.tracer.start_as_current_span("raft.append_entries") as span:
                    span.set_attribute("entries.count", len(entries))
                    span.set_attribute("leader.commit_index", leader_commit)
                    
                    result = super().append_entries(entries, leader_commit)
                    
                    span.set_attribute("success", result['success'])
                    span.set_attribute("log.length", len(self.log))
                    
                    return result
        
        return InstrumentedRaftNode
    
    def coordination_metrics(self):
        """
        Key metrics for coordination patterns
        """
        return {
            'consensus': {
                'election_duration': Histogram('raft_election_duration_seconds'),
                'term_changes': Counter('raft_term_changes_total'),
                'log_replication_lag': Gauge('raft_log_replication_lag'),
                'commit_latency': Histogram('raft_commit_latency_seconds')
            },
            'locking': {
                'lock_acquisition_time': Histogram('distributed_lock_acquisition_seconds'),
                'lock_hold_time': Histogram('distributed_lock_hold_seconds'),
                'lock_contention': Counter('distributed_lock_contention_total'),
                'lock_timeouts': Counter('distributed_lock_timeouts_total')
            },
            'leader_election': {
                'elections_triggered': Counter('leader_elections_total'),
                'election_duration': Histogram('leader_election_duration_seconds'),
                'leader_changes': Counter('leader_changes_total'),
                'split_brain_detected': Counter('split_brain_detections_total')
            }
        }
```

### Coordination Pattern Decision Matrix

```python
def choose_coordination_pattern(requirements):
    """
    Decision framework for coordination patterns
    """
    patterns = {
        'consensus': {
            'when': 'Need strong consistency across replicas',
            'examples': ['Configuration management', 'Leader election', 'Distributed locks'],
            'options': {
                'raft': 'Understandable, widely implemented',
                'paxos': 'Theoretical foundation, complex',
                'pbft': 'Byzantine fault tolerance'
            }
        },
        'locking': {
            'when': 'Need mutual exclusion for resources',
            'examples': ['Distributed cron', 'Resource allocation', 'Deduplication'],
            'options': {
                'redis_redlock': 'Good for short locks',
                'zookeeper': 'Strong consistency',
                'database': 'Simple but limited'
            }
        },
        'time': {
            'when': 'Need to order events or synchronize time',
            'examples': ['Event ordering', 'Distributed snapshots', 'Causal consistency'],
            'options': {
                'ntp': 'Physical time sync',
                'logical_clocks': 'Causality without wall time',
                'hlc': 'Best of both worlds',
                'truetime': 'Uncertainty bounds (Google)'
            }
        }
    }
    
    return patterns
```

### Anti-Patterns in Coordination

```python
class CoordinationAntiPatterns:
    """
    Common mistakes in distributed coordination
    """
    
    def assuming_synchronized_clocks(self):
        """
        Never assume clocks are synchronized
        """
        return {
            'bad': 'if current_time > lock_expiry: release_lock()',
            'why': 'Clock skew can cause premature release',
            'good': 'Use logical expiry or consensus-based release'
        }
    
    def ignoring_partial_failures(self):
        """
        Coordination must handle partial failures
        """
        return {
            'bad': 'Send updates to all nodes, assume success',
            'why': 'Some nodes might fail, causing inconsistency',
            'good': 'Use consensus or handle failures explicitly'
        }
    
    def blocking_operations(self):
        """
        Avoid indefinite blocking
        """
        return {
            'bad': 'Wait forever for lock acquisition',
            'why': 'Can deadlock entire system',
            'good': 'Always use timeouts and deadlock detection'
        }
```