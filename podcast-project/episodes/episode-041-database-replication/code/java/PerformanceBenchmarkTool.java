/**
 * Episode 41: Database Replication Strategies
 * Java Example: Performance Benchmarking Tool for Replication Strategies
 * 
 * यह comprehensive performance benchmarking tool है जो different replication 
 * strategies की performance measure करता है। Real-world Indian scenarios के साथ
 * detailed metrics और analysis provide करता है।
 * 
 * Real-world Use Case: Banking और E-commerce Performance Analysis
 * - Master-slave vs Master-master performance comparison
 * - Latency और throughput analysis
 * - Indian network conditions simulation
 * - Resource utilization monitoring
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;

// Performance metrics data structures
class PerformanceMetrics {
    private final AtomicLong totalOperations = new AtomicLong(0);
    private final AtomicLong successfulOperations = new AtomicLong(0);
    private final AtomicLong failedOperations = new AtomicLong(0);
    private final List<Long> latencies = Collections.synchronizedList(new ArrayList<>());
    private final AtomicReference<LocalDateTime> startTime = new AtomicReference<>();
    private final AtomicReference<LocalDateTime> endTime = new AtomicReference<>();
    
    public void recordOperation(long latencyMs, boolean success) {
        totalOperations.incrementAndGet();
        if (success) {
            successfulOperations.incrementAndGet();
        } else {
            failedOperations.incrementAndGet();
        }
        latencies.add(latencyMs);
    }
    
    public void start() {
        startTime.set(LocalDateTime.now());
    }
    
    public void stop() {
        endTime.set(LocalDateTime.now());
    }
    
    public double getThroughput() {
        if (startTime.get() == null || endTime.get() == null) return 0.0;
        
        Duration duration = Duration.between(startTime.get(), endTime.get());
        if (duration.toMillis() == 0) return 0.0;
        
        return (double) totalOperations.get() / (duration.toMillis() / 1000.0);
    }
    
    public double getSuccessRate() {
        long total = totalOperations.get();
        return total == 0 ? 0.0 : (double) successfulOperations.get() / total * 100.0;
    }
    
    public LatencyStats getLatencyStats() {
        if (latencies.isEmpty()) {
            return new LatencyStats(0, 0, 0, 0, 0);
        }
        
        List<Long> sortedLatencies = new ArrayList<>(latencies);
        Collections.sort(sortedLatencies);
        
        long min = sortedLatencies.get(0);
        long max = sortedLatencies.get(sortedLatencies.size() - 1);
        double avg = sortedLatencies.stream().mapToLong(Long::longValue).average().orElse(0.0);
        long p95 = sortedLatencies.get((int) (sortedLatencies.size() * 0.95));
        long p99 = sortedLatencies.get((int) (sortedLatencies.size() * 0.99));
        
        return new LatencyStats(min, max, avg, p95, p99);
    }
    
    public long getTotalOperations() { return totalOperations.get(); }
    public long getSuccessfulOperations() { return successfulOperations.get(); }
    public long getFailedOperations() { return failedOperations.get(); }
}

class LatencyStats {
    public final long min, max, p95, p99;
    public final double avg;
    
    public LatencyStats(long min, long max, double avg, long p95, long p99) {
        this.min = min;
        this.max = max;
        this.avg = avg;
        this.p95 = p95;
        this.p99 = p99;
    }
}

// Replication strategy interfaces
interface ReplicationStrategy {
    String getName();
    boolean processOperation(String operation, String data) throws Exception;
    PerformanceMetrics getMetrics();
    void cleanup();
}

// Master-Slave Replication Implementation
class MasterSlaveReplication implements ReplicationStrategy {
    private final String name;
    private final int replicationDelayMs;
    private final ExecutorService replicationPool;
    private final PerformanceMetrics metrics;
    private final AtomicInteger activeReplications = new AtomicInteger(0);
    
    // Simulate Indian banking network latencies
    private final Map<String, Integer> regionLatencies = Map.of(
        "Mumbai-Delhi", 25,     // 25ms typical inter-city latency
        "Mumbai-Bangalore", 35,
        "Delhi-Chennai", 40,
        "Mumbai-Kolkata", 45
    );
    
    public MasterSlaveReplication(String name, int replicationDelayMs) {
        this.name = name;
        this.replicationDelayMs = replicationDelayMs;
        this.replicationPool = Executors.newFixedThreadPool(5);
        this.metrics = new PerformanceMetrics();
    }
    
    @Override
    public String getName() { return name; }
    
    @Override
    public boolean processOperation(String operation, String data) throws Exception {
        long startTime = System.currentTimeMillis();
        boolean success = false;
        
        try {
            // Simulate master processing
            Thread.sleep(2); // 2ms for master processing
            
            // Async replication to slaves
            CompletableFuture<Boolean> replicationFuture = CompletableFuture.supplyAsync(() -> {
                try {
                    activeReplications.incrementAndGet();
                    
                    // Simulate network latency based on Indian geography
                    String region = getRandomRegion();
                    int networkLatency = regionLatencies.get(region);
                    Thread.sleep(networkLatency + replicationDelayMs);
                    
                    // Simulate occasional replication failure (2% failure rate)
                    if (Math.random() < 0.02) {
                        throw new RuntimeException("Network partition in " + region);
                    }
                    
                    return true;
                } catch (Exception e) {
                    return false;
                } finally {
                    activeReplications.decrementAndGet();
                }
            }, replicationPool);
            
            // For master-slave, we don't wait for replication (async)
            success = true;
            
        } catch (Exception e) {
            success = false;
        }
        
        long latency = System.currentTimeMillis() - startTime;
        metrics.recordOperation(latency, success);
        
        return success;
    }
    
    private String getRandomRegion() {
        List<String> regions = new ArrayList<>(regionLatencies.keySet());
        return regions.get((int) (Math.random() * regions.size()));
    }
    
    @Override
    public PerformanceMetrics getMetrics() { return metrics; }
    
    @Override
    public void cleanup() {
        replicationPool.shutdown();
        try {
            replicationPool.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public int getActiveReplications() {
        return activeReplications.get();
    }
}

// Master-Master Replication Implementation
class MasterMasterReplication implements ReplicationStrategy {
    private final String name;
    private final PerformanceMetrics metrics;
    private final ExecutorService consensusPool;
    private final AtomicInteger conflictCount = new AtomicInteger(0);
    
    // Simulate conflict probability based on operation type
    private final Map<String, Double> conflictProbabilities = Map.of(
        "BANK_TRANSFER", 0.15,      // 15% conflict probability for banking
        "UPI_PAYMENT", 0.10,        // 10% for UPI (faster processing)
        "INVENTORY_UPDATE", 0.08,   // 8% for inventory updates
        "USER_PROFILE", 0.02        // 2% for profile updates
    );
    
    public MasterMasterReplication(String name) {
        this.name = name;
        this.metrics = new PerformanceMetrics();
        this.consensusPool = Executors.newFixedThreadPool(3);
    }
    
    @Override
    public String getName() { return name; }
    
    @Override
    public boolean processOperation(String operation, String data) throws Exception {
        long startTime = System.currentTimeMillis();
        boolean success = false;
        
        try {
            // Check for conflicts
            double conflictProb = conflictProbabilities.getOrDefault(operation, 0.05);
            boolean hasConflict = Math.random() < conflictProb;
            
            if (hasConflict) {
                conflictCount.incrementAndGet();
                // Simulate conflict resolution time
                success = resolveConflict(operation, data);
            } else {
                // Normal processing with peer coordination
                success = processWithPeerCoordination(operation, data);
            }
            
        } catch (Exception e) {
            success = false;
        }
        
        long latency = System.currentTimeMillis() - startTime;
        metrics.recordOperation(latency, success);
        
        return success;
    }
    
    private boolean resolveConflict(String operation, String data) throws Exception {
        // Simulate different conflict resolution strategies
        int resolutionTime;
        
        switch (operation) {
            case "BANK_TRANSFER":
                // Banking conflicts require careful resolution (serializable isolation)
                resolutionTime = 50 + (int) (Math.random() * 30); // 50-80ms
                break;
            case "UPI_PAYMENT":
                // UPI conflicts resolved faster (timestamp ordering)
                resolutionTime = 20 + (int) (Math.random() * 15); // 20-35ms
                break;
            default:
                // General conflict resolution
                resolutionTime = 30 + (int) (Math.random() * 20); // 30-50ms
        }
        
        Thread.sleep(resolutionTime);
        
        // 95% of conflicts are resolved successfully
        return Math.random() < 0.95;
    }
    
    private boolean processWithPeerCoordination(String operation, String data) throws Exception {
        // Simulate peer coordination overhead
        
        // Multi-phase coordination
        List<CompletableFuture<Boolean>> coordinationPhases = Arrays.asList(
            // Phase 1: Prepare
            CompletableFuture.supplyAsync(() -> {
                try {
                    Thread.sleep(15); // 15ms prepare phase
                    return Math.random() < 0.98; // 98% prepare success
                } catch (InterruptedException e) {
                    return false;
                }
            }, consensusPool),
            
            // Phase 2: Coordinate with peers
            CompletableFuture.supplyAsync(() -> {
                try {
                    Thread.sleep(25); // 25ms peer coordination
                    return Math.random() < 0.97; // 97% coordination success
                } catch (InterruptedException e) {
                    return false;
                }
            }, consensusPool)
        );
        
        // Wait for all phases to complete
        CompletableFuture<Void> allPhases = CompletableFuture.allOf(
            coordinationPhases.toArray(new CompletableFuture[0])
        );
        
        allPhases.get(200, TimeUnit.MILLISECONDS); // 200ms timeout
        
        // Check if all phases succeeded
        return coordinationPhases.stream()
                .allMatch(future -> {
                    try {
                        return future.get();
                    } catch (Exception e) {
                        return false;
                    }
                });
    }
    
    @Override
    public PerformanceMetrics getMetrics() { return metrics; }
    
    @Override
    public void cleanup() {
        consensusPool.shutdown();
        try {
            consensusPool.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public int getConflictCount() {
        return conflictCount.get();
    }
}

// Workload Generator for Indian scenarios
class IndianWorkloadGenerator {
    private final Random random = new Random();
    
    // Banking operations distribution (based on Indian banking patterns)
    private final Map<String, Double> bankingWorkload = Map.of(
        "ACCOUNT_BALANCE", 0.40,    // 40% balance inquiries
        "UPI_PAYMENT", 0.25,        // 25% UPI payments  
        "BANK_TRANSFER", 0.15,      // 15% bank transfers
        "BILL_PAYMENT", 0.12,       // 12% bill payments
        "DEPOSIT", 0.05,            // 5% deposits
        "WITHDRAWAL", 0.03          // 3% withdrawals
    );
    
    // E-commerce operations (based on Flipkart/Amazon India patterns)
    private final Map<String, Double> ecommerceWorkload = Map.of(
        "PRODUCT_VIEW", 0.45,       // 45% product views
        "INVENTORY_UPDATE", 0.20,   // 20% inventory updates
        "ORDER_PROCESS", 0.15,      // 15% order processing
        "USER_PROFILE", 0.10,       // 10% profile updates
        "SEARCH_QUERY", 0.07,       // 7% search queries
        "PAYMENT_PROCESS", 0.03     // 3% payment processing
    );
    
    public List<WorkloadOperation> generateBankingWorkload(int operationCount) {
        return generateWorkload(bankingWorkload, operationCount, "BANKING");
    }
    
    public List<WorkloadOperation> generateEcommerceWorkload(int operationCount) {
        return generateWorkload(ecommerceWorkload, operationCount, "ECOMMERCE");
    }
    
    private List<WorkloadOperation> generateWorkload(Map<String, Double> distribution, 
                                                   int operationCount, String type) {
        List<WorkloadOperation> operations = new ArrayList<>();
        List<String> operationTypes = new ArrayList<>(distribution.keySet());
        List<Double> weights = new ArrayList<>(distribution.values());
        
        for (int i = 0; i < operationCount; i++) {
            String operation = selectWeightedRandom(operationTypes, weights);
            String data = generateOperationData(operation, type);
            operations.add(new WorkloadOperation(operation, data));
        }
        
        return operations;
    }
    
    private String selectWeightedRandom(List<String> items, List<Double> weights) {
        double totalWeight = weights.stream().mapToDouble(Double::doubleValue).sum();
        double randomValue = random.nextDouble() * totalWeight;
        
        double cumulativeWeight = 0.0;
        for (int i = 0; i < items.size(); i++) {
            cumulativeWeight += weights.get(i);
            if (randomValue <= cumulativeWeight) {
                return items.get(i);
            }
        }
        
        return items.get(items.size() - 1);
    }
    
    private String generateOperationData(String operation, String type) {
        // Generate realistic Indian data based on operation type
        switch (operation) {
            case "UPI_PAYMENT":
                return String.format("Amount: ₹%d, From: %s@paytm, To: %s@phonepe",
                    random.nextInt(10000) + 100,
                    generateIndianName(),
                    generateIndianName());
                    
            case "BANK_TRANSFER":
                return String.format("Amount: ₹%d, From: %s, To: %s",
                    random.nextInt(100000) + 1000,
                    generateAccountNumber("HDFC"),
                    generateAccountNumber("ICICI"));
                    
            case "INVENTORY_UPDATE":
                return String.format("SKU: %s, Quantity: %d, Warehouse: %s",
                    generateSKU(),
                    random.nextInt(100) + 1,
                    generateWarehouse());
                    
            default:
                return String.format("Operation: %s, Timestamp: %s",
                    operation, 
                    LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME));
        }
    }
    
    private String generateIndianName() {
        String[] names = {"Rajesh", "Priya", "Amit", "Sunita", "Vikram", "Kavya", "Deepak", "Neha"};
        return names[random.nextInt(names.length)];
    }
    
    private String generateAccountNumber(String bank) {
        return bank + String.format("%08d", random.nextInt(100000000));
    }
    
    private String generateSKU() {
        String[] categories = {"MOB", "LAP", "TV", "CLOTH", "SHOE"};
        String category = categories[random.nextInt(categories.length)];
        return category + String.format("%06d", random.nextInt(1000000));
    }
    
    private String generateWarehouse() {
        String[] warehouses = {"MUM_WH", "DEL_WH", "BLR_WH", "CHE_WH", "KOL_WH"};
        return warehouses[random.nextInt(warehouses.length)];
    }
}

class WorkloadOperation {
    public final String operation;
    public final String data;
    
    public WorkloadOperation(String operation, String data) {
        this.operation = operation;
        this.data = data;
    }
}

// Main benchmarking tool
public class PerformanceBenchmarkTool {
    private final IndianWorkloadGenerator workloadGenerator = new IndianWorkloadGenerator();
    
    public static void main(String[] args) {
        PerformanceBenchmarkTool tool = new PerformanceBenchmarkTool();
        
        System.out.println("=".repeat(80));
        System.out.println("Database Replication Performance Benchmarking Tool");
        System.out.println("Episode 41: Database Replication Strategies");
        System.out.println("Indian Banking और E-commerce Scenarios");
        System.out.println("=".repeat(80));
        
        // Run banking workload benchmark
        System.out.println("\n--- Banking Workload Benchmark ---");
        tool.runBankingBenchmark();
        
        // Run e-commerce workload benchmark  
        System.out.println("\n--- E-commerce Workload Benchmark ---");
        tool.runEcommerceBenchmark();
        
        // Comparative analysis
        System.out.println("\n--- Comparative Analysis ---");
        tool.runComparativeBenchmark();
    }
    
    public void runBankingBenchmark() {
        // Banking workload के लिए different strategies test करना
        List<ReplicationStrategy> strategies = Arrays.asList(
            new MasterSlaveReplication("Banking Master-Slave", 5),
            new MasterMasterReplication("Banking Master-Master")
        );
        
        List<WorkloadOperation> bankingWorkload = workloadGenerator.generateBankingWorkload(1000);
        
        System.out.println("Testing banking workload with 1000 operations...");
        
        for (ReplicationStrategy strategy : strategies) {
            System.out.println(String.format("\nTesting: %s", strategy.getName()));
            
            BenchmarkResult result = runBenchmark(strategy, bankingWorkload, 10); // 10 threads
            printBenchmarkResult(strategy.getName(), result);
            
            strategy.cleanup();
        }
    }
    
    public void runEcommerceBenchmark() {
        // E-commerce workload के लिए different strategies test करना
        List<ReplicationStrategy> strategies = Arrays.asList(
            new MasterSlaveReplication("E-commerce Master-Slave", 3),
            new MasterMasterReplication("E-commerce Master-Master")
        );
        
        List<WorkloadOperation> ecommerceWorkload = workloadGenerator.generateEcommerceWorkload(1500);
        
        System.out.println("Testing e-commerce workload with 1500 operations...");
        
        for (ReplicationStrategy strategy : strategies) {
            System.out.println(String.format("\nTesting: %s", strategy.getName()));
            
            BenchmarkResult result = runBenchmark(strategy, ecommerceWorkload, 15); // 15 threads
            printBenchmarkResult(strategy.getName(), result);
            
            strategy.cleanup();
        }
    }
    
    public void runComparativeBenchmark() {
        // Different load patterns के साथ comparative analysis
        int[] threadCounts = {5, 10, 20, 30};
        int operationsPerTest = 500;
        
        System.out.println("Running comparative benchmark with varying thread counts...");
        System.out.println("Format: Threads | Strategy | Throughput (ops/sec) | P95 Latency (ms) | Success Rate (%)");
        System.out.println("-".repeat(90));
        
        for (int threadCount : threadCounts) {
            List<WorkloadOperation> workload = workloadGenerator.generateBankingWorkload(operationsPerTest);
            
            // Test Master-Slave
            MasterSlaveReplication masterSlave = new MasterSlaveReplication("MS", 5);
            BenchmarkResult msResult = runBenchmark(masterSlave, workload, threadCount);
            
            System.out.println(String.format("%7d | %20s | %15.2f | %14d | %12.1f",
                threadCount, "Master-Slave", msResult.throughput, 
                msResult.latencyStats.p95, msResult.successRate));
            
            masterSlave.cleanup();
            
            // Test Master-Master
            MasterMasterReplication masterMaster = new MasterMasterReplication("MM");
            BenchmarkResult mmResult = runBenchmark(masterMaster, workload, threadCount);
            
            System.out.println(String.format("%7d | %20s | %15.2f | %14d | %12.1f",
                threadCount, "Master-Master", mmResult.throughput,
                mmResult.latencyStats.p95, mmResult.successRate));
            
            masterMaster.cleanup();
            
            System.out.println();
        }
    }
    
    private BenchmarkResult runBenchmark(ReplicationStrategy strategy, 
                                       List<WorkloadOperation> workload, 
                                       int threadCount) {
        PerformanceMetrics metrics = strategy.getMetrics();
        ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        CountDownLatch latch = new CountDownLatch(workload.size());
        
        metrics.start();
        
        // Submit all operations
        for (WorkloadOperation operation : workload) {
            executor.submit(() -> {
                try {
                    strategy.processOperation(operation.operation, operation.data);
                } catch (Exception e) {
                    // Error already recorded in strategy
                } finally {
                    latch.countDown();
                }
            });
        }
        
        // Wait for completion
        try {
            latch.await(60, TimeUnit.SECONDS); // 60 second timeout
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        metrics.stop();
        
        executor.shutdown();
        try {
            executor.awaitTermination(5, TimeUnit.SECONDS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        return new BenchmarkResult(
            metrics.getThroughput(),
            metrics.getSuccessRate(),
            metrics.getLatencyStats(),
            metrics.getTotalOperations(),
            metrics.getSuccessfulOperations(),
            metrics.getFailedOperations()
        );
    }
    
    private void printBenchmarkResult(String strategyName, BenchmarkResult result) {
        System.out.println(String.format("Strategy: %s", strategyName));
        System.out.println(String.format("  Throughput: %.2f operations/second", result.throughput));
        System.out.println(String.format("  Success Rate: %.1f%%", result.successRate));
        System.out.println(String.format("  Total Operations: %d", result.totalOperations));
        System.out.println(String.format("  Successful: %d", result.successfulOperations));
        System.out.println(String.format("  Failed: %d", result.failedOperations));
        System.out.println("  Latency Statistics:");
        System.out.println(String.format("    Min: %d ms", result.latencyStats.min));
        System.out.println(String.format("    Avg: %.2f ms", result.latencyStats.avg));
        System.out.println(String.format("    P95: %d ms", result.latencyStats.p95));
        System.out.println(String.format("    P99: %d ms", result.latencyStats.p99));
        System.out.println(String.format("    Max: %d ms", result.latencyStats.max));
    }
}

class BenchmarkResult {
    public final double throughput;
    public final double successRate;
    public final LatencyStats latencyStats;
    public final long totalOperations;
    public final long successfulOperations;
    public final long failedOperations;
    
    public BenchmarkResult(double throughput, double successRate, LatencyStats latencyStats,
                          long totalOperations, long successfulOperations, long failedOperations) {
        this.throughput = throughput;
        this.successRate = successRate;
        this.latencyStats = latencyStats;
        this.totalOperations = totalOperations;
        this.successfulOperations = successfulOperations;
        this.failedOperations = failedOperations;
    }
}