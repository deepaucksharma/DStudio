package com.paytm.cloudnative.autoscaling;

/**
 * Auto-Scaling System for Paytm Payment Services
 * Cloud Native Auto-scaling Patterns Implementation
 * 
 * Paytm के payment processing के लिए intelligent auto-scaling
 * CPU, Memory, Request Rate, और Custom Metrics के basis पर scaling
 */

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.logging.Logger;
import java.lang.Math;

// Auto-scaling Core Classes
public class AutoScalingSystem {
    private static final Logger logger = Logger.getLogger(AutoScalingSystem.class.getName());
    
    // Metrics Collection
    public static class MetricsCollector {
        private final Map<String, List<Double>> metrics = new ConcurrentHashMap<>();
        private final int maxHistorySize = 100;
        
        public void recordMetric(String metricName, double value) {
            metrics.computeIfAbsent(metricName, k -> new ArrayList<>()).add(value);
            
            // Keep only recent metrics
            List<Double> history = metrics.get(metricName);
            if (history.size() > maxHistorySize) {
                history.remove(0);
            }
        }
        
        public double getAverageMetric(String metricName, int windowSize) {
            List<Double> history = metrics.getOrDefault(metricName, new ArrayList<>());
            if (history.isEmpty()) return 0.0;
            
            int startIndex = Math.max(0, history.size() - windowSize);
            return history.subList(startIndex, history.size())
                         .stream()
                         .mapToDouble(Double::doubleValue)
                         .average()
                         .orElse(0.0);
        }
        
        public double getCurrentMetric(String metricName) {
            List<Double> history = metrics.getOrDefault(metricName, new ArrayList<>());
            return history.isEmpty() ? 0.0 : history.get(history.size() - 1);
        }
        
        public Map<String, Double> getAllCurrentMetrics() {
            Map<String, Double> current = new HashMap<>();
            metrics.forEach((name, values) -> {
                if (!values.isEmpty()) {
                    current.put(name, values.get(values.size() - 1));
                }
            });
            return current;
        }
    }
    
    // Scaling Decision Engine
    public enum ScalingAction {
        SCALE_UP, SCALE_DOWN, NO_ACTION
    }
    
    public static class ScalingDecision {
        private final ScalingAction action;
        private final int targetReplicas;
        private final String reason;
        private final Map<String, Double> triggerMetrics;
        private final LocalDateTime timestamp;
        
        public ScalingDecision(ScalingAction action, int targetReplicas, String reason, 
                             Map<String, Double> triggerMetrics) {
            this.action = action;
            this.targetReplicas = targetReplicas;
            this.reason = reason;
            this.triggerMetrics = new HashMap<>(triggerMetrics);
            this.timestamp = LocalDateTime.now();
        }
        
        // Getters
        public ScalingAction getAction() { return action; }
        public int getTargetReplicas() { return targetReplicas; }
        public String getReason() { return reason; }
        public Map<String, Double> getTriggerMetrics() { return triggerMetrics; }
        public LocalDateTime getTimestamp() { return timestamp; }
        
        @Override
        public String toString() {
            return String.format("ScalingDecision{action=%s, replicas=%d, reason='%s', time=%s}", 
                action, targetReplicas, reason, timestamp.format(DateTimeFormatter.ISO_LOCAL_TIME));
        }
    }
    
    // Paytm Payment Service Auto-Scaler
    public static class PaytmAutoScaler {
        private final String serviceName;
        private final MetricsCollector metricsCollector;
        private final ScheduledExecutorService scheduler;
        private final List<ScalingDecision> scalingHistory = new ArrayList<>();
        
        // Scaling configuration
        private int currentReplicas = 3;
        private final int minReplicas = 2;
        private final int maxReplicas = 50;
        private final Duration cooldownPeriod = Duration.ofMinutes(5);
        private LocalDateTime lastScalingTime = LocalDateTime.now().minusHours(1);
        
        // Scaling thresholds
        private final double cpuScaleUpThreshold = 70.0;
        private final double cpuScaleDownThreshold = 30.0;
        private final double memoryScaleUpThreshold = 80.0;
        private final double memoryScaleDownThreshold = 40.0;
        private final double requestRateScaleUpThreshold = 1000.0; // requests per second
        private final double requestRateScaleDownThreshold = 200.0;
        
        // Paytm specific thresholds
        private final double paymentLatencyThreshold = 500.0; // milliseconds
        private final double errorRateThreshold = 5.0; // percentage
        private final double queueDepthThreshold = 100.0; // pending transactions
        
        public PaytmAutoScaler(String serviceName) {
            this.serviceName = serviceName;
            this.metricsCollector = new MetricsCollector();
            this.scheduler = Executors.newScheduledThreadPool(2);
            
            // Start metrics collection and scaling evaluation
            startMetricsCollection();
            startScalingEvaluation();
            
            logger.info(String.format("💳 Paytm Auto-Scaler initialized for %s (replicas: %d)", 
                serviceName, currentReplicas));
        }
        
        private void startMetricsCollection() {
            // Simulate real metrics collection every 10 seconds
            scheduler.scheduleAtFixedRate(this::collectMetrics, 0, 10, TimeUnit.SECONDS);
        }
        
        private void startScalingEvaluation() {
            // Evaluate scaling decisions every 30 seconds
            scheduler.scheduleAtFixedRate(this::evaluateScaling, 30, 30, TimeUnit.SECONDS);
        }
        
        private void collectMetrics() {
            try {
                // Simulate realistic Paytm payment service metrics
                double baseLoad = getTimeBasedLoad();
                
                // CPU metrics (varies with payment processing load)
                double cpuUsage = Math.max(10, Math.min(95, 
                    baseLoad + (Math.random() - 0.5) * 20));
                metricsCollector.recordMetric("cpu_usage_percent", cpuUsage);
                
                // Memory metrics (grows with concurrent transactions)
                double memoryUsage = Math.max(20, Math.min(90, 
                    baseLoad * 0.8 + (Math.random() - 0.5) * 15));
                metricsCollector.recordMetric("memory_usage_percent", memoryUsage);
                
                // Request rate (payment transactions per second)
                double requestRate = Math.max(50, baseLoad * 20 + (Math.random() - 0.5) * 400);
                metricsCollector.recordMetric("request_rate_per_second", requestRate);
                
                // Payment specific metrics
                double paymentLatency = Math.max(50, Math.min(2000, 
                    200 + (baseLoad - 50) * 8 + (Math.random() - 0.5) * 100));
                metricsCollector.recordMetric("payment_latency_ms", paymentLatency);
                
                double errorRate = Math.max(0, Math.min(15, 
                    (baseLoad > 80 ? (baseLoad - 80) * 0.5 : 0) + Math.random() * 2));
                metricsCollector.recordMetric("error_rate_percent", errorRate);
                
                double queueDepth = Math.max(0, Math.min(500, 
                    (baseLoad - 40) * 5 + (Math.random() - 0.5) * 50));
                metricsCollector.recordMetric("queue_depth", queueDepth);
                
                // Active connections
                double activeConnections = Math.max(10, currentReplicas * 50 + (Math.random() - 0.5) * 100);
                metricsCollector.recordMetric("active_connections", activeConnections);
                
                logger.fine(String.format("📊 Metrics collected - CPU: %.1f%%, Memory: %.1f%%, " +
                    "Requests/s: %.0f, Payment Latency: %.0fms", 
                    cpuUsage, memoryUsage, requestRate, paymentLatency));
                
            } catch (Exception e) {
                logger.severe(String.format("❌ Metrics collection failed: %s", e.getMessage()));
            }
        }
        
        private double getTimeBasedLoad() {
            // Simulate time-based load patterns for Paytm
            // Peak hours: 10 AM - 2 PM and 6 PM - 10 PM
            LocalDateTime now = LocalDateTime.now();
            int hour = now.getHour();
            
            if ((hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 22)) {
                return 75 + Math.random() * 20; // Peak hours: 75-95% base load
            } else if (hour >= 6 && hour <= 9) {
                return 45 + Math.random() * 15; // Morning: 45-60% base load
            } else if (hour >= 23 || hour <= 5) {
                return 20 + Math.random() * 15; // Night: 20-35% base load
            } else {
                return 55 + Math.random() * 20; // Regular: 55-75% base load
            }
        }
        
        private void evaluateScaling() {
            try {
                if (isInCooldownPeriod()) {
                    logger.fine("❄️  Scaling evaluation skipped - in cooldown period");
                    return;
                }
                
                ScalingDecision decision = makeScalingDecision();
                
                if (decision.getAction() != ScalingAction.NO_ACTION) {
                    executeScalingDecision(decision);
                }
                
                // Record decision in history
                scalingHistory.add(decision);
                if (scalingHistory.size() > 50) {
                    scalingHistory.remove(0);
                }
                
            } catch (Exception e) {
                logger.severe(String.format("❌ Scaling evaluation failed: %s", e.getMessage()));
            }
        }
        
        private boolean isInCooldownPeriod() {
            return Duration.between(lastScalingTime, LocalDateTime.now()).compareTo(cooldownPeriod) < 0;
        }
        
        private ScalingDecision makeScalingDecision() {
            // Get current metrics (average over last 3 data points)
            Map<String, Double> currentMetrics = new HashMap<>();
            currentMetrics.put("cpu_usage", metricsCollector.getAverageMetric("cpu_usage_percent", 3));
            currentMetrics.put("memory_usage", metricsCollector.getAverageMetric("memory_usage_percent", 3));
            currentMetrics.put("request_rate", metricsCollector.getAverageMetric("request_rate_per_second", 3));
            currentMetrics.put("payment_latency", metricsCollector.getAverageMetric("payment_latency_ms", 3));
            currentMetrics.put("error_rate", metricsCollector.getAverageMetric("error_rate_percent", 3));
            currentMetrics.put("queue_depth", metricsCollector.getAverageMetric("queue_depth", 3));
            
            // Check for scale-up conditions
            ScalingDecision scaleUpDecision = checkScaleUpConditions(currentMetrics);
            if (scaleUpDecision != null) {
                return scaleUpDecision;
            }
            
            // Check for scale-down conditions  
            ScalingDecision scaleDownDecision = checkScaleDownConditions(currentMetrics);
            if (scaleDownDecision != null) {
                return scaleDownDecision;
            }
            
            return new ScalingDecision(ScalingAction.NO_ACTION, currentReplicas, 
                "All metrics within normal range", currentMetrics);
        }
        
        private ScalingDecision checkScaleUpConditions(Map<String, Double> metrics) {
            List<String> reasons = new ArrayList<>();
            
            // CPU threshold check
            if (metrics.get("cpu_usage") > cpuScaleUpThreshold) {
                reasons.add(String.format("CPU usage %.1f%% > %.1f%%", 
                    metrics.get("cpu_usage"), cpuScaleUpThreshold));
            }
            
            // Memory threshold check
            if (metrics.get("memory_usage") > memoryScaleUpThreshold) {
                reasons.add(String.format("Memory usage %.1f%% > %.1f%%", 
                    metrics.get("memory_usage"), memoryScaleUpThreshold));
            }
            
            // Request rate check
            if (metrics.get("request_rate") > requestRateScaleUpThreshold) {
                reasons.add(String.format("Request rate %.0f/s > %.0f/s", 
                    metrics.get("request_rate"), requestRateScaleUpThreshold));
            }
            
            // Payment latency check (Paytm specific)
            if (metrics.get("payment_latency") > paymentLatencyThreshold) {
                reasons.add(String.format("Payment latency %.0fms > %.0fms", 
                    metrics.get("payment_latency"), paymentLatencyThreshold));
            }
            
            // Error rate check
            if (metrics.get("error_rate") > errorRateThreshold) {
                reasons.add(String.format("Error rate %.1f%% > %.1f%%", 
                    metrics.get("error_rate"), errorRateThreshold));
            }
            
            // Queue depth check
            if (metrics.get("queue_depth") > queueDepthThreshold) {
                reasons.add(String.format("Queue depth %.0f > %.0f", 
                    metrics.get("queue_depth"), queueDepthThreshold));
            }
            
            if (!reasons.isEmpty() && currentReplicas < maxReplicas) {
                // Calculate target replicas based on severity
                int targetReplicas = calculateTargetReplicas(metrics, true);
                return new ScalingDecision(ScalingAction.SCALE_UP, targetReplicas, 
                    String.join(", ", reasons), metrics);
            }
            
            return null;
        }
        
        private ScalingDecision checkScaleDownConditions(Map<String, Double> metrics) {
            List<String> reasons = new ArrayList<>();
            
            // All conditions must be met for scale down (conservative approach)
            boolean canScaleDown = true;
            
            if (metrics.get("cpu_usage") < cpuScaleDownThreshold) {
                reasons.add(String.format("CPU usage %.1f%% < %.1f%%", 
                    metrics.get("cpu_usage"), cpuScaleDownThreshold));
            } else {
                canScaleDown = false;
            }
            
            if (metrics.get("memory_usage") < memoryScaleDownThreshold) {
                reasons.add(String.format("Memory usage %.1f%% < %.1f%%", 
                    metrics.get("memory_usage"), memoryScaleDownThreshold));
            } else {
                canScaleDown = false;
            }
            
            if (metrics.get("request_rate") < requestRateScaleDownThreshold) {
                reasons.add(String.format("Request rate %.0f/s < %.0f/s", 
                    metrics.get("request_rate"), requestRateScaleDownThreshold));
            } else {
                canScaleDown = false;
            }
            
            // Additional safety checks for scale down
            if (metrics.get("error_rate") > 2.0 || metrics.get("payment_latency") > 300) {
                canScaleDown = false;
                reasons.clear();
                reasons.add("Cannot scale down - service under stress");
            }
            
            if (canScaleDown && !reasons.isEmpty() && currentReplicas > minReplicas) {
                int targetReplicas = calculateTargetReplicas(metrics, false);
                return new ScalingDecision(ScalingAction.SCALE_DOWN, targetReplicas, 
                    String.join(", ", reasons), metrics);
            }
            
            return null;
        }
        
        private int calculateTargetReplicas(Map<String, Double> metrics, boolean scaleUp) {
            if (scaleUp) {
                // Aggressive scale-up for payment critical scenarios
                double cpuRatio = metrics.get("cpu_usage") / cpuScaleUpThreshold;
                double memRatio = metrics.get("memory_usage") / memoryScaleUpThreshold;
                double reqRatio = metrics.get("request_rate") / requestRateScaleUpThreshold;
                
                double maxRatio = Math.max(Math.max(cpuRatio, memRatio), reqRatio);
                
                // Scale up by 50-200% based on severity
                int additionalReplicas = (int) Math.ceil(currentReplicas * (maxRatio - 1));
                additionalReplicas = Math.max(1, Math.min(additionalReplicas, currentReplicas)); // Cap at 100% increase
                
                return Math.min(maxReplicas, currentReplicas + additionalReplicas);
            } else {
                // Conservative scale-down
                return Math.max(minReplicas, currentReplicas - 1);
            }
        }
        
        private void executeScalingDecision(ScalingDecision decision) {
            logger.info(String.format("🎯 Executing scaling decision: %s", decision));
            
            // Simulate scaling operation
            int previousReplicas = currentReplicas;
            currentReplicas = decision.getTargetReplicas();
            lastScalingTime = LocalDateTime.now();
            
            // In real implementation, this would call Kubernetes API or cloud provider API
            simulateScalingOperation(previousReplicas, currentReplicas);
            
            logger.info(String.format("✅ Scaling completed: %s service scaled from %d to %d replicas", 
                serviceName, previousReplicas, currentReplicas));
        }
        
        private void simulateScalingOperation(int from, int to) {
            try {
                if (to > from) {
                    // Scale up - add replicas
                    for (int i = from; i < to; i++) {
                        Thread.sleep(2000); // Simulate pod startup time
                        logger.info(String.format("🚀 Started replica %d/%d", i + 1, to));
                    }
                } else {
                    // Scale down - remove replicas  
                    for (int i = from; i > to; i--) {
                        Thread.sleep(1000); // Simulate graceful shutdown
                        logger.info(String.format("🛑 Stopped replica %d", i));
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
        
        public AutoScalerStatus getStatus() {
            Map<String, Double> currentMetrics = metricsCollector.getAllCurrentMetrics();
            
            return new AutoScalerStatus(
                serviceName,
                currentReplicas,
                minReplicas,
                maxReplicas,
                currentMetrics,
                lastScalingTime,
                isInCooldownPeriod(),
                new ArrayList<>(scalingHistory.subList(
                    Math.max(0, scalingHistory.size() - 10), scalingHistory.size()))
            );
        }
        
        // Predictive scaling based on time patterns
        public void enablePredictiveScaling() {
            scheduler.scheduleAtFixedRate(() -> {
                try {
                    int predictedReplicas = predictRequiredReplicas();
                    if (Math.abs(predictedReplicas - currentReplicas) > 1) {
                        logger.info(String.format("🔮 Predictive scaling suggestion: %d replicas " +
                            "(current: %d) based on time patterns", predictedReplicas, currentReplicas));
                    }
                } catch (Exception e) {
                    logger.warning(String.format("⚠️  Predictive scaling failed: %s", e.getMessage()));
                }
            }, 5, 5, TimeUnit.MINUTES);
        }
        
        private int predictRequiredReplicas() {
            LocalDateTime now = LocalDateTime.now();
            LocalDateTime in30Minutes = now.plusMinutes(30);
            
            // Predict load based on historical patterns
            double predictedLoad = getTimeBasedLoad(in30Minutes);
            
            // Map load to required replicas (simplified)
            if (predictedLoad > 80) {
                return Math.min(maxReplicas, (int) Math.ceil(currentReplicas * 1.5));
            } else if (predictedLoad < 40) {
                return Math.max(minReplicas, (int) Math.ceil(currentReplicas * 0.7));
            }
            
            return currentReplicas;
        }
        
        private double getTimeBasedLoad(LocalDateTime dateTime) {
            int hour = dateTime.getHour();
            if ((hour >= 10 && hour <= 14) || (hour >= 18 && hour <= 22)) {
                return 85; // Peak hours
            } else if (hour >= 6 && hour <= 9) {
                return 55; // Morning
            } else if (hour >= 23 || hour <= 5) {
                return 30; // Night
            } else {
                return 65; // Regular
            }
        }
        
        public void shutdown() {
            scheduler.shutdown();
            try {
                if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                    scheduler.shutdownNow();
                }
                logger.info("🛑 Auto-scaler shutdown completed");
            } catch (InterruptedException e) {
                scheduler.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
    
    // Auto-scaler Status
    public static class AutoScalerStatus {
        private final String serviceName;
        private final int currentReplicas;
        private final int minReplicas;
        private final int maxReplicas;
        private final Map<String, Double> currentMetrics;
        private final LocalDateTime lastScalingTime;
        private final boolean inCooldownPeriod;
        private final List<ScalingDecision> recentDecisions;
        
        public AutoScalerStatus(String serviceName, int currentReplicas, int minReplicas, 
                               int maxReplicas, Map<String, Double> currentMetrics, 
                               LocalDateTime lastScalingTime, boolean inCooldownPeriod,
                               List<ScalingDecision> recentDecisions) {
            this.serviceName = serviceName;
            this.currentReplicas = currentReplicas;
            this.minReplicas = minReplicas;
            this.maxReplicas = maxReplicas;
            this.currentMetrics = new HashMap<>(currentMetrics);
            this.lastScalingTime = lastScalingTime;
            this.inCooldownPeriod = inCooldownPeriod;
            this.recentDecisions = new ArrayList<>(recentDecisions);
        }
        
        // Getters
        public String getServiceName() { return serviceName; }
        public int getCurrentReplicas() { return currentReplicas; }
        public int getMinReplicas() { return minReplicas; }
        public int getMaxReplicas() { return maxReplicas; }
        public Map<String, Double> getCurrentMetrics() { return currentMetrics; }
        public LocalDateTime getLastScalingTime() { return lastScalingTime; }
        public boolean isInCooldownPeriod() { return inCooldownPeriod; }
        public List<ScalingDecision> getRecentDecisions() { return recentDecisions; }
        
        public void printStatus() {
            System.out.println(String.format("\n📊 Auto-Scaler Status: %s", serviceName));
            System.out.println("=".repeat(50));
            System.out.printf("Current Replicas: %d (min: %d, max: %d)\n", 
                currentReplicas, minReplicas, maxReplicas);
            System.out.printf("Last Scaling: %s\n", 
                lastScalingTime.format(DateTimeFormatter.ISO_LOCAL_TIME));
            System.out.printf("Cooldown Period: %s\n", inCooldownPeriod ? "Active" : "Inactive");
            
            System.out.println("\nCurrent Metrics:");
            currentMetrics.forEach((metric, value) -> {
                System.out.printf("  %s: %.1f\n", metric, value);
            });
            
            if (!recentDecisions.isEmpty()) {
                System.out.println("\nRecent Scaling Decisions:");
                recentDecisions.stream()
                    .sorted((a, b) -> b.getTimestamp().compareTo(a.getTimestamp()))
                    .limit(5)
                    .forEach(decision -> System.out.printf("  %s\n", decision));
            }
        }
    }
}

// Demo Class
class PaytmAutoScalingDemo {
    private static final Logger logger = Logger.getLogger(PaytmAutoScalingDemo.class.getName());
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("💳 Paytm Auto-Scaling Demo");
        System.out.println("=".repeat(50));
        
        // Initialize auto-scaler for Paytm payment service
        AutoScalingSystem.PaytmAutoScaler autoScaler = 
            new AutoScalingSystem.PaytmAutoScaler("paytm-payment-processor");
        
        // Enable predictive scaling
        autoScaler.enablePredictiveScaling();
        
        System.out.println("🚀 Auto-scaler started. Monitoring payment service metrics...");
        System.out.println("📈 Simulating various load conditions over time\n");
        
        // Run demo for 2 minutes
        for (int i = 0; i < 8; i++) {
            Thread.sleep(15000); // Wait 15 seconds between status updates
            
            AutoScalingSystem.AutoScalerStatus status = autoScaler.getStatus();
            status.printStatus();
            
            // Simulate load changes
            if (i == 2) {
                System.out.println("\n🔥 Simulating payment rush (Diwali shopping)...");
            } else if (i == 5) {
                System.out.println("\n😴 Simulating low traffic period (late night)...");
            }
        }
        
        // Final status
        System.out.println("\n📊 Final Auto-Scaler Status:");
        autoScaler.getStatus().printStatus();
        
        // Cleanup
        autoScaler.shutdown();
        
        System.out.println("\n" + "=".repeat(50));
        System.out.println("🎯 Paytm Auto-Scaling Demo Complete!");
        printLearnings();
    }
    
    private static void printLearnings() {
        System.out.println("Key Auto-Scaling Features Demonstrated:");
        System.out.println("1. 📊 Multi-metric monitoring (CPU, Memory, Request Rate)");
        System.out.println("2. 💳 Payment-specific metrics (Latency, Error Rate, Queue Depth)");
        System.out.println("3. 🎯 Intelligent scaling decisions with multiple thresholds");
        System.out.println("4. ❄️  Cooldown periods to prevent thrashing");
        System.out.println("5. 🔮 Predictive scaling based on time patterns");
        System.out.println("6. 🛡️  Conservative scale-down with safety checks");
        System.out.println("7. 📈 Aggressive scale-up for critical scenarios");
        System.out.println("8. 📊 Comprehensive status monitoring and history");
    }
}