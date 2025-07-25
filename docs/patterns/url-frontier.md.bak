---
title: URL Frontier
description: Advanced queue management system for web crawlers balancing politeness, priority, and freshness
type: pattern
category: specialized
difficulty: intermediate
reading_time: 30 min
prerequisites: [priority-queues, distributed-systems, web-protocols]
when_to_use: Web crawlers, search engines, content aggregators, site monitoring systems
when_not_to_use: Simple scrapers, single-site crawlers, batch processing systems
status: complete
last_updated: 2025-07-24
---

# URL Frontier


## Overview

The URL Frontier is a sophisticated queue management system that orchestrates web crawling by balancing multiple competing requirements: politeness (respecting server limits), priority (crawling important pages first), freshness (updating stale content), and breadth (ensuring coverage).

<div class="law-box">
<strong>Crawling Constraint</strong>: Web crawlers must balance aggressive crawling for completeness against respectful crawling to avoid overwhelming servers and getting blocked.
</div>

## The Web Crawling Challenge

Web crawling at scale faces multiple constraints:

```python
# Simple approach fails at scale
import requests
from collections import deque

# ❌ Naive crawler - will get blocked
urls_to_crawl = deque(['https://example.com'])

while urls_to_crawl:
    url = urls_to_crawl.popleft()
    response = requests.get(url)  # No rate limiting!
# Extract and queue new URLs...

# Problems:
# - No politeness (rapid-fire requests)
# - No prioritization (breadth-first only)
# - No freshness tracking
# - No duplicate detection
# - No failure handling
```

**Frontier Requirements**:
- **Politeness**: Respect robots.txt and crawl delays
- **Priority**: Crawl important pages first
- **Freshness**: Re-crawl stale content
- **Efficiency**: Avoid duplicates and failures
- **Scalability**: Handle billions of URLs

## Mercator-Style URL Frontier

Based on the Mercator web crawler architecture:

### Implementation

```python
import time
import heapq
import hashlib
from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class URLItem:
    url: str
    priority: float
    last_crawled: Optional[datetime] = None
    crawl_delay: float = 1.0
    retry_count: int = 0
    discovered_time: datetime = field(default_factory=datetime.now)
    
    def __lt__(self, other):
        return self.priority > other.priority  # Higher priority first

class URLFrontier:
    def __init__(self, max_host_queues: int = 1000):
# Front queues (priority-based)
        self.front_queues = []  # List of priority queues
        self.num_front_queues = 8
        
# Back queues (host-based for politeness)
        self.back_queues = {}  # hostname -> deque of URLs
        self.max_host_queues = max_host_queues
        
# Host management
        self.host_last_access = {}  # hostname -> last access time
        self.host_crawl_delay = {}  # hostname -> crawl delay in seconds
        self.host_queue_assignments = {}  # hostname -> back queue index
        
# Duplicate detection
        self.seen_urls = set()  # Simple duplicate detection
        self.url_hashes = {}   # URL -> hash mapping
        
# Statistics
        self.stats = {
            'urls_added': 0,
            'urls_crawled': 0,
            'urls_blocked': 0,
            'politeness_delays': 0
        }
        
# Initialize front queues
        for i in range(self.num_front_queues):
            heapq.heappush(self.front_queues, [])
    
    def add_url(self, url_item: URLItem) -> bool:
        """Add URL to frontier with duplicate detection"""
        
# Normalize URL for duplicate detection
        normalized_url = self._normalize_url(url_item.url)
        url_hash = self._hash_url(normalized_url)
        
# Check for duplicates
        if url_hash in self.url_hashes:
            return False  # Duplicate
        
# Store URL hash
        self.url_hashes[url_hash] = normalized_url
        self.seen_urls.add(normalized_url)
        
# Determine priority queue (front queue)
        priority_level = self._calculate_priority_level(url_item.priority)
        
# Add to appropriate front queue
        heapq.heappush(self.front_queues[priority_level], url_item)
        
        self.stats['urls_added'] += 1
        return True
    
    def get_next_url(self) -> Optional[URLItem]:
        """Get next URL to crawl, respecting politeness"""
        
# Try to find a crawlable URL from front queues
        for _ in range(100):  # Avoid infinite loops
            url_item = self._get_from_front_queues()
            if not url_item:
                return None
            
            hostname = urlparse(url_item.url).netloc
            
# Check if we can crawl this host now
            if self._can_crawl_host(hostname):
# Update host access time
                self.host_last_access[hostname] = time.time()
                self.stats['urls_crawled'] += 1
                return url_item
            else:
# Add to back queue for later
                self._add_to_back_queue(url_item, hostname)
                self.stats['politeness_delays'] += 1
        
# Try back queues for hosts that are ready
        return self._get_from_back_queues()
    
    def _get_from_front_queues(self) -> Optional[URLItem]:
        """Get URL from highest priority front queue"""
        for front_queue in self.front_queues:
            if front_queue:
                return heapq.heappop(front_queue)
        return None
    
    def _get_from_back_queues(self) -> Optional[URLItem]:
        """Get URL from back queues for hosts that are ready"""
        current_time = time.time()
        
        for hostname, queue in list(self.back_queues.items()):
            if not queue:
                continue
                
# Check if enough time has passed since last crawl
            last_access = self.host_last_access.get(hostname, 0)
            crawl_delay = self.host_crawl_delay.get(hostname, 1.0)
            
            if current_time - last_access >= crawl_delay:
                url_item = queue.popleft()
                self.host_last_access[hostname] = current_time
                self.stats['urls_crawled'] += 1
                
# Clean up empty queues
                if not queue:
                    del self.back_queues[hostname]
                
                return url_item
        
        return None
    
    def _can_crawl_host(self, hostname: str) -> bool:
        """Check if we can crawl a host based on politeness rules"""
        current_time = time.time()
        last_access = self.host_last_access.get(hostname, 0)
        crawl_delay = self.host_crawl_delay.get(hostname, 1.0)
        
        return current_time - last_access >= crawl_delay
    
    def _add_to_back_queue(self, url_item: URLItem, hostname: str):
        """Add URL to host-specific back queue"""
        if hostname not in self.back_queues:
            self.back_queues[hostname] = deque()
        
        self.back_queues[hostname].append(url_item)
        
# Limit queue size per host
        if len(self.back_queues[hostname]) > 1000:
            self.back_queues[hostname].popleft()  # Remove oldest
    
    def _calculate_priority_level(self, priority: float) -> int:
        """Map priority score to front queue index"""
# Higher priority = lower index (processed first)
        if priority >= 10.0:
            return 0  # Highest priority
        elif priority >= 8.0:
            return 1
        elif priority >= 6.0:
            return 2
        elif priority >= 4.0:
            return 3
        elif priority >= 2.0:
            return 4
        elif priority >= 1.0:
            return 5
        elif priority >= 0.5:
            return 6
        else:
            return 7  # Lowest priority
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL for duplicate detection"""
        from urllib.parse import urlparse, urlunparse
        
        parsed = urlparse(url.lower())
        
# Remove fragment and normalize query
        normalized = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path.rstrip('/') if parsed.path != '/' else '/',
            parsed.params,
            parsed.query,
            ''  # Remove fragment
        ))
        
        return normalized
    
    def _hash_url(self, url: str) -> str:
        """Generate hash for URL"""
        return hashlib.sha256(url.encode()).hexdigest()
    
    def set_crawl_delay(self, hostname: str, delay: float):
        """Set crawl delay for specific host"""
        self.host_crawl_delay[hostname] = delay
    
    def get_stats(self) -> Dict:
        """Get frontier statistics"""
        front_queue_sizes = [len(q) for q in self.front_queues]
        back_queue_sizes = [len(q) for q in self.back_queues.values()]
        
        return {
            **self.stats,
            'front_queues': front_queue_sizes,
            'back_queues_count': len(self.back_queues),
            'total_back_queue_size': sum(back_queue_sizes),
            'unique_hosts': len(self.host_last_access),
            'seen_urls': len(self.seen_urls)
        }

# Usage example
frontier = URLFrontier()

# Add URLs with different priorities
high_priority_url = URLItem("https://example.com/", priority=10.0)
medium_priority_url = URLItem("https://example.com/about", priority=5.0)
low_priority_url = URLItem("https://example.com/contact", priority=1.0)

frontier.add_url(high_priority_url)
frontier.add_url(medium_priority_url)
frontier.add_url(low_priority_url)

# Set politeness rules
frontier.set_crawl_delay("example.com", 2.0)  # 2 second delay

# Crawl URLs
while True:
    url_item = frontier.get_next_url()
    if not url_item:
        break
    
    print(f"Crawling: {url_item.url} (priority: {url_item.priority})")
    
# Simulate crawling delay
    time.sleep(0.1)

print(f"Frontier stats: {frontier.get_stats()}")
```

## Advanced Frontier Features

### Freshness-Based Recrawling

```python
from datetime import datetime, timedelta
import math

class FreshnessAwareFrontier(URLFrontier):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_freshness = {}  # URL -> last modified time
        self.content_hashes = {}  # URL -> content hash
        self.freshness_weights = {
            'news': 0.1,      # Recrawl every 2.4 hours
            'social': 0.25,   # Recrawl every hour
            'static': 7.0,    # Recrawl every week
            'default': 1.0    # Recrawl daily
        }
    
    def calculate_freshness_priority(self, url: str, 
                                   content_type: str = 'default') -> float:
        """Calculate priority based on content freshness"""
        
        now = datetime.now()
        last_crawled = self.page_freshness.get(url)
        
        if not last_crawled:
            return 10.0  # Never crawled - highest priority
        
# Calculate staleness in hours
        staleness_hours = (now - last_crawled).total_seconds() / 3600
        
# Get expected freshness interval
        freshness_interval = self.freshness_weights.get(content_type, 1.0) * 24
        
# Calculate freshness score (exponential decay)
        if staleness_hours >= freshness_interval:
# Stale content - high priority
            return 8.0 + min(2.0, staleness_hours / freshness_interval)
        else:
# Fresh content - lower priority
            return 1.0 * (staleness_hours / freshness_interval)
    
    def update_page_freshness(self, url: str, content_hash: str):
        """Update page freshness information"""
        now = datetime.now()
        
# Check if content actually changed
        if url in self.content_hashes:
            if self.content_hashes[url] == content_hash:
# Content unchanged - just update access time
                self.page_freshness[url] = now
                return False  # No change
        
# Content changed or new page
        self.page_freshness[url] = now
        self.content_hashes[url] = content_hash
        return True  # Changed

# Usage with freshness
freshness_frontier = FreshnessAwareFrontier()

# Add URLs with freshness-based priorities
news_url = URLItem(
    "https://news.example.com/breaking-news",
    priority=freshness_frontier.calculate_freshness_priority(
        "https://news.example.com/breaking-news", 'news'
    )
)

static_url = URLItem(
    "https://example.com/terms-of-service",
    priority=freshness_frontier.calculate_freshness_priority(
        "https://example.com/terms-of-service", 'static'
    )
)

freshness_frontier.add_url(news_url)
freshness_frontier.add_url(static_url)
```

### Distributed URL Frontier

```python
import redis
import pickle
import json
from typing import Any
import threading

class DistributedURLFrontier:
    def __init__(self, redis_client: redis.Redis, crawler_id: str):
        self.redis = redis_client
        self.crawler_id = crawler_id
        self.local_buffer = deque(maxlen=1000)  # Local buffer for performance
        self.buffer_lock = threading.Lock()
        
# Redis keys
        self.priority_queue_key = "crawler:priority_queue"
        self.host_queues_key = "crawler:host_queues"
        self.seen_urls_key = "crawler:seen_urls"
        self.host_delays_key = "crawler:host_delays"
        self.stats_key = "crawler:stats"
    
    def add_url(self, url_item: URLItem) -> bool:
        """Add URL to distributed frontier"""
        
# Check for duplicates using Redis set
        url_hash = hashlib.sha256(url_item.url.encode()).hexdigest()
        
        if self.redis.sismember(self.seen_urls_key, url_hash):
            return False  # Duplicate
        
# Add to seen set
        self.redis.sadd(self.seen_urls_key, url_hash)
        
# Serialize URL item
        serialized_item = pickle.dumps(url_item)
        
# Add to priority queue with score
        self.redis.zadd(
            self.priority_queue_key,
            {serialized_item: url_item.priority}
        )
        
# Update statistics
        self.redis.hincrby(self.stats_key, 'urls_added', 1)
        
        return True
    
    def get_next_url(self) -> Optional[URLItem]:
        """Get next URL from distributed frontier"""
        
# Try local buffer first
        with self.buffer_lock:
            if self.local_buffer:
                return self.local_buffer.popleft()
        
# Fetch batch from Redis for efficiency
        self._fill_local_buffer()
        
        with self.buffer_lock:
            if self.local_buffer:
                return self.local_buffer.popleft()
        
        return None
    
    def _fill_local_buffer(self):
        """Fill local buffer from distributed queue"""
        pipeline = self.redis.pipeline()
        
# Get high-priority URLs (batch of 50)
        pipeline.zrevrange(
            self.priority_queue_key, 0, 49, withscores=True
        )
        pipeline.zremrangebyrank(self.priority_queue_key, -50, -1)
        
        results = pipeline.execute()
        url_items = results[0]
        
        with self.buffer_lock:
            for serialized_item, priority in url_items:
                try:
                    url_item = pickle.loads(serialized_item)
                    
# Check politeness
                    hostname = urlparse(url_item.url).netloc
                    if self._can_crawl_host_distributed(hostname):
                        self.local_buffer.append(url_item)
                        self._update_host_access_time(hostname)
                    else:
# Re-add to queue with lower priority for later
                        reduced_priority = max(0.1, priority - 1.0)
                        self.redis.zadd(
                            self.priority_queue_key,
                            {serialized_item: reduced_priority}
                        )
                        
                except Exception as e:
# Skip corrupted items
                    continue
    
    def _can_crawl_host_distributed(self, hostname: str) -> bool:
        """Check host politeness using distributed state"""
        current_time = time.time()
        
# Get last access time from Redis
        last_access_key = f"host_access:{hostname}"
        last_access = self.redis.get(last_access_key)
        
        if last_access:
            last_access = float(last_access)
            
# Get crawl delay
            delay = self.redis.hget(self.host_delays_key, hostname)
            delay = float(delay) if delay else 1.0
            
            return current_time - last_access >= delay
        
        return True  # No previous access recorded
    
    def _update_host_access_time(self, hostname: str):
        """Update host access time in Redis"""
        current_time = time.time()
        last_access_key = f"host_access:{hostname}"
        
# Set with expiration (cleanup old entries)
        self.redis.setex(last_access_key, 86400, current_time)  # 24 hour TTL
    
    def set_crawl_delay(self, hostname: str, delay: float):
        """Set crawl delay for host in distributed storage"""
        self.redis.hset(self.host_delays_key, hostname, delay)
    
    def get_distributed_stats(self) -> Dict:
        """Get distributed frontier statistics"""
        stats = {}
        
# Get basic stats
        redis_stats = self.redis.hgetall(self.stats_key)
        for key, value in redis_stats.items():
            stats[key.decode()] = int(value)
        
# Get queue sizes
        stats['priority_queue_size'] = self.redis.zcard(self.priority_queue_key)
        stats['seen_urls_count'] = self.redis.scard(self.seen_urls_key)
        stats['local_buffer_size'] = len(self.local_buffer)
        
        return stats

# Usage with Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)
distributed_frontier = DistributedURLFrontier(redis_client, 'crawler-1')

# Add URL to distributed frontier
url_item = URLItem("https://example.com/page", priority=5.0)
distributed_frontier.add_url(url_item)

# Get next URL for crawling
next_url = distributed_frontier.get_next_url()
if next_url:
    print(f"Crawling: {next_url.url}")
```

## Robots.txt Integration

```python
import requests
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin, urlparse

class RobotsAwareFrontier(URLFrontier):
    def __init__(self, user_agent: str = "WebCrawler/1.0", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_agent = user_agent
        self.robots_cache = {}  # hostname -> RobotFileParser
        self.robots_cache_ttl = {}  # hostname -> expiration time
        self.crawl_delay_override = {}  # hostname -> delay from robots.txt
    
    def is_allowed(self, url: str) -> Tuple[bool, float]:
        """Check if URL is allowed by robots.txt"""
        
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
# Get robots.txt parser for this host
        robots_parser = self._get_robots_parser(hostname)
        
        if not robots_parser:
            return True, 1.0  # Allow if robots.txt unavailable
        
# Check if URL is allowed
        allowed = robots_parser.can_fetch(self.user_agent, url)
        
# Get crawl delay from robots.txt
        crawl_delay = robots_parser.crawl_delay(self.user_agent)
        if crawl_delay is None:
            crawl_delay = 1.0  # Default delay
        
        return allowed, crawl_delay
    
    def _get_robots_parser(self, hostname: str) -> Optional[RobotFileParser]:
        """Get cached robots.txt parser for hostname"""
        
        current_time = time.time()
        
# Check cache expiration
        if hostname in self.robots_cache_ttl:
            if current_time > self.robots_cache_ttl[hostname]:
# Cache expired, remove
                if hostname in self.robots_cache:
                    del self.robots_cache[hostname]
                del self.robots_cache_ttl[hostname]
        
# Return cached parser if available
        if hostname in self.robots_cache:
            return self.robots_cache[hostname]
        
# Fetch and parse robots.txt
        try:
            robots_url = f"https://{hostname}/robots.txt"
            
            response = requests.get(robots_url, timeout=5)
            if response.status_code == 200:
                parser = RobotFileParser()
                parser.set_url(robots_url)
                parser.read()
                
# Cache parser
                self.robots_cache[hostname] = parser
                self.robots_cache_ttl[hostname] = current_time + 3600  # 1 hour TTL
                
                return parser
                
        except Exception as e:
# If robots.txt fetch fails, allow crawling
            pass
        
        return None
    
    def add_url(self, url_item: URLItem) -> bool:
        """Add URL with robots.txt checking"""
        
# Check robots.txt
        allowed, robots_delay = self.is_allowed(url_item.url)
        
        if not allowed:
            self.stats['urls_blocked'] += 1
            return False
        
# Update crawl delay based on robots.txt
        hostname = urlparse(url_item.url).netloc
        url_item.crawl_delay = max(url_item.crawl_delay, robots_delay)
        self.set_crawl_delay(hostname, url_item.crawl_delay)
        
        return super().add_url(url_item)

# Usage with robots.txt checking
robots_frontier = RobotsAwareFrontier(user_agent="MyBot/1.0")

# URLs will be checked against robots.txt
test_url = URLItem("https://example.com/admin/secret", priority=5.0)
added = robots_frontier.add_url(test_url)
print(f"URL added: {added}")  # May be False if blocked by robots.txt
```

## Performance Optimization

```python
import asyncio
import aioredis
from concurrent.futures import ThreadPoolExecutor
import uvloop  # High-performance event loop

class HighPerformanceFrontier:
    def __init__(self, redis_url: str, max_workers: int = 32):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
# Use uvloop for better performance
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        
# Connection pool for Redis
        self.redis_pool = None
        self.redis_url = redis_url
        
# Local buffers for batch operations
        self.add_buffer = []
        self.add_buffer_lock = asyncio.Lock()
        self.buffer_size = 1000
    
    async def initialize(self):
        """Initialize async components"""
        self.redis_pool = aioredis.ConnectionPool.from_url(
            self.redis_url, max_connections=20
        )
    
    async def batch_add_urls(self, url_items: List[URLItem]) -> int:
        """Add multiple URLs in batches for better performance"""
        
        if not url_items:
            return 0
        
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
# Batch operations
        pipeline = redis.pipeline()
        added_count = 0
        
        for url_item in url_items:
# Check duplicates
            url_hash = hashlib.sha256(url_item.url.encode()).hexdigest()
            
# Add to pipeline
            pipeline.sadd("seen_urls", url_hash)
            pipeline.zadd(
                "priority_queue",
                {pickle.dumps(url_item): url_item.priority}
            )
            added_count += 1
        
# Execute batch
        await pipeline.execute()
        
        await redis.close()
        return added_count
    
    async def batch_get_urls(self, count: int = 100) -> List[URLItem]:
        """Get multiple URLs in batch"""
        
        redis = aioredis.Redis(connection_pool=self.redis_pool)
        
# Get high-priority URLs
        items = await redis.zrevrange(
            "priority_queue", 0, count-1, withscores=True
        )
        
# Remove from queue
        if items:
            await redis.zremrangebyrank("priority_queue", -count, -1)
        
# Deserialize items
        url_items = []
        for serialized_item, priority in items:
            try:
                url_item = pickle.loads(serialized_item)
                url_items.append(url_item)
            except:
                continue
        
        await redis.close()
        return url_items
    
    async def parallel_url_processing(self, url_items: List[URLItem]):
        """Process URLs in parallel"""
        
        async def process_url(url_item):
# Simulate URL processing
            await asyncio.sleep(0.01)  # I/O simulation
            return f"Processed: {url_item.url}"
        
# Process URLs concurrently
        tasks = [process_url(item) for item in url_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results

# Performance testing
async def benchmark_frontier():
    frontier = HighPerformanceFrontier("redis://localhost:6379")
    await frontier.initialize()
    
# Generate test URLs
    test_urls = [
        URLItem(f"https://example{i}.com/page", priority=float(i % 10))
        for i in range(10000)
    ]
    
# Benchmark batch add
    start_time = time.time()
    added = await frontier.batch_add_urls(test_urls)
    add_time = time.time() - start_time
    
    print(f"Added {added} URLs in {add_time:.2f}s ({added/add_time:.0f} URLs/sec)")
    
# Benchmark batch get
    start_time = time.time()
    retrieved_urls = await frontier.batch_get_urls(1000)
    get_time = time.time() - start_time
    
    print(f"Retrieved {len(retrieved_urls)} URLs in {get_time:.2f}s")
    
# Benchmark parallel processing
    start_time = time.time()
    results = await frontier.parallel_url_processing(retrieved_urls)
    process_time = time.time() - start_time
    
    print(f"Processed {len(results)} URLs in {process_time:.2f}s")

# Run benchmark
# asyncio.run(benchmark_frontier())
```

<div class="decision-box">
<strong>Decision Framework</strong>:

- **Large-scale crawlers**: Distributed frontier with Redis
- **Focused crawlers**: In-memory frontier with priority queues
- **News aggregators**: Freshness-aware frontier
- **Respectful crawlers**: Robots.txt aware frontier
- **High-throughput systems**: Batch processing with async operations
- **Multi-tenant crawlers**: Separate frontiers per user/domain
</div>

## Trade-offs

| Approach | Scalability | Performance | Memory Usage | Complexity |
|----------|-------------|-------------|--------------|------------|
| In-Memory | Medium | Very High | High | Low |
| Distributed | Very High | High | Low | High |
| Freshness-Aware | High | Medium | Medium | Medium |
| Robots-Aware | High | Medium | Medium | Medium |
| Batch Processing | Very High | Very High | Medium | Medium |

## Frontier Architecture Patterns

### Single-Threaded Frontier
- **Use case**: Simple crawlers, development
- **Pros**: Simple, no concurrency issues
- **Cons**: Limited throughput

### Multi-Threaded Frontier
- **Use case**: Medium-scale crawlers
- **Pros**: Better CPU utilization
- **Cons**: Lock contention, complexity

### Distributed Frontier
- **Use case**: Large-scale search engines
- **Pros**: Unlimited scale, fault tolerance
- **Cons**: Network overhead, eventual consistency

### Hybrid Frontier
- **Use case**: Production systems
- **Pros**: Local performance + distributed coordination
- **Cons**: Complex architecture

## Related Patterns
- Priority Queue (Coming Soon) - Queue management strategies
- Distributed Queue (Coming Soon) - Scaling queue systems
- [Rate Limiting](rate-limiting.md) - Politeness implementation
- [Bloom Filter](bloom-filter.md) - Efficient duplicate detection

## References
- [Mercator Web Crawler](http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.15.6279)
- [Google Web Crawler Architecture](https://static.googleusercontent.com/media/research.google.com/en//archive/googlecluster-ieee.pdf)
- [Robots Exclusion Protocol](https://www.robotstxt.org/)