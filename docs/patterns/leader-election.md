---
title: Leader Election Pattern
description: "Distributed coordination pattern for selecting a single node to perform critical operations and avoid split-brain scenarios"
type: pattern
difficulty: advanced
reading_time: 45 min
prerequisites: []
pattern_type: "coordination"
status: complete
last_updated: 2025-07-21
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Leader Election Pattern**

# Leader Election Pattern

**Distributed coordination pattern for selecting a single node to perform critical operations and avoid split-brain scenarios**

> *"In a distributed system, everyone thinks they should be the leader. Leader election ensures only one actually is, and everyone else agrees."*

---

## 🎯 Level 1: Intuition

### Core Concept

Leader election ensures exactly one node in a distributed system has the authority to make decisions, preventing conflicts and maintaining consistency:

```
Without Leader:                       With Leader Election:
🖥️ → 📊 ← 🖥️                          🖥️ ↘
↓     ↕     ↑                                📊 ← 👑🖥️ (Leader)
🖥️ → 📊 ← 🖥️                          🖥️ ↗

Chaos: Conflicts                      Order: Coordinated decisions
```

### Real-World Examples

| System | Leader Responsibility | Benefit |
|--------|---------------------|----------|
| **Database Cluster** | Write coordination | Consistent updates |
| **Job Scheduler** | Task assignment | No duplicate work |
| **Service Registry** | Config updates | Synchronized state |
| **Shard Manager** | Data rebalancing | Optimal placement |

### Basic Implementation

```mermaid
flowchart TB
    subgraph "Leader Election Flow"
        Start([Node Starts])
        Follower[FOLLOWER STATE<br/>- Wait for heartbeat<br/>- Reset timer]
        Timeout{Election<br/>Timeout?}
        Candidate[CANDIDATE STATE<br/>- Increment term<br/>- Vote for self<br/>- Request votes]
        Votes{Majority<br/>Votes?}
        Leader[LEADER STATE<br/>- Send heartbeats<br/>- Handle requests]
        HigherTerm{Higher<br/>Term?}
        
        Start --> Follower
        Follower --> Timeout
        Timeout -->|Yes| Candidate
        Timeout -->|No| Follower
        Candidate --> Votes
        Votes -->|Yes| Leader
        Votes -->|No| Follower
        Leader --> HigherTerm
        HigherTerm -->|Yes| Follower
        HigherTerm -->|No| Leader
        Candidate --> HigherTerm
    end
    
    style Follower fill:#94a3b8,stroke:#475569
    style Candidate fill:#f59e0b,stroke:#d97706
    style Leader fill:#10b981,stroke:#059669,stroke-width:3px
```

### Election Process Visualization

```mermaid
sequenceDiagram
    participant N1 as Node 1
    participant N2 as Node 2
    participant N3 as Node 3
    participant N4 as Node 4
    participant N5 as Node 5
    
    Note over N1,N5: All nodes start as Followers
    
    Note over N2: Election timeout!
    N2->>N2: State = CANDIDATE<br/>Term = 1<br/>Vote for self
    
    par Vote Request
        N2->>N1: RequestVote(term=1)
        N2->>N3: RequestVote(term=1)
        N2->>N4: RequestVote(term=1)
        N2->>N5: RequestVote(term=1)
    end
    
    par Vote Response
        N1-->>N2: VoteGranted
        N3-->>N2: VoteGranted
        N4-->>N2: VoteDenied
        N5-->>N2: VoteGranted
    end
    
    Note over N2: Votes = 4/5 (majority!)
    N2->>N2: State = LEADER
    
    loop Heartbeats
        N2->>N1: AppendEntries(heartbeat)
        N2->>N3: AppendEntries(heartbeat)
        N2->>N4: AppendEntries(heartbeat)
        N2->>N5: AppendEntries(heartbeat)
    end
```

---

## 🏗️ Level 2: Foundation

### Core Concepts

#### Election Terms
Each election happens in a numbered term to prevent stale messages:

```
Term 1: Node A elected
Term 2: Node A fails, Node B elected
Term 3: Network partition, Node C elected
```

#### State Machine

```mermaid
stateDiagram-v2
    [*] --> Follower: Start
    
    Follower --> Candidate: Election timeout
    
    Candidate --> Leader: Receive majority votes
    Candidate --> Follower: Lose election/Higher term
    Candidate --> Candidate: Split vote/Retry
    
    Leader --> Follower: Discover higher term
    
    note right of Follower
        - Follow current leader
        - Respond to vote requests
        - Reset timer on heartbeat
    end note
    
    note right of Candidate  
        - Increment term
        - Vote for self
        - Request votes
    end note
    
    note right of Leader
        - Send heartbeats
        - Process client requests  
        - Replicate decisions
    end note
```

### Term Progression Example

```mermaid
gantt
    title Leader Election Terms Over Time
    dateFormat X
    axisFormat Term %d
    
    section Node 1
    Follower (T0)    :0, 1
    Candidate (T1)   :crit, 1, 1  
    Leader (T1)      :active, 2, 3
    Follower (T2)    :5, 2
    
    section Node 2
    Follower (T0)    :0, 1
    Follower (T1)    :1, 4
    Candidate (T2)   :crit, 5, 1
    Leader (T2)      :active, 6, 1
    
    section Node 3
    Follower (T0)    :0, 1
    Follower (T1)    :1, 4
    Follower (T2)    :5, 2
    
    section Events
    Election 1       :milestone, 1, 0
    Node1 Wins       :milestone, 2, 0
    Node1 Fails      :milestone, 5, 0
    Election 2       :milestone, 5, 0
    Node2 Wins       :milestone, 6, 0
```

### Consensus Requirements

#### Majority Quorum
- 5 nodes: Need 3 votes (majority = ⌊5/2⌋ + 1)
- 7 nodes: Need 4 votes
- 9 nodes: Need 5 votes

**Why majority?** Prevents split brain, tolerates failures, ensures overlap.

#### Timing Parameters

| Parameter | Typical Range | Purpose |
|-----------|---------------|----------|
| **Election Timeout** | 150-300ms | Trigger election (randomized) |
| **Heartbeat Interval** | 50-150ms | Maintain leadership |
| **RPC Timeout** | 10-50ms | Network calls |

### Raft Algorithm Implementation

```mermaid
graph TB
    subgraph "Raft Node Structure"
        subgraph "Persistent State"
            Term[Current Term]
            Vote[Voted For]
            Log[Log Entries]
        end
        
        subgraph "Volatile State"
            State[State: F/C/L]
            Leader[Current Leader]
            Timeout[Election Timeout]
        end
        
        subgraph "Leader Only"
            NextIdx[Next Index[]]
            MatchIdx[Match Index[]]
        end
    end
    
    subgraph "Core Operations"
        Election[Start Election]
        Heartbeat[Send Heartbeats]
        Replicate[Replicate Entries]
        Vote[Request Votes]
    end
    
    State -->|CANDIDATE| Election
    State -->|LEADER| Heartbeat
    State -->|LEADER| Replicate
    Election --> Vote
```

### Election Algorithm Flow

```mermaid
flowchart LR
    subgraph "Follower Loop"
        F1[Check heartbeat]
        F2{Timeout?}
        F3[Reset timer]
        F4[Become candidate]
        
        F1 --> F2
        F2 -->|No heartbeat| F1
        F2 -->|Heartbeat received| F3
        F3 --> F1
        F2 -->|Election timeout| F4
    end
    
    subgraph "Candidate Loop"
        C1[Increment term]
        C2[Vote for self]
        C3[Request votes]
        C4{Majority?}
        C5[Become leader]
        C6[Back to follower]
        
        F4 --> C1
        C1 --> C2
        C2 --> C3
        C3 --> C4
        C4 -->|Yes| C5
        C4 -->|No| C6
        C6 --> F1
    end
    
    subgraph "Leader Loop"
        L1[Send heartbeats]
        L2[Process requests]
        L3{Higher term?}
        L4[Step down]
        
        C5 --> L1
        L1 --> L2
        L2 --> L3
        L3 -->|No| L1
        L3 -->|Yes| L4
        L4 --> F1
    end
```

### Leader Election Communication Pattern

```mermaid
sequenceDiagram
    participant F as Follower
    participant C as Candidate  
    participant L as Leader
    participant P1 as Peer 1
    participant P2 as Peer 2
    
    rect rgb(240, 240, 255)
        Note over F: Election Timeout
        F->>C: Become Candidate
        C->>C: term++, vote for self
        
        par Request Votes
            C->>P1: RequestVote(term, lastLog)
            C->>P2: RequestVote(term, lastLog)
        end
        
        P1-->>C: Vote granted
        P2-->>C: Vote granted
        
        Note over C: Majority achieved (3/3)
        C->>L: Become Leader
    end
    
    rect rgb(240, 255, 240)
        Note over L: Leader Operations
        loop Every 50ms
            L->>P1: Heartbeat
            L->>P2: Heartbeat
            P1-->>L: Success
            P2-->>L: Success
        end
    end
    
    rect rgb(255, 240, 240)
        Note over L: Discover higher term
        P1->>L: Response(term=5)
        Note over L: My term=3, their term=5
        L->>F: Step down to Follower
    end
```

    async def _heartbeat_loop(self):
        """Send heartbeats if leader"""
        while self._running:
            try:
                if self.state == NodeState.LEADER:
                    await self._send_heartbeats()

                await asyncio.sleep(self.heartbeat_interval / 1000)

            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")

    async def _become_candidate(self):
        """Transition to candidate and start election"""
        self.state = NodeState.CANDIDATE
        self.current_term.number += 1
        self.current_term.voted_for = self.node_id
        self.votes_received = {self.node_id}  # Vote for self
        self.election_timeout = self._random_timeout()

        self.logger.info(f"Became candidate for term {self.current_term.number}")

        # Request votes from all peers
        vote_tasks = []
        for peer_id in self.peers:
            if peer_id != self.node_id:
                vote_tasks.append(self._request_vote(peer_id))

        # Wait for votes
        results = await asyncio.gather(*vote_tasks, return_exceptions=True)

        # Count votes
        for i, peer_id in enumerate(self.peers):
            if peer_id != self.node_id and results[i-1] is True:
                self.votes_received.add(peer_id)

        # Check if won election
        if len(self.votes_received) > len(self.peers) / 2:
            await self._become_leader()
        else:
            # Lost election, revert to follower
            self.logger.info(f"Lost election with {len(self.votes_received)} votes")
            self.state = NodeState.FOLLOWER
            self.last_heartbeat = time.time() * 1000

    async def _request_vote(self, peer_id: str) -> bool:
        """Request vote from a peer"""
        try:
            # Use Redis for communication
            vote_key = f"vote_request:{peer_id}:{self.current_term.number}"
            response_key = f"vote_response:{self.node_id}:{self.current_term.number}"

            # Send vote request
            await self.redis.setex(
                vote_key,
                int(self.election_timeout / 1000),
                self.node_id
            )

            # Wait for response
            start_time = time.time()
            while time.time() - start_time < (self.election_timeout / 1000):
                response = await self.redis.get(response_key)
                if response:
                    await self.redis.delete(response_key)
                    return response == b"yes"
                await asyncio.sleep(0.01)

            return False

        except Exception as e:
            self.logger.error(f"Vote request error: {e}")
            return False

    async def _handle_vote_request(self, candidate_id: str, term: int) -> bool:
        """Handle incoming vote request"""
        # Grant vote if haven't voted in this term
        if term > self.current_term.number:
            self.current_term = Term(term)
            self.state = NodeState.FOLLOWER
            self.last_heartbeat = time.time() * 1000

        if (self.current_term.voted_for is None or
            self.current_term.voted_for == candidate_id):
            self.current_term.voted_for = candidate_id
            return True

        return False

    async def _become_leader(self):
        """Transition to leader state"""
        self.state = NodeState.LEADER
        self.leader_id = self.node_id
        self.current_term.leader_id = self.node_id

        self.logger.info(f"Became leader for term {self.current_term.number}")

        # Notify via callback
        if self.leader_callback:
            await self.leader_callback()

        # Send initial heartbeats
        await self._send_heartbeats()

    async def _send_heartbeats(self):
        """Send heartbeats to all followers"""
        heartbeat_tasks = []

        for peer_id in self.peers:
            if peer_id != self.node_id:
                heartbeat_tasks.append(self._send_heartbeat(peer_id))

        await asyncio.gather(*heartbeat_tasks, return_exceptions=True)

    async def _send_heartbeat(self, peer_id: str):
        """Send heartbeat to specific peer"""
        try:
            heartbeat_key = f"heartbeat:{peer_id}:{self.current_term.number}"

            await self.redis.setex(
                heartbeat_key,
                int(self.heartbeat_interval * 2 / 1000),
                f"{self.node_id}:{time.time()}"
            )

        except Exception as e:
            self.logger.error(f"Heartbeat error to {peer_id}: {e}")

    async def _handle_heartbeat(self, leader_id: str, term: int):
        """Handle incoming heartbeat"""
        if term >= self.current_term.number:
            self.current_term = Term(term, leader_id)
            self.state = NodeState.FOLLOWER
            self.leader_id = leader_id
            self.last_heartbeat = time.time() * 1000

            if self.follower_callback:
                await self.follower_callback(leader_id)

    async def _step_down(self):
        """Step down from leadership"""
        self.logger.info("Stepping down from leadership")
        self.state = NodeState.FOLLOWER
        self.leader_id = None
        self.last_heartbeat = time.time() * 1000

    def is_leader(self) -> bool:
        """Check if this node is the current leader"""
        return self.state == NodeState.LEADER

    def get_leader(self) -> Optional[str]:
        """Get current leader ID"""
        return self.leader_id

class DistributedLock:
    """Distributed lock implementation using leader election"""

    def __init__(self,
                 name: str,
                 node_id: str,
                 redis_client: aioredis.Redis,
                 ttl: int = 30):
        self.name = name
        self.node_id = node_id
        self.redis = redis_client
        self.ttl = ttl
        self._lock_key = f"dlock:{name}"
        self._owner_key = f"dlock:owner:{name}"

    @asynccontextmanager
    async def acquire(self, timeout: float = 10.0):
        """Acquire distributed lock"""
        start_time = time.time()
        acquired = False

        try:
            while time.time() - start_time < timeout:
                # Try to acquire lock
                acquired = await self.redis.set(
                    self._lock_key,
                    self.node_id,
                    nx=True,
                    ex=self.ttl
                )

                if acquired:
                    # Store owner info
                    await self.redis.setex(
                        self._owner_key,
                        self.ttl,
                        f"{self.node_id}:{time.time()}"
                    )
                    break

                # Check if we already own it
                current_owner = await self.redis.get(self._lock_key)
                if current_owner and current_owner.decode() == self.node_id:
                    # Refresh TTL
                    await self.redis.expire(self._lock_key, self.ttl)
                    acquired = True
                    break

                await asyncio.sleep(0.1)

            if not acquired:
                raise TimeoutError(f"Failed to acquire lock {self.name}")

            yield

        finally:
            if acquired:
                # Release lock only if we own it
                await self._release()

    async def _release(self):
        """Release the lock if we own it"""
        current_owner = await self.redis.get(self._lock_key)
        if current_owner and current_owner.decode() == self.node_id:
            await self.redis.delete(self._lock_key, self._owner_key)

class LeaderElectedService:
    """Base class for services that require leader election"""

    def __init__(self,
                 node_id: str,
                 peers: List[NodeInfo],
                 redis_client: aioredis.Redis):
        self.node_id = node_id
        self.election = LeaderElection(node_id, peers, redis_client)
        self.election.leader_callback = self._on_became_leader
        self.election.follower_callback = self._on_became_follower
        self._leader_task: Optional[asyncio.Task] = None
        self.logger = logging.getLogger(f"Service[{node_id}]")

    async def start(self):
        """Start the service"""
        await self.election.start()
        self.logger.info("Service started")

    async def stop(self):
        """Stop the service"""
        if self._leader_task:
            self._leader_task.cancel()
        await self.election.stop()
        self.logger.info("Service stopped")

    async def _on_became_leader(self):
        """Called when this node becomes leader"""
        self.logger.info("Became leader, starting leader tasks")
        if self._leader_task:
            self._leader_task.cancel()
        self._leader_task = asyncio.create_task(self._leader_loop())

    async def _on_became_follower(self, leader_id: str):
        """Called when this node becomes follower"""
        self.logger.info(f"Became follower, leader is {leader_id}")
        if self._leader_task:
            self._leader_task.cancel()
            self._leader_task = None

    async def _leader_loop(self):
        """Override this to implement leader-specific tasks"""
        raise NotImplementedError

# Example: Distributed Job Scheduler
class DistributedScheduler(LeaderElectedService):
    """Job scheduler where only leader schedules jobs"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scheduled_jobs = {}

    async def _leader_loop(self):
        """Leader scheduling loop"""
        while self.election.is_leader():
            try:
                # Get pending jobs from Redis
                jobs = await self._get_pending_jobs()

                for job in jobs:
                    if job['id'] not in self.scheduled_jobs:
                        # Schedule new job
                        task = asyncio.create_task(self._execute_job(job))
                        self.scheduled_jobs[job['id']] = task
                        self.logger.info(f"Scheduled job {job['id']}")

                # Cleanup completed jobs
                completed = []
                for job_id, task in self.scheduled_jobs.items():
                    if task.done():
                        completed.append(job_id)

                for job_id in completed:
                    del self.scheduled_jobs[job_id]

                await asyncio.sleep(1)

            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(1)

    async def _get_pending_jobs(self) -> List[Dict]:
        """Get jobs from queue"""
        # Implementation depends on job storage
        return []

    async def _execute_job(self, job: Dict):
        """Execute a scheduled job"""
        self.logger.info(f"Executing job {job['id']}")
        # Job execution logic here
        await asyncio.sleep(job.get('duration', 1))

# Example: Shard Manager
class ShardManager(LeaderElectedService):
    """Manages shard assignments - only leader rebalances"""

    def __init__(self, *args, total_shards: int = 100, **kwargs):
        super().__init__(*args, **kwargs)
        self.total_shards = total_shards
        self.shard_assignments = {}

    async def _leader_loop(self):
        """Leader shard management loop"""
        while self.election.is_leader():
            try:
                # Get active nodes
                active_nodes = await self._get_active_nodes()

                # Check if rebalancing needed
                if self._needs_rebalancing(active_nodes):
                    new_assignments = self._calculate_assignments(active_nodes)
                    await self._apply_assignments(new_assignments)
                    self.logger.info("Rebalanced shards across nodes")

                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                self.logger.error(f"Shard manager error: {e}")
                await asyncio.sleep(10)

    async def _get_active_nodes(self) -> List[str]:
        """Get list of active nodes"""
        # Check heartbeats in Redis
        pattern = "heartbeat:*"
        active = []

        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern)
            for key in keys:
                node_id = key.decode().split(':')[1]
                if node_id not in active:
                    active.append(node_id)

            if cursor == 0:
                break

        return active

    def _needs_rebalancing(self, active_nodes: List[str]) -> bool:
        """Check if shards need rebalancing"""
        if not self.shard_assignments:
            return True

        # Check if nodes changed
        current_nodes = set(self.shard_assignments.values())
        active_set = set(active_nodes)

        return current_nodes != active_set

    def _calculate_assignments(self, nodes: List[str]) -> Dict[int, str]:
        """Calculate optimal shard distribution"""
        assignments = {}
        shards_per_node = self.total_shards // len(nodes)

        for i in range(self.total_shards):
            node_index = i // shards_per_node
            if node_index >= len(nodes):
                node_index = len(nodes) - 1
            assignments[i] = nodes[node_index]

        return assignments

    async def _apply_assignments(self, assignments: Dict[int, str]):
        """Apply new shard assignments"""
        # Store in Redis for all nodes to see
        pipe = self.redis.pipeline()

        for shard, node in assignments.items():
            pipe.hset("shard_assignments", str(shard), node)

        await pipe.execute()
        self.shard_assignments = assignments
```

---

## 🔧 Level 3: Deep Dive

### Advanced Election Scenarios

#### Split Vote Handling

```mermaid
sequenceDiagram
    participant A as Node A
    participant B as Node B
    participant C as Node C
    participant D as Node D
    participant E as Node E
    
    Note over A,E: Split Vote Scenario (Term 3)
    
    par Simultaneous Elections
        A->>A: Timeout! Become candidate
        B->>B: Timeout! Become candidate
    end
    
    par A requests votes
        A->>C: Vote for me (Term 3)
        A->>D: Vote for me (Term 3)
        A->>E: Vote for me (Term 3)
    and B requests votes
        B->>C: Vote for me (Term 3)
        B->>D: Vote for me (Term 3)
        B->>E: Vote for me (Term 3)
    end
    
    C-->>A: Vote granted (first request)
    D-->>B: Vote granted (first request)
    
    Note over E: Network delay...
    
    Note over A: Votes: 2/5 (self + C)
    Note over B: Votes: 2/5 (self + D)
    
    E-->>A: Vote granted (or timeout)
    
    Note over A,E: No majority! New election needed
    
    rect rgb(255, 240, 240)
        Note over A,E: Randomized timeouts prevent repeat
        Note over A: Timeout = 172ms
        Note over B: Timeout = 251ms
        A->>A: Start election (Term 4) first!
    end
```

### Split Vote Prevention

```mermaid
graph LR
    subgraph "Timeout Randomization"
        Base[Base: 150-300ms]
        Random[+Random: 0-150ms]
        Final[Final: 150-450ms]
        
        Base --> Random
        Random --> Final
    end
    
    subgraph "Exponential Backoff"
        Split1[1st split: 1x timeout]
        Split2[2nd split: 2x timeout]
        Split3[3rd split: 4x timeout]
        
        Split1 --> Split2
        Split2 --> Split3
    end
    
    Note1[Reduces probability of<br/>simultaneous elections]
    Note2[Gives network time<br/>to stabilize]
    
    Final -.-> Note1
    Split3 -.-> Note2
```

#### Network Partition Scenarios

```
Scenario 1: Clean Partition
[A, B] | [C, D, E]
- Right side elects leader (has majority)
- Left side cannot elect (no majority)
- System remains available

Scenario 2: Complex Partition  
[A, B] | [C] | [D, E]
- No partition has majority
- No leader can be elected
- System unavailable until partition heals

Scenario 3: Intermittent Partition
A ←→ B ←X→ C ←→ D ←→ E
- B-C link flaps
- May cause leadership instability
- Use stable leader preference
```

### Pre-Vote Optimization

```mermaid
sequenceDiagram
    participant I as Isolated Node
    participant L as Current Leader
    participant F1 as Follower 1
    participant F2 as Follower 2
    
    Note over I: Network issue, missed heartbeats
    
    rect rgb(255, 250, 240)
        Note over I,F2: Pre-Vote Phase (no term increment)
        I->>L: PreVote Request (hypothetical term 5)
        I->>F1: PreVote Request (hypothetical term 5)
        I->>F2: PreVote Request (hypothetical term 5)
        
        L-->>I: No (I'm still leader)
        F1-->>I: No (leader is alive)
        F2-->>I: No (leader is alive)
        
        Note over I: Pre-vote failed (1/4 votes)
        Note over I: Don't start real election
    end
    
    Note over L,F2: System remains stable!
    
    loop Leader continues
        L->>F1: Heartbeat
        L->>F2: Heartbeat
    end
```

### Pre-Vote Benefits

```mermaid
graph TB
    subgraph "Without Pre-Vote"
        WO1[Isolated node]
        WO2[Increment term]
        WO3[Force new election]
        WO4[Disrupt stable cluster]
        
        WO1 --> WO2 --> WO3 --> WO4
        
        style WO4 fill:#ef4444,stroke:#dc2626
    end
    
    subgraph "With Pre-Vote"
        W1[Isolated node]
        W2[Check if election viable]
        W3{Would win?}
        W4[Start election]
        W5[Stay follower]
        
        W1 --> W2 --> W3
        W3 -->|Yes| W4
        W3 -->|No| W5
        
        style W5 fill:#10b981,stroke:#059669
    end
```

### Leadership Transfer

```mermaid
sequenceDiagram
    participant C as Client
    participant L as Current Leader
    participant T as Target Node
    participant F1 as Follower 1
    participant F2 as Follower 2
    
    Note over L: Decide to transfer leadership
    
    rect rgb(240, 250, 255)
        Note over L,T: Phase 1: Preparation
        L->>L: Stop accepting new writes
        C->>L: Write request
        L-->>C: Redirect to new leader (pending)
        
        L->>T: Sync missing entries
        T-->>L: Acknowledge sync
        
        Note over L,T: Target is now up-to-date
    end
    
    rect rgb(240, 255, 240)
        Note over L,T: Phase 2: Transfer
        L->>T: TimeoutNow RPC
        T->>T: Immediately timeout
        T->>T: Start election (Term++)
        
        par Request votes
            T->>L: RequestVote
            T->>F1: RequestVote  
            T->>F2: RequestVote
        end
        
        Note over L: Support transfer
        L-->>T: Vote granted
        F1-->>T: Vote granted
        F2-->>T: Vote granted
        
        T->>T: Become leader
    end
    
    T->>L: AppendEntries (as new leader)
    T->>F1: AppendEntries
    T->>F2: AppendEntries
    
    L->>L: Become follower
    
    Note over C,F2: Smooth transition complete!
```

### Joint Consensus for Membership Changes

```python
class MembershipChange:
    """Safe cluster membership changes"""
    
    def add_node(self, new_node: str):
        """Add node using joint consensus"""
        # Phase 1: Joint configuration
        # Old AND new majority required
        self.config = JointConfig(
            old_nodes=self.current_nodes,
            new_nodes=self.current_nodes + [new_node]
        )
        
        # Phase 2: Replicate joint config
        self.replicate_config(self.config)
        
        # Phase 3: Transition to new config
        # Only new majority required
        self.config = NewConfig(self.current_nodes + [new_node])
        self.replicate_config(self.config)
```

---

## 🚀 Level 4: Expert

### Production Case Study: Apache Kafka

**Scale**: 2M+ partitions, 100s of brokers

```mermaid
graph TB
    subgraph "Kafka Controller Architecture"
        ZK[ZooKeeper<br/>Ensemble]
        
        subgraph "Controller Election"
            Path["/controller"<br/>ephemeral node]
            Controller[Controller Broker<br/>ID: 101]
        end
        
        subgraph "Brokers"
            B1[Broker 101<br/>CONTROLLER]
            B2[Broker 102]
            B3[Broker 103]
            B4[Broker 104]
        end
        
        subgraph "Partitions"
            P1[Topic-A-0<br/>Leader: 102]
            P2[Topic-A-1<br/>Leader: 103]
            P3[Topic-B-0<br/>Leader: 104]
        end
        
        ZK --> Path
        Path --> Controller
        Controller --> B1
        
        B1 -->|Manages| P1
        B1 -->|Manages| P2
        B1 -->|Manages| P3
        
        B2 -.->|ISR| P1
        B3 -.->|ISR| P2
        B4 -.->|ISR| P3
    end
    
    style B1 fill:#10b981,stroke:#059669,stroke-width:3px
    style Path fill:#fbbf24,stroke:#f59e0b
```

### Kafka Controller Responsibilities

```mermaid
flowchart LR
    subgraph "Controller Duties"
        PE[Partition<br/>Election]
        BR[Broker<br/>Registration]
        ISR[ISR<br/>Management]
        RM[Replica<br/>Management]
        MD[Metadata<br/>Updates]
    end
    
    subgraph "Failure Scenarios"
        BF[Broker Failure]
        CF[Controller Failure]
        PF[Partition Leader Failure]
    end
    
    BF -->|Trigger| PE
    CF -->|New Election| ZK[ZooKeeper]
    PF -->|Elect from ISR| PE
    
    PE --> MD
    BR --> MD
    ISR --> MD
    RM --> MD
```

### Real-World Challenges

#### Controller Hotspot
- **Problem**: Single controller bottleneck at scale
- **Solution**: Delegate to partition coordinators

```mermaid
graph TB
    subgraph "Before: Controller Bottleneck"
        C1[Controller]
        P1[1M Partitions]
        P2[1M Partitions]
        
        C1 -->|Manages all| P1
        C1 -->|Manages all| P2
        
        Note1[CPU: 95%<br/>Latency: High]
        C1 -.-> Note1
        
        style C1 fill:#ef4444,stroke:#dc2626
    end
    
    subgraph "After: Delegated Coordinators"
        C2[Controller]
        
        subgraph "Group Coordinators"
            GC1[Consumer<br/>Coordinator]
            GC2[Transaction<br/>Coordinator]
            GC3[Partition<br/>Coordinator 1]
            GC4[Partition<br/>Coordinator 2]
        end
        
        C2 -->|Delegates| GC1
        C2 -->|Delegates| GC2
        C2 -->|Delegates| GC3
        C2 -->|Delegates| GC4
        
        GC1 -->|200K parts| G1[Group 1]
        GC2 -->|Transactions| TX[TX Log]
        GC3 -->|500K parts| G3[Group 3]
        GC4 -->|500K parts| G4[Group 4]
        
        Note2[CPU: 40%<br/>Latency: Low]
        C2 -.-> Note2
        
        style C2 fill:#10b981,stroke:#059669
    end
```

#### ZooKeeper Removal (KRaft)
- **Problem**: External dependency on ZooKeeper
- **Solution**: Built-in Raft consensus

```mermaid
graph LR
    subgraph "Legacy: With ZooKeeper"
        K1[Kafka Cluster]
        Z1[ZooKeeper<br/>Ensemble]
        E1[External<br/>Dependency]
        
        K1 <-->|Controller election<br/>Metadata storage| Z1
        Z1 --> E1
        
        style E1 fill:#ef4444,stroke:#dc2626
    end
    
    subgraph "KRaft: Built-in Consensus"
        subgraph "Kafka Cluster"
            KR1[Controller 1<br/>Raft Node]
            KR2[Controller 2<br/>Raft Node]
            KR3[Controller 3<br/>Raft Node]
            
            KR1 <-->|Raft Protocol| KR2
            KR2 <-->|Raft Protocol| KR3
            KR1 <-->|Raft Protocol| KR3
        end
        
        Benefits[No external deps<br/>Simpler ops<br/>Better performance]
        
        style Benefits fill:#10b981,stroke:#059669
    end
```

### KRaft Metadata Log

```mermaid
sequenceDiagram
    participant C as Client
    participant L as Leader Controller
    participant F1 as Follower 1
    participant F2 as Follower 2
    participant ML as Metadata Log
    
    C->>L: Create Topic
    
    L->>ML: Append: CreateTopic
    L->>F1: Replicate entry
    L->>F2: Replicate entry
    
    F1-->>L: Ack
    F2-->>L: Ack
    
    L->>ML: Commit
    L-->>C: Topic created
    
    Note over ML: Metadata changes are<br/>ordered log entries
```

### Production Monitoring

```python
# Key metrics to track
METRICS = {
    'leader_elections_total': 'Election frequency',
    'election_duration_seconds': 'Time to elect',
    'leader_stable_seconds': 'Leadership stability',
    'active_leaders_count': 'Split brain detection'
}

# Critical alerts
ALERTS = [
    {
        'name': 'FrequentElections',
        'condition': 'rate(elections[5m]) > 0.1',
        'severity': 'warning'
    },
    {
        'name': 'NoLeader',
        'condition': 'active_leaders != 1',
        'severity': 'critical'
    }
]
```

---

## 🎯 Level 5: Mastery

### Theoretical Foundations

#### FLP Impossibility Result

**Fischer-Lynch-Paterson (1985)**: Cannot guarantee both safety and liveness in asynchronous systems with failures.

- **Problem**: Can't distinguish slow node from failed node
- **Trade-off**: Safety (no split brain) vs Liveness (always elect)
- **Solution**: Assume partial synchrony, use timeouts

#### Paxos vs Raft

| Aspect | Paxos | Raft |
|--------|-------|------|
| **Complexity** | High - multiple roles | Simple - leader-based |
| **Understandability** | Difficult | Designed for clarity |
| **Leader concept** | Optional | Central to algorithm |
| **Use cases** | General consensus | Leader election + logs |

### Advanced Optimizations

#### Hierarchical Election

Used by Microsoft Azure Cosmos DB for global scale:

```mermaid
graph TB
    subgraph "Global Scale Hierarchical Election"
        subgraph "Level 3: Global"
            GL[Global Leader<br/>Region: US-East]
        end
        
        subgraph "Level 2: Regional"
            RL1[Regional Leader<br/>Americas]
            RL2[Regional Leader<br/>Europe]
            RL3[Regional Leader<br/>Asia]
        end
        
        subgraph "Level 1: Datacenter"
            subgraph "US-East"
                DC1L[DC Leader]
                DC1N1[Node 1]
                DC1N2[Node 2]
            end
            
            subgraph "EU-West"
                DC2L[DC Leader]
                DC2N1[Node 1]
                DC2N2[Node 2]
            end
            
            subgraph "Asia-SE"
                DC3L[DC Leader]
                DC3N1[Node 1]
                DC3N2[Node 2]
            end
        end
        
        GL -.->|Coordinates| RL1
        GL -.->|Coordinates| RL2
        GL -.->|Coordinates| RL3
        
        RL1 -->|Manages| DC1L
        RL2 -->|Manages| DC2L
        RL3 -->|Manages| DC3L
        
        DC1L --> DC1N1
        DC1L --> DC1N2
        DC2L --> DC2N1
        DC2L --> DC2N2
        DC3L --> DC3N1
        DC3L --> DC3N2
    end
    
    style GL fill:#10b981,stroke:#059669,stroke-width:4px
    style RL1 fill:#3b82f6,stroke:#2563eb,stroke-width:3px
    style RL2 fill:#3b82f6,stroke:#2563eb,stroke-width:3px
    style RL3 fill:#3b82f6,stroke:#2563eb,stroke-width:3px
    style DC1L fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px
    style DC2L fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px
    style DC3L fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px
```

### Benefits of Hierarchical Election

| Level | Latency | Scope | Failure Impact |
|-------|---------|-------|----------------|
| **Local** | <1ms | Datacenter | Minimal |
| **Regional** | <50ms | Continent | Regional failover |
| **Global** | <200ms | Worldwide | Full re-election |

#### Witness Nodes

```mermaid
graph LR
    subgraph "Without Witness (4 nodes)"
        WO1[Data Node 1]
        WO2[Data Node 2]
        WO3[Data Node 3]
        WO4[Data Node 4]
        
        WO1 <--> WO2
        WO2 <--> WO3
        WO3 <--> WO4
        WO1 <--> WO4
        
        Cost1[Cost: 4 × $100 = $400/mo]
        Problem1[Problem: Even number<br/>No clear majority]
        
        style Problem1 fill:#ef4444,stroke:#dc2626
    end
    
    subgraph "With Witness (2+1 nodes)"
        W1[Data Node 1<br/>Full replica]
        W2[Data Node 2<br/>Full replica]
        W3[Witness Node<br/>Vote only]
        
        W1 <--> W2
        W2 <--> W3
        W1 <--> W3
        
        Cost2[Cost: 2 × $100 + $10 = $210/mo]
        Benefit[Benefit: Odd quorum<br/>47% cost savings]
        
        style W3 fill:#fbbf24,stroke:#f59e0b,stroke-width:2px
        style Benefit fill:#10b981,stroke:#059669
    end
```

### Witness Node Properties

| Property | Value | Purpose |
|----------|-------|---------|  
| **Storage** | None | Only participates in voting |
| **CPU** | Minimal | Just heartbeat processing |
| **Network** | Low bandwidth | Only election traffic |
| **Cost** | ~5% of data node | Economical quorum |

### Economic Impact

| Cost Without Leader | Cost With Leader | Savings |
|-------------------|------------------|----------|
| Conflict resolution: $500K/year | Implementation: $10K | $490K |
| Data inconsistency: $1M/year | Election downtime: $50K/year | $950K |
| **Total**: $1.5M/year | **Total**: $60K + $50K/year | **$1.44M/year** |

**ROI**: 2-week implementation pays back in < 1 month

### Future Directions

- **Byzantine Fault Tolerance**: Handle malicious nodes with cryptographic voting
- **ML-Enhanced**: Predict failures, auto-tune parameters
- **Quantum-Resistant**: Post-quantum cryptography for future-proof consensus

---

## 📊 Analysis & Trade-offs

### Axiom Relationships

| Axiom | How Leader Election Addresses It |
|-------|----------------------------------|
| **Latency** | Leader decisions avoid coordination delay |
| **Capacity** | Single leader prevents resource conflicts |
| **Failure** | Automatic failover on leader failure |
| **Concurrency** | Serializes decisions through leader |
| **Coordination** | Consensus protocol ensures agreement |
| **Observability** | Clear leader identity aids debugging |
| **Human Interface** | Simple mental model of single decider |
| **Economics** | Reduces coordination overhead costs |

### Trade-off Analysis

| Aspect | Gains | Losses |
|--------|-------|--------|
| **Consistency** | Strong coordination | Single point of failure |
| **Performance** | No coordination overhead | Leader bottleneck |
| **Availability** | Automatic failover | Election downtime |
| **Complexity** | Centralized decisions | Election protocol complexity |

### Common Pitfalls

1. **Split Brain Scenarios**
   - **Problem**: Network partition creates multiple leaders
   - **Solution**: Majority quorum requirement

2. **Leader Bottleneck**
   - **Problem**: All decisions go through one node
   - **Solution**: Delegate read operations to followers

3. **Cascading Elections**
   - **Problem**: Flapping leader causes repeated elections
   - **Solution**: Randomized timeouts, minimum leader time

4. **Clock Synchronization**
   - **Problem**: Timeout calculations assume synchronized clocks
   - **Solution**: Use logical clocks, generous timeouts

5. **Byzantine Failures**
   - **Problem**: Malicious nodes disrupt elections
   - **Solution**: Use Byzantine fault-tolerant protocols

---

## 🔧 Practical Considerations

### Configuration Guidelines

| Parameter | Description | Typical Range | Default |
|-----------|-------------|---------------|---------|
| **Election Timeout** | Time before starting election | 150-300ms | 200ms |
| **Heartbeat Interval** | Leader pulse frequency | 30-100ms | 50ms |
| **Majority Size** | Nodes needed to win | (n/2)+1 | - |
| **Term Duration** | Minimum leader tenure | 5-60s | 30s |

### Monitoring & Metrics

| Metric | What It Tells You | Alert Threshold |
|--------|-------------------|-----------------|
| **Election Frequency** | System stability | > 1/minute |
| **Leader Changes** | Failover rate | > 5/hour |
| **Election Duration** | Convergence time | > 5 seconds |
| **Split Brain Events** | Protocol violations | Any occurrence |

### Integration Patterns

How leader election works with other patterns:
- **With Sharding**: Leader assigns shards to nodes
- **With Saga Pattern**: Leader coordinates saga execution
- **With Distributed Lock**: Leader holds global locks
- **With Work Queue**: Leader distributes work items

---

## 🚀 Real-World Examples

### Example 1: Apache Kafka Controller
- **Challenge**: Manage partition leaders across brokers
- **Implementation**:
  - ZooKeeper-based leader election
  - Controller broker manages all metadata
  - Automatic failover on controller failure
- **Results**:
  - Consistent partition management
  - Fast leader failover (<5 seconds)
  - Simplified operational model

### Example 2: Kubernetes Controller Manager
- **Challenge**: Ensure only one controller modifies cluster state
- **Implementation**:
  - Leader election using ConfigMap/Lease
  - Active controller holds lease
  - Standby controllers wait
- **Results**:
  - No conflicting cluster modifications
  - High availability control plane
  - Clear operational responsibility

---

## 🎓 Key Takeaways

1. **Core Insight**: Leader election trades distributed complexity for a single coordination point
2. **When It Shines**: Centralized decision making, resource allocation, preventing conflicts
3. **What to Watch**: Leader bottlenecks, election storms, network partitions
4. **Remember**: A good leader election protocol is invisible when working, obvious when needed

---

---

*"In distributed systems, leadership is not about power—it's about responsibility for coordination."*

---

**Previous**: [← Idempotent Receiver Pattern](idempotent-receiver.md) | **Next**: [Load Balancing Pattern →](load-balancing.md)
## 📋 Quick Reference

### Decision Framework

| Question | Yes → Use Leader Election | No → Alternative |
|----------|--------------------------|------------------|
| Need single coordinator? | ✅ Essential pattern | ⚠️ Use distributed approach |
| Preventing split-brain? | ✅ Critical requirement | ⚠️ Consider eventual consistency |
| Resource allocation? | ✅ Leader assigns resources | ⚠️ Use work stealing |
| Configuration management? | ✅ Leader pushes updates | ⚠️ Use gossip protocol |
| Ordering guarantees? | ✅ Leader sequences operations | ⚠️ Use vector clocks |

### Implementation Checklist

- [ ] Choose consensus algorithm (Raft recommended)
- [ ] Set up majority quorum (odd number of nodes)
- [ ] Configure election timeouts (150-300ms)
- [ ] Implement heartbeat mechanism
- [ ] Add pre-vote optimization
- [ ] Handle network partitions
- [ ] Set up monitoring and alerts
- [ ] Test split-brain scenarios
- [ ] Document failover procedures
- [ ] Plan capacity for witness nodes

### Common Anti-Patterns

1. **Even number of nodes** - Can't form majority
2. **Too short timeouts** - Constant elections
3. **No pre-vote** - Disrupts stable clusters
4. **Ignoring clock skew** - Incorrect timeout calculations
5. **Single leader dependency** - No read scaling

---

## 🎓 Key Takeaways

1. **Consensus is hard** - Use proven algorithms (Raft, Paxos)
2. **Quorum matters** - Always use odd numbers (3, 5, 7)
3. **Timeouts are critical** - Too short causes instability
4. **Network partitions happen** - Design for split-brain
5. **Monitoring is essential** - Elections should be rare

---

*"In distributed systems, agreeing on who's in charge is often harder than doing the actual work."*

---

**Previous**: [← Bulkhead Pattern](bulkhead.md) | **Next**: [Service Discovery →](service-discovery.md)
