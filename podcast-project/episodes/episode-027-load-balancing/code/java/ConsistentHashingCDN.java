/**
 * Consistent Hashing for CDN Node Selection
 * CDN नोड selection के लिए consistent hashing
 * 
 * यह class दिखाती है कि कैसे भारतीय CDN network में
 * consistent hashing का use करके optimal node selection करें
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDateTime;

public class ConsistentHashingCDN {
    
    // Indian CDN node configurations
    private final Map<String, CDNNode> nodes = new ConcurrentHashMap<>();
    private final TreeMap<Long, CDNNode> hashRing = new TreeMap<>();
    private final int virtualNodesPerNode = 150; // Virtual nodes for better distribution
    
    /**
     * CDN Node representation
     */
    public static class CDNNode {
        public final String nodeId;
        public final String city;
        public final String region;
        public final String provider; // Cloudflare, Akamai, AWS CloudFront, etc.
        public final String datacenterLocation;
        public final double latitude;
        public final double longitude;
        
        // Capacity and performance metrics
        public final long bandwidthMbps;
        public final long storageTB;
        public volatile long currentBandwidthUsage = 0;
        public volatile long currentStorageUsage = 0;
        public volatile double avgResponseTimeMs = 50.0;
        public volatile boolean isHealthy = true;
        
        // Traffic statistics
        public volatile long totalRequests = 0;
        public volatile long successfulRequests = 0;
        public volatile double hitRatio = 85.0; // Cache hit ratio percentage
        
        public CDNNode(String nodeId, String city, String region, String provider,
                      String datacenterLocation, double latitude, double longitude,
                      long bandwidthMbps, long storageTB) {
            this.nodeId = nodeId;
            this.city = city;
            this.region = region;
            this.provider = provider;
            this.datacenterLocation = datacenterLocation;
            this.latitude = latitude;
            this.longitude = longitude;
            this.bandwidthMbps = bandwidthMbps;
            this.storageTB = storageTB;
        }
        
        public double getLoadPercentage() {
            return (double) currentBandwidthUsage / bandwidthMbps * 100;
        }
        
        public double getStorageUsagePercentage() {
            return (double) currentStorageUsage / storageTB * 100;
        }
        
        public double getSuccessRate() {
            return totalRequests > 0 ? (double) successfulRequests / totalRequests * 100 : 100.0;
        }
        
        @Override
        public String toString() {
            return String.format("CDNNode{%s, %s, Load: %.1f%%, Storage: %.1f%%, Success: %.1f%%}", 
                nodeId, city, getLoadPercentage(), getStorageUsagePercentage(), getSuccessRate());
        }
    }
    
    /**
     * Content request representation
     */
    public static class ContentRequest {
        public final String requestId;
        public final String contentUrl;
        public final String contentType; // image, video, script, document
        public final long contentSizeKB;
        public final String userLocation; // User's city/region
        public final double userLatitude;
        public final double userLongitude;
        public final int priority; // 1=low, 2=normal, 3=high, 4=critical
        public final LocalDateTime timestamp;
        
        public ContentRequest(String requestId, String contentUrl, String contentType,
                            long contentSizeKB, String userLocation, double userLatitude, 
                            double userLongitude, int priority) {
            this.requestId = requestId;
            this.contentUrl = contentUrl;
            this.contentType = contentType;
            this.contentSizeKB = contentSizeKB;
            this.userLocation = userLocation;
            this.userLatitude = userLatitude;
            this.userLongitude = userLongitude;
            this.priority = priority;
            this.timestamp = LocalDateTime.now();
        }
    }
    
    /**
     * Initialize Indian CDN network
     */
    public ConsistentHashingCDN() {
        initializeIndianCDNNodes();
        buildHashRing();
        
        System.out.println("🌐 भारतीय CDN Consistent Hashing Network initialized");
        System.out.println("📡 Total nodes: " + nodes.size());
        System.out.println("⭕ Hash ring positions: " + hashRing.size());
    }
    
    /**
     * Initialize CDN nodes across major Indian cities
     */
    private void initializeIndianCDNNodes() {
        CDNNode[] indianNodes = {
            // Tier 1 Cities - High capacity nodes
            new CDNNode("MUM_CF_001", "Mumbai", "West India", "Cloudflare", 
                       "Mumbai-Powai DC", 19.0760, 72.8777, 100000, 500), // 100 Gbps, 500TB
            
            new CDNNode("MUM_AK_001", "Mumbai", "West India", "Akamai",
                       "Mumbai-BKC DC", 19.0596, 72.8656, 80000, 400),
            
            new CDNNode("DEL_AWS_001", "Delhi", "North India", "AWS CloudFront",
                       "Delhi-Gurgaon DC", 28.4595, 77.0266, 120000, 600),
            
            new CDNNode("DEL_CF_001", "Delhi", "North India", "Cloudflare", 
                       "Delhi-Noida DC", 28.5355, 77.3910, 90000, 450),
            
            new CDNNode("BLR_AWS_001", "Bangalore", "South India", "AWS CloudFront",
                       "Bangalore-Electronic City", 12.8456, 77.6603, 110000, 550),
            
            new CDNNode("BLR_AZ_001", "Bangalore", "South India", "Azure CDN",
                       "Bangalore-Whitefield", 12.9698, 77.7500, 70000, 350),
            
            new CDNNode("HYD_CF_001", "Hyderabad", "South India", "Cloudflare",
                       "Hyderabad-Hitech City", 17.4435, 78.3772, 60000, 300),
            
            new CDNNode("CHN_AK_001", "Chennai", "South India", "Akamai",
                       "Chennai-OMR", 12.9141, 80.2316, 65000, 320),
            
            // Tier 2 Cities - Medium capacity nodes
            new CDNNode("PUN_CF_001", "Pune", "West India", "Cloudflare",
                       "Pune-Hinjewadi", 18.5679, 73.9143, 40000, 200),
            
            new CDNNode("KOL_AK_001", "Kolkata", "East India", "Akamai",
                       "Kolkata-Salt Lake", 22.5726, 88.3639, 35000, 175),
            
            new CDNNode("AHM_AWS_001", "Ahmedabad", "West India", "AWS CloudFront",
                       "Ahmedabad-SG Highway", 23.0225, 72.5714, 30000, 150),
            
            new CDNNode("JAI_CF_001", "Jaipur", "North India", "Cloudflare",
                       "Jaipur-Malviya Nagar", 26.8467, 75.7794, 25000, 125),
            
            // Edge locations - Lower capacity but strategic
            new CDNNode("LKO_EDGE_001", "Lucknow", "North India", "EdgeNetwork",
                       "Lucknow-Gomti Nagar", 26.8467, 80.9462, 15000, 75),
            
            new CDNNode("IND_EDGE_001", "Indore", "Central India", "EdgeNetwork",
                       "Indore-Vijay Nagar", 22.7196, 75.8577, 12000, 60),
            
            new CDNNode("COI_EDGE_001", "Coimbatore", "South India", "EdgeNetwork",
                       "Coimbatore-Peelamedu", 11.0168, 76.9558, 10000, 50)
        };
        
        for (CDNNode node : indianNodes) {
            nodes.put(node.nodeId, node);
            
            // Simulate initial load and storage usage
            node.currentBandwidthUsage = (long) (node.bandwidthMbps * ThreadLocalRandom.current().nextDouble(0.1, 0.4));
            node.currentStorageUsage = (long) (node.storageTB * ThreadLocalRandom.current().nextDouble(0.3, 0.7));
            node.avgResponseTimeMs = 30 + ThreadLocalRandom.current().nextDouble(0, 50);
            node.hitRatio = 80 + ThreadLocalRandom.current().nextDouble(0, 15);
            
            System.out.printf("📡 Added CDN node: %s (%s) - %s - Capacity: %d Gbps, %d TB%n",
                node.nodeId, node.city, node.provider, node.bandwidthMbps/1000, node.storageTB);
        }
    }
    
    /**
     * Build consistent hash ring with virtual nodes
     */
    private void buildHashRing() {
        hashRing.clear();
        
        for (CDNNode node : nodes.values()) {
            for (int i = 0; i < virtualNodesPerNode; i++) {
                String virtualNodeKey = node.nodeId + ":" + i;
                long hash = hash(virtualNodeKey);
                hashRing.put(hash, node);
            }
        }
        
        System.out.printf("⭕ Hash ring built with %d virtual nodes%n", hashRing.size());
    }
    
    /**
     * Get optimal CDN node for content request using consistent hashing
     */
    public CDNNode selectNode(ContentRequest request) {
        if (hashRing.isEmpty()) {
            return null;
        }
        
        // Primary selection using consistent hashing
        String requestKey = request.contentUrl + ":" + request.userLocation;
        long hash = hash(requestKey);
        
        // Find the first node >= hash (clockwise on the ring)
        Map.Entry<Long, CDNNode> entry = hashRing.ceilingEntry(hash);
        if (entry == null) {
            entry = hashRing.firstEntry(); // Wrap around
        }
        
        CDNNode primaryNode = entry.getValue();
        
        // Apply intelligent selection considering node health, load, and geography
        CDNNode selectedNode = selectOptimalNode(request, primaryNode);
        
        System.out.printf("🎯 Selected node %s for request %s (User: %s)%n", 
            selectedNode.nodeId, request.requestId, request.userLocation);
        
        return selectedNode;
    }
    
    /**
     * Intelligent node selection considering multiple factors
     */
    private CDNNode selectOptimalNode(ContentRequest request, CDNNode primaryNode) {
        List<CDNNode> candidates = new ArrayList<>();
        
        // Add primary node and nearby nodes on the hash ring
        candidates.add(primaryNode);
        
        // Add a few adjacent nodes for comparison
        Long primaryHash = null;
        for (Map.Entry<Long, CDNNode> entry : hashRing.entrySet()) {
            if (entry.getValue() == primaryNode) {
                primaryHash = entry.getKey();
                break;
            }
        }
        
        if (primaryHash != null) {
            // Get next few nodes in the ring
            Map.Entry<Long, CDNNode> current = hashRing.higherEntry(primaryHash);
            for (int i = 0; i < 3 && current != null; i++) {
                if (!candidates.contains(current.getValue())) {
                    candidates.add(current.getValue());
                }
                current = hashRing.higherEntry(current.getKey());
                if (current == null) {
                    current = hashRing.firstEntry(); // Wrap around
                }
            }
        }
        
        // Filter healthy nodes with available capacity
        List<CDNNode> availableNodes = new ArrayList<>();
        for (CDNNode node : candidates) {
            if (node.isHealthy && node.getLoadPercentage() < 90) {
                availableNodes.add(node);
            }
        }
        
        if (availableNodes.isEmpty()) {
            return primaryNode; // Fallback to primary even if overloaded
        }
        
        // Score nodes based on multiple criteria
        CDNNode bestNode = availableNodes.get(0);
        double bestScore = calculateNodeScore(request, bestNode);
        
        for (CDNNode node : availableNodes) {
            double score = calculateNodeScore(request, node);
            if (score > bestScore) {
                bestScore = score;
                bestNode = node;
            }
        }
        
        return bestNode;
    }
    
    /**
     * Calculate node score based on multiple factors
     */
    private double calculateNodeScore(ContentRequest request, CDNNode node) {
        double score = 100.0; // Base score
        
        // Load factor (lower load is better)
        double loadFactor = 1.0 - (node.getLoadPercentage() / 100.0);
        score *= loadFactor;
        
        // Response time factor (lower is better)
        double responseTimeFactor = Math.max(0.1, 1.0 - (node.avgResponseTimeMs - 20) / 200.0);
        score *= responseTimeFactor;
        
        // Hit ratio factor (higher is better)
        double hitRatioFactor = node.hitRatio / 100.0;
        score *= hitRatioFactor;
        
        // Geographic proximity (simplified distance calculation)
        double distance = calculateDistance(request.userLatitude, request.userLongitude,
                                          node.latitude, node.longitude);
        double proximityFactor = Math.max(0.1, 1.0 - (distance / 2000.0)); // Normalize by 2000km
        score *= proximityFactor;
        
        // Content type optimization
        if (request.contentType.equals("video") && node.bandwidthMbps > 80000) {
            score *= 1.2; // Prefer high-bandwidth nodes for video
        }
        
        if (request.contentType.equals("image") && node.hitRatio > 90) {
            score *= 1.1; // Prefer high-cache-hit nodes for images
        }
        
        // Priority boost
        if (request.priority >= 3) {
            score *= 1.15; // Boost for high-priority requests
        }
        
        return score;
    }
    
    /**
     * Process content request and update node statistics
     */
    public ContentDeliveryResult processRequest(ContentRequest request) {
        long startTime = System.currentTimeMillis();
        
        CDNNode selectedNode = selectNode(request);
        if (selectedNode == null) {
            return new ContentDeliveryResult(request.requestId, false, 0, 
                "No CDN nodes available", null);
        }
        
        // Update node statistics
        selectedNode.totalRequests++;
        
        // Simulate content delivery
        boolean success = simulateContentDelivery(selectedNode, request);
        long responseTime = System.currentTimeMillis() - startTime;
        
        if (success) {
            selectedNode.successfulRequests++;
            
            // Update bandwidth usage (temporary increase)
            long bandwidthIncrease = request.contentSizeKB / 8; // Convert KB to Kbps roughly
            selectedNode.currentBandwidthUsage = Math.min(selectedNode.bandwidthMbps, 
                selectedNode.currentBandwidthUsage + bandwidthIncrease);
        }
        
        // Update response time (moving average)
        selectedNode.avgResponseTimeMs = (selectedNode.avgResponseTimeMs + responseTime) / 2.0;
        
        String deliveryInfo = String.format("%s (%s) via %s", 
            selectedNode.city, selectedNode.provider, selectedNode.nodeId);
        
        return new ContentDeliveryResult(request.requestId, success, responseTime, 
            success ? "Content delivered successfully" : "Delivery failed", deliveryInfo);
    }
    
    /**
     * Simulate content delivery with realistic factors
     */
    private boolean simulateContentDelivery(CDNNode node, ContentRequest request) {
        try {
            // Base success rate
            double successRate = 0.98;
            
            // Adjust for node load
            if (node.getLoadPercentage() > 80) {
                successRate -= 0.05;
            }
            
            // Adjust for content size (larger files are harder to deliver)
            if (request.contentSizeKB > 10000) { // > 10MB
                successRate -= 0.02;
            }
            
            // Adjust for hit ratio (higher hit ratio = higher success rate)
            successRate += (node.hitRatio - 85) / 1000.0;
            
            // Simulate delivery delay
            long deliveryDelay = Math.round(node.avgResponseTimeMs + 
                (request.contentSizeKB / 1000.0) * 2); // 2ms per MB
            Thread.sleep(Math.min(deliveryDelay, 500)); // Cap at 500ms for simulation
            
            return ThreadLocalRandom.current().nextDouble() < successRate;
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }
    
    /**
     * Content delivery result
     */
    public static class ContentDeliveryResult {
        public final String requestId;
        public final boolean success;
        public final long responseTimeMs;
        public final String message;
        public final String deliveryInfo;
        
        public ContentDeliveryResult(String requestId, boolean success, long responseTimeMs,
                                   String message, String deliveryInfo) {
            this.requestId = requestId;
            this.success = success;
            this.responseTimeMs = responseTimeMs;
            this.message = message;
            this.deliveryInfo = deliveryInfo;
        }
        
        @Override
        public String toString() {
            return String.format("ContentDelivery{%s, Success: %s, Time: %dms, Via: %s}",
                requestId, success, responseTimeMs, deliveryInfo);
        }
    }
    
    /**
     * Add new CDN node and rebalance hash ring
     */
    public void addNode(CDNNode newNode) {
        System.out.printf("➕ Adding new CDN node: %s (%s)%n", newNode.nodeId, newNode.city);
        
        nodes.put(newNode.nodeId, newNode);
        
        // Add virtual nodes to hash ring
        for (int i = 0; i < virtualNodesPerNode; i++) {
            String virtualNodeKey = newNode.nodeId + ":" + i;
            long hash = hash(virtualNodeKey);
            hashRing.put(hash, newNode);
        }
        
        System.out.printf("✅ Node added successfully. Total nodes: %d%n", nodes.size());
    }
    
    /**
     * Remove CDN node and rebalance hash ring
     */
    public void removeNode(String nodeId) {
        CDNNode nodeToRemove = nodes.get(nodeId);
        if (nodeToRemove == null) {
            System.out.printf("⚠️ Node not found: %s%n", nodeId);
            return;
        }
        
        System.out.printf("➖ Removing CDN node: %s (%s)%n", nodeId, nodeToRemove.city);
        
        // Remove from nodes map
        nodes.remove(nodeId);
        
        // Remove virtual nodes from hash ring
        Iterator<Map.Entry<Long, CDNNode>> iterator = hashRing.entrySet().iterator();
        while (iterator.hasNext()) {
            Map.Entry<Long, CDNNode> entry = iterator.next();
            if (entry.getValue().nodeId.equals(nodeId)) {
                iterator.remove();
            }
        }
        
        System.out.printf("✅ Node removed successfully. Remaining nodes: %d%n", nodes.size());
    }
    
    /**
     * Get comprehensive CDN statistics
     */
    public CDNStatistics getStatistics() {
        long totalBandwidth = 0;
        long totalUsedBandwidth = 0;
        long totalStorage = 0;
        long totalUsedStorage = 0;
        long totalRequests = 0;
        long totalSuccessfulRequests = 0;
        double avgResponseTime = 0;
        int healthyNodes = 0;
        
        Map<String, Integer> regionNodeCount = new HashMap<>();
        Map<String, Integer> providerNodeCount = new HashMap<>();
        
        for (CDNNode node : nodes.values()) {
            totalBandwidth += node.bandwidthMbps;
            totalUsedBandwidth += node.currentBandwidthUsage;
            totalStorage += node.storageTB;
            totalUsedStorage += node.currentStorageUsage;
            totalRequests += node.totalRequests;
            totalSuccessfulRequests += node.successfulRequests;
            avgResponseTime += node.avgResponseTimeMs;
            
            if (node.isHealthy) healthyNodes++;
            
            regionNodeCount.merge(node.region, 1, Integer::sum);
            providerNodeCount.merge(node.provider, 1, Integer::sum);
        }
        
        avgResponseTime = nodes.size() > 0 ? avgResponseTime / nodes.size() : 0;
        
        return new CDNStatistics(nodes.size(), healthyNodes, totalBandwidth/1000, 
            totalUsedBandwidth/1000, totalStorage, totalUsedStorage, totalRequests, 
            totalSuccessfulRequests, avgResponseTime, regionNodeCount, providerNodeCount);
    }
    
    /**
     * CDN Statistics class
     */
    public static class CDNStatistics {
        public final int totalNodes;
        public final int healthyNodes;
        public final long totalBandwidthGbps;
        public final long usedBandwidthGbps;
        public final long totalStorageTB;
        public final long usedStorageTB;
        public final long totalRequests;
        public final long successfulRequests;
        public final double avgResponseTime;
        public final Map<String, Integer> regionDistribution;
        public final Map<String, Integer> providerDistribution;
        
        public CDNStatistics(int totalNodes, int healthyNodes, long totalBandwidthGbps,
                           long usedBandwidthGbps, long totalStorageTB, long usedStorageTB,
                           long totalRequests, long successfulRequests, double avgResponseTime,
                           Map<String, Integer> regionDistribution, Map<String, Integer> providerDistribution) {
            this.totalNodes = totalNodes;
            this.healthyNodes = healthyNodes;
            this.totalBandwidthGbps = totalBandwidthGbps;
            this.usedBandwidthGbps = usedBandwidthGbps;
            this.totalStorageTB = totalStorageTB;
            this.usedStorageTB = usedStorageTB;
            this.totalRequests = totalRequests;
            this.successfulRequests = successfulRequests;
            this.avgResponseTime = avgResponseTime;
            this.regionDistribution = regionDistribution;
            this.providerDistribution = providerDistribution;
        }
        
        public double getSuccessRate() {
            return totalRequests > 0 ? (double) successfulRequests / totalRequests * 100 : 100.0;
        }
        
        public double getBandwidthUtilization() {
            return totalBandwidthGbps > 0 ? (double) usedBandwidthGbps / totalBandwidthGbps * 100 : 0.0;
        }
        
        public double getStorageUtilization() {
            return totalStorageTB > 0 ? (double) usedStorageTB / totalStorageTB * 100 : 0.0;
        }
    }
    
    // Utility methods
    private long hash(String key) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] digest = md.digest(key.getBytes());
            long hash = 0;
            for (int i = 0; i < 8; i++) {
                hash = (hash << 8) | (digest[i] & 0xFF);
            }
            return hash;
        } catch (NoSuchAlgorithmException e) {
            return key.hashCode();
        }
    }
    
    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
        // Simplified distance calculation using Haversine formula
        double R = 6371; // Earth radius in kilometers
        double dLat = Math.toRadians(lat2 - lat1);
        double dLon = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) *
                  Math.sin(dLon / 2) * Math.sin(dLon / 2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        return R * c;
    }
    
    /**
     * Main demonstration method
     */
    public static void main(String[] args) {
        System.out.println("🌐 भारतीय CDN Consistent Hashing System");
        System.out.println("=" + "=".repeat(60));
        
        ConsistentHashingCDN cdn = new ConsistentHashingCDN();
        
        // Generate sample content requests from different Indian cities
        ContentRequest[] sampleRequests = {
            new ContentRequest("REQ_001", "https://example.com/bollywood-movie.mp4", "video", 
                             850000, "Mumbai", 19.0760, 72.8777, 3),
            new ContentRequest("REQ_002", "https://example.com/product-image.jpg", "image", 
                             250, "Delhi", 28.5355, 77.3910, 1),
            new ContentRequest("REQ_003", "https://example.com/app-update.apk", "application", 
                             45000, "Bangalore", 12.9141, 77.6101, 2),
            new ContentRequest("REQ_004", "https://example.com/news-article.html", "document", 
                             15, "Chennai", 13.0827, 80.2707, 1),
            new ContentRequest("REQ_005", "https://example.com/startup-pitch.pdf", "document", 
                             5200, "Hyderabad", 17.4435, 78.3772, 2),
            new ContentRequest("REQ_006", "https://example.com/cricket-highlights.mp4", "video", 
                             1200000, "Kolkata", 22.5726, 88.3639, 3),
            new ContentRequest("REQ_007", "https://example.com/ecommerce-banner.png", "image", 
                             180, "Pune", 18.5679, 73.9143, 1),
            new ContentRequest("REQ_008", "https://example.com/music-album.mp3", "audio", 
                             8500, "Ahmedabad", 23.0225, 72.5714, 2)
        };
        
        System.out.println("\n📥 Processing Content Requests:");
        System.out.println("-" + "-".repeat(70));
        
        List<ContentDeliveryResult> results = new ArrayList<>();
        
        for (ContentRequest request : sampleRequests) {
            ContentDeliveryResult result = cdn.processRequest(request);
            results.add(result);
            
            System.out.printf("Request %s: %s (%s, %dKB) -> %s%n",
                request.requestId, request.contentType, request.userLocation, 
                request.contentSizeKB, result.success ? "✅ SUCCESS" : "❌ FAILED");
            System.out.printf("  Via: %s, Response: %dms%n", 
                result.deliveryInfo, result.responseTimeMs);
        }
        
        // Display statistics
        System.out.println("\n📊 CDN Performance Statistics:");
        System.out.println("=" + "=".repeat(50));
        
        CDNStatistics stats = cdn.getStatistics();
        
        System.out.printf("System Overview:%n");
        System.out.printf("  Total Nodes: %d (Healthy: %d)%n", stats.totalNodes, stats.healthyNodes);
        System.out.printf("  Total Bandwidth: %d Gbps (Used: %.1f%%)%n", 
            stats.totalBandwidthGbps, stats.getBandwidthUtilization());
        System.out.printf("  Total Storage: %d TB (Used: %.1f%%)%n", 
            stats.totalStorageTB, stats.getStorageUtilization());
        System.out.printf("  Success Rate: %.2f%%  (%d/%d requests)%n", 
            stats.getSuccessRate(), stats.successfulRequests, stats.totalRequests);
        System.out.printf("  Average Response Time: %.1f ms%n", stats.avgResponseTime);
        
        System.out.printf("%nRegional Distribution:%n");
        for (Map.Entry<String, Integer> entry : stats.regionDistribution.entrySet()) {
            System.out.printf("  %s: %d nodes%n", entry.getKey(), entry.getValue());
        }
        
        System.out.printf("%nProvider Distribution:%n");
        for (Map.Entry<String, Integer> entry : stats.providerDistribution.entrySet()) {
            System.out.printf("  %s: %d nodes%n", entry.getKey(), entry.getValue());
        }
        
        // Demonstrate adding and removing nodes
        System.out.println("\n🔧 Node Management Demo:");
        System.out.println("-" + "-".repeat(30));
        
        // Add new edge node in Kochi
        CDNNode kochiNode = new CDNNode("KOCHI_EDGE_001", "Kochi", "South India", "EdgeNetwork",
                                       "Kochi-InfoPark", 9.9312, 76.2673, 8000, 40);
        cdn.addNode(kochiNode);
        
        // Remove a node (simulate maintenance)
        cdn.removeNode("COI_EDGE_001");
        
        // Final statistics
        CDNStatistics finalStats = cdn.getStatistics();
        System.out.printf("Final Network: %d nodes (%d healthy)%n", 
            finalStats.totalNodes, finalStats.healthyNodes);
        
        System.out.println("\n💡 Consistent Hashing Benefits:");
        System.out.println("✅ Minimal key redistribution when nodes are added/removed");
        System.out.println("⚖️ Even load distribution across all nodes");
        System.out.println("🌍 Geographic optimization for better user experience");
        System.out.println("🔄 Automatic failover to nearby nodes");
        System.out.println("📈 Scalable architecture for growing content demands");
        
        System.out.println("\n🚀 Production Enhancements:");
        System.out.println("📊 Real-time health monitoring and auto-scaling");
        System.out.println("🧠 ML-based content popularity prediction");
        System.out.println("⚡ Edge computing integration for dynamic content");
        System.out.println("🔐 Enhanced security with DDoS protection");
        System.out.println("📱 Mobile-first optimization for Indian users");
    }
}