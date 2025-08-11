package com.flipkart.saga.services;

import com.flipkart.saga.models.OrderRequest;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

/**
 * Order Service for Flipkart Order Processing
 * जैसे IRCTC में ticket booking validation
 */
@Service
public class OrderService {
    
    private static final Logger logger = LoggerFactory.getLogger(OrderService.class);
    private final Random random = new Random();
    
    /**
     * Validate order request
     * जैसे IRCTC में seat availability और passenger details check
     */
    public OrderValidationResult validateOrder(OrderRequest orderRequest) {
        logger.info("Validating order {} - Checking like IRCTC seat availability", 
                   orderRequest.getOrderId());
        
        OrderValidationResult result = new OrderValidationResult();
        result.setOrderId(orderRequest.getOrderId());
        result.setValidationTimestamp(LocalDateTime.now());
        
        try {
            // Simulate validation delay (database calls, external APIs)
            Thread.sleep(100 + random.nextInt(200)); // 100-300ms delay
            
            // Basic validation checks
            if (orderRequest.getOrderId() == null || orderRequest.getOrderId().trim().isEmpty()) {
                result.setValid(false);
                result.setErrorMessage("Order ID is required");
                return result;
            }
            
            if (orderRequest.getCustomerId() == null || orderRequest.getCustomerId().trim().isEmpty()) {
                result.setValid(false);
                result.setErrorMessage("Customer ID is required");
                return result;
            }
            
            if (orderRequest.getItems() == null || orderRequest.getItems().isEmpty()) {
                result.setValid(false);
                result.setErrorMessage("Order must contain at least one item");
                return result;
            }
            
            if (orderRequest.getTotalAmount() == null || 
                orderRequest.getTotalAmount().compareTo(BigDecimal.ZERO) <= 0) {
                result.setValid(false);
                result.setErrorMessage("Order total must be greater than zero");
                return result;
            }
            
            // Check for duplicate orders
            if (isDuplicateOrder(orderRequest.getOrderId())) {
                result.setValid(false);
                result.setErrorMessage("Duplicate order detected");
                return result;
            }
            
            // Validate customer eligibility
            CustomerEligibility eligibility = checkCustomerEligibility(orderRequest.getCustomerId());
            if (!eligibility.isEligible()) {
                result.setValid(false);
                result.setErrorMessage("Customer not eligible for order: " + eligibility.getReason());
                return result;
            }
            
            // Validate shipping address (Mumbai special handling)
            AddressValidation addressValidation = validateShippingAddress(orderRequest.getShippingAddress());
            if (!addressValidation.isValid()) {
                result.setValid(false);
                result.setErrorMessage("Invalid shipping address: " + addressValidation.getReason());
                return result;
            }
            
            // Business rule validations
            BusinessRuleValidation businessValidation = validateBusinessRules(orderRequest);
            if (!businessValidation.isValid()) {
                result.setValid(false);
                result.setErrorMessage("Business rule violation: " + businessValidation.getReason());
                return result;
            }
            
            // Simulate occasional failures (5% failure rate for demo)
            if (random.nextDouble() < 0.05) {
                result.setValid(false);
                result.setErrorMessage("System temporarily unavailable - Like Mumbai monsoon disruption");
                logger.warn("Simulated validation failure for order {}", orderRequest.getOrderId());
                return result;
            }
            
            // All validations passed
            result.setValid(true);
            result.setValidatedOrder(enhanceOrderWithValidationData(orderRequest));
            result.setValidationDetails(buildValidationDetails(orderRequest));
            
            logger.info("Order {} validated successfully", orderRequest.getOrderId());
            
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            result.setValid(false);
            result.setErrorMessage("Validation interrupted");
        } catch (Exception ex) {
            logger.error("Order validation failed for {}: {}", orderRequest.getOrderId(), ex.getMessage());
            result.setValid(false);
            result.setErrorMessage("Validation service error: " + ex.getMessage());
        }
        
        return result;
    }
    
    /**
     * Cancel order validation (compensation action)
     */
    public void cancelOrderValidation(String orderId) {
        logger.info("Cancelling order validation for {} - Rolling back like train ticket cancellation", 
                   orderId);
        
        // In real implementation, this would:
        // - Remove any temporary reservations
        // - Clear validation caches
        // - Update order status
        // - Log cancellation for audit
        
        try {
            Thread.sleep(50); // Simulate cleanup time
            logger.info("Order validation cancelled for {}", orderId);
        } catch (InterruptedException ex) {
            Thread.currentThread().interrupt();
            logger.error("Order validation cancellation interrupted for {}", orderId);
        }
    }
    
    /**
     * Check if order is duplicate
     */
    private boolean isDuplicateOrder(String orderId) {
        // In real implementation, check against database
        // For demo, assume orderId starting with "DUP_" are duplicates
        return orderId.startsWith("DUP_");
    }
    
    /**
     * Check customer eligibility
     */
    private CustomerEligibility checkCustomerEligibility(String customerId) {
        CustomerEligibility eligibility = new CustomerEligibility();
        
        // Simulate customer blacklist check
        if (customerId.startsWith("BLOCKED_")) {
            eligibility.setEligible(false);
            eligibility.setReason("Customer account blocked");
            return eligibility;
        }
        
        // Check for credit limit (for EMI customers)
        if (customerId.startsWith("EMI_")) {
            // Simulate credit check
            if (random.nextDouble() < 0.1) { // 10% chance of credit failure
                eligibility.setEligible(false);
                eligibility.setReason("Insufficient credit limit");
                return eligibility;
            }
        }
        
        eligibility.setEligible(true);
        return eligibility;
    }
    
    /**
     * Validate shipping address
     */
    private AddressValidation validateShippingAddress(ShippingAddress address) {
        AddressValidation validation = new AddressValidation();
        
        if (address == null) {
            validation.setValid(false);
            validation.setReason("Shipping address is required");
            return validation;
        }
        
        // Basic address field validation
        if (address.getAddressLine1() == null || address.getAddressLine1().trim().isEmpty()) {
            validation.setValid(false);
            validation.setReason("Address line 1 is required");
            return validation;
        }
        
        if (address.getCity() == null || address.getCity().trim().isEmpty()) {
            validation.setValid(false);
            validation.setReason("City is required");
            return validation;
        }
        
        if (address.getPincode() == null || !isValidPincode(address.getPincode())) {
            validation.setValid(false);
            validation.setReason("Valid pincode is required");
            return validation;
        }
        
        // Special validation for Mumbai addresses
        if (address.isMumbaiAddress()) {
            if (!isValidMumbaiPincode(address.getPincode())) {
                validation.setValid(false);
                validation.setReason("Invalid Mumbai pincode");
                return validation;
            }
        }
        
        validation.setValid(true);
        return validation;
    }
    
    /**
     * Validate business rules
     */
    private BusinessRuleValidation validateBusinessRules(OrderRequest orderRequest) {
        BusinessRuleValidation validation = new BusinessRuleValidation();
        
        // Check minimum order value
        BigDecimal minimumOrderValue = new BigDecimal("50.00"); // ₹50 minimum
        if (orderRequest.getTotalAmount().compareTo(minimumOrderValue) < 0) {
            validation.setValid(false);
            validation.setReason("Minimum order value is ₹50");
            return validation;
        }
        
        // Check maximum order value for COD
        if (orderRequest.getPaymentMethod().getCode().equals("COD")) {
            BigDecimal maxCodValue = new BigDecimal("50000.00"); // ₹50,000 max for COD
            if (orderRequest.getTotalAmount().compareTo(maxCodValue) > 0) {
                validation.setValid(false);
                validation.setReason("COD not available for orders above ₹50,000");
                return validation;
            }
        }
        
        // Check delivery constraints
        if (orderRequest.getExpectedDeliveryDate() != null) {
            LocalDateTime minDeliveryDate = LocalDateTime.now().plusDays(1);
            if (orderRequest.getExpectedDeliveryDate().isBefore(minDeliveryDate)) {
                validation.setValid(false);
                validation.setReason("Minimum delivery time is 24 hours");
                return validation;
            }
        }
        
        validation.setValid(true);
        return validation;
    }
    
    /**
     * Enhance order with validation data
     */
    private OrderRequest enhanceOrderWithValidationData(OrderRequest orderRequest) {
        // Add validation timestamp
        if (orderRequest.getMetadata() != null) {
            orderRequest.getMetadata().setValidationTimestamp(LocalDateTime.now());
        }
        
        // Calculate estimated delivery date if not provided
        if (orderRequest.getExpectedDeliveryDate() == null) {
            int deliveryDays = orderRequest.isExpressOrder() ? 1 : 3;
            if (orderRequest.getShippingAddress().isMumbaiAddress()) {
                deliveryDays = Math.max(1, deliveryDays - 1); // Mumbai gets faster delivery
            }
            orderRequest.setExpectedDeliveryDate(LocalDateTime.now().plusDays(deliveryDays));
        }
        
        return orderRequest;
    }
    
    /**
     * Build validation details
     */
    private Map<String, Object> buildValidationDetails(OrderRequest orderRequest) {
        Map<String, Object> details = new HashMap<>();
        details.put("validatedAt", LocalDateTime.now());
        details.put("validatedBy", "OrderService");
        details.put("customerTier", orderRequest.getCustomerTier());
        details.put("isExpressOrder", orderRequest.isExpressOrder());
        details.put("requiresSpecialHandling", orderRequest.requiresSpecialHandling());
        details.put("estimatedShippingCost", orderRequest.calculateShippingCost());
        details.put("isMumbaiDelivery", orderRequest.getShippingAddress().isMumbaiAddress());
        return details;
    }
    
    /**
     * Validate Indian pincode format
     */
    private boolean isValidPincode(String pincode) {
        return pincode != null && pincode.matches("\\d{6}");
    }
    
    /**
     * Validate Mumbai pincode ranges
     */
    private boolean isValidMumbaiPincode(String pincode) {
        if (!isValidPincode(pincode)) return false;
        
        int pin = Integer.parseInt(pincode);
        // Mumbai pincodes: 400001-400099
        return pin >= 400001 && pin <= 400099;
    }
    
    /**
     * Order validation result
     */
    public static class OrderValidationResult {
        private String orderId;
        private boolean valid;
        private String errorMessage;
        private OrderRequest validatedOrder;
        private Map<String, Object> validationDetails;
        private LocalDateTime validationTimestamp;
        
        // Getters and setters
        public String getOrderId() { return orderId; }
        public void setOrderId(String orderId) { this.orderId = orderId; }
        
        public boolean isValid() { return valid; }
        public void setValid(boolean valid) { this.valid = valid; }
        
        public String getErrorMessage() { return errorMessage; }
        public void setErrorMessage(String errorMessage) { this.errorMessage = errorMessage; }
        
        public OrderRequest getValidatedOrder() { return validatedOrder; }
        public void setValidatedOrder(OrderRequest validatedOrder) { this.validatedOrder = validatedOrder; }
        
        public Map<String, Object> getValidationDetails() { return validationDetails; }
        public void setValidationDetails(Map<String, Object> validationDetails) { 
            this.validationDetails = validationDetails; 
        }
        
        public LocalDateTime getValidationTimestamp() { return validationTimestamp; }
        public void setValidationTimestamp(LocalDateTime validationTimestamp) { 
            this.validationTimestamp = validationTimestamp; 
        }
    }
    
    /**
     * Customer eligibility check result
     */
    private static class CustomerEligibility {
        private boolean eligible;
        private String reason;
        
        public boolean isEligible() { return eligible; }
        public void setEligible(boolean eligible) { this.eligible = eligible; }
        
        public String getReason() { return reason; }
        public void setReason(String reason) { this.reason = reason; }
    }
    
    /**
     * Address validation result
     */
    private static class AddressValidation {
        private boolean valid;
        private String reason;
        
        public boolean isValid() { return valid; }
        public void setValid(boolean valid) { this.valid = valid; }
        
        public String getReason() { return reason; }
        public void setReason(String reason) { this.reason = reason; }
    }
    
    /**
     * Business rule validation result
     */
    private static class BusinessRuleValidation {
        private boolean valid;
        private String reason;
        
        public boolean isValid() { return valid; }
        public void setValid(boolean valid) { this.valid = valid; }
        
        public String getReason() { return reason; }
        public void setReason(String reason) { this.reason = reason; }
    }
}