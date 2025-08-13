/**
 * Raft Consensus Algorithm Implementation in Java
 * Inspired by Apache Kafka's controller election and CockroachDB's consensus
 * 
 * यह implementation production-ready Raft consensus को Java में दिखाती है
 * जैसे कि बड़े distributed systems में इस्तेमाल होती है
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.time.Instant;
import java.security.MessageDigest;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

// Enums for Raft states
enum NodeState {
    FOLLOWER, CANDIDATE, LEADER
}

// Log entry class
class LogEntry {
    @JsonProperty
    private final int term;
    
    @JsonProperty
    private final int index;
    
    @JsonProperty
    private final Map<String, Object> command;
    
    @JsonProperty
    private final long timestamp;
    
    @JsonProperty
    private final String entryId;
    
    public LogEntry(int term, int index, Map<String, Object> command, String entryId) {
        this.term = term;
        this.index = index;
        this.command = command;
        this.timestamp = Instant.now().toEpochMilli();
        this.entryId = entryId;
    }
    
    // Getters
    public int getTerm() { return term; }
    public int getIndex() { return index; }
    public Map<String, Object> getCommand() { return command; }
    public long getTimestamp() { return timestamp; }
    public String getEntryId() { return entryId; }
}

// Raft RPC messages
class VoteRequest {
    private final int term;
    private final String candidateId;
    private final int lastLogIndex;
    private final int lastLogTerm;
    
    public VoteRequest(int term, String candidateId, int lastLogIndex, int lastLogTerm) {
        this.term = term;
        this.candidateId = candidateId;
        this.lastLogIndex = lastLogIndex;
        this.lastLogTerm = lastLogTerm;
    }
    
    public int getTerm() { return term; }
    public String getCandidateId() { return candidateId; }
    public int getLastLogIndex() { return lastLogIndex; }
    public int getLastLogTerm() { return lastLogTerm; }
}

class VoteResponse {
    private final int term;
    private final boolean voteGranted;
    private final String voterId;
    
    public VoteResponse(int term, boolean voteGranted, String voterId) {
        this.term = term;
        this.voteGranted = voteGranted;
        this.voterId = voterId;
    }
    
    public int getTerm() { return term; }
    public boolean isVoteGranted() { return voteGranted; }
    public String getVoterId() { return voterId; }
}

class AppendEntriesRequest {
    private final int term;
    private final String leaderId;
    private final int prevLogIndex;
    private final int prevLogTerm;
    private final List<LogEntry> entries;
    private final int leaderCommit;
    
    public AppendEntriesRequest(int term, String leaderId, int prevLogIndex, 
                               int prevLogTerm, List<LogEntry> entries, int leaderCommit) {
        this.term = term;
        this.leaderId = leaderId;
        this.prevLogIndex = prevLogIndex;
        this.prevLogTerm = prevLogTerm;
        this.entries = entries;
        this.leaderCommit = leaderCommit;
    }
    
    public int getTerm() { return term; }
    public String getLeaderId() { return leaderId; }
    public int getPrevLogIndex() { return prevLogIndex; }
    public int getPrevLogTerm() { return prevLogTerm; }
    public List<LogEntry> getEntries() { return entries; }
    public int getLeaderCommit() { return leaderCommit; }
}

class AppendEntriesResponse {
    private final int term;
    private final boolean success;
    private final String followerId;
    private final int matchIndex;
    
    public AppendEntriesResponse(int term, boolean success, String followerId, int matchIndex) {
        this.term = term;
        this.success = success;
        this.followerId = followerId;
        this.matchIndex = matchIndex;
    }
    
    public int getTerm() { return term; }
    public boolean isSuccess() { return success; }
    public String getFollowerId() { return followerId; }
    public int getMatchIndex() { return matchIndex; }
}

/**
 * Main Raft Node Implementation
 * बिल्कुल CockroachDB और TiDB की तरह distributed consensus के लिए
 */
public class RaftConsensus {
    private final String nodeId;
    private final List<String> clusterNodes;
    private volatile NodeState state;
    
    // Persistent state (यह disk पर store होना चाहिए)
    private final AtomicInteger currentTerm;
    private volatile String votedFor;
    private final List<LogEntry> log;
    
    // Volatile state
    private final AtomicInteger commitIndex;
    private final AtomicInteger lastApplied;
    
    // Leader state
    private final ConcurrentHashMap<String, Integer> nextIndex;
    private final ConcurrentHashMap<String, Integer> matchIndex;
    
    // Networking and threading
    private final ExecutorService executorService;
    private final ScheduledExecutorService scheduledExecutor;
    private final ConcurrentHashMap<String, RaftConsensus> network;
    
    // Timers
    private ScheduledFuture<?> electionTimer;
    private ScheduledFuture<?> heartbeatTimer;
    
    // Election
    private final Set<String> votesReceived;
    private final Random random;
    
    // State machine (जहाँ actual data store होता है)
    private final ConcurrentHashMap<String, Object> stateMachine;
    
    // JSON serialization
    private final ObjectMapper objectMapper;
    
    public RaftConsensus(String nodeId, List<String> clusterNodes) {
        this.nodeId = nodeId;
        this.clusterNodes = new ArrayList<>(clusterNodes);
        this.state = NodeState.FOLLOWER;
        
        // Initialize persistent state
        this.currentTerm = new AtomicInteger(0);
        this.votedFor = null;
        this.log = Collections.synchronizedList(new ArrayList<>());
        
        // Initialize volatile state
        this.commitIndex = new AtomicInteger(-1);
        this.lastApplied = new AtomicInteger(-1);
        
        // Initialize leader state
        this.nextIndex = new ConcurrentHashMap<>();
        this.matchIndex = new ConcurrentHashMap<>();
        
        // Initialize networking
        this.network = new ConcurrentHashMap<>();
        this.executorService = Executors.newCachedThreadPool();
        this.scheduledExecutor = Executors.newScheduledThreadPool(2);
        
        // Initialize election state
        this.votesReceived = ConcurrentHashMap.newKeySet();
        this.random = new Random();
        
        // Initialize state machine
        this.stateMachine = new ConcurrentHashMap<>();
        
        // JSON mapper
        this.objectMapper = new ObjectMapper();
        
        System.out.printf("🚀 Raft node %s initialized in cluster %s%n", nodeId, clusterNodes);
        
        // Start election timer
        resetElectionTimer();
    }
    
    public void setNetwork(ConcurrentHashMap<String, RaftConsensus> network) {
        this.network.putAll(network);
    }
    
    /**
     * Client request to append new entry (केवल leader पर)
     */
    public boolean appendEntry(Map<String, Object> command) {
        if (state != NodeState.LEADER) {
            System.out.printf("❌ Node %s: Not leader, cannot accept writes%n", nodeId);
            return false;
        }
        
        // Create log entry
        LogEntry entry = new LogEntry(
            currentTerm.get(),
            log.size(),
            command,
            UUID.randomUUID().toString().substring(0, 8)
        );
        
        // Add to log
        synchronized (log) {
            log.add(entry);
        }
        
        System.out.printf("📝 Leader %s: Appended entry %d: %s%n", 
                         nodeId, entry.getIndex(), command);
        
        // Replicate immediately
        replicateToFollowers();
        
        return true;
    }
    
    /**
     * Replicate log entries to all followers
     */
    private void replicateToFollowers() {
        if (state != NodeState.LEADER) {
            return;
        }
        
        for (String follower : clusterNodes) {
            if (!follower.equals(nodeId) && network.containsKey(follower)) {
                executorService.submit(() -> replicateToFollower(follower));
            }
        }
    }
    
    private void replicateToFollower(String followerId) {
        try {
            int nextIdx = nextIndex.getOrDefault(followerId, 0);
            
            // Entries to send
            List<LogEntry> entriesToSend;
            synchronized (log) {
                if (nextIdx < log.size()) {
                    entriesToSend = new ArrayList<>(log.subList(nextIdx, log.size()));
                } else {
                    entriesToSend = new ArrayList<>();
                }
            }
            
            // Previous log info
            int prevLogIndex = nextIdx - 1;
            int prevLogTerm = 0;
            synchronized (log) {
                if (prevLogIndex >= 0 && prevLogIndex < log.size()) {
                    prevLogTerm = log.get(prevLogIndex).getTerm();
                }
            }
            
            // Create append entries request
            AppendEntriesRequest request = new AppendEntriesRequest(
                currentTerm.get(),
                nodeId,
                prevLogIndex,
                prevLogTerm,
                entriesToSend,
                commitIndex.get()
            );
            
            // Send request
            RaftConsensus follower = network.get(followerId);
            if (follower != null) {
                AppendEntriesResponse response = follower.handleAppendEntries(request);
                handleAppendEntriesResponse(followerId, request, response);
            }
            
        } catch (Exception e) {
            System.out.printf("❌ Leader %s: Failed to replicate to %s: %s%n", 
                             nodeId, followerId, e.getMessage());
        }
    }
    
    /**
     * Handle append entries request from leader
     */
    public AppendEntriesResponse handleAppendEntries(AppendEntriesRequest request) {
        // Reply false if term < currentTerm
        if (request.getTerm() < currentTerm.get()) {
            return new AppendEntriesResponse(currentTerm.get(), false, nodeId, -1);
        }
        
        // Update term and become follower if necessary
        if (request.getTerm() > currentTerm.get()) {
            currentTerm.set(request.getTerm());
            votedFor = null;
            state = NodeState.FOLLOWER;
        }
        
        state = NodeState.FOLLOWER;
        resetElectionTimer();
        
        // Check log consistency
        synchronized (log) {
            if (request.getPrevLogIndex() >= 0) {
                if (request.getPrevLogIndex() >= log.size() ||
                    log.get(request.getPrevLogIndex()).getTerm() != request.getPrevLogTerm()) {
                    
                    System.out.printf("🔄 Follower %s: Log inconsistency at index %d%n", 
                                     nodeId, request.getPrevLogIndex());
                    return new AppendEntriesResponse(currentTerm.get(), false, nodeId, -1);
                }
            }
            
            // Handle new entries
            if (!request.getEntries().isEmpty()) {
                int startIndex = request.getPrevLogIndex() + 1;
                
                // Remove conflicting entries
                for (int i = 0; i < request.getEntries().size(); i++) {
                    int entryIndex = startIndex + i;
                    LogEntry newEntry = request.getEntries().get(i);
                    
                    if (entryIndex < log.size()) {
                        LogEntry existingEntry = log.get(entryIndex);
                        if (existingEntry.getTerm() != newEntry.getTerm()) {
                            // Remove conflicting entries
                            log.subList(entryIndex, log.size()).clear();
                            System.out.printf("🗑️ Follower %s: Removed conflicting entries from index %d%n", 
                                             nodeId, entryIndex);
                            break;
                        }
                    }
                }
                
                // Append new entries
                for (int i = log.size() - startIndex; i < request.getEntries().size(); i++) {
                    LogEntry entry = request.getEntries().get(i);
                    log.add(entry);
                    System.out.printf("➕ Follower %s: Appended entry %d%n", nodeId, entry.getIndex());
                }
            }
        }
        
        // Update commit index
        if (request.getLeaderCommit() > commitIndex.get()) {
            int oldCommit = commitIndex.get();
            int newCommit = Math.min(request.getLeaderCommit(), log.size() - 1);
            commitIndex.set(newCommit);
            
            applyCommittedEntries();
            
            if (newCommit > oldCommit) {
                System.out.printf("✅ Follower %s: Updated commit index to %d%n", nodeId, newCommit);
            }
        }
        
        return new AppendEntriesResponse(currentTerm.get(), true, nodeId, log.size() - 1);
    }
    
    private void handleAppendEntriesResponse(String followerId, AppendEntriesRequest request, 
                                           AppendEntriesResponse response) {
        if (state != NodeState.LEADER) {
            return;
        }
        
        // Step down if higher term
        if (response.getTerm() > currentTerm.get()) {
            currentTerm.set(response.getTerm());
            state = NodeState.FOLLOWER;
            votedFor = null;
            resetElectionTimer();
            return;
        }
        
        if (response.isSuccess()) {
            // Update indices
            nextIndex.put(followerId, response.getMatchIndex() + 1);
            matchIndex.put(followerId, response.getMatchIndex());
            
            System.out.printf("✅ Leader %s: Successfully replicated to %s (match: %d)%n", 
                             nodeId, followerId, response.getMatchIndex());
            
            // Try to update commit index
            updateCommitIndex();
        } else {
            // Decrement nextIndex and retry
            int currentNext = nextIndex.getOrDefault(followerId, 0);
            nextIndex.put(followerId, Math.max(0, currentNext - 1));
            
            System.out.printf("🔄 Leader %s: Retrying replication to %s from index %d%n", 
                             nodeId, followerId, nextIndex.get(followerId));
            
            // Retry
            executorService.submit(() -> replicateToFollower(followerId));
        }
    }
    
    private void updateCommitIndex() {
        if (state != NodeState.LEADER) {
            return;
        }
        
        synchronized (log) {
            for (int index = log.size() - 1; index > commitIndex.get(); index--) {
                if (log.get(index).getTerm() != currentTerm.get()) {
                    continue;
                }
                
                // Count replications
                int replicationCount = 1; // Leader has it
                for (String node : clusterNodes) {
                    if (!node.equals(nodeId) && matchIndex.getOrDefault(node, -1) >= index) {
                        replicationCount++;
                    }
                }
                
                // Check majority
                int majority = clusterNodes.size() / 2 + 1;
                if (replicationCount >= majority) {
                    int oldCommit = commitIndex.get();
                    commitIndex.set(index);
                    
                    applyCommittedEntries();
                    
                    System.out.printf("🎯 Leader %s: Committed entries up to %d (%d/%d replicated)%n", 
                                     nodeId, index, replicationCount, clusterNodes.size());
                    break;
                }
            }
        }
    }
    
    private void applyCommittedEntries() {
        while (lastApplied.get() < commitIndex.get()) {
            int nextToApply = lastApplied.incrementAndGet();
            
            synchronized (log) {
                if (nextToApply < log.size()) {
                    LogEntry entry = log.get(nextToApply);
                    applyCommand(entry.getCommand());
                    
                    System.out.printf("🔧 Node %s: Applied entry %d: %s%n", 
                                     nodeId, nextToApply, entry.getCommand());
                }
            }
        }
    }
    
    private void applyCommand(Map<String, Object> command) {
        String type = (String) command.get("type");
        
        if ("SET".equals(type)) {
            String key = (String) command.get("key");
            Object value = command.get("value");
            stateMachine.put(key, value);
            
        } else if ("DELETE".equals(type)) {
            String key = (String) command.get("key");
            stateMachine.remove(key);
            
        } else if ("TRANSFER".equals(type)) {
            // UPI-style money transfer
            String fromAccount = (String) command.get("from_account");
            String toAccount = (String) command.get("to_account");
            Number amount = (Number) command.get("amount");
            
            // Debit from source
            Object fromBalance = stateMachine.get(fromAccount);
            if (fromBalance instanceof Number) {
                double newFromBalance = ((Number) fromBalance).doubleValue() - amount.doubleValue();
                stateMachine.put(fromAccount, newFromBalance);
            }
            
            // Credit to destination
            Object toBalance = stateMachine.getOrDefault(toAccount, 0.0);
            if (toBalance instanceof Number) {
                double newToBalance = ((Number) toBalance).doubleValue() + amount.doubleValue();
                stateMachine.put(toAccount, newToBalance);
            }
        }
    }
    
    /**
     * Start leader election
     */
    private void startElection() {
        if (state == NodeState.LEADER) {
            return;
        }
        
        System.out.printf("🗳️ Node %s: Starting election for term %d%n", nodeId, currentTerm.get() + 1);
        
        state = NodeState.CANDIDATE;
        currentTerm.incrementAndGet();
        votedFor = nodeId;
        votesReceived.clear();
        votesReceived.add(nodeId);
        
        resetElectionTimer();
        
        // Send vote requests
        sendVoteRequests();
    }
    
    private void sendVoteRequests() {
        int lastLogIndex;
        int lastLogTerm;
        
        synchronized (log) {
            lastLogIndex = log.size() - 1;
            lastLogTerm = (lastLogIndex >= 0) ? log.get(lastLogIndex).getTerm() : 0;
        }
        
        VoteRequest request = new VoteRequest(currentTerm.get(), nodeId, lastLogIndex, lastLogTerm);
        
        for (String nodeIdTarget : clusterNodes) {
            if (!nodeIdTarget.equals(nodeId) && network.containsKey(nodeIdTarget)) {
                executorService.submit(() -> {
                    try {
                        RaftConsensus node = network.get(nodeIdTarget);
                        VoteResponse response = node.handleVoteRequest(request);
                        handleVoteResponse(response);
                    } catch (Exception e) {
                        System.out.printf("❌ Candidate %s: Failed to get vote from %s%n", nodeId, nodeIdTarget);
                    }
                });
            }
        }
    }
    
    public VoteResponse handleVoteRequest(VoteRequest request) {
        System.out.printf("📬 Node %s: Received vote request from %s for term %d%n", 
                         nodeId, request.getCandidateId(), request.getTerm());
        
        // Reject if candidate's term is older
        if (request.getTerm() < currentTerm.get()) {
            return new VoteResponse(currentTerm.get(), false, nodeId);
        }
        
        // Update term if candidate's term is newer
        if (request.getTerm() > currentTerm.get()) {
            currentTerm.set(request.getTerm());
            votedFor = null;
            state = NodeState.FOLLOWER;
        }
        
        // Grant vote if we haven't voted or voted for same candidate
        boolean voteGranted = false;
        if (votedFor == null || votedFor.equals(request.getCandidateId())) {
            // Check if candidate's log is up-to-date
            synchronized (log) {
                int ourLastLogTerm = log.isEmpty() ? 0 : log.get(log.size() - 1).getTerm();
                int ourLastLogIndex = log.size() - 1;
                
                boolean candidateLogOk = (request.getLastLogTerm() > ourLastLogTerm) ||
                                       (request.getLastLogTerm() == ourLastLogTerm && 
                                        request.getLastLogIndex() >= ourLastLogIndex);
                
                if (candidateLogOk) {
                    voteGranted = true;
                    votedFor = request.getCandidateId();
                    resetElectionTimer();
                    System.out.printf("✅ Node %s: Granted vote to %s%n", nodeId, request.getCandidateId());
                }
            }
        }
        
        return new VoteResponse(currentTerm.get(), voteGranted, nodeId);
    }
    
    private void handleVoteResponse(VoteResponse response) {
        if (state != NodeState.CANDIDATE) {
            return;
        }
        
        // Step down if higher term
        if (response.getTerm() > currentTerm.get()) {
            currentTerm.set(response.getTerm());
            state = NodeState.FOLLOWER;
            votedFor = null;
            resetElectionTimer();
            return;
        }
        
        // Count vote
        if (response.isVoteGranted() && response.getTerm() == currentTerm.get()) {
            votesReceived.add(response.getVoterId());
            
            System.out.printf("📊 Candidate %s: Received vote from %s (%d/%d)%n", 
                             nodeId, response.getVoterId(), votesReceived.size(), clusterNodes.size());
            
            // Check if we have majority
            int majority = clusterNodes.size() / 2 + 1;
            if (votesReceived.size() >= majority) {
                becomeLeader();
            }
        }
    }
    
    private void becomeLeader() {
        if (state != NodeState.CANDIDATE) {
            return;
        }
        
        System.out.printf("👑 Node %s: Became LEADER for term %d%n", nodeId, currentTerm.get());
        state = NodeState.LEADER;
        
        // Cancel election timer
        if (electionTimer != null) {
            electionTimer.cancel(false);
        }
        
        // Initialize leader state
        synchronized (log) {
            int nextIdx = log.size();
            for (String node : clusterNodes) {
                if (!node.equals(nodeId)) {
                    nextIndex.put(node, nextIdx);
                    matchIndex.put(node, -1);
                }
            }
        }
        
        // Start heartbeats
        startHeartbeatTimer();
        
        // Send initial heartbeat
        replicateToFollowers();
    }
    
    private void resetElectionTimer() {
        if (electionTimer != null) {
            electionTimer.cancel(false);
        }
        
        // Random timeout between 150-300ms
        long timeout = 150 + random.nextInt(150);
        electionTimer = scheduledExecutor.schedule(
            this::startElection,
            timeout,
            TimeUnit.MILLISECONDS
        );
    }
    
    private void startHeartbeatTimer() {
        if (heartbeatTimer != null) {
            heartbeatTimer.cancel(false);
        }
        
        if (state == NodeState.LEADER) {
            heartbeatTimer = scheduledExecutor.scheduleAtFixedRate(
                this::replicateToFollowers,
                50,
                50,
                TimeUnit.MILLISECONDS
            );
        }
    }
    
    public Map<String, Object> getStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("node_id", nodeId);
        status.put("state", state.name());
        status.put("term", currentTerm.get());
        status.put("voted_for", votedFor);
        status.put("log_length", log.size());
        status.put("commit_index", commitIndex.get());
        status.put("last_applied", lastApplied.get());
        status.put("state_machine_size", stateMachine.size());
        
        return status;
    }
    
    public void shutdown() {
        if (electionTimer != null) {
            electionTimer.cancel(false);
        }
        if (heartbeatTimer != null) {
            heartbeatTimer.cancel(false);
        }
        executorService.shutdown();
        scheduledExecutor.shutdown();
    }
    
    public Map<String, Object> getStateMachine() {
        return new HashMap<>(stateMachine);
    }
    
    /**
     * Demo simulation method
     */
    public static void main(String[] args) {
        System.out.println("🇮🇳 Raft Consensus Java Implementation - Banking Cluster Demo");
        System.out.println("=".repeat(70));
        
        // Create cluster nodes
        List<String> nodeIds = Arrays.asList("bank-mumbai", "bank-delhi", "bank-bangalore");
        
        // Create Raft nodes
        Map<String, RaftConsensus> cluster = new HashMap<>();
        for (String nodeId : nodeIds) {
            cluster.put(nodeId, new RaftConsensus(nodeId, nodeIds));
        }
        
        // Set network connections
        ConcurrentHashMap<String, RaftConsensus> network = new ConcurrentHashMap<>(cluster);
        for (RaftConsensus node : cluster.values()) {
            node.setNetwork(network);
        }
        
        try {
            // Wait for leader election
            Thread.sleep(2000);
            
            // Find leader
            RaftConsensus leader = null;
            for (RaftConsensus node : cluster.values()) {
                if (node.state == NodeState.LEADER) {
                    leader = node;
                    break;
                }
            }
            
            if (leader != null) {
                System.out.printf("👑 Leader: %s%n", leader.nodeId);
                
                // Simulate banking transactions
                System.out.println("\n💳 Processing banking transactions...");
                
                Map<String, Object>[] transactions = new Map[]{
                    Map.of("type", "SET", "key", "account:rahul", "value", 50000),
                    Map.of("type", "SET", "key", "account:priya", "value", 30000),
                    Map.of("type", "TRANSFER", "from_account", "account:rahul", 
                           "to_account", "account:priya", "amount", 5000),
                    Map.of("type", "SET", "key", "account:merchant:amazon", "value", 0),
                    Map.of("type", "TRANSFER", "from_account", "account:priya", 
                           "to_account", "account:merchant:amazon", "amount", 2500)
                };
                
                // Process transactions
                for (int i = 0; i < transactions.length; i++) {
                    System.out.printf("\n📱 Transaction %d: %s%n", i+1, transactions[i]);
                    leader.appendEntry(transactions[i]);
                    Thread.sleep(500);
                }
                
                // Wait for commits
                Thread.sleep(2000);
                
                // Show final state
                System.out.println("\n💰 Final Account Balances:");
                Map<String, Object> finalState = leader.getStateMachine();
                for (Map.Entry<String, Object> entry : finalState.entrySet()) {
                    System.out.printf("   %s: ₹%s%n", entry.getKey(), entry.getValue());
                }
                
                // Verify consistency
                System.out.println("\n🔍 Consistency Check:");
                boolean consistent = true;
                for (RaftConsensus node : cluster.values()) {
                    Map<String, Object> nodeState = node.getStateMachine();
                    if (nodeState.equals(finalState)) {
                        System.out.printf("   ✅ %s: CONSISTENT%n", node.nodeId);
                    } else {
                        System.out.printf("   ❌ %s: INCONSISTENT%n", node.nodeId);
                        consistent = false;
                    }
                }
                
                if (consistent) {
                    System.out.println("\n🎉 All nodes have consistent state!");
                }
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            // Cleanup
            for (RaftConsensus node : cluster.values()) {
                node.shutdown();
            }
        }
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("Java Raft Implementation Key Features:");
        System.out.println("1. Thread-safe concurrent operations");
        System.out.println("2. Atomic operations for term management");
        System.out.println("3. Scheduled executor for timers");
        System.out.println("4. ConcurrentHashMap for state management");
        System.out.println("5. Production-ready error handling");
    }
}