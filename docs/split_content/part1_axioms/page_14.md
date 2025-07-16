Page 14: Runbook Skeleton & Toil Index
The Anatomy of a Perfect Runbook:
markdown# RUNBOOK: Service Name - Alert Name

## Quick Actions (If you're paged at 3 AM)
1. Check dashboard: http://dashboard.internal/service
2. If CPU > 90%: Run `kubectl scale deployment api --replicas=+2`
3. If still bad: Page secondary on-call

## Alert Meaning
- **What**: [Specific condition that triggered]
- **Why it matters**: [Business impact if ignored]
- **SLO impact**: [How many error budget minutes this burns]

## Diagnostic Steps
1. [ ] Check golden signals dashboard
2. [ ] Look for correlated alerts
3. [ ] Check recent deployments
4. [ ] Review dependency health

## Resolution Paths

### Path A: High CPU (70% of cases)
Symptoms: CPU > 85%, latency increasing
Actions:
1. Scale horizontally: `kubectl scale ...`
2. Check for runaway queries: `SELECT * FROM pg_stat_activity WHERE state = 'active' AND query_time > '1 minute'`
3. If queries found, kill them: `SELECT pg_terminate_backend(pid) FROM ...`

### Path B: Memory Leak (20% of cases)
Symptoms: Memory growing, GC time increasing
Actions:
1. Capture heap dump: `kubectl exec $POD -- jmap -dump:live,format=b,file=/tmp/heap.bin 1`
2. Rolling restart: `kubectl rollout restart deployment api`
3. Page development team for fix

### Path C: Dependency failure (10% of cases)
[Details...]

## Post-Incident
- [ ] Update metrics if this was a new failure mode
- [ ] File ticket for automation if resolved manually
- [ ] Update this runbook with learnings
The Toil Index Calculator:
Toil Score = Frequency × Duration × Interruptiveness × Automatable

Where:
- Frequency: How often per month (0-100)
- Duration: Minutes per incident (0-100)  
- Interruptiveness: Off-hours multiplier (1-3x)
- Automatable: Could a script do this? (0.1 if yes, 1.0 if no)

Examples:
- Certificate renewal: 1 × 30 × 1 × 0.1 = 3 (automate!)
- Debugging OOM: 5 × 120 × 2 × 1.0 = 1200 (invest in prevention)
- Scaling for traffic: 20 × 5 × 1 × 0.1 = 10 (automate!)
Toil Reduction Curve:
Engineer Time Spent
100% │ ╱
     │╱ Manual everything
 75% │────────
     │         ╲
 50% │          ╲ Runbooks
     │           ╲
 25% │            ╲───────
     │                     ╲ Automation
  0% └──────────────────────╲───────
     0%        50%         100%
           System Maturity →