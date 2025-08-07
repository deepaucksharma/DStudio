# Data Pipeline Architecture Examination

**Duration**: 3 hours  
**Total Points**: 400 points  
**Passing Score**: 280 points (70%)  
**Focus**: Petabyte-scale data processing and production-grade implementations

## Exam Instructions

- Answer all questions completely
- Show your work for system design problems
- Provide code snippets where requested
- Consider scalability, reliability, and performance in all solutions
- Use real-world examples and trade-offs in your explanations

---

## Section 1: Batch vs Stream Processing (50 points)

### Question 1.1 (5 points)
Compare the latency characteristics of batch processing vs stream processing for a 10TB daily dataset. When would you choose each approach?

### Question 1.2 (5 points)
Explain the Lambda Architecture and Kappa Architecture. What are the operational complexities of each at petabyte scale?

### Question 1.3 (5 points)
Design a hybrid batch-stream system for processing click-stream data where:
- Real-time aggregations needed for fraud detection (sub-second)
- Daily reports for business analytics
- Historical data reprocessing capabilities

### Question 1.4 (5 points)
How does Apache Kafka's log-based storage enable both batch and stream processing paradigms? Discuss partition strategies for 1TB/hour ingestion.

### Question 1.5 (5 points)
Compare resource utilization patterns between Apache Spark (batch) and Apache Flink (stream) for the same 100GB/hour workload.

### Question 1.6 (5 points)
Explain exactly-once semantics in stream processing. How does Kafka Streams achieve this differently from Apache Storm?

### Question 1.7 (5 points)
Design a backpressure handling mechanism for a stream processing pipeline that can scale from 1GB/hour to 10TB/hour.

### Question 1.8 (5 points)
When processing time-series data with late arrivals, compare windowing strategies: tumbling, sliding, and session windows.

### Question 1.9 (5 points)
How would you implement watermarks in a distributed stream processing system to handle out-of-order events in a 24/7 trading platform?

### Question 1.10 (5 points)
Describe the trade-offs between micro-batching (Spark Streaming) and true streaming (Flink) for processing IoT sensor data from 1M devices.

---

## Section 2: ETL/ELT Patterns (50 points)

### Question 2.1 (5 points)
Compare ETL vs ELT approaches for a data warehouse with 500TB of historical data and 10TB daily ingestion. Include cost analysis.

### Question 2.2 (5 points)
Design an ELT pipeline using dbt that transforms raw e-commerce data into star schema for analytics. Show lineage tracking.

### Question 2.3 (5 points)
Implement incremental data loading using merge/upsert operations for a slowly changing dimension with 10M records updated daily.

### Question 2.4 (5 points)
How would you implement data lineage tracking across a multi-stage ETL pipeline with 50+ transformation steps?

### Question 2.5 (5 points)
Design a CDC-based ELT pipeline that can handle schema evolution while maintaining backward compatibility.

### Question 2.6 (5 points)
Explain the medallion architecture (bronze, silver, gold) for data lakes. How does it support both ETL and ELT patterns?

### Question 2.7 (5 points)
Implement idempotent data transformations in an ETL pipeline that may experience duplicate message delivery.

### Question 2.8 (5 points)
Design a multi-tenant ETL system where each tenant's data transformations are isolated but share compute resources.

### Question 2.9 (5 points)
How would you implement data quality gates in an ELT pipeline to prevent bad data from propagating downstream?

### Question 2.10 (5 points)
Compare columnar formats (Parquet, ORC, Delta Lake) for ETL workloads. Include compression ratios and query performance.

---

## Section 3: Data Quality and Validation (50 points)

### Question 3.1 (5 points)
Design a real-time data quality monitoring system for a pipeline processing 1TB/hour of financial transactions.

### Question 3.2 (5 points)
Implement statistical outlier detection for time-series data with concept drift. Handle false positives and seasonal patterns.

### Question 3.3 (5 points)
Create a data quality scorecard that aggregates multiple quality dimensions: completeness, accuracy, consistency, timeliness.

### Question 3.4 (5 points)
How would you implement schema validation for semi-structured data (JSON) with evolving schemas across multiple data sources?

### Question 3.5 (5 points)
Design a data profiling system that can automatically discover data quality rules from historical data patterns.

### Question 3.6 (5 points)
Implement referential integrity checks across distributed datasets without impacting pipeline performance.

### Question 3.7 (5 points)
Create a data quality alerting system with smart thresholding that adapts to normal business patterns and reduces false alarms.

### Question 3.8 (5 points)
How would you implement data quality quarantine where bad records are isolated for manual review without stopping the pipeline?

### Question 3.9 (5 points)
Design a data freshness monitoring system for a multi-source data pipeline with different SLA requirements per source.

### Question 3.10 (5 points)
Implement duplicate detection across streaming data using probabilistic data structures (Bloom filters, HyperLogLog).

---

## Section 4: Schema Evolution and Versioning (50 points)

### Question 4.1 (5 points)
Design a schema registry system that supports backward and forward compatibility for Avro schemas in a Kafka ecosystem.

### Question 4.2 (5 points)
Implement schema evolution for Parquet files in a data lake without breaking existing consumers. Handle column addition, deletion, and type changes.

### Question 4.3 (5 points)
How would you manage schema versioning across a microservices architecture where 20+ services produce events?

### Question 4.4 (5 points)
Design a migration strategy from JSON to Avro for a high-throughput pipeline (100K messages/sec) with zero downtime.

### Question 4.5 (5 points)
Implement schema validation at ingestion time with automatic schema inference and evolution detection.

### Question 4.6 (5 points)
Create a schema compatibility testing framework that validates schema changes against downstream consumers.

### Question 4.7 (5 points)
How would you handle schema conflicts when merging data from multiple sources with overlapping but incompatible schemas?

### Question 4.8 (5 points)
Design a schema governance system with approval workflows for breaking changes and automated deployment for compatible changes.

### Question 4.9 (5 points)
Implement schema-aware data serialization with compression optimization for different schema versions.

### Question 4.10 (5 points)
Create a schema evolution monitoring system that tracks schema drift and usage patterns across the data ecosystem.

---

## Section 5: Pipeline Orchestration (Apache Airflow, Dagster) (50 points)

### Question 5.1 (5 points)
Design an Apache Airflow DAG for a complex ML pipeline with data ingestion, feature engineering, training, and deployment stages. Include error handling and retries.

### Question 5.2 (5 points)
Implement dynamic DAG generation in Airflow for processing data from multiple regions with different compliance requirements.

### Question 5.3 (5 points)
Compare Airflow vs Dagster for orchestrating data pipelines. Include asset-based thinking and development experience.

### Question 5.4 (5 points)
Design a multi-cluster Airflow deployment that can handle 10,000+ DAGs with geographic distribution and disaster recovery.

### Question 5.5 (5 points)
Implement smart scheduling in Airflow that considers data availability, resource constraints, and business priorities.

### Question 5.6 (5 points)
Create a pipeline dependency management system that can handle cross-DAG dependencies and circular dependency detection.

### Question 5.7 (5 points)
Design an auto-scaling strategy for Airflow workers based on queue depth and task complexity metrics.

### Question 5.8 (5 points)
Implement pipeline testing strategies including unit tests for operators and integration tests for complete DAGs.

### Question 5.9 (5 points)
How would you implement blue-green deployments for data pipelines with complex interdependencies?

### Question 5.10 (5 points)
Design a pipeline observability system with metrics, tracing, and alerting for a 24/7 data platform.

---

## Section 6: Error Handling and Recovery (50 points)

### Question 6.1 (5 points)
Design a comprehensive error handling strategy for a multi-stage data pipeline including transient errors, data quality failures, and infrastructure issues.

### Question 6.2 (5 points)
Implement exponential backoff with jitter for retry mechanisms in a distributed data pipeline. Consider thundering herd problems.

### Question 6.3 (5 points)
Create a dead letter queue system for failed messages with automatic reprocessing and manual intervention capabilities.

### Question 6.4 (5 points)
Design a circuit breaker pattern for external API calls in a data ingestion pipeline processing 1M requests/hour.

### Question 6.5 (5 points)
Implement checkpointing and recovery for a stream processing application to minimize data loss during failures.

### Question 6.6 (5 points)
How would you implement graceful degradation in a real-time analytics pipeline when downstream systems are unavailable?

### Question 6.7 (5 points)
Design an error categorization system that automatically triages failures and routes them to appropriate teams.

### Question 6.8 (5 points)
Implement distributed transaction rollback across multiple data stores when pipeline execution fails midway.

### Question 6.9 (5 points)
Create a disaster recovery strategy for a data pipeline that processes critical financial data with RPO < 15 minutes.

### Question 6.10 (5 points)
Design an automatic pipeline healing system that can recover from common failure scenarios without human intervention.

---

## Implementation Challenges (100 points)

### Challenge 1: CDC Pipeline with Debezium (25 points)

Build a Change Data Capture pipeline using Debezium that:

**Requirements:**
- Captures changes from MySQL database (10M records, 100K updates/hour)
- Publishes to Kafka with exactly-once semantics
- Handles schema evolution automatically
- Provides monitoring and alerting
- Supports backfill for historical data

**Deliverables:**
- Debezium connector configuration
- Kafka topic design and partitioning strategy
- Consumer application with error handling
- Monitoring dashboard design
- Performance benchmarks

```yaml
# Provide your Debezium connector configuration here
```

```sql
-- Provide any required database setup scripts
```

```java
// Provide consumer implementation with error handling
```

### Challenge 2: Exactly-Once Processing (25 points)

Implement exactly-once processing for a payment processing pipeline:

**Requirements:**
- Process payment events from Kafka
- Update multiple downstream systems atomically
- Handle duplicate messages and out-of-order delivery
- Maintain throughput of 50K transactions/minute
- Provide audit trail for all processed transactions

**Deliverables:**
- Idempotency key design
- Transaction coordination mechanism
- State store implementation
- Monitoring and verification system
- Load testing results

```scala
// Provide Kafka Streams implementation
```

```sql
-- Provide database schema for idempotency tracking
```

### Challenge 3: Multi-Stage Data Transformation (25 points)

Design a multi-stage transformation pipeline for e-commerce data:

**Requirements:**
- Raw JSON events → Structured format → Business metrics
- Support for late-arriving data (up to 24 hours)
- Real-time aggregations and batch corrections
- Data quality validation at each stage
- Cost optimization for compute and storage

**Deliverables:**
- Pipeline architecture diagram
- Data flow and transformation logic
- Quality validation rules
- Performance optimization strategies
- Cost analysis and optimization

```python
# Provide transformation logic implementation
```

```sql
-- Provide data quality validation queries
```

### Challenge 4: Data Quality Monitoring (25 points)

Create a comprehensive data quality monitoring system:

**Requirements:**
- Monitor 100+ data pipelines across different domains
- Detect anomalies in real-time
- Provide quality scores and trending
- Smart alerting with reduced false positives
- Self-healing capabilities for common issues

**Deliverables:**
- Quality metrics framework
- Anomaly detection algorithms
- Alerting strategy and escalation
- Dashboard and visualization design
- Automated remediation workflows

```python
# Provide anomaly detection implementation
```

```yaml
# Provide monitoring configuration
```

---

## System Design Scenarios (50 points)

### Scenario 1: Real-Time Analytics Pipeline (12.5 points)

Design a real-time analytics platform for a rideshare company:

**Requirements:**
- Process 10M ride events per hour
- Provide real-time dashboards for operations
- Support ad-hoc queries on historical data
- Handle traffic spikes during peak hours
- Multi-region deployment with local analytics

**Deliverables:**
- Architecture diagram with technology stack
- Data flow and processing strategy
- Scaling and performance considerations
- Disaster recovery plan
- Cost estimation for 3-year operation

### Scenario 2: ML Feature Pipeline (12.5 points)

Build a feature engineering pipeline for ML model serving:

**Requirements:**
- Real-time feature computation (< 100ms latency)
- Batch feature backfill for training
- Feature versioning and lineage
- Online/offline feature consistency
- Support for 1000+ features across 50+ models

**Deliverables:**
- Feature store architecture
- Real-time vs batch computation strategy
- Feature versioning and deployment
- Monitoring and quality assurance
- Integration with ML platforms

### Scenario 3: Data Lake to Data Warehouse (12.5 points)

Design an ELT pipeline from data lake to data warehouse:

**Requirements:**
- Process 50TB of daily data from data lake
- Transform into dimensional model for analytics
- Handle late-arriving and corrected data
- Maintain historical data for 7 years
- Support both reporting and ad-hoc analytics

**Deliverables:**
- ETL/ELT architecture design
- Data modeling strategy
- Incremental loading approach
- Performance optimization techniques
- Governance and access control

### Scenario 4: Cross-Region Replication (12.5 points)

Implement cross-region data replication for global operations:

**Requirements:**
- Replicate critical datasets across 5 regions
- Handle network partitions and regional outages
- Ensure data consistency with acceptable latency
- Comply with data residency requirements
- Minimize cross-region data transfer costs

**Deliverables:**
- Replication topology and strategy
- Conflict resolution mechanisms
- Monitoring and alerting system
- Compliance and governance framework
- Cost optimization plan

---

## Production Case Studies (30 points)

### Case Study 1: Airbnb's Data Infrastructure (10 points)

Analyze Airbnb's data platform evolution:

**Questions:**
1. How does Airbnb handle the transition from monolith to microservices for data?
2. What are the key components of their real-time data platform?
3. How do they manage schema evolution across 1000+ microservices?
4. What lessons can be applied to other organizations?

**Reference Materials:**
- Airbnb's data platform architecture blog posts
- Conference presentations on their real-time infrastructure
- Open source contributions (Airflow origins)

### Case Study 2: Uber's Data Platform (10 points)

Examine Uber's approach to large-scale data processing:

**Questions:**
1. How does Uber's HDFS architecture handle petabyte-scale storage?
2. What is their approach to real-time stream processing for dynamic pricing?
3. How do they ensure data quality across thousands of data sources?
4. What innovations have they contributed to the data engineering community?

**Reference Materials:**
- Uber Engineering blog posts on data platform
- Technical papers on their distributed systems
- Open source projects (Hoodie, JanusGraph)

### Case Study 3: Netflix's Data Pipeline (10 points)

Study Netflix's approach to global data distribution:

**Questions:**
1. How does Netflix handle data processing for personalization at scale?
2. What is their strategy for A/B testing data infrastructure?
3. How do they manage data across multiple AWS regions?
4. What can be learned from their failure handling strategies?

**Reference Materials:**
- Netflix Technology Blog
- Conference talks on their data platform
- Open source contributions to the ecosystem

---

## Troubleshooting Exercises (35 points)

### Exercise 1: Pipeline Performance Degradation (10 points)

**Scenario**: A Spark ETL job that normally completes in 2 hours is now taking 8 hours.

**Symptoms**:
- No changes to input data volume
- Same cluster configuration
- Started 3 days ago
- Other jobs on the cluster are unaffected

**Investigation Steps**:
1. What metrics would you check first?
2. How would you identify the bottleneck?
3. What are the most likely root causes?
4. How would you implement monitoring to catch this earlier?

**Provide your troubleshooting approach and solution.**

### Exercise 2: Data Quality Regression (10 points)

**Scenario**: Data quality alerts are firing for missing values in a critical business metric.

**Symptoms**:
- 15% of records have null values in revenue field
- Started after recent deployment
- Upstream systems report no changes
- Only affects specific customer segments

**Investigation Steps**:
1. How would you trace the data lineage?
2. What validation checks would you implement?
3. How would you handle the corrupted data?
4. What preventive measures would you put in place?

**Provide your analysis and remediation plan.**

### Exercise 3: Stream Processing Lag (10 points)

**Scenario**: Kafka Streams application is falling behind with increasing consumer lag.

**Symptoms**:
- Consumer lag growing from 1 minute to 2 hours
- No increase in input rate
- CPU utilization is low (30%)
- Memory usage is stable

**Investigation Steps**:
1. What Kafka metrics would you examine?
2. How would you identify processing bottlenecks?
3. What scaling strategies would you consider?
4. How would you prevent future occurrences?

**Provide your diagnostic approach and solution.**

### Exercise 4: Cross-Region Sync Issues (5 points)

**Scenario**: Data replication between regions is experiencing inconsistencies.

**Investigation and solution approach needed.**

---

## Performance Optimization Questions (20 points)

### Question P1 (5 points)
Optimize a Spark job that's processing 10TB of data but experiencing frequent OOM errors. The job does complex aggregations and joins.

### Question P2 (5 points)
Design a caching strategy for a real-time feature serving system that needs to handle 100K QPS with sub-10ms latency.

### Question P3 (5 points)
Optimize Kafka producer throughput for a high-volume ingestion pipeline while maintaining message ordering guarantees.

### Question P4 (5 points)
Improve query performance for a data warehouse serving both real-time dashboards and batch analytical workloads.

---

## Detailed Solutions

### Section 1 Solutions: Batch vs Stream Processing

#### Solution 1.1: Latency Characteristics
**Batch Processing (10TB daily dataset):**
- Latency: Hours to complete entire dataset
- Typical workflow: Ingest → Store → Process → Output
- Best for: Historical analysis, complex transformations, cost-sensitive workloads

**Stream Processing:**
- Latency: Milliseconds to seconds per record
- Continuous processing with bounded memory
- Best for: Real-time alerts, live dashboards, immediate responses

**Decision Framework:**
- Use batch when: Cost optimization is primary, complex joins required, eventual consistency acceptable
- Use stream when: Sub-second responses needed, continuous monitoring required, event-driven architecture

#### Solution 1.2: Lambda vs Kappa Architecture

**Lambda Architecture:**
```
Raw Data → Batch Layer (HDFS/S3) → Batch Views
         → Speed Layer (Kafka/Storm) → Real-time Views
         → Serving Layer → Combined Views
```

**Operational Complexities at Petabyte Scale:**
- Dual code paths increase maintenance overhead
- Batch-speed layer synchronization challenges
- Complex deployment and testing procedures

**Kappa Architecture:**
```
Raw Data → Stream Processing (Kafka + Flink/Kafka Streams) → Derived Data
```

**Advantages:**
- Single code path reduces complexity
- Reprocessing through stream replay
- Simpler operational model

**At Petabyte Scale:**
- Kappa requires robust stream processing platform
- Lambda provides better fault isolation
- Choose based on team expertise and operational maturity

#### Solution 1.3: Hybrid Batch-Stream Design

```yaml
Architecture:
  Ingestion:
    - Kafka (7-day retention)
    - Schema Registry for evolution
    - Multi-region replication
  
  Stream Layer:
    - Kafka Streams for fraud detection
    - 100ms processing latency SLA
    - Stateful processing with RocksDB
    
  Batch Layer:
    - Apache Spark on Kubernetes
    - Daily aggregation jobs
    - Historical reprocessing capability
    
  Storage:
    - S3/HDFS for long-term storage
    - Delta Lake for ACID transactions
    - Partitioned by date and region
```

**Implementation:**
```scala
// Stream processing for fraud detection
val fraudDetectionStream = clickStreamEvents
  .groupByKey
  .windowedBy(TimeWindows.of(Duration.ofMinutes(5)))
  .aggregate(new FraudAggregator)
  .filter(_.riskScore > 0.8)
  .to("fraud-alerts")

// Batch processing for daily reports
val dailyReports = spark.read
  .format("delta")
  .load("s3://datalake/clickstream/")
  .where(col("date") === current_date())
  .groupBy("user_segment", "region")
  .agg(sum("revenue"), count("clicks"))
```

#### Solution 1.4: Kafka's Log-Based Storage

**Dual Nature:**
- Stream: Continuous consumption with consumer groups
- Batch: Replay from beginning or specific offsets

**Partition Strategy for 1TB/hour:**
```yaml
Topic Configuration:
  partitions: 1000  # 1GB per partition per hour
  replication_factor: 3
  min_insync_replicas: 2
  retention_ms: 604800000  # 7 days
  segment_ms: 3600000      # 1 hour segments
  
Partitioning Strategy:
  - Hash by user_id for session affinity
  - Consider hot partition mitigation
  - Monitor partition skew metrics
```

**Producer Configuration:**
```properties
# Optimize for throughput
batch.size=65536
linger.ms=100
compression.type=lz4
acks=1
```

#### Solution 1.5: Spark vs Flink Resource Utilization

**Apache Spark (Batch - 100GB/hour):**
```yaml
Resource Pattern:
  - Burst resource usage during job execution
  - High memory for caching and shuffling
  - CPU intensive during transformation phases
  - Network I/O during shuffle operations

Configuration:
  executors: 50
  executor_cores: 4
  executor_memory: 8g
  total_cores: 200
  peak_memory_usage: 400GB
  avg_cpu_utilization: 70%
```

**Apache Flink (Stream - 100GB/hour):**
```yaml
Resource Pattern:
  - Consistent resource usage
  - Lower memory footprint
  - Steady CPU utilization
  - Predictable network patterns

Configuration:
  task_managers: 20
  slots_per_tm: 4
  tm_memory: 4g
  total_slots: 80
  steady_memory_usage: 80GB
  avg_cpu_utilization: 45%
```

#### Solution 1.6: Exactly-Once Semantics

**Kafka Streams Approach:**
```java
Properties config = new Properties();
config.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, 
           StreamsConfig.EXACTLY_ONCE_V2);
config.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

// Transactional processing
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Order> orders = builder.stream("orders");

orders.mapValues(order -> processOrder(order))
      .to("processed-orders");

KafkaStreams streams = new KafkaStreams(builder.build(), config);
streams.start();
```

**Apache Storm Approach:**
```java
// Storm requires manual state management
public class ExactlyOnceOrderBolt implements IRichBolt {
    private Map<String, Long> processedOffsets;
    private TransactionalOutputCollector collector;
    
    @Override
    public void execute(Tuple tuple) {
        String orderId = tuple.getString(0);
        
        // Check if already processed
        if (!isProcessed(orderId)) {
            processOrder(orderId);
            markProcessed(orderId);
            collector.emit(tuple, new Values(result));
        }
        collector.ack(tuple);
    }
}
```

#### Solution 1.7: Backpressure Handling Design

```java
public class AdaptiveBackpressureHandler {
    private final RateLimiter rateLimiter;
    private final MetricRegistry metrics;
    private final CircuitBreaker circuitBreaker;
    
    public void handleBackpressure(StreamContext context) {
        // Monitor queue depth and processing latency
        double queueDepth = context.getQueueDepth();
        double processingLatency = context.getAvgProcessingLatency();
        
        // Adjust rate based on system health
        if (queueDepth > HIGH_WATERMARK || processingLatency > SLA_THRESHOLD) {
            // Reduce ingestion rate
            rateLimiter.setRate(getCurrentRate() * 0.8);
            
            // Enable load shedding for non-critical events
            context.enableLoadShedding(EventPriority.LOW);
            
            // Scale out processing capacity
            context.requestAdditionalResources();
        }
        
        // Circuit breaker for downstream failures
        if (context.getDownstreamErrorRate() > ERROR_THRESHOLD) {
            circuitBreaker.openCircuit();
        }
    }
}
```

#### Solution 1.8: Windowing Strategies Comparison

**Tumbling Windows:**
```sql
-- Good for: Regular reporting, non-overlapping aggregations
SELECT 
  TUMBLE_START(ts, INTERVAL '1' HOUR) as window_start,
  user_id,
  COUNT(*) as events_count
FROM events
GROUP BY TUMBLE(ts, INTERVAL '1' HOUR), user_id
```

**Sliding Windows:**
```sql
-- Good for: Moving averages, trend analysis
SELECT 
  HOP_START(ts, INTERVAL '15' MINUTE, INTERVAL '1' HOUR) as window_start,
  AVG(response_time) as avg_response_time
FROM api_calls
GROUP BY HOP(ts, INTERVAL '15' MINUTE, INTERVAL '1' HOUR)
```

**Session Windows:**
```java
// Good for: User behavior analysis, variable-length activities
KGroupedStream<String, Event> grouped = events.groupByKey();
TimeWindowedKStream<String, Event> sessionized = grouped
    .windowedBy(SessionWindows.with(Duration.ofMinutes(30)));
```

#### Solution 1.9: Watermarks for Trading Platform

```java
public class TradingWatermarkStrategy implements WatermarkStrategy<TradeEvent> {
    
    @Override
    public WatermarkGenerator<TradeEvent> createWatermarkGenerator(
            WatermarkGeneratorSupplier.Context context) {
        return new TradingWatermarkGenerator();
    }
    
    @Override
    public TimestampAssigner<TradeEvent> createTimestampAssigner(
            TimestampAssignerSupplier.Context context) {
        return (event, timestamp) -> event.getTradeTimestamp();
    }
    
    private static class TradingWatermarkGenerator implements WatermarkGenerator<TradeEvent> {
        private long maxTimestamp = Long.MIN_VALUE;
        private final long allowedLateness = Duration.ofSeconds(10).toMillis();
        
        @Override
        public void onEvent(TradeEvent event, long eventTimestamp, WatermarkOutput output) {
            maxTimestamp = Math.max(maxTimestamp, eventTimestamp);
        }
        
        @Override
        public void onPeriodicEmit(WatermarkOutput output) {
            // Conservative watermark for financial data
            output.emitWatermark(new Watermark(maxTimestamp - allowedLateness));
        }
    }
}
```

#### Solution 1.10: Micro-batching vs True Streaming Trade-offs

**Spark Streaming (Micro-batching) - 1M IoT Devices:**

Advantages:
- Better fault tolerance through batch semantics
- Easier integration with Spark ecosystem
- Better handling of burst traffic

Disadvantages:
- Higher latency (minimum batch interval)
- Resource over-provisioning for steady loads
- Complex tuning for optimal batch sizes

```scala
val streamingContext = new StreamingContext(sparkConf, Seconds(5))
val deviceStream = KafkaUtils.createDirectStream[String, DeviceReading](
  streamingContext, ConsumerStrategies.Subscribe[String, DeviceReading](topics, kafkaParams)
)

deviceStream
  .foreachRDD { rdd =>
    rdd.foreachPartition { partition =>
      // Process 5 seconds worth of data per partition
      partition.foreach(processDeviceReading)
    }
  }
```

**Flink (True Streaming) - 1M IoT Devices:**

Advantages:
- Lower latency (milliseconds)
- Better resource efficiency
- True event-time processing

Disadvantages:
- More complex failure recovery
- Steeper learning curve
- State management complexity

```java
DataStream<DeviceReading> deviceStream = env
    .addSource(new FlinkKafkaConsumer<>("device-readings", deserializer, properties))
    .assignTimestampsAndWatermarks(watermarkStrategy);

deviceStream
    .keyBy(DeviceReading::getDeviceId)
    .window(TumblingEventTimeWindows.of(Time.minutes(1)))
    .aggregate(new DeviceAggregateFunction())
    .addSink(new DeviceAlertsSink());
```

---

### Section 2 Solutions: ETL/ELT Patterns

#### Solution 2.1: ETL vs ELT Comparison (500TB historical, 10TB daily)

**ETL Approach:**
```yaml
Architecture:
  - Extract from source systems to staging
  - Transform in dedicated compute cluster
  - Load cleaned data to warehouse
  
Pros:
  - Data quality validation before storage
  - Reduced warehouse storage costs
  - Network bandwidth optimization
  
Cons:
  - Limited transformation flexibility
  - Longer time-to-insight
  - Bottleneck at transformation layer
  
Cost Analysis (Annual):
  - Compute: $2M (dedicated ETL cluster)
  - Storage: $1.2M (only processed data)
  - Network: $800K
  - Total: $4M
```

**ELT Approach:**
```yaml
Architecture:
  - Extract and load raw data to data lake
  - Transform using warehouse compute
  - Multiple transformation layers (bronze → silver → gold)
  
Pros:
  - Faster time-to-insight
  - Schema flexibility
  - Parallel transformation development
  
Cons:
  - Higher storage costs
  - Data quality issues propagate
  - Warehouse resource contention
  
Cost Analysis (Annual):
  - Compute: $1.5M (warehouse compute)
  - Storage: $2.1M (all raw + processed)
  - Network: $1M
  - Total: $4.6M
```

**Recommendation:** Hybrid approach with medallion architecture for 15% cost savings and improved flexibility.

#### Solution 2.2: dbt ELT Pipeline with Lineage

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

SELECT
    order_id,
    customer_id,
    order_date,
    order_status,
    {{ dollars_to_cents('order_total') }} as order_total_cents,
    _fivetran_synced as ingested_at
FROM {{ source('ecommerce', 'orders') }}
WHERE order_date >= '2020-01-01'

-- models/marts/dim_customers.sql
{{ config(materialized='table') }}

SELECT
    customer_id,
    first_name,
    last_name,
    email,
    registration_date,
    {{ calculate_customer_lifetime_value('customer_id') }} as ltv,
    current_timestamp as updated_at
FROM {{ ref('stg_customers') }}

-- models/marts/fct_order_metrics.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='append_new_columns'
) }}

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_total_cents,
    c.customer_segment,
    p.product_category,
    {{ calculate_order_profitability('order_id') }} as profit_margin
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('dim_customers') }} c USING (customer_id)
JOIN {{ ref('stg_products') }} p USING (product_id)

{% if is_incremental() %}
WHERE o.order_date > (SELECT max(order_date) FROM {{ this }})
{% endif %}
```

**Lineage Tracking Configuration:**
```yaml
# dbt_project.yml
models:
  ecommerce:
    staging:
      +docs:
        node_color: "lightblue"
    marts:
      +docs:
        node_color: "green"

# Use dbt docs generate && dbt docs serve for lineage visualization
```

#### Solution 2.3: Incremental Loading with Merge/Upsert

```sql
-- Slowly Changing Dimension (SCD Type 2) implementation
CREATE OR REPLACE PROCEDURE upsert_customer_dimension()
LANGUAGE SQL
AS $$
BEGIN
  -- Stage new and changed records
  CREATE TEMP TABLE customer_changes AS
  SELECT 
    s.*,
    COALESCE(d.customer_key, -1) as existing_key,
    CASE 
      WHEN d.customer_key IS NULL THEN 'INSERT'
      WHEN d.current_flag = 'Y' AND (
        s.first_name != d.first_name OR 
        s.last_name != d.last_name OR 
        s.email != d.email
      ) THEN 'UPDATE'
      ELSE 'NO_CHANGE'
    END as change_type
  FROM staging.customers s
  LEFT JOIN dim_customer d ON s.customer_id = d.customer_id 
    AND d.current_flag = 'Y';
  
  -- Close existing records for updates
  UPDATE dim_customer 
  SET 
    current_flag = 'N',
    effective_end_date = current_date - 1
  WHERE customer_key IN (
    SELECT existing_key 
    FROM customer_changes 
    WHERE change_type = 'UPDATE'
  );
  
  -- Insert new and updated records
  INSERT INTO dim_customer (
    customer_id, first_name, last_name, email,
    effective_start_date, effective_end_date, current_flag
  )
  SELECT 
    customer_id, first_name, last_name, email,
    current_date, '9999-12-31', 'Y'
  FROM customer_changes
  WHERE change_type IN ('INSERT', 'UPDATE');
  
END;
$$;

-- Apache Airflow DAG for daily execution
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

dag = DAG(
    'customer_dimension_upsert',
    schedule_interval='@daily',
    catchup=False
)

upsert_task = PostgresOperator(
    task_id='upsert_customer_dim',
    postgres_conn_id='warehouse',
    sql='CALL upsert_customer_dimension();',
    dag=dag
)
```

#### Solution 2.4: Data Lineage Tracking System

```python
class LineageTracker:
    def __init__(self, metadata_store):
        self.metadata_store = metadata_store
        self.lineage_graph = nx.DiGraph()
    
    def track_transformation(self, transformation_id, inputs, outputs, metadata):
        """Track a single transformation step"""
        
        # Record transformation metadata
        transformation_record = {
            'transformation_id': transformation_id,
            'timestamp': datetime.utcnow(),
            'inputs': inputs,
            'outputs': outputs,
            'transformation_logic': metadata.get('sql_query'),
            'data_profile': metadata.get('data_profile'),
            'execution_stats': metadata.get('execution_stats')
        }
        
        # Store in metadata repository
        self.metadata_store.store_transformation(transformation_record)
        
        # Update lineage graph
        for input_dataset in inputs:
            for output_dataset in outputs:
                self.lineage_graph.add_edge(
                    input_dataset, 
                    output_dataset,
                    transformation=transformation_id,
                    timestamp=datetime.utcnow()
                )
    
    def get_upstream_lineage(self, dataset, max_depth=10):
        """Get all upstream dependencies for a dataset"""
        upstream = []
        
        def dfs(node, depth):
            if depth > max_depth:
                return
            
            predecessors = list(self.lineage_graph.predecessors(node))
            for pred in predecessors:
                upstream.append({
                    'dataset': pred,
                    'transformation': self.lineage_graph[pred][node]['transformation'],
                    'depth': depth
                })
                dfs(pred, depth + 1)
        
        dfs(dataset, 0)
        return upstream
    
    def get_impact_analysis(self, dataset):
        """Get all downstream datasets that would be affected by changes"""
        downstream = []
        
        def dfs(node, depth=0):
            successors = list(self.lineage_graph.successors(node))
            for succ in successors:
                downstream.append({
                    'dataset': succ,
                    'transformation': self.lineage_graph[node][succ]['transformation'],
                    'depth': depth + 1
                })
                dfs(succ, depth + 1)
        
        dfs(dataset)
        return downstream

# Integration with Apache Airflow
class LineageAirflowPlugin(AirflowPlugin):
    name = "lineage_tracker"
    
    def on_task_instance_success(self, task_instance, **kwargs):
        # Extract lineage from task metadata
        inputs = task_instance.task.get_input_datasets()
        outputs = task_instance.task.get_output_datasets()
        
        lineage_tracker.track_transformation(
            transformation_id=f"{task_instance.dag_id}.{task_instance.task_id}",
            inputs=inputs,
            outputs=outputs,
            metadata={
                'sql_query': getattr(task_instance.task, 'sql', None),
                'execution_stats': task_instance.execution_stats
            }
        )
```

#### Solution 2.5: CDC-based ELT with Schema Evolution

```yaml
# Debezium connector configuration
{
  "name": "ecommerce-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.mysql.MySqlConnector",
    "database.hostname": "mysql-source",
    "database.port": "3306",
    "database.user": "debezium",
    "database.password": "password",
    "database.server.id": "184054",
    "database.server.name": "ecommerce",
    "database.include.list": "ecommerce",
    "table.include.list": "ecommerce.orders,ecommerce.customers,ecommerce.products",
    "database.history.kafka.bootstrap.servers": "kafka:9092",
    "database.history.kafka.topic": "schema-changes-ecommerce",
    "schema.history.internal.kafka.bootstrap.servers": "kafka:9092",
    "schema.history.internal.kafka.topic": "ecommerce-schema-history",
    "include.schema.changes": "true",
    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "([^.]+)\\.([^.]+)\\.([^.]+)",
    "transforms.route.replacement": "$3"
  }
}
```

```python
# Schema evolution handler
class SchemaEvolutionHandler:
    def __init__(self, schema_registry_url):
        self.schema_registry = SchemaRegistryClient({'url': schema_registry_url})
        self.compatibility_checker = CompatibilityChecker()
    
    def handle_schema_change(self, event):
        if event['payload']['source']['snapshot'] == 'false':
            table_name = event['payload']['source']['table']
            
            # Extract new schema from DDL
            new_schema = self.extract_schema_from_ddl(event['payload']['ddl'])
            
            # Get current schema from registry
            current_schema = self.schema_registry.get_latest_schema(f"{table_name}-value")
            
            # Check compatibility
            compatibility = self.compatibility_checker.check(current_schema, new_schema)
            
            if compatibility.is_compatible():
                # Register new schema version
                new_version = self.schema_registry.register_schema(
                    f"{table_name}-value", 
                    new_schema
                )
                
                # Update downstream consumer configs
                self.update_consumer_configs(table_name, new_version)
                
                # Trigger schema migration in warehouse
                self.trigger_warehouse_migration(table_name, new_schema)
            else:
                # Handle breaking changes
                self.handle_breaking_change(table_name, compatibility.issues)
    
    def trigger_warehouse_migration(self, table_name, schema):
        """Trigger schema evolution in data warehouse"""
        migration_sql = self.generate_migration_sql(table_name, schema)
        
        # Execute with zero-downtime strategy
        self.execute_online_schema_migration(migration_sql)
```

#### Solution 2.6: Medallion Architecture Implementation

```python
# Bronze Layer - Raw data ingestion
def bronze_layer_ingestion():
    """Ingest raw data with minimal transformation"""
    
    bronze_config = {
        'format': 'delta',
        'mode': 'append',
        'mergeSchema': 'true',
        'path': 's3://datalake/bronze/ecommerce/'
    }
    
    # Stream from Kafka to Bronze
    kafka_stream = (spark
        .readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", "kafka:9092")
        .option("subscribe", "orders,customers,products")
        .option("startingOffsets", "latest")
        .load())
    
    # Minimal parsing - preserve raw data
    bronze_data = kafka_stream.select(
        col("topic").alias("source_topic"),
        col("partition").alias("source_partition"),
        col("offset").alias("source_offset"),
        col("timestamp").alias("ingestion_time"),
        col("value").cast("string").alias("raw_data")
    )
    
    # Write to Bronze with checkpointing
    bronze_stream = (bronze_data
        .writeStream
        .format("delta")
        .option("checkpointLocation", "s3://checkpoints/bronze/")
        .option("path", bronze_config['path'])
        .trigger(processingTime='30 seconds')
        .start())

# Silver Layer - Cleaned and validated data
def silver_layer_processing():
    """Clean, validate, and standardize data"""
    
    # Read from Bronze
    bronze_df = spark.read.format("delta").load("s3://datalake/bronze/ecommerce/")
    
    # Parse JSON and apply data quality rules
    silver_df = bronze_df.select(
        col("source_topic"),
        col("ingestion_time"),
        from_json(col("raw_data"), get_schema(col("source_topic"))).alias("data")
    ).select(
        "*",
        # Data quality validations
        when(col("data.email").rlike("^[^@]+@[^@]+\\.[^@]+$"), True).otherwise(False).alias("email_valid"),
        when(col("data.amount") > 0, True).otherwise(False).alias("amount_valid"),
        # Data standardization
        upper(col("data.country")).alias("country_code"),
        col("data.timestamp").cast("timestamp").alias("event_time")
    ).filter(
        # Filter out invalid records
        col("email_valid") & col("amount_valid")
    )
    
    # Write to Silver with partitioning
    silver_df.write.format("delta").mode("overwrite").partitionBy("country_code", "date").save("s3://datalake/silver/ecommerce/")

# Gold Layer - Business aggregates
def gold_layer_aggregation():
    """Create business-ready aggregated data"""
    
    # Read from Silver
    silver_df = spark.read.format("delta").load("s3://datalake/silver/ecommerce/")
    
    # Business logic aggregations
    daily_metrics = silver_df.groupBy("country_code", "date").agg(
        sum("amount").alias("daily_revenue"),
        count("*").alias("transaction_count"),
        countDistinct("customer_id").alias("active_customers"),
        avg("amount").alias("avg_transaction_value")
    )
    
    # Customer lifetime value calculation
    customer_ltv = silver_df.groupBy("customer_id").agg(
        sum("amount").alias("total_spent"),
        count("*").alias("total_transactions"),
        datediff(max("event_time"), min("event_time")).alias("customer_tenure_days")
    )
    
    # Write to Gold layer
    daily_metrics.write.format("delta").mode("overwrite").save("s3://datalake/gold/daily_metrics/")
    customer_ltv.write.format("delta").mode("overwrite").save("s3://datalake/gold/customer_ltv/")
```

#### Solution 2.7: Idempotent ETL Transformations

```python
class IdempotentETLProcessor:
    def __init__(self, checkpoint_store):
        self.checkpoint_store = checkpoint_store
        
    def process_batch_idempotently(self, batch_id, input_data):
        """Process batch with idempotency guarantees"""
        
        # Check if batch already processed
        if self.checkpoint_store.is_processed(batch_id):
            logging.info(f"Batch {batch_id} already processed, skipping")
            return self.checkpoint_store.get_result(batch_id)
        
        # Process with transaction semantics
        try:
            with self.checkpoint_store.transaction():
                # Mark as processing
                self.checkpoint_store.mark_processing(batch_id)
                
                # Perform transformations
                result = self.transform_data(input_data)
                
                # Validate output
                self.validate_output(result)
                
                # Store result atomically
                output_path = self.store_result(batch_id, result)
                
                # Mark as completed
                self.checkpoint_store.mark_completed(batch_id, output_path)
                
                return result
                
        except Exception as e:
            # Mark as failed and cleanup
            self.checkpoint_store.mark_failed(batch_id, str(e))
            self.cleanup_partial_results(batch_id)
            raise
    
    def transform_data(self, data):
        """Deterministic transformations"""
        
        # Use deterministic UUIDs based on content
        def generate_deterministic_id(row):
            content = f"{row['customer_id']}-{row['order_date']}-{row['amount']}"
            return str(uuid.uuid5(uuid.NAMESPACE_DNS, content))
        
        # Apply transformations
        transformed = data.withColumn(
            "order_uuid", 
            generate_deterministic_id(struct("customer_id", "order_date", "amount"))
        ).withColumn(
            "processed_timestamp",
            lit(datetime.utcnow())  # Fixed timestamp for idempotency
        )
        
        return transformed

# Kafka Streams idempotent processor
@Component
class OrderProcessingService {
    
    @KafkaListener(topics = "orders")
    public void processOrder(@Payload OrderEvent event, 
                           @Header(KafkaHeaders.RECEIVED_MESSAGE_KEY) String key) {
        
        // Generate idempotency key from message content
        String idempotencyKey = generateIdempotencyKey(event);
        
        // Check if already processed
        if (processedMessages.containsKey(idempotencyKey)) {
            log.info("Message {} already processed", idempotencyKey);
            return;
        }
        
        try {
            // Process with database transaction
            @Transactional
            ProcessingResult result = processOrderEvent(event);
            
            // Store result and mark as processed atomically
            orderRepository.save(result.getOrder());
            processedMessages.put(idempotencyKey, result);
            
            // Publish downstream event
            eventPublisher.publishOrderProcessed(result);
            
        } catch (Exception e) {
            log.error("Failed to process order {}", event.getOrderId(), e);
            // Dead letter queue handling
            dlqPublisher.publish(event, e.getMessage());
        }
    }
    
    private String generateIdempotencyKey(OrderEvent event) {
        // Content-based key generation
        return DigestUtils.sha256Hex(
            event.getOrderId() + 
            event.getCustomerId() + 
            event.getAmount() + 
            event.getTimestamp()
        );
    }
}
```

#### Solution 2.8: Multi-Tenant ETL System

```yaml
# Multi-tenant ETL architecture
apiVersion: argoproj.io/v1alpha1
kind: WorkflowTemplate
metadata:
  name: multi-tenant-etl
spec:
  entrypoint: etl-pipeline
  arguments:
    parameters:
    - name: tenant-id
    - name: data-source
    - name: output-format
  
  templates:
  - name: etl-pipeline
    dag:
      tasks:
      - name: validate-tenant
        template: tenant-validation
        arguments:
          parameters:
          - name: tenant-id
            value: "{{workflow.parameters.tenant-id}}"
      
      - name: extract-data
        template: data-extraction
        dependencies: [validate-tenant]
        arguments:
          parameters:
          - name: tenant-id
            value: "{{workflow.parameters.tenant-id}}"
          - name: data-source
            value: "{{workflow.parameters.data-source}}"
      
      - name: transform-data
        template: data-transformation
        dependencies: [extract-data]
        arguments:
          parameters:
          - name: tenant-id
            value: "{{workflow.parameters.tenant-id}}"
      
      - name: load-data
        template: data-loading
        dependencies: [transform-data]
        arguments:
          parameters:
          - name: tenant-id
            value: "{{workflow.parameters.tenant-id}}"
          - name: output-format
            value: "{{workflow.parameters.output-format}}"
```

```python
class MultiTenantETLOrchestrator:
    def __init__(self):
        self.resource_manager = KubernetesResourceManager()
        self.tenant_config_store = TenantConfigStore()
        self.cost_tracker = CostTracker()
    
    def execute_tenant_pipeline(self, tenant_id, pipeline_config):
        """Execute ETL pipeline for specific tenant with resource isolation"""
        
        # Get tenant configuration and limits
        tenant_config = self.tenant_config_store.get_config(tenant_id)
        resource_limits = tenant_config.get_resource_limits()
        
        # Create isolated namespace
        namespace = f"tenant-{tenant_id}-{uuid.uuid4().hex[:8]}"
        self.resource_manager.create_namespace(namespace, resource_limits)
        
        try:
            # Deploy tenant-specific resources
            spark_cluster = self.deploy_spark_cluster(namespace, tenant_config)
            
            # Execute pipeline with tenant isolation
            pipeline_result = self.execute_pipeline(
                spark_cluster=spark_cluster,
                tenant_id=tenant_id,
                config=pipeline_config,
                namespace=namespace
            )
            
            # Track resource usage and costs
            resource_usage = self.resource_manager.get_usage_metrics(namespace)
            self.cost_tracker.record_usage(tenant_id, resource_usage)
            
            return pipeline_result
            
        finally:
            # Cleanup resources
            self.resource_manager.cleanup_namespace(namespace)
    
    def execute_pipeline(self, spark_cluster, tenant_id, config, namespace):
        """Execute ETL pipeline with tenant-specific transformations"""
        
        # Load tenant-specific transformation rules
        transformation_rules = self.tenant_config_store.get_transformation_rules(tenant_id)
        
        # Create Spark session with tenant isolation
        spark = SparkSession.builder \
            .appName(f"ETL-{tenant_id}") \
            .config("spark.kubernetes.namespace", namespace) \
            .config("spark.kubernetes.executor.deleteOnTermination", "true") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        # Apply tenant-specific data masking
        def apply_data_masking(df, tenant_id):
            masking_rules = self.tenant_config_store.get_masking_rules(tenant_id)
            
            for rule in masking_rules:
                if rule.type == 'hash':
                    df = df.withColumn(rule.column, sha2(col(rule.column), 256))
                elif rule.type == 'encrypt':
                    df = df.withColumn(rule.column, encrypt_udf(col(rule.column)))
                elif rule.type == 'redact':
                    df = df.withColumn(rule.column, lit('***REDACTED***'))
            
            return df
        
        # Execute transformations
        raw_data = spark.read.format(config.input_format).load(config.input_path)
        
        # Apply tenant-specific transformations
        transformed_data = raw_data
        for rule in transformation_rules:
            transformed_data = transformed_data.transform(rule.apply)
        
        # Apply data masking based on tenant permissions
        masked_data = apply_data_masking(transformed_data, tenant_id)
        
        # Write to tenant-specific location
        output_path = f"s3://tenant-data/{tenant_id}/processed/{datetime.now().strftime('%Y/%m/%d')}"
        masked_data.write.format(config.output_format).mode("overwrite").save(output_path)
        
        return {
            'tenant_id': tenant_id,
            'output_path': output_path,
            'records_processed': masked_data.count(),
            'execution_time': time.time() - start_time
        }
```

#### Solution 2.9: Data Quality Gates in ELT

```python
class DataQualityGateSystem:
    def __init__(self):
        self.quality_rules = QualityRuleEngine()
        self.alert_manager = AlertManager()
        self.quarantine_store = QuarantineStore()
    
    def validate_data_quality(self, dataset_name, dataframe, quality_config):
        """Comprehensive data quality validation"""
        
        validation_results = []
        
        # Completeness checks
        completeness_results = self.check_completeness(dataframe, quality_config)
        validation_results.extend(completeness_results)
        
        # Accuracy checks
        accuracy_results = self.check_accuracy(dataframe, quality_config)
        validation_results.extend(accuracy_results)
        
        # Consistency checks
        consistency_results = self.check_consistency(dataframe, quality_config)
        validation_results.extend(consistency_results)
        
        # Timeliness checks
        timeliness_results = self.check_timeliness(dataframe, quality_config)
        validation_results.extend(timeliness_results)
        
        # Calculate overall quality score
        quality_score = self.calculate_quality_score(validation_results)
        
        # Determine action based on quality gates
        action = self.determine_action(quality_score, quality_config.thresholds)
        
        return DataQualityResult(
            dataset_name=dataset_name,
            quality_score=quality_score,
            validation_results=validation_results,
            action=action,
            timestamp=datetime.utcnow()
        )
    
    def check_completeness(self, df, config):
        """Check for missing values and null percentages"""
        results = []
        
        for column in config.required_columns:
            null_count = df.filter(col(column).isNull()).count()
            total_count = df.count()
            null_percentage = (null_count / total_count) * 100
            
            threshold = config.completeness_thresholds.get(column, 5.0)
            
            results.append(QualityCheck(
                rule_name=f"completeness_{column}",
                metric_value=null_percentage,
                threshold=threshold,
                passed=null_percentage <= threshold,
                details=f"{null_count} null values out of {total_count} records"
            ))
        
        return results
    
    def check_accuracy(self, df, config):
        """Validate data accuracy using business rules"""
        results = []
        
        # Range validation
        for column, range_config in config.range_validations.items():
            out_of_range_count = df.filter(
                ~col(column).between(range_config.min_value, range_config.max_value)
            ).count()
            
            total_count = df.count()
            error_percentage = (out_of_range_count / total_count) * 100
            
            results.append(QualityCheck(
                rule_name=f"range_validation_{column}",
                metric_value=error_percentage,
                threshold=range_config.max_error_percentage,
                passed=error_percentage <= range_config.max_error_percentage
            ))
        
        # Pattern validation (regex)
        for column, pattern_config in config.pattern_validations.items():
            invalid_count = df.filter(
                ~col(column).rlike(pattern_config.pattern)
            ).count()
            
            total_count = df.count()
            error_percentage = (invalid_count / total_count) * 100
            
            results.append(QualityCheck(
                rule_name=f"pattern_validation_{column}",
                metric_value=error_percentage,
                threshold=pattern_config.max_error_percentage,
                passed=error_percentage <= pattern_config.max_error_percentage
            ))
        
        return results
    
    def quarantine_bad_records(self, df, validation_results, dataset_name):
        """Quarantine records that fail quality checks"""
        
        quarantine_conditions = []
        
        # Build quarantine conditions from failed validations
        for result in validation_results:
            if not result.passed:
                if result.rule_name.startswith('completeness_'):
                    column = result.rule_name.replace('completeness_', '')
                    quarantine_conditions.append(col(column).isNull())
                elif result.rule_name.startswith('range_validation_'):
                    column = result.rule_name.replace('range_validation_', '')
                    range_config = config.range_validations[column]
                    quarantine_conditions.append(
                        ~col(column).between(range_config.min_value, range_config.max_value)
                    )
        
        if quarantine_conditions:
            # Identify bad records
            bad_records = df.filter(reduce(lambda x, y: x | y, quarantine_conditions))
            
            # Add quarantine metadata
            quarantined_data = bad_records.withColumn(
                "quarantine_timestamp", current_timestamp()
            ).withColumn(
                "quarantine_reason", lit("Failed data quality validation")
            ).withColumn(
                "dataset_name", lit(dataset_name)
            )
            
            # Store in quarantine
            self.quarantine_store.store_quarantined_data(quarantined_data, dataset_name)
            
            # Return clean data
            clean_data = df.filter(~reduce(lambda x, y: x | y, quarantine_conditions))
            return clean_data
        
        return df
```

#### Solution 2.10: Columnar Format Comparison

```python
# Performance comparison framework
class ColumnarFormatBenchmark:
    def __init__(self, test_data_path, formats=['parquet', 'orc', 'delta']):
        self.test_data_path = test_data_path
        self.formats = formats
        self.results = {}
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive performance tests across all formats"""
        
        # Test scenarios
        scenarios = [
            self.test_compression_ratio,
            self.test_write_performance,
            self.test_read_performance,
            self.test_predicate_pushdown,
            self.test_schema_evolution,
            self.test_concurrent_reads,
            self.test_acid_operations
        ]
        
        for scenario in scenarios:
            print(f"Running {scenario.__name__}...")
            scenario_results = scenario()
            self.results[scenario.__name__] = scenario_results
        
        return self.generate_comparison_report()
    
    def test_compression_ratio(self):
        """Compare compression ratios across formats"""
        results = {}
        
        # Load test dataset (10GB e-commerce data)
        test_data = spark.read.parquet(self.test_data_path)
        
        for format_name in self.formats:
            start_time = time.time()
            
            if format_name == 'parquet':
                test_data.write.mode('overwrite').option('compression', 'snappy').parquet(f'/tmp/{format_name}_test')
            elif format_name == 'orc':
                test_data.write.mode('overwrite').option('compression', 'zlib').orc(f'/tmp/{format_name}_test')
            elif format_name == 'delta':
                test_data.write.mode('overwrite').format('delta').save(f'/tmp/{format_name}_test')
            
            # Measure compressed size
            compressed_size = self.get_directory_size(f'/tmp/{format_name}_test')
            original_size = self.get_directory_size(self.test_data_path)
            compression_ratio = original_size / compressed_size
            
            results[format_name] = {
                'compressed_size_mb': compressed_size / (1024 * 1024),
                'compression_ratio': compression_ratio,
                'write_time_seconds': time.time() - start_time
            }
        
        return results
    
    def test_query_performance(self):
        """Test query performance across different patterns"""
        
        queries = {
            'full_scan': "SELECT COUNT(*) FROM table",
            'filtered_scan': "SELECT * FROM table WHERE date >= '2023-01-01'",
            'aggregation': "SELECT customer_segment, SUM(revenue) FROM table GROUP BY customer_segment",
            'join_operation': """
                SELECT o.order_id, c.customer_name, SUM(o.amount)
                FROM orders o JOIN customers c ON o.customer_id = c.customer_id
                GROUP BY o.order_id, c.customer_name
            """
        }
        
        results = {}
        
        for format_name in self.formats:
            format_results = {}
            
            for query_name, query_sql in queries.items():
                # Create temporary view
                if format_name == 'parquet':
                    df = spark.read.parquet(f'/tmp/{format_name}_test')
                elif format_name == 'orc':
                    df = spark.read.orc(f'/tmp/{format_name}_test')
                elif format_name == 'delta':
                    df = spark.read.format('delta').load(f'/tmp/{format_name}_test')
                
                df.createOrReplaceTempView('table')
                
                # Run query multiple times and average
                execution_times = []
                for i in range(3):
                    start_time = time.time()
                    spark.sql(query_sql).collect()
                    execution_times.append(time.time() - start_time)
                
                format_results[query_name] = {
                    'avg_execution_time': sum(execution_times) / len(execution_times),
                    'min_execution_time': min(execution_times),
                    'max_execution_time': max(execution_times)
                }
            
            results[format_name] = format_results
        
        return results

# Example benchmark results
benchmark_results = {
    'compression_ratio': {
        'parquet': {'compression_ratio': 4.2, 'compressed_size_mb': 2380},
        'orc': {'compression_ratio': 4.6, 'compressed_size_mb': 2174},
        'delta': {'compression_ratio': 4.1, 'compressed_size_mb': 2439}
    },
    'query_performance': {
        'parquet': {
            'full_scan': {'avg_execution_time': 12.3},
            'filtered_scan': {'avg_execution_time': 3.8},
            'aggregation': {'avg_execution_time': 8.7}
        },
        'orc': {
            'full_scan': {'avg_execution_time': 11.9},
            'filtered_scan': {'avg_execution_time': 3.2},
            'aggregation': {'avg_execution_time': 8.1}
        },
        'delta': {
            'full_scan': {'avg_execution_time': 12.8},
            'filtered_scan': {'avg_execution_time': 2.9},  # Better due to data skipping
            'aggregation': {'avg_execution_time': 9.1}
        }
    }
}

# Recommendation matrix
format_recommendations = {
    'parquet': {
        'best_for': ['Analytics workloads', 'Data science', 'Cross-platform compatibility'],
        'avoid_for': ['Frequent updates', 'ACID requirements'],
        'compression': 'Excellent',
        'read_performance': 'Very Good',
        'write_performance': 'Good',
        'ecosystem_support': 'Excellent'
    },
    'orc': {
        'best_for': ['Hive workloads', 'Complex nested data', 'Predicate pushdown'],
        'avoid_for': ['Spark-centric workflows', 'Real-time updates'],
        'compression': 'Excellent',
        'read_performance': 'Excellent',
        'write_performance': 'Good',
        'ecosystem_support': 'Good'
    },
    'delta': {
        'best_for': ['ACID transactions', 'Time travel', 'Streaming + batch'],
        'avoid_for': ['Cost-sensitive scenarios', 'Simple analytics'],
        'compression': 'Good',
        'read_performance': 'Very Good',
        'write_performance': 'Excellent',
        'ecosystem_support': 'Growing'
    }
}
```

---

### Section 3 Solutions: Data Quality and Validation

#### Solution 3.1: Real-time Data Quality Monitoring (1TB/hour Financial)

```python
class RealTimeDataQualityMonitor:
    def __init__(self, kafka_config, alert_config):
        self.kafka_config = kafka_config
        self.alert_manager = AlertManager(alert_config)
        self.metrics_collector = MetricsCollector()
        self.quality_rules = self.load_financial_quality_rules()
    
    def start_monitoring(self):
        """Start real-time monitoring of financial transaction stream"""
        
        # Kafka Streams topology for quality monitoring
        streams_config = {
            'application.id': 'financial-quality-monitor',
            'bootstrap.servers': self.kafka_config['brokers'],
            'default.key.serde': 'org.apache.kafka.common.serialization.Serdes$StringSerde',
            'default.value.serde': 'io.confluent.kafka.streams.serdes.avro.SpecificAvroSerde',
            'schema.registry.url': self.kafka_config['schema_registry'],
            'processing.guarantee': 'exactly_once_v2'
        }
        
        builder = StreamsBuilder()
        
        # Main transaction stream
        transactions = builder.stream('financial-transactions')
        
        # Real-time quality validation
        validated_transactions = transactions.mapValues(self.validate_transaction)
        
        # Split into valid and invalid streams
        valid_transactions = validated_transactions.filter(
            lambda key, value: value.quality_score >= 0.95
        )
        
        invalid_transactions = validated_transactions.filterNot(
            lambda key, value: value.quality_score >= 0.95
        )
        
        # Aggregate quality metrics in tumbling windows
        quality_metrics = validated_transactions.groupByKey().windowedBy(
            TimeWindows.of(Duration.ofMinutes(1))
        ).aggregate(
            QualityMetricsAggregator::new,
            (key, value, aggregate) -> aggregate.add(value),
            Materialized.as('quality-metrics-store')
        )
        
        # Real-time alerting on quality degradation
        quality_metrics.toStream().filter(
            lambda windowed_key, metrics: metrics.quality_score < 0.90
        ).foreach(self.trigger_quality_alert)
        
        # Route invalid transactions to DLQ
        invalid_transactions.to('financial-transactions-dlq')
        
        # Route valid transactions downstream
        valid_transactions.mapValues(lambda tx: tx.transaction).to('validated-financial-transactions')
        
        # Start the streams application
        streams = KafkaStreams(builder.build(), StreamsConfig(streams_config))
        streams.start()
        
        return streams
    
    def validate_transaction(self, transaction):
        """Comprehensive real-time transaction validation"""
        
        quality_checks = []
        quality_score = 1.0
        
        # Amount validation
        if transaction.amount <= 0:
            quality_checks.append('invalid_amount')
            quality_score -= 0.3
        elif transaction.amount > 1000000:  # $1M limit
            quality_checks.append('suspicious_amount')
            quality_score -= 0.1
        
        # Account validation
        if not self.validate_account_format(transaction.from_account):
            quality_checks.append('invalid_from_account')
            quality_score -= 0.4
        
        if not self.validate_account_format(transaction.to_account):
            quality_checks.append('invalid_to_account')
            quality_score -= 0.4
        
        # Timestamp validation
        now = datetime.utcnow()
        tx_time = datetime.fromisoformat(transaction.timestamp)
        
        if tx_time > now + timedelta(minutes=5):
            quality_checks.append('future_timestamp')
            quality_score -= 0.5
        elif tx_time < now - timedelta(hours=24):
            quality_checks.append('old_timestamp')
            quality_score -= 0.2
        
        # Currency validation
        if transaction.currency not in ['USD', 'EUR', 'GBP', 'JPY']:
            quality_checks.append('invalid_currency')
            quality_score -= 0.3
        
        # Business rule validation
        if transaction.transaction_type not in ['TRANSFER', 'PAYMENT', 'DEPOSIT', 'WITHDRAWAL']:
            quality_checks.append('invalid_transaction_type')
            quality_score -= 0.3
        
        # Duplicate detection (using recent transaction cache)
        if self.is_potential_duplicate(transaction):
            quality_checks.append('potential_duplicate')
            quality_score -= 0.6
        
        return ValidationResult(
            transaction=transaction,
            quality_score=max(0.0, quality_score),
            quality_checks=quality_checks,
            validation_timestamp=datetime.utcnow()
        )
    
    def trigger_quality_alert(self, windowed_key, quality_metrics):
        """Trigger alerts for quality degradation"""
        
        window_start = windowed_key.window().start()
        window_end = windowed_key.window().end()
        
        alert = QualityAlert(
            severity='HIGH' if quality_metrics.quality_score < 0.8 else 'MEDIUM',
            message=f"Quality score dropped to {quality_metrics.quality_score:.2f}",
            window_start=window_start,
            window_end=window_end,
            metrics=quality_metrics.to_dict(),
            timestamp=datetime.utcnow()
        )
        
        self.alert_manager.send_alert(alert)
        
        # Auto-remediation for known issues
        if 'high_duplicate_rate' in quality_metrics.primary_issues:
            self.initiate_duplicate_investigation(quality_metrics)

# Kafka Streams aggregator for quality metrics
class QualityMetricsAggregator:
    def __init__(self):
        self.total_transactions = 0
        self.quality_scores = []
        self.issue_counts = defaultdict(int)
    
    def add(self, validation_result):
        self.total_transactions += 1
        self.quality_scores.append(validation_result.quality_score)
        
        for issue in validation_result.quality_checks:
            self.issue_counts[issue] += 1
        
        return self
    
    @property
    def quality_score(self):
        return sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 1.0
    
    @property
    def primary_issues(self):
        return [issue for issue, count in self.issue_counts.items() 
                if count / self.total_transactions > 0.05]  # 5% threshold
```

#### Solution 3.2: Statistical Outlier Detection with Concept Drift

```python
class AdaptiveOutlierDetector:
    def __init__(self, window_size=1000, sensitivity=0.05):
        self.window_size = window_size
        self.sensitivity = sensitivity
        self.seasonal_models = {}
        self.drift_detector = ConceptDriftDetector()
        
    def detect_outliers_with_drift_handling(self, time_series_data):
        """Detect outliers while handling concept drift and seasonality"""
        
        results = []
        
        for timestamp, value, metadata in time_series_data:
            # Update drift detector
            drift_detected = self.drift_detector.update(value, timestamp)
            
            if drift_detected:
                # Reset models on concept drift
                self.handle_concept_drift(timestamp)
            
            # Get seasonal context
            seasonal_context = self.get_seasonal_context(timestamp)
            
            # Multi-method outlier detection
            outlier_scores = self.calculate_outlier_scores(
                value, timestamp, seasonal_context
            )
            
            # Ensemble scoring
            final_score = self.ensemble_outlier_score(outlier_scores)
            
            # Adaptive threshold based on recent false positive rate
            threshold = self.get_adaptive_threshold(seasonal_context)
            
            is_outlier = final_score > threshold
            
            # False positive mitigation
            if is_outlier:
                is_outlier = self.validate_outlier(
                    value, timestamp, outlier_scores, metadata
                )
            
            results.append(OutlierResult(
                timestamp=timestamp,
                value=value,
                outlier_score=final_score,
                is_outlier=is_outlier,
                detection_methods=outlier_scores,
                seasonal_context=seasonal_context
            ))
            
            # Update models with validated data
            if not is_outlier:
                self.update_models(value, timestamp, seasonal_context)
        
        return results
    
    def calculate_outlier_scores(self, value, timestamp, seasonal_context):
        """Multiple outlier detection methods for robustness"""
        
        scores = {}
        
        # 1. Z-score with seasonal adjustment
        seasonal_mean = seasonal_context.get('mean', self.global_mean)
        seasonal_std = seasonal_context.get('std', self.global_std)
        
        if seasonal_std > 0:
            z_score = abs(value - seasonal_mean) / seasonal_std
            scores['z_score'] = min(z_score / 3.0, 1.0)  # Normalize to 0-1
        
        # 2. Isolation Forest score
        if hasattr(self, 'isolation_forest') and self.isolation_forest:
            iso_score = self.isolation_forest.decision_function([[value]])[0]
            scores['isolation_forest'] = max(0, -iso_score)  # Convert to positive score
        
        # 3. Local Outlier Factor (LOF)
        if len(self.recent_values) >= 20:
            lof_score = self.calculate_lof_score(value)
            scores['lof'] = min(lof_score / 2.0, 1.0)
        
        # 4. LSTM Autoencoder reconstruction error
        if hasattr(self, 'autoencoder_model'):
            reconstruction_error = self.calculate_reconstruction_error(value, timestamp)
            scores['autoencoder'] = min(reconstruction_error / self.max_reconstruction_error, 1.0)
        
        # 5. Seasonal decomposition residual analysis
        if seasonal_context.get('has_seasonal_pattern'):
            residual_score = self.calculate_seasonal_residual_score(value, timestamp)
            scores['seasonal_residual'] = residual_score
        
        return scores
    
    def ensemble_outlier_score(self, method_scores):
        """Weighted ensemble of different outlier detection methods"""
        
        # Dynamic weights based on method reliability
        weights = {
            'z_score': 0.2,
            'isolation_forest': 0.3,
            'lof': 0.2,
            'autoencoder': 0.25,
            'seasonal_residual': 0.15
        }
        
        # Adjust weights based on recent performance
        for method in method_scores:
            if hasattr(self, f'{method}_recent_accuracy'):
                accuracy = getattr(self, f'{method}_recent_accuracy')
                weights[method] *= (0.5 + accuracy)  # Scale weights by accuracy
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {k: v/total_weight for k, v in weights.items()}
        
        # Calculate weighted average
        ensemble_score = sum(
            normalized_weights.get(method, 0) * score 
            for method, score in method_scores.items()
        )
        
        return ensemble_score
    
    def validate_outlier(self, value, timestamp, scores, metadata):
        """Reduce false positives through contextual validation"""
        
        # Check if it's a known business event
        if self.is_known_business_event(timestamp, metadata):
            return False
        
        # Check if it's part of a legitimate trend
        if self.is_trending_pattern(value, timestamp):
            return False
        
        # Cross-validate with external data sources
        if hasattr(self, 'external_validator'):
            external_validation = self.external_validator.validate(value, timestamp, metadata)
            if not external_validation.is_anomalous:
                return False
        
        # Check confidence level
        confidence = self.calculate_detection_confidence(scores)
        return confidence > 0.8
    
    def get_adaptive_threshold(self, seasonal_context):
        """Adaptive threshold based on recent false positive rates"""
        
        base_threshold = 0.7
        
        # Adjust based on recent false positive rate
        recent_fp_rate = self.calculate_recent_false_positive_rate()
        if recent_fp_rate > 0.1:  # Too many false positives
            base_threshold += 0.1
        elif recent_fp_rate < 0.05:  # Too few detections
            base_threshold -= 0.05
        
        # Adjust based on business criticality
        if seasonal_context.get('business_critical_period'):
            base_threshold -= 0.1  # More sensitive during critical periods
        
        # Adjust based on data quality
        data_quality_score = seasonal_context.get('data_quality_score', 1.0)
        base_threshold += (1.0 - data_quality_score) * 0.2
        
        return max(0.5, min(0.9, base_threshold))

class ConceptDriftDetector:
    """Detect concept drift in time series data"""
    
    def __init__(self, window_size=100, drift_threshold=0.05):
        self.window_size = window_size
        self.drift_threshold = drift_threshold
        self.reference_window = []
        self.current_window = []
        self.drift_history = []
    
    def update(self, value, timestamp):
        """Update detector and return True if drift detected"""
        
        self.current_window.append((value, timestamp))
        
        if len(self.current_window) > self.window_size:
            self.current_window.pop(0)
        
        # Check for drift when windows are full
        if len(self.reference_window) == self.window_size and len(self.current_window) == self.window_size:
            drift_detected = self.detect_drift()
            
            if drift_detected:
                # Update reference window
                self.reference_window = self.current_window.copy()
                self.drift_history.append(timestamp)
                return True
        
        # Initialize reference window
        if len(self.reference_window) < self.window_size:
            self.reference_window.append((value, timestamp))
        
        return False
    
    def detect_drift(self):
        """Statistical tests for concept drift detection"""
        
        ref_values = [v for v, t in self.reference_window]
        cur_values = [v for v, t in self.current_window]
        
        # Kolmogorov-Smirnov test
        ks_stat, ks_p_value = kstest(ref_values, cur_values)
        
        # Mann-Whitney U test
        mw_stat, mw_p_value = mannwhitneyu(ref_values, cur_values)
        
        # Combined decision
        return (ks_p_value < self.drift_threshold) or (mw_p_value < self.drift_threshold)
```

#### Solution 3.3: Data Quality Scorecard System

```python
class DataQualityScorecard:
    def __init__(self):
        self.dimensions = {
            'completeness': CompletenessAnalyzer(),
            'accuracy': AccuracyAnalyzer(),
            'consistency': ConsistencyAnalyzer(),
            'timeliness': TimelinessAnalyzer(),
            'validity': ValidityAnalyzer(),
            'uniqueness': UniquenessAnalyzer()
        }
        self.weights = self.load_dimension_weights()
    
    def generate_scorecard(self, dataset_name, dataframe, reference_data=None):
        """Generate comprehensive data quality scorecard"""
        
        scorecard = DataQualityScorecard()
        dimension_scores = {}
        
        for dimension_name, analyzer in self.dimensions.items():
            print(f"Analyzing {dimension_name}...")
            
            dimension_result = analyzer.analyze(
                dataframe, 
                reference_data=reference_data,
                dataset_name=dataset_name
            )
            
            dimension_scores[dimension_name] = dimension_result
        
        # Calculate weighted overall score
        overall_score = self.calculate_overall_score(dimension_scores)
        
        # Generate insights and recommendations
        insights = self.generate_insights(dimension_scores)
        recommendations = self.generate_recommendations(dimension_scores)
        
        return QualityScorecard(
            dataset_name=dataset_name,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            insights=insights,
            recommendations=recommendations,
            generated_at=datetime.utcnow()
        )
    
    def calculate_overall_score(self, dimension_scores):
        """Calculate weighted overall quality score"""
        
        weighted_sum = 0
        total_weight = 0
        
        for dimension, result in dimension_scores.items():
            weight = self.weights.get(dimension, 1.0)
            weighted_sum += result.score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0

class CompletenessAnalyzer:
    def analyze(self, df, **kwargs):
        """Analyze data completeness across all columns"""
        
        total_records = df.count()
        completeness_results = {}
        
        for column in df.columns:
            null_count = df.filter(col(column).isNull() | (col(column) == "")).count()
            completeness_rate = 1 - (null_count / total_records)
            
            completeness_results[column] = {
                'completeness_rate': completeness_rate,
                'null_count': null_count,
                'total_records': total_records
            }
        
        # Overall completeness score
        overall_completeness = sum(
            result['completeness_rate'] for result in completeness_results.values()
        ) / len(completeness_results) if completeness_results else 0
        
        return DimensionResult(
            dimension='completeness',
            score=overall_completeness,
            details=completeness_results,
            issues=self.identify_completeness_issues(completeness_results)
        )
    
    def identify_completeness_issues(self, results):
        """Identify specific completeness issues"""
        issues = []
        
        for column, result in results.items():
            if result['completeness_rate'] < 0.9:
                severity = 'high' if result['completeness_rate'] < 0.7 else 'medium'
                issues.append({
                    'type': 'low_completeness',
                    'column': column,
                    'completeness_rate': result['completeness_rate'],
                    'severity': severity,
                    'recommendation': f"Investigate data source for {column} to reduce missing values"
                })
        
        return issues

class AccuracyAnalyzer:
    def analyze(self, df, reference_data=None, **kwargs):
        """Analyze data accuracy against business rules and reference data"""
        
        accuracy_checks = []
        
        # Business rule validations
        business_rules = self.get_business_rules(kwargs.get('dataset_name'))
        
        for rule in business_rules:
            violation_count = df.filter(~expr(rule.condition)).count()
            total_count = df.count()
            accuracy_rate = 1 - (violation_count / total_count)
            
            accuracy_checks.append({
                'rule_name': rule.name,
                'accuracy_rate': accuracy_rate,
                'violations': violation_count,
                'rule_description': rule.description
            })
        
        # Reference data comparison (if available)
        if reference_data:
            ref_comparison = self.compare_with_reference(df, reference_data)
            accuracy_checks.extend(ref_comparison)
        
        # Statistical accuracy checks
        statistical_checks = self.perform_statistical_accuracy_checks(df)
        accuracy_checks.extend(statistical_checks)
        
        # Calculate overall accuracy score
        overall_accuracy = sum(
            check['accuracy_rate'] for check in accuracy_checks
        ) / len(accuracy_checks) if accuracy_checks else 1.0
        
        return DimensionResult(
            dimension='accuracy',
            score=overall_accuracy,
            details=accuracy_checks,
            issues=self.identify_accuracy_issues(accuracy_checks)
        )

class ConsistencyAnalyzer:
    def analyze(self, df, **kwargs):
        """Analyze internal consistency and cross-field relationships"""
        
        consistency_checks = []
        
        # Cross-field consistency
        cross_field_rules = [
            ('start_date', 'end_date', 'start_date <= end_date'),
            ('price', 'discount_price', 'discount_price <= price'),
            ('quantity', 'total_amount', 'quantity * unit_price = total_amount')
        ]
        
        for field1, field2, rule in cross_field_rules:
            if field1 in df.columns and field2 in df.columns:
                violations = df.filter(~expr(rule.replace(field1, f'`{field1}`').replace(field2, f'`{field2}`'))).count()
                total = df.count()
                consistency_rate = 1 - (violations / total)
                
                consistency_checks.append({
                    'check_name': f'{field1}_{field2}_consistency',
                    'consistency_rate': consistency_rate,
                    'violations': violations,
                    'rule': rule
                })
        
        # Format consistency
        format_consistency = self.check_format_consistency(df)
        consistency_checks.extend(format_consistency)
        
        # Value consistency across similar fields
        value_consistency = self.check_value_consistency(df)
        consistency_checks.extend(value_consistency)
        
        overall_consistency = sum(
            check['consistency_rate'] for check in consistency_checks
        ) / len(consistency_checks) if consistency_checks else 1.0
        
        return DimensionResult(
            dimension='consistency',
            score=overall_consistency,
            details=consistency_checks,
            issues=self.identify_consistency_issues(consistency_checks)
        )

class TimelinessAnalyzer:
    def analyze(self, df, **kwargs):
        """Analyze data timeliness and freshness"""
        
        timeliness_checks = []
        current_time = datetime.utcnow()
        
        # Find timestamp columns
        timestamp_columns = self.identify_timestamp_columns(df)
        
        for column in timestamp_columns:
            # Calculate data freshness
            max_timestamp = df.agg(F.max(column)).collect()[0][0]
            
            if max_timestamp:
                data_age_hours = (current_time - max_timestamp).total_seconds() / 3600
                freshness_score = max(0, 1 - (data_age_hours / 24))  # Degrade over 24 hours
                
                timeliness_checks.append({
                    'column': column,
                    'max_timestamp': max_timestamp,
                    'age_hours': data_age_hours,
                    'freshness_score': freshness_score
                })
        
        # Check for future dates (data quality issue)
        future_date_checks = self.check_future_dates(df, timestamp_columns, current_time)
        timeliness_checks.extend(future_date_checks)
        
        # Check timestamp distribution for gaps
        gap_analysis = self.analyze_timestamp_gaps(df, timestamp_columns)
        timeliness_checks.extend(gap_analysis)
        
        overall_timeliness = sum(
            check.get('freshness_score', check.get('score', 1.0)) for check in timeliness_checks
        ) / len(timeliness_checks) if timeliness_checks else 1.0
        
        return DimensionResult(
            dimension='timeliness',
            score=overall_timeliness,
            details=timeliness_checks,
            issues=self.identify_timeliness_issues(timeliness_checks)
        )

# Usage example with visualization
def generate_quality_dashboard(scorecard):
    """Generate interactive quality dashboard"""
    
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Overall Score', 'Dimension Scores', 'Issues by Severity', 'Trends'),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "scatter"}]]
    )
    
    # Overall score gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=scorecard.overall_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Data Quality Score (%)"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ),
        row=1, col=1
    )
    
    # Dimension scores
    dimensions = list(scorecard.dimension_scores.keys())
    scores = [scorecard.dimension_scores[dim].score * 100 for dim in dimensions]
    
    fig.add_trace(
        go.Bar(x=dimensions, y=scores, name="Dimension Scores"),
        row=1, col=2
    )
    
    return fig
```

#### Solution 3.4: Schema Validation for Semi-Structured Data

```python
class SemiStructuredSchemaValidator:
    def __init__(self):
        self.schema_registry = SchemaRegistry()
        self.evolution_tracker = SchemaEvolutionTracker()
        self.validation_rules = ValidationRuleEngine()
    
    def validate_json_schema_evolution(self, json_data_stream, schema_config):
        """Validate JSON data with evolving schemas across multiple sources"""
        
        validation_results = []
        
        for source_name, json_records in json_data_stream:
            # Get or infer schema for source
            current_schema = self.get_current_schema(source_name)
            
            for record in json_records:
                # Validate against current schema
                validation_result = self.validate_record(record, current_schema, source_name)
                
                # Handle schema evolution
                if not validation_result.is_valid:
                    evolution_result = self.handle_potential_evolution(
                        record, current_schema, source_name
                    )
                    
                    if evolution_result.schema_evolved:
                        # Update schema and re-validate
                        current_schema = evolution_result.new_schema
                        self.schema_registry.register_schema(source_name, current_schema)
                        validation_result = self.validate_record(record, current_schema, source_name)
                
                validation_results.append(validation_result)
        
        return SchemaValidationReport(
            total_records=len(validation_results),
            valid_records=sum(1 for r in validation_results if r.is_valid),
            validation_details=validation_results,
            schema_evolutions=self.evolution_tracker.get_recent_evolutions()
        )
    
    def infer_schema_from_sample(self, json_records, confidence_threshold=0.8):
        """Infer JSON schema from sample data with confidence scoring"""
        
        field_analysis = defaultdict(lambda: {
            'types': defaultdict(int),
            'null_count': 0,
            'samples': [],
            'patterns': []
        })
        
        total_records = len(json_records)
        
        # Analyze field characteristics
        for record in json_records:
            self.analyze_record_fields(record, field_analysis, "")
        
        # Generate schema with confidence scores
        inferred_schema = {
            'type': 'object',
            'properties': {},
            'confidence_metadata': {}
        }
        
        for field_path, analysis in field_analysis.items():
            field_schema, confidence = self.infer_field_schema(
                analysis, total_records, confidence_threshold
            )
            
            # Build nested schema structure
            self.set_nested_field(inferred_schema['properties'], field_path.split('.'), field_schema)
            inferred_schema['confidence_metadata'][field_path] = confidence
        
        return inferred_schema
    
    def validate_record(self, record, schema, source_name):
        """Comprehensive record validation with detailed error reporting"""
        
        errors = []
        warnings = []
        
        try:
            # Basic JSON schema validation
            jsonschema.validate(record, schema)
            basic_validation_passed = True
        except jsonschema.ValidationError as e:
            basic_validation_passed = False
            errors.append({
                'type': 'schema_violation',
                'field': '.'.join(str(x) for x in e.absolute_path),
                'message': e.message,
                'invalid_value': e.instance
            })
        
        # Business rule validation
        business_rules = self.validation_rules.get_rules(source_name)
        for rule in business_rules:
            rule_result = rule.validate(record)
            if not rule_result.passed:
                if rule_result.severity == 'error':
                    errors.append({
                        'type': 'business_rule_violation',
                        'rule_name': rule.name,
                        'message': rule_result.message,
                        'field': rule_result.field
                    })
                else:
                    warnings.append({
                        'type': 'business_rule_warning',
                        'rule_name': rule.name,
                        'message': rule_result.message,
                        'field': rule_result.field
                    })
        
        # Data quality checks
        quality_issues = self.check_data_quality(record, schema)
        warnings.extend(quality_issues)
        
        return ValidationResult(
            record_id=record.get('id', 'unknown'),
            source=source_name,
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            schema_version=schema.get('version', 'unknown'),
            validated_at=datetime.utcnow()
        )
    
    def handle_potential_evolution(self, record, current_schema, source_name):
        """Handle potential schema evolution scenarios"""
        
        # Detect evolution patterns
        evolution_patterns = []
        
        # New field detection
        new_fields = self.detect_new_fields(record, current_schema)
        if new_fields:
            evolution_patterns.append({
                'type': 'field_addition',
                'fields': new_fields,
                'compatibility': 'backward_compatible'
            })
        
        # Type change detection
        type_changes = self.detect_type_changes(record, current_schema)
        if type_changes:
            evolution_patterns.append({
                'type': 'type_change',
                'changes': type_changes,
                'compatibility': 'potentially_breaking'
            })
        
        # Field removal detection (missing required fields)
        missing_fields = self.detect_missing_required_fields(record, current_schema)
        if missing_fields:
            evolution_patterns.append({
                'type': 'field_removal',
                'fields': missing_fields,
                'compatibility': 'breaking'
            })
        
        # Decide on evolution strategy
        if evolution_patterns:
            evolution_strategy = self.determine_evolution_strategy(evolution_patterns, source_name)
            
            if evolution_strategy.allow_evolution:
                new_schema = self.evolve_schema(current_schema, evolution_patterns)
                
                # Track evolution
                self.evolution_tracker.record_evolution(
                    source_name, current_schema, new_schema, evolution_patterns
                )
                
                return EvolutionResult(
                    schema_evolved=True,
                    new_schema=new_schema,
                    evolution_patterns=evolution_patterns,
                    strategy=evolution_strategy
                )
        
        return EvolutionResult(schema_evolved=False)

class SchemaEvolutionTracker:
    """Track schema changes over time with impact analysis"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.compatibility_checker = SchemaCompatibilityChecker()
    
    def record_evolution(self, source_name, old_schema, new_schema, patterns):
        """Record schema evolution event"""
        
        evolution_record = {
            'source_name': source_name,
            'timestamp': datetime.utcnow(),
            'old_schema_version': old_schema.get('version', 'unknown'),
            'new_schema_version': self.generate_version(new_schema),
            'evolution_patterns': patterns,
            'compatibility_impact': self.analyze_compatibility_impact(old_schema, new_schema),
            'affected_consumers': self.identify_affected_consumers(source_name, patterns)
        }
        
        self.storage.store_evolution_record(evolution_record)
        
        # Trigger notifications to affected consumers
        self.notify_affected_consumers(evolution_record)
    
    def analyze_compatibility_impact(self, old_schema, new_schema):
        """Analyze the impact of schema changes on compatibility"""
        
        impact_analysis = {
            'backward_compatible': True,
            'forward_compatible': True,
            'breaking_changes': [],
            'risk_level': 'low'
        }
        
        # Check backward compatibility
        backward_issues = self.compatibility_checker.check_backward_compatibility(old_schema, new_schema)
        if backward_issues:
            impact_analysis['backward_compatible'] = False
            impact_analysis['breaking_changes'].extend(backward_issues)
        
        # Check forward compatibility
        forward_issues = self.compatibility_checker.check_forward_compatibility(old_schema, new_schema)
        if forward_issues:
            impact_analysis['forward_compatible'] = False
        
        # Assess risk level
        if not impact_analysis['backward_compatible']:
            impact_analysis['risk_level'] = 'high'
        elif not impact_analysis['forward_compatible']:
            impact_analysis['risk_level'] = 'medium'
        
        return impact_analysis

# Advanced validation rules engine
class ValidationRuleEngine:
    def __init__(self):
        self.rules_registry = {}
        self.custom_validators = {}
    
    def register_custom_validator(self, name, validator_func):
        """Register custom validation function"""
        self.custom_validators[name] = validator_func
    
    def define_business_rules(self, source_name, rules_config):
        """Define business validation rules for a data source"""
        
        rules = []
        
        for rule_config in rules_config:
            if rule_config['type'] == 'range':
                rule = RangeValidationRule(
                    field=rule_config['field'],
                    min_value=rule_config.get('min'),
                    max_value=rule_config.get('max'),
                    severity=rule_config.get('severity', 'error')
                )
            elif rule_config['type'] == 'pattern':
                rule = PatternValidationRule(
                    field=rule_config['field'],
                    pattern=rule_config['pattern'],
                    severity=rule_config.get('severity', 'error')
                )
            elif rule_config['type'] == 'custom':
                validator_func = self.custom_validators[rule_config['validator']]
                rule = CustomValidationRule(
                    field=rule_config['field'],
                    validator=validator_func,
                    severity=rule_config.get('severity', 'error')
                )
            elif rule_config['type'] == 'cross_field':
                rule = CrossFieldValidationRule(
                    fields=rule_config['fields'],
                    condition=rule_config['condition'],
                    severity=rule_config.get('severity', 'error')
                )
            
            rules.append(rule)
        
        self.rules_registry[source_name] = rules
    
    def get_rules(self, source_name):
        """Get validation rules for a data source"""
        return self.rules_registry.get(source_name, [])

# Example usage
validator = SemiStructuredSchemaValidator()

# Register custom business validation
validator.validation_rules.register_custom_validator(
    'valid_email', 
    lambda value: re.match(r'^[^@]+@[^@]+\.[^@]+$', value) is not None
)

# Define business rules for user data
user_validation_rules = [
    {
        'type': 'pattern',
        'field': 'email',
        'pattern': r'^[^@]+@[^@]+\.[^@]+$',
        'severity': 'error'
    },
    {
        'type': 'range',
        'field': 'age',
        'min': 0,
        'max': 150,
        'severity': 'error'
    },
    {
        'type': 'cross_field',
        'fields': ['birth_date', 'age'],
        'condition': 'age == current_year - birth_year',
        'severity': 'warning'
    }
]

validator.validation_rules.define_business_rules('user_events', user_validation_rules)
```

This comprehensive examination covers all the required topics with detailed solutions. The exam is structured to test both theoretical knowledge and practical implementation skills at a petabyte scale. Each section builds upon previous concepts and requires candidates to demonstrate deep understanding of data pipeline architecture, performance optimization, and production-grade implementations.

Would you like me to continue with the remaining sections (Implementation Challenges, System Design Scenarios, Production Case Studies, etc.)?