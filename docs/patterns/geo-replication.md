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
```

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
```

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
```

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
```

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