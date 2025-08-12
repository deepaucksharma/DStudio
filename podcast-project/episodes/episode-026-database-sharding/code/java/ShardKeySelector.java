/**
 * Optimal Shard Key Selection for Indian E-commerce
 * भारतीय ई-कॉमर्स के लिए optimal shard key selection
 * 
 * यह class दिखाती है कि कैसे different business scenarios के लिए
 * optimal shard keys select करें - Flipkart/Amazon जैसे platforms के लिए
 */

import java.util.*;
import java.util.stream.Collectors;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class ShardKeySelector {
    
    // Shard configuration for Indian e-commerce
    private static final Map<String, ShardConfig> SHARD_CONFIGS = Map.of(
        "user_shard", new ShardConfig("user_shard", "users-db.flipkart.com", 1000000),
        "order_shard", new ShardConfig("order_shard", "orders-db.flipkart.com", 5000000),  
        "product_shard", new ShardConfig("product_shard", "products-db.flipkart.com", 2000000),
        "payment_shard", new ShardConfig("payment_shard", "payments-db.flipkart.com", 3000000),
        "inventory_shard", new ShardConfig("inventory_shard", "inventory-db.flipkart.com", 1500000)
    );
    
    /**
     * Shard configuration class
     */
    public static class ShardConfig {
        public final String name;
        public final String host;
        public final int capacity;
        
        public ShardConfig(String name, String host, int capacity) {
            this.name = name;
            this.host = host;
            this.capacity = capacity;
        }
        
        @Override
        public String toString() {
            return String.format("Shard{name=%s, host=%s, capacity=%d}", name, host, capacity);
        }
    }
    
    /**
     * Shard key analysis result
     */
    public static class ShardKeyAnalysis {
        public final String keyName;
        public final double distributionScore;  // 0-100, higher is better
        public final double queryEfficiency;   // 0-100, higher is better  
        public final double hotspotRisk;       // 0-100, lower is better
        public final String recommendation;
        
        public ShardKeyAnalysis(String keyName, double distributionScore, 
                              double queryEfficiency, double hotspotRisk, String recommendation) {
            this.keyName = keyName;
            this.distributionScore = distributionScore;
            this.queryEfficiency = queryEfficiency;
            this.hotspotRisk = hotspotRisk;
            this.recommendation = recommendation;
        }
    }
    
    /**
     * User shard key selector - यूजर डेटा के लिए optimal key
     */
    public static class UserShardKeySelector {
        
        public ShardKeyAnalysis analyzeUserIdSharding(List<String> userIds) {
            // User ID based sharding analysis
            System.out.println("\n🔍 User ID Sharding Analysis (यूजर ID शार्डिंग विश्लेषण):");
            
            // Calculate distribution uniformity
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String userId : userIds) {
                int shardId = getShardId(userId, 4);
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, userIds.size());
            double queryEfficiency = 95.0; // High for user lookups
            double hotspotRisk = 15.0;     // Low risk with good hash function
            
            String recommendation = distributionScore > 80 ? 
                "✅ Recommended: Excellent for user lookups और profile queries" :
                "⚠️ Consider composite key: user_id + registration_date";
            
            return new ShardKeyAnalysis("user_id", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
        
        public ShardKeyAnalysis analyzePincodeSharding(List<String> pincodes) {
            // PIN code based sharding analysis  
            System.out.println("\n📍 Pincode Sharding Analysis (पिन कोड शार्डिंग विश्लेषण):");
            
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String pincode : pincodes) {
                int shardId = getShardId(pincode, 4);
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, pincodes.size());
            double queryEfficiency = 85.0; // Good for geo queries
            double hotspotRisk = 35.0;     // Medium risk due to population density
            
            String recommendation = "🏙️ Good for geo-based queries लेकिन metro cities में hotspots possible";
            
            return new ShardKeyAnalysis("pincode", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
        
        public ShardKeyAnalysis analyzePhoneSharding(List<String> phoneNumbers) {
            // Phone number based sharding analysis
            System.out.println("\n📱 Phone Number Sharding Analysis (फोन नंबर शार्डिंग विश्लेषण):");
            
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String phone : phoneNumbers) {
                int shardId = getShardId(phone, 4);
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, phoneNumbers.size());
            double queryEfficiency = 90.0; // High for OTP and verification
            double hotspotRisk = 25.0;     // Medium-low risk
            
            String recommendation = "📞 Excellent for OTP services और user verification workflows";
            
            return new ShardKeyAnalysis("phone_number", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
    }
    
    /**
     * Order shard key selector - ऑर्डर डेटा के लिए optimal key
     */
    public static class OrderShardKeySelector {
        
        public ShardKeyAnalysis analyzeOrderIdSharding(List<String> orderIds) {
            System.out.println("\n📦 Order ID Sharding Analysis (ऑर्डर ID शार्डिंग विश्लेषण):");
            
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String orderId : orderIds) {
                int shardId = getShardId(orderId, 8);
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, orderIds.size());
            double queryEfficiency = 95.0; // Excellent for order tracking
            double hotspotRisk = 10.0;     // Very low with UUID-based orders
            
            String recommendation = "🎯 Perfect for order tracking और individual order queries";
            
            return new ShardKeyAnalysis("order_id", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
        
        public ShardKeyAnalysis analyzeUserIdSharding(List<String> userIds) {
            System.out.println("\n👤 User-based Order Sharding (यूजर आधारित ऑर्डर शार्डिंग):");
            
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String userId : userIds) {
                int shardId = getShardId(userId, 6);
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, userIds.size());
            double queryEfficiency = 75.0; // Good for user order history
            double hotspotRisk = 40.0;     // High risk with power users
            
            String recommendation = "⚡ Good for 'my orders' queries लेकिन power users से hotspot risk";
            
            return new ShardKeyAnalysis("user_id_orders", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
        
        public ShardKeyAnalysis analyzeDateSharding(List<String> dates) {
            System.out.println("\n📅 Date-based Order Sharding (तारीख आधारित ऑर्डर शार्डिंग):");
            
            Map<Integer, Integer> shardDistribution = new HashMap<>();
            for (String date : dates) {
                int shardId = getShardId(date, 12); // Monthly sharding
                shardDistribution.put(shardId, shardDistribution.getOrDefault(shardId, 0) + 1);
            }
            
            double distributionScore = calculateDistributionScore(shardDistribution, dates.size());
            double queryEfficiency = 60.0; // Moderate for range queries
            double hotspotRisk = 70.0;     // High during festivals/sales
            
            String recommendation = "🎊 Risky during BigBillionDay/GreatIndianSale - festival seasons में hotspots";
            
            return new ShardKeyAnalysis("order_date", distributionScore, queryEfficiency, hotspotRisk, recommendation);
        }
    }
    
    /**
     * Cross-shard query optimizer
     */
    public static class CrossShardQueryOptimizer {
        
        public void demonstrateFlipkartOrderQuery() {
            System.out.println("\n🔄 Cross-Shard Query Example (Flipkart Order Analytics):");
            System.out.println("Query: Get all orders for user 'U12345' in last 30 days");
            
            // Step 1: Identify required shards
            String userId = "U12345";
            int userShard = getShardId(userId, 4);
            
            System.out.println("\n1️⃣ Shard Identification:");
            System.out.println("   User Shard: " + userShard + " (for user profile)");
            System.out.println("   Order Shards: Multiple (date-based partitioning)");
            
            // Step 2: Query execution plan
            System.out.println("\n2️⃣ Query Execution Plan:");
            System.out.println("   a) Query user shard for user validation");
            System.out.println("   b) Query last 30 days of order shards");
            System.out.println("   c) Aggregate results in application layer");
            
            // Step 3: Optimization techniques
            System.out.println("\n3️⃣ Optimization Techniques:");
            System.out.println("   ✅ Use secondary index on user_id in order shards");
            System.out.println("   ✅ Parallel query execution across date shards");  
            System.out.println("   ✅ Result caching for frequent users");
            System.out.println("   ⚡ Estimated Response Time: 45ms (vs 200ms without optimization)");
        }
        
        public void demonstratePaytmTransactionQuery() {
            System.out.println("\n💳 Paytm Cross-Shard Transaction Query:");
            System.out.println("Query: Monthly transaction summary by merchant category");
            
            System.out.println("\n1️⃣ Challenges:");
            System.out.println("   - Data spread across 12 monthly shards");
            System.out.println("   - Need to aggregate by merchant_category");
            System.out.println("   - Handle UPI, wallet, और card transactions");
            
            System.out.println("\n2️⃣ Solution Strategy:");
            System.out.println("   a) Map-Reduce pattern across shards");
            System.out.println("   b) Pre-computed daily aggregates");
            System.out.println("   c) Real-time + batch processing hybrid");
            
            System.out.println("\n3️⃣ Performance Metrics:");
            System.out.println("   📊 Data Volume: 50 crore transactions/month");
            System.out.println("   ⚡ Query Time: 2.3 seconds (vs 45 seconds without sharding)");
            System.out.println("   💾 Memory Usage: 8GB (vs 180GB single machine)");
        }
    }
    
    // Utility methods
    private static int getShardId(String key, int numShards) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] hash = md.digest(key.getBytes());
            int hashInt = Math.abs(Arrays.hashCode(hash));
            return hashInt % numShards;
        } catch (NoSuchAlgorithmException e) {
            // Fallback to simple hash
            return Math.abs(key.hashCode()) % numShards;
        }
    }
    
    private static double calculateDistributionScore(Map<Integer, Integer> distribution, int totalItems) {
        if (totalItems == 0) return 0.0;
        
        double expectedPerShard = (double) totalItems / distribution.size();
        double variance = 0.0;
        
        for (int count : distribution.values()) {
            variance += Math.pow(count - expectedPerShard, 2);
        }
        
        variance /= distribution.size();
        double standardDeviation = Math.sqrt(variance);
        
        // Lower standard deviation = better distribution
        // Convert to 0-100 score
        double distributionScore = Math.max(0, 100 - (standardDeviation / expectedPerShard * 100));
        return distributionScore;
    }
    
    /**
     * Main method - भारतीय e-commerce shard key selection demo
     */
    public static void main(String[] args) {
        System.out.println("🛍️ भारतीय ई-कॉमर्स Shard Key Selection System");
        System.out.println("=" + "=".repeat(60));
        
        // Sample Indian user data
        List<String> userIds = Arrays.asList(
            "U001_DEL", "U002_MUM", "U003_BLR", "U004_HYD", "U005_CHN",
            "U006_KOL", "U007_PUN", "U008_AHM", "U009_JAI", "U010_SRT"
        );
        
        List<String> pincodes = Arrays.asList(
            "110001", "400001", "560001", "500001", "600001",
            "700001", "411001", "380001", "302001", "395001"
        );
        
        List<String> phoneNumbers = Arrays.asList(
            "9876543210", "8765432109", "7654321098", "6543210987", "5432109876",
            "9988776655", "8899776644", "7766554433", "9955667788", "8844337722"
        );
        
        List<String> orderIds = Arrays.asList(
            "ORD_2024_001", "ORD_2024_002", "ORD_2024_003", "ORD_2024_004", "ORD_2024_005",
            "FL_001_MUM", "FL_002_DEL", "FL_003_BLR", "FL_004_CHN", "FL_005_HYD"
        );
        
        List<String> dates = Arrays.asList(
            "2024-01", "2024-02", "2024-03", "2024-04", "2024-05",
            "2024-06", "2024-07", "2024-08", "2024-09", "2024-10"
        );
        
        // User shard key analysis
        UserShardKeySelector userSelector = new UserShardKeySelector();
        
        ShardKeyAnalysis userIdAnalysis = userSelector.analyzeUserIdSharding(userIds);
        displayAnalysis(userIdAnalysis);
        
        ShardKeyAnalysis pincodeAnalysis = userSelector.analyzePincodeSharding(pincodes);
        displayAnalysis(pincodeAnalysis);
        
        ShardKeyAnalysis phoneAnalysis = userSelector.analyzePhoneSharding(phoneNumbers);
        displayAnalysis(phoneAnalysis);
        
        // Order shard key analysis  
        OrderShardKeySelector orderSelector = new OrderShardKeySelector();
        
        ShardKeyAnalysis orderIdAnalysis = orderSelector.analyzeOrderIdSharding(orderIds);
        displayAnalysis(orderIdAnalysis);
        
        ShardKeyAnalysis userOrderAnalysis = orderSelector.analyzeUserIdSharding(userIds);
        displayAnalysis(userOrderAnalysis);
        
        ShardKeyAnalysis dateAnalysis = orderSelector.analyzeDateSharding(dates);
        displayAnalysis(dateAnalysis);
        
        // Cross-shard query examples
        CrossShardQueryOptimizer optimizer = new CrossShardQueryOptimizer();
        optimizer.demonstrateFlipkartOrderQuery();
        optimizer.demonstratePaytmTransactionQuery();
        
        // Final recommendations
        System.out.println("\n📋 Final Recommendations (अंतिम सुझाव):");
        System.out.println("=" + "=".repeat(50));
        System.out.println("🎯 User Data: user_id (95% queries benefit)");
        System.out.println("📦 Orders: Composite key (order_id + date) for balanced load");  
        System.out.println("💳 Payments: transaction_id with monthly rotation");
        System.out.println("📱 Real-time: phone_number for OTP/verification");
        System.out.println("🗺️ Geo queries: pincode with metro-specific handling");
        
        System.out.println("\n⚠️ Anti-patterns to Avoid:");
        System.out.println("❌ Don't shard by date during festival seasons");
        System.out.println("❌ Avoid single user_id for high-volume sellers");
        System.out.println("❌ Never use incremental IDs as shard keys");
        System.out.println("❌ Don't ignore Indian geo-specific hotspots");
    }
    
    private static void displayAnalysis(ShardKeyAnalysis analysis) {
        System.out.println("\n" + "─".repeat(60));
        System.out.printf("📊 Shard Key: %s%n", analysis.keyName);
        System.out.printf("📈 Distribution Score: %.1f/100%n", analysis.distributionScore);
        System.out.printf("⚡ Query Efficiency: %.1f/100%n", analysis.queryEfficiency);
        System.out.printf("🔥 Hotspot Risk: %.1f/100%n", analysis.hotspotRisk);
        System.out.printf("💡 Recommendation: %s%n", analysis.recommendation);
    }
}