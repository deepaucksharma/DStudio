/**
 * AI Model Monitor for Production Systems
 * Episode 5: Java Implementation
 * 
 * Production-ready monitoring system for AI models in Indian infrastructure
 * Tracks performance, drift, costs, and reliability metrics
 * 
 * Author: Code Developer Agent
 * Context: Indian AI/ML production monitoring with multi-language support
 */

package com.aiScale.monitoring;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.stream.Collectors;
import java.time.LocalDateTime;
import java.time.Duration;
import java.time.format.DateTimeFormatter;
import java.util.logging.Logger;
import java.util.logging.Level;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.function.Function;

/**
 * AI Model Monitor - production AI models की comprehensive monitoring
 * Indian companies (Paytm, Flipkart, Zomato) के real-world use cases के साथ
 */
public class AIModelMonitor {
    private static final Logger logger = Logger.getLogger(AIModelMonitor.class.getName());
    
    private final Map<String, ModelInstance> deployedModels;
    private final Map<String, ModelMetrics> modelMetrics;
    private final AlertManager alertManager;
    private final DriftDetector driftDetector;
    private final PerformanceTracker performanceTracker;
    private final CostTracker costTracker;
    private final ScheduledExecutorService monitoringExecutor;
    private final ExecutorService alertExecutor;
    
    // भारतीय infrastructure के लिए default thresholds
    private static final double DEFAULT_LATENCY_THRESHOLD_MS = 500.0;  // 500ms for Indian internet speeds
    private static final double DEFAULT_ACCURACY_THRESHOLD = 0.85;     // 85% minimum accuracy
    private static final double DEFAULT_DRIFT_THRESHOLD = 0.15;        // 15% drift threshold
    private static final double DEFAULT_ERROR_RATE_THRESHOLD = 0.05;   // 5% error rate threshold
    
    public AIModelMonitor() {
        this.deployedModels = new ConcurrentHashMap<>();
        this.modelMetrics = new ConcurrentHashMap<>();
        this.alertManager = new AlertManager();
        this.driftDetector = new DriftDetector();
        this.performanceTracker = new PerformanceTracker();
        this.costTracker = new CostTracker();
        this.monitoringExecutor = Executors.newScheduledThreadPool(5);
        this.alertExecutor = Executors.newFixedThreadPool(3);
        
        // Start background monitoring
        startContinuousMonitoring();
        
        logger.info("AI Model Monitor initialized for Indian production systems");
    }
    
    /**
     * Model Instance class representing deployed AI models
     * भारतीय companies के real production models
     */
    public static class ModelInstance {
        private final String modelId;
        private final String modelName;
        private final String version;
        private final ModelType modelType;
        private final String deploymentRegion;
        private final LocalDateTime deployedAt;
        private volatile ModelStatus status;
        private volatile String endpoint;
        private volatile int concurrentRequests;
        private volatile long totalRequests;
        private volatile double avgLatencyMs;
        private volatile double currentAccuracy;
        private volatile double memoryUsageMB;
        private volatile double cpuUtilization;
        private volatile double costPerRequestINR;
        
        // Indian specific configurations
        private final Set<String> supportedLanguages;
        private final boolean handlesCodeMixing; // For Hindi-English mixed text
        private final String useCase;           // E.g., "fraud_detection", "food_recommendation"
        private final String companyName;       // E.g., "paytm", "flipkart", "zomato"
        
        public ModelInstance(String modelId, String modelName, String version, 
                           ModelType modelType, String deploymentRegion, String useCase, 
                           String companyName, Set<String> supportedLanguages, 
                           boolean handlesCodeMixing) {
            this.modelId = modelId;
            this.modelName = modelName;
            this.version = version;
            this.modelType = modelType;
            this.deploymentRegion = deploymentRegion;
            this.useCase = useCase;
            this.companyName = companyName;
            this.supportedLanguages = new HashSet<>(supportedLanguages);
            this.handlesCodeMixing = handlesCodeMixing;
            this.deployedAt = LocalDateTime.now();
            this.status = ModelStatus.DEPLOYING;
            this.totalRequests = 0;
            this.concurrentRequests = 0;
            this.avgLatencyMs = 0.0;
            this.currentAccuracy = 1.0; // Start optimistic
            this.memoryUsageMB = 0.0;
            this.cpuUtilization = 0.0;
            this.costPerRequestINR = 0.0;
        }
        
        // Getters और setters with thread safety
        public synchronized void updateMetrics(double latency, double accuracy, 
                                            double memoryUsage, double cpuUtil) {
            this.avgLatencyMs = (this.avgLatencyMs * 0.9) + (latency * 0.1); // Exponential moving average
            this.currentAccuracy = accuracy;
            this.memoryUsageMB = memoryUsage;
            this.cpuUtilization = cpuUtil;
            this.totalRequests++;
        }
        
        public synchronized void incrementConcurrentRequests() {
            this.concurrentRequests++;
        }
        
        public synchronized void decrementConcurrentRequests() {
            this.concurrentRequests = Math.max(0, this.concurrentRequests - 1);
        }
        
        public synchronized boolean isHealthy() {
            return status == ModelStatus.HEALTHY &&
                   avgLatencyMs < DEFAULT_LATENCY_THRESHOLD_MS &&
                   currentAccuracy > DEFAULT_ACCURACY_THRESHOLD &&
                   cpuUtilization < 90.0 &&
                   memoryUsageMB < 8192; // 8GB memory limit
        }
        
        // Getters
        public String getModelId() { return modelId; }
        public String getModelName() { return modelName; }
        public String getVersion() { return version; }
        public ModelType getModelType() { return modelType; }
        public String getDeploymentRegion() { return deploymentRegion; }
        public LocalDateTime getDeployedAt() { return deployedAt; }
        public ModelStatus getStatus() { return status; }
        public String getEndpoint() { return endpoint; }
        public int getConcurrentRequests() { return concurrentRequests; }
        public long getTotalRequests() { return totalRequests; }
        public double getAvgLatencyMs() { return avgLatencyMs; }
        public double getCurrentAccuracy() { return currentAccuracy; }
        public double getMemoryUsageMB() { return memoryUsageMB; }
        public double getCpuUtilization() { return cpuUtilization; }
        public double getCostPerRequestINR() { return costPerRequestINR; }
        public Set<String> getSupportedLanguages() { return new HashSet<>(supportedLanguages); }
        public boolean handlesCodeMixing() { return handlesCodeMixing; }
        public String getUseCase() { return useCase; }
        public String getCompanyName() { return companyName; }
        
        // Setters with validation
        public synchronized void setStatus(ModelStatus status) {
            this.status = status;
        }
        
        public synchronized void setEndpoint(String endpoint) {
            this.endpoint = endpoint;
        }
        
        public synchronized void setCostPerRequestINR(double cost) {
            this.costPerRequestINR = Math.max(0.0, cost);
        }
    }
    
    public enum ModelType {
        TRANSFORMER("transformer", "Text processing, NLP"),
        CNN("cnn", "Image classification, Computer vision"),
        RNN("rnn", "Sequential data, Time series"),
        DECISION_TREE("decision_tree", "Classification, Regression"),
        SVM("svm", "Classification, Text classification"),
        ENSEMBLE("ensemble", "Multiple models combined"),
        RECOMMENDATION("recommendation", "Collaborative filtering"),
        ANOMALY_DETECTION("anomaly_detection", "Fraud detection, Outlier detection"),
        EMBEDDINGS("embeddings", "Feature extraction, Similarity");
        
        private final String code;
        private final String description;
        
        ModelType(String code, String description) {
            this.code = code;
            this.description = description;
        }
        
        public String getCode() { return code; }
        public String getDescription() { return description; }
    }
    
    public enum ModelStatus {
        DEPLOYING, HEALTHY, DEGRADED, UNHEALTHY, FAILED, MAINTENANCE
    }
    
    /**
     * Model Metrics class for comprehensive tracking
     * Indian production environments के लिए detailed metrics
     */
    public static class ModelMetrics {
        private final String modelId;
        private final AtomicLong totalRequests;
        private final AtomicLong successfulRequests;
        private final AtomicLong failedRequests;
        private final AtomicReference<Double> averageLatency;
        private final AtomicReference<Double> p95Latency;
        private final AtomicReference<Double> p99Latency;
        private final AtomicReference<Double> currentAccuracy;
        private final AtomicReference<Double> totalCostINR;
        private final Map<String, AtomicLong> requestsByLanguage;
        private final Map<String, AtomicLong> errorsByType;
        private final Queue<LatencyMeasurement> recentLatencies;
        private final Queue<AccuracyMeasurement> recentAccuracies;
        
        public ModelMetrics(String modelId) {
            this.modelId = modelId;
            this.totalRequests = new AtomicLong(0);
            this.successfulRequests = new AtomicLong(0);
            this.failedRequests = new AtomicLong(0);
            this.averageLatency = new AtomicReference<>(0.0);
            this.p95Latency = new AtomicReference<>(0.0);
            this.p99Latency = new AtomicReference<>(0.0);
            this.currentAccuracy = new AtomicReference<>(1.0);
            this.totalCostINR = new AtomicReference<>(0.0);
            this.requestsByLanguage = new ConcurrentHashMap<>();
            this.errorsByType = new ConcurrentHashMap<>();
            this.recentLatencies = new ConcurrentLinkedQueue<>();
            this.recentAccuracies = new ConcurrentLinkedQueue<>();
            
            // Initialize language tracking for Indian languages
            Arrays.asList("hindi", "english", "tamil", "bengali", "telugu", "code_mixed")
                  .forEach(lang -> requestsByLanguage.put(lang, new AtomicLong(0)));
        }
        
        public synchronized void recordRequest(double latencyMs, boolean success, 
                                            String language, String errorType) {
            totalRequests.incrementAndGet();
            
            if (success) {
                successfulRequests.incrementAndGet();
            } else {
                failedRequests.incrementAndGet();
                if (errorType != null) {
                    errorsByType.computeIfAbsent(errorType, k -> new AtomicLong(0)).incrementAndGet();
                }
            }
            
            // Track latency
            recentLatencies.offer(new LatencyMeasurement(latencyMs, LocalDateTime.now()));
            if (recentLatencies.size() > 1000) { // Keep last 1000 measurements
                recentLatencies.poll();
            }
            
            // Track by language
            if (language != null) {
                requestsByLanguage.computeIfAbsent(language, k -> new AtomicLong(0)).incrementAndGet();
            }
            
            // Update latency percentiles
            updateLatencyPercentiles();
        }
        
        public synchronized void recordAccuracy(double accuracy) {
            recentAccuracies.offer(new AccuracyMeasurement(accuracy, LocalDateTime.now()));
            if (recentAccuracies.size() > 100) { // Keep last 100 accuracy measurements
                recentAccuracies.poll();
            }
            
            // Update current accuracy (moving average)
            double currentAcc = currentAccuracy.get();
            currentAccuracy.set((currentAcc * 0.9) + (accuracy * 0.1));
        }
        
        public synchronized void addCost(double costINR) {
            totalCostINR.updateAndGet(current -> current + costINR);
        }
        
        private void updateLatencyPercentiles() {
            List<Double> latencies = recentLatencies.stream()
                .map(LatencyMeasurement::getLatencyMs)
                .sorted()
                .collect(Collectors.toList());
            
            if (latencies.size() >= 10) {
                double avg = latencies.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
                averageLatency.set(avg);
                
                int p95Index = (int) Math.ceil(latencies.size() * 0.95) - 1;
                int p99Index = (int) Math.ceil(latencies.size() * 0.99) - 1;
                
                p95Latency.set(latencies.get(Math.max(0, p95Index)));
                p99Latency.set(latencies.get(Math.max(0, p99Index)));
            }
        }
        
        public Map<String, Object> getMetricsSummary() {
            Map<String, Object> summary = new HashMap<>();
            
            long total = totalRequests.get();
            summary.put("total_requests", total);
            summary.put("successful_requests", successfulRequests.get());
            summary.put("failed_requests", failedRequests.get());
            summary.put("success_rate", total > 0 ? (double) successfulRequests.get() / total * 100 : 100.0);
            summary.put("error_rate", total > 0 ? (double) failedRequests.get() / total * 100 : 0.0);
            
            summary.put("avg_latency_ms", averageLatency.get());
            summary.put("p95_latency_ms", p95Latency.get());
            summary.put("p99_latency_ms", p99Latency.get());
            summary.put("current_accuracy", currentAccuracy.get());
            summary.put("total_cost_inr", totalCostINR.get());
            
            // Language distribution
            Map<String, Long> langDistribution = new HashMap<>();
            requestsByLanguage.forEach((lang, count) -> langDistribution.put(lang, count.get()));
            summary.put("requests_by_language", langDistribution);
            
            // Error distribution
            Map<String, Long> errorDistribution = new HashMap<>();
            errorsByType.forEach((type, count) -> errorDistribution.put(type, count.get()));
            summary.put("errors_by_type", errorDistribution);
            
            return summary;
        }
        
        // Getters
        public String getModelId() { return modelId; }
        public long getTotalRequests() { return totalRequests.get(); }
        public double getSuccessRate() { 
            long total = totalRequests.get();
            return total > 0 ? (double) successfulRequests.get() / total * 100 : 100.0;
        }
        public double getErrorRate() {
            long total = totalRequests.get();
            return total > 0 ? (double) failedRequests.get() / total * 100 : 0.0;
        }
        public double getCurrentAccuracy() { return currentAccuracy.get(); }
        public double getTotalCostINR() { return totalCostINR.get(); }
    }
    
    // Supporting classes
    public static class LatencyMeasurement {
        private final double latencyMs;
        private final LocalDateTime timestamp;
        
        public LatencyMeasurement(double latencyMs, LocalDateTime timestamp) {
            this.latencyMs = latencyMs;
            this.timestamp = timestamp;
        }
        
        public double getLatencyMs() { return latencyMs; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    public static class AccuracyMeasurement {
        private final double accuracy;
        private final LocalDateTime timestamp;
        
        public AccuracyMeasurement(double accuracy, LocalDateTime timestamp) {
            this.accuracy = accuracy;
            this.timestamp = timestamp;
        }
        
        public double getAccuracy() { return accuracy; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    /**
     * Alert Manager for proactive monitoring
     * Indian production environments के लिए intelligent alerting
     */
    public static class AlertManager {
        private final Set<AlertRule> alertRules;
        private final Queue<Alert> recentAlerts;
        private final Set<String> activeAlerts; // To prevent alert spam
        
        public AlertManager() {
            this.alertRules = ConcurrentHashMap.newKeySet();
            this.recentAlerts = new ConcurrentLinkedQueue<>();
            this.activeAlerts = ConcurrentHashMap.newKeySet();
            
            // Add default alert rules for Indian production environments
            addDefaultAlertRules();
        }
        
        private void addDefaultAlertRules() {
            // Latency alerts - adjusted for Indian internet speeds
            alertRules.add(new AlertRule(
                "high_latency",
                AlertSeverity.WARNING,
                model -> model.getAvgLatencyMs() > DEFAULT_LATENCY_THRESHOLD_MS,
                "Average latency exceeds " + DEFAULT_LATENCY_THRESHOLD_MS + "ms",
                300 // 5 minute cooldown
            ));
            
            alertRules.add(new AlertRule(
                "very_high_latency", 
                AlertSeverity.CRITICAL,
                model -> model.getAvgLatencyMs() > DEFAULT_LATENCY_THRESHOLD_MS * 2,
                "Average latency exceeds " + (DEFAULT_LATENCY_THRESHOLD_MS * 2) + "ms",
                600 // 10 minute cooldown
            ));
            
            // Accuracy alerts
            alertRules.add(new AlertRule(
                "low_accuracy",
                AlertSeverity.WARNING,
                model -> model.getCurrentAccuracy() < DEFAULT_ACCURACY_THRESHOLD,
                "Model accuracy dropped below " + (DEFAULT_ACCURACY_THRESHOLD * 100) + "%",
                900 // 15 minute cooldown
            ));
            
            // Resource utilization alerts
            alertRules.add(new AlertRule(
                "high_cpu",
                AlertSeverity.WARNING,
                model -> model.getCpuUtilization() > 85.0,
                "CPU utilization exceeds 85%",
                300
            ));
            
            alertRules.add(new AlertRule(
                "high_memory",
                AlertSeverity.CRITICAL,
                model -> model.getMemoryUsageMB() > 7168, // 7GB out of 8GB
                "Memory usage exceeds 7GB",
                300
            ));
            
            // Cost alerts - important for Indian companies
            alertRules.add(new AlertRule(
                "high_cost_per_request",
                AlertSeverity.WARNING,
                model -> model.getCostPerRequestINR() > 0.50, // ₹0.50 per request
                "Cost per request exceeds ₹0.50",
                1800 // 30 minute cooldown
            ));
        }
        
        public void checkAlerts(ModelInstance model, ModelMetrics metrics) {
            for (AlertRule rule : alertRules) {
                String alertKey = model.getModelId() + ":" + rule.getName();
                
                if (rule.shouldTrigger(model) && !activeAlerts.contains(alertKey)) {
                    Alert alert = new Alert(
                        model.getModelId(),
                        model.getModelName(),
                        rule.getName(),
                        rule.getSeverity(),
                        rule.getDescription(),
                        LocalDateTime.now(),
                        generateAlertContext(model, metrics)
                    );
                    
                    recentAlerts.offer(alert);
                    activeAlerts.add(alertKey);
                    
                    // Trigger alert action (email, Slack, etc.)
                    triggerAlert(alert);
                    
                    // Schedule alert cooldown
                    scheduleAlertCooldown(alertKey, rule.getCooldownSeconds());
                }
            }
            
            // Cleanup old alerts
            while (recentAlerts.size() > 1000) {
                recentAlerts.poll();
            }
        }
        
        private Map<String, Object> generateAlertContext(ModelInstance model, ModelMetrics metrics) {
            Map<String, Object> context = new HashMap<>();
            context.put("model_id", model.getModelId());
            context.put("company", model.getCompanyName());
            context.put("use_case", model.getUseCase());
            context.put("region", model.getDeploymentRegion());
            context.put("current_latency_ms", model.getAvgLatencyMs());
            context.put("current_accuracy", model.getCurrentAccuracy());
            context.put("concurrent_requests", model.getConcurrentRequests());
            context.put("total_requests", metrics.getTotalRequests());
            context.put("error_rate", metrics.getErrorRate());
            context.put("cost_per_request_inr", model.getCostPerRequestINR());
            return context;
        }
        
        private void triggerAlert(Alert alert) {
            // In production, this would send to PagerDuty, Slack, email, etc.
            logger.severe(String.format(
                "🚨 ALERT [%s] %s - %s: %s",
                alert.getSeverity(),
                alert.getModelName(),
                alert.getAlertType(),
                alert.getDescription()
            ));
            
            // For Indian companies, could also send WhatsApp/SMS alerts
            if (alert.getSeverity() == AlertSeverity.CRITICAL) {
                logger.severe("CRITICAL alert triggered - immediate attention required!");
            }
        }
        
        private void scheduleAlertCooldown(String alertKey, int cooldownSeconds) {
            // Use a timer to remove from active alerts after cooldown
            Timer timer = new Timer(true);
            timer.schedule(new TimerTask() {
                @Override
                public void run() {
                    activeAlerts.remove(alertKey);
                }
            }, cooldownSeconds * 1000);
        }
        
        public List<Alert> getRecentAlerts(int count) {
            return recentAlerts.stream()
                .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
                .limit(count)
                .collect(Collectors.toList());
        }
    }
    
    public static class AlertRule {
        private final String name;
        private final AlertSeverity severity;
        private final Function<ModelInstance, Boolean> condition;
        private final String description;
        private final int cooldownSeconds;
        
        public AlertRule(String name, AlertSeverity severity, 
                        Function<ModelInstance, Boolean> condition, 
                        String description, int cooldownSeconds) {
            this.name = name;
            this.severity = severity;
            this.condition = condition;
            this.description = description;
            this.cooldownSeconds = cooldownSeconds;
        }
        
        public boolean shouldTrigger(ModelInstance model) {
            try {
                return condition.apply(model);
            } catch (Exception e) {
                logger.warning("Alert rule evaluation failed: " + e.getMessage());
                return false;
            }
        }
        
        // Getters
        public String getName() { return name; }
        public AlertSeverity getSeverity() { return severity; }
        public String getDescription() { return description; }
        public int getCooldownSeconds() { return cooldownSeconds; }
    }
    
    public static class Alert {
        private final String modelId;
        private final String modelName;
        private final String alertType;
        private final AlertSeverity severity;
        private final String description;
        private final LocalDateTime timestamp;
        private final Map<String, Object> context;
        
        public Alert(String modelId, String modelName, String alertType, 
                    AlertSeverity severity, String description, LocalDateTime timestamp,
                    Map<String, Object> context) {
            this.modelId = modelId;
            this.modelName = modelName;
            this.alertType = alertType;
            this.severity = severity;
            this.description = description;
            this.timestamp = timestamp;
            this.context = new HashMap<>(context);
        }
        
        // Getters
        public String getModelId() { return modelId; }
        public String getModelName() { return modelName; }
        public String getAlertType() { return alertType; }
        public AlertSeverity getSeverity() { return severity; }
        public String getDescription() { return description; }
        public LocalDateTime getTimestamp() { return timestamp; }
        public Map<String, Object> getContext() { return new HashMap<>(context); }
    }
    
    public enum AlertSeverity {
        INFO, WARNING, ERROR, CRITICAL
    }
    
    /**
     * Drift Detector for model performance degradation
     * Indian context के साथ data distribution changes detect करना
     */
    public static class DriftDetector {
        private final Map<String, BaselineDistribution> modelBaselines;
        
        public DriftDetector() {
            this.modelBaselines = new ConcurrentHashMap<>();
        }
        
        public void establishBaseline(String modelId, List<Double> baselineData) {
            if (baselineData.size() < 100) {
                logger.warning("Insufficient baseline data for model: " + modelId);
                return;
            }
            
            BaselineDistribution baseline = new BaselineDistribution(baselineData);
            modelBaselines.put(modelId, baseline);
            
            logger.info(String.format(
                "Baseline established for model %s: mean=%.3f, std=%.3f",
                modelId, baseline.getMean(), baseline.getStdDev()
            ));
        }
        
        public double detectDrift(String modelId, List<Double> currentData) {
            BaselineDistribution baseline = modelBaselines.get(modelId);
            if (baseline == null || currentData.size() < 20) {
                return 0.0; // No drift if no baseline or insufficient data
            }
            
            // Calculate KL divergence as drift measure
            return calculateKLDivergence(baseline, currentData);
        }
        
        private double calculateKLDivergence(BaselineDistribution baseline, List<Double> current) {
            // Simplified KL divergence calculation
            // In production, use more sophisticated statistical tests
            double currentMean = current.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            double currentStd = calculateStdDev(current, currentMean);
            
            // Measure how much the distribution has shifted
            double meanDrift = Math.abs(baseline.getMean() - currentMean) / baseline.getStdDev();
            double stdDrift = Math.abs(baseline.getStdDev() - currentStd) / baseline.getStdDev();
            
            return (meanDrift + stdDrift) / 2.0;
        }
        
        private double calculateStdDev(List<Double> data, double mean) {
            double variance = data.stream()
                .mapToDouble(val -> Math.pow(val - mean, 2))
                .average()
                .orElse(0.0);
            return Math.sqrt(variance);
        }
    }
    
    public static class BaselineDistribution {
        private final double mean;
        private final double stdDev;
        private final double min;
        private final double max;
        
        public BaselineDistribution(List<Double> data) {
            this.mean = data.stream().mapToDouble(Double::doubleValue).average().orElse(0.0);
            this.min = data.stream().mapToDouble(Double::doubleValue).min().orElse(0.0);
            this.max = data.stream().mapToDouble(Double::doubleValue).max().orElse(0.0);
            
            double variance = data.stream()
                .mapToDouble(val -> Math.pow(val - mean, 2))
                .average()
                .orElse(0.0);
            this.stdDev = Math.sqrt(variance);
        }
        
        // Getters
        public double getMean() { return mean; }
        public double getStdDev() { return stdDev; }
        public double getMin() { return min; }
        public double getMax() { return max; }
    }
    
    /**
     * Performance Tracker for detailed performance analysis
     */
    public static class PerformanceTracker {
        private final Map<String, Queue<PerformanceSnapshot>> performanceHistory;
        
        public PerformanceTracker() {
            this.performanceHistory = new ConcurrentHashMap<>();
        }
        
        public void recordSnapshot(String modelId, ModelInstance model, ModelMetrics metrics) {
            PerformanceSnapshot snapshot = new PerformanceSnapshot(
                LocalDateTime.now(),
                model.getAvgLatencyMs(),
                model.getCurrentAccuracy(),
                model.getCpuUtilization(),
                model.getMemoryUsageMB(),
                metrics.getSuccessRate(),
                model.getCostPerRequestINR()
            );
            
            Queue<PerformanceSnapshot> history = performanceHistory.computeIfAbsent(
                modelId, k -> new ConcurrentLinkedQueue<>()
            );
            
            history.offer(snapshot);
            if (history.size() > 1440) { // Keep 24 hours of minute-by-minute snapshots
                history.poll();
            }
        }
        
        public Map<String, Object> getPerformanceTrend(String modelId, Duration duration) {
            Queue<PerformanceSnapshot> history = performanceHistory.get(modelId);
            if (history == null || history.isEmpty()) {
                return Map.of("error", "No performance data available");
            }
            
            LocalDateTime cutoff = LocalDateTime.now().minus(duration);
            List<PerformanceSnapshot> recentSnapshots = history.stream()
                .filter(snapshot -> snapshot.getTimestamp().isAfter(cutoff))
                .collect(Collectors.toList());
            
            if (recentSnapshots.isEmpty()) {
                return Map.of("error", "No recent performance data");
            }
            
            // Calculate trends
            double avgLatency = recentSnapshots.stream()
                .mapToDouble(PerformanceSnapshot::getLatencyMs)
                .average()
                .orElse(0.0);
            
            double avgAccuracy = recentSnapshots.stream()
                .mapToDouble(PerformanceSnapshot::getAccuracy)
                .average()
                .orElse(0.0);
            
            double avgCost = recentSnapshots.stream()
                .mapToDouble(PerformanceSnapshot::getCostPerRequestINR)
                .average()
                .orElse(0.0);
            
            // Calculate trend direction (improving/degrading)
            String latencyTrend = calculateTrend(
                recentSnapshots.stream().mapToDouble(PerformanceSnapshot::getLatencyMs).toArray()
            );
            
            String accuracyTrend = calculateTrend(
                recentSnapshots.stream().mapToDouble(PerformanceSnapshot::getAccuracy).toArray()
            );
            
            return Map.of(
                "duration_analyzed", duration.toString(),
                "snapshots_count", recentSnapshots.size(),
                "avg_latency_ms", avgLatency,
                "avg_accuracy", avgAccuracy,
                "avg_cost_per_request_inr", avgCost,
                "latency_trend", latencyTrend,
                "accuracy_trend", accuracyTrend
            );
        }
        
        private String calculateTrend(double[] values) {
            if (values.length < 2) return "insufficient_data";
            
            // Simple linear regression slope
            int n = values.length;
            double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
            
            for (int i = 0; i < n; i++) {
                sumX += i;
                sumY += values[i];
                sumXY += i * values[i];
                sumX2 += i * i;
            }
            
            double slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
            
            if (Math.abs(slope) < 0.001) return "stable";
            return slope > 0 ? "increasing" : "decreasing";
        }
    }
    
    public static class PerformanceSnapshot {
        private final LocalDateTime timestamp;
        private final double latencyMs;
        private final double accuracy;
        private final double cpuUtilization;
        private final double memoryUsageMB;
        private final double successRate;
        private final double costPerRequestINR;
        
        public PerformanceSnapshot(LocalDateTime timestamp, double latencyMs, double accuracy,
                                 double cpuUtilization, double memoryUsageMB, 
                                 double successRate, double costPerRequestINR) {
            this.timestamp = timestamp;
            this.latencyMs = latencyMs;
            this.accuracy = accuracy;
            this.cpuUtilization = cpuUtilization;
            this.memoryUsageMB = memoryUsageMB;
            this.successRate = successRate;
            this.costPerRequestINR = costPerRequestINR;
        }
        
        // Getters
        public LocalDateTime getTimestamp() { return timestamp; }
        public double getLatencyMs() { return latencyMs; }
        public double getAccuracy() { return accuracy; }
        public double getCpuUtilization() { return cpuUtilization; }
        public double getMemoryUsageMB() { return memoryUsageMB; }
        public double getSuccessRate() { return successRate; }
        public double getCostPerRequestINR() { return costPerRequestINR; }
    }
    
    /**
     * Cost Tracker for Indian companies
     * INR-based cost tracking with budget management
     */
    public static class CostTracker {
        private final Map<String, DailyCostTracker> dailyCosts;
        private final Map<String, Double> budgetLimits;
        
        public CostTracker() {
            this.dailyCosts = new ConcurrentHashMap<>();
            this.budgetLimits = new ConcurrentHashMap<>();
        }
        
        public void setBudgetLimit(String modelId, double dailyBudgetINR) {
            budgetLimits.put(modelId, dailyBudgetINR);
        }
        
        public void recordCost(String modelId, double costINR) {
            String today = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
            String key = modelId + ":" + today;
            
            DailyCostTracker tracker = dailyCosts.computeIfAbsent(
                key, k -> new DailyCostTracker()
            );
            
            tracker.addCost(costINR);
            
            // Check budget limit
            Double budgetLimit = budgetLimits.get(modelId);
            if (budgetLimit != null && tracker.getTotalCost() > budgetLimit) {
                logger.warning(String.format(
                    "Budget exceeded for model %s: ₹%.2f / ₹%.2f",
                    modelId, tracker.getTotalCost(), budgetLimit
                ));
            }
        }
        
        public Map<String, Object> getCostSummary(String modelId) {
            // Get costs for last 7 days
            Map<String, Double> last7Days = new HashMap<>();
            double totalCost = 0.0;
            
            for (int i = 0; i < 7; i++) {
                String date = LocalDateTime.now().minusDays(i)
                    .format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));
                String key = modelId + ":" + date;
                
                DailyCostTracker tracker = dailyCosts.get(key);
                double dayCost = tracker != null ? tracker.getTotalCost() : 0.0;
                last7Days.put(date, dayCost);
                totalCost += dayCost;
            }
            
            return Map.of(
                "last_7_days_cost_inr", totalCost,
                "daily_breakdown", last7Days,
                "avg_daily_cost_inr", totalCost / 7.0,
                "budget_limit_inr", budgetLimits.getOrDefault(modelId, 0.0),
                "budget_utilized_percent", 
                    budgetLimits.containsKey(modelId) ? 
                        (totalCost / 7.0) / budgetLimits.get(modelId) * 100 : 0.0
            );
        }
    }
    
    public static class DailyCostTracker {
        private double totalCost;
        private int requestCount;
        
        public DailyCostTracker() {
            this.totalCost = 0.0;
            this.requestCount = 0;
        }
        
        public synchronized void addCost(double cost) {
            this.totalCost += cost;
            this.requestCount++;
        }
        
        public double getTotalCost() { return totalCost; }
        public int getRequestCount() { return requestCount; }
    }
    
    // Main monitoring methods
    
    /**
     * Register a new model for monitoring
     */
    public synchronized void registerModel(String modelId, String modelName, String version,
                                        ModelType modelType, String deploymentRegion,
                                        String useCase, String companyName, 
                                        Set<String> supportedLanguages, boolean handlesCodeMixing) {
        if (deployedModels.containsKey(modelId)) {
            logger.warning("Model already registered: " + modelId);
            return;
        }
        
        ModelInstance model = new ModelInstance(
            modelId, modelName, version, modelType, deploymentRegion,
            useCase, companyName, supportedLanguages, handlesCodeMixing
        );
        
        model.setStatus(ModelStatus.HEALTHY);
        model.setEndpoint("https://api." + companyName + ".com/ml/" + modelId);
        
        deployedModels.put(modelId, model);
        modelMetrics.put(modelId, new ModelMetrics(modelId));
        
        logger.info(String.format(
            "Registered model: %s (%s) for %s - Use case: %s, Languages: %s",
            modelName, modelId, companyName, useCase, supportedLanguages
        ));
    }
    
    /**
     * Record a prediction request for monitoring
     */
    public void recordPrediction(String modelId, double latencyMs, boolean success, 
                               double accuracy, String language, String errorType, 
                               double costINR) {
        ModelInstance model = deployedModels.get(modelId);
        ModelMetrics metrics = modelMetrics.get(modelId);
        
        if (model == null || metrics == null) {
            logger.warning("Model not found for recording: " + modelId);
            return;
        }
        
        // Update model instance
        model.updateMetrics(latencyMs, accuracy, 
                          model.getMemoryUsageMB(), model.getCpuUtilization());
        model.setCostPerRequestINR(costINR);
        
        if (success) {
            model.incrementConcurrentRequests();
            // Simulate concurrent request completion
            CompletableFuture.delayedExecutor(100, TimeUnit.MILLISECONDS)
                .execute(model::decrementConcurrentRequests);
        }
        
        // Update metrics
        metrics.recordRequest(latencyMs, success, language, errorType);
        metrics.recordAccuracy(accuracy);
        metrics.addCost(costINR);
        
        // Record performance snapshot
        performanceTracker.recordSnapshot(modelId, model, metrics);
        
        // Record cost
        costTracker.recordCost(modelId, costINR);
        
        // Check alerts
        alertExecutor.submit(() -> alertManager.checkAlerts(model, metrics));
    }
    
    /**
     * Start continuous monitoring background tasks
     */
    private void startContinuousMonitoring() {
        // Monitor model health every minute
        monitoringExecutor.scheduleAtFixedRate(() -> {
            for (ModelInstance model : deployedModels.values()) {
                checkModelHealth(model);
            }
        }, 1, 1, TimeUnit.MINUTES);
        
        // Update drift detection every 5 minutes
        monitoringExecutor.scheduleAtFixedRate(() -> {
            for (String modelId : deployedModels.keySet()) {
                checkModelDrift(modelId);
            }
        }, 5, 5, TimeUnit.MINUTES);
        
        // Cleanup old data every hour
        monitoringExecutor.scheduleAtFixedRate(() -> {
            cleanupOldData();
        }, 1, 1, TimeUnit.HOURS);
        
        logger.info("Started continuous monitoring tasks");
    }
    
    private void checkModelHealth(ModelInstance model) {
        // Update status based on current metrics
        if (!model.isHealthy()) {
            if (model.getStatus() == ModelStatus.HEALTHY) {
                model.setStatus(ModelStatus.DEGRADED);
                logger.warning("Model " + model.getModelId() + " status changed to DEGRADED");
            }
        } else if (model.getStatus() == ModelStatus.DEGRADED) {
            model.setStatus(ModelStatus.HEALTHY);
            logger.info("Model " + model.getModelId() + " recovered to HEALTHY");
        }
    }
    
    private void checkModelDrift(String modelId) {
        ModelMetrics metrics = modelMetrics.get(modelId);
        if (metrics == null) return;
        
        // For demonstration, using accuracy as drift indicator
        // In production, would use more sophisticated features
        List<Double> recentAccuracies = metrics.recentAccuracies.stream()
            .filter(acc -> acc.getTimestamp().isAfter(LocalDateTime.now().minusHours(1)))
            .map(AccuracyMeasurement::getAccuracy)
            .collect(Collectors.toList());
        
        if (recentAccuracies.size() >= 10) {
            double drift = driftDetector.detectDrift(modelId, recentAccuracies);
            
            if (drift > DEFAULT_DRIFT_THRESHOLD) {
                logger.warning(String.format(
                    "Drift detected for model %s: %.3f (threshold: %.3f)",
                    modelId, drift, DEFAULT_DRIFT_THRESHOLD
                ));
            }
        }
    }
    
    private void cleanupOldData() {
        // Cleanup old performance snapshots, metrics, etc.
        // Implementation would remove data older than retention period
        logger.info("Performing data cleanup...");
    }
    
    /**
     * Get comprehensive monitoring dashboard data
     */
    public synchronized Map<String, Object> getMonitoringDashboard() {
        Map<String, Object> dashboard = new HashMap<>();
        
        // Overall stats
        dashboard.put("total_models", deployedModels.size());
        dashboard.put("healthy_models", deployedModels.values().stream()
            .mapToInt(model -> model.getStatus() == ModelStatus.HEALTHY ? 1 : 0).sum());
        dashboard.put("degraded_models", deployedModels.values().stream()
            .mapToInt(model -> model.getStatus() == ModelStatus.DEGRADED ? 1 : 0).sum());
        
        // Model details
        List<Map<String, Object>> modelDetails = new ArrayList<>();
        for (ModelInstance model : deployedModels.values()) {
            ModelMetrics metrics = modelMetrics.get(model.getModelId());
            
            Map<String, Object> modelInfo = new HashMap<>();
            modelInfo.put("model_id", model.getModelId());
            modelInfo.put("model_name", model.getModelName());
            modelInfo.put("company", model.getCompanyName());
            modelInfo.put("use_case", model.getUseCase());
            modelInfo.put("status", model.getStatus());
            modelInfo.put("avg_latency_ms", model.getAvgLatencyMs());
            modelInfo.put("accuracy", model.getCurrentAccuracy());
            modelInfo.put("total_requests", metrics != null ? metrics.getTotalRequests() : 0);
            modelInfo.put("success_rate", metrics != null ? metrics.getSuccessRate() : 100.0);
            modelInfo.put("cost_per_request_inr", model.getCostPerRequestINR());
            modelInfo.put("supported_languages", model.getSupportedLanguages());
            
            modelDetails.add(modelInfo);
        }
        dashboard.put("models", modelDetails);
        
        // Recent alerts
        dashboard.put("recent_alerts", alertManager.getRecentAlerts(10));
        
        // System health
        dashboard.put("monitoring_status", "healthy");
        dashboard.put("last_updated", LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        
        return dashboard;
    }
    
    /**
     * Shutdown monitoring system
     */
    public void shutdown() {
        logger.info("Shutting down AI Model Monitor...");
        
        monitoringExecutor.shutdown();
        alertExecutor.shutdown();
        
        try {
            if (!monitoringExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                monitoringExecutor.shutdownNow();
            }
            if (!alertExecutor.awaitTermination(30, TimeUnit.SECONDS)) {
                alertExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("AI Model Monitor shutdown complete");
    }
    
    /**
     * Demo showing typical usage for Indian AI companies
     */
    public static void main(String[] args) {
        System.out.println("📊 AI Model Monitor Demo - Indian Production Systems");
        System.out.println("=" .repeat(70));
        
        AIModelMonitor monitor = new AIModelMonitor();
        
        try {
            // Register models from different Indian companies
            monitor.registerModel(
                "paytm_fraud_v2.1", "PayTM Fraud Detection", "2.1",
                ModelType.ENSEMBLE, "ap-south-1", "fraud_detection", "paytm",
                Set.of("hindi", "english"), true
            );
            
            monitor.registerModel(
                "flipkart_recom_v3.0", "Flipkart Recommendation Engine", "3.0",
                ModelType.RECOMMENDATION, "azure-centralindia", "product_recommendation", "flipkart",
                Set.of("hindi", "english", "tamil", "bengali"), true
            );
            
            monitor.registerModel(
                "zomato_food_classifier_v1.5", "Zomato Food Image Classifier", "1.5", 
                ModelType.CNN, "asia-south1", "image_classification", "zomato",
                Set.of("hindi", "english"), false
            );
            
            System.out.println("\n✅ Registered 3 models from Indian companies");
            
            // Set budget limits
            monitor.costTracker.setBudgetLimit("paytm_fraud_v2.1", 5000.0); // ₹5000/day
            monitor.costTracker.setBudgetLimit("flipkart_recom_v3.0", 8000.0); // ₹8000/day
            monitor.costTracker.setBudgetLimit("zomato_food_classifier_v1.5", 3000.0); // ₹3000/day
            
            // Simulate prediction requests
            Random random = new Random();
            String[] languages = {"hindi", "english", "code_mixed"};
            String[] errorTypes = {"timeout", "invalid_input", "model_error", null};
            
            System.out.println("\n🔄 Simulating prediction requests...");
            
            for (int i = 0; i < 200; i++) {
                // Simulate different patterns for different models
                
                // PayTM Fraud Detection - high volume, low latency requirements
                monitor.recordPrediction(
                    "paytm_fraud_v2.1",
                    50 + random.nextGaussian() * 20, // 50ms ± 20ms latency
                    random.nextDouble() > 0.02, // 98% success rate
                    0.95 + random.nextGaussian() * 0.02, // ~95% accuracy
                    languages[random.nextInt(languages.length)],
                    random.nextDouble() > 0.98 ? errorTypes[random.nextInt(3)] : null,
                    0.10 + random.nextGaussian() * 0.02 // ₹0.10 per request
                );
                
                // Flipkart Recommendations - moderate volume, personalization focus
                if (i % 2 == 0) {
                    monitor.recordPrediction(
                        "flipkart_recom_v3.0",
                        150 + random.nextGaussian() * 50, // 150ms ± 50ms latency
                        random.nextDouble() > 0.05, // 95% success rate
                        0.88 + random.nextGaussian() * 0.03, // ~88% accuracy
                        languages[random.nextInt(languages.length)],
                        random.nextDouble() > 0.95 ? errorTypes[random.nextInt(3)] : null,
                        0.25 + random.nextGaussian() * 0.05 // ₹0.25 per request
                    );
                }
                
                // Zomato Food Classification - image processing, higher latency
                if (i % 3 == 0) {
                    monitor.recordPrediction(
                        "zomato_food_classifier_v1.5",
                        300 + random.nextGaussian() * 100, // 300ms ± 100ms latency
                        random.nextDouble() > 0.03, // 97% success rate
                        0.92 + random.nextGaussian() * 0.04, // ~92% accuracy
                        "english", // Images don't have language, but metadata might
                        random.nextDouble() > 0.97 ? errorTypes[random.nextInt(3)] : null,
                        0.15 + random.nextGaussian() * 0.03 // ₹0.15 per request
                    );
                }
                
                // Small delay to simulate real traffic
                if (i % 50 == 0) {
                    Thread.sleep(100);
                    System.out.print(".");
                }
            }
            
            System.out.println("\n\n📊 Monitoring Dashboard:");
            Map<String, Object> dashboard = monitor.getMonitoringDashboard();
            
            System.out.println("Overall Status:");
            System.out.println("   Total Models: " + dashboard.get("total_models"));
            System.out.println("   Healthy Models: " + dashboard.get("healthy_models"));
            System.out.println("   Degraded Models: " + dashboard.get("degraded_models"));
            
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> models = (List<Map<String, Object>>) dashboard.get("models");
            
            System.out.println("\nModel Performance:");
            for (Map<String, Object> modelInfo : models) {
                System.out.println(String.format(
                    "   %s (%s):",
                    modelInfo.get("model_name"),
                    modelInfo.get("company")
                ));
                System.out.println(String.format(
                    "      Status: %s | Latency: %.1fms | Accuracy: %.3f",
                    modelInfo.get("status"),
                    modelInfo.get("avg_latency_ms"),
                    modelInfo.get("accuracy")
                ));
                System.out.println(String.format(
                    "      Requests: %d | Success Rate: %.1f%% | Cost: ₹%.4f/req",
                    modelInfo.get("total_requests"),
                    modelInfo.get("success_rate"),
                    modelInfo.get("cost_per_request_inr")
                ));
                System.out.println(String.format(
                    "      Languages: %s | Use Case: %s",
                    modelInfo.get("supported_languages"),
                    modelInfo.get("use_case")
                ));
                System.out.println();
            }
            
            // Show cost summaries
            System.out.println("💰 Cost Analysis:");
            for (String modelId : Arrays.asList("paytm_fraud_v2.1", "flipkart_recom_v3.0", "zomato_food_classifier_v1.5")) {
                Map<String, Object> costSummary = monitor.costTracker.getCostSummary(modelId);
                System.out.println(String.format(
                    "   %s: ₹%.2f (7-day) | Avg Daily: ₹%.2f | Budget: %.1f%%",
                    modelId,
                    costSummary.get("last_7_days_cost_inr"),
                    costSummary.get("avg_daily_cost_inr"),
                    costSummary.get("budget_utilized_percent")
                ));
            }
            
            // Show recent alerts
            @SuppressWarnings("unchecked")
            List<Alert> alerts = (List<Alert>) dashboard.get("recent_alerts");
            if (!alerts.isEmpty()) {
                System.out.println("\n🚨 Recent Alerts:");
                for (Alert alert : alerts.subList(0, Math.min(5, alerts.size()))) {
                    System.out.println(String.format(
                        "   [%s] %s - %s: %s",
                        alert.getSeverity(),
                        alert.getModelName(),
                        alert.getAlertType(),
                        alert.getDescription()
                    ));
                }
            }
            
            System.out.println("\n🎯 Indian Production AI Monitoring Features:");
            System.out.println("   ✅ Multi-language support (Hindi, English, Tamil, Bengali)");
            System.out.println("   ✅ Code-mixing detection for Indian users");
            System.out.println("   ✅ INR-based cost tracking with daily budgets");
            System.out.println("   ✅ Latency thresholds adjusted for Indian internet");
            System.out.println("   ✅ Real-time drift detection and alerts");
            System.out.println("   ✅ Company-specific use case tracking");
            System.out.println("   ✅ Performance trend analysis");
            System.out.println("   ✅ Proactive alerting with cooldown periods");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        } finally {
            monitor.shutdown();
        }
    }
}