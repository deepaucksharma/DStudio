package com.flipkart.saga.models;

import com.fasterxml.jackson.annotation.JsonProperty;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * Flipkart Order Request Model
 * जैसे Mumbai local train में ticket booking form
 */
public class OrderRequest {
    
    @NotNull
    @JsonProperty("orderId")
    private String orderId;
    
    @NotNull
    @JsonProperty("customerId")
    private String customerId;
    
    @NotNull
    @JsonProperty("items")
    private List<OrderItem> items;
    
    @NotNull
    @Positive
    @JsonProperty("totalAmount")
    private BigDecimal totalAmount;
    
    @NotNull
    @JsonProperty("paymentMethod")
    private PaymentMethod paymentMethod;
    
    @NotNull
    @JsonProperty("shippingAddress")
    private ShippingAddress shippingAddress;
    
    @JsonProperty("customerTier")
    private CustomerTier customerTier = CustomerTier.REGULAR;
    
    @JsonProperty("priority")
    private OrderPriority priority = OrderPriority.NORMAL;
    
    @JsonProperty("expectedDeliveryDate")
    private LocalDateTime expectedDeliveryDate;
    
    @JsonProperty("orderSource")
    private String orderSource = "MOBILE_APP";
    
    @JsonProperty("metadata")
    private OrderMetadata metadata;
    
    // Constructors
    public OrderRequest() {}
    
    public OrderRequest(String orderId, String customerId, List<OrderItem> items, 
                       BigDecimal totalAmount, PaymentMethod paymentMethod, 
                       ShippingAddress shippingAddress) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.items = items;
        this.totalAmount = totalAmount;
        this.paymentMethod = paymentMethod;
        this.shippingAddress = shippingAddress;
        this.metadata = new OrderMetadata();
    }
    
    // Getters and setters
    public String getOrderId() { return orderId; }
    public void setOrderId(String orderId) { this.orderId = orderId; }
    
    public String getCustomerId() { return customerId; }
    public void setCustomerId(String customerId) { this.customerId = customerId; }
    
    public List<OrderItem> getItems() { return items; }
    public void setItems(List<OrderItem> items) { this.items = items; }
    
    public BigDecimal getTotalAmount() { return totalAmount; }
    public void setTotalAmount(BigDecimal totalAmount) { this.totalAmount = totalAmount; }
    
    public PaymentMethod getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(PaymentMethod paymentMethod) { this.paymentMethod = paymentMethod; }
    
    public ShippingAddress getShippingAddress() { return shippingAddress; }
    public void setShippingAddress(ShippingAddress shippingAddress) { this.shippingAddress = shippingAddress; }
    
    public CustomerTier getCustomerTier() { return customerTier; }
    public void setCustomerTier(CustomerTier customerTier) { this.customerTier = customerTier; }
    
    public OrderPriority getPriority() { return priority; }
    public void setPriority(OrderPriority priority) { this.priority = priority; }
    
    public LocalDateTime getExpectedDeliveryDate() { return expectedDeliveryDate; }
    public void setExpectedDeliveryDate(LocalDateTime expectedDeliveryDate) { 
        this.expectedDeliveryDate = expectedDeliveryDate; 
    }
    
    public String getOrderSource() { return orderSource; }
    public void setOrderSource(String orderSource) { this.orderSource = orderSource; }
    
    public OrderMetadata getMetadata() { return metadata; }
    public void setMetadata(OrderMetadata metadata) { this.metadata = metadata; }
    
    // Business methods
    public boolean isExpressOrder() {
        return priority == OrderPriority.EXPRESS || 
               customerTier == CustomerTier.PLUS || 
               customerTier == CustomerTier.PREMIUM;
    }
    
    public boolean requiresSpecialHandling() {
        return items.stream().anyMatch(item -> 
            item.getCategory().equals("ELECTRONICS") || 
            item.getCategory().equals("FRAGILE"));
    }
    
    public BigDecimal calculateShippingCost() {
        // Mumbai delivery cost calculation
        BigDecimal baseCost = new BigDecimal("40.00"); // ₹40 base shipping
        
        if (isExpressOrder()) {
            baseCost = baseCost.multiply(new BigDecimal("1.5")); // 1.5x for express
        }
        
        if (requiresSpecialHandling()) {
            baseCost = baseCost.multiply(new BigDecimal("1.2")); // 1.2x for fragile items
        }
        
        // Free shipping for orders above ₹500
        if (totalAmount.compareTo(new BigDecimal("500.00")) >= 0) {
            return BigDecimal.ZERO;
        }
        
        return baseCost;
    }
    
    @Override
    public String toString() {
        return String.format("OrderRequest{orderId='%s', customerId='%s', amount=%s, items=%d}", 
                           orderId, customerId, totalAmount, items.size());
    }
}

/**
 * Individual item in the order
 */
class OrderItem {
    private String productId;
    private String productName;
    private String category;
    private int quantity;
    private BigDecimal unitPrice;
    private BigDecimal totalPrice;
    private String sellerId;
    private boolean isInStock;
    
    public OrderItem() {}
    
    public OrderItem(String productId, String productName, String category, 
                    int quantity, BigDecimal unitPrice, String sellerId) {
        this.productId = productId;
        this.productName = productName;
        this.category = category;
        this.quantity = quantity;
        this.unitPrice = unitPrice;
        this.totalPrice = unitPrice.multiply(new BigDecimal(quantity));
        this.sellerId = sellerId;
        this.isInStock = true; // Default assumption
    }
    
    // Getters and setters
    public String getProductId() { return productId; }
    public void setProductId(String productId) { this.productId = productId; }
    
    public String getProductName() { return productName; }
    public void setProductName(String productName) { this.productName = productName; }
    
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    
    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { 
        this.quantity = quantity;
        if (unitPrice != null) {
            this.totalPrice = unitPrice.multiply(new BigDecimal(quantity));
        }
    }
    
    public BigDecimal getUnitPrice() { return unitPrice; }
    public void setUnitPrice(BigDecimal unitPrice) { 
        this.unitPrice = unitPrice;
        if (quantity > 0) {
            this.totalPrice = unitPrice.multiply(new BigDecimal(quantity));
        }
    }
    
    public BigDecimal getTotalPrice() { return totalPrice; }
    
    public String getSellerId() { return sellerId; }
    public void setSellerId(String sellerId) { this.sellerId = sellerId; }
    
    public boolean isInStock() { return isInStock; }
    public void setInStock(boolean inStock) { this.isInStock = inStock; }
}

/**
 * Payment method enum
 */
enum PaymentMethod {
    UPI("UPI", "PhonePe/GooglePay/Paytm"),
    CREDIT_CARD("CREDIT_CARD", "Credit Card"),
    DEBIT_CARD("DEBIT_CARD", "Debit Card"), 
    NET_BANKING("NET_BANKING", "Net Banking"),
    COD("COD", "Cash on Delivery"),
    EMI("EMI", "Easy Monthly Installments"),
    WALLET("WALLET", "Flipkart Wallet");
    
    private final String code;
    private final String description;
    
    PaymentMethod(String code, String description) {
        this.code = code;
        this.description = description;
    }
    
    public String getCode() { return code; }
    public String getDescription() { return description; }
}

/**
 * Customer tier for special handling
 */
enum CustomerTier {
    REGULAR("REGULAR", 0),
    PLUS("PLUS", 1), 
    PREMIUM("PREMIUM", 2);
    
    private final String name;
    private final int priority;
    
    CustomerTier(String name, int priority) {
        this.name = name;
        this.priority = priority;
    }
    
    public String getName() { return name; }
    public int getPriority() { return priority; }
}

/**
 * Order priority levels
 */
enum OrderPriority {
    LOW(1),
    NORMAL(2),
    HIGH(3),
    EXPRESS(4),
    URGENT(5);
    
    private final int level;
    
    OrderPriority(int level) {
        this.level = level;
    }
    
    public int getLevel() { return level; }
}

/**
 * Shipping address
 */
class ShippingAddress {
    private String recipientName;
    private String addressLine1;
    private String addressLine2;
    private String city;
    private String state;
    private String pincode;
    private String country = "India";
    private String phoneNumber;
    private String landmark;
    private AddressType addressType = AddressType.HOME;
    
    public ShippingAddress() {}
    
    public ShippingAddress(String recipientName, String addressLine1, String city, 
                          String state, String pincode, String phoneNumber) {
        this.recipientName = recipientName;
        this.addressLine1 = addressLine1;
        this.city = city;
        this.state = state;
        this.pincode = pincode;
        this.phoneNumber = phoneNumber;
    }
    
    // Getters and setters
    public String getRecipientName() { return recipientName; }
    public void setRecipientName(String recipientName) { this.recipientName = recipientName; }
    
    public String getAddressLine1() { return addressLine1; }
    public void setAddressLine1(String addressLine1) { this.addressLine1 = addressLine1; }
    
    public String getAddressLine2() { return addressLine2; }
    public void setAddressLine2(String addressLine2) { this.addressLine2 = addressLine2; }
    
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    
    public String getPincode() { return pincode; }
    public void setPincode(String pincode) { this.pincode = pincode; }
    
    public String getCountry() { return country; }
    public void setCountry(String country) { this.country = country; }
    
    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }
    
    public String getLandmark() { return landmark; }
    public void setLandmark(String landmark) { this.landmark = landmark; }
    
    public AddressType getAddressType() { return addressType; }
    public void setAddressType(AddressType addressType) { this.addressType = addressType; }
    
    public boolean isMumbaiAddress() {
        return "Mumbai".equalsIgnoreCase(city) || "Mumbai".equalsIgnoreCase(state);
    }
    
    public String getFormattedAddress() {
        StringBuilder sb = new StringBuilder();
        sb.append(addressLine1);
        if (addressLine2 != null && !addressLine2.trim().isEmpty()) {
            sb.append(", ").append(addressLine2);
        }
        if (landmark != null && !landmark.trim().isEmpty()) {
            sb.append(", ").append(landmark);
        }
        sb.append(", ").append(city)
          .append(", ").append(state)
          .append(" - ").append(pincode);
        return sb.toString();
    }
}

enum AddressType {
    HOME, OFFICE, OTHER
}

/**
 * Order metadata for tracking additional information
 */
class OrderMetadata {
    private String ipAddress;
    private String userAgent;
    private String referrer;
    private String campaignId;
    private LocalDateTime createdAt;
    private String sessionId;
    
    public OrderMetadata() {
        this.createdAt = LocalDateTime.now();
    }
    
    // Getters and setters
    public String getIpAddress() { return ipAddress; }
    public void setIpAddress(String ipAddress) { this.ipAddress = ipAddress; }
    
    public String getUserAgent() { return userAgent; }
    public void setUserAgent(String userAgent) { this.userAgent = userAgent; }
    
    public String getReferrer() { return referrer; }
    public void setReferrer(String referrer) { this.referrer = referrer; }
    
    public String getCampaignId() { return campaignId; }
    public void setCampaignId(String campaignId) { this.campaignId = campaignId; }
    
    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    public String getSessionId() { return sessionId; }
    public void setSessionId(String sessionId) { this.sessionId = sessionId; }
}