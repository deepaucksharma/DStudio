---
title: Incident Response
description: "Organized approach to addressing system failures and security breaches with clear procedures for crisis management"
type: human-factors
difficulty: beginner
reading_time: 25 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](../index.md) → [Part V: Human Factors](index.md) → **Incident Response**

# Incident Response

**Coordinated action when systems fail**

> *"The best incident response is like a well-rehearsed fire drill—everyone knows their role."*

---

## What is Incident Response?

Incident response is the organized approach to addressing and managing the aftermath of a security breach or system failure. The goal is to handle the situation in a way that limits damage and reduces recovery time and costs.

## Incident Severity Levels

| Level | Definition | Response Time | Example |
|-------|------------|---------------|---------|
| **SEV-1** | Critical business impact | < 15 minutes | Complete outage, data loss |
| **SEV-2** | Major functionality impaired | < 30 minutes | Core features down |
| **SEV-3** | Minor functionality impaired | < 2 hours | Non-critical features affected |
| **SEV-4** | Minimal impact | < 24 hours | Cosmetic issues |

## Incident Response Lifecycle

```mermaid
flowchart LR
    subgraph "Incident Response Lifecycle"
        A[Detection<br/>👀] --> B[Triage<br/>🔍]
        B --> C[Response<br/>🔨]
        C --> D[Recovery<br/>✅]
        D --> E[Analysis<br/>📊]
        E --> F[Improvement<br/>📝]
        F -.-> A
    end
    
    style A fill:#ffebee
    style B fill:#fff3cd
    style C fill:#e3f2fd
    style D fill:#c8e6c9
    style E fill:#f3e5f5
    style F fill:#e0f2f1
```

## Key Roles

### 1. Incident Commander (IC)
- Overall incident coordination
- Decision making authority
- External communication
- Not necessarily technical lead

### 2. Technical Lead
- Technical investigation
- Solution implementation
- Coordinate engineering response

### 3. Communications Lead
- Status page updates
- Customer communication
- Internal updates

### 4. Scribe
- Document timeline
- Track decisions
- Record action items

## Response Procedures

### Initial Response Checklist
```mermaid
flowchart TD
    subgraph "Initial Response Flow"
        A[Incident Detected] --> B[Acknowledge<br/>< 5 min]
        B --> C[Assess Severity]
        C --> D{SEV Level?}
        
        D -->|SEV-1| E[All Hands<br/>War Room]
        D -->|SEV-2| F[Core Team<br/>Virtual Bridge]
        D -->|SEV-3/4| G[Normal Team<br/>Slack Channel]
        
        E --> H[Begin Investigation]
        F --> H
        G --> H
        
        H --> I[Status Update]
        I --> J[Implement Fix]
        J --> K[Verify Resolution]
        K --> L[Document & Schedule Postmortem]
    end
    
    style A fill:#ffcdd2
    style E fill:#ff5252
    style L fill:#c8e6c9
```

**Response Checklist by Phase:**

| Phase | Task | Target Time | Owner |
|-------|------|-------------|-------|
| **Detection** | Acknowledge alert | < 5 minutes | On-call |
| **Triage** | Assess severity | < 10 minutes | On-call |
| **Assembly** | Form response team | < 15 minutes | IC |
| **Communication** | First customer update | < 30 minutes | Comms |
| **Investigation** | Root cause analysis | Ongoing | Tech Lead |
| **Resolution** | Deploy fix | ASAP | Dev Team |
| **Verification** | Confirm fixed | +15 minutes | QA/Ops |
| **Documentation** | Timeline complete | +2 hours | Scribe |

### Communication Templates

#### Initial Customer Communication
**Communication Templates:**

```mermaid
flowchart LR
    subgraph "Communication Flow"
        A[Incident Start] --> B[Initial Notice<br/>< 30 min]
        B --> C[Regular Updates<br/>Every 30 min]
        C --> D[Resolution Notice<br/>When fixed]
        D --> E[RCA Summary<br/>< 48 hours]
        
        B -.-> F[Customers]
        C -.-> F
        D -.-> F
        
        B -.-> G[Internal Teams]
        C -.-> G
        D -.-> G
        E -.-> G
    end
    
    style A fill:#ffcdd2
    style D fill:#c8e6c9
```

| Template | When to Use | Key Elements | Tone |
|----------|-------------|--------------|------|  
| **Initial** | First 30 min | Impact, investigating, next update | Acknowledge concern |
| **Update** | Every 30-60 min | Progress, current state, ETA | Transparent |
| **Resolution** | When fixed | Duration, cause, prevention | Apologetic, forward-looking |
| **RCA** | Within 48hr | Deep dive, lessons, improvements | Technical, honest |

#### Update Communication
**Status Update Framework:**

| Status | Meaning | Customer Message | Internal Actions |
|--------|---------|-----------------|------------------|
| **Investigating** | Cause unknown | "We're investigating the issue" | All hands debugging |
| **Identified** | Cause found | "We've identified the problem" | Working on fix |
| **Monitoring** | Fix deployed | "A fix has been implemented" | Watching metrics |
| **Resolved** | Confirmed fixed | "The issue has been resolved" | Start postmortem |

#### Resolution Communication
**Resolution Communication Guide:**

```mermaid
graph TB
    subgraph "Resolution Message Components"
        A[Clear Status] --> B["✅ Incident Resolved"]
        C[Timeline] --> D["Duration: 47 minutes<br/>(14:32 - 15:19)"]
        E[Impact Summary] --> F["15,000 failed transactions<br/>Estimated revenue impact: $150k"]
        G[Root Cause] --> H["Memory leak in v2.5.0<br/>payment validation"]
        I[Actions Taken] --> J["1. Rolled back to v2.4.9<br/>2. Added monitoring<br/>3. Fixed root cause"]
        K[Next Steps] --> L["Postmortem: Tuesday 2pm<br/>Preventive measures in progress"]
    end
```

## Incident Response Automation

```mermaid
flowchart TD
    subgraph "Automated Incident Creation"
        A[Alert Triggered] --> B[Create PagerDuty Incident]
        B --> C[Calculate Severity]
        C --> D[Create Slack Channel]
        D --> E[Invite On-Call Team]
        E --> F[Post Initial Status]
        F --> G[Update Status Page]
        G --> H[Start Timer]
        
        I[Tools Integrated]
        I --> J[PagerDuty: Alerting]
        I --> K[Slack: Collaboration]
        I --> L[StatusPage: Customer Comms]
        I --> M[Jira: Tracking]
    end
    
    style A fill:#ffcdd2
    style H fill:#c8e6c9
```

**Automation Benefits:**

| Task | Manual Time | Automated Time | Time Saved |
|------|-------------|----------------|------------|
| Create incident | 5 minutes | 5 seconds | 98% |
| Assemble team | 10 minutes | 30 seconds | 95% |
| Initial comms | 15 minutes | 1 minute | 93% |
| Status page | 5 minutes | Instant | 100% |
| **Total** | **35 minutes** | **< 2 minutes** | **94%** |

## On-Call Best Practices

### 1. On-Call Rotation
```mermaid
gantt
    title On-Call Rotation Schedule
    dateFormat YYYY-MM-DD
    axisFormat %m/%d
    
    section Primary
    Alice    :done, p1, 2024-03-04, 7d
    Bob      :active, p2, 2024-03-11, 7d
    Carol    :p3, 2024-03-18, 7d
    Dave     :p4, 2024-03-25, 7d
    
    section Secondary
    Eve      :done, s1, 2024-03-04, 7d
    Frank    :active, s2, 2024-03-11, 7d
    Alice    :s3, 2024-03-18, 7d
    Bob      :s4, 2024-03-25, 7d
```

**On-Call Best Practices:**

| Practice | Rationale | Implementation |
|----------|-----------|----------------|
| **6+ person rotation** | Prevents burnout | Max 1 week/month |
| **Primary + Secondary** | Backup coverage | Escalation path |
| **Weekday handoffs** | Fresh for weekend | Monday 9am |
| **Compensation** | Respect the burden | Time off or pay |
| **Documentation** | Knowledge transfer | Handoff checklist |

### 2. On-Call Kit
- Laptop with VPN access
- Phone with PagerDuty app
- Access to all critical systems
- Runbook repository access
- Emergency contact list

### 3. Escalation Policies
```mermaid
flowchart TD
    subgraph "Escalation Flow"
        A[Alert Fires] --> B[Page Primary<br/>T+0 min]
        B --> C{Acknowledged?}
        C -->|No in 5min| D[Page Secondary<br/>+ Team Lead<br/>T+5 min]
        C -->|Yes| Z[Incident Handled]
        
        D --> E{Acknowledged?}
        E -->|No in 5min| F[Page Director<br/>+ VP Engineering<br/>T+10 min]
        E -->|Yes| Z
        
        F --> G{Acknowledged?}
        G -->|No in 5min| H[Page CTO<br/>+ CEO<br/>T+15 min]
        G -->|Yes| Z
    end
    
    style A fill:#ffcdd2
    style H fill:#d32f2f,color:#fff
    style Z fill:#c8e6c9
```

**Escalation Matrix:**

| Time | Level | Who Gets Paged | Expected Action |
|------|-------|----------------|------------------|
| 0-5 min | L1 | Primary on-call | Acknowledge & respond |
| 5-10 min | L2 | Secondary + Lead | Assist or take over |
| 10-15 min | L3 | Director + VP | Resource allocation |
| 15+ min | L4 | C-Suite | Business decisions |

## Runbook Structure

```markdown
# Service Name Runbook

## Service Overview
- Purpose: What does this service do?
- Dependencies: What does it depend on?
- Impact: What happens when it fails?

## Key Metrics
- Dashboard: [link]
- Key metrics to monitor:
  - Request rate
  - Error rate
  - Latency (p50, p95, p99)

## Common Issues

### Issue 1: High Memory Usage
**Symptoms**: Memory alerts, OOM kills
**Diagnosis**: Check memory metrics, heap dumps
**Resolution**:
1. Restart service (immediate relief)
2. Investigate memory leak
3. Scale horizontally if needed

### Issue 2: Database Connection Exhaustion
**Symptoms**: Connection timeout errors
**Diagnosis**: Check connection pool metrics
**Resolution**:
1. Kill idle connections
2. Increase connection limit
3. Investigate connection leak

## Emergency Procedures

### Rollback
```bash
# Get previous version
kubectl rollout history deployment/service-name

# Rollback to previous
kubectl rollout undo deployment/service-name

# Rollback to specific version
kubectl rollout undo deployment/service-name --to-revision=2
```bash
### Emergency Scale
```bash
# Scale up immediately
kubectl scale deployment/service-name --replicas=10

# Auto-scale based on CPU
kubectl autoscale deployment/service-name --cpu-percent=50 --min=5 --max=20
```text
```

## Axiom Impact Analysis

How incident response connects to fundamental distributed systems axioms:

| Axiom | Impact on Incident Response | Strategic Considerations |
|-------|----------------------------|-------------------------|
| **Latency** | Detection and response time critical | Minimize alert latency, optimize communication channels, pre-position resources |
| **Finite Capacity** | Incidents often triggered by capacity limits | Plan for degraded modes, have scaling runbooks ready, monitor resource usage |
| **Failure** | Core trigger for incident response | Build resilient systems, plan for failure scenarios, practice recovery |
| **Consistency** | Inconsistencies complicate debugging | Include consistency checks in runbooks, understand trade-offs during incidents |
| **Time** | Critical for correlation and timeline | Ensure clock sync, timestamp everything, account for timezone differences |
| **Ordering** | Race conditions cause complex incidents | Document expected order, have tools to trace operation flow |
| **Knowledge** | Incomplete info hampers response | Invest in observability, maintain up-to-date documentation, share knowledge |
| **Growth** | Scale triggers new incident patterns | Plan for growth-related failures, update runbooks as systems evolve |

## Incident Response Decision Tree

```mermaid
graph TD
    A[Alert Triggered] --> B{Auto-remediation Available?}
    B -->|Yes| C[Execute Auto-fix]
    B -->|No| D{Critical Service?}
    
    C --> E{Fixed?}
    E -->|Yes| F[Monitor & Document]
    E -->|No| D
    
    D -->|Yes| G[Page On-call Immediately]
    D -->|No| H{Business Hours?}
    
    G --> I[Assemble War Room]
    
    H -->|Yes| J[Notify Team]
    H -->|No| K{Can Wait?}
    
    K -->|Yes| L[Queue for Morning]
    K -->|No| G
    
    I --> M[Execute Response Plan]
    J --> M
    L --> M
```

## Incident Classification Framework

### Severity Assessment Matrix

| Criteria ↓ / Level → | SEV-1 (Critical) | SEV-2 (Major) | SEV-3 (Minor) | SEV-4 (Low) |
|---------------------|------------------|---------------|---------------|-------------|
| **Revenue Impact** | >$10k/minute | $1k-10k/minute | <$1k/minute | None |
| **User Impact** | All users affected | Many users (>10%) | Some users (<10%) | Few users |
| **Data Risk** | Data loss/corruption | Data at risk | Data delays | No risk |
| **Security** | Active breach | Vulnerability exposed | Potential issue | None |
| **Reputation** | Media attention | Social media noise | Customer complaints | Internal only |
| **Recovery Time** | >4 hours | 1-4 hours | <1 hour | <30 minutes |

### Response Requirements by Severity

```
┌─────────────────────────────────────────────────────────────────┐
│ SEV-1: All Hands On Deck                                        │
├─────────────────────────────────────────────────────────────────┤
│ • Response Time: < 5 minutes                                    │
│ • War Room: Mandatory                                           │
│ • Updates: Every 15 minutes                                     │
│ • Leadership: VP notification                                   │
│ • Customer Comms: Immediate                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ SEV-2: Rapid Response                                           │
├─────────────────────────────────────────────────────────────────┤
│ • Response Time: < 15 minutes                                   │
│ • War Room: As needed                                           │
│ • Updates: Every 30 minutes                                     │
│ • Leadership: Director notification                             │
│ • Customer Comms: Within 30 min                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Incident Metrics

### Key Performance Indicators
- **MTTA** (Mean Time To Acknowledge)
- **MTTD** (Mean Time To Detect)
- **MTTR** (Mean Time To Resolve)
- **MTTF** (Mean Time To Failure)

### Tracking and Improvement
```mermaid
flowchart LR
    subgraph "Key Incident Metrics"
        A[Incident Triggered] -->|MTTA| B[Acknowledged]
        B -->|Investigation Time| C[Root Cause Found]
        C -->|Fix Time| D[Resolution Applied]
        D -->|Verification Time| E[Incident Resolved]
        
        A -->|MTTR| E
        
        F[MTTD: Time to Detect]
        G[MTTA: Time to Acknowledge]
        H[MTTR: Time to Resolve]
        I[MTTF: Time Between Failures]
    end
    
    style A fill:#ffcdd2
    style E fill:#c8e6c9
```

**Incident Metrics Dashboard:**

| Metric | Definition | Target | Current | Trend |
|--------|------------|--------|---------|-------|
| **MTTD** | Detection time | < 5 min | 3.2 min | ↓ 15% |
| **MTTA** | Acknowledge time | < 5 min | 4.1 min | ↓ 8% |
| **MTTR** | Resolution time | < 30 min | 28 min | ↓ 22% |
| **MTTF** | Between failures | > 720 hr | 892 hr | ↑ 18% |
| **Incidents/Month** | Total count | < 10 | 7 | ↓ 30% |

## Communication Strategy Matrix

### Stakeholder Communication Plan

| Stakeholder | SEV-1 | SEV-2 | SEV-3 | SEV-4 |
|-------------|-------|-------|-------|-------|
| **Customers** | Immediate status page | 30 min status update | If asked | No comms |
| **Support Team** | Immediate briefing | Alert + talking points | FYI notice | Wiki update |
| **Engineering** | All hands page | Team page | Slack notify | Ticket only |
| **Leadership** | CEO + VP alert | Director alert | Manager FYI | Weekly report |
| **Sales** | Account manager alert | If customer facing | No action | No action |

### Incident Timeline Tracking

```
┌─────────────────────────────────────────────────────────────┐
│ Incident Timeline: Payment Service Outage                   │
├─────────────┬───────────────────────────────────────────────┤
│ Time        │ Event                                         │
├─────────────┼───────────────────────────────────────────────┤
│ 14:32:15    │ 🔴 First alert: High error rate (>5%)       │
│ 14:32:45    │ 🔔 PagerDuty triggered                       │
│ 14:33:12    │ ✅ On-call acknowledged                      │
│ 14:35:00    │ 🔍 Initial investigation started             │
│ 14:38:30    │ 🎯 Root cause identified: DB connection pool │
│ 14:40:00    │ 📢 Customer communication sent               │
│ 14:42:15    │ 🔧 Mitigation applied: Increased pool size   │
│ 14:45:00    │ 📊 Error rate dropping                       │
│ 14:48:00    │ ✅ Service recovered                          │
│ 14:55:00    │ 📝 All clear, monitoring continues           │
└─────────────┴───────────────────────────────────────────────┘
```

## Role Responsibility RACI Matrix

| Activity | Incident Commander | Tech Lead | Comms Lead | Scribe | On-call |
|----------|-------------------|-----------|------------|---------|----------|
| **Declare Incident** | A | C | I | I | R |
| **Assess Severity** | A | C | I | R | C |
| **Technical Investigation** | I | A | I | R | R |
| **Customer Updates** | A | I | R | C | I |
| **Execute Fixes** | A | R | I | I | C |
| **Status Updates** | R | C | A | R | I |
| **Document Timeline** | I | C | C | A | C |
| **Call Postmortem** | A | R | I | R | C |

*R = Responsible, A = Accountable, C = Consulted, I = Informed*

## Learning and Improvement

1. **Regular Drills**: Practice incident response quarterly
2. **Runbook Reviews**: Update runbooks after each incident
3. **Tool Training**: Ensure everyone knows the tools
4. **Postmortem Culture**: Learn from every incident
5. **Metrics Review**: Monthly review of incident metrics

---

---

*"Smooth seas never made a skilled sailor—incidents make experienced engineers."*
