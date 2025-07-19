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
```

## THE SOLUTION

```
Let clients choose consistency per operation:

client.read(key, consistency=STRONG)    → Wait for majority
client.read(key, consistency=EVENTUAL)  → Return from any node
client.read(key, consistency=BOUNDED)   → Max staleness 5 sec
```

## Consistency Levels

```
STRONGEST ←————————————————————→ WEAKEST
    ↓                                ↓
Linearizable                    Eventual
Sequential                      Read Uncommitted  
Snapshot                        Monotonic Read
Read Your Write                 Bounded Staleness
```

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
```

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