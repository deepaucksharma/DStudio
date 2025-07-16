Page 22: PILLAR I – Distribution of Work
Learning Objective: Master the art of spreading computation without spreading complexity.
First Principle of Work Distribution:
Work should flow to where it can be processed most efficiently,
considering:
- Physical location (latency)
- Available capacity
- Required resources
- Failure domains
The Statelessness Imperative:
Stateless Service Properties:
✓ Any request to any instance
✓ Instances interchangeable
✓ Horizontal scaling trivial
✓ Failure recovery simple
✓ Load balancing easy

Stateful Service Properties:
✗ Requests tied to instances
✗ Complex scaling (resharding)
✗ Failure means data loss
✗ Load balancing tricky
✗ Coordination required
Work Distribution Patterns Hierarchy:
Level 1: Random Distribution
- Round-robin
- Random selection
- DNS load balancing
Efficiency: 60-70%

Level 2: Smart Distribution
- Least connections
- Weighted round-robin
- Response time based
Efficiency: 70-85%

Level 3: Affinity-Based
- Session affinity
- Consistent hashing
- Geographic routing
Efficiency: 80-90%

Level 4: Adaptive Distribution
- Predictive routing
- Cost-aware placement
- SLO-based routing
Efficiency: 90-95%
The Autoscaling Mathematics:
Optimal Instance Count = ceil(
    (Arrival Rate × Processing Time) / 
    (Target Utilization)
)

Example:
- Arrival: 1000 requests/second
- Processing: 100ms/request
- Target utilization: 70%

Instances = ceil((1000 × 0.1) / 0.7) = ceil(142.8) = 143
Autoscaling Response Curves:
Instances
    ↑
150 |            ┌─────────── (Overprovisioned)
    |          ╱
100 |        ╱─── (Ideal)
    |      ╱
 50 |    ╱╱ ← (Reactive scaling)
    |  ╱╱
  0 |╱________________________
    0   500   1000   1500  Load (req/s)
Work Distribution Anti-Patterns:

Hot Shard Problem:

Hash(UserID) % N can create:
- Celebrity user → overloaded shard
- Power law distribution → uneven load
Fix: Virtual shards, consistent hashing

Thundering Herd:

All instances start simultaneously:
- Cache empty → database overload
- Health checks → false failures
Fix: Staggered starts, cache priming

Work Duplication:

Multiple workers process same item:
- No coordination → wasted work
- Optimistic locking → conflict storms
Fix: Work stealing, leases
🔧 Try This: Build a Work Stealer
pythonimport time
import random
from multiprocessing import Process, Queue, Value

class WorkStealer:
    def __init__(self, num_workers=4):
        self.work_queue = Queue()
        self.steal_queue = Queue()
        self.completed = Value('i', 0)
        self.workers = []
        
    def worker(self, worker_id, local_queue):
        while True:
            # Try local queue first
            if not local_queue.empty():
                work = local_queue.get()
            # Try stealing if local empty
            elif not self.steal_queue.empty():
                work = self.steal_queue.get()
            else:
                time.sleep(0.01)
                continue
                
            if work is None:
                break
                
            # Simulate work
            time.sleep(random.uniform(0.01, 0.1))
            with self.completed.get_lock():
                self.completed.value += 1
    
    def distribute_work(self, items):
        # Create local queues
        local_queues = [Queue() for _ in range(len(self.workers))]
        
        # Initial distribution
        for i, item in enumerate(items):
            if i < len(items) // 2:
                # First half goes to workers
                local_queues[i % len(self.workers)].put(item)
            else:
                # Second half goes to steal queue
                self.steal_queue.put(item)
        
        # Start workers
        for i, q in enumerate(local_queues):
            p = Process(target=self.worker, args=(i, q))
            p.start()
            self.workers.append(p)
        
        # Wait for completion
        start = time.time()
        while self.completed.value < len(items):
            time.sleep(0.1)
        
        # Cleanup
        for q in local_queues:
            q.put(None)
        for w in self.workers:
            w.join()
            
        return time.time() - start

# Compare with and without work stealing
stealer = WorkStealer()
elapsed = stealer.distribute_work(list(range(100)))
print(f"With work stealing: {elapsed:.2f}s")