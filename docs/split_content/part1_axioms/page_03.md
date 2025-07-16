Page 3: AXIOM 2 – Finite Capacity
Learning Objective: Every resource has a breaking point; find it before production does.
Core Principle Box:
Every system component has finite:
- CPU cycles per second
- Memory bytes
- Network packets/sec  
- Disk IOPS
- Connection pool slots
- Thread count
- Queue depth

Corollary: Infinite scaling is a lie sold by cloud vendors
The Thermodynamics Angle:
"Just as energy cannot be created or destroyed, computational capacity cannot be materialized from nothing. It can only be moved (migration), transformed (optimization), or purchased (scaling)."
🎬 Failure Vignette: Black Friday Database Meltdown
Company: Major retailer, $2B revenue
Date: Black Friday 2021, 6:00 AM EST
Sequence:
  06:00 - Marketing sends "50% off everything" email
  06:01 - 2M users click simultaneously  
  06:02 - API servers scale from 100 to 1000 pods
  06:03 - Each pod opens 10 connections to DB
  06:04 - Database connection limit: 5000
  06:05 - 10,000 connections attempted
  06:06 - Database rejects new connections
  06:07 - Health checks fail, cascading restarts
  06:15 - Site completely down
  08:00 - Manual intervention restores service
  
Loss: $50M in sales, brand damage

Root Cause: Scaled compute, forgot DB connections are finite
Fix: Connection pooling, admission control, backpressure
The Capacity Staircase:
Level 1: Single Server Limits
  - 16 cores = 16 truly parallel operations
  - 64GB RAM = ~1M concurrent user sessions
  - 10Gbps NIC = 1.25GB/sec theoretical max
  
Level 2: Distributed Limits  
  - Coordination overhead eats 20-30% capacity
  - Network becomes the bottleneck
  - Shared storage creates contention
  
Level 3: Planetary Limits
  - Speed of light creates coordination delays
  - CAP theorem forces trade-offs
  - Human operators become bottleneck
🎯 Decision Tree: Scale-Up vs Scale-Out
START: Need more capacity
  │
  ├─ Is workload parallelizable?
  │   ├─ NO → Scale UP (bigger box)
  │   └─ YES → Continue
  │
  ├─ Is data easily partitioned?
  │   ├─ NO → Scale UP + Read replicas
  │   └─ YES → Continue  
  │
  ├─ Can tolerate eventual consistency?
  │   ├─ NO → Scale UP to limits, then shard carefully
  │   └─ YES → Scale OUT (add nodes)
  │
  └─ Result: Your scaling strategy
Capacity Arithmetic:
Effective Capacity = Raw Capacity × Utilization Factor × Efficiency Factor

Where:
- Utilization Factor = 1 - (idle + overhead)
- Efficiency Factor = 1 / (1 + coordination_cost)

Example:
- Raw: 100 CPU cores
- Utilization: 0.7 (30% overhead)
- Efficiency: 0.8 (25% coordination cost)
- Effective: 100 × 0.7 × 0.8 = 56 cores actual work
🔧 Try This: Find Your Breaking Point
bash# Local capacity test (DO NOT RUN IN PROD!)
# Terminal 1: Start a simple server
python -m http.server 8000

# Terminal 2: Find the limit
ab -n 10000 -c 100 http://localhost:8000/
# Watch for the cliff where latency spikes

# Terminal 3: Monitor resources
htop  # Watch CPU, memory
iftop # Watch network
iotop # Watch disk
Real Capacity Limits (2024 numbers):
PostgreSQL:      5000 connections (practical)
Redis:           10K ops/sec/core
Kafka:           1M messages/sec/broker
Load Balancer:   100K concurrent connections
Docker:          ~10K containers/host
Kubernetes:      5000 nodes/cluster
Elasticsearch:   1000 shards/node (recommended)
Counter-Intuitive Truth 💡:
"Running at 100% capacity means you're already over capacity. Systems need breathing room for spikes, garbage collection, and maintenance. Target 60-70% steady-state."
Let me continue with the remaining axioms in the next response...RetryDcontinueEditPlotted continuation of distributed systems book outline meticulously.5sThe user wants me to continue with the comprehensive expansion of the distributed systems book outline. I was in the middle of Part I (Axiom-Based Foundation), having completed pages 1-3. I need to continue with pages 4-20 of Part I, maintaining the same level of detail and first-principles approach.
I should continue with:
