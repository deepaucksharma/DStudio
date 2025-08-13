/**
 * Indian Payment System Reliability Analyzer
 * ==========================================
 * 
 * Production-grade reliability analyzer for Indian payment systems.
 * Real examples: PhonePe, Paytm, GPay transaction success rate analysis
 * 
 * मुख्य concepts:
 * 1. Statistical reliability analysis using Java
 * 2. Indian payment gateway failure patterns
 * 3. Festival season impact modeling
 * 4. Real-time reliability monitoring
 * 
 * Mumbai analogy: Like analyzing Mumbai local train reliability patterns
 * Author: Hindi Tech Podcast Series
 */

import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.math.BigDecimal;
import java.math.RoundingMode;

// Hindi comments के साथ comprehensive payment reliability analyzer

/**
 * Individual payment transaction record
 * हर payment transaction का record
 */
class PaymentTransaction {
    private final String transactionId;
    private final String paymentProvider;    // PhonePe, Paytm, GPay, etc.
    private final BigDecimal amount;
    private final LocalDateTime timestamp;
    private final boolean successful;
    private final String failureReason;     // If failed
    private final Duration processingTime;
    private final String merchantCategory;   // Food, Shopping, Recharge, etc.
    
    // Indian context factors
    private final boolean isMonsoonSeason;
    private final boolean isFestivalSeason;
    private final boolean isPeakHour;
    private final String userLocation;      // Mumbai, Delhi, Bangalore, etc.
    
    public PaymentTransaction(String transactionId, String paymentProvider, BigDecimal amount,
                            LocalDateTime timestamp, boolean successful, String failureReason,
                            Duration processingTime, String merchantCategory,
                            boolean isMonsoonSeason, boolean isFestivalSeason, 
                            boolean isPeakHour, String userLocation) {
        this.transactionId = transactionId;
        this.paymentProvider = paymentProvider;
        this.amount = amount;
        this.timestamp = timestamp;
        this.successful = successful;
        this.failureReason = failureReason;
        this.processingTime = processingTime;
        this.merchantCategory = merchantCategory;
        this.isMonsoonSeason = isMonsoonSeason;
        this.isFestivalSeason = isFestivalSeason;
        this.isPeakHour = isPeakHour;
        this.userLocation = userLocation;
    }
    
    // Getters
    public String getTransactionId() { return transactionId; }
    public String getPaymentProvider() { return paymentProvider; }
    public BigDecimal getAmount() { return amount; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public boolean isSuccessful() { return successful; }
    public String getFailureReason() { return failureReason; }
    public Duration getProcessingTime() { return processingTime; }
    public String getMerchantCategory() { return merchantCategory; }
    public boolean isMonsoonSeason() { return isMonsoonSeason; }
    public boolean isFestivalSeason() { return isFestivalSeason; }
    public boolean isPeakHour() { return isPeakHour; }
    public String getUserLocation() { return userLocation; }
}

/**
 * Reliability metrics for a payment provider
 * Payment provider की reliability metrics
 */
class ReliabilityMetrics {
    private final String provider;
    private final long totalTransactions;
    private final long successfulTransactions;
    private final double successRate;
    private final Duration averageProcessingTime;
    private final BigDecimal totalVolume;
    
    // Indian context metrics
    private final double monsoonSuccessRate;
    private final double festivalSuccessRate;
    private final double peakHourSuccessRate;
    private final Map<String, Double> locationSuccessRates;
    
    public ReliabilityMetrics(String provider, long totalTransactions, 
                            long successfulTransactions, double successRate,
                            Duration averageProcessingTime, BigDecimal totalVolume,
                            double monsoonSuccessRate, double festivalSuccessRate,
                            double peakHourSuccessRate, Map<String, Double> locationSuccessRates) {
        this.provider = provider;
        this.totalTransactions = totalTransactions;
        this.successfulTransactions = successfulTransactions;
        this.successRate = successRate;
        this.averageProcessingTime = averageProcessingTime;
        this.totalVolume = totalVolume;
        this.monsoonSuccessRate = monsoonSuccessRate;
        this.festivalSuccessRate = festivalSuccessRate;
        this.peakHourSuccessRate = peakHourSuccessRate;
        this.locationSuccessRates = locationSuccessRates;
    }
    
    // Getters
    public String getProvider() { return provider; }
    public long getTotalTransactions() { return totalTransactions; }
    public long getSuccessfulTransactions() { return successfulTransactions; }
    public double getSuccessRate() { return successRate; }
    public Duration getAverageProcessingTime() { return averageProcessingTime; }
    public BigDecimal getTotalVolume() { return totalVolume; }
    public double getMonsoonSuccessRate() { return monsoonSuccessRate; }
    public double getFestivalSuccessRate() { return festivalSuccessRate; }
    public double getPeakHourSuccessRate() { return peakHourSuccessRate; }
    public Map<String, Double> getLocationSuccessRates() { return locationSuccessRates; }
}

/**
 * Main reliability analyzer class
 * मुख्य reliability analyzer class
 */
public class IndianPaymentReliabilityAnalyzer {
    
    private final List<PaymentTransaction> transactions;
    private final Map<String, ReliabilityMetrics> providerMetrics;
    
    // Indian cities with high payment volume
    private static final Set<String> MAJOR_INDIAN_CITIES = Set.of(
        "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", 
        "Pune", "Kolkata", "Ahmedabad", "Surat", "Jaipur"
    );
    
    // Festival seasons in India (month numbers)
    private static final Set<Integer> FESTIVAL_MONTHS = Set.of(3, 8, 10, 11); // Holi, Ganesh, Diwali, etc.
    
    // Monsoon season in India
    private static final Set<Integer> MONSOON_MONTHS = Set.of(6, 7, 8, 9); // June to September
    
    public IndianPaymentReliabilityAnalyzer() {
        this.transactions = Collections.synchronizedList(new ArrayList<>());
        this.providerMetrics = new ConcurrentHashMap<>();
        
        System.out.println("🇮🇳 Indian Payment Reliability Analyzer initialized");
        System.out.println("💳 Ready to analyze payment success patterns with Indian context!");
    }
    
    /**
     * Add a payment transaction for analysis
     * Analysis के लिए payment transaction add करते हैं
     */
    public void addTransaction(PaymentTransaction transaction) {
        transactions.add(transaction);
        
        // Auto-update metrics every 100 transactions
        if (transactions.size() % 100 == 0) {
            updateProviderMetrics();
        }
    }
    
    /**
     * Generate realistic Indian payment transactions for demo
     * Demo के लिए realistic Indian payment transactions generate करते हैं
     */
    public void generateDemoTransactions(int count) {
        System.out.println("📊 Generating " + count + " realistic Indian payment transactions...");
        
        String[] providers = {"PhonePe", "GooglePay", "Paytm", "BHIM", "PayU", "Razorpay"};
        String[] categories = {"Food", "Shopping", "Recharge", "Travel", "Utilities", "Healthcare"};
        String[] cities = MAJOR_INDIAN_CITIES.toArray(new String[0]);
        String[] failureReasons = {
            "NETWORK_ERROR", "BANK_TIMEOUT", "INSUFFICIENT_FUNDS", 
            "CARD_EXPIRED", "OTP_FAILURE", "SYSTEM_MAINTENANCE"
        };
        
        Random random = new Random();
        LocalDateTime startTime = LocalDateTime.now().minusDays(30); // Last 30 days
        
        for (int i = 0; i < count; i++) {
            // Random timestamp in last 30 days
            LocalDateTime timestamp = startTime.plusMinutes(random.nextInt(30 * 24 * 60));
            
            // Context factors
            boolean isMonsoon = MONSOON_MONTHS.contains(timestamp.getMonthValue());
            boolean isFestival = FESTIVAL_MONTHS.contains(timestamp.getMonthValue());
            boolean isPeakHour = isPeakHour(timestamp.getHour());
            
            String provider = providers[random.nextInt(providers.length)];
            String category = categories[random.nextInt(categories.length)];
            String city = cities[random.nextInt(cities.length)];
            
            // Amount based on category
            BigDecimal amount = generateRealisticAmount(category, random);
            
            // Success probability based on context
            double baseSuccessRate = getProviderBaseSuccessRate(provider);
            double contextAdjustedRate = adjustSuccessRateForContext(
                baseSuccessRate, isMonsoon, isFestival, isPeakHour, city, amount
            );
            
            boolean successful = random.nextDouble() < contextAdjustedRate;
            String failureReason = successful ? null : failureReasons[random.nextInt(failureReasons.length)];
            
            // Processing time (longer during peak hours and monsoon)
            int baseProcessingMs = 1500; // 1.5 seconds base
            if (isPeakHour) baseProcessingMs += 500;
            if (isMonsoon) baseProcessingMs += 800;
            if (isFestival) baseProcessingMs += 1200;
            if (!successful) baseProcessingMs += random.nextInt(3000); // Failures take longer
            
            Duration processingTime = Duration.ofMillis(
                baseProcessingMs + random.nextInt(2000) // Add some randomness
            );
            
            PaymentTransaction transaction = new PaymentTransaction(
                "TXN_" + System.currentTimeMillis() + "_" + i,
                provider, amount, timestamp, successful, failureReason,
                processingTime, category, isMonsoon, isFestival, isPeakHour, city
            );
            
            addTransaction(transaction);
        }
        
        System.out.println("✅ Generated " + count + " transactions successfully!");
    }
    
    /**
     * Check if given hour is peak hour for payments
     * Given hour peak hour है या नहीं check करते हैं
     */
    private boolean isPeakHour(int hour) {
        // Peak payment hours: 9-11 AM (office), 6-9 PM (evening), 12-2 PM (lunch)
        return (hour >= 9 && hour <= 11) || (hour >= 12 && hour <= 14) || (hour >= 18 && hour <= 21);
    }
    
    /**
     * Generate realistic amount based on merchant category
     * Category के अनुसार realistic amount generate करते हैं
     */
    private BigDecimal generateRealisticAmount(String category, Random random) {
        switch (category) {
            case "Food":
                return BigDecimal.valueOf(200 + random.nextInt(800)); // ₹200-1000
            case "Shopping":
                return BigDecimal.valueOf(500 + random.nextInt(4500)); // ₹500-5000
            case "Recharge":
                return BigDecimal.valueOf(50 + random.nextInt(450)); // ₹50-500
            case "Travel":
                return BigDecimal.valueOf(300 + random.nextInt(2700)); // ₹300-3000
            case "Utilities":
                return BigDecimal.valueOf(100 + random.nextInt(900)); // ₹100-1000
            case "Healthcare":
                return BigDecimal.valueOf(200 + random.nextInt(2800)); // ₹200-3000
            default:
                return BigDecimal.valueOf(100 + random.nextInt(900));
        }
    }
    
    /**
     * Get base success rate for each provider
     * हर provider का base success rate निकालते हैं
     */
    private double getProviderBaseSuccessRate(String provider) {
        // Based on real-world observations (approximate values)
        switch (provider) {
            case "PhonePe": return 0.982;   // 98.2%
            case "GooglePay": return 0.979; // 97.9%
            case "Paytm": return 0.971;     // 97.1%
            case "BHIM": return 0.968;      // 96.8%
            case "PayU": return 0.975;      // 97.5%
            case "Razorpay": return 0.977;  // 97.7%
            default: return 0.970;          // 97.0% default
        }
    }
    
    /**
     * Adjust success rate based on Indian context factors
     * Indian context के अनुसार success rate adjust करते हैं
     */
    private double adjustSuccessRateForContext(double baseRate, boolean isMonsoon, 
                                             boolean isFestival, boolean isPeakHour, 
                                             String city, BigDecimal amount) {
        double adjustedRate = baseRate;
        
        // Monsoon impact - network issues common during rains
        if (isMonsoon) {
            adjustedRate *= 0.94; // 6% decrease in success rate
        }
        
        // Festival impact - higher load, more failures
        if (isFestival) {
            adjustedRate *= 0.91; // 9% decrease during festivals
        }
        
        // Peak hour impact - server overload
        if (isPeakHour) {
            adjustedRate *= 0.96; // 4% decrease during peak hours
        }
        
        // City impact - tier 1 cities have better infrastructure
        if (Set.of("Mumbai", "Delhi", "Bangalore").contains(city)) {
            adjustedRate *= 1.02; // 2% bonus for tier 1 cities
        }
        
        // Amount impact - higher amounts have slightly lower success (more verification)
        if (amount.compareTo(BigDecimal.valueOf(2000)) > 0) {
            adjustedRate *= 0.98; // 2% decrease for high-value transactions
        }
        
        return Math.max(0.80, Math.min(1.0, adjustedRate)); // Keep between 80% and 100%
    }
    
    /**
     * Update provider-wise reliability metrics
     * Provider-wise reliability metrics update करते हैं
     */
    private void updateProviderMetrics() {
        Map<String, List<PaymentTransaction>> providerTransactions = transactions.stream()
            .collect(Collectors.groupingBy(PaymentTransaction::getPaymentProvider));
            
        for (Map.Entry<String, List<PaymentTransaction>> entry : providerTransactions.entrySet()) {
            String provider = entry.getKey();
            List<PaymentTransaction> providerTxns = entry.getValue();
            
            ReliabilityMetrics metrics = calculateMetricsForProvider(provider, providerTxns);
            providerMetrics.put(provider, metrics);
        }
    }
    
    /**
     * Calculate comprehensive metrics for a payment provider
     * Payment provider के लिए comprehensive metrics calculate करते हैं
     */
    private ReliabilityMetrics calculateMetricsForProvider(String provider, 
                                                         List<PaymentTransaction> providerTxns) {
        long totalTxns = providerTxns.size();
        long successfulTxns = providerTxns.stream()
            .mapToLong(txn -> txn.isSuccessful() ? 1 : 0)
            .sum();
            
        double successRate = (double) successfulTxns / totalTxns;
        
        // Average processing time
        Duration avgProcessingTime = Duration.ofMillis(
            (long) providerTxns.stream()
                .mapToLong(txn -> txn.getProcessingTime().toMillis())
                .average()
                .orElse(0)
        );
        
        // Total volume
        BigDecimal totalVolume = providerTxns.stream()
            .map(PaymentTransaction::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
            
        // Context-specific success rates
        double monsoonSuccessRate = calculateContextualSuccessRate(providerTxns, 
            txn -> txn.isMonsoonSeason());
        double festivalSuccessRate = calculateContextualSuccessRate(providerTxns,
            txn -> txn.isFestivalSeason());
        double peakHourSuccessRate = calculateContextualSuccessRate(providerTxns,
            txn -> txn.isPeakHour());
            
        // Location-wise success rates
        Map<String, Double> locationSuccessRates = new HashMap<>();
        for (String city : MAJOR_INDIAN_CITIES) {
            locationSuccessRates.put(city, calculateContextualSuccessRate(providerTxns,
                txn -> city.equals(txn.getUserLocation())));
        }
        
        return new ReliabilityMetrics(provider, totalTxns, successfulTxns, successRate,
                                    avgProcessingTime, totalVolume, monsoonSuccessRate,
                                    festivalSuccessRate, peakHourSuccessRate, locationSuccessRates);
    }
    
    /**
     * Calculate success rate for transactions matching a specific condition
     * Specific condition के लिए success rate calculate करते हैं
     */
    private double calculateContextualSuccessRate(List<PaymentTransaction> transactions,
                                                java.util.function.Predicate<PaymentTransaction> condition) {
        List<PaymentTransaction> filteredTxns = transactions.stream()
            .filter(condition)
            .collect(Collectors.toList());
            
        if (filteredTxns.isEmpty()) {
            return 0.0;
        }
        
        long successful = filteredTxns.stream()
            .mapToLong(txn -> txn.isSuccessful() ? 1 : 0)
            .sum();
            
        return (double) successful / filteredTxns.size();
    }
    
    /**
     * Generate comprehensive reliability report
     * Comprehensive reliability report generate करते हैं
     */
    public String generateReliabilityReport() {
        updateProviderMetrics(); // Ensure latest metrics
        
        StringBuilder report = new StringBuilder();
        report.append("🇮🇳 INDIAN PAYMENT SYSTEM RELIABILITY REPORT\n");
        report.append("=".repeat(60)).append("\n");
        report.append("📊 Total Transactions Analyzed: ").append(transactions.size()).append("\n");
        report.append("💳 Payment Providers: ").append(providerMetrics.size()).append("\n");
        report.append("📅 Report Generated: ").append(
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        ).append(" IST\n\n");
        
        // Overall statistics
        report.append("📈 OVERALL STATISTICS\n");
        report.append("-".repeat(40)).append("\n");
        
        long totalSuccessful = transactions.stream()
            .mapToLong(txn -> txn.isSuccessful() ? 1 : 0)
            .sum();
        double overallSuccessRate = (double) totalSuccessful / transactions.size();
        
        report.append("Overall Success Rate: ").append(String.format("%.2f%%", overallSuccessRate * 100)).append("\n");
        
        BigDecimal totalVolume = transactions.stream()
            .map(PaymentTransaction::getAmount)
            .reduce(BigDecimal.ZERO, BigDecimal::add);
        report.append("Total Transaction Volume: ₹").append(totalVolume.toString()).append("\n");
        
        Duration avgProcessingTime = Duration.ofMillis(
            (long) transactions.stream()
                .mapToLong(txn -> txn.getProcessingTime().toMillis())
                .average()
                .orElse(0)
        );
        report.append("Average Processing Time: ").append(avgProcessingTime.toMillis()).append("ms\n\n");
        
        // Provider-wise analysis
        report.append("💳 PROVIDER-WISE ANALYSIS\n");
        report.append("-".repeat(40)).append("\n");
        
        // Sort providers by success rate
        List<ReliabilityMetrics> sortedProviders = providerMetrics.values().stream()
            .sorted((a, b) -> Double.compare(b.getSuccessRate(), a.getSuccessRate()))
            .collect(Collectors.toList());
            
        for (int i = 0; i < sortedProviders.size(); i++) {
            ReliabilityMetrics metrics = sortedProviders.get(i);
            report.append("\n").append(i + 1).append(". ").append(metrics.getProvider()).append("\n");
            report.append("   Success Rate: ").append(String.format("%.2f%%", metrics.getSuccessRate() * 100)).append("\n");
            report.append("   Total Transactions: ").append(metrics.getTotalTransactions()).append("\n");
            report.append("   Avg Processing Time: ").append(metrics.getAverageProcessingTime().toMillis()).append("ms\n");
            report.append("   Total Volume: ₹").append(metrics.getTotalVolume()).append("\n");
        }
        
        // Indian context analysis
        report.append("\n\n🇮🇳 INDIAN CONTEXT ANALYSIS\n");
        report.append("-".repeat(40)).append("\n");
        
        // Monsoon impact
        double monsoonSuccessRate = calculateContextualSuccessRate(transactions, 
            PaymentTransaction::isMonsoonSeason);
        double normalSuccessRate = calculateContextualSuccessRate(transactions, 
            txn -> !txn.isMonsoonSeason());
        
        report.append("🌧️ Monsoon Season Impact:\n");
        report.append("   Success Rate (Monsoon): ").append(String.format("%.2f%%", monsoonSuccessRate * 100)).append("\n");
        report.append("   Success Rate (Normal): ").append(String.format("%.2f%%", normalSuccessRate * 100)).append("\n");
        report.append("   Impact: ").append(String.format("%.1f%%", (normalSuccessRate - monsoonSuccessRate) * 100))
            .append(" decrease during monsoon\n\n");
        
        // Festival impact
        double festivalSuccessRate = calculateContextualSuccessRate(transactions,
            PaymentTransaction::isFestivalSeason);
        report.append("🎉 Festival Season Impact:\n");
        report.append("   Success Rate (Festival): ").append(String.format("%.2f%%", festivalSuccessRate * 100)).append("\n");
        report.append("   Success Rate (Normal): ").append(String.format("%.2f%%", normalSuccessRate * 100)).append("\n");
        report.append("   Impact: ").append(String.format("%.1f%%", (normalSuccessRate - festivalSuccessRate) * 100))
            .append(" decrease during festivals\n\n");
        
        // Peak hour impact
        double peakHourSuccessRate = calculateContextualSuccessRate(transactions,
            PaymentTransaction::isPeakHour);
        report.append("⏰ Peak Hour Impact:\n");
        report.append("   Success Rate (Peak): ").append(String.format("%.2f%%", peakHourSuccessRate * 100)).append("\n");
        report.append("   Success Rate (Off-peak): ").append(String.format("%.2f%%", normalSuccessRate * 100)).append("\n");
        report.append("   Impact: ").append(String.format("%.1f%%", (normalSuccessRate - peakHourSuccessRate) * 100))
            .append(" decrease during peak hours\n\n");
        
        // Mumbai analogies and insights
        report.append("🏙️ MUMBAI ANALOGIES & INSIGHTS\n");
        report.append("-".repeat(40)).append("\n");
        report.append("🚊 Like Mumbai local trains:\n");
        report.append("   • Normal days: High reliability (").append(String.format("%.1f%%", normalSuccessRate * 100)).append(")\n");
        report.append("   • Monsoon days: Reduced reliability (").append(String.format("%.1f%%", monsoonSuccessRate * 100)).append(")\n");
        report.append("   • Peak hours: System stress affects performance\n");
        report.append("   • Festival seasons: Overload causes disruptions\n\n");
        
        // Recommendations
        report.append("💡 ACTIONABLE RECOMMENDATIONS\n");
        report.append("-".repeat(40)).append("\n");
        
        if (monsoonSuccessRate < 0.95) {
            report.append("🌧️ Monsoon Preparation:\n");
            report.append("   • Increase timeout values during monsoon months\n");
            report.append("   • Implement retry mechanisms for network failures\n");
            report.append("   • Set up alternate connectivity for critical transactions\n\n");
        }
        
        if (festivalSuccessRate < 0.95) {
            report.append("🎉 Festival Season Preparation:\n");
            report.append("   • Scale up infrastructure during festival months\n");
            report.append("   • Implement queue management for high load\n");
            report.append("   • Pre-load balance payment gateways\n\n");
        }
        
        if (peakHourSuccessRate < 0.96) {
            report.append("⏰ Peak Hour Optimization:\n");
            report.append("   • Auto-scaling based on transaction volume\n");
            report.append("   • Load balancing across multiple payment providers\n");
            report.append("   • Implement priority queues for critical transactions\n\n");
        }
        
        report.append("🎯 Remember: Like Mumbai's resilient systems, plan for the worst-case scenarios!\n");
        report.append("🚀 Happy payment processing! May your success rates be higher than Mumbai local train punctuality!");
        
        return report.toString();
    }
    
    /**
     * Main method for demonstration
     * Demo के लिए main method
     */
    public static void main(String[] args) {
        System.out.println("🚀 Starting Indian Payment Reliability Analysis Demo");
        System.out.println("=".repeat(60));
        
        // Create analyzer
        IndianPaymentReliabilityAnalyzer analyzer = new IndianPaymentReliabilityAnalyzer();
        
        // Generate demo transactions
        analyzer.generateDemoTransactions(2000);
        
        // Generate and print report
        System.out.println("📋 GENERATING COMPREHENSIVE RELIABILITY REPORT...\n");
        String report = analyzer.generateReliabilityReport();
        System.out.println(report);
        
        System.out.println("\n🎉 Payment reliability analysis completed!");
        System.out.println("🏙️ Just like analyzing Mumbai traffic patterns - data reveals insights!");
        System.out.println("💡 Use this analysis to improve payment system reliability!");
    }
}