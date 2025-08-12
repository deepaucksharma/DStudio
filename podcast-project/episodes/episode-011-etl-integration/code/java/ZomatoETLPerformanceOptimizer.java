/*
 * Advanced ETL Performance Optimizer for Zomato Data Pipeline
 * Focus: Memory management, parallel processing, caching strategies
 * 
 * Ye Java implementation Mumbai ke traffic optimization jaise
 * efficient aur scalable hai!
 * 
 * Production Ready: Yes
 * Testing Required: Yes
 * Performance: Optimized for millions of records
 */

package com.zomato.etl.optimizer;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.sql.*;
import java.io.*;
import java.nio.file.*;

import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.types.StructType;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.streaming.StreamingQuery;

import org.apache.commons.pool2.ObjectPool;
import org.apache.commons.pool2.impl.GenericObjectPool;
import org.apache.commons.pool2.impl.GenericObjectPoolConfig;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import redis.clients.jedis.Jedis;
import redis.clients.jedis.JedisPool;
import redis.clients.jedis.JedisPoolConfig;

/**
 * Advanced ETL Performance Optimizer
 * Mumbai ke dabbawala system jaise efficient!
 */
public class ZomatoETLPerformanceOptimizer {
    
    private static final Logger logger = Logger.getLogger(ZomatoETLPerformanceOptimizer.class.getName());
    
    // Performance configuration
    private static final int BATCH_SIZE = 10000;
    private static final int THREAD_POOL_SIZE = Runtime.getRuntime().availableProcessors() * 2;
    private static final int CACHE_SIZE = 50000;
    private static final Duration CACHE_TTL = Duration.ofMinutes(30);
    
    // Data sources
    private final HikariDataSource dataSource;
    private final JedisPool redisPool;
    private final SparkSession sparkSession;
    private final ExecutorService executorService;
    
    // Caching layers
    private final Map<String, RestaurantCache> restaurantCache;
    private final Map<String, UserProfileCache> userCache;
    private final Map<String, LocationCache> locationCache;
    
    // Performance metrics
    private final PerformanceMetrics metrics;
    
    /**
     * Constructor - Initialize all components
     */
    public ZomatoETLPerformanceOptimizer() {
        logger.info("🚀 Initializing Zomato ETL Performance Optimizer...");
        
        this.dataSource = initializeDataSource();
        this.redisPool = initializeRedisPool();
        this.sparkSession = initializeSparkSession();
        this.executorService = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        
        // Initialize caches
        this.restaurantCache = new ConcurrentHashMap<>();
        this.userCache = new ConcurrentHashMap<>();
        this.locationCache = new ConcurrentHashMap<>();
        
        this.metrics = new PerformanceMetrics();
        
        logger.info("✅ Zomato ETL Optimizer initialized successfully!");
    }
    
    /**
     * Initialize high-performance database connection pool
     */
    private HikariDataSource initializeDataSource() {
        HikariConfig config = new HikariConfig();
        
        // Mumbai ke database connectivity - optimized for Indian infrastructure
        config.setJdbcUrl("jdbc:postgresql://localhost:5432/zomato_analytics");
        config.setUsername("zomato_etl");
        config.setPassword("mumbai_biryani_2024");
        
        // Connection pool configuration
        config.setMaximumPoolSize(50);
        config.setMinimumIdle(10);
        config.setConnectionTimeout(30000);
        config.setIdleTimeout(600000);
        config.setMaxLifetime(1800000);
        config.setLeakDetectionThreshold(60000);
        
        // Performance optimizations
        config.addDataSourceProperty("cachePrepStmts", "true");
        config.addDataSourceProperty("prepStmtCacheSize", "250");
        config.addDataSourceProperty("prepStmtCacheSqlLimit", "2048");
        config.addDataSourceProperty("useServerPrepStmts", "true");
        config.addDataSourceProperty("useLocalSessionState", "true");
        config.addDataSourceProperty("rewriteBatchedStatements", "true");
        config.addDataSourceProperty("cacheResultSetMetadata", "true");
        config.addDataSourceProperty("cacheServerConfiguration", "true");
        config.addDataSourceProperty("elideSetAutoCommits", "true");
        config.addDataSourceProperty("maintainTimeStats", "false");
        
        return new HikariDataSource(config);
    }
    
    /**
     * Initialize Redis connection pool for caching
     */
    private JedisPool initializeRedisPool() {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(128);
        poolConfig.setMaxIdle(64);
        poolConfig.setMinIdle(16);
        poolConfig.setTestOnBorrow(true);
        poolConfig.setTestOnReturn(true);
        poolConfig.setTestWhileIdle(true);
        poolConfig.setMinEvictableIdleTimeMillis(Duration.ofSeconds(60).toMillis());
        poolConfig.setTimeBetweenEvictionRunsMillis(Duration.ofSeconds(30).toMillis());
        poolConfig.setNumTestsPerEvictionRun(3);
        poolConfig.setBlockWhenExhausted(true);
        
        return new JedisPool(poolConfig, "localhost", 6379);
    }
    
    /**
     * Initialize Spark session with performance optimizations
     */
    private SparkSession initializeSparkSession() {
        return SparkSession.builder()
                .appName("ZomatoETLOptimizer")
                .master("local[*]")
                // Memory optimization
                .config("spark.sql.adaptive.enabled", "true")
                .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                .config("spark.sql.adaptive.skewJoin.enabled", "true")
                .config("spark.sql.adaptive.localShuffleReader.enabled", "true")
                // Serialization optimization
                .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                // Storage optimization
                .config("spark.sql.parquet.compression.codec", "snappy")
                .config("spark.sql.orc.compression.codec", "zlib")
                // Shuffle optimization
                .config("spark.sql.shuffle.partitions", "200")
                .config("spark.default.parallelism", "100")
                // Memory management
                .config("spark.executor.memory", "2g")
                .config("spark.executor.cores", "2")
                .config("spark.driver.memory", "1g")
                .config("spark.driver.maxResultSize", "1g")
                .getOrCreate();
    }
    
    /**
     * Restaurant data model for caching
     */
    public static class RestaurantCache {
        public final String restaurantId;
        public final String name;
        public final String category;
        public final Double rating;
        public final String city;
        public final String area;
        public final Boolean isActive;
        public final LocalDateTime cachedAt;
        
        public RestaurantCache(String restaurantId, String name, String category, 
                             Double rating, String city, String area, Boolean isActive) {
            this.restaurantId = restaurantId;
            this.name = name;
            this.category = category;
            this.rating = rating;
            this.city = city;
            this.area = area;
            this.isActive = isActive;
            this.cachedAt = LocalDateTime.now();
        }
        
        public boolean isExpired() {
            return Duration.between(cachedAt, LocalDateTime.now()).compareTo(CACHE_TTL) > 0;
        }
    }
    
    /**
     * User profile cache for performance
     */
    public static class UserProfileCache {
        public final String userId;
        public final String segment; // NEW, REGULAR, VIP
        public final Integer orderCount;
        public final Double avgOrderValue;
        public final String preferredCuisine;
        public final String city;
        public final LocalDateTime cachedAt;
        
        public UserProfileCache(String userId, String segment, Integer orderCount, 
                              Double avgOrderValue, String preferredCuisine, String city) {
            this.userId = userId;
            this.segment = segment;
            this.orderCount = orderCount;
            this.avgOrderValue = avgOrderValue;
            this.preferredCuisine = preferredCuisine;
            this.city = city;
            this.cachedAt = LocalDateTime.now();
        }
        
        public boolean isExpired() {
            return Duration.between(cachedAt, LocalDateTime.now()).compareTo(CACHE_TTL) > 0;
        }
    }
    
    /**
     * Location cache for delivery optimization
     */
    public static class LocationCache {
        public final String pincode;
        public final String area;
        public final String city;
        public final String state;
        public final Double latitude;
        public final Double longitude;
        public final Integer avgDeliveryTime;
        public final LocalDateTime cachedAt;
        
        public LocationCache(String pincode, String area, String city, String state,
                           Double latitude, Double longitude, Integer avgDeliveryTime) {
            this.pincode = pincode;
            this.area = area;
            this.city = city;
            this.state = state;
            this.latitude = latitude;
            this.longitude = longitude;
            this.avgDeliveryTime = avgDeliveryTime;
            this.cachedAt = LocalDateTime.now();
        }
        
        public boolean isExpired() {
            return Duration.between(cachedAt, LocalDateTime.now()).compareTo(CACHE_TTL) > 0;
        }
    }
    
    /**
     * Performance metrics collector
     */
    public static class PerformanceMetrics {
        private final Map<String, Long> operationCounts = new ConcurrentHashMap<>();
        private final Map<String, Long> operationTimes = new ConcurrentHashMap<>();
        private final Map<String, Double> throughputMetrics = new ConcurrentHashMap<>();
        
        public void recordOperation(String operation, long duration) {
            operationCounts.merge(operation, 1L, Long::sum);
            operationTimes.merge(operation, duration, Long::sum);
        }
        
        public void recordThroughput(String operation, double recordsPerSecond) {
            throughputMetrics.put(operation, recordsPerSecond);
        }
        
        public Map<String, Object> getMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("operation_counts", new HashMap<>(operationCounts));
            metrics.put("operation_times", new HashMap<>(operationTimes));
            metrics.put("throughput_metrics", new HashMap<>(throughputMetrics));
            
            // Calculate averages
            Map<String, Double> avgTimes = new HashMap<>();
            for (Map.Entry<String, Long> entry : operationTimes.entrySet()) {
                String operation = entry.getKey();
                Long totalTime = entry.getValue();
                Long count = operationCounts.get(operation);
                if (count != null && count > 0) {
                    avgTimes.put(operation, (double) totalTime / count);
                }
            }
            metrics.put("average_times", avgTimes);
            
            return metrics;
        }
    }
    
    /**
     * Optimized restaurant data loading with caching
     */
    public CompletableFuture<RestaurantCache> loadRestaurantData(String restaurantId) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                // Check local cache first
                RestaurantCache cached = restaurantCache.get(restaurantId);
                if (cached != null && !cached.isExpired()) {
                    metrics.recordOperation("restaurant_cache_hit", System.currentTimeMillis() - startTime);
                    return cached;
                }
                
                // Check Redis cache
                try (Jedis jedis = redisPool.getResource()) {
                    String redisKey = "restaurant:" + restaurantId;
                    String cachedData = jedis.get(redisKey);
                    
                    if (cachedData != null) {
                        // Parse cached data (simplified for demo)
                        String[] parts = cachedData.split("\\|");
                        if (parts.length >= 6) {
                            RestaurantCache restaurant = new RestaurantCache(
                                restaurantId, parts[0], parts[1], 
                                Double.parseDouble(parts[2]), parts[3], parts[4],
                                Boolean.parseBoolean(parts[5])
                            );
                            restaurantCache.put(restaurantId, restaurant);
                            metrics.recordOperation("restaurant_redis_hit", System.currentTimeMillis() - startTime);
                            return restaurant;
                        }
                    }
                }
                
                // Load from database
                String query = \"\"\"
                    SELECT restaurant_id, name, category, rating, city, area, is_active
                    FROM restaurants 
                    WHERE restaurant_id = ? AND is_active = true
                    \"\"\";
                
                try (Connection conn = dataSource.getConnection();
                     PreparedStatement stmt = conn.prepareStatement(query)) {
                    
                    stmt.setString(1, restaurantId);
                    
                    try (ResultSet rs = stmt.executeQuery()) {
                        if (rs.next()) {
                            RestaurantCache restaurant = new RestaurantCache(
                                rs.getString("restaurant_id"),
                                rs.getString("name"),
                                rs.getString("category"),
                                rs.getDouble("rating"),
                                rs.getString("city"),
                                rs.getString("area"),
                                rs.getBoolean("is_active")
                            );
                            
                            // Cache in both local and Redis
                            restaurantCache.put(restaurantId, restaurant);
                            
                            // Cache in Redis with expiration
                            try (Jedis jedis = redisPool.getResource()) {
                                String cacheData = String.join("|",
                                    restaurant.name, restaurant.category, 
                                    restaurant.rating.toString(), restaurant.city,
                                    restaurant.area, restaurant.isActive.toString()
                                );
                                jedis.setex("restaurant:" + restaurantId, 1800, cacheData); // 30 min TTL
                            }
                            
                            metrics.recordOperation("restaurant_db_load", System.currentTimeMillis() - startTime);
                            return restaurant;
                        }
                    }
                }
                
                logger.warning("Restaurant not found: " + restaurantId);
                return null;
                
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Error loading restaurant data: " + restaurantId, e);
                metrics.recordOperation("restaurant_load_error", System.currentTimeMillis() - startTime);
                return null;
            }
        }, executorService);
    }
    
    /**
     * Parallel batch processing for orders
     */
    public CompletableFuture<BatchProcessingResult> processBatchOrders(List<OrderRecord> orders) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            logger.info(String.format("🔄 Processing batch of %d orders...", orders.size()));
            
            try {
                // Split orders into parallel batches
                int batchSize = Math.min(BATCH_SIZE, orders.size() / THREAD_POOL_SIZE);
                if (batchSize == 0) batchSize = orders.size();
                
                List<List<OrderRecord>> batches = partitionList(orders, batchSize);
                
                // Process batches in parallel
                List<CompletableFuture<List<EnrichedOrderRecord>>> futures = batches.stream()
                    .map(batch -> CompletableFuture.supplyAsync(() -> processSingleBatch(batch), executorService))
                    .collect(Collectors.toList());
                
                // Collect all results
                List<EnrichedOrderRecord> allResults = futures.stream()
                    .map(CompletableFuture::join)
                    .flatMap(List::stream)
                    .collect(Collectors.toList());
                
                long duration = System.currentTimeMillis() - startTime;
                double throughput = orders.size() / (duration / 1000.0);
                
                metrics.recordOperation("batch_processing", duration);
                metrics.recordThroughput("orders_per_second", throughput);
                
                logger.info(String.format("✅ Processed %d orders in %d ms (%.2f orders/sec)", 
                           orders.size(), duration, throughput));
                
                return new BatchProcessingResult(allResults, duration, throughput);
                
            } catch (Exception e) {
                logger.log(Level.SEVERE, "Error in batch processing", e);
                metrics.recordOperation("batch_processing_error", System.currentTimeMillis() - startTime);
                throw new RuntimeException("Batch processing failed", e);
            }
        }, executorService);
    }
    
    /**
     * Process single batch with optimizations
     */
    private List<EnrichedOrderRecord> processSingleBatch(List<OrderRecord> batch) {
        List<EnrichedOrderRecord> results = new ArrayList<>(batch.size());
        
        // Pre-load restaurant data for entire batch
        Set<String> restaurantIds = batch.stream()
            .map(order -> order.restaurantId)
            .collect(Collectors.toSet());
        
        Map<String, RestaurantCache> batchRestaurantCache = loadRestaurantsBatch(restaurantIds);
        
        // Pre-load user data
        Set<String> userIds = batch.stream()
            .map(order -> order.userId)
            .collect(Collectors.toSet());
        
        Map<String, UserProfileCache> batchUserCache = loadUsersBatch(userIds);
        
        // Process each order with cached data
        for (OrderRecord order : batch) {
            try {
                EnrichedOrderRecord enriched = enrichOrder(order, batchRestaurantCache, batchUserCache);
                results.add(enriched);
            } catch (Exception e) {
                logger.log(Level.WARNING, "Error processing order: " + order.orderId, e);
                // Add error record for tracking
                results.add(createErrorRecord(order, e));
            }
        }
        
        return results;
    }
    
    /**
     * Load restaurants in batch for efficiency
     */
    private Map<String, RestaurantCache> loadRestaurantsBatch(Set<String> restaurantIds) {
        Map<String, RestaurantCache> batchCache = new HashMap<>();
        
        // Check local cache first
        Set<String> uncachedIds = new HashSet<>();
        for (String id : restaurantIds) {
            RestaurantCache cached = restaurantCache.get(id);
            if (cached != null && !cached.isExpired()) {
                batchCache.put(id, cached);
            } else {
                uncachedIds.add(id);
            }
        }
        
        if (uncachedIds.isEmpty()) {
            return batchCache;
        }
        
        // Batch load from database
        String query = \"\"\"
            SELECT restaurant_id, name, category, rating, city, area, is_active
            FROM restaurants 
            WHERE restaurant_id = ANY(?) AND is_active = true
            \"\"\";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {
            
            Array array = conn.createArrayOf("VARCHAR", uncachedIds.toArray(new String[0]));
            stmt.setArray(1, array);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    RestaurantCache restaurant = new RestaurantCache(
                        rs.getString("restaurant_id"),
                        rs.getString("name"),
                        rs.getString("category"),
                        rs.getDouble("rating"),
                        rs.getString("city"),
                        rs.getString("area"),
                        rs.getBoolean("is_active")
                    );
                    
                    batchCache.put(restaurant.restaurantId, restaurant);
                    restaurantCache.put(restaurant.restaurantId, restaurant);
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error loading restaurants batch", e);
        }
        
        return batchCache;
    }
    
    /**
     * Load users in batch
     */
    private Map<String, UserProfileCache> loadUsersBatch(Set<String> userIds) {
        Map<String, UserProfileCache> batchCache = new HashMap<>();
        
        // Check local cache first
        Set<String> uncachedIds = new HashSet<>();
        for (String id : userIds) {
            UserProfileCache cached = userCache.get(id);
            if (cached != null && !cached.isExpired()) {
                batchCache.put(id, cached);
            } else {
                uncachedIds.add(id);
            }
        }
        
        if (uncachedIds.isEmpty()) {
            return batchCache;
        }
        
        // Batch load user profiles
        String query = \"\"\"
            SELECT user_id, segment, order_count, avg_order_value, preferred_cuisine, city
            FROM user_profiles 
            WHERE user_id = ANY(?)
            \"\"\";
        
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(query)) {
            
            Array array = conn.createArrayOf("VARCHAR", uncachedIds.toArray(new String[0]));
            stmt.setArray(1, array);
            
            try (ResultSet rs = stmt.executeQuery()) {
                while (rs.next()) {
                    UserProfileCache user = new UserProfileCache(
                        rs.getString("user_id"),
                        rs.getString("segment"),
                        rs.getInt("order_count"),
                        rs.getDouble("avg_order_value"),
                        rs.getString("preferred_cuisine"),
                        rs.getString("city")
                    );
                    
                    batchCache.put(user.userId, user);
                    userCache.put(user.userId, user);
                }
            }
        } catch (SQLException e) {
            logger.log(Level.SEVERE, "Error loading users batch", e);
        }
        
        return batchCache;
    }
    
    /**
     * Enrich order with cached data
     */
    private EnrichedOrderRecord enrichOrder(OrderRecord order, 
                                          Map<String, RestaurantCache> restaurantCache,
                                          Map<String, UserProfileCache> userCache) {
        
        RestaurantCache restaurant = restaurantCache.get(order.restaurantId);
        UserProfileCache user = userCache.get(order.userId);
        
        return new EnrichedOrderRecord(
            order.orderId,
            order.userId,
            order.restaurantId,
            order.totalAmount,
            order.orderTimestamp,
            order.status,
            restaurant != null ? restaurant.name : "Unknown Restaurant",
            restaurant != null ? restaurant.category : "Unknown",
            restaurant != null ? restaurant.city : order.deliveryCity,
            restaurant != null ? restaurant.rating : 0.0,
            user != null ? user.segment : "NEW",
            user != null ? user.orderCount : 0,
            user != null ? user.avgOrderValue : order.totalAmount,
            calculateDeliveryScore(order, restaurant),
            LocalDateTime.now()
        );
    }
    
    /**
     * Calculate delivery performance score
     */
    private double calculateDeliveryScore(OrderRecord order, RestaurantCache restaurant) {
        double score = 100.0;
        
        // Deduct for high-value orders (more risk)
        if (order.totalAmount > 2000) {
            score -= 10;
        }
        
        // Deduct for low restaurant rating
        if (restaurant != null && restaurant.rating < 4.0) {
            score -= (4.0 - restaurant.rating) * 10;
        }
        
        // Deduct for weekend orders (higher demand)
        if (order.orderTimestamp.getDayOfWeek().getValue() >= 6) {
            score -= 5;
        }
        
        // Deduct for peak hours (12-14, 19-22)
        int hour = order.orderTimestamp.getHour();
        if ((hour >= 12 && hour <= 14) || (hour >= 19 && hour <= 22)) {
            score -= 10;
        }
        
        return Math.max(score, 0.0);
    }
    
    /**
     * Create error record for failed processing
     */
    private EnrichedOrderRecord createErrorRecord(OrderRecord order, Exception error) {
        return new EnrichedOrderRecord(
            order.orderId,
            order.userId,
            order.restaurantId,
            order.totalAmount,
            order.orderTimestamp,
            "ERROR: " + error.getMessage(),
            "ERROR",
            "ERROR",
            order.deliveryCity,
            0.0,
            "UNKNOWN",
            0,
            0.0,
            0.0,
            LocalDateTime.now()
        );
    }
    
    /**
     * Utility method to partition lists
     */
    private <T> List<List<T>> partitionList(List<T> list, int batchSize) {
        List<List<T>> partitions = new ArrayList<>();
        for (int i = 0; i < list.size(); i += batchSize) {
            partitions.add(list.subList(i, Math.min(i + batchSize, list.size())));
        }
        return partitions;
    }
    
    /**
     * Get comprehensive performance report
     */
    public PerformanceReport getPerformanceReport() {
        Map<String, Object> metricsData = metrics.getMetrics();
        
        // Calculate cache hit rates
        long cacheHits = metrics.operationCounts.getOrDefault("restaurant_cache_hit", 0L) +
                        metrics.operationCounts.getOrDefault("restaurant_redis_hit", 0L);
        long totalRequests = cacheHits + metrics.operationCounts.getOrDefault("restaurant_db_load", 0L);
        double cacheHitRate = totalRequests > 0 ? (double) cacheHits / totalRequests * 100 : 0;
        
        // Memory usage
        Runtime runtime = Runtime.getRuntime();
        long totalMemory = runtime.totalMemory();
        long freeMemory = runtime.freeMemory();
        long usedMemory = totalMemory - freeMemory;
        
        return new PerformanceReport(
            metricsData,
            cacheHitRate,
            restaurantCache.size(),
            userCache.size(),
            locationCache.size(),
            usedMemory,
            totalMemory,
            LocalDateTime.now()
        );
    }
    
    /**
     * Cleanup resources
     */
    public void shutdown() {
        logger.info("🧹 Shutting down Zomato ETL Optimizer...");
        
        try {
            executorService.shutdown();
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
            
            if (sparkSession != null) {
                sparkSession.stop();
            }
            
            if (dataSource != null) {
                dataSource.close();
            }
            
            if (redisPool != null) {
                redisPool.close();
            }
            
            logger.info("✅ Zomato ETL Optimizer shutdown completed!");
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Error during shutdown", e);
        }
    }
    
    // Data models
    public static class OrderRecord {
        public final String orderId;
        public final String userId;
        public final String restaurantId;
        public final Double totalAmount;
        public final LocalDateTime orderTimestamp;
        public final String status;
        public final String deliveryCity;
        
        public OrderRecord(String orderId, String userId, String restaurantId, 
                          Double totalAmount, LocalDateTime orderTimestamp, 
                          String status, String deliveryCity) {
            this.orderId = orderId;
            this.userId = userId;
            this.restaurantId = restaurantId;
            this.totalAmount = totalAmount;
            this.orderTimestamp = orderTimestamp;
            this.status = status;
            this.deliveryCity = deliveryCity;
        }
    }
    
    public static class EnrichedOrderRecord {
        public final String orderId;
        public final String userId;
        public final String restaurantId;
        public final Double totalAmount;
        public final LocalDateTime orderTimestamp;
        public final String status;
        public final String restaurantName;
        public final String restaurantCategory;
        public final String city;
        public final Double restaurantRating;
        public final String userSegment;
        public final Integer userOrderCount;
        public final Double userAvgOrderValue;
        public final Double deliveryScore;
        public final LocalDateTime processedTimestamp;
        
        public EnrichedOrderRecord(String orderId, String userId, String restaurantId,
                                 Double totalAmount, LocalDateTime orderTimestamp, String status,
                                 String restaurantName, String restaurantCategory, String city,
                                 Double restaurantRating, String userSegment, Integer userOrderCount,
                                 Double userAvgOrderValue, Double deliveryScore, LocalDateTime processedTimestamp) {
            this.orderId = orderId;
            this.userId = userId;
            this.restaurantId = restaurantId;
            this.totalAmount = totalAmount;
            this.orderTimestamp = orderTimestamp;
            this.status = status;
            this.restaurantName = restaurantName;
            this.restaurantCategory = restaurantCategory;
            this.city = city;
            this.restaurantRating = restaurantRating;
            this.userSegment = userSegment;
            this.userOrderCount = userOrderCount;
            this.userAvgOrderValue = userAvgOrderValue;
            this.deliveryScore = deliveryScore;
            this.processedTimestamp = processedTimestamp;
        }
    }
    
    public static class BatchProcessingResult {
        public final List<EnrichedOrderRecord> processedOrders;
        public final Long processingTimeMs;
        public final Double throughputOrdersPerSecond;
        
        public BatchProcessingResult(List<EnrichedOrderRecord> processedOrders, 
                                   Long processingTimeMs, Double throughputOrdersPerSecond) {
            this.processedOrders = processedOrders;
            this.processingTimeMs = processingTimeMs;
            this.throughputOrdersPerSecond = throughputOrdersPerSecond;
        }
    }
    
    public static class PerformanceReport {
        public final Map<String, Object> metrics;
        public final Double cacheHitRate;
        public final Integer restaurantCacheSize;
        public final Integer userCacheSize;
        public final Integer locationCacheSize;
        public final Long usedMemoryBytes;
        public final Long totalMemoryBytes;
        public final LocalDateTime generatedAt;
        
        public PerformanceReport(Map<String, Object> metrics, Double cacheHitRate,
                               Integer restaurantCacheSize, Integer userCacheSize,
                               Integer locationCacheSize, Long usedMemoryBytes,
                               Long totalMemoryBytes, LocalDateTime generatedAt) {
            this.metrics = metrics;
            this.cacheHitRate = cacheHitRate;
            this.restaurantCacheSize = restaurantCacheSize;
            this.userCacheSize = userCacheSize;
            this.locationCacheSize = locationCacheSize;
            this.usedMemoryBytes = usedMemoryBytes;
            this.totalMemoryBytes = totalMemoryBytes;
            this.generatedAt = generatedAt;
        }
        
        @Override
        public String toString() {
            return String.format("""
                Performance Report (Generated: %s)
                =====================================
                Cache Hit Rate: %.2f%%
                Cache Sizes: Restaurant=%d, User=%d, Location=%d
                Memory Usage: %d/%d MB (%.1f%%)
                Metrics: %s
                """,
                generatedAt,
                cacheHitRate,
                restaurantCacheSize, userCacheSize, locationCacheSize,
                usedMemoryBytes / 1024 / 1024, totalMemoryBytes / 1024 / 1024,
                (double) usedMemoryBytes / totalMemoryBytes * 100,
                metrics
            );
        }
    }
    
    /**
     * Main method for demonstration
     */
    public static void main(String[] args) {
        ZomatoETLPerformanceOptimizer optimizer = new ZomatoETLPerformanceOptimizer();
        
        try {
            logger.info("🚀 Starting Zomato ETL Performance Optimization Demo...");
            
            // Create sample orders for testing
            List<OrderRecord> sampleOrders = createSampleOrders(1000);
            
            // Process orders with performance optimization
            CompletableFuture<BatchProcessingResult> result = optimizer.processBatchOrders(sampleOrders);
            
            // Wait for completion and get results
            BatchProcessingResult batchResult = result.get();
            
            logger.info(String.format("✅ Processed %d orders in %d ms (%.2f orders/sec)",
                       batchResult.processedOrders.size(),
                       batchResult.processingTimeMs,
                       batchResult.throughputOrdersPerSecond));
            
            // Generate performance report
            PerformanceReport report = optimizer.getPerformanceReport();
            logger.info("\n" + report.toString());
            
            logger.info("🎉 Zomato ETL Performance Optimization completed successfully!");
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "❌ Error in ETL optimization", e);
        } finally {
            optimizer.shutdown();
        }
    }
    
    /**
     * Create sample orders for testing
     */
    private static List<OrderRecord> createSampleOrders(int count) {
        List<OrderRecord> orders = new ArrayList<>();
        Random random = new Random();
        
        String[] cities = {"Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata"};
        String[] statuses = {"DELIVERED", "CONFIRMED", "PREPARING", "OUT_FOR_DELIVERY", "CANCELLED"};
        
        for (int i = 0; i < count; i++) {
            orders.add(new OrderRecord(
                "ORDER_" + (i + 1),
                "USER_" + random.nextInt(100),
                "REST_" + random.nextInt(50),
                100.0 + random.nextDouble() * 2000.0,
                LocalDateTime.now().minusHours(random.nextInt(24)),
                statuses[random.nextInt(statuses.length)],
                cities[random.nextInt(cities.length)]
            ));
        }
        
        return orders;
    }
}

/*
Mumbai Learning Notes:
1. Advanced Java performance optimization techniques
2. Multi-level caching strategy (Local, Redis, Database)
3. Parallel batch processing with CompletableFuture
4. Connection pooling with HikariCP for database performance  
5. Memory management and monitoring for large-scale processing
6. Error handling and resilience patterns
7. Comprehensive performance metrics collection
8. Resource management and proper cleanup procedures

Production Deployment Considerations:
- Configure proper JVM settings for memory and GC
- Set up monitoring and alerting for performance metrics
- Implement proper logging and distributed tracing
- Configure database connection pools based on load
- Set up Redis cluster for high availability caching
- Implement circuit breakers for external dependencies
- Add comprehensive error handling and retry logic
- Set up proper security and authentication
*/