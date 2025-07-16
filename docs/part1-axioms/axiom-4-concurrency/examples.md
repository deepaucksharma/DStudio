# Concurrency Examples & Failure Stories

!!! info "Prerequisites"
    - [Axiom 4: Concurrency Core Concepts](index.md)

!!! tip "Quick Navigation"
    [← Concurrency Concepts](index.md) | 
    [Exercises →](exercises.md) |
    [↑ Axioms Overview](../index.md)

## Real-World Failure Stories

<div class="failure-vignette">

### 🎬 The Double-Booked Airplane Seat

```yaml
Airline: Major US carrier
Date: December 23, 2019 (peak travel)
System: Seat assignment during online check-in

Race Condition Timeline:
T1 00:00.000: Alice views seat map, 14A shows available
T1 00:00.000: Bob views seat map, 14A shows available
T1 00:00.100: Alice clicks "Select 14A"
T1 00:00.150: Bob clicks "Select 14A"
T1 00:00.200: System checks 14A available for Alice ✓
T1 00:00.250: System checks 14A available for Bob ✓
T1 00:00.300: System assigns 14A to Alice
T1 00:00.350: System assigns 14A to Bob
T1 00:00.400: Database now shows Bob in 14A

At the gate:
- Both passengers have boarding passes for 14A
- Alice boards first, sits down
- Bob boards, confrontation ensues
- Flight delayed 40 minutes for resolution
- Social media nightmare

Root Cause:
- Check and Set were not atomic
- No locking between read and write
- Last write wins

Fix: 
- Distributed lock with atomic compare-and-swap
- Versioned updates
- Immediate consistency for seat assignments
```

</div>

<div class="failure-vignette">

### 🎬 The Banking Deadlock Crisis

```yaml
Bank: Top 5 US Bank
Date: Month-end processing, 2021
System: Inter-account transfer system

The Deadly Embrace:
Thread 1: Transfer $1000 from A to B
  1. Lock account A
  2. Deduct $1000 from A
  3. Try to lock account B... (waiting)

Thread 2: Transfer $500 from B to A  
  1. Lock account B
  2. Deduct $500 from B
  3. Try to lock account A... (waiting)

DEADLOCK! Both threads waiting forever

Cascade Effect:
- 2 threads deadlocked at 9:01 PM
- 50 threads deadlocked by 9:05 PM
- 500 threads deadlocked by 9:10 PM
- Thread pool exhausted
- All transfers stopped
- Month-end processing failed

Business Impact:
- 100,000 delayed transactions
- $50M in late fees waived
- 3 days to reconcile accounts
- Regulatory investigation

Fix:
- Always lock accounts in order (by ID)
- Deadlock detection with timeout
- Circuit breaker on lock wait time
- Separate thread pools by operation type
```

</div>

<div class="failure-vignette">

### 🎬 The Inventory Count Catastrophe

```yaml
E-commerce: Flash sale platform
Event: iPhone 15 launch
Problem: Oversold by 10,000 units

The Race Condition:
inventory = 1000  # Available units

# 10,000 concurrent users
for user in users:
    if inventory > 0:  # Check
        inventory -= 1  # Update
        process_order(user)

What Actually Happened:
- All 10,000 threads read inventory = 1000
- All 10,000 passed the check
- All 10,000 placed orders
- Final inventory: -9000

Timeline:
00:00: Sale starts, 1000 units available
00:01: 10,000 orders accepted
00:05: Warehouse reports "only 1000 units!"
00:30: Customer service flooded
01:00: CEO apologizing on Twitter

Financial Impact:
- $5M in compensation
- 20% stock price drop
- Class action lawsuit
- Brand damage

Fix:
- Atomic decrement operations
- Distributed semaphore
- Pre-allocated inventory tokens
- Pessimistic locking for hot items
```

</div>

## Common Concurrency Patterns & Problems

### 1. The ABA Problem

```cpp
// Thread 1 reads
Node* head = stack->head;  // head = A
// Context switch...

// Thread 2 executes
pop();  // Removes A
pop();  // Removes B  
push(A); // A is back!

// Thread 1 continues
// head still points to A, seems valid
if (compare_and_swap(&stack->head, head, head->next)) {
    // Success! But head->next is now garbage!
}
```

Real-world impact: Memory corruption in lock-free data structures.

### 2. Priority Inversion

```yaml
The Mars Pathfinder Bug (1997):

High Priority: Data collection task
Medium Priority: Communications task
Low Priority: Meteorological task

What happened:
1. Low priority task acquires mutex
2. High priority task needs mutex, blocks
3. Medium priority task runs (higher than low)
4. Low priority can't release mutex
5. High priority task misses deadline
6. Watchdog timer resets system

Solution: Priority inheritance protocol
```

### 3. The Thundering Herd

```python
# Naive cache implementation
def get_data(key):
    value = cache.get(key)
    if value is None:
        # Cache miss - all threads do this!
        value = expensive_database_query(key)
        cache.set(key, value)
    return value

# Problem: 1000 concurrent requests for same key
# Result: 1000 database queries!
```

### 4. False Sharing

```c
// Looks safe - different array elements
struct counter {
    long count;  // 8 bytes
} counters[NUM_THREADS];

// Thread 1
counters[0].count++;  

// Thread 2
counters[1].count++;

// Problem: Both in same cache line (64 bytes)
// Result: Cache ping-pong between cores
// Performance: 10x slower than expected!
```

## Concurrency in Different Contexts

### Database Concurrency

#### Lost Update Problem

```sql
-- User 1 reads balance
SELECT balance FROM accounts WHERE id = 123;  -- Returns 1000

-- User 2 reads balance  
SELECT balance FROM accounts WHERE id = 123;  -- Returns 1000

-- User 1 deposits 100
UPDATE accounts SET balance = 1100 WHERE id = 123;

-- User 2 withdraws 200
UPDATE accounts SET balance = 800 WHERE id = 123;

-- Result: Lost $100 deposit!
```

#### Phantom Reads

```sql
-- Transaction 1: Count premium users
BEGIN;
SELECT COUNT(*) FROM users WHERE type = 'premium';  -- Returns 100

-- Transaction 2: Add premium user
INSERT INTO users (type) VALUES ('premium');
COMMIT;

-- Transaction 1: Count again
SELECT COUNT(*) FROM users WHERE type = 'premium';  -- Returns 101!
-- Phantom record appeared!
```

### Distributed System Concurrency

#### Split-Brain Syndrome

```yaml
Cluster: 2-node active-active database

Normal: 
  Node A: Primary
  Node B: Secondary
  Heartbeat: OK

Network Partition:
  Node A: "B is dead, I'm primary"
  Node B: "A is dead, I'm primary"
  
Both nodes accepting writes!

Client 1 → Node A: UPDATE user SET email = 'new@example.com'
Client 2 → Node B: DELETE user WHERE id = 123

Partition heals:
  Which change wins?
  User exists or not?
  Data corrupted!
```

### Memory Model Issues

#### Weak Memory Ordering

```java
// Thread 1
data = 42;
flag = true;

// Thread 2  
while (!flag) { }
print(data);  // May print 0!

// Why? CPU reordered writes
// Fix: Memory barriers/volatile
```

## Debugging Concurrent Issues

### Heisenbugs

Bugs that disappear when you try to observe them:

```python
# Production code - always fails
def transfer_money(from_acc, to_acc, amount):
    balance1 = get_balance(from_acc)
    balance2 = get_balance(to_acc)
    
    set_balance(from_acc, balance1 - amount)
    set_balance(to_acc, balance2 + amount)

# Debug version - never fails!
def transfer_money(from_acc, to_acc, amount):
    print(f"Starting transfer...")  # Added logging
    balance1 = get_balance(from_acc)
    print(f"Got balance1: {balance1}")  # Slows down execution
    balance2 = get_balance(to_acc)
    print(f"Got balance2: {balance2}")  # Changes timing
    
    set_balance(from_acc, balance1 - amount)
    set_balance(to_acc, balance2 + amount)
    
# The print statements change timing, hide the race!
```

### Tools & Techniques

#### Thread Sanitizer Output

```
WARNING: ThreadSanitizer: data race
  Write of size 4 at 0x7b04000000 by thread T1:
    #0 increment counter.cpp:10
    
  Previous read of size 4 at 0x7b04000000 by thread T2:
    #0 read_value counter.cpp:15
    
  Location is global 'counter' of size 4 at counter.cpp:3
```

#### Deadlock Detection

```python
# Visualize lock dependencies
Lock Graph:
  Thread1 → LockA → LockB ↓
     ↑                    ↓
     ↑                    ↓
  Thread2 ← LockB ← LockA ←
  
  CYCLE DETECTED: Deadlock!
```

## Best Practices & Solutions

### 1. Lock Ordering

```python
# Always acquire locks in consistent order
def transfer(account1, account2, amount):
    # Sort by account ID to prevent deadlock
    if account1.id < account2.id:
        first, second = account1, account2
    else:
        first, second = account2, account1
        amount = -amount  # Reverse direction
    
    with lock(first):
        with lock(second):
            first.balance -= amount
            second.balance += amount
```

### 2. Compare-And-Swap Patterns

```java
// Retry loop for CAS operations
public void increment() {
    while (true) {
        int current = counter.get();
        int next = current + 1;
        if (counter.compareAndSet(current, next)) {
            break;  // Success
        }
        // Retry - someone else modified it
    }
}
```

### 3. Lock-Free Queue

```c
// Michael & Scott lock-free queue
bool enqueue(Queue* q, Node* node) {
    while (true) {
        Node* last = q->tail;
        Node* next = last->next;
        
        if (last == q->tail) {  // Still valid?
            if (next == NULL) {
                // Try to link node
                if (CAS(&last->next, NULL, node)) {
                    // Success! Try to swing tail
                    CAS(&q->tail, last, node);
                    return true;
                }
            } else {
                // Help other thread finish
                CAS(&q->tail, last, next);
            }
        }
    }
}
```

## Key Insights from Failures

!!! danger "Common Patterns"
    
    1. **Testing doesn't find concurrency bugs** - Too many possible interleavings
    2. **Adding threads makes things worse** - More complexity, not more speed
    3. **Locks aren't compositional** - Two correct components = deadlock
    4. **Timing assumptions always break** - Never depend on speed
    5. **Debugging changes behavior** - Heisenbugs are real

## Navigation

!!! tip "Continue Learning"
    
    **Practice**: [Try Concurrency Exercises](exercises.md) →
    
    **Next Axiom**: [Axiom 5: Coordination Cost](../axiom-5-coordination/index.md) →
    
    **Tools**: [Concurrency Testing Tools](../../tools/concurrency-tools.md)