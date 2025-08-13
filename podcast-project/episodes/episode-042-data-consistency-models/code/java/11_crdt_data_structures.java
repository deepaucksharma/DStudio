/**
 * CRDT (Conflict-Free Replicated Data Types) Implementation
 * Google Docs/Figma collaborative editing jaisa functionality
 * State-based CRDTs for distributed systems
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;
import java.util.logging.Logger;

// Base CRDT interface
interface CRDT<T> {
    T getValue();
    void merge(CRDT<T> other);
    CRDT<T> copy();
}

// G-Counter: Grow-only counter CRDT
class GCounter implements CRDT<Long> {
    private final String nodeId;
    private final Map<String, Long> counters;
    
    public GCounter(String nodeId) {
        this.nodeId = nodeId;
        this.counters = new ConcurrentHashMap<>();
        this.counters.put(nodeId, 0L);
    }
    
    public GCounter(String nodeId, Map<String, Long> counters) {
        this.nodeId = nodeId;
        this.counters = new ConcurrentHashMap<>(counters);
    }
    
    public void increment() {
        counters.put(nodeId, counters.get(nodeId) + 1);
    }
    
    public void increment(long delta) {
        counters.put(nodeId, counters.get(nodeId) + delta);
    }
    
    @Override
    public Long getValue() {
        return counters.values().stream().mapToLong(Long::longValue).sum();
    }
    
    @Override
    public void merge(CRDT<Long> other) {
        if (!(other instanceof GCounter)) {
            throw new IllegalArgumentException("Can only merge with another GCounter");
        }
        
        GCounter otherCounter = (GCounter) other;
        
        for (Map.Entry<String, Long> entry : otherCounter.counters.entrySet()) {
            String node = entry.getKey();
            Long otherValue = entry.getValue();
            
            counters.put(node, Math.max(counters.getOrDefault(node, 0L), otherValue));
        }
    }
    
    @Override
    public GCounter copy() {
        return new GCounter(nodeId, new HashMap<>(counters));
    }
    
    public String getNodeId() { return nodeId; }
    public Map<String, Long> getCounters() { return new HashMap<>(counters); }
    
    @Override
    public String toString() {
        return String.format("GCounter[%s]=%d %s", nodeId, getValue(), counters);
    }
}

// PN-Counter: Increment/Decrement counter CRDT
class PNCounter implements CRDT<Long> {
    private final GCounter positive;
    private final GCounter negative;
    
    public PNCounter(String nodeId) {
        this.positive = new GCounter(nodeId);
        this.negative = new GCounter(nodeId);
    }
    
    public PNCounter(GCounter positive, GCounter negative) {
        this.positive = positive;
        this.negative = negative;
    }
    
    public void increment() {
        positive.increment();
    }
    
    public void increment(long delta) {
        positive.increment(delta);
    }
    
    public void decrement() {
        negative.increment();
    }
    
    public void decrement(long delta) {
        negative.increment(delta);
    }
    
    @Override
    public Long getValue() {
        return positive.getValue() - negative.getValue();
    }
    
    @Override
    public void merge(CRDT<Long> other) {
        if (!(other instanceof PNCounter)) {
            throw new IllegalArgumentException("Can only merge with another PNCounter");
        }
        
        PNCounter otherCounter = (PNCounter) other;
        positive.merge(otherCounter.positive);
        negative.merge(otherCounter.negative);
    }
    
    @Override
    public PNCounter copy() {
        return new PNCounter(positive.copy(), negative.copy());
    }
    
    @Override
    public String toString() {
        return String.format("PNCounter[%s]=%d (+%d, -%d)", 
                           positive.getNodeId(), getValue(), positive.getValue(), negative.getValue());
    }
}

// G-Set: Grow-only set CRDT
class GSet<T> implements CRDT<Set<T>> {
    private final Set<T> elements;
    
    public GSet() {
        this.elements = new ConcurrentHashMap<T, Boolean>().keySet(ConcurrentHashMap.newKeySet());
    }
    
    public GSet(Set<T> elements) {
        this.elements = new ConcurrentHashMap<T, Boolean>().keySet(ConcurrentHashMap.newKeySet());
        this.elements.addAll(elements);
    }
    
    public void add(T element) {
        elements.add(element);
    }
    
    public boolean contains(T element) {
        return elements.contains(element);
    }
    
    @Override
    public Set<T> getValue() {
        return new HashSet<>(elements);
    }
    
    @Override
    public void merge(CRDT<Set<T>> other) {
        if (!(other instanceof GSet)) {
            throw new IllegalArgumentException("Can only merge with another GSet");
        }
        
        @SuppressWarnings("unchecked")
        GSet<T> otherSet = (GSet<T>) other;
        elements.addAll(otherSet.elements);
    }
    
    @Override
    public GSet<T> copy() {
        return new GSet<>(new HashSet<>(elements));
    }
    
    @Override
    public String toString() {
        return "GSet" + elements.toString();
    }
}

// OR-Set: Observed-Remove set CRDT
class ORSet<T> implements CRDT<Set<T>> {
    private final Map<T, Set<String>> added;    // Element -> Set of unique tags
    private final Map<T, Set<String>> removed;  // Element -> Set of unique tags
    private final AtomicLong tagCounter;
    private final String nodeId;
    
    public ORSet(String nodeId) {
        this.nodeId = nodeId;
        this.added = new ConcurrentHashMap<>();
        this.removed = new ConcurrentHashMap<>();
        this.tagCounter = new AtomicLong(1);
    }
    
    public ORSet(String nodeId, Map<T, Set<String>> added, Map<T, Set<String>> removed, long tagCounter) {
        this.nodeId = nodeId;
        this.added = new ConcurrentHashMap<>(added);
        this.removed = new ConcurrentHashMap<>(removed);
        this.tagCounter = new AtomicLong(tagCounter);
    }
    
    public void add(T element) {
        String tag = nodeId + "_" + tagCounter.getAndIncrement() + "_" + System.nanoTime();
        added.computeIfAbsent(element, k -> ConcurrentHashMap.newKeySet()).add(tag);
    }
    
    public void remove(T element) {
        Set<String> elementTags = added.get(element);
        if (elementTags != null) {
            removed.computeIfAbsent(element, k -> ConcurrentHashMap.newKeySet()).addAll(elementTags);
        }
    }
    
    @Override
    public Set<T> getValue() {
        Set<T> result = new HashSet<>();
        
        for (Map.Entry<T, Set<String>> entry : added.entrySet()) {
            T element = entry.getKey();
            Set<String> addedTags = entry.getValue();
            Set<String> removedTags = removed.getOrDefault(element, Collections.emptySet());
            
            // Element is present if it has added tags not in removed tags
            if (!addedTags.isEmpty() && !removedTags.containsAll(addedTags)) {
                result.add(element);
            }
        }
        
        return result;
    }
    
    @Override
    public void merge(CRDT<Set<T>> other) {
        if (!(other instanceof ORSet)) {
            throw new IllegalArgumentException("Can only merge with another ORSet");
        }
        
        @SuppressWarnings("unchecked")
        ORSet<T> otherSet = (ORSet<T>) other;
        
        // Merge added sets
        for (Map.Entry<T, Set<String>> entry : otherSet.added.entrySet()) {
            T element = entry.getKey();
            Set<String> otherTags = entry.getValue();
            
            added.computeIfAbsent(element, k -> ConcurrentHashMap.newKeySet()).addAll(otherTags);
        }
        
        // Merge removed sets
        for (Map.Entry<T, Set<String>> entry : otherSet.removed.entrySet()) {
            T element = entry.getKey();
            Set<String> otherTags = entry.getValue();
            
            removed.computeIfAbsent(element, k -> ConcurrentHashMap.newKeySet()).addAll(otherTags);
        }
    }
    
    @Override
    public ORSet<T> copy() {
        Map<T, Set<String>> addedCopy = new HashMap<>();
        for (Map.Entry<T, Set<String>> entry : added.entrySet()) {
            addedCopy.put(entry.getKey(), new HashSet<>(entry.getValue()));
        }
        
        Map<T, Set<String>> removedCopy = new HashMap<>();
        for (Map.Entry<T, Set<String>> entry : removed.entrySet()) {
            removedCopy.put(entry.getKey(), new HashSet<>(entry.getValue()));
        }
        
        return new ORSet<>(nodeId, addedCopy, removedCopy, tagCounter.get());
    }
    
    public boolean contains(T element) {
        return getValue().contains(element);
    }
    
    @Override
    public String toString() {
        return String.format("ORSet[%s]=%s", nodeId, getValue());
    }
}

// LWW-Register: Last-Write-Wins register CRDT
class LWWRegister<T> implements CRDT<T> {
    private T value;
    private long timestamp;
    private String nodeId;
    
    public LWWRegister(String nodeId) {
        this.nodeId = nodeId;
        this.value = null;
        this.timestamp = 0;
    }
    
    public LWWRegister(String nodeId, T value, long timestamp) {
        this.nodeId = nodeId;
        this.value = value;
        this.timestamp = timestamp;
    }
    
    public void set(T newValue) {
        this.value = newValue;
        this.timestamp = System.nanoTime(); // Use nanoseconds for better precision
    }
    
    @Override
    public T getValue() {
        return value;
    }
    
    @Override
    public void merge(CRDT<T> other) {
        if (!(other instanceof LWWRegister)) {
            throw new IllegalArgumentException("Can only merge with another LWWRegister");
        }
        
        @SuppressWarnings("unchecked")
        LWWRegister<T> otherRegister = (LWWRegister<T>) other;
        
        // Keep the value with the latest timestamp
        // Use node ID as tiebreaker for deterministic ordering
        if (otherRegister.timestamp > this.timestamp || 
            (otherRegister.timestamp == this.timestamp && 
             otherRegister.nodeId.compareTo(this.nodeId) > 0)) {
            
            this.value = otherRegister.value;
            this.timestamp = otherRegister.timestamp;
        }
    }
    
    @Override
    public LWWRegister<T> copy() {
        return new LWWRegister<>(nodeId, value, timestamp);
    }
    
    public long getTimestamp() { return timestamp; }
    public String getNodeId() { return nodeId; }
    
    @Override
    public String toString() {
        return String.format("LWWRegister[%s]=%s@%d", nodeId, value, timestamp);
    }
}

// CRDT-based collaborative document - Google Docs jaisa
class CollaborativeDocument {
    private final String documentId;
    private final String nodeId;
    private final LWWRegister<String> title;
    private final ORSet<String> collaborators;
    private final PNCounter editCount;
    private final GCounter viewCount;
    private final Map<String, LWWRegister<String>> sections;
    
    public CollaborativeDocument(String documentId, String nodeId) {
        this.documentId = documentId;
        this.nodeId = nodeId;
        this.title = new LWWRegister<>(nodeId);
        this.collaborators = new ORSet<>(nodeId);
        this.editCount = new PNCounter(nodeId);
        this.viewCount = new GCounter(nodeId);
        this.sections = new ConcurrentHashMap<>();
    }
    
    public void setTitle(String newTitle) {
        title.set(newTitle);
        editCount.increment();
    }
    
    public void addCollaborator(String collaboratorId) {
        collaborators.add(collaboratorId);
        editCount.increment();
    }
    
    public void removeCollaborator(String collaboratorId) {
        collaborators.remove(collaboratorId);
        editCount.increment();
    }
    
    public void updateSection(String sectionId, String content) {
        sections.computeIfAbsent(sectionId, k -> new LWWRegister<>(nodeId)).set(content);
        editCount.increment();
    }
    
    public void incrementViewCount() {
        viewCount.increment();
    }
    
    public void mergeWith(CollaborativeDocument other) {
        if (!documentId.equals(other.documentId)) {
            throw new IllegalArgumentException("Cannot merge documents with different IDs");
        }
        
        title.merge(other.title);
        collaborators.merge(other.collaborators);
        editCount.merge(other.editCount);
        viewCount.merge(other.viewCount);
        
        // Merge sections
        for (Map.Entry<String, LWWRegister<String>> entry : other.sections.entrySet()) {
            String sectionId = entry.getKey();
            LWWRegister<String> otherSection = entry.getValue();
            
            sections.computeIfAbsent(sectionId, k -> new LWWRegister<>(nodeId)).merge(otherSection);
        }
    }
    
    public Map<String, Object> getDocumentState() {
        Map<String, Object> state = new HashMap<>();
        state.put("documentId", documentId);
        state.put("title", title.getValue());
        state.put("collaborators", collaborators.getValue());
        state.put("editCount", editCount.getValue());
        state.put("viewCount", viewCount.getValue());
        
        Map<String, String> sectionContents = new HashMap<>();
        for (Map.Entry<String, LWWRegister<String>> entry : sections.entrySet()) {
            sectionContents.put(entry.getKey(), entry.getValue().getValue());
        }
        state.put("sections", sectionContents);
        
        return state;
    }
    
    public String getDocumentId() { return documentId; }
    public String getNodeId() { return nodeId; }
}

// Distributed like counter system - Instagram/Facebook likes
class DistributedLikeSystem {
    private final String systemId;
    private final Map<String, GCounter> postLikes;    // PostId -> Like counter
    private final Map<String, ORSet<String>> postLikers; // PostId -> Set of user IDs who liked
    
    public DistributedLikeSystem(String systemId) {
        this.systemId = systemId;
        this.postLikes = new ConcurrentHashMap<>();
        this.postLikers = new ConcurrentHashMap<>();
    }
    
    public void likePost(String postId, String userId) {
        // Add user to likers set
        ORSet<String> likers = postLikers.computeIfAbsent(postId, k -> new ORSet<>(systemId));
        
        if (!likers.contains(userId)) {
            likers.add(userId);
            
            // Increment like counter
            GCounter counter = postLikes.computeIfAbsent(postId, k -> new GCounter(systemId));
            counter.increment();
        }
    }
    
    public void unlikePost(String postId, String userId) {
        ORSet<String> likers = postLikers.get(postId);
        
        if (likers != null && likers.contains(userId)) {
            likers.remove(userId);
            
            // Note: We don't decrement the counter to maintain grow-only property
            // In practice, you might use a PN-Counter here
        }
    }
    
    public long getLikeCount(String postId) {
        GCounter counter = postLikes.get(postId);
        return counter != null ? counter.getValue() : 0;
    }
    
    public Set<String> getLikers(String postId) {
        ORSet<String> likers = postLikers.get(postId);
        return likers != null ? likers.getValue() : new HashSet<>();
    }
    
    public void mergeWith(DistributedLikeSystem other) {
        // Merge like counters
        for (Map.Entry<String, GCounter> entry : other.postLikes.entrySet()) {
            String postId = entry.getKey();
            GCounter otherCounter = entry.getValue();
            
            postLikes.computeIfAbsent(postId, k -> new GCounter(systemId)).merge(otherCounter);
        }
        
        // Merge likers sets
        for (Map.Entry<String, ORSet<String>> entry : other.postLikers.entrySet()) {
            String postId = entry.getKey();
            ORSet<String> otherLikers = entry.getValue();
            
            postLikers.computeIfAbsent(postId, k -> new ORSet<>(systemId)).merge(otherLikers);
        }
    }
    
    public String getSystemId() { return systemId; }
}

// Main demo class
public class CRDTDataStructures {
    private static final Logger logger = Logger.getLogger(CRDTDataStructures.class.getName());
    
    public static void main(String[] args) {
        System.out.println("=== CRDT Data Structures Demo ===");
        System.out.println("Conflict-Free Replicated Data Types for distributed systems");
        
        try {
            // Demo 1: Counter CRDTs
            demonstrateCounters();
            
            // Demo 2: Set CRDTs  
            demonstrateSets();
            
            // Demo 3: Register CRDTs
            demonstrateRegisters();
            
            // Demo 4: Collaborative Document
            demonstrateCollaborativeDocument();
            
            // Demo 5: Distributed Like System
            demonstrateDistributedLikes();
            
            System.out.println("\n✅ CRDT Data Structures demo completed successfully!");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void demonstrateCounters() {
        System.out.println("\n=== Counter CRDTs Demo ===");
        
        // G-Counter demo - Website visitor count
        System.out.println("\n1. G-Counter (Grow-only): Website visitor tracking");
        
        GCounter mumbaiServer = new GCounter("mumbai");
        GCounter delhiServer = new GCounter("delhi");
        GCounter bangaloreServer = new GCounter("bangalore");
        
        // Each server counts visitors
        mumbaiServer.increment(100);    // 100 visitors
        delhiServer.increment(75);      // 75 visitors
        bangaloreServer.increment(120); // 120 visitors
        
        System.out.println("Mumbai: " + mumbaiServer);
        System.out.println("Delhi: " + delhiServer);
        System.out.println("Bangalore: " + bangaloreServer);
        
        // Merge to get global count
        GCounter globalCounter = mumbaiServer.copy();
        globalCounter.merge(delhiServer);
        globalCounter.merge(bangaloreServer);
        
        System.out.println("Global visitor count: " + globalCounter.getValue());
        
        // PN-Counter demo - Upvotes/Downvotes
        System.out.println("\n2. PN-Counter: Reddit-style upvotes/downvotes");
        
        PNCounter post1Votes = new PNCounter("server1");
        PNCounter post2Votes = new PNCounter("server2");
        
        // Server 1 counts
        post1Votes.increment(50);  // 50 upvotes
        post1Votes.decrement(10);  // 10 downvotes
        
        // Server 2 counts (same post, different server)
        post2Votes.increment(30);  // 30 upvotes
        post2Votes.decrement(5);   // 5 downvotes
        
        System.out.println("Server 1 vote count: " + post1Votes.getValue());
        System.out.println("Server 2 vote count: " + post2Votes.getValue());
        
        // Merge for global count
        post1Votes.merge(post2Votes);
        System.out.println("Global vote count: " + post1Votes.getValue());
    }
    
    private static void demonstrateSets() {
        System.out.println("\n=== Set CRDTs Demo ===");
        
        // G-Set demo - User interests
        System.out.println("\n1. G-Set (Grow-only): User interests tracking");
        
        GSet<String> userInterests1 = new GSet<>();
        GSet<String> userInterests2 = new GSet<>();
        
        // Different servers track interests
        userInterests1.add("Technology");
        userInterests1.add("Cricket");
        userInterests1.add("Movies");
        
        userInterests2.add("Technology");
        userInterests2.add("Food");
        userInterests2.add("Travel");
        
        System.out.println("Server 1 interests: " + userInterests1);
        System.out.println("Server 2 interests: " + userInterests2);
        
        userInterests1.merge(userInterests2);
        System.out.println("Merged interests: " + userInterests1);
        
        // OR-Set demo - Shopping cart items
        System.out.println("\n2. OR-Set (Observed-Remove): Shopping cart");
        
        ORSet<String> cart1 = new ORSet<>("user_session_1");
        ORSet<String> cart2 = new ORSet<>("user_session_2");
        
        // User adds items from different devices
        cart1.add("iPhone");
        cart1.add("AirPods");
        cart1.add("MacBook");
        
        cart2.add("iPhone");  // Same item added twice
        cart2.add("iPad");
        cart2.remove("iPhone"); // User removes iPhone
        
        System.out.println("Cart 1: " + cart1);
        System.out.println("Cart 2: " + cart2);
        
        cart1.merge(cart2);
        System.out.println("Merged cart: " + cart1);
    }
    
    private static void demonstrateRegisters() throws InterruptedException {
        System.out.println("\n=== Register CRDTs Demo ===");
        System.out.println("LWW-Register: User profile updates");
        
        LWWRegister<String> profile1 = new LWWRegister<>("mobile_app");
        LWWRegister<String> profile2 = new LWWRegister<>("web_app");
        
        // User updates profile from mobile
        profile1.set("Rahul Sharma, Software Engineer");
        Thread.sleep(10); // Small delay
        
        // User updates profile from web (later)
        profile2.set("Rahul Sharma, Senior Software Engineer, Mumbai");
        
        System.out.println("Mobile app profile: " + profile1);
        System.out.println("Web app profile: " + profile2);
        
        // Merge - last write wins
        profile1.merge(profile2);
        System.out.println("Final profile: " + profile1);
    }
    
    private static void demonstrateCollaborativeDocument() throws InterruptedException {
        System.out.println("\n=== Collaborative Document Demo ===");
        System.out.println("Google Docs-style collaborative editing");
        
        // Three users editing the same document
        CollaborativeDocument doc1 = new CollaborativeDocument("DOC_001", "rahul_laptop");
        CollaborativeDocument doc2 = new CollaborativeDocument("DOC_001", "priya_mobile"); 
        CollaborativeDocument doc3 = new CollaborativeDocument("DOC_001", "vikram_tablet");
        
        // Rahul starts the document
        doc1.setTitle("Project Proposal: AI-Powered E-commerce");
        doc1.addCollaborator("rahul");
        doc1.updateSection("introduction", "This project aims to revolutionize e-commerce using AI...");
        
        Thread.sleep(5);
        
        // Priya joins and edits
        doc2.addCollaborator("priya");
        doc2.updateSection("market_analysis", "Current market trends show increasing demand for personalized shopping...");
        
        Thread.sleep(5);
        
        // Vikram joins and edits
        doc3.addCollaborator("vikram");
        doc3.setTitle("Project Proposal: AI-Powered E-commerce Platform"); // Updated title
        doc3.updateSection("technical_approach", "We will use machine learning algorithms for recommendation engine...");
        
        // Everyone views the document
        doc1.incrementViewCount();
        doc2.incrementViewCount();
        doc3.incrementViewCount();
        
        System.out.println("\nDocument states before merge:");
        System.out.println("Rahul's view: " + doc1.getDocumentState());
        System.out.println("Priya's view: " + doc2.getDocumentState());
        System.out.println("Vikram's view: " + doc3.getDocumentState());
        
        // Merge all changes
        doc1.mergeWith(doc2);
        doc1.mergeWith(doc3);
        
        System.out.println("\nFinal merged document:");
        Map<String, Object> finalState = doc1.getDocumentState();
        for (Map.Entry<String, Object> entry : finalState.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
    }
    
    private static void demonstrateDistributedLikes() {
        System.out.println("\n=== Distributed Like System Demo ===");
        System.out.println("Instagram/Facebook-style distributed likes");
        
        // Three servers handling likes
        DistributedLikeSystem server1 = new DistributedLikeSystem("mumbai_server");
        DistributedLikeSystem server2 = new DistributedLikeSystem("delhi_server");
        DistributedLikeSystem server3 = new DistributedLikeSystem("bangalore_server");
        
        String post1 = "POST_Mumbai_Rains";
        String post2 = "POST_Cricket_Match";
        
        // Users like posts on different servers
        server1.likePost(post1, "user1");
        server1.likePost(post1, "user2");
        server1.likePost(post2, "user1");
        
        server2.likePost(post1, "user3");
        server2.likePost(post1, "user4");
        server2.likePost(post2, "user3");
        server2.likePost(post2, "user4");
        
        server3.likePost(post1, "user5");
        server3.likePost(post2, "user2"); // user2 likes from different server
        server3.likePost(post2, "user5");
        
        // Some users unlike
        server2.unlikePost(post1, "user3");
        server3.unlikePost(post2, "user5");
        
        System.out.println("\nBefore synchronization:");
        System.out.println("Mumbai server - Post1 likes: " + server1.getLikeCount(post1) + 
                          ", likers: " + server1.getLikers(post1));
        System.out.println("Delhi server - Post1 likes: " + server2.getLikeCount(post1) + 
                          ", likers: " + server2.getLikers(post1));
        System.out.println("Bangalore server - Post1 likes: " + server3.getLikeCount(post1) + 
                          ", likers: " + server3.getLikers(post1));
        
        // Synchronize all servers
        server1.mergeWith(server2);
        server1.mergeWith(server3);
        
        System.out.println("\nAfter synchronization:");
        System.out.println("Post1 total likes: " + server1.getLikeCount(post1) + 
                          ", active likers: " + server1.getLikers(post1));
        System.out.println("Post2 total likes: " + server1.getLikeCount(post2) + 
                          ", active likers: " + server1.getLikers(post2));
    }
}