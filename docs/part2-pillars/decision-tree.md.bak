---
title: Decision Tree Walk-Through
description: "Interactive decision tree walkthrough for choosing distributed architectures based on requirements and constraints"
type: pillar
difficulty: intermediate
reading_time: 10 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Decision Tree Walk-Through

## Case Study: Fintech Ledger System Design

### Requirements

```text
- Double-entry bookkeeping
- Immutable audit trail
- Global operations (3 regions)
- 100M transactions/day
- <500ms transaction confirmation
- Zero data loss tolerance
- Regulatory compliance (SOX)
```

### The Decision Journey

```dockerfile
START: Design a ledger system
│
├─Q1: What's the consistency requirement?
│ └─A: ACID for financial integrity
│   └─Decision: Need strong consistency
│
├─Q2: What's the scale requirement?
│ └─A: 100M tx/day = 1,157 tx/sec average
│   └─Decision: Single DB won't scale
│
├─Q3: How to scale with ACID?
│ ├─Option A: Vertical scaling
│ │ └─Limit: Biggest box = 10K tx/sec
│ ├─Option B: Sharding
│ │ └─Problem: Cross-shard transactions
│ └─Option C: Event sourcing
│   └─Decision: Event sourcing + CQRS
│
├─Q4: How to handle global distribution?
│ ├─Option A: Single region, global replicas
│ │ └─Problem: Write latency from Asia
│ ├─Option B: Multi-master
│ │ └─Problem: Conflict resolution
│ └─Option C: Regional aggregation
│   └─Decision: Regional write nodes
│
├─Q5: How to ensure immutability?
│ └─Decision: Append-only event store
│
└─FINAL ARCHITECTURE:
  ├─Regional write nodes (event capture)
  ├─Global event store (Kafka + S3)
  ├─CQRS read models (per query pattern)
  ├─Eventual consistency (seconds)
  └─Point-in-time reconstruction
```

### Implementation Sketch

```python
class FinTechLedger:
    def __init__(self, region):
        self.region = region
        self.event_store = EventStore()
        self.read_store = ReadStore()

    def transfer(self, from_account, to_account, amount):
# 1. Validate (read path)
        if not self.validate_balance(from_account, amount):
            raise InsufficientFunds()

# 2. Create events (write path)
        events = [
            DebitEvent(
                id=uuid4(),
                account=from_account,
                amount=amount,
                timestamp=now(),
                region=self.region
            ),
            CreditEvent(
                id=uuid4(),
                account=to_account,
                amount=amount,
                timestamp=now(),
                region=self.region
            )
        ]

# 3. Persist events (immutable)
        for event in events:
            self.event_store.append(event)

# 4. Update read models (async)
        self.update_projections_async(events)

        return TransferResult(
            status="accepted",
            eventual_consistency_sla="5 seconds"
        )

    def get_balance(self, account, as_of=None):
        if as_of:
# Historical query - replay events
            return self.replay_events_until(account, as_of)
        else:
# Current query - use projection
            return self.read_store.get_balance(account)

    def audit_trail(self, account, start_date, end_date):
# Immutable events provide perfect audit
        events = self.event_store.query(
            account=account,
            date_range=(start_date, end_date)
        )
        return self.format_audit_report(events)
```

### Decision Impact Analysis

```yaml
Decision: Event Sourcing
+ Immutable audit trail ✓
+ Horizontal scalability ✓
+ Regional distribution ✓
- Eventual consistency
- Complex querying
- Storage growth

Mitigation:
- Read models for complex queries
- Archival strategy for old events
- Clear SLAs on consistency windows
```

---

**Next**: [Pillar Checkpoint Exercise →](pillar-checkpoint.md)
