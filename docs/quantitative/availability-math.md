---
title: Availability Math & Nines
description: "Understanding availability percentages and their real impact on system uptime and downtime calculations"
type: quantitative
difficulty: beginner
reading_time: 45 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---


# Availability Math & Nines

**Building reliable systems from unreliable parts**

## The Nines

```
90% (1 nine)     = 36.5 days/year downtime
99% (2 nines)    = 3.65 days/year  
99.9% (3 nines)  = 8.76 hours/year
99.99% (4 nines) = 52.6 minutes/year
99.999% (5 nines)= 5.26 minutes/year
```

## Visual Availability Framework

```mermaid
graph TB
    subgraph "Availability Patterns"
        subgraph "Series (Chain) - Multiply"
            S1[Service A<br/>99.9%] --> S2[Service B<br/>99.9%]
            S2 --> S3[Service C<br/>99.9%]
            S3 --> SR[System: 99.7%<br/>(0.999³)]
        end
        
        subgraph "Parallel (Redundant) - Complement"
            P1[Service A<br/>99.9%]
            P2[Service B<br/>99.9%]
            P1 & P2 --> PR[System: 99.9999%<br/>(1 - 0.001²)]
        end
        
        subgraph "Mixed: Chain + Redundancy"
            M1[LB<br/>99.99%] --> M2A[App A<br/>99.9%]
            M1 --> M2B[App B<br/>99.9%]
            M2A --> M3[DB<br/>99.9%]
            M2B --> M3
            M3 --> MR[System: 99.89%]
        end
    end
    
    subgraph "Availability Impact Visualization"
        AV1[1 Nine: 36.5 days/year]
        AV2[2 Nines: 3.65 days/year]
        AV3[3 Nines: 8.76 hours/year]
        AV4[4 Nines: 52.6 min/year]
        AV5[5 Nines: 5.26 min/year]
        
        AV1 --> AV2
        AV2 --> AV3
        AV3 --> AV4
        AV4 --> AV5
    end
    
    style SR fill:#ffcccc
    style PR fill:#ccffcc
    style MR fill:#ffffcc
    style AV5 fill:#ccffcc
    style AV1 fill:#ffcccc
```

## Availability Calculations

### Series (AND): Multiply
```
A → B → C = A × B × C
99.99% → 99.9% → 99.9% = 99.79%
```

### Parallel (OR): Complement
```
A | B = 1 - (1-A) × (1-B)
Two 99.9% DBs = 1 - 0.001² = 99.9999%
```

### N+M Redundancy

<div class="truth-box">
<h4>📈 N+M Redundancy Formula</h4>

<div style="background: #E3F2FD; padding: 20px; border-radius: 8px; margin: 15px 0;">
  <p><strong>Scenario</strong>: Need N components working, have N+M total</p>
  <p><strong>System fails when</strong>: More than M components fail</p>
  
  <div style="background: white; padding: 15px; border-radius: 5px; margin: 15px 0; font-family: 'Courier New', monospace;">
    <strong>For identical components with availability A:</strong><br><br>
    Availability = Σ<sub>k=0</sub><sup>M</sup> C(N+M,k) × A<sup>(N+M-k)</sup> × (1-A)<sup>k</sup>
  </div>
  
  <div style="margin-top: 15px;">
    <strong>Example: 3+2 Redundancy (Need 3, Have 5)</strong>
    <table style="width: 100%; margin-top: 10px;">
      <tr style="background: #BBDEFB;">
        <th style="padding: 8px;">Component Availability</th>
        <th style="padding: 8px;">System Availability</th>
        <th style="padding: 8px;">Improvement</th>
      </tr>
      <tr>
        <td style="padding: 8px; text-align: center;">90%</td>
        <td style="padding: 8px; text-align: center;">99.14%</td>
        <td style="padding: 8px; text-align: center; color: #4CAF50;">+10x</td>
      </tr>
      <tr style="background: #F5F5F5;">
        <td style="padding: 8px; text-align: center;">99%</td>
        <td style="padding: 8px; text-align: center;">99.999%</td>
        <td style="padding: 8px; text-align: center; color: #4CAF50;">+100x</td>
      </tr>
      <tr>
        <td style="padding: 8px; text-align: center;">99.9%</td>
        <td style="padding: 8px; text-align: center;">99.99999%</td>
        <td style="padding: 8px; text-align: center; color: #4CAF50;">+1000x</td>
      </tr>
    </table>
  </div>
</div>
</div>

## System Modeling

```python
# Active-Active
LB(99.99%) → [App1|App2](99.9999%) → DB(99.9%) = 99.89%

# Multi-Region
Two 99.8% regions = 1 - 0.002² = 99.9996%

# Microservice Chain
Five 99.9% services = 0.999⁵ = 99.5%
(With circuit breakers: maintain 99.9%)
```

## Improving Availability

```
Strategy         Cost   Impact
--------         ----   ------
Better HW        $$     99% → 99.9%
Redundancy       $      99% → 99.99%  
Multi-region     $$     99.9% → 99.99%
Fewer deps       $      Big gains
Faster recovery  $      Big gains
```

## Error Budgets

```python
99.9% SLO = 0.1% error budget = 43.8 min/month

if budget_remaining > risk * 2: deploy()
elif budget_remaining > 0: needs_approval()
else: focus_on_reliability()
```

## Cloud Reality

```
Service    SLA      Reality   Your Max
EC2        99.99%   99.995%   99.99%
S3         99.99%   99.99%+   99.99%
RDS        99.95%   99.97%    99.95%

Your app: 99.9% × EC2 × ELB × RDS = 99.83% theoretical
Reality: 99.5-99.7%
```

## MTBF and MTTR

### Visual MTBF/MTTR Relationship

```mermaid
graph LR
    subgraph "System Lifecycle"
        WORK1[Working] --> FAIL1[Failed]
        FAIL1 --> WORK2[Working]
        WORK2 --> FAIL2[Failed]
        FAIL2 --> WORK3[Working]
    end
    
    subgraph "Time Measurements"
        MTBF1[MTBF<br/>Mean Time Between Failures]
        MTTR1[MTTR<br/>Mean Time To Recovery]
        
        WORK1 -.->|Measure| MTBF1
        FAIL1 -.->|Measure| MTTR1
    end
    
    subgraph "Availability Formula"
        FORMULA[Availability = MTBF / (MTBF + MTTR)]
        
        EXAMPLE1[MTBF=30d, MTTR=30min<br/>→ 99.93%]
        EXAMPLE2[MTBF=30d, MTTR=15min<br/>→ 99.97%]
        
        FORMULA --> EXAMPLE1
        FORMULA --> EXAMPLE2
    end
    
    subgraph "Improvement Strategies"
        PREVENT[Improve MTBF<br/>Testing (+20%)<br/>Reviews (+30%)<br/>Redundancy (+100%)]
        
        RECOVER[Improve MTTR<br/>Monitoring (-50%)<br/>Automation (-80%)<br/>Runbooks (-30%)]
        
        INSIGHT[🎯 Key Insight:<br/>Faster recovery ><br/>preventing failures!]
    end
    
    style INSIGHT fill:#fff3cd,stroke:#856404
    style EXAMPLE2 fill:#ccffcc
    style RECOVER fill:#ccffcc
```

```python
Availability = MTBF / (MTBF + MTTR)

MTBF=30d, MTTR=30min → 99.93%
MTBF=30d, MTTR=15min → 99.97%

Improving MTBF: Testing (+20%), Reviews (+30%), Redundancy (+100%)
Improving MTTR: Monitoring (-50%), Automation (-80%), Runbooks (-30%)

Faster recovery > preventing failures!
```

## Availability Patterns

### Failover Impact
```
10s = negligible, 1min = -0.1 nine, 5min = -0.5 nine, 30min = -1 nine
```

### Degraded Modes
```
Full: 99.9%, Read-only: 99.99%, Maintenance: 99.999%
(Better than binary up/down)
```

### Cascading Failures
```
A(99.9%) needs B+C(99.9%) = 99.7% without breakers
With circuit breakers = 99.9% (graceful degradation)
```

## Economics

```
Nines   Cost    Complexity
99%     1x      Simple
99.9%   3x      Moderate  
99.99%  10x     High
99.999% 100x    Extreme

$10M business: 99%→99.9% costs $200K, saves $90K = -55% ROI
$1B business: Same upgrade saves $9M = +4400% ROI!
```

## Practical Guidelines

```python
# Design for failure
try:
    result = service.call()
except ServiceUnavailable:
    result = cache_or_default()
except Timeout:
    result = circuit_breaker.fallback()

# Track availability
availability = successes / total_requests
if availability < target_sla:
    alert()
```

## Law Connections

### Law 1: Failure
```mermaid
graph TD
    A[Component Failure] --> B[System Response]
    B --> C{Architecture}
    C -->|Series| D[System Fails]
    C -->|Parallel| E[System Survives]
    C -->|N+M| F[Degraded Operation]
    
    style A fill:#ff6b6b
    style E fill:#90ee90
    style F fill:#ffd700
```

**Key Insight**: Availability math quantifies [Law 1: Failure ⛓️](/part1-axioms/law1-failure/) - we can't prevent failures, but we can design systems that survive them.

### Law 4: Trade-offs
- Redundancy requires 2x resources for high availability
- N+M patterns trade capacity for reliability
- During failures, remaining capacity must handle full load

### Law 4: Trade-offs (CAP Trade-offs)
```python
# Consistency vs Availability Trade-off
Strong Consistency + Partition = No Availability
High Availability + Partition = Inconsistency
# CAP theorem in action
```

### Law 7: Economics
- As systems grow, probability of component failure increases
- More components = more failure modes
- Availability targets become harder to maintain at scale

## Visual Availability Architecture

### Series vs Parallel - Visual Impact

```mermaid
graph LR
    subgraph "Series (99% each) = 97%"
        A1[LB 99%] --> B1[App 99%] --> C1[DB 99%]
    end
    
    subgraph "Parallel (99% each) = 99.99%"
        A2[App1 99%]
        A3[App2 99%]
        A2 --> D[Either Works]
        A3 --> D
    end
    
    style A1 fill:#ffa500
    style D fill:#90ee90
```

### The Nines Visualization

```text
99% (2 nines):    ████████████████████░ 3.65 days/year
99.9% (3 nines):  ███████████████████▉░ 8.76 hours/year  
99.99% (4 nines): ████████████████████░ 52.6 minutes/year
99.999% (5 nines):████████████████████░ 5.26 minutes/year

Cost to achieve:  $    $$    $$$    $$$$$$$$
Complexity:       ▂    ▄     ▆      █████████
```

## Decision Framework: Choosing Availability Target

```mermaid
flowchart TD
    Start[Business Requirements]
    Start --> Revenue{Revenue Impact?}
    
    Revenue -->|>$1M/hour| Five[Target: 99.999%<br/>5.26 min/year]
    Revenue -->|>$10K/hour| Four[Target: 99.99%<br/>52.6 min/year]
    Revenue -->|>$1K/hour| Three[Target: 99.9%<br/>8.76 hours/year]
    Revenue -->|<$1K/hour| Two[Target: 99%<br/>3.65 days/year]
    
    Five --> Arch1[Multi-region<br/>Active-active<br/>Zero downtime deploys]
    Four --> Arch2[Multi-AZ<br/>Hot standby<br/>Blue-green deploys]
    Three --> Arch3[Single region<br/>Cold standby<br/>Rolling updates]
    Two --> Arch4[Basic redundancy<br/>Manual failover<br/>Scheduled maintenance]
    
    style Five fill:#ff6b6b
    style Four fill:#ffa500
    style Three fill:#ffd700
    style Two fill:#90ee90
```

## Real-World Application: E-commerce Platform

```mermaid
graph TB
    subgraph "User Traffic"
        U[Users]
    end
    
    subgraph "Edge Layer 99.99%"
        CDN[CDN]
        WAF[WAF]
    end
    
    subgraph "Application Layer"
        LB1[LB 99.99%]
        LB2[LB 99.99%]
        App1[App 99.9%]
        App2[App 99.9%]
        App3[App 99.9%]
    end
    
    subgraph "Data Layer"
        DB1[(Primary 99.9%)]
        DB2[(Replica 99.9%)]
        Cache[Cache 99.99%]
    end
    
    U --> CDN
    CDN --> WAF
    WAF --> LB1
    WAF --> LB2
    LB1 --> App1
    LB1 --> App2
    LB2 --> App2
    LB2 --> App3
    App1 --> Cache
    App2 --> Cache
    App3 --> Cache
    Cache --> DB1
    DB1 -.-> DB2
    
    style CDN fill:#90ee90
    style Cache fill:#90ee90
```

### Availability Calculation
```python
# Component Availability
Edge: 0.9999 × 0.9999 = 99.98%
LB Layer: 1 - (0.0001)² = 99.9999%
App Layer: 1 - (0.001)³ = 99.9999%
Cache: 99.99%
DB Layer: 1 - (0.001)² = 99.9999%

# End-to-end (Series)
Total = 0.9998 × 0.999999 × 0.999999 × 0.9999 × 0.999999
      = 99.97% (2.6 hours downtime/year)
```

## MTBF/MTTR Visualization

```mermaid
graph LR
    subgraph "Current State"
        A[MTBF: 30 days<br/>MTTR: 30 min<br/>Avail: 99.93%]
    end
    
    subgraph "Improve MTTR"
        B[MTBF: 30 days<br/>MTTR: 5 min<br/>Avail: 99.99%]
    end
    
    subgraph "Improve MTBF"
        C[MTBF: 90 days<br/>MTTR: 30 min<br/>Avail: 99.98%]
    end
    
    A -->|Faster Recovery| B
    A -->|Better Testing| C
    
    style B fill:#90ee90
    style C fill:#ffd700
```

### Error Budget Dashboard

```dockerfile
Monthly Error Budget: 43.8 minutes (99.9% SLO)

Week 1: ████████░░░░░░░░░░░░ 8.5 min used
Week 2: ████████████░░░░░░░░ 12.3 min used  
Week 3: ██████████████████░░ 18.2 min used
Week 4: ████████████████████ 20.0 min used

Remaining: 4.8 minutes ⚠️
Status: CAUTION - Reduce deployment risk
```

## Advanced Pattern: Cell-Based Architecture

```mermaid
graph TB
    subgraph "Cell Architecture"
        subgraph "Cell 1"
            C1A[App]
            C1D[(Data)]
            C1C[Cache]
        end
        
        subgraph "Cell 2"
            C2A[App]
            C2D[(Data)]
            C2C[Cache]
        end
        
        subgraph "Cell 3"
            C3A[App]
            C3D[(Data)]
            C3C[Cache]
        end
    end
    
    R[Router] --> C1A
    R --> C2A
    R --> C3A
    
    style C1A fill:#90ee90
    style C2A fill:#90ee90
    style C3A fill:#90ee90
```

**Availability Impact**:
- Cell failure affects only 1/N of users
- No cascading failures between cells
- Simplified recovery procedures

This architecture pattern is related to [Bulkhead](/patterns/bulkhead) and Cell-Based Architecture (Coming Soon) for isolation.

## Key Takeaways

1. **Series multiplies, parallel adds nines**
2. **Five 9s = extremely expensive** (most don't need it)
3. **MTTR > MTBF** (recovery easier than prevention)
4. **Degraded > down** (partial availability wins)
5. **Measure actual availability** (SLAs are ceilings)

Perfect availability is impossible. Design for graceful degradation.

## Related Concepts

- **Quantitative**: [Little's Law](littles-law.md) | [Queueing Theory](queueing-models.md) | [Latency Ladder](latency-ladder.md)
- **Patterns**: [Bulkhead](/patterns/bulkhead) | [Circuit Breaker](/patterns/circuit-breaker) | [Failover](/patterns/failover)
