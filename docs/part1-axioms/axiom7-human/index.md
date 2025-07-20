---
title: "Axiom 7: Human-System Interface"
description: "Think about airplane cockpits:
- 1920s: Hundreds of unlabeled switches, dials everywhere
- 1970s: Organized panels, standard layouts
- Today: Glass..."
type: axiom
difficulty: intermediate
reading_time: 55 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part I: Axioms](/part1-axioms/) → [Axiom 7](/part1-axioms/axiom7-human/) → **Axiom 7: Human-System Interface**


# Axiom 7: Human-System Interface

---

## Level 1: Intuition (Start Here) 🌱

### The Airline Cockpit Metaphor

Think about airplane cockpits:
- **1920s**: Hundreds of unlabeled switches, dials everywhere
- **1970s**: Organized panels, standard layouts
- **Today**: Glass cockpits, automation, clear alerts

**Your ops interface is a cockpit.** Bad design causes:
- Wrong button pressed → System down
- Information overload → Missed problems  
- Poor layout → Slow response
- No automation → Human exhaustion

### Real-World Analogy: Kitchen Design

```text
Bad Kitchen (Bad Ops Interface):
- Knives mixed with spoons
- Hot stove next to paper towels
- No labels on spice jars
- Fire extinguisher behind locked door
Result: Chaos, burns, mistakes

Good Kitchen (Good Ops Interface):
- Dangerous items clearly marked
- Logical groupings
- Safety equipment accessible
- Clear workflows
Result: Efficient, safe cooking
```

### Your First Human Factors Experiment

<div class="experiment-box">
<h4>🧪 The Typo Test</h4>

Try typing these commands quickly:

**Test 1: IP Addresses**
```text
ssh 10.0.1.5   (production)
ssh 10.0.1.15  (development)
```
How easy to mix up? Very!

**Test 2: Meaningful Names**
```text
ssh prod-database-primary
ssh dev-database-test
```
How easy to mix up? Much harder!

**Lesson**: Human-friendly naming prevents disasters
</div>

### The Human Limitations Chart

| Human Aspect | Limitation | System Design Implication |
|--------------|------------|---------------------------|
| **Reading Speed** | 200-300 words/min | Don't flood with text |
| **Reaction Time** | 200ms minimum | Don't require split-second decisions |
| **Short-term Memory** | 7±2 items | Group related things |
| **Attention Span** | 20 minutes focused | Automate routine tasks |
| **Error Rate** | 1% normally, 10% under stress | Add confirmations |
| **Work Hours** | 8 hours/day | Build for handoffs |

---

## Level 2: Foundation (Understand Why) 🌿

### Core Principle: Humans ARE the System

<div class="principle-box">
<h3>The Human Component Specifications</h3>

```text
Human "Hardware" Specs:
- Input: Eyes (10 Mbps), Ears (1 Mbps)
- Processing: ~50 bits/second conscious thought
- Output: Fingers (10 actions/second max)
- Uptime: 16 hours/day (needs 8 hour maintenance)
- MTBF: 4 hours (needs breaks)
- Error rate: 0.01 baseline, 0.1 under load

System Implications:
- Humans are the slowest component
- Humans are the least reliable component
- Humans are the most adaptable component
- Humans are the only component that learns
```
</div>

### The Swiss Cheese Model

<div class="swiss-cheese-diagram">
<h3>🧀 How Human Errors Become Disasters</h3>

```yaml
Defense Layer 1: UI Design
    🧀 (Hole: Similar looking buttons)
         ↓
Defense Layer 2: Confirmation
    🧀 (Hole: Muscle memory clicks "OK")
         ↓
Defense Layer 3: Permissions  
    🧀 (Hole: Over-broad access)
         ↓
Defense Layer 4: Monitoring
    🧀 (Hole: Alert fatigue)
         ↓
    💥 DISASTER

When holes align = Failure gets through
```

**Real Example**: GitLab Database Deletion (2017)
- Hole 1: Prod/staging commands identical
- Hole 2: No confirmation for `rm -rf`
- Hole 3: Admin had full access
- Hole 4: Backups were broken
- Result: 6 hours of data lost
</div>

### 🎬 Failure Vignette: Amazon S3 Outage 2017

<div class="failure-story">
<h3>When a Typo Takes Down the Internet</h3>

**Date**: February 28, 2017
**Duration**: 4 hours
**Impact**: Major websites down, $150M lost

**The Command**:
```bash
# Intended: Remove small subset of servers
$ remove-capacity -n 12

# Actual (typo): Remove massive subset
$ remove-capacity -n 12000
```

**The UI That Failed**:
```text
Enter number of servers to remove: [________]
[Execute]
```

**What Went Wrong**:
1. No bounds checking (12,000 > total capacity!)
2. No impact preview ("This will remove 60% of S3")
3. No confirmation proportional to impact
4. No "undo" capability
5. Tool allowed impossible operations

**The Fix**:
```proto
New UI:
┌─────────────────────────────────────┐
│ Remove Capacity Tool                │
│                                     │
│ Current: 20,000 servers             │
│ Remove:  [12] servers (0.06%)       │
│                                     │
│ ⚠️ WARNING: Removing >5% requires   │
│ two-person approval                 │
│                                     │
│ Impact Preview:                     │
│ - Service capacity: 99.94%          │
│ - Estimated risk: LOW               │
│                                     │
│ [Cancel] [Dry Run] [Execute]        │
└─────────────────────────────────────┘
```
</div>

### Cognitive Load Theory

<div class="cognitive-load">
<h3>🧠 Mental Capacity Budget</h3>

```yaml
Total Cognitive Capacity: 100%

During Normal Operations:
├─ Monitoring: 20%
├─ Routine tasks: 30%
├─ Communication: 20%
├─ Reserve: 30% ✓

During Incident:
├─ Understanding problem: 40%
├─ Stress: 30%
├─ Communication: 25%
├─ Decision making: 5% ⚠️ (Not enough!)

Design Implication:
Reduce cognitive load during incidents
- Pre-compute suggestions
- Hide non-essential info
- Provide clear next steps
- Automate gathering of context
```
</div>

---

## Level 3: Deep Dive (Master the Patterns) 🌳

### Information Architecture Patterns

<div class="info-architecture">
<h3>📊 Progressive Disclosure Pattern</h3>

```proto
Level 1: Status Overview (Glanceable)
┌─────────────────────────────────┐
│ System Status: ● HEALTHY        │
│ Active Alerts: 0                │
│ Request Rate: 45K/sec           │
└─────────────────────────────────┘
                ↓ Click

Level 2: Service Health (Scannable)
┌─────────────────────────────────┐
│ API Gateway:    ● (45K/s)       │
│ Auth Service:   ● (12K/s)       │
│ Database:       ● (89% CPU) ⚠️   │
│ Cache:          ● (95% hit)     │
└─────────────────────────────────┘
                ↓ Click on Database

Level 3: Detailed Metrics (Analytical)
┌─────────────────────────────────┐
│ Database Metrics:               │
│ ┌─────────────────────────┐     │
│ │ CPU: ▁▃▅▇▇▇█▇▆▅ 89%    │     │
│ │ Memory: ████████░░ 82%  │     │
│ │ Connections: 456/500    │     │
│ └─────────────────────────┘     │
│ Top Queries:                    │
│ 1. SELECT * FROM orders... 45% │
│ 2. UPDATE inventory SET... 12% │
└─────────────────────────────────┘
```
</div>

### Confirmation Patterns

<div class="confirmation-patterns">
<h3>✅ Confirmation Proportional to Impact</h3>

| Impact Level | Confirmation Required | Example |
|-------------|----------------------|---------|
| **Trivial** | None | View logs |
| **Low** | Single click | Restart development server |
| **Medium** | Click + checkbox | Restart staging server |
| **High** | Type server name | Restart production server |
| **Critical** | Two-person + wait | Delete production data |
| **Catastrophic** | Physical key turn | Shutdown entire region |

**Implementation Example**:
```yaml
┌─────────────────────────────────────────┐
│ ⚠️ DANGEROUS OPERATION                  │
│                                         │
│ You are about to DELETE:                │
│ Database: prod-users-primary            │
│ Records: 45,231,892                     │
│                                         │
│ This action is IRREVERSIBLE             │
│                                         │
│ Type the database name to confirm:      │
│ [________________________]              │
│                                         │
│ ⏱️ 30 second cooling period...          │
│                                         │
│ [Cancel]            [Delete] (disabled) │
└─────────────────────────────────────────┘
```
</div>

### Automation Decision Matrix

<div class="automation-matrix">
<h3>🤖 Human vs Machine Task Allocation</h3>

| Task Type | Frequency | Complexity | Risk | Decision | Implementation |
|-----------|-----------|------------|------|----------|----------------|
| **Scaling for load** | Daily | Low | Low | Fully automate | Auto-scaling rules |
| **Security patches** | Weekly | Medium | Medium | Automate + verify | Patch, test, human review |
| **Debug weird issue** | Rare | High | Low | Human-driven | Better tools for human |
| **Disaster recovery** | Rare | High | High | Human decides, machine executes | Automated playbooks |
| **Data deletion** | Rare | Low | Critical | Human only | Multiple confirmations |
| **Cert renewal** | Monthly | Low | High | Automate + alert | Auto-renew, human backup |
</div>

### The Perfect Runbook Template

<div class="runbook-template">
<h3>📋 Runbook That Actually Gets Used</h3>

```markdown
# SERVICE: Payment API - ALERT: High Latency

## 🚨 QUICK ACTIONS (If paged at 3 AM)
1. Dashboard: https://dash.internal/payments
2. If latency >1s: Run `scale-payment-api +3`
3. Still bad after 5min? Page: @senior-oncall

## 📊 WHAT THIS MEANS
- **Trigger**: p95 latency > 500ms for 5 minutes
- **Impact**: Users see "Processing..." >5 seconds
- **Revenue risk**: ~$10K/minute during business hours
- **SLO burn**: 2.3 error budget minutes/hour

## 🔍 DIAGNOSIS FLOWCHART
┌─────────────────────┐
│ Check CPU on dash   │
└──────────┬──────────┘
           │
     CPU > 80%? ────NO───→ Check DB query times
           │                      │
          YES                    >100ms?
           ↓                      ↓
    Scale horizontal         Check slow query log
           ↓                      ↓
    Wait 2 minutes          Kill long queries
           ↓                      ↓
       Better? ────NO───→ Page backend team

## 🛠️ COMMON FIXES

### Fix A: High CPU (60% of cases)
Symptoms: CPU >80%, requests queuing
```bash
# Add 3 instances
kubectl scale deployment payment-api --replicas=+3

# Verify new pods ready
kubectl get pods -l app=payment-api --watch

# Should see CPU drop within 2 minutes
```bash
### Fix B: Database locks (30% of cases)
[Full query and resolution steps...]

## 📝 FOLLOW-UP
- [ ] If manually scaled, create ticket for capacity planning
- [ ] If new failure mode, update this runbook
- [ ] Check if this should be automated
```
</div>

---

## Level 4: Expert (Production Patterns) 🌲

### Case Study: NASA Mission Control Design

<div class="case-study">
<h3>🚀 Ultimate Human-System Interface</h3>

**Challenge**: Control spacecraft with lives at stake

**Design Principles Applied**:

1. **Role-Based Stations**
```text
┌─────┬─────┬─────┬─────┐
│FLIGHT│RETRO│FIDO │EECOM│  Front Row: Critical
├─────┼─────┼─────┼─────┤
│ GNC │TELMU│CAPCOM│ FAO │  Middle: Support
├─────┼─────┼─────┼─────┤
│SURGEON│PAO│RECOVERY│   │  Back: Auxiliary
└─────┴─────┴─────┴─────┘

Each station: One responsibility
Clear sight lines to main screen
Voice loops for coordination
```

2. **Information Hierarchy**
- Main screen: Mission critical only
- Station screens: Role-specific data
- Reference books: Detailed procedures
- No information overload

3. **Communication Protocol**
```text
"Flight, RETRO"      (Address, Identify)
"Go ahead, RETRO"    (Acknowledge)
"Trajectory nominal" (Message)
"Copy, RETRO"        (Confirm)

Clear, unambiguous, recorded
```

4. **Decision Authority**
- Flight Director: Final decision
- Controllers: Domain experts
- CAPCOM: Only voice to crew
- Clear chain of command

**Applied to Modern Ops**:
- Incident Commander = Flight Director
- Service owners = Controllers
- SRE = CAPCOM to systems
- Same principles, different domain
</div>

### Advanced UI Patterns

<div class="ui-patterns">
<h3>🎨 Production-Tested Interface Patterns</h3>

**1. The Status Semaphore**
```bash
Normal Operations          During Incident
┌─────────────────┐       ┌─────────────────┐
│                 │       │    INCIDENT     │
│  ALL SYSTEMS    │       │   ⚠️ SEV-2      │
│      ✅         │       │                 │
│                 │       │ Payments Down   │
│  Status: GREEN  │       │ Duration: 5m    │
│  Alerts: 0      │       │ Loss: $2.5K     │
│                 │       │                 │
│ [View Details]  │       │ [Join War Room] │
└─────────────────┘       └─────────────────┘

Color + Symbol + Text = Redundancy
Big, obvious state changes
One-click to action
```

**2. The Danger Zone Pattern**
```proto
┌─────────────────────────────────────────┐
│ Normal Operations                       │
│ ┌─────────────┐ ┌─────────────┐        │
│ │   Scale Up  │ │  Restart     │        │
│ │   Service   │ │  Service     │        │
│ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────┤
│ ⚠️ Danger Zone (Requires Confirmation)  │
│ ┌─────────────┐ ┌─────────────┐        │
│ │  Failover   │ │ Drop Cache   │        │
│ │  Database   │ │              │        │
│ └─────────────┘ └─────────────┘        │
├─────────────────────────────────────────┤
│ 🚫 Destructive (Two-Person Auth)       │
│ ┌─────────────┐ ┌─────────────┐        │
│ │   Delete    │ │  Shutdown    │        │
│ │   Data      │ │  Region      │        │
│ └─────────────┘ └─────────────┘        │
└─────────────────────────────────────────┘

Visual hierarchy prevents accidents
```

**3. The Context Accumulator**
```yaml
As you navigate, breadcrumbs build context:

Home > Production > US-East > Payments > API Servers > Instance-42

Current Context Bubble:
┌─────────────────────────────────────┐
│ 📍 Instance-42 (payment-api)        │
│ 🌎 Region: us-east-1                │
│ 🏢 Environment: PRODUCTION          │
│ ⚡ Current load: 78%                │
│ 🕒 Uptime: 47 days                  │
└─────────────────────────────────────┘

Always visible, prevents "where am I?" confusion
```
</div>

### Toil Measurement and Elimination

<div class="toil-elimination">
<h3>📊 The Toil Elimination Pyramid</h3>

```text
         Toil Hierarchy
              △
            /   \
          /  🤖  \  ← Fully Automated
        /         \    (No human needed)
      /─────────────\
     /   📋 Runbook  \ ← Semi-Automated
    /                 \  (Human triggers)
  /─────────────────────\
 /  📝 Documentation     \ ← Documented
/                         \  (Human does all)
───────────────────────────
   🔥 Tribal Knowledge   ← Undocumented
                           (In someone's head)

Progress: Bottom to top
Measure: Time spent at each level
Goal: Move everything up
```

**Real Toil Metrics**:
```text
Team: Payment Platform SRE
Quarter: Q1 2024

Toil Breakdown:
├─ Certificate renewals: 20 hrs/month → Automated → 0 hrs
├─ Scaling for traffic: 15 hrs/month → Automated → 1 hr
├─ Debug OOM errors: 40 hrs/month → Added memory profiler → 10 hrs
├─ Incident response: 30 hrs/month → Better runbooks → 20 hrs
└─ Database vacuuming: 10 hrs/month → Still manual → 10 hrs

Total reduction: 115 hrs → 41 hrs (64% reduction)
```
</div>

---

## Level 5: Mastery (Push the Boundaries) 🌴

### The Future: Augmented Operations

<div class="future-ops">
<h3>🚀 Beyond Traditional Interfaces</h3>

**1. Predictive Interfaces**
```yaml
Traditional: Show current state
Future: Show predicted future

┌─────────────────────────────────────────┐
│ Database CPU: 72% ↗️                    │
│                                         │
│ 📈 Prediction: Will hit 90% in 23 min  │
│                                         │
│ Cause: Batch job starts at 2 PM         │
│ Recommendation: Pre-scale now           │
│                                         │
│ [Ignore] [Pre-scale] [See details]     │
└─────────────────────────────────────────┘
```

**2. AR/VR Operations Centers**
```text
Instead of 2D dashboards:
- 3D service topology
- Walk through your infrastructure
- Grab and move workloads
- See data flows as particles
- Natural gesture controls

Example: Netflix VROE (VR Ops Environment)
- Put on headset
- See global traffic as flowing lights
- Spot congestion visually
- Redirect traffic with hand gestures
```

**3. AI Pair Operator**
```dockerfile
Human: "Why is latency high?"
AI: "Database queries from the new feature.
     Query time increased 10x after deploy.
     Should I show you the slow queries?"

Human: "Yes, and recommend fixes"
AI: "Top query: SELECT * without index.
     Adding index would reduce time 100x.
     Want me to generate the migration?"

Natural collaboration, not replacement
```
</div>

### The Human-Centric Design Principles

<div class="principles-summary">
<h3>🎯 10 Commandments of Human-System Design</h3>

1. **Make the right thing easy, wrong thing hard**
2. **Show state clearly, changes obviously**
3. **Confirm destructive actions proportionally**
4. **Design for tired humans at 3 AM**
5. **Automate toil, augment decisions**
6. **Group related, separate dangerous**
7. **Progressive disclosure, not information dump**
8. **Context always visible**
9. **Errors should be recoverable**
10. **Learn from every incident**
</div>

## Summary: Key Insights by Level

### 🌱 Beginner
1. **Humans have limits - design for them**
2. **Bad UI causes disasters**
3. **Meaningful names prevent errors**

### 🌿 Intermediate
1. **Humans ARE part of the system**
2. **Swiss cheese model - layer defenses**
3. **Cognitive load management critical**

### 🌳 Advanced
1. **Progressive disclosure manages complexity**
2. **Confirmation proportional to impact**
3. **Runbooks that actually work**

### 🌲 Expert
1. **NASA principles apply to ops**
2. **Toil measurement drives automation**
3. **Context prevents confusion**

### 🌴 Master
1. **Future is augmented, not replaced**
2. **AI as partner, not overlord**
3. **Design for human+machine symbiosis**

## Quick Reference Card

<div class="reference-card">
<h3>📋 Human Factors Checklist</h3>

**For Every Interface**:
```text
☐ Can tired person use safely?
☐ Destructive actions protected?
☐ State clearly visible?
☐ Context always shown?
☐ Errors recoverable?
```

**For Every Procedure**:
```dockerfile
☐ Documented in runbook?
☐ Automated if possible?
☐ Tested regularly?
☐ Updated from incidents?
☐ Metrics on toil time?
```

**For Every Incident**:
```text
☐ Human factors analyzed?
☐ UI improvements identified?
☐ Automation opportunities?
☐ Training needs?
☐ Process updates?
```
</div>

---

**Next**: [Axiom 8: Economics →](../axiom8-economics/index.md)

*"The best interface is no interface. The best process is no process. But until then, design for humans."*

---

**Next**: [Examples](examples.md)
