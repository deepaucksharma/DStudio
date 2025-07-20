# Distributed Lock Pattern

**Mutual exclusion across distributed nodes**

> *"In a distributed system, acquiring a lock is easy—it's the releasing that's hard."*

<div class="pattern-context">
<h3>🧭 Pattern Context</h3>

**🔬 Primary Axioms Addressed**:
- [Axiom 4: Concurrency](/part1-axioms/axiom4-concurrency/) - Coordinating concurrent access
- [Axiom 5: Coordination](/part1-axioms/axiom5-coordination/) - Distributed agreement

**🔧 Solves These Problems**:
- Race conditions in distributed systems
- Resource contention across nodes
- Distributed critical sections
- Preventing duplicate work

**🤝 Works Best With**:
- [Leader Election](/patterns/leader-election/) - Locks for coordination
- [Timeout Pattern](/patterns/timeout/) - Preventing deadlocks
- [Fencing Tokens](/patterns/fencing/) - Preventing split-brain
</div>

---

## 🎯 Level 1: Intuition

### The Bathroom Stall Analogy

A distributed lock is like a public bathroom stall:
- **Lock acquisition**: Check if door is locked, if not, lock it
- **Lock holding**: Use the facility while others wait
- **Lock release**: Unlock when done
- **Lock timeout**: Janitor has master key for emergencies

The challenge: What if someone passes out inside? (node failure while holding lock)

### Basic Distributed Lock

```python
import redis
import time
import uuid

class SimpleDistributedLock:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def acquire(self, resource: str, timeout_ms: int = 5000) -> Optional[str]:
        """Try to acquire lock"""
        lock_id = str(uuid.uuid4())
        
        # SET NX EX - atomic set if not exists with expiry
        acquired = self.redis.set(
            f"lock:{resource}",
            lock_id,
            nx=True,  # Only set if not exists
            px=timeout_ms  # Expire after milliseconds
        )
        
        return lock_id if acquired else None
    
    def release(self, resource: str, lock_id: str) -> bool:
        """Release lock if we own it"""
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = self.redis.eval(
            lua_script,
            1,
            f"lock:{resource}",
            lock_id
        )
        
        return bool(result)
```

---

## 🏗️ Level 2: Foundation

### Distributed Lock Properties

| Property | Description | Why It Matters |
|----------|-------------|----------------|
| **Mutual Exclusion** | Only one holder at a time | Core requirement |
| **Deadlock Free** | Locks eventually expire | Prevents system freeze |
| **Fault Tolerant** | Survives node failures | Distributed reliability |
| **Non-Byzantine** | Assumes non-malicious nodes | Simplifies design |

### Lock Implementation Strategies

#### 1. Database-Based Locks
```sql
-- Acquire lock
INSERT INTO distributed_locks 
    (resource_name, lock_holder, acquired_at, expires_at)
VALUES 
    ('inventory-update', 'node-123', NOW(), NOW() + INTERVAL '30 seconds')
ON CONFLICT (resource_name) DO NOTHING
RETURNING lock_id;

-- Release lock
DELETE FROM distributed_locks 
WHERE resource_name = 'inventory-update' 
  AND lock_holder = 'node-123';
```

#### 2. ZooKeeper-Based Locks
```python
from kazoo.client import KazooClient
from kazoo.recipe.lock import Lock

class ZooKeeperLock:
    def __init__(self, zk_hosts: str):
        self.zk = KazooClient(hosts=zk_hosts)
        self.zk.start()
    
    def with_lock(self, path: str, func, *args, **kwargs):
        """Execute function with distributed lock"""
        lock = Lock(self.zk, f"/locks/{path}")
        
        with lock:
            # Lock acquired
            return func(*args, **kwargs)
        # Lock automatically released
```

#### 3. Consensus-Based Locks
```python
class ConsensusLock:
    """Lock using consensus algorithm like Raft"""
    
    def __init__(self, nodes: List[str]):
        self.nodes = nodes
        self.lock_state = {}
    
    def acquire(self, resource: str, node_id: str) -> bool:
        # Propose lock acquisition to cluster
        proposal = {
            'type': 'acquire_lock',
            'resource': resource,
            'holder': node_id,
            'timestamp': time.time()
        }
        
        # Get consensus on proposal
        if self.propose_to_cluster(proposal):
            self.lock_state[resource] = node_id
            return True
        
        return False
```

### Lock Safety Properties

```python
class SafeDistributedLock:
    """Lock with safety guarantees"""
    
    def __init__(self, storage_backend):
        self.storage = storage_backend
        self.clock = LogicalClock()
    
    def acquire_with_fencing(self, resource: str) -> Optional[dict]:
        """Acquire lock with fencing token"""
        token = self.clock.increment()
        lock_info = {
            'holder': self.node_id,
            'token': token,
            'acquired_at': time.time(),
            'ttl': 30  # seconds
        }
        
        # Store with compare-and-swap
        if self.storage.compare_and_set(
            f"lock:{resource}",
            expected=None,
            new_value=lock_info
        ):
            return lock_info
        
        return None
    
    def validate_lock(self, resource: str, lock_info: dict) -> bool:
        """Check if lock is still valid"""
        current = self.storage.get(f"lock:{resource}")
        
        if not current:
            return False
        
        # Check token hasn't been superseded
        if current['token'] > lock_info['token']:
            return False
        
        # Check TTL hasn't expired
        elapsed = time.time() - current['acquired_at']
        if elapsed > current['ttl']:
            return False
        
        return current['holder'] == lock_info['holder']
```

---

## 🔧 Level 3: Deep Dive

### The Redlock Algorithm

Martin Kleppmann's analysis of Redis Redlock revealed important limitations:

```python
class Redlock:
    """
    Redis Redlock implementation
    Note: Has known safety issues in distributed systems!
    """
    
    def __init__(self, redis_nodes: List[Redis]):
        self.nodes = redis_nodes
        self.quorum = len(redis_nodes) // 2 + 1
        self.lock_ttl = 30000  # 30 seconds
        self.clock_drift = 0.01  # 1% clock drift
    
    def acquire(self, resource: str) -> Optional[str]:
        lock_id = str(uuid.uuid4())
        start_time = time.time() * 1000  # milliseconds
        
        # Try to acquire lock on majority of nodes
        locked_nodes = 0
        
        for node in self.nodes:
            try:
                if self._acquire_on_node(node, resource, lock_id):
                    locked_nodes += 1
            except:
                # Node failure, continue
                pass
        
        # Calculate validity time
        elapsed = (time.time() * 1000) - start_time
        validity_time = self.lock_ttl - elapsed - (self.lock_ttl * self.clock_drift)
        
        # Check if we have quorum and time remaining
        if locked_nodes >= self.quorum and validity_time > 0:
            return lock_id
        
        # Failed to acquire, release any partial locks
        self._release_all(resource, lock_id)
        return None
    
    def _acquire_on_node(self, node: Redis, resource: str, lock_id: str) -> bool:
        return node.set(
            f"lock:{resource}",
            lock_id,
            nx=True,
            px=self.lock_ttl
        )
```

### Problems with Distributed Locks

<div class="antipatterns">
<h3>⚠️ Common Distributed Lock Issues</h3>

1. **Clock Skew**
   ```python
   # BAD: Relies on synchronized clocks
   if current_time() > lock.expires_at:
       # Lock expired? Or is our clock wrong?
   
   # GOOD: Use monotonic clock or fence tokens
   if lock.fence_token < current_max_token:
       # Lock has been superseded
   ```

2. **Network Delays**
   ```python
   # BAD: Assumes instant network
   lock = acquire_lock()
   # Network delay here!
   do_work()  # Lock might have expired
   
   # GOOD: Check lock validity before critical operations
   lock = acquire_lock()
   if validate_lock(lock):
       do_work()
   ```

3. **Process Pauses**
   ```python
   # BAD: GC pause can break assumptions
   lock = acquire_lock()
   # GC pause for 30 seconds!
   # Lock expired during pause
   update_database()  # Unsafe!
   
   # GOOD: Use fencing tokens
   lock = acquire_lock_with_fence()
   database.update_if_fence_valid(data, lock.fence_token)
   ```
</div>

### Fencing Tokens for Safety

```python
class FencedLock:
    """Lock with monotonically increasing fence tokens"""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.token_counter = 0
    
    def acquire(self, resource: str) -> Optional[FencedLockHandle]:
        # Get next token from coordinator
        token = self.coordinator.get_next_token()
        
        # Try to acquire lock with token
        lock_data = {
            'holder': self.node_id,
            'token': token,
            'resource': resource,
            'acquired_at': time.time()
        }
        
        if self.coordinator.try_acquire(resource, lock_data):
            return FencedLockHandle(resource, token, self)
        
        return None

class FencedLockHandle:
    """Handle for a fenced lock"""
    
    def __init__(self, resource: str, token: int, lock_manager):
        self.resource = resource
        self.token = token
        self.lock_manager = lock_manager
    
    def execute_with_fence(self, storage, operation):
        """Execute operation only if fence token is valid"""
        # Storage checks fence token before applying operation
        return storage.conditional_execute(
            operation,
            fence_token=self.token
        )
```

---

## 🚀 Level 4: Expert

### Production Distributed Lock Systems

#### Google's Chubby Lock Service
```python
class ChubbyLockService:
    """
    Simplified version of Google's Chubby
    """
    
    def __init__(self):
        self.paxos_group = PaxosGroup()
        self.lock_table = {}
        self.sessions = {}
        
    def create_session(self, client_id: str) -> str:
        """Create client session with keepalive"""
        session_id = uuid.uuid4().hex
        
        self.sessions[session_id] = {
            'client_id': client_id,
            'last_keepalive': time.time(),
            'locks_held': set()
        }
        
        return session_id
    
    def acquire_lock(self, session_id: str, lock_path: str, mode: str = 'exclusive'):
        """Acquire lock with session"""
        if session_id not in self.sessions:
            raise InvalidSessionError()
        
        # Propose lock acquisition through Paxos
        proposal = {
            'operation': 'acquire_lock',
            'session_id': session_id,
            'lock_path': lock_path,
            'mode': mode,
            'timestamp': time.time()
        }
        
        if self.paxos_group.propose(proposal):
            self.lock_table[lock_path] = {
                'holder': session_id,
                'mode': mode,
                'acquired_at': time.time()
            }
            self.sessions[session_id]['locks_held'].add(lock_path)
            return True
        
        return False
    
    def handle_session_timeout(self, session_id: str):
        """Release all locks held by timed-out session"""
        if session_id in self.sessions:
            locks_to_release = self.sessions[session_id]['locks_held'].copy()
            
            for lock_path in locks_to_release:
                self.release_lock_internal(session_id, lock_path)
            
            del self.sessions[session_id]
```

#### etcd Distributed Locks
```python
import etcd3

class EtcdDistributedLock:
    """Production-ready lock using etcd"""
    
    def __init__(self, etcd_host='localhost', etcd_port=2379):
        self.etcd = etcd3.client(host=etcd_host, port=etcd_port)
    
    def acquire_lock(self, name: str, ttl: int = 60) -> etcd3.Lock:
        """Acquire distributed lock with TTL"""
        # etcd uses leases for TTL
        lease = self.etcd.lease(ttl)
        
        # Create lock associated with lease
        lock = self.etcd.lock(name, lease=lease)
        
        # Acquire lock (blocks until available)
        lock.acquire()
        
        return lock
    
    def with_lock(self, name: str, func, *args, **kwargs):
        """Context manager for lock"""
        lock = self.acquire_lock(name)
        try:
            return func(*args, **kwargs)
        finally:
            lock.release()
    
    def try_acquire_with_timeout(self, name: str, timeout: float) -> Optional[etcd3.Lock]:
        """Try to acquire lock with timeout"""
        lock = self.etcd.lock(name)
        
        acquired = lock.acquire(timeout=timeout)
        
        if acquired:
            return lock
        return None
```

### Real-World Case Study: Uber's Distributed Lock

```python
class UberDistributedLockManager:
    """
    Uber's approach to distributed locking at scale
    """
    
    def __init__(self):
        self.local_cache = {}  # Fast path for read locks
        self.lock_service = RemoteLockService()
        self.metrics = LockMetrics()
        
    def acquire_read_lock(self, resource: str) -> Optional[ReadLock]:
        """Optimized read lock acquisition"""
        # Check local cache first
        if self.is_cached_valid(resource):
            self.metrics.cache_hit()
            return ReadLock(resource, cached=True)
        
        # Fall back to distributed lock
        self.metrics.cache_miss()
        
        lock = self.lock_service.acquire_read(resource)
        if lock:
            self.update_cache(resource, lock)
        
        return lock
    
    def acquire_write_lock(self, resource: str, priority: int = 0) -> Optional[WriteLock]:
        """Write lock with priority queuing"""
        # Invalidate cache
        self.invalidate_cache(resource)
        
        # Use priority queue for fairness
        request = LockRequest(
            resource=resource,
            mode='write',
            priority=priority,
            timestamp=time.time()
        )
        
        return self.lock_service.acquire_with_queue(request)
    
    def monitor_lock_health(self):
        """Track lock system health"""
        return {
            'acquisition_latency_p99': self.metrics.get_latency_p99(),
            'lock_contention_rate': self.metrics.get_contention_rate(),
            'timeout_rate': self.metrics.get_timeout_rate(),
            'deadlock_detected': self.detect_deadlocks()
        }
```

---

## 🎯 Level 5: Mastery

### Theoretical Foundations

#### The FLP Impossibility Result
```python
class FLPImpossibility:
    """
    Fischer-Lynch-Paterson impossibility result:
    No consensus algorithm can guarantee both safety and liveness
    in an asynchronous system with one faulty process
    """
    
    def demonstrate_impossibility(self):
        """
        Show why perfect distributed locks are impossible
        """
        scenarios = []
        
        # Scenario 1: Network delay indistinguishable from failure
        scenarios.append({
            'situation': 'Node holding lock is slow',
            'observer_view': 'Node appears failed',
            'dilemma': 'Revoke lock (unsafe) or wait forever (no progress)?'
        })
        
        # Scenario 2: Clock skew
        scenarios.append({
            'situation': 'Lock expires by wall clock',
            'observer_view': 'Different nodes see different times',
            'dilemma': 'Who decides when lock truly expired?'
        })
        
        return scenarios
```

#### Optimal Lock Algorithms
```python
class OptimalDistributedLock:
    """
    Theoretically optimal distributed lock based on:
    - Lamport's happens-before relation
    - Vector clocks for causality
    - Quorum systems for fault tolerance
    """
    
    def __init__(self, nodes: int):
        self.nodes = nodes
        self.vector_clock = VectorClock(nodes)
        self.quorum_size = (nodes // 2) + 1
        
    def acquire_optimal(self, resource: str) -> OptimalLockHandle:
        # Step 1: Increment local vector clock
        my_timestamp = self.vector_clock.increment(self.node_id)
        
        # Step 2: Send request to all nodes
        request = LockRequest(
            resource=resource,
            requester=self.node_id,
            timestamp=my_timestamp,
            request_id=uuid.uuid4()
        )
        
        # Step 3: Collect acknowledgments
        acks = self.broadcast_request(request)
        
        # Step 4: Check if we have quorum
        if len(acks) >= self.quorum_size:
            # Step 5: Verify causality
            if self.verify_causality(acks, my_timestamp):
                return OptimalLockHandle(
                    resource=resource,
                    timestamp=my_timestamp,
                    quorum=acks
                )
        
        return None
    
    def verify_causality(self, acks, my_timestamp):
        """Ensure no concurrent conflicting operations"""
        for ack in acks:
            if self.vector_clock.concurrent(ack.timestamp, my_timestamp):
                # Concurrent operation detected
                return False
        return True
```

### Future Directions

1. **Blockchain-Based Locks**: Using smart contracts for distributed locks
2. **ML-Optimized Locks**: Predicting contention and pre-acquiring locks
3. **Quantum Distributed Locks**: Leveraging quantum entanglement
4. **Conflict-Free Locks**: CRDT-based locking mechanisms

---

## 📋 Quick Reference

### Lock Selection Guide

| Use Case | Recommended Solution | Why |
|----------|---------------------|-----|
| Leader election | etcd/ZooKeeper | Built-in lease support |
| Resource pooling | Database locks | Simple, ACID guarantees |
| Distributed cron | Redis with Redlock | Good enough for most cases |
| Critical sections | Chubby/etcd | Strong consistency |
| Cache invalidation | Eventually consistent | Locks often overkill |

### Implementation Checklist

- [ ] Define lock granularity (resource level)
- [ ] Set appropriate timeouts
- [ ] Implement lock renewal for long operations
- [ ] Add monitoring and metrics
- [ ] Handle lock release on process crash
- [ ] Test with network partitions
- [ ] Document lock hierarchy to prevent deadlocks
- [ ] Implement deadlock detection

---

---

*"A distributed lock is a promise that's hard to keep and harder to break safely."*