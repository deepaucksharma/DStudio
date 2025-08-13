/**
 * Model Serving Pipeline - MLOps Episode 44
 * Production-ready model serving infrastructure for high-throughput ML inference
 * 
 * Author: Claude Code
 * Context: Real-time model serving system like what Flipkart uses in production
 */

package com.episode44.mlops;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.io.*;
import java.time.LocalDateTime;
import java.time.Duration;
import java.time.Instant;
import java.nio.file.Paths;
import java.nio.file.Files;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Production Model Serving Pipeline for Flipkart-style ML systems
 * Mumbai me sabse fast aur reliable model serving!
 */
public class ModelServingPipeline {
    
    private static final Logger logger = LoggerFactory.getLogger(ModelServingPipeline.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Model registry and cache
    private final Map<String, ModelMetadata> modelRegistry = new ConcurrentHashMap<>();
    private final Map<String, LoadedModel> modelCache = new ConcurrentHashMap<>();
    private final ReadWriteLock cacheLock = new ReentrantReadWriteLock();
    
    // Thread pools for async processing
    private final ExecutorService predictionExecutor;
    private final ExecutorService modelLoadExecutor;
    private final ScheduledExecutorService healthCheckExecutor;
    
    // Performance metrics
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong successfulRequests = new AtomicLong(0);
    private final AtomicLong failedRequests = new AtomicLong(0);
    private final Map<String, ModelMetrics> modelMetrics = new ConcurrentHashMap<>();
    
    // Configuration
    private final ServingConfig config;
    private final CircuitBreaker circuitBreaker;
    
    /**
     * Model metadata for registry
     */
    public static class ModelMetadata {
        @JsonProperty("model_id")
        private String modelId;
        
        @JsonProperty("name")
        private String name;
        
        @JsonProperty("version")
        private String version;
        
        @JsonProperty("framework")
        private String framework;
        
        @JsonProperty("model_path")
        private String modelPath;
        
        @JsonProperty("input_schema")
        private Map<String, Object> inputSchema;
        
        @JsonProperty("output_schema")
        private Map<String, Object> outputSchema;
        
        @JsonProperty("created_at")
        private LocalDateTime createdAt;
        
        @JsonProperty("is_active")
        private boolean isActive;
        
        @JsonProperty("warm_up_required")
        private boolean warmUpRequired;
        
        @JsonProperty("max_batch_size")
        private int maxBatchSize;
        
        @JsonProperty("timeout_ms")
        private long timeoutMs;
        
        // Constructors, getters, setters
        public ModelMetadata() {}
        
        public ModelMetadata(String modelId, String name, String version, String framework, String modelPath) {
            this.modelId = modelId;
            this.name = name;
            this.version = version;
            this.framework = framework;
            this.modelPath = modelPath;
            this.createdAt = LocalDateTime.now();
            this.isActive = true;
            this.warmUpRequired = true;
            this.maxBatchSize = 32;
            this.timeoutMs = 5000;
        }
        
        // Getters and setters
        public String getModelId() { return modelId; }
        public void setModelId(String modelId) { this.modelId = modelId; }
        
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
        
        public String getVersion() { return version; }
        public void setVersion(String version) { this.version = version; }
        
        public String getFramework() { return framework; }
        public void setFramework(String framework) { this.framework = framework; }
        
        public String getModelPath() { return modelPath; }
        public void setModelPath(String modelPath) { this.modelPath = modelPath; }
        
        public boolean isActive() { return isActive; }
        public void setActive(boolean active) { isActive = active; }
        
        public int getMaxBatchSize() { return maxBatchSize; }
        public void setMaxBatchSize(int maxBatchSize) { this.maxBatchSize = maxBatchSize; }
        
        public long getTimeoutMs() { return timeoutMs; }
        public void setTimeoutMs(long timeoutMs) { this.timeoutMs = timeoutMs; }
    }
    
    /**
     * Loaded model wrapper with inference capabilities
     */
    public static class LoadedModel {
        private final ModelMetadata metadata;
        private final Object model; // Actual model object (framework-specific)
        private final Instant loadedAt;
        private final AtomicLong inferenceCount = new AtomicLong(0);
        private volatile boolean isWarmedUp = false;
        
        public LoadedModel(ModelMetadata metadata, Object model) {
            this.metadata = metadata;
            this.model = model;
            this.loadedAt = Instant.now();
        }
        
        public ModelMetadata getMetadata() { return metadata; }
        public Object getModel() { return model; }
        public Instant getLoadedAt() { return loadedAt; }
        public long getInferenceCount() { return inferenceCount.get(); }
        public boolean isWarmedUp() { return isWarmedUp; }
        public void setWarmedUp(boolean warmedUp) { this.isWarmedUp = warmedUp; }
        
        public void incrementInferenceCount() {
            inferenceCount.incrementAndGet();
        }
    }
    
    /**
     * Prediction request structure
     */
    public static class PredictionRequest {
        @JsonProperty("model_id")
        private String modelId;
        
        @JsonProperty("input_data")
        private Map<String, Object> inputData;
        
        @JsonProperty("request_id")
        private String requestId;
        
        @JsonProperty("timeout_ms")
        private Long timeoutMs;
        
        @JsonProperty("batch_data")
        private List<Map<String, Object>> batchData;
        
        // Constructors, getters, setters
        public PredictionRequest() {}
        
        public String getModelId() { return modelId; }
        public void setModelId(String modelId) { this.modelId = modelId; }
        
        public Map<String, Object> getInputData() { return inputData; }
        public void setInputData(Map<String, Object> inputData) { this.inputData = inputData; }
        
        public String getRequestId() { return requestId; }
        public void setRequestId(String requestId) { this.requestId = requestId; }
        
        public List<Map<String, Object>> getBatchData() { return batchData; }
        public void setBatchData(List<Map<String, Object>> batchData) { this.batchData = batchData; }
    }
    
    /**
     * Prediction response structure
     */
    public static class PredictionResponse {
        @JsonProperty("request_id")
        private String requestId;
        
        @JsonProperty("model_id")
        private String modelId;
        
        @JsonProperty("prediction")
        private Object prediction;
        
        @JsonProperty("confidence")
        private Double confidence;
        
        @JsonProperty("processing_time_ms")
        private long processingTimeMs;
        
        @JsonProperty("model_version")
        private String modelVersion;
        
        @JsonProperty("timestamp")
        private LocalDateTime timestamp;
        
        @JsonProperty("status")
        private String status;
        
        @JsonProperty("error_message")
        private String errorMessage;
        
        // Constructors, getters, setters
        public PredictionResponse() {
            this.timestamp = LocalDateTime.now();
            this.status = "success";
        }
        
        public static PredictionResponse success(String requestId, String modelId, Object prediction, 
                                               long processingTime, String modelVersion) {
            PredictionResponse response = new PredictionResponse();
            response.requestId = requestId;
            response.modelId = modelId;
            response.prediction = prediction;
            response.processingTimeMs = processingTime;
            response.modelVersion = modelVersion;
            return response;
        }
        
        public static PredictionResponse error(String requestId, String modelId, String errorMessage) {
            PredictionResponse response = new PredictionResponse();
            response.requestId = requestId;
            response.modelId = modelId;
            response.errorMessage = errorMessage;
            response.status = "error";
            return response;
        }
        
        // Getters and setters
        public String getRequestId() { return requestId; }
        public String getModelId() { return modelId; }
        public Object getPrediction() { return prediction; }
        public long getProcessingTimeMs() { return processingTimeMs; }
        public String getStatus() { return status; }
        public String getErrorMessage() { return errorMessage; }
    }
    
    /**
     * Model performance metrics
     */
    public static class ModelMetrics {
        private final AtomicLong requestCount = new AtomicLong(0);
        private final AtomicLong errorCount = new AtomicLong(0);
        private final List<Long> latencies = new CopyOnWriteArrayList<>();
        private volatile double averageLatency = 0.0;
        private volatile double p95Latency = 0.0;
        private volatile double errorRate = 0.0;
        
        public void recordRequest(long latencyMs, boolean isError) {
            requestCount.incrementAndGet();
            if (isError) {
                errorCount.incrementAndGet();
            }
            
            latencies.add(latencyMs);
            
            // Keep only last 1000 latencies for calculation
            if (latencies.size() > 1000) {
                latencies.remove(0);
            }
            
            // Update metrics
            updateMetrics();
        }
        
        private void updateMetrics() {
            if (latencies.isEmpty()) return;
            
            List<Long> sortedLatencies = new ArrayList<>(latencies);
            Collections.sort(sortedLatencies);
            
            // Calculate average
            averageLatency = sortedLatencies.stream().mapToLong(Long::longValue).average().orElse(0.0);
            
            // Calculate P95
            int p95Index = (int) Math.ceil(0.95 * sortedLatencies.size()) - 1;
            p95Latency = sortedLatencies.get(Math.max(0, p95Index));
            
            // Calculate error rate
            long totalRequests = requestCount.get();
            errorRate = totalRequests > 0 ? (double) errorCount.get() / totalRequests : 0.0;
        }
        
        // Getters
        public long getRequestCount() { return requestCount.get(); }
        public long getErrorCount() { return errorCount.get(); }
        public double getAverageLatency() { return averageLatency; }
        public double getP95Latency() { return p95Latency; }
        public double getErrorRate() { return errorRate; }
    }
    
    /**
     * Serving configuration
     */
    public static class ServingConfig {
        private int predictionThreads = 20;
        private int modelLoadThreads = 5;
        private int maxCachedModels = 10;
        private long modelTimeoutMs = 5000;
        private boolean enableBatching = true;
        private int maxBatchSize = 32;
        private long batchTimeoutMs = 50;
        
        // Getters and setters
        public int getPredictionThreads() { return predictionThreads; }
        public void setPredictionThreads(int predictionThreads) { this.predictionThreads = predictionThreads; }
        
        public int getMaxCachedModels() { return maxCachedModels; }
        public void setMaxCachedModels(int maxCachedModels) { this.maxCachedModels = maxCachedModels; }
        
        public long getModelTimeoutMs() { return modelTimeoutMs; }
        public void setModelTimeoutMs(long modelTimeoutMs) { this.modelTimeoutMs = modelTimeoutMs; }
    }
    
    /**
     * Circuit breaker for fault tolerance
     */
    public static class CircuitBreaker {
        private final int failureThreshold;
        private final long timeoutMs;
        private int failureCount = 0;
        private long lastFailureTime = 0;
        private State state = State.CLOSED;
        
        public enum State { CLOSED, OPEN, HALF_OPEN }
        
        public CircuitBreaker(int failureThreshold, long timeoutMs) {
            this.failureThreshold = failureThreshold;
            this.timeoutMs = timeoutMs;
        }
        
        public synchronized boolean canExecute() {
            if (state == State.CLOSED) {
                return true;
            } else if (state == State.OPEN) {
                if (System.currentTimeMillis() - lastFailureTime > timeoutMs) {
                    state = State.HALF_OPEN;
                    return true;
                }
                return false;
            } else { // HALF_OPEN
                return true;
            }
        }
        
        public synchronized void recordSuccess() {
            failureCount = 0;
            state = State.CLOSED;
        }
        
        public synchronized void recordFailure() {
            failureCount++;
            lastFailureTime = System.currentTimeMillis();
            
            if (failureCount >= failureThreshold) {
                state = State.OPEN;
            }
        }
        
        public State getState() { return state; }
    }
    
    /**
     * Initialize model serving pipeline
     */
    public ModelServingPipeline(ServingConfig config) {
        this.config = config;
        this.circuitBreaker = new CircuitBreaker(5, 60000); // 5 failures, 60s timeout
        
        // Initialize thread pools
        this.predictionExecutor = Executors.newFixedThreadPool(config.getPredictionThreads());
        this.modelLoadExecutor = Executors.newFixedThreadPool(config.modelLoadThreads);
        this.healthCheckExecutor = Executors.newScheduledThreadPool(2);
        
        // Start health check
        startHealthCheck();
        
        logger.info("Model serving pipeline initialized with {} prediction threads", config.getPredictionThreads());
    }
    
    /**
     * Register model in the serving pipeline
     * Mumbai me model ka registration!
     */
    public boolean registerModel(ModelMetadata metadata) {
        if (metadata.getModelId() == null || metadata.getModelPath() == null) {
            logger.error("Invalid model metadata: missing model_id or model_path");
            return false;
        }
        
        try {
            // Validate model file exists
            if (!Files.exists(Paths.get(metadata.getModelPath()))) {
                logger.error("Model file not found: {}", metadata.getModelPath());
                return false;
            }
            
            modelRegistry.put(metadata.getModelId(), metadata);
            logger.info("Model registered: {} ({})", metadata.getModelId(), metadata.getName());
            
            // Pre-load model if it's marked as active
            if (metadata.isActive()) {
                CompletableFuture.runAsync(() -> loadModel(metadata.getModelId()), modelLoadExecutor);
            }
            
            return true;
        } catch (Exception e) {
            logger.error("Failed to register model: {}", metadata.getModelId(), e);
            return false;
        }
    }
    
    /**
     * Load model into memory cache
     * Mumbai me model loading ka efficient system!
     */
    public CompletableFuture<LoadedModel> loadModel(String modelId) {
        return CompletableFuture.supplyAsync(() -> {
            ModelMetadata metadata = modelRegistry.get(modelId);
            if (metadata == null) {
                throw new IllegalArgumentException("Model not found: " + modelId);
            }
            
            cacheLock.writeLock().lock();
            try {
                // Check if already loaded
                LoadedModel cached = modelCache.get(modelId);
                if (cached != null) {
                    logger.debug("Model already loaded: {}", modelId);
                    return cached;
                }
                
                // Load model based on framework
                Object model = loadModelByFramework(metadata);
                LoadedModel loadedModel = new LoadedModel(metadata, model);
                
                // Add to cache
                modelCache.put(modelId, loadedModel);
                
                // Warm up model if required
                if (metadata.warmUpRequired) {
                    warmUpModel(loadedModel);
                }
                
                logger.info("Model loaded successfully: {}", modelId);
                return loadedModel;
                
            } finally {
                cacheLock.writeLock().unlock();
            }
        }, modelLoadExecutor);
    }
    
    /**
     * Load model based on framework (simplified simulation)
     */
    private Object loadModelByFramework(ModelMetadata metadata) {
        // Simulate model loading delay
        try {
            Thread.sleep(1000 + new Random().nextInt(2000)); // 1-3 seconds
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Return mock model object (in production, load actual model)
        Map<String, Object> mockModel = new HashMap<>();
        mockModel.put("framework", metadata.getFramework());
        mockModel.put("path", metadata.getModelPath());
        mockModel.put("loaded_at", Instant.now());
        
        return mockModel;
    }
    
    /**
     * Warm up model with sample data
     */
    private void warmUpModel(LoadedModel loadedModel) {
        try {
            // Simulate warm-up inference
            Map<String, Object> sampleInput = createSampleInput(loadedModel.getMetadata());
            
            // Run a few warm-up predictions
            for (int i = 0; i < 3; i++) {
                simulateInference(loadedModel, sampleInput);
            }
            
            loadedModel.setWarmedUp(true);
            logger.info("Model warmed up: {}", loadedModel.getMetadata().getModelId());
            
        } catch (Exception e) {
            logger.warn("Model warm-up failed: {}", loadedModel.getMetadata().getModelId(), e);
        }
    }
    
    /**
     * Create sample input for warm-up
     */
    private Map<String, Object> createSampleInput(ModelMetadata metadata) {
        Map<String, Object> sampleInput = new HashMap<>();
        
        // Create sample data based on framework
        if ("scikit-learn".equals(metadata.getFramework())) {
            sampleInput.put("features", Arrays.asList(1.0, 2.0, 3.0, 4.0));
        } else if ("tensorflow".equals(metadata.getFramework())) {
            sampleInput.put("image", new double[224][224][3]); // Sample image
        } else {
            sampleInput.put("data", "sample_input");
        }
        
        return sampleInput;
    }
    
    /**
     * Make prediction using loaded model
     * Mumbai me real-time prediction!
     */
    public CompletableFuture<PredictionResponse> predict(PredictionRequest request) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            totalRequests.incrementAndGet();
            
            try {
                // Validate request
                if (request.getModelId() == null) {
                    throw new IllegalArgumentException("Model ID is required");
                }
                
                // Check circuit breaker
                if (!circuitBreaker.canExecute()) {
                    throw new RuntimeException("Circuit breaker is open");
                }
                
                // Get loaded model
                LoadedModel loadedModel = getOrLoadModel(request.getModelId());
                
                // Record metrics
                ModelMetrics metrics = modelMetrics.computeIfAbsent(
                    request.getModelId(), 
                    k -> new ModelMetrics()
                );
                
                // Perform inference
                Object prediction;
                if (request.getBatchData() != null && !request.getBatchData().isEmpty()) {
                    prediction = performBatchInference(loadedModel, request.getBatchData());
                } else {
                    prediction = performSingleInference(loadedModel, request.getInputData());
                }
                
                long processingTime = System.currentTimeMillis() - startTime;
                
                // Update metrics
                metrics.recordRequest(processingTime, false);
                loadedModel.incrementInferenceCount();
                successfulRequests.incrementAndGet();
                circuitBreaker.recordSuccess();
                
                return PredictionResponse.success(
                    request.getRequestId(),
                    request.getModelId(),
                    prediction,
                    processingTime,
                    loadedModel.getMetadata().getVersion()
                );
                
            } catch (Exception e) {
                long processingTime = System.currentTimeMillis() - startTime;
                
                // Update error metrics
                ModelMetrics metrics = modelMetrics.computeIfAbsent(
                    request.getModelId(), 
                    k -> new ModelMetrics()
                );
                metrics.recordRequest(processingTime, true);
                
                failedRequests.incrementAndGet();
                circuitBreaker.recordFailure();
                
                logger.error("Prediction failed for request: {}", request.getRequestId(), e);
                return PredictionResponse.error(request.getRequestId(), request.getModelId(), e.getMessage());
            }
        }, predictionExecutor);
    }
    
    /**
     * Get model from cache or load if not available
     */
    private LoadedModel getOrLoadModel(String modelId) throws Exception {
        cacheLock.readLock().lock();
        try {
            LoadedModel cached = modelCache.get(modelId);
            if (cached != null) {
                return cached;
            }
        } finally {
            cacheLock.readLock().unlock();
        }
        
        // Model not in cache, load it
        return loadModel(modelId).get(config.getModelTimeoutMs(), TimeUnit.MILLISECONDS);
    }
    
    /**
     * Perform single inference
     */
    private Object performSingleInference(LoadedModel loadedModel, Map<String, Object> inputData) {
        return simulateInference(loadedModel, inputData);
    }
    
    /**
     * Perform batch inference
     */
    private Object performBatchInference(LoadedModel loadedModel, List<Map<String, Object>> batchData) {
        List<Object> batchResults = new ArrayList<>();
        
        for (Map<String, Object> input : batchData) {
            Object result = simulateInference(loadedModel, input);
            batchResults.add(result);
        }
        
        return batchResults;
    }
    
    /**
     * Simulate model inference (in production, call actual model)
     */
    private Object simulateInference(LoadedModel loadedModel, Map<String, Object> inputData) {
        try {
            // Simulate inference time
            Thread.sleep(10 + new Random().nextInt(90)); // 10-100ms
            
            // Return mock prediction based on framework
            String framework = loadedModel.getMetadata().getFramework();
            
            if ("scikit-learn".equals(framework)) {
                return Map.of(
                    "prediction", new Random().nextDouble(),
                    "confidence", 0.8 + new Random().nextDouble() * 0.2
                );
            } else if ("tensorflow".equals(framework)) {
                return Map.of(
                    "class_probabilities", Arrays.asList(0.2, 0.8),
                    "predicted_class", 1
                );
            } else {
                return Map.of("result", "mock_prediction_" + System.currentTimeMillis());
            }
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Inference interrupted", e);
        }
    }
    
    /**
     * Get model serving statistics
     */
    public Map<String, Object> getServingStats() {
        Map<String, Object> stats = new HashMap<>();
        
        stats.put("total_requests", totalRequests.get());
        stats.put("successful_requests", successfulRequests.get());
        stats.put("failed_requests", failedRequests.get());
        stats.put("success_rate", totalRequests.get() > 0 ? 
            (double) successfulRequests.get() / totalRequests.get() : 0.0);
        
        stats.put("cached_models", modelCache.size());
        stats.put("registered_models", modelRegistry.size());
        stats.put("circuit_breaker_state", circuitBreaker.getState().name());
        
        // Model-specific metrics
        Map<String, Object> modelStats = new HashMap<>();
        for (Map.Entry<String, ModelMetrics> entry : modelMetrics.entrySet()) {
            ModelMetrics metrics = entry.getValue();
            modelStats.put(entry.getKey(), Map.of(
                "request_count", metrics.getRequestCount(),
                "error_count", metrics.getErrorCount(),
                "error_rate", metrics.getErrorRate(),
                "avg_latency_ms", metrics.getAverageLatency(),
                "p95_latency_ms", metrics.getP95Latency()
            ));
        }
        stats.put("model_metrics", modelStats);
        
        return stats;
    }
    
    /**
     * Start health check monitoring
     */
    private void startHealthCheck() {
        healthCheckExecutor.scheduleAtFixedRate(() -> {
            try {
                // Check model health
                for (LoadedModel model : modelCache.values()) {
                    // Perform health check (simplified)
                    if (Duration.between(model.getLoadedAt(), Instant.now()).toHours() > 24) {
                        logger.warn("Model {} has been loaded for more than 24 hours", 
                                  model.getMetadata().getModelId());
                    }
                }
                
                // Log statistics
                if (totalRequests.get() % 1000 == 0 && totalRequests.get() > 0) {
                    logger.info("Serving stats: {} total requests, {}% success rate", 
                              totalRequests.get(), 
                              (double) successfulRequests.get() / totalRequests.get() * 100);
                }
                
            } catch (Exception e) {
                logger.error("Health check failed", e);
            }
        }, 30, 30, TimeUnit.SECONDS);
    }
    
    /**
     * Shutdown the serving pipeline
     */
    public void shutdown() {
        logger.info("Shutting down model serving pipeline...");
        
        predictionExecutor.shutdown();
        modelLoadExecutor.shutdown();
        healthCheckExecutor.shutdown();
        
        try {
            if (!predictionExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                predictionExecutor.shutdownNow();
            }
            if (!modelLoadExecutor.awaitTermination(10, TimeUnit.SECONDS)) {
                modelLoadExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("Model serving pipeline shutdown complete");
    }
    
    /**
     * Demo main method
     */
    public static void main(String[] args) throws Exception {
        System.out.println("🚀 Starting Model Serving Pipeline Demo");
        System.out.println("=" + "=".repeat(50));
        
        // Initialize serving pipeline
        ServingConfig config = new ServingConfig();
        config.setPredictionThreads(10);
        config.setMaxCachedModels(5);
        
        ModelServingPipeline pipeline = new ModelServingPipeline(config);
        
        // Register sample models
        System.out.println("\n📦 Registering sample models...");
        
        ModelMetadata fraudModel = new ModelMetadata(
            "paytm_fraud_detector_v1", 
            "Paytm Fraud Detection", 
            "1.0", 
            "scikit-learn", 
            "/models/fraud_detector.pkl"
        );
        fraudModel.setMaxBatchSize(64);
        fraudModel.setTimeoutMs(1000);
        
        ModelMetadata recommendationModel = new ModelMetadata(
            "flipkart_recommendation_v2", 
            "Flipkart Product Recommendation", 
            "2.0", 
            "tensorflow", 
            "/models/recommendation.h5"
        );
        recommendationModel.setMaxBatchSize(32);
        
        pipeline.registerModel(fraudModel);
        pipeline.registerModel(recommendationModel);
        
        // Wait for models to load
        Thread.sleep(3000);
        
        // Test predictions
        System.out.println("\n🔮 Testing model predictions...");
        
        List<CompletableFuture<PredictionResponse>> futures = new ArrayList<>();
        
        // Test fraud detection
        for (int i = 0; i < 10; i++) {
            PredictionRequest fraudRequest = new PredictionRequest();
            fraudRequest.setRequestId("fraud_req_" + i);
            fraudRequest.setModelId("paytm_fraud_detector_v1");
            fraudRequest.setInputData(Map.of(
                "amount", 1000 + new Random().nextInt(9000),
                "user_age_days", new Random().nextInt(1000),
                "transaction_hour", new Random().nextInt(24)
            ));
            
            futures.add(pipeline.predict(fraudRequest));
        }
        
        // Test recommendations
        for (int i = 0; i < 5; i++) {
            PredictionRequest recRequest = new PredictionRequest();
            recRequest.setRequestId("rec_req_" + i);
            recRequest.setModelId("flipkart_recommendation_v2");
            recRequest.setInputData(Map.of(
                "user_id", "user_" + (1000 + i),
                "category", "electronics",
                "price_range", Arrays.asList(100, 5000)
            ));
            
            futures.add(pipeline.predict(recRequest));
        }
        
        // Wait for all predictions
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
        
        // Collect and display results
        System.out.println("\n📊 Prediction Results:");
        int successCount = 0;
        
        for (CompletableFuture<PredictionResponse> future : futures) {
            PredictionResponse response = future.get();
            
            if ("success".equals(response.getStatus())) {
                successCount++;
                System.out.println("  ✅ " + response.getRequestId() + 
                                 " (" + response.getModelId() + ") - " + 
                                 response.getProcessingTimeMs() + "ms");
            } else {
                System.out.println("  ❌ " + response.getRequestId() + 
                                 " - " + response.getErrorMessage());
            }
        }
        
        System.out.println("\n📈 Success Rate: " + successCount + "/" + futures.size() + 
                          " (" + (successCount * 100.0 / futures.size()) + "%)");
        
        // Display serving statistics
        System.out.println("\n📊 Serving Pipeline Statistics:");
        Map<String, Object> stats = pipeline.getServingStats();
        
        System.out.println("  Total Requests: " + stats.get("total_requests"));
        System.out.println("  Success Rate: " + String.format("%.2f%%", 
                          (Double) stats.get("success_rate") * 100));
        System.out.println("  Cached Models: " + stats.get("cached_models"));
        System.out.println("  Circuit Breaker: " + stats.get("circuit_breaker_state"));
        
        @SuppressWarnings("unchecked")
        Map<String, Object> modelMetrics = (Map<String, Object>) stats.get("model_metrics");
        System.out.println("\n📊 Model-specific Metrics:");
        
        for (Map.Entry<String, Object> entry : modelMetrics.entrySet()) {
            @SuppressWarnings("unchecked")
            Map<String, Object> metrics = (Map<String, Object>) entry.getValue();
            System.out.println("  " + entry.getKey() + ":");
            System.out.println("    Requests: " + metrics.get("request_count"));
            System.out.println("    Avg Latency: " + String.format("%.2f ms", 
                              (Double) metrics.get("avg_latency_ms")));
            System.out.println("    P95 Latency: " + String.format("%.2f ms", 
                              (Double) metrics.get("p95_latency_ms")));
        }
        
        System.out.println("\n✅ Model serving pipeline demo completed!");
        System.out.println("Mumbai me model serving bhi express train ki tarah fast!");
        
        // Shutdown
        pipeline.shutdown();
    }
}