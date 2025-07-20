---
title: SRE Practices
description: "Site Reliability Engineering treats operations as a software problem. Core tenets:"
type: human-factors
difficulty: beginner
reading_time: 40 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part V: Human Factors](index.md) → **SRE Practices**

# SRE Practices

**Running systems reliably at scale**

## What is SRE?

Site Reliability Engineering treats operations as a software problem. Core tenets:

1. **Embrace Risk** - 100% reliability is wrong target
2. **Service Level Objectives** - Define and measure reliability
3. **Eliminate Toil** - Automate repetitive work
4. **Monitoring** - Measure everything that matters
5. **Release Engineering** - Make releases boring
6. **Simplicity** - Complexity is the enemy

!!! quote "Ben Treynor Sloss, Google VP and SRE Founder"
    "SRE is what happens when you ask a software engineer to design an operations team."

    Google's SRE insights from running billions of queries daily:
    - **50% cap on ops work** - Other 50% must be development
    - **Error budgets** - Shared between dev and SRE teams
    - **Blameless culture** - Focus on systems, not people
    - **20% project time** - Like Google's famous 20% but for reliability

## Error Budgets

### The Fundamental Equation

```redis
Error Budget = 100% - SLO

If SLO = 99.9%, Error Budget = 0.1% = 43 minutes/month
```

### Real-World Error Budget Examples

!!! example "How Companies Use Error Budgets"
    **Google Search (2020)**:
    - SLO: 99.95% availability
    - Monthly budget: 21.9 minutes downtime
    - Actual incident: 45-minute outage
    - Result: Feature freeze for 2 weeks, all hands on reliability

    **Stripe Payments (2019)**:
    - SLO: 99.99% API success rate
    - Quarterly budget: 13 minutes of errors
    - Used 8 minutes in one incident
    - Result: Delayed new API version, fixed timeout handling

    **Netflix Streaming**:
    - SLO: 99.9% stream start success
    - Innovation budget: 0.05% for experiments
    - Uses errors to test new encoding algorithms

### Using Error Budgets

```python
class ErrorBudgetManager:
    def __init__(self, slo_target):
        self.slo_target = slo_target
        self.error_budget = 1.0 - slo_target

    def can_deploy(self, current_availability, time_remaining):
        # Calculate burn rate
        budget_spent = (self.slo_target - current_availability)
        budget_remaining = self.error_budget - budget_spent

        if budget_remaining <= 0:
            return False, "Error budget exhausted"

        # Project if we'll have budget for incidents
        days_remaining = time_remaining.days
        daily_budget = budget_remaining / days_remaining

        if daily_budget < 0.001:  # Less than 1.4 min/day
            return False, "Insufficient budget for remainder"

        return True, f"{budget_remaining*100:.3f}% budget remaining"
```

**Budget Policies:**
- No feature launches when budget exhausted
- All hands on reliability when <25% remains
- Postmortem for any incident >10% of budget

## SLI/SLO/SLA Hierarchy

### Definitions

**SLI (Service Level Indicator)**: What we measure
```text
- Request latency
- Error rate
- Availability
- Durability
```

**SLO (Service Level Objective)**: Internal target
```text
- 99.9% of requests < 100ms
- 99.95% success rate
- 99.99% availability
```

**SLA (Service Level Agreement)**: External promise
```redis
- Always set looser than SLO
- SLO: 99.9% → SLA: 99.5%
- Leaves room for error
```

### Choosing Good SLIs

```python
# Bad SLI: Average latency (can hide problems)
avg_latency = sum(latencies) / len(latencies)

# Good SLI: Percentile latency
p95_latency = np.percentile(latencies, 95)
p99_latency = np.percentile(latencies, 99)

# Better SLI: User-centric metric
successful_page_loads = count(
    latency < 1000ms AND
    no_errors AND
    all_resources_loaded
)
sli = successful_page_loads / total_page_loads
```

### Setting SLOs

**Data-driven approach:**
1. Measure current performance
2. Look at historical data
3. Understand user expectations
4. Consider business requirements
5. Leave headroom for degradation

**Common SLO Targets:**
```yaml
User-facing: 99.9% (43.8 min/month)
Internal API: 99.95% (21.9 min/month)
Batch jobs: 99% (7.3 hours/month)
Data pipeline: 99.99% (4.4 min/month)
```

!!! warning "The Hidden Cost of Each Nine"
    | Availability | Downtime/Year | Downtime/Month | Typical Use Case | Annual Cost* |
    |--------------|---------------|----------------|------------------|-------------|
    | 99% | 3.65 days | 7.3 hours | Dev/Test | $10K |
    | 99.9% | 8.77 hours | 43.8 minutes | Basic web apps | $100K |
    | 99.95% | 4.38 hours | 21.9 minutes | E-commerce | $500K |
    | 99.99% | 52.6 minutes | 4.38 minutes | Financial services | $2M |
    | 99.999% | 5.26 minutes | 26.3 seconds | Healthcare/Trading | $10M+ |

    *Rough infrastructure + engineering cost for typical 1000 req/s service

## Toil Elimination

!!! info "Google's Toil Reduction Success Stories"
    **YouTube (2016)**: Reduced toil from 70% to 30% in 18 months
    - Automated database failovers (saved 10 hours/week)
    - Self-service capacity provisioning (saved 20 hours/week)
    - Automated abuse detection (saved 30 hours/week)

    **Gmail**: Eliminated 95% of manual spam config updates
    - Before: 8 SREs spending 50% time on spam rules
    - After: ML model auto-updates, 1 SRE reviews weekly
    - Saved: ~150 engineering hours/week

### What is Toil?

- **Manual** - Human has to do it
- **Repetitive** - Done over and over
- **Automatable** - Could be scripted
- **Tactical** - No enduring value
- **Scales with service** - More traffic = more toil

### Toil Budget

Goal: <50% of SRE time on toil

```python
class ToilTracker:
    def __init__(self):
        self.tasks = {}

    def log_toil(self, task_type, duration_minutes):
        self.tasks[task_type] = self.tasks.get(task_type, 0) + duration_minutes

    def analyze(self, total_work_minutes):
        toil_minutes = sum(self.tasks.values())
        toil_percentage = (toil_minutes / total_work_minutes) * 100

        # Prioritize automation
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: x[1],
            reverse=True
        )

        print(f"Toil: {toil_percentage:.1f}% of time")
        print("\nTop toil sources:")
        for task, minutes in sorted_tasks[:5]:
            hours = minutes / 60
            print(f"  {task}: {hours:.1f} hours/week")
```

### Automation Examples

**Before (Toil):**
```bash
# Manual cert renewal
1. Check cert expiry dates
2. Generate new CSR
3. Submit to CA
4. Download cert
5. Deploy to servers
6. Restart services
```

**After (Automated):**
```python
# Automated cert management
@schedule.weekly
def renew_certificates():
    for domain in get_monitored_domains():
        cert = get_certificate(domain)
        if cert.expires_in_days < 30:
            new_cert = acme_client.renew(domain)
            deploy_certificate(domain, new_cert)
            graceful_reload_services(domain)
```

## On-Call Excellence

### On-Call Principles

1. **Maximum 25% on-call** - Prevent burnout
2. **Minimum 6 people** - Sustainable rotation
3. **Equal distribution** - Fair load sharing
4. **Time-off post-incident** - Recovery time
5. **Compensated fairly** - Respect the burden

!!! example "How Top Companies Handle On-Call"
    **Netflix**: "Sleep when you're dead" → "Sleep to stay alive"
    - Moved from hero culture to sustainable on-call
    - Automatic comp time after night incidents
    - "Chaos engineering" reduces 3am pages by 90%

    **Airbnb**: Tiered on-call with clear escalation
    - L1: Product engineers (own service issues)
    - L2: SRE team (infrastructure issues)
    - L3: Staff engineers (architectural issues)
    - Result: 50% reduction in false pages

    **Cloudflare**: Follow-the-sun model
    - Singapore → London → San Francisco → Singapore
    - Nobody on-call during their night
    - 24/7 coverage with better work-life balance

### Effective Handoffs

```markdown
## On-Call Handoff Template

**Outgoing:** Alice
**Incoming:** Bob
**Period:** 2024-03-11 to 2024-03-18

### Active Issues
- [P2] Elevated memory usage on cache-3 (investigating)
- [P3] Sporadic timeout errors on payment service

### Completed Incidents
- [INC-1234] Database failover - resolved, postmortem pending
- [INC-1235] DDoS attack - mitigated with rate limiting

### Pending Changes
- Tuesday: Database migration (batch-service)
- Thursday: New region deployment (us-west-2)

### Watch Areas
- CPU on api-server-7 trending up
- Disk usage approaching 80% on log servers
- Customer complaints about slow checkout

### Learnings
- Runbook for cache eviction was outdated (fixed)
- Need better alerting for SSL cert expiry
```

### Alert Quality

**Good Alert:**
```yaml
alert: HighErrorRate
expr: |
  rate(http_requests_total{status=~"5.."}[5m])
  / rate(http_requests_total[5m]) > 0.05
for: 2m
labels:
  severity: page
  service: api
annotations:
  summary: "High 5xx error rate on {{'{{ $labels.instance }}'}}"
  impact: "Users experiencing failures"
  dashboard: "https://grafana/d/api-errors"
  runbook: "https://wiki/runbooks/high-error-rate"
```

**Bad Alert:**
```yaml
# Too noisy, no context, no action
alert: CPUHigh
expr: cpu_usage > 80
```

## Postmortem Culture

### Blameless Postmortems

Focus on systems and processes, not people.

```markdown
## Postmortem: Payment Service Outage

**Date:** 2024-03-15
**Duration:** 47 minutes
**Impact:** 15,000 failed transactions

### Timeline
- 14:32 - Deploy of v2.5.0 begins
- 14:35 - Memory usage spikes
- 14:38 - First alerts fire
- 14:45 - On-call engaged
- 14:52 - Root cause identified
- 15:02 - Rollback initiated
- 15:19 - Service recovered

### Root Cause
Memory leak in new payment validation logic.
Testing did not catch because:
1. Load tests used different data patterns
2. Staging has different memory limits
3. Canary period too short (5 min)

### Action Items
- [ ] Add memory leak detection to CI
- [ ] Align staging with prod configs
- [ ] Extend canary to 30 minutes
- [ ] Add memory-based auto-rollback

### What Went Well
- Monitoring detected issue quickly
- Rollback procedure worked perfectly
- Team communicated effectively

### Lessons Learned
- Need better production-like testing
- Canary duration matters
- Memory limits should be consistent
```

### Postmortem Metrics

Track improvement over time:
- MTTR by category
- Repeat incidents
- Action item completion rate
- Time to postmortem publication

## Change Management

### Safe Changes

```python
class ChangeRiskAssessor:
    def assess_risk(self, change):
        risk_score = 0

        # Size of change
        if change.lines_changed > 1000:
            risk_score += 3
        elif change.lines_changed > 100:
            risk_score += 1

        # Type of change
        if change.touches_database:
            risk_score += 2
        if change.modifies_api:
            risk_score += 2
        if change.updates_dependencies:
            risk_score += 3

        # Timing
        if is_peak_hours():
            risk_score += 2
        if is_friday():
            risk_score += 1

        # Mitigation
        if change.has_feature_flag:
            risk_score -= 1
        if change.has_canary_plan:
            risk_score -= 1

        return {
            'score': risk_score,
            'level': 'high' if risk_score > 5 else 'medium' if risk_score > 2 else 'low',
            'recommendation': self.get_recommendation(risk_score)
        }
```

### Progressive Rollouts

```text
1. Dev environment (immediate)
   ↓
2. Staging environment (1 hour)
   ↓
3. Canary (1% traffic, 30 min)
   ↓
4. Phase 1 (10% traffic, 2 hours)
   ↓
5. Phase 2 (50% traffic, 4 hours)
   ↓
6. Full rollout (100% traffic)
```

## Capacity Planning

### Forecasting Model

```python
def capacity_forecast(
    current_usage,
    growth_rate,
    peak_multiplier=3,
    safety_margin=1.4
):
    """
    Forecast capacity needs
    """
    forecasts = {}

    for months in [3, 6, 12]:
        # Compound growth
        projected = current_usage * ((1 + growth_rate) ** months)

        # Account for peaks
        peak_capacity = projected * peak_multiplier

        # Add safety margin
        required = peak_capacity * safety_margin

        forecasts[f"{months}_month"] = {
            'average': projected,
            'peak': peak_capacity,
            'provision': required
        }

    return forecasts

# Example
current = 1000  # requests/second
growth = 0.15   # 15% monthly

forecast = capacity_forecast(current, growth)
# 12_month: {'average': 5350, 'peak': 16050, 'provision': 22470}
```

### Leading Indicators

Monitor trends before they become problems:

```sql
-- Weekly growth rate
WITH weekly_traffic AS (
  SELECT
    DATE_TRUNC('week', timestamp) as week,
    COUNT(*) as requests
  FROM api_logs
  GROUP BY week
)
SELECT
  week,
  requests,
  (requests - LAG(requests) OVER (ORDER BY week))
    / LAG(requests) OVER (ORDER BY week) * 100 as growth_percent
FROM weekly_traffic;
```

## SRE Tools & Practices

### Chaos Engineering
See: [Chaos Engineering Guide](chaos-engineering.md)

### Observability
See: [Observability Stacks](observability-stacks.md)

### Runbooks
See: [Runbooks & Playbooks](runbooks-playbooks.md)

## Best Practices

1. **Measure Everything**
   - If it matters to users, make it an SLI
   - If it affects SLI, alert on it
   - If it causes alerts, fix it

2. **Gradual Rollouts**
   - Every change is guilty until proven innocent
   - Canary everything
   - Feature flags are your friend

3. **Practice Failures**
   - Game days monthly
   - Chaos engineering weekly
   - Disaster recovery quarterly

4. **Document Everything**
   - Runbooks for every alert
   - Postmortems for every incident
   - Architecture decisions recorded

5. **Invest in Tooling**
   - Automation reduces toil
   - Good tools prevent incidents
   - Time saved compounds

## Key Takeaways

- **Reliability is a feature** - Plan and prioritize it
- **Error budgets align incentives** - Speed vs stability balance
- **Toil is the enemy** - Automate relentlessly
- **Blameless culture** - Learn from failures
- **Measure what matters** - SLIs drive decisions

Remember: Perfect reliability is not the goal. The right amount of reliability at the right cost is the goal.
