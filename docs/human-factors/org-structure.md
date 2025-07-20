---
title: Org-Structure Physics
description: ""Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure."
- Melvin Co..."
type: human-factors
difficulty: beginner
reading_time: 60 min
prerequisites: []
status: complete
last_updated: 2025-07-20
---

<!-- Navigation -->
[Home](/) → [Part V: Human Factors](/human-factors/) → **Org-Structure Physics**

# Org-Structure Physics

**Conway's Law in action: You ship your org chart**

## Conway's Law

"Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure."
- Melvin Conway, 1967

This isn't a suggestion. It's physics.

## Why Conway's Law is Inevitable

### Communication Bandwidth

```text
Team A ←──high bandwidth──→ Team A members
   ↓
   low bandwidth
   ↓
Team B ←──high bandwidth──→ Team B members
```

Result: Natural module boundaries form at team boundaries.

### The Physics

1. **Information flow follows org structure**
   - Same team: Rich, frequent communication
   - Different teams: Meetings, tickets, emails
   - Different orgs: Contracts, SLAs, APIs

2. **Interfaces emerge at boundaries**
   - Within team: Method calls, shared memory
   - Between teams: REST APIs, message queues
   - Between companies: Public APIs, webhooks

3. **Architecture mirrors hierarchy**
   - Monolith ← Single team
   - Services ← Multiple teams
   - Platforms ← Organizational divisions

## Organizational Patterns

### 1. Functional Organization

```text
         CTO
      /   |   \
   Eng   QA   Ops
```

**System Architecture:**
- Dev throws code over wall to QA
- QA throws bugs back to Dev
- Ops throws incidents back to everyone

**Result:** Waterfall process, slow delivery

### 2. Product Teams

```text
    Product Org
    /    |    \
Team A  Team B  Team C
(Full   (Full   (Full
Stack)  Stack)  Stack)
```

**System Architecture:**
- Service A (owned by Team A)
- Service B (owned by Team B)
- Service C (owned by Team C)
- APIs between services

**Result:** Microservices, clear ownership

### 3. Platform Model

```text
    Product Teams
         ↓
    Platform Team
         ↓
    Infrastructure
```

**System Architecture:**
- Standardized platform APIs
- Self-service infrastructure
- Clear abstraction layers

**Result:** Scalable development

### 4. Matrix Organization

```text
   Feature Teams ←→ Component Teams
        ↓               ↓
   Product Focus    Technical Focus
```

**System Architecture:**
- Shared components
- Complex dependencies
- Conflicting priorities

**Result:** Coordination overhead

## Team Topologies

### Stream-Aligned Teams

**Purpose:** Deliver value streams

```python
class StreamAlignedTeam:
    """
    - Own entire feature/product
    - Direct customer value
    - Fast flow of work
    - Minimal dependencies
    """
    size = "5-9 people"
    owns = ["frontend", "backend", "database", "deployment"]
    cognitive_load = "one domain"
```

### Platform Teams

**Purpose:** Enable stream-aligned teams

```python
class PlatformTeam:
    """
    - Build internal products
    - Hide complexity
    - Self-service APIs
    - Force multiplier
    """
    customers = "internal teams"
    products = ["deployment platform", "monitoring", "data pipeline"]
    success_metric = "adoption rate"
```

### Enabling Teams

**Purpose:** Help teams adopt new practices

```python
class EnablingTeam:
    """
    - Coaching and facilitation
    - Temporary engagement
    - Knowledge transfer
    - Best practices
    """
    mode = "consulting"
    duration = "3-6 months per engagement"
    goal = "team self-sufficiency"
```

### Complicated Subsystem Teams

**Purpose:** Own complex domains

```python
class SubsystemTeam:
    """
    - Deep expertise required
    - Mathematical/algorithmic complexity
    - Would overload stream teams
    - Clear interface needed
    """
    examples = ["ML models", "video codec", "crypto", "search"]
    interface = "simple API hiding complexity"
```

## Communication Patterns

### Team Interaction Modes

**1. Collaboration**
- Working together
- Fuzzy boundaries
- High bandwidth
- Innovation mode

**2. X-as-a-Service**
- Clear API/contract
- Consumer/provider
- Low coupling
- Execution mode

**3. Facilitating**
- Coaching/mentoring
- Temporary
- Knowledge transfer
- Growth mode

### Choosing Interaction Modes

```python
def select_interaction_mode(context):
    if context.exploring_new_tech:
        return "collaboration"
    elif context.established_pattern:
        return "x-as-a-service"
    elif context.capability_gap:
        return "facilitating"
    else:
        raise ValueError("Unclear context")
```

## The Inverse Conway Maneuver

### Definition

Deliberately structuring teams to achieve desired architecture.

### Process

1. **Design target architecture**
   ```text
   Ideal System Architecture
   ├── User Service
   ├── Order Service
   ├── Payment Service
   └── Notification Service
   ```

2. **Create matching org structure**
   ```
   Engineering Organization
   ├── User Team
   ├── Order Team
   ├── Payment Team
   └── Notification Team
   ```

3. **Let Conway's Law work**
   - Teams naturally build their services
   - Interfaces emerge at team boundaries
   - Architecture follows organization

### Example: Monolith to Microservices

**Before:**
```
Single Team → Monolith
```text
**Transition:**
```python
# 1. Identify bounded contexts
contexts = [
    "user_management",
    "order_processing",
    "payment_handling",
    "notifications"
]

# 2. Create teams per context
for context in contexts:
    create_team(
        name=f"{context}_team",
        members=5,
        ownership=context
    )

# 3. Teams extract their services
# Architecture emerges naturally
```text
**After:**
```
User Team → User Service
Order Team → Order Service
Payment Team → Payment Service
Notification Team → Notification Service
```bash
## Anti-Patterns

### 1. Misaligned Architecture

**Symptom:** Cross-team dependencies everywhere

```
Team A owns: [ServiceA, half of ServiceB]
Team B owns: [half of ServiceB, ServiceC]
Result: Coordination nightmare
```proto
**Fix:** Align service boundaries with team boundaries

### 2. Shared Ownership

**Symptom:** "Everyone owns it" = "No one owns it"

```python
# Anti-pattern
service_owners = {
    "platform": ["team_a", "team_b", "team_c"],
    "result": "ignored_until_fire"
}

# Better
service_owners = {
    "platform": "platform_team",
    "sla": "99.9%",
    "on_call": "platform_team"
}
```bash
### 3. Cognitive Overload

**Symptom:** Team owns too many unrelated things

```
TeamX owns:
- User authentication
- Email service
- Report generation
- Data pipeline
- Mobile app
- Kitchen sink

Result: Nothing done well
```yaml
**Fix:** Split into focused teams

### 4. Awkward Handoffs

**Symptom:** Work ping-pongs between teams

```
Feature Flow:
Frontend Team → Backend Team → Frontend Team →
Database Team → Backend Team → Deploy Team →
Frontend Team → Done (6 months later)
```yaml
**Fix:** Stream-aligned teams with full ownership

## Scaling Patterns

### Dunbar's Number

Cognitive limit for relationships: ~150 people

**Implications:**
```
Team: 5-9 people (deep trust)
  ↓
Tribe: 50-150 people (know everyone)
  ↓
Division: 500-1500 people (know of everyone)
  ↓
Company: Federated divisions
```bash
### Scaling Models

**1. Spotify Model**
```
Squad (team) → Tribe (collection) → Guild (practice)
                                    ↓
                                Chapter (expertise)
```text
**2. Amazon Model**
```
Two-Pizza Team → Single-threaded owner → Full P&L
                                         ↓
                                    Service API
```text
**3. Google Model**
```
Small Team → Tech Lead/Manager → Director → VP
             ↓
        Engineering Excellence (SRE, EngProd)
```bash
## Measuring Organizational Effectiveness

### Team Health Metrics

```python
class TeamHealthCheck:
    def assess(self, team):
        return {
            'deployment_frequency': self.measure_deploy_freq(team),
            'lead_time': self.measure_commit_to_prod(team),
            'mttr': self.measure_recovery_time(team),
            'change_failure_rate': self.measure_failed_deploys(team),
            'cognitive_load': self.survey_team_stress(team),
            'dependencies': self.count_blocking_deps(team)
        }
```bash
### Communication Health

```sql
-- Meeting overhead by team
SELECT
    team,
    AVG(meetings_per_week) as avg_meetings,
    AVG(meeting_hours_per_week) as avg_hours,
    AVG(cross_team_meetings) as coordination_overhead
FROM team_calendars
GROUP BY team
ORDER BY coordination_overhead DESC;
```bash
### Architecture-Org Alignment

```python
def measure_conway_alignment(org_structure, system_architecture):
    """
    Measure how well org matches architecture
    """
    misalignments = []

    for service in system_architecture:
        owners = get_service_owners(service)
        if len(owners) > 1:
            misalignments.append({
                'service': service,
                'issue': 'multiple_owners',
                'owners': owners
            })

        dependencies = get_service_dependencies(service)
        for dep in dependencies:
            if not same_team(service.owner, dep.owner):
                if interaction_frequency(service, dep) > threshold:
                    misalignments.append({
                        'issue': 'high_coupling_across_teams',
                        'services': [service, dep]
                    })

    return misalignments
```proto
## Best Practices

1. **Design Organization Intentionally**
   - Org structure is architecture
   - Plan both together
   - Use Inverse Conway Maneuver

2. **Minimize Cognitive Load**
   - One team, one domain
   - Clear boundaries
   - Limit work in progress

3. **Optimize Communication**
   - Colocate when collaborating
   - APIs when executing
   - Documentation always

4. **Enable Team Autonomy**
   - Full ownership
   - Minimal dependencies
   - Self-service platforms

5. **Evolve Thoughtfully**
   - Team topology changes are expensive
   - Plan transitions carefully
   - Communicate extensively

## Case Study: Ride-Sharing Reorg

**Initial Structure (Functional):**
```
Mobile Team → Backend Team → Data Team
Result: 3-month feature cycle
```yaml
**Problem:** Features required coordination across all teams

**Reorganization (Stream-aligned):**
```
Rider Team: [mobile, backend, data engineers]
Driver Team: [mobile, backend, data engineers]
Marketplace Team: [algorithms, backend, data]
```

**Results:**
- Feature cycle: 3 months → 2 weeks
- Deployments: Monthly → Daily
- Team satisfaction: 6/10 → 8.5/10

**Architecture evolved to match:**
- Rider Service (owned by Rider Team)
- Driver Service (owned by Driver Team)
- Matching Service (owned by Marketplace Team)
- Clean APIs between services

## Key Takeaways

- **Conway's Law is inevitable** - Work with it, not against it
- **Team Topologies matter** - Choose patterns that fit your goals
- **Cognitive load is real** - Respect human limitations
- **Architecture follows organization** - Design both together
- **Communication paths define systems** - Optimize for flow

Remember: You can't fight Conway's Law, but you can use it to your advantage. Design your organization to build the system you want.
