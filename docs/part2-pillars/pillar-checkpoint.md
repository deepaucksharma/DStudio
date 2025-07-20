---
title: Pillar Checkpoint Exercise
description: How would you distribute the chat workload?
```proto
□ Geographic sharding (users by region)
□ Channel-based sharding (rooms/groups)
□ Temporal sharding...
type: pillar
difficulty: intermediate
reading_time: 15 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part II: Pillars](index.md) → **Pillar Checkpoint Exercise**

# Pillar Checkpoint Exercise

## Exercise: Design a Global Chat System

### Requirements

- 10M concurrent users
- <100ms message delivery
- Message history persistence
- Presence (online/offline)
- Read receipts
- Group chats (up to 10K members)
- End-to-end encryption

### Questions

**1. Work Distribution (2 points)**

How would you distribute the chat workload?
```
□ Geographic sharding (users by region)
□ Channel-based sharding (rooms/groups)
□ Temporal sharding (active vs archived)
□ Feature sharding (presence separate)

Your design: ________________
```text
**2. State Distribution (2 points)**

Where does each type of state live?
```
Messages:      [________________]
Presence:      [________________]
User profiles: [________________]
Read receipts: [________________]

Justify your choices: ________________
```text
**3. Truth Distribution (2 points)**

What consistency model for each feature?
```
Message ordering:  [________________]
Read receipts:     [________________]
Presence:          [________________]
User blocks:       [________________]

Trade-offs: ________________
```text
**4. Control Distribution (2 points)**

How do you manage the system?
```
Service discovery: [________________]
Config management: [________________]
Traffic routing:   [________________]
Monitoring:        [________________]
```text
**5. Intelligence Distribution (2 points)**

Where can ML/AI help?
```
□ Spam detection at edge
□ Smart notification batching
□ Predictive caching of contacts
□ Anomaly detection for security
□ Auto-scaling predictions

Your top 2 choices: ________________
```bash
### Design Sketch Section

Draw your architecture showing:
- Regional deployment
- Data flow for messages
- Consistency boundaries
- Failure domains

### Grading Rubric

```
0-4:  Missing key distributed concepts
5-6:  Basic understanding, major gaps
7-8:  Good design, minor issues
9-10: Production-ready thinking
```

---

**Next**: [Failure Vignette Recap →](failure-recap.md)
