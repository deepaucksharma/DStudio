---
title: "Law 1 Exam: Correlated Failure Mastery Assessment"
description: Concept-focused examination testing deep understanding of correlated failures without heavy arithmetic
type: exam
difficulty: hard
prerequisites:
  - core-principles/laws/correlated-failure.md
  - core-principles/laws/tests/correlated-failure-test.md
time_limit:
  hard: 90m
  very_hard: 180m
open_book: true
calculator: not_needed
status: complete
last_updated: 2025-01-29
---

# Law 1 Mastery Exam: Correlated Failure

!!! warning "Exam Instructions"
    **Format:** Open book | **Calculator:** Not needed
    
    - Focus on **conceptual understanding**, not calculations
    - Answers should be **1-3 paragraphs** or a **small diagram**
    - Grading focuses on **identifying patterns** and **practical solutions**
    - Reference formulas are provided - apply them conceptually

## Quick Reference Formulas

!!! info "Core Formulas (No Heavy Math Required)"
    - **Correlated Failure:** If two services share ≥ 1 critical dependency, failures are *not* independent
    - **Real Availability:** `Real_Availability ≈ min(components) × (1 - max(ρ))`
    - **Blast Radius:** `Impact = failed_cells / total_cells`
    - **Correlation Coefficient:** ρ = 0 (independent), ρ = 1 (perfectly correlated)

---

## Section 1: Hard Questions (90 minutes)

=== "H-1: Shared Dependency Analysis"
    
    ### Scenario
    Two microservices (`Checkout`, `Inventory`) live in the same Availability Zone but rely on a *shared* Redis cluster. During a spike, the cluster fails.
    
    **Question A:** Which Law explains why *both* services drop, even though you deployed them redundantly?
    
    **Question B:** Name one architecture change that would have limited the blast radius.
    
    ??? tip "Hint"
        Think about what makes components truly independent vs. just appearing independent.
    
    ??? success "Expected Answer"
        **A: Law 1 (Correlated Failure)**
        - The shared Redis cluster creates a hidden correlation (ρ ≈ 1.0)
        - Despite being "redundantly deployed," both services share the same critical dependency
        - When Redis fails, both services fail simultaneously - classic common cause failure
        
        **B: Architecture Changes (any one):**
        - **Cell/Bulkhead Pattern:** Separate Redis instances per service
        - **Shuffle Sharding:** Each service gets a subset of Redis nodes
        - **Circuit Breaker:** Fail fast with degraded mode when Redis unavailable
        - **Local Caching:** Reduce Redis dependency with service-level caches

=== "H-2: Clock Synchronization"
    
    ### Scenario
    A product team insists on a *global* mutex (based on wall-clock time) to enforce exactly-once coupon redemption across 3 regions.
    
    **Question:** List **two concrete reasons** this violates the Law of Asynchronous Reality.
    
    ??? tip "Hint"
        Consider what "simultaneous" means across geographic distances.
    
    ??? success "Expected Answer"
        **Reason 1: No Universal "Now"**
        - Clock drift between regions means no single definition of "current time"
        - Even with NTP, clocks can drift by milliseconds to seconds
        - Mutex ordering becomes observer-dependent (who has the "correct" time?)
        
        **Reason 2: Physical Latency Limits**
        - Minimum inter-region latency ≥ distance/speed_of_light
        - NYC ↔ Singapore: minimum 85ms one-way
        - Global lock acquisition blocks user operations for hundreds of milliseconds
        - Creates terrible user experience and violates real-time requirements

=== "H-3: Gray Failure Detection"
    
    ### Scenario
    A dashboard shows p95 latency is stable, yet users complain of "lag" every evening.
    
    **Question:** Suggest **one Gray Failure hypothesis** and the **single metric** you would add to detect it.
    
    ??? tip "Hint"
        What might health checks miss that users experience?
    
    ??? success "Expected Answer"
        **Gray Failure Hypothesis:**
        Health checks hit cached responses or lightweight endpoints while real user requests face resource contention (e.g., database lock contention, connection pool exhaustion, or network congestion on user-facing paths).
        
        **Metric to Add:**
        **HC-minus-User Latency Delta:** `real_user_p95 - health_check_p95`
        - Alert when gap > 500ms for 3 minutes
        - Directly measures the "lie" health checks tell
        - Alternative: Client-side latency instrumentation or synthetic user journeys

=== "H-4: CAP Trade-offs"
    
    ### Scenario
    Your system promises *AP* in the CAP triangle. A network partition occurs and both partitions process writes.
    
    **Question:** What additional mechanism must you design for *after* the partition heals, and why?
    
    ??? tip "Hint"
        What happens to the divergent states when communication resumes?
    
    ??? success "Expected Answer"
        **Required Mechanism: Conflict Resolution / Merge Strategy**
        
        Since you chose AP (Availability + Partition tolerance), you sacrificed Consistency. Both partitions accepted writes independently, creating divergent states.
        
        **Options include:**
        - **CRDTs (Conflict-free Replicated Data Types):** Automatic, deterministic merging
        - **Last-Write-Wins (LWW):** Simple but may lose data
        - **Vector Clocks:** Track causality for intelligent merging
        - **Application-level reconciliation:** Business logic determines merge strategy
        
        Without this, the system cannot converge to a single state after partition healing.

=== "H-5: Alert Fatigue"
    
    ### Scenario
    During a game launch, your service scales from 10 to 100 instances in 3 minutes. On-call engineers face 700 alerts.
    
    **Question:** Using the Cognitive Load Law, name **two alert-quality criteria** that would justify automatically suppressing most of them.
    
    ??? tip "Hint"
        What makes an alert worth waking someone up at 3 AM?
    
    ??? success "Expected Answer"
        **Two Key Criteria (from the 5-point framework):**
        
        1. **Actionable:** Can the engineer actually do something about it?
           - Suppress: "Instance i-abc123 CPU at 71%" (auto-scaling handles this)
           - Keep: "Payment API rejecting all requests" (needs immediate action)
        
        2. **Unique/Deduplicated:** Is this alert redundant with others?
           - Suppress: 90 identical "connection timeout" alerts from same root cause
           - Keep: First alert in the cascade chain
        
        Other valid criteria: Urgent (user-facing impact), Clear (unambiguous), Accurate (low false-positive rate)

=== "H-6: Economic Reality"
    
    ### Scenario
    Identify the **single sentence** that breaks the Law of Economic Reality:
    
    > "For Black Friday we will triple our instance count across three cloud providers to guarantee zero downtime at any cost."
    
    ??? tip "Hint"
        Which phrase ignores fundamental constraints?
    
    ??? success "Expected Answer"
        **Problematic sentence:** "...to guarantee zero downtime at *any cost*."
        
        This violates Economic Reality because:
        - **No budget is infinite** - "any cost" is impossible
        - **Diminishing returns** - Each additional 9 of availability costs 10x more
        - **Opportunity cost** - Resources spent here can't be used elsewhere
        - **Business trade-off** - At some point, the cost exceeds the business value
        
        Better phrasing: "...to achieve 99.99% availability within our $X budget."

=== "H-7: Thundering Herd"
    
    ### Scenario
    Every service in one Kubernetes cluster polls a config map every 30s at the top of the minute (:00, :30).
    
    **Question:** Which failure pattern could this create and what **one-line patch** breaks the pattern?
    
    ??? tip "Hint"
        What happens when everyone acts at exactly the same time?
    
    ??? success "Expected Answer"
        **Failure Pattern: Thundering Herd / Synchronization Storm**
        - Creates emergent chaos through synchronized behavior
        - All services hit the API server simultaneously
        - Can overwhelm the control plane, causing cascading failures
        
        **One-line Patch:**
        ```python
        poll_interval = 30 + random.uniform(-5, 5)  # Add jitter
        ```
        
        Or in configuration:
        ```yaml
        pollInterval: 30s
        jitter: 5s  # Randomize ±5 seconds
        ```
        
        This breaks the synchronization by distributing load over time.

=== "H-8: Clock Drift"
    
    ### Scenario
    True or False: "If a database replica never becomes primary, it can tolerate unbounded clock drift."
    
    **Question:** Briefly justify your answer.
    
    ??? tip "Hint"
        How do replicas use timestamps even when not accepting writes?
    
    ??? success "Expected Answer"
        **False** - Replicas still need bounded clock drift.
        
        **Justification:**
        - **Read timestamps** affect staleness guarantees ("read-after-write" consistency)
        - **Causal ordering** depends on timestamps to order events correctly
        - **TTL/Expiry** operations use wall-clock time for cache invalidation
        - **Monitoring/Alerting** relies on accurate timestamps for correlation
        - **Snapshot consistency** requires temporal coordination
        
        Example: With unbounded drift, a replica might serve data that appears to be from the "future" relative to the primary, violating causality and confusing applications.

---

## Section 2: Very Hard Questions (3 hours)

=== "VH-1: Spacetime Budget Memo"
    
    ### Challenge
    Your CEO wants *1 ms* end-to-end trade order confirmation from Singapore to New York. Write a **short memo (<250 words)** explaining:
    1. Which physical law makes this impossible
    2. A practical SLA proposal
    3. One design compromise
    
    ??? example "Model Answer"
        **MEMO: Trade Latency Physical Limits**
        
        **To:** CEO
        **Re:** Singapore-NYC 1ms Target
        
        **Physical Impossibility:**
        The speed of light creates an absolute minimum latency of 85ms one-way between Singapore and NYC (15,000 km at 300,000 km/s through fiber optic cables, which travel at ~0.67c). Round-trip physical minimum: 170ms. The 1ms target violates fundamental physics - no amount of engineering can overcome this.
        
        **Practical SLA Proposal:**
        - **150ms p50** (near theoretical minimum with excellent infrastructure)
        - **200ms p99** (accounting for routing, processing, congestion)
        - **500ms p99.9** (handling retries and failovers)
        
        **Design Compromise:**
        Implement **regional pre-confirmation** with eventual global settlement:
        1. Singapore node confirms locally in <5ms with risk modeling
        2. Provides provisional confirmation to user
        3. Asynchronously settles with NYC
        4. Compensates rare conflicts via business logic
        
        This trades **global consistency** for **user experience**, accepting small financial risk for dramatic latency improvement. Similar to how credit cards authorize locally but settle globally.
        
        **Budget Impact:** Requires $2M annually for premium network routes and regional infrastructure.
        
        [CEO: This is why high-frequency traders pay millions for microsecond advantages - physics is expensive to fight]

=== "VH-2: Failure Spectrum Map"
    
    ### Challenge
    Create a table matching each of the five "Specters of Correlated Failure" to **one specific monitoring signal** you would track.
    
    ??? example "Model Answer"
        | **Specter** | **Monitoring Signal** | **Implementation** | **Alert Threshold** |
        |-------------|----------------------|-------------------|-------------------|
        | **BLAST RADIUS** | Cell heat-map column density | Count services failing per cell | >30% services in single cell red |
        | **CASCADE** | Retry rate amplification factor | `retry_rate(t) / retry_rate(t-60s)` | Amplification >2x sustained 30s |
        | **GRAY FAILURE** | HC-minus-user latency gap | `user_p95 - health_check_p95` | Gap >500ms for 3 minutes |
        | **METASTABLE** | Queue depth knee detection | Second derivative of queue size | d²Q/dt² > 0 (acceleration) |
        | **COMMON CAUSE** | Simultaneous failure correlation | Services failing within same 1s window | >3 unrelated services at T₀ |
        
        **Visual Dashboard Layout:**
        ```
        ┌─────────────────┬──────────────────┐
        │ BLAST: Heat Map │ CASCADE: Timeline│
        │ [Cell][Cell]    │ Retry━━━╱╱╱      │
        │ [▓▓▓▓][░░░░]    │ Load ━━━━╱       │
        ├─────────────────┼──────────────────┤
        │ GRAY: Gap Meter │ META: Queue Knee │
        │ HC  ▄▄▄▄        │      ╱│          │
        │ User ▄▄▄▄▄▄▄▄   │    ╱  │←knee     │
        ├─────────────────┴──────────────────┤
        │ COMMON: Correlation Matrix [T=now] │
        │ A B C D → All failed at 14:23:17   │
        └─────────────────────────────────────┘
        ```

=== "VH-3: Trade-off Narrative"
    
    ### Challenge
    A startup can't decide between strong consistency and 99.99% availability for its social feed. In **three sentences**:
    1. Outline the trade-off
    2. Reference Multidimensional Optimization and CAP
    3. Recommend for a "likes & comments" feed
    
    ??? example "Model Answer"
        **Three-Sentence Analysis:**
        
        1. **The Trade-off:** According to CAP theorem and Multidimensional Optimization, you can maximize only 2 of 3 properties (Consistency, Availability, Partition-tolerance); choosing strong consistency with 99.99% availability means partition-tolerance must be sacrificed, but network partitions are inevitable in distributed systems.
        
        2. **The Reality:** Since partition-tolerance is mandatory (networks fail), you must choose between CP (consistent but less available) or AP (available but eventually consistent); the Law of Multidimensional Optimization states that optimizing consistency necessarily degrades availability under fixed resources.
        
        3. **The Recommendation:** For a social feed displaying likes and comments, choose AP with eventual consistency - users tolerate seeing slightly stale like counts (consistency relaxed) far better than seeing error pages (availability lost), and business impact of temporary inconsistency is minimal compared to downtime.

=== "VH-4: Cell Design Violation"
    
    ### Challenge
    You built four cells, each carrying ≤25% of user load. Marketing now wants a *single* "global leaderboard" API from one Redis instance.
    
    **Task:** Explain in **≤150 words** why this violates cell architecture and propose an alternative.
    
    ??? example "Model Answer"
        **Why This Violates Cell Architecture:**
        
        A single global Redis instance creates a **common cause failure point** with ρ=1.0 correlation across all cells. When (not if) this Redis fails, 100% of users lose leaderboard functionality, defeating the entire purpose of cellular architecture which aims to limit blast radius to 25%. This shared dependency transforms four independent cells into four facades of a monolith.
        
        **Alternative Pattern:**
        
        Implement **per-cell aggregation with async fan-in**:
        1. Each cell maintains local leaderboard in cell-specific Redis
        2. Background process aggregates into eventual-consistent global view
        3. Use CRDT counters for conflict-free merging
        4. Serve "global" leaderboard from nearest cell's cache
        
        This maintains cell isolation (ρ<0.2) while providing global view. If one cell fails, others continue serving their cached global state. Trade-off: accepts 30-60 second staleness for 4x resilience improvement.
        
        **Key principle:** Never let a feature requirement break your failure isolation boundaries.

=== "VH-5: Runbook Compression"
    
    ### Challenge
    The current incident runbook is 12 pages. Using Cognitive Load principles, list **four concrete techniques** to compress it for a fatigued engineer at 3 AM.
    
    ??? example "Model Answer"
        **Four Compression Techniques:**
        
        **1. Binary Decision Tree (Progressive Disclosure)**
        ```
        Start → Is it customer-facing?
               ├─ YES → Page incident commander → Go to CRITICAL-PATH.md
               └─ NO → Is it data loss risk?
                      ├─ YES → Freeze deployments → Go to DATA-RECOVERY.md
                      └─ NO → Continue diagnosis → Go to TROUBLESHOOT.md
        ```
        Cognitive benefit: Only see relevant information, reducing decision fatigue.
        
        **2. Visual Cheat Sheet (One Page)**
        - System diagram with numbered components
        - Red annotations showing common failure points
        - QR codes linking to detailed procedures
        - Cognitive benefit: Visual processing faster than text at 3 AM
        
        **3. Alert-Linked Sections**
        - Each alert includes direct link: `[RUNBOOK: Section 4.2]`
        - Jump straight to relevant procedure
        - No searching through 12 pages
        - Cognitive benefit: Reduces navigation overhead
        
        **4. Three-Step Page Limit**
        - Each page: DETECT (symptoms) → DIAGNOSE (1 command) → ACT (1 action)
        - Complex procedures link to appendix
        - Example: "High CPU? → Run `top -p $(pgrep app)` → If >80%, restart with `./restart.sh`"
        - Cognitive benefit: Chunking reduces working memory load

---

## Grading Rubric

!!! abstract "Assessment Criteria"
    
    ### Hard Section (80 points total)
    | Criterion | Points | What We Look For |
    |-----------|--------|-------------------|
    | **Identifies Correct Law/Pattern** | 40 | Correctly names the law, identifies failure pattern |
    | **Clear, Concise Reasoning** | 25 | Logical explanation, uses correct terminology |
    | **Practical Mitigation** | 15 | Proposes realistic, implementable solutions |
    
    **Passing Score:** 60/80 (75%)
    
    ### Very Hard Section (120 points total)
    | Criterion | Points | What We Look For |
    |-----------|--------|-------------------|
    | **Cross-Law Integration** | 60 | Connects multiple laws, shows system thinking |
    | **Depth of Analysis** | 40 | Nuanced understanding, considers trade-offs |
    | **Real-World Applicability** | 20 | Solutions work in production, acknowledges constraints |
    
    **Passing Score:** 90/120 (75%)

## Study Tips

!!! tip "Exam Preparation"
    1. **Focus on Concepts, Not Math**
       - Understand what ρ=0.9 means, don't calculate it
       - Know when patterns apply, not their exact formulas
    
    2. **Practice Pattern Recognition**
       - Review the five specters until you can identify them instantly
       - Study real incident post-mortems
    
    3. **Think in Trade-offs**
       - Every solution has a cost
       - No free lunch in distributed systems
    
    4. **Use Simple Diagrams**
       - A small sketch often explains better than paragraphs
       - Practice drawing cells, dependencies, and failure paths

## Answer Submission

!!! info "How to Submit"
    For self-study, write answers in markdown files:
    ```
    /tests/answers/law1-exam/
    ├── h1-shared-dependency.md
    ├── h2-clock-sync.md
    ├── h3-gray-failure.md
    ├── h4-cap-tradeoffs.md
    ├── h5-alert-fatigue.md
    ├── h6-economic-reality.md
    ├── h7-thundering-herd.md
    ├── h8-clock-drift.md
    ├── vh1-spacetime-memo.md
    ├── vh2-failure-spectrum.md
    ├── vh3-tradeoff-narrative.md
    ├── vh4-cell-violation.md
    └── vh5-runbook-compression.md
    ```

---

*Remember: This exam tests understanding, not memorization. If you can explain WHY something fails and HOW to fix it, you've mastered the law.*