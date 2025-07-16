Page 69: Universal Scalability Law
Why systems don't scale linearly
THE USL EQUATION
C(N) = N / (1 + α(N-1) + βN(N-1))

Where:
C(N) = Capacity at N nodes
α = Contention parameter (serialization)
β = Coherency parameter (coordination)
N = Number of nodes
THREE SCALING REGIMES
1. Linear Scaling (α=0, β=0)
Perfect world: 2x nodes = 2x capacity
Reality: Never happens
Example: Embarrassingly parallel batch jobs
2. Contention-Limited (α>0, β=0)
Shared resource bottleneck
Example: Database lock contention
Shape: Approaches horizontal asymptote
3. Coherency-Limited (α>0, β>0)
Coordination overhead dominates
Example: Distributed consensus
Shape: Performance DECREASES after peak
MEASURING YOUR PARAMETERS
Data Collection
Nodes  Throughput   Relative
-----  ----------   --------
1      1000 req/s   1.0
2      1900 req/s   1.9
4      3400 req/s   3.4
8      5200 req/s   5.2
16     6400 req/s   6.4
32     5800 req/s   5.8  ← Performance degraded!
Parameter Fitting
Using regression or optimization:
α ≈ 0.03 (3% serialization)
β ≈ 0.0008 (0.08% coordination cost)

Peak performance at: N = sqrt((1-α)/β) ≈ 35 nodes
REAL-WORLD EXAMPLES
Database Replication
Read replicas scaling:
- Contention: Connection pool limits
- Coherency: Replication lag monitoring

Typical values:
α = 0.05 (5% management overhead)
β = 0.001 (0.1% cross-replica coordination)
Peak: ~30 replicas
Microservice Mesh
Service-to-service calls:
- Contention: Service discovery lookups
- Coherency: Health checking, N² connections

Typical values:
α = 0.1 (10% discovery overhead)
β = 0.01 (1% health check storms)
Peak: ~10 services before degradation
Distributed Cache
Cache nodes:
- Contention: Hash ring updates
- Coherency: Cache invalidation broadcasts

Typical values:
α = 0.02 (2% ring management)
β = 0.0001 (0.01% invalidation)
Peak: ~100 nodes practical limit
OPTIMIZATION STRATEGIES
Reduce α (Contention)
- Eliminate shared locks
- Partition resources
- Local caches
- Optimistic concurrency
Reduce β (Coherency)
- Eventual consistency
- Hierarchical coordination
- Gossip protocols
- Reduce broadcast storms
CAPACITY PLANNING WITH USL
Scenario Analysis
Current: 10 nodes, 8000 req/s
Target: 16000 req/s

USL prediction:
20 nodes → 12000 req/s (not enough)
30 nodes → 14500 req/s (not enough)
40 nodes → 15200 req/s (degrading)

Conclusion: Need architectural change
Break the Bottleneck
Options:
1. Shard the workload (multiple USL curves)
2. Reduce coordination (lower β)
3. Async processing (lower α)
4. Caching layer (offload entirely)