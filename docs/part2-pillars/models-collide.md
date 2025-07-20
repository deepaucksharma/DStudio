---
title: When Models Collide
description: "Exploring conflicts between different distributed system models and approaches"
type: pillar
difficulty: intermediate
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part II: Pillars](index.md) → **When Models Collide**

# When Models Collide

**Learning Objective**: Real systems don't fit neatly into models; learn to handle the mess.

## Case Study: Stripe's Dual-Region Architecture

### The Challenge

```text
Requirements:
1. <100ms latency globally (Axiom 1)
2. 99.999% availability (Axiom 3)
3. Strict consistency for payments (Pillar 3)
4. Cost effective (Axiom 8)

Conflict: Can't have all four!
```

### The Hybrid Solution

```text
┌─────────────── US-WEST ───────────────┐
│  ┌─────────────────────────────────┐  │
│  │   Primary Payment Database       │  │
│  │   (Strongly Consistent)          │  │
│  └──────────────┬──────────────────┘  │
│                 │                      │
│  ┌──────────────▼──────────────────┐  │
│  │   Read Replicas (Eventual)      │  │
│  └─────────────────────────────────┘  │
└────────────────┬───────────────────────┘
                 │ Cross-region
                 │ replication
┌────────────────▼───────────────────────┐
│  ┌─────────────────────────────────┐  │
│  │   Hot Standby Database          │  │
│  │   (Async replication)           │  │
│  └──────────────┬──────────────────┘  │
│                 │                      │
│  ┌──────────────▼──────────────────┐  │
│  │   Read Replicas (Eventual)      │  │
│  └─────────────────────────────────┘  │
└──────────────── US-EAST ──────────────┘
```

## The Model Collision Points

### 1. CAP Theorem says: Pick 2 of 3
- **Reality**: Different choices for different operations
- Payments: CP (consistent, partition-tolerant)
- Analytics: AP (available, partition-tolerant)

### 2. ACID says: All or nothing transactions
- **Reality**: Saga pattern with compensation
- Begin transaction in primary
- Prepare in secondary
- Commit in primary
- Eventual commit in secondary

### 3. Latency says: Can't beat physics
- **Reality**: Cache the uncacheable
- Merchant settings: Cached with TTL
- Payment tokens: Pre-validated
- Risk scores: Computed async

## The Actual Architecture

```python
class StripePaymentFlow:
    def __init__(self):
        self.primary_db = Database("us-west", consistency="strong")
        self.secondary_db = Database("us-east", consistency="async")
        self.cache = Cache(ttl=300)

    def process_payment(self, payment):
        # 1. Quick risk check (cached)
        risk_score = self.cache.get(f"risk:{payment.merchant_id}")
        if not risk_score:
            risk_score = self.compute_risk(payment.merchant_id)
            self.cache.set(f"risk:{payment.merchant_id}", risk_score)

        if risk_score > 0.8:
            return self.decline_high_risk(payment)

        # 2. Idempotency check (both regions)
        if self.is_duplicate(payment.idempotency_key):
            return self.get_previous_result(payment.idempotency_key)

        # 3. Payment processing (primary region)
        try:
            result = self.primary_db.transaction(
                lambda tx: self.execute_payment(tx, payment)
            )

            # 4. Async replicate to secondary
            self.replicate_async(payment, result)

            return result

        except NetworkPartition:
            # 5. Fallback to secondary (degraded mode)
            if payment.amount < 10000:  # Small payments only
                return self.secondary_db.transaction(
                    lambda tx: self.execute_payment_degraded(tx, payment)
                )
            else:
                return PaymentResult(
                    status="retry_later",
                    message="High-value payments temporarily unavailable"
                )

    def execute_payment(self, tx, payment):
        # Strong consistency path
        tx.debit(payment.source, payment.amount)
        tx.credit(payment.destination, payment.amount)
        tx.log_transaction(payment)
        return PaymentResult(status="success")

    def execute_payment_degraded(self, tx, payment):
        # Eventual consistency path
        # Log intent, process async
        tx.log_intent(payment)
        self.queue_for_reconciliation(payment)
        return PaymentResult(
            status="processing",
            message="Payment will be processed within 5 minutes"
        )
```

## Lessons from Model Collisions

1. **Models are guides, not laws**: Reality requires compromise
2. **Different data, different rules**: Not everything needs strong consistency
3. **Degraded > Down**: Accept reduced functionality over unavailability
4. **Cost is a feature**: Sometimes "good enough" is perfect
5. **Monitor the boundaries**: Where models meet is where failures hide

---

**Next**: [Pattern Interconnection Matrix →](pattern-matrix.md)
