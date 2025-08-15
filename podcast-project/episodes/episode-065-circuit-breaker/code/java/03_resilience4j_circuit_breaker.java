/**
 * Resilience4j Circuit Breaker Implementation
 * Production-grade Java circuit breaker using Resilience4j library
 * 
 * यह modern Java applications में सबसे popular circuit breaker library है
 * Spring Boot के साथ बहुत अच्छी integration है
 */

import io.github.resilience4j.circuitbreaker.CircuitBreaker;
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig;
import io.github.resilience4j.circuitbreaker.CircuitBreakerRegistry;
import io.github.resilience4j.core.IntervalFunction;
import io.github.resilience4j.decorators.Decorators;
import io.github.resilience4j.retry.Retry;
import io.github.resilience4j.retry.RetryConfig;
import io.github.resilience4j.bulkhead.Bulkhead;
import io.github.resilience4j.bulkhead.BulkheadConfig;

import java.time.Duration;
import java.util.Random;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.TimeoutException;
import java.util.function.Supplier;

/**
 * PaymentService - एक typical payment gateway service simulation
 */
class PaymentService {
    private final Random random = new Random();
    private final double failureRate;
    
    public PaymentService(double failureRate) {
        this.failureRate = failureRate;
    }
    
    /**
     * Payment process करता है - randomly fail होता है
     */
    public String processPayment(String orderId, double amount) throws Exception {
        // Response time simulation
        Thread.sleep(random.nextInt(500) + 100);
        
        if (random.nextDouble() < failureRate) {
            throw new RuntimeException("Payment gateway unavailable - UPI server down");
        }
        
        return String.format("Payment successful: Order=%s, Amount=%.2f", orderId, amount);
    }
    
    /**
     * Timeout simulation के लिए slow payment method
     */
    public String slowPayment(String orderId, double amount) throws Exception {
        Thread.sleep(2000); // 2 second delay
        return processPayment(orderId, amount);
    }
}

/**
 * OrderService - Circuit breaker के साथ order processing
 */
class OrderService {
    private final PaymentService paymentService;
    private final CircuitBreaker circuitBreaker;
    private final Retry retry;
    private final Bulkhead bulkhead;
    
    public OrderService() {
        this.paymentService = new PaymentService(0.6); // 60% failure rate
        
        // Circuit breaker configuration - production ready settings
        CircuitBreakerConfig circuitBreakerConfig = CircuitBreakerConfig.custom()
                .failureRateThreshold(50)                    // 50% failure rate पर open होगा
                .waitDurationInOpenState(Duration.ofSeconds(30))  // 30 seconds wait
                .slidingWindowSize(10)                       // Last 10 requests consider करेगा
                .minimumNumberOfCalls(5)                     // कम से कम 5 calls के बाद decide करेगा
                .permittedNumberOfCallsInHalfOpenState(3)    // Half-open में 3 calls allow
                .slowCallRateThreshold(80)                   // 80% slow calls पर भी open
                .slowCallDurationThreshold(Duration.ofMillis(1000)) // 1 second से ज्यादा slow
                .automaticTransitionFromOpenToHalfOpenEnabled(true)
                .build();
        
        // Retry configuration
        RetryConfig retryConfig = RetryConfig.custom()
                .maxAttempts(3)
                .waitDuration(Duration.ofMillis(500))
                .intervalFunction(IntervalFunction.ofExponentialBackoff(Duration.ofMillis(500), 2))
                .build();
        
        // Bulkhead configuration - concurrent requests limit
        BulkheadConfig bulkheadConfig = BulkheadConfig.custom()
                .maxConcurrentCalls(5)                       // Max 5 concurrent calls
                .maxWaitDuration(Duration.ofMillis(1000))    // 1 second wait for slot
                .build();
        
        // Create instances
        this.circuitBreaker = CircuitBreaker.of("paymentService", circuitBreakerConfig);
        this.retry = Retry.of("paymentService", retryConfig);
        this.bulkhead = Bulkhead.of("paymentService", bulkheadConfig);
        
        // Event listeners - monitoring के लिए
        setupEventListeners();
    }
    
    /**
     * Order process करता है circuit breaker protection के साथ
     */
    public String processOrder(String orderId, double amount) {
        // Circuit breaker + Retry + Bulkhead का combination
        Supplier<String> decoratedSupplier = Decorators.ofSupplier(() -> {
            try {
                return paymentService.processPayment(orderId, amount);
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        })
        .withCircuitBreaker(circuitBreaker)
        .withRetry(retry)
        .withBulkhead(bulkhead);
        
        try {
            return decoratedSupplier.get();
        } catch (Exception e) {
            // Fallback mechanism
            return handlePaymentFailure(orderId, amount, e);
        }
    }
    
    /**
     * Async order processing
     */
    public CompletableFuture<String> processOrderAsync(String orderId, double amount) {
        Supplier<CompletableFuture<String>> decoratedSupplier = Decorators.ofSupplier(() -> {
            return CompletableFuture.supplyAsync(() -> {
                try {
                    return paymentService.processPayment(orderId, amount);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
        })
        .withCircuitBreaker(circuitBreaker)
        .withRetry(retry)
        .withBulkhead(bulkhead);
        
        return decoratedSupplier.get()
                .exceptionally(throwable -> handlePaymentFailure(orderId, amount, throwable));
    }
    
    /**
     * Payment failure के लिए fallback mechanism
     */
    private String handlePaymentFailure(String orderId, double amount, Throwable error) {
        System.err.println("🚨 Payment failed for order " + orderId + ": " + error.getMessage());
        
        // Different fallback strategies
        if (error.getMessage().contains("CircuitBreakerOpenException")) {
            // Circuit open है - queue में डाल देते हैं
            return queuePaymentForLater(orderId, amount);
        } else if (error.getMessage().contains("BulkheadFullException")) {
            // Bulkhead full है - priority queue में डालते हैं
            return addToPriorityQueue(orderId, amount);
        } else {
            // Generic failure - alternative payment method try करते हैं
            return tryAlternativePaymentMethod(orderId, amount);
        }
    }
    
    private String queuePaymentForLater(String orderId, double amount) {
        System.out.println("📋 Queuing payment for later: " + orderId);
        // Database में store करके later process करने के लिए
        return "Payment queued for processing when service recovers";
    }
    
    private String addToPriorityQueue(String orderId, double amount) {
        System.out.println("⚡ Adding to priority queue: " + orderId);
        // High priority queue में add करते हैं
        return "Payment added to priority queue";
    }
    
    private String tryAlternativePaymentMethod(String orderId, double amount) {
        System.out.println("🔄 Trying alternative payment method: " + orderId);
        // Alternative payment gateway try करते हैं
        return "Processed via alternative payment gateway";
    }
    
    /**
     * Event listeners setup करता है monitoring के लिए
     */
    private void setupEventListeners() {
        // Circuit breaker events
        circuitBreaker.getEventPublisher()
                .onStateTransition(event -> 
                    System.out.println("🔄 Circuit Breaker State Transition: " + 
                        event.getStateTransition().getFromState() + " -> " + 
                        event.getStateTransition().getToState())
                )
                .onFailureRateExceeded(event -> 
                    System.out.println("📈 Failure rate exceeded: " + 
                        event.getFailureRate() + "%")
                )
                .onCallNotPermitted(event -> 
                    System.out.println("🚫 Call not permitted - Circuit is " + 
                        circuitBreaker.getState())
                )
                .onSlowCallRateExceeded(event -> 
                    System.out.println("🐌 Slow call rate exceeded: " + 
                        event.getSlowCallRate() + "%")
                );
        
        // Retry events
        retry.getEventPublisher()
                .onRetry(event -> 
                    System.out.println("🔁 Retry attempt #" + 
                        event.getNumberOfRetryAttempts() + 
                        " for: " + event.getName())
                );
        
        // Bulkhead events
        bulkhead.getEventPublisher()
                .onCallRejected(event -> 
                    System.out.println("🚧 Bulkhead rejected call - " + 
                        "Available: " + bulkhead.getMetrics().getAvailableConcurrentCalls())
                );
    }
    
    /**
     * Current metrics return करता है
     */
    public void printMetrics() {
        System.out.println("\n📊 Circuit Breaker Metrics:");
        System.out.println("State: " + circuitBreaker.getState());
        System.out.println("Failure Rate: " + circuitBreaker.getMetrics().getFailureRate() + "%");
        System.out.println("Slow Call Rate: " + circuitBreaker.getMetrics().getSlowCallRate() + "%");
        System.out.println("Number of Calls: " + circuitBreaker.getMetrics().getNumberOfCalls());
        System.out.println("Number of Failed Calls: " + circuitBreaker.getMetrics().getNumberOfFailedCalls());
        
        System.out.println("\n📊 Bulkhead Metrics:");
        System.out.println("Available Concurrent Calls: " + bulkhead.getMetrics().getAvailableConcurrentCalls());
        System.out.println("Max Allowed Concurrent Calls: " + bulkhead.getMetrics().getMaxAllowedConcurrentCalls());
        
        System.out.println("─".repeat(50));
    }
}

/**
 * Main class - Circuit breaker testing के लिए
 */
public class Resilience4jCircuitBreakerDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🧪 Testing Resilience4j Circuit Breaker");
        System.out.println("═".repeat(60));
        
        OrderService orderService = new OrderService();
        
        // Test Phase 1: Normal load to trigger circuit opening
        System.out.println("\n📊 Phase 1: Normal load testing");
        System.out.println("─".repeat(40));
        
        for (int i = 1; i <= 20; i++) {
            String orderId = "ORDER_" + i;
            double amount = 100.0 + (i * 10);
            
            try {
                String result = orderService.processOrder(orderId, amount);
                System.out.println("✅ Order " + i + ": " + result);
            } catch (Exception e) {
                System.err.println("❌ Order " + i + " failed: " + e.getMessage());
            }
            
            // हर 5 orders के बाद metrics show करते हैं
            if (i % 5 == 0) {
                orderService.printMetrics();
            }
            
            Thread.sleep(200); // 200ms delay between requests
        }
        
        // Test Phase 2: Wait and test recovery
        System.out.println("\n⏳ Phase 2: Waiting for circuit recovery...");
        Thread.sleep(35000); // Wait for circuit to go half-open
        
        System.out.println("\n📊 Phase 3: Testing recovery");
        System.out.println("─".repeat(40));
        
        // Simulate improved service (lower failure rate)
        OrderService recoveredService = new OrderService();
        
        for (int i = 1; i <= 10; i++) {
            String orderId = "RECOVERY_ORDER_" + i;
            double amount = 500.0 + (i * 50);
            
            try {
                String result = recoveredService.processOrder(orderId, amount);
                System.out.println("✅ Recovery Order " + i + ": " + result);
            } catch (Exception e) {
                System.err.println("❌ Recovery Order " + i + " failed: " + e.getMessage());
            }
            
            Thread.sleep(500);
        }
        
        recoveredService.printMetrics();
        
        // Test Phase 3: Async processing
        System.out.println("\n📊 Phase 4: Async processing test");
        System.out.println("─".repeat(40));
        
        CompletableFuture<String>[] futures = new CompletableFuture[5];
        
        for (int i = 0; i < 5; i++) {
            final int orderNum = i + 1;
            futures[i] = orderService.processOrderAsync("ASYNC_ORDER_" + orderNum, 1000.0)
                    .thenApply(result -> {
                        System.out.println("✅ Async Order " + orderNum + ": " + result);
                        return result;
                    })
                    .exceptionally(throwable -> {
                        System.err.println("❌ Async Order " + orderNum + " failed: " + throwable.getMessage());
                        return "Failed";
                    });
        }
        
        // Wait for all async operations to complete
        CompletableFuture.allOf(futures).join();
        
        System.out.println("\n🎯 Circuit Breaker Demo Completed!");
        orderService.printMetrics();
    }
}

/**
 * Spring Boot Integration Example
 * Spring Boot application में कैसे use करते हैं
 */
/*
@Service
@Component
public class SpringOrderService {
    
    @Autowired
    private PaymentService paymentService;
    
    // Configuration के through circuit breaker enable करते हैं
    @CircuitBreaker(name = "payment-service", fallbackMethod = "fallbackPayment")
    @Retry(name = "payment-service")
    @Bulkhead(name = "payment-service")
    public String processPayment(String orderId, double amount) {
        return paymentService.processPayment(orderId, amount);
    }
    
    // Fallback method
    public String fallbackPayment(String orderId, double amount, Exception ex) {
        return "Payment failed, please try again later. Order queued: " + orderId;
    }
}

// application.yml configuration:
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        failure-rate-threshold: 50
        wait-duration-in-open-state: 30s
        sliding-window-size: 10
        minimum-number-of-calls: 5
  retry:
    instances:
      payment-service:
        max-attempts: 3
        wait-duration: 500ms
  bulkhead:
    instances:
      payment-service:
        max-concurrent-calls: 5
*/