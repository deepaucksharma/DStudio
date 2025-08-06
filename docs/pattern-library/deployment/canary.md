---
title: Canary Deployment
description: Gradual rollout with early failure detection
---

# Canary Deployment

## Overview

Canary deployment is a pattern for rolling out releases to a subset of users or servers, allowing you to test in production with reduced risk.

## How It Works

1. **Deploy to Small Subset**: Release new version to 1-5% of infrastructure
2. **Monitor Metrics**: Watch error rates, latency, and business metrics
3. **Gradual Rollout**: If healthy, progressively increase traffic
4. **Quick Rollback**: If issues detected, instantly revert

## Implementation

### Traffic Routing
```yaml
# Example: Kubernetes canary with Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
spec:
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: service
        subset: v2
      weight: 10  # 10% to canary
    - destination:
        host: service
        subset: v1
      weight: 90  # 90% to stable
```

## Success Metrics

- Error rate remains below threshold
- P99 latency within bounds
- Business metrics stable or improving
- No increase in support tickets

## When to Use

- **High-risk changes**: Database migrations, algorithm changes
- **Performance-sensitive**: When latency matters
- **Large user base**: Minimize blast radius
- **Continuous deployment**: Part of CD pipeline

## Related Patterns

- [Blue-Green Deployment](blue-green.md)
- [Circuit Breaker](../resilience/circuit-breaker.md)
- [Feature Flags](feature-flags.md)

