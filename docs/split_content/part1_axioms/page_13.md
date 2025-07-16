Page 13: AXIOM 7 – Human-System Interface
Learning Objective: Humans are part of the distributed system, not observers of it.
The Human API:
Human Characteristics:
- Bandwidth: ~50 bits/second reading
- Latency: ~200ms reaction time
- Memory: 7±2 items short-term
- Availability: 8 hours/day, 5 days/week
- Error rate: 1 in 100 actions under stress
- MTTR: 8 hours (sleep required)
🎬 Failure Vignette: The Wrong Server Reboot
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
Human Factors Engineering Principles:
1. Recognition Over Recall:
BAD:  "Enter server IP: ___________"
GOOD: "Select server: [▼ Dropdown with names]"
2. Confirmation Proportional to Impact:
Low impact:   Single click
Medium impact: Click + confirm button
High impact:  Type server name to confirm
Critical:     Two-person authentication
3. Progressive Disclosure:
Normal view: Green/Red status only
Hover: Basic metrics
Click: Detailed metrics
Expert mode: Full diagnostics
4. Error Prevention > Error Handling:
// BAD: Let user enter any command
$ run_command: ___________

// GOOD: Constrain to safe operations
$ Select operation:
  [ ] Restart replica
  [ ] Failover (requires approval)
  [X] View status (safe)
🎯 Decision Framework: Automation vs Human
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
The Operator Experience Stack:
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
🔧 Try This: CLI Safety Wrapper
bash#!/bin/bash
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
Counter-Intuitive Truth 💡:
"The most reliable systems are designed to work without humans in the loop. The most resilient systems are designed to work with humans when automation fails."