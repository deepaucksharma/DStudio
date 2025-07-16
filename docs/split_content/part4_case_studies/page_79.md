Page 79: Org-Structure Physics
Conway's Law in action: You ship your org chart
CONWAY'S LAW
"Organizations which design systems are constrained to 
produce designs which are copies of the communication 
structures of these organizations"

Implication: Fix your org to fix your architecture
ORGANIZATIONAL PATTERNS
1. Functional Teams
Structure:
├── Frontend Team
├── Backend Team  
├── Database Team
└── Operations Team

Results in:
- Layered architecture
- Handoffs between layers
- Integration challenges
- Slow feature delivery

Best for:
- Small companies
- Stable products
- Clear boundaries
2. Feature Teams
Structure:
├── Checkout Team (full stack)
├── Search Team (full stack)
├── Recommendations Team (full stack)
└── Platform Team

Results in:
- Microservices
- Duplicate solutions
- Fast feature delivery
- Integration overhead

Best for:
- Product companies
- Rapid iteration
- Customer focus
3. Matrix Organization
Structure:
        PM   Eng  Design
Checkout ×    ×     ×
Search   ×    ×     ×  
Platform ×    ×     ×

Results in:
- Flexible resourcing
- Complex coordination
- Shared ownership
- Decision paralysis

Best for:
- Agencies
- Consulting
- Project-based work
TEAM TOPOLOGIES
Stream-Aligned Teams
Purpose: Feature delivery
Size: 5-9 people
Cognitive Load: One domain
Dependencies: Minimal

Example:
- Payments team
- Full ownership
- Direct customer value
- Independent releases
Platform Teams
Purpose: Enable stream teams
Size: Varies
Focus: Self-service tools
Success Metric: Adoption

Example:
- Kubernetes platform
- CI/CD pipelines
- Observability stack
- Security tools
Enabling Teams
Purpose: Grow capabilities
Size: Small (3-5)
Mode: Temporary engagement
Goal: Knowledge transfer

Example:
- SRE coaching
- Security reviews
- Performance tuning
- Architecture guidance
Complicated Subsystem Teams
Purpose: Specialist knowledge
Size: Varies
Focus: Deep expertise
Interface: Clear API

Example:
- ML platform
- Video encoding
- Search algorithm
- Fraud detection
COMMUNICATION PATTERNS
Team Interaction Modes
1. Collaboration
When: Discovery phase
Duration: Limited
Purpose: Innovation

Example: Two teams working on new API design
Risk: Cognitive overload if permanent
2. X-as-a-Service
When: Clear requirements
Duration: Ongoing
Purpose: Scale

Example: Platform provides deployment service
Risk: Bottlenecks if not self-service
3. Facilitating
When: Capability gaps
Duration: Temporary
Purpose: Enable

Example: SRE team teaching observability
Risk: Dependency if not time-boxed
COGNITIVE LOAD
Types of Cognitive Load
1. Intrinsic: Fundamental task complexity
2. Extraneous: Irrelevant complexity
3. Germane: Learning and improvement

Team Capacity = Limit - (Intrinsic + Extraneous)
Reducing Cognitive Load
- Clear boundaries
- Good documentation
- Automated operations
- Stable interfaces
- Limited domains

Signs of overload:
- Missed deadlines
- Quality issues
- Team burnout
- Context switching
- Knowledge silos
INVERSE CONWAY MANEUVER
Process
1. Design target architecture
2. Organize teams to match
3. Let system evolve naturally
4. Architecture follows organization

Example:
Want microservices?
→ Create independent teams
→ Give them business domains
→ Minimize dependencies
→ Watch services emerge
SCALING PATTERNS
Dunbar's Number
~150: Tribal limit
~50: Trust limit
~15: Deep trust
~5: Close collaboration

Applied to tech:
- Company: <150 people = one tribe
- Division: ~50 people
- Team: 5-9 people
Scaling Strategies
<10 people: Everyone talks to everyone
<50 people: Functional teams work
<150 people: Need clear structure
<500 people: Multiple tribes
>500 people: Full hierarchy needed
ORGANIZATIONAL ANTIPATTERNS
1. Ticket Tossing
Symptom: Work thrown over wall
Cause: Siloed teams
Fix: Shared ownership

Frontend: "Backend is slow"
Backend: "Database is the issue"
DBA: "Queries are inefficient"
Result: Nothing gets fixed
2. Architecture Astronauts
Symptom: Over-engineered solutions
Cause: Architects disconnected from implementation
Fix: Architects must code

"We need microservices, Kafka, and blockchain"
Reality: 10 users, CRUD app
3. Hero Culture
Symptom: Single person knows everything
Cause: No knowledge sharing
Fix: Documentation, pairing, rotation

"Only Jane can fix the payment system"
Risk: Jane leaves, system dies
MEASURING ORG HEALTH
Metrics
1. Deployment Frequency
   - Daily: Healthy
   - Weekly: OK
   - Monthly: Problematic

2. Lead Time
   - <1 day: Excellent
   - <1 week: Good
   - >1 month: Poor

3. Team Stability
   - <10% turnover: Healthy
   - 10-20%: Normal
   - >20%: Problems

4. Cross-team Dependencies
   - <2: Independent
   - 2-5: Manageable
   - >5: Restructure needed
REORG STRATEGIES
When to Reorganize
Signals:
- Architecture doesn't match org
- Constant coordination overhead
- Slow delivery
- Quality issues
- Team morale low

Not signals:
- New executive
- Industry trends
- Consultant recommendation
How to Reorganize
1. Map current state
   - Team boundaries
   - Communication flows
   - Pain points

2. Design target state
   - Clear ownership
   - Minimal dependencies
   - Balanced cognitive load

3. Incremental migration
   - One team at a time
   - Preserve knowledge
   - Measure impact

4. Continuous adjustment
   - Regular retrospectives
   - Data-driven decisions
   - Team feedback