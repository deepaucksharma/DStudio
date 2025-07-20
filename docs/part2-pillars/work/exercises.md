---
title: Work Distribution Exercises
description: <details>
<summary>Solution Approach</summary>
type: pillar
difficulty: beginner
reading_time: 20 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part II: Pillars](/part2-pillars/) → [Work](/part2-pillars/work/) → **Work Distribution Exercises**

# Work Distribution Exercises

## Exercise 1: Design a Video Processing Pipeline

**Scenario**: You're building a video processing service that needs to:
- Accept video uploads (100MB - 10GB files)
- Transcode to multiple formats (1080p, 720p, 480p)
- Generate thumbnails every 10 seconds
- Extract subtitles using speech recognition
- Scan for inappropriate content

**Constraints**:
- 10,000 videos uploaded daily
- 95% of videos are under 1GB
- Users expect processing within 30 minutes
- Budget: $50,000/month for infrastructure

**Tasks**:
1. Design the work distribution architecture
2. Calculate required compute resources
3. Handle failure scenarios
4. Optimize for the 95% case while handling outliers

**Considerations**:
- Should you split videos into chunks?
- How do you handle priority users?
- What happens if a worker dies mid-processing?
- How do you prevent reprocessing?

<details>
<summary>Solution Approach</summary>

```python
class VideoProcessor:
    def __init__(self):
        self.chunk_size = 60  # seconds
        self.workers = ConsistentHash()
        self.job_tracker = JobTracker()

    def process_video(self, video_id, video_url):
        # 1. Split into chunks for parallel processing
        metadata = self.get_video_metadata(video_url)
        chunks = self.split_into_chunks(metadata.duration)

        # 2. Create job DAG
        job = {
            'id': video_id,
            'chunks': chunks,
            'tasks': {
                'download': {'status': 'pending'},
                'split': {'status': 'pending', 'depends': ['download']},
                'transcode': {
                    '1080p': {'status': 'pending', 'depends': ['split']},
                    '720p': {'status': 'pending', 'depends': ['split']},
                    '480p': {'status': 'pending', 'depends': ['split']}
                },
                'thumbnails': {'status': 'pending', 'depends': ['split']},
                'speech': {'status': 'pending', 'depends': ['split']},
                'content_scan': {'status': 'pending', 'depends': ['split']},
                'merge': {'status': 'pending',
                         'depends': ['transcode', 'thumbnails', 'speech', 'content_scan']}
            }
        }

        # 3. Distribute work
        self.job_tracker.create(job)
        self.enqueue_ready_tasks(job)

    def enqueue_ready_tasks(self, job):
        for task_name, task in job['tasks'].items():
            if task['status'] == 'pending':
                deps_met = all(
                    job['tasks'][dep]['status'] == 'completed'
                    for dep in task.get('depends', [])
                )
                if deps_met:
                    worker = self.workers.get_node(f"{job['id']}:{task_name}")
                    self.send_to_worker(worker, job['id'], task_name)
```

**Resource Calculation**:
- 10,000 videos/day ≈ 417 videos/hour
- Assuming 30-min SLA, need to process 208 videos concurrently
- Each video needs ~4 CPU cores for 20 minutes
- Total: ~800 CPU cores required
- With 20% headroom: 1,000 cores
- Using c5.4xlarge (16 vCPUs): 63 instances
- Cost: ~$30,000/month for compute

</details>

## Exercise 2: Distributed Web Crawler

**Scenario**: Build a web crawler that:
- Crawls 1 million pages per day
- Respects robots.txt and rate limits
- Extracts structured data (title, meta, links)
- Handles JavaScript-rendered pages
- Maintains crawl frontier efficiently

**Design Questions**:
1. How do you distribute URLs among workers?
2. How do you prevent duplicate crawling?
3. How do you handle politeness (rate limiting per domain)?
4. How do you manage the frontier (URLs to crawl)?

**Implementation Task**:
Complete this distributed crawler framework:

```python
class DistributedCrawler:
    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.url_frontier = PriorityQueue()
        self.seen_urls = BloomFilter(capacity=100_000_000)
        self.domain_locks = {}

    def add_urls(self, urls):
        """Add URLs to frontier with priority"""
        # TODO: Implement URL filtering and priority assignment
        pass

    def get_next_url(self, worker_id):
        """Get next URL for worker respecting rate limits"""
        # TODO: Implement work distribution with per-domain rate limiting
        pass

    def mark_complete(self, url, extracted_links):
        """Process crawl results"""
        # TODO: Handle extracted links and update frontier
        pass

    def handle_failure(self, url, error):
        """Handle crawl failures"""
        # TODO: Implement retry logic with exponential backoff
        pass
```

<details>
<summary>Solution</summary>

```python
import time
import heapq
from collections import defaultdict
from urllib.parse import urlparse

class DistributedCrawler:
    def __init__(self, num_workers):
        self.num_workers = num_workers
        self.url_frontier = []  # Heap of (priority, timestamp, url)
        self.seen_urls = BloomFilter(capacity=100_000_000)
        self.domain_last_access = defaultdict(float)
        self.domain_delay = defaultdict(lambda: 1.0)  # Default 1 second
        self.retry_counts = defaultdict(int)

    def add_urls(self, urls):
        """Add URLs to frontier with priority"""
        current_time = time.time()

        for url in urls:
            # Skip if seen
            if url in self.seen_urls:
                continue

            self.seen_urls.add(url)

            # Calculate priority
            domain = urlparse(url).netloc
            priority = self.calculate_priority(url, domain)

            # Calculate earliest crawl time
            last_access = self.domain_last_access[domain]
            delay = self.domain_delay[domain]
            earliest_time = max(current_time, last_access + delay)

            # Add to frontier
            heapq.heappush(self.url_frontier, (earliest_time, priority, url))

    def calculate_priority(self, url, domain):
        """Higher score = higher priority (negated for min heap)"""
        score = 0

        # Prioritize new domains
        if domain not in self.domain_last_access:
            score += 100

        # Prioritize shorter URLs (likely more important)
        score -= len(url) * 0.1

        # Deprioritize based on retry count
        score -= self.retry_counts[url] * 50

        return -score  # Negate for min heap

    def get_next_url(self, worker_id):
        """Get next URL for worker respecting rate limits"""
        current_time = time.time()

        # Clean up expired entries
        while self.url_frontier:
            earliest_time, priority, url = self.url_frontier[0]

            # If not ready yet, no URLs available
            if earliest_time > current_time:
                return None

            # Pop the URL
            heapq.heappop(self.url_frontier)

            # Update domain access time
            domain = urlparse(url).netloc
            self.domain_last_access[domain] = current_time

            return url

        return None

    def mark_complete(self, url, extracted_links):
        """Process crawl results"""
        # Reset retry count on success
        self.retry_counts[url] = 0

        # Add new URLs to frontier
        self.add_urls(extracted_links)

    def handle_failure(self, url, error):
        """Handle crawl failures"""
        self.retry_counts[url] += 1

        # Exponential backoff
        if self.retry_counts[url] <= 3:
            retry_delay = (2 ** self.retry_counts[url]) * 60  # 2, 4, 8 minutes
            retry_time = time.time() + retry_delay

            # Re-add to frontier with lower priority
            domain = urlparse(url).netloc
            priority = self.calculate_priority(url, domain)
            heapq.heappush(self.url_frontier, (retry_time, priority, url))

    def update_crawl_delay(self, domain, delay):
        """Update rate limit for domain (from robots.txt)"""
        self.domain_delay[domain] = max(delay, 0.1)  # Minimum 100ms
```

</details>

## Exercise 3: Load Balancer Implementation

**Task**: Implement a load balancer that supports multiple strategies:

```python
class LoadBalancer:
    def __init__(self, servers, strategy='round_robin'):
        self.servers = servers
        self.strategy = strategy
        # TODO: Initialize strategy-specific state

    def select_server(self, request=None):
        """Select a server based on strategy"""
        if self.strategy == 'round_robin':
            # TODO: Implement round-robin selection
            pass
        elif self.strategy == 'least_connections':
            # TODO: Implement least-connections selection
            pass
        elif self.strategy == 'weighted_round_robin':
            # TODO: Implement weighted selection
            pass
        elif self.strategy == 'consistent_hash':
            # TODO: Implement consistent hashing
            pass
        elif self.strategy == 'least_response_time':
            # TODO: Implement response-time based selection
            pass

    def mark_server_down(self, server):
        """Handle server failure"""
        # TODO: Remove server and redistribute load
        pass

    def add_server(self, server):
        """Handle server addition"""
        # TODO: Add server and rebalance
        pass
```

**Requirements**:
1. Round-robin with equal distribution
2. Least connections with accurate tracking
3. Weighted round-robin based on server capacity
4. Consistent hashing with minimal redistribution
5. Response time tracking with exponential weighted average

<details>
<summary>Solution</summary>

```python
import hashlib
import bisect
from collections import defaultdict

class LoadBalancer:
    def __init__(self, servers, strategy='round_robin'):
        self.servers = servers
        self.strategy = strategy
        self.active_servers = set(servers)

        # Strategy-specific initialization
        self.round_robin_counter = 0
        self.connections = defaultdict(int)
        self.weights = {s: s.weight if hasattr(s, 'weight') else 1 for s in servers}
        self.weighted_counter = 0

        # Response time tracking
        self.response_times = defaultdict(lambda: 0.0)
        self.response_counts = defaultdict(int)
        self.ewma_alpha = 0.3  # Exponential weighted moving average

        # Consistent hashing
        self.hash_ring = {}
        self.sorted_hashes = []
        if strategy == 'consistent_hash':
            self._build_hash_ring()

    def _build_hash_ring(self):
        """Build consistent hash ring with virtual nodes"""
        self.hash_ring.clear()
        self.sorted_hashes.clear()

        for server in self.active_servers:
            # Add 150 virtual nodes per server
            for i in range(150):
                virtual_key = f"{server.id}:{i}"
                hash_val = int(hashlib.md5(virtual_key.encode()).hexdigest(), 16)
                self.hash_ring[hash_val] = server
                bisect.insort(self.sorted_hashes, hash_val)

    def select_server(self, request=None):
        """Select a server based on strategy"""
        if not self.active_servers:
            raise Exception("No active servers available")

        if self.strategy == 'round_robin':
            servers_list = list(self.active_servers)
            server = servers_list[self.round_robin_counter % len(servers_list)]
            self.round_robin_counter += 1
            return server

        elif self.strategy == 'least_connections':
            return min(self.active_servers, key=lambda s: self.connections[s])

        elif self.strategy == 'weighted_round_robin':
            # Build weighted list
            weighted_servers = []
            for server in self.active_servers:
                weighted_servers.extend([server] * self.weights[server])

            if not weighted_servers:
                return list(self.active_servers)[0]

            server = weighted_servers[self.weighted_counter % len(weighted_servers)]
            self.weighted_counter += 1
            return server

        elif self.strategy == 'consistent_hash':
            if not request or not hasattr(request, 'key'):
                # Fallback to round-robin if no key
                return self.select_server_round_robin()

            key_hash = int(hashlib.md5(request.key.encode()).hexdigest(), 16)
            idx = bisect.bisect_right(self.sorted_hashes, key_hash)

            if idx == len(self.sorted_hashes):
                idx = 0

            return self.hash_ring[self.sorted_hashes[idx]]

        elif self.strategy == 'least_response_time':
            # Select server with lowest average response time
            def get_avg_response_time(server):
                if self.response_counts[server] == 0:
                    return 0  # Favor untested servers
                return self.response_times[server]

            return min(self.active_servers, key=get_avg_response_time)

    def mark_server_down(self, server):
        """Handle server failure"""
        if server in self.active_servers:
            self.active_servers.remove(server)

            # Clean up consistent hash ring
            if self.strategy == 'consistent_hash':
                self._build_hash_ring()

            # Reset connections for this server
            self.connections[server] = 0

    def add_server(self, server):
        """Handle server addition"""
        if server not in self.active_servers:
            self.active_servers.add(server)

            # Set default weight if needed
            if not hasattr(server, 'weight'):
                self.weights[server] = 1

            # Rebuild consistent hash ring
            if self.strategy == 'consistent_hash':
                self._build_hash_ring()

    def record_request_start(self, server):
        """Track connection start"""
        self.connections[server] += 1

    def record_request_end(self, server, response_time):
        """Track connection end and response time"""
        self.connections[server] = max(0, self.connections[server] - 1)

        # Update response time with EWMA
        if self.response_counts[server] == 0:
            self.response_times[server] = response_time
        else:
            old_avg = self.response_times[server]
            self.response_times[server] = (
                self.ewma_alpha * response_time +
                (1 - self.ewma_alpha) * old_avg
            )

        self.response_counts[server] += 1
```

</details>

## Exercise 4: MapReduce Word Count

**Task**: Implement a simple MapReduce framework and use it for word counting.

```python
class MapReduceFramework:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers

    def run(self, data, map_func, reduce_func):
        """Execute MapReduce job"""
        # TODO: Implement the MapReduce execution flow
        # 1. Split data among mappers
        # 2. Run map phase
        # 3. Shuffle/sort intermediate results
        # 4. Run reduce phase
        # 5. Collect results
        pass

# Implement these functions
def word_count_map(document):
    """Map function for word count"""
    # TODO: Emit (word, 1) for each word
    pass

def word_count_reduce(word, counts):
    """Reduce function for word count"""
    # TODO: Sum all counts for the word
    pass

# Test with sample data
documents = [
    "the quick brown fox",
    "the lazy dog",
    "the brown dog"
]
```

<details>
<summary>Solution</summary>

```python
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

class MapReduceFramework:
    def __init__(self, num_workers=4):
        self.num_workers = num_workers

    def run(self, data, map_func, reduce_func):
        """Execute MapReduce job"""
        # 1. Split data among mappers
        chunk_size = max(1, len(data) // self.num_workers)
        chunks = [
            data[i:i + chunk_size]
            for i in range(0, len(data), chunk_size)
        ]

        # 2. Run map phase in parallel
        intermediate = defaultdict(list)

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Map phase
            map_results = executor.map(
                lambda chunk: self._run_mapper(chunk, map_func),
                chunks
            )

            # Collect intermediate results
            for result in map_results:
                for key, value in result:
                    intermediate[key].append(value)

        # 3. Shuffle/sort is implicit in our dict structure

        # 4. Run reduce phase
        final_results = {}

        # Partition keys among reducers
        keys = list(intermediate.keys())
        key_chunks = [
            keys[i::self.num_workers]
            for i in range(min(self.num_workers, len(keys)))
        ]

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            reduce_results = executor.map(
                lambda key_chunk: self._run_reducer(key_chunk, intermediate, reduce_func),
                key_chunks
            )

            # Collect final results
            for result in reduce_results:
                final_results.update(result)

        return final_results

    def _run_mapper(self, chunk, map_func):
        """Run map function on a chunk"""
        results = []
        for item in chunk:
            # map_func should yield (key, value) pairs
            for key_value in map_func(item):
                results.append(key_value)
        return results

    def _run_reducer(self, keys, intermediate, reduce_func):
        """Run reduce function on a set of keys"""
        results = {}
        for key in keys:
            values = intermediate[key]
            results[key] = reduce_func(key, values)
        return results

def word_count_map(document):
    """Map function for word count"""
    # Simple tokenization (production would use better tokenizer)
    words = document.lower().split()
    for word in words:
        # Remove punctuation
        word = word.strip('.,!?;:"')
        if word:
            yield (word, 1)

def word_count_reduce(word, counts):
    """Reduce function for word count"""
    return sum(counts)

# Advanced example: Word count with combiners
class OptimizedMapReduceFramework(MapReduceFramework):
    def run(self, data, map_func, reduce_func, combine_func=None):
        """Execute MapReduce job with optional combiner"""
        # Split data among mappers
        chunk_size = max(1, len(data) // self.num_workers)
        chunks = [
            data[i:i + chunk_size]
            for i in range(0, len(data), chunk_size)
        ]

        intermediate = defaultdict(list)

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # Map phase with local combining
            map_results = executor.map(
                lambda chunk: self._run_mapper_with_combiner(
                    chunk, map_func, combine_func
                ),
                chunks
            )

            # Collect intermediate results
            for result in map_results:
                for key, value in result.items():
                    intermediate[key].append(value)

        # Reduce phase
        final_results = {}

        keys = list(intermediate.keys())
        key_chunks = [
            keys[i::self.num_workers]
            for i in range(min(self.num_workers, len(keys)))
        ]

        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            reduce_results = executor.map(
                lambda key_chunk: self._run_reducer(key_chunk, intermediate, reduce_func),
                key_chunks
            )

            for result in reduce_results:
                final_results.update(result)

        return final_results

    def _run_mapper_with_combiner(self, chunk, map_func, combine_func):
        """Run map function with local combining"""
        local_results = defaultdict(list)

        # Run mapper
        for item in chunk:
            for key, value in map_func(item):
                local_results[key].append(value)

        # Run combiner locally if provided
        if combine_func:
            combined = {}
            for key, values in local_results.items():
                combined[key] = combine_func(key, values)
            return combined
        else:
            return dict(local_results)

# Test
if __name__ == "__main__":
    documents = [
        "the quick brown fox jumps over the lazy dog",
        "the lazy dog sleeps all day",
        "the brown fox is quick and clever",
        "a quick brown dog runs fast"
    ]

    # Basic MapReduce
    mr = MapReduceFramework(num_workers=2)
    result = mr.run(documents, word_count_map, word_count_reduce)
    print("Word counts:", result)

    # Optimized with combiner
    mr_opt = OptimizedMapReduceFramework(num_workers=2)
    result_opt = mr_opt.run(
        documents,
        word_count_map,
        word_count_reduce,
        combine_func=word_count_reduce  # Use same reduce as combiner
    )
    print("Optimized word counts:", result_opt)
```

</details>

## Exercise 5: Distributed Task Queue

**Challenge**: Build a distributed task queue with the following features:
- Priority queues
- Task dependencies
- Retry logic
- Dead letter queue
- Rate limiting

```python
class DistributedTaskQueue:
    def __init__(self):
        # TODO: Initialize queue structures
        pass

    def submit_task(self, task, priority=0, depends_on=None):
        """Submit a task with optional dependencies"""
        # TODO: Add task to appropriate queue
        pass

    def get_next_task(self, worker_capabilities):
        """Get next available task for worker"""
        # TODO: Find highest priority task with met dependencies
        pass

    def complete_task(self, task_id, result):
        """Mark task as complete and trigger dependents"""
        # TODO: Update task status and check dependencies
        pass

    def fail_task(self, task_id, error, retry=True):
        """Handle task failure"""
        # TODO: Implement retry or move to DLQ
        pass
```

## Exercise 6: Distributed Aggregation

**Problem**: Implement a distributed aggregation system that can:
- Count distinct values across nodes
- Compute percentiles
- Perform group-by operations
- Handle data skew

**Bonus**: Implement approximate algorithms for better performance.

## Thought Experiments

### 1. The Thundering Herd

Your service has 10,000 workers polling a queue. The queue becomes empty, then suddenly receives 1 task.
- What happens?
- How do you prevent 10,000 workers from waking up for 1 task?
- Design a solution that scales.

### 2. The Hot Partition

In your distributed system, 90% of requests go to 1% of your data (e.g., celebrity tweets).
- How do you detect hot partitions?
- How do you handle them without manual intervention?
- What are the trade-offs of different approaches?

### 3. The Graceful Degradation

Your system has 5 services: A → B → C → D → E
Service D is slow but not dead.
- How does this manifest to users?
- How do you prevent cascading failure?
- Design a degradation strategy.

## Reflection Questions

1. **When is work distribution not worth it?**
   - Consider the overhead of distribution
   - Think about Amdahl's Law

2. **How does CAP theorem affect work distribution?**
   - Can you have consistent work distribution?
   - What happens during network partitions?

3. **What's the relationship between work distribution and data distribution?**
   - Should computation follow data or vice versa?
   - When does this decision matter most?

## Further Challenges

1. **Implement a distributed sort**
   - Handle data larger than any single machine
   - Optimize for different data distributions

2. **Build a distributed graph processor**
   - Handle graphs that don't fit in memory
   - Implement PageRank or connected components

3. **Create a stream processing system**
   - Handle out-of-order events
   - Implement windowing and watermarks

Remember: These exercises are designed to make you think about trade-offs. There's rarely a "perfect" solution—only solutions that fit specific constraints better than others.
