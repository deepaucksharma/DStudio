Page 19: Summary Matrix: Axioms ↔ Common Failures
The Failure Pattern Matrix:
Failure Mode         Primary Axiom    Secondary Axioms    Prevention
------------         -------------    ----------------    ----------
Cascade failure      Partial Failure  Capacity, Coord     Circuit breakers
Retry storm         Coordination     Capacity            Backoff, limits
Split brain         Coordination     Partial Failure     Proper consensus
Thundering herd     Capacity         Coordination        Jitter, queuing
Data corruption     Concurrency      Observability       ACID, validation
Slow death          Capacity         Observability       Metrics, alerts
Lost messages       Partial Failure  Observability       Acks, tracing
Clock skew          Coordination     Concurrency         NTP, logical time
Memory leak         Capacity         Human Interface     Monitoring, limits
Config error        Human Interface  Observability       Validation, staging
The Axiom Interaction Effects:
When Axioms Combine:
- Latency + Coordination = Distributed transaction pain
- Capacity + Partial Failure = Cascade failures
- Concurrency + Observability = Heisenbugs
- Cost + Coordination = Expensive consistency
- Human + Partial Failure = Confusion under pressure