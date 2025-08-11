/*
 * Model Monitor for Production Drift Detection
 * Episode 5: Code Example 13
 *
 * Production-ready model monitoring system in Java
 * Supporting drift detection, performance monitoring, and alerting
 *
 * Author: Code Developer Agent
 * Context: Enterprise model monitoring for Indian applications
 */

package com.ai.monitoring;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.stereotype.Component;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;
import java.sql.*;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Main Spring Boot application for AI Model Monitoring System
 */
@SpringBootApplication
@EnableScheduling
public class ModelMonitorApplication {
    
    public static void main(String[] args) {
        System.out.println("🔍 AI Model Monitor - Production Drift Detection");
        System.out.println("================================================");
        SpringApplication.run(ModelMonitorApplication.class, args);
    }
}

/**
 * Data classes for monitoring metrics and events
 */
class PredictionEvent {
    private String modelId;
    private String version;
    private Map<String, Object> inputFeatures;
    private Object prediction;
    private double confidence;
    private long timestamp;
    private String userId;
    private String region;
    private double responseTimeMs;
    
    // Constructors, getters, setters
    public PredictionEvent() {}
    
    public PredictionEvent(String modelId, String version, Map<String, Object> inputFeatures, 
                          Object prediction, double confidence, String userId, String region) {
        this.modelId = modelId;
        this.version = version;
        this.inputFeatures = inputFeatures;
        this.prediction = prediction;
        this.confidence = confidence;
        this.userId = userId;
        this.region = region;
        this.timestamp = System.currentTimeMillis();
    }
    
    // Getters and setters
    public String getModelId() { return modelId; }
    public void setModelId(String modelId) { this.modelId = modelId; }
    
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    
    public Map<String, Object> getInputFeatures() { return inputFeatures; }
    public void setInputFeatures(Map<String, Object> inputFeatures) { this.inputFeatures = inputFeatures; }
    
    public Object getPrediction() { return prediction; }
    public void setPrediction(Object prediction) { this.prediction = prediction; }
    
    public double getConfidence() { return confidence; }
    public void setConfidence(double confidence) { this.confidence = confidence; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
    
    public String getUserId() { return userId; }
    public void setUserId(String userId) { this.userId = userId; }
    
    public String getRegion() { return region; }
    public void setRegion(String region) { this.region = region; }
    
    public double getResponseTimeMs() { return responseTimeMs; }
    public void setResponseTimeMs(double responseTimeMs) { this.responseTimeMs = responseTimeMs; }
}

class ModelMetrics {
    private String modelId;
    private String version;
    private long totalPredictions;
    private double avgConfidence;
    private double avgResponseTime;
    private double accuracyScore;
    private Map<String, Integer> predictionDistribution;
    private Map<String, Double> featureStatistics;
    private LocalDateTime lastUpdated;
    private double costPerPredictionINR;
    
    // Constructors
    public ModelMetrics() {
        this.predictionDistribution = new HashMap<>();
        this.featureStatistics = new HashMap<>();
        this.lastUpdated = LocalDateTime.now();
        this.costPerPredictionINR = 0.05; // ₹0.05 per prediction
    }
    
    public ModelMetrics(String modelId, String version) {
        this();
        this.modelId = modelId;
        this.version = version;
    }
    
    // Getters and setters
    public String getModelId() { return modelId; }
    public void setModelId(String modelId) { this.modelId = modelId; }
    
    public String getVersion() { return version; }
    public void setVersion(String version) { this.version = version; }
    
    public long getTotalPredictions() { return totalPredictions; }
    public void setTotalPredictions(long totalPredictions) { this.totalPredictions = totalPredictions; }
    
    public double getAvgConfidence() { return avgConfidence; }
    public void setAvgConfidence(double avgConfidence) { this.avgConfidence = avgConfidence; }
    
    public double getAvgResponseTime() { return avgResponseTime; }
    public void setAvgResponseTime(double avgResponseTime) { this.avgResponseTime = avgResponseTime; }
    
    public double getAccuracyScore() { return accuracyScore; }
    public void setAccuracyScore(double accuracyScore) { this.accuracyScore = accuracyScore; }
    
    public Map<String, Integer> getPredictionDistribution() { return predictionDistribution; }
    public void setPredictionDistribution(Map<String, Integer> predictionDistribution) { 
        this.predictionDistribution = predictionDistribution; 
    }
    
    public Map<String, Double> getFeatureStatistics() { return featureStatistics; }
    public void setFeatureStatistics(Map<String, Double> featureStatistics) { 
        this.featureStatistics = featureStatistics; 
    }
    
    public LocalDateTime getLastUpdated() { return lastUpdated; }
    public void setLastUpdated(LocalDateTime lastUpdated) { this.lastUpdated = lastUpdated; }
    
    public double getCostPerPredictionINR() { return costPerPredictionINR; }
    public void setCostPerPredictionINR(double costPerPredictionINR) { 
        this.costPerPredictionINR = costPerPredictionINR; 
    }
}

class DriftAlert {
    private String alertId;
    private String modelId;
    private String alertType;
    private String severity;
    private String message;
    private LocalDateTime timestamp;
    private Map<String, Object> metadata;
    private boolean resolved;
    
    public DriftAlert(String modelId, String alertType, String severity, String message) {
        this.alertId = UUID.randomUUID().toString();
        this.modelId = modelId;
        this.alertType = alertType;
        this.severity = severity;
        this.message = message;
        this.timestamp = LocalDateTime.now();
        this.metadata = new HashMap<>();
        this.resolved = false;
    }
    
    // Getters and setters
    public String getAlertId() { return alertId; }
    public void setAlertId(String alertId) { this.alertId = alertId; }
    
    public String getModelId() { return modelId; }
    public void setModelId(String modelId) { this.modelId = modelId; }
    
    public String getAlertType() { return alertType; }
    public void setAlertType(String alertType) { this.alertType = alertType; }
    
    public String getSeverity() { return severity; }
    public void setSeverity(String severity) { this.severity = severity; }
    
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
    
    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
    
    public Map<String, Object> getMetadata() { return metadata; }
    public void setMetadata(Map<String, Object> metadata) { this.metadata = metadata; }
    
    public boolean isResolved() { return resolved; }
    public void setResolved(boolean resolved) { this.resolved = resolved; }
}

/**
 * Core service for monitoring model performance and detecting drift
 */
@Service
class ModelMonitoringService {
    
    private static final Logger logger = LoggerFactory.getLogger(ModelMonitoringService.class);
    
    // In-memory storage for demo (use database in production)
    private final Map<String, List<PredictionEvent>> predictionHistory = new ConcurrentHashMap<>();
    private final Map<String, ModelMetrics> modelMetrics = new ConcurrentHashMap<>();
    private final List<DriftAlert> alerts = new ArrayList<>();
    
    // Drift detection thresholds
    private static final double CONFIDENCE_DRIFT_THRESHOLD = 0.1;
    private static final double ACCURACY_DRIFT_THRESHOLD = 0.05;
    private static final double RESPONSE_TIME_THRESHOLD_MS = 1000.0;
    private static final int BATCH_SIZE_FOR_ANALYSIS = 1000;
    
    /**
     * Record a new prediction event for monitoring
     */
    public void recordPrediction(PredictionEvent event) {
        String modelKey = event.getModelId() + ":" + event.getVersion();
        
        // Store prediction history
        predictionHistory.computeIfAbsent(modelKey, k -> new ArrayList<>()).add(event);
        
        // Update model metrics
        updateModelMetrics(modelKey, event);
        
        // Check for immediate anomalies
        checkRealTimeAnomalies(event);
        
        logger.info("Recorded prediction for model: {}, confidence: {}, response_time: {}ms", 
                   event.getModelId(), event.getConfidence(), event.getResponseTimeMs());
    }
    
    /**
     * Update running metrics for a model
     */
    private void updateModelMetrics(String modelKey, PredictionEvent event) {
        ModelMetrics metrics = modelMetrics.computeIfAbsent(modelKey, 
            k -> new ModelMetrics(event.getModelId(), event.getVersion()));
        
        // Update counters
        long totalPreds = metrics.getTotalPredictions() + 1;
        metrics.setTotalPredictions(totalPreds);
        
        // Update average confidence (running average)
        double newAvgConfidence = ((metrics.getAvgConfidence() * (totalPreds - 1)) + event.getConfidence()) / totalPreds;
        metrics.setAvgConfidence(newAvgConfidence);
        
        // Update average response time
        double newAvgResponseTime = ((metrics.getAvgResponseTime() * (totalPreds - 1)) + event.getResponseTimeMs()) / totalPreds;
        metrics.setAvgResponseTime(newAvgResponseTime);
        
        // Update prediction distribution
        String predictionStr = event.getPrediction().toString();
        metrics.getPredictionDistribution().merge(predictionStr, 1, Integer::sum);
        
        // Update feature statistics (simplified for demo)
        if (event.getInputFeatures() != null) {
            for (Map.Entry<String, Object> feature : event.getInputFeatures().entrySet()) {
                if (feature.getValue() instanceof Number) {
                    double value = ((Number) feature.getValue()).doubleValue();
                    String featureKey = feature.getKey() + "_avg";
                    double currentAvg = metrics.getFeatureStatistics().getOrDefault(featureKey, 0.0);
                    double newAvg = ((currentAvg * (totalPreds - 1)) + value) / totalPreds;
                    metrics.getFeatureStatistics().put(featureKey, newAvg);
                }
            }
        }
        
        metrics.setLastUpdated(LocalDateTime.now());
    }
    
    /**
     * Check for real-time anomalies in predictions
     */
    private void checkRealTimeAnomalies(PredictionEvent event) {
        // Check for low confidence predictions
        if (event.getConfidence() < 0.5) {
            createAlert(event.getModelId(), "LOW_CONFIDENCE", "WARNING", 
                       String.format("Low confidence prediction: %.3f for model %s", 
                                   event.getConfidence(), event.getModelId()));
        }
        
        // Check for high response time
        if (event.getResponseTimeMs() > RESPONSE_TIME_THRESHOLD_MS) {
            createAlert(event.getModelId(), "HIGH_LATENCY", "WARNING",
                       String.format("High response time: %.1fms for model %s",
                                   event.getResponseTimeMs(), event.getModelId()));
        }
        
        // Check for feature anomalies (simplified)
        if (event.getInputFeatures() != null) {
            for (Map.Entry<String, Object> feature : event.getInputFeatures().entrySet()) {
                if (feature.getValue() instanceof Number) {
                    double value = ((Number) feature.getValue()).doubleValue();
                    
                    // Simple outlier detection (values beyond 3 standard deviations)
                    if (Math.abs(value) > 1000) {  // Simplified threshold
                        createAlert(event.getModelId(), "FEATURE_ANOMALY", "INFO",
                                   String.format("Unusual feature value: %s = %.2f", 
                                               feature.getKey(), value));
                    }
                }
            }
        }
    }
    
    /**
     * Detect data drift by comparing recent predictions with historical baseline
     */
    public Map<String, Object> detectDataDrift(String modelId, String version) {
        String modelKey = modelId + ":" + version;
        List<PredictionEvent> history = predictionHistory.get(modelKey);
        
        if (history == null || history.size() < BATCH_SIZE_FOR_ANALYSIS) {
            return Map.of("drift_detected", false, "reason", "Insufficient data for analysis");
        }
        
        // Get recent and baseline data
        int historySize = history.size();
        List<PredictionEvent> recentData = history.subList(
            Math.max(0, historySize - BATCH_SIZE_FOR_ANALYSIS/2), historySize);
        List<PredictionEvent> baselineData = history.subList(0, 
            Math.min(BATCH_SIZE_FOR_ANALYSIS/2, historySize/2));
        
        Map<String, Object> driftAnalysis = new HashMap<>();
        driftAnalysis.put("model_id", modelId);
        driftAnalysis.put("version", version);
        driftAnalysis.put("analysis_timestamp", LocalDateTime.now());
        
        // Confidence drift detection
        double recentAvgConfidence = recentData.stream()
            .mapToDouble(PredictionEvent::getConfidence)
            .average().orElse(0.0);
        
        double baselineAvgConfidence = baselineData.stream()
            .mapToDouble(PredictionEvent::getConfidence)
            .average().orElse(0.0);
        
        double confidenceDrift = Math.abs(recentAvgConfidence - baselineAvgConfidence);
        boolean confidenceDriftDetected = confidenceDrift > CONFIDENCE_DRIFT_THRESHOLD;
        
        // Response time drift detection
        double recentAvgResponseTime = recentData.stream()
            .mapToDouble(PredictionEvent::getResponseTimeMs)
            .average().orElse(0.0);
        
        double baselineAvgResponseTime = baselineData.stream()
            .mapToDouble(PredictionEvent::getResponseTimeMs)
            .average().orElse(0.0);
        
        double responseDrift = Math.abs(recentAvgResponseTime - baselineAvgResponseTime);
        boolean responseDriftDetected = responseDrift > 100.0; // 100ms threshold
        
        // Prediction distribution drift (simplified)
        Map<String, Integer> recentDistribution = recentData.stream()
            .collect(Collectors.groupingBy(
                e -> e.getPrediction().toString(),
                Collectors.summingInt(e -> 1)
            ));
        
        Map<String, Integer> baselineDistribution = baselineData.stream()
            .collect(Collectors.groupingBy(
                e -> e.getPrediction().toString(),
                Collectors.summingInt(e -> 1)
            ));
        
        double distributionDrift = calculateDistributionDrift(recentDistribution, baselineDistribution);
        boolean distributionDriftDetected = distributionDrift > 0.15; // 15% threshold
        
        // Overall drift assessment
        boolean overallDriftDetected = confidenceDriftDetected || responseDriftDetected || distributionDriftDetected;
        
        driftAnalysis.put("drift_detected", overallDriftDetected);
        driftAnalysis.put("confidence_drift", Map.of(
            "detected", confidenceDriftDetected,
            "recent_avg", recentAvgConfidence,
            "baseline_avg", baselineAvgConfidence,
            "drift_magnitude", confidenceDrift
        ));
        driftAnalysis.put("response_time_drift", Map.of(
            "detected", responseDriftDetected,
            "recent_avg_ms", recentAvgResponseTime,
            "baseline_avg_ms", baselineAvgResponseTime,
            "drift_magnitude_ms", responseDrift
        ));
        driftAnalysis.put("distribution_drift", Map.of(
            "detected", distributionDriftDetected,
            "recent_distribution", recentDistribution,
            "baseline_distribution", baselineDistribution,
            "drift_score", distributionDrift
        ));
        
        // Create alert if drift detected
        if (overallDriftDetected) {
            String alertMessage = String.format(
                "Data drift detected for model %s: confidence_drift=%s, response_drift=%s, distribution_drift=%s",
                modelId, confidenceDriftDetected, responseDriftDetected, distributionDriftDetected
            );
            createAlert(modelId, "DATA_DRIFT", "HIGH", alertMessage);
        }
        
        logger.info("Drift analysis completed for model {}: drift_detected={}", 
                   modelId, overallDriftDetected);
        
        return driftAnalysis;
    }
    
    /**
     * Calculate distribution drift between two prediction distributions
     */
    private double calculateDistributionDrift(Map<String, Integer> recent, Map<String, Integer> baseline) {
        Set<String> allKeys = new HashSet<>(recent.keySet());
        allKeys.addAll(baseline.keySet());
        
        int recentTotal = recent.values().stream().mapToInt(Integer::intValue).sum();
        int baselineTotal = baseline.values().stream().mapToInt(Integer::intValue).sum();
        
        double totalDrift = 0.0;
        
        for (String key : allKeys) {
            double recentProp = recent.getOrDefault(key, 0) / (double) recentTotal;
            double baselineProp = baseline.getOrDefault(key, 0) / (double) baselineTotal;
            totalDrift += Math.abs(recentProp - baselineProp);
        }
        
        return totalDrift / 2.0; // Normalize (total variation distance)
    }
    
    /**
     * Create and store alert
     */
    private void createAlert(String modelId, String alertType, String severity, String message) {
        DriftAlert alert = new DriftAlert(modelId, alertType, severity, message);
        alerts.add(alert);
        
        // Log alert
        logger.warn("Alert created - Model: {}, Type: {}, Severity: {}, Message: {}", 
                   modelId, alertType, severity, message);
        
        // In production, send to notification system (Slack, email, etc.)
        sendAlertNotification(alert);
    }
    
    /**
     * Send alert notifications (mock implementation)
     */
    private void sendAlertNotification(DriftAlert alert) {
        // Mock notification - in production, integrate with Slack, email, SMS
        logger.info("📱 Notification sent for alert: {} - {} - {}", 
                   alert.getSeverity(), alert.getAlertType(), alert.getMessage());
        
        // For Indian context - send alerts in local timezone
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
        String formattedTime = alert.getTimestamp().format(formatter);
        
        System.out.println(String.format(
            "🚨 Alert: [%s] %s at %s IST\n" +
            "   Model: %s\n" +
            "   Type: %s\n" +
            "   Message: %s\n",
            alert.getSeverity(), alert.getAlertType(), formattedTime,
            alert.getModelId(), alert.getAlertType(), alert.getMessage()
        ));
    }
    
    /**
     * Get model performance summary
     */
    public ModelMetrics getModelMetrics(String modelId, String version) {
        String modelKey = modelId + ":" + version;
        return modelMetrics.get(modelKey);
    }
    
    /**
     * Get all active alerts
     */
    public List<DriftAlert> getActiveAlerts(String modelId) {
        return alerts.stream()
            .filter(alert -> !alert.isResolved())
            .filter(alert -> modelId == null || alert.getModelId().equals(modelId))
            .collect(Collectors.toList());
    }
    
    /**
     * Get cost analysis for a model
     */
    public Map<String, Object> getCostAnalysis(String modelId, String version) {
        ModelMetrics metrics = getModelMetrics(modelId, version);
        if (metrics == null) {
            return Map.of("error", "Model metrics not found");
        }
        
        long totalPredictions = metrics.getTotalPredictions();
        double costPerPrediction = metrics.getCostPerPredictionINR();
        double totalCost = totalPredictions * costPerPrediction;
        
        // Calculate daily/monthly projections
        double dailyPredictions = totalPredictions / 30.0; // Assuming 30-day window
        double dailyCost = dailyPredictions * costPerPrediction;
        double monthlyCost = dailyCost * 30;
        
        return Map.of(
            "model_id", modelId,
            "version", version,
            "total_predictions", totalPredictions,
            "cost_per_prediction_inr", costPerPrediction,
            "total_cost_inr", String.format("₹%.2f", totalCost),
            "daily_cost_inr", String.format("₹%.2f", dailyCost),
            "monthly_projected_cost_inr", String.format("₹%.2f", monthlyCost),
            "avg_response_time_ms", metrics.getAvgResponseTime(),
            "cost_per_second_inr", String.format("₹%.6f", costPerPrediction / (metrics.getAvgResponseTime() / 1000))
        );
    }
}

/**
 * REST API endpoints for model monitoring
 */
@RestController
@RequestMapping("/api/v1/monitor")
class ModelMonitorController {
    
    private static final Logger logger = LoggerFactory.getLogger(ModelMonitorController.class);
    private final ModelMonitoringService monitoringService;
    
    public ModelMonitorController(ModelMonitoringService monitoringService) {
        this.monitoringService = monitoringService;
    }
    
    /**
     * Record a new prediction event
     */
    @PostMapping("/predictions")
    public Map<String, Object> recordPrediction(@RequestBody PredictionEvent event) {
        try {
            event.setTimestamp(System.currentTimeMillis());
            monitoringService.recordPrediction(event);
            
            return Map.of(
                "status", "success",
                "message", "Prediction recorded successfully",
                "model_id", event.getModelId(),
                "timestamp", event.getTimestamp()
            );
        } catch (Exception e) {
            logger.error("Failed to record prediction", e);
            return Map.of(
                "status", "error",
                "message", "Failed to record prediction: " + e.getMessage()
            );
        }
    }
    
    /**
     * Get model metrics
     */
    @GetMapping("/models/{modelId}/versions/{version}/metrics")
    public Map<String, Object> getModelMetrics(@PathVariable String modelId, @PathVariable String version) {
        try {
            ModelMetrics metrics = monitoringService.getModelMetrics(modelId, version);
            
            if (metrics == null) {
                return Map.of(
                    "status", "error",
                    "message", "Model metrics not found"
                );
            }
            
            return Map.of(
                "status", "success",
                "data", metrics
            );
        } catch (Exception e) {
            logger.error("Failed to get model metrics", e);
            return Map.of(
                "status", "error",
                "message", "Failed to get model metrics: " + e.getMessage()
            );
        }
    }
    
    /**
     * Trigger drift analysis
     */
    @PostMapping("/models/{modelId}/versions/{version}/drift-analysis")
    public Map<String, Object> analyzeDrift(@PathVariable String modelId, @PathVariable String version) {
        try {
            Map<String, Object> driftAnalysis = monitoringService.detectDataDrift(modelId, version);
            
            return Map.of(
                "status", "success",
                "data", driftAnalysis
            );
        } catch (Exception e) {
            logger.error("Failed to analyze drift", e);
            return Map.of(
                "status", "error",
                "message", "Failed to analyze drift: " + e.getMessage()
            );
        }
    }
    
    /**
     * Get active alerts
     */
    @GetMapping("/alerts")
    public Map<String, Object> getAlerts(@RequestParam(required = false) String modelId) {
        try {
            List<DriftAlert> alerts = monitoringService.getActiveAlerts(modelId);
            
            return Map.of(
                "status", "success",
                "data", alerts,
                "count", alerts.size()
            );
        } catch (Exception e) {
            logger.error("Failed to get alerts", e);
            return Map.of(
                "status", "error",
                "message", "Failed to get alerts: " + e.getMessage()
            );
        }
    }
    
    /**
     * Get cost analysis
     */
    @GetMapping("/models/{modelId}/versions/{version}/cost-analysis")
    public Map<String, Object> getCostAnalysis(@PathVariable String modelId, @PathVariable String version) {
        try {
            Map<String, Object> costAnalysis = monitoringService.getCostAnalysis(modelId, version);
            
            return Map.of(
                "status", "success",
                "data", costAnalysis
            );
        } catch (Exception e) {
            logger.error("Failed to get cost analysis", e);
            return Map.of(
                "status", "error",
                "message", "Failed to get cost analysis: " + e.getMessage()
            );
        }
    }
    
    /**
     * Health check endpoint
     */
    @GetMapping("/health")
    public Map<String, Object> healthCheck() {
        return Map.of(
            "status", "healthy",
            "timestamp", System.currentTimeMillis(),
            "service", "Model Monitor",
            "version", "1.0.0"
        );
    }
}

/**
 * Scheduled tasks for periodic monitoring
 */
@Component
class ScheduledMonitoringTasks {
    
    private static final Logger logger = LoggerFactory.getLogger(ScheduledMonitoringTasks.class);
    private final ModelMonitoringService monitoringService;
    
    public ScheduledMonitoringTasks(ModelMonitoringService monitoringService) {
        this.monitoringService = monitoringService;
    }
    
    /**
     * Run drift analysis every 30 minutes
     */
    @Scheduled(fixedRate = 1800000) // 30 minutes
    public void scheduledDriftAnalysis() {
        logger.info("Starting scheduled drift analysis...");
        
        // In production, get list of active models from database
        List<String> activeModels = Arrays.asList(
            "sentiment_analyzer:v1.0",
            "recommendation_engine:v2.1",
            "fraud_detector:v1.5"
        );
        
        for (String modelKey : activeModels) {
            try {
                String[] parts = modelKey.split(":");
                if (parts.length == 2) {
                    monitoringService.detectDataDrift(parts[0], parts[1]);
                }
            } catch (Exception e) {
                logger.error("Failed drift analysis for model: " + modelKey, e);
            }
        }
        
        logger.info("Scheduled drift analysis completed");
    }
    
    /**
     * Generate daily monitoring report
     */
    @Scheduled(cron = "0 0 9 * * *") // 9 AM IST daily
    public void generateDailyReport() {
        logger.info("Generating daily monitoring report...");
        
        try {
            // Generate summary report (mock implementation)
            LocalDateTime now = LocalDateTime.now();
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd-MM-yyyy");
            String dateStr = now.format(formatter);
            
            System.out.println("\n📊 Daily Model Monitoring Report - " + dateStr);
            System.out.println("=" + "=".repeat(50));
            System.out.println("Generated at: " + now.format(DateTimeFormatter.ofPattern("HH:mm:ss IST")));
            System.out.println("Total active alerts: " + monitoringService.getActiveAlerts(null).size());
            System.out.println("Report details would include:");
            System.out.println("  • Model performance summaries");
            System.out.println("  • Cost analysis in INR");
            System.out.println("  • Drift detection results");
            System.out.println("  • System health metrics");
            System.out.println("  • Recommendations for optimization");
            
        } catch (Exception e) {
            logger.error("Failed to generate daily report", e);
        }
    }
}