/**
 * Byzantine Fault Tolerance Implementation in Java
 * Production-ready implementation for enterprise distributed systems
 * 
 * यह implementation enterprise-grade Byzantine fault tolerance को Java में दिखाती है
 * जैसे कि Apache Kafka, Apache Cassandra, और enterprise blockchain में इस्तेमाल होती है
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.Instant;
import java.math.BigDecimal;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;

// Enums for Byzantine consensus
enum NodeType {
    HONEST, BYZANTINE, COORDINATOR
}

enum MessageType {
    REQUEST, PREPARE, COMMIT, VIEW_CHANGE, NEW_VIEW
}

enum ConsensusPhase {
    REQUEST_PHASE, PREPARE_PHASE, COMMIT_PHASE, FINALIZED
}

// Byzantine transaction class
class ByzantineTransaction {
    @JsonProperty
    private final String transactionId;
    
    @JsonProperty
    private final String sender;
    
    @JsonProperty
    private final String receiver;
    
    @JsonProperty
    private final BigDecimal amount;
    
    @JsonProperty
    private final long timestamp;
    
    @JsonProperty
    private final String signature;
    
    public ByzantineTransaction(String transactionId, String sender, String receiver, 
                               BigDecimal amount, String signature) {
        this.transactionId = transactionId;
        this.sender = sender;
        this.receiver = receiver;
        this.amount = amount;
        this.timestamp = Instant.now().toEpochMilli();
        this.signature = signature != null ? signature : generateSignature();
    }
    
    private String generateSignature() {
        try {
            String data = transactionId + sender + receiver + amount.toString() + timestamp;
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(data.getBytes());
            return bytesToHex(hash).substring(0, 16);
        } catch (NoSuchAlgorithmException e) {
            return "default_signature";
        }
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public String getSender() { return sender; }
    public String getReceiver() { return receiver; }
    public BigDecimal getAmount() { return amount; }
    public long getTimestamp() { return timestamp; }
    public String getSignature() { return signature; }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        ByzantineTransaction that = (ByzantineTransaction) obj;
        return Objects.equals(transactionId, that.transactionId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(transactionId);
    }
}

// Byzantine consensus message
class ByzantineMessage {
    @JsonProperty
    private final MessageType messageType;
    
    @JsonProperty
    private final String senderId;
    
    @JsonProperty
    private final int viewNumber;
    
    @JsonProperty
    private final int sequenceNumber;
    
    @JsonProperty
    private final ByzantineTransaction transaction;
    
    @JsonProperty
    private final long timestamp;
    
    @JsonProperty
    private final String messageHash;
    
    public ByzantineMessage(MessageType messageType, String senderId, int viewNumber,
                           int sequenceNumber, ByzantineTransaction transaction) {
        this.messageType = messageType;
        this.senderId = senderId;
        this.viewNumber = viewNumber;
        this.sequenceNumber = sequenceNumber;
        this.transaction = transaction;
        this.timestamp = Instant.now().toEpochMilli();
        this.messageHash = generateMessageHash();
    }
    
    private String generateMessageHash() {
        try {
            String data = messageType + senderId + viewNumber + sequenceNumber + 
                         (transaction != null ? transaction.getTransactionId() : "") + timestamp;
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(data.getBytes());
            return bytesToHex(hash).substring(0, 12);
        } catch (NoSuchAlgorithmException e) {
            return "default_hash";
        }
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte b : bytes) {
            result.append(String.format("%02x", b));
        }
        return result.toString();
    }
    
    // Getters
    public MessageType getMessageType() { return messageType; }
    public String getSenderId() { return senderId; }
    public int getViewNumber() { return viewNumber; }
    public int getSequenceNumber() { return sequenceNumber; }
    public ByzantineTransaction getTransaction() { return transaction; }
    public long getTimestamp() { return timestamp; }
    public String getMessageHash() { return messageHash; }
}

/**
 * Main Byzantine Fault Tolerance Node Implementation
 * बिल्कुल enterprise distributed systems की तरह Byzantine nodes को handle करता है
 */
public class ByzantineFaultTolerance {
    
    // Node configuration
    private final String nodeId;
    private final NodeType nodeType;
    private final List<String> allNodes;
    private final int f; // Maximum Byzantine nodes tolerated
    
    // Byzantine state
    private volatile int currentView;
    private volatile ConsensusPhase currentPhase;
    private final AtomicInteger sequenceNumber;
    
    // Message logs
    private final ConcurrentHashMap<Integer, ByzantineMessage> requestLog;
    private final ConcurrentHashMap<Integer, ConcurrentHashMap<String, ByzantineMessage>> prepareLog;
    private final ConcurrentHashMap<Integer, ConcurrentHashMap<String, ByzantineMessage>> commitLog;
    
    // State machine
    private final ConcurrentHashMap<String, BigDecimal> accountBalances;
    private final Set<String> processedTransactions;
    
    // Network simulation
    private final ConcurrentHashMap<String, ByzantineFaultTolerance> network;
    private final ExecutorService executorService;
    private final ScheduledExecutorService scheduledExecutor;
    
    // Byzantine behavior parameters
    private final Random random;
    private final double maliciousProbability;
    
    // Performance metrics
    private final AtomicInteger transactionsProcessed;
    private final AtomicInteger byzantineAttacksDetected;
    private final AtomicInteger consensusRounds;
    
    // JSON serialization
    private final ObjectMapper objectMapper;
    
    public ByzantineFaultTolerance(String nodeId, List<String> allNodes, NodeType nodeType) {
        this.nodeId = nodeId;
        this.nodeType = nodeType;
        this.allNodes = new ArrayList<>(allNodes);
        this.f = (allNodes.size() - 1) / 3; // Byzantine fault tolerance: f < n/3
        
        // Initialize state
        this.currentView = 0;
        this.currentPhase = ConsensusPhase.REQUEST_PHASE;
        this.sequenceNumber = new AtomicInteger(0);
        
        // Initialize logs
        this.requestLog = new ConcurrentHashMap<>();
        this.prepareLog = new ConcurrentHashMap<>();
        this.commitLog = new ConcurrentHashMap<>();
        
        // Initialize state machine
        this.accountBalances = new ConcurrentHashMap<>();
        this.processedTransactions = ConcurrentHashMap.newKeySet();
        
        // Initialize network
        this.network = new ConcurrentHashMap<>();
        this.executorService = Executors.newCachedThreadPool();
        this.scheduledExecutor = Executors.newScheduledThreadPool(4);
        
        // Initialize Byzantine parameters
        this.random = new Random();
        this.maliciousProbability = (nodeType == NodeType.BYZANTINE) ? 0.7 : 0.0;
        
        // Initialize metrics
        this.transactionsProcessed = new AtomicInteger(0);
        this.byzantineAttacksDetected = new AtomicInteger(0);
        this.consensusRounds = new AtomicInteger(0);
        
        // JSON mapper
        this.objectMapper = new ObjectMapper();
        
        System.out.printf("🏛️ Byzantine node %s (%s) initialized (f=%d)%n", 
                         nodeId, nodeType, f);
        
        if (nodeType == NodeType.BYZANTINE) {
            System.out.printf("⚠️ WARNING: Node %s configured as Byzantine%n", nodeId);
        }
    }
    
    public void setNetwork(ConcurrentHashMap<String, ByzantineFaultTolerance> network) {
        this.network.putAll(network);
    }
    
    public void createAccount(String accountId, BigDecimal initialBalance) {
        accountBalances.put(accountId, initialBalance);
        System.out.printf("💳 Node %s: Created account %s with balance ₹%s%n", 
                         nodeId, accountId, initialBalance);
    }
    
    public BigDecimal getBalance(String accountId) {
        return accountBalances.getOrDefault(accountId, BigDecimal.ZERO);
    }
    
    /**
     * Submit transaction request to the Byzantine network
     */
    public CompletableFuture<Boolean> submitTransaction(ByzantineTransaction transaction) {
        return CompletableFuture.supplyAsync(() -> {
            System.out.printf("🔄 Node %s: Submitting transaction %s%n", 
                             nodeId, transaction.getTransactionId());
            
            // Validate transaction locally
            if (!validateTransactionLocally(transaction)) {
                System.out.printf("❌ Local validation failed for transaction %s%n", 
                                 transaction.getTransactionId());
                return false;
            }
            
            // Start Byzantine consensus
            return startByzantineConsensus(transaction);
        }, executorService);
    }
    
    private boolean validateTransactionLocally(ByzantineTransaction transaction) {
        // Check sender balance
        BigDecimal senderBalance = getBalance(transaction.getSender());
        if (senderBalance.compareTo(transaction.getAmount()) < 0) {
            System.out.printf("❌ Insufficient balance: %s < %s%n", senderBalance, transaction.getAmount());
            return false;
        }
        
        // Check for duplicate transaction
        if (processedTransactions.contains(transaction.getTransactionId())) {
            System.out.printf("❌ Duplicate transaction: %s%n", transaction.getTransactionId());
            return false;
        }
        
        // Additional validation
        if (transaction.getAmount().compareTo(BigDecimal.ZERO) <= 0) {
            System.out.printf("❌ Invalid amount: %s%n", transaction.getAmount());
            return false;
        }
        
        return true;
    }
    
    private boolean startByzantineConsensus(ByzantineTransaction transaction) {
        int currentSeq = sequenceNumber.incrementAndGet();
        consensusRounds.incrementAndGet();
        
        System.out.printf("🎯 Starting Byzantine consensus round %d for transaction %s%n", 
                         currentSeq, transaction.getTransactionId());
        
        // Phase 1: Request
        ByzantineMessage requestMsg = new ByzantineMessage(
            MessageType.REQUEST,
            nodeId,
            currentView,
            currentSeq,
            transaction
        );
        
        // Store request
        requestLog.put(currentSeq, requestMsg);
        
        // Broadcast request to all nodes
        broadcastMessage(requestMsg);
        
        // Wait for consensus completion
        try {
            Thread.sleep(2000); // Wait for all phases
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
        
        // Check if consensus achieved
        return checkConsensusAchieved(currentSeq);
    }
    
    private void broadcastMessage(ByzantineMessage message) {
        for (String targetNodeId : allNodes) {
            if (!targetNodeId.equals(nodeId) && network.containsKey(targetNodeId)) {
                ByzantineFaultTolerance targetNode = network.get(targetNodeId);
                
                // Byzantine behavior: might send corrupted messages
                ByzantineMessage messageToSend = message;
                if (nodeType == NodeType.BYZANTINE && random.nextDouble() < maliciousProbability) {
                    messageToSend = corruptMessage(message);
                    System.out.printf("💀 Byzantine node %s: Sending corrupted message to %s%n", 
                                     nodeId, targetNodeId);
                }
                
                executorService.submit(() -> targetNode.receiveMessage(messageToSend));
            }
        }
    }
    
    private ByzantineMessage corruptMessage(ByzantineMessage original) {
        // Create corrupted transaction
        ByzantineTransaction originalTx = original.getTransaction();
        if (originalTx != null) {
            ByzantineTransaction corruptedTx = new ByzantineTransaction(
                originalTx.getTransactionId() + "_CORRUPTED",
                originalTx.getSender(),
                nodeId, // Divert to self
                originalTx.getAmount().multiply(BigDecimal.valueOf(2)), // Double the amount
                "FAKE_SIGNATURE"
            );
            
            return new ByzantineMessage(
                original.getMessageType(),
                original.getSenderId(),
                original.getViewNumber(),
                original.getSequenceNumber(),
                corruptedTx
            );
        }
        
        return original;
    }
    
    public void receiveMessage(ByzantineMessage message) {
        try {
            switch (message.getMessageType()) {
                case REQUEST:
                    handleRequestMessage(message);
                    break;
                case PREPARE:
                    handlePrepareMessage(message);
                    break;
                case COMMIT:
                    handleCommitMessage(message);
                    break;
                default:
                    System.out.printf("Unknown message type: %s%n", message.getMessageType());
            }
        } catch (Exception e) {
            System.out.printf("❌ Error processing message: %s%n", e.getMessage());
        }
    }
    
    private void handleRequestMessage(ByzantineMessage message) {
        int sequenceNum = message.getSequenceNumber();
        ByzantineTransaction transaction = message.getTransaction();
        
        System.out.printf("📨 Node %s: Received request for sequence %d%n", nodeId, sequenceNum);
        
        // Validate the transaction
        boolean isValid = validateByzantineTransaction(transaction, message);
        
        // Byzantine behavior: might randomly validate/invalidate
        if (nodeType == NodeType.BYZANTINE && random.nextDouble() < maliciousProbability) {
            isValid = random.nextBoolean();
            System.out.printf("💀 Byzantine node %s: Random validation result: %s%n", nodeId, isValid);
        }
        
        if (isValid) {
            // Store request and send prepare
            requestLog.put(sequenceNum, message);
            sendPrepareMessage(sequenceNum, transaction);
        } else {
            System.out.printf("❌ Node %s: Invalid transaction in request %d%n", nodeId, sequenceNum);
            byzantineAttacksDetected.incrementAndGet();
        }
    }
    
    private boolean validateByzantineTransaction(ByzantineTransaction transaction, ByzantineMessage message) {
        if (transaction == null) {
            return false;
        }
        
        // Check for Byzantine indicators
        if (transaction.getTransactionId().contains("CORRUPTED")) {
            System.out.printf("🚨 Byzantine attack detected: Corrupted transaction ID%n");
            return false;
        }
        
        if (transaction.getSignature().equals("FAKE_SIGNATURE")) {
            System.out.printf("🚨 Byzantine attack detected: Fake signature%n");
            return false;
        }
        
        // Check if receiver is trying to steal funds
        if (transaction.getReceiver().equals(message.getSenderId()) && 
            !transaction.getSender().equals(message.getSenderId())) {
            System.out.printf("🚨 Byzantine attack detected: Fund diversion%n");
            return false;
        }
        
        // Check for excessive amounts
        if (transaction.getAmount().compareTo(BigDecimal.valueOf(1000000)) > 0) {
            System.out.printf("🚨 Byzantine attack detected: Excessive amount%n");
            return false;
        }
        
        return validateTransactionLocally(transaction);
    }
    
    private void sendPrepareMessage(int sequenceNumber, ByzantineTransaction transaction) {
        ByzantineMessage prepareMsg = new ByzantineMessage(
            MessageType.PREPARE,
            nodeId,
            currentView,
            sequenceNumber,
            transaction
        );
        
        // Store our prepare message
        prepareLog.computeIfAbsent(sequenceNumber, k -> new ConcurrentHashMap<>())
                  .put(nodeId, prepareMsg);
        
        // Broadcast prepare
        broadcastMessage(prepareMsg);
        
        System.out.printf("📤 Node %s: Sent prepare for sequence %d%n", nodeId, sequenceNumber);
    }
    
    private void handlePrepareMessage(ByzantineMessage message) {
        int sequenceNum = message.getSequenceNumber();
        String senderId = message.getSenderId();
        
        System.out.printf("📨 Node %s: Received prepare from %s for sequence %d%n", 
                         nodeId, senderId, sequenceNum);
        
        // Store prepare message
        prepareLog.computeIfAbsent(sequenceNum, k -> new ConcurrentHashMap<>())
                  .put(senderId, message);
        
        // Check if we have enough prepare messages (2f)
        if (checkPrepared(sequenceNum)) {
            System.out.printf("✅ Node %s: Prepared for sequence %d%n", nodeId, sequenceNum);
            sendCommitMessage(sequenceNum, message.getTransaction());
        }
    }
    
    private boolean checkPrepared(int sequenceNumber) {
        if (!requestLog.containsKey(sequenceNumber)) {
            return false;
        }
        
        Map<String, ByzantineMessage> prepares = prepareLog.get(sequenceNumber);
        if (prepares == null) {
            return false;
        }
        
        // Count matching prepare messages
        ByzantineTransaction requestTx = requestLog.get(sequenceNumber).getTransaction();
        int matchingPrepares = 0;
        
        for (ByzantineMessage prepare : prepares.values()) {
            if (transactionsMatch(prepare.getTransaction(), requestTx)) {
                matchingPrepares++;
            }
        }
        
        // Need 2f prepare messages
        return matchingPrepares >= 2 * f;
    }
    
    private void sendCommitMessage(int sequenceNumber, ByzantineTransaction transaction) {
        ByzantineMessage commitMsg = new ByzantineMessage(
            MessageType.COMMIT,
            nodeId,
            currentView,
            sequenceNumber,
            transaction
        );
        
        // Store our commit message
        commitLog.computeIfAbsent(sequenceNumber, k -> new ConcurrentHashMap<>())
                 .put(nodeId, commitMsg);
        
        // Broadcast commit
        broadcastMessage(commitMsg);
        
        System.out.printf("📤 Node %s: Sent commit for sequence %d%n", nodeId, sequenceNumber);
    }
    
    private void handleCommitMessage(ByzantineMessage message) {
        int sequenceNum = message.getSequenceNumber();
        String senderId = message.getSenderId();
        
        System.out.printf("📨 Node %s: Received commit from %s for sequence %d%n", 
                         nodeId, senderId, sequenceNum);
        
        // Store commit message
        commitLog.computeIfAbsent(sequenceNum, k -> new ConcurrentHashMap<>())
                 .put(senderId, message);
        
        // Check if we can commit
        if (checkCommitted(sequenceNum)) {
            executeTransaction(sequenceNum);
        }
    }
    
    private boolean checkCommitted(int sequenceNumber) {
        if (!requestLog.containsKey(sequenceNumber) || !checkPrepared(sequenceNumber)) {
            return false;
        }
        
        Map<String, ByzantineMessage> commits = commitLog.get(sequenceNumber);
        if (commits == null) {
            return false;
        }
        
        // Count matching commit messages
        ByzantineTransaction requestTx = requestLog.get(sequenceNumber).getTransaction();
        int matchingCommits = 0;
        
        for (ByzantineMessage commit : commits.values()) {
            if (transactionsMatch(commit.getTransaction(), requestTx)) {
                matchingCommits++;
            }
        }
        
        // Need 2f+1 commit messages
        return matchingCommits >= 2 * f + 1;
    }
    
    private boolean transactionsMatch(ByzantineTransaction tx1, ByzantineTransaction tx2) {
        if (tx1 == null || tx2 == null) {
            return tx1 == tx2;
        }
        
        return Objects.equals(tx1.getTransactionId(), tx2.getTransactionId()) &&
               Objects.equals(tx1.getSender(), tx2.getSender()) &&
               Objects.equals(tx1.getReceiver(), tx2.getReceiver()) &&
               tx1.getAmount().compareTo(tx2.getAmount()) == 0;
    }
    
    private void executeTransaction(int sequenceNumber) {
        ByzantineMessage request = requestLog.get(sequenceNumber);
        if (request == null) {
            return;
        }
        
        ByzantineTransaction transaction = request.getTransaction();
        if (transaction == null) {
            return;
        }
        
        // Check if already executed
        if (processedTransactions.contains(transaction.getTransactionId())) {
            return;
        }
        
        // Execute the transaction
        String sender = transaction.getSender();
        String receiver = transaction.getReceiver();
        BigDecimal amount = transaction.getAmount();
        
        // Debit sender
        BigDecimal senderBalance = accountBalances.getOrDefault(sender, BigDecimal.ZERO);
        accountBalances.put(sender, senderBalance.subtract(amount));
        
        // Credit receiver
        BigDecimal receiverBalance = accountBalances.getOrDefault(receiver, BigDecimal.ZERO);
        accountBalances.put(receiver, receiverBalance.add(amount));
        
        // Mark as processed
        processedTransactions.add(transaction.getTransactionId());
        transactionsProcessed.incrementAndGet();
        
        System.out.printf("🎯 Node %s: Executed transaction %s (sequence %d)%n", 
                         nodeId, transaction.getTransactionId(), sequenceNumber);
        System.out.printf("   %s: ₹%s → ₹%s%n", sender, senderBalance, accountBalances.get(sender));
        System.out.printf("   %s: ₹%s → ₹%s%n", receiver, receiverBalance, accountBalances.get(receiver));
    }
    
    private boolean checkConsensusAchieved(int sequenceNumber) {
        return processedTransactions.contains(
            requestLog.get(sequenceNumber).getTransaction().getTransactionId()
        );
    }
    
    public Map<String, Object> getNodeStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("nodeId", nodeId);
        status.put("nodeType", nodeType.name());
        status.put("currentView", currentView);
        status.put("sequenceNumber", sequenceNumber.get());
        status.put("transactionsProcessed", transactionsProcessed.get());
        status.put("byzantineAttacksDetected", byzantineAttacksDetected.get());
        status.put("consensusRounds", consensusRounds.get());
        status.put("accountCount", accountBalances.size());
        
        BigDecimal totalBalance = accountBalances.values().stream()
                                                 .reduce(BigDecimal.ZERO, BigDecimal::add);
        status.put("totalBalance", totalBalance);
        
        return status;
    }
    
    public Map<String, BigDecimal> getAllBalances() {
        return new HashMap<>(accountBalances);
    }
    
    public void shutdown() {
        executorService.shutdown();
        scheduledExecutor.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
            if (!scheduledExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduledExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * Main simulation method
     */
    public static void main(String[] args) {
        System.out.println("🇮🇳 Byzantine Fault Tolerance Java Implementation");
        System.out.println("🏦 Enterprise Banking Network with Byzantine Nodes");
        System.out.println("=".repeat(70));
        
        // Create Byzantine network
        List<String> nodeIds = Arrays.asList(
            "bank-sbi", "bank-hdfc", "bank-icici", "bank-axis", "malicious-node"
        );
        
        // Initialize nodes
        Map<String, ByzantineFaultTolerance> network = new HashMap<>();
        for (int i = 0; i < nodeIds.size(); i++) {
            String nodeId = nodeIds.get(i);
            NodeType nodeType = (i == 4) ? NodeType.BYZANTINE : NodeType.HONEST;
            network.put(nodeId, new ByzantineFaultTolerance(nodeId, nodeIds, nodeType));
        }
        
        // Set network connections
        ConcurrentHashMap<String, ByzantineFaultTolerance> concurrentNetwork = 
            new ConcurrentHashMap<>(network);
        for (ByzantineFaultTolerance node : network.values()) {
            node.setNetwork(concurrentNetwork);
        }
        
        try {
            // Create accounts
            System.out.println("\n💳 Setting up customer accounts...");
            for (ByzantineFaultTolerance node : network.values()) {
                if (node.nodeType != NodeType.BYZANTINE) {
                    node.createAccount("customer:rahul", BigDecimal.valueOf(50000));
                    node.createAccount("customer:priya", BigDecimal.valueOf(75000));
                    node.createAccount("merchant:amazon", BigDecimal.valueOf(10000));
                }
            }
            
            // Submit transactions
            System.out.println("\n💸 Processing transactions through Byzantine consensus...");
            
            ByzantineFaultTolerance primaryNode = network.get("bank-sbi");
            
            List<ByzantineTransaction> transactions = Arrays.asList(
                new ByzantineTransaction("TXN001", "customer:rahul", "customer:priya", 
                                        BigDecimal.valueOf(15000), null),
                new ByzantineTransaction("TXN002", "customer:priya", "merchant:amazon", 
                                        BigDecimal.valueOf(8000), null),
                new ByzantineTransaction("TXN003", "merchant:amazon", "customer:rahul", 
                                        BigDecimal.valueOf(2000), null)
            );
            
            // Process transactions
            List<CompletableFuture<Boolean>> futures = new ArrayList<>();
            for (ByzantineTransaction transaction : transactions) {
                CompletableFuture<Boolean> future = primaryNode.submitTransaction(transaction);
                futures.add(future);
                Thread.sleep(1000);
            }
            
            // Wait for all transactions
            CompletableFuture<Void> allOf = CompletableFuture.allOf(
                futures.toArray(new CompletableFuture[0])
            );
            allOf.get(30, TimeUnit.SECONDS);
            
            // Wait for consensus completion
            Thread.sleep(5000);
            
            // Show results
            System.out.println("\n📊 Final Network State:");
            System.out.println("=".repeat(50));
            
            boolean consistent = true;
            Map<String, BigDecimal> referenceBalances = null;
            
            for (ByzantineFaultTolerance node : network.values()) {
                Map<String, Object> status = node.getNodeStatus();
                
                System.out.printf("\n🏦 %s (%s):%n", 
                                 node.nodeId, status.get("nodeType"));
                System.out.printf("   Transactions processed: %s%n", status.get("transactionsProcessed"));
                System.out.printf("   Byzantine attacks detected: %s%n", status.get("byzantineAttacksDetected"));
                System.out.printf("   Consensus rounds: %s%n", status.get("consensusRounds"));
                System.out.printf("   Total balance: ₹%s%n", status.get("totalBalance"));
                
                // Show account balances
                Map<String, BigDecimal> balances = node.getAllBalances();
                System.out.println("   Account balances:");
                for (Map.Entry<String, BigDecimal> entry : balances.entrySet()) {
                    System.out.printf("     %s: ₹%s%n", entry.getKey(), entry.getValue());
                }
                
                // Check consistency (only among honest nodes)
                if (node.nodeType != NodeType.BYZANTINE) {
                    if (referenceBalances == null) {
                        referenceBalances = balances;
                    } else if (!referenceBalances.equals(balances)) {
                        consistent = false;
                    }
                }
            }
            
            // Verify Byzantine fault tolerance
            System.out.println("\n🔍 Byzantine Fault Tolerance Verification:");
            if (consistent) {
                System.out.println("✅ All honest nodes have consistent state!");
                System.out.println("🛡️ Network successfully tolerated Byzantine node!");
            } else {
                System.out.println("❌ Inconsistency detected among honest nodes!");
            }
            
            // Network statistics
            int totalByzantineAttacks = network.values().stream()
                .mapToInt(node -> node.byzantineAttacksDetected.get())
                .sum();
            
            System.out.printf("\n📈 Network Statistics:%n");
            System.out.printf("   Total Byzantine attacks detected: %d%n", totalByzantineAttacks);
            System.out.printf("   Byzantine nodes: 1/%d%n", nodeIds.size());
            System.out.printf("   Fault tolerance: %d Byzantine nodes%n", (nodeIds.size() - 1) / 3);
            
        } catch (Exception e) {
            System.err.printf("❌ Error during simulation: %s%n", e.getMessage());
            e.printStackTrace();
        } finally {
            // Cleanup
            System.out.println("\n🧹 Shutting down network...");
            for (ByzantineFaultTolerance node : network.values()) {
                node.shutdown();
            }
        }
        
        System.out.println("\n" + "=".repeat(70));
        System.out.println("🇮🇳 Java Byzantine Fault Tolerance Key Features:");
        System.out.println("1. Thread-safe concurrent message processing");
        System.out.println("2. CompletableFuture for asynchronous operations");
        System.out.println("3. Atomic operations for consensus state");
        System.out.println("4. ConcurrentHashMap for distributed logs");
        System.out.println("5. ExecutorService for parallel consensus");
        System.out.println("6. Production-ready error handling and timeouts");
        System.out.println("7. Suitable for enterprise distributed systems");
    }
}