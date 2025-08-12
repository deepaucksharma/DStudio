/*
 * Consistency Models Demo - Episode 4
 * विभिन्न Consistency Models का Java implementation
 * 
 * यह class दिखाती है कि कैसे अलग-अलग applications के लिए
 * अलग consistency requirements होती हैं।
 * 
 * Indian Context Examples:
 * - Flipkart Product Inventory (Strong Consistency)
 * - Zomato Order Tracking (Eventual Consistency)  
 * - Ola Ride Matching (Causal Consistency)
 */

package com.indiantech.cap.consistency;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * विभिन्न Consistency Models का demonstration
 * Real Indian tech companies के use cases के साथ
 */
public class ConsistencyModelsDemo {
    
    private static final String ANSI_RESET = "\u001B[0m";
    private static final String ANSI_GREEN = "\u001B[32m";
    private static final String ANSI_RED = "\u001B[31m";
    private static final String ANSI_YELLOW = "\u001B[33m";
    private static final String ANSI_BLUE = "\u001B[34m";
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🇮🇳 Consistency Models Demo - Indian Tech Context");
        System.out.println("=".repeat(60));
        
        // Scenario 1: Flipkart Inventory Management (Strong Consistency)
        demonstrateStrongConsistency();
        
        Thread.sleep(2000);
        
        // Scenario 2: Zomato Order Updates (Eventual Consistency)
        demonstrateEventualConsistency();
        
        Thread.sleep(2000);
        
        // Scenario 3: Ola Ride Matching (Causal Consistency)
        demonstrateCausalConsistency();
        
        Thread.sleep(2000);
        
        // Scenario 4: IRCTC Booking Race Condition
        demonstrateRaceConditions();
    }
    
    /**
     * Strong Consistency Example - Flipkart Product Inventory
     * कभी भी out-of-stock products sold नहीं होना चाहिए
     */
    private static void demonstrateStrongConsistency() throws InterruptedException {
        System.out.println(ANSI_BLUE + "\n🛒 SCENARIO 1: Flipkart Inventory - Strong Consistency" + ANSI_RESET);
        System.out.println("Requirement: No overselling of products");
        
        FlipkartInventoryManager inventory = new FlipkartInventoryManager();
        
        // Add some popular products
        inventory.addProduct("iphone_15_pro", "iPhone 15 Pro", new BigDecimal("79900"), 5);
        inventory.addProduct("samsung_s24", "Samsung Galaxy S24", new BigDecimal("72900"), 3);
        
        System.out.println("📦 Initial Inventory:");
        inventory.displayInventory();
        
        // Simulate concurrent purchases during sale (Big Billion Day)
        System.out.println("\n🔥 Big Billion Day Sale - Concurrent Purchase Attempts:");
        
        CountDownLatch latch = new CountDownLatch(1);
        List<CompletableFuture<Boolean>> purchaseFutures = new ArrayList<>();
        
        // Multiple users trying to buy iPhone (only 5 in stock)
        String[] users = {"rahul_mumbai", "priya_delhi", "amit_bangalore", "sneha_pune", "rajesh_chennai", "kavya_hyderabad"};
        
        for (String user : users) {
            CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                try {
                    latch.await(); // Wait for all threads to be ready
                    boolean success = inventory.purchaseProduct("iphone_15_pro", user);
                    System.out.println(String.format("%s Purchase by %s: %s", 
                        success ? ANSI_GREEN + "✅" : ANSI_RED + "❌",
                        user, 
                        success ? "SUCCESS" : "OUT OF STOCK" + ANSI_RESET));
                    return success;
                } catch (InterruptedException e) {
                    return false;
                }
            });
            purchaseFutures.add(future);
        }
        
        Thread.sleep(100); // Let all threads start
        latch.countDown(); // Release all threads simultaneously
        
        // Wait for all purchases to complete
        CompletableFuture.allOf(purchaseFutures.toArray(new CompletableFuture[0])).join();
        
        long successfulPurchases = purchaseFutures.stream()
            .mapToLong(f -> f.join() ? 1 : 0)
            .sum();
        
        System.out.println(String.format("\n📊 Results: %d/%d purchases successful", successfulPurchases, users.length));
        inventory.displayInventory();
        
        System.out.println(ANSI_GREEN + "✅ Strong Consistency Maintained: No overselling occurred!" + ANSI_RESET);
    }
    
    /**
     * Eventual Consistency Example - Zomato Order Tracking
     * Order status updates can be slightly delayed across different services
     */
    private static void demonstrateEventualConsistency() throws InterruptedException {
        System.out.println(ANSI_YELLOW + "\n🍔 SCENARIO 2: Zomato Order Tracking - Eventual Consistency" + ANSI_RESET);
        System.out.println("Requirement: Fast order placement, eventual status consistency");
        
        ZomatoOrderTracker orderTracker = new ZomatoOrderTracker();
        
        // Place order
        String orderId = orderTracker.placeOrder("user_mumbai_123", "Domino's Pizza", 
                                                Arrays.asList("Margherita Pizza", "Garlic Bread"), 
                                                new BigDecimal("650"));
        
        System.out.println(String.format("📱 Order placed: %s", orderId));
        
        // Show order status from different services (customer app, delivery app, restaurant)
        System.out.println("\n📋 Order Status from Different Services:");
        
        for (int i = 0; i < 8; i++) {
            System.out.println(String.format("\nTime: %s", LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss"))));
            
            // Check status from different services
            String customerStatus = orderTracker.getOrderStatusCustomerApp(orderId);
            String deliveryStatus = orderTracker.getOrderStatusDeliveryApp(orderId);
            String restaurantStatus = orderTracker.getOrderStatusRestaurant(orderId);
            
            System.out.println(String.format("👤 Customer App: %s", customerStatus));
            System.out.println(String.format("🏍️  Delivery App: %s", deliveryStatus));
            System.out.println(String.format("🏪 Restaurant App: %s", restaurantStatus));
            
            // Check if all services are consistent
            boolean isConsistent = customerStatus.equals(deliveryStatus) && deliveryStatus.equals(restaurantStatus);
            System.out.println(String.format("🎯 Consistency: %s", 
                isConsistent ? ANSI_GREEN + "CONSISTENT" + ANSI_RESET : ANSI_YELLOW + "EVENTUALLY CONSISTENT" + ANSI_RESET));
            
            // Simulate order progress
            if (i % 2 == 0) {
                orderTracker.updateOrderStatus(orderId);
            }
            
            Thread.sleep(1500);
        }
        
        System.out.println(ANSI_GREEN + "\n✅ Eventual Consistency: All services eventually synchronized!" + ANSI_RESET);
    }
    
    /**
     * Causal Consistency Example - Ola Ride Matching
     * Cause-effect relationship must be maintained in ride booking
     */
    private static void demonstrateCausalConsistency() throws InterruptedException {
        System.out.println(ANSI_BLUE + "\n🚗 SCENARIO 3: Ola Ride Matching - Causal Consistency" + ANSI_RESET);
        System.out.println("Requirement: Cause-effect order must be maintained");
        
        OlaRideMatchingSystem rideSystem = new OlaRideMatchingSystem();
        
        // Register drivers
        rideSystem.registerDriver("driver_001", "Suresh Kumar", "Santro", "MH01AB1234");
        rideSystem.registerDriver("driver_002", "Ramesh Singh", "Swift", "MH02CD5678");
        
        // Customer requests ride
        String rideRequestId = rideSystem.requestRide("customer_001", "Bandra West", "Andheri East", new BigDecimal("250"));
        System.out.println(String.format("📱 Ride requested: %s", rideRequestId));
        
        // Simulate causal relationships in ride booking
        System.out.println("\n🔄 Causal Event Sequence:");
        
        // Event 1: Driver accepts ride (cause)
        System.out.println("1️⃣ Driver accepts ride request...");
        boolean accepted = rideSystem.acceptRide(rideRequestId, "driver_001");
        System.out.println(String.format("   Result: %s", accepted ? "ACCEPTED" : "FAILED"));
        Thread.sleep(1000);
        
        // Event 2: Customer is notified (effect of Event 1)
        System.out.println("2️⃣ Customer notification (caused by driver acceptance)...");
        rideSystem.notifyCustomer(rideRequestId, "Driver assigned: Suresh Kumar");
        Thread.sleep(1000);
        
        // Event 3: Driver starts journey (cause)
        System.out.println("3️⃣ Driver starts journey...");
        rideSystem.startRide(rideRequestId);
        Thread.sleep(1000);
        
        // Event 4: Live tracking enabled (effect of Event 3)
        System.out.println("4️⃣ Live tracking enabled (caused by ride start)...");
        rideSystem.enableLiveTracking(rideRequestId);
        Thread.sleep(1000);
        
        // Event 5: Ride completed (cause)
        System.out.println("5️⃣ Ride completed...");
        rideSystem.completeRide(rideRequestId);
        Thread.sleep(1000);
        
        // Event 6: Payment processed (effect of Event 5)
        System.out.println("6️⃣ Payment processed (caused by ride completion)...");
        rideSystem.processPayment(rideRequestId, new BigDecimal("250"));
        
        // Verify causal consistency
        boolean causalConsistency = rideSystem.verifyCausalConsistency(rideRequestId);
        System.out.println(String.format("\n🎯 Causal Consistency: %s", 
            causalConsistency ? ANSI_GREEN + "MAINTAINED" + ANSI_RESET : ANSI_RED + "VIOLATED" + ANSI_RESET));
    }
    
    /**
     * Race Condition Demo - IRCTC Booking System
     * Shows what happens without proper consistency controls
     */
    private static void demonstrateRaceConditions() throws InterruptedException {
        System.out.println(ANSI_RED + "\n🚆 SCENARIO 4: IRCTC Race Conditions - Consistency Violations" + ANSI_RESET);
        System.out.println("Demonstration: What happens WITHOUT proper consistency controls");
        
        IRCTCBookingSystem bookingSystem = new IRCTCBookingSystem();
        
        // Add train with limited seats
        bookingSystem.addTrain("12345", "Mumbai-Delhi Rajdhani", 2); // Only 2 seats available
        
        System.out.println("🚆 Train: Mumbai-Delhi Rajdhani");
        System.out.println("💺 Available Seats: 2");
        System.out.println("\n⚠️ WARNING: Simulating race condition without proper locking!");
        
        // Multiple users trying to book simultaneously (Tatkal booking scenario)
        CountDownLatch latch = new CountDownLatch(1);
        List<CompletableFuture<String>> bookingFutures = new ArrayList<>();
        
        String[] passengers = {"Raj_Mumbai", "Priya_Delhi", "Amit_Pune", "Sneha_Surat"};
        
        for (String passenger : passengers) {
            CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
                try {
                    latch.await();
                    // Simulate race condition - no proper locking
                    String result = bookingSystem.bookSeatWithRaceCondition("12345", passenger);
                    System.out.println(String.format("%s Booking by %s: %s", 
                        result.startsWith("SUCCESS") ? ANSI_GREEN + "✅" : ANSI_RED + "❌",
                        passenger, 
                        result + ANSI_RESET));
                    return result;
                } catch (InterruptedException e) {
                    return "ERROR";
                }
            });
            bookingFutures.add(future);
        }
        
        Thread.sleep(100);
        latch.countDown(); // Start all bookings simultaneously
        
        // Wait for all bookings
        CompletableFuture.allOf(bookingFutures.toArray(new CompletableFuture[0])).join();
        
        // Check final state
        int finalSeats = bookingSystem.getAvailableSeats("12345");
        List<String> bookings = bookingSystem.getBookings("12345");
        
        System.out.println(String.format("\n📊 Final Results:"));
        System.out.println(String.format("💺 Remaining Seats: %d", finalSeats));
        System.out.println(String.format("🎫 Total Bookings: %d", bookings.size()));
        System.out.println(String.format("👥 Booked By: %s", String.join(", ", bookings)));
        
        if (bookings.size() > 2 || finalSeats < 0) {
            System.out.println(ANSI_RED + "💥 CONSISTENCY VIOLATION: Overselling occurred!" + ANSI_RESET);
            System.out.println(ANSI_RED + "   This is why strong consistency is needed for IRCTC!" + ANSI_RESET);
        } else {
            System.out.println(ANSI_GREEN + "✅ No overselling - consistency maintained by luck!" + ANSI_RESET);
        }
        
        // Show corrected version
        System.out.println(ANSI_BLUE + "\n🔒 Now with proper synchronization..." + ANSI_RESET);
        
        IRCTCBookingSystem correctSystem = new IRCTCBookingSystem();
        correctSystem.addTrain("54321", "Delhi-Mumbai Rajdhani", 2);
        
        CountDownLatch latch2 = new CountDownLatch(1);
        List<CompletableFuture<String>> safeFutures = new ArrayList<>();
        
        for (String passenger : passengers) {
            CompletableFuture<String> future = CompletableFuture.supplyAsync(() -> {
                try {
                    latch2.await();
                    String result = correctSystem.bookSeatSafely("54321", passenger);
                    System.out.println(String.format("%s Safe booking by %s: %s", 
                        result.startsWith("SUCCESS") ? ANSI_GREEN + "✅" : ANSI_YELLOW + "⚠️",
                        passenger, 
                        result + ANSI_RESET));
                    return result;
                } catch (InterruptedException e) {
                    return "ERROR";
                }
            });
            safeFutures.add(future);
        }
        
        Thread.sleep(100);
        latch2.countDown();
        
        CompletableFuture.allOf(safeFutures.toArray(new CompletableFuture[0])).join();
        
        int safeFinalSeats = correctSystem.getAvailableSeats("54321");
        List<String> safeBookings = correctSystem.getBookings("54321");
        
        System.out.println(String.format("\n📊 Safe Results:"));
        System.out.println(String.format("💺 Remaining Seats: %d", safeFinalSeats));
        System.out.println(String.format("🎫 Total Bookings: %d", safeBookings.size()));
        System.out.println(ANSI_GREEN + "✅ Strong consistency maintained - no overselling!" + ANSI_RESET);
        
        System.out.println(ANSI_BLUE + "\n💡 Key Learnings:" + ANSI_RESET);
        System.out.println("1. Race conditions can cause data inconsistency");
        System.out.println("2. Strong consistency requires proper synchronization");
        System.out.println("3. IRCTC needs strong consistency to prevent double booking");
        System.out.println("4. Performance vs Consistency trade-off is real");
    }
}

/**
 * Flipkart Inventory Management with Strong Consistency
 * कभी भी stock से ज्यादा selling नहीं होना चाहिए
 */
class FlipkartInventoryManager {
    private final Map<String, ProductInfo> inventory = new ConcurrentHashMap<>();
    private final Object lockObject = new Object();
    
    static class ProductInfo {
        String productId;
        String name;
        BigDecimal price;
        AtomicInteger stock;
        List<String> purchaseHistory;
        
        ProductInfo(String productId, String name, BigDecimal price, int initialStock) {
            this.productId = productId;
            this.name = name;
            this.price = price;
            this.stock = new AtomicInteger(initialStock);
            this.purchaseHistory = Collections.synchronizedList(new ArrayList<>());
        }
    }
    
    public void addProduct(String productId, String name, BigDecimal price, int stock) {
        inventory.put(productId, new ProductInfo(productId, name, price, stock));
        System.out.println(String.format("📦 Added: %s (₹%s) - %d units", name, price, stock));
    }
    
    public boolean purchaseProduct(String productId, String customerId) {
        synchronized (lockObject) { // Strong consistency through synchronization
            ProductInfo product = inventory.get(productId);
            if (product == null) return false;
            
            // Simulate some processing time (network latency, DB operations)
            try {
                Thread.sleep(50);
            } catch (InterruptedException e) {
                return false;
            }
            
            if (product.stock.get() > 0) {
                product.stock.decrementAndGet();
                product.purchaseHistory.add(String.format("%s - %s", customerId, LocalDateTime.now()));
                return true;
            }
            return false;
        }
    }
    
    public void displayInventory() {
        for (ProductInfo product : inventory.values()) {
            System.out.println(String.format("  📱 %s: ₹%s (Stock: %d)", 
                product.name, product.price, product.stock.get()));
        }
    }
}

/**
 * Zomato Order Tracking with Eventual Consistency
 * Different services can have slightly different order status
 */
class ZomatoOrderTracker {
    private final Map<String, OrderInfo> orders = new ConcurrentHashMap<>();
    private final Random random = new Random();
    
    static class OrderInfo {
        String orderId;
        String customerId;
        String restaurant;
        List<String> items;
        BigDecimal amount;
        volatile String actualStatus;
        Map<String, String> serviceStatuses; // Different services may have different status
        LocalDateTime createdAt;
        
        OrderInfo(String orderId, String customerId, String restaurant, List<String> items, BigDecimal amount) {
            this.orderId = orderId;
            this.customerId = customerId;
            this.restaurant = restaurant;
            this.items = new ArrayList<>(items);
            this.amount = amount;
            this.actualStatus = "PLACED";
            this.serviceStatuses = new ConcurrentHashMap<>();
            this.serviceStatuses.put("customer", "PLACED");
            this.serviceStatuses.put("delivery", "PLACED");  
            this.serviceStatuses.put("restaurant", "PLACED");
            this.createdAt = LocalDateTime.now();
        }
    }
    
    public String placeOrder(String customerId, String restaurant, List<String> items, BigDecimal amount) {
        String orderId = "ZOM" + System.currentTimeMillis();
        orders.put(orderId, new OrderInfo(orderId, customerId, restaurant, items, amount));
        return orderId;
    }
    
    public void updateOrderStatus(String orderId) {
        OrderInfo order = orders.get(orderId);
        if (order == null) return;
        
        // Progress order status
        switch (order.actualStatus) {
            case "PLACED" -> order.actualStatus = "CONFIRMED";
            case "CONFIRMED" -> order.actualStatus = "PREPARING";
            case "PREPARING" -> order.actualStatus = "OUT_FOR_DELIVERY";
            case "OUT_FOR_DELIVERY" -> order.actualStatus = "DELIVERED";
        }
        
        // Simulate eventual consistency - different services update at different times
        // Some services might be slower to update
        updateServiceStatusEventually(orderId, "customer", order.actualStatus);
        updateServiceStatusEventually(orderId, "delivery", order.actualStatus);
        updateServiceStatusEventually(orderId, "restaurant", order.actualStatus);
    }
    
    private void updateServiceStatusEventually(String orderId, String service, String status) {
        // Simulate network delay and eventual consistency
        new Thread(() -> {
            try {
                Thread.sleep(random.nextInt(2000)); // 0-2 second delay
                OrderInfo order = orders.get(orderId);
                if (order != null) {
                    order.serviceStatuses.put(service, status);
                }
            } catch (InterruptedException e) {
                // Handle interruption
            }
        }).start();
    }
    
    public String getOrderStatusCustomerApp(String orderId) {
        OrderInfo order = orders.get(orderId);
        return order != null ? order.serviceStatuses.get("customer") : "NOT_FOUND";
    }
    
    public String getOrderStatusDeliveryApp(String orderId) {
        OrderInfo order = orders.get(orderId);
        return order != null ? order.serviceStatuses.get("delivery") : "NOT_FOUND";
    }
    
    public String getOrderStatusRestaurant(String orderId) {
        OrderInfo order = orders.get(orderId);
        return order != null ? order.serviceStatuses.get("restaurant") : "NOT_FOUND";
    }
}

/**
 * Ola Ride Matching System with Causal Consistency
 * Events must happen in correct cause-effect order
 */
class OlaRideMatchingSystem {
    private final Map<String, DriverInfo> drivers = new ConcurrentHashMap<>();
    private final Map<String, RideInfo> rides = new ConcurrentHashMap<>();
    private final Map<String, List<String>> causalChain = new ConcurrentHashMap<>();
    
    static class DriverInfo {
        String driverId;
        String name;
        String vehicle;
        String plateNumber;
        boolean available;
        
        DriverInfo(String driverId, String name, String vehicle, String plateNumber) {
            this.driverId = driverId;
            this.name = name;
            this.vehicle = vehicle;
            this.plateNumber = plateNumber;
            this.available = true;
        }
    }
    
    static class RideInfo {
        String rideId;
        String customerId;
        String pickup;
        String destination;
        BigDecimal fare;
        String status;
        String driverId;
        List<String> eventHistory;
        
        RideInfo(String rideId, String customerId, String pickup, String destination, BigDecimal fare) {
            this.rideId = rideId;
            this.customerId = customerId;
            this.pickup = pickup;
            this.destination = destination;
            this.fare = fare;
            this.status = "REQUESTED";
            this.eventHistory = Collections.synchronizedList(new ArrayList<>());
        }
    }
    
    public void registerDriver(String driverId, String name, String vehicle, String plateNumber) {
        drivers.put(driverId, new DriverInfo(driverId, name, vehicle, plateNumber));
    }
    
    public String requestRide(String customerId, String pickup, String destination, BigDecimal fare) {
        String rideId = "RIDE" + System.currentTimeMillis();
        RideInfo ride = new RideInfo(rideId, customerId, pickup, destination, fare);
        rides.put(rideId, ride);
        
        // Initialize causal chain
        causalChain.put(rideId, Collections.synchronizedList(new ArrayList<>()));
        addCausalEvent(rideId, "RIDE_REQUESTED");
        
        return rideId;
    }
    
    public boolean acceptRide(String rideId, String driverId) {
        RideInfo ride = rides.get(rideId);
        DriverInfo driver = drivers.get(driverId);
        
        if (ride == null || driver == null || !driver.available) {
            return false;
        }
        
        ride.driverId = driverId;
        ride.status = "ACCEPTED";
        driver.available = false;
        
        addCausalEvent(rideId, "RIDE_ACCEPTED");
        return true;
    }
    
    public void notifyCustomer(String rideId, String message) {
        RideInfo ride = rides.get(rideId);
        if (ride != null) {
            ride.eventHistory.add("CUSTOMER_NOTIFIED: " + message);
            addCausalEvent(rideId, "CUSTOMER_NOTIFIED");
        }
    }
    
    public void startRide(String rideId) {
        RideInfo ride = rides.get(rideId);
        if (ride != null && "ACCEPTED".equals(ride.status)) {
            ride.status = "IN_PROGRESS";
            addCausalEvent(rideId, "RIDE_STARTED");
        }
    }
    
    public void enableLiveTracking(String rideId) {
        RideInfo ride = rides.get(rideId);
        if (ride != null) {
            ride.eventHistory.add("LIVE_TRACKING_ENABLED");
            addCausalEvent(rideId, "LIVE_TRACKING_ENABLED");
        }
    }
    
    public void completeRide(String rideId) {
        RideInfo ride = rides.get(rideId);
        if (ride != null && "IN_PROGRESS".equals(ride.status)) {
            ride.status = "COMPLETED";
            addCausalEvent(rideId, "RIDE_COMPLETED");
        }
    }
    
    public void processPayment(String rideId, BigDecimal amount) {
        RideInfo ride = rides.get(rideId);
        if (ride != null && "COMPLETED".equals(ride.status)) {
            ride.eventHistory.add("PAYMENT_PROCESSED: ₹" + amount);
            addCausalEvent(rideId, "PAYMENT_PROCESSED");
            
            // Free up driver
            if (ride.driverId != null) {
                DriverInfo driver = drivers.get(ride.driverId);
                if (driver != null) {
                    driver.available = true;
                }
            }
        }
    }
    
    private void addCausalEvent(String rideId, String event) {
        List<String> chain = causalChain.get(rideId);
        if (chain != null) {
            chain.add(event + " @ " + LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss.SSS")));
        }
    }
    
    public boolean verifyCausalConsistency(String rideId) {
        List<String> chain = causalChain.get(rideId);
        if (chain == null) return false;
        
        // Define expected causal order
        String[] expectedOrder = {
            "RIDE_REQUESTED", "RIDE_ACCEPTED", "CUSTOMER_NOTIFIED",
            "RIDE_STARTED", "LIVE_TRACKING_ENABLED", "RIDE_COMPLETED", "PAYMENT_PROCESSED"
        };
        
        int expectedIndex = 0;
        for (String event : chain) {
            String eventType = event.split(" @ ")[0];
            if (expectedIndex < expectedOrder.length && eventType.equals(expectedOrder[expectedIndex])) {
                expectedIndex++;
            }
        }
        
        return expectedIndex == expectedOrder.length;
    }
}

/**
 * IRCTC Booking System demonstrating race conditions and their solutions
 */
class IRCTCBookingSystem {
    private final Map<String, TrainInfo> trains = new ConcurrentHashMap<>();
    
    static class TrainInfo {
        String trainId;
        String name;
        AtomicInteger availableSeats;
        List<String> bookings;
        
        TrainInfo(String trainId, String name, int seats) {
            this.trainId = trainId;
            this.name = name;
            this.availableSeats = new AtomicInteger(seats);
            this.bookings = Collections.synchronizedList(new ArrayList<>());
        }
    }
    
    public void addTrain(String trainId, String name, int seats) {
        trains.put(trainId, new TrainInfo(trainId, name, seats));
    }
    
    // Race condition version - UNSAFE
    public String bookSeatWithRaceCondition(String trainId, String passenger) {
        TrainInfo train = trains.get(trainId);
        if (train == null) return "TRAIN_NOT_FOUND";
        
        // Simulate checking availability (race condition window)
        try {
            Thread.sleep(10); // Simulate processing time
        } catch (InterruptedException e) {
            return "ERROR";
        }
        
        if (train.availableSeats.get() > 0) {
            // Another thread might reduce seats here!
            train.availableSeats.decrementAndGet();
            train.bookings.add(passenger);
            return "SUCCESS - Seat booked for " + passenger;
        }
        
        return "NO_SEATS_AVAILABLE";
    }
    
    // Safe version with proper synchronization
    public String bookSeatSafely(String trainId, String passenger) {
        TrainInfo train = trains.get(trainId);
        if (train == null) return "TRAIN_NOT_FOUND";
        
        // Atomic check and decrement
        int currentSeats;
        do {
            currentSeats = train.availableSeats.get();
            if (currentSeats <= 0) {
                return "NO_SEATS_AVAILABLE";
            }
        } while (!train.availableSeats.compareAndSet(currentSeats, currentSeats - 1));
        
        train.bookings.add(passenger);
        return "SUCCESS - Seat booked for " + passenger;
    }
    
    public int getAvailableSeats(String trainId) {
        TrainInfo train = trains.get(trainId);
        return train != null ? train.availableSeats.get() : -1;
    }
    
    public List<String> getBookings(String trainId) {
        TrainInfo train = trains.get(trainId);
        return train != null ? new ArrayList<>(train.bookings) : Collections.emptyList();
    }
}