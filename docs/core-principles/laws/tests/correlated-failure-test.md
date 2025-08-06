---
title: "Law 1 Test: Correlated Failure Assessment"
description: Interactive learning module and self-assessment for understanding correlated failures in distributed systems
type: test
difficulty: advanced
prerequisites:
  - core-principles/laws/correlated-failure.md
status: complete
last_updated: 2025-01-29
---

# Learning Module: Law 1 - The Law of Inevitable and Correlated Failure

!!! info "Learning Objectives"
    By completing this module, you will:
    
    - Build intuitive understanding of how failures are secretly linked
    - Identify and categorize different types of correlated failures
    - Design systems resilient to correlated failure patterns
    - Apply mathematical models to calculate real availability
    - Recognize correlation patterns in production incidents

## Module Navigation

=== "Foundational Concepts"

    ### Section 1: Core Principles
    
    #### Question 1: The Flaw of Independence
    
    The common practice of calculating system availability by multiplying the uptime of its individual servers (e.g., 99.9% × 99.9%) is fundamentally flawed because it ignores a single, critical variable. What is that variable, and why does its omission lead to a dangerous overestimation of reliability?
    
    ??? tip "Think About It"
        Consider what happens when two servers share the same rack, power supply, or software deployment...
    
    ??? success "Answer & Explanation"
        **The critical variable is the correlation coefficient (ρ)**, which represents the degree to which components are linked by shared dependencies.
        
        The formula `Availability = Uptime(A) × Uptime(B)` is only valid if ρ = 0 (perfect independence). In reality:
        
        - Server A and Server B might share a network switch (ρ = 0.6)
        - A power distribution unit (ρ = 0.8)  
        - A buggy software patch (ρ = 1.0)
        
        When a shared dependency fails, it takes both servers down together. Ignoring this correlation leads to an availability estimate that is **orders of magnitude more optimistic than reality**, creating a dangerous false sense of security.
        
        **Real Formula:** `Real_Availability = min(components) × (1 - max(correlation_coefficient))`
    
    #### Question 2: Observing Failure Patterns
    
    Contrast **Cascade Failure** with **Common Cause Failure**. What is the key difference in how you would observe these two types of failures on a monitoring dashboard's timeline graph?
    
    ??? tip "Visualization Hint"
        Think about the temporal relationship between failures...
    
    ??? success "Answer & Explanation"
        **On a timeline graph:**
        
        - **Common Cause Failure:** Sharp, **simultaneous** spike in error rates across multiple unrelated services at the **exact same instant**
        - **Cascade Failure:** Series of **sequential** spikes—Service A's errors spike first, followed seconds or minutes later by Service B, then Service C
        
        **Key observational difference:** Simultaneity vs. sequence.
        
        - Common cause failures are simultaneous because the root failure (e.g., expired certificate) affects everyone at once
        - Cascades are sequential because they propagate through the system's call graph; the failure has to travel from one component to the next
        
        ```
        Common Cause:    A: ████
                        B: ████  (all at T=0)
                        C: ████
        
        Cascade:        A: ████
                        B:   ████  (T=30s)
                        C:     ████  (T=60s)
        ```
    
    #### Question 3: Identifying the Specter
    
    A service is experiencing a "retry storm"—clients are retrying failed requests so aggressively that the service is overwhelmed and cannot recover. Some might call this a Cascade, while others might call it a Metastable State. What is the critical difference between these two failure patterns?
    
    ??? tip "Consider the Dynamics"
        What happens when you remove the initial trigger in each case?
    
    ??? success "Answer & Explanation"
        **A retry storm is best described as a Metastable State.**
        
        While it involves a cascade of retries, the defining characteristic of a **Metastable State** is the **positive feedback loop** that becomes self-sustaining:
        
        - **Simple Cascade:** Linear domino effect (A → B → C)
        - **Metastable State:** Circular, self-perpetuating trap (A fails → B retries → A more overloaded → A fails more → B retries more)
        
        The system enters a new, stable-but-broken equilibrium where:
        - High number of retries guarantees high number of failures
        - Which in turn guarantees high number of retries
        - Cannot recover on its own without external intervention (like shedding load)
        
        **Mathematical Model:**
        ```
        dRetries/dt = α × Failures - β × Success
        dLoad/dt = γ × Retries
        
        At metastable equilibrium: dRetries/dt = 0
        (System stuck in high-retry, high-failure state)
        ```
    
    #### Question 4: The Power of Isolation
    
    Explain how **Shuffle Sharding** protects a system from a widespread server failure. Contrast it with traditional load-balancing. What is the primary trade-off?
    
    ??? tip "Think Probabilistically"
        Consider the probability of impact for each user...
    
    ??? success "Answer & Explanation"
        **Traditional Load Balancing:**
        - Spreads all traffic across all servers
        - If 30% of servers fail, 100% of users are impacted (30% of their requests hit dead servers)
        
        **Shuffle Sharding:**
        - Assigns each user a small, dedicated subset of servers (their "shard")
        - If 30% of total servers fail, only users whose personal shards overlap significantly with failed set are affected
        - Probability of impact for any given user becomes tiny
        
        **Example:**
        ```
        Traditional: 100 servers, 30 fail
        Impact: 100% of users (each has 30% failed requests)
        
        Shuffle Sharding: 100 servers, 5 per user, 30 fail
        P(user affected) = C(5,3) × C(95,27) / C(100,30)
                        ≈ 0.001% chance
        ```
        
        **Primary Trade-off:** Increased complexity
        - Need deterministic routing layer to map users to shards
        - Monitoring becomes complex (can't just look at aggregate health)
        - Must monitor health of potentially millions of tiny, overlapping virtual shards
        - This trades off against the Law of Cognitive Load

=== "Architectural Review"

    ### Section 2: Vulnerability Analysis
    
    !!! warning "Scenario: PhotoSphere Architecture Review"
        You are conducting an architectural review for "PhotoSphere," a new photo-sharing application designed for high availability.
        
        **Proposed Architecture:**
        
        - **Web/App Tier:** Single auto-scaling group of 50 servers running both web and application logic
        - **Deployment:** Blue-green deployment strategy. "Blue" runs old code, "green" gets new code. Load balancer switches all traffic at once
        - **Database:** High-performance, single-node relational database with network-attached RAID-10 volume, hourly snapshots
        - **Caching & Session:** Three-node Redis cluster
        - **Infrastructure:** All components deployed across three AZs in us-east-1 for "maximum resilience"
    
    #### Task 1: Architectural Risk Assessment
    
    Identify three distinct, high-severity risks of correlated failure in this design. For each risk, categorize it and describe a plausible scenario where it leads to a major outage.
    
    - [ ] Identified Data Tier Risk
    - [ ] Identified Deployment Risk  
    - [ ] Identified Control Plane Risk
    - [ ] Described plausible failure scenarios
    
    ??? danger "Risk 1: Data Tier Risk"
        **Single-node database is a critical SPOF (Single Point of Failure)**
        
        - RAID protects against disk failure, but not against:
          - Database software crashes
          - CPU saturation from slow query
          - Data corruption
        
        **Scenario:** Poorly written query gets deployed, consuming 100% CPU on database node. Every one of the 50 application servers will see database connections hang and timeout. **Result: 100% application unavailability.**
        
        **Correlation:** ρ = 1.0 (perfect correlation through shared dependency)
    
    ??? danger "Risk 2: Deployment Risk"
        **All-at-once blue-green deployment = correlated deployment failure**
        
        **Scenario:** New code has subtle memory leak that only appears under production load. When load balancer flips 100% of traffic to "green":
        - All servers begin leaking memory simultaneously
        - Within an hour, all run out of memory and crash in unison
        - **Result: Total outage**
        
        **Correlation:** ρ = 1.0 (simultaneous exposure to same bug)
    
    ??? danger "Risk 3: Control Plane Risk"
        **Three-node Redis cluster is a subtle shared dependency**
        
        While distributed across AZs, it's a single cluster.
        
        **Scenario:** Bug in Redis client library or misconfiguration causes:
        - "Keyspace storm" or invalid data written to session store
        - Corrupts session state for all users simultaneously
        - All users logged out or experience errors
        - **Result: System-wide functional outage**
        
        **Correlation:** ρ = 0.95 (near-perfect through shared state)
    
    #### Task 2: Challenging Assumptions
    
    Your Lead Architect defends the design: 
    
    > "This architecture is resilient. We are spread across three AZs, which is the industry best practice. The database is on an enterprise-grade RAID volume, and blue-green deployments are instantaneous and safe."
    
    Write a clear, respectful counter-argument addressing each point and explaining how they represent a misunderstanding of correlated failure.
    
    ??? example "Model Counter-Argument"
        "I agree that using three AZs is a great first step for infrastructure resilience, but it only protects us from one type of failure. We've designed a system where the components have a high correlation coefficient (ρ), meaning their fates are linked.
        
        **Regarding the three AZs:**
        - While servers are in different AZs, they all talk to the same single database instance
        - Correlation between server in AZ-A and server in AZ-B is nearly ρ=1.0
        - Both depend on that single database
        - If database fails, AZ distribution is irrelevant
        
        **Regarding the RAID volume:**
        - Protects against physical disk failure
        - Doesn't protect against database process failure
        - All servers correlated by dependency on single postgres.exe process
        
        **Regarding blue-green deployment:**
        - Actually maximizes correlation
        - Switching 100% of traffic at once ensures if there's a latent bug, 100% of servers exposed simultaneously
        - Guarantees full-fleet failure
        - Canary deployment would actively de-correlate deployment risk"

=== "Live Incident Diagnosis"

    ### Section 3: Incident Response Simulation
    
    !!! alert "Scenario: Black Friday Crisis"
        You are the incident commander for a major e-commerce platform. During Black Friday peak, the site suddenly becomes extremely slow.
        
        **Incoming Signals:**
        
        1. **Symptom:** p99 latency for "Checkout" API jumped from 200ms to 15,000ms
        2. **Initial Triage:** CPU and memory on CheckoutService servers high but not maxed. No new deployments in 12 hours
        3. **Observation 1:** InventoryService (Checkout dependency) also has high latency. Its servers look completely idle (low CPU, low memory)
        4. **Observation 2:** InventoryService's database shows huge spike in active connections, many queries in "waiting for lock" state
        5. **Observation 3:** ProductCatalogService (no direct connection to Checkout/Inventory) also reporting extreme latency, its database also showing connection spikes and lock waits
    
    #### Task 1: Hypothesis Formation
    
    Based on the evidence, form a primary hypothesis. What specific type of correlated failure is likely occurring?
    
    - [ ] Identified failure type
    - [ ] Explained connection between observations
    - [ ] Explained why InventoryService servers are idle
    - [ ] Explained why unrelated ProductCatalogService is affected
    
    ??? success "Primary Hypothesis"
        **Most likely failure: Common Cause Failure from shared, contended resource in data tier, creating Bulkhead Failure pattern**
        
        **Evidence Analysis:**
        
        1. **Common cause failure** - Two unrelated services (Inventory and ProductCatalog) failing same way at same time → shared dependency
        
        2. **Shared dependency** - Likely database system/platform, even if instances are different. Clue: "waiting for lock" state
        
        3. **Root cause hypothesis** - Low-priority, high-volume process (analytics job) started, acquiring aggressive locks on popular rows/tables in both databases
        
        4. **Why InventoryService servers idle** - Classic Bulkhead Failure:
           - All threads stuck in connection pool
           - Waiting for database response
           - Database waiting for lock release
           - Server CPU idle but service unresponsive
        
        5. **Why CheckoutService slow** - Cascade effect from root common cause:
           - CheckoutService depends on InventoryService
           - InventoryService timing out
           - Creates downstream cascade
        
        **Correlation Analysis:**
        - Database lock contention: ρ = 1.0 (perfect correlation)
        - Service impact: ρ = 0.85 (high correlation through shared pattern)
    
    #### Task 2: Investigation Plan
    
    List three specific, targeted questions you would ask or queries you would run to confirm your hypothesis.
    
    ??? example "Investigation Steps"
        **1. Confirm Database Locks:**
        ```sql
        -- PostgreSQL
        SELECT * FROM pg_locks WHERE NOT granted;
        -- Looking for: process ID (PID) of query holding lock
        ```
        
        **2. Identify Locking Query:**
        ```sql
        SELECT query, application_name, usename, query_start 
        FROM pg_stat_activity 
        WHERE pid = [locking_pid];
        -- Looking for: SELECT...FOR UPDATE or long transaction from analytics user
        ```
        
        **3. Correlate Across Services:**
        - "Show me graph of all background jobs that started around 14:00 UTC"
        - Cross-reference with user/application name from locking query
        - Confirm it's same analytics job in both systems

=== "Strategic Redesign"

    ### Section 4: Resilience Roadmap
    
    !!! info "Context"
        After the Black Friday incident, it was discovered that a background analytics job had started running, acquiring aggressive locks on certain rows in both the Inventory and Product Catalog databases. You are tasked with designing a more resilient architecture.
    
    #### Create a Phased Resiliency Roadmap
    
    ##### Phase 1: Immediate Stabilization (Next 2 Weeks)
    
    Describe tactical changes to prevent recurrence. Justify why these are the right first steps.
    
    ??? success "Phase 1 Solution"
        **Change: Implement resource isolation for background jobs using Bulkheads**
        
        **Implementation:**
        - Create separate, lower-priority database user roles for analytical/background jobs
        - Configure at database level:
          - Statement timeouts (max 30 seconds)
          - Lower connection pool limit
          - Lower priority scheduling
        
        **Justification:**
        - Fastest, most effective tactical fix
        - Acts as database-level bulkhead
        - Ensures runaway analytics query cannot:
          - Consume all resources
          - Hold locks indefinitely
        - Protects primary transactional workload
        
        **Correlation Impact:** Reduces ρ from 1.0 to ~0.3
    
    ##### Phase 2: Long-Term Resilience (Next 6 Months)
    
    Describe fundamental architectural change to permanently solve the problem.
    
    ??? success "Phase 2 Solution"
        **Change: Implement CQRS (Command Query Responsibility Segregation) pattern**
        
        **Architecture:**
        ```mermaid
        graph LR
            T[Transactional DB] -->|CDC| S[Stream]
            S --> A[Analytics DB]
            
            W[Writes] --> T
            R[Analytics] --> A
            
            style T fill:#4ecdc4
            style A fill:#95e1d3
        ```
        
        **Implementation:**
        1. Main transactional database handles commands (writes) only
        2. Use CDC (Change Data Capture) like Debezium to stream changes
        3. Separate analytics-optimized data warehouse (Snowflake/BigQuery)
        4. All analytical jobs run against read-optimized copy
        
        **Benefits:**
        - Physically and logically decouples workloads
        - Impossible for analytics to acquire locks affecting checkouts
        - Correlation reduced to near-zero (ρ < 0.05)
    
    ##### Integration & Trade-offs
    
    Analyze impact on other distributed systems laws. What are you sacrificing to gain resilience?
    
    ??? info "Trade-off Analysis"
        **Impact on Law 7 (Economic Reality):**
        - CQRS significantly more expensive
        - Now paying for:
          - Transactional database
          - Real-time streaming pipeline (Kafka + Debezium)
          - Analytical data warehouse
        - Infrastructure costs could 2-3x
        - **Trade-off:** Spending money to buy resilience
        
        **Impact on Law 6 (Cognitive Load):**
        - Architecture far more complex
        - Team needs to understand:
          - Multiple data stores
          - Data streaming
          - Potential replication lag
        - Number of "moving parts" increased dramatically
        - **Trade-off:** Trading simplicity for resilience
        - **Mitigation:** Heavy investment in observability, automation, training

=== "Self-Assessment"

    ### Progress Checklist
    
    Use this checklist to track your understanding:
    
    #### Conceptual Understanding
    - [ ] I can explain why independence assumptions are flawed
    - [ ] I can identify the five specters of correlated failure
    - [ ] I understand the correlation coefficient and its impact
    - [ ] I can distinguish cascade from metastable failures
    
    #### Practical Application
    - [ ] I can spot correlated failure risks in architecture diagrams
    - [ ] I can calculate real availability using correlation
    - [ ] I can design isolation strategies (cells, bulkheads, shuffle sharding)
    - [ ] I can diagnose correlation patterns from monitoring data
    
    #### Advanced Topics
    - [ ] I understand metastable states and positive feedback loops
    - [ ] I can model failure propagation mathematically
    - [ ] I can design chaos experiments to test correlation
    - [ ] I can perform cost-benefit analysis for correlation breaking
    
    !!! tip "Next Steps"
        If you checked all boxes, you're ready to:
        
        1. Review real production incidents in your organization
        2. Identify hidden correlations in your current architecture
        3. Design and run chaos experiments
        4. Implement correlation-breaking patterns
        
        If some boxes are unchecked, revisit those sections in the [main law documentation](../correlated-failure.md).

## Quick Reference Card

!!! abstract "Key Formulas & Patterns"
    **Real Availability with Correlation:**
    ```
    Real_Availability = min(components) × (1 - max(ρ))
    ```
    
    **Five Specters Quick ID:**
    - **BLAST** → Single heat-map column red
    - **CASCADE** → Sequential failure propagation
    - **GRAY** → Green health checks, screaming users
    - **METASTABLE** → Self-sustaining failure loop
    - **COMMON** → Simultaneous failures at exact timestamp
    
    **Correlation Breaking Patterns:**
    1. **Cells** - Island model with < 35% capacity per cell
    2. **Shuffle Sharding** - Personalized server subsets
    3. **Bulkheads** - Resource isolation boundaries
    4. **True Diversity** - Different providers/implementations
    
    **Emergency Actions:**
    - Load shedding for metastable states
    - Circuit breakers for cascades
    - Isolation for blast radius
    - Staggering for common cause

## Additional Resources

!!! info "Continue Learning"
    - [📖 Full Law Documentation](../correlated-failure.md)
    - [🔬 Chaos Engineering Guide](../../../pattern-library/resilience/chaos-engineering.md)
    - [🏗️ Cell Architecture Pattern](../../../pattern-library/architecture/cell-based.md)
    - [🛡️ Bulkhead Pattern](../../../pattern-library/resilience/bulkhead.md)
    
    **Real Incident Post-Mortems:**
    - [AWS S3 Outage Analysis](https://aws.amazon.com/message/41926/)
    - [Facebook BGP Incident](https://engineering.fb.com/2021/10/05/networking-traffic/outage-details/)
    - [Cloudflare Regex Outage](https://blog.cloudflare.com/cloudflare-outage/)