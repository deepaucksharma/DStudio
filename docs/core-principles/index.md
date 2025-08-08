---
title: Core Principles
description: Core Principles overview and navigation
---

# Core Principles

Master the fundamental laws and pillars that govern all distributed systems.

## Why Physics Matters for Software

Understanding distributed systems requires grasping the fundamental constraints imposed by physics - the speed of light, thermodynamics, and quantum mechanics. These aren't abstract concepts but real limits that manifest as network latency, heat dissipation, and information propagation delays in every distributed architecture.

!!! info "Physics-Derived Foundation"
    Every pattern in this compendium traces back to physical constraints. By starting with fundamental laws, you'll develop intuition for why certain architectures work and others fail at scale.

## Overview

Distributed systems are governed by **7 immutable laws** derived from physics and organized around **5 core pillars** that shape every architectural decision. This section provides the theoretical foundation you'll need before diving into specific patterns.

```mermaid
graph TB
    Physics[Physical Constraints] --> Laws[7 Fundamental Laws]
    Laws --> Pillars[5 Core Pillars]
    Pillars --> Patterns[91+ Design Patterns]
    Patterns --> Systems[Production Systems]
    
    Laws --> L1[Correlated Failure]
    Laws --> L2[Asynchronous Reality]
    Laws --> L3[Emergent Chaos]
    
    Pillars --> P1[Work Distribution]
    Pillars --> P2[State Distribution]
    Pillars --> P3[Truth Distribution]
```

## 📚 Sections

<div class="grid cards" markdown>

- :material-atom:{ .lg } **[The 7 Laws](laws.md)**
    
    ---
    
    Immutable constraints derived from physics that govern all distributed architectures
    
    | Law | Summary |
    |-----|---------|
    | [Correlated Failure](laws/correlated-failure.md) | Failures cascade across system boundaries |
    | [Asynchronous Reality](laws/asynchronous-reality.md) | Networks are inherently unreliable and slow |
    | [Temporal Constraints](laws/temporal-constraints.md) | Perfect time synchronization is unattainable |
    | [Emergent Chaos](laws/emergent-chaos.md) | Complexity emerges from simple interactions |
    | [Multidimensional Optimization](laws/multidimensional-optimization.md) | Every trade-off has multiple dimensions |
    | [Distributed Knowledge](laws/distributed-knowledge.md) | Perfect knowledge is physically impossible |
    | [Cognitive Load](laws/cognitive-load.md) | Human comprehension limits system design |
    | [Economic Reality](laws/economic-reality.md) | Resource constraints drive architectural decisions |

- :material-pillar:{ .lg } **[The 5 Pillars](pillars.md)**
    
    ---
    
    Foundational concepts for organizing and distributing system responsibilities
    
    | Pillar | Summary |
    |--------|---------|
    | [Work Distribution](pillars/work-distribution.md) | How computational tasks spread across nodes |
    | [State Distribution](pillars/state-distribution.md) | How data and memory scatter through the system |
    | [Truth Distribution](pillars/truth-distribution.md) | How consistency and consensus emerge |
    | [Control Distribution](pillars/control-distribution.md) | How decisions and coordination happen |
    | [Intelligence Distribution](pillars/intelligence-distribution.md) | How learning and adaptation occur |

</div>

## 🚀 Quick Start

New to distributed systems? Begin your journey with the fundamental laws that govern every system.

[:octicons-arrow-right-24: Start with the 7 Laws](laws.md){ .md-button .md-button--primary }

## 🎯 Learning Paths

Choose a structured curriculum tailored to your role and experience level:

| Path | Duration | Focus | Week-by-Week Coverage |
|------|----------|-------|----------------------|
| **[New Graduate](../../architects-handbook/learning-paths/new-graduate.md)** | 12 weeks | Foundation-building | Laws → Pillars → Basic Patterns → Simple Systems |
| **[Senior Engineer](../../architects-handbook/learning-paths/senior-engineer.md)** | 8 weeks | Architecture mastery | Advanced Patterns → Trade-offs → Complex Systems |
| **[Architect](../../architects-handbook/learning-paths/architect.md)** | 6 weeks | System design leadership | High-level design → Cost optimization → Team decisions |
| **[Manager](../../architects-handbook/learning-paths/manager.md)** | 4 weeks | Strategic understanding | Business implications → Team structure → Risk assessment |

## 📖 How to Use This Section

1. **Start with the Laws** - Understand the fundamental constraints
2. **Study the Pillars** - Learn how to organize solutions
3. **Apply to Patterns** - See how principles manifest in real patterns
4. **Practice with Examples** - Work through exercises and case studies

---

*Ready to begin? Start with [The 7 Laws](laws.md) to understand the physics that shapes all distributed systems.*