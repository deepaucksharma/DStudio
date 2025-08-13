# Episode 22: Streaming Architectures Code Examples

## Overview
यह directory contains production-ready code examples for Streaming Architectures। ये examples Indian context में real-world scenarios को demonstrate करते हैं - UPI transactions, social media analytics, fraud detection, और e-commerce streaming।

## Code Examples Summary

### Python Examples

#### 1. Kafka Producer/Consumer for UPI (`python/01_kafka_producer_consumer_upi.py`)
- **Description**: UPI transactions के लिए high-throughput Kafka implementation
- **Features**:
  - Real-time UPI transaction processing
  - Fraud detection pipeline
  - Transaction metrics streaming
  - Paytm/PhonePe style transaction flow
- **Usage**:
  ```bash
  python python/01_kafka_producer_consumer_upi.py
  ```

#### 2. Kafka Streams Word Count (`python/02_kafka_streams_word_count.py`)
- **Description**: Indian social media के लिए real-time word count और trend analysis
- **Features**:
  - Multi-language support (Hindi, English, Hinglish)
  - Stop words filtering
  - Trending hashtags
  - Real-time analytics
- **Usage**:
  ```bash
  python python/02_kafka_streams_word_count.py
  ```

#### 3. Real-time Fraud Detection (`python/03_realtime_fraud_detection.py`)
- **Description**: ML-powered real-time fraud detection for Indian banking
- **Features**:
  - Feature engineering for Indian banking patterns
  - Risk scoring algorithms
  - Real-time alert generation
  - Location-based fraud detection
- **Usage**:
  ```bash
  python python/03_realtime_fraud_detection.py
  ```

### Go Examples

#### 1. Apache Flink Stream Processing (`go/stream_processing_flink.go`)
- **Description**: E-commerce analytics के लिए stateful stream processing
- **Features**:
  - Real-time product analytics
  - User session tracking
  - Conversion rate analysis
  - Time window aggregations
- **Compilation**:
  ```bash
  cd go/
  go run stream_processing_flink.go
  ```

## Requirements

### Python Dependencies
```bash
pip install asyncio dataclasses numpy json datetime uuid threading
```

### Go Dependencies
```bash
go mod init streaming-examples
# No external dependencies required for basic examples
```

### For Production Use
```bash
# Kafka
pip install confluent-kafka kafka-python

# Apache Flink
pip install apache-flink

# Stream Processing
pip install apache-beam pyspark
```

## Key Concepts Demonstrated

### Apache Kafka
1. **High Throughput**: Millions of messages per second
2. **Partitioning**: Horizontal scaling through partitions
3. **Consumer Groups**: Load balancing and fault tolerance
4. **Producer Patterns**: Batching, compression, acknowledgments

### Stream Processing
1. **Stateful Processing**: Complex aggregations और joins
2. **Time Windows**: Tumbling, sliding, and session windows
3. **Watermarks**: Late event handling
4. **Exactly-Once Semantics**: Data consistency guarantees

### Real-time Analytics
1. **Feature Engineering**: Real-time feature extraction
2. **ML Model Inference**: Online prediction serving
3. **Alert Generation**: Real-time anomaly detection
4. **Dashboard Updates**: Live metrics streaming

## Indian Context Use Cases

### UPI Payment Processing
- Real-time transaction validation
- Fraud detection and prevention
- Payment routing optimization
- Regulatory compliance monitoring

### Social Media Analytics
- Trending topics detection
- Sentiment analysis
- User engagement metrics
- Content moderation

### E-commerce Streaming
- Real-time recommendation engines
- Inventory level monitoring
- Price optimization
- Customer behavior tracking

### Banking & Fintech
- Risk assessment pipelines
- Credit scoring updates
- Transaction monitoring
- Regulatory reporting

## Architecture Patterns

### Lambda Architecture
```
Batch Layer (Historical Data) + Speed Layer (Real-time) + Serving Layer (Queries)
```

### Kappa Architecture
```
Stream Processing Only (Unified approach)
```

### Event Sourcing + CQRS
```
Event Stream → Command Processing → Query Views
```

## Performance Optimizations

### Kafka Optimizations
1. **Producer Settings**:
   - `batch.size`: 16384 (16KB)
   - `linger.ms`: 10
   - `compression.type`: gzip
   - `acks`: all

2. **Consumer Settings**:
   - `fetch.min.bytes`: 1024
   - `fetch.max.wait.ms`: 500
   - `max.poll.records`: 500

### Stream Processing Optimizations
1. **Parallelism**: Match partition count
2. **State Stores**: RocksDB for large state
3. **Checkpointing**: Regular state snapshots
4. **Windowing**: Appropriate window sizes

## Scaling Strategies

### Horizontal Scaling
1. **Kafka Partitions**: Increase partitions for higher throughput
2. **Consumer Instances**: Scale consumer groups
3. **Stream Processing**: Increase parallelism
4. **State Distribution**: Partition state stores

### Vertical Scaling
1. **Memory**: Increase heap sizes
2. **CPU**: More cores for parallel processing
3. **Network**: Higher bandwidth
4. **Storage**: Fast SSDs for state stores

## Monitoring & Observability

### Key Metrics
1. **Throughput**: Messages per second
2. **Latency**: End-to-end processing time
3. **Lag**: Consumer lag monitoring
4. **Error Rates**: Failed message processing

### Tools
1. **Kafka Manager**: Cluster monitoring
2. **Grafana**: Metrics visualization
3. **Prometheus**: Metrics collection
4. **ELK Stack**: Log analysis

## Running Examples

```bash
# Python examples
python python/01_kafka_producer_consumer_upi.py
python python/02_kafka_streams_word_count.py
python python/03_realtime_fraud_detection.py

# Go examples
cd go/
go run stream_processing_flink.go
```

## Production Deployment

### Kafka Cluster Setup
```yaml
# 3-node Kafka cluster
broker-1: kafka-1:9092
broker-2: kafka-2:9092
broker-3: kafka-3:9092
replication-factor: 3
min-insync-replicas: 2
```

### Stream Processing Deployment
```yaml
# Kubernetes deployment
replicas: 3
resources:
  cpu: 2 cores
  memory: 4GB
  storage: 50GB SSD
```

## Security Considerations

### Kafka Security
1. **SASL/SCRAM**: Authentication
2. **SSL/TLS**: Encryption in transit
3. **ACLs**: Topic-level authorization
4. **Encryption at Rest**: Sensitive data protection

### Stream Processing Security
1. **State Store Encryption**: Sensitive state protection
2. **Network Security**: VPC and security groups
3. **Secrets Management**: Credentials handling
4. **Audit Logging**: Access and operation logs

## Troubleshooting

### Common Issues
1. **Consumer Lag**: Scale consumers or optimize processing
2. **Memory Issues**: Tune JVM heap sizes
3. **Network Partitions**: Configure timeouts properly
4. **Data Skew**: Improve partitioning strategies

### Debugging Tools
1. **Kafka Console Tools**: kafka-console-consumer/producer
2. **JVM Profiling**: VisualVM, JProfiler
3. **Network Analysis**: tcpdump, Wireshark
4. **Log Analysis**: Centralized logging

## Best Practices

### Development
1. **Schema Evolution**: Use Avro/Protobuf schemas
2. **Error Handling**: Implement retry and dead letter queues
3. **Testing**: Use embedded Kafka for tests
4. **Monitoring**: Add comprehensive metrics

### Operations
1. **Capacity Planning**: Monitor resource usage
2. **Backup Strategy**: Regular configuration backups
3. **Disaster Recovery**: Multi-region setup
4. **Performance Tuning**: Regular optimization

## Further Reading

### Books
- "Kafka: The Definitive Guide" by Neha Narkhede
- "Streaming Systems" by Tyler Akidau
- "Building Event-Driven Microservices" by Adam Bellemare

### Online Resources
- Apache Kafka documentation
- Confluent Platform guides
- Apache Flink tutorials
- Stream processing patterns

## Contributing

When adding new examples:
1. Focus on Indian use cases and scale
2. Include comprehensive error handling
3. Add performance benchmarks
4. Document deployment strategies
5. Include monitoring and alerting

## License

MIT License - Use freely for learning and production use.