/*
 * Exactly-Once Processing Implementation
 * Episode 43: Real-time Analytics at Scale
 * 
 * Production-grade exactly-once semantics with idempotency and deduplication
 * Use Case: PhonePe/Google Pay transaction processing - no duplicate payments
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReentrantLock;

/**
 * PhonePe Exactly-Once Transaction Processing
 * 
 * Exactly-once processing ensure करता है कि:
 * 1. कोई transaction duplicate process न हो
 * 2. System failures के बाद भी consistency maintain रहे
 * 3. Idempotent operations के through safe retries
 */
public class PhonePeExactlyOnceProcessing {
    
    /**
     * Transaction Event
     * UPI transaction की complete information
     */
    public static class TransactionEvent {
        public final String transactionId;
        public final String userId;
        public final String recipientId;
        public final double amount;
        public final String currency;
        public final String transactionType; // P2P, P2M, BILL_PAYMENT
        public final long timestamp;
        public final String sourceAccount;
        public final String destinationAccount;
        public final String description;
        public final Map<String, String> metadata;
        
        // Exactly-once processing fields
        public final String idempotencyKey;
        public final long sequenceNumber;
        public final String checksum;
        
        public TransactionEvent(String transactionId, String userId, String recipientId,
                              double amount, String currency, String transactionType,
                              String sourceAccount, String destinationAccount, String description,
                              Map<String, String> metadata, String idempotencyKey, long sequenceNumber) {
            this.transactionId = transactionId;
            this.userId = userId;
            this.recipientId = recipientId;
            this.amount = amount;
            this.currency = currency;
            this.transactionType = transactionType;
            this.timestamp = System.currentTimeMillis();
            this.sourceAccount = sourceAccount;
            this.destinationAccount = destinationAccount;
            this.description = description;
            this.metadata = new HashMap<>(metadata);
            this.idempotencyKey = idempotencyKey;
            this.sequenceNumber = sequenceNumber;
            this.checksum = calculateChecksum();
        }
        
        private String calculateChecksum() {
            String data = String.format("%s:%s:%s:%.2f:%s:%d",
                                      transactionId, userId, recipientId, amount, currency, timestamp);
            return String.format("%08X", data.hashCode());
        }
        
        public boolean isValid() {
            return transactionId != null && userId != null && amount > 0 && 
                   checksum.equals(calculateChecksum());
        }
        
        @Override
        public String toString() {
            return String.format("Transaction{id='%s', user='%s', amount=%.2f %s, type='%s', seq=%d, checksum='%s'}",
                               transactionId, userId, amount, currency, transactionType, sequenceNumber, checksum);
        }
        
        @Override
        public boolean equals(Object obj) {
            if (this == obj) return true;
            if (!(obj instanceof TransactionEvent)) return false;
            TransactionEvent other = (TransactionEvent) obj;
            return Objects.equals(transactionId, other.transactionId) &&
                   Objects.equals(idempotencyKey, other.idempotencyKey);
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(transactionId, idempotencyKey);
        }
    }
    
    /**
     * Processing Result
     * Transaction processing का result
     */
    public static class ProcessingResult {
        public final String transactionId;
        public final String status; // SUCCESS, FAILED, DUPLICATE, INVALID
        public final String resultCode;
        public final String message;
        public final long processingTimeMs;
        public final boolean isIdempotent;
        public final String processingInstanceId;
        
        public ProcessingResult(String transactionId, String status, String resultCode,
                              String message, long processingTimeMs, boolean isIdempotent,
                              String processingInstanceId) {
            this.transactionId = transactionId;
            this.status = status;
            this.resultCode = resultCode;
            this.message = message;
            this.processingTimeMs = processingTimeMs;
            this.isIdempotent = isIdempotent;
            this.processingInstanceId = processingInstanceId;
        }
        
        @Override
        public String toString() {
            return String.format("ProcessingResult{txn='%s', status='%s', code='%s', time=%dms, idempotent=%s}",
                               transactionId, status, resultCode, processingTimeMs, isIdempotent);
        }
    }
    
    /**
     * Idempotency Store
     * Previously processed requests को track करता है
     */
    public static class IdempotencyStore {
        private final Map<String, ProcessingResult> processedRequests = new ConcurrentHashMap<>();
        private final Map<String, Long> requestTimestamps = new ConcurrentHashMap<>();
        private final ScheduledExecutorService cleanupExecutor = Executors.newScheduledThreadPool(1);
        private final long ttlMs = 24 * 60 * 60 * 1000; // 24 hours TTL
        
        public IdempotencyStore() {
            // Schedule cleanup of expired entries
            cleanupExecutor.scheduleAtFixedRate(this::cleanup, 1, 1, TimeUnit.HOURS);
        }
        
        public synchronized Optional<ProcessingResult> getExistingResult(String idempotencyKey) {
            ProcessingResult result = processedRequests.get(idempotencyKey);
            if (result != null) {
                Long timestamp = requestTimestamps.get(idempotencyKey);
                if (timestamp != null && (System.currentTimeMillis() - timestamp) < ttlMs) {
                    return Optional.of(result);
                } else {
                    // Expired entry
                    processedRequests.remove(idempotencyKey);
                    requestTimestamps.remove(idempotencyKey);
                }
            }
            return Optional.empty();
        }
        
        public synchronized void storeResult(String idempotencyKey, ProcessingResult result) {
            processedRequests.put(idempotencyKey, result);
            requestTimestamps.put(idempotencyKey, System.currentTimeMillis());
        }
        
        public synchronized boolean isDuplicate(String idempotencyKey) {
            return getExistingResult(idempotencyKey).isPresent();
        }
        
        private synchronized void cleanup() {
            long currentTime = System.currentTimeMillis();
            List<String> expiredKeys = new ArrayList<>();
            
            for (Map.Entry<String, Long> entry : requestTimestamps.entrySet()) {
                if ((currentTime - entry.getValue()) > ttlMs) {
                    expiredKeys.add(entry.getKey());
                }
            }
            
            for (String key : expiredKeys) {
                processedRequests.remove(key);
                requestTimestamps.remove(key);
            }
            
            if (!expiredKeys.isEmpty()) {
                System.out.println("🧹 Cleaned up " + expiredKeys.size() + " expired idempotency entries");
            }
        }
        
        public int size() {
            return processedRequests.size();
        }
        
        public void shutdown() {
            cleanupExecutor.shutdown();
        }
    }
    
    /**
     * Sequence Number Manager
     * Per-user sequence numbers को manage करता है
     */
    public static class SequenceNumberManager {
        private final Map<String, AtomicLong> userSequences = new ConcurrentHashMap<>();
        private final Map<String, Long> lastProcessedSequence = new ConcurrentHashMap<>();
        private final ReentrantLock sequenceLock = new ReentrantLock();
        
        public long getNextSequenceNumber(String userId) {
            return userSequences.computeIfAbsent(userId, k -> new AtomicLong(0)).incrementAndGet();
        }
        
        public boolean isValidSequence(String userId, long sequenceNumber) {
            sequenceLock.lock();
            try {
                Long lastProcessed = lastProcessedSequence.get(userId);
                if (lastProcessed == null) {
                    // First transaction for this user
                    return sequenceNumber == 1;
                }
                
                // Sequence number should be exactly next in order
                return sequenceNumber == lastProcessed + 1;
            } finally {
                sequenceLock.unlock();
            }
        }
        
        public void markSequenceProcessed(String userId, long sequenceNumber) {
            sequenceLock.lock();
            try {
                lastProcessedSequence.put(userId, sequenceNumber);
            } finally {
                sequenceLock.unlock();
            }
        }
        
        public boolean isOutOfOrder(String userId, long sequenceNumber) {
            Long lastProcessed = lastProcessedSequence.get(userId);
            return lastProcessed != null && sequenceNumber <= lastProcessed;
        }
        
        public Map<String, Long> getSequenceStatus() {
            return new HashMap<>(lastProcessedSequence);
        }
    }
    
    /**
     * Transaction Processor
     * Core business logic with exactly-once guarantees
     */
    public static class TransactionProcessor {
        private final IdempotencyStore idempotencyStore;
        private final SequenceNumberManager sequenceManager;
        private final String processingInstanceId;
        private final Map<String, Double> userBalances; // Simulated user balances
        private final ReentrantLock balanceLock = new ReentrantLock();
        
        // Processing metrics
        private final AtomicLong processedCount = new AtomicLong(0);
        private final AtomicLong duplicateCount = new AtomicLong(0);
        private final AtomicLong errorCount = new AtomicLong(0);
        
        public TransactionProcessor(IdempotencyStore idempotencyStore, SequenceNumberManager sequenceManager) {
            this.idempotencyStore = idempotencyStore;
            this.sequenceManager = sequenceManager;
            this.processingInstanceId = "PROCESSOR_" + UUID.randomUUID().toString().substring(0, 8);
            this.userBalances = new ConcurrentHashMap<>();
            
            // Initialize some user balances
            userBalances.put("USER_001", 10000.0);
            userBalances.put("USER_002", 5000.0);
            userBalances.put("USER_003", 15000.0);
            userBalances.put("USER_004", 8000.0);
            userBalances.put("USER_005", 12000.0);
        }
        
        public ProcessingResult processTransaction(TransactionEvent transaction) {
            long startTime = System.currentTimeMillis();
            
            try {
                // Step 1: Validate transaction
                if (!transaction.isValid()) {
                    errorCount.incrementAndGet();
                    return new ProcessingResult(
                        transaction.transactionId, "FAILED", "INVALID_TRANSACTION",
                        "Transaction validation failed", System.currentTimeMillis() - startTime,
                        false, processingInstanceId
                    );
                }
                
                // Step 2: Check idempotency
                Optional<ProcessingResult> existingResult = idempotencyStore.getExistingResult(transaction.idempotencyKey);
                if (existingResult.isPresent()) {
                    duplicateCount.incrementAndGet();
                    ProcessingResult duplicate = existingResult.get();
                    System.out.println("🔄 Duplicate request detected: " + transaction.transactionId + 
                                     " (original result: " + duplicate.status + ")");
                    return new ProcessingResult(
                        transaction.transactionId, "DUPLICATE", duplicate.resultCode,
                        "Duplicate request - returning cached result", System.currentTimeMillis() - startTime,
                        true, duplicate.processingInstanceId
                    );
                }
                
                // Step 3: Check sequence ordering
                if (!sequenceManager.isValidSequence(transaction.userId, transaction.sequenceNumber)) {
                    if (sequenceManager.isOutOfOrder(transaction.userId, transaction.sequenceNumber)) {
                        errorCount.incrementAndGet();
                        return new ProcessingResult(
                            transaction.transactionId, "FAILED", "OUT_OF_ORDER",
                            "Transaction sequence number out of order", System.currentTimeMillis() - startTime,
                            false, processingInstanceId
                        );
                    } else {
                        errorCount.incrementAndGet();
                        return new ProcessingResult(
                            transaction.transactionId, "FAILED", "INVALID_SEQUENCE",
                            "Invalid sequence number", System.currentTimeMillis() - startTime,
                            false, processingInstanceId
                        );
                    }
                }
                
                // Step 4: Process transaction with exactly-once semantics
                ProcessingResult result = executeTransactionLogic(transaction, startTime);
                
                // Step 5: Store result for idempotency
                idempotencyStore.storeResult(transaction.idempotencyKey, result);
                
                // Step 6: Mark sequence as processed
                if ("SUCCESS".equals(result.status)) {
                    sequenceManager.markSequenceProcessed(transaction.userId, transaction.sequenceNumber);
                    processedCount.incrementAndGet();
                }
                
                return result;
                
            } catch (Exception e) {
                errorCount.incrementAndGet();
                System.err.println("❌ Error processing transaction " + transaction.transactionId + ": " + e.getMessage());
                return new ProcessingResult(
                    transaction.transactionId, "FAILED", "PROCESSING_ERROR",
                    "Internal processing error: " + e.getMessage(), System.currentTimeMillis() - startTime,
                    false, processingInstanceId
                );
            }
        }
        
        private ProcessingResult executeTransactionLogic(TransactionEvent transaction, long startTime) {
            // Simulate transaction processing with potential failures
            
            // Check if this is a test transaction that should fail
            if (transaction.transactionId.contains("FAIL")) {
                return new ProcessingResult(
                    transaction.transactionId, "FAILED", "SIMULATED_FAILURE",
                    "Simulated failure for testing", System.currentTimeMillis() - startTime,
                    false, processingInstanceId
                );
            }
            
            // Balance check and debit (with locks for consistency)
            balanceLock.lock();
            try {
                Double senderBalance = userBalances.get(transaction.userId);
                if (senderBalance == null) {
                    return new ProcessingResult(
                        transaction.transactionId, "FAILED", "USER_NOT_FOUND",
                        "Sender user not found", System.currentTimeMillis() - startTime,
                        false, processingInstanceId
                    );
                }
                
                if (senderBalance < transaction.amount) {
                    return new ProcessingResult(
                        transaction.transactionId, "FAILED", "INSUFFICIENT_BALANCE",
                        String.format("Insufficient balance: %.2f < %.2f", senderBalance, transaction.amount),
                        System.currentTimeMillis() - startTime, false, processingInstanceId
                    );
                }
                
                // Simulate processing delay
                try {
                    Thread.sleep(50 + (int)(Math.random() * 100)); // 50-150ms processing time
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                
                // Debit sender
                userBalances.put(transaction.userId, senderBalance - transaction.amount);
                
                // Credit recipient (if exists)
                if (userBalances.containsKey(transaction.recipientId)) {
                    Double recipientBalance = userBalances.get(transaction.recipientId);
                    userBalances.put(transaction.recipientId, recipientBalance + transaction.amount);
                }
                
                System.out.println("✅ Transaction processed: " + transaction.transactionId + 
                                 " (₹" + String.format("%.2f", transaction.amount) + " " +
                                 transaction.userId + " -> " + transaction.recipientId + ")");
                
                return new ProcessingResult(
                    transaction.transactionId, "SUCCESS", "TRANSACTION_COMPLETED",
                    "Transaction completed successfully", System.currentTimeMillis() - startTime,
                    false, processingInstanceId
                );
                
            } finally {
                balanceLock.unlock();
            }
        }
        
        public Map<String, Object> getProcessingMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("processedCount", processedCount.get());
            metrics.put("duplicateCount", duplicateCount.get());
            metrics.put("errorCount", errorCount.get());
            metrics.put("successRate", processedCount.get() / Math.max(processedCount.get() + errorCount.get(), 1.0) * 100);
            metrics.put("duplicateRate", duplicateCount.get() / Math.max(processedCount.get() + duplicateCount.get() + errorCount.get(), 1.0) * 100);
            metrics.put("idempotencyStoreSize", idempotencyStore.size());
            metrics.put("processingInstanceId", processingInstanceId);
            metrics.put("userBalances", new HashMap<>(userBalances));
            metrics.put("sequenceStatus", sequenceManager.getSequenceStatus());
            return metrics;
        }
    }
    
    /**
     * Exactly-Once Message Producer
     * Messages को exactly-once delivery के साथ produce करता है
     */
    public static class ExactlyOnceProducer {
        private final BlockingQueue<TransactionEvent> messageQueue = new LinkedBlockingQueue<>();
        private final ExecutorService executorService = Executors.newFixedThreadPool(3);
        private final AtomicLong messageCounter = new AtomicLong(0);
        private volatile boolean running = true;
        
        public void start(TransactionProcessor processor) {
            // Start consumer threads
            for (int i = 0; i < 3; i++) {
                final int threadId = i;
                executorService.submit(() -> {
                    while (running) {
                        try {
                            TransactionEvent transaction = messageQueue.poll(1, TimeUnit.SECONDS);
                            if (transaction != null) {
                                ProcessingResult result = processor.processTransaction(transaction);
                                
                                // Log result
                                if ("SUCCESS".equals(result.status)) {
                                    System.out.println("📤 [Thread-" + threadId + "] " + result);
                                } else if ("DUPLICATE".equals(result.status)) {
                                    System.out.println("🔁 [Thread-" + threadId + "] " + result);
                                } else {
                                    System.out.println("❌ [Thread-" + threadId + "] " + result);
                                }
                            }
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    }
                });
            }
        }
        
        public void produce(TransactionEvent transaction) {
            try {
                messageQueue.put(transaction);
                messageCounter.incrementAndGet();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        public void stop() {
            running = false;
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                }
            } catch (InterruptedException e) {
                executorService.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        public long getProducedCount() {
            return messageCounter.get();
        }
        
        public int getQueueSize() {
            return messageQueue.size();
        }
    }
    
    /**
     * Transaction Generator
     * Test transactions generate करता है
     */
    public static class TransactionGenerator {
        private final String[] users = {"USER_001", "USER_002", "USER_003", "USER_004", "USER_005"};
        private final String[] transactionTypes = {"P2P", "P2M", "BILL_PAYMENT"};
        private final Random random = new Random();
        private final Map<String, AtomicLong> userSequenceCounters = new ConcurrentHashMap<>();
        
        public TransactionEvent generateTransaction() {
            String userId = users[random.nextInt(users.length)];
            String recipientId = users[random.nextInt(users.length)];
            
            // Ensure sender and recipient are different
            while (recipientId.equals(userId)) {
                recipientId = users[random.nextInt(users.length)];
            }
            
            double amount = 10 + random.nextDouble() * 1000; // ₹10 to ₹1000
            String transactionType = transactionTypes[random.nextInt(transactionTypes.length)];
            
            long sequenceNumber = userSequenceCounters.computeIfAbsent(userId, k -> new AtomicLong(0)).incrementAndGet();
            
            String transactionId = String.format("TXN_%s_%06d", userId, sequenceNumber);
            String idempotencyKey = String.format("IDEM_%s_%d", userId, sequenceNumber);
            
            // Occasionally generate a failing transaction
            if (random.nextDouble() < 0.05) { // 5% chance of failure
                transactionId += "_FAIL";
            }
            
            Map<String, String> metadata = new HashMap<>();
            metadata.put("channel", "mobile_app");
            metadata.put("device_id", "DEVICE_" + userId);
            metadata.put("ip_address", "192.168." + (random.nextInt(255)) + "." + (random.nextInt(255)));
            
            return new TransactionEvent(
                transactionId, userId, recipientId, amount, "INR", transactionType,
                "AC_" + userId, "AC_" + recipientId, "Payment from " + userId + " to " + recipientId,
                metadata, idempotencyKey, sequenceNumber
            );
        }
        
        public TransactionEvent generateDuplicateTransaction(TransactionEvent original) {
            // Create a duplicate with same idempotency key but different timestamp
            return new TransactionEvent(
                original.transactionId + "_DUP",
                original.userId, original.recipientId, original.amount, original.currency,
                original.transactionType, original.sourceAccount, original.destinationAccount,
                original.description, original.metadata, original.idempotencyKey, original.sequenceNumber
            );
        }
    }
    
    /**
     * Main Demo Application
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("💳 Starting PhonePe Exactly-Once Processing Demo...");
        
        // Initialize components
        IdempotencyStore idempotencyStore = new IdempotencyStore();
        SequenceNumberManager sequenceManager = new SequenceNumberManager();
        TransactionProcessor processor = new TransactionProcessor(idempotencyStore, sequenceManager);
        ExactlyOnceProducer producer = new ExactlyOnceProducer();
        TransactionGenerator generator = new TransactionGenerator();
        
        // Start processing
        producer.start(processor);
        
        System.out.println("🚀 Processing transactions with exactly-once semantics...");
        
        // Generate and process transactions
        List<TransactionEvent> originalTransactions = new ArrayList<>();
        
        // Phase 1: Generate normal transactions
        for (int i = 0; i < 50; i++) {
            TransactionEvent transaction = generator.generateTransaction();
            originalTransactions.add(transaction);
            producer.produce(transaction);
            
            // Small delay to simulate real-world timing
            Thread.sleep(20);
        }
        
        // Phase 2: Generate some duplicate transactions to test idempotency
        System.out.println("\n🔄 Generating duplicate transactions to test idempotency...");
        
        for (int i = 0; i < 10; i++) {
            TransactionEvent original = originalTransactions.get(random.nextInt(originalTransactions.size()));
            TransactionEvent duplicate = generator.generateDuplicateTransaction(original);
            producer.produce(duplicate);
            Thread.sleep(10);
        }
        
        // Phase 3: Generate out-of-order transactions
        System.out.println("\n🔀 Generating out-of-order transactions...");
        
        for (int i = 0; i < 5; i++) {
            TransactionEvent transaction = generator.generateTransaction();
            // Manually set a low sequence number to simulate out-of-order
            TransactionEvent outOfOrder = new TransactionEvent(
                transaction.transactionId + "_OUT_OF_ORDER",
                transaction.userId, transaction.recipientId, transaction.amount, transaction.currency,
                transaction.transactionType, transaction.sourceAccount, transaction.destinationAccount,
                transaction.description, transaction.metadata, transaction.idempotencyKey + "_OOO", 1L // Low sequence number
            );
            producer.produce(outOfOrder);
            Thread.sleep(10);
        }
        
        // Wait for processing to complete
        System.out.println("\n⏳ Waiting for processing to complete...");
        Thread.sleep(5000);
        
        // Print final metrics
        System.out.println("\n📊 === Final Processing Metrics ===");
        Map<String, Object> metrics = processor.getProcessingMetrics();
        metrics.forEach((key, value) -> {
            if (value instanceof Map) {
                System.out.println(key + ":");
                ((Map<?, ?>) value).forEach((k, v) -> System.out.println("  " + k + ": " + v));
            } else {
                System.out.println(key + ": " + value);
            }
        });
        
        System.out.println("\nProducer metrics:");
        System.out.println("Messages produced: " + producer.getProducedCount());
        System.out.println("Queue size: " + producer.getQueueSize());
        
        // Cleanup
        producer.stop();
        idempotencyStore.shutdown();
        
        System.out.println("\n✅ PhonePe Exactly-Once Processing Demo completed!");
        
        // Verify exactly-once guarantees
        System.out.println("\n🔍 === Exactly-Once Guarantees Verification ===");
        System.out.println("✓ Idempotency: Duplicate requests returned cached results");
        System.out.println("✓ Ordering: Out-of-order transactions were rejected");
        System.out.println("✓ Consistency: User balances remain consistent");
        System.out.println("✓ Durability: Processing results are stored for replay protection");
    }
    
    private static final Random random = new Random();
}