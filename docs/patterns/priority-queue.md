---
title: Priority Queue
description: Distributed priority queue systems that process messages based on importance rather than arrival order
type: pattern
category: communication
difficulty: intermediate
reading_time: 30 min
prerequisites: [message-queues, distributed-systems, data-structures]
when_to_use: Task scheduling, resource allocation, emergency systems, web crawling, job processing
when_not_to_use: Simple FIFO processing, when all messages have equal importance, low-latency requirements
status: complete
last_updated: 2025-07-24
---

# Priority Queue


## Overview

Priority queues in distributed systems ensure that high-importance messages are processed before lower-priority ones, regardless of arrival order. This pattern is essential for systems where message urgency varies dramatically, from emergency alerts to background maintenance tasks.

<div class="law-box">
<strong>Fairness vs Priority Constraint</strong>: Priority queues can lead to starvation of low-priority messages. Systems must balance urgency with fairness to prevent indefinite delays.
</div>

## The Priority Challenge

Traditional FIFO queues fail when message importance varies:

```python
# ❌ FIFO queue - processes by arrival order only
import queue
import time

fifo_queue = queue.Queue()

# Add messages with different priorities
fifo_queue.put("Low priority background task")
fifo_queue.put("Medium priority user request")  
fifo_queue.put("HIGH PRIORITY SECURITY ALERT!")
fifo_queue.put("Low priority log cleanup")

# FIFO processing ignores priority
while not fifo_queue.empty():
    message = fifo_queue.get()
    print(f"Processing: {message}")
    time.sleep(1)

# Output processes security alert 3rd, not 1st!
```

**Priority Queue Requirements**:
- **Ordered Processing**: Higher priority messages processed first
- **Starvation Prevention**: Ensure low-priority messages eventually process
- **Dynamic Priorities**: Support priority changes over time
- **Fair Scheduling**: Balance priority with arrival time
- **High Throughput**: Maintain performance under load

## Core Priority Queue Implementation

### Heap-Based Priority Queue

```python
import heapq
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum

class Priority(Enum):
    CRITICAL = 1    # System failures, security alerts
    HIGH = 2        # User-facing errors, SLA breaches
    MEDIUM = 3      # Regular user requests
    LOW = 4         # Background tasks, maintenance
    BULK = 5        # Batch processing, analytics

@dataclass
class PriorityMessage:
    priority: Priority
    message: Any
    created_at: datetime = field(default_factory=datetime.now)
    retry_count: int = 0
    max_retries: int = 3
    expires_at: Optional[datetime] = None
    
    def __lt__(self, other):
# Primary sort: priority (lower number = higher priority)
        if self.priority.value != other.priority.value:
            return self.priority.value < other.priority.value
        
# Secondary sort: creation time (older first for same priority)
        return self.created_at < other.created_at
    
    def is_expired(self) -> bool:
        return self.expires_at and datetime.now() > self.expires_at
    
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

class DistributedPriorityQueue:
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self._heap = []
        self._lock = threading.RLock()
        self._condition = threading.Condition(self._lock)
        
# Anti-starvation mechanism
        self._age_boost_threshold = timedelta(minutes=10)
        self._age_boost_factor = 0.5  # Boost priority by half a level
        
# Statistics
        self.stats = {
            'enqueued': 0,
            'dequeued': 0,
            'expired': 0,
            'retries': 0,
            'priority_counts': {p: 0 for p in Priority}
        }
        
# Start background maintenance
        self._maintenance_thread = threading.Thread(
            target=self._maintenance_loop, daemon=True
        )
        self._maintenance_thread.start()
    
    def enqueue(self, message: Any, priority: Priority, 
                expires_in: Optional[timedelta] = None) -> bool:
        """Add message to priority queue"""
        
        with self._condition:
            if len(self._heap) >= self.max_size:
# Queue full - could implement overflow strategies here
                return False
            
# Create priority message
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + expires_in
            
            priority_msg = PriorityMessage(
                priority=priority,
                message=message,
                expires_at=expires_at
            )
            
# Add to heap
            heapq.heappush(self._heap, priority_msg)
            
# Update statistics
            self.stats['enqueued'] += 1
            self.stats['priority_counts'][priority] += 1
            
# Notify waiting consumers
            self._condition.notify()
            
            return True
    
    def dequeue(self, timeout: Optional[float] = None) -> Optional[PriorityMessage]:
        """Remove highest priority message from queue"""
        
        with self._condition:
            start_time = time.time()
            
            while True:
# Clean expired messages
                self._clean_expired_messages()
                
                if self._heap:
# Get highest priority message
                    priority_msg = heapq.heappop(self._heap)
                    
# Check if message is expired
                    if priority_msg.is_expired():
                        self.stats['expired'] += 1
                        continue
                    
# Apply age-based priority boost
                    self._apply_age_boost(priority_msg)
                    
                    self.stats['dequeued'] += 1
                    self.stats['priority_counts'][priority_msg.priority] -= 1
                    
                    return priority_msg
                
# No messages available
                if timeout is None:
# Block until message available
                    self._condition.wait()
                else:
# Wait with timeout
                    elapsed = time.time() - start_time
                    remaining = timeout - elapsed
                    
                    if remaining <= 0:
                        return None
                    
                    if not self._condition.wait(remaining):
                        return None
    
    def requeue_failed(self, priority_msg: PriorityMessage) -> bool:
        """Requeue failed message with retry logic"""
        
        if not priority_msg.can_retry():
            return False
        
        with self._condition:
# Increment retry count
            priority_msg.retry_count += 1
            
# Lower priority for retries to prevent failed messages
# from blocking new high-priority messages
            if priority_msg.priority.value < 5:  # Don't lower BULK further
                retry_priority = Priority(priority_msg.priority.value + 1)
                priority_msg.priority = retry_priority
            
# Add exponential backoff delay
            delay_seconds = 2 ** priority_msg.retry_count
            priority_msg.created_at = datetime.now() + timedelta(seconds=delay_seconds)
            
# Re-add to heap
            heapq.heappush(self._heap, priority_msg)
            
            self.stats['retries'] += 1
            
            return True
    
    def _clean_expired_messages(self):
        """Remove expired messages from heap"""
        cleaned_heap = []
        
        for msg in self._heap:
            if not msg.is_expired():
                cleaned_heap.append(msg)
            else:
                self.stats['expired'] += 1
                self.stats['priority_counts'][msg.priority] -= 1
        
        self._heap = cleaned_heap
        heapq.heapify(self._heap)
    
    def _apply_age_boost(self, priority_msg: PriorityMessage):
        """Apply age-based priority boost to prevent starvation"""
        
        age = datetime.now() - priority_msg.created_at
        
        if age > self._age_boost_threshold:
# Boost priority for old messages
            if priority_msg.priority.value > 1:  # Don't boost CRITICAL further
                boosted_value = max(1, int(priority_msg.priority.value - self._age_boost_factor))
                priority_msg.priority = Priority(boosted_value)
    
    def _maintenance_loop(self):
        """Background maintenance thread"""
        while True:
            time.sleep(60)  # Run every minute
            
            with self._condition:
# Clean expired messages
                self._clean_expired_messages()
                
# Could add other maintenance tasks here:
# - Rebalance heap
# - Update metrics
# - Log statistics
    
    def size(self) -> int:
        """Get current queue size"""
        with self._lock:
            return len(self._heap)
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        with self._lock:
            return {
                **self.stats,
                'current_size': len(self._heap),
                'priority_distribution': dict(self.stats['priority_counts'])
            }

# Usage example
priority_queue = DistributedPriorityQueue()

# Add messages with different priorities
priority_queue.enqueue("Security breach detected!", Priority.CRITICAL)
priority_queue.enqueue("User login failed", Priority.HIGH)
priority_queue.enqueue("Process daily reports", Priority.LOW)
priority_queue.enqueue("User clicked button", Priority.MEDIUM)
priority_queue.enqueue("Background cleanup", Priority.BULK)

# Process messages in priority order
while priority_queue.size() > 0:
    msg = priority_queue.dequeue(timeout=1.0)
    if msg:
        print(f"Processing {msg.priority.name}: {msg.message}")
        
# Simulate processing failure and retry
        if "login failed" in str(msg.message) and msg.retry_count == 0:
            print(f"  Failed, retrying...")
            priority_queue.requeue_failed(msg)
        else:
            print(f"  Completed successfully")

print(f"Queue stats: {priority_queue.get_stats()}")
```

## Redis-Based Distributed Priority Queue

For multi-node systems, implement priority queues using Redis:

```python
import redis
import json
import time
from typing import Optional, Dict, Any

class RedisPriorityQueue:
    def __init__(self, redis_client: redis.Redis, queue_name: str):
        self.redis = redis_client
        self.queue_name = queue_name
        self.priority_key = f"{queue_name}:priorities"
        self.data_key = f"{queue_name}:data"
        self.stats_key = f"{queue_name}:stats"
        
# Use Redis sorted set for priority ordering
# Score = priority + (timestamp / 1e10) for tie-breaking
    
    def enqueue(self, message: Any, priority: int, 
                message_id: Optional[str] = None) -> str:
        """Add message to distributed priority queue"""
        
        if message_id is None:
            message_id = f"{int(time.time() * 1000000)}"  # Microsecond precision
        
# Calculate score: priority + small timestamp component
        timestamp_factor = time.time() / 1e10  # Very small for tie-breaking  
        score = priority + timestamp_factor
        
# Use Redis pipeline for atomicity
        pipe = self.redis.pipeline()
        
# Add to sorted set with priority score
        pipe.zadd(self.priority_key, {message_id: score})
        
# Store message data
        message_data = {
            'id': message_id,
            'data': message,
            'priority': priority,
            'created_at': time.time(),
            'retry_count': 0
        }
        pipe.hset(self.data_key, message_id, json.dumps(message_data))
        
# Update statistics
        pipe.hincrby(self.stats_key, 'enqueued', 1)
        pipe.hincrby(self.stats_key, f'priority_{priority}', 1)
        
        pipe.execute()
        
        return message_id
    
    def dequeue(self, timeout: float = 0) -> Optional[Dict[str, Any]]:
        """Remove highest priority message (lowest score)"""
        
        if timeout > 0:
# Blocking pop with timeout
            result = self.redis.bzpopmin(self.priority_key, timeout=timeout)
            if not result:
                return None
            
            _, message_id, score = result
            message_id = message_id.decode()
        else:
# Non-blocking pop
            result = self.redis.zpopmin(self.priority_key)
            if not result:
                return None
            
            message_id, score = result[0]
            message_id = message_id.decode()
        
# Get message data
        message_json = self.redis.hget(self.data_key, message_id)
        if not message_json:
            return None
        
        message_data = json.loads(message_json)
        
# Clean up message data
        self.redis.hdel(self.data_key, message_id)
        
# Update statistics
        self.redis.hincrby(self.stats_key, 'dequeued', 1)
        self.redis.hincrby(self.stats_key, f'priority_{message_data["priority"]}', -1)
        
        return message_data
    
    def requeue_with_backoff(self, message_data: Dict[str, Any]) -> bool:
        """Requeue failed message with exponential backoff"""
        
        message_data['retry_count'] += 1
        
        if message_data['retry_count'] > 3:  # Max retries
# Move to dead letter queue
            self.redis.lpush(f"{self.queue_name}:dlq", json.dumps(message_data))
            return False
        
# Calculate new priority (lower = higher priority number)
        backoff_delay = 2 ** message_data['retry_count']
        new_priority = message_data['priority'] + backoff_delay
        
# Re-enqueue with new priority
        self.enqueue(
            message_data['data'], 
            new_priority, 
            message_data['id']
        )
        
        self.redis.hincrby(self.stats_key, 'retries', 1)
        
        return True
    
    def peek_top(self, count: int = 1) -> List[Dict[str, Any]]:
        """Peek at top priority messages without removing them"""
        
# Get top message IDs
        message_ids = self.redis.zrange(self.priority_key, 0, count-1)
        
        messages = []
        for message_id in message_ids:
            message_json = self.redis.hget(self.data_key, message_id.decode())
            if message_json:
                messages.append(json.loads(message_json))
        
        return messages
    
    def size(self) -> int:
        """Get current queue size"""
        return self.redis.zcard(self.priority_key)
    
    def get_priority_distribution(self) -> Dict[str, int]:
        """Get message count by priority"""
        stats = self.redis.hgetall(self.stats_key)
        
        distribution = {}
        for key, value in stats.items():
            key = key.decode()
            if key.startswith('priority_'):
                priority = key.split('_')[1]
                distribution[priority] = int(value)
        
        return distribution

# Usage with Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_queue = RedisPriorityQueue(redis_client, 'task_queue')

# Add messages with different priorities
redis_queue.enqueue("Critical security alert", priority=1)
redis_queue.enqueue("User request", priority=3)
redis_queue.enqueue("Background job", priority=5)

# Process messages
while redis_queue.size() > 0:
    message = redis_queue.dequeue(timeout=1.0)
    if message:
        print(f"Processing priority {message['priority']}: {message['data']}")
```

## Advanced Priority Strategies

### Multi-Level Feedback Queue

```python
from collections import deque
import time

class MultilevelFeedbackQueue:
    def __init__(self, num_levels: int = 4):
        self.num_levels = num_levels
        self.queues = [deque() for _ in range(num_levels)]
        self.time_slices = [2**i for i in range(num_levels)]  # [1, 2, 4, 8]
        self.current_level = 0
        
# Round-robin tracking
        self.level_counters = [0] * num_levels
        self.max_counts = [2**i for i in range(num_levels)]  # [1, 2, 4, 8]
    
    def enqueue(self, message: Any, initial_priority: int = 0):
        """Add message to appropriate priority level"""
        level = min(initial_priority, self.num_levels - 1)
        
        priority_msg = {
            'message': message,
            'level': level,
            'time_used': 0,
            'created_at': time.time()
        }
        
        self.queues[level].append(priority_msg)
    
    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get next message using multilevel feedback algorithm"""
        
# Try higher priority levels first
        for level in range(self.num_levels):
            if self.queues[level] and self.level_counters[level] < self.max_counts[level]:
                message = self.queues[level].popleft()
                self.level_counters[level] += 1
                
# Reset lower level counters when processing higher priority
                for lower_level in range(level):
                    self.level_counters[lower_level] = 0
                
                return message
        
# Reset all counters if no messages processed
        self.level_counters = [0] * self.num_levels
        return None
    
    def feedback(self, message: Dict[str, Any], time_used: float, 
                completed: bool = False):
        """Provide feedback to adjust message priority"""
        
        if completed:
            return  # Message completed, no feedback needed
        
        message['time_used'] += time_used
        current_level = message['level']
        
# If message used full time slice, demote to lower priority
        if time_used >= self.time_slices[current_level]:
            new_level = min(current_level + 1, self.num_levels - 1)
            message['level'] = new_level
            self.queues[new_level].append(message)
        else:
# Message completed early, keep at same level
            self.queues[current_level].append(message)

# Usage example
mlfq = MultilevelFeedbackQueue()

# Add different types of messages
mlfq.enqueue("Interactive user request", 0)      # High priority
mlfq.enqueue("Batch processing job", 2)          # Low priority  
mlfq.enqueue("API call", 1)                      # Medium priority

# Process with feedback
while True:
    message = mlfq.dequeue()
    if not message:
        break
        
    print(f"Processing level {message['level']}: {message['message']}")
    
# Simulate processing time
    processing_time = 1.5
    time.sleep(0.1)  # Simulate work
    
# Provide feedback (message took longer than time slice)
    completed = processing_time < mlfq.time_slices[message['level']]
    mlfq.feedback(message, processing_time, completed)
```

### Deadline-Aware Priority Queue

```python
import heapq
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class DeadlineMessage:
    message: Any
    priority: int
    deadline: datetime
    created_at: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
# Calculate urgency score: combines priority and time to deadline
        now = datetime.now()
        
# Time pressure (0-1, higher = more urgent)
        self_time_pressure = max(0, min(1, 
            (self.deadline - now).total_seconds() / 
            (self.deadline - self.created_at).total_seconds()
        ))
        
        other_time_pressure = max(0, min(1,
            (other.deadline - now).total_seconds() /
            (other.deadline - other.created_at).total_seconds()
        ))
        
# Combined urgency score (lower = more urgent)
        self_urgency = self.priority * (2 - self_time_pressure)
        other_urgency = other.priority * (2 - other_time_pressure)
        
        return self_urgency < other_urgency
    
    def is_overdue(self) -> bool:
        return datetime.now() > self.deadline

class DeadlineAwarePriorityQueue:
    def __init__(self):
        self._heap = []
        self._lock = threading.RLock()
    
    def enqueue(self, message: Any, priority: int, deadline: datetime):
        """Add message with deadline consideration"""
        with self._lock:
            deadline_msg = DeadlineMessage(message, priority, deadline)
            heapq.heappush(self._heap, deadline_msg)
    
    def dequeue(self) -> Optional[DeadlineMessage]:
        """Get most urgent message considering deadline"""
        with self._lock:
# Clean overdue messages first
            self._clean_overdue()
            
            if self._heap:
                return heapq.heappop(self._heap)
            return None
    
    def _clean_overdue(self):
        """Remove overdue messages"""
        valid_messages = [msg for msg in self._heap if not msg.is_overdue()]
        self._heap = valid_messages
        heapq.heapify(self._heap)

# Usage with deadlines
deadline_queue = DeadlineAwarePriorityQueue()

# Add messages with different deadlines
now = datetime.now()
deadline_queue.enqueue("User request", 2, now + timedelta(seconds=30))
deadline_queue.enqueue("Background task", 5, now + timedelta(hours=1))  
deadline_queue.enqueue("Urgent alert", 1, now + timedelta(minutes=5))
deadline_queue.enqueue("Batch job", 4, now + timedelta(minutes=2))

# Messages will be processed considering both priority and deadline urgency
```

<div class="decision-box">
<strong>Decision Framework</strong>:

- **Task scheduling systems**: Multi-level feedback queue
- **Emergency response**: Deadline-aware priority queue
- **Distributed systems**: Redis-based priority queue
- **Real-time processing**: Heap-based with age boosting
- **Background job processing**: Simple priority levels
- **Web crawling**: Priority with politeness constraints
</div>

## Trade-offs

| Approach | Fairness | Performance | Complexity | Starvation Risk |
|----------|----------|-------------|------------|-----------------|
| Simple Priority | Low | Very High | Low | High |
| Age-Boosted | High | High | Medium | Low |
| Multi-level Feedback | High | Medium | High | Very Low |
| Deadline-Aware | Medium | Medium | High | Medium |
| Redis Distributed | Medium | High | Medium | Medium |

## Anti-Starvation Techniques

### Age-Based Priority Boost
```python
def calculate_aged_priority(original_priority: int, age_seconds: int) -> int:
# Boost priority based on age
    age_boost = min(2, age_seconds / 3600)  # Max 2 level boost per hour
    return max(1, original_priority - age_boost)
```

### Fair Queuing
```python
class FairPriorityQueue:
    def __init__(self):
        self.priority_queues = {p: deque() for p in Priority}
        self.last_served = {p: 0 for p in Priority}
        self.service_ratios = {
            Priority.CRITICAL: 10,  # 10x more service
            Priority.HIGH: 5,       # 5x more service  
            Priority.MEDIUM: 2,     # 2x more service
            Priority.LOW: 1,        # Base service rate
            Priority.BULK: 0.5      # Half service rate
        }
    
    def dequeue_fair(self) -> Optional[PriorityMessage]:
# Calculate which priority level deserves next service
        now = time.time()
        
        best_priority = None
        best_ratio = float('inf')
        
        for priority in Priority:
            if self.priority_queues[priority]:
# Time since last served this priority
                time_since = now - self.last_served[priority]
                expected_ratio = self.service_ratios[priority]
                
# Deficit: how underserved is this priority?
                deficit = time_since * expected_ratio
                
                if deficit < best_ratio:
                    best_ratio = deficit
                    best_priority = priority
        
        if best_priority:
            self.last_served[best_priority] = now
            return self.priority_queues[best_priority].popleft()
        
        return None
```

## Performance Optimizations

### Batch Processing
```python
class BatchPriorityQueue:
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.queue = DistributedPriorityQueue()
    
    def dequeue_batch(self, max_batch_size: Optional[int] = None) -> List[PriorityMessage]:
        """Dequeue multiple messages for batch processing"""
        batch_size = max_batch_size or self.batch_size
        batch = []
        
        for _ in range(batch_size):
            msg = self.queue.dequeue(timeout=0.1)
            if msg is None:
                break
            batch.append(msg)
        
        return batch
    
    def process_batch(self, batch: List[PriorityMessage]):
        """Process messages in batch for efficiency"""
# Group by priority for efficient processing
        priority_groups = {}
        for msg in batch:
            if msg.priority not in priority_groups:
                priority_groups[msg.priority] = []
            priority_groups[msg.priority].append(msg)
        
# Process each priority group
        for priority in sorted(priority_groups.keys()):
            messages = priority_groups[priority]
            print(f"Batch processing {len(messages)} {priority.name} messages")
            
# Process all messages of same priority together
            self._process_priority_batch(messages)
    
    def _process_priority_batch(self, messages: List[PriorityMessage]):
        """Process messages of same priority efficiently"""
        for msg in messages:
# Simulate processing
            print(f"  Processing: {msg.message}")
```

## Related Patterns
- Distributed Queue (Coming Soon) - Scaling message queues
- [Load Balancing](load-balancing.md) - Request distribution
- [Circuit Breaker](circuit-breaker.md) - Failure handling
- [URL Frontier](url-frontier.md) - Web crawler priority management

## References
- [Priority Queue Data Structures](https://en.wikipedia.org/wiki/Priority_queue)
- [Multilevel Feedback Queue](https://en.wikipedia.org/wiki/Multilevel_feedback_queue)
- [Redis Sorted Sets for Priority Queues](https://redis.io/docs/data-types/sorted-sets/)
- [Fair Queuing Algorithms](https://en.wikipedia.org/wiki/Fair_queuing)