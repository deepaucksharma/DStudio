# Google System Design Interview Evaluation Rubric

## Overview

This comprehensive evaluation framework helps candidates assess their performance in Google system design interviews using a structured 1-4 scoring scale across eight key competency areas.

## 📊 Scoring Scale

### Level 1: Needs Improvement (1.0 - 1.9)
**"Struggling with fundamentals"**
- Requires significant guidance
- Missing critical components
- Unable to justify decisions
- Communication gaps

### Level 2: Meets Expectations (2.0 - 2.9)
**"Solid foundation"**
- Completes basic design
- Makes reasonable choices
- Communicates adequately
- Some areas need refinement

### Level 3: Exceeds Expectations (3.0 - 3.9)
**"Strong performance"**
- Comprehensive design
- Well-justified decisions
- Clear communication
- Handles complexity well

### Level 4: Outstanding (4.0)
**"Exceptional demonstration"**
- Innovative solutions
- Deep technical insights
- Masterful communication
- Teaches while designing

## 🎯 Assessment Categories

### 1. Problem Analysis & Requirements (25%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - Jumps to solution without clarifying requirements
  - Misses critical functional requirements
  - Ignores non-functional requirements
  - No quantification of scale
- **Example:** "Let's build a URL shortener" → Immediately starts drawing databases
- **Gap:** Lacks systematic requirements gathering

#### Level 2: Meets Expectations
- **Behaviors:**
  - Asks basic clarifying questions
  - Identifies main functional requirements
  - Mentions scale considerations
  - Basic user journey understanding
- **Example:** Asks about daily active users, storage needs, latency requirements
- **Competency:** Covers essentials but may miss edge cases

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Systematic requirements exploration
  - Quantifies all constraints
  - Identifies hidden requirements
  - Prioritizes requirements
- **Example:** "For 1B users with 100 requests/day, that's 1.2M QPS peak. What's our SLA?"
- **Strength:** Thorough and methodical approach

#### Level 4: Outstanding
- **Behaviors:**
  - Anticipates unstated requirements
  - Connects requirements to business goals
  - Identifies conflicting requirements
  - Creates requirement dependency graph
- **Example:** "The 99.9% availability requirement conflicts with the real-time sync need. Let's explore CAP trade-offs..."
- **Mastery:** Sees beyond stated needs to underlying business drivers

### 2. System Architecture (20%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - Monolithic thinking
  - No clear component separation
  - Missing critical services
  - Unclear data flow
- **Example:** Single box labeled "Backend" handling everything
- **Gap:** Lacks understanding of distributed systems

#### Level 2: Meets Expectations
- **Behaviors:**
  - Basic service separation
  - Standard components present
  - Clear client-server model
  - Basic load balancing
- **Example:** Web servers → App servers → Database with load balancer
- **Competency:** Standard n-tier architecture

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Microservices where appropriate
  - Clear bounded contexts
  - Async processing patterns
  - Resilience patterns implemented
- **Example:** Event-driven architecture with circuit breakers, retry logic, and graceful degradation
- **Strength:** Modern distributed patterns

#### Level 4: Outstanding
- **Behaviors:**
  - Novel architectural insights
  - Cross-cutting concerns handled elegantly
  - Evolution path considered
  - Trade-offs deeply analyzed
- **Example:** "This hexagonal architecture allows us to swap data stores without touching business logic, crucial for our migration plan"
- **Mastery:** Architectural decisions tied to long-term strategy

### 3. Data Design (15%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - Single database for everything
  - No schema discussion
  - Ignores data relationships
  - No consistency model
- **Example:** "We'll store everything in a database"
- **Gap:** Lacks data modeling skills

#### Level 2: Meets Expectations
- **Behaviors:**
  - Basic schema design
  - SQL vs NoSQL choice justified
  - Primary keys identified
  - Basic indexing strategy
- **Example:** User table with id, email, password; appropriate indexes
- **Competency:** Fundamental data modeling

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Multiple data stores for different needs
  - Denormalization strategies
  - Caching layers designed
  - Consistency guarantees specified
- **Example:** "User profiles in MySQL, sessions in Redis, logs in BigQuery, with eventual consistency for analytics"
- **Strength:** Polyglot persistence understanding

#### Level 4: Outstanding
- **Behaviors:**
  - Data lifecycle management
  - Complex consistency protocols
  - Novel storage optimizations
  - Cost-performance optimization
- **Example:** "Using LSM trees for write-heavy workload, with bloom filters reducing read amplification by 10x"
- **Mastery:** Deep understanding of storage engines

### 4. API Design (10%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - No API discussion
  - Mixing concerns in endpoints
  - No versioning strategy
  - Ignores error handling
- **Example:** Single endpoint doing multiple unrelated operations
- **Gap:** API design principles unknown

#### Level 2: Meets Expectations
- **Behaviors:**
  - RESTful endpoints defined
  - Basic CRUD operations
  - Standard HTTP status codes
  - Simple request/response format
- **Example:** POST /users, GET /users/{id} with JSON payloads
- **Competency:** Standard REST practices

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - GraphQL/gRPC where appropriate
  - Pagination and filtering
  - Rate limiting design
  - Comprehensive error responses
- **Example:** "GraphQL for flexible queries, gRPC for internal services, with cursor-based pagination"
- **Strength:** Modern API patterns

#### Level 4: Outstanding
- **Behaviors:**
  - API gateway patterns
  - Versioning migration strategy
  - Performance optimization (field masks, partial responses)
  - Developer experience focus
- **Example:** "This field mask approach reduces payload by 80% for mobile clients"
- **Mastery:** API as a product mindset

### 5. Scalability Considerations (10%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - No scaling discussion
  - Single points of failure
  - No capacity planning
  - Ignores bottlenecks
- **Example:** Single database handling all load
- **Gap:** Lacks scaling awareness

#### Level 2: Meets Expectations
- **Behaviors:**
  - Horizontal scaling mentioned
  - Basic sharding strategy
  - CDN for static content
  - Load balancer usage
- **Example:** "We'll shard users by ID range across databases"
- **Competency:** Basic scaling patterns

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Multi-region design
  - Auto-scaling policies
  - Capacity forecasting
  - Performance budgets
- **Example:** "Using consistent hashing for 10x growth without resharding"
- **Strength:** Proactive scaling design

#### Level 4: Outstanding
- **Behaviors:**
  - Novel scaling techniques
  - Cost-aware scaling
  - Workload-specific optimizations
  - Elasticity modeling
- **Example:** "This adaptive partitioning scheme handles hot spots by splitting popular ranges dynamically"
- **Mastery:** Cutting-edge scaling approaches

### 6. Trade-off Analysis (10%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - No trade-offs discussed
  - One-size-fits-all solutions
  - Ignores constraints
  - No alternative considered
- **Example:** "This is the best solution" without justification
- **Gap:** Critical thinking absent

#### Level 2: Meets Expectations
- **Behaviors:**
  - Basic trade-offs identified
  - Pros and cons listed
  - Simple comparisons made
  - Decisions justified
- **Example:** "SQL gives us ACID but limits scale; NoSQL scales but lacks transactions"
- **Competency:** Understands basic trade-offs

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Multiple alternatives analyzed
  - Quantified trade-offs
  - Context-aware decisions
  - Future-proofing considered
- **Example:** "Option A costs 40% more but reduces latency by 60%. Given our SLA, this is worthwhile"
- **Strength:** Data-driven decisions

#### Level 4: Outstanding
- **Behaviors:**
  - Creates decision matrices
  - Identifies non-obvious trade-offs
  - Risk analysis included
  - Evolution strategies
- **Example:** "This seemingly suboptimal choice positions us for the upcoming privacy regulations while maintaining performance"
- **Mastery:** Strategic thinking

### 7. Operational Excellence (5%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - No monitoring mentioned
  - Ignores failure scenarios
  - No deployment strategy
  - Missing logging/debugging
- **Example:** Design assumes everything works perfectly
- **Gap:** Production readiness ignored

#### Level 2: Meets Expectations
- **Behaviors:**
  - Basic monitoring mentioned
  - Simple health checks
  - Log aggregation
  - Basic alerting
- **Example:** "We'll monitor CPU, memory, and error rates"
- **Competency:** Basic observability

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Comprehensive observability
  - SLI/SLO/SLA defined
  - Chaos engineering mentioned
  - Runbooks considered
- **Example:** "These custom metrics track business KPIs, with PagerDuty escalation for SLO breaches"
- **Strength:** DevOps mindset

#### Level 4: Outstanding
- **Behaviors:**
  - Self-healing systems
  - Predictive monitoring
  - Cost optimization included
  - Compliance considerations
- **Example:** "This anomaly detection will predict failures 30 minutes before impact, triggering automatic remediation"
- **Mastery:** Site reliability engineering excellence

### 8. Communication Skills (5%)

#### Level 1: Needs Improvement
- **Behaviors:**
  - Unclear explanations
  - No visual aids
  - Rambling responses
  - Defensive when questioned
- **Example:** Long monologues without checking understanding
- **Gap:** Poor technical communication

#### Level 2: Meets Expectations
- **Behaviors:**
  - Clear verbal explanations
  - Basic diagrams drawn
  - Responds to questions
  - Organized presentation
- **Example:** Draws clear system diagrams while explaining
- **Competency:** Adequate communication

#### Level 3: Exceeds Expectations
- **Behaviors:**
  - Engaging presentation style
  - Excellent visualizations
  - Invites collaboration
  - Adapts to audience level
- **Example:** "Let me show you three ways this could work. Which aligns best with Google's approach?"
- **Strength:** Collaborative communication

#### Level 4: Outstanding
- **Behaviors:**
  - Teaches while designing
  - Storytelling approach
  - Handles pushback gracefully
  - Influences thinking
- **Example:** "This reminds me of how Google evolved Spanner. Let me show you the parallel..."
- **Mastery:** Inspiring communication

## 📋 Self-Assessment Checklists

### Pre-Interview Readiness

**System Design Fundamentals**
- [ ] Can I explain CAP theorem with examples?
- [ ] Do I know when to use SQL vs NoSQL?
- [ ] Can I design a basic distributed system?
- [ ] Do I understand consistency models?
- [ ] Can I identify system bottlenecks?

**Problem-Solving Approach**
- [ ] Do I have a structured approach to problems?
- [ ] Can I gather requirements systematically?
- [ ] Do I ask clarifying questions?
- [ ] Can I estimate capacity needs?
- [ ] Do I consider edge cases?

**Technical Communication**
- [ ] Can I draw clear architecture diagrams?
- [ ] Do I explain choices clearly?
- [ ] Can I handle technical pushback?
- [ ] Do I check for understanding?
- [ ] Can I adapt explanations to the audience?

**Google-Specific Knowledge**
- [ ] Do I understand Google's scale?
- [ ] Am I familiar with Google technologies?
- [ ] Can I relate designs to Google products?
- [ ] Do I know Google's engineering principles?
- [ ] Can I discuss Google-scale challenges?

### Post-Problem Review

**What Went Well**
- [ ] Requirements gathering complete?
- [ ] Architecture clearly explained?
- [ ] Trade-offs well analyzed?
- [ ] Scale considerations addressed?
- [ ] Communication effective?

**Areas for Improvement**
- [ ] What questions stumped me?
- [ ] Which concepts need review?
- [ ] Where did I lose clarity?
- [ ] What details did I miss?
- [ ] How could I communicate better?

**Action Items**
- [ ] Concepts to study deeper
- [ ] Patterns to practice more
- [ ] Communication skills to improve
- [ ] Mock interviews needed
- [ ] Resources to review

## 📝 Mock Interview Evaluation Form

### Candidate Information
- **Name:** ________________________
- **Date:** ________________________
- **Problem:** ________________________
- **Interviewer:** ________________________

### Scoring Matrix

| Category | Score (1-4) | Weight | Weighted Score |
|----------|-------------|---------|----------------|
| Problem Analysis | ___ | 25% | ___ |
| System Architecture | ___ | 20% | ___ |
| Data Design | ___ | 15% | ___ |
| API Design | ___ | 10% | ___ |
| Scalability | ___ | 10% | ___ |
| Trade-offs | ___ | 10% | ___ |
| Operations | ___ | 5% | ___ |
| Communication | ___ | 5% | ___ |
| **Total Score** | | | **___/4.0** |

### Detailed Feedback

**Strengths:**
1. ________________________________
2. ________________________________
3. ________________________________

**Areas for Improvement:**
1. ________________________________
2. ________________________________
3. ________________________________

**Specific Examples:**
- **Best Moment:** _________________
- **Missed Opportunity:** ___________
- **Key Learning:** ________________

### Common Feedback Patterns

**If Score < 2.0: Foundation Building Needed**
- Focus on system design fundamentals
- Practice basic patterns repeatedly
- Study reference architectures
- Work on structured thinking

**If Score 2.0-2.9: Refinement Required**
- Deepen technical knowledge
- Practice trade-off analysis
- Improve requirement gathering
- Enhance visual communication

**If Score 3.0-3.5: Advanced Preparation**
- Study Google-specific technologies
- Practice complex scenarios
- Focus on operational excellence
- Develop unique insights

**If Score > 3.5: Final Polish**
- Practice storytelling
- Prepare war stories
- Focus on presence
- Review cutting-edge tech

### Improvement Strategies

**Technical Gaps**
1. **Identify weak areas** from scoring
2. **Study specific topics** deeply
3. **Build proof-of-concepts**
4. **Read engineering blogs**
5. **Practice implementations**

**Communication Issues**
1. **Record yourself** explaining designs
2. **Practice with non-technical friends**
3. **Use more diagrams**
4. **Structure responses** better
5. **Ask for feedback** actively

**Problem-Solving Approach**
1. **Create a personal framework**
2. **Time-box each section**
3. **Practice with timer**
4. **Build pattern library**
5. **Study exemplar solutions**

## 🎯 Action Planning Template

### Immediate Actions (This Week)
1. **Concept to Master:** ____________
   - Resources: _________________
   - Practice Problem: ___________
   - Success Metric: ____________

2. **Skill to Improve:** _____________
   - Exercise: __________________
   - Feedback Source: ___________
   - Target Level: ______________

### Short-term Goals (Next Month)
1. **Mock Interviews:** ___ per week
2. **Problems to Solve:** ___ total
3. **Concepts to Review:** 
   - [ ] ______________________
   - [ ] ______________________
   - [ ] ______________________

### Long-term Development (3 Months)
1. **Target Score:** ___/4.0
2. **Focus Areas:**
   - Primary: _________________
   - Secondary: _______________
3. **Success Indicators:**
   - [ ] ______________________
   - [ ] ______________________

## 📈 Progress Tracking

### Weekly Review Template

**Week of: ________________**

| Day | Problem Practiced | Score | Key Learning |
|-----|------------------|-------|--------------|
| Mon | | | |
| Tue | | | |
| Wed | | | |
| Thu | | | |
| Fri | | | |
| Sat | | | |
| Sun | | | |

**Weekly Average Score:** ___/4.0
**Improvement from Last Week:** +/- ___

### Monthly Progression Chart

Track your scores over time:

```
4.0 |                    ⭐ (Goal)
3.5 |                  /
3.0 |                /
2.5 |              /
2.0 |            /
1.5 |          /
1.0 |________/
    | M1  M2  M3
```

## 🚀 Using This Rubric Effectively

### For Self-Study
1. **Score yourself honestly** after each practice
2. **Focus on lowest scores** for improvement
3. **Track progress weekly**
4. **Celebrate improvements**
5. **Adjust strategies based on data**

### For Mock Interviews
1. **Share rubric with interviewer** beforehand
2. **Request structured feedback**
3. **Discuss scores together**
4. **Create action plans**
5. **Schedule follow-ups**

### For Real Interviews
1. **Mental self-check** during interview
2. **Adjust approach** based on rubric
3. **Ensure coverage** of all categories
4. **Demonstrate strengths** explicitly
5. **Address weaknesses** proactively

Remember: The goal isn't perfection, but consistent improvement. Even Google engineers continually refine these skills throughout their careers.