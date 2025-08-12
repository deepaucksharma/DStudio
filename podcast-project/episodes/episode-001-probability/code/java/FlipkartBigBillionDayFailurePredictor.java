/**
 * Flipkart Big Billion Day System Failure Predictor
 * फ्लिपकार्ट बिग बिलियन डे के दौरान system failures का probability analysis
 * 
 * Indian Context: E-commerce flash sales के दौरान server overload prediction
 * Mumbai Example: Dharavi के electronics market में Diwali sale की crowd analysis
 */

import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;

public class FlipkartBigBillionDayFailurePredictor {
    
    // Flipkart system components की realistic capacity limits
    private static final int MAX_CONCURRENT_USERS = 50_000_000;  // 5 crore concurrent users
    private static final int DATABASE_CONNECTION_POOL = 10000;    // DB connection limit
    private static final int PAYMENT_GATEWAY_TPS = 50000;        // Transactions per second
    private static final int INVENTORY_SERVICE_RPS = 100000;     // Requests per second
    
    // Big Billion Day के specific timings
    private static final List<LocalTime> FLASH_SALE_TIMINGS = Arrays.asList(
        LocalTime.of(0, 0),   // Midnight flash sale
        LocalTime.of(8, 0),   // Morning office hours
        LocalTime.of(12, 0),  // Lunch break shopping
        LocalTime.of(18, 0),  // Evening rush
        LocalTime.of(21, 0)   // Night prime time
    );
    
    // Product categories और उनके popularity patterns
    private enum ProductCategory {
        SMARTPHONES(0.85, 15.0),    // 85% traffic, 15x normal demand
        ELECTRONICS(0.70, 12.0),   // Electronics high demand
        FASHION(0.60, 8.0),        // Fashion moderate demand  
        HOME_KITCHEN(0.45, 5.0),   // Home appliances steady
        BOOKS(0.30, 2.0);          // Books low demand multiplier
        
        public final double trafficShare;
        public final double demandMultiplier;
        
        ProductCategory(double trafficShare, double demandMultiplier) {
            this.trafficShare = trafficShare;
            this.demandMultiplier = demandMultiplier;
        }
    }
    
    // System failure types जो Big Billion Day में common होते हैं
    private enum FailureType {
        DATABASE_OVERLOAD("Database connection pool exhausted", 0.25),
        PAYMENT_TIMEOUT("Payment gateway timeout", 0.20),
        INVENTORY_SYNC_FAIL("Inventory service synchronization failed", 0.18),
        CDN_SLOWDOWN("Content delivery network slowdown", 0.15),
        CACHE_MISS_STORM("Cache miss storm causing DB overload", 0.12),
        THIRD_PARTY_API_FAIL("Third party service (logistics/payment) failure", 0.10);
        
        public final String description;
        public final double probability;
        
        FailureType(String description, double probability) {
            this.description = description;
            this.probability = probability;
        }
    }
    
    private final Random random = new Random();
    
    /**
     * Big Billion Day के दौरान system failure probability calculator
     * 
     * @param currentUsers Currently active users
     * @param category Product category being accessed
     * @param currentTime Current timestamp
     * @param isFlashSale Whether it's flash sale timing
     * @return Failure probability between 0.0 and 1.0
     */
    public double calculateFailureProbability(long currentUsers, 
                                            ProductCategory category,
                                            LocalDateTime currentTime,
                                            boolean isFlashSale) {
        
        // Base failure probability - Flipkart normal day का baseline
        double baseFailureRate = 0.02; // 2% normal failure rate
        
        // User load factor - Mumbai local train capacity की तरह
        double userLoadFactor = Math.min((double) currentUsers / MAX_CONCURRENT_USERS, 3.0);
        double loadMultiplier = 1.0 + (userLoadFactor * 2.0); // Max 7x multiplier
        
        // Category demand multiplier
        double categoryMultiplier = category.demandMultiplier / 10.0; // Normalize करें
        
        // Flash sale timing multiplier - Tatkal ticket booking की तरह chaos
        double flashSaleMultiplier = isFlashSale ? 5.0 : 1.0;
        
        // Time of day multiplier - Indian shopping patterns
        double timeMultiplier = getTimeOfDayMultiplier(currentTime.toLocalTime());
        
        // Day of sale multiplier - Big Billion Day specific
        double saleMultiplier = isBigBillionDayPeak(currentTime) ? 3.0 : 1.5;
        
        // Final probability calculation
        double failureProbability = baseFailureRate * loadMultiplier * 
                                  categoryMultiplier * flashSaleMultiplier * 
                                  timeMultiplier * saleMultiplier;
        
        // Cap at maximum 90% failure rate
        return Math.min(failureProbability, 0.9);
    }
    
    /**
     * Time of day के अनुसार multiplier calculate करता है
     * Indian shopping patterns को consider करता है
     */
    private double getTimeOfDayMultiplier(LocalTime time) {
        int hour = time.getHour();
        
        // Peak shopping hours - office lunch breaks और evening
        if ((hour >= 12 && hour <= 14) || (hour >= 19 && hour <= 23)) {
            return 2.5; // Peak hours
        }
        // Late night shopping - insomniacs और serious shoppers
        else if (hour >= 0 && hour <= 2) {
            return 2.0; // Midnight rush
        }
        // Morning hours - moderate activity
        else if (hour >= 8 && hour <= 11) {
            return 1.5; // Morning shoppers
        }
        // Off-peak hours
        else {
            return 1.0; // Normal activity
        }
    }
    
    /**
     * Check if current time is Big Billion Day peak period
     */
    private boolean isBigBillionDayPeak(LocalDateTime dateTime) {
        int dayOfMonth = dateTime.getDayOfMonth();
        int hour = dateTime.getHour();
        
        // Usually Big Billion Day starts from October month
        return dateTime.getMonth() == Month.OCTOBER && 
               dayOfMonth >= 1 && dayOfMonth <= 7 &&  // First week of October
               hour >= 0 && hour <= 23; // Entire day is peak
    }
    
    /**
     * Specific failure type predict करता है based on current conditions
     */
    public FailureType predictFailureType(double failureProbability) {
        double rand = random.nextDouble();
        double cumulative = 0.0;
        
        for (FailureType type : FailureType.values()) {
            cumulative += type.probability;
            if (rand <= cumulative && failureProbability > 0.1) {
                return type;
            }
        }
        
        return FailureType.DATABASE_OVERLOAD; // Default fallback
    }
    
    /**
     * Monte Carlo simulation for Big Billion Day performance prediction
     */
    public SimulationResult runMonteCarloSimulation(int simulationCount, 
                                                   ProductCategory category,
                                                   boolean enableFlashSales) {
        
        System.out.println("🛒 Flipkart Big Billion Day Simulation शुरू हो रहा है...");
        System.out.println("📱 Category: " + category.name());
        System.out.println("⚡ Flash Sales: " + (enableFlashSales ? "Enabled" : "Disabled"));
        System.out.println("🔢 Simulations: " + simulationCount);
        
        List<SimulationData> results = new ArrayList<>();
        Map<FailureType, Integer> failureDistribution = new HashMap<>();
        int totalFailures = 0;
        double totalResponseTime = 0.0;
        
        for (int i = 0; i < simulationCount; i++) {
            // Random simulation parameters
            long currentUsers = generateRealisticUserCount();
            LocalDateTime simulationTime = generateRandomBigBillionDayTime();
            boolean isFlashSale = enableFlashSales && isFlashSaleTiming(simulationTime.toLocalTime());
            
            // Calculate failure probability
            double failureProbability = calculateFailureProbability(
                currentUsers, category, simulationTime, isFlashSale
            );
            
            // Determine if failure occurs
            boolean systemFailed = random.nextDouble() < failureProbability;
            FailureType failureType = null;
            double responseTime = generateResponseTime(systemFailed);
            
            if (systemFailed) {
                totalFailures++;
                failureType = predictFailureType(failureProbability);
                failureDistribution.merge(failureType, 1, Integer::sum);
            }
            
            totalResponseTime += responseTime;
            
            results.add(new SimulationData(currentUsers, simulationTime, 
                       failureProbability, systemFailed, failureType, responseTime));
            
            // Progress indicator
            if ((i + 1) % 1000 == 0) {
                System.out.println("✅ Completed " + (i + 1) + " simulations...");
            }
        }
        
        // Calculate final statistics
        double successRate = 1.0 - ((double) totalFailures / simulationCount);
        double avgResponseTime = totalResponseTime / simulationCount;
        
        return new SimulationResult(simulationCount, successRate, avgResponseTime, 
                                  failureDistribution, results);
    }
    
    /**
     * Realistic user count generate करता है Big Billion Day patterns के basis पर
     */
    private long generateRealisticUserCount() {
        // Big Billion Day पर traffic patterns
        double[] distribution = {0.1, 0.2, 0.3, 0.25, 0.15}; // 5 buckets
        long[] userRanges = {
            1_000_000,   // 10 lakh users
            5_000_000,   // 50 lakh users  
            15_000_000,  // 1.5 crore users (peak)
            25_000_000,  // 2.5 crore users (super peak)
            40_000_000   // 4 crore users (maximum)
        };
        
        double rand = random.nextDouble();
        double cumulative = 0.0;
        
        for (int i = 0; i < distribution.length; i++) {
            cumulative += distribution[i];
            if (rand <= cumulative) {
                long baseUsers = userRanges[i];
                // Add some randomness
                return baseUsers + random.nextLong(baseUsers / 4);
            }
        }
        
        return 1_000_000; // Default fallback
    }
    
    /**
     * Random Big Billion Day timestamp generate करता है
     */
    private LocalDateTime generateRandomBigBillionDayTime() {
        LocalDate saleDate = LocalDate.of(2024, Month.OCTOBER, 
                                        1 + random.nextInt(7)); // First week of October
        
        LocalTime saleTime = LocalTime.of(random.nextInt(24), 
                                        random.nextInt(60));
        
        return LocalDateTime.of(saleDate, saleTime);
    }
    
    /**
     * Check if given time is flash sale timing
     */
    private boolean isFlashSaleTiming(LocalTime time) {
        return FLASH_SALE_TIMINGS.stream()
                .anyMatch(flashTime -> 
                    Math.abs(Duration.between(time, flashTime).toMinutes()) <= 30
                );
    }
    
    /**
     * Response time generate करता है based on system state
     */
    private double generateResponseTime(boolean systemFailed) {
        if (systemFailed) {
            // Failure scenarios में high response time या timeout
            return 10.0 + random.nextDouble() * 20.0; // 10-30 seconds
        } else {
            // Normal scenarios में fast response
            return 0.5 + random.nextDouble() * 2.0;    // 0.5-2.5 seconds
        }
    }
    
    // Data classes for simulation results
    static class SimulationData {
        final long userCount;
        final LocalDateTime timestamp;
        final double failureProbability;
        final boolean systemFailed;
        final FailureType failureType;
        final double responseTime;
        
        SimulationData(long userCount, LocalDateTime timestamp, double failureProbability,
                      boolean systemFailed, FailureType failureType, double responseTime) {
            this.userCount = userCount;
            this.timestamp = timestamp;
            this.failureProbability = failureProbability;
            this.systemFailed = systemFailed;
            this.failureType = failureType;
            this.responseTime = responseTime;
        }
    }
    
    static class SimulationResult {
        final int totalSimulations;
        final double successRate;
        final double avgResponseTime;
        final Map<FailureType, Integer> failureDistribution;
        final List<SimulationData> detailedResults;
        
        SimulationResult(int totalSimulations, double successRate, double avgResponseTime,
                        Map<FailureType, Integer> failureDistribution, 
                        List<SimulationData> detailedResults) {
            this.totalSimulations = totalSimulations;
            this.successRate = successRate;
            this.avgResponseTime = avgResponseTime;
            this.failureDistribution = failureDistribution;
            this.detailedResults = detailedResults;
        }
    }
    
    public static void main(String[] args) {
        System.out.println("🛍️ Flipkart Big Billion Day Failure Prediction Analysis");
        System.out.println("=" + "=".repeat(60));
        
        FlipkartBigBillionDayFailurePredictor predictor = 
            new FlipkartBigBillionDayFailurePredictor();
        
        // Smartphone category analysis (highest traffic)
        System.out.println("\n📱 Smartphone Category Analysis:");
        SimulationResult smartphoneResults = predictor.runMonteCarloSimulation(
            10000, ProductCategory.SMARTPHONES, true
        );
        
        System.out.println("\n📊 Simulation Results:");
        System.out.println("✅ Success Rate: " + 
                          String.format("%.2f%%", smartphoneResults.successRate * 100));
        System.out.println("❌ Failure Rate: " + 
                          String.format("%.2f%%", (1 - smartphoneResults.successRate) * 100));
        System.out.println("⏱️  Average Response Time: " + 
                          String.format("%.2f seconds", smartphoneResults.avgResponseTime));
        
        // Failure type distribution
        System.out.println("\n🚨 Failure Type Distribution:");
        smartphoneResults.failureDistribution.entrySet().stream()
            .sorted(Map.Entry.<FailureType, Integer>comparingByValue().reversed())
            .forEach(entry -> {
                double percentage = (entry.getValue() * 100.0) / 
                                  smartphoneResults.totalSimulations;
                System.out.println(String.format("   %s: %d occurrences (%.1f%%)",
                    entry.getKey().name(), entry.getValue(), percentage));
                System.out.println("     └─ " + entry.getKey().description);
            });
        
        // Business impact analysis
        long estimatedUsers = 30_000_000; // 3 crore users on Big Billion Day
        double avgOrderValue = 2500.0; // ₹2500 average order
        double revenueImpact = estimatedUsers * (1 - smartphoneResults.successRate) * avgOrderValue;
        
        System.out.println("\n💰 Business Impact Analysis:");
        System.out.println("   📈 Estimated Big Billion Day Users: " + 
                          String.format("%,d", estimatedUsers));
        System.out.println("   🛒 Average Order Value: ₹" + 
                          String.format("%.0f", avgOrderValue));
        System.out.println("   💸 Potential Revenue Loss: ₹" + 
                          String.format("%,.0f crores", revenueImpact / 10_000_000));
        
        // Mumbai analogy
        System.out.println("\n🏙️ Mumbai Local Train Analogy:");
        System.out.println("   Flipkart servers = Mumbai local train coaches");
        System.out.println("   Big Billion Day traffic = Festival crowd at Dadar station");
        System.out.println("   Flash sales = Last train to Virar (everyone rushing)");
        System.out.println("   Payment gateway = Ticket window (limited capacity)");
        System.out.println("   Database overload = Platform overcrowding");
        
        // Technical recommendations
        System.out.println("\n🔧 Technical Recommendations:");
        System.out.println("   1. Pre-scale infrastructure by 5x before Big Billion Day");
        System.out.println("   2. Implement queue-based processing for flash sales");
        System.out.println("   3. Use circuit breakers for payment gateway timeouts");
        System.out.println("   4. Add CDN caching for product images and static content");
        System.out.println("   5. Implement database read replicas for inventory checks");
    }
}