# Axiom 7: Human-System Interface

<div class="axiom-header">
  <div class="learning-objective">
    <strong>Learning Objective</strong>: Humans are part of the distributed system, not observers of it.
  </div>
</div>

## Core Principle

```
Human Characteristics:
- Bandwidth: ~50 bits/second reading
- Latency: ~200ms reaction time
- Memory: 7±2 items short-term
- Availability: 8 hours/day, 5 days/week
- Error rate: 1 in 100 actions under stress
- MTTR: 8 hours (sleep required)
```

## 🎬 Failure Vignette: The Wrong Server Reboot

```
Company: E-commerce platform
Date: Black Friday 2020, 2:47 PM PST
Situation: Database replica lag increasing

Operator's view:
┌────────────────────────────────────┐
│ PRODUCTION DATABASE CLUSTER        │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐│
│ │ PRIMARY │ │REPLICA-1│ │REPLICA-2││
│ │10.0.1.5 │ │10.0.2.5 │ │10.0.3.5 ││
│ │  Lag: 0 │ │ Lag: 45s│ │  Lag: 2s││
│ └─────────┘ └─────────┘ └─────────┘│
└────────────────────────────────────┘

Intended action: Restart REPLICA-1 (10.0.2.5)
Actual command: ssh 10.0.1.5 'sudo reboot'  # Typo!
Result: Primary database offline
Impact: $3.2M lost revenue in 12 minutes

Root cause analysis:
1. Similar IP addresses (differ by 1 digit)
2. No confirmation for destructive actions
3. Stress (peak traffic day)
4. UI showed IPs, not meaningful names

Fixes implemented:
1. Confirmation dialog with server role
2. Color coding: Primary=RED, Replica=GREEN
3. Aliases: db-primary-1, db-replica-1
4. Two-person rule for production changes
5. Automated failover (remove human from loop)
```

## Human Factors Engineering Principles

### 1. Recognition Over Recall

```
BAD:  "Enter server IP: ___________"
GOOD: "Select server: [▼ Dropdown with names]"
```

### 2. Confirmation Proportional to Impact

```
Low impact:   Single click
Medium impact: Click + confirm button
High impact:  Type server name to confirm
Critical:     Two-person authentication
```

### 3. Progressive Disclosure

```
Normal view: Green/Red status only
Hover: Basic metrics
Click: Detailed metrics
Expert mode: Full diagnostics
```

### 4. Error Prevention > Error Handling

```
// BAD: Let user enter any command
$ run_command: ___________

// GOOD: Constrain to safe operations
$ Select operation:
  [ ] Restart replica
  [ ] Failover (requires approval)
  [X] View status (safe)
```

## 🎯 Decision Framework: Automation vs Human

```
Should a human be in the loop?

├─ Is the decision reversible?
│  └─ NO → Require human confirmation
│
├─ Can it be fully specified in code?
│  └─ NO → Human judgment needed
│
├─ Is response time critical (<1s)?
│  └─ YES → Automate, alert human
│
├─ Are consequences well understood?
│  └─ NO → Human required
│
└─ Is this a learned response?
   └─ YES → Encode in runbook → automate
```

## The Operator Experience Stack

```
Layer 4: Decision Support
  - What should I do?
  - Suggested actions
  - Impact prediction

Layer 3: Situational Awareness  
  - What's happening?
  - Correlations shown
  - Root cause hints

Layer 2: Information Design
  - What am I seeing?
  - Clear visualizations
  - Meaningful groupings

Layer 1: Data Access
  - Can I see the data?
  - Fast queries
  - Reliable access
```

## 🔧 Try This: CLI Safety Wrapper

```bash
#!/bin/bash
# safe-prod-cmd.sh - Wrapper for dangerous commands

DANGEROUS_CMDS="reboot|shutdown|rm.*-rf|drop|delete|truncate"
PROD_SERVERS="prod-|primary|master"

# Function to confirm dangerous operations
confirm_dangerous() {
    echo "⚠️  WARNING: Dangerous operation detected!"
    echo "Command: $1"
    echo "Server: $2"
    echo
    echo "Type the server name to confirm: "
    read confirmation
    if [ "$confirmation" != "$2" ]; then
        echo "❌ Confirmation failed. Aborting."
        exit 1
    fi
}

# Check if command is dangerous
if echo "$2" | grep -qE "$DANGEROUS_CMDS"; then
    if echo "$1" | grep -qE "$PROD_SERVERS"; then
        confirm_dangerous "$2" "$1"
    fi
fi

# Log all commands
echo "[$(date)] User: $(whoami) Server: $1 Cmd: $2" >> ~/.prod_commands.log

# Execute the actual command
ssh "$1" "$2"
```

## Counter-Intuitive Truth 💡

"The most reliable systems are designed to work without humans in the loop. The most resilient systems are designed to work with humans when automation fails."

## Runbook Skeleton

### The Anatomy of a Perfect Runbook

```markdown
# RUNBOOK: Service Name - Alert Name

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
```

## The Toil Index Calculator

```
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
```

### Toil Reduction Curve

```
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
```

## Cross-References

- → [Axiom 6: Observability](../axiom6-observability/index.md): What humans need to see
- → [Axiom 8: Economics](../axiom8-economics/index.md): Cost of human errors
<!-- - → [Runbook Patterns](../../patterns/runbooks): Operational excellence -->

---

**Next**: [Axiom 8: Economics →](../axiom8-economics/index.md)

*"The best system is one that requires no human intervention, but the most resilient system is one that degrades gracefully when humans must intervene."*