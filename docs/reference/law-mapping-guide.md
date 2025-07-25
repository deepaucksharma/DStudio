---
title: "Law Framework Transition Guide"
description: A comprehensive mapping guide for transitioning from the old 8-axiom structure to the new 7-law framework
type: reference
status: complete
last_updated: 2025-07-23
---

# Law Framework Transition Guide
## From 8 Simple Laws to 7 Fundamental Laws

This guide helps users familiar with the original 8-law framework navigate to the new 7-law structure. The new framework provides deeper theoretical foundations while maintaining practical applicability.

## Quick Reference Mapping

<div class="responsive-table" markdown>

| Old Law (8-Law Framework) | New Law (7-Law Framework) | Key Changes |
|-------------------------------|---------------------------|-------------|
| **1. Latency** 🏃‍♂️<br/>*Speed of light limits* | **2. Law of Asynchronous Reality** ⏳<br/>*Information travels at finite speed* | Expanded beyond just latency to include temporal uncertainty, information theory limits, and partial ordering |
| **2. Finite Capacity** 📦<br/>*All resources have limits* | **Merged into multiple laws** | Capacity constraints now appear in trade-offs (Law 4) and emergence (Law 3) |
| **3. Inevitable Failure** 💥<br/>*Components fail independently* | **1. Law of Correlated Failure** ⛓️<br/>*Components fail together* | Elevated to first position, focuses on correlated rather than independent failures |
| **4. Concurrency Complexity** 🔀<br/>*Multiple operations happen* | **3. Law of Emergent Chaos** 🌪️<br/>*Scale creates unpredictability* | Concurrency is now part of emergent complexity at scale |
| **5. Coordination Costs** 🤝<br/>*Agreement requires communication* | **4. Law of Multidimensional Optimization** ⚖️<br/>*n-dimensional trade-off space* | Coordination is one dimension in a larger optimization space |
| **6. Limited Observability** 👁️<br/>*Can't see everything* | **5. Law of Distributed Knowledge** 🧠<br/>*Truth is local, certainty expensive* | Reframed as epistemology - what can be known in distributed systems |
| **7. Human Interface** 👤<br/>*Humans interact with systems* | **6. Law of Cognitive Load** 🤯<br/>*Complexity must fit human limits* | Deeper focus on mental models and cognitive constraints |
| **8. Economic Reality** 💰<br/>*Systems have costs* | **7. Law of Economic Reality** 💰<br/>*Every decision is financial* | Enhanced with TCO, opportunity cost, and FinOps principles |

</div>


## Detailed Mapping and Evolution

### Old Law 1: Latency → New Law 2: Asynchronous Reality

**What changed:**
- **Scope**: Expanded from just communication delays to the fundamental impossibility of knowing "now"
- **Theory**: Added FLP impossibility theorem, Lamport's happens-before, Shannon's information theory
- **Focus**: Shifted from measuring latency to reasoning about temporal uncertainty

**Key concepts added:**
- Information-theoretic limits on communication
- Formal temporal logic and partial ordering
- The unknowability of the present in distributed systems

**Find it here:** [Law of Asynchronous Reality](/part1-axioms/law2-asynchrony/)

### Old Law 2: Finite Capacity → Distributed Across Multiple Laws

**What changed:**
- **Integration**: Capacity constraints now appear as aspects of other laws rather than standalone
- **Context**: Capacity limits manifest differently in different contexts

**Where to find capacity concepts:**
- **In Law 3 (Emergent Chaos)**: How capacity limits trigger phase transitions
- **In Law 4 (Trade-offs)**: Capacity as one dimension in optimization space
- **In Law 7 (Economics)**: Capacity planning as economic decision

### Old Law 3: Failure → New Law 1: Failure

**What changed:**
- **Priority**: Elevated to first position as the most fundamental constraint
- **Sophistication**: Moved beyond simple fail-stop to correlated, gray, and metastable failures
- **Theory**: Added dependency graph analysis, blast radius calculations

**Key concepts added:**
- Correlated failures from shared dependencies
- Gray failures (partial degradation)
- Metastable failure states
- Cascading failure analysis

**Find it here:** [Law of Correlated Failure](/part1-axioms/law1-failure/)

### Old Law 4: Concurrency → New Law 3: Emergence

**What changed:**
- **Scope**: Concurrency is now one source of emergent complexity
- **Theory**: Added complexity theory, phase transitions, self-organized criticality
- **Focus**: From managing concurrency to understanding emergent behaviors

**Key concepts added:**
- State space explosion at scale
- Non-linear dynamics and tipping points
- Chaos engineering as a response to emergence

**Find it here:** [Law of Emergent Chaos](/part1-axioms/law3-emergence/)

### Old Law 5: Coordination → New Law 4: Trade-offs

**What changed:**
- **Perspective**: Coordination cost is one dimension in a larger trade-off space
- **Sophistication**: Moved beyond CAP theorem to n-dimensional optimization
- **Models**: Added harvest/yield, consistency models spectrum

**Key concepts added:**
- Multi-objective optimization theory
- Non-linear trade-off surfaces
- Context-dependent optimization

**Find it here:** [Law of Multidimensional Optimization](/part1-axioms/law4-tradeoffs/)

### Old Law 6: Observability → New Law 5: Epistemology

**What changed:**
- **Philosophy**: Reframed as epistemology - what can be known
- **Theory**: Added formal knowledge logic, Byzantine epistemology
- **Depth**: Distinguishes belief, knowledge, and common knowledge

**Key concepts added:**
- Levels of distributed knowledge
- Probabilistic certainty (Bloom filters, HyperLogLog)
- The cost of certainty in distributed systems

**Find it here:** [Law of Distributed Knowledge](/part1-axioms/law5-epistemology/)

### Old Law 7: Human Interface → New Law 6: Human-API

**What changed:**
- **Focus**: From generic human factors to specific cognitive constraints
- **Application**: Mental models, error design, incident response
- **Theory**: Added cognitive science principles, 7±2 rule

**Key concepts added:**
- Mental model accuracy requirements
- Cognitive load of different consistency models
- Observability as user interface design

**Find it here:** [Law of Cognitive Load](/part1-axioms/law6-human-api/)

### Old Law 7: Economics → New Law 7: Economics

**What changed:**
- **Depth**: Enhanced with TCO, opportunity cost, build vs buy analysis
- **Integration**: Links architectural decisions directly to financial impact
- **Modern concepts**: Added FinOps, cloud economics, performance per dollar

**Key concepts added:**
- Total Cost of Ownership modeling
- Economic modeling of architectural choices
- Cost-aware system design

**Find it here:** [Law of Economic Reality](/part1-axioms/law7-economics/)

## Why the Framework Was Restructured

### 1. **From Description to Foundation**
The old framework described observable phenomena. The new framework identifies fundamental laws from which these phenomena emerge.

### 2. **From Independence to Interaction**
The old laws were presented as independent facts. The new laws explicitly acknowledge their deep interconnections.

### 3. **From Simplification to Nuance**
The old framework prioritized accessibility. The new framework embraces complexity while remaining practical.

### 4. **From Observation to Theory**
The old laws were empirical observations. The new laws are grounded in formal theory from multiple disciplines.

## Key Conceptual Differences

### Old Framework Mindset
- "Here are 8 things that make distributed systems hard"
- Each law is a separate challenge
- Focus on individual problems
- Practical patterns for each law

### New Framework Mindset
- "Here are 7 fundamental laws governing all distributed systems"
- Laws interact to create complex behaviors
- Focus on systemic understanding
- Theoretical foundations inform practice

## Migration Tips for Different Audiences

### For Engineers Using the Old Framework
1. Your understanding remains valid - the new framework builds on it
2. Start with the laws that map directly to laws you use most
3. Explore the new emergent complexity concepts in Law 3
4. Pay attention to the theoretical foundations sections

### For Educators and Trainers
1. The old framework remains excellent for introduction
2. Use the new framework for advanced courses
3. The mapping guide helps create learning progressions
4. Consider teaching both as "levels" of understanding

### For System Architects
1. The multidimensional trade-off model (Law 4) revolutionizes design decisions
2. Correlated failure analysis (Law 1) improves reliability planning
3. Economic modeling (Law 7) helps justify architectural choices
4. Cognitive load (Law 6) informs API and tool design

## Quick Navigation

### If you're looking for content on...

- **Latency, RTT, speed of light** → [Law 2: Asynchronous Reality](/part1-axioms/law2-asynchrony/)
- **Capacity planning, limits** → [Law 4: Trade-offs](/part1-axioms/law4-tradeoffs/) and [Law 7: Economics](/part1-axioms/law7-economics/)
- **Failure modes, fault tolerance** → [Law 1: Failure](/part1-axioms/law1-failure/)
- **Race conditions, concurrency** → [Law 3: Emergence](/part1-axioms/law3-emergence/)
- **Consensus, coordination** → [Law 4: Trade-offs](/part1-axioms/law4-tradeoffs/) and [Law 5: Knowledge](/part1-axioms/law5-epistemology/)
- **Monitoring, observability** → [Law 5: Epistemology](/part1-axioms/law5-epistemology/)
- **UX, operations, tooling** → [Law 6: Human-API](/part1-axioms/law6-human-api/)
- **Cost, resources, scaling** → [Law 7: Economics](/part1-axioms/law7-economics/)

## Archived Content

The original 8-law content is preserved in the archive for reference:
- [Archive: Old 8-Law Structure](/part1-axioms/archive-old-8-law-structure/README)

## Summary: What You Gain with the New Framework

1. **Deeper Understanding**: Theoretical foundations explain *why* things work
2. **Better Mental Models**: Think in terms of fundamental laws, not just patterns
3. **Improved Decision Making**: Multidimensional trade-off analysis
4. **Modern Concepts**: Addresses emergence, metastability, and cognitive factors
5. **Unified Theory**: See how all aspects interconnect

---

*"The evolution from simple laws to fundamental laws represents our field's maturation from empirical observation to theoretical understanding."*