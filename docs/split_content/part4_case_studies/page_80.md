Page 80: Runbooks & Playbooks
Turning chaos into checklist
RUNBOOK PHILOSOPHY
A runbook is:
- Executable documentation
- Cognitive offload during stress
- Training material
- Automation target

Not:
- Set in stone
- Replacement for thinking
- Excuse for bad design
- One-time write
ANATOMY OF A GREAT RUNBOOK
1. Quick Actions (First 5 Minutes)
## IMMEDIATE ACTIONS
If you're here because of an alert:

1. [ ] Check dashboard: [link to dashboard]
2. [ ] Verify impact: [link to user metrics]
3. [ ] If customer-facing: Update status page

Quick fixes that often work:
- [ ] Restart service: `kubectl rollout restart deployment/api`
- [ ] Clear cache: `redis-cli FLUSHALL`
- [ ] Scale up: `kubectl scale deployment/api --replicas=+5`

If not resolved in 5 minutes, continue below...
2. Understanding the Alert
## WHAT THIS ALERT MEANS

Alert: HighErrorRate
Threshold: >1% 5xx errors for 5 minutes
Business Impact: Users cannot complete checkout
SLO Budget Impact: Burns 1 hour of monthly budget per minute

Common causes:
1. Database connection exhaustion (60% of incidents)
2. Downstream service failure (30%)
3. Bad deployment (10%)
3. Diagnostic Steps
## DIAGNOSIS CHECKLIST

### 1. Identify Error Pattern
```bash
# Check error logs
kubectl logs -l app=api --tail=100 | grep ERROR

# Common patterns:
# "connection refused" → Database issue
# "timeout" → Downstream service issue  
# "nil pointer" → Code bug
2. Check Dependencies

 Database connections: [query]
 Cache hit rate: [dashboard]
 Downstream service health: [status page]

3. Recent Changes
bash# Last 5 deployments
kubectl rollout history deployment/api

# Recent config changes
git log --oneline -n 10 configs/

**4. Resolution Procedures**
RESOLUTION PATHS
Path A: Database Connection Exhaustion (60% of cases)
Symptoms: "connection pool exhausted" errors

Immediate mitigation:
bash# Kill long-running queries
psql -c "SELECT pg_terminate_backend(pid) 
         FROM pg_stat_activity 
         WHERE state = 'active' 
         AND query_time > interval '5 minutes'"

Scale connection pool:
bashkubectl set env deployment/api DB_POOL_SIZE=200

Find root cause:

Check for query loops
Look for missing connection.close()
Review recent code changes



Path B: Downstream Service Failure (30% of cases)
[Details...]
Path C: Bad Deployment (10% of cases)
[Details...]

**5. Verification**
VERIFY RESOLUTION

 Error rate returning to normal
 No active customer complaints
 SLO burn rate acceptable
 No secondary issues

Monitor for 15 minutes before declaring resolved.

**PLAYBOOK PATTERNS**

**Disaster Recovery Playbook**
REGIONAL FAILOVER PLAYBOOK
DECISION CRITERIA
Failover if:

Primary region unavailable >5 minutes
Data corruption detected
Security breach confirmed

PRE-FLIGHT CHECKS

 Secondary region health: GREEN
 Data sync lag: <30 seconds
 Capacity available: >150%

FAILOVER PROCEDURE

 Notify stakeholders:

@incident-room
executives@company
customers via status page


 Execute failover:
bash./scripts/regional-failover.sh \
  --from=us-east-1 \
  --to=us-west-2 \
  --verify

 Update DNS:

TTL is 60 seconds
Propagation monitor: [link]


 Verify traffic shift:

 Load balancer targets updated
 No traffic to failed region
 Metrics flowing



ROLLBACK PROCEDURE
[If failover fails...]

**Security Incident Playbook**
DATA BREACH RESPONSE
IMMEDIATE CONTAINMENT

 Isolate affected systems
 Revoke compromised credentials
 Enable emergency logging

STAKEHOLDER NOTIFICATION
Within 1 hour:

 Security team
 Legal team
 Executive team

Within 4 hours:

 Customer success
 PR team
 Compliance officer

INVESTIGATION
[Forensics procedures...]

**RUNBOOK QUALITY CHECKLIST**
GOOD RUNBOOK CHECKLIST
Content:
□ Starts with quick actions
□ Clear success criteria
□ Multiple resolution paths
□ Rollback procedures
□ Verification steps
Format:
□ Scannable headers
□ Copy-paste commands
□ Checkbox tasks
□ Links to tools
□ Time estimates
Maintenance:
□ Last updated date
□ Owner identified
□ Review schedule
□ Version controlled
□ Test procedure
Usage:
□ <10 minute read
□ Works under stress
□ No assumed knowledge
□ Feedback mechanism
□ Analytics tracking

**RUNBOOK AUTOMATION**

**Evolution Path**
Level 1: Word document

Static
Out of date
Not tested

Level 2: Wiki/Markdown

Version controlled
Searchable
Links to tools

Level 3: Interactive

Dynamic data
One-click actions
Auto-updates

Level 4: Automated

Self-executing
Human approval points
Full automation


**Example Automation**
```python
class DatabaseFailoverRunbook:
    def __init__(self):
        self.steps = [
            self.check_primary_health,
            self.verify_secondary_ready,
            self.get_approval,
            self.execute_failover,
            self.verify_traffic_shifted,
            self.notify_stakeholders
        ]
    
    async def execute(self):
        for step in self.steps:
            result = await step()
            if not result.success:
                await self.rollback()
                return
        
        await self.mark_complete()
    
    async def check_primary_health(self):
        health = await check_database_health('primary')
        if health.status == 'healthy':
            raise AbortRunbook("Primary is healthy")
        return StepResult(success=True, data=health)
RUNBOOK METRICS
Usage Analytics
Track:
- Runbook execution frequency
- Time to resolution
- Success rate
- Most used sections
- Abandoned procedures

Dashboard shows:
- Top 10 runbooks by usage
- Average resolution time
- Runbook effectiveness
- Update frequency
- Team coverage
RUNBOOK CULTURE
Writing Culture
- Every incident produces/updates a runbook
- New features include runbooks
- Runbooks reviewed like code
- Regular runbook fire drills
- Gamification for contributions
Testing Culture
Monthly runbook day:
- Each team tests 2 runbooks
- Find outdated information
- Update and improve
- Share learnings

Chaos engineering:
- Trigger real incidents
- Follow runbooks exactly
- Measure effectiveness
- Update based on results
COMMON RUNBOOK MISTAKES
1. Too Generic
Bad: "Check the logs for errors"
Good: "Run: kubectl logs -l app=api --since=10m | grep ERROR"
2. Missing Context
Bad: "Scale up if needed"
Good: "If CPU >80%, scale: kubectl scale deployment/api --replicas=+5"
3. No Verification
Bad: "Restart the service"
Good: "Restart: [command]. Verify: Check [metric] returns to <0.1%"
4. Out of Date
Bad: Last updated 2 years ago
Good: Auto-generated from monitoring + monthly review