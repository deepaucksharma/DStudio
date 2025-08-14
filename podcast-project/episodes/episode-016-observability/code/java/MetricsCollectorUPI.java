package com.episode16.observability;

import io.micrometer.core.instrument.*;
import io.micrometer.core.instrument.simple.SimpleMeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

/**
 * Episode 16: Observability & Monitoring
 * Java Example: Comprehensive UPI Metrics Collector
 * 
 * भारतीय context: PhonePe/Paytm style UPI transaction metrics
 * Real-world scenario: Production-grade metrics collection for UPI payments
 */
public class MetricsCollectorUPI {
    
    private static final Logger logger = LoggerFactory.getLogger(MetricsCollectorUPI.class);
    
    // Micrometer meter registry for metrics
    private final MeterRegistry meterRegistry;
    
    // UPI transaction metrics
    private final Counter upiTransactionCounter;
    private final Timer upiTransactionTimer;
    private final Gauge upiSuccessRateGauge;
    private final DistributionSummary upiAmountSummary;
    
    // Bank-specific metrics
    private final Map<String, Counter> bankTransactionCounters = new HashMap<>();
    private final Map<String, Timer> bankResponseTimers = new HashMap<>();
    
    // Regional metrics for Indian cities
    private final Map<String, Counter> regionalCounters = new HashMap<>();
    
    // Business metrics for Indian context
    private final AtomicLong totalSuccessfulTransactions = new AtomicLong(0);
    private final AtomicLong totalFailedTransactions = new AtomicLong(0);
    private final AtomicInteger currentActiveUsers = new AtomicInteger(0);
    
    // UPI-specific failure tracking
    private final Map<String, AtomicLong> upiErrorTypes = new ConcurrentHashMap<>();
    
    // Indian bank list for UPI
    private static final List<String> INDIAN_BANKS = Arrays.asList(
        "SBI", "HDFC", "ICICI", "AXIS", "KOTAK", "YES_BANK", "BOI", "PNB", "CANARA", "IOB"
    );
    
    // Indian cities for regional metrics
    private static final List<String> INDIAN_CITIES = Arrays.asList(
        "MUMBAI", "BANGALORE", "DELHI", "CHENNAI", "KOLKATA", "HYDERABAD", 
        "PUNE", "AHMEDABAD", "JAIPUR", "LUCKNOW"
    );
    
    public MetricsCollectorUPI() {
        this.meterRegistry = new SimpleMeterRegistry();
        initializeMetrics();
        initializeBankMetrics();
        initializeRegionalMetrics();
        initializeUPIErrorTracking();
        
        logger.info("🚀 UPI Metrics Collector initialized for Indian market");
    }
    
    private void initializeMetrics() {
        // Main UPI transaction counter with tags
        this.upiTransactionCounter = Counter.builder("upi.transactions.total")
            .description("Total UPI transactions processed")
            .tag("country", "india")
            .tag("payment_method", "upi")
            .register(meterRegistry);
        
        // UPI transaction processing time
        this.upiTransactionTimer = Timer.builder("upi.transaction.duration")
            .description("UPI transaction processing time")
            .minimumExpectedValue(Duration.ofMillis(100))
            .maximumExpectedValue(Duration.ofSeconds(10))
            .sla(Duration.ofMillis(500), Duration.ofSeconds(1), Duration.ofSeconds(3))
            .register(meterRegistry);
        
        // UPI success rate gauge (dynamic calculation)
        this.upiSuccessRateGauge = Gauge.builder("upi.success.rate")
            .description("Current UPI success rate percentage")
            .register(meterRegistry, this, MetricsCollectorUPI::calculateSuccessRate);
        
        // UPI transaction amount distribution
        this.upiAmountSummary = DistributionSummary.builder("upi.transaction.amount")
            .description("UPI transaction amounts in INR")
            .baseUnit("INR")
            .minimumExpectedValue(1.0)
            .maximumExpectedValue(100000.0)
            .sla(100, 500, 1000, 5000, 10000, 50000)
            .register(meterRegistry);
        
        logger.info("📊 Core UPI metrics initialized");
    }
    
    private void initializeBankMetrics() {
        for (String bank : INDIAN_BANKS) {
            // Transaction counter per bank
            Counter bankCounter = Counter.builder("upi.bank.transactions")
                .description("UPI transactions per bank")
                .tag("bank", bank)
                .tag("country", "india")
                .register(meterRegistry);
            bankTransactionCounters.put(bank, bankCounter);
            
            // Response time per bank
            Timer bankTimer = Timer.builder("upi.bank.response.time")
                .description("Bank response time for UPI transactions")
                .tag("bank", bank)
                .minimumExpectedValue(Duration.ofMillis(50))
                .maximumExpectedValue(Duration.ofSeconds(5))
                .register(meterRegistry);
            bankResponseTimers.put(bank, bankTimer);
        }
        
        logger.info("🏦 Bank-specific metrics initialized for {} banks", INDIAN_BANKS.size());
    }
    
    private void initializeRegionalMetrics() {
        for (String city : INDIAN_CITIES) {
            Counter regionalCounter = Counter.builder("upi.regional.transactions")
                .description("UPI transactions per Indian city")
                .tag("city", city)
                .tag("country", "india")
                .register(meterRegistry);
            regionalCounters.put(city, regionalCounter);
        }
        
        logger.info("🗺️ Regional metrics initialized for {} cities", INDIAN_CITIES.size());
    }
    
    private void initializeUPIErrorTracking() {
        // Common UPI error types in India
        String[] errorTypes = {
            "INSUFFICIENT_BALANCE", "INVALID_VPA", "BANK_SERVER_ERROR", 
            "NETWORK_TIMEOUT", "INVALID_PIN", "DAILY_LIMIT_EXCEEDED",
            "BENEFICIARY_BANK_ERROR", "REMITTER_BANK_ERROR", "TECHNICAL_ERROR"
        };
        
        for (String errorType : errorTypes) {
            upiErrorTypes.put(errorType, new AtomicLong(0));
            
            // Create counter for each error type
            Counter.builder("upi.errors.total")
                .description("UPI errors by type")
                .tag("error_type", errorType)
                .tag("country", "india")
                .register(meterRegistry, upiErrorTypes.get(errorType));
        }
        
        logger.info("❌ UPI error tracking initialized for {} error types", errorTypes.length);
    }
    
    /**
     * Record a UPI transaction with comprehensive metrics
     */
    public void recordUPITransaction(UPITransaction transaction) {
        try {
            // Record basic transaction
            upiTransactionCounter.increment(
                Tags.of(
                    "status", transaction.isSuccessful() ? "success" : "failure",
                    "payment_type", transaction.getPaymentType(),
                    "user_type", transaction.getUserType()
                )
            );
            
            // Record transaction duration
            Duration duration = Duration.ofMillis(transaction.getProcessingTimeMs());
            upiTransactionTimer.record(duration, 
                Tags.of("bank", transaction.getBank(), "status", transaction.getStatus()));
            
            // Record transaction amount
            upiAmountSummary.record(transaction.getAmountINR());
            
            // Update success/failure counters
            if (transaction.isSuccessful()) {
                totalSuccessfulTransactions.incrementAndGet();
            } else {
                totalFailedTransactions.incrementAndGet();
                recordUPIError(transaction.getErrorType());
            }
            
            // Bank-specific metrics
            recordBankMetrics(transaction);
            
            // Regional metrics
            recordRegionalMetrics(transaction);
            
            // Business-specific metrics
            recordBusinessMetrics(transaction);
            
            logger.debug("📈 Recorded UPI transaction: {} INR via {} ({})", 
                transaction.getAmountINR(), transaction.getBank(), 
                transaction.isSuccessful() ? "SUCCESS" : "FAILED");
                
        } catch (Exception e) {
            logger.error("❌ Failed to record UPI transaction metrics", e);
        }
    }
    
    private void recordBankMetrics(UPITransaction transaction) {
        String bank = transaction.getBank();
        
        if (bankTransactionCounters.containsKey(bank)) {
            bankTransactionCounters.get(bank).increment(
                Tags.of("status", transaction.isSuccessful() ? "success" : "failure")
            );
        }
        
        if (bankResponseTimers.containsKey(bank)) {
            bankResponseTimers.get(bank).record(
                Duration.ofMillis(transaction.getProcessingTimeMs()),
                Tags.of("status", transaction.getStatus())
            );
        }
    }
    
    private void recordRegionalMetrics(UPITransaction transaction) {
        String city = transaction.getUserCity().toUpperCase();
        
        if (regionalCounters.containsKey(city)) {
            regionalCounters.get(city).increment(
                Tags.of(
                    "status", transaction.isSuccessful() ? "success" : "failure",
                    "payment_type", transaction.getPaymentType()
                )
            );
        }
    }
    
    private void recordBusinessMetrics(UPITransaction transaction) {
        // Festival season metrics
        if (isFestivalSeason()) {
            meterRegistry.counter("upi.festival.transactions", 
                "festival", getCurrentFestival(),
                "status", transaction.isSuccessful() ? "success" : "failure")
                .increment();
        }
        
        // Peak hour metrics
        if (isPeakHour()) {
            meterRegistry.counter("upi.peak.hour.transactions",
                "hour", String.valueOf(LocalDateTime.now().getHour()),
                "status", transaction.isSuccessful() ? "success" : "failure")
                .increment();
        }
        
        // High-value transaction metrics
        if (transaction.getAmountINR() >= 50000) {
            meterRegistry.counter("upi.high.value.transactions",
                "amount_range", "50000_plus",
                "status", transaction.isSuccessful() ? "success" : "failure")
                .increment();
        }
    }
    
    private void recordUPIError(String errorType) {
        if (errorType != null && upiErrorTypes.containsKey(errorType)) {
            upiErrorTypes.get(errorType).incrementAndGet();
        }
    }
    
    /**
     * Calculate current UPI success rate
     */
    private double calculateSuccessRate() {
        long successful = totalSuccessfulTransactions.get();
        long failed = totalFailedTransactions.get();
        long total = successful + failed;
        
        if (total == 0) return 100.0;
        
        return (double) successful / total * 100.0;
    }
    
    /**
     * Get comprehensive UPI metrics report
     */
    public UPIMetricsReport getMetricsReport() {
        UPIMetricsReport report = new UPIMetricsReport();
        
        // Basic metrics
        report.setTotalTransactions(totalSuccessfulTransactions.get() + totalFailedTransactions.get());
        report.setSuccessfulTransactions(totalSuccessfulTransactions.get());
        report.setFailedTransactions(totalFailedTransactions.get());
        report.setSuccessRate(calculateSuccessRate());
        
        // Bank performance
        Map<String, Double> bankPerformance = new HashMap<>();
        for (String bank : INDIAN_BANKS) {
            Counter counter = bankTransactionCounters.get(bank);
            if (counter != null) {
                bankPerformance.put(bank, counter.count());
            }
        }
        report.setBankTransactionCounts(bankPerformance);
        
        // Regional distribution
        Map<String, Double> regionalDistribution = new HashMap<>();
        for (String city : INDIAN_CITIES) {
            Counter counter = regionalCounters.get(city);
            if (counter != null) {
                regionalDistribution.put(city, counter.count());
            }
        }
        report.setRegionalDistribution(regionalDistribution);
        
        // Error analysis
        Map<String, Long> errorAnalysis = new HashMap<>();
        upiErrorTypes.forEach((errorType, counter) -> 
            errorAnalysis.put(errorType, counter.get()));
        report.setErrorAnalysis(errorAnalysis);
        
        return report;
    }
    
    /**
     * Start background metrics collection for system health
     */
    public void startHealthMetricsCollection() {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);
        
        // Collect system metrics every 30 seconds
        scheduler.scheduleAtFixedRate(this::collectSystemMetrics, 0, 30, TimeUnit.SECONDS);
        
        // Collect business metrics every minute
        scheduler.scheduleAtFixedRate(this::collectBusinessMetrics, 0, 1, TimeUnit.MINUTES);
        
        logger.info("⚡ Started background health metrics collection");
    }
    
    private void collectSystemMetrics() {
        try {
            // JVM metrics
            Runtime runtime = Runtime.getRuntime();
            long totalMemory = runtime.totalMemory();
            long freeMemory = runtime.freeMemory();
            long usedMemory = totalMemory - freeMemory;
            
            Gauge.builder("jvm.memory.used")
                .description("JVM used memory in bytes")
                .baseUnit("bytes")
                .register(meterRegistry, () -> usedMemory);
            
            Gauge.builder("jvm.memory.usage.percent")
                .description("JVM memory usage percentage")
                .register(meterRegistry, () -> (double) usedMemory / totalMemory * 100);
            
            // Active users gauge
            Gauge.builder("upi.active.users")
                .description("Current active UPI users")
                .register(meterRegistry, currentActiveUsers);
            
        } catch (Exception e) {
            logger.error("Failed to collect system metrics", e);
        }
    }
    
    private void collectBusinessMetrics() {
        try {
            // Transaction velocity (transactions per minute)
            double transactionVelocity = calculateTransactionVelocity();
            meterRegistry.gauge("upi.transaction.velocity", transactionVelocity);
            
            // Average transaction amount
            double avgAmount = calculateAverageTransactionAmount();
            meterRegistry.gauge("upi.transaction.avg.amount", avgAmount);
            
            // Peak load indicator
            boolean isPeak = isPeakHour();
            meterRegistry.gauge("upi.peak.hour.indicator", isPeak ? 1.0 : 0.0);
            
            logger.debug("📊 Collected business metrics - Velocity: {}, Avg Amount: ₹{}", 
                transactionVelocity, avgAmount);
                
        } catch (Exception e) {
            logger.error("Failed to collect business metrics", e);
        }
    }
    
    // Helper methods for business context
    private boolean isFestivalSeason() {
        int month = LocalDateTime.now().getMonthValue();
        // Diwali (Oct-Nov), Holi (Mar), Eid (varies), New Year (Dec-Jan)
        return month == 10 || month == 11 || month == 3 || month == 12 || month == 1;
    }
    
    private String getCurrentFestival() {
        int month = LocalDateTime.now().getMonthValue();
        switch (month) {
            case 10:
            case 11: return "DIWALI";
            case 3: return "HOLI";
            case 12:
            case 1: return "NEW_YEAR";
            default: return "NONE";
        }
    }
    
    private boolean isPeakHour() {
        int hour = LocalDateTime.now().getHour();
        // Peak UPI usage: 9-12 AM, 6-10 PM
        return (hour >= 9 && hour <= 12) || (hour >= 18 && hour <= 22);
    }
    
    private double calculateTransactionVelocity() {
        // Simplified calculation - in production, use time-windowed counters
        return (totalSuccessfulTransactions.get() + totalFailedTransactions.get()) / 60.0;
    }
    
    private double calculateAverageTransactionAmount() {
        // Simplified calculation - in production, maintain running average
        return 2500.0; // Average UPI transaction amount in India
    }
    
    /**
     * Export metrics in Prometheus format
     */
    public String exportPrometheusMetrics() {
        StringBuilder prometheus = new StringBuilder();
        
        // UPI transaction metrics
        prometheus.append("# HELP upi_transactions_total Total UPI transactions\n");
        prometheus.append("# TYPE upi_transactions_total counter\n");
        prometheus.append("upi_transactions_total{country=\"india\"} ")
            .append(totalSuccessfulTransactions.get() + totalFailedTransactions.get())
            .append("\n");
        
        prometheus.append("# HELP upi_success_rate UPI success rate percentage\n");
        prometheus.append("# TYPE upi_success_rate gauge\n");
        prometheus.append("upi_success_rate{country=\"india\"} ")
            .append(calculateSuccessRate())
            .append("\n");
        
        // Bank metrics
        prometheus.append("# HELP upi_bank_transactions UPI transactions per bank\n");
        prometheus.append("# TYPE upi_bank_transactions counter\n");
        for (Map.Entry<String, Counter> entry : bankTransactionCounters.entrySet()) {
            prometheus.append("upi_bank_transactions{bank=\"")
                .append(entry.getKey())
                .append("\",country=\"india\"} ")
                .append(entry.getValue().count())
                .append("\n");
        }
        
        return prometheus.toString();
    }
    
    // UPI Transaction model class
    public static class UPITransaction {
        private final String transactionId;
        private final double amountINR;
        private final String bank;
        private final String userCity;
        private final String paymentType;
        private final String userType;
        private final long processingTimeMs;
        private final boolean successful;
        private final String status;
        private final String errorType;
        
        public UPITransaction(String transactionId, double amountINR, String bank, 
                             String userCity, String paymentType, String userType,
                             long processingTimeMs, boolean successful, 
                             String status, String errorType) {
            this.transactionId = transactionId;
            this.amountINR = amountINR;
            this.bank = bank;
            this.userCity = userCity;
            this.paymentType = paymentType;
            this.userType = userType;
            this.processingTimeMs = processingTimeMs;
            this.successful = successful;
            this.status = status;
            this.errorType = errorType;
        }
        
        // Getters
        public String getTransactionId() { return transactionId; }
        public double getAmountINR() { return amountINR; }
        public String getBank() { return bank; }
        public String getUserCity() { return userCity; }
        public String getPaymentType() { return paymentType; }
        public String getUserType() { return userType; }
        public long getProcessingTimeMs() { return processingTimeMs; }
        public boolean isSuccessful() { return successful; }
        public String getStatus() { return status; }
        public String getErrorType() { return errorType; }
    }
    
    // Metrics report model
    public static class UPIMetricsReport {
        private long totalTransactions;
        private long successfulTransactions;
        private long failedTransactions;
        private double successRate;
        private Map<String, Double> bankTransactionCounts;
        private Map<String, Double> regionalDistribution;
        private Map<String, Long> errorAnalysis;
        
        // Getters and setters
        public long getTotalTransactions() { return totalTransactions; }
        public void setTotalTransactions(long totalTransactions) { this.totalTransactions = totalTransactions; }
        
        public long getSuccessfulTransactions() { return successfulTransactions; }
        public void setSuccessfulTransactions(long successfulTransactions) { this.successfulTransactions = successfulTransactions; }
        
        public long getFailedTransactions() { return failedTransactions; }
        public void setFailedTransactions(long failedTransactions) { this.failedTransactions = failedTransactions; }
        
        public double getSuccessRate() { return successRate; }
        public void setSuccessRate(double successRate) { this.successRate = successRate; }
        
        public Map<String, Double> getBankTransactionCounts() { return bankTransactionCounts; }
        public void setBankTransactionCounts(Map<String, Double> bankTransactionCounts) { this.bankTransactionCounts = bankTransactionCounts; }
        
        public Map<String, Double> getRegionalDistribution() { return regionalDistribution; }
        public void setRegionalDistribution(Map<String, Double> regionalDistribution) { this.regionalDistribution = regionalDistribution; }
        
        public Map<String, Long> getErrorAnalysis() { return errorAnalysis; }
        public void setErrorAnalysis(Map<String, Long> errorAnalysis) { this.errorAnalysis = errorAnalysis; }
        
        @Override
        public String toString() {
            return String.format("UPIMetricsReport{total=%d, successful=%d, failed=%d, successRate=%.2f%%}", 
                totalTransactions, successfulTransactions, failedTransactions, successRate);
        }
    }
    
    // Test method
    public static void main(String[] args) throws InterruptedException {
        MetricsCollectorUPI collector = new MetricsCollectorUPI();
        collector.startHealthMetricsCollection();
        
        System.out.println("🚀 Starting UPI metrics collection simulation...");
        
        // Simulate UPI transactions
        Random random = new Random();
        String[] banks = {"SBI", "HDFC", "ICICI", "AXIS", "KOTAK"};
        String[] cities = {"MUMBAI", "BANGALORE", "DELHI", "CHENNAI"};
        String[] paymentTypes = {"P2P", "P2M", "BILL_PAYMENT", "RECHARGE"};
        String[] userTypes = {"REGULAR", "PREMIUM", "MERCHANT"};
        String[] errorTypes = {"INSUFFICIENT_BALANCE", "NETWORK_TIMEOUT", "INVALID_VPA"};
        
        for (int i = 0; i < 1000; i++) {
            boolean successful = random.nextDouble() > 0.05; // 95% success rate
            
            UPITransaction transaction = new UPITransaction(
                "TXN" + (i + 1000000),
                random.nextDouble() * 10000 + 100, // ₹100 to ₹10,000
                banks[random.nextInt(banks.length)],
                cities[random.nextInt(cities.length)],
                paymentTypes[random.nextInt(paymentTypes.length)],
                userTypes[random.nextInt(userTypes.length)],
                random.nextLong() % 5000 + 500, // 500-5500ms processing time
                successful,
                successful ? "SUCCESS" : "FAILED",
                successful ? null : errorTypes[random.nextInt(errorTypes.length)]
            );
            
            collector.recordUPITransaction(transaction);
            
            if ((i + 1) % 100 == 0) {
                System.out.printf("✅ Processed %d transactions...\n", i + 1);
            }
            
            Thread.sleep(10); // Small delay to simulate real processing
        }
        
        // Generate report
        UPIMetricsReport report = collector.getMetricsReport();
        System.out.println("\n📊 UPI Metrics Report:");
        System.out.println("==========================================");
        System.out.println(report);
        System.out.println("\n🏦 Top Banks by Transaction Volume:");
        report.getBankTransactionCounts().entrySet().stream()
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
            .limit(5)
            .forEach(entry -> System.out.printf("   %s: %.0f transactions\n", 
                entry.getKey(), entry.getValue()));
        
        System.out.println("\n🗺️ Top Cities by Transaction Volume:");
        report.getRegionalDistribution().entrySet().stream()
            .sorted(Map.Entry.<String, Double>comparingByValue().reversed())
            .limit(5)
            .forEach(entry -> System.out.printf("   %s: %.0f transactions\n", 
                entry.getKey(), entry.getValue()));
        
        System.out.println("\n❌ Error Analysis:");
        report.getErrorAnalysis().forEach((errorType, count) -> 
            System.out.printf("   %s: %d occurrences\n", errorType, count));
        
        System.out.println("\n📈 Prometheus Metrics Export:");
        System.out.println(collector.exportPrometheusMetrics());
        
        System.out.println("\n🎉 UPI metrics collection simulation completed!");
    }
}