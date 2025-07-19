# Availability Math & Nines

**Building reliable systems from unreliable parts**

## The Nines

Understanding availability percentages and their real impact:

```
Availability    Downtime/Year    Downtime/Month    Downtime/Day
-----------    -------------    --------------    ------------
90% (1 nine)    36.5 days       3 days            2.4 hours
99% (2 nines)   3.65 days       7.2 hours         14.4 minutes
99.9% (3 nines) 8.76 hours      43.8 minutes      1.44 minutes
99.99% (4 nines) 52.56 minutes  4.38 minutes      8.64 seconds
99.999% (5 nines) 5.26 minutes  26.3 seconds      0.864 seconds
```

## Availability Calculations

### Series (AND) - Multiply
```
System works = A works AND B works AND C works
Availability = A × B × C

Example:
Load Balancer (99.99%) → App (99.9%) → Database (99.9%)
System = 0.9999 × 0.999 × 0.999 = 99.79%
```

### Parallel (OR) - Complement
```
System fails = A fails AND B fails
Availability = 1 - (1-A) × (1-B)

Example:
Two databases (99.9% each) in failover:
System = 1 - (0.001 × 0.001) = 99.9999%
```

### N+M Redundancy
```
Need N components, have N+M
System fails when more than M fail

For identical components with availability A:
Availability = Σ(k=0 to M) C(N+M,k) × A^(N+M-k) × (1-A)^k
```

## Complex System Modeling

### Active-Active with Load Balancer
```
     LB (99.99%)
    /           \
App1 (99.9%)  App2 (99.9%)
    \           /
     DB (99.9%)

App tier: 1 - (0.001)² = 99.9999%
Full system: 0.9999 × 0.999999 × 0.999 = 99.89%
```

### Multi-Region Architecture
```
Region 1                Region 2
LB → Apps → DB         LB → Apps → DB
(99.8%)                (99.8%)

With failover:
System = 1 - (0.002)² = 99.9996%
```

### Microservices Chain
```
A → B → C → D → E
Each 99.9%

Chain: 0.999⁵ = 99.5%

With circuit breakers and fallbacks:
Can maintain 99.9% overall
```

## Improving Availability

### Strategy Comparison
```
Approach                Cost    Improvement
--------                ----    -----------
Better hardware         $$     99% → 99.9%
Redundant hardware      $      99% → 99.99%
Multiple regions        $$    99.9% → 99.99%
Reduce dependencies     $       Big impact
Faster recovery         $       Big impact
```

### Redundancy Patterns
```
Pattern              Formula                     Example
-------              -------                     -------
Simple redundancy    1-(1-A)²                   99% → 99.99%
N+1 redundancy      Complex, see above          99.9% → 99.999%
Geographic redundancy 1-(1-A_region)²            99.9% → 99.999%
```

## Error Budgets

### Calculating Error Budget
```
SLO: 99.9% availability
Error budget: 0.1% = 43.8 minutes/month

Spending the budget:
- Deployment downtime: 10 min
- Unexpected outage: 20 min
- Remaining: 13.8 min
```

### Error Budget Policy
```python
def can_deploy():
    error_budget_remaining = calculate_remaining_budget()
    deployment_risk = estimate_deployment_risk()
    
    if error_budget_remaining > deployment_risk * 2:
        return True  # Safe to deploy
    elif error_budget_remaining > 0:
        return needs_approval()  # Risky
    else:
        return False  # Focus on reliability
```

## Real-World Availability

### Cloud Provider SLAs
```
Service              SLA      Reality      Your App Max
-------              ---      -------      ------------
AWS EC2              99.99%   99.995%      99.99%
AWS S3               99.99%   99.99%+      99.99%
AWS RDS Multi-AZ     99.95%   99.97%       99.95%
Google GCE           99.99%   99.99%       99.99%
Azure VMs            99.99%   99.98%       99.98%
```

### Building on Cloud
```
Your app on AWS:
- Your code: 99.9%
- EC2: 99.99%
- ELB: 99.99%
- RDS: 99.95%

Theoretical max: 99.83%
Reality with issues: 99.5-99.7%
```

## MTBF and MTTR

Availability through the lens of failure and recovery:

```
Availability = MTBF / (MTBF + MTTR)

Where:
MTBF = Mean Time Between Failures
MTTR = Mean Time To Recovery
```

### Examples
```
Example 1:
MTBF = 30 days
MTTR = 30 minutes
Availability = 720 hours / 720.5 hours = 99.93%

Example 2: Halving MTTR
New MTTR = 15 minutes
Availability = 720 / 720.25 = 99.97%

Faster recovery is often easier than preventing failures!
```

### Improving MTBF vs MTTR
```
Improving MTBF:
- Better testing (+10% effort → +20% MTBF)
- Code reviews (+20% effort → +30% MTBF)
- Redundancy (+50% cost → +100% MTBF)

Improving MTTR:
- Better monitoring (+10% effort → -50% MTTR)
- Automated recovery (+20% effort → -80% MTTR)
- Practice runbooks (+5% effort → -30% MTTR)
```

## Availability Patterns

### Failover Time Impact
```
Failover Time    Monthly Impact    Nines Lost
-------------    --------------    ----------
10 seconds       Negligible        None
1 minute         1-2 incidents     0.1
5 minutes        5-10 incidents    0.5
30 minutes       30-60 incidents   1.0
```

### Partial Availability
```
System with degraded modes:
- Full functionality: 99.9%
- Degraded (read-only): 99.99%
- Maintenance mode: 99.999%

User-perceived: Much better than binary up/down
```

### Cascading Failures
```
Service A (99.9%) depends on B (99.9%) and C (99.9%)

Without circuit breakers:
A = 0.999 × 0.999 × 0.999 = 99.7%

With circuit breakers and fallbacks:
A = 0.999 (degrades gracefully)
```

## Availability Economics

### Cost vs Nines
```
Nines    Relative Cost    Complexity
-----    -------------    ----------
99%      1x               Simple
99.9%    3x               Moderate
99.99%   10x              High
99.999%  100x             Extreme
```

### ROI of Availability
```
E-commerce site:
- Revenue: $10M/year
- Each 0.1% downtime = $10K lost

Investment:
- 99% → 99.9%: $200K
- Saves: $90K/year
- ROI: -55% (not worth it)

- 99.9% → 99.99%: $500K
- Saves: $9K/year
- ROI: -98% (definitely not)

But for $1B/year business: Different story!
```

## Practical Guidelines

### Design for Failure
```python
# Bad: Assume success
result = critical_service.call()
process(result)

# Good: Handle failures
try:
    result = critical_service.call()
except ServiceUnavailable:
    result = use_cache_or_default()
except Timeout:
    result = circuit_breaker.fallback()
process(result)
```

### Measure Component Availability
```python
class AvailabilityTracker:
    def track_request(self, success, component):
        self.requests[component] += 1
        if success:
            self.successes[component] += 1
    
    def get_availability(self, component):
        return self.successes[component] / self.requests[component]
    
    def alert_if_degraded(self):
        for component, target_sla in self.slas.items():
            if self.get_availability(component) < target_sla:
                alert(f"{component} below SLA: {availability}")
```

## Key Takeaways

1. **Series multiplies, parallel adds nines** - Architecture matters more than component reliability
2. **Five 9s is extremely expensive** - Most systems don't need it
3. **MTTR often easier to improve than MTBF** - Fast recovery beats perfect prevention
4. **Degraded modes improve perceived availability** - Partial > nothing
5. **Measure actual availability** - SLAs are ceilings, not floors

Remember: Perfect availability is impossible. Design for graceful degradation and fast recovery.