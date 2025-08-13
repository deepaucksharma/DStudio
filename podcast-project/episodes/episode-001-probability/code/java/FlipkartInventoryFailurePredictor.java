/**
 * Flipkart Inventory Failure Prediction System
 * ==========================================
 * 
 * Advanced failure prediction system for e-commerce inventory management.
 * Real examples: Flipkart Big Billion Day, Amazon Great Indian Festival preparation
 * 
 * मुख्य concepts:
 * 1. Probability-based failure prediction using historical data
 * 2. Machine learning approach for inventory forecasting
 * 3. Indian festival season impact modeling
 * 4. Supply chain reliability analysis
 * 
 * Mumbai analogy: Like predicting Mumbai local train breakdowns during monsoon
 * Author: Hindi Tech Podcast Series
 */

import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;
import java.math.BigDecimal;
import java.math.RoundingMode;

// Hindi comments के साथ comprehensive inventory failure predictor

/**
 * Inventory item with failure tracking
 * Inventory item का failure tracking के साथ
 */
class InventoryItem {
    private final String itemId;
    private final String itemName;
    private final String category;          // Electronics, Fashion, Home, etc.
    private final String brand;
    private final BigDecimal price;
    private final int currentStock;
    private final int demandForecast;
    private final LocalDateTime lastRestocked;
    
    // Failure indicators
    private final boolean isLowStock;       // Stock below threshold
    private final boolean isHighDemand;     // Demand exceeds supply
    private final boolean isSlowMoving;     // Slow-selling item
    private final boolean hasSupplyIssues;  // Supplier reliability issues
    
    // Indian context factors
    private final boolean isFestivalItem;   // Popular during festivals
    private final String preferredRegion;   // North, South, East, West India
    private final boolean isMonsoonSensitive; // Logistics affected by monsoon
    
    public InventoryItem(String itemId, String itemName, String category, String brand,
                        BigDecimal price, int currentStock, int demandForecast,
                        LocalDateTime lastRestocked, boolean isLowStock, boolean isHighDemand,
                        boolean isSlowMoving, boolean hasSupplyIssues, boolean isFestivalItem,
                        String preferredRegion, boolean isMonsoonSensitive) {
        this.itemId = itemId;
        this.itemName = itemName;
        this.category = category;
        this.brand = brand;
        this.price = price;
        this.currentStock = currentStock;
        this.demandForecast = demandForecast;
        this.lastRestocked = lastRestocked;
        this.isLowStock = isLowStock;
        this.isHighDemand = isHighDemand;
        this.isSlowMoving = isSlowMoving;
        this.hasSupplyIssues = hasSupplyIssues;
        this.isFestivalItem = isFestivalItem;
        this.preferredRegion = preferredRegion;
        this.isMonsoonSensitive = isMonsoonSensitive;
    }
    
    // Getters
    public String getItemId() { return itemId; }
    public String getItemName() { return itemName; }
    public String getCategory() { return category; }
    public String getBrand() { return brand; }
    public BigDecimal getPrice() { return price; }
    public int getCurrentStock() { return currentStock; }
    public int getDemandForecast() { return demandForecast; }
    public LocalDateTime getLastRestocked() { return lastRestocked; }
    public boolean isLowStock() { return isLowStock; }
    public boolean isHighDemand() { return isHighDemand; }
    public boolean isSlowMoving() { return isSlowMoving; }
    public boolean hasSupplyIssues() { return hasSupplyIssues; }
    public boolean isFestivalItem() { return isFestivalItem; }
    public String getPreferredRegion() { return preferredRegion; }
    public boolean isMonsoonSensitive() { return isMonsoonSensitive; }
}

/**
 * Failure prediction result
 * Failure prediction का result
 */
class FailurePrediction {
    private final String itemId;
    private final double failureProbability;    // 0.0 to 1.0
    private final String riskLevel;            // LOW, MEDIUM, HIGH, CRITICAL
    private final LocalDateTime predictedFailureTime;
    private final String primaryReason;        // Main reason for potential failure
    private final List<String> contributingFactors;
    private final List<String> recommendations;
    
    // Indian context insights
    private final String mumbaiAnalogy;        // Mumbai-based explanation
    private final double festivalImpact;       // Impact factor during festivals
    private final double monsoonImpact;        // Impact factor during monsoon
    
    public FailurePrediction(String itemId, double failureProbability, String riskLevel,
                           LocalDateTime predictedFailureTime, String primaryReason,
                           List<String> contributingFactors, List<String> recommendations,
                           String mumbaiAnalogy, double festivalImpact, double monsoonImpact) {
        this.itemId = itemId;
        this.failureProbability = failureProbability;
        this.riskLevel = riskLevel;
        this.predictedFailureTime = predictedFailureTime;
        this.primaryReason = primaryReason;
        this.contributingFactors = contributingFactors;
        this.recommendations = recommendations;
        this.mumbaiAnalogy = mumbaiAnalogy;
        this.festivalImpact = festivalImpact;
        this.monsoonImpact = monsoonImpact;
    }
    
    // Getters
    public String getItemId() { return itemId; }
    public double getFailureProbability() { return failureProbability; }
    public String getRiskLevel() { return riskLevel; }
    public LocalDateTime getPredictedFailureTime() { return predictedFailureTime; }
    public String getPrimaryReason() { return primaryReason; }
    public List<String> getContributingFactors() { return contributingFactors; }
    public List<String> getRecommendations() { return recommendations; }
    public String getMumbaiAnalogy() { return mumbaiAnalogy; }
    public double getFestivalImpact() { return festivalImpact; }
    public double getMonsoonImpact() { return monsoonImpact; }
}

/**
 * Main inventory failure predictor class
 * मुख्य inventory failure predictor class  
 */
public class FlipkartInventoryFailurePredictor {
    
    private final Map<String, InventoryItem> inventory;
    private final Map<String, List<Double>> historicalFailureRates;
    private final Map<String, Double> categoryRiskFactors;
    
    // Indian seasonal factors
    private static final Set<Integer> FESTIVAL_MONTHS = Set.of(3, 8, 10, 11); // Holi, Ganesh, Diwali
    private static final Set<Integer> MONSOON_MONTHS = Set.of(6, 7, 8, 9);   // June to September
    
    // Category-specific risk factors based on Indian market
    private static final Map<String, Double> INDIAN_CATEGORY_RISKS = Map.of(
        "Electronics", 0.15,      // High demand, complex supply chain
        "Fashion", 0.12,          // Seasonal, trend-sensitive
        "Home", 0.08,            // Steady demand
        "Books", 0.05,           // Low risk, predictable demand
        "Sports", 0.10,          // Seasonal variations
        "Beauty", 0.11,          // Brand loyalty issues
        "Grocery", 0.18,         // Perishable, high turnover
        "Mobiles", 0.20          // Highest risk due to launches/offers
    );
    
    public FlipkartInventoryFailurePredictor() {
        this.inventory = new ConcurrentHashMap<>();
        this.historicalFailureRates = new ConcurrentHashMap<>();
        this.categoryRiskFactors = new ConcurrentHashMap<>(INDIAN_CATEGORY_RISKS);
        
        System.out.println("🛒 Flipkart Inventory Failure Predictor initialized");
        System.out.println("📦 Ready to predict inventory failures with Indian market context!");
    }
    
    /**
     * Add inventory item for monitoring
     * Monitoring के लिए inventory item add करते हैं
     */
    public void addInventoryItem(InventoryItem item) {
        inventory.put(item.getItemId(), item);
        
        // Initialize historical failure rates if not exists
        historicalFailureRates.putIfAbsent(item.getCategory(), new ArrayList<>());
        
        System.out.println("📝 Added item: " + item.getItemName() + " (" + item.getCategory() + ")");
    }
    
    /**
     * Generate realistic Indian e-commerce inventory for demo
     * Demo के लिए realistic Indian e-commerce inventory generate करते हैं
     */
    public void generateDemoInventory(int itemCount) {
        System.out.println("📊 Generating " + itemCount + " realistic Indian inventory items...");
        
        String[] categories = {"Electronics", "Fashion", "Home", "Books", "Sports", "Beauty", "Grocery", "Mobiles"};
        String[] brands = {"Samsung", "Xiaomi", "Realme", "Levi's", "Nike", "Adidas", "Lakme", "Godrej"};
        String[] regions = {"North", "South", "East", "West"};
        
        String[][] itemsByCategory = {
            {"iPhone", "Samsung Galaxy", "Laptop", "Headphones", "TV", "Washing Machine"},
            {"Jeans", "T-Shirt", "Saree", "Kurta", "Shoes", "Handbag"},
            {"Sofa", "Bed", "Dining Table", "Refrigerator", "Microwave", "AC"},
            {"Novel", "Textbook", "Comics", "Biography", "Self-Help", "Programming"},
            {"Cricket Bat", "Football", "Badminton Racket", "Gym Equipment", "Yoga Mat", "Running Shoes"},
            {"Lipstick", "Foundation", "Perfume", "Shampoo", "Face Cream", "Nail Polish"},
            {"Rice", "Dal", "Oil", "Spices", "Biscuits", "Tea"},
            {"iPhone 15", "Samsung S24", "OnePlus 12", "Pixel 8", "Realme GT", "Xiaomi 14"}
        };
        
        Random random = new Random();
        
        for (int i = 0; i < itemCount; i++) {
            String category = categories[random.nextInt(categories.length)];
            int categoryIndex = Arrays.asList(categories).indexOf(category);
            
            String itemName = itemsByCategory[categoryIndex][random.nextInt(itemsByCategory[categoryIndex].length)];
            String brand = brands[random.nextInt(brands.length)];
            String itemId = "ITEM_" + category.toUpperCase() + "_" + (i + 1);
            
            // Price based on category
            BigDecimal price = generateRealisticPrice(category, random);
            
            // Stock levels with realistic distribution
            int currentStock = 50 + random.nextInt(950); // 50-1000 units
            int demandForecast = 100 + random.nextInt(400); // 100-500 units forecast
            
            // Last restocked (random time in last 30 days)
            LocalDateTime lastRestocked = LocalDateTime.now()
                .minusDays(random.nextInt(30))
                .minusHours(random.nextInt(24));
            
            // Calculate failure indicators
            boolean isLowStock = currentStock < (demandForecast * 0.3); // Less than 30% of demand
            boolean isHighDemand = demandForecast > (currentStock * 1.5); // Demand > 150% of stock
            boolean isSlowMoving = random.nextDouble() < 0.15; // 15% chance of slow-moving
            boolean hasSupplyIssues = random.nextDouble() < 0.1; // 10% chance of supply issues
            
            // Indian context factors
            boolean isFestivalItem = isFestivalItem(category, random);
            String preferredRegion = regions[random.nextInt(regions.length)];
            boolean isMonsoonSensitive = isMonsoonSensitive(category, random);
            
            InventoryItem item = new InventoryItem(
                itemId, itemName, category, brand, price, currentStock, demandForecast,
                lastRestocked, isLowStock, isHighDemand, isSlowMoving, hasSupplyIssues,
                isFestivalItem, preferredRegion, isMonsoonSensitive
            );
            
            addInventoryItem(item);
        }
        
        System.out.println("✅ Generated " + itemCount + " inventory items successfully!");
    }
    
    /**
     * Generate realistic price based on category
     * Category के अनुसार realistic price generate करते हैं
     */
    private BigDecimal generateRealisticPrice(String category, Random random) {
        switch (category) {
            case "Electronics":
                return BigDecimal.valueOf(5000 + random.nextInt(45000)); // ₹5K-50K
            case "Fashion":
                return BigDecimal.valueOf(500 + random.nextInt(4500)); // ₹500-5K
            case "Home":
                return BigDecimal.valueOf(2000 + random.nextInt(48000)); // ₹2K-50K
            case "Books":
                return BigDecimal.valueOf(200 + random.nextInt(800)); // ₹200-1K
            case "Sports":
                return BigDecimal.valueOf(1000 + random.nextInt(9000)); // ₹1K-10K
            case "Beauty":
                return BigDecimal.valueOf(300 + random.nextInt(2700)); // ₹300-3K
            case "Grocery":
                return BigDecimal.valueOf(50 + random.nextInt(950)); // ₹50-1K
            case "Mobiles":
                return BigDecimal.valueOf(8000 + random.nextInt(92000)); // ₹8K-1L
            default:
                return BigDecimal.valueOf(1000 + random.nextInt(9000));
        }
    }
    
    /**
     * Determine if item is popular during festivals
     * Item festival के दौरान popular है या नहीं
     */
    private boolean isFestivalItem(String category, Random random) {
        Map<String, Double> festivalProbability = Map.of(
            "Electronics", 0.8,    // High demand during festivals
            "Fashion", 0.9,        // Very high demand for clothes
            "Home", 0.6,          // Moderate demand for home items
            "Mobiles", 0.9,       // Very high demand for phones
            "Beauty", 0.7,        // High demand for cosmetics
            "Books", 0.3,         // Low festival demand
            "Sports", 0.4,        // Low-moderate demand
            "Grocery", 0.5        // Moderate demand for special foods
        );
        
        double probability = festivalProbability.getOrDefault(category, 0.5);
        return random.nextDouble() < probability;
    }
    
    /**
     * Determine if item logistics are affected by monsoon
     * Item की logistics monsoon से affected होती है या नहीं
     */
    private boolean isMonsoonSensitive(String category, Random random) {
        Map<String, Double> monsoonSensitivity = Map.of(
            "Electronics", 0.7,    // Electronic goods sensitive to water
            "Fashion", 0.4,        // Some sensitivity due to transport
            "Home", 0.8,          // Large items, transport issues
            "Mobiles", 0.8,       // High-value, sensitive items
            "Beauty", 0.3,        // Less sensitive
            "Books", 0.6,         // Paper products sensitive
            "Sports", 0.5,        // Moderate sensitivity
            "Grocery", 0.9        // Highly sensitive, perishable
        );
        
        double probability = monsoonSensitivity.getOrDefault(category, 0.5);
        return random.nextDouble() < probability;
    }
    
    /**
     * Predict failure probability for an inventory item
     * Inventory item के लिए failure probability predict करते हैं
     */
    public FailurePrediction predictFailure(String itemId) {
        InventoryItem item = inventory.get(itemId);
        if (item == null) {
            return null;
        }
        
        // Base failure probability calculation
        double baseProbability = calculateBaseProbability(item);
        
        // Apply Indian context multipliers
        double contextAdjustedProbability = applyIndianContextFactors(baseProbability, item);
        
        // Determine risk level
        String riskLevel = determineRiskLevel(contextAdjustedProbability);
        
        // Predict failure time
        LocalDateTime predictedFailureTime = predictFailureTime(item, contextAdjustedProbability);
        
        // Identify primary failure reason
        String primaryReason = identifyPrimaryFailureReason(item);
        
        // Contributing factors
        List<String> contributingFactors = identifyContributingFactors(item);
        
        // Generate recommendations
        List<String> recommendations = generateRecommendations(item, contextAdjustedProbability);
        
        // Mumbai analogy
        String mumbaiAnalogy = generateMumbaiAnalogy(item, contextAdjustedProbability);
        
        // Seasonal impacts
        double festivalImpact = calculateFestivalImpact(item);
        double monsoonImpact = calculateMonsoonImpact(item);
        
        return new FailurePrediction(
            itemId, contextAdjustedProbability, riskLevel, predictedFailureTime,
            primaryReason, contributingFactors, recommendations, mumbaiAnalogy,
            festivalImpact, monsoonImpact
        );
    }
    
    /**
     * Calculate base failure probability
     * Base failure probability calculate करते हैं
     */
    private double calculateBaseProbability(InventoryItem item) {
        double probability = 0.0;
        
        // Stock level risk
        if (item.isLowStock()) {
            probability += 0.4; // 40% risk for low stock
        }
        
        // Demand vs supply imbalance
        if (item.isHighDemand()) {
            probability += 0.3; // 30% risk for high demand
        }
        
        // Supply chain issues
        if (item.hasSupplyIssues()) {
            probability += 0.25; // 25% risk for supply issues
        }
        
        // Slow-moving inventory
        if (item.isSlowMoving()) {
            probability += 0.15; // 15% risk for slow-moving items
        }
        
        // Category-specific risk
        Double categoryRisk = categoryRiskFactors.get(item.getCategory());
        if (categoryRisk != null) {
            probability += categoryRisk;
        }
        
        // Age of stock (how long since last restock)
        long daysSinceRestock = Duration.between(item.getLastRestocked(), LocalDateTime.now()).toDays();
        if (daysSinceRestock > 30) {
            probability += 0.1; // 10% additional risk for old stock
        }
        
        return Math.min(0.95, probability); // Cap at 95%
    }
    
    /**
     * Apply Indian context factors to probability
     * Indian context factors apply करके probability adjust करते हैं
     */
    private double applyIndianContextFactors(double baseProbability, InventoryItem item) {
        double adjustedProbability = baseProbability;
        
        // Festival season impact
        if (isFestivalSeason() && item.isFestivalItem()) {
            adjustedProbability *= 1.4; // 40% increase during festivals
        }
        
        // Monsoon impact
        if (isMonsoonSeason() && item.isMonsoonSensitive()) {
            adjustedProbability *= 1.3; // 30% increase during monsoon
        }
        
        // Regional preference mismatch (simplified logic)
        LocalDateTime now = LocalDateTime.now();
        if (item.getPreferredRegion().equals("North") && now.getMonthValue() <= 3) {
            adjustedProbability *= 0.9; // 10% lower risk in preferred season
        }
        
        // High-value item protection (better handling)
        if (item.getPrice().compareTo(BigDecimal.valueOf(10000)) > 0) {
            adjustedProbability *= 0.85; // 15% lower risk for expensive items
        }
        
        return Math.min(0.99, adjustedProbability); // Cap at 99%
    }
    
    /**
     * Check if current time is festival season
     * Current time festival season है या नहीं check करते हैं
     */
    private boolean isFestivalSeason() {
        return FESTIVAL_MONTHS.contains(LocalDateTime.now().getMonthValue());
    }
    
    /**
     * Check if current time is monsoon season
     * Current time monsoon season है या नहीं check करते हैं
     */
    private boolean isMonsoonSeason() {
        return MONSOON_MONTHS.contains(LocalDateTime.now().getMonthValue());
    }
    
    /**
     * Determine risk level based on probability
     * Probability के base पर risk level determine करते हैं
     */
    private String determineRiskLevel(double probability) {
        if (probability < 0.2) return "LOW";
        else if (probability < 0.5) return "MEDIUM";
        else if (probability < 0.8) return "HIGH";
        else return "CRITICAL";
    }
    
    /**
     * Predict when failure might occur
     * Failure कब हो सकती है predict करते हैं
     */
    private LocalDateTime predictFailureTime(InventoryItem item, double probability) {
        // Base prediction: higher probability = sooner failure
        long hoursToFailure = (long) (168 / (probability + 0.1)); // Max 1 week
        
        // Adjust based on stock levels
        if (item.isLowStock() && item.isHighDemand()) {
            hoursToFailure = Math.min(24, hoursToFailure); // Within 24 hours
        }
        
        return LocalDateTime.now().plusHours(hoursToFailure);
    }
    
    /**
     * Identify primary reason for potential failure
     * Potential failure का primary reason identify करते हैं
     */
    private String identifyPrimaryFailureReason(InventoryItem item) {
        if (item.isLowStock() && item.isHighDemand()) {
            return "STOCK_OUT_IMMINENT";
        } else if (item.hasSupplyIssues()) {
            return "SUPPLY_CHAIN_DISRUPTION";
        } else if (item.isSlowMoving()) {
            return "INVENTORY_OBSOLESCENCE";
        } else if (item.isLowStock()) {
            return "LOW_STOCK_WARNING";
        } else {
            return "DEMAND_SUPPLY_IMBALANCE";
        }
    }
    
    /**
     * Identify contributing factors
     * Contributing factors identify करते हैं
     */
    private List<String> identifyContributingFactors(InventoryItem item) {
        List<String> factors = new ArrayList<>();
        
        if (isFestivalSeason() && item.isFestivalItem()) {
            factors.add("Festival season demand surge");
        }
        
        if (isMonsoonSeason() && item.isMonsoonSensitive()) {
            factors.add("Monsoon logistics challenges");
        }
        
        if (item.hasSupplyIssues()) {
            factors.add("Supplier reliability issues");
        }
        
        long daysSinceRestock = Duration.between(item.getLastRestocked(), LocalDateTime.now()).toDays();
        if (daysSinceRestock > 21) {
            factors.add("Long time since last restock (" + daysSinceRestock + " days)");
        }
        
        if (item.getPrice().compareTo(BigDecimal.valueOf(20000)) > 0) {
            factors.add("High-value item requiring special handling");
        }
        
        return factors;
    }
    
    /**
     * Generate actionable recommendations
     * Actionable recommendations generate करते हैं
     */
    private List<String> generateRecommendations(InventoryItem item, double probability) {
        List<String> recommendations = new ArrayList<>();
        
        if (probability > 0.6) {
            recommendations.add("🚨 URGENT: Immediate restock required");
            recommendations.add("📞 Contact supplier for emergency delivery");
        }
        
        if (item.isLowStock()) {
            recommendations.add("📦 Place bulk order to prevent stockout");
            recommendations.add("⚡ Enable auto-reorder trigger");
        }
        
        if (item.isHighDemand()) {
            recommendations.add("📈 Increase safety stock for this item");
            recommendations.add("🎯 Consider demand-based pricing strategy");
        }
        
        if (isFestivalSeason() && item.isFestivalItem()) {
            recommendations.add("🎉 Prepare for festival demand spike");
            recommendations.add("🚛 Arrange additional logistics capacity");
        }
        
        if (isMonsoonSeason() && item.isMonsoonSensitive()) {
            recommendations.add("🌧️ Use waterproof packaging for shipments");
            recommendations.add("🛣️ Plan alternate delivery routes");
        }
        
        if (item.hasSupplyIssues()) {
            recommendations.add("🔄 Identify backup suppliers");
            recommendations.add("📊 Review supplier performance metrics");
        }
        
        return recommendations;
    }
    
    /**
     * Generate Mumbai analogy for the failure scenario
     * Failure scenario के लिए Mumbai analogy generate करते हैं
     */
    private String generateMumbaiAnalogy(InventoryItem item, double probability) {
        if (probability > 0.8) {
            return "जैसे Mumbai में peak hours के दौरान train overcrowded हो जाती है - inventory भी खत्म होने वाली है!";
        } else if (probability > 0.6) {
            return "जैसे monsoon के दौरान Mumbai traffic slow हो जाता है - supply chain में delay आ सकती है";
        } else if (probability > 0.4) {
            return "जैसे Mumbai local train में sometimes delay होती है - stock replenishment में थोड़ी problem हो सकती है";
        } else if (probability > 0.2) {
            return "जैसे Mumbai का weather unpredictable होता है - inventory levels को monitor करते रहना चाहिए";
        } else {
            return "जैसे Mumbai locals reliable हैं most of the time - inventory भी stable condition में है";
        }
    }
    
    /**
     * Calculate festival impact factor
     * Festival impact factor calculate करते हैं
     */
    private double calculateFestivalImpact(InventoryItem item) {
        if (!item.isFestivalItem()) {
            return 1.0; // No impact
        }
        
        // Higher impact during actual festival months
        if (isFestivalSeason()) {
            return 1.8; // 80% higher risk/demand
        } else {
            return 1.2; // 20% preparation impact
        }
    }
    
    /**
     * Calculate monsoon impact factor
     * Monsoon impact factor calculate करते हैं
     */
    private double calculateMonsoonImpact(InventoryItem item) {
        if (!item.isMonsoonSensitive()) {
            return 1.0; // No impact
        }
        
        if (isMonsoonSeason()) {
            return 1.6; // 60% higher logistics risk
        } else {
            return 1.1; // 10% preparatory impact
        }
    }
    
    /**
     * Generate comprehensive failure prediction report
     * Comprehensive failure prediction report generate करते हैं
     */
    public String generateFailurePredictionReport() {
        StringBuilder report = new StringBuilder();
        report.append("🛒 FLIPKART INVENTORY FAILURE PREDICTION REPORT\n");
        report.append("=".repeat(65)).append("\n");
        report.append("📊 Total Items Analyzed: ").append(inventory.size()).append("\n");
        report.append("📅 Report Generated: ").append(
            LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))
        ).append(" IST\n");
        report.append("🇮🇳 Indian Context: ");
        
        List<String> contextFactors = new ArrayList<>();
        if (isFestivalSeason()) contextFactors.add("Festival Season Active");
        if (isMonsoonSeason()) contextFactors.add("Monsoon Season Active");
        
        report.append(contextFactors.isEmpty() ? "Normal Season" : String.join(", ", contextFactors));
        report.append("\n\n");
        
        // Generate predictions for all items
        List<FailurePrediction> predictions = new ArrayList<>();
        for (String itemId : inventory.keySet()) {
            FailurePrediction prediction = predictFailure(itemId);
            if (prediction != null) {
                predictions.add(prediction);
            }
        }
        
        // Sort by failure probability (highest risk first)
        predictions.sort((a, b) -> Double.compare(b.getFailureProbability(), a.getFailureProbability()));
        
        // High-risk items
        List<FailurePrediction> highRiskItems = predictions.stream()
            .filter(p -> p.getFailureProbability() > 0.6)
            .collect(Collectors.toList());
            
        if (!highRiskItems.isEmpty()) {
            report.append("🚨 HIGH RISK ITEMS (Probability > 60%)\n");
            report.append("-".repeat(50)).append("\n");
            
            for (int i = 0; i < Math.min(10, highRiskItems.size()); i++) {
                FailurePrediction pred = highRiskItems.get(i);
                InventoryItem item = inventory.get(pred.getItemId());
                
                report.append("\n").append(i + 1).append(". ").append(item.getItemName())
                    .append(" (").append(item.getCategory()).append(")\n");
                report.append("   Risk Level: ").append(pred.getRiskLevel()).append("\n");
                report.append("   Failure Probability: ").append(String.format("%.1f%%", pred.getFailureProbability() * 100)).append("\n");
                report.append("   Predicted Failure: ").append(
                    pred.getPredictedFailureTime().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm"))
                ).append("\n");
                report.append("   Primary Reason: ").append(pred.getPrimaryReason()).append("\n");
                report.append("   🏙️ ").append(pred.getMumbaiAnalogy()).append("\n");
            }
        }
        
        // Category-wise risk analysis
        report.append("\n\n📊 CATEGORY-WISE RISK ANALYSIS\n");
        report.append("-".repeat(50)).append("\n");
        
        Map<String, List<FailurePrediction>> categoryPredictions = predictions.stream()
            .collect(Collectors.groupingBy(p -> inventory.get(p.getItemId()).getCategory()));
            
        for (Map.Entry<String, List<FailurePrediction>> entry : categoryPredictions.entrySet()) {
            String category = entry.getKey();
            List<FailurePrediction> categoryPreds = entry.getValue();
            
            double avgRisk = categoryPreds.stream()
                .mapToDouble(FailurePrediction::getFailureProbability)
                .average()
                .orElse(0.0);
                
            long highRiskCount = categoryPreds.stream()
                .mapToLong(p -> p.getFailureProbability() > 0.6 ? 1 : 0)
                .sum();
                
            report.append("\n").append(category).append(":\n");
            report.append("   Average Risk: ").append(String.format("%.1f%%", avgRisk * 100)).append("\n");
            report.append("   High Risk Items: ").append(highRiskCount).append("/").append(categoryPreds.size()).append("\n");
        }
        
        // Indian context insights
        report.append("\n\n🇮🇳 INDIAN CONTEXT INSIGHTS\n");
        report.append("-".repeat(50)).append("\n");
        
        if (isFestivalSeason()) {
            long festivalItems = inventory.values().stream()
                .mapToLong(item -> item.isFestivalItem() ? 1 : 0)
                .sum();
            report.append("🎉 Festival Season Impact:\n");
            report.append("   Festival-sensitive items: ").append(festivalItems).append("/").append(inventory.size()).append("\n");
            report.append("   Expected demand surge: 40-80% increase\n");
            report.append("   Recommendation: Increase safety stock for festival items\n\n");
        }
        
        if (isMonsoonSeason()) {
            long monsoonSensitive = inventory.values().stream()
                .mapToLong(item -> item.isMonsoonSensitive() ? 1 : 0)
                .sum();
            report.append("🌧️ Monsoon Season Impact:\n");
            report.append("   Monsoon-sensitive items: ").append(monsoonSensitive).append("/").append(inventory.size()).append("\n");
            report.append("   Expected logistics delays: 30-60% increase\n");
            report.append("   Recommendation: Use waterproof packaging and alternate routes\n\n");
        }
        
        // Overall recommendations
        report.append("💡 OVERALL RECOMMENDATIONS\n");
        report.append("-".repeat(50)).append("\n");
        report.append("📦 Immediate Actions:\n");
        
        if (highRiskItems.size() > 0) {
            report.append("   • Prioritize restocking for ").append(highRiskItems.size()).append(" high-risk items\n");
            report.append("   • Contact suppliers for emergency deliveries\n");
            report.append("   • Consider alternative suppliers for critical items\n");
        }
        
        report.append("📈 Strategic Actions:\n");
        report.append("   • Implement automated reorder triggers\n");
        report.append("   • Increase safety stock during peak seasons\n");
        report.append("   • Develop monsoon-specific logistics strategies\n");
        report.append("   • Create festival season demand forecasting models\n");
        
        report.append("\n🎯 Remember: Like Mumbai's dabbawalas - consistency and preparation prevent failures!\n");
        report.append("🚀 Happy inventory management! May your shelves never be empty during Big Billion Days!");
        
        return report.toString();
    }
    
    /**
     * Main method for demonstration
     * Demo के लिए main method
     */
    public static void main(String[] args) {
        System.out.println("🚀 Starting Flipkart Inventory Failure Prediction Demo");
        System.out.println("=".repeat(65));
        
        // Create predictor
        FlipkartInventoryFailurePredictor predictor = new FlipkartInventoryFailurePredictor();
        
        // Generate demo inventory
        predictor.generateDemoInventory(200);
        
        // Generate and print comprehensive report
        System.out.println("📋 GENERATING COMPREHENSIVE FAILURE PREDICTION REPORT...\n");
        String report = predictor.generateFailurePredictionReport();
        System.out.println(report);
        
        System.out.println("\n🎉 Inventory failure prediction analysis completed!");
        System.out.println("🏙️ Just like predicting Mumbai local train delays - data helps preparation!");
        System.out.println("💡 Use these predictions to prevent inventory stockouts!");
    }
}