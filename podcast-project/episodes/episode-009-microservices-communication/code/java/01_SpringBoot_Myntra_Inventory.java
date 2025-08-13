/*
Spring Boot Microservice for Myntra-style Fashion Inventory Management
Production-grade REST API with Spring Cloud features

Author: Episode 9 - Microservices Communication
Context: Myntra jaise fashion inventory - Java Spring Boot implementation
*/

package com.myntra.inventory;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.netflix.eureka.EnableEurekaClient;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpStatus;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.stereotype.Component;
import org.springframework.data.annotation.Id;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.validation.annotation.Validated;

import javax.validation.Valid;
import javax.validation.constraints.NotBlank;
import javax.validation.constraints.NotNull;
import javax.validation.constraints.Positive;
import javax.validation.constraints.Min;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.time.LocalDateTime;
import java.math.BigDecimal;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// Main Application Class
@SpringBootApplication
@EnableEurekaClient
public class MyntraInventoryApplication {
    
    private static final Logger logger = LoggerFactory.getLogger(MyntraInventoryApplication.class);
    
    public static void main(String[] args) {
        System.out.println("👗 Myntra Fashion Inventory - Spring Boot Microservice");
        System.out.println("=".repeat(65));
        
        SpringApplication.run(MyntraInventoryApplication.class, args);
        
        logger.info("Myntra Inventory Service started successfully");
        logger.info("Available endpoints: /api/v1/inventory/**");
    }
}

// Enums
enum ProductCategory {
    MENS_CLOTHING("Men's Clothing"),
    WOMENS_CLOTHING("Women's Clothing"),
    KIDS_CLOTHING("Kids Clothing"),
    FOOTWEAR("Footwear"),
    ACCESSORIES("Accessories"),
    BEAUTY("Beauty & Personal Care");
    
    private final String displayName;
    
    ProductCategory(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

enum ProductSize {
    XS, S, M, L, XL, XXL, XXXL,
    UK_6, UK_7, UK_8, UK_9, UK_10, UK_11, UK_12,
    ONE_SIZE
}

enum ProductColor {
    RED("Red"), BLUE("Blue"), GREEN("Green"), BLACK("Black"), 
    WHITE("White"), YELLOW("Yellow"), PINK("Pink"), PURPLE("Purple"),
    BROWN("Brown"), GREY("Grey"), NAVY("Navy"), MULTICOLOR("Multicolor");
    
    private final String displayName;
    
    ProductColor(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

enum InventoryStatus {
    IN_STOCK("In Stock"),
    LOW_STOCK("Low Stock"), 
    OUT_OF_STOCK("Out of Stock"),
    DISCONTINUED("Discontinued");
    
    private final String displayName;
    
    InventoryStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}

// Data Models
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
class ProductInventory {
    
    @Id
    private String productId;
    
    @NotBlank(message = "Product name cannot be blank")
    private String productName;
    
    @NotBlank(message = "Brand cannot be blank")
    private String brand;
    
    @NotNull(message = "Category cannot be null")
    private ProductCategory category;
    
    private String description;
    
    @NotNull(message = "Size cannot be null")
    private ProductSize size;
    
    @NotNull(message = "Color cannot be null") 
    private ProductColor color;
    
    @NotNull(message = "Price cannot be null")
    @Positive(message = "Price must be positive")
    private BigDecimal price;
    
    @NotNull(message = "MRP cannot be null")
    @Positive(message = "MRP must be positive")
    private BigDecimal mrp;
    
    @Min(value = 0, message = "Stock quantity cannot be negative")
    private Integer stockQuantity;
    
    @Min(value = 0, message = "Reserved quantity cannot be negative")
    private Integer reservedQuantity;
    
    private InventoryStatus status;
    
    private String imageUrl;
    
    private String sku; // Stock Keeping Unit
    
    private String vendorId;
    
    private String warehouseId;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime createdAt;
    
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private LocalDateTime updatedAt;
    
    // Business logic methods
    public Integer getAvailableQuantity() {
        return stockQuantity - reservedQuantity;
    }
    
    public boolean isAvailable() {
        return status == InventoryStatus.IN_STOCK && getAvailableQuantity() > 0;
    }
    
    public boolean isLowStock(int threshold) {
        return getAvailableQuantity() <= threshold;
    }
    
    public double getDiscountPercentage() {
        if (mrp.compareTo(BigDecimal.ZERO) == 0) {
            return 0.0;
        }
        return (1 - price.divide(mrp, 2, BigDecimal.ROUND_HALF_UP).doubleValue()) * 100;
    }
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class InventoryUpdateRequest {
    
    @NotBlank(message = "Product ID cannot be blank")
    private String productId;
    
    @NotNull(message = "Quantity cannot be null")
    @Min(value = 0, message = "Quantity cannot be negative")
    private Integer quantity;
    
    private String reason;
    
    private String updatedBy;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class InventoryReservationRequest {
    
    @NotBlank(message = "Product ID cannot be blank")
    private String productId;
    
    @NotNull(message = "Quantity cannot be null")
    @Positive(message = "Quantity must be positive")
    private Integer quantity;
    
    @NotBlank(message = "Order ID cannot be blank")
    private String orderId;
    
    private Integer reservationTimeoutMinutes = 15; // Default 15 minutes
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class InventorySearchFilter {
    private String category;
    private String brand;
    private String color;
    private String size;
    private BigDecimal minPrice;
    private BigDecimal maxPrice;
    private InventoryStatus status;
    private String warehouseId;
    private Boolean lowStockOnly = false;
    private Integer page = 0;
    private Integer size_param = 20;
}

@Data
@AllArgsConstructor
class ApiResponse<T> {
    private boolean success;
    private String message;
    private T data;
    private LocalDateTime timestamp;
    
    public static <T> ApiResponse<T> success(T data, String message) {
        return new ApiResponse<>(true, message, data, LocalDateTime.now());
    }
    
    public static <T> ApiResponse<T> error(String message) {
        return new ApiResponse<>(false, message, null, LocalDateTime.now());
    }
}

@Data
@AllArgsConstructor
class InventoryMetrics {
    private Long totalProducts;
    private Long inStockProducts;
    private Long outOfStockProducts;
    private Long lowStockProducts;
    private BigDecimal totalInventoryValue;
    private Map<ProductCategory, Long> categoryDistribution;
    private Map<String, Long> topBrands;
}

// Service Layer
@Service
public class InventoryService {
    
    private static final Logger logger = LoggerFactory.getLogger(InventoryService.class);
    private static final int LOW_STOCK_THRESHOLD = 10;
    
    // In-memory storage (production mein database aur Redis hoga)
    private final Map<String, ProductInventory> inventory = new ConcurrentHashMap<>();
    private final Map<String, LocalDateTime> reservations = new ConcurrentHashMap<>();
    
    public InventoryService() {
        initializeDemoData();
    }
    
    private void initializeDemoData() {
        List<ProductInventory> demoProducts = Arrays.asList(
            // Men's Clothing
            ProductInventory.builder()
                .productId("MYN001")
                .productName("Roadster Men Blue Skinny Fit Jeans")
                .brand("Roadster")
                .category(ProductCategory.MENS_CLOTHING)
                .description("Comfortable skinny fit jeans with stretch fabric")
                .size(ProductSize.L)
                .color(ProductColor.BLUE)
                .price(new BigDecimal("1199.00"))
                .mrp(new BigDecimal("1499.00"))
                .stockQuantity(50)
                .reservedQuantity(2)
                .status(InventoryStatus.IN_STOCK)
                .imageUrl("/images/roadster-jeans-blue.jpg")
                .sku("RDS-JNS-BLU-L-001")
                .vendorId("VENDOR_001")
                .warehouseId("WH_Mumbai_01")
                .createdAt(LocalDateTime.now().minusDays(30))
                .updatedAt(LocalDateTime.now())
                .build(),
            
            // Women's Clothing
            ProductInventory.builder()
                .productId("MYN002")
                .productName("H&M Women Black A-Line Dress")
                .brand("H&M")
                .category(ProductCategory.WOMENS_CLOTHING)
                .description("Elegant A-line dress perfect for office and parties")
                .size(ProductSize.M)
                .color(ProductColor.BLACK)
                .price(new BigDecimal("2999.00"))
                .mrp(new BigDecimal("3499.00"))
                .stockQuantity(25)
                .reservedQuantity(1)
                .status(InventoryStatus.IN_STOCK)
                .imageUrl("/images/hm-dress-black.jpg")
                .sku("HM-DRS-BLK-M-002")
                .vendorId("VENDOR_002")
                .warehouseId("WH_Delhi_01")
                .createdAt(LocalDateTime.now().minusDays(15))
                .updatedAt(LocalDateTime.now())
                .build(),
            
            // Footwear
            ProductInventory.builder()
                .productId("MYN003")
                .productName("Nike Air Max 270 Running Shoes")
                .brand("Nike")
                .category(ProductCategory.FOOTWEAR)
                .description("Lightweight running shoes with Air Max cushioning")
                .size(ProductSize.UK_9)
                .color(ProductColor.WHITE)
                .price(new BigDecimal("12995.00"))
                .mrp(new BigDecimal("14995.00"))
                .stockQuantity(8)
                .reservedQuantity(0)
                .status(InventoryStatus.LOW_STOCK)
                .imageUrl("/images/nike-airmax-white.jpg")
                .sku("NK-AM270-WHT-UK9-003")
                .vendorId("VENDOR_003")
                .warehouseId("WH_Bangalore_01")
                .createdAt(LocalDateTime.now().minusDays(7))
                .updatedAt(LocalDateTime.now())
                .build(),
            
            // Accessories
            ProductInventory.builder()
                .productId("MYN004")
                .productName("Fossil Gen 5 Smartwatch")
                .brand("Fossil")
                .category(ProductCategory.ACCESSORIES)
                .description("Advanced smartwatch with health tracking features")
                .size(ProductSize.ONE_SIZE)
                .color(ProductColor.BLACK)
                .price(new BigDecimal("22995.00"))
                .mrp(new BigDecimal("24995.00"))
                .stockQuantity(0)
                .reservedQuantity(0)
                .status(InventoryStatus.OUT_OF_STOCK)
                .imageUrl("/images/fossil-smartwatch-black.jpg")
                .sku("FSL-GN5-BLK-OS-004")
                .vendorId("VENDOR_004")
                .warehouseId("WH_Chennai_01")
                .createdAt(LocalDateTime.now().minusDays(45))
                .updatedAt(LocalDateTime.now())
                .build(),
            
            // Kids Clothing
            ProductInventory.builder()
                .productId("MYN005")
                .productName("United Colors of Benetton Kids T-Shirt")
                .brand("UCB")
                .category(ProductCategory.KIDS_CLOTHING)
                .description("Colorful cotton t-shirt for kids aged 5-8 years")
                .size(ProductSize.M)
                .color(ProductColor.MULTICOLOR)
                .price(new BigDecimal("899.00"))
                .mrp(new BigDecimal("1199.00"))
                .stockQuantity(35)
                .reservedQuantity(3)
                .status(InventoryStatus.IN_STOCK)
                .imageUrl("/images/ucb-kids-tshirt.jpg")
                .sku("UCB-TSH-MUL-M-005")
                .vendorId("VENDOR_002")
                .warehouseId("WH_Mumbai_01")
                .createdAt(LocalDateTime.now().minusDays(20))
                .updatedAt(LocalDateTime.now())
                .build(),
            
            // Beauty
            ProductInventory.builder()
                .productId("MYN006")
                .productName("Lakme Absolute Skin Natural Mousse Foundation")
                .brand("Lakme")
                .category(ProductCategory.BEAUTY)
                .description("Light-weight mousse foundation for natural finish")
                .size(ProductSize.ONE_SIZE)
                .color(ProductColor.BROWN) // Skin tone
                .price(new BigDecimal("850.00"))
                .mrp(new BigDecimal("950.00"))
                .stockQuantity(60)
                .reservedQuantity(5)
                .status(InventoryStatus.IN_STOCK)
                .imageUrl("/images/lakme-foundation.jpg")
                .sku("LKM-FND-BRN-OS-006")
                .vendorId("VENDOR_005")
                .warehouseId("WH_Delhi_01")
                .createdAt(LocalDateTime.now().minusDays(10))
                .updatedAt(LocalDateTime.now())
                .build()
        );
        
        for (ProductInventory product : demoProducts) {
            inventory.put(product.getProductId(), product);
        }
        
        logger.info("Initialized demo inventory with {} products", demoProducts.size());
    }
    
    @Cacheable(value = "inventory", key = "#productId")
    public Optional<ProductInventory> getProductById(String productId) {
        logger.info("Fetching product inventory for ID: {}", productId);
        return Optional.ofNullable(inventory.get(productId));
    }
    
    public List<ProductInventory> searchProducts(InventorySearchFilter filter) {
        logger.info("Searching products with filter: {}", filter);
        
        return inventory.values().stream()
            .filter(product -> filterByCategory(product, filter.getCategory()))
            .filter(product -> filterByBrand(product, filter.getBrand()))
            .filter(product -> filterByColor(product, filter.getColor()))
            .filter(product -> filterBySize(product, filter.getSize()))
            .filter(product -> filterByPriceRange(product, filter.getMinPrice(), filter.getMaxPrice()))
            .filter(product -> filterByStatus(product, filter.getStatus()))
            .filter(product -> filterByWarehouse(product, filter.getWarehouseId()))
            .filter(product -> filterByLowStock(product, filter.getLowStockOnly()))
            .skip((long) filter.getPage() * filter.getSize_param())
            .limit(filter.getSize_param())
            .collect(Collectors.toList());
    }
    
    @CacheEvict(value = "inventory", key = "#request.productId")
    public boolean updateStock(InventoryUpdateRequest request) {
        logger.info("Updating stock for product: {}, new quantity: {}", 
                   request.getProductId(), request.getQuantity());
        
        ProductInventory product = inventory.get(request.getProductId());
        if (product == null) {
            logger.warn("Product not found for stock update: {}", request.getProductId());
            return false;
        }
        
        // Update stock quantity
        product.setStockQuantity(request.getQuantity());
        product.setUpdatedAt(LocalDateTime.now());
        
        // Update status based on stock
        if (request.getQuantity() == 0) {
            product.setStatus(InventoryStatus.OUT_OF_STOCK);
        } else if (request.getQuantity() <= LOW_STOCK_THRESHOLD) {
            product.setStatus(InventoryStatus.LOW_STOCK);
        } else {
            product.setStatus(InventoryStatus.IN_STOCK);
        }
        
        logger.info("Stock updated successfully for product: {}, new status: {}", 
                   request.getProductId(), product.getStatus());
        
        return true;
    }
    
    public boolean reserveInventory(InventoryReservationRequest request) {
        logger.info("Reserving inventory: {} units of product {}", 
                   request.getQuantity(), request.getProductId());
        
        ProductInventory product = inventory.get(request.getProductId());
        if (product == null || !product.isAvailable()) {
            logger.warn("Product not available for reservation: {}", request.getProductId());
            return false;
        }
        
        if (product.getAvailableQuantity() < request.getQuantity()) {
            logger.warn("Insufficient stock for reservation. Available: {}, Requested: {}", 
                       product.getAvailableQuantity(), request.getQuantity());
            return false;
        }
        
        // Reserve the inventory
        product.setReservedQuantity(product.getReservedQuantity() + request.getQuantity());
        product.setUpdatedAt(LocalDateTime.now());
        
        // Set reservation timeout
        String reservationKey = request.getOrderId() + ":" + request.getProductId();
        LocalDateTime expiryTime = LocalDateTime.now().plusMinutes(request.getReservationTimeoutMinutes());
        reservations.put(reservationKey, expiryTime);
        
        logger.info("Inventory reserved successfully for order: {}", request.getOrderId());
        return true;
    }
    
    public boolean releaseReservation(String orderId, String productId, Integer quantity) {
        logger.info("Releasing reservation for order: {}, product: {}", orderId, productId);
        
        ProductInventory product = inventory.get(productId);
        if (product == null) {
            return false;
        }
        
        // Release reservation
        int newReserved = Math.max(0, product.getReservedQuantity() - quantity);
        product.setReservedQuantity(newReserved);
        product.setUpdatedAt(LocalDateTime.now());
        
        // Remove reservation timeout
        String reservationKey = orderId + ":" + productId;
        reservations.remove(reservationKey);
        
        logger.info("Reservation released for order: {}", orderId);
        return true;
    }
    
    public InventoryMetrics getInventoryMetrics() {
        logger.info("Generating inventory metrics");
        
        List<ProductInventory> allProducts = new ArrayList<>(inventory.values());
        
        long totalProducts = allProducts.size();
        long inStockProducts = allProducts.stream()
            .mapToLong(p -> p.getStatus() == InventoryStatus.IN_STOCK ? 1 : 0)
            .sum();
        long outOfStockProducts = allProducts.stream()
            .mapToLong(p -> p.getStatus() == InventoryStatus.OUT_OF_STOCK ? 1 : 0)
            .sum();
        long lowStockProducts = allProducts.stream()
            .mapToLong(p -> p.getStatus() == InventoryStatus.LOW_STOCK ? 1 : 0)
            .sum();
        
        BigDecimal totalValue = allProducts.stream()
            .map(p -> p.getPrice().multiply(new BigDecimal(p.getStockQuantity())))
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        
        Map<ProductCategory, Long> categoryDistribution = allProducts.stream()
            .collect(Collectors.groupingBy(
                ProductInventory::getCategory,
                Collectors.counting()
            ));
        
        Map<String, Long> topBrands = allProducts.stream()
            .collect(Collectors.groupingBy(
                ProductInventory::getBrand,
                Collectors.counting()
            ));
        
        return new InventoryMetrics(
            totalProducts,
            inStockProducts,
            outOfStockProducts,
            lowStockProducts,
            totalValue,
            categoryDistribution,
            topBrands
        );
    }
    
    // Helper filter methods
    private boolean filterByCategory(ProductInventory product, String category) {
        return category == null || product.getCategory().name().equalsIgnoreCase(category);
    }
    
    private boolean filterByBrand(ProductInventory product, String brand) {
        return brand == null || product.getBrand().toLowerCase().contains(brand.toLowerCase());
    }
    
    private boolean filterByColor(ProductInventory product, String color) {
        return color == null || product.getColor().name().equalsIgnoreCase(color);
    }
    
    private boolean filterBySize(ProductInventory product, String size) {
        return size == null || product.getSize().name().equalsIgnoreCase(size);
    }
    
    private boolean filterByPriceRange(ProductInventory product, BigDecimal minPrice, BigDecimal maxPrice) {
        if (minPrice != null && product.getPrice().compareTo(minPrice) < 0) {
            return false;
        }
        if (maxPrice != null && product.getPrice().compareTo(maxPrice) > 0) {
            return false;
        }
        return true;
    }
    
    private boolean filterByStatus(ProductInventory product, InventoryStatus status) {
        return status == null || product.getStatus() == status;
    }
    
    private boolean filterByWarehouse(ProductInventory product, String warehouseId) {
        return warehouseId == null || product.getWarehouseId().equals(warehouseId);
    }
    
    private boolean filterByLowStock(ProductInventory product, Boolean lowStockOnly) {
        if (lowStockOnly == null || !lowStockOnly) {
            return true;
        }
        return product.isLowStock(LOW_STOCK_THRESHOLD);
    }
}

// REST Controller
@RestController
@RequestMapping("/api/v1/inventory")
@Validated
public class InventoryController {
    
    private static final Logger logger = LoggerFactory.getLogger(InventoryController.class);
    
    @Autowired
    private InventoryService inventoryService;
    
    @GetMapping("/health")
    public ResponseEntity<ApiResponse<Map<String, Object>>> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("service", "myntra-inventory");
        health.put("version", "1.0.0");
        health.put("timestamp", LocalDateTime.now());
        
        return ResponseEntity.ok(
            ApiResponse.success(health, "Service is healthy")
        );
    }
    
    @GetMapping("/{productId}")
    public ResponseEntity<ApiResponse<ProductInventory>> getProduct(
            @PathVariable @NotBlank String productId) {
        
        logger.info("GET request for product: {}", productId);
        
        Optional<ProductInventory> product = inventoryService.getProductById(productId);
        
        if (product.isPresent()) {
            return ResponseEntity.ok(
                ApiResponse.success(product.get(), "Product found")
            );
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error("Product not found"));
        }
    }
    
    @GetMapping("/search")
    public ResponseEntity<ApiResponse<List<ProductInventory>>> searchProducts(
            @RequestParam(required = false) String category,
            @RequestParam(required = false) String brand,
            @RequestParam(required = false) String color,
            @RequestParam(required = false) String size,
            @RequestParam(required = false) BigDecimal minPrice,
            @RequestParam(required = false) BigDecimal maxPrice,
            @RequestParam(required = false) String status,
            @RequestParam(required = false) String warehouseId,
            @RequestParam(required = false, defaultValue = "false") Boolean lowStockOnly,
            @RequestParam(required = false, defaultValue = "0") Integer page,
            @RequestParam(required = false, defaultValue = "20") Integer size_param) {
        
        logger.info("Search request with filters - category: {}, brand: {}, page: {}", 
                   category, brand, page);
        
        InventorySearchFilter filter = new InventorySearchFilter();
        filter.setCategory(category);
        filter.setBrand(brand);
        filter.setColor(color);
        filter.setSize(size);
        filter.setMinPrice(minPrice);
        filter.setMaxPrice(maxPrice);
        if (status != null) {
            try {
                filter.setStatus(InventoryStatus.valueOf(status.toUpperCase()));
            } catch (IllegalArgumentException e) {
                logger.warn("Invalid status parameter: {}", status);
            }
        }
        filter.setWarehouseId(warehouseId);
        filter.setLowStockOnly(lowStockOnly);
        filter.setPage(page);
        filter.setSize_param(size_param);
        
        List<ProductInventory> products = inventoryService.searchProducts(filter);
        
        return ResponseEntity.ok(
            ApiResponse.success(products, 
                String.format("Found %d products", products.size()))
        );
    }
    
    @PutMapping("/{productId}/stock")
    public ResponseEntity<ApiResponse<String>> updateStock(
            @PathVariable @NotBlank String productId,
            @RequestBody @Valid InventoryUpdateRequest request) {
        
        logger.info("Stock update request for product: {}", productId);
        
        request.setProductId(productId);
        boolean updated = inventoryService.updateStock(request);
        
        if (updated) {
            return ResponseEntity.ok(
                ApiResponse.success("Stock updated successfully", 
                    "Stock updated for product: " + productId)
            );
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error("Product not found"));
        }
    }
    
    @PostMapping("/reserve")
    public ResponseEntity<ApiResponse<String>> reserveInventory(
            @RequestBody @Valid InventoryReservationRequest request) {
        
        logger.info("Inventory reservation request for product: {}, order: {}", 
                   request.getProductId(), request.getOrderId());
        
        boolean reserved = inventoryService.reserveInventory(request);
        
        if (reserved) {
            return ResponseEntity.ok(
                ApiResponse.success("Inventory reserved successfully",
                    "Reserved " + request.getQuantity() + " units for order: " + request.getOrderId())
            );
        } else {
            return ResponseEntity.status(HttpStatus.CONFLICT)
                .body(ApiResponse.error("Unable to reserve inventory - insufficient stock or product not available"));
        }
    }
    
    @PostMapping("/release")
    public ResponseEntity<ApiResponse<String>> releaseReservation(
            @RequestParam @NotBlank String orderId,
            @RequestParam @NotBlank String productId,
            @RequestParam @Positive Integer quantity) {
        
        logger.info("Release reservation request for order: {}, product: {}", 
                   orderId, productId);
        
        boolean released = inventoryService.releaseReservation(orderId, productId, quantity);
        
        if (released) {
            return ResponseEntity.ok(
                ApiResponse.success("Reservation released successfully",
                    "Released reservation for order: " + orderId)
            );
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                .body(ApiResponse.error("Product not found or reservation not found"));
        }
    }
    
    @GetMapping("/metrics")
    public ResponseEntity<ApiResponse<InventoryMetrics>> getMetrics() {
        logger.info("Metrics request received");
        
        InventoryMetrics metrics = inventoryService.getInventoryMetrics();
        
        return ResponseEntity.ok(
            ApiResponse.success(metrics, "Inventory metrics generated successfully")
        );
    }
    
    @GetMapping("/categories")
    public ResponseEntity<ApiResponse<List<String>>> getCategories() {
        List<String> categories = Arrays.stream(ProductCategory.values())
            .map(ProductCategory::name)
            .collect(Collectors.toList());
        
        return ResponseEntity.ok(
            ApiResponse.success(categories, "Available product categories")
        );
    }
    
    // Exception handling
    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiResponse<String>> handleException(Exception e) {
        logger.error("Unhandled exception occurred", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
            .body(ApiResponse.error("Internal server error: " + e.getMessage()));
    }
}