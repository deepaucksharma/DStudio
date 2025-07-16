# Concurrency Exercises

!!! info "Prerequisites"
    - [Axiom 4: Concurrency Core Concepts](index.md)
    - [Concurrency Examples](examples.md)
    - Understanding of threads and synchronization

!!! tip "Quick Navigation"
    [← Examples](examples.md) | 
    [↑ Concurrency Home](index.md) |
    [→ Next Axiom](../axiom-5-coordination/index.md)

## Exercise 1: Demonstrate Race Conditions

### 🔧 Try This: The Classic Counter Problem

```python
import threading
import time

# Shared counter without protection
counter = 0

def increment_unsafe():
    global counter
    for _ in range(100000):
        # This is NOT atomic!
        temp = counter
        temp = temp + 1
        counter = temp

def increment_safe():
    global counter
    global lock
    for _ in range(100000):
        with lock:
            counter += 1

# Exercise: Compare unsafe vs safe increment
def test_race_condition():
    global counter
    global lock
    
    # Test 1: Unsafe increment
    counter = 0
    threads = []
    
    print("Testing UNSAFE increment...")
    start = time.time()
    
    for i in range(5):
        t = threading.Thread(target=increment_unsafe)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    unsafe_time = time.time() - start
    unsafe_result = counter
    
    # Test 2: Safe increment
    counter = 0
    lock = threading.Lock()
    threads = []
    
    print("Testing SAFE increment...")
    start = time.time()
    
    for i in range(5):
        t = threading.Thread(target=increment_safe)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    safe_time = time.time() - start
    safe_result = counter
    
    # Results
    print(f"\nResults:")
    print(f"Expected: 500,000")
    print(f"Unsafe: {unsafe_result} (lost {500000 - unsafe_result} updates)")
    print(f"Safe: {safe_result}")
    print(f"\nTiming:")
    print(f"Unsafe: {unsafe_time:.3f}s")
    print(f"Safe: {safe_time:.3f}s (overhead: {((safe_time/unsafe_time)-1)*100:.1f}%)")

# TODO: Implement a version using atomic operations
# Hint: Use threading.Lock() or multiprocessing.Value
```

<details>
<summary>Solution</summary>

```python
import threading
import time
from multiprocessing import Value, Process
import ctypes

# Different synchronization approaches

# 1. Lock-based solution
class SafeCounterLock:
    def __init__(self):
        self.value = 0
        self.lock = threading.Lock()
    
    def increment(self):
        with self.lock:
            self.value += 1
    
    def get(self):
        with self.lock:
            return self.value

# 2. Atomic operation solution (using multiprocessing.Value)
def increment_atomic(counter, n):
    for _ in range(n):
        with counter.get_lock():
            counter.value += 1

# 3. Lock-free solution using compare-and-swap simulation
class LockFreeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()  # For CAS simulation
    
    def compare_and_swap(self, expected, new_value):
        with self._lock:  # Simulating atomic CAS
            if self._value == expected:
                self._value = new_value
                return True
            return False
    
    def increment(self):
        while True:
            current = self._value
            if self.compare_and_swap(current, current + 1):
                break
    
    def get(self):
        return self._value

# Complete test suite
def comprehensive_concurrency_test():
    num_threads = 5
    operations_per_thread = 100000
    expected = num_threads * operations_per_thread
    
    print("=== Comprehensive Concurrency Test ===\n")
    
    # Test 1: No synchronization (race condition)
    print("1. No Synchronization (Race Condition):")
    counter = 0
    
    def unsafe_increment():
        global counter
        for _ in range(operations_per_thread):
            counter += 1
    
    threads = []
    start = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=unsafe_increment)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    unsafe_time = time.time() - start
    print(f"   Result: {counter:,} (expected {expected:,})")
    print(f"   Lost updates: {expected - counter:,}")
    print(f"   Time: {unsafe_time:.3f}s\n")
    
    # Test 2: Lock-based synchronization
    print("2. Lock-based Synchronization:")
    safe_counter = SafeCounterLock()
    
    def safe_increment():
        for _ in range(operations_per_thread):
            safe_counter.increment()
    
    threads = []
    start = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=safe_increment)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    lock_time = time.time() - start
    print(f"   Result: {safe_counter.get():,}")
    print(f"   Time: {lock_time:.3f}s")
    print(f"   Overhead: {((lock_time/unsafe_time)-1)*100:.1f}%\n")
    
    # Test 3: Atomic operations
    print("3. Atomic Operations (multiprocessing.Value):")
    atomic_counter = Value('i', 0)
    
    processes = []
    start = time.time()
    
    for _ in range(num_threads):
        p = Process(target=increment_atomic, args=(atomic_counter, operations_per_thread))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    atomic_time = time.time() - start
    print(f"   Result: {atomic_counter.value:,}")
    print(f"   Time: {atomic_time:.3f}s\n")
    
    # Test 4: Lock-free (CAS)
    print("4. Lock-free (Compare-and-Swap):")
    lf_counter = LockFreeCounter()
    
    def lockfree_increment():
        for _ in range(operations_per_thread):
            lf_counter.increment()
    
    threads = []
    start = time.time()
    
    for _ in range(num_threads):
        t = threading.Thread(target=lockfree_increment)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    cas_time = time.time() - start
    print(f"   Result: {lf_counter.get():,}")
    print(f"   Time: {cas_time:.3f}s\n")
    
    # Summary
    print("=== Summary ===")
    print(f"Unsafe (race): {unsafe_time:.3f}s - INCORRECT RESULT")
    print(f"Lock-based: {lock_time:.3f}s - {((lock_time/unsafe_time)-1)*100:+.1f}% vs unsafe")
    print(f"Atomic: {atomic_time:.3f}s - {((atomic_time/unsafe_time)-1)*100:+.1f}% vs unsafe")
    print(f"Lock-free: {cas_time:.3f}s - {((cas_time/unsafe_time)-1)*100:+.1f}% vs unsafe")

# Run the comprehensive test
comprehensive_concurrency_test()
```

</details>

## Exercise 2: Deadlock Detection

### 🔧 Try This: Create and Detect Deadlocks

```python
import threading
import time
import random

class BankAccount:
    def __init__(self, id, balance):
        self.id = id
        self.balance = balance
        self.lock = threading.Lock()

def transfer_unsafe(from_acc, to_acc, amount):
    """Transfer with potential deadlock"""
    # TODO: Implement transfer that can deadlock
    # Hint: Lock accounts in different orders
    pass

def transfer_safe(from_acc, to_acc, amount):
    """Transfer with deadlock prevention"""
    # TODO: Implement deadlock-free transfer
    # Hint: Always lock in consistent order
    pass

class DeadlockDetector:
    def __init__(self):
        self.lock_graph = {}  # thread -> list of held locks
        self.wait_graph = {}  # thread -> lock waiting for
        
    def acquire_lock(self, thread_id, lock_id):
        # TODO: Track lock acquisition
        pass
    
    def wait_for_lock(self, thread_id, lock_id):
        # TODO: Track waiting
        pass
    
    def release_lock(self, thread_id, lock_id):
        # TODO: Track release
        pass
    
    def detect_cycle(self):
        """Detect cycle in wait graph"""
        # TODO: Implement cycle detection
        # Return True if deadlock detected
        pass

# Exercise: Create a scenario that deadlocks
def deadlock_scenario():
    acc1 = BankAccount(1, 1000)
    acc2 = BankAccount(2, 1000)
    acc3 = BankAccount(3, 1000)
    
    # TODO: Create threads that will deadlock
    # Thread 1: Transfer A→B, then B→C
    # Thread 2: Transfer B→C, then C→A  
    # Thread 3: Transfer C→A, then A→B
    
    # Run and observe deadlock
    # Then implement deadlock-free version
```

<details>
<summary>Solution</summary>

```python
import threading
import time
import random
from collections import defaultdict
import networkx as nx

class BankAccount:
    def __init__(self, id, balance):
        self.id = id
        self.balance = balance
        self.lock = threading.Lock()
        self.lock_id = f"Account-{id}"

def transfer_unsafe(from_acc, to_acc, amount, thread_name):
    """Transfer with potential deadlock"""
    print(f"{thread_name}: Trying to transfer ${amount} from {from_acc.id} to {to_acc.id}")
    
    # Acquire locks in the order we receive them (DANGEROUS!)
    print(f"{thread_name}: Acquiring lock on account {from_acc.id}")
    from_acc.lock.acquire()
    
    # Simulate some processing time
    time.sleep(0.01)
    
    print(f"{thread_name}: Acquiring lock on account {to_acc.id}")
    to_acc.lock.acquire()
    
    try:
        if from_acc.balance >= amount:
            from_acc.balance -= amount
            to_acc.balance += amount
            print(f"{thread_name}: Transfer complete")
        else:
            print(f"{thread_name}: Insufficient funds")
    finally:
        to_acc.lock.release()
        from_acc.lock.release()

def transfer_safe(from_acc, to_acc, amount, thread_name):
    """Transfer with deadlock prevention using ordered locking"""
    print(f"{thread_name}: Trying to transfer ${amount} from {from_acc.id} to {to_acc.id}")
    
    # Always acquire locks in a consistent order (by account ID)
    first, second = (from_acc, to_acc) if from_acc.id < to_acc.id else (to_acc, from_acc)
    
    print(f"{thread_name}: Acquiring locks in order: {first.id}, {second.id}")
    
    with first.lock:
        with second.lock:
            if from_acc.balance >= amount:
                from_acc.balance -= amount
                to_acc.balance += amount
                print(f"{thread_name}: Transfer complete")
            else:
                print(f"{thread_name}: Insufficient funds")

class DeadlockDetector:
    def __init__(self):
        self.lock_graph = defaultdict(set)  # thread -> set of held locks
        self.wait_graph = defaultdict(str)   # thread -> lock waiting for
        self.lock_owners = {}                # lock -> thread
        self.lock = threading.Lock()
        
    def acquire_lock(self, thread_id, lock_id):
        with self.lock:
            self.lock_graph[thread_id].add(lock_id)
            self.lock_owners[lock_id] = thread_id
            # Remove from wait graph if was waiting
            if thread_id in self.wait_graph and self.wait_graph[thread_id] == lock_id:
                del self.wait_graph[thread_id]
    
    def wait_for_lock(self, thread_id, lock_id):
        with self.lock:
            self.wait_graph[thread_id] = lock_id
            # Check for deadlock
            if self.detect_cycle():
                print(f"⚠️ DEADLOCK DETECTED involving thread {thread_id}!")
                self.print_cycle()
    
    def release_lock(self, thread_id, lock_id):
        with self.lock:
            if lock_id in self.lock_graph[thread_id]:
                self.lock_graph[thread_id].remove(lock_id)
            if lock_id in self.lock_owners:
                del self.lock_owners[lock_id]
    
    def detect_cycle(self):
        """Detect cycle in wait-for graph using DFS"""
        # Build directed graph: thread -> thread it's waiting for
        graph = nx.DiGraph()
        
        for waiting_thread, lock in self.wait_graph.items():
            if lock in self.lock_owners:
                owning_thread = self.lock_owners[lock]
                graph.add_edge(waiting_thread, owning_thread)
        
        try:
            cycles = list(nx.simple_cycles(graph))
            return len(cycles) > 0
        except:
            return False
    
    def print_cycle(self):
        """Print the deadlock cycle"""
        graph = nx.DiGraph()
        
        for waiting_thread, lock in self.wait_graph.items():
            if lock in self.lock_owners:
                owning_thread = self.lock_owners[lock]
                graph.add_edge(waiting_thread, owning_thread)
        
        cycles = list(nx.simple_cycles(graph))
        if cycles:
            print("Deadlock cycle:")
            for cycle in cycles:
                cycle_str = " -> ".join(cycle + [cycle[0]])
                print(f"  {cycle_str}")

# Global deadlock detector
detector = DeadlockDetector()

# Monitored lock class
class MonitoredLock:
    def __init__(self, lock_id):
        self.lock_id = lock_id
        self.lock = threading.Lock()
    
    def acquire(self):
        thread_id = threading.current_thread().name
        detector.wait_for_lock(thread_id, self.lock_id)
        self.lock.acquire()
        detector.acquire_lock(thread_id, self.lock_id)
    
    def release(self):
        thread_id = threading.current_thread().name
        self.lock.release()
        detector.release_lock(thread_id, self.lock_id)

# Test deadlock scenario
def test_deadlock_detection():
    print("=== Deadlock Detection Demo ===\n")
    
    # Create accounts with monitored locks
    accounts = []
    for i in range(4):
        acc = BankAccount(i, 1000)
        acc.lock = MonitoredLock(f"Account-{i}")
        accounts.append(acc)
    
    print("Creating circular transfer pattern that will deadlock...\n")
    
    def circular_transfer(acc1, acc2, acc3, thread_name):
        """Transfer in a circle: acc1→acc2, acc2→acc3, acc3→acc1"""
        try:
            # First transfer
            transfer_with_monitoring(acc1, acc2, 100, thread_name)
            time.sleep(0.1)  # Increase chance of interleaving
            
            # Second transfer  
            transfer_with_monitoring(acc2, acc3, 100, thread_name)
            time.sleep(0.1)
            
            # Third transfer (completes the circle)
            transfer_with_monitoring(acc3, acc1, 100, thread_name)
            
        except Exception as e:
            print(f"{thread_name}: Error - {e}")
    
    def transfer_with_monitoring(from_acc, to_acc, amount, thread_name):
        print(f"{thread_name}: Transferring ${amount} from {from_acc.id} to {to_acc.id}")
        
        from_acc.lock.acquire()
        time.sleep(0.05)  # Simulate work
        
        to_acc.lock.acquire()
        
        try:
            from_acc.balance -= amount
            to_acc.balance += amount
            print(f"{thread_name}: Transfer complete")
        finally:
            to_acc.lock.release()
            from_acc.lock.release()
    
    # Create threads with circular dependencies
    threads = []
    
    # Thread 1: 0→1→2→0
    t1 = threading.Thread(
        target=circular_transfer,
        args=(accounts[0], accounts[1], accounts[2], "Thread-1"),
        name="Thread-1"
    )
    
    # Thread 2: 1→2→3→1 
    t2 = threading.Thread(
        target=circular_transfer,
        args=(accounts[1], accounts[2], accounts[3], "Thread-2"),
        name="Thread-2"
    )
    
    # Thread 3: 2→3→0→2
    t3 = threading.Thread(
        target=circular_transfer,
        args=(accounts[2], accounts[3], accounts[0], "Thread-3"),
        name="Thread-3"
    )
    
    threads = [t1, t2, t3]
    
    # Start threads
    for t in threads:
        t.start()
    
    # Wait a bit to see if deadlock occurs
    time.sleep(2)
    
    # Check thread status
    print("\n=== Thread Status ===")
    for t in threads:
        if t.is_alive():
            print(f"{t.name}: BLOCKED (likely deadlocked)")
        else:
            print(f"{t.name}: Completed")
    
    print("\nNote: In a real system, you would implement deadlock recovery")
    print("Options: timeout & rollback, victim selection, or restart")

# Run the test
test_deadlock_detection()
```

</details>

## Exercise 3: Implement Lock-Free Stack

### 🔧 Try This: Build a Lock-Free Data Structure

```python
import threading
import time
from typing import Optional

class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LockFreeStack:
    """
    Implement a lock-free stack using compare-and-swap
    """
    def __init__(self):
        self.head = None
        self._lock = threading.Lock()  # For simulating CAS
        
    def compare_and_swap(self, expected, new_value):
        """
        Simulate atomic CAS operation
        In real implementation, this would be a CPU instruction
        """
        with self._lock:
            if self.head is expected:
                self.head = new_value
                return True
            return False
    
    def push(self, value):
        """
        TODO: Implement lock-free push
        1. Create new node
        2. Set new_node.next to current head
        3. CAS head from current to new_node
        4. Retry if CAS fails
        """
        pass
    
    def pop(self) -> Optional[int]:
        """
        TODO: Implement lock-free pop
        1. Read current head
        2. If null, return None
        3. CAS head from current to current.next
        4. If CAS succeeds, return current.value
        5. Retry if CAS fails
        """
        pass

# Exercise: Test the lock-free stack
def stress_test_stack():
    stack = LockFreeStack()
    push_count = 10000
    pop_count = 10000
    num_threads = 4
    
    # TODO: Create producer and consumer threads
    # Verify that no values are lost
    # Compare performance with locked version
```

<details>
<summary>Solution</summary>

```python
import threading
import time
from typing import Optional
import random
from collections import Counter

class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LockFreeStack:
    """Lock-free stack using compare-and-swap"""
    def __init__(self):
        self.head = None
        self._lock = threading.Lock()  # For simulating CAS
        self.push_retries = 0
        self.pop_retries = 0
        
    def compare_and_swap(self, expected, new_value):
        """Simulate atomic CAS operation"""
        with self._lock:
            if self.head is expected:
                self.head = new_value
                return True
            return False
    
    def push(self, value):
        """Lock-free push with retry loop"""
        new_node = Node(value)
        
        while True:
            current_head = self.head
            new_node.next = current_head
            
            if self.compare_and_swap(current_head, new_node):
                return
            
            # CAS failed, someone else modified head
            self.push_retries += 1
            # Optional: exponential backoff
            time.sleep(0.000001 * (2 ** min(self.push_retries % 10, 5)))
    
    def pop(self) -> Optional[int]:
        """Lock-free pop with retry loop"""
        while True:
            current_head = self.head
            
            if current_head is None:
                return None
            
            next_node = current_head.next
            
            if self.compare_and_swap(current_head, next_node):
                return current_head.value
            
            # CAS failed, someone else modified head
            self.pop_retries += 1
            # Optional: exponential backoff
            time.sleep(0.000001 * (2 ** min(self.pop_retries % 10, 5)))
    
    def size(self):
        """Get approximate size (not thread-safe, for debugging)"""
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

class LockedStack:
    """Traditional stack with lock for comparison"""
    def __init__(self):
        self.head = None
        self.lock = threading.Lock()
    
    def push(self, value):
        with self.lock:
            new_node = Node(value)
            new_node.next = self.head
            self.head = new_node
    
    def pop(self) -> Optional[int]:
        with self.lock:
            if self.head is None:
                return None
            value = self.head.value
            self.head = self.head.next
            return value

# Comprehensive test
def stress_test_stacks():
    print("=== Lock-Free Stack Stress Test ===\n")
    
    # Test configuration
    num_producers = 4
    num_consumers = 4
    items_per_producer = 10000
    
    # Test both implementations
    for stack_type in ["lock-free", "locked"]:
        print(f"Testing {stack_type} stack...")
        
        if stack_type == "lock-free":
            stack = LockFreeStack()
        else:
            stack = LockedStack()
        
        produced_values = []
        consumed_values = []
        produce_lock = threading.Lock()
        consume_lock = threading.Lock()
        
        start_time = time.time()
        
        def producer(producer_id):
            local_produced = []
            for i in range(items_per_producer):
                value = producer_id * items_per_producer + i
                stack.push(value)
                local_produced.append(value)
                
                # Simulate some work
                if i % 1000 == 0:
                    time.sleep(0.001)
            
            with produce_lock:
                produced_values.extend(local_produced)
        
        def consumer():
            local_consumed = []
            empty_attempts = 0
            
            while empty_attempts < 100:  # Stop after 100 consecutive empty pops
                value = stack.pop()
                
                if value is not None:
                    local_consumed.append(value)
                    empty_attempts = 0
                else:
                    empty_attempts += 1
                    time.sleep(0.001)  # Back off when empty
            
            with consume_lock:
                consumed_values.extend(local_consumed)
        
        # Create threads
        threads = []
        
        # Start producers
        for i in range(num_producers):
            t = threading.Thread(target=producer, args=(i,))
            threads.append(t)
            t.start()
        
        # Start consumers
        for i in range(num_consumers):
            t = threading.Thread(target=consumer)
            threads.append(t)
            t.start()
        
        # Wait for producers to finish
        for t in threads[:num_producers]:
            t.join()
        
        # Wait for consumers to finish
        for t in threads[num_producers:]:
            t.join()
        
        elapsed_time = time.time() - start_time
        
        # Verify correctness
        produced_set = set(produced_values)
        consumed_set = set(consumed_values)
        
        print(f"\nResults for {stack_type} stack:")
        print(f"  Time: {elapsed_time:.3f}s")
        print(f"  Produced: {len(produced_values)} items")
        print(f"  Consumed: {len(consumed_values)} items")
        print(f"  Unique produced: {len(produced_set)}")
        print(f"  Unique consumed: {len(consumed_set)}")
        
        # Check for lost values
        lost_values = produced_set - consumed_set
        duplicate_values = [v for v in consumed_values if consumed_values.count(v) > 1]
        
        if lost_values:
            print(f"  ❌ Lost values: {len(lost_values)}")
        else:
            print(f"  ✅ No lost values")
        
        if duplicate_values:
            print(f"  ❌ Duplicate values: {len(set(duplicate_values))}")
        else:
            print(f"  ✅ No duplicate values")
        
        if hasattr(stack, 'push_retries'):
            print(f"  Push retries: {stack.push_retries}")
            print(f"  Pop retries: {stack.pop_retries}")
            retry_rate = (stack.push_retries + stack.pop_retries) / (len(produced_values) + len(consumed_values))
            print(f"  Retry rate: {retry_rate:.2%}")
        
        print()

# ABA Problem demonstration
def demonstrate_aba_problem():
    print("\n=== ABA Problem Demonstration ===\n")
    
    stack = LockFreeStack()
    
    # Initial state: Stack contains [A]
    stack.push("A")
    print("Initial stack: [A]")
    
    def thread1_operation():
        print("Thread 1: Reading head (sees A)")
        head = stack.head  # Reads A
        
        print("Thread 1: Sleeping (context switch)...")
        time.sleep(0.1)  # Context switch
        
        print("Thread 1: Attempting CAS(A, None) for pop")
        # This will succeed even though stack state changed!
        success = stack.compare_and_swap(head, head.next)
        if success:
            print("Thread 1: ✅ CAS succeeded (but shouldn't have!)")
        else:
            print("Thread 1: ❌ CAS failed (correct behavior)")
    
    def thread2_operation():
        time.sleep(0.01)  # Let thread 1 read
        
        print("Thread 2: Pop A")
        stack.pop()  # Stack is now empty
        
        print("Thread 2: Push B")
        stack.push("B")  # Stack is [B]
        
        print("Thread 2: Push A")  
        stack.push("A")  # Stack is [A, B]
        
        print("Thread 2: Stack is now [A, B]")
    
    t1 = threading.Thread(target=thread1_operation)
    t2 = threading.Thread(target=thread2_operation)
    
    t1.start()
    t2.start()
    
    t1.join()
    t2.join()
    
    print("\nFinal stack state:")
    current = stack.head
    while current:
        print(f"  {current.value}")
        current = current.next
    
    print("\nNote: The ABA problem occurred because Thread 1's CAS succeeded")
    print("even though the stack changed from [A] to [A,B] between read and CAS.")

# Run tests
stress_test_stacks()
demonstrate_aba_problem()
```

</details>

## Exercise 4: Producer-Consumer Queue

### 🔧 Try This: Implement Thread-Safe Queue

```python
import threading
import time
import queue

class BoundedQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
    
    def put(self, item):
        """
        TODO: Implement blocking put
        - Wait if queue is full
        - Add item
        - Signal not_empty
        """
        pass
    
    def get(self):
        """
        TODO: Implement blocking get
        - Wait if queue is empty
        - Remove and return item
        - Signal not_full
        """
        pass

# Exercise: Implement producer-consumer pattern
def producer_consumer_test():
    q = BoundedQueue(capacity=10)
    
    # TODO: Create multiple producers and consumers
    # Verify no items are lost
    # Measure throughput
    # Test with different production/consumption rates
```

<details>
<summary>Solution</summary>

```python
import threading
import time
import queue
import random
from statistics import mean, stdev

class BoundedQueue:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []
        self.lock = threading.Lock()
        self.not_full = threading.Condition(self.lock)
        self.not_empty = threading.Condition(self.lock)
        
        # Metrics
        self.total_puts = 0
        self.total_gets = 0
        self.wait_times_put = []
        self.wait_times_get = []
    
    def put(self, item, timeout=None):
        """Blocking put with optional timeout"""
        start_wait = time.time()
        
        with self.lock:
            # Wait while queue is full
            while len(self.items) >= self.capacity:
                if timeout is not None:
                    remaining = timeout - (time.time() - start_wait)
                    if remaining <= 0:
                        raise queue.Full("Put timed out")
                    if not self.not_full.wait(remaining):
                        raise queue.Full("Put timed out")
                else:
                    self.not_full.wait()
            
            # Add item
            self.items.append(item)
            self.total_puts += 1
            
            wait_time = time.time() - start_wait
            if wait_time > 0.001:  # Only record significant waits
                self.wait_times_put.append(wait_time)
            
            # Signal that queue is not empty
            self.not_empty.notify()
    
    def get(self, timeout=None):
        """Blocking get with optional timeout"""
        start_wait = time.time()
        
        with self.lock:
            # Wait while queue is empty
            while len(self.items) == 0:
                if timeout is not None:
                    remaining = timeout - (time.time() - start_wait)
                    if remaining <= 0:
                        raise queue.Empty("Get timed out")
                    if not self.not_empty.wait(remaining):
                        raise queue.Empty("Get timed out")
                else:
                    self.not_empty.wait()
            
            # Remove and return item
            item = self.items.pop(0)
            self.total_gets += 1
            
            wait_time = time.time() - start_wait
            if wait_time > 0.001:  # Only record significant waits
                self.wait_times_get.append(wait_time)
            
            # Signal that queue is not full
            self.not_full.notify()
            
            return item
    
    def size(self):
        with self.lock:
            return len(self.items)
    
    def get_metrics(self):
        with self.lock:
            return {
                'total_puts': self.total_puts,
                'total_gets': self.total_gets,
                'avg_put_wait': mean(self.wait_times_put) if self.wait_times_put else 0,
                'avg_get_wait': mean(self.wait_times_get) if self.wait_times_get else 0,
                'max_put_wait': max(self.wait_times_put) if self.wait_times_put else 0,
                'max_get_wait': max(self.wait_times_get) if self.wait_times_get else 0,
            }

# Advanced producer-consumer test
def advanced_producer_consumer_test():
    print("=== Advanced Producer-Consumer Test ===\n")
    
    # Test different scenarios
    scenarios = [
        {
            'name': 'Balanced',
            'producers': 4,
            'consumers': 4,
            'produce_rate': 100,  # items/sec
            'consume_rate': 100,  # items/sec
            'queue_size': 20,
            'duration': 5
        },
        {
            'name': 'Fast Producer',
            'producers': 4,
            'consumers': 2,
            'produce_rate': 200,
            'consume_rate': 50,
            'queue_size': 10,
            'duration': 5
        },
        {
            'name': 'Fast Consumer',
            'producers': 2,
            'consumers': 4,
            'produce_rate': 50,
            'consume_rate': 200,
            'queue_size': 10,
            'duration': 5
        },
        {
            'name': 'Bursty',
            'producers': 3,
            'consumers': 3,
            'produce_rate': 'burst',
            'consume_rate': 100,
            'queue_size': 50,
            'duration': 5
        }
    ]
    
    for scenario in scenarios:
        print(f"\n--- Scenario: {scenario['name']} ---")
        print(f"Producers: {scenario['producers']}, Consumers: {scenario['consumers']}")
        print(f"Queue size: {scenario['queue_size']}")
        
        q = BoundedQueue(scenario['queue_size'])
        produced_items = []
        consumed_items = []
        produce_lock = threading.Lock()
        consume_lock = threading.Lock()
        stop_event = threading.Event()
        
        def producer(producer_id):
            local_produced = []
            item_count = 0
            
            while not stop_event.is_set():
                item = f"P{producer_id}-{item_count}"
                
                try:
                    q.put(item, timeout=0.1)
                    local_produced.append(item)
                    item_count += 1
                    
                    # Control production rate
                    if scenario['produce_rate'] == 'burst':
                        # Burst mode: produce 10 items quickly, then pause
                        if item_count % 10 == 0:
                            time.sleep(0.5)
                        else:
                            time.sleep(0.001)
                    else:
                        # Steady rate
                        sleep_time = 1.0 / scenario['produce_rate']
                        time.sleep(sleep_time + random.uniform(-0.01, 0.01))
                        
                except queue.Full:
                    pass  # Queue is full, skip this item
            
            with produce_lock:
                produced_items.extend(local_produced)
        
        def consumer(consumer_id):
            local_consumed = []
            
            while not stop_event.is_set() or q.size() > 0:
                try:
                    item = q.get(timeout=0.1)
                    local_consumed.append(item)
                    
                    # Control consumption rate
                    sleep_time = 1.0 / scenario['consume_rate']
                    time.sleep(sleep_time + random.uniform(-0.01, 0.01))
                    
                except queue.Empty:
                    if stop_event.is_set():
                        break
            
            with consume_lock:
                consumed_items.extend(local_consumed)
        
        # Start threads
        threads = []
        start_time = time.time()
        
        for i in range(scenario['producers']):
            t = threading.Thread(target=producer, args=(i,))
            threads.append(t)
            t.start()
        
        for i in range(scenario['consumers']):
            t = threading.Thread(target=consumer, args=(i,))
            threads.append(t)
            t.start()
        
        # Monitor queue size
        monitor_data = []
        monitor_thread = threading.Thread(
            target=lambda: monitor_queue(q, monitor_data, stop_event)
        )
        monitor_thread.start()
        
        # Run for specified duration
        time.sleep(scenario['duration'])
        stop_event.set()
        
        # Wait for all threads
        for t in threads:
            t.join()
        monitor_thread.join()
        
        elapsed = time.time() - start_time
        
        # Analyze results
        metrics = q.get_metrics()
        produced_set = set(produced_items)
        consumed_set = set(consumed_items)
        
        print(f"\nResults:")
        print(f"  Duration: {elapsed:.1f}s")
        print(f"  Produced: {len(produced_items)} items")
        print(f"  Consumed: {len(consumed_items)} items")
        print(f"  Throughput: {len(consumed_items)/elapsed:.1f} items/sec")
        print(f"  Lost items: {len(produced_set - consumed_set)}")
        print(f"  Duplicate consumption: {len(consumed_items) - len(consumed_set)}")
        
        print(f"\nQueue metrics:")
        print(f"  Avg put wait: {metrics['avg_put_wait']*1000:.1f}ms")
        print(f"  Max put wait: {metrics['max_put_wait']*1000:.1f}ms")
        print(f"  Avg get wait: {metrics['avg_get_wait']*1000:.1f}ms")
        print(f"  Max get wait: {metrics['max_get_wait']*1000:.1f}ms")
        
        if monitor_data:
            sizes = [d['size'] for d in monitor_data]
            print(f"\nQueue utilization:")
            print(f"  Average size: {mean(sizes):.1f}")
            print(f"  Max size: {max(sizes)}")
            print(f"  Min size: {min(sizes)}")
            print(f"  Utilization: {mean(sizes)/scenario['queue_size']*100:.1f}%")
    
    print("\n=== Insights ===")
    print("1. Fast producers cause put waits and full queue")
    print("2. Fast consumers cause get waits and empty queue")
    print("3. Balanced systems have minimal wait times")
    print("4. Bursty traffic needs larger buffers")

def monitor_queue(q, data, stop_event):
    """Monitor queue size over time"""
    while not stop_event.is_set():
        data.append({
            'time': time.time(),
            'size': q.size()
        })
        time.sleep(0.1)

# Deadlock-free multi-queue transfer
def multi_queue_transfer_test():
    print("\n\n=== Multi-Queue Transfer Test ===\n")
    
    # Create multiple queues
    queues = [BoundedQueue(10) for _ in range(4)]
    
    def transfer_between_queues(from_q, to_q, count):
        """Transfer items between queues without deadlock"""
        transferred = 0
        
        for _ in range(count):
            try:
                # Use timeouts to prevent deadlock
                item = from_q.get(timeout=0.1)
                try:
                    to_q.put(item, timeout=0.1)
                    transferred += 1
                except queue.Full:
                    # Put it back if destination is full
                    from_q.put(item, timeout=0.1)
            except queue.Empty:
                pass
        
        return transferred
    
    # Initialize queues with some items
    for i, q in enumerate(queues):
        for j in range(5):
            q.put(f"Q{i}-Item{j}")
    
    print("Initial state:")
    for i, q in enumerate(queues):
        print(f"  Queue {i}: {q.size()} items")
    
    # Create transfer threads
    threads = []
    
    # Circular transfers: 0→1, 1→2, 2→3, 3→0
    for i in range(4):
        from_idx = i
        to_idx = (i + 1) % 4
        t = threading.Thread(
            target=transfer_between_queues,
            args=(queues[from_idx], queues[to_idx], 10)
        )
        threads.append(t)
        t.start()
    
    # Wait for completion
    for t in threads:
        t.join()
    
    print("\nFinal state:")
    for i, q in enumerate(queues):
        print(f"  Queue {i}: {q.size()} items")
    
    print("\nNo deadlock occurred!")

# Run all tests
advanced_producer_consumer_test()
multi_queue_transfer_test()
```

</details>

## Exercise 5: Vector Clocks

### 🔧 Try This: Implement Vector Clock Algorithm

```python
class VectorClock:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = [0] * num_processes
    
    def increment(self):
        """Increment own clock component"""
        # TODO: Implement local event
        pass
    
    def send_event(self):
        """Prepare clock for sending"""
        # TODO: Increment and return copy
        pass
    
    def receive_event(self, other_clock):
        """Update clock on receive"""
        # TODO: Merge clocks and increment
        pass
    
    def happens_before(self, other):
        """Check if self → other"""
        # TODO: Implement happens-before check
        pass
    
    def concurrent_with(self, other):
        """Check if self || other"""
        # TODO: Implement concurrency check
        pass

# Exercise: Simulate distributed system with vector clocks
def simulate_distributed_system():
    # Create 3 processes
    # Simulate message passing
    # Detect causality violations
    pass
```

<details>
<summary>Solution</summary>

```python
import copy
import threading
import time
import random
from collections import deque

class VectorClock:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = [0] * num_processes
        self.lock = threading.Lock()
    
    def increment(self):
        """Increment own clock component for local event"""
        with self.lock:
            self.clock[self.process_id] += 1
            return copy.deepcopy(self.clock)
    
    def send_event(self):
        """Prepare clock for sending (increment first)"""
        with self.lock:
            self.clock[self.process_id] += 1
            return copy.deepcopy(self.clock)
    
    def receive_event(self, other_clock):
        """Update clock on receive (merge then increment)"""
        with self.lock:
            # Take max of each component
            for i in range(len(self.clock)):
                self.clock[i] = max(self.clock[i], other_clock[i])
            # Increment own component
            self.clock[self.process_id] += 1
            return copy.deepcopy(self.clock)
    
    def happens_before(self, other):
        """Check if self → other (self happened before other)"""
        # self → other iff:
        # 1. self[i] <= other[i] for all i
        # 2. self[i] < other[i] for at least one i
        all_leq = all(self.clock[i] <= other[i] for i in range(len(self.clock)))
        exists_less = any(self.clock[i] < other[i] for i in range(len(self.clock)))
        return all_leq and exists_less
    
    def concurrent_with(self, other):
        """Check if self || other (concurrent events)"""
        # self || other iff neither self → other nor other → self
        return not self.happens_before(other) and not other.happens_before(self.clock)
    
    def __str__(self):
        return str(self.clock)
    
    def __repr__(self):
        return f"VC{self.process_id}: {self.clock}"

class Event:
    def __init__(self, process_id, event_type, clock, data=None):
        self.process_id = process_id
        self.event_type = event_type  # 'local', 'send', 'receive'
        self.clock = copy.deepcopy(clock)
        self.data = data
        self.timestamp = time.time()
    
    def __str__(self):
        return f"P{self.process_id} {self.event_type}: {self.clock} - {self.data}"

class DistributedProcess:
    def __init__(self, process_id, num_processes, message_queue):
        self.process_id = process_id
        self.vector_clock = VectorClock(process_id, num_processes)
        self.message_queue = message_queue
        self.events = []
        self.running = True
        
    def local_event(self, data=None):
        """Perform a local computation"""
        clock = self.vector_clock.increment()
        event = Event(self.process_id, 'local', clock, data)
        self.events.append(event)
        print(f"P{self.process_id} local event: {clock} - {data}")
        
    def send_message(self, to_process, data):
        """Send a message to another process"""
        clock = self.vector_clock.send_event()
        event = Event(self.process_id, 'send', clock, f"to P{to_process}: {data}")
        self.events.append(event)
        
        # Put message in the shared queue
        self.message_queue.put({
            'from': self.process_id,
            'to': to_process,
            'clock': clock,
            'data': data
        })
        print(f"P{self.process_id} send to P{to_process}: {clock} - {data}")
        
    def receive_messages(self):
        """Check for and process incoming messages"""
        messages = []
        
        # Collect messages for this process
        temp_queue = deque()
        while not self.message_queue.empty():
            try:
                msg = self.message_queue.get_nowait()
                if msg['to'] == self.process_id:
                    messages.append(msg)
                else:
                    temp_queue.append(msg)
            except:
                break
        
        # Put back messages for other processes
        for msg in temp_queue:
            self.message_queue.put(msg)
        
        # Process received messages
        for msg in messages:
            clock = self.vector_clock.receive_event(msg['clock'])
            event = Event(self.process_id, 'receive', clock, 
                         f"from P{msg['from']}: {msg['data']}")
            self.events.append(event)
            print(f"P{self.process_id} receive from P{msg['from']}: {clock} - {msg['data']}")
    
    def run_scenario(self, scenario_func):
        """Run a specific scenario function"""
        scenario_func(self)

# Simulation scenarios
def simulate_distributed_system():
    print("=== Vector Clock Simulation ===\n")
    
    num_processes = 3
    message_queue = queue.Queue()
    processes = [DistributedProcess(i, num_processes, message_queue) 
                 for i in range(num_processes)]
    
    # Scenario 1: Simple causality chain
    print("--- Scenario 1: Causality Chain ---")
    
    def scenario1():
        # P0: local event, then send to P1
        processes[0].local_event("Start computation")
        time.sleep(0.1)
        processes[0].send_message(1, "Hello P1")
        
        # P1: receive, local event, send to P2
        time.sleep(0.1)
        processes[1].receive_messages()
        processes[1].local_event("Process data")
        processes[1].send_message(2, "Hello P2")
        
        # P2: receive, send back to P0
        time.sleep(0.1)
        processes[2].receive_messages()
        processes[2].send_message(0, "Hello P0")
        
        # P0: receive
        time.sleep(0.1)
        processes[0].receive_messages()
    
    scenario1()
    
    # Analyze causality
    print("\nCausality Analysis:")
    all_events = []
    for p in processes:
        all_events.extend(p.events)
    
    # Sort by timestamp for display
    all_events.sort(key=lambda e: e.timestamp)
    
    # Check happens-before relationships
    for i in range(len(all_events)):
        for j in range(i + 1, len(all_events)):
            e1, e2 = all_events[i], all_events[j]
            v1 = VectorClock(0, num_processes)
            v1.clock = e1.clock
            v2 = VectorClock(0, num_processes)
            v2.clock = e2.clock
            
            if v1.happens_before(e2.clock):
                print(f"  {e1.event_type} P{e1.process_id} → {e2.event_type} P{e2.process_id}")
    
    # Scenario 2: Concurrent events
    print("\n--- Scenario 2: Concurrent Events ---")
    
    # Reset
    processes = [DistributedProcess(i, num_processes, message_queue) 
                 for i in range(num_processes)]
    
    def scenario2():
        # P0 and P1 perform local events concurrently
        processes[0].local_event("A")
        processes[1].local_event("B")
        
        # Both send to P2
        processes[0].send_message(2, "From P0")
        processes[1].send_message(2, "From P1")
        
        # P2 receives both
        time.sleep(0.1)
        processes[2].receive_messages()  # Receives both
    
    scenario2()
    
    # Detect concurrent events
    print("\nConcurrency Detection:")
    for p in processes:
        if len(p.events) >= 2:
            e1, e2 = p.events[0], p.events[1]
            v1 = VectorClock(0, num_processes)
            v1.clock = e1.clock
            
            if e1.process_id != e2.process_id:
                if v1.concurrent_with(e2.clock):
                    print(f"  Events are concurrent: P{e1.process_id} || P{e2.process_id}")
    
    # Scenario 3: Causality violation detection
    print("\n--- Scenario 3: Detect Causality Violation ---")
    
    def detect_causality_violation():
        """Simulate a scenario where messages arrive out of order"""
        # P0 sends two messages to P1
        clock1 = processes[0].send_message(1, "Message 1")
        time.sleep(0.01)
        clock2 = processes[0].send_message(1, "Message 2")
        
        # Simulate network delay - Message 2 arrives first
        # In real system, this would be network reordering
        print("\nSimulating network reordering...")
        
        # P1 processes messages
        processes[1].receive_messages()
        
        # Check if causality is preserved
        if processes[1].events:
            received_clocks = [e.clock for e in processes[1].events if e.event_type == 'receive']
            if len(received_clocks) >= 2:
                v1 = VectorClock(0, num_processes)
                v1.clock = received_clocks[0]
                v2 = VectorClock(0, num_processes)
                v2.clock = received_clocks[1]
                
                if v2.happens_before(received_clocks[0]):
                    print("⚠️ Causality violation detected!")
                else:
                    print("✅ Causality preserved despite reordering")
    
    detect_causality_violation()
    
    print("\n=== Summary ===")
    print("Vector clocks enable:")
    print("1. Detecting causality between events")
    print("2. Identifying concurrent events")
    print("3. Ordering events in distributed systems")
    print("4. Detecting causality violations")

# Run the simulation
simulate_distributed_system()
```

</details>

## Challenge Problems

### 1. The Distributed Counter 🔢

Design a distributed counter that:
- Supports increment/decrement from multiple nodes
- Eventually converges to correct value
- Handles network partitions
- No coordination required

Hint: Look into CRDTs (Conflict-free Replicated Data Types)

### 2. The Fair Lock 🎯

Implement a fair distributed lock where:
- Requests are served in order
- No starvation
- Handles node failures
- Minimal coordination

### 3. The Concurrent Skip List 🏃

Build a lock-free skip list supporting:
- Concurrent insert/delete/search
- No global locks
- Linearizable operations
- Good performance under contention

## Summary

!!! success "Key Skills Practiced"
    
    - ✅ Identifying race conditions
    - ✅ Implementing synchronization primitives
    - ✅ Building lock-free data structures
    - ✅ Understanding distributed time
    - ✅ Detecting and preventing deadlocks

## Navigation

!!! tip "Continue Your Journey"
    
    **Next Axiom**: [Axiom 5: Coordination Cost](../axiom-5-coordination/index.md) →
    
    **Back to**: [Concurrency Overview](index.md) | [Examples](examples.md)
    
    **Jump to**: [Concurrency Patterns](../../patterns/concurrency-patterns.md) | [Part II](../../part2-pillars/index.md)