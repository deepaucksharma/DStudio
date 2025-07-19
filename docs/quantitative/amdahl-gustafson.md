# Amdahl & Gustafson Laws

**The limits of parallelization**

## Amdahl's Law

The speedup of a program using multiple processors is limited by the sequential portion:

```
Speedup = 1 / (s + p/n)

Where:
s = Serial fraction (can't parallelize)
p = Parallel fraction (can parallelize)  
n = Number of processors
s + p = 1
```

**Key Insight**: Serial bottlenecks dominate

## Amdahl's Law Examples

### Example 1: 95% Parallelizable
```
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
```

### Example 2: Web Request Processing
```
Request breakdown:
- Auth check: 10ms (serial)
- Database queries: 90ms (can parallelize)
- Response formatting: 10ms (serial)

Serial fraction = 20ms/110ms = 18%
Max speedup = 1/0.18 = 5.5x

No point in more than 6 parallel queries!
```

### Example 3: Data Pipeline
```
Pipeline stages:
- Read input: 5% (serial - single source)
- Transform: 80% (parallel)
- Aggregate: 10% (partially parallel)
- Write output: 5% (serial - single sink)

Serial fraction = 10%
Max speedup = 10x

Even with 1000 cores, can't exceed 10x
```

## Gustafson's Law

Different perspective: Scale the problem, not just processors

```
Speedup = s + p×n

Where:
s = Serial fraction of parallel execution
p = Parallel fraction
n = Number of processors
```

**Key Insight**: Larger problems often more parallel

## Gustafson's Law Examples

### Example 1: Image Processing
```
Small image (100x100):
- Setup: 10ms (serial)
- Processing: 100ms (parallel)
- Serial fraction: 9%

Large image (1000x1000):
- Setup: 10ms (serial)
- Processing: 10,000ms (parallel)
- Serial fraction: 0.1%

Larger problem → More parallel benefit!
```

### Example 2: Database Analytics
```
Small dataset (1GB):
- Query parsing: 100ms (serial)
- Data scan: 1000ms (parallel)
- Result merge: 100ms (serial)
Serial: 17%

Large dataset (1TB):
- Query parsing: 100ms (serial)
- Data scan: 1,000,000ms (parallel)
- Result merge: 10,000ms (semi-parallel)
Serial: 0.01%

Bigger data = better scaling!
```

## Applying Both Laws

### System Design Decisions

**Amdahl Perspective** (fixed problem):
```
"Our payment processing is 20% serial,
so max speedup is 5x. Don't over-provision."
```

**Gustafson Perspective** (scaled problem):
```
"As we grow, we'll process more payments in 
batches, reducing serial fraction to 2%."
```

### Real Example: Video Encoding
```
Single video (Amdahl):
- Read file: 5% (serial)
- Encode frames: 90% (parallel)
- Write output: 5% (serial)
Max speedup: 10x

Video platform (Gustafson):
- Process 1000s of videos
- Serial overhead amortized
- Near-linear scaling possible
```

## Real-World Implications

### Microservice Decomposition
```
Monolith response time: 1000ms
- Authentication: 50ms
- Business logic: 900ms
- Formatting: 50ms

Microservices (parallel logic):
- Min response time: 100ms (serial parts)
- With 10 services: ~190ms
- 5x speedup achieved
```

### Database Sharding
```
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
```

### MapReduce Jobs
```
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
```

## Optimization Strategies

### Reduce Serial Bottlenecks
```python
# Before:
lock(global_counter)
counter++
unlock(global_counter)

# After:
thread_local_counter++
# Periodic merge
```

### Pipeline Parallelism
```
Instead of: A → B → C → D
Do: A₁ → B₁ → C₁ → D₁
    A₂ → B₂ → C₂ → D₂
    A₃ → B₃ → C₃ → D₃
```

### Data Parallelism
```
Instead of: Process entire dataset
Do: Partition and process chunks
    Merge results
```

### Speculative Execution
```
Can't parallelize decision?
Execute both branches:
- Calculate both paths
- Discard unused result
- Trading compute for latency
```

## Breaking Through Limits

### When Amdahl Seems Limiting
1. **Question serial assumptions**
   - Can authentication be cached?
   - Can I/O be overlapped?
   - Can coordination be relaxed?

2. **Change the problem**
   - Batch processing vs. stream
   - Approximate vs. exact
   - Eventual vs. strong consistency

3. **Hardware solutions**
   - RDMA for network
   - NVMe for storage
   - GPU for compute

### When Gustafson Applies
1. **Batch workloads**
   - More data = better efficiency
   - Fixed overhead amortized

2. **Analytics systems**
   - Queries over larger datasets
   - Parallel algorithms shine

3. **Machine learning**
   - Bigger models need more parallelism
   - Data parallelism scales well

## Practical Guidelines

### Choosing Parallelization Strategy
```
Serial fraction < 5%:
  → Aggressive parallelization worthwhile

Serial fraction 5-20%:
  → Moderate parallelization (4-8x)
  
Serial fraction > 20%:
  → Focus on reducing serial parts first
```

### Investment Decision
```
Current speedup: 4x with 8 cores
Amdahl limit: 10x

Worth doubling cores?
- 16 cores → 5.7x (only 1.7x improvement)
- 32 cores → 7.5x (diminishing returns)

Better investment: Reduce serial fraction
```

## Key Takeaways

1. **Measure serial fraction first** - It determines your ceiling
2. **Consider problem scaling** - Bigger problems parallelize better
3. **Optimize serial parts aggressively** - They dominate at scale
4. **Use both laws** - Amdahl for limits, Gustafson for opportunities
5. **Architecture matters** - Design to minimize serial bottlenecks

Remember: Perfect parallelization is rare. Plan for serial bottlenecks and design systems that scale the problem, not just the processors.