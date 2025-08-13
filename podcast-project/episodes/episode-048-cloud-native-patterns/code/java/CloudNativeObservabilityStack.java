/**
 * Cloud Native Observability Stack
 * क्लाउड नेटिव ऑब्जर्वेबिलिटी स्टैक
 * 
 * Real-world example: Zerodha's trading platform observability
 * Comprehensive observability stack for high-frequency trading systems
 */

package com.zerodha.observability;

import java.util.*;
import java.util.concurrent.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.stream.Collectors;
import io.micrometer.core.instrument.*;
import io.micrometer.prometheus.PrometheusConfig;
import io.micrometer.prometheus.PrometheusMeterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * Metric types for trading system
 */
enum MetricType {
    COUNTER("counter"),
    GAUGE("gauge"),
    HISTOGRAM("histogram"),
    TIMER("timer"),
    SUMMARY("summary");
    
    private final String type;
    
    MetricType(String type) {
        this.type = type;
    }
    
    public String getType() { return type; }
}

/**
 * Log levels with Indian context
 */
enum LogLevel {
    TRACE, DEBUG, INFO, WARN, ERROR, CRITICAL;
}

/**
 * Alert severity levels
 */
enum AlertSeverity {
    LOW(1), MEDIUM(2), HIGH(3), CRITICAL(4);
    
    private final int level;
    
    AlertSeverity(int level) {
        this.level = level;
    }
    
    public int getLevel() { return level; }
}

/**
 * Trading event for observability
 */
class TradingEvent {
    private final String eventId;
    private final String eventType;
    private final String userId;
    private final String symbol;
    private final double quantity;
    private final double price;
    private final Instant timestamp;
    private final Map<String, String> metadata;
    
    public TradingEvent(String eventType, String userId, String symbol, 
                       double quantity, double price) {
        this.eventId = UUID.randomUUID().toString();
        this.eventType = eventType;
        this.userId = userId;
        this.symbol = symbol;
        this.quantity = quantity;
        this.price = price;
        this.timestamp = Instant.now();
        this.metadata = new HashMap<>();
    }
    
    // Getters
    public String getEventId() { return eventId; }
    public String getEventType() { return eventType; }
    public String getUserId() { return userId; }
    public String getSymbol() { return symbol; }
    public double getQuantity() { return quantity; }
    public double getPrice() { return price; }
    public Instant getTimestamp() { return timestamp; }
    public Map<String, String> getMetadata() { return new HashMap<>(metadata); }
    
    public void addMetadata(String key, String value) {
        this.metadata.put(key, value);
    }
}

/**
 * Custom alert definition
 */
class AlertRule {
    private final String ruleName;
    private final String query;
    private final double threshold;
    private final String operator; // gt, lt, eq, ne
    private final Duration evaluationWindow;
    private final AlertSeverity severity;
    private final List<String> notificationChannels;
    private final Map<String, String> labels;
    
    public AlertRule(String ruleName, String query, double threshold, 
                    String operator, Duration evaluationWindow, 
                    AlertSeverity severity, List<String> notificationChannels) {
        this.ruleName = ruleName;
        this.query = query;
        this.threshold = threshold;
        this.operator = operator;
        this.evaluationWindow = evaluationWindow;
        this.severity = severity;
        this.notificationChannels = new ArrayList<>(notificationChannels);
        this.labels = new HashMap<>();
    }
    
    // Getters
    public String getRuleName() { return ruleName; }
    public String getQuery() { return query; }
    public double getThreshold() { return threshold; }
    public String getOperator() { return operator; }
    public Duration getEvaluationWindow() { return evaluationWindow; }
    public AlertSeverity getSeverity() { return severity; }
    public List<String> getNotificationChannels() { return new ArrayList<>(notificationChannels); }
    public Map<String, String> getLabels() { return new HashMap<>(labels); }
    
    public void addLabel(String key, String value) {
        this.labels.put(key, value);
    }
}

/**
 * Distributed trace span
 */
class TraceSpan {
    private final String traceId;
    private final String spanId;
    private final String parentSpanId;
    private final String operationName;
    private final String serviceName;
    private final Instant startTime;
    private Instant endTime;
    private final Map<String, Object> tags;
    private final List<String> logs;
    
    public TraceSpan(String traceId, String operationName, String serviceName) {
        this.traceId = traceId;
        this.spanId = UUID.randomUUID().toString().substring(0, 8);
        this.parentSpanId = null;
        this.operationName = operationName;
        this.serviceName = serviceName;
        this.startTime = Instant.now();
        this.tags = new HashMap<>();
        this.logs = new ArrayList<>();
    }
    
    public TraceSpan(String traceId, String parentSpanId, String operationName, String serviceName) {
        this.traceId = traceId;
        this.spanId = UUID.randomUUID().toString().substring(0, 8);
        this.parentSpanId = parentSpanId;
        this.operationName = operationName;
        this.serviceName = serviceName;
        this.startTime = Instant.now();
        this.tags = new HashMap<>();
        this.logs = new ArrayList<>();
    }
    
    public void setTag(String key, Object value) {
        this.tags.put(key, value);
    }
    
    public void log(String message) {
        String logEntry = String.format("[%s] %s", 
            Instant.now().toString(), message);
        this.logs.add(logEntry);
    }
    
    public void finish() {
        this.endTime = Instant.now();
    }
    
    public Duration getDuration() {
        if (endTime != null) {
            return Duration.between(startTime, endTime);
        }
        return Duration.between(startTime, Instant.now());
    }
    
    // Getters
    public String getTraceId() { return traceId; }
    public String getSpanId() { return spanId; }
    public String getParentSpanId() { return parentSpanId; }
    public String getOperationName() { return operationName; }
    public String getServiceName() { return serviceName; }
    public Instant getStartTime() { return startTime; }
    public Instant getEndTime() { return endTime; }
    public Map<String, Object> getTags() { return new HashMap<>(tags); }
    public List<String> getLogs() { return new ArrayList<>(logs); }
}

/**
 * Zerodha Trading Platform Observability Stack
 * जेरोधा ट्रेडिंग प्लेटफॉर्म ऑब्जर्वेबिलिटी स्टैक
 */
public class CloudNativeObservabilityStack {
    
    private static final Logger logger = LoggerFactory.getLogger(CloudNativeObservabilityStack.class);
    
    private final MeterRegistry meterRegistry;
    private final Map<String, Counter> counters;
    private final Map<String, Gauge> gauges;
    private final Map<String, Timer> timers;
    private final Map<String, DistributionSummary> summaries;
    
    // Tracing
    private final Map<String, TraceSpan> activeSpans;
    private final List<TraceSpan> completedTraces;
    
    // Alerting
    private final List<AlertRule> alertRules;
    private final Map<String, Instant> alertStates;
    
    // Service information
    private final String serviceName;
    private final String serviceVersion;
    private final String environment;
    private final String region;
    
    public CloudNativeObservabilityStack(String serviceName, String serviceVersion, 
                                       String environment, String region) {
        this.serviceName = serviceName;
        this.serviceVersion = serviceVersion;
        this.environment = environment;
        this.region = region;
        
        // Initialize Prometheus metrics registry
        this.meterRegistry = new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
        this.counters = new ConcurrentHashMap<>();
        this.gauges = new ConcurrentHashMap<>();
        this.timers = new ConcurrentHashMap<>();
        this.summaries = new ConcurrentHashMap<>();
        
        // Initialize tracing
        this.activeSpans = new ConcurrentHashMap<>();
        this.completedTraces = Collections.synchronizedList(new ArrayList<>());
        
        // Initialize alerting
        this.alertRules = Collections.synchronizedList(new ArrayList<>());
        this.alertStates = new ConcurrentHashMap<>();
        
        setupDefaultMetrics();
        setupDefaultAlerts();
        
        logger.info("🔍 Initialized observability stack for service: {} version: {} in region: {}", 
                   serviceName, serviceVersion, region);
    }
    
    /**
     * Setup default metrics for trading platform
     * ट्रेडिंग प्लेटफॉर्म के लिए डिफ़ॉल्ट मेट्रिक्स सेट करें
     */
    private void setupDefaultMetrics() {
        // Trading-specific counters
        createCounter("trades_total", "Total number of trades executed", 
                     "symbol", "order_type");
        createCounter("orders_total", "Total number of orders placed", 
                     "symbol", "order_type", "status");
        createCounter("market_data_events_total", "Total market data events processed",
                     "symbol", "event_type");
        createCounter("user_sessions_total", "Total user sessions",
                     "platform", "user_type");
        createCounter("api_requests_total", "Total API requests",
                     "endpoint", "method", "status_code");
        
        // Trading-specific timers
        createTimer("order_processing_duration", "Time taken to process orders",
                   "order_type", "symbol");
        createTimer("market_data_latency", "Market data processing latency",
                   "symbol", "feed_type");
        createTimer("database_query_duration", "Database query execution time",
                   "query_type", "table");
        createTimer("external_api_duration", "External API call duration",
                   "provider", "endpoint");
        
        // Trading-specific summaries
        createSummary("order_value_distribution", "Distribution of order values",
                     "symbol", "order_type");
        createSummary("portfolio_value_distribution", "Distribution of portfolio values",
                     "user_type", "segment");
        
        logger.info("📊 Default trading metrics initialized");
    }
    
    /**
     * Setup default alert rules
     * डिफ़ॉल्ट अलर्ट नियम स्थापित करें
     */
    private void setupDefaultAlerts() {
        // High-frequency trading alerts
        AlertRule highLatencyAlert = new AlertRule(
            "high_order_processing_latency",
            "histogram_quantile(0.95, rate(order_processing_duration_seconds_bucket[5m]))",
            0.100, // 100ms
            "gt",
            Duration.ofMinutes(2),
            AlertSeverity.HIGH,
            Arrays.asList("pagerduty", "slack-trading", "sms")
        );
        highLatencyAlert.addLabel("team", "trading");
        highLatencyAlert.addLabel("runbook", "https://wiki.zerodha.com/runbooks/high-latency");
        
        AlertRule highErrorRateAlert = new AlertRule(
            "high_api_error_rate",
            "rate(api_requests_total{status_code!~\"2..\"}[5m]) / rate(api_requests_total[5m])",
            0.05, // 5%
            "gt",
            Duration.ofMinutes(3),
            AlertSeverity.CRITICAL,
            Arrays.asList("pagerduty", "slack-trading", "email-oncall")
        );
        highErrorRateAlert.addLabel("team", "platform");
        
        AlertRule marketDataLagAlert = new AlertRule(
            "market_data_lag",
            "histogram_quantile(0.99, rate(market_data_latency_seconds_bucket[1m]))",
            0.050, // 50ms
            "gt",
            Duration.ofMinutes(1),
            AlertSeverity.CRITICAL,
            Arrays.asList("pagerduty", "slack-market-data")
        );
        marketDataLagAlert.addLabel("team", "market-data");
        marketDataLagAlert.addLabel("severity", "trading-critical");
        
        alertRules.addAll(Arrays.asList(highLatencyAlert, highErrorRateAlert, marketDataLagAlert));
        
        logger.info("⚠️ Default alert rules configured");
    }
    
    /**
     * Create and register a counter metric
     * काउंटर मेट्रिक बनाएं और रजिस्टर करें
     */
    public Counter createCounter(String name, String description, String... tagNames) {
        Counter counter = Counter.builder(name)
            .description(description)
            .tags("service", serviceName, "version", serviceVersion, 
                  "environment", environment, "region", region)
            .register(meterRegistry);
        
        counters.put(name, counter);
        return counter;
    }
    
    /**
     * Create and register a timer metric
     * टाइमर मेट्रिक बनाएं और रजिस्टर करें
     */
    public Timer createTimer(String name, String description, String... tagNames) {
        Timer timer = Timer.builder(name)
            .description(description)
            .tags("service", serviceName, "version", serviceVersion,
                  "environment", environment, "region", region)
            .register(meterRegistry);
        
        timers.put(name, timer);
        return timer;
    }
    
    /**
     * Create and register a summary metric
     * सारांश मेट्रिक बनाएं और रजिस्टर करें
     */
    public DistributionSummary createSummary(String name, String description, String... tagNames) {
        DistributionSummary summary = DistributionSummary.builder(name)
            .description(description)
            .tags("service", serviceName, "version", serviceVersion,
                  "environment", environment, "region", region)
            .register(meterRegistry);
        
        summaries.put(name, summary);
        return summary;
    }
    
    /**
     * Record trading event with comprehensive observability
     * व्यापक ऑब्जर्वेबिलिटी के साथ ट्रेडिंग इवेंट रिकॉर्ड करें
     */
    public void recordTradingEvent(TradingEvent event) {
        // Start distributed trace
        TraceSpan span = startTrace("trade_execution", "trading-engine");
        span.setTag("user.id", event.getUserId());
        span.setTag("symbol", event.getSymbol());
        span.setTag("quantity", event.getQuantity());
        span.setTag("price", event.getPrice());
        span.setTag("event.type", event.getEventType());
        
        try {
            // Setup MDC for structured logging
            MDC.put("traceId", span.getTraceId());
            MDC.put("spanId", span.getSpanId());
            MDC.put("userId", event.getUserId());
            MDC.put("symbol", event.getSymbol());
            
            // Record metrics
            recordTradeMetrics(event);
            
            // Log the event
            logTradingEvent(event);
            
            span.log("Trading event processed successfully");
            
        } catch (Exception e) {
            span.setTag("error", true);
            span.setTag("error.message", e.getMessage());
            span.log("Error processing trading event: " + e.getMessage());
            
            logger.error("Error processing trading event: {}", event.getEventId(), e);
            
            // Increment error counter
            counters.get("trades_total").increment(
                Tags.of("symbol", event.getSymbol(), "order_type", event.getEventType(), "status", "error")
            );
            
        } finally {
            span.finish();
            completedTraces.add(span);
            
            // Clear MDC
            MDC.clear();
        }
    }
    
    /**
     * Record trade-specific metrics
     * व्यापार-विशिष्ट मेट्रिक्स रिकॉर्ड करें
     */
    private void recordTradeMetrics(TradingEvent event) {
        // Increment trade counter
        counters.get("trades_total").increment(
            Tags.of("symbol", event.getSymbol(), "order_type", event.getEventType())
        );
        
        // Record order value distribution
        double orderValue = event.getQuantity() * event.getPrice();
        summaries.get("order_value_distribution").record(orderValue,
            Tags.of("symbol", event.getSymbol(), "order_type", event.getEventType())
        );
        
        // Simulate order processing time
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            Thread.sleep(ThreadLocalRandom.current().nextInt(10, 50)); // Simulate processing
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        sample.stop(timers.get("order_processing_duration").timer(
            Tags.of("order_type", event.getEventType(), "symbol", event.getSymbol())
        ));
    }
    
    /**
     * Log trading event with structured format
     * संरचित प्रारूप के साथ ट्रेडिंग इवेंट लॉग करें
     */
    private void logTradingEvent(TradingEvent event) {
        logger.info("Trading event processed: {} for user: {} symbol: {} quantity: {} price: {} value: INR {}",
            event.getEventType(),
            event.getUserId(),
            event.getSymbol(),
            event.getQuantity(),
            event.getPrice(),
            String.format("%.2f", event.getQuantity() * event.getPrice())
        );
    }
    
    /**
     * Start a new distributed trace
     * नया डिस्ट्रिब्यूटेड ट्रेस शुरू करें
     */
    public TraceSpan startTrace(String operationName, String serviceName) {
        String traceId = UUID.randomUUID().toString().replace("-", "").substring(0, 16);
        TraceSpan span = new TraceSpan(traceId, operationName, serviceName);
        
        activeSpans.put(span.getSpanId(), span);
        return span;
    }
    
    /**
     * Start a child span
     * चाइल्ड स्पैन शुरू करें
     */
    public TraceSpan startChildSpan(String parentSpanId, String operationName, String serviceName) {
        TraceSpan parentSpan = activeSpans.get(parentSpanId);
        if (parentSpan == null) {
            // If parent not found, start new trace
            return startTrace(operationName, serviceName);
        }
        
        TraceSpan childSpan = new TraceSpan(parentSpan.getTraceId(), parentSpanId, operationName, serviceName);
        activeSpans.put(childSpan.getSpanId(), childSpan);
        return childSpan;
    }
    
    /**
     * Simulate market data processing with observability
     * ऑब्जर्वेबिलिटी के साथ मार्केट डेटा प्रोसेसिंग सिम्युलेट करें
     */
    public void processMarketData(String symbol, String feedType, double price, long volume) {
        TraceSpan span = startTrace("market_data_processing", "market-data-service");
        span.setTag("symbol", symbol);
        span.setTag("feed.type", feedType);
        span.setTag("price", price);
        span.setTag("volume", volume);
        
        Timer.Sample latencySample = Timer.start(meterRegistry);
        
        try {
            MDC.put("traceId", span.getTraceId());
            MDC.put("symbol", symbol);
            
            // Simulate processing delay
            Thread.sleep(ThreadLocalRandom.current().nextInt(5, 25));
            
            // Record market data event
            counters.get("market_data_events_total").increment(
                Tags.of("symbol", symbol, "event_type", "price_update")
            );
            
            span.log(String.format("Processed market data for %s: INR %.2f (Volume: %d)", 
                symbol, price, volume));
            
            logger.info("Market data processed: {} price: INR {:.2f} volume: {} feed: {}",
                symbol, price, volume, feedType);
            
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            span.setTag("error", true);
            span.log("Market data processing interrupted");
            
        } finally {
            latencySample.stop(timers.get("market_data_latency").timer(
                Tags.of("symbol", symbol, "feed_type", feedType)
            ));
            
            span.finish();
            completedTraces.add(span);
            activeSpans.remove(span.getSpanId());
            
            MDC.clear();
        }
    }
    
    /**
     * Check alert rules and fire alerts
     * अलर्ट नियमों की जाँच करें और अलर्ट फायर करें
     */
    public void evaluateAlerts() {
        for (AlertRule rule : alertRules) {
            try {
                // Simulate metric evaluation (in real implementation, query Prometheus)
                double currentValue = simulateMetricQuery(rule.getQuery());
                boolean alertCondition = evaluateCondition(currentValue, rule.getThreshold(), rule.getOperator());
                
                String alertKey = rule.getRuleName();
                Instant lastAlertTime = alertStates.get(alertKey);
                Instant now = Instant.now();
                
                if (alertCondition) {
                    // Check if we should fire alert (not in cooldown)
                    if (lastAlertTime == null || 
                        Duration.between(lastAlertTime, now).compareTo(rule.getEvaluationWindow()) > 0) {
                        
                        fireAlert(rule, currentValue);
                        alertStates.put(alertKey, now);
                    }
                } else {
                    // Clear alert state if condition is no longer met
                    alertStates.remove(alertKey);
                }
                
            } catch (Exception e) {
                logger.error("Error evaluating alert rule: {}", rule.getRuleName(), e);
            }
        }
    }
    
    /**
     * Simulate metric query (replace with actual Prometheus query)
     * मेट्रिक क्वेरी सिम्युलेट करें
     */
    private double simulateMetricQuery(String query) {
        // Simulate different metric values based on query
        if (query.contains("order_processing_duration")) {
            return ThreadLocalRandom.current().nextDouble(0.050, 0.200); // 50-200ms
        } else if (query.contains("api_error_rate")) {
            return ThreadLocalRandom.current().nextDouble(0.01, 0.10); // 1-10%
        } else if (query.contains("market_data_latency")) {
            return ThreadLocalRandom.current().nextDouble(0.020, 0.080); // 20-80ms
        }
        
        return ThreadLocalRandom.current().nextDouble(0, 100);
    }
    
    /**
     * Evaluate alert condition
     * अलर्ट स्थिति का मूल्यांकन करें
     */
    private boolean evaluateCondition(double value, double threshold, String operator) {
        switch (operator) {
            case "gt": return value > threshold;
            case "lt": return value < threshold;
            case "eq": return Math.abs(value - threshold) < 0.001;
            case "ne": return Math.abs(value - threshold) >= 0.001;
            default: return false;
        }
    }
    
    /**
     * Fire alert to configured channels
     * कॉन्फ़िगर चैनल पर अलर्ट फायर करें
     */
    private void fireAlert(AlertRule rule, double currentValue) {
        String alertMessage = String.format(
            "🚨 ALERT: %s\n" +
            "Current Value: %.4f\n" +
            "Threshold: %.4f (%s)\n" +
            "Severity: %s\n" +
            "Service: %s (%s)\n" +
            "Region: %s\n" +
            "Time: %s IST",
            rule.getRuleName(),
            currentValue,
            rule.getThreshold(),
            rule.getOperator(),
            rule.getSeverity(),
            serviceName,
            serviceVersion,
            region,
            LocalDateTime.now(ZoneId.of("Asia/Kolkata")).format(DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss"))
        );
        
        // Send to notification channels
        for (String channel : rule.getNotificationChannels()) {
            sendNotification(channel, alertMessage, rule.getSeverity());
        }
        
        logger.warn("Alert fired: {} - Current value: {:.4f}, Threshold: {:.4f}", 
            rule.getRuleName(), currentValue, rule.getThreshold());
    }
    
    /**
     * Send notification to channel
     * चैनल पर नोटिफिकेशन भेजें
     */
    private void sendNotification(String channel, String message, AlertSeverity severity) {
        // Simulate notification sending
        switch (channel) {
            case "pagerduty":
                logger.info("📟 PagerDuty alert sent: {}", severity);
                break;
            case "slack-trading":
                logger.info("📱 Slack (trading) notification sent");
                break;
            case "email-oncall":
                logger.info("📧 Email notification sent to on-call team");
                break;
            case "sms":
                logger.info("📲 SMS alert sent for critical issue");
                break;
            default:
                logger.info("📢 Notification sent to channel: {}", channel);
        }
    }
    
    /**
     * Get observability dashboard data
     * ऑब्जर्वेबिलिटी डैशबोर्ड डेटा प्राप्त करें
     */
    public Map<String, Object> getDashboardData() {
        Map<String, Object> dashboard = new HashMap<>();
        
        // Service information
        dashboard.put("service", Map.of(
            "name", serviceName,
            "version", serviceVersion,
            "environment", environment,
            "region", region,
            "uptime_seconds", System.currentTimeMillis() / 1000
        ));
        
        // Metrics summary
        dashboard.put("metrics", Map.of(
            "counters_count", counters.size(),
            "timers_count", timers.size(),
            "summaries_count", summaries.size(),
            "active_spans", activeSpans.size(),
            "completed_traces", completedTraces.size()
        ));
        
        // Alert summary
        long activeAlerts = alertStates.size();
        long criticalAlerts = alertRules.stream()
            .filter(rule -> rule.getSeverity() == AlertSeverity.CRITICAL)
            .count();
        
        dashboard.put("alerts", Map.of(
            "total_rules", alertRules.size(),
            "active_alerts", activeAlerts,
            "critical_rules", criticalAlerts
        ));
        
        // Recent traces
        List<Map<String, Object>> recentTraces = completedTraces.stream()
            .sorted((a, b) -> b.getStartTime().compareTo(a.getStartTime()))
            .limit(10)
            .map(span -> Map.of(
                "trace_id", span.getTraceId(),
                "operation", span.getOperationName(),
                "duration_ms", span.getDuration().toMillis(),
                "service", span.getServiceName(),
                "tags", span.getTags()
            ))
            .collect(Collectors.toList());
        
        dashboard.put("recent_traces", recentTraces);
        
        return dashboard;
    }
    
    /**
     * Main demonstration method
     * मुख्य प्रदर्शन विधि
     */
    public static void main(String[] args) throws InterruptedException {
        System.out.println("📊 Zerodha Trading Platform Observability Stack Demo");
        System.out.println("=================================================");
        
        CloudNativeObservabilityStack observability = new CloudNativeObservabilityStack(
            "trading-engine", "2.1.0", "production", "ap-south-1"
        );
        
        System.out.println("\n🔍 Processing sample trading events...");
        
        // Simulate trading events
        String[] symbols = {"RELIANCE", "TCS", "INFY", "HDFC", "ICICI"};
        String[] orderTypes = {"BUY", "SELL", "MODIFY", "CANCEL"};
        
        for (int i = 0; i < 20; i++) {
            String symbol = symbols[ThreadLocalRandom.current().nextInt(symbols.length)];
            String orderType = orderTypes[ThreadLocalRandom.current().nextInt(orderTypes.length)];
            
            TradingEvent event = new TradingEvent(
                orderType,
                "user_" + (1000 + i),
                symbol,
                ThreadLocalRandom.current().nextInt(1, 1000),
                ThreadLocalRandom.current().nextDouble(100, 3000)
            );
            
            observability.recordTradingEvent(event);
            
            // Simulate market data
            observability.processMarketData(
                symbol,
                "NSE_LIVE",
                ThreadLocalRandom.current().nextDouble(100, 3000),
                ThreadLocalRandom.current().nextLong(1000, 100000)
            );
            
            Thread.sleep(100); // Small delay between events
        }
        
        System.out.println("\n⚠️ Evaluating alert rules...");
        observability.evaluateAlerts();
        
        System.out.println("\n📊 Dashboard Summary:");
        Map<String, Object> dashboard = observability.getDashboardData();
        dashboard.forEach((key, value) -> {
            System.out.println("  " + key + ": " + value);
        });
        
        System.out.println("\n✅ Observability stack demonstration completed!");
        System.out.println("\n📈 Key Features Demonstrated:");
        System.out.println("  ✅ Prometheus metrics integration");
        System.out.println("  ✅ Distributed tracing with spans");
        System.out.println("  ✅ Structured logging with MDC");
        System.out.println("  ✅ Custom alert rules and evaluation");
        System.out.println("  ✅ Multi-channel notification system");
        System.out.println("  ✅ Trading-specific metrics and monitoring");
        System.out.println("  ✅ Indian timezone and localization");
    }
}