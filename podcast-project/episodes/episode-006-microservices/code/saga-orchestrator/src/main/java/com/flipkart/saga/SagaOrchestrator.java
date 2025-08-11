package com.flipkart.saga;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Saga Pattern Orchestrator for Flipkart Order Processing
 * 
 * जैसे Mumbai local train में multiple stations का coordination होता है,
 * वैसे ही saga pattern में multiple services का coordination होता है
 * 
 * Example: Order placement process
 * 1. Validate Order -> 2. Reserve Inventory -> 3. Process Payment -> 4. Ship Order
 * अगर कोई step fail हो जाए तो सभी previous steps को rollback करना पड़ेगा
 */
@Service
public class SagaOrchestrator {
    
    private static final Logger logger = LoggerFactory.getLogger(SagaOrchestrator.class);
    
    private final Map<String, SagaExecution> activeSagas = new ConcurrentHashMap<>();
    private final ExecutorService executorService = Executors.newFixedThreadPool(20);
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private ShippingService shippingService;
    
    @Autowired
    private NotificationService notificationService;
    
    /**
     * Flipkart Order Saga Definition
     * जैसे train journey में stations की sequence होती है
     */
    public enum OrderSagaStep {
        VALIDATE_ORDER("validateOrder", "cancelOrderValidation"),
        RESERVE_INVENTORY("reserveInventory", "releaseInventoryReservation"),
        PROCESS_PAYMENT("processPayment", "refundPayment"),
        SHIP_ORDER("shipOrder", "cancelShipment"),
        SEND_CONFIRMATION("sendConfirmation", "sendCancellationNotice");
        
        private final String action;
        private final String compensationAction;
        
        OrderSagaStep(String action, String compensationAction) {
            this.action = action;
            this.compensationAction = compensationAction;
        }
        
        public String getAction() { return action; }
        public String getCompensationAction() { return compensationAction; }
    }
    
    /**
     * Saga Execution Context
     * सभी saga की state और data यहाँ store होता है
     */
    public static class SagaExecution {
        private String sagaId;
        private String orderId;
        private SagaStatus status;
        private List<SagaStepResult> completedSteps;
        private Map<String, Object> sagaData;
        private LocalDateTime startTime;
        private LocalDateTime endTime;
        private String errorMessage;
        
        public SagaExecution(String sagaId, String orderId) {
            this.sagaId = sagaId;
            this.orderId = orderId;
            this.status = SagaStatus.STARTED;
            this.completedSteps = new ArrayList<>();
            this.sagaData = new HashMap<>();
            this.startTime = LocalDateTime.now();
        }
        
        // Getters and setters
        public String getSagaId() { return sagaId; }
        public String getOrderId() { return orderId; }
        public SagaStatus getStatus() { return status; }
        public void setStatus(SagaStatus status) { this.status = status; }
        public List<SagaStepResult> getCompletedSteps() { return completedSteps; }
        public Map<String, Object> getSagaData() { return sagaData; }
        public LocalDateTime getStartTime() { return startTime; }
        public LocalDateTime getEndTime() { return endTime; }
        public void setEndTime(LocalDateTime endTime) { this.endTime = endTime; }
        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    }
    
    public enum SagaStatus {
        STARTED, IN_PROGRESS, COMPLETED, COMPENSATING, FAILED, CANCELLED
    }
    
    /**
     * Individual step execution result
     */
    public static class SagaStepResult {
        private OrderSagaStep step;
        private boolean successful;
        private Map<String, Object> data;
        private LocalDateTime timestamp;
        private String errorMessage;
        
        public SagaStepResult(OrderSagaStep step, boolean successful) {
            this.step = step;
            this.successful = successful;
            this.data = new HashMap<>();
            this.timestamp = LocalDateTime.now();
        }
        
        // Getters and setters
        public OrderSagaStep getStep() { return step; }
        public boolean isSuccessful() { return successful; }
        public Map<String, Object> getData() { return data; }
        public LocalDateTime getTimestamp() { return timestamp; }
        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
    }
    
    /**
     * Start Order Processing Saga
     * जैसे Mumbai local में journey start करना
     */
    public CompletableFuture<SagaExecution> startOrderSaga(OrderRequest orderRequest) {
        String sagaId = "SAGA_" + UUID.randomUUID().toString();
        String orderId = orderRequest.getOrderId();
        
        logger.info("Starting order saga {} for order {} - Like booking Tatkal ticket in IRCTC!", 
                   sagaId, orderId);
        
        SagaExecution saga = new SagaExecution(sagaId, orderId);
        saga.getSagaData().put("orderRequest", orderRequest);
        saga.getSagaData().put("customerId", orderRequest.getCustomerId());
        saga.getSagaData().put("totalAmount", orderRequest.getTotalAmount());
        
        activeSagas.put(sagaId, saga);
        
        return CompletableFuture
            .supplyAsync(() -> executeSaga(saga), executorService)
            .exceptionally(ex -> {
                logger.error("Saga execution failed for {}: {}", sagaId, ex.getMessage());
                saga.setStatus(SagaStatus.FAILED);
                saga.setErrorMessage(ex.getMessage());
                saga.setEndTime(LocalDateTime.now());
                return saga;
            });
    }
    
    /**
     * Execute Saga Steps Sequentially
     * हर step successful होने पर next step execute करते हैं
     */
    private SagaExecution executeSaga(SagaExecution saga) {
        logger.info("Executing saga {} - Starting Flipkart order journey!", saga.getSagaId());
        
        saga.setStatus(SagaStatus.IN_PROGRESS);
        
        // Execute all saga steps in sequence
        OrderSagaStep[] steps = OrderSagaStep.values();
        
        for (OrderSagaStep step : steps) {
            try {
                logger.info("Executing step {} for saga {}", step.name(), saga.getSagaId());
                
                SagaStepResult result = executeStep(saga, step);
                saga.getCompletedSteps().add(result);
                
                if (!result.isSuccessful()) {
                    logger.error("Step {} failed for saga {}: {}", 
                               step.name(), saga.getSagaId(), result.getErrorMessage());
                    
                    // Start compensation - जैसे train cancel होने पर refund process
                    compensateSaga(saga);
                    return saga;
                }
                
                logger.info("Step {} completed successfully for saga {}", 
                           step.name(), saga.getSagaId());
                
            } catch (Exception ex) {
                logger.error("Unexpected error in step {} for saga {}: {}", 
                           step.name(), saga.getSagaId(), ex.getMessage());
                
                SagaStepResult errorResult = new SagaStepResult(step, false);
                errorResult.setErrorMessage(ex.getMessage());
                saga.getCompletedSteps().add(errorResult);
                
                compensateSaga(saga);
                return saga;
            }
        }
        
        // All steps completed successfully
        saga.setStatus(SagaStatus.COMPLETED);
        saga.setEndTime(LocalDateTime.now());
        
        logger.info("Saga {} completed successfully - Order processed like efficient Mumbai Dabbawalas!", 
                   saga.getSagaId());
        
        return saga;
    }
    
    /**
     * Execute individual saga step
     */
    private SagaStepResult executeStep(SagaExecution saga, OrderSagaStep step) {
        OrderRequest orderRequest = (OrderRequest) saga.getSagaData().get("orderRequest");
        
        switch (step) {
            case VALIDATE_ORDER:
                return validateOrder(saga, orderRequest);
                
            case RESERVE_INVENTORY:
                return reserveInventory(saga, orderRequest);
                
            case PROCESS_PAYMENT:
                return processPayment(saga, orderRequest);
                
            case SHIP_ORDER:
                return shipOrder(saga, orderRequest);
                
            case SEND_CONFIRMATION:
                return sendConfirmation(saga, orderRequest);
                
            default:
                throw new IllegalArgumentException("Unknown saga step: " + step);
        }
    }
    
    /**
     * Step 1: Validate Order
     * जैसे IRCTC में seat availability check करना
     */
    private SagaStepResult validateOrder(SagaExecution saga, OrderRequest orderRequest) {
        try {
            logger.info("Validating order {} - Checking like IRCTC seat availability", 
                       orderRequest.getOrderId());
            
            OrderValidationResult validation = orderService.validateOrder(orderRequest);
            
            SagaStepResult result = new SagaStepResult(OrderSagaStep.VALIDATE_ORDER, validation.isValid());
            result.getData().put("validationResult", validation);
            
            if (!validation.isValid()) {
                result.setErrorMessage("Order validation failed: " + validation.getErrorMessage());
                logger.warn("Order validation failed: {}", validation.getErrorMessage());
            } else {
                saga.getSagaData().put("validatedOrder", validation.getValidatedOrder());
                logger.info("Order validation successful");
            }
            
            return result;
            
        } catch (Exception ex) {
            logger.error("Order validation error: {}", ex.getMessage());
            SagaStepResult result = new SagaStepResult(OrderSagaStep.VALIDATE_ORDER, false);
            result.setErrorMessage("Validation service error: " + ex.getMessage());
            return result;
        }
    }
    
    /**
     * Step 2: Reserve Inventory
     * जैसे concert tickets book करना - limited quantity
     */
    private SagaStepResult reserveInventory(SagaExecution saga, OrderRequest orderRequest) {
        try {
            logger.info("Reserving inventory for order {} - Like booking last few concert tickets", 
                       orderRequest.getOrderId());
            
            InventoryReservationResult reservation = inventoryService.reserveItems(orderRequest.getItems());
            
            SagaStepResult result = new SagaStepResult(OrderSagaStep.RESERVE_INVENTORY, reservation.isSuccessful());
            result.getData().put("reservationResult", reservation);
            
            if (!reservation.isSuccessful()) {
                result.setErrorMessage("Inventory reservation failed: " + reservation.getErrorMessage());
                logger.warn("Inventory reservation failed: {}", reservation.getErrorMessage());
            } else {
                saga.getSagaData().put("reservationId", reservation.getReservationId());
                saga.getSagaData().put("reservedItems", reservation.getReservedItems());
                logger.info("Inventory reserved successfully with ID: {}", reservation.getReservationId());
            }
            
            return result;
            
        } catch (Exception ex) {
            logger.error("Inventory reservation error: {}", ex.getMessage());
            SagaStepResult result = new SagaStepResult(OrderSagaStep.RESERVE_INVENTORY, false);
            result.setErrorMessage("Inventory service error: " + ex.getMessage());
            return result;
        }
    }
    
    /**
     * Step 3: Process Payment
     * जैसे UPI payment करना - critical step
     */
    private SagaStepResult processPayment(SagaExecution saga, OrderRequest orderRequest) {
        try {
            logger.info("Processing payment for order {} - Like UPI payment through PhonePe", 
                       orderRequest.getOrderId());
            
            PaymentRequest paymentRequest = new PaymentRequest(
                orderRequest.getCustomerId(),
                orderRequest.getTotalAmount(),
                orderRequest.getPaymentMethod()
            );
            
            PaymentResult payment = paymentService.processPayment(paymentRequest);
            
            SagaStepResult result = new SagaStepResult(OrderSagaStep.PROCESS_PAYMENT, payment.isSuccessful());
            result.getData().put("paymentResult", payment);
            
            if (!payment.isSuccessful()) {
                result.setErrorMessage("Payment failed: " + payment.getErrorMessage());
                logger.warn("Payment failed: {}", payment.getErrorMessage());
            } else {
                saga.getSagaData().put("transactionId", payment.getTransactionId());
                saga.getSagaData().put("paymentMethod", payment.getPaymentMethod());
                logger.info("Payment processed successfully with transaction ID: {}", payment.getTransactionId());
            }
            
            return result;
            
        } catch (Exception ex) {
            logger.error("Payment processing error: {}", ex.getMessage());
            SagaStepResult result = new SagaStepResult(OrderSagaStep.PROCESS_PAYMENT, false);
            result.setErrorMessage("Payment service error: " + ex.getMessage());
            return result;
        }
    }
    
    /**
     * Step 4: Ship Order
     * जैसे Mumbai Dabbawalas का delivery system
     */
    private SagaStepResult shipOrder(SagaExecution saga, OrderRequest orderRequest) {
        try {
            logger.info("Shipping order {} - Dispatching like Mumbai Dabbawalas precision delivery", 
                       orderRequest.getOrderId());
            
            ShippingRequest shippingRequest = new ShippingRequest(
                orderRequest.getOrderId(),
                orderRequest.getShippingAddress(),
                (List<OrderItem>) saga.getSagaData().get("reservedItems")
            );
            
            ShippingResult shipping = shippingService.shipOrder(shippingRequest);
            
            SagaStepResult result = new SagaStepResult(OrderSagaStep.SHIP_ORDER, shipping.isSuccessful());
            result.getData().put("shippingResult", shipping);
            
            if (!shipping.isSuccessful()) {
                result.setErrorMessage("Shipping failed: " + shipping.getErrorMessage());
                logger.warn("Shipping failed: {}", shipping.getErrorMessage());
            } else {
                saga.getSagaData().put("trackingId", shipping.getTrackingId());
                saga.getSagaData().put("estimatedDelivery", shipping.getEstimatedDelivery());
                logger.info("Order shipped successfully with tracking ID: {}", shipping.getTrackingId());
            }
            
            return result;
            
        } catch (Exception ex) {
            logger.error("Shipping error: {}", ex.getMessage());
            SagaStepResult result = new SagaStepResult(OrderSagaStep.SHIP_ORDER, false);
            result.setErrorMessage("Shipping service error: " + ex.getMessage());
            return result;
        }
    }
    
    /**
     * Step 5: Send Confirmation
     * जैसे IRCTC का booking confirmation SMS
     */
    private SagaStepResult sendConfirmation(SagaExecution saga, OrderRequest orderRequest) {
        try {
            logger.info("Sending confirmation for order {} - Like IRCTC booking confirmation SMS", 
                       orderRequest.getOrderId());
            
            NotificationRequest notificationRequest = new NotificationRequest(
                orderRequest.getCustomerId(),
                "ORDER_CONFIRMATION",
                buildConfirmationMessage(saga, orderRequest)
            );
            
            NotificationResult notification = notificationService.sendNotification(notificationRequest);
            
            SagaStepResult result = new SagaStepResult(OrderSagaStep.SEND_CONFIRMATION, notification.isSuccessful());
            result.getData().put("notificationResult", notification);
            
            if (!notification.isSuccessful()) {
                // यह step fail हो तो भी saga को successful माना जाएगा
                // क्योंकि order process हो गया है, notification secondary है
                logger.warn("Notification failed but order completed: {}", notification.getErrorMessage());
                result = new SagaStepResult(OrderSagaStep.SEND_CONFIRMATION, true);
                result.getData().put("warning", "Notification failed but order processed");
            } else {
                logger.info("Order confirmation sent successfully");
            }
            
            return result;
            
        } catch (Exception ex) {
            logger.error("Notification error: {}", ex.getMessage());
            // Notification failure doesn't fail the entire saga
            SagaStepResult result = new SagaStepResult(OrderSagaStep.SEND_CONFIRMATION, true);
            result.getData().put("warning", "Notification service error: " + ex.getMessage());
            return result;
        }
    }
    
    /**
     * Compensate Saga - Rollback completed steps
     * जैसे train cancel होने पर सभी bookings को cancel करना
     */
    private void compensateSaga(SagaExecution saga) {
        logger.warn("Starting compensation for saga {} - Rolling back like train cancellation refunds", 
                   saga.getSagaId());
        
        saga.setStatus(SagaStatus.COMPENSATING);
        
        // Compensate in reverse order
        List<SagaStepResult> completedSteps = new ArrayList<>(saga.getCompletedSteps());
        Collections.reverse(completedSteps);
        
        for (SagaStepResult stepResult : completedSteps) {
            if (stepResult.isSuccessful()) {
                try {
                    compensateStep(saga, stepResult.getStep());
                    logger.info("Compensated step {} for saga {}", 
                               stepResult.getStep().name(), saga.getSagaId());
                } catch (Exception ex) {
                    logger.error("Compensation failed for step {} in saga {}: {}", 
                               stepResult.getStep().name(), saga.getSagaId(), ex.getMessage());
                    // Continue with other compensations even if one fails
                }
            }
        }
        
        saga.setStatus(SagaStatus.CANCELLED);
        saga.setEndTime(LocalDateTime.now());
        
        logger.info("Saga {} compensation completed - All changes rolled back like efficient refund system", 
                   saga.getSagaId());
    }
    
    /**
     * Compensate individual step
     */
    private void compensateStep(SagaExecution saga, OrderSagaStep step) {
        OrderRequest orderRequest = (OrderRequest) saga.getSagaData().get("orderRequest");
        
        switch (step) {
            case VALIDATE_ORDER:
                orderService.cancelOrderValidation(orderRequest.getOrderId());
                break;
                
            case RESERVE_INVENTORY:
                String reservationId = (String) saga.getSagaData().get("reservationId");
                if (reservationId != null) {
                    inventoryService.releaseReservation(reservationId);
                }
                break;
                
            case PROCESS_PAYMENT:
                String transactionId = (String) saga.getSagaData().get("transactionId");
                if (transactionId != null) {
                    paymentService.refundPayment(transactionId);
                }
                break;
                
            case SHIP_ORDER:
                String trackingId = (String) saga.getSagaData().get("trackingId");
                if (trackingId != null) {
                    shippingService.cancelShipment(trackingId);
                }
                break;
                
            case SEND_CONFIRMATION:
                // Send cancellation notice instead
                NotificationRequest cancelNotification = new NotificationRequest(
                    orderRequest.getCustomerId(),
                    "ORDER_CANCELLATION",
                    buildCancellationMessage(saga, orderRequest)
                );
                notificationService.sendNotification(cancelNotification);
                break;
        }
    }
    
    /**
     * Get saga status
     */
    public SagaExecution getSagaStatus(String sagaId) {
        return activeSagas.get(sagaId);
    }
    
    /**
     * List all active sagas
     */
    public List<SagaExecution> getActiveSagas() {
        return new ArrayList<>(activeSagas.values());
    }
    
    /**
     * Cleanup completed sagas (should be called periodically)
     */
    public void cleanupCompletedSagas() {
        LocalDateTime cutoff = LocalDateTime.now().minusHours(24);
        
        activeSagas.entrySet().removeIf(entry -> {
            SagaExecution saga = entry.getValue();
            return (saga.getStatus() == SagaStatus.COMPLETED || saga.getStatus() == SagaStatus.CANCELLED)
                   && saga.getEndTime() != null && saga.getEndTime().isBefore(cutoff);
        });
    }
    
    /**
     * Build confirmation message
     */
    private String buildConfirmationMessage(SagaExecution saga, OrderRequest orderRequest) {
        return String.format(
            "आपका Flipkart order %s successfully place हो गया है! " +
            "Tracking ID: %s, Estimated delivery: %s. " +
            "Mumbai की तरह efficient delivery guaranteed! 🚚",
            orderRequest.getOrderId(),
            saga.getSagaData().get("trackingId"),
            saga.getSagaData().get("estimatedDelivery")
        );
    }
    
    /**
     * Build cancellation message
     */
    private String buildCancellationMessage(SagaExecution saga, OrderRequest orderRequest) {
        return String.format(
            "Sorry, आपका order %s cancel करना पड़ा। " +
            "Refund 2-3 business days में आपके account में credit हो जाएगा। " +
            "Mumbai monsoon की तरह temporary setback है!",
            orderRequest.getOrderId()
        );
    }
}