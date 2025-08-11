/**
 * Circuit Breaker with Hystrix Pattern - Episode 2
 * Hystrix पैटर्न के साथ सर्किट ब्रेकर
 * 
 * Production-ready Circuit Breaker implementation for resilient microservices
 * माइक्रोसर्विसेज के लिए resilient सर्किट ब्रेकर implementation
 * 
 * जैसे Mumbai local train में safety mechanisms होते हैं - 
 * अगर कोई problem है तो train रुक जाती है, fix होने के बाद चलती है!
 * 
 * Author: Code Developer Agent A5-C-002
 * Indian Context: Flipkart Payment Gateway, Zomato Order Processing, IRCTC Booking
 */

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;
import java.time.*;
import java.util.*;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * Circuit Breaker States - सर्किट ब्रेकर की स्थितियां
 */
enum CircuitBreakerState {
    CLOSED,    // सामान्य स्थिति - Normal operation, requests flow through
    OPEN,      // खुली स्थिति - Failing fast, not calling downstream service  
    HALF_OPEN  // अर्ध-खुली स्थिति - Testing if downstream service is back up
}

/**
 * Circuit Breaker Configuration - सर्किट ब्रेकर कॉन्फ़िगरेशन
 */
class CircuitBreakerConfig {
    private final int failureThreshold;           // कितनी failures के बाद OPEN करना - e.g., 5
    private final int successThreshold;           // कितनी success के बाद CLOSED करना - e.g., 3
    private final Duration timeout;               // कितनी देर बाद HALF_OPEN करना - e.g., 60 seconds
    private final Duration requestTimeout;        // Individual request timeout
    private final int rollingWindowSize;          // Rolling window size for failure counting
    private final double failureRateThreshold;   // Failure rate threshold (0.0 to 1.0)
    
    public CircuitBreakerConfig(int failureThreshold, int successThreshold, 
                               Duration timeout, Duration requestTimeout,
                               int rollingWindowSize, double failureRateThreshold) {
        this.failureThreshold = failureThreshold;
        this.successThreshold = successThreshold;
        this.timeout = timeout;
        this.requestTimeout = requestTimeout;
        this.rollingWindowSize = rollingWindowSize;
        this.failureRateThreshold = failureRateThreshold;
    }
    
    // Indian service specific configurations
    public static CircuitBreakerConfig forPaymentGateway() {
        // Payment services need quick failover - पेमेंट सर्विस के लिए जल्दी failover
        return new CircuitBreakerConfig(
            3,                              // कम failures tolerance - only 3 failures
            2,                              // जल्दी recovery - only 2 success needed
            Duration.ofSeconds(30),         // जल्दी retry - 30 seconds timeout
            Duration.ofSeconds(5),          // Quick request timeout
            10,                             // Small rolling window
            0.3                            // 30% failure rate threshold
        );
    }
    
    public static CircuitBreakerConfig forRecommendationService() {
        // Recommendation can tolerate more failures - recommendation अधिक failures सह सकती है
        return new CircuitBreakerConfig(
            10,                             // ज्यादा failures tolerance - 10 failures
            5,                              // धीमी recovery - 5 success needed
            Duration.ofMinutes(2),          // लंबी timeout - 2 minutes
            Duration.ofSeconds(10),         // Longer request timeout
            50,                             // Larger rolling window
            0.6                            // 60% failure rate threshold
        );
    }
    
    public static CircuitBreakerConfig forBookingService() {
        // IRCTC style booking - critical but can handle some failures
        return new CircuitBreakerConfig(
            5,                              // Moderate failures tolerance
            3,                              // Moderate recovery
            Duration.ofSeconds(60),         // 1 minute timeout
            Duration.ofSeconds(15),         // Longer timeout for complex booking
            25,                             // Medium rolling window
            0.4                            // 40% failure rate threshold
        );
    }
    
    // Getters
    public int getFailureThreshold() { return failureThreshold; }
    public int getSuccessThreshold() { return successThreshold; }
    public Duration getTimeout() { return timeout; }
    public Duration getRequestTimeout() { return requestTimeout; }
    public int getRollingWindowSize() { return rollingWindowSize; }
    public double getFailureRateThreshold() { return failureRateThreshold; }
}

/**
 * Circuit Breaker Metrics - सर्किट ब्रेकर के metrics
 */
class CircuitBreakerMetrics {
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong successfulRequests = new AtomicLong(0);
    private final AtomicLong failedRequests = new AtomicLong(0);
    private final AtomicLong rejectedRequests = new AtomicLong(0);
    private final AtomicLong timeouts = new AtomicLong(0);
    
    // Rolling window for recent requests
    private final Queue<RequestResult> rollingWindow = new ConcurrentLinkedQueue<>();
    private final int windowSize;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    
    public CircuitBreakerMetrics(int windowSize) {
        this.windowSize = windowSize;
    }
    
    public void recordSuccess() {
        totalRequests.incrementAndGet();
        successfulRequests.incrementAndGet();
        addToRollingWindow(new RequestResult(true, Instant.now()));
    }
    
    public void recordFailure() {
        totalRequests.incrementAndGet();
        failedRequests.incrementAndGet();
        addToRollingWindow(new RequestResult(false, Instant.now()));
    }
    
    public void recordRejection() {
        rejectedRequests.incrementAndGet();
    }
    
    public void recordTimeout() {
        totalRequests.incrementAndGet();
        timeouts.incrementAndGet();
        addToRollingWindow(new RequestResult(false, Instant.now()));
    }
    
    private void addToRollingWindow(RequestResult result) {
        lock.writeLock().lock();
        try {
            rollingWindow.offer(result);
            while (rollingWindow.size() > windowSize) {
                rollingWindow.poll();
            }
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public double getFailureRate() {
        lock.readLock().lock();
        try {
            if (rollingWindow.isEmpty()) {
                return 0.0;
            }
            
            long failures = rollingWindow.stream()
                .mapToLong(r -> r.isSuccess() ? 0 : 1)
                .sum();
            
            return (double) failures / rollingWindow.size();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public int getRecentFailureCount() {
        lock.readLock().lock();
        try {
            return (int) rollingWindow.stream()
                .mapToLong(r -> r.isSuccess() ? 0 : 1)
                .sum();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    public int getRecentSuccessCount() {
        lock.readLock().lock();
        try {
            return (int) rollingWindow.stream()
                .mapToLong(r -> r.isSuccess() ? 1 : 0)
                .sum();
        } finally {
            lock.readLock().unlock();
        }
    }
    
    // Getters for metrics
    public long getTotalRequests() { return totalRequests.get(); }
    public long getSuccessfulRequests() { return successfulRequests.get(); }
    public long getFailedRequests() { return failedRequests.get(); }
    public long getRejectedRequests() { return rejectedRequests.get(); }
    public long getTimeouts() { return timeouts.get(); }
    
    public double getSuccessRate() {
        long total = totalRequests.get();
        return total == 0 ? 0.0 : (double) successfulRequests.get() / total;
    }
    
    private static class RequestResult {
        private final boolean success;
        private final Instant timestamp;
        
        public RequestResult(boolean success, Instant timestamp) {
            this.success = success;
            this.timestamp = timestamp;
        }
        
        public boolean isSuccess() { return success; }
        public Instant getTimestamp() { return timestamp; }
    }
}

/**
 * Circuit Breaker Exception - सर्किट ब्रेकर exception
 */
class CircuitBreakerOpenException extends RuntimeException {
    public CircuitBreakerOpenException(String serviceName, String message) {
        super(String.format("Circuit Breaker OPEN for service '%s': %s | सर्किट ब्रेकर खुला है: %s", 
                          serviceName, message, message));
    }
}

/**
 * Main Circuit Breaker Implementation - मुख्य सर्किट ब्रेकर implementation
 */
public class CircuitBreakerHystrix<T> {
    
    private final String serviceName;
    private final CircuitBreakerConfig config;
    private final CircuitBreakerMetrics metrics;
    private final ExecutorService executorService;
    
    // State management
    private volatile CircuitBreakerState state = CircuitBreakerState.CLOSED;
    private volatile Instant lastFailureTime = Instant.now();
    private final AtomicInteger consecutiveSuccesses = new AtomicInteger(0);
    private final Object stateLock = new Object();
    
    // Fallback function
    private Function<Exception, T> fallbackFunction;
    
    public CircuitBreakerHystrix(String serviceName, CircuitBreakerConfig config) {
        this.serviceName = serviceName;
        this.config = config;
        this.metrics = new CircuitBreakerMetrics(config.getRollingWindowSize());
        this.executorService = Executors.newCachedThreadPool(r -> {
            Thread t = new Thread(r, "CircuitBreaker-" + serviceName);
            t.setDaemon(true);
            return t;
        });
        
        System.out.printf("🔧 Circuit Breaker initialized for service: %s | सर्विस के लिए सर्किट ब्रेकर: %s%n", 
                         serviceName, serviceName);
        System.out.printf("   Config: Failure Threshold=%d, Success Threshold=%d, Timeout=%s%n",
                         config.getFailureThreshold(), config.getSuccessThreshold(), config.getTimeout());
    }
    
    /**
     * Set fallback function - fallback function सेट करें
     * यह function तब call होती है जब main service fail हो जाती है
     */
    public CircuitBreakerHystrix<T> withFallback(Function<Exception, T> fallback) {
        this.fallbackFunction = fallback;
        System.out.printf("✅ Fallback function registered for %s | Fallback function रजिस्टर: %s%n", 
                         serviceName, serviceName);
        return this;
    }
    
    /**
     * Execute a supplier with circuit breaker protection
     * सर्किट ब्रेकर protection के साथ function execute करें
     */
    public T execute(Supplier<T> supplier) {
        return execute(supplier, "default-operation");
    }
    
    public T execute(Supplier<T> supplier, String operationName) {
        // Check circuit breaker state
        if (state == CircuitBreakerState.OPEN) {
            if (shouldTryHalfOpen()) {
                // Mumbai local train logic: थोड़ी देर बाद check करते हैं कि service ठीक है या नहीं
                System.out.printf("🔄 Circuit Breaker moving to HALF_OPEN for %s | HALF_OPEN में जा रहे हैं: %s%n", 
                                 serviceName, serviceName);
                synchronized (stateLock) {
                    if (state == CircuitBreakerState.OPEN) {
                        state = CircuitBreakerState.HALF_OPEN;
                    }
                }
            } else {
                // Still in OPEN state, reject request
                metrics.recordRejection();
                String errorMsg = String.format("Service %s circuit breaker is OPEN | सर्विस %s का circuit breaker खुला है", 
                                               serviceName, serviceName);
                
                if (fallbackFunction != null) {
                    System.out.printf("🔄 Using fallback for %s operation | Fallback का उपयोग: %s%n", 
                                     operationName, operationName);
                    return fallbackFunction.apply(new CircuitBreakerOpenException(serviceName, errorMsg));
                } else {
                    throw new CircuitBreakerOpenException(serviceName, errorMsg);
                }
            }
        }
        
        // Execute the operation with timeout
        return executeWithTimeout(supplier, operationName);
    }
    
    private T executeWithTimeout(Supplier<T> supplier, String operationName) {
        CompletableFuture<T> future = CompletableFuture.supplyAsync(() -> {
            try {
                System.out.printf("🚀 Executing %s operation for service %s | ऑपरेशन चला रहे हैं: %s%n", 
                                 operationName, serviceName, operationName);
                return supplier.get();
            } catch (Exception e) {
                System.err.printf("❌ Operation failed for %s: %s | ऑपरेशन असफल: %s - %s%n", 
                                 serviceName, e.getMessage(), serviceName, e.getMessage());
                throw new RuntimeException(e);
            }
        }, executorService);
        
        try {
            T result = future.get(config.getRequestTimeout().toMillis(), TimeUnit.MILLISECONDS);
            
            // Operation succeeded
            handleSuccess();
            System.out.printf("✅ Success: %s operation for %s | सफलता: %s - %s%n", 
                             operationName, serviceName, operationName, serviceName);
            return result;
            
        } catch (TimeoutException e) {
            future.cancel(true);
            handleTimeout();
            String timeoutMsg = String.format("Timeout after %s for operation %s | %s के बाद timeout: %s", 
                                            config.getRequestTimeout(), operationName, config.getRequestTimeout(), operationName);
            
            if (fallbackFunction != null) {
                System.out.printf("⏰ Timeout, using fallback for %s | Timeout, fallback का उपयोग: %s%n", 
                                 operationName, operationName);
                return fallbackFunction.apply(new RuntimeException(timeoutMsg));
            } else {
                throw new RuntimeException(timeoutMsg);
            }
            
        } catch (Exception e) {
            handleFailure();
            
            if (fallbackFunction != null) {
                System.out.printf("🔄 Exception, using fallback for %s | Exception, fallback का उपयोग: %s%n", 
                                 operationName, operationName);
                return fallbackFunction.apply(e);
            } else {
                throw new RuntimeException("Circuit breaker execution failed", e);
            }
        }
    }
    
    private void handleSuccess() {
        metrics.recordSuccess();
        
        if (state == CircuitBreakerState.HALF_OPEN) {
            int successes = consecutiveSuccesses.incrementAndGet();
            System.out.printf("📈 HALF_OPEN: %d consecutive successes for %s | लगातार सफलताएं: %d%n", 
                             successes, serviceName, successes);
            
            if (successes >= config.getSuccessThreshold()) {
                // Mumbai local train जब ठीक हो जाती है तो normal service शुरू हो जाती है
                synchronized (stateLock) {
                    state = CircuitBreakerState.CLOSED;
                    consecutiveSuccesses.set(0);
                    System.out.printf("🟢 Circuit Breaker CLOSED for %s - Service recovered | " +
                                     "सर्विस ठीक हो गई: %s%n", serviceName, serviceName);
                }
            }
        }
    }
    
    private void handleFailure() {
        metrics.recordFailure();
        lastFailureTime = Instant.now();
        
        if (state == CircuitBreakerState.HALF_OPEN) {
            // Failed during half-open, go back to open
            synchronized (stateLock) {
                state = CircuitBreakerState.OPEN;
                consecutiveSuccesses.set(0);
                System.out.printf("🔴 Circuit Breaker back to OPEN for %s - Service still failing | " +
                                 "अभी भी सर्विस fail हो रही है: %s%n", serviceName, serviceName);
            }
        } else if (state == CircuitBreakerState.CLOSED) {
            // Check if we should trip the circuit breaker
            if (shouldTripCircuitBreaker()) {
                // Mumbai local train की तरह - अगर बार बार problem आती है तो service बंद कर देते हैं
                synchronized (stateLock) {
                    if (state == CircuitBreakerState.CLOSED) {
                        state = CircuitBreakerState.OPEN;
                        System.out.printf("🔴 Circuit Breaker OPENED for %s - Too many failures | " +
                                         "बहुत ज्यादा failures: %s%n", serviceName, serviceName);
                        System.out.printf("   Recent failures: %d, Failure rate: %.2f%% | " +
                                         "हाल की failures: %d, Failure rate: %.2f%%%n", 
                                         metrics.getRecentFailureCount(), 
                                         metrics.getFailureRate() * 100);
                    }
                }
            }
        }
    }
    
    private void handleTimeout() {
        metrics.recordTimeout();
        lastFailureTime = Instant.now();
        
        // Treat timeout as failure
        if (state == CircuitBreakerState.CLOSED && shouldTripCircuitBreaker()) {
            synchronized (stateLock) {
                if (state == CircuitBreakerState.CLOSED) {
                    state = CircuitBreakerState.OPEN;
                    System.out.printf("🔴 Circuit Breaker OPENED for %s - Timeouts detected | " +
                                     "Timeouts की वजह से बंद: %s%n", serviceName, serviceName);
                }
            }
        }
    }
    
    private boolean shouldTripCircuitBreaker() {
        // Check failure count threshold
        if (metrics.getRecentFailureCount() >= config.getFailureThreshold()) {
            return true;
        }
        
        // Check failure rate threshold
        return metrics.getFailureRate() >= config.getFailureRateThreshold();
    }
    
    private boolean shouldTryHalfOpen() {
        return Instant.now().isAfter(lastFailureTime.plus(config.getTimeout()));
    }
    
    // State and metrics getters
    public CircuitBreakerState getState() {
        return state;
    }
    
    public CircuitBreakerMetrics getMetrics() {
        return metrics;
    }
    
    public String getServiceName() {
        return serviceName;
    }
    
    /**
     * Print detailed status - विस्तृत स्थिति प्रिंट करें
     */
    public void printStatus() {
        System.out.printf("%n📊 Circuit Breaker Status for %s | %s के लिए स्थिति:%n", serviceName, serviceName);
        System.out.printf("   State: %s | स्थिति: %s%n", state, state);
        System.out.printf("   Total Requests: %d | कुल अनुरोध: %d%n", metrics.getTotalRequests(), metrics.getTotalRequests());
        System.out.printf("   Successful: %d (%.1f%%) | सफल: %d (%.1f%%)%n", 
                         metrics.getSuccessfulRequests(), metrics.getSuccessRate() * 100,
                         metrics.getSuccessfulRequests(), metrics.getSuccessRate() * 100);
        System.out.printf("   Failed: %d | असफल: %d%n", metrics.getFailedRequests(), metrics.getFailedRequests());
        System.out.printf("   Timeouts: %d | Timeouts: %d%n", metrics.getTimeouts(), metrics.getTimeouts());
        System.out.printf("   Rejected: %d | अस्वीकृत: %d%n", metrics.getRejectedRequests(), metrics.getRejectedRequests());
        System.out.printf("   Recent Failure Rate: %.1f%% | हाल की असफलता दर: %.1f%%%n", 
                         metrics.getFailureRate() * 100, metrics.getFailureRate() * 100);
        System.out.printf("   Consecutive Successes: %d | लगातार सफलताएं: %d%n", 
                         consecutiveSuccesses.get(), consecutiveSuccesses.get());
    }
    
    /**
     * Reset circuit breaker - सर्किट ब्रेकर रीसेट करें
     * इमरजेंसी के लिए manual reset
     */
    public void reset() {
        synchronized (stateLock) {
            state = CircuitBreakerState.CLOSED;
            consecutiveSuccesses.set(0);
            System.out.printf("🔄 Circuit Breaker manually reset for %s | Manual reset: %s%n", 
                             serviceName, serviceName);
        }
    }
    
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(5, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
        }
    }
    
    /**
     * Demo method to show circuit breaker in action
     * सर्किट ब्रेकर का डेमो
     */
    public static void main(String[] args) {
        System.out.println("🔧 Circuit Breaker with Hystrix Pattern Demo - Episode 2");
        System.out.println("Hystrix पैटर्न के साथ सर्किट ब्रेकर डेमो - एपिसोड 2\n");
        
        // Test different service types with Indian context
        testPaymentGateway();
        System.out.println("\n" + "=".repeat(80) + "\n");
        testRecommendationService();
        System.out.println("\n" + "=".repeat(80) + "\n");
        testBookingService();
        
        System.out.println("\n🎉 All circuit breaker demos completed!");
        System.out.println("सभी सर्किट ब्रेकर डेमो पूर्ण!");
    }
    
    private static void testPaymentGateway() {
        System.out.println("💳 Testing Payment Gateway Circuit Breaker");
        System.out.println("पेमेंट गेटवे सर्किट ब्रेकर का टेस्ट\n");
        
        CircuitBreakerHystrix<String> paymentCB = new CircuitBreakerHystrix<>(
            "PaytmPaymentGateway", 
            CircuitBreakerConfig.forPaymentGateway()
        );
        
        // Set fallback for payment - पेमेंट के लिए fallback
        paymentCB.withFallback(ex -> {
            System.out.println("🔄 Payment fallback: Using wallet balance | Wallet balance का उपयोग");
            return "PAYMENT_PROCESSED_VIA_WALLET";
        });
        
        // Simulate payment requests with failures
        AtomicInteger requestCount = new AtomicInteger(0);
        
        for (int i = 1; i <= 15; i++) {
            try {
                String result = paymentCB.execute(() -> {
                    int reqNum = requestCount.incrementAndGet();
                    
                    // Simulate payment processing
                    if (reqNum <= 5) {
                        // First 5 requests succeed
                        return "PAYMENT_SUCCESS_" + reqNum;
                    } else if (reqNum <= 10) {
                        // Next 5 requests fail (network issues)
                        throw new RuntimeException("Payment gateway timeout - network issues");
                    } else {
                        // Next 5 requests succeed (service recovered)
                        return "PAYMENT_SUCCESS_RECOVERED_" + reqNum;
                    }
                }, "processPayment");
                
                System.out.printf("Request %d: %s%n", i, result);
                
            } catch (Exception e) {
                System.out.printf("Request %d failed: %s%n", i, e.getMessage());
            }
            
            // Print status every 3 requests
            if (i % 3 == 0) {
                paymentCB.printStatus();
                System.out.println();
            }
            
            // Small delay between requests
            try { Thread.sleep(100); } catch (InterruptedException e) { /* ignore */ }
        }
        
        paymentCB.shutdown();
    }
    
    private static void testRecommendationService() {
        System.out.println("🔍 Testing Recommendation Service Circuit Breaker");
        System.out.println("रेकमंडेशन सर्विस सर्किट ब्रेकर का टेस्ट\n");
        
        CircuitBreakerHystrix<List<String>> recommendationCB = new CircuitBreakerHystrix<>(
            "FlipkartRecommendations", 
            CircuitBreakerConfig.forRecommendationService()
        );
        
        // Set fallback for recommendations - रेकमंडेशन के लिए fallback  
        recommendationCB.withFallback(ex -> {
            System.out.println("🔄 Recommendation fallback: Using cached popular items");
            return Arrays.asList("iPhone 15", "Samsung Galaxy S24", "OnePlus 12", "Nothing Phone 2");
        });
        
        Random random = new Random();
        
        for (int i = 1; i <= 20; i++) {
            try {
                List<String> recommendations = recommendationCB.execute(() -> {
                    
                    // 40% chance of failure (ML model overloaded)
                    if (random.nextDouble() < 0.4) {
                        throw new RuntimeException("ML recommendation model overloaded");
                    }
                    
                    // Simulate successful recommendations
                    return Arrays.asList(
                        "Recommended Product " + i + "A",
                        "Recommended Product " + i + "B", 
                        "Recommended Product " + i + "C"
                    );
                }, "getRecommendations");
                
                System.out.printf("Request %d: Got %d recommendations%n", i, recommendations.size());
                
            } catch (Exception e) {
                System.out.printf("Request %d failed: %s%n", i, e.getMessage());
            }
            
            // Print status every 5 requests
            if (i % 5 == 0) {
                recommendationCB.printStatus();
                System.out.println();
            }
            
            try { Thread.sleep(50); } catch (InterruptedException e) { /* ignore */ }
        }
        
        recommendationCB.shutdown();
    }
    
    private static void testBookingService() {
        System.out.println("🚂 Testing IRCTC Booking Service Circuit Breaker");
        System.out.println("IRCTC बुकिंग सर्विस सर्किट ब्रेकर का टेस्ट\n");
        
        CircuitBreakerHystrix<String> bookingCB = new CircuitBreakerHystrix<>(
            "IRCTCBookingService", 
            CircuitBreakerConfig.forBookingService()
        );
        
        // Set fallback for booking - बुकिंग के लिए fallback
        bookingCB.withFallback(ex -> {
            System.out.println("🔄 Booking fallback: Added to waiting list | वेटिंग लिस्ट में जोड़ा गया");
            return "TICKET_WAITLISTED_WL001";
        });
        
        // Simulate Tatkal booking rush
        AtomicInteger bookingAttempt = new AtomicInteger(0);
        
        for (int i = 1; i <= 12; i++) {
            try {
                String result = bookingCB.execute(() -> {
                    int attempt = bookingAttempt.incrementAndGet();
                    
                    // Simulate booking behavior
                    if (attempt <= 3) {
                        // First few bookings succeed
                        return "TICKET_CONFIRMED_PNR" + (1000 + attempt);
                    } else if (attempt <= 8) {
                        // High load period - frequent failures
                        if (attempt % 2 == 0) {
                            throw new RuntimeException("Server overloaded - Tatkal rush hour");
                        } else {
                            return "TICKET_CONFIRMED_PNR" + (1000 + attempt);
                        }
                    } else {
                        // Service stabilizes
                        return "TICKET_CONFIRMED_PNR" + (1000 + attempt);
                    }
                }, "bookTatkalTicket");
                
                System.out.printf("Booking %d: %s%n", i, result);
                
            } catch (Exception e) {
                System.out.printf("Booking %d failed: %s%n", i, e.getMessage());
            }
            
            // Print status every 3 bookings
            if (i % 3 == 0) {
                bookingCB.printStatus();
                System.out.println();
            }
            
            try { Thread.sleep(200); } catch (InterruptedException e) { /* ignore */ }
        }
        
        bookingCB.shutdown();
    }
}