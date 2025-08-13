/**
 * Versioned API Gateway System
 * वर्जन्ड एपीआई गेटवे सिस्टम
 * 
 * Real-world example: PayTM API Gateway for handling multiple API versions
 * Handles request routing based on version headers, URL paths, and content negotiation
 */

package com.paytm.gateway.versioning;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

/**
 * API Version metadata
 */
class ApiVersion {
    private final String version;
    private final String description;
    private final LocalDateTime deprecationDate;
    private final LocalDateTime sunsetDate;
    private final boolean isDefault;
    private final Map<String, String> migrationGuides;
    
    public ApiVersion(String version, String description, LocalDateTime deprecationDate, 
                     LocalDateTime sunsetDate, boolean isDefault) {
        this.version = version;
        this.description = description;
        this.deprecationDate = deprecationDate;
        this.sunsetDate = sunsetDate;
        this.isDefault = isDefault;
        this.migrationGuides = new HashMap<>();
    }
    
    // Getters
    public String getVersion() { return version; }
    public String getDescription() { return description; }
    public LocalDateTime getDeprecationDate() { return deprecationDate; }
    public LocalDateTime getSunsetDate() { return sunsetDate; }
    public boolean isDefault() { return isDefault; }
    public Map<String, String> getMigrationGuides() { return migrationGuides; }
    
    public boolean isDeprecated() {
        return deprecationDate != null && LocalDateTime.now().isAfter(deprecationDate);
    }
    
    public boolean isSunset() {
        return sunsetDate != null && LocalDateTime.now().isAfter(sunsetDate);
    }
}

/**
 * API Route configuration
 */
class ApiRoute {
    private final String path;
    private final String method;
    private final String serviceName;
    private final String endpoint;
    private final Set<String> supportedVersions;
    
    public ApiRoute(String path, String method, String serviceName, 
                   String endpoint, Set<String> supportedVersions) {
        this.path = path;
        this.method = method;
        this.serviceName = serviceName;
        this.endpoint = endpoint;
        this.supportedVersions = new HashSet<>(supportedVersions);
    }
    
    // Getters
    public String getPath() { return path; }
    public String getMethod() { return method; }
    public String getServiceName() { return serviceName; }
    public String getEndpoint() { return endpoint; }
    public Set<String> getSupportedVersions() { return supportedVersions; }
}

/**
 * HTTP Request representation
 */
class HttpRequest {
    private final String method;
    private final String path;
    private final Map<String, String> headers;
    private final Map<String, String> queryParams;
    private final String body;
    
    public HttpRequest(String method, String path, Map<String, String> headers,
                      Map<String, String> queryParams, String body) {
        this.method = method;
        this.path = path;
        this.headers = new HashMap<>(headers);
        this.queryParams = new HashMap<>(queryParams);
        this.body = body;
    }
    
    // Getters
    public String getMethod() { return method; }
    public String getPath() { return path; }
    public Map<String, String> getHeaders() { return headers; }
    public Map<String, String> getQueryParams() { return queryParams; }
    public String getBody() { return body; }
}

/**
 * HTTP Response representation
 */
class HttpResponse {
    private final int statusCode;
    private final Map<String, String> headers;
    private final String body;
    
    public HttpResponse(int statusCode, Map<String, String> headers, String body) {
        this.statusCode = statusCode;
        this.headers = new HashMap<>(headers);
        this.body = body;
    }
    
    // Getters
    public int getStatusCode() { return statusCode; }
    public Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
}

/**
 * Version Resolution Result
 */
class VersionResolutionResult {
    private final String resolvedVersion;
    private final String source; // header, url, query, default
    private final boolean isDeprecated;
    private final boolean isSunset;
    private final String migrationGuide;
    
    public VersionResolutionResult(String resolvedVersion, String source, 
                                 boolean isDeprecated, boolean isSunset, String migrationGuide) {
        this.resolvedVersion = resolvedVersion;
        this.source = source;
        this.isDeprecated = isDeprecated;
        this.isSunset = isSunset;
        this.migrationGuide = migrationGuide;
    }
    
    // Getters
    public String getResolvedVersion() { return resolvedVersion; }
    public String getSource() { return source; }
    public boolean isDeprecated() { return isDeprecated; }
    public boolean isSunset() { return isSunset; }
    public String getMigrationGuide() { return migrationGuide; }
}

/**
 * PayTM-style Versioned API Gateway
 * PayTM-स्टाइल वर्जन्ड एपीआई गेटवे
 */
public class VersionedApiGateway {
    
    private final Map<String, ApiVersion> versions;
    private final Map<String, ApiRoute> routes;
    private final String defaultVersion;
    private final Map<String, Integer> versionUsageStats;
    
    // Version extraction patterns
    private final Pattern urlVersionPattern = Pattern.compile("/v(\\d+(?:\\.\\d+)*)/.*");
    private final Pattern semanticVersionPattern = Pattern.compile("\\d+\\.\\d+\\.\\d+");
    
    public VersionedApiGateway() {
        this.versions = new ConcurrentHashMap<>();
        this.routes = new ConcurrentHashMap<>();
        this.defaultVersion = "2.1.0";
        this.versionUsageStats = new ConcurrentHashMap<>();
        
        initializeVersions();
        initializeRoutes();
    }
    
    /**
     * Initialize API versions - एपीआई वर्जन इनिशियलाइज़ करें
     */
    private void initializeVersions() {
        System.out.println("🔧 Initializing API versions for PayTM gateway...");
        
        // Version 1.0.0 - Legacy UPI
        versions.put("1.0.0", new ApiVersion(
            "1.0.0",
            "Legacy UPI payment API - लेगेसी यूपीआई पेमेंट एपीआई",
            LocalDateTime.now().plusDays(30), // Deprecation in 30 days
            LocalDateTime.now().plusDays(90), // Sunset in 90 days
            false
        ));
        
        // Version 2.0.0 - Enhanced UPI with QR
        versions.put("2.0.0", new ApiVersion(
            "2.0.0",
            "Enhanced UPI with QR support - QR सपोर्ट के साथ एन्हांस्ड यूपीआई",
            LocalDateTime.now().plusDays(180), // Deprecation in 6 months
            LocalDateTime.now().plusDays(365), // Sunset in 1 year
            false
        ));
        
        // Version 2.1.0 - Current stable
        versions.put("2.1.0", new ApiVersion(
            "2.1.0",
            "Current stable with fraud detection - फ्रॉड डिटेक्शन के साथ करंट स्टेबल",
            null, // Not deprecated
            null, // No sunset planned
            true  // Default version
        ));
        
        // Version 3.0.0 - Beta with CBDC support
        versions.put("3.0.0-beta", new ApiVersion(
            "3.0.0-beta",
            "Beta version with CBDC support - CBDC सपोर्ट के साथ बीटा वर्जन",
            null,
            null,
            false
        ));
    }
    
    /**
     * Initialize API routes - एपीआई रूट्स इनिशियलाइज़ करें
     */
    private void initializeRoutes() {
        System.out.println("🛤️ Setting up API routes...");
        
        // Payment initiation routes
        routes.put("POST:/payments", new ApiRoute(
            "/payments",
            "POST",
            "payment-service",
            "/api/payments/initiate",
            Set.of("1.0.0", "2.0.0", "2.1.0", "3.0.0-beta")
        ));
        
        // Payment status routes
        routes.put("GET:/payments/{id}", new ApiRoute(
            "/payments/{id}",
            "GET",
            "payment-service",
            "/api/payments/status",
            Set.of("1.0.0", "2.0.0", "2.1.0", "3.0.0-beta")
        ));
        
        // QR code generation (v2.0.0+)
        routes.put("POST:/qr/generate", new ApiRoute(
            "/qr/generate",
            "POST",
            "qr-service",
            "/api/qr/generate",
            Set.of("2.0.0", "2.1.0", "3.0.0-beta")
        ));
        
        // CBDC operations (v3.0.0+)
        routes.put("POST:/cbdc/transfer", new ApiRoute(
            "/cbdc/transfer",
            "POST",
            "cbdc-service",
            "/api/cbdc/transfer",
            Set.of("3.0.0-beta")
        ));
    }
    
    /**
     * Resolve API version from request - रिक्वेस्ट से एपीआई वर्जन रिज़ॉल्व करें
     */
    public VersionResolutionResult resolveVersion(HttpRequest request) {
        System.out.println("🔍 Resolving API version for: " + request.getMethod() + " " + request.getPath());
        
        String resolvedVersion = null;
        String source = null;
        
        // 1. Check URL path versioning (/v2.1/payments)
        Matcher urlMatcher = urlVersionPattern.matcher(request.getPath());
        if (urlMatcher.matches()) {
            String urlVersion = urlMatcher.group(1);
            resolvedVersion = findFullVersion(urlVersion);
            source = "url_path";
            System.out.println("📍 Version from URL path: " + resolvedVersion);
        }
        
        // 2. Check version header (API-Version: 2.1.0)
        if (resolvedVersion == null) {
            String headerVersion = request.getHeaders().get("API-Version");
            if (headerVersion != null && versions.containsKey(headerVersion)) {
                resolvedVersion = headerVersion;
                source = "header";
                System.out.println("📋 Version from header: " + resolvedVersion);
            }
        }
        
        // 3. Check Accept header content negotiation
        if (resolvedVersion == null) {
            String acceptHeader = request.getHeaders().get("Accept");
            if (acceptHeader != null) {
                resolvedVersion = parseVersionFromAcceptHeader(acceptHeader);
                source = "content_negotiation";
                if (resolvedVersion != null) {
                    System.out.println("🤝 Version from Accept header: " + resolvedVersion);
                }
            }
        }
        
        // 4. Check query parameter
        if (resolvedVersion == null) {
            String queryVersion = request.getQueryParams().get("version");
            if (queryVersion != null && versions.containsKey(queryVersion)) {
                resolvedVersion = queryVersion;
                source = "query_param";
                System.out.println("❓ Version from query parameter: " + resolvedVersion);
            }
        }
        
        // 5. Use default version
        if (resolvedVersion == null) {
            resolvedVersion = defaultVersion;
            source = "default";
            System.out.println("🎯 Using default version: " + resolvedVersion);
        }
        
        // Get version metadata
        ApiVersion version = versions.get(resolvedVersion);
        
        return new VersionResolutionResult(
            resolvedVersion,
            source,
            version != null ? version.isDeprecated() : false,
            version != null ? version.isSunset() : false,
            version != null ? version.getMigrationGuides().get("latest") : null
        );
    }
    
    /**
     * Route request to appropriate service - अप्रोप्रिएट सर्विस पर रिक्वेस्ट रूट करें
     */
    public HttpResponse routeRequest(HttpRequest request) {
        System.out.println("\n🚀 Processing request: " + request.getMethod() + " " + request.getPath());
        
        // Resolve version
        VersionResolutionResult versionResult = resolveVersion(request);
        String resolvedVersion = versionResult.getResolvedVersion();
        
        // Track version usage
        versionUsageStats.merge(resolvedVersion, 1, Integer::sum);
        
        // Check if version is sunset
        if (versionResult.isSunset()) {
            Map<String, String> errorHeaders = new HashMap<>();
            errorHeaders.put("X-API-Deprecated", "true");
            errorHeaders.put("X-API-Sunset", "true");
            
            return new HttpResponse(
                410, // Gone
                errorHeaders,
                "{\"error\": \"API version " + resolvedVersion + " has been sunset\", \"code\": \"VERSION_SUNSET\"}"
            );
        }
        
        // Find matching route
        String routeKey = request.getMethod() + ":" + extractRoutePattern(request.getPath());
        ApiRoute route = routes.get(routeKey);
        
        if (route == null) {
            return new HttpResponse(
                404,
                new HashMap<>(),
                "{\"error\": \"Route not found\", \"code\": \"ROUTE_NOT_FOUND\"}"
            );
        }
        
        // Check if version is supported by route
        if (!route.getSupportedVersions().contains(resolvedVersion)) {
            Map<String, String> errorHeaders = new HashMap<>();
            errorHeaders.put("X-Supported-Versions", String.join(", ", route.getSupportedVersions()));
            
            return new HttpResponse(
                400,
                errorHeaders,
                "{\"error\": \"Version " + resolvedVersion + " not supported for this endpoint\", \"code\": \"VERSION_NOT_SUPPORTED\"}"
            );
        }
        
        // Build response headers
        Map<String, String> responseHeaders = new HashMap<>();
        responseHeaders.put("X-API-Version", resolvedVersion);
        responseHeaders.put("X-Version-Source", versionResult.getSource());
        
        if (versionResult.isDeprecated()) {
            responseHeaders.put("X-API-Deprecated", "true");
            responseHeaders.put("X-API-Deprecation-Info", "This version will be sunset soon");
        }
        
        // Simulate service call based on version
        String responseBody = simulateServiceCall(route, resolvedVersion, request);
        
        System.out.println("✅ Request routed successfully to " + route.getServiceName());
        
        return new HttpResponse(200, responseHeaders, responseBody);
    }
    
    /**
     * Find full version from partial version - पार्शियल वर्जन से फुल वर्जन खोजें
     */
    private String findFullVersion(String partialVersion) {
        for (String fullVersion : versions.keySet()) {
            if (fullVersion.startsWith(partialVersion + ".")) {
                return fullVersion;
            }
        }
        return partialVersion + ".0"; // Default patch version
    }
    
    /**
     * Parse version from Accept header - Accept header से वर्जन पार्स करें
     */
    private String parseVersionFromAcceptHeader(String acceptHeader) {
        // Example: application/vnd.paytm.v2+json
        if (acceptHeader.contains("vnd.paytm.v")) {
            Pattern pattern = Pattern.compile("vnd\\.paytm\\.v(\\d+)");
            Matcher matcher = pattern.matcher(acceptHeader);
            if (matcher.find()) {
                return matcher.group(1) + ".0.0"; // Convert to semantic version
            }
        }
        return null;
    }
    
    /**
     * Extract route pattern from path - पाथ से रूट पैटर्न एक्सट्रैक्ट करें
     */
    private String extractRoutePattern(String path) {
        // Remove version prefix from path
        String cleanPath = urlVersionPattern.matcher(path).replaceFirst("");
        if (cleanPath.isEmpty()) {
            cleanPath = path;
        }
        
        // Convert path parameters to pattern
        return cleanPath.replaceAll("/\\w+", "/{id}");
    }
    
    /**
     * Simulate service call - सर्विस कॉल सिम्युलेट करें
     */
    private String simulateServiceCall(ApiRoute route, String version, HttpRequest request) {
        Map<String, Object> response = new HashMap<>();
        response.put("service", route.getServiceName());
        response.put("version", version);
        response.put("timestamp", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        
        // Version-specific response format
        switch (version) {
            case "1.0.0":
                response.put("data", Map.of(
                    "paymentId", "pay_" + System.currentTimeMillis(),
                    "status", "initiated",
                    "message", "Payment initiated via legacy API"
                ));
                break;
                
            case "2.0.0":
            case "2.1.0":
                response.put("data", Map.of(
                    "paymentId", "pay_" + System.currentTimeMillis(),
                    "status", "initiated",
                    "qrCode", "upi://pay?pa=merchant@paytm&am=100",
                    "fraudScore", 0.1,
                    "message", "Enhanced payment with QR and fraud detection"
                ));
                break;
                
            case "3.0.0-beta":
                response.put("data", Map.of(
                    "paymentId", "pay_" + System.currentTimeMillis(),
                    "status", "initiated",
                    "qrCode", "upi://pay?pa=merchant@paytm&am=100",
                    "fraudScore", 0.1,
                    "cbdcSupported", true,
                    "digitalRupeeId", "dr_" + System.currentTimeMillis(),
                    "message", "Beta payment with CBDC support"
                ));
                break;
        }
        
        return response.toString().replace("=", ":");
    }
    
    /**
     * Get version usage statistics - वर्जन यूसेज स्टैटिस्टिक्स प्राप्त करें
     */
    public Map<String, Integer> getVersionUsageStats() {
        return new HashMap<>(versionUsageStats);
    }
    
    /**
     * Get deprecated versions - डेप्रीकेटेड वर्जन प्राप्त करें
     */
    public List<String> getDeprecatedVersions() {
        return versions.values().stream()
                .filter(ApiVersion::isDeprecated)
                .map(ApiVersion::getVersion)
                .collect(ArrayList::new, (list, item) -> list.add(item), (list1, list2) -> list1.addAll(list2));
    }
    
    /**
     * Main demonstration method - मुख्य प्रदर्शन मेथड
     */
    public static void main(String[] args) {
        System.out.println("💰 PayTM API Gateway Versioning Demo");
        System.out.println("=====================================");
        
        VersionedApiGateway gateway = new VersionedApiGateway();
        
        // Test different versioning strategies
        
        // 1. URL path versioning
        HttpRequest request1 = new HttpRequest(
            "POST",
            "/v2/payments",
            Map.of("Content-Type", "application/json"),
            new HashMap<>(),
            "{\"amount\": 100, \"currency\": \"INR\"}"
        );
        
        System.out.println("\n🧪 Test 1: URL Path Versioning");
        HttpResponse response1 = gateway.routeRequest(request1);
        System.out.println("Response: " + response1.getStatusCode() + " - " + response1.getBody());
        
        // 2. Header-based versioning
        HttpRequest request2 = new HttpRequest(
            "GET",
            "/payments/pay_123456",
            Map.of("API-Version", "2.1.0", "Accept", "application/json"),
            new HashMap<>(),
            ""
        );
        
        System.out.println("\n🧪 Test 2: Header-based Versioning");
        HttpResponse response2 = gateway.routeRequest(request2);
        System.out.println("Response: " + response2.getStatusCode() + " - " + response2.getBody());
        
        // 3. Content negotiation
        HttpRequest request3 = new HttpRequest(
            "POST",
            "/qr/generate",
            Map.of("Accept", "application/vnd.paytm.v2+json"),
            new HashMap<>(),
            "{\"merchantId\": \"MERCHANT123\"}"
        );
        
        System.out.println("\n🧪 Test 3: Content Negotiation");
        HttpResponse response3 = gateway.routeRequest(request3);
        System.out.println("Response: " + response3.getStatusCode() + " - " + response3.getBody());
        
        // 4. Deprecated version
        HttpRequest request4 = new HttpRequest(
            "POST",
            "/payments",
            Map.of("API-Version", "1.0.0"),
            new HashMap<>(),
            "{\"amount\": 100}"
        );
        
        System.out.println("\n🧪 Test 4: Deprecated Version");
        HttpResponse response4 = gateway.routeRequest(request4);
        System.out.println("Response: " + response4.getStatusCode() + " - " + response4.getBody());
        System.out.println("Headers: " + response4.getHeaders());
        
        // 5. Version usage statistics
        System.out.println("\n📊 Version Usage Statistics:");
        gateway.getVersionUsageStats().forEach((version, count) -> 
            System.out.println("  " + version + ": " + count + " requests"));
        
        System.out.println("\n⚠️ Deprecated Versions:");
        gateway.getDeprecatedVersions().forEach(version -> 
            System.out.println("  - " + version));
    }
}