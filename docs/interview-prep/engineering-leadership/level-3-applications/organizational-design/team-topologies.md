# Team Topology Patterns for Engineering Leaders

## Overview

As an engineering leader, one of your most impactful decisions is how to organize teams. The wrong structure can create friction, slow velocity, and frustrate engineers. The right structure enables autonomy, speed, and innovation. This guide covers proven patterns and anti-patterns.

## Conway's Law in Practice

> "Organizations which design systems are constrained to produce designs which are copies of the communication structures of these organizations." - Melvin Conway

### Practical Implications
- Your team structure will mirror your architecture
- Changing architecture requires changing teams
- Communication paths become API boundaries
- Handoffs between teams become system bottlenecks

### Interview Example
"When we moved from monolith to microservices, I first redesigned our team structure. Instead of functional teams (frontend, backend, DBA), I created full-stack feature teams. This allowed each team to own their services end-to-end, reducing coordination overhead by 60%."

## Core Team Types

### 1. Stream-Aligned Teams (Feature Teams)
**Purpose**: Deliver value directly to customers

**Characteristics**:
- 5-9 engineers (two-pizza rule)
- Full-stack capabilities
- Own features end-to-end
- Direct customer feedback loop

**When to Use**:
- Product-focused companies
- Rapid iteration needed
- Clear product boundaries
- B2C or B2B2C models

**Example Structure**:
```
Checkout Team
├── Frontend Engineer (2)
├── Backend Engineer (3)
├── iOS Engineer (1)
├── Android Engineer (1)
├── QA Engineer (1)
└── Engineering Manager (1)
```

### 2. Platform Teams
**Purpose**: Enable stream-aligned teams to deliver faster

**Characteristics**:
- 4-8 engineers
- Deep technical expertise
- API/tool builders
- Internal customers

**When to Use**:
- 30+ engineers total
- Common needs across teams
- Technical complexity requiring specialists
- Economies of scale needed

**Platform Examples**:
- Developer Productivity (CI/CD, testing)
- Data Platform (pipelines, warehousing)
- Infrastructure (Kubernetes, monitoring)
- Identity & Access Management

### 3. Enabling Teams
**Purpose**: Grow capabilities of other teams

**Characteristics**:
- 2-4 experts
- Temporary engagements
- Teaching/coaching focus
- Success = working themselves out of job

**When to Use**:
- New technology adoption
- Skill gaps across teams
- Major technical transitions
- Quality improvements needed

**Example Engagements**:
- SRE team teaching reliability practices
- Security team implementing SecOps
- Architecture team guiding migrations

### 4. Complicated Subsystem Teams
**Purpose**: Own technically complex components

**Characteristics**:
- 3-6 deep experts
- Mathematical/algorithmic focus
- Stable APIs
- Long-term ownership

**When to Use**:
- ML/AI components
- Video encoding/streaming
- Search algorithms
- Real-time systems

## Organizational Patterns

### Pattern 1: Spotify Model (Squads, Tribes, Chapters, Guilds)

```
Tribe: Payments (40 engineers)
├── Squad: Checkout (8)
├── Squad: Fraud Detection (7)
├── Squad: Payment Methods (8)
├── Squad: Reconciliation (6)
├── Squad: Platform (6)
└── Squad: International (5)

Chapters (Functional Excellence):
├── Backend Chapter
├── Frontend Chapter
├── Mobile Chapter
└── QA Chapter

Guilds (Communities of Practice):
├── Security Guild
├── Performance Guild
└── Machine Learning Guild
```

**Interview Talking Points**:
- Balances autonomy with functional excellence
- Chapters prevent skill silos
- Guilds spread innovation
- Requires strong engineering culture

### Pattern 2: Platform + Product Teams

```
Product Teams (70%)
├── Search Team
├── Recommendations Team
├── User Profile Team
└── Messaging Team

Platform Teams (30%)
├── Infrastructure Platform
├── Data Platform
├── Developer Experience
└── Security Platform
```

**When This Works**:
- Clear platform/product boundaries
- Platform team has clear customers
- Strong product management
- Good engineering/product ratio

### Pattern 3: Service-Oriented Teams

```
Services aligned to business domains:
├── Identity Service Team
├── Catalog Service Team
├── Order Service Team
├── Fulfillment Service Team
├── Notification Service Team
└── Analytics Service Team
```

**Benefits**:
- Clear ownership boundaries
- Reduces coordination
- Enables team autonomy
- Scales naturally

## Anti-Patterns to Avoid

### 1. The Feature Factory
❌ All teams are feature teams
❌ No platform investment
❌ Every team reinvents the wheel
❌ Technical debt accumulates

**Fix**: Allocate 20-30% to platform teams

### 2. The Ivory Tower
❌ Platform team disconnected from products
❌ Builds things nobody uses
❌ Over-engineers solutions
❌ No customer feedback

**Fix**: Platform teams must have internal SLAs and NPS

### 3. The Matrix Maze
❌ Everyone reports to multiple managers
❌ Unclear ownership
❌ Decisions take forever
❌ Accountability diffusion

**Fix**: Single reporting line, clear RACI

### 4. The Silo Fortress
❌ No communication between teams
❌ Duplicate work everywhere
❌ Integration nightmares
❌ "Not my problem" culture

**Fix**: Regular demos, rotation programs, shared OKRs

## Scaling Considerations

### 10 → 30 Engineers
- Start with feature teams
- Extract first platform team (usually DevOps)
- Maintain single reporting line
- Focus on communication

### 30 → 100 Engineers
- Create 2-3 platform teams
- Introduce team-of-teams concept
- Consider chapter model
- Implement architecture reviews

### 100 → 300 Engineers
- Full platform organization
- Multiple tribes/divisions
- Enabling teams for transitions
- Formal governance needed

### 300+ Engineers
- Business unit structure
- Federated platforms
- Centers of excellence
- Internal marketplaces

## Interview Scenarios

### Scenario 1: Reorg Planning
**Question**: "You're taking over a 50-person org with low velocity. How do you approach reorganization?"

**Answer Framework**:
1. **Assess Current State** (Weeks 1-2)
   - Map current teams to value streams
   - Identify dependencies and handoffs
   - Survey team satisfaction
   - Analyze delivery metrics

2. **Design Future State** (Weeks 3-4)
   - Align teams to products/services
   - Reduce dependencies
   - Create platform capabilities
   - Plan transition phases

3. **Execute Transition** (Months 2-6)
   - Communicate why and how
   - Move volunteers first
   - Maintain delivery during transition
   - Measure and adjust

### Scenario 2: Platform Investment
**Question**: "How do you justify creating a platform team to business stakeholders?"

**Business Case Structure**:
```
Current State:
- 5 teams spending 30% time on infrastructure
- Inconsistent practices costing $2M in incidents
- 3-month onboarding for new services

Platform Team Investment:
- 6 engineers + 1 manager = $1.5M/year

Expected Returns:
- 5 teams get 30% time back = $3M value
- 50% reduction in incidents = $1M saved
- 3 months → 1 week onboarding = $500K saved
- ROI: 200% in year 1
```

### Scenario 3: Cross-Team Collaboration
**Question**: "How do you structure teams when building a two-sided marketplace?"

**Topology Design**:
```
Stream-Aligned Teams:
├── Buyer Experience Team
├── Seller Experience Team
├── Discovery/Search Team
└── Trust & Safety Team

Platform Teams:
├── Marketplace Platform (matching engine)
├── Payment Platform
└── Identity Platform

Enabling Teams:
└── Mobile Excellence Team

Coordination Mechanisms:
- Weekly marketplace leads sync
- Shared OKRs on GMV
- Rotating "exchange program"
- Joint architecture reviews
```

## Metrics That Matter

### Team Health Metrics
- Cycle time (idea → production)
- Deployment frequency
- Cross-team dependencies
- Team cognitive load
- Engineer satisfaction (eNPS)

### Organizational Metrics
- Time to create new service
- Mean time to onboard engineer
- Percentage of shared code/platforms
- Number of handoffs per feature
- Architecture-team alignment score

## Real-World Examples

### Example 1: Netflix
- Small autonomous teams (5-7 people)
- Full ownership and accountability
- Platform teams provide paved roads
- No mandates, only better options

### Example 2: Amazon
- Two-pizza teams
- Service-oriented architecture
- Clear ownership boundaries
- APIs between everything

### Example 3: Spotify
- Autonomous squads
- Tribes for alignment
- Chapters for craft excellence
- Guilds for knowledge sharing

## Key Takeaways for Interviews

### Do's
- ✅ Show you understand Conway's Law
- ✅ Connect team design to business outcomes
- ✅ Discuss trade-offs explicitly
- ✅ Have experience with transitions
- ✅ Measure impact of changes

### Don'ts
- ❌ Copy models without adaptation
- ❌ Reorg for reorg's sake
- ❌ Ignore cultural factors
- ❌ Underestimate transition costs
- ❌ Forget about people impact

---

**Remember**: The best team topology is the one that minimizes coordination costs while maximizing value delivery. There's no one-size-fits-all solution—context is king.'''