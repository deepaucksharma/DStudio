Page 78: SRE Practices
Running systems reliably at scale
SRE FUNDAMENTALS
SRE = Software Engineering applied to Operations

Core Tenets:
1. Embrace risk (100% reliability is wrong target)
2. Service Level Objectives (SLOs) are key
3. Toil elimination through automation
4. Monitoring distributed systems
5. Emergency response
6. Change management
7. Capacity planning
ERROR BUDGETS
Concept
Error Budget = 100% - SLO

Example:
- SLO: 99.9% availability
- Error Budget: 0.1% = 43.8 minutes/month
- Spend budget on:
  - Feature velocity
  - Experiments
  - Technical debt
Error Budget Policy
if error_budget_remaining > 50%:
    # Green zone
    - Ship features aggressively
    - Run chaos experiments
    - Refactor at will
    
elif error_budget_remaining > 25%:
    # Yellow zone
    - Feature freeze for unstable services
    - Focus on reliability improvements
    - Increase testing
    
else:
    # Red zone
    - Complete feature freeze
    - All hands on reliability
    - Post-mortem for all incidents
    - Executive escalation
SLI/SLO/SLA HIERARCHY
Service Level Indicators (SLIs)
"What we measure"

Good SLIs:
- Request latency (p50, p95, p99)
- Error rate (5xx errors / total)
- Availability (successful probes / total)
- Throughput (requests/second)

Bad SLIs:
- CPU usage (users don't care)
- Memory consumption (implementation detail)
- Thread count (meaningless to users)
Service Level Objectives (SLOs)
"What we promise ourselves"

Examples:
- 99.9% of requests < 100ms latency
- 99.95% availability per month
- <0.01% error rate

Setting SLOs:
1. Look at historical performance
2. Understand user expectations
3. Consider business impact
4. Leave room for innovation
Service Level Agreements (SLAs)
"What we promise customers"

SLA < SLO (always have buffer)

Example:
- SLO: 99.9% (43.8 min/month)
- SLA: 99.5% (216 min/month)
- Buffer: 172.2 minutes
TOIL ELIMINATION
What is Toil?
- Manual
- Repetitive  
- Automatable
- Tactical
- No lasting value
- Scales with service

Not Toil:
- Overhead (meetings, planning)
- Code development
- Architecture work
Toil Budget
Target: <50% of time on toil

Measurement:
- Track all operational work
- Categorize as toil vs engineering
- Weekly/monthly reporting
- Team goal on reduction

Example tracking:
Week 1: 30 hours toil / 40 hours = 75% (bad)
Week 4: 15 hours toil / 40 hours = 37% (good)
Toil Elimination Playbook
1. Measure current toil
2. Rank by time consumed
3. Automate highest impact
4. Document what can't be automated
5. Create self-service tools
6. Push back on toil sources

Example automation progression:
Manual deployment (2hr/week)
→ Script deployment (30min/week)
→ CI/CD pipeline (5min/week)
→ GitOps (0min/week)
ON-CALL PRACTICES
On-Call Philosophy
- On-call is a professional responsibility
- Must be sustainable
- Compensated appropriately
- Learning opportunity
- Shared fairly
On-Call Structure
Rotation:
- Primary: First responder
- Secondary: Backup/escalation
- Tertiary: Management escalation

Schedule:
- 1 week rotations (sustainable)
- Follow the sun (global teams)
- No more than 1 in 4 weeks
- Handoff procedure mandatory
Incident Response
1. DETECT
   - Alert fires
   - Customer report
   - Proactive discovery

2. TRIAGE
   - Severity assessment
   - Impact analysis
   - Stakeholder notification

3. MITIGATE
   - Stop the bleeding
   - Restore service
   - Document actions

4. RESOLVE
   - Root cause analysis
   - Permanent fix
   - Verification

5. LEARN
   - Blameless postmortem
   - Action items
   - Process improvements
POSTMORTEM CULTURE
Blameless Postmortems
Focus on:
- What happened (timeline)
- How it happened (contributing factors)
- How to prevent recurrence

Not on:
- Who caused it
- Punishment
- Blame

Template:
# Incident Title
Date: 
Duration:
Impact:

## Timeline
- 10:00 Deployment started
- 10:05 Errors spike
- 10:10 Page fired
- etc.

## Root Cause
Technical failure that allowed incident

## Contributing Factors
- Lack of testing
- Missing alerts
- Unclear runbook

## Action Items
- [ ] Add integration test
- [ ] Improve monitoring
- [ ] Update runbook

## Lessons Learned
What we learned from this incident
CHANGE MANAGEMENT
Safe Change Practices
1. Progressive Rollout
   - Dev → Staging → Canary → Production
   - 1% → 10% → 50% → 100%

2. Feature Flags
   - Decouple deploy from release
   - Instant rollback capability
   - A/B testing built-in

3. Automated Validation
   - Health checks
   - Smoke tests
   - Rollback triggers

4. Change Calendar
   - No Friday deployments
   - Freeze during peak seasons
   - Coordination across teams
CAPACITY PLANNING
Capacity Planning Process
1. Measure current usage
2. Project growth
3. Add safety margin
4. Plan purchases
5. Execute changes
6. Validate predictions

Timeline:
- Daily: Monitor usage
- Weekly: Review trends
- Monthly: Update projections
- Quarterly: Major purchases
- Yearly: Architecture review
SRE TEAM STRUCTURE
Embedded SRE
- SREs on product teams
- Deep service knowledge
- Direct influence
- Risk: Silo formation
Centralized SRE
- SRE as separate team
- Broad platform view
- Consistent practices
- Risk: Disconnection
Hybrid Model
- Core SRE team + embedded
- Rotation program
- Best of both worlds
- Most complex to manage
SRE METRICS
Team Health
- Toil percentage
- On-call load
- Incident frequency
- MTTR trends
- Error budget burn rate
Service Health
- SLO compliance
- Incident count
- Change failure rate
- Deployment frequency
- Customer satisfaction