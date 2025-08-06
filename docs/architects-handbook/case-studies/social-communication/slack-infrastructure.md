---
title: 'Slack''s Infrastructure: Real-time Messaging at Scale'
description: How Slack built infrastructure to deliver millions of messages with sub-second
  latency
type: case-study
difficulty: intermediate
reading_time: 30 min
prerequisites: []
status: complete
last_updated: 2025-07-28
excellence_tier: silver
scale_category: large-scale
domain: messaging
company: Slack
year_implemented: 2013
current_status: production
metrics:
  daily_active_users: 20M+
  messages_per_day: 1B+
  concurrent_connections: 10M+
  latency_p99: 100ms
  uptime: 99.99%
  teams: 750K+
patterns_used:
  silver:
  - websocket: Maintains 10M+ persistent connections for real-time delivery
  - message-queue: Kafka handles 1B+ messages/day with ordering guarantees
  - sharding: Channel-based sharding for horizontal scaling
  - cache-aside: Redis caches active channel data
  - event-sourcing: Complete message history with search
  gold:
  - circuit-breaker: Prevents cascade failures in service mesh
  - rate-limiting: Protects against spam and abuse
  bronze:
  - polling: Fallback for websocket failures
trade_offs:
  pros:
  - Real-time message delivery with presence
  - Scalable to millions of concurrent users
  - Rich message history and search
  - Reliable with multiple fallback mechanisms
  cons:
  - Complex infrastructure with many moving parts
  - High operational overhead for real-time features
  - Memory intensive for connection management
  - Challenging data consistency across shards
best_for:
- Real-time collaborative applications
- Team communication platforms
- Applications requiring persistent connections
- Rich messaging with history and search
excellence_guides:
- scale/large-scale
- ../../../pattern-library/real-time-systems
- architecture/messaging
key_innovations:
- 'Flannel: Custom websocket gateway for connection management'
- Channel-based sharding for team isolation
- Lazy loading of message history
- Graceful degradation during outages
lessons_learned:
- category: Architecture
  lesson: Websockets at scale require careful connection management
- category: Operations
  lesson: Real-time systems need multiple fallback mechanisms
- category: Performance
  lesson: Channel-based sharding provides natural boundaries
---

# Slack's Infrastructure: Real-time Messaging at Scale

!!! success "Excellence Badge"
    🥈 **Silver Tier**: Proven patterns with careful trade-off management

!!! abstract "Quick Facts"
    | Metric | Value |
    |--------|-------|
    | **Users** | 20M+ daily active |
    | **Messages** | 1B+ per day |
    | **Connections** | 10M+ concurrent |
    | **Teams** | 750K+ organizations |
    | **Latency** | <100ms p99 |

## Executive Summary

Slack transformed team communication by building a real-time messaging platform that feels instant. Through innovations like Flannel (their websocket gateway), channel-based sharding, and graceful degradation, Slack maintains millions of persistent connections while delivering messages in under 100ms. This case study explores how they built infrastructure that scales while maintaining the responsiveness users expect.

## System Architecture

### High-Level Overview

```mermaid
graph TB
    subgraph "Client Layer"
        D[Desktop] --> WS[WebSocket]
        M[Mobile] --> WS
        W[Web] --> WS
    end
    
    subgraph "Edge Layer"
        WS --> F[Flannel Gateway]
        F --> LB[Load Balancer]
    end
    
    subgraph "Service Layer"
        LB --> MS[Message Service]
        LB --> PS[Presence Service]
        LB --> NS[Notification Service]
        
        MS --> K[Kafka]
        MS --> R[Redis Cache]
        MS --> DB[MySQL Shards]
    end
    
    style F fill:#ff9800
    style K fill:#4caf50
    style R fill:#f44336
```

### Key Components

| Component | Purpose | Scale |
|-----------|---------|-------|
| **Flannel** | WebSocket gateway | 10M+ connections |
| **Kafka** | Message queue | 1B+ messages/day |
| **Redis** | Channel cache | 100K+ ops/sec |
| **MySQL** | Message storage | 100TB+ data |
| **Elasticsearch** | Message search | 1B+ documents |

## Technical Deep Dive

### WebSocket Management

=== "Connection Handling"
    ```go
    // Flannel gateway connection manager
    type ConnectionManager struct {
        connections map[string]*WSConnection
        mu sync.RWMutex
    }
    
    func (cm *ConnectionManager) HandleConnection(ws *websocket.Conn, userID string) {
        conn := &WSConnection{
            ws: ws,
            userID: userID,
            channels: make(map[string]bool),
            send: make(chan []byte, 256),
        }
        
        cm.mu.Lock()
        cm.connections[userID] = conn
        cm.mu.Unlock()
        
        // Start goroutines for read/write
        go conn.readPump()
        go conn.writePump()
    }
    ```

=== "Message Routing"
    ```python
    class MessageRouter:
        def route_message(self, message):
            # Determine target channels
            channel_id = message['channel_id']
            
            # Get channel members
            members = self.redis.smembers(f'channel:{channel_id}:members')
            
            # Find active connections
            for member in members:
                if connection := self.flannel.get_connection(member):
                    # Direct delivery via WebSocket
                    connection.send(message)
                else:
                    # Queue for offline delivery
                    self.queue_offline_message(member, message)
    ```

=== "Graceful Degradation"
    ```python
    class GracefulDegradation:
        def deliver_message(self, user_id, message):
            strategies = [
                self.websocket_delivery,
                self.long_polling_delivery,
                self.push_notification,
                self.email_notification
            ]
            
            for strategy in strategies:
                try:
                    if strategy(user_id, message):
                        return True
                except Exception as e:
                    logger.warning(f"Strategy {strategy} failed: {e}")
            
            return False
    ```

### Sharding Strategy

```mermaid
graph TB
    subgraph "Channel-Based Sharding"
        T[Team] --> C1[Channel 1]
        T --> C2[Channel 2]
        T --> C3[Channel 3]
        
        C1 --> S1[Shard 1]
        C2 --> S2[Shard 2]
        C3 --> S1
    end
    
    subgraph "Benefits"
        B1[Team Isolation]
        B2[Linear Scaling]
        B3[Simple Routing]
    end
    
    style T fill:#2196f3
    style S1,S2 fill:#4caf50
```

### Message Flow

```mermaid
sequenceDiagram
    participant User
    participant Flannel
    participant API
    participant Kafka
    participant Redis
    participant MySQL
    participant Recipients
    
    User->>Flannel: Send message
    Flannel->>API: Validate & process
    API->>Kafka: Publish to topic
    API->>Redis: Update channel cache
    
    par Async Processing
        Kafka->>MySQL: Persist message
    and
        Kafka->>Recipients: Fan-out delivery
    end
    
    Recipients-->>User: Delivery confirmation
```

## Performance Optimization

### Caching Strategy

| Cache Layer | Data | TTL | Hit Rate |
|-------------|------|-----|----------|
| **Connection Cache** | User -> Server mapping | 5 min | 95% |
| **Channel Cache** | Active channel members | 1 min | 90% |
| **Message Cache** | Recent messages | 30 min | 80% |
| **User Cache** | Profile data | 1 hour | 85% |

### Trade-off Analysis

```mermaid
graph LR
    subgraph "Real-time Delivery"
        RT[WebSocket] --> RTP[Pros: Instant, Efficient]
        RT --> RTC[Cons: Complex, Stateful]
    end
    
    subgraph "Reliability"
        R[Message Queue] --> RP[Pros: Durable, Ordered]
        R --> RC[Cons: Latency, Complexity]
    end
    
    subgraph "Scalability"
        S[Sharding] --> SP[Pros: Horizontal Scale]
        S --> SC[Cons: Cross-shard Queries]
    end
```

## Operational Challenges

### Challenge 1: Connection Storms

**Problem**: Mass reconnections after outages

**Solution**:
```python
class ConnectionThrottler:
    def __init__(self, rate_limit=1000):
        self.rate_limit = rate_limit
        self.window = TokenBucket(rate_limit)
    
    def accept_connection(self, client_id):
        # Exponential backoff for reconnections
        backoff = self.calculate_backoff(client_id)
        
        if self.window.try_consume(1):
            return True, 0
        else:
            return False, backoff
```

### Challenge 2: Message Ordering

**Problem**: Messages arriving out of order across shards

**Solution**: Channel-scoped ordering with Kafka partitions

```python
def get_partition(channel_id):
    # All messages for a channel go to same partition
    return hash(channel_id) % NUM_PARTITIONS

# Kafka producer config
producer.send(
    topic='messages',
    key=channel_id,  # Ensures ordering
    value=message,
    partition=get_partition(channel_id)
)
```

### Challenge 3: Search at Scale

```mermaid
graph TB
    subgraph "Search Architecture"
        Q[Query] --> S[Search Service]
        S --> ES1[ES Cluster 1]
        S --> ES2[ES Cluster 2]
        S --> ES3[ES Cluster 3]
        
        K[Kafka] --> I[Indexer]
        I --> ES1
        I --> ES2
        I --> ES3
    end
    
    style S fill:#ff9800
    style I fill:#4caf50
```

## Best Practices Implemented

### 1. Graceful Degradation

✅ **Multiple Delivery Paths**
- Primary: WebSocket
- Fallback 1: Long polling
- Fallback 2: Push notifications
- Fallback 3: Email digest

### 2. Resource Management

```python
# Connection limits per server
MAX_CONNECTIONS_PER_SERVER = 50000
CONNECTION_IDLE_TIMEOUT = 300  # 5 minutes
MESSAGE_BUFFER_SIZE = 256

# Memory optimization
class ConnectionPool:
    def __init__(self):
        self.pool = []
        self.max_size = 1000
    
    def get_connection(self):
        if self.pool:
            return self.pool.pop()
        return self.create_connection()
    
    def return_connection(self, conn):
        if len(self.pool) < self.max_size:
            conn.reset()
            self.pool.append(conn)
```

### 3. Monitoring and Alerting

| Metric | Alert Threshold | Response |
|--------|-----------------|----------|
| **Connection Count** | >45K per server | Scale out |
| **Message Latency** | >200ms p99 | Investigate bottleneck |
| **Kafka Lag** | >10K messages | Add consumers |
| **Cache Hit Rate** | <80% | Warm cache |
| **Error Rate** | >0.1% | Page on-call |

## Migration Path

### From Polling to WebSockets

```mermaid
graph LR
    subgraph "Phase 1"
        P1[100% Polling]
    end
    
    subgraph "Phase 2"
        P2["80% Polling<br/>20% WebSocket"]
    end
    
    subgraph "Phase 3"
        P3["20% Polling<br/>80% WebSocket"]
    end
    
    subgraph "Phase 4"
        P4["100% WebSocket<br/>(Polling fallback)"]
    end
    
    P1 --> P2 --> P3 --> P4
```

## Lessons for Your Architecture

### When to Use This Approach

✅ **Good Fit**
- Real-time collaboration needs
- Millions of concurrent users
- Rich message history requirements
- Team/channel-based isolation

❌ **Consider Alternatives**
- Simple request/response patterns (use REST)
- Batch processing needs (use queues)
- Very high message rates (>1M/sec)
- Strict ordering across all messages

### Implementation Checklist

- [ ] Design connection management strategy
- [ ] Implement multiple delivery mechanisms
- [ ] Plan sharding strategy early
- [ ] Build comprehensive monitoring
- [ ] Test failure scenarios
- [ ] Plan for connection storms
- [ ] Implement message ordering
- [ ] Design cache warming strategy

## Related Resources

- [WebSocket Pattern](../../../pattern-library/communication/websocket.md)
- [Message Queue Pattern](../../../pattern-library/message-queue.md)
- [Sharding Pattern](../../../pattern-library/scaling/sharding.md)
- [Building Slack's Architecture](https://slack.engineering/)

---

*"Real-time messaging is not just about speed, it's about reliability at speed." - Slack Engineering*