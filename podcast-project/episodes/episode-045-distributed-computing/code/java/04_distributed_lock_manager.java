import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicBoolean;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Distributed Lock Manager Implementation
 * जैसे कि Zomato के order processing में coordination के लिए use होता है
 * 
 * यह example दिखाता है कि कैसे distributed lock manager work करती है
 * large-scale systems में। Indian companies जैसे Zomato, Swiggy इसे use करती हैं
 * order processing, inventory management, और resource coordination के लिए।
 * 
 * Production context: Zomato coordinates 2M+ daily orders across distributed services
 * Scale: Manages locks across hundreds of services and thousands of resources
 * Challenge: Preventing deadlocks while ensuring high availability and performance
 */

/**
 * Represents a distributed lock
 */
class DistributedLock {
    private final String lockId;
    private final String resourceId;
    private final String ownerNodeId;
    private final long acquiredTime;
    private final long leaseTime;
    private final AtomicInteger renewalCount;
    private volatile boolean isActive;
    
    public DistributedLock(String lockId, String resourceId, String ownerNodeId, long leaseTime) {
        this.lockId = lockId;
        this.resourceId = resourceId;
        this.ownerNodeId = ownerNodeId;
        this.acquiredTime = System.currentTimeMillis();
        this.leaseTime = leaseTime;
        this.renewalCount = new AtomicInteger(0);
        this.isActive = true;
    }
    
    public boolean isExpired() {
        return System.currentTimeMillis() > (acquiredTime + leaseTime);
    }
    
    public boolean renew(long additionalTime) {
        if (isActive && !isExpired()) {
            renewalCount.incrementAndGet();
            return true;
        }
        return false;
    }
    
    public void release() {
        isActive = false;
    }
    
    // Getters
    public String getLockId() { return lockId; }
    public String getResourceId() { return resourceId; }
    public String getOwnerNodeId() { return ownerNodeId; }
    public long getAcquiredTime() { return acquiredTime; }
    public long getLeaseTime() { return leaseTime; }
    public int getRenewalCount() { return renewalCount.get(); }
    public boolean isActive() { return isActive; }
    
    @Override
    public String toString() {
        return String.format("Lock{id=%s, resource=%s, owner=%s, active=%s, renewals=%d}",
                           lockId, resourceId, ownerNodeId, isActive, renewalCount.get());
    }
}

/**
 * Zomato order for demonstration
 */
class ZomatoOrder {
    public final String orderId;
    public final String customerId;
    public final String restaurantId;
    public final String deliveryPartnerId;
    public final List<String> items;
    public final double totalAmount;
    public final long orderTime;
    public volatile String status;
    
    public ZomatoOrder(String orderId, String customerId, String restaurantId, 
                      List<String> items, double totalAmount) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.restaurantId = restaurantId;
        this.deliveryPartnerId = null;
        this.items = new ArrayList<>(items);
        this.totalAmount = totalAmount;
        this.orderTime = System.currentTimeMillis();
        this.status = "PENDING";
    }
    
    @Override
    public String toString() {
        return String.format("Order{id=%s, customer=%s, restaurant=%s, amount=₹%.2f, status=%s}",
                           orderId, customerId, restaurantId, totalAmount, status);
    }
}

/**
 * Distributed Lock Manager using Raft-style consensus
 */
class ZomatoDistributedLockManager {
    private final String nodeId;
    private final String region;
    private final Map<String, DistributedLock> activeLocks;
    private final Map<String, Queue<LockRequest>> lockQueue;
    private final Map<String, ZomatoDistributedLockManager> clusterNodes;
    private final AtomicLong lockIdCounter;
    private final AtomicInteger locksAcquired;
    private final AtomicInteger locksReleased;
    private final AtomicInteger lockContentions;
    
    // Lock manager settings
    private final long defaultLeaseTime = 30000; // 30 seconds
    private final long maxWaitTime = 10000; // 10 seconds
    private final int maxRetries = 3;
    
    // Threading
    private final ExecutorService lockProcessingExecutor;
    private final ScheduledExecutorService maintenanceExecutor;
    private final AtomicBoolean isRunning;
    
    public ZomatoDistributedLockManager(String nodeId, String region) {
        this.nodeId = nodeId;
        this.region = region;
        this.activeLocks = new ConcurrentHashMap<>();
        this.lockQueue = new ConcurrentHashMap<>();
        this.clusterNodes = new ConcurrentHashMap<>();
        this.lockIdCounter = new AtomicLong(0);
        this.locksAcquired = new AtomicInteger(0);
        this.locksReleased = new AtomicInteger(0);
        this.lockContentions = new AtomicInteger(0);
        
        this.lockProcessingExecutor = Executors.newFixedThreadPool(10);
        this.maintenanceExecutor = Executors.newScheduledThreadPool(2);
        this.isRunning = new AtomicBoolean(false);
        
        System.out.printf("[%s] Zomato Distributed Lock Manager initialized in %s region%n", 
                         nodeId, region);
    }
    
    /**
     * Start the lock manager
     */
    public void start() {
        if (isRunning.compareAndSet(false, true)) {
            // Start lock expiration cleanup
            maintenanceExecutor.scheduleAtFixedRate(this::cleanupExpiredLocks, 5, 5, TimeUnit.SECONDS);
            
            // Start lock queue processing
            maintenanceExecutor.scheduleAtFixedRate(this::processLockQueues, 1, 1, TimeUnit.SECONDS);
            
            System.out.printf("[%s] Started distributed lock manager%n", nodeId);
        }
    }
    
    /**
     * Stop the lock manager
     */
    public void stop() {
        if (isRunning.compareAndSet(true, false)) {
            lockProcessingExecutor.shutdown();
            maintenanceExecutor.shutdown();
            
            try {
                if (!lockProcessingExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    lockProcessingExecutor.shutdownNow();
                }
                if (!maintenanceExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    maintenanceExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            System.out.printf("[%s] Stopped distributed lock manager%n", nodeId);
        }
    }
    
    /**
     * Add cluster node for coordination
     */
    public void addClusterNode(ZomatoDistributedLockManager node) {
        clusterNodes.put(node.nodeId, node);
        System.out.printf("[%s] Added cluster node: %s (%s)%n", nodeId, node.nodeId, node.region);
    }
    
    /**
     * Acquire a distributed lock
     */
    public CompletableFuture<DistributedLock> acquireLock(String resourceId) {
        return acquireLock(resourceId, defaultLeaseTime, maxWaitTime);
    }
    
    /**
     * Acquire a distributed lock with custom parameters
     */
    public CompletableFuture<DistributedLock> acquireLock(String resourceId, long leaseTime, long waitTime) {
        CompletableFuture<DistributedLock> future = new CompletableFuture<>();
        
        lockProcessingExecutor.submit(() -> {
            try {
                DistributedLock lock = tryAcquireLock(resourceId, leaseTime, waitTime);
                if (lock != null) {
                    future.complete(lock);
                } else {
                    future.completeExceptionally(new LockAcquisitionException(
                        "Failed to acquire lock for resource: " + resourceId));
                }
            } catch (Exception e) {
                future.completeExceptionally(e);
            }
        });
        
        return future;
    }
    
    /**
     * Try to acquire lock immediately or wait in queue
     */
    private DistributedLock tryAcquireLock(String resourceId, long leaseTime, long waitTime) {
        String lockId = generateLockId();
        
        // Check if resource is already locked
        DistributedLock existingLock = activeLocks.get(resourceId);
        if (existingLock != null && existingLock.isActive() && !existingLock.isExpired()) {
            // Resource is locked, add to queue if wait time > 0
            if (waitTime > 0) {
                return waitForLock(resourceId, lockId, leaseTime, waitTime);
            } else {
                lockContentions.incrementAndGet();
                return null;
            }
        }
        
        // Try to acquire lock across cluster
        if (tryAcquireFromCluster(resourceId, lockId, leaseTime)) {
            DistributedLock lock = new DistributedLock(lockId, resourceId, nodeId, leaseTime);
            activeLocks.put(resourceId, lock);
            locksAcquired.incrementAndGet();
            
            System.out.printf("[%s] Acquired lock %s for resource %s%n", nodeId, lockId, resourceId);
            return lock;
        }
        
        return null;
    }
    
    /**
     * Wait for lock to become available
     */
    private DistributedLock waitForLock(String resourceId, String lockId, long leaseTime, long waitTime) {
        LockRequest request = new LockRequest(lockId, resourceId, nodeId, leaseTime, System.currentTimeMillis() + waitTime);
        
        // Add to queue
        lockQueue.computeIfAbsent(resourceId, k -> new ConcurrentLinkedQueue<>()).offer(request);
        
        // Wait for lock to become available
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < waitTime) {
            DistributedLock existingLock = activeLocks.get(resourceId);
            if (existingLock == null || !existingLock.isActive() || existingLock.isExpired()) {
                // Lock became available, try to acquire
                if (tryAcquireFromCluster(resourceId, lockId, leaseTime)) {
                    DistributedLock lock = new DistributedLock(lockId, resourceId, nodeId, leaseTime);
                    activeLocks.put(resourceId, lock);
                    locksAcquired.incrementAndGet();
                    
                    // Remove from queue
                    Queue<LockRequest> queue = lockQueue.get(resourceId);
                    if (queue != null) {
                        queue.removeIf(req -> req.lockId.equals(lockId));
                    }
                    
                    System.out.printf("[%s] Acquired queued lock %s for resource %s%n", nodeId, lockId, resourceId);
                    return lock;
                }
            }
            
            try {
                Thread.sleep(100); // Check every 100ms
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }
        
        // Timeout, remove from queue
        Queue<LockRequest> queue = lockQueue.get(resourceId);
        if (queue != null) {
            queue.removeIf(req -> req.lockId.equals(lockId));
        }
        
        lockContentions.incrementAndGet();
        return null;
    }
    
    /**
     * Try to acquire lock from cluster (simplified consensus)
     */
    private boolean tryAcquireFromCluster(String resourceId, String lockId, long leaseTime) {
        // In a real implementation, this would involve consensus protocol
        // For simulation, we check with majority of nodes
        
        int approvals = 1; // Self approval
        int totalNodes = clusterNodes.size() + 1;
        
        for (ZomatoDistributedLockManager node : clusterNodes.values()) {
            if (node.isRunning.get() && node.canGrantLock(resourceId, lockId, nodeId)) {
                approvals++;
            }
        }
        
        // Need majority approval
        return approvals > totalNodes / 2;
    }
    
    /**
     * Check if this node can grant lock for resource
     */
    private boolean canGrantLock(String resourceId, String lockId, String requestingNodeId) {
        DistributedLock existingLock = activeLocks.get(resourceId);
        
        // Grant if no existing lock or lock is expired
        return existingLock == null || !existingLock.isActive() || existingLock.isExpired();
    }
    
    /**
     * Release a distributed lock
     */
    public boolean releaseLock(DistributedLock lock) {
        if (lock == null || !lock.getOwnerNodeId().equals(nodeId)) {
            return false;
        }
        
        DistributedLock existingLock = activeLocks.get(lock.getResourceId());
        if (existingLock != null && existingLock.getLockId().equals(lock.getLockId())) {
            existingLock.release();
            activeLocks.remove(lock.getResourceId());
            locksReleased.incrementAndGet();
            
            System.out.printf("[%s] Released lock %s for resource %s%n", 
                             nodeId, lock.getLockId(), lock.getResourceId());
            
            // Notify cluster
            notifyClusterLockReleased(lock.getResourceId(), lock.getLockId());
            
            return true;
        }
        
        return false;
    }
    
    /**
     * Renew a lock lease
     */
    public boolean renewLock(DistributedLock lock, long additionalTime) {
        if (lock == null || !lock.getOwnerNodeId().equals(nodeId)) {
            return false;
        }
        
        DistributedLock existingLock = activeLocks.get(lock.getResourceId());
        if (existingLock != null && existingLock.getLockId().equals(lock.getLockId())) {
            boolean renewed = existingLock.renew(additionalTime);
            if (renewed) {
                System.out.printf("[%s] Renewed lock %s for resource %s%n", 
                                 nodeId, lock.getLockId(), lock.getResourceId());
            }
            return renewed;
        }
        
        return false;
    }
    
    /**
     * Notify cluster nodes that lock was released
     */
    private void notifyClusterLockReleased(String resourceId, String lockId) {
        for (ZomatoDistributedLockManager node : clusterNodes.values()) {
            if (node.isRunning.get()) {
                node.handleLockReleaseNotification(resourceId, lockId);
            }
        }
    }
    
    /**
     * Handle lock release notification from another node
     */
    private void handleLockReleaseNotification(String resourceId, String lockId) {
        // Remove lock if it exists and matches
        DistributedLock existingLock = activeLocks.get(resourceId);
        if (existingLock != null && existingLock.getLockId().equals(lockId)) {
            activeLocks.remove(resourceId);
        }
    }
    
    /**
     * Process queued lock requests
     */
    private void processLockQueues() {
        if (!isRunning.get()) return;
        
        for (Map.Entry<String, Queue<LockRequest>> entry : lockQueue.entrySet()) {
            String resourceId = entry.getKey();
            Queue<LockRequest> queue = entry.getValue();
            
            if (queue.isEmpty()) continue;
            
            // Check if resource is available
            DistributedLock existingLock = activeLocks.get(resourceId);
            if (existingLock == null || !existingLock.isActive() || existingLock.isExpired()) {
                // Process next request in queue
                LockRequest request = queue.poll();
                if (request != null && !request.isExpired()) {
                    if (tryAcquireFromCluster(resourceId, request.lockId, request.leaseTime)) {
                        DistributedLock lock = new DistributedLock(request.lockId, resourceId, request.nodeId, request.leaseTime);
                        activeLocks.put(resourceId, lock);
                        locksAcquired.incrementAndGet();
                        
                        System.out.printf("[%s] Processed queued lock %s for resource %s%n", 
                                         nodeId, request.lockId, resourceId);
                    }
                }
            }
        }
    }
    
    /**
     * Clean up expired locks
     */
    private void cleanupExpiredLocks() {
        if (!isRunning.get()) return;
        
        List<String> expiredResources = new ArrayList<>();
        
        for (Map.Entry<String, DistributedLock> entry : activeLocks.entrySet()) {
            DistributedLock lock = entry.getValue();
            if (!lock.isActive() || lock.isExpired()) {
                expiredResources.add(entry.getKey());
            }
        }
        
        for (String resourceId : expiredResources) {
            DistributedLock removedLock = activeLocks.remove(resourceId);
            if (removedLock != null) {
                System.out.printf("[%s] Cleaned up expired lock %s for resource %s%n", 
                                 nodeId, removedLock.getLockId(), resourceId);
            }
        }
        
        // Clean up expired queue requests
        for (Queue<LockRequest> queue : lockQueue.values()) {
            queue.removeIf(LockRequest::isExpired);
        }
    }
    
    /**
     * Generate unique lock ID
     */
    private String generateLockId() {
        return String.format("LOCK_%s_%d_%d", nodeId, System.currentTimeMillis(), lockIdCounter.incrementAndGet());
    }
    
    /**
     * Get lock manager statistics
     */
    public LockManagerStats getStats() {
        return new LockManagerStats(
            nodeId,
            region,
            activeLocks.size(),
            lockQueue.values().stream().mapToInt(Queue::size).sum(),
            locksAcquired.get(),
            locksReleased.get(),
            lockContentions.get(),
            clusterNodes.size()
        );
    }
    
    /**
     * Lock request for queuing
     */
    private static class LockRequest {
        final String lockId;
        final String resourceId;
        final String nodeId;
        final long leaseTime;
        final long expiryTime;
        
        LockRequest(String lockId, String resourceId, String nodeId, long leaseTime, long expiryTime) {
            this.lockId = lockId;
            this.resourceId = resourceId;
            this.nodeId = nodeId;
            this.leaseTime = leaseTime;
            this.expiryTime = expiryTime;
        }
        
        boolean isExpired() {
            return System.currentTimeMillis() > expiryTime;
        }
    }
    
    /**
     * Lock manager statistics
     */
    public static class LockManagerStats {
        public final String nodeId;
        public final String region;
        public final int activeLocks;
        public final int queuedRequests;
        public final int locksAcquired;
        public final int locksReleased;
        public final int lockContentions;
        public final int clusterSize;
        
        public LockManagerStats(String nodeId, String region, int activeLocks, int queuedRequests,
                              int locksAcquired, int locksReleased, int lockContentions, int clusterSize) {
            this.nodeId = nodeId;
            this.region = region;
            this.activeLocks = activeLocks;
            this.queuedRequests = queuedRequests;
            this.locksAcquired = locksAcquired;
            this.locksReleased = locksReleased;
            this.lockContentions = lockContentions;
            this.clusterSize = clusterSize;
        }
        
        @Override
        public String toString() {
            return String.format("Stats{node=%s, region=%s, active=%d, queued=%d, acquired=%d, released=%d, contentions=%d}",
                               nodeId, region, activeLocks, queuedRequests, locksAcquired, locksReleased, lockContentions);
        }
    }
    
    /**
     * Exception for lock acquisition failures
     */
    public static class LockAcquisitionException extends Exception {
        public LockAcquisitionException(String message) {
            super(message);
        }
    }
}

/**
 * Zomato Order Processing Service using Distributed Locks
 */
class ZomatoOrderProcessingService {
    private final String serviceId;
    private final ZomatoDistributedLockManager lockManager;
    private final Map<String, ZomatoOrder> orders;
    private final Map<String, String> restaurantInventory;
    private final AtomicInteger processedOrders;
    
    public ZomatoOrderProcessingService(String serviceId, ZomatoDistributedLockManager lockManager) {
        this.serviceId = serviceId;
        this.lockManager = lockManager;
        this.orders = new ConcurrentHashMap<>();
        this.restaurantInventory = new ConcurrentHashMap<>();
        this.processedOrders = new AtomicInteger(0);
        
        // Initialize sample inventory
        initializeSampleInventory();
    }
    
    private void initializeSampleInventory() {
        // Sample restaurants with inventory
        restaurantInventory.put("rest_001:biryani", "50");
        restaurantInventory.put("rest_001:pizza", "30");
        restaurantInventory.put("rest_002:burger", "25");
        restaurantInventory.put("rest_002:pasta", "20");
        restaurantInventory.put("rest_003:dosa", "40");
        restaurantInventory.put("rest_003:idli", "60");
    }
    
    /**
     * Process Zomato order with distributed locking
     */
    public CompletableFuture<String> processOrder(ZomatoOrder order) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                System.out.printf("[%s] Processing order: %s%n", serviceId, order.orderId);
                
                // Lock order for processing
                String orderLockResource = "order:" + order.orderId;
                DistributedLock orderLock = lockManager.acquireLock(orderLockResource).get(5, TimeUnit.SECONDS);
                
                try {
                    // Lock restaurant for inventory check
                    String restaurantLockResource = "restaurant:" + order.restaurantId;
                    DistributedLock restaurantLock = lockManager.acquireLock(restaurantLockResource).get(5, TimeUnit.SECONDS);
                    
                    try {
                        // Check inventory and process order
                        if (checkAndUpdateInventory(order)) {
                            order.status = "CONFIRMED";
                            orders.put(order.orderId, order);
                            processedOrders.incrementAndGet();
                            
                            System.out.printf("[%s] Order %s confirmed successfully%n", serviceId, order.orderId);
                            return "ORDER_CONFIRMED";
                        } else {
                            order.status = "REJECTED_INVENTORY";
                            System.out.printf("[%s] Order %s rejected - insufficient inventory%n", serviceId, order.orderId);
                            return "ORDER_REJECTED";
                        }
                    } finally {
                        lockManager.releaseLock(restaurantLock);
                    }
                } finally {
                    lockManager.releaseLock(orderLock);
                }
                
            } catch (Exception e) {
                System.err.printf("[%s] Error processing order %s: %s%n", serviceId, order.orderId, e.getMessage());
                return "ORDER_ERROR";
            }
        });
    }
    
    /**
     * Check and update restaurant inventory
     */
    private boolean checkAndUpdateInventory(ZomatoOrder order) {
        for (String item : order.items) {
            String inventoryKey = order.restaurantId + ":" + item;
            String currentStock = restaurantInventory.get(inventoryKey);
            
            if (currentStock == null) {
                System.out.printf("[%s] Item %s not available in restaurant %s%n", 
                                 serviceId, item, order.restaurantId);
                return false;
            }
            
            int stock = Integer.parseInt(currentStock);
            if (stock <= 0) {
                System.out.printf("[%s] Item %s out of stock in restaurant %s%n", 
                                 serviceId, item, order.restaurantId);
                return false;
            }
        }
        
        // Update inventory (decrement stock)
        for (String item : order.items) {
            String inventoryKey = order.restaurantId + ":" + item;
            String currentStock = restaurantInventory.get(inventoryKey);
            int newStock = Integer.parseInt(currentStock) - 1;
            restaurantInventory.put(inventoryKey, String.valueOf(newStock));
            
            System.out.printf("[%s] Updated inventory for %s: %d remaining%n", 
                             serviceId, inventoryKey, newStock);
        }
        
        return true;
    }
    
    /**
     * Get service statistics
     */
    public ServiceStats getStats() {
        return new ServiceStats(
            serviceId,
            orders.size(),
            processedOrders.get(),
            restaurantInventory.size()
        );
    }
    
    public static class ServiceStats {
        public final String serviceId;
        public final int totalOrders;
        public final int processedOrders;
        public final int inventoryItems;
        
        public ServiceStats(String serviceId, int totalOrders, int processedOrders, int inventoryItems) {
            this.serviceId = serviceId;
            this.totalOrders = totalOrders;
            this.processedOrders = processedOrders;
            this.inventoryItems = inventoryItems;
        }
        
        @Override
        public String toString() {
            return String.format("Service{id=%s, total=%d, processed=%d, inventory=%d}",
                               serviceId, totalOrders, processedOrders, inventoryItems);
        }
    }
}

/**
 * Main demonstration class
 */
public class ZomatoDistributedLockDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🍽️  Zomato Distributed Lock Manager Demo");
        System.out.println("=" .repeat(60));
        
        // Create distributed lock managers for different regions
        ZomatoDistributedLockManager mumbaiLockManager = new ZomatoDistributedLockManager("zomato-lock-mumbai", "Mumbai");
        ZomatoDistributedLockManager delhiLockManager = new ZomatoDistributedLockManager("zomato-lock-delhi", "Delhi");
        ZomatoDistributedLockManager bangaloreLockManager = new ZomatoDistributedLockManager("zomato-lock-bangalore", "Bangalore");
        
        // Setup cluster
        System.out.println("\n🏢 Setting up distributed lock manager cluster...");
        mumbaiLockManager.addClusterNode(delhiLockManager);
        mumbaiLockManager.addClusterNode(bangaloreLockManager);
        delhiLockManager.addClusterNode(mumbaiLockManager);
        delhiLockManager.addClusterNode(bangaloreLockManager);
        bangaloreLockManager.addClusterNode(mumbaiLockManager);
        bangaloreLockManager.addClusterNode(delhiLockManager);
        
        // Start all lock managers
        mumbaiLockManager.start();
        delhiLockManager.start();
        bangaloreLockManager.start();
        
        System.out.println("✅ All lock managers started");
        
        // Create order processing services
        ZomatoOrderProcessingService mumbaiService = new ZomatoOrderProcessingService("zomato-service-mumbai", mumbaiLockManager);
        ZomatoOrderProcessingService delhiService = new ZomatoOrderProcessingService("zomato-service-delhi", delhiLockManager);
        ZomatoOrderProcessingService bangaloreService = new ZomatoOrderProcessingService("zomato-service-bangalore", bangaloreLockManager);
        
        // Create sample orders
        System.out.println("\n🍽️  Creating sample Zomato orders...");
        
        List<ZomatoOrder> orders = Arrays.asList(
            new ZomatoOrder("ORD001", "customer_rahul", "rest_001", Arrays.asList("biryani", "pizza"), 450.0),
            new ZomatoOrder("ORD002", "customer_priya", "rest_001", Arrays.asList("biryani"), 250.0),
            new ZomatoOrder("ORD003", "customer_arjun", "rest_002", Arrays.asList("burger", "pasta"), 380.0),
            new ZomatoOrder("ORD004", "customer_sneha", "rest_002", Arrays.asList("burger"), 180.0),
            new ZomatoOrder("ORD005", "customer_amit", "rest_003", Arrays.asList("dosa", "idli"), 120.0),
            new ZomatoOrder("ORD006", "customer_deepika", "rest_003", Arrays.asList("dosa"), 80.0),
            new ZomatoOrder("ORD007", "customer_vikash", "rest_001", Arrays.asList("pizza"), 200.0),
            new ZomatoOrder("ORD008", "customer_kiran", "rest_002", Arrays.asList("pasta"), 220.0)
        );
        
        for (ZomatoOrder order : orders) {
            System.out.printf("📋 Created order: %s%n", order);
        }
        
        // Process orders concurrently using different services
        System.out.println("\n⚡ Processing orders concurrently with distributed locking...");
        
        List<CompletableFuture<String>> futures = new ArrayList<>();
        ZomatoOrderProcessingService[] services = {mumbaiService, delhiService, bangaloreService};
        
        for (int i = 0; i < orders.size(); i++) {
            ZomatoOrder order = orders.get(i);
            ZomatoOrderProcessingService service = services[i % services.length];
            
            CompletableFuture<String> future = service.processOrder(order);
            futures.add(future);
            
            System.out.printf("🚀 Submitted order %s to %s%n", order.orderId, service.getStats().serviceId);
            
            // Small delay to create some contention
            Thread.sleep(100);
        }
        
        // Wait for all orders to complete
        System.out.println("\n⏳ Waiting for order processing to complete...");
        
        for (int i = 0; i < futures.size(); i++) {
            try {
                String result = futures.get(i).get(10, TimeUnit.SECONDS);
                ZomatoOrder order = orders.get(i);
                System.out.printf("✅ Order %s: %s (Status: %s)%n", order.orderId, result, order.status);
            } catch (Exception e) {
                System.err.printf("❌ Order processing failed: %s%n", e.getMessage());
            }
        }
        
        // Show lock manager statistics
        System.out.println("\n📊 Lock Manager Statistics:");
        
        ZomatoDistributedLockManager[] lockManagers = {mumbaiLockManager, delhiLockManager, bangaloreLockManager};
        for (ZomatoDistributedLockManager lockManager : lockManagers) {
            System.out.println("  " + lockManager.getStats());
        }
        
        // Show service statistics
        System.out.println("\n📈 Order Processing Service Statistics:");
        ZomatoOrderProcessingService[] allServices = {mumbaiService, delhiService, bangaloreService};
        for (ZomatoOrderProcessingService service : allServices) {
            System.out.println("  " + service.getStats());
        }
        
        // Demonstrate lock contention scenario
        System.out.println("\n🔒 Demonstrating lock contention scenario...");
        
        // Multiple services trying to process same restaurant simultaneously
        String contentionResource = "restaurant:rest_001";
        
        List<CompletableFuture<DistributedLock>> lockFutures = new ArrayList<>();
        for (ZomatoDistributedLockManager lockManager : lockManagers) {
            CompletableFuture<DistributedLock> lockFuture = lockManager.acquireLock(contentionResource, 5000, 3000);
            lockFutures.add(lockFuture);
        }
        
        // See which lock manager wins
        for (int i = 0; i < lockFutures.size(); i++) {
            try {
                DistributedLock lock = lockFutures.get(i).get(5, TimeUnit.SECONDS);
                System.out.printf("🏆 %s acquired contested lock: %s%n", 
                                 lockManagers[i].nodeId, lock.getLockId());
                
                // Hold lock for a bit then release
                Thread.sleep(2000);
                lockManagers[i].releaseLock(lock);
                
            } catch (Exception e) {
                System.out.printf("❌ %s failed to acquire contested lock: %s%n", 
                                 lockManagers[i].nodeId, e.getMessage());
            }
        }
        
        // Final statistics
        System.out.println("\n📊 Final Lock Manager Statistics:");
        for (ZomatoDistributedLockManager lockManager : lockManagers) {
            System.out.println("  " + lockManager.getStats());
        }
        
        // Production insights
        System.out.println("\n💡 Production Insights:");
        System.out.println("- Distributed locks prevent race conditions in order processing");
        System.out.println("- Essential for maintaining inventory consistency across services");
        System.out.println("- Zomato processes 2M+ daily orders requiring coordination");
        System.out.println("- Lock leasing prevents deadlocks from failed nodes");
        System.out.println("- Queue-based fairness ensures no order processing starvation");
        System.out.println("- Consensus protocol ensures cluster-wide lock coordination");
        System.out.println("- Critical for preventing double-booking of delivery partners");
        System.out.println("- Enables safe concurrent access to shared restaurant resources");
        System.out.println("- Horizontal scaling across regions with distributed coordination");
        
        // Cleanup
        System.out.println("\n🧹 Shutting down lock managers...");
        mumbaiLockManager.stop();
        delhiLockManager.stop();
        bangaloreLockManager.stop();
        
        System.out.println("Demo completed!");
    }
}