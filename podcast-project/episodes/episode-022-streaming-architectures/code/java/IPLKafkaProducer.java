/**
 * IPL Live Score Updates - Kafka Producer
 * यह Kafka producer IPL के live score updates भेजने के लिए है
 * Example: Hotstar जैसे platforms के लिए real-time cricket data
 */

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.*;
import java.util.concurrent.Future;

public class IPLKafkaProducer {
    
    private final KafkaProducer<String, String> producer;
    private final ObjectMapper objectMapper;
    private final String topicName;
    
    // Kafka producer configuration for high-throughput IPL data
    public IPLKafkaProducer(String bootstrapServers, String topic) {
        this.topicName = topic;
        this.objectMapper = new ObjectMapper();
        
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        
        // Performance optimizations for live cricket data
        // बैच साइज़ बढ़ाया है क्योंकि IPL में बहुत सारे events आते हैं
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 32768); // 32KB batches
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10); // 10ms batching delay
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "snappy"); // Fast compression
        props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864); // 64MB buffer
        
        // Reliability settings for critical IPL data
        props.put(ProducerConfig.ACKS_CONFIG, "1"); // Leader acknowledgment only for speed
        props.put(ProducerConfig.RETRIES_CONFIG, 3);
        props.put(ProducerConfig.RETRY_BACKOFF_MS_CONFIG, 100);
        
        this.producer = new KafkaProducer<>(props);
    }
    
    /**
     * Ball-by-ball data के लिए main method
     * हर ball पर यह data send करता है - score, wicket, extras सब कुछ
     */
    public void publishBallByBallUpdate(IPLBallData ballData) {
        try {
            String jsonData = objectMapper.writeValueAsString(ballData);
            String key = generatePartitionKey(ballData);
            
            ProducerRecord<String, String> record = new ProducerRecord<>(
                topicName,
                key,
                jsonData
            );
            
            // Asynchronous send with callback for error handling
            // गलती होने पर तुरंत पता चल जाएगा
            Future<RecordMetadata> future = producer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    if (exception != null) {
                        System.err.println("IPL Ball data send failed: " + exception.getMessage());
                        // Implement retry logic or dead letter queue
                    } else {
                        System.out.println(
                            String.format("Ball data sent successfully - Match: %s, Over: %d.%d", 
                                ballData.getMatchId(), 
                                ballData.getOver(), 
                                ballData.getBall())
                        );
                    }
                }
            });
            
        } catch (Exception e) {
            System.err.println("Error serializing IPL ball data: " + e.getMessage());
        }
    }
    
    /**
     * Milestone events के लिए special handling
     * जैसे - century, wicket, six, etc.
     */
    public void publishMilestoneEvent(IPLMilestoneEvent milestone) {
        try {
            String jsonData = objectMapper.writeValueAsString(milestone);
            String key = milestone.getMatchId() + "_milestone";
            
            ProducerRecord<String, String> record = new ProducerRecord<>(
                "ipl-milestones", // Separate topic for important events
                key,
                jsonData
            );
            
            // High priority send for milestones
            producer.send(record).get(); // Synchronous send for milestones
            
            System.out.println("Milestone published: " + milestone.getEventType() + 
                             " by " + milestone.getPlayerName());
                             
        } catch (Exception e) {
            System.err.println("Milestone event send failed: " + e.getMessage());
        }
    }
    
    /**
     * Partition key generation for optimal load distribution
     * सभी matches का data अलग-अलग partitions में जाएगा
     */
    private String generatePartitionKey(IPLBallData ballData) {
        // Use match ID as partition key to keep all match data together
        return ballData.getMatchId();
    }
    
    /**
     * Close producer gracefully
     * Program end होने पर सभी pending messages send करके close करना
     */
    public void close() {
        try {
            producer.flush(); // Send all buffered records
            producer.close();
            System.out.println("IPL Kafka Producer closed successfully");
        } catch (Exception e) {
            System.err.println("Error closing producer: " + e.getMessage());
        }
    }
    
    // Demo method for testing with sample IPL data
    public static void main(String[] args) {
        String kafkaServers = "localhost:9092"; // Local Kafka for testing
        IPLKafkaProducer producer = new IPLKafkaProducer(kafkaServers, "ipl-live-scores");
        
        // Sample ball-by-ball data - Mumbai Indians vs Chennai Super Kings
        IPLBallData sampleBall = new IPLBallData(
            "MI_vs_CSK_2024_Final",
            "Mumbai Indians",
            "Chennai Super Kings", 
            20, // 20th over
            4,  // 4th ball
            "Rohit Sharma",
            "Deepak Chahar",
            6, // Six runs
            false, // No wicket
            "SIX! Rohit ने Chahar को stands में भेज दिया!",
            185, // Mumbai's total score
            8,   // Wickets lost
            System.currentTimeMillis()
        );
        
        // Send sample data
        producer.publishBallByBallUpdate(sampleBall);
        
        // Sample milestone - Rohit's fifty
        IPLMilestoneEvent fifty = new IPLMilestoneEvent(
            "MI_vs_CSK_2024_Final",
            "Rohit Sharma",
            "FIFTY",
            50,
            "28 balls में captain का अर्धशतक!",
            System.currentTimeMillis()
        );
        
        producer.publishMilestoneEvent(fifty);
        
        // Close producer
        producer.close();
    }
}

/**
 * IPL Ball Data Model
 * हर ball की complete information store करने के लिए
 */
class IPLBallData {
    private String matchId;
    private String battingTeam;
    private String bowlingTeam;
    private int over;
    private int ball;
    private String batsman;
    private String bowler;
    private int runs;
    private boolean isWicket;
    private String commentary;
    private int totalRuns;
    private int wicketsDown;
    private long timestamp;
    
    // Constructor
    public IPLBallData(String matchId, String battingTeam, String bowlingTeam,
                      int over, int ball, String batsman, String bowler,
                      int runs, boolean isWicket, String commentary,
                      int totalRuns, int wicketsDown, long timestamp) {
        this.matchId = matchId;
        this.battingTeam = battingTeam;
        this.bowlingTeam = bowlingTeam;
        this.over = over;
        this.ball = ball;
        this.batsman = batsman;
        this.bowler = bowler;
        this.runs = runs;
        this.isWicket = isWicket;
        this.commentary = commentary;
        this.totalRuns = totalRuns;
        this.wicketsDown = wicketsDown;
        this.timestamp = timestamp;
    }
    
    // Getters and Setters
    public String getMatchId() { return matchId; }
    public void setMatchId(String matchId) { this.matchId = matchId; }
    
    public String getBattingTeam() { return battingTeam; }
    public void setBattingTeam(String battingTeam) { this.battingTeam = battingTeam; }
    
    public String getBowlingTeam() { return bowlingTeam; }
    public void setBowlingTeam(String bowlingTeam) { this.bowlingTeam = bowlingTeam; }
    
    public int getOver() { return over; }
    public void setOver(int over) { this.over = over; }
    
    public int getBall() { return ball; }
    public void setBall(int ball) { this.ball = ball; }
    
    public String getBatsman() { return batsman; }
    public void setBatsman(String batsman) { this.batsman = batsman; }
    
    public String getBowler() { return bowler; }
    public void setBowler(String bowler) { this.bowler = bowler; }
    
    public int getRuns() { return runs; }
    public void setRuns(int runs) { this.runs = runs; }
    
    public boolean isWicket() { return isWicket; }
    public void setWicket(boolean wicket) { isWicket = wicket; }
    
    public String getCommentary() { return commentary; }
    public void setCommentary(String commentary) { this.commentary = commentary; }
    
    public int getTotalRuns() { return totalRuns; }
    public void setTotalRuns(int totalRuns) { this.totalRuns = totalRuns; }
    
    public int getWicketsDown() { return wicketsDown; }
    public void setWicketsDown(int wicketsDown) { this.wicketsDown = wicketsDown; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}

/**
 * IPL Milestone Events Model
 * खास moments के लिए - fifty, century, hat-trick, etc.
 */
class IPLMilestoneEvent {
    private String matchId;
    private String playerName;
    private String eventType; // FIFTY, CENTURY, WICKET, HAT_TRICK, etc.
    private int milestone; // 50, 100, etc.
    private String description;
    private long timestamp;
    
    public IPLMilestoneEvent(String matchId, String playerName, String eventType,
                           int milestone, String description, long timestamp) {
        this.matchId = matchId;
        this.playerName = playerName;
        this.eventType = eventType;
        this.milestone = milestone;
        this.description = description;
        this.timestamp = timestamp;
    }
    
    // Getters and Setters
    public String getMatchId() { return matchId; }
    public void setMatchId(String matchId) { this.matchId = matchId; }
    
    public String getPlayerName() { return playerName; }
    public void setPlayerName(String playerName) { this.playerName = playerName; }
    
    public String getEventType() { return eventType; }
    public void setEventType(String eventType) { this.eventType = eventType; }
    
    public int getMilestone() { return milestone; }
    public void setMilestone(int milestone) { this.milestone = milestone; }
    
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    
    public long getTimestamp() { return timestamp; }
    public void setTimestamp(long timestamp) { this.timestamp = timestamp; }
}