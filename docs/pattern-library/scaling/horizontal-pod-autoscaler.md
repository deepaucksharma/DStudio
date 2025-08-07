---
title: Horizontal Pod Autoscaler
description: Kubernetes autoscaling
---

## The Complete Blueprint

Horizontal Pod Autoscaler (HPA) patterns automatically scale Kubernetes applications by adjusting the number of pod replicas based on observed metrics like CPU utilization, memory usage, or custom application metrics. This pattern addresses the fundamental challenge of matching compute resources to dynamic workload demands without manual intervention, ensuring applications maintain performance during traffic spikes while optimizing costs during low usage periods. The HPA controller continuously monitors metrics, makes scaling decisions based on configurable thresholds, and works with the Kubernetes scheduler to deploy or remove pod instances across the cluster infrastructure.

```mermaid
graph TB
    subgraph "Metrics Collection"
        A[Resource Metrics<br/>CPU, Memory usage]
        B[Custom Metrics<br/>Queue length, RPS]
        C[External Metrics<br/>Cloud monitoring]
        D[Metrics Server<br/>Kubernetes metrics API]
    end
    
    subgraph "HPA Controller"
        E[Metric Evaluation<br/>Target vs current]
        F[Scaling Algorithm<br/>Desired replica calculation]
        G[Scaling Policies<br/>Rate limits, cooldowns]
        H[Decision Engine<br/>Scale up/down logic]
    end
    
    subgraph "Pod Management"
        I[Deployment Controller<br/>Replica management]
        J[Pod Scheduler<br/>Node placement]
        K[Resource Allocation<br/>CPU/Memory limits]
        L[Load Balancer<br/>Traffic distribution]
    end
    
    subgraph "Infrastructure"
        M[Kubernetes Nodes<br/>Worker capacity]
        N[Service Discovery<br/>Pod endpoints]
        O[Health Checks<br/>Pod readiness]
        P[Monitoring<br/>Observability]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    
    E --> F
    F --> G
    G --> H
    
    H --> I
    I --> J
    J --> K
    K --> L
    
    L --> M
    M --> N
    N --> O
    O --> P
    
    style E fill:#4CAF50,color:#fff
    style H fill:#2196F3,color:#fff
    style I fill:#FF9800,color:#fff
    style M fill:#9C27B0,color:#fff
```

### What You'll Master

- **Kubernetes autoscaling mechanics** with HPA controllers, metrics APIs, and scaling algorithms for automatic pod replica management
- **Metrics-based scaling strategies** using CPU, memory, custom application metrics, and external monitoring data for scaling decisions
- **Scaling policies and configuration** including target thresholds, rate limits, cooldown periods, and scaling behavior tuning
- **Resource management integration** working with node autoscaling, resource quotas, and cluster capacity planning
- **Performance optimization** preventing scaling thrashing, handling metric lag, and optimizing for cost and performance trade-offs
- **Production deployment patterns** monitoring autoscaling behavior, troubleshooting scaling issues, and operational best practices

# Horizontal Pod Autoscaler

Kubernetes autoscaling

## See Also

- [Eventual Consistency](/pattern-library/data-management/eventual-consistency)
- [Event Streaming](/pattern-library/architecture/event-streaming)
- [Rate Limiting Pattern](/pattern-library/scaling/rate-limiting)
