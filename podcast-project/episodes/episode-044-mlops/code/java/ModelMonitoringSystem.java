/**
 * Model Monitoring System - MLOps Episode 44
 * Production-ready ML model monitoring and alerting system
 * 
 * Author: Claude Code
 * Context: Real-time model monitoring system for production ML deployments
 */

package com.episode44.mlops;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.DoubleAdder;
import java.io.*;
import java.time.LocalDateTime;
import java.time.Duration;
import java.time.Instant;
import java.time.format.DateTimeFormatter;
import java.sql.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Production Model Monitoring System for MLOps
 * Mumbai me sabse comprehensive model monitoring!
 */
public class ModelMonitoringSystem {
    
    private static final Logger logger = LoggerFactory.getLogger(ModelMonitoringSystem.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    private final String dbPath;
    private final ScheduledExecutorService scheduler;
    private final ExecutorService alertExecutor;
    private final Map<String, ModelMonitor> modelMonitors = new ConcurrentHashMap<>();
    private final List<AlertHandler> alertHandlers = new CopyOnWriteArrayList<>();
    
    // Global monitoring state
    private volatile boolean isMonitoring = true;
    
    /**
     * Model monitoring configuration
     */
    public static class MonitoringConfig {
        @JsonProperty("model_id")
        private String modelId;
        
        @JsonProperty("monitoring_interval_seconds")
        private int monitoringIntervalSeconds = 60;
        
        @JsonProperty("performance_thresholds")
        private Map<String, Double> performanceThresholds;
        
        @JsonProperty("latency_threshold_ms")
        private double latencyThresholdMs = 1000.0;
        
        @JsonProperty("error_rate_threshold")
        private double errorRateThreshold = 0.05; // 5%
        
        @JsonProperty("data_drift_threshold")
        private double dataDriftThreshold = 0.1;
        
        @JsonProperty("traffic_anomaly_threshold")
        private double trafficAnomalyThreshold = 2.0; // 2x normal traffic
        
        @JsonProperty("alert_cooldown_minutes")
        private int alertCooldownMinutes = 15;
        
        @JsonProperty("enabled_checks")
        private Set<MonitoringCheck> enabledChecks;
        
        public MonitoringConfig() {
            this.performanceThresholds = new HashMap<>();
            this.enabledChecks = EnumSet.allOf(MonitoringCheck.class);
        }
        
        public MonitoringConfig(String modelId) {
            this();
            this.modelId = modelId;
            
            // Default thresholds
            this.performanceThresholds.put("accuracy", 0.85);
            this.performanceThresholds.put("precision", 0.80);
            this.performanceThresholds.put("recall", 0.75);
        }
        
        // Getters and setters
        public String getModelId() { return modelId; }
        public void setModelId(String modelId) { this.modelId = modelId; }
        
        public int getMonitoringIntervalSeconds() { return monitoringIntervalSeconds; }
        public void setMonitoringIntervalSeconds(int monitoringIntervalSeconds) { this.monitoringIntervalSeconds = monitoringIntervalSeconds; }
        
        public Map<String, Double> getPerformanceThresholds() { return performanceThresholds; }
        public void setPerformanceThresholds(Map<String, Double> performanceThresholds) { this.performanceThresholds = performanceThresholds; }
        
        public double getLatencyThresholdMs() { return latencyThresholdMs; }
        public void setLatencyThresholdMs(double latencyThresholdMs) { this.latencyThresholdMs = latencyThresholdMs; }
        
        public double getErrorRateThreshold() { return errorRateThreshold; }
        public void setErrorRateThreshold(double errorRateThreshold) { this.errorRateThreshold = errorRateThreshold; }
        
        public Set<MonitoringCheck> getEnabledChecks() { return enabledChecks; }
        public void setEnabledChecks(Set<MonitoringCheck> enabledChecks) { this.enabledChecks = enabledChecks; }
    }
    
    /**
     * Types of monitoring checks
     */
    public enum MonitoringCheck {
        PERFORMANCE_DEGRADATION,
        LATENCY_INCREASE,
        ERROR_RATE_SPIKE,
        DATA_DRIFT,
        TRAFFIC_ANOMALY,
        PREDICTION_DRIFT,
        FEATURE_DISTRIBUTION_SHIFT
    }
    
    /**
     * Alert severity levels
     */
    public enum AlertSeverity {
        INFO, WARNING, CRITICAL
    }
    
    /**
     * Monitoring alert
     */
    public static class MonitoringAlert {
        @JsonProperty("alert_id")
        private String alertId;
        
        @JsonProperty("model_id")
        private String modelId;
        
        @JsonProperty("check_type")
        private MonitoringCheck checkType;
        
        @JsonProperty("severity")
        private AlertSeverity severity;
        
        @JsonProperty("message")
        private String message;
        
        @JsonProperty("current_value")
        private double currentValue;
        
        @JsonProperty("threshold_value")
        private double thresholdValue;
        
        @JsonProperty("timestamp")
        private LocalDateTime timestamp;
        
        @JsonProperty("metadata")
        private Map<String, Object> metadata;
        
        @JsonProperty("is_resolved")
        private boolean isResolved;
        
        public MonitoringAlert() {
            this.alertId = UUID.randomUUID().toString();
            this.timestamp = LocalDateTime.now();
            this.metadata = new HashMap<>();
            this.isResolved = false;
        }
        
        public MonitoringAlert(String modelId, MonitoringCheck checkType, AlertSeverity severity, 
                             String message, double currentValue, double thresholdValue) {
            this();
            this.modelId = modelId;
            this.checkType = checkType;
            this.severity = severity;
            this.message = message;
            this.currentValue = currentValue;
            this.thresholdValue = thresholdValue;
        }
        
        // Getters and setters
        public String getAlertId() { return alertId; }
        public String getModelId() { return modelId; }
        public MonitoringCheck getCheckType() { return checkType; }
        public AlertSeverity getSeverity() { return severity; }
        public String getMessage() { return message; }
        public double getCurrentValue() { return currentValue; }
        public double getThresholdValue() { return thresholdValue; }
        public LocalDateTime getTimestamp() { return timestamp; }
        public Map<String, Object> getMetadata() { return metadata; }
        public boolean isResolved() { return isResolved; }
        public void setResolved(boolean resolved) { isResolved = resolved; }
    }
    
    /**
     * Model performance metrics
     */
    public static class ModelMetrics {
        private final AtomicLong requestCount = new AtomicLong(0);
        private final AtomicLong errorCount = new AtomicLong(0);
        private final DoubleAdder totalLatency = new DoubleAdder();
        private final Map<String, DoubleAdder> performanceMetrics = new ConcurrentHashMap<>();
        private final Queue<Double> latencyWindow = new ConcurrentLinkedQueue<>();
        private final Queue<Long> requestTimestamps = new ConcurrentLinkedQueue<>();
        
        // Feature statistics
        private final Map<String, FeatureStatistics> featureStats = new ConcurrentHashMap<>();
        
        public void recordRequest(double latencyMs, boolean isError, Map<String, Double> performance, 
                                 Map<String, Double> features) {
            long now = System.currentTimeMillis();
            
            // Basic metrics
            requestCount.incrementAndGet();
            if (isError) {
                errorCount.incrementAndGet();
            }
            
            totalLatency.add(latencyMs);
            
            // Performance metrics
            if (performance != null) {
                performance.forEach((metric, value) -> 
                    performanceMetrics.computeIfAbsent(metric, k -> new DoubleAdder()).add(value)
                );
            }
            
            // Latency window (keep last 1000 requests)
            latencyWindow.offer(latencyMs);
            if (latencyWindow.size() > 1000) {
                latencyWindow.poll();
            }
            
            // Request timestamps (keep last hour)
            requestTimestamps.offer(now);
            while (!requestTimestamps.isEmpty() && 
                   now - requestTimestamps.peek() > 3600000) { // 1 hour
                requestTimestamps.poll();
            }
            
            // Feature statistics
            if (features != null) {
                features.forEach((feature, value) -> {
                    featureStats.computeIfAbsent(feature, k -> new FeatureStatistics())
                              .addValue(value);
                });
            }
        }
        
        public double getAverageLatency() {
            long count = requestCount.get();
            return count > 0 ? totalLatency.sum() / count : 0.0;
        }
        
        public double getErrorRate() {
            long total = requestCount.get();
            return total > 0 ? (double) errorCount.get() / total : 0.0;
        }
        
        public double getRequestsPerSecond() {
            long now = System.currentTimeMillis();
            long count = requestTimestamps.stream()
                .mapToLong(timestamp -> 1L)
                .count();
            return count / 3600.0; // Requests per second over last hour
        }
        
        public double getP95Latency() {
            if (latencyWindow.isEmpty()) return 0.0;
            
            List<Double> sorted = new ArrayList<>(latencyWindow);
            Collections.sort(sorted);
            int index = (int) Math.ceil(0.95 * sorted.size()) - 1;
            return sorted.get(Math.max(0, index));
        }
        
        public Map<String, Double> getAveragePerformanceMetrics() {
            Map<String, Double> averages = new HashMap<>();
            long total = requestCount.get();
            
            if (total > 0) {
                performanceMetrics.forEach((metric, adder) -> 
                    averages.put(metric, adder.sum() / total)
                );
            }
            
            return averages;
        }
        
        public Map<String, FeatureStatistics> getFeatureStatistics() {
            return new HashMap<>(featureStats);
        }
        
        // Getters
        public long getRequestCount() { return requestCount.get(); }
        public long getErrorCount() { return errorCount.get(); }
    }
    
    /**
     * Feature statistics tracking
     */
    public static class FeatureStatistics {
        private final DoubleAdder sum = new DoubleAdder();
        private final DoubleAdder sumSquares = new DoubleAdder();
        private final AtomicLong count = new AtomicLong(0);
        private volatile double min = Double.MAX_VALUE;
        private volatile double max = Double.MIN_VALUE;
        private final Queue<Double> recentValues = new ConcurrentLinkedQueue<>();
        
        public synchronized void addValue(double value) {
            sum.add(value);
            sumSquares.add(value * value);
            count.incrementAndGet();
            
            if (value < min) min = value;
            if (value > max) max = value;
            
            // Keep recent values for drift detection
            recentValues.offer(value);
            if (recentValues.size() > 1000) {
                recentValues.poll();
            }
        }
        
        public double getMean() {
            long n = count.get();
            return n > 0 ? sum.sum() / n : 0.0;
        }
        
        public double getStandardDeviation() {
            long n = count.get();
            if (n <= 1) return 0.0;
            
            double mean = getMean();
            double variance = (sumSquares.sum() / n) - (mean * mean);
            return Math.sqrt(Math.max(0.0, variance));
        }
        
        public double getMin() { return min == Double.MAX_VALUE ? 0.0 : min; }
        public double getMax() { return max == Double.MIN_VALUE ? 0.0 : max; }
        public long getCount() { return count.get(); }
        public List<Double> getRecentValues() { return new ArrayList<>(recentValues); }
    }
    
    /**
     * Individual model monitor
     */
    public static class ModelMonitor {
        private final String modelId;
        private final MonitoringConfig config;
        private final ModelMetrics metrics;
        private final Map<MonitoringCheck, LocalDateTime> lastAlertTimes = new ConcurrentHashMap<>();
        
        // Baseline statistics for comparison
        private volatile ModelMetrics baselineMetrics;
        private volatile LocalDateTime baselineTimestamp;
        
        public ModelMonitor(String modelId, MonitoringConfig config) {
            this.modelId = modelId;
            this.config = config;
            this.metrics = new ModelMetrics();
            this.baselineTimestamp = LocalDateTime.now();
        }
        
        public void recordPrediction(double latencyMs, boolean isError, Map<String, Double> performance, 
                                   Map<String, Double> features) {
            metrics.recordRequest(latencyMs, isError, performance, features);
        }
        
        public void setBaseline() {
            this.baselineMetrics = this.metrics; // In production, create a snapshot
            this.baselineTimestamp = LocalDateTime.now();
            logger.info("Baseline set for model: {}", modelId);
        }
        
        public List<MonitoringAlert> checkHealth() {
            List<MonitoringAlert> alerts = new ArrayList<>();
            LocalDateTime now = LocalDateTime.now();
            
            for (MonitoringCheck check : config.getEnabledChecks()) {
                // Check cooldown period
                LocalDateTime lastAlert = lastAlertTimes.get(check);
                if (lastAlert != null && 
                    Duration.between(lastAlert, now).toMinutes() < config.alertCooldownMinutes) {
                    continue;
                }
                
                MonitoringAlert alert = performCheck(check);
                if (alert != null) {
                    alerts.add(alert);
                    lastAlertTimes.put(check, now);
                }
            }
            
            return alerts;
        }
        
        private MonitoringAlert performCheck(MonitoringCheck check) {
            switch (check) {
                case PERFORMANCE_DEGRADATION:
                    return checkPerformanceDegradation();
                case LATENCY_INCREASE:
                    return checkLatencyIncrease();
                case ERROR_RATE_SPIKE:
                    return checkErrorRateSpike();
                case DATA_DRIFT:
                    return checkDataDrift();
                case TRAFFIC_ANOMALY:
                    return checkTrafficAnomaly();
                default:
                    return null;
            }
        }
        
        private MonitoringAlert checkPerformanceDegradation() {
            Map<String, Double> currentPerformance = metrics.getAveragePerformanceMetrics();
            
            for (Map.Entry<String, Double> threshold : config.getPerformanceThresholds().entrySet()) {
                String metric = threshold.getKey();
                double thresholdValue = threshold.getValue();
                Double currentValue = currentPerformance.get(metric);
                
                if (currentValue != null && currentValue < thresholdValue) {
                    return new MonitoringAlert(
                        modelId,
                        MonitoringCheck.PERFORMANCE_DEGRADATION,
                        AlertSeverity.CRITICAL,
                        String.format("Performance degradation detected: %s = %.4f (threshold: %.4f)", 
                                    metric, currentValue, thresholdValue),
                        currentValue,
                        thresholdValue
                    );
                }
            }
            
            return null;
        }
        
        private MonitoringAlert checkLatencyIncrease() {
            double currentLatency = metrics.getAverageLatency();
            double threshold = config.getLatencyThresholdMs();
            
            if (currentLatency > threshold) {
                return new MonitoringAlert(
                    modelId,
                    MonitoringCheck.LATENCY_INCREASE,
                    currentLatency > threshold * 2 ? AlertSeverity.CRITICAL : AlertSeverity.WARNING,
                    String.format("High latency detected: %.2f ms (threshold: %.2f ms)", 
                                currentLatency, threshold),
                    currentLatency,
                    threshold
                );
            }
            
            return null;
        }
        
        private MonitoringAlert checkErrorRateSpike() {
            double currentErrorRate = metrics.getErrorRate();
            double threshold = config.getErrorRateThreshold();
            
            if (currentErrorRate > threshold) {
                return new MonitoringAlert(
                    modelId,
                    MonitoringCheck.ERROR_RATE_SPIKE,
                    currentErrorRate > threshold * 2 ? AlertSeverity.CRITICAL : AlertSeverity.WARNING,
                    String.format("High error rate detected: %.2f%% (threshold: %.2f%%)", 
                                currentErrorRate * 100, threshold * 100),
                    currentErrorRate,
                    threshold
                );
            }
            
            return null;
        }
        
        private MonitoringAlert checkDataDrift() {
            if (baselineMetrics == null) {
                return null; // No baseline set
            }
            
            Map<String, FeatureStatistics> currentStats = metrics.getFeatureStatistics();
            Map<String, FeatureStatistics> baselineStats = baselineMetrics.getFeatureStatistics();
            
            for (Map.Entry<String, FeatureStatistics> entry : currentStats.entrySet()) {
                String feature = entry.getKey();
                FeatureStatistics currentStat = entry.getValue();
                FeatureStatistics baselineStat = baselineStats.get(feature);
                
                if (baselineStat != null) {
                    // Simple drift detection using mean difference
                    double meanDiff = Math.abs(currentStat.getMean() - baselineStat.getMean()) / 
                                    Math.max(baselineStat.getStandardDeviation(), 0.001);
                    
                    if (meanDiff > config.getDataDriftThreshold()) {
                        MonitoringAlert alert = new MonitoringAlert(
                            modelId,
                            MonitoringCheck.DATA_DRIFT,
                            AlertSeverity.WARNING,
                            String.format("Data drift detected in feature '%s': drift score = %.4f", 
                                        feature, meanDiff),
                            meanDiff,
                            config.getDataDriftThreshold()
                        );
                        alert.getMetadata().put("feature", feature);
                        alert.getMetadata().put("current_mean", currentStat.getMean());
                        alert.getMetadata().put("baseline_mean", baselineStat.getMean());
                        return alert;
                    }
                }
            }
            
            return null;
        }
        
        private MonitoringAlert checkTrafficAnomaly() {
            double currentRPS = metrics.getRequestsPerSecond();
            
            // Simple anomaly detection: if requests per second is very low or very high
            // In production, use more sophisticated methods
            double expectedRPS = 10.0; // Expected baseline RPS
            double threshold = config.getTrafficAnomalyThreshold();
            
            if (currentRPS > expectedRPS * threshold || currentRPS < expectedRPS / threshold) {
                AlertSeverity severity = currentRPS < expectedRPS / threshold ? 
                    AlertSeverity.WARNING : AlertSeverity.CRITICAL;
                
                return new MonitoringAlert(
                    modelId,
                    MonitoringCheck.TRAFFIC_ANOMALY,
                    severity,
                    String.format("Traffic anomaly detected: %.2f RPS (expected: %.2f RPS)", 
                                currentRPS, expectedRPS),
                    currentRPS,
                    expectedRPS
                );
            }
            
            return null;
        }
        
        public String getModelId() { return modelId; }
        public MonitoringConfig getConfig() { return config; }
        public ModelMetrics getMetrics() { return metrics; }
    }
    
    /**
     * Alert handler interface
     */
    public interface AlertHandler {
        void handleAlert(MonitoringAlert alert);
    }
    
    /**
     * Console alert handler
     */
    public static class ConsoleAlertHandler implements AlertHandler {
        @Override
        public void handleAlert(MonitoringAlert alert) {
            String severityIcon = getSeverityIcon(alert.getSeverity());
            System.out.println(String.format("\n%s ALERT: %s", severityIcon, alert.getMessage()));
            System.out.println("  Model: " + alert.getModelId());
            System.out.println("  Check: " + alert.getCheckType());
            System.out.println("  Current: " + String.format("%.4f", alert.getCurrentValue()));
            System.out.println("  Threshold: " + String.format("%.4f", alert.getThresholdValue()));
            System.out.println("  Time: " + alert.getTimestamp().format(TIMESTAMP_FORMAT));
        }
        
        private String getSeverityIcon(AlertSeverity severity) {
            switch (severity) {
                case INFO: return "ℹ️";
                case WARNING: return "⚠️";
                case CRITICAL: return "🚨";
                default: return "📊";
            }
        }
    }
    
    /**
     * Initialize monitoring system
     */
    public ModelMonitoringSystem(String dbPath) {
        this.dbPath = dbPath;
        this.scheduler = Executors.newScheduledThreadPool(5);
        this.alertExecutor = Executors.newFixedThreadPool(3);
        
        // Initialize database
        initializeDatabase();
        
        // Add default console alert handler
        addAlertHandler(new ConsoleAlertHandler());
        
        logger.info("Model Monitoring System initialized with database: {}", dbPath);
    }
    
    /**
     * Initialize monitoring database
     */
    private void initializeDatabase() {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            // Create monitoring_alerts table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS monitoring_alerts (" +
                "alert_id TEXT PRIMARY KEY, " +
                "model_id TEXT NOT NULL, " +
                "check_type TEXT NOT NULL, " +
                "severity TEXT NOT NULL, " +
                "message TEXT NOT NULL, " +
                "current_value REAL NOT NULL, " +
                "threshold_value REAL NOT NULL, " +
                "timestamp TEXT NOT NULL, " +
                "metadata TEXT, " +
                "is_resolved INTEGER DEFAULT 0" +
                ")"
            );
            
            // Create model_metrics table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS model_metrics (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "model_id TEXT NOT NULL, " +
                "timestamp TEXT NOT NULL, " +
                "request_count INTEGER, " +
                "error_count INTEGER, " +
                "avg_latency REAL, " +
                "error_rate REAL, " +
                "requests_per_second REAL, " +
                "performance_metrics TEXT" +
                ")"
            );
            
            // Create indexes
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_alerts_model_time ON monitoring_alerts (model_id, timestamp)"
            );
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_metrics_model_time ON model_metrics (model_id, timestamp)"
            );
            
            logger.info("Monitoring database initialized successfully");
            
        } catch (SQLException e) {
            logger.error("Failed to initialize monitoring database", e);
            throw new RuntimeException("Database initialization failed", e);
        }
    }
    
    /**
     * Register model for monitoring
     */
    public void registerModel(String modelId, MonitoringConfig config) {
        ModelMonitor monitor = new ModelMonitor(modelId, config);
        modelMonitors.put(modelId, monitor);
        
        // Start monitoring task
        scheduler.scheduleAtFixedRate(
            () -> runHealthChecks(modelId),
            config.getMonitoringIntervalSeconds(),
            config.getMonitoringIntervalSeconds(),
            TimeUnit.SECONDS
        );
        
        logger.info("Registered model for monitoring: {} (interval: {}s)", 
                   modelId, config.getMonitoringIntervalSeconds());
    }
    
    /**
     * Record prediction for monitoring
     */
    public void recordPrediction(String modelId, double latencyMs, boolean isError, 
                                Map<String, Double> performance, Map<String, Double> features) {
        ModelMonitor monitor = modelMonitors.get(modelId);
        if (monitor != null) {
            monitor.recordPrediction(latencyMs, isError, performance, features);
        } else {
            logger.warn("Model monitor not found: {}", modelId);
        }
    }
    
    /**
     * Set baseline for a model
     */
    public void setModelBaseline(String modelId) {
        ModelMonitor monitor = modelMonitors.get(modelId);
        if (monitor != null) {
            monitor.setBaseline();
        } else {
            logger.warn("Model monitor not found: {}", modelId);
        }
    }
    
    /**
     * Add alert handler
     */
    public void addAlertHandler(AlertHandler handler) {
        alertHandlers.add(handler);
    }
    
    /**
     * Run health checks for a model
     */
    private void runHealthChecks(String modelId) {
        if (!isMonitoring) return;
        
        try {
            ModelMonitor monitor = modelMonitors.get(modelId);
            if (monitor == null) return;
            
            List<MonitoringAlert> alerts = monitor.checkHealth();
            
            for (MonitoringAlert alert : alerts) {
                // Store alert in database
                storeAlert(alert);
                
                // Trigger alert handlers
                for (AlertHandler handler : alertHandlers) {
                    CompletableFuture.runAsync(() -> {
                        try {
                            handler.handleAlert(alert);
                        } catch (Exception e) {
                            logger.error("Alert handler failed", e);
                        }
                    }, alertExecutor);
                }
            }
            
            // Store metrics snapshot
            storeMetricsSnapshot(monitor);
            
        } catch (Exception e) {
            logger.error("Health check failed for model: " + modelId, e);
        }
    }
    
    /**
     * Store alert in database
     */
    private void storeAlert(MonitoringAlert alert) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT INTO monitoring_alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            stmt.setString(1, alert.getAlertId());
            stmt.setString(2, alert.getModelId());
            stmt.setString(3, alert.getCheckType().name());
            stmt.setString(4, alert.getSeverity().name());
            stmt.setString(5, alert.getMessage());
            stmt.setDouble(6, alert.getCurrentValue());
            stmt.setDouble(7, alert.getThresholdValue());
            stmt.setString(8, alert.getTimestamp().format(TIMESTAMP_FORMAT));
            stmt.setString(9, objectMapper.writeValueAsString(alert.getMetadata()));
            stmt.setInt(10, alert.isResolved() ? 1 : 0);
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to store alert: " + alert.getAlertId(), e);
        }
    }
    
    /**
     * Store metrics snapshot
     */
    private void storeMetricsSnapshot(ModelMonitor monitor) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT INTO model_metrics VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            ModelMetrics metrics = monitor.getMetrics();
            
            stmt.setString(1, monitor.getModelId());
            stmt.setString(2, LocalDateTime.now().format(TIMESTAMP_FORMAT));
            stmt.setLong(3, metrics.getRequestCount());
            stmt.setLong(4, metrics.getErrorCount());
            stmt.setDouble(5, metrics.getAverageLatency());
            stmt.setDouble(6, metrics.getErrorRate());
            stmt.setDouble(7, metrics.getRequestsPerSecond());
            stmt.setString(8, objectMapper.writeValueAsString(metrics.getAveragePerformanceMetrics()));
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to store metrics snapshot for model: " + monitor.getModelId(), e);
        }
    }
    
    /**
     * Get model health summary
     */
    public Map<String, Object> getModelHealth(String modelId) {
        ModelMonitor monitor = modelMonitors.get(modelId);
        if (monitor == null) {
            return Collections.singletonMap("error", "Model not found");
        }
        
        ModelMetrics metrics = monitor.getMetrics();
        Map<String, Object> health = new HashMap<>();
        
        health.put("model_id", modelId);
        health.put("total_requests", metrics.getRequestCount());
        health.put("error_count", metrics.getErrorCount());
        health.put("error_rate", metrics.getErrorRate());
        health.put("avg_latency_ms", metrics.getAverageLatency());
        health.put("p95_latency_ms", metrics.getP95Latency());
        health.put("requests_per_second", metrics.getRequestsPerSecond());
        health.put("performance_metrics", metrics.getAveragePerformanceMetrics());
        
        // Get recent alerts
        List<MonitoringAlert> recentAlerts = getRecentAlerts(modelId, 24); // Last 24 hours
        health.put("recent_alerts", recentAlerts.size());
        health.put("critical_alerts", recentAlerts.stream()
            .mapToLong(alert -> alert.getSeverity() == AlertSeverity.CRITICAL ? 1 : 0)
            .sum());
        
        return health;
    }
    
    /**
     * Get recent alerts for a model
     */
    public List<MonitoringAlert> getRecentAlerts(String modelId, int hours) {
        List<MonitoringAlert> alerts = new ArrayList<>();
        
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "SELECT * FROM monitoring_alerts WHERE model_id = ? AND " +
                        "datetime(timestamp) > datetime('now', '-" + hours + " hours') " +
                        "ORDER BY timestamp DESC";
            
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, modelId);
            
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                MonitoringAlert alert = new MonitoringAlert();
                alert.setAlertId(rs.getString("alert_id"));
                alert.setModelId(rs.getString("model_id"));
                alert.setCheckType(MonitoringCheck.valueOf(rs.getString("check_type")));
                alert.setSeverity(AlertSeverity.valueOf(rs.getString("severity")));
                alert.setMessage(rs.getString("message"));
                alert.setCurrentValue(rs.getDouble("current_value"));
                alert.setThresholdValue(rs.getDouble("threshold_value"));
                alert.setTimestamp(LocalDateTime.parse(rs.getString("timestamp"), TIMESTAMP_FORMAT));
                alert.setResolved(rs.getInt("is_resolved") == 1);
                
                alerts.add(alert);
            }
            
        } catch (SQLException e) {
            logger.error("Failed to get recent alerts for model: " + modelId, e);
        }
        
        return alerts;
    }
    
    /**
     * Get monitoring dashboard data
     */
    public Map<String, Object> getDashboardData() {
        Map<String, Object> dashboard = new HashMap<>();
        
        // Overall statistics
        int totalModels = modelMonitors.size();
        long totalRequests = modelMonitors.values().stream()
            .mapToLong(monitor -> monitor.getMetrics().getRequestCount())
            .sum();
        
        dashboard.put("total_models", totalModels);
        dashboard.put("total_requests", totalRequests);
        dashboard.put("monitoring_status", isMonitoring ? "active" : "paused");
        
        // Model health summary
        Map<String, Object> modelHealths = new HashMap<>();
        for (String modelId : modelMonitors.keySet()) {
            modelHealths.put(modelId, getModelHealth(modelId));
        }
        dashboard.put("model_healths", modelHealths);
        
        // Recent alerts summary
        Map<String, Long> alertCounts = new HashMap<>();
        for (AlertSeverity severity : AlertSeverity.values()) {
            alertCounts.put(severity.name().toLowerCase(), 0L);
        }
        
        for (String modelId : modelMonitors.keySet()) {
            List<MonitoringAlert> recentAlerts = getRecentAlerts(modelId, 24);
            for (MonitoringAlert alert : recentAlerts) {
                String severity = alert.getSeverity().name().toLowerCase();
                alertCounts.put(severity, alertCounts.get(severity) + 1);
            }
        }
        dashboard.put("alert_counts_24h", alertCounts);
        
        return dashboard;
    }
    
    /**
     * Stop monitoring
     */
    public void stopMonitoring() {
        isMonitoring = false;
        logger.info("Model monitoring stopped");
    }
    
    /**
     * Start monitoring
     */
    public void startMonitoring() {
        isMonitoring = true;
        logger.info("Model monitoring started");
    }
    
    /**
     * Shutdown monitoring system
     */
    public void shutdown() {
        logger.info("Shutting down Model Monitoring System...");
        
        isMonitoring = false;
        
        scheduler.shutdown();
        alertExecutor.shutdown();
        
        try {
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!alertExecutor.awaitTermination(10, TimeUnit.SECONDS)) {
                alertExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("Model Monitoring System shutdown complete");
    }
    
    /**
     * Demo main method
     */
    public static void main(String[] args) throws Exception {
        System.out.println("📊 Starting Model Monitoring System Demo");
        System.out.println("=" + "=".repeat(50));
        
        // Initialize monitoring system
        ModelMonitoringSystem monitoring = new ModelMonitoringSystem("monitoring.db");
        
        // Register models for monitoring
        System.out.println("\n📡 Registering models for monitoring...");
        
        // Fraud detection model
        MonitoringConfig fraudConfig = new MonitoringConfig("paytm_fraud_detector");
        fraudConfig.setMonitoringIntervalSeconds(5); // 5 seconds for demo
        fraudConfig.setLatencyThresholdMs(500.0);
        fraudConfig.setErrorRateThreshold(0.02); // 2%
        fraudConfig.getPerformanceThresholds().put("accuracy", 0.90);
        fraudConfig.getPerformanceThresholds().put("precision", 0.85);
        
        monitoring.registerModel("paytm_fraud_detector", fraudConfig);
        
        // Recommendation model
        MonitoringConfig recConfig = new MonitoringConfig("flipkart_recommendation");
        recConfig.setMonitoringIntervalSeconds(10); // 10 seconds for demo
        recConfig.setLatencyThresholdMs(200.0);
        recConfig.setErrorRateThreshold(0.01); // 1%
        recConfig.getPerformanceThresholds().put("precision_at_k", 0.75);
        
        monitoring.registerModel("flipkart_recommendation", recConfig);
        
        // Wait for initial setup
        Thread.sleep(2000);
        
        // Set baselines
        monitoring.setModelBaseline("paytm_fraud_detector");
        monitoring.setModelBaseline("flipkart_recommendation");
        
        // Simulate normal traffic
        System.out.println("\n🚗 Simulating normal traffic...");
        
        Random random = new Random();
        
        // Simulate 30 seconds of normal traffic
        for (int i = 0; i < 30; i++) {
            // Fraud detection predictions
            for (int j = 0; j < 5; j++) {
                Map<String, Double> performance = Map.of(
                    "accuracy", 0.92 + random.nextGaussian() * 0.01,
                    "precision", 0.88 + random.nextGaussian() * 0.01
                );
                
                Map<String, Double> features = Map.of(
                    "transaction_amount", 1000 + random.nextGaussian() * 500,
                    "user_age_days", 365 + random.nextGaussian() * 200
                );
                
                monitoring.recordPrediction(
                    "paytm_fraud_detector",
                    200 + random.nextGaussian() * 50, // Normal latency
                    random.nextDouble() < 0.01, // 1% error rate
                    performance,
                    features
                );
            }
            
            // Recommendation predictions
            for (int j = 0; j < 3; j++) {
                Map<String, Double> performance = Map.of(
                    "precision_at_k", 0.78 + random.nextGaussian() * 0.02
                );
                
                Map<String, Double> features = Map.of(
                    "user_session_length", 300 + random.nextGaussian() * 100,
                    "num_items_viewed", 5 + random.nextGaussian() * 2
                );
                
                monitoring.recordPrediction(
                    "flipkart_recommendation",
                    80 + random.nextGaussian() * 20, // Normal latency
                    random.nextDouble() < 0.005, // 0.5% error rate
                    performance,
                    features
                );
            }
            
            Thread.sleep(1000); // 1 second intervals
        }
        
        // Simulate problems
        System.out.println("\n⚠️  Simulating model problems...");
        
        // Simulate latency spike
        for (int i = 0; i < 10; i++) {
            Map<String, Double> performance = Map.of(
                "accuracy", 0.91 + random.nextGaussian() * 0.01,
                "precision", 0.87 + random.nextGaussian() * 0.01
            );
            
            monitoring.recordPrediction(
                "paytm_fraud_detector",
                800 + random.nextGaussian() * 200, // High latency
                random.nextDouble() < 0.01,
                performance,
                Map.of("transaction_amount", 1000.0)
            );
            
            Thread.sleep(500);
        }
        
        // Simulate performance degradation
        for (int i = 0; i < 15; i++) {
            Map<String, Double> performance = Map.of(
                "accuracy", 0.80 + random.nextGaussian() * 0.02, // Low accuracy
                "precision", 0.75 + random.nextGaussian() * 0.02 // Low precision
            );
            
            monitoring.recordPrediction(
                "paytm_fraud_detector",
                250 + random.nextGaussian() * 50,
                random.nextDouble() < 0.01,
                performance,
                Map.of("transaction_amount", 1000.0)
            );
            
            Thread.sleep(500);
        }
        
        // Simulate error rate spike
        for (int i = 0; i < 10; i++) {
            Map<String, Double> performance = Map.of(
                "precision_at_k", 0.76 + random.nextGaussian() * 0.02
            );
            
            monitoring.recordPrediction(
                "flipkart_recommendation",
                100 + random.nextGaussian() * 30,
                random.nextDouble() < 0.05, // High error rate
                performance,
                Map.of("user_session_length", 300.0)
            );
            
            Thread.sleep(500);
        }
        
        // Wait for alerts to be processed
        Thread.sleep(15000);
        
        // Display monitoring dashboard
        System.out.println("\n📊 Monitoring Dashboard:");
        Map<String, Object> dashboard = monitoring.getDashboardData();
        
        System.out.println("  Total Models: " + dashboard.get("total_models"));
        System.out.println("  Total Requests: " + dashboard.get("total_requests"));
        System.out.println("  Monitoring Status: " + dashboard.get("monitoring_status"));
        
        @SuppressWarnings("unchecked")
        Map<String, Long> alertCounts = (Map<String, Long>) dashboard.get("alert_counts_24h");
        System.out.println("  Alert Counts (24h):");
        alertCounts.forEach((severity, count) -> 
            System.out.println("    " + severity.toUpperCase() + ": " + count)
        );
        
        // Display model health
        System.out.println("\n🏥 Model Health Summary:");
        @SuppressWarnings("unchecked")
        Map<String, Object> modelHealths = (Map<String, Object>) dashboard.get("model_healths");
        
        for (Map.Entry<String, Object> entry : modelHealths.entrySet()) {
            String modelId = entry.getKey();
            @SuppressWarnings("unchecked")
            Map<String, Object> health = (Map<String, Object>) entry.getValue();
            
            System.out.println("\n  " + modelId + ":");
            System.out.println("    Total Requests: " + health.get("total_requests"));
            System.out.println("    Error Rate: " + String.format("%.2f%%", 
                              ((Number) health.get("error_rate")).doubleValue() * 100));
            System.out.println("    Avg Latency: " + String.format("%.2f ms", 
                              ((Number) health.get("avg_latency_ms")).doubleValue()));
            System.out.println("    P95 Latency: " + String.format("%.2f ms", 
                              ((Number) health.get("p95_latency_ms")).doubleValue()));
            System.out.println("    Recent Alerts: " + health.get("recent_alerts"));
            System.out.println("    Critical Alerts: " + health.get("critical_alerts"));
        }
        
        // Show recent alerts
        System.out.println("\n🚨 Recent Alerts Summary:");
        for (String modelId : Arrays.asList("paytm_fraud_detector", "flipkart_recommendation")) {
            List<MonitoringAlert> alerts = monitoring.getRecentAlerts(modelId, 1);
            System.out.println("\n  " + modelId + " (" + alerts.size() + " alerts):");
            
            for (MonitoringAlert alert : alerts.stream().limit(3).toArray(MonitoringAlert[]::new)) {
                System.out.println("    " + alert.getSeverity() + ": " + alert.getCheckType() + 
                                 " - " + alert.getMessage().substring(0, Math.min(60, alert.getMessage().length())));
            }
        }
        
        System.out.println("\n✅ Model monitoring demo completed!");
        System.out.println("Mumbai me model monitoring bhi traffic police ki tarah vigilant!");
        
        // Shutdown
        monitoring.shutdown();
    }
}