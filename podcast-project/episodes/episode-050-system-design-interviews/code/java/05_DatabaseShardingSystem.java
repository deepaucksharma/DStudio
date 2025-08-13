/**
 * Database Sharding System - Episode 50: System Design Interview Mastery
 * Flipkart Product Catalog Sharding - Mumbai Railway Network Distribution
 * 
 * Database Sharding जैसे Mumbai की railway lines हैं -
 * Central, Western, Harbour - हर line अपना area handle करती है
 * 
 * Author: Hindi Podcast Series
 * Topic: Horizontal Database Partitioning and Sharding
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

/**
 * Database shard configuration - मुंबई railway line configuration
 */
class ShardConfig {
    private final String shardId;
    private final String database;
    private final String host;
    private final int port;
    private final int weight;
    private final String region;
    private boolean isHealthy;
    private final Map<String, Object> metadata;
    
    // Performance metrics
    private final AtomicLong queryCount = new AtomicLong(0);
    private final AtomicLong errorCount = new AtomicLong(0);
    private volatile double avgResponseTime = 0.0;
    
    public ShardConfig(String shardId, String database, String host, int port, int weight, String region) {
        this.shardId = shardId;
        this.database = database;
        this.host = host;
        this.port = port;
        this.weight = weight;
        this.region = region;
        this.isHealthy = true;
        this.metadata = new ConcurrentHashMap<>();
    }
    
    // Getters
    public String getShardId() { return shardId; }
    public String getDatabase() { return database; }
    public String getHost() { return host; }
    public int getPort() { return port; }
    public int getWeight() { return weight; }
    public String getRegion() { return region; }
    public boolean isHealthy() { return isHealthy; }
    public void setHealthy(boolean healthy) { this.isHealthy = healthy; }
    
    // Metrics
    public long getQueryCount() { return queryCount.get(); }
    public long getErrorCount() { return errorCount.get(); }
    public double getAvgResponseTime() { return avgResponseTime; }
    
    public void incrementQueryCount() { queryCount.incrementAndGet(); }
    public void incrementErrorCount() { errorCount.incrementAndGet(); }
    public void updateResponseTime(double responseTime) {
        this.avgResponseTime = (avgResponseTime + responseTime) / 2.0;
    }
    
    public double getLoadScore() {
        if (!isHealthy) return Double.MAX_VALUE;
        return queryCount.get() / (double) weight;
    }
    
    @Override
    public String toString() {
        return String.format("Shard{id='%s', db='%s', host='%s:%d', region='%s', healthy=%b, queries=%d}", 
                shardId, database, host, port, region, isHealthy, queryCount.get());
    }
}

/**
 * Sharding strategies - Mumbai railway line distribution strategies
 */
enum ShardingStrategy {
    HASH_BASED,      // Hash key पर based - Customer ID hash
    RANGE_BASED,     // Range partition - Product ID ranges
    DIRECTORY_BASED, // Lookup table - City wise distribution
    GEOGRAPHIC,      // Location based - Mumbai zones
    CONSISTENT_HASH  // Ring based distribution
}

/**
 * Shard key extractor - मुख्य sharding key निकालना
 */
interface ShardKeyExtractor {
    String extractKey(Object entity);
}

/**
 * Query router - Query को सही shard पर route करना
 */
class QueryRouter {
    private final ShardingStrategy strategy;
    private final List<ShardConfig> shards;
    private final ShardKeyExtractor keyExtractor;
    private final MessageDigest hasher;
    
    // Range-based sharding maps
    private final TreeMap<String, ShardConfig> rangeMap = new TreeMap<>();
    
    // Directory-based lookup
    private final Map<String, ShardConfig> directoryMap = new ConcurrentHashMap<>();
    
    // Consistent hashing ring
    private final TreeMap<Long, ShardConfig> hashRing = new TreeMap<>();
    
    public QueryRouter(ShardingStrategy strategy, List<ShardConfig> shards, ShardKeyExtractor keyExtractor) {
        this.strategy = strategy;
        this.shards = new ArrayList<>(shards);
        this.keyExtractor = keyExtractor;
        
        try {
            this.hasher = MessageDigest.getInstance("MD5");
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("MD5 not available", e);
        }
        
        initializeShardingMaps();
    }
    
    private void initializeShardingMaps() {
        switch (strategy) {
            case RANGE_BASED:
                initializeRangeBasedSharding();
                break;
            case DIRECTORY_BASED:
                initializeDirectoryBasedSharding();
                break;
            case CONSISTENT_HASH:
                initializeConsistentHashing();
                break;
        }
    }
    
    private void initializeRangeBasedSharding() {
        // Mumbai Product ID ranges - A-F: Central, G-M: Western, N-Z: Harbour
        if (shards.size() >= 3) {
            rangeMap.put("A", shards.get(0)); // Central line - A to F
            rangeMap.put("G", shards.get(1)); // Western line - G to M  
            rangeMap.put("N", shards.get(2)); // Harbour line - N to Z
        }
        System.out.println("📊 Range-based sharding initialized - Mumbai railway zones");
    }
    
    private void initializeDirectoryBasedSharding() {
        // Mumbai area to shard mapping
        String[] centralAreas = {"CST", "DADAR", "KURLA", "THANE"};
        String[] westernAreas = {"CHURCHGATE", "BANDRA", "ANDHERI", "BORIVALI"};
        String[] harbourAreas = {"PANVEL", "VASHI", "NERUL", "BELAPUR"};
        
        if (shards.size() >= 3) {
            for (String area : centralAreas) {
                directoryMap.put(area, shards.get(0));
            }
            for (String area : westernAreas) {
                directoryMap.put(area, shards.get(1));
            }
            for (String area : harbourAreas) {
                directoryMap.put(area, shards.get(2));
            }
        }
        System.out.println("🗂️ Directory-based sharding initialized - Mumbai area mapping");
    }
    
    private void initializeConsistentHashing() {
        // Add multiple virtual nodes per shard for better distribution
        for (ShardConfig shard : shards) {
            for (int i = 0; i < 100; i++) {  // 100 virtual nodes per shard
                String virtualNodeId = shard.getShardId() + "-virtual-" + i;
                long hash = computeHash(virtualNodeId);
                hashRing.put(hash, shard);
            }
        }
        System.out.println("🔄 Consistent hashing initialized - " + hashRing.size() + " virtual nodes");
    }
    
    public ShardConfig routeQuery(Object entity) {
        String key = keyExtractor.extractKey(entity);
        
        switch (strategy) {
            case HASH_BASED:
                return hashBasedRouting(key);
            case RANGE_BASED:
                return rangeBasedRouting(key);
            case DIRECTORY_BASED:
                return directoryBasedRouting(key);
            case GEOGRAPHIC:
                return geographicRouting(entity);
            case CONSISTENT_HASH:
                return consistentHashRouting(key);
            default:
                return shards.get(0); // Fallback
        }
    }
    
    private ShardConfig hashBasedRouting(String key) {
        long hash = computeHash(key);
        int shardIndex = (int) (Math.abs(hash) % shards.size());
        return shards.get(shardIndex);
    }
    
    private ShardConfig rangeBasedRouting(String key) {
        if (key == null || key.isEmpty()) return shards.get(0);
        
        String firstChar = key.substring(0, 1).toUpperCase();
        Map.Entry<String, ShardConfig> entry = rangeMap.floorEntry(firstChar);
        return entry != null ? entry.getValue() : shards.get(0);
    }
    
    private ShardConfig directoryBasedRouting(String key) {
        return directoryMap.getOrDefault(key.toUpperCase(), shards.get(0));
    }
    
    private ShardConfig geographicRouting(Object entity) {
        // Extract location from entity - simplified
        if (entity instanceof Map) {
            Map<String, Object> map = (Map<String, Object>) entity;
            String location = (String) map.get("location");
            if (location != null) {
                return directoryBasedRouting(location);
            }
        }
        return hashBasedRouting(entity.toString());
    }
    
    private ShardConfig consistentHashRouting(String key) {
        long hash = computeHash(key);
        Map.Entry<Long, ShardConfig> entry = hashRing.ceilingEntry(hash);
        if (entry == null) {
            entry = hashRing.firstEntry(); // Wrap around
        }
        return entry != null ? entry.getValue() : shards.get(0);
    }
    
    private long computeHash(String key) {
        synchronized (hasher) {
            hasher.reset();
            byte[] hashBytes = hasher.digest(key.getBytes());
            long hash = 0;
            for (int i = 0; i < Math.min(8, hashBytes.length); i++) {
                hash = (hash << 8) | (hashBytes[i] & 0xFF);
            }
            return hash;
        }
    }
    
    public List<ShardConfig> getHealthyShards() {
        return shards.stream()
                .filter(ShardConfig::isHealthy)
                .sorted((a, b) -> Double.compare(a.getLoadScore(), b.getLoadScore()))
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
}

/**
 * Main Database Sharding Manager - Mumbai Railway Control Center
 */
public class DatabaseShardingSystem {
    
    private final String systemName;
    private final Map<String, ShardConfig> shardConfigs;
    private final QueryRouter queryRouter;
    private final ShardingStrategy strategy;
    
    // Metrics and monitoring
    private final AtomicLong totalQueries = new AtomicLong(0);
    private final AtomicLong crossShardQueries = new AtomicLong(0);
    private final Map<String, AtomicLong> queryDistribution = new ConcurrentHashMap<>();
    
    public DatabaseShardingSystem(String systemName, ShardingStrategy strategy, 
                                 List<ShardConfig> shards, ShardKeyExtractor keyExtractor) {
        this.systemName = systemName;
        this.strategy = strategy;
        this.shardConfigs = new ConcurrentHashMap<>();
        
        // Initialize shard configs
        for (ShardConfig shard : shards) {
            this.shardConfigs.put(shard.getShardId(), shard);
            this.queryDistribution.put(shard.getShardId(), new AtomicLong(0));
        }
        
        this.queryRouter = new QueryRouter(strategy, shards, keyExtractor);
        
        System.out.printf("🏗️ Database Sharding System '%s' initialized with %s strategy%n", 
                systemName, strategy);
        System.out.printf("📊 Configured %d shards across regions%n", shards.size());
    }
    
    /**
     * Execute query on appropriate shard - सही database पर query execute करना
     */
    public QueryResult executeQuery(String query, Object entity) {
        totalQueries.incrementAndGet();
        
        ShardConfig targetShard = queryRouter.routeQuery(entity);
        if (targetShard == null || !targetShard.isHealthy()) {
            return new QueryResult(false, "No healthy shard available", null, null);
        }
        
        // Track query distribution
        queryDistribution.get(targetShard.getShardId()).incrementAndGet();
        
        // Simulate query execution
        return executeQueryOnShard(query, entity, targetShard);
    }
    
    private QueryResult executeQueryOnShard(String query, Object entity, ShardConfig shard) {
        long startTime = System.currentTimeMillis();
        
        try {
            shard.incrementQueryCount();
            
            // Simulate query execution time
            double responseTime = simulateQueryExecution(query, shard);
            shard.updateResponseTime(responseTime);
            
            String result = String.format("Query executed on shard %s in %.2fms", 
                    shard.getShardId(), responseTime);
            
            return new QueryResult(true, result, shard.getShardId(), responseTime);
            
        } catch (Exception e) {
            shard.incrementErrorCount();
            return new QueryResult(false, "Query execution failed: " + e.getMessage(), 
                    shard.getShardId(), null);
        }
    }
    
    private double simulateQueryExecution(String query, ShardConfig shard) {
        // Simulate different query types with different response times
        double baseResponseTime = ThreadLocalRandom.current().nextDouble(10, 100);
        
        if (query.toLowerCase().contains("select")) {
            baseResponseTime *= 0.8; // SELECT queries are faster
        } else if (query.toLowerCase().contains("insert") || 
                  query.toLowerCase().contains("update")) {
            baseResponseTime *= 1.2; // Write queries are slower
        } else if (query.toLowerCase().contains("join")) {
            baseResponseTime *= 2.0; // Complex joins are much slower
        }
        
        // Add shard-specific latency based on region
        switch (shard.getRegion()) {
            case "mumbai":
                baseResponseTime *= 0.9; // Local region is faster
                break;
            case "bangalore":
                baseResponseTime *= 1.1; // Slight network delay
                break;
            case "delhi":
                baseResponseTime *= 1.3; // Higher latency
                break;
        }
        
        // Simulate processing time
        try {
            Thread.sleep((long) (baseResponseTime / 10)); // Scale down for demo
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return baseResponseTime;
    }
    
    /**
     * Execute cross-shard query - Multiple shards पर query
     */
    public List<QueryResult> executeCrossShardQuery(String query, List<Object> entities) {
        crossShardQueries.incrementAndGet();
        
        Map<ShardConfig, List<Object>> shardToEntities = new HashMap<>();
        
        // Group entities by target shard
        for (Object entity : entities) {
            ShardConfig targetShard = queryRouter.routeQuery(entity);
            if (targetShard != null && targetShard.isHealthy()) {
                shardToEntities.computeIfAbsent(targetShard, k -> new ArrayList<>()).add(entity);
            }
        }
        
        List<QueryResult> results = new ArrayList<>();
        
        // Execute query on each shard
        for (Map.Entry<ShardConfig, List<Object>> entry : shardToEntities.entrySet()) {
            ShardConfig shard = entry.getKey();
            List<Object> shardEntities = entry.getValue();
            
            String modifiedQuery = String.format("%s -- Batch size: %d", query, shardEntities.size());
            QueryResult result = executeQueryOnShard(modifiedQuery, shardEntities.get(0), shard);
            results.add(result);
        }
        
        return results;
    }
    
    /**
     * Add new shard - नई railway line add करना
     */
    public void addShard(ShardConfig newShard) {
        shardConfigs.put(newShard.getShardId(), newShard);
        queryDistribution.put(newShard.getShardId(), new AtomicLong(0));
        
        // In production, this would trigger resharding process
        System.out.printf("✅ New shard added: %s - Resharding required%n", newShard.getShardId());
    }
    
    /**
     * Remove shard - Railway line maintenance
     */
    public void removeShard(String shardId) {
        ShardConfig removedShard = shardConfigs.remove(shardId);
        if (removedShard != null) {
            queryDistribution.remove(shardId);
            System.out.printf("🔧 Shard removed: %s - Data migration required%n", shardId);
        }
    }
    
    /**
     * Rebalance shards - Load को evenly distribute करना
     */
    public void rebalanceShards() {
        System.out.println("⚖️ Starting shard rebalancing...");
        
        List<ShardConfig> healthyShards = queryRouter.getHealthyShards();
        
        for (ShardConfig shard : healthyShards) {
            double loadScore = shard.getLoadScore();
            System.out.printf("📊 Shard %s - Load Score: %.2f, Queries: %d, Avg Response: %.2fms%n",
                    shard.getShardId(), loadScore, shard.getQueryCount(), shard.getAvgResponseTime());
        }
        
        // Simulate rebalancing recommendations
        if (healthyShards.size() > 1) {
            ShardConfig leastLoaded = healthyShards.get(0);
            ShardConfig mostLoaded = healthyShards.get(healthyShards.size() - 1);
            
            double loadDifference = mostLoaded.getLoadScore() - leastLoaded.getLoadScore();
            if (loadDifference > 100) {
                System.out.printf("⚠️ High load imbalance detected! Consider migrating data from %s to %s%n",
                        mostLoaded.getShardId(), leastLoaded.getShardId());
            }
        }
    }
    
    /**
     * Get system statistics - Mumbai railway network performance
     */
    public ShardingStats getSystemStats() {
        ShardingStats stats = new ShardingStats();
        stats.systemName = this.systemName;
        stats.strategy = this.strategy.toString();
        stats.totalShards = shardConfigs.size();
        stats.healthyShards = (int) shardConfigs.values().stream().filter(ShardConfig::isHealthy).count();
        stats.totalQueries = totalQueries.get();
        stats.crossShardQueries = crossShardQueries.get();
        
        // Per-shard statistics
        stats.shardStats = new ArrayList<>();
        for (ShardConfig shard : shardConfigs.values()) {
            ShardStats shardStat = new ShardStats();
            shardStat.shardId = shard.getShardId();
            shardStat.region = shard.getRegion();
            shardStat.queryCount = shard.getQueryCount();
            shardStat.errorCount = shard.getErrorCount();
            shardStat.avgResponseTime = shard.getAvgResponseTime();
            shardStat.isHealthy = shard.isHealthy();
            shardStat.loadScore = shard.getLoadScore();
            
            stats.shardStats.add(shardStat);
        }
        
        return stats;
    }
    
    /**
     * Demonstrate Flipkart product catalog sharding
     */
    public static void demonstrateFlipkartSharding() {
        System.out.println("🛒 Flipkart Product Catalog Sharding Demo");
        System.out.println("=" + "=".repeat(60));
        
        // Create shards for different regions - Mumbai railway network inspired
        List<ShardConfig> shards = Arrays.asList(
            new ShardConfig("CENTRAL_SHARD", "flipkart_central", "central.mumbai.flipkart.db", 3306, 100, "mumbai"),
            new ShardConfig("WESTERN_SHARD", "flipkart_western", "western.mumbai.flipkart.db", 3306, 120, "mumbai"),
            new ShardConfig("HARBOUR_SHARD", "flipkart_harbour", "harbour.mumbai.flipkart.db", 3306, 80, "mumbai"),
            new ShardConfig("BANGALORE_SHARD", "flipkart_bangalore", "bangalore.flipkart.db", 3306, 90, "bangalore")
        );
        
        // Product ID based sharding key extractor
        ShardKeyExtractor productExtractor = entity -> {
            if (entity instanceof Map) {
                return (String) ((Map<?, ?>) entity).get("product_id");
            }
            return entity.toString();
        };
        
        // Test different sharding strategies
        ShardingStrategy[] strategies = {
            ShardingStrategy.HASH_BASED,
            ShardingStrategy.RANGE_BASED,
            ShardingStrategy.DIRECTORY_BASED,
            ShardingStrategy.CONSISTENT_HASH
        };
        
        for (ShardingStrategy strategy : strategies) {
            System.out.printf("%n🔄 Testing %s Sharding Strategy%n", strategy);
            System.out.println("-".repeat(50));
            
            DatabaseShardingSystem shardingSystem = new DatabaseShardingSystem(
                "FlipkartProductCatalog", strategy, shards, productExtractor);
            
            // Create sample products
            List<Map<String, Object>> products = Arrays.asList(
                Map.of("product_id", "APPLE_IPHONE_15", "category", "Electronics", "location", "CST"),
                Map.of("product_id", "SAMSUNG_GALAXY_S24", "category", "Electronics", "location", "BANDRA"),
                Map.of("product_id", "NIKE_AIR_MAX", "category", "Fashion", "location", "ANDHERI"),
                Map.of("product_id", "ADIDAS_ULTRABOOST", "category", "Fashion", "location", "DADAR"),
                Map.of("product_id", "BOAT_HEADPHONES", "category", "Electronics", "location", "THANE"),
                Map.of("product_id", "ONEPLUS_12", "category", "Electronics", "location", "NERUL")
            );
            
            // Execute queries for each product
            for (Map<String, Object> product : products) {
                String query = String.format("SELECT * FROM products WHERE product_id = '%s'", 
                        product.get("product_id"));
                QueryResult result = shardingSystem.executeQuery(query, product);
                
                if (result.success) {
                    System.out.printf("✅ %s → Shard: %s (%.2fms)%n", 
                            product.get("product_id"), result.shardId, result.responseTime);
                } else {
                    System.out.printf("❌ %s → Error: %s%n", 
                            product.get("product_id"), result.message);
                }
            }
            
            // Test cross-shard query
            System.out.printf("%n📊 Cross-shard analytics query...%n");
            List<QueryResult> crossShardResults = shardingSystem.executeCrossShardQuery(
                "SELECT category, COUNT(*) FROM products GROUP BY category", 
                new ArrayList<>(products));
            
            for (QueryResult result : crossShardResults) {
                System.out.printf("📈 Analytics from %s: %s%n", result.shardId, result.message);
            }
            
            // Show statistics
            ShardingStats stats = shardingSystem.getSystemStats();
            System.out.printf("%n📊 System Statistics:%n");
            System.out.printf("   Strategy: %s%n", stats.strategy);
            System.out.printf("   Total Queries: %d%n", stats.totalQueries);
            System.out.printf("   Cross-shard Queries: %d%n", stats.crossShardQueries);
            System.out.printf("   Healthy Shards: %d/%d%n", stats.healthyShards, stats.totalShards);
            
            // Rebalance analysis
            shardingSystem.rebalanceShards();
        }
    }
    
    public static void main(String[] args) {
        demonstrateFlipkartSharding();
        
        System.out.println("\n" + "=".repeat(80));
        System.out.println("✅ Database Sharding System Demo Complete!");
        System.out.println("📚 Key Concepts Demonstrated:");
        System.out.println("   • Hash-based sharding - Uniform distribution");
        System.out.println("   • Range-based sharding - Logical partitioning"); 
        System.out.println("   • Directory-based sharding - Lookup table approach");
        System.out.println("   • Consistent hashing - Minimal reshuffling");
        System.out.println("   • Cross-shard queries - Multi-shard operations");
        System.out.println("   • Load balancing and rebalancing");
        System.out.println("   • Performance monitoring and metrics");
        System.out.println("   • Production-ready for Flipkart scale");
    }
}

/**
 * Query execution result
 */
class QueryResult {
    final boolean success;
    final String message;
    final String shardId;
    final Double responseTime;
    
    public QueryResult(boolean success, String message, String shardId, Double responseTime) {
        this.success = success;
        this.message = message;
        this.shardId = shardId;
        this.responseTime = responseTime;
    }
}

/**
 * System statistics
 */
class ShardingStats {
    String systemName;
    String strategy;
    int totalShards;
    int healthyShards;
    long totalQueries;
    long crossShardQueries;
    List<ShardStats> shardStats;
}

/**
 * Individual shard statistics  
 */
class ShardStats {
    String shardId;
    String region;
    long queryCount;
    long errorCount;
    double avgResponseTime;
    boolean isHealthy;
    double loadScore;
}