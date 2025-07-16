Page 27: PILLAR III – Distribution of Truth
Learning Objective: In distributed systems, truth is negotiated, not declared.
The Fundamental Question:
"What's the current state?" seems simple until:
- Nodes have different views
- Messages arrive out of order  
- Clocks aren't synchronized
- Failures are partial
- Network partitions happen
Consensus Algorithms Landscape:
2-Phase Commit (2PC)
├─ Blocking protocol
├─ Coordinator bottleneck
└─ Used in: Traditional databases

3-Phase Commit (3PC)  
├─ Non-blocking (in theory)
├─ Extra round trip
└─ Used in: Almost nowhere (too complex)

Paxos
├─ Proven correct
├─ Hard to understand
└─ Used in: Chubby, Spanner

Raft
├─ Understandable
├─ Leader-based
└─ Used in: etcd, Consul

Byzantine (PBFT, BFT)
├─ Tolerates malicious nodes
├─ O(n²) messages
└─ Used in: Blockchain
Quorum Mathematics:
For N replicas:
Write quorum (W) + Read quorum (R) > N

Examples:
N=3: W=2, R=2 (strict quorum)
N=5: W=3, R=3 (majority quorum)
N=5: W=1, R=5 (read-heavy optimization)
N=5: W=5, R=1 (write-heavy optimization)
CAP Theorem Visualized:
Network Partition Occurs:
        [A,B]  ~~~X~~~  [C,D,E]
      (2 nodes)      (3 nodes)

Choice 1: Maintain Consistency
- Reject writes to [A,B] minority
- System partially unavailable
- Example: Bank accounts

Choice 2: Maintain Availability  
- Accept writes on both sides
- Divergent state (resolve later)
- Example: Shopping cart
Truth Coordination Patterns:
1. Last Write Wins (LWW):
Node A: Set X=5 at time 100
Node B: Set X=7 at time 99
Result: X=5 (highest timestamp wins)

Pros: Simple, automatic
Cons: Lost updates, clock dependent
2. Vector Clocks:
Node A: X=5, version=[A:1, B:0]
Node B: X=7, version=[A:0, B:1]
Merge: Conflict detected! 

Pros: Detects all conflicts
Cons: Requires resolution logic
3. CRDTs (Conflict-free Replicated Data Types):
Counter CRDT:
Node A: +3
Node B: +2
Merge: +5 (commutative!)

Pros: Automatic merge
Cons: Limited operations
🎬 Real Incident: Split-Brain at Scale
Company: Major social network
Incident: Network partition splits datacenter

West Coast DC          East Coast DC
[Master thinks         [Master thinks
 it's primary]         it's primary]
     ↓                      ↓
Accepts writes         Accepts writes
     ↓                      ↓
User posts             User posts
diverge               diverge

Duration: 12 minutes
Impact: 
- 100K posts on each side
- Friends see different timelines
- Likes/comments on phantom posts

Resolution attempt #1: Last-write-wins
Problem: Angry users, "lost" posts

Resolution attempt #2: Merge everything
Problem: Duplicate posts, broken threads

Final resolution: 
- Show both versions with "conflict" banner
- Let users choose version to keep
- Took 3 weeks to fully resolve

Lesson: Some conflicts need human resolution
🔧 Try This: Simple Raft Leader Election
pythonimport random
import time
from enum import Enum

class State(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftNode:
    def __init__(self, node_id, all_nodes):
        self.id = node_id
        self.state = State.FOLLOWER
        self.term = 0
        self.voted_for = None
        self.leader = None
        self.all_nodes = all_nodes
        self.election_timeout = random.uniform(1.5, 3.0)
        self.last_heartbeat = time.time()
    
    def start_election(self):
        self.state = State.CANDIDATE
        self.term += 1
        self.voted_for = self.id
        votes = 1  # Vote for self
        
        print(f"Node {self.id} starting election for term {self.term}")
        
        # Request votes from others
        for node in self.all_nodes:
            if node.id != self.id:
                if node.grant_vote(self.term, self.id):
                    votes += 1
        
        # Check if won
        if votes > len(self.all_nodes) // 2:
            self.become_leader()
        else:
            self.state = State.FOLLOWER
    
    def grant_vote(self, term, candidate_id):
        if term > self.term:
            self.term = term
            self.voted_for = None
        
        if self.voted_for is None:
            self.voted_for = candidate_id
            return True
        return False
    
    def become_leader(self):
        self.state = State.LEADER
        self.leader = self.id
        print(f"Node {self.id} became leader for term {self.term}")
        
        # Notify others
        for node in self.all_nodes:
            if node.id != self.id:
                node.accept_leader(self.id, self.term)
    
    def accept_leader(self, leader_id, term):
        if term >= self.term:
            self.term = term
            self.state = State.FOLLOWER
            self.leader = leader_id
            self.last_heartbeat = time.time()