

How to use this framework
- Score: For each layer, rate L1–L4. Build a heatmap.
- Focus: Pick the top 3 constraints. Run 6-week A3s to move each up one level.
- Install: Use the “Minimal Install Pack” and “Guardrails & Thresholds” to make changes stick.

The Layered Engineering Leadership Framework 2.0
A complete knowledge architecture for technical organizations

Layer 0: Foundational Physics
The immutable laws and control knobs

A) The Three Fundamental Forces
| Force | Nature | Control Knobs | Measurements | Healthy Thresholds |
|---|---|---|---|---|
| Cognitive Gravity | Finite mental capacity attracts complexity | Reduce extraneous load, tighten boundaries, platform paved paths | Cognitive load pulse, context switches/day, deep work hours | Load pulse stable or improving; <3 context switches/day; 2–4 deep work hrs/day |
| Organizational Entropy | Systems drift to chaos without energy | Process half‑life, deletion cadence, platformization | Process count, orphan services, coupling metrics | −10%/qtr process count; coupling trending down |
| Information Friction | Communication decays with distance/handoffs | Async writing as OS, clear APIs/SLAs, decision SLAs | Decision latency, rework rate, duplicate work | 2‑way decisions <48h; rework rate <10% |

B) Universal Constants (operationalized)
- Hierarchy of constraints: Time → Attention → Cognitive load → Relationships → Communication.
- Conservation of complexity: You can only move complexity (to platform, to build-time, to a template, to async).
- Capability equation: Total capability = Individual skills × Team autonomy × Platform leverage.
- Queue law heuristics: Lead time = WIP / Throughput. Reduce WIP before adding people.

Layer 1: Organizational Models
Structure for outcomes, cognition, and speed

A) Evolution of organizational thinking (compressed)
| Era | Model | Strength | Failure Mode | Upgrade |
|---|---|---|---|---|
| 1.0 | Functional silos | Deep expertise | O(n²) coordination | Stream-aligned teams |
| 2.0 | Cross-functional | Faster delivery | Unclear ownership | Outcome ownership |
| 3.0 | DevOps | Quality via ownership | Cognitive overload | Platform leverage |
| 4.0 | Team Topologies | Load-aware structure | Static boundaries | Dynamic topology |
| 5.0 | Adaptive organism | Evolves with needs | Requires maturity | Guardrails + metrics |

B) Team topology patterns (installables)
| Type | Purpose | Cognitive Focus | Success | Anti‑patterns | Artifacts |
|---|---|---|---|---|---|
| Stream‑aligned | Own one outcome | Minimize domain surface | Outcome metric improves | Feature factory | Team charter (metric, users, SLOs) |
| Platform | Remove extraneous load | DevEx | ≥80% paved‑path use; time‑saved | Ivory tower | Platform SLAs, roadmap, NPS |
| Enabling | Uplift capability | Germane learning | Time to competence ↓ | Permanent dependency | Engagement contract (exit criteria) |
| Complicated subsystem | Essential complexity | Deep expertise | Stability/perf | Knowledge hoarding | Interface/SLA; ADRs |

C) Team interaction modes
| Mode | Use | Timebox | Exit Signal | Guardrail |
|---|---|---|---|---|
| Collaboration | Discovery | 2–12 weeks | Breakthrough/decision | Written decision + owner |
| X‑as‑a‑Service | Stable capability | Ongoing | SLA adherence | API first; no “side meetings” |
| Facilitating | Close gaps | 2–8 weeks | Self‑sufficient team | Exit checklist met |

D) Organizational maturity (L1–L4)
| Area | L1 Chaos | L2 Defined | L3 Optimized | L4 Adaptive |
|---|---|---|---|---|
| Structure | Ad‑hoc | Stable teams | Topologies + ownership | Self‑reorg by load |
| Decisions | Loudest voice | Process‑slow | SLAs + ADRs | Edge‑pushed, reversible |
| Flow | Interruptions | Visible queues | Measured, improving | Near‑zero friction |
| Knowledge | Tribal | Wiki (stale) | Living docs | Embedded in platform |

Layer 2: Operating Systems
Decision architecture, metrics, cadence

A) Decision architecture
| Type | Scope | Reversibility | SLA | Decider | Artifact |
|---|---|---|---|---|---|
| Type 1 Strategic | Org‑wide | Low | ≤2 weeks | LT/ELT | Strategy doc |
| Type 2 Architectural | System | Medium | ≤1 week | TLs/Architects | ADR (with expiry) |
| Type 3 Tactical | Team | High | ≤48 hours | Team lead/Owner | Decision log |
| Type 4 Operational | Individual | Trivial | Minutes | IC | PR/comment |

Decision velocity maturity
- L1: Weeks‑months; escalation default; no record
- L2: Days‑weeks; meeting notes
- L3: Hours‑days; SLAs; ADRs; R&R clear
- L4: Minutes‑hours; edge decisions; quarterly guardrail tune

B) Measurement systems (north‑star chain)
| Layer | Examples | Cadence | Owner | Thresholds |
|---|---|---|---|---|
| Business | Revenue, Retention | Monthly | GM/VP | Trending up |
| Team outcome | Adoption, Perf | Weekly | Team | Clear linkage to business |
| System health | DORA, SLOs | Real‑time | Eng | DF daily+; LT <1d; MTTR <1h; CFR <10% |
| DevEx/load | PR times, load pulse | Weekly | EM/Platform | PR P50 <8h/P90 <24h; load stable |

New metrics that matter
- Decision latency (2‑way <48h; 1‑way <2w)
- Platform leverage (≥80% paved‑path adoption; NPS >50; time‑saved/eng‑month published)
- Flow efficiency ≥15% (35–50% elite)
- Outcome attribution ≥70% of work tied to measurable impact

C) Cadence rhythms (nested loops)
| Rhythm | Purpose | Key Activities | Output/Guardrail |
|---|---|---|---|
| Daily | Synchronize flow | PRs same‑day; queue hygiene; 2h focus | No >24h PRs |
| Weekly | Course correct | Outcome review; retro → 1 change; 1:1s | 1 improvement/week |
| Monthly | System health | Value‑stream, decision ledger, SLO/budget review | Bottleneck chosen + plan |
| Quarterly | Strategy & bets | Outcome roadmap; capacity 70/20/10; platform friction top‑3 | Targets reset; guardrails tuned |

Layer 3: Knowledge Architecture
Make learning and context flow with minimal meetings

A) Knowledge types and half‑lives
| Type | Half‑life | Capture | Distribution | Refresh |
|---|---|---|---|---|
| Declarative (facts) | 6–12m | Docs | Search, training | On change |
| Procedural (how‑to) | 3–6m | Runbooks | Onboarding, rotations | Process change |
| Conceptual (models) | 12–24m | ADRs, design docs | Reviews, talks | Paradigm shift |
| Tacit (experience) | Indefinite | Pairing/mentoring | Apprenticeship | Risk (bus factor) |
| Meta (how to learn) | Permanent | Retros, writing | Culture | Never |

B) Documentation hierarchy
| Level | Purpose | Audience | Update | Artifact (installable) |
|---|---|---|---|---|
| L4 Vision | Why | All | Yearly | Narrative |
| L3 Strategy | Where | Leads | Quarterly | Strategy doc |
| L2 Architecture | How | Eng | Monthly | Diagrams + ADRs (with expiry) |
| L1 Operations | Run/Support | On‑call | Weekly | Runbooks |
| L0 Code | Implementation | Devs | Continuous | Comments + tests |

C) Learning system maturity
- L1 Individual heroes → L2 Documented practices → L3 Learning org → L4 Evolutionary, AI‑augmented knowledge, self‑improving.

Layer 4: Platform as Lever
Make the right way the easiest way

A) Platform evolution
| Stage | Focus | Capabilities | Investment | ROI |
|---|---|---|---|---|
| 0 Chaos | Survival | None | 0% | Negative |
| 1 Tools | Sharing | Scripts/templates | 5–10% | 2× |
| 2 Services | Common functions | Auth, logging, deploy | 10–15% | 5× |
| 3 Platform | DevEx | Golden paths, self‑service, SLAs | 15–20% | 10× |
| 4 Ecosystem | Capability marketplace | AI‑assists, policy‑as‑code, observability‑by‑default | 20–25% | 20×+ |

B) Golden path architecture (batteries‑included)
| Layer | Component | Purpose | Target |
|---|---|---|---|
| Experience | CLI/IDE/Portal | One interface | Time‑to‑first‑change <1 day |
| Workflows | CI/CD, tests, observability | Fast feedback | Commit‑to‑prod <10m; local tests <60s |
| Services | Auth, data, messaging | Reuse primitives | Reuse ratio >50% |
| Infrastructure | Compute/network/storage | Elastic resources | Cost/txn trending down |
| Governance | Security/compliance/cost | Guardrails | Policy pass in CI; zero hard‑coded secrets |

C) Adoption patterns
| Pattern | Use | Success | Guardrail |
|---|---|---|---|
| Paved road | Default with escape hatch | 80–90% | Evidence for opt‑out; time‑bound |
| Rails | Rigid + fast | 60–70% | Known domains only |
| Buffet | Experimental | 30–40% | Sunset or platformize winners |
| Walled garden | Regulated/safety‑critical | 95%+ | Evidence capture automated |

Layer 5: Cultural Operating System
High standards × high safety, default‑open, deletion culture

A) Trust × standards matrix (operate in the Learning Zone)
- High standards + high safety: direct, kind, specific feedback; blameless postmortems; excellence is normal.

B) Talent system
| Area | Practice | Guardrail |
|---|---|---|
| Capacity mix | 70/20/10 (delivery/enablement/bets) | Publish & protect; don’t borrow from 20/10 |
| Promotions | Durable, system‑level impact | No heroics rewarded |
| Talent liquidity | Skills graph; rotations; pairing | Reduce key‑person risk quarterly |
| Transparency | Default‑open metrics/decisions | Sensitive exceptions only |
| Deletion culture | Monthly pruning (code/process/meetings) | Process half‑life; renew or remove |

Layer 6: Operational Excellence
Daily practices that compound into excellence

A) Code review maturity
| Level | Focus | Speed | Learning | Quality Impact |
|---|---|---|---|---|
| L1 Blocking | Find bugs | Days | Low | Negative |
| L2 Gatekeeping | Enforce rules | Hours | Medium | Neutral |
| L3 Collaborative | Share knowledge | Hours | High | Positive |
| L4 Coaching | Build capability | Minutes | Very high | Transformative |

B) Incident response evolution
| Maturity | Detection | Response | Recovery | Learning |
|---|---|---|---|---|
| Chaotic | Customer reports | Panic | Manual | None |
| Reactive | Basic alerts | War room | Documented | Postmortem |
| Proactive | Predictive | Defined roles | Automated | RCAs to backlog |
| Resilient | Self‑healing | Calm | Graceful degradation | System fixes |
| Anti‑fragile | Chaos engineering | Learning ops | Stronger after | Continuous evolution |

C) Technical debt classification
| Type | Description | Interest | Payment |
|---|---|---|---|
| Critical | Security/data loss | Exponential | Immediate |
| High | Blocks features/causes incidents | Compounding | This quarter |
| Medium | Slows dev | Linear | This year |
| Low | Cosmetic | Minimal | Opportunistic |
| Strategic | Intentional trade‑off | Controlled | Planned sunset |

D) Change safety defaults
- Trunk‑based development, feature flags, canaries, auto‑rollback, SLO‑gated pace.

Layer 7: Implementation Roadmap
Install and evolve the system

A) 30/60/90 with success criteria
| Phase | Focus | Actions | Success |
|---|---|---|---|
| Days 1–30 Foundation | Measure & reveal | Baseline DORA, PR cycle, flow, load pulse; publish team charters; kill 2 meetings | Metrics live; ownership visible |
| Days 31–60 Momentum | Quick wins | Fix 1 bottleneck (CI/env/reviews); launch golden path v1 + SLAs; decision SLAs live | 30% adoption; 50% SLA compliance |
| Days 61–90 Acceleration | Lock compounding | SLOs + flags/canary/rollback on 1 service; AI L2 (reviews/tests) with policy; start rotations | 60% teams on paved path; PR P50 <8h |

B) Phase 4 (Days 91–180) Transformation
- Embed: ≥80% paved‑path adoption; budgets gate delivery.
- Sustain: Metrics improve monthly; deletion log active.
- Expand: Portfolio experiments (5–20/qtr; ≥50–60% kill rate).

C) Context adaptations
| Size | Focus | Don’t do |
|---|---|---|
| Startup (<50) | Templates > platform; avoid sprawl | Premature platforming |
| Scale‑up (50–500) | Platform PM; trunk; decision SLAs | Team type proliferation |
| Enterprise (500–5000) | Governance‑as‑code; outcome ownership | Process accretion |
| Big Tech (5000+) | Talent liquidity; ecosystem platforms | Innovation suffocation |
| Regulated/Critical | Automated evidence; walled gardens | Manual compliance heroics |

Layer 8: Meta‑Patterns
Patterns that generate patterns

A) Recursive improvement engine
- Do → Improve → Improve the improvement → Transcend (question assumptions; redesign the game).

B) Three questions that matter
- What’s the constraint?
- What did we learn?
- What can we delete?

C) Ultimate test
- If your team disappeared for 3 months, would the system keep improving? If yes, you’ve transcended.

Guardrails & Thresholds (cheat sheet)
- PR cycle: P50 < 8h; P90 < 24h; same‑day reviews.
- Deploy cadence: Daily+ services; Weekly+ apps.
- Lead time: < 1 day. MTTR: < 1 hour. CFR: < 10% (elite < 5%).
- Flow efficiency: ≥ 15% baseline; 35–50% elite.
- Golden path: Clone‑to‑run < 5 min; tests < 60 sec; commit‑to‑prod < 10 min; ≥80% adoption; NPS > 50.
- Decision SLAs: 2‑way < 48h; 1‑way < 2 weeks; quarterly guardrail review.
- SLOs: ≥ 99% attainment; error budgets gate delivery pace.
- Cognitive load: Weekly pulse; < 3 context switches/day.
- Outcome attribution: ≥ 70% of work tied to measurable business impact.
- Deletion: 2+ deletions/month (code/process/meetings).

Minimal Install Pack (to move from L2 → L3 fast)
- Team charter template (outcome metric, users, SLOs, decision rights, dependencies)
- ADR template with expiry; decision ledger + SLAs (48h/2w), quarterly review
- Golden path v1 (one‑command scaffold; auth/telemetry/flags/security baked‑in; 5‑min README)
- Metrics dashboard (DORA, PR times, flow, decision latency, load pulse, SLOs, platform adoption/NPS)
- AI runbook + policy (allowed use, validation rubric, prompt/version registry; no sensitive data to external models)
- Reliability kit (SLOs/error budgets; trunk/flags/canary/rollback; blast‑radius budget)
- Process half‑life policy (renew with evidence or delete)
- Skills graph + rotation plan (talent liquidity)

Layer‑wise Maturity Spectra (roll‑up, L1→L4)
| Layer | L1 | L2 | L3 | L4 |
|---|---|---|---|---|
| L0 Physics | Ignored | Aware | Managed via metrics | Engineered for flow |
| L1 Org Models | Ad‑hoc | Defined | Topologies + ownership | Dynamic topology |
| L2 Operating | Slow, escalated | Process‑heavy | SLAs, cadence, ADRs | Edge decisions; self‑healing |
| L3 Knowledge | Tribal | Stale docs | Living docs + rotations | Embedded in platform |
| L4 Platform | DIY toil | Shared tools | Golden paths + SLAs | Ecosystem with governance‑as‑code |
| L5 Culture | Blame/low bar | “Nice” inconsistency | High standards + safety | Compounding capability |
| L6 Ops Excellence | Heroics | Reactive | Proactive + SLOs | Anti‑fragile |
| L7 Implementation | Slides | Partial | 30/60/90 executed | Compounding adoption |
| L8 Meta | Static | Occasional retros | Continuous improvement | Transcend + paradigm shifts |

Why this version is superior
- Single spine from principles to artifacts and thresholds.
- Prioritized control knobs and minimal install set.
- Falsifiable targets that turn intent into behavior.
- Anti‑theater safeguards (adoption, time‑saved, SLAs, process half‑life).
- Context‑ready (startup → big tech; regulated environments).

If you want, I can package this into:
- A Notion/Confluence kit (charters, ADRs, ledgers, SLAs, runbooks)
- A weighted scorecard/heatmap template
- A 6‑week A3 playbook to move any row from L2 → L3
