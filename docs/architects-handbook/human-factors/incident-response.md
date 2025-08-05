---
title: Incident Response
description: Managing system failures within cognitive limits - applying Law 6 when
  stress reduces capacity by 80%
type: human-factors
difficulty: beginner
reading_time: 25 min
prerequisites:
- core-principles/laws/cognitive-load
status: complete
last_updated: 2025-07-23
---


# Incident Response

!!! abstract "Incident Response Philosophy"
    **🎯 Core Truth**: Under stress, cognitive capacity drops 80%
    **🧠 Design Principle**: Simple enough for 20% brain capacity
    **⏱️ Speed Matters**: Every minute = $1000s lost
    **🤝 Human-Centric**: Tools serve humans, not vice versa

## Incident Response at a Glance

| Phase | Time Target | Cognitive Load | Key Actions |
|-------|-------------|----------------|-------------|
| **Detect** | < 1 min | 🟥 Very High | Acknowledge alert |
| **Triage** | < 5 min | 🟥 Very High | Assess severity |
| **Respond** | < 15 min | 🟧 High | Form team, start fix |
| **Recover** | ASAP | 🟨 Medium | Deploy, verify |
| **Learn** | < 48 hr | 🟩 Low | Postmortem |

## Incident Severity Levels

### Severity Classification Decision Tree

```mermaid
flowchart TD
    A[Incident Detected] --> B{Customer Impact?}
    
    B -->|Complete Outage| C[SEV-1: Critical]
    B -->|Major Features Down| D[SEV-2: Major]
    B -->|Minor Features| E[SEV-3: Minor]
    B -->|Cosmetic/Internal| F[SEV-4: Low]
    
    C --> C1{Data Loss?}
    C1 -->|Yes| C2[🔴 SEV-1 CRITICAL<br/>• < 5 min response<br/>• Executive escalation<br/>• War room required]
    C1 -->|No| C3[🔴 SEV-1 HIGH<br/>• < 15 min response<br/>• All hands on deck<br/>• Immediate action]
    
    D --> D1{Revenue Impact?}
    D1 -->|Yes| D2[🟠 SEV-2 HIGH<br/>• < 20 min response<br/>• Team escalation<br/>• Priority fix]
    D1 -->|No| D3[🟠 SEV-2 MEDIUM<br/>• < 30 min response<br/>• Standard process<br/>• Quick resolution]
    
    E --> E1[🟡 SEV-3<br/>• < 2 hour response<br/>• Normal priority<br/>• Scheduled fix]
    
    F --> F1[🟢 SEV-4<br/>• < 24 hour response<br/>• Low priority<br/>• Next sprint]
    
    style C2 fill:#d32f2f,color:#fff
    style C3 fill:#f44336,color:#fff
    style D2 fill:#ff6f00,color:#fff
    style D3 fill:#ffa726
    style E1 fill:#fdd835
    style F1 fill:#66bb6a
```

| Level | Definition | Response Time | Example |
|-------|------------|---------------|---------|
| **SEV-1** | Critical business impact | < 15 minutes | Complete outage, data loss |
| **SEV-2** | Major functionality impaired | < 30 minutes | Core features down |
| **SEV-3** | Minor functionality impaired | < 2 hours | Non-critical features affected |
| **SEV-4** | Minimal impact | < 24 hours | Cosmetic issues |


## Incident Response Lifecycle (Cognitive Load Aware)

```mermaid
flowchart LR
    subgraph "Incident Response Lifecycle - Law 6 Optimized"
        A[Detection<br/>👀<br/>(Clear signals)] --> B[Triage<br/>🔍<br/>(Simple decision tree)]
        B --> C[Response<br/>🔨<br/>(Practiced actions)] --> D[Recovery<br/>✅<br/>(Verification steps)]
        D --> E[Analysis<br/>📊<br/>(When calm)] --> F[Improvement<br/>📝<br/>(Update runbooks)]
        F -.-> A
    end
    
    subgraph "Cognitive Load at Each Stage"
        CL1[High stress<br/>20% capacity] --> A
        CL1 --> B
        CL2[Moderate stress<br/>40% capacity] --> C
        CL2 --> D
        CL3[Low stress<br/>80% capacity] --> E
        CL3 --> F
    end
    
    style A fill:#ffebee
    style B fill:#fff3cd
    style C fill:#e3f2fd
    style D fill:#c8e6c9
    style E fill:#f3e5f5
    style F fill:#e0f2f1
```

## Incident Response Roles Matrix

| Role | Primary Focus | Cognitive Limit | Anti-Patterns |
|------|---------------|-----------------|---------------|
| **Incident Commander** | • Coordination<br/>• Decisions<br/>• External comms | Max 7±2 concerns | ❌ Don't debug<br/>❌ Don't code |
| **Technical Lead** | • Root cause<br/>• Solution<br/>• Implementation | Deep focus on 1 problem | ❌ Don't manage<br/>❌ Don't communicate |
| **Comms Lead** | • Status updates<br/>• Customer messaging<br/>• Stakeholders | 3 audiences max | ❌ Don't debug<br/>❌ Don't promise ETAs |
| **Scribe** | • Timeline<br/>• Decisions<br/>• Actions | Document everything | ❌ Don't filter<br/>❌ Don't delay |

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


### Visual Incident Flow Diagram

```mermaid
flowchart TB
    subgraph "Incident Response Flow"
        START[🚨 Alert Triggered] --> DETECT[Detection & Acknowledgment<br/>⏱️ < 5 min]
        
        DETECT --> TRIAGE[Triage & Severity<br/>🔍 Assess impact]
        
        TRIAGE --> ASSEMBLE[Assemble Team<br/>👥 Based on severity]
        
        ASSEMBLE --> PARALLEL{Parallel Actions}
        
        PARALLEL --> INVESTIGATE[Investigation<br/>🔧 Find root cause]
        PARALLEL --> COMMUNICATE[Communication<br/>📢 Update stakeholders]
        PARALLEL --> MITIGATE[Mitigation<br/>🛡️ Stop bleeding]
        
        INVESTIGATE --> FIX[Implement Fix<br/>💻 Deploy solution]
        MITIGATE --> FIX
        
        FIX --> VERIFY[Verification<br/>✅ Confirm resolution]
        
        VERIFY --> CLOSE[Close Incident<br/>📝 Document timeline]
        
        CLOSE --> POSTMORTEM[Postmortem<br/>📊 Learn & improve]
        
        COMMUNICATE -.-> STATUS[Status Updates<br/>Every 30 min]
        STATUS -.-> COMMUNICATE
    end
    
    subgraph "Time Targets"
        T1[Detection: < 5 min]
        T2[Triage: < 10 min]
        T3[Team: < 15 min]
        T4[First Update: < 30 min]
        T5[Resolution: ASAP]
    end
    
    style START fill:#ff5252,color:#fff
    style DETECT fill:#ffcdd2
    style VERIFY fill:#c8e6c9
    style POSTMORTEM fill:#e1bee7
```

## Communication Templates (Copy-Paste Ready)

### 🔴 SEV-1 Initial Message (< 5 min)
```
We are experiencing a service disruption affecting [FEATURE].
Impact: [NUMBER] users affected
Status: Investigating
Next update: In 15 minutes
```

### 🟡 Update Message (Every 30 min)
```
Update on [FEATURE] disruption:
Current status: [INVESTIGATING/IDENTIFIED/FIXING/MONITORING]
Progress: [WHAT WE'VE DONE]
Next steps: [WHAT WE'RE DOING]
ETA: [TIME or "Working to resolve ASAP"]
Next update: In 30 minutes
```

### ✅ Resolution Message
```
[FEATURE] service has been restored.
Duration: [START] - [END] ([TOTAL TIME])
Root cause: [ONE SENTENCE]
Prevention: [WHAT WE'RE DOING]
Full RCA: To follow within 48 hours
```

### Communication Decision Matrix

| Severity | Customer Comms | Internal Comms | Executive Brief |
|----------|----------------|----------------|------------------|
| **SEV-1** | Immediate | All-hands page | CEO + VP alert |
| **SEV-2** | < 30 min | Team page | Director alert |
| **SEV-3** | If asked | Slack channel | Weekly report |
| **SEV-4** | None | Ticket only | Monthly metrics |


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

**Best Practices:**
- **6+ person rotation**: Max 1 week/month
- **Primary + Secondary**: Backup coverage
- **Weekday handoffs**: Monday 9am
- **Compensation**: Time off or pay
- **Documentation**: Handoff checklist

### 2. On-Call Kit
- Laptop + VPN
- Phone + PagerDuty
- System access
- Runbooks
- Emergency contacts

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


## Runbook Template (Optimized for Stress)

### 🚨 HIGH MEMORY - QUICK FIX
```bash
# COPY THIS ENTIRE BLOCK:
kubectl rollout restart deployment/service-name && \
kubectl scale deployment/service-name --replicas=+2 && \
echo "Restarted and scaled. Check metrics in 2 min."
```

### 🚨 DATABASE CONNECTIONS FULL
```sql
-- COPY THIS ENTIRE BLOCK:
-- Kill idle connections and increase limit
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
  AND state_change < NOW() - INTERVAL '5 minutes';

ALTER SYSTEM SET max_connections = 500;
SELECT pg_reload_conf();
```

### 🚨 EMERGENCY ROLLBACK
```bash
# ONE COMMAND TO ROLLBACK:
kubectl rollout undo deployment/service-name

# CHECK STATUS:
kubectl rollout status deployment/service-name
```

## Visual Runbook Index

| Symptom | Likely Cause | Quick Fix Command | Dashboard |
|---------|--------------|-------------------|-----------||
| 🔴 **High CPU** | Infinite loop | `kubectl rollout restart` | [CPU Dashboard](#) |
| 🔴 **High Memory** | Memory leak | `kubectl scale --replicas=+2` | [Memory Dashboard](#) |
| 🔴 **Timeouts** | DB connections | See SQL above | [DB Dashboard](#) |
| 🔴 **500 Errors** | Bad deploy | `kubectl rollout undo` | [Error Dashboard](#) |
| 🟡 **Slow Response** | High load | `kubectl autoscale` | [Latency Dashboard](#) |

## Law Impact Analysis

How incident response connects to fundamental distributed systems laws:

| Law | Impact on Incident Response | Strategic Considerations |
|-----|----------------------------|-------------------------|
| **Law 2: Asynchronous Reality ⏱️** | Detection and response time critical | Minimize alert latency, optimize communication channels, pre-position resources |
| **Law 4: Trade-offs 📊** | Incidents often triggered by capacity limits | Plan for degraded modes, have scaling runbooks ready, monitor resource usage |
| **Law 1: Failure ⛓️** | Core trigger for incident response | Build resilient systems, plan for failure scenarios, practice recovery |
| **Law 4: Trade-offs 🔐** | Inconsistencies complicate debugging | Include consistency checks in runbooks, understand trade-offs during incidents |
| **Law 5: Epistemology 🧠** | Incomplete info hampers response | Invest in observability, maintain up-to-date documentation, share knowledge |
| **Law 6: Human-API 🤯** | Stress reduces capacity by 80% | Simple runbooks, clear roles, practiced procedures, cognitive offload tools |
| **Law 5: Epistemology 🤝** | Coordination failures extend incidents | Clear ownership, defined handoffs, single communication channel |
| **Law 7: Economics 💰** | Scale triggers new incident patterns | Plan for growth-related failures, update runbooks as systems evolve |


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

```text
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

## Incident Metrics That Matter

### Real-Time Performance Dashboard

```mermaid
graph LR
    subgraph "Current Month"
        DETECT[Detect<br/>3.2min<br/>🟢] --> ACK[Acknowledge<br/>4.1min<br/>🟢]
        ACK --> FIX[Resolve<br/>28min<br/>🟢]
        FIX --> VERIFY[Verify<br/>5min<br/>🟢]
    end
    
    subgraph "Targets"
        T1[< 5 min]
        T2[< 5 min]
        T3[< 30 min]
        T4[< 10 min]
    end
```

### Metrics Scorecard

| Metric | This Month | Last Month | Target | Status |
|--------|------------|------------|--------|--------|
| **Detection (MTTD)** | 3.2 min | 3.8 min | < 5 min | 🟢 -16% |
| **Response (MTTA)** | 4.1 min | 4.5 min | < 5 min | 🟢 -9% |
| **Resolution (MTTR)** | 28 min | 36 min | < 30 min | 🟢 -22% |
| **Reliability (MTTF)** | 892 hrs | 756 hrs | > 720 hrs | 🟢 +18% |
| **Volume** | 7 incidents | 10 incidents | < 10 | 🟢 -30% |

### Cost Impact Analysis

| Metric Improvement | Business Value | Annual Savings |
|--------------------|----------------|----------------|
| **MTTR -22%** | 8 min less downtime/incident | $240K |
| **MTTF +18%** | 3 fewer incidents/month | $450K |
| **MTTA -9%** | Faster customer communication | +2% NPS |


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

```text
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

1. **Regular Drills**: Quarterly practice
2. **Runbook Reviews**: Update post-incident
3. **Tool Training**: Universal knowledge
4. **Postmortem Culture**: Learn from all
5. **Metrics Review**: Monthly analysis

---

---

*"Smooth seas never made a skilled sailor—incidents make experienced engineers."*