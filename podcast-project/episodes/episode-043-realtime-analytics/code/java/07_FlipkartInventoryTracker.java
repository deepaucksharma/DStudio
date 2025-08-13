/**
 * Flipkart Real-time Inventory Analytics
 * Episode 43: Real-time Analytics at Scale
 * 
 * यह Java example Flipkart का real-time inventory tracking और analytics दिखाता है
 * Big Billion Day, product demand prediction, और supply chain optimization के लिए।
 * 
 * Production Stats:
 * - Flipkart: 150+ million products tracked
 * - Peak orders: 8+ million per day (BBD)
 * - Inventory updates: 100,000+ per minute
 * - Warehouse locations: 1500+ across India
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;

// Data Models
class Product {
    private final String productId;
    private final String name;
    private final String category;
    private final String brand;
    private final double price;
    private final String seller;
    private final Map<String, Object> attributes;
    
    public Product(String productId, String name, String category, String brand, 
                  double price, String seller, Map<String, Object> attributes) {
        this.productId = productId;
        this.name = name;
        this.category = category;
        this.brand = brand;
        this.price = price;
        this.seller = seller;
        this.attributes = attributes;
    }
    
    // Getters
    public String getProductId() { return productId; }
    public String getName() { return name; }
    public String getCategory() { return category; }
    public String getBrand() { return brand; }
    public double getPrice() { return price; }
    public String getSeller() { return seller; }
    public Map<String, Object> getAttributes() { return attributes; }
}

class InventoryItem {
    private final String warehouseId;
    private final String productId;
    private final AtomicInteger quantity;
    private final AtomicInteger reservedQuantity;
    private final LocalDateTime lastUpdated;
    private final String location;
    private final InventoryStatus status;
    
    public enum InventoryStatus {
        IN_STOCK, LOW_STOCK, OUT_OF_STOCK, BACKORDERED, DISCONTINUED
    }
    
    public InventoryItem(String warehouseId, String productId, int quantity, 
                        String location, InventoryStatus status) {
        this.warehouseId = warehouseId;
        this.productId = productId;
        this.quantity = new AtomicInteger(quantity);
        this.reservedQuantity = new AtomicInteger(0);
        this.lastUpdated = LocalDateTime.now();
        this.location = location;
        this.status = status;
    }
    
    public boolean reserveStock(int requestedQuantity) {
        int available = quantity.get() - reservedQuantity.get();
        if (available >= requestedQuantity) {
            reservedQuantity.addAndGet(requestedQuantity);
            return true;
        }
        return false;
    }
    
    public void confirmReservation(int confirmedQuantity) {
        quantity.addAndGet(-confirmedQuantity);
        reservedQuantity.addAndGet(-confirmedQuantity);
    }
    
    public void releaseReservation(int releasedQuantity) {
        reservedQuantity.addAndGet(-releasedQuantity);
    }
    
    public void addStock(int additionalStock) {
        quantity.addAndGet(additionalStock);
    }
    
    // Getters
    public String getWarehouseId() { return warehouseId; }
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity.get(); }
    public int getReservedQuantity() { return reservedQuantity.get(); }
    public int getAvailableQuantity() { return quantity.get() - reservedQuantity.get(); }
    public LocalDateTime getLastUpdated() { return lastUpdated; }
    public String getLocation() { return location; }
    public InventoryStatus getStatus() { return status; }
}

class OrderEvent {
    private final String orderId;
    private final String productId;
    private final int quantity;
    private final String customerId;
    private final String deliveryLocation;
    private final LocalDateTime orderTime;
    private final OrderEventType eventType;
    private final double orderValue;
    
    public enum OrderEventType {
        ORDER_PLACED, ORDER_CANCELLED, ORDER_SHIPPED, ORDER_DELIVERED, ORDER_RETURNED
    }
    
    public OrderEvent(String orderId, String productId, int quantity, String customerId,
                     String deliveryLocation, LocalDateTime orderTime, OrderEventType eventType,
                     double orderValue) {
        this.orderId = orderId;
        this.productId = productId;
        this.quantity = quantity;
        this.customerId = customerId;
        this.deliveryLocation = deliveryLocation;
        this.orderTime = orderTime;
        this.eventType = eventType;
        this.orderValue = orderValue;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public String getCustomerId() { return customerId; }
    public String getDeliveryLocation() { return deliveryLocation; }
    public LocalDateTime getOrderTime() { return orderTime; }
    public OrderEventType getEventType() { return eventType; }
    public double getOrderValue() { return orderValue; }
}

class DemandPredictionEngine {
    private final Map<String, List<OrderEvent>> productOrderHistory = new ConcurrentHashMap<>();
    private final Map<String, Double> productDemandScores = new ConcurrentHashMap<>();
    
    public void processOrderEvent(OrderEvent orderEvent) {
        String productId = orderEvent.getProductId();
        productOrderHistory.computeIfAbsent(productId, k -> new ArrayList<>()).add(orderEvent);
        
        // Keep only recent history (last 1000 orders per product)
        List<OrderEvent> history = productOrderHistory.get(productId);
        if (history.size() > 1000) {
            history.removeAll(history.subList(0, history.size() - 1000));
        }
        
        updateDemandScore(productId);
    }
    
    private void updateDemandScore(String productId) {
        List<OrderEvent> history = productOrderHistory.get(productId);
        if (history == null || history.isEmpty()) return;
        
        // Calculate demand score based on recent activity
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime oneDayAgo = now.minusDays(1);
        LocalDateTime oneWeekAgo = now.minusWeeks(1);
        
        // Recent orders (last 24 hours)
        long recentOrders = history.stream()
                .filter(order -> order.getOrderTime().isAfter(oneDayAgo))
                .filter(order -> order.getEventType() == OrderEvent.OrderEventType.ORDER_PLACED)
                .count();
        
        // Weekly orders
        long weeklyOrders = history.stream()
                .filter(order -> order.getOrderTime().isAfter(oneWeekAgo))
                .filter(order -> order.getEventType() == OrderEvent.OrderEventType.ORDER_PLACED)
                .count();
        
        // Cancellation rate
        long cancellations = history.stream()
                .filter(order -> order.getOrderTime().isAfter(oneWeekAgo))
                .filter(order -> order.getEventType() == OrderEvent.OrderEventType.ORDER_CANCELLED)
                .count();
        
        double cancellationRate = weeklyOrders > 0 ? (double) cancellations / weeklyOrders : 0;
        
        // Demand score calculation
        double baseScore = recentOrders * 10; // Recent activity weight
        double trendScore = weeklyOrders * 2; // Overall trend weight
        double qualityScore = (1 - cancellationRate) * 5; // Quality adjustment
        
        double demandScore = baseScore + trendScore + qualityScore;
        productDemandScores.put(productId, demandScore);
    }
    
    public List<String> getHighDemandProducts(int limit) {
        return productDemandScores.entrySet().stream()
                .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
                .limit(limit)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }
    
    public double getDemandScore(String productId) {
        return productDemandScores.getOrDefault(productId, 0.0);
    }
    
    public Map<String, String> getRestockRecommendations() {
        Map<String, String> recommendations = new HashMap<>();
        
        productDemandScores.entrySet().stream()
                .filter(entry -> entry.getValue() > 50) // High demand threshold
                .forEach(entry -> {
                    String productId = entry.getKey();
                    double score = entry.getValue();
                    
                    if (score > 100) {
                        recommendations.put(productId, "URGENT_RESTOCK - Very high demand detected");
                    } else if (score > 75) {
                        recommendations.put(productId, "HIGH_PRIORITY - Increase stock levels");
                    } else {
                        recommendations.put(productId, "MONITOR - Watch for increasing demand");
                    }
                });
        
        return recommendations;
    }
}

class InventoryAnalytics {
    private final AtomicLong totalProducts = new AtomicLong(0);
    private final AtomicLong totalInventoryValue = new AtomicLong(0);
    private final AtomicLong lowStockItems = new AtomicLong(0);
    private final AtomicLong outOfStockItems = new AtomicLong(0);
    private final ConcurrentHashMap<String, AtomicLong> categoryInventory = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, AtomicLong> warehouseUtilization = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, AtomicLong> brandDistribution = new ConcurrentHashMap<>();
    
    public void updateInventoryMetrics(Product product, InventoryItem inventoryItem) {
        totalProducts.incrementAndGet();
        
        // Calculate inventory value
        long productValue = Math.round(product.getPrice() * inventoryItem.getQuantity());
        totalInventoryValue.addAndGet(productValue);
        
        // Stock level analysis
        if (inventoryItem.getStatus() == InventoryItem.InventoryStatus.LOW_STOCK) {
            lowStockItems.incrementAndGet();
        } else if (inventoryItem.getStatus() == InventoryItem.InventoryStatus.OUT_OF_STOCK) {
            outOfStockItems.incrementAndGet();
        }
        
        // Category-wise inventory
        categoryInventory.computeIfAbsent(product.getCategory(), k -> new AtomicLong(0))
                .addAndGet(inventoryItem.getQuantity());
        
        // Warehouse utilization
        warehouseUtilization.computeIfAbsent(inventoryItem.getWarehouseId(), k -> new AtomicLong(0))
                .addAndGet(inventoryItem.getQuantity());
        
        // Brand distribution
        brandDistribution.computeIfAbsent(product.getBrand(), k -> new AtomicLong(0))
                .addAndGet(inventoryItem.getQuantity());
    }
    
    public Map<String, Object> getAnalyticsSnapshot() {
        Map<String, Object> analytics = new HashMap<>();
        analytics.put("totalProducts", totalProducts.get());
        analytics.put("totalInventoryValue", totalInventoryValue.get());
        analytics.put("lowStockItems", lowStockItems.get());
        analytics.put("outOfStockItems", outOfStockItems.get());
        analytics.put("stockHealthRate", calculateStockHealthRate());
        
        // Top categories
        List<Map.Entry<String, AtomicLong>> topCategories = categoryInventory.entrySet().stream()
                .sorted(Map.Entry.<String, AtomicLong>comparingByValue((a, b) -> Long.compare(b.get(), a.get())))
                .limit(5)
                .collect(Collectors.toList());
        analytics.put("topCategories", topCategories);
        
        // Warehouse utilization
        List<Map.Entry<String, AtomicLong>> warehouseStats = warehouseUtilization.entrySet().stream()
                .sorted(Map.Entry.<String, AtomicLong>comparingByValue((a, b) -> Long.compare(b.get(), a.get())))
                .limit(5)
                .collect(Collectors.toList());
        analytics.put("warehouseUtilization", warehouseStats);
        
        // Top brands
        List<Map.Entry<String, AtomicLong>> topBrands = brandDistribution.entrySet().stream()
                .sorted(Map.Entry.<String, AtomicLong>comparingByValue((a, b) -> Long.compare(b.get(), a.get())))
                .limit(5)
                .collect(Collectors.toList());
        analytics.put("topBrands", topBrands);
        
        return analytics;
    }
    
    private double calculateStockHealthRate() {
        long total = totalProducts.get();
        if (total == 0) return 100.0;
        
        long unhealthyStock = lowStockItems.get() + outOfStockItems.get();
        return ((double)(total - unhealthyStock) / total) * 100;
    }
}

public class FlipkartInventoryTracker {
    private final Map<String, Product> productCatalog = new ConcurrentHashMap<>();
    private final Map<String, InventoryItem> inventoryMap = new ConcurrentHashMap<>();
    private final DemandPredictionEngine demandEngine = new DemandPredictionEngine();
    private final InventoryAnalytics analytics = new InventoryAnalytics();
    private final ExecutorService processingPool = Executors.newFixedThreadPool(20);
    private final ScheduledExecutorService scheduledPool = Executors.newScheduledThreadPool(3);
    
    // Indian product categories popular on Flipkart
    private final String[] categories = {
        "Electronics", "Fashion", "Home & Kitchen", "Books", "Sports",
        "Beauty & Personal Care", "Toys", "Automotive", "Grocery", "Mobiles"
    };
    
    private final String[] brands = {
        "Samsung", "Apple", "Xiaomi", "OnePlus", "Realme", "Vivo", "Oppo",
        "Adidas", "Nike", "Puma", "Levi's", "H&M", "Zara",
        "LG", "Sony", "Panasonic", "Whirlpool", "Godrej"
    };
    
    private final String[] warehouses = {
        "BLR_001", "MUM_002", "DEL_003", "HYD_004", "CHN_005",
        "KOL_006", "PUN_007", "AHM_008", "JP_009", "LKO_010"
    };
    
    private final String[] locations = {
        "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai",
        "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
    };
    
    public void initializeInventory() {
        System.out.println("🏭 Initializing Flipkart inventory system...");
        System.out.println("📦 Loading products और warehouse data...\n");
        
        Random random = new Random();
        
        // Create products
        for (int i = 1; i <= 10000; i++) { // 10K products for demo
            String productId = "PROD_" + String.format("%06d", i);
            String category = categories[random.nextInt(categories.length)];
            String brand = brands[random.nextInt(brands.length)];
            String name = generateProductName(category, brand);
            double price = generateRealisticPrice(category);
            String seller = random.nextBoolean() ? "Flipkart" : "Seller_" + random.nextInt(1000);
            
            Map<String, Object> attributes = new HashMap<>();
            attributes.put("rating", 3.5 + random.nextDouble() * 1.5); // 3.5-5.0 rating
            attributes.put("reviews", random.nextInt(10000));
            attributes.put("weight", random.nextDouble() * 5); // 0-5 kg
            
            Product product = new Product(productId, name, category, brand, price, seller, attributes);
            productCatalog.put(productId, product);
            
            // Create inventory entries across warehouses
            for (String warehouse : warehouses) {
                String inventoryKey = warehouse + "_" + productId;
                int stockQuantity = random.nextInt(1000); // 0-1000 units
                
                InventoryItem.InventoryStatus status;
                if (stockQuantity == 0) {
                    status = InventoryItem.InventoryStatus.OUT_OF_STOCK;
                } else if (stockQuantity < 50) {
                    status = InventoryItem.InventoryStatus.LOW_STOCK;
                } else {
                    status = InventoryItem.InventoryStatus.IN_STOCK;
                }
                
                String location = locations[Arrays.asList(warehouses).indexOf(warehouse)];
                InventoryItem inventoryItem = new InventoryItem(warehouse, productId, stockQuantity, location, status);
                inventoryMap.put(inventoryKey, inventoryItem);
                
                // Update analytics
                analytics.updateInventoryMetrics(product, inventoryItem);
            }
        }
        
        System.out.printf("✅ Initialized %,d products across %d warehouses%n", 
                         productCatalog.size(), warehouses.length);
        System.out.printf("📊 Total inventory items: %,d%n", inventoryMap.size());
    }
    
    private String generateProductName(String category, String brand) {
        Map<String, String[]> categoryProducts = Map.of(
            "Electronics", new String[]{"LED TV", "Laptop", "Headphones", "Speaker", "Camera"},
            "Fashion", new String[]{"T-Shirt", "Jeans", "Dress", "Shoes", "Watch"},
            "Home & Kitchen", new String[]{"Mixer", "Pressure Cooker", "Bed Sheet", "Curtain", "Sofa"},
            "Mobiles", new String[]{"Smartphone", "Feature Phone", "Power Bank", "Phone Case", "Charger"},
            "Books", new String[]{"Novel", "Textbook", "Biography", "Self-Help", "Children's Book"}
        );
        
        String[] products = categoryProducts.getOrDefault(category, new String[]{"Product"});
        String baseProduct = products[new Random().nextInt(products.length)];
        
        return brand + " " + baseProduct + " " + (new Random().nextInt(10) + 1);
    }
    
    private double generateRealisticPrice(String category) {
        Random random = new Random();
        
        Map<String, Double[]> categoryPriceRanges = Map.of(
            "Electronics", new Double[]{5000.0, 50000.0},
            "Fashion", new Double[]{500.0, 5000.0}, 
            "Home & Kitchen", new Double[]{1000.0, 15000.0},
            "Mobiles", new Double[]{8000.0, 80000.0},
            "Books", new Double[]{200.0, 2000.0},
            "Beauty & Personal Care", new Double[]{300.0, 3000.0}
        );
        
        Double[] priceRange = categoryPriceRanges.getOrDefault(category, new Double[]{500.0, 5000.0});
        return priceRange[0] + (random.nextDouble() * (priceRange[1] - priceRange[0]));
    }
    
    public void startRealTimeTracking() {
        System.out.println("🚀 Starting Flipkart Real-time Inventory Tracking");
        System.out.println("📦 Processing orders, stock updates, और demand analysis...\n");
        
        // Start analytics dashboard
        scheduledPool.scheduleAtFixedRate(this::printInventoryDashboard, 15, 45, TimeUnit.SECONDS);
        
        // Start order simulation
        scheduledPool.scheduleAtFixedRate(this::simulateOrders, 0, 1, TimeUnit.SECONDS);
        
        // Start stock updates
        scheduledPool.scheduleAtFixedRate(this::simulateStockUpdates, 5, 10, TimeUnit.SECONDS);
    }
    
    private void simulateOrders() {
        Random random = new Random();
        
        // Simulate BBD-like traffic with varying intensity
        int ordersThisSecond = random.nextInt(100) + 20; // 20-120 orders per second
        
        for (int i = 0; i < ordersThisSecond; i++) {
            processingPool.submit(() -> {
                OrderEvent order = generateRealisticOrder();
                processOrderEvent(order);
            });
        }
    }
    
    private OrderEvent generateRealisticOrder() {
        Random random = new Random();
        
        String orderId = "ORD_" + System.currentTimeMillis() + "_" + random.nextInt(10000);
        String productId = "PROD_" + String.format("%06d", random.nextInt(10000) + 1);
        int quantity = random.nextInt(5) + 1; // 1-5 items typically
        String customerId = "CUST_" + random.nextInt(1000000);
        String deliveryLocation = locations[random.nextInt(locations.length)];
        
        Product product = productCatalog.get(productId);
        double orderValue = product != null ? product.getPrice() * quantity : 1000.0;
        
        // Most orders are placements, some are cancellations/returns
        OrderEvent.OrderEventType eventType = random.nextDouble() < 0.85 ? 
                OrderEvent.OrderEventType.ORDER_PLACED : 
                random.nextDouble() < 0.7 ? OrderEvent.OrderEventType.ORDER_CANCELLED :
                OrderEvent.OrderEventType.ORDER_RETURNED;
        
        return new OrderEvent(orderId, productId, quantity, customerId, 
                             deliveryLocation, LocalDateTime.now(), eventType, orderValue);
    }
    
    private void processOrderEvent(OrderEvent orderEvent) {
        try {
            demandEngine.processOrderEvent(orderEvent);
            
            if (orderEvent.getEventType() == OrderEvent.OrderEventType.ORDER_PLACED) {
                // Try to fulfill the order
                boolean fulfilled = fulfillOrder(orderEvent);
                
                if (!fulfilled) {
                    System.out.printf("⚠️ Stock shortage: Product %s - Quantity %d unavailable%n",
                                    orderEvent.getProductId(), orderEvent.getQuantity());
                }
            }
            
            // Log high-value orders
            if (orderEvent.getOrderValue() > 50000) {
                System.out.printf("💎 High-value order: %s - ₹%.2f (%s)%n",
                                orderEvent.getOrderId(), orderEvent.getOrderValue(),
                                orderEvent.getEventType());
            }
            
        } catch (Exception e) {
            System.err.println("Error processing order: " + e.getMessage());
        }
    }
    
    private boolean fulfillOrder(OrderEvent orderEvent) {
        String productId = orderEvent.getProductId();
        int requestedQuantity = orderEvent.getQuantity();
        
        // Find warehouses with available stock
        List<String> availableWarehouses = new ArrayList<>();
        
        for (String warehouse : warehouses) {
            String inventoryKey = warehouse + "_" + productId;
            InventoryItem item = inventoryMap.get(inventoryKey);
            
            if (item != null && item.getAvailableQuantity() >= requestedQuantity) {
                availableWarehouses.add(warehouse);
            }
        }
        
        if (!availableWarehouses.isEmpty()) {
            // Choose nearest warehouse (simplified - just pick first available)
            String selectedWarehouse = availableWarehouses.get(0);
            String inventoryKey = selectedWarehouse + "_" + productId;
            InventoryItem item = inventoryMap.get(inventoryKey);
            
            if (item != null && item.reserveStock(requestedQuantity)) {
                // Simulate fulfillment delay
                processingPool.submit(() -> {
                    try {
                        Thread.sleep(100 + new Random().nextInt(400)); // 100-500ms delay
                        item.confirmReservation(requestedQuantity);
                    } catch (InterruptedException e) {
                        item.releaseReservation(requestedQuantity);
                        Thread.currentThread().interrupt();
                    }
                });
                return true;
            }
        }
        
        return false;
    }
    
    private void simulateStockUpdates() {
        Random random = new Random();
        
        // Simulate warehouse receiving new stock
        int stockUpdates = random.nextInt(20) + 5; // 5-25 updates per cycle
        
        for (int i = 0; i < stockUpdates; i++) {
            processingPool.submit(() -> {
                String warehouse = warehouses[random.nextInt(warehouses.length)];
                String productId = "PROD_" + String.format("%06d", random.nextInt(10000) + 1);
                String inventoryKey = warehouse + "_" + productId;
                
                InventoryItem item = inventoryMap.get(inventoryKey);
                if (item != null) {
                    int newStock = random.nextInt(500) + 50; // 50-550 new units
                    item.addStock(newStock);
                    
                    System.out.printf("📦 Stock received: %s - %d units added to %s%n",
                                    productId, newStock, warehouse);
                }
            });
        }
    }
    
    private void printInventoryDashboard() {
        Map<String, Object> analyticsSnapshot = analytics.getAnalyticsSnapshot();
        List<String> highDemandProducts = demandEngine.getHighDemandProducts(5);
        Map<String, String> restockRecommendations = demandEngine.getRestockRecommendations();
        
        System.out.println("\n" + "=".repeat(80));
        System.out.println("📦 FLIPKART REAL-TIME INVENTORY ANALYTICS DASHBOARD 📦");
        System.out.println("=".repeat(80));
        
        System.out.printf("📊 Total Products: %,d%n", (Long) analyticsSnapshot.get("totalProducts"));
        System.out.printf("💰 Total Inventory Value: ₹%,d%n", (Long) analyticsSnapshot.get("totalInventoryValue"));
        System.out.printf("⚠️ Low Stock Items: %,d%n", (Long) analyticsSnapshot.get("lowStockItems"));
        System.out.printf("❌ Out of Stock Items: %,d%n", (Long) analyticsSnapshot.get("outOfStockItems"));
        System.out.printf("💚 Stock Health Rate: %.2f%%%n", (Double) analyticsSnapshot.get("stockHealthRate"));
        
        // Top categories
        System.out.println("\n🏷️ Top Categories by Inventory:");
        List<Map.Entry<String, AtomicLong>> topCategories = 
            (List<Map.Entry<String, AtomicLong>>) analyticsSnapshot.get("topCategories");
        for (int i = 0; i < Math.min(5, topCategories.size()); i++) {
            Map.Entry<String, AtomicLong> entry = topCategories.get(i);
            System.out.printf("  %d. %s: %,d units%n", i + 1, entry.getKey(), entry.getValue().get());
        }
        
        // Warehouse utilization
        System.out.println("\n🏭 Top Warehouses by Inventory:");
        List<Map.Entry<String, AtomicLong>> warehouseStats = 
            (List<Map.Entry<String, AtomicLong>>) analyticsSnapshot.get("warehouseUtilization");
        for (int i = 0; i < Math.min(5, warehouseStats.size()); i++) {
            Map.Entry<String, AtomicLong> entry = warehouseStats.get(i);
            int warehouseIndex = Arrays.asList(warehouses).indexOf(entry.getKey());
            String location = warehouseIndex >= 0 ? locations[warehouseIndex] : "Unknown";
            System.out.printf("  %d. %s (%s): %,d units%n", i + 1, entry.getKey(), location, entry.getValue().get());
        }
        
        // High demand products
        System.out.println("\n🔥 High Demand Products:");
        for (int i = 0; i < Math.min(5, highDemandProducts.size()); i++) {
            String productId = highDemandProducts.get(i);
            Product product = productCatalog.get(productId);
            double demandScore = demandEngine.getDemandScore(productId);
            
            if (product != null) {
                System.out.printf("  %d. %s (%s) - Score: %.1f%n", 
                                i + 1, product.getName(), product.getCategory(), demandScore);
            }
        }
        
        // Restock recommendations
        System.out.println("\n🚛 Restock Recommendations:");
        if (restockRecommendations.isEmpty()) {
            System.out.println("  ✅ No urgent restocking needed");
        } else {
            restockRecommendations.entrySet().stream()
                    .limit(5)
                    .forEach(entry -> {
                        Product product = productCatalog.get(entry.getKey());
                        if (product != null) {
                            System.out.printf("  🚨 %s: %s%n", product.getName(), entry.getValue());
                        }
                    });
        }
        
        System.out.println("\n🕐 Last Updated: " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
        System.out.println("=".repeat(80));
    }
    
    public static void main(String[] args) {
        FlipkartInventoryTracker tracker = new FlipkartInventoryTracker();
        
        System.out.println("🛒 Flipkart Real-time Inventory Analytics - Production Simulation");
        System.out.println("📦 Tracking inventory across Indian warehouses...");
        System.out.println("🔍 Real-time demand prediction और stock optimization active...\n");
        
        // Initialize inventory
        tracker.initializeInventory();
        
        // Start real-time tracking
        tracker.startRealTimeTracking();
        
        // Keep running for demo
        try {
            // Run for 5 minutes in demo mode
            Thread.sleep(300000);
            System.out.println("\n🏁 Demo completed! Production system tracks millions of products 24/7");
        } catch (InterruptedException e) {
            System.out.println("🛑 Application stopped");
        }
        
        // Cleanup
        tracker.processingPool.shutdown();
        tracker.scheduledPool.shutdown();
    }
}\n";