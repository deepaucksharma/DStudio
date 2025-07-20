---
title: Geo-Replication Patterns
description: Physics wins every time
```text
type: pattern
difficulty: advanced
reading_time: 10 min
prerequisites: []
pattern_type: "general"
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part III: Patterns](/patterns/) → **Geo-Replication Patterns**


# Geo-Replication Patterns

**Data everywhere, consistency nowhere (kidding!)**

## THE PROBLEM

```
Global users, single datacenter:
- US → EU datacenter = 150ms latency
- EU datacenter fails = US users down too
- Regulations require data sovereignty
- Users want fast access everywhere

Physics wins every time
```bash
## THE SOLUTION

```
Replicate data globally:

    US-East          EU-West         AP-South
       ↓                ↓               ↓
   [Primary]  ←→  [Replica]  ←→  [Replica]
       ↓                ↓               ↓
   US Users        EU Users       Asia Users
   
Local reads = Fast
Global consistency = Tricky
```bash
## Replication Strategies

```
1. MASTER-SLAVE (Single Writer)
   One region writes, others read
   
2. MULTI-MASTER (Active-Active)
   All regions can write
   
3. CONSENSUS-BASED
   Majority agreement (Raft/Paxos)
   
4. CRDT-BASED
   Conflict-free replicated data types
```bash
## IMPLEMENTATION

```python
from enum import Enum
from typing import Dict, List, Optional, Any
import asyncio
import time

class ReplicationMode(Enum):
    ASYNC = "async"
    SYNC = "sync"
    SEMI_SYNC = "semi_sync"

class GeoRegion:
    def __init__(self, name: str, endpoint: str, is_primary: bool = False):
        self.name = name
        self.endpoint = endpoint
        self.is_primary = is_primary
        self.latency_map = {}  # Latency to other regions
        
class GeoReplicatedStore:
    def __init__(self, regions: List[GeoRegion], mode: ReplicationMode):
        self.regions = regions
        self.mode = mode
        self.primary = next(r for r in regions if r.is_primary)
        self.replicas = [r for r in regions if not r.is_primary]
        
    async def write(self, key: str, value: Any, options: dict = None):
        """Write with geo-replication"""
        
        # Always write to primary first
        await self._write_to_region(self.primary, key, value)
        
        if self.mode == ReplicationMode.SYNC:
            # Wait for all replicas
            await self._replicate_sync(key, value)
            
        elif self.mode == ReplicationMode.SEMI_SYNC:
            # Wait for at least one replica
            await self._replicate_semi_sync(key, value)
            
        elif self.mode == ReplicationMode.ASYNC:
            # Fire and forget
            asyncio.create_task(self._replicate_async(key, value))
            
        return True
    
    async def read(self, key: str, consistency: str = "eventual"):
        """Read with consistency options"""
        
        if consistency == "strong":
            # Read from primary
            return await self._read_from_region(self.primary, key)
            
        elif consistency == "bounded":
            # Read from replica if fresh enough
            return await self._read_bounded_staleness(key, max_staleness_ms=5000)
            
        elif consistency == "local":
            # Read from nearest region
            nearest = self._find_nearest_region()
            return await self._read_from_region(nearest, key)
            
        else:  # eventual
            # Read from any available replica
            return await self._read_any_replica(key)
    
    async def _replicate_sync(self, key: str, value: Any):
        """Synchronous replication to all replicas"""
        
        tasks = []
        for replica in self.replicas:
            task = self._write_to_region(replica, key, value)
            tasks.append(task)
            
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for failures
        failures = [r for r in results if isinstance(r, Exception)]
        if failures:
            raise ReplicationError(f"Failed to replicate to {len(failures)} regions")
    
    async def _replicate_semi_sync(self, key: str, value: Any):
        """Semi-synchronous: wait for at least one replica"""
        
        tasks = []
        for replica in self.replicas:
            task = self._write_to_region(replica, key, value)
            tasks.append(task)
            
        # Wait for first successful write
        done, pending = await asyncio.wait(
            tasks, 
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
            
        # Check if we got at least one success
        success = any(not task.exception() for task in done)
        if not success:
            raise ReplicationError("No replica acknowledged write")

# Multi-master replication with conflict resolution
class MultiMasterReplication:
    def __init__(self, regions: List[GeoRegion]):
        self.regions = {r.name: r for r in regions}
        self.vector_clocks = {}  # Track causality
        self.conflict_resolver = ConflictResolver()
        
    async def write(self, region: str, key: str, value: Any):
        """Write to any region"""
        
        # Get current vector clock
        clock = self.vector_clocks.get(key, VectorClock())
        
        # Increment clock for this region
        clock.increment(region)
        
        # Create versioned value
        versioned_value = VersionedValue(
            value=value,
            vector_clock=clock.copy(),
            region=region,
            timestamp=time.time()
        )
        
        # Write locally
        await self._write_local(region, key, versioned_value)
        
        # Replicate to other regions
        asyncio.create_task(
            self._replicate_to_others(region, key, versioned_value)
        )
        
        # Update vector clock
        self.vector_clocks[key] = clock
        
    async def read(self, region: str, key: str):
        """Read from any region with conflict resolution"""
        
        # Read all versions from all regions
        versions = await self._read_all_versions(key)
        
        if not versions:
            return None
            
        # Detect conflicts
        conflicts = self._detect_conflicts(versions)
        
        if conflicts:
            # Resolve conflicts
            resolved = await self.conflict_resolver.resolve(conflicts)
            
            # Write resolved value back
            await self._write_resolved(key, resolved)
            
            return resolved.value
        else:
            # No conflicts, return latest
            return max(versions, key=lambda v: v.timestamp).value
    
    def _detect_conflicts(self, versions: List[VersionedValue]):
        """Detect concurrent writes"""
        
        conflicts = []
        
        for i, v1 in enumerate(versions):
            for v2 in versions[i+1:]:
                if v1.vector_clock.concurrent_with(v2.vector_clock):
                    conflicts.append((v1, v2))
                    
        return conflicts

# Conflict-free replicated data types (CRDTs)
class CRDTCounter:
    """Grow-only counter CRDT"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts = {node_id: 0}
        
    def increment(self, amount: int = 1):
        """Local increment"""
        self.counts[self.node_id] += amount
        
    def merge(self, other: 'CRDTCounter'):
        """Merge with another counter"""
        for node_id, count in other.counts.items():
            self.counts[node_id] = max(
                self.counts.get(node_id, 0),
                count
            )
            
    def value(self) -> int:
        """Get total count"""
        return sum(self.counts.values())

class CRDTSet:
    """Observed-Remove Set CRDT"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.adds = {}  # element -> (node_id, timestamp)
        self.removes = {}  # element -> (node_id, timestamp)
        
    def add(self, element: Any):
        """Add element to set"""
        timestamp = time.time()
        self.adds[element] = (self.node_id, timestamp)
        
    def remove(self, element: Any):
        """Remove element from set"""
        if element in self.adds:
            timestamp = time.time()
            self.removes[element] = (self.node_id, timestamp)
            
    def merge(self, other: 'CRDTSet'):
        """Merge with another set"""
        
        # Merge adds
        for elem, (node, ts) in other.adds.items():
            if elem not in self.adds or ts > self.adds[elem][1]:
                self.adds[elem] = (node, ts)
                
        # Merge removes
        for elem, (node, ts) in other.removes.items():
            if elem not in self.removes or ts > self.removes[elem][1]:
                self.removes[elem] = (node, ts)
                
    def value(self) -> set:
        """Get current set"""
        result = set()
        
        for elem in self.adds:
            add_ts = self.adds[elem][1]
            remove_ts = self.removes.get(elem, (None, 0))[1]
            
            if add_ts > remove_ts:
                result.add(elem)
                
        return result

# Geo-aware query routing
class GeoRouter:
    def __init__(self, regions: Dict[str, GeoRegion]):
        self.regions = regions
        self.latency_cache = {}
        
    async def route_query(self, query: Query, client_location: str):
        """Route query to optimal region"""
        
        if query.requires_strong_consistency:
            # Must go to primary
            return self._find_primary()
            
        elif query.is_write:
            # Route writes based on strategy
            if query.conflict_free:
                # Can write to nearest
                return await self._find_nearest(client_location)
            else:
                # Must go to primary
                return self._find_primary()
                
        else:  # Read query
            # Find best replica based on:
            # 1. Data freshness requirements
            # 2. Network latency
            # 3. Region load
            
            candidates = []
            
            for region in self.regions.values():
                score = await self._calculate_region_score(
                    region, 
                    client_location,
                    query.max_staleness
                )
                candidates.append((region, score))
                
            # Return best scoring region
            return max(candidates, key=lambda x: x[1])[0]
    
    async def _calculate_region_score(self, region, client_location, max_staleness):
        """Score region for query routing"""
        
        # Get network latency
        latency = await self._measure_latency(client_location, region.name)
        
        # Get replication lag
        lag = await region.get_replication_lag()
        
        # Check if meets staleness requirements
        if lag > max_staleness:
            return -1  # Disqualified
            
        # Calculate score (lower latency = higher score)
        score = 1000 / (latency + 1)
        
        # Bonus for local region
        if region.name == client_location:
            score *= 2
            
        # Penalty for high load
        load = await region.get_load()
        score *= (1 - load)
        
        return score

# Cross-region consistency monitoring
class ConsistencyMonitor:
    def __init__(self, regions: List[GeoRegion]):
        self.regions = regions
        self.lag_metrics = defaultdict(list)
        
    async def monitor_replication_lag(self):
        """Monitor lag between regions"""
        
        while True:
            primary = self._find_primary()
            
            for replica in self.regions:
                if replica.is_primary:
                    continue
                    
                # Measure replication lag
                lag = await self._measure_lag(primary, replica)
                
                self.lag_metrics[replica.name].append({
                    'timestamp': time.time(),
                    'lag_ms': lag
                })
                
                # Alert if lag is too high
                if lag > 10000:  # 10 seconds
                    await self.alert(
                        f"High replication lag: {replica.name} is {lag}ms behind"
                    )
                    
            await asyncio.sleep(10)  # Check every 10 seconds
```bash
## Advanced Patterns

```python
# Geo-partitioned data
class GeoPartitionedStore:
    """Partition data by geography"""
    
    def __init__(self):
        self.partitions = {
            'us': USDataStore(),
            'eu': EUDataStore(),
            'asia': AsiaDataStore()
        }
        self.partition_strategy = GeographicPartitioner()
        
    async def write(self, key: str, value: Any, user_location: str):
        """Write to geographically appropriate partition"""
        
        # Determine home partition
        partition = self.partition_strategy.get_partition(key, user_location)
        
        # Write to home partition
        await self.partitions[partition].write(key, value)
        
        # Optionally replicate to other partitions
        if self._requires_global_access(key):
            await self._replicate_globally(key, value, partition)

# Geo-fencing for data sovereignty
class GeoFencedStore:
    """Ensure data stays in specific regions"""
    
    def __init__(self):
        self.geo_policies = {
            'gdpr': ['eu-west', 'eu-central'],
            'china': ['cn-north', 'cn-south'],
            'russia': ['ru-central']
        }
        
    async def write(self, key: str, value: Any, data_policy: str):
        """Write respecting geo-fencing policies"""
        
        allowed_regions = self.geo_policies.get(data_policy, [])
        
        if not allowed_regions:
            # No restrictions, replicate globally
            await self._replicate_all(key, value)
        else:
            # Only replicate to allowed regions
            await self._replicate_to_regions(key, value, allowed_regions)
```

## ✓ CHOOSE THIS WHEN:
• Global user base
• Low latency requirements
• Disaster recovery needed
• Data sovereignty requirements
• Read-heavy workloads

## ⚠️ BEWARE OF:
• Consistency complexities
• Network partition handling
• Conflict resolution overhead
• Increased operational complexity
• Cross-region bandwidth costs

## REAL EXAMPLES
• **Google Spanner**: Global consistency
• **Amazon DynamoDB Global Tables**: Multi-region
• **CockroachDB**: Geo-partitioned SQL

---

**Previous**: [← FinOps Patterns](finops.md) | **Next**: [Graceful Degradation Pattern →](graceful-degradation.md)
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
class Geo_ReplicationPattern:
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
pattern = Geo_ReplicationPattern(config)
result = pattern.process(user_request)
```

### Configuration Example

```yaml
geo_replication:
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
def test_geo_replication_behavior():
    pattern = Geo_ReplicationPattern(test_config)
    
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
**Objective**: Identify Geo-Replication s in existing systems

**Task**: 
Find 2 real-world examples where Geo-Replication s is implemented:
1. **Example 1**: A well-known tech company or service
2. **Example 2**: An open-source project or tool you've used

For each example:
- Describe how the pattern is implemented
- What problems it solves in that context
- What alternatives could have been used

### Exercise 2: Implementation Planning ⭐⭐⭐
**Time**: ~25 minutes  
**Objective**: Design an implementation of Geo-Replication s

**Scenario**: You need to implement Geo-Replication s for an e-commerce checkout system processing 10,000 orders/hour.

**Requirements**:
- 99.9% availability required
- Payment processing must be reliable
- Orders must not be lost or duplicated

**Your Task**:
1. Design the architecture using Geo-Replication s
2. Identify key components and their responsibilities
3. Define interfaces between components
4. Consider failure scenarios and mitigation strategies

**Deliverable**: Architecture diagram + 1-page implementation plan

### Exercise 3: Trade-off Analysis ⭐⭐⭐⭐
**Time**: ~20 minutes  
**Objective**: Evaluate when NOT to use Geo-Replication s

**Challenge**: You're consulting for a startup building their first product.

**Analysis Required**:
1. **Context Assessment**: Under what conditions would Geo-Replication s be overkill?
2. **Cost-Benefit**: Compare implementation costs vs. benefits
3. **Alternatives**: What simpler approaches could work initially?
4. **Evolution Path**: How would you migrate to Geo-Replication s later?

**Anti-Pattern Warning**: Identify one common mistake teams make when implementing this pattern.

---

## 🛠️ Code Challenge

### Beginner: Basic Implementation
Implement a minimal version of Geo-Replication s in your preferred language.
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
- How would you introduce Geo-Replication s to an existing system?
- What migration strategy would minimize risk?
- How would you measure success?

**Team Discussion Points**:
1. When team members suggest this pattern, what questions should you ask?
2. How would you explain the value to non-technical stakeholders?
3. What monitoring would indicate the pattern is working well?

---
