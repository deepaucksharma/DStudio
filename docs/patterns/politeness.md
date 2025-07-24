---
title: Crawler Politeness
description: Respectful web crawling practices that balance efficiency with server resource conservation
type: pattern
category: specialized
difficulty: intermediate
reading_time: 30 min
prerequisites: [web-protocols, rate-limiting, robots-txt]
when_to_use: Web crawlers, search engines, content aggregators, monitoring systems
when_not_to_use: Internal API crawlers, authorized bulk data transfers, single-site scrapers with permission
status: complete
last_updated: 2025-07-24
---

# Crawler Politeness

<!-- Navigation -->
[Home](../introduction/index.md) → [Part III: Patterns](index.md) → **Crawler Politeness**

## Overview

Crawler politeness is a set of practices that ensure web crawlers behave respectfully toward target websites, balancing crawling efficiency with server resource conservation. Polite crawlers avoid overwhelming servers, respect robots.txt directives, and adapt to server behavior.

<div class="law-box">
<strong>Web Etiquette Constraint</strong>: Aggressive crawling can overload servers, trigger rate limiting, or result in IP bans. Polite crawlers must balance thoroughness with respectful resource usage.
</div>

## The Politeness Challenge

Uncontrolled crawling causes problems:

```python
# ❌ Impolite crawler - will cause problems
import requests
import threading
from concurrent.futures import ThreadPoolExecutor

def crawl_aggressively():
    urls = [f"https://example.com/page{i}" for i in range(1000)]
    
    with ThreadPoolExecutor(max_workers=50) as executor:
        # 50 concurrent requests to same server!
        futures = [executor.submit(requests.get, url) for url in urls]
        
        for future in futures:
            response = future.result()  # No error handling

# Problems:
# - Overwhelming server with concurrent requests
# - No respect for robots.txt
# - No adaptive behavior
# - Can trigger DDoS protection
# - May violate Terms of Service
```

**Politeness Requirements**:
- **Rate Limiting**: Control request frequency per host
- **Robots.txt Compliance**: Respect crawling directives
- **Adaptive Behavior**: Respond to server signals
- **Resource Conservation**: Minimize server load
- **Error Handling**: Gracefully handle failures

## Core Politeness Implementation

### Polite Crawler Framework

```python
import time
import requests
import threading
from collections import defaultdict, deque
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class CrawlPolicy:
    base_delay: float = 1.0           # Base delay between requests
    max_delay: float = 60.0           # Maximum delay
    concurrent_limit: int = 1         # Max concurrent requests per host
    respect_robots: bool = True       # Follow robots.txt
    user_agent: str = "PoliteBot/1.0"
    timeout: float = 10.0             # Request timeout
    retry_limit: int = 3              # Max retries
    backoff_factor: float = 2.0       # Exponential backoff multiplier

class PoliteCrawler:
    def __init__(self, policy: CrawlPolicy):
        self.policy = policy
        
        # Per-host state management
        self.host_delays = defaultdict(lambda: policy.base_delay)
        self.host_last_request = defaultdict(float)
        self.host_active_requests = defaultdict(int)
        self.host_error_counts = defaultdict(int)
        self.host_consecutive_errors = defaultdict(int)
        
        # Robots.txt cache
        self.robots_cache = {}
        self.robots_cache_expiry = {}
        
        # Request session with configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': policy.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'requests_made': 0,
            'requests_blocked': 0,
            'errors_encountered': 0,
            'total_delay_time': 0.0
        }
    
    def can_crawl(self, url: str) -> Tuple[bool, str]:
        """Check if URL can be crawled considering all politeness rules"""
        
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        
        # Check robots.txt
        if self.policy.respect_robots:
            allowed, reason = self._check_robots_txt(url, hostname)
            if not allowed:
                return False, reason
        
        # Check concurrent request limit
        with self.lock:
            if self.host_active_requests[hostname] >= self.policy.concurrent_limit:
                return False, f"Concurrent limit exceeded ({self.policy.concurrent_limit})"
        
        # Check if we need to wait for rate limiting
        time_since_last = time.time() - self.host_last_request[hostname]
        required_delay = self.host_delays[hostname]
        
        if time_since_last < required_delay:
            return False, f"Rate limit active (wait {required_delay - time_since_last:.1f}s)"
        
        return True, "OK"
    
    def crawl_url(self, url: str) -> Optional[requests.Response]:
        """Crawl a single URL with full politeness compliance"""
        
        # Pre-crawl checks
        can_crawl, reason = self.can_crawl(url)
        if not can_crawl:
            print(f"Blocked crawling {url}: {reason}")
            self.stats['requests_blocked'] += 1
            return None
        
        hostname = urlparse(url).netloc
        
        # Wait for required delay
        self._wait_for_politeness(hostname)
        
        # Update active request count
        with self.lock:
            self.host_active_requests[hostname] += 1
            self.host_last_request[hostname] = time.time()
        
        try:
            # Make the request
            response = self.session.get(
                url, 
                timeout=self.policy.timeout,
                allow_redirects=True
            )
            
            # Update statistics and state based on response
            self._handle_response(hostname, response)
            
            self.stats['requests_made'] += 1
            return response
            
        except requests.exceptions.RequestException as e:
            # Handle errors and update politeness parameters
            self._handle_error(hostname, e)
            self.stats['errors_encountered'] += 1
            return None
            
        finally:
            # Always decrement active request count
            with self.lock:
                self.host_active_requests[hostname] -= 1
    
    def _check_robots_txt(self, url: str, hostname: str) -> Tuple[bool, str]:
        """Check robots.txt compliance"""
        
        # Get robots.txt parser
        robots_parser = self._get_robots_parser(hostname)
        
        if robots_parser is None:
            return True, "No robots.txt"  # Allow if robots.txt unavailable
        
        # Check if URL is allowed
        allowed = robots_parser.can_fetch(self.policy.user_agent, url)
        
        if not allowed:
            return False, "Blocked by robots.txt"
        
        # Update crawl delay based on robots.txt
        robots_delay = robots_parser.crawl_delay(self.policy.user_agent)
        if robots_delay:
            with self.lock:
                self.host_delays[hostname] = max(
                    self.host_delays[hostname], 
                    float(robots_delay)
                )
        
        return True, "Allowed by robots.txt"
    
    def _get_robots_parser(self, hostname: str) -> Optional[RobotFileParser]:
        """Get cached robots.txt parser for hostname"""
        
        current_time = time.time()
        
        # Check cache expiration
        if hostname in self.robots_cache_expiry:
            if current_time > self.robots_cache_expiry[hostname]:
                # Remove expired entry
                self.robots_cache.pop(hostname, None)
                self.robots_cache_expiry.pop(hostname, None)
        
        # Return cached parser if available
        if hostname in self.robots_cache:
            return self.robots_cache[hostname]
        
        # Fetch and parse robots.txt
        try:
            robots_url = f"https://{hostname}/robots.txt"
            
            response = self.session.get(robots_url, timeout=5)
            
            if response.status_code == 200:
                parser = RobotFileParser()
                parser.set_url(robots_url)
                
                # Parse from string content
                parser.read()
                
                # Cache the parser (1 hour TTL)
                self.robots_cache[hostname] = parser
                self.robots_cache_expiry[hostname] = current_time + 3600
                
                return parser
                
        except Exception:
            # If robots.txt fetch fails, cache None to avoid repeated attempts
            self.robots_cache[hostname] = None
            self.robots_cache_expiry[hostname] = current_time + 1800  # 30 min TTL
        
        return None
    
    def _wait_for_politeness(self, hostname: str):
        """Wait appropriate amount of time before making request"""
        
        current_time = time.time()
        time_since_last = current_time - self.host_last_request[hostname]
        required_delay = self.host_delays[hostname]
        
        if time_since_last < required_delay:
            wait_time = required_delay - time_since_last
            print(f"Waiting {wait_time:.1f}s for {hostname} politeness")
            time.sleep(wait_time)
            self.stats['total_delay_time'] += wait_time
    
    def _handle_response(self, hostname: str, response: requests.Response):
        """Update crawler state based on response"""
        
        with self.lock:
            # Reset error counts on successful response
            if response.status_code < 400:
                self.host_consecutive_errors[hostname] = 0
                
                # Gradually reduce delay for well-behaved servers
                if self.host_delays[hostname] > self.policy.base_delay:
                    self.host_delays[hostname] *= 0.9  # Reduce by 10%
                    self.host_delays[hostname] = max(
                        self.host_delays[hostname], 
                        self.policy.base_delay
                    )
            
            # Handle specific HTTP status codes
            elif response.status_code == 429:  # Too Many Requests
                self._handle_rate_limit(hostname, response)
                
            elif response.status_code >= 500:  # Server errors
                self._handle_server_error(hostname)
                
            elif response.status_code == 403:  # Forbidden
                # Increase delay significantly
                self.host_delays[hostname] = min(
                    self.host_delays[hostname] * 3.0,
                    self.policy.max_delay
                )
    
    def _handle_rate_limit(self, hostname: str, response: requests.Response):
        """Handle 429 Too Many Requests response"""
        
        # Check for Retry-After header
        retry_after = response.headers.get('Retry-After')
        
        with self.lock:
            if retry_after:
                try:
                    # Retry-After can be in seconds or HTTP date
                    if retry_after.isdigit():
                        delay = min(int(retry_after), self.policy.max_delay)
                    else:
                        # Parse HTTP date (simplified)
                        delay = 60  # Default to 1 minute if can't parse
                    
                    self.host_delays[hostname] = delay
                    print(f"Rate limited by {hostname}, waiting {delay}s")
                    
                except ValueError:
                    # Double the delay if can't parse Retry-After
                    self.host_delays[hostname] = min(
                        self.host_delays[hostname] * 2.0,
                        self.policy.max_delay
                    )
            else:
                # No Retry-After header, exponentially back off
                self.host_delays[hostname] = min(
                    self.host_delays[hostname] * self.policy.backoff_factor,
                    self.policy.max_delay
                )
    
    def _handle_server_error(self, hostname: str):
        """Handle 5xx server errors"""
        
        with self.lock:
            self.host_consecutive_errors[hostname] += 1
            
            # Increase delay based on consecutive errors
            error_multiplier = min(2 ** self.host_consecutive_errors[hostname], 16)
            self.host_delays[hostname] = min(
                self.policy.base_delay * error_multiplier,
                self.policy.max_delay
            )
    
    def _handle_error(self, hostname: str, error: Exception):
        """Handle request exceptions"""
        
        with self.lock:
            self.host_error_counts[hostname] += 1
            self.host_consecutive_errors[hostname] += 1
            
            # Increase delay based on error type
            if isinstance(error, requests.exceptions.Timeout):
                # Timeout - increase delay moderately
                self.host_delays[hostname] = min(
                    self.host_delays[hostname] * 1.5,
                    self.policy.max_delay
                )
            
            elif isinstance(error, requests.exceptions.ConnectionError):
                # Connection error - increase delay significantly
                self.host_delays[hostname] = min(
                    self.host_delays[hostname] * 3.0,
                    self.policy.max_delay
                )
            
            else:
                # Other errors - moderate increase
                self.host_delays[hostname] = min(
                    self.host_delays[hostname] * 2.0,
                    self.policy.max_delay
                )
            
            print(f"Error crawling {hostname}: {error}")
    
    def get_stats(self) -> Dict:
        """Get crawler statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_hosts': len(self.host_last_request),
                'avg_delay': sum(self.host_delays.values()) / max(len(self.host_delays), 1),
                'hosts_with_errors': len([h for h, c in self.host_error_counts.items() if c > 0])
            }

# Usage example
policy = CrawlPolicy(
    base_delay=2.0,           # 2 second base delay
    concurrent_limit=1,       # 1 request at a time per host
    respect_robots=True,      # Follow robots.txt
    user_agent="MyBot/1.0"
)

crawler = PoliteCrawler(policy)

# Crawl URLs politely
urls = [
    "https://example.com/page1",
    "https://example.com/page2", 
    "https://different.com/page1"
]

successful_responses = []
for url in urls:
    response = crawler.crawl_url(url)
    if response:
        successful_responses.append(response)
        print(f"Successfully crawled {url} ({response.status_code})")

print(f"Crawler stats: {crawler.get_stats()}")
```

## Advanced Politeness Strategies

### Adaptive Politeness

```python
import numpy as np
from collections import deque

class AdaptivePoliteCrawler(PoliteCrawler):
    def __init__(self, policy: CrawlPolicy):
        super().__init__(policy)
        
        # Adaptive behavior tracking
        self.host_response_times = defaultdict(lambda: deque(maxlen=10))
        self.host_success_rates = defaultdict(lambda: deque(maxlen=20))
        self.host_server_load_indicators = defaultdict(list)
        
    def _handle_response(self, hostname: str, response: requests.Response):
        """Enhanced response handling with adaptive behavior"""
        
        # Record response time
        response_time = response.elapsed.total_seconds()
        self.host_response_times[hostname].append(response_time)
        
        # Record success/failure
        success = response.status_code < 400
        self.host_success_rates[hostname].append(success)
        
        # Analyze server load indicators
        self._analyze_server_load(hostname, response)
        
        # Call parent handler
        super()._handle_response(hostname, response)
        
        # Apply adaptive adjustments
        self._adaptive_delay_adjustment(hostname)
    
    def _analyze_server_load(self, hostname: str, response: requests.Response):
        """Analyze response for server load indicators"""
        
        indicators = []
        
        # Response time indicates load
        response_time = response.elapsed.total_seconds()
        if response_time > 5.0:
            indicators.append('slow_response')
        
        # Check for server load headers
        server_timing = response.headers.get('Server-Timing', '')
        if 'cpu' in server_timing.lower():
            # Parse server timing if available
            indicators.append('cpu_timing')
        
        # X-RateLimit headers indicate approaching limits
        if 'X-RateLimit-Remaining' in response.headers:
            remaining = int(response.headers.get('X-RateLimit-Remaining', 1000))
            if remaining < 10:
                indicators.append('rate_limit_approaching')
        
        # Check for cache headers
        cache_control = response.headers.get('Cache-Control', '')
        if 'no-cache' in cache_control or 'must-revalidate' in cache_control:
            indicators.append('dynamic_content')
        
        self.host_server_load_indicators[hostname].extend(indicators)
        
        # Keep only recent indicators
        if len(self.host_server_load_indicators[hostname]) > 50:
            self.host_server_load_indicators[hostname] = \
                self.host_server_load_indicators[hostname][-50:]
    
    def _adaptive_delay_adjustment(self, hostname: str):
        """Adjust crawl delay based on server behavior patterns"""
        
        with self.lock:
            # Calculate recent success rate
            recent_successes = list(self.host_success_rates[hostname])
            if len(recent_successes) >= 5:
                success_rate = sum(recent_successes) / len(recent_successes)
                
                if success_rate < 0.7:  # Less than 70% success
                    # Increase delay for struggling servers
                    self.host_delays[hostname] *= 1.3
                elif success_rate > 0.95:  # More than 95% success
                    # Slightly decrease delay for healthy servers
                    self.host_delays[hostname] *= 0.95
            
            # Adjust based on response times
            recent_times = list(self.host_response_times[hostname])
            if len(recent_times) >= 5:
                avg_response_time = np.mean(recent_times)
                
                if avg_response_time > 3.0:  # Slow responses
                    self.host_delays[hostname] *= 1.2
                elif avg_response_time < 0.5:  # Fast responses
                    self.host_delays[hostname] *= 0.9
            
            # Adjust based on server load indicators
            recent_indicators = self.host_server_load_indicators[hostname][-20:]
            load_score = len(recent_indicators)
            
            if load_score > 10:  # High load indicators
                self.host_delays[hostname] *= 1.5
            elif load_score == 0:  # No load indicators
                self.host_delays[hostname] *= 0.9
            
            # Ensure delay stays within bounds
            self.host_delays[hostname] = max(
                min(self.host_delays[hostname], self.policy.max_delay),
                self.policy.base_delay
            )

# Usage with adaptive behavior
adaptive_policy = CrawlPolicy(base_delay=1.0, max_delay=30.0)
adaptive_crawler = AdaptivePoliteCrawler(adaptive_policy)

# The crawler will automatically adjust delays based on server behavior
```

### Distributed Politeness Coordination

```python
import redis
import json
import hashlib
from typing import Any

class DistributedPoliteCrawler:
    def __init__(self, policy: CrawlPolicy, redis_client: redis.Redis, 
                 crawler_id: str):
        self.policy = policy
        self.redis = redis_client
        self.crawler_id = crawler_id
        self.local_crawler = PoliteCrawler(policy)
        
        # Redis key prefixes
        self.host_delay_key = "crawler:host_delays"
        self.host_requests_key = "crawler:host_requests"
        self.host_errors_key = "crawler:host_errors"
        self.crawler_heartbeat_key = "crawler:heartbeat"
        
        # Distributed state sync interval
        self.sync_interval = 30.0  # 30 seconds
        self.last_sync = 0.0
    
    def can_crawl_distributed(self, url: str) -> Tuple[bool, str]:
        """Check if URL can be crawled with distributed coordination"""
        
        hostname = urlparse(url).netloc
        
        # Sync with distributed state if needed
        current_time = time.time()
        if current_time - self.last_sync > self.sync_interval:
            self._sync_distributed_state()
            self.last_sync = current_time
        
        # Check local politeness first
        can_crawl_local, reason = self.local_crawler.can_crawl(url)
        if not can_crawl_local:
            return False, reason
        
        # Check distributed concurrent limits
        active_crawlers = self._get_active_crawlers_for_host(hostname)
        if len(active_crawlers) >= self.policy.concurrent_limit:
            return False, f"Distributed concurrent limit exceeded"
        
        return True, "OK"
    
    def crawl_url_distributed(self, url: str) -> Optional[requests.Response]:
        """Crawl URL with distributed politeness coordination"""
        
        hostname = urlparse(url).netloc
        
        # Check distributed politeness
        can_crawl, reason = self.can_crawl_distributed(url)
        if not can_crawl:
            return None
        
        # Register this crawler as active for the host
        self._register_crawler_activity(hostname)
        
        try:
            # Use local crawler for actual request
            response = self.local_crawler.crawl_url(url)
            
            # Share response data with other crawlers
            if response:
                self._share_response_data(hostname, response)
            
            return response
            
        finally:
            # Unregister crawler activity
            self._unregister_crawler_activity(hostname)
    
    def _sync_distributed_state(self):
        """Synchronize local state with distributed state"""
        
        # Get distributed delay information
        distributed_delays = self.redis.hgetall(self.host_delay_key)
        
        for hostname_bytes, delay_bytes in distributed_delays.items():
            hostname = hostname_bytes.decode()
            delay = float(delay_bytes)
            
            # Update local delay if distributed delay is higher
            with self.local_crawler.lock:
                current_delay = self.local_crawler.host_delays[hostname]
                if delay > current_delay:
                    self.local_crawler.host_delays[hostname] = delay
        
        # Share local state with distributed store
        for hostname, delay in self.local_crawler.host_delays.items():
            existing_delay = self.redis.hget(self.host_delay_key, hostname)
            if existing_delay is None or float(existing_delay) < delay:
                self.redis.hset(self.host_delay_key, hostname, delay)
    
    def _get_active_crawlers_for_host(self, hostname: str) -> List[str]:
        """Get list of active crawlers for a host"""
        
        # Get all crawler heartbeats for this host
        pattern = f"{self.host_requests_key}:{hostname}:*"
        keys = self.redis.keys(pattern)
        
        current_time = time.time()
        active_crawlers = []
        
        for key in keys:
            last_activity = self.redis.get(key)
            if last_activity and current_time - float(last_activity) < 60:
                # Extract crawler ID from key
                crawler_id = key.decode().split(':')[-1]
                active_crawlers.append(crawler_id)
        
        return active_crawlers
    
    def _register_crawler_activity(self, hostname: str):
        """Register this crawler as active for a host"""
        
        key = f"{self.host_requests_key}:{hostname}:{self.crawler_id}"
        self.redis.setex(key, 120, time.time())  # 2 minute TTL
    
    def _unregister_crawler_activity(self, hostname: str):
        """Unregister crawler activity for a host"""
        
        key = f"{self.host_requests_key}:{hostname}:{self.crawler_id}"
        self.redis.delete(key)
    
    def _share_response_data(self, hostname: str, response: requests.Response):
        """Share response data with other crawlers"""
        
        # Share useful response data for collective learning
        response_data = {
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'timestamp': time.time(),
            'crawler_id': self.crawler_id
        }
        
        # Store recent responses (keep last 10)
        key = f"crawler:responses:{hostname}"
        self.redis.lpush(key, json.dumps(response_data))
        self.redis.ltrim(key, 0, 9)  # Keep only last 10
        self.redis.expire(key, 3600)  # 1 hour expiry

# Usage with distributed coordination  
redis_client = redis.Redis(host='localhost', port=6379, db=0)
distributed_crawler = DistributedPoliteCrawler(
    policy, redis_client, "crawler-1"
)

response = distributed_crawler.crawl_url_distributed("https://example.com/page")
```

## Politeness Monitoring and Metrics

```python
import logging
from dataclasses import asdict
import json

class PolitenessMonitor:
    def __init__(self, crawler: PoliteCrawler):
        self.crawler = crawler
        self.logger = logging.getLogger('politeness_monitor')
        
        # Set up detailed logging
        handler = logging.FileHandler('crawler_politeness.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_crawl_attempt(self, url: str, can_crawl: bool, reason: str):
        """Log crawl attempt with politeness decision"""
        
        hostname = urlparse(url).netloc
        current_delay = self.crawler.host_delays[hostname]
        
        log_data = {
            'url': url,
            'hostname': hostname,
            'can_crawl': can_crawl,
            'reason': reason,
            'current_delay': current_delay,
            'active_requests': self.crawler.host_active_requests[hostname],
            'error_count': self.crawler.host_error_counts[hostname]
        }
        
        if can_crawl:
            self.logger.info(f"CRAWL_ALLOWED: {json.dumps(log_data)}")
        else:
            self.logger.warning(f"CRAWL_BLOCKED: {json.dumps(log_data)}")
    
    def log_response(self, url: str, response: requests.Response):
        """Log response with performance metrics"""
        
        hostname = urlparse(url).netloc
        
        log_data = {
            'url': url,
            'hostname': hostname,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'content_length': len(response.content),
            'server': response.headers.get('Server', 'unknown'),
            'cache_control': response.headers.get('Cache-Control', ''),
            'rate_limit_remaining': response.headers.get('X-RateLimit-Remaining', '')
        }
        
        self.logger.info(f"RESPONSE: {json.dumps(log_data)}")
    
    def generate_politeness_report(self) -> Dict:
        """Generate comprehensive politeness report"""
        
        with self.crawler.lock:
            report = {
                'timestamp': datetime.now().isoformat(),
                'policy': asdict(self.crawler.policy),
                'statistics': self.crawler.get_stats(),
                'host_delays': dict(self.crawler.host_delays),
                'host_error_counts': dict(self.crawler.host_error_counts),
                'active_hosts': len(self.crawler.host_last_request),
                'politeness_score': self._calculate_politeness_score()
            }
        
        return report
    
    def _calculate_politeness_score(self) -> float:
        """Calculate overall politeness score (0-100)"""
        
        score = 100.0
        
        # Penalize for high error rates
        total_requests = self.crawler.stats['requests_made']
        total_errors = self.crawler.stats['errors_encountered']
        
        if total_requests > 0:
            error_rate = total_errors / total_requests
            score -= error_rate * 30  # Max 30 point penalty
        
        # Penalize for blocked requests
        total_attempts = total_requests + self.crawler.stats['requests_blocked']
        if total_attempts > 0:
            block_rate = self.crawler.stats['requests_blocked'] / total_attempts
            score -= block_rate * 20  # Max 20 point penalty
        
        # Bonus for respecting robots.txt
        if self.crawler.policy.respect_robots:
            score += 10
        
        # Bonus for reasonable delays
        avg_delay = sum(self.crawler.host_delays.values()) / max(len(self.crawler.host_delays), 1)
        if avg_delay >= 1.0:
            score += 10
        
        return max(0.0, min(100.0, score))

# Usage with monitoring
monitor = PolitenessMonitor(crawler)

# Enhanced crawling with monitoring
for url in urls:
    can_crawl, reason = crawler.can_crawl(url)
    monitor.log_crawl_attempt(url, can_crawl, reason)
    
    if can_crawl:
        response = crawler.crawl_url(url)
        if response:
            monitor.log_response(url, response)

# Generate politeness report
report = monitor.generate_politeness_report()
print(f"Politeness Score: {report['politeness_score']:.1f}/100")
```

<div class="decision-box">
<strong>Decision Framework</strong>:

- **Large-scale crawlers**: Distributed politeness with Redis coordination
- **Research crawlers**: Adaptive politeness with detailed monitoring
- **Commercial crawlers**: Strict robots.txt compliance with rate limiting
- **News aggregators**: Lightweight politeness with error handling
- **SEO tools**: Enhanced politeness with competitive analysis
- **Academic research**: Maximum politeness with detailed logging
</div>

## Trade-offs

| Approach | Respectfulness | Performance | Complexity | Resource Usage |
|----------|----------------|-------------|------------|----------------|
| Basic Politeness | Good | High | Low | Low |
| Adaptive Politeness | Excellent | Medium | Medium | Medium |
| Distributed Politeness | Excellent | Medium | High | High |
| Monitored Politeness | Excellent | Medium | Medium | Medium |

## Common Politeness Violations

### What NOT to Do

1. **Excessive Parallelism**
   ```python
   # ❌ Don't do this
   with ThreadPoolExecutor(max_workers=100) as executor:
       futures = [executor.submit(requests.get, url) for url in urls]
   ```

2. **Ignoring robots.txt**
   ```python
   # ❌ Don't do this
   def crawl_everything(base_url):
       # Completely ignore robots.txt restrictions
       pass
   ```

3. **No Rate Limiting**
   ```python
   # ❌ Don't do this
   for url in urls:
       requests.get(url)  # Immediate requests
   ```

4. **Aggressive Retries**
   ```python
   # ❌ Don't do this
   for _ in range(10):  # 10 immediate retries
       try:
           response = requests.get(url, timeout=1)
           break
       except:
           continue  # No delay between retries
   ```

## Best Practices

### Essential Politeness Rules

1. **Respect robots.txt**: Always check and follow robots.txt directives
2. **Rate limiting**: Implement delays between requests to same host
3. **Concurrent limits**: Limit parallel requests per host
4. **Error handling**: Back off on errors, don't retry aggressively
5. **User-Agent identification**: Use descriptive, contactable User-Agent
6. **Timeout handling**: Set reasonable request timeouts
7. **Adaptive behavior**: Adjust based on server responses

### Advanced Politeness

8. **Cache robots.txt**: Don't fetch robots.txt for every request
9. **Honor Retry-After**: Respect HTTP 429 Retry-After headers
10. **Monitor server health**: Detect and respond to server stress
11. **Distributed coordination**: Coordinate across multiple crawlers
12. **Resource-aware crawling**: Consider server load indicators

## Related Patterns
- [Rate Limiting](rate-limiting.md) - Request frequency control
- [Circuit Breaker](circuit-breaker.md) - Failure protection
- [Backpressure](backpressure.md) - Load management
- [URL Frontier](url-frontier.md) - Polite URL queue management

## References
- [Robots Exclusion Protocol](https://www.robotstxt.org/)
- [HTTP 429 Too Many Requests](https://tools.ietf.org/html/rfc6585#section-4)
- [Web Crawling Ethics](https://blog.apify.com/web-scraping-ethics/)
- [Google Webmaster Guidelines](https://developers.google.com/search/docs/advanced/guidelines/webmaster-guidelines)