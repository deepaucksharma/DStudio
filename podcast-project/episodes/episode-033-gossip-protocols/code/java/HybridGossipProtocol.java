/**
 * Hybrid Gossip Protocol for Large-Scale Distributed Systems
 * ==========================================================
 * 
 * Paytm Payment Gateway Network: जब millions of transactions process करने हों
 * तो कैसे efficiently status updates को propagate करें across hundreds of servers?
 * 
 * This implements a hybrid gossip protocol that combines push-pull gossip
 * with hierarchical routing for scalable information dissemination.
 * 
 * Author: Code Developer Agent
 * Episode: 33 - Gossip Protocols
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;

enum GossipMode {
    PUSH_ONLY,    // केवल भेजना
    PULL_ONLY,    // केवल मांगना
    PUSH_PULL,    // दोनों
    ADAPTIVE      // स्थिति के अनुसार
}

enum NodeTier {
    GATEWAY,      // Front-end payment gateways
    PROCESSOR,    // Core transaction processors
    VALIDATOR,    // Transaction validators
    STORAGE       // Data storage nodes
}

class PaymentTransaction {
    private final String transactionId;
    private final String merchantId;
    private final String customerId;
    private final double amount;
    private final String currency;
    private final String status;
    private final long timestamp;
    private final int version;
    private final String processingNode;
    
    public PaymentTransaction(String transactionId, String merchantId, String customerId,
                            double amount, String currency, String status, String processingNode) {
        this.transactionId = transactionId;
        this.merchantId = merchantId;
        this.customerId = customerId;
        this.amount = amount;
        this.currency = currency;
        this.status = status;
        this.timestamp = System.currentTimeMillis();
        this.version = 1;
        this.processingNode = processingNode;
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public String getMerchantId() { return merchantId; }
    public String getCustomerId() { return customerId; }
    public double getAmount() { return amount; }
    public String getCurrency() { return currency; }
    public String getStatus() { return status; }
    public long getTimestamp() { return timestamp; }
    public int getVersion() { return version; }
    public String getProcessingNode() { return processingNode; }
    
    @Override
    public String toString() {
        return String.format("Txn{id=%s, amount=%.2f %s, status=%s, node=%s}", 
                           transactionId, amount, currency, status, processingNode);
    }
}

class GossipPayload {
    private final String senderId;
    private final GossipMode mode;
    private final Map<String, PaymentTransaction> transactions;
    private final Map<String, Long> versionVector;
    private final Set<String> requestedKeys;
    private final long timestamp;
    private final int payloadSize;
    
    public GossipPayload(String senderId, GossipMode mode) {
        this.senderId = senderId;
        this.mode = mode;
        this.transactions = new HashMap<>();
        this.versionVector = new HashMap<>();
        this.requestedKeys = new HashSet<>();
        this.timestamp = System.currentTimeMillis();
        this.payloadSize = 0;
    }
    
    public void addTransaction(PaymentTransaction transaction) {
        transactions.put(transaction.getTransactionId(), transaction);
    }
    
    public void addVersionInfo(String nodeId, long version) {
        versionVector.put(nodeId, version);
    }
    
    public void addRequestedKey(String key) {
        requestedKeys.add(key);
    }
    
    // Getters
    public String getSenderId() { return senderId; }
    public GossipMode getMode() { return mode; }
    public Map<String, PaymentTransaction> getTransactions() { return transactions; }
    public Map<String, Long> getVersionVector() { return versionVector; }
    public Set<String> getRequestedKeys() { return requestedKeys; }
    public long getTimestamp() { return timestamp; }
    public int getPayloadSize() { return transactions.size(); }
}

class NetworkMetrics {
    private final AtomicLong messagesExchanged = new AtomicLong(0);
    private final AtomicLong bytesTransferred = new AtomicLong(0);
    private final AtomicInteger convergenceTime = new AtomicInteger(0);
    private final AtomicInteger activeConnections = new AtomicInteger(0);
    private final Map<String, AtomicInteger> nodeMessageCounts = new ConcurrentHashMap<>();
    
    public void recordMessage(String nodeId, int messageSize) {
        messagesExchanged.incrementAndGet();
        bytesTransferred.addAndGet(messageSize);
        nodeMessageCounts.computeIfAbsent(nodeId, k -> new AtomicInteger(0)).incrementAndGet();
    }
    
    public void recordConnection(int delta) {
        activeConnections.addAndGet(delta);
    }
    
    public void recordConvergence(int time) {
        convergenceTime.set(time);
    }
    
    // Getters
    public long getMessagesExchanged() { return messagesExchanged.get(); }
    public long getBytesTransferred() { return bytesTransferred.get(); }
    public int getConvergenceTime() { return convergenceTime.get(); }
    public int getActiveConnections() { return activeConnections.get(); }
    public Map<String, AtomicInteger> getNodeMessageCounts() { return nodeMessageCounts; }
}

public class HybridGossipProtocol {
    private final String nodeId;
    private final String region;
    private final NodeTier tier;
    private final GossipMode currentMode;
    
    // Data storage
    private final Map<String, PaymentTransaction> transactionStore;
    private final Map<String, Long> versionVector;
    private final AtomicLong localVersion;
    
    // Network topology
    private final Set<String> peers;
    private final Map<String, NodeTier> peerTiers;
    private final Map<String, Double> peerWeights;
    
    // Hybrid gossip parameters
    private final int maxPeersPerRound;
    private final long gossipInterval;
    private final int payloadSizeLimit;
    private final double adaptiveThreshold;
    
    // Threading
    private final ScheduledExecutorService scheduler;
    private final Random random;
    
    // Statistics
    private final NetworkMetrics metrics;
    private final AtomicInteger gossipRounds = new AtomicInteger(0);
    private final AtomicInteger pushRounds = new AtomicInteger(0);
    private final AtomicInteger pullRounds = new AtomicInteger(0);
    private final AtomicInteger hybridRounds = new AtomicInteger(0);
    
    public HybridGossipProtocol(String nodeId, String region, NodeTier tier) {
        this.nodeId = nodeId;
        this.region = region;
        this.tier = tier;
        this.currentMode = GossipMode.ADAPTIVE;
        
        this.transactionStore = new ConcurrentHashMap<>();
        this.versionVector = new ConcurrentHashMap<>();
        this.localVersion = new AtomicLong(0);
        
        this.peers = ConcurrentHashMap.newKeySet();
        this.peerTiers = new ConcurrentHashMap<>();
        this.peerWeights = new ConcurrentHashMap<>();
        
        // Configuration based on node tier
        this.maxPeersPerRound = calculateMaxPeers(tier);
        this.gossipInterval = calculateGossipInterval(tier);
        this.payloadSizeLimit = calculatePayloadLimit(tier);
        this.adaptiveThreshold = 0.7;
        
        this.scheduler = Executors.newScheduledThreadPool(3);
        this.random = new Random();
        this.metrics = new NetworkMetrics();
        
        startHybridGossipProtocol();
        
        System.out.println("💳 Paytm " + tier + " node " + nodeId + " started in " + region);
    }
    
    private int calculateMaxPeers(NodeTier tier) {
        switch (tier) {
            case GATEWAY: return 5;    // High connectivity for gateways
            case PROCESSOR: return 4;  // Medium connectivity for processors
            case VALIDATOR: return 3;  // Lower connectivity for validators
            case STORAGE: return 2;    // Minimal connectivity for storage
            default: return 3;
        }
    }
    
    private long calculateGossipInterval(NodeTier tier) {
        switch (tier) {
            case GATEWAY: return 1000;   // 1 second - high frequency
            case PROCESSOR: return 2000; // 2 seconds - medium frequency
            case VALIDATOR: return 3000; // 3 seconds - lower frequency
            case STORAGE: return 5000;   // 5 seconds - lowest frequency
            default: return 2000;
        }
    }
    
    private int calculatePayloadLimit(NodeTier tier) {
        switch (tier) {
            case GATEWAY: return 100;    // Large payloads for gateways
            case PROCESSOR: return 75;   // Medium payloads for processors
            case VALIDATOR: return 50;   // Smaller payloads for validators
            case STORAGE: return 25;     // Minimal payloads for storage
            default: return 50;
        }
    }
    
    public void addPeer(String peerId, NodeTier peerTier, double weight) {
        peers.add(peerId);
        peerTiers.put(peerId, peerTier);
        peerWeights.put(peerId, weight);
        versionVector.put(peerId, 0L);
        
        metrics.recordConnection(1);
        
        System.out.println("🔗 " + nodeId + " connected to " + peerId + " (" + peerTier + ")");
    }
    
    public void processTransaction(PaymentTransaction transaction) {
        String txnId = transaction.getTransactionId();
        transactionStore.put(txnId, transaction);
        
        long version = localVersion.incrementAndGet();
        versionVector.put(nodeId, version);
        
        System.out.println("💰 " + nodeId + " processed: " + transaction);
        
        // Trigger immediate gossip for critical transactions
        if (transaction.getAmount() > 100000 || "FAILED".equals(transaction.getStatus())) {
            scheduler.schedule(this::performUrgentGossip, 100, TimeUnit.MILLISECONDS);
        }
    }
    
    private void startHybridGossipProtocol() {
        scheduler.scheduleAtFixedRate(this::performAdaptiveGossip, 
                                    gossipInterval, gossipInterval, TimeUnit.MILLISECONDS);
                                    
        scheduler.scheduleAtFixedRate(this::performNetworkMaintenance, 
                                    30000, 30000, TimeUnit.MILLISECONDS);
    }
    
    private void performAdaptiveGossip() {
        gossipRounds.incrementAndGet();
        
        // Determine optimal gossip mode based on current conditions
        GossipMode optimalMode = determineOptimalGossipMode();
        
        switch (optimalMode) {
            case PUSH_ONLY:
                performPushGossip();
                pushRounds.incrementAndGet();
                break;
            case PULL_ONLY:
                performPullGossip();
                pullRounds.incrementAndGet();
                break;
            case PUSH_PULL:
                performHybridGossip();
                hybridRounds.incrementAndGet();
                break;
            case ADAPTIVE:
                performIntelligentGossip();
                break;
        }
        
        System.out.println("🔄 " + nodeId + " gossip round " + gossipRounds.get() + 
                         " using " + optimalMode + " mode");
    }
    
    private GossipMode determineOptimalGossipMode() {
        // Adaptive mode selection based on:
        // 1. Network congestion
        // 2. Data freshness
        // 3. Peer availability
        // 4. Transaction load
        
        double networkCongestion = estimateNetworkCongestion();
        double dataFreshness = estimateDataFreshness();
        int availablePeers = peers.size();
        int recentTransactions = getRecentTransactionCount();
        
        // High transaction load + fresh data = PUSH
        if (recentTransactions > 50 && dataFreshness > 0.8) {
            return GossipMode.PUSH_ONLY;
        }
        
        // Low transaction load + stale data = PULL
        if (recentTransactions < 10 && dataFreshness < 0.3) {
            return GossipMode.PULL_ONLY;
        }
        
        // Balanced conditions = PUSH_PULL
        if (networkCongestion < 0.5 && availablePeers >= 3) {
            return GossipMode.PUSH_PULL;
        }
        
        return GossipMode.ADAPTIVE;
    }
    
    private double estimateNetworkCongestion() {
        // Simple congestion estimation based on message exchange rate
        long messagesPerSecond = metrics.getMessagesExchanged() / 
                               Math.max(1, gossipRounds.get());
        
        // Normalize based on expected load for this tier
        double expectedLoad = getExpectedMessageLoad();
        return Math.min(1.0, messagesPerSecond / expectedLoad);
    }
    
    private double estimateDataFreshness() {
        if (transactionStore.isEmpty()) {
            return 0.0;
        }
        
        long currentTime = System.currentTimeMillis();
        long totalAge = 0;
        int count = 0;
        
        for (PaymentTransaction txn : transactionStore.values()) {
            totalAge += (currentTime - txn.getTimestamp());
            count++;
        }
        
        double avgAge = (double) totalAge / count;
        double maxAge = 300000; // 5 minutes
        
        return Math.max(0.0, 1.0 - (avgAge / maxAge));
    }
    
    private double getExpectedMessageLoad() {
        switch (tier) {
            case GATEWAY: return 20.0;
            case PROCESSOR: return 15.0;
            case VALIDATOR: return 10.0;
            case STORAGE: return 5.0;
            default: return 10.0;
        }
    }
    
    private int getRecentTransactionCount() {
        long cutoffTime = System.currentTimeMillis() - gossipInterval;
        
        return (int) transactionStore.values().stream()
                .filter(txn -> txn.getTimestamp() > cutoffTime)
                .count();
    }
    
    private void performPushGossip() {
        List<String> selectedPeers = selectOptimalPeers(maxPeersPerRound / 2);
        
        for (String peerId : selectedPeers) {
            GossipPayload payload = createPushPayload();
            sendGossipMessage(peerId, payload);
        }
    }
    
    private void performPullGossip() {
        List<String> selectedPeers = selectOptimalPeers(maxPeersPerRound / 2);
        
        for (String peerId : selectedPeers) {
            GossipPayload payload = createPullPayload();
            sendGossipMessage(peerId, payload);
        }
    }
    
    private void performHybridGossip() {
        List<String> allSelectedPeers = selectOptimalPeers(maxPeersPerRound);
        
        // Split peers for push and pull
        int splitPoint = allSelectedPeers.size() / 2;
        List<String> pushPeers = allSelectedPeers.subList(0, splitPoint);
        List<String> pullPeers = allSelectedPeers.subList(splitPoint, allSelectedPeers.size());
        
        // Perform push with some peers
        for (String peerId : pushPeers) {
            GossipPayload payload = createPushPayload();
            sendGossipMessage(peerId, payload);
        }
        
        // Perform pull with other peers
        for (String peerId : pullPeers) {
            GossipPayload payload = createPullPayload();
            sendGossipMessage(peerId, payload);
        }
    }
    
    private void performIntelligentGossip() {
        // Intelligent gossip that adapts per peer
        List<String> selectedPeers = selectOptimalPeers(maxPeersPerRound);
        
        for (String peerId : selectedPeers) {
            // Decide push or pull based on peer characteristics
            NodeTier peerTier = peerTiers.get(peerId);
            double peerWeight = peerWeights.getOrDefault(peerId, 1.0);
            
            GossipPayload payload;
            if (shouldPushToPeer(peerTier, peerWeight)) {
                payload = createPushPayload();
            } else {
                payload = createPullPayload();
            }
            
            sendGossipMessage(peerId, payload);
        }
    }
    
    private boolean shouldPushToPeer(NodeTier peerTier, double peerWeight) {
        // Push to higher-tier nodes (they need fresh data)
        // Pull from storage nodes (they have comprehensive data)
        
        switch (peerTier) {
            case GATEWAY:
                return tier != NodeTier.GATEWAY; // Push to gateways unless we're a gateway
            case PROCESSOR:
                return tier == NodeTier.GATEWAY || tier == NodeTier.VALIDATOR;
            case VALIDATOR:
                return tier == NodeTier.GATEWAY || tier == NodeTier.PROCESSOR;
            case STORAGE:
                return false; // Always pull from storage
            default:
                return peerWeight > 0.7; // Push to high-weight peers
        }
    }
    
    private void performUrgentGossip() {
        // Immediate gossip for urgent transactions
        List<String> allPeers = new ArrayList<>(peers);
        
        for (String peerId : allPeers) {
            GossipPayload payload = createUrgentPayload();
            sendGossipMessage(peerId, payload);
        }
    }
    
    private List<String> selectOptimalPeers(int maxPeers) {
        if (peers.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Weight-based peer selection
        List<Map.Entry<String, Double>> weightedPeers = new ArrayList<>();
        
        for (String peerId : peers) {
            double weight = calculatePeerWeight(peerId);
            weightedPeers.add(Map.entry(peerId, weight));
        }
        
        // Sort by weight (descending)
        weightedPeers.sort(Map.Entry.<String, Double>comparingByValue().reversed());
        
        // Select top peers with some randomness
        int targetCount = Math.min(maxPeers, weightedPeers.size());
        List<String> selected = new ArrayList<>();
        
        // Take top 70% by weight
        int deterministicCount = (int) (targetCount * 0.7);
        for (int i = 0; i < deterministicCount && i < weightedPeers.size(); i++) {
            selected.add(weightedPeers.get(i).getKey());
        }
        
        // Random selection for remaining
        List<String> remaining = new ArrayList<>();
        for (int i = deterministicCount; i < weightedPeers.size(); i++) {
            remaining.add(weightedPeers.get(i).getKey());
        }
        
        Collections.shuffle(remaining, random);
        int randomCount = targetCount - selected.size();
        for (int i = 0; i < randomCount && i < remaining.size(); i++) {
            selected.add(remaining.get(i));
        }
        
        return selected;
    }
    
    private double calculatePeerWeight(String peerId) {
        double baseWeight = peerWeights.getOrDefault(peerId, 1.0);
        NodeTier peerTier = peerTiers.get(peerId);
        
        // Tier-based weight adjustment
        double tierMultiplier = switch (peerTier) {
            case GATEWAY -> 1.2;    // Prefer gateways
            case PROCESSOR -> 1.1;  // Prefer processors
            case VALIDATOR -> 1.0;  // Neutral for validators
            case STORAGE -> 0.8;    // Lower preference for storage
        };
        
        // Version freshness factor
        Long peerVersion = versionVector.get(peerId);
        Long localVer = versionVector.get(nodeId);
        double freshnessFactor = 1.0;
        
        if (peerVersion != null && localVer != null) {
            if (peerVersion > localVer) {
                freshnessFactor = 1.3; // Prefer peers with newer data
            } else if (peerVersion < localVer * 0.8) {
                freshnessFactor = 0.7; // Lower preference for stale peers
            }
        }
        
        return baseWeight * tierMultiplier * freshnessFactor;
    }
    
    private GossipPayload createPushPayload() {
        GossipPayload payload = new GossipPayload(nodeId, GossipMode.PUSH_ONLY);
        
        // Add recent transactions
        List<PaymentTransaction> recentTxns = getRecentTransactions(payloadSizeLimit);
        for (PaymentTransaction txn : recentTxns) {
            payload.addTransaction(txn);
        }
        
        // Add version vector
        for (Map.Entry<String, Long> entry : versionVector.entrySet()) {
            payload.addVersionInfo(entry.getKey(), entry.getValue());
        }
        
        return payload;
    }
    
    private GossipPayload createPullPayload() {
        GossipPayload payload = new GossipPayload(nodeId, GossipMode.PULL_ONLY);
        
        // Add version vector to show what we have
        for (Map.Entry<String, Long> entry : versionVector.entrySet()) {
            payload.addVersionInfo(entry.getKey(), entry.getValue());
        }
        
        // Add specific keys we're interested in
        Set<String> requestedKeys = getRequestedTransactionKeys();
        for (String key : requestedKeys) {
            payload.addRequestedKey(key);
        }
        
        return payload;
    }
    
    private GossipPayload createUrgentPayload() {
        GossipPayload payload = new GossipPayload(nodeId, GossipMode.PUSH_ONLY);
        
        // Add only urgent/high-value transactions
        List<PaymentTransaction> urgentTxns = getUrgentTransactions();
        for (PaymentTransaction txn : urgentTxns) {
            payload.addTransaction(txn);
        }
        
        return payload;
    }
    
    private List<PaymentTransaction> getRecentTransactions(int limit) {
        return transactionStore.values().stream()
                .sorted((t1, t2) -> Long.compare(t2.getTimestamp(), t1.getTimestamp()))
                .limit(limit)
                .toList();
    }
    
    private Set<String> getRequestedTransactionKeys() {
        // In a real system, this would be based on specific business logic
        // For simulation, return empty set
        return new HashSet<>();
    }
    
    private List<PaymentTransaction> getUrgentTransactions() {
        return transactionStore.values().stream()
                .filter(txn -> txn.getAmount() > 100000 || 
                              "FAILED".equals(txn.getStatus()) ||
                              "SUSPICIOUS".equals(txn.getStatus()))
                .sorted((t1, t2) -> Long.compare(t2.getTimestamp(), t1.getTimestamp()))
                .limit(10)
                .toList();
    }
    
    private void sendGossipMessage(String peerId, GossipPayload payload) {
        // Simulate network transmission
        int messageSize = payload.getPayloadSize() * 100; // Rough estimate in bytes
        metrics.recordMessage(nodeId, messageSize);
        
        // Simulate processing delay
        scheduler.schedule(() -> {
            processGossipPayload(payload, peerId);
        }, random.nextInt(200), TimeUnit.MILLISECONDS);
        
        System.out.println("📤 " + nodeId + " → " + peerId + ": " + payload.getMode() + 
                         " (" + payload.getPayloadSize() + " items)");
    }
    
    public void processGossipPayload(GossipPayload payload, String fromPeer) {
        metrics.recordMessage(fromPeer, payload.getPayloadSize() * 100);
        
        System.out.println("📥 " + nodeId + " ← " + fromPeer + ": " + payload.getMode() + 
                         " (" + payload.getPayloadSize() + " items)");
        
        // Process based on gossip mode
        switch (payload.getMode()) {
            case PUSH_ONLY:
                processPushPayload(payload, fromPeer);
                break;
            case PULL_ONLY:
                processPullPayload(payload, fromPeer);
                break;
            default:
                // Handle other modes
                processPushPayload(payload, fromPeer);
        }
        
        // Update version vector
        for (Map.Entry<String, Long> entry : payload.getVersionVector().entrySet()) {
            String nodeId = entry.getKey();
            Long version = entry.getValue();
            
            Long currentVersion = versionVector.get(nodeId);
            if (currentVersion == null || version > currentVersion) {
                versionVector.put(nodeId, version);
            }
        }
    }
    
    private void processPushPayload(GossipPayload payload, String fromPeer) {
        int updatedCount = 0;
        
        for (PaymentTransaction transaction : payload.getTransactions().values()) {
            String txnId = transaction.getTransactionId();
            
            if (!transactionStore.containsKey(txnId)) {
                transactionStore.put(txnId, transaction);
                updatedCount++;
                
                System.out.println("💾 " + nodeId + " stored new transaction: " + txnId);
            }
        }
        
        if (updatedCount > 0) {
            localVersion.addAndGet(updatedCount);
            versionVector.put(nodeId, localVersion.get());
        }
    }
    
    private void processPullPayload(GossipPayload payload, String fromPeer) {
        // Respond to pull request by sending relevant data
        GossipPayload response = createPushPayload();
        
        // Send response
        scheduler.schedule(() -> {
            sendGossipMessage(fromPeer, response);
        }, 100, TimeUnit.MILLISECONDS);
    }
    
    private void performNetworkMaintenance() {
        // Clean old transactions
        cleanOldTransactions();
        
        // Update peer weights based on performance
        updatePeerWeights();
        
        // Log statistics
        logPerformanceMetrics();
    }
    
    private void cleanOldTransactions() {
        long cutoffTime = System.currentTimeMillis() - 3600000; // 1 hour
        
        transactionStore.entrySet().removeIf(entry -> 
            entry.getValue().getTimestamp() < cutoffTime
        );
    }
    
    private void updatePeerWeights() {
        // Update peer weights based on responsiveness and data quality
        // This is simplified for the simulation
        for (String peerId : peers) {
            double currentWeight = peerWeights.getOrDefault(peerId, 1.0);
            double newWeight = currentWeight * (0.95 + random.nextDouble() * 0.1);
            peerWeights.put(peerId, Math.max(0.1, Math.min(2.0, newWeight)));
        }
    }
    
    private void logPerformanceMetrics() {
        if (gossipRounds.get() % 10 == 0) { // Log every 10 rounds
            System.out.println("📊 " + nodeId + " metrics: " +
                             "Rounds=" + gossipRounds.get() + 
                             ", Transactions=" + transactionStore.size() +
                             ", Messages=" + metrics.getMessagesExchanged());
        }
    }
    
    public Map<String, Object> getDetailedMetrics() {
        Map<String, Object> detailedMetrics = new HashMap<>();
        
        detailedMetrics.put("nodeId", nodeId);
        detailedMetrics.put("tier", tier);
        detailedMetrics.put("transactionCount", transactionStore.size());
        detailedMetrics.put("gossipRounds", gossipRounds.get());
        detailedMetrics.put("pushRounds", pushRounds.get());
        detailedMetrics.put("pullRounds", pullRounds.get());
        detailedMetrics.put("hybridRounds", hybridRounds.get());
        detailedMetrics.put("messagesExchanged", metrics.getMessagesExchanged());
        detailedMetrics.put("bytesTransferred", metrics.getBytesTransferred());
        detailedMetrics.put("activeConnections", metrics.getActiveConnections());
        detailedMetrics.put("peerCount", peers.size());
        
        return detailedMetrics;
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
        System.out.println("🇮🇳 Paytm Hybrid Gossip Protocol Simulation");
        System.out.println("=" + "=".repeat(50));
        
        // Create Paytm payment network nodes
        Map<String, HybridGossipProtocol> nodes = new HashMap<>();
        
        // Gateway nodes
        nodes.put("gateway-mumbai", new HybridGossipProtocol("gateway-mumbai", "West", NodeTier.GATEWAY));
        nodes.put("gateway-delhi", new HybridGossipProtocol("gateway-delhi", "North", NodeTier.GATEWAY));
        
        // Processor nodes
        nodes.put("processor-01", new HybridGossipProtocol("processor-01", "Central", NodeTier.PROCESSOR));
        nodes.put("processor-02", new HybridGossipProtocol("processor-02", "Central", NodeTier.PROCESSOR));
        
        // Validator nodes
        nodes.put("validator-01", new HybridGossipProtocol("validator-01", "South", NodeTier.VALIDATOR));
        nodes.put("validator-02", new HybridGossipProtocol("validator-02", "East", NodeTier.VALIDATOR));
        
        // Storage nodes
        nodes.put("storage-01", new HybridGossipProtocol("storage-01", "Central", NodeTier.STORAGE));
        nodes.put("storage-02", new HybridGossipProtocol("storage-02", "Central", NodeTier.STORAGE));
        
        // Create hierarchical network topology
        String[][] connections = {
            // Gateways connect to processors
            {"gateway-mumbai", "processor-01", "1.0"},
            {"gateway-delhi", "processor-02", "1.0"},
            {"gateway-mumbai", "processor-02", "0.8"},
            {"gateway-delhi", "processor-01", "0.8"},
            
            // Processors connect to validators and storage
            {"processor-01", "validator-01", "0.9"},
            {"processor-01", "storage-01", "1.0"},
            {"processor-02", "validator-02", "0.9"},
            {"processor-02", "storage-02", "1.0"},
            
            // Cross connections for redundancy
            {"processor-01", "processor-02", "0.7"},
            {"validator-01", "validator-02", "0.6"},
            {"storage-01", "storage-02", "1.0"},
            
            // Validators connect to storage
            {"validator-01", "storage-01", "0.8"},
            {"validator-02", "storage-02", "0.8"}
        };
        
        for (String[] conn : connections) {
            String node1 = conn[0];
            String node2 = conn[1];
            double weight = Double.parseDouble(conn[2]);
            
            if (nodes.containsKey(node1) && nodes.containsKey(node2)) {
                HybridGossipProtocol n1 = nodes.get(node1);
                HybridGossipProtocol n2 = nodes.get(node2);
                
                n1.addPeer(node2, n2.tier, weight);
                n2.addPeer(node1, n1.tier, weight);
            }
        }
        
        System.out.println("Paytm network topology created. Starting transaction processing...\n");
        
        // Simulate payment transactions
        HybridGossipProtocol gateway1 = nodes.get("gateway-mumbai");
        HybridGossipProtocol gateway2 = nodes.get("gateway-delhi");
        HybridGossipProtocol processor1 = nodes.get("processor-01");
        
        // Generate sample transactions
        String[] merchants = {"AMAZON", "FLIPKART", "SWIGGY", "ZOMATO", "OLA", "UBER"};
        String[] statuses = {"SUCCESS", "PENDING", "FAILED", "PROCESSING"};
        
        for (int i = 0; i < 20; i++) {
            String merchant = merchants[i % merchants.length];
            String status = statuses[i % statuses.length];
            double amount = 100 + (i * 150.0);
            
            PaymentTransaction txn = new PaymentTransaction(
                "TXN_" + String.format("%04d", i + 1),
                merchant,
                "CUST_" + String.format("%03d", (i % 50) + 1),
                amount,
                "INR",
                status,
                "gateway-mumbai"
            );
            
            if (i % 3 == 0) {
                gateway1.processTransaction(txn);
            } else if (i % 3 == 1) {
                gateway2.processTransaction(txn);
            } else {
                processor1.processTransaction(txn);
            }
            
            Thread.sleep(200); // Small delay between transactions
        }
        
        // Let the network run and gossip
        Thread.sleep(15000);
        
        // Print final statistics
        System.out.println("\n📊 Final Network Statistics:");
        
        for (Map.Entry<String, HybridGossipProtocol> entry : nodes.entrySet()) {
            Map<String, Object> metrics = entry.getValue().getDetailedMetrics();
            System.out.printf("  %s (%s): Txns=%d, Rounds=%d, Messages=%d%n",
                            entry.getKey(),
                            metrics.get("tier"),
                            metrics.get("transactionCount"),
                            metrics.get("gossipRounds"),
                            metrics.get("messagesExchanged"));
        }
        
        // Calculate convergence metrics
        long totalMessages = nodes.values().stream()
            .mapToLong(n -> n.metrics.getMessagesExchanged())
            .sum();
        
        int totalTransactions = nodes.values().stream()
            .mapToInt(n -> n.transactionStore.size())
            .sum();
        
        System.out.println("\n📈 Network Summary:");
        System.out.println("  Total messages exchanged: " + totalMessages);
        System.out.println("  Total transactions stored: " + totalTransactions);
        System.out.println("  Average transactions per node: " + (totalTransactions / nodes.size()));
        
        // Cleanup
        for (HybridGossipProtocol node : nodes.values()) {
            node.shutdown();
        }
        
        System.out.println("\nHybrid gossip simulation completed!");
    }
}