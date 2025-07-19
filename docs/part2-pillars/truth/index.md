# Pillar 3: Distribution of Truth

**Learning Objective**: Master the art of achieving consensus without a single source of truth.

## The Central Question

How do distributed nodes agree on what happened when they can't trust clocks, networks fail, and nodes crash?

This is where computer science meets philosophy: What is truth when reality itself is distributed?

## First Principles of Truth Distribution

```
In a perfect world:
- All nodes would see the same events in the same order
- Clocks would be perfectly synchronized
- Networks would never fail
- Nodes would never crash

In our world:
- Events have no natural global order
- Clocks drift by milliseconds per day
- Networks partition regularly
- Nodes fail unpredictably

Truth must be constructed, not observed.
```

## The Hierarchy of Distributed Truth

```
Level 5: Global Total Order
   └─ Most expensive (blockchain, atomic broadcast)
   
Level 4: Causal Order
   └─ Preserves cause-and-effect (vector clocks)
   
Level 3: Consensus Truth  
   └─ Majority agreement (Raft, Paxos)
   
Level 2: Eventual Truth
   └─ Converges over time (CRDTs, gossip)
   
Level 1: Local Truth
   └─ What I believe right now

Cost increases exponentially with each level
```

## 🎬 Truth Vignette: The Bitcoin Double-Spend Attack

```
Setting: Bitcoin network, March 2013
Attack: Mining pool briefly controls 51% of hash power

Timeline:
T+0:   Alice sends 1000 BTC to Exchange
T+10:  Transaction confirmed in block 500,001
T+20:  Exchange credits Alice's account
T+30:  Alice withdraws USD
T+40:  Mining pool releases secret chain
T+50:  Secret chain (length 6) overtakes public chain (length 5)
T+60:  Alice's transaction disappears from history

Result:
- Exchange loses 1000 BTC
- Alice keeps both BTC and USD
- "Truth" rewrote itself

Lesson: In distributed systems, truth is what the majority agrees on
Fix: Exchanges now wait for 6+ confirmations
```

## Consensus Algorithms: The Truth Makers

### The FLP Impossibility

Fischer-Lynch-Paterson proved: **In an asynchronous system, no algorithm can guarantee consensus if even one node might fail.**

So all practical algorithms "cheat" by assuming:
- Partial synchrony (Paxos/Raft)
- Randomization (blockchain)
- Failure detectors (impossibly perfect ones)

### 1. Paxos: The Academic Truth

```python
class PaxosAcceptor:
    def __init__(self):
        self.promised_proposal = None
        self.accepted_proposal = None
        self.accepted_value = None
    
    def handle_prepare(self, proposal_num):
        if self.promised_proposal is None or proposal_num > self.promised_proposal:
            self.promised_proposal = proposal_num
            return {
                'promise': True,
                'accepted_proposal': self.accepted_proposal,
                'accepted_value': self.accepted_value
            }
        return {'promise': False}
    
    def handle_accept(self, proposal_num, value):
        if proposal_num >= self.promised_proposal:
            self.promised_proposal = proposal_num
            self.accepted_proposal = proposal_num  
            self.accepted_value = value
            return {'accepted': True}
        return {'accepted': False}

class PaxosProposer:
    def propose(self, value):
        proposal_num = self.get_next_proposal_number()
        
        # Phase 1: Prepare
        promises = []
        for acceptor in self.acceptors:
            response = acceptor.handle_prepare(proposal_num)
            if response['promise']:
                promises.append(response)
        
        if len(promises) <= len(self.acceptors) // 2:
            return None  # No majority
        
        # Choose value from highest accepted proposal
        accepted_proposals = [p for p in promises if p['accepted_proposal']]
        if accepted_proposals:
            highest = max(accepted_proposals, key=lambda p: p['accepted_proposal'])
            value = highest['accepted_value']
        
        # Phase 2: Accept
        accepts = 0
        for acceptor in self.acceptors:
            if acceptor.handle_accept(proposal_num, value)['accepted']:
                accepts += 1
        
        return value if accepts > len(self.acceptors) // 2 else None
```

### 2. Raft: The Understandable Truth

```python
class RaftNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.state = 'follower'  # follower, candidate, leader
        
    def start_election(self):
        self.state = 'candidate'
        self.current_term += 1
        self.voted_for = self.node_id
        
        votes = 1  # Vote for self
        for peer in self.peers:
            vote_request = {
                'term': self.current_term,
                'candidate_id': self.node_id,
                'last_log_index': len(self.log) - 1,
                'last_log_term': self.log[-1]['term'] if self.log else 0
            }
            
            if peer.request_vote(vote_request):
                votes += 1
        
        if votes > len(self.peers) // 2:
            self.become_leader()
    
    def request_vote(self, request):
        # Grant vote if haven't voted and candidate's log is up-to-date
        if request['term'] < self.current_term:
            return False
            
        if request['term'] > self.current_term:
            self.current_term = request['term']
            self.voted_for = None
            self.state = 'follower'
        
        if self.voted_for is None or self.voted_for == request['candidate_id']:
            if self.is_candidate_log_up_to_date(request):
                self.voted_for = request['candidate_id']
                return True
        
        return False
```

### 3. Byzantine Generals: Truth with Traitors

```python
class ByzantineGeneral:
    def __init__(self, general_id, is_traitor=False):
        self.general_id = general_id
        self.is_traitor = is_traitor
        
    def byzantine_agreement(self, value, generals):
        n = len(generals)
        f = (n - 1) // 3  # Max traitors
        
        if n <= 3 * f:
            raise Exception("Too many potential traitors!")
        
        # Round 1: Commander sends value
        messages = {}
        for g in generals:
            if self.is_traitor:
                # Traitor sends different values
                messages[g.general_id] = random.choice([0, 1])
            else:
                messages[g.general_id] = value
        
        # Rounds 2 to f+1: Relay messages
        for round in range(f):
            new_messages = {}
            for g1 in generals:
                for g2 in generals:
                    if g1 != g2:
                        # Each general shares what they heard
                        relay = messages.get(g1.general_id, {})
                        if g1.is_traitor:
                            # Traitors lie
                            relay = {k: random.choice([0, 1]) for k in relay}
                        new_messages[g2.general_id] = relay
            messages.update(new_messages)
        
        # Decision: Take majority
        votes = [v for v in messages.values() if v is not None]
        return 1 if sum(votes) > len(votes) // 2 else 0
```

## 🎯 Decision Framework: Choosing Your Truth

```
What's your threat model?
├─ Just crashes? → Use Raft (simple, fast)
├─ Byzantine nodes? → Use PBFT (complex, slow)
├─ Network partitions? → Use eventual consistency
└─ Global scale? → Use blockchain consensus

What's your consistency need?
├─ Strong consistency? → Raft/Paxos
├─ Causal consistency? → Vector clocks
├─ Eventual consistency? → CRDTs
└─ Probabilistic? → Gossip protocols

What's your performance requirement?
├─ Low latency? → Single leader
├─ High throughput? → Sharded consensus
├─ Geo-distributed? → Regional consensus
└─ Fault tolerant? → Multi-Paxos

What's your scale?
├─ <10 nodes? → Simple primary-backup
├─ 10-100 nodes? → Raft/etcd
├─ 100-1000 nodes? → Cassandra/DynamoDB
└─ >1000 nodes? → Blockchain/DHT
```

## Time: The Foundation of Truth

### The Problem with Time

```
Node A: "Event X happened at 10:00:00.001"
Node B: "Event Y happened at 10:00:00.002"

Which happened first?
- If clocks are synchronized to 1μs: X before Y
- If clocks drift by 2ms: Could be either!
- If network delay is 5ms: Definitely unknown
```

### Logical Time Solutions

```python
class LogicalTimestamp:
    """Lamport timestamps - establish partial order"""
    def __init__(self):
        self.time = 0
    
    def tick(self):
        self.time += 1
        return self.time
    
    def update(self, received_time):
        self.time = max(self.time, received_time) + 1
        return self.time

class VectorClock:
    """Vector clocks - establish causal order"""
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.vector = [0] * num_nodes
    
    def tick(self):
        self.vector[self.node_id] += 1
        return self.vector.copy()
    
    def update(self, other_vector):
        for i in range(len(self.vector)):
            self.vector[i] = max(self.vector[i], other_vector[i])
        self.tick()
    
    def happens_before(self, other):
        return all(a <= b for a, b in zip(self.vector, other)) and \
               any(a < b for a, b in zip(self.vector, other))

class HybridLogicalClock:
    """HLC - combines physical and logical time"""
    def __init__(self):
        self.physical = 0
        self.logical = 0
    
    def now(self):
        wall_time = get_physical_time()
        if wall_time > self.physical:
            self.physical = wall_time
            self.logical = 0
        else:
            self.logical += 1
        return (self.physical, self.logical)
    
    def update(self, received_physical, received_logical):
        wall_time = get_physical_time()
        
        if wall_time > max(self.physical, received_physical):
            self.physical = wall_time
            self.logical = 0
        elif self.physical == received_physical:
            self.logical = max(self.logical, received_logical) + 1
        else:
            self.physical = max(self.physical, received_physical)
            self.logical = received_logical + 1
        
        return (self.physical, self.logical)
```

## Truth at Scale: Gossip Protocols

```python
class GossipProtocol:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = {}
        self.version_vector = defaultdict(int)
    
    def update_local(self, key, value):
        self.version_vector[key] += 1
        self.state[key] = {
            'value': value,
            'version': self.version_vector[key],
            'timestamp': time.time()
        }
    
    def gossip_round(self):
        # Pick random subset of peers
        targets = random.sample(self.peers, min(3, len(self.peers)))
        
        for peer in targets:
            # Exchange state information
            peer_state = peer.get_state()
            
            # Merge states - accept newer versions
            for key, remote_data in peer_state.items():
                local_data = self.state.get(key)
                
                if not local_data or remote_data['version'] > local_data['version']:
                    self.state[key] = remote_data
                    self.version_vector[key] = remote_data['version']
    
    def get_state(self):
        return self.state.copy()

# Anti-entropy: Ensure eventual consistency
class AntiEntropyProtocol(GossipProtocol):
    def __init__(self, node_id, peers):
        super().__init__(node_id, peers)
        self.merkle_tree = MerkleTree()
    
    def reconcile(self, peer):
        # Compare merkle trees to find differences
        my_root = self.merkle_tree.root()
        peer_root = peer.merkle_tree.root()
        
        if my_root != peer_root:
            # Find differing branches
            diffs = self.merkle_tree.find_differences(peer.merkle_tree)
            
            # Exchange only different data
            for key in diffs:
                self.exchange_single_key(peer, key)
```

## 🔧 Try This: Build a Distributed Counter

```python
class DistributedCounter:
    """
    Eventually consistent counter using CRDTs
    Each node can increment independently
    Converges to correct total when synchronized
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.counts = defaultdict(int)  # {node_id: count}
    
    def increment(self, amount=1):
        self.counts[self.node_id] += amount
    
    def value(self):
        return sum(self.counts.values())
    
    def merge(self, other_counts):
        # CRDT merge: take maximum for each node
        for node_id, count in other_counts.items():
            self.counts[node_id] = max(self.counts[node_id], count)
    
    def get_state(self):
        return dict(self.counts)

# Test convergence
node1 = DistributedCounter("node1")
node2 = DistributedCounter("node2")
node3 = DistributedCounter("node3")

# Concurrent increments
node1.increment(5)
node2.increment(3)
node3.increment(2)

print(f"Before sync - Node1: {node1.value()}, Node2: {node2.value()}, Node3: {node3.value()}")

# Partial synchronization
node1.merge(node2.get_state())
node2.merge(node3.get_state())
node3.merge(node1.get_state())

# Continue incrementing during sync
node1.increment(1)

# Final synchronization
node1.merge(node2.get_state())
node2.merge(node1.get_state())
node3.merge(node1.get_state())

print(f"After sync - Node1: {node1.value()}, Node2: {node2.value()}, Node3: {node3.value()}")
# All should show 11
```

## Counter-Intuitive Truth 💡

**"Strong consistency is a luxury, not a requirement. Most real-world systems work fine with 'good enough' consistency."**

Your bank doesn't use strong consistency for checking your balance (eventual consistency with conflict resolution). Social media definitely doesn't (likes might be off by thousands). Even "mission-critical" systems often choose availability over consistency.

## Truth Anti-Patterns

### 1. The Unanimous Vote Fallacy
```python
# WRONG: Requiring all nodes to agree
def unanimous_consensus(nodes, value):
    votes = [node.vote(value) for node in nodes]
    return all(votes)  # One failed node blocks everything!

# RIGHT: Majority consensus
def majority_consensus(nodes, value):
    votes = [node.vote(value) for node in nodes if node.is_alive()]
    return sum(votes) > len(nodes) // 2
```

### 2. The Perfect Clock Assumption
```python
# WRONG: Trusting wall clock time
def order_events(event1, event2):
    return event1.timestamp < event2.timestamp  # Clocks drift!

# RIGHT: Use logical ordering
def order_events(event1, event2):
    return event1.logical_clock.happens_before(event2.logical_clock)
```

### 3. The Split-Brain Nightmare
```python
# WRONG: Multiple leaders
if not heard_from_leader_recently():
    become_leader()  # Now you have two leaders!

# RIGHT: Proper leader election
if won_majority_vote() and has_latest_log():
    become_leader()
```

---

*"In distributed systems, truth isn't discovered—it's negotiated."*