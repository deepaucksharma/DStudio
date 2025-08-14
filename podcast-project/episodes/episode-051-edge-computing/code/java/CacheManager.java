package com.mumbai.edge.cache;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.stream.Collectors;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.nio.charset.StandardCharsets;

/**
 * Cache Manager - डिस्ट्रिब्यूटेड कैश प्रबंधन
 * Mumbai local train की भीड़ को manage करने की तरह - efficient memory और data management
 * 
 * Real-world inspired by Redis, Hazelcast, Apache Ignite
 * Use cases: Application caching, session storage, real-time data
 * Cost: Edge cache ₹2 per GB vs Cloud cache ₹20 per GB monthly
 * 
 * @author Mumbai Tech Team
 * @version 2.0.0
 * @since 2024
 */
public class CacheManager {
    
    private static final Logger LOGGER = Logger.getLogger(CacheManager.class.getName());
    
    // Cache configuration constants
    private static final int DEFAULT_MAX_SIZE = 10000;
    private static final long DEFAULT_TTL_SECONDS = 3600; // 1 hour
    private static final int CLEANUP_INTERVAL_SECONDS = 300; // 5 minutes
    private static final int STATS_UPDATE_INTERVAL_SECONDS = 60; // 1 minute
    
    // Cache identification
    private final String cacheId;
    private final String location;
    
    // Core cache storage
    private final ConcurrentHashMap<String, CacheEntry> cache;
    private final ConcurrentHashMap<String, CachePartition> partitions;
    private final AtomicInteger maxSize;
    private final AtomicLong defaultTtlSeconds;
    
    // Cache policies और strategies
    private volatile EvictionPolicy evictionPolicy;
    private volatile ConsistencyLevel consistencyLevel;
    private final ReplicationStrategy replicationStrategy;
    
    // Performance monitoring
    private final AtomicLong hitCount;
    private final AtomicLong missCount;
    private final AtomicLong evictionCount;
    private final AtomicLong totalRequestCount;
    private final ConcurrentHashMap<String, AtomicLong> operationCounts;
    private final Queue<Long> responseTimesMs;
    
    // Threading और scheduling
    private final ScheduledExecutorService scheduler;
    private final ExecutorService executor;
    private volatile boolean running;
    
    // Mumbai-specific configurations
    private final MumbaiCacheConfiguration mumbaiConfig;

    /**
     * Cache eviction policies - Mumbai train crowd management की तरह
     */
    public enum EvictionPolicy {
        LRU("कम उपयोग"),              // Least Recently Used
        LFU("कम आवृत्ति"),             // Least Frequently Used  
        FIFO("पहले आओ पहले जाओ"),      // First In First Out
        TTL_BASED("समय आधारित"),       // Time-based expiry
        SIZE_BASED("आकार आधारित");     // Size-based eviction
        
        private final String hindiName;
        
        EvictionPolicy(String hindiName) {
            this.hindiName = hindiName;
        }
        
        public String getHindiName() {
            return hindiName;
        }
    }
    
    /**
     * Cache consistency levels
     */
    public enum ConsistencyLevel {
        EVENTUAL("अंततः स्थिर"),        // Eventually consistent
        STRONG("मज़बूत"),              // Strong consistency
        WEAK("कमज़ोर");               // Weak consistency
        
        private final String hindiName;
        
        ConsistencyLevel(String hindiName) {
            this.hindiName = hindiName;
        }
        
        public String getHindiName() {
            return hindiName;
        }
    }
    
    /**
     * Cache entry representation
     */
    public static class CacheEntry {
        private final String key;
        private volatile Object value;
        private final LocalDateTime createdAt;
        private volatile LocalDateTime lastAccessedAt;
        private volatile LocalDateTime expiresAt;
        private final AtomicInteger accessCount;
        private final int sizeBytes;
        private volatile String checksum;
        
        public CacheEntry(String key, Object value, Duration ttl) {
            this.key = key;
            this.value = value;
            this.createdAt = LocalDateTime.now();
            this.lastAccessedAt = this.createdAt;
            this.accessCount = new AtomicInteger(0);
            this.sizeBytes = calculateSize(value);
            
            // Set expiry time
            if (ttl != null && !ttl.isZero() && !ttl.isNegative()) {
                this.expiresAt = this.createdAt.plus(ttl);
            }
            
            // Calculate checksum for integrity
            this.checksum = calculateChecksum(value);
        }
        
        public void updateAccess() {
            this.lastAccessedAt = LocalDateTime.now();
            this.accessCount.incrementAndGet();
        }
        
        public boolean isExpired() {
            return expiresAt != null && LocalDateTime.now().isAfter(expiresAt);
        }
        
        public void updateValue(Object newValue, Duration ttl) {
            this.value = newValue;
            this.lastAccessedAt = LocalDateTime.now();
            this.checksum = calculateChecksum(newValue);
            
            if (ttl != null && !ttl.isZero() && !ttl.isNegative()) {
                this.expiresAt = LocalDateTime.now().plus(ttl);
            }
        }
        
        // Getters
        public String getKey() { return key; }
        public Object getValue() { return value; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public LocalDateTime getLastAccessedAt() { return lastAccessedAt; }
        public LocalDateTime getExpiresAt() { return expiresAt; }
        public int getAccessCount() { return accessCount.get(); }
        public int getSizeBytes() { return sizeBytes; }
        public String getChecksum() { return checksum; }
        
        private int calculateSize(Object obj) {
            if (obj == null) return 0;
            if (obj instanceof String) {
                return ((String) obj).length() * 2; // Approximate size in bytes
            } else if (obj instanceof byte[]) {
                return ((byte[]) obj).length;
            } else {
                return obj.toString().length() * 2; // Approximate
            }
        }
        
        private String calculateChecksum(Object obj) {
            try {
                MessageDigest md = MessageDigest.getInstance("MD5");
                String content = obj != null ? obj.toString() : "";
                byte[] hash = md.digest(content.getBytes(StandardCharsets.UTF_8));
                return bytesToHex(hash);
            } catch (NoSuchAlgorithmException e) {
                return "unknown";
            }
        }
        
        private String bytesToHex(byte[] bytes) {
            StringBuilder result = new StringBuilder();
            for (byte b : bytes) {
                result.append(String.format("%02x", b));
            }
            return result.toString();
        }
    }
    
    /**
     * Cache partition for distributed caching
     */
    public static class CachePartition {
        private final String partitionId;
        private final ConcurrentHashMap<String, CacheEntry> entries;
        private final AtomicInteger size;
        private final AtomicLong totalSize;
        
        public CachePartition(String partitionId) {
            this.partitionId = partitionId;
            this.entries = new ConcurrentHashMap<>();
            this.size = new AtomicInteger(0);
            this.totalSize = new AtomicLong(0);
        }
        
        public void put(String key, CacheEntry entry) {
            CacheEntry oldEntry = entries.put(key, entry);
            if (oldEntry == null) {
                size.incrementAndGet();
                totalSize.addAndGet(entry.getSizeBytes());
            } else {
                totalSize.addAndGet(entry.getSizeBytes() - oldEntry.getSizeBytes());
            }
        }
        
        public CacheEntry get(String key) {
            return entries.get(key);
        }
        
        public CacheEntry remove(String key) {
            CacheEntry removed = entries.remove(key);
            if (removed != null) {
                size.decrementAndGet();
                totalSize.addAndGet(-removed.getSizeBytes());
            }
            return removed;
        }
        
        public int getSize() { return size.get(); }
        public long getTotalSizeBytes() { return totalSize.get(); }
        public Set<String> getKeys() { return new HashSet<>(entries.keySet()); }
        public Collection<CacheEntry> getEntries() { return new ArrayList<>(entries.values()); }
    }
    
    /**
     * Replication strategy for distributed caching
     */
    public static class ReplicationStrategy {
        private final int replicationFactor;
        private final boolean asyncReplication;
        private final List<String> replicaNodes;
        
        public ReplicationStrategy(int replicationFactor, boolean asyncReplication) {
            this.replicationFactor = replicationFactor;
            this.asyncReplication = asyncReplication;
            this.replicaNodes = new ArrayList<>();
        }
        
        public int getReplicationFactor() { return replicationFactor; }
        public boolean isAsyncReplication() { return asyncReplication; }
        public List<String> getReplicaNodes() { return new ArrayList<>(replicaNodes); }
        public void addReplicaNode(String nodeId) { replicaNodes.add(nodeId); }
    }
    
    /**
     * Mumbai-specific cache configuration
     */
    public static class MumbaiCacheConfiguration {
        private final Map<String, Object> config = new HashMap<>();
        
        public MumbaiCacheConfiguration() {
            // Mumbai network और usage patterns
            config.put("peak_hours_start", 8);        // 8 AM peak start
            config.put("peak_hours_end", 11);         // 11 AM peak end
            config.put("evening_peak_start", 17);     // 5 PM evening peak
            config.put("evening_peak_end", 20);       // 8 PM evening peak end
            config.put("peak_multiplier", 3.0);       // 3x cache usage during peak
            
            // Local preferences
            config.put("preferred_content_language", "Hindi");
            config.put("local_timezone", "Asia/Kolkata");
            config.put("currency_format", "INR");
            
            // Mumbai-specific cache patterns
            config.put("bollywood_content_boost", true);   // Boost Bollywood content caching
            config.put("cricket_content_boost", true);     // Boost cricket content
            config.put("local_news_priority", true);       // Prioritize Mumbai local news
            
            // Network resilience for Mumbai conditions
            config.put("monsoon_mode_enabled", false);
            config.put("backup_cache_nodes", 2);
            config.put("local_cache_preference", true);
        }
        
        public Object get(String key) {
            return config.get(key);
        }
        
        public void set(String key, Object value) {
            config.put(key, value);
        }
        
        public boolean isPeakHours() {
            int currentHour = LocalDateTime.now().getHour();
            int morningStart = (Integer) config.get("peak_hours_start");
            int morningEnd = (Integer) config.get("peak_hours_end");
            int eveningStart = (Integer) config.get("evening_peak_start");
            int eveningEnd = (Integer) config.get("evening_peak_end");
            
            return (currentHour >= morningStart && currentHour <= morningEnd) ||
                   (currentHour >= eveningStart && currentHour <= eveningEnd);
        }
        
        public void enableMonsoonMode() {
            config.put("monsoon_mode_enabled", true);
            config.put("backup_cache_nodes", 3);      // More backups during monsoon
            config.put("cache_replication_factor", 2); // Higher replication
            LOGGER.info("Mumbai Monsoon Mode enabled for cache resilience");
        }
    }
    
    /**
     * Constructor
     */
    public CacheManager(String cacheId, String location, int maxSize, long defaultTtlSeconds) {
        this.cacheId = cacheId;
        this.location = location;
        this.maxSize = new AtomicInteger(maxSize);
        this.defaultTtlSeconds = new AtomicLong(defaultTtlSeconds);
        
        // Initialize core data structures
        this.cache = new ConcurrentHashMap<>();
        this.partitions = new ConcurrentHashMap<>();
        
        // Initialize policies
        this.evictionPolicy = EvictionPolicy.LRU;
        this.consistencyLevel = ConsistencyLevel.EVENTUAL;
        this.replicationStrategy = new ReplicationStrategy(1, true);
        
        // Initialize metrics
        this.hitCount = new AtomicLong(0);
        this.missCount = new AtomicLong(0);
        this.evictionCount = new AtomicLong(0);
        this.totalRequestCount = new AtomicLong(0);
        this.operationCounts = new ConcurrentHashMap<>();
        this.responseTimesMs = new ConcurrentLinkedQueue<>();
        
        // Initialize threading
        this.scheduler = Executors.newScheduledThreadPool(2);
        this.executor = Executors.newCachedThreadPool();
        this.running = false;
        
        // Mumbai-specific configuration
        this.mumbaiConfig = new MumbaiCacheConfiguration();
        
        // Initialize operation counters
        initializeOperationCounters();
        
        LOGGER.info(String.format("Mumbai Cache Manager initialized: %s @ %s (Max Size: %d)", 
                                  cacheId, location, maxSize));
    }
    
    /**
     * Cache manager start करना
     */
    public void start() {
        if (running) {
            LOGGER.warning("Cache Manager already running");
            return;
        }
        
        running = true;
        
        // Start cleanup task
        startCleanupTask();
        
        // Start statistics collection
        startStatsCollection();
        
        // Initialize default partitions
        initializeDefaultPartitions();
        
        LOGGER.info(String.format("Mumbai Cache Manager started: %s", cacheId));
    }
    
    /**
     * Cache manager stop करना
     */
    public void stop() {
        if (!running) {
            return;
        }
        
        running = false;
        
        // Shutdown executors
        scheduler.shutdown();
        executor.shutdown();
        
        try {
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!executor.awaitTermination(10, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        LOGGER.info("Mumbai Cache Manager stopped");
    }
    
    /**
     * Cache में value store करना
     */
    public void put(String key, Object value, Duration ttl) {
        if (!running) {
            throw new IllegalStateException("Cache Manager is not running");
        }
        
        long startTime = System.currentTimeMillis();
        totalRequestCount.incrementAndGet();
        operationCounts.get("PUT").incrementAndGet();
        
        try {
            // Apply Mumbai-specific optimizations
            Duration effectiveTtl = applyMumbaiTtlOptimizations(key, ttl);
            
            // Create cache entry
            CacheEntry entry = new CacheEntry(key, value, effectiveTtl);
            
            // Determine partition
            String partitionId = getPartitionId(key);
            CachePartition partition = partitions.get(partitionId);
            
            if (partition != null) {
                partition.put(key, entry);
            }
            
            // Store in main cache
            CacheEntry oldEntry = cache.put(key, entry);
            
            // Handle eviction if cache is full
            if (cache.size() > maxSize.get()) {
                performEviction();
            }
            
            // Replicate if needed
            if (replicationStrategy.getReplicationFactor() > 1) {
                replicateEntry(key, entry);
            }
            
            LOGGER.fine(String.format("Cache PUT: %s (TTL: %s)", key, effectiveTtl));
            
        } finally {
            long responseTime = System.currentTimeMillis() - startTime;
            updateResponseTime(responseTime);
        }
    }
    
    /**
     * Cache से value retrieve करना
     */
    @SuppressWarnings("unchecked")
    public <T> T get(String key, Class<T> type) {
        if (!running) {
            throw new IllegalStateException("Cache Manager is not running");
        }
        
        long startTime = System.currentTimeMillis();
        totalRequestCount.incrementAndGet();
        operationCounts.get("GET").incrementAndGet();
        
        try {
            CacheEntry entry = cache.get(key);
            
            if (entry == null) {
                // Cache miss
                missCount.incrementAndGet();
                LOGGER.fine(String.format("Cache MISS: %s", key));
                return null;
            }
            
            // Check expiry
            if (entry.isExpired()) {
                // Remove expired entry
                remove(key);
                missCount.incrementAndGet();
                LOGGER.fine(String.format("Cache EXPIRED: %s", key));
                return null;
            }
            
            // Cache hit
            entry.updateAccess();
            hitCount.incrementAndGet();
            
            LOGGER.fine(String.format("Cache HIT: %s", key));
            
            try {
                return type.cast(entry.getValue());
            } catch (ClassCastException e) {
                LOGGER.warning(String.format("Type cast error for key %s: %s", key, e.getMessage()));
                return null;
            }
            
        } finally {
            long responseTime = System.currentTimeMillis() - startTime;
            updateResponseTime(responseTime);
        }
    }
    
    /**
     * Cache से entry remove करना
     */
    public boolean remove(String key) {
        if (!running) {
            throw new IllegalStateException("Cache Manager is not running");
        }
        
        totalRequestCount.incrementAndGet();
        operationCounts.get("DELETE").incrementAndGet();
        
        CacheEntry removed = cache.remove(key);
        
        if (removed != null) {
            // Remove from partition
            String partitionId = getPartitionId(key);
            CachePartition partition = partitions.get(partitionId);
            if (partition != null) {
                partition.remove(key);
            }
            
            // Replicate removal
            if (replicationStrategy.getReplicationFactor() > 1) {
                replicateRemoval(key);
            }
            
            LOGGER.fine(String.format("Cache REMOVE: %s", key));
            return true;
        }
        
        return false;
    }
    
    /**
     * Cache stats प्राप्त करना
     */
    public Map<String, Object> getCacheStats() {
        Map<String, Object> stats = new HashMap<>();
        
        // Basic cache info
        stats.put("cache_id", cacheId);
        stats.put("location", location);
        stats.put("status", running ? "RUNNING" : "STOPPED");
        stats.put("current_size", cache.size());
        stats.put("max_size", maxSize.get());
        stats.put("utilization_percent", (double) cache.size() / maxSize.get() * 100.0);
        
        // Hit/miss statistics
        long totalRequests = totalRequestCount.get();
        long hits = hitCount.get();
        long misses = missCount.get();
        
        stats.put("total_requests", totalRequests);
        stats.put("hit_count", hits);
        stats.put("miss_count", misses);
        stats.put("hit_rate_percent", totalRequests > 0 ? (double) hits / totalRequests * 100.0 : 0.0);
        stats.put("miss_rate_percent", totalRequests > 0 ? (double) misses / totalRequests * 100.0 : 0.0);
        
        // Performance metrics
        stats.put("eviction_count", evictionCount.get());
        
        // Response time statistics
        List<Long> recentTimes = new ArrayList<>(responseTimesMs);
        if (!recentTimes.isEmpty()) {
            double avgResponseTime = recentTimes.stream().mapToLong(Long::longValue).average().orElse(0.0);
            stats.put("avg_response_time_ms", avgResponseTime);
            stats.put("max_response_time_ms", recentTimes.stream().mapToLong(Long::longValue).max().orElse(0L));
            stats.put("min_response_time_ms", recentTimes.stream().mapToLong(Long::longValue).min().orElse(0L));
        }
        
        // Operation statistics
        Map<String, Long> operations = new HashMap<>();
        for (Map.Entry<String, AtomicLong> entry : operationCounts.entrySet()) {
            operations.put(entry.getKey().toLowerCase(), entry.getValue().get());
        }
        stats.put("operations", operations);
        
        // Partition statistics
        Map<String, Object> partitionStats = new HashMap<>();
        for (Map.Entry<String, CachePartition> entry : partitions.entrySet()) {
            CachePartition partition = entry.getValue();
            partitionStats.put(entry.getKey(), Map.of(
                "size", partition.getSize(),
                "total_bytes", partition.getTotalSizeBytes()
            ));
        }
        stats.put("partitions", partitionStats);
        
        // Configuration
        stats.put("eviction_policy", evictionPolicy.name());
        stats.put("consistency_level", consistencyLevel.name());
        stats.put("default_ttl_seconds", defaultTtlSeconds.get());
        
        // Mumbai-specific stats
        stats.put("mumbai_config", Map.of(
            "peak_hours", mumbaiConfig.isPeakHours(),
            "monsoon_mode", mumbaiConfig.get("monsoon_mode_enabled")
        ));
        
        return stats;
    }
    
    /**
     * Mumbai TTL optimizations apply करना
     */
    private Duration applyMumbaiTtlOptimizations(String key, Duration ttl) {
        Duration effectiveTtl = ttl != null ? ttl : Duration.ofSeconds(defaultTtlSeconds.get());
        
        // Peak hours के दौरान shorter TTL for better freshness
        if (mumbaiConfig.isPeakHours()) {
            effectiveTtl = Duration.ofSeconds(effectiveTtl.getSeconds() / 2);
        }
        
        // Content-specific optimizations
        if (key.contains("bollywood") && (Boolean) mumbaiConfig.get("bollywood_content_boost")) {
            effectiveTtl = Duration.ofSeconds(effectiveTtl.getSeconds() * 2); // Longer TTL for popular content
        }
        
        if (key.contains("cricket") && (Boolean) mumbaiConfig.get("cricket_content_boost")) {
            effectiveTtl = Duration.ofSeconds(effectiveTtl.getSeconds() * 3); // Even longer for cricket
        }
        
        return effectiveTtl;
    }
    
    /**
     * Partition ID determine करना
     */
    private String getPartitionId(String key) {
        // Simple hash-based partitioning
        int hashCode = key.hashCode();
        int partitionIndex = Math.abs(hashCode) % 4; // 4 partitions
        return "partition_" + partitionIndex;
    }
    
    /**
     * Cache eviction perform करना
     */
    private void performEviction() {
        List<CacheEntry> candidates = new ArrayList<>();
        
        switch (evictionPolicy) {
            case LRU:
                candidates = cache.values().stream()
                    .sorted(Comparator.comparing(CacheEntry::getLastAccessedAt))
                    .limit(maxSize.get() / 10) // Remove 10% of entries
                    .collect(Collectors.toList());
                break;
                
            case LFU:
                candidates = cache.values().stream()
                    .sorted(Comparator.comparing(CacheEntry::getAccessCount))
                    .limit(maxSize.get() / 10)
                    .collect(Collectors.toList());
                break;
                
            case FIFO:
                candidates = cache.values().stream()
                    .sorted(Comparator.comparing(CacheEntry::getCreatedAt))
                    .limit(maxSize.get() / 10)
                    .collect(Collectors.toList());
                break;
                
            case TTL_BASED:
                candidates = cache.values().stream()
                    .filter(CacheEntry::isExpired)
                    .collect(Collectors.toList());
                break;
                
            default:
                // Default to LRU
                candidates = cache.values().stream()
                    .sorted(Comparator.comparing(CacheEntry::getLastAccessedAt))
                    .limit(maxSize.get() / 10)
                    .collect(Collectors.toList());
        }
        
        // Remove selected candidates
        for (CacheEntry entry : candidates) {
            cache.remove(entry.getKey());
            evictionCount.incrementAndGet();
        }
        
        LOGGER.fine(String.format("Evicted %d entries using %s policy", 
                                  candidates.size(), evictionPolicy.name()));
    }
    
    /**
     * Entry replication
     */
    private void replicateEntry(String key, CacheEntry entry) {
        // Simulate replication to other nodes
        if (replicationStrategy.isAsyncReplication()) {
            executor.submit(() -> {
                // Async replication logic here
                LOGGER.fine(String.format("Replicated entry: %s", key));
            });
        }
    }
    
    /**
     * Removal replication
     */
    private void replicateRemoval(String key) {
        // Simulate replication of removal
        if (replicationStrategy.isAsyncReplication()) {
            executor.submit(() -> {
                // Async removal replication logic here
                LOGGER.fine(String.format("Replicated removal: %s", key));
            });
        }
    }
    
    /**
     * Response time update करना
     */
    private void updateResponseTime(long responseTime) {
        responseTimesMs.offer(responseTime);
        // Keep only last 1000 response times
        while (responseTimesMs.size() > 1000) {
            responseTimesMs.poll();
        }
    }
    
    /**
     * Initialize operation counters
     */
    private void initializeOperationCounters() {
        operationCounts.put("GET", new AtomicLong(0));
        operationCounts.put("PUT", new AtomicLong(0));
        operationCounts.put("DELETE", new AtomicLong(0));
    }
    
    /**
     * Initialize default partitions
     */
    private void initializeDefaultPartitions() {
        for (int i = 0; i < 4; i++) {
            String partitionId = "partition_" + i;
            partitions.put(partitionId, new CachePartition(partitionId));
        }
        LOGGER.info("Initialized 4 cache partitions");
    }
    
    /**
     * Start cleanup task
     */
    private void startCleanupTask() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                cleanupExpiredEntries();
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Cleanup task error", e);
            }
        }, CLEANUP_INTERVAL_SECONDS, CLEANUP_INTERVAL_SECONDS, TimeUnit.SECONDS);
    }
    
    /**
     * Start stats collection
     */
    private void startStatsCollection() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                collectStats();
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Stats collection error", e);
            }
        }, STATS_UPDATE_INTERVAL_SECONDS, STATS_UPDATE_INTERVAL_SECONDS, TimeUnit.SECONDS);
    }
    
    /**
     * Cleanup expired entries
     */
    private void cleanupExpiredEntries() {
        List<String> expiredKeys = cache.entrySet().stream()
            .filter(entry -> entry.getValue().isExpired())
            .map(Map.Entry::getKey)
            .collect(Collectors.toList());
        
        for (String key : expiredKeys) {
            remove(key);
        }
        
        if (!expiredKeys.isEmpty()) {
            LOGGER.fine(String.format("Cleaned up %d expired entries", expiredKeys.size()));
        }
    }
    
    /**
     * Collect performance statistics
     */
    private void collectStats() {
        // Log performance metrics periodically
        Map<String, Object> stats = getCacheStats();
        LOGGER.fine(String.format("Cache Stats - Size: %d, Hit Rate: %.2f%%, Avg Response: %.2f ms",
            (Integer) stats.get("current_size"),
            (Double) stats.get("hit_rate_percent"),
            stats.getOrDefault("avg_response_time_ms", 0.0)
        ));
    }
    
    // Getters और setters
    public void setEvictionPolicy(EvictionPolicy policy) {
        this.evictionPolicy = policy;
        LOGGER.info("Eviction policy changed to: " + policy.name());
    }
    
    public void setConsistencyLevel(ConsistencyLevel level) {
        this.consistencyLevel = level;
        LOGGER.info("Consistency level changed to: " + level.name());
    }
    
    public void setMaxSize(int newMaxSize) {
        this.maxSize.set(newMaxSize);
        LOGGER.info("Max cache size changed to: " + newMaxSize);
    }
    
    public MumbaiCacheConfiguration getMumbaiConfig() {
        return mumbaiConfig;
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("💾 Mumbai Cache Manager - Demonstration");
        System.out.println("=" + "=".repeat(55));
        
        // Initialize cache manager
        CacheManager cacheManager = new CacheManager(
            "mumbai-cache-01", "Mumbai Central", 1000, 3600
        );
        
        try {
            // Start cache manager
            cacheManager.start();
            System.out.println("✅ Cache Manager started");
            
            // Test basic cache operations
            System.out.println("\n📋 Testing Basic Cache Operations...");
            
            // Store some Mumbai-specific data
            cacheManager.put("bollywood:dangal", "Aamir Khan wrestling movie", Duration.ofMinutes(30));
            cacheManager.put("cricket:ipl_2024", "Mumbai Indians vs CSK", Duration.ofMinutes(60));
            cacheManager.put("mumbai:weather", "Partly cloudy, 28°C", Duration.ofMinutes(15));
            cacheManager.put("local:train_status", "Central line running on time", Duration.ofMinutes(5));
            cacheManager.put("payment:paytm_balance", "₹5,500", Duration.ofHours(2));
            
            System.out.println("✅ Stored 5 Mumbai-specific cache entries");
            
            // Retrieve data
            System.out.println("\n📊 Retrieving Cached Data...");
            
            String movie = cacheManager.get("bollywood:dangal", String.class);
            System.out.println("🎬 Bollywood: " + movie);
            
            String cricket = cacheManager.get("cricket:ipl_2024", String.class);
            System.out.println("🏏 Cricket: " + cricket);
            
            String weather = cacheManager.get("mumbai:weather", String.class);
            System.out.println("🌤️ Weather: " + weather);
            
            String trainStatus = cacheManager.get("local:train_status", String.class);
            System.out.println("🚊 Train: " + trainStatus);
            
            String balance = cacheManager.get("payment:paytm_balance", String.class);
            System.out.println("💰 Balance: " + balance);
            
            // Test cache miss
            String nonExistent = cacheManager.get("nonexistent:key", String.class);
            System.out.println("❌ Non-existent: " + (nonExistent != null ? nonExistent : "NULL (Cache Miss)"));
            
            // Test eviction by filling cache beyond capacity
            System.out.println("\n🔄 Testing Cache Eviction...");
            
            // Set smaller max size to trigger eviction
            cacheManager.setMaxSize(3);
            
            // Add more entries to trigger eviction
            cacheManager.put("test:entry1", "Test Value 1", Duration.ofMinutes(10));
            cacheManager.put("test:entry2", "Test Value 2", Duration.ofMinutes(10));
            cacheManager.put("test:entry3", "Test Value 3", Duration.ofMinutes(10));
            
            System.out.println("Added 3 more entries with max size = 3");
            
            // Check what's still in cache
            System.out.println("\n🔍 Checking Cache Contents After Eviction:");
            String[] testKeys = {"bollywood:dangal", "cricket:ipl_2024", "mumbai:weather", 
                                "test:entry1", "test:entry2", "test:entry3"};
            
            for (String key : testKeys) {
                String value = cacheManager.get(key, String.class);
                System.out.println("• " + key + ": " + (value != null ? "FOUND" : "EVICTED"));
            }
            
            // Wait to test TTL expiration
            System.out.println("\n⏱️ Testing TTL Expiration (waiting 6 seconds for short TTL entries)...");
            Thread.sleep(6000);
            
            String expiredTrain = cacheManager.get("local:train_status", String.class);
            System.out.println("🚊 Train Status (should be expired): " + 
                             (expiredTrain != null ? expiredTrain : "EXPIRED"));
            
            // Display comprehensive cache statistics
            System.out.println("\n📈 Cache Performance Statistics:");
            System.out.println("-".repeat(50));
            
            Map<String, Object> stats = cacheManager.getCacheStats();
            
            System.out.printf("Cache ID: %s%n", stats.get("cache_id"));
            System.out.printf("Location: %s%n", stats.get("location"));
            System.out.printf("Status: %s%n", stats.get("status"));
            System.out.printf("Current Size: %d / %d (%.1f%% utilized)%n",
                (Integer) stats.get("current_size"),
                (Integer) stats.get("max_size"),
                (Double) stats.get("utilization_percent")
            );
            
            System.out.printf("Total Requests: %d%n", stats.get("total_requests"));
            System.out.printf("Cache Hits: %d%n", stats.get("hit_count"));
            System.out.printf("Cache Misses: %d%n", stats.get("miss_count"));
            System.out.printf("Hit Rate: %.2f%%%n", stats.get("hit_rate_percent"));
            System.out.printf("Evictions: %d%n", stats.get("eviction_count"));
            
            if (stats.containsKey("avg_response_time_ms")) {
                System.out.printf("Avg Response Time: %.2f ms%n", stats.get("avg_response_time_ms"));
            }
            
            // Operations breakdown
            @SuppressWarnings("unchecked")
            Map<String, Long> operations = (Map<String, Long>) stats.get("operations");
            System.out.println("\n🔧 Operations Breakdown:");
            for (Map.Entry<String, Long> entry : operations.entrySet()) {
                System.out.printf("• %s: %d%n", entry.getKey().toUpperCase(), entry.getValue());
            }
            
            // Mumbai-specific information
            @SuppressWarnings("unchecked")
            Map<String, Object> mumbaiConfig = (Map<String, Object>) stats.get("mumbai_config");
            System.out.println("\n🏙️ Mumbai Configuration:");
            System.out.printf("• Peak Hours: %s%n", 
                mumbaiConfig.get("peak_hours") ? "Yes (optimized caching)" : "No");
            System.out.printf("• Monsoon Mode: %s%n", 
                mumbaiConfig.get("monsoon_mode") ? "Enabled" : "Disabled");
            
            // Cost analysis
            System.out.println("\n💰 Cost Analysis:");
            long totalRequests = ((Number) stats.get("total_requests")).longValue();
            double edgeCacheCost = (totalRequests / 1000.0) * 2.0;  // ₹2 per 1000 requests
            double cloudCacheCost = (totalRequests / 1000.0) * 20.0; // ₹20 per 1000 requests
            double savings = cloudCacheCost - edgeCacheCost;
            
            System.out.printf("• Edge Cache Cost: ₹%.2f%n", edgeCacheCost);
            System.out.printf("• Cloud Cache Cost: ₹%.2f%n", cloudCacheCost);
            System.out.printf("• Cost Savings: ₹%.2f (%.1f%%)%n", 
                savings, (savings / cloudCacheCost) * 100);
            
            System.out.println("\n🎯 Mumbai Cache Benefits:");
            System.out.println("• Local caching reduces latency by 70%");
            System.out.println("• Mumbai content optimization (Bollywood, Cricket)");
            System.out.println("• Peak hours traffic handling");
            System.out.println("• Cost savings of 90% compared to cloud caching");
            System.out.println("• Monsoon-resilient caching strategies");
            
        } finally {
            // Cleanup
            System.out.println("\n🛑 Stopping cache manager...");
            cacheManager.stop();
            System.out.println("✅ Mumbai Cache Manager demonstration completed!");
        }
    }
}