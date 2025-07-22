# Code Analysis Report for MkDocs Documentation

**Total Issues Found:** 172

**High Severity:** 5
**Medium Severity:** 167
**Low Severity:** 0

## Issues by Type

- **Bad Practice:** 1 issues
- **Deprecated Syntax:** 5 issues
- **Missing Error Handling:** 9 issues
- **Missing Language:** 152 issues
- **Security Issue:** 5 issues

## Detailed Issues by File

### docs/case-studies/ad-click-aggregation.md

**1 issues found**

**Line 474** 🟡 **Deprecated Syntax**
- **Issue:** Deprecated syntax detected: Avoid SELECT *, specify columns explicitly
- **Recommendation:** Avoid SELECT *, specify columns explicitly
- **Code Snippet:**
  ```
  -- Create OLAP cube for fast queries
CREATE TABLE click_cube AS
WITH dimensions AS (
    SELECT 
        DATE_TRUNC('hour', timestamp) as hour,
        advertiser_id,
        publisher_id,
        cam...
  ```

### docs/case-studies/distributed-message-queue-enhanced.md

**1 issues found**

**Line 801** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class PerformanceOptimizer:
    """Optimizations for high throughput"""
    
    def __init__(self):
        self.batch_size = 16384  # 16KB
        self.linger_ms = 10
        self.compression_type =...
  ```

### docs/case-studies/distributed-message-queue.md

**7 issues found**

**Line 134** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Partition 0:
[Offset 0][Offset 1][Offset 2][Offset 3]...[Offset N]
   |         |         |         ...
  ```

**Line 186** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Topic: Orders (6 partitions)
Consumer Group: OrderProcessors (3 consumers)

Assignment:
- Consumer 1...
  ```

**Line 205** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  1. Read data from disk to OS buffer
2. Copy from OS buffer to application buffer
3. Copy from applic...
  ```

**Line 213** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  1. Read data from disk to OS buffer
2. Send directly from OS buffer to NIC
  ```

**Line 283** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Message size: 1KB
Retention: 7 days
Throughput: 100K messages/sec

Daily storage = 100K * 1KB * 8640...
  ```

**Line 317** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Partition Scenario:
[Broker 1, 2] <--X--> [Broker 3, 4, 5]

With min.insync.replicas = 2:
- Minority...
  ```

**Line 328** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Consumer Group Before:
- C1: Partitions 0,1,2
- C2: Partitions 3,4,5

C1 Fails →

Rebalancing Result...
  ```

### docs/case-studies/metrics-monitoring.md

**9 issues found**

**Line 142** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Metric: http_requests_total
Labels: {method="GET", endpoint="/api/users", status="200", region="us-e...
  ```

**Line 187** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Recent Data (Hot Storage):
- In-memory for last 2 hours
- SSD for last 24 hours
- Optimized for writ...
  ```

**Line 272** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  # Explosion example
metrics = 1000
services = 100
endpoints = 50
regions = 10
status_codes = 5

Tota...
  ```

**Line 362** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Global Level (Cross-Region):
  ├── Regional Level (US-East)
  │   ├── Cluster Level (Prod-1)
  │   │...
  ```

**Line 438** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Inverted Index:
  "region=us-east" -> [series1, series2, series3, ...]
  "service=api" -> [series2, ...
  ```

**Line 487** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  prometheus_tsdb_head_samples_appended_total
prometheus_tsdb_compaction_duration_seconds
prometheus_r...
  ```

**Line 516** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Impact: Loss of recent data (last 2 hours)
Mitigation: 
- 3x replication across nodes
- Automatic fa...
  ```

**Line 525** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Symptoms: 
- Query latency spikes
- Memory exhaustion
- CPU throttling

Mitigation:
- Query result c...
  ```

**Line 539** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Detection:
- Series count growing exponentially
- Memory usage increasing rapidly
- Ingestion slowin...
  ```

### docs/case-studies/prometheus-datadog-enhanced.md

**2 issues found**

**Line 451** 🟡 **Deprecated Syntax**
- **Issue:** Deprecated syntax detected: Use print() function syntax
- **Recommendation:** Use print() function syntax
- **Code Snippet:**
  ```
  import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import aioredis

class AlertRule:
    """Alert rule definition"""
    
    def __init__(self, rule_...
  ```

**Line 631** 🟡 **Bad Practice**
- **Issue:** Wildcard import detected
- **Recommendation:** Use specific imports instead of import *
- **Code Snippet:**
  ```
  from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pyspark.sql.functions as F

class MetricAggregationPipeline:
    """Spark-based metric a...
  ```

### docs/case-studies/proximity-service-enhanced.md

**1 issues found**

**Line 33** 🟡 **Deprecated Syntax**
- **Issue:** Deprecated syntax detected: Avoid SELECT *, specify columns explicitly
- **Recommendation:** Avoid SELECT *, specify columns explicitly
- **Code Snippet:**
  ```
  -- Original naive approach
SELECT * FROM businesses 
WHERE latitude BETWEEN :lat - 0.1 AND :lat + 0.1
  AND longitude BETWEEN :lng - 0.1 AND :lng + 0.1
ORDER BY distance(latitude, longitude, :lat, :ln...
  ```

### docs/case-studies/s3-object-storage-enhanced.md

**1 issues found**

**Line 1292** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class S3MetricsCollector:
    """Collects and aggregates S3 metrics"""
    
    def __init__(self):
        self.metrics_pipeline = MetricsPipeline()
        self.request_logger = RequestLogger()
    ...
  ```

### docs/case-studies/spotify-recommendations.md

**6 issues found**

**Line 211** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## 📊 Complete Axiom Analysis

### Comprehensive Axiom Mapping Table

| Design Decision | Axiom 1: L...
  ```

**Line 339** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## 🏛️ Architecture Alternatives

### Alternative 1: Pure Collaborative Filtering

  ```

**Line 364** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Alternative 2: Content-Based System

  ```

**Line 393** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Alternative 3: Deep Learning Only

  ```

**Line 422** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Alternative 4: Graph-Based Recommendation

  ```

**Line 452** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Alternative 5: Spotify's Hybrid Architecture

  ```

### docs/case-studies/web-crawler.md

**3 issues found**

**Line 237** 🟡 **Deprecated Syntax**
- **Issue:** Deprecated syntax detected: Use print() function syntax
- **Recommendation:** Use print() function syntax
- **Code Snippet:**
  ```
  import rocksdb
import mmh3
from urllib.parse import urlparse
import heapq
from collections import defaultdict
import struct

class ScalableURLFrontier:
    def __init__(self, num_priority_queues=1000)...
  ```

**Line 237** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  import rocksdb
import mmh3
from urllib.parse import urlparse
import heapq
from collections import defaultdict
import struct

class ScalableURLFrontier:
    def __init__(self, num_priority_queues=1000)...
  ```

**Line 2001** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class CostOptimizedCrawler:
    def __init__(self):
        self.cost_tracker = CostTracker()
        self.bandwidth_used = 0
        self.storage_used = 0
        self.compute_hours = 0
        
    ...
  ```

### docs/case-studies/youtube-enhanced.md

**1 issues found**

**Line 346** 🟡 **Deprecated Syntax**
- **Issue:** Deprecated syntax detected: Use print() function syntax
- **Recommendation:** Use print() function syntax
- **Code Snippet:**
  ```
  class TieredStorageManager:
    """Manage hot/warm/cold storage tiers"""
    
    def __init__(self):
        self.tiers = {
            'hot': {
                'type': 'SSD',
                'capaci...
  ```

### docs/human-factors/blameless-postmortems.md

**2 issues found**

**Line 233** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Process   │ │   Tools     │ │   ...
  ```

**Line 269** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  ┌─────────────────────────────────────────────────────────────┐
│                  Postmortem Qualit...
  ```

### docs/human-factors/incident-response.md

**3 issues found**

**Line 338** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## Incident Classification Framework

### Severity Assessment Matrix

| Criteria ↓ / Level → | SEV-...
  ```

**Line 375** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## Incident Metrics

### Key Performance Indicators
- **MTTA** (Mean Time To Acknowledge)
- **MTTD*...
  ```

**Line 411** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## Communication Strategy Matrix

### Stakeholder Communication Plan

| Stakeholder | SEV-1 | SEV-2...
  ```

### docs/human-factors/oncall-culture.md

**2 issues found**

**Line 359** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
          Mon  Tue  Wed  Thu  Fri  Sat  Sun
00-04   🟢   🟢   🟢   🟢   🟢   🟡   🟡
04-08   🟢   🟢   🟢   🟢   ...
  ```

**Line 383** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  ┌─────────────────────────────────────────────────────────────┐
│                    Alert Quality S...
  ```

### docs/part1-axioms/axiom1-latency/index-enhanced.md

**15 issues found**

**Line 22** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
      L1 cache reference ......................... 0.5 ns
    L2 cache reference ........................
  ```

**Line 60** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
The practical manifestation of this constraint:
- **Theoretical basis**: Einstein's special relativ...
  ```

**Line 79** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Quick Reference Table**:

| Route | Distance | Theoretical Min | Typical Reality | Why the Differ...
  ```

**Line 118** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Why This Constraint Exists

Unlike software bugs or implementation details, this is a fundament...
  ```

**Line 203** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## ⚙️ Practical Implications

How this constraint shapes real system design:

### Quantitative...
  ```

**Line 230** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Engineering Guidelines

When designing systems, always:

1. **Measure First**: Use tools like `...
  ```

**Line 273** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
This is latency in distributed systems: **the fundamental time it takes for information to travel f...
  ```

**Line 334** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Impact on System Architecture

Different latency tolerances drive different architectures:

| L...
  ```

**Line 363** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
This creates a latency-bandwidth product limit:

  ```

**Line 371** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Little's Law Applied

For distributed systems²³:

  ```

**Line 388** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🛠️ Mitigation Strategies

Since we can't beat physics, we work around it:

### 1. Proximity...
  ```

**Line 407** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### 2. Predictive Prefetching
  ```

**Line 420** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### 3. Protocol Optimization
  ```

**Line 433** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### 4. Asynchronous Design
  ```

**Line 446** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🎯 Quick Decision Guide

  ```

### docs/part1-axioms/axiom2-capacity/examples.md

**2 issues found**

**Line 130** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  00:00 - Black Friday sale starts
00:02 - Traffic spike begins (10x normal)
00:05 - Database connecti...
  ```

**Line 660** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Connection Pool Full → Threads Block → 
CPU Idle → Requests Queue → 
Timeouts → Retries → More Load ...
  ```

### docs/part1-axioms/axiom2-capacity/exercises.md

**1 issues found**

**Line 388** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Load Balancer (10K RPS capacity)
    ↓
Web Servers (100 instances, 100 RPS each)
    ↓
Cache Layer (...
  ```

### docs/part1-axioms/axiom4-concurrency/examples.md

**1 issues found**

**Line 668** 🔴 **Security Issue**
- **Issue:** Security issue: eval() can be dangerous
- **Recommendation:** Remove or replace: eval() can be dangerous
- **Code Snippet:**
  ```
  class RedisDistributedLock:
    """Distributed lock with safety properties"""
    
    def __init__(self, redis_client, key, timeout=10):
        self.redis = redis_client
        self.key = f"lock:{k...
  ```

### docs/part1-axioms/axiom4-concurrency/index.md

**6 issues found**

**Line 949** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Facebook's TAO: Optimistic Concurrency at Scale

  ```

**Line 1076** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Uber's Ringpop: Consistent Hashing with Concurrent Updates

  ```

**Line 1238** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## Level 5: Mastery (The Art of Concurrency) 🌴

### The Linux Kernel: RCU (Read-Copy-Update)

  ```

**Line 1331** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### CockroachDB: Distributed SQL Transactions

  ```

**Line 1503** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### The Art of Lock-Free Programming

  ```

**Line 1677** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### The Disruptor Pattern: Mechanical Sympathy

  ```

### docs/part1-axioms/axiom5-coordination/examples.md

**1 issues found**

**Line 1231** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class UberMarketplace:
    """City-level sharding to minimize coordination"""
    
    def __init__(self):
        self.cities = {}  # city -> local marketplace
        self.cross_city_trips = 0.001  ...
  ```

### docs/part1-axioms/axiom6-observability/index.md

**1 issues found**

**Line 680** 🔴 **Security Issue**
- **Issue:** Security issue: Hardcoded password detected
- **Recommendation:** Remove or replace: Hardcoded password detected
- **Code Snippet:**
  ```
  class SyntheticMonitor:
    """Probe your system continuously"""
    
    @every(60)  # Every minute
    def probe_critical_path(self):
        # Create synthetic user journey
        trace_id = gener...
  ```

### docs/part1-axioms/axiom7-human/examples.md

**3 issues found**

**Line 665** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## COMMON ISSUES AND FIXES

### Issue 1: Database Connection Pool Exhausted
**Symptoms**: "connecti...
  ```

**Line 678** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Issue 2: Memory Leak After 7 Days Uptime
**Symptoms**: Gradually increasing memory, OOM kills
*...
  ```

**Line 689** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## ESCALATION

If service not recovered in 15 minutes:

1. Page secondary: @payments-oncall-seconda...
  ```

### docs/part1-axioms/axiom7-human/index.md

**4 issues found**

**Line 235** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Capacity = Base Capacity 
         - Intrinsic Load (can't reduce)
         - Extraneous Load (MUST ...
  ```

**Line 380** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Step 2: Examine Recent Changes
  ```

**Line 386** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## 🚨 Mitigation Paths

### Path A: High CPU (if CPU > 80%)
1. Enable rate limiting:
   ```bash
   k...
  ```

**Line 416** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
## ✅ Resolution Confirmation
- [ ] Metrics returned to normal
- [ ] Alerts cleared
- [ ] Synthetic ...
  ```

### docs/part2-pillars/control/exercises.md

**1 issues found**

**Line 341** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
</details>

## Exercise 2: Design Rate Limiting Systems

**Challenge**: Create visual designs for m...
  ```

### docs/part2-pillars/intelligence/exercises.md

**1 issues found**

**Line 170** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Score = 0.5 × (1 - ErrorRate) + 0.3 × LatencyScore + 0.2 × VariancePenalty
  ```

### docs/part2-pillars/state/exercises.md

**1 issues found**

**Line 346** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
</details>

## Exercise 2: Design Vector Clock Visualization

**Challenge**: Create visual represen...
  ```

### docs/part2-pillars/truth/exercises.md

**6 issues found**

**Line 68** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
     [Idle] --Local Event--> [Processing] --Complete--> [Idle]
     |                                 ...
  ```

**Line 120** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Protocol Design Options

<div class="decision-box">
<h4>Election Algorithm Comparison</h4>

Des...
  ```

**Line 234** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Protocol State Machines

<div class="truth-box">
<h4>2PC State Transitions</h4>

Design state m...
  ```

**Line 352** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Byzantine Agreement Protocol

<div class="decision-box">
<h4>Byzantine Fault Tolerance Rules</h...
  ```

**Line 502** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Raft Protocol Components

<div class="truth-box">
<h4>Raft Design Principles</h4>

Create visua...
  ```

**Line 651** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Snapshot Algorithm Components

<div class="truth-box">
<h4>Chandy-Lamport Rules</h4>

Design vi...
  ```

### docs/part2-pillars/work/index.md

**15 issues found**

**Line 71** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Dimension        Options              Trade-offs                Real Example
---------        ------...
  ```

**Line 209** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Speedup = 1 / (S + P/N)

Where:
S = Sequential fraction (can't be parallelized)
P = Parallel fractio...
  ```

**Line 518** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**MapReduce Phases Overview:**

| Phase | Operation | Parallelism | Data Structure | Purpose |
|---...
  ```

**Line 573** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**MapReduce Usage Pattern:**

| Step | Function | Description | Example |
|------|----------|------...
  ```

**Line 847** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="truth-box">
<h4>Consistent Hashing Algorithm Flow</h4>

<b>Ring Construction:</b>
<ol>
...
  ```

**Line 918** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="axiom-box">
<h4>Two-Phase Commit Protocol</h4>

<b>Protocol Guarantees:</b>
<ul>
<li><b...
  ```

**Line 970** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="decision-box">
<h4>Speculative Execution Strategy</h4>

<b>When to Use Speculation:</b>...
  ```

**Line 1057** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="truth-box">
<h4>Distributed Task Scheduler Implementation</h4>

<b>Task State Machine:<...
  ```

**Line 1556** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  ### Production War Stories

#### Story 1: The 100x Speed-Up That Almost Broke Everything

**Company*...
  ```

**Line 1601** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  **What Went Wrong**:
1. Database connection pool exhausted (max 100 connections)
2. Memory usage: 10...
  ```

**Line 1638** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="decision-box">
<h4>Smart Processing Strategy</h4>
<table>
<tr><th>Component</th><th>Set...
  ```

**Line 1669** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  **The Solution**: Implemented work stealing

  ```

**Line 1698** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="truth-box">
<h4>Work Stealing Algorithm</h4>

<b>Rebalancing Logic:</b>
<ol>
<li>Calcul...
  ```

**Line 1746** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="decision-box">
<h4>Batch Accumulator Pattern</h4>

<b>Configuration:</b>
<table>
<tr><t...
  ```

**Line 1800** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
<div class="axiom-box">
<h4>Priority Queue with Anti-Starvation</h4>

<b>Priority Levels:</b>
<tabl...
  ```

### docs/patterns/bulkhead.md

**13 issues found**

**Line 692** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Error = 0.4 × (Target_Latency - Current_Latency) / Target_Latency
      + 0.4 × (Current_Rejections ...
  ```

**Line 816** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Container Isolation Benefits**:
| Aspect | Benefit |
|--------|----------|
| **CPU** | Hard limit...
  ```

**Line 879** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🚀 Level 4: Expert

### Real-World Case Study: Amazon's Cell-Based Architecture

#### The Ch...
  ```

**Line 897** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Impact of Shared Fate**:
- 🌍 **Global outages**: One issue affects all regions
- 💣 **Blast radius...
  ```

**Line 994** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
#### Implementation Results

  ```

**Line 1028** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Case Study: Spotify's Squad Isolation

  ```

**Line 1106** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Production Monitoring Dashboard

  ```

**Line 1146** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Enterprise Implementation Patterns

#### Microsoft Azure's Deployment Stamps
  ```

**Line 1218** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🎯 Level 5: Mastery

### Theoretical Foundations of Isolation

#### Queueing Theory Applied ...
  ```

**Line 1634** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 📋 Quick Reference

### Decision Matrix: Choosing Bulkhead Strategy

  ```

**Line 1655** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Configuration Cheat Sheet

| Service Type | Bulkhead Type | Size Formula | Queue Size |
|------...
  ```

**Line 1698** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Implementation Checklist

#### Basic Bulkhead
- [ ] Identify resource boundaries
- [ ] Choose i...
  ```

**Line 1770** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Best Practices Summary

1. **Start small** - Begin with coarse-grained isolation
2. **Monitor e...
  ```

### docs/patterns/caching-strategies.md

**1 issues found**

**Line 36** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Cache:                    With Cache:
Every request → Database         First request → Datab...
  ```

### docs/patterns/cdc.md

**1 issues found**

**Line 36** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Approach:              CDC Approach:
Database → Batch ETL → Target     Database → Change...
  ```

### docs/patterns/distributed-lock.md

**1 issues found**

**Line 38** 🔴 **Security Issue**
- **Issue:** Security issue: eval() can be dangerous
- **Recommendation:** Remove or replace: eval() can be dangerous
- **Code Snippet:**
  ```
  import redis
import time
import uuid

class SimpleDistributedLock:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def acquire(self, resource: str, timeout_ms...
  ```

### docs/patterns/edge-computing.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Cloud (Central Hospital):        Edge Computing (Distributed Care):

🏥 Main Hospital    ...
  ```

**Line 49** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  The Edge Computing Hierarchy:

☁️ Cloud (Brain)
   ↓ Strategic decisions, deep analysis
🏢 Regional D...
  ```

### docs/patterns/event-driven.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional (Request-Response):          Event-Driven:

📱 Phone Calls                          📻 Rad...
  ```

**Line 47** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Synchronous Architecture:               Event-Driven Architecture:

Order Service                   ...
  ```

### docs/patterns/finops.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without FinOps (Living without a budget):
- Electric bill arrives: "Why is it $500?!"
- "Who left al...
  ```

**Line 64** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  What you see (10%):
┌─────────────────┐
│ Compute (EC2)   │ ← "Our servers cost $10K/month"
└───────...
  ```

### docs/patterns/geo-replication.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Single Library:                       Global Library Network:

📚 Central Library                    ...
  ```

**Line 50** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Geo-Replication:              With Geo-Replication:

Users → [Atlantic Ocean] → Server     U...
  ```

### docs/patterns/graphql-federation.md

**2 issues found**

**Line 1040** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  C(Q) = Σᵢ (Lᵢ × Dᵢ) + Σⱼ (Nⱼ × Tⱼ) + P × log(F)

Where:
- Lᵢ = Latency of service i
- Dᵢ = Data tran...
  ```

**Line 1054** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  E = (R₁ / Rₙ) × (1 / C)

Where:
- R₁ = Response time with 1 service
- Rₙ = Response time with n serv...
  ```

### docs/patterns/health-check.md

**1 issues found**

**Line 267** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class DependencyHealthChecker:
    """Check health of all dependencies with smart aggregation"""

    def __init__(self):
        self.dependencies = {}
        self.weights = {}  # Importance weights...
  ```

### docs/patterns/idempotent-receiver.md

**5 issues found**

**Line 364** 🔴 **Security Issue**
- **Issue:** Security issue: eval() can be dangerous
- **Recommendation:** Remove or replace: eval() can be dangerous
- **Code Snippet:**
  ```
  import asyncio
from enum import Enum
from typing import List, Dict, Any, Optional, Set
import time
from dataclasses import dataclass, field
from collections import defaultdict

class ProcessingStatus(...
  ```

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Idempotency:               With Idempotency:
Person presses UP button           Person press...
  ```

**Line 44** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  The Duplicate Message Problem:

Network: "Did you get my message?"
→ No response (timeout)
→ "Let me...
  ```

**Line 949** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🎯 Level 5: Mastery

### Theoretical Foundations

#### Formal Verification of Idempotency

  ```

**Line 1162** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Economic Impact

  ```

### docs/patterns/leader-election.md

**5 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  🏫 Classroom Election Process:

1. Campaign Period (FOLLOWER state)
   - Everyone is equal
   - Stude...
  ```

**Line 56** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Distributed System without Leader:     With Leader Election:

🖥️ → 📊 ← 🖥️                          🖥...
  ```

**Line 154** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Term 1: Node A elected
Term 2: Node A fails, Node B elected  
Term 3: Network partition, Node C elec...
  ```

**Line 197** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  5 nodes: Need 3 votes to win (⌊5/2⌋ + 1 = 3)
7 nodes: Need 4 votes to win (⌊7/2⌋ + 1 = 4)
9 nodes: N...
  ```

**Line 747** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Scenario 1: Clean Partition
[A, B] | [C, D, E]
- Right side elects leader (has majority)
- Left side...
  ```

### docs/patterns/load-shedding.md

**1 issues found**

**Line 96** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  import time
import heapq
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class Request:
    id: str
    priority: int
    cost: float
    timestamp: float
    user_tier: st...
  ```

### docs/patterns/observability.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Observability (Emergency Room):
Patient: "I don't feel well"
Doctor: "Where does it hurt?"
P...
  ```

**Line 61** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  METRICS: The Speedometer
"How fast are we going?"
- Request rate: 1000/sec
- Error rate: 0.1%
- Resp...
  ```

### docs/patterns/outbox.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Outbox:                    With Outbox:
Doctor: "Patient discharged!"      Doctor writes in ...
  ```

**Line 44** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  The Dual-Write Problem:

Application: "Save order AND send email!"

Scenario 1: ✓ Save → ✗ Email = C...
  ```

### docs/patterns/pattern-comparison.md

**5 issues found**

**Line 97** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Legend: 
✅ Excellent combination
🟡 Good combination
⚠️ Possible but complex
❌ Not recommended
  ```

**Line 164** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  High Performance ←──────────────→ High Complexity

Simple                                          C...
  ```

**Line 364** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Frontend → API Gateway (Rate Limiting)
         → Service Mesh
         → Microservices:
           ...
  ```

**Line 376** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Mobile Apps → Edge Computing (Caching)
           → GraphQL Federation
           → Services:
      ...
  ```

**Line 387** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Trading Apps → API Gateway (Rate Limiting + Auth)
            → Service Mesh (mTLS + Circuit Breaker...
  ```

### docs/patterns/queues-streaming.md

**1 issues found**

**Line 54** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Queues:                    With Queues:

Client → Service → Database        Client → Queue →...
  ```

### docs/patterns/rate-limiting.md

**7 issues found**

**Line 143** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional

class TokenBucket(RateLimiter):
    """Token bucket algorithm with burst support"""

    def __init__(self, capacity: int,...
  ```

**Line 973** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Geographic Rate Limiting

  ```

**Line 1031** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Machine Learning Enhanced Rate Limiting

  ```

**Line 1114** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🚀 Level 4: Expert

### Real-World Case Study: GitHub's Rate Limiting Evolution

#### The Ch...
  ```

**Line 1132** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Impact**:
- 🔥 **23% of API capacity** consumed by abusive clients
- 😤 **P99 latency increased 5x*...
  ```

**Line 1554** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Enterprise Rate Limiting Patterns

#### Multi-Tenant Rate Limiting
  ```

**Line 1823** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
---

## 🎯 Level 5: Mastery

### Next-Generation Rate Limiting

#### Quantum-Resistant Rate Limiting
  ```

### docs/patterns/retry-backoff.md

**4 issues found**

**Line 763** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Budget Configuration**:
| Service Type | Budget % | Window | Reasoning |
|--------------|--------...
  ```

**Line 871** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Real-World Implementation Patterns

#### AWS SDK Retry Strategy
  ```

**Line 961** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
**Impact**:
- 🔥 **Single service failure** took down entire Netflix
- 💸 **$1M+ per hour** in lost r...
  ```

**Line 1008** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
#### Implementation Details

  ```

### docs/patterns/saga.md

**2 issues found**

**Line 383** 🔴 **Security Issue**
- **Issue:** Security issue: eval() can be dangerous
- **Recommendation:** Remove or replace: eval() can be dangerous
- **Code Snippet:**
  ```
  import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

# Saga Persistence for Recovery
class SagaRe...
  ```

**Line 54** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Transaction:          Saga Pattern:

┌─────────────────┐              Step 1: Book Fligh...
  ```

### docs/patterns/serverless-faas.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Server (Restaurant):          Serverless (Food Truck Rally):

🏢 Own Kitchen             ...
  ```

**Line 48** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Architecture:                 Serverless Architecture:

     Load Balancer              ...
  ```

### docs/patterns/service-discovery.md

**1 issues found**

**Line 811** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  
### Future Directions

1. **ML-Driven Discovery**: Predict service locations before lookup
2. **Blo...
  ```

### docs/patterns/service-mesh.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Traditional Approach (No Mesh):        With Service Mesh:

🏢 → 🏢 Direct roads                  🏢 ← S...
  ```

**Line 45** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Without Service Mesh:                  With Service Mesh:

Service A ←→ Service B                Ser...
  ```

### docs/patterns/sharding.md

**1 issues found**

**Line 33** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Unsharded:                    Sharded:
┌─────────────────┐          ┌──────┐ ┌──────┐ ┌──────┐
│   A...
  ```

### docs/patterns/tunable-consistency.md

**2 issues found**

**Line 30** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  🍔 Fast Food (Eventual Consistency)
- Order at any counter
- Food might vary slightly
- Super fast se...
  ```

**Line 52** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Different Operations, Different Needs:

💰 Bank Transfer         ❤️ Social Media Like      📊 Analytic...
  ```

### docs/reference/security.md

**1 issues found**

**Line 246** 🟡 **Missing Error Handling**
- **Issue:** Network calls without exception handling
- **Recommendation:** Add try/except blocks for network operations
- **Code Snippet:**
  ```
  class OAuth2Handler:
    def __init__(self, client_id, client_secret, auth_server_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_server_url = aut...
  ```

### docs/tools/index.md

**5 issues found**

**Line 465** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  L = λ × W
- L = Items in system
- λ = Arrival rate
- W = Time in system
  ```

**Line 473** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Speedup = 1 / (S + P/N)
- S = Serial fraction
- P = Parallel fraction  
- N = Number of processors
  ```

**Line 481** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Bandwidth (Mbps) = File Size (MB) × 8 / Time (seconds)
Time = Distance (km) / 200,000 km/s + Process...
  ```

**Line 487** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  IOPS = 1000 / (Seek Time + Latency)
Throughput = IOPS × Block Size
  ```

**Line 493** 🟡 **Missing Language**
- **Issue:** Code block missing language specification
- **Recommendation:** Add language identifier to code block (e.g., ```python)
- **Code Snippet:**
  ```
  Serial: A = A₁ × A₂ × ... × Aₙ
Parallel: A = 1 - (1-A₁) × (1-A₂) × ... × (1-Aₙ)
  ```

## High Priority Recommendations

1. **docs/patterns/saga.md:383** - Security issue: eval() can be dangerous
   - Remove or replace: eval() can be dangerous

1. **docs/patterns/idempotent-receiver.md:364** - Security issue: eval() can be dangerous
   - Remove or replace: eval() can be dangerous

1. **docs/patterns/distributed-lock.md:38** - Security issue: eval() can be dangerous
   - Remove or replace: eval() can be dangerous

1. **docs/part1-axioms/axiom6-observability/index.md:680** - Security issue: Hardcoded password detected
   - Remove or replace: Hardcoded password detected

1. **docs/part1-axioms/axiom4-concurrency/examples.md:668** - Security issue: eval() can be dangerous
   - Remove or replace: eval() can be dangerous
