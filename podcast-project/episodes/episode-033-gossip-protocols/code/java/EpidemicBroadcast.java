/**
 * Epidemic Broadcast Protocol for Event Dissemination
 * ===================================================
 * 
 * Ola Cab Dispatch System: जब कोई cab available हो जाए तो कैसे सभी nearby
 * drivers को efficiently inform करें using epidemic-style broadcasting?
 * 
 * This implements an epidemic broadcast protocol that spreads information
 * across a network using gossip-style communication patterns.
 * 
 * Author: Code Developer Agent
 * Episode: 33 - Gossip Protocols
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.Instant;

enum MessageType {
    RIDE_REQUEST,     // नई ride request
    DRIVER_AVAILABLE, // Driver available हो गया
    RIDE_ACCEPTED,    // Ride accept हो गई
    TRAFFIC_UPDATE,   // Traffic condition update
    SURGE_PRICING,    // Surge pricing active
    EMERGENCY_ALERT   // Emergency broadcast
}

enum InfectionState {
    SUSCEPTIBLE,  // अभी तक message नहीं मिला
    INFECTED,     // Message मिल गया, अब spread कर रहा
    RECOVERED     // Message spread कर चुका, अब inactive
}

class BroadcastMessage {
    private final String messageId;
    private final MessageType type;
    private final String content;
    private final String sourceId;
    private final long timestamp;
    private final int priority; // 1 = highest, 5 = lowest
    private final Map<String, Object> metadata;
    private int hopCount;
    private final int maxHops;
    
    public BroadcastMessage(String messageId, MessageType type, String content, 
                           String sourceId, int priority, int maxHops) {
        this.messageId = messageId;
        this.type = type;
        this.content = content;
        this.sourceId = sourceId;
        this.timestamp = System.currentTimeMillis();
        this.priority = priority;
        this.maxHops = maxHops;
        this.hopCount = 0;
        this.metadata = new HashMap<>();
    }
    
    public boolean isExpired(long ttlMs) {
        return System.currentTimeMillis() - timestamp > ttlMs;
    }
    
    public boolean canPropagate() {
        return hopCount < maxHops;
    }
    
    public void incrementHops() {
        hopCount++;
    }
    
    // Getters
    public String getMessageId() { return messageId; }
    public MessageType getType() { return type; }
    public String getContent() { return content; }
    public String getSourceId() { return sourceId; }
    public long getTimestamp() { return timestamp; }
    public int getPriority() { return priority; }
    public Map<String, Object> getMetadata() { return metadata; }
    public int getHopCount() { return hopCount; }
    public int getMaxHops() { return maxHops; }
    
    @Override
    public String toString() {
        return String.format("Message{id=%s, type=%s, source=%s, hops=%d/%d, priority=%d}", 
                           messageId, type, sourceId, hopCount, maxHops, priority);
    }
}

class EpidemicState {
    private final String nodeId;
    private InfectionState state;
    private final Set<String> receivedMessages;
    private final Map<String, BroadcastMessage> activeMessages;
    private double infectionProbability;
    private long lastStateChange;
    private int spreadCount;
    
    public EpidemicState(String nodeId) {
        this.nodeId = nodeId;
        this.state = InfectionState.SUSCEPTIBLE;
        this.receivedMessages = ConcurrentHashMap.newKeySet();
        this.activeMessages = new ConcurrentHashMap<>();
        this.infectionProbability = 0.8; // 80% chance to spread
        this.lastStateChange = System.currentTimeMillis();
        this.spreadCount = 0;
    }
    
    public boolean receiveMessage(BroadcastMessage message) {
        if (receivedMessages.contains(message.getMessageId())) {
            return false; // Already received
        }
        
        receivedMessages.add(message.getMessageId());
        
        // Priority-based infection probability
        double adjustedProbability = infectionProbability * (6 - message.getPriority()) / 5.0;
        
        if (Math.random() < adjustedProbability) {
            activeMessages.put(message.getMessageId(), message);
            
            if (state == InfectionState.SUSCEPTIBLE) {
                state = InfectionState.INFECTED;
                lastStateChange = System.currentTimeMillis();
            }
            
            return true;
        }
        
        return false;
    }
    
    public List<BroadcastMessage> getMessagesToSpread() {
        if (state != InfectionState.INFECTED) {
            return Collections.emptyList();
        }
        
        List<BroadcastMessage> messages = new ArrayList<>();
        Iterator<BroadcastMessage> iterator = activeMessages.values().iterator();
        
        while (iterator.hasNext()) {
            BroadcastMessage message = iterator.next();
            
            // Check if message is still worth spreading
            if (message.canPropagate() && !message.isExpired(300000)) { // 5 minutes TTL
                messages.add(message);
                spreadCount++;
            } else {
                iterator.remove(); // Remove expired or max-hop messages
            }
        }
        
        // Transition to RECOVERED if no more messages to spread
        if (activeMessages.isEmpty() && state == InfectionState.INFECTED) {
            state = InfectionState.RECOVERED;
            lastStateChange = System.currentTimeMillis();
        }
        
        return messages;
    }
    
    public void resetToSusceptible() {
        // Allow node to become susceptible again after some time
        if (state == InfectionState.RECOVERED && 
            System.currentTimeMillis() - lastStateChange > 60000) { // 1 minute
            state = InfectionState.SUSCEPTIBLE;
            lastStateChange = System.currentTimeMillis();
        }
    }
    
    // Getters
    public String getNodeId() { return nodeId; }
    public InfectionState getState() { return state; }
    public int getReceivedMessageCount() { return receivedMessages.size(); }
    public int getActiveMessageCount() { return activeMessages.size(); }
    public int getSpreadCount() { return spreadCount; }
    public double getInfectionProbability() { return infectionProbability; }
    public void setInfectionProbability(double probability) { this.infectionProbability = probability; }
}

public class EpidemicBroadcast {
    private final String nodeId;
    private final String driverName;
    private final String location;
    private final EpidemicState epidemicState;
    
    // Network topology
    private final Set<String> neighbors;
    private final Map<String, Double> neighborDistances; // Geographic distances
    
    // Epidemic parameters
    private final int epidemicFanout;
    private final long epidemicInterval; // milliseconds
    private final double transmissionProbability;
    
    // Threading and scheduling
    private final ScheduledExecutorService scheduler;
    private final Random random;
    
    // Statistics
    private final AtomicInteger messagesOriginated = new AtomicInteger(0);
    private final AtomicInteger messagesReceived = new AtomicInteger(0);
    private final AtomicInteger messagesForwarded = new AtomicInteger(0);
    private final AtomicInteger epidemicRounds = new AtomicInteger(0);
    
    // Message generation
    private int messageCounter = 0;
    
    public EpidemicBroadcast(String nodeId, String driverName, String location) {
        this.nodeId = nodeId;
        this.driverName = driverName;
        this.location = location;
        this.epidemicState = new EpidemicState(nodeId);
        
        this.neighbors = ConcurrentHashMap.newKeySet();
        this.neighborDistances = new ConcurrentHashMap<>();
        
        // Epidemic configuration
        this.epidemicFanout = 3; // Spread to 3 neighbors per round
        this.epidemicInterval = 2000; // 2 seconds
        this.transmissionProbability = 0.9; // 90% transmission success
        
        this.scheduler = Executors.newScheduledThreadPool(2);
        this.random = new Random();
        
        startEpidemicProtocol();
        
        System.out.println("🚗 Ola Driver " + driverName + " connected at " + location);
    }
    
    public void addNeighbor(String neighborId, double distance) {
        neighbors.add(neighborId);
        neighborDistances.put(neighborId, distance);
        
        // Adjust infection probability based on network density
        adjustInfectionProbability();
    }
    
    private void adjustInfectionProbability() {
        // More neighbors = lower individual infection probability to control spread
        int neighborCount = neighbors.size();
        double baseProbability = 0.8;
        double adjustedProbability = baseProbability * Math.min(1.0, 5.0 / neighborCount);
        epidemicState.setInfectionProbability(adjustedProbability);
    }
    
    public void broadcastMessage(MessageType type, String content, int priority) {
        String messageId = nodeId + "_" + (++messageCounter) + "_" + System.currentTimeMillis();
        
        int maxHops = calculateMaxHops(type, priority);
        BroadcastMessage message = new BroadcastMessage(
            messageId, type, content, nodeId, priority, maxHops
        );
        
        // Add location metadata
        message.getMetadata().put("location", location);
        message.getMetadata().put("driver", driverName);
        
        // Infect self with the message
        epidemicState.receiveMessage(message);
        messagesOriginated.incrementAndGet();
        
        System.out.println("📢 " + driverName + " broadcast: " + type + " - " + content);
        
        // Immediate epidemic spread
        scheduler.schedule(this::performEpidemicRound, 100, TimeUnit.MILLISECONDS);
    }
    
    private int calculateMaxHops(MessageType type, int priority) {
        // Higher priority messages get more hops
        switch (type) {
            case EMERGENCY_ALERT:
                return 10; // Maximum spread for emergencies
            case RIDE_REQUEST:
                return 6;  // Medium spread for ride requests
            case DRIVER_AVAILABLE:
                return 4;  // Limited spread for driver availability
            case TRAFFIC_UPDATE:
                return 5;  // Good spread for traffic info
            case SURGE_PRICING:
                return 7;  // Wide spread for pricing updates
            default:
                return 3;  // Default limited spread
        }
    }
    
    private void startEpidemicProtocol() {
        scheduler.scheduleAtFixedRate(this::performEpidemicRound, 
                                    epidemicInterval, epidemicInterval, TimeUnit.MILLISECONDS);
                                    
        scheduler.scheduleAtFixedRate(this::performMaintenance, 
                                    30000, 30000, TimeUnit.MILLISECONDS); // Every 30 seconds
    }
    
    private void performEpidemicRound() {
        epidemicRounds.incrementAndGet();
        
        // Get messages to spread
        List<BroadcastMessage> messagesToSpread = epidemicState.getMessagesToSpread();
        
        if (messagesToSpread.isEmpty()) {
            return;
        }
        
        // Select neighbors for epidemic spread
        List<String> selectedNeighbors = selectEpidemicTargets();
        
        if (selectedNeighbors.isEmpty()) {
            return;
        }
        
        // Spread messages to selected neighbors
        for (BroadcastMessage message : messagesToSpread) {
            for (String neighborId : selectedNeighbors) {
                if (random.nextDouble() < transmissionProbability) {
                    transmitMessage(neighborId, message);
                }
            }
        }
        
        System.out.println("🦠 " + driverName + " epidemic round " + epidemicRounds.get() + 
                         ": spreading " + messagesToSpread.size() + " messages to " + 
                         selectedNeighbors.size() + " neighbors");
    }
    
    private List<String> selectEpidemicTargets() {
        if (neighbors.isEmpty()) {
            return Collections.emptyList();
        }
        
        // Distance-based selection: prefer closer neighbors for efficiency
        List<Map.Entry<String, Double>> neighborsByDistance = new ArrayList<>();
        for (String neighborId : neighbors) {
            Double distance = neighborDistances.get(neighborId);
            if (distance != null) {
                neighborsByDistance.add(Map.entry(neighborId, distance));
            }
        }
        
        // Sort by distance (closer first)
        neighborsByDistance.sort(Map.Entry.comparingByValue());
        
        // Select fanout number of closest neighbors with some randomness
        List<String> selected = new ArrayList<>();
        int targetCount = Math.min(epidemicFanout, neighborsByDistance.size());
        
        // Take top 70% closest, then random selection for remaining
        int closeCount = (int) (targetCount * 0.7);
        for (int i = 0; i < closeCount && i < neighborsByDistance.size(); i++) {
            selected.add(neighborsByDistance.get(i).getKey());
        }
        
        // Random selection for remaining slots
        List<String> remaining = new ArrayList<>();
        for (int i = closeCount; i < neighborsByDistance.size(); i++) {
            remaining.add(neighborsByDistance.get(i).getKey());
        }
        
        Collections.shuffle(remaining, random);
        int remainingSlots = targetCount - selected.size();
        for (int i = 0; i < remainingSlots && i < remaining.size(); i++) {
            selected.add(remaining.get(i));
        }
        
        return selected;
    }
    
    private void transmitMessage(String targetId, BroadcastMessage message) {
        // Create a copy of message with incremented hop count
        BroadcastMessage transmittedMessage = new BroadcastMessage(
            message.getMessageId(),
            message.getType(),
            message.getContent(),
            message.getSourceId(),
            message.getPriority(),
            message.getMaxHops()
        );
        
        transmittedMessage.incrementHops();
        transmittedMessage.getMetadata().putAll(message.getMetadata());
        
        // Simulate network transmission delay
        scheduler.schedule(() -> {
            // In real implementation, this would send to actual neighbor
            // For simulation, we'll process the message reception
            receiveMessage(transmittedMessage, targetId);
        }, random.nextInt(500), TimeUnit.MILLISECONDS);
        
        messagesForwarded.incrementAndGet();
    }
    
    public void receiveMessage(BroadcastMessage message, String fromNeighbor) {
        messagesReceived.incrementAndGet();
        
        boolean newMessage = epidemicState.receiveMessage(message);
        
        if (newMessage) {
            System.out.println("📱 " + driverName + " received " + message.getType() + 
                             " from " + fromNeighbor + ": " + message.getContent());
                             
            // Process message based on type
            processMessage(message);
        }
    }
    
    private void processMessage(BroadcastMessage message) {
        switch (message.getType()) {
            case RIDE_REQUEST:
                handleRideRequest(message);
                break;
            case DRIVER_AVAILABLE:
                handleDriverAvailable(message);
                break;
            case TRAFFIC_UPDATE:
                handleTrafficUpdate(message);
                break;
            case SURGE_PRICING:
                handleSurgePricing(message);
                break;
            case EMERGENCY_ALERT:
                handleEmergencyAlert(message);
                break;
            default:
                System.out.println("ℹ️  " + driverName + " processed: " + message.getType());
        }
    }
    
    private void handleRideRequest(BroadcastMessage message) {
        // Simulate driver considering the ride request
        if (random.nextDouble() < 0.3) { // 30% chance to respond
            System.out.println("✅ " + driverName + " interested in ride request: " + 
                             message.getContent());
        }
    }
    
    private void handleDriverAvailable(BroadcastMessage message) {
        System.out.println("👥 " + driverName + " noted driver availability: " + 
                         message.getMetadata().get("driver"));
    }
    
    private void handleTrafficUpdate(BroadcastMessage message) {
        System.out.println("🚦 " + driverName + " updated route based on traffic: " + 
                         message.getContent());
    }
    
    private void handleSurgePricing(BroadcastMessage message) {
        System.out.println("💰 " + driverName + " aware of surge pricing: " + 
                         message.getContent());
    }
    
    private void handleEmergencyAlert(BroadcastMessage message) {
        System.out.println("🚨 " + driverName + " received emergency alert: " + 
                         message.getContent());
    }
    
    private void performMaintenance() {
        // Reset epidemic state if needed
        epidemicState.resetToSusceptible();
        
        // Clean up old data, perform health checks, etc.
    }
    
    public EpidemicStatistics getStatistics() {
        return new EpidemicStatistics(
            nodeId,
            driverName,
            epidemicState.getState(),
            epidemicState.getReceivedMessageCount(),
            epidemicState.getActiveMessageCount(),
            epidemicState.getSpreadCount(),
            messagesOriginated.get(),
            messagesReceived.get(),
            messagesForwarded.get(),
            epidemicRounds.get(),
            neighbors.size()
        );
    }
    
    public void shutdown() {
        scheduler.shutdown();
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            scheduler.shutdownNow();
        }
    }
    
    // Statistics class
    public static class EpidemicStatistics {
        public final String nodeId;
        public final String driverName;
        public final InfectionState state;
        public final int receivedMessages;
        public final int activeMessages;
        public final int spreadCount;
        public final int originatedMessages;
        public final int totalReceived;
        public final int totalForwarded;
        public final int epidemicRounds;
        public final int neighborCount;
        
        public EpidemicStatistics(String nodeId, String driverName, InfectionState state,
                                int receivedMessages, int activeMessages, int spreadCount,
                                int originatedMessages, int totalReceived, int totalForwarded,
                                int epidemicRounds, int neighborCount) {
            this.nodeId = nodeId;
            this.driverName = driverName;
            this.state = state;
            this.receivedMessages = receivedMessages;
            this.activeMessages = activeMessages;
            this.spreadCount = spreadCount;
            this.originatedMessages = originatedMessages;
            this.totalReceived = totalReceived;
            this.totalForwarded = totalForwarded;
            this.epidemicRounds = epidemicRounds;
            this.neighborCount = neighborCount;
        }
        
        @Override
        public String toString() {
            return String.format(
                "%s (%s): State=%s, Received=%d, Active=%d, Spread=%d, Neighbors=%d",
                driverName, nodeId, state, receivedMessages, activeMessages, 
                spreadCount, neighborCount
            );
        }
    }
    
    // Main method for testing
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🇮🇳 Ola Epidemic Broadcast Simulation");
        System.out.println("=" + "=".repeat(40));
        
        // Create Ola drivers in Mumbai
        Map<String, EpidemicBroadcast> drivers = new HashMap<>();
        
        String[] driverData = {
            "driver_001,Rajesh,Bandra",
            "driver_002,Amit,Andheri", 
            "driver_003,Vikash,Borivali",
            "driver_004,Suresh,Thane",
            "driver_005,Ravi,Mulund",
            "driver_006,Deepak,Ghatkopar",
            "driver_007,Prakash,Kurla",
            "driver_008,Mahesh,Dadar"
        };
        
        for (String data : driverData) {
            String[] parts = data.split(",");
            String driverId = parts[0];
            String name = parts[1];
            String location = parts[2];
            
            drivers.put(driverId, new EpidemicBroadcast(driverId, name, location));
        }
        
        // Create network topology (drivers can communicate with nearby drivers)
        String[][] connections = {
            {"driver_001", "driver_002", "2.5"}, // Bandra-Andheri
            {"driver_002", "driver_003", "4.1"}, // Andheri-Borivali
            {"driver_003", "driver_004", "8.2"}, // Borivali-Thane
            {"driver_004", "driver_005", "3.7"}, // Thane-Mulund
            {"driver_005", "driver_006", "5.1"}, // Mulund-Ghatkopar
            {"driver_006", "driver_007", "2.8"}, // Ghatkopar-Kurla
            {"driver_007", "driver_008", "6.3"}, // Kurla-Dadar
            {"driver_008", "driver_001", "4.9"}, // Dadar-Bandra
            {"driver_001", "driver_007", "3.2"}, // Bandra-Kurla (direct)
            {"driver_002", "driver_006", "7.8"}, // Andheri-Ghatkopar
        };
        
        for (String[] conn : connections) {
            String driver1 = conn[0];
            String driver2 = conn[1];
            double distance = Double.parseDouble(conn[2]);
            
            if (drivers.containsKey(driver1) && drivers.containsKey(driver2)) {
                drivers.get(driver1).addNeighbor(driver2, distance);
                drivers.get(driver2).addNeighbor(driver1, distance);
            }
        }
        
        System.out.println("Network topology created. Starting epidemic simulation...\n");
        
        // Wait for network to stabilize
        Thread.sleep(3000);
        
        // Simulate various broadcast scenarios
        
        // Scenario 1: Ride request
        System.out.println("--- Scenario 1: Ride Request Broadcast ---");
        drivers.get("driver_001").broadcastMessage(
            MessageType.RIDE_REQUEST,
            "Ride needed from Bandra to Airport, 2 passengers",
            2 // High priority
        );
        
        Thread.sleep(5000);
        
        // Scenario 2: Emergency alert
        System.out.println("\n--- Scenario 2: Emergency Alert ---");
        drivers.get("driver_004").broadcastMessage(
            MessageType.EMERGENCY_ALERT,
            "Accident on Eastern Express Highway near Thane, avoid route",
            1 // Highest priority
        );
        
        Thread.sleep(4000);
        
        // Scenario 3: Surge pricing
        System.out.println("\n--- Scenario 3: Surge Pricing ---");
        drivers.get("driver_006").broadcastMessage(
            MessageType.SURGE_PRICING,
            "2.5x surge pricing active in Ghatkopar area due to heavy demand",
            3 // Medium priority
        );
        
        Thread.sleep(6000);
        
        // Print epidemic statistics
        System.out.println("\n📊 Epidemic Broadcast Statistics:");
        
        for (EpidemicBroadcast driver : drivers.values()) {
            EpidemicStatistics stats = driver.getStatistics();
            System.out.println("  " + stats);
        }
        
        // Calculate network-wide metrics
        int totalOriginated = drivers.values().stream()
            .mapToInt(d -> d.getStatistics().originatedMessages).sum();
        int totalReceived = drivers.values().stream()
            .mapToInt(d -> d.getStatistics().totalReceived).sum();
        int totalForwarded = drivers.values().stream()
            .mapToInt(d -> d.getStatistics().totalForwarded).sum();
            
        System.out.println("\n📈 Network Summary:");
        System.out.println("  Total messages originated: " + totalOriginated);
        System.out.println("  Total messages received: " + totalReceived);
        System.out.println("  Total messages forwarded: " + totalForwarded);
        System.out.println("  Average epidemic efficiency: " + 
                         String.format("%.2f%%", (double) totalReceived / totalOriginated * 100));
        
        // Cleanup
        for (EpidemicBroadcast driver : drivers.values()) {
            driver.shutdown();
        }
        
        System.out.println("\nEpidemic broadcast simulation completed!");
    }
}