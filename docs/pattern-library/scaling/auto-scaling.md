---
title: Auto-scaling Pattern
category: scaling
excellence_tier: silver
pattern_status: recommended
description: Dynamic resource management pattern that adjusts capacity based on demand metrics
introduced: 2024-01
current_relevance: mainstream
trade_offs:
  pros:
    - Cost optimization through right-sizing
    - Handles traffic spikes automatically
    - Reduces operational overhead
  cons:
    - Configuration complexity
    - Cold start latency
    - Potential for oscillation
best_for:
  - Variable workloads (10x+ daily variation)
  - Cloud-native applications
  - Cost-sensitive environments
---

# Auto-scaling Pattern

!!! warning "🥈 Silver Tier Pattern"
    **Powerful but requires careful tuning** • Use when you have variable workloads
    
    Auto-scaling can save costs and handle spikes, but misconfiguration leads to thrashing, cold starts, and instability. Requires continuous monitoring and adjustment of scaling policies, thresholds, and cooldown periods to work effectively.

## Essential Questions

!!! question "Before Implementing Auto-scaling"
    1. **What's your traffic pattern?** Daily peaks? Seasonal? Unpredictable spikes?
    2. **What's your cold start time?** Can users tolerate 30s-5min delays?
    3. **What metrics correlate with load?** CPU? Memory? Queue depth? Custom metrics?
    4. **What's your cost tolerance?** Over-provision for safety or optimize aggressively?
    5. **Do you have stateful services?** Connection draining? Session affinity?

## When to Use / When NOT to Use

### Use Auto-scaling When:
- ✅ **Variable Load**: Traffic varies >3x daily or weekly
- ✅ **Cloud Environment**: Running on AWS/GCP/Azure with auto-scaling support
- ✅ **Stateless Services**: Applications can scale horizontally
- ✅ **Cost Pressure**: Need to optimize infrastructure spend
- ✅ **Predictable Patterns**: Load follows time-based or metric-based patterns

### DON'T Use Auto-scaling When:
- ❌ **Constant Load**: Traffic varies <20% throughout the day
- ❌ **Stateful Services**: Databases, caches, or connection-heavy services
- ❌ **Fast Response Required**: Can't tolerate 1-5 minute scale-up delays
- ❌ **Complex Dependencies**: Scaling requires coordinated changes
- ❌ **Regulatory Constraints**: Minimum capacity requirements

## Architecture Overview

```mermaid
graph TB
    subgraph "Auto-scaling Components"
        M[Metrics<br/>Collection] --> D[Decision<br/>Engine]
        D --> A[Scaling<br/>Actions]
        A --> I[Infrastructure]
        I --> M
        
        subgraph "Scaling Strategies"
            R[Reactive<br/>Scaling]
            P[Predictive<br/>Scaling]
            S[Scheduled<br/>Scaling]
        end
        
        D --> R & P & S
    end
    
    subgraph "Metrics Sources"
        CPU[CPU Usage]
        MEM[Memory]
        NET[Network I/O]
        APP[App Metrics]
        Q[Queue Depth]
    end
    
    CPU & MEM & NET & APP & Q --> M
    
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style A fill:#bfb,stroke:#333,stroke-width:2px
```

## Decision Matrix: Choosing Scaling Strategy

| Strategy | Response Time | Accuracy | Complexity | Best For |
|----------|--------------|----------|------------|-----------|
| **Reactive** | 2-5 min | Medium | Low | Unpredictable spikes |
| **Predictive** | Proactive | High | High | Regular patterns |
| **Scheduled** | Exact | Perfect | Low | Known schedules |
| **Hybrid** | Fast | High | Medium | Most production systems |

## Implementation Strategies

### 1. Reactive Scaling (Most Common)

```mermaid
stateDiagram-v2
    [*] --> Monitoring: Collect Metrics
    Monitoring --> Evaluating: Check Thresholds
    Evaluating --> Scaling: Threshold Exceeded
    Evaluating --> Monitoring: Normal Range
    Scaling --> Cooldown: Action Taken
    Cooldown --> Monitoring: Period Expired
    
    note right of Scaling
        Scale Up: CPU > 80%
        Scale Down: CPU < 30%
    end note
    
    note right of Cooldown
        Prevent oscillation
        Typical: 5 minutes
    end note
```

**Key Configuration Parameters**:

| Parameter | Typical Range | Impact |
|-----------|--------------|---------|
| Scale-up threshold | 70-80% | Lower = faster response, higher cost |
| Scale-down threshold | 20-40% | Higher = more stable, higher cost |
| Cooldown period | 300-600s | Shorter = more responsive, risk of flapping |
| Scale increment | 10-50% | Larger = faster scaling, potential waste |

### 2. Predictive Scaling (Advanced)

```mermaid
graph LR
    subgraph "ML Pipeline"
        H[Historical<br/>Data] --> F[Feature<br/>Extraction]
        F --> M[ML Model]
        M --> P[Load<br/>Prediction]
        P --> S[Scaling<br/>Decision]
    end
    
    subgraph "Features"
        T[Time of Day]
        D[Day of Week]
        E[Events/Holidays]
        W[Weather]
    end
    
    T & D & E & W --> F
    
    S --> PRE[Pre-scale<br/>Resources]
    
    style M fill:#f9f,stroke:#333,stroke-width:2px
    style S fill:#bfb,stroke:#333,stroke-width:2px
```

### 3. Multi-Metric Scaling

```mermaid
graph TB
    subgraph "Metrics Aggregation"
        CPU[CPU: 75%] --> W1[Weight: 0.4]
        MEM[Memory: 60%] --> W2[Weight: 0.3]
        REQ[Requests: 85%] --> W3[Weight: 0.2]
        LAT[Latency: 70%] --> W4[Weight: 0.1]
        
        W1 & W2 & W3 & W4 --> AGG[Weighted Score: 72%]
    end
    
    AGG --> DEC{Decision}
    DEC -->|>80%| UP[Scale Up]
    DEC -->|<30%| DOWN[Scale Down]
    DEC -->|30-80%| NONE[No Action]
    
    style AGG fill:#bbf,stroke:#333,stroke-width:2px
    style DEC fill:#f9f,stroke:#333,stroke-width:2px
```

## Production Patterns

### Netflix Scryer Architecture

```mermaid
graph TB
    subgraph "Scryer Components"
        TS[Time Series<br/>Data] --> EN[Ensemble<br/>Predictors]
        EN --> FFT[FFT Analysis]
        EN --> LIN[Linear Regression]
        EN --> NN[Neural Network]
        
        FFT & LIN & NN --> AGG[Aggregator]
        AGG --> PRED[Prediction]
        PRED --> ACT[Scaling Actions]
    end
    
    subgraph "Safety Mechanisms"
        PRED --> VAL[Validation]
        VAL --> LIM[Limits Check]
        LIM --> ACT
        
        VAL -.->|Invalid| FALL[Fallback to<br/>Reactive]
    end
    
    style EN fill:#f9f,stroke:#333,stroke-width:2px
    style AGG fill:#bbf,stroke:#333,stroke-width:2px
```

### AWS Auto Scaling Groups

| Policy Type | Use Case | Example Configuration |
|-------------|----------|---------------------|
| **Target Tracking** | Maintain specific metric | CPU = 70% ± 5% |
| **Step Scaling** | Graduated response | +2 instances if CPU >80%<br/>+4 if >90% |
| **Simple Scaling** | Binary decisions | Add 50% if CPU >80% |
| **Predictive** | Forecast-based | ML-driven, 10min ahead |

## Common Pitfalls & Solutions

| Pitfall | Impact | Solution |
|---------|--------|----------|
| **Flapping** | Constant scale up/down | Increase cooldown, add hysteresis |
| **Thundering Herd** | All instances scale together | Stagger scaling, use jitter |
| **Metric Lag** | Scaling too late | Use leading indicators, reduce collection interval |
| **Cold Starts** | User impact during scale-up | Pre-warm instances, use predictive scaling |
| **Cost Overrun** | Expensive mistakes | Set max limits, implement cost alerts |

## Implementation Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Identify key scaling metrics
- [ ] Establish baseline performance
- [ ] Define min/max instance limits
- [ ] Set up metric collection (1-min intervals)
- [ ] Implement basic reactive scaling

### Phase 2: Optimization (Week 3-4)
- [ ] Analyze scaling patterns
- [ ] Tune thresholds based on data
- [ ] Add multi-metric policies
- [ ] Implement cooldown periods
- [ ] Set up alerting for scaling events

### Phase 3: Advanced (Month 2+)
- [ ] Add predictive scaling
- [ ] Implement scheduled scaling
- [ ] Optimize for cost
- [ ] Add chaos testing
- [ ] Document runbooks

## Monitoring & Observability

```mermaid
graph LR
    subgraph "Key Metrics"
        A[Scaling Events/Hour]
        B[Time to Scale]
        C[Capacity Utilization]
        D[Cost per Request]
        E[Cold Start Impact]
    end
    
    subgraph "Dashboards"
        A & B --> OPS[Operations]
        C & D --> FIN[Finance]
        E --> UX[User Experience]
    end
    
    subgraph "Alerts"
        OPS --> AL1[Flapping Detected]
        FIN --> AL2[Cost Anomaly]
        UX --> AL3[SLA Violation]
    end
```

## Cost Optimization Strategies

| Strategy | Savings | Complexity | Risk |
|----------|---------|------------|------|
| **Aggressive scale-down** | 20-30% | Low | Service degradation |
| **Spot instances** | 60-80% | Medium | Interruptions |
| **Reserved + Auto-scale** | 40-50% | Medium | Over-commitment |
| **Predictive pre-scaling** | 10-20% | High | Prediction errors |
| **Cross-region scaling** | 30-40% | High | Latency variance |

## Real-World Examples

### Uber: Demand-Based Scaling
- **Challenge**: 50x surge during events
- **Solution**: Geospatial predictive scaling
- **Result**: 35% cost reduction, <10s response

### Spotify: Playback Service
- **Pattern**: Morning/evening peaks
- **Approach**: Time-based + reactive hybrid
- **Outcome**: 40% infrastructure savings

### Airbnb: Search Infrastructure
- **Metrics**: Query rate + result computation time
- **Strategy**: Multi-dimensional scaling
- **Impact**: 3x capacity with same budget

## Quick Decision Guide

```mermaid
graph TD
    START[Need Auto-scaling?] --> VAR{Load Variation?}
    VAR -->|<2x Daily| NO[Use Fixed Capacity]
    VAR -->|>2x Daily| STATE{Stateless?}
    
    STATE -->|No| MANUAL[Manual Scaling<br/>+ Monitoring]
    STATE -->|Yes| PRED{Predictable?}
    
    PRED -->|Yes| HYBRID[Scheduled +<br/>Reactive]
    PRED -->|No| REACT[Reactive Only]
    
    HYBRID --> IMPL[Implement<br/>Auto-scaling]
    REACT --> IMPL
    
    style NO fill:#fbb,stroke:#333,stroke-width:2px
    style IMPL fill:#bfb,stroke:#333,stroke-width:2px
```

---

*"The best infrastructure is invisible—it grows when needed, shrinks when not."*

---

**Related Patterns**: [Load Balancing](load-balancing.md) | [Circuit Breaker](../resilience/circuit-breaker.md) | [Bulkhead](../resilience/bulkhead.md)

**Next**: [Backpressure Pattern →](backpressure.md)