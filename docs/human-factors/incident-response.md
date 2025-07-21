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
graph LR
    A[Detection] --> B[Triage]
    B --> C[Response]
    C --> D[Recovery]
    D --> E[Analysis]
    E --> F[Improvement]
    F --> A
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
```python
class IncidentResponseChecklist:
    def __init__(self):
        self.checklist = [
            "Acknowledge incident",
            "Assess severity",
            "Assemble response team",
            "Create incident channel/bridge",
            "Begin investigation",
            "Communicate status",
            "Implement fixes",
            "Verify resolution",
            "Document timeline",
            "Schedule postmortem"
        ]

    def validate_response(self, incident):
        completed = []
        missing = []

        for item in self.checklist:
            if self.is_completed(incident, item):
                completed.append(item)
            else:
                missing.append(item)

        return {
            'completed': completed,
            'missing': missing,
            'compliance': len(completed) / len(self.checklist)
        }
```

### Communication Templates

#### Initial Customer Communication
```text
We are currently investigating reports of [service] issues.
Our team is actively working on the problem.

Affected services: [list]
Impact: [description]

Next update in: 30 minutes
Status page: [link]
```

#### Update Communication
```text
Update on [service] incident:

Current status: [Investigating/Identified/Monitoring]
Progress: [what has been done]
Current impact: [updated impact]

Next update in: [timeframe]
```

#### Resolution Communication
```yaml
The [service] incident has been resolved.

Duration: [start time] - [end time]
Root cause: [brief explanation]
Actions taken: [summary]

A detailed postmortem will follow.
Thank you for your patience.
```

## Incident Response Automation

```python
class IncidentAutomation:
    def __init__(self):
        self.pagerduty = PagerDutyClient()
        self.slack = SlackClient()
        self.statuspage = StatusPageClient()

    def create_incident(self, alert):
        # Create PagerDuty incident
        incident = self.pagerduty.create_incident({
            'title': alert.title,
            'service': alert.service,
            'urgency': self.calculate_urgency(alert)
        })

        # Create Slack channel
        channel = self.slack.create_channel(
            f"incident-{incident.id}",
            purpose=f"Response for: {alert.title}"
        )

        # Invite on-call team
        oncall = self.pagerduty.get_oncall(alert.service)
        self.slack.invite_users(channel, oncall)

        # Post initial message
        self.slack.post_message(channel, self.format_incident_message(incident))

        # Update status page
        self.statuspage.create_incident({
            'name': alert.title,
            'status': 'investigating',
            'impact': self.determine_impact(alert)
        })

        return incident
```

## On-Call Best Practices

### 1. On-Call Rotation
```yaml
on_call_schedule:
  rotation_period: 1_week
  team_size: 6
  shifts:
    primary:
      start: Monday 9:00
      duration: 168h
    secondary:
      start: Monday 9:00
      duration: 168h
  handoff_process:
    - Review open incidents
    - Discuss recent issues
    - Update documentation
    - Confirm contact info
```

### 2. On-Call Kit
- Laptop with VPN access
- Phone with PagerDuty app
- Access to all critical systems
- Runbook repository access
- Emergency contact list

### 3. Escalation Policies
```python
class EscalationPolicy:
    def __init__(self):
        self.levels = [
            {
                'timeout': 5,  # minutes
                'targets': ['primary_oncall']
            },
            {
                'timeout': 10,
                'targets': ['secondary_oncall', 'team_lead']
            },
            {
                'timeout': 15,
                'targets': ['director', 'vp_engineering']
            }
        ]

    def get_escalation_targets(self, incident_age_minutes):
        targets = []
        for level in self.levels:
            if incident_age_minutes >= level['timeout']:
                targets.extend(level['targets'])
        return list(set(targets))
```

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
```python
class IncidentMetrics:
    def calculate_mttr(self, incidents):
        total_time = sum(
            (inc.resolved_at - inc.started_at).total_seconds()
            for inc in incidents
        )
        return total_time / len(incidents) / 60  # minutes

    def calculate_mtta(self, incidents):
        total_time = sum(
            (inc.acknowledged_at - inc.triggered_at).total_seconds()
            for inc in incidents
        )
        return total_time / len(incidents) / 60  # minutes

    def generate_report(self, incidents):
        return {
            'total_incidents': len(incidents),
            'mttr_minutes': self.calculate_mttr(incidents),
            'mtta_minutes': self.calculate_mtta(incidents),
            'by_severity': self.group_by_severity(incidents),
            'by_service': self.group_by_service(incidents),
            'repeat_incidents': self.find_repeat_incidents(incidents)
        }
```

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
