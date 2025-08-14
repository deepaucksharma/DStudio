/**
 * Episode 41: Database Replication Strategies - Flipkart Inventory CDC System
 * Change Data Capture implementation for large-scale e-commerce inventory
 * 
 * यह implementation demonstrate करती है कि कैसे Flipkart जैसे large e-commerce platforms
 * में inventory changes को real-time capture और replicate किया जाता है।
 * जैसे Mumbai के stock market में हर trade instantly सभी exchanges में sync होती है,
 * वैसे ही inventory changes भी real-time में सभी systems में propagate होनी चाहिए।
 * 
 * Real-world Usage:
 * - Flipkart: Big Billion Days के दौरान real-time inventory sync
 * - Amazon: Product availability across warehouses
 * - Myntra: Fashion inventory management with size/color variants
 * 
 * Author: Hindi Tech Podcast Team
 * Episode: 41 - Database Replication Strategies
 */

package com.episode41.replication.ecommerce;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.sql.*;
import java.io.*;
import java.math.BigDecimal;
import javax.sql.DataSource;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.core.JsonProcessingException;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;
import org.apache.kafka.clients.producer.ProducerConfig;
import org.apache.kafka.common.serialization.StringSerializer;

/**
 * Flipkart Inventory Change Data Capture System
 * Real-time inventory synchronization across multiple warehouses and systems
 */
public class FlipkartInventoryCDC {
    
    private static final Logger logger = LoggerFactory.getLogger(FlipkartInventoryCDC.class);
    private static final Logger inventoryLogger = LoggerFactory.getLogger("FLIPKART_INVENTORY");
    
    // CDC Configuration
    private static final int CDC_BATCH_SIZE = 1000;
    private static final int CDC_POLL_INTERVAL_MS = 1000;
    private static final int MAX_REPLICATION_LAG_MS = 5000;
    private static final int KAFKA_BUFFER_SIZE = 64 * 1024; // 64KB
    
    // Big Billion Days special configuration
    private static final int BBD_BATCH_SIZE = 5000;
    private static final int BBD_POLL_INTERVAL_MS = 500;
    private static final double BBD_SCALE_FACTOR = 5.0;
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(8);
    private final ExecutorService cdcExecutor = Executors.newFixedThreadPool(10);
    
    // Core components
    private final Map<String, FlipkartWarehouse> warehouses = new ConcurrentHashMap<>();
    private final Map<String, DataSource> warehouseDataSources = new ConcurrentHashMap<>();
    private final KafkaProducer<String, String> kafkaProducer;
    private final FlipkartInventoryCache inventoryCache;
    private final CDCEventProcessor eventProcessor;
    
    // State management
    private final AtomicBoolean cdcActive = new AtomicBoolean(false);
    private final AtomicBoolean bigBillionDaysMode = new AtomicBoolean(false);
    private final AtomicLong totalEventsProcessed = new AtomicLong(0);
    private final AtomicLong eventsPerSecond = new AtomicLong(0);
    
    // CDC Position tracking
    private final Map<String, Long> lastProcessedPosition = new ConcurrentHashMap<>();
    private final Map<String, LocalDateTime> lastProcessedTime = new ConcurrentHashMap<>();
    
    /**
     * Flipkart Warehouse configuration
     */
    public static class FlipkartWarehouse {
        private final String warehouseId;
        private final String name;
        private final String city;
        private final String region;
        private final int capacity;
        private final Set<String> productCategories;
        private volatile boolean isActive = true;
        private volatile int currentLoad = 0;
        private volatile double utilizationPercentage = 0.0;
        
        // Big Billion Days specific
        private volatile boolean bbdActive = false;
        private volatile int bbdCapacityMultiplier = 3;
        
        public FlipkartWarehouse(String warehouseId, String name, String city, String region,
                               int capacity, Set<String> categories) {
            this.warehouseId = warehouseId;
            this.name = name;
            this.city = city;
            this.region = region;
            this.capacity = capacity;
            this.productCategories = categories;
        }
        
        // Getters
        public String getWarehouseId() { return warehouseId; }
        public String getName() { return name; }
        public String getCity() { return city; }
        public String getRegion() { return region; }
        public boolean isActive() { return isActive; }
        public void setActive(boolean active) { this.isActive = active; }
        
        public int getEffectiveCapacity() {
            return bbdActive ? capacity * bbdCapacityMultiplier : capacity;
        }
        
        public void enableBigBillionDays() {
            this.bbdActive = true;
            logger.info("Big Billion Days mode enabled for warehouse: {}", warehouseId);
        }
        
        public void disableBigBillionDays() {
            this.bbdActive = false;
            logger.info("Big Billion Days mode disabled for warehouse: {}", warehouseId);
        }
        
        public Map<String, Object> getMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("warehouse_id", warehouseId);
            metrics.put("current_load", currentLoad);
            metrics.put("capacity", getEffectiveCapacity());
            metrics.put("utilization", utilizationPercentage);
            metrics.put("is_active", isActive);
            metrics.put("bbd_active", bbdActive);
            metrics.put("categories", productCategories.size());
            return metrics;
        }
    }
    
    /**
     * Inventory change event
     */
    public static class InventoryChangeEvent {
        private String eventId;
        private String warehouseId;
        private String productId;
        private String sku;
        private LocalDateTime timestamp;
        private ChangeType changeType;
        private Map<String, Object> oldValues;
        private Map<String, Object> newValues;
        private String changeReason;
        private boolean bbdEvent = false;
        private Map<String, Object> metadata;
        
        public enum ChangeType {
            INSERT, UPDATE, DELETE, BULK_UPDATE, RESTOCK, OUT_OF_STOCK
        }
        
        // Constructors
        public InventoryChangeEvent() {
            this.eventId = generateEventId();
            this.timestamp = LocalDateTime.now();
            this.metadata = new HashMap<>();
        }
        
        public InventoryChangeEvent(String warehouseId, String productId, ChangeType changeType) {
            this();
            this.warehouseId = warehouseId;
            this.productId = productId;
            this.changeType = changeType;
        }
        
        // Getters and Setters
        public String getEventId() { return eventId; }
        public void setEventId(String eventId) { this.eventId = eventId; }
        
        public String getWarehouseId() { return warehouseId; }
        public void setWarehouseId(String warehouseId) { this.warehouseId = warehouseId; }
        
        public String getProductId() { return productId; }
        public void setProductId(String productId) { this.productId = productId; }
        
        public String getSku() { return sku; }
        public void setSku(String sku) { this.sku = sku; }
        
        public LocalDateTime getTimestamp() { return timestamp; }
        public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
        
        public ChangeType getChangeType() { return changeType; }
        public void setChangeType(ChangeType changeType) { this.changeType = changeType; }
        
        public Map<String, Object> getOldValues() { return oldValues; }
        public void setOldValues(Map<String, Object> oldValues) { this.oldValues = oldValues; }
        
        public Map<String, Object> getNewValues() { return newValues; }
        public void setNewValues(Map<String, Object> newValues) { this.newValues = newValues; }
        
        public String getChangeReason() { return changeReason; }
        public void setChangeReason(String changeReason) { this.changeReason = changeReason; }
        
        public boolean isBbdEvent() { return bbdEvent; }
        public void setBbdEvent(boolean bbdEvent) { this.bbdEvent = bbdEvent; }
        
        public Map<String, Object> getMetadata() { return metadata; }
        public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
        
        private static String generateEventId() {
            return String.format("INV_%s_%d", 
                               LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss")),
                               System.nanoTime() % 1000000);
        }
        
        public String toKafkaMessage() throws JsonProcessingException {
            Map<String, Object> message = new HashMap<>();
            message.put("event_id", eventId);
            message.put("warehouse_id", warehouseId);
            message.put("product_id", productId);
            message.put("sku", sku);
            message.put("timestamp", timestamp.toString());
            message.put("change_type", changeType.name());
            message.put("old_values", oldValues);
            message.put("new_values", newValues);
            message.put("change_reason", changeReason);
            message.put("bbd_event", bbdEvent);
            message.put("metadata", metadata);
            
            ObjectMapper mapper = new ObjectMapper();
            return mapper.writeValueAsString(message);
        }
    }
    
    /**
     * Flipkart Inventory Cache for quick lookups
     */
    private static class FlipkartInventoryCache {
        private final ConcurrentHashMap<String, Map<String, Object>> cache = new ConcurrentHashMap<>();
        private final ScheduledExecutorService cacheCleanup = Executors.newSingleThreadScheduledExecutor();
        
        public FlipkartInventoryCache() {
            // Cleanup expired entries every 5 minutes
            cacheCleanup.scheduleWithFixedDelay(this::cleanupExpiredEntries, 5, 5, TimeUnit.MINUTES);
        }
        
        public void put(String key, Map<String, Object> value) {
            value.put("cache_timestamp", System.currentTimeMillis());
            cache.put(key, value);
        }
        
        public Map<String, Object> get(String key) {
            return cache.get(key);
        }
        
        public boolean containsKey(String key) {
            return cache.containsKey(key);
        }
        
        public void invalidate(String key) {
            cache.remove(key);
        }
        
        public int size() {
            return cache.size();
        }
        
        private void cleanupExpiredEntries() {
            long now = System.currentTimeMillis();
            long expireTime = 30 * 60 * 1000; // 30 minutes
            
            cache.entrySet().removeIf(entry -> {
                Map<String, Object> value = entry.getValue();
                Long timestamp = (Long) value.get("cache_timestamp");
                return timestamp != null && (now - timestamp) > expireTime;
            });
        }
        
        public void shutdown() {
            cacheCleanup.shutdown();
        }
    }
    
    /**
     * CDC Event Processor
     */
    private class CDCEventProcessor {
        private final BlockingQueue<InventoryChangeEvent> eventQueue = new LinkedBlockingQueue<>(10000);
        private final AtomicBoolean processing = new AtomicBoolean(false);
        
        public void submitEvent(InventoryChangeEvent event) {
            if (!eventQueue.offer(event)) {
                logger.warn("Event queue full, dropping event: {}", event.getEventId());
            }
        }
        
        public void startProcessing() {
            if (processing.compareAndSet(false, true)) {
                cdcExecutor.submit(this::processEvents);
                logger.info("CDC Event Processor started");
            }
        }
        
        public void stopProcessing() {
            processing.set(false);
            logger.info("CDC Event Processor stopped");
        }
        
        private void processEvents() {
            List<InventoryChangeEvent> batch = new ArrayList<>();
            
            while (processing.get() || !eventQueue.isEmpty()) {
                try {
                    // Collect batch of events
                    batch.clear();
                    InventoryChangeEvent event = eventQueue.poll(1, TimeUnit.SECONDS);
                    
                    if (event != null) {
                        batch.add(event);
                        
                        // Collect additional events for batch processing
                        int currentBatchSize = bigBillionDaysMode.get() ? BBD_BATCH_SIZE : CDC_BATCH_SIZE;
                        eventQueue.drainTo(batch, currentBatchSize - 1);
                        
                        // Process batch
                        processBatch(batch);
                    }
                    
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    logger.error("Error processing events batch: {}", e.getMessage(), e);
                }
            }
        }
        
        private void processBatch(List<InventoryChangeEvent> events) {
            if (events.isEmpty()) return;
            
            long startTime = System.currentTimeMillis();
            
            try {
                // Group events by warehouse for efficient processing
                Map<String, List<InventoryChangeEvent>> eventsByWarehouse = events.stream()
                    .collect(Collectors.groupingBy(InventoryChangeEvent::getWarehouseId));
                
                // Process each warehouse's events
                List<CompletableFuture<Void>> futures = new ArrayList<>();
                
                for (Map.Entry<String, List<InventoryChangeEvent>> entry : eventsByWarehouse.entrySet()) {
                    String warehouseId = entry.getKey();
                    List<InventoryChangeEvent> warehouseEvents = entry.getValue();
                    
                    CompletableFuture<Void> future = CompletableFuture.runAsync(() -> {
                        try {
                            processWarehouseEvents(warehouseId, warehouseEvents);
                        } catch (Exception e) {
                            logger.error("Error processing events for warehouse {}: {}", warehouseId, e.getMessage(), e);
                        }
                    }, cdcExecutor);
                    
                    futures.add(future);
                }
                
                // Wait for all warehouse processing to complete
                CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get(30, TimeUnit.SECONDS);
                
                // Update metrics
                totalEventsProcessed.addAndGet(events.size());
                long duration = System.currentTimeMillis() - startTime;
                
                inventoryLogger.info("Processed batch of {} events in {}ms (avg: {}ms/event)",
                                   events.size(), duration, duration / events.size());
                
            } catch (Exception e) {
                logger.error("Batch processing failed: {}", e.getMessage(), e);
            }
        }
        
        private void processWarehouseEvents(String warehouseId, List<InventoryChangeEvent> events) {
            FlipkartWarehouse warehouse = warehouses.get(warehouseId);
            if (warehouse == null || !warehouse.isActive()) {
                logger.warn("Warehouse {} not active, skipping {} events", warehouseId, events.size());
                return;
            }
            
            for (InventoryChangeEvent event : events) {
                try {
                    // Apply business logic based on event type
                    processInventoryEvent(event);
                    
                    // Publish to Kafka for downstream systems
                    publishToKafka(event);
                    
                    // Update cache
                    updateInventoryCache(event);
                    
                    // Special handling for Big Billion Days
                    if (event.isBbdEvent()) {
                        handleBigBillionDaysEvent(event);
                    }
                    
                } catch (Exception e) {
                    logger.error("Error processing event {}: {}", event.getEventId(), e.getMessage(), e);
                }
            }
        }
        
        private void processInventoryEvent(InventoryChangeEvent event) {
            switch (event.getChangeType()) {
                case INSERT:
                    handleInventoryInsert(event);
                    break;
                case UPDATE:
                    handleInventoryUpdate(event);
                    break;
                case DELETE:
                    handleInventoryDelete(event);
                    break;
                case BULK_UPDATE:
                    handleBulkUpdate(event);
                    break;
                case RESTOCK:
                    handleRestock(event);
                    break;
                case OUT_OF_STOCK:
                    handleOutOfStock(event);
                    break;
                default:
                    logger.warn("Unknown change type: {}", event.getChangeType());
            }
        }
        
        private void handleInventoryInsert(InventoryChangeEvent event) {
            inventoryLogger.info("New product added: {} in warehouse {}", 
                               event.getProductId(), event.getWarehouseId());
            
            // Validate new product data
            if (event.getNewValues() != null) {
                validateProductData(event.getNewValues());
            }
        }
        
        private void handleInventoryUpdate(InventoryChangeEvent event) {
            Map<String, Object> oldValues = event.getOldValues();
            Map<String, Object> newValues = event.getNewValues();
            
            if (oldValues != null && newValues != null) {
                // Check for significant quantity changes
                Integer oldQty = (Integer) oldValues.get("quantity");
                Integer newQty = (Integer) newValues.get("quantity");
                
                if (oldQty != null && newQty != null) {
                    int qtyChange = newQty - oldQty;
                    
                    if (Math.abs(qtyChange) > 100) {
                        inventoryLogger.info("Significant quantity change: {} ({} -> {}) for product {} in warehouse {}",
                                           qtyChange, oldQty, newQty, event.getProductId(), event.getWarehouseId());
                    }
                    
                    // Alert for low stock
                    if (newQty < 10) {
                        event.getMetadata().put("low_stock_alert", true);
                        inventoryLogger.warn("Low stock alert: {} units remaining for product {} in warehouse {}",
                                           newQty, event.getProductId(), event.getWarehouseId());
                    }
                }
            }
        }
        
        private void handleInventoryDelete(InventoryChangeEvent event) {
            inventoryLogger.info("Product removed: {} from warehouse {}", 
                               event.getProductId(), event.getWarehouseId());
            
            // Cleanup related cache entries
            String cacheKey = String.format("%s:%s", event.getWarehouseId(), event.getProductId());
            inventoryCache.invalidate(cacheKey);
        }
        
        private void handleBulkUpdate(InventoryChangeEvent event) {
            inventoryLogger.info("Bulk update processed for warehouse {}: {}", 
                               event.getWarehouseId(), event.getChangeReason());
            
            // Mark event for special processing
            event.getMetadata().put("bulk_operation", true);
        }
        
        private void handleRestock(InventoryChangeEvent event) {
            Map<String, Object> newValues = event.getNewValues();
            if (newValues != null) {
                Integer newQty = (Integer) newValues.get("quantity");
                if (newQty != null && newQty > 0) {
                    inventoryLogger.info("Product restocked: {} (qty: {}) in warehouse {}", 
                                       event.getProductId(), newQty, event.getWarehouseId());
                    
                    // Notify recommendation system about availability
                    event.getMetadata().put("notify_recommendation_system", true);
                }
            }
        }
        
        private void handleOutOfStock(InventoryChangeEvent event) {
            inventoryLogger.warn("Product out of stock: {} in warehouse {}", 
                               event.getProductId(), event.getWarehouseId());
            
            // Mark for immediate replication to prevent overselling
            event.getMetadata().put("high_priority", true);
            event.getMetadata().put("replicate_immediately", true);
        }
        
        private void handleBigBillionDaysEvent(InventoryChangeEvent event) {
            // Special processing for Big Billion Days events
            event.getMetadata().put("bbd_priority", true);
            
            // Check for flash sale scenarios
            Map<String, Object> newValues = event.getNewValues();
            if (newValues != null) {
                Integer quantity = (Integer) newValues.get("quantity");
                Boolean isFlashSale = (Boolean) newValues.get("is_flash_sale");
                
                if (Boolean.TRUE.equals(isFlashSale) && quantity != null && quantity < 50) {
                    // Low stock in flash sale - high priority replication
                    event.getMetadata().put("flash_sale_low_stock", true);
                    event.getMetadata().put("replication_priority", "CRITICAL");
                    
                    inventoryLogger.warn("Flash sale low stock: {} units for product {} in warehouse {}",
                                       quantity, event.getProductId(), event.getWarehouseId());
                }
            }
        }
        
        private void validateProductData(Map<String, Object> productData) {
            // Basic validation for new product data
            if (productData.get("product_id") == null) {
                throw new IllegalArgumentException("Product ID is required");
            }
            
            if (productData.get("sku") == null) {
                throw new IllegalArgumentException("SKU is required");
            }
            
            Object quantity = productData.get("quantity");
            if (quantity == null || (Integer) quantity < 0) {
                throw new IllegalArgumentException("Valid quantity is required");
            }
        }
    }
    
    /**
     * Initialize Flipkart Inventory CDC System
     */
    public FlipkartInventoryCDC() {
        // Initialize Flipkart warehouses across India
        initializeFlipkartWarehouses();
        
        // Initialize database connections
        initializeWarehouseConnections();
        
        // Initialize Kafka producer
        this.kafkaProducer = createKafkaProducer();
        
        // Initialize components
        this.inventoryCache = new FlipkartInventoryCache();
        this.eventProcessor = new CDCEventProcessor();
        
        logger.info("Flipkart Inventory CDC System initialized with {} warehouses", warehouses.size());
    }
    
    /**
     * Initialize Flipkart warehouses across India
     */
    private void initializeFlipkartWarehouses() {
        // Mumbai Region
        warehouses.put("FK_MUM_001", new FlipkartWarehouse(
            "FK_MUM_001",
            "Flipkart Mumbai Bhiwandi FC",
            "Mumbai",
            "Western",
            100000,
            Set.of("Electronics", "Fashion", "Home", "Books")
        ));
        
        // Bangalore Region
        warehouses.put("FK_BLR_001", new FlipkartWarehouse(
            "FK_BLR_001", 
            "Flipkart Bangalore Whitefield FC",
            "Bangalore",
            "Southern",
            120000,
            Set.of("Electronics", "Fashion", "Books", "Grocery")
        ));
        
        // Delhi Region
        warehouses.put("FK_DEL_001", new FlipkartWarehouse(
            "FK_DEL_001",
            "Flipkart Delhi Sonipat FC", 
            "Delhi",
            "Northern",
            80000,
            Set.of("Fashion", "Home", "Electronics", "Sports")
        ));
        
        // Chennai Region  
        warehouses.put("FK_CHN_001", new FlipkartWarehouse(
            "FK_CHN_001",
            "Flipkart Chennai Sriperumbudur FC",
            "Chennai", 
            "Southern",
            70000,
            Set.of("Electronics", "Books", "Home", "Grocery")
        ));
        
        // Kolkata Region
        warehouses.put("FK_KOL_001", new FlipkartWarehouse(
            "FK_KOL_001",
            "Flipkart Kolkata New Town FC",
            "Kolkata",
            "Eastern", 
            50000,
            Set.of("Books", "Fashion", "Electronics", "Home")
        ));
        
        // Hyderabad Region
        warehouses.put("FK_HYD_001", new FlipkartWarehouse(
            "FK_HYD_001",
            "Flipkart Hyderabad Medchal FC",
            "Hyderabad",
            "Southern",
            90000,
            Set.of("Electronics", "Fashion", "Grocery", "Sports")
        ));
        
        logger.info("Initialized {} Flipkart warehouses across India", warehouses.size());
    }
    
    /**
     * Initialize database connections for warehouses
     */
    private void initializeWarehouseConnections() {
        for (FlipkartWarehouse warehouse : warehouses.values()) {
            try {
                HikariConfig config = new HikariConfig();
                config.setJdbcUrl(String.format("jdbc:postgresql://warehouse-%s.flipkart.internal:5432/inventory", 
                                               warehouse.getWarehouseId().toLowerCase()));
                config.setUsername("inventory_user");
                config.setPassword("secure_inventory_password");
                config.setMaximumPoolSize(20);
                config.setMinimumIdle(5);
                config.setConnectionTimeout(30000);
                config.setIdleTimeout(300000);
                config.setMaxLifetime(900000);
                
                // Flipkart-specific configurations
                config.addDataSourceProperty("ApplicationName", "Flipkart_Inventory_CDC");
                config.addDataSourceProperty("reWriteBatchedInserts", "true");
                
                HikariDataSource dataSource = new HikariDataSource(config);
                warehouseDataSources.put(warehouse.getWarehouseId(), dataSource);
                
                logger.info("Database connection initialized for warehouse: {}", warehouse.getWarehouseId());
                
            } catch (Exception e) {
                logger.error("Failed to initialize database for warehouse {}: {}", 
                           warehouse.getWarehouseId(), e.getMessage(), e);
            }
        }
    }
    
    /**
     * Create Kafka producer for event streaming
     */
    private KafkaProducer<String, String> createKafkaProducer() {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-cluster.flipkart.internal:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, KAFKA_BUFFER_SIZE);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10);
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 32 * 1024 * 1024); // 32MB
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy");
        
        // Flipkart-specific configurations
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "flipkart-inventory-cdc");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        return new KafkaProducer<>(props);
    }
    
    /**
     * Start CDC monitoring and processing
     */
    public void startCDC() {
        if (cdcActive.compareAndSet(false, true)) {
            logger.info("Starting Flipkart Inventory CDC System...");
            
            // Start event processor
            eventProcessor.startProcessing();
            
            // Start CDC monitoring for each warehouse
            for (String warehouseId : warehouses.keySet()) {
                scheduler.scheduleWithFixedDelay(
                    () -> performCDCCapture(warehouseId),
                    0,
                    getCurrentPollInterval(),
                    TimeUnit.MILLISECONDS
                );
            }
            
            // Start metrics collection
            scheduler.scheduleWithFixedDelay(
                this::collectMetrics,
                0,
                10,
                TimeUnit.SECONDS
            );
            
            // Start Big Billion Days monitoring
            scheduler.scheduleWithFixedDelay(
                this::monitorBigBillionDays,
                0,
                60,
                TimeUnit.SECONDS
            );
            
            logger.info("Flipkart Inventory CDC System started successfully");
        }
    }
    
    /**
     * Get current poll interval based on system mode
     */
    private int getCurrentPollInterval() {
        return bigBillionDaysMode.get() ? BBD_POLL_INTERVAL_MS : CDC_POLL_INTERVAL_MS;
    }
    
    /**
     * Perform CDC capture for a specific warehouse
     */
    private void performCDCCapture(String warehouseId) {
        try {
            FlipkartWarehouse warehouse = warehouses.get(warehouseId);
            if (warehouse == null || !warehouse.isActive()) {
                return;
            }
            
            DataSource dataSource = warehouseDataSources.get(warehouseId);
            if (dataSource == null) {
                return;
            }
            
            // Get last processed position for this warehouse
            Long lastPosition = lastProcessedPosition.get(warehouseId);
            if (lastPosition == null) {
                lastPosition = getInitialCDCPosition(warehouseId);
                lastProcessedPosition.put(warehouseId, lastPosition);
            }
            
            // Capture changes since last position
            List<InventoryChangeEvent> events = captureInventoryChanges(warehouseId, dataSource, lastPosition);
            
            if (!events.isEmpty()) {
                // Process captured events
                for (InventoryChangeEvent event : events) {
                    // Mark Big Billion Days events if mode is active
                    if (bigBillionDaysMode.get()) {
                        event.setBbdEvent(true);
                    }
                    
                    eventProcessor.submitEvent(event);
                }
                
                // Update last processed position
                Long maxPosition = events.stream()
                    .mapToLong(event -> (Long) event.getMetadata().getOrDefault("cdc_position", 0L))
                    .max()
                    .orElse(lastPosition);
                
                lastProcessedPosition.put(warehouseId, maxPosition);
                lastProcessedTime.put(warehouseId, LocalDateTime.now());
                
                logger.debug("Captured {} inventory changes from warehouse {}", events.size(), warehouseId);
            }
            
        } catch (Exception e) {
            logger.error("CDC capture failed for warehouse {}: {}", warehouseId, e.getMessage(), e);
        }
    }
    
    /**
     * Get initial CDC position for warehouse
     */
    private Long getInitialCDCPosition(String warehouseId) {
        DataSource dataSource = warehouseDataSources.get(warehouseId);
        if (dataSource == null) {
            return 0L;
        }
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(
                 "SELECT COALESCE(MAX(cdc_position), 0) FROM inventory_cdc_log WHERE warehouse_id = ?")) {
            
            stmt.setString(1, warehouseId);
            ResultSet rs = stmt.executeQuery();
            
            if (rs.next()) {
                return rs.getLong(1);
            }
            
        } catch (SQLException e) {
            logger.error("Failed to get initial CDC position for warehouse {}: {}", warehouseId, e.getMessage());
        }
        
        return 0L;
    }
    
    /**
     * Capture inventory changes from database
     */
    private List<InventoryChangeEvent> captureInventoryChanges(String warehouseId, DataSource dataSource, Long fromPosition) {
        List<InventoryChangeEvent> events = new ArrayList<>();
        
        String query = """
            SELECT 
                cdc.cdc_position,
                cdc.operation_type,
                cdc.product_id,
                cdc.sku,
                cdc.old_values,
                cdc.new_values,
                cdc.change_timestamp,
                cdc.change_reason,
                inv.category,
                inv.brand,
                inv.is_flash_sale
            FROM inventory_cdc_log cdc
            LEFT JOIN inventory inv ON cdc.product_id = inv.product_id AND cdc.warehouse_id = inv.warehouse_id
            WHERE cdc.warehouse_id = ? AND cdc.cdc_position > ?
            ORDER BY cdc.cdc_position
            LIMIT ?
            """;
        
        int batchSize = bigBillionDaysMode.get() ? BBD_BATCH_SIZE : CDC_BATCH_SIZE;
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {
            
            stmt.setString(1, warehouseId);
            stmt.setLong(2, fromPosition);
            stmt.setInt(3, batchSize);
            
            ResultSet rs = stmt.executeQuery();
            
            while (rs.next()) {
                InventoryChangeEvent event = new InventoryChangeEvent(warehouseId, rs.getString("product_id"),
                    InventoryChangeEvent.ChangeType.valueOf(rs.getString("operation_type")));
                
                event.setSku(rs.getString("sku"));
                event.setTimestamp(rs.getTimestamp("change_timestamp").toLocalDateTime());
                event.setChangeReason(rs.getString("change_reason"));
                
                // Parse JSON values
                String oldValuesJson = rs.getString("old_values");
                String newValuesJson = rs.getString("new_values");
                
                try {
                    if (oldValuesJson != null) {
                        event.setOldValues(objectMapper.readValue(oldValuesJson, Map.class));
                    }
                    if (newValuesJson != null) {
                        event.setNewValues(objectMapper.readValue(newValuesJson, Map.class));
                    }
                } catch (JsonProcessingException e) {
                    logger.warn("Failed to parse JSON values for event {}: {}", event.getEventId(), e.getMessage());
                }
                
                // Add metadata
                Map<String, Object> metadata = event.getMetadata();
                metadata.put("cdc_position", rs.getLong("cdc_position"));
                metadata.put("category", rs.getString("category"));
                metadata.put("brand", rs.getString("brand"));
                metadata.put("is_flash_sale", rs.getBoolean("is_flash_sale"));
                
                events.add(event);
            }
            
        } catch (SQLException e) {
            logger.error("Failed to capture inventory changes for warehouse {}: {}", warehouseId, e.getMessage(), e);
        }
        
        return events;
    }
    
    /**
     * Publish event to Kafka
     */
    private void publishToKafka(InventoryChangeEvent event) {
        try {
            String topic = determineKafkaTopic(event);
            String key = String.format("%s:%s", event.getWarehouseId(), event.getProductId());
            String message = event.toKafkaMessage();
            
            ProducerRecord<String, String> record = new ProducerRecord<>(topic, key, message);
            
            // Add headers for routing and processing
            record.headers()
                .add("warehouse_id", event.getWarehouseId().getBytes())
                .add("change_type", event.getChangeType().name().getBytes())
                .add("bbd_event", String.valueOf(event.isBbdEvent()).getBytes());
            
            kafkaProducer.send(record, (metadata, exception) -> {
                if (exception != null) {
                    logger.error("Failed to publish event {} to Kafka: {}", event.getEventId(), exception.getMessage());
                } else {
                    logger.debug("Event {} published to topic {} at offset {}", 
                               event.getEventId(), metadata.topic(), metadata.offset());
                }
            });
            
        } catch (Exception e) {
            logger.error("Error publishing event {} to Kafka: {}", event.getEventId(), e.getMessage(), e);
        }
    }
    
    /**
     * Determine Kafka topic based on event characteristics
     */
    private String determineKafkaTopic(InventoryChangeEvent event) {
        if (event.isBbdEvent()) {
            return "flipkart-inventory-bbd-changes";
        }
        
        switch (event.getChangeType()) {
            case OUT_OF_STOCK:
                return "flipkart-inventory-stock-alerts";
            case RESTOCK:
                return "flipkart-inventory-restock-notifications";
            case BULK_UPDATE:
                return "flipkart-inventory-bulk-operations";
            default:
                return "flipkart-inventory-changes";
        }
    }
    
    /**
     * Update inventory cache with event data
     */
    private void updateInventoryCache(InventoryChangeEvent event) {
        String cacheKey = String.format("%s:%s", event.getWarehouseId(), event.getProductId());
        
        if (event.getChangeType() == InventoryChangeEvent.ChangeType.DELETE) {
            inventoryCache.invalidate(cacheKey);
        } else if (event.getNewValues() != null) {
            Map<String, Object> cacheData = new HashMap<>(event.getNewValues());
            cacheData.put("warehouse_id", event.getWarehouseId());
            cacheData.put("product_id", event.getProductId());
            cacheData.put("last_updated", event.getTimestamp().toString());
            cacheData.putAll(event.getMetadata());
            
            inventoryCache.put(cacheKey, cacheData);
        }
    }
    
    /**
     * Monitor Big Billion Days status and adjust system accordingly
     */
    private void monitorBigBillionDays() {
        try {
            // Check if Big Billion Days should be active (simplified logic)
            LocalDateTime now = LocalDateTime.now();
            boolean shouldBeBBDActive = isBigBillionDaysPeriod(now);
            
            if (shouldBeBBDActive && !bigBillionDaysMode.get()) {
                activateBigBillionDaysMode();
            } else if (!shouldBeBBDActive && bigBillionDaysMode.get()) {
                deactivateBigBillionDaysMode();
            }
            
        } catch (Exception e) {
            logger.error("Error monitoring Big Billion Days status: {}", e.getMessage(), e);
        }
    }
    
    /**
     * Check if current time is within Big Billion Days period
     */
    private boolean isBigBillionDaysPeriod(LocalDateTime dateTime) {
        // Simplified logic - in production, this would check against actual BBD dates
        // For demo, assume BBD is active during certain hours
        int hour = dateTime.getHour();
        int dayOfYear = dateTime.getDayOfYear();
        
        // Simulate BBD period (e.g., October 15-20, peak hours 10 AM - 2 PM and 6 PM - 10 PM)
        boolean isBBDDate = (dayOfYear >= 288 && dayOfYear <= 293); // Approx Oct 15-20
        boolean isPeakHour = (hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 22);
        
        return isBBDDate && isPeakHour;
    }
    
    /**
     * Activate Big Billion Days mode
     */
    private void activateBigBillionDaysMode() {
        bigBillionDaysMode.set(true);
        
        // Enable BBD mode for all warehouses
        for (FlipkartWarehouse warehouse : warehouses.values()) {
            warehouse.enableBigBillionDays();
        }
        
        logger.info("🎯 Big Billion Days mode ACTIVATED - Enhanced processing enabled");
        inventoryLogger.info("BBD_MODE_ACTIVATED: timestamp={}, warehouses={}", 
                           LocalDateTime.now(), warehouses.size());
    }
    
    /**
     * Deactivate Big Billion Days mode
     */
    private void deactivateBigBillionDaysMode() {
        bigBillionDaysMode.set(false);
        
        // Disable BBD mode for all warehouses
        for (FlipkartWarehouse warehouse : warehouses.values()) {
            warehouse.disableBigBillionDays();
        }
        
        logger.info("✅ Big Billion Days mode DEACTIVATED - Normal processing resumed");
        inventoryLogger.info("BBD_MODE_DEACTIVATED: timestamp={}, warehouses={}", 
                           LocalDateTime.now(), warehouses.size());
    }
    
    /**
     * Collect and report system metrics
     */
    private void collectMetrics() {
        try {
            long currentTime = System.currentTimeMillis();
            long eventsInLastSecond = totalEventsProcessed.get() - eventsPerSecond.get();
            eventsPerSecond.set(totalEventsProcessed.get());
            
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("total_events_processed", totalEventsProcessed.get());
            metrics.put("events_per_second", eventsInLastSecond);
            metrics.put("cdc_active", cdcActive.get());
            metrics.put("bbd_mode", bigBillionDaysMode.get());
            metrics.put("cache_size", inventoryCache.size());
            metrics.put("active_warehouses", warehouses.values().stream()
                .mapToInt(w -> w.isActive() ? 1 : 0).sum());
            
            // Warehouse-specific metrics
            Map<String, Object> warehouseMetrics = new HashMap<>();
            for (FlipkartWarehouse warehouse : warehouses.values()) {
                warehouseMetrics.put(warehouse.getWarehouseId(), warehouse.getMetrics());
            }
            metrics.put("warehouses", warehouseMetrics);
            
            // CDC lag metrics
            Map<String, Object> lagMetrics = new HashMap<>();
            for (Map.Entry<String, LocalDateTime> entry : lastProcessedTime.entrySet()) {
                long lagSeconds = java.time.Duration.between(entry.getValue(), LocalDateTime.now()).getSeconds();
                lagMetrics.put(entry.getKey(), lagSeconds);
            }
            metrics.put("replication_lag_seconds", lagMetrics);
            
            inventoryLogger.info("CDC_METRICS: {}", objectMapper.writeValueAsString(metrics));
            
        } catch (Exception e) {
            logger.error("Error collecting metrics: {}", e.getMessage(), e);
        }
    }
    
    /**
     * Stop CDC processing
     */
    public void stopCDC() {
        if (cdcActive.compareAndSet(true, false)) {
            logger.info("Stopping Flipkart Inventory CDC System...");
            
            // Stop event processor
            eventProcessor.stopProcessing();
            
            // Stop scheduler tasks
            scheduler.shutdown();
            try {
                if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                    scheduler.shutdownNow();
                }
            } catch (InterruptedException e) {
                scheduler.shutdownNow();
                Thread.currentThread().interrupt();
            }
            
            // Stop CDC executor
            cdcExecutor.shutdown();
            try {
                if (!cdcExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                    cdcExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                cdcExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
            
            // Close Kafka producer
            kafkaProducer.close();
            
            // Close database connections
            for (DataSource ds : warehouseDataSources.values()) {
                if (ds instanceof HikariDataSource) {
                    ((HikariDataSource) ds).close();
                }
            }
            
            // Shutdown cache
            inventoryCache.shutdown();
            
            logger.info("Flipkart Inventory CDC System stopped successfully");
        }
    }
    
    /**
     * Get current system status
     */
    public Map<String, Object> getSystemStatus() {
        Map<String, Object> status = new HashMap<>();
        
        status.put("cdc_active", cdcActive.get());
        status.put("bbd_mode_active", bigBillionDaysMode.get());
        status.put("total_events_processed", totalEventsProcessed.get());
        status.put("current_poll_interval_ms", getCurrentPollInterval());
        status.put("cache_size", inventoryCache.size());
        
        // Warehouse status
        Map<String, String> warehouseStatus = new HashMap<>();
        for (FlipkartWarehouse warehouse : warehouses.values()) {
            warehouseStatus.put(warehouse.getWarehouseId(), 
                              warehouse.isActive() ? "ACTIVE" : "INACTIVE");
        }
        status.put("warehouse_status", warehouseStatus);
        
        return status;
    }
    
    /**
     * Demo main method
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🛒 Flipkart Inventory CDC System");
        System.out.println("Episode 41: Real-time E-commerce Inventory Management");
        System.out.println("=" + "=".repeat(65));
        
        FlipkartInventoryCDC cdcSystem = new FlipkartInventoryCDC();
        
        try {
            // Start CDC system
            cdcSystem.startCDC();
            
            System.out.println("✅ Flipkart Inventory CDC System started");
            System.out.println("📦 Monitoring " + cdcSystem.warehouses.size() + " warehouses");
            System.out.println("🔄 Poll Interval: " + cdcSystem.getCurrentPollInterval() + "ms");
            
            // Run normal processing for 30 seconds
            System.out.println("\n🔄 Running normal processing for 30 seconds...");
            Thread.sleep(30000);
            
            // Simulate Big Billion Days activation
            System.out.println("\n🎯 Activating Big Billion Days mode...");
            cdcSystem.activateBigBillionDaysMode();
            
            System.out.println("📈 Enhanced processing active:");
            System.out.println("  • Batch Size: " + BBD_BATCH_SIZE);
            System.out.println("  • Poll Interval: " + BBD_POLL_INTERVAL_MS + "ms");
            System.out.println("  • Scale Factor: " + BBD_SCALE_FACTOR + "x");
            
            // Run BBD processing for 45 seconds
            System.out.println("\n🔄 Running Big Billion Days processing for 45 seconds...");
            Thread.sleep(45000);
            
            // Deactivate BBD mode
            System.out.println("\n✅ Deactivating Big Billion Days mode...");
            cdcSystem.deactivateBigBillionDaysMode();
            
            // Run normal processing for 15 more seconds
            Thread.sleep(15000);
            
            // Show final status
            Map<String, Object> status = cdcSystem.getSystemStatus();
            System.out.println("\n📊 Final System Status:");
            System.out.println("  Total Events: " + status.get("total_events_processed"));
            System.out.println("  Cache Size: " + status.get("cache_size"));
            System.out.println("  CDC Active: " + status.get("cdc_active"));
            System.out.println("  BBD Mode: " + status.get("bbd_mode_active"));
            
            System.out.println("\n✅ Demo completed successfully");
            
        } catch (Exception e) {
            System.err.println("❌ Error during demo: " + e.getMessage());
            e.printStackTrace();
        } finally {
            cdcSystem.stopCDC();
            System.out.println("🔚 Flipkart Inventory CDC System stopped");
        }
    }
}

/**
 * Key Learning Points from Flipkart Inventory CDC:
 * 
 * 1. **E-commerce Scale Challenges**:
 *    - Multiple warehouses across India with different capacities
 *    - Big Billion Days requires 5x normal processing capability
 *    - Real-time inventory sync to prevent overselling
 *    - Flash sales create extreme traffic spikes
 * 
 * 2. **CDC Implementation Patterns**:
 *    - Polling-based CDC for inventory tables
 *    - Batch processing for efficiency
 *    - Kafka for event streaming to downstream systems
 *    - Cache integration for quick lookups
 * 
 * 3. **Business Logic Integration**:
 *    - Low stock alerts and restock notifications
 *    - Flash sale special handling
 *    - Category-based warehouse routing
 *    - Dynamic scaling based on business events
 * 
 * 4. **Production Considerations**:
 *    - Connection pooling for multiple warehouses
 *    - Comprehensive error handling and retries
 *    - Monitoring and metrics collection
 *    - Cache management with TTL
 *    - Graceful system shutdown
 * 
 * This implementation demonstrates how to build scalable CDC systems
 * for e-commerce platforms that can handle Indian market scale and
 * seasonal traffic variations like Big Billion Days.
 */