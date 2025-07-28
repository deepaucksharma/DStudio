---
title: "Operational Sight: Running, Watching & Proving Correlation-Resilience"
description: "The cockpit dashboard + drill routine your team lives by once the architecture is in place"
type: guide
difficulty: advanced
reading_time: 20 min
prerequisites: ["part1-axioms/law1-failure/index.md", "part1-axioms/law1-failure/five-specters.md", "part1-axioms/law1-failure/architectural-lenses.md"]
status: complete
last_updated: 2025-01-28
---

# Operational Sight: Running, Watching & Proving Correlation-Resilience

*The cockpit dashboard + drill routine your team lives by once the architecture is in place.*

---

## One-Glance Control Room Layout

```
┌─ GRID-VIEW (Blast Radius) ─┐  ┌─ LATENCY-DELTA (Gray) ─┐  ┌─ RETRY-SPIRAL (Metastable) ─┐
│ cell-a  cell-b  cell-c  … │  │  p95_user – HC_gap     │  │  queueDepth vs retryRate    │
│ ███     ░░░     ░░░       │  │  ▄▄▄▄▄ ▄   <- alert    │  │  ↗ exponential?  🔔         │
└───────────────────────────┘  └────────────────────────┘  └──────────────────────────────┘

┌─ CORRELATION MATRIX ─┐        ┌─ CHANGE-TRAIN ROLL-MAP ──┐
│      A  B  C  D      │        │ R1  R2  R3  R4           │
│  A  1 .8 .1 .0      │        │ ▒▒█ Canaries ▒▒▒▒▒ Prod │
│  B .8  1 .2 .1      │        └─────────────────────────┘
│  …                  │
└───────────────────────┘
```

!!! tip "Goal"
    Inside 5s an operator can answer: "*Where is the pain, how big, why together, and which release caused it?*"

---

## 1. Golden Signals Extended for Correlation

| Classic Four | Add Two More | Why |
|--------------|--------------|-----|
| **Latency** | **Lat-Δ (user p95 – HC p95)** | Gray failure early-warning |
| **Traffic** | **Correlation Heat (ρ > 0.6 pairs)** | Detect hidden coupling |
| **Errors** | — | — |
| **Saturation** | — | — |

**Alert Rules** – fire *only* when signal pair confirms user harm:

```yaml
- name: gray-failure
  expr: (lat_user_p95 - lat_hc_p95) > 800ms for 3m
- name: hidden-correlation
  expr: max_over_time(corr_matrix[5m]) > 0.6
```

---

## 2. Litmus-Gate for Every Change (PR → Prod)

| Gate | Test | Fail Action |
|------|------|-------------|
| **Blast-Radius** | Simulate cell kill; user loss < X% | Block merge |
| **Correlation** | Inject synthetic 5xx in target service; corr ≤ 0.3 | Rollback |
| **Gray Canary** | Canary Lat-Δ < 200ms | Halt rollout |
| **Metastable Probe** | Retry storm simulator stays < 120% load | Add back-off patch |

Automate gates in CI; show traffic-light badges on PR.

---

## 3. Chaos Loop – Monthly Muscle-Build

```
 DISCOVER  →  INJECT  →  OBSERVE  →  LEARN  →  HARDEN
   ^                                          |
   └──────────── retrospective  ◄─────────────┘
```

| Phase | Tool Snippet |
|-------|--------------|
| **Discover** | `corr-scan --top 5` – SQL that logs top ρ pairs |
| **Inject** | `chaos-cli kill --az us-east-1a --duration 5m` |
| **Observe** | Watch GRID + Lat-Δ + Spiral boards |
| **Learn** | "Specter Bingo" – team tags which specter manifested |
| **Harden** | Write checklist item / playbook patch |

*Rule: run one chaos game-day per cell per quarter; rotate the game-master.*

---

## 4. On-Call Playbook – Four-Step Triage

| Time | Action |
|------|--------|
| T + 0 min | Look at GRID: scope sized? (blast) |
| T + 2 min | Check Correlation Heat: shared cause? |
| T + 4 min | Lat-Δ? → Yes ⇒ suspect Gray |
| T + 5 min | Queue↗+Retry↗? ⇒ Metastable – **shed load NOW** |

**Communication Macro**

```
🚨 Incident <id> – Specter:<Blast/Cascade/...> – Cell <x> – 30% users – Mitigation: block release; load shed 40%
```

Send in < 7 min; updates every 15 min.

---

## 5. Post-Mortem Template – Specter First

1. **Specter Tag** (pick one or stack)
2. **Correlation Map** (red-line all shared deps touched)
3. **Blast Radius % vs SLO**
4. **What blocked auto-recovery?**
5. **Checklist delta** (which gate/metric now added)
6. **Cost & ROI** (minutes, user sessions, $)
7. **Chaos Replay Plan** (prove fix)

---

## 6. Run-Time Circuit Board

| Circuit | Trip When | Auto-Action | Pager? |
|---------|-----------|-------------|--------|
| **Bulkhead-DB** | pool wait > 200ms | Drop oldest req | No |
| **Cell-Breaker** | error rate cell > 2× baseline 3m | Shed 100% → neighbours | Yes |
| **Client-Retry** | 2 fails | Back-off ×4 + jitter | No |
| **Global "Kill Switch"** | corr_heat > 0.8 & errors ↑ | Freeze deployments | Yes |

Implement in policy-engine (e.g., Envoy Lua, Istio rules).

---

## 7. Continuous Verification Pipeline

```
git push
  ↓
Unit + Bulkhead tests
  ↓
Corr-Sim (shuffle-shard maths)
  ↓
Canary 1 (1%)
  ↓
Specter Scanners live (Blast, Gray, Metastable)
  ↓
Auto-Promote step 2,4,8,16%
  ↓
Prod 100%
```

Failed step reverts & opens "WHY" ticket pre-filled with dashboards. No human exception.

---

## 8. Cheat-Codes & Mnemonics

| Need To Remember | Say This Out Loud |
|------------------|-------------------|
| Correlation Matrix | "Red in the square? Something we share." |
| Gray Failure | "Green ≠ Seen" |
| Metastable | "Retry is a drug; dose or die." |
| Cells | "Lose 1 island, not the map." |
| Shuffle-Shard | "Luck of the draw protects the VIPs." |

Stick them on team wiki headers; repetition builds instinct.

---

## 9. The Operator's Oath – **Pocket Edition**

> *"I will see webs, not boxes.*  
> *I will measure pain, not uptime.*  
> *I will distrust the green light until the customer smiles.*  
> *I will drill for chaos until boredom.*  
> *I will make failure irrelevant."*

Print, sign, laminate, tape to laptop.

---

### Graduation Badge 🏅

When a new hire can, unaided:

1. classify an incident into a specter
2. diagram the hidden dependency
3. name the correct architectural lens
4. write the monitoring rule to catch it next time

...they earn the "Correlation Slayer" sticker.  
Give it proudly; culture scales better than configs.

---

**End of Page 4 (and of the four-page visual blueprint).**  
**May every outage henceforth be small, boring, and scientifically deliberate.**

---

## Next Steps

- **[Architectural Lenses](part1-axioms/law1-failure/architectural-lenses/) – Review the patterns
- **[Five Specters](part1-axioms/law1-failure/five-specters/) – Master failure recognition
- **[Law 1 Main](part1-axioms/law1-failure/) – Return to fundamentals

---

<div class="page-nav" markdown>
[:material-arrow-left: Architectural Lenses](part1-axioms/law1-failure/architectural-lenses/) | 
[:material-arrow-up: Top](#) | 
[:material-arrow-right: Law 2](part1-axioms/law2-asynchrony/)
</div>