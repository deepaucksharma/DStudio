---
title: "Law 1: The Law of Inevitable and Correlated Failure"
description: Any component can fail, and failures are often correlated, not independent - with mathematical proofs, production examples, and battle-tested solutions
type: law
difficulty: expert
reading_time: 25 min
prerequisites: ["part1-axioms/index.md"]
status: enhanced
last_updated: 2025-01-25
---

# Law 1: The Law of Inevitable and Correlated Failure ⚡

[Home](/) > [The 7 Laws](part1-axioms) > [Law 1: Correlated Failure](part1-axioms/law1-failure/index) > Deep Dive

!!! danger "🚨 DURING AN INCIDENT? Jump to:"
    - **[Identify Which Specter](five-specters.md#quick-identification)** – Pattern recognition in 30s
    - **[Check Dashboards](operational-sight.md#one-glance-control-room-layout)** – What to look for
    - **[Apply Fix](architectural-lenses.md#specter-counter-lens-map)** – Which pattern stops it
    - **[Triage Playbook](operational-sight.md#4-on-call-playbook-four-step-triage)** – Step-by-step

## Visual Language for This Guide

```
STATES:           FLOWS:              RELATIONSHIPS:       IMPACT:
healthy ░░░       normal ──→          depends │            minimal ·
degraded ▄▄▄      critical ══►        contains ┌─┐         partial ▪
failed ███        blocked ──X                  └─┘         total ●
```

## Opening the Eye – "From Parts to Web"

```
        THE ILLUSION                            THE REVEAL
        ════════════                          ═════════════

          ┌───┐  ┌───┐  ┌───┐              ┌───┐  ┌───┐  ┌───┐
          │ A │  │ B │  │ C │              │ A │  │ B │  │ C │
          └─┬─┘  └─┬─┘  └─┬─┘                │      │      │
            │      │      │                  ┌┴──────┴──────┐
            ▼      ▼      ▼                  │  EBS CONTROL │
    "Count the nines."                       │     PLANE    │
                                             └┬────┬────┬───┘
                                              ▼    ▼    ▼
                                            A OUT B OUT C OUT
```

!!! quote "Your First Reflex From Now On"
    Where is the **control plane** or other unseen spine that will fell every component at once?

## Central Dogma of Reliability – Math vs Reality

### The Seductive Math Lie

```
P(system fails) = Π P(component_i fails)

0.001³ = 1×10⁻⁹   →   "Nine nines!"
```

### The Actual Math

```
P(system fails) = P(independent) + P(shared_dependency_j fails)

=> Availability ≈ min(component_availability) × (1 – max ρ_correlations)
```

| Variable | Meaning | Typical Range |
|----------|---------|---------------|
| *A_i* | Availability of component *i* | 95% – 99.999% |
| *ρ* | Correlation coefficient between any two components | 0.1 – 0.95 |

!!! warning "Rule of Thumb"
    If *ρ* > 0.6 anywhere, your *effective* availability collapses to within striking distance of your worst single component.

## Categories of Invisible Dependency

*Know them; draw them.*

| Glyph | Dependency Class | Typical "Gotcha" Example |
|-------|------------------|-------------------------|
| 🔌 | **Power** (feed, UPS, PDU, cooling) | Both "A+B" feeds share the same upstream breaker |
| 🌐 | **Network / Control Plane** | Auth, config, or DNS service every call path secretly hits |
| 💾 | **Data** (storage, lock, queue) | Global metadata DB behind "independent" shards |
| 🛠 | **Software / Config** | Kubernetes admission webhook, feature flag service |
| 👤 | **Human** | One on-call owning the only production credential |
| 🕰 | **Time** | Cert expiry, DST switch, leap second, cron storm |

!!! tip "Checklist Mantra"
    **P N D S H T** (Power-Network-Data-Software-Human-Time) – run it against every architecture diagram.

## Correlation Shapes – Spot Them Visually

| Shape | ASCII Sketch | Where It Hides | Why It's Deadly |
|-------|-------------|----------------|------------------|
| **Fan-In** | `A,B,C → X` | Central key-value store, CI/CD controller | X dies ⇒ whole fleet blind |
| **Fan-Out** | `X → A,B,C` | Mis-scoped config push, regex rule | X mistake cascades in seconds |
| **Temporal Sync** | `00:00Z → All AZs deploy` | Certificate renewal, global cron job | Simultaneous blast |
| **Admin Path** | `Fix tool → Uses broken net` | Status page in same region | Blocks self-recovery |
| **Retry Feedback** | `Fail → Retry ×3 → Fail+` | Client libs with naive retry | Metastable overload |

!!! tip "Quick Recognition"
    During incidents, ask: "Which shape is this?" The answer tells you where to look next.

## Mind-Shift Table – Engineer → System Thinker

### Before This Law vs After This Law

| Thinking Before | Thinking After | Mental Image |
|----------------|----------------|-------------|
| **"Prevent all failures"** | **"Make failure irrelevant"** | *Bulkheads on a submarine* |
| "Why did X break?" | **"Why did X drag Y & Z down?"** | *Domino chain* |
| "Add more redundancy" | **"Add independence first"** | *Different clouds, not more servers* |
| "99.99% uptime!" | **"< 20% blast radius"** | *How many users affected?* |
| "It's redundant" | **"But is it correlated?"** | *Puppet strings* |
| "Health check passed" | **"Users still suffering?"** | *Green ≠ Seen* |

## Dashboard Signature-Reading Cheat-Sheet

```
PATTERN 1 – Perfectly Synchronized Error Spike
  Services A-Z error lines snap upward at same timestamp
  ⇒ Likely common-cause (bad deploy / cert / control plane)

PATTERN 2 – p99 Latency ↑ 10× while HC stays flat
  ⇒ Gray failure; customers hurt, monitoring blind.

PATTERN 3 – Queue Depth Exponential Growth
  ⇒ Metastable feedback; auto-scaling won't save you.
```

!!! tip "Training Drill"
    Pick a past incident; replay graphs; ask "Which pattern?" until muscle memory forms.

## The Litmus-Test Questions

*Tape beside every whiteboard:*

1. **Pull-the-Plug Test:**
   > "If I switch off rack *R*, what *outside* that rack feels pain?"

2. **Midnight Test:**
   > "What's the worst thing that can kick off simultaneously on *all* nodes at 00:00?"

3. **Health-Check False-Positive Test:**
   > "Name one bug where `/healthz` stays green but the CEO's login fails."

4. **Blast-Radius Box Test:**
   > "Draw the rectangle around a failure domain; prove < X% users inside."

5. **Who-Can-Fix-It Test:**
   > "Can the people & tools that heal outage *F* operate while *F* is still happening?"

## The Operator's Oath

*Pin to your pager:*

```
I will no longer see servers; I will see dependency webs.
I will distrust nines that ignore correlation.
I will treat every shared resource as a latent single point of failure.
I will invest first in isolation, second in redundancy.
My mission is not perfect uptime; it is making failure inconsequential.
```

## Real-World Case Studies – Pattern Recognition

| Incident | Year | Pattern | Visual Signature | Your Lesson |
|----------|------|---------|------------------|-------------|
| **AWS EBS Storm** | 2011 | Fan-In | `Zones A,B,C → Control Plane` | Find your hidden control planes |
| **S3 Typo** | 2017 | Fan-Out | `Typo → S3 → Everything` | Your status page has same dependency? |
| **GitHub Split-Brain** | 2018 | Admin Path | `Fix needs broken system` | Can you recover if primary is dead? |
| **Cloudflare Regex** | 2019 | Temporal Sync | `Deploy → 100% CPU @ same time` | Do you deploy globally in < 60s? |
| **Facebook BGP** | 2021 | Admin Path | `Network tools need network` | Test your recovery tools offline |
| **Knight Capital** | 2012 | Version Mismatch | `Old code + new flag = 💥` | Do you verify all deploys? |

## Strategies for Breaking Correlations

### 1. Cell-Based Architecture 🏝️
```
BEFORE: 10,000 servers = 1 giant failure domain
        ████████████████████████ (all users affected)

AFTER:  100 cells × 100 servers each
        ██░░░░░░░░░░░░░░░░░░░░ (only 1% affected)
```

### 2. Shuffle Sharding 🎲
```
Traditional Assignment:          Shuffle-Sharded:
All clients → All servers        Each client → Random 5 servers

Client impact if 3 servers fail:
Traditional: 100% affected       Shuffle: < 2% affected
```

### 3. Progressive Deployment 🚀
```
Hour 0: Deploy to 1% (canary)     ▒
Hour 1: Expand to 10%             ▒▒▒▒
Hour 2: Expand to 50%             ▒▒▒▒▒▒▒▒▒▒
Hour 3: Full deployment           ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒

Auto-rollback if: errors > normal + 3σ
```

### 4. Diversity Requirements 🌈
```
✅ GOOD Diversity              ❌ BAD "Redundancy"
├─ 30% AWS us-east            ├─ 100% AWS us-east
├─ 30% AWS us-west            │   ├─ Zone A: 50%
├─ 20% Azure east             │   └─ Zone B: 50%
└─ 20% On-premise             └─ (Same provider = correlated)
```



## The Visual Blueprint Series

Master correlation-resistant systems through our four-page visual guide:

### 📄 [Page 2: The Five Specters of Failure](five-specters.md)
Every correlated failure manifests as one of five patterns:
1. **BLAST RADIUS** – Size of the crater
2. **CASCADE** – Pebble → Avalanche  
3. **GRAY FAILURE** – Looks fine, isn't
4. **METASTABLE** – Self-feeding spiral
5. **COMMON CAUSE** – One string, many puppets

### 🏗️ [Page 3: Architectural Lenses](architectural-lenses.md)
Patterns that break correlation:
- **Cells** – Island model for blast radius control
- **Shuffle-Sharding** – Personalized fate mapping
- **Bulkheads** – Internal watertight doors
- **Diversity** – True independence through variety

### 🎛️ [Page 4: Operational Sight](operational-sight.md)
Running and proving correlation-resilience:
- Dashboard layouts for instant failure recognition
- Chaos engineering loops
- On-call playbooks
- Continuous verification pipelines

## Key Takeaways

!!! abstract "The Core Truth"
    **Your real system availability = `min(component_availability)` × `(1 - max(correlation_coefficient))`**

### What Changed Your Mind?
1. **Illusion shattered**: Components aren't independent
2. **New lens**: See webs, not parts
3. **New mission**: Make failure inconsequential, not impossible

### Your Next Actions
1. **Today**: Run the 5 litmus tests on your current system
2. **This week**: Map all PNDSHT dependencies
3. **This month**: Implement one correlation breaker
4. **This quarter**: Measure actual ρ values in production

## Reading Road-Map

*If you crave proof:*

1. **"The Network is Reliable"** – Kingsbury & Bailis (debunks independence)
2. **"Metastable Failures"** – Bronson et al. (positive feedback death)
3. AWS & GitHub post-mortems – real graphs that match patterns above

## Quick Reference

### 📚 Deep Dives
- **[Real-World Failures](examples.md)**: Detailed case study analyses
- **[Hands-On Labs](exercises.md)**: Correlation detection exercises
- **[Next: Law 2](../law2-asynchrony/index.md)**: The Asynchronous Reality

### 🔗 Related Patterns
- [Circuit Breaker](../../patterns/circuit-breaker.md) - Stop cascades
- [Bulkhead](../../patterns/bulkhead.md) - Isolate failures
- [Cell-Based Architecture](../../patterns/cell-based-architecture.md) - Break correlations

---

<div class="page-nav" markdown>
[:material-arrow-left: The 7 Laws](../../part1-axioms/index.md) | 
[:material-arrow-up: Top](#) | 
[:material-arrow-right: Law 2: Async Reality](../law2-asynchrony/index.md)
</div>