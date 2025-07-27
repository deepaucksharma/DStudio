---
title: Blue-Green Deployment
description: Zero-downtime deployment strategy using two identical environments
type: pattern
category: deployment
difficulty: intermediate
reading_time: 25 min
prerequisites: [load-balancing, deployment-basics]
when_to_use: Zero-downtime deployments, instant rollback requirements, production testing
when_not_to_use: Database schema changes, stateful applications, resource-constrained environments
status: complete
last_updated: 2025-01-27
excellence_tier: silver
pattern_status: stable
introduced: 2005-01
current_relevance: specialized
trade_offs:
  pros:
    - Zero downtime deployments
    - Instant rollback capability
    - Production testing before cutover
  cons:
    - Double infrastructure cost
    - Database migration complexity
    - Session state challenges
best_for:
  - Stateless applications
  - Critical production systems
  - Applications requiring instant rollback
  - A/B testing infrastructure
---

# Blue-Green Deployment

!!! warning "🥈 Silver Tier Pattern"
    **Zero-Downtime Deployment Strategy** • Best for critical production systems
    
    A proven deployment pattern that eliminates downtime by using two identical environments. While excellent for stateless applications, it requires double infrastructure and careful handling of database changes.

## The Pattern

Blue-Green deployment eliminates downtime and reduces risk by maintaining two identical production environments - only one serving live traffic at any time.

```mermaid
graph TB
    subgraph "Blue-Green Architecture"
        LB[Load Balancer/Router]
        
        subgraph "Blue Environment (Live)"
            B1[App Instance 1]
            B2[App Instance 2]
            B3[App Instance 3]
        end
        
        subgraph "Green Environment (Staging)"
            G1[App Instance 1]
            G2[App Instance 2]
            G3[App Instance 3]
        end
        
        DB[(Shared Database)]
        
        Users --> LB
        LB -->|100% Traffic| B1
        LB -->|100% Traffic| B2
        LB -->|100% Traffic| B3
        LB -.->|0% Traffic| G1
        LB -.->|0% Traffic| G2
        LB -.->|0% Traffic| G3
        
        B1 --> DB
        B2 --> DB
        B3 --> DB
        G1 -.-> DB
        G2 -.-> DB
        G3 -.-> DB
    end
    
    style B1 fill:#4CAF50
    style B2 fill:#4CAF50
    style B3 fill:#4CAF50
    style G1 fill:#2196F3
    style G2 fill:#2196F3
    style G3 fill:#2196F3
```

## Problem-Solution Matrix

| Problem | Blue-Green Solution |
|---------|-------------------|
| Deployment downtime | Zero-downtime switch between environments |
| Rollback complexity | Instant rollback by switching back |
| Testing in production | Full production testing before switch |
| Configuration drift | Identical environments enforced |
| Partial deployment failures | All-or-nothing deployment |

## Traffic Switching Process

```mermaid
sequenceDiagram
    participant U as Users
    participant LB as Load Balancer
    participant B as Blue (Live)
    participant G as Green (New)
    participant M as Monitoring
    
    Note over B: v1.0 serving traffic
    Note over G: Deploy v2.0
    
    G->>M: Health checks pass
    M->>LB: Update routing rules
    
    rect rgb(200, 230, 255)
        Note over LB: Switch Traffic
        LB->>LB: Update config
        U->>LB: New requests
        LB->>G: Route to Green
        Note over B: Drain connections
    end
    
    Note over G: v2.0 now live
    Note over B: v1.0 standby
    
    alt Rollback needed
        M->>LB: Issues detected
        LB->>LB: Revert config
        U->>LB: Requests
        LB->>B: Route to Blue
    end
```

## Database Migration Strategies

| Strategy | Approach | Use Case |
|----------|----------|----------|
| **Backward Compatible** | Schema changes support both versions | Most common approach |
| **Blue-Green Database** | Separate databases with sync | Complete isolation needed |
| **Expand-Contract** | Gradual schema evolution | Complex migrations |
| **Feature Flags** | Code handles both schemas | Conditional logic |

```mermaid
graph LR
    subgraph "Backward Compatible Migration"
        DB1[(Database v1)]
        DB2[(Add Column<br/>Default Value)]
        DB3[(Migrate Data)]
        DB4[(Remove Old<br/>Column)]
        
        DB1 -->|Blue Running| DB2
        DB2 -->|Deploy Green| DB3
        DB3 -->|Switch Traffic| DB4
    end
```

## Deployment Comparison

| Aspect | Blue-Green | Canary | Rolling Update |
|--------|------------|--------|----------------|
| **Rollback Speed** | Instant (< 1s) | Minutes | 10-30 minutes |
| **Resource Cost** | 2x infrastructure | 1.1-1.5x | 1x |
| **Risk Profile** | Very low | Low | Medium |
| **Testing Scope** | Full environment | Partial users | Progressive |
| **Complexity** | Low | Medium | High |
| **Database Changes** | Challenging | Easier | Easiest |

## Cloud Provider Implementation

### AWS Blue-Green

```mermaid
graph TB
    subgraph "AWS Implementation"
        R53[Route 53]
        ALB[Application Load Balancer]
        
        subgraph "Blue ASG"
            BEC2[EC2 Instances]
        end
        
        subgraph "Green ASG"
            GEC2[EC2 Instances]
        end
        
        R53 --> ALB
        ALB --> BEC2
        ALB -.-> GEC2
        
        CW[CloudWatch] --> ALB
        CW --> BEC2
        CW --> GEC2
    end
```

| AWS Service | Blue-Green Feature | Configuration |
|-------------|-------------------|---------------|
| **Route 53** | Weighted routing | 100-0 or 0-100 split |
| **ALB** | Target group switching | Instant switch |
| **CodeDeploy** | Native blue-green | Automated process |
| **ECS** | Service update | Task definition swap |

### GCP Blue-Green

```mermaid
graph TB
    subgraph "GCP Implementation"
        GLB[Global Load Balancer]
        
        subgraph "Blue MIG"
            BMIG[Instance Group]
        end
        
        subgraph "Green MIG"
            GMIG[Instance Group]
        end
        
        NEG1[Network Endpoint Group]
        NEG2[Network Endpoint Group]
        
        GLB --> NEG1 --> BMIG
        GLB -.-> NEG2 -.-> GMIG
    end
```

### Azure Blue-Green

```mermaid
graph TB
    subgraph "Azure Implementation"
        TM[Traffic Manager]
        
        subgraph "Blue Slot"
            BAS[App Service]
        end
        
        subgraph "Green Slot"
            GAS[Staging Slot]
        end
        
        TM --> BAS
        TM -.-> GAS
        
        AI[App Insights] --> BAS
        AI --> GAS
    end
```

## Health Check Configuration

```mermaid
graph LR
    subgraph "Health Check Layers"
        L1[L4: TCP Port Check]
        L2[L7: HTTP Endpoint]
        L3[App: Business Logic]
        L4[Dep: Dependencies]
        
        L1 --> L2 --> L3 --> L4
    end
```

| Check Type | Endpoint | Frequency | Timeout | Threshold |
|------------|----------|-----------|---------|-----------|
| **Liveness** | `/health` | 5s | 3s | 3 failures |
| **Readiness** | `/ready` | 10s | 5s | 2 failures |
| **Deep** | `/health/full` | 30s | 10s | 1 failure |

## Rollback Procedures

```mermaid
stateDiagram-v2
    [*] --> GreenDeployed: Deploy to Green
    GreenDeployed --> HealthChecks: Run checks
    HealthChecks --> SmokeTests: Passed
    HealthChecks --> [*]: Failed
    
    SmokeTests --> TrafficSwitch: Passed
    SmokeTests --> [*]: Failed
    
    TrafficSwitch --> Monitoring: Switch complete
    Monitoring --> Stable: Metrics good
    Monitoring --> Rollback: Issues detected
    
    Rollback --> BlueActive: Switch back
    BlueActive --> Investigation: Analyze failure
    
    Stable --> BlueDecommission: After bake time
    BlueDecommission --> [*]
```

## Real-World Metrics

| Metric | Traditional | Blue-Green | Improvement |
|--------|-------------|------------|-------------|
| **Deployment Time** | 20-30 min | 2-5 min | 85% faster |
| **Rollback Time** | 20-30 min | < 30 sec | 98% faster |
| **Downtime** | 5-10 min | 0 min | 100% eliminated |
| **Failed Deployments** | 5-10% | < 1% | 90% reduction |
| **MTTR** | 45 min | 2 min | 95% reduction |

### Netflix Case Study

```mermaid
graph TB
    subgraph "Netflix Blue-Green Pipeline"
        Build[Build & Test]
        Bake[Bake AMI]
        
        subgraph "Regional Deployment"
            R1[us-east-1]
            R2[us-west-2]
            R3[eu-west-1]
        end
        
        Build --> Bake
        Bake --> R1
        R1 -->|Success| R2
        R2 -->|Success| R3
        
        R1 -.->|Failure| Rollback1[Instant Rollback]
    end
```

**Netflix Results:**
- 4,000+ deployments/day
- < 0.001% failure rate
- Average rollback: 15 seconds
- Zero customer-facing downtime

### Etsy Case Study

| Phase | Duration | Actions |
|-------|----------|---------|
| **Build** | 5 min | CI/CD pipeline |
| **Deploy Green** | 2 min | Provision new environment |
| **Smoke Test** | 3 min | Automated test suite |
| **Switch** | 30 sec | DNS/LB update |
| **Monitor** | 15 min | Error rate, latency |
| **Decommission** | 1 min | Remove blue |

## Implementation Checklist

- [ ] **Infrastructure as Code**: Terraform/CloudFormation templates
- [ ] **Environment Parity**: Identical blue/green configurations
- [ ] **Database Strategy**: Backward compatible migrations
- [ ] **Load Balancer**: Instant switching capability
- [ ] **Health Checks**: Multi-layer validation
- [ ] **Monitoring**: Real-time metrics comparison
- [ ] **Rollback Plan**: Automated switch-back procedure
- [ ] **Testing Suite**: Smoke tests for green environment
- [ ] **Documentation**: Runbooks for operations team

## When to Use Blue-Green

### Ideal For
- **Critical Systems**: Zero downtime requirements
- **Predictable Load**: Known traffic patterns
- **Stateless Apps**: Easy to replicate
- **Quick Rollback**: Instant recovery needed
- **Full Testing**: Production-like validation

### Not Suitable For
- **Stateful Systems**: Complex session management
- **Database Heavy**: Frequent schema changes
- **Resource Constrained**: Can't afford 2x infrastructure
- **Long Transactions**: Can't drain connections quickly
- **Continuous Deployment**: Many daily deployments

## Pattern Relationships

```mermaid
graph TB
    BG[Blue-Green Deployment]
    
    CB[Circuit Breaker]
    HC[Health Check]
    CD[Canary Deployment]
    FF[Feature Flags]
    
    BG -->|Monitors with| HC
    BG -->|Protects with| CB
    BG -->|Alternative to| CD
    BG -->|Combines with| FF
    
    HC -->|Triggers| CB
    CD -->|Gradual vs Instant| BG
    FF -->|Dark launches| BG
```

## Key Decisions

1. **Switch Mechanism**: DNS vs Load Balancer vs Service Mesh
2. **Database Handling**: Shared vs Separate vs Replicated
3. **State Management**: Stateless vs Session draining vs Replication
4. **Validation Depth**: Basic health vs Full integration tests
5. **Bake Time**: How long before decommissioning old environment

## References

- [Circuit Breaker Pattern](circuit-breaker.md) - Protecting during switches
- [Health Check Pattern](health-check.md) - Validating green environment
- [Distributed Tracing](distributed-tracing.md) - Monitoring both environments
- [Work Distribution Pillar](../part2-pillars/work-distribution/index.md) - Load balancing strategies