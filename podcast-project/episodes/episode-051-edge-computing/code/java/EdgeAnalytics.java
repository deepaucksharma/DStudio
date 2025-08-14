package com.mumbai.edge.analytics;

import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;
import java.time.LocalDateTime;
import java.time.Duration;
import java.util.stream.Collectors;
import java.util.logging.Logger;
import java.util.logging.Level;
import java.util.function.Function;

/**
 * Edge Analytics Engine - एज पर रियल-टाइम एनालिटिक्स
 * Mumbai Dabba delivery system की तरह - efficient और real-time data processing
 * 
 * Real-world inspired by Apache Kafka Streams, Amazon Kinesis Analytics
 * Use cases: IoT sensor analytics, traffic monitoring, financial fraud detection
 * Cost: Edge analytics ₹2 vs Cloud analytics ₹15 per GB processed
 * 
 * @author Mumbai Tech Team
 * @version 2.0.0
 * @since 2024
 */
public class EdgeAnalytics {
    
    private static final Logger LOGGER = Logger.getLogger(EdgeAnalytics.class.getName());
    
    // Configuration constants
    private static final int DEFAULT_WINDOW_SIZE_SECONDS = 60;
    private static final int DEFAULT_BATCH_SIZE = 100;
    private static final int MAX_MEMORY_WINDOWS = 1000;
    private static final long CLEANUP_INTERVAL_MS = 30000;
    
    // Service identification
    private final String analyticsId;
    private final String location;
    
    // Data processing components
    private final ExecutorService processingPool;
    private final ScheduledExecutorService scheduler;
    private final Map<String, DataStream> dataStreams;
    private final Map<String, AnalyticsRule> rules;
    private final Map<String, WindowedMetrics> windowedData;
    
    // Performance और monitoring
    private final AtomicLong totalEventsProcessed;
    private final AtomicLong totalAnomaliesDetected;
    private final AtomicLong totalAlertsGenerated;
    private final Map<String, StreamMetrics> streamMetrics;
    
    // Mumbai-specific configuration
    private final MumbaiAnalyticsConfiguration mumbaiConfig;
    private volatile boolean running;
    
    /**
     * Data event representation
     */
    public static class DataEvent {
        private final String eventId;
        private final String streamId;
        private final String source;
        private final Map<String, Object> data;
        private final LocalDateTime timestamp;
        private final EventType type;
        private final double value;
        
        public enum EventType {
            SENSOR_READING("सेंसर_रीडिंग"),
            TRANSACTION("लेन-देन"),
            USER_ACTION("उपयोगकर्ता_कार्य"),
            SYSTEM_METRIC("सिस्टम_मेट्रिक"),
            ALERT("अलर्ट");
            
            private final String hindiName;
            
            EventType(String hindiName) {
                this.hindiName = hindiName;
            }
            
            public String getHindiName() {
                return hindiName;
            }
        }
        
        public DataEvent(String eventId, String streamId, String source, 
                        Map<String, Object> data, EventType type, double value) {
            this.eventId = eventId;
            this.streamId = streamId;
            this.source = source;
            this.data = data != null ? new HashMap<>(data) : new HashMap<>();
            this.timestamp = LocalDateTime.now();
            this.type = type;
            this.value = value;
        }
        
        // Getters
        public String getEventId() { return eventId; }
        public String getStreamId() { return streamId; }
        public String getSource() { return source; }
        public Map<String, Object> getData() { return new HashMap<>(data); }
        public LocalDateTime getTimestamp() { return timestamp; }
        public EventType getType() { return type; }
        public double getValue() { return value; }
    }
    
    /**
     * Data stream configuration
     */
    public static class DataStream {
        private final String streamId;
        private final String description;
        private final int windowSizeSeconds;
        private final int maxEventsPerWindow;
        private final Queue<DataEvent> eventBuffer;
        private final AtomicLong eventCount;
        private final LocalDateTime createdTime;
        
        public DataStream(String streamId, String description, 
                         int windowSizeSeconds, int maxEventsPerWindow) {
            this.streamId = streamId;
            this.description = description;
            this.windowSizeSeconds = windowSizeSeconds;
            this.maxEventsPerWindow = maxEventsPerWindow;
            this.eventBuffer = new ConcurrentLinkedQueue<>();
            this.eventCount = new AtomicLong(0);
            this.createdTime = LocalDateTime.now();
        }
        
        public void addEvent(DataEvent event) {
            eventBuffer.offer(event);
            eventCount.incrementAndGet();
            
            // Remove old events to maintain window size
            while (eventBuffer.size() > maxEventsPerWindow) {
                eventBuffer.poll();
            }
        }
        
        public List<DataEvent> getRecentEvents(int limit) {
            return eventBuffer.stream()
                .limit(limit)
                .collect(Collectors.toList());
        }
        
        // Getters
        public String getStreamId() { return streamId; }
        public String getDescription() { return description; }
        public int getWindowSizeSeconds() { return windowSizeSeconds; }
        public long getEventCount() { return eventCount.get(); }
        public int getCurrentBufferSize() { return eventBuffer.size(); }
        public LocalDateTime getCreatedTime() { return createdTime; }
    }
    
    /**
     * Analytics rule for pattern detection
     */
    public static class AnalyticsRule {
        private final String ruleId;
        private final String streamId;
        private final String condition;
        private final RuleType type;
        private final Map<String, Object> parameters;
        private final Function<List<DataEvent>, Boolean> matcher;
        private final AtomicLong matchCount;
        
        public enum RuleType {
            THRESHOLD("सीमा"),
            PATTERN("पैटर्न"),
            ANOMALY("विसंगति"),
            FREQUENCY("आवृत्ति");
            
            private final String hindiName;
            
            RuleType(String hindiName) {
                this.hindiName = hindiName;
            }
            
            public String getHindiName() {
                return hindiName;
            }
        }
        
        public AnalyticsRule(String ruleId, String streamId, String condition, 
                           RuleType type, Map<String, Object> parameters,
                           Function<List<DataEvent>, Boolean> matcher) {
            this.ruleId = ruleId;
            this.streamId = streamId;
            this.condition = condition;
            this.type = type;
            this.parameters = parameters != null ? new HashMap<>(parameters) : new HashMap<>();
            this.matcher = matcher;
            this.matchCount = new AtomicLong(0);
        }
        
        public boolean evaluate(List<DataEvent> events) {
            boolean result = matcher.apply(events);
            if (result) {
                matchCount.incrementAndGet();
            }
            return result;
        }
        
        // Getters
        public String getRuleId() { return ruleId; }
        public String getStreamId() { return streamId; }
        public String getCondition() { return condition; }
        public RuleType getType() { return type; }
        public Map<String, Object> getParameters() { return new HashMap<>(parameters); }
        public long getMatchCount() { return matchCount.get(); }
    }
    
    /**
     * Windowed metrics for time-based analysis
     */
    public static class WindowedMetrics {
        private final String windowId;
        private final int windowSizeSeconds;
        private final Map<LocalDateTime, WindowData> windows;
        private final AtomicReference<WindowData> currentWindow;
        
        public static class WindowData {
            private final LocalDateTime windowStart;
            private final List<DataEvent> events;
            private final Map<String, Double> aggregations;
            private final AtomicLong eventCount;
            
            public WindowData(LocalDateTime windowStart) {
                this.windowStart = windowStart;
                this.events = new ArrayList<>();
                this.aggregations = new ConcurrentHashMap<>();
                this.eventCount = new AtomicLong(0);
            }
            
            public void addEvent(DataEvent event) {
                synchronized (events) {
                    events.add(event);
                    eventCount.incrementAndGet();
                    updateAggregations(event);
                }
            }
            
            private void updateAggregations(DataEvent event) {
                // Update various aggregations
                aggregations.merge("sum", event.getValue(), Double::sum);
                aggregations.merge("count", 1.0, Double::sum);
                aggregations.put("avg", aggregations.get("sum") / aggregations.get("count"));
                
                // Update min/max
                aggregations.merge("min", event.getValue(), Double::min);
                aggregations.merge("max", event.getValue(), Double::max);
            }
            
            // Getters
            public LocalDateTime getWindowStart() { return windowStart; }
            public List<DataEvent> getEvents() { return new ArrayList<>(events); }
            public Map<String, Double> getAggregations() { return new HashMap<>(aggregations); }
            public long getEventCount() { return eventCount.get(); }
        }
        
        public WindowedMetrics(String windowId, int windowSizeSeconds) {
            this.windowId = windowId;
            this.windowSizeSeconds = windowSizeSeconds;
            this.windows = new ConcurrentHashMap<>();
            this.currentWindow = new AtomicReference<>(createNewWindow());
        }
        
        public void addEvent(DataEvent event) {
            WindowData window = getCurrentWindow();
            window.addEvent(event);
        }
        
        public WindowData getCurrentWindow() {
            WindowData window = currentWindow.get();
            LocalDateTime now = LocalDateTime.now();
            
            // Check if we need a new window
            if (Duration.between(window.getWindowStart(), now).getSeconds() >= windowSizeSeconds) {
                WindowData newWindow = createNewWindow();
                if (currentWindow.compareAndSet(window, newWindow)) {
                    windows.put(window.getWindowStart(), window);
                    // Clean up old windows
                    cleanupOldWindows();
                }
                return newWindow;
            }
            
            return window;
        }
        
        private WindowData createNewWindow() {
            return new WindowData(LocalDateTime.now());
        }
        
        private void cleanupOldWindows() {
            LocalDateTime cutoff = LocalDateTime.now().minusSeconds(windowSizeSeconds * MAX_MEMORY_WINDOWS);
            windows.entrySet().removeIf(entry -> entry.getKey().isBefore(cutoff));
        }
        
        public List<WindowData> getRecentWindows(int limit) {
            return windows.values().stream()
                .sorted((w1, w2) -> w2.getWindowStart().compareTo(w1.getWindowStart()))
                .limit(limit)
                .collect(Collectors.toList());
        }
        
        // Getters
        public String getWindowId() { return windowId; }
        public int getWindowSizeSeconds() { return windowSizeSeconds; }
        public int getActiveWindowsCount() { return windows.size(); }
    }
    
    /**
     * Stream performance metrics
     */
    public static class StreamMetrics {
        private final AtomicLong eventsProcessed = new AtomicLong(0);
        private final AtomicLong rulesTriggered = new AtomicLong(0);
        private final AtomicLong processingErrors = new AtomicLong(0);
        private final AtomicLong totalProcessingTimeMs = new AtomicLong(0);
        private final Queue<Long> recentProcessingTimes = new ConcurrentLinkedQueue<>();
        
        public void recordEvent(long processingTimeMs) {
            eventsProcessed.incrementAndGet();
            totalProcessingTimeMs.addAndGet(processingTimeMs);
            
            recentProcessingTimes.offer(processingTimeMs);
            while (recentProcessingTimes.size() > 100) {
                recentProcessingTimes.poll();
            }
        }
        
        public void recordRuleTriggered() {
            rulesTriggered.incrementAndGet();
        }
        
        public void recordError() {
            processingErrors.incrementAndGet();
        }
        
        public long getEventsProcessed() { return eventsProcessed.get(); }
        public long getRulesTriggered() { return rulesTriggered.get(); }
        public long getProcessingErrors() { return processingErrors.get(); }
        
        public double getAverageProcessingTimeMs() {
            long events = eventsProcessed.get();
            return events > 0 ? (double) totalProcessingTimeMs.get() / events : 0.0;
        }
        
        public double getRecentAverageProcessingTimeMs() {
            if (recentProcessingTimes.isEmpty()) {
                return 0.0;
            }
            return recentProcessingTimes.stream()
                .mapToLong(Long::longValue)
                .average()
                .orElse(0.0);
        }
        
        public double getErrorRate() {
            long total = eventsProcessed.get();
            return total > 0 ? (double) processingErrors.get() / total * 100.0 : 0.0;
        }
    }
    
    /**
     * Mumbai-specific analytics configuration
     */
    public static class MumbaiAnalyticsConfiguration {
        private final Map<String, Object> config = new HashMap<>();
        
        public MumbaiAnalyticsConfiguration() {
            // Mumbai के business patterns के लिए configuration
            config.put("business_hours_start", 9);
            config.put("business_hours_end", 21);    // Till 9 PM for Mumbai
            config.put("peak_traffic_hours", Arrays.asList(8, 9, 19, 20, 21));
            config.put("monsoon_alert_threshold", 50.0);  // mm rainfall
            
            // Local Mumbai preferences
            config.put("local_currency", "INR");
            config.put("timezone", "Asia/Kolkata");
            config.put("language", "Hindi");
            
            // Performance thresholds for Mumbai conditions
            config.put("high_latency_threshold_ms", 1000);
            config.put("anomaly_detection_sensitivity", 0.8);
            config.put("alert_cooldown_minutes", 5);
        }
        
        public Object get(String key) {
            return config.get(key);
        }
        
        public void set(String key, Object value) {
            config.put(key, value);
        }
        
        public boolean isBusinessHours() {
            int currentHour = LocalDateTime.now().getHour();
            int startHour = (Integer) config.get("business_hours_start");
            int endHour = (Integer) config.get("business_hours_end");
            return currentHour >= startHour && currentHour <= endHour;
        }
        
        public boolean isPeakTrafficHour() {
            int currentHour = LocalDateTime.now().getHour();
            @SuppressWarnings("unchecked")
            List<Integer> peakHours = (List<Integer>) config.get("peak_traffic_hours");
            return peakHours.contains(currentHour);
        }
        
        public boolean shouldTriggerMonsoonAlert(double rainfallMm) {
            double threshold = (Double) config.get("monsoon_alert_threshold");
            return rainfallMm > threshold;
        }
    }
    
    /**
     * Constructor for Mumbai Edge Analytics
     */
    public EdgeAnalytics(String analyticsId, String location, int threadPoolSize) {
        this.analyticsId = analyticsId;
        this.location = location;
        
        // Initialize processing components
        this.processingPool = Executors.newFixedThreadPool(threadPoolSize);
        this.scheduler = Executors.newScheduledThreadPool(2);
        this.dataStreams = new ConcurrentHashMap<>();
        this.rules = new ConcurrentHashMap<>();
        this.windowedData = new ConcurrentHashMap<>();
        
        // Initialize metrics
        this.totalEventsProcessed = new AtomicLong(0);
        this.totalAnomaliesDetected = new AtomicLong(0);
        this.totalAlertsGenerated = new AtomicLong(0);
        this.streamMetrics = new ConcurrentHashMap<>();
        
        // Mumbai configuration
        this.mumbaiConfig = new MumbaiAnalyticsConfiguration();
        this.running = false;
        
        LOGGER.info(String.format("Mumbai Edge Analytics initialized: %s @ %s", 
                                  analyticsId, location));
    }
    
    /**
     * Analytics service start करना
     */
    public void start() {
        if (running) {
            LOGGER.warning("Analytics service already running");
            return;
        }
        
        running = true;
        
        // Start cleanup scheduler
        startMaintenanceTasks();
        
        // Register default Mumbai analytics rules
        registerDefaultMumbaiRules();
        
        LOGGER.info("Mumbai Edge Analytics started: " + analyticsId);
    }
    
    /**
     * Analytics service stop करना
     */
    public void stop() {
        if (!running) {
            return;
        }
        
        running = false;
        LOGGER.info("Stopping Mumbai Edge Analytics...");
        
        // Shutdown executors
        scheduler.shutdown();
        processingPool.shutdown();
        
        try {
            if (!processingPool.awaitTermination(30, TimeUnit.SECONDS)) {
                processingPool.shutdownNow();
            }
            if (!scheduler.awaitTermination(10, TimeUnit.SECONDS)) {
                scheduler.shutdownNow();
            }
        } catch (InterruptedException e) {
            processingPool.shutdownNow();
            scheduler.shutdownNow();
            Thread.currentThread().interrupt();
        }
        
        LOGGER.info("Mumbai Edge Analytics stopped");
    }
    
    /**
     * Data stream create करना
     */
    public boolean createStream(String streamId, String description, 
                              int windowSizeSeconds, int maxEventsPerWindow) {
        if (dataStreams.containsKey(streamId)) {
            LOGGER.warning("Stream already exists: " + streamId);
            return false;
        }
        
        DataStream stream = new DataStream(streamId, description, 
                                         windowSizeSeconds, maxEventsPerWindow);
        dataStreams.put(streamId, stream);
        streamMetrics.put(streamId, new StreamMetrics());
        
        // Create windowed metrics for this stream
        WindowedMetrics windowed = new WindowedMetrics(streamId + "_windows", windowSizeSeconds);
        windowedData.put(streamId, windowed);
        
        LOGGER.info(String.format("Stream created: %s - %s", streamId, description));
        return true;
    }
    
    /**
     * Analytics rule add करना
     */
    public boolean addRule(String ruleId, String streamId, String condition, 
                          AnalyticsRule.RuleType type, Map<String, Object> parameters,
                          Function<List<DataEvent>, Boolean> matcher) {
        if (!dataStreams.containsKey(streamId)) {
            LOGGER.warning("Stream not found for rule: " + streamId);
            return false;
        }
        
        if (rules.containsKey(ruleId)) {
            LOGGER.warning("Rule already exists: " + ruleId);
            return false;
        }
        
        AnalyticsRule rule = new AnalyticsRule(ruleId, streamId, condition, type, parameters, matcher);
        rules.put(ruleId, rule);
        
        LOGGER.info(String.format("Rule added: %s for stream %s", ruleId, streamId));
        return true;
    }
    
    /**
     * Event process करना
     */
    public void processEvent(DataEvent event) {
        if (!running) {
            LOGGER.warning("Analytics service not running");
            return;
        }
        
        long startTime = System.currentTimeMillis();
        
        try {
            // Add event to stream
            DataStream stream = dataStreams.get(event.getStreamId());
            if (stream == null) {
                LOGGER.warning("Stream not found: " + event.getStreamId());
                return;
            }
            
            stream.addEvent(event);
            
            // Add to windowed data
            WindowedMetrics windowed = windowedData.get(event.getStreamId());
            if (windowed != null) {
                windowed.addEvent(event);
            }
            
            // Process rules asynchronously
            processingPool.submit(() -> evaluateRules(event));
            
            // Update metrics
            totalEventsProcessed.incrementAndGet();
            StreamMetrics metrics = streamMetrics.get(event.getStreamId());
            if (metrics != null) {
                metrics.recordEvent(System.currentTimeMillis() - startTime);
            }
            
        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "Error processing event: " + event.getEventId(), e);
            StreamMetrics metrics = streamMetrics.get(event.getStreamId());
            if (metrics != null) {
                metrics.recordError();
            }
        }
    }
    
    /**
     * Batch events process करना
     */
    public void processBatch(List<DataEvent> events) {
        if (events == null || events.isEmpty()) {
            return;
        }
        
        LOGGER.fine("Processing batch of " + events.size() + " events");
        
        // Process events in parallel
        events.parallelStream().forEach(this::processEvent);
    }
    
    /**
     * Stream analytics get करना
     */
    public Map<String, Object> getStreamAnalytics(String streamId) {
        DataStream stream = dataStreams.get(streamId);
        if (stream == null) {
            return null;
        }
        
        StreamMetrics metrics = streamMetrics.get(streamId);
        WindowedMetrics windowed = windowedData.get(streamId);
        
        Map<String, Object> analytics = new HashMap<>();
        
        // Basic stream info
        analytics.put("stream_id", streamId);
        analytics.put("description", stream.getDescription());
        analytics.put("created_time", stream.getCreatedTime());
        
        // Event statistics
        analytics.put("total_events", stream.getEventCount());
        analytics.put("current_buffer_size", stream.getCurrentBufferSize());
        analytics.put("window_size_seconds", stream.getWindowSizeSeconds());
        
        // Processing metrics
        if (metrics != null) {
            analytics.put("events_processed", metrics.getEventsProcessed());
            analytics.put("rules_triggered", metrics.getRulesTriggered());
            analytics.put("processing_errors", metrics.getProcessingErrors());
            analytics.put("avg_processing_time_ms", metrics.getAverageProcessingTimeMs());
            analytics.put("error_rate_percent", metrics.getErrorRate());
        }
        
        // Windowed data
        if (windowed != null) {
            WindowedMetrics.WindowData currentWindow = windowed.getCurrentWindow();
            analytics.put("current_window_events", currentWindow.getEventCount());
            analytics.put("current_window_aggregations", currentWindow.getAggregations());
            analytics.put("active_windows_count", windowed.getActiveWindowsCount());
            
            // Recent windows summary
            List<WindowedMetrics.WindowData> recentWindows = windowed.getRecentWindows(5);
            List<Map<String, Object>> windowsSummary = recentWindows.stream()
                .map(w -> Map.of(
                    "window_start", w.getWindowStart(),
                    "event_count", w.getEventCount(),
                    "aggregations", w.getAggregations()
                ))
                .collect(Collectors.toList());
            analytics.put("recent_windows", windowsSummary);
        }
        
        return analytics;
    }
    
    /**
     * Overall service metrics get करना
     */
    public Map<String, Object> getServiceMetrics() {
        Map<String, Object> metrics = new HashMap<>();
        
        // Service info
        metrics.put("analytics_id", analyticsId);
        metrics.put("location", location);
        metrics.put("running", running);
        
        // Overall statistics
        metrics.put("total_events_processed", totalEventsProcessed.get());
        metrics.put("total_anomalies_detected", totalAnomaliesDetected.get());
        metrics.put("total_alerts_generated", totalAlertsGenerated.get());
        
        // Streams summary
        metrics.put("total_streams", dataStreams.size());
        metrics.put("total_rules", rules.size());
        
        // Stream metrics summary
        Map<String, Object> streamsMetrics = new HashMap<>();
        for (Map.Entry<String, StreamMetrics> entry : streamMetrics.entrySet()) {
            StreamMetrics sm = entry.getValue();
            streamsMetrics.put(entry.getKey(), Map.of(
                "events_processed", sm.getEventsProcessed(),
                "avg_processing_time_ms", sm.getAverageProcessingTimeMs(),
                "error_rate_percent", sm.getErrorRate()
            ));
        }
        metrics.put("streams_performance", streamsMetrics);
        
        // Mumbai-specific metrics
        metrics.put("mumbai_config", Map.of(
            "business_hours", mumbaiConfig.isBusinessHours(),
            "peak_traffic_hour", mumbaiConfig.isPeakTrafficHour()
        ));
        
        return metrics;
    }
    
    /**
     * Rules evaluate करना
     */
    private void evaluateRules(DataEvent event) {
        try {
            DataStream stream = dataStreams.get(event.getStreamId());
            if (stream == null) {
                return;
            }
            
            // Get recent events for rule evaluation
            List<DataEvent> recentEvents = stream.getRecentEvents(100);
            
            // Evaluate all rules for this stream
            for (AnalyticsRule rule : rules.values()) {
                if (rule.getStreamId().equals(event.getStreamId())) {
                    try {
                        if (rule.evaluate(recentEvents)) {
                            handleRuleMatch(rule, event, recentEvents);
                        }
                    } catch (Exception e) {
                        LOGGER.log(Level.WARNING, "Rule evaluation error: " + rule.getRuleId(), e);
                    }
                }
            }
            
        } catch (Exception e) {
            LOGGER.log(Level.WARNING, "Error in rule evaluation", e);
        }
    }
    
    /**
     * Rule match handle करना
     */
    private void handleRuleMatch(AnalyticsRule rule, DataEvent triggerEvent, 
                                List<DataEvent> recentEvents) {
        StreamMetrics metrics = streamMetrics.get(rule.getStreamId());
        if (metrics != null) {
            metrics.recordRuleTriggered();
        }
        
        // Generate alert based on rule type
        switch (rule.getType()) {
            case ANOMALY:
                totalAnomaliesDetected.incrementAndGet();
                generateAnomalyAlert(rule, triggerEvent);
                break;
            case THRESHOLD:
                generateThresholdAlert(rule, triggerEvent);
                break;
            case PATTERN:
                generatePatternAlert(rule, triggerEvent, recentEvents);
                break;
            case FREQUENCY:
                generateFrequencyAlert(rule, triggerEvent, recentEvents);
                break;
        }
        
        totalAlertsGenerated.incrementAndGet();
        
        LOGGER.info(String.format("Rule triggered: %s (%s) for event %s", 
                   rule.getRuleId(), rule.getType().getHindiName(), triggerEvent.getEventId()));
    }
    
    /**
     * Default Mumbai rules register करना
     */
    private void registerDefaultMumbaiRules() {
        // Mumbai traffic congestion rule
        addRule("mumbai_traffic_congestion", "mumbai_traffic", 
               "Traffic density > 80%",
               AnalyticsRule.RuleType.THRESHOLD,
               Map.of("threshold", 80.0),
               events -> events.stream()
                   .filter(e -> e.getTimestamp().isAfter(LocalDateTime.now().minusMinutes(5)))
                   .anyMatch(e -> e.getValue() > 80.0)
        );
        
        // Mumbai monsoon alert rule
        addRule("mumbai_monsoon_alert", "mumbai_weather",
               "Heavy rainfall detected",
               AnalyticsRule.RuleType.THRESHOLD,
               Map.of("rainfall_threshold", 50.0),
               events -> events.stream()
                   .filter(e -> e.getTimestamp().isAfter(LocalDateTime.now().minusMinutes(10)))
                   .anyMatch(e -> mumbaiConfig.shouldTriggerMonsoonAlert(e.getValue()))
        );
        
        // Mumbai payment fraud detection rule
        addRule("mumbai_payment_anomaly", "mumbai_payments",
               "Unusual payment pattern detected",
               AnalyticsRule.RuleType.ANOMALY,
               Map.of("amount_threshold", 100000.0, "frequency_threshold", 10),
               events -> {
                   List<DataEvent> recentPayments = events.stream()
                       .filter(e -> e.getTimestamp().isAfter(LocalDateTime.now().minusMinutes(5)))
                       .collect(Collectors.toList());
                   
                   // Check for high-value transactions
                   boolean highValueDetected = recentPayments.stream()
                       .anyMatch(e -> e.getValue() > 100000.0);
                   
                   // Check for high frequency
                   boolean highFrequencyDetected = recentPayments.size() > 10;
                   
                   return highValueDetected || highFrequencyDetected;
               }
        );
        
        LOGGER.info("Default Mumbai analytics rules registered");
    }
    
    /**
     * Maintenance tasks start करना
     */
    private void startMaintenanceTasks() {
        // Cleanup old data every 30 seconds
        scheduler.scheduleAtFixedRate(() -> {
            try {
                performCleanup();
            } catch (Exception e) {
                LOGGER.log(Level.WARNING, "Cleanup task error", e);
            }
        }, CLEANUP_INTERVAL_MS, CLEANUP_INTERVAL_MS, TimeUnit.MILLISECONDS);
    }
    
    /**
     * Cleanup old data
     */
    private void performCleanup() {
        // Cleanup would involve removing old windowed data
        // This is handled automatically in WindowedMetrics.cleanupOldWindows()
        LOGGER.fine("Performing analytics data cleanup");
    }
    
    // Alert generation methods
    private void generateAnomalyAlert(AnalyticsRule rule, DataEvent triggerEvent) {
        LOGGER.info(String.format("🚨 ANOMALY DETECTED: %s - Event: %s, Value: %.2f", 
                   rule.getCondition(), triggerEvent.getEventId(), triggerEvent.getValue()));
    }
    
    private void generateThresholdAlert(AnalyticsRule rule, DataEvent triggerEvent) {
        LOGGER.info(String.format("⚠️ THRESHOLD EXCEEDED: %s - Event: %s, Value: %.2f", 
                   rule.getCondition(), triggerEvent.getEventId(), triggerEvent.getValue()));
    }
    
    private void generatePatternAlert(AnalyticsRule rule, DataEvent triggerEvent, List<DataEvent> events) {
        LOGGER.info(String.format("🔍 PATTERN DETECTED: %s - Event: %s, Pattern Events: %d", 
                   rule.getCondition(), triggerEvent.getEventId(), events.size()));
    }
    
    private void generateFrequencyAlert(AnalyticsRule rule, DataEvent triggerEvent, List<DataEvent> events) {
        LOGGER.info(String.format("📊 FREQUENCY ALERT: %s - Event: %s, Frequency: %d events", 
                   rule.getCondition(), triggerEvent.getEventId(), events.size()));
    }
    
    /**
     * Main method for testing
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("🔬 Mumbai Edge Analytics Engine - Demonstration");
        System.out.println("=" + "=".repeat(60));
        
        // Initialize analytics engine
        EdgeAnalytics analytics = new EdgeAnalytics(
            "mumbai-edge-analytics-01", "Mumbai Bandra Kurla Complex", 4
        );
        
        try {
            // Start analytics engine
            analytics.start();
            System.out.println("✅ Edge Analytics Engine started");
            
            // Create data streams
            System.out.println("\n📊 Creating Mumbai Data Streams...");
            analytics.createStream("mumbai_traffic", "Mumbai Traffic Monitoring", 60, 1000);
            analytics.createStream("mumbai_weather", "Mumbai Weather Monitoring", 300, 500);
            analytics.createStream("mumbai_payments", "Mumbai Payment Processing", 30, 2000);
            System.out.println("✅ Data streams created");
            
            // Generate sample events
            System.out.println("\n📈 Generating Sample Events...");
            Random random = new Random();
            
            // Traffic events
            for (int i = 0; i < 20; i++) {
                DataEvent trafficEvent = new DataEvent(
                    "traffic_" + i,
                    "mumbai_traffic",
                    "Traffic Sensor " + (i % 5),
                    Map.of(
                        "location", "Bandra-Worli Sea Link",
                        "lane", i % 4,
                        "vehicle_type", i % 2 == 0 ? "car" : "bus"
                    ),
                    DataEvent.EventType.SENSOR_READING,
                    30.0 + random.nextDouble() * 70.0  // 30-100% traffic density
                );
                analytics.processEvent(trafficEvent);
                Thread.sleep(50);
            }
            
            // Weather events
            for (int i = 0; i < 10; i++) {
                DataEvent weatherEvent = new DataEvent(
                    "weather_" + i,
                    "mumbai_weather",
                    "Weather Station Mumbai Central",
                    Map.of(
                        "temperature", 28 + random.nextInt(10),
                        "humidity", 60 + random.nextInt(30),
                        "pressure", 1010 + random.nextInt(20)
                    ),
                    DataEvent.EventType.SENSOR_READING,
                    random.nextDouble() * 100.0  // Rainfall in mm
                );
                analytics.processEvent(weatherEvent);
                Thread.sleep(100);
            }
            
            // Payment events
            for (int i = 0; i < 15; i++) {
                double amount = i > 10 ? 150000.0 : 1000.0 + random.nextDouble() * 5000.0;
                DataEvent paymentEvent = new DataEvent(
                    "payment_" + i,
                    "mumbai_payments",
                    "Payment Gateway Mumbai",
                    Map.of(
                        "merchant_id", "MUM_MERCHANT_" + (i % 3),
                        "payment_method", i % 2 == 0 ? "UPI" : "Card",
                        "currency", "INR"
                    ),
                    DataEvent.EventType.TRANSACTION,
                    amount
                );
                analytics.processEvent(paymentEvent);
                Thread.sleep(30);
            }
            
            // Wait for processing
            System.out.println("⏳ Processing events...");
            Thread.sleep(3000);
            
            // Display analytics results
            System.out.println("\n📊 Stream Analytics Results:");
            System.out.println("-".repeat(50));
            
            for (String streamId : Arrays.asList("mumbai_traffic", "mumbai_weather", "mumbai_payments")) {
                Map<String, Object> streamAnalytics = analytics.getStreamAnalytics(streamId);
                if (streamAnalytics != null) {
                    System.out.printf("\n🏷️ Stream: %s%n", streamId);
                    System.out.printf("• Total Events: %d%n", streamAnalytics.get("total_events"));
                    System.out.printf("• Current Buffer: %d%n", streamAnalytics.get("current_buffer_size"));
                    System.out.printf("• Events Processed: %d%n", streamAnalytics.get("events_processed"));
                    System.out.printf("• Rules Triggered: %d%n", streamAnalytics.get("rules_triggered"));
                    System.out.printf("• Avg Processing Time: %.2f ms%n", 
                        streamAnalytics.get("avg_processing_time_ms"));
                    System.out.printf("• Error Rate: %.2f%%n", streamAnalytics.get("error_rate_percent"));
                }
            }
            
            // Display service metrics
            System.out.println("\n📈 Service Performance Metrics:");
            System.out.println("-".repeat(40));
            Map<String, Object> serviceMetrics = analytics.getServiceMetrics();
            System.out.printf("Analytics ID: %s%n", serviceMetrics.get("analytics_id"));
            System.out.printf("Location: %s%n", serviceMetrics.get("location"));
            System.out.printf("Total Events Processed: %d%n", serviceMetrics.get("total_events_processed"));
            System.out.printf("Total Anomalies Detected: %d%n", serviceMetrics.get("total_anomalies_detected"));
            System.out.printf("Total Alerts Generated: %d%n", serviceMetrics.get("total_alerts_generated"));
            System.out.printf("Total Streams: %d%n", serviceMetrics.get("total_streams"));
            System.out.printf("Total Rules: %d%n", serviceMetrics.get("total_rules"));
            
            // Mumbai-specific information
            @SuppressWarnings("unchecked")
            Map<String, Object> mumbaiConfig = (Map<String, Object>) serviceMetrics.get("mumbai_config");
            System.out.println("\n🏙️ Mumbai Configuration:");
            System.out.printf("• Business Hours: %s%n", 
                mumbaiConfig.get("business_hours") ? "Yes" : "No");
            System.out.printf("• Peak Traffic Hour: %s%n", 
                mumbaiConfig.get("peak_traffic_hour") ? "Yes" : "No");
            
            // Cost analysis
            System.out.println("\n💰 Cost Analysis:");
            long totalEvents = ((Number) serviceMetrics.get("total_events_processed")).longValue();
            double dataProcessedGB = totalEvents * 0.001; // Assume 1KB per event
            double edgeCost = dataProcessedGB * 2.0;       // ₹2 per GB
            double cloudCost = dataProcessedGB * 15.0;     // ₹15 per GB
            double savings = cloudCost - edgeCost;
            
            System.out.printf("• Data Processed: %.3f GB%n", dataProcessedGB);
            System.out.printf("• Edge Analytics Cost: ₹%.2f%n", edgeCost);
            System.out.printf("• Cloud Analytics Cost: ₹%.2f%n", cloudCost);
            System.out.printf("• Cost Savings: ₹%.2f (%.1f%%)%n", 
                savings, (savings / cloudCost) * 100);
            
            System.out.println("\n🎯 Mumbai Edge Analytics Benefits:");
            System.out.println("• Real-time processing with <100ms latency");
            System.out.println("• Cost savings of 86% compared to cloud analytics");
            System.out.println("• Mumbai-specific rules for traffic and monsoon");
            System.out.println("• Local data processing for privacy compliance");
            System.out.println("• Automatic anomaly detection for fraud prevention");
            
        } finally {
            // Cleanup
            System.out.println("\n🛑 Stopping analytics engine...");
            analytics.stop();
            System.out.println("✅ Mumbai Edge Analytics demonstration completed!");
        }
    }
}