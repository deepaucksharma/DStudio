/**
 * Social Media Feed Ordering System
 * Instagram/Facebook jaisa feed consistency with causal ordering
 * Handles posts, comments, likes with proper timeline ordering
 */

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.time.Instant;
import java.util.logging.Logger;
import java.util.stream.Collectors;

// Social media post - Instagram post jaisa
class SocialPost {
    private final String postId;
    private final String userId;
    private final String content;
    private final Instant timestamp;
    private final Set<String> dependencies; // Causal dependencies
    private volatile int likesCount;
    private volatile int commentsCount;
    private final String mediaUrl;
    private final VectorClock vectorClock;
    
    public SocialPost(String postId, String userId, String content, String mediaUrl, VectorClock vectorClock) {
        this.postId = postId;
        this.userId = userId;
        this.content = content;
        this.mediaUrl = mediaUrl;
        this.timestamp = Instant.now();
        this.dependencies = new HashSet<>();
        this.likesCount = 0;
        this.commentsCount = 0;
        this.vectorClock = vectorClock;
    }
    
    public void incrementLikes() { likesCount++; }
    public void incrementComments() { commentsCount++; }
    
    // Getters
    public String getPostId() { return postId; }
    public String getUserId() { return userId; }
    public String getContent() { return content; }
    public Instant getTimestamp() { return timestamp; }
    public Set<String> getDependencies() { return dependencies; }
    public int getLikesCount() { return likesCount; }
    public int getCommentsCount() { return commentsCount; }
    public String getMediaUrl() { return mediaUrl; }
    public VectorClock getVectorClock() { return vectorClock; }
    
    @Override
    public String toString() {
        return String.format("Post[%s]: %s by @%s (%d likes, %d comments)",
                           postId, content.substring(0, Math.min(content.length(), 50)),
                           userId, likesCount, commentsCount);
    }
}

// Comment on a post
class Comment {
    private final String commentId;
    private final String postId;
    private final String userId;
    private final String content;
    private final Instant timestamp;
    private final VectorClock vectorClock;
    private volatile int likesCount;
    
    public Comment(String commentId, String postId, String userId, String content, VectorClock vectorClock) {
        this.commentId = commentId;
        this.postId = postId;
        this.userId = userId;
        this.content = content;
        this.timestamp = Instant.now();
        this.vectorClock = vectorClock;
        this.likesCount = 0;
    }
    
    public void incrementLikes() { likesCount++; }
    
    // Getters
    public String getCommentId() { return commentId; }
    public String getPostId() { return postId; }
    public String getUserId() { return userId; }
    public String getContent() { return content; }
    public Instant getTimestamp() { return timestamp; }
    public VectorClock getVectorClock() { return vectorClock; }
    public int getLikesCount() { return likesCount; }
    
    @Override
    public String toString() {
        return String.format("@%s: %s (%d likes)", userId, content, likesCount);
    }
}

// Vector clock implementation for causal ordering
class VectorClock {
    private final Map<String, Integer> clocks;
    
    public VectorClock() {
        this.clocks = new ConcurrentHashMap<>();
    }
    
    public VectorClock(Map<String, Integer> clocks) {
        this.clocks = new ConcurrentHashMap<>(clocks);
    }
    
    public synchronized VectorClock increment(String nodeId) {
        Map<String, Integer> newClocks = new HashMap<>(clocks);
        newClocks.put(nodeId, newClocks.getOrDefault(nodeId, 0) + 1);
        return new VectorClock(newClocks);
    }
    
    public synchronized VectorClock merge(VectorClock other, String nodeId) {
        Map<String, Integer> newClocks = new HashMap<>();
        
        Set<String> allNodes = new HashSet<>(clocks.keySet());
        allNodes.addAll(other.clocks.keySet());
        
        for (String node : allNodes) {
            int thisTime = clocks.getOrDefault(node, 0);
            int otherTime = other.clocks.getOrDefault(node, 0);
            newClocks.put(node, Math.max(thisTime, otherTime));
        }
        
        // Increment current node
        newClocks.put(nodeId, newClocks.getOrDefault(nodeId, 0) + 1);
        
        return new VectorClock(newClocks);
    }
    
    public synchronized CausalRelation compareWith(VectorClock other) {
        if (clocks.equals(other.clocks)) {
            return CausalRelation.EQUAL;
        }
        
        boolean thisLessEqual = true;
        boolean thisGreaterEqual = true;
        
        Set<String> allNodes = new HashSet<>(clocks.keySet());
        allNodes.addAll(other.clocks.keySet());
        
        for (String node : allNodes) {
            int thisTime = clocks.getOrDefault(node, 0);
            int otherTime = other.clocks.getOrDefault(node, 0);
            
            if (thisTime > otherTime) {
                thisLessEqual = false;
            }
            if (thisTime < otherTime) {
                thisGreaterEqual = false;
            }
        }
        
        if (thisLessEqual && thisGreaterEqual) {
            return CausalRelation.EQUAL;
        } else if (thisLessEqual) {
            return CausalRelation.HAPPENS_BEFORE;
        } else if (thisGreaterEqual) {
            return CausalRelation.HAPPENS_AFTER;
        } else {
            return CausalRelation.CONCURRENT;
        }
    }
    
    @Override
    public String toString() {
        return clocks.toString();
    }
}

enum CausalRelation {
    HAPPENS_BEFORE, HAPPENS_AFTER, CONCURRENT, EQUAL
}

// User feed with causal consistency
class UserFeed {
    private final String userId;
    private final List<SocialPost> posts;
    private final Map<String, List<Comment>> postComments;
    private final VectorClock userClock;
    private final Set<String> seenPosts;
    
    public UserFeed(String userId) {
        this.userId = userId;
        this.posts = new ArrayList<>();
        this.postComments = new ConcurrentHashMap<>();
        this.userClock = new VectorClock();
        this.seenPosts = new HashSet<>();
    }
    
    public synchronized void addPost(SocialPost post) {
        if (!seenPosts.contains(post.getPostId())) {
            posts.add(post);
            seenPosts.add(post.getPostId());
            postComments.put(post.getPostId(), new ArrayList<>());
        }
    }
    
    public synchronized void addComment(Comment comment) {
        List<Comment> comments = postComments.get(comment.getPostId());
        if (comments != null) {
            comments.add(comment);
        }
    }
    
    public synchronized List<SocialPost> getCausallyOrderedPosts() {
        // Sort posts based on causal ordering
        List<SocialPost> orderedPosts = new ArrayList<>(posts);
        
        orderedPosts.sort((p1, p2) -> {
            CausalRelation relation = p1.getVectorClock().compareWith(p2.getVectorClock());
            
            switch (relation) {
                case HAPPENS_BEFORE:
                    return -1;
                case HAPPENS_AFTER:
                    return 1;
                case CONCURRENT:
                case EQUAL:
                    // Use timestamp as tiebreaker for concurrent events
                    return p1.getTimestamp().compareTo(p2.getTimestamp());
                default:
                    return 0;
            }
        });
        
        return orderedPosts;
    }
    
    public List<Comment> getCommentsForPost(String postId) {
        return postComments.getOrDefault(postId, new ArrayList<>());
    }
    
    public String getUserId() { return userId; }
    public VectorClock getUserClock() { return userClock; }
}

// Main social media feed manager
public class SocialMediaFeedOrdering {
    private static final Logger logger = Logger.getLogger(SocialMediaFeedOrdering.class.getName());
    
    private final Map<String, UserFeed> userFeeds;
    private final Map<String, SocialPost> allPosts;
    private final Map<String, Comment> allComments;
    private final AtomicLong postCounter;
    private final AtomicLong commentCounter;
    private final ExecutorService feedUpdater;
    
    // Simulated servers in different regions
    private final Map<String, VectorClock> serverClocks;
    
    public SocialMediaFeedOrdering() {
        this.userFeeds = new ConcurrentHashMap<>();
        this.allPosts = new ConcurrentHashMap<>();
        this.allComments = new ConcurrentHashMap<>();
        this.postCounter = new AtomicLong(1);
        this.commentCounter = new AtomicLong(1);
        this.feedUpdater = Executors.newFixedThreadPool(10);
        
        // Initialize server clocks
        this.serverClocks = new ConcurrentHashMap<>();
        serverClocks.put("mumbai", new VectorClock());
        serverClocks.put("delhi", new VectorClock());
        serverClocks.put("bangalore", new VectorClock());
    }
    
    public void registerUser(String userId) {
        userFeeds.put(userId, new UserFeed(userId));
        logger.info("User registered: " + userId);
    }
    
    // Create new post - Instagram post karna jaisa
    public String createPost(String userId, String content, String mediaUrl, String serverLocation) {
        if (!userFeeds.containsKey(userId)) {
            registerUser(userId);
        }
        
        String postId = "POST_" + postCounter.getAndIncrement();
        
        // Get and update server clock
        VectorClock serverClock = serverClocks.get(serverLocation);
        VectorClock newClock = serverClock.increment(serverLocation);
        serverClocks.put(serverLocation, newClock);
        
        SocialPost post = new SocialPost(postId, userId, content, mediaUrl, newClock);
        allPosts.put(postId, post);
        
        // Add to user's own feed
        UserFeed userFeed = userFeeds.get(userId);
        userFeed.addPost(post);
        
        logger.info(String.format("Post created: %s by %s on %s server", postId, userId, serverLocation));
        
        // Async propagation to followers
        propagatePostToFollowers(post, userId);
        
        return postId;
    }
    
    // Add comment with causal dependency
    public String addComment(String userId, String postId, String content, String serverLocation) {
        SocialPost post = allPosts.get(postId);
        if (post == null) {
            logger.warning("Post not found: " + postId);
            return null;
        }
        
        // Check if user has seen the post (causal dependency)
        UserFeed userFeed = userFeeds.get(userId);
        if (userFeed == null || !userFeed.seenPosts.contains(postId)) {
            logger.warning(String.format("User %s hasn't seen post %s", userId, postId));
            return null;
        }
        
        String commentId = "COMMENT_" + commentCounter.getAndIncrement();
        
        // Merge with post's vector clock and increment
        VectorClock serverClock = serverClocks.get(serverLocation);
        VectorClock mergedClock = serverClock.merge(post.getVectorClock(), serverLocation);
        serverClocks.put(serverLocation, mergedClock);
        
        Comment comment = new Comment(commentId, postId, userId, content, mergedClock);
        allComments.put(commentId, comment);
        
        // Update post comment count
        post.incrementComments();
        
        // Add to all feeds that have seen the post
        for (UserFeed feed : userFeeds.values()) {
            if (feed.seenPosts.contains(postId)) {
                feed.addComment(comment);
            }
        }
        
        logger.info(String.format("Comment added: %s by %s on post %s", commentId, userId, postId));
        
        return commentId;
    }
    
    // Like a post
    public boolean likePost(String userId, String postId, String serverLocation) {
        SocialPost post = allPosts.get(postId);
        if (post == null) {
            return false;
        }
        
        // Check if user has seen the post
        UserFeed userFeed = userFeeds.get(userId);
        if (userFeed == null || !userFeed.seenPosts.contains(postId)) {
            logger.warning(String.format("User %s hasn't seen post %s", userId, postId));
            return false;
        }
        
        post.incrementLikes();
        
        // Update server clock
        VectorClock serverClock = serverClocks.get(serverLocation);
        VectorClock newClock = serverClock.increment(serverLocation);
        serverClocks.put(serverLocation, newClock);
        
        logger.info(String.format("Post liked: %s by %s", postId, userId));
        
        return true;
    }
    
    // Propagate post to followers (simulated)
    private void propagatePostToFollowers(SocialPost post, String authorId) {
        feedUpdater.submit(() -> {
            try {
                // Simulate network delay
                Thread.sleep(new Random().nextInt(100) + 50);
                
                // Add to all user feeds (simulating followers)
                for (Map.Entry<String, UserFeed> entry : userFeeds.entrySet()) {
                    String userId = entry.getKey();
                    UserFeed feed = entry.getValue();
                    
                    // Don't add to author's own feed again
                    if (!userId.equals(authorId)) {
                        feed.addPost(post);
                    }
                }
                
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
    }
    
    // Get user's feed in causal order
    public List<SocialPost> getUserFeed(String userId, int limit) {
        UserFeed feed = userFeeds.get(userId);
        if (feed == null) {
            return new ArrayList<>();
        }
        
        List<SocialPost> orderedPosts = feed.getCausallyOrderedPosts();
        
        return orderedPosts.stream()
                          .limit(limit)
                          .collect(Collectors.toList());
    }
    
    // Get comments for a post in causal order
    public List<Comment> getPostComments(String postId) {
        List<Comment> comments = new ArrayList<>();
        
        for (Comment comment : allComments.values()) {
            if (comment.getPostId().equals(postId)) {
                comments.add(comment);
            }
        }
        
        // Sort by causal order
        comments.sort((c1, c2) -> {
            CausalRelation relation = c1.getVectorClock().compareWith(c2.getVectorClock());
            
            switch (relation) {
                case HAPPENS_BEFORE:
                    return -1;
                case HAPPENS_AFTER:
                    return 1;
                case CONCURRENT:
                case EQUAL:
                    return c1.getTimestamp().compareTo(c2.getTimestamp());
                default:
                    return 0;
            }
        });
        
        return comments;
    }
    
    // Detect causal violations in feed
    public List<String> detectCausalViolations(String userId) {
        List<String> violations = new ArrayList<>();
        UserFeed feed = userFeeds.get(userId);
        
        if (feed == null) {
            return violations;
        }
        
        List<SocialPost> posts = feed.getCausallyOrderedPosts();
        
        for (int i = 0; i < posts.size() - 1; i++) {
            SocialPost current = posts.get(i);
            SocialPost next = posts.get(i + 1);
            
            CausalRelation relation = current.getVectorClock().compareWith(next.getVectorClock());
            
            if (relation == CausalRelation.HAPPENS_AFTER) {
                violations.add(String.format("Causal violation: Post %s should come after %s",
                                            current.getPostId(), next.getPostId()));
            }
        }
        
        return violations;
    }
    
    // Simulate Instagram-like user activity
    public void simulateUserActivity(int users, int postsPerUser, int interactionsPerUser) {
        List<String> userIds = new ArrayList<>();
        
        // Create users
        for (int i = 1; i <= users; i++) {
            String userId = "user_" + i;
            registerUser(userId);
            userIds.add(userId);
        }
        
        Random random = new Random();
        String[] servers = {"mumbai", "delhi", "bangalore"};
        String[] postContents = {
            "Mumbai mein baarish! 🌧️",
            "Coffee with friends ☕",
            "Weekend vibes 🎉",
            "Work from home setup 💻",
            "Delicious food! 🍕",
            "Beautiful sunset 🌅",
            "Reading a good book 📚",
            "Gym workout done! 💪"
        };
        
        List<String> allPostIds = new ArrayList<>();
        
        // Create posts
        for (String userId : userIds) {
            for (int i = 0; i < postsPerUser; i++) {
                String content = postContents[random.nextInt(postContents.length)];
                String server = servers[random.nextInt(servers.length)];
                
                String postId = createPost(userId, content, "image_" + i + ".jpg", server);
                allPostIds.add(postId);
                
                // Small delay between posts
                try {
                    Thread.sleep(10);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
        
        // Wait for propagation
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        }
        
        // User interactions
        for (String userId : userIds) {
            for (int i = 0; i < interactionsPerUser; i++) {
                String postId = allPostIds.get(random.nextInt(allPostIds.size()));
                String server = servers[random.nextInt(servers.length)];
                
                if (random.nextBoolean()) {
                    // Like post
                    likePost(userId, postId, server);
                } else {
                    // Comment on post
                    String[] commentTexts = {"Nice!", "Great post!", "Love it!", "Amazing!"};
                    String commentText = commentTexts[random.nextInt(commentTexts.length)];
                    addComment(userId, postId, commentText, server);
                }
                
                try {
                    Thread.sleep(5);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }
    
    public void shutdown() {
        feedUpdater.shutdown();
        try {
            if (!feedUpdater.awaitTermination(5, TimeUnit.SECONDS)) {
                feedUpdater.shutdownNow();
            }
        } catch (InterruptedException e) {
            feedUpdater.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    public static void main(String[] args) {
        System.out.println("=== Social Media Feed Ordering Demo ===");
        
        SocialMediaFeedOrdering feedManager = new SocialMediaFeedOrdering();
        
        try {
            // Register users
            System.out.println("\n=== Registering Users ===");
            String[] users = {"rahul", "priya", "vikram", "anita", "rohan"};
            
            for (String user : users) {
                feedManager.registerUser(user);
                System.out.println("Registered: @" + user);
            }
            
            // Create posts with causal dependencies
            System.out.println("\n=== Creating Posts ===");
            
            String post1 = feedManager.createPost("rahul", "Mumbai mein baarish aa gayi! 🌧️", "rain.jpg", "mumbai");
            String post2 = feedManager.createPost("priya", "Coffee time! ☕", "coffee.jpg", "delhi");
            String post3 = feedManager.createPost("vikram", "Working from home today 💻", "wfh.jpg", "bangalore");
            
            // Wait for propagation
            Thread.sleep(200);
            
            // Add comments and likes
            System.out.println("\n=== User Interactions ===");
            
            feedManager.likePost("priya", post1, "delhi");
            feedManager.addComment("priya", post1, "Stay safe in the rain!", "delhi");
            
            feedManager.likePost("vikram", post1, "bangalore");
            feedManager.addComment("vikram", post1, "Mumbai weather is unpredictable!", "bangalore");
            
            feedManager.likePost("rahul", post2, "mumbai");
            feedManager.addComment("rahul", post2, "Which cafe?", "mumbai");
            
            feedManager.likePost("anita", post3, "mumbai");
            feedManager.addComment("anita", post3, "WFH is the best!", "mumbai");
            
            // More posts creating causal chains
            String post4 = feedManager.createPost("anita", "Reply to @rahul: It's Cafe Coffee Day in Bandra", "ccd.jpg", "mumbai");
            
            // Wait for all updates
            Thread.sleep(300);
            
            // Display user feeds
            System.out.println("\n=== User Feeds (Causal Order) ===");
            
            for (String user : users) {
                System.out.println("\n@" + user + "'s feed:");
                List<SocialPost> feed = feedManager.getUserFeed(user, 5);
                
                for (SocialPost post : feed) {
                    System.out.println("  " + post.toString());
                    
                    // Show comments
                    List<Comment> comments = feedManager.getPostComments(post.getPostId());
                    for (Comment comment : comments) {
                        System.out.println("    💬 " + comment.toString());
                    }
                }
            }
            
            // Check for causal violations
            System.out.println("\n=== Causal Consistency Check ===");
            
            for (String user : users) {
                List<String> violations = feedManager.detectCausalViolations(user);
                
                if (violations.isEmpty()) {
                    System.out.println("✅ @" + user + ": No causal violations");
                } else {
                    System.out.println("❌ @" + user + ": Causal violations detected:");
                    for (String violation : violations) {
                        System.out.println("  - " + violation);
                    }
                }
            }
            
            // Simulate heavy activity
            System.out.println("\n=== Simulating Heavy User Activity ===");
            feedManager.simulateUserActivity(10, 3, 5);
            
            Thread.sleep(1000);
            
            System.out.println("Heavy activity simulation completed");
            
            // Final stats
            System.out.println("\n=== Final Statistics ===");
            System.out.println("Total posts: " + feedManager.allPosts.size());
            System.out.println("Total comments: " + feedManager.allComments.size());
            System.out.println("Active users: " + feedManager.userFeeds.size());
            
            System.out.println("\n✅ Social Media Feed Ordering demo completed!");
            
        } catch (Exception e) {
            System.err.println("Demo failed: " + e.getMessage());
            e.printStackTrace();
        } finally {
            feedManager.shutdown();
        }
    }
}