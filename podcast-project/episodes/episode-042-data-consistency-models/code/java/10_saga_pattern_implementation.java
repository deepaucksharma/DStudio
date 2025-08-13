/**
 * Saga Pattern Implementation
 * Long-running distributed transactions with compensation
 * Example: E-commerce order processing across multiple services
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;
import java.util.logging.Logger;
import java.util.logging.Level;

// Saga execution status
enum SagaStatus {
    STARTED, IN_PROGRESS, COMPLETED, COMPENSATING, COMPENSATED, FAILED
}

// Individual saga step result
enum StepResult {
    SUCCESS, FAILURE, RETRY_NEEDED
}

// Saga step definition
abstract class SagaStep {
    protected final String stepId;
    protected final String serviceName;
    protected final Map<String, Object> stepData;
    protected volatile StepResult lastResult;
    protected volatile String errorMessage;
    
    public SagaStep(String stepId, String serviceName) {
        this.stepId = stepId;
        this.serviceName = serviceName;
        this.stepData = new HashMap<>();
        this.lastResult = null;
    }
    
    // Execute the forward action
    public abstract CompletableFuture<StepResult> execute(Map<String, Object> sagaContext);
    
    // Execute the compensation action
    public abstract CompletableFuture<StepResult> compensate(Map<String, Object> sagaContext);
    
    public String getStepId() { return stepId; }
    public String getServiceName() { return serviceName; }
    public StepResult getLastResult() { return lastResult; }
    public String getErrorMessage() { return errorMessage; }
    
    protected void setResult(StepResult result, String error) {
        this.lastResult = result;
        this.errorMessage = error;
    }
}

// Payment processing step - Razorpay/Paytm integration
class PaymentProcessingStep extends SagaStep {
    private final PaymentService paymentService;
    
    public PaymentProcessingStep(PaymentService paymentService) {
        super("PAYMENT_PROCESSING", "PaymentService");
        this.paymentService = paymentService;
    }
    
    @Override
    public CompletableFuture<StepResult> execute(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String orderId = (String) sagaContext.get("orderId");
                Double amount = (Double) sagaContext.get("totalAmount");
                String customerId = (String) sagaContext.get("customerId");
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[PAYMENT] Processing payment for order %s: ₹%.2f", orderId, amount));
                
                String paymentId = paymentService.processPayment(customerId, amount, orderId);
                
                if (paymentId != null) {
                    sagaContext.put("paymentId", paymentId);
                    setResult(StepResult.SUCCESS, null);
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[PAYMENT] Payment successful: %s", paymentId));
                    return StepResult.SUCCESS;
                } else {
                    setResult(StepResult.FAILURE, "Payment processing failed");
                    return StepResult.FAILURE;
                }
                
            } catch (Exception e) {
                String error = "Payment processing error: " + e.getMessage();
                setResult(StepResult.FAILURE, error);
                Logger.getLogger(getClass().getName()).warning(error);
                return StepResult.FAILURE;
            }
        });
    }
    
    @Override
    public CompletableFuture<StepResult> compensate(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String paymentId = (String) sagaContext.get("paymentId");
                if (paymentId != null) {
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[PAYMENT] Refunding payment: %s", paymentId));
                    
                    boolean refunded = paymentService.refundPayment(paymentId);
                    if (refunded) {
                        Logger.getLogger(getClass().getName()).info(
                            String.format("[PAYMENT] Refund successful: %s", paymentId));
                        return StepResult.SUCCESS;
                    }
                }
                return StepResult.FAILURE;
                
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).warning("Payment compensation failed: " + e.getMessage());
                return StepResult.FAILURE;
            }
        });
    }
}

// Inventory reservation step
class InventoryReservationStep extends SagaStep {
    private final InventoryService inventoryService;
    
    public InventoryReservationStep(InventoryService inventoryService) {
        super("INVENTORY_RESERVATION", "InventoryService");
        this.inventoryService = inventoryService;
    }
    
    @Override
    public CompletableFuture<StepResult> execute(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String orderId = (String) sagaContext.get("orderId");
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> items = (List<Map<String, Object>>) sagaContext.get("orderItems");
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[INVENTORY] Reserving items for order %s", orderId));
                
                List<String> reservationIds = new ArrayList<>();
                
                for (Map<String, Object> item : items) {
                    String productId = (String) item.get("productId");
                    Integer quantity = (Integer) item.get("quantity");
                    
                    String reservationId = inventoryService.reserveInventory(productId, quantity, orderId);
                    
                    if (reservationId == null) {
                        // Compensation - release already reserved items
                        for (String prevReservation : reservationIds) {
                            inventoryService.releaseReservation(prevReservation);
                        }
                        
                        setResult(StepResult.FAILURE, "Insufficient inventory for product: " + productId);
                        return StepResult.FAILURE;
                    }
                    
                    reservationIds.add(reservationId);
                }
                
                sagaContext.put("reservationIds", reservationIds);
                setResult(StepResult.SUCCESS, null);
                Logger.getLogger(getClass().getName()).info(
                    String.format("[INVENTORY] Successfully reserved %d items", reservationIds.size()));
                
                return StepResult.SUCCESS;
                
            } catch (Exception e) {
                String error = "Inventory reservation error: " + e.getMessage();
                setResult(StepResult.FAILURE, error);
                Logger.getLogger(getClass().getName()).warning(error);
                return StepResult.FAILURE;
            }
        });
    }
    
    @Override
    public CompletableFuture<StepResult> compensate(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                @SuppressWarnings("unchecked")
                List<String> reservationIds = (List<String>) sagaContext.get("reservationIds");
                
                if (reservationIds != null) {
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[INVENTORY] Releasing %d reservations", reservationIds.size()));
                    
                    for (String reservationId : reservationIds) {
                        inventoryService.releaseReservation(reservationId);
                    }
                    
                    Logger.getLogger(getClass().getName()).info("[INVENTORY] All reservations released");
                }
                
                return StepResult.SUCCESS;
                
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).warning("Inventory compensation failed: " + e.getMessage());
                return StepResult.FAILURE;
            }
        });
    }
}

// Shipping arrangement step
class ShippingArrangementStep extends SagaStep {
    private final ShippingService shippingService;
    
    public ShippingArrangementStep(ShippingService shippingService) {
        super("SHIPPING_ARRANGEMENT", "ShippingService");
        this.shippingService = shippingService;
    }
    
    @Override
    public CompletableFuture<StepResult> execute(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String orderId = (String) sagaContext.get("orderId");
                @SuppressWarnings("unchecked")
                Map<String, String> shippingAddress = (Map<String, String>) sagaContext.get("shippingAddress");
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[SHIPPING] Arranging shipping for order %s", orderId));
                
                String trackingNumber = shippingService.arrangeShipping(orderId, shippingAddress);
                
                if (trackingNumber != null) {
                    sagaContext.put("trackingNumber", trackingNumber);
                    setResult(StepResult.SUCCESS, null);
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[SHIPPING] Shipping arranged: %s", trackingNumber));
                    return StepResult.SUCCESS;
                } else {
                    setResult(StepResult.FAILURE, "Shipping arrangement failed");
                    return StepResult.FAILURE;
                }
                
            } catch (Exception e) {
                String error = "Shipping arrangement error: " + e.getMessage();
                setResult(StepResult.FAILURE, error);
                Logger.getLogger(getClass().getName()).warning(error);
                return StepResult.FAILURE;
            }
        });
    }
    
    @Override
    public CompletableFuture<StepResult> compensate(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String trackingNumber = (String) sagaContext.get("trackingNumber");
                if (trackingNumber != null) {
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[SHIPPING] Cancelling shipment: %s", trackingNumber));
                    
                    boolean cancelled = shippingService.cancelShipment(trackingNumber);
                    if (cancelled) {
                        Logger.getLogger(getClass().getName()).info(
                            String.format("[SHIPPING] Shipment cancelled: %s", trackingNumber));
                        return StepResult.SUCCESS;
                    }
                }
                return StepResult.FAILURE;
                
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).warning("Shipping compensation failed: " + e.getMessage());
                return StepResult.FAILURE;
            }
        });
    }
}

// Order confirmation step
class OrderConfirmationStep extends SagaStep {
    private final OrderService orderService;
    
    public OrderConfirmationStep(OrderService orderService) {
        super("ORDER_CONFIRMATION", "OrderService");
        this.orderService = orderService;
    }
    
    @Override
    public CompletableFuture<StepResult> execute(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String orderId = (String) sagaContext.get("orderId");
                String paymentId = (String) sagaContext.get("paymentId");
                String trackingNumber = (String) sagaContext.get("trackingNumber");
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[ORDER] Confirming order %s", orderId));
                
                boolean confirmed = orderService.confirmOrder(orderId, paymentId, trackingNumber);
                
                if (confirmed) {
                    setResult(StepResult.SUCCESS, null);
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[ORDER] Order confirmed: %s", orderId));
                    return StepResult.SUCCESS;
                } else {
                    setResult(StepResult.FAILURE, "Order confirmation failed");
                    return StepResult.FAILURE;
                }
                
            } catch (Exception e) {
                String error = "Order confirmation error: " + e.getMessage();
                setResult(StepResult.FAILURE, error);
                Logger.getLogger(getClass().getName()).warning(error);
                return StepResult.FAILURE;
            }
        });
    }
    
    @Override
    public CompletableFuture<StepResult> compensate(Map<String, Object> sagaContext) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                String orderId = (String) sagaContext.get("orderId");
                
                Logger.getLogger(getClass().getName()).info(
                    String.format("[ORDER] Cancelling order: %s", orderId));
                
                boolean cancelled = orderService.cancelOrder(orderId);
                if (cancelled) {
                    Logger.getLogger(getClass().getName()).info(
                        String.format("[ORDER] Order cancelled: %s", orderId));
                    return StepResult.SUCCESS;
                }
                
                return StepResult.FAILURE;
                
            } catch (Exception e) {
                Logger.getLogger(getClass().getName()).warning("Order compensation failed: " + e.getMessage());
                return StepResult.FAILURE;
            }
        });
    }
}

// Saga definition and execution
class Saga {
    private final String sagaId;
    private final List<SagaStep> steps;
    private final Map<String, Object> context;
    private volatile SagaStatus status;
    private volatile int currentStepIndex;
    private final Instant startTime;
    private volatile Instant endTime;
    private final List<String> executionLog;
    
    public Saga(String sagaId) {
        this.sagaId = sagaId;
        this.steps = new ArrayList<>();
        this.context = new ConcurrentHashMap<>();
        this.status = SagaStatus.STARTED;
        this.currentStepIndex = 0;
        this.startTime = Instant.now();
        this.executionLog = new ArrayList<>();
    }
    
    public void addStep(SagaStep step) {
        steps.add(step);
    }
    
    public void setContext(String key, Object value) {
        context.put(key, value);
    }
    
    public CompletableFuture<SagaStatus> execute() {
        return CompletableFuture.supplyAsync(() -> {
            try {
                status = SagaStatus.IN_PROGRESS;
                addLog("Saga execution started");
                
                // Execute all steps in sequence
                for (currentStepIndex = 0; currentStepIndex < steps.size(); currentStepIndex++) {
                    SagaStep step = steps.get(currentStepIndex);
                    addLog("Executing step: " + step.getStepId());
                    
                    StepResult result = step.execute(context).get(30, TimeUnit.SECONDS);
                    
                    if (result != StepResult.SUCCESS) {
                        addLog("Step failed: " + step.getStepId() + " - " + step.getErrorMessage());
                        return compensate();
                    }
                    
                    addLog("Step completed: " + step.getStepId());
                }
                
                status = SagaStatus.COMPLETED;
                endTime = Instant.now();
                addLog("Saga completed successfully");
                
                return SagaStatus.COMPLETED;
                
            } catch (Exception e) {
                addLog("Saga execution error: " + e.getMessage());
                return compensate();
            }
        });
    }
    
    private SagaStatus compensate() {
        try {
            status = SagaStatus.COMPENSATING;
            addLog("Starting compensation");
            
            // Compensate in reverse order, starting from the last successful step
            for (int i = currentStepIndex - 1; i >= 0; i--) {
                SagaStep step = steps.get(i);
                addLog("Compensating step: " + step.getStepId());
                
                StepResult result = step.compensate(context).get(30, TimeUnit.SECONDS);
                
                if (result != StepResult.SUCCESS) {
                    addLog("Compensation failed for step: " + step.getStepId());
                    // Continue with other compensations
                }
                
                addLog("Step compensated: " + step.getStepId());
            }
            
            status = SagaStatus.COMPENSATED;
            endTime = Instant.now();
            addLog("Saga compensated");
            
            return SagaStatus.COMPENSATED;
            
        } catch (Exception e) {
            status = SagaStatus.FAILED;
            endTime = Instant.now();
            addLog("Compensation failed: " + e.getMessage());
            return SagaStatus.FAILED;
        }
    }
    
    private void addLog(String message) {
        String logEntry = String.format("[%s] %s", Instant.now(), message);
        executionLog.add(logEntry);
        Logger.getLogger(getClass().getName()).info(String.format("[SAGA-%s] %s", sagaId, message));
    }
    
    // Getters
    public String getSagaId() { return sagaId; }
    public SagaStatus getStatus() { return status; }
    public Map<String, Object> getContext() { return new HashMap<>(context); }
    public List<String> getExecutionLog() { return new ArrayList<>(executionLog); }
    public Instant getStartTime() { return startTime; }
    public Instant getEndTime() { return endTime; }
}

// Mock services for demonstration
class PaymentService {
    private final Random random = new Random();
    private final double failureRate;
    
    public PaymentService(double failureRate) {
        this.failureRate = failureRate;
    }
    
    public String processPayment(String customerId, double amount, String orderId) throws InterruptedException {
        Thread.sleep(random.nextInt(200) + 100); // Simulate processing time
        
        if (random.nextDouble() < failureRate) {
            return null; // Payment failed
        }
        
        return "PAY_" + System.currentTimeMillis() + "_" + orderId;
    }
    
    public boolean refundPayment(String paymentId) throws InterruptedException {
        Thread.sleep(random.nextInt(100) + 50);
        return random.nextDouble() < 0.95; // 95% success rate for refunds
    }
}

class InventoryService {
    private final Map<String, Integer> inventory = new ConcurrentHashMap<>();
    private final Random random = new Random();
    
    public InventoryService() {
        // Initialize inventory
        inventory.put("PROD_001", 100);
        inventory.put("PROD_002", 50);
        inventory.put("PROD_003", 75);
        inventory.put("PROD_004", 25);
        inventory.put("PROD_005", 200);
    }
    
    public String reserveInventory(String productId, int quantity, String orderId) throws InterruptedException {
        Thread.sleep(random.nextInt(100) + 50);
        
        Integer available = inventory.get(productId);
        if (available == null || available < quantity) {
            return null; // Insufficient inventory
        }
        
        inventory.put(productId, available - quantity);
        return "RES_" + System.currentTimeMillis() + "_" + productId;
    }
    
    public boolean releaseReservation(String reservationId) throws InterruptedException {
        Thread.sleep(random.nextInt(50) + 25);
        return true; // Always successful for demo
    }
}

class ShippingService {
    private final Random random = new Random();
    private final double failureRate;
    
    public ShippingService(double failureRate) {
        this.failureRate = failureRate;
    }
    
    public String arrangeShipping(String orderId, Map<String, String> address) throws InterruptedException {
        Thread.sleep(random.nextInt(150) + 100);
        
        if (random.nextDouble() < failureRate) {
            return null; // Shipping arrangement failed
        }
        
        return "SHIP_" + System.currentTimeMillis() + "_" + orderId;
    }
    
    public boolean cancelShipment(String trackingNumber) throws InterruptedException {
        Thread.sleep(random.nextInt(100) + 50);
        return true; // Always successful for demo
    }
}

class OrderService {
    private final Random random = new Random();
    
    public boolean confirmOrder(String orderId, String paymentId, String trackingNumber) throws InterruptedException {
        Thread.sleep(random.nextInt(100) + 50);
        return random.nextDouble() < 0.98; // 98% success rate
    }
    
    public boolean cancelOrder(String orderId) throws InterruptedException {
        Thread.sleep(random.nextInt(50) + 25);
        return true; // Always successful for demo
    }
}

// Main Saga orchestrator
public class SagaPatternImplementation {
    private static final Logger logger = Logger.getLogger(SagaPatternImplementation.class.getName());
    private static final AtomicLong sagaCounter = new AtomicLong(1);
    
    private final PaymentService paymentService;
    private final InventoryService inventoryService;
    private final ShippingService shippingService;
    private final OrderService orderService;
    
    public SagaPatternImplementation() {
        this.paymentService = new PaymentService(0.1); // 10% failure rate
        this.inventoryService = new InventoryService();
        this.shippingService = new ShippingService(0.05); // 5% failure rate
        this.orderService = new OrderService();
    }
    
    public CompletableFuture<Saga> processOrder(String customerId, List<Map<String, Object>> orderItems,
                                               Map<String, String> shippingAddress, double totalAmount) {
        
        String sagaId = "SAGA_" + sagaCounter.getAndIncrement();
        String orderId = "ORDER_" + System.currentTimeMillis();
        
        Saga saga = new Saga(sagaId);
        
        // Set saga context
        saga.setContext("sagaId", sagaId);
        saga.setContext("orderId", orderId);
        saga.setContext("customerId", customerId);
        saga.setContext("orderItems", orderItems);
        saga.setContext("shippingAddress", shippingAddress);
        saga.setContext("totalAmount", totalAmount);
        
        // Add saga steps in order
        saga.addStep(new PaymentProcessingStep(paymentService));
        saga.addStep(new InventoryReservationStep(inventoryService));
        saga.addStep(new ShippingArrangementStep(shippingService));
        saga.addStep(new OrderConfirmationStep(orderService));
        
        logger.info(String.format("Created saga %s for order %s (₹%.2f)", sagaId, orderId, totalAmount));
        
        return saga.execute().thenApply(status -> saga);
    }
    
    public static void main(String[] args) {
        System.out.println("=== Saga Pattern Implementation Demo ===");
        System.out.println("E-commerce order processing with compensation");
        
        SagaPatternImplementation sagaOrchestrator = new SagaPatternImplementation();
        
        try {
            // Successful order scenario
            System.out.println("\n=== Successful Order Scenario ===");
            
            List<Map<String, Object>> orderItems1 = Arrays.asList(
                Map.of("productId", "PROD_001", "quantity", 2, "price", 1500.0),
                Map.of("productId", "PROD_002", "quantity", 1, "price", 2500.0)
            );
            
            Map<String, String> address1 = Map.of(
                "street", "123 MG Road",
                "city", "Mumbai",
                "pincode", "400001"
            );
            
            CompletableFuture<Saga> order1Future = sagaOrchestrator.processOrder(
                "CUST_001", orderItems1, address1, 5500.0
            );
            
            Saga saga1 = order1Future.get(60, TimeUnit.SECONDS);
            
            System.out.println("Order 1 Status: " + saga1.getStatus());
            System.out.println("Order 1 Context: " + saga1.getContext());
            
            // Failed order scenario (insufficient inventory)
            System.out.println("\n=== Failed Order Scenario (Insufficient Inventory) ===");
            
            List<Map<String, Object>> orderItems2 = Arrays.asList(
                Map.of("productId", "PROD_004", "quantity", 50, "price", 1000.0) // More than available
            );
            
            Map<String, String> address2 = Map.of(
                "street", "456 Brigade Road",
                "city", "Bangalore", 
                "pincode", "560001"
            );
            
            CompletableFuture<Saga> order2Future = sagaOrchestrator.processOrder(
                "CUST_002", orderItems2, address2, 50000.0
            );
            
            Saga saga2 = order2Future.get(60, TimeUnit.SECONDS);
            
            System.out.println("Order 2 Status: " + saga2.getStatus());
            
            // Multiple concurrent orders
            System.out.println("\n=== Concurrent Orders Test ===");
            
            List<CompletableFuture<Saga>> concurrentOrders = new ArrayList<>();
            
            for (int i = 1; i <= 5; i++) {
                List<Map<String, Object>> items = Arrays.asList(
                    Map.of("productId", "PROD_00" + (i % 5 + 1), "quantity", 1, "price", 1000.0 + i * 100)
                );
                
                Map<String, String> address = Map.of(
                    "street", "Address " + i,
                    "city", "City " + i,
                    "pincode", "40000" + i
                );
                
                CompletableFuture<Saga> orderFuture = sagaOrchestrator.processOrder(
                    "CUST_00" + i, items, address, 1000.0 + i * 100
                );
                
                concurrentOrders.add(orderFuture);
            }
            
            // Wait for all concurrent orders
            List<Saga> completedSagas = new ArrayList<>();
            for (CompletableFuture<Saga> orderFuture : concurrentOrders) {
                completedSagas.add(orderFuture.get(60, TimeUnit.SECONDS));
            }
            
            // Analyze results
            System.out.println("\n=== Concurrent Orders Results ===");
            
            Map<SagaStatus, Long> statusCounts = completedSagas.stream()
                .collect(Collectors.groupingBy(Saga::getStatus, Collectors.counting()));
            
            for (Map.Entry<SagaStatus, Long> entry : statusCounts.entrySet()) {
                System.out.println(entry.getKey() + ": " + entry.getValue() + " orders");
            }
            
            // Show detailed execution log for one saga
            if (!completedSagas.isEmpty()) {
                Saga exampleSaga = completedSagas.get(0);
                System.out.println("\n=== Example Saga Execution Log ===");
                System.out.println("Saga ID: " + exampleSaga.getSagaId());
                System.out.println("Status: " + exampleSaga.getStatus());
                System.out.println("Duration: " + 
                    (exampleSaga.getEndTime() != null ? 
                     java.time.Duration.between(exampleSaga.getStartTime(), exampleSaga.getEndTime()).toMillis() + " ms" :
                     "Still running"));
                
                System.out.println("\nExecution Log:");
                List<String> log = exampleSaga.getExecutionLog();
                for (String logEntry : log) {
                    System.out.println("  " + logEntry);
                }
            }
            
            System.out.println("\n✅ Saga Pattern demo completed successfully!");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
}