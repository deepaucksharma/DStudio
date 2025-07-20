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


## ✅ When to Use

### Ideal Scenarios
- **Distributed systems** with external dependencies
- **High-availability services** requiring reliability
- **External service integration** with potential failures
- **High-traffic applications** needing protection

### Environmental Factors
- **High Traffic**: System handles significant load
- **External Dependencies**: Calls to other services or systems
- **Reliability Requirements**: Uptime is critical to business
- **Resource Constraints**: Limited connections, threads, or memory

### Team Readiness
- Team understands distributed systems concepts
- Monitoring and alerting infrastructure exists
- Operations team can respond to pattern-related alerts

### Business Context
- Cost of downtime is significant
- User experience is a priority
- System is customer-facing or business-critical



## ❌ When NOT to Use

### Inappropriate Scenarios
- **Simple applications** with minimal complexity
- **Development environments** where reliability isn't critical
- **Single-user systems** without scale requirements
- **Internal tools** with relaxed availability needs

### Technical Constraints
- **Simple Systems**: Overhead exceeds benefits
- **Development/Testing**: Adds unnecessary complexity
- **Performance Critical**: Pattern overhead is unacceptable
- **Legacy Systems**: Cannot be easily modified

### Resource Limitations
- **No Monitoring**: Cannot observe pattern effectiveness
- **Limited Expertise**: Team lacks distributed systems knowledge
- **Tight Coupling**: System design prevents pattern implementation

### Anti-Patterns
- Adding complexity without clear benefit
- Implementing without proper monitoring
- Using as a substitute for fixing root causes
- Over-engineering simple problems



## ⚖️ Trade-offs

### Benefits vs Costs

| Benefit | Cost | Mitigation |
|---------|------|------------|
| **Improved Reliability** | Implementation complexity | Use proven libraries/frameworks |
| **Better Performance** | Resource overhead | Monitor and tune parameters |
| **Faster Recovery** | Operational complexity | Invest in monitoring and training |
| **Clearer Debugging** | Additional logging | Use structured logging |

### Performance Impact
- **Latency**: Small overhead per operation
- **Memory**: Additional state tracking
- **CPU**: Monitoring and decision logic
- **Network**: Possible additional monitoring calls

### Operational Complexity
- **Monitoring**: Need dashboards and alerts
- **Configuration**: Parameters must be tuned
- **Debugging**: Additional failure modes to understand
- **Testing**: More scenarios to validate

### Development Trade-offs
- **Initial Cost**: More time to implement correctly
- **Maintenance**: Ongoing tuning and monitoring
- **Testing**: Complex failure scenarios to validate
- **Documentation**: More concepts for team to understand



## 💻 Code Sample

### Basic Implementation

```python
class Queues_StreamingPattern:
    def __init__(self, config):
        self.config = config
        self.metrics = Metrics()
        self.state = "ACTIVE"
    
    def process(self, request):
        """Main processing logic with pattern protection"""
        if not self._is_healthy():
            return self._fallback(request)
        
        try:
            result = self._protected_operation(request)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            return self._fallback(request)
    
    def _is_healthy(self):
        """Check if the protected resource is healthy"""
        return self.metrics.error_rate < self.config.threshold
    
    def _protected_operation(self, request):
        """The operation being protected by this pattern"""
        # Implementation depends on specific use case
        pass
    
    def _fallback(self, request):
        """Fallback behavior when protection activates"""
        return {"status": "fallback", "message": "Service temporarily unavailable"}
    
    def _record_success(self):
        self.metrics.record_success()
    
    def _record_failure(self, error):
        self.metrics.record_failure(error)

# Usage example
pattern = Queues_StreamingPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
queues_streaming:
  enabled: true
  thresholds:
    failure_rate: 50%
    response_time: 5s
    error_count: 10
  timeouts:
    operation: 30s
    recovery: 60s
  fallback:
    enabled: true
    strategy: "cached_response"
  monitoring:
    metrics_enabled: true
    health_check_interval: 30s
```

### Testing the Implementation

```python
def test_queues_streaming_behavior():
    pattern = Queues_StreamingPattern(test_config)
    
    # Test normal operation
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
    
    # Test failure handling
    with mock.patch('external_service.call', side_effect=Exception):
        result = pattern.process(failing_request)
        assert result['status'] == 'fallback'
    
    # Test recovery
    result = pattern.process(normal_request)
    assert result['status'] == 'success'
```


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
