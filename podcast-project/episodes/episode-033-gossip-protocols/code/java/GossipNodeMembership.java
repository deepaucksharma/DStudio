/**
 * Gossip-based Node Membership Protocol
 * =====================================
 * 
 * IRCTC Server Cluster: जब train booking servers का cluster हो तो
 * कैसे पता चले कि कौन से servers available हैं और कौन से fail हो गए?
 * 
 * This implements a gossip-based membership protocol similar to SWIM
 * for maintaining cluster membership in distributed systems.
 * 
 * Author: Code Developer Agent
 * Episode: 33 - Gossip Protocols
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.Instant;
import java.time.Duration;

enum NodeState {
    ALIVE,
    SUSPECTED,  // शक है कि fail हो गया
    FAILED,     // confirm fail हो गया  
    LEFT        // gracefully left cluster
}

class MembershipInfo {
    private final String nodeId;
    private final String address;
    private final int port;
    private NodeState state;
    private int incarnation;
    private long lastSeen;
    private int suspicionCount;
    
    public MembershipInfo(String nodeId, String address, int port) {
        this.nodeId = nodeId;
        this.address = address;
        this.port = port;
        this.state = NodeState.ALIVE;
        this.incarnation = 0;
        this.lastSeen = System.currentTimeMillis();
        this.suspicionCount = 0;
    }
    
    // Getters and setters
    public String getNodeId() { return nodeId; }
    public String getAddress() { return address; }
    public int getPort() { return port; }
    public NodeState getState() { return state; }
    public void setState(NodeState state) { this.state = state; }
    public int getIncarnation() { return incarnation; }
    public void setIncarnation(int incarnation) { this.incarnation = incarnation; }
    public long getLastSeen() { return lastSeen; }
    public void setLastSeen(long lastSeen) { this.lastSeen = lastSeen; }
    public int getSuspicionCount() { return suspicionCount; }
    public void setSuspicionCount(int count) { this.suspicionCount = count; }
    
    public void incrementIncarnation() {
        this.incarnation++;
    }
    
    public boolean isNewerThan(MembershipInfo other) {
        return this.incarnation > other.incarnation ||
               (this.incarnation == other.incarnation && this.lastSeen > other.lastSeen);
    }
    
    @Override
    public String toString() {
        return String.format("Node{id=%s, state=%s, incarnation=%d, lastSeen=%d}", 
                           nodeId, state, incarnation, lastSeen);
    }
}

class GossipMessage {
    private final String senderId;
    private final List<MembershipInfo> membershipList;
    private final long timestamp;
    private final int gossipRound;
    
    public GossipMessage(String senderId, List<MembershipInfo> membershipList, int gossipRound) {
        this.senderId = senderId;
        this.membershipList = new ArrayList<>(membershipList);
        this.timestamp = System.currentTimeMillis();
        this.gossipRound = gossipRound;
    }
    
    public String getSenderId() { return senderId; }
    public List<MembershipInfo> getMembershipList() { return membershipList; }
    public long getTimestamp() { return timestamp; }
    public int getGossipRound() { return gossipRound; }
}

public class GossipNodeMembership {
    private final String nodeId;
    private final String serverName;
    private final String region;
    private final Map<String, MembershipInfo> membershipTable;
    private final Set<String> knownNodes;
    private final Random random;
    
    // Gossip protocol parameters
    private final int gossipFanout;
    private final long gossipInterval; // milliseconds
    private final long failureTimeout; // milliseconds
    private final long suspicionTimeout; // milliseconds
    
    // Threading
    private final ScheduledExecutorService scheduler;
    private final AtomicInteger gossipRound;
    
    // Statistics
    private int gossipMessagesSent;
    private int gossipMessagesReceived;
    private int nodeFailuresDetected;
    
    public GossipNodeMembership(String nodeId, String serverName, String region) {
        this.nodeId = nodeId;
        this.serverName = serverName;
        this.region = region;
        this.membershipTable = new ConcurrentHashMap<>();
        this.knownNodes = ConcurrentHashMap.newKeySet();
        this.random = new Random();
        
        // Configuration
        this.gossipFanout = 3;
        this.gossipInterval = 2000; // 2 seconds
        this.failureTimeout = 10000; // 10 seconds
        this.suspicionTimeout = 5000; // 5 seconds
        
        this.scheduler = Executors.newScheduledThreadPool(2);
        this.gossipRound = new AtomicInteger(0);
        
        // Add self to membership table
        MembershipInfo selfInfo = new MembershipInfo(nodeId, "localhost", 8080);
        membershipTable.put(nodeId, selfInfo);
        knownNodes.add(nodeId);
        
        startGossipProtocol();
        startFailureDetection();
        
        System.out.println("🚂 IRCTC Server " + serverName + " started in " + region);
    }
    
    public void addNode(String nodeId, String address, int port) {
        MembershipInfo info = new MembershipInfo(nodeId, address, port);
        membershipTable.put(nodeId, info);
        knownNodes.add(nodeId);
        
        System.out.println("➕ Added node: " + nodeId + " (" + address + ":" + port + ")");
    }
    
    public void simulateNodeFailure() {
        // Simulate this node failing (stop participating in gossip)
        System.out.println("💀 " + serverName + " failed!");
        scheduler.shutdown();
    }
    
    public void simulateNodeRecovery() {
        // Simulate node recovery by incrementing incarnation
        MembershipInfo selfInfo = membershipTable.get(nodeId);
        if (selfInfo != null) {
            selfInfo.incrementIncarnation();
            selfInfo.setState(NodeState.ALIVE);
            selfInfo.setLastSeen(System.currentTimeMillis());
            
            System.out.println("🔄 " + serverName + " recovered with incarnation " + 
                             selfInfo.getIncarnation());
        }
    }
    
    private void startGossipProtocol() {
        scheduler.scheduleAtFixedRate(this::performGossipRound, 
                                    gossipInterval, gossipInterval, TimeUnit.MILLISECONDS);
    }
    
    private void startFailureDetection() {
        scheduler.scheduleAtFixedRate(this::detectFailures, 
                                    failureTimeout / 2, failureTimeout / 2, TimeUnit.MILLISECONDS);
    }
    
    private void performGossipRound() {
        int currentRound = gossipRound.incrementAndGet();
        
        // Select random nodes for gossip
        List<String> gossipTargets = selectGossipTargets();
        
        if (gossipTargets.isEmpty()) {
            return;
        }
        
        // Create gossip message with current membership info
        List<MembershipInfo> membershipSnapshot = new ArrayList<>(membershipTable.values());
        GossipMessage message = new GossipMessage(nodeId, membershipSnapshot, currentRound);
        
        // Send gossip to selected targets
        for (String targetId : gossipTargets) {
            sendGossipMessage(targetId, message);
        }
        
        System.out.println("📡 " + serverName + " gossip round " + currentRound + 
                         " to " + gossipTargets.size() + " nodes");
    }
    
    private List<String> selectGossipTargets() {
        List<String> availableNodes = new ArrayList<>();
        
        for (MembershipInfo info : membershipTable.values()) {
            if (!info.getNodeId().equals(nodeId) && info.getState() != NodeState.FAILED) {
                availableNodes.add(info.getNodeId());
            }
        }
        
        if (availableNodes.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Select random subset
        Collections.shuffle(availableNodes, random);
        int targetCount = Math.min(gossipFanout, availableNodes.size());
        
        return availableNodes.subList(0, targetCount);
    }
    
    private void sendGossipMessage(String targetId, GossipMessage message) {
        // Simulate network transmission
        gossipMessagesSent++;
        
        // In real implementation, this would use actual network communication
        System.out.println("📤 Sending gossip from " + nodeId + " to " + targetId);
        
        // Simulate message processing delay
        scheduler.schedule(() -> {
            // Simulate the target node receiving this message
            processGossipMessage(message);
        }, random.nextInt(100), TimeUnit.MILLISECONDS);
    }
    
    public void processGossipMessage(GossipMessage message) {
        gossipMessagesReceived++;
        
        System.out.println("📥 " + serverName + " received gossip from " + message.getSenderId());
        
        // Process each membership entry in the gossip
        for (MembershipInfo receivedInfo : message.getMembershipList()) {
            String receivedNodeId = receivedInfo.getNodeId();
            
            // Skip self
            if (receivedNodeId.equals(nodeId)) {
                continue;
            }
            
            MembershipInfo localInfo = membershipTable.get(receivedNodeId);
            
            if (localInfo == null) {
                // New node discovered
                membershipTable.put(receivedNodeId, receivedInfo);
                knownNodes.add(receivedNodeId);
                
                System.out.println("🔍 Discovered new node: " + receivedNodeId);
                
            } else {
                // Update existing node info if received info is newer
                if (receivedInfo.isNewerThan(localInfo)) {
                    // Update membership info
                    localInfo.setState(receivedInfo.getState());
                    localInfo.setIncarnation(receivedInfo.getIncarnation());
                    localInfo.setLastSeen(receivedInfo.getLastSeen());
                    
                    if (receivedInfo.getState() == NodeState.FAILED) {
                        System.out.println("💀 Learned about node failure: " + receivedNodeId);
                        nodeFailuresDetected++;
                    } else if (receivedInfo.getState() == NodeState.ALIVE && 
                               localInfo.getState() != NodeState.ALIVE) {
                        System.out.println("🔄 Node recovered: " + receivedNodeId);
                    }
                }
            }
        }
    }
    
    private void detectFailures() {
        long currentTime = System.currentTimeMillis();
        List<String> suspectedNodes = new ArrayList<>();
        List<String> failedNodes = new ArrayList<>();
        
        for (MembershipInfo info : membershipTable.values()) {
            if (info.getNodeId().equals(nodeId)) {
                continue; // Skip self
            }
            
            long timeSinceLastSeen = currentTime - info.getLastSeen();
            
            if (info.getState() == NodeState.ALIVE) {
                if (timeSinceLastSeen > failureTimeout) {
                    // Declare node as failed
                    info.setState(NodeState.FAILED);
                    failedNodes.add(info.getNodeId());
                } else if (timeSinceLastSeen > suspicionTimeout) {
                    // Suspect node failure
                    info.setState(NodeState.SUSPECTED);
                    info.setSuspicionCount(info.getSuspicionCount() + 1);
                    suspectedNodes.add(info.getNodeId());
                }
            } else if (info.getState() == NodeState.SUSPECTED) {
                if (timeSinceLastSeen > failureTimeout) {
                    // Promote suspicion to failure
                    info.setState(NodeState.FAILED);
                    failedNodes.add(info.getNodeId());
                }
            }
        }
        
        // Log detected failures and suspicions
        for (String nodeId : suspectedNodes) {
            System.out.println("⚠️ Suspecting node failure: " + nodeId);
        }
        
        for (String nodeId : failedNodes) {
            System.out.println("💀 Detected node failure: " + nodeId);
            nodeFailuresDetected++;
        }
    }
    
    public Map<NodeState, Integer> getClusterStatus() {
        Map<NodeState, Integer> statusCount = new EnumMap<>(NodeState.class);
        
        for (NodeState state : NodeState.values()) {
            statusCount.put(state, 0);
        }
        
        for (MembershipInfo info : membershipTable.values()) {
            statusCount.merge(info.getState(), 1, Integer::sum);
        }
        
        return statusCount;
    }
    
    public void printClusterStatus() {
        Map<NodeState, Integer> status = getClusterStatus();
        
        System.out.println("\n📊 Cluster Status for " + serverName + ":");
        System.out.println("  Total nodes known: " + membershipTable.size());
        
        for (Map.Entry<NodeState, Integer> entry : status.entrySet()) {
            System.out.println("  " + entry.getKey() + ": " + entry.getValue());
        }
        
        System.out.println("  Gossip messages sent: " + gossipMessagesSent);
        System.out.println("  Gossip messages received: " + gossipMessagesReceived);
        System.out.println("  Node failures detected: " + nodeFailuresDetected);
    }
    
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
        }
    }
    
    // Main method for testing
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🇮🇳 IRCTC Server Cluster Membership Simulation");
        System.out.println("=" + "=".repeat(50));
        
        // Create IRCTC booking servers
        List<GossipNodeMembership> servers = Arrays.asList(
            new GossipNodeMembership("irctc-mumbai-01", "Mumbai Central", "West"),
            new GossipNodeMembership("irctc-delhi-01", "New Delhi", "North"),
            new GossipNodeMembership("irctc-bangalore-01", "Bangalore City", "South"),
            new GossipNodeMembership("irctc-chennai-01", "Chennai Central", "South"),
            new GossipNodeMembership("irctc-kolkata-01", "Howrah", "East")
        );
        
        // Build network topology
        for (int i = 0; i < servers.size(); i++) {
            for (int j = i + 1; j < servers.size(); j++) {
                GossipNodeMembership server1 = servers.get(i);
                GossipNodeMembership server2 = servers.get(j);
                
                // Add each server to the other's membership table
                server1.addNode(server2.nodeId, "localhost", 8080 + j);
                server2.addNode(server1.nodeId, "localhost", 8080 + i);
            }
        }
        
        System.out.println("\nNetwork topology created. Simulating cluster activity...\n");
        
        // Let the cluster run for a while
        Thread.sleep(8000);
        
        // Simulate server failure
        System.out.println("\n🔥 Simulating Mumbai server failure...");
        servers.get(0).simulateNodeFailure();
        
        // Wait for failure detection
        Thread.sleep(6000);
        
        // Print status from different servers
        for (int i = 1; i < Math.min(3, servers.size()); i++) {
            servers.get(i).printClusterStatus();
        }
        
        // Simulate recovery
        System.out.println("\n🔄 Simulating Mumbai server recovery...");
        // Create new instance to simulate recovery
        GossipNodeMembership recoveredServer = new GossipNodeMembership(
            "irctc-mumbai-01", "Mumbai Central (Recovered)", "West"
        );
        
        // Reconnect to cluster
        for (int i = 1; i < servers.size(); i++) {
            recoveredServer.addNode(servers.get(i).nodeId, "localhost", 8080 + i);
        }
        
        Thread.sleep(5000);
        
        // Final status
        System.out.println("\n📈 Final Cluster Status:");
        recoveredServer.printClusterStatus();
        
        // Cleanup
        for (GossipNodeMembership server : servers) {
            server.shutdown();
        }
        recoveredServer.shutdown();
        
        System.out.println("\nSimulation completed!");
    }
}