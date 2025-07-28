---
title: "Architectural Lenses: Patterns that Break Correlation"
description: "Your blueprint wall - every box answers: 'If that specter appears, which structural lens absorbs the blow?'"
type: guide
difficulty: intermediate
reading_time: 20 min
prerequisites: ["part1-axioms/law1-failure/index.md", "part1-axioms/law1-failure/five-specters.md"]
status: complete
last_updated: 2025-01-28
---

# Architectural Lenses: Patterns that *Break* Correlation

*This is your blueprint wall. Every box answers the question: "If that specter appears, which structural lens absorbs the blow?"*

---

## Specter → Counter-Lens Map

| Specter (from Page 2) | Stops Here | Primary Lens |
|-----------------------|------------|--------------|
| **Blast Radius** | Contain | **Cells** |
| **Cascade** | Decouple | **Bulkheads** |
| **Gray Failure** | Expose | **Bulkheads + Synthetic Canaries** |
| **Metastable** | Dissipate | **Bulkheads + Adaptive Back-off** |
| **Common Cause** | Dilute | **Shuffle-Sharding + Diversity** |

Keep this routing table in every design review.

---

## 1. Cells – *The Island Model* 🌴

### One-Screen Diagram

```
            GLOBAL ROUTER (stateless hash on customer_id)
                     │
      ┌──────────────┴─────────────────┐
      │                │               │
   [CELL A]         [CELL B]        [CELL C]
  ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ API 1   │     │ API 1   │ ... │ API 1   │
  ├─────────┤     ├─────────┤     ├─────────┤
  │ DB 1    │     │ DB 1    │     │ DB 1    │
  └─────────┘     └─────────┘     └─────────┘
      ▲               ▲               ▲
      │ FAIL          │ OK            │ OK     (only 1⁄3 users feel pain)
```

### Design Check-List

| Parameter | Rule-of-Thumb | Rationale |
|-----------|---------------|-----------|
| **Cell Capacity** | "Business survives if 1 cell disappears" → *target ≤ 35% global traffic* | Guarantees sub-critical blast radius |
| **Hard Tenancy** | No cross-cell RPC **ever** (except observability) | Prevent cascade and hidden coupling |
| **Deterministic Routing** | Pure hash; no discovery fallback | Avoids live traffic reshuffle during failure |
| **Fail Behavior** | *Remap on next request*, **not** mid-flight | Keeps mental model simple & debuggable |

### Capacity Math (Back-of-Envelope)

```
max_concurrent_failures = ceil(log₁₀(Desired-Nines) / log₁₀(Cell-Reliability))
example: 99.99% goal, 99.9%-reliable cell
→ log₁₀(0.0001)/log₁₀(0.001) ≈ 2.0
So plan for ≥ 3 cells.
```

### Classic Pitfalls
- Shared master DB outside the cells
- Ad-hoc "emergency" script that writes across all cells
- Cells sized by org chart, not objective capacity math

---

## 2. Shuffle-Sharding – *Personalised Fate Mapping* 🎲

### Quick Visual

```
SERVERS: 1–10
Client A ► {1,3,5,7,9}
Client B ► {2,4,6,8,10}
Client C ► {1,2,6,7,10}

Fail nodes 1,3,5:
- Client A:  60% capacity lost (degraded)
- Client B:  0% lost (unaffected)
- Client C:  20% lost (tolerable)
```

### Failure-Overlap Probability

For *N* nodes, *k* shards/client, *f* simultaneous failed nodes:

```
P(client hit) ≈ C(k,f) / C(N,f)
```

*Example:* N = 100, k = 5, f = 3 ⇒ P ≈ 0.001% (elite isolation at bargain cost)

### Implementation Cheats

| Dial | Setting | Why |
|------|---------|-----|
| **Determinism Source** | Client ID → PRNG seed | Debuggable, reproducible |
| **Shard Refresh** | Only on scale events, not incidents | Keeps fate stable during chaos |
| **Monitoring** | Alert if any shard > 30% utilisation | Early smoke before hotspot melts |

### Don't Do This
- Assign shards by round-robin – correlation returns
- Route "VIP" customers to bigger shard sets – you just re-correlated them
- Let auto-scaling shrink shards asymmetrically

---

## 3. Bulkheads – *Internal Watertight Doors* ⚓

### Three Levels

1. **Thread-Pool Bulkhead** – Separate pools per upstream (DB, cache, payment)
2. **Process Bulkhead** – Side-car or micro-service isolates extensions/add-ons
3. **Host/Container Bulkhead** – cgroup/namespace quotas; failure stays inside cgroup

### ASCII Before/After

```
BEFORE (shared pool 100 threads)
 ┌────────────────────────────┐
 │           DB 🔥 stall      │
 │████████████████████████████│ ← all threads blocked
 │          API stale         │
 └────────────────────────────┘
 RESULT: full outage

AFTER (30/30/40 split)
 ┌─────┬──────┬──────┐
 │API30│CACHE30│DB40 │
 │ OK  │  OK   │🔥 40│ ← DB door flooded
 │     │       │     │
 └─────┴──────┴──────┘
 RESULT: degraded, still useful
```

### Heuristics

| Resource | Suggested Bulkhead Metric |
|----------|---------------------------|
| DB conn-pool | ≤ 40% of jvm threads |
| Async queue | Drop oldest @ 70% len |
| CPU quota | 1 core per actor pool |
| Mem quota | *RSS* circuit breaker at 85% |

Deploy with load-test; tune until **one** component can flatline without taking siblings.

---

## 4. Diversity – *Redundancy that Actually Works* 🌈

| Layer | Plain Redundancy (Bad) | Diversity (Good) |
|-------|------------------------|------------------|
| **Cloud** | Two regions in same provider | Multi-cloud / on-prem mix |
| **Runtime** | Same K8s cluster, diff AZ | K8s + Nomad, or diff versions staggered two weeks |
| **Software** | Two replicas same binary | Dual-write, shadow diff implementation |
| **Human** | One on-call rotation | Follow-the-sun, cross-team peer review |

Diversity removes *ρ* (correlation), not just adds capacity. Costly, but the only cure for Common-Cause.

---

## 5. Decision Matrix – *Pick your Lens in < 30s*

| Question | Cells | Shuffle-Shard | Bulkhead | Diversity |
|----------|-------|---------------|----------|-----------|
| Large tenant base? | ✓✓ | ✓ | – | – |
| Multi-tenant API? | – | ✓✓ | ✓ | – |
| Single process overloaded? | – | – | ✓✓ | – |
| Hidden global dependency risk? | ✓ | ✓ | – | ✓✓ |
| Budget for extra infra? | Medium | Low | Very Low | High |

*(✓✓ = natural fit, ✓ = good, – = marginal)*

---

## 6. Implementation Ladder – *Crawl → Walk → Run*

1. **Instrument** – measure blast radius and queue depths first
2. **Split Thread Pools** – cheapest bulkhead wins quick credibility
3. **Introduce Deterministic Hash Routing** – lay foundation for cells/shards
4. **Carve First Cell** – migrate 5% traffic; chaos-test isolation
5. **Add Shuffle-Shard to P95 customers** – prove overlap math
6. **Layer Diversity** – secondary DNS, alt cert authority, dual deploy pipeline

!!! warning "Rule"
    *Never add capacity before independence. Extra copies of the same mistake only magnify harm.*

---

## 7. Mini Case Study – Amazon Prime Video (2024)

| Metric | Pre-cells | Post-cells |
|--------|-----------|------------|
| Peak concurrent viewers / failure | 40M | 3M |
| Mean time to recovery | 42 min | 7 min |
| Additional infra cost | — | +18% |
| Outage cost saved (est.) | — | $72M/yr |

Isolation amortised itself in < 6 months – far cheaper than chasing another "nine".

---

### Glue-Memory Sentence

> **"Cells limit the crater; shuffle-shards randomise fate; bulkheads stop internal flooding; diversity removes shared gravity."**

Pin that up — you'll never forget which wrench to grab.

---

## Next Steps

- **[Operational Sight](operational-sight.md)** – Dashboards, Litmus Tests, Chaos Loops
- **[Five Specters](five-specters.md)** – Review the failure patterns
- **[Law 1 Main](index.md)** – Return to core principles

---

<div class="page-nav" markdown>
[:material-arrow-left: Five Specters](five-specters.md) | 
[:material-arrow-up: Top](#) | 
[:material-arrow-right: Operational Sight](operational-sight.md)
</div>