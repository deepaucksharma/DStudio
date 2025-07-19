# Coordination Cost Models

**The hidden tax of distributed systems**

## 2-Phase Commit Costs

The classic distributed transaction protocol:

```
Messages: 3N (prepare, vote, commit)
Rounds: 3
Latency: 3 × RTT
Failure modes: N + 1 (coordinator + participants)

Cost function:
Cost = 3N × message_cost + 3 × RTT × latency_cost
```

### Example Calculation
```
5 participants across regions:
- Message cost: $0.01 per 1000
- RTT: 100ms
- Latency cost: $1 per second of delay

Per transaction:
Messages: 15 × $0.01/1000 = $0.00015
Latency: 300ms × $1/s = $0.30
Total: ~$0.30 per transaction

At 1M transactions/day: $300,000/day!
```

## Paxos/Raft Costs

Modern consensus protocols:

```
Messages per round: 2N (propose + accept)
Rounds (normal): 2
Rounds (conflict): 2 + retries
Leader election: N² messages

Steady state: 2N messages/decision
During failures: N² messages
```

### Cost Optimization
```
Multi-Paxos batching:
- Single decision: 2N messages
- 100 decisions: 2N + 99 messages
- Amortized: ~1 message per decision

Massive improvement through batching!
```

## Consensus Scaling Costs

### 3 Nodes
```
Messages: 6 per decision
Network paths: 3
Failure tolerance: 1
Sweet spot for many systems
```

### 5 Nodes
```
Messages: 10 per decision (+67%)
Network paths: 10 (+233%)
Failure tolerance: 2
Common for regional distribution
```

### 7 Nodes
```
Messages: 14 per decision (+133%)
Network paths: 21 (+600%)
Failure tolerance: 3
Usually overkill
```

### 9+ Nodes
```
Messages: O(N) per decision
Network paths: O(N²)
Coordination overhead dominates
Rarely justified
```

## Coordination Patterns Compared

### Gossip Protocol
```
Messages: O(log N) average
Convergence: O(log N) rounds
Eventual consistency only

Cost: Low
Speed: Medium
Consistency: Weak

Best for: Membership, failure detection
```

### Leader-Based
```
Messages: N per update
Rounds: 1 (no conflicts)
Single point of failure

Cost: Low
Speed: Fast
Consistency: Strong

Best for: Stable environments
```

### Leaderless Quorum
```
Messages: W + R (write/read quorums)
Rounds: 1 per operation
No SPOF

Cost: Medium
Speed: Medium
Consistency: Tunable

Best for: Geographic distribution
```

### Byzantine Consensus
```
Messages: O(N²) per round
Rounds: Multiple
Tolerates malicious nodes

Cost: Very High
Speed: Slow
Consistency: Strong

Best for: Untrusted environments
```

## Real Dollar Costs

### Cross-Region Coordination
```
AWS Data Transfer Pricing:
- Same AZ: $0
- Cross AZ: $0.01/GB
- Cross Region: $0.02/GB

Coordination message: ~1KB
Daily coordination messages: 100M
Daily cost: 100M × 1KB × $0.02/GB = $2,000
Annual: $730,000
```

### Optimization Strategies
```
1. Hierarchical Coordination
   Global → Regional → Local
   Reduces cross-region messages 90%

2. Batching
   Accumulate changes, coordinate once
   Reduces frequency 99%

3. Regional Affinity
   Keep related data in same region
   Reduces cross-region needs 80%
```

## Coordination Elimination

### CRDTs (Conflict-free Replicated Data Types)
```
Coordination cost: $0
Merge complexity: O(1)
Limitations: Specific operations only

Example: Distributed counter
Each node increments locally
Merge: Sum all counters
No coordination needed!
```

### Event Sourcing
```
Coordination: Only for global ordering
Cost: O(1) not O(N)
Trade-off: Complex event merging

Example: Bank transactions
Each transaction is an event
Apply in any order (commutative)
```

### Sharding
```
Coordination: Within shard only
Cost reduction: N-way sharding = N× reduction
Trade-off: Cross-shard operations expensive

Example: User data by ID
Each shard handles range
No cross-shard coordination
```

## Hidden Coordination Costs

### Service Discovery
```
Naive: Every service polls registry
- N services × M queries/sec
- Registry becomes bottleneck

Better: Local caching + push updates
- Reduces queries 100x
- Adds staleness risk
```

### Health Checking
```
Full mesh: N² health checks
- 100 services = 10,000 checks/interval
- Network saturation

Hierarchical: O(N log N)
- Regional aggregators
- Reduced traffic
```

### Configuration Management
```
Push to all: O(N) messages
- Config change → N updates
- Thundering herd on changes

Pull with jitter: Smoothed load
- Random interval pulls
- Natural load distribution
```

## Cost-Aware Architecture

### Minimize Coordination Scope
```python
# Bad: Global coordination
def transfer_money(from_account, to_account, amount):
    with distributed_lock("global"):
        debit(from_account, amount)
        credit(to_account, amount)

# Better: Account-level coordination  
def transfer_money(from_account, to_account, amount):
    # Only coordinate affected accounts
    with multi_lock([from_account, to_account]):
        debit(from_account, amount)
        credit(to_account, amount)
```

### Async When Possible
```python
# Expensive: Synchronous consensus
def update_all_replicas(data):
    futures = []
    for replica in replicas:
        futures.append(replica.update(data))
    wait_all(futures)  # Blocks on slowest

# Cheaper: Async replication
def update_all_replicas(data):
    for replica in replicas:
        async_send(replica, data)
    # Return immediately
```

### Batch Coordination
```python
# Expensive: Coordinate per operation
for update in updates:
    coordinate_update(update)  # 3N messages each

# Cheaper: Batch coordination
coordinate_batch(updates)  # 3N messages total
```

## Monitoring Coordination Costs

### Key Metrics
1. **Messages per operation** - Direct cost indicator
2. **Coordination latency** - User-visible impact
3. **Failed coordinations** - Retry amplification
4. **Network bandwidth** - Infrastructure cost

### Cost Dashboard
```
Coordination Cost Metrics:
- 2PC transactions: 50K/day @ $0.30 = $15K/day
- Raft consensus: 1M/day @ $0.02 = $20K/day  
- Health checks: 100M/day @ $0.001 = $100/day
- Config updates: 10K/day @ $0.10 = $1K/day
Total: $36K/day = $13M/year
```

## Key Takeaways

1. **Coordination is expensive** - Both in latency and dollars
2. **Batching is powerful** - Amortize fixed costs
3. **Hierarchy reduces N²** - Tree structures scale better
4. **Eliminate when possible** - CRDTs, sharding, eventual consistency
5. **Measure actual costs** - Hidden coordination adds up

Remember: The best coordination is no coordination. When you must coordinate, do it efficiently.