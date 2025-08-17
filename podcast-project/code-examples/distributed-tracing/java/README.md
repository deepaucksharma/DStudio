# ☕ Java Distributed Tracing Examples
## Episode 67: Distributed Tracing - Java Implementations

---

## 🇮🇳 भारतीय Context में Distributed Tracing

Distributed tracing Indian e-commerce में बहुत important है। जब Flipkart पर order place करते हैं - product service, inventory service, payment service, shipping service - सबमें से request गुजरती है। हर step को trace करना पड़ता है।

Mumbai delivery boy की तरह, हर package का पूरा journey track करना होता है - warehouse से customer तक।

---

## 📂 Examples Structure

```
java/
├── 01_jaeger_tracing_integration.java    # Jaeger distributed tracing
├── 02_zipkin_microservices.java          # Zipkin tracing implementation
├── 03_opentelemetry_setup.java           # OpenTelemetry complete setup
├── 04_custom_span_management.java        # Manual span instrumentation
├── 05_correlation_id_tracking.java       # Request correlation patterns
├── pom.xml                                # Maven dependencies
├── tests/                                 # Unit tests
│   ├── TracingTest.java
│   └── SpanTest.java
└── README.md                             # This file
```

---

## ☕ Example 1: Jaeger Distributed Tracing Integration

```java
/*
🇮🇳 Jaeger Distributed Tracing - Flipkart Order Processing Style
E-commerce order की पूरी journey trace करने जैसा

Features:
- Complete Jaeger integration
- Microservices tracing
- Custom span creation
- Flipkart order processing patterns
- Error tracking and debugging
- Performance monitoring
- Hindi comments

Author: Agent 5 - Code Developer
Episode: 67 - Distributed Tracing
Context: Flipkart-style order processing system
*/

package com.flipkart.tracing;

import io.jaegertracing.Configuration;
import io.jaegertracing.internal.JaegerTracer;
import io.jaegertracing.internal.samplers.ConstSampler;
import io.opentracing.Scope;
import io.opentracing.Span;
import io.opentracing.Tracer;
import io.opentracing.log.Fields;
import io.opentracing.tag.Tags;
import io.opentracing.util.GlobalTracer;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * Flipkart Order Processing Service with Jaeger Tracing
 * 
 * यह service complete order processing pipeline को trace करती है:
 * - Product validation (product service)
 * - Inventory check (inventory service)  
 * - Payment processing (payment service)
 * - Shipping arrangement (logistics service)
 */
public class FlipkartOrderProcessingService {
    
    private static final Logger logger = LoggerFactory.getLogger(FlipkartOrderProcessingService.class);
    private final Tracer tracer;
    private final ExecutorService executorService;
    
    // Mock services for demonstration
    private final ProductService productService;
    private final InventoryService inventoryService;
    private final PaymentService paymentService;
    private final LogisticsService logisticsService;
    
    public FlipkartOrderProcessingService() {
        // Initialize Jaeger tracer
        this.tracer = initializeJaegerTracer();
        this.executorService = Executors.newFixedThreadPool(10);
        
        // Initialize mock services
        this.productService = new ProductService(tracer);
        this.inventoryService = new InventoryService(tracer);
        this.paymentService = new PaymentService(tracer);
        this.logisticsService = new LogisticsService(tracer);
        
        logger.info("🛒 Flipkart Order Processing Service initialized with Jaeger tracing");
    }
    
    /**
     * Initialize Jaeger tracer configuration
     * Jaeger tracer setup for Flipkart microservices
     */
    private Tracer initializeJaegerTracer() {
        // Jaeger configuration
        Configuration.SamplerConfiguration samplerConfig = 
            Configuration.SamplerConfiguration.fromEnv()
                .withType(ConstSampler.TYPE)
                .withParam(1); // Sample all requests
        
        Configuration.ReporterConfiguration reporterConfig = 
            Configuration.ReporterConfiguration.fromEnv()
                .withLogSpans(true)
                .withFlushInterval(1000)
                .withMaxQueueSize(10000);
        
        Configuration config = new Configuration("flipkart-order-service")
            .withSampler(samplerConfig)
            .withReporter(reporterConfig);
        
        JaegerTracer jaegerTracer = config.getTracer();
        GlobalTracer.registerIfAbsent(jaegerTracer);
        
        logger.info("📊 Jaeger tracer initialized for Flipkart order service");
        return jaegerTracer;
    }
    
    /**
     * Process order with complete distributed tracing
     * Order processing main method with tracing
     */
    public CompletableFuture<OrderResult> processOrder(OrderRequest orderRequest) {
        // Create root span for order processing
        Span orderSpan = tracer.nextSpan()
            .setOperationName("flipkart.order.process")
            .setTag(Tags.COMPONENT, "order-service")
            .setTag(Tags.SPAN_KIND, Tags.SPAN_KIND_SERVER)
            .setTag("order.id", orderRequest.getOrderId())
            .setTag("customer.id", orderRequest.getCustomerId())
            .setTag("order.value", orderRequest.getTotalValue())
            .setTag("region", orderRequest.getRegion())
            .start();
        
        // Add custom tags for business context
        orderSpan.setTag("business.category", "e-commerce");
        orderSpan.setTag("platform", "flipkart");
        orderSpan.setTag("order.items.count", orderRequest.getItems().size());
        
        try (Scope scope = tracer.scopeManager().activate(orderSpan)) {
            logger.info("🛒 Processing order: {} for customer: {} in region: {}", 
                       orderRequest.getOrderId(), 
                       orderRequest.getCustomerId(),
                       orderRequest.getRegion());
            
            // Process order through multiple services
            return CompletableFuture
                .supplyAsync(() -> validateProducts(orderRequest), executorService)
                .thenCompose(this::checkInventory)
                .thenCompose(this::processPayment)
                .thenCompose(this::arrangeShipping)
                .whenComplete((result, throwable) -> {
                    if (throwable != null) {
                        // Log error in span
                        Tags.ERROR.set(orderSpan, true);
                        orderSpan.log(Map.of(
                            Fields.EVENT, "error",
                            Fields.ERROR_OBJECT, throwable,
                            Fields.MESSAGE, "Order processing failed: " + throwable.getMessage()
                        ));
                        logger.error("❌ Order processing failed for {}: {}", 
                                   orderRequest.getOrderId(), throwable.getMessage());
                    } else {
                        orderSpan.setTag("order.status", result.getStatus());
                        orderSpan.setTag("processing.time.ms", result.getProcessingTimeMs());
                        logger.info("✅ Order {} processed successfully with status: {}", 
                                   orderRequest.getOrderId(), result.getStatus());
                    }
                    orderSpan.finish();
                });
                
        } catch (Exception e) {
            Tags.ERROR.set(orderSpan, true);
            orderSpan.log(Map.of(
                Fields.EVENT, "error",
                Fields.ERROR_OBJECT, e,
                Fields.MESSAGE, "Unexpected error: " + e.getMessage()
            ));
            orderSpan.finish();
            throw e;
        }
    }
    
    /**
     * Validate products in the order
     * Product validation step with tracing
     */
    private OrderProcessingContext validateProducts(OrderRequest orderRequest) {
        Span validateSpan = tracer.nextSpan()
            .setOperationName("flipkart.product.validate")
            .setTag(Tags.COMPONENT, "product-service")
            .setTag("order.id", orderRequest.getOrderId())
            .start();
        
        try (Scope scope = tracer.scopeManager().activate(validateSpan)) {
            logger.info("📦 Validating products for order: {}", orderRequest.getOrderId());
            
            // Simulate product validation
            List<ProductValidationResult> validationResults = new ArrayList<>();
            
            for (OrderItem item : orderRequest.getItems()) {
                ProductValidationResult result = productService.validateProduct(item.getProductId());
                validationResults.add(result);
                
                // Add product-specific spans
                validateSpan.setTag("product." + item.getProductId() + ".valid", result.isValid());
                validateSpan.setTag("product." + item.getProductId() + ".category", result.getCategory());
            }
            
            OrderProcessingContext context = new OrderProcessingContext(orderRequest);
            context.setProductValidationResults(validationResults);
            
            validateSpan.setTag("validation.products.count", validationResults.size());
            validateSpan.setTag("validation.status", "success");
            
            logger.info("✅ Product validation completed for order: {}", orderRequest.getOrderId());
            return context;
            
        } catch (Exception e) {
            Tags.ERROR.set(validateSpan, true);
            validateSpan.log(Map.of(
                Fields.EVENT, "error",
                Fields.ERROR_OBJECT, e,
                Fields.MESSAGE, "Product validation failed: " + e.getMessage()
            ));
            logger.error("❌ Product validation failed for order {}: {}", 
                        orderRequest.getOrderId(), e.getMessage());
            throw e;
        } finally {
            validateSpan.finish();
        }
    }
    
    /**
     * Check inventory availability
     * Inventory checking step with tracing
     */
    private CompletableFuture<OrderProcessingContext> checkInventory(OrderProcessingContext context) {
        return CompletableFuture.supplyAsync(() -> {
            Span inventorySpan = tracer.nextSpan()
                .setOperationName("flipkart.inventory.check")
                .setTag(Tags.COMPONENT, "inventory-service")
                .setTag("order.id", context.getOrderRequest().getOrderId())
                .start();
            
            try (Scope scope = tracer.scopeManager().activate(inventorySpan)) {
                logger.info("📊 Checking inventory for order: {}", context.getOrderRequest().getOrderId());
                
                // Simulate inventory checking across multiple warehouses
                Map<String, InventoryStatus> inventoryResults = new HashMap<>();
                
                for (OrderItem item : context.getOrderRequest().getItems()) {
                    InventoryStatus status = inventoryService.checkInventory(
                        item.getProductId(), 
                        item.getQuantity(),
                        context.getOrderRequest().getRegion()
                    );
                    inventoryResults.put(item.getProductId(), status);
                    
                    // Add inventory-specific metadata
                    inventorySpan.setTag("inventory." + item.getProductId() + ".available", status.isAvailable());
                    inventorySpan.setTag("inventory." + item.getProductId() + ".warehouse", status.getWarehouse());
                    inventorySpan.setTag("inventory." + item.getProductId() + ".stock", status.getStockCount());
                }
                
                context.setInventoryResults(inventoryResults);
                
                inventorySpan.setTag("inventory.check.status", "completed");
                inventorySpan.setTag("inventory.warehouses.checked", inventoryResults.size());
                
                logger.info("✅ Inventory check completed for order: {}", context.getOrderRequest().getOrderId());
                return context;
                
            } catch (Exception e) {
                Tags.ERROR.set(inventorySpan, true);
                inventorySpan.log(Map.of(
                    Fields.EVENT, "error",
                    Fields.ERROR_OBJECT, e,
                    Fields.MESSAGE, "Inventory check failed: " + e.getMessage()
                ));
                logger.error("❌ Inventory check failed for order {}: {}", 
                           context.getOrderRequest().getOrderId(), e.getMessage());
                throw e;
            } finally {
                inventorySpan.finish();
            }
        }, executorService);
    }
    
    /**
     * Process payment for the order
     * Payment processing step with tracing
     */
    private CompletableFuture<OrderProcessingContext> processPayment(OrderProcessingContext context) {
        return CompletableFuture.supplyAsync(() -> {
            Span paymentSpan = tracer.nextSpan()
                .setOperationName("flipkart.payment.process")
                .setTag(Tags.COMPONENT, "payment-service")
                .setTag("order.id", context.getOrderRequest().getOrderId())
                .setTag("payment.amount", context.getOrderRequest().getTotalValue())
                .setTag("payment.method", context.getOrderRequest().getPaymentMethod())
                .start();
            
            try (Scope scope = tracer.scopeManager().activate(paymentSpan)) {
                logger.info("💳 Processing payment for order: {} amount: ₹{}", 
                           context.getOrderRequest().getOrderId(),
                           context.getOrderRequest().getTotalValue());
                
                // Simulate payment processing
                PaymentResult paymentResult = paymentService.processPayment(
                    context.getOrderRequest().getOrderId(),
                    context.getOrderRequest().getTotalValue(),
                    context.getOrderRequest().getPaymentMethod(),
                    context.getOrderRequest().getCustomerId()
                );
                
                context.setPaymentResult(paymentResult);
                
                // Add payment-specific metadata
                paymentSpan.setTag("payment.transaction.id", paymentResult.getTransactionId());
                paymentSpan.setTag("payment.gateway", paymentResult.getGateway());
                paymentSpan.setTag("payment.status", paymentResult.getStatus());
                paymentSpan.setTag("payment.processing.time.ms", paymentResult.getProcessingTimeMs());
                
                if (paymentResult.isSuccess()) {
                    logger.info("✅ Payment processed successfully for order: {} transaction: {}", 
                               context.getOrderRequest().getOrderId(), paymentResult.getTransactionId());
                } else {
                    paymentSpan.setTag("payment.failure.reason", paymentResult.getFailureReason());
                    logger.warn("⚠️ Payment failed for order: {} reason: {}", 
                               context.getOrderRequest().getOrderId(), paymentResult.getFailureReason());
                }
                
                return context;
                
            } catch (Exception e) {
                Tags.ERROR.set(paymentSpan, true);
                paymentSpan.log(Map.of(
                    Fields.EVENT, "error",
                    Fields.ERROR_OBJECT, e,
                    Fields.MESSAGE, "Payment processing failed: " + e.getMessage()
                ));
                logger.error("❌ Payment processing failed for order {}: {}", 
                           context.getOrderRequest().getOrderId(), e.getMessage());
                throw e;
            } finally {
                paymentSpan.finish();
            }
        }, executorService);
    }
    
    /**
     * Arrange shipping for the order
     * Logistics arrangement step with tracing
     */
    private CompletableFuture<OrderResult> arrangeShipping(OrderProcessingContext context) {
        return CompletableFuture.supplyAsync(() -> {
            Span shippingSpan = tracer.nextSpan()
                .setOperationName("flipkart.shipping.arrange")
                .setTag(Tags.COMPONENT, "logistics-service")
                .setTag("order.id", context.getOrderRequest().getOrderId())
                .setTag("shipping.address.city", context.getOrderRequest().getShippingAddress().getCity())
                .setTag("shipping.address.state", context.getOrderRequest().getShippingAddress().getState())
                .start();
            
            try (Scope scope = tracer.scopeManager().activate(shippingSpan)) {
                logger.info("🚚 Arranging shipping for order: {} to: {}", 
                           context.getOrderRequest().getOrderId(),
                           context.getOrderRequest().getShippingAddress().getCity());
                
                // Simulate shipping arrangement
                ShippingResult shippingResult = logisticsService.arrangeShipping(
                    context.getOrderRequest().getOrderId(),
                    context.getOrderRequest().getShippingAddress(),
                    context.getInventoryResults()
                );
                
                // Create final order result
                OrderResult orderResult = new OrderResult(
                    context.getOrderRequest().getOrderId(),
                    "CONFIRMED",
                    context.getPaymentResult(),
                    shippingResult,
                    System.currentTimeMillis() - context.getStartTime()
                );
                
                // Add shipping-specific metadata
                shippingSpan.setTag("shipping.tracking.id", shippingResult.getTrackingId());
                shippingSpan.setTag("shipping.carrier", shippingResult.getCarrier());
                shippingSpan.setTag("shipping.estimated.delivery", shippingResult.getEstimatedDeliveryDate());
                shippingSpan.setTag("shipping.cost", shippingResult.getShippingCost());
                
                logger.info("✅ Shipping arranged for order: {} tracking: {} carrier: {}", 
                           context.getOrderRequest().getOrderId(),
                           shippingResult.getTrackingId(),
                           shippingResult.getCarrier());
                
                return orderResult;
                
            } catch (Exception e) {
                Tags.ERROR.set(shippingSpan, true);
                shippingSpan.log(Map.of(
                    Fields.EVENT, "error",
                    Fields.ERROR_OBJECT, e,
                    Fields.MESSAGE, "Shipping arrangement failed: " + e.getMessage()
                ));
                logger.error("❌ Shipping arrangement failed for order {}: {}", 
                           context.getOrderRequest().getOrderId(), e.getMessage());
                throw e;
            } finally {
                shippingSpan.finish();
            }
        }, executorService);
    }
    
    /**
     * Get tracing statistics and metrics
     * Tracing metrics for monitoring
     */
    public TracingMetrics getTracingMetrics() {
        // Implementation would depend on Jaeger client metrics
        return new TracingMetrics();
    }
    
    /**
     * Shutdown the service gracefully
     * Graceful shutdown with proper cleanup
     */
    public void shutdown() {
        try {
            logger.info("🛑 Shutting down Flipkart Order Processing Service...");
            
            executorService.shutdown();
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
            
            // Close tracer if it's closeable
            if (tracer instanceof JaegerTracer) {
                ((JaegerTracer) tracer).close();
            }
            
            logger.info("✅ Flipkart Order Processing Service shutdown complete");
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            logger.error("❌ Error during shutdown: {}", e.getMessage());
        }
    }
}

// Supporting classes for the example
class OrderRequest {
    private String orderId;
    private String customerId;
    private List<OrderItem> items;
    private double totalValue;
    private String paymentMethod;
    private String region;
    private Address shippingAddress;
    
    // Constructors, getters, setters
    public OrderRequest(String orderId, String customerId) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.items = new ArrayList<>();
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public List<OrderItem> getItems() { return items; }
    public double getTotalValue() { return totalValue; }
    public String getPaymentMethod() { return paymentMethod; }
    public String getRegion() { return region; }
    public Address getShippingAddress() { return shippingAddress; }
    
    // Setters
    public void setTotalValue(double totalValue) { this.totalValue = totalValue; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    public void setRegion(String region) { this.region = region; }
    public void setShippingAddress(Address shippingAddress) { this.shippingAddress = shippingAddress; }
}

class OrderItem {
    private String productId;
    private int quantity;
    private double price;
    
    public OrderItem(String productId, int quantity, double price) {
        this.productId = productId;
        this.quantity = quantity;
        this.price = price;
    }
    
    // Getters
    public String getProductId() { return productId; }
    public int getQuantity() { return quantity; }
    public double getPrice() { return price; }
}

class Address {
    private String city;
    private String state;
    private String country;
    private String zipCode;
    
    public Address(String city, String state, String country, String zipCode) {
        this.city = city;
        this.state = state;
        this.country = country;
        this.zipCode = zipCode;
    }
    
    // Getters
    public String getCity() { return city; }
    public String getState() { return state; }
    public String getCountry() { return country; }
    public String getZipCode() { return zipCode; }
}

// Additional supporting classes would be defined here...
// (ProductService, InventoryService, PaymentService, LogisticsService, etc.)

class OrderProcessingContext {
    private final OrderRequest orderRequest;
    private final long startTime;
    private List<ProductValidationResult> productValidationResults;
    private Map<String, InventoryStatus> inventoryResults;
    private PaymentResult paymentResult;
    
    public OrderProcessingContext(OrderRequest orderRequest) {
        this.orderRequest = orderRequest;
        this.startTime = System.currentTimeMillis();
    }
    
    // Getters and setters
    public OrderRequest getOrderRequest() { return orderRequest; }
    public long getStartTime() { return startTime; }
    
    public void setProductValidationResults(List<ProductValidationResult> results) {
        this.productValidationResults = results;
    }
    
    public void setInventoryResults(Map<String, InventoryStatus> results) {
        this.inventoryResults = results;
    }
    
    public Map<String, InventoryStatus> getInventoryResults() { return inventoryResults; }
    
    public void setPaymentResult(PaymentResult result) {
        this.paymentResult = result;
    }
    
    public PaymentResult getPaymentResult() { return paymentResult; }
}

class OrderResult {
    private String orderId;
    private String status;
    private PaymentResult paymentResult;
    private ShippingResult shippingResult;
    private long processingTimeMs;
    
    public OrderResult(String orderId, String status, PaymentResult paymentResult, 
                      ShippingResult shippingResult, long processingTimeMs) {
        this.orderId = orderId;
        this.status = status;
        this.paymentResult = paymentResult;
        this.shippingResult = shippingResult;
        this.processingTimeMs = processingTimeMs;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getStatus() { return status; }
    public PaymentResult getPaymentResult() { return paymentResult; }
    public ShippingResult getShippingResult() { return shippingResult; }
    public long getProcessingTimeMs() { return processingTimeMs; }
}

// Mock service implementations would be defined here...
```

This is the comprehensive first Java example for distributed tracing. Let me continue with the other examples in the same detailed manner.