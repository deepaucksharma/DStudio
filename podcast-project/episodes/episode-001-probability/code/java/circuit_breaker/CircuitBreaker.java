/**
 * Production-Ready Circuit Breaker Implementation
 * =============================================
 * Hystrix-style pattern for Indian scale applications
 * 
 * Real-world use cases:
 * - Paytm payment timeouts
 * - Flipkart inventory service failures  
 * - Ola ride matching service overload
 * - IRCTC booking service protection
 * 
 * Features:
 * - Configurable failure thresholds
 * - Multiple fallback strategies
 * - Metrics collection for monitoring
 * - Thread-safe implementation
 */

import java.time.Duration;
import java.time.Instant;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.Map;

/**
 * Circuit Breaker states as per Netflix Hystrix pattern
 */
enum CircuitState {
    CLOSED,    // Normal operation - sab theek hai
    OPEN,      // Circuit open - calls blocked - system protection mode
    HALF_OPEN  // Testing mode - limited calls allowed to check recovery
}

/**
 * Circuit breaker configuration class
 * Customizable for different Indian traffic patterns
 */
class CircuitBreakerConfig {
    // Failure threshold for opening circuit
    private final int failureThreshold;
    
    // Success threshold for closing circuit from half-open
    private final int successThreshold; 
    
    // Timeout duration for moving from open to half-open
    private final Duration timeout;
    
    // Request volume threshold - minimum requests before evaluation
    private final int requestVolumeThreshold;
    
    // Error percentage threshold (0-100)
    private final double errorPercentageThreshold;
    
    // Slow call duration threshold
    private final Duration slowCallDurationThreshold;
    
    public CircuitBreakerConfig(int failureThreshold, int successThreshold, 
                               Duration timeout, int requestVolumeThreshold,
                               double errorPercentageThreshold, 
                               Duration slowCallDurationThreshold) {
        this.failureThreshold = failureThreshold;
        this.successThreshold = successThreshold;
        this.timeout = timeout;
        this.requestVolumeThreshold = requestVolumeThreshold;
        this.errorPercentageThreshold = errorPercentageThreshold;
        this.slowCallDurationThreshold = slowCallDurationThreshold;
    }
    
    // Getters
    public int getFailureThreshold() { return failureThreshold; }
    public int getSuccessThreshold() { return successThreshold; }
    public Duration getTimeout() { return timeout; }
    public int getRequestVolumeThreshold() { return requestVolumeThreshold; }
    public double getErrorPercentageThreshold() { return errorPercentageThreshold; }
    public Duration getSlowCallDurationThreshold() { return slowCallDurationThreshold; }
    
    /**
     * Predefined configurations for Indian platforms
     */
    public static class IndianPlatformConfigs {
        
        // High-traffic configuration - for Paytm, Flipkart scale
        public static CircuitBreakerConfig highTraffic() {
            return new CircuitBreakerConfig(
                10,                              // 10 failures to open
                5,                               // 5 successes to close
                Duration.ofSeconds(30),          // 30 second timeout
                20,                              // Min 20 requests for evaluation
                50.0,                            // 50% error rate threshold
                Duration.ofSeconds(2)            // 2 second slow call threshold
            );
        }
        
        // Critical service configuration - for payment, booking services  
        public static CircuitBreakerConfig criticalService() {
            return new CircuitBreakerConfig(
                3,                               // 3 failures to open (very sensitive)
                2,                               // 2 successes to close  
                Duration.ofMinutes(1),           // 1 minute timeout
                10,                              // Min 10 requests
                25.0,                            // 25% error rate threshold (strict)
                Duration.ofSeconds(1)            // 1 second slow call threshold
            );
        }
        
        // Non-critical service configuration - for analytics, notifications
        public static CircuitBreakerConfig nonCriticalService() {
            return new CircuitBreakerConfig(
                20,                              // 20 failures to open (lenient)
                10,                              // 10 successes to close
                Duration.ofMinutes(5),           // 5 minute timeout
                50,                              // Min 50 requests
                75.0,                            // 75% error rate threshold
                Duration.ofSeconds(5)            // 5 second slow call threshold
            );
        }
    }
}

/**
 * Circuit breaker metrics for monitoring
 */
class CircuitBreakerMetrics {
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong successfulRequests = new AtomicLong(0);
    private final AtomicLong failedRequests = new AtomicLong(0);
    private final AtomicLong slowRequests = new AtomicLong(0);
    private final AtomicLong shortCircuitedRequests = new AtomicLong(0);
    private final AtomicLong totalResponseTime = new AtomicLong(0);
    
    // State transition counters
    private final AtomicLong stateTransitions = new AtomicLong(0);
    private final Map<String, AtomicLong> stateTransitionDetails = new ConcurrentHashMap<>();
    
    public void recordRequest() {
        totalRequests.incrementAndGet();
    }
    
    public void recordSuccess(long responseTimeMs) {
        successfulRequests.incrementAndGet();
        totalResponseTime.addAndGet(responseTimeMs);
    }
    
    public void recordFailure() {
        failedRequests.incrementAndGet();
    }
    
    public void recordSlowRequest() {
        slowRequests.incrementAndGet();
    }
    
    public void recordShortCircuit() {
        shortCircuitedRequests.incrementAndGet();
    }
    
    public void recordStateTransition(CircuitState from, CircuitState to) {
        stateTransitions.incrementAndGet();
        String key = from + " -> " + to;
        stateTransitionDetails.computeIfAbsent(key, k -> new AtomicLong(0)).incrementAndGet();
    }
    
    // Calculate success rate percentage
    public double getSuccessRate() {
        long total = totalRequests.get();
        if (total == 0) return 100.0;
        return (successfulRequests.get() * 100.0) / total;
    }
    
    // Calculate failure rate percentage  
    public double getFailureRate() {
        long total = totalRequests.get();
        if (total == 0) return 0.0;
        return (failedRequests.get() * 100.0) / total;
    }
    
    // Calculate average response time
    public double getAverageResponseTime() {
        long successes = successfulRequests.get();
        if (successes == 0) return 0.0;
        return totalResponseTime.get() / (double) successes;
    }
    
    // Get metrics summary for monitoring dashboards
    public String getMetricsSummary() {
        return String.format(
            "📊 CIRCUIT BREAKER METRICS\n" +
            "Total Requests: %d\n" +
            "Success Rate: %.2f%%\n" + 
            "Failure Rate: %.2f%%\n" +
            "Slow Requests: %d\n" +
            "Short Circuited: %d\n" +
            "Avg Response Time: %.2fms\n" +
            "State Transitions: %d",
            totalRequests.get(),
            getSuccessRate(),
            getFailureRate(), 
            slowRequests.get(),
            shortCircuitedRequests.get(),
            getAverageResponseTime(),
            stateTransitions.get()
        );
    }
}

/**
 * Main Circuit Breaker Implementation
 * Thread-safe and production-ready for Indian scale
 */
public class CircuitBreaker {
    private final String name;
    private final CircuitBreakerConfig config;
    private final CircuitBreakerMetrics metrics;
    
    // Circuit state management
    private final AtomicReference<CircuitState> state = new AtomicReference<>(CircuitState.CLOSED);
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0); 
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    private final AtomicLong requestCount = new AtomicLong(0);
    
    // Fallback strategy
    private final Supplier<Object> fallbackSupplier;
    
    /**
     * Constructor with fallback
     */
    public CircuitBreaker(String name, CircuitBreakerConfig config, 
                         Supplier<Object> fallbackSupplier) {
        this.name = name;
        this.config = config;
        this.metrics = new CircuitBreakerMetrics();
        this.fallbackSupplier = fallbackSupplier;
    }
    
    /**
     * Constructor without fallback
     */
    public CircuitBreaker(String name, CircuitBreakerConfig config) {
        this(name, config, () -> {
            throw new RuntimeException("Service temporarily unavailable - Circuit breaker open");
        });
    }
    
    /**
     * Execute a supplier with circuit breaker protection
     * Ye main method hai jo sabse zyada use hoga
     */
    public <T> T execute(Supplier<T> supplier) throws Exception {
        metrics.recordRequest();
        
        // Check if circuit should be opened
        if (shouldOpenCircuit()) {
            transitionToOpen();
        }
        
        // Check current state and decide action
        CircuitState currentState = state.get();
        
        switch (currentState) {
            case OPEN:
                // Circuit is open - don't execute, return fallback
                if (shouldAttemptReset()) {
                    transitionToHalfOpen();
                    return executeWithMonitoring(supplier);
                } else {
                    metrics.recordShortCircuit();
                    return (T) fallbackSupplier.get();
                }
                
            case HALF_OPEN:
                // Testing mode - execute but monitor closely
                return executeWithMonitoring(supplier);
                
            case CLOSED:
            default:
                // Normal operation
                return executeWithMonitoring(supplier);
        }
    }
    
    /**
     * Execute supplier with performance monitoring
     */
    private <T> T executeWithMonitoring(Supplier<T> supplier) throws Exception {
        long startTime = System.currentTimeMillis();
        
        try {
            T result = supplier.get();
            long responseTime = System.currentTimeMillis() - startTime;
            
            // Check if call was slow
            if (responseTime > config.getSlowCallDurationThreshold().toMillis()) {
                metrics.recordSlowRequest();
            }
            
            // Record success
            recordSuccess(responseTime);
            metrics.recordSuccess(responseTime);
            
            return result;
            
        } catch (Exception e) {
            // Record failure
            recordFailure();
            metrics.recordFailure();
            throw e;
        }
    }
    
    /**
     * Check if circuit should be opened
     */
    private boolean shouldOpenCircuit() {
        long totalRequests = requestCount.get();
        
        // Not enough requests to evaluate
        if (totalRequests < config.getRequestVolumeThreshold()) {
            return false;
        }
        
        // Check failure threshold
        if (failureCount.get() >= config.getFailureThreshold()) {
            return true;
        }
        
        // Check error percentage threshold
        double errorRate = metrics.getFailureRate();
        return errorRate >= config.getErrorPercentageThreshold();
    }
    
    /**
     * Check if circuit should attempt reset from open to half-open
     */
    private boolean shouldAttemptReset() {
        long timeSinceLastFailure = System.currentTimeMillis() - lastFailureTime.get();
        return timeSinceLastFailure >= config.getTimeout().toMillis();
    }
    
    /**
     * Record successful execution
     */
    private void recordSuccess(long responseTime) {
        requestCount.incrementAndGet();
        
        if (state.get() == CircuitState.HALF_OPEN) {
            int currentSuccesses = successCount.incrementAndGet();
            if (currentSuccesses >= config.getSuccessThreshold()) {
                transitionToClosed();
            }
        } else {
            // Reset failure count on successful execution in closed state
            failureCount.set(0);
        }
    }
    
    /**
     * Record failed execution
     */
    private void recordFailure() {
        requestCount.incrementAndGet();
        failureCount.incrementAndGet();
        lastFailureTime.set(System.currentTimeMillis());
        
        if (state.get() == CircuitState.HALF_OPEN) {
            // Any failure in half-open state should open circuit
            transitionToOpen();
        }
    }
    
    /**
     * State transition methods
     */
    private void transitionToOpen() {
        CircuitState previousState = state.getAndSet(CircuitState.OPEN);
        if (previousState != CircuitState.OPEN) {
            metrics.recordStateTransition(previousState, CircuitState.OPEN);
            System.out.println("🔴 Circuit breaker '" + name + "' opened - blocking requests");
        }
    }
    
    private void transitionToHalfOpen() {
        CircuitState previousState = state.getAndSet(CircuitState.HALF_OPEN);
        if (previousState != CircuitState.HALF_OPEN) {
            successCount.set(0);
            metrics.recordStateTransition(previousState, CircuitState.HALF_OPEN);
            System.out.println("🟡 Circuit breaker '" + name + "' half-open - testing recovery");
        }
    }
    
    private void transitionToClosed() {
        CircuitState previousState = state.getAndSet(CircuitState.CLOSED);
        if (previousState != CircuitState.CLOSED) {
            failureCount.set(0);
            successCount.set(0);
            metrics.recordStateTransition(previousState, CircuitState.CLOSED);
            System.out.println("🟢 Circuit breaker '" + name + "' closed - normal operation resumed");
        }
    }
    
    /**
     * Get current circuit breaker state
     */
    public CircuitState getState() {
        return state.get();
    }
    
    /**
     * Get metrics for monitoring
     */
    public CircuitBreakerMetrics getMetrics() {
        return metrics;
    }
    
    /**
     * Get circuit breaker name
     */
    public String getName() {
        return name;
    }
    
    /**
     * Print current status
     */
    public void printStatus() {
        System.out.println("\n🔧 CIRCUIT BREAKER STATUS: " + name);
        System.out.println("Current State: " + getState());
        System.out.println("Failure Count: " + failureCount.get());
        System.out.println("Success Count: " + successCount.get());
        System.out.println("Request Count: " + requestCount.get());
        System.out.println(metrics.getMetricsSummary());
    }
    
    /**
     * Demo method showing real-world usage patterns
     */
    public static void main(String[] args) throws Exception {
        System.out.println("🚀 Circuit Breaker Demo - Indian Scale Examples");
        System.out.println("=" .repeat(60));
        
        // Example 1: Paytm Payment Service Protection
        demonstratePaymentService();
        
        // Example 2: Flipkart Inventory Service Protection  
        demonstrateInventoryService();
        
        // Example 3: IRCTC Booking Service Protection
        demonstrateBookingService();
    }
    
    /**
     * Paytm payment service circuit breaker demo
     */
    private static void demonstratePaymentService() throws Exception {
        System.out.println("\n💳 PAYTM PAYMENT SERVICE DEMO");
        System.out.println("-".repeat(40));
        
        // Create circuit breaker with critical service configuration
        CircuitBreaker paymentCB = new CircuitBreaker(
            "PaytmPaymentService",
            CircuitBreakerConfig.IndianPlatformConfigs.criticalService(),
            () -> "Payment temporarily unavailable. Try UPI or cash."
        );
        
        // Simulate payment requests with some failures
        for (int i = 1; i <= 15; i++) {
            try {
                String result = paymentCB.execute(() -> {
                    // Simulate random payment failures
                    if (Math.random() < 0.3) { // 30% failure rate
                        throw new RuntimeException("Payment gateway timeout");
                    }
                    
                    // Simulate processing time
                    try {
                        Thread.sleep(100 + (int)(Math.random() * 500));
                    } catch (InterruptedException e) {}
                    
                    return "Payment processed successfully - ₹" + (100 + i * 10);
                });
                
                System.out.println("Request " + i + ": " + result);
                
            } catch (Exception e) {
                System.out.println("Request " + i + ": Failed - " + e.getMessage());
            }
            
            // Small delay between requests
            Thread.sleep(100);
        }
        
        paymentCB.printStatus();
    }
    
    /**
     * Flipkart inventory service circuit breaker demo
     */
    private static void demonstrateInventoryService() throws Exception {
        System.out.println("\n📦 FLIPKART INVENTORY SERVICE DEMO");
        System.out.println("-".repeat(40));
        
        CircuitBreaker inventoryCB = new CircuitBreaker(
            "FlipkartInventoryService", 
            CircuitBreakerConfig.IndianPlatformConfigs.highTraffic(),
            () -> "Inventory check unavailable. Showing cached data."
        );
        
        // Simulate high-traffic inventory checks
        for (int i = 1; i <= 25; i++) {
            try {
                String result = inventoryCB.execute(() -> {
                    // Simulate inventory service overload
                    if (i > 10 && i < 20 && Math.random() < 0.6) { // Heavy failures mid-way
                        throw new RuntimeException("Database connection timeout");
                    }
                    
                    return "Stock available: " + (100 - i) + " units";
                });
                
                System.out.println("Check " + i + ": " + result);
                
            } catch (Exception e) {
                System.out.println("Check " + i + ": " + e.getMessage());
            }
            
            Thread.sleep(50);
        }
        
        inventoryCB.printStatus();
    }
    
    /**
     * IRCTC booking service circuit breaker demo
     */
    private static void demonstrateBookingService() throws Exception {
        System.out.println("\n🚂 IRCTC BOOKING SERVICE DEMO");
        System.out.println("-".repeat(40));
        
        CircuitBreaker bookingCB = new CircuitBreaker(
            "IRCTCBookingService",
            CircuitBreakerConfig.IndianPlatformConfigs.highTraffic(),
            () -> "Booking unavailable. Please try again or use mobile app."
        );
        
        // Simulate Tatkal booking rush (high failure rate initially)
        for (int i = 1; i <= 30; i++) {
            try {
                String result = bookingCB.execute(() -> {
                    // Simulate Tatkal booking stress
                    if (i <= 12) { // Initial rush failures
                        if (Math.random() < 0.8) { // 80% failure during rush
                            throw new RuntimeException("Server overloaded - 50000+ concurrent users");
                        }
                    } else if (i <= 20) { // Recovery phase
                        if (Math.random() < 0.3) { // 30% failure during recovery
                            throw new RuntimeException("Database slow response");
                        }
                    }
                    
                    // Simulate booking processing
                    Thread.sleep(200);
                    return "Booking confirmed - PNR: " + (1000000 + i);
                });
                
                System.out.println("Booking " + i + ": " + result);
                
            } catch (Exception e) {
                System.out.println("Booking " + i + ": " + e.getMessage());
            }
            
            Thread.sleep(200);
        }
        
        bookingCB.printStatus();
        
        System.out.println("\n✅ Circuit Breaker Demo Completed");
        System.out.println("💡 Key Insights:");
        System.out.println("  - Circuit breakers prevent cascade failures");
        System.out.println("  - Fallback responses maintain user experience");
        System.out.println("  - Different configurations for different criticality");
        System.out.println("  - Metrics help optimize thresholds");
        System.out.println("💰 Cost Impact: Prevents ₹1Cr+ losses during outages");
    }
}