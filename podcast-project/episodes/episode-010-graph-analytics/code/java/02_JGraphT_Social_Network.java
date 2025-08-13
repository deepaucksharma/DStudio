/*
JGraphT Social Network Analysis for Indian Social Media Platforms
Production-grade graph algorithms with community detection

Author: Episode 10 - Graph Analytics at Scale
Context: Social media network analysis - WhatsApp groups, Facebook connections
*/

package com.indiansocial.graph;

import org.jgrapht.*;
import org.jgrapht.alg.clustering.*;
import org.jgrapht.alg.shortestpath.*;
import org.jgrapht.alg.scoring.*;
import org.jgrapht.graph.*;
import org.jgrapht.graph.builder.*;
import org.jgrapht.nio.*;
import org.jgrapht.nio.dot.*;
import org.jgrapht.traverse.*;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.io.*;
import java.time.LocalDateTime;

// Data models for Social Network
class SocialUser {
    private String userId;
    private String name;
    private String city;
    private String language;
    private int age;
    private int followerCount;
    private int followingCount;
    private Set<String> interests;
    private LocalDateTime joinDate;
    
    public SocialUser(String userId, String name, String city, String language, int age) {
        this.userId = userId;
        this.name = name;
        this.city = city;
        this.language = language;
        this.age = age;
        this.interests = new HashSet<>();
        this.joinDate = LocalDateTime.now();
    }
    
    // Getters and setters
    public String getUserId() { return userId; }
    public String getName() { return name; }
    public String getCity() { return city; }
    public String getLanguage() { return language; }
    public int getAge() { return age; }
    public int getFollowerCount() { return followerCount; }
    public void setFollowerCount(int count) { this.followerCount = count; }
    public int getFollowingCount() { return followingCount; }
    public void setFollowingCount(int count) { this.followingCount = count; }
    public Set<String> getInterests() { return interests; }
    public void addInterest(String interest) { this.interests.add(interest); }
    public LocalDateTime getJoinDate() { return joinDate; }
    
    @Override
    public String toString() {
        return String.format("%s (%s) - %s, %s", name, userId, city, language);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        SocialUser user = (SocialUser) obj;
        return Objects.equals(userId, user.userId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(userId);
    }
}

class SocialConnection {
    private String connectionType; // FRIEND, FOLLOW, GROUP_MEMBER, COLLEAGUE
    private double strength; // 0.0 to 1.0
    private LocalDateTime createdAt;
    private Map<String, Object> properties;
    
    public SocialConnection(String connectionType, double strength) {
        this.connectionType = connectionType;
        this.strength = strength;
        this.createdAt = LocalDateTime.now();
        this.properties = new HashMap<>();
    }
    
    public String getConnectionType() { return connectionType; }
    public double getStrength() { return strength; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public Map<String, Object> getProperties() { return properties; }
    
    @Override
    public String toString() {
        return String.format("%s (%.2f)", connectionType, strength);
    }
}

// Main Social Network Analyzer
public class IndianSocialNetworkAnalyzer {
    
    private Graph<SocialUser, SocialConnection> socialGraph;
    private Map<String, SocialUser> users;
    
    // Algorithm instances
    private PageRank<SocialUser, SocialConnection> pageRankAlg;
    private BetweennessCentrality<SocialUser, SocialConnection> betweennessAlg;
    private ClosenessCentrality<SocialUser, SocialConnection> closenessAlg;
    private DijkstraShortestPath<SocialUser, SocialConnection> dijkstraAlg;
    
    // Performance metrics
    private Map<String, Long> performanceMetrics;
    
    public IndianSocialNetworkAnalyzer() {
        System.out.println("📱 Indian Social Network - JGraphT Analytics");
        System.out.println("=".repeat(60));
        
        // Initialize weighted graph for social connections
        socialGraph = new DefaultWeightedGraph<>(SocialConnection.class);
        users = new HashMap<>();
        performanceMetrics = new HashMap<>();
        
        // Initialize algorithms
        pageRankAlg = new PageRank<>(socialGraph);
        betweennessAlg = new BetweennessCentrality<>(socialGraph);
        closenessAlg = new ClosenessCentrality<>(socialGraph);
        dijkstraAlg = new DijkstraShortestPath<>(socialGraph);
        
        System.out.println("✅ Social Network Analyzer initialized");
        
        // Load demo social network data
        loadDemoSocialNetwork();
        
        // Run comprehensive analysis
        runSocialNetworkAnalysis();
    }
    
    private void loadDemoSocialNetwork() {
        System.out.println("\n🏗️  Building Indian Social Media Network...");
        
        // Create diverse Indian social media users
        SocialUser[] demoUsers = {
            // Tier 1 Cities
            new SocialUser("mumbai_raj_001", "Raj Sharma", "Mumbai", "Hindi", 28),
            new SocialUser("delhi_priya_002", "Priya Gupta", "Delhi", "Hindi", 25),
            new SocialUser("blr_arjun_003", "Arjun Krishna", "Bangalore", "Kannada", 30),
            new SocialUser("chennai_meera_004", "Meera Iyer", "Chennai", "Tamil", 27),
            new SocialUser("hyd_vikram_005", "Vikram Reddy", "Hyderabad", "Telugu", 32),
            new SocialUser("kolkata_anita_006", "Anita Das", "Kolkata", "Bengali", 29),
            new SocialUser("pune_rohit_007", "Rohit Patil", "Pune", "Marathi", 26),
            
            // Tier 2 Cities
            new SocialUser("jaipur_kavya_008", "Kavya Agarwal", "Jaipur", "Hindi", 24),
            new SocialUser("lucknow_amit_009", "Amit Verma", "Lucknow", "Hindi", 31),
            new SocialUser("indore_pooja_010", "Pooja Jain", "Indore", "Hindi", 28),
            new SocialUser("kochi_ravi_011", "Ravi Nair", "Kochi", "Malayalam", 33),
            new SocialUser("chandigarh_simran_012", "Simran Singh", "Chandigarh", "Punjabi", 26),
            
            // Influencers and Content Creators
            new SocialUser("influencer_tech_013", "Tech Guru", "Mumbai", "English", 35),
            new SocialUser("influencer_food_014", "Food Explorer", "Delhi", "Hindi", 29),
            new SocialUser("influencer_travel_015", "Travel Nomad", "Goa", "English", 27),
            
            // Small Town Users
            new SocialUser("mysore_deepak_016", "Deepak Kumar", "Mysore", "Kannada", 25),
            new SocialUser("nashik_sunita_017", "Sunita Kulkarni", "Nashik", "Marathi", 30),
            new SocialUser("trichy_murugan_018", "Murugan S", "Trichy", "Tamil", 28),
            new SocialUser("bhubaneswar_sita_019", "Sita Panda", "Bhubaneswar", "Odia", 26),
            new SocialUser("jammu_manish_020", "Manish Khurana", "Jammu", "Hindi", 31)
        };
        
        // Add users to graph and set their interests
        for (SocialUser user : demoUsers) {
            addUserToGraph(user);
            assignInterestsToUser(user);
        }
        
        // Create realistic social connections
        createSocialConnections(demoUsers);
        
        System.out.printf("✅ Social network created: %d users, %d connections\n", 
                         socialGraph.vertexSet().size(), socialGraph.edgeSet().size());
    }
    
    private void addUserToGraph(SocialUser user) {
        socialGraph.addVertex(user);
        users.put(user.getUserId(), user);
        
        // Set follower/following counts based on city tier and interests
        int baseFollowers = getBaseFollowerCount(user.getCity());
        user.setFollowerCount(baseFollowers + new Random().nextInt(baseFollowers));
        user.setFollowingCount(baseFollowers / 2 + new Random().nextInt(baseFollowers / 2));
    }
    
    private void assignInterestsToUser(SocialUser user) {
        String[] allInterests = {
            "Technology", "Food", "Travel", "Movies", "Sports", "Music", 
            "Fashion", "Photography", "Gaming", "Business", "Health", "Education",
            "Cricket", "Bollywood", "Regional_Cinema", "Startups", "Finance"
        };
        
        // Assign 3-6 interests per user
        int numInterests = 3 + new Random().nextInt(4);
        Set<String> userInterests = new HashSet<>();
        
        while (userInterests.size() < numInterests) {
            String interest = allInterests[new Random().nextInt(allInterests.length)];
            userInterests.add(interest);
        }
        
        for (String interest : userInterests) {
            user.addInterest(interest);
        }
    }
    
    private int getBaseFollowerCount(String city) {
        // Different base follower counts based on city tier
        Map<String, Integer> cityTiers = Map.of(
            "Mumbai", 1000, "Delhi", 1000, "Bangalore", 800, "Chennai", 800,
            "Hyderabad", 700, "Kolkata", 700, "Pune", 600,
            "Jaipur", 400, "Lucknow", 400, "Indore", 400,
            "Kochi", 300, "Chandigarh", 300, "Goa", 500
        );
        return cityTiers.getOrDefault(city, 200);
    }
    
    private void createSocialConnections(SocialUser[] users) {
        Random random = new Random(42); // Seed for reproducible results
        
        // Create connections based on multiple factors
        for (int i = 0; i < users.length; i++) {
            for (int j = i + 1; j < users.length; j++) {
                SocialUser user1 = users[i];
                SocialUser user2 = users[j];
                
                double connectionProbability = calculateConnectionProbability(user1, user2);
                
                if (random.nextDouble() < connectionProbability) {
                    String connectionType = determineConnectionType(user1, user2);
                    double connectionStrength = calculateConnectionStrength(user1, user2, connectionType);
                    
                    SocialConnection connection = new SocialConnection(connectionType, connectionStrength);
                    
                    // Add mutual properties
                    connection.getProperties().put("mutual_interests", 
                        getMutualInterests(user1, user2).size());
                    connection.getProperties().put("age_difference", 
                        Math.abs(user1.getAge() - user2.getAge()));
                    
                    socialGraph.addEdge(user1, user2, connection);
                    socialGraph.setEdgeWeight(connection, connectionStrength);
                }
            }
        }
        
        // Add some high-influence connections (influencers)
        createInfluencerConnections(users);
    }
    
    private double calculateConnectionProbability(SocialUser user1, SocialUser user2) {
        double probability = 0.1; // Base probability
        
        // Same city increases probability significantly
        if (user1.getCity().equals(user2.getCity())) {
            probability += 0.4;
        }
        
        // Same language increases probability
        if (user1.getLanguage().equals(user2.getLanguage())) {
            probability += 0.2;
        }
        
        // Similar age increases probability
        int ageDiff = Math.abs(user1.getAge() - user2.getAge());
        if (ageDiff <= 5) {
            probability += 0.3;
        } else if (ageDiff <= 10) {
            probability += 0.1;
        }
        
        // Common interests increase probability
        int commonInterests = getMutualInterests(user1, user2).size();
        probability += commonInterests * 0.15;
        
        // Cap probability at 0.9
        return Math.min(0.9, probability);
    }
    
    private String determineConnectionType(SocialUser user1, SocialUser user2) {
        Random random = new Random();
        
        // Same city users are more likely to be friends
        if (user1.getCity().equals(user2.getCity())) {
            return random.nextDouble() < 0.7 ? "FRIEND" : "FOLLOW";
        }
        
        // Different cities are more likely to be follows
        if (user1.getFollowerCount() > user2.getFollowerCount() * 2 || 
            user2.getFollowerCount() > user1.getFollowerCount() * 2) {
            return "FOLLOW";
        }
        
        // Professional connections for similar interests
        int commonInterests = getMutualInterests(user1, user2).size();
        if (commonInterests >= 3 && (user1.getInterests().contains("Business") || 
                                    user2.getInterests().contains("Business"))) {
            return "COLLEAGUE";
        }
        
        return random.nextDouble() < 0.6 ? "FRIEND" : "FOLLOW";
    }
    
    private double calculateConnectionStrength(SocialUser user1, SocialUser user2, String connectionType) {
        double baseStrength = 0.5;
        
        // Connection type affects strength
        switch (connectionType) {
            case "FRIEND":
                baseStrength = 0.8;
                break;
            case "COLLEAGUE":
                baseStrength = 0.6;
                break;
            case "FOLLOW":
                baseStrength = 0.3;
                break;
            case "GROUP_MEMBER":
                baseStrength = 0.4;
                break;
        }
        
        // Mutual interests increase strength
        int mutualInterests = getMutualInterests(user1, user2).size();
        baseStrength += mutualInterests * 0.05;
        
        // Same city increases strength
        if (user1.getCity().equals(user2.getCity())) {
            baseStrength += 0.1;
        }
        
        // Similar age increases strength
        int ageDiff = Math.abs(user1.getAge() - user2.getAge());
        if (ageDiff <= 3) {
            baseStrength += 0.1;
        } else if (ageDiff <= 7) {
            baseStrength += 0.05;
        }
        
        // Add some randomness
        Random random = new Random();
        baseStrength += (random.nextDouble() - 0.5) * 0.2;
        
        return Math.min(1.0, Math.max(0.1, baseStrength));
    }
    
    private Set<String> getMutualInterests(SocialUser user1, SocialUser user2) {
        Set<String> mutual = new HashSet<>(user1.getInterests());
        mutual.retainAll(user2.getInterests());
        return mutual;
    }
    
    private void createInfluencerConnections(SocialUser[] users) {
        // Find influencers (users with "influencer" in their ID)
        List<SocialUser> influencers = Arrays.stream(users)
            .filter(user -> user.getUserId().contains("influencer"))
            .collect(Collectors.toList());
        
        Random random = new Random(42);
        
        for (SocialUser influencer : influencers) {
            // Influencers get many followers
            int additionalFollowers = 15 + random.nextInt(10);
            int count = 0;
            
            for (SocialUser user : users) {
                if (!user.equals(influencer) && count < additionalFollowers) {
                    if (random.nextDouble() < 0.8) { // High probability of following influencer
                        SocialConnection followConnection = new SocialConnection("FOLLOW", 0.6);
                        followConnection.getProperties().put("influencer_relationship", true);
                        
                        if (!socialGraph.containsEdge(user, influencer)) {
                            socialGraph.addEdge(user, influencer, followConnection);
                            socialGraph.setEdgeWeight(followConnection, 0.6);
                            count++;
                        }
                    }
                }
            }
        }
    }
    
    private void runSocialNetworkAnalysis() {
        System.out.println("\n📊 Running Comprehensive Social Network Analysis...");
        
        // 1. PageRank Analysis
        analyzePageRank();
        
        // 2. Centrality Analysis
        analyzeCentrality();
        
        // 3. Community Detection
        detectCommunities();
        
        // 4. Path Analysis
        analyzeShortestPaths();
        
        // 5. Network Properties
        analyzeNetworkProperties();
        
        // 6. Influence Analysis
        analyzeInfluence();
        
        // Display performance summary
        displayPerformanceSummary();
    }
    
    private void analyzePageRank() {
        System.out.println("\n🏆 PageRank Analysis (User Importance):");
        System.out.println("-".repeat(45));
        
        long startTime = System.currentTimeMillis();
        
        Map<SocialUser, Double> pageRankScores = pageRankAlg.getScores();
        
        // Sort users by PageRank score
        List<Map.Entry<SocialUser, Double>> sortedByPageRank = pageRankScores.entrySet().stream()
            .sorted(Map.Entry.<SocialUser, Double>comparingByValue().reversed())
            .collect(Collectors.toList());
        
        // Display top 10 most important users
        System.out.println("Top 10 Most Important Users:");
        for (int i = 0; i < Math.min(10, sortedByPageRank.size()); i++) {
            Map.Entry<SocialUser, Double> entry = sortedByPageRank.get(i);
            SocialUser user = entry.getKey();
            double score = entry.getValue();
            
            System.out.printf("%2d. %s (Score: %.6f)\n", i + 1, user.toString(), score);
            System.out.printf("    Interests: %s\n", 
                String.join(", ", user.getInterests().stream().limit(3).collect(Collectors.toList())));
            System.out.printf("    Connections: %d\n", socialGraph.degreeOf(user));
        }
        
        long endTime = System.currentTimeMillis();
        performanceMetrics.put("PageRank", endTime - startTime);
    }
    
    private void analyzeCentrality() {
        System.out.println("\n🎯 Centrality Analysis:");
        System.out.println("-".repeat(25));
        
        long startTime = System.currentTimeMillis();
        
        // Betweenness Centrality
        Map<SocialUser, Double> betweennessScores = betweennessAlg.getScores();
        SocialUser mostBetween = Collections.max(betweennessScores.entrySet(), 
            Map.Entry.comparingByValue()).getKey();
        
        // Closeness Centrality
        Map<SocialUser, Double> closenessScores = closenessAlg.getScores();
        SocialUser mostClose = Collections.max(closenessScores.entrySet(), 
            Map.Entry.comparingByValue()).getKey();
        
        System.out.printf("Highest Betweenness Centrality: %s (%.6f)\n", 
            mostBetween.toString(), betweennessScores.get(mostBetween));
        System.out.printf("   Role: Bridge between different communities\n");
        
        System.out.printf("\nHighest Closeness Centrality: %s (%.6f)\n", 
            mostClose.toString(), closenessScores.get(mostClose));
        System.out.printf("   Role: Most efficiently connected to all users\n");
        
        long endTime = System.currentTimeMillis();
        performanceMetrics.put("Centrality", endTime - startTime);
    }
    
    private void detectCommunities() {
        System.out.println("\n🏘️  Community Detection:");
        System.out.println("-".repeat(25));
        
        long startTime = System.currentTimeMillis();
        
        // Use Label Propagation for community detection
        LabelPropagationClustering<SocialUser, SocialConnection> clustering = 
            new LabelPropagationClustering<>(socialGraph);
        
        clustering.setClustering(clustering.getClustering());
        Set<Set<SocialUser>> communities = clustering.getClusters();
        
        System.out.printf("Detected %d communities:\n\n", communities.size());
        
        int communityId = 1;
        for (Set<SocialUser> community : communities) {
            if (community.size() >= 3) { // Only show communities with 3+ members
                System.out.printf("Community %d (%d members):\n", communityId, community.size());
                
                // Analyze community characteristics
                Map<String, Integer> cityCount = new HashMap<>();
                Map<String, Integer> languageCount = new HashMap<>();
                Map<String, Integer> interestCount = new HashMap<>();
                
                for (SocialUser user : community) {
                    cityCount.put(user.getCity(), cityCount.getOrDefault(user.getCity(), 0) + 1);
                    languageCount.put(user.getLanguage(), languageCount.getOrDefault(user.getLanguage(), 0) + 1);
                    
                    for (String interest : user.getInterests()) {
                        interestCount.put(interest, interestCount.getOrDefault(interest, 0) + 1);
                    }
                }
                
                // Find dominant characteristics
                String dominantCity = Collections.max(cityCount.entrySet(), 
                    Map.Entry.comparingByValue()).getKey();
                String dominantLanguage = Collections.max(languageCount.entrySet(), 
                    Map.Entry.comparingByValue()).getKey();
                String dominantInterest = Collections.max(interestCount.entrySet(), 
                    Map.Entry.comparingByValue()).getKey();
                
                System.out.printf("   Dominant City: %s (%d users)\n", 
                    dominantCity, cityCount.get(dominantCity));
                System.out.printf("   Dominant Language: %s (%d users)\n", 
                    dominantLanguage, languageCount.get(dominantLanguage));
                System.out.printf("   Popular Interest: %s (%d users)\n", 
                    dominantInterest, interestCount.get(dominantInterest));
                
                // Show a few representative members
                System.out.printf("   Members: ");
                community.stream().limit(3).forEach(user -> 
                    System.out.printf("%s, ", user.getName()));
                if (community.size() > 3) {
                    System.out.printf("and %d more", community.size() - 3);
                }
                System.out.println("\n");
                
                communityId++;
            }
        }
        
        long endTime = System.currentTimeMillis();
        performanceMetrics.put("Community Detection", endTime - startTime);
    }
    
    private void analyzeShortestPaths() {
        System.out.println("🛤️  Shortest Path Analysis:");
        System.out.println("-".repeat(30));
        
        long startTime = System.currentTimeMillis();
        
        // Sample path analysis between different city users
        List<SocialUser> userList = new ArrayList<>(socialGraph.vertexSet());
        Random random = new Random(42);
        
        for (int i = 0; i < 5; i++) {
            SocialUser source = userList.get(random.nextInt(userList.size()));
            SocialUser target = userList.get(random.nextInt(userList.size()));
            
            if (!source.equals(target)) {
                GraphPath<SocialUser, SocialConnection> path = dijkstraAlg.getPath(source, target);
                
                if (path != null) {
                    System.out.printf("\nPath %d: %s → %s\n", i + 1, 
                        source.getName(), target.getName());
                    System.out.printf("   Length: %d hops, Weight: %.2f\n", 
                        path.getLength(), path.getWeight());
                    
                    // Show intermediate connections
                    List<SocialUser> pathVertices = path.getVertexList();
                    if (pathVertices.size() > 2) {
                        System.out.printf("   Route: %s", pathVertices.get(0).getName());
                        for (int j = 1; j < pathVertices.size(); j++) {
                            System.out.printf(" → %s", pathVertices.get(j).getName());
                        }
                        System.out.println();
                    }
                }
            }
        }
        
        long endTime = System.currentTimeMillis();
        performanceMetrics.put("Shortest Paths", endTime - startTime);
    }
    
    private void analyzeNetworkProperties() {
        System.out.println("\n📈 Network Properties:");
        System.out.println("-".repeat(22));
        
        int vertices = socialGraph.vertexSet().size();
        int edges = socialGraph.edgeSet().size();
        
        // Calculate average degree
        double avgDegree = (2.0 * edges) / vertices;
        
        // Calculate clustering coefficient (simplified)
        double clusteringCoefficient = calculateClusteringCoefficient();
        
        // Degree distribution
        Map<Integer, Integer> degreeDistribution = new HashMap<>();
        for (SocialUser user : socialGraph.vertexSet()) {
            int degree = socialGraph.degreeOf(user);
            degreeDistribution.put(degree, degreeDistribution.getOrDefault(degree, 0) + 1);
        }
        
        // Find max degree
        int maxDegree = degreeDistribution.keySet().stream().mapToInt(Integer::intValue).max().orElse(0);
        
        System.out.printf("Network Size: %d users, %d connections\n", vertices, edges);
        System.out.printf("Average Degree: %.2f\n", avgDegree);
        System.out.printf("Max Degree: %d\n", maxDegree);
        System.out.printf("Clustering Coefficient: %.4f\n", clusteringCoefficient);
        System.out.printf("Network Density: %.6f\n", (2.0 * edges) / (vertices * (vertices - 1)));
        
        // Show degree distribution (top 5)
        System.out.println("\nDegree Distribution (Top 5):");
        degreeDistribution.entrySet().stream()
            .sorted(Map.Entry.<Integer, Integer>comparingByValue().reversed())
            .limit(5)
            .forEach(entry -> System.out.printf("   Degree %d: %d users\n", 
                entry.getKey(), entry.getValue()));
    }
    
    private double calculateClusteringCoefficient() {
        double totalCoefficient = 0.0;
        int validVertices = 0;
        
        for (SocialUser user : socialGraph.vertexSet()) {
            Set<SocialUser> neighbors = new HashSet<>();
            
            for (SocialConnection edge : socialGraph.edgesOf(user)) {
                SocialUser neighbor = socialGraph.getEdgeSource(edge).equals(user) ? 
                    socialGraph.getEdgeTarget(edge) : socialGraph.getEdgeSource(edge);
                neighbors.add(neighbor);
            }
            
            int k = neighbors.size();
            if (k >= 2) {
                int actualConnections = 0;
                
                for (SocialUser neighbor1 : neighbors) {
                    for (SocialUser neighbor2 : neighbors) {
                        if (!neighbor1.equals(neighbor2) && socialGraph.containsEdge(neighbor1, neighbor2)) {
                            actualConnections++;
                        }
                    }
                }
                
                actualConnections /= 2; // Each edge counted twice
                int possibleConnections = k * (k - 1) / 2;
                
                if (possibleConnections > 0) {
                    totalCoefficient += (double) actualConnections / possibleConnections;
                    validVertices++;
                }
            }
        }
        
        return validVertices > 0 ? totalCoefficient / validVertices : 0.0;
    }
    
    private void analyzeInfluence() {
        System.out.println("\n🌟 Influence Analysis:");
        System.out.println("-".repeat(20));
        
        // Calculate influence scores based on PageRank and connections
        Map<SocialUser, Double> pageRankScores = pageRankAlg.getScores();
        Map<SocialUser, Double> influenceScores = new HashMap<>();
        
        for (SocialUser user : socialGraph.vertexSet()) {
            double pageRankScore = pageRankScores.getOrDefault(user, 0.0);
            int degree = socialGraph.degreeOf(user);
            int followerCount = user.getFollowerCount();
            
            // Combined influence score
            double influenceScore = (pageRankScore * 0.4) + 
                                  (degree / 20.0 * 0.3) + 
                                  (Math.log(followerCount + 1) / 10.0 * 0.3);
            
            influenceScores.put(user, influenceScore);
        }
        
        // Top influencers
        List<Map.Entry<SocialUser, Double>> topInfluencers = influenceScores.entrySet().stream()
            .sorted(Map.Entry.<SocialUser, Double>comparingByValue().reversed())
            .limit(5)
            .collect(Collectors.toList());
        
        System.out.println("Top 5 Most Influential Users:");
        for (int i = 0; i < topInfluencers.size(); i++) {
            Map.Entry<SocialUser, Double> entry = topInfluencers.get(i);
            SocialUser user = entry.getKey();
            
            System.out.printf("%d. %s (Score: %.4f)\n", i + 1, user.toString(), entry.getValue());
            System.out.printf("   Followers: %,d | Connections: %d\n", 
                user.getFollowerCount(), socialGraph.degreeOf(user));
            System.out.printf("   Top Interests: %s\n", 
                user.getInterests().stream().limit(2).collect(Collectors.joining(", ")));
        }
    }
    
    private void displayPerformanceSummary() {
        System.out.println("\n⚡ Performance Summary:");
        System.out.println("-".repeat(25));
        
        long totalTime = performanceMetrics.values().stream().mapToLong(Long::longValue).sum();
        
        for (Map.Entry<String, Long> entry : performanceMetrics.entrySet()) {
            System.out.printf("• %-20s: %d ms\n", entry.getKey(), entry.getValue());
        }
        System.out.printf("• %-20s: %d ms\n", "Total Analysis", totalTime);
        
        // Memory estimation
        long estimatedMemory = (socialGraph.vertexSet().size() * 200L + 
                               socialGraph.edgeSet().size() * 100L) / 1024;
        System.out.printf("• %-20s: ~%d KB\n", "Memory Usage", estimatedMemory);
    }
    
    public static void main(String[] args) {
        System.setProperty("java.awt.headless", "true"); // For server environments
        
        try {
            new IndianSocialNetworkAnalyzer();
            
            System.out.println("\n" + "=".repeat(60));
            System.out.println("📚 LEARNING POINTS:");
            System.out.println("• JGraphT Java mein powerful graph algorithms provide karta hai");
            System.out.println("• Social networks mein community detection natural groups reveal karta hai");
            System.out.println("• PageRank algorithm user importance accurately measure karta hai");
            System.out.println("• Centrality measures different types of influence identify karte hai");
            System.out.println("• Shortest path algorithms social connections trace karte hai");
            System.out.println("• Graph properties network behavior understand karne mein help karte hai");
            System.out.println("• Indian social media networks unique patterns show karte hai");
            
        } catch (Exception e) {
            System.err.println("Error in Social Network Analysis: " + e.getMessage());
            e.printStackTrace();
        }
    }
}