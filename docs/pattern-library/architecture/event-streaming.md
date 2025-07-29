---
title: Event Streaming
description: Process infinite streams of events in real-time with scalable, fault-tolerant architectures
type: pattern
category: data-processing
difficulty: advanced
reading_time: 45 min
prerequisites: [distributed-systems, message-queues, event-driven-architecture]
when_to_use: When you need real-time processing, continuous computation, or event-driven architectures at scale
when_not_to_use: For simple request-response patterns or when batch processing is sufficient
status: complete
last_updated: 2025-01-26
excellence_tier: silver
pattern_status: use-with-expertise
introduced: 2011-01
current_relevance: mainstream
trade_offs:
  pros:
    - "Enables real-time processing and analytics"
    - "Handles unbounded data streams"
    - "Powerful for event-driven architectures"
  cons:
    - "Steep learning curve and operational complexity"
    - "Requires expertise in distributed systems"
    - "Difficult to debug and test"
best_for: "Real-time analytics, IoT data processing, event-driven microservices"
implementations:
  - company: LinkedIn
    scale: "Apache Kafka creator, 7T messages/day"
  - company: Uber
    scale: "Flink for dynamic pricing"
  - company: Netflix
    scale: "Keystone platform, 500B events/day"
---

# Event Streaming Pattern

!!! warning "🥈 Silver Tier Pattern"
    **Powerful but complex streaming solution**
    
    Event streaming provides unmatched capabilities for real-time processing but comes with significant complexity. Requires deep expertise in distributed systems, careful capacity planning, and robust monitoring.
    
    **Best suited for:**
    - Real-time analytics and monitoring
    - IoT and sensor data processing
    - Event-driven microservices
    - Teams with streaming expertise

<div class="pattern-type">Data Processing Pattern</div>

Build systems that process continuous, unbounded streams of events in real-time, enabling reactive architectures and real-time analytics at scale.

## Problem Context

!!! warning "🎯 The Challenge"

    Modern systems generate continuous streams of events that traditional batch processing can't handle:
    
    - **Unbounded data**: No clear beginning or end
    - **Real-time requirements**: Millisecond latency processing
    - **High volume**: Millions of events per second
    - **Out-of-order arrival**: Network delays cause temporal disorder
    - **Exactly-once semantics**: Each event must be processed exactly once
    - **Distributed state**: Maintain consistency across stream processors

## Core Concepts

### Event Streaming vs Batch Processing

```mermaid
graph LR
    subgraph "Batch Processing"
        B1[Collect Data] --> B2[Store Data]
        B2 --> B3[Process Batch]
        B3 --> B4[Output Results]
        B4 --> B5[Wait for Next Batch]
        B5 --> B1
    end
    
    subgraph "Stream Processing"
        S1[Event Arrives] --> S2[Process Immediately]
        S2 --> S3[Update State]
        S3 --> S4[Emit Result]
        S4 --> S1
    end
    
    style B1 fill:#ff9999
    style B2 fill:#ff9999
    style B3 fill:#ff9999
    style S1 fill:#99ff99
    style S2 fill:#99ff99
    style S3 fill:#99ff99
```

<table class="comparison-table">
<thead>
<tr>
<th>Aspect</th>
<th>Batch Processing</th>
<th>Stream Processing</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Data Model</strong></td>
<td>Bounded datasets</td>
<td>Unbounded streams</td>
</tr>
<tr>
<td><strong>Latency</strong></td>
<td>Minutes to hours</td>
<td>Milliseconds to seconds</td>
</tr>
<tr>
<td><strong>Throughput</strong></td>
<td>Very high (optimized)</td>
<td>High (continuous)</td>
</tr>
<tr>
<td><strong>State Management</strong></td>
<td>Between batches</td>
<td>Continuous, distributed</td>
</tr>
<tr>
<td><strong>Reprocessing</strong></td>
<td>Simple (re-run batch)</td>
<td>Complex (replay stream)</td>
</tr>
<tr>
<td><strong>Use Cases</strong></td>
<td>ETL, reporting, ML training</td>
<td>Real-time analytics, monitoring, CEP</td>
</tr>
</tbody>
</table>

### Stream Components

```mermaid
graph TB
    subgraph "Event Producers"
        P1[Web Servers]
        P2[IoT Sensors]
        P3[Mobile Apps]
        P4[Databases<br/>CDC]
    end
    
    subgraph "Event Bus"
        EB[Event Stream<br/>Kafka/Pulsar/Kinesis]
        T1[Topic: Orders]
        T2[Topic: Clicks]
        T3[Topic: Sensors]
    end
    
    subgraph "Stream Processors"
        SP1[Filter]
        SP2[Transform]
        SP3[Aggregate]
        SP4[Join]
        SP5[Pattern<br/>Detect]
    end
    
    subgraph "Consumers"
        C1[Real-time<br/>Dashboard]
        C2[Alert<br/>System]
        C3[Data<br/>Lake]
        C4[ML<br/>Model]
    end
    
    P1 --> EB
    P2 --> EB
    P3 --> EB
    P4 --> EB
    
    EB --> T1
    EB --> T2
    EB --> T3
    
    T1 --> SP1
    T2 --> SP2
    T3 --> SP3
    
    SP1 --> SP4
    SP2 --> SP4
    SP3 --> SP5
    
    SP4 --> C1
    SP5 --> C2
    SP4 --> C3
    SP5 --> C4
```

## Architecture Patterns

### 1. Lambda Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        DS[Event Stream]
    end
    
    subgraph "Lambda Architecture"
        subgraph "Speed Layer"
            RT[Real-time<br/>Processing]
            RV[Real-time<br/>Views]
        end
        
        subgraph "Batch Layer"
            BT[Batch<br/>Processing]
            BV[Batch<br/>Views]
        end
        
        subgraph "Serving Layer"
            SL[Query<br/>Service]
            MV[Merged<br/>Views]
        end
    end
    
    DS --> RT
    DS --> BT
    RT --> RV
    BT --> BV
    RV --> MV
    BV --> MV
    MV --> SL
```

### 2. Kappa Architecture

```mermaid
graph TB
    subgraph "Kappa Architecture"
        ES[Event Stream] --> SP[Stream<br/>Processing]
        SP --> SV[Serving<br/>Views]
        
        ES --> RP[Reprocess<br/>Stream]
        RP --> NV[New<br/>Views]
        
        NV -.->|Replace| SV
    end
    
    style SP fill:#99ff99
    style RP fill:#ffff99
```

### 3. Event Sourcing Integration

```mermaid
graph LR
    subgraph "Commands"
        C1[Create Order]
        C2[Update Status]
        C3[Cancel Order]
    end
    
    subgraph "Event Store"
        ES[Event Log<br/>Kafka]
    end
    
    subgraph "Stream Processing"
        SP1[Order<br/>Projector]
        SP2[Analytics<br/>Processor]
        SP3[Notification<br/>Handler]
    end
    
    subgraph "Read Models"
        RM1[Order<br/>View]
        RM2[Analytics<br/>Dashboard]
    end
    
    C1 --> ES
    C2 --> ES
    C3 --> ES
    
    ES --> SP1
    ES --> SP2
    ES --> SP3
    
    SP1 --> RM1
    SP2 --> RM2
    SP3 --> |Send| N[Notifications]
```

## Technology Comparison

### Stream Processing Platforms

<table class="tech-comparison">
<thead>
<tr>
<th>Technology</th>
<th>Architecture</th>
<th>Throughput</th>
<th>Latency</th>
<th>Durability</th>
<th>Best For</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Apache Kafka</strong></td>
<td>Distributed log</td>
<td>1M+ msg/sec</td>
<td>2-10ms</td>
<td>Replicated</td>
<td>Event bus, log aggregation</td>
</tr>
<tr>
<td><strong>Apache Pulsar</strong></td>
<td>Segmented storage</td>
<td>1M+ msg/sec</td>
<td>5-15ms</td>
<td>BookKeeper</td>
<td>Multi-tenancy, geo-replication</td>
</tr>
<tr>
<td><strong>AWS Kinesis</strong></td>
<td>Managed shards</td>
<td>1K-1M rec/sec</td>
<td>70-200ms</td>
<td>3 AZ replication</td>
<td>AWS ecosystem, serverless</td>
</tr>
<tr>
<td><strong>Redis Streams</strong></td>
<td>In-memory</td>
<td>100K+ msg/sec</td>
<td><1ms</td>
<td>Optional</td>
<td>Low latency, simple streams</td>
</tr>
</tbody>
</table>

### Processing Frameworks

```mermaid
graph TB
    subgraph "Processing Models"
        subgraph "Native Streaming"
            F1[Apache Flink]
            F2[Kafka Streams]
        end
        
        subgraph "Micro-batch"
            S1[Spark Streaming]
            S2[Structured Streaming]
        end
        
        subgraph "Actor-based"
            A1[Akka Streams]
            A2[Orleans]
        end
    end
    
    style F1 fill:#99ff99
    style F2 fill:#99ff99
    style S1 fill:#ffff99
    style S2 fill:#ffff99
```

## Stream Processing Patterns

### 1. Windowing

```mermaid
graph LR
    subgraph "Event Stream"
        E1[e1] --> E2[e2] --> E3[e3] --> E4[e4] --> E5[e5] --> E6[e6] --> E7[e7] --> E8[e8]
    end
    
    subgraph "Tumbling Windows"
        TW1[Window 1<br/>e1,e2,e3] 
        TW2[Window 2<br/>e4,e5,e6]
        TW3[Window 3<br/>e7,e8]
    end
    
    subgraph "Sliding Windows"
        SW1[Window 1<br/>e1,e2,e3,e4]
        SW2[Window 2<br/>e3,e4,e5,e6]
        SW3[Window 3<br/>e5,e6,e7,e8]
    end
    
    subgraph "Session Windows"
        SE1[Session 1<br/>e1,e2]
        SE2[Session 2<br/>e4,e5,e6]
        SE3[Session 3<br/>e8]
    end
```

### 2. Watermarks and Late Data

```mermaid
graph TD
    subgraph "Event Time Progress"
        ET[Event Time: 12:00:00]
        WT[Watermark: 11:59:50<br/>10s behind]
        
        E1[Event<br/>11:59:45] -->|On Time| P1[Process]
        E2[Event<br/>11:59:55] -->|On Time| P2[Process]
        E3[Event<br/>11:59:40] -->|Late| L1[Late Handler]
    end
    
    style E1 fill:#99ff99
    style E2 fill:#99ff99
    style E3 fill:#ff9999
```

### 3. Exactly-Once Processing

```mermaid
stateDiagram-v2
    [*] --> Reading: Read Event
    Reading --> Processing: Begin Transaction
    Processing --> Checkpointing: Process Event
    Checkpointing --> Committing: Save State
    Committing --> [*]: Commit Offset
    
    Processing --> Rollback: Failure
    Checkpointing --> Rollback: Failure
    Rollback --> Reading: Retry
```

## Real-World Examples

### Netflix Real-Time Analytics

<div class="failure-vignette">
<h4>📊 Netflix Streaming Metrics</h4>

**Scale**: 200M+ subscribers, billions of events/day

**Architecture**:
- Apache Kafka for event ingestion
- Apache Flink for stream processing
- Druid for real-time analytics

**Challenges Solved**:
- Global event ordering
- Multi-region aggregation
- Sub-second dashboards

**Key Metrics**:
- 4M events/second peak
- 50ms p99 latency
- 99.99% processing guarantee
</div>

### Uber Dynamic Pricing

```mermaid
graph TB
    subgraph "Event Sources"
        D[Driver<br/>Locations]
        R[Ride<br/>Requests]
        T[Traffic<br/>Data]
    end
    
    subgraph "Stream Processing"
        subgraph "Apache Flink"
            A[Area<br/>Aggregator]
            S[Supply<br/>Calculator]
            P[Price<br/>Engine]
        end
    end
    
    subgraph "Output"
        PM[Price<br/>Model]
        UI[Rider<br/>App]
        DA[Driver<br/>App]
    end
    
    D --> A
    R --> A
    T --> A
    
    A --> S
    S --> P
    
    P --> PM
    PM --> UI
    PM --> DA
```

**Performance Metrics**:
- Latency: < 1 second price updates
- Throughput: 100K+ events/second
- Accuracy: 95%+ demand prediction

### LinkedIn Real-Time Anomaly Detection

<div class="decision-box">
<h4>🔍 LinkedIn Security Monitoring</h4>

**Problem**: Detect account takeovers in real-time

**Solution**:
```mermaid
graph LR
    L[Login Events] --> K[Kafka]
    K --> S[Samza<br/>Processor]
    S --> ML[ML Model<br/>Scoring]
    ML --> A{Anomaly?}
    A -->|Yes| Alert[Security<br/>Alert]
    A -->|No| Log[Audit<br/>Log]
```

**Results**:
- 90% reduction in detection time
- 50ms average processing latency
- 99.9% accuracy rate
</div>

## Implementation Guide

### Basic Stream Processor

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio

@dataclass
class StreamEvent:
    key: str
    value: Any
    timestamp: datetime
    headers: Dict[str, str] = None

class StreamProcessor(ABC):
    """Base class for stream processors"""
    
    @abstractmethod
    async def process(self, event: StreamEvent) -> Optional[StreamEvent]:
        pass

class FilterProcessor(StreamProcessor):
    """Filter events based on predicate"""
    def __init__(self, predicate):
        self.predicate = predicate
    
    async def process(self, event: StreamEvent) -> Optional[StreamEvent]:
        if self.predicate(event):
            return event
        return None

class MapProcessor(StreamProcessor):
    """Transform event values"""
    def __init__(self, mapper):
        self.mapper = mapper
    
    async def process(self, event: StreamEvent) -> Optional[StreamEvent]:
        transformed = await self.mapper(event.value)
        return StreamEvent(
            key=event.key,
            value=transformed,
            timestamp=event.timestamp,
            headers=event.headers
        )

class StreamPipeline:
    """Chain multiple processors"""
    def __init__(self):
        self.processors = []
    
    def add_processor(self, processor: StreamProcessor):
        self.processors.append(processor)
        return self
    
    async def process(self, event: StreamEvent) -> Optional[StreamEvent]:
        current = event
        for processor in self.processors:
            if current is None:
                break
            current = await processor.process(current)
        return current
```

### Windowed Aggregation

```python
from collections import defaultdict
from datetime import timedelta
import heapq

class WindowedAggregator:
    """Time-based windowed aggregation"""
    
    def __init__(self, window_size: timedelta, slide: timedelta = None):
        self.window_size = window_size
        self.slide = slide or window_size
        self.windows = defaultdict(list)
        self.watermark = datetime.min
        self.late_events = 0
    
    def process_event(self, event: StreamEvent) -> List[Dict]:
        """Process event and return completed windows"""
        # Update watermark
        self.watermark = max(self.watermark, 
                           event.timestamp - timedelta(seconds=10))
        
        # Check if event is late
        if event.timestamp < self.watermark:
            self.late_events += 1
            return []
        
        # Assign to windows
        window_start = self._get_window_start(event.timestamp)
        self.windows[window_start].append(event)
        
        # Check for completed windows
        completed = []
        for start, events in list(self.windows.items()):
            if start + self.window_size <= self.watermark:
                # Window is complete
                result = self._aggregate(events)
                completed.append({
                    'window_start': start,
                    'window_end': start + self.window_size,
                    'result': result,
                    'event_count': len(events)
                })
                del self.windows[start]
        
        return completed
    
    def _get_window_start(self, timestamp: datetime) -> datetime:
        """Calculate window start time"""
        epoch = datetime(1970, 1, 1)
        window_ms = int(self.window_size.total_seconds() * 1000)
        ts_ms = int((timestamp - epoch).total_seconds() * 1000)
        window_start_ms = (ts_ms // window_ms) * window_ms
        return epoch + timedelta(milliseconds=window_start_ms)
    
    def _aggregate(self, events: List[StreamEvent]) -> Any:
        """Override this for custom aggregation"""
        return len(events)  # Default: count
```

### State Management

```python
class StatefulProcessor:
    """Processor with managed state"""
    
    def __init__(self, state_backend):
        self.state_backend = state_backend
        self.pending_checkpoints = []
    
    async def process_with_state(self, event: StreamEvent):
        """Process event with exactly-once semantics"""
        # Begin transaction
        tx = await self.state_backend.begin_transaction()
        
        try:
            # Get current state
            state = await tx.get(event.key)
            
            # Process event
            new_state = await self.update_state(state, event)
            
            # Update state
            await tx.put(event.key, new_state)
            
            # Commit transaction
            await tx.commit()
            
            return new_state
        except Exception as e:
            # Rollback on failure
            await tx.rollback()
            raise e
    
    async def update_state(self, state: Any, event: StreamEvent) -> Any:
        """Override this for custom state updates"""
        if state is None:
            state = {'count': 0, 'sum': 0}
        
        state['count'] += 1
        state['sum'] += event.value
        return state
```

## Performance Optimization

### Partitioning Strategy

```mermaid
graph TB
    subgraph "Input Stream"
        IS[1M events/sec]
    end
    
    subgraph "Partitioning"
        P[Partitioner<br/>hash(key) % N]
    end
    
    subgraph "Parallel Processing"
        PP1[Partition 1<br/>200K/sec]
        PP2[Partition 2<br/>200K/sec]
        PP3[Partition 3<br/>200K/sec]
        PP4[Partition 4<br/>200K/sec]
        PP5[Partition 5<br/>200K/sec]
    end
    
    IS --> P
    P --> PP1
    P --> PP2
    P --> PP3
    P --> PP4
    P --> PP5
```

### Backpressure Handling

<table class="strategy-table">
<thead>
<tr>
<th>Strategy</th>
<th>Implementation</th>
<th>Pros</th>
<th>Cons</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Rate Limiting</strong></td>
<td>Limit input rate</td>
<td>Simple, predictable</td>
<td>May drop events</td>
</tr>
<tr>
<td><strong>Buffering</strong></td>
<td>Queue events</td>
<td>No data loss</td>
<td>Memory pressure</td>
</tr>
<tr>
<td><strong>Dynamic Scaling</strong></td>
<td>Add processors</td>
<td>Handles spikes</td>
<td>Complex, costly</td>
</tr>
<tr>
<td><strong>Sampling</strong></td>
<td>Process subset</td>
<td>Reduces load</td>
<td>Loses accuracy</td>
</tr>
</tbody>
</table>

## When to Use vs Message Queues

### Decision Matrix

```mermaid
graph TD
    Start[Data Processing<br/>Requirement] --> Q1{Unbounded<br/>Stream?}
    
    Q1 -->|Yes| Q2{Real-time<br/>Required?}
    Q1 -->|No| MQ[Use Message Queue]
    
    Q2 -->|Yes| Q3{Complex<br/>Processing?}
    Q2 -->|No| MQ
    
    Q3 -->|Yes| ES[Use Event Streaming]
    Q3 -->|No| Q4{High<br/>Volume?}
    
    Q4 -->|Yes| ES
    Q4 -->|No| MQ
    
    style ES fill:#99ff99
    style MQ fill:#ffff99
```

### Comparison Table

<table class="comparison-table">
<thead>
<tr>
<th>Aspect</th>
<th>Event Streaming</th>
<th>Message Queues</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Data Model</strong></td>
<td>Continuous streams</td>
<td>Discrete messages</td>
</tr>
<tr>
<td><strong>Processing</strong></td>
<td>Stateful, windowed</td>
<td>Stateless, per-message</td>
</tr>
<tr>
<td><strong>Ordering</strong></td>
<td>Per-partition ordering</td>
<td>FIFO or priority</td>
</tr>
<tr>
<td><strong>Replay</strong></td>
<td>Full replay capability</td>
<td>Limited/no replay</td>
</tr>
<tr>
<td><strong>Use Cases</strong></td>
<td>Analytics, CEP, ETL</td>
<td>Task queues, RPC</td>
</tr>
</tbody>
</table>

## Common Pitfalls

<div class="failure-vignette">
<h4>⚠️ Late Data Handling</h4>

**Problem**: Events arrive after window closes

**Symptoms**:
- Missing data in aggregations
- Incorrect results
- Customer complaints

**Solution**:
```mermaid
graph LR
    E[Late Event] --> W{Within<br/>Allowed<br/>Lateness?}
    W -->|Yes| R[Recompute<br/>Window]
    W -->|No| S[Side<br/>Output]
    R --> U[Update<br/>Results]
    S --> L[Late Data<br/>Stream]
```
</div>

## Best Practices

<div class="axiom-box">
<h4>🎯 Stream Processing Guidelines</h4>

1. **Design for Failure**
   - Checkpointing strategy
   - Idempotent operations
   - Dead letter queues

2. **Optimize State**
   - Minimize state size
   - Use appropriate backends
   - Regular compaction

3. **Monitor Everything**
   - Lag metrics
   - Throughput/latency
   - State size
   - Rebalancing events

4. **Handle Time Properly**
   - Event time > processing time
   - Appropriate watermarks
   - Late data strategy
</div>

## Implementation Checklist

- [ ] **Event Design**
  - [ ] Define event schema
  - [ ] Choose serialization format
  - [ ] Plan versioning strategy

- [ ] **Processing Logic**
  - [ ] Select time semantics
  - [ ] Design windowing strategy
  - [ ] Plan state management
  - [ ] Implement exactly-once

- [ ] **Infrastructure**
  - [ ] Choose streaming platform
  - [ ] Design partitioning
  - [ ] Plan scaling strategy
  - [ ] Set up monitoring

- [ ] **Operations**
  - [ ] Checkpointing configuration
  - [ ] Backpressure handling
  - [ ] Replay procedures
  - [ ] Failure recovery

## Related Patterns

- [Event-Driven Architecture](event-driven.md) - Architectural style using events
- [Event Sourcing](event-sourcing.md) - Store state as event sequence
- [CQRS](cqrs.md) - Separate read/write models
- [Saga Pattern](saga.md) - Distributed transactions
- [Message Queue Case Study](../case-studies/distributed-message-queue.md) - Deep dive into queuing

## References

- "Streaming Systems" - Tyler Akidau, Slava Chernyak, Reuven Lax
- "Designing Data-Intensive Applications" - Martin Kleppmann
- "Kafka: The Definitive Guide" - Neha Narkhede, Gwen Shapira, Todd Palino
- Apache Flink Documentation
- Google Dataflow Model Paper