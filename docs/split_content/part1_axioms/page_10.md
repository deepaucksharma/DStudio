Page 10: Coordination Estimator Cheat-Table
Quick Reference Cost Calculator:
Scenario                          Formula                      Example (5 nodes, 50ms RTT)
--------                          -------                      -------------------------
Async fire-and-forget            0                            0ms
Quorum read (majority)           RTT × ceil(N/2)              50ms × 3 = 150ms
Quorum write                     RTT × ceil(N/2)              150ms
Read-your-writes                 RTT × write_replicas         50ms × 3 = 150ms
Linearizable read                RTT × N (worst case)         50ms × 5 = 250ms
2PC transaction                  3 × RTT × N                  3 × 50ms × 5 = 750ms
Paxos/Raft (normal)             2 × RTT                      100ms
Paxos/Raft (leader change)      4 × RTT + election_timeout   200ms + 150ms = 350ms
Chain replication               RTT × N (sequential)          250ms
Byzantine consensus             O(N²) messages                25 × 50ms = 1250ms
Cost Multipliers:

Retries: × (1 + retry_rate)
Failures: + (failure_rate × detection_time)
Monitoring: × 1.1 (10% overhead typical)
Encryption: × 1.05 (TLS overhead)
Compression: × 0.8 (if payload > 1KB)

Let me continue with the remaining axioms in the next response...RetryDcontinueEditPlotted continuation of distributed systems book outline.4sThe user wants me to continue with the comprehensive expansion of the distributed systems book outline. I've covered Axioms 1-5 and their associated pages (1-10). Now I need to continue with:

Axioms 6-8 (pages 11-16)
The synthesis pages (17-20) that wrap up Part I
Then move on to Part II (pages 21-44) about Foundational Pillars & Modern Extensions

I should maintain the same level of detail and first-principles approach throughout.Response 3: PART I Continued - Axioms 6-8 and Synthesis (Pages 11-20)