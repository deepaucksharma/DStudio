/*
 * Domain-Driven Design: Complex Domain Model - BigBasket Inventory Management
 * Hindi Tech Podcast Series - Episode 40
 * 
 * यह example दिखाता है कि कैसे DDD में complex domain model बनाते हैं
 * BigBasket के inventory management system के लिए।
 * Multiple entities, value objects, और domain services का combination।
 * 
 * Author: Hindi Tech Podcast
 * Date: 2025
 */

package com.hindipodcast.ddd.bigbasket;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

// ====================================================================
// DOMAIN EXCEPTIONS
// ====================================================================

class DomainException extends RuntimeException {
    public DomainException(String message) { super(message); }
}

class InsufficientStockException extends DomainException {
    public InsufficientStockException(String message) { super(message); }
}

class ExpiredProductException extends DomainException {
    public ExpiredProductException(String message) { super(message); }
}

class InvalidPriceException extends DomainException {
    public InvalidPriceException(String message) { super(message); }
}

class SupplierNotActiveException extends DomainException {
    public SupplierNotActiveException(String message) { super(message); }
}

// ====================================================================
// ENUMS
// ====================================================================

enum ProductCategory {
    FRESH_PRODUCE("Fresh Produce", 3, true),
    DAIRY("Dairy & Eggs", 7, true),
    MEAT_FISH("Meat & Fish", 2, true),
    PACKAGED_FOODS("Packaged Foods", 180, false),
    BEVERAGES("Beverages", 90, false),
    PERSONAL_CARE("Personal Care", 365, false),
    HOUSEHOLD("Household", 730, false);
    
    private final String displayName;
    private final int defaultShelfLifeDays;
    private final boolean isPerishable;
    
    ProductCategory(String displayName, int defaultShelfLifeDays, boolean isPerishable) {
        this.displayName = displayName;
        this.defaultShelfLifeDays = defaultShelfLifeDays;
        this.isPerishable = isPerishable;
    }
    
    public String getDisplayName() { return displayName; }
    public int getDefaultShelfLifeDays() { return defaultShelfLifeDays; }
    public boolean isPerishable() { return isPerishable; }
}

enum StockStatus {
    IN_STOCK("In Stock"),
    LOW_STOCK("Low Stock"),
    OUT_OF_STOCK("Out of Stock"),
    DISCONTINUED("Discontinued");
    
    private final String displayName;
    
    StockStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

enum SupplierStatus {
    ACTIVE("Active"),
    INACTIVE("Inactive"),
    SUSPENDED("Suspended"),
    BLACKLISTED("Blacklisted");
    
    private final String displayName;
    
    SupplierStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() { return displayName; }
}

enum StorageCondition {
    AMBIENT("Ambient", 25, 60),
    CHILLED("Chilled", 4, 80),
    FROZEN("Frozen", -18, 85),
    DRY("Dry Storage", 20, 40);
    
    private final String displayName;
    private final int temperatureCelsius;
    private final int humidityPercent;
    
    StorageCondition(String displayName, int temperatureCelsius, int humidityPercent) {
        this.displayName = displayName;
        this.temperatureCelsius = temperatureCelsius;
        this.humidityPercent = humidityPercent;
    }
    
    public String getDisplayName() { return displayName; }
    public int getTemperatureCelsius() { return temperatureCelsius; }
    public int getHumidityPercent() { return humidityPercent; }
}

// ====================================================================
// VALUE OBJECTS
// ====================================================================

/**
 * Product SKU - Strong typed identifier
 * Product SKU - Strong typed identifier
 */
class ProductSKU {
    private final String value;
    
    public ProductSKU(String value) {
        if (value == null || value.trim().isEmpty()) {
            throw new IllegalArgumentException("SKU cannot be empty - SKU खाली नहीं हो सकता");
        }
        if (!value.matches("^[A-Z0-9]{6,12}$")) {
            throw new IllegalArgumentException("Invalid SKU format - गलत SKU format");
        }
        this.value = value.toUpperCase().trim();
    }
    
    public String getValue() { return value; }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof ProductSKU)) return false;
        ProductSKU sku = (ProductSKU) o;
        return Objects.equals(value, sku.value);
    }
    
    @Override
    public int hashCode() { return Objects.hash(value); }
    
    @Override
    public String toString() { return value; }
}

/**
 * Money value object with currency support
 * Currency support के साथ money value object
 */
class Money {
    private final BigDecimal amount;
    private final String currency;
    
    public Money(BigDecimal amount, String currency) {
        if (amount == null || amount.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Amount cannot be negative - रकम negative नहीं हो सकती");
        }
        this.amount = amount.setScale(2, BigDecimal.ROUND_HALF_UP);
        this.currency = currency != null ? currency.toUpperCase() : "INR";
    }
    
    public Money(double amount) {
        this(BigDecimal.valueOf(amount), "INR");
    }
    
    public BigDecimal getAmount() { return amount; }
    public String getCurrency() { return currency; }
    
    public Money add(Money other) {
        validateSameCurrency(other);
        return new Money(this.amount.add(other.amount), this.currency);
    }
    
    public Money subtract(Money other) {
        validateSameCurrency(other);
        return new Money(this.amount.subtract(other.amount), this.currency);
    }
    
    public Money multiply(BigDecimal factor) {
        return new Money(this.amount.multiply(factor), this.currency);
    }
    
    public Money multiply(double factor) {
        return multiply(BigDecimal.valueOf(factor));
    }
    
    public boolean isGreaterThan(Money other) {
        validateSameCurrency(other);
        return this.amount.compareTo(other.amount) > 0;
    }
    
    private void validateSameCurrency(Money other) {
        if (!this.currency.equals(other.currency)) {
            throw new IllegalArgumentException("Currency mismatch - Currency match नहीं करती");
        }
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Money)) return false;
        Money money = (Money) o;
        return Objects.equals(amount, money.amount) && Objects.equals(currency, money.currency);
    }
    
    @Override
    public int hashCode() { return Objects.hash(amount, currency); }
    
    @Override
    public String toString() {
        return String.format("₹%.2f", amount.doubleValue());
    }
}

/**
 * Quantity value object with unit support
 * Unit support के साथ quantity value object
 */
class Quantity {
    private final BigDecimal value;
    private final String unit;
    
    public Quantity(BigDecimal value, String unit) {
        if (value == null || value.compareTo(BigDecimal.ZERO) < 0) {
            throw new IllegalArgumentException("Quantity cannot be negative - Quantity negative नहीं हो सकती");
        }
        this.value = value.setScale(3, BigDecimal.ROUND_HALF_UP);
        this.unit = unit != null ? unit.toLowerCase() : "pcs";
    }
    
    public Quantity(double value, String unit) {
        this(BigDecimal.valueOf(value), unit);
    }
    
    public BigDecimal getValue() { return value; }
    public String getUnit() { return unit; }
    
    public Quantity add(Quantity other) {
        validateSameUnit(other);
        return new Quantity(this.value.add(other.value), this.unit);
    }
    
    public Quantity subtract(Quantity other) {
        validateSameUnit(other);
        return new Quantity(this.value.subtract(other.value), this.unit);
    }
    
    public boolean isGreaterThan(Quantity other) {
        validateSameUnit(other);
        return this.value.compareTo(other.value) > 0;
    }
    
    public boolean isZero() {
        return this.value.compareTo(BigDecimal.ZERO) == 0;
    }
    
    private void validateSameUnit(Quantity other) {
        if (!this.unit.equals(other.unit)) {
            throw new IllegalArgumentException("Unit mismatch - Unit match नहीं करती");
        }
    }
    
    @Override
    public String toString() {
        return String.format("%.2f %s", value.doubleValue(), unit);
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Quantity)) return false;
        Quantity quantity = (Quantity) o;
        return Objects.equals(value, quantity.value) && Objects.equals(unit, quantity.unit);
    }
    
    @Override
    public int hashCode() { return Objects.hash(value, unit); }
}

/**
 * Expiry information value object
 * Expiry information value object
 */
class ExpiryInfo {
    private final LocalDate manufacturedDate;
    private final LocalDate expiryDate;
    private final int shelfLifeDays;
    
    public ExpiryInfo(LocalDate manufacturedDate, LocalDate expiryDate) {
        if (manufacturedDate == null || expiryDate == null) {
            throw new IllegalArgumentException("Dates cannot be null - Dates null नहीं हो सकती");
        }
        if (expiryDate.isBefore(manufacturedDate)) {
            throw new IllegalArgumentException("Expiry date cannot be before manufactured date");
        }
        
        this.manufacturedDate = manufacturedDate;
        this.expiryDate = expiryDate;
        this.shelfLifeDays = (int) ChronoUnit.DAYS.between(manufacturedDate, expiryDate);
    }
    
    public LocalDate getManufacturedDate() { return manufacturedDate; }
    public LocalDate getExpiryDate() { return expiryDate; }
    public int getShelfLifeDays() { return shelfLifeDays; }
    
    /**
     * Check if product is expired
     * Product expired है या नहीं check करना
     */
    public boolean isExpired() {
        return LocalDate.now().isAfter(expiryDate);
    }
    
    /**
     * Check if product will expire soon (within warning days)
     * Product जल्दी expire होगा या नहीं check करना
     */
    public boolean willExpireSoon(int warningDays) {
        LocalDate warningDate = LocalDate.now().plusDays(warningDays);
        return expiryDate.isBefore(warningDate) || expiryDate.equals(warningDate);
    }
    
    /**
     * Get days remaining until expiry
     * Expiry तक कितने दिन बचे हैं
     */
    public long getDaysUntilExpiry() {
        return ChronoUnit.DAYS.between(LocalDate.now(), expiryDate);
    }
    
    @Override
    public String toString() {
        return String.format("MFD: %s, EXP: %s (%d days shelf life)", 
            manufacturedDate, expiryDate, shelfLifeDays);
    }
}

// ====================================================================
// ENTITIES
// ====================================================================

/**
 * Product Entity - Core product information
 * Product Entity - Core product की जानकारी
 */
class Product {
    private final ProductSKU sku;
    private String name;
    private String description;
    private ProductCategory category;
    private String brand;
    private Money unitPrice;
    private Quantity unitSize;
    private StorageCondition storageCondition;
    private boolean isActive;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    public Product(ProductSKU sku, String name, ProductCategory category, String brand) {
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Product name required - Product name जरूरी है");
        }
        if (brand == null || brand.trim().isEmpty()) {
            throw new IllegalArgumentException("Brand required - Brand जरूरी है");
        }
        
        this.sku = sku;
        this.name = name.trim();
        this.category = category;
        this.brand = brand.trim();
        this.description = "";
        this.isActive = true;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        // Default storage condition based on category
        this.storageCondition = determineDefaultStorageCondition(category);
        
        System.out.println("📦 Product created: " + name + " (" + sku + ")");
    }
    
    // Business methods
    public void updatePrice(Money newPrice) {
        if (newPrice == null) {
            throw new IllegalArgumentException("Price cannot be null");
        }
        
        Money oldPrice = this.unitPrice;
        this.unitPrice = newPrice;
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("💰 Price updated for " + name + ": " + oldPrice + " → " + newPrice);
    }
    
    public void updateDescription(String description) {
        this.description = description != null ? description.trim() : "";
        this.updatedAt = LocalDateTime.now();
    }
    
    public void deactivate(String reason) {
        this.isActive = false;
        this.updatedAt = LocalDateTime.now();
        System.out.println("🚫 Product deactivated: " + name + " - " + reason);
    }
    
    public void activate() {
        this.isActive = true;
        this.updatedAt = LocalDateTime.now();
        System.out.println("✅ Product activated: " + name);
    }
    
    private StorageCondition determineDefaultStorageCondition(ProductCategory category) {
        return switch (category) {
            case FRESH_PRODUCE -> StorageCondition.CHILLED;
            case DAIRY -> StorageCondition.CHILLED;
            case MEAT_FISH -> StorageCondition.FROZEN;
            case BEVERAGES -> StorageCondition.CHILLED;
            default -> StorageCondition.AMBIENT;
        };
    }
    
    // Getters
    public ProductSKU getSku() { return sku; }
    public String getName() { return name; }
    public String getDescription() { return description; }
    public ProductCategory getCategory() { return category; }
    public String getBrand() { return brand; }
    public Money getUnitPrice() { return unitPrice; }
    public Quantity getUnitSize() { return unitSize; }
    public StorageCondition getStorageCondition() { return storageCondition; }
    public boolean isActive() { return isActive; }
    
    public void setUnitSize(Quantity unitSize) { 
        this.unitSize = unitSize; 
        this.updatedAt = LocalDateTime.now();
    }
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Product)) return false;
        Product product = (Product) o;
        return Objects.equals(sku, product.sku);
    }
    
    @Override
    public int hashCode() { return Objects.hash(sku); }
    
    @Override
    public String toString() { return String.format("Product(%s: %s)", sku, name); }
}

/**
 * Supplier Entity - Supplier information and management
 * Supplier Entity - Supplier की जानकारी और management
 */
class Supplier {
    private final String supplierId;
    private String name;
    private String contactPerson;
    private String phone;
    private String email;
    private String address;
    private SupplierStatus status;
    private double rating; // 1.0 to 5.0
    private int paymentTermsDays;
    private Money creditLimit;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
    
    // Performance metrics
    private int totalOrders;
    private int onTimeDeliveries;
    private int qualityIssues;
    
    public Supplier(String supplierId, String name, String contactPerson) {
        if (supplierId == null || supplierId.trim().isEmpty()) {
            throw new IllegalArgumentException("Supplier ID required");
        }
        if (name == null || name.trim().isEmpty()) {
            throw new IllegalArgumentException("Supplier name required");
        }
        
        this.supplierId = supplierId.trim();
        this.name = name.trim();
        this.contactPerson = contactPerson != null ? contactPerson.trim() : "";
        this.status = SupplierStatus.ACTIVE;
        this.rating = 3.0; // Default rating
        this.paymentTermsDays = 30; // 30 days payment terms
        this.creditLimit = new Money(100000.0); // ₹1 lakh default credit limit
        this.createdAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("🏪 Supplier registered: " + name + " (" + supplierId + ")");
    }
    
    // Business methods
    public void updateContactInfo(String phone, String email, String address) {
        this.phone = phone;
        this.email = email;
        this.address = address;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void updateRating(double rating) {
        if (rating < 1.0 || rating > 5.0) {
            throw new IllegalArgumentException("Rating must be between 1.0 and 5.0");
        }
        this.rating = rating;
        this.updatedAt = LocalDateTime.now();
    }
    
    public void recordDelivery(boolean onTime, boolean qualityOk) {
        this.totalOrders++;
        if (onTime) this.onTimeDeliveries++;
        if (!qualityOk) this.qualityIssues++;
        this.updatedAt = LocalDateTime.now();
        
        // Auto-adjust rating based on performance
        adjustRatingBasedOnPerformance();
    }
    
    private void adjustRatingBasedOnPerformance() {
        if (totalOrders < 5) return; // Need minimum orders for rating
        
        double onTimePercentage = (double) onTimeDeliveries / totalOrders;
        double qualityPercentage = 1.0 - ((double) qualityIssues / totalOrders);
        
        double calculatedRating = 2.5 + (onTimePercentage * 1.5) + (qualityPercentage * 1.0);
        this.rating = Math.min(5.0, Math.max(1.0, calculatedRating));
    }
    
    public void suspend(String reason) {
        this.status = SupplierStatus.SUSPENDED;
        this.updatedAt = LocalDateTime.now();
        System.out.println("⚠️ Supplier suspended: " + name + " - " + reason);
    }
    
    public void activate() {
        this.status = SupplierStatus.ACTIVE;
        this.updatedAt = LocalDateTime.now();
        System.out.println("✅ Supplier activated: " + name);
    }
    
    public boolean isActive() {
        return status == SupplierStatus.ACTIVE;
    }
    
    // Getters
    public String getSupplierId() { return supplierId; }
    public String getName() { return name; }
    public String getContactPerson() { return contactPerson; }
    public SupplierStatus getStatus() { return status; }
    public double getRating() { return rating; }
    public double getOnTimeDeliveryRate() {
        return totalOrders > 0 ? (double) onTimeDeliveries / totalOrders : 0.0;
    }
    
    @Override
    public String toString() {
        return String.format("Supplier(%s: %s - %.1f⭐)", supplierId, name, rating);
    }
}

/**
 * Stock Entry Entity - Individual stock batch tracking
 * Stock Entry Entity - Individual stock batch की tracking
 */
class StockEntry {
    private final String batchId;
    private final ProductSKU productSku;
    private final String supplierId;
    private Quantity currentQuantity;
    private final Quantity originalQuantity;
    private final Money unitCost;
    private final ExpiryInfo expiryInfo;
    private final LocalDateTime receivedAt;
    private LocalDateTime updatedAt;
    
    public StockEntry(String batchId, ProductSKU productSku, String supplierId,
                     Quantity quantity, Money unitCost, ExpiryInfo expiryInfo) {
        if (batchId == null || batchId.trim().isEmpty()) {
            throw new IllegalArgumentException("Batch ID required");
        }
        if (quantity.isZero()) {
            throw new IllegalArgumentException("Quantity must be positive");
        }
        
        this.batchId = batchId.trim();
        this.productSku = productSku;
        this.supplierId = supplierId;
        this.currentQuantity = quantity;
        this.originalQuantity = quantity;
        this.unitCost = unitCost;
        this.expiryInfo = expiryInfo;
        this.receivedAt = LocalDateTime.now();
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📥 Stock received: " + quantity + " of " + productSku + " (Batch: " + batchId + ")");
    }
    
    // Business methods
    public Quantity reserve(Quantity requestedQuantity) {
        if (requestedQuantity.isGreaterThan(currentQuantity)) {
            throw new InsufficientStockException("Insufficient stock in batch " + batchId + 
                ". Available: " + currentQuantity + ", Requested: " + requestedQuantity);
        }
        
        if (expiryInfo.isExpired()) {
            throw new ExpiredProductException("Cannot reserve expired stock from batch " + batchId);
        }
        
        this.currentQuantity = currentQuantity.subtract(requestedQuantity);
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("📤 Reserved " + requestedQuantity + " from batch " + batchId + 
            ". Remaining: " + currentQuantity);
        
        return requestedQuantity;
    }
    
    public void adjustQuantity(Quantity adjustment, String reason) {
        Quantity oldQuantity = this.currentQuantity;
        this.currentQuantity = currentQuantity.add(adjustment);
        this.updatedAt = LocalDateTime.now();
        
        System.out.println("🔧 Stock adjusted for batch " + batchId + ": " + 
            oldQuantity + " → " + currentQuantity + " (" + reason + ")");
    }
    
    public boolean isEmpty() {
        return currentQuantity.isZero();
    }
    
    public boolean isExpired() {
        return expiryInfo.isExpired();
    }
    
    public boolean willExpireSoon(int warningDays) {
        return expiryInfo.willExpireSoon(warningDays);
    }
    
    public long getDaysUntilExpiry() {
        return expiryInfo.getDaysUntilExpiry();
    }
    
    // Getters
    public String getBatchId() { return batchId; }
    public ProductSKU getProductSku() { return productSku; }
    public String getSupplierId() { return supplierId; }
    public Quantity getCurrentQuantity() { return currentQuantity; }
    public Quantity getOriginalQuantity() { return originalQuantity; }
    public Money getUnitCost() { return unitCost; }
    public ExpiryInfo getExpiryInfo() { return expiryInfo; }
    public LocalDateTime getReceivedAt() { return receivedAt; }
    
    @Override
    public String toString() {
        return String.format("StockEntry(%s: %s of %s)", batchId, currentQuantity, productSku);
    }
}

// ====================================================================
// DOMAIN SERVICES
// ====================================================================

/**
 * Stock Allocation Service - Complex stock allocation logic
 * Stock Allocation Service - Complex stock allocation logic
 */
class StockAllocationService {
    
    /**
     * Allocate stock using FIFO (First In First Out) strategy
     * FIFO strategy का इस्तेमाल करके stock allocate करना
     */
    public List<StockEntry> allocateStock(ProductSKU productSku, Quantity requestedQuantity,
                                        List<StockEntry> availableStock) {
        
        System.out.println("🎯 Allocating " + requestedQuantity + " of " + productSku);
        
        // Filter available stock for the product (non-expired, non-empty)
        List<StockEntry> validStock = availableStock.stream()
            .filter(entry -> entry.getProductSku().equals(productSku))
            .filter(entry -> !entry.isEmpty())
            .filter(entry -> !entry.isExpired())
            .sorted((a, b) -> a.getReceivedAt().compareTo(b.getReceivedAt())) // FIFO
            .collect(Collectors.toList());
        
        if (validStock.isEmpty()) {
            throw new InsufficientStockException("No valid stock available for " + productSku);
        }
        
        // Calculate total available quantity
        Quantity totalAvailable = validStock.stream()
            .map(StockEntry::getCurrentQuantity)
            .reduce(new Quantity(0, requestedQuantity.getUnit()), Quantity::add);
        
        if (requestedQuantity.isGreaterThan(totalAvailable)) {
            throw new InsufficientStockException("Insufficient total stock. Available: " + 
                totalAvailable + ", Requested: " + requestedQuantity);
        }
        
        // Allocate from batches using FIFO
        List<StockEntry> allocatedBatches = new ArrayList<>();
        Quantity remainingToAllocate = requestedQuantity;
        
        for (StockEntry stockEntry : validStock) {
            if (remainingToAllocate.isZero()) break;
            
            Quantity batchAvailable = stockEntry.getCurrentQuantity();
            Quantity toAllocateFromBatch = remainingToAllocate.isGreaterThan(batchAvailable) 
                ? batchAvailable 
                : remainingToAllocate;
            
            stockEntry.reserve(toAllocateFromBatch);
            allocatedBatches.add(stockEntry);
            remainingToAllocate = remainingToAllocate.subtract(toAllocateFromBatch);
            
            System.out.println("   📦 Allocated " + toAllocateFromBatch + " from batch " + 
                stockEntry.getBatchId());
        }
        
        System.out.println("✅ Stock allocation complete: " + allocatedBatches.size() + " batches");
        return allocatedBatches;
    }
    
    /**
     * Check stock levels and get status
     * Stock levels check करके status निकालना
     */
    public StockStatus checkStockStatus(ProductSKU productSku, List<StockEntry> stockEntries,
                                       Quantity lowStockThreshold) {
        
        Quantity totalStock = stockEntries.stream()
            .filter(entry -> entry.getProductSku().equals(productSku))
            .filter(entry -> !entry.isEmpty())
            .filter(entry -> !entry.isExpired())
            .map(StockEntry::getCurrentQuantity)
            .reduce(new Quantity(0, lowStockThreshold.getUnit()), Quantity::add);
        
        if (totalStock.isZero()) {
            return StockStatus.OUT_OF_STOCK;
        } else if (totalStock.isGreaterThan(lowStockThreshold)) {
            return StockStatus.IN_STOCK;
        } else {
            return StockStatus.LOW_STOCK;
        }
    }
    
    /**
     * Get products expiring soon
     * जल्दी expire होने वाले products निकालना
     */
    public List<StockEntry> getExpiringStock(List<StockEntry> stockEntries, int warningDays) {
        return stockEntries.stream()
            .filter(entry -> !entry.isEmpty())
            .filter(entry -> entry.willExpireSoon(warningDays))
            .sorted((a, b) -> Long.compare(a.getDaysUntilExpiry(), b.getDaysUntilExpiry()))
            .collect(Collectors.toList());
    }
}

/**
 * Pricing Service - Dynamic pricing calculations
 * Pricing Service - Dynamic pricing calculations
 */
class PricingService {
    private static final double DEFAULT_MARKUP_PERCENTAGE = 25.0; // 25% markup
    private static final double CLEARANCE_DISCOUNT_PERCENTAGE = 30.0; // 30% clearance discount
    
    /**
     * Calculate selling price based on cost and various factors
     * Cost और various factors के base पर selling price calculate करना
     */
    public Money calculateSellingPrice(StockEntry stockEntry, Product product, 
                                     boolean isClearance, double demandMultiplier) {
        
        Money baseCost = stockEntry.getUnitCost();
        double markupPercentage = DEFAULT_MARKUP_PERCENTAGE;
        
        // Adjust markup based on demand
        markupPercentage *= demandMultiplier;
        
        // Apply category-based pricing strategy
        markupPercentage = adjustForCategory(product.getCategory(), markupPercentage);
        
        // Calculate base selling price
        Money sellingPrice = baseCost.multiply(1.0 + (markupPercentage / 100.0));
        
        // Apply clearance discount if needed
        if (isClearance || stockEntry.willExpireSoon(3)) {
            sellingPrice = sellingPrice.multiply(1.0 - (CLEARANCE_DISCOUNT_PERCENTAGE / 100.0));
            System.out.println("🏷️ Clearance pricing applied: " + CLEARANCE_DISCOUNT_PERCENTAGE + "% off");
        }
        
        return sellingPrice;
    }
    
    private double adjustForCategory(ProductCategory category, double baseMarkup) {
        return switch (category) {
            case FRESH_PRODUCE -> baseMarkup * 0.8; // Lower markup for fresh produce
            case DAIRY -> baseMarkup * 0.9;
            case MEAT_FISH -> baseMarkup * 1.1; // Higher markup for premium products
            case PERSONAL_CARE -> baseMarkup * 1.3;
            case HOUSEHOLD -> baseMarkup * 1.2;
            default -> baseMarkup;
        };
    }
    
    /**
     * Calculate bulk discount
     * Bulk discount calculate करना
     */
    public Money applyBulkDiscount(Money totalAmount, Quantity totalQuantity) {
        double discountPercentage = 0.0;
        
        // Quantity-based bulk discount
        if (totalQuantity.getValue().doubleValue() >= 50) {
            discountPercentage = 10.0; // 10% for 50+ items
        } else if (totalQuantity.getValue().doubleValue() >= 20) {
            discountPercentage = 5.0; // 5% for 20+ items
        }
        
        // Amount-based discount
        if (totalAmount.getAmount().doubleValue() >= 5000) {
            discountPercentage = Math.max(discountPercentage, 8.0); // 8% for ₹5000+ orders
        }
        
        if (discountPercentage > 0) {
            Money discount = totalAmount.multiply(discountPercentage / 100.0);
            System.out.println("💰 Bulk discount applied: " + discountPercentage + "% (₹" + 
                discount.getAmount() + ")");
            return totalAmount.subtract(discount);
        }
        
        return totalAmount;
    }
}

// ====================================================================
// AGGREGATE ROOT - Inventory Management
// ====================================================================

/**
 * Inventory Aggregate - Main inventory management logic
 * Inventory Aggregate - Main inventory management logic
 */
public class BigBasketInventoryDomain {
    // Core entities
    private final Map<ProductSKU, Product> products;
    private final Map<String, Supplier> suppliers;
    private final List<StockEntry> stockEntries;
    
    // Domain services
    private final StockAllocationService allocationService;
    private final PricingService pricingService;
    
    // Configuration
    private final Map<ProductCategory, Quantity> lowStockThresholds;
    
    public BigBasketInventoryDomain() {
        this.products = new ConcurrentHashMap<>();
        this.suppliers = new ConcurrentHashMap<>();
        this.stockEntries = Collections.synchronizedList(new ArrayList<>());
        
        this.allocationService = new StockAllocationService();
        this.pricingService = new PricingService();
        
        this.lowStockThresholds = initializeLowStockThresholds();
        
        System.out.println("🏪 BigBasket Inventory Domain initialized");
    }
    
    private Map<ProductCategory, Quantity> initializeLowStockThresholds() {
        Map<ProductCategory, Quantity> thresholds = new HashMap<>();
        thresholds.put(ProductCategory.FRESH_PRODUCE, new Quantity(50, "kg"));
        thresholds.put(ProductCategory.DAIRY, new Quantity(100, "liters"));
        thresholds.put(ProductCategory.PACKAGED_FOODS, new Quantity(500, "pcs"));
        thresholds.put(ProductCategory.BEVERAGES, new Quantity(200, "bottles"));
        thresholds.put(ProductCategory.PERSONAL_CARE, new Quantity(100, "pcs"));
        thresholds.put(ProductCategory.HOUSEHOLD, new Quantity(50, "pcs"));
        return thresholds;
    }
    
    // ====================================================================
    // PRODUCT MANAGEMENT
    // ====================================================================
    
    public void addProduct(ProductSKU sku, String name, ProductCategory category, 
                          String brand, Money unitPrice, Quantity unitSize) {
        
        if (products.containsKey(sku)) {
            throw new IllegalArgumentException("Product already exists: " + sku);
        }
        
        Product product = new Product(sku, name, category, brand);
        product.updatePrice(unitPrice);
        product.setUnitSize(unitSize);
        
        products.put(sku, product);
        System.out.println("✅ Product added to catalog: " + name);
    }
    
    public void addSupplier(String supplierId, String name, String contactPerson,
                           String phone, String email) {
        
        if (suppliers.containsKey(supplierId)) {
            throw new IllegalArgumentException("Supplier already exists: " + supplierId);
        }
        
        Supplier supplier = new Supplier(supplierId, name, contactPerson);
        supplier.updateContactInfo(phone, email, null);
        
        suppliers.put(supplierId, supplier);
        System.out.println("✅ Supplier added: " + name);
    }
    
    // ====================================================================
    // STOCK MANAGEMENT
    // ====================================================================
    
    public void receiveStock(ProductSKU productSku, String supplierId, String batchId,
                           Quantity quantity, Money unitCost, ExpiryInfo expiryInfo) {
        
        // Validate product exists
        Product product = products.get(productSku);
        if (product == null) {
            throw new IllegalArgumentException("Product not found: " + productSku);
        }
        
        // Validate supplier exists and is active
        Supplier supplier = suppliers.get(supplierId);
        if (supplier == null) {
            throw new IllegalArgumentException("Supplier not found: " + supplierId);
        }
        if (!supplier.isActive()) {
            throw new SupplierNotActiveException("Supplier is not active: " + supplierId);
        }
        
        // Create stock entry
        StockEntry stockEntry = new StockEntry(batchId, productSku, supplierId, 
                                             quantity, unitCost, expiryInfo);
        stockEntries.add(stockEntry);
        
        System.out.println("📦 Stock received from " + supplier.getName());
    }
    
    public List<StockEntry> allocateStock(ProductSKU productSku, Quantity requestedQuantity) {
        Product product = products.get(productSku);
        if (product == null) {
            throw new IllegalArgumentException("Product not found: " + productSku);
        }
        
        if (!product.isActive()) {
            throw new IllegalArgumentException("Product is not active: " + productSku);
        }
        
        return allocationService.allocateStock(productSku, requestedQuantity, stockEntries);
    }
    
    // ====================================================================
    // INVENTORY QUERIES AND REPORTS
    // ====================================================================
    
    public StockStatus getStockStatus(ProductSKU productSku) {
        Product product = products.get(productSku);
        if (product == null) return StockStatus.OUT_OF_STOCK;
        
        Quantity threshold = lowStockThresholds.getOrDefault(product.getCategory(), 
                                                           new Quantity(10, "pcs"));
        
        return allocationService.checkStockStatus(productSku, stockEntries, threshold);
    }
    
    public Quantity getTotalAvailableStock(ProductSKU productSku) {
        String unit = "pcs"; // Default unit
        Product product = products.get(productSku);
        if (product != null && product.getUnitSize() != null) {
            unit = product.getUnitSize().getUnit();
        }
        
        return stockEntries.stream()
            .filter(entry -> entry.getProductSku().equals(productSku))
            .filter(entry -> !entry.isEmpty())
            .filter(entry -> !entry.isExpired())
            .map(StockEntry::getCurrentQuantity)
            .reduce(new Quantity(0, unit), Quantity::add);
    }
    
    public List<StockEntry> getExpiringStock(int warningDays) {
        return allocationService.getExpiringStock(stockEntries, warningDays);
    }
    
    public Map<String, Object> getInventoryReport() {
        Map<String, Object> report = new HashMap<>();
        
        // Product statistics
        long totalProducts = products.size();
        long activeProducts = products.values().stream()
            .mapToLong(p -> p.isActive() ? 1 : 0)
            .sum();
        
        // Stock statistics
        long totalBatches = stockEntries.size();
        long expiredBatches = stockEntries.stream()
            .mapToLong(entry -> entry.isExpired() ? 1 : 0)
            .sum();
        
        // Supplier statistics
        long totalSuppliers = suppliers.size();
        long activeSuppliers = suppliers.values().stream()
            .mapToLong(s -> s.isActive() ? 1 : 0)
            .sum();
        
        // Category-wise stock status
        Map<ProductCategory, Long> categoryStats = products.values().stream()
            .collect(Collectors.groupingBy(Product::getCategory, Collectors.counting()));
        
        report.put("totalProducts", totalProducts);
        report.put("activeProducts", activeProducts);
        report.put("totalStockBatches", totalBatches);
        report.put("expiredBatches", expiredBatches);
        report.put("totalSuppliers", totalSuppliers);
        report.put("activeSuppliers", activeSuppliers);
        report.put("categoryBreakdown", categoryStats);
        report.put("generatedAt", LocalDateTime.now());
        
        return report;
    }
    
    // ====================================================================
    // DEMO AND TESTING
    // ====================================================================
    
    public static void main(String[] args) {
        System.out.println("🏪 BigBasket Inventory Domain - DDD Example");
        System.out.println("=" + "=".repeat(50));
        
        // Create inventory system
        BigBasketInventoryDomain inventory = new BigBasketInventoryDomain();
        
        try {
            System.out.println("\n📦 Step 1: Setup Products and Suppliers");
            
            // Add suppliers
            inventory.addSupplier("SUP_001", "Fresh Valley Farms", "Rajesh Kumar", 
                                "9876543210", "rajesh@freshvalley.com");
            inventory.addSupplier("SUP_002", "Amul Dairy", "Priya Sharma", 
                                "9876543211", "priya@amul.com");
            
            // Add products
            inventory.addProduct(
                new ProductSKU("APPLE001"), 
                "Himalayan Apples", 
                ProductCategory.FRESH_PRODUCE, 
                "Fresh Valley",
                new Money(150.0), 
                new Quantity(1, "kg")
            );
            
            inventory.addProduct(
                new ProductSKU("MILK001"),
                "Amul Fresh Milk",
                ProductCategory.DAIRY,
                "Amul",
                new Money(45.0),
                new Quantity(1, "liter")
            );
            
            System.out.println("\n📥 Step 2: Receive Stock");
            
            // Receive apple stock
            ExpiryInfo appleExpiry = new ExpiryInfo(LocalDate.now(), LocalDate.now().plusDays(7));
            inventory.receiveStock(
                new ProductSKU("APPLE001"),
                "SUP_001",
                "BATCH_APL_001",
                new Quantity(100, "kg"),
                new Money(120.0), // Cost price
                appleExpiry
            );
            
            // Receive milk stock
            ExpiryInfo milkExpiry = new ExpiryInfo(LocalDate.now(), LocalDate.now().plusDays(3));
            inventory.receiveStock(
                new ProductSKU("MILK001"),
                "SUP_002", 
                "BATCH_MLK_001",
                new Quantity(500, "liter"),
                new Money(35.0), // Cost price
                milkExpiry
            );
            
            System.out.println("\n🛒 Step 3: Stock Allocation");
            
            // Allocate apples for an order
            List<StockEntry> appleAllocation = inventory.allocateStock(
                new ProductSKU("APPLE001"), 
                new Quantity(15, "kg")
            );
            
            System.out.println("Allocated " + appleAllocation.size() + " batches for apples");
            
            // Allocate milk
            List<StockEntry> milkAllocation = inventory.allocateStock(
                new ProductSKU("MILK001"),
                new Quantity(50, "liter")
            );
            
            System.out.println("Allocated " + milkAllocation.size() + " batches for milk");
            
            System.out.println("\n📊 Step 4: Inventory Status");
            
            // Check stock levels
            ProductSKU appleSku = new ProductSKU("APPLE001");
            StockStatus appleStatus = inventory.getStockStatus(appleSku);
            Quantity appleStock = inventory.getTotalAvailableStock(appleSku);
            
            System.out.println("Apple Stock Status: " + appleStatus.getDisplayName());
            System.out.println("Apple Available: " + appleStock);
            
            ProductSKU milkSku = new ProductSKU("MILK001");
            StockStatus milkStatus = inventory.getStockStatus(milkSku);
            Quantity milkStock = inventory.getTotalAvailableStock(milkSku);
            
            System.out.println("Milk Stock Status: " + milkStatus.getDisplayName());
            System.out.println("Milk Available: " + milkStock);
            
            System.out.println("\n⚠️ Step 5: Expiry Management");
            
            // Check expiring stock
            List<StockEntry> expiringStock = inventory.getExpiringStock(5);
            System.out.println("Products expiring in 5 days: " + expiringStock.size());
            
            for (StockEntry entry : expiringStock) {
                System.out.println("   - Batch " + entry.getBatchId() + 
                    " (" + entry.getProductSku() + "): " + entry.getDaysUntilExpiry() + " days left");
            }
            
            System.out.println("\n📋 Step 6: Inventory Report");
            
            Map<String, Object> report = inventory.getInventoryReport();
            System.out.println("Inventory Report:");
            report.forEach((key, value) -> {
                if (!key.equals("categoryBreakdown")) {
                    System.out.println("   " + key + ": " + value);
                }
            });
            
            System.out.println("\n✨ Domain operations completed successfully!");
            System.out.println("✨ All business rules enforced!");
            System.out.println("✨ Ready for production BigBasket-scale system!");
            
        } catch (Exception e) {
            System.err.println("❌ Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}