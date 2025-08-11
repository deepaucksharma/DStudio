/**
 * Vector Clock Implementation - Episode 4
 * व्यावहारिक Vector Clock का production-ready implementation
 * 
 * यह system distributed events का causal ordering maintain करता है।
 * बिना central coordination के पता चल जाता है कि कौन सा event पहले हुआ।
 * 
 * Indian Context Examples:
 * - WhatsApp group messages का ordering
 * - Paytm transaction logs का synchronization  
 * - Flipkart order processing pipeline
 * - Zomato delivery status updates
 * 
 * Vector Clock Rules:
 * 1. हर node का अपना counter होता है
 * 2. Local event पर अपना counter increment
 * 3. Message send करते time अपना clock include
 * 4. Message receive करते time clocks merge
 */

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

/**
 * VectorClock class - Distributed systems के लिए logical time
 */
public class VectorClock implements Cloneable, Comparable<VectorClock> {
    
    // Node ID से उसके counter का mapping
    private final Map<String, Integer> clock;
    private final String nodeId;
    
    // Debug और monitoring के लिए
    private long physicalTimestamp;
    private static final DateTimeFormatter FORMATTER = 
        DateTimeFormatter.ofPattern("HH:mm:ss.SSS").withZone(ZoneId.systemDefault());
    
    /**
     * Constructor - नए VectorClock बनाने के लिए
     */
    public VectorClock(String nodeId) {
        this.clock = new ConcurrentHashMap<>();
        this.nodeId = nodeId;
        this.physicalTimestamp = System.currentTimeMillis();
        
        // अपना counter 0 से start करें
        this.clock.put(nodeId, 0);
        
        System.out.printf("🔄 VectorClock initialized for node: %s%n", nodeId);
    }
    
    /**
     * Copy constructor - existing clock को copy करने के लिए
     */
    public VectorClock(VectorClock other, String nodeId) {
        this.clock = new ConcurrentHashMap<>(other.clock);
        this.nodeId = nodeId;
        this.physicalTimestamp = System.currentTimeMillis();
        
        // अगर इस node का entry नहीं है तो add करें
        this.clock.putIfAbsent(nodeId, 0);
    }
    
    /**
     * Local event handle करना - जैसे user का कोई action
     * Example: WhatsApp में message type करना
     */
    public synchronized void tick() {
        int currentValue = this.clock.getOrDefault(this.nodeId, 0);
        this.clock.put(this.nodeId, currentValue + 1);
        this.physicalTimestamp = System.currentTimeMillis();
        
        System.out.printf("⏰ Node %s: Local tick → %s%n", 
            this.nodeId, this.toString());
    }
    
    /**
     * Message receive करते time clock को update करना
     * Example: WhatsApp group में दूसरे member का message receive
     */
    public synchronized void update(VectorClock other) {
        if (other == null) {
            throw new IllegalArgumentException("Other VectorClock cannot be null");
        }
        
        System.out.printf("🔄 Node %s: Updating with %s%n", 
            this.nodeId, other.toString());
        
        // सभी nodes के लिए maximum value लें
        Set<String> allNodes = new HashSet<>(this.clock.keySet());
        allNodes.addAll(other.clock.keySet());
        
        for (String node : allNodes) {
            int thisValue = this.clock.getOrDefault(node, 0);
            int otherValue = other.clock.getOrDefault(node, 0);
            this.clock.put(node, Math.max(thisValue, otherValue));
        }
        
        // अपना counter increment करें (message receive भी एक event है)
        int currentValue = this.clock.getOrDefault(this.nodeId, 0);
        this.clock.put(this.nodeId, currentValue + 1);
        this.physicalTimestamp = System.currentTimeMillis();
        
        System.out.printf("✅ Node %s: Updated clock → %s%n", 
            this.nodeId, this.toString());
    }
    
    /**
     * दो VectorClocks को compare करना - causality check
     * Returns:
     * - BEFORE: this happened-before other
     * - AFTER: other happened-before this  
     * - CONCURRENT: concurrent events (कोई causal relation नहीं)
     */
    public CausalRelation compareTo(VectorClock other) {
        if (other == null) {
            return CausalRelation.CONCURRENT;
        }
        
        boolean thisLessOrEqual = true;
        boolean thisGreaterOrEqual = true;
        boolean atLeastOneLess = false;
        boolean atLeastOneGreater = false;
        
        // सभी nodes check करें
        Set<String> allNodes = new HashSet<>(this.clock.keySet());
        allNodes.addAll(other.clock.keySet());
        
        for (String node : allNodes) {
            int thisValue = this.clock.getOrDefault(node, 0);
            int otherValue = other.clock.getOrDefault(node, 0);
            
            if (thisValue < otherValue) {
                thisGreaterOrEqual = false;
                atLeastOneLess = true;
            } else if (thisValue > otherValue) {
                thisLessOrEqual = false;
                atLeastOneGreater = true;
            }
        }
        
        if (thisLessOrEqual && atLeastOneLess) {
            return CausalRelation.BEFORE;
        } else if (thisGreaterOrEqual && atLeastOneGreater) {
            return CausalRelation.AFTER;
        } else {
            return CausalRelation.CONCURRENT;
        }
    }
    
    /**
     * Standard Comparable interface implementation
     */
    @Override
    public int compareTo(VectorClock other) {
        CausalRelation relation = this.compareTo(other);
        switch (relation) {
            case BEFORE: return -1;
            case AFTER: return 1;
            case CONCURRENT: 
            default: return 0;
        }
    }
    
    /**
     * Deep copy बनाना
     */
    @Override
    public VectorClock clone() {
        VectorClock copy = new VectorClock(this.nodeId);
        copy.clock.clear();
        copy.clock.putAll(this.clock);
        copy.physicalTimestamp = this.physicalTimestamp;
        return copy;
    }
    
    /**
     * Current timestamp for this node
     */
    public int getTimestamp(String nodeId) {
        return this.clock.getOrDefault(nodeId, 0);
    }
    
    /**
     * All nodes that this clock knows about
     */
    public Set<String> getNodes() {
        return new HashSet<>(this.clock.keySet());
    }
    
    /**
     * Physical timestamp (for debugging)
     */
    public long getPhysicalTimestamp() {
        return this.physicalTimestamp;
    }
    
    /**
     * Formatted physical time
     */
    public String getFormattedTime() {
        return FORMATTER.format(Instant.ofEpochMilli(this.physicalTimestamp));
    }
    
    /**
     * Human-readable string representation
     */
    @Override
    public String toString() {
        StringBuilder sb = new StringBuilder();
        sb.append("{");
        
        // Sorted nodes for consistent output
        List<String> sortedNodes = new ArrayList<>(this.clock.keySet());
        Collections.sort(sortedNodes);
        
        for (int i = 0; i < sortedNodes.size(); i++) {
            String node = sortedNodes.get(i);
            sb.append(node).append(":").append(this.clock.get(node));
            if (i < sortedNodes.size() - 1) {
                sb.append(", ");
            }
        }
        sb.append("}");
        return sb.toString();
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        
        VectorClock other = (VectorClock) obj;
        return this.clock.equals(other.clock);
    }
    
    @Override
    public int hashCode() {
        return this.clock.hashCode();
    }
}

/**
 * Causal relationship के types
 */
enum CausalRelation {
    BEFORE,      // happened-before
    AFTER,       // happened-after  
    CONCURRENT   // concurrent (no causal relation)
}

/**
 * Distributed Event class - VectorClock के साथ events को represent करने के लिए
 */
class DistributedEvent {
    private final String eventId;
    private final String nodeId;
    private final String eventType;
    private final Object eventData;
    private final VectorClock vectorClock;
    private final long physicalTimestamp;
    
    public DistributedEvent(String eventId, String nodeId, String eventType, 
                           Object eventData, VectorClock vectorClock) {
        this.eventId = eventId;
        this.nodeId = nodeId;
        this.eventType = eventType;
        this.eventData = eventData;
        this.vectorClock = vectorClock.clone(); // Deep copy
        this.physicalTimestamp = System.currentTimeMillis();
    }
    
    // Getters
    public String getEventId() { return eventId; }
    public String getNodeId() { return nodeId; }
    public String getEventType() { return eventType; }
    public Object getEventData() { return eventData; }
    public VectorClock getVectorClock() { return vectorClock.clone(); }
    public long getPhysicalTimestamp() { return physicalTimestamp; }
    
    /**
     * इस event का दूसरे event के साथ causal relation check करना
     */
    public CausalRelation getCausalRelation(DistributedEvent other) {
        return this.vectorClock.compareTo(other.vectorClock);
    }
    
    @Override
    public String toString() {
        return String.format("Event{id=%s, node=%s, type=%s, clock=%s, time=%s}", 
            eventId, nodeId, eventType, vectorClock.toString(),
            DateTimeFormatter.ofPattern("HH:mm:ss.SSS")
                .withZone(ZoneId.systemDefault())
                .format(Instant.ofEpochMilli(physicalTimestamp)));
    }
}

/**
 * WhatsApp Group Chat Simulator - Vector Clock का practical use case
 */
class WhatsAppGroupSimulator {
    private final Map<String, VectorClock> memberClocks;
    private final List<DistributedEvent> messageHistory;
    private final AtomicInteger messageCounter;
    
    public WhatsAppGroupSimulator(List<String> members) {
        this.memberClocks = new ConcurrentHashMap<>();
        this.messageHistory = new ArrayList<>();
        this.messageCounter = new AtomicInteger(0);
        
        // सभी members के लिए VectorClock initialize करें
        for (String member : members) {
            this.memberClocks.put(member, new VectorClock(member));
        }
        
        System.out.printf("💬 WhatsApp Group created with members: %s%n", members);
    }
    
    /**
     * Member द्वारा message send करना
     */
    public synchronized DistributedEvent sendMessage(String sender, String message) {
        if (!memberClocks.containsKey(sender)) {
            throw new IllegalArgumentException("Unknown member: " + sender);
        }
        
        // Sender का clock increment करें
        VectorClock senderClock = memberClocks.get(sender);
        senderClock.tick();
        
        // Message event create करें
        String eventId = "msg_" + messageCounter.incrementAndGet();
        DistributedEvent messageEvent = new DistributedEvent(
            eventId, sender, "MESSAGE", message, senderClock
        );
        
        messageHistory.add(messageEvent);
        
        System.out.printf("📱 %s sent: \"%s\" [Clock: %s]%n", 
            sender, message, senderClock.toString());
        
        return messageEvent;
    }
    
    /**
     * Member द्वारा message receive करना
     */
    public synchronized void receiveMessage(String receiver, DistributedEvent messageEvent) {
        if (!memberClocks.containsKey(receiver)) {
            throw new IllegalArgumentException("Unknown member: " + receiver);
        }
        
        if (receiver.equals(messageEvent.getNodeId())) {
            // Sender को अपना message receive नहीं करना
            return;
        }
        
        // Receiver का clock update करें
        VectorClock receiverClock = memberClocks.get(receiver);
        receiverClock.update(messageEvent.getVectorClock());
        
        System.out.printf("📥 %s received message from %s [Clock: %s]%n", 
            receiver, messageEvent.getNodeId(), receiverClock.toString());
    }
    
    /**
     * सभी members को message broadcast करना
     */
    public void broadcastMessage(String sender, String message) {
        DistributedEvent messageEvent = sendMessage(sender, message);
        
        // सभी other members को send करें
        for (String member : memberClocks.keySet()) {
            if (!member.equals(sender)) {
                receiveMessage(member, messageEvent);
            }
        }
    }
    
    /**
     * Message ordering analysis - कौन सा message पहले आया
     */
    public void analyzeMessageOrdering() {
        System.out.println("\n📊 MESSAGE ORDERING ANALYSIS");
        System.out.println("=" + "=".repeat(50));
        
        for (int i = 0; i < messageHistory.size(); i++) {
            for (int j = i + 1; j < messageHistory.size(); j++) {
                DistributedEvent event1 = messageHistory.get(i);
                DistributedEvent event2 = messageHistory.get(j);
                
                CausalRelation relation = event1.getCausalRelation(event2);
                
                System.out.printf("Message %d vs Message %d: %s%n", 
                    i + 1, j + 1, formatCausalRelation(relation));
                System.out.printf("  Msg %d: %s by %s [%s]%n", 
                    i + 1, event1.getEventData(), event1.getNodeId(), 
                    event1.getVectorClock());
                System.out.printf("  Msg %d: %s by %s [%s]%n", 
                    j + 1, event2.getEventData(), event2.getNodeId(), 
                    event2.getVectorClock());
                System.out.println();
            }
        }
    }
    
    /**
     * Current state of all member clocks
     */
    public void printCurrentState() {
        System.out.println("\n🕐 CURRENT MEMBER CLOCKS");
        System.out.println("=" + "=".repeat(30));
        
        for (Map.Entry<String, VectorClock> entry : memberClocks.entrySet()) {
            System.out.printf("%s: %s [Physical: %s]%n", 
                entry.getKey(), 
                entry.getValue().toString(),
                entry.getValue().getFormattedTime());
        }
    }
    
    private String formatCausalRelation(CausalRelation relation) {
        switch (relation) {
            case BEFORE: return "HAPPENED-BEFORE (⏪)";
            case AFTER: return "HAPPENED-AFTER (⏩)"; 
            case CONCURRENT: return "CONCURRENT (⏸️)";
            default: return "UNKNOWN";
        }
    }
}

/**
 * Paytm Transaction Ordering System - Vector Clock for financial transactions
 */
class PaytmTransactionSystem {
    private final Map<String, VectorClock> serviceClocks;
    private final List<DistributedEvent> transactionLog;
    private final AtomicInteger transactionCounter;
    
    public PaytmTransactionSystem() {
        this.serviceClocks = new ConcurrentHashMap<>();
        this.transactionLog = new ArrayList<>();
        this.transactionCounter = new AtomicInteger(0);
        
        // Paytm के different services initialize करें
        String[] services = {
            "paytm_wallet_service", 
            "paytm_bank_service", 
            "paytm_merchant_service",
            "paytm_notification_service"
        };
        
        for (String service : services) {
            serviceClocks.put(service, new VectorClock(service));
        }
        
        System.out.println("💰 Paytm Transaction System initialized");
    }
    
    /**
     * Transaction event record करना
     */
    public DistributedEvent recordTransaction(String service, String transactionType, 
                                            Map<String, Object> transactionData) {
        VectorClock serviceClock = serviceClocks.get(service);
        if (serviceClock == null) {
            throw new IllegalArgumentException("Unknown service: " + service);
        }
        
        serviceClock.tick();
        
        String txnId = "TXN_" + transactionCounter.incrementAndGet();
        DistributedEvent transactionEvent = new DistributedEvent(
            txnId, service, transactionType, transactionData, serviceClock
        );
        
        transactionLog.add(transactionEvent);
        
        System.out.printf("💳 %s: %s [%s] Clock: %s%n", 
            service, transactionType, txnId, serviceClock.toString());
        
        return transactionEvent;
    }
    
    /**
     * Service communication - एक service दूसरी को message भेजना
     */
    public void serviceCommunication(String fromService, String toService, 
                                   DistributedEvent relatedTransaction) {
        VectorClock fromClock = serviceClocks.get(fromService);
        VectorClock toClock = serviceClocks.get(toService);
        
        if (fromClock == null || toClock == null) {
            throw new IllegalArgumentException("Unknown service");
        }
        
        // To service को update करें
        toClock.update(relatedTransaction.getVectorClock());
        
        System.out.printf("🔄 %s → %s: Transaction sync [Clock: %s]%n", 
            fromService, toService, toClock.toString());
    }
    
    /**
     * Transaction consistency check
     */
    public void checkTransactionConsistency() {
        System.out.println("\n🔍 TRANSACTION CONSISTENCY CHECK");
        System.out.println("=" + "=".repeat(40));
        
        // Find potentially problematic transactions
        for (int i = 0; i < transactionLog.size() - 1; i++) {
            DistributedEvent txn1 = transactionLog.get(i);
            DistributedEvent txn2 = transactionLog.get(i + 1);
            
            CausalRelation relation = txn1.getCausalRelation(txn2);
            
            if (relation == CausalRelation.CONCURRENT && 
                txn1.getPhysicalTimestamp() > txn2.getPhysicalTimestamp()) {
                System.out.printf("⚠️ Potential ordering issue between %s and %s%n", 
                    txn1.getEventId(), txn2.getEventId());
                System.out.printf("   Physical time suggests %s before %s%n", 
                    txn2.getEventId(), txn1.getEventId());
                System.out.printf("   But vector clocks show CONCURRENT%n");
            }
        }
    }
}

/**
 * Main demonstration class
 */
public class VectorClockDemo {
    
    public static void main(String[] args) {
        System.out.println("🇮🇳 Vector Clock Implementation - Indian Tech Context");
        System.out.println("=" + "=".repeat(60));
        
        // Demo 1: Basic Vector Clock Operations
        basicVectorClockDemo();
        
        // Demo 2: WhatsApp Group Chat Simulation
        whatsappGroupDemo();
        
        // Demo 3: Paytm Transaction Ordering
        paytmTransactionDemo();
        
        // Demo 4: Causality Detection
        causalityDetectionDemo();
        
        System.out.println("\n✅ Vector Clock demonstration complete!");
        printKeyLearnings();
    }
    
    /**
     * Basic Vector Clock operations demo
     */
    private static void basicVectorClockDemo() {
        System.out.println("\n🔄 DEMO 1: Basic Vector Clock Operations");
        System.out.println("-" + "-".repeat(45));
        
        // Create clocks for different nodes
        VectorClock clockMumbai = new VectorClock("mumbai_server");
        VectorClock clockDelhi = new VectorClock("delhi_server");
        VectorClock clockBangalore = new VectorClock("bangalore_server");
        
        // Local events
        clockMumbai.tick(); // Mumbai: {mumbai:1}
        clockDelhi.tick();  // Delhi: {delhi:1}
        
        // Message from Mumbai to Delhi
        clockDelhi.update(clockMumbai); // Delhi merges Mumbai's clock
        
        // More events
        clockMumbai.tick(); // Mumbai: {mumbai:2}
        clockBangalore.tick(); // Bangalore: {bangalore:1}
        
        // Message from Delhi to Bangalore
        clockBangalore.update(clockDelhi); // Bangalore gets Delhi+Mumbai info
        
        System.out.println("\nFinal clock states:");
        System.out.println("Mumbai: " + clockMumbai.toString());
        System.out.println("Delhi: " + clockDelhi.toString());
        System.out.println("Bangalore: " + clockBangalore.toString());
        
        // Test causality
        System.out.println("\nCausality relationships:");
        System.out.println("Mumbai vs Delhi: " + clockMumbai.compareTo(clockDelhi));
        System.out.println("Delhi vs Bangalore: " + clockDelhi.compareTo(clockBangalore));
        System.out.println("Mumbai vs Bangalore: " + clockMumbai.compareTo(clockBangalore));
    }
    
    /**
     * WhatsApp group chat simulation
     */
    private static void whatsappGroupDemo() {
        System.out.println("\n💬 DEMO 2: WhatsApp Group Chat Simulation");
        System.out.println("-" + "-".repeat(45));
        
        List<String> groupMembers = Arrays.asList(
            "rajesh_mumbai", "priya_delhi", "amit_bangalore", "sneha_chennai"
        );
        
        WhatsAppGroupSimulator whatsapp = new WhatsAppGroupSimulator(groupMembers);
        
        // Simulate group conversation
        whatsapp.broadcastMessage("rajesh_mumbai", "Kya haal hai sabka?");
        
        // Simulate network delay - messages might arrive out of order
        try { Thread.sleep(100); } catch (InterruptedException e) {}
        
        whatsapp.broadcastMessage("priya_delhi", "Sab badhiya! Tum batao");
        whatsapp.broadcastMessage("amit_bangalore", "Office mein busy hun 😅");
        
        // Simulate concurrent messages
        whatsapp.sendMessage("sneha_chennai", "Same here, project deadline hai");
        whatsapp.receiveMessage("rajesh_mumbai", 
            whatsapp.sendMessage("rajesh_mumbai", "Weekend plan kya hai?"));
        
        whatsapp.printCurrentState();
        whatsapp.analyzeMessageOrdering();
    }
    
    /**
     * Paytm transaction system demo
     */
    private static void paytmTransactionDemo() {
        System.out.println("\n💰 DEMO 3: Paytm Transaction System");
        System.out.println("-" + "-".repeat(40));
        
        PaytmTransactionSystem paytm = new PaytmTransactionSystem();
        
        // Simulate transaction flow
        Map<String, Object> walletData = Map.of(
            "user_id", "user_123",
            "amount", 1000,
            "type", "credit",
            "source", "bank_transfer"
        );
        
        DistributedEvent walletTxn = paytm.recordTransaction(
            "paytm_wallet_service", "WALLET_CREDIT", walletData
        );
        
        Map<String, Object> merchantData = Map.of(
            "merchant_id", "zomato_restaurant_456", 
            "amount", 500,
            "order_id", "ORD_789"
        );
        
        DistributedEvent merchantTxn = paytm.recordTransaction(
            "paytm_merchant_service", "MERCHANT_PAYMENT", merchantData
        );
        
        // Service communication
        paytm.serviceCommunication(
            "paytm_wallet_service", 
            "paytm_notification_service", 
            walletTxn
        );
        
        paytm.serviceCommunication(
            "paytm_merchant_service", 
            "paytm_bank_service", 
            merchantTxn
        );
        
        paytm.checkTransactionConsistency();
    }
    
    /**
     * Advanced causality detection
     */
    private static void causalityDetectionDemo() {
        System.out.println("\n🔍 DEMO 4: Advanced Causality Detection");
        System.out.println("-" + "-".repeat(45));
        
        // Create events with different causal relationships
        VectorClock clock1 = new VectorClock("node1");
        VectorClock clock2 = new VectorClock("node2");
        VectorClock clock3 = new VectorClock("node3");
        
        // Sequential events
        clock1.tick();  // Event A
        DistributedEvent eventA = new DistributedEvent("A", "node1", "ACTION", "User login", clock1);
        
        clock2.update(clock1); // Node2 learns about A
        clock2.tick(); // Event B (causally after A)
        DistributedEvent eventB = new DistributedEvent("B", "node2", "ACTION", "Load profile", clock2);
        
        // Concurrent event
        clock3.tick(); // Event C (concurrent with A and B)
        DistributedEvent eventC = new DistributedEvent("C", "node3", "ACTION", "Background job", clock3);
        
        // Analysis
        System.out.println("Event relationships:");
        System.out.printf("A vs B: %s%n", eventA.getCausalRelation(eventB));
        System.out.printf("A vs C: %s%n", eventA.getCausalRelation(eventC));
        System.out.printf("B vs C: %s%n", eventB.getCausalRelation(eventC));
        
        System.out.println("\nEvent details:");
        System.out.println("Event A: " + eventA.toString());
        System.out.println("Event B: " + eventB.toString());
        System.out.println("Event C: " + eventC.toString());
    }
    
    /**
     * Key learnings summary
     */
    private static void printKeyLearnings() {
        System.out.println("\n📚 KEY LEARNINGS - Vector Clocks");
        System.out.println("=" + "=".repeat(40));
        System.out.println("1. Vector clocks track causality in distributed systems");
        System.out.println("2. No need for synchronized physical clocks");
        System.out.println("3. Can detect:");
        System.out.println("   • Happened-before relationships");
        System.out.println("   • Concurrent events");
        System.out.println("   • Causality violations");
        System.out.println("4. Real applications:");
        System.out.println("   • WhatsApp message ordering");
        System.out.println("   • Paytm transaction consistency");
        System.out.println("   • Distributed database replication");
        System.out.println("   • Microservice event ordering");
        System.out.println("5. Trade-offs:");
        System.out.println("   ✅ Accurate causality tracking");
        System.out.println("   ❌ Clock size grows with nodes");
        System.out.println("   ❌ Network overhead for clock exchange");
    }
}