---
title: Tunable Consistency
description: "Adjust consistency levels dynamically based on application requirements and trade-offs"
type: pattern
difficulty: advanced
reading_time: 25 min
prerequisites: []
pattern_type: "data"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part III: Patterns](index.md) → **Tunable Consistency**

# Tunable Consistency

**One size doesn't fit all**

## THE PROBLEM

```
Different operations need different guarantees:
- Password change → Must be strongly consistent
- Like count → Can be eventually consistent
- View count → Can be very relaxed
- Bank transfer → Requires linearizability

Fixed consistency = Over-engineering or under-delivering
```bash
## THE SOLUTION

```
Let clients choose consistency per operation:

client.read(key, consistency=STRONG)    → Wait for majority
client.read(key, consistency=EVENTUAL)  → Return from any node
client.read(key, consistency=BOUNDED)   → Max staleness 5 sec
```bash
## Consistency Levels

```
STRONGEST ←————————————————————→ WEAKEST
    ↓                                ↓
Linearizable                    Eventual
Sequential                      Read Uncommitted
Snapshot                        Monotonic Read
Read Your Write                 Bounded Staleness
```bash
## IMPLEMENTATION

```python
from enum import Enum
from typing import Optional, Any
import time

class ConsistencyLevel(Enum):
    # Strongest to weakest
    LINEARIZABLE = "linearizable"        # Global order
    SEQUENTIAL = "sequential"            # Per-client order
    SNAPSHOT = "snapshot"                # Point-in-time
    READ_YOUR_WRITE = "read_your_write"  # See own writes
    MONOTONIC_READ = "monotonic_read"    # No going back
    BOUNDED_STALENESS = "bounded"        # Max lag
    EVENTUAL = "eventual"                # Whatever

class TunableDataStore:
    def __init__(self, nodes):
        self.nodes = nodes
        self.vector_clock = VectorClock()
        self.write_timestamp = {}

    async def write(self, key, value, consistency=ConsistencyLevel.SEQUENTIAL):
        """Write with chosen consistency"""

        timestamp = time.time()
        version = self.vector_clock.increment()

        if consistency == ConsistencyLevel.LINEARIZABLE:
            # Wait for all nodes
            await self._write_all_nodes(key, value, version)

        elif consistency == ConsistencyLevel.SEQUENTIAL:
            # Write to majority
            await self._write_quorum(key, value, version)

        elif consistency == ConsistencyLevel.EVENTUAL:
            # Write to any node, return immediately
            await self._write_any_node(key, value, version)
            # Async replication happens in background

        self.write_timestamp[key] = timestamp
        return version

    async def read(self, key, consistency=ConsistencyLevel.SEQUENTIAL):
        """Read with chosen consistency"""

        if consistency == ConsistencyLevel.LINEARIZABLE:
            # Read from majority, return latest
            return await self._read_quorum_latest(key)

        elif consistency == ConsistencyLevel.SEQUENTIAL:
            # Read from majority
            return await self._read_quorum(key)

        elif consistency == ConsistencyLevel.SNAPSHOT:
            # Read from consistent snapshot
            return await self._read_snapshot(key)

        elif consistency == ConsistencyLevel.READ_YOUR_WRITE:
            # Ensure we see our own writes
            return await self._read_after_write(key)

        elif consistency == ConsistencyLevel.MONOTONIC_READ:
            # Never go backwards
            return await self._read_monotonic(key)

        elif consistency == ConsistencyLevel.BOUNDED_STALENESS:
            # Accept stale data within bounds
            return await self._read_bounded(key, max_staleness_ms=5000)

        elif consistency == ConsistencyLevel.EVENTUAL:
            # Read from any node
            return await self._read_any(key)

    async def _write_quorum(self, key, value, version):
        """Write to majority of nodes"""
        quorum_size = len(self.nodes) // 2 + 1
        write_futures = []

        for node in self.nodes[:quorum_size]:
            future = node.write(key, value, version)
            write_futures.append(future)

        # Wait for quorum
        results = await asyncio.gather(*write_futures)

        # Background replication to remaining nodes
        for node in self.nodes[quorum_size:]:
            asyncio.create_task(node.write(key, value, version))

    async def _read_quorum_latest(self, key):
        """Read from majority, return latest version"""
        quorum_size = len(self.nodes) // 2 + 1
        read_futures = []

        for node in self.nodes[:quorum_size]:
            future = node.read(key)
            read_futures.append(future)

        results = await asyncio.gather(*read_futures)

        # Return value with highest version
        latest = max(results, key=lambda r: r.version if r else -1)
        return latest

# Bounded staleness implementation
class BoundedStalenessStore:
    def __init__(self, max_staleness_ms=5000):
        self.max_staleness_ms = max_staleness_ms
        self.primary = None
        self.replicas = []
        self.last_sync_time = {}

    async def read_bounded(self, key):
        """Read with staleness guarantee"""

        # Try to read from replica
        for replica in self.replicas:
            staleness = time.time() * 1000 - self.last_sync_time.get(replica.id, 0)

            if staleness <= self.max_staleness_ms:
                # Replica is fresh enough
                return await replica.read(key)

        # Fallback to primary if replicas too stale
        return await self.primary.read(key)

    async def sync_replicas(self):
        """Keep replicas within staleness bound"""
        while True:
            current_time = time.time() * 1000

            for replica in self.replicas:
                staleness = current_time - self.last_sync_time.get(replica.id, 0)

                if staleness > self.max_staleness_ms * 0.8:  # 80% threshold
                    # Sync before hitting limit
                    await self.sync_replica(replica)
                    self.last_sync_time[replica.id] = current_time

            await asyncio.sleep(1)  # Check every second

# Session consistency implementation
class SessionConsistency:
    def __init__(self, store):
        self.store = store
        self.session_vectors = {}  # session_id -> vector clock

    async def read(self, key, session_id):
        """Read with session consistency"""

        # Get session's last known version
        session_vector = self.session_vectors.get(session_id, VectorClock())

        # Read from any replica that has caught up
        for node in self.store.nodes:
            node_vector = await node.get_vector_clock()

            if node_vector.happens_after(session_vector):
                # This node has all writes from session
                value = await node.read(key)

                # Update session vector
                self.session_vectors[session_id] = node_vector

                return value

        # No node caught up, wait for replication
        await self.wait_for_vector(session_vector)
        return await self.read(key, session_id)

# Consistency level negotiation
class ConsistencyNegotiator:
    def __init__(self):
        self.rules = []

    def add_rule(self, pattern, consistency):
        """Add consistency rule for operations"""
        self.rules.append({
            'pattern': pattern,
            'consistency': consistency
        })

    def negotiate(self, operation):
        """Determine consistency for operation"""

        # Check rules in order
        for rule in self.rules:
            if self.matches(operation, rule['pattern']):
                return rule['consistency']

        # Default consistency
        return ConsistencyLevel.SEQUENTIAL

    def matches(self, operation, pattern):
        """Check if operation matches pattern"""
        if pattern.get('table') and operation.table != pattern['table']:
            return False

        if pattern.get('operation') and operation.type != pattern['operation']:
            return False

        if pattern.get('user_type') and operation.user_type != pattern['user_type']:
            return False

        return True

# Example usage patterns
negotiator = ConsistencyNegotiator()

# Financial operations need strong consistency
negotiator.add_rule(
    {'table': 'accounts', 'operation': 'UPDATE'},
    ConsistencyLevel.LINEARIZABLE
)

# Analytics can use eventual consistency
negotiator.add_rule(
    {'table': 'page_views', 'operation': 'INSERT'},
    ConsistencyLevel.EVENTUAL
)

# User profiles need read-your-write
negotiator.add_rule(
    {'table': 'users', 'operation': 'UPDATE'},
    ConsistencyLevel.READ_YOUR_WRITE
)

# Metrics can tolerate bounded staleness
negotiator.add_rule(
    {'table': 'metrics', 'operation': 'READ'},
    ConsistencyLevel.BOUNDED_STALENESS
)
```bash
## Advanced Patterns

```python
# Dynamic consistency based on load
class AdaptiveConsistency:
    def __init__(self, store):
        self.store = store
        self.load_monitor = LoadMonitor()

    async def read(self, key, preferred_consistency):
        """Adapt consistency based on system load"""

        current_load = self.load_monitor.get_load()

        if current_load > 0.8:  # High load
            # Downgrade consistency for performance
            if preferred_consistency == ConsistencyLevel.LINEARIZABLE:
                actual_consistency = ConsistencyLevel.SEQUENTIAL
            elif preferred_consistency == ConsistencyLevel.SEQUENTIAL:
                actual_consistency = ConsistencyLevel.EVENTUAL
            else:
                actual_consistency = preferred_consistency

            print(f"High load: downgrading from {preferred_consistency} to {actual_consistency}")

        else:  # Normal load
            actual_consistency = preferred_consistency

        return await self.store.read(key, actual_consistency)

# Consistency SLA monitoring
class ConsistencySLAMonitor:
    def __init__(self):
        self.consistency_met = Counter()
        self.consistency_violated = Counter()
        self.staleness_histogram = Histogram()

    def record_read(self, requested_consistency, actual_staleness_ms):
        """Track if consistency SLA was met"""

        if requested_consistency == ConsistencyLevel.BOUNDED_STALENESS:
            if actual_staleness_ms <= 5000:  # 5 second bound
                self.consistency_met.inc()
            else:
                self.consistency_violated.inc()
                self.alert(f"Staleness SLA violated: {actual_staleness_ms}ms")

        self.staleness_histogram.observe(actual_staleness_ms)
```

## ✓ CHOOSE THIS WHEN:
• Different data has different needs
• Trading consistency for performance
• Global distribution required
• Multi-tenant systems
• Mixed workload patterns

## ⚠️ BEWARE OF:
• Complexity of consistency models
• Debugging consistency issues
• Client must understand trade-offs
• Testing all consistency levels
• Monitoring consistency SLAs

## REAL EXAMPLES
• **Azure Cosmos DB**: 5 consistency levels
• **Amazon DynamoDB**: Eventual & strong
• **Google Spanner**: External consistency option

---

**Previous**: [← Timeout Pattern](timeout.md)
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
class Tunable_ConsistencyPattern:
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
pattern = Tunable_ConsistencyPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
tunable_consistency:
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
def test_tunable_consistency_behavior():
    pattern = Tunable_ConsistencyPattern(test_config)

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
**Objective**: Identify Tunable Consistency in existing systems

**Task**:
Find 2 real-world examples where Tunable Consistency is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes
**Objective**: Design an implementation of Tunable Consistency

**Scenario**: You need to implement Tunable Consistency for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Tunable Consistency
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes
**Objective**: Evaluate when NOT to use Tunable Consistency

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Tunable Consistency be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Tunable Consistency later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Tunable Consistency in your preferred language.
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
- How would you introduce Tunable Consistency to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
