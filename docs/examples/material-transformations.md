# Material for MkDocs Content Transformations

This page demonstrates specific transformations of existing Compendium content using Material for MkDocs built-in components.

## Example 1: Law of Correlated Failure

### Original Content
```markdown
### The Reality: Correlated Failure Dominates
This calculation is dangerously wrong because it assumes independence. In reality:

[Mermaid diagram showing failure correlation]
```

### Enhanced with Material Components
!!! danger "The Reality: Correlated Failure Dominates"
    
    The traditional calculation is **dangerously wrong** because it assumes independence.
    
    === "Shared Hardware"
    
        ```mermaid
        graph TD
            PS[Power Supply] --> R1[Rack 1]
            PS --> R2[Rack 2]
            PS --> R3[Rack 3]
            PS -.->|Single point<br/>of failure| OUTAGE[Mass Outage]
        ```
        
        !!! failure "Real Incident"
            GitHub's 2018 outage: UPS failure took down entire availability zone
    
    === "Shared Software"
    
        ```mermaid
        graph TD
            CONFIG[Config Service] --> S1[Service 1]
            CONFIG --> S2[Service 2]
            CONFIG --> S3[Service 3]
            CONFIG -.->|Bad config| OUTAGE[Cascade Failure]
        ```
        
        !!! failure "Real Incident"
            Cloudflare's 2019 outage: Bad regex deployed globally
    
    === "Shared Dependencies"
    
        ```mermaid
        graph TD
            DEPLOY[Deployment Tool] --> S1[Service 1]
            DEPLOY --> S2[Service 2]
            DEPLOY --> S3[Service 3]
            DEPLOY -.->|Bug in tool| OUTAGE[Simultaneous Failure]
        ```
        
        !!! failure "Real Incident"
            AWS S3 2017: Typo in deployment script affected thousands of services

## Example 2: Circuit Breaker States

### Original Table
```markdown
<div class="responsive-table" markdown>

| State | Behavior | When to Transition |
|-------|----------|--------------------|
| CLOSED | Let requests through | After X failures → OPEN |
| OPEN | Reject immediately | After timeout → HALF-OPEN |
| HALF-OPEN | Test with few requests | Success → CLOSED, Failure → OPEN |

</div>

```

### Enhanced with Cards and Admonitions

<div class="grid cards" markdown>

- :material-check-circle:{ .lg .middle } **CLOSED State**

    ---
    
    Normal operation - all requests pass through
    
    !!! success "Behavior"
        - Monitor all requests
        - Count failures
        - Reset counter on success
    
    !!! warning "Transition"
        Opens after **5 consecutive failures** or **50% error rate**

- :material-cancel:{ .lg .middle } **OPEN State**

    ---
    
    Protection mode - fail fast without calling service
    
    !!! danger "Behavior"
        - Reject all requests immediately
        - Return cached/default response
        - Start recovery timer
    
    !!! info "Transition"
        Moves to HALF-OPEN after **30 second timeout**

- :material-help-circle:{ .lg .middle } **HALF-OPEN State**

    ---
    
    Recovery test - limited traffic to check health
    
    !!! tip "Behavior"
        - Allow 10% of requests through
        - Monitor success rate closely
        - Gradual traffic increase
    
    !!! abstract "Transition"
        - **3 successes** → CLOSED
        - **1 failure** → OPEN

</div>

## Example 3: Failure Types

### Original List Format
```markdown
**Examples**:
- **Power**: UPS failure takes down entire rack (GitHub, 2018)
- **Cooling**: HVAC failure causes thermal shutdown
- **Network**: Core switch failure isolates entire availability zone
- **Geographic**: Natural disaster affects entire region
```

### Enhanced with Collapsible Cards

??? danger "Correlated Hardware Failures"

    === "Power Failures"
        
        !!! failure "GitHub 2018 Incident"
            **What happened**: UPS battery failure during maintenance  
            **Impact**: 12 hours of degraded service  
            **Root cause**: Correlated battery age across units  
            **Lesson**: Stagger battery replacement schedules
        
        ```mermaid
        graph LR
            UPS[UPS Failure] --> R1[Rack 1<br/>20 servers]
            UPS --> R2[Rack 2<br/>20 servers]
            UPS --> R3[Rack 3<br/>20 servers]
            R1 & R2 & R3 --> OUT[60 servers offline]
        ```
    
    === "Cooling Failures"
        
        !!! failure "AWS 2017 Incident"
            **What happened**: HVAC control system malfunction  
            **Impact**: Thermal shutdown of 3 data halls  
            **Root cause**: Software bug in temperature controller  
            **Lesson**: Diverse HVAC control systems
        
        <details>
        <summary>Temperature Cascade Timeline</summary>
        
<div class="responsive-table" markdown>

        | Time | Temperature | Action |
        |------|-------------|--------|
        | 00:00 | 68°F | Normal operation |
        | 00:15 | 75°F | Warning alerts |
        | 00:30 | 85°F | Throttle CPUs |
        | 00:45 | 95°F | Emergency shutdown |

</div>

        
        </details>
    
    === "Network Failures"
        
        !!! failure "Azure 2019 Incident"
            **What happened**: BGP configuration error  
            **Impact**: Region-wide connectivity loss  
            **Root cause**: Automation script with no bounds checking  
            **Lesson**: Staged rollouts for network changes

## Example 4: Testing Strategies

### Original Bullet List
```markdown
def test_correlated_failure():
    # Don't just fail random instances
    # Fail entire racks, AZs, or regions
    failure_scenarios = [
        fail_entire_rack("rack-42"),
        fail_availability_zone("us-east-1a"),
        corrupt_shared_config("service-mesh-config"),
    ]
```

### Enhanced with Tabs and Task Lists

!!! tip "Chaos Engineering for Correlation Testing"

    === "Infrastructure Failures"
        
        Test physical infrastructure correlations:
        
        - [ ] Power failure simulation
            ```python
            fail_entire_rack("rack-42")
            ```
        - [ ] Network partition test
            ```python
            partition_availability_zone("us-east-1a")
            ```
        - [ ] Storage array failure
            ```python
            fail_storage_cluster("ssd-cluster-1")
            ```
    
    === "Software Failures"
        
        Test software dependency correlations:
        
        - [ ] Configuration corruption
            ```python
            corrupt_shared_config("service-mesh-config")
            ```
        - [ ] Deployment tool failure
            ```python
            fail_deployment_pipeline("jenkins-prod")
            ```
        - [ ] Certificate expiration
            ```python
            expire_certificate("*.example.com")
            ```
    
    === "Time-Based Failures"
        
        Test temporal correlations:
        
        - [ ] Clock skew injection
            ```python
            introduce_clock_skew("ntp-server-1", offset=300)
            ```
        - [ ] Leap second handling
            ```python
            simulate_leap_second()
            ```
        - [ ] Timezone changes
            ```python
            change_system_timezone("UTC-5")
            ```

## Example 5: Complex Decision Framework

### Original Table
```markdown
<div class="responsive-table" markdown>

| Question | Yes → Use Circuit Breaker | No → Alternative |
|----------|---------------------------|------------------|
| Calling external services? | ✅ Essential | ⚠️ Consider for internal |
| Risk of cascade failures? | ✅ High priority | ⚠️ Simple retry may suffice |

</div>

```

### Enhanced with Admonitions and Annotations

!!! abstract "Circuit Breaker Decision Framework"
    
    Follow this decision tree to determine if you need a circuit breaker:
    
    ```mermaid
    graph TD
        A[Service Call] -->|External?| B{External Service?}
        B -->|Yes| C[✅ Use Circuit Breaker]
        B -->|No| D{High Traffic?>1000 RPS?}
        D -->|Yes| E{Cascade Risk?}
        D -->|No| F[⚠️ Simple Timeout]
        E -->|Yes| C
        E -->|No| G[⚠️ Retry + Backoff]
    ```
    
    ??? tip "Quick Reference Guide"
        
<div class="responsive-table" markdown>

        | Scenario | Circuit Breaker? | Alternative | Reasoning |
        |----------|-----------------|-------------|-----------|
        | External API calls | ✅ **Required** | None | Protect against provider outages |
        | Database queries | ✅ **Recommended** | Connection pooling | Prevent connection exhaustion |
        | Internal microservices | ✅ **If >1000 RPS**(1) | Simple retry | High traffic needs protection |
        | Cache lookups | ❌ **Not needed** | Timeout only | Already fast-failing |
        | Message queue | ✅ **For consumers**(2) | Dead letter queue | Prevent poison messages |

</div>

        { .annotate }
        
        1. High traffic increases cascade risk exponentially
        2. Producers typically use async patterns instead

## Example 6: Monitoring Dashboard

### Original Metrics List
```markdown
Key Metrics to Track:
- Circuit state changes
- Request volume when open
- Recovery success rate
- Fallback execution rate
- Latency percentiles (P50, P95, P99)
```

### Enhanced with Visual Dashboard

!!! example "Production Monitoring Dashboard"
    
    === "Health Overview"
        
        <div class="grid cards" markdown>
        
        - :material-heart-pulse:{ .lg .middle } **System Health**
            
            ---
            
            🟢 **Healthy**: 45 services  
            🟡 **Degraded**: 3 services  
            🔴 **Failed**: 1 service
        
        - :material-chart-line:{ .lg .middle } **Success Rate**
            
            ---
            
            **Overall**: 99.94%  
            **With Fallbacks**: 99.98%  
            **Without CB**: ~94%
        
        - :material-timer:{ .lg .middle } **Recovery Time**
            
            ---
            
            **Average**: 2.3 min  
            **P50**: 1.8 min  
            **P95**: 4.2 min
        
        </div>
    
    === "Detailed Metrics"
        
        !!! info "Circuit State Distribution"
            ```
            CLOSED:     ████████████████████ 90%
            OPEN:       ██ 8%
            HALF-OPEN:  █ 2%
            ```
        
        !!! warning "Top Failing Services"
            1. **payment-service**: 15 trips today (−5 from yesterday)
            2. **inventory-db**: 8 trips today (+2 from yesterday)
            3. **shipping-api**: 3 trips today (no change)
    
    === "Alerts Configuration"
        
        !!! danger "Critical Alerts"
            - [ ] More than 10% circuits OPEN
            - [ ] Any circuit OPEN > 10 minutes
            - [ ] Fallback failure rate > 5%
        
        !!! warning "Warning Alerts"
            - [ ] Circuit flapping (>5 transitions/hour)
            - [ ] Increased trip frequency (+50% from baseline)
            - [ ] High latency before trips (>2x normal)

## Best Practices Summary

!!! success "Do's"
    - Use admonitions for important callouts
    - Group related content with tabs
    - Add visual indicators with icons
    - Make long content collapsible
    - Provide interactive checklists

!!! failure "Don'ts"
    - Don't create custom CSS when built-in components work
    - Don't nest too many levels (max 3)
    - Don't overuse animations or colors
    - Don't hide critical information in collapsed sections
    - Don't mix different component styles inconsistently