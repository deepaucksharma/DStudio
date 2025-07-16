Page 68: Amdahl & Gustafson Laws
The limits of parallelization
AMDAHL'S LAW
Speedup = 1 / (s + p/n)

Where:
s = Serial fraction (can't parallelize)
p = Parallel fraction (can parallelize)  
n = Number of processors
s + p = 1
Key Insight: Serial bottlenecks dominate
AMDAHL'S LAW EXAMPLES
Example 1: 95% Parallelizable
s = 0.05, p = 0.95

Processors  Speedup    Efficiency
----------  -------    ----------
1           1.0x       100%
2           1.9x       95%
4           3.5x       87%
8           5.9x       74%
16          8.4x       53%
32          10.3x      32%
∞           20x        0%

Even with infinite processors, max speedup = 20x
Example 2: Web Request Processing
Request breakdown:
- Auth check: 10ms (serial)
- Database queries: 90ms (can parallelize)
- Response formatting: 10ms (serial)

Serial fraction = 20ms/110ms = 18%
Max speedup = 1/0.18 = 5.5x

No point in more than 6 parallel queries!
GUSTAFSON'S LAW
Speedup = s + p×n

Different perspective: 
Scale the problem, not just processors
Key Insight: Larger problems often more parallel
GUSTAFSON'S LAW EXAMPLES
Example 1: Image Processing
Small image (100x100):
- Setup: 10ms (serial)
- Processing: 100ms (parallel)
- Serial fraction: 9%

Large image (1000x1000):
- Setup: 10ms (serial)
- Processing: 10,000ms (parallel)
- Serial fraction: 0.1%

Larger problem → More parallel benefit!
APPLYING BOTH LAWS
System Design Decisions
Amdahl Perspective (fixed problem):
"Our payment processing is 20% serial,
so max speedup is 5x. Don't over-provision."
Gustafson Perspective (scaled problem):
"As we grow, we'll process more payments in 
batches, reducing serial fraction to 2%."
REAL-WORLD IMPLICATIONS
Microservice Decomposition
Monolith response time: 1000ms
- Authentication: 50ms
- Business logic: 900ms
- Formatting: 50ms

Microservices (parallel logic):
- Min response time: 100ms (serial parts)
- With 10 services: ~190ms
- 5x speedup achieved
Database Sharding
Single DB query: 100ms

Sharded across 10 nodes:
- Query routing: 5ms (serial)
- Parallel queries: 100ms/10 = 10ms  
- Result merging: 5ms (serial)
- Total: 20ms (5x speedup)

Adding more shards:
- 20 shards: 15ms (6.7x)
- 100 shards: 11ms (9x)
- Diminishing returns
MapReduce Jobs
Job structure:
- Input split: O(n) serial
- Map phase: Perfectly parallel
- Shuffle: O(n log n) partly serial
- Reduce: Partly parallel
- Output merge: O(n) serial

For large datasets:
- Map phase dominates (good scaling)
For small datasets:
- Overhead dominates (poor scaling)
OPTIMIZATION STRATEGIES
Reduce Serial Bottlenecks
Before:
lock(global_counter)
counter++
unlock(global_counter)

After:
thread_local_counter++
// Periodic merge
Pipeline Parallelism
Instead of: A → B → C → D
Do: A₁ → B₁ → C₁ → D₁
    A₂ → B₂ → C₂ → D₂
    A₃ → B₃ → C₃ → D₃
Data Parallelism
Instead of: Process entire dataset
Do: Partition and process chunks
    Merge results