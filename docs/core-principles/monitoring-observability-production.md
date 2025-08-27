# Monitoring and Observability in Production: The Complete Guide

## Executive Summary

Observability is not just monitoring - it's the ability to understand your system's internal state from its external outputs. This guide provides production-ready implementations for comprehensive observability including metrics, logs, traces, and alerting strategies used by companies operating at scale.

---

## Part 1: The Three Pillars of Observability

### Metrics - Quantitative Measurements

```java
@Configuration
public class MetricsConfiguration {
    
    /**
     * Prometheus metrics setup
     */
    @Bean
    public MeterRegistry meterRegistry() {
        PrometheusMeterRegistry registry = new PrometheusMeterRegistry(PrometheusConfig.DEFAULT);
        
        // Common tags for all metrics
        registry.config().commonTags(
            "application", applicationName,
            "environment", environment,
            "region", region,
            "instance", instanceId
        );
        
        // JVM metrics
        new ClassLoaderMetrics().bindTo(registry);
        new JvmMemoryMetrics().bindTo(registry);
        new JvmGcMetrics().bindTo(registry);
        new JvmThreadMetrics().bindTo(registry);
        
        // System metrics
        new ProcessorMetrics().bindTo(registry);
        new FileDescriptorMetrics().bindTo(registry);
        
        return registry;
    }
    
    /**
     * Custom business metrics
     */
    @Component
    public class BusinessMetrics {
        
        private final MeterRegistry registry;
        
        // Revenue metrics
        public void recordTransaction(Transaction transaction) {
            registry.counter("business.transactions",
                "type", transaction.getType(),
                "currency", transaction.getCurrency(),
                "status", transaction.getStatus())
                .increment();
            
            registry.summary("business.transaction.amount",
                "currency", transaction.getCurrency())
                .record(transaction.getAmount());
            
            // Track by percentiles
            registry.timer("business.transaction.processing_time")
                .record(transaction.getProcessingTime());
        }
        
        // User metrics
        public void recordUserActivity(UserActivity activity) {
            registry.counter("users.activity",
                "action", activity.getAction(),
                "platform", activity.getPlatform())
                .increment();
            
            // Gauge for active users
            registry.gauge("users.active", 
                activeUserService.getActiveUserCount());
        }
        
        // Error metrics
        public void recordError(Exception error, String context) {
            registry.counter("errors",
                "type", error.getClass().getSimpleName(),
                "context", context)
                .increment();
            
            // Track error rate
            errorRateGauge.set(calculateErrorRate());
        }
    }
}
```

### Logging - Structured Event Data

```java
@Configuration
public class LoggingConfiguration {
    
    /**
     * Structured logging with context
     */
    @Component
    public class StructuredLogger {
        
        private static final Logger log = LoggerFactory.getLogger(StructuredLogger.class);
        
        public void logRequest(HttpServletRequest request, HttpServletResponse response, long duration) {
            MDC.put("request_id", request.getHeader("X-Request-ID"));
            MDC.put("user_id", extractUserId(request));
            MDC.put("method", request.getMethod());
            MDC.put("path", request.getRequestURI());
            MDC.put("status", String.valueOf(response.getStatus()));
            MDC.put("duration_ms", String.valueOf(duration));
            MDC.put("ip", request.getRemoteAddr());
            
            if (response.getStatus() >= 500) {
                log.error("Request failed with server error");
            } else if (response.getStatus() >= 400) {
                log.warn("Request failed with client error");
            } else {
                log.info("Request completed successfully");
            }
            
            MDC.clear();
        }
        
        public void logBusinessEvent(BusinessEvent event) {
            try (MDC.MDCCloseable closeable = MDC.putCloseable("event_type", event.getType())) {
                MDC.put("event_id", event.getId());
                MDC.put("timestamp", event.getTimestamp().toString());
                MDC.put("user_id", event.getUserId());
                
                // Add custom fields
                event.getMetadata().forEach(MDC::put);
                
                log.info("Business event: {}", event.getDescription());
            }
        }
        
        public void logError(Exception error, Map<String, String> context) {
            context.forEach(MDC::put);
            MDC.put("error_type", error.getClass().getName());
            MDC.put("error_message", error.getMessage());
            
            // Add stack trace fingerprint for grouping
            MDC.put("error_fingerprint", generateFingerprint(error));
            
            log.error("Application error occurred", error);
            
            MDC.clear();
        }
        
        private String generateFingerprint(Exception error) {
            // Create fingerprint from exception type and top stack frames
            StringBuilder fingerprint = new StringBuilder();
            fingerprint.append(error.getClass().getName());
            
            StackTraceElement[] stack = error.getStackTrace();
            for (int i = 0; i < Math.min(3, stack.length); i++) {
                fingerprint.append(":")
                    .append(stack[i].getClassName())
                    .append(".")
                    .append(stack[i].getMethodName())
                    .append(":")
                    .append(stack[i].getLineNumber());
            }
            
            return DigestUtils.md5Hex(fingerprint.toString());
        }
    }
    
    /**
     * Log aggregation configuration
     */
    @Bean
    public LogbackConfiguration logbackConfiguration() {
        LoggerContext context = (LoggerContext) LoggerFactory.getILoggerFactory();
        
        // JSON encoder for structured logs
        LogstashEncoder encoder = new LogstashEncoder();
        encoder.setIncludeMdc(true);
        encoder.setIncludeContext(true);
        encoder.setIncludeCallerData(true);
        
        // Async appender for performance
        AsyncAppender asyncAppender = new AsyncAppender();
        asyncAppender.setQueueSize(512);
        asyncAppender.setDiscardingThreshold(0);
        
        // Console appender
        ConsoleAppender<ILoggingEvent> consoleAppender = new ConsoleAppender<>();
        consoleAppender.setEncoder(encoder);
        asyncAppender.addAppender(consoleAppender);
        
        // Add to root logger
        ch.qos.logback.classic.Logger rootLogger = context.getLogger(Logger.ROOT_LOGGER_NAME);
        rootLogger.addAppender(asyncAppender);
        
        return new LogbackConfiguration();
    }
}
```

### Distributed Tracing - Request Flow Tracking

```java
@Configuration
public class TracingConfiguration {
    
    /**
     * OpenTelemetry setup
     */
    @Bean
    public OpenTelemetry openTelemetry() {
        Resource resource = Resource.getDefault()
            .merge(Resource.create(Attributes.of(
                ResourceAttributes.SERVICE_NAME, applicationName,
                ResourceAttributes.SERVICE_VERSION, applicationVersion,
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT, environment
            )));
        
        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(
                OtlpGrpcSpanExporter.builder()
                    .setEndpoint(otlpEndpoint)
                    .build())
                .build())
            .setSampler(Sampler.traceIdRatioBased(samplingRate))
            .setResource(resource)
            .build();
        
        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setPropagators(ContextPropagators.create(
                W3CTraceContextPropagator.getInstance()))
            .buildAndRegisterGlobal();
    }
    
    /**
     * Tracing interceptor
     */
    @Component
    public class TracingInterceptor implements HandlerInterceptor {
        
        private final Tracer tracer;
        
        @Override
        public boolean preHandle(HttpServletRequest request, 
                               HttpServletResponse response, 
                               Object handler) {
            
            // Extract parent context
            Context extractedContext = openTelemetry.getPropagators()
                .getTextMapPropagator()
                .extract(Context.current(), request, getter);
            
            // Start span
            Span span = tracer.spanBuilder(request.getMethod() + " " + request.getRequestURI())
                .setParent(extractedContext)
                .setSpanKind(SpanKind.SERVER)
                .setAttribute("http.method", request.getMethod())
                .setAttribute("http.url", request.getRequestURL().toString())
                .setAttribute("http.target", request.getRequestURI())
                .setAttribute("user.id", extractUserId(request))
                .startSpan();
            
            // Store in request
            request.setAttribute("span", span);
            
            return true;
        }
        
        @Override
        public void afterCompletion(HttpServletRequest request,
                                   HttpServletResponse response,
                                   Object handler,
                                   Exception ex) {
            
            Span span = (Span) request.getAttribute("span");
            if (span != null) {
                span.setAttribute("http.status_code", response.getStatus());
                
                if (ex != null) {
                    span.recordException(ex);
                    span.setStatus(StatusCode.ERROR, ex.getMessage());
                } else if (response.getStatus() >= 400) {
                    span.setStatus(StatusCode.ERROR);
                } else {
                    span.setStatus(StatusCode.OK);
                }
                
                span.end();
            }
        }
    }
    
    /**
     * Database tracing
     */
    @Component
    public class DatabaseTracingAspect {
        
        private final Tracer tracer;
        
        @Around("@annotation(org.springframework.data.repository.Query)")
        public Object traceQuery(ProceedingJoinPoint joinPoint) throws Throwable {
            String query = extractQuery(joinPoint);
            
            Span span = tracer.spanBuilder("database.query")
                .setSpanKind(SpanKind.CLIENT)
                .setAttribute("db.system", "postgresql")
                .setAttribute("db.statement", query)
                .setAttribute("db.operation", extractOperation(query))
                .startSpan();
            
            try (Scope scope = span.makeCurrent()) {
                Object result = joinPoint.proceed();
                
                if (result instanceof Collection) {
                    span.setAttribute("db.rows_affected", 
                        ((Collection<?>) result).size());
                }
                
                return result;
                
            } catch (Exception e) {
                span.recordException(e);
                span.setStatus(StatusCode.ERROR, e.getMessage());
                throw e;
                
            } finally {
                span.end();
            }
        }
    }
}
```

---

## Part 2: Production Monitoring Stack

### Prometheus + Grafana Setup

```yaml
# docker-compose.yml for monitoring stack
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alerts.yml:/etc/prometheus/alerts.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
      - '--storage.tsdb.retention.size=50GB'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana:latest
    volumes:
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - ./grafana/provisioning:/etc/grafana/provisioning
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    ports:
      - "3000:3000"
    
  alertmanager:
    image: prom/alertmanager:latest
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    ports:
      - "9093:9093"
    
  loki:
    image: grafana/loki:latest
    volumes:
      - ./loki-config.yml:/etc/loki/local-config.yaml
      - loki_data:/loki
    ports:
      - "3100:3100"
    
  tempo:
    image: grafana/tempo:latest
    volumes:
      - ./tempo-config.yml:/etc/tempo.yaml
      - tempo_data:/tmp/tempo
    command: ["-config.file=/etc/tempo.yaml"]
    ports:
      - "3200:3200"   # tempo
      - "4317:4317"   # otlp grpc
      - "4318:4318"   # otlp http

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
  loki_data:
  tempo_data:
```

### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'production'
    region: 'us-east-1'

# Alert rules
rule_files:
  - "alerts.yml"

# Alertmanager configuration
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# Scrape configurations
scrape_configs:
  # Application metrics
  - job_name: 'application'
    kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
            - production
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
  
  # Node exporter
  - job_name: 'node'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
  
  # Kubernetes metrics
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https
```

---

## Part 3: Alert Engineering

### Alert Rules and Runbooks

```yaml
# alerts.yml
groups:
  - name: application_alerts
    interval: 30s
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m])) 
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} for the last 5 minutes"
          runbook_url: "https://wiki/runbooks/high-error-rate"
          dashboard_url: "https://grafana/d/app-health"
      
      # P99 latency
      - alert: HighP99Latency
        expr: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 1
        for: 10m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "P99 latency above 1s"
          description: "P99 latency is {{ $value | humanizeDuration }}"
      
      # Memory pressure
      - alert: HighMemoryUsage
        expr: |
          (container_memory_working_set_bytes 
          / container_spec_memory_limit_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Container memory usage above 90%"
          description: "Container {{ $labels.container }} memory usage is {{ $value | humanizePercentage }}"
      
      # Database connection pool
      - alert: DatabaseConnectionPoolExhaustion
        expr: |
          (hikaricp_connections_active / hikaricp_connections_max) > 0.9
        for: 5m
        labels:
          severity: critical
          team: database
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool {{ $labels.pool }} is {{ $value | humanizePercentage }} utilized"
      
      # Circuit breaker open
      - alert: CircuitBreakerOpen
        expr: |
          circuit_breaker_state{state="OPEN"} == 1
        for: 1m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "Circuit breaker is open"
          description: "Circuit breaker for {{ $labels.service }} is OPEN"
```

### Alert Manager Configuration

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_from: 'alerts@company.com'
  smtp_smarthost: 'smtp.company.com:587'
  smtp_auth_username: 'alerts@company.com'
  smtp_auth_password: 'password'
  slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
  pagerduty_url: 'https://events.pagerduty.com/v2/enqueue'

# Templates
templates:
  - '/etc/alertmanager/templates/*.tmpl'

# Route tree
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  
  routes:
    # Critical alerts go to PagerDuty
    - match:
        severity: critical
      receiver: pagerduty
      continue: true
    
    # Database alerts to DBA team
    - match:
        team: database
      receiver: dba_team
    
    # Platform alerts to platform team
    - match:
        team: platform
      receiver: platform_team

# Receivers
receivers:
  - name: 'default'
    slack_configs:
      - channel: '#alerts'
        title: 'Alert: {{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: 'YOUR-PAGERDUTY-INTEGRATION-KEY'
        description: '{{ .GroupLabels.alertname }}'
        details:
          firing: '{{ .Alerts.Firing | len }}'
          resolved: '{{ .Alerts.Resolved | len }}'
  
  - name: 'platform_team'
    slack_configs:
      - channel: '#platform-alerts'
        send_resolved: true
    email_configs:
      - to: 'platform-oncall@company.com'
  
  - name: 'dba_team'
    slack_configs:
      - channel: '#database-alerts'
    email_configs:
      - to: 'dba-oncall@company.com'

# Inhibition rules
inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'cluster', 'service']
```

---

## Part 4: SLI/SLO Implementation

### Service Level Indicators and Objectives

```java
@Service
public class SLOMonitoringService {
    
    private final MeterRegistry registry;
    
    /**
     * Track SLI metrics
     */
    @Component
    public class SLICollector {
        
        // Availability SLI
        public void recordAvailability(boolean success) {
            registry.counter("sli.availability.total").increment();
            if (success) {
                registry.counter("sli.availability.success").increment();
            }
        }
        
        // Latency SLI
        public void recordLatency(long latencyMs, String operation) {
            registry.timer("sli.latency", "operation", operation)
                .record(latencyMs, TimeUnit.MILLISECONDS);
            
            // Track against SLO threshold
            if (latencyMs <= 1000) { // 1 second SLO
                registry.counter("sli.latency.within_slo", 
                    "operation", operation).increment();
            } else {
                registry.counter("sli.latency.violation", 
                    "operation", operation).increment();
            }
        }
        
        // Error budget tracking
        @Scheduled(fixedDelay = 60000) // Every minute
        public void calculateErrorBudget() {
            // 99.9% SLO = 0.1% error budget
            double slo = 0.999;
            double errorBudget = 1 - slo;
            
            // Calculate actual error rate
            double totalRequests = registry.counter("http.requests.total")
                .count();
            double failedRequests = registry.counter("http.requests.failed")
                .count();
            double errorRate = failedRequests / totalRequests;
            
            // Calculate remaining budget
            double budgetUsed = errorRate / errorBudget;
            double budgetRemaining = Math.max(0, 1 - budgetUsed);
            
            registry.gauge("slo.error_budget.remaining", budgetRemaining);
            registry.gauge("slo.error_budget.burn_rate", 
                calculateBurnRate(errorRate, errorBudget));
            
            // Alert if budget nearly exhausted
            if (budgetRemaining < 0.1) { // Less than 10% remaining
                alertService.sendAlert(Alert.critical()
                    .title("Error budget nearly exhausted")
                    .description(String.format(
                        "Only %.1f%% of error budget remaining", 
                        budgetRemaining * 100))
                    .build());
            }
        }
    }
    
    /**
     * Multi-window error budget burn rate
     */
    public class ErrorBudgetBurnRate {
        
        private final Map<Duration, Double> burnRates = new HashMap<>();
        
        @Scheduled(fixedDelay = 60000)
        public void calculateBurnRates() {
            // Calculate burn rate for different windows
            burnRates.put(Duration.ofHours(1), 
                calculateBurnRateForWindow(Duration.ofHours(1)));
            burnRates.put(Duration.ofHours(6), 
                calculateBurnRateForWindow(Duration.ofHours(6)));
            burnRates.put(Duration.ofDays(1), 
                calculateBurnRateForWindow(Duration.ofDays(1)));
            burnRates.put(Duration.ofDays(3), 
                calculateBurnRateForWindow(Duration.ofDays(3)));
            
            // Multi-window alerting
            if (burnRates.get(Duration.ofHours(1)) > 14.4 && 
                burnRates.get(Duration.ofHours(6)) > 6) {
                // Page immediately - will exhaust budget in 1 day
                sendPage("Critical: Error budget burn rate too high");
            } else if (burnRates.get(Duration.ofHours(6)) > 3 && 
                       burnRates.get(Duration.ofDays(1)) > 1) {
                // Alert team - will exhaust budget in 4 days
                sendAlert("Warning: Elevated error budget burn rate");
            }
        }
    }
}
```

### SLO Dashboard Queries

```yaml
# Grafana dashboard for SLOs
slo_panels:
  - title: "Availability SLO"
    query: |
      (
        sum(rate(sli_availability_success[30d])) 
        / sum(rate(sli_availability_total[30d]))
      ) * 100
    thresholds:
      - value: 99.9
        color: green
      - value: 99.5
        color: yellow
      - value: 99.0
        color: red
  
  - title: "Latency SLO (P99 < 1s)"
    query: |
      (
        sum(rate(sli_latency_within_slo[30d]))
        / sum(rate(http_requests_total[30d]))
      ) * 100
  
  - title: "Error Budget Remaining"
    query: |
      slo_error_budget_remaining * 100
    unit: percent
    thresholds:
      - value: 50
        color: green
      - value: 25
        color: yellow
      - value: 10
        color: red
  
  - title: "Error Budget Burn Rate"
    query: |
      slo_error_budget_burn_rate
    thresholds:
      - value: 1
        color: green
      - value: 2
        color: yellow
      - value: 5
        color: red
```

---

## Part 5: Debugging Production Issues

### Distributed Debugging Tools

```java
@RestController
@RequestMapping("/debug")
public class ProductionDebugController {
    
    /**
     * Thread dump endpoint
     */
    @GetMapping("/threads")
    public String threadDump() {
        StringBuilder dump = new StringBuilder();
        ThreadMXBean threadMXBean = ManagementFactory.getThreadMXBean();
        
        for (ThreadInfo threadInfo : threadMXBean.dumpAllThreads(true, true)) {
            dump.append(threadInfo.toString());
        }
        
        return dump.toString();
    }
    
    /**
     * Heap dump trigger
     */
    @PostMapping("/heap-dump")
    public ResponseEntity<String> heapDump() {
        try {
            String fileName = "/tmp/heap-dump-" + 
                System.currentTimeMillis() + ".hprof";
            
            MBeanServer server = ManagementFactory.getPlatformMBeanServer();
            HotSpotDiagnosticMXBean mxBean = ManagementFactory.newPlatformMXBeanProxy(
                server, 
                "com.sun.management:type=HotSpotDiagnostic", 
                HotSpotDiagnosticMXBean.class);
            
            mxBean.dumpHeap(fileName, true);
            
            // Upload to S3
            s3Client.uploadFile(fileName, "heap-dumps/" + fileName);
            
            return ResponseEntity.ok("Heap dump created: " + fileName);
            
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Failed: " + e.getMessage());
        }
    }
    
    /**
     * Dynamic log level adjustment
     */
    @PostMapping("/log-level")
    public ResponseEntity<String> setLogLevel(
            @RequestParam String logger,
            @RequestParam String level) {
        
        LoggerContext context = (LoggerContext) LoggerFactory.getILoggerFactory();
        ch.qos.logback.classic.Logger targetLogger = context.getLogger(logger);
        
        Level newLevel = Level.toLevel(level, Level.INFO);
        targetLogger.setLevel(newLevel);
        
        return ResponseEntity.ok(String.format(
            "Logger %s set to %s", logger, level));
    }
    
    /**
     * Profiling endpoint
     */
    @GetMapping("/profile")
    public ResponseEntity<String> profile(
            @RequestParam(defaultValue = "30") int seconds) {
        
        // Start async profiling
        CompletableFuture.runAsync(() -> {
            try {
                // Use async-profiler
                String output = "/tmp/profile-" + 
                    System.currentTimeMillis() + ".html";
                
                ProcessBuilder pb = new ProcessBuilder(
                    "/opt/async-profiler/profiler.sh",
                    "-d", String.valueOf(seconds),
                    "-f", output,
                    String.valueOf(ProcessHandle.current().pid())
                );
                
                Process process = pb.start();
                process.waitFor();
                
                // Upload result
                s3Client.uploadFile(output, "profiles/" + output);
                
            } catch (Exception e) {
                log.error("Profiling failed", e);
            }
        });
        
        return ResponseEntity.ok("Profiling started for " + seconds + " seconds");
    }
}
```

---

## Part 6: Observability Best Practices

### Golden Signals Monitoring

```java
@Component
public class GoldenSignalsMonitor {
    
    /**
     * The Four Golden Signals
     */
    
    // 1. Latency
    public void recordLatency(String operation, long duration) {
        registry.timer("golden_signal.latency",
            "operation", operation)
            .record(duration, TimeUnit.MILLISECONDS);
    }
    
    // 2. Traffic
    public void recordTraffic(String endpoint) {
        registry.counter("golden_signal.traffic",
            "endpoint", endpoint)
            .increment();
    }
    
    // 3. Errors
    public void recordError(String operation, Exception error) {
        registry.counter("golden_signal.errors",
            "operation", operation,
            "error_type", error.getClass().getSimpleName())
            .increment();
    }
    
    // 4. Saturation
    @Scheduled(fixedDelay = 10000)
    public void recordSaturation() {
        // CPU saturation
        OperatingSystemMXBean os = ManagementFactory.getOperatingSystemMXBean();
        registry.gauge("golden_signal.saturation.cpu", 
            os.getProcessCpuLoad());
        
        // Memory saturation
        MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
        double heapUsage = (double) memory.getHeapMemoryUsage().getUsed() / 
            memory.getHeapMemoryUsage().getMax();
        registry.gauge("golden_signal.saturation.memory", heapUsage);
        
        // Thread pool saturation
        ThreadPoolExecutor executor = getMainExecutor();
        double threadSaturation = (double) executor.getActiveCount() / 
            executor.getMaximumPoolSize();
        registry.gauge("golden_signal.saturation.threads", threadSaturation);
        
        // Database connection saturation
        HikariDataSource dataSource = getDataSource();
        double connectionSaturation = (double) dataSource.getHikariPoolMXBean()
            .getActiveConnections() / dataSource.getMaximumPoolSize();
        registry.gauge("golden_signal.saturation.db_connections", 
            connectionSaturation);
    }
}
```

### Observability Checklist

```yaml
observability_checklist:
  metrics:
    - [ ] Application metrics exposed
    - [ ] Business metrics tracked
    - [ ] Resource utilization monitored
    - [ ] Error rates calculated
    - [ ] Latency percentiles recorded
    
  logging:
    - [ ] Structured logging implemented
    - [ ] Request IDs propagated
    - [ ] Error fingerprinting enabled
    - [ ] Log levels configurable
    - [ ] Sensitive data redacted
    
  tracing:
    - [ ] Distributed tracing enabled
    - [ ] Critical paths instrumented
    - [ ] Database queries traced
    - [ ] External calls traced
    - [ ] Sampling configured
    
  alerting:
    - [ ] SLOs defined
    - [ ] Error budgets tracked
    - [ ] Alert fatigue minimized
    - [ ] Runbooks linked
    - [ ] Escalation paths defined
    
  dashboards:
    - [ ] Service overview dashboard
    - [ ] Business metrics dashboard
    - [ ] Infrastructure dashboard
    - [ ] SLO dashboard
    - [ ] Debug dashboard
```

---

## Summary: Building Observable Systems

### Key Principles

1. **Instrument Everything**: Every request, every operation, every decision
2. **Structure Your Data**: Use consistent schemas and naming conventions
3. **Sample Wisely**: Balance data volume with observability needs
4. **Alert on Symptoms**: Focus on user impact, not individual metrics
5. **Automate Response**: Build self-healing where possible

### Common Pitfalls

1. **Metric Explosion**: Too many metrics without clear purpose
2. **Alert Fatigue**: Too many alerts that don't require action
3. **Missing Context**: Logs/metrics without correlation IDs
4. **Sampling Bias**: Unrepresentative sampling skewing insights
5. **Tool Sprawl**: Too many observability tools without integration

Remember: **Observability is not a feature you add, it's a property you design for.**