---
title: Queues & Stream-Processing
description: 2. PUBLISH-SUBSCRIBE (Topics)
   Producer → [M1|M2|M3] → Consumer 1
                        ↘ Consumer 2
   Each consumer gets all messages
type: pattern
difficulty: beginner
reading_time: 15 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Queues & Stream-Processing**


# Queues & Stream-Processing

**Decoupling work from workers since 1958**

## THE PROBLEM

```proto
Direct coupling creates cascading failures:
Client → Service A → Service B → Database
         ↓ Failure    ↓ Blocked   ↓ Overload
     Timeout      Backpressure   Death
```

## THE SOLUTION

```proto
Queues break temporal coupling:
Client → Queue → Service A → Queue → Service B
         ↓ Buffered         ↓ Decoupled
     Returns fast      Independent scaling
```

## Core Queue Patterns

```proto
1. POINT-TO-POINT (Work Queue)
   Producer → [M1|M2|M3|M4] → Consumer
   Each message processed once

2. PUBLISH-SUBSCRIBE (Topics)
   Producer → [M1|M2|M3] → Consumer 1
                        ↘ Consumer 2
   Each consumer gets all messages

3. STREAMING (Ordered Log)
   Producer → [M1→M2→M3→M4...] → Consumer
                               ↗ Replay from offset
   Persistent, replayable
```

## IMPLEMENTATION

```python
class ResilientQueue:
    def __init__(self, max_size=10000, overflow_strategy='reject'):
        self.queue = deque(maxlen=max_size if overflow_strategy == 'drop' else None)
        self.max_size = max_size
        self.overflow_strategy = overflow_strategy
        self.metrics = {
            'enqueued': 0,
            'dequeued': 0,
            'rejected': 0,
            'dropped': 0
        }
        
    def enqueue(self, message):
        if self.overflow_strategy == 'reject' and len(self.queue) >= self.max_size:
            self.metrics['rejected'] += 1
            raise QueueFullError("Queue at capacity")
            
        self.queue.append({
            'id': str(uuid4()),
            'timestamp': time.time(),
            'attempts': 0,
            'message': message
        })
        self.metrics['enqueued'] += 1
        
    def dequeue(self, timeout=None):
        start = time.time()
        while True:
            try:
                item = self.queue.popleft()
                self.metrics['dequeued'] += 1
                return item
            except IndexError:
                if timeout and (time.time() - start) > timeout:
                    return None
                time.sleep(0.01)
    
    def ack(self, message_id):
        # In real system, would remove from in-flight set
        pass
    
    def nack(self, message_id, requeue=True):
        # In real system, would requeue or DLQ
        pass

# Stream processor example
class StreamProcessor:
    def __init__(self, source_queue, sink_queue, processor_fn):
        self.source = source_queue
        self.sink = sink_queue
        self.processor = processor_fn
        self.running = False
        
    def start(self, num_workers=1):
        self.running = True
        workers = []
        for i in range(num_workers):
            w = threading.Thread(target=self._worker, args=(i,))
            w.start()
            workers.append(w)
        return workers
    
    def _worker(self, worker_id):
        while self.running:
            msg = self.source.dequeue(timeout=1)
            if msg:
                try:
                    result = self.processor(msg['message'])
                    self.sink.enqueue(result)
                    self.source.ack(msg['id'])
                except Exception as e:
                    print(f"Worker {worker_id} error: {e}")
                    self.source.nack(msg['id'])
```

## Kafka-Style Log Implementation

```python
class CommitLog:
    def __init__(self, partition_count=16):
        self.partitions = [[] for _ in range(partition_count)]
        self.offsets = {i: 0 for i in range(partition_count)}
        
    def append(self, key, value):
        partition = hash(key) % len(self.partitions)
        offset = len(self.partitions[partition])
        
        self.partitions[partition].append({
            'offset': offset,
            'key': key,
            'value': value,
            'timestamp': time.time()
        })
        
        return partition, offset
    
    def consume(self, partition, offset):
        if partition >= len(self.partitions):
            raise ValueError(f"Invalid partition {partition}")
            
        messages = []
        partition_log = self.partitions[partition]
        
        for i in range(offset, len(partition_log)):
            messages.append(partition_log[i])
            
        return messages
    
    def consumer_group(self, group_id, partitions):
        """Manages offsets for consumer groups"""
        if group_id not in self.offsets:
            self.offsets[group_id] = {p: 0 for p in partitions}
            
        messages = []
        for partition in partitions:
            msgs = self.consume(partition, self.offsets[group_id][partition])
            messages.extend(msgs)
            if msgs:
                self.offsets[group_id][partition] = msgs[-1]['offset'] + 1
                
        return messages
```

## ✓ CHOOSE THIS WHEN:
• Variable load (handles spikes)  
• Producers/consumers scale differently
• Need resilience to downstream failures
• Ordering matters (streaming)
• Want replay capability

## ⚠️ BEWARE OF:
• Queue overflow (monitor depth!)
• Poison messages (need DLQ)
• Out-of-order processing (partitions)
• Latency addition (queue wait)
• Split-brain consumers

## REAL EXAMPLES
• **Uber**: 1M+ rides/min through Kafka
• **LinkedIn**: 7 trillion messages/day
• **Netflix**: Kinesis for real-time analytics

## Performance Characteristics

```yaml
Throughput: 100K-1M msg/sec (Kafka)
Latency: 1-10ms typical
Durability: Configurable (memory/disk)
Ordering: Per-partition guaranteed
```

---

**Previous**: [← Pattern Catalog Quiz](pattern-quiz.md) | **Next**: [Rate Limiting Pattern →](rate-limiting.md)
---

## 💪 Hands-On Exercises

### Exercise 1: Pattern Recognition ⭐⭐
**Time**: ~15 minutes  
**Objective**: Identify Queues & Stream-Processing in existing systems

**Task**: 
Find 2 real-world examples where Queues & Stream-Processing is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Design an implementation of Queues & Stream-Processing

**Scenario**: You need to implement Queues & Stream-Processing for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Queues & Stream-Processing
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Evaluate when NOT to use Queues & Stream-Processing

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Queues & Stream-Processing be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Queues & Stream-Processing later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Queues & Stream-Processing in your preferred language.
- Focus on core functionality
- Include basic error handling
- Add simple logging

### Intermediate: Production Features  
Extend the basic implementation with:
- Configuration management
- Metrics collection
- Unit tests
- Documentation

### Advanced: Performance & Scale
Optimize for production use:
- Handle concurrent access
- Implement backpressure
- Add monitoring hooks
- Performance benchmarks

---

## 🎯 Real-World Application

**Project Integration**: 
- How would you introduce Queues & Stream-Processing to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
