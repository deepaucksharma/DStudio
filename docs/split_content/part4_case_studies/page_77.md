Page 77: Observability Stacks
You can't fix what you can't see
THE OBSERVABILITY TRIAD
        Metrics
          ↑
       INSIGHTS
      ↙        ↘
   Logs ←----→ Traces

Metrics: What is broken
Logs: Why it's broken  
Traces: Where it's broken
MODERN OBSERVABILITY STACK
Metrics Layer
Collection → Storage → Query → Visualization → Alerting

Popular Stack:
- Collection: Prometheus exporters, StatsD
- Storage: Prometheus, InfluxDB, M3
- Query: PromQL, Flux
- Visualization: Grafana
- Alerting: Alertmanager

Key Decisions:
- Push vs Pull model
- Retention period (15d default)
- Cardinality limits
- Aggregation strategy
Logging Layer
Generation → Collection → Processing → Storage → Analysis

Popular Stack:
- Generation: Structured logging (JSON)
- Collection: Fluentd, Logstash, Vector
- Processing: Stream processing
- Storage: Elasticsearch, Loki, S3
- Analysis: Kibana, Grafana

Key Decisions:
- Structured vs unstructured
- Sampling rate
- Retention policy  
- Index strategy
Tracing Layer
Instrumentation → Collection → Storage → Analysis

Popular Stack:
- Instrumentation: OpenTelemetry
- Collection: Jaeger agent, OTLP
- Storage: Cassandra, Elasticsearch
- Analysis: Jaeger UI, Grafana Tempo

Key Decisions:
- Sampling strategy
- Trace context propagation
- Storage retention
- Head vs tail sampling
REFERENCE ARCHITECTURE
                    Applications
                         ↓
              [OpenTelemetry SDK/Agents]
                    ↓    ↓    ↓
                Metrics Logs Traces
                   ↓     ↓     ↓
              [OTLP Collector Cluster]
                ↙      ↓        ↘
        Prometheus  Loki    Jaeger/Tempo
              ↘      ↓        ↙
                  Grafana
                     ↓
              📊 Dashboards
              🚨 Alerts
              🔍 Exploration
IMPLEMENTATION GUIDE
1. Instrument Applications
// Metrics
const requestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request latency',
  labelNames: ['method', 'route', 'status']
});

// Logs (structured)
logger.info('Request processed', {
  requestId: req.id,
  userId: user.id,
  duration: duration,
  status: res.statusCode
});

// Traces
const span = tracer.startSpan('process_payment', {
  attributes: {
    'payment.amount': amount,
    'payment.currency': currency
  }
});
2. Optimize Collection
Collector Configuration:
processors:
  batch:
    send_batch_size: 1000
    timeout: 10s
  
  memory_limiter:
    check_interval: 1s
    limit_mib: 512
  
  sampling:
    decision_cache_size: 10000
    trace_id_ratio: 0.1  # 10% sampling

Resource optimization:
- Batch to reduce network calls
- Sample to control volume
- Filter noise early
- Compress where possible
3. Design Dashboards
Dashboard Hierarchy:

1. Service Overview (RED metrics)
   - Rate: Requests per second
   - Errors: Error percentage  
   - Duration: Latency percentiles

2. Infrastructure View
   - CPU, Memory, Disk, Network
   - Saturation indicators
   - Capacity remaining

3. Business Metrics
   - Conversion rates
   - Revenue impact
   - User experience scores

4. Detailed Debugging
   - Log aggregations
   - Trace analysis
   - Error breakdowns
OBSERVABILITY PATTERNS
1. Correlation IDs
Flow:
Request → Generate ID → Pass to all services → Include in all telemetry

Implementation:
middleware.correlationId = (req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] 
                      || generateId();
  res.setHeader('x-correlation-id', req.correlationId);
  
  // Add to all telemetry
  logger.setContext({correlationId: req.correlationId});
  tracer.setTag('correlation.id', req.correlationId);
  metrics.setLabel('correlation_id', req.correlationId);
  
  next();
};
2. Service Dependency Mapping
Automatic discovery through:
- Trace analysis (who calls whom)
- Network traffic analysis
- Service mesh data
- DNS queries

Visualization:
- Force-directed graphs
- Sankey diagrams
- Heat maps for call volume
3. Anomaly Detection
Statistical approach:
- Baseline normal behavior
- Detect deviations (3-sigma)
- Seasonal adjustment
- Trend analysis

ML approach:
- Train on historical data
- Predict expected values
- Alert on anomalies
- Reduce false positives
COST OPTIMIZATION
Metrics Costs
Factors:
- Cardinality (unique label combinations)
- Retention period
- Query frequency

Optimizations:
- Limit label cardinality
- Downsample old data
- Pre-aggregate common queries
- Use recording rules

Example savings:
Before: 10M series × 15d = $5000/month
After: 1M series × 15d + aggregates = $800/month
Log Costs
Factors:
- Volume (GB/day)
- Retention
- Indexing

Optimizations:
- Log sampling (1:10 for info)
- Compression
- Tiered storage (hot/warm/cold)
- Index only searchable fields

Example savings:
Before: 1TB/day × 30d = $15000/month
After: 100GB/day × 7d hot + S3 = $2000/month
Trace Costs
Factors:
- Trace volume
- Span cardinality
- Retention

Optimizations:
- Head-based sampling (random)
- Tail-based sampling (errors only)
- Trace aggregation
- Adaptive sampling

Example savings:
Before: 100% traces = $8000/month
After: 1% baseline + errors = $1200/month
TROUBLESHOOTING WITH OBSERVABILITY
Investigation Flow
1. Alert fires: "Payment service error rate high"

2. Check metrics dashboard:
   - Error rate: 15% (normal: <1%)
   - Latency: p99 = 5s (normal: 100ms)
   - Started: 10:42 AM

3. Query logs:
   - Filter: service="payment" level="error" @timestamp>10:40
   - Finding: "Database connection timeout"
   - Pattern: All errors from payment-db-2

4. Analyze traces:
   - Filter: service="payment" error=true
   - Finding: payment-db-2 responding in 5s
   - Root span: Database query stuck

5. Check infrastructure:
   - payment-db-2 CPU: 100%
   - Disk I/O: Saturated
   - Finding: Backup job running

Resolution: Kill backup job, reschedule for off-peak
OBSERVABILITY MATURITY
Level 1: Reactive
- Basic logging to files
- Manual log searching
- CPU/memory graphs
- Email alerts
Level 2: Proactive
- Centralized logging
- Basic dashboards
- Threshold alerts
- Some tracing
Level 3: Predictive
- Full observability stack
- Correlation across signals
- Anomaly detection
- SLO-based alerts
Level 4: Prescriptive
- AIOps integration
- Automated remediation
- Predictive scaling
- Cost optimization