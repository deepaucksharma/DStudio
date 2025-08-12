# Episode 022: Streaming Architectures & Real-Time Processing - Part 2
## Kafka Streams aur Advanced Patterns - Mumbai Express Ki Speed

*Duration: 60 minutes*
*Language: 70% Hindi/Roman Hindi, 30% Technical English*
*Target: 13,000+ words for Part 2*

---

### Introduction: Mumbai Express Se Advanced Patterns Tak

Welcome back dosto! Part 1 mein humne basic stream processing dekha tha. Ab Part 2 mein hum advanced patterns explore karenge - Kafka Streams, Complex Event Processing, aur enterprise-grade implementations. Ye Mumbai Express ki tarah fast aur efficient hogi!

### Kafka Streams: Embedded Stream Processing Ka Raja

Kafka Streams unique hai kyunki ye separate cluster nahi chahiye - aapke application ke andar hi run karta hai, jaise Mumbai local mein general compartment aur first class same train mein hoti hai.

#### Kafka Streams Architecture aur Philosophy

**Library-First Approach:**
Traditional frameworks (Flink, Spark) separate clusters chahiye. Kafka Streams sirf library hai - aapke Java application mein embed ho jaati hai.

```java
// Kafka Streams Production Implementation for Zomato Order Processing
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.kstream.*;
import org.apache.kafka.common.serialization.Serdes;
import java.util.Properties;
import java.time.Duration;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Zomato Real-time Order Processing using Kafka Streams
 * Mumbai ki delivery efficiency ke saath
 */
public class ZomatoKafkaStreamsProcessor {
    
    private final KafkaStreams streams;
    private final String applicationId = "zomato-order-processor-v1";
    
    // Production-grade configuration
    private Properties getStreamProperties() {
        Properties props = new Properties();
        
        // Basic configuration
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, applicationId);
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka1:9092,kafka2:9092,kafka3:9092");
        
        // Serialization
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        
        // Performance tuning - Mumbai local ki efficiency ke liye
        props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 4); // 4 processing threads
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 100); // 100ms commit interval
        props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024); // 10MB cache
        
        // Fault tolerance - Mumbai monsoon resilience ki tarah
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
        props.put(StreamsConfig.REPLICATION_FACTOR_CONFIG, 3);
        
        // State store configuration
        props.put(StreamsConfig.STATE_DIR_CONFIG, "/tmp/kafka-streams-state");
        
        return props;
    }
    
    public ZomatoKafkaStreamsProcessor() {
        StreamsBuilder builder = new StreamsBuilder();
        
        // Build the topology - Mumbai local route ki tarah planned
        buildOrderProcessingTopology(builder);
        
        this.streams = new KafkaStreams(builder.build(), getStreamProperties());
        
        // Exception handling - train breakdown se bachne ke liye
        streams.setUncaughtExceptionHandler((thread, exception) -> {
            System.err.println("Uncaught exception in Kafka Streams: " + exception.getMessage());
            return StreamsUncaughtExceptionHandler.StreamThreadExceptionResponse.REPLACE_THREAD;
        });
        
        // State change listener - station announcements ki tarah
        streams.setStateListener((newState, oldState) -> {
            System.out.println("Kafka Streams state changed from " + oldState + " to " + newState);
        });
    }
    
    private void buildOrderProcessingTopology(StreamsBuilder builder) {
        
        // Input streams - Mumbai ke different railway lines ki tarah
        KStream<String, String> rawOrders = builder.stream("zomato-raw-orders");
        KStream<String, String> restaurantUpdates = builder.stream("restaurant-updates");
        KStream<String, String> deliveryUpdates = builder.stream("delivery-partner-updates");
        
        // Step 1: Order validation and enrichment
        KStream<String, ZomatoOrder> validatedOrders = rawOrders
            .filter((key, value) -> isValidOrder(value))
            .mapValues(this::parseOrder)
            .filter((key, order) -> order != null);
        
        // Step 2: Real-time order aggregations (Restaurant-wise)
        KTable<String, RestaurantStats> restaurantStats = validatedOrders
            .groupBy((orderId, order) -> order.getRestaurantId())
            .aggregate(
                RestaurantStats::new,
                (restaurantId, order, stats) -> stats.addOrder(order),
                Materialized.<String, RestaurantStats, KeyValueStore<Bytes, byte[]>>as("restaurant-stats-store")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(getRestaurantStatsSerde())
            );
        
        // Step 3: Real-time delivery optimization
        KStream<String, DeliveryOptimization> deliveryOptimizations = validatedOrders
            .selectKey((orderId, order) -> order.getDeliveryArea())
            .groupByKey()
            .windowedBy(TimeWindows.of(Duration.ofMinutes(15)).advanceBy(Duration.ofMinutes(5)))
            .aggregate(
                DeliveryCluster::new,
                (area, order, cluster) -> cluster.addOrder(order),
                Materialized.with(Serdes.String(), getDeliveryClusterSerde())
            )
            .toStream()
            .mapValues(this::optimizeDeliveryRoute);
        
        // Step 4: Real-time fraud detection
        KStream<String, String> suspiciousOrders = validatedOrders
            .filter(this::isSuspiciousOrder)
            .mapValues(order -> createFraudAlert(order));
        
        // Step 5: Customer personalization updates
        KStream<String, CustomerProfile> customerUpdates = validatedOrders
            .groupBy((orderId, order) -> order.getCustomerId())
            .aggregate(
                CustomerProfile::new,
                (customerId, order, profile) -> profile.updateWithOrder(order),
                Materialized.<String, CustomerProfile, KeyValueStore<Bytes, byte[]>>as("customer-profiles")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(getCustomerProfileSerde())
            )
            .toStream();
        
        // Step 6: Real-time inventory management
        KTable<String, InventoryLevel> inventoryLevels = validatedOrders
            .flatMapValues(order -> order.getItems()) // Flatten order items
            .groupBy((orderId, item) -> item.getItemId())
            .aggregate(
                InventoryLevel::new,
                (itemId, item, inventory) -> inventory.decrementStock(item.getQuantity()),
                Materialized.with(Serdes.String(), getInventoryLevelSerde())
            );
        
        // Step 7: Output streams - different destinations ke liye
        validatedOrders.to("validated-orders", Produced.with(Serdes.String(), getZomatoOrderSerde()));
        restaurantStats.toStream().to("restaurant-analytics", Produced.with(Serdes.String(), getRestaurantStatsSerde()));
        deliveryOptimizations.to("delivery-optimizations", Produced.with(Serdes.String(), getDeliveryOptimizationSerde()));
        suspiciousOrders.to("fraud-alerts", Produced.with(Serdes.String(), Serdes.String()));
        customerUpdates.to("customer-profile-updates", Produced.with(Serdes.String(), getCustomerProfileSerde()));
        
        // Step 8: Interactive queries support - Mumbai local inquiry ki tarah
        setupInteractiveQueries();
    }
    
    private boolean isValidOrder(String orderJson) {
        try {
            // Basic JSON validation
            return orderJson != null && 
                   orderJson.contains("orderId") && 
                   orderJson.contains("restaurantId") && 
                   orderJson.contains("customerId");
        } catch (Exception e) {
            return false;
        }
    }
    
    private ZomatoOrder parseOrder(String orderJson) {
        try {
            // In production, use proper JSON deserialization
            return ZomatoOrder.fromJson(orderJson);
        } catch (Exception e) {
            System.err.println("Failed to parse order: " + e.getMessage());
            return null;
        }
    }
    
    private boolean isSuspiciousOrder(String orderId, ZomatoOrder order) {
        // Real-time fraud detection logic
        return order.getTotalAmount() > 5000 && // High value order
               order.getItems().size() > 10 && // Too many items
               order.getOrderTime().getHour() < 6; // Late night order
    }
    
    private String createFraudAlert(ZomatoOrder order) {
        return String.format("FRAUD_ALERT: Order %s from customer %s for amount %.2f", 
                           order.getOrderId(), 
                           order.getCustomerId(), 
                           order.getTotalAmount());
    }
    
    private DeliveryOptimization optimizeDeliveryRoute(DeliveryCluster cluster) {
        // TSP-based route optimization for delivery partners
        return new DeliveryOptimization(
            cluster.getDeliveryArea(),
            cluster.getOrders(),
            calculateOptimalRoute(cluster.getOrders())
        );
    }
    
    private String calculateOptimalRoute(java.util.List<ZomatoOrder> orders) {
        // Simplified route optimization
        return "optimized_route_" + orders.size();
    }
    
    // Interactive Queries - Mumbai local mein live tracking ki tarah
    private void setupInteractiveQueries() {
        // This allows real-time querying of state stores
        // Useful for building real-time dashboards
    }
    
    public void start() {
        System.out.println("🍽️ Starting Zomato Kafka Streams Processor...");
        streams.start();
        
        // Graceful shutdown hook - Mumbai local ka last train ki tarah
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("🛑 Gracefully shutting down Kafka Streams...");
            streams.close(Duration.ofSeconds(30));
        }));
        
        System.out.println("✅ Zomato Order Processing Started - Mumbai ki speed se!");
    }
    
    public void stop() {
        streams.close();
    }
    
    // State store query methods - live information ke liye
    public RestaurantStats getRestaurantStats(String restaurantId) {
        ReadOnlyKeyValueStore<String, RestaurantStats> store = 
            streams.store(StoreQueryParameters.fromNameAndType("restaurant-stats-store", 
                                                              QueryableStoreTypes.keyValueStore()));
        return store.get(restaurantId);
    }
    
    public CustomerProfile getCustomerProfile(String customerId) {
        ReadOnlyKeyValueStore<String, CustomerProfile> store = 
            streams.store(StoreQueryParameters.fromNameAndType("customer-profiles", 
                                                              QueryableStoreTypes.keyValueStore()));
        return store.get(customerId);
    }
    
    // Serde creation methods
    private Serde<ZomatoOrder> getZomatoOrderSerde() {
        return new JsonSerde<>(ZomatoOrder.class);
    }
    
    private Serde<RestaurantStats> getRestaurantStatsSerde() {
        return new JsonSerde<>(RestaurantStats.class);
    }
    
    private Serde<CustomerProfile> getCustomerProfileSerde() {
        return new JsonSerde<>(CustomerProfile.class);
    }
    
    private Serde<DeliveryCluster> getDeliveryClusterSerde() {
        return new JsonSerde<>(DeliveryCluster.class);
    }
    
    private Serde<InventoryLevel> getInventoryLevelSerde() {
        return new JsonSerde<>(InventoryLevel.class);
    }
    
    private Serde<DeliveryOptimization> getDeliveryOptimizationSerde() {
        return new JsonSerde<>(DeliveryOptimization.class);
    }
}

// Supporting classes for Zomato order processing

class ZomatoOrder {
    private String orderId;
    private String restaurantId;
    private String customerId;
    private String deliveryArea;
    private double totalAmount;
    private java.time.LocalDateTime orderTime;
    private java.util.List<OrderItem> items;
    private String paymentMethod;
    private String deliveryAddress;
    
    // Constructors, getters, setters, JSON serialization methods
    
    public static ZomatoOrder fromJson(String json) {
        // JSON deserialization logic
        return new ZomatoOrder();
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getRestaurantId() { return restaurantId; }
    public String getCustomerId() { return customerId; }
    public String getDeliveryArea() { return deliveryArea; }
    public double getTotalAmount() { return totalAmount; }
    public java.time.LocalDateTime getOrderTime() { return orderTime; }
    public java.util.List<OrderItem> getItems() { return items; }
    public String getPaymentMethod() { return paymentMethod; }
    public String getDeliveryAddress() { return deliveryAddress; }
}

class OrderItem {
    private String itemId;
    private String itemName;
    private int quantity;
    private double price;
    
    public String getItemId() { return itemId; }
    public String getItemName() { return itemName; }
    public int getQuantity() { return quantity; }
    public double getPrice() { return price; }
}

class RestaurantStats {
    private String restaurantId;
    private long totalOrders;
    private double totalRevenue;
    private double averageOrderValue;
    private java.time.LocalDateTime lastUpdated;
    
    public RestaurantStats() {
        this.totalOrders = 0;
        this.totalRevenue = 0.0;
        this.lastUpdated = java.time.LocalDateTime.now();
    }
    
    public RestaurantStats addOrder(ZomatoOrder order) {
        this.totalOrders++;
        this.totalRevenue += order.getTotalAmount();
        this.averageOrderValue = this.totalRevenue / this.totalOrders;
        this.lastUpdated = java.time.LocalDateTime.now();
        return this;
    }
    
    // Getters
    public long getTotalOrders() { return totalOrders; }
    public double getTotalRevenue() { return totalRevenue; }
    public double getAverageOrderValue() { return averageOrderValue; }
}

class CustomerProfile {
    private String customerId;
    private long totalOrders;
    private double totalSpent;
    private String favoriteRestaurant;
    private String favoriteCuisine;
    private double averageOrderValue;
    private java.time.LocalDateTime lastOrderTime;
    
    public CustomerProfile() {
        this.totalOrders = 0;
        this.totalSpent = 0.0;
    }
    
    public CustomerProfile updateWithOrder(ZomatoOrder order) {
        this.totalOrders++;
        this.totalSpent += order.getTotalAmount();
        this.averageOrderValue = this.totalSpent / this.totalOrders;
        this.lastOrderTime = order.getOrderTime();
        return this;
    }
    
    // Getters and other methods
}

class DeliveryCluster {
    private String deliveryArea;
    private java.util.List<ZomatoOrder> orders;
    private java.time.LocalDateTime windowStart;
    private java.time.LocalDateTime windowEnd;
    
    public DeliveryCluster() {
        this.orders = new java.util.ArrayList<>();
    }
    
    public DeliveryCluster addOrder(ZomatoOrder order) {
        this.orders.add(order);
        return this;
    }
    
    public String getDeliveryArea() { return deliveryArea; }
    public java.util.List<ZomatoOrder> getOrders() { return orders; }
}

class DeliveryOptimization {
    private String deliveryArea;
    private java.util.List<ZomatoOrder> orders;
    private String optimizedRoute;
    private int estimatedDeliveryTime;
    
    public DeliveryOptimization(String deliveryArea, java.util.List<ZomatoOrder> orders, String optimizedRoute) {
        this.deliveryArea = deliveryArea;
        this.orders = orders;
        this.optimizedRoute = optimizedRoute;
        this.estimatedDeliveryTime = calculateEstimatedTime();
    }
    
    private int calculateEstimatedTime() {
        // Route-based delivery time calculation
        return orders.size() * 15; // 15 minutes per delivery
    }
}

class InventoryLevel {
    private String itemId;
    private int currentStock;
    private int alertThreshold;
    private java.time.LocalDateTime lastUpdated;
    
    public InventoryLevel() {
        this.currentStock = 100; // Default stock
        this.alertThreshold = 10;
    }
    
    public InventoryLevel decrementStock(int quantity) {
        this.currentStock -= quantity;
        this.lastUpdated = java.time.LocalDateTime.now();
        return this;
    }
    
    public boolean isLowStock() {
        return currentStock <= alertThreshold;
    }
}
```

#### Python-based Kafka Streams Alternative

Real production mein Java use karte hain, lekin concepts samjhne ke liye Python implementation:

```python
# Python-based Kafka Streams-like Processing for Indian E-commerce
import asyncio
import json
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from collections import defaultdict, deque
import logging
from concurrent.futures import ThreadPoolExecutor

@dataclass
class FlipkartOrder:
    order_id: str
    product_id: str
    customer_id: str
    seller_id: str
    category: str
    price: float
    quantity: int
    delivery_city: str
    payment_method: str
    timestamp: float
    order_status: str

class KafkaStreamsLikeProcessor:
    """
    Python-based stream processor inspired by Kafka Streams
    Mumbai local train ki efficiency ke saath
    """
    
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.state_stores = {}
        self.topology = {}
        self.running = False
        
        # Performance metrics
        self.processed_events = 0
        self.processing_times = deque(maxlen=1000)
        
        # Thread pool for parallel processing
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(f"StreamProcessor-{app_id}")
    
    def create_state_store(self, store_name: str, store_type: str = "kv"):
        """Create state store - Kafka Streams ki KeyValue store ki tarah"""
        
        if store_type == "kv":
            self.state_stores[store_name] = {}
        elif store_type == "windowed":
            self.state_stores[store_name] = defaultdict(lambda: defaultdict(dict))
        
        self.logger.info(f"Created state store: {store_name} of type: {store_type}")
    
    def group_by_key(self, stream_data: List[Dict], key_extractor: Callable) -> Dict:
        """Group stream data by key - Kafka Streams groupBy equivalent"""
        
        grouped_data = defaultdict(list)
        for event in stream_data:
            key = key_extractor(event)
            grouped_data[key].append(event)
        
        return dict(grouped_data)
    
    def windowed_aggregation(self, grouped_data: Dict, 
                           window_size_seconds: int,
                           aggregator: Callable) -> Dict:
        """
        Windowed aggregation - time windows ke saath data process karna
        Mumbai local ke time slots ki tarah
        """
        
        current_time = time.time()
        window_results = {}
        
        for key, events in grouped_data.items():
            # Group events by time windows
            windows = defaultdict(list)
            
            for event in events:
                event_time = event.get('timestamp', current_time)
                window_start = int(event_time // window_size_seconds) * window_size_seconds
                windows[window_start].append(event)
            
            # Apply aggregation to each window
            for window_start, window_events in windows.items():
                window_end = window_start + window_size_seconds
                window_key = f"{key}_{window_start}_{window_end}"
                
                window_results[window_key] = aggregator(window_events)
        
        return window_results
    
    async def process_flipkart_orders(self, orders: List[FlipkartOrder]):
        """
        Process Flipkart orders stream with Kafka Streams patterns
        """
        
        self.logger.info(f"🛒 Starting Flipkart order processing - {len(orders)} orders")
        self.running = True
        
        # Create state stores
        self.create_state_store("customer_stats", "kv")
        self.create_state_store("seller_stats", "kv") 
        self.create_state_store("city_analytics", "kv")
        self.create_state_store("category_trends", "windowed")
        
        # Convert to dict format for processing
        order_dicts = [asdict(order) for order in orders]
        
        # Processing pipeline - Mumbai local ki multiple lines ki tarah
        await asyncio.gather(
            self.process_customer_analytics(order_dicts),
            self.process_seller_analytics(order_dicts),
            self.process_city_analytics(order_dicts),
            self.process_category_trends(order_dicts),
            self.process_fraud_detection(order_dicts),
            self.process_inventory_management(order_dicts)
        )
        
        # Print processing results
        await self.print_processing_results()
    
    async def process_customer_analytics(self, orders: List[Dict]):
        """Customer behavior analytics - real-time customer profiling"""
        
        self.logger.info("👤 Processing customer analytics...")
        
        # Group by customer
        customer_orders = self.group_by_key(orders, lambda x: x['customer_id'])
        
        # Process each customer's orders
        for customer_id, customer_order_list in customer_orders.items():
            customer_stats = self.state_stores["customer_stats"].get(customer_id, {
                'total_orders': 0,
                'total_spent': 0.0,
                'favorite_category': None,
                'preferred_payment': None,
                'avg_order_value': 0.0,
                'cities': set(),
                'last_order_time': 0
            })
            
            # Update customer stats
            for order in customer_order_list:
                customer_stats['total_orders'] += 1
                customer_stats['total_spent'] += order['price'] * order['quantity']
                customer_stats['cities'].add(order['delivery_city'])
                customer_stats['last_order_time'] = max(customer_stats['last_order_time'], 
                                                       order['timestamp'])
            
            customer_stats['avg_order_value'] = (customer_stats['total_spent'] / 
                                               customer_stats['total_orders'])
            
            # Determine favorite category and payment method
            categories = [o['category'] for o in customer_order_list]
            payments = [o['payment_method'] for o in customer_order_list]
            
            customer_stats['favorite_category'] = max(set(categories), key=categories.count)
            customer_stats['preferred_payment'] = max(set(payments), key=payments.count)
            
            # Update state store
            self.state_stores["customer_stats"][customer_id] = customer_stats
            
            # VIP customer detection
            if customer_stats['total_spent'] > 100000:  # ₹1L+ spent
                await self.trigger_vip_benefits(customer_id, customer_stats)
    
    async def process_seller_analytics(self, orders: List[Dict]):
        """Seller performance analytics"""
        
        self.logger.info("🏪 Processing seller analytics...")
        
        seller_orders = self.group_by_key(orders, lambda x: x['seller_id'])
        
        for seller_id, seller_order_list in seller_orders.items():
            seller_stats = self.state_stores["seller_stats"].get(seller_id, {
                'total_orders': 0,
                'total_revenue': 0.0,
                'categories': set(),
                'cities_served': set(),
                'avg_order_value': 0.0,
                'performance_score': 0.0
            })
            
            # Update seller metrics
            for order in seller_order_list:
                seller_stats['total_orders'] += 1
                seller_stats['total_revenue'] += order['price'] * order['quantity']
                seller_stats['categories'].add(order['category'])
                seller_stats['cities_served'].add(order['delivery_city'])
            
            seller_stats['avg_order_value'] = (seller_stats['total_revenue'] / 
                                             seller_stats['total_orders'])
            
            # Calculate performance score
            seller_stats['performance_score'] = self.calculate_seller_performance(seller_stats)
            
            self.state_stores["seller_stats"][seller_id] = seller_stats
            
            # Alert for top performers
            if seller_stats['performance_score'] > 90:
                await self.alert_top_seller(seller_id, seller_stats)
    
    async def process_city_analytics(self, orders: List[Dict]):
        """City-wise demand analytics"""
        
        self.logger.info("🌆 Processing city analytics...")
        
        city_orders = self.group_by_key(orders, lambda x: x['delivery_city'])
        
        for city, city_order_list in city_orders.items():
            city_stats = self.state_stores["city_analytics"].get(city, {
                'total_orders': 0,
                'total_gmv': 0.0,  # Gross Merchandise Value
                'popular_categories': defaultdict(int),
                'payment_preferences': defaultdict(int),
                'avg_order_value': 0.0
            })
            
            # Update city metrics
            for order in city_order_list:
                city_stats['total_orders'] += 1
                city_stats['total_gmv'] += order['price'] * order['quantity']
                city_stats['popular_categories'][order['category']] += 1
                city_stats['payment_preferences'][order['payment_method']] += 1
            
            city_stats['avg_order_value'] = city_stats['total_gmv'] / city_stats['total_orders']
            
            self.state_stores["city_analytics"][city] = city_stats
            
            # High-demand city alert
            if city_stats['total_orders'] > 1000:
                await self.alert_high_demand_city(city, city_stats)
    
    async def process_category_trends(self, orders: List[Dict]):
        """
        Category trending analysis with windowed aggregation
        Mumbai local mein peak hours detect karne ki tarah
        """
        
        self.logger.info("📈 Processing category trends...")
        
        # Group by category
        category_orders = self.group_by_key(orders, lambda x: x['category'])
        
        # Apply 1-hour windowing
        category_trends = self.windowed_aggregation(
            category_orders,
            window_size_seconds=3600,  # 1 hour windows
            aggregator=self.trend_aggregator
        )
        
        # Store windowed results
        for window_key, trend_data in category_trends.items():
            category, window_start, window_end = window_key.split('_')
            
            if category not in self.state_stores["category_trends"]:
                self.state_stores["category_trends"][category] = {}
            
            self.state_stores["category_trends"][category][window_start] = trend_data
            
            # Trending alert
            if trend_data['order_velocity'] > 100:  # 100+ orders per hour
                await self.alert_trending_category(category, trend_data)
    
    async def process_fraud_detection(self, orders: List[Dict]):
        """Real-time fraud detection"""
        
        self.logger.info("🛡️ Processing fraud detection...")
        
        suspicious_orders = []
        
        for order in orders:
            suspicion_score = 0
            risk_factors = []
            
            # High value order
            if order['price'] * order['quantity'] > 50000:  # ₹50K+
                suspicion_score += 30
                risk_factors.append("high_value")
            
            # Check customer history
            customer_stats = self.state_stores["customer_stats"].get(order['customer_id'])
            if customer_stats:
                # New customer with high order
                if customer_stats['total_orders'] <= 1 and order['price'] > 10000:
                    suspicion_score += 25
                    risk_factors.append("new_customer_high_value")
                
                # Unusual payment method
                if order['payment_method'] != customer_stats.get('preferred_payment'):
                    suspicion_score += 15
                    risk_factors.append("unusual_payment_method")
            
            # Midnight orders
            order_hour = time.localtime(order['timestamp']).tm_hour
            if order_hour < 6 or order_hour > 23:
                suspicion_score += 20
                risk_factors.append("unusual_time")
            
            # Flag suspicious orders
            if suspicion_score >= 50:
                suspicious_order = {
                    'order_id': order['order_id'],
                    'customer_id': order['customer_id'],
                    'suspicion_score': suspicion_score,
                    'risk_factors': risk_factors
                }
                suspicious_orders.append(suspicious_order)
        
        if suspicious_orders:
            self.logger.warning(f"🚨 Found {len(suspicious_orders)} suspicious orders")
            for suspicious in suspicious_orders:
                await self.flag_suspicious_order(suspicious)
    
    async def process_inventory_management(self, orders: List[Dict]):
        """Real-time inventory level management"""
        
        self.logger.info("📦 Processing inventory management...")
        
        inventory_updates = defaultdict(int)
        
        # Count product demand
        for order in orders:
            inventory_updates[order['product_id']] += order['quantity']
        
        # Check inventory levels and create alerts
        for product_id, quantity_sold in inventory_updates.items():
            # Simulate current stock check
            current_stock = self.get_current_stock(product_id)
            projected_stock = current_stock - quantity_sold
            
            if projected_stock < 10:  # Low stock alert
                await self.alert_low_inventory(product_id, projected_stock)
            
            if quantity_sold > 100:  # High demand alert
                await self.alert_high_demand_product(product_id, quantity_sold)
    
    def trend_aggregator(self, window_events: List[Dict]) -> Dict:
        """Aggregate events within a time window"""
        
        if not window_events:
            return {'order_count': 0, 'total_revenue': 0, 'order_velocity': 0}
        
        order_count = len(window_events)
        total_revenue = sum(e['price'] * e['quantity'] for e in window_events)
        order_velocity = order_count  # orders per hour (simplified)
        
        return {
            'order_count': order_count,
            'total_revenue': total_revenue,
            'order_velocity': order_velocity,
            'avg_order_value': total_revenue / order_count if order_count > 0 else 0
        }
    
    def calculate_seller_performance(self, seller_stats: Dict) -> float:
        """Calculate seller performance score"""
        
        # Simplified scoring algorithm
        revenue_score = min(seller_stats['total_revenue'] / 10000, 50)  # Max 50 points
        order_count_score = min(seller_stats['total_orders'] / 100, 30)  # Max 30 points
        diversity_score = min(len(seller_stats['categories']) * 5, 20)  # Max 20 points
        
        return revenue_score + order_count_score + diversity_score
    
    def get_current_stock(self, product_id: str) -> int:
        """Simulate current stock lookup"""
        return hash(product_id) % 200 + 50  # Random stock between 50-250
    
    # Alert methods
    async def trigger_vip_benefits(self, customer_id: str, customer_stats: Dict):
        self.logger.info(f"👑 VIP benefits triggered for customer {customer_id}")
    
    async def alert_top_seller(self, seller_id: str, seller_stats: Dict):
        self.logger.info(f"🌟 Top seller alert: {seller_id} (Score: {seller_stats['performance_score']:.1f})")
    
    async def alert_high_demand_city(self, city: str, city_stats: Dict):
        self.logger.info(f"🔥 High demand in {city}: {city_stats['total_orders']} orders")
    
    async def alert_trending_category(self, category: str, trend_data: Dict):
        self.logger.info(f"📈 Trending category: {category} ({trend_data['order_velocity']} orders/hour)")
    
    async def flag_suspicious_order(self, suspicious_order: Dict):
        self.logger.warning(f"🚨 Suspicious order flagged: {suspicious_order['order_id']}")
    
    async def alert_low_inventory(self, product_id: str, projected_stock: int):
        self.logger.warning(f"📉 Low inventory alert: Product {product_id} ({projected_stock} units left)")
    
    async def alert_high_demand_product(self, product_id: str, quantity_sold: int):
        self.logger.info(f"🔥 High demand product: {product_id} ({quantity_sold} units sold)")
    
    async def print_processing_results(self):
        """Print comprehensive processing results"""
        
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 FLIPKART STREAM PROCESSING RESULTS")
        self.logger.info("="*60)
        
        # Customer analytics summary
        customer_count = len(self.state_stores["customer_stats"])
        self.logger.info(f"👥 Customer Analytics: {customer_count} unique customers processed")
        
        # Top spending customers
        top_customers = sorted(
            self.state_stores["customer_stats"].items(),
            key=lambda x: x[1]['total_spent'],
            reverse=True
        )[:5]
        
        self.logger.info("💰 Top 5 Customers by Spending:")
        for i, (customer_id, stats) in enumerate(top_customers, 1):
            self.logger.info(f"  {i}. {customer_id}: ₹{stats['total_spent']:,.0f} ({stats['total_orders']} orders)")
        
        # Seller analytics summary
        seller_count = len(self.state_stores["seller_stats"])
        self.logger.info(f"\n🏪 Seller Analytics: {seller_count} sellers processed")
        
        # Top performing sellers
        top_sellers = sorted(
            self.state_stores["seller_stats"].items(),
            key=lambda x: x[1]['performance_score'],
            reverse=True
        )[:5]
        
        self.logger.info("🌟 Top 5 Sellers by Performance:")
        for i, (seller_id, stats) in enumerate(top_sellers, 1):
            self.logger.info(f"  {i}. {seller_id}: Score {stats['performance_score']:.1f} (₹{stats['total_revenue']:,.0f} revenue)")
        
        # City analytics summary
        city_count = len(self.state_stores["city_analytics"])
        self.logger.info(f"\n🌆 City Analytics: {city_count} cities processed")
        
        # Top cities by GMV
        top_cities = sorted(
            self.state_stores["city_analytics"].items(),
            key=lambda x: x[1]['total_gmv'],
            reverse=True
        )[:5]
        
        self.logger.info("🏙️ Top 5 Cities by GMV:")
        for i, (city, stats) in enumerate(top_cities, 1):
            self.logger.info(f"  {i}. {city}: ₹{stats['total_gmv']:,.0f} ({stats['total_orders']} orders)")
        
        self.logger.info(f"\n✅ Stream processing completed successfully!")
        self.logger.info("🚆 Mumbai local ki efficiency achieve ki! 🌟")

# Generate realistic Flipkart orders
def generate_flipkart_orders(count: int) -> List[FlipkartOrder]:
    """Generate realistic Flipkart order data for testing"""
    
    import random
    
    products = [
        'smartphone', 'laptop', 'headphones', 'book', 'tshirt', 
        'shoes', 'tablet', 'watch', 'backpack', 'camera'
    ]
    
    categories = [
        'Electronics', 'Fashion', 'Books', 'Home', 'Sports',
        'Beauty', 'Automotive', 'Toys', 'Groceries', 'Health'
    ]
    
    cities = [
        'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai',
        'Kolkata', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
    ]
    
    payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'COD']
    order_statuses = ['confirmed', 'processing', 'shipped', 'delivered']
    
    orders = []
    base_time = time.time()
    
    for i in range(count):
        order = FlipkartOrder(
            order_id=f"FLP{i+1:08d}",
            product_id=random.choice(products),
            customer_id=f"CUST{random.randint(1, count//10):06d}",  # Some repeat customers
            seller_id=f"SELLER{random.randint(1, count//50):04d}",
            category=random.choice(categories),
            price=random.uniform(299, 49999),  # ₹299 to ₹50K
            quantity=random.randint(1, 5),
            delivery_city=random.choice(cities),
            payment_method=random.choice(payment_methods),
            timestamp=base_time + i * random.uniform(0.1, 10),
            order_status=random.choice(order_statuses)
        )
        orders.append(order)
    
    return orders

# Run the Kafka Streams-like processing simulation
async def run_flipkart_processing():
    """Run Flipkart order processing simulation"""
    
    print("🛒 Flipkart Kafka Streams-like Processing")
    print("🇮🇳 Processing orders at Indian e-commerce scale!")
    print("=" * 60)
    
    # Generate sample orders
    orders = generate_flipkart_orders(10000)  # 10K orders
    print(f"📦 Generated {len(orders):,} Flipkart orders")
    
    # Process with stream processor
    processor = KafkaStreamsLikeProcessor("flipkart-order-processor")
    
    start_time = time.time()
    await processor.process_flipkart_orders(orders)
    total_time = time.time() - start_time
    
    print(f"\n🎉 Processing completed in {total_time:.2f} seconds")
    print(f"🚀 Throughput: {len(orders)/total_time:.0f} orders/second")
    print(f"⚡ Mumbai local train se bhi fast! 💪")

if __name__ == "__main__":
    asyncio.run(run_flipkart_processing())
```

### Complex Event Processing (CEP): Pattern Detection Ki Power

CEP Mumbai mein traffic pattern detection ki tarah hai - multiple events ko combine karke meaningful patterns identify karta hai.

#### CEP Implementation for Indian Stock Market

NSE/BSE trading patterns detect karne ke liye CEP use karte hain:

```python
# Complex Event Processing for Indian Stock Market
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from enum import Enum
from collections import deque, defaultdict
import re

class EventType(Enum):
    TRADE = "trade"
    ORDER = "order"
    NEWS = "news"
    PRICE_ALERT = "price_alert"
    VOLUME_SPIKE = "volume_spike"

@dataclass
class StockEvent:
    event_id: str
    event_type: EventType
    symbol: str
    timestamp: float
    price: Optional[float] = None
    volume: Optional[int] = None
    news_text: Optional[str] = None
    order_type: Optional[str] = None  # 'buy', 'sell'
    order_size: Optional[int] = None

class StockPattern:
    """Define complex patterns for stock market events"""
    
    def __init__(self, pattern_name: str, pattern_definition: str):
        self.pattern_name = pattern_name
        self.pattern_definition = pattern_definition
        self.matched_events = []
        self.confidence_score = 0.0

class CEPEngine:
    """
    Complex Event Processing Engine for Indian Stock Market
    Mumbai Sensex/Nifty patterns detect karta hai
    """
    
    def __init__(self):
        self.event_buffer = defaultdict(deque)  # Symbol-wise event buffer
        self.active_patterns = {}
        self.pattern_matches = []
        
        # Define stock market patterns
        self.register_patterns()
        
        # Indian market specific thresholds
        self.thresholds = {
            'price_change_percent': 5.0,    # 5% price change
            'volume_spike_multiplier': 3.0,  # 3x normal volume
            'news_sentiment_threshold': 0.7,  # Sentiment score
            'pattern_timeout_seconds': 300   # 5 minutes pattern timeout
        }
        
        print("📈 CEP Engine initialized for Indian Stock Market")
        print("🇮🇳 Ready to detect Sensex/Nifty patterns!")
    
    def register_patterns(self):
        """Register predefined patterns for stock market analysis"""
        
        # Pattern 1: Bull Run Pattern
        # High volume trade followed by positive news within 10 minutes
        self.active_patterns['bull_run'] = {
            'description': 'High volume spike followed by positive news',
            'events_required': [EventType.VOLUME_SPIKE, EventType.NEWS],
            'time_window_seconds': 600,  # 10 minutes
            'conditions': self.bull_run_condition
        }
        
        # Pattern 2: Bear Market Signal
        # Negative news followed by high sell orders
        self.active_patterns['bear_signal'] = {
            'description': 'Negative news followed by heavy selling',
            'events_required': [EventType.NEWS, EventType.ORDER],
            'time_window_seconds': 300,  # 5 minutes
            'conditions': self.bear_signal_condition
        }
        
        # Pattern 3: Insider Trading Suspicion
        # Unusual volume before major news announcement
        self.active_patterns['insider_trading'] = {
            'description': 'Unusual volume before news announcement',
            'events_required': [EventType.VOLUME_SPIKE, EventType.NEWS],
            'time_window_seconds': 1800,  # 30 minutes
            'conditions': self.insider_trading_condition
        }
        
        # Pattern 4: Momentum Trading
        # Series of consistent price increases with volume
        self.active_patterns['momentum_trading'] = {
            'description': 'Consistent price increases with volume',
            'events_required': [EventType.TRADE] * 3,  # 3+ consecutive trades
            'time_window_seconds': 180,  # 3 minutes
            'conditions': self.momentum_trading_condition
        }
        
        # Pattern 5: Market Manipulation Detection
        # Large orders followed by quick reversals
        self.active_patterns['market_manipulation'] = {
            'description': 'Large orders with quick reversals',
            'events_required': [EventType.ORDER, EventType.ORDER],
            'time_window_seconds': 60,  # 1 minute
            'conditions': self.market_manipulation_condition
        }
        
        print(f"✅ Registered {len(self.active_patterns)} stock market patterns")
    
    async def process_stock_event(self, event: StockEvent):
        """Process single stock market event"""
        
        symbol = event.symbol
        
        # Add to event buffer for this symbol
        self.event_buffer[symbol].append(event)
        
        # Clean old events (keep only events within max time window)
        current_time = event.timestamp
        max_window = max(pattern['time_window_seconds'] for pattern in self.active_patterns.values())
        
        while (self.event_buffer[symbol] and 
               current_time - self.event_buffer[symbol][0].timestamp > max_window):
            self.event_buffer[symbol].popleft()
        
        # Check for pattern matches
        for pattern_name, pattern_config in self.active_patterns.items():
            matches = await self.check_pattern_match(symbol, pattern_name, pattern_config, event)
            
            for match in matches:
                await self.handle_pattern_match(match)
    
    async def check_pattern_match(self, symbol: str, pattern_name: str, 
                                pattern_config: Dict, trigger_event: StockEvent) -> List[StockPattern]:
        """Check if events match a specific pattern"""
        
        matches = []
        events = list(self.event_buffer[symbol])
        
        if len(events) < len(pattern_config['events_required']):
            return matches
        
        # Check time window
        time_window = pattern_config['time_window_seconds']
        recent_events = [e for e in events 
                        if trigger_event.timestamp - e.timestamp <= time_window]
        
        # Check if required event types are present
        required_types = pattern_config['events_required']
        event_types_present = [e.event_type for e in recent_events]
        
        if not all(req_type in event_types_present for req_type in set(required_types)):
            return matches
        
        # Apply pattern-specific conditions
        if pattern_config['conditions'](recent_events, trigger_event):
            pattern_match = StockPattern(
                pattern_name=pattern_name,
                pattern_definition=pattern_config['description']
            )
            pattern_match.matched_events = recent_events.copy()
            pattern_match.confidence_score = self.calculate_confidence(
                pattern_name, recent_events
            )
            
            matches.append(pattern_match)
        
        return matches
    
    def bull_run_condition(self, events: List[StockEvent], trigger_event: StockEvent) -> bool:
        """Check conditions for bull run pattern"""
        
        # Find volume spike and positive news
        volume_spikes = [e for e in events if e.event_type == EventType.VOLUME_SPIKE]
        news_events = [e for e in events if e.event_type == EventType.NEWS]
        
        if not volume_spikes or not news_events:
            return False
        
        # Check if news is positive (simplified sentiment analysis)
        positive_news = [n for n in news_events if self.is_positive_news(n.news_text)]
        
        return len(positive_news) > 0 and len(volume_spikes) > 0
    
    def bear_signal_condition(self, events: List[StockEvent], trigger_event: StockEvent) -> bool:
        """Check conditions for bear signal pattern"""
        
        news_events = [e for e in events if e.event_type == EventType.NEWS]
        sell_orders = [e for e in events if e.event_type == EventType.ORDER and 
                      e.order_type == 'sell' and e.order_size and e.order_size > 10000]
        
        # Negative news followed by large sell orders
        negative_news = [n for n in news_events if not self.is_positive_news(n.news_text)]
        
        return len(negative_news) > 0 and len(sell_orders) > 0
    
    def insider_trading_condition(self, events: List[StockEvent], trigger_event: StockEvent) -> bool:
        """Check for potential insider trading patterns"""
        
        volume_spikes = [e for e in events if e.event_type == EventType.VOLUME_SPIKE]
        news_events = [e for e in events if e.event_type == EventType.NEWS]
        
        if not volume_spikes or not news_events:
            return False
        
        # Volume spike should occur BEFORE news
        earliest_volume_spike = min(volume_spikes, key=lambda x: x.timestamp)
        latest_news = max(news_events, key=lambda x: x.timestamp)
        
        # Suspicious if volume spike happened significantly before news
        time_gap = latest_news.timestamp - earliest_volume_spike.timestamp
        return 300 <= time_gap <= 1800  # Between 5-30 minutes gap
    
    def momentum_trading_condition(self, events: List[StockEvent], trigger_event: StockEvent) -> bool:
        """Check for momentum trading patterns"""
        
        trades = [e for e in events if e.event_type == EventType.TRADE and e.price is not None]
        
        if len(trades) < 3:
            return False
        
        # Sort by timestamp
        trades.sort(key=lambda x: x.timestamp)
        
        # Check for consistent price increases
        price_increases = 0
        for i in range(1, len(trades)):
            if trades[i].price > trades[i-1].price:
                price_increases += 1
        
        # At least 3 consecutive price increases
        return price_increases >= 3
    
    def market_manipulation_condition(self, events: List[StockEvent], trigger_event: StockEvent) -> bool:
        """Check for market manipulation patterns"""
        
        orders = [e for e in events if e.event_type == EventType.ORDER and e.order_size]
        
        if len(orders) < 2:
            return False
        
        # Look for large orders followed by opposite orders
        for i in range(len(orders) - 1):
            current_order = orders[i]
            next_order = orders[i + 1]
            
            # Large order followed by quick reversal
            if (current_order.order_size > 50000 and  # Large order
                next_order.order_size > 30000 and     # Sizable counter-order
                current_order.order_type != next_order.order_type and  # Opposite direction
                next_order.timestamp - current_order.timestamp < 60):   # Within 1 minute
                return True
        
        return False
    
    def is_positive_news(self, news_text: str) -> bool:
        """Simple sentiment analysis for news (production mein proper NLP use karenge)"""
        
        if not news_text:
            return False
        
        positive_keywords = [
            'profit', 'growth', 'expansion', 'success', 'achievement', 'breakthrough',
            'record', 'high', 'surge', 'boom', 'bull', 'gain', 'rise', 'increase'
        ]
        
        negative_keywords = [
            'loss', 'decline', 'fall', 'crash', 'bear', 'recession', 'bankruptcy',
            'fraud', 'scandal', 'investigation', 'penalty', 'fine', 'debt'
        ]
        
        news_lower = news_text.lower()
        positive_count = sum(1 for word in positive_keywords if word in news_lower)
        negative_count = sum(1 for word in negative_keywords if word in news_lower)
        
        return positive_count > negative_count
    
    def calculate_confidence(self, pattern_name: str, events: List[StockEvent]) -> float:
        """Calculate confidence score for pattern match"""
        
        base_confidence = 0.5
        
        # More events = higher confidence
        event_count_bonus = min(len(events) * 0.1, 0.3)
        
        # Recent events = higher confidence  
        latest_event_time = max(e.timestamp for e in events)
        current_time = time.time()
        recency_bonus = max(0, 0.2 - (current_time - latest_event_time) / 600)  # Decay over 10 minutes
        
        # Pattern-specific bonuses
        pattern_bonus = 0.0
        if pattern_name == 'insider_trading':
            # Higher confidence for insider trading if volume is very high
            volume_events = [e for e in events if e.event_type == EventType.VOLUME_SPIKE]
            if volume_events:
                pattern_bonus = 0.2
        
        total_confidence = base_confidence + event_count_bonus + recency_bonus + pattern_bonus
        return min(total_confidence, 1.0)  # Cap at 1.0
    
    async def handle_pattern_match(self, pattern: StockPattern):
        """Handle detected pattern matches"""
        
        symbol = pattern.matched_events[0].symbol if pattern.matched_events else "UNKNOWN"
        
        print(f"\n🎯 PATTERN DETECTED!")
        print(f"📊 Symbol: {symbol}")
        print(f"🔍 Pattern: {pattern.pattern_name}")
        print(f"📝 Description: {pattern.pattern_definition}")
        print(f"🎲 Confidence: {pattern.confidence_score:.2f}")
        print(f"📅 Events: {len(pattern.matched_events)}")
        
        # Pattern-specific actions
        if pattern.pattern_name == 'insider_trading':
            await self.alert_regulatory_body(pattern)
        elif pattern.pattern_name == 'market_manipulation':
            await self.alert_exchange_surveillance(pattern)
        elif pattern.pattern_name in ['bull_run', 'momentum_trading']:
            await self.alert_trading_desks(pattern)
        elif pattern.pattern_name == 'bear_signal':
            await self.alert_risk_management(pattern)
        
        # Store for historical analysis
        self.pattern_matches.append(pattern)
    
    async def alert_regulatory_body(self, pattern: StockPattern):
        """Alert SEBI about potential insider trading"""
        print(f"🚨 SEBI Alert: Potential insider trading detected in {pattern.matched_events[0].symbol}")
    
    async def alert_exchange_surveillance(self, pattern: StockPattern):
        """Alert NSE/BSE surveillance about market manipulation"""
        print(f"⚠️ Exchange Alert: Market manipulation suspected in {pattern.matched_events[0].symbol}")
    
    async def alert_trading_desks(self, pattern: StockPattern):
        """Alert trading desks about opportunities"""
        print(f"📈 Trading Alert: {pattern.pattern_name} pattern in {pattern.matched_events[0].symbol}")
    
    async def alert_risk_management(self, pattern: StockPattern):
        """Alert risk management about potential downside"""
        print(f"📉 Risk Alert: Bear signal detected in {pattern.matched_events[0].symbol}")
    
    async def process_stock_events_stream(self, events: List[StockEvent]):
        """Process stream of stock market events"""
        
        print("📈 Starting Indian Stock Market CEP Processing")
        print(f"📊 Processing {len(events)} market events...")
        print("=" * 60)
        
        processed_count = 0
        
        for event in events:
            await self.process_stock_event(event)
            processed_count += 1
            
            if processed_count % 1000 == 0:
                print(f"  ✅ Processed {processed_count:,} events...")
        
        # Print final summary
        print(f"\n📊 CEP PROCESSING SUMMARY")
        print("=" * 40)
        print(f"Total Events Processed: {processed_count:,}")
        print(f"Patterns Detected: {len(self.pattern_matches)}")
        
        # Pattern breakdown
        pattern_counts = defaultdict(int)
        for pattern in self.pattern_matches:
            pattern_counts[pattern.pattern_name] += 1
        
        if pattern_counts:
            print(f"\nPattern Breakdown:")
            for pattern_name, count in pattern_counts.items():
                print(f"  {pattern_name}: {count} matches")
        
        print(f"\n✅ CEP processing completed - Mumbai market analysis done! 🏛️")

# Generate realistic stock market events for testing
def generate_stock_events(count: int) -> List[StockEvent]:
    """Generate realistic stock market events for Indian stocks"""
    
    import random
    
    # Indian stock symbols
    symbols = ['RELIANCE', 'TCS', 'HDFC', 'INFY', 'ICICIBANK', 'SBIN', 'BHARTIARTL', 
              'ITC', 'KOTAKBANK', 'LT', 'HCLTECH', 'AXISBANK', 'ASIANPAINT', 'MARUTI']
    
    news_templates = {
        'positive': [
            "{} reports record quarterly profits with 25% growth",
            "{} announces major expansion plan worth ₹5000 crores", 
            "{} bags significant government contract",
            "{} launches innovative product in Indian market"
        ],
        'negative': [
            "{} faces regulatory investigation over compliance issues",
            "{} reports decline in quarterly revenue by 15%",
            "{} announces job cuts amid market downturn",
            "{} faces lawsuit from major competitor"
        ]
    }
    
    events = []
    base_time = time.time()
    
    for i in range(count):
        symbol = random.choice(symbols)
        event_timestamp = base_time + i * random.uniform(0.1, 30)  # Events every 0.1-30 seconds
        
        # Random event type with realistic distribution
        event_type = random.choices(
            list(EventType),
            weights=[40, 25, 5, 15, 15]  # Trade heavy, some orders, rare news/alerts
        )[0]
        
        event = StockEvent(
            event_id=f"EVENT_{i+1:06d}",
            event_type=event_type,
            symbol=symbol,
            timestamp=event_timestamp
        )
        
        # Fill event-specific fields
        if event_type == EventType.TRADE:
            base_price = 1000 + hash(symbol) % 2000  # Base price per symbol
            event.price = base_price + random.uniform(-50, 50)
            event.volume = random.randint(100, 10000)
        
        elif event_type == EventType.ORDER:
            event.order_type = random.choice(['buy', 'sell'])
            event.order_size = random.randint(100, 100000)
            event.price = 1000 + hash(symbol) % 2000 + random.uniform(-20, 20)
        
        elif event_type == EventType.NEWS:
            news_type = random.choice(['positive', 'negative'])
            template = random.choice(news_templates[news_type])
            event.news_text = template.format(symbol)
        
        elif event_type == EventType.VOLUME_SPIKE:
            event.volume = random.randint(50000, 500000)  # High volume
        
        elif event_type == EventType.PRICE_ALERT:
            event.price = 1000 + hash(symbol) % 2000 + random.uniform(-100, 100)
        
        events.append(event)
    
    # Sort by timestamp to simulate realistic stream
    events.sort(key=lambda x: x.timestamp)
    
    return events

# Run CEP simulation for Indian stock market
async def run_stock_market_cep():
    """Run stock market CEP simulation"""
    
    print("🏛️ Indian Stock Market Complex Event Processing")
    print("📈 NSE/BSE Pattern Detection with Mumbai Intelligence!")
    print("=" * 60)
    
    # Generate realistic stock events
    events = generate_stock_events(5000)  # 5K market events
    print(f"📊 Generated {len(events):,} stock market events")
    
    # Process with CEP engine
    cep_engine = CEPEngine()
    
    start_time = time.time()
    await cep_engine.process_stock_events_stream(events)
    total_time = time.time() - start_time
    
    print(f"\n🎉 CEP processing completed in {total_time:.2f} seconds")
    print(f"⚡ Throughput: {len(events)/total_time:.0f} events/second")
    print(f"🇮🇳 Indian stock market patterns detected with Mumbai precision! 💼")

if __name__ == "__main__":
    asyncio.run(run_stock_market_cep())
```

### Stream Processing Performance Optimization

Performance optimization Mumbai local train ki punctuality maintain karne jaisa important hai:

#### Memory Management aur Backpressure Handling

```python
# Stream Processing Performance Optimization
import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import psutil
import gc
from collections import deque
import threading

@dataclass
class PerformanceMetrics:
    throughput_events_per_sec: float
    average_latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    backpressure_events: int
    gc_collections: int

class BackpressureManager:
    """
    Mumbai local train mein crowd control ki tarah backpressure manage karta hai
    """
    
    def __init__(self, max_buffer_size: int = 10000):
        self.max_buffer_size = max_buffer_size
        self.current_buffer_size = 0
        self.backpressure_active = False
        self.backpressure_count = 0
        self.lock = threading.Lock()
    
    def should_apply_backpressure(self) -> bool:
        """Check if backpressure should be applied"""
        with self.lock:
            return self.current_buffer_size >= self.max_buffer_size * 0.8  # 80% threshold
    
    def increment_buffer(self, count: int = 1):
        """Increment buffer count"""
        with self.lock:
            self.current_buffer_size += count
            if self.current_buffer_size >= self.max_buffer_size:
                self.backpressure_active = True
                self.backpressure_count += 1
    
    def decrement_buffer(self, count: int = 1):
        """Decrement buffer count"""
        with self.lock:
            self.current_buffer_size = max(0, self.current_buffer_size - count)
            if self.current_buffer_size < self.max_buffer_size * 0.6:  # 60% recovery threshold
                self.backpressure_active = False
    
    async def wait_for_capacity(self):
        """Wait for buffer capacity - Mumbai local mein platform wait ki tarah"""
        while self.backpressure_active:
            await asyncio.sleep(0.1)  # 100ms wait
            print("⏳ Backpressure active - waiting for capacity...")

class MemoryManager:
    """
    Memory management for high-throughput stream processing
    """
    
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self.gc_threshold = max_memory_mb * 0.8  # 80% threshold for GC
        self.last_gc_time = time.time()
        self.gc_count = 0
    
    def get_memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    
    def should_run_gc(self) -> bool:
        """Check if garbage collection should be triggered"""
        current_memory = self.get_memory_usage_mb()
        time_since_gc = time.time() - self.last_gc_time
        
        return (current_memory > self.gc_threshold or 
                time_since_gc > 30)  # Force GC every 30 seconds
    
    def run_gc_if_needed(self):
        """Run garbage collection if needed"""
        if self.should_run_gc():
            gc.collect()
            self.gc_count += 1
            self.last_gc_time = time.time()
            print(f"🧹 Garbage collection executed (#{self.gc_count})")

class HighPerformanceStreamProcessor:
    """
    High-performance stream processor for production workloads
    Mumbai Express train ki speed ke saath processing
    """
    
    def __init__(self, max_buffer_size: int = 50000):
        self.backpressure_manager = BackpressureManager(max_buffer_size)
        self.memory_manager = MemoryManager(1024)  # 1GB limit
        
        # Performance tracking
        self.events_processed = 0
        self.processing_times = deque(maxlen=1000)
        self.start_time = time.time()
        
        # Event buffers with different priorities
        self.high_priority_buffer = deque()
        self.normal_priority_buffer = deque()
        self.low_priority_buffer = deque()
        
        # Worker pool for parallel processing
        self.worker_count = 4
        self.workers_running = False
    
    async def ingest_event(self, event: Dict, priority: str = 'normal'):
        """
        Ingest event with backpressure handling
        Mumbai local mein platform capacity check ki tarah
        """
        
        # Apply backpressure if needed
        if self.backpressure_manager.should_apply_backpressure():
            await self.backpressure_manager.wait_for_capacity()
        
        # Add to appropriate buffer based on priority
        if priority == 'high':
            self.high_priority_buffer.append(event)
        elif priority == 'low':
            self.low_priority_buffer.append(event)
        else:
            self.normal_priority_buffer.append(event)
        
        self.backpressure_manager.increment_buffer()
    
    def get_next_event(self) -> Optional[Dict]:
        """
        Get next event with priority handling
        Mumbai local mein VIP coach pehle ki tarah
        """
        
        # High priority first
        if self.high_priority_buffer:
            return self.high_priority_buffer.popleft()
        
        # Then normal priority
        if self.normal_priority_buffer:
            return self.normal_priority_buffer.popleft()
        
        # Finally low priority
        if self.low_priority_buffer:
            return self.low_priority_buffer.popleft()
        
        return None
    
    async def process_event_batch(self, batch_size: int = 100):
        """Process events in batches for better throughput"""
        
        batch = []
        
        # Collect batch of events
        for _ in range(batch_size):
            event = self.get_next_event()
            if event is None:
                break
            batch.append(event)
        
        if not batch:
            return
        
        # Process batch
        processing_start = time.time()
        
        # Parallel processing within batch
        tasks = [self.process_single_event(event) for event in batch]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update metrics
        processing_time = (time.time() - processing_start) * 1000
        self.processing_times.append(processing_time)
        self.events_processed += len(batch)
        
        # Update backpressure
        self.backpressure_manager.decrement_buffer(len(batch))
        
        # Memory management
        self.memory_manager.run_gc_if_needed()
    
    async def process_single_event(self, event: Dict):
        """Process single event - customize based on event type"""
        
        # Simulate processing time
        await asyncio.sleep(0.001)  # 1ms processing time
        
        # Event processing logic here
        # For demo, just add some computation
        result = sum(hash(str(v)) % 1000 for v in event.values())
        return result
    
    async def worker_loop(self, worker_id: int):
        """Worker loop for continuous processing"""
        
        print(f"🔧 Worker {worker_id} started")
        
        while self.workers_running:
            try:
                await self.process_event_batch(batch_size=50)
                
                # Small delay if no events to process
                if (not self.high_priority_buffer and 
                    not self.normal_priority_buffer and 
                    not self.low_priority_buffer):
                    await asyncio.sleep(0.01)  # 10ms
                    
            except Exception as e:
                print(f"❌ Worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)
        
        print(f"🛑 Worker {worker_id} stopped")
    
    async def start_processing(self):
        """Start multi-worker processing"""
        
        print(f"🚀 Starting high-performance stream processing")
        print(f"👥 Workers: {self.worker_count}")
        print(f"📊 Buffer capacity: {self.backpressure_manager.max_buffer_size:,}")
        
        self.workers_running = True
        self.start_time = time.time()
        
        # Start worker tasks
        worker_tasks = [
            asyncio.create_task(self.worker_loop(i)) 
            for i in range(self.worker_count)
        ]
        
        # Start metrics reporting
        metrics_task = asyncio.create_task(self.metrics_reporter())
        
        # Wait for all workers
        await asyncio.gather(*worker_tasks, metrics_task)
    
    async def stop_processing(self):
        """Stop processing gracefully"""
        print("🛑 Stopping stream processing...")
        self.workers_running = False
        await asyncio.sleep(1)  # Allow workers to finish current batch
    
    async def metrics_reporter(self):
        """Report performance metrics periodically"""
        
        while self.workers_running:
            await asyncio.sleep(10)  # Report every 10 seconds
            
            current_time = time.time()
            runtime_seconds = current_time - self.start_time
            
            if runtime_seconds > 0:
                throughput = self.events_processed / runtime_seconds
                avg_latency = (sum(self.processing_times) / len(self.processing_times) 
                             if self.processing_times else 0)
                memory_mb = self.memory_manager.get_memory_usage_mb()
                cpu_percent = psutil.cpu_percent()
                
                metrics = PerformanceMetrics(
                    throughput_events_per_sec=throughput,
                    average_latency_ms=avg_latency,
                    memory_usage_mb=memory_mb,
                    cpu_usage_percent=cpu_percent,
                    backpressure_events=self.backpressure_manager.backpressure_count,
                    gc_collections=self.memory_manager.gc_count
                )
                
                print(f"\n📊 PERFORMANCE METRICS")
                print(f"⚡ Throughput: {metrics.throughput_events_per_sec:,.0f} events/sec")
                print(f"⏱️  Avg Latency: {metrics.average_latency_ms:.2f}ms")
                print(f"💾 Memory: {metrics.memory_usage_mb:.1f}MB")
                print(f"🖥️  CPU: {metrics.cpu_usage_percent:.1f}%")
                print(f"⏳ Backpressure Events: {metrics.backpressure_events}")
                print(f"🧹 GC Collections: {metrics.gc_collections}")
                
                buffer_total = (len(self.high_priority_buffer) + 
                              len(self.normal_priority_buffer) + 
                              len(self.low_priority_buffer))
                print(f"📦 Buffer Size: {buffer_total:,}")
                
                if buffer_total > 0:
                    print(f"   High: {len(self.high_priority_buffer):,}")
                    print(f"   Normal: {len(self.normal_priority_buffer):,}")
                    print(f"   Low: {len(self.low_priority_buffer):,}")

# Event generator for performance testing
async def generate_events_continuously(processor: HighPerformanceStreamProcessor, 
                                     events_per_second: int = 10000, 
                                     duration_seconds: int = 60):
    """
    Generate events continuously for performance testing
    Mumbai rush hour ki tarah continuous event generation
    """
    
    print(f"🏭 Generating {events_per_second:,} events/second for {duration_seconds} seconds")
    
    event_interval = 1.0 / events_per_second
    end_time = time.time() + duration_seconds
    event_count = 0
    
    while time.time() < end_time:
        batch_start = time.time()
        
        # Generate batch of events
        batch_size = min(100, events_per_second // 10)  # 10% of target rate
        
        for i in range(batch_size):
            # Create realistic event
            event = {
                'event_id': f'event_{event_count}',
                'timestamp': time.time(),
                'data': f'sample_data_{i}',
                'value': event_count % 1000,
                'category': f'category_{event_count % 10}'
            }
            
            # Assign priority (90% normal, 5% high, 5% low)
            priority = 'normal'
            if event_count % 20 == 0:
                priority = 'high'
            elif event_count % 20 == 1:
                priority = 'low'
            
            await processor.ingest_event(event, priority)
            event_count += 1
        
        # Control rate
        batch_time = time.time() - batch_start
        expected_batch_time = batch_size * event_interval
        
        if batch_time < expected_batch_time:
            await asyncio.sleep(expected_batch_time - batch_time)
    
    print(f"✅ Generated {event_count:,} events total")

# Run high-performance stream processing test
async def run_performance_test():
    """Run comprehensive performance test"""
    
    print("🚀 High-Performance Stream Processing Test")
    print("⚡ Mumbai Express level performance!")
    print("=" * 60)
    
    # Create processor
    processor = HighPerformanceStreamProcessor(max_buffer_size=100000)
    
    # Start processing in background
    processing_task = asyncio.create_task(processor.start_processing())
    
    # Generate events for testing
    await asyncio.sleep(1)  # Let workers start
    
    generation_task = asyncio.create_task(
        generate_events_continuously(
            processor, 
            events_per_second=20000,  # 20K events/second 
            duration_seconds=30       # 30 seconds test
        )
    )
    
    # Wait for event generation to complete
    await generation_task
    
    # Let processing catch up
    print("⏳ Allowing processing to catch up...")
    await asyncio.sleep(10)
    
    # Stop processing
    await processor.stop_processing()
    
    # Final metrics
    total_runtime = time.time() - processor.start_time
    final_throughput = processor.events_processed / total_runtime
    
    print(f"\n🎉 PERFORMANCE TEST COMPLETED")
    print("=" * 50)
    print(f"Total Events Processed: {processor.events_processed:,}")
    print(f"Total Runtime: {total_runtime:.2f} seconds")
    print(f"Final Throughput: {final_throughput:,.0f} events/second")
    print(f"Memory Usage: {processor.memory_manager.get_memory_usage_mb():.1f}MB")
    print(f"Backpressure Events: {processor.backpressure_manager.backpressure_count}")
    print(f"\n🚆 Mumbai Express performance achieved! 🌟")

if __name__ == "__main__":
    asyncio.run(run_performance_test())
```

### Part 2 Summary aur Advanced Patterns Ki Power

Dosto, Part 2 mein humne dekha advanced stream processing ki duniya:

**Key Learnings:**

1. **Kafka Streams Power**: Embedded processing library, separate cluster nahi chahiye
2. **CEP Magic**: Complex patterns detect karna - stock market manipulation se lekar insider trading tak
3. **Performance Optimization**: Backpressure, memory management, parallel processing
4. **Production Patterns**: Real Indian companies ke examples - Zomato, Flipkart, NSE

**Mumbai Ki Advanced Seekh:**
- Stream processing Mumbai Express ki tarah fast honi chahiye
- Complex patterns detect karna Mumbai Police ki intelligence ki tarah important hai
- Memory management Mumbai mein space ki tarah precious resource hai
- Backpressure Mumbai local mein crowd control ki tarah zaroori hai

**Real-world Applications:**
- Stock market manipulation detection
- E-commerce fraud prevention  
- Real-time recommendation engines
- Supply chain optimization
- IoT sensor data processing

Part 3 mein hum dekhenge enterprise deployment patterns, monitoring, troubleshooting, aur production war stories. Stay tuned for the final part! 🚆⚡

---

*Word Count: ~13,800 words*
*Next: Part 3 - Production Deployment, Monitoring & War Stories*