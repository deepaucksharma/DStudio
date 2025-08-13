/**
 * Zomato ML Pipeline for Food Delivery Optimization
 * Episode 44: MLOps at Scale
 * 
 * यह Java example Zomato का complete ML pipeline दिखाता है
 * Delivery time prediction, demand forecasting, और dynamic pricing के लिए
 * production-ready MLOps system।
 * 
 * Production Stats:
 * - Zomato: 10 crore+ monthly active users
 * - Restaurant partners: 200,000+ across India
 * - ML predictions: 100,000+ per minute
 * - Model accuracy: 92%+ for delivery time
 * - Real-time inference latency: <50ms
 */

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

// Data Models
class Restaurant {
    private final String restaurantId;
    private final String name;
    private final String cuisine;
    private final Location location;
    private final double rating;
    private final int avgPreparationTime;
    private final boolean isActive;
    private final String priceRange;
    private final List<String> specialties;
    
    public Restaurant(String restaurantId, String name, String cuisine, Location location,
                     double rating, int avgPreparationTime, boolean isActive, 
                     String priceRange, List<String> specialties) {
        this.restaurantId = restaurantId;
        this.name = name;
        this.cuisine = cuisine;
        this.location = location;
        this.rating = rating;
        this.avgPreparationTime = avgPreparationTime;
        this.isActive = isActive;
        this.priceRange = priceRange;
        this.specialties = specialties;
    }
    
    // Getters
    public String getRestaurantId() { return restaurantId; }
    public String getName() { return name; }
    public String getCuisine() { return cuisine; }
    public Location getLocation() { return location; }
    public double getRating() { return rating; }
    public int getAvgPreparationTime() { return avgPreparationTime; }
    public boolean isActive() { return isActive; }
    public String getPriceRange() { return priceRange; }
    public List<String> getSpecialties() { return specialties; }
}

class Location {
    private final double latitude;
    private final double longitude;
    private final String address;
    private final String city;
    private final String area;
    
    public Location(double latitude, double longitude, String address, String city, String area) {
        this.latitude = latitude;
        this.longitude = longitude;
        this.address = address;
        this.city = city;
        this.area = area;
    }
    
    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public String getAddress() { return address; }
    public String getCity() { return city; }
    public String getArea() { return area; }
}

class Order {
    private final String orderId;
    private final String customerId;
    private final String restaurantId;
    private final List<OrderItem> items;
    private final Location deliveryLocation;
    private final LocalDateTime orderTime;
    private final double totalAmount;
    private final String paymentMethod;
    private final OrderStatus status;
    private final LocalDateTime estimatedDeliveryTime;
    private final LocalDateTime actualDeliveryTime;
    private final double distanceKm;
    private final String weatherCondition;
    private final boolean isPriority;
    
    public enum OrderStatus {
        PLACED, CONFIRMED, PREPARING, PICKED_UP, OUT_FOR_DELIVERY, DELIVERED, CANCELLED
    }
    
    public Order(String orderId, String customerId, String restaurantId,
                List<OrderItem> items, Location deliveryLocation, LocalDateTime orderTime,
                double totalAmount, String paymentMethod, OrderStatus status,
                LocalDateTime estimatedDeliveryTime, LocalDateTime actualDeliveryTime,
                double distanceKm, String weatherCondition, boolean isPriority) {
        this.orderId = orderId;
        this.customerId = customerId;
        this.restaurantId = restaurantId;
        this.items = items;
        this.deliveryLocation = deliveryLocation;
        this.orderTime = orderTime;
        this.totalAmount = totalAmount;
        this.paymentMethod = paymentMethod;
        this.status = status;
        this.estimatedDeliveryTime = estimatedDeliveryTime;
        this.actualDeliveryTime = actualDeliveryTime;
        this.distanceKm = distanceKm;
        this.weatherCondition = weatherCondition;
        this.isPriority = isPriority;
    }
    
    // Getters
    public String getOrderId() { return orderId; }
    public String getCustomerId() { return customerId; }
    public String getRestaurantId() { return restaurantId; }
    public List<OrderItem> getItems() { return items; }
    public Location getDeliveryLocation() { return deliveryLocation; }
    public LocalDateTime getOrderTime() { return orderTime; }
    public double getTotalAmount() { return totalAmount; }
    public String getPaymentMethod() { return paymentMethod; }
    public OrderStatus getStatus() { return status; }
    public LocalDateTime getEstimatedDeliveryTime() { return estimatedDeliveryTime; }
    public LocalDateTime getActualDeliveryTime() { return actualDeliveryTime; }
    public double getDistanceKm() { return distanceKm; }
    public String getWeatherCondition() { return weatherCondition; }
    public boolean isPriority() { return isPriority; }
}

class OrderItem {
    private final String itemId;
    private final String name;
    private final int quantity;
    private final double price;
    private final List<String> customizations;
    
    public OrderItem(String itemId, String name, int quantity, double price, List<String> customizations) {
        this.itemId = itemId;
        this.name = name;
        this.quantity = quantity;
        this.price = price;
        this.customizations = customizations;
    }
    
    public String getItemId() { return itemId; }
    public String getName() { return name; }
    public int getQuantity() { return quantity; }
    public double getPrice() { return price; }
    public List<String> getCustomizations() { return customizations; }
}

class MLFeatureVector {
    private final Map<String, Double> features;
    
    public MLFeatureVector() {
        this.features = new HashMap<>();
    }
    
    public void addFeature(String name, double value) {
        features.put(name, value);
    }
    
    public double getFeature(String name) {
        return features.getOrDefault(name, 0.0);
    }
    
    public Map<String, Double> getAllFeatures() {
        return new HashMap<>(features);
    }
    
    public double[] toArray(List<String> featureNames) {
        return featureNames.stream()
                .mapToDouble(name -> features.getOrDefault(name, 0.0))
                .toArray();
    }
}

class MLPrediction {
    private final String predictionType;
    private final double value;
    private final double confidence;
    private final LocalDateTime timestamp;
    private final Map<String, Object> metadata;
    
    public MLPrediction(String predictionType, double value, double confidence, Map<String, Object> metadata) {
        this.predictionType = predictionType;
        this.value = value;
        this.confidence = confidence;
        this.timestamp = LocalDateTime.now();
        this.metadata = metadata;
    }
    
    public String getPredictionType() { return predictionType; }
    public double getValue() { return value; }
    public double getConfidence() { return confidence; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public Map<String, Object> getMetadata() { return metadata; }
}

class FeatureEngineer {
    private final Map<String, Double> historicalAverages = new ConcurrentHashMap<>();
    private final Map<String, List<Double>> timeSeriesData = new ConcurrentHashMap<>();
    
    public MLFeatureVector extractFeatures(Order order, Restaurant restaurant, 
                                         Map<String, Object> externalData) {
        MLFeatureVector features = new MLFeatureVector();
        
        // Time-based features
        int hourOfDay = order.getOrderTime().getHour();
        int dayOfWeek = order.getOrderTime().getDayOfWeek().getValue();
        boolean isWeekend = dayOfWeek >= 6;
        boolean isPeakHour = (hourOfDay >= 12 && hourOfDay <= 14) || (hourOfDay >= 19 && hourOfDay <= 21);
        
        features.addFeature("hour_of_day", hourOfDay);
        features.addFeature("day_of_week", dayOfWeek);
        features.addFeature("is_weekend", isWeekend ? 1.0 : 0.0);
        features.addFeature("is_peak_hour", isPeakHour ? 1.0 : 0.0);
        
        // Restaurant features
        features.addFeature("restaurant_rating", restaurant.getRating());
        features.addFeature("avg_preparation_time", restaurant.getAvgPreparationTime());
        features.addFeature("restaurant_busy_score", calculateBusyScore(restaurant.getRestaurantId()));
        
        // Order features
        features.addFeature("order_value", order.getTotalAmount());
        features.addFeature("item_count", order.getItems().size());
        features.addFeature("distance_km", order.getDistanceKm());
        features.addFeature("is_priority", order.isPriority() ? 1.0 : 0.0);
        
        // Cuisine features (one-hot encoding simplified)
        features.addFeature("cuisine_" + restaurant.getCuisine().toLowerCase(), 1.0);
        
        // Weather features
        features.addFeature("weather_rain", order.getWeatherCondition().equals("rainy") ? 1.0 : 0.0);
        features.addFeature("weather_sunny", order.getWeatherCondition().equals("sunny") ? 1.0 : 0.0);
        
        // Historical features
        String restaurantKey = "restaurant_" + restaurant.getRestaurantId();
        features.addFeature("restaurant_avg_delivery_time", 
                          historicalAverages.getOrDefault(restaurantKey, 30.0));
        
        // Location-based features
        features.addFeature("delivery_area_traffic", calculateTrafficScore(order.getDeliveryLocation()));
        
        // Complexity features
        double complexityScore = calculateOrderComplexity(order);
        features.addFeature("order_complexity", complexityScore);
        
        return features;
    }
    
    private double calculateBusyScore(String restaurantId) {
        // Simulate restaurant busy score based on recent orders
        Random random = new Random(restaurantId.hashCode());
        return random.nextDouble() * 10; // 0-10 scale
    }
    
    private double calculateTrafficScore(Location location) {
        // Simulate traffic score based on area
        // High traffic areas like Mumbai, Delhi get higher scores
        String area = location.getArea().toLowerCase();
        if (area.contains("bkc") || area.contains("connaught") || area.contains("mg road")) {
            return 8.0 + (new Random().nextDouble() * 2); // 8-10
        } else if (area.contains("andheri") || area.contains("gurgaon")) {
            return 6.0 + (new Random().nextDouble() * 2); // 6-8
        }
        return 3.0 + (new Random().nextDouble() * 3); // 3-6
    }
    
    private double calculateOrderComplexity(Order order) {
        double complexity = 0.0;
        
        // More items = more complex
        complexity += order.getItems().size() * 0.5;
        
        // Customizations add complexity
        int totalCustomizations = order.getItems().stream()
                .mapToInt(item -> item.getCustomizations().size())
                .sum();
        complexity += totalCustomizations * 0.3;
        
        return Math.min(complexity, 10.0); // Cap at 10
    }
    
    public void updateHistoricalData(String key, double value) {
        historicalAverages.put(key, value);
        
        timeSeriesData.computeIfAbsent(key, k -> new ArrayList<>()).add(value);
        
        // Keep only last 1000 data points
        List<Double> series = timeSeriesData.get(key);
        if (series.size() > 1000) {
            series.remove(0);
        }
    }
}

class DeliveryTimePredictor {
    private final List<String> featureNames;
    private final Map<String, Double> modelWeights;
    private final Random random = new Random(42); // Fixed seed for consistency
    
    public DeliveryTimePredictor() {
        // Simplified linear model feature names
        this.featureNames = Arrays.asList(
            "hour_of_day", "is_weekend", "is_peak_hour", "restaurant_rating",
            "avg_preparation_time", "restaurant_busy_score", "order_value",
            "item_count", "distance_km", "is_priority", "weather_rain",
            "restaurant_avg_delivery_time", "delivery_area_traffic", "order_complexity"
        );
        
        // Simulated trained model weights (normally loaded from file/database)
        this.modelWeights = new HashMap<>();
        modelWeights.put("hour_of_day", 0.5);
        modelWeights.put("is_weekend", -2.0);
        modelWeights.put("is_peak_hour", 8.0);
        modelWeights.put("restaurant_rating", -1.5);
        modelWeights.put("avg_preparation_time", 0.8);
        modelWeights.put("restaurant_busy_score", 1.2);
        modelWeights.put("order_value", 0.01);
        modelWeights.put("item_count", 2.0);
        modelWeights.put("distance_km", 3.5);
        modelWeights.put("is_priority", -5.0);
        modelWeights.put("weather_rain", 7.0);
        modelWeights.put("restaurant_avg_delivery_time", 0.6);
        modelWeights.put("delivery_area_traffic", 1.8);
        modelWeights.put("order_complexity", 1.0);
    }
    
    public MLPrediction predict(MLFeatureVector features) {
        double basePrediction = 25.0; // Base delivery time: 25 minutes
        
        // Apply model weights
        for (String featureName : featureNames) {
            double featureValue = features.getFeature(featureName);
            double weight = modelWeights.getOrDefault(featureName, 0.0);
            basePrediction += featureValue * weight;
        }
        
        // Add some noise for realism
        basePrediction += random.nextGaussian() * 2.0;
        
        // Ensure reasonable bounds
        double prediction = Math.max(15.0, Math.min(basePrediction, 60.0));
        
        // Calculate confidence based on feature consistency
        double confidence = calculateConfidence(features);
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("model_version", "v2.1.0");
        metadata.put("feature_count", featureNames.size());
        metadata.put("base_prediction", basePrediction);
        
        return new MLPrediction("delivery_time", prediction, confidence, metadata);
    }
    
    private double calculateConfidence(MLFeatureVector features) {
        // Simplified confidence calculation
        double confidence = 0.85; // Base confidence
        
        // Reduce confidence for edge cases
        if (features.getFeature("distance_km") > 10) {
            confidence -= 0.1; // Long distance reduces confidence
        }
        
        if (features.getFeature("weather_rain") == 1.0) {
            confidence -= 0.05; // Rain reduces confidence
        }
        
        if (features.getFeature("restaurant_busy_score") > 8) {
            confidence -= 0.05; // Very busy restaurant
        }
        
        return Math.max(0.5, Math.min(confidence, 0.95));
    }
}

class DemandForecaster {
    private final Map<String, List<Double>> demandHistory = new ConcurrentHashMap<>();
    
    public MLPrediction predictDemand(String restaurantId, int hourAhead) {
        // Simple time series forecasting
        List<Double> history = demandHistory.getOrDefault(restaurantId, 
                Arrays.asList(10.0, 15.0, 20.0, 25.0, 30.0)); // Default history
        
        // Calculate trend and seasonality (simplified)
        double recent = history.subList(Math.max(0, history.size() - 5), history.size())
                .stream().mapToDouble(Double::doubleValue).average().orElse(20.0);
        
        double trend = 0.0;
        if (history.size() >= 2) {
            trend = history.get(history.size() - 1) - history.get(history.size() - 2);
        }
        
        // Hour-based seasonality
        int currentHour = LocalDateTime.now().getHour();
        int targetHour = (currentHour + hourAhead) % 24;
        
        double seasonality = 1.0;
        if (targetHour >= 12 && targetHour <= 14) {
            seasonality = 1.5; // Lunch peak
        } else if (targetHour >= 19 && targetHour <= 21) {
            seasonality = 1.8; // Dinner peak
        } else if (targetHour >= 22 || targetHour <= 6) {
            seasonality = 0.3; // Low demand hours
        }
        
        double prediction = (recent + trend) * seasonality;
        prediction = Math.max(0, prediction);
        
        double confidence = 0.7 + (history.size() * 0.01); // More history = more confidence
        confidence = Math.min(confidence, 0.9);
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("restaurant_id", restaurantId);
        metadata.put("hours_ahead", hourAhead);
        metadata.put("seasonality_factor", seasonality);
        metadata.put("trend", trend);
        
        return new MLPrediction("demand_forecast", prediction, confidence, metadata);
    }
    
    public void updateDemandHistory(String restaurantId, double actualDemand) {
        demandHistory.computeIfAbsent(restaurantId, k -> new ArrayList<>()).add(actualDemand);
        
        // Keep only last 168 hours (1 week)
        List<Double> history = demandHistory.get(restaurantId);
        if (history.size() > 168) {
            history.remove(0);
        }
    }
}

class DynamicPricer {
    public MLPrediction calculateOptimalPrice(Order order, Restaurant restaurant, double demandForecast) {
        double basePrice = order.getTotalAmount();
        
        // Demand-based pricing
        double demandMultiplier = 1.0;
        if (demandForecast > 50) {
            demandMultiplier = 1.15; // 15% surge for high demand
        } else if (demandForecast > 30) {
            demandMultiplier = 1.05; // 5% surge for medium demand
        }
        
        // Time-based pricing
        int hour = order.getOrderTime().getHour();
        double timeMultiplier = 1.0;
        if ((hour >= 12 && hour <= 14) || (hour >= 19 && hour <= 21)) {
            timeMultiplier = 1.1; // Peak hour pricing
        }
        
        // Weather-based pricing
        double weatherMultiplier = 1.0;
        if (order.getWeatherCondition().equals("rainy")) {
            weatherMultiplier = 1.2; // 20% surge for rain
        }
        
        // Distance-based pricing
        double distanceMultiplier = 1.0 + (order.getDistanceKm() * 0.02); // 2% per km
        
        double optimalPrice = basePrice * demandMultiplier * timeMultiplier * 
                             weatherMultiplier * distanceMultiplier;
        
        // Apply bounds (±30% of base price)
        optimalPrice = Math.max(basePrice * 0.7, Math.min(optimalPrice, basePrice * 1.3));
        
        double confidence = 0.8;
        
        Map<String, Object> metadata = new HashMap<>();
        metadata.put("base_price", basePrice);
        metadata.put("demand_multiplier", demandMultiplier);
        metadata.put("time_multiplier", timeMultiplier);
        metadata.put("weather_multiplier", weatherMultiplier);
        metadata.put("distance_multiplier", distanceMultiplier);
        
        return new MLPrediction("optimal_price", optimalPrice, confidence, metadata);
    }
}

class MLPipelineMetrics {
    private final AtomicLong totalPredictions = new AtomicLong(0);
    private final AtomicLong deliveryTimePredictions = new AtomicLong(0);
    private final AtomicLong demandPredictions = new AtomicLong(0);
    private final AtomicLong pricingPredictions = new AtomicLong(0);
    
    private final ConcurrentHashMap<String, Double> averageLatency = new ConcurrentHashMap<>();
    private final ConcurrentHashMap<String, Double> averageAccuracy = new ConcurrentHashMap<>();
    
    public void recordPrediction(String predictionType, double latencyMs, double accuracy) {
        totalPredictions.incrementAndGet();
        
        switch (predictionType) {
            case "delivery_time":
                deliveryTimePredictions.incrementAndGet();
                break;
            case "demand_forecast":
                demandPredictions.incrementAndGet();
                break;
            case "optimal_price":
                pricingPredictions.incrementAndGet();
                break;
        }
        
        // Update rolling averages (simplified)
        averageLatency.put(predictionType, latencyMs);
        averageAccuracy.put(predictionType, accuracy);
    }
    
    public void printMetrics() {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("🤖 ZOMATO ML PIPELINE PERFORMANCE METRICS 🤖");
        System.out.println("=".repeat(70));
        
        System.out.printf("📊 Total Predictions: %,d%n", totalPredictions.get());
        System.out.printf("⏱️ Delivery Time Predictions: %,d%n", deliveryTimePredictions.get());
        System.out.printf("📈 Demand Forecasts: %,d%n", demandPredictions.get());
        System.out.printf("💰 Pricing Predictions: %,d%n", pricingPredictions.get());
        
        System.out.println("\n📡 Average Latency:");
        averageLatency.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> System.out.printf("  %s: %.2f ms%n", 
                         entry.getKey(), entry.getValue()));
        
        System.out.println("\n🎯 Average Accuracy:");
        averageAccuracy.entrySet().stream()
                .sorted(Map.Entry.comparingByKey())
                .forEach(entry -> System.out.printf("  %s: %.1f%%%n", 
                         entry.getKey(), entry.getValue() * 100));
        
        System.out.printf("\n🕐 Last Updated: %s%n", 
                         LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")));
        System.out.println("=".repeat(70));
    }
}

public class ZomatoMLPipeline {
    private final FeatureEngineer featureEngineer;
    private final DeliveryTimePredictor deliveryTimePredictor;
    private final DemandForecaster demandForecaster;
    private final DynamicPricer dynamicPricer;
    private final MLPipelineMetrics metrics;
    private final ExecutorService mlExecutor;
    private final ScheduledExecutorService scheduledExecutor;
    
    // Mock data
    private final List<Restaurant> restaurants;
    private final List<String> indianCities = Arrays.asList(
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad"
    );
    
    public ZomatoMLPipeline() {
        this.featureEngineer = new FeatureEngineer();
        this.deliveryTimePredictor = new DeliveryTimePredictor();
        this.demandForecaster = new DemandForecaster();
        this.dynamicPricer = new DynamicPricer();
        this.metrics = new MLPipelineMetrics();
        this.mlExecutor = Executors.newFixedThreadPool(10);
        this.scheduledExecutor = Executors.newScheduledThreadPool(3);
        
        // Initialize mock restaurants
        this.restaurants = generateMockRestaurants();
        
        // Start metrics reporting
        scheduledExecutor.scheduleAtFixedRate(
            metrics::printMetrics, 30, 30, TimeUnit.SECONDS
        );
    }
    
    private List<Restaurant> generateMockRestaurants() {
        List<Restaurant> restaurantList = new ArrayList<>();
        String[] cuisines = {"North Indian", "South Indian", "Chinese", "Italian", "Fast Food", "Biryani"};
        String[] priceRanges = {"Budget", "Mid-Range", "Premium"};
        
        Random random = new Random(42);
        
        for (int i = 0; i < 100; i++) {
            String city = indianCities.get(random.nextInt(indianCities.size()));
            String cuisine = cuisines[random.nextInt(cuisines.length)];
            String priceRange = priceRanges[random.nextInt(priceRanges.length)];
            
            Location location = new Location(
                18.9 + random.nextDouble() * 0.2, // Mumbai area coordinates
                72.8 + random.nextDouble() * 0.2,
                "Address " + i,
                city,
                "Area " + (i % 20)
            );
            
            Restaurant restaurant = new Restaurant(
                "rest_" + String.format("%04d", i),
                cuisine + " Restaurant " + i,
                cuisine,
                location,
                3.5 + random.nextDouble() * 1.5, // 3.5 to 5.0 rating
                15 + random.nextInt(20), // 15-35 minutes prep time
                random.nextBoolean(),
                priceRange,
                Arrays.asList("Specialty 1", "Specialty 2")
            );
            
            restaurantList.add(restaurant);
        }
        
        return restaurantList;
    }
    
    private Order generateMockOrder() {
        Random random = new Random();
        Restaurant restaurant = restaurants.get(random.nextInt(restaurants.size()));
        
        // Generate order items
        List<OrderItem> items = IntStream.range(0, 1 + random.nextInt(3))
                .mapToObj(i -> new OrderItem(
                    "item_" + i,
                    "Food Item " + i,
                    1 + random.nextInt(2),
                    100 + random.nextDouble() * 400, // 100-500 INR per item
                    random.nextBoolean() ? Arrays.asList("Extra Spicy") : Collections.emptyList()
                ))
                .collect(Collectors.toList());
        
        double totalAmount = items.stream().mapToDouble(OrderItem::getPrice).sum();
        
        Location deliveryLocation = new Location(
            restaurant.getLocation().getLatitude() + (random.nextDouble() - 0.5) * 0.05,
            restaurant.getLocation().getLongitude() + (random.nextDouble() - 0.5) * 0.05,
            "Delivery Address",
            restaurant.getLocation().getCity(),
            "Delivery Area"
        );
        
        double distance = 2 + random.nextDouble() * 8; // 2-10 km
        String[] weather = {"sunny", "cloudy", "rainy"};
        String[] payments = {"UPI", "Credit Card", "Cash", "Wallet"};
        
        return new Order(
            "order_" + System.currentTimeMillis() + "_" + random.nextInt(1000),
            "customer_" + random.nextInt(10000),
            restaurant.getRestaurantId(),
            items,
            deliveryLocation,
            LocalDateTime.now(),
            totalAmount,
            payments[random.nextInt(payments.length)],
            Order.OrderStatus.PLACED,
            LocalDateTime.now().plusMinutes(30), // Estimated
            null, // Not delivered yet
            distance,
            weather[random.nextInt(weather.length)],
            random.nextDouble() < 0.1 // 10% priority orders
        );
    }
    
    public CompletableFuture<Map<String, MLPrediction>> processOrder(Order order) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                Map<String, MLPrediction> predictions = new HashMap<>();
                
                // Find restaurant
                Restaurant restaurant = restaurants.stream()
                        .filter(r -> r.getRestaurantId().equals(order.getRestaurantId()))
                        .findFirst()
                        .orElse(restaurants.get(0)); // Fallback
                
                // Extract features
                Map<String, Object> externalData = new HashMap<>(); // Could include weather API data
                MLFeatureVector features = featureEngineer.extractFeatures(order, restaurant, externalData);
                
                // 1. Delivery Time Prediction
                long deliveryStartTime = System.nanoTime();
                MLPrediction deliveryTimePred = deliveryTimePredictor.predict(features);
                double deliveryLatency = (System.nanoTime() - deliveryStartTime) / 1_000_000.0;
                metrics.recordPrediction("delivery_time", deliveryLatency, 0.92); // Mock accuracy
                predictions.put("delivery_time", deliveryTimePred);
                
                // 2. Demand Forecasting
                long demandStartTime = System.nanoTime();
                MLPrediction demandPred = demandForecaster.predictDemand(restaurant.getRestaurantId(), 1);
                double demandLatency = (System.nanoTime() - demandStartTime) / 1_000_000.0;
                metrics.recordPrediction("demand_forecast", demandLatency, 0.85); // Mock accuracy
                predictions.put("demand_forecast", demandPred);
                
                // 3. Dynamic Pricing
                long pricingStartTime = System.nanoTime();
                MLPrediction pricingPred = dynamicPricer.calculateOptimalPrice(order, restaurant, demandPred.getValue());
                double pricingLatency = (System.nanoTime() - pricingStartTime) / 1_000_000.0;
                metrics.recordPrediction("optimal_price", pricingLatency, 0.88); // Mock accuracy
                predictions.put("optimal_price", pricingPred);
                
                // Log high-value or problematic predictions
                if (deliveryTimePred.getValue() > 45) {
                    System.out.printf("⚠️ Long delivery time predicted: %.1f minutes for order %s%n",
                                    deliveryTimePred.getValue(), order.getOrderId());
                }
                
                if (pricingPred.getValue() > order.getTotalAmount() * 1.2) {
                    System.out.printf("💰 High surge pricing: ₹%.2f (%.0f%% surge) for order %s%n",
                                    pricingPred.getValue(), 
                                    ((pricingPred.getValue() / order.getTotalAmount()) - 1) * 100,
                                    order.getOrderId());
                }
                
                return predictions;
                
            } catch (Exception e) {
                System.err.println("Error processing order " + order.getOrderId() + ": " + e.getMessage());
                return new HashMap<>();
            }
        }, mlExecutor);
    }
    
    public void simulateRealTimeProcessing(int durationMinutes) {
        System.out.println("🍕 Starting Zomato ML Pipeline Simulation");
        System.out.println("🤖 Processing orders with ML predictions...");
        System.out.println("⚡ Real-time delivery time, demand forecasting, और dynamic pricing...\n");
        
        ScheduledExecutorService simulator = Executors.newScheduledThreadPool(2);
        
        // Order generation patterns
        Map<Integer, Integer> hourlyOrderRates = new HashMap<>();
        hourlyOrderRates.put(12, 100); // Lunch peak
        hourlyOrderRates.put(13, 120);
        hourlyOrderRates.put(19, 150); // Dinner peak
        hourlyOrderRates.put(20, 180);
        hourlyOrderRates.put(21, 140);
        // Default rate for other hours
        int defaultRate = 50;
        
        AtomicInteger processedOrders = new AtomicInteger(0);
        
        // Start order processing simulation
        simulator.scheduleAtFixedRate(() -> {
            try {
                int currentHour = LocalDateTime.now().getHour();
                int ordersThisCycle = hourlyOrderRates.getOrDefault(currentHour, defaultRate) / 60; // Per minute
                
                for (int i = 0; i < ordersThisCycle; i++) {
                    Order mockOrder = generateMockOrder();
                    
                    processOrder(mockOrder).thenAccept(predictions -> {
                        processedOrders.incrementAndGet();
                        
                        // Simulate feedback loop (update historical data)
                        Restaurant restaurant = restaurants.stream()
                                .filter(r -> r.getRestaurantId().equals(mockOrder.getRestaurantId()))
                                .findFirst().orElse(null);
                        
                        if (restaurant != null) {
                            // Update demand history
                            demandForecaster.updateDemandHistory(restaurant.getRestaurantId(), 
                                                               ordersThisCycle * 60.0); // Orders per hour
                            
                            // Update feature engineer with feedback
                            if (predictions.containsKey("delivery_time")) {
                                featureEngineer.updateHistoricalData(
                                    "restaurant_" + restaurant.getRestaurantId(), 
                                    predictions.get("delivery_time").getValue()
                                );
                            }
                        }
                    }).exceptionally(throwable -> {
                        System.err.println("Failed to process order: " + throwable.getMessage());
                        return null;
                    });
                }
            } catch (Exception e) {
                System.err.println("Error in order generation: " + e.getMessage());
            }
        }, 0, 1, TimeUnit.MINUTES);
        
        // Run simulation for specified duration
        try {
            Thread.sleep(durationMinutes * 60 * 1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Shutdown simulation
        simulator.shutdown();
        
        // Final summary
        System.out.printf("\n🏁 SIMULATION COMPLETED%n");
        System.out.printf("📊 Total Orders Processed: %,d%n", processedOrders.get());
        System.out.printf("⚡ Average Processing Rate: %,.1f orders/minute%n", 
                         processedOrders.get() / (double) durationMinutes);
        
        metrics.printMetrics();
    }
    
    public void shutdown() {
        mlExecutor.shutdown();
        scheduledExecutor.shutdown();
    }
    
    public static void main(String[] args) {
        System.out.println("🇮🇳 Zomato ML Pipeline - Production Scale Food Delivery Optimization");
        System.out.println("🍕 Complete MLOps system for Indian food delivery market");
        System.out.println("🤖 Real-time ML predictions for delivery optimization...\n");
        
        ZomatoMLPipeline pipeline = new ZomatoMLPipeline();
        
        try {
            // Run simulation for 3 minutes (demo)
            pipeline.simulateRealTimeProcessing(3);
            
            System.out.println("\n💡 Production system would handle:");
            System.out.println("   - 100,000+ orders per minute across India");
            System.out.println("   - <50ms ML inference latency");
            System.out.println("   - 92%+ delivery time prediction accuracy");
            System.out.println("   - Real-time model updates और feedback loops");
            System.out.println("   - Integration with weather, traffic, और restaurant APIs");
            
        } finally {
            pipeline.shutdown();
        }
    }
}