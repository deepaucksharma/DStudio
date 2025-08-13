/*
 * Apache Flink Real-time Stream Processing
 * Episode 43: Real-time Analytics at Scale
 * 
 * Production-grade Flink application for real-time stream processing
 * Use Case: Flipkart BBD में real-time inventory tracking
 */

import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.api.java.tuple.Tuple4;
import org.apache.flink.streaming.api.TimeCharacteristic;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaProducer;
import org.apache.flink.util.Collector;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.JsonNode;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Properties;

/**
 * Flipkart BBD Real-time Inventory Analytics
 * 
 * यह application real-time में inventory changes को track करता है
 * और out-of-stock alerts generate करता है
 */
public class FlipkartInventoryAnalytics {
    
    /**
     * Inventory Event POJO
     * Inventory में होने वाले changes को represent करता है
     */
    public static class InventoryEvent {
        public String productId;
        public String warehouseId;
        public String eventType; // sale, restock, return, damage
        public int quantityChange;
        public long timestamp;
        public double price;
        public String category;
        
        public InventoryEvent() {}
        
        public InventoryEvent(String productId, String warehouseId, String eventType, 
                            int quantityChange, long timestamp, double price, String category) {
            this.productId = productId;
            this.warehouseId = warehouseId;
            this.eventType = eventType;
            this.quantityChange = quantityChange;
            this.timestamp = timestamp;
            this.price = price;
            this.category = category;
        }
        
        @Override
        public String toString() {
            return String.format("InventoryEvent{productId='%s', warehouseId='%s', eventType='%s', " +
                               "quantityChange=%d, timestamp=%d, price=%.2f, category='%s'}",
                               productId, warehouseId, eventType, quantityChange, timestamp, price, category);
        }
    }
    
    /**
     * Inventory Status
     * Current inventory status के साथ alerts
     */
    public static class InventoryStatus {
        public String productId;
        public String warehouseId;
        public int currentStock;
        public int stockChange;
        public double revenue;
        public String alertLevel; // OK, LOW, CRITICAL, OUT_OF_STOCK
        public long lastUpdated;
        
        public InventoryStatus() {}
        
        public InventoryStatus(String productId, String warehouseId, int currentStock, 
                             int stockChange, double revenue, String alertLevel, long lastUpdated) {
            this.productId = productId;
            this.warehouseId = warehouseId;
            this.currentStock = currentStock;
            this.stockChange = stockChange;
            this.revenue = revenue;
            this.alertLevel = alertLevel;
            this.lastUpdated = lastUpdated;
        }
        
        @Override
        public String toString() {
            return String.format("InventoryStatus{productId='%s', warehouseId='%s', currentStock=%d, " +
                               "stockChange=%d, revenue=%.2f, alertLevel='%s', lastUpdated=%d}",
                               productId, warehouseId, currentStock, stockChange, revenue, alertLevel, lastUpdated);
        }
    }
    
    /**
     * JSON to InventoryEvent Mapper
     * Kafka से आने वाले JSON messages को parse करता है
     */
    public static class JsonToInventoryEventMapper implements MapFunction<String, InventoryEvent> {
        private final ObjectMapper objectMapper = new ObjectMapper();
        
        @Override
        public InventoryEvent map(String jsonString) throws Exception {
            try {
                JsonNode jsonNode = objectMapper.readTree(jsonString);
                
                return new InventoryEvent(
                    jsonNode.get("product_id").asText(),
                    jsonNode.get("warehouse_id").asText(),
                    jsonNode.get("event_type").asText(),
                    jsonNode.get("quantity_change").asInt(),
                    jsonNode.get("timestamp").asLong(),
                    jsonNode.get("price").asDouble(),
                    jsonNode.get("category").asText()
                );
            } catch (Exception e) {
                System.err.println("Error parsing JSON: " + jsonString + " - " + e.getMessage());
                // Return a default event in case of parsing error
                return new InventoryEvent("unknown", "unknown", "error", 0, 
                                        System.currentTimeMillis(), 0.0, "unknown");
            }
        }
    }
    
    /**
     * Inventory Aggregation Function
     * Inventory changes को aggregate करके current status calculate करता है
     */
    public static class InventoryAggregator extends ProcessWindowFunction<InventoryEvent, InventoryStatus, String, TimeWindow> {
        
        @Override
        public void process(String key, Context context, 
                          Iterable<InventoryEvent> events, 
                          Collector<InventoryStatus> out) throws Exception {
            
            // Parse key (productId + warehouseId)
            String[] keyParts = key.split(":", 2);
            String productId = keyParts[0];
            String warehouseId = keyParts.length > 1 ? keyParts[1] : "unknown";
            
            int totalStockChange = 0;
            double totalRevenue = 0.0;
            long latestTimestamp = 0;
            int eventCount = 0;
            
            // Aggregate all events in the window
            for (InventoryEvent event : events) {
                totalStockChange += event.quantityChange;
                
                // Calculate revenue for sales
                if ("sale".equals(event.eventType)) {
                    totalRevenue += Math.abs(event.quantityChange) * event.price;
                }
                
                latestTimestamp = Math.max(latestTimestamp, event.timestamp);
                eventCount++;
            }
            
            // Simulate current stock calculation
            // Production में यह database से current stock fetch करेगा
            int baseStock = Math.abs(productId.hashCode()) % 1000; // Simulated base stock
            int currentStock = Math.max(0, baseStock + totalStockChange);
            
            // Determine alert level
            String alertLevel = determineAlertLevel(currentStock, eventCount);
            
            InventoryStatus status = new InventoryStatus(
                productId, warehouseId, currentStock, totalStockChange, 
                totalRevenue, alertLevel, latestTimestamp
            );
            
            out.collect(status);
            
            // Log high-priority alerts
            if ("CRITICAL".equals(alertLevel) || "OUT_OF_STOCK".equals(alertLevel)) {
                System.out.println("🚨 INVENTORY ALERT: " + status);
            }
        }
        
        private String determineAlertLevel(int currentStock, int eventCount) {
            if (currentStock == 0) {
                return "OUT_OF_STOCK";
            } else if (currentStock < 10) {
                return "CRITICAL";
            } else if (currentStock < 50) {
                return "LOW";
            } else {
                return "OK";
            }
        }
    }
    
    /**
     * Revenue Calculator
     * Real-time revenue calculation करता है
     */
    public static class RevenueCalculator implements MapFunction<InventoryEvent, Tuple3<String, Double, Long>> {
        
        @Override
        public Tuple3<String, Double, Long> map(InventoryEvent event) throws Exception {
            double revenue = 0.0;
            
            // केवल sales से revenue calculate करें
            if ("sale".equals(event.eventType)) {
                revenue = Math.abs(event.quantityChange) * event.price;
            }
            
            return new Tuple3<>(event.category, revenue, event.timestamp);
        }
    }
    
    /**
     * Top Selling Products Processor
     * Window के अंदर top selling products find करता है
     */
    public static class TopSellingProcessor extends ProcessWindowFunction<InventoryEvent, String, String, TimeWindow> {
        
        @Override
        public void process(String category, Context context,
                          Iterable<InventoryEvent> events,
                          Collector<String> out) throws Exception {
            
            // Count sales by product
            java.util.Map<String, Integer> productSales = new java.util.HashMap<>();
            java.util.Map<String, Double> productRevenue = new java.util.HashMap<>();
            
            for (InventoryEvent event : events) {
                if ("sale".equals(event.eventType)) {
                    String productId = event.productId;
                    int quantity = Math.abs(event.quantityChange);
                    double revenue = quantity * event.price;
                    
                    productSales.put(productId, productSales.getOrDefault(productId, 0) + quantity);
                    productRevenue.put(productId, productRevenue.getOrDefault(productId, 0.0) + revenue);
                }
            }
            
            // Find top selling product
            String topProduct = null;
            int maxSales = 0;
            
            for (java.util.Map.Entry<String, Integer> entry : productSales.entrySet()) {
                if (entry.getValue() > maxSales) {
                    maxSales = entry.getValue();
                    topProduct = entry.getKey();
                }
            }
            
            if (topProduct != null) {
                String result = String.format("{\"category\": \"%s\", \"top_product\": \"%s\", " +
                                            "\"units_sold\": %d, \"revenue\": %.2f, \"window_end\": %d}",
                                            category, topProduct, maxSales, 
                                            productRevenue.get(topProduct), context.window().getEnd());
                out.collect(result);
            }
        }
    }
    
    public static void main(String[] args) throws Exception {
        // Flink execution environment setup
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Set event time processing
        env.setStreamTimeCharacteristic(TimeCharacteristic.EventTime);
        
        // Set parallelism for high throughput
        env.setParallelism(4);
        
        // Enable checkpointing for fault tolerance
        env.enableCheckpointing(5000); // Checkpoint every 5 seconds
        
        // Kafka consumer configuration
        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", "localhost:9092");
        kafkaProps.setProperty("group.id", "flink-inventory-analytics");
        kafkaProps.setProperty("auto.offset.reset", "latest");
        
        // Create Kafka consumer
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
            "flipkart_inventory_events",
            new SimpleStringSchema(),
            kafkaProps
        );
        
        // Kafka producer configuration for output
        Properties producerProps = new Properties();
        producerProps.setProperty("bootstrap.servers", "localhost:9092");
        
        FlinkKafkaProducer<String> kafkaProducer = new FlinkKafkaProducer<>(
            "flipkart_inventory_alerts",
            new SimpleStringSchema(),
            producerProps
        );
        
        // Create input stream
        DataStream<String> inputStream = env.addSource(kafkaConsumer)
            .name("Inventory Events Source");
        
        // Parse JSON to InventoryEvent objects
        DataStream<InventoryEvent> eventStream = inputStream
            .map(new JsonToInventoryEventMapper())
            .name("JSON Parser");
        
        // Stream 1: Real-time inventory status tracking
        DataStream<InventoryStatus> inventoryStatusStream = eventStream
            .keyBy(event -> event.productId + ":" + event.warehouseId)
            .timeWindow(Time.minutes(1)) // 1-minute windows
            .process(new InventoryAggregator())
            .name("Inventory Aggregation");
        
        // Filter and alert for critical inventory levels
        DataStream<String> criticalAlerts = inventoryStatusStream
            .filter(status -> "CRITICAL".equals(status.alertLevel) || "OUT_OF_STOCK".equals(status.alertLevel))
            .map(status -> String.format("{\"alert_type\": \"inventory_critical\", " +
                                       "\"product_id\": \"%s\", \"warehouse_id\": \"%s\", " +
                                       "\"current_stock\": %d, \"alert_level\": \"%s\", " +
                                       "\"timestamp\": %d}",
                                       status.productId, status.warehouseId, 
                                       status.currentStock, status.alertLevel, status.lastUpdated))
            .name("Critical Alerts");
        
        // Stream 2: Real-time revenue tracking by category
        DataStream<String> revenueStream = eventStream
            .map(new RevenueCalculator())
            .keyBy(tuple -> tuple.f0) // Group by category
            .timeWindow(Time.minutes(5)) // 5-minute revenue windows
            .reduce((tuple1, tuple2) -> new Tuple3<>(tuple1.f0, tuple1.f1 + tuple2.f1, 
                                                   Math.max(tuple1.f2, tuple2.f2)))
            .map(tuple -> String.format("{\"revenue_alert\": {\"category\": \"%s\", " +
                                       "\"revenue_5min\": %.2f, \"timestamp\": %d}}",
                                       tuple.f0, tuple.f1, tuple.f2))
            .name("Revenue Analytics");
        
        // Stream 3: Top selling products by category
        DataStream<String> topSellingStream = eventStream
            .keyBy(event -> event.category)
            .timeWindow(Time.minutes(10)) // 10-minute windows for top products
            .process(new TopSellingProcessor())
            .name("Top Selling Products");
        
        // Combine all alert streams
        DataStream<String> allAlerts = criticalAlerts
            .union(revenueStream)
            .union(topSellingStream)
            .name("Combined Analytics Stream");
        
        // Output to Kafka
        allAlerts.addSink(kafkaProducer).name("Kafka Output");
        
        // Print to console for monitoring
        allAlerts.print("BBD Analytics");
        
        // Additional monitoring stream - print inventory status
        inventoryStatusStream
            .filter(status -> !"OK".equals(status.alertLevel))
            .print("Inventory Status");
        
        // Execute the job
        System.out.println("🚀 Starting Flipkart BBD Real-time Analytics...");
        System.out.println("📊 Monitoring inventory levels, revenue, and top products");
        
        env.execute("Flipkart BBD Inventory Analytics");
    }
    
    /**
     * Utility method to create sample data for testing
     * Testing के लिए sample inventory events generate करता है
     */
    public static void generateSampleData() {
        System.out.println("Sample Inventory Events for Testing:");
        
        String[] products = {"phone_001", "laptop_002", "shirt_003", "book_004", "headphone_005"};
        String[] warehouses = {"WH_MUM", "WH_DEL", "WH_BLR", "WH_CHN"};
        String[] categories = {"electronics", "fashion", "books", "accessories"};
        String[] eventTypes = {"sale", "restock", "return", "damage"};
        
        for (int i = 0; i < 10; i++) {
            String productId = products[i % products.length];
            String warehouseId = warehouses[i % warehouses.length];
            String category = categories[i % categories.length];
            String eventType = eventTypes[i % eventTypes.length];
            
            int quantityChange = "sale".equals(eventType) ? -(10 + i * 2) : (20 + i * 3);
            double price = 1000 + (i * 500);
            long timestamp = System.currentTimeMillis() + (i * 1000);
            
            String json = String.format(
                "{\"product_id\": \"%s\", \"warehouse_id\": \"%s\", \"event_type\": \"%s\", " +
                "\"quantity_change\": %d, \"timestamp\": %d, \"price\": %.2f, \"category\": \"%s\"}",
                productId, warehouseId, eventType, quantityChange, timestamp, price, category
            );
            
            System.out.println(json);
        }
    }
}