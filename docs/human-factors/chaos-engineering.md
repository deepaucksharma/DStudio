---
title: Chaos Engineering
description: 1. Build hypothesis around steady state
2. Vary real-world events
3. Run experiments in production
4. Automate experiments
5. Minimize blast radius
type: human-factors
difficulty: intermediate
reading_time: 30 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part V: Human Factors](/human-factors/) → **Chaos Engineering**


# Chaos Engineering

**Breaking things on purpose to build confidence**

## Chaos Engineering Principles

1. Build hypothesis around steady state
2. Vary real-world events
3. Run experiments in production
4. Automate experiments
5. Minimize blast radius

Not random destruction, but scientific discovery.

## Chaos Experiment Lifecycle

### 1. Steady State Definition

Key metrics that define "working":
- Success rate > 99.9%
- p99 latency < 100ms
- Zero data loss
- No customer complaints

Baseline measurement:
- Week of normal operation
- Capture variance
- Document assumptions

### 2. Hypothesis Formation

```text
"We believe that [SYSTEM] can tolerate [FAILURE]
 as measured by [METRICS] staying within [BOUNDS]"
```

Examples:
- "Payment service can tolerate 1 database replica failure with <10ms p99 latency increase"
- "Recommendation API can lose 50% of cache nodes with <5% error rate increase"
- "Order system can handle primary region failure with <30 second recovery time"

### 3. Experiment Design

**Scope:**
- Blast radius (% of traffic/users affected)
- Duration (how long to run)
- Severity (partial vs complete failure)
- Rollback plan (how to stop)

**Safety mechanisms:**
- Automatic abort on SLO breach
- Manual kill switch
- Gradual rollout
- Business hours only (initially)

## Chaos Experiments Catalog

### Infrastructure Chaos

**1. Instance Termination**
```python
def chaos_terminate_instance():
    # Random EC2 instance shutdown
    instances = ec2.describe_instances(
        Filters=[{'Name': 'tag:chaos', 'Values': ['enabled']}]
    )
    target = random.choice(instances)
    
    # Safety check
    if not can_terminate_safely(target):
        return
        
    # Terminate with notification
    notify_team(f"Terminating {target.id}")
    ec2.terminate_instances(InstanceIds=[target.id])
```

Tests: Auto-scaling, service discovery

**2. Network Partitions**
```bash
# Isolate availability zones
iptables -A INPUT -s 10.0.2.0/24 -j DROP
iptables -A OUTPUT -d 10.0.2.0/24 -j DROP
```

Tests: Quorum logic, split-brain handling

**3. Clock Skew**
```python
def chaos_clock_skew(skew_seconds=300):
    # Advance/delay system clocks
    subprocess.run(['date', '-s', f'+{skew_seconds} seconds'])
```

Tests: Time-dependent logic, ordering

**4. Resource Exhaustion**
```python
def chaos_fill_disk(fill_percent=90):
    available = shutil.disk_usage('/').free
    to_fill = int(available * fill_percent / 100)
    
    with open('/tmp/chaos_disk', 'wb') as f:
        f.write(b'0' * to_fill)
```

Tests: Degradation handling, alerts

### Application Chaos

**1. Latency Injection**
```python
class ChaosMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, request):
        # Inject latency randomly
        if random.random() < 0.1:  # 10% of requests
            await asyncio.sleep(1.0)  # 1 second delay
            
        return await self.app(request)
```

Tests: Timeout handling, circuit breakers

**2. Error Injection**
```python
class ChaosProxy:
    def inject_error(self, percent=5, error_code=500):
        if random.random() < percent/100:
            raise HttpError(error_code)
```

Tests: Retry logic, fallbacks

**3. Data Corruption**
```python
def chaos_corrupt_response(response):
    if random.random() < 0.01:  # 1% chance
        # Modify response data
        if isinstance(response, dict):
            response['amount'] = response.get('amount', 0) * 1.1
    return response
```

Tests: Validation, error detection

**4. Rate Limiting**
```python
class ChaosRateLimiter:
    def __init__(self, limit=10):
        self.limit = limit
        self.window = {}
        
    def check_limit(self, key):
        count = self.window.get(key, 0)
        if count >= self.limit:
            raise RateLimitExceeded()
        self.window[key] = count + 1
```

Tests: Backoff, queueing

## GameDay Planning

### Pre-GameDay Checklist

```text
□ Hypothesis documented
□ Success criteria defined
□ Monitoring dashboards ready
□ Abort procedures tested
□ Team roles assigned
□ Communication plan ready
□ Customer support warned
□ Rollback tested
□ Business stakeholders informed
□ Runbooks updated
```

### GameDay Roles

- **Game Master**: Runs the experiment
- **Observer**: Watches metrics
- **Communicator**: Updates stakeholders
- **Fixer**: Ready to intervene
- **Scribe**: Documents everything

### GameDay Timeline

```yaml
T-30min: Final checks, team assembly
T-15min: Monitoring verification
T-0: Begin experiment
T+5min: First health check
T+15min: Evaluate continue/abort
T+30min: Planned end
T+45min: Debrief starts
T+2hr: Report published
```

## Real GameDay Example

### Scenario: Payment Service Region Failure

**Hypothesis:**
"Payment service can failover to secondary region within 60 seconds with zero transaction loss"

**Experiment:**
1. Block all traffic to us-east-1
2. Monitor failover behavior
3. Verify no payments lost

**Results:**
- Failover time: 47 seconds ✓
- Transactions lost: 0 ✓
- Unexpected finding: 15% timeout errors
- Root cause: Connection pool size

**Improvements:**
- Increase connection pool warmup
- Add pre-flight checks
- Reduce health check interval

## Chaos Maturity Model

### Level 1: In Development
- Chaos in test environment only
- Manual experiments
- Known failures only
- Team-initiated

### Level 2: In Staging
- Staging environment chaos
- Some automation
- Broader failure modes
- Weekly schedule

### Level 3: In Production
- Production experiments
- Automated suite
- Business hours only
- Monthly GameDays

### Level 4: Continuous Chaos
- Always-on chaos
- Random scheduling
- Full automation
- Part of CI/CD

## Chaos Engineering Tools

### Tool Comparison

**Chaos Monkey (Netflix):**
- Scope: AWS instances
- Maturity: Very high
- Use case: Instance failures

**Gremlin:**
- Scope: Full infrastructure
- Maturity: Commercial product
- Use case: Enterprise chaos

**Litmus:**
- Scope: Kubernetes
- Maturity: CNCF project
- Use case: Container chaos

**Chaos Toolkit:**
- Scope: Extensible
- Maturity: Growing
- Use case: Custom experiments

## Measuring Chaos Success

### Metrics

1. **Experiments Run**
   - Target: 1 per service per month

2. **Issues Discovered**
   - Track: Unknown failure modes found

3. **MTTR Improvement**
   - Before/after chaos findings

4. **Confidence Score**
   - Team survey on system reliability

5. **Incident Reduction**
   - Correlation with real incidents

### ROI Calculation

```bash
Investment:
- 2 engineers × 20% time = $100k/year
- Tools and infrastructure = $20k/year

Returns:
- Prevented outages: 5 × $200k = $1M
- Reduced MTTR: 50% × $500k = $250k
- Team confidence: Priceless

ROI = 940% first year
```

## Best Practices

1. **Start Small**
   - Single service
   - Known failures
   - Test environment
   - Build confidence

2. **Automate Early**
   - Reproducible experiments
   - Consistent results
   - Reduced toil

3. **Communicate Well**
   - Clear hypotheses
   - Regular updates
   - Share learnings
   - Celebrate findings

4. **Safety First**
   - Blast radius limits
   - Abort procedures
   - Monitoring ready
   - Rollback tested

5. **Learn Always**
   - Document everything
   - Share findings
   - Update runbooks
   - Improve systems

## Common Pitfalls

1. **Too Much Too Soon**
   - Start with small experiments
   - Build confidence gradually
   - Don't break everything day 1

2. **Poor Communication**
   - Surprise chaos = angry teammates
   - Always announce experiments
   - Share results widely

3. **No Learning**
   - Running chaos without fixing findings
   - Document and prioritize fixes
   - Track improvements

4. **Production Cowboy**
   - Chaos without safety measures
   - Always have abort procedures
   - Start in lower environments

## Key Takeaways

- **Chaos finds unknown unknowns** - You don't know what you don't know
- **Production is different** - Test where it matters
- **Small experiments** - Minimize blast radius
- **Automate everything** - Manual chaos doesn't scale
- **Culture matters** - Teams must embrace failure

Remember: The goal is not to break things, but to discover weaknesses before they break in production.
