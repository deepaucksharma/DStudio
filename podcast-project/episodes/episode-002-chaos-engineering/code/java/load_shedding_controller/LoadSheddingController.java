/**
 * Load Shedding Controller - Episode 2
 * लोड शेडिंग नियंत्रक
 * 
 * Dynamic load shedding controller with priority-based request dropping
 * प्राथमिकता आधारित request dropping के साथ dynamic load shedding controller
 * 
 * जैसे Mumbai में power cut के दौरान important areas को पहले electricity देते हैं -
 * यह भी important requests को पहले process करता है और less important को drop करता है!
 * 
 * Author: Code Developer Agent A5-C-002
 * Indian Context: IRCTC peak hour load management, Zomato surge handling
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.time.*;
import java.util.function.*;

/**
 * Request priority levels - Request की प्राथमिकता स्तर
 */
enum RequestPriority {
    CRITICAL(1),    // महत्वपूर्ण - Payment, emergency services
    HIGH(2),        // उच्च - VIP users, premium features
    MEDIUM(3),      // मध्यम - Regular users, standard operations
    LOW(4),         // निम्न - Background tasks, analytics
    BULK(5);        // थोक - Batch operations, cleanup tasks
    
    private final int value;
    
    RequestPriority(int value) {
        this.value = value;
    }
    
    public int getValue() { return value; }
    
    public String getHindiName() {
        switch (this) {
            case CRITICAL: return "महत्वपूर्ण";
            case HIGH: return "उच्च";
            case MEDIUM: return "मध्यम";
            case LOW: return "निम्न";
            case BULK: return "थोक";
            default: return "अज्ञात";
        }
    }
}

/**
 * Load shedding strategies - लोड शेडिंग रणनीतियां
 */
enum SheddingStrategy {
    PRIORITY_BASED,     // प्राथमिकता आधारित - Drop by priority
    PERCENTAGE_BASED,   // प्रतिशत आधारित - Drop fixed percentage
    ADAPTIVE,          // अनुकूलन - Adapt based on system conditions
    MUMBAI_POWER_CUT,  // मुंबई पावर कट - Mumbai power cut style (essential first)
    IRCTC_PEAK_HOUR    // IRCTC पीक ऑवर - IRCTC peak hour style
}

/**
 * Request information - Request की जानकारी
 */
class RequestInfo {
    private final String requestId;
    private final RequestPriority priority;
    private final String userType;  // "premium", "regular", "bulk"
    private final String region;    // "mumbai", "delhi", etc.
    private final String serviceType; // "booking", "payment", "search"
    private final Instant arrivalTime;
    private final long estimatedProcessingTimeMs;
    
    // Indian context fields
    private final boolean isVerifiedUser;
    private final boolean isFestivalSeason;
    private final double resourceRequirement; // 0.0 to 1.0
    
    public RequestInfo(String requestId, RequestPriority priority, String userType, 
                      String region, String serviceType, long estimatedProcessingTimeMs) {
        this.requestId = requestId;
        this.priority = priority;
        this.userType = userType;
        this.region = region;
        this.serviceType = serviceType;
        this.arrivalTime = Instant.now();
        this.estimatedProcessingTimeMs = estimatedProcessingTimeMs;
        this.isVerifiedUser = Math.random() < 0.7; // 70% verified users
        this.isFestivalSeason = isFestivalSeason();
        this.resourceRequirement = Math.random() * 0.8 + 0.1; // 10% to 90%
    }
    
    private boolean isFestivalSeason() {
        int month = LocalDateTime.now().getMonthValue();
        return month == 3 || month == 4 || month == 10 || month == 11; // Festival months
    }
    
    // Getters
    public String getRequestId() { return requestId; }
    public RequestPriority getPriority() { return priority; }
    public String getUserType() { return userType; }
    public String getRegion() { return region; }
    public String getServiceType() { return serviceType; }
    public Instant getArrivalTime() { return arrivalTime; }
    public long getEstimatedProcessingTimeMs() { return estimatedProcessingTimeMs; }
    public boolean isVerifiedUser() { return isVerifiedUser; }
    public boolean isFestivalSeason() { return isFestivalSeason; }
    public double getResourceRequirement() { return resourceRequirement; }
    
    @Override
    public String toString() {
        return String.format("Request[id=%s, priority=%s, user=%s, region=%s, service=%s]",
                requestId, priority, userType, region, serviceType);
    }
}

/**
 * System metrics for load shedding decisions - लोड शेडिंग निर्णयों के लिए सिस्टम metrics
 */
class SystemMetrics {
    private final AtomicDouble cpuUtilization = new AtomicDouble(0.0);
    private final AtomicDouble memoryUtilization = new AtomicDouble(0.0);
    private final AtomicInteger activeConnections = new AtomicInteger(0);
    private final AtomicInteger queueDepth = new AtomicInteger(0);
    private final AtomicDouble responseTime = new AtomicDouble(0.0);
    private final AtomicDouble errorRate = new AtomicDouble(0.0);
    
    // Indian context metrics
    private final AtomicInteger mumbaiConnections = new AtomicInteger(0);
    private final AtomicInteger delhiConnections = new AtomicInteger(0);
    private final AtomicInteger festivalRequests = new AtomicInteger(0);
    
    // Getters and setters
    public double getCpuUtilization() { return cpuUtilization.get(); }
    public void setCpuUtilization(double cpu) { cpuUtilization.set(cpu); }
    
    public double getMemoryUtilization() { return memoryUtilization.get(); }
    public void setMemoryUtilization(double memory) { memoryUtilization.set(memory); }
    
    public int getActiveConnections() { return activeConnections.get(); }
    public void setActiveConnections(int connections) { activeConnections.set(connections); }
    
    public int getQueueDepth() { return queueDepth.get(); }
    public void setQueueDepth(int depth) { queueDepth.set(depth); }
    
    public double getResponseTime() { return responseTime.get(); }
    public void setResponseTime(double time) { responseTime.set(time); }
    
    public double getErrorRate() { return errorRate.get(); }
    public void setErrorRate(double rate) { errorRate.set(rate); }
    
    // Indian context
    public int getMumbaiConnections() { return mumbaiConnections.get(); }
    public void setMumbaiConnections(int connections) { mumbaiConnections.set(connections); }
    
    public int getDelhiConnections() { return delhiConnections.get(); }
    public void setDelhiConnections(int connections) { delhiConnections.set(connections); }
    
    public int getFestivalRequests() { return festivalRequests.get(); }
    public void setFestivalRequests(int requests) { festivalRequests.set(requests); }
    
    /**
     * Calculate overall system load - समग्र सिस्टम लोड की गणना करें
     */
    public double calculateOverallLoad() {
        double cpuFactor = getCpuUtilization() * 0.3;
        double memoryFactor = getMemoryUtilization() * 0.2;
        double connectionFactor = Math.min(getActiveConnections() / 1000.0, 1.0) * 0.3;
        double queueFactor = Math.min(getQueueDepth() / 500.0, 1.0) * 0.2;
        
        return Math.min(cpuFactor + memoryFactor + connectionFactor + queueFactor, 1.0);
    }
}

/**
 * Load shedding statistics - लोड शेडिंग आंकड़े
 */
class SheddingStats {
    private final AtomicLong totalRequests = new AtomicLong(0);
    private final AtomicLong droppedRequests = new AtomicLong(0);
    private final AtomicLong processedRequests = new AtomicLong(0);
    
    private final Map<RequestPriority, AtomicLong> droppedByPriority = new ConcurrentHashMap<>();
    private final Map<String, AtomicLong> droppedByRegion = new ConcurrentHashMap<>();
    private final Map<String, AtomicLong> droppedByServiceType = new ConcurrentHashMap<>();
    
    public SheddingStats() {
        for (RequestPriority priority : RequestPriority.values()) {
            droppedByPriority.put(priority, new AtomicLong(0));
        }
    }
    
    public void recordRequest(RequestInfo request, boolean dropped) {
        totalRequests.incrementAndGet();
        
        if (dropped) {
            droppedRequests.incrementAndGet();
            droppedByPriority.get(request.getPriority()).incrementAndGet();
            droppedByRegion.computeIfAbsent(request.getRegion(), k -> new AtomicLong(0)).incrementAndGet();
            droppedByServiceType.computeIfAbsent(request.getServiceType(), k -> new AtomicLong(0)).incrementAndGet();
        } else {
            processedRequests.incrementAndGet();
        }
    }
    
    public double getDropRate() {
        long total = totalRequests.get();
        return total > 0 ? (double) droppedRequests.get() / total : 0.0;
    }
    
    public long getTotalRequests() { return totalRequests.get(); }
    public long getDroppedRequests() { return droppedRequests.get(); }
    public long getProcessedRequests() { return processedRequests.get(); }
    
    public Map<RequestPriority, Long> getDroppedByPriority() {
        Map<RequestPriority, Long> result = new HashMap<>();
        droppedByPriority.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
    
    public Map<String, Long> getDroppedByRegion() {
        Map<String, Long> result = new HashMap<>();
        droppedByRegion.forEach((k, v) -> result.put(k, v.get()));
        return result;
    }
}

/**
 * Main Load Shedding Controller - मुख्य लोड शेडिंग नियंत्रक
 */
public class LoadSheddingController {
    
    private final SheddingStrategy strategy;
    private final SystemMetrics systemMetrics;
    private final SheddingStats stats;
    
    // Thresholds
    private volatile double loadThreshold = 0.8;        // 80% load threshold
    private volatile double criticalThreshold = 0.95;  // 95% critical threshold
    
    // Shedding rates by priority (when load > threshold)
    private final Map<RequestPriority, Double> sheddingRates = new ConcurrentHashMap<>();
    
    // Indian context configuration
    private final Map<String, Double> regionPriorities = new ConcurrentHashMap<>();
    private final Map<String, Double> serviceTypePriorities = new ConcurrentHashMap<>();
    
    // Monitoring
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
    private volatile boolean isMonitoring = false;
    
    public LoadSheddingController(SheddingStrategy strategy) {
        this.strategy = strategy;
        this.systemMetrics = new SystemMetrics();
        this.stats = new SheddingStats();
        
        // Initialize default shedding rates
        initializeDefaultSheddingRates();
        
        // Initialize Indian context priorities
        initializeIndianContextPriorities();
        
        System.out.printf("🔧 Load Shedding Controller initialized | लोड शेडिंग नियंत्रक शुरू%n");
        System.out.printf("   Strategy: %s | रणनीति: %s%n", strategy, strategy);
        System.out.printf("   Load Threshold: %.1f%% | लोड सीमा: %.1f%%%n", loadThreshold * 100, loadThreshold * 100);
    }
    
    private void initializeDefaultSheddingRates() {
        // Default drop rates when system is overloaded
        sheddingRates.put(RequestPriority.CRITICAL, 0.01);  // Drop only 1% of critical
        sheddingRates.put(RequestPriority.HIGH, 0.10);      // Drop 10% of high priority
        sheddingRates.put(RequestPriority.MEDIUM, 0.30);    // Drop 30% of medium
        sheddingRates.put(RequestPriority.LOW, 0.60);       // Drop 60% of low
        sheddingRates.put(RequestPriority.BULK, 0.90);      // Drop 90% of bulk
    }
    
    private void initializeIndianContextPriorities() {
        // Regional priorities (lower value = higher priority to keep)
        regionPriorities.put("mumbai", 1.0);     // Mumbai gets highest priority
        regionPriorities.put("delhi", 1.1);     // Delhi slightly lower
        regionPriorities.put("bangalore", 1.1); // Bangalore same as Delhi
        regionPriorities.put("hyderabad", 1.2); // Hyderabad lower
        regionPriorities.put("chennai", 1.2);   // Chennai same as Hyderabad
        regionPriorities.put("tier2", 1.4);     // Tier 2 cities lower priority
        regionPriorities.put("rural", 1.6);     // Rural areas lowest priority
        
        // Service type priorities
        serviceTypePriorities.put("payment", 0.8);    // Payments highest priority
        serviceTypePriorities.put("booking", 1.0);    // Booking standard priority
        serviceTypePriorities.put("search", 1.2);     // Search lower priority
        serviceTypePriorities.put("analytics", 1.8);  // Analytics lowest priority
    }
    
    /**
     * Main decision method - should we drop this request?
     * मुख्य निर्णय विधि - क्या हमें यह request drop करनी चाहिए?
     */
    public boolean shouldDropRequest(RequestInfo request) {
        double currentLoad = systemMetrics.calculateOverallLoad();
        
        // If system is not overloaded, don't drop anything
        if (currentLoad < loadThreshold) {
            stats.recordRequest(request, false);
            return false;
        }
        
        boolean shouldDrop = false;
        
        switch (strategy) {
            case PRIORITY_BASED:
                shouldDrop = shouldDropPriorityBased(request, currentLoad);
                break;
            case PERCENTAGE_BASED:
                shouldDrop = shouldDropPercentageBased(request, currentLoad);
                break;
            case ADAPTIVE:
                shouldDrop = shouldDropAdaptive(request, currentLoad);
                break;
            case MUMBAI_POWER_CUT:
                shouldDrop = shouldDropMumbaiPowerCutStyle(request, currentLoad);
                break;
            case IRCTC_PEAK_HOUR:
                shouldDrop = shouldDropIRCTCPeakHour(request, currentLoad);
                break;
        }
        
        stats.recordRequest(request, shouldDrop);
        
        if (shouldDrop) {
            System.out.printf("🚫 Dropped request: %s (Load: %.1f%%) | Request drop: %s%n", 
                             request.getRequestId(), currentLoad * 100, request.getRequestId());
        }
        
        return shouldDrop;
    }
    
    private boolean shouldDropPriorityBased(RequestInfo request, double currentLoad) {
        double dropRate = sheddingRates.get(request.getPriority());
        
        // Increase drop rate based on how much we're over the threshold
        double overloadFactor = Math.min((currentLoad - loadThreshold) / (1.0 - loadThreshold), 1.0);
        double adjustedDropRate = dropRate * (1.0 + overloadFactor * 2);
        
        return Math.random() < adjustedDropRate;
    }
    
    private boolean shouldDropPercentageBased(RequestInfo request, double currentLoad) {
        // Drop percentage based on overall load
        double dropPercentage = Math.min((currentLoad - loadThreshold) * 2, 0.8); // Max 80% drop
        return Math.random() < dropPercentage;
    }
    
    private boolean shouldDropAdaptive(RequestInfo request, double currentLoad) {
        // Adaptive strategy considers multiple factors
        double baseDrop = sheddingRates.get(request.getPriority());
        
        // Factor 1: System load
        double loadFactor = Math.max(1.0, (currentLoad - loadThreshold) * 5);
        
        // Factor 2: Queue depth
        double queueFactor = Math.max(1.0, systemMetrics.getQueueDepth() / 100.0);
        
        // Factor 3: Response time degradation
        double responseFactor = Math.max(1.0, systemMetrics.getResponseTime() / 1000.0);
        
        double adaptiveDropRate = baseDrop * loadFactor * queueFactor * responseFactor;
        return Math.random() < Math.min(adaptiveDropRate, 0.95);
    }
    
    private boolean shouldDropMumbaiPowerCutStyle(RequestInfo request, double currentLoad) {
        /**
         * Mumbai power cut style:
         * - Essential services (hospitals, police) never cut
         * - Important areas (business districts) cut less
         * - Residential areas cut more
         * - Industrial areas cut most
         */
        
        // Critical requests (like payments) are like hospitals - never drop
        if (request.getPriority() == RequestPriority.CRITICAL || 
            "payment".equals(request.getServiceType())) {
            return false;
        }
        
        // Mumbai region gets priority (like business district)
        double regionFactor = regionPriorities.getOrDefault(request.getRegion(), 1.5);
        
        // Service type factor
        double serviceFactor = serviceTypePriorities.getOrDefault(request.getServiceType(), 1.0);
        
        // User type factor (premium users are like VIP areas)
        double userFactor = "premium".equals(request.getUserType()) ? 0.5 : 
                           "regular".equals(request.getUserType()) ? 1.0 : 1.5;
        
        // Combine factors
        double dropProbability = ((currentLoad - loadThreshold) * 3) * regionFactor * serviceFactor * userFactor;
        
        return Math.random() < Math.min(dropProbability, 0.9);
    }
    
    private boolean shouldDropIRCTCPeakHour(RequestInfo request, double currentLoad) {
        /**
         * IRCTC peak hour style:
         * - Tatkal booking gets priority
         * - Verified users get priority
         * - Limit per user to prevent hoarding
         * - Fair distribution across regions
         */
        
        // Critical and high priority requests (like Tatkal) get preference
        if (request.getPriority() == RequestPriority.CRITICAL || 
            request.getPriority() == RequestPriority.HIGH) {
            return Math.random() < 0.05; // Only 5% drop rate
        }
        
        double baseDrop = 0.3; // 30% base drop rate during peak
        
        // Verified users get advantage
        if (request.isVerifiedUser()) {
            baseDrop *= 0.7; // 30% reduction in drop rate
        }
        
        // Festival season adjustment
        if (request.isFestivalSeason()) {
            baseDrop *= 1.3; // 30% increase during festivals
        }
        
        // Regional fairness - don't let one region dominate
        if ("mumbai".equals(request.getRegion()) && systemMetrics.getMumbaiConnections() > 500) {
            baseDrop *= 1.4; // Penalize Mumbai if too many connections
        }
        
        double loadFactor = Math.max(1.0, (currentLoad - loadThreshold) * 3);
        return Math.random() < (baseDrop * loadFactor);
    }
    
    /**
     * Start system monitoring - सिस्टम मॉनिटरिंग शुरू करें
     */
    public void startMonitoring() {
        if (isMonitoring) return;
        
        isMonitoring = true;
        
        // Simulate system metrics updates
        scheduler.scheduleAtFixedRate(this::updateSystemMetrics, 0, 1, TimeUnit.SECONDS);
        
        // Print periodic stats
        scheduler.scheduleAtFixedRate(this::printStats, 10, 10, TimeUnit.SECONDS);
        
        System.out.println("📊 Started system monitoring | सिस्टम मॉनिटरिंग शुरू");
    }
    
    private void updateSystemMetrics() {
        // Simulate realistic system metrics with Indian context
        
        // Base metrics with some randomness
        double baseCpu = 0.6 + Math.random() * 0.3; // 60-90% CPU
        double baseMemory = 0.5 + Math.random() * 0.4; // 50-90% Memory
        
        // Peak hour adjustments
        LocalTime now = LocalTime.now();
        boolean isPeakHour = (now.isAfter(LocalTime.of(9, 0)) && now.isBefore(LocalTime.of(11, 0))) ||
                            (now.isAfter(LocalTime.of(18, 0)) && now.isBefore(LocalTime.of(21, 0)));
        
        if (isPeakHour) {
            baseCpu *= 1.3; // 30% higher during peak
            baseMemory *= 1.2; // 20% higher during peak
        }
        
        systemMetrics.setCpuUtilization(Math.min(baseCpu, 1.0));
        systemMetrics.setMemoryUtilization(Math.min(baseMemory, 1.0));
        systemMetrics.setActiveConnections((int)(500 + Math.random() * 500));
        systemMetrics.setQueueDepth((int)(50 + Math.random() * 200));
        systemMetrics.setResponseTime(200 + Math.random() * 800); // 200-1000ms
        systemMetrics.setErrorRate(Math.random() * 0.05); // 0-5% error rate
        
        // Regional distribution
        systemMetrics.setMumbaiConnections((int)(Math.random() * 300));
        systemMetrics.setDelhiConnections((int)(Math.random() * 200));
        systemMetrics.setFestivalRequests((int)(Math.random() * 100));
    }
    
    private void printStats() {
        double currentLoad = systemMetrics.calculateOverallLoad();
        
        System.out.printf("%n📊 SYSTEM STATUS | सिस्टम स्थिति%n");
        System.out.printf("   Overall Load: %.1f%% | समग्र लोड: %.1f%%%n", currentLoad * 100, currentLoad * 100);
        System.out.printf("   CPU: %.1f%%, Memory: %.1f%% | CPU: %.1f%%, Memory: %.1f%%%n", 
                         systemMetrics.getCpuUtilization() * 100, 
                         systemMetrics.getMemoryUtilization() * 100,
                         systemMetrics.getCpuUtilization() * 100, 
                         systemMetrics.getMemoryUtilization() * 100);
        System.out.printf("   Active Connections: %d, Queue: %d | सक्रिय कनेक्शन: %d, Queue: %d%n",
                         systemMetrics.getActiveConnections(), systemMetrics.getQueueDepth(),
                         systemMetrics.getActiveConnections(), systemMetrics.getQueueDepth());
        
        System.out.printf("%n🚫 SHEDDING STATS | शेडिंग आंकड़े%n");
        System.out.printf("   Total Requests: %d | कुल अनुरोध: %d%n", stats.getTotalRequests(), stats.getTotalRequests());
        System.out.printf("   Dropped: %d (%.1f%%) | Drop: %d (%.1f%%)%n", 
                         stats.getDroppedRequests(), stats.getDropRate() * 100,
                         stats.getDroppedRequests(), stats.getDropRate() * 100);
        System.out.printf("   Processed: %d | प्रसंस्करित: %d%n", stats.getProcessedRequests(), stats.getProcessedRequests());
        
        // Priority-wise breakdown
        System.out.printf("   Dropped by Priority | प्राथमिकता के आधार पर Drop:%n");
        stats.getDroppedByPriority().forEach((priority, count) -> {
            if (count > 0) {
                System.out.printf("     %s (%s): %d%n", priority, priority.getHindiName(), count);
            }
        });
    }
    
    public void stopMonitoring() {
        isMonitoring = false;
        scheduler.shutdown();
        System.out.println("⏹️  Stopped monitoring | मॉनिटरिंग बंद");
    }
    
    // Getters for testing
    public SystemMetrics getSystemMetrics() { return systemMetrics; }
    public SheddingStats getStats() { return stats; }
    
    /**
     * Demo method showing load shedding in action
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🔧 Load Shedding Controller Demo - Episode 2");
        System.out.println("लोड शेडिंग नियंत्रक डेमो - एपिसोड 2\n");
        
        // Test different strategies
        SheddingStrategy[] strategies = {
            SheddingStrategy.PRIORITY_BASED,
            SheddingStrategy.MUMBAI_POWER_CUT,
            SheddingStrategy.IRCTC_PEAK_HOUR,
            SheddingStrategy.ADAPTIVE
        };
        
        for (SheddingStrategy strategy : strategies) {
            System.out.printf("\n" + "=".repeat(60) + "\n");
            System.out.printf("TESTING STRATEGY: %s\n", strategy);
            System.out.printf("रणनीति का परीक्षण: %s\n", strategy);
            System.out.printf("=".repeat(60) + "\n");
            
            LoadSheddingController controller = new LoadSheddingController(strategy);
            controller.startMonitoring();
            
            // Generate sample requests
            String[] regions = {"mumbai", "delhi", "bangalore", "chennai", "tier2"};
            String[] userTypes = {"premium", "regular", "bulk"};
            String[] serviceTypes = {"payment", "booking", "search", "analytics"};
            
            // Simulate high load scenario
            for (int i = 0; i < 100; i++) {
                RequestInfo request = new RequestInfo(
                    "req_" + i,
                    RequestPriority.values()[(int)(Math.random() * RequestPriority.values().length)],
                    userTypes[(int)(Math.random() * userTypes.length)],
                    regions[(int)(Math.random() * regions.length)],
                    serviceTypes[(int)(Math.random() * serviceTypes.length)],
                    (long)(Math.random() * 5000 + 1000) // 1-6 seconds
                );
                
                boolean dropped = controller.shouldDropRequest(request);
                
                // Print some examples
                if (i < 10 || (dropped && Math.random() < 0.1)) {
                    System.out.printf("%s %s | %s %s\n", 
                                     dropped ? "🚫 DROP" : "✅ PROCESS",
                                     request,
                                     dropped ? "DROP" : "PROCESS",
                                     request);
                }
                
                Thread.sleep(50); // Small delay
            }
            
            // Wait for final stats
            Thread.sleep(2000);
            controller.stopMonitoring();
        }
        
        System.out.println("\n🎉 Load Shedding Controller demonstration completed!");
        System.out.println("लोड शेडिंग नियंत्रक प्रदर्शन पूर्ण!");
        
        System.out.println("\n💡 KEY LEARNINGS | मुख्य शिक्षाएं:");
        System.out.println("1. Priority-based shedding protects critical requests");
        System.out.println("   प्राथमिकता आधारित shedding महत्वपूर्ण requests की सुरक्षा करता है");
        System.out.println("2. Mumbai power cut style ensures fairness across regions");
        System.out.println("   Mumbai power cut style regions में निष्पक्षता सुनिश्चित करता है");
        System.out.println("3. IRCTC style prevents gaming and ensures fair access");
        System.out.println("   IRCTC style gaming रोकता है और fair access सुनिश्चित करता है");
        System.out.println("4. Adaptive strategies respond to changing system conditions");
        System.out.println("   Adaptive strategies बदलती system conditions के अनुकूल होती हैं");
    }
}