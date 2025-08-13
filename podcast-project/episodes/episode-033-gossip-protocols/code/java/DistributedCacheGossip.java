/**
 * Distributed Cache with Gossip-based Invalidation
 * ================================================
 * 
 * Flipkart Product Cache Network: जब product prices update होती हैं तो
 * कैसे सभी cache nodes को efficiently inform करें कि data stale हो गया?
 * 
 * This implements a distributed cache system that uses gossip protocol
 * for cache invalidation and data consistency across multiple nodes.
 * 
 * Author: Code Developer Agent
 * Episode: 33 - Gossip Protocols
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

enum CacheEntryState {
    VALID,
    STALE,
    INVALIDATED,
    UPDATING
}

class CacheEntry {
    private final String key;
    private Object value;
    private long version;
    private long timestamp;
    private CacheEntryState state;
    private long ttl; // Time to live in milliseconds
    private String checksum;
    
    public CacheEntry(String key, Object value, long version, long ttl) {
        this.key = key;
        this.value = value;
        this.version = version;
        this.timestamp = System.currentTimeMillis();
        this.state = CacheEntryState.VALID;
        this.ttl = ttl;
        this.checksum = calculateChecksum(value);
    }
    
    private String calculateChecksum(Object value) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            md.update(value.toString().getBytes());
            byte[] digest = md.digest();
            
            StringBuilder sb = new StringBuilder();
            for (byte b : digest) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString().substring(0, 8); // Short checksum
        } catch (NoSuchAlgorithmException e) {
            return "unknown";
        }
    }
    
    public boolean isExpired() {
        return System.currentTimeMillis() - timestamp > ttl;
    }
    
    public boolean isValid() {
        return state == CacheEntryState.VALID && !isExpired();
    }
    
    // Getters and setters
    public String getKey() { return key; }
    public Object getValue() { return value; }
    public void setValue(Object value) { 
        this.value = value; 
        this.checksum = calculateChecksum(value);
        this.timestamp = System.currentTimeMillis();
    }
    public long getVersion() { return version; }
    public void setVersion(long version) { this.version = version; }
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    public CacheEntryState getState() { return state; }
    public void setState(CacheEntryState state) { this.state = state; }
    public long getTtl() { return ttl; }
    public String getChecksum() { return checksum; }
    
    @Override
    public String toString() {
        return String.format("CacheEntry{key='%s', version=%d, state=%s, checksum=%s}", 
                           key, version, state, checksum);
    }
}

class InvalidationMessage {
    private final String nodeId;
    private final List<String> invalidatedKeys;
    private final Map<String, Long> keyVersions;
    private final long timestamp;
    private final int messageId;
    
    public InvalidationMessage(String nodeId, List<String> invalidatedKeys, 
                             Map<String, Long> keyVersions, int messageId) {
        this.nodeId = nodeId;
        this.invalidatedKeys = new ArrayList<>(invalidatedKeys);
        this.keyVersions = new HashMap<>(keyVersions);
        this.timestamp = System.currentTimeMillis();
        this.messageId = messageId;
    }
    
    public String getNodeId() { return nodeId; }
    public List<String> getInvalidatedKeys() { return invalidatedKeys; }
    public Map<String, Long> getKeyVersions() { return keyVersions; }
    public long getTimestamp() { return timestamp; }
    public int getMessageId() { return messageId; }
}

class ProductInfo {
    private final String productId;
    private final String name;
    private double price;
    private int stock;
    private String category;
    
    public ProductInfo(String productId, String name, double price, int stock, String category) {
        this.productId = productId;
        this.name = name;
        this.price = price;
        this.stock = stock;
        this.category = category;
    }
    
    // Getters and setters
    public String getProductId() { return productId; }
    public String getName() { return name; }
    public double getPrice() { return price; }
    public void setPrice(double price) { this.price = price; }
    public int getStock() { return stock; }
    public void setStock(int stock) { this.stock = stock; }
    public String getCategory() { return category; }
    
    @Override
    public String toString() {
        return String.format("Product{id='%s', name='%s', price=%.2f, stock=%d}", 
                           productId, name, price, stock);
    }
}

public class DistributedCacheGossip {
    private final String nodeId;
    private final String region;
    private final Map<String, CacheEntry> cache;
    private final Set<String> peerNodes;
    private final Map<String, Long> versionVector;
    private final AtomicLong localVersion;
    
    // Gossip protocol parameters
    private final int gossipFanout = 3;
    private final long gossipInterval = 3000; // 3 seconds
    private final long cacheEntryTtl = 300000; // 5 minutes
    
    // Threading
    private final ScheduledExecutorService scheduler;
    private final Random random;
    
    // Statistics
    private int cacheHits = 0;
    private int cacheMisses = 0;
    private int invalidationsReceived = 0;
    private int invalidationsSent = 0;
    private int gossipRounds = 0;
    
    // Message tracking
    private final Set<Integer> processedMessages;
    private int messageCounter = 0;
    
    public DistributedCacheGossip(String nodeId, String region) {
        this.nodeId = nodeId;
        this.region = region;
        this.cache = new ConcurrentHashMap<>();
        this.peerNodes = ConcurrentHashMap.newKeySet();
        this.versionVector = new ConcurrentHashMap<>();
        this.localVersion = new AtomicLong(0);
        this.scheduler = Executors.newScheduledThreadPool(2);
        this.random = new Random();
        this.processedMessages = ConcurrentHashMap.newKeySet();
        
        startGossipProtocol();
        startCacheCleanup();
        
        System.out.println("🏪 Flipkart Cache Node " + nodeId + " started in " + region);
    }
    
    public void addPeer(String peerId) {
        peerNodes.add(peerId);
        versionVector.put(peerId, 0L);
        System.out.println("🔗 Added peer: " + peerId);
    }
    
    public void put(String key, Object value) {
        put(key, value, cacheEntryTtl);
    }
    
    public void put(String key, Object value, long ttl) {
        long version = localVersion.incrementAndGet();
        CacheEntry entry = new CacheEntry(key, value, version, ttl);
        
        cache.put(key, entry);
        versionVector.put(nodeId, version);
        
        System.out.println("💾 " + nodeId + " cached: " + key + " (v" + version + ")");
        
        // Trigger gossip for cache invalidation
        scheduleInvalidationGossip(key, version);
    }
    
    public Object get(String key) {
        CacheEntry entry = cache.get(key);
        
        if (entry == null) {
            cacheMisses++;
            System.out.println("❌ Cache miss: " + key + " on " + nodeId);
            
            // Simulate loading from database
            Object value = loadFromDatabase(key);
            if (value != null) {
                put(key, value);
            }
            return value;
        }
        
        if (!entry.isValid()) {
            cacheMisses++;
            cache.remove(key);
            System.out.println("⏰ Expired entry removed: " + key + " on " + nodeId);
            
            // Load fresh data
            Object value = loadFromDatabase(key);
            if (value != null) {
                put(key, value);
            }
            return value;
        }
        
        cacheHits++;
        System.out.println("✅ Cache hit: " + key + " on " + nodeId + " (v" + entry.getVersion() + ")");
        return entry.getValue();
    }
    
    public void invalidate(String key) {
        CacheEntry entry = cache.get(key);
        if (entry != null) {
            entry.setState(CacheEntryState.INVALIDATED);
            cache.remove(key);
            
            long version = localVersion.incrementAndGet();
            versionVector.put(nodeId, version);
            
            System.out.println("🗑️  " + nodeId + " invalidated: " + key);
            
            // Gossip invalidation to peers
            scheduleInvalidationGossip(key, version);
        }
    }
    
    private Object loadFromDatabase(String key) {
        // Simulate database load with some sample product data
        if (key.startsWith("product_")) {
            String productId = key.substring(8);
            return new ProductInfo(
                productId,
                "Product " + productId,
                1000 + random.nextDouble() * 9000, // Price between 1000-10000
                random.nextInt(100), // Stock 0-99
                "Electronics"
            );
        }
        return null;
    }
    
    private void scheduleInvalidationGossip(String key, long version) {
        // Immediate gossip for invalidation
        scheduler.schedule(() -> {
            gossipInvalidation(Arrays.asList(key), Map.of(key, version));
        }, 100, TimeUnit.MILLISECONDS);
    }
    
    private void startGossipProtocol() {
        scheduler.scheduleAtFixedRate(this::performGossipRound, 
                                    gossipInterval, gossipInterval, TimeUnit.MILLISECONDS);
    }
    
    private void startCacheCleanup() {
        scheduler.scheduleAtFixedRate(this::cleanupExpiredEntries, 
                                    60000, 60000, TimeUnit.MILLISECONDS); // Every minute
    }
    
    private void performGossipRound() {
        gossipRounds++;
        
        if (peerNodes.isEmpty()) {
            return;
        }
        
        // Select peers for this gossip round
        List<String> selectedPeers = selectGossipPeers();
        
        // Collect recently updated cache entries for gossip
        List<String> recentlyUpdatedKeys = getRecentlyUpdatedKeys();
        
        if (!recentlyUpdatedKeys.isEmpty()) {
            Map<String, Long> keyVersions = new HashMap<>();
            for (String key : recentlyUpdatedKeys) {
                CacheEntry entry = cache.get(key);
                if (entry != null) {
                    keyVersions.put(key, entry.getVersion());
                }
            }
            
            gossipInvalidation(recentlyUpdatedKeys, keyVersions);
        }
        
        System.out.println("📡 " + nodeId + " gossip round " + gossipRounds + 
                         " to " + selectedPeers.size() + " peers");
    }
    
    private List<String> selectGossipPeers() {
        List<String> availablePeers = new ArrayList<>(peerNodes);
        Collections.shuffle(availablePeers, random);
        
        int peerCount = Math.min(gossipFanout, availablePeers.size());
        return availablePeers.subList(0, peerCount);
    }
    
    private List<String> getRecentlyUpdatedKeys() {
        long cutoffTime = System.currentTimeMillis() - gossipInterval;
        List<String> recentKeys = new ArrayList<>();
        
        for (CacheEntry entry : cache.values()) {
            if (entry.getTimestamp() > cutoffTime) {
                recentKeys.add(entry.getKey());
            }
        }
        
        return recentKeys;
    }
    
    private void gossipInvalidation(List<String> keys, Map<String, Long> keyVersions) {
        if (keys.isEmpty() || peerNodes.isEmpty()) {
            return;
        }
        
        List<String> targets = selectGossipPeers();
        int messageId = ++messageCounter;
        
        InvalidationMessage message = new InvalidationMessage(nodeId, keys, keyVersions, messageId);
        
        for (String peerId : targets) {
            sendInvalidationMessage(peerId, message);
        }
        
        invalidationsSent += targets.size();
    }
    
    private void sendInvalidationMessage(String peerId, InvalidationMessage message) {
        // Simulate network transmission
        scheduler.schedule(() -> {
            // Simulate the peer receiving this message
            processInvalidationMessage(message);
        }, random.nextInt(200), TimeUnit.MILLISECONDS);
        
        System.out.println("📤 Sending invalidation from " + nodeId + " to " + peerId + 
                         " (keys: " + message.getInvalidatedKeys().size() + ")");
    }
    
    public void processInvalidationMessage(InvalidationMessage message) {
        // Avoid processing duplicate messages
        if (processedMessages.contains(message.getMessageId())) {
            return;
        }
        processedMessages.add(message.getMessageId());
        
        invalidationsReceived++;
        
        System.out.println("📥 " + nodeId + " received invalidation from " + message.getNodeId() + 
                         " (keys: " + message.getInvalidatedKeys().size() + ")");
        
        boolean hasUpdates = false;
        List<String> keysToInvalidate = new ArrayList<>();
        
        for (String key : message.getInvalidatedKeys()) {
            Long messageVersion = message.getKeyVersions().get(key);
            CacheEntry localEntry = cache.get(key);
            
            if (messageVersion != null) {
                if (localEntry == null) {
                    // We don't have this key, nothing to invalidate
                    continue;
                }
                
                if (messageVersion > localEntry.getVersion()) {
                    // Remote version is newer, invalidate local entry
                    localEntry.setState(CacheEntryState.STALE);
                    keysToInvalidate.add(key);
                    hasUpdates = true;
                    
                    System.out.println("🔄 " + nodeId + " invalidated stale entry: " + key + 
                                     " (local v" + localEntry.getVersion() + 
                                     " < remote v" + messageVersion + ")");
                }
            }
        }
        
        // Remove invalidated entries
        for (String key : keysToInvalidate) {
            cache.remove(key);
        }
        
        // Update version vector
        String senderId = message.getNodeId();
        Long senderVersion = versionVector.get(senderId);
        if (senderVersion == null || message.getTimestamp() > senderVersion) {
            versionVector.put(senderId, message.getTimestamp());
        }
        
        // Forward invalidation to other peers (gossip propagation)
        if (hasUpdates && !keysToInvalidate.isEmpty()) {
            scheduler.schedule(() -> {
                Map<String, Long> forwardVersions = new HashMap<>();
                for (String key : keysToInvalidate) {
                    forwardVersions.put(key, message.getKeyVersions().get(key));
                }
                gossipInvalidation(keysToInvalidate, forwardVersions);
            }, 500, TimeUnit.MILLISECONDS);
        }
    }
    
    private void cleanupExpiredEntries() {
        int removedCount = 0;
        List<String> expiredKeys = new ArrayList<>();
        
        for (Map.Entry<String, CacheEntry> entry : cache.entrySet()) {
            if (entry.getValue().isExpired() || 
                entry.getValue().getState() == CacheEntryState.INVALIDATED) {
                expiredKeys.add(entry.getKey());
            }
        }
        
        for (String key : expiredKeys) {
            cache.remove(key);
            removedCount++;
        }
        
        if (removedCount > 0) {
            System.out.println("🧹 " + nodeId + " cleaned up " + removedCount + " expired entries");
        }
    }
    
    public void printCacheStats() {
        double hitRate = (double) cacheHits / (cacheHits + cacheMisses);
        
        System.out.println("\n📊 Cache Statistics for " + nodeId + ":");
        System.out.println("  Cache size: " + cache.size());
        System.out.println("  Cache hits: " + cacheHits);
        System.out.println("  Cache misses: " + cacheMisses);
        System.out.println("  Hit rate: " + String.format("%.2f%%", hitRate * 100));
        System.out.println("  Invalidations sent: " + invalidationsSent);
        System.out.println("  Invalidations received: " + invalidationsReceived);
        System.out.println("  Gossip rounds: " + gossipRounds);
        System.out.println("  Peers: " + peerNodes.size());
    }
    
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
        }
    }
    
    // Main method for testing
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🇮🇳 Flipkart Distributed Cache Gossip Simulation");
        System.out.println("=" + "=".repeat(55));
        
        // Create Flipkart cache nodes in different regions
        List<DistributedCacheGossip> cacheNodes = Arrays.asList(
            new DistributedCacheGossip("cache-mumbai-01", "West"),
            new DistributedCacheGossip("cache-delhi-01", "North"),
            new DistributedCacheGossip("cache-bangalore-01", "South"),
            new DistributedCacheGossip("cache-chennai-01", "South"),
            new DistributedCacheGossip("cache-kolkata-01", "East")
        );
        
        // Setup peer connections
        for (int i = 0; i < cacheNodes.size(); i++) {
            for (int j = 0; j < cacheNodes.size(); j++) {
                if (i != j) {
                    cacheNodes.get(i).addPeer(cacheNodes.get(j).nodeId);
                }
            }
        }
        
        System.out.println("\nCache network topology created. Starting simulation...\n");
        
        // Simulate cache operations
        DistributedCacheGossip mumbaiCache = cacheNodes.get(0);
        DistributedCacheGossip delhiCache = cacheNodes.get(1);
        DistributedCacheGossip bangaloreCache = cacheNodes.get(2);
        
        // Add some products to different caches
        mumbaiCache.put("product_001", new ProductInfo("001", "Samsung Galaxy S23", 75000, 50, "Electronics"));
        mumbaiCache.put("product_002", new ProductInfo("002", "iPhone 14", 80000, 30, "Electronics"));
        
        delhiCache.put("product_003", new ProductInfo("003", "Dell Laptop", 55000, 25, "Computers"));
        bangaloreCache.put("product_004", new ProductInfo("004", "Nike Shoes", 8000, 100, "Fashion"));
        
        Thread.sleep(2000);
        
        // Simulate cache access from different nodes
        System.out.println("\n--- Cache Access Simulation ---");
        
        // Access products from different nodes
        mumbaiCache.get("product_001"); // Local hit
        delhiCache.get("product_001");  // Cache miss, load from DB
        bangaloreCache.get("product_002"); // Cache miss, load from DB
        
        Thread.sleep(3000);
        
        // Simulate product price update (invalidation)
        System.out.println("\n--- Price Update Simulation ---");
        
        // Update product price in Mumbai cache
        ProductInfo updatedProduct = new ProductInfo("001", "Samsung Galaxy S23", 72000, 50, "Electronics");
        mumbaiCache.put("product_001", updatedProduct); // This will trigger invalidation gossip
        
        Thread.sleep(5000);
        
        // Access updated product from other nodes
        delhiCache.get("product_001");     // Should get updated price
        bangaloreCache.get("product_001"); // Should get updated price
        
        Thread.sleep(3000);
        
        // Print cache statistics
        System.out.println("\n📊 Final Cache Statistics:");
        for (DistributedCacheGossip node : cacheNodes) {
            node.printCacheStats();
        }
        
        // Cleanup
        for (DistributedCacheGossip node : cacheNodes) {
            node.shutdown();
        }
        
        System.out.println("\nSimulation completed!");
    }
}