---
title: Sharding (Data Partitioning)
description: "Horizontally partition data across multiple databases to improve scalability and performance"
type: pattern
difficulty: advanced
reading_time: 30 min
prerequisites: []
pattern_type: "data"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Sharding (Data Partitioning)**

# Sharding (Data Partitioning)

**Divide and conquer at scale**

## THE PROBLEM

```
Single database limits:
- 10TB data → Doesn't fit on one machine
- 1M queries/sec → CPU melts
- Global users → 200ms+ latency
- Single failure → Everything down

Vertical scaling hits physics
```bash
## THE SOLUTION

```
Sharding: Split data across multiple databases

Users A-F     Users G-M     Users N-S     Users T-Z
   DB1           DB2           DB3           DB4

100TB → 25TB each
1M QPS → 250K QPS each
```bash
## Sharding Strategies

```
1. RANGE SHARDING
   User ID 1-1000 → Shard 1
   User ID 1001-2000 → Shard 2

2. HASH SHARDING
   shard = hash(user_id) % num_shards

3. GEOGRAPHIC SHARDING
   US users → US shard
   EU users → EU shard

4. DIRECTORY SHARDING
   Lookup service maps key → shard
```bash
## IMPLEMENTATION

```python
# Consistent hashing for sharding
class ConsistentHashSharding:
    def __init__(self, nodes, virtual_nodes=150):
        self.nodes = nodes
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self._build_ring()

    def _build_ring(self):
        """Build hash ring with virtual nodes"""
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node.id}:{i}"
                hash_value = self._hash(virtual_key)
                self.ring[hash_value] = node

        # Sort ring positions
        self.sorted_keys = sorted(self.ring.keys())

    def _hash(self, key):
        """Hash function (MD5 for distribution)"""
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def get_shard(self, key):
        """Find shard for key"""
        if not self.ring:
            return None

        hash_value = self._hash(str(key))

        # Find first node clockwise from hash
        idx = bisect.bisect_left(self.sorted_keys, hash_value)

        if idx == len(self.sorted_keys):
            idx = 0

        return self.ring[self.sorted_keys[idx]]

    def add_node(self, node):
        """Add new shard (for scaling)"""
        self.nodes.append(node)

        # Add virtual nodes for new shard
        for i in range(self.virtual_nodes):
            virtual_key = f"{node.id}:{i}"
            hash_value = self._hash(virtual_key)
            self.ring[hash_value] = node
            bisect.insort(self.sorted_keys, hash_value)

    def remove_node(self, node):
        """Remove shard (for maintenance)"""
        self.nodes.remove(node)

        # Remove virtual nodes
        for i in range(self.virtual_nodes):
            virtual_key = f"{node.id}:{i}"
            hash_value = self._hash(virtual_key)
            del self.ring[hash_value]
            self.sorted_keys.remove(hash_value)

# Sharded database client
class ShardedDatabase:
    def __init__(self, shard_config):
        self.sharding = ConsistentHashSharding(
            [Shard(cfg) for cfg in shard_config]
        )
        self.connections = {}

    def get_connection(self, shard):
        """Get connection to shard (with pooling)"""
        if shard.id not in self.connections:
            self.connections[shard.id] = ConnectionPool(
                host=shard.host,
                port=shard.port,
                max_connections=10
            )
        return self.connections[shard.id].get()

    async def write(self, key, value):
        """Write to appropriate shard"""
        shard = self.sharding.get_shard(key)
        conn = self.get_connection(shard)

        try:
            await conn.execute(
                "INSERT INTO data (key, value) VALUES (?, ?)",
                [key, value]
            )
        finally:
            conn.release()

    async def read(self, key):
        """Read from appropriate shard"""
        shard = self.sharding.get_shard(key)
        conn = self.get_connection(shard)

        try:
            result = await conn.query(
                "SELECT value FROM data WHERE key = ?",
                [key]
            )
            return result[0] if result else None
        finally:
            conn.release()

    async def read_range(self, start_key, end_key):
        """Read range across shards (scatter-gather)"""
        # Determine affected shards
        affected_shards = self.get_shards_for_range(start_key, end_key)

        # Query all affected shards in parallel
        futures = []
        for shard in affected_shards:
            future = self.read_range_from_shard(shard, start_key, end_key)
            futures.append(future)

        # Gather and merge results
        all_results = await asyncio.gather(*futures)
        return self.merge_sorted(all_results)

# Cross-shard queries
class CrossShardQueryEngine:
    def __init__(self, sharded_db):
        self.db = sharded_db

    async def join_query(self, query):
        """Execute join across shards"""

        # Example: Find orders for users in specific city
        # SELECT o.* FROM orders o
        # JOIN users u ON o.user_id = u.id
        # WHERE u.city = 'NYC'

        # Step 1: Find all NYC users (might be on multiple shards)
        user_futures = []
        for shard in self.db.all_shards():
            future = shard.query(
                "SELECT id FROM users WHERE city = 'NYC'"
            )
            user_futures.append(future)

        user_results = await asyncio.gather(*user_futures)
        nyc_user_ids = [uid for result in user_results for uid in result]

        # Step 2: Fetch orders for these users
        order_futures = []
        for user_id in nyc_user_ids:
            shard = self.db.get_shard_for_key(f"order:{user_id}")
            future = shard.query(
                "SELECT * FROM orders WHERE user_id = ?",
                [user_id]
            )
            order_futures.append(future)

        order_results = await asyncio.gather(*order_futures)
        return [order for result in order_results for order in result]

# Resharding (changing shard count)
class ReshardingManager:
    def __init__(self, old_shards, new_shards):
        self.old_shards = old_shards
        self.new_shards = new_shards
        self.old_sharding = ConsistentHashSharding(old_shards)
        self.new_sharding = ConsistentHashSharding(new_shards)

    async def reshard(self):
        """Migrate data to new shard layout"""

        migration_tasks = []

        # For each old shard
        for old_shard in self.old_shards:
            # Scan all data
            cursor = await old_shard.scan()

            async for batch in cursor:
                for row in batch:
                    # Determine new shard
                    new_shard = self.new_sharding.get_shard(row.key)

                    # Only migrate if shard changed
                    if new_shard.id != old_shard.id:
                        task = self.migrate_row(row, old_shard, new_shard)
                        migration_tasks.append(task)

                # Process batch
                if len(migration_tasks) >= 1000:
                    await asyncio.gather(*migration_tasks)
                    migration_tasks = []

        # Final batch
        if migration_tasks:
            await asyncio.gather(*migration_tasks)

    async def migrate_row(self, row, old_shard, new_shard):
        """Migrate single row between shards"""

        # Write to new shard
        await new_shard.write(row.key, row.value)

        # Delete from old shard
        await old_shard.delete(row.key)

        # Log migration
        print(f"Migrated {row.key}: {old_shard.id} → {new_shard.id}")

# Shard-aware caching
class ShardedCache:
    def __init__(self, sharded_db):
        self.db = sharded_db
        self.local_caches = {}  # shard_id -> LRU cache

    async def get(self, key):
        """Get with shard-local caching"""
        shard = self.db.sharding.get_shard(key)

        # Get shard-local cache
        if shard.id not in self.local_caches:
            self.local_caches[shard.id] = LRUCache(capacity=10000)

        cache = self.local_caches[shard.id]

        # Check cache
        if key in cache:
            return cache[key]

        # Fetch from shard
        value = await self.db.read(key)

        # Cache result
        if value is not None:
            cache[key] = value

        return value
```bash
## Advanced Sharding Patterns

```python
# Hot shard detection and splitting
class HotShardManager:
    def __init__(self, monitoring):
        self.monitoring = monitoring
        self.thresholds = {
            'qps': 10000,
            'bandwidth_mbps': 1000,
            'cpu_percent': 80
        }

    async def detect_hot_shards(self):
        """Find overloaded shards"""
        hot_shards = []

        for shard in self.monitoring.get_all_shards():
            metrics = await self.monitoring.get_metrics(shard)

            if (metrics.qps > self.thresholds['qps'] or
                metrics.bandwidth > self.thresholds['bandwidth_mbps'] or
                metrics.cpu > self.thresholds['cpu_percent']):

                hot_shards.append({
                    'shard': shard,
                    'metrics': metrics,
                    'hotness_score': self.calculate_hotness(metrics)
                })

        return sorted(hot_shards, key=lambda x: x['hotness_score'], reverse=True)

    async def split_hot_shard(self, hot_shard):
        """Split hot shard into two"""
        shard = hot_shard['shard']

        # Create two new shards
        new_shard_1 = await self.provision_new_shard()
        new_shard_2 = await self.provision_new_shard()

        # Migrate data based on key distribution
        await self.migrate_by_split(shard, new_shard_1, new_shard_2)

        # Update routing
        await self.update_shard_map(shard, [new_shard_1, new_shard_2])

        # Decommission old shard
        await self.decommission_shard(shard)

# Geo-distributed sharding
class GeoSharding:
    def __init__(self, regions):
        self.regions = regions
        self.geo_router = GeoRouter()

    def get_shard_for_user(self, user):
        """Route based on geography"""

        # Get user location
        location = self.geo_router.get_location(user.ip_address)

        # Find nearest region
        nearest_region = min(
            self.regions,
            key=lambda r: self.calculate_distance(location, r.location)
        )

        # Get shard in that region
        return nearest_region.get_shard(user.id)
```

## ✓ CHOOSE THIS WHEN:
• Data doesn't fit on one machine
• Need horizontal scaling
• Global distribution required
• High availability needed
• Cost-effective scaling

## ⚠️ BEWARE OF:
• Cross-shard queries are expensive
• Transactions across shards
• Hot shard problems
• Resharding complexity
• Shard key changes impossible

## REAL EXAMPLES
• **MongoDB**: Auto-sharding built-in
• **Instagram**: Sharded PostgreSQL by user_id
• **Discord**: Sharded by guild_id

---

**Previous**: [← Service Mesh](service-mesh.md) | **Next**: [Timeout Pattern →](timeout.md)

**Related**: [Consistent Hashing](/patterns/consistent-hashing/) • [Geo Replication](geo-replication.md)
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
class ShardingPattern:
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
pattern = ShardingPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
sharding:
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
def test_sharding_behavior():
    pattern = ShardingPattern(test_config)

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
**Objective**: Identify Sharding (Data Partitioning) in existing systems

**Task**:
Find 2 real-world examples where Sharding (Data Partitioning) is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Sharding (Data Partitioning)

**Scenario**: You need to implement Sharding (Data Partitioning) for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Sharding (Data Partitioning)
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Sharding (Data Partitioning)

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Sharding (Data Partitioning) be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Sharding (Data Partitioning) later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Sharding (Data Partitioning) in your preferred language.
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
- How would you introduce Sharding (Data Partitioning) to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
