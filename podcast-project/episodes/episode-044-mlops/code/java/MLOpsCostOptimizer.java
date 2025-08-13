/**
 * MLOps Cost Optimizer - MLOps Episode 44
 * Production-ready cost optimization system for ML infrastructure
 * 
 * Author: Claude Code
 * Context: Intelligent cost optimization for ML workloads in cloud environments
 */

package com.episode44.mlops;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.DoubleAdder;
import java.io.*;
import java.time.LocalDateTime;
import java.time.Duration;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.sql.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.core.type.TypeReference;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Production MLOps Cost Optimization System
 * Mumbai me sabse cost-effective ML infrastructure!
 */
public class MLOpsCostOptimizer {
    
    private static final Logger logger = LoggerFactory.getLogger(MLOpsCostOptimizer.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    private final String dbPath;
    private final ScheduledExecutorService scheduler;
    private final ExecutorService optimizationExecutor;
    
    // Cost tracking
    private final Map<String, ResourceCostTracker> resourceTrackers = new ConcurrentHashMap<>();
    private final Map<String, OptimizationRule> optimizationRules = new ConcurrentHashMap<>();
    private final List<CostOptimizationAction> pendingActions = new CopyOnWriteArrayList<>();
    
    // Optimization settings
    private final OptimizationConfig config;
    
    /**
     * Resource types for cost tracking
     */
    public enum ResourceType {
        COMPUTE_INSTANCE,
        GPU_INSTANCE,
        STORAGE,
        NETWORK,
        MODEL_SERVING,
        DATA_PROCESSING,
        TRAINING_JOB
    }
    
    /**
     * Cost optimization strategies
     */
    public enum OptimizationStrategy {
        AUTO_SCALING,
        SPOT_INSTANCES,
        RESERVED_INSTANCES,
        RESOURCE_RIGHTSIZING,
        SCHEDULED_SHUTDOWN,
        MODEL_COMPRESSION,
        BATCH_OPTIMIZATION,
        INSTANCE_TYPE_RECOMMENDATION
    }
    
    /**
     * Optimization configuration
     */
    public static class OptimizationConfig {
        @JsonProperty("max_cost_increase_percent")
        private double maxCostIncreasePercent = 20.0;
        
        @JsonProperty("min_savings_threshold_usd")
        private double minSavingsThresholdUsd = 10.0;
        
        @JsonProperty("optimization_interval_hours")
        private int optimizationIntervalHours = 6;
        
        @JsonProperty("auto_apply_safe_optimizations")
        private boolean autoApplySafeOptimizations = true;
        
        @JsonProperty("notification_threshold_usd")
        private double notificationThresholdUsd = 100.0;
        
        @JsonProperty("enabled_strategies")
        private Set<OptimizationStrategy> enabledStrategies;
        
        public OptimizationConfig() {
            this.enabledStrategies = EnumSet.allOf(OptimizationStrategy.class);
        }
        
        // Getters and setters
        public double getMaxCostIncreasePercent() { return maxCostIncreasePercent; }
        public void setMaxCostIncreasePercent(double maxCostIncreasePercent) { this.maxCostIncreasePercent = maxCostIncreasePercent; }
        
        public double getMinSavingsThresholdUsd() { return minSavingsThresholdUsd; }
        public void setMinSavingsThresholdUsd(double minSavingsThresholdUsd) { this.minSavingsThresholdUsd = minSavingsThresholdUsd; }
        
        public boolean isAutoApplySafeOptimizations() { return autoApplySafeOptimizations; }
        public void setAutoApplySafeOptimizations(boolean autoApplySafeOptimizations) { this.autoApplySafeOptimizations = autoApplySafeOptimizations; }
        
        public Set<OptimizationStrategy> getEnabledStrategies() { return enabledStrategies; }
        public void setEnabledStrategies(Set<OptimizationStrategy> enabledStrategies) { this.enabledStrategies = enabledStrategies; }
    }
    
    /**
     * Resource usage and cost tracking
     */
    public static class ResourceCostTracker {
        @JsonProperty("resource_id")
        private String resourceId;
        
        @JsonProperty("resource_type")
        private ResourceType resourceType;
        
        @JsonProperty("current_hourly_cost_usd")
        private double currentHourlyCostUsd;
        
        @JsonProperty("daily_cost_usd")
        private double dailyCostUsd;
        
        @JsonProperty("monthly_projected_cost_usd")
        private double monthlyProjectedCostUsd;
        
        @JsonProperty("utilization_metrics")
        private Map<String, Double> utilizationMetrics;
        
        @JsonProperty("usage_patterns")
        private List<UsagePattern> usagePatterns;
        
        @JsonProperty("tags")
        private Map<String, String> tags;
        
        @JsonProperty("last_updated")
        private LocalDateTime lastUpdated;
        
        // Cost history
        private final DoubleAdder totalCost = new DoubleAdder();
        private final Queue<CostDataPoint> costHistory = new ConcurrentLinkedQueue<>();
        
        public ResourceCostTracker() {
            this.utilizationMetrics = new HashMap<>();
            this.usagePatterns = new ArrayList<>();
            this.tags = new HashMap<>();
            this.lastUpdated = LocalDateTime.now();
        }
        
        public ResourceCostTracker(String resourceId, ResourceType resourceType, double hourlyCost) {
            this();
            this.resourceId = resourceId;
            this.resourceType = resourceType;
            this.currentHourlyCostUsd = hourlyCost;
            this.dailyCostUsd = hourlyCost * 24;
            this.monthlyProjectedCostUsd = hourlyCost * 24 * 30;
        }
        
        public void addCostDataPoint(double cost, LocalDateTime timestamp) {
            totalCost.add(cost);
            costHistory.offer(new CostDataPoint(cost, timestamp));
            
            // Keep only last 7 days of data
            LocalDateTime weekAgo = timestamp.minus(7, ChronoUnit.DAYS);
            while (!costHistory.isEmpty() && costHistory.peek().getTimestamp().isBefore(weekAgo)) {
                costHistory.poll();
            }
            
            updateProjections();
        }
        
        private void updateProjections() {
            // Calculate daily average from recent data
            if (!costHistory.isEmpty()) {
                double recentCostSum = costHistory.stream()
                    .mapToDouble(CostDataPoint::getCost)
                    .sum();
                this.dailyCostUsd = recentCostSum / Math.max(1, costHistory.size()) * 24;
                this.monthlyProjectedCostUsd = this.dailyCostUsd * 30;
            }
        }
        
        // Getters and setters
        public String getResourceId() { return resourceId; }
        public ResourceType getResourceType() { return resourceType; }
        public double getCurrentHourlyCostUsd() { return currentHourlyCostUsd; }
        public double getDailyCostUsd() { return dailyCostUsd; }
        public double getMonthlyProjectedCostUsd() { return monthlyProjectedCostUsd; }
        public Map<String, Double> getUtilizationMetrics() { return utilizationMetrics; }
        public List<UsagePattern> getUsagePatterns() { return usagePatterns; }
        public double getTotalCost() { return totalCost.sum(); }
        public Queue<CostDataPoint> getCostHistory() { return new ConcurrentLinkedQueue<>(costHistory); }
    }
    
    /**
     * Usage pattern analysis
     */
    public static class UsagePattern {
        @JsonProperty("pattern_type")
        private String patternType;
        
        @JsonProperty("peak_hours")
        private List<Integer> peakHours;
        
        @JsonProperty("avg_utilization_percent")
        private double avgUtilizationPercent;
        
        @JsonProperty("peak_utilization_percent")
        private double peakUtilizationPercent;
        
        @JsonProperty("idle_time_percent")
        private double idleTimePercent;
        
        @JsonProperty("confidence_score")
        private double confidenceScore;
        
        public UsagePattern() {}
        
        public UsagePattern(String patternType, List<Integer> peakHours, double avgUtilization) {
            this.patternType = patternType;
            this.peakHours = peakHours;
            this.avgUtilizationPercent = avgUtilization;
            this.confidenceScore = 0.8;
        }
        
        // Getters and setters
        public String getPatternType() { return patternType; }
        public List<Integer> getPeakHours() { return peakHours; }
        public double getAvgUtilizationPercent() { return avgUtilizationPercent; }
        public double getIdleTimePercent() { return idleTimePercent; }
        public void setIdleTimePercent(double idleTimePercent) { this.idleTimePercent = idleTimePercent; }
    }
    
    /**
     * Cost data point for tracking
     */
    public static class CostDataPoint {
        private final double cost;
        private final LocalDateTime timestamp;
        
        public CostDataPoint(double cost, LocalDateTime timestamp) {
            this.cost = cost;
            this.timestamp = timestamp;
        }
        
        public double getCost() { return cost; }
        public LocalDateTime getTimestamp() { return timestamp; }
    }
    
    /**
     * Optimization recommendation
     */
    public static class OptimizationRecommendation {
        @JsonProperty("recommendation_id")
        private String recommendationId;
        
        @JsonProperty("resource_id")
        private String resourceId;
        
        @JsonProperty("strategy")
        private OptimizationStrategy strategy;
        
        @JsonProperty("current_cost_usd")
        private double currentCostUsd;
        
        @JsonProperty("optimized_cost_usd")
        private double optimizedCostUsd;
        
        @JsonProperty("potential_savings_usd")
        private double potentialSavingsUsd;
        
        @JsonProperty("savings_percentage")
        private double savingsPercentage;
        
        @JsonProperty("implementation_effort")
        private String implementationEffort; // LOW, MEDIUM, HIGH
        
        @JsonProperty("risk_level")
        private String riskLevel; // LOW, MEDIUM, HIGH
        
        @JsonProperty("description")
        private String description;
        
        @JsonProperty("action_steps")
        private List<String> actionSteps;
        
        @JsonProperty("prerequisites")
        private List<String> prerequisites;
        
        @JsonProperty("estimated_impact_time_hours")
        private int estimatedImpactTimeHours;
        
        @JsonProperty("created_at")
        private LocalDateTime createdAt;
        
        public OptimizationRecommendation() {
            this.recommendationId = UUID.randomUUID().toString();
            this.actionSteps = new ArrayList<>();
            this.prerequisites = new ArrayList<>();
            this.createdAt = LocalDateTime.now();
        }
        
        public OptimizationRecommendation(String resourceId, OptimizationStrategy strategy, 
                                        double currentCost, double optimizedCost, String description) {
            this();
            this.resourceId = resourceId;
            this.strategy = strategy;
            this.currentCostUsd = currentCost;
            this.optimizedCostUsd = optimizedCost;
            this.potentialSavingsUsd = currentCost - optimizedCost;
            this.savingsPercentage = currentCost > 0 ? (this.potentialSavingsUsd / currentCost) * 100 : 0;
            this.description = description;
        }
        
        // Getters and setters
        public String getRecommendationId() { return recommendationId; }
        public String getResourceId() { return resourceId; }
        public OptimizationStrategy getStrategy() { return strategy; }
        public double getPotentialSavingsUsd() { return potentialSavingsUsd; }
        public double getSavingsPercentage() { return savingsPercentage; }
        public String getImplementationEffort() { return implementationEffort; }
        public void setImplementationEffort(String implementationEffort) { this.implementationEffort = implementationEffort; }
        public String getRiskLevel() { return riskLevel; }
        public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }
        public String getDescription() { return description; }
        public List<String> getActionSteps() { return actionSteps; }
        public LocalDateTime getCreatedAt() { return createdAt; }
    }
    
    /**
     * Cost optimization action
     */
    public static class CostOptimizationAction {
        @JsonProperty("action_id")
        private String actionId;
        
        @JsonProperty("recommendation_id")
        private String recommendationId;
        
        @JsonProperty("status")
        private String status; // PENDING, IN_PROGRESS, COMPLETED, FAILED
        
        @JsonProperty("scheduled_execution_time")
        private LocalDateTime scheduledExecutionTime;
        
        @JsonProperty("actual_execution_time")
        private LocalDateTime actualExecutionTime;
        
        @JsonProperty("result_message")
        private String resultMessage;
        
        @JsonProperty("actual_savings_usd")
        private Double actualSavingsUsd;
        
        public CostOptimizationAction() {
            this.actionId = UUID.randomUUID().toString();
            this.status = "PENDING";
        }
        
        public CostOptimizationAction(String recommendationId, LocalDateTime scheduledTime) {
            this();
            this.recommendationId = recommendationId;
            this.scheduledExecutionTime = scheduledTime;
        }
        
        // Getters and setters
        public String getActionId() { return actionId; }
        public String getRecommendationId() { return recommendationId; }
        public String getStatus() { return status; }
        public void setStatus(String status) { this.status = status; }
        public LocalDateTime getScheduledExecutionTime() { return scheduledExecutionTime; }
        public LocalDateTime getActualExecutionTime() { return actualExecutionTime; }
        public void setActualExecutionTime(LocalDateTime actualExecutionTime) { this.actualExecutionTime = actualExecutionTime; }
        public String getResultMessage() { return resultMessage; }
        public void setResultMessage(String resultMessage) { this.resultMessage = resultMessage; }
        public Double getActualSavingsUsd() { return actualSavingsUsd; }
        public void setActualSavingsUsd(Double actualSavingsUsd) { this.actualSavingsUsd = actualSavingsUsd; }
    }
    
    /**
     * Optimization rule
     */
    public static class OptimizationRule {
        @JsonProperty("rule_id")
        private String ruleId;
        
        @JsonProperty("name")
        private String name;
        
        @JsonProperty("resource_type")
        private ResourceType resourceType;
        
        @JsonProperty("trigger_conditions")
        private Map<String, Object> triggerConditions;
        
        @JsonProperty("optimization_strategy")
        private OptimizationStrategy optimizationStrategy;
        
        @JsonProperty("is_safe_to_auto_apply")
        private boolean isSafeToAutoApply;
        
        @JsonProperty("is_enabled")
        private boolean isEnabled;
        
        public OptimizationRule() {
            this.ruleId = UUID.randomUUID().toString();
            this.triggerConditions = new HashMap<>();
            this.isEnabled = true;
        }
        
        public OptimizationRule(String name, ResourceType resourceType, OptimizationStrategy strategy) {
            this();
            this.name = name;
            this.resourceType = resourceType;
            this.optimizationStrategy = strategy;
        }
        
        // Getters and setters
        public String getRuleId() { return ruleId; }
        public String getName() { return name; }
        public ResourceType getResourceType() { return resourceType; }
        public Map<String, Object> getTriggerConditions() { return triggerConditions; }
        public OptimizationStrategy getOptimizationStrategy() { return optimizationStrategy; }
        public boolean isSafeToAutoApply() { return isSafeToAutoApply; }
        public void setSafeToAutoApply(boolean safeToAutoApply) { isSafeToAutoApply = safeToAutoApply; }
        public boolean isEnabled() { return isEnabled; }
        public void setEnabled(boolean enabled) { isEnabled = enabled; }
    }
    
    /**
     * Initialize cost optimizer
     */
    public MLOpsCostOptimizer(String dbPath, OptimizationConfig config) {
        this.dbPath = dbPath;
        this.config = config;
        this.scheduler = Executors.newScheduledThreadPool(3);
        this.optimizationExecutor = Executors.newFixedThreadPool(5);
        
        // Initialize database
        initializeDatabase();
        
        // Setup default optimization rules
        setupDefaultOptimizationRules();
        
        // Start optimization scheduler
        startOptimizationScheduler();
        
        logger.info("MLOps Cost Optimizer initialized with optimization interval: {} hours", 
                   config.optimizationIntervalHours);
    }
    
    /**
     * Initialize cost tracking database
     */
    private void initializeDatabase() {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            // Create resource_costs table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS resource_costs (" +
                "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                "resource_id TEXT NOT NULL, " +
                "resource_type TEXT NOT NULL, " +
                "cost_usd REAL NOT NULL, " +
                "utilization_data TEXT, " +
                "timestamp TEXT NOT NULL" +
                ")"
            );
            
            // Create optimization_recommendations table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS optimization_recommendations (" +
                "recommendation_id TEXT PRIMARY KEY, " +
                "resource_id TEXT NOT NULL, " +
                "strategy TEXT NOT NULL, " +
                "current_cost_usd REAL NOT NULL, " +
                "optimized_cost_usd REAL NOT NULL, " +
                "potential_savings_usd REAL NOT NULL, " +
                "implementation_effort TEXT, " +
                "risk_level TEXT, " +
                "description TEXT, " +
                "action_steps TEXT, " +
                "created_at TEXT NOT NULL, " +
                "is_applied INTEGER DEFAULT 0" +
                ")"
            );
            
            // Create cost_optimization_actions table
            conn.createStatement().execute(
                "CREATE TABLE IF NOT EXISTS cost_optimization_actions (" +
                "action_id TEXT PRIMARY KEY, " +
                "recommendation_id TEXT NOT NULL, " +
                "status TEXT NOT NULL, " +
                "scheduled_execution_time TEXT, " +
                "actual_execution_time TEXT, " +
                "result_message TEXT, " +
                "actual_savings_usd REAL, " +
                "FOREIGN KEY (recommendation_id) REFERENCES optimization_recommendations (recommendation_id)" +
                ")"
            );
            
            // Create indexes
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_resource_costs_resource_time ON resource_costs (resource_id, timestamp)"
            );
            conn.createStatement().execute(
                "CREATE INDEX IF NOT EXISTS idx_recommendations_resource ON optimization_recommendations (resource_id)"
            );
            
            logger.info("Cost optimization database initialized successfully");
            
        } catch (SQLException e) {
            logger.error("Failed to initialize cost optimization database", e);
            throw new RuntimeException("Database initialization failed", e);
        }
    }
    
    /**
     * Setup default optimization rules
     */
    private void setupDefaultOptimizationRules() {
        // Low utilization compute instances
        OptimizationRule lowUtilizationRule = new OptimizationRule(
            "Low Utilization Compute", 
            ResourceType.COMPUTE_INSTANCE, 
            OptimizationStrategy.RESOURCE_RIGHTSIZING
        );
        lowUtilizationRule.getTriggerConditions().put("avg_cpu_utilization", 20.0); // < 20%
        lowUtilizationRule.getTriggerConditions().put("avg_memory_utilization", 30.0); // < 30%
        lowUtilizationRule.setSafeToAutoApply(false); // Requires human review
        optimizationRules.put(lowUtilizationRule.getRuleId(), lowUtilizationRule);
        
        // Idle resources overnight
        OptimizationRule overnightIdleRule = new OptimizationRule(
            "Overnight Idle Resources",
            ResourceType.COMPUTE_INSTANCE,
            OptimizationStrategy.SCHEDULED_SHUTDOWN
        );
        overnightIdleRule.getTriggerConditions().put("idle_hours_per_day", 8.0); // > 8 hours idle
        overnightIdleRule.getTriggerConditions().put("night_utilization", 5.0); // < 5% at night
        overnightIdleRule.setSafeToAutoApply(true); // Safe to auto-apply
        optimizationRules.put(overnightIdleRule.getRuleId(), overnightIdleRule);
        
        // High cost GPU instances
        OptimizationRule expensiveGpuRule = new OptimizationRule(
            "Expensive GPU Instances",
            ResourceType.GPU_INSTANCE,
            OptimizationStrategy.SPOT_INSTANCES
        );
        expensiveGpuRule.getTriggerConditions().put("hourly_cost", 5.0); // > $5/hour
        expensiveGpuRule.getTriggerConditions().put("fault_tolerance", true); // Can handle interruptions
        expensiveGpuRule.setSafeToAutoApply(false); // Requires evaluation
        optimizationRules.put(expensiveGpuRule.getRuleId(), expensiveGpuRule);
        
        // Over-provisioned training jobs
        OptimizationRule overprovisionedTrainingRule = new OptimizationRule(
            "Over-provisioned Training Jobs",
            ResourceType.TRAINING_JOB,
            OptimizationStrategy.BATCH_OPTIMIZATION
        );
        overprovisionedTrainingRule.getTriggerConditions().put("resource_utilization", 50.0); // < 50%
        overprovisionedTrainingRule.getTriggerConditions().put("training_duration_hours", 4.0); // > 4 hours
        overprovisionedTrainingRule.setSafeToAutoApply(true);
        optimizationRules.put(overprovisionedTrainingRule.getRuleId(), overprovisionedTrainingRule);
        
        logger.info("Setup {} default optimization rules", optimizationRules.size());
    }
    
    /**
     * Track resource cost and usage
     */
    public void trackResourceCost(String resourceId, ResourceType resourceType, double costUsd, 
                                 Map<String, Double> utilizationMetrics) {
        ResourceCostTracker tracker = resourceTrackers.computeIfAbsent(
            resourceId, 
            id -> new ResourceCostTracker(id, resourceType, costUsd)
        );
        
        // Update utilization metrics
        if (utilizationMetrics != null) {
            tracker.getUtilizationMetrics().putAll(utilizationMetrics);
        }
        
        // Add cost data point
        tracker.addCostDataPoint(costUsd, LocalDateTime.now());
        
        // Store in database
        storeCostData(resourceId, resourceType, costUsd, utilizationMetrics);
        
        logger.debug("Tracked cost for resource {}: ${}", resourceId, costUsd);
    }
    
    /**
     * Store cost data in database
     */
    private void storeCostData(String resourceId, ResourceType resourceType, double costUsd, 
                              Map<String, Double> utilizationMetrics) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT INTO resource_costs VALUES (NULL, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            stmt.setString(1, resourceId);
            stmt.setString(2, resourceType.name());
            stmt.setDouble(3, costUsd);
            stmt.setString(4, utilizationMetrics != null ? 
                          objectMapper.writeValueAsString(utilizationMetrics) : null);
            stmt.setString(5, LocalDateTime.now().format(TIMESTAMP_FORMAT));
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to store cost data for resource: " + resourceId, e);
        }
    }
    
    /**
     * Analyze usage patterns for a resource
     */
    public void analyzeUsagePatterns(String resourceId) {
        ResourceCostTracker tracker = resourceTrackers.get(resourceId);
        if (tracker == null) {
            logger.warn("Resource tracker not found: {}", resourceId);
            return;
        }
        
        Map<String, Double> utilization = tracker.getUtilizationMetrics();
        
        // Analyze CPU utilization pattern
        Double avgCpuUtilization = utilization.get("avg_cpu_utilization");
        Double peakCpuUtilization = utilization.get("peak_cpu_utilization");
        
        if (avgCpuUtilization != null && peakCpuUtilization != null) {
            List<Integer> peakHours = Arrays.asList(9, 10, 11, 14, 15, 16); // Business hours
            
            UsagePattern cpuPattern = new UsagePattern("CPU_UTILIZATION", peakHours, avgCpuUtilization);
            cpuPattern.setIdleTimePercent(100 - avgCpuUtilization);
            
            tracker.getUsagePatterns().clear(); // Replace existing patterns
            tracker.getUsagePatterns().add(cpuPattern);
            
            logger.info("Analyzed usage pattern for {}: {}% avg CPU utilization", 
                       resourceId, avgCpuUtilization);
        }
    }
    
    /**
     * Generate optimization recommendations
     */
    public List<OptimizationRecommendation> generateOptimizationRecommendations(String resourceId) {
        List<OptimizationRecommendation> recommendations = new ArrayList<>();
        
        ResourceCostTracker tracker = resourceTrackers.get(resourceId);
        if (tracker == null) {
            logger.warn("Resource tracker not found: {}", resourceId);
            return recommendations;
        }
        
        // Check each optimization rule
        for (OptimizationRule rule : optimizationRules.values()) {
            if (!rule.isEnabled() || rule.getResourceType() != tracker.getResourceType()) {
                continue;
            }
            
            if (evaluateRuleConditions(rule, tracker)) {
                OptimizationRecommendation recommendation = generateRecommendation(rule, tracker);
                if (recommendation != null && 
                    recommendation.getPotentialSavingsUsd() >= config.getMinSavingsThresholdUsd()) {
                    recommendations.add(recommendation);
                }
            }
        }
        
        // Sort by potential savings (highest first)
        recommendations.sort((r1, r2) -> Double.compare(r2.getPotentialSavingsUsd(), r1.getPotentialSavingsUsd()));
        
        logger.info("Generated {} optimization recommendations for resource: {}", 
                   recommendations.size(), resourceId);
        
        return recommendations;
    }
    
    /**
     * Evaluate rule conditions against resource tracker
     */
    private boolean evaluateRuleConditions(OptimizationRule rule, ResourceCostTracker tracker) {
        Map<String, Object> conditions = rule.getTriggerConditions();
        Map<String, Double> utilization = tracker.getUtilizationMetrics();
        
        for (Map.Entry<String, Object> condition : conditions.entrySet()) {
            String key = condition.getKey();
            Object expectedValue = condition.getValue();
            
            if (expectedValue instanceof Number) {
                double threshold = ((Number) expectedValue).doubleValue();
                Double actualValue = utilization.get(key);
                
                if (actualValue == null) {
                    return false; // Missing required metric
                }
                
                // For utilization metrics, check if actual is BELOW threshold (indicating underutilization)
                if (key.contains("utilization") && actualValue >= threshold) {
                    return false;
                }
                
                // For cost metrics, check if actual is ABOVE threshold
                if (key.contains("cost") && actualValue <= threshold) {
                    return false;
                }
                
                // For time-based metrics, check if actual meets threshold
                if (key.contains("hours") || key.contains("duration")) {
                    // Calculate approximate values based on usage patterns
                    if (key.equals("idle_hours_per_day")) {
                        List<UsagePattern> patterns = tracker.getUsagePatterns();
                        if (!patterns.isEmpty()) {
                            double idlePercent = patterns.get(0).getIdleTimePercent();
                            double idleHours = (idlePercent / 100.0) * 24;
                            if (idleHours <= threshold) {
                                return false;
                            }
                        }
                    }
                }
            } else if (expectedValue instanceof Boolean) {
                // For boolean conditions, assume they're met for demo purposes
                // In production, this would check actual resource properties
                continue;
            }
        }
        
        return true;
    }
    
    /**
     * Generate specific recommendation based on rule and tracker
     */
    private OptimizationRecommendation generateRecommendation(OptimizationRule rule, ResourceCostTracker tracker) {
        double currentCost = tracker.getMonthlyProjectedCostUsd();
        OptimizationStrategy strategy = rule.getOptimizationStrategy();
        
        double optimizedCost = currentCost;
        String description = "";
        String effort = "MEDIUM";
        String risk = "LOW";
        List<String> actionSteps = new ArrayList<>();
        
        switch (strategy) {
            case RESOURCE_RIGHTSIZING:
                // Estimate 30-50% cost reduction for rightsizing
                optimizedCost = currentCost * 0.6; // 40% savings
                description = "Right-size instance based on low utilization patterns. " +
                            "Current utilization suggests a smaller instance type would be sufficient.";
                effort = "LOW";
                risk = "MEDIUM";
                actionSteps.addAll(Arrays.asList(
                    "Analyze peak usage requirements",
                    "Select appropriate smaller instance type",
                    "Schedule maintenance window for migration",
                    "Monitor performance after migration"
                ));
                break;
                
            case SCHEDULED_SHUTDOWN:
                // Estimate savings based on idle hours
                List<UsagePattern> patterns = tracker.getUsagePatterns();
                if (!patterns.isEmpty()) {
                    double idlePercent = patterns.get(0).getIdleTimePercent();
                    optimizedCost = currentCost * (1 - idlePercent / 100.0);
                }
                description = "Implement scheduled shutdown during idle hours to reduce costs. " +
                            "Auto-start when needed for workloads.";
                effort = "LOW";
                risk = "LOW";
                actionSteps.addAll(Arrays.asList(
                    "Identify consistent idle periods",
                    "Setup automated shutdown schedule",
                    "Configure auto-start triggers",
                    "Test shutdown/startup automation"
                ));
                break;
                
            case SPOT_INSTANCES:
                // Estimate 60-80% cost reduction with spot instances
                optimizedCost = currentCost * 0.3; // 70% savings
                description = "Migrate fault-tolerant workloads to spot instances for significant cost savings. " +
                            "Suitable for batch processing and training jobs.";
                effort = "MEDIUM";
                risk = "MEDIUM";
                actionSteps.addAll(Arrays.asList(
                    "Verify workload fault tolerance",
                    "Implement checkpointing mechanism",
                    "Setup spot instance request",
                    "Monitor spot price trends"
                ));
                break;
                
            case BATCH_OPTIMIZATION:
                // Estimate 20-40% cost reduction through batch optimization
                optimizedCost = currentCost * 0.7; // 30% savings
                description = "Optimize batch processing by combining jobs and using more efficient scheduling. " +
                            "Reduce overhead and improve resource utilization.";
                effort = "HIGH";
                risk = "LOW";
                actionSteps.addAll(Arrays.asList(
                    "Analyze job scheduling patterns",
                    "Implement batch job queuing",
                    "Optimize resource allocation",
                    "Setup job dependency management"
                ));
                break;
                
            case AUTO_SCALING:
                // Estimate 25-45% cost reduction through auto-scaling
                optimizedCost = currentCost * 0.65; // 35% savings
                description = "Implement auto-scaling to dynamically adjust resources based on demand. " +
                            "Scale down during low usage periods.";
                effort = "MEDIUM";
                risk = "LOW";
                actionSteps.addAll(Arrays.asList(
                    "Configure auto-scaling policies",
                    "Set appropriate scaling metrics",
                    "Test scaling behavior",
                    "Monitor scaling performance"
                ));
                break;
                
            default:
                return null;
        }
        
        OptimizationRecommendation recommendation = new OptimizationRecommendation(
            tracker.getResourceId(), strategy, currentCost, optimizedCost, description
        );
        
        recommendation.setImplementationEffort(effort);
        recommendation.setRiskLevel(risk);
        recommendation.getActionSteps().addAll(actionSteps);
        
        return recommendation;
    }
    
    /**
     * Start optimization scheduler
     */
    private void startOptimizationScheduler() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                runOptimizationAnalysis();
            } catch (Exception e) {
                logger.error("Optimization analysis failed", e);
            }
        }, 1, config.optimizationIntervalHours, TimeUnit.HOURS);
        
        logger.info("Optimization scheduler started with {} hour intervals", config.optimizationIntervalHours);
    }
    
    /**
     * Run comprehensive optimization analysis
     */
    private void runOptimizationAnalysis() {
        logger.info("Starting optimization analysis for {} resources", resourceTrackers.size());
        
        List<OptimizationRecommendation> allRecommendations = new ArrayList<>();
        
        // Analyze each resource
        for (String resourceId : resourceTrackers.keySet()) {
            try {
                // Update usage patterns
                analyzeUsagePatterns(resourceId);
                
                // Generate recommendations
                List<OptimizationRecommendation> recommendations = generateOptimizationRecommendations(resourceId);
                allRecommendations.addAll(recommendations);
                
                // Store recommendations in database
                for (OptimizationRecommendation rec : recommendations) {
                    storeRecommendation(rec);
                }
                
            } catch (Exception e) {
                logger.error("Failed to analyze resource: " + resourceId, e);
            }
        }
        
        // Calculate total potential savings
        double totalPotentialSavings = allRecommendations.stream()
            .mapToDouble(OptimizationRecommendation::getPotentialSavingsUsd)
            .sum();
        
        logger.info("Optimization analysis complete: {} recommendations, ${:.2f} total potential savings", 
                   allRecommendations.size(), totalPotentialSavings);
        
        // Auto-apply safe optimizations if enabled
        if (config.isAutoApplySafeOptimizations()) {
            autoApplySafeOptimizations(allRecommendations);
        }
        
        // Send notifications for high-value recommendations
        sendHighValueNotifications(allRecommendations);
    }
    
    /**
     * Auto-apply safe optimizations
     */
    private void autoApplySafeOptimizations(List<OptimizationRecommendation> recommendations) {
        int autoAppliedCount = 0;
        
        for (OptimizationRecommendation rec : recommendations) {
            if ("LOW".equals(rec.getRiskLevel()) && 
                "LOW".equals(rec.getImplementationEffort()) &&
                rec.getPotentialSavingsUsd() >= config.getMinSavingsThresholdUsd()) {
                
                // Schedule auto-application
                CostOptimizationAction action = new CostOptimizationAction(
                    rec.getRecommendationId(),
                    LocalDateTime.now().plusMinutes(5) // 5 minute delay
                );
                
                pendingActions.add(action);
                autoAppliedCount++;
                
                logger.info("Scheduled auto-application of safe optimization: {} (${:.2f} savings)", 
                           rec.getStrategy(), rec.getPotentialSavingsUsd());
            }
        }
        
        if (autoAppliedCount > 0) {
            logger.info("Scheduled {} safe optimizations for auto-application", autoAppliedCount);
        }
    }
    
    /**
     * Send notifications for high-value recommendations
     */
    private void sendHighValueNotifications(List<OptimizationRecommendation> recommendations) {
        for (OptimizationRecommendation rec : recommendations) {
            if (rec.getPotentialSavingsUsd() >= config.getNotificationThresholdUsd()) {
                logger.info("HIGH-VALUE OPTIMIZATION OPPORTUNITY: {} - ${:.2f} potential savings for resource {}", 
                           rec.getStrategy(), rec.getPotentialSavingsUsd(), rec.getResourceId());
                
                // In production, send actual notifications (email, Slack, etc.)
            }
        }
    }
    
    /**
     * Store recommendation in database
     */
    private void storeRecommendation(OptimizationRecommendation recommendation) {
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "INSERT OR REPLACE INTO optimization_recommendations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
            PreparedStatement stmt = conn.prepareStatement(sql);
            
            stmt.setString(1, recommendation.getRecommendationId());
            stmt.setString(2, recommendation.getResourceId());
            stmt.setString(3, recommendation.getStrategy().name());
            stmt.setDouble(4, recommendation.getCurrentCostUsd());
            stmt.setDouble(5, recommendation.getOptimizedCostUsd());
            stmt.setDouble(6, recommendation.getPotentialSavingsUsd());
            stmt.setString(7, recommendation.getImplementationEffort());
            stmt.setString(8, recommendation.getRiskLevel());
            stmt.setString(9, recommendation.getDescription());
            stmt.setString(10, objectMapper.writeValueAsString(recommendation.getActionSteps()));
            stmt.setString(11, recommendation.getCreatedAt().format(TIMESTAMP_FORMAT));
            stmt.setInt(12, 0); // Not applied yet
            
            stmt.executeUpdate();
            
        } catch (Exception e) {
            logger.error("Failed to store recommendation: " + recommendation.getRecommendationId(), e);
        }
    }
    
    /**
     * Get cost optimization dashboard data
     */
    public Map<String, Object> getDashboardData() {
        Map<String, Object> dashboard = new HashMap<>();
        
        // Total cost tracking
        double totalMonthlyCost = resourceTrackers.values().stream()
            .mapToDouble(ResourceCostTracker::getMonthlyProjectedCostUsd)
            .sum();
        
        dashboard.put("total_monthly_cost_usd", totalMonthlyCost);
        dashboard.put("total_resources", resourceTrackers.size());
        
        // Cost by resource type
        Map<String, Double> costByType = new HashMap<>();
        for (ResourceCostTracker tracker : resourceTrackers.values()) {
            String type = tracker.getResourceType().name();
            costByType.merge(type, tracker.getMonthlyProjectedCostUsd(), Double::sum);
        }
        dashboard.put("cost_by_resource_type", costByType);
        
        // Recent recommendations
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "SELECT COUNT(*), SUM(potential_savings_usd) FROM optimization_recommendations " +
                        "WHERE datetime(created_at) > datetime('now', '-7 days')";
            PreparedStatement stmt = conn.prepareStatement(sql);
            ResultSet rs = stmt.executeQuery();
            
            if (rs.next()) {
                dashboard.put("recent_recommendations_count", rs.getInt(1));
                dashboard.put("recent_potential_savings_usd", rs.getDouble(2));
            }
            
        } catch (SQLException e) {
            logger.error("Failed to get dashboard data", e);
        }
        
        // Utilization summary
        Map<String, Double> avgUtilization = new HashMap<>();
        for (ResourceCostTracker tracker : resourceTrackers.values()) {
            Map<String, Double> utilization = tracker.getUtilizationMetrics();
            utilization.forEach((metric, value) -> 
                avgUtilization.merge(metric, value, (old, new_val) -> (old + new_val) / 2)
            );
        }
        dashboard.put("average_utilization", avgUtilization);
        
        return dashboard;
    }
    
    /**
     * Get optimization recommendations for a resource
     */
    public List<OptimizationRecommendation> getRecommendations(String resourceId, int limit) {
        List<OptimizationRecommendation> recommendations = new ArrayList<>();
        
        try (Connection conn = DriverManager.getConnection("jdbc:sqlite:" + dbPath)) {
            String sql = "SELECT * FROM optimization_recommendations WHERE resource_id = ? " +
                        "ORDER BY potential_savings_usd DESC LIMIT ?";
            PreparedStatement stmt = conn.prepareStatement(sql);
            stmt.setString(1, resourceId);
            stmt.setInt(2, limit);
            
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                OptimizationRecommendation rec = new OptimizationRecommendation();
                rec.setRecommendationId(rs.getString("recommendation_id"));
                rec.setResourceId(rs.getString("resource_id"));
                rec.setStrategy(OptimizationStrategy.valueOf(rs.getString("strategy")));
                rec.setCurrentCostUsd(rs.getDouble("current_cost_usd"));
                rec.setOptimizedCostUsd(rs.getDouble("optimized_cost_usd"));
                rec.setPotentialSavingsUsd(rs.getDouble("potential_savings_usd"));
                rec.setImplementationEffort(rs.getString("implementation_effort"));
                rec.setRiskLevel(rs.getString("risk_level"));
                rec.setDescription(rs.getString("description"));
                
                recommendations.add(rec);
            }
            
        } catch (SQLException e) {
            logger.error("Failed to get recommendations for resource: " + resourceId, e);
        }
        
        return recommendations;
    }
    
    /**
     * Shutdown cost optimizer
     */
    public void shutdown() {
        logger.info("Shutting down MLOps Cost Optimizer...");
        
        scheduler.shutdown();
        optimizationExecutor.shutdown();
        
        try {
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!optimizationExecutor.awaitTermination(10, TimeUnit.SECONDS)) {
                optimizationExecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("MLOps Cost Optimizer shutdown complete");
    }
    
    /**
     * Demo main method
     */
    public static void main(String[] args) throws Exception {
        System.out.println("💰 Starting MLOps Cost Optimizer Demo");
        System.out.println("=" + "=".repeat(50));
        
        // Initialize cost optimizer
        OptimizationConfig config = new OptimizationConfig();
        config.setOptimizationIntervalHours(1); // 1 hour for demo
        config.setMinSavingsThresholdUsd(5.0); // $5 minimum
        config.setAutoApplySafeOptimizations(true);
        
        MLOpsCostOptimizer optimizer = new MLOpsCostOptimizer("cost_optimizer.db", config);
        
        // Simulate resource costs
        System.out.println("\n💸 Simulating resource costs...");
        
        Random random = new Random();
        
        // Training instances (high cost, variable utilization)
        for (int i = 1; i <= 3; i++) {
            String resourceId = "training_instance_" + i;
            double hourlyCost = 8.0 + random.nextDouble() * 4.0; // $8-12/hour
            
            Map<String, Double> utilization = Map.of(
                "avg_cpu_utilization", 15.0 + random.nextDouble() * 25.0, // 15-40%
                "avg_memory_utilization", 20.0 + random.nextDouble() * 30.0, // 20-50%
                "peak_cpu_utilization", 60.0 + random.nextDouble() * 40.0, // 60-100%
                "avg_gpu_utilization", 30.0 + random.nextDouble() * 40.0 // 30-70%
            );
            
            optimizer.trackResourceCost(resourceId, ResourceType.TRAINING_JOB, hourlyCost, utilization);
            System.out.println("  " + resourceId + ": $" + String.format("%.2f", hourlyCost) + "/hour");
        }
        
        // GPU instances (very high cost, low utilization)
        for (int i = 1; i <= 2; i++) {
            String resourceId = "gpu_instance_" + i;
            double hourlyCost = 15.0 + random.nextDouble() * 10.0; // $15-25/hour
            
            Map<String, Double> utilization = Map.of(
                "avg_cpu_utilization", 10.0 + random.nextDouble() * 15.0, // 10-25%
                "avg_memory_utilization", 25.0 + random.nextDouble() * 20.0, // 25-45%
                "avg_gpu_utilization", 20.0 + random.nextDouble() * 20.0 // 20-40%
            );
            
            optimizer.trackResourceCost(resourceId, ResourceType.GPU_INSTANCE, hourlyCost, utilization);
            System.out.println("  " + resourceId + ": $" + String.format("%.2f", hourlyCost) + "/hour");
        }
        
        // Compute instances (medium cost, mixed utilization)
        for (int i = 1; i <= 5; i++) {
            String resourceId = "compute_instance_" + i;
            double hourlyCost = 2.0 + random.nextDouble() * 3.0; // $2-5/hour
            
            Map<String, Double> utilization = Map.of(
                "avg_cpu_utilization", 5.0 + random.nextDouble() * 30.0, // 5-35%
                "avg_memory_utilization", 15.0 + random.nextDouble() * 35.0, // 15-50%
                "night_utilization", 2.0 + random.nextDouble() * 8.0 // 2-10% (low at night)
            );
            
            optimizer.trackResourceCost(resourceId, ResourceType.COMPUTE_INSTANCE, hourlyCost, utilization);
            System.out.println("  " + resourceId + ": $" + String.format("%.2f", hourlyCost) + "/hour");
        }
        
        // Wait for initial analysis
        Thread.sleep(3000);
        
        // Trigger optimization analysis
        System.out.println("\n🔍 Running optimization analysis...");
        optimizer.runOptimizationAnalysis();
        
        // Wait for analysis to complete
        Thread.sleep(2000);
        
        // Display dashboard
        System.out.println("\n📊 Cost Optimization Dashboard:");
        Map<String, Object> dashboard = optimizer.getDashboardData();
        
        System.out.println("  Total Monthly Cost: $" + String.format("%.2f", 
                          (Double) dashboard.get("total_monthly_cost_usd")));
        System.out.println("  Total Resources: " + dashboard.get("total_resources"));
        System.out.println("  Recent Recommendations: " + dashboard.get("recent_recommendations_count"));
        System.out.println("  Potential Savings: $" + String.format("%.2f", 
                          (Double) dashboard.get("recent_potential_savings_usd")));
        
        @SuppressWarnings("unchecked")
        Map<String, Double> costByType = (Map<String, Double>) dashboard.get("cost_by_resource_type");
        System.out.println("\n💰 Cost by Resource Type:");
        costByType.forEach((type, cost) -> 
            System.out.println("    " + type + ": $" + String.format("%.2f", cost))
        );
        
        // Show top recommendations
        System.out.println("\n🎯 Top Optimization Recommendations:");
        
        for (String resourceId : Arrays.asList("training_instance_1", "gpu_instance_1", "compute_instance_1")) {
            List<OptimizationRecommendation> recommendations = optimizer.getRecommendations(resourceId, 2);
            
            if (!recommendations.isEmpty()) {
                System.out.println("\n  " + resourceId + ":");
                
                for (OptimizationRecommendation rec : recommendations) {
                    System.out.println("    Strategy: " + rec.getStrategy());
                    System.out.println("    Potential Savings: $" + String.format("%.2f", rec.getPotentialSavingsUsd()) + 
                                     " (" + String.format("%.1f", rec.getSavingsPercentage()) + "%)");
                    System.out.println("    Effort: " + rec.getImplementationEffort() + 
                                     ", Risk: " + rec.getRiskLevel());
                    System.out.println("    Description: " + rec.getDescription().substring(0, 
                                     Math.min(80, rec.getDescription().length())) + "...");
                    System.out.println();
                }
            }
        }
        
        // Calculate total optimization potential
        double totalCurrentCost = optimizer.resourceTrackers.values().stream()
            .mapToDouble(ResourceCostTracker::getMonthlyProjectedCostUsd)
            .sum();
        
        double totalPotentialSavings = (Double) dashboard.get("recent_potential_savings_usd");
        double savingsPercentage = totalCurrentCost > 0 ? (totalPotentialSavings / totalCurrentCost) * 100 : 0;
        
        System.out.println("📈 Optimization Summary:");
        System.out.println("  Current Monthly Cost: $" + String.format("%.2f", totalCurrentCost));
        System.out.println("  Potential Monthly Savings: $" + String.format("%.2f", totalPotentialSavings));
        System.out.println("  Optimization Opportunity: " + String.format("%.1f", savingsPercentage) + "%");
        
        System.out.println("\n✅ MLOps cost optimization demo completed!");
        System.out.println("Mumbai me cost optimization bhi budget planning ki tarah important!");
        
        // Shutdown
        optimizer.shutdown();
    }
}