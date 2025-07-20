---
title: Runbooks & Playbooks
description: "Think: Runbook = Recipe, Playbook = Cooking principles"
type: human-factors
difficulty: intermediate
reading_time: 55 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part V: Human Factors](/human-factors/) → **Runbooks & Playbooks**


# Runbooks & Playbooks

**Turning chaos into checklist**

## What's the Difference?

**Runbook**: Step-by-step instructions for a specific scenario
- "If X happens, do exactly Y"
- Detailed, prescriptive
- Handles known situations

**Playbook**: Strategic guide for classes of problems
- "When facing situation like X, consider approaches Y, Z"
- Flexible, adaptive
- Handles unknown variations

Think: Runbook = Recipe, Playbook = Cooking principles

## Anatomy of a Great Runbook

### Essential Components

```markdown
# Service: Payment Gateway High Latency

## Quick Actions (First 5 minutes)
1. Check dashboard: https://dash.internal/payments
2. Verify not a monitoring false positive
3. Page secondary on-call if >1000ms p99

## Symptoms
- Alert: "payment_gateway_p99_latency > 500ms"
- User reports: "Checkout is slow"
- Metrics: Latency spike on payment-service

## Immediate Mitigation
```bash
# 1. Increase timeout temporarily
kubectl set env deployment/api-gateway PAYMENT_TIMEOUT=5000

# 2. Enable circuit breaker
curl -X POST https://admin/circuit-breaker/payment/enable

# 3. Switch to degraded mode
./scripts/enable-cached-payment-tokens.sh
```proto
## Investigation Steps
1. **Check upstream dependencies**
   ```sql
   SELECT service, avg(latency), count(*)
   FROM traces
   WHERE parent_service = 'payment-gateway'
   AND timestamp > NOW() - INTERVAL '10 minutes'
   GROUP BY service
   ORDER BY avg(latency) DESC;
   ```

2. **Examine error logs**
   ```bash
   kubectl logs -l app=payment-gateway --since=10m | grep ERROR
   ```

3. **Database connection pool**
   ```bash
   curl https://payment-gateway:9090/metrics | grep db_connections
   ```

## Resolution Paths

### Path A: Database Overload
If: Connection pool exhausted or DB CPU > 80%
Then:
1. Increase connection pool: `POOL_SIZE=100`
2. Enable read replicas: `USE_READ_REPLICA=true`
3. Kill long-running queries: `SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE query_time > interval '5 minutes'`

### Path B: Third-party API Degradation
If: External payment processor latency > 2s
Then:
1. Switch to secondary processor
2. Enable async processing mode
3. Contact vendor: support@processor.com

### Path C: Memory Pressure
If: Memory usage > 90%
Then:
1. Trigger garbage collection
2. Restart with higher heap
3. Investigate memory leak

## Rollback Procedures
Last resort if mitigation fails:
```bash
# Revert to last known good version
./deploy/rollback.sh payment-gateway

# Verification
curl https://payment-gateway/health | jq .version
```bash
## Follow-up Actions
- [ ] Create incident ticket
- [ ] Update status page
- [ ] Schedule postmortem
- [ ] Check SLO impact
```

### Key Elements Demonstrated

1. **Urgency gradient** - Quick actions first
2. **Clear symptoms** - How to recognize
3. **Copy-paste commands** - No thinking required
4. **Decision trees** - If this, then that
5. **Rollback procedures** - Escape hatch
6. **Follow-up** - Don't forget after fire is out

## Runbook Best Practices

### 1. Test Under Stress

Your brain doesn't work well at 3 AM:

```python
class RunbookValidator:
    def test_runbook(self, runbook_path):
        """
        Validate runbook is usable under stress
        """
        checks = []
        
        # All commands should be copy-pasteable
        commands = extract_code_blocks(runbook_path)
        for cmd in commands:
            if has_placeholder(cmd):
                checks.append(f"Command has placeholder: {cmd}")
        
        # All links should work
        links = extract_links(runbook_path)
        for link in links:
            if not is_reachable(link):
                checks.append(f"Dead link: {link}")
        
        # Decision points should be clear
        if_thens = extract_conditionals(runbook_path)
        for condition in if_thens:
            if not is_measurable(condition):
                checks.append(f"Vague condition: {condition}")
        
        return checks
```

### 2. Keep Updated

```yaml
# runbook-freshness.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: runbook-freshness-check
spec:
  schedule: "0 9 * * MON"  # Weekly
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: checker
            image: runbook-validator:latest
            command:
            - python
            - -c
            - |
              # Check all runbooks for staleness
              for runbook in /runbooks/*.md:
                  last_modified = get_last_modified(runbook)
                  if days_ago(last_modified) > 90:
                      alert_team(f"{runbook} not updated in 90+ days")
                  
                  # Verify all commands still valid
                  test_runbook_commands(runbook)
```

### 3. Runbook Driven Development

Write the runbook first:

```python
def implement_feature(feature_name):
    """
    TDD but for operations
    """
    # 1. Write runbook for operating feature
    runbook = write_operational_guide(feature_name)
    
    # 2. Implement monitoring/alerts from runbook
    for alert in runbook.alerts_needed:
        implement_alert(alert)
    
    # 3. Build dashboards from runbook
    for metric in runbook.key_metrics:
        add_to_dashboard(metric)
    
    # 4. Then implement feature
    implement_actual_feature(feature_name)
    
    # 5. Verify runbook works
    chaos_test_with_runbook(feature_name, runbook)
```

## Playbook Patterns

### Investigation Playbook

For when you don't know what's wrong:

```markdown
# General Investigation Playbook

## Start Wide, Narrow Down

### 1. Establish Timeline
- When did it start? Check:
  - Alert history
  - Deploy log
  - User reports
  - Metric discontinuities

### 2. What Changed?
```bash
# Recent deploys
kubectl get deployments -A -o json | \
  jq '.items[] | select(.metadata.creationTimestamp > (now - 3600))'

# Config changes
git log --since="2 hours ago" -- config/

# Infrastructure events
aws ec2 describe-instances --filters "Name=launch-time,Values=>2024-01-01"
```bash
### 3. Blast Radius
- Which services affected?
- Which regions?
- Which customers?
- Percentage impact?

### 4. Correlation Hunt
Look for patterns:
- Time correlation (every hour? daily?)
- Load correlation (traffic spikes?)
- Dependency correlation (after X, Y fails?)
- Customer correlation (specific accounts?)

## Investigation Tools

### Distributed Grep
When you need to search everywhere:
```bash
# Search all logs across all services
for service in $(kubectl get deployments -o name); do
  echo "=== $service ==="
  kubectl logs -l app=$service --since=1h | grep -i "error\|timeout\|fail"
done | tee investigation-$(date +%s).log
```bash
### Time Series Correlation
```python
# Find what else spiked when issue started
anomaly_time = "2024-03-14 15:32:00"
metrics = get_all_metrics()

for metric in metrics:
    values_before = metric.get_values(anomaly_time - 1h, anomaly_time)
    values_after = metric.get_values(anomaly_time, anomaly_time + 10m)
    
    if spike_detected(values_before, values_after):
        print(f"Correlated spike: {metric.name}")
```bash
### Hypothesis Testing
1. Form hypothesis: "DB connection exhaustion"
2. Make prediction: "Connection count = max"
3. Test: Check metric
4. If false, next hypothesis
```

### Performance Playbook

When things are slow:

```markdown
# Performance Investigation Playbook

## Measure First
Never assume - always measure:

### 1. End-to-End Timing
```bash
# Trace full request path
curl -H "X-Trace: true" https://api/endpoint | jq .trace_timeline
```proto
### 2. Component Breakdown
- Network time (DNS, TLS, transfer)
- Gateway processing
- Service processing
- Database query time
- Response serialization

### 3. Resource Saturation
Check the USE method:
- **Utilization**: How busy?
- **Saturation**: How much queuing?
- **Errors**: What's failing?

For each resource:
- CPU: %used, run queue, throttles
- Memory: %used, page faults, OOM kills  
- Disk: %busy, queue depth, errors
- Network: %bandwidth, drops, retransmits

## Common Bottlenecks

### N+1 Queries
Symptom: Linear performance degradation
```sql
-- Find repeated queries
SELECT query_template, COUNT(*), AVG(duration)
FROM query_log
WHERE timestamp > NOW() - INTERVAL '5 minutes'
GROUP BY query_template
HAVING COUNT(*) > 100
ORDER BY COUNT(*) DESC;
```bash
### Lock Contention
Symptom: Spiky latency
```sql
-- PostgreSQL lock analysis
SELECT 
    waiting.pid AS waiting_pid,
    waiting.query AS waiting_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity AS waiting
JOIN pg_stat_activity AS blocking 
    ON blocking.pid = ANY(pg_blocking_pids(waiting.pid))
WHERE waiting.wait_event_type = 'Lock';
```bash
### GC Pauses
Symptom: Periodic freezes
```bash
# Check GC logs
grep "Full GC" app.log | awk '{print $10}' | stats
```bash
```

### Incident Command Playbook

For managing major incidents:

```markdown
# Major Incident Commander Playbook

## Immediate Actions (First 5 Minutes)

1. **Assess Severity**
   - Customer impact (how many?)
   - Revenue impact ($$$/minute?)
   - Data risk (any corruption?)
   - Security risk (breach possible?)

2. **Establish Command**
   - Declare self as IC
   - Start incident channel/bridge
   - Assign roles:
     - Technical lead
     - Communications lead
     - Scribe

3. **Communicate**
   - Status page: "Investigating issues"
   - Stakeholder notification
   - Support team briefing

## Running the Incident

### Battle Rhythm
Every 15 minutes:
1. Status check from tech lead
2. Update stakeholders
3. Re-assess severity
4. Check on team health

### Decision Framework
For any proposed action:
- What's the risk?
- What's the rollback?
- How long to implement?
- How long to verify?

### Communication Templates

**Initial Report:**
"We are investigating [ISSUE] affecting [SERVICE]. 
Impact: [CUSTOMER IMPACT]. 
Started: [TIME]. 
Team is engaged. 
Updates every 15 min."

**Update:**
"[TIME] update on [ISSUE]:
Current status: [WHAT WE KNOW]
Actions taken: [WHAT WE DID]
Next steps: [WHAT'S NEXT]
ETA: [REALISTIC ESTIMATE]"

**Resolution:**
"[ISSUE] has been resolved as of [TIME].
Root cause: [BRIEF EXPLANATION]
Duration: [TOTAL TIME]
Impact: [FINAL NUMBERS]
Postmortem to follow."

## Incident Roles

### Incident Commander
- Makes decisions
- Manages priorities
- External communication
- DOES NOT debug

### Tech Lead  
- Leads investigation
- Coordinates fixers
- Reports to IC
- DOES debug

### Scribe
- Documents everything
- Maintains timeline
- Captures decisions
- Silent observer

### Communications Lead
- Updates status page
- Handles stakeholders
- Drafts messaging
- Shields tech team
```bash
## Automation Integration

### Executable Runbooks

```python
# runbook_executor.py
class RunbookExecutor:
    def __init__(self, runbook_path):
        self.runbook = parse_runbook(runbook_path)
        self.context = {}
        
    def execute(self):
        """
        Semi-automated runbook execution
        """
        for step in self.runbook.steps:
            print(f"\n[Step {step.number}] {step.description}")
            
            if step.is_automated:
                # Execute automatically
                result = self.run_command(step.command)
                self.context[step.output_var] = result
                
            elif step.is_decision:
                # Human decision required
                print(f"Check: {step.condition}")
                decision = input("Result (yes/no): ")
                if decision.lower() == 'yes':
                    self.execute_branch(step.yes_branch)
                else:
                    self.execute_branch(step.no_branch)
                    
            else:
                # Manual step
                print(f"Manual action required: {step.instruction}")
                input("Press Enter when complete...")
                
        print("\nRunbook execution complete!")
```bash
### ChatOps Integration

```yaml
# Slack command integration
commands:
  - name: /runbook
    description: Execute a runbook
    handler: |
      def handle_runbook_command(text, user):
          runbook_name = text.strip()
          
          # Validate access
          if not user_can_execute(user, runbook_name):
              return "Sorry, you don't have permission"
          
          # Start execution
          thread = execute_runbook_interactive(
              runbook_name,
              channel=user.channel,
              executor=user
          )
          
          return f"Starting runbook: {runbook_name}"
```bash
## Runbook Library Structure

### Organization

```
runbooks/
├── alerts/
│   ├── high-cpu.md
│   ├── memory-leak.md
│   └── disk-full.md
├── services/
│   ├── api-gateway/
│   ├── payment-service/
│   └── user-service/
├── incidents/
│   ├── total-outage.md
│   ├── data-corruption.md
│   └── security-breach.md
├── maintenance/
│   ├── database-upgrade.md
│   ├── certificate-renewal.md
│   └── capacity-expansion.md
└── investigation/
    ├── general-slowness.md
    ├── intermittent-errors.md
    └── customer-reports.md
```bash
### Runbook Metadata

```yaml
# Front matter for each runbook
---
title: Payment Service High Latency
severity: P2
services: [payment-service, api-gateway]
author: payment-team
last_reviewed: 2024-03-01
related_runbooks:
  - database-connection-exhaustion
  - third-party-api-timeout
metrics:
  - payment_service_p99_latency
  - payment_service_error_rate
  - database_connection_pool_size
dashboards:
  - https://grafana/d/payments
  - https://grafana/d/database
---
```bash
## Testing Runbooks

### Chaos Day Validation

```python
def chaos_test_runbook(runbook, environment='staging'):
    """
    Test runbook by causing the actual problem
    """
    # 1. Inject failure
    failure = inject_failure(runbook.failure_scenario)
    
    # 2. Wait for alert
    alert = wait_for_alert(runbook.alert_name, timeout=300)
    assert alert.fired, "Alert didn't fire!"
    
    # 3. Execute runbook
    start_time = time.now()
    result = execute_runbook(runbook, dry_run=False)
    duration = time.now() - start_time
    
    # 4. Verify resolution
    assert system_healthy(), "Runbook didn't fix issue!"
    assert duration < runbook.sla, f"Took too long: {duration}"
    
    # 5. Cleanup
    cleanup_failure(failure)
    
    return TestResult(success=True, duration=duration)
```bash
### Regular Drills

```yaml
# Schedule regular runbook drills
apiVersion: batch/v1
kind: CronJob
metadata:
  name: runbook-drill
spec:
  schedule: "0 14 * * WED"  # Weekly Wednesday 2 PM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: drill-runner
            command: ["python", "-m", "runbook_drill"]
            env:
            - name: DRILL_MODE
              value: "safe"  # Don't break prod
            - name: RUNBOOK
              value: "random"  # Pick random runbook
```bash
## Best Practices

1. **Write for Your Tired Self**
   - Assume zero context
   - Make commands copy-pasteable
   - Include verification steps

2. **Test Regularly**
   - Monthly runbook review
   - Quarterly execution drill
   - Update after every incident

3. **Version Control Everything**
   - Git for runbooks
   - Tag versions
   - Review changes

4. **Link Liberally**
   - Dashboard links
   - Related runbooks
   - Documentation

5. **Measure Effectiveness**
   - Time to resolution
   - Runbook usage rate
   - Success rate

## Metrics for Runbooks

```sql
-- Runbook effectiveness
SELECT 
    runbook_name,
    COUNT(*) as times_used,
    AVG(time_to_resolution) as avg_ttr,
    SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END) / COUNT(*) as success_rate,
    MAX(last_updated) as last_update
FROM runbook_executions
WHERE timestamp > NOW() - INTERVAL '90 days'
GROUP BY runbook_name
ORDER BY times_used DESC;
```

## Key Takeaways

- **Runbooks save lives** - And sleep, and weekends
- **Test under stress** - 3 AM you is not smart
- **Automate what you can** - But keep human judgment
- **Update constantly** - Stale runbooks are dangerous
- **Practice makes perfect** - Regular drills matter

Remember: The best runbook is the one you don't need because you automated the problem away. The second best is the one that works at 3 AM when you're half asleep.
