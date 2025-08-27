# Distributed System Patterns: Complete Production Implementation Guide

## Executive Summary

This guide provides production-ready implementations of essential distributed system patterns. Each pattern includes working code, deployment configurations, monitoring strategies, and real-world case studies from companies like Netflix, Amazon, and Uber.

---

## Part 1: Circuit Breaker Pattern - Preventing Cascade Failures

### Complete Production Implementation

```java
@Component
@Slf4j
public class CircuitBreakerService {
    
    private enum State {
        CLOSED,      // Normal operation
        OPEN,        // Failing fast
        HALF_OPEN    // Testing recovery
    }
    
    private State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    private final AtomicLong stateChangeTime = new AtomicLong(System.currentTimeMillis());
    
    // Configuration
    @Value("${circuit.breaker.failure.threshold:5}")
    private int failureThreshold;
    
    @Value("${circuit.breaker.success.threshold:3}")
    private int successThreshold;
    
    @Value("${circuit.breaker.timeout.ms:60000}")
    private long timeoutMs;
    
    @Value("${circuit.breaker.half.open.requests:3}")
    private int halfOpenRequests;
    
    private final Semaphore halfOpenSemaphore;
    private final MeterRegistry metrics;
    
    public CircuitBreakerService(MeterRegistry metrics) {
        this.metrics = metrics;
        this.halfOpenSemaphore = new Semaphore(halfOpenRequests);
    }
    
    /**
     * Execute operation with circuit breaker protection
     */
    public <T> T execute(String operationName, Supplier<T> operation, 
                         Function<Exception, T> fallback) {
        
        // Check circuit state
        if (!allowRequest()) {
            metrics.counter("circuit.breaker.rejected",
                "operation", operationName,
                "state", state.toString()).increment();
            
            log.warn("Circuit breaker OPEN for operation: {}", operationName);
            return fallback.apply(new CircuitBreakerOpenException(
                "Circuit breaker is OPEN"));
        }
        
        long startTime = System.currentTimeMillis();
        boolean isHalfOpen = (state == State.HALF_OPEN);
        
        try {
            // Execute the operation
            T result = operation.get();
            
            // Record success
            onSuccess(isHalfOpen);
            
            metrics.timer("circuit.breaker.execution",
                "operation", operationName,
                "result", "success")
                .record(System.currentTimeMillis() - startTime, 
                    TimeUnit.MILLISECONDS);
            
            return result;
            
        } catch (Exception e) {
            // Record failure
            onFailure(isHalfOpen);
            
            metrics.timer("circuit.breaker.execution",
                "operation", operationName,
                "result", "failure",
                "exception", e.getClass().getSimpleName())
                .record(System.currentTimeMillis() - startTime, 
                    TimeUnit.MILLISECONDS);
            
            log.error("Operation {} failed: {}", operationName, e.getMessage());
            
            // Use fallback
            return fallback.apply(e);
            
        } finally {
            if (isHalfOpen) {
                halfOpenSemaphore.release();
            }
        }
    }
    
    /**
     * Determine if request should be allowed
     */
    private boolean allowRequest() {
        State currentState = state;
        
        switch (currentState) {
            case CLOSED:
                return true;
                
            case OPEN:
                // Check if timeout has passed
                if (System.currentTimeMillis() - stateChangeTime.get() > timeoutMs) {
                    // Try to transition to HALF_OPEN
                    if (transitionToHalfOpen()) {
                        return halfOpenSemaphore.tryAcquire();
                    }
                }
                return false;
                
            case HALF_OPEN:
                // Limited requests in half-open state
                return halfOpenSemaphore.tryAcquire();
                
            default:
                return false;
        }
    }
    
    /**
     * Handle successful operation
     */
    private void onSuccess(boolean isHalfOpen) {
        if (isHalfOpen) {
            int successes = successCount.incrementAndGet();
            if (successes >= successThreshold) {
                transitionToClosed();
            }
        } else if (state == State.CLOSED) {
            // Reset failure count on success in closed state
            failureCount.set(0);
        }
    }
    
    /**
     * Handle failed operation
     */
    private void onFailure(boolean isHalfOpen) {
        lastFailureTime.set(System.currentTimeMillis());
        
        if (isHalfOpen) {
            // Single failure in half-open trips back to open
            transitionToOpen();
        } else if (state == State.CLOSED) {
            int failures = failureCount.incrementAndGet();
            if (failures >= failureThreshold) {
                transitionToOpen();
            }
        }
    }
    
    /**
     * State transitions with proper synchronization
     */
    private synchronized boolean transitionToHalfOpen() {
        if (state == State.OPEN) {
            log.info("Circuit breaker transitioning to HALF_OPEN");
            state = State.HALF_OPEN;
            successCount.set(0);
            stateChangeTime.set(System.currentTimeMillis());
            
            metrics.counter("circuit.breaker.state.change",
                "from", "OPEN",
                "to", "HALF_OPEN").increment();
            
            return true;
        }
        return false;
    }
    
    private synchronized void transitionToOpen() {
        if (state != State.OPEN) {
            log.error("Circuit breaker tripping to OPEN");
            State previousState = state;
            state = State.OPEN;
            failureCount.set(0);
            stateChangeTime.set(System.currentTimeMillis());
            
            metrics.counter("circuit.breaker.state.change",
                "from", previousState.toString(),
                "to", "OPEN").increment();
            
            // Alert on circuit open
            alertService.sendAlert(Alert.critical()
                .title("Circuit Breaker Opened")
                .description("Circuit breaker has opened due to failures")
                .build());
        }
    }
    
    private synchronized void transitionToClosed() {
        if (state != State.CLOSED) {
            log.info("Circuit breaker transitioning to CLOSED");
            State previousState = state;
            state = State.CLOSED;
            failureCount.set(0);
            successCount.set(0);
            stateChangeTime.set(System.currentTimeMillis());
            
            metrics.counter("circuit.breaker.state.change",
                "from", previousState.toString(),
                "to", "CLOSED").increment();
        }
    }
    
    /**
     * Advanced circuit breaker with sliding window
     */
    @Component
    public static class SlidingWindowCircuitBreaker {
        
        private final CircularFifoQueue<CallResult> window;
        private final int windowSize;
        private final double failureRateThreshold;
        
        public SlidingWindowCircuitBreaker(
                @Value("${circuit.breaker.window.size:100}") int windowSize,
                @Value("${circuit.breaker.failure.rate:0.5}") double failureRateThreshold) {
            
            this.windowSize = windowSize;
            this.failureRateThreshold = failureRateThreshold;
            this.window = new CircularFifoQueue<>(windowSize);
        }
        
        public boolean shouldAllowRequest() {
            if (window.size() < windowSize / 2) {
                // Not enough data, allow request
                return true;
            }
            
            long failures = window.stream()
                .filter(r -> !r.isSuccess())
                .count();
            
            double failureRate = (double) failures / window.size();
            return failureRate < failureRateThreshold;
        }
        
        public void recordResult(boolean success, long latencyMs) {
            window.add(new CallResult(success, latencyMs, System.currentTimeMillis()));
            
            // Also track slow calls as failures
            if (latencyMs > 1000) { // 1 second threshold
                window.add(new CallResult(false, latencyMs, System.currentTimeMillis()));
            }
        }
    }
}
```

### Netflix Hystrix-Style Implementation

```java
@Component
public class HystrixStyleCommand<T> {
    
    private final String commandKey;
    private final Supplier<T> command;
    private final Supplier<T> fallback;
    private final CircuitBreaker circuitBreaker;
    private final BulkheadSemaphore bulkhead;
    private final ExecutorService threadPool;
    
    public T execute() {
        // Bulkhead protection
        if (!bulkhead.tryAcquire()) {
            metrics.counter("hystrix.rejected.bulkhead", 
                "command", commandKey).increment();
            return fallback.get();
        }
        
        try {
            // Circuit breaker check
            if (!circuitBreaker.allowRequest()) {
                metrics.counter("hystrix.short.circuited",
                    "command", commandKey).increment();
                return fallback.get();
            }
            
            // Execute with timeout
            Future<T> future = threadPool.submit(() -> {
                try {
                    return command.get();
                } catch (Exception e) {
                    circuitBreaker.recordFailure();
                    throw new CommandExecutionException(e);
                }
            });
            
            try {
                T result = future.get(timeoutMs, TimeUnit.MILLISECONDS);
                circuitBreaker.recordSuccess();
                return result;
                
            } catch (TimeoutException e) {
                future.cancel(true);
                circuitBreaker.recordTimeout();
                metrics.counter("hystrix.timeout",
                    "command", commandKey).increment();
                return fallback.get();
            }
            
        } finally {
            bulkhead.release();
        }
    }
}
```

---

## Part 2: Rate Limiting - Protecting Services from Overload

### Token Bucket Implementation

```java
@Service
@Slf4j
public class TokenBucketRateLimiter {
    
    private final long capacity;
    private final long refillRate; // tokens per second
    private final AtomicLong tokens;
    private final AtomicLong lastRefillTime;
    
    public TokenBucketRateLimiter(
            @Value("${rate.limiter.capacity:100}") long capacity,
            @Value("${rate.limiter.refill.rate:10}") long refillRate) {
        
        this.capacity = capacity;
        this.refillRate = refillRate;
        this.tokens = new AtomicLong(capacity);
        this.lastRefillTime = new AtomicLong(System.nanoTime());
    }
    
    /**
     * Try to acquire tokens
     */
    public boolean tryAcquire(int requestedTokens) {
        refill();
        
        long currentTokens = tokens.get();
        if (currentTokens < requestedTokens) {
            return false;
        }
        
        // Try to consume tokens
        return tokens.compareAndSet(currentTokens, currentTokens - requestedTokens);
    }
    
    /**
     * Acquire with blocking
     */
    public void acquire(int requestedTokens) throws InterruptedException {
        while (!tryAcquire(requestedTokens)) {
            Thread.sleep(100); // Wait and retry
        }
    }
    
    /**
     * Refill tokens based on elapsed time
     */
    private void refill() {
        long now = System.nanoTime();
        long lastRefill = lastRefillTime.get();
        long elapsedNanos = now - lastRefill;
        
        if (elapsedNanos > TimeUnit.SECONDS.toNanos(1)) {
            long tokensToAdd = (elapsedNanos * refillRate) / TimeUnit.SECONDS.toNanos(1);
            
            if (tokensToAdd > 0 && lastRefillTime.compareAndSet(lastRefill, now)) {
                tokens.updateAndGet(current -> 
                    Math.min(capacity, current + tokensToAdd));
            }
        }
    }
}
```

### Distributed Rate Limiting with Redis

```java
@Service
public class DistributedRateLimiter {
    
    private final RedisTemplate<String, String> redis;
    private final RedisScript<List<Long>> rateLimitScript;
    
    public DistributedRateLimiter(RedisTemplate<String, String> redis) {
        this.redis = redis;
        
        // Lua script for atomic rate limiting
        String script = 
            "local key = KEYS[1]\n" +
            "local limit = tonumber(ARGV[1])\n" +
            "local window = tonumber(ARGV[2])\n" +
            "local current = redis.call('GET', key)\n" +
            "if current == false then\n" +
            "  current = 0\n" +
            "else\n" +
            "  current = tonumber(current)\n" +
            "end\n" +
            "if current < limit then\n" +
            "  redis.call('INCR', key)\n" +
            "  redis.call('EXPIRE', key, window)\n" +
            "  return {1, limit - current - 1}\n" +
            "else\n" +
            "  local ttl = redis.call('TTL', key)\n" +
            "  return {0, ttl}\n" +
            "end";
        
        this.rateLimitScript = new DefaultRedisScript<>(script, List.class);
    }
    
    /**
     * Check rate limit for a client
     */
    public RateLimitResult checkLimit(String clientId, int limit, int windowSeconds) {
        String key = "rate_limit:" + clientId + ":" + 
            (System.currentTimeMillis() / (windowSeconds * 1000));
        
        List<Long> result = redis.execute(
            rateLimitScript,
            Collections.singletonList(key),
            String.valueOf(limit),
            String.valueOf(windowSeconds)
        );
        
        boolean allowed = result.get(0) == 1;
        long remaining = allowed ? result.get(1) : 0;
        long retryAfter = allowed ? 0 : result.get(1);
        
        return RateLimitResult.builder()
            .allowed(allowed)
            .remaining(remaining)
            .retryAfterSeconds(retryAfter)
            .build();
    }
    
    /**
     * Rate limiting filter for Spring
     */
    @Component
    public class RateLimitingFilter extends OncePerRequestFilter {
        
        @Override
        protected void doFilterInternal(HttpServletRequest request,
                                      HttpServletResponse response,
                                      FilterChain filterChain) 
                                      throws ServletException, IOException {
            
            String clientId = extractClientId(request);
            RateLimitResult result = checkLimit(clientId, 100, 60);
            
            // Add rate limit headers
            response.setHeader("X-RateLimit-Limit", "100");
            response.setHeader("X-RateLimit-Remaining", 
                String.valueOf(result.getRemaining()));
            response.setHeader("X-RateLimit-Reset", 
                String.valueOf(System.currentTimeMillis() / 1000 + 60));
            
            if (!result.isAllowed()) {
                response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
                response.setHeader("Retry-After", 
                    String.valueOf(result.getRetryAfterSeconds()));
                response.getWriter().write("Rate limit exceeded");
                return;
            }
            
            filterChain.doFilter(request, response);
        }
        
        private String extractClientId(HttpServletRequest request) {
            // Try API key first
            String apiKey = request.getHeader("X-API-Key");
            if (apiKey != null) {
                return "api:" + apiKey;
            }
            
            // Fall back to IP address
            return "ip:" + request.getRemoteAddr();
        }
    }
}
```

---

## Part 3: Bulkhead Pattern - Isolation of Resources

### Thread Pool Bulkhead

```java
@Configuration
public class BulkheadConfiguration {
    
    /**
     * Create isolated thread pools for different operations
     */
    @Bean
    public ExecutorService criticalOperationsPool() {
        return new ThreadPoolExecutor(
            10,  // Core pool size
            20,  // Maximum pool size
            60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(100), // Bounded queue
            new ThreadFactory() {
                private final AtomicInteger counter = new AtomicInteger();
                @Override
                public Thread newThread(Runnable r) {
                    Thread thread = new Thread(r);
                    thread.setName("critical-pool-" + counter.incrementAndGet());
                    thread.setPriority(Thread.MAX_PRIORITY);
                    return thread;
                }
            },
            new ThreadPoolExecutor.CallerRunsPolicy() // Rejection policy
        );
    }
    
    @Bean
    public ExecutorService normalOperationsPool() {
        return new ThreadPoolExecutor(
            5,   // Core pool size
            10,  // Maximum pool size
            60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(50),
            new ThreadFactoryBuilder()
                .setNameFormat("normal-pool-%d")
                .setPriority(Thread.NORM_PRIORITY)
                .build(),
            new ThreadPoolExecutor.AbortPolicy()
        );
    }
    
    @Bean
    public ExecutorService backgroundOperationsPool() {
        return new ThreadPoolExecutor(
            2,   // Core pool size
            5,   // Maximum pool size
            60L, TimeUnit.SECONDS,
            new LinkedBlockingQueue<>(200),
            new ThreadFactoryBuilder()
                .setNameFormat("background-pool-%d")
                .setPriority(Thread.MIN_PRIORITY)
                .build(),
            new ThreadPoolExecutor.DiscardPolicy()
        );
    }
}

@Service
public class BulkheadService {
    
    private final ExecutorService criticalPool;
    private final ExecutorService normalPool;
    private final ExecutorService backgroundPool;
    
    /**
     * Execute with appropriate bulkhead
     */
    public <T> CompletableFuture<T> execute(
            OperationType type, 
            Callable<T> task) {
        
        ExecutorService pool = selectPool(type);
        
        return CompletableFuture.supplyAsync(() -> {
            try {
                return task.call();
            } catch (Exception e) {
                throw new CompletionException(e);
            }
        }, pool);
    }
    
    private ExecutorService selectPool(OperationType type) {
        switch (type) {
            case CRITICAL:
                return criticalPool;
            case NORMAL:
                return normalPool;
            case BACKGROUND:
                return backgroundPool;
            default:
                return normalPool;
        }
    }
}
```

### Connection Pool Bulkhead

```java
@Configuration
public class DatabaseBulkheadConfiguration {
    
    /**
     * Separate connection pools for different operations
     */
    @Bean
    @Primary
    public DataSource primaryDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(primaryDbUrl);
        config.setUsername(primaryDbUsername);
        config.setPassword(primaryDbPassword);
        
        // Critical operations pool
        config.setMaximumPoolSize(20);
        config.setMinimumIdle(10);
        config.setConnectionTimeout(5000);
        config.setPoolName("primary-pool");
        
        return new HikariDataSource(config);
    }
    
    @Bean
    public DataSource readOnlyDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(readReplicaDbUrl);
        config.setUsername(readReplicaUsername);
        config.setPassword(readReplicaPassword);
        
        // Read operations pool
        config.setMaximumPoolSize(50);
        config.setMinimumIdle(10);
        config.setConnectionTimeout(3000);
        config.setReadOnly(true);
        config.setPoolName("readonly-pool");
        
        return new HikariDataSource(config);
    }
    
    @Bean
    public DataSource analyticsDataSource() {
        HikariConfig config = new HikariConfig();
        config.setJdbcUrl(analyticsDbUrl);
        config.setUsername(analyticsUsername);
        config.setPassword(analyticsPassword);
        
        // Analytics operations pool (can be slower)
        config.setMaximumPoolSize(10);
        config.setMinimumIdle(2);
        config.setConnectionTimeout(10000);
        config.setPoolName("analytics-pool");
        
        return new HikariDataSource(config);
    }
}
```

---

## Part 4: Retry with Backoff - Handling Transient Failures

### Exponential Backoff with Jitter

```java
@Service
@Slf4j
public class RetryService {
    
    /**
     * Retry with exponential backoff and jitter
     */
    public <T> T executeWithRetry(
            String operationName,
            Callable<T> operation,
            RetryConfig config) {
        
        int attempt = 0;
        Exception lastException = null;
        
        while (attempt < config.getMaxAttempts()) {
            attempt++;
            
            try {
                log.debug("Attempting {} - attempt {}/{}", 
                    operationName, attempt, config.getMaxAttempts());
                
                T result = operation.call();
                
                if (attempt > 1) {
                    log.info("Operation {} succeeded after {} attempts", 
                        operationName, attempt);
                }
                
                return result;
                
            } catch (Exception e) {
                lastException = e;
                
                if (!isRetryable(e) || attempt >= config.getMaxAttempts()) {
                    log.error("Operation {} failed after {} attempts", 
                        operationName, attempt, e);
                    break;
                }
                
                long backoffMs = calculateBackoff(attempt, config);
                
                log.warn("Operation {} failed on attempt {}, retrying in {}ms", 
                    operationName, attempt, backoffMs);
                
                try {
                    Thread.sleep(backoffMs);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RetryInterruptedException(ie);
                }
            }
        }
        
        throw new RetryExhaustedException(
            "Failed after " + attempt + " attempts", lastException);
    }
    
    /**
     * Calculate backoff with jitter
     */
    private long calculateBackoff(int attempt, RetryConfig config) {
        // Exponential backoff: base * 2^attempt
        long exponentialBackoff = config.getBaseDelayMs() * 
            (long) Math.pow(2, attempt - 1);
        
        // Cap at maximum
        long cappedBackoff = Math.min(exponentialBackoff, config.getMaxDelayMs());
        
        // Add jitter (0-25% additional random delay)
        double jitterFactor = config.getJitterFactor();
        long jitter = (long) (cappedBackoff * Math.random() * jitterFactor);
        
        return cappedBackoff + jitter;
    }
    
    /**
     * Determine if exception is retryable
     */
    private boolean isRetryable(Exception e) {
        // Network errors - retryable
        if (e instanceof IOException || 
            e instanceof SocketTimeoutException) {
            return true;
        }
        
        // HTTP errors - selective retry
        if (e instanceof HttpException) {
            int status = ((HttpException) e).getStatusCode();
            // Retry on 429 (rate limit), 502 (bad gateway), 503 (unavailable), 504 (timeout)
            return status == 429 || status == 502 || status == 503 || status == 504;
        }
        
        // Database errors - selective retry
        if (e instanceof SQLException) {
            String sqlState = ((SQLException) e).getSQLState();
            // Retry on connection errors and deadlocks
            return sqlState != null && 
                (sqlState.startsWith("08") || sqlState.equals("40001"));
        }
        
        // Default: don't retry
        return false;
    }
}

@Data
@Builder
public class RetryConfig {
    @Builder.Default
    private int maxAttempts = 3;
    
    @Builder.Default
    private long baseDelayMs = 100;
    
    @Builder.Default
    private long maxDelayMs = 10000;
    
    @Builder.Default
    private double jitterFactor = 0.25;
}
```

---

## Part 5: Saga Pattern - Distributed Transactions

### Orchestration-Based Saga

```java
@Service
@Slf4j
public class OrderSagaOrchestrator {
    
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    private final ShippingService shippingService;
    private final NotificationService notificationService;
    
    /**
     * Execute order saga with compensation
     */
    public SagaResult executeOrderSaga(OrderRequest request) {
        String sagaId = UUID.randomUUID().toString();
        List<CompensationAction> compensations = new ArrayList<>();
        
        try {
            // Step 1: Reserve inventory
            ReservationResult reservation = inventoryService.reserve(
                request.getItems(), sagaId);
            
            compensations.add(() -> 
                inventoryService.cancelReservation(reservation.getReservationId()));
            
            // Step 2: Process payment
            PaymentResult payment = paymentService.charge(
                request.getPaymentDetails(), request.getAmount(), sagaId);
            
            compensations.add(() -> 
                paymentService.refund(payment.getTransactionId()));
            
            // Step 3: Create shipment
            ShipmentResult shipment = shippingService.createShipment(
                request.getShippingAddress(), reservation.getItems(), sagaId);
            
            compensations.add(() -> 
                shippingService.cancelShipment(shipment.getShipmentId()));
            
            // Step 4: Send confirmation
            notificationService.sendOrderConfirmation(
                request.getCustomerEmail(), sagaId);
            
            // Success - commit saga
            return SagaResult.success(sagaId, buildOrder(
                reservation, payment, shipment));
            
        } catch (Exception e) {
            log.error("Saga {} failed, starting compensation", sagaId, e);
            
            // Execute compensations in reverse order
            Collections.reverse(compensations);
            for (CompensationAction compensation : compensations) {
                try {
                    compensation.compensate();
                } catch (Exception ce) {
                    log.error("Compensation failed in saga {}", sagaId, ce);
                    // Continue with other compensations
                }
            }
            
            return SagaResult.failed(sagaId, e.getMessage());
        }
    }
    
    /**
     * Choreography-based saga using events
     */
    @Component
    public class EventDrivenSaga {
        
        @EventHandler
        public void handle(OrderCreatedEvent event) {
            try {
                inventoryService.reserve(event.getItems(), event.getSagaId());
                eventBus.publish(new InventoryReservedEvent(event.getSagaId()));
            } catch (Exception e) {
                eventBus.publish(new SagaFailedEvent(event.getSagaId(), e));
            }
        }
        
        @EventHandler
        public void handle(InventoryReservedEvent event) {
            try {
                paymentService.charge(event.getSagaId());
                eventBus.publish(new PaymentProcessedEvent(event.getSagaId()));
            } catch (Exception e) {
                eventBus.publish(new InventoryReleaseEvent(event.getSagaId()));
                eventBus.publish(new SagaFailedEvent(event.getSagaId(), e));
            }
        }
        
        @EventHandler
        public void handle(PaymentProcessedEvent event) {
            try {
                shippingService.ship(event.getSagaId());
                eventBus.publish(new OrderCompletedEvent(event.getSagaId()));
            } catch (Exception e) {
                eventBus.publish(new PaymentRefundEvent(event.getSagaId()));
                eventBus.publish(new InventoryReleaseEvent(event.getSagaId()));
                eventBus.publish(new SagaFailedEvent(event.getSagaId(), e));
            }
        }
    }
}
```

---

## Part 6: Caching Strategies - Performance Optimization

### Multi-Level Cache Implementation

```java
@Service
public class MultiLevelCacheService {
    
    private final LoadingCache<String, Object> l1Cache; // In-memory
    private final RedisTemplate<String, Object> l2Cache; // Redis
    private final DataSource dataSource; // Database
    
    public MultiLevelCacheService() {
        // L1 Cache configuration
        this.l1Cache = CacheBuilder.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(5, TimeUnit.MINUTES)
            .recordStats()
            .build(new CacheLoader<String, Object>() {
                @Override
                public Object load(String key) throws Exception {
                    return loadFromL2(key);
                }
            });
    }
    
    /**
     * Get with cache hierarchy
     */
    public <T> T get(String key, Class<T> type) {
        // Try L1 cache
        try {
            T value = type.cast(l1Cache.get(key));
            metrics.counter("cache.hit", "level", "L1").increment();
            return value;
        } catch (ExecutionException e) {
            // L1 miss, will load from L2/L3
        }
        
        // Try L2 cache
        T value = type.cast(l2Cache.opsForValue().get(key));
        if (value != null) {
            metrics.counter("cache.hit", "level", "L2").increment();
            // Populate L1
            l1Cache.put(key, value);
            return value;
        }
        
        // Load from database (L3)
        metrics.counter("cache.miss", "level", "L2").increment();
        value = loadFromDatabase(key, type);
        
        // Populate both caches
        if (value != null) {
            l2Cache.opsForValue().set(key, value, 1, TimeUnit.HOURS);
            l1Cache.put(key, value);
        }
        
        return value;
    }
    
    /**
     * Cache-aside pattern with stampede protection
     */
    public <T> T getWithStampedeProtection(String key, 
                                          Supplier<T> loader,
                                          Duration ttl) {
        String lockKey = "lock:" + key;
        
        // Try to get from cache
        T cached = (T) l2Cache.opsForValue().get(key);
        if (cached != null) {
            return cached;
        }
        
        // Try to acquire lock to prevent stampede
        Boolean lockAcquired = l2Cache.opsForValue()
            .setIfAbsent(lockKey, "locked", Duration.ofSeconds(30));
        
        if (Boolean.TRUE.equals(lockAcquired)) {
            try {
                // Double-check after acquiring lock
                cached = (T) l2Cache.opsForValue().get(key);
                if (cached != null) {
                    return cached;
                }
                
                // Load data
                T value = loader.get();
                
                // Store in cache
                l2Cache.opsForValue().set(key, value, ttl);
                
                return value;
                
            } finally {
                // Release lock
                l2Cache.delete(lockKey);
            }
        } else {
            // Another thread is loading, wait and retry
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            // Retry (with recursion limit in production)
            return getWithStampedeProtection(key, loader, ttl);
        }
    }
}
```

---

## Part 7: Production Monitoring and Observability

### Comprehensive Pattern Monitoring

```java
@Configuration
public class PatternMonitoringConfiguration {
    
    @Bean
    public MeterRegistry meterRegistry() {
        return new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
    }
    
    @Component
    public class PatternMetricsCollector {
        
        private final MeterRegistry registry;
        
        // Circuit Breaker Metrics
        @EventListener
        public void onCircuitBreakerStateChange(CircuitBreakerEvent event) {
            registry.counter("circuit_breaker_state_transitions",
                "from", event.getFromState(),
                "to", event.getToState(),
                "service", event.getServiceName()
            ).increment();
        }
        
        // Rate Limiter Metrics
        @EventListener
        public void onRateLimitExceeded(RateLimitEvent event) {
            registry.counter("rate_limit_exceeded",
                "client", event.getClientId(),
                "endpoint", event.getEndpoint()
            ).increment();
        }
        
        // Bulkhead Metrics
        @Scheduled(fixedDelay = 10000)
        public void collectBulkheadMetrics() {
            // Thread pool metrics
            ThreadPoolExecutor criticalPool = getCriticalPool();
            registry.gauge("bulkhead.thread_pool.active",
                criticalPool.getActiveCount(),
                "pool", "critical");
            registry.gauge("bulkhead.thread_pool.queued",
                criticalPool.getQueue().size(),
                "pool", "critical");
            
            // Connection pool metrics
            HikariDataSource dataSource = getPrimaryDataSource();
            registry.gauge("bulkhead.connection_pool.active",
                dataSource.getHikariPoolMXBean().getActiveConnections(),
                "pool", "primary");
            registry.gauge("bulkhead.connection_pool.idle",
                dataSource.getHikariPoolMXBean().getIdleConnections(),
                "pool", "primary");
        }
        
        // Retry Metrics
        @EventListener
        public void onRetryAttempt(RetryEvent event) {
            registry.counter("retry_attempts",
                "operation", event.getOperationName(),
                "attempt", String.valueOf(event.getAttemptNumber())
            ).increment();
            
            if (event.isSuccess()) {
                registry.timer("retry_success_after",
                    "operation", event.getOperationName()
                ).record(event.getTotalDuration());
            }
        }
    }
}
```

### Grafana Dashboard Queries

```yaml
# Circuit Breaker Dashboard
circuit_breaker_panels:
  - title: "Circuit Breaker State"
    query: |
      sum by (service, state) (
        increase(circuit_breaker_state_transitions[5m])
      )
  
  - title: "Request Success Rate"
    query: |
      sum(rate(circuit_breaker_execution_total{result="success"}[5m])) /
      sum(rate(circuit_breaker_execution_total[5m])) * 100
  
  - title: "Circuit Open Duration"
    query: |
      histogram_quantile(0.99,
        sum(rate(circuit_breaker_open_duration_bucket[5m])) by (le)
      )

# Rate Limiting Dashboard
rate_limiting_panels:
  - title: "Rate Limit Violations"
    query: |
      sum by (client) (
        increase(rate_limit_exceeded_total[5m])
      )
  
  - title: "API Usage by Client"
    query: |
      topk(10,
        sum by (client) (
          rate(api_requests_total[5m])
        )
      )

# Bulkhead Dashboard
bulkhead_panels:
  - title: "Thread Pool Saturation"
    query: |
      bulkhead_thread_pool_active / bulkhead_thread_pool_size * 100
  
  - title: "Connection Pool Usage"
    query: |
      bulkhead_connection_pool_active / bulkhead_connection_pool_max * 100
  
  - title: "Rejected Requests"
    query: |
      sum(rate(bulkhead_rejected_total[5m])) by (pool)
```

---

## Summary: Pattern Implementation Best Practices

### Pattern Selection Matrix

| Pattern | Use When | Don't Use When | Complexity |
|---------|----------|----------------|------------|
| Circuit Breaker | External service calls, Preventing cascades | Internal method calls, Infrequent operations | Medium |
| Rate Limiting | Public APIs, Resource protection | Internal services only, Unlimited resources | Low |
| Bulkhead | Resource isolation needed, Multi-tenant | Single operation type, Unlimited resources | Medium |
| Retry | Transient failures expected, Network calls | Non-idempotent operations, Permanent failures | Low |
| Saga | Distributed transactions, Compensatable operations | Simple transactions, Non-compensatable | High |
| Caching | Read-heavy workloads, Expensive computations | Write-heavy, Real-time data | Medium |

### Production Checklist

- [ ] **Circuit Breaker**: Configure thresholds, implement fallbacks, monitor state changes
- [ ] **Rate Limiting**: Set appropriate limits, implement client identification, add headers
- [ ] **Bulkhead**: Size pools correctly, monitor saturation, implement rejection policies
- [ ] **Retry**: Add jitter, set max attempts, identify retryable errors
- [ ] **Saga**: Design compensations, handle partial failures, monitor completion
- [ ] **Caching**: Set TTLs, implement invalidation, monitor hit rates

### Common Pitfalls

1. **Circuit Breaker**: Setting thresholds too low/high
2. **Rate Limiting**: Not considering burst traffic
3. **Bulkhead**: Undersizing pools causing starvation
4. **Retry**: Creating retry storms without jitter
5. **Saga**: Missing compensation logic
6. **Caching**: Cache stampedes on expiration

Remember: **Patterns are tools, not solutions. Combine them appropriately for your specific use case.**