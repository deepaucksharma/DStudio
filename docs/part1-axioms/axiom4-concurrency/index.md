# Axiom 4: Concurrency

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Concurrent operations create states that don't exist in sequential execution.
  </div>
</div>

---

## Level 1: Intuition (Start Here) 🌱

### The Restaurant Kitchen Chaos

Imagine a busy restaurant kitchen with multiple chefs:
- Chef A starts making pasta
- Chef B starts making sauce  
- Chef C needs the same pan

**Sequential kitchen**: One chef at a time = Slow but predictable  
**Concurrent kitchen**: All chefs at once = Fast but chaotic!

What can go wrong?
- Two chefs grab the last tomato
- Someone adds salt twice
- Orders get mixed up
- The pan gets used for two different dishes

That's concurrency in distributed systems!

### Your First Race Condition

```python
# race_condition_demo.py - See concurrency bugs in action!

import threading
import time

# Shared bank account
balance = 1000

def withdraw(amount, person):
    """Withdraw money (badly!)"""
    global balance
    
    print(f"{person} checks balance: ${balance}")
    
    if balance >= amount:
        print(f"{person} sees enough money, proceeding...")
        time.sleep(0.1)  # Simulate processing time
        balance -= amount
        print(f"{person} withdrew ${amount}, balance now: ${balance}")
    else:
        print(f"{person} insufficient funds!")

# Both people try to withdraw $800 at the same time
thread1 = threading.Thread(target=withdraw, args=(800, "Alice"))
thread2 = threading.Thread(target=withdraw, args=(800, "Bob"))

print("Initial balance: $1000")
print("\nBoth Alice and Bob try to withdraw $800...\n")

thread1.start()
thread2.start()
thread1.join()
thread2.join()

print(f"\nFinal balance: ${balance}")
print("💥 WHOA! The bank lost money due to race condition!")
```

### The Concurrency Zoo 🦁

Types of concurrency bugs you'll meet:

1. **Race Condition** 🏃: "First one wins, everyone else is confused"
2. **Deadlock** 🔒: "You wait for me, I wait for you, we both starve"
3. **Livelock** 🌀: "After you... No, after you... No, after you..."
4. **Starvation** 🍽️: "The popular kids get all the resources"
5. **Phantom Writes** 👻: "I swear I saved that data..."

### Simple Fix: Take Turns!

```python
# Fixed version with a lock
import threading

balance = 1000
lock = threading.Lock()  # Our "take a number" system

def safe_withdraw(amount, person):
    global balance
    
    with lock:  # Only one person at a time!
        print(f"{person} has exclusive access")
        
        if balance >= amount:
            print(f"{person} withdrawing ${amount}")
            time.sleep(0.1)
            balance -= amount
            print(f"{person} done, balance: ${balance}")
        else:
            print(f"{person} insufficient funds!")

# Now it's safe!
thread1 = threading.Thread(target=safe_withdraw, args=(800, "Alice"))
thread2 = threading.Thread(target=safe_withdraw, args=(800, "Bob"))

thread1.start()
thread2.start()
thread1.join()
thread2.join()

print(f"\nFinal balance: ${balance}")
print("✅ Only one withdrawal succeeded!")
```

### Beginner's Mental Model

Think of concurrent operations like:
- **Multiple browser tabs** editing the same Google Doc
- **Two people** trying to book the last concert ticket
- **Kitchen timers** all going off at once
- **Traffic** at a 4-way intersection without signals

**Key Insight**: Without coordination, chaos ensues!

---

## Level 2: Foundation (Understand Why) 🌿

### Core Principle: The State Explosion

<div class="definition-box">
<h3>Sequential vs Concurrent Execution</h3>

**Sequential (Predictable):**
```
Operation A → Operation B → Operation C
Total states: 1 (always same order)
```

**Concurrent (Chaos):**
```
Operations A, B, C happening "at the same time"
Possible orderings:
- A → B → C
- A → C → B  
- B → A → C
- B → C → A
- C → A → B
- C → B → A
- A starts → B starts → A finishes → B finishes → C
- ... (many more with interleaving!)

Total states: n! × (ways to interleave) = explosion!
```

**With 10 concurrent operations**: Over 3.6 million possible orderings!
</div>

### 🎬 Failure Vignette: The Double-Booked Airplane Seat

**Company**: Major US Airline  
**Date**: December 23, 2019 (Peak Holiday Travel)  
**Impact**: 40-minute flight delay, viral social media incident

```
The Race Condition Timeline:

T 00:00.000: Alice opens seat map, sees 14A available
T 00:00.000: Bob opens seat map, sees 14A available
T 00:00.100: Alice clicks "Select 14A"
T 00:00.150: Bob clicks "Select 14A"

Server Processing (The Fatal Flaw):
T 00:00.200: Thread 1: Check if 14A available for Alice
T 00:00.210: Thread 2: Check if 14A available for Bob
T 00:00.220: Thread 1: Yes! 14A is free
T 00:00.230: Thread 2: Yes! 14A is free
T 00:00.240: Thread 1: UPDATE seats SET passenger='Alice' WHERE seat='14A'
T 00:00.250: Thread 2: UPDATE seats SET passenger='Bob' WHERE seat='14A'
T 00:00.260: Database commits Bob's update (last write wins)

At The Gate:
- Alice boards first with boarding pass for 14A
- Bob boards with boarding pass for 14A
- Confrontation in aisle
- Flight attendants can't resolve
- Pilots have to get involved
- FAA regulations require re-documentation

Root Cause: No atomic check-and-set operation
Fix Applied: Distributed lock with Redis
Cost: $50,000 in delays + bad PR
```

### The Fundamental Concurrency Challenges

#### 1. Lost Updates
```python
# The problem
def unsafe_increment():
    global counter
    temp = counter      # Read
    temp = temp + 1     # Modify  
    counter = temp      # Write
    
# If two threads do this "simultaneously":
# Thread 1: reads 0, calculates 1
# Thread 2: reads 0, calculates 1  
# Both write 1, losing an update!
```

#### 2. Dirty Reads
```python
# Thread 1: Transfer money
account_a -= 100  # Step 1
# CRASH or DELAY here!
account_b += 100  # Step 2

# Thread 2: Calculate total
total = account_a + account_b  # Sees inconsistent state!
```

#### 3. Phantom Reads
```sql
-- Thread 1: Count premium users
SELECT COUNT(*) FROM users WHERE type = 'premium';  -- Returns 100

-- Thread 2: Add a premium user
INSERT INTO users (type) VALUES ('premium');

-- Thread 1: Count again in same transaction
SELECT COUNT(*) FROM users WHERE type = 'premium';  -- Returns 101!?
```

### Concurrency Control Mechanisms

```python
# 1. PESSIMISTIC LOCKING (Lock and hold)
def transfer_pessimistic(from_acc, to_acc, amount):
    # Lock both accounts (in consistent order to avoid deadlock)
    acc1, acc2 = sorted([from_acc, to_acc], key=lambda x: x.id)
    
    with acc1.lock():
        with acc2.lock():
            if from_acc.balance >= amount:
                from_acc.balance -= amount
                to_acc.balance += amount
                return True
    return False

# 2. OPTIMISTIC LOCKING (Check on commit)
def transfer_optimistic(from_acc, to_acc, amount):
    while True:
        # Read current versions
        from_version = from_acc.version
        to_version = to_acc.version
        
        # Check balance
        if from_acc.balance < amount:
            return False
            
        # Try to update with version check
        updates = [
            ("UPDATE accounts SET balance = balance - ?, version = version + 1 "
             "WHERE id = ? AND version = ?", [amount, from_acc.id, from_version]),
            ("UPDATE accounts SET balance = balance + ?, version = version + 1 "
             "WHERE id = ? AND version = ?", [amount, to_acc.id, to_version])
        ]
        
        if all_updates_succeeded(updates):
            return True
        # Else retry - someone else modified the accounts

# 3. MVCC (Multi-Version Concurrency Control)
# Each transaction sees a consistent snapshot
# PostgreSQL/MySQL InnoDB use this
```

---

## Level 3: Deep Dive (Master the Patterns) 🌳

### Advanced Concurrency Patterns

#### 1. Compare-And-Swap (CAS) Operations
```python
import threading

class AtomicCounter:
    """Lock-free counter using CAS"""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        """Increment atomically without holding lock"""
        while True:
            current = self._value
            new_value = current + 1
            
            # CAS: Compare and swap if unchanged
            if self._compare_and_swap(current, new_value):
                return new_value
            # Else retry - value changed, try again
    
    def _compare_and_swap(self, expected, new_value):
        """Atomic CAS operation"""
        with self._lock:  # Very brief lock
            if self._value == expected:
                self._value = new_value
                return True
            return False

# Real implementation would use CPU CAS instructions
# Java: AtomicInteger, C++: std::atomic, Go: sync/atomic
```

#### 2. Software Transactional Memory (STM)
```python
class STMTransaction:
    """Simplified STM for illustration"""
    
    def __init__(self):
        self.read_set = {}   # Variables read
        self.write_set = {}  # Variables to write
        self.version = global_version_clock
    
    def read(self, ref):
        """Read a value, tracking for conflicts"""
        if ref in self.write_set:
            return self.write_set[ref]
        
        value, version = ref.read_versioned()
        self.read_set[ref] = version
        return value
    
    def write(self, ref, value):
        """Buffer write until commit"""
        self.write_set[ref] = value
    
    def commit(self):
        """Try to commit all writes atomically"""
        # Phase 1: Validate reads are still valid
        for ref, read_version in self.read_set.items():
            if ref.current_version() != read_version:
                raise ConflictException("Read conflict")
        
        # Phase 2: Lock all write locations
        write_locks = sorted(self.write_set.keys())  # Ordered to prevent deadlock
        for ref in write_locks:
            ref.lock()
        
        try:
            # Phase 3: Validate again under locks
            for ref, read_version in self.read_set.items():
                if ref.current_version() != read_version:
                    raise ConflictException("Read conflict")
            
            # Phase 4: Apply all writes
            new_version = global_version_clock.increment()
            for ref, value in self.write_set.items():
                ref.write_versioned(value, new_version)
            
        finally:
            # Release all locks
            for ref in write_locks:
                ref.unlock()

# Usage
def transfer_stm(from_id, to_id, amount):
    while True:
        try:
            with STMTransaction() as tx:
                from_balance = tx.read(accounts[from_id])
                to_balance = tx.read(accounts[to_id])
                
                if from_balance >= amount:
                    tx.write(accounts[from_id], from_balance - amount)
                    tx.write(accounts[to_id], to_balance + amount)
                    return True
                return False
                
        except ConflictException:
            continue  # Retry
```

#### 3. Lock-Free Data Structures
```python
class LockFreeQueue:
    """Michael & Scott lock-free queue (simplified)"""
    
    class Node:
        def __init__(self, value=None):
            self.value = value
            self.next = AtomicReference(None)
    
    def __init__(self):
        dummy = self.Node()
        self.head = AtomicReference(dummy)
        self.tail = AtomicReference(dummy)
    
    def enqueue(self, value):
        """Add to queue without locks"""
        new_node = self.Node(value)
        
        while True:
            tail = self.tail.get()
            tail_next = tail.next.get()
            
            if tail == self.tail.get():  # Still valid?
                if tail_next is None:
                    # Try to link new node
                    if tail.next.compare_and_set(None, new_node):
                        # Success! Try to move tail
                        self.tail.compare_and_set(tail, new_node)
                        return
                else:
                    # Help move tail forward
                    self.tail.compare_and_set(tail, tail_next)
    
    def dequeue(self):
        """Remove from queue without locks"""
        while True:
            head = self.head.get()
            tail = self.tail.get()
            head_next = head.next.get()
            
            if head == self.head.get():  # Still valid?
                if head == tail:
                    if head_next is None:
                        return None  # Queue empty
                    # Help move tail
                    self.tail.compare_and_set(tail, head_next)
                else:
                    # Read value before CAS
                    value = head_next.value
                    
                    # Try to move head
                    if self.head.compare_and_set(head, head_next):
                        return value
```

### Distributed Concurrency: Vector Clocks

```python
class VectorClock:
    """Track causality in distributed systems"""
    
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = [0] * num_processes
    
    def increment(self):
        """Increment own logical time"""
        self.clock[self.process_id] += 1
        return self.clock.copy()
    
    def update(self, other_clock):
        """Update clock on message receive"""
        for i in range(len(self.clock)):
            self.clock[i] = max(self.clock[i], other_clock[i])
        self.increment()  # Increment own time after receive
    
    def happens_before(self, other):
        """Check if this clock happens-before other"""
        return all(self.clock[i] <= other.clock[i] for i in range(len(self.clock)))
    
    def concurrent_with(self, other):
        """Check if events are concurrent"""
        return not self.happens_before(other) and not other.happens_before(self)

# Example usage
class DistributedProcess:
    def __init__(self, process_id, num_processes):
        self.vc = VectorClock(process_id, num_processes)
        self.events = []
    
    def local_event(self, description):
        """Record local event"""
        timestamp = self.vc.increment()
        self.events.append({
            'description': description,
            'timestamp': timestamp,
            'type': 'local'
        })
    
    def send_message(self, to_process, content):
        """Send message with vector clock"""
        timestamp = self.vc.increment()
        message = {
            'from': self.process_id,
            'to': to_process,
            'content': content,
            'vector_clock': timestamp
        }
        # Actually send message...
        return message
    
    def receive_message(self, message):
        """Receive and update vector clock"""
        self.vc.update(message['vector_clock'])
        self.events.append({
            'description': f"Received: {message['content']}",
            'timestamp': self.vc.clock.copy(),
            'type': 'receive'
        })
```

---

## Level 4: Expert (Production Patterns) 🌲

### Google's Chubby: Distributed Lock Service

```go
// Simplified version of Google's Chubby lock service
type ChubbyCell struct {
    replicas    []Replica
    master      *Replica
    epoch       uint64
    locks       map[string]*Lock
    sessions    map[string]*Session
}

type Lock struct {
    path        string
    owner       *Session
    mode        LockMode
    waiters     []*LockRequest
    version     uint64
    
    // Lock metadata
    created     time.Time
    modified    time.Time
    sequencer   uint64  // For fencing tokens
}

type Session struct {
    id          string
    client      ClientInfo
    leaseTime   time.Duration
    lastRenewal time.Time
    locks       map[string]*Lock
    
    // Jeopardy state when master changes
    inJeopardy  bool
}

// Client API
type ChubbyClient struct {
    cell        *ChubbyCell
    session     *Session
    cache       *FileCache
    
    // Callbacks for lock events
    callbacks   map[string]LockCallback
}

func (c *ChubbyClient) AcquireLock(path string, mode LockMode) (*LockHandle, error) {
    // 1. Ensure valid session
    if err := c.ensureSession(); err != nil {
        return nil, err
    }
    
    // 2. Send request to master
    req := &LockRequest{
        SessionID: c.session.id,
        Path:      path,
        Mode:      mode,
        Sequencer: c.getNextSequencer(),
    }
    
    resp, err := c.sendToMaster(req)
    if err != nil {
        return nil, err
    }
    
    // 3. Create lock handle with fencing token
    handle := &LockHandle{
        path:         path,
        mode:         mode,
        sequencer:    resp.Sequencer,
        session:      c.session,
        refreshTimer: time.NewTimer(c.session.leaseTime / 2),
    }
    
    // 4. Start automatic lease renewal
    go c.maintainLock(handle)
    
    return handle, nil
}

// Fencing tokens prevent delayed operations
func (h *LockHandle) GetSequencer() string {
    // Include cell epoch to detect master changes
    return fmt.Sprintf("%s:%d:%d", h.session.id, h.session.cell.epoch, h.sequencer)
}

// Usage: Storage system with Chubby locks
type StorageNode struct {
    chubby *ChubbyClient
    data   map[string][]byte
}

func (s *StorageNode) Write(key string, value []byte, lockHandle *LockHandle) error {
    // Verify we still hold the lock
    if !lockHandle.IsValid() {
        return errors.New("lock lost")
    }
    
    // Include fencing token in write
    s.data[key] = value
    s.data[key+":sequencer"] = []byte(lockHandle.GetSequencer())
    
    return nil
}

func (s *StorageNode) Read(key string) ([]byte, string, error) {
    value := s.data[key]
    sequencer := string(s.data[key+":sequencer"])
    
    // Reader can verify sequencer for consistency
    return value, sequencer, nil
}
```

### Facebook's TAO: Optimistic Concurrency at Scale

```cpp
// Simplified TAO (The Associations and Objects) system
class TAOClient {
private:
    struct Association {
        int64_t id1;          // Source object
        int64_t atype;        // Association type  
        int64_t id2;          // Destination object
        int64_t time;         // Creation timestamp
        std::string data;     // Payload
        
        // Optimistic concurrency control
        int64_t version;
        int64_t shard_id;
    };
    
    struct CacheEntry {
        Association assoc;
        uint64_t cache_version;
        bool is_negative;     // Negative cache entry
        
        std::chrono::steady_clock::time_point expiry;
    };
    
    // Multi-level cache hierarchy
    thread_local std::unordered_map<std::string, CacheEntry> l1_cache;
    std::shared_ptr<RegionalCache> l2_cache;
    std::shared_ptr<MasterDB> master_db;
    
public:
    // Read with cache hierarchy
    folly::Future<Association> AssocGet(
        int64_t id1, 
        int64_t atype, 
        int64_t id2) {
        
        std::string key = makeKey(id1, atype, id2);
        
        // L1: Thread-local cache (microseconds)
        if (auto entry = l1_cache.find(key); entry != l1_cache.end()) {
            if (entry->second.expiry > std::chrono::steady_clock::now()) {
                return folly::makeFuture(entry->second.assoc);
            }
        }
        
        // L2: Regional cache (milliseconds)
        return l2_cache->get(key).thenValue([this, key](auto result) {
            if (result.found) {
                // Populate L1
                l1_cache[key] = result.entry;
                return result.entry.assoc;
            }
            
            // L3: Master database (cross-region)
            return master_db->read(key);
        }).thenValue([this, key](Association assoc) {
            // Write-through caching
            CacheEntry entry{assoc, generateCacheVersion(), false, 
                           std::chrono::steady_clock::now() + std::chrono::seconds(60)};
            
            l1_cache[key] = entry;
            l2_cache->set(key, entry);
            
            return assoc;
        });
    }
    
    // Write with optimistic concurrency
    folly::Future<bool> AssocAdd(
        int64_t id1,
        int64_t atype, 
        int64_t id2,
        std::string data) {
        
        Association assoc{id1, atype, id2, currentTime(), data, 0, getShardId(id1)};
        
        // Optimistic add - assume no conflict
        return master_db->insert(assoc).thenValue([this, assoc](bool success) {
            if (success) {
                // Invalidate caches on write
                invalidateCaches(assoc);
                return true;
            }
            
            // Handle duplicate - might be OK for idempotent ops
            return handleDuplicate(assoc);
        });
    }
    
    // Conditional update with version check
    folly::Future<bool> AssocUpdate(
        Association old_assoc,
        std::string new_data) {
        
        Association new_assoc = old_assoc;
        new_assoc.data = new_data;
        new_assoc.version = old_assoc.version + 1;
        
        // CAS update
        return master_db->compareAndSwap(old_assoc, new_assoc)
            .thenValue([this, new_assoc](bool success) {
                if (success) {
                    invalidateCaches(new_assoc);
                    return true;
                }
                
                // Version mismatch - retry with backoff
                return folly::futures::retrying(
                    std::chrono::milliseconds(100),
                    [this, new_assoc](size_t retry_count) {
                        return exponentialBackoff(retry_count);
                    },
                    [this, new_assoc](size_t retry_count) {
                        // Re-read and retry
                        return this->AssocGet(new_assoc.id1, new_assoc.atype, new_assoc.id2)
                            .thenValue([this, new_data](Association current) {
                                return AssocUpdate(current, new_data);
                            });
                    }
                );
            });
    }
};
```

### Uber's Ringpop: Consistent Hashing with Concurrent Updates

```js
// Uber's Ringpop - Eventually consistent hash ring
class RingPop {
    constructor(node_id, options = {}) {
        this.node_id = node_id;
        this.incarnation = 0;
        
        // SWIM membership + consistent hashing
        this.members = new Map();
        this.ring = new ConsistentHashRing();
        
        // Concurrent update handling
        this.pending_updates = new Map();
        this.vector_clock = new VectorClock(node_id);
        
        // Gossip protocol
        this.gossip_interval = options.gossip_interval || 1000;
        this.fanout = options.fanout || 3;
    }
    
    // Handle concurrent ring updates
    async handleUpdate(update) {
        const update_key = `${update.node}:${update.type}`;
        
        // Check if we have a concurrent update
        if (this.pending_updates.has(update_key)) {
            const pending = this.pending_updates.get(update_key);
            
            // Resolve using vector clocks
            if (this.vector_clock.happensBefore(
                pending.vclock, 
                update.vclock
            )) {
                // New update supersedes pending
                this.pending_updates.set(update_key, update);
            } else if (this.vector_clock.concurrent(
                pending.vclock,
                update.vclock
            )) {
                // Concurrent updates - need resolution
                const resolved = this.resolveConflict(pending, update);
                this.pending_updates.set(update_key, resolved);
            }
            // else pending happens-after update, ignore
        } else {
            this.pending_updates.set(update_key, update);
        }
        
        // Process updates in causal order
        await this.processOrderedUpdates();
    }
    
    resolveConflict(update1, update2) {
        // Deterministic conflict resolution
        // Higher incarnation wins
        if (update1.incarnation > update2.incarnation) {
            return update1;
        } else if (update2.incarnation > update1.incarnation) {
            return update2;
        }
        
        // Same incarnation - compare node IDs
        if (update1.node > update2.node) {
            return update1;
        }
        
        return update2;
    }
    
    // Apply updates maintaining consistency
    async processOrderedUpdates() {
        // Topological sort based on vector clocks
        const sorted = this.topologicalSort(
            Array.from(this.pending_updates.values())
        );
        
        for (const update of sorted) {
            await this.applyUpdate(update);
            this.pending_updates.delete(
                `${update.node}:${update.type}`
            );
        }
    }
    
    // Concurrent request routing
    async lookup(key) {
        const start_time = Date.now();
        
        // Find preference list
        const nodes = this.ring.getNodes(key, this.replication_factor);
        
        // Concurrent requests to all replicas
        const requests = nodes.map(node => 
            this.sendRequest(node, 'lookup', { key })
                .catch(err => ({ error: err, node }))
        );
        
        // Wait for quorum
        const responses = await Promise.race([
            this.waitForQuorum(requests),
            this.timeout(this.request_timeout)
        ]);
        
        // Resolve concurrent values
        return this.resolveResponses(responses);
    }
    
    async waitForQuorum(requests) {
        const responses = [];
        const quorum = Math.floor(this.replication_factor / 2) + 1;
        
        return new Promise((resolve) => {
            requests.forEach(async (request) => {
                try {
                    const response = await request;
                    responses.push(response);
                    
                    if (responses.length >= quorum) {
                        resolve(responses);
                    }
                } catch (err) {
                    // Count errors toward quorum
                    responses.push({ error: err });
                    
                    if (responses.length >= quorum) {
                        resolve(responses);
                    }
                }
            });
        });
    }
    
    resolveResponses(responses) {
        // Filter successful responses
        const successful = responses.filter(r => !r.error);
        
        if (successful.length === 0) {
            throw new Error('No successful responses');
        }
        
        // Use vector clocks to find most recent
        let mostRecent = successful[0];
        
        for (const response of successful.slice(1)) {
            if (this.vector_clock.happensBefore(
                mostRecent.vclock,
                response.vclock
            )) {
                mostRecent = response;
            }
        }
        
        // Read repair - update stale replicas
        this.readRepair(responses, mostRecent);
        
        return mostRecent.value;
    }
}
```

---

## Level 5: Mastery (The Art of Concurrency) 🌴

### The Linux Kernel: RCU (Read-Copy-Update)

```c
/*
 * RCU - Concurrent reads with zero overhead
 * Used throughout Linux kernel for extreme performance
 */

struct foo {
    struct list_head list;
    int data;
    struct rcu_head rcu;
};

/* Reader - No locks, no atomic operations! */
void reader_thread(void)
{
    struct foo *p;
    
    rcu_read_lock();  /* Just disables preemption */
    
    list_for_each_entry_rcu(p, &foo_list, list) {
        /* Can read p->data safely even if writer active */
        process_data(p->data);
    }
    
    rcu_read_unlock();  /* Re-enables preemption */
}

/* Writer - Copy, update, wait for readers */
void writer_thread(int new_data)
{
    struct foo *new_foo, *old_foo;
    
    /* 1. Allocate and initialize new version */
    new_foo = kmalloc(sizeof(*new_foo), GFP_KERNEL);
    new_foo->data = new_data;
    
    /* 2. Atomically replace pointer */
    spin_lock(&foo_lock);
    old_foo = rcu_dereference_protected(global_foo,
                                      lockdep_is_held(&foo_lock));
    rcu_assign_pointer(global_foo, new_foo);
    spin_unlock(&foo_lock);
    
    /* 3. Wait for all readers to finish */
    synchronize_rcu();  /* Waits for grace period */
    
    /* 4. Now safe to free old version */
    kfree(old_foo);
}

/* 
 * RCU State Machine:
 * 
 * Reader CPU 0:  -----|reader|--------|reader|--------
 * Reader CPU 1:  --|reader|--------|reader|----------
 * Writer:        ---|update|--GP--|free|-------------
 *                           ^     ^
 *                           |     |
 *                    Grace Period Start
 *                              All Pre-existing Readers Done
 */

/* Advanced: Callback-based RCU for async free */
static void foo_rcu_free(struct rcu_head *head)
{
    struct foo *p = container_of(head, struct foo, rcu);
    kfree(p);
}

void writer_async(int new_data)
{
    struct foo *new_foo, *old_foo;
    
    new_foo = kmalloc(sizeof(*new_foo), GFP_KERNEL);
    new_foo->data = new_data;
    
    spin_lock(&foo_lock);
    old_foo = rcu_dereference_protected(global_foo,
                                      lockdep_is_held(&foo_lock));
    rcu_assign_pointer(global_foo, new_foo);
    spin_unlock(&foo_lock);
    
    /* Schedule async free after grace period */
    call_rcu(&old_foo->rcu, foo_rcu_free);
}
```

### CockroachDB: Distributed SQL Transactions

```go
// CockroachDB's distributed transaction protocol
// Combines Raft consensus + MVCC + Hybrid Logical Clocks

type Transaction struct {
    ID           UUID
    Priority     int32
    Timestamp    hlc.Timestamp  // Hybrid Logical Clock
    ReadTimestamp hlc.Timestamp
    Epoch        int32          // For detecting restarts
    
    // Distributed state
    IntentSpans  []Span         // Write intents
    InFlightWrites map[Key]Write // Uncommitted writes
    RefreshSpans []Span         // For read refresh
}

// Distributed transaction execution
func (txn *Transaction) Execute(ops []Operation) error {
    // Phase 1: Optimistic execution
    for _, op := range ops {
        switch op.Type {
        case READ:
            val, err := txn.readWithRefresh(op.Key)
            if err != nil {
                return txn.handleReadError(err)
            }
            op.Result = val
            
        case WRITE:
            // Lay down write intent
            intent := WriteIntent{
                Key:       op.Key,
                Value:     op.Value,
                Timestamp: txn.Timestamp,
                TxnID:     txn.ID,
            }
            
            if err := txn.writeIntent(intent); err != nil {
                return txn.handleWriteError(err)
            }
        }
    }
    
    // Phase 2: Commit protocol
    return txn.commit()
}

// Read with MVCC and refresh
func (txn *Transaction) readWithRefresh(key Key) (Value, error) {
    // Find right version using MVCC
    versions := mvccGet(key, txn.ReadTimestamp)
    
    for _, v := range versions {
        if v.Timestamp.LessEq(txn.ReadTimestamp) {
            // Check for write intents from other txns
            if v.IsIntent() && v.TxnID != txn.ID {
                // Hit write intent - need to resolve
                return nil, txn.handleWriteIntentError(v)
            }
            
            // Track for refresh
            txn.RefreshSpans = append(txn.RefreshSpans, 
                Span{Start: key, End: key.Next()})
            
            return v.Value, nil
        }
    }
    
    return nil, ErrNotFound
}

// Handle concurrent transactions
func (txn *Transaction) handleWriteIntentError(intent WriteIntent) error {
    otherTxn := lookupTransaction(intent.TxnID)
    
    switch otherTxn.Status {
    case PENDING:
        // Concurrent transaction - may need to wait or push
        return txn.pushTransaction(otherTxn)
        
    case COMMITTED:
        // Resolve intent to committed value
        resolveIntent(intent, COMMITTED)
        return RetryableError{Reason: "concurrent write"}
        
    case ABORTED:
        // Clean up aborted intent
        resolveIntent(intent, ABORTED)
        return nil  // Can proceed
    }
}

// Distributed commit protocol
func (txn *Transaction) commit() error {
    // Step 1: Check if read refresh needed
    if !txn.canCommitAtTimestamp(txn.Timestamp) {
        // Try to refresh reads to newer timestamp
        newTS, err := txn.refreshReads()
        if err != nil {
            return err  // Must retry
        }
        txn.Timestamp = newTS
    }
    
    // Step 2: Parallel commit optimization
    if txn.canUseParallelCommit() {
        return txn.parallelCommit()
    }
    
    // Step 3: Standard 2-phase commit
    
    // Prepare phase - write commit record
    commitRecord := TransactionRecord{
        ID:        txn.ID,
        Status:    STAGING,
        Timestamp: txn.Timestamp,
        Intents:   txn.IntentSpans,
    }
    
    if err := writeTransactionRecord(commitRecord); err != nil {
        return err
    }
    
    // Commit phase - resolve all intents
    g := errgroup.Group{}
    for _, span := range txn.IntentSpans {
        span := span  // Capture
        g.Go(func() error {
            return resolveIntentSpan(span, txn.ID, COMMITTED)
        })
    }
    
    if err := g.Wait(); err != nil {
        // Async cleanup will handle
        return err
    }
    
    // Update record to COMMITTED
    commitRecord.Status = COMMITTED
    return writeTransactionRecord(commitRecord)
}

// Parallel commit optimization
func (txn *Transaction) parallelCommit() error {
    // Write intents with "staging" status
    // Readers can determine commit status by checking all intents
    
    staging := make(chan error, len(txn.InFlightWrites))
    
    for key, write := range txn.InFlightWrites {
        go func(k Key, w Write) {
            staging <- writeIntentStaging(k, w, txn.ID)
        }(key, write)
    }
    
    // Wait for all staging writes
    for i := 0; i < len(txn.InFlightWrites); i++ {
        if err := <-staging; err != nil {
            // Abort - async cleanup will resolve
            return err
        }
    }
    
    // Implicit commit - no record needed!
    // Readers check all intents to determine status
    return nil
}
```

### The Art of Lock-Free Programming

```cpp
// Hazard Pointers - Safe memory reclamation without locks
template<typename T>
class HazardPointerList {
private:
    struct Node {
        T data;
        std::atomic<Node*> next;
        
        Node(T value) : data(std::move(value)), next(nullptr) {}
    };
    
    std::atomic<Node*> head{nullptr};
    
    // Per-thread hazard pointers
    static thread_local std::array<std::atomic<Node*>, 2> hazard_pointers;
    static std::vector<std::atomic<Node*>*> all_hazard_pointers;
    
    // Retired nodes waiting to be freed
    static thread_local std::vector<Node*> retired_nodes;
    static constexpr size_t BATCH_SIZE = 100;
    
public:
    class Iterator {
        Node* current;
        int hazard_index;
        
    public:
        Iterator(Node* node, int idx) 
            : current(node), hazard_index(idx) {
            // Protect current node
            hazard_pointers[hazard_index].store(current);
        }
        
        ~Iterator() {
            // Clear hazard pointer
            hazard_pointers[hazard_index].store(nullptr);
        }
        
        T& operator*() { return current->data; }
        
        Iterator& operator++() {
            Node* next = current->next.load();
            hazard_pointers[hazard_index].store(next);
            current = next;
            return *this;
        }
    };
    
    void push_front(T value) {
        Node* new_node = new Node(std::move(value));
        Node* old_head = head.load();
        
        do {
            new_node->next = old_head;
        } while (!head.compare_exchange_weak(old_head, new_node));
    }
    
    bool pop_front() {
        hazard_pointers[0].store(head.load());
        
        do {
            Node* old_head = hazard_pointers[0].load();
            if (!old_head) {
                return false;  // Empty
            }
            
            Node* next = old_head->next.load();
            
            // Try to update head
            if (head.compare_exchange_weak(old_head, next)) {
                // Success - retire the node
                retire_node(old_head);
                hazard_pointers[0].store(nullptr);
                return true;
            }
            
            // Failed - update hazard pointer and retry
            hazard_pointers[0].store(head.load());
            
        } while (true);
    }
    
private:
    void retire_node(Node* node) {
        retired_nodes.push_back(node);
        
        if (retired_nodes.size() >= BATCH_SIZE) {
            scan_and_free();
        }
    }
    
    void scan_and_free() {
        // Collect all hazard pointers
        std::unordered_set<Node*> hazards;
        
        for (auto& hp_array : all_hazard_pointers) {
            for (auto& hp : *hp_array) {
                Node* p = hp.load();
                if (p) {
                    hazards.insert(p);
                }
            }
        }
        
        // Free nodes not in hazard set
        auto new_end = std::remove_if(
            retired_nodes.begin(),
            retired_nodes.end(),
            [&hazards](Node* node) {
                if (hazards.find(node) == hazards.end()) {
                    delete node;
                    return true;  // Remove from retired
                }
                return false;  // Keep in retired
            }
        );
        
        retired_nodes.erase(new_end, retired_nodes.end());
    }
};

// Memory ordering subtleties
class SeqLockOptimized {
    struct alignas(64) Data {  // Cache line aligned
        uint64_t value1;
        uint64_t value2;
        char padding[48];  // Avoid false sharing
    };
    
    alignas(64) std::atomic<uint32_t> seq{0};
    alignas(64) Data data;
    
public:
    void write(uint64_t v1, uint64_t v2) {
        uint32_t s = seq.load(std::memory_order_relaxed);
        
        // Odd sequence = write in progress
        seq.store(s + 1, std::memory_order_relaxed);
        std::atomic_thread_fence(std::memory_order_release);
        
        // Non-atomic writes (safe due to odd sequence)
        data.value1 = v1;
        data.value2 = v2;
        
        std::atomic_thread_fence(std::memory_order_release);
        seq.store(s + 2, std::memory_order_relaxed);
    }
    
    std::pair<uint64_t, uint64_t> read() {
        uint32_t s1, s2;
        uint64_t v1, v2;
        
        do {
            s1 = seq.load(std::memory_order_acquire);
            
            // Compiler barrier to prevent reordering
            std::atomic_signal_fence(std::memory_order_acq_rel);
            
            v1 = data.value1;
            v2 = data.value2;
            
            std::atomic_thread_fence(std::memory_order_acquire);
            s2 = seq.load(std::memory_order_relaxed);
            
        } while (s1 != s2 || s1 & 1);  // Retry if seq changed or odd
        
        return {v1, v2};
    }
};
```

### The Disruptor Pattern: Mechanical Sympathy

```java
/**
 * LMAX Disruptor - Million+ messages/sec with single thread
 * Key insight: CPU cache is the new RAM
 */
public class Disruptor<T> {
    
    // Ring buffer - power of 2 size for fast modulo
    private final Object[] entries;
    private final int indexMask;
    
    // Padded to prevent false sharing
    private final PaddedAtomicLong cursor = new PaddedAtomicLong();
    
    // Wait strategies
    private final WaitStrategy waitStrategy;
    
    // Consumer tracking
    private final Sequence[] gatingSequences;
    
    public Disruptor(int bufferSize, EventFactory<T> factory) {
        this.entries = new Object[bufferSize];
        this.indexMask = bufferSize - 1;
        
        // Pre-allocate all events
        for (int i = 0; i < bufferSize; i++) {
            entries[i] = factory.newInstance();
        }
    }
    
    // Producer - wait-free
    public long next() {
        long current;
        long next;
        
        do {
            current = cursor.get();
            next = current + 1;
            
            // Check if buffer full
            long wrapPoint = next - entries.length;
            long minGatingSequence = getMinimumSequence(gatingSequences);
            
            if (wrapPoint > minGatingSequence) {
                // Buffer full - need to wait
                waitStrategy.signalAllWhenBlocking();
                LockSupport.parkNanos(1L);
                continue;
            }
            
        } while (!cursor.compareAndSet(current, next));
        
        return next;
    }
    
    public void publish(long sequence) {
        // Memory barrier ensures visibility
        cursor.set(sequence);
        waitStrategy.signalAllWhenBlocking();
    }
    
    // Consumer - wait-free reading
    public T get(long sequence) {
        // Fast modulo using bit mask
        return (T) entries[(int) sequence & indexMask];
    }
    
    // Batching consumer for efficiency
    public interface EventHandler<T> {
        void onEvent(T event, long sequence, boolean endOfBatch);
    }
    
    class BatchEventProcessor implements Runnable {
        private final EventHandler<T> handler;
        private final Sequence sequence = new Sequence();
        
        public void run() {
            long nextSequence = sequence.get() + 1L;
            
            while (running) {
                long availableSequence = cursor.get();
                
                if (nextSequence <= availableSequence) {
                    // Process batch
                    for (long seq = nextSequence; seq <= availableSequence; seq++) {
                        T event = get(seq);
                        boolean endOfBatch = seq == availableSequence;
                        
                        handler.onEvent(event, seq, endOfBatch);
                    }
                    
                    sequence.set(availableSequence);
                    nextSequence = availableSequence + 1;
                    
                } else {
                    // No events available
                    waitStrategy.idle();
                }
            }
        }
    }
}

// Mechanical sympathy: cache-line padding
class PaddedAtomicLong extends AtomicLong {
    // 64 bytes = typical cache line size
    private volatile long p1, p2, p3, p4, p5, p6 = 7L;
    
    // Prevent false sharing between CPU cores
    public long sumPadding() {
        // Prevent elimination by HotSpot
        return p1 + p2 + p3 + p4 + p5 + p6;
    }
}
```

## Summary: Concurrency Mastery Levels

### 🌱 Beginner
1. **Race conditions exist** - Multiple threads = chaos
2. **Locks prevent races** - But reduce parallelism
3. **Order matters** - A then B ≠ B then A

### 🌿 Intermediate
1. **State explosion** - n! possible orderings
2. **Deadlocks happen** - Circular dependencies kill
3. **Optimistic vs Pessimistic** - Trade-offs exist

### 🌳 Advanced
1. **Lock-free is possible** - CAS operations
2. **Vector clocks track causality** - Distributed ordering
3. **MVCC enables readers** - Writers don't block readers

### 🌲 Expert
1. **Consensus is expensive** - Paxos/Raft complexity
2. **Eventually consistent** - Works for many cases
3. **Cache coherence matters** - False sharing kills performance

### 🌴 Master
1. **Memory ordering subtleties** - Acquire/release semantics
2. **Hardware matters** - Cache lines, NUMA effects
3. **Wait-free algorithms** - The holy grail of concurrency

## Quick Reference: Concurrency Patterns

<div class="reference-card">
<h3>📋 Concurrency Control Cheat Sheet</h3>

**Choose Your Weapon:**
```
Low Contention (< 10% conflicts):
  → Optimistic locking (CAS)
  → MVCC
  → Lock-free data structures

Medium Contention (10-50%):
  → Fine-grained locking
  → Read-write locks
  → Striped locks

High Contention (> 50%):
  → Queue and serialize
  → Partition the resource
  → Redesign to avoid sharing
```

**Common Patterns:**
```
□ Double-checked locking (careful!)
□ Copy-on-write
□ Reader-writer locks
□ Lock striping
□ Wait-free queues
□ Hazard pointers
□ RCU (Read-Copy-Update)
□ STM (Software Transactional Memory)
```

**Debugging Concurrency:**
```
□ Thread sanitizer (TSan)
□ Helgrind (Valgrind)
□ Stress testing with chaos
□ Model checking (TLA+)
□ Linearizability testing
```
</div>

---

**Next**: [Axiom 5: Coordination →](../axiom5-coordination/)

*"Shared mutable state is the root of all evil. The history of computing is the history of avoiding shared mutable state."*