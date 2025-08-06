---
title: Pillars
description: Pillars overview and navigation
---

# The 5 Core Pillars

Foundational concepts for organizing distributed solutions.

## Overview

While the 7 Laws tell us what we cannot do, the 5 Pillars guide us in what we should do. Each pillar represents a fundamental aspect of distribution that must be addressed in any distributed system.

## The Pillars

1. **[Work Distribution](work-distribution/index.md)** - How to divide and coordinate computational tasks
2. **[State Distribution](state-distribution/index.md)** - How to manage and replicate data across nodes
3. **[Truth Distribution](truth-distribution/index.md)** - How to achieve consensus and consistency
4. **[Control Distribution](control-distribution/index.md)** - How to coordinate actions and decisions
5. **[Intelligence Distribution](intelligence-distribution/index.md)** - How to distribute logic and decision-making

## Key Concepts

Each pillar addresses critical questions:

### Work Distribution
- How do we partition tasks?
- How do we balance load?
- How do we handle stragglers?

### State Distribution
- Where does data live?
- How is it replicated?
- How do we handle conflicts?

### Truth Distribution
- What is the source of truth?
- How do we achieve consensus?
- What consistency guarantees do we provide?

### Control Distribution
- Who makes decisions?
- How are actions coordinated?
- What happens during partitions?

### Intelligence Distribution
- Where does logic execute?
- How do we distribute algorithms?
- How do we aggregate insights?

## Pillar Interactions

The pillars are interdependent:
- **Work + State** = Data locality decisions
- **State + Truth** = Consistency models
- **Truth + Control** = Consensus protocols
- **Control + Intelligence** = Autonomous systems
- **All Five** = Complete distributed system

---

*Begin with [Work Distribution](work-distribution/index.md) to understand how to effectively divide computational tasks across your system.*