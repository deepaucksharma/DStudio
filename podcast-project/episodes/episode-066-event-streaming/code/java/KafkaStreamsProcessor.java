/*
 * Event Streaming Episode - Kafka Streams Real-time Processing
 * Production-ready stream processing for Indian e-commerce analytics
 * 
 * Author: Hindi Tech Podcast Series
 */

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.streams.processor.WallclockTimestampExtractor;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.time.Duration;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Flipkart जैसे e-commerce platform के लिए real-time analytics
 * Kafka Streams के साथ order processing, user behavior, और inventory tracking
 */
public class FlipkartAnalyticsStreamsProcessor {
    
    private static final Logger logger = Logger.getLogger(FlipkartAnalyticsStreamsProcessor.class.getName());
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Kafka topics
    private static final String ORDER_EVENTS_TOPIC = "flipkart-order-events";
    private static final String USER_ACTIVITY_TOPIC = "flipkart-user-activity";
    private static final String INVENTORY_EVENTS_TOPIC = "flipkart-inventory-events";
    private static final String REAL_TIME_ANALYTICS_TOPIC = "flipkart-analytics-output";
    
    public static void main(String[] args) {
        System.out.println("🛍️ Starting Flipkart Real-time Analytics with Kafka Streams");
        System.out.println("📊 Processing orders, user activity, and inventory events");
        System.out.println("-".repeat(60));
        
        FlipkartAnalyticsStreamsProcessor processor = new FlipkartAnalyticsStreamsProcessor();
        processor.startStreaming();
    }
    
    public void startStreaming() {
        // Kafka Streams configuration - Production ready settings
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "flipkart-analytics-app");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        
        // Serialization configuration
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        
        // Performance और reliability के लिए settings
        props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 3); // 3 threads for parallel processing
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000); // Commit every 1 second
        props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024); // 10MB cache
        
        // Error handling और recovery
        props.put(StreamsConfig.DEFAULT_DESERIALIZATION_EXCEPTION_HANDLER_CLASS_CONFIG,
                 "org.apache.kafka.streams.errors.LogAndContinueExceptionHandler");
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
        
        // Consumer configuration for reliability
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 30000);
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
        
        try {
            // Build stream topology
            StreamsBuilder builder = new StreamsBuilder();
            buildAnalyticsTopology(builder);
            
            // Create और start Kafka Streams
            KafkaStreams streams = new KafkaStreams(builder.build(), props);
            
            // Graceful shutdown के लिए shutdown hook
            CountDownLatch latch = new CountDownLatch(1);
            Runtime.getRuntime().addShutdownHook(new Thread("streams-shutdown-hook") {
                @Override
                public void run() {
                    logger.info("🛑 Shutting down Flipkart Analytics Streams...");
                    streams.close(Duration.ofSeconds(10));
                    latch.countDown();
                }
            });
            
            // Exception handler
            streams.setUncaughtExceptionHandler((Thread thread, Throwable exception) -> {
                logger.log(Level.SEVERE, "❌ Uncaught exception in stream thread: " + thread.getName(), exception);
                return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.SHUTDOWN_APPLICATION;
            });
            
            // State change listener
            streams.setStateListener((newState, oldState) -> {
                logger.info(String.format("🔄 Stream state changed: %s -> %s", oldState, newState));
            });
            
            logger.info("🚀 Starting Kafka Streams...");
            streams.start();
            
            // आगे demonstration के लिए sample data भेजते हैं
            startSampleDataProducer();
            
            // Wait for shutdown
            latch.await();
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "❌ Error in Kafka Streams application", e);
        }
    }
    
    private void buildAnalyticsTopology(StreamsBuilder builder) {
        logger.info("🏗️ Building stream processing topology...");
        
        // Input streams define करते हैं
        KStream<String, String> orderEvents = builder.stream(ORDER_EVENTS_TOPIC);
        KStream<String, String> userActivity = builder.stream(USER_ACTIVITY_TOPIC);
        KStream<String, String> inventoryEvents = builder.stream(INVENTORY_EVENTS_TOPIC);
        
        // 1. Order Analytics - Real-time order processing metrics
        processOrderAnalytics(orderEvents);
        
        // 2. User Behavior Analytics - User engagement patterns
        processUserBehaviorAnalytics(userActivity);
        
        // 3. Inventory Analytics - Stock level monitoring
        processInventoryAnalytics(inventoryEvents);
        
        // 4. Cross-stream analytics - Order और user activity correlation
        processCrossStreamAnalytics(orderEvents, userActivity);
        
        // 5. Fraud detection - Suspicious activity detection
        processFraudDetection(orderEvents, userActivity);
        
        logger.info("✅ Stream topology built successfully");
    }
    
    private void processOrderAnalytics(KStream<String, String> orderEvents) {
        logger.info("📊 Setting up order analytics pipeline...");
        
        // Order events को filter और transform करते हैं
        KStream<String, OrderMetrics> orderMetrics = orderEvents
            .filter((key, value) -> {
                // केवल valid order events process करें
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return node.has("order_id") && node.has("total_amount");
                } catch (Exception e) {
                    logger.warning("⚠️ Invalid order event format: " + value);
                    return false;
                }
            })
            .mapValues(value -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return new OrderMetrics(
                        node.get("order_id").asText(),
                        node.get("user_id").asText(),
                        node.get("total_amount").asDouble(),
                        node.get("item_count").asInt(),
                        node.get("category").asText(),
                        System.currentTimeMillis()
                    );
                } catch (Exception e) {
                    logger.warning("⚠️ Error parsing order event: " + e.getMessage());
                    return null;
                }
            })
            .filter((key, value) -> value != null);
        
        // Time window based aggregations
        // 5-minute windows के लिए order volume और revenue tracking
        TimeWindows orderWindow = TimeWindows.of(Duration.ofMinutes(5)).advanceBy(Duration.ofMinutes(1));
        
        KTable<Windowed<String>, OrderAggregates> orderAggregates = orderMetrics
            .groupBy((key, orderMetric) -> orderMetric.category) // Category wise group करें
            .windowedBy(orderWindow)
            .aggregate(
                OrderAggregates::new, // Initial value
                (key, orderMetric, aggregate) -> {
                    // Order metrics को aggregate करें
                    aggregate.orderCount++;
                    aggregate.totalRevenue += orderMetric.totalAmount;
                    aggregate.totalItems += orderMetric.itemCount;
                    aggregate.avgOrderValue = aggregate.totalRevenue / aggregate.orderCount;
                    aggregate.lastUpdated = System.currentTimeMillis();
                    return aggregate;
                },
                Materialized.with(Serdes.String(), createOrderAggregatesSerde())
            );
        
        // Aggregated results को output topic में send करें
        orderAggregates.toStream()
            .map((windowedKey, aggregate) -> {
                String outputKey = String.format("order_analytics_%s_%d_%d", 
                    windowedKey.key(), 
                    windowedKey.window().start(), 
                    windowedKey.window().end());
                
                String outputValue = String.format(
                    "{\"category\":\"%s\",\"window_start\":%d,\"window_end\":%d," +
                    "\"order_count\":%d,\"total_revenue\":%.2f,\"avg_order_value\":%.2f," +
                    "\"total_items\":%d,\"timestamp\":%d}",
                    windowedKey.key(), windowedKey.window().start(), windowedKey.window().end(),
                    aggregate.orderCount, aggregate.totalRevenue, aggregate.avgOrderValue,
                    aggregate.totalItems, aggregate.lastUpdated
                );
                
                return KeyValue.pair(outputKey, outputValue);
            })
            .to(REAL_TIME_ANALYTICS_TOPIC);
        
        logger.info("✅ Order analytics pipeline configured");
    }
    
    private void processUserBehaviorAnalytics(KStream<String, String> userActivity) {
        logger.info("👤 Setting up user behavior analytics pipeline...");
        
        // User activity को sessionization करते हैं
        TimeWindows sessionWindow = TimeWindows.of(Duration.ofMinutes(30));
        
        KTable<Windowed<String>, UserSessionMetrics> userSessions = userActivity
            .filter((key, value) -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return node.has("user_id") && node.has("activity_type");
                } catch (Exception e) {
                    return false;
                }
            })
            .groupByKey()
            .windowedBy(sessionWindow)
            .aggregate(
                UserSessionMetrics::new,
                (key, value, session) -> {
                    try {
                        JsonNode node = objectMapper.readTree(value);
                        String activityType = node.get("activity_type").asText();
                        
                        session.userId = node.get("user_id").asText();
                        session.activityCount++;
                        session.lastActivity = System.currentTimeMillis();
                        
                        // Activity type के based पर different metrics
                        switch (activityType) {
                            case "VIEW_PRODUCT":
                                session.productViews++;
                                break;
                            case "ADD_TO_CART":
                                session.cartAdditions++;
                                break;
                            case "SEARCH":
                                session.searchCount++;
                                break;
                            case "PURCHASE":
                                session.purchases++;
                                break;
                        }
                        
                        return session;
                    } catch (Exception e) {
                        return session;
                    }
                },
                Materialized.with(Serdes.String(), createUserSessionSerde())
            );
        
        // User engagement score calculate करें
        userSessions.toStream()
            .map((windowedKey, session) -> {
                double engagementScore = calculateEngagementScore(session);
                
                String outputKey = String.format("user_behavior_%s_%d_%d",
                    windowedKey.key(),
                    windowedKey.window().start(),
                    windowedKey.window().end());
                
                String outputValue = String.format(
                    "{\"user_id\":\"%s\",\"window_start\":%d,\"window_end\":%d," +
                    "\"activity_count\":%d,\"product_views\":%d,\"cart_additions\":%d," +
                    "\"search_count\":%d,\"purchases\":%d,\"engagement_score\":%.2f," +
                    "\"session_duration\":%d,\"timestamp\":%d}",
                    session.userId, windowedKey.window().start(), windowedKey.window().end(),
                    session.activityCount, session.productViews, session.cartAdditions,
                    session.searchCount, session.purchases, engagementScore,
                    (session.lastActivity - windowedKey.window().start()), session.lastActivity
                );
                
                return KeyValue.pair(outputKey, outputValue);
            })
            .to(REAL_TIME_ANALYTICS_TOPIC);
        
        logger.info("✅ User behavior analytics pipeline configured");
    }
    
    private void processInventoryAnalytics(KStream<String, String> inventoryEvents) {
        logger.info("📦 Setting up inventory analytics pipeline...");
        
        // Inventory changes को track करते हैं
        KStream<String, InventoryMetrics> inventoryMetrics = inventoryEvents
            .mapValues(value -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return new InventoryMetrics(
                        node.get("product_id").asText(),
                        node.get("category").asText(),
                        node.get("brand").asText(),
                        node.get("old_quantity").asInt(),
                        node.get("new_quantity").asInt(),
                        node.get("change_reason").asText(),
                        System.currentTimeMillis()
                    );
                } catch (Exception e) {
                    return null;
                }
            })
            .filter((key, value) -> value != null);
        
        // Low stock alerts generate करें
        inventoryMetrics
            .filter((key, metrics) -> metrics.newQuantity < 10) // Low stock threshold
            .map((key, metrics) -> {
                String alertKey = "low_stock_alert_" + metrics.productId;
                String alertValue = String.format(
                    "{\"alert_type\":\"LOW_STOCK\",\"product_id\":\"%s\"," +
                    "\"category\":\"%s\",\"brand\":\"%s\",\"current_quantity\":%d," +
                    "\"threshold\":10,\"severity\":\"HIGH\",\"timestamp\":%d}",
                    metrics.productId, metrics.category, metrics.brand,
                    metrics.newQuantity, metrics.timestamp
                );
                return KeyValue.pair(alertKey, alertValue);
            })
            .to(REAL_TIME_ANALYTICS_TOPIC);
        
        // Category-wise inventory trends
        TimeWindows inventoryWindow = TimeWindows.of(Duration.ofMinutes(10));
        
        inventoryMetrics
            .groupBy((key, metrics) -> metrics.category)
            .windowedBy(inventoryWindow)
            .aggregate(
                InventoryAggregates::new,
                (key, metrics, aggregate) -> {
                    aggregate.totalProducts++;
                    aggregate.totalStockChange += (metrics.newQuantity - metrics.oldQuantity);
                    
                    if (metrics.newQuantity < 10) {
                        aggregate.lowStockProducts++;
                    }
                    
                    aggregate.lastUpdated = System.currentTimeMillis();
                    return aggregate;
                },
                Materialized.with(Serdes.String(), createInventoryAggregatesSerde())
            )
            .toStream()
            .map((windowedKey, aggregate) -> {
                String outputKey = String.format("inventory_analytics_%s_%d_%d",
                    windowedKey.key(),
                    windowedKey.window().start(),
                    windowedKey.window().end());
                
                String outputValue = String.format(
                    "{\"category\":\"%s\",\"window_start\":%d,\"window_end\":%d," +
                    "\"total_products\":%d,\"total_stock_change\":%d," +
                    "\"low_stock_products\":%d,\"stock_health\":%.2f,\"timestamp\":%d}",
                    windowedKey.key(), windowedKey.window().start(), windowedKey.window().end(),
                    aggregate.totalProducts, aggregate.totalStockChange, aggregate.lowStockProducts,
                    (aggregate.totalProducts > 0 ? (double)(aggregate.totalProducts - aggregate.lowStockProducts) / aggregate.totalProducts : 0.0),
                    aggregate.lastUpdated
                );
                
                return KeyValue.pair(outputKey, outputValue);
            })
            .to(REAL_TIME_ANALYTICS_TOPIC);
        
        logger.info("✅ Inventory analytics pipeline configured");
    }
    
    private void processCrossStreamAnalytics(KStream<String, String> orderEvents, 
                                           KStream<String, String> userActivity) {
        logger.info("🔄 Setting up cross-stream analytics pipeline...");
        
        // User activity और orders को join करते हैं conversion analysis के लिए
        TimeWindows joinWindow = TimeWindows.of(Duration.ofMinutes(60));
        
        KStream<String, String> userActivityByUser = userActivity
            .selectKey((key, value) -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return node.get("user_id").asText();
                } catch (Exception e) {
                    return key;
                }
            });
        
        KStream<String, String> ordersByUser = orderEvents
            .selectKey((key, value) -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    return node.get("user_id").asText();
                } catch (Exception e) {
                    return key;
                }
            });
        
        // Join user activity with orders for conversion tracking
        ordersByUser.join(
            userActivityByUser,
            (orderValue, activityValue) -> {
                try {
                    JsonNode orderNode = objectMapper.readTree(orderValue);
                    JsonNode activityNode = objectMapper.readTree(activityValue);
                    
                    return String.format(
                        "{\"conversion_event\":true,\"user_id\":\"%s\"," +
                        "\"order_id\":\"%s\",\"order_amount\":%.2f," +
                        "\"activity_type\":\"%s\",\"conversion_timestamp\":%d}",
                        orderNode.get("user_id").asText(),
                        orderNode.get("order_id").asText(),
                        orderNode.get("total_amount").asDouble(),
                        activityNode.get("activity_type").asText(),
                        System.currentTimeMillis()
                    );
                } catch (Exception e) {
                    return null;
                }
            },
            JoinWindows.of(Duration.ofMinutes(30))
        )
        .filter((key, value) -> value != null)
        .to(REAL_TIME_ANALYTICS_TOPIC);
        
        logger.info("✅ Cross-stream analytics pipeline configured");
    }
    
    private void processFraudDetection(KStream<String, String> orderEvents, 
                                     KStream<String, String> userActivity) {
        logger.info("🛡️ Setting up fraud detection pipeline...");
        
        // Suspicious order patterns detect करते हैं
        TimeWindows fraudWindow = TimeWindows.of(Duration.ofMinutes(5));
        
        // Multiple high-value orders from same user in short time
        orderEvents
            .mapValues(value -> {
                try {
                    JsonNode node = objectMapper.readTree(value);
                    if (node.get("total_amount").asDouble() > 50000) { // High value orders
                        return new FraudMetrics(
                            node.get("user_id").asText(),
                            node.get("order_id").asText(),
                            node.get("total_amount").asDouble(),
                            System.currentTimeMillis()
                        );
                    }
                } catch (Exception e) {
                    // Ignore parsing errors
                }
                return null;
            })
            .filter((key, value) -> value != null)
            .groupBy((key, fraudMetric) -> fraudMetric.userId)
            .windowedBy(fraudWindow)
            .aggregate(
                FraudAggregates::new,
                (key, fraudMetric, aggregate) -> {
                    aggregate.orderCount++;
                    aggregate.totalAmount += fraudMetric.amount;
                    aggregate.orderIds.add(fraudMetric.orderId);
                    aggregate.lastOrderTime = fraudMetric.timestamp;
                    return aggregate;
                },
                Materialized.with(Serdes.String(), createFraudAggregatesSerde())
            )
            .toStream()
            .filter((windowedKey, aggregate) -> 
                aggregate.orderCount >= 3 || aggregate.totalAmount > 100000) // Fraud thresholds
            .map((windowedKey, aggregate) -> {
                String alertKey = "fraud_alert_" + windowedKey.key() + "_" + windowedKey.window().start();
                String alertValue = String.format(
                    "{\"alert_type\":\"POTENTIAL_FRAUD\",\"user_id\":\"%s\"," +
                    "\"window_start\":%d,\"window_end\":%d,\"order_count\":%d," +
                    "\"total_amount\":%.2f,\"severity\":\"CRITICAL\"," +
                    "\"detection_timestamp\":%d,\"order_ids\":%s}",
                    windowedKey.key(), windowedKey.window().start(), windowedKey.window().end(),
                    aggregate.orderCount, aggregate.totalAmount, System.currentTimeMillis(),
                    aggregate.orderIds.toString()
                );
                return KeyValue.pair(alertKey, alertValue);
            })
            .to(REAL_TIME_ANALYTICS_TOPIC);
        
        logger.info("✅ Fraud detection pipeline configured");
    }
    
    private double calculateEngagementScore(UserSessionMetrics session) {
        // Simple engagement score calculation
        // Real implementation में more sophisticated algorithm होगा
        double score = 0.0;
        score += session.productViews * 1.0;
        score += session.cartAdditions * 3.0;
        score += session.searchCount * 2.0;
        score += session.purchases * 10.0;
        
        // Session duration bonus
        long sessionDuration = session.lastActivity - session.activityCount; // Simplified
        if (sessionDuration > 300000) { // 5 minutes+
            score *= 1.2;
        }
        
        return Math.min(score, 100.0); // Cap at 100
    }
    
    private void startSampleDataProducer() {
        // Sample data generation के लिए background thread
        // Real environment में separate producer होगा
        new Thread(() -> {
            logger.info("🎲 Starting sample data generation...");
            // Sample data generation logic यहाँ होगी
            // Production में यह अलग service होगी
        }).start();
    }
    
    // Helper methods for Serde creation
    private static Serde<OrderAggregates> createOrderAggregatesSerde() {
        // Production में proper JSON serde use करेंगे
        return Serdes.serdeFrom(new JsonSerializer<>(), new JsonDeserializer<>(OrderAggregates.class));
    }
    
    private static Serde<UserSessionMetrics> createUserSessionSerde() {
        return Serdes.serdeFrom(new JsonSerializer<>(), new JsonDeserializer<>(UserSessionMetrics.class));
    }
    
    private static Serde<InventoryAggregates> createInventoryAggregatesSerde() {
        return Serdes.serdeFrom(new JsonSerializer<>(), new JsonDeserializer<>(InventoryAggregates.class));
    }
    
    private static Serde<FraudAggregates> createFraudAggregatesSerde() {
        return Serdes.serdeFrom(new JsonSerializer<>(), new JsonDeserializer<>(FraudAggregates.class));
    }
    
    // Data model classes
    static class OrderMetrics {
        String orderId;
        String userId;
        double totalAmount;
        int itemCount;
        String category;
        long timestamp;
        
        OrderMetrics(String orderId, String userId, double totalAmount, 
                    int itemCount, String category, long timestamp) {
            this.orderId = orderId;
            this.userId = userId;
            this.totalAmount = totalAmount;
            this.itemCount = itemCount;
            this.category = category;
            this.timestamp = timestamp;
        }
    }
    
    static class OrderAggregates {
        int orderCount = 0;
        double totalRevenue = 0.0;
        double avgOrderValue = 0.0;
        int totalItems = 0;
        long lastUpdated = 0;
    }
    
    static class UserSessionMetrics {
        String userId = "";
        int activityCount = 0;
        int productViews = 0;
        int cartAdditions = 0;
        int searchCount = 0;
        int purchases = 0;
        long lastActivity = 0;
    }
    
    static class InventoryMetrics {
        String productId;
        String category;
        String brand;
        int oldQuantity;
        int newQuantity;
        String changeReason;
        long timestamp;
        
        InventoryMetrics(String productId, String category, String brand,
                        int oldQuantity, int newQuantity, String changeReason, long timestamp) {
            this.productId = productId;
            this.category = category;
            this.brand = brand;
            this.oldQuantity = oldQuantity;
            this.newQuantity = newQuantity;
            this.changeReason = changeReason;
            this.timestamp = timestamp;
        }
    }
    
    static class InventoryAggregates {
        int totalProducts = 0;
        int totalStockChange = 0;
        int lowStockProducts = 0;
        long lastUpdated = 0;
    }
    
    static class FraudMetrics {
        String userId;
        String orderId;
        double amount;
        long timestamp;
        
        FraudMetrics(String userId, String orderId, double amount, long timestamp) {
            this.userId = userId;
            this.orderId = orderId;
            this.amount = amount;
            this.timestamp = timestamp;
        }
    }
    
    static class FraudAggregates {
        int orderCount = 0;
        double totalAmount = 0.0;
        Set<String> orderIds = new HashSet<>();
        long lastOrderTime = 0;
    }
    
    // Placeholder classes for JSON serialization
    static class JsonSerializer<T> implements org.apache.kafka.common.serialization.Serializer<T> {
        @Override
        public byte[] serialize(String topic, T data) {
            try {
                return objectMapper.writeValueAsBytes(data);
            } catch (Exception e) {
                throw new RuntimeException("Error serializing object", e);
            }
        }
    }
    
    static class JsonDeserializer<T> implements org.apache.kafka.common.serialization.Deserializer<T> {
        private final Class<T> type;
        
        JsonDeserializer(Class<T> type) {
            this.type = type;
        }
        
        @Override
        public T deserialize(String topic, byte[] data) {
            try {
                return objectMapper.readValue(data, type);
            } catch (Exception e) {
                throw new RuntimeException("Error deserializing object", e);
            }
        }
    }
}