# Queues & Stream-Processing

**Decoupling work from workers since 1958**

## THE PROBLEM

```
Direct coupling creates cascading failures:
Client → Service A → Service B → Database
         ↓ Failure    ↓ Blocked   ↓ Overload
     Timeout      Backpressure   Death
```

## THE SOLUTION

```
Queues break temporal coupling:
Client → Queue → Service A → Queue → Service B
         ↓ Buffered         ↓ Decoupled
     Returns fast      Independent scaling
```

## Core Queue Patterns

```
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

```
Throughput: 100K-1M msg/sec (Kafka)
Latency: 1-10ms typical
Durability: Configurable (memory/disk)
Ordering: Per-partition guaranteed
```