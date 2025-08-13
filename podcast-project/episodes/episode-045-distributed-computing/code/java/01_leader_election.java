import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * Leader Election Protocol for Distributed Systems
 * जैसे कि Swiggy के delivery coordination में use होता है
 * 
 * यह example दिखाता है कि कैसे multiple nodes के बीच leader election होता है
 * using Bully algorithm. Indian companies जैसे Swiggy, Zomato इसे use करती हैं
 * order coordination और delivery routing के लिए।
 * 
 * Production context: Swiggy coordinates 100k+ delivery partners using leader election
 * Scale: Handles dynamic node failures and network partitions
 * Cost benefit: Prevents coordination conflicts and ensures single point of decision
 */

/**
 * Swiggy-style delivery coordination node
 * हर node एक delivery coordinator है जो specific area को handle करता है
 */
class SwiggyDeliveryCoordinator {
    private final String nodeId;
    private final int priority; // Higher number = higher priority
    private final List<String> clusterNodes;
    private final Map<String, Integer> nodePriorities;
    
    // Node state
    private volatile NodeState state;
    private volatile String currentLeader;
    private final AtomicInteger currentTerm;
    private final AtomicBoolean isRunning;
    
    // Heartbeat and timing
    private final long heartbeatInterval = 5000; // 5 seconds
    private final long electionTimeout = 15000; // 15 seconds
    private volatile long lastHeartbeatReceived;
    
    // Delivery coordination state
    private final Map<String, DeliveryOrder> activeOrders;
    private final Map<String, DeliveryPartner> availablePartners;
    private final Queue<String> pendingAssignments;
    
    // Threading
    private final ExecutorService executorService;
    private final ScheduledExecutorService scheduledExecutor;
    private ScheduledFuture<?> heartbeatTask;
    private ScheduledFuture<?> electionTask;
    
    public enum NodeState {
        FOLLOWER, CANDIDATE, LEADER
    }
    
    /**
     * Delivery order representation
     */
    public static class DeliveryOrder {
        public final String orderId;
        public final String customerId;
        public final String restaurantId;
        public final double latitude;
        public final double longitude;
        public final double orderValue;
        public final long orderTime;
        
        public DeliveryOrder(String orderId, String customerId, String restaurantId, 
                           double lat, double lng, double value) {
            this.orderId = orderId;
            this.customerId = customerId;
            this.restaurantId = restaurantId;
            this.latitude = lat;
            this.longitude = lng;
            this.orderValue = value;
            this.orderTime = System.currentTimeMillis();
        }
        
        @Override
        public String toString() {
            return String.format("Order{id=%s, customer=%s, restaurant=%s, value=₹%.2f}", 
                               orderId, customerId, restaurantId, orderValue);
        }
    }
    
    /**
     * Delivery partner representation
     */
    public static class DeliveryPartner {
        public final String partnerId;
        public final String name;
        public double currentLatitude;
        public double currentLongitude;
        public boolean isAvailable;
        public String assignedOrderId;
        
        public DeliveryPartner(String partnerId, String name, double lat, double lng) {
            this.partnerId = partnerId;
            this.name = name;
            this.currentLatitude = lat;
            this.currentLongitude = lng;
            this.isAvailable = true;
        }
        
        @Override
        public String toString() {
            return String.format("Partner{id=%s, name=%s, available=%s}", 
                               partnerId, name, isAvailable);
        }
    }
    
    public SwiggyDeliveryCoordinator(String nodeId, int priority, List<String> clusterNodes, 
                                   Map<String, Integer> nodePriorities) {
        this.nodeId = nodeId;
        this.priority = priority;
        this.clusterNodes = new ArrayList<>(clusterNodes);
        this.nodePriorities = new HashMap<>(nodePriorities);
        
        this.state = NodeState.FOLLOWER;
        this.currentLeader = null;
        this.currentTerm = new AtomicInteger(0);
        this.isRunning = new AtomicBoolean(false);
        this.lastHeartbeatReceived = System.currentTimeMillis();
        
        this.activeOrders = new ConcurrentHashMap<>();
        this.availablePartners = new ConcurrentHashMap<>();
        this.pendingAssignments = new ConcurrentLinkedQueue<>();
        
        this.executorService = Executors.newCachedThreadPool();
        this.scheduledExecutor = Executors.newScheduledThreadPool(3);
        
        // Initialize sample delivery partners for this zone
        initializeSamplePartners();
        
        System.out.printf("[%s] Swiggy delivery coordinator initialized with priority %d%n", 
                         nodeId, priority);
    }
    
    private void initializeSamplePartners() {
        // Mumbai delivery partners
        if (nodeId.contains("mumbai")) {
            availablePartners.put("DP001", new DeliveryPartner("DP001", "Rahul Sharma", 19.0760, 72.8777));
            availablePartners.put("DP002", new DeliveryPartner("DP002", "Priya Patel", 19.0896, 72.8656));
            availablePartners.put("DP003", new DeliveryPartner("DP003", "Amit Kumar", 19.0728, 72.8826));
        }
        // Delhi delivery partners
        else if (nodeId.contains("delhi")) {
            availablePartners.put("DP101", new DeliveryPartner("DP101", "Arjun Singh", 28.6139, 77.2090));
            availablePartners.put("DP102", new DeliveryPartner("DP102", "Sneha Gupta", 28.6542, 77.2373));
            availablePartners.put("DP103", new DeliveryPartner("DP103", "Vikash Yadav", 28.5355, 77.3910));
        }
        // Bangalore delivery partners
        else if (nodeId.contains("bangalore")) {
            availablePartners.put("DP201", new DeliveryPartner("DP201", "Kiran Reddy", 12.9716, 77.5946));
            availablePartners.put("DP202", new DeliveryPartner("DP202", "Deepika Nair", 12.9352, 77.6245));
            availablePartners.put("DP203", new DeliveryPartner("DP203", "Rajesh Iyer", 13.0067, 77.5648));
        }
    }
    
    public void start() {
        if (isRunning.compareAndSet(false, true)) {
            lastHeartbeatReceived = System.currentTimeMillis();
            
            // Start election timeout monitoring
            startElectionTimeoutMonitoring();
            
            System.out.printf("[%s] Started Swiggy delivery coordinator%n", nodeId);
        }
    }
    
    public void stop() {
        if (isRunning.compareAndSet(true, false)) {
            if (heartbeatTask != null) {
                heartbeatTask.cancel(true);
            }
            if (electionTask != null) {
                electionTask.cancel(true);
            }
            
            scheduledExecutor.shutdown();
            executorService.shutdown();
            
            System.out.printf("[%s] Stopped Swiggy delivery coordinator%n", nodeId);
        }
    }
    
    /**
     * Place a new delivery order
     */
    public boolean placeOrder(String orderId, String customerId, String restaurantId, 
                            double lat, double lng, double orderValue) {
        if (state != NodeState.LEADER) {
            System.out.printf("[%s] Cannot place order - not the leader. Current leader: %s%n", 
                             nodeId, currentLeader);
            return false;
        }
        
        DeliveryOrder order = new DeliveryOrder(orderId, customerId, restaurantId, lat, lng, orderValue);
        activeOrders.put(orderId, order);
        pendingAssignments.offer(orderId);
        
        System.out.printf("[%s] New order placed: %s%n", nodeId, order);
        
        // Try to assign delivery partner immediately
        return assignDeliveryPartner(orderId);
    }
    
    /**
     * Assign delivery partner to an order
     */
    private boolean assignDeliveryPartner(String orderId) {
        DeliveryOrder order = activeOrders.get(orderId);
        if (order == null) {
            return false;
        }
        
        // Find closest available partner
        DeliveryPartner bestPartner = null;
        double minDistance = Double.MAX_VALUE;
        
        for (DeliveryPartner partner : availablePartners.values()) {
            if (partner.isAvailable) {
                double distance = calculateDistance(order.latitude, order.longitude, 
                                                  partner.currentLatitude, partner.currentLongitude);
                if (distance < minDistance) {
                    minDistance = distance;
                    bestPartner = partner;
                }
            }
        }
        
        if (bestPartner != null) {
            bestPartner.isAvailable = false;
            bestPartner.assignedOrderId = orderId;
            
            System.out.printf("[%s] Assigned order %s to partner %s (%.2f km away)%n", 
                             nodeId, orderId, bestPartner.name, minDistance);
            return true;
        } else {
            System.out.printf("[%s] No available partners for order %s%n", nodeId, orderId);
            return false;
        }
    }
    
    /**
     * Calculate distance between two points (simplified)
     */
    private double calculateDistance(double lat1, double lng1, double lat2, double lng2) {
        // Simplified distance calculation (not accurate for large distances)
        double deltaLat = lat2 - lat1;
        double deltaLng = lng2 - lng1;
        return Math.sqrt(deltaLat * deltaLat + deltaLng * deltaLng) * 111; // Rough km conversion
    }
    
    /**
     * Start leader election
     */
    public void startElection() {
        if (!isRunning.get()) {
            return;
        }
        
        System.out.printf("[%s] Starting leader election in term %d%n", nodeId, currentTerm.get() + 1);
        
        state = NodeState.CANDIDATE;
        currentTerm.incrementAndGet();
        currentLeader = null;
        
        // Vote for self
        int votesReceived = 1;
        
        // Request votes from higher priority nodes first (Bully algorithm)
        List<String> higherPriorityNodes = getHigherPriorityNodes();
        
        if (!higherPriorityNodes.isEmpty()) {
            // Send election messages to higher priority nodes
            for (String nodeId : higherPriorityNodes) {
                if (sendElectionMessage(nodeId)) {
                    // Higher priority node responded, step down
                    System.out.printf("[%s] Higher priority node %s responded, stepping down%n", 
                                     this.nodeId, nodeId);
                    state = NodeState.FOLLOWER;
                    return;
                }
            }
        }
        
        // No higher priority nodes responded, continue election
        List<String> lowerPriorityNodes = getLowerPriorityNodes();
        
        for (String nodeId : lowerPriorityNodes) {
            if (requestVote(nodeId)) {
                votesReceived++;
            }
        }
        
        // Check if won election
        int majority = (clusterNodes.size() / 2) + 1;
        if (votesReceived >= majority) {
            becomeLeader();
        } else {
            state = NodeState.FOLLOWER;
            System.out.printf("[%s] Lost election with %d votes (needed %d)%n", 
                             nodeId, votesReceived, majority);
        }
    }
    
    private List<String> getHigherPriorityNodes() {
        return clusterNodes.stream()
                .filter(node -> !node.equals(nodeId))
                .filter(node -> nodePriorities.getOrDefault(node, 0) > priority)
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
    
    private List<String> getLowerPriorityNodes() {
        return clusterNodes.stream()
                .filter(node -> !node.equals(nodeId))
                .filter(node -> nodePriorities.getOrDefault(node, 0) < priority)
                .collect(ArrayList::new, ArrayList::add, ArrayList::addAll);
    }
    
    private boolean sendElectionMessage(String targetNodeId) {
        // Simulate network call to send election message
        // In real implementation, this would be actual network communication
        
        // Simulate network delay
        try {
            Thread.sleep(50 + new Random().nextInt(100)); // 50-150ms delay
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
        
        // Simulate response based on target node priority
        int targetPriority = nodePriorities.getOrDefault(targetNodeId, 0);
        
        // Higher priority nodes will respond to election messages
        if (targetPriority > priority) {
            // Simulate 80% response rate
            return new Random().nextDouble() > 0.2;
        }
        
        return false;
    }
    
    private boolean requestVote(String targetNodeId) {
        // Simulate vote request
        try {
            Thread.sleep(30 + new Random().nextInt(70)); // 30-100ms delay
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
        
        // Lower priority nodes will vote for higher priority candidates
        return new Random().nextDouble() > 0.3; // 70% vote grant rate
    }
    
    private void becomeLeader() {
        state = NodeState.LEADER;
        currentLeader = nodeId;
        
        System.out.printf("[%s] *** BECAME LEADER *** in term %d%n", nodeId, currentTerm.get());
        
        // Start sending heartbeats
        startHeartbeats();
        
        // Process pending order assignments
        processPendingAssignments();
        
        // Announce leadership to all nodes
        announceLeadership();
    }
    
    private void startHeartbeats() {
        if (heartbeatTask != null) {
            heartbeatTask.cancel(true);
        }
        
        heartbeatTask = scheduledExecutor.scheduleAtFixedRate(() -> {
            if (state == NodeState.LEADER && isRunning.get()) {
                sendHeartbeats();
            }
        }, heartbeatInterval, heartbeatInterval, TimeUnit.MILLISECONDS);
    }
    
    private void sendHeartbeats() {
        for (String nodeId : clusterNodes) {
            if (!nodeId.equals(this.nodeId)) {
                executorService.submit(() -> sendHeartbeatToNode(nodeId));
            }
        }
    }
    
    private void sendHeartbeatToNode(String targetNodeId) {
        // Simulate heartbeat sending
        try {
            Thread.sleep(20 + new Random().nextInt(30)); // 20-50ms delay
            
            // Simulate 95% success rate
            if (new Random().nextDouble() > 0.05) {
                System.out.printf("[%s] Sent heartbeat to %s%n", nodeId, targetNodeId);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    private void announceLeadership() {
        for (String nodeId : clusterNodes) {
            if (!nodeId.equals(this.nodeId)) {
                executorService.submit(() -> {
                    // Simulate leadership announcement
                    try {
                        Thread.sleep(30);
                        System.out.printf("[%s] Announced leadership to %s%n", this.nodeId, nodeId);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                });
            }
        }
    }
    
    private void processPendingAssignments() {
        System.out.printf("[%s] Processing %d pending order assignments%n", 
                         nodeId, pendingAssignments.size());
        
        while (!pendingAssignments.isEmpty()) {
            String orderId = pendingAssignments.poll();
            assignDeliveryPartner(orderId);
        }
    }
    
    public void receiveHeartbeat(String leaderId, int term) {
        if (term >= currentTerm.get()) {
            currentTerm.set(term);
            currentLeader = leaderId;
            lastHeartbeatReceived = System.currentTimeMillis();
            
            if (state != NodeState.FOLLOWER) {
                state = NodeState.FOLLOWER;
                System.out.printf("[%s] Received heartbeat from leader %s, became follower%n", 
                                 nodeId, leaderId);
            }
        }
    }
    
    private void startElectionTimeoutMonitoring() {
        electionTask = scheduledExecutor.scheduleAtFixedRate(() -> {
            if (!isRunning.get()) {
                return;
            }
            
            long timeSinceLastHeartbeat = System.currentTimeMillis() - lastHeartbeatReceived;
            
            if (state != NodeState.LEADER && timeSinceLastHeartbeat > electionTimeout) {
                System.out.printf("[%s] Election timeout! Last heartbeat %d ms ago%n", 
                                 nodeId, timeSinceLastHeartbeat);
                startElection();
            }
        }, electionTimeout, electionTimeout / 3, TimeUnit.MILLISECONDS);
    }
    
    public CoordinatorStatus getStatus() {
        return new CoordinatorStatus(
            nodeId,
            state.toString(),
            currentLeader,
            currentTerm.get(),
            activeOrders.size(),
            (int) availablePartners.values().stream().filter(p -> p.isAvailable).count(),
            pendingAssignments.size()
        );
    }
    
    public static class CoordinatorStatus {
        public final String nodeId;
        public final String state;
        public final String currentLeader;
        public final int term;
        public final int activeOrders;
        public final int availablePartners;
        public final int pendingAssignments;
        
        public CoordinatorStatus(String nodeId, String state, String currentLeader, 
                               int term, int activeOrders, int availablePartners, int pendingAssignments) {
            this.nodeId = nodeId;
            this.state = state;
            this.currentLeader = currentLeader;
            this.term = term;
            this.activeOrders = activeOrders;
            this.availablePartners = availablePartners;
            this.pendingAssignments = pendingAssignments;
        }
        
        @Override
        public String toString() {
            return String.format("Status{node=%s, state=%s, leader=%s, term=%d, orders=%d, partners=%d, pending=%d}",
                               nodeId, state, currentLeader, term, activeOrders, availablePartners, pendingAssignments);
        }
    }
}

/**
 * Main demonstration class
 */
public class SwiggyLeaderElectionDemo {
    
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🛵 Swiggy Delivery Coordination with Leader Election");
        System.out.println("=" .repeat(60));
        
        // Setup cluster nodes with priorities
        List<String> clusterNodes = Arrays.asList(
            "mumbai-coord-01",
            "delhi-coord-01", 
            "bangalore-coord-01"
        );
        
        Map<String, Integer> nodePriorities = Map.of(
            "mumbai-coord-01", 3,      // Highest priority (main hub)
            "delhi-coord-01", 2,       // Medium priority
            "bangalore-coord-01", 1    // Lowest priority
        );
        
        // Create coordinator nodes
        Map<String, SwiggyDeliveryCoordinator> coordinators = new HashMap<>();
        
        System.out.println("\n🏢 Setting up Swiggy delivery coordinators...");
        for (String nodeId : clusterNodes) {
            int priority = nodePriorities.get(nodeId);
            SwiggyDeliveryCoordinator coordinator = new SwiggyDeliveryCoordinator(
                nodeId, priority, clusterNodes, nodePriorities);
            coordinators.put(nodeId, coordinator);
            coordinator.start();
            System.out.printf("✅ Started coordinator: %s (priority: %d)%n", nodeId, priority);
        }
        
        // Wait for initial leader election
        System.out.println("\n🗳️ Waiting for initial leader election...");
        Thread.sleep(3000);
        
        // Trigger election from lowest priority node
        System.out.println("\n⚡ Triggering election from bangalore-coord-01...");
        coordinators.get("bangalore-coord-01").startElection();
        
        Thread.sleep(5000);
        
        // Show cluster status
        System.out.println("\n📊 Cluster Status after Election:");
        SwiggyDeliveryCoordinator leader = null;
        for (SwiggyDeliveryCoordinator coordinator : coordinators.values()) {
            CoordinatorStatus status = coordinator.getStatus();
            System.out.println("  " + status);
            if ("LEADER".equals(status.state)) {
                leader = coordinator;
            }
        }
        
        if (leader != null) {
            System.out.printf("\n👑 Leader: %s%n", leader.getStatus().nodeId);
            
            // Place some orders through the leader
            System.out.println("\n🍽️ Placing orders through leader...");
            
            // Mumbai orders
            leader.placeOrder("ORD001", "customer_rahul", "restaurant_mcdonalds_bandra", 
                            19.0596, 72.8295, 450.0);
            leader.placeOrder("ORD002", "customer_priya", "restaurant_dominos_andheri", 
                            19.1136, 72.8697, 780.0);
            
            // Delhi orders  
            leader.placeOrder("ORD003", "customer_arjun", "restaurant_kfc_cp", 
                            28.6315, 77.2167, 320.0);
            
            Thread.sleep(2000);
            
            // Show updated status
            System.out.println("\n📈 Updated Cluster Status:");
            for (SwiggyDeliveryCoordinator coordinator : coordinators.values()) {
                System.out.println("  " + coordinator.getStatus());
            }
        }
        
        // Simulate leader failure
        if (leader != null) {
            System.out.printf("\n💥 Simulating leader failure: %s%n", leader.getStatus().nodeId);
            leader.stop();
            
            Thread.sleep(8000); // Wait for election timeout
            
            // Show status after leader failure
            System.out.println("\n🔄 Cluster Status after Leader Failure:");
            for (SwiggyDeliveryCoordinator coordinator : coordinators.values()) {
                if (coordinator != leader) {
                    System.out.println("  " + coordinator.getStatus());
                }
            }
        }
        
        // Production insights
        System.out.println("\n💡 Production Insights:");
        System.out.println("- Leader election ensures single point of coordination for delivery assignments");
        System.out.println("- Bully algorithm promotes highest priority node (main hub) as leader");
        System.out.println("- Automatic failover maintains service availability during node failures");
        System.out.println("- Prevents split-brain scenarios in delivery coordination");
        System.out.println("- Scales to 10-15 coordinator nodes across cities");
        System.out.println("- Critical for maintaining order assignment consistency");
        System.out.println("- Reduces customer wait times through centralized optimization");
        
        // Cleanup
        System.out.println("\n🧹 Cleaning up coordinators...");
        for (SwiggyDeliveryCoordinator coordinator : coordinators.values()) {
            if (coordinator != leader) {
                coordinator.stop();
            }
        }
        
        System.out.println("Demo completed!");
    }
}