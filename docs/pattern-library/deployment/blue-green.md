---
title: Blue-Green Deployment
description: Zero-downtime deployment with instant rollback
---

# Blue-Green Deployment

## Overview

Blue-green deployment eliminates downtime and reduces risk by running two identical production environments called Blue and Green.

## How It Works

1. **Blue = Current Production**: Live environment serving all traffic
2. **Green = New Version**: Deploy and test new version
3. **Switch Traffic**: Route all traffic from blue to green
4. **Keep Blue as Backup**: Instant rollback if issues arise

## Implementation

### Load Balancer Switch
```nginx
## Nginx configuration
upstream backend {
    # Switch between blue and green
    server green.internal.com;  # Currently active
    # server blue.internal.com backup;
}
```

### DNS Switch
```python
## Route53 weighted routing
def switch_to_green():
    route53.change_resource_record_sets(
        ChangeBatch={
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': 'api.example.com',
                    'Type': 'A',
                    'AliasTarget': {
                        'HostedZoneId': GREEN_ZONE_ID,
                        'DNSName': GREEN_DNS
                    }
                }
            }]
        }
    )
```

## Advantages

- Zero downtime deployments
- Instant rollback capability
- Full production testing before switch
- Simple and reliable

## Disadvantages

- Requires double infrastructure
- Database migrations complex
- Long-running transactions need handling
- Session state management

## When to Use

- **Critical systems**: Where downtime is unacceptable
- **Major releases**: Significant changes needing validation
- **Quick rollback required**: Financial, healthcare systems
- **Simple architecture**: Stateless applications

## Related Patterns

- [Canary Deployment](canary.md)
- [Feature Flags](feature-flags.md)
- [Database Migration Patterns](../data-management/migration-patterns.md)

## See Also

- [Pattern Decision Matrix](/pattern-library/pattern-decision-matrix)
- [Pattern Comparison Tool](/pattern-library/pattern-comparison-tool)
- [CRDT (Conflict-free Replicated Data Types)](/pattern-library/data-management/crdt)
