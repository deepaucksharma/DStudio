/**
 * Circuit Breaker Pattern Implementation (Hystrix-style)
 * भारतीय infrastructure के लिए circuit breaker pattern
 * 
 * Indian Context: Mumbai power grid की load shedding pattern को software में apply करना
 * Real Example: Zomato/Swiggy delivery service के लिए payment gateway circuit breaker
 */

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;

public class CircuitBreakerHystrix {
    
    // Circuit breaker states - Mumbai electricity board की तरह
    public enum CircuitState {
        CLOSED,     // Normal operation - सब कुछ ठीक चल रहा
        OPEN,       // Circuit open - service को traffic नहीं भेज रहे (load shedding)
        HALF_OPEN   // Testing phase - slowly trying to restore (limited supply)
    }
    
    // Configuration for circuit breaker
    private final String serviceName;
    private final int failureThreshold;          // Kitne failures के बाद circuit open करें
    private final int successThreshold;          // Half-open में kitne success चाहिए
    private final Duration openTimeout;          // Circuit open kitne देर रखें
    private final Duration executionTimeout;     // Individual request timeout
    private final int slidingWindowSize;         // Rolling window size for failure calculation
    
    // State tracking
    private volatile CircuitState state = CircuitState.CLOSED;
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    private final AtomicInteger consecutiveSuccesses = new AtomicInteger(0);
    
    // Metrics collection - Mumbai BEST bus की तरह real-time monitoring
    private final Queue<RequestResult> requestHistory = new ConcurrentLinkedQueue<>();
    private final AtomicInteger totalRequests = new AtomicInteger(0);
    private final AtomicInteger totalFailures = new AtomicInteger(0);
    private final AtomicInteger circuitOpenCount = new AtomicInteger(0);
    
    // Executor for timeout management
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    
    public CircuitBreakerHystrix(String serviceName,
                               int failureThreshold,
                               int successThreshold, 
                               Duration openTimeout,
                               Duration executionTimeout,
                               int slidingWindowSize) {
        this.serviceName = serviceName;
        this.failureThreshold = failureThreshold;
        this.successThreshold = successThreshold;
        this.openTimeout = openTimeout;
        this.executionTimeout = executionTimeout;
        this.slidingWindowSize = slidingWindowSize;
        
        System.out.println("🔌 Circuit Breaker initialized for: " + serviceName);
        System.out.println("   Failure Threshold: " + failureThreshold + " failures");
        System.out.println("   Open Timeout: " + openTimeout.getSeconds() + " seconds");
        System.out.println("   Execution Timeout: " + executionTimeout.toMillis() + "ms");
    }
    
    /**
     * Execute request with circuit breaker protection
     * Mumbai power grid की तरह - overload होने पर automatically cut कर देता है
     */
    public <T> CircuitBreakerResult<T> execute(Supplier<T> operation) {
        totalRequests.incrementAndGet();
        LocalDateTime startTime = LocalDateTime.now();
        
        // Check current circuit state
        CircuitState currentState = getCurrentState();
        
        // If circuit is OPEN, immediately fail (load shedding mode)
        if (currentState == CircuitState.OPEN) {
            System.out.println("⚡ Circuit OPEN - Request rejected (load shedding mode)");
            recordFailure(startTime);
            
            return new CircuitBreakerResult<>(
                false, null, "Circuit breaker OPEN - service unavailable",
                currentState, Duration.between(startTime, LocalDateTime.now())
            );
        }
        
        try {
            // Execute with timeout protection
            Future<T> future = executorService.submit(() -> operation.get());
            T result = future.get(executionTimeout.toMillis(), TimeUnit.MILLISECONDS);
            
            // Success case
            recordSuccess(startTime);
            
            // If we were in HALF_OPEN, check if we can close circuit
            if (currentState == CircuitState.HALF_OPEN) {
                int successes = consecutiveSuccesses.incrementAndGet();
                if (successes >= successThreshold) {
                    closeCircuit();
                }
            }
            
            return new CircuitBreakerResult<>(
                true, result, null, getCurrentState(),
                Duration.between(startTime, LocalDateTime.now())
            );
            
        } catch (TimeoutException e) {
            System.out.println("⏰ Request timeout - " + executionTimeout.toMillis() + "ms exceeded");
            recordFailure(startTime);
            
            return new CircuitBreakerResult<>(
                false, null, "Request timeout: " + executionTimeout.toMillis() + "ms",
                getCurrentState(), Duration.between(startTime, LocalDateTime.now())
            );
            
        } catch (Exception e) {
            System.out.println("❌ Request failed: " + e.getMessage());
            recordFailure(startTime);
            
            return new CircuitBreakerResult<>(
                false, null, "Request failed: " + e.getMessage(),
                getCurrentState(), Duration.between(startTime, LocalDateTime.now())
            );
        }
    }
    
    /**
     * Get current circuit state with automatic state transitions
     */
    private CircuitState getCurrentState() {
        if (state == CircuitState.OPEN) {
            // Check if we should transition to HALF_OPEN
            long timeSinceLastFailure = System.currentTimeMillis() - lastFailureTime.get();
            if (timeSinceLastFailure >= openTimeout.toMillis()) {
                state = CircuitState.HALF_OPEN;
                consecutiveSuccesses.set(0);
                System.out.println("🔄 Circuit transitioning to HALF_OPEN (testing mode)");
            }
        }
        
        return state;
    }
    
    /**
     * Record successful request
     */
    private void recordSuccess(LocalDateTime timestamp) {
        RequestResult result = new RequestResult(timestamp, true, null);
        addToHistory(result);
        
        System.out.println("✅ Request successful at " + 
                         timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss")));
    }
    
    /**
     * Record failed request and check if circuit should open
     */
    private void recordFailure(LocalDateTime timestamp) {
        RequestResult result = new RequestResult(timestamp, false, "Service failure");
        addToHistory(result);
        
        totalFailures.incrementAndGet();
        lastFailureTime.set(System.currentTimeMillis());
        consecutiveSuccesses.set(0);  // Reset success counter
        
        // Check if we should open the circuit
        if (state == CircuitState.CLOSED || state == CircuitState.HALF_OPEN) {
            double failureRate = calculateFailureRate();
            
            System.out.println("❌ Request failed at " + 
                             timestamp.format(DateTimeFormatter.ofPattern("HH:mm:ss")) +
                             " (Failure rate: " + String.format("%.1f%%", failureRate * 100) + ")");
            
            if (failureRate >= (double) failureThreshold / 100.0) {
                openCircuit();
            }
        }
    }
    
    /**
     * Calculate failure rate over sliding window
     */
    private double calculateFailureRate() {
        cleanupOldRequests();
        
        if (requestHistory.size() < 5) {
            return 0.0; // Not enough data
        }
        
        long failures = requestHistory.stream()
                .mapToLong(r -> r.success ? 0 : 1)
                .sum();
        
        return (double) failures / requestHistory.size();
    }
    
    /**
     * Open circuit breaker (load shedding mode)
     */
    private void openCircuit() {
        state = CircuitState.OPEN;
        circuitOpenCount.incrementAndGet();
        
        System.out.println("⚡ CIRCUIT OPENED - Load shedding mode activated");
        System.out.println("   Service: " + serviceName);
        System.out.println("   Reason: Failure rate exceeded threshold");
        System.out.println("   Will retry after: " + openTimeout.getSeconds() + " seconds");
    }
    
    /**
     * Close circuit breaker (normal operation restored)
     */
    private void closeCircuit() {
        state = CircuitState.CLOSED;
        consecutiveSuccesses.set(0);
        
        System.out.println("🔋 CIRCUIT CLOSED - Normal operation restored");
        System.out.println("   Service: " + serviceName + " is healthy again");
    }
    
    /**
     * Add request result to sliding window history
     */
    private void addToHistory(RequestResult result) {
        requestHistory.offer(result);
        
        // Maintain sliding window size
        while (requestHistory.size() > slidingWindowSize) {
            requestHistory.poll();
        }
    }
    
    /**
     * Clean up requests older than sliding window
     */
    private void cleanupOldRequests() {
        LocalDateTime cutoffTime = LocalDateTime.now().minus(Duration.ofMinutes(5));
        
        requestHistory.removeIf(request -> request.timestamp.isBefore(cutoffTime));
    }
    
    /**
     * Get comprehensive metrics for monitoring
     */
    public CircuitBreakerMetrics getMetrics() {
        cleanupOldRequests();
        
        long successCount = requestHistory.stream()
                .mapToLong(r -> r.success ? 1 : 0)
                .sum();
        
        double failureRate = requestHistory.isEmpty() ? 0.0 : 
                           (double) (requestHistory.size() - successCount) / requestHistory.size();
        
        return new CircuitBreakerMetrics(
            serviceName,
            state,
            totalRequests.get(),
            totalFailures.get(),
            circuitOpenCount.get(),
            failureRate,
            requestHistory.size(),
            successCount
        );
    }
    
    // Data classes
    static class RequestResult {
        final LocalDateTime timestamp;
        final boolean success;
        final String errorMessage;
        
        RequestResult(LocalDateTime timestamp, boolean success, String errorMessage) {
            this.timestamp = timestamp;
            this.success = success;
            this.errorMessage = errorMessage;
        }
    }
    
    public static class CircuitBreakerResult<T> {
        public final boolean success;
        public final T result;
        public final String errorMessage;
        public final CircuitState circuitState;
        public final Duration executionTime;
        
        CircuitBreakerResult(boolean success, T result, String errorMessage,
                           CircuitState circuitState, Duration executionTime) {
            this.success = success;
            this.result = result;
            this.errorMessage = errorMessage;
            this.circuitState = circuitState;
            this.executionTime = executionTime;
        }
    }
    
    public static class CircuitBreakerMetrics {
        public final String serviceName;
        public final CircuitState currentState;
        public final int totalRequests;
        public final int totalFailures;
        public final int circuitOpenCount;
        public final double currentFailureRate;
        public final int slidingWindowRequests;
        public final long slidingWindowSuccesses;
        
        CircuitBreakerMetrics(String serviceName, CircuitState currentState,
                            int totalRequests, int totalFailures, int circuitOpenCount,
                            double currentFailureRate, int slidingWindowRequests,
                            long slidingWindowSuccesses) {
            this.serviceName = serviceName;
            this.currentState = currentState;
            this.totalRequests = totalRequests;
            this.totalFailures = totalFailures;
            this.circuitOpenCount = circuitOpenCount;
            this.currentFailureRate = currentFailureRate;
            this.slidingWindowRequests = slidingWindowRequests;
            this.slidingWindowSuccesses = slidingWindowSuccesses;
        }
        
        public void printMetrics() {
            System.out.println("\n📊 Circuit Breaker Metrics for " + serviceName + ":");
            System.out.println("   Current State: " + currentState);
            System.out.println("   Total Requests: " + totalRequests);
            System.out.println("   Total Failures: " + totalFailures);
            System.out.println("   Circuit Opened: " + circuitOpenCount + " times");
            System.out.println("   Current Failure Rate: " + 
                             String.format("%.1f%%", currentFailureRate * 100));
            System.out.println("   Sliding Window: " + slidingWindowSuccesses + 
                             "/" + slidingWindowRequests + " successes");
        }
    }
    
    // Simulation classes for Indian services
    
    /**
     * Zomato Payment Gateway Simulator
     * Real payment gateway patterns को simulate करता है
     */
    static class ZomatoPaymentGateway {
        private int callCount = 0;
        private final Random random = new Random();
        
        public String processPayment(double amount, String orderId) throws Exception {
            callCount++;
            
            // Simulate network latency
            try {
                Thread.sleep(random.nextInt(1000) + 500); // 500-1500ms
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
            
            // Simulate failures based on realistic patterns
            double failureRate = calculateFailureRate();
            
            if (random.nextDouble() < failureRate) {
                String[] errors = {
                    "Payment gateway timeout",
                    "Bank server unavailable", 
                    "Insufficient balance",
                    "Network connectivity error",
                    "Card declined by bank"
                };
                throw new Exception(errors[random.nextInt(errors.length)]);
            }
            
            return "PAYMENT_SUCCESS_" + orderId + "_" + callCount;
        }
        
        private double calculateFailureRate() {
            // Realistic failure patterns for Indian payment gateways
            if (callCount <= 3) return 0.8;      // High initial failures
            if (callCount <= 10) return 0.4;     // Moderate failures  
            if (callCount <= 20) return 0.2;     // Lower failures
            return 0.05;                         // Stable after warmup
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🇮🇳 Circuit Breaker Pattern - Indian Service Example");
        System.out.println("🍕 Zomato Payment Gateway Protection Demo");
        System.out.println("=" + "=".repeat(60));
        
        // Create circuit breaker for Zomato payment service
        CircuitBreakerHystrix paymentCircuitBreaker = new CircuitBreakerHystrix(
            "ZomatoPaymentGateway",
            50,                              // 50% failure threshold
            3,                               // 3 consecutive successes to close
            Duration.ofSeconds(10),          // 10 seconds open timeout
            Duration.ofMillis(2000),         // 2 second request timeout
            20                               // 20 request sliding window
        );
        
        ZomatoPaymentGateway paymentGateway = new ZomatoPaymentGateway();
        
        // Simulate order processing during peak hours
        System.out.println("\n🍕 Simulating Zomato orders during dinner rush...");
        
        for (int orderNum = 1; orderNum <= 30; orderNum++) {
            String orderId = "ZOMATO_ORDER_" + orderNum;
            double amount = 250 + (orderNum * 50); // Increasing order amounts
            
            System.out.println("\n📱 Processing Order #" + orderNum + 
                             " (₹" + amount + ") - " + orderId);
            
            CircuitBreakerResult<String> result = paymentCircuitBreaker.execute(
                () -> paymentGateway.processPayment(amount, orderId)
            );
            
            if (result.success) {
                System.out.println("✅ Payment successful: " + result.result);
                System.out.println("   Execution time: " + result.executionTime.toMillis() + "ms");
            } else {
                System.out.println("❌ Payment failed: " + result.errorMessage);
                System.out.println("   Circuit state: " + result.circuitState);
            }
            
            // Display metrics every 5 orders
            if (orderNum % 5 == 0) {
                paymentCircuitBreaker.getMetrics().printMetrics();
            }
            
            // Small delay between orders (realistic flow)
            Thread.sleep(1000);
        }
        
        // Final metrics
        System.out.println("\n" + "=".repeat(60));
        System.out.println("📊 Final Circuit Breaker Analysis");
        paymentCircuitBreaker.getMetrics().printMetrics();
        
        // Business impact analysis
        System.out.println("\n💼 Business Impact Analysis:");
        CircuitBreakerMetrics metrics = paymentCircuitBreaker.getMetrics();
        
        double successRate = (double) metrics.slidingWindowSuccesses / 
                           metrics.slidingWindowRequests * 100;
        double avgOrderValue = 400.0; // ₹400 average order
        double protectedRevenue = metrics.slidingWindowSuccesses * avgOrderValue;
        
        System.out.println("   Success Rate: " + String.format("%.1f%%", successRate));
        System.out.println("   Protected Revenue: ₹" + String.format("%.0f", protectedRevenue));
        System.out.println("   Avoided Cascade Failures: " + 
                         (metrics.totalRequests - metrics.slidingWindowRequests));
        
        // Mumbai analogy explanation
        System.out.println("\n🏙️ Mumbai Power Grid Analogy:");
        System.out.println("   Circuit Breaker = Electrical load shedding during peak demand");
        System.out.println("   CLOSED state = Normal power supply (सब कुछ ठीक)");
        System.out.println("   OPEN state = Load shedding active (power cut to prevent grid failure)");
        System.out.println("   HALF_OPEN = Testing limited supply (slowly restoring power)");
        System.out.println("   Failure threshold = Maximum load before tripping circuit");
        
        // Technical recommendations  
        System.out.println("\n🔧 Circuit Breaker Best Practices:");
        System.out.println("   1. Set failure threshold based on SLA requirements (usually 50-80%)");
        System.out.println("   2. Use sliding window for accurate failure rate calculation");
        System.out.println("   3. Implement exponential backoff with jitter");
        System.out.println("   4. Monitor metrics and adjust thresholds based on traffic patterns");
        System.out.println("   5. Provide fallback mechanisms for better user experience");
        
        // Shutdown executor
        paymentCircuitBreaker.executorService.shutdown();
    }
}