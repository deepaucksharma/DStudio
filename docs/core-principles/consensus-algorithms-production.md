# Consensus Algorithms in Production: The Complete Implementation Guide

## Executive Summary

Consensus algorithms are the heart of distributed systems, enabling multiple nodes to agree on a single value despite failures. This guide provides production-ready implementations of major consensus algorithms with real-world optimizations, deployment strategies, and operational guidance.

---

## Part 1: Raft - The Understandable Consensus

### Complete Production Raft Implementation

```java
@Component
@Slf4j
public class RaftNode {
    
    // Node states
    private enum State {
        FOLLOWER, CANDIDATE, LEADER
    }
    
    private State state = State.FOLLOWER;
    private int currentTerm = 0;
    private String votedFor = null;
    private List<LogEntry> log = new ArrayList<>();
    private int commitIndex = 0;
    private int lastApplied = 0;
    
    // Leader state
    private Map<String, Integer> nextIndex = new ConcurrentHashMap<>();
    private Map<String, Integer> matchIndex = new ConcurrentHashMap<>();
    
    // Cluster configuration
    private final String nodeId;
    private final List<String> peers;
    private final RaftRPC rpc;
    private final StateMachine stateMachine;
    
    // Timing
    private long lastHeartbeat = System.currentTimeMillis();
    private long electionTimeout = generateElectionTimeout();
    
    @Value("${raft.heartbeat.interval:50}")
    private long heartbeatInterval;
    
    @Value("${raft.election.timeout.min:150}")
    private long electionTimeoutMin;
    
    @Value("${raft.election.timeout.max:300}")
    private long electionTimeoutMax;
    
    /**
     * Main Raft loop - handles state transitions
     */
    @Scheduled(fixedDelay = 10)
    public void raftLoop() {
        switch (state) {
            case FOLLOWER:
                handleFollower();
                break;
            case CANDIDATE:
                handleCandidate();
                break;
            case LEADER:
                handleLeader();
                break;
        }
    }
    
    /**
     * Follower logic - timeout triggers election
     */
    private void handleFollower() {
        if (System.currentTimeMillis() - lastHeartbeat > electionTimeout) {
            log.info("Election timeout, becoming candidate");
            becomeCandidate();
        }
    }
    
    /**
     * Candidate logic - request votes
     */
    private void handleCandidate() {
        state = State.CANDIDATE;
        currentTerm++;
        votedFor = nodeId;
        electionTimeout = generateElectionTimeout();
        
        // Vote for self
        int votes = 1;
        int votesNeeded = (peers.size() + 1) / 2 + 1;
        
        // Request votes from all peers
        List<CompletableFuture<VoteResponse>> voteFutures = new ArrayList<>();
        
        for (String peer : peers) {
            VoteRequest request = VoteRequest.builder()
                .term(currentTerm)
                .candidateId(nodeId)
                .lastLogIndex(log.size() - 1)
                .lastLogTerm(log.isEmpty() ? 0 : 
                    log.get(log.size() - 1).getTerm())
                .build();
            
            voteFutures.add(rpc.requestVote(peer, request));
        }
        
        // Count votes with timeout
        for (CompletableFuture<VoteResponse> future : voteFutures) {
            try {
                VoteResponse response = future.get(
                    electionTimeout / 2, TimeUnit.MILLISECONDS);
                
                if (response.getTerm() > currentTerm) {
                    // Discovered higher term
                    currentTerm = response.getTerm();
                    becomeFollower();
                    return;
                }
                
                if (response.isVoteGranted()) {
                    votes++;
                    if (votes >= votesNeeded) {
                        becomeLeader();
                        return;
                    }
                }
            } catch (TimeoutException e) {
                // Vote timeout, continue
            } catch (Exception e) {
                log.error("Error requesting vote", e);
            }
        }
        
        // Split vote or timeout - remain candidate
        if (System.currentTimeMillis() - lastHeartbeat > electionTimeout) {
            // Start new election
            becomeCandidate();
        }
    }
    
    /**
     * Leader logic - send heartbeats and replicate log
     */
    private void handleLeader() {
        // Send heartbeats
        long now = System.currentTimeMillis();
        if (now - lastHeartbeat > heartbeatInterval) {
            sendHeartbeats();
            lastHeartbeat = now;
        }
        
        // Update commit index
        updateCommitIndex();
        
        // Apply committed entries
        applyCommittedEntries();
    }
    
    /**
     * Send AppendEntries to all followers
     */
    private void sendHeartbeats() {
        for (String peer : peers) {
            int prevLogIndex = nextIndex.getOrDefault(peer, log.size()) - 1;
            int prevLogTerm = prevLogIndex >= 0 ? 
                log.get(prevLogIndex).getTerm() : 0;
            
            // Get entries to send
            List<LogEntry> entries = new ArrayList<>();
            if (prevLogIndex + 1 < log.size()) {
                entries = log.subList(prevLogIndex + 1, log.size());
            }
            
            AppendEntriesRequest request = AppendEntriesRequest.builder()
                .term(currentTerm)
                .leaderId(nodeId)
                .prevLogIndex(prevLogIndex)
                .prevLogTerm(prevLogTerm)
                .entries(entries)
                .leaderCommit(commitIndex)
                .build();
            
            rpc.appendEntries(peer, request).thenAccept(response -> {
                if (response.getTerm() > currentTerm) {
                    currentTerm = response.getTerm();
                    becomeFollower();
                    return;
                }
                
                if (response.isSuccess()) {
                    // Update indices
                    nextIndex.put(peer, prevLogIndex + entries.size() + 1);
                    matchIndex.put(peer, prevLogIndex + entries.size());
                } else {
                    // Decrement nextIndex and retry
                    nextIndex.put(peer, Math.max(1, 
                        nextIndex.getOrDefault(peer, 1) - 1));
                }
            });
        }
    }
    
    /**
     * Client command handling
     */
    public CompletableFuture<CommandResult> submitCommand(Command command) {
        if (state != State.LEADER) {
            return CompletableFuture.completedFuture(
                CommandResult.notLeader(getCurrentLeader()));
        }
        
        // Append to log
        LogEntry entry = LogEntry.builder()
            .term(currentTerm)
            .command(command)
            .clientId(command.getClientId())
            .sequenceNum(command.getSequenceNum())
            .build();
        
        log.add(entry);
        
        // Return future that completes when committed
        CompletableFuture<CommandResult> future = new CompletableFuture<>();
        
        // Track pending command
        pendingCommands.put(log.size() - 1, future);
        
        // Trigger immediate replication
        sendHeartbeats();
        
        return future;
    }
    
    /**
     * Update commit index based on majority replication
     */
    private void updateCommitIndex() {
        for (int n = log.size() - 1; n > commitIndex; n--) {
            if (log.get(n).getTerm() != currentTerm) {
                continue;
            }
            
            int replicatedCount = 1; // Leader
            for (int matchIdx : matchIndex.values()) {
                if (matchIdx >= n) {
                    replicatedCount++;
                }
            }
            
            if (replicatedCount > (peers.size() + 1) / 2) {
                commitIndex = n;
                break;
            }
        }
    }
    
    /**
     * Apply committed entries to state machine
     */
    private void applyCommittedEntries() {
        while (lastApplied < commitIndex) {
            lastApplied++;
            LogEntry entry = log.get(lastApplied);
            
            // Apply to state machine
            CommandResult result = stateMachine.apply(entry.getCommand());
            
            // Complete pending future if leader
            if (state == State.LEADER) {
                CompletableFuture<CommandResult> future = 
                    pendingCommands.remove(lastApplied);
                if (future != null) {
                    future.complete(result);
                }
            }
        }
    }
    
    /**
     * Persistent state management
     */
    @Component
    public class RaftPersistentState {
        
        private final Path stateFile;
        
        public RaftPersistentState(@Value("${raft.state.dir}") String dir) {
            this.stateFile = Paths.get(dir, nodeId + ".state");
        }
        
        @PostConstruct
        public void loadState() {
            if (Files.exists(stateFile)) {
                try {
                    RaftState saved = objectMapper.readValue(
                        stateFile.toFile(), RaftState.class);
                    currentTerm = saved.getCurrentTerm();
                    votedFor = saved.getVotedFor();
                    log = saved.getLog();
                    log.info("Loaded persistent state: term={}, votedFor={}, log_size={}",
                        currentTerm, votedFor, log.size());
                } catch (IOException e) {
                    log.error("Failed to load state", e);
                }
            }
        }
        
        public void saveState() {
            try {
                RaftState state = RaftState.builder()
                    .currentTerm(currentTerm)
                    .votedFor(votedFor)
                    .log(log)
                    .build();
                
                // Atomic write with rename
                Path temp = stateFile.resolveSibling(stateFile.getFileName() + ".tmp");
                objectMapper.writeValue(temp.toFile(), state);
                Files.move(temp, stateFile, StandardCopyOption.ATOMIC_MOVE);
                
            } catch (IOException e) {
                log.error("Failed to save state", e);
            }
        }
    }
}
```

### Kubernetes StatefulSet for Raft Cluster

```yaml
apiVersion: v1
kind: Service
metadata:
  name: raft-cluster
spec:
  clusterIP: None  # Headless service
  selector:
    app: raft
  ports:
  - name: client
    port: 8080
  - name: peer
    port: 8081
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: raft
spec:
  serviceName: raft-cluster
  replicas: 5
  podManagementPolicy: Parallel
  selector:
    matchLabels:
      app: raft
  template:
    metadata:
      labels:
        app: raft
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchLabels:
                app: raft
            topologyKey: kubernetes.io/hostname
      containers:
      - name: raft-node
        image: raft:production
        env:
        - name: NODE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: PEERS
          value: "raft-0,raft-1,raft-2,raft-3,raft-4"
        - name: HEARTBEAT_INTERVAL_MS
          value: "50"
        - name: ELECTION_TIMEOUT_MIN_MS
          value: "150"
        - name: ELECTION_TIMEOUT_MAX_MS
          value: "300"
        ports:
        - containerPort: 8080
          name: client
        - containerPort: 8081
          name: peer
        volumeMounts:
        - name: data
          mountPath: /var/raft
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

---

## Part 2: Paxos - The Original Consensus

### Multi-Paxos Production Implementation

```java
@Service
@Slf4j
public class MultiPaxosNode {
    
    // Paxos roles
    private final Proposer proposer;
    private final Acceptor acceptor;
    private final Learner learner;
    
    // State
    private long currentRound = 0;
    private Map<Long, PaxosInstance> instances = new ConcurrentHashMap<>();
    
    /**
     * Proposer - initiates consensus
     */
    @Component
    public class Proposer {
        
        private final String nodeId;
        private final List<String> acceptors;
        
        public CompletableFuture<Value> propose(long instanceId, Value value) {
            PaxosInstance instance = instances.computeIfAbsent(
                instanceId, k -> new PaxosInstance());
            
            // Phase 1a: Prepare
            long proposalNumber = generateProposalNumber();
            
            PrepareRequest prepare = PrepareRequest.builder()
                .instanceId(instanceId)
                .proposalNumber(proposalNumber)
                .build();
            
            List<CompletableFuture<PrepareResponse>> prepareFutures = 
                acceptors.stream()
                    .map(acceptor -> rpc.prepare(acceptor, prepare))
                    .collect(Collectors.toList());
            
            // Wait for majority
            return CompletableFuture.allOf(
                prepareFutures.toArray(new CompletableFuture[0]))
                .thenCompose(v -> {
                    List<PrepareResponse> responses = prepareFutures.stream()
                        .map(CompletableFuture::join)
                        .filter(r -> r != null && r.isPromised())
                        .collect(Collectors.toList());
                    
                    if (responses.size() <= acceptors.size() / 2) {
                        // No majority, retry with higher proposal
                        return propose(instanceId, value);
                    }
                    
                    // Phase 2a: Accept
                    Value proposalValue = selectValue(responses, value);
                    
                    AcceptRequest accept = AcceptRequest.builder()
                        .instanceId(instanceId)
                        .proposalNumber(proposalNumber)
                        .value(proposalValue)
                        .build();
                    
                    List<CompletableFuture<AcceptResponse>> acceptFutures = 
                        acceptors.stream()
                            .map(acceptor -> rpc.accept(acceptor, accept))
                            .collect(Collectors.toList());
                    
                    return CompletableFuture.allOf(
                        acceptFutures.toArray(new CompletableFuture[0]))
                        .thenApply(a -> {
                            long accepted = acceptFutures.stream()
                                .map(CompletableFuture::join)
                                .filter(r -> r != null && r.isAccepted())
                                .count();
                            
                            if (accepted > acceptors.size() / 2) {
                                // Value chosen!
                                instance.setChosen(proposalValue);
                                return proposalValue;
                            }
                            
                            // Retry
                            throw new RetryException("Accept failed");
                        });
                });
        }
        
        private Value selectValue(List<PrepareResponse> responses, Value proposed) {
            // Select highest numbered accepted value, or proposed if none
            return responses.stream()
                .filter(r -> r.getAcceptedValue() != null)
                .max(Comparator.comparing(PrepareResponse::getAcceptedProposal))
                .map(PrepareResponse::getAcceptedValue)
                .orElse(proposed);
        }
        
        private long generateProposalNumber() {
            // Unique proposal: round.nodeId
            return (++currentRound << 16) | nodeId.hashCode() & 0xFFFF;
        }
    }
    
    /**
     * Acceptor - votes on proposals
     */
    @Component
    public class Acceptor {
        
        // Persistent state per instance
        private Map<Long, AcceptorState> states = new ConcurrentHashMap<>();
        
        @Transactional
        public PrepareResponse handlePrepare(PrepareRequest request) {
            AcceptorState state = states.computeIfAbsent(
                request.getInstanceId(), k -> new AcceptorState());
            
            synchronized (state) {
                if (request.getProposalNumber() > state.getPromisedProposal()) {
                    // Promise not to accept lower proposals
                    state.setPromisedProposal(request.getProposalNumber());
                    persistState(request.getInstanceId(), state);
                    
                    return PrepareResponse.builder()
                        .promised(true)
                        .acceptedProposal(state.getAcceptedProposal())
                        .acceptedValue(state.getAcceptedValue())
                        .build();
                }
                
                return PrepareResponse.builder()
                    .promised(false)
                    .build();
            }
        }
        
        @Transactional
        public AcceptResponse handleAccept(AcceptRequest request) {
            AcceptorState state = states.computeIfAbsent(
                request.getInstanceId(), k -> new AcceptorState());
            
            synchronized (state) {
                if (request.getProposalNumber() >= state.getPromisedProposal()) {
                    // Accept the proposal
                    state.setAcceptedProposal(request.getProposalNumber());
                    state.setAcceptedValue(request.getValue());
                    persistState(request.getInstanceId(), state);
                    
                    // Notify learners
                    notifyLearners(request.getInstanceId(), request.getValue());
                    
                    return AcceptResponse.builder()
                        .accepted(true)
                        .build();
                }
                
                return AcceptResponse.builder()
                    .accepted(false)
                    .build();
            }
        }
        
        private void persistState(long instanceId, AcceptorState state) {
            // Write to stable storage
            storage.write("paxos/" + instanceId, state);
        }
    }
    
    /**
     * Learner - learns chosen values
     */
    @Component
    public class Learner {
        
        private Map<Long, Map<String, Value>> acceptedValues = 
            new ConcurrentHashMap<>();
        private Map<Long, Value> chosenValues = new ConcurrentHashMap<>();
        
        public void handleAccepted(long instanceId, String acceptor, Value value) {
            Map<String, Value> accepts = acceptedValues.computeIfAbsent(
                instanceId, k -> new ConcurrentHashMap<>());
            
            accepts.put(acceptor, value);
            
            // Check if value is chosen (majority accepted)
            Map<Value, Long> counts = accepts.values().stream()
                .collect(Collectors.groupingBy(
                    Function.identity(), Collectors.counting()));
            
            counts.forEach((val, count) -> {
                if (count > acceptors.size() / 2) {
                    // Value chosen!
                    chosenValues.put(instanceId, val);
                    applyValue(instanceId, val);
                }
            });
        }
        
        private void applyValue(long instanceId, Value value) {
            // Apply to state machine in order
            while (lastApplied + 1 <= instanceId) {
                Value toApply = chosenValues.get(++lastApplied);
                if (toApply != null) {
                    stateMachine.apply(toApply);
                } else {
                    // Gap in sequence, wait
                    lastApplied--;
                    break;
                }
            }
        }
    }
}
```

---

## Part 3: Byzantine Fault Tolerant Consensus (PBFT)

### Production PBFT Implementation

```java
@Service
@Slf4j
public class PBFTNode {
    
    private final String nodeId;
    private final int nodeIndex;
    private final int totalNodes;
    private final int faultyNodes; // f
    
    private int viewNumber = 0;
    private long sequenceNumber = 0;
    
    // Message logs
    private Map<Long, ClientRequest> clientRequests = new ConcurrentHashMap<>();
    private Map<Long, Set<PrepareMessage>> prepareLog = new ConcurrentHashMap<>();
    private Map<Long, Set<CommitMessage>> commitLog = new ConcurrentHashMap<>();
    
    @Value("${pbft.checkpoint.interval:100}")
    private int checkpointInterval;
    
    /**
     * Client request handling (Primary only)
     */
    public CompletableFuture<Reply> handleClientRequest(ClientRequest request) {
        if (!isPrimary()) {
            // Forward to primary
            return forwardToPrimary(request);
        }
        
        // Verify client signature
        if (!verifyClientSignature(request)) {
            return CompletableFuture.completedFuture(
                Reply.error("Invalid signature"));
        }
        
        // Check for duplicate
        if (isDuplicate(request)) {
            return CompletableFuture.completedFuture(
                getCachedReply(request));
        }
        
        // Assign sequence number
        long seq = ++sequenceNumber;
        
        // Pre-prepare phase
        PrePrepareMessage prePrepare = PrePrepareMessage.builder()
            .viewNumber(viewNumber)
            .sequenceNumber(seq)
            .digest(hash(request))
            .request(request)
            .signature(sign(hash(request)))
            .build();
        
        // Store and broadcast
        clientRequests.put(seq, request);
        broadcast(prePrepare);
        
        // Also prepare as primary
        handlePrePrepare(prePrepare);
        
        // Return future that completes when executed
        return trackExecution(seq, request);
    }
    
    /**
     * Pre-prepare phase (Backup nodes)
     */
    public void handlePrePrepare(PrePrepareMessage message) {
        // Verify primary signature
        if (!verifySignature(getPrimary(), message)) {
            log.warn("Invalid pre-prepare signature");
            return;
        }
        
        // Check view and sequence
        if (message.getViewNumber() != viewNumber) {
            // Trigger view change if needed
            if (message.getViewNumber() > viewNumber) {
                initiateViewChange(message.getViewNumber());
            }
            return;
        }
        
        // Verify request
        ClientRequest request = message.getRequest();
        if (!hash(request).equals(message.getDigest())) {
            log.warn("Pre-prepare digest mismatch");
            return;
        }
        
        // Store request
        clientRequests.put(message.getSequenceNumber(), request);
        
        // Prepare phase
        PrepareMessage prepare = PrepareMessage.builder()
            .viewNumber(viewNumber)
            .sequenceNumber(message.getSequenceNumber())
            .digest(message.getDigest())
            .nodeId(nodeId)
            .signature(sign(message.getDigest()))
            .build();
        
        broadcast(prepare);
        handlePrepare(prepare); // Count own prepare
    }
    
    /**
     * Prepare phase - collect 2f prepares
     */
    public void handlePrepare(PrepareMessage message) {
        // Verify signature
        if (!verifySignature(message.getNodeId(), message)) {
            return;
        }
        
        // Add to prepare log
        Set<PrepareMessage> prepares = prepareLog.computeIfAbsent(
            message.getSequenceNumber(), k -> ConcurrentHashMap.newKeySet());
        
        prepares.add(message);
        
        // Check if prepared (2f + 1 prepares with same digest)
        Map<String, Long> digestCounts = prepares.stream()
            .collect(Collectors.groupingBy(
                PrepareMessage::getDigest, Collectors.counting()));
        
        digestCounts.forEach((digest, count) -> {
            if (count >= 2 * faultyNodes + 1) {
                // Prepared! Move to commit phase
                commitPhase(message.getSequenceNumber(), digest);
            }
        });
    }
    
    /**
     * Commit phase - collect 2f + 1 commits
     */
    private void commitPhase(long sequenceNumber, String digest) {
        CommitMessage commit = CommitMessage.builder()
            .viewNumber(viewNumber)
            .sequenceNumber(sequenceNumber)
            .digest(digest)
            .nodeId(nodeId)
            .signature(sign(digest))
            .build();
        
        broadcast(commit);
        handleCommit(commit);
    }
    
    public void handleCommit(CommitMessage message) {
        // Verify signature
        if (!verifySignature(message.getNodeId(), message)) {
            return;
        }
        
        // Add to commit log
        Set<CommitMessage> commits = commitLog.computeIfAbsent(
            message.getSequenceNumber(), k -> ConcurrentHashMap.newKeySet());
        
        commits.add(message);
        
        // Check if committed (2f + 1 commits)
        if (commits.size() >= 2 * faultyNodes + 1) {
            // Execute request
            executeRequest(message.getSequenceNumber());
        }
    }
    
    /**
     * Execute committed requests in order
     */
    private void executeRequest(long sequenceNumber) {
        // Execute in sequence order
        while (lastExecuted + 1 <= sequenceNumber) {
            long toExecute = ++lastExecuted;
            ClientRequest request = clientRequests.get(toExecute);
            
            if (request != null) {
                // Execute on state machine
                Reply reply = stateMachine.execute(request);
                
                // Send reply to client
                sendReplyToClient(request.getClientId(), reply);
                
                // Complete tracking future
                completeExecution(toExecute, reply);
                
                // Checkpoint periodically
                if (toExecute % checkpointInterval == 0) {
                    createCheckpoint(toExecute);
                }
            } else {
                // Gap in sequence, wait
                lastExecuted--;
                break;
            }
        }
    }
    
    /**
     * View change protocol for fault recovery
     */
    private void initiateViewChange(int newView) {
        log.info("Initiating view change from {} to {}", viewNumber, newView);
        
        ViewChangeMessage viewChange = ViewChangeMessage.builder()
            .newViewNumber(newView)
            .lastStableCheckpoint(lastCheckpoint)
            .checkpointProof(getCheckpointProof())
            .preparedMessages(getPreparedMessages())
            .nodeId(nodeId)
            .signature(sign(newView))
            .build();
        
        broadcast(viewChange);
        
        // Collect view change messages
        viewChangeCollector.add(viewChange);
        
        // Check if new view can start
        if (viewChangeCollector.size() >= 2 * faultyNodes + 1) {
            if (isNewPrimary(newView)) {
                startNewView(newView);
            }
        }
    }
    
    /**
     * Checkpoint for garbage collection
     */
    private void createCheckpoint(long sequenceNumber) {
        // Create state snapshot
        byte[] stateDigest = stateMachine.getStateDigest();
        
        CheckpointMessage checkpoint = CheckpointMessage.builder()
            .sequenceNumber(sequenceNumber)
            .stateDigest(stateDigest)
            .nodeId(nodeId)
            .signature(sign(stateDigest))
            .build();
        
        broadcast(checkpoint);
        
        // Collect checkpoint confirmations
        checkpointCollector.add(checkpoint);
        
        if (checkpointCollector.countMatching(sequenceNumber, stateDigest) 
                >= 2 * faultyNodes + 1) {
            // Stable checkpoint reached
            stableCheckpoint = sequenceNumber;
            
            // Garbage collect old messages
            garbageCollect(sequenceNumber);
        }
    }
}
```

### Kubernetes Deployment for PBFT

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pbft-config
data:
  pbft.yaml: |
    cluster:
      total_nodes: 4     # 3f + 1 for f = 1
      fault_tolerance: 1 # Byzantine fault tolerance
      
    consensus:
      view_change_timeout: 10s
      checkpoint_interval: 100
      max_batch_size: 10
      
    crypto:
      algorithm: Ed25519
      verify_client_signatures: true
      
    network:
      message_buffer_size: 10000
      max_message_size: 1MB
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: pbft-cluster
spec:
  serviceName: pbft
  replicas: 4  # 3f + 1 for f = 1
  selector:
    matchLabels:
      app: pbft
  template:
    spec:
      containers:
      - name: pbft-node
        image: pbft:production
        env:
        - name: NODE_INDEX
          valueFrom:
            fieldRef:
              fieldPath: metadata.annotations['spec.pod-index']
        - name: TOTAL_NODES
          value: "4"
        - name: FAULT_TOLERANCE
          value: "1"
        volumeMounts:
        - name: config
          mountPath: /config
        - name: keys
          mountPath: /keys
          readOnly: true
        - name: data
          mountPath: /data
      volumes:
      - name: config
        configMap:
          name: pbft-config
      - name: keys
        secret:
          secretName: pbft-keys
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

---

## Part 4: Consensus Algorithm Comparison and Selection

### When to Use Which Algorithm

```java
@Component
public class ConsensusAlgorithmSelector {
    
    /**
     * Select appropriate consensus algorithm based on requirements
     */
    public ConsensusAlgorithm selectAlgorithm(SystemRequirements requirements) {
        
        // Byzantine fault tolerance needed?
        if (requirements.hasByzantineNodes()) {
            if (requirements.getNodeCount() <= 10) {
                return ConsensusAlgorithm.PBFT; // Good for small clusters
            } else {
                return ConsensusAlgorithm.TENDERMINT; // Scales better
            }
        }
        
        // Need simple, understandable consensus?
        if (requirements.prioritizeSimplicity()) {
            return ConsensusAlgorithm.RAFT;
        }
        
        // Need maximum throughput?
        if (requirements.prioritizeThroughput()) {
            return ConsensusAlgorithm.MULTI_PAXOS;
        }
        
        // Need geo-distributed consensus?
        if (requirements.isGeoDistributed()) {
            return ConsensusAlgorithm.EPAXOS; // Egalitarian Paxos
        }
        
        // Default to Raft for most use cases
        return ConsensusAlgorithm.RAFT;
    }
    
    /**
     * Performance characteristics comparison
     */
    public PerformanceProfile getPerformanceProfile(ConsensusAlgorithm algorithm) {
        switch (algorithm) {
            case RAFT:
                return PerformanceProfile.builder()
                    .latency("2 RTT in common case")
                    .throughput("10K-50K ops/sec")
                    .faultTolerance("f failures with 2f+1 nodes")
                    .complexity("Simple")
                    .reconfiguration("Built-in membership changes")
                    .build();
                    
            case MULTI_PAXOS:
                return PerformanceProfile.builder()
                    .latency("2 RTT when stable leader")
                    .throughput("50K-100K ops/sec")
                    .faultTolerance("f failures with 2f+1 nodes")
                    .complexity("Complex")
                    .reconfiguration("Requires external coordination")
                    .build();
                    
            case PBFT:
                return PerformanceProfile.builder()
                    .latency("3 phases minimum")
                    .throughput("5K-20K ops/sec")
                    .faultTolerance("f Byzantine with 3f+1 nodes")
                    .complexity("Very complex")
                    .reconfiguration("View changes built-in")
                    .build();
                    
            default:
                throw new IllegalArgumentException("Unknown algorithm");
        }
    }
}
```

### Monitoring Consensus Performance

```java
@Component
public class ConsensusMonitoring {
    
    private final MeterRegistry metrics;
    
    @EventListener
    public void onConsensusEvent(ConsensusEvent event) {
        // Track consensus latency
        metrics.timer("consensus.latency",
            "algorithm", event.getAlgorithm(),
            "phase", event.getPhase())
            .record(event.getDuration());
        
        // Track success rate
        metrics.counter("consensus.attempts",
            "algorithm", event.getAlgorithm(),
            "result", event.isSuccess() ? "success" : "failure")
            .increment();
        
        // Track leader changes
        if (event.getType() == EventType.LEADER_CHANGE) {
            metrics.counter("consensus.leader.changes",
                "algorithm", event.getAlgorithm())
                .increment();
        }
    }
    
    /**
     * Health checks for consensus
     */
    @Component
    public class ConsensusHealthIndicator implements HealthIndicator {
        
        @Override
        public Health health() {
            ConsensusStatus status = getConsensusStatus();
            
            Health.Builder builder = status.hasQuorum() ? 
                Health.up() : Health.down();
            
            return builder
                .withDetail("algorithm", status.getAlgorithm())
                .withDetail("leader", status.getLeader())
                .withDetail("term", status.getTerm())
                .withDetail("quorum", status.getQuorumSize())
                .withDetail("committed_index", status.getCommittedIndex())
                .withDetail("applied_index", status.getAppliedIndex())
                .build();
        }
    }
}
```

### Testing Consensus Algorithms

```java
@SpringBootTest
public class ConsensusIntegrationTest {
    
    @Test
    public void testRaftLeaderElection() {
        // Start 5-node cluster
        List<RaftNode> nodes = startRaftCluster(5);
        
        // Wait for leader election
        await().atMost(5, TimeUnit.SECONDS)
            .until(() -> getLeader(nodes) != null);
        
        RaftNode leader = getLeader(nodes);
        assertNotNull(leader);
        
        // Kill leader
        stopNode(leader);
        
        // New leader should be elected
        await().atMost(5, TimeUnit.SECONDS)
            .until(() -> {
                RaftNode newLeader = getLeader(nodes);
                return newLeader != null && !newLeader.equals(leader);
            });
    }
    
    @Test
    public void testByzantineFaultTolerance() {
        // Start 4-node PBFT cluster (tolerates 1 Byzantine)
        List<PBFTNode> nodes = startPBFTCluster(4);
        
        // Make one node Byzantine
        PBFTNode byzantine = nodes.get(0);
        makeByzantine(byzantine);
        
        // Submit request
        ClientRequest request = ClientRequest.builder()
            .operation("SET x 10")
            .clientId("test-client")
            .build();
        
        CompletableFuture<Reply> future = nodes.get(1)
            .handleClientRequest(request);
        
        // Should still reach consensus
        Reply reply = future.get(10, TimeUnit.SECONDS);
        assertTrue(reply.isSuccess());
        
        // Verify all honest nodes have same state
        List<PBFTNode> honest = nodes.subList(1, 4);
        String state = honest.get(0).getState();
        
        for (PBFTNode node : honest) {
            assertEquals(state, node.getState());
        }
    }
    
    @Test
    public void testNetworkPartition() {
        // Test Raft behavior during partition
        List<RaftNode> nodes = startRaftCluster(5);
        
        // Create partition: [n0, n1] | [n2, n3, n4]
        createPartition(
            Arrays.asList(nodes.get(0), nodes.get(1)),
            Arrays.asList(nodes.get(2), nodes.get(3), nodes.get(4))
        );
        
        // Majority partition should elect leader
        await().atMost(5, TimeUnit.SECONDS)
            .until(() -> {
                List<RaftNode> majority = nodes.subList(2, 5);
                return getLeader(majority) != null;
            });
        
        // Minority partition should have no leader
        List<RaftNode> minority = nodes.subList(0, 2);
        assertNull(getLeader(minority));
        
        // Heal partition
        healPartition();
        
        // Should converge to single leader
        await().atMost(5, TimeUnit.SECONDS)
            .until(() -> {
                Set<RaftNode> leaders = nodes.stream()
                    .filter(RaftNode::isLeader)
                    .collect(Collectors.toSet());
                return leaders.size() == 1;
            });
    }
}
```

---

## Part 5: Production Operational Procedures

### Consensus Cluster Operations

```bash
#!/bin/bash
# Consensus cluster management script

# Add new node to Raft cluster
add_raft_node() {
    local NEW_NODE=$1
    local LEADER=$(get_leader)
    
    echo "Adding node $NEW_NODE to cluster via leader $LEADER"
    
    # Trigger configuration change
    curl -X POST "http://$LEADER:8080/admin/add-node" \
        -H "Content-Type: application/json" \
        -d "{\"nodeId\": \"$NEW_NODE\", \"address\": \"$NEW_NODE:8081\"}"
    
    # Wait for node to catch up
    wait_for_sync $NEW_NODE
}

# Remove node from cluster
remove_raft_node() {
    local NODE=$1
    local LEADER=$(get_leader)
    
    echo "Removing node $NODE from cluster"
    
    # Trigger configuration change
    curl -X POST "http://$LEADER:8080/admin/remove-node" \
        -H "Content-Type: application/json" \
        -d "{\"nodeId\": \"$NODE\"}"
    
    # Scale down StatefulSet
    kubectl scale statefulset raft --replicas=$(($(get_replica_count) - 1))
}

# Rolling upgrade
rolling_upgrade() {
    local NEW_VERSION=$1
    
    echo "Starting rolling upgrade to version $NEW_VERSION"
    
    # Update StatefulSet image
    kubectl set image statefulset/raft raft-node=raft:$NEW_VERSION
    
    # Wait for rolling update to complete
    kubectl rollout status statefulset/raft
    
    # Verify cluster health
    check_cluster_health
}

# Backup consensus state
backup_consensus_state() {
    local BACKUP_DIR="/backups/$(date +%Y%m%d-%H%M%S)"
    
    for NODE in $(get_all_nodes); do
        echo "Backing up $NODE"
        kubectl exec $NODE -- tar czf - /var/raft | \
            aws s3 cp - "s3://backups/$BACKUP_DIR/$NODE.tar.gz"
    done
    
    echo "Backup completed to $BACKUP_DIR"
}
```

### Emergency Recovery Procedures

```java
@Component
@Slf4j
public class ConsensusEmergencyRecovery {
    
    /**
     * Recover from split brain
     */
    public void recoverFromSplitBrain() {
        log.error("SPLIT BRAIN DETECTED - Starting recovery");
        
        // 1. Identify all leaders
        List<String> leaders = identifyAllLeaders();
        
        if (leaders.size() <= 1) {
            log.info("No split brain detected");
            return;
        }
        
        // 2. Determine legitimate leader (highest term + most logs)
        String legitimateLeader = determineLegitimateLeader(leaders);
        
        // 3. Force other leaders to step down
        for (String leader : leaders) {
            if (!leader.equals(legitimateLeader)) {
                forceStepDown(leader);
            }
        }
        
        // 4. Trigger new election if needed
        if (!verifyLeader(legitimateLeader)) {
            triggerNewElection();
        }
        
        // 5. Verify cluster health
        verifyClusterHealth();
    }
    
    /**
     * Recover from data corruption
     */
    public void recoverFromCorruption(String corruptedNode) {
        log.error("Data corruption detected on node: {}", corruptedNode);
        
        // 1. Isolate corrupted node
        isolateNode(corruptedNode);
        
        // 2. Wipe corrupted data
        wipeNodeData(corruptedNode);
        
        // 3. Restore from leader
        String leader = getLeader();
        
        // 4. Stream snapshot from leader
        streamSnapshot(leader, corruptedNode);
        
        // 5. Rejoin cluster
        rejoinCluster(corruptedNode);
        
        // 6. Verify replication
        verifyReplication(corruptedNode);
    }
    
    /**
     * Recover from total cluster failure
     */
    public void recoverFromTotalFailure() {
        log.error("TOTAL CLUSTER FAILURE - Starting disaster recovery");
        
        // 1. Find most recent backup
        Backup latestBackup = findLatestBackup();
        
        // 2. Restore to single node
        String bootstrapNode = selectBootstrapNode();
        restoreBackup(bootstrapNode, latestBackup);
        
        // 3. Force single-node cluster
        forceSingleNodeMode(bootstrapNode);
        
        // 4. Add other nodes one by one
        for (String node : getOtherNodes(bootstrapNode)) {
            wipeNodeData(node);
            addNodeToCluster(node);
            waitForSync(node);
        }
        
        // 5. Verify cluster integrity
        verifyClusterIntegrity();
        
        // 6. Resume normal operations
        resumeOperations();
    }
}
```

---

## Summary: Consensus in Production

### Key Takeaways

1. **Raft for Simplicity**: Use when understandability and operational simplicity are priorities
2. **Paxos for Performance**: Use when you need maximum throughput and can handle complexity
3. **PBFT for Byzantine**: Use when nodes might be malicious, not just crash-faulty
4. **Monitor Everything**: Consensus performance directly impacts system availability
5. **Test Failures**: Regularly test leader election, network partitions, and node failures
6. **Plan Recovery**: Have procedures for split-brain, corruption, and total failure

### Production Checklist

- [ ] Choose appropriate algorithm based on requirements
- [ ] Deploy with proper anti-affinity and failure domains
- [ ] Implement comprehensive monitoring and alerting
- [ ] Test all failure scenarios in staging
- [ ] Document operational procedures
- [ ] Train team on consensus behavior and recovery
- [ ] Regular backups of consensus state
- [ ] Automated health checks and recovery

### Common Pitfalls to Avoid

1. **Incorrect Quorum Size**: Always use 2f+1 nodes for f failures
2. **Ignoring Network Partitions**: Test and plan for partition scenarios
3. **Weak Failure Detection**: Use proper timeouts and heartbeats
4. **No State Persistence**: Always persist consensus state to disk
5. **Manual Operations**: Automate common operations to prevent errors

Remember: **Consensus is the foundation of distributed systems. Get it wrong, and everything built on top fails.**