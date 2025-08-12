/**
 * IPL Ball-by-Ball Analytics using Apache Flink Windowing
 * यह Flink application IPL के ball-by-ball data पर windowing करके analytics करती है
 * Example: Over-by-over analysis, powerplay statistics, partnership tracking
 */

import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.api.common.functions.MapFunction;
import org.apache.flink.api.common.functions.ReduceFunction;
import org.apache.flink.api.common.serialization.SimpleStringSchema;
import org.apache.flink.api.java.tuple.Tuple2;
import org.apache.flink.api.java.tuple.Tuple3;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction;
import org.apache.flink.streaming.api.windowing.assigners.TumblingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.apache.flink.streaming.api.windowing.time.Time;
import org.apache.flink.streaming.api.windowing.windows.TimeWindow;
import org.apache.flink.streaming.connectors.kafka.FlinkKafkaConsumer;
import org.apache.flink.util.Collector;
import org.apache.flink.shaded.jackson2.com.fasterxml.jackson.databind.ObjectMapper;

import java.time.Duration;
import java.util.*;

public class IPLFlinkWindowingAnalytics {
    
    public static void main(String[] args) throws Exception {
        
        // Flink execution environment setup
        // High throughput configuration for IPL data processing
        final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
        
        // Parallelism configuration for IPL scale
        // IPL matches में बहुत data आता है, इसलिए parallelism बढ़ाना पड़ता है
        env.setParallelism(4); // 4 parallel tasks
        
        // Checkpoint configuration for fault tolerance
        // अगर कोई failure आए तो data loss न हो
        env.enableCheckpointing(5000); // Checkpoint every 5 seconds
        
        // Kafka consumer properties
        Properties kafkaProps = new Properties();
        kafkaProps.setProperty("bootstrap.servers", "localhost:9092");
        kafkaProps.setProperty("group.id", "ipl-analytics-flink");
        kafkaProps.setProperty("auto.offset.reset", "latest");
        
        // Create Kafka source for IPL ball data
        FlinkKafkaConsumer<String> kafkaConsumer = new FlinkKafkaConsumer<>(
            "ipl-live-scores",
            new SimpleStringSchema(),
            kafkaProps
        );
        
        // Parse incoming IPL ball data
        DataStream<IPLBallAnalytics> ballStream = env
            .addSource(kafkaConsumer)
            .map(new IPLBallDataParser())
            .assignTimestampsAndWatermarks(
                WatermarkStrategy
                    .<IPLBallAnalytics>forBoundedOutOfOrderness(Duration.ofSeconds(10))
                    .withTimestampAssigner((event, timestamp) -> event.getEventTime())
            );
        
        // 1. Over-by-Over Analysis using Tumbling Windows
        // हर over का complete analysis करते हैं
        performOverAnalysis(ballStream);
        
        // 2. Powerplay Analysis (First 6 overs)
        // Powerplay में teams का performance track करते हैं
        performPowerplayAnalysis(ballStream);
        
        // 3. Sliding Window Analysis for Run Rate Trends
        // Last 5 overs का run rate trend देखते हैं
        performRunRateTrendAnalysis(ballStream);
        
        // 4. Partnership Analysis using Session Windows
        // Wickets के बीच partnerships को track करते हैं
        performPartnershipAnalysis(ballStream);
        
        // 5. Player Performance Windowing
        // Individual player performance windowing
        performPlayerAnalysis(ballStream);
        
        // Execute the Flink job
        env.execute("IPL Ball-by-Ball Analytics with Windowing");
    }
    
    /**
     * Over-by-Over Analysis using Tumbling Windows
     * हर over की complete statistics निकालते हैं
     */
    private static void performOverAnalysis(DataStream<IPLBallAnalytics> ballStream) {
        
        ballStream
            .keyBy(ball -> ball.getMatchId() + "_" + ball.getOver()) // Key by match and over
            .window(TumblingEventTimeWindows.of(Time.minutes(10))) // 10 minute tumbling window
            .process(new ProcessWindowFunction<IPLBallAnalytics, OverAnalytics, String, TimeWindow>() {
                @Override
                public void process(String key, 
                                  Context context, 
                                  Iterable<IPLBallAnalytics> balls,
                                  Collector<OverAnalytics> out) {
                    
                    int totalRuns = 0;
                    int wickets = 0;
                    int boundaries = 0;
                    int sixes = 0;
                    int dots = 0;
                    int extras = 0;
                    String bowlerName = "";
                    List<String> batsmenNames = new ArrayList<>();
                    
                    // Process all balls in the over
                    for (IPLBallAnalytics ball : balls) {
                        totalRuns += ball.getRuns();
                        
                        if (ball.isWicket()) wickets++;
                        if (ball.getRuns() == 4) boundaries++;
                        if (ball.getRuns() == 6) sixes++;
                        if (ball.getRuns() == 0) dots++;
                        if (ball.isExtra()) extras++;
                        
                        bowlerName = ball.getBowler();
                        if (!batsmenNames.contains(ball.getBatsman())) {
                            batsmenNames.add(ball.getBatsman());
                        }
                    }
                    
                    // Create over analytics
                    OverAnalytics overStats = new OverAnalytics(
                        extractMatchId(key),
                        extractOverNumber(key),
                        totalRuns,
                        wickets,
                        boundaries,
                        sixes,
                        dots,
                        extras,
                        bowlerName,
                        batsmenNames,
                        context.window().getEnd()
                    );
                    
                    out.collect(overStats);
                    
                    // Print over summary
                    System.out.println(String.format(
                        "Over %d Summary: %d runs, %d wickets, %d boundaries, %d sixes - Bowler: %s",
                        extractOverNumber(key), totalRuns, wickets, boundaries, sixes, bowlerName
                    ));
                }
            })
            .print("Over-Analysis");
    }
    
    /**
     * Powerplay Analysis (First 6 overs - 36 balls)
     * Powerplay statistics के लिए custom window
     */
    private static void performPowerplayAnalysis(DataStream<IPLBallAnalytics> ballStream) {
        
        ballStream
            .filter(ball -> ball.getOver() <= 6) // Only powerplay overs
            .keyBy(IPLBallAnalytics::getMatchId)
            .window(TumblingEventTimeWindows.of(Time.minutes(30))) // 30-minute window for full powerplay
            .process(new ProcessWindowFunction<IPLBallAnalytics, PowerplayAnalytics, String, TimeWindow>() {
                @Override
                public void process(String matchId,
                                  Context context,
                                  Iterable<IPLBallAnalytics> balls,
                                  Collector<PowerplayAnalytics> out) {
                    
                    int totalRuns = 0;
                    int wicketsLost = 0;
                    int boundaries = 0;
                    int sixes = 0;
                    int ballsFaced = 0;
                    Set<String> bowlersUsed = new HashSet<>();
                    
                    for (IPLBallAnalytics ball : balls) {
                        totalRuns += ball.getRuns();
                        ballsFaced++;
                        
                        if (ball.isWicket()) wicketsLost++;
                        if (ball.getRuns() >= 4) {
                            if (ball.getRuns() == 4) boundaries++;
                            else if (ball.getRuns() == 6) sixes++;
                        }
                        
                        bowlersUsed.add(ball.getBowler());
                    }
                    
                    // Calculate powerplay run rate
                    double runRate = ballsFaced > 0 ? (totalRuns * 6.0) / ballsFaced : 0.0;
                    
                    PowerplayAnalytics ppStats = new PowerplayAnalytics(
                        matchId,
                        totalRuns,
                        wicketsLost,
                        boundaries,
                        sixes,
                        runRate,
                        bowlersUsed.size(),
                        context.window().getEnd()
                    );
                    
                    out.collect(ppStats);
                    
                    System.out.println(String.format(
                        "Powerplay: %d/%d in %d balls (RR: %.2f) - %d boundaries, %d sixes",
                        totalRuns, wicketsLost, ballsFaced, runRate, boundaries, sixes
                    ));
                }
            })
            .print("Powerplay-Analysis");
    }
    
    /**
     * Sliding Window Analysis for Run Rate Trends
     * Last 5 overs का moving average run rate
     */
    private static void performRunRateTrendAnalysis(DataStream<IPLBallAnalytics> ballStream) {
        
        ballStream
            .keyBy(IPLBallAnalytics::getMatchId)
            .window(SlidingEventTimeWindows.of(Time.minutes(25), Time.minutes(5))) // 25min window, slide every 5min
            .process(new ProcessWindowFunction<IPLBallAnalytics, RunRateTrend, String, TimeWindow>() {
                @Override
                public void process(String matchId,
                                  Context context,
                                  Iterable<IPLBallAnalytics> balls,
                                  Collector<RunRateTrend> out) {
                    
                    Map<Integer, Integer> overRuns = new HashMap<>();
                    int totalRuns = 0;
                    int totalBalls = 0;
                    
                    for (IPLBallAnalytics ball : balls) {
                        totalRuns += ball.getRuns();
                        totalBalls++;
                        
                        overRuns.merge(ball.getOver(), ball.getRuns(), Integer::sum);
                    }
                    
                    // Calculate trend
                    double currentRunRate = totalBalls > 0 ? (totalRuns * 6.0) / totalBalls : 0.0;
                    
                    // Determine trend direction
                    List<Integer> recentOvers = overRuns.entrySet().stream()
                        .sorted(Map.Entry.comparingByKey())
                        .map(Map.Entry::getValue)
                        .collect(java.util.stream.Collectors.toList());
                    
                    String trend = determineTrend(recentOvers);
                    
                    RunRateTrend trendData = new RunRateTrend(
                        matchId,
                        currentRunRate,
                        trend,
                        overRuns.size(),
                        context.window().getEnd()
                    );
                    
                    out.collect(trendData);
                    
                    System.out.println(String.format(
                        "Run Rate Trend: %.2f (Trend: %s) over %d overs",
                        currentRunRate, trend, overRuns.size()
                    ));
                }
            })
            .print("RunRate-Trend");
    }
    
    /**
     * Partnership Analysis using Custom Windowing
     * Wickets के बीच partnerships को track करते हैं
     */
    private static void performPartnershipAnalysis(DataStream<IPLBallAnalytics> ballStream) {
        
        ballStream
            .keyBy(ball -> ball.getMatchId() + "_" + ball.getPartnershipId())
            .window(TumblingEventTimeWindows.of(Time.minutes(15)))
            .process(new ProcessWindowFunction<IPLBallAnalytics, PartnershipAnalytics, String, TimeWindow>() {
                @Override
                public void process(String key,
                                  Context context,
                                  Iterable<IPLBallAnalytics> balls,
                                  Collector<PartnershipAnalytics> out) {
                    
                    int partnershipRuns = 0;
                    int ballsFaced = 0;
                    Set<String> batsmen = new HashSet<>();
                    int boundaries = 0;
                    boolean partnershipEnded = false;
                    
                    for (IPLBallAnalytics ball : balls) {
                        partnershipRuns += ball.getRuns();
                        ballsFaced++;
                        batsmen.add(ball.getBatsman());
                        
                        if (ball.getRuns() >= 4) boundaries++;
                        if (ball.isWicket()) partnershipEnded = true;
                    }
                    
                    if (ballsFaced > 0) {
                        double strikeRate = (partnershipRuns * 100.0) / ballsFaced;
                        
                        PartnershipAnalytics partnership = new PartnershipAnalytics(
                            extractMatchId(key),
                            extractPartnershipId(key),
                            partnershipRuns,
                            ballsFaced,
                            new ArrayList<>(batsmen),
                            strikeRate,
                            boundaries,
                            partnershipEnded,
                            context.window().getEnd()
                        );
                        
                        out.collect(partnership);
                        
                        System.out.println(String.format(
                            "Partnership: %d runs in %d balls (SR: %.1f) - %s",
                            partnershipRuns, ballsFaced, strikeRate, 
                            String.join(" & ", batsmen)
                        ));
                    }
                }
            })
            .print("Partnership-Analysis");
    }
    
    /**
     * Player Performance Analysis with Time Windows
     * Individual player statistics windowing
     */
    private static void performPlayerAnalysis(DataStream<IPLBallAnalytics> ballStream) {
        
        ballStream
            .keyBy(IPLBallAnalytics::getBatsman) // Key by batsman
            .window(TumblingEventTimeWindows.of(Time.hours(1))) // 1-hour windows
            .process(new ProcessWindowFunction<IPLBallAnalytics, PlayerAnalytics, String, TimeWindow>() {
                @Override
                public void process(String playerName,
                                  Context context,
                                  Iterable<IPLBallAnalytics> balls,
                                  Collector<PlayerAnalytics> out) {
                    
                    int runsScored = 0;
                    int ballsFaced = 0;
                    int boundaries = 0;
                    int sixes = 0;
                    int dots = 0;
                    Set<String> bowlersFaced = new HashSet<>();
                    
                    for (IPLBallAnalytics ball : balls) {
                        runsScored += ball.getRuns();
                        ballsFaced++;
                        
                        if (ball.getRuns() == 0) dots++;
                        if (ball.getRuns() == 4) boundaries++;
                        if (ball.getRuns() == 6) sixes++;
                        
                        bowlersFaced.add(ball.getBowler());
                    }
                    
                    if (ballsFaced > 0) {
                        double strikeRate = (runsScored * 100.0) / ballsFaced;
                        double dotBallPercentage = (dots * 100.0) / ballsFaced;
                        
                        PlayerAnalytics playerStats = new PlayerAnalytics(
                            playerName,
                            runsScored,
                            ballsFaced,
                            strikeRate,
                            boundaries,
                            sixes,
                            dots,
                            dotBallPercentage,
                            bowlersFaced.size(),
                            context.window().getEnd()
                        );
                        
                        out.collect(playerStats);
                        
                        System.out.println(String.format(
                            "Player %s: %d runs in %d balls (SR: %.1f) - %d×4, %d×6",
                            playerName, runsScored, ballsFaced, strikeRate, boundaries, sixes
                        ));
                    }
                }
            })
            .print("Player-Analysis");
    }
    
    // Helper methods for key extraction
    private static String extractMatchId(String compositeKey) {
        return compositeKey.split("_")[0] + "_" + compositeKey.split("_")[1] + "_" + compositeKey.split("_")[2];
    }
    
    private static int extractOverNumber(String compositeKey) {
        String[] parts = compositeKey.split("_");
        return Integer.parseInt(parts[parts.length - 1]);
    }
    
    private static String extractPartnershipId(String compositeKey) {
        String[] parts = compositeKey.split("_");
        return parts[parts.length - 1];
    }
    
    private static String determineTrend(List<Integer> recentOvers) {
        if (recentOvers.size() < 2) return "STABLE";
        
        int increasing = 0;
        int decreasing = 0;
        
        for (int i = 1; i < recentOvers.size(); i++) {
            if (recentOvers.get(i) > recentOvers.get(i-1)) increasing++;
            else if (recentOvers.get(i) < recentOvers.get(i-1)) decreasing++;
        }
        
        if (increasing > decreasing) return "INCREASING";
        else if (decreasing > increasing) return "DECREASING";
        else return "STABLE";
    }
}

/**
 * IPL Ball Data Parser
 * Kafka से आने वाले JSON data को parse करता है
 */
class IPLBallDataParser implements MapFunction<String, IPLBallAnalytics> {
    
    private final ObjectMapper objectMapper = new ObjectMapper();
    
    @Override
    public IPLBallAnalytics map(String jsonString) throws Exception {
        // Parse JSON and convert to IPLBallAnalytics
        Map<String, Object> ballData = objectMapper.readValue(jsonString, Map.class);
        
        return new IPLBallAnalytics(
            (String) ballData.get("matchId"),
            (String) ballData.get("battingTeam"),
            (String) ballData.get("bowlingTeam"),
            (Integer) ballData.get("over"),
            (Integer) ballData.get("ball"),
            (String) ballData.get("batsman"),
            (String) ballData.get("bowler"),
            (Integer) ballData.get("runs"),
            (Boolean) ballData.get("isWicket"),
            (Boolean) ballData.getOrDefault("isExtra", false),
            System.currentTimeMillis(),
            generatePartnershipId((String) ballData.get("matchId"), 
                               (Integer) ballData.get("wicketsDown"))
        );
    }
    
    private String generatePartnershipId(String matchId, int wicketsDown) {
        return matchId + "_partnership_" + wicketsDown;
    }
}

/**
 * IPL Ball Analytics Data Model
 * Flink processing के लिए ball data structure
 */
class IPLBallAnalytics {
    private String matchId;
    private String battingTeam;
    private String bowlingTeam;
    private int over;
    private int ball;
    private String batsman;
    private String bowler;
    private int runs;
    private boolean isWicket;
    private boolean isExtra;
    private long eventTime;
    private String partnershipId;
    
    // Constructor
    public IPLBallAnalytics(String matchId, String battingTeam, String bowlingTeam,
                           int over, int ball, String batsman, String bowler,
                           int runs, boolean isWicket, boolean isExtra,
                           long eventTime, String partnershipId) {
        this.matchId = matchId;
        this.battingTeam = battingTeam;
        this.bowlingTeam = bowlingTeam;
        this.over = over;
        this.ball = ball;
        this.batsman = batsman;
        this.bowler = bowler;
        this.runs = runs;
        this.isWicket = isWicket;
        this.isExtra = isExtra;
        this.eventTime = eventTime;
        this.partnershipId = partnershipId;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public String getBattingTeam() { return battingTeam; }
    public String getBowlingTeam() { return bowlingTeam; }
    public int getOver() { return over; }
    public int getBall() { return ball; }
    public String getBatsman() { return batsman; }
    public String getBowler() { return bowler; }
    public int getRuns() { return runs; }
    public boolean isWicket() { return isWicket; }
    public boolean isExtra() { return isExtra; }
    public long getEventTime() { return eventTime; }
    public String getPartnershipId() { return partnershipId; }
}

/**
 * Over Analytics Result Model
 * हर over के results के लिए
 */
class OverAnalytics {
    private String matchId;
    private int overNumber;
    private int totalRuns;
    private int wickets;
    private int boundaries;
    private int sixes;
    private int dots;
    private int extras;
    private String bowler;
    private List<String> batsmen;
    private long windowEnd;
    
    public OverAnalytics(String matchId, int overNumber, int totalRuns, int wickets,
                        int boundaries, int sixes, int dots, int extras,
                        String bowler, List<String> batsmen, long windowEnd) {
        this.matchId = matchId;
        this.overNumber = overNumber;
        this.totalRuns = totalRuns;
        this.wickets = wickets;
        this.boundaries = boundaries;
        this.sixes = sixes;
        this.dots = dots;
        this.extras = extras;
        this.bowler = bowler;
        this.batsmen = batsmen;
        this.windowEnd = windowEnd;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public int getOverNumber() { return overNumber; }
    public int getTotalRuns() { return totalRuns; }
    public int getWickets() { return wickets; }
    public int getBoundaries() { return boundaries; }
    public int getSixes() { return sixes; }
    public int getDots() { return dots; }
    public int getExtras() { return extras; }
    public String getBowler() { return bowler; }
    public List<String> getBatsmen() { return batsmen; }
    public long getWindowEnd() { return windowEnd; }
}

/**
 * Powerplay Analytics Result Model
 * Powerplay statistics के लिए
 */
class PowerplayAnalytics {
    private String matchId;
    private int totalRuns;
    private int wicketsLost;
    private int boundaries;
    private int sixes;
    private double runRate;
    private int bowlersUsed;
    private long windowEnd;
    
    public PowerplayAnalytics(String matchId, int totalRuns, int wicketsLost,
                            int boundaries, int sixes, double runRate,
                            int bowlersUsed, long windowEnd) {
        this.matchId = matchId;
        this.totalRuns = totalRuns;
        this.wicketsLost = wicketsLost;
        this.boundaries = boundaries;
        this.sixes = sixes;
        this.runRate = runRate;
        this.bowlersUsed = bowlersUsed;
        this.windowEnd = windowEnd;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public int getTotalRuns() { return totalRuns; }
    public int getWicketsLost() { return wicketsLost; }
    public int getBoundaries() { return boundaries; }
    public int getSixes() { return sixes; }
    public double getRunRate() { return runRate; }
    public int getBowlersUsed() { return bowlersUsed; }
    public long getWindowEnd() { return windowEnd; }
}

/**
 * Run Rate Trend Model
 * Run rate के trends के लिए
 */
class RunRateTrend {
    private String matchId;
    private double currentRunRate;
    private String trend;
    private int oversAnalyzed;
    private long windowEnd;
    
    public RunRateTrend(String matchId, double currentRunRate, String trend,
                       int oversAnalyzed, long windowEnd) {
        this.matchId = matchId;
        this.currentRunRate = currentRunRate;
        this.trend = trend;
        this.oversAnalyzed = oversAnalyzed;
        this.windowEnd = windowEnd;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public double getCurrentRunRate() { return currentRunRate; }
    public String getTrend() { return trend; }
    public int getOversAnalyzed() { return oversAnalyzed; }
    public long getWindowEnd() { return windowEnd; }
}

/**
 * Partnership Analytics Model
 * Partnership statistics के लिए
 */
class PartnershipAnalytics {
    private String matchId;
    private String partnershipId;
    private int runs;
    private int balls;
    private List<String> batsmen;
    private double strikeRate;
    private int boundaries;
    private boolean ended;
    private long windowEnd;
    
    public PartnershipAnalytics(String matchId, String partnershipId, int runs, int balls,
                               List<String> batsmen, double strikeRate, int boundaries,
                               boolean ended, long windowEnd) {
        this.matchId = matchId;
        this.partnershipId = partnershipId;
        this.runs = runs;
        this.balls = balls;
        this.batsmen = batsmen;
        this.strikeRate = strikeRate;
        this.boundaries = boundaries;
        this.ended = ended;
        this.windowEnd = windowEnd;
    }
    
    // Getters
    public String getMatchId() { return matchId; }
    public String getPartnershipId() { return partnershipId; }
    public int getRuns() { return runs; }
    public int getBalls() { return balls; }
    public List<String> getBatsmen() { return batsmen; }
    public double getStrikeRate() { return strikeRate; }
    public int getBoundaries() { return boundaries; }
    public boolean isEnded() { return ended; }
    public long getWindowEnd() { return windowEnd; }
}

/**
 * Player Analytics Model
 * Individual player performance के लिए
 */
class PlayerAnalytics {
    private String playerName;
    private int runsScored;
    private int ballsFaced;
    private double strikeRate;
    private int boundaries;
    private int sixes;
    private int dots;
    private double dotBallPercentage;
    private int bowlersFaced;
    private long windowEnd;
    
    public PlayerAnalytics(String playerName, int runsScored, int ballsFaced,
                          double strikeRate, int boundaries, int sixes, int dots,
                          double dotBallPercentage, int bowlersFaced, long windowEnd) {
        this.playerName = playerName;
        this.runsScored = runsScored;
        this.ballsFaced = ballsFaced;
        this.strikeRate = strikeRate;
        this.boundaries = boundaries;
        this.sixes = sixes;
        this.dots = dots;
        this.dotBallPercentage = dotBallPercentage;
        this.bowlersFaced = bowlersFaced;
        this.windowEnd = windowEnd;
    }
    
    // Getters
    public String getPlayerName() { return playerName; }
    public int getRunsScored() { return runsScored; }
    public int getBallsFaced() { return ballsFaced; }
    public double getStrikeRate() { return strikeRate; }
    public int getBoundaries() { return boundaries; }
    public int getSixes() { return sixes; }
    public int getDots() { return dots; }
    public double getDotBallPercentage() { return dotBallPercentage; }
    public int getBowlersFaced() { return bowlersFaced; }
    public long getWindowEnd() { return windowEnd; }
}