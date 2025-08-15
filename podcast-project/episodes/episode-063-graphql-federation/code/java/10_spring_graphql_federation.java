// 10_spring_graphql_federation.java
// Spring Boot के साथ GraphQL Federation implementation
// Enterprise-grade GraphQL federation for Indian e-commerce systems

package com.flipkart.graphql.federation;

import com.apollographql.federation.graphqljava.Federation;
import com.apollographql.federation.graphqljava._Entity;
import com.apollographql.federation.graphqljava.tracing.FederatedTracingInstrumentation;
import graphql.GraphQL;
import graphql.execution.instrumentation.ChainedInstrumentation;
import graphql.execution.instrumentation.Instrumentation;
import graphql.execution.instrumentation.dataloader.DataLoaderDispatcherInstrumentation;
import graphql.execution.instrumentation.tracing.TracingInstrumentation;
import graphql.schema.GraphQLSchema;
import graphql.schema.idl.RuntimeWiring;
import graphql.schema.idl.SchemaGenerator;
import graphql.schema.idl.SchemaParser;
import graphql.schema.idl.TypeDefinitionRegistry;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.bind.annotation.*;
import org.springframework.stereotype.Service;
import org.springframework.stereotype.Component;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.cache.annotation.EnableCaching;

import org.dataloader.DataLoader;
import org.dataloader.DataLoaderFactory;
import org.dataloader.DataLoaderRegistry;
import org.dataloader.BatchLoader;

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.stream.Collectors;

import javax.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Spring Boot GraphQL Federation Service
 * यह service e-commerce के products को handle करती है Federation के through
 * 
 * Features:
 * - Apollo Federation support
 * - DataLoader for N+1 problem resolution 
 * - Caching for performance
 * - Indian e-commerce context
 * - Production-ready error handling
 * - Metrics and monitoring
 */
@SpringBootApplication
@EnableCaching
public class SpringGraphQLFederationApplication {
    
    private static final Logger logger = LoggerFactory.getLogger(SpringGraphQLFederationApplication.class);
    
    public static void main(String[] args) {
        logger.info("🚀 Starting Flipkart GraphQL Federation Service...");
        logger.info("🇮🇳 Serving पूरे भारत में customers को products की जानकारी");
        SpringApplication.run(SpringGraphQLFederationApplication.class, args);
    }
}

/**
 * Product Entity for Federation
 * यह entity दूसरी services से reference हो सकती है
 */
class Product {
    private String id;
    private String name;
    private Double price;
    private String category;
    private String brand;
    private String sellerId;
    private String description;
    private Boolean inStock;
    private Integer stockCount;
    private List<String> imageUrls;
    private String createdAt;
    private String updatedAt;
    
    // Constructors
    public Product() {}
    
    public Product(String id, String name, Double price, String category, String brand, String sellerId) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.category = category;
        this.brand = brand;
        this.sellerId = sellerId;
        this.inStock = true;
        this.stockCount = 100;
        this.imageUrls = new ArrayList<>();
        this.createdAt = new Date().toString();
        this.updatedAt = new Date().toString();
    }
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public Double getPrice() { return price; }
    public void setPrice(Double price) { this.price = price; }
    
    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }
    
    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }
    
    public String getSellerId() { return sellerId; }
    public void setSellerId(String sellerId) { this.sellerId = sellerId; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public Boolean getInStock() { return inStock; }
    public void setInStock(Boolean inStock) { this.inStock = inStock; }
    
    public Integer getStockCount() { return stockCount; }
    public void setStockCount(Integer stockCount) { this.stockCount = stockCount; }
    
    public List<String> getImageUrls() { return imageUrls; }
    public void setImageUrls(List<String> imageUrls) { this.imageUrls = imageUrls; }
    
    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
    
    public String getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(String updatedAt) { this.updatedAt = updatedAt; }
    
    @Override
    public String toString() {
        return String.format("Product{id='%s', name='%s', price=%.2f, brand='%s'}", 
                           id, name, price, brand);
    }
}

/**
 * Seller Entity - Federation के लिए
 */
class Seller {
    private String id;
    private String name;
    private String email;
    private String businessName;
    private String city;
    private String state;
    private String gstNumber;
    private Double rating;
    private Integer totalProducts;
    
    public Seller() {}
    
    public Seller(String id, String name, String businessName, String city) {
        this.id = id;
        this.name = name;
        this.businessName = businessName;
        this.city = city;
        this.rating = 4.2;
        this.totalProducts = 0;
    }
    
    // Getters and Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getBusinessName() { return businessName; }
    public void setBusinessName(String businessName) { this.businessName = businessName; }
    
    public String getCity() { return city; }
    public void setCity(String city) { this.city = city; }
    
    public String getState() { return state; }
    public void setState(String state) { this.state = state; }
    
    public String getGstNumber() { return gstNumber; }
    public void setGstNumber(String gstNumber) { this.gstNumber = gstNumber; }
    
    public Double getRating() { return rating; }
    public void setRating(Double rating) { this.rating = rating; }
    
    public Integer getTotalProducts() { return totalProducts; }
    public void setTotalProducts(Integer totalProducts) { this.totalProducts = totalProducts; }
}

/**
 * Product Service - Business Logic
 * यहाँ सारी product related operations होंगी
 */
@Service
public class ProductService {
    
    private static final Logger logger = LoggerFactory.getLogger(ProductService.class);
    
    // Mock database - Production में proper database होगा
    private final Map<String, Product> productDatabase = new HashMap<>();
    private final Map<String, Seller> sellerDatabase = new HashMap<>();
    
    @PostConstruct
    public void initializeData() {
        logger.info("🏪 Initializing Indian e-commerce product data...");
        
        // Initialize sellers from different cities
        sellerDatabase.put("1", new Seller("1", "राज शर्मा", "Raj Electronics", "Delhi"));
        sellerDatabase.put("2", new Seller("2", "प्रिया पटेल", "Priya Fashion Hub", "Ahmedabad"));
        sellerDatabase.put("3", new Seller("3", "अमित कुमार", "Kumar Tech Store", "Bangalore"));
        sellerDatabase.put("4", new Seller("4", "सुनीता देवी", "Sunita Handicrafts", "Jaipur"));
        sellerDatabase.put("5", new Seller("5", "विकास गुप्ता", "Gupta Books & More", "Kolkata"));
        
        // Initialize products
        initializeProducts();
        
        logger.info("✅ Initialized {} products और {} sellers", 
                   productDatabase.size(), sellerDatabase.size());
    }
    
    private void initializeProducts() {
        // Electronics - Delhi seller
        productDatabase.put("1", createProduct("1", "iPhone 15 Pro Max", 159900.0, 
                          "Electronics", "Apple", "1", 
                          "Apple का flagship phone with titanium design और advanced cameras"));
        
        productDatabase.put("2", createProduct("2", "Samsung Galaxy S24 Ultra", 124999.0, 
                          "Electronics", "Samsung", "1", 
                          "Samsung का premium phone with S Pen और excellent display"));
        
        productDatabase.put("3", createProduct("3", "OnePlus 12", 64999.0, 
                          "Electronics", "OnePlus", "3", 
                          "Never Settle! OnePlus का latest flagship with Snapdragon 8 Gen 3"));
        
        // Fashion - Ahmedabad seller
        productDatabase.put("4", createProduct("4", "Banarasi Silk Saree", 8999.0, 
                          "Fashion", "Traditional Weavers", "2", 
                          "हाथ से बुनी गई बनारसी साड़ी - शादी और त्योहारों के लिए perfect"));
        
        productDatabase.put("5", createProduct("5", "Khadi Cotton Kurta", 1299.0, 
                          "Fashion", "Khadi Gram", "2", 
                          "Pure cotton khadi kurta - comfortable और eco-friendly"));
        
        // Books - Kolkata seller
        productDatabase.put("6", createProduct("6", "Geetanjali by Rabindranath Tagore", 299.0, 
                          "Books", "Sahitya Akademi", "5", 
                          "Nobel Prize winner की immortal poetry collection"));
        
        productDatabase.put("7", createProduct("7", "Design Patterns (Hindi Edition)", 599.0, 
                          "Books", "Tech Publications", "5", 
                          "Software engineering के fundamental design patterns - Hindi में"));
        
        // Handicrafts - Jaipur seller
        productDatabase.put("8", createProduct("8", "Rajasthani Blue Pottery Set", 2499.0, 
                          "Handicrafts", "Jaipur Artisans", "4", 
                          "Hand-painted blue pottery dinnerware set - authentic Rajasthani craft"));
        
        productDatabase.put("9", createProduct("9", "Madhubani Painting", 1899.0, 
                          "Art", "Bihar Folk Artists", "4", 
                          "Traditional Madhubani art piece - brings Indian culture to your home"));
        
        // More tech products - Bangalore seller  
        productDatabase.put("10", createProduct("10", "MacBook Air M2", 114900.0, 
                           "Electronics", "Apple", "3", 
                           "Apple MacBook Air with M2 chip - perfect for developers"));
    }
    
    private Product createProduct(String id, String name, Double price, String category, 
                                String brand, String sellerId, String description) {
        Product product = new Product(id, name, price, category, brand, sellerId);
        product.setDescription(description);
        
        // Set stock based on price range
        if (price > 100000) {
            product.setStockCount(5); // Expensive items - limited stock
        } else if (price > 10000) {
            product.setStockCount(25); // Medium price - moderate stock
        } else {
            product.setStockCount(100); // Affordable items - good stock
        }
        
        return product;
    }
    
    /**
     * Get all products with pagination
     */
    @Cacheable("products")
    public List<Product> getAllProducts(Integer limit, Integer offset) {
        logger.info("📦 Fetching products: limit={}, offset={}", limit, offset);
        
        List<Product> allProducts = new ArrayList<>(productDatabase.values());
        
        // Apply pagination
        int startIndex = Math.min(offset, allProducts.size());
        int endIndex = Math.min(offset + limit, allProducts.size());
        
        List<Product> result = allProducts.subList(startIndex, endIndex);
        
        logger.info("✅ Returning {} products", result.size());
        return result;
    }
    
    /**
     * Get product by ID
     */
    @Cacheable("product")
    public Product getProductById(String id) {
        logger.info("🎯 Fetching product by ID: {}", id);
        
        Product product = productDatabase.get(id);
        if (product == null) {
            logger.warn("❌ Product not found: {}", id);
        } else {
            logger.info("✅ Found product: {}", product.getName());
        }
        
        return product;
    }
    
    /**
     * Get products by IDs (for DataLoader)
     */
    public CompletionStage<List<Product>> getProductsByIds(List<String> ids) {
        logger.info("📦 Batch loading products: {}", ids);
        
        return CompletableFuture.supplyAsync(() -> {
            List<Product> products = ids.stream()
                .map(productDatabase::get)
                .collect(Collectors.toList());
            
            logger.info("✅ Batch loaded {} products", products.size());
            return products;
        });
    }
    
    /**
     * Search products by name/brand/category
     */
    public List<Product> searchProducts(String query, Integer limit) {
        logger.info("🔍 Searching products: query='{}', limit={}", query, limit);
        
        String searchTerm = query.toLowerCase().trim();
        
        List<Product> results = productDatabase.values().stream()
            .filter(product -> 
                product.getName().toLowerCase().contains(searchTerm) ||
                product.getBrand().toLowerCase().contains(searchTerm) ||
                product.getCategory().toLowerCase().contains(searchTerm) ||
                (product.getDescription() != null && 
                 product.getDescription().toLowerCase().contains(searchTerm))
            )
            .limit(limit)
            .collect(Collectors.toList());
        
        logger.info("✅ Search found {} products for '{}'", results.size(), query);
        return results;
    }
    
    /**
     * Get products by category
     */
    public List<Product> getProductsByCategory(String category, Integer limit) {
        logger.info("📂 Fetching products by category: {}, limit: {}", category, limit);
        
        List<Product> results = productDatabase.values().stream()
            .filter(product -> product.getCategory().equalsIgnoreCase(category))
            .limit(limit)
            .collect(Collectors.toList());
        
        logger.info("✅ Found {} products in category '{}'", results.size(), category);
        return results;
    }
    
    /**
     * Get products by seller
     */
    public List<Product> getProductsBySeller(String sellerId) {
        logger.info("🏪 Fetching products by seller: {}", sellerId);
        
        List<Product> results = productDatabase.values().stream()
            .filter(product -> product.getSellerId().equals(sellerId))
            .collect(Collectors.toList());
        
        logger.info("✅ Found {} products for seller {}", results.size(), sellerId);
        return results;
    }
    
    /**
     * Get seller by ID
     */
    @Cacheable("seller")
    public Seller getSellerById(String id) {
        logger.info("👨‍💼 Fetching seller by ID: {}", id);
        
        Seller seller = sellerDatabase.get(id);
        if (seller != null) {
            // Update product count
            long productCount = productDatabase.values().stream()
                .filter(p -> p.getSellerId().equals(id))
                .count();
            seller.setTotalProducts((int) productCount);
        }
        
        return seller;
    }
    
    /**
     * Get sellers by IDs (for DataLoader)
     */
    public CompletionStage<List<Seller>> getSellersByIds(List<String> ids) {
        logger.info("👥 Batch loading sellers: {}", ids);
        
        return CompletableFuture.supplyAsync(() -> {
            List<Seller> sellers = ids.stream()
                .map(this::getSellerById)
                .collect(Collectors.toList());
            
            logger.info("✅ Batch loaded {} sellers", sellers.size());
            return sellers;
        });
    }
}

/**
 * DataLoader Configuration
 * N+1 problem को solve करने के लिए
 */
@Component
public class DataLoaderConfiguration {
    
    private final ProductService productService;
    
    public DataLoaderConfiguration(ProductService productService) {
        this.productService = productService;
    }
    
    /**
     * Product DataLoader
     */
    public DataLoader<String, Product> createProductDataLoader() {
        BatchLoader<String, Product> batchLoader = ids -> {
            return productService.getProductsByIds(ids);
        };
        
        return DataLoaderFactory.newDataLoader(batchLoader);
    }
    
    /**
     * Seller DataLoader
     */
    public DataLoader<String, Seller> createSellerDataLoader() {
        BatchLoader<String, Seller> batchLoader = ids -> {
            return productService.getSellersByIds(ids);
        };
        
        return DataLoaderFactory.newDataLoader(batchLoader);
    }
    
    /**
     * DataLoader Registry
     */
    public DataLoaderRegistry createDataLoaderRegistry() {
        DataLoaderRegistry registry = new DataLoaderRegistry();
        
        registry.register("products", createProductDataLoader());
        registry.register("sellers", createSellerDataLoader());
        
        return registry;
    }
}

/**
 * GraphQL Configuration
 * Federation schema और resolvers setup
 */
@Configuration
public class GraphQLConfig {
    
    private static final Logger logger = LoggerFactory.getLogger(GraphQLConfig.class);
    
    private final ProductService productService;
    private final DataLoaderConfiguration dataLoaderConfig;
    
    public GraphQLConfig(ProductService productService, DataLoaderConfiguration dataLoaderConfig) {
        this.productService = productService;
        this.dataLoaderConfig = dataLoaderConfig;
    }
    
    /**
     * GraphQL Schema Definition
     */
    private static final String SCHEMA = """
        # Federation directives
        directive @key(fields: String!) on OBJECT | INTERFACE
        directive @external on FIELD_DEFINITION
        directive @requires(fields: String!) on FIELD_DEFINITION
        directive @provides(fields: String!) on FIELD_DEFINITION
        
        # Product Entity - Federation key
        type Product @key(fields: "id") {
            id: ID!
            name: String!
            price: Float!
            category: String!
            brand: String!
            sellerId: ID!
            description: String
            inStock: Boolean!
            stockCount: Int!
            imageUrls: [String!]!
            createdAt: String!
            updatedAt: String!
            
            # Resolved from other services
            seller: Seller!
        }
        
        # Seller Entity - Federation key
        type Seller @key(fields: "id") {
            id: ID!
            name: String!
            businessName: String
            city: String
            rating: Float
            totalProducts: Int!
            
            # Products sold by this seller
            products: [Product!]!
        }
        
        type Query {
            # Product queries
            products(limit: Int = 10, offset: Int = 0): [Product!]!
            product(id: ID!): Product
            searchProducts(query: String!, limit: Int = 20): [Product!]!
            productsByCategory(category: String!, limit: Int = 10): [Product!]!
            
            # Seller queries
            seller(id: ID!): Seller
            
            # Health check
            _service: _Service!
        }
        
        # Federation service info
        type _Service {
            sdl: String!
        }
        """;
    
    @Bean
    public GraphQL graphQL() {
        logger.info("🏗️ Building GraphQL Federation schema...");
        
        // Parse schema
        SchemaParser schemaParser = new SchemaParser();
        TypeDefinitionRegistry typeRegistry = schemaParser.parse(SCHEMA);
        
        // Runtime wiring with resolvers
        RuntimeWiring runtimeWiring = RuntimeWiring.newRuntimeWiring()
            .type("Query", builder -> builder
                .dataFetcher("products", env -> {
                    Integer limit = env.getArgument("limit");
                    Integer offset = env.getArgument("offset");
                    return productService.getAllProducts(limit, offset);
                })
                .dataFetcher("product", env -> {
                    String id = env.getArgument("id");
                    return productService.getProductById(id);
                })
                .dataFetcher("searchProducts", env -> {
                    String query = env.getArgument("query");
                    Integer limit = env.getArgument("limit");
                    return productService.searchProducts(query, limit);
                })
                .dataFetcher("productsByCategory", env -> {
                    String category = env.getArgument("category");
                    Integer limit = env.getArgument("limit");
                    return productService.getProductsByCategory(category, limit);
                })
                .dataFetcher("seller", env -> {
                    String id = env.getArgument("id");
                    return productService.getSellerById(id);
                })
                .dataFetcher("_service", env -> {
                    Map<String, Object> service = new HashMap<>();
                    service.put("sdl", SCHEMA);
                    return service;
                })
            )
            .type("Product", builder -> builder
                .dataFetcher("seller", env -> {
                    Product product = env.getSource();
                    DataLoaderRegistry registry = env.getDataLoaderRegistry();
                    DataLoader<String, Seller> sellerLoader = registry.getDataLoader("sellers");
                    
                    return sellerLoader.load(product.getSellerId());
                })
            )
            .type("Seller", builder -> builder
                .dataFetcher("products", env -> {
                    Seller seller = env.getSource();
                    return productService.getProductsBySeller(seller.getId());
                })
            )
            // Federation entity resolver
            .type("_Entity", builder -> builder
                .typeResolver(env -> {
                    Object src = env.getObject();
                    if (src instanceof Product) {
                        return env.getSchema().getObjectType("Product");
                    } else if (src instanceof Seller) {
                        return env.getSchema().getObjectType("Seller");
                    }
                    return null;
                })
            )
            .build();
        
        // Build federated schema
        GraphQLSchema federatedSchema = Federation.transform(typeRegistry, runtimeWiring)
            .fetchEntities(env -> {
                List<Map<String, Object>> representations = env.getArgument(_Entity.argumentName);
                
                return representations.stream().map(representation -> {
                    String typename = (String) representation.get("__typename");
                    String id = (String) representation.get("id");
                    
                    if ("Product".equals(typename)) {
                        return productService.getProductById(id);
                    } else if ("Seller".equals(typename)) {
                        return productService.getSellerById(id);
                    }
                    return null;
                }).collect(Collectors.toList());
            })
            .resolveEntityType(env -> {
                Object src = env.getObject();
                if (src instanceof Product) {
                    return env.getSchema().getObjectType("Product");
                } else if (src instanceof Seller) {
                    return env.getSchema().getObjectType("Seller");
                }
                return null;
            })
            .build();
        
        // Add instrumentation for tracing, data loaders
        List<Instrumentation> instrumentations = Arrays.asList(
            new FederatedTracingInstrumentation(),
            new DataLoaderDispatcherInstrumentation(),
            new TracingInstrumentation()
        );
        
        GraphQL graphQLInstance = GraphQL.newGraphQL(federatedSchema)
            .instrumentation(new ChainedInstrumentation(instrumentations))
            .build();
        
        logger.info("✅ GraphQL Federation schema built successfully");
        return graphQLInstance;
    }
}

/**
 * REST Controller for GraphQL
 */
@RestController
@RequestMapping("/graphql")
public class GraphQLController {
    
    private static final Logger logger = LoggerFactory.getLogger(GraphQLController.class);
    
    private final GraphQL graphQL;
    private final DataLoaderConfiguration dataLoaderConfig;
    
    public GraphQLController(GraphQL graphQL, DataLoaderConfiguration dataLoaderConfig) {
        this.graphQL = graphQL;
        this.dataLoaderConfig = dataLoaderConfig;
    }
    
    @PostMapping
    public Map<String, Object> graphql(@RequestBody Map<String, Object> body,
                                     @RequestHeader Map<String, String> headers) {
        
        String query = (String) body.get("query");
        String operationName = (String) body.get("operationName");
        Map<String, Object> variables = (Map<String, Object>) body.get("variables");
        
        logger.info("📞 GraphQL Request: operation={}, query preview={}", 
                   operationName != null ? operationName : "Anonymous",
                   query != null ? query.substring(0, Math.min(100, query.length())) + "..." : "");
        
        // Create execution context
        Map<String, Object> context = new HashMap<>();
        context.put("headers", headers);
        
        // User context from headers (simplified auth)
        String userId = headers.get("x-user-id");
        String userRole = headers.get("x-user-role");
        if (userId != null) {
            Map<String, String> user = new HashMap<>();
            user.put("id", userId);
            user.put("role", userRole != null ? userRole : "customer");
            context.put("user", user);
        }
        
        // Execute query
        long startTime = System.currentTimeMillis();
        
        var executionResult = graphQL.executeAsync(builder -> builder
            .query(query)
            .operationName(operationName)
            .variables(variables != null ? variables : new HashMap<>())
            .context(context)
            .dataLoaderRegistry(dataLoaderConfig.createDataLoaderRegistry())
        ).join();
        
        long endTime = System.currentTimeMillis();
        long executionTime = endTime - startTime;
        
        // Build response
        Map<String, Object> response = new HashMap<>();
        response.put("data", executionResult.getData());
        
        if (executionResult.getErrors() != null && !executionResult.getErrors().isEmpty()) {
            response.put("errors", executionResult.getErrors());
            logger.error("❌ GraphQL Errors: {}", executionResult.getErrors());
        }
        
        // Add extensions
        Map<String, Object> extensions = new HashMap<>();
        extensions.put("executionTime", executionTime + "ms");
        extensions.put("timestamp", new Date().toString());
        response.put("extensions", extensions);
        
        logger.info("✅ GraphQL Response completed in {}ms, hasData={}, hasErrors={}", 
                   executionTime, 
                   executionResult.getData() != null,
                   executionResult.getErrors() != null && !executionResult.getErrors().isEmpty());
        
        return response;
    }
    
    @GetMapping("/health")
    public Map<String, Object> health() {
        Map<String, Object> health = new HashMap<>();
        health.put("service", "products-federation-service");
        health.put("status", "healthy");
        health.put("timestamp", new Date().toString());
        health.put("features", Arrays.asList(
            "Apollo Federation",
            "DataLoader batching",
            "Caching support",
            "Indian e-commerce context",
            "Production monitoring"
        ));
        
        return health;
    }
    
    @GetMapping("/info")
    public Map<String, Object> info() {
        Map<String, Object> info = new HashMap<>();
        info.put("service_name", "Flipkart Products Federation Service");
        info.put("description", "GraphQL Federation service for Indian e-commerce products");
        info.put("version", "1.0.0");
        info.put("endpoints", Arrays.asList(
            "POST /graphql - GraphQL queries and mutations",
            "GET /graphql/health - Health check",
            "GET /graphql/info - Service information"
        ));
        
        info.put("sample_queries", Map.of(
            "all_products", "{ products(limit: 5) { id name price brand } }",
            "search", "{ searchProducts(query: \"iPhone\") { id name price } }",
            "with_seller", "{ products(limit: 3) { name seller { name businessName city } } }",
            "by_category", "{ productsByCategory(category: \"Electronics\") { name price } }"
        ));
        
        info.put("federation_features", Arrays.asList(
            "Entity resolution",
            "Cross-service references", 
            "Type extensions",
            "Federated tracing"
        ));
        
        info.put("indian_context", Arrays.asList(
            "Multi-language product names",
            "City-wise seller information",
            "Indian currency (INR) pricing",
            "Regional product categories"
        ));
        
        return info;
    }
}

/**
 * Error Handling और Monitoring
 */
@Component
class GraphQLMetrics {
    
    private static final Logger logger = LoggerFactory.getLogger(GraphQLMetrics.class);
    
    // Simple in-memory metrics (Production में proper metrics system use करेंगे)
    private long totalQueries = 0;
    private long totalErrors = 0;
    private double avgExecutionTime = 0;
    private Map<String, Long> queryFrequency = new HashMap<>();
    
    public void recordQuery(String operationName, long executionTime, boolean hasErrors) {
        totalQueries++;
        
        if (hasErrors) {
            totalErrors++;
        }
        
        // Update average execution time
        avgExecutionTime = (avgExecutionTime * (totalQueries - 1) + executionTime) / totalQueries;
        
        // Update query frequency
        String operation = operationName != null ? operationName : "Anonymous";
        queryFrequency.put(operation, queryFrequency.getOrDefault(operation, 0L) + 1);
        
        logger.debug("📊 Metrics updated: total={}, errors={}, avgTime={}ms", 
                    totalQueries, totalErrors, Math.round(avgExecutionTime));
    }
    
    public Map<String, Object> getMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        metrics.put("total_queries", totalQueries);
        metrics.put("total_errors", totalErrors);
        metrics.put("error_rate", totalQueries > 0 ? (double) totalErrors / totalQueries : 0);
        metrics.put("avg_execution_time_ms", Math.round(avgExecutionTime));
        metrics.put("query_frequency", queryFrequency);
        
        return metrics;
    }
}