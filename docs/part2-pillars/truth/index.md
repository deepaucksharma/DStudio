# Pillar 3: Truth

## The Central Question

How do independent nodes agree on what happened when they can't tell the difference between a slow response and a dead node?

This is where distributed systems become philosophy. What is truth when observers are limited and communication is unreliable?

## The Fundamental Problem

```
Node A says: "I am the leader"
Node B says: "I am the leader"  
Node C says: "A is the leader"
Node D says: "B is the leader"
Network partitioned, clocks skewed, nodes failing...

Who is telling the truth?
```

## 🎬 Truth Vignette: The Google Spanner Clock Skew of 2012

```
Setting: Google Spanner, globally distributed database
Challenge: Maintain global consistency across continents

The Problem:
- Node in Tokyo thinks timestamp is 14:32:01.000
- Node in London thinks timestamp is 14:32:01.003  
- 3ms difference breaks transaction ordering
- Inconsistent reads across regions

The Solution (TrueTime):
- GPS + atomic clocks at each datacenter
- Track clock uncertainty: 14:32:01.000 ± 3ms
- Wait out uncertainty before committing
- Trade latency for perfect ordering

Result: Global consistency with bounded uncertainty
Physics win: Accept uncertainty, don't pretend it doesn't exist
```

## The Truth Hierarchy

Not all truths are equal. There's a hierarchy:

```
Level 5: Global Linear Truth
    ↓   (Blockchain, Spanner TrueTime)
Level 4: Causal Truth  
    ↓   (Vector clocks, happens-before)
Level 3: Majority Truth
    ↓   (Raft, Byzantine consensus)
Level 2: Local Truth
    ↓   (Single-node transactions)
Level 1: Observed Truth
    ↓   (What this node believes)
```

Each level costs exponentially more to achieve.

## Consensus Algorithms: The Truth Makers

### 1. Raft Consensus

**When**: Need strong consistency, can tolerate minority failures

```python
class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = "follower"  # follower, candidate, leader
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
    
    def start_election(self):
        self.state = "candidate"
        self.current_term += 1
        self.voted_for = self.node_id
        
        votes = 1  # Vote for self
        for peer in self.peers:
            if peer.request_vote(self.current_term, self.node_id):
                votes += 1
        
        if votes > len(self.peers) // 2:
            self.become_leader()
    
    def append_entry(self, entry):
        if self.state != "leader":
            raise Exception("Only leader can append entries")
        
        # Add to local log
        self.log.append({
            'term': self.current_term,
            'entry': entry,
            'index': len(self.log)
        })
        
        # Replicate to majority
        replicated_count = 1  # Self
        for peer in self.peers:
            if peer.append_entries(self.log[-1]):
                replicated_count += 1
        
        if replicated_count > len(self.peers) // 2:
            self.commit_index = len(self.log) - 1
            return True
        return False
```

**Why it works**: Majority agreement ensures safety. Leader election ensures liveness. Log replication ensures consistency.

### 2. Byzantine Fault Tolerance (PBFT)

**When**: Nodes might be malicious, not just failed

```python
class PBFTNode:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.num_nodes = num_nodes
        self.f = (num_nodes - 1) // 3  # Max Byzantine nodes
        self.view = 0
        self.sequence = 0
        
    def request_phase(self, request):
        # Client sends request to primary
        if self.is_primary():
            self.broadcast_prepare(request)
    
    def prepare_phase(self, request):
        # Primary broadcasts prepare message
        prepare_msg = {
            'view': self.view,
            'sequence': self.sequence,
            'request': request,
            'signature': self.sign(request)
        }
        self.broadcast(prepare_msg)
        
    def commit_phase(self, prepare_msg):
        # Wait for 2f+1 matching prepare messages
        if self.count_matching_prepares(prepare_msg) >= 2 * self.f + 1:
            commit_msg = {
                'view': prepare_msg['view'],
                'sequence': prepare_msg['sequence'],
                'signature': self.sign(prepare_msg)
            }
            self.broadcast(commit_msg)
            
    def execute_phase(self, commit_msg):
        # Wait for 2f+1 matching commit messages
        if self.count_matching_commits(commit_msg) >= 2 * self.f + 1:
            self.execute_request(commit_msg['request'])
```

**Cost**: 3 phases, O(n²) message complexity. Expensive but guarantees safety even with malicious nodes.

### 3. Practical Byzantine Fault Tolerance (Proof of Stake)

Modern blockchain consensus:

```python
class ProofOfStake:
    def __init__(self, validators):
        self.validators = validators  # {validator_id: stake_amount}
        self.total_stake = sum(validators.values())
        
    def propose_block(self, proposer_id, block):
        # Proposer selected by stake-weighted random
        if not self.is_valid_proposer(proposer_id):
            return False
            
        # Validators vote weighted by stake
        votes = {}
        for validator_id, stake in self.validators.items():
            if self.validate_block(block, validator_id):
                votes[validator_id] = stake
        
        # Need 2/3 of stake to finalize
        total_votes = sum(votes.values())
        if total_votes >= (2 * self.total_stake) // 3:
            self.finalize_block(block)
            return True
        return False
    
    def slash_validator(self, validator_id):
        # Economic penalty for bad behavior
        self.validators[validator_id] *= 0.5  # Lose half stake
```

## 🎯 Decision Framework: Consensus Strategy

```
THREAT MODEL:
├─ Honest but crash-prone? → Raft/Paxos
├─ Potentially malicious? → Byzantine consensus
├─ Economic incentives? → Proof of Stake
└─ Computational proof? → Proof of Work

PERFORMANCE REQUIREMENTS:
├─ Low latency needed? → Single leader (Raft)
├─ High throughput? → Multi-leader with conflicts
├─ Global scale? → Blockchain consensus
└─ Local cluster? → Traditional consensus

CONSISTENCY NEEDS:
├─ Strong consistency? → Synchronous consensus
├─ Eventual consistency? → Gossip protocols
├─ Causal consistency? → Vector clocks
└─ Session consistency? → Sticky sessions

FAILURE TOLERANCE:
├─ < 50% failures? → Majority consensus
├─ < 33% Byzantine? → Byzantine consensus  
├─ Any failures? → Probabilistic consensus
└─ Network partitions? → Partition-tolerant
```

## The FLP Impossibility Result

**Fischer-Lynch-Paterson Theorem**: In an asynchronous network, no deterministic consensus algorithm can guarantee termination in the presence of even one crash failure.

This is a fundamental limit of distributed computing. **All practical consensus algorithms violate one assumption**:

- **Raft**: Assumes partial synchrony (timeouts work)
- **PBFT**: Assumes bounded message delays  
- **Blockchain**: Uses randomization (probabilistic termination)

## Clock Synchronization: The Time Truth

Time is surprisingly hard in distributed systems:

### Logical Clocks

```python
class LamportClock:
    def __init__(self):
        self.time = 0
    
    def tick(self):
        self.time += 1
        return self.time
    
    def update(self, other_time):
        self.time = max(self.time, other_time) + 1
        return self.time

class VectorClock:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.clock = [0] * num_nodes
    
    def tick(self):
        self.clock[self.node_id] += 1
    
    def update(self, other_clock):
        for i in range(len(self.clock)):
            if i != self.node_id:
                self.clock[i] = max(self.clock[i], other_clock[i])
        self.tick()
    
    def happened_before(self, other):
        return (all(a <= b for a, b in zip(self.clock, other.clock)) and
                any(a < b for a, b in zip(self.clock, other.clock)))
```

### Physical Clock Synchronization

```python
class NTPClient:
    def synchronize(self, ntp_server):
        # Network Time Protocol
        t1 = time.now()                    # Client send time
        response = ntp_server.request(t1)
        t4 = time.now()                    # Client receive time
        t2 = response.server_receive_time   # Server receive time  
        t3 = response.server_send_time      # Server send time
        
        # Calculate offset and round-trip delay
        offset = ((t2 - t1) + (t3 - t4)) / 2
        delay = (t4 - t1) - (t3 - t2)
        
        # Adjust local clock
        self.local_clock_offset = offset
        return delay  # Network latency estimate
```

## Distributed Coordination Patterns

### 1. Leader Election

```python
class ZooKeeperLeaderElection:
    def __init__(self, zk_client, election_path):
        self.zk = zk_client
        self.election_path = election_path
        self.my_node = None
    
    def join_election(self):
        # Create ephemeral sequential node
        self.my_node = self.zk.create(
            f"{self.election_path}/candidate-",
            ephemeral=True,
            sequence=True
        )
        
        # Watch for changes
        self.check_leadership()
    
    def check_leadership(self):
        candidates = sorted(self.zk.get_children(self.election_path))
        
        if candidates[0] == self.my_node.split('/')[-1]:
            self.become_leader()
        else:
            # Watch the candidate just before me
            predecessor = candidates[candidates.index(self.my_node.split('/')[-1]) - 1]
            self.zk.watch(f"{self.election_path}/{predecessor}", self.check_leadership)
```

### 2. Distributed Locking

```python
class DistributedLock:
    def __init__(self, redis_client, lock_name, timeout=10):
        self.redis = redis_client
        self.lock_name = lock_name
        self.timeout = timeout
        self.identifier = str(uuid4())
    
    def acquire(self):
        # Set lock with expiration
        acquired = self.redis.set(
            self.lock_name,
            self.identifier,
            nx=True,  # Only if key doesn't exist
            ex=self.timeout  # Expiration in seconds
        )
        return acquired
    
    def release(self):
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        return self.redis.eval(lua_script, 1, self.lock_name, self.identifier)
```

### 3. Barrier Synchronization

```python
class DistributedBarrier:
    def __init__(self, zk_client, barrier_path, num_participants):
        self.zk = zk_client
        self.barrier_path = barrier_path
        self.num_participants = num_participants
        
    def enter(self):
        # Create my participation node
        self.zk.create(f"{self.barrier_path}/{uuid4()}", ephemeral=True)
        
        # Wait until enough participants
        while True:
            participants = self.zk.get_children(self.barrier_path)
            if len(participants) >= self.num_participants:
                break
            self.zk.watch(self.barrier_path, self.on_barrier_change)
            time.sleep(0.1)
    
    def leave(self):
        # Delete my participation node  
        self.zk.delete(f"{self.barrier_path}/{self.my_id}")
```

## Truth in Probabilistic Systems

Some systems trade perfect truth for probabilistic truth:

### Bloom Filters

```python
class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size
        
    def add(self, item):
        for i in range(self.num_hashes):
            index = hash(item + str(i)) % self.size
            self.bit_array[index] = 1
    
    def might_contain(self, item):
        # Can have false positives, never false negatives
        for i in range(self.num_hashes):
            index = hash(item + str(i)) % self.size
            if self.bit_array[index] == 0:
                return False  # Definitely not present
        return True  # Probably present
```

### HyperLogLog

```python
class HyperLogLog:
    def __init__(self, precision=10):
        self.precision = precision
        self.num_buckets = 2 ** precision
        self.buckets = [0] * self.num_buckets
        
    def add(self, item):
        # Hash the item
        h = hash(item)
        
        # Use first p bits for bucket selection
        bucket = h & ((1 << self.precision) - 1)
        
        # Count leading zeros in remaining bits
        remaining = h >> self.precision
        leading_zeros = self.count_leading_zeros(remaining) + 1
        
        # Keep maximum leading zeros seen for this bucket
        self.buckets[bucket] = max(self.buckets[bucket], leading_zeros)
    
    def count(self):
        # Estimate cardinality from harmonic mean
        raw_estimate = self.alpha() * (self.num_buckets ** 2) / sum(2 ** (-b) for b in self.buckets)
        return int(raw_estimate)
```

## Counter-Intuitive Truth 💡

**"In distributed systems, 'eventually consistent' often means 'never consistent'—because the system never stops changing."**

The window of inconsistency might be microseconds, but in a high-throughput system, there are always updates in flight. Perfect consistency is an asymptote we approach but never reach.

## Truth Anti-Patterns

### 1. The Split-Brain Problem
```python
# WRONG: Multiple nodes think they're primary
class NaiveLeaderElection:
    def __init__(self):
        self.am_leader = False
    
    def check_leadership(self):
        # Dangerous: timeout-based leadership
        if not self.heard_from_leader_recently():
            self.am_leader = True  # Multiple nodes can decide this!

# RIGHT: Use proper consensus
class SafeLeaderElection:
    def become_leader(self):
        # Only become leader after majority vote
        votes = self.request_votes_from_majority()
        if votes >= self.majority_threshold:
            self.am_leader = True
```

### 2. The Observer Effect Problem
```python
# WRONG: Reading changes the state
def get_next_id():
    current = database.get("counter")
    database.set("counter", current + 1)  # Race condition!
    return current

# RIGHT: Atomic operations
def get_next_id():
    return database.atomic_increment("counter")
```

### 3. The Causal Violation
```python
# WRONG: Events appear out of order
user_service.update_name(user_id, "Alice")
message_service.send_message("Hello from Alice")  # Might arrive first!

# RIGHT: Causal consistency
vector_clock.tick()
user_service.update_name(user_id, "Alice", vector_clock.copy())
vector_clock.tick()  
message_service.send_message("Hello from Alice", vector_clock.copy())
```

## The Future of Truth

Three trends are reshaping how we think about distributed truth:

1. **Zero-Knowledge Proofs**: Prove truth without revealing information
2. **Verifiable Computing**: Cryptographic proofs of correct execution
3. **Quantum Consensus**: Quantum entanglement for instant coordination

Each represents a different approach to the fundamental question: How do we know what really happened?

---

*"Truth is not what actually happened—it's what the system agrees happened."*