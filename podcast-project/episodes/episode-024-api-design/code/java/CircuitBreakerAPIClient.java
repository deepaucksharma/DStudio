/**
 * Circuit Breaker Pattern for API Resilience
 * Indian e-commerce के लिए resilient API client implementation
 * 
 * Key Features:
 * - Automatic failure detection
 * - Configurable thresholds
 * - Fallback mechanisms
 * - Health check capabilities
 * - Mumbai local train जैसा backup system
 * 
 * Author: Code Developer Agent for Hindi Tech Podcast
 * Episode: 24 - API Design Patterns
 */

package com.flipkart.api.resilience;

import java.time.LocalDateTime;
import java.time.Duration;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Circuit Breaker implementation for API resilience
 * API calls के लिए circuit breaker pattern
 */
public class CircuitBreakerAPIClient {
    
    private static final Logger logger = Logger.getLogger(CircuitBreakerAPIClient.class.getName());
    
    // Circuit breaker states - Mumbai local train service जैसा
    public enum State {
        CLOSED,     // Normal operation - train chal rahi hai
        OPEN,       // Failing fast - train service disrupted  
        HALF_OPEN   // Testing recovery - limited service
    }
    
    private volatile State state = State.CLOSED;
    private final AtomicInteger failureCount = new AtomicInteger(0);
    private final AtomicInteger successCount = new AtomicInteger(0);
    private final AtomicLong lastFailureTime = new AtomicLong(0);
    
    // Configuration - production ready values
    private final int failureThreshold;          // Max failures before opening
    private final long timeoutInMillis;          // Request timeout
    private final long retryTimeoutInMillis;     // Time before retry
    private final int maxRetryAttempts;          // Max retry attempts
    private final ExecutorService executor;
    
    /**
     * Constructor with Indian e-commerce optimized defaults
     */
    public CircuitBreakerAPIClient() {
        this(5, 3000, 60000, 3); // Conservative values for Indian networks
    }
    
    public CircuitBreakerAPIClient(int failureThreshold, long timeoutInMillis, 
                                 long retryTimeoutInMillis, int maxRetryAttempts) {
        this.failureThreshold = failureThreshold;
        this.timeoutInMillis = timeoutInMillis;
        this.retryTimeoutInMillis = retryTimeoutInMillis;
        this.maxRetryAttempts = maxRetryAttempts;
        this.executor = Executors.newFixedThreadPool(10);
        
        logger.info("🔧 Circuit Breaker initialized - Failure threshold: " + failureThreshold);
    }
    
    /**
     * Execute API call with circuit breaker protection
     * API call को safely execute करते हैं
     */
    public <T> CompletableFuture<T> execute(Supplier<T> operation, Supplier<T> fallback) {
        return CompletableFuture.supplyAsync(() -> {
            // Check circuit breaker state
            if (state == State.OPEN) {
                if (shouldRetry()) {
                    logger.info("🔄 Circuit breaker moving to HALF_OPEN state");
                    state = State.HALF_OPEN;
                } else {
                    logger.warning("⚡ Circuit breaker OPEN - Using fallback");
                    return fallback.get();
                }
            }
            
            try {
                long startTime = System.currentTimeMillis();
                T result = executeWithTimeout(operation);
                long executionTime = System.currentTimeMillis() - startTime;
                
                onSuccess(executionTime);
                return result;
                
            } catch (Exception e) {
                onFailure(e);
                logger.log(Level.WARNING, "🚨 API call failed: " + e.getMessage(), e);
                return fallback.get();
            }
        }, executor);
    }
    
    /**
     * Execute operation with timeout
     * Timeout के साथ operation execute करते हैं
     */
    private <T> T executeWithTimeout(Supplier<T> operation) {
        CompletableFuture<T> future = CompletableFuture.supplyAsync(operation, executor);
        
        try {
            return future.get(timeoutInMillis, java.util.concurrent.TimeUnit.MILLISECONDS);
        } catch (java.util.concurrent.TimeoutException e) {
            future.cancel(true);
            throw new RuntimeException("API call timeout after " + timeoutInMillis + "ms", e);
        } catch (Exception e) {
            throw new RuntimeException("API call execution failed", e);
        }
    }
    
    /**
     * Handle successful API call
     * Success के बाद circuit breaker state update करते हैं
     */
    private void onSuccess(long executionTime) {
        failureCount.set(0);
        successCount.incrementAndGet();
        
        // If we were in HALF_OPEN state, close the circuit
        if (state == State.HALF_OPEN) {
            logger.info("✅ Circuit breaker closing - Service recovered");
            state = State.CLOSED;
        }
        
        logger.fine("✅ API call successful in " + executionTime + "ms");
    }
    
    /**
     * Handle failed API call
     * Failure के बाद circuit breaker logic apply करते हैं
     */
    private void onFailure(Exception e) {
        int failures = failureCount.incrementAndGet();
        lastFailureTime.set(System.currentTimeMillis());
        
        logger.warning("❌ API failure count: " + failures + "/" + failureThreshold);
        
        // Open circuit if failure threshold reached
        if (failures >= failureThreshold) {
            logger.severe("🚨 Circuit breaker OPENING - Too many failures!");
            state = State.OPEN;
        }
    }
    
    /**
     * Check if we should retry (for OPEN state)
     * OPEN state में retry करना चाहिए या नहीं check करते हैं
     */
    private boolean shouldRetry() {
        long timeSinceLastFailure = System.currentTimeMillis() - lastFailureTime.get();
        return timeSinceLastFailure >= retryTimeoutInMillis;
    }
    
    /**
     * Get current circuit breaker metrics
     * Current metrics और health status return करते हैं
     */
    public CircuitBreakerMetrics getMetrics() {
        return new CircuitBreakerMetrics(
            state,
            failureCount.get(),
            successCount.get(),
            failureThreshold,
            lastFailureTime.get()
        );
    }
    
    /**
     * Reset circuit breaker to initial state
     * Circuit breaker को reset करते हैं
     */
    public void reset() {
        logger.info("🔄 Resetting circuit breaker to CLOSED state");
        state = State.CLOSED;
        failureCount.set(0);
        successCount.set(0);
        lastFailureTime.set(0);
    }
    
    /**
     * Graceful shutdown
     */
    public void shutdown() {
        logger.info("🛑 Shutting down circuit breaker executor");
        executor.shutdown();
        try {
            if (!executor.awaitTermination(30, java.util.concurrent.TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    /**
     * Circuit breaker metrics data class
     */
    public static class CircuitBreakerMetrics {
        private final State state;
        private final int failureCount;
        private final int successCount;
        private final int failureThreshold;
        private final long lastFailureTime;
        
        public CircuitBreakerMetrics(State state, int failureCount, int successCount, 
                                   int failureThreshold, long lastFailureTime) {
            this.state = state;
            this.failureCount = failureCount;
            this.successCount = successCount;
            this.failureThreshold = failureThreshold;
            this.lastFailureTime = lastFailureTime;
        }
        
        public State getState() { return state; }
        public int getFailureCount() { return failureCount; }
        public int getSuccessCount() { return successCount; }
        public int getFailureThreshold() { return failureThreshold; }
        public long getLastFailureTime() { return lastFailureTime; }
        
        public double getSuccessRate() {
            int total = successCount + failureCount;
            return total > 0 ? (double) successCount / total : 0.0;
        }
        
        @Override
        public String toString() {
            return String.format(
                "CircuitBreakerMetrics{state=%s, failures=%d/%d, success_rate=%.2f%%, last_failure=%d}",
                state, failureCount, failureThreshold, getSuccessRate() * 100, lastFailureTime
            );
        }
    }
    
    /**
     * Demo class showing Flipkart-like usage
     */
    public static class FlipkartAPIDemo {
        
        private final CircuitBreakerAPIClient circuitBreaker;
        
        public FlipkartAPIDemo() {
            // Initialize with production-ready settings
            this.circuitBreaker = new CircuitBreakerAPIClient(
                3,      // 3 failures to open circuit
                5000,   // 5 second timeout  
                30000,  // 30 second retry timeout
                3       // Max 3 retry attempts
            );
        }
        
        /**
         * Simulate Flipkart product search API call
         */
        public CompletableFuture<String> searchProducts(String query) {
            return circuitBreaker.execute(
                // Primary operation - actual API call
                () -> {
                    logger.info("🔍 Searching products for: " + query);
                    
                    // Simulate API call to product service
                    simulateNetworkCall(2000); // 2 second network call
                    
                    // Simulate random failures (20% failure rate)
                    if (Math.random() < 0.2) {
                        throw new RuntimeException("Product service unavailable");
                    }
                    
                    return String.format("Found 25 products for '%s' - Price range: ₹299-₹2999", query);
                },
                
                // Fallback operation - cached results
                () -> {
                    logger.info("📦 Using cached results for: " + query);
                    return String.format("Cached results for '%s' - Limited selection available", query);
                }
            );
        }
        
        /**
         * Simulate Flipkart order placement
         */
        public CompletableFuture<String> placeOrder(String productId, String userId) {
            return circuitBreaker.execute(
                // Primary operation
                () -> {
                    logger.info("🛒 Placing order - Product: " + productId + ", User: " + userId);
                    
                    simulateNetworkCall(3000); // 3 second order processing
                    
                    // Simulate failures during high traffic
                    if (Math.random() < 0.15) {
                        throw new RuntimeException("Order service overloaded");
                    }
                    
                    String orderId = "ORD" + System.currentTimeMillis();
                    return String.format("Order placed successfully! Order ID: %s", orderId);
                },
                
                // Fallback operation - queue order
                () -> {
                    logger.info("📋 Queueing order for later processing");
                    return "Order queued - You'll receive confirmation within 15 minutes";
                }
            );
        }
        
        /**
         * Simulate network call with random delays
         */
        private void simulateNetworkCall(int baseDelayMs) {
            try {
                // Add some randomness to simulate real network conditions
                int delay = baseDelayMs + (int) (Math.random() * 1000);
                Thread.sleep(delay);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new RuntimeException("Network call interrupted", e);
            }
        }
        
        /**
         * Monitor circuit breaker health
         */
        public void printHealthStatus() {
            CircuitBreakerMetrics metrics = circuitBreaker.getMetrics();
            
            System.out.println("\n📊 Circuit Breaker Health Status:");
            System.out.println("================================");
            System.out.println("🔴 Current State: " + metrics.getState());
            System.out.println("❌ Failures: " + metrics.getFailureCount() + "/" + metrics.getFailureThreshold());
            System.out.println("✅ Successes: " + metrics.getSuccessCount());
            System.out.println("📈 Success Rate: " + String.format("%.1f%%", metrics.getSuccessRate() * 100));
            
            if (metrics.getLastFailureTime() > 0) {
                long timeSinceFailure = System.currentTimeMillis() - metrics.getLastFailureTime();
                System.out.println("⏰ Last Failure: " + timeSinceFailure / 1000 + " seconds ago");
            }
            
            System.out.println();
        }
        
        public void shutdown() {
            circuitBreaker.shutdown();
        }
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) {
        System.out.println("🚀 Circuit Breaker API Client Demo");
        System.out.println("🇮🇳 Flipkart-style resilient API calls");
        System.out.println("=" + "=".repeat(50));
        
        FlipkartAPIDemo demo = new FlipkartAPIDemo();
        
        try {
            // Test multiple API calls
            for (int i = 1; i <= 10; i++) {
                System.out.println("\n🔄 Test " + i + ":");
                
                // Product search test
                CompletableFuture<String> searchResult = demo.searchProducts("smartphone");
                System.out.println("Search: " + searchResult.get());
                
                // Order placement test
                CompletableFuture<String> orderResult = demo.placeOrder("PROD123", "USER456");
                System.out.println("Order: " + orderResult.get());
                
                // Print health status every 3 calls
                if (i % 3 == 0) {
                    demo.printHealthStatus();
                }
                
                // Small delay between tests
                Thread.sleep(1000);
            }
            
            System.out.println("\n🎉 Circuit breaker demo completed!");
            System.out.println("💡 Key learnings:");
            System.out.println("  - Automatic failure detection और recovery");
            System.out.println("  - Graceful degradation with fallback responses");
            System.out.println("  - Production-ready timeout handling");
            System.out.println("  - Real-time health monitoring");
            
        } catch (Exception e) {
            logger.log(Level.SEVERE, "Demo execution failed", e);
        } finally {
            demo.shutdown();
        }
    }
}