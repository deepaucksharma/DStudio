---
title: "The Five Specters of Failure"
description: "A field-guide for instantly recognising the patterns that turn 'a glitch' into an extinction-level event"
type: guide
difficulty: intermediate
reading_time: 15 min
prerequisites: ["part1-axioms/law1-failure/index.md"]
status: complete
last_updated: 2025-01-28
---

# The Five Specters of Failure

*A field-guide for instantly recognising the patterns that turn "a glitch" into an extinction-level event.*

## Visual Language Reference
```
STATES:           FLOWS:              RELATIONSHIPS:       IMPACT:
healthy ░░░       normal ──→          depends │            minimal ·
degraded ▄▄▄      critical ══►        contains ┌─┐         partial ▪
failed ███        blocked ──X                  └─┘         total ●
```

---

## The Rosetta Stone

```
             ┌─────────────┐   asks "Who else hurts?"
             │ BLAST RADIUS│  ──────────────────────────►  USER IMPACT
             └────┬────────┘
                  │
┌─────────────┐   │   ┌────────────┐
│ COMMON CAUSE│◄──┼──►│  CASCADE   │  "Will this snowball?"
└────┬────────┘   │   └────────────┘
     │            │
     ▼            ▼
┌─────────────┐   ┌────────────┐
│ GRAY FAILURE│   │ METASTABLE │  "Will retries kill us?"
└─────────────┘   └────────────┘
```

!!! tip "Mnemonic"
    **B**last, **C**ascade, **G**ray, **M**etastable, **C**ommon-Cause – "*Big Cats Growl, Maul & Claw*"

---

## Quick Identification

!!! danger "During an Incident?"
    1. Look at your dashboard grid - how many cells/services are red?
    2. Check error correlation - are multiple services failing together?
    3. Look for these visual patterns in your metrics
    4. Match to a specter below
    5. Jump to the [architectural lens](architectural-lenses.md) that counters it

## 1. BLAST RADIUS – *"If this dies, who cries?"*

| Quick Sketch | Core Insight |
|--------------|--------------|
| `[====XXXX====]` | Outage size is **designed** long before failure strikes |

**Tell-tale Dashboard:** A single heat-map column glows red; adjacent columns stay blue.

**Signature Outages:**
- Azure AD global auth (2023) – one dependency, worldwide sign-in failure

### Scan-Questions ✢
*Tape them on the spec sheet:*

1. Can I draw a **box** around a failure domain that contains < X% of users?
2. What is the *largest* thing we deploy in one atomic step?

**Antidote Patterns:** Cells • Bulkheads • Shuffle-sharding

---

## 2. CASCADE – *"Which pebble starts the avalanche?"*

```
○  →  ●  →  ●●  →  ●●●●  →  💥
tiny   small   medium   OMG
```

**Dynamics:** Downstream retries / rebalance > upstream overload > feedback loop

| Warning Light | Typical Root |
|---------------|--------------|
| 300% traffic jump 30s after first 5xx | Client library with unlimited retries |
| Queue depth doubles every refresh | FIFO shared by diverse services |

**Real Emblem:** *S3 typo 2017 – index sub-system removed, cascaded through every AWS console tool*

**Mitigation Lenses:** Back-pressure • Circuit-breakers • Progressive rollout

---

## 3. GRAY FAILURE – *"Green dashboards, screaming users"*

```
HEALTH-CHECK   ▄▄▄▄▄▄▄▄▄▄▄  ✓
REAL LATENCY   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄  ✗
```

**Symptoms:** p99 latency jumps ×10; error-rate flat; business KPIs nose-dive

| Lie Detector | How to Build One |
|--------------|------------------|
| Synthetic customer journey | Headless browser / prod mirrors |
| **HC-minus-p95** gap alert | Compare "SELECT 1" with real query latency |

**Case Pin:** Slack DB lock contention (2022) – HC 5ms, user fetch 30s

**Mental Rule:** *Healthy ≠ Useful*

---

## 4. METASTABLE – *"The cure becomes the killer"*

> **Positive feedback + overload = state you can't exit without external force**

```
REQ  ↗
FAIL │  ↻ retry×3 → load↑ → fail↑ → …
CAP  └──────────────────────────────►
```

**Field Signs:**
- Queue depth curve bends vertical
- CPU idle yet latency infinite (threads stuck in retry loops)

**Hall-of-Fame Incident:** Facebook BGP 2021 – withdrawal → DNS fail → global retry storm → auth down → can't push fix

**Escape Tools:** Immediate load-shedding • Adaptive back-off • Manual circuit open

---

## 5. COMMON CAUSE – *"One puppet-string, many puppets"*

```
A ─┐
B ─┼───►  CERT EXPIRES 00:00Z  →  A+B+C dead
C ─┘
```

**Hunting Grounds:**
- TLS certs shared across regions
- Config service, feature-flag service, time sync
- "Small" DNS or OAuth dependency everyone silently embeds

**Detection Clue:** Multiple unrelated services fail at **exact same timestamp** – a square pulse on a bar-chart

**Dissolving the String:** Diverse issuers • Staggered cron • Chaos drills that cut hidden power ties

---

## Putting the Specters to Work

| Scenario | Dominant Specter | First Question to Ask |
|----------|------------------|----------------------|
| Single AZ power loss | Blast Radius | "Did our cell size cap user pain < 33%?" |
| Feature flag rollout in 30s | Cascade | "What is max QPS multiplier if flag misbehaves?" |
| Users say "slow" yet SRE sees green | Gray | "Do we alert on HC-minus-real latency?" |
| Spike in retries after DB hiccup | Metastable | "Who will hit the big red *shed load* switch?" |
| Midnight cert expiry kills API & admin console | Common Cause | "Why did we renew *everything* at once?" |

---

## Quick-Sight Memory Palace

```
        ┌─────────────┐
        │ BLAST RADIUS│   Size of the crater
        └────┬────────┘
             │
    ┌────────▼──────────┐
    │   CASCADE         │  Pebble → Avalanche
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │   GRAY FAILURE    │  Looks fine, isn't
    └────────┬──────────┘
             │
    ┌────────▼──────────┐
    │   METASTABLE      │  Self-feeding spiral
    └────────┬──────────┘
             │
        ┌────▼─────┐
        │COMMON-CAUSE│  One string, many puppets
        └────────────┘
```

!!! abstract "Key Insight"
    Memorise the pyramid. In any incident review, point at the specter you met.
    If you can't decide which one it was... you haven't looked hard enough yet.

---

## Next Steps

- **[Architectural Lenses](../architectural-lenses.md)** – Cells, Shuffle-Sharding, and Bulkheads in high-resolution
- **[Law 1: Correlated Failure](index.md)** – Return to the core principle
- **[Hands-On Labs](exercises.md)** – Practice identifying specters in real scenarios

---

<div class="page-nav" markdown>
[:material-arrow-left: Law 1 Main](index.md) | 
[:material-arrow-up: Top](#) | 
[:material-arrow-right: Case Studies](examples.md)
</div>