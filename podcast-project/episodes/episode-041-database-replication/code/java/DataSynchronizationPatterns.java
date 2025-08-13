/**
 * Episode 41: Database Replication Strategies
 * Java Example: Data Synchronization Patterns Implementation
 * 
 * यह comprehensive data synchronization patterns का implementation है
 * जो different replication scenarios में use होते हैं। Indian financial
 * और e-commerce systems के real patterns include किए गए हैं।
 * 
 * Real-world Use Case: Banking और E-commerce Data Synchronization
 * - Write-Ahead Logging (WAL) pattern
 * - Change Data Capture (CDC) pattern  
 * - Event Sourcing pattern
 * - Saga pattern for distributed transactions
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

// Base interfaces and common classes
interface SynchronizationPattern {
    String getPatternName();
    void processChange(DataChange change) throws Exception;
    List<DataChange> getPendingChanges();
    void markChangeAsApplied(String changeId);
    SyncStatistics getStatistics();
}

class DataChange {
    public final String changeId;
    public final String entityId;
    public final String entityType;
    public final ChangeType changeType;
    public final String oldValue;
    public final String newValue;
    public final LocalDateTime timestamp;
    public final String source;
    public final Map<String, Object> metadata;
    public final String checksum;
    
    public DataChange(String entityId, String entityType, ChangeType changeType,
                     String oldValue, String newValue, String source, Map<String, Object> metadata) {
        this.changeId = generateChangeId();
        this.entityId = entityId;
        this.entityType = entityType;
        this.changeType = changeType;
        this.oldValue = oldValue;
        this.newValue = newValue;
        this.timestamp = LocalDateTime.now();
        this.source = source;
        this.metadata = metadata != null ? new HashMap<>(metadata) : new HashMap<>();
        this.checksum = calculateChecksum();
    }
    
    private String generateChangeId() {
        return String.format("%s_%d_%s", 
            entityId != null ? entityId : "NULL",
            System.currentTimeMillis(),
            UUID.randomUUID().toString().substring(0, 8));
    }
    
    private String calculateChecksum() {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String content = String.format("%s|%s|%s|%s|%s|%s",
                entityId, entityType, changeType, oldValue, newValue, timestamp);
            byte[] hash = digest.digest(content.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(hash).substring(0, 16);
        } catch (Exception e) {
            return "INVALID_CHECKSUM";
        }
    }
    
    public boolean isValid() {
        return checksum.equals(calculateChecksum());
    }
}

enum ChangeType {
    INSERT, UPDATE, DELETE, SCHEMA_CHANGE
}

class SyncStatistics {
    public final AtomicLong totalChanges = new AtomicLong(0);
    public final AtomicLong appliedChanges = new AtomicLong(0);
    public final AtomicLong failedChanges = new AtomicLong(0);
    public final AtomicLong pendingChanges = new AtomicLong(0);
    public final LocalDateTime startTime = LocalDateTime.now();
    
    public double getSuccessRate() {
        long total = totalChanges.get();
        return total == 0 ? 0.0 : (double) appliedChanges.get() / total * 100.0;
    }
    
    public long getChangesPerSecond() {
        Duration duration = Duration.between(startTime, LocalDateTime.now());
        long seconds = duration.getSeconds();
        return seconds == 0 ? 0 : totalChanges.get() / seconds;
    }
}

/**
 * Write-Ahead Logging (WAL) Pattern
 * Banking systems में transaction durability के लिए critical
 */
class WriteAheadLoggingPattern implements SynchronizationPattern {
    private final String patternName = "Write-Ahead Logging (WAL)";
    private final Queue<WALEntry> walQueue = new ConcurrentLinkedQueue<>();
    private final Map<String, WALEntry> walIndex = new ConcurrentHashMap<>();
    private final SyncStatistics statistics = new SyncStatistics();
    private final AtomicLong sequenceNumber = new AtomicLong(1);
    
    // WAL configuration for Indian banking compliance
    private final int maxWalSize = 10000;  // Maximum WAL entries
    private final int checkpointInterval = 1000;  // Checkpoint every 1000 entries
    private final ExecutorService walWriter = Executors.newSingleThreadExecutor();
    
    @Override
    public String getPatternName() { return patternName; }
    
    @Override
    public void processChange(DataChange change) throws Exception {
        // Step 1: Write to WAL first (durability guarantee)
        WALEntry walEntry = new WALEntry(
            sequenceNumber.getAndIncrement(),
            change,
            LocalDateTime.now(),
            WALEntryStatus.PENDING
        );
        
        // Simulate write to persistent storage
        walWriter.submit(() -> writeToWAL(walEntry));
        
        walQueue.offer(walEntry);
        walIndex.put(change.changeId, walEntry);
        
        statistics.totalChanges.incrementAndGet();
        statistics.pendingChanges.incrementAndGet();
        
        // Step 2: Apply change to main storage (after WAL write)
        try {
            applyChangeToMainStorage(change);
            walEntry.status = WALEntryStatus.APPLIED;
            statistics.appliedChanges.incrementAndGet();
            statistics.pendingChanges.decrementAndGet();
            
        } catch (Exception e) {
            walEntry.status = WALEntryStatus.FAILED;
            walEntry.errorMessage = e.getMessage();
            statistics.failedChanges.incrementAndGet();
            statistics.pendingChanges.decrementAndGet();
            throw e;
        }
        
        // Periodic checkpoint to reduce WAL size
        if (sequenceNumber.get() % checkpointInterval == 0) {
            performCheckpoint();
        }
    }
    
    private void writeToWAL(WALEntry entry) {
        try {
            // Simulate persistent WAL write (normally to disk)
            Thread.sleep(2); // 2ms write latency
            
            // Banking regulatory requirement: WAL integrity check
            if (!entry.change.isValid()) {
                throw new RuntimeException("WAL entry integrity check failed");
            }
            
            entry.status = WALEntryStatus.WRITTEN;
            
        } catch (Exception e) {
            entry.status = WALEntryStatus.FAILED;
            entry.errorMessage = e.getMessage();
        }
    }
    
    private void applyChangeToMainStorage(DataChange change) throws Exception {
        // Simulate applying change to main database
        Thread.sleep(1); // 1ms application latency
        
        // Banking validation: ensure change is within business rules
        if (change.entityType.equals("ACCOUNT_BALANCE")) {
            validateBankingTransaction(change);
        }
        
        // Simulate occasional storage failure (1% rate)
        if (Math.random() < 0.01) {
            throw new RuntimeException("Storage subsystem temporary failure");
        }
    }
    
    private void validateBankingTransaction(DataChange change) throws Exception {
        if (change.newValue != null) {
            try {
                double newBalance = Double.parseDouble(change.newValue);
                
                // Indian banking regulation: negative balance check
                if (newBalance < 0 && !change.metadata.getOrDefault("overdraft_allowed", false).equals(true)) {
                    throw new RuntimeException("Negative balance not allowed without overdraft facility");
                }
                
                // Large transaction alert (₹5 lakhs)
                if (change.oldValue != null) {
                    double oldBalance = Double.parseDouble(change.oldValue);
                    double transactionAmount = Math.abs(newBalance - oldBalance);
                    
                    if (transactionAmount > 500000) {
                        // Log for regulatory reporting
                        change.metadata.put("high_value_transaction", true);
                        change.metadata.put("requires_reporting", true);
                    }
                }
                
            } catch (NumberFormatException e) {
                throw new RuntimeException("Invalid balance format in transaction");
            }
        }
    }
    
    private void performCheckpoint() {
        // Checkpoint: remove applied WAL entries to save space
        long appliedCount = walQueue.stream()
                .filter(entry -> entry.status == WALEntryStatus.APPLIED)
                .count();
        
        walQueue.removeIf(entry -> entry.status == WALEntryStatus.APPLIED);
        
        System.out.println(String.format("WAL Checkpoint: Removed %d applied entries. Remaining: %d",
            appliedCount, walQueue.size()));
    }
    
    @Override
    public List<DataChange> getPendingChanges() {
        return walQueue.stream()
                .filter(entry -> entry.status == WALEntryStatus.PENDING || entry.status == WALEntryStatus.WRITTEN)
                .map(entry -> entry.change)
                .collect(Collectors.toList());
    }
    
    @Override
    public void markChangeAsApplied(String changeId) {
        WALEntry entry = walIndex.get(changeId);
        if (entry != null) {
            entry.status = WALEntryStatus.APPLIED;
            statistics.appliedChanges.incrementAndGet();
            statistics.pendingChanges.decrementAndGet();
        }
    }
    
    @Override
    public SyncStatistics getStatistics() { return statistics; }
    
    public void shutdown() {
        walWriter.shutdown();
        try {
            walWriter.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    // WAL specific classes
    static class WALEntry {
        public final long sequenceNumber;
        public final DataChange change;
        public final LocalDateTime writeTime;
        public volatile WALEntryStatus status;
        public String errorMessage;
        
        public WALEntry(long sequenceNumber, DataChange change, LocalDateTime writeTime, WALEntryStatus status) {
            this.sequenceNumber = sequenceNumber;
            this.change = change;
            this.writeTime = writeTime;
            this.status = status;
        }
    }
    
    enum WALEntryStatus {
        PENDING, WRITTEN, APPLIED, FAILED
    }
}

/**
 * Change Data Capture (CDC) Pattern  
 * E-commerce inventory changes के लिए real-time synchronization
 */
class ChangeDataCapturePattern implements SynchronizationPattern {
    private final String patternName = "Change Data Capture (CDC)";
    private final BlockingQueue<DataChange> changeStream = new LinkedBlockingQueue<>();
    private final Map<String, DataChange> changeIndex = new ConcurrentHashMap<>();
    private final SyncStatistics statistics = new SyncStatistics();
    
    // CDC configuration for e-commerce systems
    private final ExecutorService cdcProcessor = Executors.newFixedThreadPool(3);
    private final ScheduledExecutorService batchProcessor = Executors.newScheduledThreadPool(1);
    
    // Batch processing for efficiency (like Flipkart inventory updates)
    private final List<DataChange> batchBuffer = Collections.synchronizedList(new ArrayList<>());
    private final int batchSize = 100;
    private final int batchTimeoutMs = 1000;
    
    public ChangeDataCapturePattern() {
        startBatchProcessor();
    }
    
    @Override
    public String getPatternName() { return patternName; }
    
    @Override
    public void processChange(DataChange change) throws Exception {
        // Add to change stream
        changeStream.offer(change);
        changeIndex.put(change.changeId, change);
        
        statistics.totalChanges.incrementAndGet();
        statistics.pendingChanges.incrementAndGet();
        
        // Submit for async processing
        cdcProcessor.submit(() -> {
            try {
                processChangeAsync(change);
            } catch (Exception e) {
                statistics.failedChanges.incrementAndGet();
                change.metadata.put("error", e.getMessage());
            }
        });
    }
    
    private void processChangeAsync(DataChange change) throws Exception {
        // E-commerce specific change processing
        if (change.entityType.equals("PRODUCT_INVENTORY")) {
            processInventoryChange(change);
        } else if (change.entityType.equals("ORDER_STATUS")) {
            processOrderStatusChange(change);
        } else if (change.entityType.equals("PRICE_UPDATE")) {
            processPriceChange(change);
        }
        
        // Add to batch for downstream systems
        synchronized (batchBuffer) {
            batchBuffer.add(change);
            
            // Process batch if size limit reached
            if (batchBuffer.size() >= batchSize) {
                processBatch(new ArrayList<>(batchBuffer));
                batchBuffer.clear();
            }
        }
    }
    
    private void processInventoryChange(DataChange change) throws Exception {
        // Flipkart-style inventory change processing
        Thread.sleep(5); // Simulate processing time
        
        // Validate inventory levels
        if (change.newValue != null) {
            try {
                int newQuantity = Integer.parseInt(change.newValue);
                
                // Negative inventory check
                if (newQuantity < 0) {
                    change.metadata.put("stock_out", true);
                    change.metadata.put("requires_reorder", true);
                }
                
                // Low stock alert (less than 10 units)
                if (newQuantity > 0 && newQuantity < 10) {
                    change.metadata.put("low_stock_alert", true);
                    // Trigger reorder for popular products
                    if (change.metadata.getOrDefault("product_category", "").equals("electronics")) {
                        change.metadata.put("auto_reorder", true);
                    }
                }
                
                // High stock movement detection (for trend analysis)
                if (change.oldValue != null) {
                    int oldQuantity = Integer.parseInt(change.oldValue);
                    int movement = Math.abs(newQuantity - oldQuantity);
                    
                    if (movement > 50) {
                        change.metadata.put("high_movement", true);
                        change.metadata.put("movement_amount", movement);
                    }
                }
                
            } catch (NumberFormatException e) {
                throw new RuntimeException("Invalid inventory quantity format");
            }
        }
        
        statistics.appliedChanges.incrementAndGet();
        statistics.pendingChanges.decrementAndGet();
    }
    
    private void processOrderStatusChange(DataChange change) throws Exception {
        Thread.sleep(3); // Simulate processing time
        
        // Order lifecycle tracking
        String newStatus = change.newValue;
        if (newStatus != null) {
            switch (newStatus.toUpperCase()) {
                case "CONFIRMED":
                    change.metadata.put("inventory_reserved", true);
                    break;
                case "SHIPPED":
                    change.metadata.put("tracking_required", true);
                    change.metadata.put("delivery_estimation", calculateDeliveryDate());
                    break;
                case "DELIVERED":
                    change.metadata.put("customer_feedback_due", true);
                    break;
                case "CANCELLED":
                    change.metadata.put("inventory_release", true);
                    change.metadata.put("refund_required", true);
                    break;
            }
        }
        
        statistics.appliedChanges.incrementAndGet();
        statistics.pendingChanges.decrementAndGet();
    }
    
    private void processPriceChange(DataChange change) throws Exception {
        Thread.sleep(2); // Simulate processing time
        
        // Price change validation and notifications
        if (change.oldValue != null && change.newValue != null) {
            try {
                double oldPrice = Double.parseDouble(change.oldValue);
                double newPrice = Double.parseDouble(change.newValue);
                double changePercent = ((newPrice - oldPrice) / oldPrice) * 100;
                
                change.metadata.put("price_change_percent", changePercent);
                
                // Significant price changes require approval
                if (Math.abs(changePercent) > 20) {
                    change.metadata.put("requires_approval", true);
                    change.metadata.put("significant_change", true);
                }
                
                // Discount alerts for customers
                if (changePercent < -10) {
                    change.metadata.put("discount_alert", true);
                    change.metadata.put("notify_customers", true);
                }
                
            } catch (NumberFormatException e) {
                throw new RuntimeException("Invalid price format");
            }
        }
        
        statistics.appliedChanges.incrementAndGet();
        statistics.pendingChanges.decrementAndGet();
    }
    
    private String calculateDeliveryDate() {
        // Simple delivery estimation (real system would be more complex)
        LocalDateTime estimatedDelivery = LocalDateTime.now().plusDays(3);
        return estimatedDelivery.format(DateTimeFormatter.ISO_LOCAL_DATE);
    }
    
    private void startBatchProcessor() {
        batchProcessor.scheduleAtFixedRate(() -> {
            synchronized (batchBuffer) {
                if (!batchBuffer.isEmpty()) {
                    processBatch(new ArrayList<>(batchBuffer));
                    batchBuffer.clear();
                }
            }
        }, batchTimeoutMs, batchTimeoutMs, TimeUnit.MILLISECONDS);
    }
    
    private void processBatch(List<DataChange> batch) {
        // Process batch of changes for downstream systems
        try {
            // Simulate batch processing to downstream systems
            Thread.sleep(batch.size() * 2); // 2ms per change in batch
            
            System.out.println(String.format("CDC: Processed batch of %d changes", batch.size()));
            
            // Group by entity type for specialized handling
            Map<String, List<DataChange>> groupedChanges = batch.stream()
                    .collect(Collectors.groupingBy(change -> change.entityType));
            
            for (Map.Entry<String, List<DataChange>> entry : groupedChanges.entrySet()) {
                System.out.println(String.format("  %s: %d changes", entry.getKey(), entry.getValue().size()));
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    @Override
    public List<DataChange> getPendingChanges() {
        return new ArrayList<>(changeStream);
    }
    
    @Override
    public void markChangeAsApplied(String changeId) {
        DataChange change = changeIndex.get(changeId);
        if (change != null) {
            changeStream.remove(change);
            statistics.appliedChanges.incrementAndGet();
            statistics.pendingChanges.decrementAndGet();
        }
    }
    
    @Override
    public SyncStatistics getStatistics() { return statistics; }
    
    public void shutdown() {
        cdcProcessor.shutdown();
        batchProcessor.shutdown();
        try {
            cdcProcessor.awaitTermination(5, TimeUnit.SECONDS);
            batchProcessor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Event Sourcing Pattern
 * Financial transactions के लिए complete audit trail
 */
class EventSourcingPattern implements SynchronizationPattern {
    private final String patternName = "Event Sourcing";
    private final List<EventStore> eventStore = Collections.synchronizedList(new ArrayList<>());
    private final Map<String, EntitySnapshot> snapshots = new ConcurrentHashMap<>();
    private final SyncStatistics statistics = new SyncStatistics();
    private final AtomicLong eventSequence = new AtomicLong(1);
    
    // Snapshot configuration for performance
    private final int snapshotInterval = 100; // Create snapshot every 100 events
    
    @Override
    public String getPatternName() { return patternName; }
    
    @Override
    public void processChange(DataChange change) throws Exception {
        // Convert change to event
        Event event = new Event(
            eventSequence.getAndIncrement(),
            change.entityId,
            change.entityType,
            change.changeType.name(),
            change.newValue,
            change.timestamp,
            change.source,
            change.metadata
        );
        
        // Store event (append-only)
        EventStore eventStoreEntry = new EventStore(event, LocalDateTime.now());
        eventStore.add(eventStoreEntry);
        
        statistics.totalChanges.incrementAndGet();
        
        try {
            // Apply event to build current state
            applyEvent(event);
            
            // Create snapshot if needed
            if (event.sequenceNumber % snapshotInterval == 0) {
                createSnapshot(event.entityId);
            }
            
            statistics.appliedChanges.incrementAndGet();
            
        } catch (Exception e) {
            statistics.failedChanges.incrementAndGet();
            throw e;
        }
    }
    
    private void applyEvent(Event event) throws Exception {
        // Get or create entity snapshot
        EntitySnapshot snapshot = snapshots.computeIfAbsent(event.entityId, 
            id -> new EntitySnapshot(id, event.entityType, new HashMap<>(), 0));
        
        // Apply event based on entity type
        switch (event.entityType) {
            case "BANK_ACCOUNT":
                applyBankAccountEvent(snapshot, event);
                break;
            case "ORDER":
                applyOrderEvent(snapshot, event);
                break;
            case "INVENTORY":
                applyInventoryEvent(snapshot, event);
                break;
            default:
                applyGenericEvent(snapshot, event);
        }
        
        snapshot.lastEventSequence = event.sequenceNumber;
        snapshot.lastUpdated = LocalDateTime.now();
    }
    
    private void applyBankAccountEvent(EntitySnapshot snapshot, Event event) throws Exception {
        Map<String, Object> state = snapshot.currentState;
        
        switch (event.eventType) {
            case "ACCOUNT_CREATED":
                state.put("balance", 0.0);
                state.put("status", "ACTIVE");
                state.put("created_date", event.timestamp.toString());
                break;
                
            case "DEPOSIT":
                double currentBalance = (Double) state.getOrDefault("balance", 0.0);
                double depositAmount = Double.parseDouble(event.eventData);
                state.put("balance", currentBalance + depositAmount);
                state.put("last_transaction", event.timestamp.toString());
                break;
                
            case "WITHDRAWAL":
                currentBalance = (Double) state.getOrDefault("balance", 0.0);
                double withdrawAmount = Double.parseDouble(event.eventData);
                
                if (currentBalance < withdrawAmount) {
                    throw new RuntimeException("Insufficient funds for withdrawal");
                }
                
                state.put("balance", currentBalance - withdrawAmount);
                state.put("last_transaction", event.timestamp.toString());
                break;
                
            case "ACCOUNT_FROZEN":
                state.put("status", "FROZEN");
                state.put("frozen_date", event.timestamp.toString());
                break;
        }
    }
    
    private void applyOrderEvent(EntitySnapshot snapshot, Event event) {
        Map<String, Object> state = snapshot.currentState;
        
        switch (event.eventType) {
            case "ORDER_CREATED":
                state.put("status", "CREATED");
                state.put("created_date", event.timestamp.toString());
                if (event.metadata.containsKey("total_amount")) {
                    state.put("total_amount", event.metadata.get("total_amount"));
                }
                break;
                
            case "ORDER_CONFIRMED":
                state.put("status", "CONFIRMED");
                state.put("confirmed_date", event.timestamp.toString());
                break;
                
            case "ORDER_SHIPPED":
                state.put("status", "SHIPPED");
                state.put("shipped_date", event.timestamp.toString());
                if (event.metadata.containsKey("tracking_number")) {
                    state.put("tracking_number", event.metadata.get("tracking_number"));
                }
                break;
                
            case "ORDER_DELIVERED":
                state.put("status", "DELIVERED");
                state.put("delivered_date", event.timestamp.toString());
                break;
        }
    }
    
    private void applyInventoryEvent(EntitySnapshot snapshot, Event event) {
        Map<String, Object> state = snapshot.currentState;
        
        switch (event.eventType) {
            case "STOCK_ADDED":
                int currentStock = (Integer) state.getOrDefault("quantity", 0);
                int addedStock = Integer.parseInt(event.eventData);
                state.put("quantity", currentStock + addedStock);
                state.put("last_updated", event.timestamp.toString());
                break;
                
            case "STOCK_REMOVED":
                currentStock = (Integer) state.getOrDefault("quantity", 0);
                int removedStock = Integer.parseInt(event.eventData);
                state.put("quantity", Math.max(0, currentStock - removedStock));
                state.put("last_updated", event.timestamp.toString());
                break;
                
            case "PRICE_CHANGED":
                double newPrice = Double.parseDouble(event.eventData);
                state.put("price", newPrice);
                state.put("price_updated", event.timestamp.toString());
                break;
        }
    }
    
    private void applyGenericEvent(EntitySnapshot snapshot, Event event) {
        Map<String, Object> state = snapshot.currentState;
        state.put("last_event", event.eventType);
        state.put("last_updated", event.timestamp.toString());
        
        if (event.eventData != null) {
            state.put("data", event.eventData);
        }
    }
    
    private void createSnapshot(String entityId) {
        EntitySnapshot current = snapshots.get(entityId);
        if (current != null) {
            // Create a snapshot for faster future rebuilds
            EntitySnapshot snapshot = new EntitySnapshot(
                current.entityId,
                current.entityType,
                new HashMap<>(current.currentState),
                current.lastEventSequence
            );
            
            // In a real system, this would be persisted
            System.out.println(String.format("Created snapshot for entity %s at sequence %d",
                entityId, current.lastEventSequence));
        }
    }
    
    public EntitySnapshot getEntityCurrentState(String entityId) {
        return snapshots.get(entityId);
    }
    
    public List<Event> getEntityHistory(String entityId) {
        return eventStore.stream()
                .map(store -> store.event)
                .filter(event -> event.entityId.equals(entityId))
                .sorted(Comparator.comparing(event -> event.sequenceNumber))
                .collect(Collectors.toList());
    }
    
    @Override
    public List<DataChange> getPendingChanges() {
        // In event sourcing, all events are immediately stored
        return Collections.emptyList();
    }
    
    @Override
    public void markChangeAsApplied(String changeId) {
        // Events are immediately applied in event sourcing
        statistics.appliedChanges.incrementAndGet();
    }
    
    @Override
    public SyncStatistics getStatistics() { return statistics; }
    
    // Event sourcing specific classes
    static class Event {
        public final long sequenceNumber;
        public final String entityId;
        public final String entityType;
        public final String eventType;
        public final String eventData;
        public final LocalDateTime timestamp;
        public final String source;
        public final Map<String, Object> metadata;
        
        public Event(long sequenceNumber, String entityId, String entityType, String eventType,
                    String eventData, LocalDateTime timestamp, String source, Map<String, Object> metadata) {
            this.sequenceNumber = sequenceNumber;
            this.entityId = entityId;
            this.entityType = entityType;
            this.eventType = eventType;
            this.eventData = eventData;
            this.timestamp = timestamp;
            this.source = source;
            this.metadata = metadata != null ? new HashMap<>(metadata) : new HashMap<>();
        }
    }
    
    static class EventStore {
        public final Event event;
        public final LocalDateTime storedAt;
        
        public EventStore(Event event, LocalDateTime storedAt) {
            this.event = event;
            this.storedAt = storedAt;
        }
    }
    
    static class EntitySnapshot {
        public final String entityId;
        public final String entityType;
        public final Map<String, Object> currentState;
        public long lastEventSequence;
        public LocalDateTime lastUpdated;
        
        public EntitySnapshot(String entityId, String entityType, Map<String, Object> currentState, long lastEventSequence) {
            this.entityId = entityId;
            this.entityType = entityType;
            this.currentState = currentState;
            this.lastEventSequence = lastEventSequence;
            this.lastUpdated = LocalDateTime.now();
        }
    }
}

// Main demonstration class
public class DataSynchronizationPatterns {
    
    public static void main(String[] args) throws Exception {
        System.out.println("=".repeat(80));
        System.out.println("Data Synchronization Patterns Implementation");
        System.out.println("Episode 41: Database Replication Strategies");
        System.out.println("Indian Banking और E-commerce Scenarios");
        System.out.println("=".repeat(80));
        
        DataSynchronizationPatterns demo = new DataSynchronizationPatterns();
        
        // Demonstrate WAL pattern with banking scenario
        System.out.println("\n--- Write-Ahead Logging Pattern (Banking) ---");
        demo.demonstrateWALPattern();
        
        // Demonstrate CDC pattern with e-commerce scenario
        System.out.println("\n--- Change Data Capture Pattern (E-commerce) ---");
        demo.demonstrateCDCPattern();
        
        // Demonstrate Event Sourcing pattern with financial audit
        System.out.println("\n--- Event Sourcing Pattern (Financial Audit) ---");
        demo.demonstrateEventSourcingPattern();
        
        // Performance comparison
        System.out.println("\n--- Performance Comparison ---");
        demo.comparePatternPerformance();
    }
    
    public void demonstrateWALPattern() throws Exception {
        WriteAheadLoggingPattern wal = new WriteAheadLoggingPattern();
        
        System.out.println("Processing banking transactions with WAL...");
        
        // Simulate banking transactions
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("branch", "Mumbai Central");
        metadata.put("transaction_type", "NEFT");
        
        // Account balance updates
        wal.processChange(new DataChange("ACC123456", "ACCOUNT_BALANCE", ChangeType.UPDATE, 
            "50000.00", "55000.00", "BANKING_SYSTEM", metadata));
            
        wal.processChange(new DataChange("ACC789012", "ACCOUNT_BALANCE", ChangeType.UPDATE,
            "25000.00", "20000.00", "BANKING_SYSTEM", metadata));
            
        // Large transaction (requires reporting)
        metadata.put("large_transaction", true);
        wal.processChange(new DataChange("ACC345678", "ACCOUNT_BALANCE", ChangeType.UPDATE,
            "1000000.00", "300000.00", "BANKING_SYSTEM", metadata));
        
        Thread.sleep(100); // Allow processing
        
        SyncStatistics stats = wal.getStatistics();
        System.out.println(String.format("WAL Statistics: %d total, %d applied, %.1f%% success rate",
            stats.totalChanges.get(), stats.appliedChanges.get(), stats.getSuccessRate()));
            
        wal.shutdown();
    }
    
    public void demonstrateCDCPattern() throws Exception {
        ChangeDataCapturePattern cdc = new ChangeDataCapturePattern();
        
        System.out.println("Processing e-commerce changes with CDC...");
        
        // Simulate inventory changes
        Map<String, Object> inventoryMeta = new HashMap<>();
        inventoryMeta.put("product_category", "electronics");
        inventoryMeta.put("warehouse", "Mumbai_WH");
        
        cdc.processChange(new DataChange("PROD001", "PRODUCT_INVENTORY", ChangeType.UPDATE,
            "100", "85", "INVENTORY_SYSTEM", inventoryMeta));
            
        cdc.processChange(new DataChange("PROD002", "PRODUCT_INVENTORY", ChangeType.UPDATE,
            "50", "5", "INVENTORY_SYSTEM", inventoryMeta)); // Low stock
            
        // Order status changes
        Map<String, Object> orderMeta = new HashMap<>();
        orderMeta.put("customer_id", "CUST12345");
        orderMeta.put("order_value", 15999.00);
        
        cdc.processChange(new DataChange("ORD001", "ORDER_STATUS", ChangeType.UPDATE,
            "PENDING", "CONFIRMED", "ORDER_SYSTEM", orderMeta));
            
        cdc.processChange(new DataChange("ORD001", "ORDER_STATUS", ChangeType.UPDATE,
            "CONFIRMED", "SHIPPED", "ORDER_SYSTEM", orderMeta));
            
        // Price changes
        Map<String, Object> priceMeta = new HashMap<>();
        priceMeta.put("product_name", "iPhone 15");
        
        cdc.processChange(new DataChange("PROD003", "PRICE_UPDATE", ChangeType.UPDATE,
            "79999.00", "69999.00", "PRICING_SYSTEM", priceMeta)); // Discount
        
        Thread.sleep(2000); // Allow batch processing
        
        SyncStatistics stats = cdc.getStatistics();
        System.out.println(String.format("CDC Statistics: %d total, %d applied, %.1f%% success rate",
            stats.totalChanges.get(), stats.appliedChanges.get(), stats.getSuccessRate()));
            
        cdc.shutdown();
    }
    
    public void demonstrateEventSourcingPattern() throws Exception {
        EventSourcingPattern eventSourcing = new EventSourcingPattern();
        
        System.out.println("Processing financial events with Event Sourcing...");
        
        // Bank account lifecycle
        Map<String, Object> accountMeta = new HashMap<>();
        accountMeta.put("customer_id", "CUST789");
        accountMeta.put("account_type", "SAVINGS");
        
        eventSourcing.processChange(new DataChange("ACC999888", "BANK_ACCOUNT", ChangeType.INSERT,
            null, "ACCOUNT_CREATED", "CORE_BANKING", accountMeta));
            
        eventSourcing.processChange(new DataChange("ACC999888", "BANK_ACCOUNT", ChangeType.UPDATE,
            null, "10000.00", "CORE_BANKING", accountMeta)); // Deposit
            
        eventSourcing.processChange(new DataChange("ACC999888", "BANK_ACCOUNT", ChangeType.UPDATE,
            null, "2500.00", "CORE_BANKING", accountMeta)); // Withdrawal
            
        // Order lifecycle
        Map<String, Object> orderMeta = new HashMap<>();
        orderMeta.put("customer_id", "CUST456");
        orderMeta.put("total_amount", 5999.00);
        
        eventSourcing.processChange(new DataChange("ORD789", "ORDER", ChangeType.INSERT,
            null, "ORDER_CREATED", "E_COMMERCE", orderMeta));
            
        eventSourcing.processChange(new DataChange("ORD789", "ORDER", ChangeType.UPDATE,
            null, "ORDER_CONFIRMED", "E_COMMERCE", orderMeta));
            
        orderMeta.put("tracking_number", "TRK123456789");
        eventSourcing.processChange(new DataChange("ORD789", "ORDER", ChangeType.UPDATE,
            null, "ORDER_SHIPPED", "E_COMMERCE", orderMeta));
        
        Thread.sleep(50); // Allow processing
        
        // Show entity current state
        EntitySnapshot accountState = eventSourcing.getEntityCurrentState("ACC999888");
        if (accountState != null) {
            System.out.println(String.format("Account current state: %s", accountState.currentState));
        }
        
        EntitySnapshot orderState = eventSourcing.getEntityCurrentState("ORD789");
        if (orderState != null) {
            System.out.println(String.format("Order current state: %s", orderState.currentState));
        }
        
        // Show event history
        List<Event> accountHistory = eventSourcing.getEntityHistory("ACC999888");
        System.out.println(String.format("Account event history: %d events", accountHistory.size()));
        
        SyncStatistics stats = eventSourcing.getStatistics();
        System.out.println(String.format("Event Sourcing Statistics: %d total, %d applied, %.1f%% success rate",
            stats.totalChanges.get(), stats.appliedChanges.get(), stats.getSuccessRate()));
    }
    
    public void comparePatternPerformance() throws Exception {
        System.out.println("Comparing synchronization pattern performance...");
        
        int testOperations = 500;
        
        // Test WAL pattern
        WriteAheadLoggingPattern wal = new WriteAheadLoggingPattern();
        long walStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < testOperations; i++) {
            wal.processChange(new DataChange("TEST" + i, "TEST_ENTITY", ChangeType.UPDATE,
                "old_value", "new_value", "TEST_SYSTEM", null));
        }
        
        long walDuration = System.currentTimeMillis() - walStartTime;
        SyncStatistics walStats = wal.getStatistics();
        
        // Test CDC pattern
        ChangeDataCapturePattern cdc = new ChangeDataCapturePattern();
        long cdcStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < testOperations; i++) {
            cdc.processChange(new DataChange("TEST" + i, "PRODUCT_INVENTORY", ChangeType.UPDATE,
                "old_value", "new_value", "TEST_SYSTEM", null));
        }
        
        Thread.sleep(1000); // Allow CDC batch processing
        long cdcDuration = System.currentTimeMillis() - cdcStartTime;
        SyncStatistics cdcStats = cdc.getStatistics();
        
        // Test Event Sourcing pattern
        EventSourcingPattern eventSourcing = new EventSourcingPattern();
        long esStartTime = System.currentTimeMillis();
        
        for (int i = 0; i < testOperations; i++) {
            eventSourcing.processChange(new DataChange("TEST" + i, "BANK_ACCOUNT", ChangeType.UPDATE,
                "old_value", "new_value", "TEST_SYSTEM", null));
        }
        
        long esDuration = System.currentTimeMillis() - esStartTime;
        SyncStatistics esStats = eventSourcing.getStatistics();
        
        // Print comparison
        System.out.println("\nPerformance Comparison:");
        System.out.println("Pattern                | Duration (ms) | Throughput (ops/sec) | Success Rate (%)");
        System.out.println("-".repeat(80));
        
        System.out.println(String.format("%-18s | %11d | %16.1f | %12.1f",
            "WAL", walDuration, (double) testOperations / walDuration * 1000, walStats.getSuccessRate()));
            
        System.out.println(String.format("%-18s | %11d | %16.1f | %12.1f",
            "CDC", cdcDuration, (double) testOperations / cdcDuration * 1000, cdcStats.getSuccessRate()));
            
        System.out.println(String.format("%-18s | %11d | %16.1f | %12.1f",
            "Event Sourcing", esDuration, (double) testOperations / esDuration * 1000, esStats.getSuccessRate()));
        
        // Cleanup
        wal.shutdown();
        cdc.shutdown();
    }
}