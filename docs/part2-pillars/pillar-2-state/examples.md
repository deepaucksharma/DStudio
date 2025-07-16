# State Distribution Examples & Case Studies

!!! info "Prerequisites"
    - [Distribution of State Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← State Distribution Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Pillars Overview](../index.md)

## Real-World State Distribution Failures

<div class="failure-vignette">

### 🎬 Reddit's Sharding Journey

```yaml
Company: Reddit
Timeline: 2010-2015
Challenge: Growing from 1 to 1000× scale

2010: Single PostgreSQL (100GB)
- Problem: CPU maxed, can't scale up more
- Solution: Functional sharding

2011: Functional sharding
- User data: DB1
- Posts: DB2  
- Comments: DB3
- Problem: Joins impossible, queries complex

2012: Horizontal sharding
- Users: Shard by user_id % 16
- Posts: Shard by subreddit
- Problem: Hot subreddits (/r/funny)
- Impact: Some shards at 100%, others at 10%

2013: Virtual shards
- 1000 virtual shards → 16 physical
- Rebalance virtual → physical mapping
- Problem: Operational complexity
- Tooling: Custom shard manager

2015: Cassandra migration
- Eventually consistent
- Geographic distribution
- Trade-off: No transactions
- New problems: Debugging, consistency

Lessons learned:
1. Start with more shards than needed
2. Hot spots are inevitable
3. Cross-shard queries kill performance
4. Virtual sharding provides flexibility
5. NoSQL isn't always simpler
```

</div>

<div class="failure-vignette">

### 🎬 The GitHub Database Outage

```yaml
Company: GitHub
Date: October 21, 2018
Duration: 24 hours 11 minutes

What happened:
- Routine maintenance on East Coast
- 43 seconds of connectivity loss
- MySQL replicas promoted in both DCs
- Split brain: 2 masters!

Timeline:
21:52 - Network partition begins
21:53 - Auto-failover promotes West Coast
21:54 - East Coast comes back
21:55 - Both accepting writes!
22:10 - Split brain detected
22:15 - Site taken offline

The damage:
- East: 3,000 writes
- West: 4,000 writes  
- Conflicts: 1,200 rows

Recovery attempts:
1. Merge data (failed - conflicts)
2. Pick East as winner (data loss)
3. Manual reconciliation

Resolution:
- 24 hours of manual data merging
- Custom scripts for each table
- Some data permanently lost
- Users had to re-submit work

Lessons:
1. Auto-failover can cause split-brain
2. Network partitions happen
3. Conflict resolution needs planning
4. Sometimes manual intervention required
```

</div>

<div class="failure-vignette">

### 🎬 DynamoDB's Hot Partition Problem

```yaml
Company: Major gaming company
Game: Battle royale launch
Date: Launch day 2019

Architecture:
- DynamoDB for player stats
- Partition key: player_id
- Provisioned: 10,000 RCU/WCU

What went wrong:
- Streamer with 5M followers plays
- All viewers check his stats
- One partition gets 90% traffic
- Throttling begins

The cascade:
Minute 1: Streamer goes live
Minute 2: 100K concurrent viewers
Minute 3: Stats page times out
Minute 5: Anger on social media
Minute 10: Whole game seems "broken"

DynamoDB's response:
- Adaptive capacity (10 min delay)
- Still not enough for viral load
- Manual intervention needed

Fix attempts:
1. Increase capacity (didn't help)
2. Add caching (stampede on expire)
3. Create "celebrity cache" table

Final solution:
- Separate table for top 1000 players
- Aggressive caching with jitter
- Read replicas in multiple regions
- Cost increased 10×

Lesson: Design for non-uniform access
```

</div>

## State Distribution Patterns in Practice

### 1. The Saga Pattern Implementation

```python
class OrderSaga:
    """Distributed transaction across services"""
    
    def __init__(self):
        self.steps = []
        self.compensations = []
        
    def execute_order(self, order):
        saga_id = generate_id()
        
        try:
            # Step 1: Reserve inventory
            reservation = self.reserve_inventory(order)
            self.steps.append(('inventory', reservation))
            self.compensations.append(
                lambda: self.cancel_reservation(reservation)
            )
            
            # Step 2: Charge payment
            payment = self.charge_payment(order)
            self.steps.append(('payment', payment))
            self.compensations.append(
                lambda: self.refund_payment(payment)
            )
            
            # Step 3: Create shipment
            shipment = self.create_shipment(order)
            self.steps.append(('shipment', shipment))
            self.compensations.append(
                lambda: self.cancel_shipment(shipment)
            )
            
            # Success - commit saga
            self.commit_saga(saga_id, self.steps)
            return {'success': True, 'order_id': order.id}
            
        except Exception as e:
            # Failure - compensate in reverse order
            self.compensate()
            return {'success': False, 'error': str(e)}
    
    def compensate(self):
        """Undo all completed steps"""
        for compensation in reversed(self.compensations):
            try:
                compensation()
            except Exception as e:
                # Log but continue - compensation must complete
                log_error(f"Compensation failed: {e}")
    
    def reserve_inventory(self, order):
        # Call inventory service
        response = requests.post(
            'http://inventory/reserve',
            json={
                'items': order.items,
                'duration': '15m'  # Timeout for saga
            }
        )
        return response.json()['reservation_id']
    
    def charge_payment(self, order):
        # Call payment service with idempotency key
        response = requests.post(
            'http://payment/charge',
            json={
                'amount': order.total,
                'idempotency_key': f"order-{order.id}"
            }
        )
        return response.json()['transaction_id']
```

### 2. CRDT Shopping Cart

```python
class CRDTShoppingCart:
    """Conflict-free replicated shopping cart"""
    
    def __init__(self, replica_id):
        self.replica_id = replica_id
        self.items = {}  # item_id -> {quantity, version_vector}
        self.version_vector = defaultdict(int)
        
    def add_item(self, item_id, quantity):
        """Add item - always grows"""
        self.version_vector[self.replica_id] += 1
        
        if item_id not in self.items:
            self.items[item_id] = {
                'add_wins': {
                    self.replica_id: {
                        'quantity': quantity,
                        'version': self.version_vector.copy()
                    }
                },
                'remove_wins': {}
            }
        else:
            # Add to existing
            add_wins = self.items[item_id]['add_wins']
            add_wins[self.replica_id] = {
                'quantity': quantity,
                'version': self.version_vector.copy()
            }
    
    def remove_item(self, item_id):
        """Remove item - tombstone approach"""
        self.version_vector[self.replica_id] += 1
        
        if item_id in self.items:
            # Mark all current quantities as removed
            add_wins = self.items[item_id]['add_wins']
            remove_wins = self.items[item_id]['remove_wins']
            
            for replica_id, entry in add_wins.items():
                remove_wins[replica_id] = entry['version']
    
    def merge(self, other_cart):
        """Merge two carts - always converges"""
        # Merge version vectors
        for replica_id in set(self.version_vector) | set(other_cart.version_vector):
            self.version_vector[replica_id] = max(
                self.version_vector[replica_id],
                other_cart.version_vector[replica_id]
            )
        
        # Merge items
        all_items = set(self.items) | set(other_cart.items)
        
        for item_id in all_items:
            self_add = self.items.get(item_id, {'add_wins': {}, 'remove_wins': {}})
            other_add = other_cart.items.get(item_id, {'add_wins': {}, 'remove_wins': {}})
            
            # Merge add_wins - take all unique entries
            merged_adds = self_add['add_wins'].copy()
            merged_adds.update(other_add['add_wins'])
            
            # Merge remove_wins - take all tombstones
            merged_removes = self_add['remove_wins'].copy()
            merged_removes.update(other_add['remove_wins'])
            
            self.items[item_id] = {
                'add_wins': merged_adds,
                'remove_wins': merged_removes
            }
    
    def get_items(self):
        """Get current cart state"""
        result = {}
        
        for item_id, data in self.items.items():
            # Sum quantities that haven't been removed
            total = 0
            for replica_id, entry in data['add_wins'].items():
                removed_version = data['remove_wins'].get(replica_id, {})
                if not self._is_removed(entry['version'], removed_version):
                    total += entry['quantity']
            
            if total > 0:
                result[item_id] = total
                
        return result
    
    def _is_removed(self, add_version, remove_version):
        """Check if add happened before remove"""
        for replica_id, version in add_version.items():
            if version > remove_version.get(replica_id, -1):
                return False
        return bool(remove_version)
```

### 3. Read Replica Lag Monitoring

```python
class ReplicaLagMonitor:
    """Monitor and handle replica lag intelligently"""
    
    def __init__(self, master, replicas):
        self.master = master
        self.replicas = replicas
        self.lag_history = defaultdict(deque)
        self.max_acceptable_lag = timedelta(seconds=5)
        
    def get_replica_for_read(self, consistency_requirement='eventual'):
        """Select replica based on consistency needs"""
        
        if consistency_requirement == 'strong':
            # Always read from master
            return self.master
            
        elif consistency_requirement == 'bounded':
            # Find replica with acceptable lag
            for replica in self.replicas:
                lag = self.measure_lag(replica)
                if lag < self.max_acceptable_lag:
                    return replica
            # Fall back to master if no replica is caught up
            return self.master
            
        else:  # eventual
            # Use least loaded replica
            return min(self.replicas, key=lambda r: r.current_load())
    
    def measure_lag(self, replica):
        """Measure replication lag"""
        # Method 1: Heartbeat table
        master_time = self.master.query(
            "SELECT timestamp FROM heartbeat"
        )[0]['timestamp']
        
        replica_time = replica.query(
            "SELECT timestamp FROM heartbeat"
        )[0]['timestamp']
        
        lag = master_time - replica_time
        
        # Track history
        self.lag_history[replica.id].append({
            'timestamp': datetime.now(),
            'lag': lag
        })
        
        # Keep only last hour
        cutoff = datetime.now() - timedelta(hours=1)
        while (self.lag_history[replica.id] and 
               self.lag_history[replica.id][0]['timestamp'] < cutoff):
            self.lag_history[replica.id].popleft()
        
        return lag
    
    def get_lag_statistics(self, replica_id):
        """Calculate lag statistics"""
        lags = [entry['lag'] for entry in self.lag_history[replica_id]]
        
        if not lags:
            return None
            
        return {
            'current': lags[-1],
            'average': sum(lags, timedelta()) / len(lags),
            'p95': sorted(lags)[int(len(lags) * 0.95)],
            'max': max(lags),
            'trend': 'increasing' if lags[-1] > lags[0] else 'decreasing'
        }
```

### 4. Geo-Distributed State with Conflict Resolution

```python
class GeoDistributedStore:
    """Multi-region eventually consistent store"""
    
    def __init__(self, region, peer_regions):
        self.region = region
        self.peer_regions = peer_regions
        self.local_store = {}
        self.vector_clock = VectorClock()
        self.conflict_resolution = self.last_write_wins
        
    def put(self, key, value, context=None):
        """Write with vector clock"""
        # Increment local clock
        self.vector_clock.increment(self.region)
        
        # Store with metadata
        self.local_store[key] = {
            'value': value,
            'vector_clock': self.vector_clock.copy(),
            'timestamp': time.time(),
            'region': self.region
        }
        
        # Async replicate to peers
        self.replicate_async(key, self.local_store[key])
        
    def get(self, key, consistency='eventual'):
        """Read with consistency level"""
        if consistency == 'strong':
            # Read from quorum of regions
            return self.quorum_read(key)
        elif consistency == 'local':
            # Read only from local
            return self.local_read(key)
        else:
            # Read from local with async repair
            value = self.local_read(key)
            self.read_repair_async(key)
            return value
    
    def handle_replication(self, key, remote_data, from_region):
        """Handle incoming replication"""
        if key not in self.local_store:
            # New key - just store
            self.local_store[key] = remote_data
            return
            
        local_data = self.local_store[key]
        
        # Compare vector clocks
        comparison = self.vector_clock.compare(
            local_data['vector_clock'],
            remote_data['vector_clock']
        )
        
        if comparison == 'concurrent':
            # Conflict! Use resolution strategy
            winner = self.conflict_resolution(local_data, remote_data)
            self.local_store[key] = winner
            
            # Store conflict for analysis
            self.log_conflict(key, local_data, remote_data, winner)
            
        elif comparison == 'remote_newer':
            # Remote is newer
            self.local_store[key] = remote_data
            
        # else local is newer, keep local
    
    def last_write_wins(self, local_data, remote_data):
        """Simple conflict resolution"""
        if local_data['timestamp'] > remote_data['timestamp']:
            return local_data
        return remote_data
    
    def custom_resolution(self, merge_function):
        """Allow custom conflict resolution"""
        self.conflict_resolution = merge_function
```

## Successful State Distribution Implementations

### Netflix's Viewing History

```yaml
Challenge: 200M users × viewing history
Scale: Billions of records, global access

Solution:
1. Time-based sharding
   - Current month: Hot storage
   - Older: Cold storage
   - Archive: Compressed S3

2. Geographic caching
   - Local caches per region
   - Async replication
   - Read from nearest

3. Dual writes
   - Write to current shard
   - Write to user's home region
   - Eventual consistency OK

Results:
- 10ms p99 read latency globally
- 99.99% availability
- 90% reduction in storage costs
```

### Uber's Location Tracking

```yaml
Challenge: Real-time location for millions of drivers

Architecture:
1. H3 geographic indexing
   - Hierarchical hexagonal grid
   - Efficient proximity queries
   - Natural sharding boundary

2. In-memory storage
   - Recent locations in Redis
   - Historical in Cassandra
   - S3 for analytics

3. Write amplification
   - Write to multiple indexes
   - By driver_id
   - By geographic cell
   - By time window

Optimizations:
- Batch writes (1s windows)
- Lossy compression for history
- Adaptive precision by zoom level
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Hot shards are inevitable** - Design for rebalancing
    2. **Split-brain will happen** - Plan conflict resolution
    3. **Replication lag compounds** - Monitor and alert
    4. **Cross-shard queries kill** - Denormalize when needed
    5. **Consistency is expensive** - Choose level wisely

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try State Distribution Exercises](exercises.md) →
    
    **Next Pillar**: [Distribution of Truth](../pillar-3-truth/index.md) →
    
    **Related**: [Failure Modes](../../part1-axioms/axiom-3-failure/index.md)