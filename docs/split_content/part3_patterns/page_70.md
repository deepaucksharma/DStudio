Page 70: Coordination Cost Models
The hidden tax of distributed systems
2-PHASE COMMIT COSTS
Messages: 3N (prepare, vote, commit)
Rounds: 3
Latency: 3 × RTT
Failure modes: N + 1 (coordinator + participants)

Cost function:
Cost = 3N × message_cost + 3 × RTT × latency_cost
Example Calculation
5 participants across regions:
- Message cost: $0.01 per 1000
- RTT: 100ms
- Latency cost: $1 per second of delay

Per transaction:
Messages: 15 × $0.01/1000 = $0.00015
Latency: 300ms × $1/s = $0.30
Total: ~$0.30 per transaction

At 1M transactions/day: $300,000/day!
PAXOS/RAFT COSTS
Messages per round: 2N (propose + accept)
Rounds (normal): 2
Rounds (conflict): 2 + retries
Leader election: N² messages

Steady state: 2N messages/decision
During failures: N² messages
Cost Optimization
Multi-Paxos batching:
- Single decision: 2N messages
- 100 decisions: 2N + 99 messages
- Amortized: ~1 message per decision
CONSENSUS SCALING COSTS
3 Nodes
Messages: 6 per decision
Network paths: 3
Failure tolerance: 1
Sweet spot for many systems
5 Nodes
Messages: 10 per decision (+67%)
Network paths: 10 (+233%)
Failure tolerance: 2
Common for regional distribution
7 Nodes
Messages: 14 per decision (+133%)
Network paths: 21 (+600%)
Failure tolerance: 3
Usually overkill
COORDINATION PATTERNS COMPARED
Gossip Protocol
Messages: O(log N) average
Convergence: O(log N) rounds
Eventual consistency only

Cost: Low
Speed: Medium
Consistency: Weak
Leader-Based
Messages: N per update
Rounds: 1 (no conflicts)
Single point of failure

Cost: Low
Speed: Fast
Consistency: Strong
Leaderless Quorum
Messages: W + R (write/read quorums)
Rounds: 1 per operation
No SPOF

Cost: Medium
Speed: Medium
Consistency: Tunable
REAL DOLLAR COSTS
Cross-Region Coordination
AWS Data Transfer Pricing:
- Same AZ: $0
- Cross AZ: $0.01/GB
- Cross Region: $0.02/GB

Coordination message: ~1KB
Daily coordination messages: 100M
Daily cost: 100M × 1KB × $0.02/GB = $2,000
Annual: $730,000
Optimization Strategies
1. Hierarchical Coordination
   Global → Regional → Local
   Reduces cross-region messages 90%

2. Batching
   Accumulate changes, coordinate once
   Reduces frequency 99%

3. Regional Affinity
   Keep related data in same region
   Reduces cross-region needs 80%
COORDINATION ELIMINATION
CRDTs (Conflict-free Replicated Data Types)
Coordination cost: $0
Merge complexity: O(1)
Limitations: Specific operations only
Event Sourcing
Coordination: Only for global ordering
Cost: O(1) not O(N)
Trade-off: Complex event merging
Sharding
Coordination: Within shard only
Cost reduction: N-way sharding = N× reduction
Trade-off: Cross-shard operations expensive