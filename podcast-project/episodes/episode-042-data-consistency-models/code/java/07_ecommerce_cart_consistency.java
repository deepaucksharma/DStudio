/**
 * E-commerce Cart Consistency Manager
 * Flipkart/Amazon jaisa shopping cart with consistency guarantees
 * Handles concurrent cart updates, session management
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.time.Instant;
import java.util.logging.Logger;
import java.util.logging.Level;

// Shopping cart item - Flipkart product jaisa
class CartItem {
    private final String productId;
    private final String productName;
    private final double price;
    private int quantity;
    private final Instant addedAt;
    
    public CartItem(String productId, String productName, double price, int quantity) {
        this.productId = productId;
        this.productName = productName; 
        this.price = price;
        this.quantity = quantity;
        this.addedAt = Instant.now();
    }
    
    // Getters and setters
    public String getProductId() { return productId; }
    public String getProductName() { return productName; }
    public double getPrice() { return price; }
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
    public Instant getAddedAt() { return addedAt; }
    
    public double getTotalPrice() {
        return price * quantity;
    }
    
    @Override
    public String toString() {
        return String.format("%s x%d (₹%.2f each)", productName, quantity, price);
    }
}

// Shopping cart with version control - Consistency ke liye
class ShoppingCart {
    private final String sessionId;
    private final String userId;
    private final Map<String, CartItem> items;
    private volatile long version;
    private final Instant createdAt;
    private volatile Instant lastModified;
    private final ReentrantReadWriteLock lock;
    
    public ShoppingCart(String sessionId, String userId) {
        this.sessionId = sessionId;
        this.userId = userId;
        this.items = new ConcurrentHashMap<>();
        this.version = 1L;
        this.createdAt = Instant.now();
        this.lastModified = Instant.now();
        this.lock = new ReentrantReadWriteLock();
    }
    
    // Thread-safe item addition - Mumbai local mein seat milne jaisa race condition
    public boolean addItem(String productId, String productName, double price, int quantity) {
        lock.writeLock().lock();
        try {
            CartItem existingItem = items.get(productId);
            
            if (existingItem != null) {
                // Update quantity - existing item hai
                existingItem.setQuantity(existingItem.getQuantity() + quantity);
            } else {
                // Naya item add karo
                items.put(productId, new CartItem(productId, productName, price, quantity));
            }
            
            version++;
            lastModified = Instant.now();
            return true;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public boolean removeItem(String productId, int quantity) {
        lock.writeLock().lock();
        try {
            CartItem item = items.get(productId);
            if (item == null) {
                return false;
            }
            
            if (quantity >= item.getQuantity()) {
                // Remove completely
                items.remove(productId);
            } else {
                // Reduce quantity
                item.setQuantity(item.getQuantity() - quantity);
            }
            
            version++;
            lastModified = Instant.now();
            return true;
            
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public Map<String, CartItem> getItems() {
        lock.readLock().lock();
        try {
            return new HashMap<>(items);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public double getTotalAmount() {
        lock.readLock().lock();
        try {
            return items.values().stream()
                    .mapToDouble(CartItem::getTotalPrice)
                    .sum();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public int getItemCount() {
        lock.readLock().lock();
        try {
            return items.values().stream()
                    .mapToInt(CartItem::getQuantity)
                    .sum();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    // Getters
    public String getSessionId() { return sessionId; }
    public String getUserId() { return userId; }
    public long getVersion() { return version; }
    public Instant getLastModified() { return lastModified; }
}

// Cart operation for audit trail
class CartOperation {
    private final String operationId;
    private final String sessionId;
    private final String operationType; // ADD, REMOVE, CLEAR
    private final String productId;
    private final int quantity;
    private final Instant timestamp;
    private final long cartVersionBefore;
    private final long cartVersionAfter;
    
    public CartOperation(String operationId, String sessionId, String operationType,
                        String productId, int quantity, long versionBefore, long versionAfter) {
        this.operationId = operationId;
        this.sessionId = sessionId;
        this.operationType = operationType;
        this.productId = productId;
        this.quantity = quantity;
        this.timestamp = Instant.now();
        this.cartVersionBefore = versionBefore;
        this.cartVersionAfter = versionAfter;
    }
    
    // Getters
    public String getOperationId() { return operationId; }
    public String getSessionId() { return sessionId; }
    public String getOperationType() { return operationType; }
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public Instant getTimestamp() { return timestamp; }
    public long getCartVersionBefore() { return cartVersionBefore; }
    public long getCartVersionAfter() { return cartVersionAfter; }
}

// Main cart consistency manager - Flipkart backend jaisa
public class ECommerceCartConsistency {
    private static final Logger logger = Logger.getLogger(ECommerceCartConsistency.class.getName());
    
    private final Map<String, ShoppingCart> activeCarts;
    private final Map<String, List<CartOperation>> operationHistory;
    private final ExecutorService syncExecutor;
    private final ReentrantReadWriteLock globalLock;
    
    // Simulated database replicas - Mumbai, Delhi, Bangalore servers
    private final Map<String, Map<String, ShoppingCart>> replicaStores;
    
    public ECommerceCartConsistency() {
        this.activeCarts = new ConcurrentHashMap<>();
        this.operationHistory = new ConcurrentHashMap<>();
        this.syncExecutor = Executors.newFixedThreadPool(5);
        this.globalLock = new ReentrantReadWriteLock();
        
        // Initialize replicas
        this.replicaStores = new ConcurrentHashMap<>();
        replicaStores.put("mumbai", new ConcurrentHashMap<>());
        replicaStores.put("delhi", new ConcurrentHashMap<>());
        replicaStores.put("bangalore", new ConcurrentHashMap<>());
    }
    
    // Create new shopping session - User login jaisa
    public String createCart(String userId, String preferredRegion) {
        String sessionId = "CART_" + System.currentTimeMillis() + "_" + userId;
        
        ShoppingCart cart = new ShoppingCart(sessionId, userId);
        activeCarts.put(sessionId, cart);
        operationHistory.put(sessionId, new ArrayList<>());
        
        // Store in preferred region replica
        Map<String, ShoppingCart> regionStore = replicaStores.get(preferredRegion);
        if (regionStore != null) {
            regionStore.put(sessionId, cart);
        }
        
        logger.info(String.format("Cart created: %s for user %s in %s", 
                                sessionId, userId, preferredRegion));
        
        // Async sync to other regions
        scheduleAsyncSync(sessionId, preferredRegion);
        
        return sessionId;
    }
    
    // Add item with consistency guarantee - Flipkart "Add to Cart" button
    public boolean addToCart(String sessionId, String productId, String productName, 
                           double price, int quantity) {
        ShoppingCart cart = activeCarts.get(sessionId);
        if (cart == null) {
            logger.warning("Cart not found: " + sessionId);
            return false;
        }
        
        globalLock.writeLock().lock();
        try {
            long versionBefore = cart.getVersion();
            
            boolean success = cart.addItem(productId, productName, price, quantity);
            
            if (success) {
                long versionAfter = cart.getVersion();
                
                // Record operation for audit
                CartOperation operation = new CartOperation(
                    UUID.randomUUID().toString(),
                    sessionId, "ADD", productId, quantity, versionBefore, versionAfter
                );
                
                operationHistory.get(sessionId).add(operation);
                
                logger.info(String.format("Added to cart: %s x%d to session %s (v%d→v%d)",
                                        productName, quantity, sessionId, versionBefore, versionAfter));
                
                // Async sync to replicas
                scheduleAsyncSync(sessionId, null);
                
                return true;
            }
            
            return false;
            
        } finally {
            globalLock.writeLock().unlock();
        }
    }
    
    public boolean removeFromCart(String sessionId, String productId, int quantity) {
        ShoppingCart cart = activeCarts.get(sessionId);
        if (cart == null) {
            return false;
        }
        
        globalLock.writeLock().lock();
        try {
            long versionBefore = cart.getVersion();
            
            boolean success = cart.removeItem(productId, quantity);
            
            if (success) {
                long versionAfter = cart.getVersion();
                
                CartOperation operation = new CartOperation(
                    UUID.randomUUID().toString(),
                    sessionId, "REMOVE", productId, quantity, versionBefore, versionAfter
                );
                
                operationHistory.get(sessionId).add(operation);
                
                logger.info(String.format("Removed from cart: %s x%d from session %s",
                                        productId, quantity, sessionId));
                
                // Async sync
                scheduleAsyncSync(sessionId, null);
                
                return true;
            }
            
            return false;
            
        } finally {
            globalLock.writeLock().unlock();
        }
    }
    
    // Get cart with read consistency - User ko consistent view dikhana
    public ShoppingCart getCart(String sessionId, String preferredRegion) {
        globalLock.readLock().lock();
        try {
            // Try preferred region first
            if (preferredRegion != null) {
                Map<String, ShoppingCart> regionStore = replicaStores.get(preferredRegion);
                if (regionStore != null && regionStore.containsKey(sessionId)) {
                    ShoppingCart regionalCart = regionStore.get(sessionId);
                    ShoppingCart mainCart = activeCarts.get(sessionId);
                    
                    // Return most recent version
                    if (mainCart != null && mainCart.getVersion() > regionalCart.getVersion()) {
                        return mainCart;
                    } else {
                        return regionalCart;
                    }
                }
            }
            
            // Fallback to main store
            return activeCarts.get(sessionId);
            
        } finally {
            globalLock.readLock().unlock();
        }
    }
    
    // Async synchronization between replicas
    private void scheduleAsyncSync(String sessionId, String excludeRegion) {
        syncExecutor.submit(() -> {
            try {
                Thread.sleep(50); // Simulate network delay
                
                ShoppingCart sourceCart = activeCarts.get(sessionId);
                if (sourceCart == null) return;
                
                for (String region : replicaStores.keySet()) {
                    if (region.equals(excludeRegion)) continue;
                    
                    Map<String, ShoppingCart> regionStore = replicaStores.get(region);
                    ShoppingCart existingCart = regionStore.get(sessionId);
                    
                    // Sync if version is newer
                    if (existingCart == null || sourceCart.getVersion() > existingCart.getVersion()) {
                        // Create new cart copy
                        ShoppingCart syncedCart = new ShoppingCart(sourceCart.getSessionId(), 
                                                                 sourceCart.getUserId());
                        
                        // Copy items
                        for (CartItem item : sourceCart.getItems().values()) {
                            syncedCart.addItem(item.getProductId(), item.getProductName(),
                                             item.getPrice(), item.getQuantity());
                        }
                        
                        regionStore.put(sessionId, syncedCart);
                        
                        logger.fine(String.format("Synced cart %s to %s region", sessionId, region));
                    }
                }
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } catch (Exception e) {
                logger.log(Level.WARNING, "Sync failed for session: " + sessionId, e);
            }
        });
    }
    
    // Check consistency across replicas
    public Map<String, Object> checkConsistency(String sessionId) {
        Map<String, Object> consistencyReport = new HashMap<>();
        List<String> inconsistencies = new ArrayList<>();
        
        ShoppingCart mainCart = activeCarts.get(sessionId);
        if (mainCart == null) {
            consistencyReport.put("error", "Cart not found");
            return consistencyReport;
        }
        
        long mainVersion = mainCart.getVersion();
        int mainItemCount = mainCart.getItemCount();
        double mainTotal = mainCart.getTotalAmount();
        
        consistencyReport.put("main_version", mainVersion);
        consistencyReport.put("main_item_count", mainItemCount);
        consistencyReport.put("main_total", mainTotal);
        
        Map<String, Map<String, Object>> replicaStatus = new HashMap<>();
        
        for (Map.Entry<String, Map<String, ShoppingCart>> replicaEntry : replicaStores.entrySet()) {
            String region = replicaEntry.getKey();
            ShoppingCart replicaCart = replicaEntry.getValue().get(sessionId);
            
            if (replicaCart != null) {
                long replicaVersion = replicaCart.getVersion();
                int replicaItemCount = replicaCart.getItemCount();
                double replicaTotal = replicaCart.getTotalAmount();
                
                Map<String, Object> replicaInfo = new HashMap<>();
                replicaInfo.put("version", replicaVersion);
                replicaInfo.put("item_count", replicaItemCount);
                replicaInfo.put("total", replicaTotal);
                
                replicaStatus.put(region, replicaInfo);
                
                // Check for inconsistencies
                if (replicaVersion != mainVersion) {
                    inconsistencies.add(String.format("%s version mismatch: %d vs %d", 
                                                    region, replicaVersion, mainVersion));
                }
                
                if (Math.abs(replicaTotal - mainTotal) > 0.01) {
                    inconsistencies.add(String.format("%s total amount mismatch: %.2f vs %.2f",
                                                    region, replicaTotal, mainTotal));
                }
            } else {
                replicaStatus.put(region, Collections.singletonMap("status", "NOT_SYNCED"));
                inconsistencies.add(region + " replica not synced");
            }
        }
        
        consistencyReport.put("replicas", replicaStatus);
        consistencyReport.put("inconsistencies", inconsistencies);
        consistencyReport.put("is_consistent", inconsistencies.isEmpty());
        
        return consistencyReport;
    }
    
    // Get operation history for debugging
    public List<CartOperation> getOperationHistory(String sessionId) {
        return operationHistory.getOrDefault(sessionId, new ArrayList<>());
    }
    
    // Simulate concurrent cart operations - Stress test
    public void simulateConcurrentOperations(String sessionId, int operationCount) {
        String[] products = {
            "iPhone_13", "Samsung_Galaxy", "MacBook_Pro", "Dell_Laptop",
            "AirPods", "Sony_Headphones", "Kindle", "iPad"
        };
        
        double[] prices = {70000, 50000, 120000, 60000, 15000, 8000, 12000, 35000};
        
        CountDownLatch latch = new CountDownLatch(operationCount);
        
        for (int i = 0; i < operationCount; i++) {
            final int operationId = i;
            
            syncExecutor.submit(() -> {
                try {
                    Random random = new Random();
                    int productIndex = random.nextInt(products.length);
                    
                    if (random.nextBoolean()) {
                        // Add operation
                        addToCart(sessionId, "PROD_" + productIndex, products[productIndex],
                                prices[productIndex], random.nextInt(3) + 1);
                    } else {
                        // Remove operation  
                        removeFromCart(sessionId, "PROD_" + productIndex, 1);
                    }
                    
                } finally {
                    latch.countDown();
                }
            });
        }
        
        try {
            latch.await(30, TimeUnit.SECONDS);
            logger.info("Concurrent operations completed for session: " + sessionId);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public void shutdown() {
        syncExecutor.shutdown();
        try {
            if (!syncExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                syncExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            syncExecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    // Demo method - Flipkart shopping scenario
    public static void main(String[] args) {
        System.out.println("=== E-commerce Cart Consistency Demo ===");
        
        ECommerceCartConsistency cartManager = new ECommerceCartConsistency();
        
        try {
            // Create user sessions
            System.out.println("\n=== Creating User Sessions ===");
            String rahulCart = cartManager.createCart("rahul_mumbai", "mumbai");
            String priyaCart = cartManager.createCart("priya_delhi", "delhi");
            String vikramCart = cartManager.createCart("vikram_blr", "bangalore");
            
            System.out.println("Rahul's cart: " + rahulCart);
            System.out.println("Priya's cart: " + priyaCart);
            System.out.println("Vikram's cart: " + vikramCart);
            
            // Shopping activities
            System.out.println("\n=== Shopping Activities ===");
            
            // Rahul ki shopping
            cartManager.addToCart(rahulCart, "IPHONE13", "iPhone 13", 70000.0, 1);
            cartManager.addToCart(rahulCart, "AIRPODS", "AirPods Pro", 25000.0, 1);
            cartManager.addToCart(rahulCart, "CASE", "Phone Case", 1500.0, 2);
            
            // Priya ki shopping  
            cartManager.addToCart(priyaCart, "MACBOOK", "MacBook Pro", 120000.0, 1);
            cartManager.addToCart(priyaCart, "MOUSE", "Magic Mouse", 8000.0, 1);
            
            // Vikram ki shopping
            cartManager.addToCart(vikramCart, "LAPTOP", "Dell XPS", 80000.0, 1);
            cartManager.addToCart(vikramCart, "HEADPHONES", "Sony WH-1000XM4", 25000.0, 1);
            
            // Wait for sync
            Thread.sleep(200);
            
            // Check cart contents
            System.out.println("\n=== Cart Contents ===");
            
            ShoppingCart rahulCartObj = cartManager.getCart(rahulCart, "mumbai");
            if (rahulCartObj != null) {
                System.out.println(String.format("Rahul's cart (₹%.2f, %d items):",
                                                rahulCartObj.getTotalAmount(), rahulCartObj.getItemCount()));
                
                for (CartItem item : rahulCartObj.getItems().values()) {
                    System.out.println("  " + item.toString());
                }
            }
            
            // Concurrent operations test
            System.out.println("\n=== Concurrent Operations Test ===");
            cartManager.simulateConcurrentOperations(rahulCart, 50);
            
            // Wait for operations to complete
            Thread.sleep(1000);
            
            // Check consistency
            System.out.println("\n=== Consistency Check ===");
            Map<String, Object> consistencyReport = cartManager.checkConsistency(rahulCart);
            
            System.out.println("Main cart version: " + consistencyReport.get("main_version"));
            System.out.println("Main cart total: ₹" + consistencyReport.get("main_total"));
            System.out.println("Is consistent: " + consistencyReport.get("is_consistent"));
            
            @SuppressWarnings("unchecked")
            List<String> inconsistencies = (List<String>) consistencyReport.get("inconsistencies");
            if (!inconsistencies.isEmpty()) {
                System.out.println("Inconsistencies found:");
                for (String inconsistency : inconsistencies) {
                    System.out.println("  - " + inconsistency);
                }
            }
            
            // Operation history
            System.out.println("\n=== Recent Operations (Rahul) ===");
            List<CartOperation> operations = cartManager.getOperationHistory(rahulCart);
            
            int displayCount = Math.min(5, operations.size());
            for (int i = operations.size() - displayCount; i < operations.size(); i++) {
                CartOperation op = operations.get(i);
                System.out.println(String.format("  %s: %s %s x%d (v%d→v%d)",
                                                op.getOperationType(), op.getProductId(), 
                                                op.getOperationType(), op.getQuantity(),
                                                op.getCartVersionBefore(), op.getCartVersionAfter()));
            }
            
            System.out.println("\n✅ E-commerce cart consistency demo completed successfully!");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        } finally {
            cartManager.shutdown();
        }
    }
}