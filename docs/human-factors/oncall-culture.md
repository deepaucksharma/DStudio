# On-Call Culture

<div class="navigation-header">
<div class="breadcrumb">
[Home](/) → [Human Factors](/human-factors/) → **On-Call Culture**
</div>
</div>

**Building sustainable and effective on-call practices**

> *"On-call should be a responsibility, not a punishment."*

---

## What is On-Call Culture?

On-call culture encompasses the practices, values, and systems that make 24/7 service support sustainable and effective while maintaining team health and morale.

## Core Principles

### 1. Shared Responsibility
- Everyone who can break production should help fix it
- Developers and operators share on-call duties
- Leadership participates in rotation

### 2. Sustainable Practices
- Reasonable rotation schedules
- Adequate compensation
- Time off after rough shifts
- Limit on consecutive incidents

### 3. Continuous Improvement
- Fix root causes, not just symptoms
- Invest in automation
- Improve monitoring and alerting
- Regular rotation retrospectives

## Building Healthy On-Call Rotations

### Rotation Models

| Model | Description | Pros | Cons |
|-------|-------------|------|------|
| **Follow the Sun** | Geographically distributed | No night shifts | Requires global team |
| **Weekly Primary/Secondary** | Two engineers per week | Backup available | Two people impacted |
| **Daily Rotation** | Different person each day | Minimal impact | More handoffs |
| **Team-based** | Entire team shares | Shared knowledge | Can impact whole team |

### Optimal Rotation Size
```python
def calculate_rotation_size(incidents_per_week, max_incidents_per_person=2):
    """
    Calculate optimal on-call rotation size
    
    Factors:
    - Each person on-call once per rotation cycle
    - No more than max_incidents per shift
    - Account for vacation/sick time (15%)
    """
    # Base calculation
    min_people = incidents_per_week / max_incidents_per_person
    
    # Add buffer for time off
    vacation_buffer = 1.15
    
    # Add buffer for burnout prevention
    burnout_buffer = 1.25
    
    optimal_size = int(min_people * vacation_buffer * burnout_buffer)
    
    # Minimum viable rotation
    return max(optimal_size, 4)
```

## On-Call Compensation

### Common Models

1. **Time-based Compensation**
   - Flat rate per on-call shift
   - Different rates for weekday/weekend
   - Additional pay for holidays

2. **Incident-based Compensation**
   - Base rate + per-incident payment
   - Escalating rates for multiple incidents
   - Severity-based compensation

3. **Time Off in Lieu**
   - Comp time for weekend shifts
   - Extra PTO after difficult rotations
   - Flexible working after incidents

### Example Compensation Structure
```yaml
on_call_compensation:
  base_rates:
    weekday: $500/week
    weekend: $750/week
    holiday: $1000/week
  
  incident_rates:
    first_incident: $0  # Included in base
    additional_incidents: $100/each
    after_hours_incident: $150/each
    
  time_off:
    weekend_shift: 0.5 days comp time
    holiday_shift: 1.0 days comp time
    rough_shift: Additional day off # >3 incidents
```

## Alert Quality and Hygiene

### Alert Quality Metrics
```python
class AlertQualityTracker:
    def __init__(self):
        self.alerts = []
    
    def calculate_alert_quality(self):
        total_alerts = len(self.alerts)
        actionable = sum(1 for a in self.alerts if a.actionable)
        
        return {
            'total_alerts': total_alerts,
            'actionable_rate': actionable / total_alerts,
            'noise_rate': 1 - (actionable / total_alerts),
            'false_positive_rate': sum(1 for a in self.alerts if a.false_positive) / total_alerts,
            'duplicate_rate': self.calculate_duplicate_rate()
        }
    
    def identify_noisy_alerts(self, threshold=0.5):
        """Find alerts with high false positive rate"""
        alert_stats = {}
        
        for alert in self.alerts:
            name = alert.name
            if name not in alert_stats:
                alert_stats[name] = {'total': 0, 'false_positives': 0}
            
            alert_stats[name]['total'] += 1
            if alert.false_positive:
                alert_stats[name]['false_positives'] += 1
        
        noisy_alerts = []
        for name, stats in alert_stats.items():
            false_rate = stats['false_positives'] / stats['total']
            if false_rate > threshold:
                noisy_alerts.append({
                    'name': name,
                    'false_positive_rate': false_rate,
                    'total_alerts': stats['total']
                })
        
        return sorted(noisy_alerts, key=lambda x: x['false_positive_rate'], reverse=True)
```

### Alert Standards

```yaml
alert_standards:
  required_fields:
    - title: Clear description of the problem
    - severity: SEV-1 through SEV-4
    - service: Affected service name
    - runbook: Link to resolution steps
    - dashboard: Link to relevant metrics
    
  quality_criteria:
    - Actionable: Engineer can do something
    - Urgent: Requires immediate attention
    - User-impacting: Affects customers
    - Unique: Not duplicate of other alerts
    
  slo_based_alerting:
    - Alert on symptoms, not causes
    - Use error budgets
    - Multi-window alerts (short and long term)
```

## On-Call Tools and Automation

### Essential On-Call Toolkit
```python
class OnCallToolkit:
    """Standard tools for on-call engineers"""
    
    def __init__(self):
        self.tools = {
            'alerting': ['PagerDuty', 'Opsgenie', 'VictorOps'],
            'communication': ['Slack', 'Zoom', 'StatusPage'],
            'monitoring': ['Datadog', 'Grafana', 'New Relic'],
            'incident_mgmt': ['Jira', 'Linear', 'ServiceNow'],
            'documentation': ['Confluence', 'Notion', 'Wiki'],
            'automation': ['Rundeck', 'Ansible', 'Jenkins']
        }
    
    def setup_new_oncall(self, engineer):
        """Setup checklist for new on-call engineer"""
        checklist = [
            "PagerDuty account and app installed",
            "Added to on-call Slack channels",
            "VPN access configured",
            "Production access provisioned",
            "Runbook repository access",
            "Shadow current on-call",
            "Review recent incidents",
            "Participate in game day exercise"
        ]
        
        return {
            'engineer': engineer,
            'checklist': checklist,
            'tools_access': self.provision_access(engineer)
        }
```

### Automation Opportunities
```python
class OnCallAutomation:
    """Automate common on-call tasks"""
    
    def auto_diagnosis(self, alert):
        """Automatically gather diagnostic information"""
        diagnostics = {
            'alert_details': alert,
            'recent_deployments': self.get_recent_deployments(alert.service),
            'error_logs': self.get_error_logs(alert.service, minutes=30),
            'metrics_snapshot': self.capture_metrics(alert.service),
            'dependencies_health': self.check_dependencies(alert.service),
            'similar_incidents': self.find_similar_incidents(alert)
        }
        
        # Post to incident channel
        self.post_diagnostics(alert.incident_channel, diagnostics)
        
        # Suggest likely causes
        causes = self.analyze_diagnostics(diagnostics)
        return causes
    
    def auto_remediation(self, alert):
        """Attempt safe auto-remediation"""
        safe_remediations = {
            'high_memory': self.restart_service,
            'stuck_jobs': self.clear_job_queue,
            'connection_exhaustion': self.reset_connections,
            'disk_full': self.cleanup_old_logs
        }
        
        if alert.type in safe_remediations:
            try:
                result = safe_remediations[alert.type](alert.service)
                self.log_remediation(alert, result)
                return result
            except Exception as e:
                self.escalate_to_human(alert, str(e))
```

## Psychological Safety and Support

### Supporting On-Call Engineers

1. **Pre-Incident Support**
   - Clear runbooks and documentation
   - Practice scenarios (game days)
   - Shadowing before first shift
   - Access to senior engineers

2. **During Incident Support**
   - No blame for waking people up
   - Encouragement to escalate
   - Clear decision-making authority
   - Support from leadership

3. **Post-Incident Support**
   - Blameless postmortems
   - Time to implement fixes
   - Recognition for good incident handling
   - Mental health resources

### Preventing Burnout
```python
class BurnoutPrevention:
    def __init__(self):
        self.engineer_stats = {}
    
    def track_oncall_load(self, engineer, week):
        stats = self.engineer_stats.get(engineer, {})
        
        return {
            'incidents_this_week': stats.get('incidents', 0),
            'night_pages_this_month': stats.get('night_pages', 0),
            'consecutive_rough_weeks': stats.get('rough_weeks', 0),
            'time_since_last_break': stats.get('weeks_on', 0)
        }
    
    def recommend_action(self, engineer):
        load = self.track_oncall_load(engineer, current_week())
        
        if load['consecutive_rough_weeks'] >= 2:
            return "Skip next rotation"
        elif load['night_pages_this_month'] >= 5:
            return "Weekday-only shifts for next rotation"
        elif load['time_since_last_break'] >= 8:
            return "Mandatory rotation break"
        else:
            return "Normal rotation"
```

## Measuring On-Call Health

### Key Metrics
```yaml
on_call_health_metrics:
  individual_metrics:
    - incidents_per_shift
    - night_pages_per_month
    - mttr_by_engineer
    - escalation_rate
    
  team_metrics:
    - rotation_participation_rate
    - voluntary_extra_shifts
    - on_call_survey_scores
    - turnover_rate
    
  system_metrics:
    - alert_quality_score
    - auto_remediation_rate
    - repeat_incident_rate
    - runbook_coverage
```

### Regular Surveys
```python
class OnCallSurvey:
    questions = [
        "How sustainable is our on-call rotation?",
        "How well-supported do you feel during incidents?",
        "How effective are our runbooks?",
        "How fair is the on-call compensation?",
        "What's your biggest on-call pain point?"
    ]
    
    def analyze_responses(self, responses):
        # Track trends over time
        # Identify problem areas
        # Generate action items
        pass
```

## Best Practices Summary

1. **Make it Sustainable**
   - Reasonable rotation sizes
   - Fair compensation
   - Limit consecutive incidents

2. **Provide Great Tools**
   - Effective alerting
   - Clear runbooks
   - Automation where possible

3. **Foster Learning**
   - Blameless culture
   - Share knowledge
   - Invest in improvements

4. **Support Your People**
   - Psychological safety
   - Clear escalation paths
   - Recognition and appreciation

---

<div class="navigation-footer">
<div class="pattern-relationships">
<h3>🔗 Related Concepts</h3>

**🤝 Related Topics**:
- [Incident Response](/human-factors/incident-response/) - Handling incidents effectively
- [SRE Practices](/human-factors/sre-practices/) - Reliability engineering culture
- [Team Topologies](/human-factors/team-topologies/) - Team organization

**🧠 Foundational Concepts**:
- [Axiom 7: Human Interface](/part1-axioms/axiom7-human-interface/) - Human factors in systems
- [Axiom 3: Failure](/part1-axioms/axiom3-failure/) - Why we need on-call
</div>
</div>

---

*"The best on-call rotation is one where engineers volunteer for extra shifts."*