---
title: Work Distribution Examples
description: "Real-world examples and case studies demonstrating the concepts in practice"
type: pillar
difficulty: intermediate
reading_time: 30 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Work](/part2-pillars/work/) → **Work Distribution Examples**

# Work Distribution Examples

## Real-World Case Studies

### 1. Spotify's Microservices Journey

**Context**: Spotify evolved from 100 engineers in 2012 to 1,800+ in 2020

**Problem**: Monolithic backend couldn't scale with team growth

**Solution Architecture**:
```proto
Before (2012):
┌─────────────────────────────┐
│    Monolithic Backend       │
│  - User Management          │
│  - Music Catalog            │
│  - Playlists               │
│  - Recommendations         │
│  - Payment Processing      │
└─────────────────────────────┘

After (2020):
┌─────────┐ ┌─────────┐ ┌──────────┐
│  User   │ │Playlist │ │ Payment  │
│ Service │ │ Service │ │ Service  │
└─────────┘ └─────────┘ └──────────┘
     │           │            │
┌─────────────────────────────────┐
│        Event Bus (Kafka)        │
└─────────────────────────────────┘
     │           │            │
┌─────────┐ ┌─────────┐ ┌──────────┐
│ Music   │ │Recommend│ │Analytics │
│ Catalog │ │ Engine  │ │ Service  │
└─────────┘ └─────────┘ └──────────┘
```

**Key Decisions**:
- Autonomous squads own services end-to-end
- Async communication via event streaming
- Service mesh for discovery and routing
- Independent deployment cycles

**Results**:
- Deploy frequency: 1/week → 1000+/day
- Time to production: Months → Hours
- Availability: 99.95% → 99.99%

### 2. Uber's Geospatial Work Distribution

**Problem**: Match riders with drivers in real-time at global scale

**Work Distribution Strategy**:
```python
# City-level sharding
class GeoShardRouter:
    def route_request(self, location):
        # H3 hexagonal hierarchical spatial index
        cell_id = h3.geo_to_h3(location.lat, location.lng, resolution=7)
        shard = self.cell_to_shard_map[cell_id]
        return self.shards[shard]

# Dynamic work stealing for load balancing
class WorkStealer:
    def balance_load(self):
        for shard in self.overloaded_shards():
            # Find neighboring shard with capacity
            neighbor = self.find_underloaded_neighbor(shard)
            if neighbor:
                # Transfer edge cells
                cells = shard.get_edge_cells(toward=neighbor)
                self.transfer_cells(cells, from_shard=shard, to_shard=neighbor)
```

**Metrics**:
- 15M+ rides daily
- <15 second dispatch time
- 99.99% match success rate

### 3. Discord's Message Distribution

**Challenge**: Distribute chat messages to millions of concurrent users

**Architecture Evolution**:

**Gen 1: Simple Fanout (2015)**
```python
def send_message(channel_id, message):
    users = get_channel_users(channel_id)
    for user in users:
        send_to_user(user, message)  # O(n) problem
```

**Gen 2: Guild Sharding (2017)**
```python
class GuildWorker:
    def __init__(self, guild_id):
        self.guild_id = guild_id
        self.websockets = {}  # user_id -> connection

    def broadcast_message(self, channel_id, message):
        # Only users in this guild
        users = self.get_channel_users(channel_id)
        # Bulk send to local connections
        self.batch_send(users, message)
```

**Gen 3: Consistent Hashing + Read Replicas (2020)**
```python
class MessageRouter:
    def route_message(self, guild_id, message):
        # Primary handles writes
        primary = self.hash_ring.get_node(guild_id)
        primary.write_message(message)

        # Replicas handle reads
        replicas = self.hash_ring.get_replicas(guild_id, count=3)
        for replica in replicas:
            replica.replicate_async(message)
```

### 4. MapReduce at Google

**Original Paper Implementation (2004)**

```python
# Classic word count example
def map_function(document):
    for word in document.split():
        emit(word, 1)

def reduce_function(word, counts):
    return sum(counts)

# Framework handles distribution
class MapReduceJob:
    def execute(self, input_files):
        # Phase 1: Map
        map_tasks = []
        for file in input_files:
            task = self.create_map_task(file, map_function)
            map_tasks.append(self.submit_to_worker(task))

        # Barrier: Wait for all maps
        self.wait_all(map_tasks)

        # Phase 2: Shuffle
        self.shuffle_intermediate_data()

        # Phase 3: Reduce
        reduce_tasks = []
        for key in self.get_unique_keys():
            task = self.create_reduce_task(key, reduce_function)
            reduce_tasks.append(self.submit_to_worker(task))

        return self.collect_results(reduce_tasks)
```

## Code Examples

### 1. Work Stealing Queue Implementation

```python
import threading
from collections import deque
from random import choice

class WorkStealingQueue:
    """
    Each worker has its own queue
    Workers steal from others when idle
    """
    def __init__(self, worker_id, all_queues):
        self.worker_id = worker_id
        self.local_queue = deque()
        self.all_queues = all_queues
        self.lock = threading.Lock()

    def push(self, task):
        """Owner pushes to bottom"""
        with self.lock:
            self.local_queue.append(task)

    def pop(self):
        """Owner pops from bottom"""
        with self.lock:
            if self.local_queue:
                return self.local_queue.pop()
        return None

    def steal(self):
        """Others steal from top"""
        with self.lock:
            if self.local_queue:
                return self.local_queue.popleft()
        return None

    def get_work(self):
        """Try local first, then steal"""
        # Try local queue
        task = self.pop()
        if task:
            return task

        # Try stealing from others
        other_queues = [q for q in self.all_queues
                       if q.worker_id != self.worker_id]

        # Random victim selection
        for _ in range(len(other_queues)):
            victim = choice(other_queues)
            task = victim.steal()
            if task:
                return task

        return None
```

### 2. Consistent Hashing for Work Distribution

```python
import hashlib
import bisect

class ConsistentHash:
    def __init__(self, nodes=None, virtual_nodes=150):
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node):
        """Add node with virtual nodes for better distribution"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
            bisect.insort(self.sorted_keys, hash_value)

    def remove_node(self, node):
        """Remove node and all its virtual nodes"""
        for i in range(self.virtual_nodes):
            virtual_key = f"{node}:{i}"
            hash_value = self._hash(virtual_key)
            if hash_value in self.ring:
                del self.ring[hash_value]
                self.sorted_keys.remove(hash_value)

    def get_node(self, key):
        """Find node responsible for key"""
        if not self.ring:
            return None

        hash_value = self._hash(key)

        # Find first node clockwise from hash
        index = bisect.bisect_right(self.sorted_keys, hash_value)
        if index == len(self.sorted_keys):
            index = 0

        return self.ring[self.sorted_keys[index]]

    def get_nodes(self, key, count=3):
        """Get N nodes for replication"""
        if not self.ring:
            return []

        nodes = []
        hash_value = self._hash(key)
        index = bisect.bisect_right(self.sorted_keys, hash_value)

        while len(nodes) < count and len(nodes) < len(set(self.ring.values())):
            if index >= len(self.sorted_keys):
                index = 0

            node = self.ring[self.sorted_keys[index]]
            if node not in nodes:
                nodes.append(node)

            index += 1

        return nodes
```

### 3. Batch Processing with Backpressure

```python
import asyncio
from typing import List, Callable

class BatchProcessor:
    def __init__(self,
                 process_fn: Callable,
                 batch_size: int = 100,
                 batch_timeout: float = 1.0,
                 max_pending: int = 10000):
        self.process_fn = process_fn
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.max_pending = max_pending

        self.pending = []
        self.semaphore = asyncio.Semaphore(max_pending)
        self.flush_task = None

    async def submit(self, item):
        """Submit item with backpressure"""
        await self.semaphore.acquire()

        self.pending.append(item)

        # Start flush timer if needed
        if not self.flush_task:
            self.flush_task = asyncio.create_task(
                self._flush_after_timeout()
            )

        # Flush if batch is full
        if len(self.pending) >= self.batch_size:
            await self._flush()

    async def _flush_after_timeout(self):
        """Flush partial batch after timeout"""
        await asyncio.sleep(self.batch_timeout)
        if self.pending:
            await self._flush()

    async def _flush(self):
        """Process current batch"""
        if not self.pending:
            return

        # Cancel timeout task
        if self.flush_task:
            self.flush_task.cancel()
            self.flush_task = None

        # Process batch
        batch = self.pending
        self.pending = []

        try:
            await self.process_fn(batch)
        finally:
            # Release semaphore for processed items
            for _ in batch:
                self.semaphore.release()

# Usage example
async def process_batch(items: List[dict]):
    """Simulate batch processing"""
    print(f"Processing batch of {len(items)} items")
    await asyncio.sleep(0.1)  # Simulate work

async def main():
    processor = BatchProcessor(
        process_fn=process_batch,
        batch_size=50,
        batch_timeout=0.5
    )

    # Simulate high-throughput submissions
    async def producer():
        for i in range(1000):
            await processor.submit({"id": i, "data": f"item-{i}"})
            await asyncio.sleep(0.001)  # 1000 items/sec

    await producer()
    await processor._flush()  # Final flush
```

### 4. Hierarchical Work Distribution

```python
class HierarchicalScheduler:
    """
    Two-level scheduling like Google's Borg
    """
    def __init__(self):
        self.clusters = {}
        self.global_queue = []

    class Cluster:
        def __init__(self, cluster_id, capacity):
            self.cluster_id = cluster_id
            self.capacity = capacity
            self.used = 0
            self.machines = {}
            self.local_queue = []

        def can_fit(self, job):
            return self.used + job.resources <= self.capacity

        def schedule_locally(self, job):
            # Find best machine using bin packing
            best_machine = None
            min_waste = float('inf')

            for machine in self.machines.values():
                if machine.can_fit(job):
                    waste = machine.capacity - machine.used - job.resources
                    if waste < min_waste:
                        min_waste = waste
                        best_machine = machine

            if best_machine:
                best_machine.assign(job)
                self.used += job.resources
                return True

            return False

    def submit_job(self, job):
        # Global scheduling decision
        suitable_clusters = [
            c for c in self.clusters.values()
            if c.can_fit(job)
        ]

        if not suitable_clusters:
            self.global_queue.append(job)
            return False

        # Score clusters (simplified)
        def score_cluster(cluster):
            # Prefer clusters with:
            # 1. Better locality
            # 2. Lower utilization
            # 3. Fewer queued jobs
            locality_score = job.get_locality_score(cluster)
            utilization = cluster.used / cluster.capacity
            queue_penalty = len(cluster.local_queue) * 0.1

            return locality_score - utilization - queue_penalty

        best_cluster = max(suitable_clusters, key=score_cluster)

        # Delegate to cluster scheduler
        if best_cluster.schedule_locally(job):
            return True
        else:
            best_cluster.local_queue.append(job)
            return True
```

## Anti-Patterns and Solutions

### 1. The "Distributed Monolith"

**Anti-Pattern**: Services that can't be deployed independently

```python
# BAD: Tight coupling through shared database
class OrderService:
    def create_order(self, order):
        # Direct DB writes to multiple domains
        self.db.execute("INSERT INTO orders ...")
        self.db.execute("UPDATE inventory ...")  # Wrong!
        self.db.execute("UPDATE user_credits ...")  # Wrong!

# GOOD: Event-driven choreography
class OrderService:
    def create_order(self, order):
        # Own domain only
        self.db.execute("INSERT INTO orders ...")

        # Publish events for others
        self.publish_event("OrderCreated", {
            "order_id": order.id,
            "items": order.items,
            "user_id": order.user_id
        })
```

### 2. The "Chatty Services"

**Anti-Pattern**: Too many synchronous calls

```python
# BAD: N+1 API calls
def get_feed(user_id):
    posts = post_service.get_posts(user_id)
    for post in posts:
        post.author = user_service.get_user(post.author_id)  # N calls!
        post.likes = like_service.get_likes(post.id)  # N more calls!
    return posts

# GOOD: Batch and cache
def get_feed(user_id):
    posts = post_service.get_posts(user_id)

    # Batch fetch
    author_ids = [p.author_id for p in posts]
    authors = user_service.get_users_batch(author_ids)

    # Local join
    author_map = {a.id: a for a in authors}
    for post in posts:
        post.author = author_map[post.author_id]

    return posts
```

### 3. The "Big Ball of Mud" in Microservices

**Anti-Pattern**: No clear boundaries

**Solution**: Domain-Driven Design
```python
# Define bounded contexts
class BoundedContext:
    def __init__(self, name, capabilities):
        self.name = name
        self.capabilities = capabilities
        self.owned_data = []
        self.published_events = []
        self.consumed_events = []

# Example contexts
contexts = [
    BoundedContext("Order Management", [
        "Create Order",
        "Update Order Status",
        "Cancel Order"
    ]),
    BoundedContext("Inventory", [
        "Reserve Stock",
        "Release Stock",
        "Update Stock Levels"
    ]),
    BoundedContext("Payments", [
        "Process Payment",
        "Refund Payment",
        "Payment Reconciliation"
    ])
]
```

## Performance Comparisons

### Synchronous vs Asynchronous Work Distribution

```python
import time
import asyncio
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor

# Synchronous approach
def sync_fetch_all(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.text)
    return results

# Threaded approach
def threaded_fetch_all(urls):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(requests.get, url) for url in urls]
        return [f.result().text for f in futures]

# Async approach
async def async_fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_one(session, url):
    async with session.get(url) as response:
        return await response.text()

# Performance comparison
urls = ["http://example.com"] * 100

# Sync: ~50 seconds (sequential)
# Threaded: ~5 seconds (limited by thread count)
# Async: ~0.5 seconds (truly concurrent)
```

## Key Takeaways

1. **Work distribution is about physics** - Network latency and data locality matter more than algorithms

2. **Conway's Law is real** - Your work distribution will mirror your organization structure

3. **Async > Sync for I/O** - But sync is simpler for CPU-bound work

4. **Batching amortizes costs** - But adds latency

5. **Stealing > Pushing** - Work stealing provides better load balancing

6. **Events > RPC for decoupling** - But add complexity

Remember: The best work distribution strategy depends on your specific constraints. Measure, don't guess.
