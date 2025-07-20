---
title: Capacity Exercises
description: 1. Calculate the optimal utilization target for different resource types
2. Design a system that gracefully degrades at capacity limits
3. Implemen...
type: axiom
difficulty: beginner
reading_time: 5 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 2](index.md) → **Capacity Exercises**

# Capacity Exercises

## Hands-On Labs

### Lab 1: Queue Simulation
Build and visualize different queue behaviors under varying loads.

### Lab 2: Capacity Planning
Use Little's Law to plan system capacity for given SLAs.

### Lab 3: Load Testing
Observe the utilization cliff in a real system.

### Lab 4: Find Your Breaking Point
Use the provided load testing scripts to discover system limits.

## Challenge Problems

1. Calculate the optimal utilization target for different resource types
2. Design a system that gracefully degrades at capacity limits
3. Implement different queue disciplines and compare their behavior
4. Build a backpressure mechanism with exponential backoff

## Thought Experiments

- What happens when you scale horizontally but forget about shared resources?
- How would you design a system that never hits capacity limits?
- When is it better to drop requests vs queueing them?

*More exercises coming soon*

---

**Previous**: [Examples](examples.md) | **Next**: [Axiom 3](../axiom3-failure/index.md)

**Related**: [Auto Scaling](../../patterns/auto-scaling.md) • [Load Balancing](../../patterns/load-balancing.md) • [Sharding](../../patterns/sharding.md)
