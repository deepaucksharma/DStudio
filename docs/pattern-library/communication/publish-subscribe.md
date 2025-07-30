---
title: Publish-Subscribe Pattern
description: Decoupled messaging pattern where publishers send messages to topics
  and subscribers receive messages based on their interests
type: pattern
category: communication
difficulty: intermediate
reading-time: 35 min
prerequisites:
- message-queues
- event-driven
- distributed-systems
when-to-use: Event-driven architectures, real-time notifications, decoupled microservices,
  multi-consumer scenarios
when-not-to-use: Point-to-point communication, request-response patterns, transactional
  consistency requirements
status: initial
last-updated: 2025-07-26
excellence_tier: gold
pattern_status: recommended
introduced: 1987-01
current_relevance: mainstream
modern-examples:
- company: Apache Kafka
  implementation: Distributed pub-sub for event streaming at LinkedIn, Uber, Netflix
  scale: 7 trillion messages/day at LinkedIn
- company: Redis
  implementation: In-memory pub-sub for real-time features
  scale: Millions of messages/sec with microsecond latency
- company: Google Cloud Pub/Sub
  implementation: Globally distributed message service
  scale: 500M messages/second, 99.95% SLA
production-checklist:
- Choose delivery semantics (at-least-once, at-most-once, exactly-once)
- Configure topic partitioning for scalability
- Implement message ordering guarantees where needed
- Set up dead letter queues for failed messages
- Configure retention policies (hours to days)
- Monitor consumer lag and backpressure
- Implement idempotent consumers
- Set up topic-based access control
- Plan for message schema evolution
- Test fan-out performance under load
---


# Publish-Subscribe Pattern

!!! success "🏆 Gold Standard Pattern"
    **Decoupled Event Distribution** • Kafka, Redis, Google Pub/Sub proven
    
    The cornerstone of event-driven architectures. Pub-sub enables scalable, decoupled communication where publishers and subscribers operate independently, supporting everything from real-time notifications to event streaming.
    
    **Key Success Metrics:**
    - LinkedIn Kafka: 7 trillion messages/day powering all services
    - Redis Pub/Sub: Microsecond latency for real-time features
    - Google Pub/Sub: 500M messages/sec with global distribution

## Essential Question
**How do we broadcast events to multiple consumers without coupling producers to consumers?**

## When to Use / When NOT to Use

### ✅ Use When
| Scenario | Why | Example |
|----------|-----|--------|
| **Event-driven architecture** | Loose coupling needed | Order events → Multiple services |
| **Multiple consumers** | 1-to-many communication | Notifications to users |
| **Temporal decoupling** | Process at different rates | Analytics pipeline |
| **Fan-out scenarios** | Broadcast to many | Real-time updates |

### ❌ DON'T Use When
| Scenario | Why | Alternative |
|----------|-----|-------------|
| **Request-response** | Need immediate reply | RPC/REST API |
| **Point-to-point** | Single receiver only | Message Queue |
| **Transactional** | ACID guarantees | Database transactions |
| **Ordered processing** | Strict sequence critical | Single partition queue |

## Level 1: Intuition (5 min)

### The News Broadcast Analogy
Pub-Sub is like a news broadcast - the TV station (publisher) broadcasts news to anyone tuned in (subscribers). The station doesn't know who's watching, and viewers can tune in or out anytime.

**Pub-Sub = Broadcasting events to interested parties**

```
Traditional Direct Communication:        Pub-Sub Communication:
┌────────┐  message  ┌────────┐         ┌────────┐
│Sender A├──────────►│Receiver│         │Pub A   │
└────────┘           └────────┘         └───┬────┘
                                            │ publish
┌────────┐  message  ┌────────┐             ▼
│Sender B├──────────►│Receiver│         ┌────────┐      ┌─────┐
└────────┘           └────────┘         │ Topic  │◄─────┤Sub 1│
                                        └───┬────┘      └─────┘
❌ Tight coupling                           │ broadcast
❌ Sender must know receiver                ▼           ┌─────┐
❌ 1-to-1 only                          ┌───┴────┐◄─────┤Sub 2│
                                        │Messages│      └─────┘
                                        └────────┘      ┌─────┐
                                                  ◄─────┤Sub 3│
                                        ✅ Loose coupling └─────┘
                                        ✅ Dynamic subscribers
                                        ✅ 1-to-many broadcast
```

### Visual Overview

```mermaid
graph TD
    subgraph "Publishers"
        P1[Order Service]
        P2[Payment Service]
        P3[Inventory Service]
    end
    
    subgraph "Message Broker"
        T1[Order Events]
        T2[Payment Events]
        T3[Inventory Events]
    end
    
    subgraph "Subscribers"
        S1[Email Service]
        S2[Analytics Service]
        S3[Audit Service]
        S4[Shipping Service]
    end
    
    P1 -->|publish| T1
    P2 -->|publish| T2
    P3 -->|publish| T3
    
    T1 -->|subscribe| S1
    T1 -->|subscribe| S2
    T1 -->|subscribe| S4
    
    T2 -->|subscribe| S2
    T2 -->|subscribe| S3
    
    T3 -->|subscribe| S4
    T3 -->|subscribe| S2
    
    style T1 fill:#3b82f6,stroke:#1e40af,stroke-width:2px
    style T2 fill:#3b82f6,stroke:#1e40af,stroke-width:2px
    style T3 fill:#3b82f6,stroke:#1e40af,stroke-width:2px
```

### Core Value
| Aspect | Direct Communication | Pub-Sub |
|--------|---------------------|----------|
| **Coupling** | Sender knows receiver | Complete decoupling |
| **Scalability** | 1-to-1 only | 1-to-many broadcast |
| **Availability** | Both must be online | Temporal decoupling |
| **Flexibility** | Fixed endpoints | Dynamic subscribers |

## Level 2: Foundation (10 min)

### Decision Matrix

```mermaid
graph TD
    Start[Communication Need] --> Q1{Multiple<br/>Consumers?}
    Q1 -->|No| Q2{Need Reply?}
    Q1 -->|Yes| PubSub[Use Pub-Sub]
    
    Q2 -->|Yes| RPC[Use RPC/REST]
    Q2 -->|No| Queue[Use Queue]
    
    PubSub --> Q3{Order<br/>Important?}
    Q3 -->|Yes| Partition[Single Partition]
    Q3 -->|No| FanOut[Full Fan-out]
    
    style PubSub fill:#4ade80,stroke:#16a34a
    style RPC fill:#f87171,stroke:#dc2626
    style Queue fill:#60a5fa,stroke:#2563eb
```

### Basic Structure

```python
from collections import defaultdict
from queue import Queue
from threading import Thread
import time

class PubSubBroker:
    def __init__(self):
        self.topics = defaultdict(list)  # topic -> [subscribers]
        self.messages = defaultdict(Queue)  # topic -> message queue
        
    def publish(self, topic, message):
        """Publish message to a topic"""
        # Store message for all subscribers
        for subscriber in self.topics[topic]:
            self.messages[subscriber].put({
                'topic': topic,
                'message': message,
                'timestamp': time.time()
            })
    
    def subscribe(self, topic, callback):
        """Subscribe to topic with callback function"""
        subscriber_id = f"{topic}_{len(self.topics[topic])}"
        self.topics[topic].append(subscriber_id)
        
        # Start subscriber thread
        thread = Thread(target=self._process_messages, 
                       args=(subscriber_id, callback))
        thread.daemon = True
        thread.start()
        
        return subscriber_id
    
    def _process_messages(self, subscriber_id, callback):
        """Process messages for a subscriber"""
        while True:
            message = self.messages[subscriber_id].get()
            try:
                callback(message)
            except Exception as e:
                print(f"Subscriber {subscriber_id} error: {e}")
```

### Architecture Diagram

```mermaid
flowchart TB
    subgraph "Pub-Sub Architecture"
        subgraph "Publishers"
            P1[Publisher 1]
            P2[Publisher 2]
        end
        
        subgraph "Broker Components"
            TM[Topic Manager]
            MM[Message Manager]
            SM[Subscription Manager]
            Q1[Queue: Topic A]
            Q2[Queue: Topic B]
        end
        
        subgraph "Subscribers"
            S1[Subscriber 1]
            S2[Subscriber 2]
            S3[Subscriber 3]
        end
        
        P1 -->|publish(topicA, msg)| TM
        P2 -->|publish(topicB, msg)| TM
        
        TM --> MM
        MM --> Q1
        MM --> Q2
        
        SM -->|route| S1
        SM -->|route| S2
        SM -->|route| S3
        
        Q1 -.->|async delivery| SM
        Q2 -.->|async delivery| SM
    end
    
    style TM fill:#f59e0b,stroke:#d97706,stroke-width:2px
    style MM fill:#3b82f6,stroke:#1e40af,stroke-width:2px
    style SM fill:#10b981,stroke:#059669,stroke-width:2px
```

## Level 3: Deep Dive (15 min)

### Production Example: Apache Kafka

Kafka implements distributed pub-sub at massive scale:

```python
from kafka import KafkaProducer, KafkaConsumer
import json
import logging

class KafkaEventBus:
    def __init__(self, bootstrap_servers):
        self.servers = bootstrap_servers
        self.producer = None
        self.consumers = {}
        
    def publish(self, topic, event):
        """Publish event to Kafka topic"""
        if not self.producer:
            self.producer = KafkaProducer(
                bootstrap_servers=self.servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas
                retries=3
            )
        
        future = self.producer.send(topic, event)
        return future.get(timeout=10)  # Synchronous send
    
    def subscribe(self, topics, group_id, handler):
        """Subscribe to Kafka topics with consumer group"""
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            enable_auto_commit=False,  # Manual commit for reliability
            max_poll_records=100
        )
        
        # Process messages
        for message in consumer:
            try:
                handler(message.value)
                consumer.commit()  # Commit after successful processing
            except Exception as e:
                logging.error(f"Processing error: {e}")
                # Message will be redelivered
```

### Implementation Strategies

| Strategy | Use Case | Example |
|----------|----------|---------|  
| **Topic-Based** | Categorical events | orders.created, users.updated |
| **Content-Based** | Filter by attributes | price > 100, region = 'US' |
| **Hierarchical** | Topic trees | sports.football.* |
| **Partitioned** | Scalable ordering | Partition by user_id |

<div class="failure-vignette">
<h4>💥 The Slack Notification Storm (2019)</h4>

**What Happened**: Slack experienced a 5-hour global outage when a routine configuration change triggered a pub-sub message storm that overwhelmed their infrastructure.

**Root Cause**: 
- Admin changed notification settings for a large workspace
- Change event published to notification topic
- 8,000 subscribers (user notification services) received the event
- Each subscriber fetched full workspace data (100MB)
- 800GB of sudden traffic overwhelmed databases
- Retry logic created exponential traffic growth

**Impact**: 
- 5 hours of complete service outage
- 12 million daily active users affected
- Cascading failures across presence, messaging, and search
- Stock price dropped 5% (market cap loss: $850M)

**Lessons Learned**:
- Pub-sub amplifies both good and bad events exponentially
- Always paginate or limit data fetched by subscribers
- Circuit breakers essential between pub-sub and databases
- Test configuration changes on small populations first
- Monitor fan-out ratio (messages published vs consumed)
</div>

### Common Pitfalls

<div class="decision-box">
<h4>🎯 Pub-Sub Design Decisions</h4>

**Delivery Semantics**:
- At-most-once: Fire and forget (data loss possible)
- At-least-once: Retry until ack (duplicates possible)
- Exactly-once: Complex, requires deduplication

**Ordering Guarantees**:
- No ordering: Maximum throughput
- Partition ordering: Order within partition only
- Total ordering: Severe performance impact

**Subscription Models**:
- Fan-out: Each subscriber gets all messages
- Competing consumers: Load balanced within group
- Content filtering: Subscribe to subset based on criteria

**Choose based on your requirements for consistency vs performance.**
</div>

1. **Message Ordering**: Pub-sub doesn't guarantee order across partitions
   ```python
   # ❌ Assuming order
   publish("orders", {"id": 1, "status": "created"})
   publish("orders", {"id": 1, "status": "paid"})  # May arrive first!
   
   # ✅ Include sequence numbers
   publish("orders", {"id": 1, "status": "created", "seq": 1})
   publish("orders", {"id": 1, "status": "paid", "seq": 2})
   ```

2. **At-least-once Delivery**: Handle duplicate messages
   ```python
   # ✅ Idempotent message processing
   processed_ids = set()
   
   def handle_message(msg):
       if msg['id'] in processed_ids:
           return  # Already processed
       processed_ids.add(msg['id'])
       process_order(msg)
   ```

3. **Subscriber Lag**: Monitor and handle slow consumers
   ```python
   # ✅ Monitor consumer lag
   lag_metrics = {
       'messages_behind': consumer.lag(),
       'processing_time': avg_processing_time,
       'error_rate': error_count / total_count
   }
   ```

## Level 4: Expert (20 min)

### Pattern Variations

```mermaid
graph TD
    subgraph "Basic Pub-Sub"
        BP[Publisher] --> BT[Topic] --> BS[Subscribers]
    end
    
    subgraph "Topic Hierarchy"
        HP[Publisher] --> HT1[sports.*]
        HT1 --> HT2[sports.football]
        HT1 --> HT3[sports.tennis]
        HT2 --> HS1[Football Fans]
        HT3 --> HS2[Tennis Fans]
        HT1 --> HS3[All Sports]
    end
    
    subgraph "Content Filtering"
        FP[Publisher] --> FT[Topic + Filter]
        FT -->|price > 100| FS1[Premium Orders]
        FT -->|region = 'US'| FS2[US Orders]
        FT -->|all| FS3[Audit Log]
    end
    
    style BT fill:#3b82f6,stroke:#1e40af
    style HT1 fill:#f59e0b,stroke:#d97706
    style FT fill:#10b981,stroke:#059669
```

### Integration with Other Patterns

#### With Event Sourcing
```python
class EventSourcingPubSub:
    def __init__(self, event_store, pubsub):
        self.event_store = event_store
        self.pubsub = pubsub
    
    def save_and_publish(self, aggregate_id, event):
        # Save to event store
        self.event_store.append(aggregate_id, event)
        
        # Publish for real-time processing
        topic = f"{event['type']}.{aggregate_id}"
        self.pubsub.publish(topic, event)
```

#### With CQRS
```python
class CQRSEventBus:
    def handle_command(self, command):
        # Process command
        events = self.domain.process(command)
        
        # Publish events for read model updates
        for event in events:
            self.pubsub.publish('domain.events', event)
```

### Performance Optimization

| Technique | Implementation | Benefit |
|-----------|---------------|---------|
| **Batching** | Group messages before sending | Reduce network overhead |
| **Compression** | Compress message payloads | Reduce bandwidth usage |
| **Partitioning** | Distribute topics across nodes | Horizontal scaling |
| **Async Processing** | Non-blocking message handling | Higher throughput |

## Level 5: Mastery (30 min)

### Distributed Pub-Sub Challenges

```mermaid
flowchart LR
    subgraph "Challenge: Network Partition"
        subgraph "Partition A"
            PA[Publisher A]
            BA[Broker A]
            SA[Subscriber A]
        end
        
        subgraph "Partition B"
            PB[Publisher B]
            BB[Broker B]
            SB[Subscriber B]
        end
        
        BA x--x BB
        
        PA --> BA --> SA
        PB --> BB --> SB
    end
    
    subgraph "Solution: Eventual Consistency"
        B1[Broker 1]
        B2[Broker 2]
        B3[Broker 3]
        
        B1 -.->|gossip| B2
        B2 -.->|gossip| B3
        B3 -.->|gossip| B1
    end
```

### Mathematical Model

**Message Delivery Probability**:
```
P(delivery) = 1 - (1 - p)^n

Where:
- p = probability of single delivery attempt success
- n = number of retry attempts
```

**Subscriber Capacity**:
```
C = M × S × (1 - L)

Where:
- C = effective capacity (messages/sec)
- M = max processing rate
- S = number of subscriber instances
- L = lag factor (0-1)
```

### Integration with Distributed Systems Laws

| Law | Application in Pub-Sub | Implementation |
|-----|----------------------|----------------|
| **Law 1: Correlated Failure** | Broker redundancy | Replicated topics, failover |
| **Law 2: Asynchronous Reality** | Core principle | Fire-and-forget publishing |
| **Law 3: Emergent Chaos** | Message storms | Rate limiting, circuit breakers |
| **Law 5: Distributed Knowledge** | Event sourcing | Immutable event log |

---

## Real-World Examples

| System | Use Case | Scale |
|--------|----------|--------|
| **Kafka** (LinkedIn) | Activity streams, logs | Trillions of messages/day |
| **Redis Pub/Sub** | Real-time notifications | Millions of messages/sec |
| **AWS SNS/SQS** | Serverless messaging | Global scale |
| **RabbitMQ** | Enterprise messaging | Thousands of queues |
| **NATS** | Cloud-native messaging | Microsecond latency |

### Production Metrics

```python
# Monitor pub-sub health
metrics = {
    # Publisher metrics
    'publish_rate': messages_per_second,
    'publish_errors': error_count,
    'publish_latency': p99_latency_ms,
    
    # Broker metrics
    'topic_count': active_topics,
    'message_backlog': pending_messages,
    'broker_cpu': cpu_percentage,
    
    # Subscriber metrics
    'consumer_lag': messages_behind,
    'processing_rate': messages_per_second,
    'error_rate': errors_per_minute
}
```

---

## Quick Reference

### Production Checklist ✓
- [ ] **Message Design**
  - [ ] Define schemas with versioning
  - [ ] Keep messages small (<1MB)
  - [ ] Include correlation IDs
  - [ ] Design for idempotency
  
- [ ] **Reliability**
  - [ ] Choose delivery semantics
  - [ ] Configure replication factor
  - [ ] Set retention policies
  - [ ] Implement DLQs
  
- [ ] **Performance**  
  - [ ] Partition for scale
  - [ ] Monitor consumer lag
  - [ ] Configure batching
  - [ ] Tune buffer sizes
  
- [ ] **Operations**
  - [ ] Set up monitoring/alerting
  - [ ] Document topic conventions
  - [ ] Plan capacity for peaks
  - [ ] Test failure scenarios

---

### Common Configurations

```yaml
# Kafka Configuration Example
kafka:
  topics:
    orders:
      partitions: 10
      replication: 3
      retention: 7d
      compression: snappy
  
  consumer:
    group-id: order-processor
    auto-commit: false
    max-poll-records: 100
    session-timeout: 30s
  
  producer:
    acks: all
    retries: 3
    batch-size: 16384
    linger-ms: 10
```

<div class="truth-box">
<h4>💡 Pub-Sub Production Insights</h4>

**The 10-100-1000 Rule:**
- 10 publishers can overwhelm 1000 subscribers
- 100 topics is the sweet spot for most systems
- 1000 subscribers per topic is the practical limit

**Message Size Economics:**
```
1KB message × 1000 subscribers = 1MB fan-out
1MB message × 1000 subscribers = 1GB fan-out
10MB message × 1000 subscribers = 10GB fan-out (💀)
```

**Real-World Patterns:**
- 80% of pub-sub issues are from unbounded fan-out
- Message storms always happen during peak traffic
- Subscribers are never as fast as publishers think
- "Exactly-once" delivery is a lie - design for idempotency

**Production Wisdom:**
> "Pub-sub is like a megaphone - great for announcements, terrible for conversations. Use request-response when you need a dialogue."

**The Three Laws of Pub-Sub:**
1. **Publishers always publish faster than subscribers consume**
2. **Topics proliferate like rabbits - governance is essential**
3. **Dead letter queues are not optional - they're mandatory**

**Cost Reality:**
- Pub-sub costs grow with (publishers × subscribers × message size)
- A single chatty publisher can bankrupt your infrastructure budget
- Always implement backpressure before going to production
</div>

## Related Patterns
- **[Event Sourcing](../coordination/event-sourcing.md)** - Store events as source of truth for state reconstruction
- **[CQRS](../architecture/cqrs.md)** - Use pub-sub to sync read/write models
- **[Message Queue](distributed-queue.md)** - Point-to-point alternative for work distribution
- **[Event Streaming](event-streaming.md)** - Process continuous event streams in real-time
- **[Saga Pattern](../coordination/saga.md)** - Coordinate distributed transactions via events
- **[Circuit Breaker](../resilience/circuit-breaker.md)** - Protect subscribers from overload
- **[API Gateway](api-gateway.md)** - Can publish events for async processing
- **[Service Mesh](service-mesh.md)** - Provides reliable message delivery infrastructure

---

**Previous**: [Service Mesh Pattern](service-mesh.md) | **Next**: [Service Discovery Pattern](service-discovery.md)