# Episode 32: Raft Consensus - सहमति का आसान तरीका

## मुंबई की कहानी: Society Election Process

आज मैं आपको Mumbai के Andheri में स्थित एक cooperative housing society की कहानी बताता हूं - "Harmony Heights". यह society 2015 में बनी थी और इसमें 200 families रहती हैं। हर साल society का chairman, secretary, और treasurer elect करना पड़ता है।

2019 में society election के दौरान एक बहुत interesting situation आया था। पूरी society के members को online voting system के through vote करना था, लेकिन Mumbai के monsoon की वजह से internet connectivity बहुत unstable था।

### Election Challenge

Society में तीन candidates थे chairman के लिए:

1. **Rajesh Sharma** (Building A representative) - अपने को "Leader" मानते थे
2. **Priya Patel** (Building B representative) - Technical background
3. **Mohan Singh** (Building C representative) - Senior-most resident

Normal election process यह होता है:
- सभी 200 families को vote करना है
- Majority (101+ votes) चाहिए जीतने के लिए  
- लेकिन network issues की वजह से कुछ families online नहीं आ पा रहे

### The Consensus Problem

यहां पर असली challenge यह था:

1. **Leader Selection**: कौन सा candidate actual में जीता है?
2. **Vote Counting**: अगर network partition हो जाए तो कैसे ensure करें कि सभी votes properly count हुए?
3. **Consistency**: सभी society members को same result पता होना चाहिए
4. **Availability**: System available रहना चाहिए even if कुछ building representatives offline हो जाएं

Traditional Paxos algorithm इस problem को solve कर सकता है, लेकिन इसकी complexity बहुत high है। Society के computer-savvy members (जो IT में काम करते हैं) ने suggest किया - क्यों न हम कोई simple approach use करें?

यहीं पर **Raft Consensus Algorithm** का concept आता है।

## Raft Algorithm: Theory Deep Dive

Raft consensus algorithm को 2013 में Diego Ongaro और John Ousterhout ने Stanford University में develop किया था। इसका main goal था - Paxos की complexity को reduce करना और understandable consensus algorithm बनाना।

### Core Design Philosophy

Raft के designers का motto था: **"Understandability"**

```
"We believe that Raft is superior to Paxos for building practical systems: 
it is more understandable than Paxos and provides a better foundation 
for building real systems."
```

### Key Differences from Paxos

| Aspect | Paxos | Raft |
|--------|--------|------|
| **Leader** | Optional (Multi-Paxos needs leader) | Always required |
| **Phases** | 2 phases (Prepare + Accept) | Leader Election + Log Replication |
| **Log Structure** | Gaps allowed | No gaps (sequential) |
| **Understanding** | Complex, hard to implement | Simple, intuitive |
| **Safety** | Hard to prove | Easier to verify |

### Raft State Machine

Har node teen states में से एक में होता है:

#### 1. Follower State

```python
class RaftFollower:
    def __init__(self):
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.last_applied = 0
        
    def handle_append_entries(self, leader_msg):
        # Heartbeat या log replication message
        if leader_msg.term >= self.current_term:
            self.current_term = leader_msg.term
            self.reset_election_timeout()
            
            # Log consistency check
            if self.log_matches(leader_msg.prev_log_index, leader_msg.prev_log_term):
                self.append_new_entries(leader_msg.entries)
                self.commit_index = min(leader_msg.leader_commit, len(self.log) - 1)
                return True
            
        return False
        
    def handle_vote_request(self, candidate_msg):
        # Vote for candidate if conditions met
        if (candidate_msg.term > self.current_term and 
            self.voted_for is None and 
            self.candidate_log_is_up_to_date(candidate_msg)):
            
            self.voted_for = candidate_msg.candidate_id
            self.current_term = candidate_msg.term
            return True
            
        return False
```

**Society Example**: Regular society members जो बस vote करते हैं और chairman के decisions को follow करते हैं।

#### 2. Candidate State

```python
class RaftCandidate:
    def __init__(self):
        self.current_term = 0
        self.votes_received = 0
        self.election_timeout = random.uniform(150, 300)  # milliseconds
        
    def start_election(self):
        # Increment term and vote for self
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = 1
        
        # Request votes from all other nodes
        for node in self.cluster_nodes:
            if node != self.node_id:
                vote_request = {
                    'term': self.current_term,
                    'candidate_id': self.node_id,
                    'last_log_index': len(self.log) - 1,
                    'last_log_term': self.log[-1].term if self.log else 0
                }
                
                response = node.send_vote_request(vote_request)
                if response.vote_granted:
                    self.votes_received += 1
                    
        # Check if won election
        if self.votes_received > len(self.cluster_nodes) // 2:
            self.become_leader()
        else:
            self.become_follower()
```

**Society Example**: Chairman के लिए nominate हुए candidates election के दौरान।

#### 3. Leader State

```python
class RaftLeader:
    def __init__(self):
        self.next_index = {}  # Next log entry to send to each follower
        self.match_index = {}  # Highest log entry known to be replicated on follower
        self.heartbeat_interval = 50  # milliseconds
        
    def send_heartbeats(self):
        # Send empty AppendEntries as heartbeat
        for follower in self.followers:
            heartbeat = {
                'term': self.current_term,
                'leader_id': self.node_id,
                'prev_log_index': self.next_index[follower] - 1,
                'prev_log_term': self.get_log_term(self.next_index[follower] - 1),
                'entries': [],  # Empty for heartbeat
                'leader_commit': self.commit_index
            }
            
            follower.send_append_entries(heartbeat)
            
    def replicate_entry(self, entry):
        # Add entry to local log
        entry.term = self.current_term
        entry.index = len(self.log)
        self.log.append(entry)
        
        # Replicate to followers
        successful_replications = 1  # Leader counts as one
        
        for follower in self.followers:
            if self.replicate_to_follower(follower, entry):
                successful_replications += 1
                
        # Commit if majority replicated
        if successful_replications > len(self.cluster) // 2:
            self.commit_index = entry.index
            self.apply_to_state_machine(entry)
            return True
            
        return False
```

**Society Example**: Elected chairman जो सभी decisions लेता है और other members को inform करता है।

### Leader Election Process

#### Step-by-step Election

**1. Election Timeout**

```python
class ElectionTimer:
    def __init__(self):
        # Randomized timeout to avoid split votes
        self.timeout = random.uniform(150, 300)  # milliseconds
        self.last_heartbeat = time.now()
        
    def should_start_election(self):
        return (time.now() - self.last_heartbeat) > self.timeout
        
    def reset(self):
        self.last_heartbeat = time.now()
        self.timeout = random.uniform(150, 300)
```

**Society Analogy**: अगर chairman से कोई communication नहीं आया prescribed time में, तो election शुरू हो जाता है।

**2. Vote Collection**

```python
class VoteCollector:
    def collect_votes(self, candidate_info):
        votes = {}
        
        for member in self.society_members:
            vote_criteria = self.evaluate_candidate(candidate_info, member)
            
            # Raft vote criteria:
            # 1. Haven't voted in this term
            # 2. Candidate's log is at least as up-to-date
            # 3. Term is current
            
            if (not member.voted_in_term and 
                self.candidate_log_up_to_date(candidate_info) and
                candidate_info.term >= member.current_term):
                
                votes[member.id] = True
                member.voted_for = candidate_info.id
                member.voted_in_term = True
                
        return votes
```

**3. Split Vote Handling**

```python
def handle_split_vote():
    """
    अगर कोई candidate को majority नहीं मिली:
    1. सभी candidates वापस follower बन जाते हैं
    2. नया election term शुरू होता है  
    3. Randomized timeout से split vote chances कम होते हैं
    """
    
    for candidate in candidates:
        if candidate.votes <= total_members // 2:
            candidate.state = "FOLLOWER"
            candidate.reset_election_timeout()
    
    # New election will start after random timeout
```

### Log Replication Mechanism

#### Log Structure

```python
class RaftLogEntry:
    def __init__(self, command, term, index):
        self.command = command  # Actual operation
        self.term = term       # Term when entry was created
        self.index = index     # Position in log
        self.committed = False
        
class RaftLog:
    def __init__(self):
        self.entries = []
        self.commit_index = 0
        
    def append(self, command, term):
        entry = RaftLogEntry(command, term, len(self.entries))
        self.entries.append(entry)
        return entry.index
        
    def get_entry(self, index):
        if 0 <= index < len(self.entries):
            return self.entries[index]
        return None
        
    def matches(self, index, term):
        # Check if log has entry at index with given term
        entry = self.get_entry(index)
        return entry is not None and entry.term == term
```

#### Replication Process

**Society Example**: Chairman के decisions का propagation

```python
class SocietyDecisionReplication:
    def make_decision(self, decision):
        """
        Chairman (Leader) ने decision लिया है:
        उदाहरण - "Painting contract approve करें ABC Company को"
        """
        
        # Step 1: Add to leader's log
        log_entry = {
            'decision': decision,
            'term': self.current_term,
            'timestamp': datetime.now(),
            'decision_id': self.generate_decision_id()
        }
        
        self.log.append(log_entry)
        
        # Step 2: Replicate to building representatives (followers)
        replication_count = 1  # Leader counts
        
        for building_rep in self.building_representatives:
            if self.send_decision_to_rep(building_rep, log_entry):
                replication_count += 1
                
        # Step 3: Commit if majority acknowledged
        total_reps = len(self.building_representatives) + 1  # +1 for leader
        
        if replication_count > total_reps // 2:
            self.commit_decision(log_entry)
            self.notify_all_members(log_entry)
            return True
            
        return False
        
    def send_decision_to_rep(self, rep, decision):
        # Building representative को decision भेजना
        message = {
            'type': 'APPEND_ENTRIES',
            'term': self.current_term,
            'leader_id': self.chairman_id,
            'prev_decision_id': self.get_last_decision_id(),
            'decision': decision,
            'committed_decisions': self.committed_decisions
        }
        
        response = rep.receive_decision(message)
        return response.success
```

#### Consistency Guarantees

**1. Log Matching Property**

```python
def verify_log_matching(leader_log, follower_log):
    """
    If two logs contain an entry with the same index and term,
    then all preceding entries are identical.
    """
    
    for i in range(min(len(leader_log), len(follower_log))):
        if (leader_log[i].index == follower_log[i].index and 
            leader_log[i].term == follower_log[i].term):
            
            # All previous entries should match
            for j in range(i):
                assert leader_log[j].equals(follower_log[j])
            
    return True
```

**2. Leader Completeness Property**

```python
def leader_completeness_check(new_leader, previous_committed_entries):
    """
    New leader contains all committed entries from previous terms
    """
    
    for committed_entry in previous_committed_entries:
        # New leader's log must contain this entry
        found = False
        for entry in new_leader.log:
            if (entry.index == committed_entry.index and 
                entry.term == committed_entry.term):
                found = True
                break
                
        assert found, f"Leader missing committed entry {committed_entry.index}"
```

## Production Use Cases

### etcd: Kubernetes' Brain

etcd is the distributed key-value store that powers Kubernetes, और यह Raft consensus का use करता है।

#### Architecture Deep Dive

```go
// etcd Raft implementation structure
type RaftNode struct {
    id        uint64
    term      uint64
    vote      uint64
    lead      uint64
    
    raftLog   *raftLog
    state     StateType
    
    msgs      []pb.Message
    
    // Progress tracking for followers  
    prs       map[uint64]*Progress
    
    // Election and heartbeat timers
    electionElapsed  int
    heartbeatElapsed int
}

type raftLog struct {
    storage   Storage
    unstable  unstable
    
    committed uint64
    applied   uint64
    
    logger    Logger
}
```

#### Key-Value Operations with Raft

```go
// etcd में key-value operation कैसे work करता है

func (s *EtcdServer) Put(key, value string) error {
    // 1. Create log entry
    entry := &pb.InternalRaftRequest{
        Put: &pb.PutRequest{
            Key:   []byte(key),
            Value: []byte(value),
        },
    }
    
    // 2. Propose through Raft
    data, err := entry.Marshal()
    if err != nil {
        return err
    }
    
    // 3. Raft consensus
    err = s.raftNode.Propose(data)
    if err != nil {
        return err
    }
    
    // 4. Wait for commit
    return s.waitForCommit(entry.ID)
}

func (s *EtcdServer) applyEntry(entry *pb.InternalRaftRequest) {
    // Apply committed entry to state machine
    switch entry.Type {
    case PUT:
        s.store.Put(entry.Put.Key, entry.Put.Value)
    case DELETE:
        s.store.Delete(entry.Delete.Key)
    case RANGE:
        return s.store.Range(entry.Range.Key, entry.Range.RangeEnd)
    }
}
```

#### Production Metrics

**Netflix's etcd Usage**:
- 5-node etcd clusters per region
- 10,000+ configuration updates per minute
- 99.9% availability during network partitions
- Sub-5ms write latency within datacenter

**Kubernetes Control Plane Stats**:
- etcd handles cluster state for 5000+ nodes
- API server interactions: 100K+ requests/second
- Watch operations: 50K+ concurrent watchers

### Consul: Service Discovery with Raft

HashiCorp Consul uses Raft for maintaining service registry और health check information।

#### Consul Raft Implementation

```go
type ConsulRaft struct {
    raft     *raft.Raft
    store    *raftboltdb.BoltStore
    snapshot *raft.FileSnapshotStore
    
    // Service registry state machine
    fsm      *consulFSM
}

type consulFSM struct {
    state *state.Store
}

func (c *consulFSM) Apply(log *raft.Log) interface{} {
    // Apply service registration/deregistration
    var req structs.RegisterRequest
    if err := structs.Decode(log.Data, &req); err != nil {
        return err
    }
    
    // Update service registry
    return c.state.EnsureService(&req)
}

// Service Registration through Raft
func (a *Agent) RegisterService(service *structs.NodeService) error {
    req := structs.RegisterRequest{
        Node:    a.config.NodeName,
        Service: service,
    }
    
    // Serialize request
    data, err := structs.Encode(structs.RegisterRequestType, req)
    if err != nil {
        return err
    }
    
    // Propose through Raft
    future := a.raft.Apply(data, raftTimeout)
    return future.Error()
}
```

#### Health Check Consensus

```go
func (a *Agent) updateHealthCheck(checkID string, status string) {
    update := &structs.HealthCheck{
        Node:      a.config.NodeName, 
        CheckID:   checkID,
        Status:    status,
        Output:    "Health check result",
        Timestamp: time.Now(),
    }
    
    // Replicate health status through Raft
    req := structs.RegisterRequest{
        Node:  a.config.NodeName,
        Check: update,
    }
    
    a.raftApply(structs.RegisterRequestType, &req)
}
```

### CockroachDB: Distributed SQL with Raft

CockroachDB uses Raft for replicating SQL data across multiple nodes।

#### Range-Based Replication

```go
// CockroachDB में har range का अपना Raft group होता है
type Replica struct {
    rangeID    roachpb.RangeID
    store     *Store
    
    // Raft group for this range
    raftGroup  *raft.RawNode
    
    // Proposal tracking
    proposals  map[storagebase.CmdIDKey]*ProposalData
    
    mu struct {
        state      storagebase.ReplicaState
        lastIndex  uint64
        raftLogSize int64
    }
}

func (r *Replica) propose(ctx context.Context, p *ProposalData) error {
    // SQL command को Raft through propose करना
    
    // 1. Encode command
    data, err := protoutil.Marshal(&p.Request)
    if err != nil {
        return err
    }
    
    // 2. Propose to Raft group
    return r.raftGroup.Propose(data)
}

func (r *Replica) applyCommand(cmd *storagebase.ReplicatedEvalResult) {
    // Apply committed SQL operations
    batch := r.store.Engine().NewWriteOnlyBatch()
    defer batch.Close()
    
    // Apply writes to storage engine
    for _, write := range cmd.WriteBatch.Repr {
        batch.Put(write.Key, write.Value)
    }
    
    batch.Commit()
}
```

#### SQL Transaction Coordination

```sql
-- CockroachDB में distributed transaction
BEGIN;

INSERT INTO users (id, name, email) VALUES (1, 'John', 'john@example.com');
INSERT INTO orders (user_id, product_id, quantity) VALUES (1, 100, 2);

COMMIT;
```

```go
// इसके behind, Raft consensus होता है
func (tc *TxnCoordinator) commitTransaction(txn *roachpb.Transaction) error {
    // For each range involved in transaction
    for _, rangeDesc := range txn.InvolvedRanges {
        
        // Create commit request
        commitReq := &roachpb.EndTxnRequest{
            RequestHeader: roachpb.RequestHeader{
                Key: txn.Key,
            },
            Txn:    txn,
            Commit: true,
        }
        
        // Send through Raft to range leader
        replica := tc.getReplicaForRange(rangeDesc.RangeID)
        err := replica.propose(ctx, commitReq)
        if err != nil {
            return err
        }
    }
    
    return nil
}
```

## Implementation Insights

### Performance Optimizations

#### 1. Batching और Pipelining

```go
type RaftBatcher struct {
    proposals    [][]byte
    batchSize    int
    flushTimeout time.Duration
    
    // Metrics
    batchesSent     int64
    avgBatchSize    float64
}

func (b *RaftBatcher) propose(data []byte) error {
    b.proposals = append(b.proposals, data)
    
    // Flush if batch is full or timeout reached
    if len(b.proposals) >= b.batchSize {
        return b.flush()
    }
    
    return nil
}

func (b *RaftBatcher) flush() error {
    if len(b.proposals) == 0 {
        return nil
    }
    
    // Combine all proposals into single Raft entry
    batch := &BatchProposal{
        Proposals: b.proposals,
        Count:     len(b.proposals),
    }
    
    data, _ := proto.Marshal(batch)
    err := b.raft.Propose(data)
    
    if err == nil {
        b.batchesSent++
        b.updateAvgBatchSize()
        b.proposals = b.proposals[:0] // Reset slice
    }
    
    return err
}
```

#### 2. Log Compaction और Snapshots

```go
type SnapshotManager struct {
    raft           *raft.Raft
    snapshotStore  raft.SnapshotStore
    
    // Configuration
    retainLogs     uint64  // Keep last N log entries
    snapshotThreshold uint64 // Create snapshot after N entries
}

func (sm *SnapshotManager) shouldSnapshot() bool {
    lastIndex := sm.raft.LastIndex()
    return lastIndex-sm.lastSnapshotIndex > sm.snapshotThreshold
}

func (sm *SnapshotManager) createSnapshot() error {
    // Get current state
    snapshot := &Snapshot{
        Index: sm.raft.LastIndex(),
        Term:  sm.raft.GetCurrentTerm(),
        State: sm.getStateMachineState(),
    }
    
    // Persist snapshot
    sink, err := sm.snapshotStore.Create(snapshot.Index, snapshot.Term, nil)
    if err != nil {
        return err
    }
    
    // Write state to snapshot
    encoder := gob.NewEncoder(sink)
    err = encoder.Encode(snapshot.State)
    if err != nil {
        sink.Cancel()
        return err
    }
    
    // Close and persist
    return sink.Close()
}

func (sm *SnapshotManager) compactLogs() {
    // Remove old log entries
    firstIndex := sm.raft.FirstIndex()
    lastIndex := sm.raft.LastIndex()
    
    if lastIndex-firstIndex > sm.retainLogs {
        compactIndex := lastIndex - sm.retainLogs
        sm.raft.Compact(compactIndex)
    }
}
```

#### 3. Network Optimizations

```go
type RaftTransport struct {
    // Connection pooling
    connPool     map[raft.ServerID]*grpc.ClientConn
    connPoolMu   sync.RWMutex
    
    // Message compression
    compression  bool
    compressor   *gzip.Writer
    
    // Batching
    msgBuffer    []raft.RPC
    bufferTimer  *time.Timer
}

func (t *RaftTransport) sendAppendEntries(target raft.ServerID, req *raft.AppendEntriesRequest) error {
    conn := t.getConnection(target)
    
    // Compress large payloads
    if t.compression && len(req.Entries) > 1000 {
        req.Entries = t.compressEntries(req.Entries)
    }
    
    // Send via gRPC
    client := NewRaftServiceClient(conn)
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()
    
    resp, err := client.AppendEntries(ctx, req)
    if err != nil {
        return err
    }
    
    // Process response
    return t.processAppendResponse(resp)
}
```

### Monitoring और Observability

#### 1. Raft State Metrics

```go
type RaftMetrics struct {
    // Leadership metrics
    isLeader          prometheus.GaugeFunc
    leaderChanges     prometheus.Counter
    leadershipDuration prometheus.Histogram
    
    // Log metrics  
    logSize           prometheus.GaugeFunc
    commitIndex       prometheus.GaugeFunc
    appliedIndex      prometheus.GaugeFunc
    logReplicationLag prometheus.HistogramVec
    
    // Election metrics
    electionTimeout   prometheus.Counter
    voteRequests      prometheus.CounterVec
    
    // Performance metrics
    proposalDuration  prometheus.Histogram
    proposalRate      prometheus.Gauge
}

func (m *RaftMetrics) recordProposal(duration time.Duration, success bool) {
    m.proposalDuration.Observe(duration.Seconds())
    
    if success {
        m.proposalRate.Inc()
    }
}

func (m *RaftMetrics) recordLeaderChange(newLeader raft.ServerID) {
    m.leaderChanges.Inc()
    
    // Record leadership duration if stepping down
    if m.wasLeader {
        duration := time.Since(m.leadershipStart)
        m.leadershipDuration.Observe(duration.Seconds())
    }
    
    m.leadershipStart = time.Now()
}
```

#### 2. Health Checks

```go
type RaftHealthChecker struct {
    raft           *raft.Raft
    lastHeartbeat  time.Time
    
    // Thresholds
    heartbeatTimeout time.Duration
    maxLogLag       uint64
}

func (hc *RaftHealthChecker) checkHealth() error {
    // Check 1: Recent heartbeat from leader
    if time.Since(hc.lastHeartbeat) > hc.heartbeatTimeout {
        return errors.New("no recent heartbeat from leader")
    }
    
    // Check 2: Log replication lag
    commitIndex := hc.raft.CommitIndex()
    lastIndex := hc.raft.LastIndex()
    
    if lastIndex-commitIndex > hc.maxLogLag {
        return fmt.Errorf("log replication lag too high: %d", lastIndex-commitIndex)
    }
    
    // Check 3: Can communicate with majority
    if !hc.canReachMajority() {
        return errors.New("cannot reach majority of cluster")
    }
    
    return nil
}
```

### Advanced Features

#### 1. Membership Changes

```go
func (r *RaftCluster) addServer(serverID raft.ServerID, address string) error {
    // Add server configuration change
    configChange := raft.Configuration{
        Servers: append(r.getCurrentConfig().Servers, raft.Server{
            ID:      serverID,
            Address: raft.ServerAddress(address),
        }),
    }
    
    // Propose configuration change through Raft
    future := r.raft.ChangeConfiguration(configChange)
    if err := future.Error(); err != nil {
        return fmt.Errorf("failed to add server: %v", err)
    }
    
    return nil
}

func (r *RaftCluster) removeServer(serverID raft.ServerID) error {
    currentConfig := r.getCurrentConfig()
    newServers := make([]raft.Server, 0)
    
    // Remove server from configuration
    for _, server := range currentConfig.Servers {
        if server.ID != serverID {
            newServers = append(newServers, server)
        }
    }
    
    newConfig := raft.Configuration{Servers: newServers}
    future := r.raft.ChangeConfiguration(newConfig)
    
    return future.Error()
}
```

#### 2. Learner Nodes (Read Replicas)

```go
type LearnerNode struct {
    raftLog      *raftLog
    leader       raft.ServerID
    
    // Read-only state
    appliedIndex uint64
    stateMachine StateMachine
}

func (ln *LearnerNode) handleLogEntry(entry *raft.LogEntry) {
    // Apply entry to local state machine (read-only)
    if entry.Index > ln.appliedIndex {
        ln.stateMachine.Apply(entry)
        ln.appliedIndex = entry.Index
    }
}

func (ln *LearnerNode) serveReadQuery(query ReadQuery) (interface{}, error) {
    // Serve reads from local state
    // No consensus needed for reads
    return ln.stateMachine.Query(query), nil
}
```

## Comparison: Raft vs Other Consensus

### Raft vs Paxos

```python
class ConsensusComparison:
    def raft_vs_paxos(self):
        return {
            'raft': {
                'phases': 'Leader Election + Log Replication',
                'complexity': 'Low - easy to understand',
                'leader': 'Always required',
                'log_structure': 'Sequential, no gaps',
                'implementation': 'Straightforward',
                'popular_uses': ['etcd', 'Consul', 'CockroachDB']
            },
            'paxos': {
                'phases': 'Prepare + Accept (2 phases)',
                'complexity': 'High - hard to understand',
                'leader': 'Optional (Multi-Paxos needs one)',
                'log_structure': 'Can have gaps',
                'implementation': 'Complex, error-prone',
                'popular_uses': ['Chubby', 'Spanner', 'Bigtable']
            }
        }
```

### When to Choose Raft

**Choose Raft When**:
1. Team needs to understand and debug consensus
2. Building new distributed system
3. Need simple, reliable consensus
4. Sequential log operations are acceptable

**Choose Paxos When**:
1. Need to handle arbitrary proposal ordering
2. Working with existing Paxos infrastructure
3. Academic research or theoretical work
4. Need to optimize for specific performance patterns

## Society Election: Raft Implementation

Let me show how our Mumbai society election would work with Raft:

### Society Raft Implementation

```python
class SocietyElectionRaft:
    def __init__(self, building_reps):
        self.state = "FOLLOWER"
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.building_reps = building_reps
        
    def handle_chairman_timeout(self):
        """जब chairman से कुछ time तक communication न आए"""
        if self.state == "FOLLOWER":
            self.start_election()
            
    def start_election(self):
        """Election शुरू करना"""
        self.state = "CANDIDATE"
        self.current_term += 1
        self.voted_for = self.rep_id
        
        votes = 1  # Vote for self
        
        # अन्य building representatives से vote मांगना
        for rep in self.building_reps:
            if rep.id != self.rep_id:
                vote_request = {
                    'term': self.current_term,
                    'candidate_id': self.rep_id,
                    'last_decision_index': len(self.log) - 1,
                    'last_decision_term': self.log[-1]['term'] if self.log else 0
                }
                
                if rep.request_vote(vote_request):
                    votes += 1
                    
        # Majority check
        if votes > len(self.building_reps) // 2:
            self.become_chairman()
        else:
            self.state = "FOLLOWER"
            
    def become_chairman(self):
        """Chairman बनना"""
        self.state = "LEADER"
        
        # सभी को heartbeat भेजना
        for rep in self.building_reps:
            self.send_heartbeat(rep)
            
    def make_society_decision(self, decision):
        """Society decision लेना (chairman only)"""
        if self.state != "LEADER":
            return False
            
        # Decision को log में add करना
        log_entry = {
            'decision': decision,
            'term': self.current_term,
            'index': len(self.log),
            'timestamp': datetime.now()
        }
        
        self.log.append(log_entry)
        
        # सभी building reps को replicate करना
        replications = 1  # Chairman counts
        
        for rep in self.building_reps:
            if self.replicate_decision(rep, log_entry):
                replications += 1
                
        # Majority से replicate हुआ तो commit
        if replications > len(self.building_reps) // 2:
            self.commit_decision(log_entry)
            return True
            
        return False
```

### Real-world Example

```python
# Harmony Heights Society - 3 building representatives
building_a_rep = SocietyElectionRaft(['A', 'B', 'C'])  # Rajesh
building_b_rep = SocietyElectionRaft(['A', 'B', 'C'])  # Priya  
building_c_rep = SocietyElectionRaft(['A', 'B', 'C'])  # Mohan

# Scenario: Network partition होता है
# Building A और B connected हैं, C isolated है

# Election starts
building_a_rep.start_election()
# Term = 1, Candidate = A

# A gets vote from B (majority = 2 out of 3)
# A becomes chairman

# C tries to start election but can't reach majority
building_c_rep.start_election()
# Term = 1, Candidate = C
# C can't get majority (only 1 vote from itself)

# Decision making
decision = "Approve painting contract for ₹2 lakhs"
success = building_a_rep.make_society_decision(decision)
# A replicates to B, gets majority (2/3), commits decision
```

## Future और Modern Adaptations

### Joint Consensus (Multi-Raft)

Modern systems often use multiple Raft groups:

```go
type MultiRaftSystem struct {
    raftGroups map[string]*raft.Raft
    router     *RequestRouter
}

func (mrs *MultiRaftSystem) routeRequest(key string, request interface{}) {
    // Determine which Raft group handles this key
    groupID := mrs.router.getGroupForKey(key)
    raftGroup := mrs.raftGroups[groupID]
    
    // Propose to appropriate group
    data, _ := json.Marshal(request)
    raftGroup.Apply(data, time.Second)
}
```

### Raft in Cloud Native

#### Kubernetes Operators with Raft

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: raft-consensus-cluster
spec:
  serviceName: raft-cluster
  replicas: 3
  selector:
    matchLabels:
      app: raft-node
  template:
    metadata:
      labels:
        app: raft-node
    spec:
      containers:
      - name: raft-node
        image: raft-consensus:latest
        env:
        - name: CLUSTER_SIZE
          value: "3"
        - name: NODE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        ports:
        - containerPort: 8080
          name: raft-port
        - containerPort: 8090
          name: client-port
```

## Key Takeaways

### Society Election Lessons

1. **Simple Leadership**: एक time में एक ही chairman/leader
2. **Majority Rule**: > 50% building representatives की agreement
3. **Sequential Decisions**: सभी decisions का proper order
4. **Fault Tolerance**: कुछ reps offline हों तो भी system काम करे

### Technical Mastery Points

1. **Leader-Based Consensus**: Raft में हमेशा leader होता है
2. **Sequential Log**: कोई gaps नहीं होते log में
3. **Randomized Timeouts**: Split votes को prevent करते हैं
4. **Strong Consistency**: सभी nodes पर same order में operations apply होती हैं

### Production Guidelines

1. **Cluster Size**: Usually 3, 5, या 7 nodes (odd numbers)
2. **Heartbeat Intervals**: 50-100ms for low latency
3. **Election Timeouts**: 150-300ms randomized
4. **Log Compaction**: Regular snapshots for performance

### When to Use Raft

**Perfect For**:
- Configuration management (etcd, Consul)
- Metadata storage (CockroachDB ranges)
- Service discovery
- Distributed locking
- Any system needing simple, understandable consensus

**Avoid For**:
- Single machine applications
- Systems with very high write throughput requirements
- Applications where eventual consistency is sufficient

Raft ने distributed systems में consensus को democratize किया है। Paxos की complexity के comparison में, Raft को समझना और implement करना much easier है। इसलिए modern distributed systems (Kubernetes, Docker Swarm, CockroachDB) में Raft का wide adoption हुआ है।

अगली episode में हम Byzantine Fault Tolerance के बारे में बात करेंगे - जहां system में कुछ nodes malicious या arbitrary behavior कर सकते हैं।