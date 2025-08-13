import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

/**
 * Distributed Caching System Implementation
 * जैसे कि Flipkart के product catalog caching में use होता है
 * 
 * यह example दिखाता है कि कैसे multiple cache nodes के बीच data को distribute करते हैं
 * consistent hashing और replication के साथ। Indian e-commerce companies
 * जैसे Flipkart, Amazon India इसे use करती हैं high-performance product serving के लिए।
 * 
 * Production context: Flipkart caches 100M+ products across distributed cache cluster
 * Scale: Handles millions of requests per second during Big Billion Days
 * Cost benefit: 90% reduction in database load, sub-millisecond response times
 */

/**
 * Cache entry with metadata
 */
class CacheEntry {
    private final String key;
    private final Object value;
    private final long creationTime;
    private final long expirationTime;
    private final int version;
    private volatile long lastAccessTime;
    private final AtomicLong accessCount;
    
    public CacheEntry(String key, Object value, long ttlMillis, int version) {
        this.key = key;
        this.value = value;
        this.creationTime = System.currentTimeMillis();
        this.expirationTime = creationTime + ttlMillis;
        this.version = version;
        this.lastAccessTime = creationTime;
        this.accessCount = new AtomicLong(0);
    }
    
    public boolean isExpired() {
        return System.currentTimeMillis() > expirationTime;
    }
    
    public void recordAccess() {
        lastAccessTime = System.currentTimeMillis();
        accessCount.incrementAndGet();
    }
    
    // Getters
    public String getKey() { return key; }
    public Object getValue() { return value; }
    public long getCreationTime() { return creationTime; }
    public long getExpirationTime() { return expirationTime; }
    public int getVersion() { return version; }
    public long getLastAccessTime() { return lastAccessTime; }
    public long getAccessCount() { return accessCount.get(); }
    
    @Override
    public String toString() {
        return String.format("CacheEntry{key='%s', version=%d, accesses=%d, expired=%s}",
                           key, version, accessCount.get(), isExpired());
    }
}

/**
 * Flipkart product information for caching
 */
class FlipkartProduct {
    public final String productId;
    public final String title;
    public final String category;
    public final double price;
    public final double rating;
    public final int reviewCount;
    public final boolean inStock;
    public final String sellerName;
    public final List<String> images;
    public final Map<String, String> specifications;
    
    public FlipkartProduct(String productId, String title, String category, 
                          double price, double rating, int reviewCount, 
                          boolean inStock, String sellerName) {
        this.productId = productId;
        this.title = title;
        this.category = category;
        this.price = price;
        this.rating = rating;
        this.reviewCount = reviewCount;
        this.inStock = inStock;
        this.sellerName = sellerName;
        this.images = new ArrayList<>();
        this.specifications = new HashMap<>();
    }
    
    @Override
    public String toString() {
        return String.format("Product{id=%s, title='%s', price=₹%.2f, rating=%.1f, inStock=%s}",
                           productId, title, price, rating, inStock);
    }
}

/**
 * Consistent hashing ring for cache distribution
 */
class ConsistentHashRing {
    private final int virtualNodes;
    private final TreeMap<Long, String> ring;
    private final Map<String, CacheNode> nodes;
    
    public ConsistentHashRing(int virtualNodes) {
        this.virtualNodes = virtualNodes;
        this.ring = new TreeMap<>();
        this.nodes = new ConcurrentHashMap<>();
    }
    
    public void addNode(CacheNode node) {
        nodes.put(node.getNodeId(), node);
        
        for (int i = 0; i < virtualNodes; i++) {
            String virtualNodeKey = node.getNodeId() + ":" + i;
            long hash = hash(virtualNodeKey);
            ring.put(hash, node.getNodeId());
        }
        
        System.out.printf("Added cache node %s to ring with %d virtual nodes%n", 
                         node.getNodeId(), virtualNodes);
    }
    
    public void removeNode(String nodeId) {
        CacheNode node = nodes.remove(nodeId);
        if (node == null) return;
        
        for (int i = 0; i < virtualNodes; i++) {
            String virtualNodeKey = nodeId + ":" + i;
            long hash = hash(virtualNodeKey);
            ring.remove(hash);
        }
        
        System.out.printf("Removed cache node %s from ring%n", nodeId);
    }
    
    public CacheNode getNode(String key) {
        if (ring.isEmpty()) return null;
        
        long hash = hash(key);
        Map.Entry<Long, String> entry = ring.ceilingEntry(hash);
        
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        return nodes.get(entry.getValue());
    }
    
    public List<CacheNode> getReplicaNodes(String key, int replicationFactor) {
        List<CacheNode> replicas = new ArrayList<>();
        if (ring.isEmpty()) return replicas;
        
        long hash = hash(key);
        Set<String> seenNodes = new HashSet<>();
        
        Map.Entry<Long, String> entry = ring.ceilingEntry(hash);
        if (entry == null) {
            entry = ring.firstEntry();
        }
        
        Iterator<Map.Entry<Long, String>> iterator = ring.tailMap(entry.getKey()).entrySet().iterator();
        
        // Get replicas in ring order
        while (replicas.size() < replicationFactor && seenNodes.size() < nodes.size()) {
            if (!iterator.hasNext()) {
                iterator = ring.entrySet().iterator();
            }
            
            Map.Entry<Long, String> current = iterator.next();
            String nodeId = current.getValue();
            
            if (!seenNodes.contains(nodeId)) {
                seenNodes.add(nodeId);
                CacheNode node = nodes.get(nodeId);
                if (node != null) {
                    replicas.add(node);
                }
            }
        }
        
        return replicas;
    }
    
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes(StandardCharsets.UTF_8));
            
            long hash = 0;
            for (int i = 0; i < 8; i++) {
                hash = (hash << 8) | (digest[i] & 0xFF);
            }
            return hash;
        } catch (Exception e) {
            return key.hashCode();
        }
    }
    
    public int getNodeCount() {
        return nodes.size();
    }
    
    public Collection<CacheNode> getAllNodes() {
        return nodes.values();
    }
}

/**
 * Individual cache node in the distributed system
 */
class CacheNode {
    private final String nodeId;
    private final String host;
    private final int port;
    private final long maxSize;
    
    private final Map<String, CacheEntry> cache;
    private final AtomicLong hitCount;
    private final AtomicLong missCount;
    private final AtomicLong evictionCount;
    private final ScheduledExecutorService cleanupExecutor;
    
    public CacheNode(String nodeId, String host, int port, long maxSize) {
        this.nodeId = nodeId;
        this.host = host;
        this.port = port;
        this.maxSize = maxSize;
        
        this.cache = new ConcurrentHashMap<>();
        this.hitCount = new AtomicLong(0);
        this.missCount = new AtomicLong(0);
        this.evictionCount = new AtomicLong(0);
        
        this.cleanupExecutor = Executors.newSingleThreadScheduledExecutor();
        
        // Start cleanup task
        cleanupExecutor.scheduleAtFixedRate(this::cleanupExpiredEntries, 30, 30, TimeUnit.SECONDS);
    }
    
    public boolean put(String key, Object value, long ttlMillis) {
        return put(key, value, ttlMillis, 1);
    }
    
    public boolean put(String key, Object value, long ttlMillis, int version) {
        if (cache.size() >= maxSize) {
            evictLRU();
        }
        
        CacheEntry entry = new CacheEntry(key, value, ttlMillis, version);
        cache.put(key, entry);
        
        System.out.printf("[%s] Cached: %s (TTL: %d ms)%n", nodeId, key, ttlMillis);
        return true;
    }
    
    public Object get(String key) {
        CacheEntry entry = cache.get(key);
        
        if (entry == null) {
            missCount.incrementAndGet();
            return null;
        }
        
        if (entry.isExpired()) {
            cache.remove(key);
            missCount.incrementAndGet();
            return null;
        }
        
        entry.recordAccess();
        hitCount.incrementAndGet();
        return entry.getValue();
    }
    
    public boolean delete(String key) {
        boolean removed = cache.remove(key) != null;
        if (removed) {
            System.out.printf("[%s] Deleted: %s%n", nodeId, key);
        }
        return removed;
    }
    
    public boolean contains(String key) {
        CacheEntry entry = cache.get(key);
        return entry != null && !entry.isExpired();
    }
    
    private void evictLRU() {
        if (cache.isEmpty()) return;
        
        String oldestKey = null;
        long oldestAccess = Long.MAX_VALUE;
        
        for (CacheEntry entry : cache.values()) {
            if (entry.getLastAccessTime() < oldestAccess) {
                oldestAccess = entry.getLastAccessTime();
                oldestKey = entry.getKey();
            }
        }
        
        if (oldestKey != null) {
            cache.remove(oldestKey);
            evictionCount.incrementAndGet();
            System.out.printf("[%s] Evicted LRU entry: %s%n", nodeId, oldestKey);
        }
    }
    
    private void cleanupExpiredEntries() {
        List<String> expiredKeys = new ArrayList<>();
        
        for (CacheEntry entry : cache.values()) {
            if (entry.isExpired()) {
                expiredKeys.add(entry.getKey());
            }
        }
        
        for (String key : expiredKeys) {
            cache.remove(key);
        }
        
        if (!expiredKeys.isEmpty()) {
            System.out.printf("[%s] Cleaned up %d expired entries%n", nodeId, expiredKeys.size());
        }
    }
    
    public CacheStats getStats() {
        long total = hitCount.get() + missCount.get();
        double hitRatio = total > 0 ? (double) hitCount.get() / total : 0.0;
        
        return new CacheStats(
            nodeId,
            cache.size(),
            hitCount.get(),
            missCount.get(),
            hitRatio,
            evictionCount.get()
        );
    }
    
    public void shutdown() {
        cleanupExecutor.shutdown();
    }
    
    // Getters
    public String getNodeId() { return nodeId; }
    public String getHost() { return host; }
    public int getPort() { return port; }
    
    public static class CacheStats {
        public final String nodeId;
        public final int size;
        public final long hits;
        public final long misses;
        public final double hitRatio;
        public final long evictions;
        
        public CacheStats(String nodeId, int size, long hits, long misses, 
                         double hitRatio, long evictions) {
            this.nodeId = nodeId;
            this.size = size;
            this.hits = hits;
            this.misses = misses;
            this.hitRatio = hitRatio;
            this.evictions = evictions;
        }
        
        @Override
        public String toString() {
            return String.format("Stats{node=%s, size=%d, hits=%d, misses=%d, ratio=%.2f%%, evictions=%d}",
                               nodeId, size, hits, misses, hitRatio * 100, evictions);
        }
    }
}

/**
 * Distributed cache manager for Flipkart-style product caching
 */
class FlipkartDistributedCache {
    private final ConsistentHashRing hashRing;
    private final int replicationFactor;
    private final long defaultTTL;
    
    public FlipkartDistributedCache(int replicationFactor, long defaultTTL) {
        this.hashRing = new ConsistentHashRing(5); // 5 virtual nodes per physical node
        this.replicationFactor = replicationFactor;
        this.defaultTTL = defaultTTL;
    }
    
    public void addCacheNode(CacheNode node) {
        hashRing.addNode(node);
    }
    
    public void removeCacheNode(String nodeId) {
        hashRing.removeNode(nodeId);
    }
    
    public boolean cacheProduct(FlipkartProduct product) {
        return cacheProduct(product, defaultTTL);
    }
    
    public boolean cacheProduct(FlipkartProduct product, long ttlMillis) {
        String key = "product:" + product.productId;
        List<CacheNode> replicas = hashRing.getReplicaNodes(key, replicationFactor);
        
        int successCount = 0;
        for (CacheNode node : replicas) {
            if (node.put(key, product, ttlMillis)) {
                successCount++;
            }
        }
        
        // Consider successful if majority of replicas are cached
        boolean success = successCount >= (replicationFactor / 2) + 1;
        
        if (success) {
            System.out.printf("Successfully cached product %s on %d/%d nodes%n", 
                             product.productId, successCount, replicas.size());
        }
        
        return success;
    }
    
    public FlipkartProduct getProduct(String productId) {
        String key = "product:" + productId;
        List<CacheNode> replicas = hashRing.getReplicaNodes(key, replicationFactor);
        
        // Try to read from replicas until we get a hit
        for (CacheNode node : replicas) {
            Object cached = node.get(key);
            if (cached instanceof FlipkartProduct) {
                System.out.printf("Cache hit for product %s on node %s%n", productId, node.getNodeId());
                return (FlipkartProduct) cached;
            }
        }
        
        System.out.printf("Cache miss for product %s%n", productId);
        return null;
    }
    
    public boolean deleteProduct(String productId) {
        String key = "product:" + productId;
        List<CacheNode> replicas = hashRing.getReplicaNodes(key, replicationFactor);
        
        int deleteCount = 0;
        for (CacheNode node : replicas) {
            if (node.delete(key)) {
                deleteCount++;
            }
        }
        
        return deleteCount > 0;
    }
    
    /**
     * Cache popular products for Big Billion Day preparation
     */
    public void preloadPopularProducts(List<FlipkartProduct> products) {
        System.out.printf("Preloading %d popular products for Big Billion Day...%n", products.size());
        
        int cached = 0;
        for (FlipkartProduct product : products) {
            // Popular products get longer TTL
            long popularTTL = defaultTTL * 4; // 4x longer for popular items
            
            if (cacheProduct(product, popularTTL)) {
                cached++;
            }
        }
        
        System.out.printf("Preloaded %d/%d products successfully%n", cached, products.size());
    }
    
    public void printClusterStats() {
        System.out.println("\n📊 Distributed Cache Cluster Statistics:");
        System.out.printf("Total nodes: %d%n", hashRing.getNodeCount());
        System.out.printf("Replication factor: %d%n", replicationFactor);
        
        for (CacheNode node : hashRing.getAllNodes()) {
            CacheNode.CacheStats stats = node.getStats();
            System.out.println("  " + stats);
        }
    }
    
    public void shutdown() {
        for (CacheNode node : hashRing.getAllNodes()) {
            node.shutdown();
        }
    }
}

/**
 * Main demonstration class
 */
public class FlipkartDistributedCacheDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🛒 Flipkart Distributed Product Cache System");
        System.out.println("=" .repeat(60));
        
        // Initialize distributed cache
        FlipkartDistributedCache distributedCache = new FlipkartDistributedCache(
            3, // Replication factor
            300000 // 5 minutes default TTL
        );
        
        // Add cache nodes (simulating different data centers)
        System.out.println("\n🏢 Setting up cache nodes across India...");
        
        CacheNode mumbaiNode = new CacheNode("mumbai-cache-01", "10.1.1.10", 11211, 1000);
        CacheNode delhiNode = new CacheNode("delhi-cache-01", "10.1.2.10", 11211, 1000);
        CacheNode bangaloreNode = new CacheNode("bangalore-cache-01", "10.1.3.10", 11211, 1000);
        CacheNode hyderabadNode = new CacheNode("hyderabad-cache-01", "10.1.4.10", 11211, 1000);
        
        distributedCache.addCacheNode(mumbaiNode);
        distributedCache.addCacheNode(delhiNode);
        distributedCache.addCacheNode(bangaloreNode);
        distributedCache.addCacheNode(hyderabadNode);
        
        System.out.println("✅ All cache nodes added to cluster");
        
        // Create sample Flipkart products
        List<FlipkartProduct> products = createSampleProducts();
        
        // Cache popular products for Big Billion Day
        System.out.println("\n🎯 Caching products for Big Billion Day...");
        List<FlipkartProduct> popularProducts = products.subList(0, 5);
        distributedCache.preloadPopularProducts(popularProducts);
        
        // Cache remaining products
        System.out.println("\n📦 Caching regular products...");
        for (int i = 5; i < products.size(); i++) {
            distributedCache.cacheProduct(products.get(i));
            Thread.sleep(50); // Simulate caching delay
        }
        
        // Simulate customer browsing
        System.out.println("\n👥 Simulating customer product lookups...");
        
        String[] lookupProducts = {
            "FLIP001", "FLIP002", "FLIP005", "FLIP008", 
            "FLIP003", "FLIP001", "FLIP007", "FLIP002" // Some repeats to show cache hits
        };
        
        for (String productId : lookupProducts) {
            System.out.printf("\n🔍 Customer looking for product: %s%n", productId);
            FlipkartProduct product = distributedCache.getProduct(productId);
            
            if (product != null) {
                System.out.printf("✅ Found: %s%n", product);
            } else {
                System.out.printf("❌ Product not found in cache, would query database%n");
            }
            
            Thread.sleep(100);
        }
        
        // Show cache statistics
        distributedCache.printClusterStats();
        
        // Simulate node failure
        System.out.println("\n💥 Simulating Mumbai cache node failure...");
        distributedCache.removeCacheNode("mumbai-cache-01");
        mumbaiNode.shutdown();
        
        // Test data availability after node failure
        System.out.println("\n🔄 Testing cache availability after node failure...");
        for (int i = 0; i < 3; i++) {
            String productId = "FLIP00" + (i + 1);
            FlipkartProduct product = distributedCache.getProduct(productId);
            
            if (product != null) {
                System.out.printf("✅ Product %s still available (fault tolerance working)%n", productId);
            } else {
                System.out.printf("❌ Product %s not available%n", productId);
            }
        }
        
        // Final statistics
        System.out.println("\n📈 Final Cache Cluster Statistics:");
        distributedCache.printClusterStats();
        
        // Production insights
        System.out.println("\n💡 Production Insights:");
        System.out.println("- Distributed caching reduces database load by 90%+ during peak traffic");
        System.out.println("- Consistent hashing ensures even data distribution across cache nodes");
        System.out.println("- Replication provides fault tolerance - data survives node failures");
        System.out.println("- TTL-based expiration ensures fresh product information");
        System.out.println("- Virtual nodes enable smooth scaling when adding/removing cache servers");
        System.out.println("- Big Billion Day traffic handled through strategic preloading");
        System.out.println("- Sub-millisecond response times improve customer experience");
        System.out.println("- Cost-effective horizontal scaling across data centers");
        
        // Cleanup
        System.out.println("\n🧹 Shutting down cache cluster...");
        distributedCache.shutdown();
        
        System.out.println("Demo completed!");
    }
    
    private static List<FlipkartProduct> createSampleProducts() {
        List<FlipkartProduct> products = new ArrayList<>();
        
        // Popular electronics for Big Billion Day
        products.add(new FlipkartProduct("FLIP001", "iPhone 15 Pro", "Electronics", 
                                       134900.0, 4.5, 2543, true, "Apple India"));
        
        products.add(new FlipkartProduct("FLIP002", "Samsung Galaxy S24 Ultra", "Electronics", 
                                       124999.0, 4.4, 1876, true, "Samsung India"));
        
        products.add(new FlipkartProduct("FLIP003", "OnePlus 12", "Electronics", 
                                       64999.0, 4.3, 3421, true, "OnePlus India"));
        
        products.add(new FlipkartProduct("FLIP004", "MacBook Air M3", "Electronics", 
                                       114900.0, 4.6, 987, true, "Apple India"));
        
        products.add(new FlipkartProduct("FLIP005", "Dell XPS 13", "Electronics", 
                                       89990.0, 4.2, 654, true, "Dell India"));
        
        // Fashion items
        products.add(new FlipkartProduct("FLIP006", "Levi's 511 Slim Jeans", "Fashion", 
                                       2999.0, 4.1, 8765, true, "Levi's India"));
        
        products.add(new FlipkartProduct("FLIP007", "Nike Air Max 270", "Fashion", 
                                       8995.0, 4.3, 2341, true, "Nike India"));
        
        products.add(new FlipkartProduct("FLIP008", "Woodland Leather Boots", "Fashion", 
                                       3499.0, 4.0, 1567, true, "Woodland"));
        
        // Home appliances
        products.add(new FlipkartProduct("FLIP009", "LG 43-inch 4K Smart TV", "Home", 
                                       32999.0, 4.2, 5432, true, "LG Electronics"));
        
        products.add(new FlipkartProduct("FLIP010", "Voltas 1.5 Ton AC", "Home", 
                                       28999.0, 3.9, 2876, true, "Voltas"));
        
        return products;
    }
}