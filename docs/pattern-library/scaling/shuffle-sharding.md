---
title: Shuffle Sharding
description: Isolation technique to prevent cascade failures
---

# Shuffle Sharding

## Overview

Shuffle sharding creates isolated failure domains by randomly assigning resources to customers, preventing one customer's issue from affecting all others.

## How It Works

Instead of traditional sharding where customers map to specific shards, shuffle sharding assigns each customer a random subset of shards.

### Traditional Sharding
```
Customer A → Shard 1
Customer B → Shard 2
Customer C → Shard 3
```

### Shuffle Sharding
```
Customer A → Shards [1, 3, 5, 7]
Customer B → Shards [2, 4, 6, 8]
Customer C → Shards [1, 2, 7, 8]
```

## Implementation

```python
import hashlib
import random

class ShuffleShardRouter:
    def __init__(self, total_shards: int, shards_per_customer: int):
        self.total_shards = total_shards
        self.shards_per_customer = shards_per_customer
    
    def get_shards(self, customer_id: str) -> List[int]:
        """Get deterministic random shards for customer"""
        # Seed with customer ID for consistency
        random.seed(hashlib.md5(customer_id.encode()).hexdigest())
        
        # Select random subset of shards
        shards = random.sample(
            range(self.total_shards), 
            self.shards_per_customer
        )
        
        return sorted(shards)
    
    def route_request(self, customer_id: str) -> int:
        """Route to one of customer's shards"""
        shards = self.get_shards(customer_id)
        # Could use round-robin, random, or load-based selection
        return random.choice(shards)
```

## Isolation Guarantees

With shuffle sharding, the probability of two customers sharing all the same shards is extremely low:

- 8 total shards, 2 per customer: 28 possible combinations
- 100 total shards, 5 per customer: ~75 million combinations

## Use Cases

- **Multi-tenant systems**: Isolate tenant failures
- **API rate limiting**: Prevent one customer affecting others
- **Database connection pools**: Isolate noisy neighbors
- **Cache partitions**: Prevent cache pollution

## Trade-offs

### Advantages
- Strong isolation between customers
- Prevents cascade failures
- Maintains redundancy per customer
- Scales with shard count

### Disadvantages
- More complex than simple sharding
- Requires more total resources
- Load balancing more difficult
- Debugging can be challenging

## Related Patterns

- [Bulkhead Pattern](../resilience/bulkhead.md)
- [Cell-Based Architecture](../architecture/cell-based.md)
- [Consistent Hashing](../data-management/consistent-hashing.md)

