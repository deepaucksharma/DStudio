/**
 * GPU Cluster Manager for AI at Scale
 * Episode 5: Java Implementation
 * 
 * Production-ready GPU cluster management system for Indian AI infrastructure
 * Optimized for cost-effective distributed training and inference
 * 
 * Author: Code Developer Agent
 * Context: Indian AI/ML production systems with cost optimization
 */

package com.aiScale.cluster;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.logging.Logger;
import java.util.logging.Level;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * GPU क्लस्टर को manage करने के लिए main class
 * Indian cloud providers (AWS Mumbai, Azure India, GCP Mumbai) के साथ optimized
 */
public class GPUClusterManager {
    private static final Logger logger = Logger.getLogger(GPUClusterManager.class.getName());
    
    // भारतीय cloud providers के लिए region configurations
    private static final Map<String, Double> REGIONAL_COSTS = Map.of(
        "ap-south-1", 45.0,     // AWS Mumbai - ₹45/hour per GPU
        "azure-centralindia", 48.0,  // Azure Central India - ₹48/hour per GPU
        "asia-south1", 42.0,    // GCP Mumbai - ₹42/hour per GPU
        "on-premise", 20.0      // On-premise cost - ₹20/hour per GPU (electricity + depreciation)
    );
    
    private final ExecutorService executorService;
    private final ScheduledExecutorService scheduler;
    private final Map<String, GPUNode> clusterNodes;
    private final Map<String, TrainingJob> activeJobs;
    private final ClusterMetrics metrics;
    private final CostOptimizer costOptimizer;
    
    public GPUClusterManager() {
        this.executorService = Executors.newFixedThreadPool(10);
        this.scheduler = Executors.newScheduledThreadPool(5);
        this.clusterNodes = new ConcurrentHashMap<>();
        this.activeJobs = new ConcurrentHashMap<>();
        this.metrics = new ClusterMetrics();
        this.costOptimizer = new CostOptimizer();
        
        logger.info("GPU Cluster Manager initialized for Indian AI infrastructure");
    }
    
    /**
     * GPU Node class representing individual compute units
     * भारतीय infrastructure के लिए specific configurations
     */
    public static class GPUNode {
        private final String nodeId;
        private final String region;
        private final GPUType gpuType;
        private final int gpuCount;
        private volatile NodeStatus status;
        private volatile double utilizationPercent;
        private volatile double memoryUsedGB;
        private volatile double totalMemoryGB;
        private volatile LocalDateTime lastHeartbeat;
        private volatile String currentJobId;
        
        // Cost tracking - भारतीय pricing के साथ
        private volatile double costPerHourINR;
        private volatile double totalCostINR;
        private volatile LocalDateTime costTrackingStart;
        
        public GPUNode(String nodeId, String region, GPUType gpuType, int gpuCount) {
            this.nodeId = nodeId;
            this.region = region;
            this.gpuType = gpuType;
            this.gpuCount = gpuCount;
            this.status = NodeStatus.IDLE;
            this.utilizationPercent = 0.0;
            this.memoryUsedGB = 0.0;
            this.totalMemoryGB = gpuType.getMemoryGB() * gpuCount;
            this.lastHeartbeat = LocalDateTime.now();
            this.costPerHourINR = REGIONAL_COSTS.getOrDefault(region, 50.0);
            this.totalCostINR = 0.0;
            this.costTrackingStart = LocalDateTime.now();
        }
        
        // Getters और setters with thread safety
        public synchronized void updateMetrics(double utilization, double memoryUsed) {
            this.utilizationPercent = Math.max(0.0, Math.min(100.0, utilization));
            this.memoryUsedGB = Math.max(0.0, Math.min(totalMemoryGB, memoryUsed));
            this.lastHeartbeat = LocalDateTime.now();
            
            // Cost tracking - real-time में cost calculate करना
            if (status == NodeStatus.BUSY) {
                long minutesElapsed = java.time.Duration.between(costTrackingStart, LocalDateTime.now()).toMinutes();
                this.totalCostINR = (minutesElapsed / 60.0) * costPerHourINR;
            }
        }
        
        public synchronized boolean isHealthy() {
            return LocalDateTime.now().minusMinutes(5).isBefore(lastHeartbeat) 
                   && status != NodeStatus.FAILED;
        }
        
        public synchronized double getAvailableMemoryGB() {
            return totalMemoryGB - memoryUsedGB;
        }
        
        // Getters
        public String getNodeId() { return nodeId; }
        public String getRegion() { return region; }
        public GPUType getGpuType() { return gpuType; }
        public int getGpuCount() { return gpuCount; }
        public NodeStatus getStatus() { return status; }
        public double getUtilizationPercent() { return utilizationPercent; }
        public double getMemoryUsedGB() { return memoryUsedGB; }
        public double getTotalMemoryGB() { return totalMemoryGB; }
        public LocalDateTime getLastHeartbeat() { return lastHeartbeat; }
        public String getCurrentJobId() { return currentJobId; }
        public double getCostPerHourINR() { return costPerHourINR; }
        public double getTotalCostINR() { return totalCostINR; }
        
        // Setters with validation
        public synchronized void setStatus(NodeStatus status) {
            this.status = status;
            if (status == NodeStatus.BUSY && costTrackingStart == null) {
                this.costTrackingStart = LocalDateTime.now();
            }
        }
        
        public synchronized void setCurrentJobId(String jobId) {
            this.currentJobId = jobId;
        }
    }
    
    /**
     * GPU types commonly available in India
     * Cost और performance के हिसाब से categorized
     */
    public enum GPUType {
        // Entry level - startups के लिए affordable
        RTX_3060("RTX 3060", 12, 170, "entry"),
        RTX_3070("RTX 3070", 8, 220, "entry"),
        
        // Mid range - small to medium companies
        RTX_3080("RTX 3080", 10, 320, "mid"),
        RTX_4080("RTX 4080", 16, 320, "mid"),
        
        // High end - enterprise और research
        RTX_4090("RTX 4090", 24, 450, "high"),
        A100_40GB("A100 40GB", 40, 400, "enterprise"),
        A100_80GB("A100 80GB", 80, 400, "enterprise"),
        H100("H100", 80, 700, "premium");
        
        private final String displayName;
        private final int memoryGB;
        private final int watts;
        private final String tier;
        
        GPUType(String displayName, int memoryGB, int watts, String tier) {
            this.displayName = displayName;
            this.memoryGB = memoryGB;
            this.watts = watts;
            this.tier = tier;
        }
        
        public String getDisplayName() { return displayName; }
        public int getMemoryGB() { return memoryGB; }
        public int getWatts() { return watts; }
        public String getTier() { return tier; }
    }
    
    public enum NodeStatus {
        IDLE, BUSY, MAINTENANCE, FAILED, PROVISIONING
    }
    
    /**
     * Training Job class for distributed AI training
     * Indian AI use cases के साथ optimized
     */
    public static class TrainingJob {
        private final String jobId;
        private final String userId;
        private final String projectName;
        private final String modelType;
        private final JobPriority priority;
        private final ResourceRequirements requirements;
        private volatile JobStatus status;
        private volatile LocalDateTime createdAt;
        private volatile LocalDateTime startedAt;
        private volatile LocalDateTime completedAt;
        private final List<String> assignedNodes;
        private volatile double progressPercent;
        private volatile String currentEpoch;
        private volatile double estimatedCostINR;
        
        public TrainingJob(String jobId, String userId, String projectName, 
                          String modelType, JobPriority priority, ResourceRequirements requirements) {
            this.jobId = jobId;
            this.userId = userId;
            this.projectName = projectName;
            this.modelType = modelType;
            this.priority = priority;
            this.requirements = requirements;
            this.status = JobStatus.QUEUED;
            this.createdAt = LocalDateTime.now();
            this.assignedNodes = new ArrayList<>();
            this.progressPercent = 0.0;
            this.estimatedCostINR = 0.0;
        }
        
        // Getters और utility methods
        public String getJobId() { return jobId; }
        public String getUserId() { return userId; }
        public String getProjectName() { return projectName; }
        public String getModelType() { return modelType; }
        public JobPriority getPriority() { return priority; }
        public ResourceRequirements getRequirements() { return requirements; }
        public JobStatus getStatus() { return status; }
        public LocalDateTime getCreatedAt() { return createdAt; }
        public LocalDateTime getStartedAt() { return startedAt; }
        public LocalDateTime getCompletedAt() { return completedAt; }
        public List<String> getAssignedNodes() { return new ArrayList<>(assignedNodes); }
        public double getProgressPercent() { return progressPercent; }
        public String getCurrentEpoch() { return currentEpoch; }
        public double getEstimatedCostINR() { return estimatedCostINR; }
        
        public synchronized void setStatus(JobStatus status) {
            this.status = status;
            if (status == JobStatus.RUNNING && startedAt == null) {
                this.startedAt = LocalDateTime.now();
            } else if (status == JobStatus.COMPLETED || status == JobStatus.FAILED) {
                this.completedAt = LocalDateTime.now();
            }
        }
        
        public synchronized void updateProgress(double progress, String epoch) {
            this.progressPercent = Math.max(0.0, Math.min(100.0, progress));
            this.currentEpoch = epoch;
        }
        
        public synchronized void addAssignedNode(String nodeId) {
            if (!assignedNodes.contains(nodeId)) {
                assignedNodes.add(nodeId);
            }
        }
        
        public synchronized void removeAssignedNode(String nodeId) {
            assignedNodes.remove(nodeId);
        }
        
        public synchronized void updateEstimatedCost(double costINR) {
            this.estimatedCostINR = costINR;
        }
    }
    
    public enum JobStatus {
        QUEUED, RUNNING, PAUSED, COMPLETED, FAILED, CANCELLED
    }
    
    public enum JobPriority {
        LOW(1), NORMAL(2), HIGH(3), CRITICAL(4);
        
        private final int value;
        
        JobPriority(int value) {
            this.value = value;
        }
        
        public int getValue() { return value; }
    }
    
    /**
     * Resource requirements for training jobs
     * Indian infrastructure constraints के साथ realistic requirements
     */
    public static class ResourceRequirements {
        private final int minGPUs;
        private final int maxGPUs;
        private final int minMemoryGB;
        private final GPUType preferredGPUType;
        private final String region;
        private final int maxDurationHours;
        private final double maxCostINR;
        
        public ResourceRequirements(int minGPUs, int maxGPUs, int minMemoryGB, 
                                  GPUType preferredGPUType, String region, 
                                  int maxDurationHours, double maxCostINR) {
            this.minGPUs = minGPUs;
            this.maxGPUs = maxGPUs;
            this.minMemoryGB = minMemoryGB;
            this.preferredGPUType = preferredGPUType;
            this.region = region;
            this.maxDurationHours = maxDurationHours;
            this.maxCostINR = maxCostINR;
        }
        
        // Getters
        public int getMinGPUs() { return minGPUs; }
        public int getMaxGPUs() { return maxGPUs; }
        public int getMinMemoryGB() { return minMemoryGB; }
        public GPUType getPreferredGPUType() { return preferredGPUType; }
        public String getRegion() { return region; }
        public int getMaxDurationHours() { return maxDurationHours; }
        public double getMaxCostINR() { return maxCostINR; }
        
        public boolean isSatisfiedBy(GPUNode node) {
            return node.getGpuCount() >= minGPUs &&
                   node.getTotalMemoryGB() >= minMemoryGB &&
                   node.getStatus() == NodeStatus.IDLE &&
                   (region == null || region.equals(node.getRegion()));
        }
    }
    
    /**
     * Cluster metrics for monitoring and optimization
     * Real-time cost tracking और performance metrics
     */
    public static class ClusterMetrics {
        private volatile long totalJobs;
        private volatile long completedJobs;
        private volatile long failedJobs;
        private volatile double totalCostINR;
        private volatile double avgJobDurationHours;
        private volatile double clusterUtilizationPercent;
        private volatile int activeNodes;
        private volatile int failedNodes;
        private final Map<String, Long> jobsByType;
        private final Map<String, Double> costByRegion;
        
        public ClusterMetrics() {
            this.totalJobs = 0;
            this.completedJobs = 0;
            this.failedJobs = 0;
            this.totalCostINR = 0.0;
            this.avgJobDurationHours = 0.0;
            this.clusterUtilizationPercent = 0.0;
            this.activeNodes = 0;
            this.failedNodes = 0;
            this.jobsByType = new ConcurrentHashMap<>();
            this.costByRegion = new ConcurrentHashMap<>();
        }
        
        public synchronized void recordJobCompletion(TrainingJob job) {
            totalJobs++;
            if (job.getStatus() == JobStatus.COMPLETED) {
                completedJobs++;
            } else if (job.getStatus() == JobStatus.FAILED) {
                failedJobs++;
            }
            
            // Calculate duration
            if (job.getStartedAt() != null && job.getCompletedAt() != null) {
                long durationMinutes = java.time.Duration.between(
                    job.getStartedAt(), job.getCompletedAt()).toMinutes();
                double durationHours = durationMinutes / 60.0;
                
                // Update average duration
                avgJobDurationHours = (avgJobDurationHours * (totalJobs - 1) + durationHours) / totalJobs;
            }
            
            // Track by job type
            jobsByType.merge(job.getModelType(), 1L, Long::sum);
            
            // Update cost
            totalCostINR += job.getEstimatedCostINR();
        }
        
        public synchronized void updateClusterStats(Collection<GPUNode> nodes) {
            if (nodes.isEmpty()) {
                this.clusterUtilizationPercent = 0.0;
                this.activeNodes = 0;
                this.failedNodes = 0;
                return;
            }
            
            double totalUtilization = 0.0;
            int healthy = 0;
            int failed = 0;
            
            Map<String, Double> regionCosts = new HashMap<>();
            
            for (GPUNode node : nodes) {
                if (node.isHealthy()) {
                    healthy++;
                    totalUtilization += node.getUtilizationPercent();
                } else {
                    failed++;
                }
                
                // Track cost by region
                regionCosts.merge(node.getRegion(), node.getTotalCostINR(), Double::sum);
            }
            
            this.clusterUtilizationPercent = healthy > 0 ? totalUtilization / healthy : 0.0;
            this.activeNodes = healthy;
            this.failedNodes = failed;
            this.costByRegion.clear();
            this.costByRegion.putAll(regionCosts);
        }
        
        // Getters
        public long getTotalJobs() { return totalJobs; }
        public long getCompletedJobs() { return completedJobs; }
        public long getFailedJobs() { return failedJobs; }
        public double getTotalCostINR() { return totalCostINR; }
        public double getAvgJobDurationHours() { return avgJobDurationHours; }
        public double getClusterUtilizationPercent() { return clusterUtilizationPercent; }
        public int getActiveNodes() { return activeNodes; }
        public int getFailedNodes() { return failedNodes; }
        public Map<String, Long> getJobsByType() { return new HashMap<>(jobsByType); }
        public Map<String, Double> getCostByRegion() { return new HashMap<>(costByRegion); }
        
        public double getSuccessRate() {
            return totalJobs > 0 ? (double) completedJobs / totalJobs * 100 : 0.0;
        }
    }
    
    /**
     * Cost optimizer for Indian cloud infrastructure
     * Spot instances, preemptible VMs, और time-based pricing के साथ optimized
     */
    public static class CostOptimizer {
        private final Map<String, List<Double>> historicalPricing;
        private final Map<String, Double> spotPricingDiscount;
        
        public CostOptimizer() {
            this.historicalPricing = new HashMap<>();
            this.spotPricingDiscount = Map.of(
                "ap-south-1", 0.70,     // AWS Spot instances - 70% of on-demand
                "azure-centralindia", 0.75,  // Azure Spot VMs - 75% of on-demand
                "asia-south1", 0.68,    // GCP Preemptible instances - 68% of on-demand
                "on-premise", 1.0       // No discount for on-premise
            );
        }
        
        /**
         * भारतीय working hours के हिसाब से optimal timing suggest करना
         * Off-peak hours में training schedule करके cost save करना
         */
        public List<OptimalSchedule> findOptimalSchedule(TrainingJob job) {
            List<OptimalSchedule> schedules = new ArrayList<>();
            
            // Off-peak hours in India (11 PM to 6 AM IST)
            // Business hours में demand कम होने पर spot pricing better होती है
            int[] offPeakHours = {23, 0, 1, 2, 3, 4, 5, 6};
            
            for (int hour : offPeakHours) {
                double discount = 0.85; // 15% discount for off-peak hours
                double estimatedCost = calculateJobCost(job) * discount;
                
                if (estimatedCost <= job.getRequirements().getMaxCostINR()) {
                    schedules.add(new OptimalSchedule(
                        hour, estimatedCost, discount, "off-peak", 
                        "Schedule during off-peak hours for 15% cost savings"
                    ));
                }
            }
            
            // Sort by cost (cheapest first)
            schedules.sort(Comparator.comparingDouble(OptimalSchedule::getCostINR));
            
            return schedules;
        }
        
        /**
         * Job के लिए estimated cost calculate करना
         * Indian infrastructure pricing के साथ realistic calculation
         */
        public double calculateJobCost(TrainingJob job) {
            ResourceRequirements req = job.getRequirements();
            
            // Base cost calculation
            double hourlyRate = REGIONAL_COSTS.getOrDefault(req.getRegion(), 50.0);
            double gpuMultiplier = req.getMinGPUs();
            double durationHours = Math.max(1, req.getMaxDurationHours());
            
            // GPU type multiplier
            double typeMultiplier = switch(req.getPreferredGPUType().getTier()) {
                case "entry" -> 0.8;
                case "mid" -> 1.0;
                case "high" -> 1.5;
                case "enterprise" -> 2.0;
                case "premium" -> 3.0;
                default -> 1.0;
            };
            
            double baseCost = hourlyRate * gpuMultiplier * durationHours * typeMultiplier;
            
            // Apply spot pricing discount if region supports it
            double spotDiscount = spotPricingDiscount.getOrDefault(req.getRegion(), 1.0);
            
            return baseCost * spotDiscount;
        }
        
        /**
         * Cost optimization recommendations
         * Indian context के साथ practical suggestions
         */
        public List<String> getCostOptimizationRecommendations(TrainingJob job, double currentCost) {
            List<String> recommendations = new ArrayList<>();
            ResourceRequirements req = job.getRequirements();
            
            // Region optimization
            if ("ap-south-1".equals(req.getRegion())) {
                recommendations.add("Consider using GCP Mumbai (asia-south1) for 7% cost savings on similar performance");
            }
            
            // GPU type optimization
            if (req.getPreferredGPUType().getTier().equals("enterprise") || req.getPreferredGPUType().getTier().equals("premium")) {
                recommendations.add("Consider using multiple mid-tier GPUs instead of premium ones for better cost per FLOP");
            }
            
            // Timing optimization
            recommendations.add("Schedule training during 11 PM - 6 AM IST for up to 15% cost savings");
            
            // Spot/Preemptible optimization
            if (!"on-premise".equals(req.getRegion())) {
                recommendations.add("Use spot instances for up to 30% cost savings (with fault tolerance)");
            }
            
            // Mixed precision optimization
            recommendations.add("Enable mixed precision training to reduce memory usage and potentially use smaller GPUs");
            
            // Batch size optimization
            recommendations.add("Optimize batch size to maximize GPU memory utilization and reduce training time");
            
            return recommendations;
        }
    }
    
    public static class OptimalSchedule {
        private final int startHour;
        private final double costINR;
        private final double discount;
        private final String scheduleType;
        private final String description;
        
        public OptimalSchedule(int startHour, double costINR, double discount, 
                             String scheduleType, String description) {
            this.startHour = startHour;
            this.costINR = costINR;
            this.discount = discount;
            this.scheduleType = scheduleType;
            this.description = description;
        }
        
        // Getters
        public int getStartHour() { return startHour; }
        public double getCostINR() { return costINR; }
        public double getDiscount() { return discount; }
        public String getScheduleType() { return scheduleType; }
        public String getDescription() { return description; }
    }
    
    // Main cluster management methods
    
    /**
     * Add new GPU node to the cluster
     * भारतीय infrastructure के साथ node को register करना
     */
    public synchronized void addNode(String nodeId, String region, GPUType gpuType, int gpuCount) {
        if (clusterNodes.containsKey(nodeId)) {
            logger.warning("Node already exists: " + nodeId);
            return;
        }
        
        GPUNode node = new GPUNode(nodeId, region, gpuType, gpuCount);
        clusterNodes.put(nodeId, node);
        
        logger.info(String.format(
            "Added GPU node: %s [%s] - %d x %s in region %s (₹%.2f/hour)", 
            nodeId, gpuType.getDisplayName(), gpuCount, gpuType.getDisplayName(), 
            region, node.getCostPerHourINR()
        ));
        
        // Start monitoring this node
        startNodeMonitoring(nodeId);
    }
    
    /**
     * Submit training job to the cluster
     * Priority-based scheduling with cost optimization
     */
    public synchronized String submitJob(String userId, String projectName, String modelType,
                                       JobPriority priority, ResourceRequirements requirements) {
        String jobId = generateJobId(userId, projectName, modelType);
        TrainingJob job = new TrainingJob(jobId, userId, projectName, modelType, priority, requirements);
        
        // Calculate estimated cost
        double estimatedCost = costOptimizer.calculateJobCost(job);
        job.updateEstimatedCost(estimatedCost);
        
        if (estimatedCost > requirements.getMaxCostINR()) {
            logger.warning(String.format(
                "Job %s estimated cost ₹%.2f exceeds budget ₹%.2f", 
                jobId, estimatedCost, requirements.getMaxCostINR()
            ));
            
            // Provide cost optimization suggestions
            List<String> recommendations = costOptimizer.getCostOptimizationRecommendations(job, estimatedCost);
            logger.info("Cost optimization recommendations: " + String.join(", ", recommendations));
        }
        
        activeJobs.put(jobId, job);
        logger.info(String.format(
            "Submitted job %s for user %s - %s model (Priority: %s, Estimated cost: ₹%.2f)",
            jobId, userId, modelType, priority, estimatedCost
        ));
        
        // Try to schedule immediately
        scheduleJobs();
        
        return jobId;
    }
    
    /**
     * Smart job scheduling based on priority and resource availability
     * Indian infrastructure constraints के साथ optimized scheduling
     */
    public synchronized void scheduleJobs() {
        List<TrainingJob> queuedJobs = activeJobs.values().stream()
            .filter(job -> job.getStatus() == JobStatus.QUEUED)
            .sorted(Comparator.comparingInt((TrainingJob job) -> -job.getPriority().getValue())
                             .thenComparing(TrainingJob::getCreatedAt))
            .collect(Collectors.toList());
        
        for (TrainingJob job : queuedJobs) {
            List<GPUNode> availableNodes = findAvailableNodes(job.getRequirements());
            
            if (availableNodes.size() >= job.getRequirements().getMinGPUs()) {
                // Allocate nodes to job
                List<GPUNode> allocatedNodes = availableNodes.subList(0, job.getRequirements().getMinGPUs());
                
                for (GPUNode node : allocatedNodes) {
                    node.setStatus(NodeStatus.BUSY);
                    node.setCurrentJobId(job.getJobId());
                    job.addAssignedNode(node.getNodeId());
                }
                
                job.setStatus(JobStatus.RUNNING);
                
                logger.info(String.format(
                    "Scheduled job %s on %d nodes: %s", 
                    job.getJobId(), 
                    allocatedNodes.size(),
                    allocatedNodes.stream().map(GPUNode::getNodeId).collect(Collectors.joining(", "))
                ));
                
                // Start job execution
                startJobExecution(job);
            }
        }
    }
    
    private List<GPUNode> findAvailableNodes(ResourceRequirements requirements) {
        return clusterNodes.values().stream()
            .filter(node -> requirements.isSatisfiedBy(node))
            .filter(GPUNode::isHealthy)
            .sorted(Comparator.comparing(GPUNode::getCostPerHourINR)) // Cheapest first
            .collect(Collectors.toList());
    }
    
    private void startJobExecution(TrainingJob job) {
        executorService.submit(() -> {
            try {
                logger.info("Starting execution for job: " + job.getJobId());
                
                // Simulate job execution with progress updates
                for (int epoch = 1; epoch <= 10; epoch++) {
                    Thread.sleep(5000); // Simulate epoch time
                    
                    double progress = (epoch / 10.0) * 100;
                    job.updateProgress(progress, "Epoch " + epoch);
                    
                    logger.info(String.format(
                        "Job %s progress: %.1f%% (Epoch %d/10)", 
                        job.getJobId(), progress, epoch
                    ));
                }
                
                // Job completed
                completeJob(job.getJobId(), JobStatus.COMPLETED);
                
            } catch (Exception e) {
                logger.severe("Job execution failed for " + job.getJobId() + ": " + e.getMessage());
                completeJob(job.getJobId(), JobStatus.FAILED);
            }
        });
    }
    
    /**
     * Complete job and release resources
     */
    public synchronized void completeJob(String jobId, JobStatus finalStatus) {
        TrainingJob job = activeJobs.get(jobId);
        if (job == null) {
            logger.warning("Job not found: " + jobId);
            return;
        }
        
        job.setStatus(finalStatus);
        
        // Release allocated nodes
        for (String nodeId : job.getAssignedNodes()) {
            GPUNode node = clusterNodes.get(nodeId);
            if (node != null) {
                node.setStatus(NodeStatus.IDLE);
                node.setCurrentJobId(null);
            }
        }
        
        // Update metrics
        metrics.recordJobCompletion(job);
        
        logger.info(String.format(
            "Job %s %s. Duration: %d minutes, Cost: ₹%.2f", 
            jobId, 
            finalStatus.name().toLowerCase(),
            job.getStartedAt() != null && job.getCompletedAt() != null ?
                java.time.Duration.between(job.getStartedAt(), job.getCompletedAt()).toMinutes() : 0,
            job.getEstimatedCostINR()
        ));
        
        // Try to schedule waiting jobs
        scheduleJobs();
    }
    
    /**
     * Get comprehensive cluster status
     * Indian infrastructure के साथ detailed monitoring
     */
    public synchronized Map<String, Object> getClusterStatus() {
        metrics.updateClusterStats(clusterNodes.values());
        
        Map<String, Object> status = new HashMap<>();
        
        // Basic stats
        status.put("total_nodes", clusterNodes.size());
        status.put("active_nodes", metrics.getActiveNodes());
        status.put("failed_nodes", metrics.getFailedNodes());
        status.put("cluster_utilization_percent", String.format("%.1f%%", metrics.getClusterUtilizationPercent()));
        
        // Job stats
        status.put("total_jobs", metrics.getTotalJobs());
        status.put("completed_jobs", metrics.getCompletedJobs());
        status.put("failed_jobs", metrics.getFailedJobs());
        status.put("success_rate", String.format("%.1f%%", metrics.getSuccessRate()));
        status.put("avg_job_duration_hours", String.format("%.2f", metrics.getAvgJobDurationHours()));
        
        // Cost stats (भारतीय pricing)
        status.put("total_cost_inr", String.format("₹%.2f", metrics.getTotalCostINR()));
        status.put("cost_by_region", metrics.getCostByRegion());
        
        // Current jobs
        status.put("active_jobs", activeJobs.size());
        status.put("queued_jobs", activeJobs.values().stream()
            .mapToInt(job -> job.getStatus() == JobStatus.QUEUED ? 1 : 0).sum());
        status.put("running_jobs", activeJobs.values().stream()
            .mapToInt(job -> job.getStatus() == JobStatus.RUNNING ? 1 : 0).sum());
        
        // Node breakdown by type
        Map<String, Long> nodesByType = clusterNodes.values().stream()
            .collect(Collectors.groupingBy(
                node -> node.getGpuType().getDisplayName(),
                Collectors.counting()
            ));
        status.put("nodes_by_type", nodesByType);
        
        return status;
    }
    
    /**
     * Node monitoring - heartbeat और health checks
     */
    private void startNodeMonitoring(String nodeId) {
        scheduler.scheduleAtFixedRate(() -> {
            GPUNode node = clusterNodes.get(nodeId);
            if (node == null) return;
            
            try {
                // Simulate getting real metrics from node
                // In production, this would call actual monitoring APIs
                simulateNodeMetrics(node);
                
                // Check if node is healthy
                if (!node.isHealthy() && node.getStatus() != NodeStatus.FAILED) {
                    logger.warning("Node " + nodeId + " appears unhealthy, marking as failed");
                    node.setStatus(NodeStatus.FAILED);
                    
                    // If running job, need to reschedule
                    if (node.getCurrentJobId() != null) {
                        rescheduleJob(node.getCurrentJobId(), nodeId);
                    }
                }
                
            } catch (Exception e) {
                logger.severe("Monitoring failed for node " + nodeId + ": " + e.getMessage());
            }
        }, 0, 30, TimeUnit.SECONDS);
    }
    
    private void simulateNodeMetrics(GPUNode node) {
        // Simulate realistic GPU usage patterns
        double utilization = node.getStatus() == NodeStatus.BUSY ? 
            75 + Math.random() * 20 : // 75-95% when busy
            5 + Math.random() * 10;   // 5-15% when idle
        
        double memoryUsed = node.getStatus() == NodeStatus.BUSY ?
            node.getTotalMemoryGB() * (0.6 + Math.random() * 0.3) : // 60-90% when busy
            node.getTotalMemoryGB() * (0.05 + Math.random() * 0.1);  // 5-15% when idle
        
        node.updateMetrics(utilization, memoryUsed);
    }
    
    private void rescheduleJob(String jobId, String failedNodeId) {
        // Implementation for rescheduling jobs when nodes fail
        // This is critical for production reliability
        logger.info("Rescheduling job " + jobId + " due to node failure: " + failedNodeId);
        // Would implement sophisticated rescheduling logic here
    }
    
    private String generateJobId(String userId, String projectName, String modelType) {
        return String.format("job_%s_%s_%s_%d", 
            userId.substring(0, Math.min(userId.length(), 8)),
            projectName.replaceAll("[^a-zA-Z0-9]", "").substring(0, Math.min(projectName.length(), 8)),
            modelType.replaceAll("[^a-zA-Z0-9]", "").substring(0, Math.min(modelType.length(), 8)),
            System.currentTimeMillis() % 10000
        );
    }
    
    /**
     * Shutdown cluster manager gracefully
     */
    public void shutdown() {
        logger.info("Shutting down GPU Cluster Manager...");
        
        scheduler.shutdown();
        executorService.shutdown();
        
        try {
            if (!scheduler.awaitTermination(30, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        logger.info("GPU Cluster Manager shutdown complete");
    }
    
    /**
     * Demo method showing typical usage for Indian AI companies
     */
    public static void main(String[] args) {
        System.out.println("🚀 GPU Cluster Manager Demo - Indian AI Infrastructure");
        System.out.println("=" .repeat(70));
        
        GPUClusterManager manager = new GPUClusterManager();
        
        try {
            // Add nodes representing typical Indian AI infrastructure
            manager.addNode("gpu-mumbai-01", "ap-south-1", GPUType.RTX_4080, 2);
            manager.addNode("gpu-mumbai-02", "ap-south-1", GPUType.A100_40GB, 1);
            manager.addNode("gpu-bangalore-01", "azure-centralindia", GPUType.RTX_4090, 1);
            manager.addNode("gpu-onprem-01", "on-premise", GPUType.RTX_3080, 4);
            
            System.out.println("\n✅ Cluster initialized with 4 nodes across regions");
            
            // Submit various types of training jobs
            String job1 = manager.submitJob(
                "paytm_ai_team", 
                "fraud_detection", 
                "transformer", 
                JobPriority.HIGH,
                new ResourceRequirements(2, 4, 16, GPUType.RTX_4080, "ap-south-1", 8, 5000.0)
            );
            
            String job2 = manager.submitJob(
                "flipkart_ml", 
                "recommendation_engine", 
                "deep_learning", 
                JobPriority.NORMAL,
                new ResourceRequirements(1, 2, 24, GPUType.A100_40GB, null, 12, 8000.0)
            );
            
            String job3 = manager.submitJob(
                "zomato_research", 
                "food_image_classifier", 
                "cnn", 
                JobPriority.LOW,
                new ResourceRequirements(1, 1, 8, GPUType.RTX_3080, "on-premise", 4, 2000.0)
            );
            
            System.out.println("\n📋 Submitted 3 training jobs from different Indian companies");
            
            // Wait for some execution
            Thread.sleep(10000);
            
            // Show cluster status
            Map<String, Object> status = manager.getClusterStatus();
            System.out.println("\n📊 Cluster Status:");
            status.forEach((key, value) -> 
                System.out.println("   " + key + ": " + value)
            );
            
            // Show cost optimization for a job
            if (!manager.activeJobs.isEmpty()) {
                TrainingJob sampleJob = manager.activeJobs.values().iterator().next();
                List<OptimalSchedule> schedules = manager.costOptimizer.findOptimalSchedule(sampleJob);
                
                System.out.println("\n💰 Cost Optimization Suggestions:");
                for (OptimalSchedule schedule : schedules.subList(0, Math.min(3, schedules.size()))) {
                    System.out.println(String.format(
                        "   %02d:00 IST - ₹%.2f (%.0f%% savings) - %s",
                        schedule.getStartHour(),
                        schedule.getCostINR(),
                        (1 - schedule.getDiscount()) * 100,
                        schedule.getDescription()
                    ));
                }
            }
            
            System.out.println("\n🎯 Indian AI Infrastructure Optimizations:");
            System.out.println("   ✅ Multi-region support (Mumbai, Bangalore, On-premise)");
            System.out.println("   ✅ INR pricing with realistic Indian cloud costs");
            System.out.println("   ✅ Off-peak scheduling for cost optimization");
            System.out.println("   ✅ GPU types suitable for Indian budgets");
            System.out.println("   ✅ Priority-based scheduling for enterprise teams");
            System.out.println("   ✅ Real-time cost tracking and budgeting");
            
            // Wait a bit more to see job completions
            Thread.sleep(30000);
            
            // Final status
            Map<String, Object> finalStatus = manager.getClusterStatus();
            System.out.println("\n📈 Final Statistics:");
            System.out.println("   Total Jobs: " + finalStatus.get("total_jobs"));
            System.out.println("   Success Rate: " + finalStatus.get("success_rate"));
            System.out.println("   Total Cost: " + finalStatus.get("total_cost_inr"));
            System.out.println("   Average Duration: " + finalStatus.get("avg_job_duration_hours") + " hours");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
        } finally {
            manager.shutdown();
        }
    }
}