# Performance Optimization for Distributed Systems: The Complete Guide

## Executive Summary

Performance optimization in distributed systems requires systematic measurement, careful analysis, and targeted improvements. This guide provides battle-tested optimization strategies from companies processing billions of requests daily.

---

## Part 1: Performance Analysis and Profiling

### Application Performance Monitoring (APM)

```java
@Configuration
public class PerformanceMonitoringConfig {
    
    /**
     * Method-level performance tracking
     */
    @Aspect
    @Component
    public class PerformanceAspect {
        
        private final MeterRegistry registry;
        
        @Around("@annotation(Monitored)")
        public Object monitorPerformance(ProceedingJoinPoint joinPoint) throws Throwable {
            String methodName = joinPoint.getSignature().toShortString();
            
            Timer.Sample sample = Timer.start(registry);
            
            try {
                Object result = joinPoint.proceed();
                
                sample.stop(Timer.builder("method.execution")
                    .tag("method", methodName)
                    .tag("status", "success")
                    .publishPercentileHistogram()
                    .register(registry));
                
                return result;
                
            } catch (Exception e) {
                sample.stop(Timer.builder("method.execution")
                    .tag("method", methodName)
                    .tag("status", "error")
                    .tag("exception", e.getClass().getSimpleName())
                    .register(registry));
                
                throw e;
            }
        }
    }
    
    /**
     * JVM profiling with async-profiler integration
     */
    @Service
    public class ContinuousProfiler {
        
        private final AsyncProfiler profiler = AsyncProfiler.getInstance();
        
        @PostConstruct
        public void startProfiling() {
            // CPU profiling
            profiler.start("cpu", 1_000_000); // 1ms sampling interval
            
            // Allocation profiling
            profiler.start("alloc", 512 * 1024); // 512KB sampling
            
            // Schedule periodic dumps
            scheduledExecutor.scheduleAtFixedRate(
                this::dumpProfile, 0, 5, TimeUnit.MINUTES);
        }
        
        private void dumpProfile() {
            String timestamp = Instant.now().toString();
            
            // Dump CPU profile
            String cpuProfile = profiler.dumpFlat(100);
            metricsService.recordProfile("cpu", timestamp, cpuProfile);
            
            // Dump allocation profile
            String allocProfile = profiler.dumpTraces(100);
            metricsService.recordProfile("alloc", timestamp, allocProfile);
            
            // Identify hot methods
            identifyHotspots(cpuProfile);
        }
        
        private void identifyHotspots(String profile) {
            // Parse profile and identify methods > 5% CPU
            Arrays.stream(profile.split("\n"))
                .filter(line -> line.matches("\\s+\\d+\\.\\d+%.*"))
                .forEach(line -> {
                    String[] parts = line.trim().split("\\s+");
                    double percentage = Double.parseDouble(
                        parts[0].replace("%", ""));
                    
                    if (percentage > 5.0) {
                        log.warn("Hotspot detected: {} consuming {}%", 
                            parts[parts.length - 1], percentage);
                        
                        registry.gauge("hotspot.cpu.percentage",
                            Tags.of("method", parts[parts.length - 1]),
                            percentage);
                    }
                });
        }
    }
}
```

### Database Query Optimization

```java
@Service
public class DatabasePerformanceOptimizer {
    
    /**
     * Query performance monitoring
     */
    @Component
    public class SlowQueryDetector {
        
        @EventListener
        public void onQueryExecuted(QueryExecutedEvent event) {
            long duration = event.getDuration();
            String query = event.getQuery();
            
            if (duration > 1000) { // Queries taking > 1 second
                log.warn("Slow query detected ({}ms): {}", duration, query);
                
                // Analyze query plan
                QueryPlan plan = analyzeQueryPlan(query);
                
                // Suggest optimizations
                List<String> suggestions = suggestOptimizations(plan);
                
                // Record metrics
                registry.counter("database.slow_queries",
                    "table", extractTable(query),
                    "operation", extractOperation(query))
                    .increment();
                
                // Store for analysis
                slowQueryRepository.save(SlowQuery.builder()
                    .query(query)
                    .duration(duration)
                    .plan(plan)
                    .suggestions(suggestions)
                    .timestamp(Instant.now())
                    .build());
            }
        }
        
        private List<String> suggestOptimizations(QueryPlan plan) {
            List<String> suggestions = new ArrayList<>();
            
            // Check for missing indexes
            if (plan.hasTableScan()) {
                suggestions.add("Consider adding index on: " + 
                    plan.getTableScanColumns());
            }
            
            // Check for N+1 queries
            if (plan.getEstimatedRows() > 1000 && plan.hasNestedLoop()) {
                suggestions.add("Potential N+1 query - consider JOIN or batch fetch");
            }
            
            // Check for missing statistics
            if (plan.getEstimatedRows() != plan.getActualRows()) {
                suggestions.add("Statistics outdated - run ANALYZE TABLE");
            }
            
            return suggestions;
        }
    }
    
    /**
     * Connection pool optimization
     */
    @Configuration
    public class ConnectionPoolOptimizer {
        
        @Bean
        public HikariDataSource optimizedDataSource() {
            HikariConfig config = new HikariConfig();
            
            // Optimal pool sizing: connections = (core_count * 2) + disk_count
            int coreCount = Runtime.getRuntime().availableProcessors();
            int optimalPoolSize = (coreCount * 2) + 1;
            
            config.setMaximumPoolSize(optimalPoolSize);
            config.setMinimumIdle(optimalPoolSize / 2);
            
            // Connection testing
            config.setConnectionTestQuery("SELECT 1");
            config.setConnectionTimeout(5000); // 5 seconds
            config.setValidationTimeout(3000); // 3 seconds
            
            // Leak detection
            config.setLeakDetectionThreshold(60000); // 1 minute
            
            // Performance optimizations
            config.setAutoCommit(false);
            config.setReadOnly(false);
            config.setIsolateInternalQueries(true);
            
            // Statement caching
            config.addDataSourceProperty("cachePrepStmts", true);
            config.addDataSourceProperty("prepStmtCacheSize", 250);
            config.addDataSourceProperty("prepStmtCacheSqlLimit", 2048);
            
            return new HikariDataSource(config);
        }
        
        @Scheduled(fixedDelay = 60000)
        public void monitorPoolPerformance() {
            HikariPoolMXBean poolMXBean = dataSource.getHikariPoolMXBean();
            
            // Pool metrics
            int active = poolMXBean.getActiveConnections();
            int idle = poolMXBean.getIdleConnections();
            int waiting = poolMXBean.getThreadsAwaitingConnection();
            int total = poolMXBean.getTotalConnections();
            
            // Auto-scaling logic
            if (waiting > 0 && total < dataSource.getMaximumPoolSize()) {
                log.info("Connection starvation detected, consider increasing pool size");
                
                // Dynamic adjustment (if enabled)
                if (dynamicPoolSizing) {
                    int newSize = Math.min(total + 2, maxAllowedConnections);
                    dataSource.setMaximumPoolSize(newSize);
                }
            }
            
            // Record metrics
            registry.gauge("db.pool.active", active);
            registry.gauge("db.pool.idle", idle);
            registry.gauge("db.pool.waiting", waiting);
        }
    }
}
```

---

## Part 2: Caching Optimization Strategies

### Multi-Level Cache Optimization

```java
@Service
public class CacheOptimizationService {
    
    /**
     * Intelligent cache warming
     */
    @Component
    public class CacheWarmer {
        
        @EventListener(ApplicationReadyEvent.class)
        public void warmCache() {
            log.info("Starting cache warming");
            
            // Identify frequently accessed data
            List<String> hotKeys = identifyHotKeys();
            
            // Parallel cache warming
            CompletableFuture<?>[] futures = hotKeys.stream()
                .map(key -> CompletableFuture.runAsync(() -> {
                    try {
                        Object value = loadFromDatabase(key);
                        cache.put(key, value);
                    } catch (Exception e) {
                        log.error("Failed to warm cache for key: {}", key, e);
                    }
                }, cacheWarmingExecutor))
                .toArray(CompletableFuture[]::new);
            
            CompletableFuture.allOf(futures).join();
            
            log.info("Cache warming completed. Warmed {} keys", hotKeys.size());
        }
        
        private List<String> identifyHotKeys() {
            // Query access logs for frequently accessed keys
            return jdbcTemplate.query(
                "SELECT key FROM access_logs " +
                "WHERE timestamp > NOW() - INTERVAL '24 hours' " +
                "GROUP BY key " +
                "HAVING COUNT(*) > 100 " +
                "ORDER BY COUNT(*) DESC " +
                "LIMIT 1000",
                (rs, rowNum) -> rs.getString("key")
            );
        }
    }
    
    /**
     * Cache hit rate optimization
     */
    @Component
    public class CacheOptimizer {
        
        private final Map<String, CacheStats> cacheStats = new ConcurrentHashMap<>();
        
        @Scheduled(fixedDelay = 300000) // Every 5 minutes
        public void optimizeCache() {
            cacheStats.forEach((cacheName, stats) -> {
                double hitRate = stats.getHitRate();
                
                if (hitRate < 0.5) { // Less than 50% hit rate
                    log.warn("Low hit rate for cache {}: {}%", 
                        cacheName, hitRate * 100);
                    
                    // Analyze miss patterns
                    analyzeMissPatterns(cacheName, stats);
                    
                    // Adjust cache configuration
                    adjustCacheConfig(cacheName, stats);
                }
                
                // Record metrics
                registry.gauge("cache.hit_rate", hitRate,
                    "cache", cacheName);
                registry.gauge("cache.eviction_rate", stats.getEvictionRate(),
                    "cache", cacheName);
            });
        }
        
        private void adjustCacheConfig(String cacheName, CacheStats stats) {
            Cache cache = cacheManager.getCache(cacheName);
            
            // Increase size if eviction rate is high
            if (stats.getEvictionRate() > 0.2) { // > 20% eviction
                long currentSize = cache.getMaxSize();
                long newSize = (long) (currentSize * 1.5);
                
                log.info("Increasing cache {} size from {} to {}", 
                    cacheName, currentSize, newSize);
                
                cache.setMaxSize(newSize);
            }
            
            // Adjust TTL based on access patterns
            if (stats.getAverageAge() < 60) { // Accessed within 1 minute
                cache.setTTL(Duration.ofMinutes(5));
            } else if (stats.getAverageAge() < 3600) { // Within 1 hour
                cache.setTTL(Duration.ofHours(1));
            } else {
                cache.setTTL(Duration.ofHours(24));
            }
        }
    }
}
```

---

## Part 3: Network and I/O Optimization

### HTTP Client Optimization

```java
@Configuration
public class HttpClientOptimization {
    
    /**
     * Optimized HTTP client with connection pooling
     */
    @Bean
    public CloseableHttpClient optimizedHttpClient() {
        // Connection pool configuration
        PoolingHttpClientConnectionManager connectionManager = 
            new PoolingHttpClientConnectionManager();
        connectionManager.setMaxTotal(200); // Total connections
        connectionManager.setDefaultMaxPerRoute(20); // Per route limit
        
        // Socket configuration
        SocketConfig socketConfig = SocketConfig.custom()
            .setTcpNoDelay(true) // Disable Nagle's algorithm
            .setSoKeepAlive(true) // Keep-alive
            .setSoReuseAddress(true)
            .build();
        connectionManager.setDefaultSocketConfig(socketConfig);
        
        // Request configuration
        RequestConfig requestConfig = RequestConfig.custom()
            .setConnectTimeout(5000) // 5 seconds
            .setSocketTimeout(10000) // 10 seconds
            .setConnectionRequestTimeout(3000) // 3 seconds
            .build();
        
        // Connection keep-alive strategy
        ConnectionKeepAliveStrategy keepAliveStrategy = (response, context) -> {
            HeaderElementIterator it = new BasicHeaderElementIterator(
                response.headerIterator(HTTP.CONN_KEEP_ALIVE));
            
            while (it.hasNext()) {
                HeaderElement he = it.nextElement();
                String param = he.getName();
                String value = he.getValue();
                
                if (value != null && param.equalsIgnoreCase("timeout")) {
                    return Long.parseLong(value) * 1000;
                }
            }
            
            return 30 * 1000; // Default 30 seconds
        };
        
        return HttpClients.custom()
            .setConnectionManager(connectionManager)
            .setDefaultRequestConfig(requestConfig)
            .setKeepAliveStrategy(keepAliveStrategy)
            .setRetryHandler(new DefaultHttpRequestRetryHandler(3, true))
            .evictExpiredConnections()
            .evictIdleConnections(60, TimeUnit.SECONDS)
            .build();
    }
    
    /**
     * HTTP/2 client for improved performance
     */
    @Bean
    public WebClient http2WebClient() {
        HttpClient httpClient = HttpClient.create()
            .protocol(HttpProtocol.H2, HttpProtocol.HTTP11)
            .compress(true)
            .responseTimeout(Duration.ofSeconds(10))
            .doOnConnected(conn -> 
                conn.addHandlerLast(new ReadTimeoutHandler(10))
                    .addHandlerLast(new WriteTimeoutHandler(10)));
        
        return WebClient.builder()
            .clientConnector(new ReactorClientHttpConnector(httpClient))
            .defaultHeader(HttpHeaders.ACCEPT_ENCODING, "gzip, deflate")
            .filter(ExchangeFilterFunction.ofRequestProcessor(
                clientRequest -> {
                    log.debug("Request: {} {}", 
                        clientRequest.method(), clientRequest.url());
                    return Mono.just(clientRequest);
                }))
            .build();
    }
}
```

### Batch Processing Optimization

```java
@Service
public class BatchProcessingOptimizer {
    
    /**
     * Optimized batch processor with dynamic sizing
     */
    public class DynamicBatchProcessor<T> {
        
        private final BlockingQueue<T> queue = new LinkedBlockingQueue<>();
        private final AtomicInteger batchSize = new AtomicInteger(100);
        private final ScheduledExecutorService scheduler = 
            Executors.newScheduledThreadPool(1);
        
        @PostConstruct
        public void start() {
            // Process batches periodically
            scheduler.scheduleWithFixedDelay(
                this::processBatch, 0, 100, TimeUnit.MILLISECONDS);
        }
        
        public void add(T item) {
            queue.offer(item);
            
            // Trigger immediate processing if queue is large
            if (queue.size() > batchSize.get() * 2) {
                processBatch();
            }
        }
        
        private void processBatch() {
            List<T> batch = new ArrayList<>();
            queue.drainTo(batch, batchSize.get());
            
            if (batch.isEmpty()) {
                return;
            }
            
            long startTime = System.currentTimeMillis();
            
            try {
                // Process batch
                processBatchItems(batch);
                
                long duration = System.currentTimeMillis() - startTime;
                
                // Adjust batch size based on processing time
                adjustBatchSize(batch.size(), duration);
                
                // Record metrics
                registry.timer("batch.processing.time")
                    .record(duration, TimeUnit.MILLISECONDS);
                registry.gauge("batch.size", batch.size());
                
            } catch (Exception e) {
                log.error("Batch processing failed", e);
                // Return items to queue for retry
                queue.addAll(batch);
            }
        }
        
        private void adjustBatchSize(int processed, long duration) {
            // Target: 100ms processing time
            double targetTime = 100.0;
            double ratio = targetTime / duration;
            
            int newSize = (int) (processed * ratio);
            newSize = Math.max(10, Math.min(1000, newSize)); // Bounds
            
            batchSize.set(newSize);
            
            log.debug("Adjusted batch size from {} to {} based on {}ms processing time",
                processed, newSize, duration);
        }
    }
}
```

---

## Part 4: JVM Tuning and Memory Optimization

### JVM Configuration for Performance

```bash
#!/bin/bash
# Optimized JVM settings for production

# Heap sizing
HEAP_SIZE="8g"
MAX_DIRECT_MEMORY="2g"

# GC Selection and tuning (G1GC for low latency)
GC_OPTIONS="-XX:+UseG1GC \
    -XX:MaxGCPauseMillis=200 \
    -XX:G1HeapRegionSize=16m \
    -XX:InitiatingHeapOccupancyPercent=45 \
    -XX:G1ReservePercent=10 \
    -XX:ParallelGCThreads=8 \
    -XX:ConcGCThreads=2"

# Memory settings
MEMORY_OPTIONS="-Xms${HEAP_SIZE} \
    -Xmx${HEAP_SIZE} \
    -XX:MaxDirectMemorySize=${MAX_DIRECT_MEMORY} \
    -XX:+AlwaysPreTouch \
    -XX:+UseCompressedOops \
    -XX:+UseCompressedClassPointers"

# Performance optimizations
PERFORMANCE_OPTIONS="-XX:+UseStringDeduplication \
    -XX:+OptimizeStringConcat \
    -XX:+UseNUMA \
    -XX:+UseBiasedLocking \
    -XX:+UseFastAccessorMethods"

# JIT compiler settings
JIT_OPTIONS="-XX:ReservedCodeCacheSize=256m \
    -XX:InitialCodeCacheSize=64m \
    -XX:+TieredCompilation \
    -XX:TieredStopAtLevel=4"

# Monitoring and diagnostics
MONITORING_OPTIONS="-XX:+UnlockDiagnosticVMOptions \
    -XX:+PrintGCDetails \
    -XX:+PrintGCDateStamps \
    -XX:+PrintTenuringDistribution \
    -Xloggc:/var/log/app/gc.log \
    -XX:+UseGCLogFileRotation \
    -XX:NumberOfGCLogFiles=10 \
    -XX:GCLogFileSize=10M \
    -XX:+HeapDumpOnOutOfMemoryError \
    -XX:HeapDumpPath=/var/dumps/ \
    -XX:+ExitOnOutOfMemoryError"

# Combine all options
JAVA_OPTS="${MEMORY_OPTIONS} ${GC_OPTIONS} ${PERFORMANCE_OPTIONS} ${JIT_OPTIONS} ${MONITORING_OPTIONS}"

# Start application
java ${JAVA_OPTS} -jar application.jar
```

### Memory Leak Detection

```java
@Service
public class MemoryLeakDetector {
    
    private final Map<String, WeakReference<Object>> objectTracker = 
        new ConcurrentHashMap<>();
    
    /**
     * Track object allocation and detect leaks
     */
    @Scheduled(fixedDelay = 60000) // Every minute
    public void detectMemoryLeaks() {
        Runtime runtime = Runtime.getRuntime();
        long usedMemory = runtime.totalMemory() - runtime.freeMemory();
        
        // Force GC to clean up weak references
        System.gc();
        
        // Check for leaked objects
        objectTracker.entrySet().removeIf(entry -> {
            WeakReference<Object> ref = entry.getValue();
            if (ref.get() == null) {
                // Object was garbage collected - good
                return true;
            }
            
            // Object still alive - potential leak
            String key = entry.getKey();
            if (isLikelyLeak(key)) {
                log.warn("Potential memory leak detected: {}", key);
                registry.counter("memory.potential_leaks",
                    "type", extractType(key)).increment();
            }
            
            return false;
        });
        
        // Monitor heap usage
        double heapUsagePercent = (double) usedMemory / runtime.maxMemory() * 100;
        
        if (heapUsagePercent > 80) {
            log.error("High heap usage: {}%", heapUsagePercent);
            
            // Trigger heap dump
            triggerHeapDump();
        }
        
        registry.gauge("memory.heap.usage.percent", heapUsagePercent);
    }
    
    /**
     * Thread-local leak detection
     */
    @Component
    public class ThreadLocalLeakDetector {
        
        @EventListener
        public void onRequestCompleted(RequestCompletedEvent event) {
            Thread currentThread = Thread.currentThread();
            
            try {
                Field threadLocalsField = Thread.class.getDeclaredField("threadLocals");
                threadLocalsField.setAccessible(true);
                Object threadLocalMap = threadLocalsField.get(currentThread);
                
                if (threadLocalMap != null) {
                    Field tableField = threadLocalMap.getClass().getDeclaredField("table");
                    tableField.setAccessible(true);
                    Object[] table = (Object[]) tableField.get(threadLocalMap);
                    
                    int count = 0;
                    for (Object entry : table) {
                        if (entry != null) {
                            count++;
                        }
                    }
                    
                    if (count > 10) { // Threshold for concern
                        log.warn("Thread {} has {} thread-local values - potential leak",
                            currentThread.getName(), count);
                    }
                }
            } catch (Exception e) {
                log.error("Failed to inspect thread locals", e);
            }
        }
    }
}
```

---

## Part 5: Scaling Strategies

### Horizontal Scaling Optimization

```yaml
# Kubernetes HPA with custom metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: app
  minReplicas: 3
  maxReplicas: 100
  metrics:
  # CPU-based scaling
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  
  # Memory-based scaling
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  
  # Custom metrics
  - type: Pods
    pods:
      metric:
        name: request_latency_p99
      target:
        type: AverageValue
        averageValue: "500m" # 500ms
  
  # External metrics (from Prometheus)
  - type: External
    external:
      metric:
        name: queue_depth
        selector:
          matchLabels:
            queue: "processing"
      target:
        type: Value
        value: "30"
  
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100 # Double pods
        periodSeconds: 60
      - type: Pods
        value: 10 # Or add 10 pods
        periodSeconds: 60
      selectPolicy: Max # Use the larger
    
    scaleDown:
      stabilizationWindowSeconds: 300 # Wait 5 minutes
      policies:
      - type: Percent
        value: 50 # Remove half
        periodSeconds: 60
      - type: Pods
        value: 5 # Or remove 5 pods
        periodSeconds: 60
      selectPolicy: Min # Use the smaller
```

### Vertical Scaling Optimization

```java
@Service
public class VerticalScalingOptimizer {
    
    /**
     * Dynamic thread pool sizing
     */
    @Component
    public class DynamicThreadPoolManager {
        
        private final ThreadPoolExecutor executor;
        
        @Scheduled(fixedDelay = 30000) // Every 30 seconds
        public void optimizeThreadPool() {
            // Get current metrics
            int activeThreads = executor.getActiveCount();
            int poolSize = executor.getPoolSize();
            int queueSize = executor.getQueue().size();
            long completedTasks = executor.getCompletedTaskCount();
            
            // Calculate optimal size
            double utilization = (double) activeThreads / poolSize;
            
            if (utilization > 0.8 && queueSize > 10) {
                // Increase pool size
                int newSize = Math.min(poolSize + 5, 200);
                executor.setMaximumPoolSize(newSize);
                executor.setCorePoolSize(newSize / 2);
                
                log.info("Increased thread pool size to {}", newSize);
                
            } else if (utilization < 0.3 && poolSize > 10) {
                // Decrease pool size
                int newSize = Math.max(poolSize - 5, 10);
                executor.setMaximumPoolSize(newSize);
                executor.setCorePoolSize(newSize / 2);
                
                log.info("Decreased thread pool size to {}", newSize);
            }
            
            // Record metrics
            registry.gauge("threadpool.utilization", utilization);
            registry.gauge("threadpool.queue.size", queueSize);
        }
    }
}
```

---

## Summary: Performance Optimization Checklist

### Pre-Production Performance Testing

```java
@SpringBootTest
public class PerformanceTest {
    
    @Test
    public void loadTest() {
        int threads = 100;
        int requestsPerThread = 1000;
        
        ExecutorService executor = Executors.newFixedThreadPool(threads);
        CountDownLatch latch = new CountDownLatch(threads);
        
        long startTime = System.currentTimeMillis();
        
        for (int i = 0; i < threads; i++) {
            executor.submit(() -> {
                try {
                    for (int j = 0; j < requestsPerThread; j++) {
                        // Make request
                        ResponseEntity<String> response = 
                            restTemplate.getForEntity("/api/test", String.class);
                        
                        assertEquals(200, response.getStatusCodeValue());
                    }
                } finally {
                    latch.countDown();
                }
            });
        }
        
        latch.await();
        
        long duration = System.currentTimeMillis() - startTime;
        double rps = (threads * requestsPerThread * 1000.0) / duration;
        
        log.info("Performance: {} requests/second", rps);
        assertTrue(rps > 1000, "Should handle > 1000 RPS");
    }
}
```

### Optimization Priority Matrix

| Area | Impact | Effort | Priority |
|------|--------|--------|----------|
| Database queries | High | Medium | 1 |
| Caching | High | Low | 1 |
| Connection pooling | Medium | Low | 2 |
| JVM tuning | Medium | Medium | 2 |
| HTTP client optimization | Medium | Low | 2 |
| Thread pool sizing | Low | Low | 3 |
| Code-level optimizations | Low | High | 3 |

Remember: **Measure first, optimize second. Premature optimization is the root of all evil.**