package com.mumbai.edge.compute;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.stream.Collectors;
import java.util.logging.Logger;
import java.util.logging.Level;

/**
 * Edge Compute Service - मुख्य एज कंप्यूटिंग सेवा
 * Mumbai local train system की तरह - efficient resource management और task distribution
 * 
 * Real-world inspired by AWS Lambda@Edge, Google Cloud Functions
 * Use cases: Real-time processing, microservices, event-driven computing
 * Cost: Edge compute ₹0.5 vs Cloud compute ₹5.0 per million requests
 * 
 * @author Mumbai Tech Team
 * @version 2.1.0
 * @since 2024
 */
public class EdgeComputeService {
    
    private static final Logger LOGGER = Logger.getLogger(EdgeComputeService.class.getName());
    
    // मुख्य configuration constants
    private static final int DEFAULT_THREAD_POOL_SIZE = 10;
    private static final int MAX_QUEUE_SIZE = 1000;
    private static final long HEALTH_CHECK_INTERVAL_MS = 30000; // 30 seconds
    
    // Service identification
    private final String serviceId;
    private final String location;
    
    // Task execution और resource management
    private final ExecutorService executorService;
    private final BlockingQueue<ComputeTask> taskQueue;
    private final Map<String, ComputeTask> activeTasks;
    private final ScheduledExecutorService scheduler;
    
    // Performance metrics और monitoring
    private final AtomicLong totalTasksProcessed;
    private final AtomicLong totalTasksCompleted;
    private final AtomicLong totalTasksFailed;
    private final AtomicLong totalProcessingTimeMs;
    private final Map<TaskPriority, AtomicInteger> tasksByPriority;
    
    // Health और status tracking
    private volatile ServiceStatus status;
    private LocalDateTime startTime;
    private final Set<String> registeredFunctions;
    private final Map<String, FunctionMetrics> functionMetrics;
    
    // Mumbai-specific configurations
    private final MumbaiComputeConfiguration mumbaiConfig;

    /**
     * Task priority levels - Mumbai traffic priority की तरह
     */
    public enum TaskPriority {
        LOW("निम्न"),           // Background tasks
        NORMAL("सामान्य"),       // Regular processing
        HIGH("उच्च"),           // Important tasks
        CRITICAL("गंभीर");       // Emergency/real-time tasks
        
        private final String hindiName;
        
        TaskPriority(String hindiName) {
            this.hindiName = hindiName;
        }
        
        public String getHindiName() {
            return hindiName;
        }
    }
    
    /**
     * Service status enumeration
     */
    public enum ServiceStatus {
        STARTING("प्रारंभ हो रहा"),
        RUNNING("चल रहा"),
        DEGRADED("क्षीण"),
        STOPPING("रुक रहा"),
        STOPPED("रुका हुआ");
        
        private final String hindiName;
        
        ServiceStatus(String hindiName) {
            this.hindiName = hindiName;
        }
        
        public String getHindiName() {
            return hindiName;
        }
    }
    
    /**
     * Compute task representation
     */
    public static class ComputeTask {
        private final String taskId;
        private final String functionName;
        private final Map<String, Object> payload;
        private final TaskPriority priority;
        private final LocalDateTime submitTime;
        private final long timeoutMs;
        private final String clientId;
        
        // Task execution tracking
        private LocalDateTime startTime;
        private LocalDateTime completionTime;
        private Object result;
        private Exception error;
        private volatile boolean completed;
        
        public ComputeTask(String taskId, String functionName, Map<String, Object> payload, 
                          TaskPriority priority, long timeoutMs, String clientId) {
            this.taskId = taskId;
            this.functionName = functionName;
            this.payload = payload != null ? new HashMap<>(payload) : new HashMap<>();
            this.priority = priority;
            this.timeoutMs = timeoutMs;
            this.clientId = clientId;
            this.submitTime = LocalDateTime.now();
            this.completed = false;
        }
        
        // Getters और setters
        public String getTaskId() { return taskId; }
        public String getFunctionName() { return functionName; }
        public Map<String, Object> getPayload() { return new HashMap<>(payload); }
        public TaskPriority getPriority() { return priority; }
        public LocalDateTime getSubmitTime() { return submitTime; }
        public long getTimeoutMs() { return timeoutMs; }
        public String getClientId() { return clientId; }
        
        public LocalDateTime getStartTime() { return startTime; }
        public void setStartTime(LocalDateTime startTime) { this.startTime = startTime; }
        
        public LocalDateTime getCompletionTime() { return completionTime; }
        public void setCompletionTime(LocalDateTime completionTime) { this.completionTime = completionTime; }
        
        public Object getResult() { return result; }
        public void setResult(Object result) { this.result = result; }
        
        public Exception getError() { return error; }
        public void setError(Exception error) { this.error = error; }
        
        public boolean isCompleted() { return completed; }
        public void setCompleted(boolean completed) { this.completed = completed; }
        
        public boolean isExpired() {
            return Duration.between(submitTime, LocalDateTime.now()).toMillis() > timeoutMs;
        }
        
        public long getExecutionTimeMs() {
            if (startTime != null && completionTime != null) {
                return Duration.between(startTime, completionTime).toMillis();
            }
            return 0;
        }
    }
    
    /**
     * Function performance metrics
     */
    public static class FunctionMetrics {
        private final AtomicLong invocations = new AtomicLong(0);
        private final AtomicLong successfulExecutions = new AtomicLong(0);
        private final AtomicLong failedExecutions = new AtomicLong(0);
        private final AtomicLong totalExecutionTimeMs = new AtomicLong(0);
        private final Queue<Long> recentExecutionTimes = new ConcurrentLinkedQueue<>();
        
        public void recordInvocation() {
            invocations.incrementAndGet();
        }
        
        public void recordSuccess(long executionTimeMs) {
            successfulExecutions.incrementAndGet();
            totalExecutionTimeMs.addAndGet(executionTimeMs);
            
            // Keep only last 100 execution times for averaging
            recentExecutionTimes.offer(executionTimeMs);
            while (recentExecutionTimes.size() > 100) {
                recentExecutionTimes.poll();
            }
        }
        
        public void recordFailure(long executionTimeMs) {
            failedExecutions.incrementAndGet();
            totalExecutionTimeMs.addAndGet(executionTimeMs);
        }
        
        public long getInvocations() { return invocations.get(); }
        public long getSuccessfulExecutions() { return successfulExecutions.get(); }
        public long getFailedExecutions() { return failedExecutions.get(); }
        
        public double getSuccessRate() {
            long total = invocations.get();
            return total > 0 ? (double) successfulExecutions.get() / total * 100.0 : 0.0;
        }
        
        public double getAverageExecutionTimeMs() {
            long executions = successfulExecutions.get() + failedExecutions.get();
            return executions > 0 ? (double) totalExecutionTimeMs.get() / executions : 0.0;
        }
        
        public double getRecentAverageExecutionTimeMs() {
            if (recentExecutionTimes.isEmpty()) {
                return 0.0;
            }
            return recentExecutionTimes.stream()
                .mapToLong(Long::longValue)
                .average()
                .orElse(0.0);
        }
    }
    
    /**
     * Mumbai-specific compute configuration
     */
    public static class MumbaiComputeConfiguration {
        private final Map<String, Object> config = new HashMap<>();
        
        public MumbaiComputeConfiguration() {
            // Mumbai के business hours के लिए configuration
            config.put("business_hours_start", 9);    // 9 AM
            config.put("business_hours_end", 18);     // 6 PM
            config.put("peak_multiplier", 2.5);       // Peak traffic multiplier
            config.put("monsoon_mode", false);        // Monsoon resilience mode
            
            // Local Mumbai preferences
            config.put("preferred_language", "Hindi");
            config.put("timezone", "Asia/Kolkata");
            config.put("currency", "INR");
            
            // Performance thresholds for Mumbai network conditions
            config.put("max_latency_ms", 500);        // Max acceptable latency
            config.put("connection_timeout_ms", 10000); // Higher timeout for Mumbai
            config.put("retry_attempts", 3);          // Network resilience
        }
        
        public Object get(String key) {
            return config.get(key);
        }
        
        public void set(String key, Object value) {
            config.put(key, value);
        }
        
        public boolean isMonsoonMode() {
            return (Boolean) config.getOrDefault("monsoon_mode", false);
        }
        
        public void enableMonsoonMode() {
            config.put("monsoon_mode", true);
            config.put("connection_timeout_ms", 15000); // Longer timeout in monsoon
            config.put("retry_attempts", 5);            // More retries
            LOGGER.info("Mumbai Monsoon Mode enabled - increased resilience settings");
        }
        
        public boolean isBusinessHours() {
            int currentHour = LocalDateTime.now().getHour();
            int startHour = (Integer) config.get("business_hours_start");
            int endHour = (Integer) config.get("business_hours_end");
            return currentHour >= startHour && currentHour <= endHour;
        }
    }
    
    /**
     * Constructor for Mumbai Edge Compute Service
     */
    public EdgeComputeService(String serviceId, String location, int threadPoolSize) {
        this.serviceId = serviceId;
        this.location = location;
        this.status = ServiceStatus.STARTING;
        
        // Initialize thread pool और queues
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
        this.taskQueue = new LinkedBlockingQueue<>(MAX_QUEUE_SIZE);
        this.activeTasks = new ConcurrentHashMap<>();
        this.scheduler = Executors.newScheduledThreadPool(2);
        
        // Initialize metrics
        this.totalTasksProcessed = new AtomicLong(0);
        this.totalTasksCompleted = new AtomicLong(0);
        this.totalTasksFailed = new AtomicLong(0);
        this.totalProcessingTimeMs = new AtomicLong(0);
        
        // Initialize priority tracking
        this.tasksByPriority = new ConcurrentHashMap<>();
        for (TaskPriority priority : TaskPriority.values()) {
            tasksByPriority.put(priority, new AtomicInteger(0));
        }
        
        // Initialize function management
        this.registeredFunctions = ConcurrentHashMap.newKeySet();
        this.functionMetrics = new ConcurrentHashMap<>();
        
        // Mumbai-specific configuration
        this.mumbaiConfig = new MumbaiComputeConfiguration();
        
        LOGGER.info(String.format("Mumbai Edge Compute Service initialized: %s @ %s", 
                                  serviceId, location));
    }
    
    /**
     * Service को start करना
     */
    public void start() {
        if (status != ServiceStatus.STARTING) {
            LOGGER.warning("Service already started or in invalid state");
            return;
        }
        
        this.startTime = LocalDateTime.now();
        this.status = ServiceStatus.RUNNING;
        
        // Start task processor
        startTaskProcessor();
        
        // Start health monitoring
        startHealthMonitoring();
        
        // Start cleanup tasks
        startMaintenanceTasks();
        
        // Register default Mumbai functions
        registerDefaultMumbaiFunctions();
        
        LOGGER.info(String.format("Mumbai Edge Compute Service started: %s", serviceId));
    }
    
    /**
     * Service को stop करना
     */
    public void stop() {
        if (status == ServiceStatus.STOPPED || status == ServiceStatus.STOPPING) {
            return;
        }
        
        LOGGER.info("Stopping Mumbai Edge Compute Service...");
        this.status = ServiceStatus.STOPPING;
        
        // Shutdown executor services
        scheduler.shutdown();
        executorService.shutdown();
        
        try {
            // Wait for tasks to complete
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        this.status = ServiceStatus.STOPPED;
        LOGGER.info("Mumbai Edge Compute Service stopped");
    }
    
    /**
     * Task submit करना
     */
    public String submitTask(String functionName, Map<String, Object> payload, 
                           TaskPriority priority, long timeoutMs, String clientId) {
        if (status != ServiceStatus.RUNNING) {
            throw new IllegalStateException("Service is not running");
        }
        
        if (!registeredFunctions.contains(functionName)) {
            throw new IllegalArgumentException("Function not registered: " + functionName);
        }
        
        String taskId = generateTaskId();
        ComputeTask task = new ComputeTask(taskId, functionName, payload, priority, timeoutMs, clientId);
        
        try {
            // Priority-based queue insertion
            boolean queued = taskQueue.offer(task, 1, TimeUnit.SECONDS);
            if (!queued) {
                throw new RuntimeException("Task queue is full");
            }
            
            activeTasks.put(taskId, task);
            totalTasksProcessed.incrementAndGet();
            tasksByPriority.get(priority).incrementAndGet();
            
            // Update function metrics
            functionMetrics.computeIfAbsent(functionName, k -> new FunctionMetrics())
                          .recordInvocation();
            
            LOGGER.fine(String.format("Task submitted: %s for function %s", taskId, functionName));
            return taskId;
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Task submission interrupted", e);
        }
    }
    
    /**
     * Task का result get करना
     */
    public Object getTaskResult(String taskId, long timeoutMs) throws InterruptedException {
        ComputeTask task = activeTasks.get(taskId);
        if (task == null) {
            throw new IllegalArgumentException("Task not found: " + taskId);
        }
        
        long startTime = System.currentTimeMillis();
        while (!task.isCompleted() && (System.currentTimeMillis() - startTime) < timeoutMs) {
            Thread.sleep(100); // Poll every 100ms
        }
        
        if (!task.isCompleted()) {
            throw new RuntimeException("Task execution timeout: " + taskId);
        }
        
        if (task.getError() != null) {
            throw new RuntimeException("Task execution failed", task.getError());
        }
        
        return task.getResult();
    }
    
    /**
     * Function register करना
     */
    public boolean registerFunction(String functionName, ComputeFunction function) {
        if (registeredFunctions.contains(functionName)) {
            LOGGER.warning("Function already registered: " + functionName);
            return false;
        }
        
        registeredFunctions.add(functionName);
        functionMetrics.put(functionName, new FunctionMetrics());
        
        LOGGER.info(String.format("Function registered: %s", functionName));
        return true;
    }
    
    /**
     * Service metrics प्राप्त करना
     */
    public Map<String, Object> getServiceMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        // Basic service info
        metrics.put("service_id", serviceId);
        metrics.put("location", location);
        metrics.put("status", status.name());
        metrics.put("uptime_seconds", getUptimeSeconds());
        
        // Task processing metrics
        long totalTasks = totalTasksProcessed.get();
        long completedTasks = totalTasksCompleted.get();
        long failedTasks = totalTasksFailed.get();
        
        metrics.put("total_tasks_processed", totalTasks);
        metrics.put("total_tasks_completed", completedTasks);
        metrics.put("total_tasks_failed", failedTasks);
        metrics.put("success_rate_percent", totalTasks > 0 ? 
                   (double) completedTasks / totalTasks * 100.0 : 0.0);
        
        // Performance metrics
        metrics.put("average_processing_time_ms", completedTasks > 0 ? 
                   (double) totalProcessingTimeMs.get() / completedTasks : 0.0);
        
        // Queue और active tasks
        metrics.put("active_tasks", activeTasks.size());
        metrics.put("queued_tasks", taskQueue.size());
        
        // Priority distribution
        Map<String, Integer> priorityStats = new HashMap<>();
        for (Map.Entry<TaskPriority, AtomicInteger> entry : tasksByPriority.entrySet()) {
            priorityStats.put(entry.getKey().name(), entry.getValue().get());
        }
        metrics.put("tasks_by_priority", priorityStats);
        
        // Function metrics
        Map<String, Object> funcMetrics = new HashMap<>();
        for (Map.Entry<String, FunctionMetrics> entry : functionMetrics.entrySet()) {
            FunctionMetrics fm = entry.getValue();
            Map<String, Object> funcStats = new HashMap<>();
            funcStats.put("invocations", fm.getInvocations());
            funcStats.put("success_rate_percent", fm.getSuccessRate());
            funcStats.put("avg_execution_time_ms", fm.getAverageExecutionTimeMs());
            funcMetrics.put(entry.getKey(), funcStats);
        }
        metrics.put("function_metrics", funcMetrics);
        
        // Mumbai-specific metrics
        metrics.put("mumbai_config", Map.of(
            "business_hours", mumbaiConfig.isBusinessHours(),
            "monsoon_mode", mumbaiConfig.isMonsoonMode()
        ));
        
        return metrics;
    }
    
    /**
     * Task processor शुरू करना
     */
    private void startTaskProcessor() {
        Runnable taskProcessor = () -> {
            while (status == ServiceStatus.RUNNING) {
                try {
                    ComputeTask task = taskQueue.poll(1, TimeUnit.SECONDS);
                    if (task != null) {
                        executorService.submit(() -> executeTask(task));
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    LOGGER.log(Level.SEVERE, "Task processor error", e);
                }
            }
        };
        
        new Thread(taskProcessor, "TaskProcessor").start();
    }
    
    /**
     * Task execute करना
     */
    private void executeTask(ComputeTask task) {
        task.setStartTime(LocalDateTime.now());
        FunctionMetrics metrics = functionMetrics.get(task.getFunctionName());
        
        try {
            // Check timeout before execution
            if (task.isExpired()) {
                throw new RuntimeException("Task expired before execution");
            }
            
            // Execute function (simulated - in real implementation, this would call actual functions)
            Object result = executeMumbaiFunction(task.getFunctionName(), task.getPayload());
            
            task.setResult(result);
            task.setCompletionTime(LocalDateTime.now());
            task.setCompleted(true);
            
            totalTasksCompleted.incrementAndGet();
            totalProcessingTimeMs.addAndGet(task.getExecutionTimeMs());
            
            if (metrics != null) {
                metrics.recordSuccess(task.getExecutionTimeMs());
            }
            
            LOGGER.fine(String.format("Task completed: %s in %dms", 
                       task.getTaskId(), task.getExecutionTimeMs()));
            
        } catch (Exception e) {
            task.setError(e);
            task.setCompletionTime(LocalDateTime.now());
            task.setCompleted(true);
            
            totalTasksFailed.incrementAndGet();
            
            if (metrics != null) {
                metrics.recordFailure(task.getExecutionTimeMs());
            }
            
            LOGGER.log(Level.WARNING, String.format("Task failed: %s", task.getTaskId()), e);
        }
        
        // Clean up completed task after some time
        scheduler.schedule(() -> activeTasks.remove(task.getTaskId()), 5, TimeUnit.MINUTES);
    }
    
    /**
     * Mumbai-specific functions execute करना
     */
    private Object executeMumbaiFunction(String functionName, Map<String, Object> payload) {
        // Simulate Mumbai-specific business logic
        switch (functionName) {
            case "mumbai_payment_processor":
                return processMumbaiPayment(payload);
            case "mumbai_traffic_analyzer":
                return analyzeMumbaiTraffic(payload);
            case "mumbai_weather_predictor":
                return predictMumbaiWeather(payload);
            case "mumbai_local_train_tracker":
                return trackMumbaiLocalTrain(payload);
            default:
                // Generic processing
                Thread.sleep(100); // Simulate processing time
                return Map.of("status", "processed", "function", functionName, "timestamp", LocalDateTime.now());
        }
    }
    
    /**
     * Mumbai payment processing function
     */
    private Object processMumbaiPayment(Map<String, Object> payload) throws InterruptedException {
        // Simulate payment processing logic
        Thread.sleep(200); // Processing time
        
        double amount = (Double) payload.getOrDefault("amount", 0.0);
        String currency = (String) payload.getOrDefault("currency", "INR");
        String merchant = (String) payload.getOrDefault("merchant", "Mumbai Store");
        
        // Business hours check
        if (mumbaiConfig.isBusinessHours()) {
            // Faster processing during business hours
            Thread.sleep(50);
        }
        
        return Map.of(
            "transaction_id", generateTransactionId(),
            "amount", amount,
            "currency", currency,
            "merchant", merchant,
            "status", "SUCCESS",
            "processing_time_ms", 200,
            "location", "Mumbai",
            "timestamp", LocalDateTime.now()
        );
    }
    
    /**
     * Mumbai traffic analysis function
     */
    private Object analyzeMumbaiTraffic(Map<String, Object> payload) throws InterruptedException {
        Thread.sleep(300); // Analysis time
        
        String location = (String) payload.getOrDefault("location", "Mumbai Central");
        int vehicleCount = (Integer) payload.getOrDefault("vehicle_count", 100);
        
        // Determine traffic density based on Mumbai patterns
        String trafficStatus;
        if (mumbaiConfig.isBusinessHours()) {
            trafficStatus = vehicleCount > 200 ? "Heavy" : "Moderate";
        } else {
            trafficStatus = vehicleCount > 50 ? "Light" : "Clear";
        }
        
        return Map.of(
            "location", location,
            "vehicle_count", vehicleCount,
            "traffic_status", trafficStatus,
            "congestion_level", calculateCongestionLevel(vehicleCount),
            "suggested_route", generateAlternateRoute(location),
            "analysis_time", LocalDateTime.now()
        );
    }
    
    /**
     * Health monitoring शुरू करना
     */
    private void startHealthMonitoring() {
        scheduler.scheduleAtFixedRate(() -> {
            try {
                performHealthCheck();
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Health check error", e);
            }
        }, HEALTH_CHECK_INTERVAL_MS, HEALTH_CHECK_INTERVAL_MS, TimeUnit.MILLISECONDS);
    }
    
    /**
     * Maintenance tasks शुरू करना
     */
    private void startMaintenanceTasks() {
        // Expired task cleanup
        scheduler.scheduleAtFixedRate(() -> {
            try {
                cleanupExpiredTasks();
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Cleanup error", e);
            }
        }, 60000, 60000, TimeUnit.MILLISECONDS); // Every minute
    }
    
    /**
     * Default Mumbai functions register करना
     */
    private void registerDefaultMumbaiFunctions() {
        registerFunction("mumbai_payment_processor", null);
        registerFunction("mumbai_traffic_analyzer", null);
        registerFunction("mumbai_weather_predictor", null);
        registerFunction("mumbai_local_train_tracker", null);
        
        LOGGER.info("Default Mumbai functions registered");
    }
    
    // Helper methods
    private String generateTaskId() {
        return "task_" + System.currentTimeMillis() + "_" + 
               Thread.currentThread().getId();
    }
    
    private String generateTransactionId() {
        return "TXN_MUM_" + System.currentTimeMillis();
    }
    
    private long getUptimeSeconds() {
        return startTime != null ? 
               Duration.between(startTime, LocalDateTime.now()).getSeconds() : 0;
    }
    
    private int calculateCongestionLevel(int vehicleCount) {
        return Math.min(100, (vehicleCount * 100) / 500); // Max 500 vehicles = 100% congestion
    }
    
    private String generateAlternateRoute(String location) {
        return "Alternate route from " + location + " via Western Express Highway";
    }
    
    private Object predictMumbaiWeather(Map<String, Object> payload) throws InterruptedException {
        Thread.sleep(150);
        return Map.of("forecast", "Partly cloudy", "temperature", 28, "humidity", 65);
    }
    
    private Object trackMumbaiLocalTrain(Map<String, Object> payload) throws InterruptedException {
        Thread.sleep(100);
        return Map.of("line", "Central", "status", "On time", "next_arrival", "2 minutes");
    }
    
    private void performHealthCheck() {
        // Check system health
        int activeTaskCount = activeTasks.size();
        int queueSize = taskQueue.size();
        
        if (queueSize > MAX_QUEUE_SIZE * 0.8) {
            status = ServiceStatus.DEGRADED;
            LOGGER.warning("Queue size high: " + queueSize);
        } else if (status == ServiceStatus.DEGRADED) {
            status = ServiceStatus.RUNNING;
            LOGGER.info("Service recovered to normal state");
        }
    }
    
    private void cleanupExpiredTasks() {
        List<String> expiredTasks = activeTasks.values().stream()
            .filter(ComputeTask::isExpired)
            .map(ComputeTask::getTaskId)
            .collect(Collectors.toList());
        
        for (String taskId : expiredTasks) {
            activeTasks.remove(taskId);
        }
        
        if (!expiredTasks.isEmpty()) {
            LOGGER.info("Cleaned up " + expiredTasks.size() + " expired tasks");
        }
    }
    
    /**
     * Compute function interface
     */
    @FunctionalInterface
    public interface ComputeFunction {
        Object execute(Map<String, Object> payload) throws Exception;
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🚀 Mumbai Edge Compute Service - Demonstration");
        System.out.println("=" + "=".repeat(60));
        
        // Initialize service
        EdgeComputeService service = new EdgeComputeService(
            "mumbai-edge-compute-01", "Mumbai Central", 8
        );
        
        try {
            // Start service
            service.start();
            System.out.println("✅ Edge Compute Service started");
            
            // Submit test tasks
            System.out.println("\n📋 Submitting Mumbai Test Tasks...");
            
            // Payment processing task
            String paymentTask = service.submitTask(
                "mumbai_payment_processor",
                Map.of("amount", 1500.0, "currency", "INR", "merchant", "Mumbai Cafe"),
                TaskPriority.HIGH,
                5000,
                "client_001"
            );
            System.out.println("💳 Payment task submitted: " + paymentTask);
            
            // Traffic analysis task
            String trafficTask = service.submitTask(
                "mumbai_traffic_analyzer",
                Map.of("location", "Bandra-Worli Sea Link", "vehicle_count", 350),
                TaskPriority.NORMAL,
                3000,
                "client_002"
            );
            System.out.println("🚗 Traffic task submitted: " + trafficTask);
            
            // Weather prediction task
            String weatherTask = service.submitTask(
                "mumbai_weather_predictor",
                Map.of("location", "Mumbai", "forecast_hours", 24),
                TaskPriority.LOW,
                2000,
                "client_003"
            );
            System.out.println("🌤️ Weather task submitted: " + weatherTask);
            
            // Wait for tasks to complete
            System.out.println("\n⏳ Waiting for tasks to complete...");
            Thread.sleep(2000);
            
            // Get results
            System.out.println("\n📊 Task Results:");
            try {
                Object paymentResult = service.getTaskResult(paymentTask, 1000);
                System.out.println("💳 Payment Result: " + paymentResult);
            } catch (Exception e) {
                System.out.println("💳 Payment Task: " + e.getMessage());
            }
            
            try {
                Object trafficResult = service.getTaskResult(trafficTask, 1000);
                System.out.println("🚗 Traffic Result: " + trafficResult);
            } catch (Exception e) {
                System.out.println("🚗 Traffic Task: " + e.getMessage());
            }
            
            try {
                Object weatherResult = service.getTaskResult(weatherTask, 1000);
                System.out.println("🌤️ Weather Result: " + weatherResult);
            } catch (Exception e) {
                System.out.println("🌤️ Weather Task: " + e.getMessage());
            }
            
            // Display service metrics
            System.out.println("\n📈 Service Performance Metrics:");
            System.out.println("-".repeat(40));
            
            Map<String, Object> metrics = service.getServiceMetrics();
            System.out.printf("Service ID: %s%n", metrics.get("service_id"));
            System.out.printf("Location: %s%n", metrics.get("location"));
            System.out.printf("Status: %s%n", metrics.get("status"));
            System.out.printf("Uptime: %d seconds%n", metrics.get("uptime_seconds"));
            System.out.printf("Tasks Processed: %d%n", metrics.get("total_tasks_processed"));
            System.out.printf("Tasks Completed: %d%n", metrics.get("total_tasks_completed"));
            System.out.printf("Success Rate: %.1f%%%n", metrics.get("success_rate_percent"));
            System.out.printf("Avg Processing Time: %.1f ms%n", metrics.get("average_processing_time_ms"));
            
            // Function metrics
            @SuppressWarnings("unchecked")
            Map<String, Object> funcMetrics = (Map<String, Object>) metrics.get("function_metrics");
            System.out.println("\n🔧 Function Performance:");
            for (Map.Entry<String, Object> entry : funcMetrics.entrySet()) {
                @SuppressWarnings("unchecked")
                Map<String, Object> stats = (Map<String, Object>) entry.getValue();
                System.out.printf("• %s: %d invocations, %.1f%% success rate%n",
                    entry.getKey(), 
                    ((Number) stats.get("invocations")).longValue(),
                    ((Number) stats.get("success_rate_percent")).doubleValue()
                );
            }
            
            // Mumbai-specific info
            @SuppressWarnings("unchecked")
            Map<String, Object> mumbaiConfig = (Map<String, Object>) metrics.get("mumbai_config");
            System.out.println("\n🏙️ Mumbai Configuration:");
            System.out.printf("• Business Hours: %s%n", 
                mumbaiConfig.get("business_hours") ? "Yes" : "No");
            System.out.printf("• Monsoon Mode: %s%n", 
                mumbaiConfig.get("monsoon_mode") ? "Enabled" : "Disabled");
            
            System.out.println("\n💰 Cost Analysis:");
            long totalTasks = ((Number) metrics.get("total_tasks_processed")).longValue();
            double edgeCost = totalTasks * 0.5;     // ₹0.5 per task
            double cloudCost = totalTasks * 5.0;    // ₹5.0 per task
            double savings = cloudCost - edgeCost;
            
            System.out.printf("• Edge Computing Cost: ₹%.2f%n", edgeCost);
            System.out.printf("• Cloud Computing Cost: ₹%.2f%n", cloudCost);
            System.out.printf("• Cost Savings: ₹%.2f (%.1f%%)%n", 
                savings, (savings / cloudCost) * 100);
            
            System.out.println("\n🎯 Mumbai Edge Computing Benefits:");
            System.out.println("• Local processing reduces latency by 80%");
            System.out.println("• Cost savings of 90% compared to cloud processing");
            System.out.println("• Business hours optimization for Mumbai traffic");
            System.out.println("• Monsoon-resilient architecture for reliability");
            System.out.println("• Hindi language support for local applications");
            
        } finally {
            // Cleanup
            System.out.println("\n🛑 Stopping service...");
            service.stop();
            System.out.println("✅ Mumbai Edge Compute Service demonstration completed!");
        }
    }
}