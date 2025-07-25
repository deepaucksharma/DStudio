---
title: "Law 1: The Law of Inevitable and Correlated Failure"
description: Any component can fail, and failures are often correlated, not independent
type: law
difficulty: expert
reading_time: 8 min
prerequisites: ["part1-axioms/index.md"]
status: complete
last_updated: 2025-07-23
---

# Law 1: The Law of Inevitable and Correlated Failure ⚡

[Home](/) > [The 7 Laws](/part1-axioms/) > [Law 1: Correlated Failure](/part1-axioms/law1-failure/) > Concept

!!! quote "Core Principle"
    Any component can fail, and failures are often correlated, not independent.

!!! progress "Your Journey Through The 7 Laws"
    - [x] **Law 1: Correlated Failure** ← You are here
    - [ ] Law 2: Asynchronous Reality
    - [ ] Law 3: Emergent Chaos
    - [ ] Law 4: Multidimensional Optimization
    - [ ] Law 5: Distributed Knowledge
    - [ ] Law 6: Cognitive Load
    - [ ] Law 7: Economic Reality

## The Naïve Model vs Reality

### What We're Taught: Independent Failure
Traditional distributed systems education begins with a simple probabilistic model:
- If a server has 99.9% uptime, it fails 0.1% of the time
- With 3 independent replicas, the probability of all failing is 0.001³ = 10⁻⁹
- Therefore, we've achieved "nine nines" of reliability!

### The Reality: Correlated Failure Dominates
This calculation is dangerously wrong because it assumes independence. In reality:

```mermaid
graph TD
    subgraph "Shared Dependencies Create Correlation"
        PS[Power Supply] --> R1[Rack 1]
        PS --> R2[Rack 2]
        PS --> R3[Rack 3]
        
        NET[Network Switch] --> R1
        NET --> R2
        NET --> R3
        
        CONFIG[Config Service] --> S1[Service 1]
        CONFIG --> S2[Service 2]
        CONFIG --> S3[Service 3]
        
        DEPLOY[Deployment Tool] --> S1
        DEPLOY --> S2
        DEPLOY --> S3
    end
    
    PS -.->|Single point<br/>of failure| OUTAGE[Mass Outage]
    NET -.->|Single point<br/>of failure| OUTAGE
    CONFIG -.->|Single point<br/>of failure| OUTAGE
    DEPLOY -.->|Single point<br/>of failure| OUTAGE
    
    style PS fill:#e74c3c
    style NET fill:#e74c3c
    style CONFIG fill:#e74c3c
    style DEPLOY fill:#e74c3c
    style OUTAGE fill:#c0392b,color:#fff
```

## A Taxonomy of Real-World Failure Modes

=== "Hardware Failures"

    !!! failure "Correlated Hardware Failures"
        
        **Definition**: Multiple components fail simultaneously due to shared physical dependencies.
        
        | Type | Example | Impact | Real Incident |
        |------|---------|--------|---------------|
        | **Power** | UPS failure | Entire rack down | GitHub 2018: 24hr outage |
        | **Cooling** | HVAC failure | Thermal shutdown | Facebook 2013: Zone offline |
        | **Network** | Core switch | AZ isolation | AWS 2011: US-East disaster |
        | **Geographic** | Natural disaster | Region offline | Japan 2011: Tsunami impact |
        
        !!! tip "Key Insight"
            Physical proximity creates correlation. "Availability zones" exist precisely to break these correlations.

=== "Gray Failures"

    !!! warning "Gray Failures: The Silent Killers"
        
        **Definition**: System doesn't crash but suffers severe performance degradation.
        
        **Characteristics:**
        - [x] Appears healthy to monitoring (heartbeats succeed)
        - [x] Actual performance makes system unusable
        - [x] Often caused by resource exhaustion
        - [x] Harder to detect than crash failures
        
        ```python hl_lines="8-10"
        # Gray failure example
        def health_check():
            return "OK"  # Passes! ✓
        
        def process_request():
            # Takes 30 seconds instead of 30ms
            with open('/full/disk/file.log', 'a') as f:
                # Disk at 100% - technically works but...
                f.write(data)  # 1000x slower than normal
                # Client already timed out!
        ```
        
        !!! example "Real Example"
            **Scenario**: Disk reaches 100% utilization  
            **Symptom**: Queries take 30s instead of 30ms  
            **Detection**: Health checks pass, but users complain

### 3. Metastable Failures
**Definition**: System stable at low load but enters persistent failure state above a threshold.

**The Metastability Pattern**:
1. System operates normally at 60% load
2. Small spike pushes to 70% load
3. Performance degrades, causing retries
4. Retries push load to 90%
5. More degradation, more retries
6. System stuck at 100% load even after initial spike subsides

```mermaid
graph LR
    subgraph "Metastable State Machine"
        STABLE[Stable<br/>60% load] -->|Load spike| THRESH[Threshold<br/>70% load]
        THRESH -->|Performance<br/>degrades| RETRY[Retries<br/>increase load]
        RETRY -->|More load| OVERLOAD[Overload<br/>100% load]
        OVERLOAD -->|Retries<br/>continue| OVERLOAD
        OVERLOAD -.->|Requires manual<br/>intervention| STABLE
    end
    
    style STABLE fill:#27ae60
    style THRESH fill:#f39c12
    style RETRY fill:#e74c3c
    style OVERLOAD fill:#c0392b,color:#fff
```

**Real Example**: Facebook's 2019 outage caused by cascading cache misses creating a retry storm.

### 4. Cascading Failures
**Definition**: One component's failure triggers failures in dependent components.

**Common Patterns**:
1. **Thundering Herd**: Cache fails → all requests hit database → database fails
2. **Retry Storms**: Service A fails → Service B retries → overwhelms Service A further
3. **Circuit Breaker Cascade**: One service triggers circuit breakers → appears as failure to dependents

### 5. Software Correlation Failures
**Definition**: Shared software creates simultaneous failures across "independent" systems.

**Examples**:
- **Bug in common library**: Affects all services using it
- **Configuration push**: Bad config deployed everywhere at once
- **Time-based bugs**: Leap second bugs, Y2K-style issues
- **Certificate expiry**: All services using same cert fail together

**Case Study - Cloudflare 2019**:
```yaml
# Bad regex deployed globally
pattern: ".*(?:.*=.*)"  # Catastrophic backtracking
# Result: CPU exhaustion across all edge servers worldwide
```

## Beyond Traditional Fault Tolerance

### Failure Domains and Blast Radius

**Definition**: A failure domain is a set of components that share fate.

```mermaid
graph TD
    subgraph "Hierarchical Failure Domains"
        subgraph "Region US-East"
            subgraph "AZ 1"
                subgraph "Rack A"
                    S1[Server 1]
                    S2[Server 2]
                end
                subgraph "Rack B"
                    S3[Server 3]
                    S4[Server 4]
                end
            end
            subgraph "AZ 2"
                subgraph "Rack C"
                    S5[Server 5]
                    S6[Server 6]
                end
            end
        end
    end
    
    style S1 fill:#3498db
    style S2 fill:#3498db
    style S3 fill:#3498db
    style S4 fill:#3498db
    style S5 fill:#2ecc71
    style S6 fill:#2ecc71
```

**Design Principles**:
1. **Identify all failure domains**: Power, network, software, configuration, human
2. **Minimize blast radius**: Limit impact of any single failure
3. **Create anti-correlation**: Ensure replicas are in different failure domains
4. **Test domain assumptions**: Validate independence through chaos engineering

### Dependency Analysis and Shared Fate

**The Dependency Graph Method**:
1. Map all dependencies (explicit and implicit)
2. Identify shared dependencies
3. Calculate correlation coefficients
4. Design to minimize correlation

```python
def analyze_failure_correlation(services):
    """Calculate correlation in failure probability"""
    dependency_graph = build_dependency_graph(services)
    shared_deps = find_shared_dependencies(dependency_graph)
    
    correlation_matrix = {}
    for s1, s2 in combinations(services, 2):
        shared = shared_deps.get((s1, s2), [])
# Correlation increases with shared dependencies
        correlation = len(shared) / max(
            len(dependency_graph[s1]), 
            len(dependency_graph[s2])
        )
        correlation_matrix[(s1, s2)] = correlation
    
    return correlation_matrix
```

## Designing for Correlated Failure

### 1. Cellular Architecture
Divide system into isolated cells that fail independently:

```mermaid
graph LR
    subgraph "Cell 1"
        LB1[Load Balancer] --> API1[API]
        API1 --> DB1[Database]
        API1 --> CACHE1[Cache]
    end
    
    subgraph "Cell 2"
        LB2[Load Balancer] --> API2[API]
        API2 --> DB2[Database]
        API2 --> CACHE2[Cache]
    end
    
    subgraph "Cell 3"
        LB3[Load Balancer] --> API3[API]
        API3 --> DB3[Database]
        API3 --> CACHE3[Cache]
    end
    
    ROUTER[Cell Router] --> LB1
    ROUTER --> LB2
    ROUTER --> LB3
```

### 2. Bulkheads and Isolation
Prevent failure propagation between components:

```java
// Thread pool isolation example
class BulkheadService {
    // Separate thread pools for different operations
    private final ExecutorService criticalPool = 
        Executors.newFixedThreadPool(50);
    private final ExecutorService analyticsPool = 
        Executors.newFixedThreadPool(10);
    
    public CompletableFuture<Response> handleCritical(Request req) {
        return CompletableFuture.supplyAsync(
            () -> processCritical(req), 
            criticalPool  // Isolated from analytics
        );
    }
}
```

### 3. Progressive Rollout and Canary Deployments
Limit correlation from software changes:

```yaml
deployment_strategy:
  stages:
    - name: "Canary"
      percentage: 1
      duration: "10m"
      rollback_on_error: true
    - name: "Early Adopters"  
      percentage: 10
      duration: "1h"
      rollback_on_error: true
    - name: "Half"
      percentage: 50
      duration: "2h"
      rollback_on_error: false  # Manual decision
    - name: "Full"
      percentage: 100
```

## Theoretical Foundations

### Percolation Theory
Network failures can be modeled using percolation theory:
- Below critical threshold: failures remain isolated
- Above threshold: failures percolate through entire system
- Design goal: Stay below percolation threshold

### Common Mode Analysis
Borrowed from safety engineering:
1. Identify all common modes of failure
2. Calculate probability of common mode vs independent
3. Design diversity to reduce common mode probability

## Practical Implications

### Testing for Correlation
```python
# Chaos engineering experiment
def test_correlated_failure():
# Don't just fail random instances
# Fail entire racks, AZs, or regions
    failure_scenarios = [
        fail_entire_rack("rack-42"),
        fail_availability_zone("us-east-1a"),
        corrupt_shared_config("service-mesh-config"),
        introduce_clock_skew("ntp-server-1"),
        exhaust_shared_resource("connection-pool")
    ]
    
    for scenario in failure_scenarios:
        impact = measure_system_impact(scenario)
        assert impact.customer_impact < SLA_THRESHOLD
```

### Monitoring for Correlation
Track correlation metrics, not just individual component health:

```sql
-- Correlation detection query
SELECT 
    s1.service_name,
    s2.service_name,
    CORR(s1.error_rate, s2.error_rate) OVER (
        ORDER BY timestamp 
        RANGE BETWEEN INTERVAL '5 minutes' PRECEDING 
        AND CURRENT ROW
    ) as error_correlation
FROM service_metrics s1
JOIN service_metrics s2 
    ON s1.timestamp = s2.timestamp
WHERE correlation > 0.8  -- High correlation threshold
```

## Check Your Understanding

!!! question "Self-Assessment Questions"

    === "Question 1"
        Why can't we just add more redundancy to solve availability problems?
        
        ??? success "Answer"
            Because failures are correlated! Adding redundancy without breaking correlation domains just creates more components that fail together. Three servers in the same rack with the same power supply gives you 3x the cost but not 3x the reliability.

    === "Question 2"
        What makes gray failures particularly dangerous?
        
        ??? success "Answer"
            Gray failures are dangerous because:
            1. They pass health checks (system appears "healthy")
            2. They cause severe performance degradation
            3. They're harder to detect than complete failures
            4. They can trigger cascading failures as timeouts propagate

    === "Question 3"
        How do metastable failures differ from regular overload?
        
        ??? success "Answer"
            Regular overload recovers when load decreases. Metastable failures persist even after load returns to normal because the system enters a "bad state" (e.g., full queues, exhausted connection pools) that prevents recovery without intervention.

## The Ultimate Lesson

!!! abstract "Key Takeaway"
    **"The question is not whether a component will fail, but which components will fail together."**
    
    Robust distributed systems aren't built by assuming independence—they're built by identifying and breaking correlations. Every shared dependency is a potential correlation. Every correlation is a single point of failure waiting to happen.

## Further Reading

- "Why Do Computers Stop and What Can Be Done About It?" - Jim Gray
- "The Network is Reliable" - Peter Bailis and Kyle Kingsbury
- "Metastable Failures in Distributed Systems" - Bronson et al.

---

<div class="page-nav" markdown>
[:material-arrow-left: Overview](/part1-axioms/) | 
[:material-arrow-up: The 7 Laws](/part1-axioms/) | 
[:material-arrow-right: Law 2: Asynchronous Reality](/part1-axioms/law2-asynchrony/)
</div>