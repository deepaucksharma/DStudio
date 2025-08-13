package com.flipkart.cloudnative.servicemesh;

/**
 * Service Mesh Configuration for Flipkart Microservices
 * Cloud Native Service Mesh Pattern Implementation
 * 
 * Flipkart के microservices के बीच communication और security के लिए
 * Istio, Linkerd, और Consul Connect के साथ compatible
 */

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Consumer;
import java.util.logging.Logger;
import java.lang.annotation.*;

// Service Mesh Annotations
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ServiceMeshEnabled {
    String serviceName();
    String version() default "v1";
    boolean enableTLS() default true;
    boolean enableTracing() default true;
    String[] tags() default {};
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@interface CircuitBreaker {
    int failureThreshold() default 5;
    Duration timeout() default @Duration(seconds = 60);
    Class<? extends Exception>[] ignoreExceptions() default {};
}

@Target(ElementType.METHOD)  
@Retention(RetentionPolicy.RUNTIME)
@interface RateLimit {
    int requestsPerSecond();
    Duration window() default @Duration(seconds = 1);
}

@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
@interface Retry {
    int maxAttempts() default 3;
    Duration delay() default @Duration(seconds = 1);
    double backoffMultiplier() default 2.0;
}

// Service Mesh Core Classes
public class ServiceMeshConfiguration {
    private static final Logger logger = Logger.getLogger(ServiceMeshConfiguration.class.getName());
    
    // Service Discovery
    public static class ServiceRegistry {
        private final Map<String, List<ServiceInstance>> services = new ConcurrentHashMap<>();
        private final Map<String, HealthChecker> healthCheckers = new ConcurrentHashMap<>();
        private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
        
        public ServiceRegistry() {
            // Start health checking background task
            scheduler.scheduleAtFixedRate(this::performHealthChecks, 10, 30, TimeUnit.SECONDS);
            logger.info("🌐 Flipkart Service Registry initialized");
        }
        
        public void registerService(ServiceInstance instance) {
            String serviceName = instance.getServiceName();
            services.computeIfAbsent(serviceName, k -> new ArrayList<>()).add(instance);
            
            // Register health checker
            healthCheckers.put(instance.getId(), new HealthChecker(instance));
            
            logger.info(String.format("📝 Registered service: %s [%s:%d] - %s", 
                serviceName, instance.getHost(), instance.getPort(), instance.getId()));
        }
        
        public List<ServiceInstance> getHealthyInstances(String serviceName) {
            return services.getOrDefault(serviceName, Collections.emptyList())
                    .stream()
                    .filter(instance -> healthCheckers.get(instance.getId()).isHealthy())
                    .toList();
        }
        
        public ServiceInstance selectInstance(String serviceName, LoadBalancingStrategy strategy) {
            List<ServiceInstance> healthy = getHealthyInstances(serviceName);
            if (healthy.isEmpty()) {
                throw new RuntimeException("No healthy instances available for service: " + serviceName);
            }
            
            return strategy.select(healthy);
        }
        
        private void performHealthChecks() {
            healthCheckers.values().parallelStream().forEach(HealthChecker::checkHealth);
        }
        
        public Map<String, Integer> getServiceStats() {
            Map<String, Integer> stats = new HashMap<>();
            services.forEach((serviceName, instances) -> {
                long healthy = instances.stream()
                    .mapToLong(instance -> healthCheckers.get(instance.getId()).isHealthy() ? 1 : 0)
                    .sum();
                stats.put(serviceName + "_total", instances.size());
                stats.put(serviceName + "_healthy", (int) healthy);
            });
            return stats;
        }
    }
    
    // Service Instance
    public static class ServiceInstance {
        private final String id;
        private final String serviceName;
        private final String host;
        private final int port;
        private final Map<String, String> metadata;
        private final LocalDateTime registrationTime;
        
        public ServiceInstance(String serviceName, String host, int port) {
            this.id = UUID.randomUUID().toString();
            this.serviceName = serviceName;
            this.host = host;
            this.port = port;
            this.metadata = new HashMap<>();
            this.registrationTime = LocalDateTime.now();
            
            // Flipkart specific metadata
            this.metadata.put("datacenter", "mumbai-east-1");
            this.metadata.put("version", "v1.0");
            this.metadata.put("team", "platform-engineering");
        }
        
        // Getters
        public String getId() { return id; }
        public String getServiceName() { return serviceName; }
        public String getHost() { return host; }
        public int getPort() { return port; }
        public Map<String, String> getMetadata() { return metadata; }
        public LocalDateTime getRegistrationTime() { return registrationTime; }
        
        public String getEndpoint() {
            return String.format("http://%s:%d", host, port);
        }
        
        @Override
        public String toString() {
            return String.format("ServiceInstance{service='%s', host='%s', port=%d, id='%s'}", 
                serviceName, host, port, id);
        }
    }
    
    // Health Checker
    public static class HealthChecker {
        private final ServiceInstance instance;
        private volatile boolean healthy = true;
        private volatile LocalDateTime lastCheck = LocalDateTime.now();
        private final AtomicInteger consecutiveFailures = new AtomicInteger(0);
        
        public HealthChecker(ServiceInstance instance) {
            this.instance = instance;
        }
        
        public void checkHealth() {
            try {
                // Simplified health check - in production, make HTTP call to /health endpoint
                // For demo, simulate random failures
                boolean isHealthy = Math.random() > 0.05; // 95% success rate
                
                if (isHealthy) {
                    healthy = true;
                    consecutiveFailures.set(0);
                    logger.fine(String.format("✅ Health check passed: %s", instance.getId()));
                } else {
                    int failures = consecutiveFailures.incrementAndGet();
                    if (failures >= 3) {
                        healthy = false;
                        logger.warning(String.format("❌ Service unhealthy after %d failures: %s", 
                            failures, instance.getId()));
                    }
                }
                
                lastCheck = LocalDateTime.now();
                
            } catch (Exception e) {
                int failures = consecutiveFailures.incrementAndGet();
                if (failures >= 3) {
                    healthy = false;
                }
                logger.severe(String.format("❌ Health check error for %s: %s", 
                    instance.getId(), e.getMessage()));
            }
        }
        
        public boolean isHealthy() { return healthy; }
        public LocalDateTime getLastCheck() { return lastCheck; }
        public int getConsecutiveFailures() { return consecutiveFailures.get(); }
    }
    
    // Load Balancing Strategies
    public interface LoadBalancingStrategy {
        ServiceInstance select(List<ServiceInstance> instances);
    }
    
    public static class RoundRobinStrategy implements LoadBalancingStrategy {
        private final AtomicInteger counter = new AtomicInteger(0);
        
        @Override
        public ServiceInstance select(List<ServiceInstance> instances) {
            int index = Math.abs(counter.getAndIncrement() % instances.size());
            return instances.get(index);
        }
    }
    
    public static class RandomStrategy implements LoadBalancingStrategy {
        private final Random random = new Random();
        
        @Override
        public ServiceInstance select(List<ServiceInstance> instances) {
            return instances.get(random.nextInt(instances.size()));
        }
    }
    
    public static class LeastConnectionsStrategy implements LoadBalancingStrategy {
        private final Map<String, AtomicInteger> connections = new ConcurrentHashMap<>();
        
        @Override
        public ServiceInstance select(List<ServiceInstance> instances) {
            return instances.stream()
                .min(Comparator.comparingInt(instance -> 
                    connections.computeIfAbsent(instance.getId(), k -> new AtomicInteger(0)).get()))
                .orElse(instances.get(0));
        }
        
        public void incrementConnections(String instanceId) {
            connections.computeIfAbsent(instanceId, k -> new AtomicInteger(0)).incrementAndGet();
        }
        
        public void decrementConnections(String instanceId) {
            connections.computeIfAbsent(instanceId, k -> new AtomicInteger(0)).decrementAndGet();
        }
    }
    
    // Circuit Breaker Implementation
    public static class ServiceMeshCircuitBreaker {
        private enum State { CLOSED, OPEN, HALF_OPEN }
        
        private final String serviceName;
        private final int failureThreshold;
        private final Duration timeout;
        private volatile State state = State.CLOSED;
        private final AtomicInteger failureCount = new AtomicInteger(0);
        private final AtomicLong lastFailureTime = new AtomicLong(0);
        private final AtomicInteger requestCount = new AtomicInteger(0);
        private final AtomicInteger successCount = new AtomicInteger(0);
        
        public ServiceMeshCircuitBreaker(String serviceName, int failureThreshold, Duration timeout) {
            this.serviceName = serviceName;
            this.failureThreshold = failureThreshold;
            this.timeout = timeout;
            logger.info(String.format("🔌 Circuit breaker initialized for %s (threshold: %d, timeout: %s)",
                serviceName, failureThreshold, timeout));
        }
        
        public <T> T execute(Callable<T> operation) throws Exception {
            requestCount.incrementAndGet();
            
            // Check circuit state
            if (state == State.OPEN) {
                if (shouldAttemptReset()) {
                    state = State.HALF_OPEN;
                    logger.info(String.format("🟡 Circuit breaker HALF-OPEN for %s", serviceName));
                } else {
                    throw new RuntimeException(String.format("Circuit breaker OPEN for %s", serviceName));
                }
            }
            
            try {
                T result = operation.call();
                onSuccess();
                return result;
                
            } catch (Exception e) {
                onFailure();
                throw e;
            }
        }
        
        private boolean shouldAttemptReset() {
            return System.currentTimeMillis() - lastFailureTime.get() >= timeout.toMillis();
        }
        
        private void onSuccess() {
            successCount.incrementAndGet();
            failureCount.set(0);
            
            if (state == State.HALF_OPEN) {
                state = State.CLOSED;
                logger.info(String.format("🟢 Circuit breaker CLOSED for %s", serviceName));
            }
        }
        
        private void onFailure() {
            int failures = failureCount.incrementAndGet();
            lastFailureTime.set(System.currentTimeMillis());
            
            if (failures >= failureThreshold) {
                state = State.OPEN;
                logger.warning(String.format("🔴 Circuit breaker OPEN for %s after %d failures", 
                    serviceName, failures));
            }
        }
        
        public Map<String, Object> getMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            metrics.put("state", state.name());
            metrics.put("failure_count", failureCount.get());
            metrics.put("request_count", requestCount.get());
            metrics.put("success_count", successCount.get());
            metrics.put("success_rate", requestCount.get() > 0 ? 
                (double) successCount.get() / requestCount.get() * 100 : 0);
            return metrics;
        }
    }
    
    // Rate Limiter Implementation
    public static class RateLimiter {
        private final int requestsPerSecond;
        private final AtomicLong lastRefillTime;
        private final AtomicInteger tokens;
        
        public RateLimiter(int requestsPerSecond) {
            this.requestsPerSecond = requestsPerSecond;
            this.tokens = new AtomicInteger(requestsPerSecond);
            this.lastRefillTime = new AtomicLong(System.currentTimeMillis());
        }
        
        public boolean tryAcquire() {
            refillTokens();
            return tokens.getAndUpdate(current -> Math.max(0, current - 1)) > 0;
        }
        
        private void refillTokens() {
            long now = System.currentTimeMillis();
            long lastRefill = lastRefillTime.get();
            
            if (now > lastRefill) {
                long elapsedSeconds = (now - lastRefill) / 1000;
                if (elapsedSeconds > 0 && lastRefillTime.compareAndSet(lastRefill, now)) {
                    int tokensToAdd = (int) Math.min(elapsedSeconds * requestsPerSecond, requestsPerSecond);
                    tokens.updateAndGet(current -> Math.min(requestsPerSecond, current + tokensToAdd));
                }
            }
        }
        
        public int getAvailableTokens() {
            refillTokens();
            return tokens.get();
        }
    }
    
    // Service Mesh Proxy
    @ServiceMeshEnabled(serviceName = "flipkart-product-catalog", version = "v1.2", 
                       enableTLS = true, enableTracing = true, 
                       tags = {"team:catalog", "env:production"})
    public static class FlipkartServiceMeshProxy {
        private final ServiceRegistry serviceRegistry;
        private final Map<String, ServiceMeshCircuitBreaker> circuitBreakers = new ConcurrentHashMap<>();
        private final Map<String, RateLimiter> rateLimiters = new ConcurrentHashMap<>();
        private final LoadBalancingStrategy loadBalancer;
        
        public FlipkartServiceMeshProxy(ServiceRegistry serviceRegistry, 
                                      LoadBalancingStrategy loadBalancer) {
            this.serviceRegistry = serviceRegistry;
            this.loadBalancer = loadBalancer;
            logger.info("🛡️  Flipkart Service Mesh Proxy initialized");
        }
        
        @CircuitBreaker(failureThreshold = 3, timeout = @Duration(seconds = 60))
        @RateLimit(requestsPerSecond = 100)
        @Retry(maxAttempts = 3, delay = @Duration(seconds = 1))
        public String callService(String serviceName, String endpoint, Map<String, Object> request) {
            // Rate limiting
            RateLimiter rateLimiter = rateLimiters.computeIfAbsent(serviceName, 
                k -> new RateLimiter(100));
            
            if (!rateLimiter.tryAcquire()) {
                throw new RuntimeException("Rate limit exceeded for service: " + serviceName);
            }
            
            // Circuit breaker
            ServiceMeshCircuitBreaker circuitBreaker = circuitBreakers.computeIfAbsent(serviceName,
                k -> new ServiceMeshCircuitBreaker(serviceName, 3, Duration.ofSeconds(60)));
            
            try {
                return circuitBreaker.execute(() -> {
                    // Service discovery and load balancing
                    ServiceInstance instance = serviceRegistry.selectInstance(serviceName, loadBalancer);
                    
                    // Simulate service call
                    logger.info(String.format("📞 Calling %s at %s%s", 
                        serviceName, instance.getEndpoint(), endpoint));
                    
                    // Mumbai se Bangalore tak call kar rahe hain
                    if (Math.random() < 0.1) { // 10% failure rate
                        throw new RuntimeException("Service call failed - network timeout");
                    }
                    
                    // Simulate response
                    return String.format("Response from %s:%d - Request processed successfully at %s", 
                        instance.getHost(), instance.getPort(), LocalDateTime.now());
                });
                
            } catch (Exception e) {
                logger.severe(String.format("❌ Service call failed: %s -> %s: %s", 
                    serviceName, endpoint, e.getMessage()));
                throw new RuntimeException(e);
            }
        }
        
        public Map<String, Object> getProxyMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            
            // Circuit breaker metrics
            Map<String, Map<String, Object>> cbMetrics = new HashMap<>();
            circuitBreakers.forEach((service, cb) -> cbMetrics.put(service, cb.getMetrics()));
            metrics.put("circuit_breakers", cbMetrics);
            
            // Rate limiter metrics  
            Map<String, Integer> rlMetrics = new HashMap<>();
            rateLimiters.forEach((service, rl) -> rlMetrics.put(service + "_tokens", rl.getAvailableTokens()));
            metrics.put("rate_limiters", rlMetrics);
            
            // Service registry metrics
            metrics.put("service_registry", serviceRegistry.getServiceStats());
            
            return metrics;
        }
    }
    
    // Traffic Splitting for Canary Deployments
    public static class TrafficSplitter {
        private final Map<String, Integer> weights = new HashMap<>();
        private final Random random = new Random();
        
        public TrafficSplitter() {
            // Default weights - सभी traffic v1 पर
            weights.put("v1", 100);
            weights.put("v2", 0);
        }
        
        public void setTrafficSplit(String version, int percentage) {
            if (percentage < 0 || percentage > 100) {
                throw new IllegalArgumentException("Percentage must be between 0 and 100");
            }
            
            weights.put(version, percentage);
            
            // Normalize weights to 100%
            int total = weights.values().stream().mapToInt(Integer::intValue).sum();
            if (total != 100) {
                // Adjust the complement
                String otherVersion = version.equals("v1") ? "v2" : "v1";
                weights.put(otherVersion, 100 - percentage);
            }
            
            logger.info(String.format("🔀 Traffic split updated: v1=%d%%, v2=%d%%", 
                weights.get("v1"), weights.get("v2")));
        }
        
        public String selectVersion() {
            int roll = random.nextInt(100);
            int cumulative = 0;
            
            for (Map.Entry<String, Integer> entry : weights.entrySet()) {
                cumulative += entry.getValue();
                if (roll < cumulative) {
                    return entry.getKey();
                }
            }
            
            return "v1"; // Fallback
        }
        
        public Map<String, Integer> getCurrentWeights() {
            return new HashMap<>(weights);
        }
    }
    
    // Service Mesh Observability
    public static class ServiceMeshObservability {
        private final Map<String, AtomicLong> requestCounts = new ConcurrentHashMap<>();
        private final Map<String, AtomicLong> errorCounts = new ConcurrentHashMap<>();
        private final Map<String, AtomicLong> responseTimes = new ConcurrentHashMap<>();
        
        public void recordRequest(String service, long responseTimeMs, boolean error) {
            requestCounts.computeIfAbsent(service, k -> new AtomicLong(0)).incrementAndGet();
            responseTimes.computeIfAbsent(service + "_total_time", k -> new AtomicLong(0))
                .addAndGet(responseTimeMs);
            
            if (error) {
                errorCounts.computeIfAbsent(service, k -> new AtomicLong(0)).incrementAndGet();
            }
        }
        
        public Map<String, Object> getMetrics() {
            Map<String, Object> metrics = new HashMap<>();
            
            for (String service : requestCounts.keySet()) {
                long requests = requestCounts.get(service).get();
                long errors = errorCounts.getOrDefault(service, new AtomicLong(0)).get();
                long totalTime = responseTimes.getOrDefault(service + "_total_time", new AtomicLong(0)).get();
                
                Map<String, Object> serviceMetrics = new HashMap<>();
                serviceMetrics.put("requests", requests);
                serviceMetrics.put("errors", errors);
                serviceMetrics.put("error_rate", requests > 0 ? (double) errors / requests * 100 : 0);
                serviceMetrics.put("avg_response_time_ms", requests > 0 ? (double) totalTime / requests : 0);
                
                metrics.put(service, serviceMetrics);
            }
            
            return metrics;
        }
    }
}

// Demo and Testing Class
class FlipkartServiceMeshDemo {
    private static final Logger logger = Logger.getLogger(FlipkartServiceMeshDemo.class.getName());
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🛡️  Flipkart Service Mesh Demo");
        System.out.println("=".repeat(50));
        
        // Initialize service registry
        ServiceMeshConfiguration.ServiceRegistry registry = 
            new ServiceMeshConfiguration.ServiceRegistry();
        
        // Register Flipkart services - Mumbai aur Bangalore datacenters
        registerFlipkartServices(registry);
        
        // Initialize service mesh proxy
        ServiceMeshConfiguration.FlipkartServiceMeshProxy proxy = 
            new ServiceMeshConfiguration.FlipkartServiceMeshProxy(
                registry, new ServiceMeshConfiguration.RoundRobinStrategy());
        
        // Initialize observability
        ServiceMeshConfiguration.ServiceMeshObservability observability = 
            new ServiceMeshConfiguration.ServiceMeshObservability();
        
        // Initialize traffic splitter for canary deployment
        ServiceMeshConfiguration.TrafficSplitter trafficSplitter = 
            new ServiceMeshConfiguration.TrafficSplitter();
        
        System.out.println("\n📞 Testing Service Mesh Features:");
        
        // Test service calls with various patterns
        testServiceCalls(proxy, observability);
        
        // Test traffic splitting (canary deployment)
        testCanaryDeployment(trafficSplitter);
        
        // Display metrics
        displayMetrics(proxy, observability);
        
        System.out.println("\n" + "=".repeat(50));
        System.out.println("🎯 Flipkart Service Mesh Demo Complete!");
        printLearnings();
    }
    
    private static void registerFlipkartServices(ServiceMeshConfiguration.ServiceRegistry registry) {
        // Product Catalog Service - Mumbai datacenter
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "product-catalog", "mumbai-catalog-1.flipkart.com", 8080));
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "product-catalog", "mumbai-catalog-2.flipkart.com", 8080));
        
        // Inventory Service - Bangalore datacenter  
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "inventory-service", "bangalore-inventory-1.flipkart.com", 8081));
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "inventory-service", "bangalore-inventory-2.flipkart.com", 8081));
        
        // Pricing Service - Mumbai datacenter
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "pricing-service", "mumbai-pricing-1.flipkart.com", 8082));
        
        // Recommendation Service - Hybrid
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "recommendation-service", "mumbai-ml-1.flipkart.com", 8083));
        registry.registerService(new ServiceMeshConfiguration.ServiceInstance(
            "recommendation-service", "bangalore-ml-1.flipkart.com", 8083));
        
        System.out.println("✅ Registered Flipkart services across Mumbai and Bangalore datacenters");
    }
    
    private static void testServiceCalls(ServiceMeshConfiguration.FlipkartServiceMeshProxy proxy,
                                       ServiceMeshConfiguration.ServiceMeshObservability observability) {
        String[] services = {"product-catalog", "inventory-service", "pricing-service", "recommendation-service"};
        String[] endpoints = {"/api/products", "/api/inventory/check", "/api/prices", "/api/recommendations"};
        
        // Test multiple service calls
        for (int i = 0; i < 20; i++) {
            for (int j = 0; j < services.length; j++) {
                try {
                    long startTime = System.currentTimeMillis();
                    String response = proxy.callService(services[j], endpoints[j], 
                        Map.of("productId", "FLP" + (1000 + i), "userId", "user_mumbai_" + i));
                    
                    long responseTime = System.currentTimeMillis() - startTime;
                    observability.recordRequest(services[j], responseTime, false);
                    
                    System.out.printf("✅ %s: %s (Response time: %dms)\n", 
                        services[j], response.substring(0, Math.min(response.length(), 80)), responseTime);
                    
                } catch (Exception e) {
                    observability.recordRequest(services[j], 0, true);
                    System.out.printf("❌ %s failed: %s\n", services[j], e.getMessage());
                }
                
                // Small delay between calls
                try { Thread.sleep(100); } catch (InterruptedException ignored) {}
            }
        }
    }
    
    private static void testCanaryDeployment(ServiceMeshConfiguration.TrafficSplitter splitter) {
        System.out.println("\n🚀 Testing Canary Deployment - Mumbai to Bangalore rollout:");
        
        // Start with 0% traffic to v2
        System.out.println("Initial: " + splitter.getCurrentWeights());
        
        // Simulate gradual rollout
        int[] canaryPercentages = {5, 10, 25, 50, 75, 100};
        for (int percentage : canaryPercentages) {
            splitter.setTrafficSplit("v2", percentage);
            
            // Test traffic distribution
            Map<String, Integer> versionCounts = new HashMap<>();
            for (int i = 0; i < 100; i++) {
                String version = splitter.selectVersion();
                versionCounts.put(version, versionCounts.getOrDefault(version, 0) + 1);
            }
            
            System.out.printf("Canary %d%%: Actual distribution - %s\n", 
                percentage, versionCounts);
            
            try { Thread.sleep(500); } catch (InterruptedException ignored) {}
        }
    }
    
    private static void displayMetrics(ServiceMeshConfiguration.FlipkartServiceMeshProxy proxy,
                                     ServiceMeshConfiguration.ServiceMeshObservability observability) {
        System.out.println("\n📊 Service Mesh Metrics:");
        
        // Proxy metrics
        Map<String, Object> proxyMetrics = proxy.getProxyMetrics();
        System.out.println("\nCircuit Breaker Status:");
        @SuppressWarnings("unchecked")
        Map<String, Map<String, Object>> cbMetrics = 
            (Map<String, Map<String, Object>>) proxyMetrics.get("circuit_breakers");
        
        cbMetrics.forEach((service, metrics) -> {
            System.out.printf("  %s: State=%s, Success Rate=%.1f%%, Requests=%s\n",
                service, metrics.get("state"), metrics.get("success_rate"), metrics.get("request_count"));
        });
        
        // Observability metrics
        System.out.println("\nService Performance:");
        observability.getMetrics().forEach((service, metrics) -> {
            @SuppressWarnings("unchecked")
            Map<String, Object> serviceMetrics = (Map<String, Object>) metrics;
            System.out.printf("  %s: Requests=%s, Error Rate=%.1f%%, Avg Response Time=%.1fms\n",
                service, serviceMetrics.get("requests"), serviceMetrics.get("error_rate"), 
                serviceMetrics.get("avg_response_time_ms"));
        });
    }
    
    private static void printLearnings() {
        System.out.println("Key Service Mesh Features Demonstrated:");
        System.out.println("1. 🔍 Service Discovery and Registration");
        System.out.println("2. ⚖️  Load Balancing (Round Robin, Random, Least Connections)");
        System.out.println("3. 🔌 Circuit Breaker Pattern for Resilience");
        System.out.println("4. 🚦 Rate Limiting for Traffic Control");  
        System.out.println("5. 🏥 Health Checking and Monitoring");
        System.out.println("6. 🚀 Canary Deployment with Traffic Splitting");
        System.out.println("7. 📊 Comprehensive Observability and Metrics");
        System.out.println("8. 🛡️  Automatic Failure Handling and Recovery");
    }
}