# Distributed Systems Cheat Sheets

!!! info "Quick Reference Cards"
    Condensed reference materials for quick lookup during system design and troubleshooting.

!!! tip "Quick Navigation"
    [← Glossary](glossary.md) |
    [Reference Home](index.md) |
    [Formulas →](formulas.md)

## System Design Cheat Sheet

### 1. Start with Requirements

<div class="cheat-sheet-box">
<h4>Functional Requirements</h4>

- What should the system do?
- Who are the users?
- What are the main features?
- What are the input/output?

<h4>Non-Functional Requirements</h4>

- **Scale**: Users, requests/sec, data size
- **Performance**: Latency, throughput
- **Availability**: Uptime target (99.9%?)
- **Consistency**: Strong, eventual, weak?
- **Durability**: Data retention needs
</div>

### 2. Capacity Estimation

<div class="cheat-sheet-box">
<h4>Quick Calculations</h4>

```
Daily active users → Requests/sec:
- 1M DAU ≈ 10-20 requests/sec average
- Peak = 2-3x average
- Special events = 10-100x average

Storage estimation:
- Text post: ~1 KB
- Image: ~200 KB (compressed)
- Video: ~2 MB/minute (compressed)

Bandwidth:
- 1 Gbps = 125 MB/s
- CDN typically handles 80% of bandwidth
```
</div>

### 3. Component Selection

<div class="cheat-sheet-box">
<h4>Common Components</h4>

| Component | Use Case | Examples |
|-----------|----------|----------|
| **Load Balancer** | Distribute traffic | Nginx, HAProxy, ALB |
| **Cache** | Reduce latency | Redis, Memcached |
| **CDN** | Static content | CloudFront, Akamai |
| **Queue** | Async processing | SQS, RabbitMQ, Kafka |
| **Database** | Data storage | PostgreSQL, MySQL |
| **NoSQL** | Flexible schema | MongoDB, Cassandra |
| **Search** | Full-text search | Elasticsearch, Solr |
| **Blob Storage** | Files, images | S3, GCS |
</div>

## Consistency Patterns Cheat Sheet

<div class="cheat-sheet-box">
<h4>Consistency Levels</h4>

| Level | Guarantee | Use Case |
|-------|-----------|----------|
| **Strong** | All see same data immediately | Financial transactions |
| **Eventual** | Will converge eventually | Social media feeds |
| **Weak** | No guarantees | Caching, analytics |
| **Causal** | Respects cause-effect | Chat messages |
| **Read-after-write** | See own writes | User profiles |
</div>

<div class="cheat-sheet-box">
<h4>Replication Strategies</h4>

| Strategy | Consistency | Availability | Use Case |
|----------|-------------|--------------|----------|
| **Single-leader** | Strong | Lower | Traditional DB |
| **Multi-leader** | Eventual | Higher | Multi-region |
| **Leaderless** | Eventual | Highest | Cassandra |
</div>

## Performance Optimization Cheat Sheet

### Latency Reduction

<div class="cheat-sheet-box">
<h4>Techniques by Impact</h4>

1. **Caching** (10-100x improvement)
   - Browser cache
   - CDN cache
   - Application cache
   - Database cache

2. **Data Locality** (2-10x improvement)
   - Edge computing
   - Regional deployments
   - Co-location

3. **Connection Pooling** (2-5x improvement)
   - Database connections
   - HTTP keep-alive
   - Persistent WebSockets

4. **Async Processing** (perceived latency)
   - Message queues
   - Background jobs
   - Webhooks
</div>

### Throughput Improvement

<div class="cheat-sheet-box">
<h4>Scaling Techniques</h4>

**Horizontal Scaling**
- Add more machines
- Stateless services
- Shared-nothing architecture
- Auto-scaling groups

**Vertical Scaling**
- Bigger machines
- More CPU/RAM
- Faster disks (NVMe)
- Limited by hardware

**Data Partitioning**
- Sharding by key
- Range partitioning
- Hash partitioning
- Geo-partitioning
</div>

## Reliability Patterns Cheat Sheet

<div class="cheat-sheet-box">
<h4>Fault Tolerance Patterns</h4>

| Pattern | Purpose | Implementation |
|---------|---------|----------------|
| **Retry** | Handle transient failures | Exponential backoff + jitter |
| **Circuit Breaker** | Prevent cascading failure | Fail fast when threshold hit |
| **Bulkhead** | Isolate failures | Separate thread pools |
| **Timeout** | Bound wait time | Hierarchical timeouts |
| **Failover** | Switch to backup | Active-passive, active-active |
| **Health Checks** | Detect failures | HTTP endpoints, heartbeats |
</div>

<div class="cheat-sheet-box">
<h4>Availability Calculation</h4>

```
Series (AND): A = A₁ × A₂ × ... × Aₙ
Parallel (OR): A = 1 - (1-A₁)(1-A₂)...(1-Aₙ)

Examples:
- Two 99% components in series: 98.01%
- Two 99% components in parallel: 99.99%
- Three 99.9% components in series: 99.7%
```
</div>

## Monitoring & Debugging Cheat Sheet

### Key Metrics

<div class="cheat-sheet-box">
<h4>Golden Signals</h4>

1. **Latency**: Response time distribution
   - p50, p95, p99, p99.9
   - Track per endpoint

2. **Traffic**: Request volume
   - Requests/second
   - Bandwidth usage

3. **Errors**: Failure rate
   - 4xx vs 5xx errors
   - Error types

4. **Saturation**: Resource usage
   - CPU, memory, disk, network
   - Queue depths
</div>

### Debugging Distributed Systems

<div class="cheat-sheet-box">
<h4>Common Issues & Checks</h4>

| Symptom | Possible Causes | First Checks |
|---------|----------------|--------------|
| **High latency** | Network, overload, GC | Traces, CPU, queue depth |
| **Timeouts** | Cascading failure, deadlock | Dependencies, thread dumps |
| **Data inconsistency** | Race condition, replication lag | Timestamps, version conflicts |
| **Memory leak** | Unclosed resources, cache | Heap dumps, GC logs |
| **Intermittent errors** | Partial failure, timing | Logs correlation, retry counts |
</div>

## Security Cheat Sheet

<div class="cheat-sheet-box">
<h4>Defense in Depth</h4>

1. **Network Security**
   - Firewalls, VPC, security groups
   - TLS/SSL everywhere
   - VPN for management

2. **Authentication & Authorization**
   - OAuth 2.0, JWT tokens
   - API keys, rate limiting
   - Role-based access control

3. **Data Protection**
   - Encryption at rest
   - Encryption in transit
   - Key rotation

4. **Operational Security**
   - Audit logging
   - Intrusion detection
   - Regular updates
</div>

## Decision Making Cheat Sheet

### Technology Choices

<div class="cheat-sheet-box">
<h4>SQL vs NoSQL</h4>

**Choose SQL when:**
- ACID requirements
- Complex queries/joins
- Well-defined schema
- Moderate scale

**Choose NoSQL when:**
- Massive scale
- Flexible schema
- Simple queries
- Geographic distribution
</div>

<div class="cheat-sheet-box">
<h4>Sync vs Async</h4>

**Use Synchronous:**
- User-facing operations
- Real-time requirements
- Simple workflows
- Strong consistency needs

**Use Asynchronous:**
- Background processing
- High latency operations
- Resilience to failures
- Eventual consistency OK
</div>

### Architecture Patterns

<div class="cheat-sheet-box">
<h4>Common Architectures</h4>

| Pattern | When to Use | Trade-offs |
|---------|-------------|------------|
| **Monolith** | Small team, simple domain | Easy start, hard to scale |
| **Microservices** | Large team, complex domain | Flexible, operational overhead |
| **Serverless** | Variable load, event-driven | No ops, vendor lock-in |
| **Event Sourcing** | Audit needs, temporal queries | Complete history, complexity |
| **CQRS** | Different read/write patterns | Optimized queries, eventual consistency |
</div>

## Quick Formula Reference

<div class="cheat-sheet-box">
<h4>Essential Formulas</h4>

```
Little's Law: L = λW
- L: items in system
- λ: arrival rate
- W: time in system

Response Time (M/M/1): R = S/(1-ρ)
- S: service time
- ρ: utilization

Availability: A = MTBF/(MTBF + MTTR)

Throughput: X = N/T
- N: completed requests
- T: time period

Utilization: U = λ/μ
- λ: arrival rate
- μ: service rate
```
</div>

## Command Line Quick Reference

<div class="cheat-sheet-box">
<h4>Performance Debugging</h4>

```bash
# System resources
top -b -n 1
htop
iostat -x 1
vmstat 1
dstat -cdnm

# Network
netstat -an | grep ESTABLISHED | wc -l
ss -s
tcpdump -i any -n port 80
iftop -i eth0

# Process investigation
strace -p PID
lsof -p PID
pmap PID

# Logs
tail -f /var/log/app.log | grep ERROR
journalctl -u service-name -f
multitail log1 log2 log3
```
</div>

## Related Resources

- [Glossary](glossary.md) - Term definitions
- [Formulas](formulas.md) - Detailed calculations
- [Tools](../tools/index.md) - Interactive calculators