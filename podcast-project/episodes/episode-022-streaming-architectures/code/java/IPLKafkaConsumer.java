/**
 * IPL Match Commentary Stream - Kafka Consumer
 * यह consumer IPL के live commentary stream को process करता है
 * Example: JioCinema, ESPN Cricinfo जैसे apps के लिए real-time updates
 */

import org.apache.kafka.clients.consumer.*;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.TopicPartition;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Duration;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class IPLKafkaConsumer {
    
    private final KafkaConsumer<String, String> consumer;
    private final ObjectMapper objectMapper;
    private final Map<String, MatchState> matchStates;
    private volatile boolean isRunning = true;
    
    // Consumer configuration optimized for IPL live commentary
    public IPLKafkaConsumer(String bootstrapServers, String groupId, List<String> topics) {
        this.objectMapper = new ObjectMapper();
        this.matchStates = new ConcurrentHashMap<>();
        
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        
        // Optimized for low latency commentary processing
        // कम से कम latency चाहिए cricket commentary के लिए
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest"); // Only new messages
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, "false"); // Manual commit for reliability
        props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, "100"); // Process in small batches
        props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, "10"); // 10ms max wait
        props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, "1"); // Don't wait for batching
        
        // Session and heartbeat settings
        props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, "30000"); // 30 seconds
        props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, "3000"); // 3 seconds
        
        this.consumer = new KafkaConsumer<>(props);
        consumer.subscribe(topics);
    }
    
    /**
     * Main polling loop for processing IPL commentary
     * यह continuously cricket commentary को process करता है
     */
    public void startCommentaryProcessing() {
        System.out.println("IPL Commentary Consumer शुरू हो गया...");
        
        try {
            while (isRunning) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                if (records.isEmpty()) {
                    continue;
                }
                
                // Process each commentary message
                for (ConsumerRecord<String, String> record : records) {
                    processCommentaryMessage(record);
                }
                
                // Manual commit after successful processing
                // सफल processing के बाद ही commit करते हैं
                consumer.commitSync();
                
                // Check for any match state updates to broadcast
                broadcastMatchUpdates();
            }
        } catch (Exception e) {
            System.err.println("Error in commentary processing: " + e.getMessage());
        } finally {
            consumer.close();
            System.out.println("IPL Commentary Consumer बंद हो गया");
        }
    }
    
    /**
     * Process individual commentary messages
     * हर commentary message को parse करके appropriate action लेता है
     */
    private void processCommentaryMessage(ConsumerRecord<String, String> record) {
        try {
            String topic = record.topic();
            String matchId = record.key();
            
            // Parse the message based on topic
            if (topic.equals("ipl-live-scores")) {
                IPLBallData ballData = objectMapper.readValue(record.value(), IPLBallData.class);
                processBallByBallUpdate(ballData);
                
            } else if (topic.equals("ipl-milestones")) {
                IPLMilestoneEvent milestone = objectMapper.readValue(record.value(), IPLMilestoneEvent.class);
                processMilestoneEvent(milestone);
                
            } else if (topic.equals("ipl-match-status")) {
                IPLMatchStatus status = objectMapper.readValue(record.value(), IPLMatchStatus.class);
                processMatchStatusUpdate(status);
            }
            
        } catch (Exception e) {
            System.err.println("Error processing message: " + e.getMessage());
            // In production, you might want to send to dead letter queue
        }
    }
    
    /**
     * Process ball-by-ball updates and update match state
     * हर ball का data process करके match की current state update करता है
     */
    private void processBallByBallUpdate(IPLBallData ballData) {
        String matchId = ballData.getMatchId();
        
        // Get or create match state
        MatchState matchState = matchStates.computeIfAbsent(matchId, k -> new MatchState(matchId));
        
        // Update match state with new ball data
        matchState.updateWithBall(ballData);
        
        // Generate real-time statistics
        MatchStatistics stats = generateRealTimeStats(matchState);
        
        // Check for interesting patterns or alerts
        checkForPatterns(ballData, matchState);
        
        System.out.println(String.format(
            "Ball Update: %s vs %s - %d/%d (Over %d.%d) - %s",
            ballData.getBattingTeam(),
            ballData.getBowlingTeam(),
            ballData.getTotalRuns(),
            ballData.getWicketsDown(),
            ballData.getOver(),
            ballData.getBall(),
            ballData.getCommentary()
        ));
        
        // Update dashboard or send push notifications
        updateLiveDashboard(matchState, stats);
    }
    
    /**
     * Process milestone events (centuries, wickets, etc.)
     * खास events के लिए special handling
     */
    private void processMilestoneEvent(IPLMilestoneEvent milestone) {
        System.out.println(String.format(
            "🎉 MILESTONE: %s - %s (%s)",
            milestone.getPlayerName(),
            milestone.getEventType(),
            milestone.getDescription()
        ));
        
        // Send push notifications for milestones
        sendPushNotification(milestone);
        
        // Update player statistics
        updatePlayerStats(milestone);
        
        // Check if this milestone affects match predictions
        updateMatchPredictions(milestone);
    }
    
    /**
     * Generate real-time statistics
     * मैच के real-time stats calculate करता है
     */
    private MatchStatistics generateRealTimeStats(MatchState matchState) {
        MatchStatistics stats = new MatchStatistics();
        
        // Current run rate calculation
        if (matchState.getBallsFaced() > 0) {
            double currentRunRate = (matchState.getTotalRuns() * 6.0) / matchState.getBallsFaced();
            stats.setCurrentRunRate(currentRunRate);
        }
        
        // Required run rate calculation (if chasing)
        if (matchState.isSecondInnings() && matchState.getTarget() > 0) {
            int remainingRuns = matchState.getTarget() - matchState.getTotalRuns();
            int remainingBalls = (20 * 6) - matchState.getBallsFaced();
            
            if (remainingBalls > 0) {
                double requiredRunRate = (remainingRuns * 6.0) / remainingBalls;
                stats.setRequiredRunRate(requiredRunRate);
            }
        }
        
        // Partnership statistics
        Partnership currentPartnership = matchState.getCurrentPartnership();
        if (currentPartnership != null) {
            stats.setPartnershipRuns(currentPartnership.getRuns());
            stats.setPartnershipBalls(currentPartnership.getBalls());
        }
        
        // Power play statistics
        if (matchState.getBallsFaced() <= 36) { // First 6 overs
            stats.setPowerPlayRuns(matchState.getTotalRuns());
            stats.setPowerPlayRunRate(stats.getCurrentRunRate());
        }
        
        return stats;
    }
    
    /**
     * Check for interesting patterns in the match
     * मैच में interesting patterns detect करता है
     */
    private void checkForPatterns(IPLBallData ballData, MatchState matchState) {
        // Check for consecutive boundaries
        if (matchState.getConsecutiveBoundaries() >= 2) {
            System.out.println("🔥 Hot streak! " + matchState.getConsecutiveBoundaries() + 
                             " consecutive boundaries!");
        }
        
        // Check for tight over (less than 6 runs)
        if (ballData.getBall() == 6 && matchState.getRunsInCurrentOver() <= 5) {
            System.out.println("🛡️ Tight over! Only " + matchState.getRunsInCurrentOver() + 
                             " runs in the over");
        }
        
        // Check for expensive over (more than 15 runs)
        if (ballData.getBall() == 6 && matchState.getRunsInCurrentOver() >= 15) {
            System.out.println("💥 Expensive over! " + matchState.getRunsInCurrentOver() + 
                             " runs conceded");
        }
        
        // Check for match momentum shifts
        double recentRunRate = matchState.getRunRateInLast5Overs();
        if (recentRunRate > matchState.getOverallRunRate() + 2.0) {
            System.out.println("📈 Momentum shift! Batting team accelerating");
        }
    }
    
    /**
     * Update live dashboard with latest match data
     * Live dashboard को latest data के साथ update करता है
     */
    private void updateLiveDashboard(MatchState matchState, MatchStatistics stats) {
        // In a real application, this would update Redis cache or database
        // जो dashboard और mobile apps real-time में use करते हैं
        
        LiveDashboardUpdate update = new LiveDashboardUpdate(
            matchState.getMatchId(),
            matchState.getTotalRuns(),
            matchState.getWicketsDown(),
            matchState.getBallsFaced(),
            stats.getCurrentRunRate(),
            stats.getRequiredRunRate(),
            matchState.getCurrentBatsman(),
            matchState.getCurrentBowler(),
            System.currentTimeMillis()
        );
        
        // Send to dashboard service (Redis/Database)
        publishToDashboard(update);
    }
    
    /**
     * Send push notifications for milestone events
     * Milestone events के लिए push notifications भेजता है
     */
    private void sendPushNotification(IPLMilestoneEvent milestone) {
        PushNotification notification = new PushNotification(
            "IPL Update",
            milestone.getDescription(),
            milestone.getMatchId(),
            "milestone"
        );
        
        // In production, this would integrate with FCM/APNS
        System.out.println("Push Notification: " + notification.getMessage());
    }
    
    /**
     * Broadcast match updates to subscribed clients
     * WebSocket connections को match updates भेजता है
     */
    private void broadcastMatchUpdates() {
        for (MatchState matchState : matchStates.values()) {
            if (matchState.hasUpdates()) {
                // Broadcast via WebSocket to all connected clients
                broadcastToWebSockets(matchState);
                matchState.clearUpdateFlag();
            }
        }
    }
    
    /**
     * Stop the consumer gracefully
     * Consumer को safely stop करने के लिए
     */
    public void stop() {
        isRunning = false;
        consumer.wakeup();
    }
    
    // Placeholder methods for external integrations
    private void updatePlayerStats(IPLMilestoneEvent milestone) {
        // Update player database with milestone
    }
    
    private void updateMatchPredictions(IPLMilestoneEvent milestone) {
        // Update ML model predictions based on milestone
    }
    
    private void publishToDashboard(LiveDashboardUpdate update) {
        // Publish to Redis or dashboard database
    }
    
    private void broadcastToWebSockets(MatchState matchState) {
        // Broadcast to WebSocket connections
    }
    
    // Demo method
    public static void main(String[] args) {
        String kafkaServers = "localhost:9092";
        String groupId = "ipl-commentary-group";
        List<String> topics = Arrays.asList("ipl-live-scores", "ipl-milestones", "ipl-match-status");
        
        IPLKafkaConsumer consumer = new IPLKafkaConsumer(kafkaServers, groupId, topics);
        
        // Add shutdown hook for graceful termination
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            System.out.println("Shutting down IPL Commentary Consumer...");
            consumer.stop();
        }));
        
        // Start processing
        consumer.startCommentaryProcessing();
    }
}

/**
 * Match State tracking class
 * हर match की current state track करने के लिए
 */
class MatchState {
    private String matchId;
    private int totalRuns = 0;
    private int wicketsDown = 0;
    private int ballsFaced = 0;
    private int currentOver = 0;
    private int runsInCurrentOver = 0;
    private int consecutiveBoundaries = 0;
    private boolean hasUpdates = false;
    private String currentBatsman = "";
    private String currentBowler = "";
    private boolean secondInnings = false;
    private int target = 0;
    private Partnership currentPartnership;
    private List<Integer> overRuns = new ArrayList<>();
    
    public MatchState(String matchId) {
        this.matchId = matchId;
        this.currentPartnership = new Partnership();
    }
    
    public void updateWithBall(IPLBallData ballData) {
        this.totalRuns = ballData.getTotalRuns();
        this.wicketsDown = ballData.getWicketsDown();
        this.ballsFaced++;
        this.currentBatsman = ballData.getBatsman();
        this.currentBowler = ballData.getBowler();
        this.hasUpdates = true;
        
        // Update over tracking
        if (ballData.getOver() != this.currentOver) {
            if (this.currentOver > 0) {
                overRuns.add(runsInCurrentOver);
            }
            this.currentOver = ballData.getOver();
            this.runsInCurrentOver = ballData.getRuns();
        } else {
            this.runsInCurrentOver += ballData.getRuns();
        }
        
        // Track consecutive boundaries
        if (ballData.getRuns() >= 4) {
            consecutiveBoundaries++;
        } else {
            consecutiveBoundaries = 0;
        }
        
        // Update partnership
        currentPartnership.addRuns(ballData.getRuns());
        if (ballData.isWicket()) {
            currentPartnership = new Partnership(); // New partnership
        }
    }
    
    public double getOverallRunRate() {
        return ballsFaced > 0 ? (totalRuns * 6.0) / ballsFaced : 0.0;
    }
    
    public double getRunRateInLast5Overs() {
        if (overRuns.size() < 5) return getOverallRunRate();
        
        int recentRuns = 0;
        for (int i = Math.max(0, overRuns.size() - 5); i < overRuns.size(); i++) {
            recentRuns += overRuns.get(i);
        }
        
        return recentRuns / 5.0; // Average runs per over in last 5 overs
    }
    
    // Getters and Setters
    public String getMatchId() { return matchId; }
    public int getTotalRuns() { return totalRuns; }
    public int getWicketsDown() { return wicketsDown; }
    public int getBallsFaced() { return ballsFaced; }
    public int getConsecutiveBoundaries() { return consecutiveBoundaries; }
    public int getRunsInCurrentOver() { return runsInCurrentOver; }
    public boolean hasUpdates() { return hasUpdates; }
    public void clearUpdateFlag() { hasUpdates = false; }
    public String getCurrentBatsman() { return currentBatsman; }
    public String getCurrentBowler() { return currentBowler; }
    public boolean isSecondInnings() { return secondInnings; }
    public void setSecondInnings(boolean secondInnings) { this.secondInnings = secondInnings; }
    public int getTarget() { return target; }
    public void setTarget(int target) { this.target = target; }
    public Partnership getCurrentPartnership() { return currentPartnership; }
}

/**
 * Partnership tracking
 * Current partnership की details track करने के लिए
 */
class Partnership {
    private int runs = 0;
    private int balls = 0;
    
    public void addRuns(int runs) {
        this.runs += runs;
        this.balls++;
    }
    
    public int getRuns() { return runs; }
    public int getBalls() { return balls; }
}

/**
 * Real-time match statistics
 * Match के real-time statistics के लिए
 */
class MatchStatistics {
    private double currentRunRate;
    private double requiredRunRate;
    private int partnershipRuns;
    private int partnershipBalls;
    private int powerPlayRuns;
    private double powerPlayRunRate;
    
    // Getters and Setters
    public double getCurrentRunRate() { return currentRunRate; }
    public void setCurrentRunRate(double currentRunRate) { this.currentRunRate = currentRunRate; }
    
    public double getRequiredRunRate() { return requiredRunRate; }
    public void setRequiredRunRate(double requiredRunRate) { this.requiredRunRate = requiredRunRate; }
    
    public int getPartnershipRuns() { return partnershipRuns; }
    public void setPartnershipRuns(int partnershipRuns) { this.partnershipRuns = partnershipRuns; }
    
    public int getPartnershipBalls() { return partnershipBalls; }
    public void setPartnershipBalls(int partnershipBalls) { this.partnershipBalls = partnershipBalls; }
    
    public int getPowerPlayRuns() { return powerPlayRuns; }
    public void setPowerPlayRuns(int powerPlayRuns) { this.powerPlayRuns = powerPlayRuns; }
    
    public double getPowerPlayRunRate() { return powerPlayRunRate; }
    public void setPowerPlayRunRate(double powerPlayRunRate) { this.powerPlayRunRate = powerPlayRunRate; }
}

/**
 * Live Dashboard Update Model
 * Dashboard updates के लिए data structure
 */
class LiveDashboardUpdate {
    private String matchId;
    private int runs;
    private int wickets;
    private int ballsFaced;
    private double currentRunRate;
    private double requiredRunRate;
    private String currentBatsman;
    private String currentBowler;
    private long timestamp;
    
    public LiveDashboardUpdate(String matchId, int runs, int wickets, int ballsFaced,
                             double currentRunRate, double requiredRunRate,
                             String currentBatsman, String currentBowler, long timestamp) {
        this.matchId = matchId;
        this.runs = runs;
        this.wickets = wickets;
        this.ballsFaced = ballsFaced;
        this.currentRunRate = currentRunRate;
        this.requiredRunRate = requiredRunRate;
        this.currentBatsman = currentBatsman;
        this.currentBowler = currentBowler;
        this.timestamp = timestamp;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public int getRuns() { return runs; }
    public int getWickets() { return wickets; }
    public int getBallsFaced() { return ballsFaced; }
    public double getCurrentRunRate() { return currentRunRate; }
    public double getRequiredRunRate() { return requiredRunRate; }
    public String getCurrentBatsman() { return currentBatsman; }
    public String getCurrentBowler() { return currentBowler; }
    public long getTimestamp() { return timestamp; }
}

/**
 * Push Notification Model
 * Mobile push notifications के लिए
 */
class PushNotification {
    private String title;
    private String message;
    private String matchId;
    private String type;
    
    public PushNotification(String title, String message, String matchId, String type) {
        this.title = title;
        this.message = message;
        this.matchId = matchId;
        this.type = type;
    }
    
    // Getters
    public String getTitle() { return title; }
    public String getMessage() { return message; }
    public String getMatchId() { return matchId; }
    public String getType() { return type; }
}

/**
 * IPL Match Status Model
 * Match status updates के लिए (innings break, toss, etc.)
 */
class IPLMatchStatus {
    private String matchId;
    private String status; // TOSS, INNINGS_BREAK, MATCH_ENDED, etc.
    private String description;
    private long timestamp;
    
    public IPLMatchStatus(String matchId, String status, String description, long timestamp) {
        this.matchId = matchId;
        this.status = status;
        this.description = description;
        this.timestamp = timestamp;
    }
    
    // Getters and Setters
    public String getMatchId() { return matchId; }
    public void setMatchId(String matchId) { this.matchId = matchId; }
    
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}