# Law 5: Exercises - The Truth Dojo 🥋

<div class="axiom-box">
<h2>Your Mission: Master the Art of Distributed Deception</h2>
<p>These exercises will rewire your brain to think in probabilities, not certainties. By the end, you'll design systems that thrive on partial knowledge—because that's all you'll ever have.</p>
</div>

## Your Truth Readiness Test

```
CHECK YOUR LEVEL
═══════════════

□ Level 0: "The database knows the truth"
□ Level 1: "OK, nodes can disagree temporarily"
□ Level 2: "I see truth as eventual consistency"
□ Level 3: "I design for Byzantine failures"
□ Level 4: "I embrace probabilistic truth"
□ Level 5: "I profit from uncertainty"

Start wherever you are. Ascend to mastery.
```

---

## Exercise 1: The Split-Brain Simulator 🧠

<div class="decision-box">
<h3>Build Your Own Network Partition Disaster</h3>

```python
class DataCenter:
    def __init__(self, name):
        self.name = name
        self.is_primary = False
        self.data = {}
        self.peers = []
        self.network_status = {}
        
    def can_reach(self, peer):
        """Check if we can reach another DC"""
        return self.network_status.get(peer.name, True)
        
    def write(self, key, value):
        """Accept a write if we think we're primary"""
        if self.is_primary:
            self.data[key] = {
                'value': value,
                'timestamp': time.time(),
                'dc': self.name
            }
            return True
        return False

class SplitBrainSimulator:
    """
    YOUR TASK: Create a split-brain scenario and watch the chaos
    """
    def __init__(self):
        self.dc_west = DataCenter("US-WEST")
        self.dc_east = DataCenter("US-EAST")
        self.dc_eu = DataCenter("EU-CENTRAL")
        
        # Initially, all can reach each other
        self.dc_west.peers = [self.dc_east, self.dc_eu]
        self.dc_east.peers = [self.dc_west, self.dc_eu]
        self.dc_eu.peers = [self.dc_west, self.dc_east]
        
        # DC-WEST starts as primary
        self.dc_west.is_primary = True
        
    def partition_network(self, groups):
        """
        Create network partition between groups
        Example: [[dc_west], [dc_east, dc_eu]]
        """
        # TODO: Implement network partitioning
        # Update each DC's network_status
        pass
        
    def simulate_primary_election(self):
        """
        Each partition elects a primary
        This is where the fun begins...
        """
        # TODO: Implement split-brain scenario
        # Each partition should elect its own primary
        pass
        
    def simulate_writes(self):
        """
        Different clients write to different primaries
        """
        # Client A (can only reach WEST)
        self.dc_west.write("user:123", {"name": "Alice", "balance": 100})
        
        # Client B (can only reach EAST)
        self.dc_east.write("user:123", {"name": "Alice", "balance": 50})
        
        # THE HORROR: Same key, different values!
        
    def heal_partition(self):
        """
        Network recovers. Now what?
        Both DCs have different data for same keys.
        """
        # TODO: Implement conflict detection
        # Which version of user:123 is correct?
        pass

# YOUR CHALLENGE:
# 1. Implement the partition logic
# 2. Create a scenario where data diverges
# 3. Try to reconcile after healing
# 4. Feel the pain of distributed truth
```

<details>
<summary>💡 Hints for Implementation</summary>

```python
def partition_network(self, groups):
    """Create network partition"""
    for group in groups:
        for dc in group:
            # Can reach others in same group
            for peer in group:
                if peer != dc:
                    dc.network_status[peer.name] = True
            
            # Cannot reach other groups
            for other_group in groups:
                if other_group != group:
                    for peer in other_group:
                        dc.network_status[peer.name] = False
                        
def detect_conflicts(self):
    """Find divergent data after healing"""
    conflicts = []
    all_keys = set()
    
    for dc in [self.dc_west, self.dc_east, self.dc_eu]:
        all_keys.update(dc.data.keys())
    
    for key in all_keys:
        values = {}
        for dc in [self.dc_west, self.dc_east, self.dc_eu]:
            if key in dc.data:
                values[dc.name] = dc.data[key]
        
        if len(set(str(v) for v in values.values())) > 1:
            conflicts.append((key, values))
    
    return conflicts
```
</details>
</div>

### The Learning Questions

1. How would you prevent split-brain with 3 data centers?
2. What's the minimum number of nodes needed for a quorum?
3. How does Raft handle this differently than Paxos?

---

## Exercise 2: Byzantine Generals Battle Simulator ⚔️

<div class="failure-vignette">
<h3>When Nodes Lie (Accidentally or Not)</h3>

```
THE SCENARIO: Distributed Database Nodes Must Agree on Next Action
═══════════════════════════════════════════════════════════════

4 Nodes Total, 1 is Byzantine (buggy/malicious)

Node A (Commander): "COMMIT transaction"
         ↓
    ┌────┴────┐
    ▼         ▼
Node B     Node C (Byzantine)
"COMMIT"   "ROLLBACK" to some
           "COMMIT" to others
    │         │
    └────┬────┘
         ▼
      Node D
   "What do I do?"

YOUR MISSION: Implement Byzantine Fault Tolerance
```

```python
class ByzantineNode:
    def __init__(self, node_id, is_byzantine=False):
        self.id = node_id
        self.is_byzantine = is_byzantine
        self.received_values = {}
        self.phase = 0
        
    def broadcast_value(self, value, recipients):
        """Send value to other nodes"""
        if not self.is_byzantine:
            # Honest node: send same value to all
            for node in recipients:
                node.receive_value(self.id, value, self.phase)
        else:
            # Byzantine node: send different values!
            for i, node in enumerate(recipients):
                if i % 2 == 0:
                    node.receive_value(self.id, value, self.phase)
                else:
                    # Send opposite value
                    bad_value = "ROLLBACK" if value == "COMMIT" else "COMMIT"
                    node.receive_value(self.id, bad_value, self.phase)
    
    def receive_value(self, sender_id, value, phase):
        """Receive and store value from another node"""
        if phase not in self.received_values:
            self.received_values[phase] = {}
        self.received_values[phase][sender_id] = value
    
    def echo_phase(self, recipients):
        """PBFT echo phase - rebroadcast what you heard"""
        # TODO: Implement echo phase
        # Each node broadcasts all values it received
        pass
    
    def decide_value(self):
        """Make final decision based on received values"""
        # TODO: Implement decision logic
        # Need 2f+1 matching values to decide
        pass

class PBFTSimulator:
    """
    Practical Byzantine Fault Tolerance Simulator
    
    The algorithm:
    1. Primary broadcasts value
    2. All nodes echo what they heard
    3. Nodes decide based on majority
    """
    def __init__(self, num_nodes=4, num_byzantine=1):
        self.nodes = []
        
        # Create nodes (make some Byzantine)
        for i in range(num_nodes):
            is_byzantine = i < num_byzantine
            self.nodes.append(ByzantineNode(f"Node_{i}", is_byzantine))
    
    def run_consensus(self, value="COMMIT"):
        """
        Run PBFT consensus protocol
        
        YOUR TASK:
        1. Primary broadcasts value
        2. All nodes echo to all others
        3. Each node decides based on majority
        4. Verify all honest nodes agree!
        """
        # Phase 1: Primary broadcast
        primary = self.nodes[0]
        others = self.nodes[1:]
        primary.broadcast_value(value, others)
        
        # Phase 2: Echo phase
        # TODO: Implement echo phase
        
        # Phase 3: Decision
        # TODO: Each node makes decision
        
        # Verify consensus among honest nodes
        # TODO: Check that all honest nodes decided same value
        
        pass

# TEST YOUR IMPLEMENTATION
simulator = PBFTSimulator(num_nodes=7, num_byzantine=2)
# Can 7 nodes tolerate 2 Byzantine nodes?
# Remember: Need n > 3f
```
</div>

### Byzantine Scenarios to Test

```
SCENARIO 1: The Optimistic Traitor
════════════════════════════════
Byzantine node always says "COMMIT"
even when primary said "ROLLBACK"

SCENARIO 2: The Chaos Agent
═══════════════════════════
Byzantine node sends random values
No pattern to the lies

SCENARIO 3: The Smart Adversary
═══════════════════════════════
Byzantine node tries to cause maximum
disagreement by analyzing the network

YOUR CHALLENGE: Make consensus work despite all three!
```

---

## Exercise 3: Vector Clock Time Machine 🕐

<div class="truth-box">
<h3>Track Causality in a Distributed System</h3>

```
THE PROBLEM: Who Edited the Document First?
═══════════════════════════════════════════

Three users editing same document:

Time →
Alice: ──[Edit A1]────────[Edit A2]───────────→
         ↓                    ↓
Bob:   ────────[Edit B1]──────────[Edit B2]───→
                  ↓                   ↓
Carol: ──────────────[Edit C1]────────────────→

Which edits conflict? Which can be auto-merged?
Vector clocks will tell you!
```

```python
class VectorClock:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.clock = {f"node_{i}": 0 for i in range(num_nodes)}
    
    def tick(self):
        """Increment local clock"""
        self.clock[self.node_id] += 1
        return self.clock.copy()
    
    def update(self, other_clock):
        """Update clock when receiving message"""
        # Take max of each component
        for node, time in other_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), time)
        # Then increment local time
        self.tick()
    
    def happens_before(self, other):
        """Check if this event happened before other"""
        # TODO: Implement happens-before relation
        # A happens-before B if all components A <= B
        # and at least one component A < B
        pass
    
    def concurrent_with(self, other):
        """Check if events are concurrent"""
        # TODO: Events are concurrent if neither
        # happens-before the other
        pass

class CollaborativeDocument:
    """
    Simulate collaborative editing with vector clocks
    """
    def __init__(self, num_users=3):
        self.users = {}
        self.edits = []
        
        for i in range(num_users):
            user_id = f"user_{i}"
            self.users[user_id] = VectorClock(user_id, num_users)
    
    def edit(self, user_id, content, clock=None):
        """User makes an edit"""
        user_clock = self.users[user_id]
        
        if clock:
            # Received edit from another user
            user_clock.update(clock)
        else:
            # Local edit
            user_clock.tick()
        
        edit = {
            'user': user_id,
            'content': content,
            'clock': user_clock.clock.copy(),
            'timestamp': time.time()
        }
        self.edits.append(edit)
        
        return edit
    
    def find_conflicts(self):
        """
        Find concurrent (conflicting) edits
        
        YOUR TASK: Identify which edits happened
        concurrently and need manual resolution
        """
        conflicts = []
        
        # TODO: Compare all pairs of edits
        # If concurrent, they conflict!
        
        return conflicts
    
    def create_total_order(self):
        """
        Create a total order of edits
        respecting causality
        
        YOUR TASK: Order edits such that
        if A happens-before B, A comes first
        """
        # TODO: Implement topological sort
        # based on happens-before relation
        pass

# SIMULATE COLLABORATIVE EDITING
doc = CollaborativeDocument(num_users=3)

# Alice starts editing
edit_a1 = doc.edit("user_0", "Hello world")

# Bob sees Alice's edit and responds
doc.edit("user_1", "Hello universe", edit_a1['clock'])

# Carol edits independently (concurrent!)
edit_c1 = doc.edit("user_2", "Goodbye world")

# Find conflicts
conflicts = doc.find_conflicts()
print(f"Conflicting edits: {conflicts}")

# YOUR CHALLENGE:
# 1. Implement happens-before checking
# 2. Detect concurrent edits
# 3. Create a causally-consistent order
# 4. Handle a "time travel" edit (clock from future)
```
</div>

---

## Exercise 4: Build Your Own CRDT 🔧

<div class="axiom-box">
<h3>Conflict-Free Magic Through Math</h3>

```
THE CHALLENGE: Shopping Cart That Never Loses Items
═══════════════════════════════════════════════════

Phone adds milk → Server A
Laptop adds eggs → Server B
Network partition!

After merge, cart must have BOTH milk and eggs
No coordination needed!
```

```python
class GSet:
    """
    Grow-only Set CRDT
    The simplest CRDT - can only add, never remove
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.elements = set()
    
    def add(self, element):
        """Add element to set"""
        self.elements.add((element, self.node_id, time.time()))
    
    def merge(self, other):
        """Merge with another GSet"""
        # Union of both sets - never loses data!
        self.elements = self.elements.union(other.elements)
    
    def values(self):
        """Get unique values in set"""
        return {elem[0] for elem in self.elements}

class ORSet:
    """
    Observed-Remove Set
    Can both add AND remove items!
    
    YOUR TASK: Implement add-wins semantics
    """
    def __init__(self, node_id):
        self.node_id = node_id
        self.adds = {}  # element -> set of unique tags
        self.removes = {}  # element -> set of removed tags
    
    def add(self, element):
        """Add element with unique tag"""
        tag = f"{self.node_id}:{time.time()}"
        
        if element not in self.adds:
            self.adds[element] = set()
        self.adds[element].add(tag)
        
        return tag
    
    def remove(self, element):
        """Remove all visible instances of element"""
        # TODO: Move current tags to removes
        pass
    
    def merge(self, other):
        """Merge another ORSet"""
        # TODO: Implement merge
        # Union adds, union removes
        # Element exists if any tag in adds is not in removes
        pass
    
    def contains(self, element):
        """Check if element exists"""
        # TODO: Element exists if it has tags not in removes
        pass

class ShoppingCartCRDT:
    """
    A shopping cart that handles concurrent updates
    """
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = ORSet(user_id)
        self.quantities = {}  # Use PN-Counter per item
        
    def add_item(self, item, quantity=1):
        """Add item to cart"""
        tag = self.items.add(item)
        
        # TODO: Implement quantity tracking
        # Hint: Use a PN-Counter for each item
        
    def remove_item(self, item):
        """Remove item from cart"""
        self.items.remove(item)
        
    def update_quantity(self, item, delta):
        """Change quantity (can be negative)"""
        # TODO: Update quantity using CRDT
        pass
        
    def merge(self, other_cart):
        """Merge with another cart"""
        self.items.merge(other_cart.items)
        
        # TODO: Merge quantities correctly
        
    def get_contents(self):
        """Get current cart contents"""
        contents = {}
        for item in self.items.values():
            # TODO: Get quantity for each item
            contents[item] = self.quantities.get(item, 0)
        return contents

# SIMULATE DISTRIBUTED SHOPPING
alice_cart = ShoppingCartCRDT("alice")
bob_cart = ShoppingCartCRDT("bob")

# Alice shops on phone
alice_cart.add_item("milk", 2)
alice_cart.add_item("bread", 1)

# Bob shops on laptop (same account!)
bob_cart.add_item("eggs", 12)
bob_cart.add_item("milk", 1)  # Also adds milk!

# Network partition! They shop independently
alice_cart.remove_item("bread")  # Changed mind
bob_cart.add_item("butter", 1)

# Eventually, network heals - merge carts
alice_cart.merge(bob_cart)
bob_cart.merge(alice_cart)

# Both should have identical contents!
print(f"Alice sees: {alice_cart.get_contents()}")
print(f"Bob sees: {bob_cart.get_contents()}")

# YOUR CHALLENGE:
# 1. Implement ORSet remove operation
# 2. Handle quantity conflicts (both added milk)
# 3. Ensure remove+add of same item works correctly
# 4. Test with 3-way merge
```
</div>

---

## Exercise 5: Distributed Truth Detective 🔍

<div class="decision-box">
<h3>Debug a Real Distributed System Problem</h3>

```
THE MYSTERY: The Case of the Vanishing Writes
═════════════════════════════════════════════

Your distributed database is losing writes.
Users complain their data disappears.
Sometimes it comes back later.
Sometimes it's gone forever.

Your tools:
- Node logs with Lamport timestamps
- Network trace showing message delays
- Client complaints with timestamps

Your mission: Find the truth!
```

```python
class DistributedSystemDebugger:
    """
    Analyze logs to find distributed system bugs
    """
    def __init__(self):
        self.events = []
        self.nodes = {}
        
    def parse_log_entry(self, log_line):
        """
        Parse a log entry like:
        [Node_A][Lamport:42] Received WRITE key=user:123 value={"name":"Alice"}
        """
        # TODO: Parse log format
        pass
        
    def build_happens_before_graph(self):
        """
        Build a graph of causal relationships
        """
        # TODO: Use Lamport timestamps to order events
        pass
        
    def detect_anomalies(self):
        """
        Find distributed system anomalies:
        
        1. Lost writes (write acknowledged but not persisted)
        2. Stale reads (read returns old value after write)
        3. Causality violations (effect before cause)
        4. Split brain (two nodes think they're primary)
        """
        anomalies = []
        
        # TODO: Implement anomaly detection
        
        return anomalies
    
    def visualize_timeline(self):
        """
        Create ASCII timeline of events
        """
        timeline = """
        Node A: ──W1──────R1────────W2─────────→
                   ↓       ↑         ↓
        Node B: ────────W3───R2──────────W4───→
                          ↓     ↑
        Node C: ────────────R3───W5──────────→
        
        W = Write, R = Read
        Arrows show causal relationships
        """
        # TODO: Generate timeline from events
        pass

# SAMPLE DISTRIBUTED SYSTEM LOGS
logs = [
    "[Node_A][Lamport:10][Time:1000] Elected as PRIMARY",
    "[Node_B][Lamport:11][Time:1001] Elected as PRIMARY",  # Uh oh!
    "[Node_A][Lamport:12][Time:1002] WRITE key=user:1 value={balance:100}",
    "[Node_B][Lamport:13][Time:1003] WRITE key=user:1 value={balance:50}",
    "[Client][Time:1004] READ key=user:1 -> {balance:100}",
    "[Client][Time:1005] READ key=user:1 -> {balance:50}",
    "[Client][Time:1006] READ key=user:1 -> {balance:100}",  # Flickering!
]

# YOUR DETECTIVE WORK:
# 1. Parse the logs
# 2. Identify the split-brain incident
# 3. Track down the flickering reads
# 4. Propose a fix
```
</div>

---

## Final Boss: Design a Truth-Aware System 🏗️

<div class="truth-box" style="background: #1a1a1a; border: 2px solid #ff5555;">
<h3>Ultimate Challenge: Build a Distributed Key-Value Store</h3>

```python
class TruthAwareKVStore:
    """
    A key-value store that exposes truth uncertainty
    
    Requirements:
    1. Returns confidence level with each read
    2. Tracks causality with vector clocks
    3. Handles Byzantine nodes
    4. Supports tunable consistency
    5. Auto-heals after partitions
    """
    
    def __init__(self, node_id, consistency_level="eventual"):
        self.node_id = node_id
        self.consistency_level = consistency_level
        self.data = {}
        self.vector_clock = VectorClock(node_id)
        self.peers = []
        
    def write(self, key, value, required_acks=1):
        """
        Write with configurable durability
        
        Returns: {
            'success': bool,
            'acks': int,
            'confidence': float,
            'write_token': str
        }
        """
        # TODO: Implement write with:
        # - Vector clock updates
        # - Peer replication
        # - Acknowledgment counting
        # - Confidence calculation
        pass
    
    def read(self, key, consistency="eventual"):
        """
        Read with truth metadata
        
        Returns: {
            'value': any,
            'version': vector_clock,
            'confidence': 0.0-1.0,
            'staleness_ms': int,
            'conflicts': list,
            'sources': list[node_id]
        }
        """
        # TODO: Implement read with:
        # - Consistency level handling
        # - Conflict detection
        # - Staleness calculation
        # - Confidence scoring
        pass
    
    def handle_partition_heal(self):
        """
        Reconcile state after network partition
        """
        # TODO: Implement healing with:
        # - Anti-entropy protocol
        # - Conflict resolution
        # - Version vector merging
        pass

# YOUR FINAL CHALLENGE:
# Build a system that never lies about what it knows
# When uncertain, it says so
# When conflicted, it exposes options
# When partitioned, it degrades gracefully
```
</div>

---

## Reflection & Synthesis

<div class="axiom-box">
<h3>The Truth Master's Checklist</h3>

After completing these exercises, you should understand:

```
TRUTH MASTERY CHECKLIST
══════════════════════

□ Network partitions create multiple realities
□ Byzantine failures happen without malice
□ Vector clocks track causality, not time
□ CRDTs merge without coordination
□ Consensus is expensive but sometimes necessary
□ Probabilistic truth often beats absolute truth
□ Systems must expose their uncertainty

If you checked all boxes, you're ready for:
THE REAL WORLD
Where truth is negotiable,
And the only certainty is uncertainty.
```
</div>

## Your Homework

<div class="decision-box">
<h3>This Week's Mission</h3>

1. **Test your production system** for split-brain scenarios
2. **Add vector clocks** to your conflict-prone data
3. **Measure your truth lag** (how long until consistency?)
4. **Design a CRDT** for your specific use case
5. **Document your truth assumptions** (and their failure modes)

Share your findings with your team.
Watch their certainties crumble. 🤯
</div>

---

**Remember**: In distributed systems, truth isn't found—it's negotiated.

**Next Law**: [Law 6: Cognitive Load](../law6-human-api/) - Where human limits meet system complexity